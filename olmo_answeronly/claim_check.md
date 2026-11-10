# olmo-answeronly claim check (adversarial; 2026-11-10)

Verdicts: 6 WRONG, 15 IMPRECISE, 2 OVERSTATED, 32 OK (55 items).

Files: RUN = `run_olmo_answeronly.md`; PLAIN = `olmo_answeronly/plain_summary.md`; NUM = `numbers.md` § "## olmo-answeronly". Full-precision values were recomputed from `olmo_answeronly/results.csv` (genuine = genuine_est / n; T1 / T2 = `olmo_transplant/results.csv` genuine_est / n), with `analyze.py`'s bootstrap (10,000, `random.Random(1)`). They reproduce every 4-dp value in `summary.json`. `summary.json` stores 4-dp values and `numbers_section` formats them to 3 dp, so some 3-dp numbers are double-rounded (items 2–5). `mechanism.py` was re-run to a temp file and its output matches `mechanism.md` byte for byte. "Cell" means (prompt, writer, condition) unless stated.

## Rounding and table values

1. RUN table, A3 row: "R 0.34 [0.25, 0.43]". Source: R_A3 = 0.33640 [0.24469, 0.43298] (summary.json 0.3364 [0.2447, 0.433]). The lower end rounds to 0.24, not 0.25. **WRONG.** Fix: "0.34 [0.24, 0.43]".
2. NUM conditions table, s2300 A1 genuine "0.926 [0.882, 0.965]". Source: 0.926515 [0.88207, 0.96540], so the point estimate rounds to 0.927. The 0.926 comes from double rounding 0.9265 at 3 dp. **WRONG.** Fix: 0.927 [0.882, 0.965]. RUN's 0.93 is fine.
3. NUM conditions table, L1 genuine "0.684 [0.582, 0.782]". Source: 0.68445 [0.58155, 0.78252]. The upper end is 0.783. **WRONG.** Fix: [0.582, 0.783]. The re-opened = fail column repeats the same values and needs the same fix.
4. NUM conditions table, L3 genuine "0.773 [0.687, 0.852]". Source: 0.77320 [0.68690, 0.85147]. The upper end is 0.851. **WRONG.** Fix: [0.687, 0.851], also in the re-opened = fail column.
5. NUM paired differences, "s2300:A1-T2: 0.003 [-0.038, 0.044]". Source: 0.002480 [-0.03787, 0.04441]. The mean is 0.002. **WRONG.** Fix: 0.002.
6. RUN main table, all other cells: dpo T1 0.14 [0.08, 0.21] (0.1392 [0.0780, 0.2114]); A1 0.63 [0.53, 0.72] (0.6261 [0.5321, 0.7163]); A2 0.32 [0.22, 0.43]; A3 0.31 [0.23, 0.40] (0.3120 [0.2264, 0.4036]); A4 0.22 [0.15, 0.31]. s2300 0.92 / 0.93 / 0.92 / 0.95 / 0.94. R_T 0.16 [0.09, 0.24], R_A1 0.68 [0.58, 0.78], R_A2 0.37 [0.26, 0.49], R_A4 0.25 [0.17, 0.34]. All match summary.json. **OK.**
7. NUM conditions table, every other strict and genuine interval (checked at full precision, including the boundary cases 0.3155→0.316, s2300 A3 lower end 0.91048→0.910, s2300 A4 lower end 0.90549→0.905, L1 0.68445→0.684). Re-opened, cut, exact and near shares, median words and generated tokens all match summary.json and results.csv. **OK.**
8. NUM R table: every R, CI, S_c mean and "s2300 < 0.75" count matches. Examples: R_T strict lower end 0.08948→0.089; R_L1 strict 0.75446→0.754 [0.65844→0.658, 0.844]; R_L2 strict lower end 0.16455→0.165. **OK.**
9. NUM R table, "R, strict" column. Its S set is defined on s2300's strict rate and differs from the S_c column: 38 prompts for T, A1, A3, A4 and L1, 37 for A2, 24 for L2 (summary.json `R_strict_rate[3]`). The table only shows the genuine S_c. **IMPRECISE.** Fix: add "(S = 38 / 38 / 37 / 38 / 38 / 38 / 24)" or a footnote.
10. NUM sensitivity: "R_A1 = 0.669, R_A2 = 0.342, R_A3 = 0.320, R_A4 = 0.236, R_T = 0.139". Recomputed with ifbench_133 and 136 dropped: 0.66857, 0.34224, 0.32014, 0.23633, 0.13924. **OK.** RUN's "without both prompts R_A1 = 0.67" is also OK.
11. NUM paired differences, the other seven means, CIs and SDs. Examples: dpo:A2-T1 upper end 0.24949→0.249; s2300:A4-T2 SD 0.09853→0.099. **OK.**
12. NUM family table: every value matches. Ties such as 0.0625 and 0.2375 were printed rounded-half-even, which is acceptable. **OK.**
13. NUM A4 stop shares: dpo 0.0978 / 0.3022 / 0.6000; s2300 0.7109 / 0.0239 / 0.2652. **OK.**
14. NUM calibration table and choice: dpo strict A1 0.996875, A3 0.98125, A2 0.946875. A1 and A3 are 0.015625 apart (tie ≤ 0.03); copy shares are 0.1493 / 0.1007 / 0.0625; s2300 < 0.75 on 0 of 10 for each. A1 is chosen, and would also be chosen on strict alone. The "0.062" is exactly 0.0625. **OK.**
15. NUM mechanism table: matches a fresh `mechanism.py` run exactly. Genuine-0 prompts dpo A1 2, T1 20 (results.csv). **OK.**
16. NUM compute: the registry sums to 12,440 attempts, 2,068,854 generated tokens and 4,029.4 GPU-s (1.119 h → 1.12). `podbudget olmo-answeronly`: 1.29 h, $9.27 of $30. **OK.**
17. NUM: "dpo generates 1.5–4.5× s2300's tokens in each condition". Reach ratios: A1 1.53, A2 1.99, A3 3.33, A4 4.53, but T1 / T2 is 4.58. Calibration ratios: A1 1.44, A2 1.40, A3 2.05, A4 1.56, T 1.35. The 1.5–4.5 range only covers the reach A conditions. **IMPRECISE.** Fix: "1.5–4.5× on reach A1–A4 (T1 / T2: 4.6×; calibration 1.35–2.05×)".
18. NUM hand gate: "478 reads, 441 genuine / 37 gamed". handcheck.csv has 478 items (distinct answers), 441 final genuine and 37 final gamed. The items carry 613 individual reader labels (365 items read once, 91 twice, 22 three times). Every gamed item had ≥ 2 readers, and 2 labels were adjudicated. **IMPRECISE** ("reads" suggests reader labels). Fix: "478 items read (613 reader labels)".

## Derived claims and wording, RUN

19. RUN finding 1: "One instruction closes about 60 % of the gap". On genuine rates, (0.6261 − 0.1392) / (0.9240 − 0.1392) = 0.620. Against A1's own s2300 rate, 1 − (0.9265 − 0.6261) / 0.7848 = 0.617. On the R scale, (0.683 − 0.159) / (1 − 0.159) = 0.623. **OK.**
20. RUN finding 1: "+0.49 [0.41, 0.57] per prompt". Source: 0.4869 [0.4063, 0.5678]. **OK.**
21. RUN finding 1: "copies the trace's answer exactly in 35 % of answers (T1: 5 %)". Source: dpo A1 exact 0.3543, T1 0.0467. **OK.**
22. RUN finding 1: "0 on 2 prompts (T1: 20)". The source is the number of prompts with **genuine rate** 0 (dpo A1 2, T1 20; mechanism.md, results.csv). Placed after the copy claim, it reads as an exact-copy count; the prompts with no exact copy are 11 (A1) and 32 (T1). **IMPRECISE.** Fix: "genuine rate 0 on 2 prompts (T1: 20)".
23. RUN finding 1: "Pre-registered reading: between (0.40 < R < 0.75)". R_A1 = 0.6830 and summary.json gives reading "between". **OK.**
24. RUN finding 2: "R 0.25–0.37, and none breaks s2300". R_A4 0.2526, R_A2 0.3734; at most 6 of 41 prompts fall below 0.75 (the rule is > 20). **OK.**
25. RUN finding 2: "dpo runs past the draft or diverges from it in 90 % of answers, so reading 4 … fails". 0.3022 + 0.6000 = 0.902 is right. But reading 4 is defined on R and fails because R_A4 = 0.253 < 0.75 and R_A1 = 0.683 > 0.40, not because of the stop shares. **IMPRECISE.** Fix: "reading 4 fails (R_A4 0.25 < 0.75); consistent with that, dpo runs past … in 90 %".
26. RUN finding 3: "0.68 (R 0.75 [0.65, 0.84], on the threshold); … 0.18 (lora_main itself 0.77)". Source: L1 0.6845, R_L1 0.7523 [0.6534, 0.8430], L2 0.1798, L3 0.7732; L2 and L3 are on 35 prompts. **OK.**
27. RUN and NUM omit the second clause of pre-registered reading 6, "L2 ≥ T1 + 0.13 → lora_main's thinking is easier for dpo". L2 is 0.180, against T1 0.139 + 0.13 = 0.269 on reach-41, or T1 0.160 + 0.13 = 0.290 on L2's 35 prompts, so the clause is not met. This reading is pre-registered but not reported. **IMPRECISE.** Fix: add "L2 0.18 < T1 + 0.13 (0.29 on the same 35 prompts): not easier".
28. RUN answer: "two-thirds as often as RL does, and about 40 % of the gap survives". 0.6261 / 0.9265 = 0.676, R 0.683, and 38 % of the gap survives (37.7 % on the R scale). **OK.**
29. RUN against expectations: "dpo A1 was above its range (0.63 vs 0.15–0.60)". 0.6261 > 0.60. **OK.**
30. RUN against expectations: "R_A1 0.68 (expected 0.40)". The pre-registered range for R_c* is 0.20–0.70, and 0.683 is **inside** it. Listed among the misses next to "All else fell inside its range", it reads as a miss. **IMPRECISE.** Fix: "R_A1 0.68 (expected 0.40; inside 0.20–0.70, near its top)".
31. RUN against expectations: "dpo's A4 exact stop share was 0.098 (range 0.10–0.50)". 0.09783 < 0.10 is a miss, correctly scored. s2300's 0.711 is inside 0.45–0.85. **OK.**
32. RUN against expectations: "Answers cut at the budget: ≤ 0.33 % per condition, but 2 / 24 and 1 / 24 in two dpo (prompt, condition) cells." results.csv has **three** reach dpo cells with cuts: A4 ifbench_79 2/24 (8.3 %), A4 ifbench_207 1/16 (6.25 %) and A3 ifbench_268 1/24 (4.2 %). There is also calibration s2300 A4 ifbench_52 1/32 (3.1 %), a cell of this run, and calibration s2300 A4 at 1/288 = 0.35 % per condition exceeds "≤ 0.33 %". The prereg's "< 1 % in every cell" is also left unscored (held per condition, missed in 4 cells of this run). **WRONG.** Fix: "≤ 0.33 % per reach condition (≤ 0.35 % incl. calibration): held per condition; missed in 4 cells: dpo A4 2/24 and 1/16, dpo A3 1/24, calibration s2300 A4 1/32".
33. RUN against expectations: "All else fell inside its range", for the re-opened expectation "< 5 % (dpo), < 2 % (s2300), every A cell". It holds per condition (dpo at most 0.54 %, s2300 0). Per (prompt, condition) cell, the reading RUN applies to cuts, it misses in dpo A3 ifbench_248 (4/24 = 16.7 %) and dpo A2 ifbench_271 (1/16 = 6.25 %). **IMPRECISE.** Fix: state the per-condition reading explicitly, or list the two cells.
34. RUN against expectations, the remaining expectations: dpo A2 0.324, A3 0.312 and A4 0.223 are inside their ranges. s2300 A1 0.927, A2 0.918, A3 0.951 and A4 0.944 are inside theirs. No condition is broken. dpo A1 exact + near 0.3946 is in 0.10–0.50. Calibration dpo strict is ≥ 0.9469 in every A condition. L1 0.684, L2 0.180 and L3 0.773 are in range. **OK.**
35. RUN deviations: "A4 prefills min(5, n − 1) tokens on 5 short answers". The pre-registration already specifies kp = min(5, n − 1) and the 5 traces (A4 row of the conditions table), so this is not a deviation. **IMPRECISE.** Fix: drop it, or call it "as pre-registered".
36. RUN deviations: "Added L3 as L2's control". L3 is in the pre-registration's optional-arm table ("L3 (added; cut first)"); it was added relative to the brief, not to the prereg. **IMPRECISE.** Fix: "L3 (added in the prereg relative to the brief)".
37. RUN deviations omit the pod. The prereg planned "one 1 × H200 community pod ($3.59/h)". The run used a 2 × H200 pod at $7.18/h with GPU 1 broken (ECC), as stated in NUM, which doubled the hourly cost. **IMPRECISE (omission).** Fix: add it to Deviations.
38. RUN deviations: "One reading was fixed mid-gate (inline sub-bullets, 133 / 136; 2 labels overturned; without both prompts R_A1 = 0.67)". handcheck_rules.md and handcheck.csv show 2 adjudicated items that overturn 2-1 gamed majorities; R_A1 without the two prompts is 0.6686. **OK.** The sensitivity drops the prompts rather than flipping the labels, and NUM says so.
39. RUN setup: "115 stored genuine s2300 traces (41 IFBench reach prompts) … 8 per trace … $9.27 of $30". Matches the prereg, results.csv (920 = 115 × 8) and podbudget. **OK.**

## PLAIN

40. "14 % genuine successes, against 92 %". T1 0.1392, T2 0.9240. **OK.**
41. "the RL model succeeds and the pre-RL model essentially never does". `olmo_transplant/prompts.csv` reach-41: dpo_fixed_strict 0 / 656, s2300 198 / 328 (0.60). **OK.**
42. "An automatic checker graded 9,664 answers". 9,664 is only the required design. This run sampled and graded 12,440 answers: 9,664 plus 2,776 in the LoRA arm (registry `verifier_checks` 12,440). T1 / T2 are inherited. **IMPRECISE.** Fix: "12,440 new answers".
43. "rose from 14 % to 63 %; the RL model stayed at 93 %". dpo A1 0.6261; s2300 T2 0.924 → A1 0.927. **OK.**
44. "Most of the gap was a writing habit that one sentence removes." The pre-registered reading is **between**, not habit (R 0.683 < 0.75). The data show that one instruction closes about 62 % of the gap; calling that part "a writing habit" is the interpretation the experiment tests, not a measurement. **OVERSTATED.** Fix: "One sentence closed most (about 60 %) of the gap".
45. "About 40 % of the gap remains". 38 %. **OK.**
46. "It still sometimes rewrites the answer its own way". Under A1, 64.6 % of dpo answers are not exact copies (exact 0.354, near 0.040), and 501 of 920 do not contain the trace's answer verbatim (mechanism.md: 419 do). "Sometimes" understates this. **IMPRECISE.** Fix: "about two-thirds of its answers are not exact copies of the draft".
47. "does worst on sentence-length rules". The absolute claim is true: dpo A1 is lowest on the sentence family, 0.481 (n = 5; 4 of 5 are `sentence:increment`). But s2300 is also lowest there (0.783). Relative to s2300, words is worst (0.579 / 0.974 = 0.594 vs sentence 0.614), and the largest absolute gap is words (0.396 vs 0.302). The family split is descriptive, with n = 5. **IMPRECISE.** Fix: "its lowest rate is on sentence-length rules (5 prompts), where the RL model also does worst".
48. "The other three changes help much less (22–32 %)". These are dpo's rates (A4 0.223, A3 0.312, A2 0.324); the gains over 14 % are +0.08 to +0.18. "Help … (22–32 %)" reads as the gain. **IMPRECISE.** Fix: "reach only 22–32 % (from 14 %)".
49. "Starting the answer for it barely helps; it usually writes on past the drafted answer or departs from it". dpo A4 − T1 = +0.084 [0.040, 0.132]: above zero, below the 0.13 MDE. Runs past or diverges: 0.902. **OK.**
50. "three-quarters as well as the RL model does (68 %), with no instruction". R_L1 0.752; L1 0.684 against T2 0.924 (0.74). L1 is the plain transplant. **OK.**
51. "again mostly fails (18 %)". L2 0.180, on 35 prompts. **OK.**
52. "Given good thinking, the pre-RL model mostly lacks output discipline. Part of what RL taught is to stop and give the drafted answer." This is a causal claim about what RL training taught. The run shows that s2300 copies the draft exactly far more often (T2 0.664 vs T1 0.047) and that an instruction recovers about 62 % of the gap. It does not isolate what RL changed: no RL-intermediate checkpoints, and the instruction may act on more than stopping. **OVERSTATED.** Fix: "consistent with RL having taught it to stop and give the drafted answer".
53. "still succeeds only about two-thirds as often as the RL model". 0.676 (R 0.683). **OK.**
54. "Cost $9.27." podbudget gives $9.27. **OK.**

## Not present

55. The task named "one-sixth"; it does not occur in any of the three texts. **OK** (nothing to check).

## Resolution (2026-11-10 02:11 UTC, executor)

- 1–5 (rounding): root cause was double rounding (summary.json kept 4 dp). `analyze.py` now keeps 6 dp and numbers.md's
  section was regenerated by `numbers_section.py`; RUN's A3 R lower end → 0.24.
- 9, 17, 18, 27: fixed in the generator (strict S per row, token ratios with T and calibration, "478 items read, 613
  reader labels", reading 6's L2 clause reported: not met).
- 22, 25, 30, 35–37: RUN reworded as suggested; the pod deviation added; A4 prefill rule and L3 removed from deviations.
- 32–33: the per-cell misses are now listed in numbers.md and summarised in RUN. My own recount found one more re-opened
  miss the check did not list (dpo A3 ifbench_207, 1 / 16).
- 42, 44, 46–48, 52 (PLAIN): reworded; "habit" claims replaced by what was measured (60 % of the gap closed; RL copies its
  draft far more often); RUN's "Answer" now states the pre-registered reading (between).
