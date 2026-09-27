#!/usr/bin/env python3
"""Compact markdown tables for run stage1-dynamics from artifacts/sd/summary.json.
  python3 sd_tables.py [q1|q2|q3|q4|q5|r|cost|cells|all]
Every table names the checkpoints behind it; nothing here recomputes anything sd_analysis.py did not.
"""
import json, sys, statistics as st

S = json.load(open('artifacts/sd/summary.json'))
Q, CELLS = S['questions'], S['cells']
pp = lambda x: '—' if x is None else f'{100 * x:+.1f}'
r3 = lambda x: '—' if x is None else f'{x:.3f}'
r4 = lambda x: '—' if x is None else f'{x:.4f}'


def get(arm, seed, step=None, rep=None):
    for c in CELLS:
        if c['arm'] == arm and c['seed'] == seed and c['rep'] == rep and (step is None or c['step'] == step):
            return c
    return None


def q1():
    print('### Q1  within-seed, W-6k -> W-12k -> W-24k (all decayed; Lean-alone greedy, 5,000 held-out)\n')
    print('| slice | n | median W-12k − W-6k | median W-24k − W-6k | seeds up >2pp (24k) | seeds within ±2pp (24k) |')
    print('|---|---|---|---|---|---|')
    for sl in ('all', 'len2', 'len3', 'len4', 'len5', 'len6', 'nodepth3_len6', 'depth3'):
        d = Q['Q1_saturation'][sl]
        print(f"| {sl} | {d['W6k_vs_W24k']['n_seeds']} | {pp(d['W6k_vs_W12k']['median_delta'])} pp "
              f"| **{pp(d['W6k_vs_W24k']['median_delta'])} pp** | {d['W6k_vs_W24k']['n_up_gt_2pp']} "
              f"| {d['W6k_vs_W24k']['n_within_2pp']} |")
    e = Q['E1_falsifier']
    print(f"\nE1 falsifier (flat within ±2 pp on the 6-line bin at BOTH 12k and 24k): "
          f"**{e['n']} seeds** {e['seeds_flat_on_both']} — fires at ≥6: **{e['fires_if_ge_6']}**\n")
    print('| arm | n | 6-line mean | 6-line cross-seed sd | overall mean | overall sd |')
    print('|---|---|---|---|---|---|')
    for lab, d in Q['E2_cross_seed_sd'].items():
        print(f"| {lab} | {d['n']} | {r3(d['len6_mean'])} | **{r4(d['len6_sd'])}** | {r3(d['all_mean'])} "
              f"| {r4(d['all_sd'])} |")
    print('\n### E5  does the long-proof validation loss keep falling?  (arm W, per seed)\n')
    print('| seed | 6-line loss at 6k | at 24k | its min (step) | end/min | depth-3 at 6k | at 24k | `val2k` at 6k | at 24k |')
    print('|---|---|---|---|---|---|---|---|---|')
    for k, d in sorted(Q['E5_long_loss'].items(), key=lambda t: int(t[0])):
        a, b, c = d['len6'], d['depth3'], d['val2k']
        if not a:
            continue
        print(f"| {k} | {r4(a['at_6000'])} | {r4(a['at_end'])} | {r4(a['min'])} ({a['argmin_step']}) "
              f"| {r3(a['end_over_min'])} | {r4(b['at_6000'])} | {r4(b['at_end'])} "
              f"| {r4(c['at_6000'])} | {r4(c['at_end'])} |")
    print('\n### E6  `val2k` flat while the 6-line bin moves\n')
    print('| seed | Δ`val2k` 6k→24k | Δ 6-line accuracy 6k→24k |')
    print('|---|---|---|')
    for r in Q['E6_val2k_flat']:
        print(f"| {r['seed']} | {r['dval2k_6k_to_24k']:+.4f} | {pp(r['dlen6_acc_6k_to_24k'])} pp |")


def q2():
    d = Q['Q2_depth3']
    print(f"### Q2  the depth-3 slice, arm W's stable-phase trajectory (cut {d['cut']}, 500 records)\n")
    print('| step | seeds | in the high mode | p(high) | Wilson 95 % |')
    print('|---|---|---|---|---|')
    for s, v in sorted(d['modes_by_step'].items(), key=lambda t: int(t[0])):
        print(f"| {s} | {v['n_seeds']} | {v['n_high']} | {r3(v['p_high'])} "
              f"| [{v['wilson'][0]:.3f}, {v['wilson'][1]:.3f}] |")
    print('\nPer-seed depth-3 rate at selected steps (never a mean — the slice is bimodal):\n')
    ks = sorted(d['per_seed'], key=int)
    shown = [1000, 2000, 4000, 6000, 9000, 12000, 16000, 19000, 24000]
    print('| seed | ' + ' | '.join(str(s) for s in shown) + ' |')
    print('|---|' + '---|' * len(shown))
    for k in ks:
        row = {p['step']: p for p in d['per_seed'][k]}
        print(f'| {k} | ' + ' | '.join(
            ('**' + r3(row[s]['depth3']) + '**' if row[s]['high_mode'] else r3(row[s]['depth3']))
            if s in row else '—' for s in shown) + ' |')
    e = Q['E7_mode_changes_6k_to_24k']
    print(f"\nE7: **{e['n_changed']} of 8 seeds change mode between the decayed W-6k and W-24k** "
          f"({e['changed']}) — 'the mode is set early' dies at ≥2: **{e['mode_set_early_dies_if_ge_2']}**")
    e9 = Q['E9_early_predicts_late']
    print(f"\nE9: depth-3 at step 2,000 vs at 24,000 over {e9['n']} seeds, Spearman ρ = **{r3(e9['spearman'])}**")


def q3():
    print('### Q3  schedule at an equal 6,000 steps — C (cosine) vs W-6k (WSD), same seed, same 6,000 batches\n')
    print('| slice | n | median W-6k − C | median |Δ| | seeds where WSD is higher |')
    print('|---|---|---|---|---|')
    for sl, d in Q['Q3_schedule'].items():
        print(f"| {sl} | {d['n_seeds']} | {pp(d['median_delta'])} pp | {pp(d['median_abs_delta'])} pp "
              f"| {d['n_wsd_higher']} / {d['n_seeds']} |")
    print('\nPer seed on the 6-line bin (C, W-6k, Δ):\n')
    print('| seed | C | W-6k | Δ |')
    print('|---|---|---|---|')
    for k, c, w, d in Q['Q3_schedule']['len6']['per_seed']:
        print(f'| {k} | {r3(c)} | {r3(w)} | {pp(d)} pp |')


def q4():
    print('### Q4  steps or repetition?  F (fresh 572,759) vs W (control 155,000), both WSD 24,000\n')
    print('| slice | n seeds | median F − W at 24,000 |')
    print('|---|---|---|')
    for sl, d in Q['Q4_steps_vs_data']['final_F_vs_W'].items():
        print(f"| {sl} | {d['n_seeds']} | **{pp(d['median_delta'])} pp** |")
    print('\nEach arm\'s own stable-phase 6,000 → decayed 24,000 gain on the 6-line bin:\n')
    print('| arm | n seeds | median gain |')
    print('|---|---|---|')
    for arm, d in Q['Q4_steps_vs_data']['own_gain_stable'].items():
        print(f"| {arm} | {len(d['per_seed'])} | {pp(d['median_gain_len6'])} pp |")
    e = Q['E11_F_gain_over_W_gain']
    print(f"\nE11: F's gain / W's gain = **{r3(e['ratio'])}** — 'the gain is steps, not repetition' "
          f"holds at ≥0.6: **{e['steps_not_repetition_if_ge_0.6']}**")


def q5():
    print('### Q5  is a validation loss a usable proxy for per-length accuracy?\n')
    print('Along a single run (arm W, 8 seeds × trajectory checkpoints):\n')
    print('| pair | points | pooled Spearman ρ | worst per-seed ρ |')
    print('|---|---|---|---|')
    for k, d in Q['Q5_proxy']['trajectory'].items():
        ws = [v['spearman'] for v in d['per_seed'].values() if v['spearman'] is not None]
        print(f"| {k} | {d['n_points']} | **{r3(d['spearman_pooled'])}** "
              f"| {r3(max(ws, key=abs) if ws else None) if not ws else r3(max(ws))} |")
    print('\nRanking different runs at the same step — the question that matters:\n')
    print('| pair | n seeds | Spearman ρ |')
    print('|---|---|---|')
    for k, d in Q['Q5_proxy']['fixed_step_ranking'].items():
        print(f"| {k} | {d['n_seeds']} | **{r3(d['spearman'])}** |")


def rep():
    print('### Arm R (addendum 1)  the same-command replicate floor — runs differing in nothing a human specified\n')
    print('| group | slice | n (same pod) | sd | range | n (with the cross-pod baseline) | sd | range |')
    print('|---|---|---|---|---|---|---|---|')
    for g, d in Q['R_replicate_floor'].items():
        for sl in ('all', 'len6', 'len5', 'depth3'):
            v = d[sl]
            rs = v['range_same_pod']; rb = v['range_with_baseline']
            print(f"| {g} | {sl} | {v['n_same_pod']} | **{r4(v['sd_same_pod'])}** "
                  f"| {r3(rs[0])}–{r3(rs[1])} | {v['n_with_baseline']} | {r4(v['sd_with_baseline'])} "
                  f"| {r3(rb[0])}–{r3(rb[1])} |")
    print()
    for g, d in Q['R_replicate_floor'].items():
        m = d['depth3_modes']
        print(f"- **{g}**: depth-3 modes {m['n_high']} high of {m['n']} — straddles the 0.44 cut: "
              f"**{m['straddles_cut']}** (E18)")
        print(f"  replicates: " + ', '.join(f"{c['stem']} {r3(c['depth3'])}" for c in d['reps'])
              + (f", baseline {d['cross_pod_baseline']['stem']} {r3(d['cross_pod_baseline']['depth3'])}"
                 if 'cross_pod_baseline' in d else ''))


def cost():
    e = Q['E16_instrumentation_overhead']
    print(f"### E16  cost of the per-length validation: median **{100 * e['median']:.1f} %** of training "
          f"wall time over {e['n']} runs, range {100 * e['range'][0]:.1f}–{100 * e['range'][1]:.1f} %\n")
    print('| arm | checkpoints | mean term size (all) | mean written lines (all) | term size (6-line) | written lines (6-line) |')
    print('|---|---|---|---|---|---|')
    for arm, d in Q['proof_length'].items():
        print(f"| {arm} | {d['n_ckpts']} | {d['mean_term_size_all']:.1f} | {d['mean_written_lines_all']:.2f} "
              f"| {d['mean_term_size_len6']:.1f} | {d['mean_written_lines_len6']:.2f} |")


def cells():
    print('| stem | arm | seed | step | all | len5 | len6 | depth3 | nod3_6 | parse-fail | lean-rej |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for c in sorted(CELLS, key=lambda c: (c['arm'], c['seed'], c['step'], c['rep'] or '')):
        if c['arm'] in ('Wtraj', 'Ftraj'):
            continue
        print(f"| {c['stem']} | {c['arm']} | {c['seed']} | {c['step']} | {r3(c['all'])} | {r3(c['len5'])} "
              f"| {r3(c['len6'])} | {r3(c['depth3'])} | {r3(c['nodepth3_len6'])} | {c['parse_fail']} "
              f"| {c['lean_rej_of_parsed']} |")


W = {'q1': q1, 'q2': q2, 'q3': q3, 'q4': q4, 'q5': q5, 'r': rep, 'cost': cost, 'cells': cells}
for w in (sys.argv[1:] or ['all']):
    if w == 'all':
        for k, f in W.items():
            print(f'\n<!-- {k} -->'); f()
    else:
        W[w]()
