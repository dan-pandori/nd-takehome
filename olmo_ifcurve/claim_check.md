# Claim check: olmo-ifcurve write-ups

Checked 2026-11-22. Documents: `run_olmo_ifcurve.md` (run doc), `olmo_ifcurve/plain_summary.md` (plain), `numbers.md` § olmo-ifcurve
(numbers). Sources: `olmo_ifcurve/` summary.json, passk.csv, emergence.csv, gaming.csv, lengths.csv, results.csv, compute.csv,
jobs.csv, gate_summary.json, handcheck.csv, checkpoints.csv, reuse_inventory.csv, `hand.armc_sample()`, the pre-registration
with amendments 1–5, `~/podhours.log`, QUESTIONS.md and log.md. Every number was recomputed in python from the CSV / JSON files.
The timing, shape and gaming intervals were re-bootstrapped independently, and they reproduce to Monte Carlo noise.

**Result: 25 findings, 9 substantive.** No table number is wrong. The problems are in plain-language readings, descriptions of
counts and expectation scoring.

## Substantive

**1. Prior runs misdescribed (plain).** "Earlier runs compared only the start and the end."
- Files: `reuse_inventory.csv` and the pre-registration's reuse table list stored olmo-ifomega fixed-phase draws at dpo, **s0100,
  s0750** and s2300 (`F_s0100_ifb`, `F_s0750_ifb`) and olmo-iffu's `T4_s0750`. `run_olmo_ifomega.md`'s table reports DPO,
  step 750 and step 2,300 (step 100 on IFBench). The pre-registration's priors quote pass@1 at dpo / 100 / 750 / 2,300 and say
  the 0 → 750 span "is already known".
- Fix: "Earlier runs looked at only a few snapshots (the start, steps 100 and 750, and the end)."

**2. "The class order" listed as a failed prediction (plain).** "Several advance predictions failed and are reported as misses:
the class order, …"
- Files: `summary.json` timing primary:F1_step gives medians P 500 / T 750 / N 1,100 and `order_holds: true`. Expectation 5's medians
  are scored held (numbers row 5). The miss is the "habit first" reading: the 90 % interval of rest − P is [0, 600], so its 5th
  percentile is not > 0. The plain summary's own previous bullet says "That is the order 'habit before skill' predicts."
- Fix: replace "the class order" with "the advance test that the class order is clear-cut (its interval touched zero)".

**3. Headline asserts what the pre-registered test did not establish (plain).** "**Easy-to-coax prompts come first.**"
- Files: the pre-registered reading is "no order" (`summary.json`: lo90 = 0.0). In an independent re-bootstrap, 9.5 % of
  replicates have rest − P ≤ 0. Only the secondary F2 reading is "habit first".
- Fix: "**Easy-to-coax prompts tend to come first**", and keep the hedge that follows.

**4. "Creeps up over several snapshots" is contradicted by the run's own categories (plain).** "The success rate usually creeps up
over several snapshots; no prompt jumped from nothing to frequent in one step."
- Files: `summary.json` categories: gradual 10, intermediate 26, slow 12, abrupt 0. "Gradual" means at least two checkpoints
  between F1\* and F25, and only 10 of the 36 prompts with F25 qualify (28 %). That is expectation 6's miss, which the same
  summary lists as a failed prediction.
- Files (`emergence.csv`): the number of checkpoint steps from F1\* to F25 is 1 on 14 prompts, 2 on 12, 3 on 8 and 4 on 2
  (median 2).
- Files (`results.csv`): several slow prompts rise and then fall. ifbench_280 has 7/32 genuine at 1,100 and 0 strict successes
  at 2,300. ifbench_166 goes 1 → 0 → 0. ifbench_1 and ifbench_4 have 0 genuine at 2,300.
- The second clause ("no prompt jumped…") is correct: abrupt = 0.
- Fix: "From the first rare success, most prompts became frequent within one or two snapshots; only 10 of 36 took three or more.
  No prompt jumped from nothing to frequent in one step."

**5. "Shortening did not come first" overstates the brevity reading (plain).** "The median answer falls from 261 words to 50,
settling only at step 1,600, after most reach prompts were solved. Shortening did not come first."
- Files (`lengths.csv`, arm A median answer words): 261, 243, 219, 181, 135, **93 at step 750**, 73, 57, 50. By H = 750, the
  first checkpoint with ≥ 24 reach prompts at F2, the median had already fallen 168 of its 211 words (80 %).
- Answer tokens fell 427 → 146 by step 750 (80 % of the drop to 74). The reach cells fell 248 → 81 → 33 (78 %).
- The pre-registered "not brevity first" (B = 1,600 > H = 750) concerns when lengths *settle* within ±20 % of the final value. It
  says nothing about when shortening starts.
- Fix: "Most of the shortening (261 → 93 words) had happened by step 750, alongside the reach prompts' progress. Answers settled
  only at step 1,600, so by the advance test (settling vs half the reach prompts) brevity did not come first."

**6. Strict "sharpening" presented as genuine improvement (plain and run doc).**
- Quotes. Plain: "Late training mostly makes the model reliable on prompts it can already solve ("sharpening")" and "The share
  solved on one try (pass@1) goes from 0.29 to 0.68". Run doc: "The estimated genuine pass@1 (40 hand reads per step) rises from
  0.25 to 0.50."
- Files: estimated genuine pass@1 is strict × (1 − arm-C share), from `summary.json` and `gaming.csv`. By step it is 0.2536,
  0.2441, 0.2676, 0.3127, 0.3911, 0.4096, **0.5052 (1,100)**, 0.4847 (1,600) and 0.4955 (2,300).
- The estimate is not monotone. It peaks at 1,100 and shows no gain after it (−0.009), while strict pass@1 gains 0.106. Over the
  same steps the arm-C gamed share goes 0.125 → 0.250 → 0.275.
- Each share rests on 40 labels, so a genuine gain is not excluded. Still, the "sharpening" reading is pre-registered on the strict
  score only, and "solved" / "reliable" is the checker's score including gamed passes.
- Fix, plain: "Late training mostly makes the model pass the checker more reliably on prompts it can already pass
  ('sharpening'). By the hand-check estimate, the genuine share stops rising after step 1,100 (about 0.50) while gaming rises."
  Also add "(an estimated 0.25 → 0.50 genuinely)" to the pass@1 sentence.
- Fix, run doc: "…rises from 0.25 to 0.51 at 1,100, then stays flat (0.48 / 0.50 at 1,600 / 2,300). The strict gain after 1,100
  is not visible in the genuine estimate."

**7. Count of late reach wins misstated (run doc).** "0.06 of 16 early wins vs 0.31 of 536 late ones."
- Files (`results.csv`, arm-B base cells): the late cells (1,100 / 1,600 / 2,300) hold 591 + 847 + 1,066 = **2,504** strict
  successes.
- 536 = 170 + 178 + 188 is the number of first-≤ 4 labels per cell (`gaming.csv` armB_first4_labelled), the pre-registered
  secondary sample.
- "16 early wins" is right: 0 + 2 + 14 strict successes, all labelled.
- Fix: "…vs 0.31 of 536 late ones (the first ≤ 4 wins of each cell; 2,504 late wins in all)".

**8. "Every hard prompt eventually gets a genuine solution" (plain headline) misreads the end state, and it holds partly by
construction (plain; run doc caveat).**
- What the data support: every prompt had a genuine success at some checkpoint (F1 ≤ 2,300 on all 48).
- At the final checkpoint (`results.csv`, s2300), a genuine success is established on only 40 of 48 prompts.
  - Four cells were read in full with 0 genuine: ifbench_1 (25 strict successes, all gamed), ifbench_4 (27, all gamed),
    ifbench_166 (7, all gamed) and ifbench_280 (0 strict; it had 7 genuine of 32 at step 1,100).
  - On four more prompts (ifbench_0 / 226 / 252 / 267), the first four strict successes were gamed and the rest were not read.
  - The number of prompts with an established genuine success per checkpoint goes 42 (1,100) → 44 (1,600) → 40 (2,300).
- The reach set was selected for step 2,300 solving it on other draws: olmo-ifomega "Reach = step 2,300 confirmed" and
  olmo-ifladder "s2300 solves them". "All 48 reached by 2,300" is therefore largely guaranteed by selection, and the 40 of 48 on
  fresh s2300 draws is the honest end-state number.
- The run doc caveat "Step 0's reach column is selection-defined" covers only the start of the run.
- Fix, plain: "**Every hard prompt gets a genuine success at some snapshot.** At the end, the final model shows one on 40 of 48;
  on 4 others all its checker passes were gamed or absent."
- Fix, run doc caveat: "The set was also selected for step 2,300 solving it (on other draws), so reaching all 48 by 2,300 is
  expected."

**9. Expectation 4's early part was scored on an unstated basis (numbers row 4).** "≤ 3 of 48 with any genuine at 50 and at
100 … | 0 / 2 **held**"
- Files (`results.csv`): on the 32 base draws, s0050 has a genuine success on 0 prompts and s0100 on 2 (ifeval_2247, ifbench_220).
- The same checkpoints also hold extension draws: s0050 on 2 prompts, s0100 on 7. Counting them, s0050 has a genuine success on 1
  prompt (ifbench_220, 1 of 96 extra draws) and s0100 on **4**: add ifeval_2563 (3 of 96) and ifbench_173 (1 of 96).
- The expectation names no cell size, so the s0100 part flips to a miss under the all-draws reading.
- Fix: "0 / 2 **held** on the 32 base draws (with the extension draws 1 / 4, which would miss at 100)".

## Minor

**10. The s2300 miss rests on lower bounds (numbers row 4; run doc; plain).**
- Quotes. Numbers: "**missed** at 2,300: 40 and 36 established". Run doc: "s2300 genuine on ≥ 44 reach prompts (40)". Plain:
  "how many hard prompts the final model still solves".
- Files (`results.csv`, s2300): established counts are ≥ 1 genuine on 40 and ≥ 2 on 36.
- With the first-4-share estimate, the counts are 40 and **39**. Three cells (ifeval_1314, ifbench_187, ifbench_271) have 1
  established genuine and 23–27 unread successes at a 1/4 genuine share.
- If every unread success were genuine, the upper bounds would be 44 and 43.
- "≥ 1 on ≥ 44" holds only if all four partly read cells hide a genuine success. "≥ 2 on ≥ 40" misses on the labels and on the
  estimate, but is not excluded.
- The numbers row explains the ≥ 1 part but not the three one-genuine cells behind the ≥ 2 part. The run doc omits the ≥ 2 part.
- Fix: "missed on the labels (40 / 36) and on the first-4 estimate (40 / 39); not excluded (upper bounds 44 / 43)".

**11. Expectation 7 (arm B) was not scored part by part (numbers row 7).** "arm B **missed**: "gaming grows" (0.062 on 16 early
items vs 0.306)"
- The pre-registration reads: "gaming first" (early ≥ 0.5 if ≥ 10 early items, late ≤ 0.35).
  - The reading missed.
  - Early ≥ 0.5 missed (0.0625, n 16).
  - **Late ≤ 0.35 held (0.306).**
- Fix: add "late ≤ 0.35 held (0.306)".

**12. The run doc's expectations line is incomplete.** "Held: the pass@k intervals, … Missed: …"
- Held parts it omits:
  - 4: early counts 0 / 2 on base draws; F1 ≤ 750 on 35, within 28–36.
  - 6: abrupt 0; median earliest rate 0.039 ≤ 3/32.
  - 7: arm-C shares in [0.05, 0.30]; arm-B late ≤ 0.35.
- Missed part it omits: 4, ≥ 2 genuine on ≥ 40 at 2,300 (36 established).
- "The length intervals" held narrowly: the 1,100 → 1,600 thinking drop is 14.8 % against a 15 % limit.
- Fix: list them.

**13. "12 prompts never reach a 0.25 rate." (run doc)**
- "Slow" means no cell showed 8 genuine of its base 32 by 2,300. That is an observed count, not a rate.
- Several slow prompts come close. ifbench_268 has 7/32 genuine at 1,600, ifbench_280 7/32 at 1,100 and ifbench_284 7/32 at
  2,300. ifbench_217 has an estimated rate of 0.219 at 1,600.
- Per the pre-registration, a true rate of 0.25 gives ≥ 8/32 only with probability ≈ 0.57.
- Fix: "12 prompts never show 8 genuine successes in 32 draws (the 0.25 mark) by 2,300."

**14. "Half the reach prompts have two genuine successes by 750" (run doc).**
- `emergence.csv`: F2 ≤ 750 on **29 of 48** (0.60). The criterion for H is ≥ 24.
- Fix: "29 of 48 (≥ 24 needed) have two genuine successes by 750".

**15. "All 48 reach prompts see a first genuine success between steps 100 and 2,300" (plain).**
- This is true on the 32 regular draws.
- But ifbench_220's 128-draw cell at **step 50** held a genuine success (`emergence.csv` F1star = s0050), and the next sentence
  of the same bullet ("a rare success was already present one snapshot earlier") counts it.
- "First solved" / "after most reach prompts were solved" means ≥ 1 genuine success in 32 tries, a rate of a few per cent.
- Fix: "…in their 32 regular tries (one had a rare success at step 50 in its extra tries)". Use "first solved once" rather than
  "solved".

**16. "in 32 fresh draws" (run doc).**
- `reuse_inventory.csv`: the s0100 IFBench cells are 8 stored `F_s0100_ifb` draws + 24 new.
- The s0750 IFBench cells are olmo-iffu's stored `T4_s0750` draws, with 16 new draws on 17 prompts.
- "Fresh" is true only in the sense "not used in selection".
- Fix: "in 32 base draws not used for selection".

**17. "40 hand reads per step" (run doc), "40 strict successes read per step" and "arm C sample read" (numbers).**
- `gaming.csv` armC_sources: 349 of the 360 arm-C labels were read and 11 were inherited from identical answers (s0050 3,
  s0100 2, s0500 1, s0750 1, s1100 2, s1600 2).
- The "arm B first-4 read" column also includes screened and inherited labels.
- Fix: "labelled" in place of "read".

**18. "rises monotonically" (run doc), "The score climbs steadily" and "stops rising" (plain).**
- `passk.csv`: the point estimates rise at every checkpoint, but the steps are uneven.
  - +0.006 (0 → 50) and +0.019 (50 → 100) are inside the pre-registered ≈ 0.03 paired noise floor.
  - The gain per 100 steps ranges from 0.005 (1,600 → 2,300) to 0.040 (500 → 750).
- After 1,100, pass@8 gains +0.014 [−0.018, 0.046]: no detectable gain, which is not the same as stopping.
- Fix: "rises at every checkpoint (point estimates; within noise before step 100, fastest from 500 to 750)", and "then shows no
  detectable further gain".

**19. Interval levels missing (run doc).**
- "0.106 [0.080, 0.132] … 0.014 [−0.018, 0.046]", "250 [0, 600]" and "600 [350, 600]" are **90 %** intervals (`summary.json`).
  Elsewhere the docs use 95 %.
- Fix: label them 90 %.

**20. Gaming wording (run doc and plain).**
- Quotes. Run doc: "the gamed share is flat: 0.14 early … vs 0.22 late". Plain: "On ordinary prompts the gamed share … stays
  around 0.1–0.3".
- Files (`gaming.csv`): the arm-C shares per checkpoint are 0.125, 0.175, 0.150, 0.100, **0.050**, 0.200, 0.125, 0.250 and
  0.275. The 90 % interval of early − late is [−0.175, 0.015].
- "Flat" is the pre-registered label for |Δ| < 0.2, not "no change".
- The arm-C sample is drawn from all 218 prompts, including the IFBench reach prompts. Those make up 18 of 360 sampled items and
  16 of the 120 late ones (`hand.armc_sample()`), so "ordinary prompts" is inexact.
- Fix: "flat by the pre-registered 0.2 threshold (0.14 → 0.22)", and "on the full prompt set it stays between 0.05 and 0.28 per
  snapshot".

**21. "(no community H200 was available)" (numbers, Spend).**
- `~/podhours.log`: three `ifc-a` pods ran on a faulty community H200 ($0.40 + $0.18 + $0.26). They are part of the $0.86.
- Fix: "no working community H200".

**22. Half-values rounded half-to-even (numbers).**
- These went down: 2116.5 → "2116", 4532.5 → "4532" (also "4,532" in row 9), 5706.5 → "5706", and 0.0625 → "0.062" (arm B; row 7).
- These went up: 4411.5 → "4412", 6139.5 → "6140", 293.5 → "294" and 145.5 → "146".
- Rounding half up would give 2117, 4533, 5707 and 0.063. No reading changes.
- Fix: round half up, or say that the tables round half to even.

**23. Pre-registered arm-C agreement not reported (numbers, hand gate).**
- The pre-registration says "a seeded quarter gets a second reader (agreement reported)". Only the pooled figure appears:
  272 of 296.
- Computed from `hand.armc_sample()` and `handcheck.csv`: the first two reads agree on 88 of the 90 arm-C items.
- Fix: add "arm-C quarter: 88 / 90 agree".

**24. Expectation 6's earliest-rate basis unstated (numbers row 6).** "earliest rate **held** (0.039)"
- 0.039 is the median over all 48 prompts. Over the 36 prompts with F25 (the row's own denominator) it is 0.043. Both are
  ≤ 3/32 = 0.094.
- The rate counts labelled genuine successes only. ifbench_226's F1\* cell has 3 unread strict successes, so its rate is 0.094
  labelled vs 0.164 estimated. The median does not change.
- Fix: "held (0.039 over 48; 0.043 over the 36 with F25)".

**25. Sub-agent token use is not recorded (numbers).** "≈ 70 batches of ≈ 100–170 k tokens each"
- The files show 64 reader batch files plus 11 audit / adjudication tasks (a1–a6b, u1–u4), 75 in all. No file records tokens per
  task.
- Fix: "75 sub-agent tasks (64 reader batches, 11 audits); token use not logged".

## Verified as correct

- **Arm A table.** Every pass@1 / pass@4 / pass@8 value and 95 % interval, and dpo's first 8 draws (0.290 / 0.459)
  (`passk.csv`). Also the run doc's pass@1 sequence 0.290 … 0.683 and pass@8 0.872 / 0.872 / 0.885.
- **Per-family values.** pass@1 at dpo → 750 → 2,300 and the family sizes 65 / 58 / 43 / 21 / 14 / 11 / 6.
- **Shape (reading 5).**
  - Δ1 / Δ8 and their 90 % intervals at 750 / 1,100 / 1,600, and the onset 1,100 (re-bootstrapped: [0.080, 0.133] /
    [−0.018, 0.046] at 1,100).
  - Expectation 3 held. Expectation 2 held (point estimates strictly increase).
- **F1 counts.** 50: 0, 100: 2, 200: 7, 500: 11, 750: 15, 1,100: 8, 1,600: 3, 2,300: 2, never: 0, plus the per-class lists. F1 ≤
  750 on 35. Every cell before F1 is fully labelled, so F1 is exact.
- **Timing (reading 1).**
  - Class medians for F1 and F2, under both class maps.
  - Rest − P = 250 / 600 / 425 / 475, with the 90 % intervals [0, 600] and [350, 600] (reproduced independently).
  - Readings "no order" (F1) and "habit first" (F2).
- **Categories (reading 2).**
  - Gradual 10 (7 / 3 / 0), intermediate 26 (15 / 8 / 3), slow 12 (3 / 5 / 4), abrupt 0.
  - Gradual share 10 / 36 = 28 %. F1\* earlier than F1 on 18 prompts. Median earliest rate 0.039 (= 5/128).
  - F25 determinations are complete: no cell has an undecided ≥ 8.
- **s2300.** Established 40 / 36, 660 unread, and the account of the 8 prompts without an established genuine success.
- **Gaming.**
  - Every `gaming.csv` row.
  - Arm C: early 0.1375 (n 160), late 0.2167 (n 120), interval [−0.175, 0.015], "flat".
  - Arm B: 0.0625 (n 16), 0.3060 (n 536), interval [−0.360, −0.091], "gaming grows". The intervals re-bootstrap to within 0.005.
  - Run doc rounding 0.14 / 0.22 / 0.06 / 0.31.
- **Arm D.**
  - The medians and cut shares 0.06 / 0.17 / 0.46 / 0.63 %.
  - Brevity: B = 1,600 and H = 750, "not brevity first".
  - The thinking drop 1,100 → 1,600 is 14.8 %.
  - Expectations 8, 9 and 10 are scored correctly.
- **Expectations 1, 5, 6 and 7.**
  - Expectation 1: all measured parts in range, including pass@8 at 500 (0.656, amendment 5); the "not measured" parts are right.
  - Expectation 5: medians held, reading missed.
  - Expectation 6: gradual missed, abrupt held.
  - Expectation 7: the arm-C part.
- **Estimated genuine pass@1 row** (all nine values).
- **Hand gate** (`gate_summary.json`, `handcheck.csv`): 1,782 items. Reads are 1,486 × 1 + 270 × 2 + 26 × 3 = 2,104, so 296
  items have ≥ 2 reads. 272 agree, 209 confirmed, 103 changes, 1,559 = 1,440 + 45 + 74, 1,079 / 480. Batches are ≤ 40. Rules
  13–14 are dated and are about keyword stuffing.
- **Compute** (`compute.csv`, `jobs.csv`): 27 job runs, 20.22 GPU-h, 116.8 M tokens, 21,216 draws, H200 TP 1.
- **Spend** (`~/podhours.log`): $154.67 and 29.72 pod-hours.
  - Orphans: $34.84 and 17 pods (REST v1 retirement per QUESTIONS.md).
  - $0.86 = $0.84 faulty community H200 + $0.02 test. $1.69 reconciled.
  - The rest is $117.28 over 22.17 h at $5.29/h.
  - The cost line in the plain summary is right.
- **Bounds.** One-sided exact 95 %: 1.16 % (256), 2.31 % (128), 8.94 % (32).
- **RL-data overlap.** 0 / 218 and 0 / 48 flagged (`olmo_ifomega/contamination.csv`, maximum content containment 0.433).
- **Checkpoint commits** (`checkpoints.csv`). `main` = `step_2300` by weights digest.
- **Plain summary figures.** 0.29 → 0.68, pass@8 0.87 by 1,100, 261 → 50 words settling at 1,600, 1,782 labelled checker passes,
  18 prompts with an earlier rare success, a median of about 4 in 100, class timing 500 / 750 / 1,100 with "the seven", and the
  interval's lower bound exactly 0. The F2 test passes.

## Resolution (executor, 2026-11-22 05:54 UTC)

All 25 findings accepted and fixed: in `run_olmo_ifcurve.md` (rewritten, 397 words), `olmo_ifcurve/plain_summary.md`
(rewritten, 500 words) and `numbers.md` § olmo-ifcurve. Specifically:
- 1–5, 8, 15, 18, 20: plain-summary wording (earlier snapshots; "tend to come first"; one-or-two-snapshot climbs; brevity
  timing; 40 of 48 at the end and the selection built-in; "at every snapshot"; gaming range).
- 6: genuine-estimate plateau after 1,100 stated in both docs.
- 7, 13, 14, 16, 19: run-doc counts and interval levels.
- 9–11, 17, 21–25: numbers.md rows and notes (base-draw basis for expectation 4, the lower-bound caveat, part-by-part
  scoring for 6 and 7, "labelled", the arm-C agreement 88 / 90, working community H200, the rounding note, the
  sub-agent task count).
- 12: the run doc now lists the misses and states that the rest held, pointing to the full table.

`numbers_section.py` generated the section's tables. The wording edits above were made by hand afterwards.
