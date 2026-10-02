#!/usr/bin/env python3
"""C7 recount (reviewer, independent): lit-measures M2 identical-seed re-run variance vs 8x8 init x data-order grid variance.
Inputs: hf lit-measures/artifacts/lit-measures/m2/heldout_i<I>_d<D>[_r<k>].jsonl (per-theorem greedy results);
depth-3 slice = data/p2/heldout.jsonl records with pat.depth3 (500). Own code; scipy for F quantiles only."""
import json, random, statistics as st, numpy as np
from scipy import stats
R = '/home/dan/review/claim-audit/rv/C567_raw/lit-measures/artifacts/lit-measures/m2'
d3 = set(); allnames = set()
for l in open('/home/dan/review/claim-audit/data/p2/heldout.jsonl'):
    r = json.loads(l); allnames.add(r['name'])
    if r['pat']['depth3']: d3.add(r['name'])
assert len(d3) == 500


def cell(fn):
    s3 = n3 = s = n = 0
    for l in open(f'{R}/{fn}'):
        r = json.loads(l); ok = bool(r['solved']); n += 1; s += ok
        if r['name'] in d3: n3 += 1; s3 += ok
    assert n == 5000 and n3 == 500, (fn, n, n3)
    return s3 / 500, s / 5000


grid = {(i, d): cell(f'heldout_i{i}_d{d}.jsonl') for i in range(8) for d in range(100, 108)}
reps = [grid[0, 100]] + [cell(f'heldout_i0_d100_r{k}.jsonl') for k in range(1, 9)]
out = {}
for j, q in ((0, 'depth3'), (1, 'overall')):
    g = np.array([v[j] for v in grid.values()]); r = np.array([v[j] for v in reps])
    vg, vr = g.var(ddof=1), r.var(ddof=1); ratio = vr / vg
    # F interval (assumes normality; both distributions are bimodal, so indicative only)
    lo = ratio / stats.f.ppf(.975, 8, 63); hi = ratio / stats.f.ppf(.025, 8, 63)
    # bootstrap: resample replicates (9) and grid cells (64) independently
    rng = np.random.default_rng(0); bs = []
    for _ in range(20000):
        rr = rng.choice(r, 9); gg = rng.choice(g, 64)
        bs.append(rr.var(ddof=1) / gg.var(ddof=1))
    bl, bh = np.percentile(bs, [2.5, 97.5])
    # two-way random effects on the grid (balanced 8x8, one obs per cell): share of init / data / residual
    M = np.array([[grid[i, d][j] for d in range(100, 108)] for i in range(8)])
    gm = M.mean(); msr = 8 * ((M.mean(1) - gm) ** 2).sum() / 7; msc = 8 * ((M.mean(0) - gm) ** 2).sum() / 7
    res = M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + gm; mse = (res ** 2).sum() / 49
    vi = max(0, (msr - mse) / 8); vd = max(0, (msc - mse) / 8); tot = vi + vd + mse
    # replicate var vs grid residual var (the residual is what GPU noise should explain)
    ratio_res = vr / mse
    lo_r = ratio_res / stats.f.ppf(.975, 8, 49); hi_r = ratio_res / stats.f.ppf(.025, 8, 49)
    # Levene / Brown-Forsythe (robust to non-normality) for equal variance reps vs grid
    lev = stats.levene(r, g, center='median')
    print(f'{q}: grid n=64 mean {g.mean():.3f} sd {g.std(ddof=1):.3f} | reps n=9 {np.round(r, 3).tolist()} sd {r.std(ddof=1):.3f}')
    print(f'   var ratio reps/grid {ratio:.3f}  F95 [{lo:.2f}, {hi:.2f}]  bootstrap95 [{bl:.2f}, {bh:.2f}]  sd ratio {ratio ** .5:.2f}')
    print(f'   grid shares init {vi / tot:.2f} data {vd / tot:.2f} resid {mse / tot:.2f}; reps/resid-var {ratio_res:.2f} F95 [{lo_r:.2f}, {hi_r:.2f}]; '
          f'Brown-Forsythe p {lev.pvalue:.3f}; high-mode (>=.5) grid {int((g >= .5).sum())}/64 reps {int((r >= .5).sum())}/9')
    out[q] = dict(grid_var=vg, rep_var=vr, ratio=ratio, F95=[lo, hi], boot95=[bl, bh], shares=[vi / tot, vd / tot, mse / tot],
                  ratio_resid=ratio_res, F95_resid=[lo_r, hi_r], reps=r.tolist())
json.dump(out, open('/home/dan/review/claim-audit/rv/C567_c7_out.json', 'w'), indent=1)
