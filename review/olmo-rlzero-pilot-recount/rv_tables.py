#!/usr/bin/env python3
"""Markdown tables for review_olmo-rlzero-pilot.md, generated from out/*.json (no hand-copied numbers)."""
import json

import rv_core as R

S = json.load(open(R.OUT / "stats.json"))
L = json.load(open(R.OUT / "ll_recount.json"))
C = json.load(open(R.OUT / "compute_axis.json"))
MODELS = ["base", "step_0100", "step_0500", "step_2800"]
LAB = {"base": "base `Olmo-3-1025-7B` main", "step_0100": "RL-Zero-Math `step_0100`", "step_0500": "RL-Zero-Math `step_0500`",
       "step_2800": "RL-Zero-Math `step_2800` (= main)"}


def f(x):
    n, mu, lo, hi = x
    return f"{mu:.3f} [{lo:.3f}, {hi:.3f}]"


print("### pass@k (rl grade, phase F samples, Chen estimator, problem bootstrap 95 %)\n")
print("| model (7.3 B, pretrained) | problems | pass@1 | pass@8 | pass@16 |")
print("|---|---|---|---|---|")
for m in MODELS:
    for s in ("all", "aime2024", "aime2025", "aime2026"):
        k1, k8, k16 = (S["passk"].get(f"rl|{m}|{s}|{k}") for k in (1, 8, 16))
        if not k1:
            continue
        print(f"| {LAB[m] if s == 'all' else ''} | {s} (n={k1[0]}) | {f(k1)} | {f(k8)} | {f(k16) if k16 else '—'} |")
print("\nSame-subset (step_0100's half, headline n = %d):\n" % S["half_head"])
print("| model | pass@1 | pass@8 |")
print("|---|---|---|")
for m in MODELS:
    h = S[f"half|{m}"]
    print(f"| {m} | {h['pass1'][0]:.3f} [{h['pass1'][1]:.3f}, {h['pass1'][2]:.3f}] | {h['pass8'][0]:.3f} [{h['pass8'][1]:.3f}, {h['pass8'][2]:.3f}] |")
print("\n### matched k = 8 expected entries / exits\n")
print("| comparison | problems | entries | exits |")
print("|---|---|---|---|")
for k, v in S["dyn_k8"].items():
    print(f"| {k.split('|')[0].replace('_vs_', ' vs ')} | {k.split('|')[1]} ({v['n']}) | {v['entries']:.2f} | {v['exits']:.2f} |")
print("\n### full-budget reach / reverse (headline 83)\n")
print("| checkpoint | reach (c's F) | reach (c's F+C) | strong reach | reverse (c's whole budget) | reach / reverse under `main` | under my integer read-out |")
print("|---|---|---|---|---|---|---|")
for c in ("step_0100", "step_0500", "step_2800"):
    r = S["reach"][c]
    print(f"| {c} | {len(r['reach_fixed'])} | {len(r['reach_any'])} | {len(r['strong'])} | {len(r['reverse'])} | "
          f"{len(r['reach_main'])} / {len(r['reverse_main'])} | {len(r['reach_int'])} / {len(r['reverse_int'])} {r['reach_int'] or ''} |")
print("\n### likelihood (phase L, 250 scored items)\n")
print("| group | items (problems) | base mean log p / token (median) | own (median) | gap own − base, median [p10, p90] | summed gap, median (nats) | inside base_own range | inside base_own + pilot | inside, other problems only |")
print("|---|---|---|---|---|---|---|---|---|")
for g, d in L["groups"].items():
    print(f"| {g} | {d['n']} ({d['n_problems']}) | {d['base_lp_median']:.3f} | {d['own_lp_median']:.3f} | {d['gap_median']:.3f} [{d['gap_p10']:.3f}, {d['gap_p90']:.3f}] | "
          f"{d['sum_gap_median']:.0f} | {d['inside_base_own']:.2f} | {d['inside_base_own_plus_pilot']:.2f} | {d['inside_other_problems']:.2f} |")
print(f"\ncontrol ranges: base_own {L['range_base_own'][0]:.3f} to {L['range_base_own'][1]:.3f} (n = {L['n_base_own']}); "
      f"+ pilot {L['range_base_own_plus_pilot'][0]:.3f} to {L['range_base_own_plus_pilot'][1]:.3f} (n = {L['n_base_own'] + L['n_pilot']})")
print("\n### compute axis (RL ÷ pretraining 6ND = 2.663e23)\n")
print("| step | low | high | geometric mean |")
print("|---|---|---|---|")
for s, (lo, hi, gm) in C["axis"].items():
    print(f"| {s} | {lo:.2e} | {hi:.2e} | {gm:.2e} |")
vi = S["verdict_inputs"]
print(f"\nverdict inputs: base pass@8 {vi['base_pass8'][0]:.3f} [{vi['base_pass8'][1]:.3f}, {vi['base_pass8'][2]:.3f}]; final "
      f"{vi['final_pass8'][0]:.3f} [{vi['final_pass8'][1]:.3f}, {vi['final_pass8'][2]:.3f}]; final − base "
      f"{vi['final_minus_base_pass8'][0]:.3f} [{vi['final_minus_base_pass8'][1]:.3f}, {vi['final_minus_base_pass8'][2]:.3f}]")
