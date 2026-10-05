#!/usr/bin/env python3
"""Reviewer: hard set H_s, J2_s, calibration pool; equal-k created sets (Q1), reliability (Q9), J5 expectations."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_load as L

def jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else float('nan')

N = L.names()
out = {}
for s in (0, 1, 2):
    p0, p1 = L.both(12, s, 'pend', 0), L.both(12, s, 'pend', 1)
    H = [n for n in N if p0[n][0] == 0 and p1[n][0] == 0]
    # RL reads available before J2 was launched: r8 x0/x1, mcts x2 (+C-only x4, r8 C x10), r16 x1
    rl_solved = set()
    srcs = [(ck, x) for ck in ('r8',) for x in (0, 1, 2)] + [('r16', 1)]     # r8 / r16 only (pre-registered); C-only r8 reads below
    for ck, x in srcs:
        d = L.both(12, s, ck, x)
        rl_solved |= {n for n in N if d[n][0] > 0}
    for ck, x in (('r8', 4), ('r8', 10)):
        d = L.read(12, s, ck, 'C', x)
        rl_solved |= {n for n, v in d.items() if v[0] > 0}
    J2 = [n for n in H if n in rl_solved]
    pooled = {n: p0[n][0] + p1[n][0] for n in N}
    calpool = [n for n in N if 3 <= pooled[n] <= 100]
    out[s] = dict(H=H, J2=J2, calpool=calpool)
    print(f's{s}: H {len(H)}  J2 {len(J2)}  H-J2 {len(H) - len(J2)}  cal pool (pend 3..100 of 512) {len(calpool)}')
sets = json.load(open(f'{L.RV}/artifacts/cd/j1/sets.json'))
for s in (0, 1, 2):
    e = sets[str(s)]
    print(f's{s}: executor H equal: {set(e["H"]) == set(out[s]["H"])}, J2 equal: {set(e["J2"]) == set(out[s]["J2"])}, '
          f'CAL subset of my cal pool: {set(e["CAL"]) <= set(out[s]["calpool"])}, cal pool size exec {e["cal_pool_size"]} mine {len(out[s]["calpool"])}')
    if set(e['J2']) != set(out[s]['J2']):
        print('   J2 exec-mine', sorted(set(e['J2']) - set(out[s]['J2'])), 'mine-exec', sorted(set(out[s]['J2']) - set(e['J2'])))

# ---- Q1 equal-k created sets; Q9 reliability; J5
print('\nQ1 equal-k created set (pend 0/256 and RL >=1/256, same draw); Q9 rel (p_pend<0.05, p_RL>=0.5)')
eq = {}
for s in (0, 1, 2):
    for rl, x in (('r8', 0), ('r8', 1), ('r16', 1), ('r16', 0), ('r12', 1)):
        b, r = L.both(12, s, 'pend', x), L.both(12, s, rl, x)
        E = sorted(n for n in N if b[n][0] == 0 and r[n][0] > 0)
        Rl = sorted(n for n in N if b[n][0] / b[n][1] < 0.05 and r[n][0] / r[n][1] >= 0.5)
        eq[(s, rl, x)] = (E, Rl)
        print(f'  s{s} {rl} x{x}: eqk {len(E):3d}  rel {len(Rl):3d}  rel/eqk {len(Rl) / len(E):.2f}   RL solved {sum(r[n][0] > 0 for n in N)}  pend solved {sum(b[n][0] > 0 for n in N)}')
for s in (0, 1, 2):
    print(f'  s{s} redraw Jaccard eqk r8 x0 vs x1: {jac(eq[(s, "r8", 0)][0], eq[(s, "r8", 1)][0]):.3f};  r16 x1 vs x0: {jac(eq[(s, "r16", 1)][0], eq[(s, "r16", 0)][0]):.3f};'
          f'  rel r8 x0 vs x1 {jac(eq[(s, "r8", 0)][1], eq[(s, "r8", 1)][1]):.3f}')
print('  seed Jaccard eqk r8 x0: ' + ' '.join(f'{jac(eq[(i, "r8", 0)][0], eq[(j, "r8", 0)][0]):.2f}' for i, j in ((0, 1), (0, 2), (1, 2))))
# J5 cap-6 r16 vs r8 on h250 x1
for s in (0, 1, 2):
    a, b = L.read(6, s, 'r16', 'h250', 1), L.read(6, s, 'r8', 'h250', 1)
    print(f'  cap-6 s{s} h250 x1 solved: r16 {sum(v[0] > 0 for v in a.values())}  r8 {sum(v[0] > 0 for v in b.values())}')
json.dump({'H': {s: v['H'] for s, v in out.items()}, 'J2': {s: v['J2'] for s, v in out.items()},
           'eqk': {f's{s}_{rl}_x{x}': v[0] for (s, rl, x), v in eq.items()},
           'rel': {f's{s}_{rl}_x{x}': v[1] for (s, rl, x), v in eq.items()}},
          open(f'{L.RV}/review_cd/out_sets.json', 'w'))
