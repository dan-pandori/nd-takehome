#!/usr/bin/env python3
"""Reviewer recount of E2's second estimate and the log p along the ladders, from the raw cd_score rows
(artifacts/coe/score/*/<ckpt>.jsonl.gz; one name base, so total = log pi(y | b0) and log pi(y) >= total - ln 33).
Per checkpoint and strict held-out member: best known proof (max over the member's known proofs) and the known-proof sum
(logsumexp) at T 0.8; medians over members; also restricted to known proofs that contain a free sigma (DN on a NEGI line)."""
import collections, glob, json, math, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
S = f'{RV}/artifacts/coe/score'
FAM = json.load(open(f'{RV}/review_coe/out_families.json'))
SH = set(FAM['strict_heldout']); ST = set(FAM['strict_trained'])
LN33 = math.log(33)


def lse(xs):
    m = max(xs); return m + math.log(sum(math.exp(x - m) for x in xs))


def summarize(d, files, label):
    T = {r['tid']: r for r in C.rows(f'{d}/targets.jsonl.gz')}
    res = {}
    for f in files:
        ck = os.path.basename(f).split('.')[0]
        best = collections.defaultdict(list)
        n = 0; bad = 0
        for r in C.rows(f):
            t = T.get(r['tid'])
            if t is None or 'T0.8' not in r or r['T0.8'] is None:
                bad += 1; continue
            n += 1
            best[t['name']].append(r['T0.8']['total'])
        hm = [max(v) for k, v in best.items() if k in SH]
        hs = [lse(v) for k, v in best.items() if k in SH]
        tm = [max(v) for k, v in best.items() if k in ST]
        res[ck] = {'rows': n, 'bad': bad, 'heldout_members': len(hm), 'median_best_heldout': statistics.median(hm) if hm else None,
                   'median_sum_heldout': statistics.median(hs) if hs else None, 'trained_members': len(tm),
                   'median_best_trained': statistics.median(tm) if tm else None}
        print(f'{label:14s} {ck:8s} rows {n:6d} (unmatched {bad}) held-out members {len(hm):3d}: median best {res[ck]["median_best_heldout"]}'
              f' (lower bound {res[ck]["median_best_heldout"] - LN33 if hm else None}), median sum {res[ck]["median_sum_heldout"]};'
              f' trained members {len(tm)} median best {res[ck]["median_best_trained"]}')
    return res


out = {}
d = f'{S}/known_b1'
out['known_b1'] = summarize(d, sorted(glob.glob(f'{d}/*_s*.jsonl.gz')), 'known_b1')
for d in sorted(glob.glob(f'{S}/rounds_*')):
    fs = [f'{d}/{c}.jsonl.gz' for c in ('pend', 'r4', 'r8', 'r12', 'r16') if os.path.exists(f'{d}/{c}.jsonl.gz')]
    if fs:
        out[os.path.basename(d)] = summarize(d, fs, os.path.basename(d))
json.dump(out, open(f'{RV}/review_coe/out_score.json', 'w'), indent=1)
