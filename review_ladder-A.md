# Review of run ladder-A (RL technique ladder, Phase A, rungs T1–T6)

Reviewer: agent:claude, role reviewer, a different session from the executor. Started 2026-09-18 18:30 UTC.

## Recount (phase 1 — written and committed before I read the executor's write-ups)

Workspace: `~/review/ladder-A` (the executor's `run*.md`, `numbers.md`, `STATUS*.md` removed). `ladder.md`, `log.md` and
`QUESTIONS.md` were still present in that copy — their names do not match the removal patterns. I did not open them, nor
`artifacts/ladder/summary.json*` (the executor's analysis output), in phase 1. I read the brief, the pre-registration,
`data/ladder/POOLS.md`, the driver `ladder_ei.py`, `ladder_inject.py`, and the raw artefacts.

My code (repo root): `rv_recount.py` (own start-index normaliser, line and depth counters, L*, Wilson interval, per-round union
over T6 siblings), `rv_labelcheck.py` (label upper bounds), `rv_reach.py` (reachability classification + my own teacher-forced
scorer), `rv_disjoint.py` (own renaming-class key = lexicographic minimum over the 24 atom permutations; a second, stronger key
also sorts the premises; training-mix provenance). Only `nd_verify`, and for re-scoring `model.py` / `tokenizer.py`, are
imported. Outputs: `review_out/`.

### Hard constraints
| check | result |
|---|---|
| `nd_verify` equals `origin/main` | yes: tree `9437bb72` on both; `verify.py` sha256 `5dc502c2…` in the worktree, in the review copy and in `origin/main` |
| `artifacts/TEST_RUN_DONE` unchanged | yes: blob `1d5cf064` on `origin/main` and `HEAD`; no commit on the run branch touches it, `test_run_once.sh` or `score_test.py` |
| evaluation files read in training code | none. `grep` for `test_long` / `test_short` / `reference_proofs` hits only `score_test.py`, `audit_test_overlap.py`, `eval_targets.py`, `try_proof.py`, `eval_val36_rounds.sh` (none is called by `ladder_ei.py`, `ladder_inject.py`, `train.py`, `pod/la/*.sh`). `ladder_ei.py` reads the transfer pool, held-out and validation-36 only to *sample/evaluate* and to build the exclusion set `eval_keys` |
| cap 6 on supervised data | holds: in every arm's `mix_1..8.jsonl`, every record that is not a model-written target proof or a model-written relabelled by-product is a Stage-1 training record or a T5 injection record, and the longest of those is 6 lines (my line counter) |
| hand-/LLM-written training proofs | none found: every distinct non-Stage-1 record in every mix (2,986–5,770 per arm) verifies with `nd_verify` (0 rejections) and is, byte-for-byte or after start-index normalisation (T6: 582–636 records per sibling differ from `found_union_8` only in start index), a proof in that arm's found set, its `relabelled_*.jsonl`, or its `inject_records.jsonl`. No pool `gen_proof` appears in any mix |
| gate 0 | `preregistration/ladder-A.md` committed 01:14 UTC (`b3845eb`), pools 01:33 (`fb7036c`), amendment (target pool v2) 01:40 (`4cfbf6e`; the text says "01:50"), earliest counted arm `args.json` 01:42:53. The amendment followed a killed round 1 on the v1 target pool and is disclosed; transfer pool and predictions were not changed |

No hard-constraint violation. No quarantine.

### Verification
Every counted proof at round 8, in every arm and both pools, was re-run through `nd_verify` against the pool's prompt (not
the prompt stored with the proof; they agree): 12,515 transfer + 46,471 target records in total (T6 siblings read separately), **0 rejections, 0 prompt
mismatches**, and the verifier's line count equals my line counter on every proof. (Far more than the required 100 per arm.)

### Counts, L*, attempts (round 8; T6 = union of its two siblings)
| arm | attempts/thm | transfer solved /2285 | distinct proofs | L* transfer (labels / corrected) | solved at L_true ≥ 8 / ≥ 9 / ≥ 10 / ≥ 11 | targets solved /4495 | distinct | L* targets | targets ≥ 9 / ≥ 10 / ≥ 11 |
|---|---:|---:|---:|---|---|---:|---:|---:|---|
| frozen_s0 | 256 | 22 | 24 | 7 / 7 | 2 / 0 / 0 / 0 | 426 | 544 | 8 | 0 / 0 / 0 |
| frozen_s1 | 256 | 24 | 26 | 7 / 7 | 3 / 0 / 0 / 0 | 408 | 532 | 8 | 0 / 0 / 0 |
| T1_s0 | 256 | 612 | 836 | 10 / 10 | 472 / 335 / 35 / 1 | 2400 | 3114 | 10 | 326 / 24 / 1 |
| T1_s1 | 256 | 623 | 868 | 10 / 10 | 484 / 346 / 34 / 0 | 2455 | 3296 | 10 | 364 / 31 / 0 |
| T2_s0 | 256 | 643 | 892 | 10 / 10 | 495 / 362 / 39 / 1 | 2486 | 3113 | 10 | 363 / 37 / 2 |
| T2_s1 | 256 | 635 | 897 | 10 / 10 | 494 / 354 / 37 / 1 | 2506 | 3146 | 10 | 372 / 40 / 1 |
| T3_s0 | 256 | 669 | 972 | 10 / 10 | 529 / 390 / 47 / 1 | 2507 | 3425 | 10 | 399 / 44 / 2 |
| T3_s1 | 256 | 601 | 811 | 10 / 10 | 462 / 328 / 26 / 0 | 2407 | 3181 | 10 | 335 / 26 / 1 |
| T4_s0 | 256 | 632 | 888 | 10 / 10 | 495 / 357 / 43 / 2 | 2383 | 3016 | 10 | 353 / 33 / 3 |
| T4_s1 | 256 | 605 | 840 | 10 / 10 | 459 / 327 / 31 / 1 | 2353 | 3013 | 10 | 336 / 21 / 0 |
| T5_s0 | 256 | 627 | 879 | 10 / 10 | 489 / 351 / 37 / 2 | 2448 | 3287 | 10 | 356 / 30 / 1 |
| T5_s1 | 256 | 648 | 952 | 10 / 10 | 510 / 368 / 35 / 0 | 2453 | 3363 | 10 | 359 / 29 / 1 |
| T6_s0 | 256 | 694 | 1038 | 10 / 10 | 556 / 409 / 46 / 1 | 2537 | 3424 | 10 | 399 / 41 / 3 |
| T6_s1 | 256 | 680 | 998 | 10 / 10 | 536 / 395 / 42 / 1 | 2535 | 3467 | 10 | 404 / 41 / 2 |

- Attempts: `alloc_8.json` gives exactly 1,150,720 target samples per arm (= 4,495 × 256; 143,840 every round); T1/T3/T5/frozen
  256 per target; T2 32–579 and T4 155–767 per target (reallocation, same total); T6 2 × 128. Transfer: 8 × 32 (T6: 8 × 2 × 16).
  Frozen control is at equal attempts.
- **L\* = 10 on transfer and on targets for all twelve trained arms; frozen L\* = 7 on transfer (both seeds), 8 on targets.**
  `L* − L*_frozen` = **+3** on transfer for every rung on both seeds.
- L\* by round on transfer: 7, 8, 9, 9, 10, 10, 10, 10 for most arms (T3 s0, T5 s1, T6 s0 reach 10 in round 4; T3 s1 in round 6).
  The count at `L_true` ≥ 10 is **still rising at round 8 in every arm** (T1 s0: 2, 12, 23, 27, 35 over rounds 4–8); nothing has plateaued.
- Acquisition over the frozen control (transfer theorems solved by the arm and by neither frozen seed, 512 frozen attempts, 25 solved):
  T1 588 / 598; T2 619 / 610; T3 645 / 578; T4 608 / 581; T5 603 / 625; T6 669 / 655. Theorems the frozen model solved that the arm did not: 0–2.

### Transfer solve rate by `L_true` bin (solved = rate [Wilson 95 %])
| arm | L_true 7 (n=300) | 8 (n=300) | 9 (n=1010) | 10 (n=451) | 11 (n=99) | 12–14 (n=125) |
|---|---|---|---|---|---|---|
| frozen_s0 | 20 = 6.7 % [4.4, 10.1] | 2 = 0.7 % [0.2, 2.4] | 0 = 0.0 % [0.0, 0.4] | 0 = 0.0 % [0.0, 0.8] | 0 = 0.0 % [0.0, 3.7] | 0 |
| frozen_s1 | 21 = 7.0 % [4.6, 10.5] | 3 = 1.0 % [0.3, 2.9] | 0 = 0.0 % [0.0, 0.4] | 0 = 0.0 % [0.0, 0.8] | 0 = 0.0 % [0.0, 3.7] | 0 |
| T1_s0 | 140 = 46.7 % [41.1, 52.3] | 137 = 45.7 % [40.1, 51.3] | 300 = 29.7 % [27.0, 32.6] | 34 = 7.5 % [5.4, 10.4] | 1 = 1.0 % [0.2, 5.5] | 0 |
| T1_s1 | 139 = 46.3 % [40.8, 52.0] | 138 = 46.0 % [40.4, 51.7] | 312 = 30.9 % [28.1, 33.8] | 34 = 7.5 % [5.4, 10.4] | 0 = 0.0 % [0.0, 3.7] | 0 |
| T2_s0 | 148 = 49.3 % [43.7, 55.0] | 133 = 44.3 % [38.8, 50.0] | 323 = 32.0 % [29.2, 34.9] | 38 = 8.4 % [6.2, 11.4] | 1 = 1.0 % [0.2, 5.5] | 0 |
| T2_s1 | 141 = 47.0 % [41.4, 52.6] | 140 = 46.7 % [41.1, 52.3] | 317 = 31.4 % [28.6, 34.3] | 36 = 8.0 % [5.8, 10.9] | 1 = 1.0 % [0.2, 5.5] | 0 |
| T3_s0 | 140 = 46.7 % [41.1, 52.3] | 139 = 46.3 % [40.8, 52.0] | 343 = 34.0 % [31.1, 36.9] | 46 = 10.2 % [7.7, 13.3] | 1 = 1.0 % [0.2, 5.5] | 0 |
| T3_s1 | 139 = 46.3 % [40.8, 52.0] | 134 = 44.7 % [39.1, 50.3] | 302 = 29.9 % [27.2, 32.8] | 26 = 5.8 % [4.0, 8.3] | 0 = 0.0 % [0.0, 3.7] | 0 |
| T4_s0 | 137 = 45.7 % [40.1, 51.3] | 138 = 46.0 % [40.4, 51.7] | 314 = 31.1 % [28.3, 34.0] | 41 = 9.1 % [6.8, 12.1] | 2 = 2.0 % [0.6, 7.1] | 0 |
| T4_s1 | 146 = 48.7 % [43.1, 54.3] | 132 = 44.0 % [38.5, 49.7] | 296 = 29.3 % [26.6, 32.2] | 30 = 6.7 % [4.7, 9.3] | 1 = 1.0 % [0.2, 5.5] | 0 |
| T5_s0 | 138 = 46.0 % [40.4, 51.7] | 138 = 46.0 % [40.4, 51.7] | 314 = 31.1 % [28.3, 34.0] | 35 = 7.8 % [5.6, 10.6] | 2 = 2.0 % [0.6, 7.1] | 0 |
| T5_s1 | 138 = 46.0 % [40.4, 51.7] | 142 = 47.3 % [41.8, 53.0] | 333 = 33.0 % [30.1, 35.9] | 35 = 7.8 % [5.6, 10.6] | 0 = 0.0 % [0.0, 3.7] | 0 |
| T6_s0 | 138 = 46.0 % [40.4, 51.7] | 147 = 49.0 % [43.4, 54.6] | 363 = 35.9 % [33.0, 38.9] | 45 = 10.0 % [7.5, 13.1] | 1 = 1.0 % [0.2, 5.5] | 0 |
| T6_s1 | 144 = 48.0 % [42.4, 53.6] | 141 = 47.0 % [41.4, 52.6] | 353 = 35.0 % [32.1, 37.9] | 41 = 9.1 % [6.8, 12.1] | 1 = 1.0 % [0.2, 5.5] | 0 |

### Base reachability (transfer)
| arm | counted transfer proofs | scored by executor (missing) | p ≥ 1e-5 at L_true 7 | at 8 | at ≥ 9 | p ≥ 1/256 at 7 / 8 / ≥ 9 | proofs at L_true ≥ 10 using ORE/NEGI/NEGE/BOTE |
|---|---:|---:|---|---|---|---|---|
| frozen_s0 | 24 | 24 (0) | 22/22 | 2/2 | 0/0 | 18 / 2 / 0 | 0/0 |
| frozen_s1 | 26 | 26 (0) | 23/23 | 3/3 | 0/0 | 19 / 2 / 0 | 0/0 |
| T1_s0 | 836 | 836 (0) | 75/176 | 5/187 | 0/473 | 20 / 2 / 0 | 0/51 |
| T1_s1 | 868 | 868 (0) | 70/163 | 7/195 | 0/510 | 20 / 2 / 0 | 0/59 |
| T2_s0 | 892 | 892 (0) | 68/175 | 5/186 | 0/531 | 20 / 2 / 0 | 0/58 |
| T2_s1 | 897 | 897 (0) | 71/170 | 5/198 | 0/529 | 20 / 2 / 0 | 0/64 |
| T3_s0 | 972 | 972 (0) | 70/169 | 6/201 | 0/602 | 19 / 2 / 0 | 0/83 |
| T3_s1 | 811 | 811 (0) | 69/162 | 5/180 | 0/469 | 18 / 2 / 0 | 0/44 |
| T4_s0 | 888 | 888 (0) | 68/160 | 6/193 | 0/535 | 19 / 2 / 0 | 0/74 |
| T4_s1 | 840 | 840 (0) | 69/170 | 4/181 | 0/489 | 19 / 2 / 0 | 1/54 |
| T5_s0 | 879 | 879 (0) | 71/166 | 7/197 | 0/516 | 19 / 2 / 0 | 0/55 |
| T5_s1 | 952 | 952 (0) | 69/172 | 7/212 | 0/568 | 19 / 2 / 0 | 0/58 |
| T6_s0 | 1038 | 1038 (0) | 73/171 | 7/217 | 0/650 | 20 / 2 / 0 | 0/82 |
| T6_s1 | 998 | 998 (0) | 75/176 | 7/203 | 0/619 | 20 / 2 / 0 | 1/65 |


- The executor's `novelty_proofs.jsonl` covers exactly my counted (theorem, normalised proof) set in every arm (0 missing, 0 extra).
  I classified from its `base_logp_T08` with my own thresholds, and **re-scored 1,370 proofs (≈ 100 per arm, random) with my own
  scorer** (CPU fp32, sum over all admissible start shifts, logits / 0.8): same number of shifts on all 1,370; |Δ log p| median 0.10,
  p99 0.88, max 1.28 nats (on log p ≈ −130); one classification flip, a proof at log p = −11.49 vs −11.53 (the line is −11.51). Reproduces.
- **Every counted transfer proof at `L_true` ≥ 9 has base p < 1e-5 (100 %, all arms)**; at `L_true` 7, 40–44 % of proofs are ≥ 1e-5.
- The direct reachability number (frozen control, equal attempts): at `L_true` ≥ 9 the base model solves **0 / 1,685 transfer theorems in
  2 × 256 attempts** (per-theorem Wilson upper bound for the 9-bin 0.4 %), and 2–3 / 300 at 8.

### What the solved long theorems are (own predicates)
- **Every solved transfer theorem with `L_true` ≥ 9 is a generator theorem.** Of the 760 textbook-schema theorems, every arm solves
  81–94, and these are contraposition (40/40) + export (39–40/40), both `L_true` 7, plus 0–5 others. 17 of the 19 schemata are at
  ≈ 0 in every arm, trained or not.
- **Rule family.** Counted transfer proofs at `L_true` ≥ 10 that use any of ORE / NEGI / NEGE / BOTE: **0 in ten arms, 1 in two arms**
  (of 44–83 proofs per arm). They are implication towers (AS/IMPI at depth 3–4) around ANDI / ORI / IMPE steps. At `L_true` 9: 5–23
  of 422–568 proofs; at 7: ≈ 37 %. Generator theorems at `L_true` 10 whose generating proof uses NEGI: 0/48 solved (T1 s0, T6 s0).
  So "L\* = 10" is a statement about one proof family getting longer, not about the pool's `L_true`-10 bin in general.

### `L_true` labels: some are wrong (overestimates), L\* unaffected
`minlen.py` never considers eliminating `( A v A )` with one box cited twice (`ORE Nj Ns Ne Ns Ne`, which the verifier accepts).
Five arms wrote such proofs with **fewer lines than `L_true`**; by merging duplicate ORE boxes in counted proofs and re-verifying
(`rv_labelcheck.py`) I get verified shorter proofs for **18 of the 818 transfer theorems ever solved and 58 of the 2,787 targets ever
solved** (all off by one: 7→6, 8→7, 9→8; 3 of them written directly by the model at 9→8 without an ORE merge). None is labelled ≥ 10.
With corrected labels L\* is unchanged in every arm (table above, "corrected"); bin counts move by ≤ 9 theorems. This is a lower
bound on label errors — only solved theorems can be checked this way — and `POOLS.md`'s caveat (restricted formula space) does not
cover it: these shorter proofs use only subformulas of the theorem.

### Split disjointness (own keys)
- Pre-registered notion (renaming class, premise order kept): **0 overlaps** between every training file (Stage-1 train, `rl_targets`,
  every arm's `mix_*`, `relabelled_*`, `inject_records`) and every evaluation pool (ladder transfer, held-out, validation-36, take-home
  transfer); `rl_targets` × ladder transfer 0; ladder transfer × Stage-1 train 0.
- Stronger key (premises also sorted): `rl_targets` × ladder transfer **2** classes (neither is in any arm's training mix × transfer
  overlap, which is 0); Stage-1 train × held-out 95, × validation-36 1, × take-home transfer 2 — these pre-date this run. Negligible for
  any number here (2 / 2,285), but the pools are disjoint "by renaming class with premise order fixed", not up to premise permutation.
- T3 relabelled by-products: 55 per seed by round 8, all ≥ 7 lines, all verify, none in an evaluation class. T5 injection: 2,505 / 2,509
  records, all ≤ 6 lines, all verify, none in an evaluation class.

### Other quantities the pre-registration promised
- Held-out greedy: 94.76–95.94 % in every round of every arm (`round_*.json`; raw generations are not saved, so this is read, not re-derived).
- T3 solve at 8: 46.3 % / 44.7 % vs T1 45.7 % / 46.0 % (within ± 5 points).
- T5 textbook-schema solve rate on transfer: 11.2 % / 10.8 % vs T1 10.9 % / 10.9 %.

### Things I noticed that bear on interpretation
1. **T3 is almost T1.** 55 relabelled records against ≈ 3,400 target proofs in the mix (< 2 % of the RL part). T3's two seeds therefore
   behave like two further T1 runs, and they span 601–669 transfer theorems solved (328–390 at ≥ 9; 26–47 at ≥ 10). That range
   contains T1, T2, T4 and T5 on both seeds. Only T6 (680 / 694; 395 / 409 at ≥ 9) lies outside it, and its margin over the best
   T1-like arm (T3 s0) is 11–25 theorems.
2. **T6 is not only an evaluation-time ensemble.** Each T6 sibling *alone*, with 128 transfer attempts, solves 636–657 (357–376 at
   ≥ 9) — more than T1 with 256 attempts (612 / 623; 335 / 346). For scale, T1 s0 ∪ s1 (512 attempts, two models) solves 667.
   T6 uses twice the training compute (two models × 600 steps per round).
3. Same-seed arms do not share round 1: seed-0 arms split into {T1, T2} and {T3, T4, T5, frozen} with different round-1 samples from the
   same checkpoint and seed (3,768 vs 3,716 accepted; base greedy 94.78 vs 94.76 %) — different pods / kernels. Harmless, but
   "same seed" does not mean paired.
4. **T3 s0 was resumed** (rounds 6–8 on 18 Sep 17:55–18:20 after a crash in `relabel`, `la_T3_s0.crash_r6.log`). The resume restarts the
   Python RNG, so rounds 6–8 replay ≈ 95 % of the Stage-1 retention samples of rounds 1–3 (19,384 / 18,791 / 18,212 of 20,000
   identical); T3 s0 saw 77.8k distinct Stage-1 records against ≈ 103.6k in every other arm. The relabelled set and found sets were
   restored correctly (49 → 55 relabelled; checkpoint `r5`). T3 s0 is the best single-model arm, so this did not hurt it, but it is
   not protocol-identical to T3 s1.
5. Frozen at `L_true` 7 is 6.7–7.0 % because 236 of the 300 transfer theorems in that bin are textbook instances the base model cannot write.

---

## Compare (phase 2 — after reading `run_ladder_A.md`, `ladder.md`, `numbers.md` §ladder-A, `log.md` §ladder-A, `STATUS.md`, `QUESTIONS.md`)

Erratum to my §Recount: "at `L_true` 7, 40–44 % of proofs are ≥ 1e-5" should read **38.9–42.9 % of proofs** (68/175 … 70/163); per
*theorem* (best counted proof) it is 36.5–42.4 %. The table was right; the sentence was not.

| # | executor's claim (source) | my independent value | verdict |
|---|---|---|---|
| 1 | Transfer `L*` = 10 for T1–T6 on both seeds; frozen 7; +3 everywhere (`run_ladder_A.md`, `ladder.md`, `numbers.md`) | 10 × 12 arms; frozen 7 / 7; also with my corrected labels | **reproduces** |
| 2 | Target-pool `L*`: trained 10 / 10, frozen 8 / 8 | same | reproduces |
| 3 | Transfer / targets solved, thms at ≥ 8 / 9 / 10 / 11, every row of the `ladder.md` main table incl. T6 single siblings (644, 657, 636, 642; 371, 376, 357, 366 at ≥ 9) | identical in all 18 rows | reproduces |
| 4 | Transfer and target bins with Wilson intervals (`ladder.md`) | identical counts; my Wilson bounds agree to the printed digit | reproduces |
| 5 | "≤ 2 of 99 transfer theorems at `L_true` 11, none of 125 at 12–14, in any arm" | max 2/99 (T4 s0, T5 s0); 0/125 everywhere | reproduces |
| 6 | "T4 spent 706 samples on each of 221 targets at `L_true` 11–13 and solved 3 and 0"; T2 351 / 2 and 1; T1 256 / 1 and 0 | 156,014 / 221 = 706, solved 3 (s0), 0 (s1); T2 s0 77,490 → 351, 2; T1 s0 1 | reproduces |
| 7 | T6 beats T1 on both seeds at ≥ 9: 409 / 395 vs 335 / 346; siblings alone 357–376 at half the attempts | same | reproduces |
| 8 | "paired p < 0.001 twice" (T6 vs T1, exact sign test; `ladder.md` paired table) | 88 / 14 and 72 / 23, p < 0.001; T1 s1 vs s0 44 / 33, p 0.25 — all reproduce. **But the same test gives T3 s0 vs T1 s0 73 / 18, p < 0.001 and T3 s1 vs T1 s1 27 / 45, p 0.044**, and T3 is T1 plus 55 records | numbers reproduce; **the inference does not hold** — the test's unit is the theorem, the noise is the training run. It rejects "these two checkpoints are equal", not "T6 = T1" |
| 9 | Base reachability: 0 of 327–409 transfer theorems solved at ≥ 9 have base p ≥ 1e-5; at 7, 37–42 % (predicted 40–60 %) | 0 of 327–409; 36.5–42.4 % per theorem; my own re-scoring of 1,370 proofs agrees (max 1.28 nats, 1 flip at the line) | reproduces. The 7-bin is a **miss at the low edge in 5 of 12 arms' terms** (range straddles 40 %); the write-up lists it without a verdict |
| 10 | Frozen: 7 % at 7 (predicted 25–35 %) — listed under "held" because `L*` = 7 held | 6.7 / 7.0 % | reproduces; the **rate prediction is a miss** and should be labelled so (cause: 236 / 300 of the bin are textbook instances) |
| 11 | T1 prediction wrong (10, not 9); headline "no rung reaches +3" wrong; T2 / T4 target `L*` prediction wrong; T5 + 5 points wrong (85, 82 vs 83, 83) | all as stated; by the pre-registered falsifiers T1, T2, T3 (transfer `L*` ≥ 10 on both seeds), T4 and T6 (same) are falsified, T5's falsifier ("≤ T1's on both seeds") is met on s1 only | reproduces; misses are reported as misses. **T3's and T6's falsified `L*` predictions are not listed** in `run_ladder_A.md` |
| 12 | Held-out greedy ≥ 0.953 final round (`numbers.md`: 0.953–0.959; frozen 0.948) | read from `round_8.json`: 0.9532–0.9594; all rounds ≥ 0.9476 | reproduces (not re-derivable: generations not saved) |
| 13 | "all generator-shaped at ≥ 9"; schemata beyond contraposition / export unsolved; no schema instance with `L_true` ≥ 9 solved | same (0 textbook at ≥ 9 in every arm; 79–80 of 80–94 textbook solves are those two schemata) | reproduces |
| 14 | 42 (run summary, `numbers.md`) / 43 (`ladder.md`) labels one line too long; `L*` unchanged | 43 by written proofs (13 transfer + 30 targets); **76** (18 + 58) when duplicate ORE boxes in counted proofs are merged and re-verified; `L*` unchanged | differs in count (42 vs 43 internally; 76 by my stronger check), same conclusion |
| 15 | T3 by-products "≈ 50"; `numbers.md`: "49 (s0) and 55 (s1)"; `ladder.md`: 55 and 55 | 55 and 55 at round 8 | `numbers.md` is stale by 6 for s0 (49 was round 6); immaterial |
| 16 | T3 s0's lead predates the resume (≥ 9 at round 5: 240 vs 204) | 240 vs 204 | reproduces |
| 17 | Log 18:00: "the only difference from an uninterrupted run is the Python `rng` stream used to shuffle the training mix" | the restarted stream also re-draws the 20,000 Stage-1 retention records: rounds 6–8 repeat 97 / 94 / 91 % of rounds 1–3's | **understated**, effect on results unknown but probably small |
| 18 | "Run-to-run spread (round-3 counts 16–58)" | 16–59 with the T6 union (58 without) | reproduces |
| 19 | Cost ≈ $39 (≈ $7.5 productive, ≈ $31.6 idle) | `~/pods.log` creation times to 17:20 at $0.50/h: 78.1 pod-h = $39.1 + $0.25 | reproduces as an estimate; the deletion time comes from the resume note, not a file |
| 20 | Gate 0: expectations committed before the first pod | `b3845eb` 01:14 < first `args.json` 01:42:53; amendment `4cfbf6e` 01:40 (text says 01:50) changes the training pool only and was made after a killed round 1 on it, as disclosed | holds |
| 21 | Bucket paths in `numbers.md` | not checked (no listing pulled); out of scope of the recount | not derived |

### Wording against n
- **"The wall is at 11" / "do not move the wall" / "beneath it"** (`run_ladder_A.md`; "wall at `L_true` 11" in `STATUS.md`). Not supported as
  worded. Evidence for: 8 rounds, 0–2 of 99 at 11, T4's 706 samples per target for 0–3 solves. Evidence against calling it a wall: the
  count at ≥ 10 is still rising every round in every arm at round 8 (T1 s0 2 → 12 → 23 → 27 → 35); each earlier length went from 0–2
  solved to ≥ 5 within one or two rounds of first appearing (10: round 4 → round 5); the Wilson upper bound at 11 is 5.5–7.1 %; and
  the executor's own Phase B proposal (a) is to find out "whether the wall at 11 is a rate limit or a hard limit". What the data say is
  **"no arm reaches 11 in 8 rounds"**.
- **"two seeds rank nothing except T6"**. The T6 ranking satisfies the standing two-seed rule (both T6 seeds above both T1 seeds in
  total, ≥ 8, ≥ 9, ≥ 10 — I checked each). But the reference noise the write-up itself identifies (T3 ≈ T1: 328 and 390 at ≥ 9) puts
  T6 (395, 409) 5–19 theorems above the best T1-like run. Treating T1 s0, T1 s1, T3 s0, T3 s1 as four T1-like runs (335, 346, 390,
  328; mean 350, sd 28) against T6's two (mean 402): pooled-variance t = 2.45 on 4 df (p ≈ 0.07); Welch t = 3.35 on ≈ 4 df (p ≈ 0.03),
  with T6's variance estimated from two runs, and with "T3 counts as T1" being my post-hoc assumption. **"T6 is ahead on both
  seeds; likely but not established"** is what n supports. The single-sibling result (each sibling alone, at 128 attempts, beats T1 at 256) is the
  stronger piece of evidence and deserves the prominence the p-values now have.
- Not said anywhere in the executor's files and needed by a reader: **T6 trains two models, i.e. twice the gradient steps per round**, and
  its pod time is 111 vs 65–93 min. "Equal sample budget" is true; "equal compute" is not.
- "Plain EI moves a never-trained frontier three lines past what 256 frozen samples reach, with proofs the base assigns < 1e-5,
  all generator-shaped at ≥ 9" — every part reproduces. It omits what my rule-family predicate shows (§Recount): at `L_true` ≥ 10 the
  counted proofs contain **no ORE / NEGI / NEGE / BOTE at all in ten arms and one such proof in two**; they are AS/IMPI towers around
  ANDI / ORI / IMPE. For the SPAR question this matters more than the rung ranking: the +3 in `L*` is one already-known proof family
  being written longer (depth 3–4 instead of ≤ 3, ≥ 10 lines instead of ≤ 6), while theorems whose generating proof needs NEGI are
  0 / 48 at `L_true` 10 and 17 of 19 textbook schemata stay at 0 under every technique. "Base p < 1e-5" and "same rule family as the
  base model's 6-line proofs" are both true of these proofs; the write-up reports only the first.

## Verdict

**Hard constraints:** all hold (`nd_verify` identical to `origin/main`; `TEST_RUN_DONE` untouched; no evaluation file in training
code; supervised data ≤ 6 lines; every trained-on proof is model-written or generator-written and verifier-accepted). No quarantine.
Every one of the 12,515 + 46,471 counted proof records verifies against its pool prompt. Pools are disjoint by the pre-registered
renaming class from every training file; under premise permutation 2 target classes coincide with transfer classes (neither was
trained on in any arm's mix × transfer intersection) — worth fixing in the key for the next pools, immaterial here.

**What stands**
- Every count, rate, interval, `L*`, reachability figure and budget figure in `ladder.md` / `numbers.md` §ladder-A reproduces from the
  raw files with independent code. The executor's bookkeeping is clean.
- Transfer `L*` 10 vs frozen 7 at equal attempts, on both seeds, for every rung; no rung differs from T1 in `L*`. Frozen solves 0 of
  1,685 transfer theorems at `L_true` ≥ 9 in 2 × 256 attempts; no solved theorem at ≥ 9 has a counted proof with base p ≥ 1e-5.
- T2, T3, T4, T5 are not distinguishable from T1 with two seeds; the executor says so.
- The pre-registered misses (T1, headline, T2 / T4 targets, T5) are reported as misses; expectations were committed before the first pod.

**What must be reworded**
1. "The wall is at 11", "do not move the wall", "beneath it", and `STATUS.md`'s "wall at `L_true` 11" → "no arm reaches 11 within 8
   rounds (≤ 2 / 99); counts at 10 were still rising when the runs stopped".
2. Drop "paired p < 0.001 twice" as support for T6 (row 8), or add next to it that the same test gives p < 0.001 for T3 s0 over T1 s0
   and p = 0.04 for T1 s1 over T3 s1. Replace with: both T6 seeds exceed both T1 seeds in every bin ≥ 8; each sibling alone at 128
   attempts exceeds T1 at 256; margin over the best T1-like run is 5–19 theorems at ≥ 9; T6 uses 2 × the training compute.
3. "Frozen `L*` 7: held (7 % solved at 7; predicted 25–35 %)" → `L*` held, rate prediction missed. Add T3's and T6's falsified transfer-`L*`
   predictions (both pre-registered "9", falsifier "≥ 10 on both seeds" met) to the expectations list. Give the `L_true`-7 elicitation share a verdict
   (36.5–42.4 % vs predicted 40–60 %: low edge).
4. Label errors: 42 / 43 → say which; my merge check finds 76 among solved theorems, and the unsolved ones cannot be checked this way.
5. `log.md` 18:00 on the T3 s0 resume: the restarted RNG also repeats > 90 % of rounds 1–3's Stage-1 retention draws in rounds 6–8.
6. `numbers.md`: T3 s0 by-products 49 → 55.

**What is not supported**
- A length wall, in the sense of a limit that more rounds would not move.
- T6 > T1 as an established technique effect (it is the run's best lead, not its finding).
- Nothing in the run supports reading "+3 lines of `L*`" as new *kinds* of proof: by my predicates the gain is confined to the
  implication-tower family on generator-shaped theorems. The executor does not claim otherwise, but the interpretation paragraph
  ("with proofs the base assigns < 1e-5") invites that reading and should carry the rule-family fact beside it.

**Next measurements that would settle what is open**
1. *Rate limit or wall:* T1 continued to 16–24 rounds from the existing round-8 checkpoints (2 seeds exist; add 2), reporting solved
   counts at 10, 11, 12 per round. Prediction to write down first: if 11 behaves like 10 did, ≥ 5 at 11 appears within ≈ 2–4 more
   rounds. Cheap (≈ 8 min per round per arm on a 3090).
2. *Is T6 real and why:* 4 seeds each of T1 and T6, plus the executor's proposed control (one policy trained on the union of two
   independent samplers' finds, which equalises training compute per model and removes the second policy), plus T1 with 1,200 steps
   per round (equal total compute).
3. *Length vs kind:* report every frontier number split by rule family (implication-tower vs uses ORE / NEGI / NEGE / BOTE), and
   compute `L*` on the second family alone — from the existing files that is a re-analysis, no pods. My count says it will be 9 in
   every arm (5–21 such theorems at 9, i.e. 0.5–2 % of the bin against 30–36 % overall; ≤ 1 at ≥ 10), against frozen's 7. That — +2 on a
   handful of theorems, not +3 on hundreds — is the size of the gain on the harder family. (The predicate is on the written proof: a
   proof that uses ORE need not need it.)
4. Fix `minlen.py` to try `ORE` with one box cited twice, relabel, and make the class key premise-order-invariant before building
   Phase B pools.

Reviewer finished 2026-09-18 UTC. Files: `review_ladder-A.md`, `rv_recount.py`, `rv_labelcheck.py`, `rv_reach.py`, `rv_disjoint.py`, `review_out/`.
