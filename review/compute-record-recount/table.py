"""Reviewer (compute-record): my own per-(arm, seed, round) sums of the pod's compute rows vs registry_merge.compute_table."""
import json, glob, collections, os, sys
sys.path.insert(0, os.getcwd())
A = os.path.expanduser('~/review/compute-record/artifacts/compute-record')
rows = [json.loads(l) for f in sorted(glob.glob(f'{A}/registry/*.jsonl')) for l in open(f)]
mine = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    L = r.get('labels') or {}
    if 'compute_id' not in L: continue
    k = (str(r.get('arm')), str(r.get('seed')), str(L.get('round')))
    m = r['metric']
    if m == 'gpu_seconds' and L['device'] == 'cpu': m = 'cpu_seconds'
    mine[k][m] += r['value']
    if r['metric'] == 'lean_checks': mine[k]['lean_s'] += L.get('lean_s', 0)
import registry_merge
t = registry_merge.compute_table(rows, ['arm', 'seed', 'round'])
diff = []
for k in set(mine) | set(t):
    for m in registry_merge.COMPUTE_COLS:
        a, b = round(mine.get(k, {}).get(m, 0), 3), round(t.get(k, {}).get(m, 0), 3)
        if abs(a - b) > 1e-6: diff.append((k, m, a, b))
for k in sorted(mine): print(k, dict(mine[k]))
print('differences vs registry_merge.compute_table:', diff)
