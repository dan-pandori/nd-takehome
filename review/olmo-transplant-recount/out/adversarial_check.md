# Adversarial check of review_olmo-transplant.md (independent read-only subagent, 2026-11-08 10:15–10:40 UTC)

Run on the draft that had §Recount (as committed in e80ba754) plus a first §Compare / §Verdict. 25 findings:
WRONG 5, INCONSISTENT 5, OVERCLAIM 6, UNTRACEABLE 1, MINOR 8; ≈ 550 checks passed (all 336 rate / contrast / F(N)
table cells against rates_*.json, the expected-results table, readings 1–7 in 7 label modes, hard constraints,
provenance, sets, protocol, label counts, the hand-gate method counts, sharetest / vacuous / mech / copy / lengths,
compute, and every §Compare quote but one). Each finding and where it was addressed:

| # | severity | finding (condensed) | addressed |
|---|---|---|---|
| 1 | WRONG | cut-only B curve and N / c bins are pre-registered (prereg "Two B curves"; "Also against N / c, post hoc in bins") and omitted by the executor; the review called them post hoc / "not errors" | §Compare #23 (omitted pre-registered analyses), §Verdict 4, Corrections 1 |
| 2 | WRONG | post-hoc F_s2300(P) = 0.249 mixed G(P) over 38 prompts with G(0), G(full) over 41; on the executor's definition (38 prompts for all three) it is 0.258 (> 0.25) | recomputed (`rvt_phase2_checks.py` [10]): 0.258 exec labels / 0.2499 mine; §Compare #9, #11, §Verdict 2 |
| 3 | WRONG | registry contrast rows (96) have `ckpt` null, incl. single-writer retained gains | Model-labels paragraph; §Verdict 6 |
| 4 | WRONG | plain summary's "256 tries" is unattributed (only the ≈ 44 % is) | §Compare #22; Model-labels paragraph |
| 5 | WRONG | the executor states natural genuine 0.685 in `summary.md`, not an "implied 0.686" | §Compare #8 |
| 6 | INCONSISTENT | "only number wrong" vs #16 / #19 marked "differs" | §Verdict "Not supported" lists #8, #16, #19 |
| 7 | INCONSISTENT | reading 4's fresh clause 0.27 = genuine / strict basis; genuine / genuine is 0.24 | Corrections 2 |
| 8 | INCONSISTENT | F_dpo(P) 0.140 / 0.146 / 0.15 | executor's definition used throughout §Compare / §Verdict (0.146; 0.15 rounded) |
| 9 | INCONSISTENT | "both draft effects" listed as misses; RL's +0.16 is inside 0.15–0.60 | "Expectations and misses" paragraph |
| 10 | INCONSISTENT | pod time 05:36:07 (line 27) vs 05:35:50 / 05:36:07 (#20) | Corrections 3; `out/facts.txt` |
| 11 | OVERCLAIM | results.csv comparison scope (F rows not compared; 73 calibration cells skipped and carrying artifacts) | F rows compared (0 differences); scope stated; §Compare #24 |
| 12 | OVERCLAIM | "every cell reproduces" without recomputing the post-hoc column; brief20 F(P) | `exec_held` mode reproduces the column 21 / 21; F(P) on the executor's definition reproduces incl. brief20; §Compare #17 |
| 13 | OVERCLAIM | "reports it for P only": numbers.md gives the post-hoc value for every cell | §Compare #7, §Verdict 7 ("the run write-up's prose") |
| 14 | OVERCLAIM | `dpo` "almost never succeeds" by re-thinking: 8 of 17 P successes | Corrections 4 |
| 15 | OVERCLAIM | olmo-ifomega's review re-read 78 / 115 of the reach `rl` trace labels, not all | verified (`rvt_phase2_checks.py` [12]); Corrections 5 |
| 16 | OVERCLAIM | share test also off at R_dpo B4096 (10.0 vs 14) | Corrections 6 |
| 17 | UNTRACEABLE | hashes / times / template sha / resume line not in `out/`; F meta has no template field | `rvt_facts.py` → `out/facts.txt`; Corrections 7 |
| 18 | MINOR | #10 sources "(run; numbers; STATUS)" | now "(run; log; STATUS)" |
| 19 | MINOR | "my value" column gave executor-label values unlabelled | both values given (#10, #11) |
| 20 | MINOR | compute gap: +525 s gives 2.50 h; 77 s overhead; 16.7 % | §Compare #19, §Verdict 6 |
| 21 | MINOR | F input tokens "–" though compute.txt had a (wrong) number | formula fixed: 1,210,335 = executor's 1.21 M; Corrections 8 |
| 22 | MINOR | credential scans differ (613 vs 629 objects; 0 vs 1 hit) | §Compare #21 "consistent in substance" |
| 23 | MINOR | calibration genuine also rests on identity inheritance from the 75 source labels | Corrections 9 |
| 24 | MINOR | F4096 is not a reach-41 condition; B2048 moves 0.022 between exec labels and mine + rule 1 | §Verdict wording ("6-prompt fresh-forcing F4096 rate is not") |
| 25 | MINOR | the alliteration item is a judgement call under my rule 2 / pre-registered rule 3 | Corrections 10 |
