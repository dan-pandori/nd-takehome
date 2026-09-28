"""Reviewer phase-2 checks of specific executor claims (own code)."""
import json, gzip, subprocess, os, glob, collections, math
import numpy as np
from rvload import *
T = json.load(open('recount_tables.json'))
W = [f'w_s{k}' for k in range(8)]; Fr = [f'f_s{k}' for k in range(4)]
tq = {7: 2.3646, 3: 3.1824}
print('== paired depth-3 differences vs E24 (t 95 %), arm W')
e = np.array(T['W|E24']['tab']['d3'])
for V in ['A24_K8', 'T24_3', 'LS6', 'LSd3', 'A24_K2', 'A24_K4', 'T24_5']:
    d = np.array(T[f'W|{V}']['tab']['d3']) - e
    h = tq[7] * d.std(ddof=1) / math.sqrt(8)
    print(f'  {V:7s} {100 * d.mean():+.1f} pp [{100 * (d.mean() - h):+.1f}, {100 * (d.mean() + h):+.1f}]')
print('== LS6 per-bin drops incl. 6-line non-d3 (W)')
for b in ['len2', 'len3', 'len4', 'len5', 'len6', 'd3', 'nd3_6']:
    print(f'  {b}: LS6 {100 * (np.mean(T["W|LS6"]["tab"][b]) - np.mean(T["W|E24"]["tab"][b])):+.2f}  LSd3 {100 * (np.mean(T["W|LSd3"]["tab"][b]) - np.mean(T["W|E24"]["tab"][b])):+.2f}')
print('== trajectory-mean readout (mean of a run\'s trajectory checkpoints\' d3 rate)')
for arm, runs, steps in (('W', W, range(1000, 24000, 1000)), ('F', Fr, range(2000, 24000, 2000))):
    for incl in ('traj only', 'traj+E24'):
        per = []
        for s in runs:
            cks = [f'{s}.step{t:05d}' for t in steps] + ([s] if incl != 'traj only' else [])
            per.append(np.mean([rate(c, 'd3') for c in cks]))
        print(f'  {arm} {incl}: mean {np.mean(per):.3f} sd {np.std(per, ddof=1):.3f}')
print('== Spearman half-A d3 loss vs half-B d3 acc, 208 W ckpts')
cks = [c for s in W for c in cands(s)]
def rk(x):
    o = np.argsort(x, kind='stable'); r = np.empty(len(x)); r[o] = np.arange(len(x))
    # average ties
    xs = np.array(x); 
    for v in set(xs.tolist()):
        m = xs == v
        if m.sum() > 1: r[m] = r[m].mean()
    return r
a = rk([VL[c]['loss']['depth3'] for c in cks]); b = rk([rate(c, 'd3') for c in cks])
print('  n', len(cks), 'rho', round(float(np.corrcoef(a, b)[0, 1]), 3))
print('== re-draw vs stage1-dynamics (all ckpts in both, .jsonl or .jsonl.gz)')
tot = dis = d3t = d3d = n = 0
for st in rows:
    old = None
    for suf in ('.jsonl', '.jsonl.gz'):
        p = subprocess.run(['git', 'show', f'HEAD:artifacts/sd/ev/{st}{suf}'], capture_output=True, cwd='..')
        if p.returncode == 0:
            bb = gzip.decompress(p.stdout) if suf.endswith('gz') else p.stdout
            old = {r['name']: r for r in map(json.loads, bb.decode().splitlines())}; break
    if old is None: continue
    n += 1
    for r in rows[st]:
        x = old[r['name']]['lean_ok'] != r['lean_ok']; dis += x; tot += 1
        if r['depth3']: d3t += 1; d3d += x
print(f'  ckpts {n} rows {tot} differ {dis} ({100 * dis / tot:.2f} %), depth3 {d3d}/{d3t}')
print('== max hit_max_new in one eval', max(m['hit_max_new'] for m in meta.values()))
print('== A6_K4 overall < 0.80:', sum(rate(f'w_s{k}.A6_K4', 'all') < 0.80 for k in range(8)), '/ 8')
print('== sd_eval mean_term_size, mean over seeds of per-ckpt d3 means (executor convention?)')
for V in ['E24', 'LSd3', 'A24_K8']:
    xs = [meta[c]['slices']['depth3']['mean_term_size'] for c in T[f'W|{V}']['ck']]
    ls = [meta[c]['slices']['depth3']['mean_written_lines'] for c in T[f'W|{V}']['ck']]
    print(f'  {V}: mean of per-seed n_tok {np.mean([x for x in xs if x]):.1f}; lines {np.mean([x for x in ls if x]):.2f}; len6 n_tok {np.mean([meta[c]["slices"]["len6"]["mean_term_size"] for c in T[f"W|{V}"]["ck"]]):.1f}')
print('== CA3: per-bin min (average - constituents mean) on len2..len5; F A24_K8 above-mean on d3')
AV = dict(l.rstrip('\n').split('\t') for l in open('/tmp/rv_ca/av.tsv'))
mn = []
for nm, mem in AV.items():
    if 'CTRL' in nm: continue
    mem = mem.split(',')
    for b in ['len2', 'len3', 'len4', 'len5']:
        mn.append((rate(nm, b) - np.mean([rate(m, b) for m in mem]), nm, b))
        if rate(nm, b) < min(rate(m, b) for m in mem) - 1e-9: print('   below worst constituent:', nm, b)
print('  min', sorted(mn)[:3])
for V in ['A24_K2', 'A24_K4', 'A24_K8', 'T24_3']:
    c = sum(rate(f'{s}.{V}', 'd3') > np.mean([rate(m, 'd3') for m in AV[f'{s}.{V}'].split(',')]) for s in Fr)
    print(f'  F {V} above constituents mean on d3: {c}/4')
bt = sum(1 for s in W if min(rate(m, 'd3') for m in AV[f'{s}.A24_K8'].split(',')) <= rate(f'{s}.A24_K8', 'd3') <= max(rate(m, 'd3') for m in AV[f'{s}.A24_K8'].split(',')))
print('  W A24_K8 between min and max (inclusive):', bt, '/8')
