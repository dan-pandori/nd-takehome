#!/usr/bin/env python3
"""The pre-registered decision rule of run `style-edl`, applied to style_edl/results.csv (-> artifacts/style_edl/verdict.json).

Floor F = max(0.1; over seeds |EDL_c(S_own) - EDL_c(S_own2)|; over seeds and S_own / S_own2, |EDL_c(order 0) - EDL_c(order 1)|).
"EDL is inflated by style at fixed capability" iff some X in {S_seed, S_RL, S_short, S_Kal} passes the capability criterion
(plain pass@32 >= 0.9 and within 0.03 of the learner's) on all three seeds AND exceeds S_own2 by more than F per proof
under both EDL and EDL_c in 3 / 3 seeds (Addendum 1's clarification).  Also: Spearman rho(style distance, EDL_c) over the
six streams (seed means), the same with the cross-fit and l_V, and the l_V share of each stream's excess.
"""
import csv, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ('S_own', 'S_own2', 'S_seed', 'S_RL', 'S_short', 'S_Kal')


def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    for k, i in enumerate(o):
        r[i] = k + 1.0
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    return 1 - 6 * sum((x - y) ** 2 for x, y in zip(ra, rb)) / (n * (n * n - 1))


def main():
    rows = {(int(r['seed']), r['stream']): r for r in csv.DictReader(open(f'{ROOT}/style_edl/results.csv'))}
    g = lambda s, S, k: float(rows[(s, S)][k]) if rows[(s, S)].get(k) not in (None, '') else None
    S3 = (0, 1, 2)
    parts = [0.1]
    parts += [abs(g(s, 'S_own', 'EDL_c_pp') - g(s, 'S_own2', 'EDL_c_pp')) for s in S3]
    parts += [abs(g(s, S, 'EDL_c_pp_o0') - g(s, S, 'EDL_c_pp_o1')) for s in S3 for S in ('S_own', 'S_own2')]
    F = max(parts)
    out = {'F': F, 'F_parts': parts, 'streams': {}}
    claim = False
    for X in ('S_seed', 'S_RL', 'S_short', 'S_Kal'):
        cap = [g(s, X, 'plain_pass32_after') >= 0.9 and abs(g(s, X, 'plain_pass32_after') - g(s, X, 'plain_pass32_before')) <= 0.03
               for s in S3]
        ex = {k: [g(s, X, k) - g(s, 'S_own2', k) for s in S3] for k in ('EDL_pp', 'EDL_c_pp', 'xfit_EDL_pp', 'lv_EDL_c_pp')
              if all(g(s, X, k) is not None and g(s, 'S_own2', k) is not None for s in S3)}
        above = {k: sum(v > F for v in vs) for k, vs in ex.items()}
        ok = all(cap) and above.get('EDL_pp') == 3 and above.get('EDL_c_pp') == 3
        claim |= ok
        lv_share = None
        if 'lv_EDL_c_pp' in ex and sum(ex['EDL_c_pp']) > 0:
            lv_share = sum(ex['lv_EDL_c_pp']) / sum(ex['EDL_c_pp'])
        out['streams'][X] = {'capability_fixed_by_seed': cap, 'excess_over_S_own2': ex, 'seeds_above_F': above,
                             'counts_for_claim': ok, 'lv_share_of_EDL_c_excess': lv_share}
    out['verdict'] = 'EDL inflated by style at fixed capability' if claim else 'against (no capability-fixed stream above the floor under both EDL and EDL_c)'
    dist = [sum(1 - g(s, S, 'tf_agree') for s in S3) / 3 for S in ORDER]
    for k in ('EDL_c_pp', 'EDL_pp', 'xfit_EDL_pp', 'lv_EDL_c_pp'):
        vals = [sum(g(s, S, k) for s in S3) / 3 for S in ORDER]
        out[f'spearman_dist_vs_{k}'] = spearman(dist, vals)
        out[f'mean_{k}'] = dict(zip(ORDER, vals))
    out['style_distance'] = dict(zip(ORDER, dist))
    json.dump(out, open(f'{ROOT}/artifacts/style_edl/verdict.json', 'w'), indent=1)
    print('F', round(F, 3), '|', out['verdict'])
    for X, v in out['streams'].items():
        print(X, 'cap', v['capability_fixed_by_seed'], 'above F', v['seeds_above_F'], 'lv share', v['lv_share_of_EDL_c_excess'])
    print({k: round(v, 3) for k, v in out.items() if k.startswith('spearman')})


if __name__ == '__main__':
    main()
