# Review — long-pool-2 (reviewer session, 2026-09-30)

Checker throughout: **Lean alone** (`lean_check.py`: nd2lean translation, Lean 4.34 core, allowlist + axiom check,
term size). `nd_verify` was not used by me to judge anything. Code and outputs: `review_lp2/` (my scripts
`rv_lp2_pool.py`, `rv_lp2_rates.py`, `rv_lp2_termsize.py`, `rv_lp2_redraw.py`; they were run from
`~/review/long-pool-2`, a copy of the run with the write-ups removed). The raw stage files (`data/lp2/*`, 178 MB, not
in git) were pulled from `hf://buckets/dan-pandori/nd-rl/long-pool-2/data/lp2`.

Models (read at k 256, T 0.8, seed 0; 3,216,384 params except K12 T1 at 3,214,336 — corrected in phase 2 from `numbers.md`; labels from `lpool_reread.py` args and
`artifacts/lpool2/setup.log`):
- **SN-cap12 T1** = `ckpts/sc12/ladder/la_T1_SN12_s{0-3}_r8.pt` (`lean_staten` state model, from scratch, Stage-1 on
  `kh/train_k12` cap-12 + 8 ladder EI rounds; state-cap12 run).
- **SN-cap12 frozen** = `ckpts/sc12/stage1_SN12_s{0-3}.pt` (the same models' Stage-1 checkpoints, no EI).
- **K12 T1** = whole-proof `lean_seq` K12 T1 s0/s1 (batch 1,024, `max_new` 1,536).
- **SN-v2 cap-6 T1** = state-env v2 cap-6 ladder T1 s0/s1 (long-pool's `la_T1_SN_s{0,1}_r8`).
State models: batch 2,048, `max_action` 512, `max_steps` 96.

## §Recount (phase 1, written before reading `run_long_pool_2.md`, `numbers.md`, `log.md`)

### Hard constraints
| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72…` at HEAD = `origin/main` = `origin/dan`. **Pass.** |
| `nd_verify` as a judge | Re-reads judge through `eval_set.judge` → `lean_judge.judge_many` (nd2lean + Lean). No new script imports `nd_verify`. **Pass.** One caveat: `minlen.py` (the shared labeller, unchanged) checks each proof it finds with `nd_verify.verify_text`. So the stage-E/F "found a proof of 17/18 lines" labels are `nd_verify`-checked by construction. I re-checked all 91 `ub_proof`s in Lean, and all are accepted (below), so every upper bound in the pool stands under Lean. The lower bounds are exhaustive-search bounds over `minlen`'s ND search space, not proof judgements (the POOLS.md caveat). |
| `artifacts/TEST_RUN_DONE` | identical to `origin/main`; no commit on the branch touches it. **Pass.** |
| evaluation file read in training code | No training was run. `transfer_long2` is read only by `lpool2_assemble.py`, `lpool2_analysis.py`, `lpool2_figure.py` and `pod/lpool2/reread_all.sh` (evaluation). **Pass.** |
| gate 0 | pre-registration committed `ea3cfdff` 16:32:46 UTC; first pod `lp2-a` 16:33:47 (`~/pods.log`). **Pass.** |
| spend | RunPod billing for the run's three pods (`5tphq5kghnfhy8`, `k81dz1uaaowcp8`, `78jr51xqe9jrvz`): **$5.82** in total ($1.46 + $2.27 + $2.09). `podbudget`: 17.08 h / $6.29. Within the $10 / 20 h budget. |

No quarantine.

### Pool funnel (own recount from `data/lp2/<chunk>_ml{10,12,14,16,17}.jsonl`, 25 chunks b1–b7, c1–c9, d1–d6, e1–e3)
| quantity | my value |
|---|---:|
| generated records | 231,809 |
| fates A/B/C/D: ≤ 10 / ≤ 12 / ≤ 14 / ≤ 16 | 220,327 / 8,629 / 2,139 / 364 |
| timeouts at bound 10 / 12 / 14 / 16 | 85 / 124 / 84 / 2 |
| lower bound 17 (records) | 55 |
| **distinct renaming classes among the 231,809 generated** | **72,765 (31.4 %)** |
| **distinct lower-bound-17 classes** | **21** (= the 21 rows of `transfer_long2.jsonl`; all keys match) |
| stage-D timeout rate (2 of 421 records reaching bound 16) | 0.5 % |
| minlen core-seconds summed over chunk records, bounds 10/12/14/16/17 | 18,750 / 44,528 / 70,319 / 53,480 / 23,148 (≈ 210 k) |

**Finding P1 (process; it cost most of the pool).** Chunk seeds are consecutive (b 35001–35007, c 36001–36009,
d 37001–37006, e 38001–38003), and `make_coverage_sets.py gen` seeds worker *i* with `seed + i` (W = 4–12). So chunk
b2's workers 35002…35007 re-run chunk b1's workers 35002…35006 with identical `tries`. The streams repeat. Distinct
fraction per family: b 0.285, c 0.261, d 0.374, e 0.388. Only 31 % of the generation and labelling compute went to
new theorems, and the 55 lower-bound-17 records are 21 theorems (34 are copies). At the observed yield, well-spaced
seeds (≥ 1,000 apart; this is also in the VPS memory notes) would have given ≈ 3× the pool, roughly 55–65 new
theorems, at the same spend. The duplicates are otherwise harmless: `lpool2_assemble.py` de-duplicates by
renaming class. They also make an internal consistency check possible: stage E gave the same outcome on every copy
of all 21 classes (0 inconsistent).

### Labels (own re-derivation)
- Stage E, new pool: **13 exact 17, 8 lower bound 18, 0 timeouts** (62 % exact 17). Calibration (70): the first pass
  had 29 OOM worker deaths (`rc=-9`), re-run as `calib_retry`. Merged: **48 exact 17, 22 lower bound 18, 0 timeouts**
  (69 %). The longest search was 1,136 s, under the 1,800 s limit.
- Stage F (bound 18; **not pre-registered**, labelled as added in the assembler): `F` (10 theorems) gave 9 exact 18
  and 1 timeout at 3,617 s. `F2` (30 in) produced 3 results: 1 exact 18 and 2 OOM deaths. The other 27 were never
  searched. Resulting strata: new 13 (17) / 4 (18) / 4 (≥ 18, F open); calibration 48 / 1 / 21. My strata match the
  file's `stratum` and `stageE` fields on all 91 rows. The `ub_proof` of every exact-17 row is the stage-E proof.
- Upper bounds: my own dependency-closure pruning gives `construction_pruned` = `gen_lines` on all 91; the
  construction does not prune, as the pre-registration found. New pool construction lengths 32–48 (median 38);
  calibration 23–49. `L_ub` matches on all 91.
- **Lean check of the bounds:** all 91 `ub_proof`s and all 91 `gen_proof`s accepted by `lean_check`.
- Pre-registered bins by `L_ub` (all 91): 17–18: 66, 19–20: 0, 21–22: 0, 23–24: 1, 25+: 24. The "upper-bound
  quartile" bins (`ub_qbin`) use `L_ub`, which stage E collapses to 17 for exact-17 theorems. They are therefore
  mostly a relabelling of the stratum, not a construction-length axis. I report construction-length bins separately
  below.

### Disjointness (own renaming-class key, ordered and premise-order-invariant)
Scanned 239 files, ≈ 11.2 M records: every `*.jsonl(.gz)` under `~/nd-takehome/data` (163 incl. `train.jsonl`,
`data/p2/pool_cap8`, `r2/train_*`, `p2/train_*`), `/tmp/longpool/excl/*` (the `kh_train_k8add/k10/k12/k14`,
`dsc_train_a1–a4`, `dsg_train_g1–g2`, `ladder_pool_inject_cap6`, `ladder_raw_textbook`, `ladder_reserve` bucket copies)
+ `pool_long.jsonl`, and all 76 files under the run's `data/` (including `ladder/rl_targets`, `ladder/transfer*`,
`transfer_long_rr600`). **The 21 new theorems hit nothing.** The 70 calibration theorems hit only
`data/ladder/transfer_long_ge17.jsonl` (70/70; they are that file, which is the positive control). New ∩ calibration = 0.

### Re-read counts (own recount from `artifacts/lpool2/rr/*.jsonl`; solved = ≥ 1 stored Lean-accepted proof)
| model | new 21: per seed | calibration 70: per seed | all 91: per seed | IQM all 91 (seed bootstrap 95 %) |
|---|---|---|---|---|
| SN-cap12 T1 | 8 / 15 / 17 / 14 | 26 / 44 / 41 / 47 | 34 / 59 / 58 / 61 | 64.3 % [37.4, 67.0] |
| SN-cap12 frozen | 3 / 1 / 3 / 5 | 8 / 15 / 18 / 18 | 11 / 16 / 21 / 23 | 20.3 % [12.1, 25.3] |
| K12 T1 | 0 / 0 | 3 / 2 | 3 / 2 | — |
| SN-v2 cap-6 T1 | 0 / 0 | 4 / 0 | 4 / 0 | — |

On the new 21 alone: SN-cap12 T1 per seed 38.1 / 71.4 / 81.0 / 66.7 %, IQM 69.0 %; frozen 14.3 / 4.8 / 14.3 / 23.8 %,
IQM 14.3 %.

**By stratum, all 91** (exact 17: n 61; ≥ 18 = 5 exact 18 + 25 with F open: n 30):
| model | exact 17 per seed | ≥ 18 per seed | 4-seed mean Δ (17 − ≥ 18) |
|---|---|---|---|
| SN-cap12 T1 | 25 / 43 / 38 / 42 (41.0 / 70.5 / 62.3 / 68.9 %) | 9 / 16 / 20 / 19 (30.0 / 53.3 / 66.7 / 63.3 %) | **+7.3 pp**; theorem bootstrap 95 % [−7.7, +22.6]; seeds +11.0 / +17.2 / −4.4 / +5.5 |
| SN-cap12 frozen | 9 / 11 / 17 / 19 | 2 / 5 / 4 / 4 | +10.5 pp; seeds +8.1 / +1.4 / +14.5 / +17.8 |

Stratum 18 alone (n 5): SN-cap12 T1 2 / 3 / 4 / 4. The two populations (new vs calibration) agree in direction:
new 17 vs ≥ 18 IQM 76.9 vs 56.2 %, calibration 61.5 vs 56.8 %. The new-pool strata are 13 and 8 theorems.

**By construction length after pruning, all 91** (SN-cap12 T1 per seed): ≤ 28 (n 8) 3 / 4 / 5 / 5; 29–32 (19)
5 / 13 / 12 / 14; 33–36 (24) 6 / 12 / 12 / 14; 37+ (40) 20 / 30 / 29 / 28. Top bin ≥ bottom bin on 4 / 4 seeds
(50.0 vs 37.5, 75.0 vs 50.0, 72.5 vs 62.5, 70.0 vs 62.5 %). There is no fall with construction length.

### Step cap, action cap, memory
- `max_steps` 96: 1 step-cap hit in all reads (`T1_SN12_s3__cal`, 1 / 17,920 = 0.006 %). Action-cap (512) / `max_new`
  (1,536) truncations 0–0.056 % per file (maximum `T1_SN12_s2__new`, 3 / 5,376); none exceeds the policy's ≈ 0.1 %. Peak memory 10.6–17.1 GB per read (recorded per file).
- rr600 at `max_steps` 96: s2 **471**, s3 **468** / 600. ≥ 17 file at `max_steps` 96: s2 **42**, s3 **41** / 70.
- **Same-settings redraw.** `T1_SN12_s3_ms96__ge17` and `T1_SN12_s3__cal` have identical args apart from file names
  and `lenfield` (same 70 prompts, seed, batch, caps) but ran on different pods about 7 h apart. They solve **41 vs
  47**, and 8 theorems flip (7 / 1). For s2 it is 42 vs 41 with 11 flips. The earlier `max_steps`-48 rows vs this
  run's 96 differ by −1 … +2 per T1 seed (flips 4–7), which is inside that same-settings spread. So the step-cap
  change has no detectable effect, and per-theorem solved/unsolved on 70 theorems at k 256 moves by ≈ 6–11 flips
  between identical reads.

### Lean re-check of counted proofs (≥ 100 per arm, stored ND text → nd2lean → Lean)
| arm | proofs available | checked | accepted | term size min / med / max | lines min / med / max |
|---|---:|---:|---:|---|---|
| SN-cap12 T1 (pool 91) | 2,717 | 160 (+ all 2,717 in the term-size pass) | 160 (2,717) | 9 / 19 / 42 | 17 / 25 / 44 |
| SN-cap12 frozen (pool 91) | 270 | 160 (+ all 270) | 160 (270) | 9 / 13 / 32 | 17 / 21 / 41 |
| K12 T1 | 9 | 9 | 9 | 10 / 11 / 15 | 17 / 19 / 20 |
| SN-v2 cap-6 T1 | 16 | 16 | 16 | 11 / 13 / 16 | 18 / 20 / 23 |
| SN-cap12 T1 `max_steps` 96, rr600 | 28,067 | 160 | 160 | 5 / 15 / 30 | 11 / 21 / 36 |
| SN-cap12 T1 `max_steps` 96, ≥ 17 file | 1,464 | 160 | 160 | 10 / 20 / 38 | 17 / 27 / 53 |
| pool `ub_proof` / `gen_proof` | 91 / 91 | 91 / 91 | 91 / 91 | 10 / 13 / 42; 14 / 29 / 45 | 17 / 17 / 48; 23 / 35 / 49 |

All 3,012 counted pool proofs across the 12 checkpoints are accepted, so **no counted proof is rejected by Lean**.
No accepted proof is shorter in lines than its row's `L_lb` (minimum written length 17 on exact-17 rows, 18 on ≥ 18
rows).

**Term size vs line strata.** The minimal proof (`ub_proof`) has term size median 12 (10–16) on exact-17 theorems
and median 25 (12–42) on ≥ 18 theorems. Note, though, that ≥ 18 `ub_proof`s are mostly *constructions* (F open), so
they are upper bounds only. Per theorem, SN-cap12 T1's smallest accepted proof has term size median 14 (min 10) on
exact-17 theorems and median 16 (min 9) on ≥ 18 theorems. The ≥ 18 stratum's easiest theorem in term size is
smaller than any exact-17 theorem's minimal proof. On 24 / 78 solved theorems, the model found a proof with a smaller
term size than the pool's `ub_proof`. Under Lean, the line strata 17 / 18 are not a clean difficulty axis in term size.

### Pre-registered expectations — my verdicts
| expectation (pre-registration) | observed (my recount) | verdict |
|---|---|---|
| brief: ≥ 10 % in 17–18, < 10 % in 23–24; falsifier ≥ 10 % in every filled bin; prediction: falsifier fires on all 4 seeds | filled `L_ub` bins 17–18 (66): 40.9–69.7 %; 23–24 (1): 100 %; 25+ (24): 25–62.5 %; ≥ 10 % everywhere on all 4 seeds | falsifier fires (as predicted); 23–24 has n = 1 |
| brief's 17–22 bins hold < 10 theorems each | 17–18 holds 66 (17 new), because stage E sets `L_ub` = 17 | **miss** (19–22 empty as expected) |
| 120–300 new lower-bound-17 theorems (point 180) | 21 distinct (55 records; P1) | **miss** |
| stage-D timeout 5–10 % | 0.5 % | miss (lower) |
| construction ≥ 95 % ≥ 23, median 33–38 | 100 % ≥ 32, median 38 | hit |
| stage E 45–70 % exact 17; timeout 15–45 % | 62 % (new), 69 % (calib); 0 % timeouts | hit / **miss** |
| SN-cap12 T1 new pool 30–70 % per seed, IQM 40–65 % | 38.1 / 71.4 / 81.0 / 66.7 %; IQM 69.0 % | **miss** (2 seeds and IQM above) |
| no monotone fall by upper-bound bin; top ≥ bottom − 10 pp on ≥ 3/4 seeds | by construction bins: top ≥ bottom on 4/4 | hit |
| exact 17 above lb 18 by 0–20 pp (4-seed mean); ≥ 20 pp = frontier | +7.3 pp (all 91), CI [−7.7, +22.6] | hit (no frontier detected; not excluded either) |
| frozen 10–35 % | new: 14.3 / 4.8 / 14.3 / 23.8 %; all 91: 12.1–25.3 % | hit on 91; s1 below on the new 21 |
| K12 T1 1–10 % | new 0 / 0; calib 4.3 / 2.9 % | miss on new pool (0) |
| SN-v2 0–10 %, s0 above s1 | new 0 / 0 (tie); calib 5.7 vs 0 % | hit (s0 > s1 only on calib) |
| rr600 within ± 12 of 476 / 472 | 471 / 468 | hit |
| ≥ 17 file within ± 4 of 42 / 46 | 42 / 41 | s2 hit, **s3 miss** (−5; the same model gave 47 in the calib read) |
| step-cap hits ≤ 0.02 % | 0.006 % in one file, 0 elsewhere | hit |

### Compute record
There are no results-registry rows (`record.py`: `gpu_seconds`, `gen_tokens`, `lean_checks`, …) on the branch. From
the re-read summaries: generation wall-seconds (on the pod GPU, class per `pods.log`/question commit) 38–187 s per
pool read and 1,429 / 1,589 s for the two rr600 reads; samples 5,376 / 17,920 / 153,600 per file. Labelling ≈ 210 k
minlen core-seconds from chunk rows (plus calibration, `lpto` and stage F). No training.

## §Comparison (phase 2: `run_long_pool_2.md`, `numbers.md` §long-pool-2, `log.md` 2026-09-29/30)

| claim (source) | my independent value | verdict |
|---|---|---|
| Pool: 21 new + 70 calibration; strata 61 / 5 / 25; all 91 disjoint; every upper-bound proof Lean-accepted (run, LP2-1) | 21 + 70; 61 / 5 / 25; 0 hits in 239 files / 11.2 M records (a superset of their 118 / 5.74 M); `ub_proof` 91 / 91 | reproduces |
| 231,809 generated → 55 lower-bound-17 → 21 distinct (LP2-1) | 231,809 → 55 → 21 | reproduces |
| Seed overlap: unique worker seeds b 12/42, c 14/54, d 9/24, e 14/36 (log 00:40) | consistent with my distinct-class fractions (b 0.285, c 0.261, d 0.374, e 0.388) | reproduces |
| "About 60 % of the generation and stage A–E CPU was spent on duplicates" (log 00:40) | 68.6 % of generated rows are repeats of an earlier class (72,765 distinct / 231,809) | differs, by ≈ 9 pp; the honest figure is ≈ 69 % of rows (CPU share not separately derivable, but stage A–D time scales with rows) |
| Yield missed for three reasons: small-CPU pods, 5–8 GB per search, overlapping seeds (run) | seeds alone cut the pool ≈ 3× (21 of an expected ≈ 55–65 at the same spend) | stands, but understated: the seed error is the dominant cause, not one of three equal ones |
| LP2-2 brief bins 65 / 0 / 0 / 1 / 25 by best upper bound | 66 / 0 / 0 / 1 / 24 (their own `tables.md` also says 66 / … / 24) | **differs by 1** (transcription error in `numbers.md`) |
| LP2-2 construction-length bins 0 / 0 / 0 / 2 / 89 | 0 / 0 / 0 / 2 / 89 | reproduces |
| LP2-3 per-seed table (all / L 17 / L ≥ 18 (exact 18) / construction bins), 12 checkpoints | identical in every cell | reproduces |
| LP2-3 SN-cap12 T1 IQM all 64.3 % [37.4, 67.0]; L 17 65.6 % [41.0, 70.5] | 64.3 [37.4, 67.0]; 65.6 [41.0, 70.5] | reproduces |
| LP2-3 SN-cap12 T1 "L ≥ 18 56.0 % [28.0, 64.0]", frozen "L ≥ 18 10.0 % [4.0, 20.0]", printed beside an "L ≥ 18 /30" column | Over the n 30 stratum (exact 18 + F open): **58.3 % [30.0, 66.7]** and frozen **13.3 % [6.7, 16.7]**. Their numbers are the n 25 F-open sub-stratum (7/13/16/15 of 25) | **mislabelled** (a right number on the wrong n) |
| Paired per-seed L17 − L≥18 +11, +17, −4, +6 pp, mean +7.5 (run, LP2-3) | +11.0, +17.2, −4.4, +5.5; mean **+7.3** (mean of the rounded values is 7.5) | reproduces to rounding; quote +7.3 |
| MDD between strata of 61 and 30 ≈ 30 pp | 2.8 × √(0.24 (1/61 + 1/30)) = 30.6 pp per seed | reproduces. My theorem-bootstrap 95 % CI on the 4-seed-mean Δ is [−7.7, +22.6] pp |
| "The brief's falsifier fired, as I predicted: ≥ 25 % in every filled bin on every seed" (run) | filled `L_ub` bins: min 40.9 % (17–18), 25.0 % (25+, s0), 100 % (23–24, **n 1**) | reproduces; the 23–24 bin is a single theorem |
| "Its rate *rises* with construction length" (run) | SN-cap12 T1 per seed, ≤ 28 / 29–32 / 33–36 / 37+: s0 37.5 / 26.3 / 25.0 / 50.0; s1 50.0 / 68.4 / 50.0 / 75.0; s2 62.5 / 63.2 / 50.0 / 72.5; s3 62.5 / 73.7 / 58.3 / 70.0 % | **overstated**: not monotone on any seed, and the bottom bin has n 8. What holds: top bin ≥ bottom bin on 4 / 4 seeds, i.e. no fall |
| "Model rates were met" (run) | Pre-registered on the **new pool**: SN-cap12 T1 30–70 % per seed with IQM 40–65 % → observed 71.4 and 81.0 % on s1/s2, IQM 69.0 %; frozen 10–35 % → s1 4.8 %; K12 T1 1–10 % → 0 / 0 | **not supported**: three model expectations missed (T1 high, K12 low, one frozen seed low). On all 91 the T1 and frozen ranges nearly hold, but that is not what was registered |
| Misses listed: pool size, stage-E timeouts, s3's ≥ 17 count (run) | Also missed: brief's 17–22 bins "< 10 each" (17–18 holds 66), stage-D timeout rate 5–10 % (0.5 %), the three model rates above | **incomplete** miss list |
| "The step-cap question is closed: rr600 471 / 468, no sample needs more than 89 steps" (run); LP2-5 "0 step-cap hits" | rr600 471 / 468; 0 hits in the four ms96 reads (max 89 / 86); **1 hit (96 steps) in `T1_SN12_s3__cal`**, which LP2-5 does report | stands for the ms96 reads; "no sample needs more than 89" is too broad because one pool sample hit 96. The s3 ≥ 17 "miss" (41 vs 46 ± 4) is inside the same-settings redraw: the identical s3 read on the same 70 theorems gave 47 (8 flips). Worth saying: the miss is sampling, not the cap |
| LP2-5 action cap 0–0.03 %; peak 10.8–17.2 GB | action-cap truncation up to **0.056 %** (`T1_SN12_s2__new`, their own `caps.md`); peak 10.6–17.1 GB | minor differences; all under the 0.1 % policy line |
| LP2-6 redraw (−1…+2 T1, −2…0 frozen; up to 13 theorems; K12 identical) | identical table | reproduces |
| LP2-7 literal-text re-check 292 / 292, controls 72 / 72 | not re-derived as such; my stronger check: all 3,012 counted pool proofs + 320 rr600/≥ 17 samples accepted | consistent |
| LP2-8 spend $6.29 / 17.08 h; per pod $1.44 / $2.33 / $2.52 | RunPod billing: $1.46 / $2.27 / $2.09 = **$5.82** | reproduces within the budget; `podbudget` over-states lp2-c by ≈ $0.43 |
| Model labels (numbers.md header, run table) | every number names checkpoint, params, format, from-scratch, training set | **pass**; the run.md table also carries the labels |
| Comparisons with earlier numbers name the checker | the inherited numbers (state-cap12 476 / 472 / 42 / 46, long-pool rows) are from 2026-09-29 runs, Lean alone on both sides | pass |
| "Up to length 18, SN-cap12 T1 shows no measurable fall-off" (conclusion) | Δ +7.3 pp, CI [−7.7, +22.6] | stands **as a null at this power**: a fall of up to ≈ 20–30 pp is not excluded |

### Omissions against `AGENT_POLICY.md`
1. **No term sizes anywhere** in `run_long_pool_2.md` or §long-pool-2 of `numbers.md`. The policy requires them beside line counts, and they matter here: the result is stated in ND line strata (17 / 18), and in Lean term size those strata overlap. My values: minimal proofs have term size median 12 on exact-17 theorems; SN-cap12 T1's smallest proof per theorem has median 14 (exact 17) vs 16 (≥ 18), minimum 9 on a ≥ 18 theorem. On 24 of 78 solved theorems, the model's proof has a smaller term size than the pool's `ub_proof`.
2. **No compute record** (`record.py` rows with `gpu_seconds`, `gen_tokens`, `lean_checks`, per arm). The re-read summaries contain `gen_s` and sample counts, so this can be derived (above). No arm-vs-arm compute matching question arises: every model read the same prompts at the same k.
3. Pre-registration deviations are labelled in the log (CPU-second limits from 21:50, `lpto` added then dropped, stage F added, F2 cut). Pass.

## §Verdict

**Stands.**
- The pool itself: 21 new theorems with lower bound 17 (13 exact 17, 4 exact 18, 4 ≥ 18), plus the 70-theorem
  calibration file relabelled with stage E (48 / 1 / 21). Labels reproduce from the raw stage files, upper bounds are
  Lean-accepted, and the pool is disjoint from every training and evaluation file I could find (239 files).
- Every per-seed solved count in LP2-3 / LP2-4 / LP2-6, and every counted proof, is Lean-accepted (3,012 / 3,012).
- The null result, worded as a null: at ND length 17 vs ≥ 18, SN-cap12 T1 shows no detectable fall (Δ +7.3 pp, CI
  [−7.7, +22.6]); the minimum detectable difference is ≈ 30 pp. The brief's falsifier fires. No fall with construction
  length either (top bin ≥ bottom on 4 / 4 seeds).
- Step cap 48 → 96 makes no detectable difference (rr600 471 / 468 vs 476 / 472; every difference is inside the
  same-settings redraw spread).

**Must be reworded.**
- "Model rates were met" → three pre-registered model-rate expectations on the new pool were missed (SN-cap12 T1 above
  70 % on s1/s2 and IQM 69.0 % > 65 %; K12 T1 0 / 0 < 1 %; frozen s1 4.8 % < 10 %). Add the stage-D timeout rate and the
  "< 10 per brief bin" misses to the miss list.
- "Its rate rises with construction length" → "does not fall with construction length (top bin ≥ bottom bin on 4 / 4
  seeds; not monotone; bottom bin n 8)".
- LP2-3's "L ≥ 18 56.0 % [28.0, 64.0]" / frozen "10.0 % [4.0, 20.0]" are the n 25 F-open sub-stratum. For n 30: 58.3 %
  [30.0, 66.7] and 13.3 % [6.7, 16.7]. Mean Δ is +7.3, not +7.5.
- LP2-2 "65 / 0 / 0 / 1 / 25" → 66 / 0 / 0 / 1 / 24.
- The 23–24 bin in the falsifier claim is one theorem.
- The yield explanation should put the seed overlap first (≈ 69 % of generated rows were repeats, not "about 60 %"; it
  cost ≈ 3× the pool).
- The s3 ≥ 17 "miss" (41 vs 46 ± 4): note that the identical s3 read in this run gave 47. It is a sampling redraw, and
  per-theorem results on 70 theorems at k 256 flip by 6–11 between identical reads.

**Not supported / missing.** No term-size reporting (policy); no compute-record rows (policy). Neither changes a
count; both should be added. "Up to length 18" is a statement in ND lines only. Under Lean term size the ≥ 18
stratum is not harder (its easiest theorem has a smaller proof than any exact-17 theorem), so "no fall-off with
length" should say which length.

**Next measurement.** The question is still open: a fall of up to ≈ 20–30 pp at 17 → 18 is not excluded, and nothing
above 18 is labelled. Two measurements would settle it:
1. The same pipeline with **chunk seeds spaced ≥ 1,000**, about ×3 the distinct yield at this spend. Finish stage F on
   the 25 F-open theorems (bound 18 needs > 20 GB per search, so use a ≥ 125 GB-limit pod like `lp2-b`). That gives
   ≈ 60–80 new theorems and splits the ≥ 18 stratum into exact 18 / ≥ 19.
2. For length beyond 19, theorems of **known length by construction** (the executor's own suggestion; e.g. chained
   lemmas), stratified by Lean term size as well as ND lines, read by SN-cap12 T1 s0–s3 and frozen s0–s3 at k 256.
   Pre-register a paired or larger design: with ≈ 60 theorems per stratum, the MDD is ≈ 20 pp.
