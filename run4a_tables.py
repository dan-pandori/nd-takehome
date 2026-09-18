#!/usr/bin/env python3
"""round3-run4a: markdown tables for numbers.md from artifacts/r3_4a/summary.json (+ heldout_split.json).  python3 run4a_tables.py"""
import json
S = json.load(open('artifacts/r3_4a/summary.json')); H = json.load(open('artifacts/r3_4a/heldout_split.json'))
def f(x, d=3):
    return '–' if x is None else (f'{x:.{d}f}' if isinstance(x, float) else str(x))
print('| draw | params | Stage-1 steps / val | held-out greedy (all / non-reductio) | pre-RL strict hits / 600k (rate) | targets hit (7/8/9/10) | pass@256 targets | EI acquired (7/8/9/10) | per round | ignition round | trained rounds | frozen | transfer acq. (of 150) | solved w/o pattern (EI/frozen/cov) | base-reachable@1e4 of acquired | EI-only fraction |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for sz, cell in S['sizes'].items():
    for tag, D in cell['draws'].items():
        s1 = D.get('stage1', {}); p = D['pre_rl']; e = D['ei']; z = D['frozen']; b = D.get('base10k'); h = H.get(tag, {})
        if not p:
            continue
        samples = p['samples']
        row = [tag, f(s1.get('params')), f"{f(s1.get('steps'))} / {f(s1.get('val_loss'), 4)}" if s1 else 'run 5',
               f"{f(s1.get('heldout_greedy'), 4)} / {f(h.get('non_reductio'), 4)}" if s1 else '–',
               f"{p['strict_hits']} / {samples:,} ({p['rate']:.1e})" + ('' if p['complete'] else ' INCOMPLETE'),
               f"{p['targets_hit']} ({'/'.join(str(p['targets_hit_by_stratum'][k]) for k in ('7','8','9','10'))})", str(p['pass_at_256_targets'])]
        if e:
            row += [f"{e['acquired']} ({'/'.join(str(e['acq_by_stratum'][k]) for k in ('7','8','9','10'))})", ' '.join(map(str, e['acq_by_round'])), f(e['ignition_round']), str(e['trained_rounds'])]
        else:
            row += ['–'] * 4
        row += [str(z['acquired']) if z else '–', f"{e['transfer_acquired']} ({'/'.join(str(e['transfer_by_stratum'][k]) for k in ('7','8','9','10'))})" if e and 'transfer_acquired' in e else '–',
                f"{e['solved_without_pattern'] if e else '–'}/{z['solved_without_pattern'] if z else '–'}/{p['solved_without_pattern']}"]
        row += [f"{b['acquired_base_reachable']} / {b['acquired_covered']}", f"{b['ei_only']} / {b['acquired_covered']} = {b['ei_only_fraction']:.2f}"] if b else ['–', '–']
        print('| ' + ' | '.join(row) + ' |')
print()
print('| cell | draws sampled | non-zero draws (≥ 1 strict hit in 600k) | rates of non-zero draws | igniting (EI ≥ 6 targets by round 8) | EI-only fractions |')
print('|---|---|---|---|---|---|')
for sz, cell in S['sizes'].items():
    ds = [d for d in cell['draws'].values() if d['pre_rl'] and d['pre_rl']['complete']]
    nz = [d for d in ds if d['pre_rl']['targets_hit_within_2000'] > 0]
    print(f"| {cell['label']} | {len(ds)} | {len(nz)} | {', '.join(f'{d['pre_rl']['rate']:.1e}' for d in nz) or '–'} | {sum(1 for d in ds if d['ei'] and d['ei']['ignition_round'])} | "
          f"{', '.join(f'{d['base10k']['ei_only_fraction']:.2f}' for d in ds if d.get('base10k')) or '–'} |")
