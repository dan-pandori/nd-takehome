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

## Compare (phase 2 — `run_trajectory.md`, `numbers.md` § trajectory, `log.md` read after the recount was committed in 79016ade)

Model for every row: fresh best-cap12 s0 / s1 / s2 (ALiBiGPT 9,560,832 params, `lean_staten`, from scratch on K12,
1,200 s Stage-1 + T1 ladder), Lean-only. The write-up labels its models correctly in its header and in `numbers.md`;
the bracketed `best-state` numbers are labelled as `best-state` best-cap12 (also Lean-only, post-2026-09-27).

| claim (executor) | my value | verdict |
|---|---|---|
| Groups A 232 / 236 / 234, B 54 / 51 / 60, C 36 / 35 / 28, A-lost 0 / 1 / 1 | identical | reproduces |
| Sanity: tb72 r0 32 / 32 / 38, r8 48 / 49 / 54; h250 r0 200 / 204 / 196, r8 238 / 237 / 239 | identical | reproduces |
| Held-out greedy 0.921 / 0.936 / 0.962; ladder cumulative 4,383 / 4,365 / 4,407 of 4,495 | identical (summary files, round_8.json) | reproduces |
| Key-checkpoint table, worst-step medians over theorem-seed pairs (A ev −215 / −4.2 / −2.1 / −1.2 / −1.0 / −1.0; B ev −191 / −8.2 / −6.3 / −4.4 / −1.8 / −1.3; B ref −187 / −7.6 / −5.8 / −4.7 / −4.3 / −4.5; C ref −217 / −9.5 / −8.9 / −9.2 / −9.2 / −9.1) | identical to 0.1 | reproduces |
| pass@1 / pass@256 table (mean over group and seeds, x1) | identical to 0.001 | reproduces |
| Per-step log p values themselves | my CPU re-score of 386 target-checkpoint pairs: max diff 7e-5 nats | reproduces |
| Eventual proof = r8's most likely accepted x0 sample | 0 mismatches / 865; candidate set = accepted set | reproduces |
| B Δ_RL 5.09 / 4.62 / 4.07 (IQM 4.59), Δ_PT 3.42 / 4.06 / 4.79 (IQM 4.09), w1 r0 −6.58 / −6.53 / −5.50, r8 −1.28 / −1.34 / −1.24 | identical (bootstrap CIs within 0.1) | reproduces |
| Finding 1: "The pre-registered headline ('mainly in RL') is **falsified**: Δ_RL ≤ Δ_PT in 2 of 3 seeds" | The 2 / 3 is the *paired* median of (Δ_RL − Δ_PT) (+1.86 / −0.22 / −0.84). The pre-registered falsifier compares group medians, median_B Δ_RL ≤ median_B Δ_PT: 5.09 > 3.42, 4.62 > 4.06, 4.07 ≤ 4.79 → **1 / 3, not triggered**. The pre-registered decision rule (all three seeds in one direction, else "not resolved at n = 3") gives **not resolved**. The miss that *is* clean: Δ_PT predicted −1 to +3, observed +3.4 to +4.8 (3 / 3) | **reword**: "not supported / not resolved at n = 3; Δ_PT far above prediction", not "falsified" by the pre-registered falsifier. The substance ("climbs about as much after step 1,600 as in RL") stands |
| Finding 1: "as much **late** in pretraining as in RL" | Δ_PT runs from step 1,600 (≈ 7 % of pretraining) to the end; the 8k → end part is +1.8 / +2.8 / +3.2 | reword "late" → "after step 1,600" (or quote the 8k → end numbers) |
| Finding 1: "At the end of pretraining B is within reach but improbable: worst step −6.2, total −15, pass@256 0.15" | −6.21; −16.9 / −14.2 / −15.0; 0.074 / 0.176 / 0.183 (x1) | reproduces (pass@256 is biased down by group selection — the write-up says so) |
| Finding 2: "RL lifts its own proofs, **not known ones**": reference Δ_RL +1.5 vs eventual +4.6, 3 / 3; "nearly all at r1" | +1.79 / +0.96 / +1.89 (IQM 1.55, CI [0.79, 2.31] excludes 0) vs +5.09 / +4.62 / +4.07; pooled reference gain pend → r1 +1.03 of +1.31 | numbers reproduce; **reword** "not known ones": RL does lift the known proof (+1.5 nats, CI excludes 0), just less. Part of the eventual-vs-reference gap is by construction (the eventual proof is chosen as r8's argmax, so its r8 likelihood is selected upward); say so |
| Finding 3: "C stays at **one bad step**", worst step ≈ −9 through RL, Δ_RL −0.2 | worst step: reproduces (pooled −8.9 → −9.1; IQM Δ_RL −0.23). But C's references usually have a *second* bad step: median second-worst −6.0 / −6.9 / −7.9 at r0 and −5.7 / −4.2 / −5.0 at r8; 55–86 % have a second step below −4 nats | **not supported** as "one bad step"; reword to "the worst step stays near −9 to −10 nats; most also have a second step below −4" |
| `numbers.md`: "C reference worst step ≤ −8 at every checkpoint ✓" | pre-registered per seed: fails at step 20,000 in s0 (−6.68) and s1 (−7.82); holds at every RL checkpoint and on the across-seed IQM | **reword**: ✓ only on the IQM; per seed a miss in 2 / 3 (at one pretraining checkpoint) |
| `numbers.md`: "C reference Δ_RL < 2 ✓" (IQM −0.23) | per seed −3.29 / +1.46 / +1.13; \|−3.29\| > 2 in s0 | **reword**: miss in s0 (RL makes s0's C references *less* likely) |
| Finding 4: B's r0 worst step a box opener in 82 / 165 (imp 30, neg 28, Or.elim 24), ∧E projection 48 | box openers 82 (30 / 28 / 24) identical; never an `exact` | reproduces |
| Example `la_transfer_1015` (s0, B, eventual): worst step `n1.2` −14.9 end PT, −7.7 r1, −1.1 r4, −0.37 r8; "every other step above −0.6 throughout" | −14.85, −7.66, −1.09, −0.37; other steps ≥ −0.57 at those four checkpoints (in pretraining before the end they reach −3.2 to −106). It is in my heatmap-rule set for B (seed 0) | reproduces ("throughout" = the four quoted checkpoints) |
| Expected vs outcome: group sizes A ✗, B ✗ (2 seeds), C ✓; B r8 pass@1 ✗; A r8 pass@1 ✗; late-PT flat ✗; B pass@256 monotone ✗ (2 / 3, selection); concentration kind ≥ 50 % ✗ marginal | same verdicts | reproduces; misses are reported as misses |
| Limits: "Pretraining reads truncate **0.1–3.5 %** of samples"; `numbers.md`: "pretraining 0–3.5 % (9.8 % at s1's init), RL 0.00–0.15 %" | per checkpoint overall: 0–9.8 % (PT), 0.00–0.15 % (RL) reproduce. **Per stratum (pool × group), which is what the policy's 0.1 % rule is about:** up to 18.7 % in pretraining (s1 step 12,000, h250-C) and 1.7 % in RL (s1 r5, h250-C); 44 / 144 RL strata and ≈ 50 % of PT strata exceed 0.1 % | **reword**: the run doc's "0.1–3.5 %" contradicts `numbers.md`'s own 9.8 %; and the per-stratum rates on C (and on B in pretraining) are much higher than the overall ones. Caps not raising was pre-registered, so this is a disclosure issue, not a protocol breach; truncation can only move C → B |
| Proof size (median actions / term size): eventual A 11 / 7, B 14 / 10; reference A 10 / 5, B 11 / 7, C 11 / 9 | actions identical (C 12 with the 8 bound-22 references, as the write-up notes); term size on my own definition 29 / 40–43 / 24 / 31 / 36–47 — same ordering | reproduces (different size definition; ranks agree) |
| All 315 references and all eventual proofs Lean-accepted | 896 / 896 distinct targets accepted (my renderer + axioms check) | reproduces |
| Compute table; "no arm exceeds 1.25× its sibling seed"; 53.92 pod-hours, $28.00 | `podbudget trajectory`: 53.92 h, $28.00; ladder GPU-s max / min 1.21, reads 1.11; registry has `gpu_seconds`, `gen_tokens`, `lean_checks`, `train_steps`, `train_tokens` rows | spend reproduces; GPU-seconds not re-derived from logs (not derivable independently here beyond the registry rows) |
| Pre-registration before the first pod (gate 0) | commit 68edd09e 06:35:22Z; first pod tj-p0 06:37:01Z (`~/pods.log`); file not changed afterwards | holds |
| Scoring change at 09:25 (stop scoring env-assigned names) "before any group result" | logged as a deviation with its reason; the change is correct for the sampler (the env overwrites those tokens). Caveat (R5a): tokens after an introduced name are scored given the canonical name, while the sampler conditions them on the model's own sampled name | stands; add the caveat |

Hard constraints: none violated (R9). One inherited textbook72 ↔ K12 renaming-class overlap (`P ∨ Q, ¬P ⊢ Q`), as in
`best-state`; it is in A in every seed, so it does not touch B or C.

## Verdict

**Stands.** Every count, group, pass@k value, per-step log p and table entry reproduces from the raw files, and an
independent CPU re-score matches the stored per-step log p to 1e-4 nats. Lean accepts every counted proof checked
(1,350 / 1,350 sampled + 896 / 896 targets; negative controls behave). The sanity check against `best-state` holds.
The pre-registration was committed before the first pod, and its misses are reported as misses. Substantive results that
stand at n = 3:
(i) B's eventual-proof worst step goes from ≈ −6.2 at the end of pretraining to ≈ −1.3 at r8, most of it by r4;
(ii) after step 1,600 that worst step rises about as much in pretraining (+4.1) as in RL (+4.6); the paired difference
spans 0;
(iii) B's eventual proofs gain far more in RL than B's fixed reference proofs (+4.6 vs +1.5, 3 / 3 seeds);
(iv) C's reference proofs do not improve under RL.

**Must be reworded.**
1. "Headline **falsified**": the pre-registered falsifier compares group medians and fires in 1 / 3 seeds. The
   pre-registered rule makes this "not resolved at n = 3". The clean miss is Δ_PT (3 / 3 above its range).
2. "late in pretraining" → "after step 1,600".
3. "RL lifts its own proofs, **not known ones**" → "lifts the known proof too (+1.5, CI excludes 0), three times less".
   Also note that eventual proofs are selected by r8's likelihood, so part of the gap is by construction.
4. "C stays at **one** bad step": most C references have a second step below −4 nats.
5. `numbers.md` ✓ marks for C (≤ −8 at every checkpoint; |Δ_RL| < 2) hold only on the IQM. Per seed, as
   pre-registered, they miss in 2 / 3 and 1 / 3.
6. Truncation: state per-stratum rates (up to 18.7 % in pretraining and 1.7 % in RL, both on C), and fix the run
   doc's "0.1–3.5 %", which contradicts `numbers.md`'s 9.8 %.

**Not supported.** "One bad step" for C (above). No claim rests on `nd_verify`, and none lacks a model label.

**Next measurements.**
(a) To separate selection from learning in Finding 2: pick the eventual proof from an *independent* r8 sample (e.g. the
x1 draw), or score r8's argmax under a held-out seed's r8. Then Δ_RL on eventual proofs is not inflated by choosing
r8's own most likely sample.
(b) Define B by a sample draw disjoint from the pass@k draw at *both* endpoints. This removes the B pass@256 dip at r0.
(c) Score with the within-action name conditioning the sampler actually uses (marginalise the model's own name token)
on a subset, to bound the caveat in R5a.
(d) Re-read the C and pretraining strata at 2× `max_action` to bound truncation's effect on C → B.
(e) 5+ seeds to resolve Δ_RL vs Δ_PT: the measured seed SD (≈ 0.5–0.7 nats per group median) gives an MDD of about
2 nats at n = 3, against a measured difference of +0.5.
