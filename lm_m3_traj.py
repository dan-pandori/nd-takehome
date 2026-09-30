#!/usr/bin/env python3
"""lit-measures M3 addendum (post hoc, not pre-registered): per-seed trajectories of the NEW-proof depth>=3 share
(share / n new, rounds 1..8) for every arm, from artifacts/lit-measures/m3/per_round.tsv (pool `found`), plus the
end gap between seeds (max - min final cumulative share) for EI vs frozen arms.  -> artifacts/lit-measures/m3/trajectories.txt"""
import csv, collections
R = [r for r in csv.DictReader(open('artifacts/lit-measures/m3/per_round.tsv'), delimiter='\t') if r['pool'] == 'found']
t = collections.defaultdict(dict); cum = collections.defaultdict(dict); role = {}
for r in R:
    k = (r['family'], r['arm'], r['seed']); rd = int(r['round']); role[k[:2]] = r['role']
    t[k][rd] = (float(r['new_d3p'] or 'nan'), int(r['n_new'])); cum[k][rd] = float(r['cum_d3p'] or 'nan')
out = []
for k in sorted(t):
    out.append(f"{role[k[:2]]:8s} {k[0]:14s} {k[1]:24s} s{k[2]:2s} " + ' '.join(f"{t[k][x][0]:.2f}/{t[k][x][1]}" for x in sorted(t[k])))
gap = collections.defaultdict(list)
for k in cum:
    gap[k[:2]].append((cum[k][1], cum[k][max(cum[k])]))
out.append('\nseed spread (max - min) of the cumulative depth>=3 share, round 1 -> last round, arms with >= 2 seeds:')
for a in sorted(gap):
    v = gap[a]
    if len(v) >= 2:
        f = lambda i: max(x[i] for x in v) - min(x[i] for x in v)
        out.append(f"  {role[a]:8s} {a[0]:14s} {a[1]:24s} n={len(v)}  r1 {f(0):.3f} -> last {f(1):.3f}")
open('artifacts/lit-measures/m3/trajectories.txt', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out[-45:]))
