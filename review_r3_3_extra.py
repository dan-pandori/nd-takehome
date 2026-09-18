#!/usr/bin/env python3
"""Reviewer extras for round3-run3: like-for-like required strata, post-hoc predictor robustness, derived-ORE required targets.
  ROOT=~/review/round3-run3 python3 review_r3_3_extra.py >> artifacts/review_r3_3/tables.txt"""
import json, os, collections, math
from scipy.stats import spearmanr, fisher_exact
from review_r3_3_tables import cov, logs, req8, SEEDS, cp, perm_rho, rd, ROOT, hr, hfull, hdr, hdd, er, ed
print('\n== 9. like-for-like: required targets only')
d3 = {x['name']: x for x in rd(f'{ROOT}/data/r3_3/targets_depth3_p1.jsonl') + rd(f'{ROOT}/data/r3_3/targets_depth3_p2.jsonl')}
print(' required@8 depth-3 targets by unrestricted min length:', dict(collections.Counter(d3[t]['min_lines_ub'] for t in req8)))
r7 = {t for t in req8 if d3[t]['min_lines_ub'] == 7}
per = []
for s in SEEDS:
    t = dict(cov['d3p1'][s]['pattern_targets']); t.update(cov['d3p2'][s]['pattern_targets'])
    per.append((sum(v for k, v in t.items() if k in r7), sum(v for k, v in t.items() if k in req8 and k not in r7)))
print(' depth-3 hits on required@8 targets, (7-line, 8-line) per draw:', {s: p for s, p in zip(SEEDS, per) if sum(p)})
k = sum(1 for p in per if sum(p)); print(' depth-3 required-only:', cp(k, 24), ' reductio (all required):', cp(sum(h > 0 for h in hr), 24), ' Fisher p =', round(fisher_exact([[k, 24 - k], [12, 12]])[1], 4))
print(' per-sample rate on required targets, pooled over 24 draws: depth-3', sum(sum(p) for p in per), '/', 24 * 142 * 2000, ' reductio 7-line', sum(hr), '/', 24 * 52 * 2000, ' reductio whole pool', sum(hr), '/', 24 * 600000)
print(' depth-3 hit targets: is a depth<=2 proof of the same length available?  (min_lines_ub, md2_min_lines_ub) of the 76 hit targets:',
      dict(collections.Counter((d3[t]['min_lines_ub'], d3[t]['md2_min_lines_ub']) for s in SEEDS for f in ('d3p1', 'd3p2') for t in cov[f][s]['pattern_targets'])))
print('\n== 10. post-hoc predictor robustness (depth-3 by_rule NEGI loss; reductio by_rule AS loss)')
for nm, st, rule, ind, e, deep in (('depth-3', 'depth3_f0_a1', 'NEGI', [int(h > 0) for h in hfull], ed, hdd), ('reductio', 'reductio_f0', 'AS', [int(h > 0) for h in hr], er, hdr)):
    x = [logs[f'{st}_s{s}']['by_rule'][rule] for s in SEEDS]
    print(f' {nm} {rule}: vs main indicator %.3f, %.5f' % perm_rho(x, ind), '| vs deep-pass indicator %.3f, %.5f' % perm_rho(x, [int(h > 0) for h in deep]),
          '| vs either %.3f, %.5f' % perm_rho(x, [int(v) for v in e]), '| vs deep hits %.3f, %.5f' % perm_rho(x, deep))
    print('   loss range', round(min(x), 4), round(max(x), 4))
for pred in ('negi_neggoal', 'neg_goal_hyp', 'negi_neggoal_nodn'):
    fh = [cov['red'][s]['fh_all'].get(pred, 0) / 6e5 for s in SEEDS]
    print(f' reductio {pred}: range {min(fh):.1e}-{max(fh):.1e}; vs main indicator %.3f, %.4f' % perm_rho(fh, [int(h > 0) for h in hr]), '| vs deep hits %.3f, %.4f' % perm_rho(fh, hdr))
for pred in ('d3_as_as', 'd2_two_boxes', 'd3_written'):
    fh = [(cov['d3p1'][s]['fh_all'].get(pred, 0)) / 6e5 for s in SEEDS]
    print(f' depth-3 {pred} (part 1): range {min(fh):.1e}-{max(fh):.1e}; vs main indicator %.3f, %.4f' % perm_rho(fh, [int(h > 0) for h in hfull]), '| vs deep hits %.3f, %.4f' % perm_rho(fh, hdd))
# first-half restricted to the targets where hits happen (7-line reductio targets): deep pass fh vs deep hits
fh = [cov['deepred'][s]['fh_all'].get('negi_neggoal_nodn', 0) / 1.04e6 for s in SEEDS]
print(' reductio deep pass: negi_neggoal_nodn rate on the 52 seven-line targets vs deep hits %.3f, %.4f' % perm_rho(fh, hdr), '| vs MAIN indicator %.3f, %.4f' % perm_rho(fh, [int(h > 0) for h in hr]))
fh = [cov['deepd3'][s]['fh_all'].get('d3_written', 0) / 9e5 for s in SEEDS]
print(' depth-3 deep pass: d3_written rate on the 45 targets vs deep hits %.3f, %.4f' % perm_rho(fh, hdd), '| vs MAIN indicator %.3f, %.4f' % perm_rho(fh, [int(h > 0) for h in hfull]))
print('\n== 11. derived-ORE: required targets')
dp = {x['name']: x for x in rd(f'{ROOT}/data/r3_3/targets_derived_ore_strict_c6.jsonl')}
tot = collections.Counter()
for s in SEEDS:
    for x in rd(f'{ROOT}/artifacts/r3_3/cov_derived_ore_f0_s{s}_dos6.s0.jsonl'):
        req = dp[x['name']]['requires']; tot[('req' if req else 'opt', 'targets')] += 1; tot[('req' if req else 'opt', 'solved')] += x['n_ok'] > 0; tot[('req' if req else 'opt', 'n_ok')] += x['n_ok']
        tot[('req' if req else 'opt', 'ore_on_derived_all')] += x['fh_by_pred']['ore_on_derived']; tot[('req' if req else 'opt', 'loose_ok')] += x['hits_by_pattern']['derived_ore']
print(' ', {f'{a}_{b}': v for (a, b), v in sorted(tot.items())})
print('\n== 12. cross-set: do same-seed draws co-generalise? (seed is the only shared factor)')
print(' reductio vs depth-3 main indicators, Fisher p:', round(fisher_exact([[sum(1 for a, b in zip(hr, hfull) if a > 0 and b > 0), sum(1 for a, b in zip(hr, hfull) if a > 0 and b == 0)],
                                                                      [sum(1 for a, b in zip(hr, hfull) if a == 0 and b > 0), sum(1 for a, b in zip(hr, hfull) if a == 0 and b == 0)]])[1], 3))
print('\n== 13. depth-3 pool by (unrestricted min, depth<=2 min at bound 8): targets, depth-3 hits, other verified samples, draws with a depth-3 hit')
comp = collections.Counter(); hitsc = collections.Counter(); other = collections.Counter(); drawsc = collections.defaultdict(set); wl = collections.Counter()
for t, x in d3.items():
    comp[(x['min_lines_ub'], x['md2_min_lines_ub'])] += 1
for s in SEEDS:
    for f, part in (('d3p1', 'p1'), ('d3p2', 'p2')):
        pt = cov[f][s]['pattern_targets']
        for k2, v in cov[f][s]['pattern_hits_by_written_len'].items():
            wl[k2] += v
        for x in rd(f'{ROOT}/artifacts/r3_3/cov_depth3_f0_a1_s{s}_{part}.s0.jsonl'):
            c = (d3[x['name']]['min_lines_ub'], d3[x['name']]['md2_min_lines_ub']); h = pt.get(x['name'], 0)
            hitsc[c] += h; other[c] += x['n_ok'] - h
            if h:
                drawsc[c].add(s)
for c in sorted(comp, key=str):
    print(f'  min {c[0]}, depth<=2 min {c[1]}: targets {comp[c]:>4}  depth-3 hits {hitsc[c]:>6}  other verified {other[c]:>8}  draws with depth-3 hit {len(drawsc[c])}')
print(' depth-3 hits by written length:', dict(wl))
print('\n== 14. like-for-like at the 7-line horizon: targets whose 7-line proof needs the pattern')
need7 = {t for t, x in d3.items() if x['min_lines_ub'] == 7 and x['md2_min_lines_ub'] != 7}
k7 = []; 
for s in SEEDS:
    t = dict(cov['d3p1'][s]['pattern_targets']); t.update(cov['d3p2'][s]['pattern_targets'])
    k7.append(sum(v for k2, v in t.items() if k2 in need7))
n7p1 = sum(1 for t in need7 if int(t.split('_')[-1]) < 300)
print(f' depth-3: {len(need7)} such targets ({n7p1} in part 1); draws with a hit on them:', cp(sum(v > 0 for v in k7), 24), '; pooled rate', sum(k7), '/', 24 * len(need7) * 2000, '=', f'{sum(k7) / (24 * len(need7) * 2000):.2e}')
print(f' reductio: 52 such targets; draws with a hit:', cp(sum(h > 0 for h in hr), 24), '; pooled rate', sum(hr), '/', 24 * 52 * 2000, '=', f'{sum(hr) / (24 * 52 * 2000):.2e}')
print(' per-draw rate on 7-line-pattern-needed targets, sorted: depth-3', sorted(f'{v / (len(need7) * 2000):.1e}' for v in k7 if v), '| reductio', sorted(f'{h / 104000:.1e}' for h in hr if h))
print(' median over generalisers: depth-3', sorted(v / (len(need7) * 2000) for v in k7 if v)[len([v for v in k7 if v]) // 2], ' reductio', sorted(h / 104000 for h in hr if h)[6])
