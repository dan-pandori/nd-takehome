#!/usr/bin/env python3
"""Reviewer recount of B1 (first-epoch prequential code from kalmar-pretrain's training curves).

  python3 rv_b1.py count data/kh/train_k12.jsonl out/b1_tokens_k12.json
  python3 rv_b1.py count data/kalmar/train_kal_sl.jsonl.gz out/b1_tokens_kal.json
  ~/.venv-torch/bin/python rv_b1.py preq            # needs both token files; reads the 6 checkpoints' extra

Token count (own segmentation, not state_env.decompose): the canonical lean_seq text (state_env.canonicalise) is cut
into actions: `have` up to and including the first `;` or `by`; `exact n` = 2 tokens; every other token is supplied
by the environment (box closings, second Or.elim branch).  Loss tokens of a pair = action tokens + <eos>.
The pair count must equal the checkpoint's `pairs`.

L_preq = sum over curve intervals of epoch 1 of  loss_i [nats/token, the interval mean] * N * (e_i - e_{i-1}) / ln 2,
the last interval cut at e = 1.  Variants: the interval's loss taken from the next point (right) or the previous
point (left), to bound the discretisation; residual L_inf = (a) final train loss, (b) final held-out loss,
(c) train loss of the interval that ends epoch 1.
"""
import gzip, json, math, os, sys, time, collections
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
sys.path.insert(0, WS)
LN2 = math.log(2)


def segment(toks):
    acts = []
    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        if t == 'have':
            j = i
            while toks[j] not in (';', 'by'):
                j += 1
            acts.append(j - i + 1)
            i = j + 1
        elif t == 'exact':
            acts.append(2)
            i += 2
        else:
            i += 1
    return acts


def count(fn, out):
    from state_env import canonicalise
    op = gzip.open if fn.endswith('.gz') else open
    t0 = time.time()
    rec = pairs = loss = 0
    per_tag = collections.defaultdict(lambda: [0, 0])
    with op(os.path.join(WS, fn), 'rt') as fh:
        for line in fh:
            r = json.loads(line)
            rec += 1
            acts = segment(canonicalise(r['prompt'], r['proof']))
            pairs += len(acts)
            loss += sum(a + 1 for a in acts)
            tags = r.get('tags')
            if tags:
                if isinstance(tags, str):
                    tags = json.loads(tags.replace("'", '"'))
                assert len(tags) == len(acts), (rec, len(tags), len(acts))
                for tg, a in zip(tags, acts):
                    per_tag[tg][0] += 1
                    per_tag[tg][1] += a + 1
            if rec % 20000 == 0:
                print(rec, pairs, loss, f'{time.time() - t0:.0f}s', flush=True)
    res = {'file': fn, 'records': rec, 'pairs': pairs, 'loss_tokens': loss, 'per_tag': dict(per_tag),
           'secs': time.time() - t0}
    json.dump(res, open(os.path.join(HERE, out), 'w'), indent=1)
    print({k: v for k, v in res.items() if k != 'per_tag'})


def preq():
    import torch
    toks = {'kal': json.load(open(os.path.join(HERE, 'out/b1_tokens_kal.json'))),
            'k12': json.load(open(os.path.join(HERE, 'out/b1_tokens_k12.json')))}
    out = {}
    for name, ck, tk in [(f'KAL-D s{s}', f'stage1_kalD_s{s}.pt', 'kal') for s in range(3)] + \
                        [(f'control s{s}', f'stage1_best12_s{s}_b1200.pt', 'k12') for s in range(3)]:
        o = torch.load(os.path.join(WS, 'ckpts/kc_src', ck), map_location='cpu', weights_only=False)
        ex = o['extra']
        N = toks[tk]['loss_tokens']
        assert toks[tk]['pairs'] == ex['pairs'], (name, toks[tk]['pairs'], ex['pairs'])
        V = o['cfg']['vocab']
        pts = sorted(ex['curve'], key=lambda p: p['step'])
        Lm = Lr = Ll = 0.0
        e0 = 0.0
        prev_loss = None
        n_int = 0
        end_loss = None
        for k, p in enumerate(pts):
            e1 = min(p['epochs'], 1.0)
            if e1 <= e0:
                break
            w = N * (e1 - e0) / LN2
            Lm += p['train_loss'] * w
            # right: the loss of the next point (the end of the interval is better trained); left: previous point
            nxt = pts[k + 1]['train_loss'] if k + 1 < len(pts) else p['train_loss']
            Lr += nxt * w
            Ll += (prev_loss if prev_loss is not None else math.log(V)) * w
            prev_loss = p['train_loss']
            end_loss = p['train_loss']
            n_int += 1
            e0 = e1
            if p['epochs'] >= 1.0:
                break
        la, lb, lc = ex['last_train_loss'], ex['final_val'], end_loss
        res = {'ckpt': ck, 'N_loss_tokens': N, 'pairs': ex['pairs'], 'vocab': V, 'n_params': ex.get('n_params'),
               'batches_per_epoch': ex['batches_per_epoch'], 'curve_points_epoch1': n_int,
               'first_point': {k: pts[0][k] for k in ('step', 'epochs', 'train_loss')},
               'L_preq_bits': Lm, 'L_preq_right_bits': Lr, 'L_preq_left_uniform_first_bits': Ll,
               'bits_per_token': Lm / N, 'L_inf_nats': {'a': la, 'b': lb, 'c': lc},
               'EDL_bits': {'a': Lm - N * la / LN2, 'b': Lm - N * lb / LN2, 'c': Lm - N * lc / LN2},
               'EDL_right_a': Lr - N * la / LN2}
        out[name] = res
        print(name, f"N={N:,} Lpreq={Lm:.4g} (right {Lr:.4g}, left {Ll:.4g}) bits/tok={Lm / N:.4f} "
                    f"EDL a={res['EDL_bits']['a']:.4g} b={res['EDL_bits']['b']:.4g} c={res['EDL_bits']['c']:.4g} "
                    f"pts={n_int}", flush=True)
    json.dump(out, open(os.path.join(HERE, 'out/b1_recount.json'), 'w'), indent=1)


if __name__ == '__main__':
    if sys.argv[1] == 'count':
        count(sys.argv[2], sys.argv[3])
    else:
        preq()
