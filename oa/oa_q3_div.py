#!/usr/bin/env python3
"""organism-analysis Q3 (read side): diversity per round from the stored sampled reads (k 256, T 0.8).

Per (run, seed, round): groups A / B / C as trajectory defines them (x0 read at r0 and r8); per theorem the number of
distinct Lean-accepted proofs in a read (`proofs`, distinct ND strings as stored; also after whitespace
normalisation); pass@1 (n_ok / n_tried, x1); cumulative solved counts.  Collapse round = first round at which the
median distinct-proof count per A-theorem (x1) falls below 50 % of its maximum over r0..r8; stall round = first round at
which the cumulative group-C solved count (x0 or x1, r1..rk) reaches its r8 value.  Writes artifacts/oa/q3_div.json.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oa_load import SEEDS, STARTS, read_both, rfc_label
from oa_common import nd_pruned_canon

RND = ['pend'] + [f'r{k}' for k in range(1, 9)]


def norm(p):
    return ' '.join(p.split())


def groups(r0, r8):
    return {n: ('A' if r0[n][0] > 0 else 'B' if r8[n][0] > 0 else 'C') for n in r0}


def main():
    out = {}
    print('distinct accepted proofs per theorem (median over the group, x1 read) and pass@1 (mean, x1), per round r0..r8')
    for run in ('c12', 'c6'):
        for seed in SEEDS:
            R = {ck: {x: read_both(run, f's{seed}_{ck}', x) for x in (0, 1)} for ck in RND}
            G = groups(R['pend'][0], R['r8'][0])
            cnt = {g: sum(v == g for v in G.values()) for g in 'ABC'}
            d = {'groups': cnt}
            for g in 'ABC':
                names = [n for n in G if G[n] == g]
                d[f'distinct_med_{g}'] = [float(np.median([len(R[ck][1][n][2]) for n in names])) for ck in RND]
                d[f'distinct_mean_{g}'] = [round(float(np.mean([len(R[ck][1][n][2]) for n in names])), 2) for ck in RND]
                d[f'distinct_norm_mean_{g}'] = [round(float(np.mean([len({norm(p) for p in R[ck][1][n][2]}) for n in names])), 2) for ck in RND]
                d[f'pass1_{g}'] = [round(float(np.mean([R[ck][1][n][0] / R[ck][1][n][1] for n in names])), 4) for ck in RND]
                d[f'distinct_pruned_mean_{g}'] = [round(float(np.mean([len({nd_pruned_canon(p) for p in R[ck][1][n][2]}) for n in names])), 2) for ck in RND]
                d[f'distinct_pruned_med_{g}'] = [float(np.median([len({nd_pruned_canon(p) for p in R[ck][1][n][2]}) for n in names])) for ck in RND]
                lens = lambda ck: [len(p.split(' ; ')) - 1 for n in names for p in R[ck][1][n][2]]
                plens = lambda ck: [len(nd_pruned_canon(p).split(' ; ')) for n in names for p in R[ck][1][n][2] if nd_pruned_canon(p)]
                d[f'mean_lines_distinct_{g}'] = [round(float(np.mean(lens(ck) or [0])), 2) for ck in RND]
                d[f'mean_pruned_lines_distinct_{g}'] = [round(float(np.mean(plens(ck) or [0])), 2) for ck in RND]
                # distinct per SOLVED theorem (conditional on n_ok > 0), to separate diversity from coverage
                d[f'distinct_per_solved_mean_{g}'] = [round(float(np.mean([len(R[ck][1][n][2]) for n in names if R[ck][1][n][0] > 0] or [0])), 2) for ck in RND]
            # cumulative C solved (x0 or x1) by round; frontier = all r0-unsolved theorems
            C = [n for n in G if G[n] == 'C']
            U = [n for n in G if G[n] != 'A']
            cum_c, cum_u, sc, su = [], [], set(), set()
            for ck in RND[1:]:
                for x in (0, 1):
                    sc |= {n for n in C if R[ck][x][n][0] > 0}
                    su |= {n for n in U if R[ck][x][n][0] > 0}
                cum_c.append(len(sc)); cum_u.append(len(su))
            d['cum_C_solved_r1_r8'] = cum_c
            d['cum_unsolved_solved_r1_r8'] = cum_u
            med = d['distinct_med_A']
            mx = max(med)
            d['collapse_round'] = next((k for k, v in enumerate(med) if k > med.index(mx) and v < 0.5 * mx), None)
            d['stall_round_C'] = next(k + 1 for k, v in enumerate(cum_c) if v == cum_c[-1])
            d['stall_round_frontier'] = next(k + 1 for k, v in enumerate(cum_u) if v == cum_u[-1])
            out[f'{run}|s{seed}'] = d
            print(f"{run} s{seed} groups {cnt}  collapse r{d['collapse_round']}  stall(C) r{d['stall_round_C']} "
                  f"stall(frontier) r{d['stall_round_frontier']}  cumC {cum_c}")
            for g in 'ABC':
                print(f"   {g}: distinct med {d[f'distinct_med_{g}']}  pruned-distinct med {d[f'distinct_pruned_med_{g}']}\n      "
                      f"lines (distinct proofs) {d[f'mean_lines_distinct_{g}']} pruned {d[f'mean_pruned_lines_distinct_{g}']}\n      "
                      f"per-solved {d[f'distinct_per_solved_mean_{g}']}  pass@1 {d[f'pass1_{g}']}")
    # rfc: r0 r2 r4 r8
    for seed in SEEDS:
        for start in STARTS:
            R = {k: {x: read_both(*rfc_label(seed, start, k), x) for x in (0, 1)} for k in (0, 2, 4, 8)}
            G = groups(R[0][0], R[8][0])
            d = {'groups': {g: sum(v == g for v in G.values()) for g in 'ABC'}}
            for g in 'ABC':
                names = [n for n in G if G[n] == g]
                d[f'distinct_mean_{g}'] = [round(float(np.mean([len(R[k][1][n][2]) for n in names] or [0])), 2) for k in (0, 2, 4, 8)]
                d[f'pass1_{g}'] = [round(float(np.mean([R[k][1][n][0] / R[k][1][n][1] for n in names] or [0])), 4) for k in (0, 2, 4, 8)]
            out[f'rfc {start}|s{seed}'] = d
    json.dump(out, open('artifacts/oa/q3_div.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
