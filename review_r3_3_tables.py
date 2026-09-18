#!/usr/bin/env python3
"""Reviewer's analysis of the round3-run3 recount (reads artifacts/review_r3_3/*.json written by review_r3_3_recount.py).

  ROOT=~/review/round3-run3 python3 review_r3_3_tables.py > artifacts/review_r3_3/tables.txt
"""
import json, os, sys, math, collections, random
from scipy.stats import beta, spearmanr, fisher_exact

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.expanduser(os.environ.get('ROOT', HERE))
R = os.path.join(HERE, 'artifacts', 'review_r3_3')
SEEDS = [str(s) for s in range(30, 54)]
J = lambda n: json.load(open(os.path.join(R, n)))
rd = lambda fn: [json.loads(l) for l in open(fn) if l.strip()]


def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return f'{k}/{n} = {k/n:.3f} [{lo:.3f}, {hi:.3f}]'


def perm_rho(x, y, n=10000, seed=0):
    rho = spearmanr(x, y)[0]
    if rho != rho:
        return float('nan'), float('nan')
    rng = random.Random(seed); y = list(y); c = 0
    for _ in range(n):
        rng.shuffle(y)
        r = spearmanr(x, y)[0]
        c += abs(r) >= abs(rho) - 1e-12
    return rho, (c + 1) / (n + 1)


cov = {f: J(f'cov_{f}.json') for f in ['red', 'deepred', 'dos6', 'd3p1', 'd3p2', 'deepd3']}
logs = J('logs.json'); req8 = set(J('req8_names.json'))
hits = lambda f: [cov[f][s]['pattern_hits'] for s in SEEDS]
tried = lambda f: [cov[f][s]['n_tried'] for s in SEEDS]

print('== 1. E1 / E2: draws with >= 1 verified pattern sample (reviewer predicates, every stored proof re-verified)')
hr = hits('red'); h1 = hits('d3p1'); h2 = hits('d3p2'); hd = hits('dos6'); hdr = hits('deepred'); hdd = hits('deepd3')
hfull = [a + b for a, b in zip(h1, h2)]
print(' samples per draw: red', set(tried('red')), 'd3p1', set(tried('d3p1')), 'd3p2', set(tried('d3p2')), 'dos6', set(tried('dos6')), 'deepred', set(tried('deepred')), 'deepd3', set(tried('deepd3')))
print(' reductio  main (300 req, 600k):       ', cp(sum(h > 0 for h in hr), 24))
print(' depth-3   main p1+p2 (1000, 2M):      ', cp(sum(h > 0 for h in hfull), 24))
print(' depth-3   part 1 only (300, 600k):    ', cp(sum(h > 0 for h in h1), 24))
print(' derived-ORE strict (300, 600k):       ', cp(sum(h > 0 for h in hd), 24))
# depth-3 restricted to the required@8 stratum
r8 = []
for s in SEEDS:
    t = dict(cov['d3p1'][s]['pattern_targets']); t.update(cov['d3p2'][s]['pattern_targets'])
    r8.append(sum(v for k, v in t.items() if k in req8))
print(' depth-3   required@8 stratum only (142 targets, 284k):', cp(sum(h > 0 for h in r8), 24), ' hits', r8)
print(' depth-3   share of all main-pass depth-3 hits on required@8 targets:', sum(r8), '/', sum(hfull))
print(' reductio  deep (52, 1.04M):           ', cp(sum(h > 0 for h in hdr), 24))
print(' depth-3   deep (45, 0.9M):            ', cp(sum(h > 0 for h in hdd), 24))
er = [a > 0 or b > 0 for a, b in zip(hr, hdr)]; ed = [a > 0 or b > 0 for a, b in zip(hfull, hdd)]
print(' reductio  either pass:                ', cp(sum(er), 24), ' zero in both:', [s for s, e in zip(SEEDS, er) if not e])
print(' depth-3   either pass:                ', cp(sum(ed), 24), ' zero in both:', [s for s, e in zip(SEEDS, ed) if not e])
print(' Fisher exact depth-3 vs reductio, main:', fisher_exact([[sum(h > 0 for h in hfull), 24 - sum(h > 0 for h in hfull)], [sum(h > 0 for h in hr), 24 - sum(h > 0 for h in hr)]])[1],
      ' either pass:', fisher_exact([[sum(ed), 24 - sum(ed)], [sum(er), 24 - sum(er)]])[1])
# threshold sensitivity: draws at or above a per-sample rate
for thr in (1e-6, 1e-5, 1e-4):
    print(f' draws with main-pass rate >= {thr:g}: reductio', sum(h / 6e5 >= thr for h in hr), ' depth-3 p1', sum(h / 6e5 >= thr for h in h1),
          f'| deep-pass rate >= {thr:g}: reductio', sum(h / 1.04e6 >= thr for h in hdr), ' depth-3', sum(h / 9e5 >= thr for h in hdd))

print('\n== 2. per-draw table (seed: main hits / targets / frozen@256 | deep hits / targets)')
for fam, deep, nm in (('red', 'deepred', 'reductio'), ('d3p1', 'deepd3', 'depth-3 (p1; p2 in brackets)')):
    print(' ', nm)
    for s in SEEDS:
        a = cov[fam][s]; b = cov[deep][s]
        extra = f" [p2 {cov['d3p2'][s]['pattern_hits']}/{len(cov['d3p2'][s]['pattern_targets'])}/{cov['d3p2'][s]['frozen256_pattern_targets']}]" if fam == 'd3p1' else ''
        print(f"   s{s}: {a['pattern_hits']:>5} / {len(a['pattern_targets']):>2} / {a['frozen256_pattern_targets']:>2}{extra} | {b['pattern_hits']:>6} / {len(b['pattern_targets']):>2}   top-target share main {max(a['pattern_targets'].values(), default=0)}/{a['pattern_hits']}")

print('\n== 3. E3: rates and schemata')
for nm, h, n in (('reductio main', hr, 6e5), ('depth-3 p1+p2', hfull, 2e6), ('depth-3 p1', h1, 6e5), ('reductio deep', hdr, 1.04e6), ('depth-3 deep', hdd, 9e5)):
    nz = sorted(x / n for x in h if x)
    print(f' {nm}: generalisers {len(nz)}, rate min {nz[0]:.2e} max {nz[-1]:.2e}, span {math.log10(nz[-1] / nz[0]):.2f} decades; at 1-3 hits: {sum(1 for x in h if 0 < x <= 3)}')
pool = {x['name']: x for x in rd(f'{ROOT}/data/p2/targets_reductio_req.jsonl')}
sch = collections.Counter(); schd = collections.Counter(); schdraws = collections.defaultdict(set)
for s in SEEDS:
    for t, v in cov['red'][s]['pattern_targets'].items():
        sch[(pool[t]['schema'], pool[t]['min_lines_ub'])] += v; schdraws[pool[t]['schema']].add(s)
    for t, v in cov['deepred'][s]['pattern_targets'].items():
        schd[(pool[t]['schema'], pool[t]['min_lines_ub'])] += v
print(' reductio main-pass hits by (schema, min lines):', dict(sch), ' draws per schema:', {k: len(v) for k, v in schdraws.items()})
print(' reductio deep-pass hits by (schema, min lines):', dict(schd))
print(' reductio main: pattern hits by written length:', dict(sum((collections.Counter(cov['red'][s]['pattern_hits_by_written_len']) for s in SEEDS), collections.Counter())))
print(' reductio main: n_ok == pattern hits in every draw (nothing else is solved):', all(cov['red'][s]['n_ok'] == cov['red'][s]['pattern_hits'] for s in SEEDS))
print(' any verified proof on an 8+-line reductio schema target (any draw):', sum(1 for s in SEEDS for t in cov['red'][s]['pattern_targets'] if pool[t]['min_lines_ub'] > 7))

print('\n== 4. E5 depth-3 full-pool effect')
print(' draws with 0 on part 1 and >= 1 on part 2:', sum(1 for a, b in zip(h1, h2) if a == 0 and b > 0), '; share of hits in part 1:', sum(h1), '/', sum(hfull), '=', round(sum(h1) / sum(hfull), 4))
print(' part-2 hits per draw:', {s: h for s, h in zip(SEEDS, h2) if h})
d3pool = {x['name']: x for x in rd(f'{ROOT}/data/r3_3/targets_depth3_p1.jsonl') + rd(f'{ROOT}/data/r3_3/targets_depth3_p2.jsonl')}
tt = collections.Counter(); td = collections.defaultdict(set)
for s in SEEDS:
    for f in ('d3p1', 'd3p2'):
        for t, v in cov[f][s]['pattern_targets'].items():
            tt[t] += v; td[t].add(s)
print(' distinct depth-3 targets hit in main pass:', len(tt), '; of which required@8:', sum(1 for t in tt if t in req8), '; min_lines_ub of hit targets:', dict(collections.Counter(d3pool[t]['min_lines_ub'] for t in tt)),
      '; gen n_lines:', dict(collections.Counter(d3pool[t]['n_lines'] for t in tt)))
print(' top targets (hits, draws, required8):', [(t, v, len(td[t]), t in req8) for t, v in tt.most_common(6)])
d45 = {x['name'] for x in rd(f'{ROOT}/data/r3_3/targets_depth3_deep45.jsonl')}
print(' main-pass hit targets inside the deep-45 pool:', sum(1 for t in tt if t in d45), 'of', len(tt), '; hits inside:', sum(v for t, v in tt.items() if t in d45), 'of', sum(tt.values()))
print(' deep-45 pool: required@8', len(d45 & req8), 'of 45')

print('\n== 5. E4 / E7 predictors (Spearman rho, 10,000-permutation p)')
def fhrate(fams, pred, s, ok_only=False):
    num = sum(cov[f][s]['fh_ok_file' if ok_only else 'fh_all'].get(pred, 0) for f in fams); den = sum(cov[f][s]['n_tried'] for f in fams)
    return num / den
for nm, st, fams, pred, h, e, hdeep in (('reductio', 'reductio_f0', ['red'], 'negi_neggoal_nodn', hr, er, hdr), ('depth-3', 'depth3_f0_a1', ['d3p1', 'd3p2'], 'd3_written', hfull, ed, hdd)):
    ind = [int(x > 0) for x in h]
    val = [logs[f'{st}_s{s}']['final_val'] for s in SEEDS]; bt = [logs[f'{st}_s{s}']['breakdown_total_mean'] for s in SEEDS]
    fh = [fhrate(fams, pred, s) for s in SEEDS]
    print(f' {nm}: final val (4-decimal log value) distinct values {len(set(val))}, range {min(val)}-{max(val)}; breakdown mean range {min(bt):.4f}-{max(bt):.4f}')
    print(f'   val vs indicator rho, p = %.3f, %.4f' % perm_rho(val, ind), '| breakdown mean vs indicator %.3f, %.4f' % perm_rho(bt, ind), '| vs either-pass indicator %.3f, %.4f' % perm_rho(bt, [int(x) for x in e]))
    print(f'   primary first-half ({pred}) rate vs indicator %.3f, %.4f' % perm_rho(fh, ind), '| vs either-pass indicator %.3f, %.4f' % perm_rho(fh, [int(x) for x in e]))
    gi = [i for i, x in enumerate(h) if x > 0]
    print(f'   among generalisers: first-half rate vs log rate rho, p = %.3f, %.4f' % perm_rho([fh[i] for i in gi], [math.log(h[i]) for i in gi]))
    # independence check: predictor from main-pass samples, outcome from the deep pass (different sampling seed)
    print(f'   main-pass first-half rate vs DEEP-pass indicator (independent samples) %.3f, %.4f' % perm_rho(fh, [int(x > 0) for x in hdeep]),
          '| vs deep-pass hits %.3f, %.4f' % perm_rho(fh, hdeep))
    print('   first-half rate, generalisers vs not (main):', sorted(f'{fh[i]:.1e}' for i in range(24) if ind[i]), 'vs', sorted(f'{fh[i]:.1e}' for i in range(24) if not ind[i]))
    ratio = [fh[i] / (h[i] / sum(cov[f][SEEDS[i]]['n_tried'] for f in fams)) for i in gi]
    print(f'   E7 first-half / verified rate among generalisers: min {min(ratio):.1f}, draws below 10x: {sum(r < 10 for r in ratio)} of {len(ratio)}')
    # per-rule losses
    rules = sorted(logs[f'{st}_s30']['by_rule'])
    out = []
    for kind in ('by_rule', 'by_rule_name_pos', 'by_class'):
        for r in sorted(logs[f'{st}_s30'][kind]):
            x = [logs[f'{st}_s{s}'][kind].get(r, float('nan')) for s in SEEDS]
            rho = spearmanr(x, ind)[0]; out.append((abs(rho), kind, r, rho))
    out.sort(reverse=True)
    print('   strongest per-rule / per-class loss correlations with the indicator (no multiplicity correction, 38 tests):', [(k, r, round(rho, 2)) for _, k, r, rho in out[:4]])
# depth-3: part-2 first-half rate predicting part-1 outcome (disjoint targets); and zero-hit draws' d3_written rate
fh2 = [fhrate(['d3p2'], 'd3_written', s) for s in SEEDS]
print(' depth-3: d3_written rate on part 2 vs part-1 indicator %.3f, %.4f' % perm_rho(fh2, [int(x > 0) for x in h1]))
z = [(s, fhrate(['d3p1', 'd3p2'], 'd3_written', s)) for s, x in zip(SEEDS, hfull) if x == 0]
print(' depth-3 zero-hit draws d3_written rate:', [(s, f'{r:.1e}') for s, r in z], ' below 1e-4:', sum(r < 1e-4 for _, r in z), 'of', len(z))
print(' fh_ok counts: file vs reviewer on verified proofs, any difference:', sum(1 for f in cov for s in SEEDS for k in set(cov[f][s]['fh_ok_file']) | set(cov[f][s]['fh_ok_mine'])
      if cov[f][s]['fh_ok_file'].get(k, 0) != cov[f][s]['fh_ok_mine'].get(k, 0)))
print(' derived-ORE: ore_on_derived / derived_disj first-half rate per draw (all samples):', [f"{fhrate(['dos6'], 'ore_on_derived', s):.1e}" for s in SEEDS][:8], '...', 'max', max(fhrate(['dos6'], 'ore_on_derived', s) for s in SEEDS))
print(' derived-ORE: verified samples with ore_on_derived:', sum(cov['dos6'][s]['fh_ok_file'].get('ore_on_derived', 0) for s in SEEDS))

print('\n== 6. derived-ORE pool: what is solved')
dpool = {x['name']: x for x in rd(f'{ROOT}/data/r3_3/targets_derived_ore_strict_c6.jsonl')}
print(' ok targets per draw (of 300):', [cov['dos6'][s]['ok_targets'] for s in SEEDS])

print('\n== 7. deep-pass addendum DA1-DA5')
z = [i for i, x in enumerate(hr) if x == 0]
print(' DA1 reductio main-zero draws with a deep hit:', sum(hdr[i] > 0 for i in z), 'of', len(z), [SEEDS[i] for i in z if hdr[i] > 0])
g2 = [i for i, x in enumerate(hr) if x >= 2]; g1 = [i for i, x in enumerate(hr) if x == 1]
print(' DA2 >= 2 main hits confirmed:', sum(hdr[i] > 0 for i in g2), 'of', len(g2), '; exactly 1 confirmed:', sum(hdr[i] > 0 for i in g1), 'of', len(g1))
z = [i for i, x in enumerate(hfull) if x == 0]
print(' DA3 depth-3 main-zero draws with a deep hit:', sum(hdd[i] > 0 for i in z), 'of', len(z), [SEEDS[i] for i in z if hdd[i] > 0], '; main >= 1 but deep 0:', [SEEDS[i] for i in range(24) if hfull[i] > 0 and hdd[i] == 0])
d52 = {x['name'] for x in rd(f'{ROOT}/data/r3_3/targets_reductio_deep52.jsonl')}
for nm, fam, deep, dp in (('reductio', ['red'], 'deepred', d52), ('depth-3', ['d3p1', 'd3p2'], 'deepd3', d45)):
    rows = []
    for s in SEEDS:
        m = sum(v for f in fam for t, v in cov[f][s]['pattern_targets'].items() if t in dp)
        if m >= 20:
            rm = m / (len(dp) * 2000); rdp = cov[deep][s]['pattern_hits'] / (len(dp) * 20000); rows.append((s, m, cov[deep][s]['pattern_hits'], round(rdp / rm, 2)))
    print(f' DA4 {nm} (seed, main hits on deep pool, deep hits, deep/main rate ratio):', rows)
print(' DA5 reductio zero in both passes:', 24 - sum(er), 'of 24 (< 8 triggers the "sampling budget" reading)')
# Poisson consistency of main-pass zero given deep rate
print(' expected main-pass hits on the 52 targets given the deep rate (draws with main 0 on reductio):', [(SEEDS[i], round(hdr[i] / 10, 2)) for i in range(24) if hr[i] == 0 and hdr[i] > 0])

print('\n== 8. external stratum (ignition study, 300-target samples, recounted)')
ign = J('ign.json')
for grp, keyf in (('depth-3 f0_a1', lambda k: k.startswith('cov_depth3_f0_a1_')), ('depth-3 other sets', lambda k: k.startswith('cov_depth3') and not k.startswith('cov_depth3_f0_a1_')), ('reductio', lambda k: k.startswith('cov_reductio'))):
    ks = [k for k in ign if not k.startswith('_') and keyf(k)]
    print(f' {grp}:', cp(sum(ign[k]['pattern_hits'] > 0 for k in ks), len(ks)), ' n_tried', sorted({ign[k]['n_tried'] for k in ks}), ' hits', [ign[k]['pattern_hits'] for k in ks])
