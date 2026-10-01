#!/usr/bin/env python3
"""Reviewer statistics: per-seed values (own recount, recount.json) + inherited values (textbook72 from the reviewed
dan_textbook72 recount; Q for SN-cap12 from review_state-cap12.md), means, IQM (scipy-free: 25 % trimmed mean with
fractional weights, as Agarwal et al.), stratified bootstrap 95 % CI of IQM differences, and the pre-registered tests."""
import json, os, random, statistics as stt, math
R = os.path.expanduser('~/review/best-state')
rc = json.load(open(f'{R}/review_bs/recount.json'))
def iqm(x):
    x = sorted(x); n = len(x); lo, hi = 0.25 * n, 0.75 * n; tot = 0; w = 0
    for i, v in enumerate(x):
        a = max(0, min(1, min(i + 1, hi) - max(i, lo)))
        tot += a * v; w += a
    return tot / w
V = {}
for cell, seeds in (('best6', (0, 1, 2)), ('best12', (0, 1, 2)), ('SN6', (0, 1)), ('SN12', (0, 1, 2, 3))):
    for st in ('Fz', 'T1'):
        for pool in ('dev', 'h250', 'tb72', 'rr600', 'long2', 'held'):
            vals = []
            for s in seeds:
                k = f'{st}_{cell}_s{s}__{pool}'
                if pool == 'held' and st == 'Fz' and cell.startswith('best'): k = f'heldout_{cell}_s{s}_b1200'
                if k in rc:
                    d = rc[k]; vals.append(d['Q'] if pool == 'rr600' else d['solved'] / (d['n'] if pool == 'held' else 1))
            if len(vals) == len(seeds): V[(st, cell, pool)] = vals
# inherited (not re-read here)
V[('Fz', 'SN6', 'tb72')] = [16, 14]; V[('T1', 'SN6', 'tb72')] = [22, 16]
V[('Fz', 'SN12', 'tb72')] = [26, 29, 32, 26]; V[('T1', 'SN12', 'tb72')] = [37, 38, 36, 38]
V[('T1', 'SN12', 'rr600')] = [233, 295, 320, 317]
rng = random.Random(0)
def boot(a, b, B=20000):
    ds = sorted(iqm([rng.choice(a) for _ in a]) - iqm([rng.choice(b) for _ in b]) for _ in range(B))
    return ds[int(0.025 * B)], ds[int(0.975 * B)]
def welch(a, b):
    va, vb = (stt.variance(a) if len(a) > 1 else 0), (stt.variance(b) if len(b) > 1 else 0)
    se = math.sqrt(va / len(a) + vb / len(b)); return (stt.mean(a) - stt.mean(b)) / se if se else float('inf')
rows = []
for (st, cell, pool), v in sorted(V.items()):
    rows.append(dict(stage=st, cell=cell, pool=pool, per_seed=v, mean=stt.mean(v), iqm=iqm(v), sd=stt.stdev(v) if len(v) > 1 else None))
    print(st, cell, pool, v, 'mean %.4g iqm %.4g sd %s' % (stt.mean(v), iqm(v), '%.3g' % stt.stdev(v) if len(v) > 1 else '-'))
MDD = {('tb72', '6'): 9.3, ('tb72', '12'): 6.5, ('dev', '6'): 88, ('dev', '12'): 61}
cmp = []
print('\nbest - ours (IQM), prereg MDD, Welch t, bootstrap 95% CI of IQM difference, observed-SD MDD')
for pool in ('tb72', 'dev', 'h250', 'held', 'rr600', 'long2'):
    for cap in ('6', '12'):
        for st in ('Fz', 'T1'):
            a = V.get((st, 'best' + cap, pool)); b = V.get((st, 'SN' + cap, pool))
            if not a or not b: continue
            d = iqm(a) - iqm(b); lo, hi = boot(a, b)
            sp = math.sqrt(((len(a) - 1) * stt.variance(a) + (len(b) - 1) * stt.variance(b)) / (len(a) + len(b) - 2))
            # two-sample t MDD at 80 % power, alpha 0.05 two-sided: (t_{.975,df} + t_{.8,df}) * sp * sqrt(1/na + 1/nb)
            df = len(a) + len(b) - 2; tq = {3: (3.182, 0.978), 4: (2.776, 0.941), 5: (2.571, 0.920)}[df]
            mdd_obs = (tq[0] + tq[1]) * sp * math.sqrt(1 / len(a) + 1 / len(b))
            c = dict(pool=pool, cap=cap, stage=st, best=a, ours=b, diff_iqm=d, diff_mean=stt.mean(a) - stt.mean(b), welch_t=welch(a, b),
                     boot95=[lo, hi], mdd_prereg=MDD.get((pool, cap)), mdd_obs_sd=mdd_obs)
            cmp.append(c)
            print(f'{pool:6} cap{cap:2} {st}: best {a} ours {b}  diff_iqm {d:+.4g} (mean {c["diff_mean"]:+.4g})  MDD_prereg {c["mdd_prereg"]}  '
                  f'MDD_obsSD {mdd_obs:.3g}  t {c["welch_t"]:.2f}  boot95 [{lo:+.4g},{hi:+.4g}]')
# cap-12 advantage on textbook72 T1
b_adv = iqm(V[('T1', 'best12', 'tb72')]) - iqm(V[('T1', 'best6', 'tb72')])
o_adv = iqm(V[('T1', 'SN12', 'tb72')]) - iqm(V[('T1', 'SN6', 'tb72')])
print(f'\ncap-12 advantage tb72 T1: best {b_adv:.2f}, ours {o_adv:.2f}, difference {b_adv - o_adv:+.2f}')
for st in ('Fz', 'T1'):
    for pool in ('dev', 'h250', 'held'):
        try:
            print(f'cap-12 advantage {pool} {st}: best {iqm(V[(st,"best12",pool)]) - iqm(V[(st,"best6",pool)]):+.4g}, ours {iqm(V[(st,"SN12",pool)]) - iqm(V[(st,"SN6",pool)]):+.4g}')
        except KeyError: pass
json.dump(dict(rows=rows, cmp=cmp, cap12_adv_tb72_T1=dict(best=b_adv, ours=o_adv)), open(f'{R}/review_bs/stats.json', 'w'), indent=1)
