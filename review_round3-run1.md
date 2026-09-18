# Review of round3-run1 (pool composition or pattern class?)

Reviewer session, independent of the executor. Phase 1 (§Recount) was written from the run brief
(`BRIEF_pool-composition.md`), `preregistration/round3-run1.md` (commit 8c318e7 + the 05:50 amendment), the code,
the data and the raw artefacts in `~/review/round3-run1` only. No executor write-up was read before §Recount was
committed. Two things in the phase-1 workspace were *not* removed by the driver's glob and I did not open them:
`round3_run1.md` (the glob is `run*.md`) and `artifacts/r3_1/summary.json`. Two executor-derived files I did see
while listing artefacts: `artifacts/r3_1/zero_rate_draws.json` (the zero-rate seed lists) and
`artifacts/r3_1/pools_summary.json` (overlap zeros and pool length histograms); the commit subject "n0 = 6 depth-3,
5 reductio" was also in my session context. All three are recomputed below from the raw files.

All counts come from my own code: `review_r3_1_recount.py`, `review_r3_1_extra.py`, `review_r3_1_tables.py`, which
use the reviewer-owned parser, dependency pruning, start-index normaliser, reductio predicate, box-depth counter
and renaming key of `review_run5_recount.py`. Only `nd_verify` is shared with the executor. Machine-readable
outputs: `artifacts/review_r3_1/*.json`.

## Recount

### Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | blob hashes of `nd_verify/verify.py` (1cfed53) and `nd_verify/__init__.py` (dfa3bc3) equal `origin/main`'s, in the worktree and in the phase-1 copy |
| `artifacts/TEST_RUN_DONE` | no diff against `origin/main`; last touched by ca93f83 (Sep 15 07:38); no test file is named in any `pod/r3_1/` job line |
| evaluation files in training code | `train.py` reads `--data` and `--heldout` (loss monitoring) only; every `expert_iter.py` job line reads the run's target pool, its transfer pool, `data/p2/heldout.jsonl` and the Stage-1 training file; nothing reads `targets/test_*` or `validation_36` |
| cap 6 on supervised data | `train_depth3_f0_a1.jsonl` and `train_reductio_f0.jsonl`: 155,000 proofs each, 31,000 per length 2…6, max 6 lines; all 16 Stage-1 checkpoints carry `cap 6, steps 6000, bs 128, mode abs`, the right data file and seed in `extra.args` |
| pattern absent from Stage-1 data | `train_depth3_f0_a1`: 0 proofs of box depth ≥ 3 (pruned or not; 10,547 strict reductio proofs, irrelevant to that pattern). `train_reductio_f0`: 0 strict reductio, 0 `DN`-of-`NEGI` of any shape (2,586 proofs use `DN`; 5,687 are depth 3) |
| gate 0 | pre-registration committed 05:09:48 UTC; first pod of the run (`r31a`) created 05:16:09 (`~/pods.log`). The amendment is in commit 8d33afe (05:50:37); the earliest reductio `mix` / `drift` `round_1.json` is stamped 06:00:10 |

### Pools (E1)

| pool | n | distinct renaming classes | my checks |
|---|---:|---:|---|
| `depth3_req` | 300 | 300 | `r8_min_lines_ub` null and `r8_timeout` false for all 300; min length 7: 6, 8: 294; every `oracle_proof` verifies and has pruned depth ≥ 3 (one is depth 4); bound-10 depth-≤ 2 alternative: 9 lines **288 (96.0 %)**, 10 lines 1, **none 11 (3.7 %)**, 0 timeouts; all 289 `r10_proof`s verify, depth 2, 9–10 lines |
| `depth3_req_transfer` | 100 | 100 | same fields; 94 with a 9-line alternative, 6 none |
| `depth3_nb` | 300 | 300 | every `nb_proof` verifies with depth ≤ 2 at 7 (178) or 8 (122) lines; unrestricted min 7: 250, 8: 50; all from `targets_depth3` |
| `reductio_req` / `_transfer` | 300 / 150 | 300 / 150 | prompts identical to `data/p2/targets_reductio_req.jsonl` / `transfer_reductio_req.jsonl`; every oracle proof verifies and is strict reductio; **min length 7: 52, 8: 133, 9: 82, 10: 33**; 16 schemata, 11 of them with 26–27 targets |
| `reductio_nb` | 300 | 300 | conclusion `( ~ ( ~ X ) )` 300 / 300; `nodn_proof` verifies, uses no `DN`, closes with `NEGI` of an assumed `( ~ X )` 300 / 300 (27 of them also use `BOTE`); `intuit_provable` true 300; unrestricted min 7: 212, 8: 88; no-DN length 7: 162, 8: 77, 9: 40, 10: 21; the unrestricted shortest proof uses `DN` for 67 targets and is itself a strict reductio for 2 |
| `depth3_mix`, `reductio_mix` | 600 | 600 | exactly `req` ∪ `nb`, prompts equal |

Not re-derived: I did not re-run `minlen.py` (the restricted searches behind `r8_*`, `r10_*`, `nodn_*`); I checked the
recorded proofs and looked for counter-examples in the model output instead — **0 required targets of either pattern
were solved without the pattern by any model** in 227,870 found records, 9.6 M pre-RL samples and 18.0 M
drift-checkpoint samples (0 oracle inconsistencies). Only 87 of the 142 known required@8 targets the pre-registration
started from are in the final pools (67 in `depth3_req`, 20 in transfer); the rest of `depth3_req` (233) are new
`pool_long` candidates.

E1 as I count it: pool sizes and the alternative-length shares are met (300 ≥ 250; 96.0 % ≥ 90 %; 3.7 % ≤ 5 %;
300 reductio neighbours). "Every draw solves ≥ 40 % of the neighbour stratum of its `mix` pool by round 8" holds for
15 of 16 draws: **depth-3 s25 solves 106 / 300 = 35.3 %**; the other depth-3 draws 126–239, the reductio draws
143–182.

### Split disjointness (my renaming key)

0 shared classes between each of `train_depth3_f0_a1`, `train_reductio_f0` and each of the six pools; 0 between any
two pools; 0 between any pool and `data/p2/heldout.jsonl`, `validation_36`, `test_short_prompts`; one class shared by
`reductio_req_transfer` and `test_long_prompts`, and one by `depth3_nb` and `heldout_c8` (neither file is used by
this run). Train × `heldout` = 0. (The two training files share classes with `test_short` — 57 and 51 — as every
cap-6 set of this repository does; no test file is run here.)

### Pre-RL sample, zero-rate classification, arms

Every one of the 227,870 raw records in the 48 arms' `found_8.jsonl` re-verifies with `nd_verify` against the pool's
prompt (0 failures, 0 unknown names, 0 prompt mismatches; 7,322 distinct normalised proofs). `found_<r>` line counts
equal the number of `round ≤ r` records of `found_8` in every arm and round. All 48 `args.json` match the
pre-registered arm settings. Coverage files: my pattern label equals the file's on every stored proof, every stored
proof re-verifies, 300 required targets × 2,000 (pre-RL) or × 1,000 (drift checkpoints) in every file.

**n₀ = 6 of 8 depth-3 draws (s20, 21, 23, 25, 26, 27) and 5 of 8 reductio draws (s20, 21, 22, 23, 25).**
Ignition = ≥ 20 (depth-3) / ≥ 12 (reductio) required targets, cumulative, min-round rule. Frozen control = pre-RL
sample restricted to the first 256 attempts per target (from the per-proof `first` index).

**depth3: pre-RL sample and arms (required stratum = targets with a verified depth-3 proof, cumulative r1…r8)**

| seed | pre-RL hits / 600k (targets) | frozen@256 targets | `req` r1…r8 | `mix` required r1…r8 | ign. round req / mix | `mix` neighbours solved r8 (with pattern) | first pattern proof in `mix`: neighbour / required round | transfer r8 req / mix (of 100) | held-out greedy r8 req / mix / drift (of 5000) |
|---|---|---|---|---|---|---|---|---|---|
| 20 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 1 | — / — | 126 (0) | — / 8 | 0 / 0 | 4354 / 4394 / 4384 |
| 21 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 2 75 202 229 238 241 | — / 4 | 207 (98) | 2 / 3 | 0 / 81 | 4392 / 4546 / 4399 |
| 22 | 2 (1) | 0 | 0 0 0 0 0 0 0 0 | 0 1 1 2 8 84 178 211 | — / 6 | 216 (82) | 3 / 2 | 0 / 71 | 4458 / 4617 / 4457 |
| 23 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 5 55 183 239 250 255 | — / 4 | 239 (92) | 2 / 3 | 0 / 88 | 4418 / 4702 / 4460 |
| 24 | 26 (3) | 2 | 0 1 1 2 4 5 5 5 | 0 15 136 193 215 224 231 233 | — / 3 | 208 (100) | 1 / 2 | 5 / 83 | 4488 / 4604 / 4470 |
| 25 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | — / — | 106 (0) | — / — | 0 / 0 | 4467 / 4418 / 4410 |
| 26 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 21 169 209 227 237 238 239 | — / 2 | 220 (102) | 1 / 2 | 0 / 85 | 4408 / 4631 / 4463 |
| 27 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | — / — | 141 (1) | 7 / — | 0 / 0 | 4369 / 4428 / 4420 |

**depth3: drift arms (neighbours only, pattern proofs excluded from training)**

| seed | neighbours solved r1…r8 | neighbour targets with a depth-3 proof r1…r8 | excluded proofs (round json) r1…r8 | required-pool hits / 300k (targets) at r2, r4, r6, r8 |
|---|---|---|---|---|
| 20 **(zero-rate)** | 44 83 92 97 98 100 105 109 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 0 (0), 0 (0), 0 (0), 0 (0) |
| 21 **(zero-rate)** | 42 77 100 105 111 111 115 119 | 0 0 2 2 2 2 2 2 | 0 0 16 26 29 37 52 52 | 1 (1), 13 (2), 0 (0), 2 (1) |
| 22 | 50 89 95 101 102 103 104 105 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 112 (1), 0 (0), 0 (0), 3 (1) |
| 23 **(zero-rate)** | 77 123 137 145 150 158 161 162 | 0 1 1 1 1 1 1 1 | 0 3 3 3 3 3 3 3 | 2 (1), 9 (2), 2 (1), 0 (0) |
| 24 | 66 91 108 112 119 120 120 122 | 4 4 11 11 15 16 16 18 | 18 19 61 61 77 93 100 137 | 2 (2), 280 (5), 185 (2), 0 (0) |
| 25 **(zero-rate)** | 70 100 107 108 108 108 110 111 | 0 2 2 2 2 2 2 2 | 0 20 20 20 20 20 20 20 | 0 (0), 0 (0), 0 (0), 0 (0) |
| 26 **(zero-rate)** | 67 108 126 135 137 143 148 154 | 4 9 14 15 15 17 19 19 | 13 57 81 86 87 94 113 114 | 13 (4), 0 (0), 3 (1), 114 (2) |
| 27 **(zero-rate)** | 58 87 95 103 110 123 132 138 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 0 (0), 19 (1), 0 (0), 0 (0) |

**reductio: pre-RL sample and arms (required stratum = targets with a verified strict reductio proof, cumulative r1…r8)**

| seed | pre-RL hits / 600k (targets) | frozen@256 targets | `req` r1…r8 | `mix` required r1…r8 | ign. round req / mix | `mix` neighbours solved r8 (with pattern) | first pattern proof in `mix`: neighbour / required round | transfer r8 req / mix (of 150) | held-out greedy r8 req / mix / drift (of 5000) |
|---|---|---|---|---|---|---|---|---|---|
| 20 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | — / — | 177 (0) | — / — | 0 / 0 | 4381 / 4395 / 4381 |
| 21 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 1 7 23 35 43 52 | — / 5 | 180 (0) | — / 3 | 1 / 26 | 4496 / 4527 / 4532 |
| 22 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | — / — | 182 (0) | — / — | 0 / 1 | 4432 / 4477 / 4450 |
| 23 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | — / — | 157 (0) | — / — | 0 / 1 | 4370 / 4413 / 4392 |
| 24 | 1 (1) | 0 | 0 0 0 0 0 0 0 0 | 0 4 21 40 47 52 53 53 | — / 3 | 170 (0) | — / 2 | 0 / 26 | 4431 / 4472 / 4430 |
| 25 **(zero-rate)** | 0 (0) | 0 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | — / — | 170 (0) | — / — | 0 / 0 | 4341 / 4412 / 4377 |
| 26 | 6 (2) | 0 | 0 0 0 0 0 1 13 33 | 0 0 1 7 31 49 52 53 | 7 / 5 | 182 (1) | 8 / 3 | 15 / 27 | 4410 / 4457 / 4417 |
| 27 | 16 (1) | 1 | 0 0 0 0 0 0 0 0 | 0 0 0 1 7 39 46 52 | — / 6 | 143 (0) | — / 4 | 0 / 25 | 4257 / 4286 / 4292 |

(The transfer proofs in the zero-rate `req` / non-igniting `mix` rows — s21 `req` 1, s22 and s23 `mix` 1 — are single
strict reductio proofs of a transfer target sampled by an arm that has 0 on its own required stratum.)

**reductio: drift arms (neighbours only, pattern proofs excluded from training)**

| seed | neighbours solved r1…r8 | neighbour targets with a reductio proof r1…r8 | excluded proofs (round json) r1…r8 | required-pool hits / 300k (targets) at r2, r4, r6, r8 |
|---|---|---|---|---|
| 20 **(zero-rate)** | 40 91 132 150 161 168 174 181 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 0 (0), 0 (0), 0 (0), 0 (0) |
| 21 **(zero-rate)** | 46 85 109 129 146 160 171 184 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 1 (1), 1 (1), **151 (8)**, 6 (1) |
| 22 **(zero-rate)** | 68 113 137 152 169 180 184 192 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 0 (0), 0 (0), **4 (1)**, 1 (1) |
| 23 **(zero-rate)** | 54 91 122 144 153 155 160 161 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 1 (1), 0 (0), 0 (0), 0 (0) |
| 24 | 59 105 133 146 154 162 165 170 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 2 (2), 0 (0), 0 (0), 667 (9) |
| 25 **(zero-rate)** | 26 62 92 112 128 141 151 157 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 0 (0), 0 (0), 0 (0), 0 (0) |
| 26 | 41 89 121 141 153 170 175 181 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | not sampled (no `dcov_reductio_s26_*`) |
| 27 | 24 62 92 119 125 136 141 143 | 0 0 0 0 0 0 0 0 | 0 0 0 0 0 0 0 0 | 0 (0), 1 (1), 0 (0), 0 (0) |

The exclusion filter: my per-round count of raw found records whose pruned form has the pattern equals the logged
`excluded_pattern_proofs` in all 16 drift arms and all 8 rounds (e.g. depth-3 s24: 18 19 61 61 77 93 100 137).
`mix_<r>.jsonl` files were not pulled, so "no pattern proof was trained on" rests on that equality plus the code
(`fs = keep` before the `max_per_thm` slice), not on the training mixes themselves.

### Expectations against my counts

| | expectation | my count | |
|---|---|---|---|
| n₀ | ≈ 3–5 (depth-3), ≈ 4–5 (reductio) of 8 | 6, 5 | depth-3 one above the range |
| E1 | pools, alternatives, 0 inconsistencies, ≥ 40 % of neighbours solved by every draw | sizes and shares met, 0 inconsistencies; depth-3 s25 35.3 % | one draw misses the 40 % clause |
| E2 | zero-rate depth-3 `req`: 0 of n₀ ignite, ≤ 5 targets; non-zero ignite ≥ 80 % by r5 | **0 of 6, 0 targets in every arm**; non-zero: **0 of 2** (s22: 0 targets, s24: 5) | first clause holds; second is a miss |
| E3 | zero-rate depth-3 `mix`: ≥ 40 % ignite, only after ≥ 1 round of neighbour-only successes | **3 of 6** (s21 r4, s23 r4, s26 r2); each after ≥ 1 round with successes on neighbours only | holds — but see "what the neighbours rewarded" below |
| E4 | zero-rate reductio `mix`: 1–2 of n₀ (rule: 0); non-zero ignite on both pools | **1 of 5** (s21, r5, 52 targets); non-zero: `mix` 3 of 3, `req` **1 of 3** (s26 r7) | first clause as the proposer expected; "both pools" is a miss |
| E5 | depth-3 drift: ≥ 3 hits / 300k by r8 in ≥ 2 of n₀; reductio drift: ≤ 1 hit at every checkpoint in every zero-rate arm | depth-3: a checkpoint with ≥ 3 hits in **4 of 6** (s21, s23, s26, s27), but **at r8 only in 1 of 6** (s26); reductio: **violated in 2 of 5** (s21: 151 hits on 8 targets at r6, 6 at r8; s22: 4 at r6) | depth-3 depends on the reading of "by round 8"; reductio is a miss |
| E6 | required targets solved without the pattern ≤ 5 % (depth-3), 0 (reductio) | 0 in all 48 arms | holds |

Pre-registered falsifiers, as I count them: "Clause (3) dies if E2 holds" — E2's zero-rate clause holds (0 of 6 on
`req` vs 3 of 6 on `mix`, same six draws, same seeds). "Clause (2) dies if ≥ 2 zero-rate reductio draws ignite on
`mix`, or if any zero-rate reductio `drift` arm reaches ≥ 10⁻⁵" — one draw ignites (not two); the drift criterion is
met by s21 (151 / 300k = 5.0·10⁻⁴ at r6, 2.0·10⁻⁵ at r8) and, at the threshold, by s22 (4 / 300k = 1.3·10⁻⁵ at r6).

### Things the counts say that the pre-registered table does not

1. **What the depth-3 neighbours rewarded.** The depth-3 neighbour stratum is pattern-*optional*, not pattern-free:
   in every `mix` arm that ignites from a zero-rate draw, the first depth-3 proof in the found set is on a *neighbour*
   target, one round before the first required one (s21, s23: neighbour r2 → required r3; s26: neighbour **r1**, 3
   targets, → required r2), and by round 8 the igniting arms hold depth-3 proofs of 82–102 neighbour targets. s26
   (0 hits in 600k on the required pool) writes depth-3 proofs for 3–4 neighbour targets in round 1, i.e. from the
   untouched Stage-1 model in 9,600 samples: "zero-rate" is a statement about the required pool only. The
   non-igniting zero-rate `mix` arms (s20, s25, s27) have 0, 0 and 1 (at r7) neighbour targets with a depth-3 proof.
   So in the `mix` condition the pattern itself was rewarded on easier targets before it appeared on required ones;
   the run has no `mix` arm with pattern proofs excluded on the neighbour stratum only. The `drift` arms are the
   closest thing: there, with every depth-3 proof excluded, depth-3 proofs of neighbours still appear after training
   on flat proofs only (s21 r3, s23 r2, s25 r2), and the required-pool rate becomes non-zero but small and
   non-monotone.
2. **Reductio neighbours are pattern-free, and the reductio ignition is two schemata.** No neighbour target has a
   strict reductio (or any `DN`-of-`NEGI`) proof before ignition in any `mix` arm (one target at r8 in s26). Every
   igniting reductio arm (`mix` s21, s24, s26, s27; `req` s26) acquires the same two schemata and nothing else:
   `nand_neg` 26 / 26 and `negimp_to_pos` 25–26 / 26, plus at most one stray target (`chain_neg` or `neg_both`) —
   52–53 of 300, all but the stray of minimum length 7. These are the two schemata whose oracle proof is a
   NEGI-closed derivation of `( ~ ( ~ G ) )` followed by one `DN` line, i.e. a (tightened-definition) neighbour proof
   plus one step. The other 14 schemata (248 targets, 8–10 lines) stay at 0–1. Every drift-checkpoint reductio hit
   (all arms, all checkpoints) is also in those two schemata, as is every pre-RL hit of the three non-zero draws.
3. **Coverage hits are concentrated on single targets and are not monotone in the round.** E.g. depth-3 s22: 112 hits
   at r2, all on `d3req_292`, then 0, 0, 3; reductio s24: 667 at r8, 533 of them on one target, after 2, 0, 0;
   reductio s21: 1, 1, 151 (96 on one target, 8 targets in all), 6. Target counts are in brackets in the tables; a
   hits-per-300k threshold is dominated by one target's rate at one checkpoint.
4. **Length asymmetry of the required pools.** `depth3_req` is 7–8 lines; `reductio_req` is 7–10 lines with only 52
   targets at 7. Everything reductio arms acquire is at 7 lines (one at 8).
5. **Held-out greedy** (of 5,000, r8) is highest in the igniting `mix` arms (depth-3 s23: 4,702 vs 4,418 for its `req`
   arm; reductio s21: 4,527 vs 4,496) and within ± 60 of the `req` arm's value everywhere else (lowest relative
   value: depth-3 s25 `drift` 4,410 vs `req` 4,467). I have no pre-RL held-out number per draw in the artefacts.
