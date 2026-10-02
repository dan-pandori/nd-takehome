# Review — run `rl-from-ckpt`

Reviewer session, 2026-10-02 (started 10:56 UTC). Phase 1 was done blind in `~/review/rl-from-ckpt` (executor
write-ups removed; I also did not open `artifacts/rfc/analysis_stdout.txt`, `summary.json` or `compute*.{json,txt}`).
Inputs: `preregistration/rl-from-ckpt.md` (commit `224cd387`, 2026-10-02 01:47:18 UTC; the first ladder `args.json`
says 01:48:31 UTC, so it was **written before the run**; the file has not been changed since), the code, the raw
read-outs (`artifacts/rfc/eval/*.jsonl`), the ladder and control `round_*.json`, the score files, and `trajectory`'s
raw reads and scores (`~/review/trajectory/artifacts/tj`, the bucket copy). Reviewer code: `review_rfc/` (recount,
analysis, calib, recheck, splits, score, compute). `rlean.py`, `splits.py` and `score.py` are earlier reviewers' code
(`review_tj6/` on `dan_trajectory-cap6`). Nothing is imported from `rfc_*.py` or `tj_*.py`. **Lean alone decides.**
`nd_verify` was not used for anything.

**Models.** Every number is on `trajectory`'s **best-cap12 s0 / s1 / s2**: `best_model.ALiBiGPT` 6 × 384,
**9,560,832 params** (I read this from `rc_best12_s0_{p1600,pend}_r8.pt`: cfg `arch best`, `lean_staten`), trained
from scratch on K12 (`data/kh/train_k12.jsonl`, 155,000 records, md5 `800b5486…`; all 17 pod setup logs show this
md5). Stage-1 was 1,200 s on an A40. Labels used below:
- `p<step>`: a Stage-1 checkpoint (the starts). `pend`: end of Stage-1.
- `L`: this run's T1 ladder from that start, rounds r2 / r4 / r8.
- `C`: this run's replay-only control at r8.
- End arm: `trajectory`'s ladders `la_T1_best12_s*`, r8 from pend. These numbers are inherited from `trajectory` and
  were re-counted here from its raw reads.

All reads: k 256, T 0.8, `max_steps` 96, `max_action` 512, batch 2,048. "x0" / "x1" = sample seed 0 / 1.

## §Recount (phase 1, blind)

### Hard constraints

| check | result |
|---|---|
| `nd_verify/` tree vs `origin/main` | identical (`9437bb72…` both) |
| `artifacts/TEST_RUN_DONE` vs `origin/main` | identical blob (`1d5cf064…`) |
| `nd_verify` used as a judge | no. `state_eval.py` → `eval_set.judge` → `lean_judge.verify_text/judge_many`. `state_env.py` imports only `nd_verify.verify.parse_formula`, a formula parser that is inherited and unchanged. No `rfc_*.py` or `tj_*.py` references it |
| training code changed in the branch | none. `state_ladder_ei.py`, `state_train*.py`, `state_eval.py`, `state_env.py` and `lean_judge.py` are unchanged from `origin/dan`, and `state_ladder_ei.py` is byte-identical to `dan_trajectory`'s. New code: `rfc_replay.py` (control), `rfc_*` analysis, pod scripts |
| evaluation files read in training code | `state_ladder_ei.py`, `state_train.py` and `rfc_replay.py` have no `data/bs` / textbook72 / holdout250 reference. The ladder *samples* `data/ladder/transfer.jsonl` (holdout250 ⊂ it, by construction) but trains only on RL-target finds + K12 replay (§4 of the driver). The control trains on K12 alone |

No hard-constraint violation.

### Split disjointness (renaming class: 24 atom permutations, premise-order-insensitive, F not renamed)

| eval pool | vs K12 (155,000) | vs `rl_targets` (trained on) | vs ladder transfer (sample-only) |
|---|---|---|---|
| textbook72 | **1** (`textbook_3ed45280…`, `P ∨ Q, ¬P ⊢ Q`) | 0 | 0 |
| holdout250 | 0 | 0 | 250 / 250 (by construction, never trained on) |

There are 0 exact-prompt matches with any training file, and textbook72 and holdout250 share 0 classes. The single
textbook72 ↔ K12 class is inherited: the `trajectory` and `best-state` reviews found the same one. It is a premise
permutation and is worth at most 1 textbook72 theorem per read.

### Completeness and consistency of the read-outs

All 320 reads I expected are present:
- this run: 144 ladder reads, 60 control reads and 8 seed-0 re-reads;
- `trajectory`: 108 reads (starts, pend, end-arm r2 / r4 / r8).

Every record has `n_tried` 256, `n_ok = n_tried − len(reasons)`, `solved == bool(proofs) == (n_ok > 0)`, and the
pool's exact 72 / 250 names. **0 inconsistencies.**

**Stop rule, p0** (all three seeds): rounds 1–2 accepted **0** of 287,680 target samples. The target, transfer and
held-out greedy counts are all 0, and `mix_rl_records` is 0, so nothing was trained. The ladder stopped (`STOPPED`), as
pre-registered, and no p0 control was needed.

### Solved counts, r8, sample seed 1 (the pre-registered y)

| start | ladder tb72 | ladder h250 | control tb72 | control h250 | start (r0) tb72 / h250 | pre-reg ladder / control (tb72; h250) |
|---|---|---|---|---|---|---|
| p1600 | 38 / 34 / 38 | 223 / 212 / 222 | 32 / 28 / 33 | 202 / 196 / 195 | 10 / 14 / 13 ; 67 / 60 / 66 | 40 [28,52] / 28 [15,40]; 225 [195,242] / 185 [130,220] — all in |
| p5000 | 48 / 44 / 46 | 234 / 234 / 238 | 32 / 27 / 36 | 205 / 203 / 204 | 19 / 19 / 18 ; 138 / 129 / 112 | 45 [34,55] / 31 [20,40]; 232 [212,243] / 195 [160,222] — all in |
| p12000 | 45 / 51 / 46 | 233 / 235 / 233 | 39 / 37 / 39 | 214 / 210 / 211 | 27 / 20 / 22 ; 162 / 153 / 142 | 47 [38,56] / 33 [24,42]; 235 [222,244] / 200 [175,225] — all in |
| p16000 | 49 / 47 / 51 | 235 / 232 / 232 | 41 / 37 / 38 | 211 / 216 / 207 | 26 / 29 / 28 ; 176 / 195 / 155 | 48 [40,56] / 34 [26,42]; 236 [225,244] / 205 [185,228] — all in |
| pend (end arm, inherited) | 48 / 48 / 53 | 240 / 236 / 237 | 38 / 31 / 35 | 206 / 210 / 213 | 34 / 33 / 36 ; 196 / 205 / 200 | control 35 [28,44]; 208 [195,228] — in |

Means over seeds (n = 3, so IQM = mean):

| start | ladder tb72 | ladder − control tb72 (paired by seed) | ladder h250 | ladder − control h250 (paired by seed) |
|---|---|---|---|---|
| p1600 | 36.7 | +5.7 (6 / 6 / 5) | 219.0 | +21.3 |
| p5000 | 46.0 | +14.3 | 235.3 | +31.3 |
| p12000 | 47.3 | +9.0 | 233.7 | +22.0 |
| p16000 | 49.0 | +10.3 | 233.0 | +21.7 |
| pend | 49.7 | +15.0 | 237.7 | +28.0 |

- Rank order on tb72 holds (36.7 ≤ 46.0 ≤ 47.3 ≤ 49.0 ≤ 49.7).
- pend − p1600 = **+13.0** textbook72 (pre-reg ≈ +8, range 0–20: in), and +18.7 on holdout250.
- p5000–p16000 are within 4 textbook72 and 5 holdout250 of the end arm, which is inside the pre-registered MDD (7 / 5).
- Ladder − control is > 0 at every start in every seed, on both pools.
- The x0 reads give the same picture: every cell is within ±4 of x1.

The **seed-0 re-reads** (`rr`, x1) of p1600 / p5000 / p12000 / p16000 match `trajectory`'s x1 reads of the same
checkpoints **theorem for theorem** on both pools (0 flips; pre-reg ±3).

### Lean re-check of counted proofs

Harness: `rlean.py`, my own ND → Lean renderer. A proof passes iff its file line has no error **and** `#print axioms` ⊆
{propext, Classical.choice, Quot.sound}.

Negative controls, run first:

| control | passed |
|---|---|
| 60 untouched counted proofs | **60 / 60** |
| 60 of the run's own LEANREJ samples | **0 / 60** |
| 60 counted proofs paired with a different theorem of the same premise count | **0 / 60** |
| bare `sorry` | **0 / 1** |
| 60 single-line `ORI1`↔`ORI2` flips | 7 / 60 |

All 7 passing flips are benign: the disjunction is of the form `A ∨ A` (`P ∨ P`, `¬Q ∨ ¬Q`, …).

Then per arm (all three training seeds, x1): the 30 longest counted proofs (distinct theorems) plus 120 random ones.

| arm | counted proofs (stored) | checked | Lean OK | term size median / max | ND lines median / max |
|---|---|---|---|---|---|
| L p1600 r8 | 34,313 | 150 | **150** | 45 / 426 | 15 / 61 |
| L p5000 r8 | 50,647 | 150 | **150** | 54 / 388 | 17 / 76 |
| L p12000 r8 | 61,701 | 150 | **150** | 52 / 466 | 16 / 74 |
| L p16000 r8 | 65,975 | 150 | **150** | 48 / 490 | 15 / 88 |
| L p1600 r2+r4 | 28,428 | 150 | **150** | 42 / 338 | 12.5 / 48 |
| L p5000 r2+r4 | 47,458 | 150 | **150** | 49 / 464 | 16 / 70 |
| L p12000 r2+r4 | 69,879 | 150 | **150** | 44 / 437 | 15 / 69 |
| L p16000 r2+r4 | 75,898 | 150 | **150** | 44 / 342 | 14.5 / 63 |
| C p1600 r8 | 6,796 | 150 | **150** | 47.5 / 166 | 14 / 35 |
| C p5000 r8 | 7,032 | 150 | **150** | 35.5 / 158 | 12 / 36 |
| C p12000 r8 | 7,326 | 150 | **150** | 40.5 / 173 | 13 / 32 |
| C p16000 r8 | 7,528 | 150 | **150** | 43 / 150 | 13 / 39 |
| C pend r8 | 6,776 | 150 | **150** | 40.5 / 182 | 12.5 / 47 |

**1,950 / 1,950 accepted.** The samples are *sampled* proofs (often padded with detours), so these term sizes describe
what the models write, not minimal proofs. Ladder proofs are longer than control proofs (median 45–54 vs 36–48 term
nodes; max 390–490 vs 150–182).

Caveat on "literal text": the reads store the env's ND rendering of each sampled action sequence, not the raw token
text. My re-check is therefore of an alpha-equivalent Lean re-rendering, as in the earlier state-env reviews.

### Truncation (`action truncated` + `step cap`)

- r8 reads (ladder 48, control 60, end arm 12): max **0.99 %** per read, so 0 reads exceed 2 % (pre-reg ≤ 2 %).
  17 / 12 / 4 exceed 0.1 %.
- Per read × length bin (486 strata, ladder + control r8): 74 exceed 0.1 % and 6 exceed 2 %:
  - s0 p12000 h250, the one 14-line theorem: 12 % / 11 %;
  - control pend s2 / s0 h250, the 8-line bin: 6.0 % / 3.2 %.
- Starts (`trajectory`'s reads): up to 5.7 % (s1 p12000 tb72), 10.6 % at s1 p0 (pre-reg "up to ≈ 20 %": in).

The caps were held fixed in every arm, as pre-registered.

### Threshold analysis

My own code: x = min of the stored per-step T 1.0 log p list, clipped at −40; Newton-Raphson logistic fits; 315
reference proofs × 3 seeds. 7 textbook theorems have no reference.

**Re-score checks.**
- This run's r0 scores of the four starts equal `trajectory`'s scores of the same checkpoints exactly (3,780 values,
  max |Δ| 0).
- **My own CPU scorer** (33-base marginalisation, env-assigned names skipped) on 12 references under each of
  `rc_best12_s0_p1600_r8` and `rc_best12_s0_pend_r8` reproduces the stored x_ctrl worst step to ≤ 5.4e-5 nats. 6 of the
  12 references had x_ctrl < −12, and the stored values are rounded to 1e-4. I fetched the checkpoints from the bucket;
  their md5s equal the executor's `score/ckpts_*.md5`.

**Null curve.** Refitting the end arm (r8 x1 vs x_start at pend, pooled) gives b0 5.341, b1 0.482, **x50 −11.09**
(per seed −10.93 / −11.26 / −11.05). This reproduces the pre-registered null. The pre-registered expected solves
among x_start < −12 pairs also reproduce: p1600 20.8 (120 pairs), p5000 10.3 (66), p12000 8.3 (50), p16000 9.4 (43);
pend 4.7 (25), of which it solves 7.

**x_start form (brief's literal form)**

x50 with seed fixed effects, mean of seeds, and a theorem-bootstrap 95 % interval:

| start | x50 per seed | mean [95 % CI] |
|---|---|---|
| p1600 | −13.7 / −12.5 / −13.3 | −13.1 [−14.1, −12.3] |
| p5000 | −14.2 / −14.4 / −15.7 | −14.7 [−16.5, −13.4] |
| p12000 | −14.6 / −16.0 / −15.0 | −15.2 [−17.7, −13.2] |
| p16000 | −11.6 / −11.3 / −12.1 | −11.7 [−12.9, −10.7] |
| pend | | −11.1 |

- The pre-registered shift (p1600 ≈ −22, p5000 ≈ −18, p12000 ≈ −16, p16000 ≈ −14) did **not** occur in the predicted
  order or size. p1600 moved least among p1600–p12000, and **p16000 is inside the 2.5-nat MDD of pend**.
- Excess E over x_start < −12 pairs (p1600–p16000, pre-reg null): **82.3** (per seed 30.4 / 30.0 / 21.9). That is
  131 solved of 279 pairs against 48.7 expected. **The literal falsifier fires** (≥ 64, and ≥ 3 in 3 / 3 seeds), as
  predicted. The pre-registered point prediction was ≈ 110 [70, 170] solves; observed 131, which is in.

**x_ctrl form (pre-registered decisive form)**

| start | x50 (seed FE) |
|---|---|
| p1600 | −12.0 |
| p5000 | −15.6 |
| p12000 | −14.9 |
| p16000 | −15.2 |
| **pend** | **−16.1** |

- Excess under the pre-registered null: **126.8** (per seed 38.4 / 46.4 / 42.0; 187 solved of 385 pairs against 60.2
  expected), so the pre-registered falsifier **fires**. Read literally, that is the pre-registered "creation" outcome:
  both forms fire.
- **But the same test fires on the end arm itself.** The end arm, evaluated against its *own* control's x, has
  x50 −16.1 and an excess of +15.9 / +10.8 / +15.7 per seed. The pend arm is the null by construction, so the
  pre-registered null curve is miscalibrated for x measured under a replay-fine-tuned model.
- The cause is scale. Replay fine-tuning moves the worst-step log p of references (median x_ctrl − x_start per seed):
  p1600 +1.7 to +2.2, p5000 +0.4 to +1.0, p12000 +0.4 to +0.6, p16000 −0.1 to −0.4, **pend −0.9**. Under the controls
  a solve at a given x is more likely than under Stage-1 checkpoints.
- **Calibrated variant** (my construction, post hoc; the null is fitted on the end arm vs *its* control's x_ctrl):
  b0 5.108, b1 0.317, x50 −16.12. The excess over x_ctrl < −12 at p1600–p16000 is then **−9.1** (per seed
  −5.6 / +0.8 / −4.3). At x_ctrl < −16 it is −0.6. The negative control (pend) is −0.2 / −0.6 / +2.5.
- On the calibrated scale **there is no excess at any start**: p1600 is −5.0 / −3.6 / −5.9 (below the null), and
  p5000–p16000 are each within ±4 per seed. Read this way, the early-start ladders' low-x solves are what the replay
  alone predicts.

**Group C** (`trajectory`'s per-seed hard set: neither pend nor end-arm r8 solves in the x0 reads; 36 / 35 / 28
theorems). Theorems solved at ladder r8 x1:

| start | per seed | sum | vs end arm (sum 5) |
|---|---|---|---|
| p1600 | 1 / 1 / 2 | 4 | −1 |
| p5000 | 5 / 5 / 3 | 13 | +8 |
| p12000 | 3 / 5 / 4 | 12 | +7 |
| p16000 | 6 / 6 / 2 | 14 | +9 |
| end arm | 3 / 1 / 1 | 5 | — |

- No start reaches the pre-registered **+10** creation threshold.
- p5000–p16000 exceed the pre-registered "≤ 4 per seed" in 4 of 9 seed-cells.
- C is defined by the end arm's own failures, which biases its count down even on the x1 draw.
  The symmetric comparison avoids that bias. Over 3 seeds × 322 theorems, counting
  theorems solved at r8 in *both* x0 and x1 by one arm and in *neither* by the other:

| start | only the early-start ladder | only the end arm |
|---|---|---|
| p1600 | 1 | 86 |
| p5000 | 11 | 21 |
| p12000 | 7 | 24 |
| p16000 | 9 | 20 |

  No creation-direction signal.

### Compute (from raw `round_*.json`; one GPU per ladder or control process; RTX A6000 on 16 pods, A40 on 1 per the logs)

| arm | wall-s (1 GPU) per seed | target samples | gen tokens (M) ≈ rows × mean action length | train steps × recs |
|---|---|---|---|---|
| L p1600 | 21,747 / 19,017 / 21,094 | 1,150,720 | 346 / 360 / 359 | 4,800 × 128 |
| L p5000 | 24,712 / 24,075 / 20,899 | 1,150,720 | 400 / 386 / 374 | 4,800 × 128 |
| L p12000 | 23,811 / 24,597 / 23,974 | 1,150,720 | 394 / 413 / 395 | 4,800 × 128 |
| L p16000 | 26,138 / 26,964 / 25,829 | 1,150,720 | 401 / 394 / 409 | 4,800 × 128 |
| End arm (trajectory) | 22,352 / 24,469 / 25,318 | 1,150,720 | 399 / 415 / 402 | 4,800 × 128 |
| L p0 (stopped) | 355 / 496 / 401 | 287,680 | 50 / 76 / 60 | 0 |
| C p1600–p16000 | ≈ 6,150–6,220 each | 0 | 0 | 4,800 × 128 |
| C pend | ≈ 3,180–3,210 each | 0 | 0 | 4,800 × 128 |

- No early-start ladder exceeds 1.25× the end arm on any measure. The largest ratio is p16000 s1 wall-s at 1.10× the
  end-arm mean.
- The C pend controls ran in half the wall time of the others. That is probably a different card or co-tenancy; I
  have not established which.
- The ladder's mixes also hold 0.41–0.52 M RL records per arm over 8 rounds; the controls hold none.
- I did not derive training tokens or Lean-check counts.
