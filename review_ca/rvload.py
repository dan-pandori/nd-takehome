"""Reviewer recount for run ckpt-avg (own code; reads only raw per-theorem files + half-A losses)."""
import json, gzip, glob, os, statistics as S, math, collections, sys
import numpy as np
R = '..'
EV = f'{R}/artifacts/ca/ev'
B = [json.loads(l) for l in open(f'{R}/data/ca/heldout_B.jsonl')]
bname = [r['name'] for r in B]
bd3 = [bool(r['pat']['depth3']) for r in B]
blen = [r['n_lines'] for r in B]
SL = {'len2': [i for i in range(2500) if blen[i] == 2], 'len3': [i for i in range(2500) if blen[i] == 3],
      'len4': [i for i in range(2500) if blen[i] == 4], 'len5': [i for i in range(2500) if blen[i] == 5],
      'len6': [i for i in range(2500) if blen[i] == 6], 'd3': [i for i in range(2500) if bd3[i]],
      'nd3_6': [i for i in range(2500) if blen[i] == 6 and not bd3[i]], 'all': list(range(2500))}
assert len(SL['d3']) == 250 and all(blen[i] == 6 for i in SL['d3'])

rows, meta, issues = {}, {}, []
for fj in sorted(glob.glob(f'{EV}/*.jsonl.gz')):
    stem = os.path.basename(fj)[:-9]
    rr = [json.loads(l) for l in gzip.open(fj, 'rt')]
    m = json.load(open(f'{EV}/{stem}.json'))
    if len(rr) != 2500: issues.append((stem, 'n', len(rr)))
    for i, r in enumerate(rr):
        if r['name'] != bname[i] or r['depth3'] != bd3[i] or r['n_lines'] != blen[i]:
            issues.append((stem, 'row mismatch', i)); break
        if r['lean_ok'] and not r['parsed']: issues.append((stem, 'ok-unparsed', i))
        if r['lean_ok'] and not r['text']: issues.append((stem, 'ok-no-text', i))
    ok = np.array([r['lean_ok'] for r in rr])
    for s, ii in [('len2', 'len2'), ('len6', 'len6'), ('depth3', 'd3'), ('all', 'all')]:
        if m['slices'][s]['solved'] != int(ok[SL[ii]].sum()): issues.append((stem, 'slice', s))
    if m['heldout'] != 'data/ca/heldout_B.jsonl' or m['sampler']['batch'] != 2500 or m['sampler']['max_new'] != 400 \
            or m['sampler']['compact'] != '1' or m['sampler']['path'] != 'fast' or not m['sampler']['greedy']:
        issues.append((stem, 'settings', m['sampler'], m['heldout']))
    if os.path.basename(m['ckpt'])[:-3] != stem: issues.append((stem, 'ckpt path', m['ckpt']))
    rows[stem] = rr; meta[stem] = m


rate = lambda stem, s: float(np.mean([rows[stem][i]['lean_ok'] for i in SL[s]]))

# ---- half-A validation loss -> my own LS selection
VL = {}
for l in open(f'{R}/artifacts/ca/valloss_A.jsonl'):
    d = json.loads(l); VL[os.path.basename(d['ckpt'])[:-3]] = d
assert all(d['val'] == 'data/ca/heldout_A.jsonl' for d in VL.values())

def cands(stem):
    k = stem.split('_s')[1]
    if stem[0] == 'w':
        return [f'w_s{k}.step{t:05d}' for t in range(1000, 24000, 1000)] + [f'w_s{k}', f'w12_s{k}', f'w6_s{k}']
    return [f'f_s{k}.step{t:05d}' for t in range(2000, 24000, 2000)] + [f'f_s{k}']

def ls(stem, key):
    c = cands(stem); assert all(x in VL for x in c), stem
    v = sorted((VL[x]['loss'][key], x) for x in c)
    if len(v) > 1 and v[0][0] == v[1][0]: print('TIE', stem, key, v[:2])
    return v[0][1]

def variant(stem, V):
    k = stem.split('_s')[1]
    if V == 'E24': return stem
    if V == 'E12': return f'w12_s{k}'
    if V == 'E6': return f'w6_s{k}'
    if V == 'LS6': return ls(stem, 'len6')
    if V == 'LSd3': return ls(stem, 'depth3')
    return f'{stem}.{V}'

