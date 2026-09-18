#!/usr/bin/env python3
"""Emit the numbers.md bullets for run 4 from artifacts/r4/summary.json (run4_analysis.py) and novelty_summary.json (run4_novelty.py).
Only arms with 8 rounds (or the sprint arms' single round) are printed."""
import json, statistics, collections
S = json.load(open('artifacts/r4/summary.json')); N = json.load(open('artifacts/r4/novelty_summary.json'))
arms = S['arms']; cov = S['coverage']
def fmt(x): return f'{x:.3f}'
draws = sorted({p['draw'] for p in arms.values()})
print('- Base rate per draw (`artifacts/r4/cov_depth3_f0_a1_s<s>.s0.jsonl`, coverage k = 2,000 on the first 300 targets, T = 0.8): ' +
      '; '.join(f"s{s}: {c['depth3_hits']} depth-3 hits / {c['samples']:,} ({c['rate']:.1e}; {c['depth3_targets']} targets), {c['targets_solved']}/{c['n_targets']} targets solved, depth-3 within 256 attempts {c['depth3_targets_within_256']}" if (c := cov.get(str(s)) or cov.get(s)) else f's{s}: missing' for s in draws) + '.')
def arm_row(p):
    ex = f", first pattern update {p.get('first_pattern_update')}, ignition update {p.get('ignition_update')}, var frac update 1 {p['var_frac_update1']:.3f} / last 40 {p['var_frac_last40']:.3f}" if 'updates' in p else ''
    return (f"{p['arm']}: acq **{fmt(p['acq'])}** ({p['acq_theorems']} thms / {p['n_depth3_proofs']} proofs / first round {p['first_round']} / ignition round {p['ignition_round']}), "
            f"per round {p['depth3_theorems_by_round']}, solved {p['targets_solved']}/1000, transfer acq {fmt(p['transfer_acq'])}, held-out greedy {fmt(p['heldout_greedy_by_round'][-1])}{ex}")
for s in draws:
    rows = [p for p in arms.values() if p['draw'] == s and (p['rounds'] == 8 or p['kind'] == 'grpo_sprint')]
    rows.sort(key=lambda p: (p['kind'], p['G'] or 0, p['lr'] or '', p['seed2']))
    print(f'- **Draw s{s}** (`ckpts/r4/stage1_depth3_f0_a1_s{s}.pt`; per-arm files `artifacts/r4/<arm>/round_<r>.json`, `found_8.jsonl`, `updates.jsonl`):')
    for p in rows:
        print('  - ' + arm_row(p))
    nv = N.get(str(s), {})
    if nv:
        print('  - base log p (T = 0.8, own Stage-1, `novelty_depth3_f0_a1_s%d_proofs.jsonl`) of depth-3 proofs: ' % s + '; '.join(
            f"{src} {d['n_depth3_proofs']} proofs, {d['below_1_256']} < 1/256, {d['below_1e5']} < 10⁻⁵, median {d['median_logp_T08']:.1f}, max {d['max_logp_T08']:.2f}, theorems > 1/256: {d['theorems_above_1_256']}" for src, d in sorted(nv.items())) + '.')
# aggregates over primary arms
def agg(kind, G=None, lr=None, seed2=None):
    v = [p['acq'] for p in arms.values() if p['kind'] == kind and p['rounds'] == 8 and (G is None or p['G'] == G) and (lr is None or p['lr'] == lr) and (seed2 is None or p['seed2'] == seed2)]
    ign = [p['ignition_round'] for p in arms.values() if p['kind'] == kind and p['rounds'] == 8 and (G is None or p['G'] == G) and (lr is None or p['lr'] == lr) and (seed2 is None or p['seed2'] == seed2)]
    H = [p['heldout_greedy_by_round'][-1] for p in arms.values() if p['kind'] == kind and p['rounds'] == 8 and (G is None or p['G'] == G) and (lr is None or p['lr'] == lr) and (seed2 is None or p['seed2'] == seed2)]
    if not v: return None
    return f"n = {len(v)}, acq mean {statistics.mean(v):.3f} (min {min(v):.3f}, max {max(v):.3f}), ignited {sum(i is not None for i in ign)}/{len(ign)}, ignition rounds {ign}, held-out greedy mean {statistics.mean(H):.3f} (min {min(H):.3f})"
print('- **Aggregates (round 8, all draws and seeds)**: EI ' + str(agg('ei')) + '; frozen ' + str(agg('frozen')) + '; ' +
      '; '.join(f"GRPO G = {G} lr {lr}: {agg('grpo', G, lr)}" for G in (8, 32) for lr in ('1e-4', '3e-5', '1e-5', '3e-4') if agg('grpo', G, lr)) + '.')
sp = [p for p in arms.values() if p['kind'] == 'grpo_sprint']
if sp:
    print('- Sprint-sized arms (3,200 samples = 100 updates × 4 groups × 8): ' + '; '.join(f"s{p['draw']} lr {p['lr']}: {p['acq_theorems']} depth-3 thms, {p['targets_solved']} solved, H {fmt(p['heldout_greedy_by_round'][-1])}" for p in sorted(sp, key=lambda p: (p['draw'], p['lr']))) + '.')
