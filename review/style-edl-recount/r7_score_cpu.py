#!/usr/bin/env python3
"""R7 (reviewer, phase 1): CPU fp32 re-score with my own scoring loop.
Uses only the repository's shared environment + tokenizer + model loader (state_env.decompose, tokenizer, model.load_ckpt;
written by earlier runs), not the run's style_edl/ code: my own per-theorem name base (sha1 of 'style-edl:<name>' mod 33,
the pre-registered convention), my own name shift, my own mask of the environment-assigned names (the `have` name and
the binder of a box / the first Or.elim branch), my own bit sum and argmax agreement.

  ~/.venv-torch/bin/python r7_score_cpu.py --what learners     # learners on all 18 streams (S_Kal: --kal_n proofs)
  ~/.venv-torch/bin/python r7_score_cpu.py --what theta        # the 18 theta* (lr*, order 0) on their test files
  ~/.venv-torch/bin/python r7_score_cpu.py --what tokens       # fit train-token counts vs the prefix they should use
"""
import argparse, hashlib, json, math, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/style-edl')
CK = os.path.expanduser('~/review/style-edl-ckpts')
sys.path.insert(0, WS)
import torch, torch.nn.functional as F
torch.set_num_threads(2)
from state_env import decompose
from model import load_ckpt
from tokenizer import make_tokenizer

SEEDS = (0, 1, 2)
STREAMS = ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')
LN2 = math.log(2)
NM = re.compile(r'n(\d+)$')


def base_of(name):
    return int(hashlib.sha1(f'style-edl:{name}'.encode()).hexdigest(), 16) % 33


def sh(toks, b):
    return [f'n{int(m.group(1)) + b}' if (m := NM.match(t)) else t for t in toks]


def env_names(act):
    """positions (in the action) of the names the environment assigns"""
    if len(act) < 2 or act[0] != 'have':
        return []
    pos = [1]
    if ':=' in act:
        i = act.index(':=') + 1
        if i < len(act) and act[i] == '(' and i + 3 < len(act) and act[i + 1] == 'fun':
            pos.append(i + 3)
        elif i < len(act) and act[i] == 'Or.elim' and i + 5 < len(act):
            pos.append(i + 5)
    return pos


def encode(tok, rec):
    b = base_of(rec['name'])
    steps, toks, env = decompose(rec['prompt'], rec['nd'], canon=True)
    out = []
    for st, act, hs in steps:
        s_ids = tok.encode_toks(sh(st, b))
        a_ids = tok.encode_toks(sh(act, b)) + [tok.eos]
        mask = [True] * len(a_ids)
        for p in env_names(act):
            assert NM.match(act[p]), (act, p)
            mask[p] = False
        out.append((s_ids, a_ids, mask))
    return out


@torch.no_grad()
def score(model, tok, enc, budget=24000):
    """-> per proof: (bits masked, bits all, coded tokens, actions agreeing)"""
    rows = [(i, s, a, m) for i, pr in enumerate(enc) for (s, a, m) in pr]
    rows.sort(key=lambda r: len(r[1]) + len(r[2]))
    res = [[0.0, 0.0, 0, 0] for _ in enc]
    k = 0
    while k < len(rows):
        T = len(rows[k][1]) + len(rows[k][2])
        j = k
        while j < len(rows) and (len(rows[j][1]) + len(rows[j][2])) * (j - k + 1) <= budget:
            j += 1
        j = max(j, k + 1)
        batch = rows[k:j]
        T = max(len(r[1]) + len(r[2]) for r in batch)
        x = torch.full((len(batch), T), tok.pad, dtype=torch.long)
        for q, (_, s, a, m) in enumerate(batch):
            x[q, :len(s) + len(a)] = torch.tensor(s + a)
        h, _ = model.features(x[:, :-1])
        lp = F.log_softmax(model.head(model.ln_f(h)).float(), -1)
        am = lp.argmax(-1)
        for q, (i, s, a, m) in enumerate(batch):
            pos = torch.arange(len(s) - 1, len(s) + len(a) - 1)
            tgt = x[q, len(s):len(s) + len(a)]
            nll = -lp[q, pos, tgt] / LN2
            mk = torch.tensor(m)
            res[i][0] += float(nll[mk].sum())
            res[i][1] += float(nll.sum())
            res[i][2] += int(mk.sum())
            res[i][3] += int(bool(((am[q, pos] == tgt) | ~mk).all()))
        k = j
    return res


def load(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--what', required=True, choices=['learners', 'theta', 'tokens'])
    ap.add_argument('--kal_n', type=int, default=6)
    a = ap.parse_args()
    t0 = time.time()
    r3 = json.load(open(os.path.join(HERE, 'out', 'r3_edl.json')))['cells']
    out = {}
    tok = make_tokenizer('lean_staten')
    if a.what == 'tokens':
        for s in SEEDS:
            for S in STREAMS:
                d = json.load(open(f'{WS}/artifacts/style_edl/edl/s{s}/{S}.json'))
                recs = load(f'{WS}/data/style_edl/streams/s{s}/{S}.stream.jsonl')
                assert [r['name'] for r in recs] == d['stream_names']
                enc = [encode(tok, r) for r in recs]
                ptok = [sum(len(x[0]) + len(x[1]) for x in e) for e in enc]
                bad = []
                nfit = 0
                for r in d['runs']:
                    perm = r['perm']
                    fits = [(b['lo'], b['fit']) for b in r['blocks']] + [(d['n_stream'], r['theta']['fit'])]
                    for n, f in fits:
                        if n == 0:
                            continue
                        nfit += 1
                        pre = [perm[i] for i in range(n)]
                        want = f['passes'] * sum(ptok[i] for i in pre)
                        steps = f['passes'] * math.ceil(n / 8)
                        tr = [perm[i] for i in range(n) if i % 4 != 3]
                        es_done = round(f.get('es_tokens', 0) / max(1, sum(ptok[i] for i in tr)), 6)
                        if f['train_tokens'] != want or f['steps'] != steps or abs(es_done - round(es_done)) > 1e-9:
                            bad.append((r['lr'], r['order'], n, f['train_tokens'], want, f['steps'], steps, es_done))
                out[f's{s}/{S}'] = {'fits_checked': nfit, 'mismatches': bad[:5], 'n_mismatch': len(bad),
                                    'stream_pair_tokens_per_proof': sum(ptok) / len(ptok),
                                    'stream_coded_tokens_per_proof': sum(sum(sum(x[2]) for x in e) for e in enc) / len(enc),
                                    'stored_coded_tokens_per_proof': sum(d['stream_tok']) / len(d['stream_tok']),
                                    'max_action_tokens': max(len(x[1]) - 1 for e in enc for x in e),
                                    'max_pair_tokens': max(len(x[0]) + len(x[1]) for e in enc for x in e),
                                    'actions_per_proof': sum(len(e) for e in enc) / len(enc)}
                print(f's{s}/{S}', out[f's{s}/{S}'], flush=True)
    elif a.what == 'learners':
        for s in SEEDS:
            fn = f'{WS}/ckpts/bs/stage1_best12_s0_b1200.pt' if s == 0 else f'{CK}/stage1_best12_s{s}_b1200.pt'
            model, tk, extra = load_ckpt(fn, 'cpu')
            model.eval()
            for S in STREAMS:
                d = json.load(open(f'{WS}/artifacts/style_edl/edl/s{s}/{S}.json'))
                for part, ref, refa in (('stream', d['base']['stream']['bits'], d['base']['stream_agree']),
                                        ('test', d['base']['test']['bits'], d['base']['test_agree'])):
                    recs = load(f'{WS}/data/style_edl/streams/s{s}/{S}.{part}.jsonl')
                    idx = list(range(len(recs)))
                    if S == 'S_Kal':
                        idx = sorted(idx, key=lambda i: len(recs[i]['nd']))[:a.kal_n]
                    enc = [encode(tk, recs[i]) for i in idx]
                    sc = score(model, tk, enc)
                    diffs = [abs(sc[q][0] - ref[i]) for q, i in enumerate(idx)]
                    agree_eq = sum(sc[q][3] == refa[i] for q, i in enumerate(idx))
                    out[f's{s}/{S}/{part}'] = {'n': len(idx), 'mine_mean_bits': sum(x[0] for x in sc) / len(sc),
                                               'stored_mean_bits': sum(ref[i] for i in idx) / len(idx),
                                               'max_abs_diff': max(diffs), 'sum_abs_diff': sum(diffs),
                                               'agree_counts_equal': agree_eq,
                                               'mine_all_tok_mean': sum(x[1] for x in sc) / len(sc)}
                    print(f's{s}/{S}/{part}', out[f's{s}/{S}/{part}'], round(time.time() - t0), flush=True)
    else:
        for s in SEEDS:
            for S in STREAMS:
                c = r3[f's{s}/{S}']
                lr = c['lr_star']
                fn = f'{CK}/s{s}_{S}_theta_es_lr{lr:g}_E0_o0.pt'
                if not os.path.exists(fn):
                    fn = f'{CK}/s{s}_{S}_theta_es_lr{"1e-05" if lr == 1e-5 else "0.0001"}_E0_o0.pt'
                model, tk, extra = load_ckpt(fn, 'cpu')
                model.eval()
                d = json.load(open(f'{WS}/artifacts/style_edl/edl/s{s}/{S}.json'))
                run = [r for r in d['runs'] if abs(r['lr'] - lr) < 1e-12 and r['order'] == 0][0]
                ref = run['theta']['test']['bits']
                recs = load(f'{WS}/data/style_edl/streams/s{s}/{S}.test.jsonl')
                idx = list(range(len(recs)))
                if S == 'S_Kal':
                    idx = sorted(idx, key=lambda i: len(recs[i]['nd']))[:a.kal_n]
                enc = [encode(tk, recs[i]) for i in idx]
                sc = score(model, tk, enc)
                diffs = [abs(sc[q][0] - ref[i]) for q, i in enumerate(idx)]
                b0 = d['base']['test']['bits']
                out[f's{s}/{S}'] = {'ckpt': os.path.basename(fn), 'extra': {k: extra.get(k) for k in ('stream', 'lr', 'order', 'algo')},
                                    'n': len(idx), 'mine_mean_bits': sum(x[0] for x in sc) / len(sc),
                                    'stored_theta_mean_bits': sum(ref[i] for i in idx) / len(idx),
                                    'stored_learner_mean_bits': sum(b0[i] for i in idx) / len(idx),
                                    'max_abs_diff': max(diffs)}
                print(f's{s}/{S}', out[f's{s}/{S}'], round(time.time() - t0), flush=True)
    json.dump(out, open(os.path.join(HERE, 'out', f'r7_{a.what}.json'), 'w'), indent=1)
    print('done', round(time.time() - t0))


if __name__ == '__main__':
    main()
