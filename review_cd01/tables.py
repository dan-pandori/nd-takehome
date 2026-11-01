#!/usr/bin/env python3
"""Reviewer (coe-dose01): markdown tables for review_coe-dose01.md §Recount, generated from review_cd01/out/*.json only."""
import json, statistics as st
O = '/home/dan/work/coe-dose01/review_cd01/out'
J = lambda n: json.load(open(f'{O}/{n}'))
F = J('flops.json'); R = J('reads.json'); S = J('stats.json'); C = J('compute.json'); RC = J('recheck_full.json')
Z = J('sizes.json')
L = []
p = L.append
# y and x per round
p('| round | ' + ' | '.join(f'0.1 % s{s} y / x' for s in range(3)) + ' |')
p('|---|' + '---|' * 3)
ys = {s: J(f'y_la_dose01_s{s}.json')['per_round'] for s in range(3)}
for r in range(1, 17):
    cells = []
    for s in range(3):
        y = ys[s][str(r)]['y']; x = next(q['x'] for q in F[f'la_dose01_s{s}']['rows'] if q['round'] == r)
        cells.append(f"{'**' if y >= 14 and (r == 1 or ys[s][str(r - 1)]['y'] < 14) else ''}{y} / {x:.2f}×{'**' if y >= 14 and (r == 1 or ys[s][str(r - 1)]['y'] < 14) else ''}")
    p(f'| r{r} | ' + ' | '.join(cells) + ' |')
p('| after r16 incl. last fine-tune | ' + ' | '.join(f"x {F[f'la_dose01_s{s}']['x_incl_last_ft']:.2f}×" for s in range(3)) + ' |')
p('')
yk = J('y_la_ko_s1.json')['per_round']
p('| knockout s1 round | ' + ' | '.join(f'r{r}' for r in range(24, 33)) + ' |')
p('|---|' + '---|' * 9)
p('| y (of 106) | ' + ' | '.join(str(yk[str(r)]['y']) for r in range(24, 33)) + ' |')
p('| x (after the round\'s sampling) | ' + ' | '.join(f"{next(q['x'] for q in F['la_ko_s1']['rows'] if q['round'] == r):.2f}×" for r in range(24, 33)) + ' |')
p(f"\nknockout s1 x after r32 incl. its last fine-tune: {F['la_ko_s1']['x_incl_last_ft']:.2f}×; y by family at r32: {yk['32']['by_family']}.")
p('')
# per-seed summary incl. inherited arms
p('| ladder (arm) | y r1 | y r16 | first round y ≥ 14 | x there |')
p('|---|---|---|---|---|')
for t, v in S['per_seed'].items():
    p(f"| {t.replace('coe_', '')} ({v['arm']}) | {v['y_r1']} | {v['y_r16']} | {('r' + str(v['cross_round'])) if v['cross_round'] else 'not by r16'} | {('%.2f×' % v['cross_x']) if v['cross_x'] else '–'} |")
p('')
# reads
p('| read (k 256, T 0.8, batch 512, max_action 512, max_steps 96, read1054) | strict solved / 106 | by family (cc / dno / em / nc / pe / pes / gen) | acquired (≥ 50 %) | read1054 solved | cut-off share: strict 106 / all / worst family |')
p('|---|---|---|---|---|---|')
fam = ['contraposition_conv', 'demorgan_nand_to_or', 'excluded_middle', 'negated_conditional', 'peirce', 'peirce_sequent', 'generated']
def famcells(o):
    return ' / '.join(o['by_family'][f].split('/')[0] for f in fam)
for k in ('dose01_s0', 'dose01_s1', 'dose01_s2', 'ko_s1'):
    for rd, o in R[k].items():
        if rd == 'heldout_p2':
            continue
        if 'cutoff' in o:
            worst = max(((s, c) for s, c in o['cutoff'].items() if s.startswith('fam:')), key=lambda z: z[1][2] or 0)
            cut = f"{o['cutoff']['strict106'][2] * 100:.2f} % / {o['cutoff']['all'][2] * 100:.2f} % / {worst[0][4:]} {worst[1][2] * 100:.1f} %"
        else:
            cut = 'n/a (guided)'
        p(f"| {k} {rd} | {o['strict_solved']} | {famcells(o)} | {', '.join(o['families_acquired']) or 'none'} | {o['solved_all']} | {cut} |")
p('')
p('p2 held-out greedy (5,000; Stage-1 bases): ' + ', '.join(f"s{s} {R[f'dose01_s{s}']['heldout_p2']['solved']}/5000 = {R[f'dose01_s{s}']['heldout_p2']['rate']:.4f}" for s in range(3)))
p('')
# reductio
p('| free positive reductio proofs (pos_free*, all targets), first found in round | ' + ' | '.join(f'r{r}' for r in (1, 2, 3, 4, 5, 8, 12, 16)) + ' |')
p('|---|' + '---|' * 8)
for s in range(3):
    d = J(f'reductio_la_dose01_s{s}_r1-16.json')
    p(f'| 0.1 % s{s} (proofs / targets) | ' + ' | '.join(f"{d['pos_free_by_round'][str(r)]} / {d['pos_free_targets_by_round'][str(r)]}" for r in (1, 2, 3, 4, 5, 8, 12, 16)) + ' |')
dk = J('reductio_la_ko_s1_r25-32.json')
p('\nknockout s1, r25–32 (proofs / targets): ' + ', '.join(f"r{r} {dk['pos_free_by_round'][str(r)]} / {dk['pos_free_targets_by_round'][str(r)]}" for r in range(25, 33)))
p('')
# lean recheck
p('| ladder | distinct counted literal texts (dump, strict members, Lean-accepted in the run) | accepted by my harness | y_lean = y at every round | found_transfer strict rows without a dump text |')
p('|---|---|---|---|---|')
for lad, o in RC.items():
    yy = J(f'y_{lad}.json')['per_round']
    same = all(int(v) == yy[str(r)]['y'] for r, v in o['y_lean'].items())
    p(f"| {lad} | {o['texts']} | {o['accepted']} | {'yes' if same else 'NO'} (r{min(map(int, o['y_lean']))}–r{max(map(int, o['y_lean']))}) | {o['ft_rows_without_dump_text']} {('(rounds ' + ', '.join(sorted(o['ft_rows_without_dump_text_rounds'], key=int)) + '; dump covers r25–32 only)') if o['ft_rows_without_dump_text'] else ''} |")
p('')
p('| ladder | term size median (IQR), 150 sampled texts | pruned lines median (same texts) | written / pruned median, all distinct counted ND proofs | Spearman size vs pruned |')
p('|---|---|---|---|---|')
for lad, o in Z.items():
    p(f"| {lad} | {o['term_size_median']} ({o['term_size_iqr'][0]}–{o['term_size_iqr'][1]}) | {o['pruned_median_sample']} | {o['written_median_all']} / {o['pruned_median_all']} (n {o['n_found_rows']}) | {o['spearman_size_vs_pruned']} |")
p('')
# compute
keys = ['attempts', 'gen_sample', 'gen_eval', 'prefill', 'ft_steps', 'ft_tokens', 'lean_sample', 'lean_eval', 'gpu_s_sample', 'gpu_s_eval', 'gpu_s_ft', 'gpu_s_total']
p('| ladder (A40) | ' + ' | '.join(keys) + ' |')
p('|---|' + '---|' * len(keys))
for lad, t in C['totals'].items():
    p(f'| {lad} ({t["rounds"]} rounds) | ' + ' | '.join(f'{t[k]:.4g}' for k in keys) + ' |')
p('| dose01 ÷ mean(1 %) | ' + ' | '.join(f"{min(C['totals'][f'la_dose01_s{s}'][k] / C['ref_mean_1pct'][k] for s in range(3)):.2f}–{max(C['totals'][f'la_dose01_s{s}'][k] / C['ref_mean_1pct'][k] for s in range(3)):.2f}" for k in keys) + ' |')
open(f'{O}/tables.md', 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
