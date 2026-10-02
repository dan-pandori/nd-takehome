# Part A notes (experiment-summaries 2026-06-09..09-19 + synthetic-cap6-proof-lengths.md)

## Protocol differences
- **Checker.** No Lean judging in this window.
  - June sprints use the old `nd_sprint` verifier. The r1-cot review found it **unsound**: it accepts forward subproof references.
  - Codex imports use a strict replay verifier.
  - Dan-agents runs use take-home `nd_verify`. Round2-run1's nd2lean agrees with it on 253,470 positives and 4,012 mutations. However, Lean itself judged only 1,106 negatives (all type errors); citation and box errors were caught by Python pre-checks. Also, Lean's `¬A := A→False` admits proofs that nd_verify rejects.
- **Textbook pools differ.**
  - textbook36: June, pass@16 T1.0, 10/36 renaming overlap with training.
  - textbook58-dev: adaptive panel, 16 samples, T0.8 (r1-cot) or T unstated (cap-comparison).
  - validation-36 and schema623: novelty campaign.
  - 760 schema instances inside ladder-A transfer.
  - **No textbook72, dev metric or holdout250 anywhere in this window.**
- **L\*** exists only in ladder-A. It is minlen-labelled, and ≥76 labels are one line too long. June and cap6-lengths report the longest written/pruned certificate, which is a different quantity.
- **Budgets.**
  - EI: 8×32. Frozen: 256. Base: pass@10⁴ or 600k per draw.
  - Ladder-A T6 trains two models (equal samples, not equal compute).
  - Run4 GRPO a1 s0 G8 is reported at round 7.
- **Seeds.** Codex imports and June Part II are one seed. Dan-agents runs use 2–3 seeds per cell, and run-to-run spread is often as large as the arm effects.
- `reviewed-findings` = reviewer marked a claim "not supported"; numbers reproduced everywhere.

## Create vs elicit
- **june-bootstrapping**: EI banks proofs beyond resampling (747 vs 607/1200), but transfer pass@64 rises only +1 pp (offset). Reads as **amplification**. Caveats: unsound verifier, textbook overlap.
- **r1-cot / cap-comparison**: 0/43 textbook targets beyond cap 6 are solved; RL adds ≤2 targets. **No creation seen** (one seed).
- **novelty-p1**: 348/1,411 RL-solved theorems are outside base 10⁴ reach, and nine-line proofs have p<1e-5. The surprisal sits in one line. **Amplification of rare paths.**
- **novelty-p2/ignition**: depth-3 at f=0 reaches 0.27–0.36 with frozen at 0. This was read as **creation by structural repetition**, but some draws have a base rate of 10⁻²–10⁻³. Reductio ignites only from a nonzero pre-RL rate: **elicitation**.
- **r2-run5**: on required reductio, zero-rate draws give 0/300 and the nonzero draw gives 51 (frozen 4). Derived-ORE (cap 8): EI ≈2× frozen. **Elicitation/amplification.**
- **r2-run2**: 0/6 patterns come from zero-rate draws. negi (3 hits/600k) reaches 0.147. Cap-8 depth-4 already appears before RL. **Elicitation**; the only creation happened in pretraining.
- **r2-run3**: one injected valid pattern proof ignites dead arms; non-pattern proofs do not. **Data-driven elicitation.**
- **r2-run4**: GRPO beats EI on depth-3 (0.40–0.51 vs 0.34–0.36) at a held-out cost. All priors are nonzero: **amplification**.
- **r3-run1**: neighbour pools switch ignition on (9/16 vs 1/16). Reductio s21 appears from 0/600k. Points to **curriculum-mediated creation**, but the depth-3 neighbours were pattern-bearing.
- **r3-run2/run3**: "zero-rate" draws do emit the pattern at 6–7 lines, and every pre-RL hit is cap+1 lines. The 8-line stratum is crossed in 1/6 runs. **Elicitation, then length extension.**
- **r3-run4a**: confined to the 7-line stratum at 3.2M, 25M and 85M, and governed by the base rate. **Elicitation.**
- **r3-run4b**: with neighbours, EI acquires 206–231 required targets, all outside base 10⁴ reach. This is the **strongest creation-like point**, but size, schedule and LR are confounded.
- **ladder-A**: L\* goes 7→10 for every rung, with base p<1e-5. Yet it is one implication-tower family, still rising when stopped. **Extension of a known family.**

## Missing
- OLMo, FLoP and fragment synthetic pools are not in metrics.
- The June fixed frozen control ("359–364") is ambiguous, so it was omitted.
- Cap-comparison temperature is not stated.
- Fragment-selection RL endpoints are given only as the range 269–279.
- Params are unknown for FLoP and FOL.
