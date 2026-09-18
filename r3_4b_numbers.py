#!/usr/bin/env python3
"""round3-run4b: print the numbers.md tables from artifacts/r3_4b/summary.json (r3_4b_analysis.py) and artifacts/r3_4b/diag_*.json."""
import json, glob, re, os
S = json.load(open('artifacts/r3_4b/summary.json'))
ORDER = ['3.2M', '25M', '25Mr', '85M', '85Mr']
LAB = {'3.2M': '3.2M (run 1, seeds 20–27)', '25M': '25M first schedule', '25Mr': '25M retry', '85M': '85M first schedule', '85Mr': '85M retry'}


def fmt(x, f='{:.3f}'):
    return f.format(x) if isinstance(x, (int, float)) else '—'


print('**Per draw** (`artifacts/r3_4b/summary.json`; pre-RL = `cov_depth3_<tag>.s0[r].jsonl`, optional pool = `optcov_depth3_<tag>.s0.jsonl`, arms = `ei_depth3_<tag>_{req,frozen,mix}/`, base@10⁴ = `cov1e4_depth3_<tag>.s0[r].jsonl`):\n')
print('| size / schedule | draw | parameters | held-out greedy | final val loss | required pool: pattern hits / samples (targets) | optional pool: hits / samples (targets) | `req` required targets w/ pattern, rounds 1–8 | frozen r8 | `mix` required targets w/ pattern, rounds 1–8 | `mix` ignition round (≥ 20; ≥ 6) | `mix` neighbours solved r8 | required solved w/o pattern (req / mix) | base@10⁴: hits / samples (targets) | EI-only / acquired (mix) | verify fails / checked (req; mix) |')
print('|' + '---|' * 16)
for k in ORDER:
    for s, d in S['sizes'].get(k, {}).items():
        p, o, r, f, m, b, e = (d.get(x) for x in ('pre_rl', 'optional_pool_pre_rl', 'req', 'frozen', 'mix', 'base_1e4', 'ei_only_mix'))
        e2 = d.get('ei_only_mix_at_2000')
        row = [LAB[k], s, str(d.get('params', '—')), fmt(d.get('heldout_greedy')), fmt((d.get('stage1_last') or {}).get('val'), '{:.4f}'),
               f"{p['hits']} / {p['n_tried']:,} ({p['targets_with_pattern']})" if p else '—',
               f"{o['hits']} / {o['n_tried']:,} ({o['targets_with_pattern']})" if o else '—',
               str([x['pattern_required'] for x in r['per_round']]) if r else '—',
               str(f['final_pattern_required']) if f else ('= req (skipped)' if d.get('frozen_skipped') else '—'),
               str([x['pattern_required'] for x in m['per_round']]) if m else '—',
               f"{m['ignition_round'] or '—'}; {m['ignition_round_2pct'] or '—'}" if m else '—',
               f"{m['final_solved_neighbour']} / {m['n_neighbour']}" if m else '—',
               f"{len(r['required_solved_without_pattern']) if r else '—'} / {len(m['required_solved_without_pattern']) if m else '—'}",
               f"{b['hits']} / {b['n_tried']:,} ({b['targets_with_pattern']})" if b else '—',
               (f"{e['ei_only']} / {e['acquired']}" if e else (f"{e2['ei_only']} / {e2['acquired']} (base at 2,000 only)" if e2 and e2['acquired'] else '—')),
               f"{r['verify_failures']} / {r['verify_sample']}; " + (f"{m['verify_failures']} / {m['verify_sample']}" if m else '—') if r else '—']
        print('| ' + ' | '.join(row) + ' |')

print('\n**By size / schedule:**\n')
print('| size / schedule | draws | held-out greedy (min–max; median) | non-zero draws, required pool | total pattern hits / samples, required pool | non-zero draws, optional pool | `req` arms igniting | `mix` arms igniting | `mix` required targets at r8 |')
print('|' + '---|' * 9)
for k in ORDER:
    ds = list(S['sizes'].get(k, {}).values())
    if not ds:
        continue
    hg = sorted(d['heldout_greedy'] for d in ds if isinstance(d.get('heldout_greedy'), float))
    pre = [d['pre_rl'] for d in ds if d.get('pre_rl')]; opt = [d['optional_pool_pre_rl'] for d in ds if d.get('optional_pool_pre_rl')]
    req = [d['req'] for d in ds if d.get('req')]; mix = [d['mix'] for d in ds if d.get('mix') and d['mix']['rounds_done'] == 8]
    print('| ' + ' | '.join([LAB[k], str(len(ds)), (f"{hg[0]:.3f}–{hg[-1]:.3f}; {hg[len(hg) // 2]:.3f}" if hg else '—'),
                             f"{sum(not p['zero_rate'] for p in pre)} / {len(pre)}", f"{sum(p['hits'] for p in pre)} / {sum(p['n_tried'] for p in pre):,}",
                             (f"{sum(not p['zero_rate'] for p in opt)} / {len(opt)}" if opt else '—'),
                             f"{sum(r['ignition_round'] is not None for r in req)} / {len(req)}", f"{sum(m['ignition_round'] is not None for m in mix)} / {len(mix)}",
                             str(sorted(m['final_pattern_required'] for m in mix))]) + ' |')

print('\n**Writing diagnostic** (`artifacts/r3_4b/diag_<tag>.json`, `r3_4b_depthdiag.py`: 64 samples × first 60 required targets = 3,840 per model, T = 0.8; none verifies):\n')
print('| size / schedule | draw | samples opening a third box | of which malformed ("depth jump") | samples with ≥ 7 lines | with ≥ 8 lines | `mix` ignition round |')
print('|' + '---|' * 7)
for k in ORDER:
    for fn in sorted(glob.glob(f'artifacts/r3_4b/diag_{k}_s*.json'), key=lambda f: int(re.search(r'_s(\d+)\.json', f).group(1))):
        D = json.load(open(fn)); s = re.search(r'_s(\d+)\.json', fn).group(1)
        m = (S['sizes'].get(k, {}).get(f's{s}') or {}).get('mix')
        d3 = sum(v for kk, v in D['written_max_depth_hist'].items() if int(kk) >= 3)
        dj = sum(v for rr, v in D['depth_ge3_reasons'] if 'depth jump' in rr)
        l7 = sum(v for kk, v in D['lines_written_hist'].items() if int(kk) >= 7); l8 = sum(v for kk, v in D['lines_written_hist'].items() if int(kk) >= 8)
        print(f"| {LAB[k]} | s{s} | {d3} | {dj} | {l7} | {l8} | {(m['ignition_round'] or '—') if m and m['rounds_done'] == 8 else 'n/a'} |")
