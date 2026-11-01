#!/usr/bin/env python3
"""Reviewer (coe-dose01): arm-level statistics from MY y recounts (out/y_*.json, incl. the inherited arms recounted from
their own found_transfer files) and MY x curves (out/flops.json; inherited arms' x where I computed it).
  * crossing round / x per seed (first round with y >= 14)
  * one-sided Boschloo exact test of the crossing indicator by r16, own implementation (rows = arms; checked against the
    transposed-table trap: groups are the ARMS)
  * exact one-sided Mann-Whitney of r16 y (all assignments enumerated, ties counted 1/2)
  * IQM (n = 3: the mean) with a stratified (per-arm) bootstrap 95 % interval
  * the pre-registered reading rule, evaluated mechanically."""
import itertools, json, math, os, random, statistics as st, sys
O = '/home/dan/work/coe-dose01/review_cd01/out'


def y_of(tag):
    return json.load(open(f'{O}/y_{tag}.json'))


def comb(n, k):
    return math.comb(n, k)


def fisher_one_sided(a, n1, b, n2):
    """P(X >= a) under the hypergeometric with margins (n1, n2, a + b): arm 1 has MORE successes"""
    K = a + b; N = n1 + n2
    return sum(comb(n1, x) * comb(n2, K - x) for x in range(a, min(n1, K) + 1) if 0 <= K - x <= n2) / comb(N, K)


def boschloo(a, n1, b, n2, grid=2001):
    """one-sided: H1 p1 > p2.  Exact unconditional test with Fisher's p as the statistic."""
    t_obs = fisher_one_sided(a, n1, b, n2)
    region = [(x, y) for x in range(n1 + 1) for y in range(n2 + 1) if fisher_one_sided(x, n1, y, n2) <= t_obs + 1e-12]
    best = 0.0
    for i in range(grid):
        p = i / (grid - 1)
        s = sum(comb(n1, x) * p ** x * (1 - p) ** (n1 - x) * comb(n2, y) * p ** y * (1 - p) ** (n2 - y) for x, y in region)
        best = max(best, s)
    return best


def mw_one_sided(xs, ys):
    """exact P(U >= U_obs), U = #(x > y) + 0.5 #(x == y), all C(n, len(xs)) assignments equally likely"""
    def U(a, b):
        return sum((1.0 if u > v else 0.5 if u == v else 0.0) for u in a for v in b)
    allv = xs + ys
    u0 = U(xs, ys)
    cnt = tot = 0
    for idx in itertools.combinations(range(len(allv)), len(xs)):
        a = [allv[i] for i in idx]; b = [allv[i] for i in range(len(allv)) if i not in idx]
        tot += 1; cnt += U(a, b) >= u0 - 1e-9
    return cnt / tot


def iqm(v):
    v = sorted(v); n = len(v); k = int(math.floor(n * 0.25))
    w = v[k:n - k] if n - 2 * k > 0 else v
    return sum(w) / len(w)


def boot(v, B=20000, seed=0):
    rng = random.Random(seed)
    s = sorted(iqm([rng.choice(v) for _ in v]) for _ in range(B))
    return s[int(0.025 * B)], s[int(0.975 * B) - 1]


def main():
    F = json.load(open(f'{O}/flops.json'))
    arms = {'dose01': [f'la_dose01_s{s}' for s in range(3)], 'dose1': [f'coe_la_dose1_s{s}' for s in range(3)],
            'ko': ['coe_la_ko_s0', 'coe_la_ko_s1', 'coe_la_ko_s2', 'coe_la_ko_s3', 'coe_la_ko_s4', 'coe_la_ko_s5'],
            'full': [f'coe_la_full_s{s}' for s in (3, 4, 5)]}
    out = {'per_seed': {}, 'tests': {}}
    for arm, tags in arms.items():
        for t in tags:
            if not os.path.exists(f'{O}/y_{t}.json'):
                print('missing', t); continue
            y = y_of(t)
            pr = {int(k): v['y'] for k, v in y['per_round'].items()}
            cross = next((r for r in sorted(pr) if r <= 16 and pr[r] >= 14), None)
            lad = t.replace('coe_', '')
            x = None
            if lad in F and cross:
                x = next(r['x'] for r in F[lad]['rows'] if r['round'] == cross)
            out['per_seed'][t] = dict(arm=arm, y_r1=pr.get(1), y_r16=pr.get(16), cross_round=cross, cross_x=x,
                                      y_r24=pr.get(24), y_r32=pr.get(32))
    for t, v in out['per_seed'].items():
        print(t, v)
    def col(arm, k):
        return [v[k] for t, v in out['per_seed'].items() if v['arm'] == arm]
    c01 = sum(1 for v in col('dose01', 'cross_round') if v); c1 = sum(1 for v in col('dose1', 'cross_round') if v)
    cko = sum(1 for v in col('ko', 'cross_round') if v)
    n01, n1, nko = len(col('dose01', 'y_r16')), len(col('dose1', 'y_r16')), len(col('ko', 'y_r16'))
    out['tests']['boschloo_cross_dose01_vs_ko'] = (f'{c01}/{n01} vs {cko}/{nko}', boschloo(c01, n01, cko, nko))
    out['tests']['boschloo_cross_dose1_vs_dose01'] = (f'{c1}/{n1} vs {c01}/{n01}', boschloo(c1, n1, c01, n01))
    # pre-registration's table values (rows = arms), as a check of my implementation
    out['tests']['prereg_table_check'] = {f'{k}/3 vs 0/6': round(boschloo(k, 3, 0, 6), 4) for k in (1, 2, 3)}
    out['tests']['prereg_table_check_vs1pct'] = {f'3/3 vs {k}/3': round(boschloo(3, 3, k, 3), 4) for k in (0, 1, 2)}
    y01, y1, yko = col('dose01', 'y_r16'), col('dose1', 'y_r16'), col('ko', 'y_r16')
    out['tests']['mw_r16_dose01_gt_ko'] = mw_one_sided(y01, yko)
    out['tests']['mw_r16_dose1_gt_dose01'] = mw_one_sided(y1, y01)
    for arm in arms:
        v = col(arm, 'y_r16')
        if v:
            out['tests'][f'iqm_r16_{arm}'] = (round(iqm(v), 2), boot(v))
    xs = [v for v in col('dose01', 'cross_x') if v]
    out['tests']['dose01_crossing_x_median'] = st.median(xs) if xs else None
    out['tests']['dose01_crossing_x'] = xs
    # pre-registered reading rule (decided on y, by r16)
    r16 = col('dose01', 'y_r16'); crossx = col('dose01', 'cross_x'); ncross = sum(1 for v in crossx if v)
    if ncross == 0 and all(v <= 5 for v in r16):
        reading = 'threshold'
    elif ncross >= 2 and st.median([v for v in crossx if v]) > 0.73 and sum(1 for v in crossx if v and v <= 0.73) < 2:
        reading = 'graded'
    elif sum(1 for v in crossx if v and v <= 0.73) >= 2:
        reading = 'no resolvable dose effect'
    else:
        reading = 'intermediate'
    out['tests']['reading_rule'] = reading
    for k, v in out['tests'].items():
        print(k, v)
    json.dump(out, open(f'{O}/stats.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
