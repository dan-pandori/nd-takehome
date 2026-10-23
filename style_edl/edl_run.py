#!/usr/bin/env python3
"""Prequential EDL of one stream under one learner (run `style-edl`).

  python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s0_b1200.pt --stream data/style_edl/streams/s0/S_own.stream.jsonl \
      --test data/style_edl/streams/s0/S_own.test.jsonl --lrs 1e-4,3e-4,1e-3 --epochs 2 --orders 0,1 \
      --out artifacts/style_edl/edl/s0/S_own.json

For every (lr, E, order): blocks [0, 8), [8, 16), [16, 32), [32, 64), [64, 128) of the stream (in the order's
permutation of the file order; order 0 = file order) are coded by the learner (first block) or by A trained from the
learner's weights on the proofs before the block; theta* = A on all 128; L_test = theta*'s mean bits per proof on the
128 test proofs of the same stream.  EDL = sum of block bits - 128 * L_test (bits; + log2(#lrs) for the lr choice is
added by the analysis, not here).  Every fit also codes the test set (the learning curve).  Per-proof bits are stored
for every block and for theta* on test and stream, so every number can be recomputed from this file.
--save_fits DIR saves each fit's state dict (for the l_V pass); --vset FILE also scores every proof of V(x) for the
block's / test set's theorems under each fit (l_V = -log2 sum_y 2^-bits(y)).
"""
import argparse, copy, json, math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import torch

PREFIXES = (0, 8, 16, 32, 64, 128)


def load_set(fn, tok):
    recs = [json.loads(l) for l in open(fn) if l.strip()]
    enc = [C.encode_proof(r['prompt'], r['nd'], tok, C.thm_base(r['name'])) for r in recs]
    return recs, enc


def lse_bits(bits_list):
    """-log2 sum 2^-b"""
    m = min(bits_list)
    return m - math.log2(sum(2.0 ** (m - b) for b in bits_list))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--stream', required=True)
    ap.add_argument('--test', required=True)
    ap.add_argument('--lrs', default='1e-4,3e-4,1e-3')
    ap.add_argument('--algo', default='es', choices=['es', 'fixed'], help='es = A_ES (primary), fixed = A_fixed (E passes)')
    ap.add_argument('--epochs', default='2', help='A_fixed: comma list of pass counts E')
    ap.add_argument('--max_passes', type=int, default=8, help='A_ES: at most this many passes')
    ap.add_argument('--patience', type=int, default=2, help='A_ES: stop after this many passes without improvement')
    ap.add_argument('--arm', default=None, help='registry label (stream)')
    ap.add_argument('--lseed', type=int, default=None, help='registry label (learner seed)')
    ap.add_argument('--orders', default='0,1')
    ap.add_argument('--recs', type=int, default=8)
    ap.add_argument('--prefixes', default=','.join(map(str, PREFIXES)))
    ap.add_argument('--seed', type=int, default=0, help='fit seeds = hash(seed, lr, E, order, n)')
    ap.add_argument('--budget', type=int, default=32768, help='padded tokens per micro-batch (same gradient)')
    ap.add_argument('--threads', type=int, default=0)
    ap.add_argument('--loss_mask', default='names', choices=['names', 'all'], help="A's training loss positions")
    ap.add_argument('--vset', default=None, help='jsonl {name, prompt, nd} of V(x): score l_V under every fit')
    ap.add_argument('--save_theta', default=None, help='directory: save theta* of every (lr, E, order) as a ckpt')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.threads:
        torch.set_num_threads(a.threads)
    os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
    torch.use_deterministic_algorithms(True, warn_only=True)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    import record
    record.save_config(vars(a), a.out, **({'arm': a.arm} if a.arm else {}), **({'seed': a.lseed} if a.lseed is not None else {}))
    from model import load_ckpt
    model, tok, extra = load_ckpt(a.ckpt, dev)
    ck = torch.load(a.ckpt, map_location='cpu')
    init = {k: v.detach().clone() for k, v in model.state_dict().items()}
    srecs, senc = load_set(a.stream, tok)
    trecs, tenc = load_set(a.test, tok)
    prefixes = [int(x) for x in a.prefixes.split(',')]
    n_all = len(senc)
    assert prefixes[0] == 0 and prefixes[-1] <= n_all, (prefixes, n_all)
    blocks = C.blocks_of(prefixes, n_all)
    vrecs = venc = None
    if a.vset:
        vr = [json.loads(l) for l in open(a.vset) if l.strip()]
        want = {r['name'] for r in srecs} | {r['name'] for r in trecs}
        vr = [r for r in vr if r['name'] in want]
        venc = [C.encode_proof(r['prompt'], r['nd'], tok, C.thm_base(r['name'])) for r in vr]
        vrecs = vr
        vby = {}
        for k, r in enumerate(vr):
            vby.setdefault(r['name'], []).append(k)
    t0 = time.time()
    if dev == 'cuda':
        torch.cuda.synchronize()

    def lv(names):
        """l_V per theorem name under the current model."""
        ks = [k for nm in names for k in vby.get(nm, [])]
        sc = C.score(model, venc, tok, dev, idxs=ks)
        return {nm: (lse_bits([sc[k]['bits'] for k in vby[nm]]) if nm in vby else None) for nm in names}

    def summ(sc, idxs):
        return {'bits': [round(sc[i]['bits'], 6) for i in idxs], 'bits_all': [round(sc[i]['bits_all'], 6) for i in idxs],
                'tok': sum(sc[i]['tok'] for i in idxs), 'tok_all': sum(sc[i]['tok_all'] for i in idxs),
                'acts': sum(sc[i]['acts'] for i in idxs)}

    base_stream = C.score(model, senc, tok, dev, agree=True)
    base_test = C.score(model, tenc, tok, dev, agree=True)
    res = {'args': vars(a), 'ckpt_md5': None, 'dev': torch.cuda.get_device_name(0) if dev == 'cuda' else 'cpu',
           'stream_names': [r['name'] for r in srecs], 'test_names': [r['name'] for r in trecs],
           'blocks': blocks, 'n_stream': n_all, 'n_test': len(tenc),
           'stream_acts': [len(e) for e in senc], 'test_acts': [len(e) for e in tenc],
           'stream_tok': [base_stream[i]['tok'] for i in range(n_all)], 'stream_tok_all': [base_stream[i]['tok_all'] for i in range(n_all)],
           'test_tok': [base_test[i]['tok'] for i in range(len(tenc))],
           'base': {'stream': summ(base_stream, range(n_all)), 'test': summ(base_test, range(len(tenc))),
                    'stream_agree': [sum(base_stream[i]['agree']) for i in range(n_all)],
                    'test_agree': [sum(base_test[i]['agree']) for i in range(len(tenc))],
                    'stream_act_bits': [base_stream[i]['act_bits'] for i in range(n_all)]},
           'runs': []}
    if a.vset:
        res['base']['lv_stream'] = lv([r['name'] for r in srecs])
        res['base']['lv_test'] = lv([r['name'] for r in trecs])
        res['vset_sizes'] = {nm: len(v) for nm, v in vby.items()}
    lrs = [float(x) for x in a.lrs.split(',')]
    eps = [float(x) for x in a.epochs.split(',')] if a.algo == 'fixed' else [None]

    def fit(penc, n, lr, E, fs):
        if a.algo == 'es':
            info = C.finetune_es(model, init, penc, n, lr, tok, dev, fs, recs=a.recs, max_passes=a.max_passes,
                                 patience=a.patience, budget=a.budget, loss_mask=a.loss_mask)
        else:
            info = C.finetune(model, init, penc, n, lr, E, tok, dev, fs, recs=a.recs, budget=a.budget, loss_mask=a.loss_mask)
        record.count(train_steps=info['steps'] + info.get('es_steps', 0), train_tokens=info['train_tokens'] + info.get('es_tokens', 0))
        return info
    orders = [int(x) for x in a.orders.split(',')]
    for E in eps:
        for lr in lrs:
            for o in orders:
                perm = list(range(n_all))
                if o:
                    random.Random(1000 + o).shuffle(perm)
                penc = [senc[i] for i in perm]
                pnames = [srecs[i]['name'] for i in perm]
                Ek = 0 if E is None else E
                run = {'algo': a.algo, 'lr': lr, 'E': E, 'order': o, 'perm': perm, 'blocks': [], 't0': round(time.time() - t0, 1)}
                for (lo, hi) in blocks:
                    fs = a.seed * 1000003 + int(round(lr * 1e7)) * 101 + int(Ek * 10) * 7 + o * 100003 + lo
                    info = fit(penc, lo, lr, E, fs)
                    sb = C.score(model, penc, tok, dev, idxs=range(lo, hi))
                    st = C.score(model, tenc, tok, dev)
                    blk = {'lo': lo, 'hi': hi, 'fit': info,
                           'block': summ(sb, range(lo, hi)),
                           'test_mean_bits': sum(st[i]['bits'] for i in st) / len(st),
                           'test_mean_bits_all': sum(st[i]['bits_all'] for i in st) / len(st)}
                    if a.vset:
                        blk['lv_block'] = lv(pnames[lo:hi])
                    run['blocks'].append(blk)
                fs = a.seed * 1000003 + int(round(lr * 1e7)) * 101 + int(Ek * 10) * 7 + o * 100003 + n_all
                info = fit(penc, n_all, lr, E, fs)
                st = C.score(model, tenc, tok, dev, agree=True)
                ss = C.score(model, penc, tok, dev)
                run['theta'] = {'fit': info, 'test': summ(st, range(len(tenc))),
                                'test_agree': [sum(st[i]['agree']) for i in range(len(tenc))],
                                'stream_after': summ(ss, range(n_all))}
                if a.vset:
                    run['theta']['lv_test'] = lv([r['name'] for r in trecs])
                pre = sum(sum(b['block']['bits']) for b in run['blocks'])
                pre_all = sum(sum(b['block']['bits_all']) for b in run['blocks'])
                Lt = sum(run['theta']['test']['bits']) / len(tenc)
                Lt_all = sum(run['theta']['test']['bits_all']) / len(tenc)
                acts = sum(len(e) for e in senc)
                run['summary'] = {'preq_bits': pre, 'L_test': Lt, 'EDL': pre - n_all * Lt, 'EDL_per_proof': (pre - n_all * Lt) / n_all,
                                  'EDL_per_action': (pre - n_all * Lt) / acts,
                                  'preq_bits_all': pre_all, 'L_test_all': Lt_all, 'EDL_all': pre_all - n_all * Lt_all,
                                  'first_block_bits_per_proof': sum(run['blocks'][0]['block']['bits']) / (blocks[0][1] - blocks[0][0])}
                if a.vset:
                    lvb = sum(v for b in run['blocks'] for v in b['lv_block'].values())
                    lvt = sum(run['theta']['lv_test'].values()) / len(tenc)
                    run['summary'].update(lv_preq_bits=lvb, lv_L_test=lvt, lv_EDL=lvb - n_all * lvt)
                run['secs'] = round(time.time() - t0 - run['t0'], 1)
                if a.save_theta:
                    os.makedirs(a.save_theta, exist_ok=True)
                    fn = os.path.join(a.save_theta, f'theta_{a.algo}_lr{lr:g}_E{Ek:g}_o{o}.pt')
                    torch.save({'cfg': ck['cfg'], 'state': model.state_dict(), 'tok_mode': ck['tok_mode'],
                                'extra': {'init': a.ckpt, 'stream': a.stream, 'algo': a.algo, 'lr': lr, 'E': E, 'order': o}}, fn)
                    run['theta_ckpt'] = fn
                res['runs'].append(run)
                s = run['summary']
                print(f"{a.algo} E {Ek:g} lr {lr:g} o {o}: p* {[b['fit'].get('passes') for b in run['blocks']] + [info.get('passes')]} preq {s['preq_bits']:.1f} L_test {s['L_test']:.3f} EDL/proof {s['EDL_per_proof']:.3f}"
                      f" first {s['first_block_bits_per_proof']:.3f} ({run['secs']:.0f}s)", flush=True)
                os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
                json.dump(res, open(a.out + '.tmp', 'w'))
                os.replace(a.out + '.tmp', a.out)
    res['secs'] = round(time.time() - t0, 1)
    if dev == 'cuda':
        res['peak_alloc_gb'] = torch.cuda.max_memory_allocated() / 2 ** 30
    json.dump(res, open(a.out + '.tmp', 'w'))
    os.replace(a.out + '.tmp', a.out)


if __name__ == '__main__':
    main()
