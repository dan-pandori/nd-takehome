# Fact-check of `peer_rl_review/REPORT.md` (adversarial checker subagent, 2026-10-17)

The checker could not write files; the executor saved its returned findings here verbatim (lightly condensed), with
the disposition of each item added at the end. Checked against the committed report `bef79db0`.

Path prefixes: L = nd-rl `origin/leon/main:code/experiments/current/thinking_traces_20261005/`,
RE = `origin/robbie-experiments:`, DM = `origin/dmitry/main:experiment-summaries/2026-10-06-…/`,
CH = `origin/charles/main:data/pretrain_data/release_2026-10-12_textbook72_distract2/README.md`, ND = `origin/dan:`,
F = this worktree.

Re-runs: `schema_overlap.py`, `lean_reject_share.py scratch` and `ours_on_leon_passk.py scratch` reproduce the three out
files byte for byte.

## Problems

### WRONG

1. **Row 4, "2 vs 3 seeds", `L/OVERNIGHT_20261008.md:L170`.** L170 is the table separator; 17.2 is on L171. T0's
   textbook72 value is the 3-seed mean at k 256 (`L/stage1_stats/tb72.md:L11`: "| T0 | 3 | 17.2% [10.4, 25.1] |").
2. **§3.1 cause 2, "the pool explains little".** The cited rows (`L/matched_eval/v2_results.md:L549, L557`) compare the
   curriculum against v1 references that already trained on `rl_hard12` and then `hard712 a` (L4–5). Leon's direct pool
   control is at `L/OVERNIGHT_20261008.md:L265–277`:
   - no-think r2 reads 62.8 on hard712 and 53.6 on the old pool;
   - textbook72 gains are +7.2 [+3.9, +10.8] with thinking and +9.3 [+3.8, +15.2] without (caveat: dev58 informed
     hard712).
   So about 9 of the ~30 points come from the pool (single seeds).
3. **§1.3 and row 15, "41.40 % against 41.44 %".** These are the joint policy's returned answer and the same models'
   first proof (`DM/learned-compute-allocation/summary.md:L133`). Trained vs untrained is 41.44 against 41.67
   (format-only start). "Flat" still holds.
4. **P2, "below half only at 8k on Charles149".** It is also below half in these cases:
   - guided Charles149, +3.7 → −0.2 (`v2_results_ynez.md:L563`);
   - 13–20 and 16–20 (`RECIPE.md:L277`);
   - our own GRPO arms.

### OVERSTATED

5. **P2 scored with pass@5.** The prereg says large k is ≥ 64. Leon's k-64 counts for the v2 GRPO vs EI pairs (s0):
   - Charles149: +1 and −1 of 149, against +5.0 at pass@1 (`confusion_charles149.md:L13, L15`). This supports P2.
   - textbook72: +2 and +3 of 72, against +4.7 and +7.7 (`confusion_tb72.md:L13, L15`). This does not.
   - The verdict is mixed.
6. **Row 5 called a "same number" consistency check.** It compares 2 EI rounds with 8: 32.4 vs 39.2, and 24.8 vs 31.8.
7. **Thinking called "Established".** Each arm has one seed and the intervals are over problems only. r2 s0's interval
   spans 0 (+4.2 [−3.2, +11.2]). Two of the three pairs share Stage-1 seed 1. The seed-2 pair (+6.3, L306) is omitted.
8. **Knob gains "within rerun noise".** This holds on Charles149 (L883) but not on 13–20:
   - the control gives +1.3 [+0.2, +2.4] (L877);
   - the components give cooldown +3.9 (L827), 3-premise rows +3.2 (L837) and unlikeliness +2.1 (L857).
9. **Rows 7 and 8 omit an exposure caveat.** Round 2 trained on `pool_s5k_a`, which "has 13 matches with Charles's
   release and textbook72, 3 of them textbook72 dev problems" (`curriculum/README.md:L218–219`).
10. **"Every search-proof arm at 54–75 %".** Counterexamples: 52.4 (OVERNIGHT L234), 53.6 (L271), 50.1 / 40.2
    (confusion files L17, the collapsed redraw arms) and 53.9 (`confusion_charles149.md:L14`).
11. **"Lean-stopping higher still (0.653)" set against 0.594.** 0.594 is any valid among 8. 0.653 is the full-pool
    first-valid oracle, which equals Robbie's oracle@64.
12. **"Our GRPO arms point the same way".** The pass@4 arm is −1.8 at pass@1, and none of the pass@5 losses is
    resolved.
13. **"Charles149 clean for both sides".** Leon used it to select KL 0 (RECIPE L307–309). It also contains 5
    four-premise problems where our r8 is 0 of 256 in every seed and arm, which is up to 3.4 points of the gap.

### UNSOURCED

14. **"Neither side has an instance" of a Charles149 theorem.** Leon checked his pools against Charles173 only by
    renaming and curried class (`curriculum/README.md:L70–108`). His instance gate covers textbook72 only (L94).
15. **Robbie's 3-hour GRPO numbers, and §3.3's "GRPO ≪ EI".** These come only from Hugging Face `summary.json` files
    (`notes/robbie.md:L152–153`).
16. **Row 7, "211–235 tokens".** This figure is not in any out file. A recount gives 235.0 / 226.8 / 211.2.
17. **P1, "15 of 16".** The rows are not listed, and the criterion uses "metric" where the prereg says "plain/guided".
18. **4·10⁻²⁴ and the failed-knob list.** Neither is cited. The first is in Charles's
    `experiments/pretrain-data/textbook72_distract2/results.md:L116`; the knobs are in `v2_results_ynez.md` §7–8.

### MINOR

19. **§3.1 calls the base's post-RL share a hypothesis.** It omits the same-pool control on `rl_hard12`: r1 52.4 vs
    30.8 and r2 53.6 vs 32.4 (OVERNIGHT L234, L271; `matched_tb72.md` L14, L21).
20. **§1.3 says "Both are test-time only".** The Codex sprint trained the prover.
21. **Row 16.** The r8's 17 → 0 is on L28, not L27. The 48-step and 256-token caps are omitted.
22. **Overlong-masking cause.** It is at `GRPO_COLLAPSE_AUDIT.md:L87–107`.
23. **"Generator problems … 0 of 320 samples".** These are 21 hand-built problems. The generator figure is 0 of 120
    (L266–268).
24. **"909 among 281,817".** The 909 Lean-only pairs lie outside the 281,817 that both judges counted (lean-judge
    README L86–101).
25. **"IQM 37.3 against 51.7".** These are counts out of 72.
26. **"7–14-line generator targets" for both pipelines.** Leon's `rl_hard12` has 7–12 lines. Ours include 760
    textbook-schema targets.
27. **"Every pool caps at 3".** The source says "every earlier pool".
28. **Row 11.** The plain counts are best-state seeds and the guided counts are trajectory seeds. The atlas's train14
    caveat concerns the factorial cells.
29. **P3.** 65 of 72 is an EI checkpoint. His GRPO arms reach 62 and 66 of 72; the verdict holds.
30. **"He reports pass@1 / pass@5 only".** The report itself uses his pass@64.
31. **Dmitry's stopping numbers.** They are averaged over three generators (L245). At m≈8 the result is 0.633 @ 12.0.
32. **§1.1.** It juxtaposes serrano's Stage-1 numbers with the ynez retrain.
33. **Row 1, r8 pass@5.** It uses best-state seeds (53.6). The r16 card compares with trajectory seeds (53.1).

## Claims checked and found correct (checker's list, condensed)

- **Model facts.** "1.15M" is RL-target attempts, 1,150,720. "320k" is 2 × 39 × 256 × 16.
- **Out files.** Every † value matches.
- **Derived values:** 71–79 %, 80.3 / 77.4, 79 % / 61 %, 31–39, 25–43, 1,054, 48–56 / 11–17 / 44–49 %, 2.7–2.9×, and
  65/72 = 90.3 %.
- **Leon's citations**, apart from the items above.
- **Judge and files.** The 19 vendored files are byte-identical, and the 24 removed names are identical.
- **Robbie:** c005, the resample counts, TTRL, the state recipes, retry-EI, the model diff and the sweep.
- **Dmitry:** the selector table, 0.653 / 0.630 and +12.58.
- **Charles:** 17 → 0 of 25; 118 of 120; k 32, T 1.0, `nd_verify`; 412 → 173 → 149; one four-premise textbook72
  problem.
- **ND numbers and the prereg time.**

## Disposition (executor)

Items 1–4 and 6–33 were fixed in the report, each against the source line. Item 5 changed P2 to "mixed".

New script outputs back items 13 and 16 (`out/charles149_premises.txt`). The executor re-verified items 2, 19, 1, 9,
31 and 18 at the source lines before editing.
