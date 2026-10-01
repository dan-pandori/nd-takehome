# Review — run `trajectory`

Reviewer: agent:claude (role reviewer), a separate session from the executor. Started 2026-10-01 19:00 UTC.
All models below are `best-state`'s **best-cap12** recipe retrained by this run: `ALiBiGPT` 6 × 384, 9,560,832 params
(read from each checkpoint's `extra`), `lean_staten` state environment with environment-assigned names, trained from
scratch on K12 `data/kh/train_k12.jsonl` (155,000 records, cap 12; md5 `800b5486…` matches the pods' setup logs),
training seeds 0 / 1 / 2. "pend" = r0 = the last Stage-1 checkpoint (24,077 / 24,345 / 24,328 steps, 1,200 s);
r1–r8 = T1 ladder rounds. Checker: **Lean only** (all numbers here are post-2026-09-27; `nd_verify` used for nothing).

## Recount (phase 1 — written before reading `run_trajectory.md`, `numbers.md` or `log.md`)

Workspace `~/review/trajectory` (executor write-ups removed). Inputs: the brief
(`nd-rl/docs/proposals/state-env/BRIEF_trajectory.md` + the 2026-10-01 15:46 budget-raise message),
`preregistration/trajectory.md`, the code, and the raw artefacts in `artifacts/tj/` (264 read files `eval/s{seed}_{ckpt}__{pool}_x{sample seed}.jsonl`,
`score/`, `targets/`, ladder `round_*.json`) and checkpoints fetched from the bucket. Reviewer code is in
`review_tj/` (my own: `recount.py`, `analysis.py`, `eventual.py`, `score.py`, `cmp.py`, `splits.py`, `recheck.py`;
`rlean.py` is the ND→Lean renderer + `#print axioms` harness written by the `best-state` reviewer, not by this
run's executor).

### R1. Reads present and well-formed

- All 264 reads exist (3 seeds × 22 checkpoints × 2 pools × 2 sample seeds); every one has k 256, T 0.8,
  `max_steps` 96, `max_action` 512, sample seed = file label; batch 2,048 in 263, **batch 1,024 in one**
  (`s2_r3__h250_x0`, an OOM retry — a sampling re-draw, not a correctness change). Every row has
  `n_tried` 256, `n_ok = n_tried − len(reasons)` and `solved == bool(proofs)` (0 inconsistencies).
- Seed 2's ladder resumed at round 2 with ladder batch 1,024 (args.json; OOM). Rounds 1–8 present for all seeds.

### R2. Sanity vs `best-state` (pre-registered expectation 1; seed-0 samples, x0)

| pool | ckpt | s0 | s1 | s2 | pre-registered range | verdict |
|---|---|---|---|---|---|---|
| textbook72 | r0 (pend) | 32 | 32 | 38 | 22–38 | in (s2 at the edge) |
| textbook72 | r8 | 48 | 49 | 54 | 46–57 | in |
| holdout250 | r0 | 200 | 204 | 196 | 175–205 | in |
| holdout250 | r8 | 238 | 237 | 239 | 230–245 | in |

(Sample seed 1, x1: tb72 r0 34 / 33 / 36, r8 48 / 48 / 53; h250 r0 196 / 205 / 200, r8 240 / 236 / 237.)

### R3. Groups (expectation 2), per training seed, from x0 at pend and r8, 322 theorems

| | s0 | s1 | s2 | predicted |
|---|---|---|---|---|
| A (r0 solves) | 232 (tb 32, h 200) | 236 (32, 204) | 234 (38, 196) | 216 (200–232) |
| B (r8 not r0) | 54 (16, 38) | 51 (18, 33) | 60 (17, 43) | 72 (55–90) |
| C (neither) | 36 (24, 12) | 35 (22, 13) | 28 (17, 11) | 32 (20–45) |
| A-lost | 0 | 1 | 1 | ≤ 4 |

A is above its range in s1, s2 (s0 at the edge); B is below its range in s0, s1. **Expectation 2 missed for A and
B (2 of 3 seeds each); C and A-lost hold.** A-lost is the same theorem in s1 and s2 (`textbook_bcb4f30a22574210fc12`).

### R4. Eventual proofs and reference proofs

- `eventual.py`: per seed the candidate set equals the distinct Lean-accepted r8 x0 proofs exactly (19,969 / 21,672 /
  21,177 proofs over 286 / 286 / 293 theorems; 0 set mismatches); 3 / 4 / 3 candidates fail replay ("too many
  names") and no theorem loses all candidates; the eventual proof equals the argmax of the stored candidate total
  log p (T 1.0) on every theorem (0 mismatches) and is always an accepted r8 x0 sample.
- Reference proofs: 315 = holdout250 250 / 250 (ladder-A minlen: 90 `raw_textbook_minlen`, 160 `pool_long_minlen`)
  + textbook72 **65 / 72** (57 minlen bound 14, 8 minlen bound 22). The 7 textbook72 theorems without a reference
  are C in every seed (6) or A (1); so C has a reference for 30 / 36, 29 / 35, 22 / 28 theorems.
- Every target replays in the environment (601 / 601 / 608; 0 failures).

### R5. Teacher-forced log p — the executor's numbers re-derived

(a) **Independent re-score.** `score.py` (CPU, unpadded, one sequence per forward, my own masking of
environment-assigned names and my own base marginalisation) on checkpoints fetched from the bucket (md5 equal to
`score/ckpts_s*.md5`). Sample: per seed 40 targets (15 B eventual, 10 A eventual,
  8 C reference, 7 other reference; seeded random) at p1600, r0 and r8, base 0 (360 target-checkpoint pairs, against the stored
  `raw_b0_total`), plus 26 targets with the full 33-base marginalisation (17 at p1600, 9 at r0, against the stored
  `total` and w1). **Max |difference| 7.0e-5 nats over all 386; max |Δw1| 4.7e-5.** The stored per-step records are
  what the definition says. (Definitional caveat, not an error: at sampling time the tokens after an introduced name
  are conditioned on the model's own sampled name, which the environment overwrites only after the action; the score
  conditions on the canonical name. The spread of a proof's total over the 33 bases is 2–16 nats on the 9 full-marginal
  targets, so the base marginalisation matters and is done; the within-action conditioning is not quantified.)

(b) **Pre-registered quantities from the per-step records** (`analysis.py`; my w1 = min of `step_lp` at T 1.0; groups
from R3; medians over theorems within seed; across seeds IQM = mean at n = 3 with a stratified bootstrap over
theorems, 2,000 resamples):

| quantity (B = B's eventual proofs unless stated) | s0 | s1 | s2 | IQM [95 %] | prediction | verdict |
|---|---|---|---|---|---|---|
| median w1 at r0 | −6.58 | −6.53 | −5.50 | −6.21 [−6.80, −5.85] | ≤ −5 (−12 to −3) | holds (s2 −5.50 in range, not ≤ −5) |
| median w1 at r8 | −1.28 | −1.34 | −1.24 | | ≥ −1.5 | holds |
| median Δ_RL = w1(r8) − w1(r0) | +5.09 | +4.62 | +4.07 | +4.59 [4.20, 5.30] | ≈ +5 (+3 to +10) | holds |
| median Δ_PT = w1(r0) − w1(p1600) | +3.42 | +4.06 | +4.79 | +4.09 [3.48, 5.01] | ≈ +1 (−1 to +3) | **miss** (above range, 3/3) |
| median_B Δ_RL − median_B Δ_PT | +1.67 | +0.56 | −0.72 | | > 0 | 2/3 seeds |
| paired median of (Δ_RL − Δ_PT) | +1.86 | −0.22 | −0.84 | +0.27 [−0.70, 1.52] | | interval spans 0 |
| falsifier: Δ_RL ≤ Δ_PT in ≥ 2/3, or w1(r0) ≥ −2.5 in ≥ 2/3 | no (1/3) | | | | | not triggered |

Decision rule (pre-registration: all three seeds in the same direction, else "not resolved at n = 3"): Δ_RL > Δ_PT
in 2 / 3 seeds only → **"climbs mainly in RL" is not resolved at n = 3.** Measured seed SD of a group median:
0.51 (Δ_RL), 0.68 (Δ_PT), 0.61 (w1 at r0) — below the pre-registered guess of ≈ 1 nat.

Selection caveat (my own, not pre-registered): B's w1(r8) is biased up because the eventual proof is r8's own most
likely sample, and B membership (x0 fails at r0) biases w1(r0) down; both inflate Δ_RL of eventual proofs. On B's
**reference** proofs (fixed, not selected by r8) Δ_RL is +1.79 / +0.96 / +1.89 against Δ_PT +3.43 / +2.60 / +3.19:
for a fixed known proof the worst step climbs more in pretraining (after step 1,600) than in RL, in all 3 seeds.
On the **total** log p of B's eventual proofs the pretraining climb p1600 → r0 (+22.3 / +21.5 / +23.1) also exceeds
the RL climb (+14.2 / +12.5 / +11.2).

Other pre-registered expectations:

| # | quantity | s0 | s1 | s2 | prediction | verdict |
|---|---|---|---|---|---|---|
| 4 | median total, A eventual, r0 | −3.77 | −4.37 | −3.95 | ≈ −3 (−6 to −1) | holds |
| 4 | median total, B eventual, r0 | −16.88 | −14.18 | −14.96 | ≈ −14 (−25 to −7) | holds |
| 4 | median total, A eventual, r8 | −2.00 | −2.24 | −2.18 | ≈ −1.5 | off by 0.5–0.7 (no range given) |
| 4 | median total, B eventual, r8 | −2.75 | −3.15 | −2.70 | ≈ −3 (−6 to −1) | holds |
| 4 | per-step mean at r0, A − B | 0.87 | 0.85 | 0.64 | ≥ 0.5 | holds |
| 5 | B r0: median w1 − median rest-of-steps mean | −5.85 | −5.88 | −4.92 | ≤ −4 | holds |
| 5 | B r0: w1 is a box opener or box-closing `exact` | 52 % | 49 % | 48 % | ≥ 50 % | **miss in 2/3** (borderline); no w1 was ever an `exact` |
| 6 | median w1 change p8000 → r0, B | +1.80 | +2.77 | +3.23 | < 1.5 | **miss 3/3** |
| 6 | same, A | +1.77 | +2.91 | +2.15 | < 1.0 | **miss 3/3** |
| 7 | C reference median w1 ≤ −8 at every checkpoint | fails at p20000 (−6.68) | fails at p20000 (−7.82) | holds | ≤ −8 everywhere | **miss in 2/3** (holds at r0…r8 in all) |
| 7 | C reference: median of per-theorem w1(r8) − w1(r0) | −3.29 | +1.46 | +1.13 | \|·\| < 2 | miss in s0 (difference of medians −1.95 / +2.83 / −0.56) |
| 8 | Δ_RL: B eventual − B reference | +3.30 | +3.66 | +2.18 | ≥ 1 in 2/3 | holds 3/3 |

w1 kinds at r0 for B (my classifier from the stored action text): atomic-term `have` 26 / 26 / 31, `Or.elim` opener
13 / 5 / 6, imp opener 9 / 9 / 12, neg opener 6 / 11 / 11.

### R6. pass@k (expectations 9, 10): groups from x0, pass@k from x1 (unbiased estimator, n = 256)

| ckpt | A pass@1 / @256 (s0, s1, s2) | B pass@1 / @256 | C pass@256 |
|---|---|---|---|
| p1600 | .036/.328, .031/.309, .037/.333 | .000/.019, .000/.020, .000/.017 | 0, 0, 0 |
| p8000 | .168/.746, .184/.661, .139/.671 | .002/.093, .019/.078, .001/.050 | 0, .029, 0 |
| r0 | .406/.974, .376/.970, .422/.962 | .000/.074, .001/.176, .001/.183 | 0, 0, 0 |
| r1 | .771/.996, .758/.996, .765/.991 | .100/.648, .120/.686, .133/.600 | 0, 0, .036 |
| r4 | .840/1.0, .832/.992, .831/.991 | .466/.926, .414/.882, .435/.933 | .083, .029, .107 |
| r8 | .855/1.0, .845/.992, .853/.991 | .615/.981, .507/.961, .571/.950 | .083, .029, .036 |

Expectation 9: B r0 pass@256 ≈ 0.15 (0.05–0.30) holds; B r0 pass@1 ≈ 0.002 holds; **B r8 pass@1 ≈ 0.3 (0.15–0.5)
missed (0.51–0.62, above range in 3/3)**; B r8 pass@256 ≈ 0.9 holds (0.95–0.98); A r0 pass@1 ≈ 0.35 close (0.38–0.42);
**A r8 pass@1 ≈ 0.6 missed (0.85)**; C r8 pass@256 ≈ 0.05 holds (0.03–0.08).

Expectation 10 (no pretraining checkpoint's B pass@256 exceeds r0's by > 0.10): p20000 exceeds r0 by **+0.111 (s0)
and +0.118 (s1)**, −0.033 (s2) → violated in 2/3 seeds, narrowly. This is very likely a selection artefact: B is
defined by r0's x0 samples failing, so r0's success probability on B is biased down even on the independent x1 draw
(on x0 itself r0's B pass@256 is 0 by construction). It should not be read as "pretraining reaches then loses B".

### R7. Truncation (`max_action` 512, `max_steps` 96 held as `best-state`)

Per-sample cut-offs (`action truncated` + `step cap`) exceed 0.1 % in 99 of 132 (seed × checkpoint × sample-seed)
group cells; largest at the endpoints: s1 r8 x0 tb72-C 0.94 %, s0 r0 h250-A 0.68 %. The pre-registration declared
the caps would not be raised (deviation from the policy's 0.1 % rule, stated in advance). Truncation is highest on C
at r8, i.e. it can only move theorems from C to B.

### R8. Lean re-check (Lean alone decides)

`recheck.py`: negative controls on s0 r8 — untouched 60 / 60 pass; stored `LEANREJ` texts 0 / 60; `Or.inl`↔`Or.inr`
flip at the ORI line 3 / 60 pass (the `A ∨ A` cases, as in the `best-state` review); proof against a mismatched
theorem 0 / 60; `sorry` 0 / 1. Main pass, per training seed, 150 counted proofs per arm (30 longest on distinct
theorems + 120 random) at r0 x0, r8 x0, and a pooled intermediate arm (all other checkpoints, x1): **1,350 / 1,350
accepted**, 0 render failures. **Every eventual and reference target** (896 distinct (theorem, proof) pairs over the
3 seeds): **896 / 896 accepted**, axioms ⊆ {propext, Classical.choice, Quot.sound}.

Term size (my own count: nodes of the elaborated theorem value) against actions and ND lines, medians:

| target set | s0 size / actions / lines | s1 | s2 |
|---|---|---|---|
| A eventual | 29 / 11 / 10 | 29 / 11 / 10 | 29 / 11 / 10 |
| B eventual | 39.5 / 14 / 13 | 43 / 14 / 13 | 42.5 / 14 / 13 |
| A reference | 24 / 10 / 9 | 24 / 10 / 9 | 24 / 10 / 9 |
| B reference | 31 / 11 / 10 | 31 / 11 / 10 | 31 / 11 / 10 |
| C reference | 36 / 12 / 11 | 36 / 12 / 11 | 47 / 12.5 / 11.5 |

B's eventual proofs are longer than B's reference (shortest-known) proofs by ≈ 3 actions / 30–40 % in term size.
My size definition differs from `lean_check`'s (Spearman 0.75 against the executor's `term_size` column), so only
rankings are comparable.

### R9. Splits and hard constraints

- Renaming-class disjointness (`splits.py`: atoms P Q R S permuted, F = falsum fixed, premises sorted — order-insensitive):
  textbook72 vs K12 **1 shared class** (`textbook_3ed45280e6c686e76ac6`, `P ∨ Q, ¬P ⊢ Q`; inherited, the `best-state`
  review found the same one), textbook72 vs `rl_targets` 0, holdout250 vs K12 0, holdout250 vs `rl_targets` 0,
  textbook72 vs holdout250 0; 0 exact-prompt matches anywhere. The ladder trains only on `rl_targets` finds + K12
  replay (`state_ladder_ei.py` mix); transfer / holdout theorems are sampled, never trained on. The ladder's
  `mix_*.jsonl` files were not pulled, so I could not re-check them directly.
- `nd_verify/` blobs identical to `origin/main` (2 files). `artifacts/TEST_RUN_DONE` unchanged versus `origin/dan`;
  `test_run_once.sh` untouched. No `nd_verify` import in the run's code path (`state_eval` → `eval_set.judge` →
  `lean_judge`; ladder imports `lean_judge.verify_text`). `minlen.py` calls `nd_verify` internally to filter
  candidate reference proofs (declared in the pre-registration); every reference is Lean-checked above, so nothing
  counted depends on it.
- No textbook72 / holdout250 path in `state_train*.py`, `state_ladder_ei.py`, `best_model.py`, `pod/tj/{seed,ladder,ladder_resume}.sh`.
  The run's only training-code change is `--save_steps` (checkpoint saving with the schedule clock paused).

No hard-constraint violation.
