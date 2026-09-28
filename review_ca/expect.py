import collections, numpy as np
from rvload import *
AV = {}
for l in open('/dev/stdin'):
    n, m = l.rstrip('\n').split('\t'); AV[n] = m.split(',')
# truncation in the reported variants
W = [f'w_s{k}' for k in range(8)]; F = [f'f_s{k}' for k in range(4)]
tr = collections.Counter()
for s in W + F:
    for V in ['E24', 'A24_K2', 'A24_K4', 'A24_K8', 'T24_3', 'T24_5', 'LS6', 'LSd3']:
        c = variant(s, V) if 'w' in s or V not in ('E12', 'E6') else None
        if c in rows:
            tr[V] += sum(1 for i in SL['d3'] if not rows[c][i]['text'])
print('d3 truncated rows summed over runs, reported variants:', dict(tr))
# expectation 1: every A and T within 3pp of mean of constituents on len2-5 (pooled len2..5); falsified if >5pp below worst constituent
L25 = SL['len2'] + SL['len3'] + SL['len4'] + SL['len5']
r25 = lambda c: float(np.mean([rows[c][i]['lean_ok'] for i in L25]))
rd3 = lambda c: rate(c, 'd3')
fals, within3, n = [], 0, 0
above_mean = collections.Counter(); below_max = collections.Counter(); cnt = collections.Counter()
for name, mem in AV.items():
    if 'CTRL' in name: continue
    n += 1
    v = r25(name); ms = [r25(m.replace('w_s', 'w_s') if m in rows else m) for m in mem]
    if abs(v - np.mean(ms)) <= 0.03: within3 += 1
    if v < min(ms) - 0.05: fals.append((name, round(v, 4), round(min(ms), 4)))
    V = name.split('.')[1]
    if name.startswith('w_s'):
        d = rd3(name); md = [rd3(m) for m in mem]
        cnt[V] += 1; above_mean[V] += d > np.mean(md); below_max[V] += d < max(md)
print(f'exp1: {within3}/{n} averages within 3pp of constituents mean on len2-5; >5pp below worst: {len(fals)}')
for f in fals: print('   ', f)
print('overall (all) min over A/T variants:', min(rate(k, 'all') for k in AV if 'CTRL' not in k))
worst_all = sorted((rate(k, 'all'), k) for k in AV if 'CTRL' not in k)[:5]; print('   lowest overall', worst_all)
print('exp2 (W): d3 avg > mean(constituents) / < max(constituents), per variant (n seeds):')
for V in cnt: print(f'   {V:8s} above-mean {above_mean[V]}/{cnt[V]}  below-max {below_max[V]}/{cnt[V]}')
dirs = collections.Counter(); byV = collections.defaultdict(list)
for name, mem in AV.items():
    if 'CTRL' in name: continue
    dlt = r25(name) - np.mean([r25(m) for m in mem]); byV[name.split('.')[1]].append(dlt)
    if abs(dlt) > 0.03: dirs['above' if dlt > 0 else 'below'] += 1
print('exp1 outside-3pp direction', dict(dirs))
for V, x in byV.items(): print(f'   {V:8s} len2-5 avg minus constituents mean: min {min(x):+.3f} max {max(x):+.3f} mean {np.mean(x):+.3f}')
