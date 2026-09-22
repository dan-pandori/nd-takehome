#!/usr/bin/env python3
"""Markdown tables for numbers.md § lean-only phase 2, printed from artifacts/lo/summary.json and artifacts/lo/e10_patterns.json
(run lean_only_analysis.py phase2 and e10_patterns first).  Lines first, term size second, everywhere."""
import json, os

S = json.load(open('artifacts/lo/summary.json'))
E10 = json.load(open('artifacts/lo/e10_patterns.json')) if os.path.exists('artifacts/lo/e10_patterns.json') else {}
g = lambda d, *ks: (lambda v: v)(__import__('functools').reduce(lambda a, k: a.get(k, {}) if isinstance(a, dict) else {}, ks, d))
f3 = lambda v: '–' if v in (None, {}) else (f'{v:.3f}' if isinstance(v, float) else str(v))
pair = lambda fn: f'{f3(fn(0))} / {f3(fn(1))}'

print('## P2-1 — Stage-1 (full cap-6 set), seeds 0 / 1 (`artifacts/lo/stage1_full_<fmt>_s<s>_{heldout_greedy,transfer2_k16}.json`)')
print('| format | held-out greedy (5,000) | transfer pass@16 (1,638) | tokens per accepted proof, held-out / transfer | distinct transfer proofs | frontier written lines / term size (transfer) | no ND denotation |')
print('|---|---|---|---|---|---|---|')
for fmt, name in (('seq', 'fragment (`have`)'), ('free', 'free-form')):
    st = lambda s, k, f: g(S, 'stage1', f'stage1_full_{fmt}_s{s}', k, f)
    print(f'| {name} | {pair(lambda s: st(s, "heldout", "rate"))} | {pair(lambda s: st(s, "transfer_k16", "rate"))} | '
          f'{pair(lambda s: round(st(s, "heldout", "tokens_per_accepted_proof") or 0, 1))} (held-out), {pair(lambda s: round(st(s, "transfer_k16", "tokens_per_accepted_proof") or 0, 1))} (transfer) | '
          f'{pair(lambda s: st(s, "transfer_k16", "distinct_proofs"))} | lines {pair(lambda s: st(s, "transfer_k16", "frontier_written"))}, term size {pair(lambda s: st(s, "transfer_k16", "frontier_ts"))} | '
          f'{pair(lambda s: st(s, "heldout", "no_nd_denotation"))} (held-out), {pair(lambda s: st(s, "transfer_k16", "no_nd_denotation"))} (transfer) |')
print('- Proposal 8 `lean_seq` seed 0 on file: 0.936 / 0.571 (old BOTE rendering, Lean ∧ `nd_verify`).')
print()
print('## P2-2 — pre-RL base rates, a1 models, 1,000 depth-3 targets × 2,000 samples at T 0.8 (`artifacts/lo/base_d3_<fmt>_s<s>_k2000.json`)')
print('| format | targets solved | depth-3 (ND box depth ≥ 3 on the pruned denoted proof) | depth-3 (`fun` nesting ≥ 3 on the term) | reductio | distinct proofs | proofs without ND denotation |')
print('|---|---|---|---|---|---|---|')
for fmt, name in (('seq', 'fragment'), ('free', 'free-form')):
    b = lambda s, k: g(S, 'base_rates_k2000', f'{fmt}_s{s}', k)
    print(f'| {name} | {pair(lambda s: b(s, "solved"))} | **{pair(lambda s: b(s, "depth3_nd_rate"))}** | {pair(lambda s: b(s, "depth3_lambda_rate"))} | {pair(lambda s: b(s, "reductio_nd_rate"))} | {pair(lambda s: b(s, "distinct_proofs"))} | {pair(lambda s: b(s, "proofs_without_nd_denotation"))} |')
print('- Proposal 8 frozen `lean_seq` controls at 256 attempts: 0.206 / 0.134; token 0.005.')
print()
print('## P2-3 — depth-3 f = 0 dial, 8 rounds × 32 (`artifacts/lo/{ei,frozen}_d3_<fmt>_s<s>/`; `phase2_metrics.arm_metrics`, pattern `depth3`)')
print('| arm | targets solved / 1,000 | **acquisition** (theorems / depth-3 proofs / first round) | acq. re-denoted | λ-depth ≥ 3 theorems | transfer solved / 500, acq | held-out greedy final | term-size hist of counted proofs | round s (r1 … r8) |')
print('|---|---|---|---|---|---|---|---|---|')
for fmt, name in (('seq', 'fragment'), ('free', 'free-form')):
    for kind in ('ei', 'frozen'):
        for s in (0, 1):
            a = g(S, 'depth3_dial', f'{kind}_d3_{fmt}_s{s}')
            if not a: continue
            print(f'| {name} {kind} s{s} | {a["targets_solved"]} | **{a["acq_targets"]:.3f}** ({a["acq_targets_theorems"]} / {a["n_pattern_proofs"]} / r{a["first_round_pattern"]}) | {a["acq_targets_redenoted"]:.3f} | {a["lambda_depth3_theorems"]} | {a["transfer_solved"]}, {a["acq_transfer"]:.3f} | {a["heldout_greedy_final"]:.3f} | {a["ts_hist"]} | {", ".join(str(int(x)) for x in a["round_secs"] if x)} |')
print('- Proposal 8 `lean_seq`: EI 0.476 / 0.479, frozen 0.206 / 0.134; token EI 0.335 / 0.364, frozen 0.005 / 0.005.')
print(f'- Solo timing round (a1 seed 0, 1,000 × 32, nothing else on the GPU): {", ".join(f"{k} {int(v)} s" for k, v in S["timing_solo_d3_round_secs"].items())} (proposal 8: `lean_seq` 141 s, token 59–64 s).')
print()
print('## P2-4 — ladder rung T1, 8 rounds × 32 (`artifacts/lo/la_{T1,frozen}_<fmt>_s<s>/found_transfer_8.jsonl`; pools `data/lo/la_*.jsonl`; `L*` = max L with ≥ 5 transfer theorems solved at label ≥ L)')
print('| arm | **`L*` lines** | **`L*` term size** | transfer solved / 2,285 | by `L_true` 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 | ≥ 5 at `ts_minlen` ≥ 7 / 8 / 9 / 10 | targets solved / 4,495 (`L*` lines / ts) | max written lines / max term size | tokens per proof | held-out greedy r8 | round s (r1, r8) |')
print('|---|---:|---:|---:|---|---|---|---|---:|---|---|')
for fmt, name in (('seq', 'fragment'), ('free', 'free-form')):
    for kind in ('T1', 'frozen'):
        for s in (0, 1):
            a = g(S, 'ladder', f'la_{kind}_{fmt}_s{s}')
            if not a: continue
            bl = ' / '.join(str(a['by_L_true'][str(L)]) for L in range(7, 15)); gt = ' / '.join(str(a['ge_ts'].get(str(t), 0)) for t in (7, 8, 9, 10))
            rs = list(a['by_round'].values())
            print(f'| {name} {kind} s{s} | **{a["lstar_lines"]}** | **{a["lstar_ts"]}** | {a["transfer_solved"]} | {bl} | {gt} | {a["targets_solved"]} ({a["lstar_lines_targets"]} / {a["lstar_ts_targets"]}) | {a["max_written"]} / {a["max_ts"]} | {a["tokens_per_proof"]:.1f} | {a["heldout_final"]:.3f} | {rs[0]["secs"]}, {rs[-1]["secs"]} |')
print('- Proposal 8 `lean_seq` (Stage-1 seed 0, EI seeds 0 / 1): T1 794 / 839 solved, `L*` 11 / 11 (12 / 13 theorems at `L_true` ≥ 11); frozen 304 / 309, `L*` 10 / 10; token T1 612 / 623, `L*` 10 / 10.')
for fmt in ('seq', 'free'):
    for kind in ('T1', 'frozen'):
        for s in (0, 1):
            a = g(S, 'ladder', f'la_{kind}_{fmt}_s{s}')
            if a and a['labels_contradicted']: print(f'- {fmt} {kind} s{s}: pool labels contradicted by a shorter accepted proof: {a["labels_contradicted"]}')
print()
print('## P2-5 — checker of record (`artifacts/lo/record_<arm>_<pool>.json`; `pod/lo/record.py`: every counted proof re-checked from scratch)')
tot = {'n': 0, 'lean_ok': 0, 'nd': 0, 'nd_both': 0, 'text': 0, 'dis': 0, 'ts': 0}
for k, v in S['record'].items():
    tot['n'] += v['n']; tot['lean_ok'] += v['lean_ok']; tot['nd'] += v['nd_proofs']; tot['nd_both'] += v['nd_both_accept']; tot['text'] += v['text_proofs']; tot['dis'] += v['nd_verify_ok_lean_rej'] + v['nd_verify_rej_lean_ok']; tot['ts'] += v['term_size_matches']
print(f'- {len(S["record"])} found files, **{tot["lean_ok"]} / {tot["n"]}** counted proofs re-accepted by `lean_check`; {tot["nd"]} ND-denoting proofs, {tot["nd_both"]} of them `nd_verify`-accepted, **{tot["dis"]} disagreements**; {tot["text"]} proofs stored as Lean text (no in-loop ND denotation); term size reproduced for {tot["ts"]} / {tot["n"]} (the rest: a duplicated subterm in the sampled text vs the canonical rendering).')
print()
print('## P2-6 — in-loop gate totals (`artifacts/lo/gate_*.jsonl`)')
print('| jobs | samples | no EOS | distinct checked | `lean_check` accepts | ND-denoting and `nd_verify` accepts | Lean yes / ND no (by kind) | ND yes / Lean no | Lean process-s |')
print('|---|---:|---:|---:|---:|---:|---|---:|---:|')
for p, v in S['gate'].items():
    if not v.get('samples'): continue
    print(f'| {p} | {v["samples"]:,} | {v["no_eos"]:,} | {v["distinct_checked"]:,} | {v["both_ok"] + v["nd_rej_lean_ok"]:,} | {v["both_ok"]:,} | {v["nd_rej_lean_ok"]:,} {v["disagreement_kinds"]} | {v["nd_ok_lean_rej"]} | {int(v["lean_proc_s"]):,} |')
print()
if E10:
    print('## P2-7 — E10: pattern acquisition of the EI arms (fraction of 1,000 targets with ≥ 1 counted proof containing the pattern; `artifacts/lo/e10_patterns.json`)')
    keys = [k for k in next(iter(E10.values())) if k not in ('solved', 'proofs_unclassified')]
    print('| arm | ' + ' | '.join(keys) + ' |'); print('|---|' + '---|' * len(keys))
    for a, v in E10.items(): print(f'| {a} | ' + ' | '.join(f'{v[k]:.3f}' for k in keys) + ' |')
