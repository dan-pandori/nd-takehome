# Adversarial check of review_olmo-iffu.md (2026-11-07)

Scope: the review at `e57060d0`+review commits, its kit `review/olmo-iffu-recount/` (out/, hand/), the executor's files, and
`review_olmo-ifomega.md`. Read-only; every value below was recomputed with short python scripts (scratch only in /tmp or
stdout). Findings are ordered by weight.

## Findings

1. **Location:** Phase-2 corrections ("226 falls to 1 genuine of 16"); §Compare row 226; §Verdict 5 ("Read to the end, the hint breaks `s2300` there").
   **Category:** OVERCLAIM / INCONSISTENT (reader-dependent outcome stated as fact; own adjudication rule not applied).
   **Review says:** the hint breaks `s2300` on ifbench_226, stated as a fact. §9's list of reader-dependent outcomes ("only … 188 (T2) and `ifbench_1` (T2c)") is extended in phase 2 to 170 but not to 226.
   **Source says:** `out/sensitivity.txt`: "T2c_s2300|ifbench_226: A {'genuine': 2 …}, B {'genuine': 1 …}, final {'genuine': 1 …}". Rank 5 (r2a6181) is genuine for both readers. Rank 6 (r3a0f2d) has exactly two reads: `r3_if_00` genuine and `b_if_04` gamed. The reviewer alone decided it gamed (`hand/confirm.json`). With every other item at its final label, rank 6 alone decides 226: flipping it gives 2 genuine, so not broken. `hand/confirm.json` `_rule` says "Outcome-deciding disagreements … also went to a third blinded reader; the majority of the three readers decides". Rank 6 never got a third reader. Ranks 9, 11, 12 and 14 are each 1 genuine to 2 gamed, so each is also individually deciding.
   **Fix:** send 226 rank 6 to a third blinded reader, as the rule requires. Until then, state 226 as reader-dependent: "breaks under B and final labels; not broken under the first readers alone (ranks 5 and 6 genuine)". Do this in the phase-2 corrections, the 226 row and §Verdict 5, and add 226 to §9's reader-dependent list.

2. **Location:** Phase-2 corrections, bullet 2: "The expectation '10 of 32 (4–16)' is therefore inside its interval … 'miss' … is withdrawn".
   **Category:** OVERCLAIM (reader-dependent verdict stated as fact; inconsistent with §12's own style).
   **Review says:** 4 of 32 (1, 3, 166, 226), inside at the lower edge; the miss is withdrawn.
   **Source says:** §12 reported this row as "3 (A alone: 2)". After phase 2, under the first readers alone, test 2c breaks `s2300` on 3 and 166 only, which is 2: `out/sensitivity.txt` gives `ifbench_1` A = 2 and 226 A = 2. That is still below 4–16. "Inside" rests on two reader-dependent prompts, 1 and 226; the second is the un-third-read 1–1 split in finding 1.
   **Fix:** "4 of 32 under B and final labels (inside, at the lower edge); 2 under the first readers alone (miss): reader-dependent".

3. **Location:** §6, not corrected in phase 2: "The hint breaks `s2300` on 6 of 48 hinted prompts … or 4 under the first reader alone".
   **Category:** INCONSISTENT (stale phase-1 count).
   **Review says:** 6 of 48.
   **Source says:** `out/outcomes.json` (phase 2) has breaks on 0, 4, 188 (T2) and 1, 3, 166, 226 (2c), which is 7 of 48, or 8 with 170 broken. The first readers alone still give 4. Relatedly, the §Compare "Hint breaks …" row lists "0, 4, 188, 1, 3, 166 (6)" with no note that 226 also breaks. That is correct for the executor's "8 more", which counts only prompts where `dpo` is not elicited, but the row does not say so.
   **Fix:** add to the phase-2 corrections: "§6 pooled becomes 7 of 48 (8 if 170 is broken; 4 under the first readers alone)". In the "8 more" row, note "226 also breaks, but `dpo` is prompt-elicitable there".

4. **Location:** §Compare row "T1 finished-length quartiles (numbers.md)": "068 identical, 055 / 069 medians 46,865 / 45,299 vs 46,860.5 / 45,087".
   **Category:** WRONG.
   **Review says:** 068's quartiles are identical under the two methods.
   **Source says:** `out/phase2_checks.txt` §7: 068 nearest-rank [42458, 45521, 49030] vs interpolated [42814.5, 45521.0, 48794.5]. Only the median and the max agree; q1 differs by 356.5 and q3 by 235.5. q1 and q3 also differ for 055 and 069, by 20–659 tokens (069 q3 is 48,426 vs 47,767.5). This row also prints 46,860.5 where §4 prints 46,860.
   **Fix:** "Medians: 068 identical (45,521); 055 46,865 vs 46,860.5; 069 45,299 vs 45,087. q1 and q3 differ on all three prompts by 20–659 tokens (method)."

5. **Location:** §Compare row "Deviations 1–4 and the 2c addition pre-registered before sampling (prereg, run)", verdict "reproduces".
   **Category:** MISQUOTE / INCONSISTENT.
   **Review says:** the executor claims deviations 1–4 and 2c were pre-registered before sampling. The review's own value says "deviations are later additions", yet the verdict is "reproduces".
   **Source says:** `run_olmo_iffu.md` reads "Deviations: test 2c (hint on 32 more IFBench prompts) pre-registered before sampling; test 4 capped at 32 draws …". Only 2c is claimed as pre-registered. The prereg's own times put deviations 1, 2 and 4 after their tests' sampling had begun:
   - deviation 1 at 00:24–00:36 (T2_s2300 started 23:53:33);
   - rule 6 at 00:08 (T2_dpo started 23:33:13);
   - deviation 4 at 05:37 (commit a6bdf6c1 at 05:37:38; T4_s0750 started 04:59:31, with 400 samples by then per log.md).
   Only deviation 3 (scheduling) preceded T4.
   **Fix:** split the row into two:
   - "2c pre-registered before its sampling (02:01:45 < 06:23:12): reproduces";
   - "deviations 1–4 recorded as run; 1, 2 and 4 were adopted after their tests' sampling began (deviation 4 about 38 min into T4)".

6. **Location:** §Compare verdicts vs §Verdict: "Not supported. 'Of the 52 reach prompts, 18 are now explained' is 17. Nothing else is unsupported".
   **Category:** INCONSISTENT.
   **Review says:** in §Verdict, only the "18 explained" claim is unsupported.
   **Source says:** the review's own §Compare gives the 069 "token budget" row the verdict "**not supported as stated**", and gives the "18 explained" row only "reword". §Verdict swaps the two: 069 goes under "Must be reworded" and "18 explained" under "Not supported". It then asserts that nothing else is unsupported.
   **Fix:** use one category per claim in both places. Either list the 069 "token budget" claim under Not supported, or soften the §Compare verdict; then drop or correct "Nothing else is unsupported" (see also findings 9 and 23).

7. **Location:** §Verdict 1: "The pre-registration's 'shown under both readings' is not met." §Compare figure row verdict: "**wrong cell**".
   **Category:** OVERCLAIM.
   **Review says:** both readings are not shown; the figure's 069 "before" cell is wrong.
   **Source says:** `olmo_iffu/status.csv`, row 069:
   - before = 0/256, before_note = "doubly reading; 2 rl-credited dpo responses read sound in the review (any reading: 2/256)";
   - t1 = 2/64, t1_doubly = 1/64.
   `numbers.md`'s test-1 row reads "**token budget** (any); one sound (doubly)". So both readings are shown in status.csv and numbers.md, but not in the figure or in run.md. 0/256 is correct under the doubly reading the executor documents; the defect is that one figure row puts a doubly "before" cell beside an any-reading test-1 cell. The review also cites "(run, status, figure)" without listing status.csv in its Sources.
   **Fix:** "not met in the figure and run.md (status.csv's before_note and numbers.md show both)". Call the cell "a doubly reading beside an any-reading test-1 cell (mixed readings)", not "wrong"; add status.csv to Sources.

8. **Location:** §Compare row "'`s2300` 28 / 40 at 32k' on 068 and 069 (run, numbers.md, plain)", verdict "reproduces (inherited, labelled)".
   **Category:** INCONSISTENT / MISQUOTE.
   **Review says:** the number is labelled as inherited, and it appears in run, numbers.md and plain.
   **Source says:** the review's own Model-labels section says "in `run_olmo_iffu.md` it is unmarked", and §Verdict 6 asks the executor to mark it. `plain_summary.md` contains no "28 / 40"; it says "solves two of these puzzles about 70 % of the time".
   **Fix:** "reproduces; marked as olmo-ifomega's in numbers.md only (unmarked in run.md; the plain summary paraphrases it as about 70 %)".

9. **Location:** same row, and §Verdict "Nothing else is unsupported".
   **Category:** UNSUPPORTED (the "reproduces" verdict checks the number, not the comparison it is used in).
   **Review says:** "reproduces".
   **Source says:**
   - `run_olmo_iffu.md` reads "Solvable, not reliable: `dpo` 1.6–4.7 % per sample, `s2300` 28 / 40 at 32k". The `dpo` rates are hand-sound (numbers.md "`dpo` sound rate"); 28/40 is automatic `omega` credit (`out/phase2_checks.txt` §9: omega 28, rl 33 and 29).
   - `review_olmo-ifomega.md` row 069 shows `s2300` at "29 / 9 / 6" (credited / read / good), so only 6 of the 9 credits read were sound.
   - The plain summary turns this into "the RL model solves two of these puzzles about 70 % of the time".
   **Fix:** flag the mixed measures: "`s2300`'s 28/40 is checker credit; on 069 only 6 of 9 read were sound (predecessor), so the hand-sound rate is unmeasured and likely lower".

10. **Location:** §Verdict, Next measurements: "IFBench prompts still open on sampling. The 19–21 prompts the hint did not elicit and did not break".
    **Category:** WRONG.
    **Review says:** 19–21 IFBench prompts.
    **Source says:** the category includes ifeval_2350 and ifeval_3478. `olmo_iffu/status.csv` "not elicited by the hint (sampling untested)" has 19 rows: 17 IFBench plus those two IFEval. `out/outcomes.json` (final labels) has 21: 19 IFBench plus 2 IFEval.
    **Fix:** "the 17–19 IFBench prompts (19–21 with ifeval_2350 and 3478)".

11. **Location:** §Compare status-of-52 row: "not elicited with the hint fine **20** (284 added; 21 if 170 is unbroken); uninformative **5**".
    **Category:** INCONSISTENT (the primary reading for 170 flips between rows and departs from the kit).
    **Review says:** the primary values assume 170 is broken (20 / 5).
    **Source says:** `out/outcomes.json` has T2 ifbench_170 "breaks": False, s_genuine 2, so the kit's own counts are 21 / 4. Other rows take 170 as unbroken by default: the "harmless" row says "13 of 16 (12 with 170 broken)", and §Verdict 2 says "6, or 7 if 170 counts as broken". The sums are right either way: 52 under both readings.
    **Fix:** use one primary throughout, preferably the kit's final labels: "21 / 4 (20 / 5 if 170 is broken)".

12. **Location:** §Compare row "Hint harmless for `s2300` on 12 of 16 (expected ≥ 14): a miss (run)", verdict "miss reproduces; exact count reader-dependent".
    **Category:** OVERCLAIM (minor).
    **Review says:** the miss reproduces.
    **Source says:** the same cell gives "14 with my first reader only", and ≥ 14 is the expectation. So under the first readers the expectation holds; §12 itself says "**miss** (reader-dependent)".
    **Fix:** "miss under B, final and executor labels; holds under the first readers alone (14)".

13. **Location:** §Verdict 3: "The strict drops are small"; §Compare: "(differences small)".
    **Category:** OVERCLAIM (minor).
    **Review says:** the drops are small.
    **Source says:** in `olmo_ifomega/results.csv` (`s2300`), ifbench_179 has succ_strict 21 of 24 attempts (87.5 %) vs 10/16 (62.5 %) with the hint, 25 points lower. ifeval_1314 has 22/24 (91.7 %) vs 12/16 (75 %). One-sided Fisher p is about 0.07 and 0.16: not significant, but not small.
    **Fix:** "not significant individually (largest: 179, 87.5 % → 62.5 %, one-sided Fisher p ≈ 0.07)".

14. **Location:** §12: "T4 `s0750` confirmed 24 of 43 (16–32) | 26 (at a 32-draw cap, not 64) | inside". §13 items "the 32-draw cap's effect on test 4's 26 of 43" and "the sub-bullet borderlines".
    **Category:** UNSUPPORTED (minor).
    **Review says:** inside; §13 promises two phase-2 comparisons.
    **Source says:** the prereg's quantity is "confirmed (≥ 2 genuine in ≤ 64)". With 17 prompts unconfirmed at 32 draws (5 of them at 1 genuine, per `out/outcomes.md`), the ≤ 64 count lies anywhere in [26, 43]. It is inside only if at most 6 of the 17 confirm in 32 more draws. Neither planned comparison appears in §Compare. (The sub-bullet items agree between executor and reviewer, which §Compare could have said.)
    **Fix:** "≥ 26 at ≤ 32 draws; the pre-registered ≤ 64 count is unmeasured". Report both §13 comparisons or remove them from §13.

15. **Location:** §12: "T3 survivors 6 of 10 (3–9); resolved 2; one genuine 2 | 10; 0; 0 | **miss**".
    **Category:** MINOR.
    **Review says:** the whole row is a miss.
    **Source says:** the prereg has "resolved 2 (0–5); exactly one genuine 2 (0–4)", so 0 and 0 are inside. `out/expect.md` limits the miss to survivors ("survivors: MISS").
    **Fix:** "survivors: miss; resolved and one-genuine: inside".

16. **Location:** §12: "T1 finished median 48k (38–58k) | 45.8k pooled | inside" (the table cites `out/expect.md`).
    **Category:** MINOR (statistic differs from the cited source).
    **Review says:** 45.8k pooled.
    **Source says:** `out/expect.md` uses the median of the per-prompt medians, 45,521: "inside the interval (median of the per-prompt medians)". 45,805 is the pooled median in `stats.txt`. Both are inside.
    **Fix:** cite `stats.txt` for 45.8k, or report 45.5k.

17. **Location:** §Compare T3 row ("k ≥ 342 … | same"); header ("Every number below is in a file under `review/olmo-iffu-recount/out/` or `hand/`").
    **Category:** MINOR.
    **Review says:** the executor's k ≥ 342 is the same as the recount; every number is in a kit file.
    **Source says:**
    - `out/outcomes.md` prints "2.92e-03 (k ≥ 343)" (ceiling). The prereg and numbers.md use 342 (floor of 342.3).
    - Several review numbers are in-text derivations found in no out/ or hand/ file: 46,580 and 2,544 GPU-s (`compute.txt` lists only 15,704 and 30,876), 95.0 %, 93.8 %, ≈ $20, and "1 / bound ≈ 342".
    **Fix:** note the 342 vs 343 rounding convention; reword the header as "every number is in, or derived from, a file under out/ or hand/".

18. **Location:** §4: "a second blind reader on the two outcome-deciding items (055 c3.11, 069 c2.8)".
    **Category:** MINOR (imprecise).
    **Review says:** only two items decide outcomes.
    **Source says:**
    - Under the pre-registered `any` rule, flipping 055 c2.5 (0 sound → "not reached") or 069 c3.4 (1 sound) also changes an outcome.
    - Under `doubly`, 068 c1.15, 068 c2.12 and 069 c3.6 do too (`out/hand.txt`).
    - Each of these has one reader: r1_om_07, r1_om_05, r1_om_08, r1_om_04 and r1_om_01 have no `_b` file. The reviewer did check their pair sets.
    **Fix:** "on the two `rl`-only items; the other deciding items rest on one reader plus my own pair-set check".

19. **Location:** §Compare 368-items row: "'every deciding one' is not quite true for the `s2300` checks".
    **Category:** MINOR (inconsistent with the row's own evidence).
    **Review says:** the gap concerns the `s2300` checks.
    **Source says:** the same cell cites T2c `dpo` 78. The executor read ranks 0, 1, 2, 5 and 7 and skipped 3, 4 and 6 (`out/hand_compare.txt`: "unread from rank 3"). That is skipping, not reading "out of draw order".
    **Fix:** "not quite true: 226's `s2300` check stopped at 5 of 16, and 78's `dpo` walk skipped ranks 3, 4 and 6".

20. **Location:** §1: "plus the shared `MANIFEST.jsonl` (rows appended), `QUESTIONS.md` and its own write-ups".
    **Category:** MINOR.
    **Review says:** these are the only files outside the run's own paths.
    **Source says:** `out/phase2_checks.txt` §1 lists outside its own paths: QUESTIONS.md, **STATUS.md**, artifacts/MANIFEST.jsonl, log.md, numbers.md, run_olmo_iffu.md.
    **Fix:** add STATUS.md (a shared file with an appended section).

21. **Location:** §12 timing: "the header says 'Written 23:20–23:50 UTC' and … 'written 23:50 UTC', both later than the commit".
    **Category:** MINOR.
    **Review says:** two post-commit timestamps.
    **Source says:** commit 048ef5fe (23:22:37) also contains "Both configs (checked 2026-11-06 23:30 UTC from the Hub)" (prereg line 25), a third post-commit time. The header's range starts at 23:20, before the commit; only its end is later.
    **Fix:** "the header's end time 23:50, the config check at 23:30 and the OMEGA rule's 23:50 all postdate the 23:22:37 commit".

22. **Location:** §Compare rows "`s2300` 31.5 → 19 (run, numbers.md)" and "≤ 2.92 × 10⁻³, k ≥ 342 (run, numbers.md, plain)".
    **Category:** MISQUOTE (attribution, minor).
    **Review says:** these appear in run.md (and in plain).
    **Source says:** `run_olmo_iffu.md` gives only "`dpo`'s median answer from 231 to 60 words" and "≤ 2.9 × 10⁻³ per sample", with no `s2300` lengths and no k. `plain_summary.md` says "below 0.3 % per try". The `s2300` 31.5 → 19 and k ≥ 342 appear only in numbers.md and log.md.
    **Fix:** cite numbers.md (and log.md) for those parts.

23. **Location:** §Verdict: "Nothing else is unsupported".
    **Category:** UNSUPPORTED (blanket claim; the review lists log.md among its sources).
    **Review says:** no other executor claim is unsupported.
    **Source says:** log.md (02:03) says "`dpo`'s median answer falls from 64–600 words … to 50–95 with the hint". `olmo_iffu/summary_tables.md` has ifbench_64 `dpo` "6.0 → 12.0", so the ranges are 6–600 → 12–94.5, and ifbench_64 is left out of both. See also finding 9.
    **Fix:** list these, or narrow the statement to "nothing else in run.md, numbers.md or the plain summary".

## Checked and found correct

- **(a) 284 / rule 5: the review's reading is right.**
  - The rule-5 text in `olmo_ifomega/handcheck_rule_if.md` matches the review's reading. It says that for `repeat:repeat_span` "an answer that is exactly that string is **genuine**" and names "b9's ifbench_284 / 287 span copies".
  - IFBench `RepeatSpanChecker.check_following` passes only if `value.strip().lower()` equals the whitespace-split span. ifbench_284 has only that instruction, with span [3, 6] = "code and theory behind". So every strict pass is an exact span copy, including rank 3 (c0.14), which the reviewer's readers did not read.
  - The executor labelled all 4 gamed (`handcheck.csv` h6b7206, h588b50, h6f43aa, h9da2ca), against its own rule 5.
- **(b) perp_069 baseline holds.**
  - `review_olmo-ifomega.md` C1 and R7: `dpo` 069 is "dpo_resolved" under union and "reach" under doubly, with 2 / 2 / 2 `rl`-credited responses read sound.
  - `out/phase2_checks.txt` §9: `dpo` 069 has omega 0 and rl 2 in 256; the credited draws are E1_dpo_oo3 c1.4 (30,198 tokens, stop) and c4.28 (cut).
  - The predecessor's "draw 69 / draw 237" map exactly to c1.4 / c4.28 (fixed phase of 16, then E1 chunks of 48).
- **(c) `s2300` hinted vs unhinted strict rates reproduce** from `olmo_ifomega/results.csv` (succ_fixed_strict / n_fixed = 8; succ_strict / attempts = 24). Below the fixed phase on 2: 179 (10/16 < 6/8) and 2563 (15/16 < 8/8). Below all draws on 6: 170, 179, 188, 1314, 2447, 2563.
- **(d) The status of the 52 sums to 52** in both variants:
  - 1 + 2 + 1 (204) + 16 + 2 + 4 + 20 + 5 + 1;
  - 21 / 4 with 170 unbroken.
  The categories match `out/outcomes.json`: uninformative 0, 1, 4, 188; inconclusive 3, 166, 136, 211; 226 counted as prompt-elicitable.
- **(e) The §12 expectation rows agree with the prereg** wording and intervals, except as noted in findings 2, 14, 15 and 16.
- **(f) Hand-gate volumes reproduce** from the reader_labels and keys:
  - first-reader IF items: 377 = 274 + 44 + 52 + 7, plus 9 OMEGA;
  - double reads: 302 = 293 B + 7 round-4 + 2 OMEGA, of which 287 agree (95.0 %);
  - 15 phase-1 disagreements, 14 gamed and 1 genuine;
  - final counts: 390 read once or more, 316 twice or more, 13 three times, 20 first/second disagreements (18 gamed, 2 genuine), all in confirm.json;
  - every deciding item in the final walk has ≥ 2 reads.
- **Re-grade and provenance numbers reproduce:**
  - the §3 table (all eight jobs: strict, loose, cut, no `</think>`);
  - the §4 table (cuts, quartiles, credits, sound counts);
  - the §5 and §6 tables and lists, §7 (790 loose; 3 cuts on 248), and the §8 table (17 unconfirmed);
  - "46 %" ≤ 60 words (0.462) and "13 of 16" ≤ 80 words;
  - the 12,816-row invariants (length iff n_tok == max_tokens, EOS on every stop row, text == decode);
  - seeded subsets (with 281 kept in test 3's pool of 33);
  - the T3 stop file is empty; T1 max_model_len is 65536; the pod logs record the revisions 97604023 / 97ade57a / 418fb274.
- **Compute and spend reproduce:**
  - 12,816 samples, 66,591,208 tokens and 44,036 GPU-s;
  - pod time 46,580 GPU-s, so the gap is 2,544 GPU-s (5.5 %);
  - spend $53.87 = $23.08 + $30.79;
  - 56 registry rows.
- **Executor comparisons reproduce:**
  - `results.csv` vs re-grade: 0 differences; all compared columns are present;
  - hand join: 368 / 336 / 315 agree / 21 disagreements, of which 20 are `s2300` plus T2c `dpo` 220;
  - CP intervals and the 16-of-43 `s0750` before-count.
- **Prereg history and executor quotes check out:**
  - the prereg's original sections are unchanged after 048ef5fe; 2c (a9b234f1) precedes T2c;
  - the executor never reports the gamed-share expectation (grep of run, numbers, plain, summary_tables, README, log);
  - the quoted 226 / strict-rate / plain / status-line texts match their sources;
  - the four `rl`-only OMEGA write-ups do stop mid-sentence after `</think>` (item texts spot-checked).
