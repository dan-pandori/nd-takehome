"""C6 audit: rl-from-ckpt ladder r8 solve counts by start vs the end arm (pend), re-derived from raw reads (n_ok>0).
Sources: ~/work/rl-from-ckpt/artifacts/rfc/eval/{s,c}<S>_<start>_r8__<pool>_x<X>.jsonl (early-start ladders, controls),
~/work/trajectory/artifacts/tj/eval/s<S>_{r8,pend}__<pool>_x<X>.jsonl (end-arm ladder = trajectory's best-cap12 T1 ladder)."""
import json, os, math, random, statistics as st
H = os.path.expanduser('~'); RFC = H + '/work/rl-from-ckpt/artifacts/rfc/eval'; TJ = H + '/work/trajectory/artifacts/tj/eval'
OUT = '/home/dan/work/claim-audit/audit/out/'
def rd(path):
    return {json.loads(l)['name']: json.loads(l)['n_ok'] > 0 for l in open(path)}
def ladder(s, start, pool, x):
    return rd(f'{TJ}/s{s}_r8__{pool}_x{x}.jsonl') if start == 'pend' else rd(f'{RFC}/s{s}_{start}_r8__{pool}_x{x}.jsonl')
STARTS = ['p1600', 'p5000', 'p12000', 'p16000', 'pend']; S = (0, 1, 2); POOLS = ('tb72', 'h250')
T975 = {2: 4.303, 4: 2.776}; T80 = {2: 1.061, 4: 0.941}
L = {(s, st_, p, x): ladder(s, st_, p, x) for s in S for st_ in STARTS for p in POOLS for x in (0, 1)}
rows = []
print('counts r8 x1 (s0/s1/s2):')
for st_ in STARTS:
    print(' ', st_, {p: [sum(L[(s, st_, p, 1)].values()) for s in S] for p in POOLS})
print('\nstart - pend, x1, paired by Stage-1 seed; seed-t 95% CI (df 2), paired MDD (80% power), theorem-bootstrap CI of the mean diff')
for p in POOLS + ('all',):
    pools = POOLS if p == 'all' else (p,)
    for st_ in STARTS[:-1]:
        d = [sum(sum(L[(s, st_, q, 1)].values()) - sum(L[(s, 'pend', q, 1)].values()) for q in pools) for s in S]
        m, sd = st.mean(d), st.stdev(d); half = T975[2] * sd / math.sqrt(3); mdd = (T975[2] + T80[2]) * sd / math.sqrt(3)
        # theorem bootstrap (resample theorems, keep 3 seeds), sampling-only uncertainty
        names = [(q, n) for q in pools for n in L[(0, 'pend', q, 1)]]
        rng = random.Random(1); bs = []
        for _ in range(2000):
            smp = [rng.choice(names) for _ in names]
            bs.append(st.mean([sum(L[(s, st_, q, 1)][n] - L[(s, 'pend', q, 1)][n] for q, n in smp) for s in S]))
        bs.sort()
        # x0 replicate of the same comparison
        d0 = [sum(sum(L[(s, st_, q, 0)].values()) - sum(L[(s, 'pend', q, 0)].values()) for q in pools) for s in S]
        rows.append(dict(pool=p, start=st_, d=d, mean=m, sd=sd, ci=[m - half, m + half], mdd=mdd, boot=[bs[50], bs[1949]], d_x0=d0))
        print(f"  {p:5s} {st_:7s} per-seed {d} mean {m:+.1f} sd {sd:.1f} seed-CI [{m-half:+.1f}, {m+half:+.1f}] MDD {mdd:.1f} | "
              f"thm-boot [{bs[50]:+.1f}, {bs[1949]:+.1f}] | x0 per-seed {d0}")
# draw-to-draw spread: same checkpoint, x0 vs x1
print('\nsame-checkpoint x0 vs x1 (tb72+h250) count differences:')
for st_ in STARTS:
    print(' ', st_, [sum(L[(s, st_, q, 0)].values()) - sum(L[(s, st_, q, 1)].values()) for s in S for q in POOLS])
# reach: theorems solved by the early-start ladder (union x0,x1) and not by pend (union), vs a same-model null:
print('\nreach (union of x0,x1 at r8): only-start / only-pend per seed; null = pend x0-only vs x1-only (one draw each)')
for st_ in STARTS[:-1]:
    a = []; b = []
    for s in S:
        U = lambda k: {(q, n) for q in POOLS for x in (0, 1) for n, v in L[(s, k, q, x)].items() if v}
        us, up = U(st_), U('pend'); a.append(len(us - up)); b.append(len(up - us))
    print(f'  {st_:7s} only-start {a} only-pend {b}')
nul = []
for s in S:
    for k in STARTS:
        X0 = {(q, n) for q in POOLS for n, v in L[(s, k, q, 0)].items() if v}; X1 = {(q, n) for q in POOLS for n, v in L[(s, k, q, 1)].items() if v}
        nul.append((k, s, len(X0 - X1), len(X1 - X0)))
print('  single-draw null (ckpt, seed, x0-only, x1-only):', nul)
# union over seeds: anything any early start solves (any seed, any draw) that pend never solves (any seed, any draw)?
Upend = {(q, n) for s in S for q in POOLS for x in (0, 1) for n, v in L[(s, 'pend', q, x)].items() if v}
for st_ in STARTS[:-1]:
    Ust = {(q, n) for s in S for q in POOLS for x in (0, 1) for n, v in L[(s, st_, q, x)].items() if v}
    print(f'  all-seeds union {st_}: only-start {len(Ust - Upend)} {sorted(Ust - Upend)[:6]}  only-pend {len(Upend - Ust)}')
json.dump(rows, open(OUT + 'c6_rfc.json', 'w'), indent=1)
