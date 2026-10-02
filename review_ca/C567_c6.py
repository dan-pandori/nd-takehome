#!/usr/bin/env python3
"""C6 recount (reviewer, independent): rl-from-ckpt r8 solved counts per start, end arm level-ness, selection-free reach.
Ladder reads: rl-from-ckpt/artifacts/rfc/eval/s<S>_<start>_r8__<pool>_<x>.jsonl; controls c<S>_...; end arm (pend ladder)
= trajectory/artifacts/tj/eval/s<S>_r8__<pool>_<x>.jsonl. Counts from my own code ('solved' field per theorem)."""
import json, math, statistics as st
R = '/home/dan/review/claim-audit/rv/C567_raw'
STARTS = ['p1600', 'p5000', 'p12000', 'p16000', 'pend']


def read(kind, s, start, pool, x):
    if kind == 'L' and start == 'pend':
        f = f'{R}/trajectory/artifacts/tj/eval/s{s}_r8__{pool}_{x}.jsonl'
    else:
        f = f'{R}/rl-from-ckpt/artifacts/rfc/eval/{"s" if kind == "L" else "c"}{s}_{start}_r8__{pool}_{x}.jsonl'
    d = {}
    for l in open(f):
        r = json.loads(l); d[r['name']] = (bool(r['solved']), r['n_ok'], r['n_tried'])
    return d


C = {}
for kind in 'LC':
    for st_ in STARTS:
        for s in range(3):
            for pool in ('tb72', 'h250'):
                for x in ('x0', 'x1'):
                    C[kind, st_, s, pool, x] = read(kind, s, st_, pool, x)
n = lambda d: sum(v[0] for v in d.values())
print('solved at r8, x1 (s0/s1/s2) mean | x0 mean')
for kind in 'LC':
    for st_ in STARTS:
        row = []
        for pool in ('tb72', 'h250'):
            v1 = [n(C[kind, st_, s, pool, 'x1']) for s in range(3)]
            v0 = [n(C[kind, st_, s, pool, 'x0']) for s in range(3)]
            row.append(f'{pool} {v1[0]}/{v1[1]}/{v1[2]} mean {st.mean(v1):.1f} sd {st.stdev(v1):.2f} | x0 {st.mean(v0):.1f}')
        print(f'{kind} {st_:7s} ' + ' ; '.join(row))
# MDD from this run's own seed sd (ladders p5000..pend, x1), two-sample t, n=3/arm, 80% power alpha .05 two-sided
T975_4, T80_4 = 2.7764, 0.9410
for pool in ('tb72', 'h250'):
    sds = [st.variance([n(C['L', st_, s, pool, 'x1']) for s in range(3)]) for st_ in STARTS[1:]]
    sd = math.sqrt(st.mean(sds))
    mdd = (T975_4 + T80_4) * sd * math.sqrt(2 / 3)
    print(f'{pool}: pooled seed sd (ladders p5000..pend) {sd:.2f} -> MDD(n=3 vs 3) {mdd:.1f}')
    pe = [n(C['L', 'pend', s, pool, 'x1']) for s in range(3)]
    for st_ in STARTS[:-1]:
        v = [n(C['L', st_, s, pool, 'x1']) for s in range(3)]
        d = [a - b for a, b in zip(pe, v)]
        md = st.mean(d); se = st.stdev(d) / math.sqrt(3)
        # pooled two-proportion z on summed counts (3 seeds x N theorems), ignores seed variance
        N = 3 * (72 if pool == 'tb72' else 250); p1, p2 = sum(pe) / N, sum(v) / N; pp = (sum(pe) + sum(v)) / (2 * N)
        z = (p1 - p2) / math.sqrt(pp * (1 - pp) * 2 / N)
        print(f'   pend - {st_:7s}: per seed {d}, mean {md:+.1f}, paired t95 [{md - 4.303 * se:+.1f},{md + 4.303 * se:+.1f}], pooled z {z:+.2f}')
# selection-free reach: union of x0,x1 at r8, theorems only this start solves / only pend solves; strict: both draws vs neither
print('reach (union x0,x1): only-start / only-pend per seed ; strict both-vs-neither summed')
for st_ in STARTS[:-1]:
    cells = []; sa = sb = 0
    for s in range(3):
        a = set(); b = set(); a2 = set(); b2 = set(); a0 = set(); b0 = set()
        for pool in ('tb72', 'h250'):
            for x in ('x0', 'x1'):
                for k, v in C['L', st_, s, pool, x].items():
                    if v[0]: a.add(k)
                for k, v in C['L', 'pend', s, pool, x].items():
                    if v[0]: b.add(k)
            for k in C['L', st_, s, pool, 'x0']:
                if C['L', st_, s, pool, 'x0'][k][0] and C['L', st_, s, pool, 'x1'][k][0]: a2.add(k)
                if C['L', 'pend', s, pool, 'x0'][k][0] and C['L', 'pend', s, pool, 'x1'][k][0]: b2.add(k)
        cells.append(f'{len(a - b)}/{len(b - a)}')
        sa += len(a2 - b); sb += len(b2 - a)
    print(f'   {st_:7s} ' + '  '.join(cells) + f'   strict {sa} vs {sb}')
# same checkpoint read twice (x0 vs x1) -> two-proportion z on per-sample success (n_ok / n_tried summed) and solved count
print('x0 vs x1 on the same checkpoint (solved counts, tb72+h250 = 322):')
for kind, st_ in (('L', 'pend'), ('L', 'p5000'), ('L', 'p1600'), ('C', 'pend')):
    out = []
    for s in range(3):
        a = sum(n(C[kind, st_, s, p, 'x0']) for p in ('tb72', 'h250')); b = sum(n(C[kind, st_, s, p, 'x1']) for p in ('tb72', 'h250'))
        pp = (a + b) / 644; z = (a - b) / 322 / math.sqrt(pp * (1 - pp) * 2 / 322)
        out.append(f's{s} {a} vs {b} z {z:+.2f}')
    print(f'   {kind} {st_:7s} ' + ' | '.join(out))
