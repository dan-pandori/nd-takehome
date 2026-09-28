#!/usr/bin/env python3
"""Reviewer's independent recount for run support-curves. Written from the raw records only."""
import json, glob, collections, os, sys, math

ART = 'artifacts/sc'

def load():
    rows = []
    for f in sorted(glob.glob(os.path.join(ART, 's*.jsonl'))):
        if 'secondary' in f:
            continue
        for l in open(f):
            if l.strip():
                r = json.loads(l); r['_file'] = os.path.basename(f); rows.append(r)
    return rows

THMS = [json.loads(l) for l in open('data/sc/theorems.jsonl')]
NAMES = [t['name'] for t in THMS]
L = {t['name']: t['L_true'] for t in THMS}
rows = load()

# ---- cells: (model, model_seed, temperature) -> name -> pooled (n, c), plus per-stage detail
cell = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
stage_cell = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
first_hit_s1 = collections.defaultdict(dict)   # (model,seed) -> name -> first_hit at T0.8 stage s1/s3
for r in rows:
    key = (r['model'], r['seed'], r['temperature'])
    cell[key][r['name']][0] += r['n_tried']
    cell[key][r['name']][1] += r['n_ok']
    stage_cell[(r['stage'],) + key][r['name']][0] += r['n_tried']
    stage_cell[(r['stage'],) + key][r['name']][1] += r['n_ok']
    if r['stage'] in ('s1', 's3') and r['temperature'] == 0.8:
        first_hit_s1[(r['model'], r['seed'])][r['name']] = r['first_hit']

def solved_within(model, seed, k):
    """solved within the first k attempts of the stage-1/3 draw at T=0.8"""
    fh = first_hit_s1[(model, seed)]
    return {n for n in NAMES if fh.get(n) is not None and fh[n] <= k}

print('=== R1: stage-1/3 coverage at T=0.8 (independent recount) ===')
for (model, seed) in [('base', 0), ('ei', 0), ('base', 1), ('ei', 1)]:
    fh = first_hit_s1[(model, seed)]
    assert len(fh) == 383, (model, seed, len(fh))
    for k in (4000, 10000):
        s = solved_within(model, seed, k)
        print(f'  {model} s{seed} T0.8 solved within k={k:5d}: {len(s):3d}/383 = {len(s)/383:.1%}')

print()
print('=== R2: forward / reverse crux (seed 0, T=0.8, stage 1 only) ===')
for k in (4000, 10000):
    b = solved_within('base', 0, k); e = solved_within('ei', 0, k)
    fwd = sorted(e - b, key=NAMES.index); rev = sorted(b - e, key=NAMES.index)
    print(f'  k={k:5d}: forward crux (c_EI>=1, c_base=0) = {len(fwd):3d}   reverse crux = {len(rev):3d}')
    if k == 10000:
        FWD, REV = fwd, rev
print('  reverse crux names:', REV)

# executor's own lists, for comparison of set membership
def rd(p):
    return [l.strip() for l in open(p) if l.strip()]
ex_fwd = rd('data/sc/crux_forward.txt'); ex_rev = rd('data/sc/crux_reverse.txt')
ex_phi = rd('data/sc/crux_forward_phi.txt'); ex_surv = rd('data/sc/falsifier_survivors.txt')
print(f'  executor crux_forward.txt {len(ex_fwd)}  set-equal to mine at k=10000: {set(ex_fwd)==set(FWD)}')
print(f'  executor crux_reverse.txt {len(ex_rev)}  set-equal to mine: {set(ex_rev)==set(REV)}')

print()
print('=== R3: p_hat_EI on the forward crux (seed 0, T=0.8, stage 1) ===')
phat_ei = {n: (cell[('ei', 0, 0.8)][n][1] / cell[('ei', 0, 0.8)][n][0]) for n in FWD}
phi = sorted([n for n in FWD if phat_ei[n] >= 0.01], key=NAMES.index)
print(f'  forward crux with p_hat_EI >= 0.01: {len(phi)}  (executor crux_forward_phi.txt {len(ex_phi)}, set-equal {set(phi)==set(ex_phi)})')

print()
print('=== R4: base attempts and successes on the crux, per temperature ===')
hdr = f"  {'name':22s} {'L':>2s} {'n_T08':>8s} {'c_T08':>5s} {'n_T10':>8s} {'c_T10':>5s} {'p_EI':>8s}"
print(hdr)
surv = []
for n in phi:
    n08, c08 = cell[('base', 0, 0.8)][n]
    n10, c10 = cell[('base', 0, 1.0)][n]
    print(f'  {n:22s} {L[n]:2d} {n08:8d} {c08:5d} {n10:8d} {c10:5d} {phat_ei[n]:8.4f}')
    if c08 == 0 and c10 == 0 and n08 >= 40000 and n10 >= 40000:
        surv.append(n)
print(f'\n  FALSIFIER (0 base successes at both T, >=40,000 attempts each, p_hat_EI>=0.01): {len(surv)}')
print(f'  executor falsifier_survivors.txt {len(ex_surv)}; set-equal: {set(surv)==set(ex_surv)}')
print(f'  threshold to fire: >=20  ->  {"FIRES" if len(surv)>=20 else "does not fire"}')
mn08 = min(cell[('base',0,0.8)][n][0] for n in surv); mn10 = min(cell[('base',0,1.0)][n][0] for n in surv)
print(f'  min base attempts among survivors: T0.8 {mn08}, T1.0 {mn10}; total min {mn08+mn10}')

print()
print('=== R5: L_true >= 13 (23 theorems) solved by anything, any stage ===')
big = [n for n in NAMES if L[n] >= 13]
for (model, seed, T), d in sorted(cell.items()):
    s = [n for n in big if d[n][1] > 0]
    if s:
        print(f'  {model} s{seed} T{T}: {len(s)} -> {s}')
allsolved = sorted({n for d in cell.values() for n in big if d[n][1] > 0})
print(f'  union over every arm/stage: {len(allsolved)} of 23  {allsolved}')

print()
print('=== R6: T=1.0 vs T=0.8 on the forward crux, base ===')
n08 = sum(cell[('base',0,0.8)][n][0] for n in FWD); c08 = sum(cell[('base',0,0.8)][n][1] for n in FWD)
n10 = sum(cell[('base',0,1.0)][n][0] for n in FWD); c10 = sum(cell[('base',0,1.0)][n][1] for n in FWD)
t08 = sorted([n for n in FWD if cell[('base',0,0.8)][n][1] > 0], key=NAMES.index)
t10 = sorted([n for n in FWD if cell[('base',0,1.0)][n][1] > 0], key=NAMES.index)
print(f'  T0.8: {c08} successes in {n08} attempts on {len(t08)} distinct theorems')
print(f'  T1.0: {c10} successes in {n10} attempts on {len(t10)} distinct theorems')
print(f'  theorems solved only at T1.0: {sorted(set(t10)-set(t08), key=NAMES.index)}')
print(f'  theorems solved only at T0.8: {sorted(set(t08)-set(t10), key=NAMES.index)}')
print(f'  ratio of per-attempt rates T1.0/T0.8: {(c10/n10)/(c08/n08):.2f}x ; theorem-count ratio {len(t10)}/{len(t08)}')

print()
print('=== R7: seed 0 vs seed 1 agreement, k=2,000 and k=10,000 (E10) ===')
for k in (2000, 10000):
    for model in ('base', 'ei'):
        a = solved_within(model, 0, k); b = solved_within(model, 1, k)
        agree = sum(1 for n in NAMES if (n in a) == (n in b))
        print(f'  {model} k={k:5d}: s0 {len(a):3d}, s1 {len(b):3d}, per-theorem agreement {agree}/383 = {agree/383:.1%}')

print()
print('=== R8: reverse crux after extra EI attempts ===')
for n in REV:
    ne, ce = stage_cell[('s2_rev','ei',0,0.8)][n]
    n1, c1 = stage_cell[('s1','ei',0,0.8)][n]
    nb, cb = cell[('base',0,0.8)][n]
    print(f'  {n:22s} L{L[n]:2d} EI s1 ({n1},{c1}) + s2_rev ({ne},{ce})  base pooled ({nb},{cb})')
still = [n for n in REV if cell[('ei',0,0.8)][n][1] == 0]
print(f'  still 0 for EI after the extra attempts: {len(still)} of {len(REV)}')
