"""Claims ledger v2 (2026-10-12): small recounts behind rows L11, L12, L20-L22, L44, L8-L9, L2, L75.
Inputs: capability-defs analysis/out/bracket.json (cd_bracket's rules), artifacts/coe/budget/budget.json (Phase 0.2),
and part3_<alloc>.json written by run_alloc.sh (sets per allocation; pass their directory as argv[1])."""
import json, math, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..')
B = json.load(open(os.path.expanduser('~/work/capability-defs/capability_defs/analysis/out/bracket.json')))
BJ = json.load(open(os.path.join(ROOT, 'artifacts/coe/budget/budget.json')))
P3 = sys.argv[1] if len(sys.argv) > 1 else None
ORDER = [('K_att', 'K_att'), ('K_train', 'K_train_sameclass'), ('K_uni', 'K_evalset_sameclass'), ('K_pub', 'K_pub'), ('K_adapt', 'K_adapt')]
K = {a: {s: BJ['per_seed'][str(s)]['r8'][k] for s in range(3)} for a, k in ORDER}
ratio = BJ['ratio_used']
c322 = {0: BJ['c_A40_322']['s0_b2048'], 1: BJ['c_A40_322']['s1_b2048'], 2: BJ['c_A40_322']['s2_b2048']}
lad = {s: BJ['per_seed'][str(s)]['r8']['ladder_s_all'] for s in range(3)}

print('== L11 bracket verdicts, r8-solved hard theorems (exclusive: sampling lo >= 1/K / estimate LB08 >= ln2 - lnK only / '
      'found c >= 1 not elicited / not reached c = 0, n >= K / undetermined); certified UB95 < 0.05/K (not exclusive)')
for a, _ in ORDER:
    row = []
    for s in range(3):
        k = K[a][s]
        H = [(n, x) for n, x in B[str(s)].items() if x['grp'] == 'H' and x['phat_r8'] > 0]
        samp = {n for n, x in H if x['lo'] >= 1 / k}
        est = {n for n, x in H if n not in samp and x['LB08'] >= math.log(2) - math.log(k)}
        found = [n for n, x in H if n not in samp | est and x['c'] >= 1]
        nr = [n for n, x in H if x['c'] == 0 and x['n'] >= k]
        und = [n for n, x in H if x['c'] == 0 and x['n'] < k]
        cert = sorted(n.replace('la_transfer_', '') for n, x in H if x['ub'] < 0.05 / k)
        row.append(f's{s} n{len(H)}: {len(samp)} / {len(est)} / {len(found)} / {len(nr)} / {len(und)}; cert {len(cert)} {cert}')
    print(f'  {a:8s} ' + ' | '.join(row))

print('\n== L12 log10 K per allocation (r8)')
for a, _ in ORDER:
    print(f'  {a:8s} ' + ' / '.join(f'{math.log10(K[a][s]):.2f}' for s in range(3)))

print('\n== L20-L21 J9: largest K each pair certifies at (0.05 / UB95), and the A40 cost on the 322 below which it fails at '
      'the uniform allocation (K_uni = ladder s / (322 x c x %.4f))' % ratio)
for p, v in BJ['j9_certified_at_r8_budgets'].items():
    s = int(p[1]); kmax = 0.05 / v['UB95']
    cmin = lad[s] / (322 * ratio * kmax) * 1e3
    print(f'  {p:22s} c {v["c"]} n {v["n"]:>9,} Kmax {kmax:8,.0f}  c_min {cmin:.2f} ms (measured {c322[s]:.2f})  K_uni/Kmax {K["K_uni"][s] / kmax:.2f}  '
          + ' '.join(f'{a}:{"Y" if v[k] else "n"}' for a, k in ORDER))

print('\n== L44 J7 seconds vs the ladders (cd_defs totals 22,350 / 24,467 / 27,021 RTX A6000-s; A6000 = %.4f x A40)' % ratio)
j7 = (18308, 20494, 21824); L = (22350, 24467, 27021)
print('  A6000-s share ' + ' / '.join(f'{j / l:.3f}' for j, l in zip(j7, L)) + '; A40-equivalent share '
      + ' / '.join(f'{j / (l / ratio):.3f}' for j, l in zip(j7, L)))

print('\n== L8 / L9 / L14 ratios to K_uni')
print('  published 0.1/0.3/1/3 x K_pub in K_uni units: ' + ' | '.join(
    f's{s}: ' + ' / '.join(f'{m * K["K_pub"][s] / K["K_uni"][s]:.2f}' for m in (0.1, 0.3, 1, 3)) for s in range(3)))
print('  ladder-attempt budget 5,571 / 5,571 / 6,245 over K_uni: ' + ' / '.join(f'{b / K["K_uni"][s]:.2f}' for s, b in enumerate((5571, 5571, 6245))))
print('  K_total / 322 (3.49 / 3.29 / 4.29 M) over K_uni: ' + ' / '.join(f'{t / 322 / K["K_uni"][s]:.3f}' for s, t in enumerate((3.49e6, 3.29e6, 4.29e6))))

if P3:
    print('\n== L2 / L75 compute-matched (r8 x0) members outside the 0-success core, with base successes / attempts (bracket.json)')
    for a, f in (('K_att', 'att'), ('K_train', 'train'), ('K_uni', 'uniform'), ('K_pub', 'pub'), ('K_adapt', 'adapt')):
        d = json.load(open(os.path.join(P3, f'part3_{f}.json')))['sets']
        row = []
        for s in range(3):
            st = d[f's{s}_r8_x0']; ex = sorted(set(st['cm']) - set(st['cm0']))
            one = sum(1 for n in ex if B[str(s)][n]['c'] == 1)
            row.append(f's{s} cm {len(st["cm"])} core {len(st["cm0"])} outside {len(ex)} (exactly 1 base success: {one})')
        print(f'  {a:8s} ' + ' | '.join(row))

print('\n== L24 agreement (r8, x0; mean Jaccard over seeds) from recount_K_*.txt: "out of reach" cluster (cm, brk_ne, tfmax, '
      'guided; chain separately) and "behaviour" cluster (eqk, sharp, irt)')
import itertools
HERE = os.path.dirname(os.path.abspath(__file__))
for a in ('K_att', 'K_train', 'K_uni', 'K_pub_control', 'K_adapt'):
    Lr = open(os.path.join(HERE, f'recount_{a}.txt')).read().splitlines()
    i = [k for k, l in enumerate(Lr) if l.startswith('agreement matrix (r8')][0]
    cols = Lr[i + 1].split(); M = {}
    for l in Lr[i + 2:i + 2 + len(cols)]:
        p = l.split(); M[p[0]] = dict(zip(cols, map(float, p[1:])))
    reach = [M[x][y] for x, y in itertools.combinations(['cm', 'brk_ne', 'tfmax', 'guided'], 2)]
    chain = [M['chain'][y] for y in ('cm', 'brk_ne', 'tfmax', 'guided')]
    beh = [M[x][y] for x, y in itertools.combinations(['eqk', 'sharp', 'irt'], 2)]
    print(f'  {a:14s} reach {min(reach):.2f}-{max(reach):.2f}; chain vs cm / brk_ne / tfmax / guided '
          + ' / '.join(f'{v:.2f}' for v in chain) + f'; behaviour {min(beh):.2f}-{max(beh):.2f}')
