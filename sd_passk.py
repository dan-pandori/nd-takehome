#!/usr/bin/env python3
"""Addendum 2: pass@k on a slice of the held-out file, judged by LEAN ALONE, for checkpoints picked by
their per-bin validation loss.  Separates "the pattern is lost and regained" from "the greedy path is
on a knife-edge".  A new file: nothing the greedy evaluations use is touched.

  python3 sd_passk.py --ckpts ckpts/sd/f_s1.step08000.pt ... --in data/p2/heldout.jsonl \
      --slice depth3 --k 8 --temperature 0.8 --outdir artifacts/sd/passk [--batch 512]

Writes <outdir>/<stem>.<slice>.k<k>.json (pass@1..k and the greedy rate on the same slice) and
<stem>.<slice>.k<k>.jsonl (one record per theorem: n_ok of k, solved, the accepted texts).
"""
import argparse, glob, json, math, os, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch
from model import load_ckpt
from sample import generate
from lean_gate import lean_check


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def judge_pass(tok, prompts, texts, raw):
    """-> per-sample bool: the strict grammar accepts the sampled ids AND Lean accepts the literal text"""
    nd = [tok.decode(r.tolist()) for r in raw]
    parsed = [bool(t) and not d.startswith('LEANPARSE') for t, d in zip(texts, nd)]
    items, where = [], []
    for i, (p, t) in enumerate(zip(prompts, texts)):
        if parsed[i]:
            items.append((tok.statement(p), t)); where.append(i)
    ok, wall, proc = lean_check(items)
    res = [False] * len(prompts)
    for i, o in zip(where, ok):
        res[i] = bool(o)
    return res, sum(1 for x in parsed if not x), wall, proc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpts', nargs='+', required=True)
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--slice', default='depth3', choices=('depth3', 'len6', 'all'))
    ap.add_argument('--k', type=int, default=8)
    ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--batch', type=int, default=512)
    ap.add_argument('--max_new', type=int, default=400)
    ap.add_argument('--outdir', required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    if a.slice == 'depth3':
        recs = [r for r in recs if (r.get('pat') or {}).get('depth3')]
    elif a.slice == 'len6':
        recs = [r for r in recs if r['n_lines'] == 6]
    prompts = [r['prompt'] for r in recs]
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'{len(recs)} theorems on slice {a.slice}, k={a.k}, T={a.temperature}', flush=True)
    for ck in [c for pat in a.ckpts for c in sorted(glob.glob(pat))]:
        stem = os.path.basename(ck)[:-3]
        t0 = time.time()
        model, tok, extra = load_ckpt(ck, dev)
        per_pass, lean_s = [], 0.0
        for c in range(a.k + 1):                     # pass 0 is greedy, on the same slice
            raw = np.full((len(prompts), a.max_new), tok.pad, dtype=np.int64)
            texts = generate(model, tok, prompts, greedy=(c == 0), temperature=a.temperature,
                             max_new=a.max_new, batch=a.batch, seed=1000 + c, gate=False, raw=raw)
            ok, pf, wall, proc = judge_pass(tok, prompts, texts, raw)
            lean_s += wall
            per_pass.append({'pass': c, 'greedy': c == 0, 'solved': sum(ok),
                             'rate': sum(ok) / len(recs), 'parse_fail': pf,
                             'texts': [t if o else None for t, o in zip(texts, ok)], 'ok': ok})
        greedy = per_pass[0]
        sampled = per_pass[1:]
        anyk = [any(p['ok'][i] for p in sampled) for i in range(len(recs))]
        nok = [sum(p['ok'][i] for p in sampled) for i in range(len(recs))]
        cum = []
        for kk in range(1, a.k + 1):
            s = sum(1 for i in range(len(recs)) if any(p['ok'][i] for p in sampled[:kk]))
            lo, hi = wilson(s, len(recs))
            cum.append({'k': kk, 'solved': s, 'rate': s / len(recs), 'ci': [lo, hi]})
        out = {'ckpt': ck, 'slice': a.slice, 'n': len(recs), 'k': a.k, 'temperature': a.temperature,
               'judge': 'lean_alone', 'batch': a.batch,
               'model': {'n_params': extra.get('n_params'), 'mode': tok.mode, 'step': extra.get('step'),
                         'train_args': extra.get('args')},
               'greedy': {'solved': greedy['solved'], 'rate': greedy['rate'],
                          'ci': list(wilson(greedy['solved'], len(recs)))},
               'per_pass': [{'pass': p['pass'], 'solved': p['solved'], 'rate': p['rate'],
                             'parse_fail': p['parse_fail']} for p in per_pass],
               'pass_at_k': cum, 'lean_wall_s': lean_s, 'total_s': time.time() - t0}
        fs = os.path.join(a.outdir, f'{stem}.{a.slice}.k{a.k}.json')
        json.dump(out, open(fs, 'w'), indent=1)
        with open(fs[:-5] + '.jsonl', 'w') as f:
            for i, r in enumerate(recs):
                f.write(json.dumps({'name': r.get('name'), 'greedy_ok': greedy['ok'][i],
                                    'n_ok_of_k': nok[i], 'solved_at_k': anyk[i],
                                    'example': next((p['texts'][i] for p in sampled if p['ok'][i]), None)}) + '\n')
        print(f"{stem} [{a.slice}] greedy {greedy['rate']:.4f} -> pass@{a.k} {cum[-1]['rate']:.4f} "
              f"({cum[-1]['solved']}/{len(recs)}), per-pass {[round(p['rate'], 3) for p in sampled]}, "
              f"{time.time() - t0:.0f}s", flush=True)
        del model


if __name__ == '__main__':
    main()
