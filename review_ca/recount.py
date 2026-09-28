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
print('evals', len(rows), 'integrity issues', issues[:10], len(issues))

rate = lambda stem, s: float(np.mean([rows[stem][i]['lean_ok'] for i in SL[s]]))
# max_new: rows that emitted no text (never <eos>) vs .json hit_max_new
hm = collections.Counter()
for st, rr in rows.items():
    for i, r in enumerate(rr):
        if not r['text']:
            hm['notext'] += 1
    hm['json_hit'] += meta[st]['hit_max_new']
    hm['stop_eos'] += meta[st]['sampler_stats'].get('stop_eos', 0)
    hm['rows'] += 2500
print('max_new:', dict(hm))
pk = [m['sampler_stats']['peak_alloc_gb'] for m in meta.values()]
print('peak_alloc_gb min/max', min(pk), max(pk), 'n_params set', {m['model']['n_params'] for m in meta.values()})
# training-set label per eval
print('train data', collections.Counter((st.split('.')[0][0], (m['model']['train_args'] or {}).get('data')) for st, m in meta.items()))

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

W = [f'w_s{k}' for k in range(8)]; F = [f'f_s{k}' for k in range(4)]
VARS = ['E24', 'A24_K2', 'A24_K4', 'A24_K8', 'T24_3', 'T24_5', 'LS6', 'LSd3', 'E12', 'A12_K2', 'A12_K4', 'A12_K8', 'E6', 'A6_K2', 'A6_K4']
BINS = ['len2', 'len3', 'len4', 'len5', 'len6', 'd3', 'nd3_6', 'all']
out = {}
for arm, runs in (('W', W), ('F', F)):
    print(f'\n==== arm {arm}')
    for V in VARS:
        ck = [variant(s, V) for s in runs]
        if not all(c in rows for c in ck): continue
        tab = {b: [rate(c, b) for c in ck] for b in BINS}
        out[(arm, V)] = (ck, tab)
        sel = ' sel=' + ','.join(c.split('.')[-1] if '.' in c else c for c in ck) if V.startswith('LS') else ''
        print(f'{V:8s} ' + ' '.join(f'{b}:{np.mean(tab[b]):.4f}/{np.std(tab[b], ddof=1):.4f}' for b in BINS) + sel)
        print(f'         d3 per seed ' + ' '.join(f'{x:.3f}' for x in tab['d3']) + '   len6 per seed ' + ' '.join(f'{x:.3f}' for x in tab['len6']))
json.dump({f'{a}|{v}': {'ck': ck, 'tab': tab} for (a, v), (ck, tab) in out.items()}, open('recount_tables.json', 'w'), indent=0)

# ---- adoption rule (arm W, n=8, point estimates) + F-test CI on sd ratio
from math import sqrt
def f_ppf(p, d1, d2):  # bisection on regularized incomplete beta via scipy-free series
    import scipy.stats as ss
    return ss.f.ppf(p, d1, d2)
try:
    import scipy.stats as ss; HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False
print('\n==== adoption rule, arm W vs E24 (sd ddof=1)')
e = out[('W', 'E24')][1]
for V in ['A24_K2', 'A24_K4', 'A24_K8', 'T24_3', 'T24_5', 'LS6', 'LSd3']:
    t = out[('W', V)][1]
    r_d3 = np.std(t['d3'], ddof=1) / np.std(e['d3'], ddof=1)
    c1 = r_d3 <= 0.5
    c2 = np.std(t['len6'], ddof=1) < np.std(e['len6'], ddof=1)
    drops = {b: np.mean(t[b]) - np.mean(e[b]) for b in ['len2', 'len3', 'len4', 'len5', 'len6', 'd3']}
    c3 = all(v >= -0.02 for v in drops.values())
    ci = ''
    if HAVE_SCIPY:
        lo, hi = ss.f.ppf(0.025, 7, 7), ss.f.ppf(0.975, 7, 7)
        ci = f' ratio CI [{r_d3 / sqrt(hi):.2f},{r_d3 / sqrt(lo):.2f}]'
    print(f'{V:8s} d3 sd ratio {r_d3:.3f}{ci} (i){c1} len6 sd {np.std(t["len6"], ddof=1):.4f} vs {np.std(e["len6"], ddof=1):.4f} (ii){c2} '
          f'(iii){c3} worst drop {min(drops.values()):+.4f} ({min(drops, key=drops.get)}) -> {"ADOPT" if c1 and c2 and c3 else "no"}')

# ---- IQM with stratified bootstrap (over seeds) for d3, arm W
rng = np.random.default_rng(0)
def iqm(x):
    x = np.sort(x); n = len(x); lo, hi = int(np.floor(n * .25)), int(np.ceil(n * .75))
    return float(np.mean(x[lo:hi]))
print('\n==== IQM d3 (arm W, n=8) with bootstrap 95% CI')
for V in ['E24', 'A24_K2', 'A24_K4', 'A24_K8', 'T24_3', 'T24_5', 'LS6', 'LSd3']:
    x = np.array(out[('W', V)][1]['d3'])
    bs = [iqm(rng.choice(x, len(x))) for _ in range(5000)]
    print(f'{V:8s} IQM {iqm(x):.3f} [{np.percentile(bs, 2.5):.3f},{np.percentile(bs, 97.5):.3f}] mean {x.mean():.3f}')
