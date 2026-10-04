# Review — rl-continue-cap6

Reviewer session, 2026-10-04 (UTC). Phase 1 was done in `~/review/rl-continue-cap6`, a copy without the executor's write-ups, using
my own code in `review_rc6/` (`recount.py`, `groupc.py`, `c_in_loop.py`, `splits.py`, `recheck.py` + `rlean.py`, `sizes.py`,
`compute.py`). The outputs are in `review_rc6/rv/*.log|json`. The renderer and Lean harness `rlean.py` are reviewer code from the
`trajectory-cap6` review kit (`review_tj6/` on `dan_trajectory-cap6`); they are independent of the executor. I did not use `nd_verify`.

**Models.** Every number below is on `trajectory-cap6`'s T1 ladders, seeds 0–2, continued here for r9–r16: ALiBiGPT 6 × 384,
9.56 M params, `lean_staten` proof-state format, from scratch on the cap-6 set (`data/p2/train_depth3_f0_a1.jsonl`, 155,000 records,
md5 `29276f24…`, the same as the pods' setup log). Stage 1 ran 1,200 s; then EI under the Lean-alone state-env gate. Checkpoints
are `ckpts/rc6/ladder/la_T1_best6_s{0,1,2}_r{9..16}.pt`. The r8 baselines are `trajectory-cap6`'s `la_T1_best6_s*_r8.pt`. Every
count is under Lean alone, on both sides; there is no pre-2026-09-27 comparison. The cap-12 comparators are `trajectory`/`rl-continue`'s
`la_T1_best12_s*` (same architecture and format, cap-12 set). They are inherited from `artifacts/rc6/cap12_rounds/` and were not
recounted by me.

## §Recount (phase 1, written before reading `run_rl_continue_cap6.md`, `numbers.md`, `log.md`)

### Hard constraints — all pass

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72…` = `origin/main`'s |
| `nd_verify` unused as judge | the ladder (`state_ladder_ei.py`) and the reads (`state_eval.py`) judge through `lean_judge` / `eval_set.judge` / `lean_gate`. The only `nd_verify` import on the path is `state_env.py`'s `parse_formula`, a formula parser that is pre-existing on `dan` and judges nothing. |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064…` = `origin/main`'s; no commit touches it or `test_run_once.sh` |
| core code | the branch changes only `pod/rc6/*` and `rc6_*.py` against its merge-base with `origin/dan` (no edits to the ladder, sampler, trainer or judge) |
| evaluation files in training | no `textbook72` / `holdout250` reference in `state_ladder_ei.py` / `state_train.py` / `state_sample.py`; the r16 fine-tune mixes (`mix_16.jsonl`, all three seeds, 24,326 / 24,317 / 24,327 prompts = the targets solved + 20,000 replay) contain **0** tb72 or h250 renaming classes |

### Seamlessness — reproduces

1. The r9 checkpoint md5s (`run_s*.log`) are `586baf0b…` / `a8dfc589…` / `1b1843d5…`. They equal `trajectory-cap6`'s
   `artifacts/tj6/score/ckpts_s*.md5` r8 entries. `round_9.json` samples from `…_r8.pt` with seed `1000·s + 9`, and later rounds follow the continuous-run seeds.
2. `resumed round 8: 72175 / 48085 / 36334 target proofs` equals the line count of `found_8.jsonl` on each seed.
3. Every r8 proof is still in `found_16` (72,175/72,175, 48,085/48,085, 36,334/36,334; transfer likewise). No r8-solved target or
   transfer theorem is lost. `targets_cum` / `transfer_cum` from my own first-solved-round count equal the round JSONs at every r8–r16.
4. There was no OOM retry: every round ran at batch 2,048.

### Per-seed ladder quantities (own count from `found_{8,16}` / `found_transfer_{8,16}`)

| quantity | s0 | s1 | s2 | pre-registered expectation | verdict |
|---|---|---|---|---|---|
| `rl_targets` solved r8 → r16 (of 4,495) | 4,257 → 4,326 | 4,235 → 4,317 | 4,204 → 4,327 | — | — |
| **new targets r9–r16** | **+69** | **+82** | **+123** | +40 to +70 per seed | s0 in range; **s1, s2 above** |
| new transfer r9–r16 (of 2,285) | +60 (2,071 → 2,131) | +80 (2,055 → 2,135) | +98 (2,031 → 2,129) | +30 to +60 | s0 at the top edge; **s1, s2 above** |
| new targets per round r9…r16 | 11 6 11 11 8 10 3 9 | 30 12 14 9 5 5 5 2 | 30 19 10 12 13 20 12 7 | declining, ≤ +8/round on most seeds by r14–r16 | r14–r16: s1 yes (5 5 2); s0 mixed (10 3 9); **s2 no (20 12 7)**. Only at r16 alone are 2/3 seeds ≤ 8 |
| target sample accuracy r8 → r16 | 0.903 → 0.918 | 0.899 → 0.918 | 0.889 → 0.903 | 0.90–0.93 | in range (alloc tried/accepted deltas = round JSON at every round) |
| `targets_cum` r16 < cap 12's r8 | 4,326 < 4,383 | 4,317 < 4,365 | 4,327 < 4,407 | below on all three (≈ 4,275–4,325) | holds on 3/3 (s0, s2 1–2 above the guessed band) |
| falsifier 1: ≥ 100 new targets on ≥ 2/3 seeds | no | no | yes | — | **does not fire** (1/3 seeds) |

The distinct proofs at r16 are 295,168 / 202,492 / 168,090. My start-index normaliser (N-labels renumbered in order of appearance)
gives the same count as the run's `norm` field and the same as the row count. Mean new targets 91.3 (bootstrap 95 % interval over
seeds 69–123; at n = 3 the IQM is the mean). The new targets are mostly `L_true` 8–10 (s0: 7:4 8:11 9:12 10:35 11:1 12:4 13:2). At
r16 the unsolved targets are 169 / 178 / 168, and 12 of them on every seed are `L_true` 14.

**Cap 12 (inherited, `rl-continue` round JSONs, unreviewed by me).** Cap 12 went r8 4,383 / 4,365 / 4,407 → r16 4,403 / 4,433 / 4,429
(+20 / +68 / +22). Cap 6's r16 sits 77 / 116 / 102 below cap 12's r16, against 126 / 130 / 203 at r8. The gap narrowed on all three
seeds but did not close. Transfer: cap 6 r16 2,131 / 2,135 / 2,129 against cap 12 r8 2,185 / 2,170 / 2,190.

### Group C and the r16 reads (sample seed 1, k 256; `groupc.py`)

Group C was recomputed from `trajectory-cap6`'s eval rows (seed-0 samples, unsolved at `pend` and at r8, tb72 + h250). It has
**52 / 52 / 60** theorems (tb72 28/31/34 + h250 24/21/26), as pre-registered. Each seed's `data/rc6/h250_C_s*.jsonl` is exactly my
h250 part of C. All eval rows are internally consistent (`n_ok = n_tried − |reasons|`, `n_tried` = 256).

| | s0 | s1 | s2 | mean |
|---|---|---|---|---|
| C pass@256 r8 (`trajectory-cap6` x1) | 0.077 (4/52) | 0.038 (2/52) | 0.050 (3/60) | 0.055 |
| C pass@256 r16 | **0.192 (10/52)** | **0.154 (8/52)** | **0.183 (11/60)** | 0.176 |
| Δ | +0.115 | +0.115 | +0.133 | **+0.121** |
| C pass@8 r8 → r16 | 0.003 → 0.102 | 0.002 → 0.105 | 0.002 → 0.110 | |
| C pass@1 r8 → r16 | 0.0004 → 0.048 | 0.0002 → 0.036 | 0.0003 → 0.060 | |
| tb72 solved r8 → r16 | 43 → 45 | 43 → 41 | 39 → 40 | within ±3 (expectation met) |
| holdout250 solved r16 | not read | not read | not read | expectation **not derivable** (only the C subset was read) |

**Falsifier 2 fires.** The seed-mean rise, +0.121, is 3.2× the r8 seed spread (0.038), and 3/3 seeds rise. Per seed, net +6 / +6 / +8
theorems (gained 6 / 7 / 11, lost 0 / 1 / 3). That is well above the 2–4 C theorems the r8 x1 re-draw itself "solved". The pre-registered
"group C unchanged within the r8 spread" is a **miss**, and "saturating" is refuted by the run's own falsifier 2.

There is independent corroboration from a different sample stream. The ladders' per-round transfer sampling (k 32, never trained on)
solved 2 / 0 / 3 of the h250-C theorems by r8 and 6 / 6 / 10 by r16, with first solves spread over r10–r16. 5 / 5 / 7 of the r16-read
solves are among them (`c_in_loop.py`).

**Truncation (policy: ≤ 0.1 % per reported stratum).** The reads keep `trajectory-cap6`'s settings (max_action 512, max_steps 96,
batch 2,048, T 0.8). They are held fixed against the r8 baseline, as the comparison requires, but the cut-off ("action truncated" +
step cap) is far above 0.1 %:
- C stratum, r8 → r16: 5.9 → 10.9 % (s0), 4.6 → 3.4 % (s1), 5.7 → 2.5 % (s2);
- h250-C alone, s0 r16: **18.7 %**;
- tb72: 1.0–3.7 %;
- the ladder's own in-loop sampling: 0.4–1.1 % per round.

The cap biases pass@k down on both sides. On s0 it got worse at r16, so it works against falsifier 2, not for it. The absolute group-C
levels are lower bounds, though.

### Lean re-check (`recheck.py`; Lean 4.34.1 core, each theorem must elaborate with no error and `#print axioms` ⊆ {propext, Classical.choice, Quot.sound})

Negative controls first:

| control | result |
|---|---|
| untouched r16-read proofs | 60/60 pass |
| samples the run recorded as Lean-rejected (`LEANREJ`) | 0/77 pass |
| `Or.inl`↔`Or.inr` flip at the ORI line | 0/60 pass |
| proof paired with another theorem of the same premise count | 0/60 pass |
| bare `sorry` | fails |

| arm (per seed s0 / s1 / s2) | checked | Lean accepts |
|---|---|---|
| first-found proof of **every** new target (69 / 82 / 123) + 100 random r9–r16 target proofs | 169 / 182 / 223 | **all** |
| first-found proof of every new transfer theorem (60 / 80 / 98) + 30 random | 90 / 110 / 128 | **all** |
| **every** proof of every C theorem solved in the r16 read (221 / 203 / 238) + 100 random r16 tb72 proofs | 321 / 303 / 338 | **all** |

That is 1,864 / 1,864 accepted, with no render failures.

**Proof length.** For the new-target first proofs, `L_true` median is 10 / 10 / 9. The lines median is 14 / 12 / 14, and no proof is
shorter than `L_true`. My line count equals the `written` field on all 274. Term size (Expr nodes of the elaborated value) has median
78 / 48.5 / 49 and range 18–489. The shortest r16 C proofs run 6–24 lines and 20–181 nodes (`sizes.log`).

### Splits (`splits.py`; renaming class over 24 atom permutations, F not renamed, premise-order insensitive)

| evaluation pool | vs train_cap6 (replay) | vs rl_targets (trained) |
|---|---|---|
| textbook72 | 0 | 0 |
| holdout250 | 0 | 0 |
| h250_C_s0/s1/s2 | 0 | 0 |
| transfer2285 | 0 | **2** (`la_transfer_307`, `la_transfer_842`) |

The two transfer overlaps are inherited from the `data/ladder` pools. Both were solved in r1–r3, so neither is among the r9–r16 new
transfer counts, and neither is in holdout250.

### Compute (`compute.py`, registry rows, A40)

| | GPU-s | gen tokens | attempts | Lean checks | train steps | train tokens |
|---|---|---|---|---|---|---|
| s0 | 33,464 | 431.0 M | 1,818,536 | 1,477,672 | 4,800 | 714 M |
| s1 | 25,666 | 399.7 M | 1,817,768 | 1,441,307 | 4,800 | 656 M |
| s2 | 26,517 | 418.5 M | 1,819,048 | 1,391,675 | 4,800 | 682 M |

GPU-s include the r16 reads, about 320–460 s per seed. Round-JSON `secs` for r9–r16 are 33,006 / 25,349 / 26,141. The registry carries
two `gpu_seconds` rows per fine-tune (the trainer's own row plus a ≈ 2 s parent-phase row), which overstates the total by ≈ 0.1 %.
s0 used 1.30× s1's GPU-seconds on an identical protocol (same attempts and steps), so the difference is pod speed, not workload.
Seeds are not arms, so the 1.25× flag does not apply. Round time grows from r9 to r16 on every seed (s0 3,542 → 4,535 s).

## §Compare (phase 2: `run_rl_continue_cap6.md`, `numbers.md` § rl-continue-cap6, `log.md` § rl-continue-cap6)

Extra phase-2 derivations are in `review_rc6/phase2.py` → `rv/phase2.log`.

| claim (executor) | my value | verdict |
|---|---|---|
| new targets r9–r16 +69 / +82 / +123 | +69 / +82 / +123 | reproduces |
| new transfer +60 / +80 / +98 | +60 / +80 / +98 | reproduces |
| `targets_cum` r16 4,326 / 4,317 / 4,327; transfer 2,131 / 2,135 / 2,129 | same | reproduces |
| new targets per round (both seeds' sequences, numbers.md) | same | reproduces |
| target accuracy 0.902 → 0.918, 0.899 → 0.918, 0.889 → 0.903 | 0.9025 → 0.9182, 0.8993 → 0.9179, 0.8887 → 0.9031 | reproduces |
| falsifier 1 not met (1 seed ≥ 100) | 1/3 seeds | reproduces |
| `targets_cum` r16 below cap 12's r8 on all seeds | 3/3 below | reproduces |
| seamlessness 1–3 | md5s = `trajectory-cap6`'s `ckpts_s*.md5`; resume counts = `found_8` lines; 0 lost, and also every r8 *proof* kept | reproduces |
| group C n 52 / 52 / 60; A 169 / 138 / 140; B 101 / 132 / 122 | same | reproduces |
| C solved r8 → r16 4 → 10, 2 → 8, 3 → 11; pass@256 0.077 → 0.192, 0.038 → 0.154, 0.050 → 0.183 | same | reproduces |
| C pass@1 r8 → r16 0.000 → 0.048 / 0.035 / 0.060 | 0.0004 → 0.0479, 0.0002 → 0.0355, 0.0003 → 0.0599 | reproduces (rounding) |
| falsifier 2 met: +0.121 > 0.038, 3 seeds rising | +0.1214, 3/3 | reproduces |
| summed C successes 5 → 637, 3 → 472, 4 → 920 | same | reproduces |
| 23 distinct C theorems solved at r16; 29 seed–theorem pairs, 24 at 0/256 at r8; 2 solved by all three | 23; 29; 24; 2 (`la_transfer_1802`, `la_transfer_205`) | reproduces |
| **"17 theorems never solved at r8 by any seed"** (numbers.md); "17 of them never solved at r8" (run.md) | 17 only when each theorem is checked against the seeds whose C contains it. Against all three r8 models' x1 reads it is **9** (8 when x0 is added): 8 of the 17 (`la_transfer_1032`, `_127`, `_1398`, `_1552`, `_1648`, `_1909`, `textbook_33a5…`, `textbook_3d57…`) were solved at r8 by another seed, where they sit in A/B | **differs — reword** |
| shortest C proofs 6–24 lines, all `lean_check`-accepted, term size 4–20 | 6–24 lines (my shortest-per-theorem list agrees). My Lean re-check accepts every one of the 662 r16 C proofs. "Term size 4–20" is `lean_check`'s inference-node count; my Expr-node count of the same theorems is 20–181. These are different measures, not a contradiction | reproduces; name the measure |
| holdout250 ⊂ transfer pool, sampled and never trained on | confirmed: the r16 mixes hold 0 h250 / tb72 classes; 0 class overlap with replay or `rl_targets` | reproduces |
| textbook72 43 → 45, 43 → 41, 39 → 40 | same | reproduces |
| cap 12 r16 4,403 / 4,433 / 4,429, 77–116 ahead; r13–r16 cap 6 +2–20 / round vs cap 12 0–5 (s1 18, 20) | same from the copied round JSONs (inherited, labelled unreviewed) | reproduces |
| compute per seed (GPU-s 33,005 / 25,349 / 26,140; gen tokens 424.8 / 394.6 / 412.4 M; attempts 1,794 k; 4,800 steps; Lean checks) | my registry sums minus the read rows give the same figures | reproduces |
| 23.93 pod-hours, $11.73 of $12 | `podbudget`: 23.93 h, $11.73 | reproduces |
| pre-registration before the first pod | commit `3889cde0` 17:45:00, first pod 17:45:39 (`~/pods.log`), budget registered 17:45 | reproduces |

**Not derivable or not reported.**
- The pre-registered holdout250 "±5 of r8" expectation could not be evaluated, because only group C was read. `numbers.md` explains why,
  but `run_rl_continue_cap6.md` does not list the expectation as unevaluated.
- The "≤ +8 per round on most seeds by r14–r16" expectation is not scored anywhere. It is a miss on s2 (20, 12, 7) and mixed on s0
  (10, 3, 9).
- The run.md table shows outcomes next to expectations but never writes "miss". New targets and new transfer were above the
  pre-registered range on 2/3 seeds, and group C was not "unchanged". These are misses of the expectation and should be called that.
- **Truncation is not reported.** Cut-off ("action truncated" + step cap) runs 2.5–18.7 % in the group-C strata of the reads and
  1–3.7 % on tb72. The ladder's own sampling sits at 0.4–1.1 % per round. Policy requires reporting the fraction, and raising the cap
  above 0.1 % per stratum. The settings are `trajectory-cap6`'s and are held fixed against r8, so the comparison is fair. `best-state`'s
  cap diagnostic (numbers.md, "Cap diagnostics") found that doubling the action budget barely moves truncation, which points to
  non-terminating actions. Even so, the absolute C levels are lower bounds, and this must be said.
- **Guided read-out.** Policy (2026-10-04) asks for plain and guided numbers for every proof-state evaluation. Only plain was run.
  The r16 reads ran on 2026-10-04, so the rule had just landed. The numbers should at least be labelled "plain".

**Model labels.** run.md and numbers.md name the checkpoints, size, format, from-scratch status and training set, and both say Lean
alone. The cap-12 overlay is labelled as `trajectory` / `rl-continue`, K12, unreviewed. I found no unlabelled number.

**Base reachability (my addition).** None of the 29 r16-solved C pairs was solved at `pend` on the independent sample draw x1
(0/29 on the same seed). Only 2 of the 23 theorems were solved at `pend` x1 by any seed. C was defined on draw x0 alone, so this
second base draw is the honest reachability number. At k = 256 × 2 draws, the gain is not a base-model re-draw.

## §Verdict

**Stands.**
- Every count in the write-up reproduces from the raw files with my own code, and every hard constraint holds.
- The continuation is seamless.
- 1,864 / 1,864 re-checked proofs are accepted by Lean, including every first proof of every new target and every r16 group-C proof.
  The harness rejects all of its negative controls.
- Falsifier 1 does not fire. Falsifier 2 fires: group C pass@256 rose on 3/3 seeds by +0.115 / +0.115 / +0.133, about 3× the r8 seed
  spread, and pass@1 rose by two orders of magnitude.
- "Saturating" is refuted by the run's own pre-registered test. Two independent sample streams corroborate it: the ladder's in-loop
  transfer sampling solved 6 / 6 / 10 of the h250-C theorems by r16, against 2 / 0 / 3 by r8.
- Cap 6's r16 is below cap 12's r8 on all three seeds.

**Must be reworded.**
1. "17 theorems never solved at r8 by any seed" should read either "17 never solved at r8 by a seed whose group C contains them",
   or "9 of 23 not solved by any of the three r8 models (sample seed 1)". 8 of the 17 were in another r8 model's reach.
2. run.md should call the misses misses: new targets and new transfer above range on s1/s2; the per-round decline missed on s2;
   group C not unchanged. It should also state that the holdout250 expectation was not evaluated.
3. Report the truncation fractions per stratum, and say that the group-C levels are lower bounds under a 3–19 % cut-off.
4. Label the read-out numbers "plain". Name the term-size measure (`lean_check` inference nodes).
5. Item 2 ("Cap 6 stays below cap 12") is accurate at r16. It should add that the gap narrowed on every seed (126 → 77, 130 → 116,
   203 → 102 targets) while cap 6 was still adding 2–20 targets per round. "Stops below" is therefore not shown; only "has not yet
   reached".

**Not supported.** Nothing in the write-up is unsupported beyond item 1. The run claims no cross-seed difference.

**Next measurements.**
- An r16 read on sample seed 0 (x0) for group C, plus the full holdout250 at r16. That gives a second draw of the C gain and the
  pre-registered holdout250 number.
- A cap diagnostic on s0's h250-C read (max_action 1,024 / max_steps 192, 18.7 % cut-off) to bound how much C reach the cap hides.
- Rounds 17–24 on the cap-6 ladders, set beside `rl-continue`'s cap-12 r16. Only that can tell "converges to cap 12's ceiling" from
  "stops below it". At the r13–r16 rates, cap 6 would need ≈ 8–15 more rounds to reach cap 12's r16.
