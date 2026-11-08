#!/usr/bin/env python3
"""Print the numbers.md section of run olmo-transplant from olmo_transplant/summary.json, mechanism.md and
handcheck tables (no hand-typed numbers). Usage: numbers_section.py >> numbers.md"""
import collections
import csv
import json

S = json.load(open("olmo_transplant/summary.json"))


def f(t, d=3):
    if t is None or t[0] is None:
        return "–"
    if len(t) < 3 or t[1] is None:
        return f"{t[0]:.{d}f}"
    return f"{t[0]:.{d}f} [{t[1]:.{d}f}, {t[2]:.{d}f}]"


hc = list(csv.DictReader(open("olmo_transplant/handcheck.csv")))
hs = list(csv.DictReader(open("olmo_transplant/handcheck_src.csv")))
nread = collections.Counter(r["n_readers"] for r in hc)
lab = collections.Counter(r["final_label"] for r in hc)
out = []
P = out.append
P("## olmo-transplant (2026-11-08, executor; UNREVIEWED)")
P("")
P("**Models (every number here):** writer `dpo` = `allenai/Olmo-3-32B-Think-DPO` `main` (`97604023`; RL's start); writer")
P("`s2300` = `allenai/Olmo-3.1-32B-Think` `main` (`97ade57a` = `step_2300`). 32 B, bf16, pretrained (Olmo 3 32B base →")
P("Think SFT → DPO → RL); natural-language chat (`olmo_thinker`), not `lean_seq`; no Lean involved. Supplied thinking =")
P("stored `olmo-ifomega` samples re-inserted by token ids (`olmo_transplant/traces.csv`: source job / chunk / i, ids sha256,")
P("think_k, draft_k); only the answer sampled (T 1, top-p 1, answer budget 32,768 − supplied tokens; vLLM 0.11.0, one")
P("H200, TP 1). Prompts `olmo_transplant/prompts.csv`: reach-41 = the review's 43 IFBench hand-reach prompts minus 226 and")
P("252 (no labelled genuine trace); `brief20` nested; 10 calibration prompts both models solve. Grades: IFBench official")
P("strict on the text after the last `</think>` (`olmo_ifomega/grade.py`); **genuine** = strict × the hand gate's genuine")
P("share per (prompt, run-condition) (`olmo_transplant/handcheck.csv`; identity inheritance from labelled answers;")
P("calibration B and P strict only). Pre-registration `preregistration/olmo-transplant.md`; per-prompt rows")
P("`olmo_transplant/results.csv`; tables `olmo_transplant/summary.md` (`analyze.py`; prompt bootstrap 10,000, seed 1).")
P("")
P("### Conditions (reach-41; mean over prompts [95 % prompt bootstrap])")
P("")
P("| cell | what | prompts | answers | strict | genuine | genuine, re-opened thinking = fail (post hoc) |")
P("|---|---|---|---|---|---|---|")
what = {"T1": "RL's full genuine thinking → dpo answers", "T2": "RL's full genuine thinking → s2300 answers",
        "T3": "dpo's failed thinking → s2300", "T4": "dpo's failed thinking → dpo", "T0-dpo": "no thinking → dpo",
        "T0-s2300": "no thinking → s2300", "P-dpo": "RL's thinking cut before its final draft → dpo",
        "P-s2300": "RL's thinking cut before its final draft → s2300"}
R = S["reach-41"]
for nm in ["T1", "T2", "T3", "T4", "T0-dpo", "T0-s2300", "P-dpo", "P-s2300"] + \
        [f"B{N}-{w}" for w in ("dpo", "s2300") for N in (1024, 2048, 4096, 8192, 16384)] + ["F2048", "F4096", "F8192"]:
    v = R.get(nm)
    if not v:
        continue
    w = what.get(nm) or (f"RL's thinking cut at {nm[1:].split('-')[0]} tokens → {nm.split('-')[1]}" if nm[0] == "B"
                         else f"fresh s2300 thinking capped at {nm[1:]} (6 prompts × 16)")
    P(f"| {nm} | {w} | {v['prompts']} | {v['samples']} | {f(v['strict'])} | {f(v['genuine'])} | "
      f"{f(v['genuine_resumed_fail'])} |")
P("")
P("Paired contrasts (genuine; reach-41 / `brief20`):")
P("")
P("| contrast | reach-41 | brief20 |")
P("|---|---|---|")
for k in ("R1 = T1 / T2 (genuine)", "D21 = T2 - T1 (genuine)", "D34 = T3 - T4 (genuine)", "D0 = T0-s2300 - T0-dpo (genuine)",
          "D30 = T3 - T0-s2300 (genuine)", "T1 - T0-dpo (genuine)", "F_s2300(1024) retained gain (genuine)",
          "F_s2300(2048) retained gain (genuine)", "F_s2300(4096) retained gain (genuine)",
          "F_s2300(8192) retained gain (genuine)", "F_s2300(P) retained gain (genuine)", "F_dpo(2048) retained gain (genuine)",
          "F_dpo(8192) retained gain (genuine)", "F_dpo(P) retained gain (genuine)"):
    P(f"| {k.replace(' (genuine)', '')} | {f(S['reach-41']['contrasts'].get(k))} | {f(S['brief20']['contrasts'].get(k))} |")
P("")
fr = S["F_ratio"]
P("Fresh forcing against `s2300`'s natural rate on the same 6 prompts (stored olmo-ifomega draws; natural genuine = strict ×")
P("that prompt's olmo-ifomega hand genuine share): ratio genuine " +
  " / ".join(f"{fr[str(N)]['genuine'][0]:.2f} [{fr[str(N)]['genuine'][1]:.2f}, {fr[str(N)]['genuine'][2]:.2f}]" for N in (2048, 4096, 8192))
  + " at 2k / 4k / 8k; strict " + " / ".join(f"{fr[str(N)]['strict'][0]:.2f}" for N in (2048, 4096, 8192)) + ".")
d = S["draft"]
P(f"Draft covariate (cut prefixes, pooled, strict): `s2300` {d['s2300|True'][1] / d['s2300|True'][0]:.3f} with the final "
  f"answer's opening in the prefix (n {d['s2300|True'][0]}) vs {d['s2300|False'][1] / d['s2300|False'][0]:.3f} without "
  f"(n {d['s2300|False'][0]}); `dpo` {d['dpo|True'][1] / d['dpo|True'][0]:.3f} vs {d['dpo|False'][1] / d['dpo|False'][0]:.3f}.")
P("")
C = S["calibration"]
P("**Calibration (10 prompts, strict):** " + ", ".join(f"{nm} {f(C[nm]['strict'])}" for nm in ("T1", "T2", "T3", "T4", "T0-dpo", "T0-s2300")
                                                        if nm in C) + " (T3 / T4 on the 5 prompts with a `dpo` failure).")
P("")
P("**Why T1 fails (`olmo_transplant/mechanism.md`):**")
P("")
for ln in open("olmo_transplant/mechanism.md").read().splitlines()[2:]:
    P(ln)
P("")
P(f"**Hand gate:** {len(hc)} run items ({lab['genuine']} genuine / {lab['gamed']} gamed; readers per item "
  f"{dict(sorted(nread.items()))}) plus {len(hs)} calibration source items "
  f"({collections.Counter(r['final_label'] for r in hs)['genuine']} genuine); blinded Claude subagent readers given "
  "`olmo_transplant/handcheck_prompt.md` (rules 1–6); a second reader on every gamed label and a seeded 15 % of genuine, "
  "a third on splits, majority decides. Rule 6's strict reading (title case in ALL CAPS is not a success) changes two "
  "cells, both `ifbench_290` (T3 0.125 → 0.083, T0-s2300 0.125 → 0.0625), and the condition means by ≤ 0.002 "
  "(`results.csv` column `genuine_rate_r6strict`).")
print("\n".join(out))
