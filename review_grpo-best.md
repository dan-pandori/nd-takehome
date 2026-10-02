# Review: grpo-best (reviewer, independent session)

Reviewer started 2026-10-02 23:02 UTC. Phase 1 used `~/review/grpo-best` (the executor's write-ups removed), the
pre-registration `preregistration/grpo-best.md`, the code and the raw artefacts. Every count below comes from the
reviewer's own scripts in `review_gb/` (committed with this file):

- `recount.py`: groups, C solves, the sign test, pass@1 and pass@256 by group, truncation, end reads;
- `compute.py`: mechanics and compute;
- `recheck.py`, `rlean.py`: Lean re-check with controls and term size;
- `splits.py`: split disjointness;
- `c_swap.py`: the headline recounted with the two sample seeds swapped.

The judge is Lean alone, as in the run. No reviewer number uses `nd_verify`.

**Model for every number in this review** (unless the row says otherwise): `trajectory`'s best-cap12 ALiBiGPT, 6 × 384,
9,560,832 parameters, `lean_staten` state environment (the environment assigns names), trained from scratch on K12
(`train_k12.jsonl`, 155,000 generator proofs, lengths 2–12). Its checkpoints are:

| label | checkpoint | what it is |
|---|---|---|
| **pend** | `stage1_best12_s{0,1,2}_b1200.pt` | the base, at the end of pretraining |
| **EI rN** | `trajectory` T1 ladder `la_T1_best12_s{S}_rN.pt` | the inherited expert-iteration arm, not re-run |
| **GRPO arm rN** | `ckpts/gb/gb_<arm>_s{S}_rN.pt` | this run, from the same base for each seed |

Read-outs: textbook72 + holdout250 (322 theorems), `state_eval.py`, k 256, T 0.8, `max_steps` 96, `max_action` 512,
sample seeds 0 (x0) and 1 (x1).

## Recount

### R0. Read-out settings and inputs

- **Settings.** All 136 GRPO read-outs and all 24 EI read-outs used k 256, T 0.8, `max_steps` 96 and `max_action` 512,
  with the sample seed equal to the file's x index. 12 GRPO read-outs ran at decode batch 1,024 rather than 2,048,
  after an OOM. The pre-registration allows this, and changing the batch only re-draws the sample. End reads: 3 of the
  12 held-out greedy reads and 3 of the 12 dev reads also ran at batch 1,024.
- **EI read-outs are the same draws as `trajectory`'s.** `artifacts/gb/ei_eval/*.json` matches `trajectory`'s committed
  summaries on solved count, n, seed and checkpoint, for the 4 files spot-checked (pend and r8, both pools, both seeds).
- **Internal consistency.** In every per-theorem row, `n_tried − len(reasons) = n_ok` (asserted for every file read).
- **Distinct arm.**
  - It stops at r4 (s2's ladder has a partial r5), so it has no r8 read.
  - `gb_distinct_s1oom2048_r2` is the r2 of the crashed first s1 run (upload md5 `0454f374…`). The rerun's r2 has md5
    `4279056a…`.
  - The `gb_distinct_s1_r2` read is dated 20:01 UTC, after the rerun started (14:10). The read logs do not record the
    md5 of the checkpoint they fetched, so which file was read is consistent with the rerun's r2 by timing only, not
    proven.

### R1. Groups (EI sample seed 0: A = solved at pend, B = solved at EI r8 only, C = neither)

| seed | A | B | C |
|---|---|---|---|
| s0 | 232 | 54 | 36 |
| s1 | 236 | 51 | 35 |
| s2 | 234 | 60 | 28 |

These reproduce the pre-registration's A / B / C exactly.

### R2. Headline: group C solved, per seed (s0 / s1 / s2)

The table also gives the IQM over the 3 seeds, with a stratified-bootstrap 95 % interval. At n = 3 the IQM equals the
mean.

| arm | ckpt | C on x1 (headline) | IQM [95 % CI] | C on x0 | C on x0 or x1 | all 322 on x1 | IQM |
|---|---|---|---|---|---|---|---|
| EI | r8 | 3 / 1 / 1 | 1.67 [1, 3] | 0 / 0 / 0 (by construction) | 3 / 1 / 1 | 288 / 284 / 290 | 287.3 |
| GRPO-default | r8 | 2 / 9 / 3 | 4.67 [2, 9] | 4 / 10 / 3 | 4 / 10 / 3 | 278 / 278 / 279 | 278.3 |
| GRPO-unlikely | r8 | 3 / 8 / 4 | 5.00 [3, 8] | 2 / 8 / 4 | 3 / 9 / 4 | 277 / 277 / 279 | 277.7 |
| GRPO-pass@k | r8 | 6 / 19 / 3 | 9.33 [3, 19] | 10 / 18 / 3 | 10 / 19 / 4 | 286 / 301 / 285 | 290.7 |
| EI | r4 | 3 / 1 / 3 | 2.33 | 4 / 1 / 3 | 5 / 2 / 4 | 285 / 280 / 291 | 285.3 |
| GRPO-default | r4 | 1 / 5 / 1 | 2.33 | 1 / 6 / 2 | 1 / 6 / 2 | 273 / 271 / 273 | 272.3 |
| GRPO-unlikely | r4 | 0 / 5 / 2 | 2.33 | 1 / 5 / 2 | 1 / 7 / 2 | 269 / 276 / 275 | 273.3 |
| GRPO-pass@k | r4 | 4 / 9 / 3 | 5.33 | 2 / 11 / 4 | 4 / 12 / 4 | 283 / 286 / 285 | 284.7 |
| GRPO-distinct | r4 | 2 / 2 / 3 | 2.33 | 0 / 2 / 3 | 2 / 2 / 3 | 273 / 266 / 273 | 270.7 |
| EI | r2 | 0 / 0 / 1 | 0.33 | 0 / 0 / 2 | 0 / 0 / 2 | 274 / 277 / 283 | 278.0 |
| GRPO-default | r2 | 2 / 2 / 2 | 2.00 | 2 / 2 / 2 | 3 / 3 / 2 | 271 / 262 / 265 | 266.0 |
| GRPO-unlikely | r2 | 0 / 2 / 1 | 1.00 | 0 / 2 / 2 | 0 / 3 / 2 | 261 / 260 / 267 | 262.7 |
| GRPO-pass@k | r2 | 2 / 6 / 1 | 3.00 | 2 / 6 / 0 | 3 / 7 / 1 | 277 / 272 / 278 | 275.7 |
| GRPO-distinct | r2 | 0 / 4 / 2 | 2.00 | 1 / 2 / 3 | 1 / 4 / 3 | 261 / 259 / 266 | 262.0 |

Against EI at r8, using the IQM on x1 and the pre-registered MDD of 3.5 C theorems:

| arm | IQM difference vs EI | outcome |
|---|---|---|
| GRPO-default | +3.0 | inside the MDD |
| GRPO-unlikely | +3.3 | inside the MDD |
| GRPO-pass@k | +7.7 | outside the MDD, but the seeds give 6 / 19 / 3: one seed (s1) carries it, and the 95 % interval [3, 19] reaches EI's per-seed maximum (3) |

**Robustness: the sample seeds swapped** (`c_swap.py`). Let C′ be the theorems unsolved by pend on x0 and by EI r8 on
x1. Counting C′ solves on x0:

| arm | C′ solved on x0 (s0 / s1 / s2) | mean |
|---|---|---|
| EI | 1 / 2 / 3 | 2.0 |
| GRPO-default | 2 / 11 / 4 | 5.7 |
| GRPO-unlikely | 1 / 9 / 4 | 4.7 |
| GRPO-pass@k | 10 / 19 / 3 | 10.7 |

The ordering survives the swap.

### R3. Bias-free companion: all 322 theorems, pooled over seeds

The test is an exact two-sided sign test. A pair counts as "GRPO-only" when GRPO r8 solves the theorem on x0 or x1 and
EI r8 solves it on neither.

| arm (ckpt) | GRPO-only | EI-only | p | per seed (GRPO-only, EI-only) | within C only: GRPO-only vs EI-only |
|---|---|---|---|---|---|
| GRPO-default r8 | 15 | 38 | **0.0022** (favours EI) | (2, 10) (10, 13) (3, 15) | 15 vs 3 |
| GRPO-unlikely r8 | 15 | 44 | **0.0002** (favours EI) | (2, 13) (9, 14) (4, 17) | 15 vs 4 |
| GRPO-pass@k r8 | 33 | 20 | 0.098 (n.s.) | (9, 6) (20, 4) (4, 10) | 32 vs 4 |
| GRPO-default r4 | 10 | 51 | < 1e-4 | | 6 vs 8 |
| GRPO-pass@k r4 | 21 | 24 | 0.77 | | 14 vs 5 |
| GRPO-distinct r4 | 7 | 53 | < 1e-4 | | 3 vs 7 |

The within-C column is biased towards GRPO: C is defined by EI's own x0 failures, so EI's x0 contributes nothing there.
That column is not the pre-registered test.

So, on the symmetric all-322 test:

- GRPO-default and GRPO-unlikely solve **significantly fewer** theorems than EI.
- GRPO-pass@k is not distinguishable from EI (33 vs 20). One seed drives it: s1 gives 20 vs 4, while s2 goes the other
  way (4 vs 10).

### R4. Sharpening vs support (sample seed 1; pass@1 = mean n_ok/256; pass@256 = fraction solved)

IQM over seeds (per seed in brackets where relevant):

| quantity | pend | EI r8 | GRPO-default r8 | GRPO-unlikely r8 | GRPO-pass@k r8 | GRPO-distinct r4 |
|---|---|---|---|---|---|---|
| A pass@1 | 0.406 / 0.376 / 0.422 | 0.851 | 0.893 | 0.892 | 0.830 | 0.806 |
| A pass@256 | 0.974 / 0.970 / 0.962 | 0.994 | 0.979 | 0.980 | 0.996 | 0.980 |
| B pass@1 | ≈ 0 | 0.564 (0.615 / 0.507 / 0.571) | 0.542 (0.564 / 0.468 / 0.592) | 0.547 (0.549 / 0.475 / 0.616) | 0.460 (0.477 / 0.406 / 0.498) | 0.331 |
| B pass@256 | 0.074 / 0.176 / 0.183 | 0.964 | 0.811 | 0.788 | 0.881 | 0.710 |
| C pass@1 | 0 | 0.000 | 0.057 (0.002 / 0.162 / 0.008) | 0.050 | 0.091 (0.106 / 0.163 / 0.003) | 0.004 |
| C pass@256 | 0 | 0.049 | 0.140 | 0.152 | 0.272 | 0.073 |

### R5. Retention and end reads (r8; held-out = `data/p2/heldout.jsonl` 5,000 at k 1, T 0; dev = `dev1108` at k 64)

| arm | held-out greedy (s0 / s1 / s2) | dev solved / 1,108 (s0 / s1 / s2) |
|---|---|---|
| pend (`trajectory`'s file, same settings) | 0.9206 / 0.9364 / 0.9618 | — |
| EI r8 | 0.9854 / 0.9918 / 0.9942 | 1055 / 1043 / 1060 |
| GRPO-default r8 | 0.9922 / 0.9840 / 0.9898 | 1022 / 1024 / 1031 |
| GRPO-unlikely r8 | 0.9896 / 0.9878 / 0.9888 | 1024 / 1023 / 1034 |
| GRPO-pass@k r8 | 0.9852 / 0.9798 / 0.9852 | 1064 / 1070 / 1039 |

Two observations:

- Every GRPO arm's held-out greedy rises by **+2.3 to +7.2 pp** over its base, and it is already 0.98–0.99 at round 1
  (`round_1.json`).
- EI r8's held-out greedy is at least GRPO-default's in 2 of 3 seeds (s1 and s2).

### R6. Mechanics (from `steps.jsonl`, 561 updates; distinct to r4 or r5)

| arm | fraction of groups with reward variance: mean over the run (s0 / s1 / s2) | first → last update | all-fail fraction, mean | mean reward, update 1 → last |
|---|---|---|---|---|
| default | 0.168 / 0.161 / 0.170 | ≈ 0.6 → 0.04–0.09 | 0.07 | 0.53 / 0.47 / 0.50 → 0.96 / 0.95 / 0.96 |
| unlikely | 0.215 / 0.171 / 0.178 | ≈ 0.6 → 0.06–0.18 | 0.07 | → 0.94 / 0.96 / 0.96 |
| pass@k | 0.438 / 0.434 / 0.446 | ≈ 0.6 → 0.29–0.39 | 0.06 | → 0.91 / 0.90 / 0.91 |
| distinct | 0.386 / 0.434 / 0.430 | ≈ 0.6 → 0.23–0.35 | 0.10 | → 0.90 / 0.86 / 0.85 |

Targets solved cumulatively at r8 (`round_8.json`):

| arm | of 4,495 (s0 / s1 / s2) |
|---|---|
| default | 4,323 / 4,341 / 4,344 |
| unlikely | 4,331 / 4,334 / 4,350 |
| pass@k | 4,411 / 4,401 / 4,371 |

Resumed runs and their optimiser state (`resume_r*.json`):

- default s2 resumed at r4 with a **fresh AdamW** and at r5 with the saved state.
- pass@k s2 resumed at r6 with a **fresh AdamW**.
- distinct s0 resumed at r2 and distinct s1 at r3, both with a **fresh AdamW**.

The pre-registration does not cover resetting the optimiser state on resume.

### R7. Compute

The step logs and the registry rows (`artifacts/grpo-best/registry/`; registry sums include steps redone after a crash)
give:

| arm | GPU-s (registry, s0 / s1 / s2) | train tokens | train steps | gen tokens | Lean checks |
|---|---|---|---|---|---|
| EI (pre-reg, A6000, alone) | 22,350 / 24,467 / 27,021 | 754 / 783 / 751 M | 4,800 | — | — |
| default | 25,250 / 24,571 / 28,861 | 217 / 210 / 225 M | 561 / 561 / 620 | 340 / 336 / 384 M | 1.32 / 1.33 / 1.48 M |
| unlikely | 25,460 / 24,825 / 25,061 | 277 / 226 / 222 M | 561 | 344 / 339 / 338 M | ≈ 1.33 M |
| pass@k | 25,392 / 25,271 / 29,360 | 141 / 128 / 132 M | 561 | 355 / 355 / 352 M | ≈ 1.29 M |
| distinct (to r4 / r5) | 31,713 / 34,112 / 32,392 | 668 / 864 / 800 M | 340 / 420 / 421 | 321 / 358 / 326 M | 0.80–0.94 M |

- **GPU-seconds.** GRPO ladders ran two per card, so their GPU-seconds are co-tenant wall-clock. They come to
  1.00–1.13× EI's, or up to 1.09× for pass@k s2, which ran on an A40 according to Addendum 1.
- **Train tokens.** Default, unlikely and pass@k used **0.17–0.37×** EI's train tokens.
- **Distinct arm.** By r4 it had used 1.2–1.4× EI's full-r8 GPU-seconds and 0.9–1.1× EI's full-r8 train tokens, so
  ≈ 2–3× EI's at matched r4. **It exceeds 1.25× its comparator**; policy requires the write-up to flag this.

### R8. Lean re-check of counted proofs (own renderer `review_gb/rlean.py`; `#print axioms` ⊆ {propext, Classical.choice, Quot.sound})

**Controls, run first in the same files:**

| control | n | Lean-accepted | expected |
|---|---|---|---|
| untouched counted proofs | 60 | 60 | all pass |
| samples the run recorded as Lean-rejected (`fail_example` with reason `lean rejected`) | 60 | 0 | all fail |
| `Or.inl` ↔ `Or.inr` flip at the ORI line | 60 | 4 | nearly all fail |
| proof paired with another theorem of the same premise count | 60 | 0 | all fail |
| bare `sorry` | 1 | 0 | must fail |

All 4 flips that passed are benign: each is an introduction into `S ∨ S`, `R ∨ R` or `P ∨ P`.

Two harness bugs turned up before the clean pass:

- One Lean process died mid-file and left 60 EI proofs without an axioms line. These were scored as failures, as they
  should be. All 60 pass on their own, and a recursive re-check now handles a dead process.
- Stored rejected samples carry a `LEANREJ ` prefix, which first made that control trivially fail.

**Counted proofs.** For each arm: every distinct counted proof of a group-C theorem in its last read (r8; distinct r4;
both sample seeds), plus a seeded random sample of 100–144 other counted proofs.

| arm | re-checked | Lean-accepted | term size (Expr nodes) median / max | ND lines median / max |
|---|---|---|---|---|
| EI r8 | 150 (6 C) | **150** | 44.5 / 222 | 15 / 31 |
| GRPO-default r8 | 235 (135 C) | **235** | 37 / 227 | 15 / 34 |
| GRPO-unlikely r8 | 400 (300 C) | **400** | 84 / 156 | 20 / 47 |
| GRPO-pass@k r8 | 727 (627 C) | **727** | 38 / 264 | 15 / 42 |
| GRPO-distinct r4 | 299 (199 C) | **299** | 45 / 161 | 20 / 43 |

**0 of 1,811 counted proofs rejected.** Two further checks:

- The stored `written_lens` equal the reviewer's ND line count for all 1,811.
- The samples are weighted to C, so the medians describe the re-checked set, not each arm's population.

### R9. Split disjointness (`splits.py`)

The reviewer's class key is the minimum over atom permutations of (sorted premises, conclusion); F is falsum. Because
the premises are sorted, this key is stricter than `gen.canon_key`.

| training file × evaluation pool | shared renaming classes |
|---|---|
| K12 × textbook72 | 1 (`textbook_3ed45280…`, `P ∨ Q, ¬P ⊢ Q`: group B/A/A, not C) |
| K12 × holdout250 | 0 |
| K12 × dev1108 | 1 |
| K12 × heldout_p2 | 22 of 5,000 |
| rl_targets × textbook72 / holdout250 / heldout_p2 | 0 |
| rl_targets × dev1108 | 1 (`la_transfer_307`) |

All of these overlaps are inherited from the shared pools: this run created no data file. **No group-C theorem is in
any training file.** The 22 held-out overlaps (0.44 %) can move held-out greedy by at most 0.44 pp.

### R10. Hard constraints

- **`nd_verify/`:** the tree hash `9437bb72…` is identical on `HEAD`, `origin/main` and `origin/dan`.
- **`artifacts/TEST_RUN_DONE`:** the blob `1d5cf064…` is identical on `HEAD`, `origin/main` and `origin/dan`.
- **`nd_verify` as a judge:** `grpo_state.py`, `state_sample.py`, `state_eval.py`, `eval_set.py` and `grpo_adv.py` do
  not import or call it. Reward and evaluation go through `lean_judge.judge_many`.
- **Evaluation files in training code:** `grpo_state.py` reads only `--targets` (trained on), `--transfer` and
  `--heldout` (evaluated, never used in updates). No `data/bs/` file (textbook72, holdout250, dev1108) is read by
  training code.

No hard-constraint violation.

### R11. Truncation (fraction of samples ending on the action cap, the step cap or exhausted names)

The policy threshold is 0.1 % of any reported stratum.

- **Within threshold or close to it.** GRPO-default, unlikely and pass@k at r8 are at most 0.11 % overall. Their worst
  reference-length stratum is 0.13–1.7 %.
- **Above threshold.** Several strata of the 322 exceed 0.1 %:
  - EI r8: worst stratum 2.9–6.6 %.
  - GRPO-distinct r4 s0: **2.9 % overall, 23.8 % in its worst stratum**.

  So distinct-arm counts are depressed by the length cap, and EI's B / C counts may be slightly understated.

The distinct-arm numbers in R2 and R3 are therefore a lower bound.

## Compare (phase 2: `run_grpo_best.md`, `numbers.md` § grpo-best, `log.md`, `STATUS.md`, `figures/grpo_best.png`)

Every number in the table is on the models above (best-cap12 s0–s2, 9.56 M ALiBiGPT, `lean_staten`, from scratch on
K12). Lean alone is the checker on both sides.

| claim (executor) | reviewer value | verdict |
|---|---|---|
| Groups A/B/C = 232/54/36, 236/51/35, 234/60/28 | same | reproduces |
| C solved at r8, sample seed 1: EI 3/1/1; default 2/9/3; unlikely 3/8/4; pass@4 6/19/3 | same (R2) | reproduces |
| IQM Δ vs EI +3.0 / +3.3 / +7.7 (MDD 3.5); bootstrap 95 % intervals in `analysis_stdout.txt` | same, with the same intervals | reproduces. `run_grpo_best.md` shows no interval; the pass@4 interval is [3, 19] |
| C solved, either sample seed (pooled, "17, 16, 33 against EI's 5") | 17 / 16 / 33 vs 5 | reproduces, but **the comparison is unequal**: EI's sample seed 0 cannot solve a C theorem (C is defined by it), so EI gets one draw against GRPO's two. On sample seed 1 alone the totals are 14 / 15 / 28 vs 5 |
| All 322 at r8, sample seed 1: 288/284/290; 278/278/279; 277/277/279; 286/301/285 | same | reproduces |
| textbook72, sample seed 0, at r8 | same | reproduces |
| Arm-only vs EI-only, all 322, pooled: 15 vs 38 (p 0.0022), 15 vs 44 (p 0.0002), 33 vs 20 (p 0.098); within C 15/3, 15/4, 32/4 | same (R3) | reproduces |
| pass@1 / pass@256 by group at r2 / r4 / r8 (IQM, sample seed 1) | every cell agrees to the stated precision | reproduces |
| Held-out greedy at r8 (all arms); dev metric per seed; dev means 1,053 / 1,026 / 1,027 / 1,058 | same | reproduces. "Dev metric is 26 lower" is 26–27 |
| C solves with a ⊥-elim + DN proof: 2/5, 7/17, 8/16, 13/33 (`gb_peirce.py`) | same, with the reviewer's own predicate (some accepted proof contains both BOTE and DN) | reproduces. This read-out was **not pre-registered** and is not labelled as post hoc |
| Peirce's law: pass@4 s0 r8, 230/256 accepted | 230/256 on both sample seeds | reproduces |
| ... term size 10 | the reviewer's Expr-node count for the 20 shortest-listed proofs is 25–44 | **not derivable as stated**: the measure behind "10" is not named. Presumably `lean_check` inference nodes; the write-up should say |
| Mechanics: default variance fraction 0.38 → 0.07, mean 0.17; pass@4 0.54 → 0.37 | round means 0.37–0.39 → 0.07; run means 0.16–0.17; pass@4 0.54–0.55 → 0.36–0.38 | reproduces |
| Mechanics: reward 0.72 → 0.95 (round means) | step 1 → step 561: 0.53 → 0.96 | consistent (a different window) |
| Compute table and "no pre-registered ladder > 1.25× EI (max 1.09×)" | registry sums identical; max 29,360 / 27,021 = 1.09 | reproduces |
| Train tokens 0.17–0.37× EI's | 0.17–0.37 | reproduces |
| Distinct arm compute | 31.7–34.1 k GPU-s and 668–864 M train tokens, by r4 / r5 | **not flagged**. It exceeds 1.25× EI's *full-r8* GPU-seconds (1.27–1.42×), and ≈ 2–3× EI's at matched r4. Policy asks for the flag on any arm, optional or not. Restarts inflate it |
| Truncation: EI 0.050 % (worst read 0.41 %), default 0.010 %, unlikely 0.011 %, pass@4 0.011 %, distinct 0.58 % (worst read 6.2 %) | identical per read (action-truncated + step cap) | reproduces as defined, but **per read, not per stratum**. Policy (> 0.1 % of any reported stratum) is breached: EI r8 2.9–6.6 % and default 0.4–1.7 % in their worst `reference_lines` strata, distinct 23.8 %. These are small strata, so the effect on the counts is a few theorems at most. "Names exhausted" endings (a further 0.02–0.06 %) are not counted |
| Gate 0: pre-registration before the first pod | commit `fa5d9b0` 11:24:52Z; `~/pods.log` gb-p0 created 11:32:35Z; Addendum 1 at 11:49, after the smoke and before the ladders, appended only | holds |
| Resumes: default s2 (fresh, then saved AdamW), pass@4 s2 (fresh) | same in `resume_r*.json` | reproduces. Distinct s0 and s1 also resumed with a fresh AdamW (log.md only) |
| Distinct s1 r2 relabelled `oom2048` (crashed-run checkpoint, md5 0454f374) | the same md5s in the logs | consistent |
| Spend 68.10 pod-h, $35.27 | not re-derived (`podbudget` ledger) | not checked |

### Expected vs outcome (the write-up's scoring, checked)

| prediction | outcome (reviewer) | write-up | verdict |
|---|---|---|---|
| E1, IQM part | pass@4 +7.7 > MDD; default and unlikely inside | "E1 missed for pass@4" | right |
| E1, per-seed range 0–5 | missed by **all three arms**: default s1 9, unlikely s1 8, pass@4 6 and 19 | mentioned for pass@4 only | **under-reported** |
| E2 | pass@4 ≥ default (59 vs 31) holds; unlikely within ±2 of default (29 vs 31) holds; pass@4 − default 4.7 > MDD, a miss | as stated | right |
| E3 | 15 vs 38, favours EI | "hit" | right |
| E4 | B pass@1 below EI and in range (arm IQMs); B pass@256 in range; A pass@1 0.89 for default and unlikely, above the band | "mostly hit" | right |
| E5, part 1 | +2.3 to +7.2 pp above base, so outside "within 3 pp" | "missed upward, 2.5–7 pp" | right; the low end is 2.3 |
| E5, part 2 | EI ≥ default in 2 of 3 seeds (s1, s2): a hit | not mentioned | omission |
| E6 | variance mean 0.17 (miss); reward rise (hit) | "missed" | right |
| E7 | GPU-s hit; train tokens miss | as stated | right |
| "Changes the story" | IQM condition met by pass@4; all-322 p = 0.098 | "not met" | right |

### Wording

- **Finding 1 overstates for default and unlikely.** As worded ("GRPO reaches theorems that EI from the same checkpoint
  does not. All three arms do"), it is literally true theorem by theorem, but the symmetric test (R3) says the reverse
  is more true: EI reaches 38 and 44 that they miss, against 15. Their C differences are inside the MDD, which the
  pre-registration calls "not resolved". The finding should say "GRPO-default and -unlikely solve different theorems,
  not more", and keep the claim of reaching more for pass@4 only. Finding 2 already says this; finding 1's heading
  should not contradict it.
- **pass@4 "beyond the MDD" is one seed's effect.** The rule is the pre-registered one and it is met. But:
  - the MDD assumed EI's between-seed sd (1.15), while pass@4's own sd is 8.5 (6 / 19 / 3);
  - a Welch t-test on the seeds gives t ≈ 1.55 (not significant at n = 3);
  - the bootstrap interval [3, 19] touches EI's maximum.

  What does stand: the paired per-seed differences are positive in 3 of 3 seeds (+3, +18, +2), and the seed-swap
  robustness check (R2) gives the same order. Suggested wording: "pass@4 exceeds EI on C in all three seeds, by 2 to 18;
  the mean difference passes the pre-registered MDD, but most of it is seed 1".
- **"EI never solved" is wrong.** The figure's panel (a) title says "Group C (EI never solved)", and `STATUS.md` says
  "EI's never-solved theorems". C is "unsolved by pend and by EI r8 on sample seed 0". EI r4 solves 3 / 1 / 3 C
  theorems, and EI r8 solves 3 / 1 / 1 on seed 1. Peirce's law is C for s0 and s1 but solved by EI s2 (245 / 256).
- **The ⊥-elim + DN read-out should be marked post hoc.** It was not pre-registered.
- **Every number carries its model label.** `run_grpo_best.md` opens with the models, `numbers.md` repeats them, and
  the figure title carries them. Inherited EI numbers are labelled `trajectory` T1 on RTX A6000.
- **Checker labels.** No comparison crosses the 2026-09-27 date. The run-4 finding is cited in the pre-registration as
  "under Lean ∧ `nd_verify`", which is correct.

## Verdict

**Hard constraints:** none violated (R10). There is no quarantine.

**Stands:**

- **Counts.** Every pre-registered count reproduces from the per-theorem files, with independent code.
- **Lean.** All 1,811 re-checked counted proofs pass Lean in a harness whose five negative controls behave.
- **Gate 0 and splits.** The expectations were committed before the first pod. Splits are clean for every group-C
  theorem.
- **Default and unlikely trade theorems.** At equal sampled attempts, from the same checkpoints, they solve some group-C
  theorems EI misses, but significantly fewer theorems overall (all-322 sign test p = 0.002 and 0.0002, pooled over 3
  seeds). Their dev metric is lower in every seed.
- **pass@4 shifts towards coverage.** It keeps ≈ 0.4 of its groups mixed, has the highest C pass@256 (0.27 vs EI's
  0.05) and the lowest A / B pass@1 of the r8 arms. It is level with EI on all 322 (33 vs 20, p 0.098, not resolved).
- **Retention.** Held-out greedy at r8 is 0.98–0.99 for every arm (EI included), up from 0.92–0.96.
- **Compute.** Each pre-registered GRPO ladder used 1.00–1.13× EI's GPU-seconds (co-tenant) and 0.17–0.37× its train
  tokens.

**Must be reworded:**

1. Finding 1's lead, so that it covers pass@4 only and treats default and unlikely as "different, not more" (above).
2. pass@4's C excess: per-seed +3 / +18 / +2, mostly seed 1. Do not cite the IQM alone.
3. "17 / 16 / 33 against EI's 5" (both sample seeds): either drop it or state that EI's seed 0 contributes 0 by
   construction. On seed 1 alone it is 14 / 15 / 28 vs 5.
4. "EI never solved", in the figure title and in STATUS.
5. E1's per-seed band was missed by all three arms, not only pass@4. E5's low end is 2.3 pp, and E5's second half
   (EI ≥ default in 2 / 3 seeds) is a hit.
6. Name the term-size measure behind "term size 10", and label the Peirce / ⊥-elim + DN count as post hoc.
7. Flag the distinct arm's compute (> 1.25× EI on GPU-seconds), and report truncation per stratum: the strata above
   0.1 % are listed in R11.

**Not supported as worded:** "GRPO reaches theorems that EI does not", as an unqualified headline for all three arms.

**Next measurements that would settle what is open:**

1. **More seeds for pass@4 against EI on C.** With 3 seeds and one outlier, the arm's sd is ≈ 8. Five to ten
   base-checkpoint seeds (fast Stage-1 makes them cheap), with the same paired per-seed difference and the same
   all-322 sign test, would show whether s1's +18 is typical or a lucky trajectory.
2. **A fresh third sample draw (seed 2) of every r8.** Groups are then defined on one draw and scored on an untouched
   one for both arms. This removes the selection effect without new training.
3. **Peirce's law in particular.** pass@4 solves it on s0 and s1, where EI never does in either draw, and default and
   unlikely solve it on s1. A per-seed log-p trace of its reference proof along both ladders would show whether this
   is acquisition or a near-miss that EI's K12 replay suppresses.
