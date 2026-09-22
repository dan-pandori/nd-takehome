#!/usr/bin/env python3
"""Write data/dsc/README.md (shape, overlap and render-check tables of every set) from data/dsc/shape_<tag>.json and assemble_report_<arm>.json."""
import json, os, glob
D = 'data/dsc'
TAGS = [('c0', 'C0 control (`data/p2/train_depth3_f0_a1.jsonl`)'), ('a1', 'A1 natural histogram'), ('a2', 'A2 rule quotas'), ('a3', 'A3 cap 8 (yardstick, outside the cap-6 rule)'), ('a4', 'A4 cap-heavy dose')]
S = {t: json.load(open(f'{D}/shape_{t}.json')) for t, _ in TAGS if os.path.exists(f'{D}/shape_{t}.json')}
R = {t: json.load(open(f'{D}/assemble_report_{t}.json')) for t, _ in TAGS if os.path.exists(f'{D}/assemble_report_{t}.json')}
L = []
L.append('# ds-composition sets (`dsc_assemble.py`, seed 0; every record re-verified by `nd_verify`, cap asserted, depth-3 excluded in the pruned and written form)\n')
L.append('Pools: `data/p2/pool_cap6_recon.jsonl` (723,534 classes, the control\'s pool; full-pool length shares 10.42 / 12.63 / 15.53 / 20.60 / 40.82 %), '
         '`data/dsc/raw_ore*.w*.jsonl` (A2 ORE top-up: `make_coverage_sets.py gen --only rule:ORE`, unchanged generator, output filter only, 2 × 3,000,000 tries, '
         '12,776 raw ORE proofs), `data/p2/pool_cap8.jsonl` (A3\'s 7–8-line records). Exclusions by renaming class: p2 held-out, `{targets,transfer}_depth3`, '
         '`{targets,transfer}_reductio_req`, `r3_1/depth3_req{,_transfer}`, ladder `rl_targets` / `transfer`, validation-36 (14,026 classes). '
         'Sets are stored gzipped (`train_<arm>.jsonl.gz`); the pods gunzip them; `train.py --cap` re-asserts the cap and the `lean_seq` round trip on every record.\n')
L.append('## Shape table\n')
tags = [t for t, _ in TAGS if t in S]
L.append('| quantity | ' + ' | '.join(tags) + ' |'); L.append('|---|' + '---|' * len(tags))
def row(name, f):
    L.append(f'| {name} | ' + ' | '.join(f(S[t]) for t in tags) + ' |')
row('records', lambda s: f"{s['n']:,}")
for k in range(2, 9):
    row(f'length {k}', lambda s, k=k: f"{s['len_hist'].get(str(k), 0):,} ({100 * s['len_hist'].get(str(k), 0) / s['n']:.1f} %)")
for k in range(0, 3):
    row(f'written box depth {k}', lambda s, k=k: f"{s['written_box_depth_hist'].get(str(k), 0):,}")
row('depth ≥ 3 (pruned or written)', lambda s: str(s['depth3_count']))
for ru in ['AS', 'IMPI', 'IMPE', 'NEGI', 'DN', 'NEGE', 'ANDI', 'ORI1', 'ORI2', 'R', 'ORE', 'ANDE1', 'ANDE2', 'BOTE']:
    row(f'proofs using `{ru}`', lambda s, ru=ru: f"{100 * s['rule_share'][ru]:.2f} %")
row('proofs using `ANDE1` or `ANDE2`', lambda s: f"{100 * s['ande_any_share']:.2f} %")
row('boxes inside an `ORE` branch (proofs)', lambda s: str(s['boxes_inside_ore_proofs']))
for k in range(0, 4):
    row(f'{k} premises', lambda s, k=k: f"{s['n_prem_hist'].get(str(k), 0):,}")
row('classically unsatisfiable premise set', lambda s: f"{100 * s['contradictory_premise_share']:.1f} %")
row('conclusion is a premise', lambda s: f"{100 * s['trivial_prem_is_concl_share']:.2f} %")
row('derived-`ORE` proofs (pruned / written)', lambda s: f"{s['pattern_counts']['derived_ore_pruned']:,} / {s['pattern_counts']['derived_ore_written']:,}")
row('reductio proofs (pruned / written)', lambda s: f"{s['pattern_counts']['reductio_pruned']:,} / {s['pattern_counts']['reductio_written']:,}")
row('`lean_seq` tokens, prompt + proof mean', lambda s: f"{s['tokens_lean_seq']['prompt_mean']:.1f} + {s['tokens_lean_seq']['proof_mean']:.1f} = {s['tokens_lean_seq']['total_mean']:.1f}")
row('`lean_seq` tokens, proof max / total max', lambda s: f"{s['tokens_lean_seq']['proof_max']} / {s['tokens_lean_seq']['total_max']}")
L.append('\n"Classically unsatisfiable premise set": the premises have no satisfying valuation (truth tables), a wider definition than the proposal\'s 6.1 % '
         '"contradictory-premise theorems"; the same function is applied to every set.\n')
if 'a2' in R and R['a2'].get('quota_report'):
    L.append('## A2 quota report (`assemble_report_a2.json`)\n')
    L.append('| rule | quota | already in earlier quota picks | added | added by length | available by length |'); L.append('|---|---|---|---|---|---|')
    for ru, q in R['a2']['quota_report'].items():
        L.append(f"| {ru} | {q['quota']:,} | {q['already']:,} | {q['added']:,} | {q['by_len']} | {q['avail_by_len']} |")
    L.append('')
L.append('## Overlap with the evaluation pools (renaming classes; order-sensitive `key` / premise-order-insensitive)\n')
pools = list(next(iter(S.values()))['overlap'].keys())
L.append('| pool (n) | ' + ' | '.join(tags) + ' |'); L.append('|---|' + '---|' * len(tags))
for p in pools:
    n = next(iter(S.values()))['overlap'][p]['pool_n']
    L.append(f'| `{p}` ({n:,}) | ' + ' | '.join(f"{S[t]['overlap'][p]['order_sensitive']} / {S[t]['overlap'][p]['premise_order_insensitive']}" for t in tags) + ' |')
L.append('\nOrder-sensitive overlaps are 0 by construction (exclusion by `key`); the premise-order-insensitive count is the number of set classes that '
         'equal a pool class after sorting premises and minimising over the 24 atom permutations (the lean-format review\'s definition).\n')
L.append('## Render check (3,000 records → `lean_seq` text → inverse; Lean on 1,000 literal texts; 300 statement-swapped negatives)\n')
L.append('| set | rendered | inverse identical | Lean accepted (of 1,000) | negatives rejected (of 300) |'); L.append('|---|---|---|---|---|')
for t in tags:
    r = S[t]['render_check']
    L.append(f"| {t} | {r['rendered']} | {r['inverse_identical']} | {r['lean_positive_accepted']} | {r['lean_negative_rejected']} |")
L.append('\n## Assembly reports\n')
for t in tags:
    if t in R:
        r = R[t]
        L.append(f"- **{t}**: counts {r['counts']}; sources {[os.path.basename(x) for x in r['sources']]}; scan {json.dumps({os.path.basename(k): {kk: vv for kk, vv in v.items() if not kk.startswith('eligible_len')} for k, v in r['scan_stats'].items()})}; {r['secs']:.0f} s.")
open(f'{D}/README.md', 'w').write('\n'.join(L) + '\n')
print('\n'.join(L[:40]))
