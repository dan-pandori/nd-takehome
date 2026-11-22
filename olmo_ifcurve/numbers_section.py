#!/usr/bin/env python3
"""numbers.md § olmo-ifcurve, generated from the run's files (no hand-copied numbers). VPS-side, stdlib only.

  numbers_section.py > /tmp/section.md      (reviewed, then appended to numbers.md)

Sources: olmo_ifcurve/summary.json, passk.csv, emergence.csv, gaming.csv, lengths.csv, results.csv, compute.csv,
gate_summary.json, checkpoints.csv; podbudget for dollars (stated in the text, not read here).
"""
import csv
import json
from collections import Counter
from pathlib import Path

O = Path("olmo_ifcurve")
S = json.load(open(O / "summary.json"))
G = json.load(open(O / "gate_summary.json"))
PK = list(csv.DictReader(open(O / "passk.csv")))
EM = list(csv.DictReader(open(O / "emergence.csv")))
GA = list(csv.DictReader(open(O / "gaming.csv")))
LE = list(csv.DictReader(open(O / "lengths.csv")))
RE = list(csv.DictReader(open(O / "results.csv")))
CO = list(csv.DictReader(open(O / "compute.csv")))
CK = ["dpo", "s0050", "s0100", "s0200", "s0500", "s0750", "s1100", "s1600", "s2300"]
STEP = {c: (0 if c == "dpo" else int(c[1:])) for c in CK}


def f3(x):
    return "–" if x in (None, "", "None") else f"{float(x):.3f}"


def pk(c, k, grp="all"):
    for r in PK:
        if r["ckpt"] == c and int(r["k"]) == k and r["group"] == grp:
            return r
    return None


out = []
w = out.append
w("## olmo-ifcurve — instruction following over Olmo 3.1 Think 32B's RL run (run olmo-ifcurve, 2026-11-21/22)")
w("")
w("Models: `dpo` = `allenai/Olmo-3-32B-Think-DPO` main (97604023; the RL start, step 0); `sNNNN` = "
  "`allenai/Olmo-3.1-32B-Think` at RL step NNNN (commits in `olmo_ifcurve/checkpoints.csv`; `s2300` = `main` 97ade57a, "
  "weights identical to `step_2300` 29884259). All 32.2 B parameters, bf16, pretrained (Olmo 3 / 3.1 Think recipe: SFT → "
  "DPO → GRPO-style RL on Dolci-Think-RL), evaluated with vLLM 0.11.0 at the Think RL rollout settings (olmo_thinker "
  "template sha eba6e269…, T 1, top-p 1, 32,768 response tokens). Checker: official IFBench / IFEval strict. s0350 was "
  "cancelled (amendment 3), so nine checkpoints. Pre-registration with five amendments: `preregistration/olmo-ifcurve.md`.")
w("")
w("### Arm A — strict pass@k on the 218 IFBench prompts (`olmo_ifcurve/passk.csv`, prompt-bootstrap 95 %)")
w("")
w("| step | draws / prompt | pass@1 | 95 % | pass@4 | pass@8 | 95 % |")
w("|---|---|---|---|---|---|---|")
na = {"dpo": 16, "s0050": 4, "s0200": 4}
for c in CK:
    a, b, d = pk(c, 1), pk(c, 4), pk(c, 8)
    w(f"| {STEP[c]} | {na.get(c, 8)} | {f3(a['pass_at_k'])} | {f3(a['lo95'])}–{f3(a['hi95'])} | {f3(b['pass_at_k'])} | "
      f"{f3(d['pass_at_k']) if d and d['pass_at_k'] else '–'} | "
      f"{(f3(d['lo95']) + '–' + f3(d['hi95'])) if d and d['pass_at_k'] else '–'} |")
w("")
w(f"dpo on its first 8 draws: pass@1 {f3(S['armA']['dpo_first8']['pass@1'])}, pass@8 {f3(S['armA']['dpo_first8']['pass@8'])}. "
  "Stored draws (olmo-ifomega fixed phase) at dpo, 100, 750 and 2,300; new draws elsewhere (s0500: 4 + 4, amendment 5).")
w("")
sh = S["shape"]
w(f"**Shape (reading 5): {sh['reading']}.** Remaining gain to 2,300 with paired 90 % intervals:")
for c, v in sh["spans"].items():
    w(f"- from {STEP[c]}: Δpass@1 {f3(v['d1']['est'])} [{f3(v['d1']['lo90'])}, {f3(v['d1']['hi90'])}], "
      f"Δpass@8 {f3(v['d8']['est'])} [{f3(v['d8']['lo90'])}, {f3(v['d8']['hi90'])}] → sharpening {v['sharpening']}")
w("")
fams = sorted({r["group"] for r in PK if r["group"] != "all"})
w("Per family (first instruction id), strict pass@1 at dpo → s0750 → s2300: " + "; ".join(
    f"{g} (n {pk('dpo', 1, g)['n_prompts']}) {f3(pk('dpo', 1, g)['pass_at_k'])} → {f3(pk('s0750', 1, g)['pass_at_k'])} → "
    f"{f3(pk('s2300', 1, g)['pass_at_k'])}" for g in fams) + ".")
w("")
w("### Arm B — the 48 reach prompts (`olmo_ifcurve/emergence.csv`, `results.csv`)")
w("")
f1 = Counter(r["F1"] or "never" for r in EM)
w("F1 = first checkpoint with ≥ 1 genuine success in its 32 base draws: " + ", ".join(
    f"{STEP[c]}: {f1.get(c, 0)}" for c in CK[1:]) + f", never: {f1.get('never', 0)}. dpo has 0 genuine in ≥ 256 on all 48 "
  "(the set's definition). F1 ≤ 750 on " + str(sum(f1.get(c, 0) for c in CK[1:6])) + " of 48.")
for cl, name in (("P", "prompt-recoverable"), ("T", "teachable only"), ("N", "neither")):
    rs = [r for r in EM if r["class"] == cl]
    w(f"- {name} ({len(rs)}): F1 " + ", ".join(f"{STEP[c]}×{n}" for c, n in sorted(Counter(r['F1'] for r in rs).items(),
                                                                                    key=lambda x: STEP.get(x[0], 9999))))
w("")
for k, v in S["timing"].items():
    w(f"**Timing {k}:** medians P {v['median']['P']:.0f}, T {v['median']['T']:.0f}, N {v['median']['N']:.0f} (n "
      f"{v['n']['P']}/{v['n']['T']}/{v['n']['N']}); rest − P = {v['diff_rest_minus_P']:.0f} steps, 90 % "
      f"[{v['lo90']:.0f}, {v['hi90']:.0f}]; order holds {v['order_holds']} → **{v['reading']}**.")
w("")
cats = S["categories"]
w("**Gradual / abrupt (reading 2; extension cells 128 draws at the checkpoint before F1, all 48):** " + ", ".join(
    f"{k} {v['all']} (P {v['P']}, T {v['T']}, N {v['N']})" for k, v in sorted(cats.items())) + ", abrupt 0. "
  f"F1\\* (any genuine in all draws) is earlier than F1 on {sum(1 for r in EM if r['F1star'] != r['F1'])} prompts "
  f"(the extension cell held a genuine success). Median genuine rate at F1\\*: {f3(S['rate_at_F1star_median'])}.")
s2 = [r for r in RE if r["arm"] == "B" and r["ckpt"] == "s2300"]
w(f"At s2300 (32 fresh draws): ≥ 1 genuine established on {sum(1 for r in s2 if int(r['genuine_labelled']) >= 1)} of 48, "
  f"≥ 2 on {sum(1 for r in s2 if int(r['genuine_labelled']) >= 2)} (lower bounds: cells past F2 / F25 are read only to their "
  f"first 4 strict successes; {sum(int(r['unlabelled']) for r in s2)} s2300 strict successes unread).")
w("")
w("### Arm C — gamed share of strict successes (`olmo_ifcurve/gaming.csv`)")
w("")
w("| step | arm C sample read | gamed | share | arm B first-4 read | gamed | share |")
w("|---|---|---|---|---|---|---|")
for r in sorted(GA, key=lambda r: int(r["step"])):
    w(f"| {r['step']} | {r['armC_labelled']} | {r['armC_gamed']} | {f3(r['armC_share'])} | {r['armB_first4_labelled']} | "
      f"{r['armB_first4_gamed']} | {f3(r['armB_share'])} |")
for nm, k in (("arm C (primary)", "gaming_armC"), ("arm B (secondary)", "gaming_armB")):
    v = S[k]
    w(f"- {nm}: early {f3(v['early'])} (n {v['n_early']}) vs late {f3(v['late'])} (n {v['n_late']}); early − late "
      f"{f3(v['diff_early_minus_late'])}, 90 % [{f3(v['lo90'])}, {f3(v['hi90'])}] → **{v['reading']}**.")
w("")
w("### Arm D — lengths (`olmo_ifcurve/lengths.csv`; medians over arm-A draws; reach = arm-B base draws)")
w("")
w("| step | thinking tokens | answer tokens | answer words | cut at 32,768 | reach thinking | reach answer words |")
w("|---|---|---|---|---|---|---|")
for c in CK:
    a = next(r for r in LE if r["ckpt"] == c and r["set"] == "armA_all")
    b = next((r for r in LE if r["ckpt"] == c and r["set"] == "reach48_armB"), None)
    w(f"| {STEP[c]} | {float(a['think_tok_median']):.0f} | {float(a['ans_tok_median']):.0f} | {float(a['ans_words_median']):.0f} | "
      f"{100 * float(a['cut_share']):.2f} % | {float(b['think_tok_median']):.0f} | {float(b['ans_words_median']):.0f} |"
      if b else f"| {STEP[c]} | {float(a['think_tok_median']):.0f} | {float(a['ans_tok_median']):.0f} | "
      f"{float(a['ans_words_median']):.0f} | {100 * float(a['cut_share']):.2f} % | – | – |")
br = S["brevity"]
w(f"**Brevity (reading 4):** B = {STEP[br['B']]} (median answer words within ±20 % of s2300's {br['m_words']['s2300']:.0f} from "
  f"then on), H = {STEP[br['H']]} (≥ 24 of 48 reach prompts with F2 ≤ H) → **{br['reading']}**.")
w("")
w("### Hand gate (`olmo_ifcurve/handcheck.csv`, `gate_summary.json`)")
w("")
w(f"{G['items']} items read blind ({G['reads']} reads by Claude reader sub-agents, 40-item batches across checkpoints); "
  f"{G['items_2plus_reads']} with ≥ 2 reads ({G['first_two_reads_agree']} first-two agreements), {G['items_3plus_reads']} with 3; "
  f"{G['confirmed']} confirmed by adjudication under rules 1–14 ({G['confirm_changed_label']} label changes; rules 13–14 dated in "
  f"`olmo_ifcurve/handcheck_rule_addendum.md`). The {G['needed_draws']} strict successes the gate needed got their labels from: "
  + ", ".join(f"{k} {v}" for k, v in G["needed_sources"].items()) + f" ({G['needed_labels'].get('genuine', 0)} genuine, "
  f"{G['needed_labels'].get('gamed', 0)} gamed). Other strict successes carry no label (estimated rates use the first-4 share).")
w("")
w("### Compute (`olmo_ifcurve/compute.csv`; registry rows ND_RUN_ID=olmo-ifcurve)")
w("")
tot = Counter()
for r in CO:
    tot["g"] += float(r["gpu_seconds"])
    tot["t"] += int(r["gen_tokens"])
    tot["d"] += int(r["attempts"])
w(f"{len(CO)} sampling job runs on 1 × H200 (TP 1): {tot['g'] / 3600:.2f} GPU-h of load + generation, {tot['t'] / 1e6:.1f} M "
  f"generated tokens, {tot['d']} draws (all graded by the checkers; no training, no Lean).")
print("\n".join(out))
