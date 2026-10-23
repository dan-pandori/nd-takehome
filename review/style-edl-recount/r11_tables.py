#!/usr/bin/env python3
"""R11 (reviewer): markdown tables for review_style-edl.md §Recount, generated from out/*.json (no hand copying).
  python3 r11_tables.py > out/r11_tables.md
"""
import json, os
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
J = lambda f: json.load(open(os.path.join(H, f)))
SEEDS = (0, 1, 2)
STREAMS = ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')


def f(x, d=3):
    return f'{x:.{d}f}'


def main():
    r1, r3, r4, r5, r6 = J('r1_rebuild.json'), J('r3_edl.json'), J('r4_cap.json'), J('r5_lv.json'), J('r6_attr.json')
    c = r3['cells']
    print('### T1. Streams (my rebuild; per seed s0 / s1 / s2; 256 theorems = stream + test halves)\n')
    print('| stream | identical to own greedy | mean actions | mean ND lines | mean term size (mine) | TF agreement (learner, 256 proofs) |')
    print('|---|---|---|---|---|---|')
    for S in STREAMS:
        st = [r1['stream_stats'][f's{s}/{S}'] for s in SEEDS]
        ta = [c[f's{s}/{S}']['learner_tf_agree_all256'] for s in SEEDS]
        print(f"| {S} | {' / '.join(f(x['identical_to_own_greedy']) for x in st)} | {' / '.join(f(x['mean_actions'], 2) for x in st)} | "
              f"{' / '.join(f(x['mean_nd_lines'], 2) for x in st)} | {' / '.join(f(x['mean_term_size'], 2) for x in st)} | {' / '.join(f(x, 4) for x in ta)} |")
    print('\n### T2. EDL (A_ES, names not coded, bits per proof; per seed s0 / s1 / s2)\n')
    print('| stream | lr* | start (block [0, 8)) | learner mean, 256 | L_test (θ*) | EDL / proof | EDL_c / proof | EDL / action | EDL_c / action | M / proof |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for S in STREAMS:
        x = [c[f's{s}/{S}'] for s in SEEDS]
        g = lambda k, d=3: ' / '.join(f(v[k], d) for v in x)
        print(f"| {S} | {' / '.join(f'{v['lr_star']:g}' for v in x)} | {g('first_block_per_proof', 2)} | {g('learner_all256_mean')} | {g('L_test_per_proof')} | "
              f"{g('EDL_per_proof')} | {g('EDL_c_per_proof')} | {g('EDL_per_action', 4)} | {g('EDL_c_per_action', 4)} | {g('M_per_proof')} |")
    print('\n### T3. Excess over S_own2 (bits per proof; s0 / s1 / s2), F =', f(r3['floor']['F']), '\n')
    print('| stream | EDL excess | > F in 3 / 3 | EDL_c excess | > F in 3 / 3 | capability criterion on 3 / 3 seeds |')
    print('|---|---|---|---|---|---|')
    for S in STREAMS:
        if S == 'S_own2':
            continue
        e = r3['excess_over_S_own2'][S]
        print(f"| {S} | {' / '.join(f(v) for v in e['EDL'])} | {e['exceeds_F_3of3_EDL']} | {' / '.join(f(v) for v in e['EDL_c'])} | "
              f"{e['exceeds_F_3of3_EDL_c']} | {r4['stream_passes_on_all_seeds'][S]} |")
    print('\n### T4. Capability on the 128 test theorems (k 32, T 0.8, sample seed 2; s0 / s1 / s2)\n')
    print('| model | plain pass@32 | plain pass@1 | guided pass@32 | guided pass@1 | criterion |')
    print('|---|---|---|---|---|---|')
    b = [r4['criterion'][f's{s}/S_own'] for s in SEEDS]
    print(f"| learner L_s | {' / '.join(f(v['before_pass32']) for v in b)} | {' / '.join(f(v['before_pass1']) for v in b)} | "
          f"{' / '.join(f(v['guided_before_pass32']) for v in b)} | {' / '.join(f(v['guided_before_pass1']) for v in b)} | – |")
    for S in STREAMS:
        x = [r4['criterion'][f's{s}/{S}'] for s in SEEDS]
        print(f"| θ*({S}) | {' / '.join(f(v['after_pass32']) for v in x)} | {' / '.join(f(v['after_pass1']) for v in x)} | "
              f"{' / '.join(f(v['guided_after_pass32']) for v in x)} | {' / '.join(f(v['guided_after_pass1']) for v in x)} | "
              f"{' / '.join('pass' if v['pass_criterion'] else 'FAIL' for v in x)} |")
    print('\n### T5. Style-blind score ℓ_V (bits per proof; s0 / s1 / s2)\n')
    print('| stream | EDL_V | EDL_V,c | EDL_c (single string) | EDL_V,c excess over S_own2 | single-string EDL_c excess |')
    print('|---|---|---|---|---|---|')
    for S in STREAMS:
        x = [r5['cells'][f's{s}/{S}'] for s in SEEDS]
        rm = r5['removed'].get(S)
        print(f"| {S} | {' / '.join(f(v['EDL_V_per_proof']) for v in x)} | {' / '.join(f(v['EDL_V_c_per_proof']) for v in x)} | "
              f"{' / '.join(f(v['EDL_c_primary_per_proof']) for v in x)} | "
              f"{' / '.join(f(v) for v in rm['excess_EDL_V_c']) if rm else '–'} | {' / '.join(f(v) for v in rm['excess_EDL_c']) if rm else '–'} |")
    print('\n### T6. Secondary: A_fixed (E = 4), cross-fit (exploratory) — EDL_c per proof (s0 / s1 / s2)\n')
    print('| stream | A_fixed lr* | A_fixed EDL | A_fixed EDL_c | cross-fit EDL (swapped) | cross-fit EDL_c (swapped) | mean of directions, EDL | mean of directions, EDL_c |')
    print('|---|---|---|---|---|---|---|---|')
    for S in STREAMS:
        fx = [c[f's{s}/{S}/fixed'] for s in SEEDS]
        xf = [c[f's{s}/{S}/xfit'] for s in SEEDS]
        pr = [c[f's{s}/{S}'] for s in SEEDS]
        print(f"| {S} | {' / '.join(f'{v['lr_star']:g}' for v in fx)} | {' / '.join(f(v['EDL_per_proof']) for v in fx)} | {' / '.join(f(v['EDL_c_per_proof']) for v in fx)} | "
              f"{' / '.join(f(v['EDL_per_proof']) for v in xf)} | {' / '.join(f(v['EDL_c_per_proof']) for v in xf)} | "
              f"{' / '.join(f((a['EDL_per_proof'] + b['EDL_per_proof']) / 2) for a, b in zip(pr, xf))} | "
              f"{' / '.join(f((a['EDL_c_per_proof'] + b['EDL_c_per_proof']) / 2) for a, b in zip(pr, xf))} |")
    print('\n### T7. Addendum-1 attribution (per class; s0 / s1 / s2): n stream / n test, learner bits per proof (stream), EDL_c per class proof\n')
    print('| stream | same: n | same: EDL_c / proof | differ: n | differ: learner bits / proof | differ: θ* test bits / proof | differ: EDL_c / differing proof |')
    print('|---|---|---|---|---|---|---|')
    for S in ('S_own2', 'S_seed', 'S_short', 'S_RL'):
        x = [r6['attribution'][f's{s}/{S}'] for s in SEEDS]
        print(f"| {S} | {' / '.join(str(v['same']['n_stream']) + '+' + str(v['same']['n_test']) for v in x)} | {' / '.join(f(v['same']['EDL_c_class_per_class_proof']) for v in x)} | "
              f"{' / '.join(str(v['differ']['n_stream']) + '+' + str(v['differ']['n_test']) for v in x)} | {' / '.join(f(v['differ']['learner_stream_mean'], 2) for v in x)} | "
              f"{' / '.join(f(v['differ']['theta_test_mean'], 2) for v in x)} | {' / '.join(f(v['differ']['EDL_c_class_per_class_proof'], 2) for v in x)} |")
    print('\n### T8. Seed summaries: IQM (n = 3, so the IQM is the mean) and bootstrap 95 % interval over seeds, bits per proof\n')
    print('| stream | EDL: IQM [95 % CI] | EDL_c: IQM [95 % CI] |')
    print('|---|---|---|')
    for S in STREAMS:
        p = r6['per_seed'][S]
        print(f"| {S} | {f(p['EDL_per_proof']['iqm'])} [{f(p['EDL_per_proof']['ci95'][0])}, {f(p['EDL_per_proof']['ci95'][1])}] | "
              f"{f(p['EDL_c_per_proof']['iqm'])} [{f(p['EDL_c_per_proof']['ci95'][0])}, {f(p['EDL_c_per_proof']['ci95'][1])}] |")
    print('\nSpearman ρ over the six streams (seed means):', {k: round(v, 3) for k, v in r6['rho'].items()})
    print('Style distance (1 − TF agreement, seed means, 256 proofs):', {k: round(v, 4) for k, v in r6['style_distance_all256'].items()})


if __name__ == '__main__':
    main()
