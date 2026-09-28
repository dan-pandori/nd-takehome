"""Reviewer recount: 14 equivalence comparisons from per-record files (own slicing)."""
import json, glob, math, numpy as np
from scipy import stats
recs = [json.loads(l) for l in open('data/p2/heldout.jsonl')]
L = np.array([r['n_lines'] for r in recs]); D3 = np.array([bool((r.get('pat') or {}).get('depth3')) for r in recs])
SL = {'all': np.ones(len(recs), bool), **{f'len{k}': L == k for k in range(2, 7)}, 'nodepth3_len6': (L == 6) & ~D3, 'depth3': D3}
print({k: int(v.sum()) for k, v in SL.items()})
def rates(fn):
    rows = [json.loads(l) for l in open(fn)]
    assert [r['name'] for r in rows] == [r['name'] for r in recs], fn
    ok = np.array([r['lean_ok'] for r in rows]); assert not (ok & ~np.array([r['parsed'] for r in rows])).any()
    return {k: ok[m].mean() for k, m in SL.items()}, ok
new = {s: rates(f) for s, f in [(int(f.split('_s')[-1][:-6]), f) for f in glob.glob('artifacts/fs/ev/*.jsonl')]}
old = {s: rates(f'rv/oldc/c_s{s}.jsonl') for s in range(8)}
# consistency with the executor's own .json summaries
for s in range(8):
    js = json.load(open(glob.glob(f'artifacts/fs/ev/*_s{s}.json')[0]))
    for k in SL:
        assert abs(js['slices'][k]['rate'] - new[s][0][k]) < 1e-12, (s, k)
    assert js['sampler']['batch'] == 512 and js['sampler']['max_new'] == 400 and js['model']['train_args']['seed'] == s
    assert js['model']['train_args']['impl'] == 'fast' and js['model']['train_args']['bs'] == 128 and js['model']['train_args']['steps'] == 6000
c = stats.t.ppf(.975, 14) + stats.t.ppf(.80, 14); K = c * math.sqrt(2 / 8)
print('MDD constant n=8:', round(K, 4), ' check n=2:', round((stats.t.ppf(.975, 2) + stats.t.ppf(.8, 2)), 4))
NF = {'all': .03038, 'len2': .003128, 'len3': .00486, 'len4': .01512, 'len5': .01502, 'len6': .1523, 'nodepth3_len6': .03667}
print(f"{'slice':14s} {'new mean':>9s} {'C mean':>9s} {'diff pp':>8s} {'MDD pp':>7s} {'|d|/MDD':>7s} {'sd_new':>7s} {'sd_C':>7s} {'MWU p':>6s}")
for k in NF:
    a = np.array([new[s][0][k] for s in range(8)]); b = np.array([old[s][0][k] for s in range(8)])
    d = a.mean() - b.mean(); mdd = K * NF[k]
    print(f"{k:14s} {a.mean():9.4f} {b.mean():9.4f} {100*d:8.3f} {100*mdd:7.3f} {abs(d)/mdd:7.2f} {a.std(ddof=1):7.4f} {b.std(ddof=1):7.4f} {stats.mannwhitneyu(a,b).pvalue:6.3f}")
a = np.array([new[s][0]['depth3'] for s in range(8)]); b = np.array([old[s][0]['depth3'] for s in range(8)])
print('depth3 new', np.round(a, 3), 'high-mode', (a > .44).sum()); print('depth3 C  ', np.round(b, 3), 'high-mode', (b > .44).sum())
for k in ['all', 'len6', 'nodepth3_len6']:
    print(k, 'new per seed', np.round([new[s][0][k] for s in range(8)], 4)); print(k, 'C   per seed', np.round([old[s][0][k] for s in range(8)], 4))
# IQM + stratified bootstrap
def iqm(x):
    x = np.sort(x); n = len(x); lo = int(np.floor(n * .25)); hi = int(np.ceil(n * .75)); return x[lo:hi].mean()
rng = np.random.default_rng(0)
for k in ['all', 'len6', 'nodepth3_len6', 'depth3']:
    a = np.array([new[s][0][k] for s in range(8)]); b = np.array([old[s][0][k] for s in range(8)])
    bs = [iqm(rng.choice(a, 8)) - iqm(rng.choice(b, 8)) for _ in range(10000)]
    print(f'IQM {k}: new {iqm(a):.4f} C {iqm(b):.4f} diff {100*(iqm(a)-iqm(b)):.2f} pp 95% [{100*np.percentile(bs,2.5):.2f}, {100*np.percentile(bs,97.5):.2f}]')
# term size of counted proofs
for nm, src in (('new', new), ('C', old)):
    pass
