# Second-pass claim check: revised `rl_compute_share/REVIEW.md` (run rl-compute-share, executor agent:claude)

Adversarial second pass, 2026-10-19, on commit c00ec2e9. Targets: `REVIEW.md`, `run_rl_compute_share.md` ("run file"),
`numbers.md` § rl-compute-share, `compute_table.csv`, `analysis_out.txt`, `frontier_ranges.csv`, `figures/ratio.png`,
`notes/yue2025-rl-compute.md` and `notes/frontier-rl-compute-sources.md`.

- **Line numbers.** `L##` are lines of the revised REVIEW.md unless another file is named. "line N" of `compute_table.csv`
  counts the header as line 1. A ProRL v2 row was inserted at line 19, so the first checker's rows 19 and later are now
  one line lower (its row 38, Interplay, is line 39).
- **What I re-ran (read-only).** `verify_ledger.py` gives 1,206 / 1,206. `check_quotes.py` gives 124 / 124. A fabricated
  quotation piped in on stdin is NOT FOUND, while a genuine one passes. The script skips quotations under 20 characters.
  The short ones in REVIEW.md ("emerge late", "at pretraining scale", "small for all players", "$1M instead of $0.1M",
  "RL fails to transfer") were grepped and found in the ledger.
- **Claim ids.** All 46 bracketed ids in REVIEW.md exist in `ledger/*.tsv`. The new ones were read against their quotes.
- **What I recomputed.** The verdict groups and medians from `compute_table.csv`, and the ProRL v2 bracket from line 19's
  inputs (4.35 × 10⁻³ – 2.12 × 10⁻²). Also the samples-per-problem median, the order-of-magnitude gaps under both unit
  readings, and the R1-Zero GPU-hour / FLOP gap under the ¼ rule. Our-runs bases come from `our_runs_table.md`.
- **Figure.** `figures/ratio.png` was viewed.

## Part 1. The first checker's 51 non-OK findings

| # | status | evidence |
|---|---|---|
| 1 | FIXED | BL4 L50–54 now reads "scale evidence within studies is mixed" and lists ProRL, Interplay and rl-continue as growing. Q4 L158–167 adds Abdulsalam and knockout s1. "Allocation matters" (L184–186) keeps only f(g(x)) and GRPO-N. The run file (L13) also says "mixed". |
| 2 | FIXED | BL4 L53–54 and Implication 1 L238 name Interplay (≈ 0.4×) and our knockout. L179–180 cites Y-inter-exposure and C-INTER-budget_row_4p2. The 204.8k samples are confirmed at 2512.07783v1 L1292 (§4 recipe) and L1396 (4.20B row). |
| 3 | FIXED | Interplay moved to "Skills removed from pretraining, at frontier-share RL" (L178–180). The tiny-RL list no longer uses C-INTER-seeds. |
| 4 | FIXED | BroRL is gone from Q4. It appears only as "no test" (L102) and "BroRL untested" (L253), and line 20's verdict is now `none`. |
| 5 | FIXED | L186 cites C-DEBATE-aime25_base and _grpon. 46.7 % and 66.7 % of 30 are 14 and 20, at k 256 (last column of Table 1), and Q2 keeps "mixed". The allocation contrast is still uncited: part 2, row I. |
| 6 | FIX INTRODUCED A NEW ERROR | BL2 L42–43 is right: "on a pretrained LLM", ≈ 2 × 10⁻², ProRL v2 line 19 = 4.35 × 10⁻³ – 2.12 × 10⁻² (recomputed). But the restatements in Verdict L225 and run file L6–7 drop the scope: "no tested model with a computable ratio exceeds ≈ 2 × 10⁻²". Interplay (0.105–2, line 39, a test the Qualification itself cites) and our runs contradict this. |
| 7 | FIXED | Line 16's verdict is now `none`. Elicit n = 16, median 8.72 × 10⁻⁵, and the ratio is 11.8× (`analysis_out.txt` L11–15). "Barely differ" is gone, and L251 reads "11.8× held (n = 3)". |
| 8 | FIXED | BL3 L49, Q3 L150 and Q4 L194 say 2.5–15× (5–8× at the midpoints), and our runs are no longer cited as support. numbers.md L1996 gives R1-Zero 2.5–12× and Olmo 3 3.7–15× (recomputed). |
| 9 | FIXED | BL3 L46–47: "No frontier lab publishes an RL / pretraining FLOP ratio", with xAI and V3.2 named as the closest statements. |
| 10 | FIXED | Run file L8: "No lab publishes a FLOP ratio". Cursor states compute and V3.2 states cost; neither is a FLOP ratio. |
| 11 | PARTLY | BL1 L39–41 now gives both readings: 3.4–4.2 orders and ≈ 2.5–3.5 (recomputed 3.41–4.24 and 2.51–3.54). Q3 L146–147 converts 2026 to ≈ 0.1–0.4. But BL3 L49, run file L9 and the figure label every period "mostly GPU-time", whereas 2024–H2 2025 rest on Epoch's compute estimates: part 2, rows C, D, F. |
| 12 | FIXED | BL1 L37–38, run file L6, Yue note L34–35, Q1 L71 and numbers.md L1966–1967 give 3 × 10⁻³ and flag DAPO's rollout-step 3 × 10⁻². The figure still draws DAPO to 3.03 × 10⁻² (part 3). |
| 13 | FIXED | BL5 L55: "0.9–19× (RL share only; up to 39× as run)". `our_runs_table.md` gives RL-only LLM-equivalent 0.895–19.1 and an as-run maximum of 38.6. |
| 14 | PARTLY | Implication 1 L237 now reads "0.9–19× (1–10× for ladders started from full pretraining)", and BL5 says "at or above". But "1–10×" mixes bases. RL-only for full-pretraining ladders is 0.895–5.11. The 9.74 is knockout s1 as run. Part 2, row E. |
| 15 | PARTLY | The Q4 scale item is gone, and line 41's `verdict_how` now names the off-policy-distilled Qwen3-8B checkpoint. But line 41 still names the 235B-A22B RL as the model, with verdict `elicit`, and BL2 L43 lists "Qwen3" among the tested models. |
| 16 | FIXED | L166–167: "free reductios went from 11 to 123 per round, and held-out members from 2 to 5". This matches numbers.md L1925–1928 (r16 2, r20 5, r24 5). BL5's "grew slowly" is removed. |
| 17 | FIXED | Verdict L222–232 separates the two questions. "Supported" covers the small-RL gap (Yue concedes). The qualification covers the mixed scale evidence and the two frontier-share tests that need exposure. Fairness: part 4. |
| 18 | PARTLY | REVIEW L110–111 splits +42 % [C-INTER-plus42] from +60 % [Y-inter-plus60], and the ledger value of C-INTER-plus42 is corrected. But `compute_table.csv` line 39 still says edge-of-competence RL "lifts OOD pass@128 by up to +42 % / +60 %". |
| 19 | FIXED | L197–198: "1.5–2,400 times (2 × 10⁶ for one-shot RLVR; median ≈ 100) … k = 32–16,384". Recomputed: minimum 1.54, maximum 2,410, median of the 25 midpoints 102. |
| 20 | FIXED | L159–160 puts boxnet under "Reach grows": "stays ahead at k 16,384 (0.492 against 0.345), though the base is not at zero". |
| 21 | FIXED | L172: "(1T parameters; tracked to step 2,000; ratio unknown)". |
| 22 | FIXED | Q3 L128 reads "R1-Zero's RL ≈ 6.1 × 10²³ FLOP" and L152 "(≈ $1M at pretraining MFU)". Both match D-epoch-r1-rlflop. |
| 23 | FIXED | L170: "at k 1,024–16,384" (C-LEASH-kmax). "Longest" is dropped. |
| 24 | PARTLY | Method L27–28 states the ⅛ exception. It does not say that this departs from the pre-registered ¼ rule, nor give its effect. With ¼, R1-Zero's FLOP low is ≈ 6.0 × 10⁻³ and its midpoint GPU-h / FLOP gap is 3.9× (not 5.5×), so "5–8× at the midpoints" (BL3 L49) becomes ≈ 4–8×. |
| 25 | FIXED | Re-run: `check_quotes.py` gives 124 / 124, matching run file L17 and numbers.md L2026. REVIEW L20 says "every quotation". |
| 26 | FIXED | L19–21 now say "Every source figure has a verbatim quote" and "A 41-row spot check matched values to quotes". The ledger values of C-INTER-plus42 and C-PRORL-sustained are corrected. |
| 27 | FIXED | Run file L15: "None … held outright: 6 held in part and 1 did not". This matches REVIEW L258. Scoring: part 4. |
| 28 | FIXED | L251: "**falsified** by Interplay (low 0.105)". |
| 29 | FIXED | L250: "median 2.0 × 10⁻⁴ (third-party 1.1 × 10⁻³)" (`analysis_out.txt` L2, L5). |
| 30 | FIXED | L253: "held (literature only)". |
| 31 | FIXED | L64–65: "ten outside checkpoints (nine computable) and trains nine runs: six algorithms, two ablations and EasyR1". |
| 32 | FIXED | L209: "six runs' registries". |
| 33 | FIXED | L206–207 names K12, cap 6, K12⁻ and the 1 % dose set, and gives rl-from-ckpt D = 2.9 × 10⁷ – 2.9 × 10⁸ (table: 29.4–294 M). L219: "20,000 records of the arm's own pretraining set". |
| 34 | FIXED | BL2 L44–45 adds MiniMax-M1, Olmo 3.1, V3.2 and Beam as larger shares without a test. |
| 35 | FIXED | L199: "mappable onto lab statements to within 2.5–15×". |
| 36 | FIXED | L164–165: "16 of the 22 new solves came on one seed". The nd-rl summary L107 gives s1 1 → 17. |
| 37 | FIXED | L176: "Leash's own 300-step run (R1-Distill-1.5B, k 256)". C-LEASH-ckpt_5of6 and C-LEASH-ckpt_design back it. |
| 38 | FIXED | L59 reads "(Yue et al. agree)" and L227 "Yue et al. call frontier scale open". |
| 39 | FIXED | L102: "ORZ-32B 3 × 10⁻³ – 1.6 × 10⁻²; R1-Zero 3 × 10⁻³ – 1.5 × 10⁻²". |
| 40 | FIXED | REVIEW L150, the 2024 note in `frontier_ranges.csv` and frontier note L70 all give 3.6–3.8 %, with both denominators. |
| 41 | FIXED | L70: "(FLOPs from GPU-hours, MFU 3–30 %)". |
| 42 | FIXED | L89: "Magistral-Medium, which they evaluate". |
| 43 | FIXED | L81–82: "Five checkpoints report 216–13,440 GPU-hours". |
| 44 | FIXED | L15–16: "13 in-depth notes … 12 sources read in full … one note on 12 frontier posts". This matches `screened.md` L3. |
| 45 | FIXED | The figure legend now has "arrow: lower bound (any marker)" (viewed). |
| 46 | FIXED | L159 cites C-PRORL-sustained and C-PRORL-boxnet, and the unsupported "pass@128" is gone. |
| 47 | FIXED | L175 cites Y-yue-verl-step150 (66.3) and Y-yue-verl-step450 (64.3). |
| 48 | FIXED | L131 cites D-epoch-gpt5notes-early25 and D-epoch-gpt5notes-range. |
| 49 | FIXED | L135 cites D-oc-sa-posttrain and D-oc-sa-pretrain. |
| 50 | FIXED | The lab table defers to `compute_table.csv`. Its Olmo 3.1 row (line 28) lists B-OL31-32b-rl-days, B-OL3-32b-rl-days and B-OL3-32b-pretrain-days. |
| 51 | FIXED | L107–108 cite C-INTER-budget_row_1 (1.05B), C-INTER-budget_row_20 (20.00B) and C-INTER-pretrain_tokens (10B). |

**Tally:**

| status | count | items |
|---|---|---|
| FIXED | 45 | all others |
| PARTLY | 5 | 11, 14, 15, 18, 24 |
| FIX INTRODUCED A NEW ERROR | 1 | 6 |
| NOT FIXED | 0 | none |

## Part 2. New or changed statements in the revised REVIEW.md

| id | location | claim | evidence | verdict | suggested fix |
|---|---|---|---|---|---|
| A | Verdict L225; run file L6–7 | "no tested model with a computable ratio exceeds ≈ 2 × 10⁻²" | **Counter-examples:** Interplay is tested and computable at 0.105–2 (line 39, verdict mixed), and the Qualification (L231) cites it as a frontier-share test. Our runs (0.9–19) are also tested and computable. **Correct version:** BL2 L42 has the right scope, "on a pretrained LLM" | WRONG | "no create-vs-elicit test on a pretrained LLM with a computable ratio exceeds ≈ 2 × 10⁻²" |
| B | Verdict paragraph L58 | "The papers test RL 2.5–4 orders of magnitude below the frontier share" | **Holds for Yue's median:** 3.41–4.24 orders in stated units and 2.51–3.54 in the GPU-time reading (recomputed). **Fails for the largest tested runs.** ProRL v2 (midpoint 9.6 × 10⁻³) is 1.5–2.3 orders below 0.3–2, and 0.6–1.6 below its GPU-time version (≈ 0.04–0.4). AceReason-7B (midpoint 3.8 × 10⁻³) is 1.0–2.7 below. The create and mixed medians are 1.1–3.3 below | OVERCLAIM | "Yue's runs sit 2.5–4 orders below the frontier share; the largest tested open runs sit ≈ 0.6–2.3 orders below" |
| C | BL3 L49; run file L9; figure label; numbers.md L1999 ("mostly GPU-time or unspecified") | "These are mostly GPU-time units; FLOPs are 2.5–15× lower", said of all three graded centrals | **2024–H2 2025 rest on Epoch compute estimates:** D-epoch-oai24-oseries ("1% … 30% of base model compute"), D-epoch-gpt5notes-early25 ("RL compute was small—maybe 1-10% of pre-training"), D-epoch-gpt5notes-range ("… 5e25 FLOP") and D-epochdb-grok4-rl ("RL relative to pre-compute"), plus xAI's unit-free words. **Only 2026** rests mainly on GPU-time and fleet shares. Q3 L146–147 says this itself ("H2 2025 rests partly on Epoch's FLOP estimates") | OVERCLAIM | "2024–H2 2025 rest on Epoch's compute estimates and unit-free statements; 2026 rests mostly on GPU-time and fleet shares (≈ 0.1–0.4 as FLOPs)" |
| D | Verdict L226 | "The frontier has been ≥ 0.1 since H2 2025 (D; ≥ 0.02 in FLOPs)" | **No conversion needed:** the H2 2025 floor of 0.1 comes from Epoch's compute estimates (Grok 4 and GPT-5 ≥ 10 % of pretraining). **If converted anyway:** the review's own 2.5–15× gives 0.007–0.04; "≥ 0.02" is ÷5 only. **Unstated consequence:** at 0.007–0.02 the floor reaches the largest tested ratios (≈ 2 × 10⁻²), and the "Supported" bullet does not say so | UNCLEAR | "≥ 0.1 since H2 2025 (D; Epoch's compute estimates; ≈ 0.01–0.04 if read as GPU-time, i.e. at the largest tested runs' high bounds)" |
| E | Implication 1, L237 | "Our RL is 0.9–19× pretraining FLOPs (1–10× for ladders started from full pretraining)" | **Outer range:** 0.9–19 is RL-only LLM-equivalent (0.895–19.1). **Parenthetical:** for full-pretraining ladders, RL-only is 0.895–5.11. The 9.74 is knockout s1 as run (`our_runs_table.md`). The sentence switches basis mid-way | UNCLEAR | "(0.9–5× RL-only, up to 10× as run, for ladders started from full pretraining)" |
| F | Q3 L146 | "That is 1–2 orders of magnitude in two years." | This compares 2024's compute-based central (0.01–0.1) with 2026's GPU-time-based central (1–2). The next sentence converts 2026 to ≈ 0.1–0.4 in FLOPs; on that basis the rise is ≈ 0.1–1.6 orders | UNCLEAR | "1–2 orders in stated units; ≈ 0.1–1.6 if 2026's GPU-time statements are converted" |
| G | BL2 L42 | "No create-vs-elicit test on a pretrained LLM with a computable ratio exceeds ≈ 2 × 10⁻² (ProRL v2, AceReason-7B)" | This holds only under DAPO-32B's gradient-step reading. `compute_table.csv` line 7, `analysis_out.txt` L2 and the figure keep DAPO's tested (elicit) high bound at 3.03 × 10⁻². BL1 explains the reading but BL2 does not | UNCLEAR | Add "(taking DAPO-32B's gradient-step reading; 3 × 10⁻² under the rollout-step reading)" |
| H | Q2 L110–111 | "new contexts gain +60 % with ≥ 1 % pretraining exposure [Y-inter-plus60]" | The quote reads "yielding up to +60% pass@128" | OVERCLAIM | "up to +60 %" |
| I | Q4 L184–186 | "Allocation matters even at tiny RL … GRPO-N takes AIME25 from 14 to 20 of 30 at k 256 [C-DEBATE-aime25_base, C-DEBATE-aime25_grpon]" | The numbers are right (46.7 → 66.7 % of 30). But the allocation contrast is GRPO-N against GRPO at the same steps. GRPO stays at 46.7, equal to the base (C-DEBATE-aime25_grpo), and that row is not cited | UNSUPPORTED | "GRPO-N reaches 20 of 30 at k 256, where GRPO stays at the base's 14 [C-DEBATE-aime25_grpo, C-DEBATE-aime25_grpon]" |
| J | Verification L22; run file L17 ("51 errors, all fixed"); numbers.md L2027–2028 | "An adversarial check found 51 problems in 131 statements, all fixed" | **This check:** 45 fixed, 5 partly, and 1 fix that introduced a new error (part 1). **"Errors":** 19 of the 51 were UNCLEAR, not errors | OVERCLAIM | "51 problems; 45 fixed, 6 partly or with a new error (`_claimcheck2.md`)" |
| K | Expectations L251 (#2) | The outcome cell scores four clauses | Pre-registered #2 also predicts R1's GPU-hours ≈ 5 % of V3's and a FLOP ratio of 3e-3 – 2e-2. That clause held (1.5–5.3 % of GPU-hours; R1-Zero 3.0 × 10⁻³ – 1.5 × 10⁻²) but is not scored. "In part" is unaffected | UNCLEAR | Add "R1 clause held" |
| L | Expectations L253 (#4) | "BroRL untested" is given for the ProRL / BroRL clause | The clause also predicts that ProRL's expansion shows only at k ≤ 256. Leash's re-test has ProRL ahead on boxnet at k 16,384 (C-LEASH-boxnet16384), which the review itself counts as growth (L159–160). "In part" is unaffected | UNCLEAR | "ProRL: boxnet lead persists to k 16,384 (k ≤ 256 falsified for boxnet); BroRL untested" |
| M | Expectations L255 (#6), tally L258 | "**not held**: supported, with a qualification" | "Supported, with a qualification" is not one of the three pre-registered labels. Its qualification is the pre-registered reason for "partly" (direct scale evidence weak). Only the third pre-registered reason, that the gap shrinks under trained tokens or gradient steps, failed. See part 4 | UNCLEAR | Say which pre-registered label the verdict maps to, or score #6 "in part" (tally 0 / 7 / 0) |
| — | Coverage L14–16 | 96 sources (52 arXiv, 44 web); 13 notes: 12 read in full plus one note on 12 frontier posts | `screened.md` L2–3 | OK | — |
| — | Verification L19–21 | 1,206 / 1,206; every quotation found; altered controls fail; 41-row spot check | Re-run: 1,206 / 1,206 and 124 / 124. The fabricated stdin control is NOT FOUND, and the short quotes are in the ledger | OK | — |
| — | Method L27–28 | R1-Zero's low bound uses ⅛ | `compute_table.csv` line 21 assumptions: "mean response low = 1/8 x 32,768" | OK | Effect on 5–8×: see #24 |
| — | BL1 L37–41 | 7 × 10⁻⁶ – 3 × 10⁻³; median 1.2 × 10⁻⁴; 3.4–4.2 orders; ≈ 2.5–3.5 if the units are GPU-time | Lines 2–16 (DAPO's caption reading ≤ 1.9 × 10⁻³; maximum is line 16 at 2.73 × 10⁻³). Median 1.155 × 10⁻⁴. Recomputed 3.41–4.24 and 2.51–3.54 (÷5–8; ÷2.5–15 gives 2.24–3.84) | OK | — |
| — | BL2 L43–45 | Magistral, Ring-Zero and Qwen3 not computable; larger shares only without a test (MiniMax-M1, Olmo 3.1, V3.2, Beam) | Lines 17, 40 and 41 are not computable, and the four listed rows are all `none`. Upper bounds are compared with an upper bound (ProRL v2 high 2.12 × 10⁻²). In FLOPs, Olmo 3.1 (0.9–5.7 × 10⁻²) and V3.2 exceed 2 × 10⁻² only at the upper end of the 2.5–15× conversion. MiniMax-M1's high bound is 5.2 × 10⁻², not ≤ 5 × 10⁻² (rounding) | OK | Optional: give the FLOP equivalents |
| — | BL3 L46–48 | No frontier lab publishes a FLOP ratio; xAI and V3.2 are closest; 0.01–0.1, 0.3–1, ≈ 1–2 | D-xai-grok4-ptscale, B-V32-ratio_stated-intro, `frontier_ranges.csv` | OK | Units: row C |
| — | BL4 L50–54 | Scale evidence is mixed; ProRL, Interplay and rl-continue grow; Interplay (≈ 0.4×) and our knockout (3–10×) need exposure | Q4 sources below. The knockout range runs from 3.07 (RL-only) to 9.74 (as run) | OK | — |
| — | BL5 L55–56 | 0.9–19× (RL share only; up to 39× as run); 9–180× by GPU-time | RL-only LLM-equivalent 0.895–19.1, as-run up to 38.6, GPU 8.93–182 (`our_runs_table.md`) | OK | — |
| — | Q1 L64–90 | Ten outside checkpoints (nine computable) and nine runs; Oat-Zero unit label; DAPO cell; five GPU-hour checkpoints; Magistral evaluated | Lines 2–17; A-DAPO-steps-unit; SimpleRL-Zoo 7B / 14B 240 h, 32B 2,304 h, Oat-Zero 216 h, DeepCoder 13,440 h | OK | — |
| — | Q2 L94–102 | 35 runs: 16 / 3 / 4 / 12; medians 8.7 × 10⁻⁵, 1.0 × 10⁻³, 2.9 × 10⁻³, 4.2 × 10⁻³; example ranges | Verdict column of lines 2–39, pretrained-LLM FLOP rows: 16 + 3 + 4 + 12 = 35. Medians from `analysis_out.txt` L11–14. The mixed median, the mean of NSR and ProRL v1, is 2.89 × 10⁻³. ProRL v2's bracket recomputes to 4.35 × 10⁻³ – 2.12 × 10⁻² and ProRL v2 + BroRL to 1.03 – 4.49 × 10⁻² | OK | — |
| — | Q2 L104–109 | Create 11.8× elicit (n = 3, ranges overlap); Interplay 0.1–2× of 10B tokens | 1.03 × 10⁻³ / 8.72 × 10⁻⁵ = 11.8. Budget rows 1.05B and 20.00B; C-INTER-pretrain_tokens "10B tokens" | OK | — |
| — | Q3 L128, L131, L132, L135 | Epoch R1-Zero; Epoch early-2025 and GPT-5 ranges; V3.2 quote; SemiAnalysis 42 % / 23 % | D-epoch-r1-rlflop; both Epoch ids are verbatim; B-V32-ratio_stated-intro "exceeding 10% of the pre-training cost"; both SemiAnalysis ids | OK | — |
| — | Q3 L146–147 | 2026, read as FLOPs, gives ≈ 0.1–0.4 | 1–2 ÷ 5–8 = 0.125–0.4; Beam 1.7 ÷ 5–8 = 0.21–0.34 | OK | — |
| — | Q3 L150–154 | 2.5–15×; R1-Zero 3.6–3.8 % vs 0.3–1.5 %; Beam trainer side ≥ 0.27–0.35; Epoch needs ≈ 490K H800-hours; 13–60× | 3.63 % / 1.46 % = 2.5 and Olmo 3 2.75 % / 0.18 % = 15.3. 101K / 2,783K and 101K / 2,664K. 6.1 × 10²³ / 1.23 × 10¹⁸ = 495K | OK | — |
| — | Q4 L158–167 | ProRL code and boxnet; boxnet 0.492 vs 0.345 at k 16,384; Interplay OOD-hard; Abdulsalam; group C 5 → 27 of 99, 16 of 22 on one seed; knockout s1 11 → 123, held-out 2 → 5 | C-PRORL-boxnet ("sustains and amplifies … across all values of k"), C-LEASH-boxnet16384, C-INTER-heavyrl, C-ABD-late. The nd-rl rl-continue-cap12 summary (path exists) L107: 3 + 1 + 1 → 6 + 17 + 4. numbers.md L1925–1928 | OK | — |
| — | Q4 L169–176 | Leash at k 1,024–16,384; Ring-Zero tracked to step 2,000; Yue 66.3 → 64.3; Leash's own run net negative on 5 of 6 | C-LEASH-kmax, C-RING-verdict, Y-yue-verl-step150 and step450. C-LEASH-ckpt_5of6 plus C-LEASH-ckpt_design (DAPO on R1-Distill-1.5B, pass@256, step 300) | OK | — |
| — | Q4 L178–182 | Interplay ≈ 0.42× (204.8k samples = 4.2B against 10B), "RL fails to transfer" at 0 % / 0.1 %; knockout 0 / 6 vs 6 / 6 | 2512.07783v1 L1292 (§4: 204.8k samples) and L1396 (4.20 ↔ 204.8); Y-inter-exposure verbatim; numbers.md L1858–1859 | OK | The 1 % dose result is exploratory (numbers.md L1892) |
| — | Q4 L193–199 | Samples per step 256–65,536; 1.5–2,400 samples per problem, median ≈ 100; k 32–16,384; within 2.5–15× | Recomputed (part 1, #19); B-OL3-rlzero-kmax gives k 32 | OK | — |
| — | Q5 L205–220 | Stage-1 sets, D for rl-from-ckpt, six runs, the four-row table, prefill ≈ 4.8×, ≈ 4–5 orders above Yue | `our_runs_table.md`: trajectory 1.49–2.89, rl-continue 3.26–6.32, p16000 2.17–4.29, p1600 17.8–38.6, create-or-elicit 3.07–9.74, GPU 32.5–53.9. log10(0.895 / 1.155 × 10⁻⁴) = 3.89 and log10(19.1 / 1.155 × 10⁻⁴) = 5.22 | OK | — |
| — | Verdict L229–232 | Qualification: both frontier-share tests are from-scratch organisms; RL extends reach near the edge yet needs exposure | C-INTER-verdict_edge, Y-inter-exposure, numbers.md knockout lines | OK | — |
| — | Implication 1, L238 | Our knockout is one of two controlled tests at frontier share and the only one above 1× | Interplay's exposure ablation runs at ≈ 0.42×; knockout 3.07–9.74 | OK | — |
| — | Expectations L250, L252, L254, L256 | #1, #3, #5 and #7 "partly", with their reasons | `analysis_out.txt` L2, L5, L7–8; `frontier_ranges.csv`; trajectory-cap6 GPU 8.93–9.36 < 10 | OK | — |

**Tally:** 13 non-OK and 22 OK.

| verdict | count | rows |
|---|---|---|
| WRONG | 1 | A |
| OVERCLAIM | 4 | B, C, H, J |
| UNSUPPORTED | 1 | I |
| UNCLEAR | 7 | D, E, F, G, K, L, M |
| OK | 22 | — |

## Part 3. Consistency across documents

- **Yue range.** The text agrees everywhere on 7 × 10⁻⁶ – 3 × 10⁻³, with 3 × 10⁻² flagged as DAPO's rollout-step reading:
  REVIEW BL1 and Q1, run file L6, numbers.md L1966–1967 and the Yue note L34–35. The figure and `analysis_out.txt` L2, L5
  still draw or print DAPO's high bound at 3.03 × 10⁻² as an ordinary elicit bar, with no mark for the disfavoured
  reading.
- **Largest tested ratio.** BL2 and numbers.md ("the largest tested ratio is ProRL v2, 4.4 × 10⁻³ – 2.1 × 10⁻²") are
  scoped correctly. Verdict L225 and run file L6–7 drop the scope (row A).
- **Units of the frontier band.** There are four descriptions:
  - BL3, run file L9 and the figure label: "mostly GPU-time".
  - numbers.md: "mostly GPU-time or unspecified".
  - REVIEW Q3 L146: "H2 2025 rests partly on Epoch's FLOP estimates".
  - The frontier note: "three currencies".
  The ledger supports Q3 (row C).
- **Ranges and medians.** The graded ranges are identical in REVIEW, numbers.md, `frontier_ranges.csv` and the figure.
  The median 1.2 × 10⁻⁴, the ratio 11.8× and the groups 16 / 3 / 4 / 12 agree across REVIEW, numbers.md and
  `analysis_out.txt`.
- **GPU-time / FLOP gap.** REVIEW gives 2.5–15× (5–8× at the midpoints), numbers.md 2.5–12× and 3.7–15× (5.5×, 7.6×),
  and the figure label 2.5–15×. These are consistent, with #24's ¼-rule caveat.
- **R1-Zero by GPU-hours.** REVIEW, `frontier_ranges.csv` and the frontier note give 3.6–3.8 %. `analysis_out.txt` uses
  3.63 %. The ScaleRL and DeepSeek-R1 notes quote ScaleRL's 3.75 % as ScaleRL's own figure, which is fine.
- **Our runs.** 0.9–19× RL-only, up to 39× as run and 9–180× GPU agree across REVIEW BL5 and Q5, the run file and
  numbers.md (0.90–19.1). Implication 1's "1–10×" uses the mixed basis (row E).
- **Check counts.** 1,206 and 124 agree across REVIEW, the run file and numbers.md, and were confirmed by re-run.
  `screened.md` L2 still says "1,014 of the 1,204 ledger rows". It should read 1,016 of 1,206, since both new
  Y-inter rows cite 2512.07783v1.
- **"51 … all fixed".** This appears in all three documents (row J). The run file calls them "51 errors".
- **Lab table.** numbers.md lists Cursor ("> 1, stated"). REVIEW's lab table (L114–120) does not, but REVIEW Q3 has Cursor
  as non-frontier. This is harmless.
- **Notes.**
  - The Yue note L40–41 gives "3–4 orders" below the band, which is the stated-unit reading only (REVIEW adds ≈ 2.5–3.5
    for GPU-time).
  - The frontier note L69 heads its bullet "Estimates disagree by about 5x" but now adds a FLOP count (0.3–1.5 %). Against
    that count Epoch's figure is 13–60× too high (REVIEW L153–154). The "about 5×" holds only for Epoch's FLOP share
    against DeepSeek's GPU-hour share.
- **`compute_table.csv`.**
  - Line 39 (Interplay) still conflates +42 % and +60 % (#18).
  - Line 41 still names the 235B-A22B RL (#15).
  - Line 19 (ProRL v2) carries arxiv 2505.24864v1, the v1 paper, though its inputs are the NVIDIA blog, BroRL Table 1
    and Leash.
  - The new Interplay claims are filed in `Y_yue.tsv` with a `Y-inter-` prefix. That is unusual but harmless.
- **Tally and verdict wording.** The tally 0 / 6 / 1 and the verdict wording agree between REVIEW (L58, L222, L258) and
  the run file (L12, L15–16).

## Part 4. Verdict assessment

**Verdict.** "Supported, with a qualification" is fair for the pre-registered question, which asks what small-RL
papers can rule out. Yue's median (1.2 × 10⁻⁴) is 2.5–4.2 orders below the band under either unit reading, and Yue
concedes the point.

**What the verdict should add.**
- The bound must stay scoped to pretrained LLMs (row A).
- The largest tested open runs (ProRL v2, AceReason-7B, high ≈ 2 × 10⁻²) are only ≈ 0.6–2.3 orders below the band. They
  reach its floor if the band is read as GPU-time (rows B, D).

The qualification itself is well supported: Interplay at ≈ 0.4× and our knockout at 3–10×.

**Scoring.** "0 held outright" is accurate, and #1–5 and #7 are fairly scored "in part", although #2 and #4 omit
clauses. #6 is arguable. The qualification is the pre-registered reason for "partly"; only the normaliser reason failed.
So "in part" (tally 0 / 7 / 0) is at least as defensible as "not held".
