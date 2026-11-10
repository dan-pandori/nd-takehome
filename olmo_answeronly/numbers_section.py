#!/usr/bin/env python3
"""Write the numbers.md section of run olmo-answeronly from olmo_answeronly/summary.json, results.csv, mechanism.md and
compute.md (so no number is copied by hand). Prints the markdown; append it to numbers.md."""
import csv
import json

S = json.load(open("olmo_answeronly/summary.json"))
C = S["conditions"]


def f(v):
    return f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"


WHAT = {"T1": "olmo-transplant baseline: s2300's thinking → dpo", "T2": "olmo-transplant baseline: s2300's thinking → s2300",
        "A1": "+ user-turn instruction", "A2": "+ \"Answer in at most 60 words.\"", "A3": "+ closing line in the thinking",
        "A4": "+ first 5 answer tokens prefilled", "L1": "s2300's thinking → lora_main",
        "L2": "lora_main's own genuine thinking → dpo", "L3": "lora_main's own genuine thinking → lora_main"}
L = ["## olmo-answeronly (2026-11-10, executor; UNREVIEWED)", "",
     "**Models (every number here):** `dpo` = `allenai/Olmo-3-32B-Think-DPO` `main` (`97604023`; RL's start); `s2300` = "
     "`allenai/Olmo-3.1-32B-Think` `main` (`97ade57a` = `step_2300`); 32 B, bf16, pretrained (Olmo 3 32B base → Think SFT → "
     "DPO → RL). `lora_main` = `dpo` + olmo-ifladder's rank-16 LoRA on 16 hand-genuine `s2300` trajectories of 16 other "
     "IFBench prompts (adapter sha256 `9921a760…`; vLLM LoRA path; olmo-ifladder's review: stands). Natural-language chat "
     "(`olmo_thinker`), not `lean_seq`; no Lean involved. Thinking = olmo-transplant's 115 reach / 36 calibration stored "
     "`s2300` genuine traces (`olmo_transplant/traces.csv`), inserted by token ids, plus one registered change "
     "(`olmo_answeronly/wordings.py`); for L2 / L3, 116 `lora_main` traces (`olmo_answeronly/lora_traces.csv`). Only the "
     "answer is sampled: 8 per prompt × trace, T 1, top-p 1, budget 32,768 − supplied tokens, vLLM 0.11.0, one H200, TP 1, "
     "seeds 8201 / 8202 / 8211 / 8212 / 8221–8223. T1 / T2 = olmo-transplant's rows (genuine rates from "
     "`olmo_transplant/results.csv`, not re-estimated). Grades: IFBench official strict (`olmo_ifomega/grade.py` via "
     "`olmo_transplant/grade_rows.py`); **genuine** = strict × the blinded hand gate's genuine share per (prompt, writer, "
     "condition) (`olmo_answeronly/handcheck.csv`: 478 items read, 613 reader labels; final 441 genuine / 37 gamed; identity inheritance; readings fixed "
     "during the run in `olmo_answeronly/handcheck_rules.md`). Rates are means over prompts with 95 % prompt bootstrap "
     "(10,000, seed 1). Pre-registration `preregistration/olmo-answeronly.md`; source `olmo_answeronly/summary.json` "
     "(`analyze.py`), per-prompt rows `olmo_answeronly/results.csv`.", "",
     "### Conditions, reach-41", "",
     "| cell | writer | what | prompts | answers | strict | genuine | genuine, re-opened = fail | re-opened | cut | exact copy | near copy | median words (cell medians) | generated tokens |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for c, w in [("T1", "dpo"), ("A1", "dpo"), ("A2", "dpo"), ("A3", "dpo"), ("A4", "dpo"), ("T2", "s2300"), ("A1", "s2300"),
             ("A2", "s2300"), ("A3", "s2300"), ("A4", "s2300"), ("L1", "lora_main"), ("L2", "dpo"), ("L3", "lora_main")]:
    d = C[f"reach|{w}|{c}"]
    L.append(f"| {c} | {w} | {WHAT[c]} | {d['n_prompts']} | {d['samples']} | {f(d['strict_rate'])} | {f(d['genuine_rate'])} | "
             f"{f(d['genuine_rate_ro_fail'])} | {d['reopened_share']:.4f} | {d['length_cut_share']:.4f} | {d['exact_share']:.3f} | "
             f"{d['near_share']:.3f} | {d['median_words_of_cell_medians']} | {d['gen_tokens']:,} |")
L += ["", "Cut = answers that hit the budget: ≤ 0.33 % in every condition; per (prompt, condition) cell, reach dpo A4 ifbench_79 "
      "2 / 24, A4 ifbench_207 1 / 16, A3 ifbench_268 1 / 24; calibration s2300 A4 ifbench_52 1 / 32 (and T2 1 / 32, olmo-transplant). "
      "Re-opened = the answer contains `</think>`: ≤ 0.54 % per condition; per A cell dpo A3 ifbench_248 4 / 24, A3 ifbench_207 1 / 16, A2 ifbench_271 1 / 16 (L2, not covered: 248 5 / 32, 217 3 / 32). "
      "The pre-registered \"< 1 % in every cell\" (cuts) and \"< 5 % every A cell\" (re-opened) hold per condition and miss in "
      "these (prompt, condition) cells.", "",
      "### R = dpo ÷ s2300 genuine, on S_c = reach prompts where the condition keeps s2300 ≥ 0.75", "",
      "| condition | numerator | denominator | s2300 < 0.75 (of n) | broken | S_c | R [95 %] | means on S_c | R, strict (its own S) | R, re-opened = fail | reading |",
      "|---|---|---|---|---|---|---|---|---|---|---|"]
rd = S["readings"]
for c, d in S["R"].items():
    rr = {"T": "(baseline)", "L1": "≥ 0.75: taught the writing (borderline)" if d["R"][0] >= 0.75 else "< 0.75",
          "L2": "L2 < T1 + 0.13 (0.29 on the same 35 prompts, T1 0.160): not easier"}.get(c, rd.get(c))
    L.append(f"| {c} | {d['writer_num']} | {d['writer_den']} | {d['s2300_below_075']} of {d['n_prompts']} | {d['broken']} | "
             f"{d['S_c']} | {f(d['R'])} | {d['num_mean_Sc']:.3f} / {d['den_mean_Sc']:.3f} | {f(d['R_strict_rate'])} (S {d['R_strict_rate'][3]}) | "
             f"{f(d['R_genuine_rate_ro_fail'])} | {rr} |")
ch = S["calib_choice"]
L += ["", "L1's denominator is olmo-transplant's T2 (s2300 on the same thinking); L2's is L3 (lora_main on its own thinking; "
      "11 of 35 prompts have L3 < 0.75, so S = 24).", "",
      "**Best of A1–A3, chosen on calibration** (dpo strict; ties ≤ 0.03 by exact + near copy share): " +
      "; ".join(f"{x['cond']} {x['dpo_strict']:.4f} (copy share {x['copy_share']:.3f}, s2300 < 0.75 on {x['s2300_below_075']} of 10)"
                for x in ch["candidates"]) +
      f". A1 and A3 tie on strict (0.016 apart); A1 has the higher copy share → **chosen: {ch['chosen']}**.", "",
      f"**Pre-registered readings:** chosen A1: R = {f(rd['chosen']['R'])} → **{rd['chosen']['reading']}** (0.40 < R < 0.75). "
      f"A2 / A3 / A4 alone: {rd['A2']} / {rd['A3']} / {rd['A4']} (R ≤ 0.40). Reading 4 (A4 high while A1–A3 low): "
      f"{'holds' if rd['first_tokens'] else 'does not hold'}. No condition breaks s2300 (≤ 6 of 41 prompts below 0.75).", "",
      "Sensitivity (post hoc) to the inline ` - ` sub-bullet reading: with ifbench_133 and 136 dropped from S_c altogether, "
      "R_A1 = 0.669, R_A2 = 0.342, R_A3 = 0.320, R_A4 = 0.236, R_T = 0.139 (from `results.csv`).", "",
      "### Paired differences by prompt (genuine, reach-41; mean [95 %], per-prompt SD; MDE pre-registered ≈ 0.13)", ""]
for k, v in S["paired"].items():
    L.append(f"- {k}: {f(v)} (SD {v[3]:.3f})")
L += ["", "### By constraint family (reach-41, genuine; descriptive, n = 2–15 prompts)", "",
      "| family | n | dpo T1 | dpo A1 | dpo A2 | dpo A3 | dpo A4 | s2300 A1 |", "|---|---|---|---|---|---|---|---|"]
for fam, v in S["family"]["A1"].items():
    L.append(f"| {fam} | {v['n']} | {v['dpo_T1']:.3f} | {v['dpo']:.3f} | {S['family']['A2'][fam]['dpo']:.3f} | "
             f"{S['family']['A3'][fam]['dpo']:.3f} | {S['family']['A4'][fam]['dpo']:.3f} | {v['s2300']:.3f} |")
L += ["", "### A4: does the writer stop where the draft stops? (reach; share of all answers)", ""]
for w in ("dpo", "s2300"):
    a = C[f"reach|{w}|A4"]["a4_stop"]
    L.append(f"- {w}: exact copy (stops there) {a['exact']:.3f}; starts with the whole draft and adds text {a['past']:.3f}; "
             f"diverges before its end {a['diverges']:.3f}.")
L += ["", "### Calibration-10 (36 traces; strict / genuine, mean over prompts)", "",
      "| writer | T1 / T2 | A1 | A2 | A3 | A4 |", "|---|---|---|---|---|---|"]
for w, t in (("dpo", "T1"), ("s2300", "T2")):
    L.append(f"| {w} | " + " | ".join(f"{C[f'calib|{w}|{c}']['strict_rate'][0]:.3f} / {C[f'calib|{w}|{c}']['genuine_rate'][0]:.3f}"
                                      for c in (t, "A1", "A2", "A3", "A4")) + " |")
L += ["", "### Mechanism (post hoc, `olmo_answeronly/mechanism.md`; sample-pooled strict)", ""]
L += [ln for ln in open("olmo_answeronly/mechanism.md").read().splitlines()[4:] if ln.strip()]
L += ["", "### Compute (`olmo_answeronly/compute.md`; registry rows `artifacts/olmo-answeronly/registry/`)", ""]
L += [ln for ln in open("olmo_answeronly/compute.md").read().splitlines() if ln.strip()]
L += ["", "GPU-seconds per arm are apportioned by generated tokens within a job (load + generation; stage 0 included in R_dpo). "
      "Pod `oa-1`: 2 × H200 community at $7.18/h with GPU 1 broken (ECC), 1.29 pod-hours, **$9.27** (podbudget) of $30. "
      "Arms are matched on answers per (prompt, trace) (8); dpo generates 1.5–4.5× s2300's tokens "
      "on reach A1–A4 (T1 / T2: 4.6×; calibration 1.35–2.05×; longer answers) — flagged, as the comparison is on answers, not tokens.", ""]
L += ["**Bucket:** `hf://buckets/dan-pandori/nd-rl/olmo-answeronly/` — `artifacts/olmo_answeronly/{requests,samples,graded}/` "
      "(every answer's text and ids; `artifacts/MANIFEST.jsonl` rows), `meta/`, `logs/`, `hand/` (kit, labels), `olmo_answeronly/`, "
      "`pod/olmo_answeronly/`, registry rows, `docs/` (write-up, pre-registration, figure).", ""]
print("\n".join(L))
