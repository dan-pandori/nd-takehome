"""long-pool review, part 4: markdown tables from out/r3_reread.json (per-bin solved, L* with the >=17 file folded in)."""
import json, collections
d = json.load(open('out/r3_reread.json'))
ORDER = ['state-env__la_T1_S_s0_r8', 'state-env__la_T1_S_s1_r8', 'state-env__la_T1_SN_s0_r8', 'state-env__la_T1_SN_s1_r8',
         'ds-generator__la_T1_c0_s0_r8', 'ds-generator__la_T1_c0_s1_r8', 'state-env__stage1_S_s0', 'state-env__stage1_S_s1',
         'state-env__stage1_SN_s0', 'state-env__stage1_SN_s1', 'lean-format__stage1_a1_seq_s0', 'lean-format__stage1_a1_seq_s1',
         'cap-horizon__stage1_k12_s0', 'cap-horizon__stage1_k14_s0']
out = {}
for ps in ('rr', 'rr2'):
    print(f'\n### pass {ps}\n')
    print('| model | 11 | 12 | 13 | 14 | 15 | 16 | ≥17 (of 70) | solved /600 | cum ≥13 | cum ≥15 | L* (600) | L* (600+≥17) |')
    print('|---|' + '---:|' * 12)
    for m in ORDER:
        a = d[f'{ps}/{m}']; g = d[f'{ps}/{m}__ge17']
        bb = {int(k): v for k, v in a['by_bin'].items()}
        s17 = g['by_bin']['17'][0]
        cum = lambda L: sum(bb[x][0] for x in bb if x >= L)
        l1 = max([L for L in range(11, 17) if cum(L) >= 5], default=None)
        l2 = max([L for L in range(11, 18) if cum(L) + s17 >= 5], default=None)
        out[f'{ps}/{m}'] = {'bins': {L: bb[L][0] for L in bb}, 'ge17': s17, 'Lstar': l1, 'Lstar17': l2}
        print(f"| {m} | " + ' | '.join(str(bb[L][0]) for L in range(11, 17)) + f" | {s17} | {a['solved']} | {cum(13)} | {cum(15)} | {l1 if l1 else '<11'} | {l2 if l2 else '<11'} |")
diff = [m for m in ORDER if out[f'rr/{m}'] != out[f'rr2/{m}']]
print('\nmodels whose per-bin counts differ between passes:', diff)
for m in diff:
    print(m, out[f'rr/{m}'], out[f'rr2/{m}'])
print('\nshortest accepted proof, lines minus L_true (pass 2), and median best term size by bin:')
for m in ORDER:
    a = d[f'rr2/{m}']
    print(m, a['shortest_best_lines_minus_L'], a['best_size_median_by_bin'], 'shorter-than-L:', a['written_shorter_than_Ltrue'], a['pruned_shorter_than_Ltrue'])
print('\nsample-level rate by bin (pass 2):')
for m in ORDER:
    print(m, d[f'rr2/{m}']['sample_rate_by_bin'], 'distinct', d[f'rr2/{m}']['distinct_accepted'])
json.dump(out, open('out/r4_tables.json', 'w'), indent=1)
