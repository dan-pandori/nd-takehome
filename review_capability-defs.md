# Review — run `capability-defs` (proposal 26: what "capability" should mean, and how to measure it)

Reviewer: agent:claude (role reviewer, independent session, `--effort max`), 2026-10-05.
Phase 1 was done in `~/review/capability-defs/`, a copy of the run's repository with the executor's write-ups removed.
I wrote all the code myself; it is in `review_cd/` (`rv_*.py`, `rlean.py`, `g4ip.py`), with each script's output saved
beside it as `*.log`. I read the executor's code only to learn its definitions (the budgets K, the set rules, the IRT
priors). I did not read its outputs (`capability_defs/analysis/out/`), `REPORT.md`, the cards, `numbers.md` or
`run_capability_defs.md` before committing this section.

**Models (labels used throughout).**
- **cap 12, best-cap12:** `best_model.ALiBiGPT` 6×384, 9,560,832 params, `lean_staten`, trained from scratch on K12
  (`data/kh/train_k12.jsonl`, 155,000 records, md5 800b5486), Stage 1 for 1,200 s, seeds s0–s2.
  - init = p0, pretraining checkpoints p50 … p20000, pend: trajectory's.
    pend md5s are 2bf801fd / eaff7f4d / abca9c63.
  - r8: trajectory's T1 EI ladder, md5 f9afd386 / c85481f9 / 3b62784b.
  - r16: rl-continue's, md5 324de94f / 7ea8c8bb / f7924ccd.
- **cap 6, best-cap6:** the same recipe on `data/p2/train_depth3_f0_a1.jsonl`.
  - pend md5 dacd64d0 / 360900c4 / 427ef388.
  - r8 md5 586baf0b / a8dfc589 / 1b1843d5.
  - r16 md5 d9d196d6 / 787bce93 / d4aa898c.

Every checkpoint md5 in this run's results-registry rows (`hf://buckets/dan-pandori/nd-rl/registry/capability-defs`)
matches these. Unless a row says otherwise, numbers are cap 12, plain sampling at T 0.8, k 256, `max_steps` 96 and
`max_action` 512, Lean alone.

**Read files.** My loader (`review_cd/rv_load.py`) reads the original per-theorem read files of trajectory,
trajectory-cap6, rl-continue(-cap6), mcts-a (`artifacts/cd/in/`), rl-from-ckpt and this run's J-jobs. The executor read
organism-analysis's compacted copies instead. I compared the two on all 540 reads (n_ok, n_tried and the proof sets)
and they are identical.

## §Recount (phase 1, before reading the write-up)

### R0. Hard constraints — no violation

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72` on HEAD = `origin/main` = `origin/dan` |
| `artifacts/TEST_RUN_DONE` unchanged | blob `1d5cf064` = `origin/main` |
| existing code modified? | `git diff 4dcd0e4f..HEAD` (the base, `origin/dan` at branch time): only additions, plus `.gitignore`, `QUESTIONS.md`, `STATUS.md`, `log.md`, `numbers.md` |
| `nd_verify` used as a judge? | not imported by `capability_defs/analysis/*.py`, `cd_score.py` or `pod/cd/*.sh`. Reads gate with `lean_gate` (Lean on the literal text; the pre-filter only rejects); J3 Lean-checks every finished guided proof (`guided_eval.py`) |
| evaluation files read in training | training jobs (J4, J6, J6b, J7) read only `data/cd/j4/mix_*.jsonl`, `data/cd/k12_nodn.jsonl` and `data/kh/train_k12.jsonl`. J6's Stage 1 passes `--heldout data/p2/heldout.jsonl`, used for logged validation loss only: `state_train_best.py` saves the final step and selects nothing. That is the standard Stage-1 recipe |

**Expectations before runs (gate 0).**
- The pre-registration (3e6f9865) was committed at 05:43:47, before the first pod (cd-a, 06:02:38). Every later job's
  expectations were committed before its first log line:

| job | pre-registration commit | first log line |
|---|---|---|
| J1–J4 | a882373d 06:01:57 | J1 06:05:34, J2 06:07:56, J4 06:59:39 |
| J5 / J3 cap 6 | 5905c89a 06:30:02 | 06:31:49 / 08:24:45 |
| J6 | 637fce06 06:37:44 | 06:39:28 |
| J2 A′ / B | 80bc390b 06:50:45 | 09:07:43 |
| J6b | d3d795d0 07:01:45 | 10:05:39 |
| J1 stage 2 | 3bf28832 07:06:48 | 07:23:05 |
| J7 | f2bad5f4 07:25:00 | 07:34:18 |
| J2 doubled-cap amendment | 50ea6815 07:56:58 | runs inside J2b from 09:07 |
| J8 | 25fa65f7 08:10:23 | 08:12:22 |
| J9 | a0a1c353 10:39:30 | 11:33:29 |
| J10 | b35862fe 11:07:18 | 11:35:10 |

- `demos.json` was rewritten at 07:01, after J4 started, to add C16n. Its A4 / A16 / C16 entries match the mixes J4
  trained on.

### R1. Lean re-check of counted proofs (`rv_recheck.py`, `rlean.py`; Lean 4.34.1 core)

- **Method.**
  - Each theorem is checked one per line; a proof passes iff its line has no error **and** `#print axioms` lists
    only `{propext, Classical.choice, Quot.sound}`.
  - ND-string proofs are rendered to Lean by my own renderer (no `LEAN_GATE_DUMP` was set, so the literal sampled
    text of state-env reads is not stored).
  - J3's guided proofs are checked from the **stored literal Lean text**.
  - Term size = nodes of the elaborated proof term.
- **Controls first, all as expected:**
  - untouched counted proofs: 60 / 60 pass;
  - the run's own recorded `LEANREJ` samples (J2, J4–J10, including every J9 fail example): 0 / 150 pass;
  - an `Or.inl`↔`Or.inr` flip at the ORI line: 2 / 60 pass, both benign (`Or.inl` into `Q ∨ Q` and `S ∨ S`);
  - a proof paired with another theorem of equal premise count: 0 / 60;
  - literal text paired with another theorem: 0 / 40;
  - `sorry`: rejected through the axiom check.

| arm | counted proofs re-checked | Lean-accepted | term size median (max) | ND lines median (max) |
|---|---|---|---|---|
| J2 pend, standard caps (all stages; every distinct proof of a B theorem (r8 x0 or r16 x1) + sample) | 362 | 362 | 45 (152) | 13 (29) |
| J2 doubled caps (the one distinct success) | 1 | 1 | 23 | 12 |
| J9 pend (both successes) | 2 | 2 | 46, 53 | 10 |
| J10 pend, long pool | 150 | 150 | 77 (196) | 25 (44) |
| J3 guided cap 12, literal text (every pend proof of a B theorem + others) | 1,170 | 1,170 | 36 (245) | — |
| J3 guided cap 6, literal text | 200 | 200 | 31 (437) | — |
| J4 reads | 150 | 150 | 55.5 (311) | 16 (37) |
| J5 reads (r16 x0, cap-6 r16) | 150 | 150 | 48.5 (223) | 16 (40) |
| J6 reads | 150 | 150 | 30 (145) | 10 (26) |
| J6b reads | 120 | 120 | 95 (203) | 25 (33) |
| J7 reads | 265 | 265 | 42 (121) | 15 (21) |
| r8 x0 proof of every B theorem–seed pair (the counted RL successes) | 165 | 165 | 54 (223) | 17 (45) |
| known proofs carrying pend's known-proof sum (top 3 per B or r16-B theorem–seed pair, J1) | 510 | 510 | 38 (172) | 12 (28) |
| reference proofs (`ref_targets.jsonl`) | 315 | 315 | 26 (119) | 9 (19) |

**No counted proof is rejected by Lean (3,710 / 3,710).**

**Proof size.** The 165 B theorem–seed pairs (r8 x0 equal-k set) all have a reference proof. For each pair I drew one
accepted r8 x0 proof at random. It is larger than the reference in term size in 155 pairs, equal in 8 and smaller in 2
(median 54 vs 31 nodes).

### R2. Splits by renaming class (`rv_splits.py`)

- **Canonical key:** the minimum over the 24 bijections of {P, Q, R, S} of (sorted premise multiset, conclusion).
  F is falsum, not an atom.
- **Training files:** the J4 / J6b mixes A0, A4, A16, C16, A16n and C16n; the no-DN K12; full K12 (J7).
- **Evaluation pools:** textbook72, holdout250, the 40 held-out A ∨ ¬A instances (lem40), `data/p2/heldout.jsonl`
  and `transfer_long2`.

| training file | records | tb72 | h250 | lem40 | p2 held-out | long2 | records with a DN line |
|---|---|---|---|---|---|---|---|
| mix A0 / A4 / A16 / C16 | 20,000 – 20,064 | 0 | 0 | 0 | 3 | 0 | 2,764 – 2,828 |
| mix A16n / C16n | 20,064 | 0 | 0 | 0 | 0 | 0 | 64 / 0 |
| `k12_nodn` | 133,726 | **1** | 0 | 0 | 21 | 0 | 0 |
| full K12 (J7) | 155,000 | **1** | 0 | 0 | 22 | 0 | 21,274 |

- **The tb72 hit is K12 itself, not this run's doing.**
  - `textbook_3ed45280e6c686e76ac6` (`P ∨ Q, ¬P ⊢ Q`) is in K12 with its premises in the other order
    (`¬P, P ∨ Q ⊢ Q`). `gen.canon_key` is premise-order sensitive, so it misses this.
  - Every best-cap12 model was pretrained on it, and J6 and J7 trained on it again.
  - It is in s0's equal-k created set B: s0 pend 0 / 512 on x0 + x1, r8 235 / 256.
- **Demonstrations:**
  - J4's 16 / 4 A ∨ ¬A demos and the 16 control proofs come from `rl_targets`. None is in any evaluation pool's
    class.
  - None of the 16 A16 demo theorems is intuitionistically provable.
  - Each demo appears exactly 4× in its mix.
  - A16n has 64 DN records: the 16 demos × 4, so the knockout's replay itself has 0.

### R3. Hard set, J2 set, equal-k created sets (`rv_sets.py`; Q1, Q9, J5)

**H, J2 and the calibration pool.**
- H_s (pend 0 / 512 on x0 + x1): **86 / 77 / 77**. This equals the executor's `sets.json`.
- J2_s, "H theorems that r8 or r16 solves in some read":
  - On r8's pool reads x0 / x1 / x2 plus r16 x1 I get **57 / 59 / 55**, equal to the executor's.
  - mcts-a's C-only r8 reads (x4, k 256; x10, k 2,560) are also reads of r8. Counting them adds s0 +3
    (`textbook_03549…`, `…58b532…`, `…9fa52…`) and s2 +2 (`la_transfer_205`, `textbook_fef8f…`), giving 60 / 59 / 57.
    These 5 went to stage A′ instead.
  - So A′ ("hard theorems no RL read solved") contains 5 theorem–seed pairs that r8 did solve in a C-only read.
- Calibration pool (pend 3–100 of 512): 83 / 93 / 71. The 30 sampled per seed are a subset.

**Equal-k created set B** (pend 0 / 256 and RL ≥ 1 / 256 on the same draw):

| seed | r8 x0 | r8 x1 | r16 x1 | r16 x0 (J5) | Jaccard r8 x0 vs x1 | Jaccard r16 x1 vs x0 | rel (p̂_pend < 0.05, p̂_r8 ≥ 0.5), x0 | rel / eqk |
|---|---|---|---|---|---|---|---|---|
| s0 | 54 | 58 | 61 | 60 | 0.78 | 0.78 | 71 | 1.31 |
| s1 | 51 | 46 | 65 | 67 | 0.70 | 0.78 | 62 | 1.22 |
| s2 | 60 | 54 | 61 | 65 | 0.68 | 0.68 | 60 | **1.00** |

- Seed Jaccard of B (r8 x0), pairs s0–s1 / s0–s2 / s1–s2: 0.35 / 0.39 / 0.34.
- Cap 6: B = 101 / 132 / 122 (r8 x0), 108 / 130 / 130 (r16 x1); redraw Jaccard 0.82 / 0.86 / 0.82.
- J5: cap-6 r16 solves 232 / 233 / 232 of holdout250 on x1, against cap-6 r8's 225 / 226 / 221.

### R4. J2 large-k base sampling (`rv_j2.py`; pend_s, T 0.8, standard caps)

| seed | stage A: J2 theorems with ≥ 1 success in 16,384 | A′: H − J2 with ≥ 1 in 16,384 | stage-A zeros still 0 / 65,536 after B | doubled-cap re-reads (16,384): successes |
|---|---|---|---|---|
| s0 | **27 / 57 (0.47)** | 0 / 29 | 23 / 30 (0.77) | 0 of 2 |
| s1 | **22 / 59 (0.37)** | 1 / 18 | 31 / 37 (0.84) | 0 of 1 |
| s2 | 34 / 55 (0.62) | 0 / 22 | 14 / 21 (0.67) | `textbook_6997…` 2 / 16,384 (it also had stage-B successes at standard caps) |

- With the wider J2 set (60 / 59 / 57; the 5 extra theorems were sampled in A′ at the same 16,384), the share is 0.45 / 0.37 / 0.60.
- The set re-read at doubled caps is exactly the stage-A zeros with > 0.1 % of attempts cut off: 2 / 1 / 3 theorems.

**Cut off per stratum** (action truncated + step cap; attempt-weighted; theorems over 0.1 % in brackets):

| stratum | s0 | s1 | s2 |
|---|---|---|---|
| stage A | 0.268 % (4 / 57) | 0.030 % (2 / 59) | 0.129 % (8 / 55) |
| calibration | **1.856 %** (4 / 30; max 48.8 %) | **1.159 %** (3 / 30) | 0.230 % (4 / 30) |
| A′ | 0.037 % | 0.017 % | **0.410 %** (5 / 22; max 7.6 %, not re-read) |
| B | 0.474 % | 0.021 % | 0.089 % |

### R5. Teacher-forced bracket (J1; `rv_bracket.py`)

**Budgets**, from trajectory's `compute.json` (the T1 ladder ran on RTX A6000):
- K_total = ladder GPU-s / read cost per attempt = **3.49 M / 3.29 M / 4.29 M**. In attempts: 1.79 M / 1.79 M / 2.01 M.
- K_per = K_total / 4,495 = **777 / 731 / 954**. In attempts: 399 / 399 / 447.
- K_eval-set = ladder GPU-s / (322 × J2's A40 cost per attempt). That is 19.4 k / 21.2 k / 23.4 k with my 3.586 ms
  (s0_c00: 470 s / 131,072). The executor's constant is 3.6 ms, which gives 19.3 k / 21.1 k / 23.3 k.
- The A6000 ladder seconds are divided by an A40 per-attempt cost. That mixes GPU classes.

**F(t) and the scorer.**
- Rebuilt from every read available at the time plus the 315 references, F(t) equals the J1 targets **exactly** on
  every H ∪ CAL theorem: 0 targets come from nowhere and 0 read proofs are missing.
- Stage 2 scored all but 5 / 2 / 2 of the J2-found proofs. The unscored ones belong to theorems pend solves anyway.
- Replay failures: stage 1 0.02 / 0.04 / 0.08 %; stage 2 0.
- J1's exact 33-base scores of reference proofs reproduce trajectory's own `tj_score` totals (pend, r8, init) to
  < 5×10⁻⁵ nats on 783 theorem–checkpoint pairs.
- The stage-1 bound b0 − ln 33 never exceeds the exact score (0 violations in 94,544 comparisons).

| quantity (B = eqk r8 x0, LB at T 0.8) | s0 | s1 | s2 |
|---|---|---|---|
| B in H (J1-scored) | 50 / 54 | 42 / 51 | 49 / 60 (50 scored, one via CAL) |
| Q3: LB ≥ 1 / K_total (factor-2 margin) | 40 / 54 = 0.74 (0.74); of the 50 scored, 0.80 | 30 / 51 = 0.59 (0.59); of 42 scored, 0.71 | 44 / 60 = 0.73 (0.73); of 50 scored, 0.88 |
| Q3: LB or sampling lower bound ≥ 1 / K_total | 0.81 | 0.76 | 0.92 |
| Q3: created at K_total (UB95 < 0.05 / K_total) | 0 | 0 | 0 |
| Q4: LB ≥ 1 / K_per | 3 / 54 = 0.06 | 0 / 51 = 0.00 | 8 / 60 = 0.13 |
| at K_eval-set: LB certifies / LB or sampling / created | 0.41 / 0.48 / 3 | 0.37 / 0.55 / 2 | 0.43 / 0.62 / 2 |
| Q5: median over scored B of LB − max_y log π_pend(y) | **0.33 nats** | **0.45** | **0.44** |
| Q6: ev log π_pend < −ln K_total and LB ≥ −ln K_total | 22 / 54 = 0.41 | 15 / 51 = 0.29 | 22 / 60 = 0.37 |
| Q7: share of B pairs with RL's share of the bits over init < 2 % (ev proof, T 1.0) | **0.815** (max 4.4 %) | **0.843** (max 4.2 %) | **0.883** (max 2.7 %) |
| Q15: calibration median Σ_F π_pend / p̂_pend (T 0.8; p̂ over 4,864 attempts) | 0.982 [0.90, 1.02] | 0.940 [0.85, 1.00] | 0.925 [0.85, 0.95] |
| same, T 1.0 | 0.79 | 0.65 | 0.65 |
| J1 stage-1 expectation: median of the stage-1-only bound / p̂ | 0.027 | 0.027 | 0.025 |
| CAL theorems whose known-proof sum exceeds the sampling UB95 | 2 | 1 | 1 |

### R6. J3 guided reads (`rv_j3.py`; `guided_eval.py --arm logical`, k 256, seed 1)

- **Inputs.** `h250_gt.jsonl` has the same names and prompts as holdout250; the tb72 dev / train files have
  textbook72's prompts.
- **Guided ≥ plain x1** in solved@256 at **18 / 18** checkpoints (cap 12 and cap 6; s1 r16 cap 12 is a tie at 303).
- **Q13**, the guided pend read solves B (r8 x0): **27 / 54 (0.50), 28 / 51 (0.55), 36 / 60 (0.60)**. For r16-x1 B it
  is 0.49 / 0.45 / 0.57.

| solved@256, guided (plain x1) | pend | r8 | r16 |
|---|---|---|---|
| cap 12 s0 | 260 (230) | 293 (288) | 295 (291) |
| cap 12 s1 | 266 (238) | 289 (284) | 303 (303) |
| cap 12 s2 | 270 (236) | 297 (290) | 303 (295) |
| cap 6 s0 | 212 (171) | 274 (268) | 284 (277) |
| cap 6 s1 | 188 (144) | 277 (269) | 281 (274) |
| cap 6 s2 | 202 (143) | 274 (260) | 284 (272) |

### R7. Excluded middle (`rv_lem.py`; J4, J6, J6b, Q10, Q11)

- **The instance sets.**
  - lem40 = the 40 held-out transfer A ∨ ¬A instances. My own G4ip (`g4ip.py`) agrees with the repo's `intuit.py`
    on all 2,647 prompts I tested. It finds exactly one intuitionistic lem40 instance, `la_transfer_882`, whose right
    disjunct ¬((Q∧R)∧¬R) is intuitionistic.
  - lem39 = the other 39.
  - Every control-arm success on lem40 is `la_transfer_882`.
- **pass@256 of an instance** = 1 if ≥ 1 of 256 attempts is accepted. The rate is the mean over instances.

| lem39 solved@256 (mean pass@1) | s0 | s1 | s2 |
|---|---|---|---|
| pend | 0 / 39 | 0 / 39 | 0 / 39 |
| r16 | 0 / 39 | **36 / 39 (0.70)** | 13 / 39 (0.13) |
| pend + A0 (replay only) | 0 | 0 | 0 |
| pend + A4 | 36 (0.66) | 33 (0.35) | 36 (0.64) |
| pend + A16 | 37 (0.79) | 34 (0.68) | 37 (0.83) |
| pend + C16 (16 non-LEM controls) | 0 | 0 | 0 |
| no-DN knockout | 0 | 0 | 0 |
| knockout + A0 / + A16 | 0 / 35 | 0 / 37 | 0 / 37 |
| J6b: A16n − C16n gain, pend vs knockout (mean of 2 fine-tune seeds) | 0.923 vs 0.872 (+0.051) | 0.910 vs 0.923 (−0.013) | 0.910 vs 0.923 (−0.013) |

- **The six holdout250 A ∨ ¬A instances** (`la_transfer_478, 1572, 956, 795, 1453, 1424`):
  - pend 0 / 6 on x0 and x1, every seed;
  - s1 r16 6 / 6 (x1 and x0), s1 r12 2 / 6, s2 r16 1 / 6, s0 r16 0 / 6;
  - pend + A16 6 / 6, 5 / 6, 6 / 6.
- **J4 holdout250 solved@64:** A16 vs A0 is 216 vs 204 (+5.9 %), 222 vs 207 (+7.2 %), 210 vs 205 (+2.4 %).
- **J6:**
  - Held-out greedy, knockout vs pend: 0.862 vs 0.921, 0.848 vs 0.936, 0.862 vs 0.962. The drops are 0.058 / 0.089 /
    0.100.
  - Knockout holdout250 solved@256 is 0.878 / **0.800** / 0.850 × pend's x1 count.
  - The knockout solves lem40 1 / 40, 0 / 40, 1 / 40, the one being `la_transfer_882`.
  - It trained 24,227 – 24,495 steps in 1,201 s, against trajectory's pend 24,077 – 24,345.

### R8. IRT, my own binomial 2PL (`rv_irt.py`)

- **Model.** MAP with θ ~ N(0, 4²), b ~ N(0, 4²), log a ~ N(0, 0.5²), the executor's stated priors.
- **Fit.** Item parameters come from the 42 pretraining examinees (3 seeds × p0 … pend, x0 + x1 pooled, 322 items).
  RL checkpoints and J7 are projected with the items fixed.

| | s0 | s1 | s2 |
|---|---|---|---|
| θ pend / r8 / r16 (x1) | −0.33 / 1.71 / 2.04 | −0.37 / 1.53 / 1.94 | −0.23 / 1.78 / 1.83 |
| Q8a: Spearman(1-D predicted p, observed rate), r8, 322 items | **0.571** | **0.592** | **0.561** |
| Q8b: θ_r8 > every pretraining θ | yes | yes | yes |
| J7 (i): θ_cont (gain over pend), inside [pend + 0.5, r8]? | 0.18 (+0.51), yes | 0.25 (+0.62), yes | 0.25 (**+0.48**), no |

- Q8a variants (0 < rate < 1 only; items pend fails; solved indicator) range 0.41 – 0.69. None reaches 0.7.
- **Fit stability.** A refit from a random start reaches the same optimum (−log posterior 952,326.2 vs .1). θ shifts
  as a whole by ≈ 0.1, the posterior being flat in that direction, but the J7 gains are +0.505 / +0.622 / +0.474.
  J7 (i) is therefore borderline: s0 and s2 are within 0.03 of the +0.5 threshold.
- Q8c, s1 r16, the six holdout250 A ∨ ¬A instances in the top decile:
  - of positive residuals: 3 / 6 (raw count), 5 / 6 (standardised), 4 / 6 (log-odds);
  - of all 322 items: 4 – 5 / 6.

### R9. J7: compute-matched continued pretraining

**Read results.**
- Solved@256: 220 / 214 (s0, x0 / x1), 215 / 208 (s1), 219 / 224 (s2).
- Against pend x0 (232 / 236 / 234) it gains 19 / 19 / 16 theorems and loses 31 / 40 / 31.
- It solves 19 / 54 (0.35), 18 / 51 (0.35) and **16 / 60 (0.27)** of B (x0).
- r8 x0 solves 286 / 286 / 293, more than J7 on every seed.

**Compute.**
- J7 trained 28,054 / 31,462 / 33,535 steps in **18,308 / 20,494 / 21,824 s**.
- That is **82 / 84 / 81 %** of the r8 ladder's 22,350 / 24,467 / 27,021 GPU-s. The ladder ran on RTX A6000, J7 on A40.

### R10. Q12, pretraining-compute equivalent (`rv_q12.py`)

| | s0 | s1 | s2 |
|---|---|---|---|
| (a) set level: my IRT θ vs ln(step) over p3000 … pend, extrapolated to θ_r8 | 6.1× | 4.7× | 7.0× |
| (b) per B theorem: log π of r8's eventual proof (T 1.0) vs ln(step), median | 7.2× [IQR 3.0 – 23.7] | 5.3× [3.2 – 10.2] | 15.6× [5.3 – 95] |

### R11. Q16, extrapolation backtest (`rv_extrap.py`)

**As pre-registered** (support-curves s1 / s3 files: 3.2 M `lean_seq` WP base and EI r8, seeds 0 / 1, 383 theorems at
10,000 attempts).
- The rows hold counts, not attempt sequences, so I drew "the first 256 attempts" by hypergeometric thinning, which
  is exact in distribution for exchangeable attempts, with 50 replicates.
- I fitted a beta-binomial (BB) and a zero-inflated BB (ZIBB) by ML on (c₂₅₆, 256), and predicted Σ_t P(solved at
  10,000).

| model | observed solved@10,000 | BB median relative error | within ±25 % | ZIBB median relative error |
|---|---|---|---|---|
| WP base s0 | 45 / 383 | **−0.29** [−0.41, −0.17] | 32 % of replicates | −0.29 |
| WP EI s0 | 121 / 383 | +0.06 | 100 % | −0.11 |
| WP base s1 | 37 / 383 | **−0.28** [−0.37, −0.16] | 24 % | −0.28 |
| WP EI s1 | 144 / 383 | +0.10 | 100 % | −0.08 |

**The executor's adaptation** (small sample = pend x0 + x1 + x2 (+ x4) on the 322; target = J2 stage A on the J2
theorems):
- BB predicts 26.8 / 28.8 / 29.5 against an observed 27 / 22 / 34. The errors are −0.01 / **+0.31** / −0.13.
- ZIBB predicts 8.7 / 9.8 / 13.1, errors −0.68 / −0.55 / −0.61.

### R12. J8, elicited share by rl-from-ckpt start (`rv_j8.py`, `rv_j8_sound.py`)

- **New-solve sets** (ladder solves at r8, x0 ∪ x1; its start fails 0 / 512) **equal the executor's on all 12**
  (start, seed) pairs.
- **Every J8 target** (708,992 / 691,165 / 702,082) appears in a Lean-accepted read or is a reference.
- Replay failures: 0.02 %.

LB at the stage-1 bound, with the factor-2 margin:

| share elicited at K_total ≈ 3.5×10⁶ (at 2×10⁴) | p1600 | p5000 | p12000 | p16000 | pend |
|---|---|---|---|---|---|
| s0 | 0.21 (0.01) | 0.29 (0.01) | 0.41 (0.01) | 0.32 (0.01) | 0.77 (0.38) |
| s1 | 0.33 (0.02) | 0.24 (0.01) | 0.34 (0.01) | 0.42 (0.00) | 0.70 (0.33) |
| s2 | 0.25 (0.00) | 0.22 (0.01) | 0.34 (0.01) | 0.34 (0.00) | 0.86 (0.44) |
| n new solves (s0 / s1 / s2) | 182 / 157 / 167 | 117 / 123 / 149 | 86 / 109 / 106 | 76 / 48 / 90 | 53 / 43 / 50 |
| replay-only control from the same start solves (s0) | 151 / 182 | 74 / 117 | 57 / 86 | 40 / 76 | 15 / 53 |

- The share is **not monotone** from pend down to p1600 on any seed.

### R13. J9 certification and J10 long pool (`rv_j9j10.py`)

**J9** (pend_S, T 0.8, standard caps).

| seed | theorem | J9 successes / attempts | total with J2 | certified at K_eval-set (0 successes in > 59.9 K) |
|---|---|---|---|---|
| s0 | `la_transfer_2060` | 0 / 1,179,648 | 1,245,184 | yes |
| s0 | `la_transfer_205` | 0 / 1,179,648 | 1,245,184 | yes |
| s0 | `la_transfer_1077` | 0 / 1,179,648 | 1,245,184 | yes |
| s1 | `la_transfer_1648` | 0 / 1,310,720 | 1,376,256 | yes |
| s1 | `la_transfer_1077` | **1** / 1,310,720 | 1,376,256 | no |
| s1 | `la_transfer_2060` | 0 / 1,310,720 | 1,376,256 | yes |
| s2 | `la_transfer_1648` | **1** / 1,048,576 (stopped) | 1,114,112 | no |
| s2 | `la_transfer_1833` | 0 / 1,441,792 | 1,507,328 | yes |
| s2 | `la_transfer_2060` | 0 / 1,441,792 | 1,507,328 | yes |

- **Certified: 7 / 9 pairs, 5 distinct theorems.**
  - The UB95 values are 2.4 / 2.2 / 2.0 ×10⁻⁶, against 0.05 / K_eval-set = 2.6 / 2.4 / 2.1 ×10⁻⁶.
- **Both J9 successes are proofs already in F.**
  - Lean accepts both.
  - Their known-proof sums predicted 0.026 (s1 1077) and 0.70 (s2 1648) expected successes.
- **Selection.**
  - Re-derived with all the data (`cm` on r8 x0, no seed's pend ever succeeds incl. J2 stage B, replay-only control
    fails x0, top 3 by r8 pass@1), it reproduces s0 exactly.
  - s1 and s2 both chose `la_transfer_1648`, which **s0's pend solved 5 / 49,152 in J2 stage B**. All 3 distinct
    proofs are in F.
  - So 1648 fails the "no seed's base ever solved t" rule on the final data. The rule's next picks would have been
    `textbook_03549…` (s1, r8 3 / 256) and `textbook_48e30…` (s2, 42 / 256).
  - Counting other seeds' bases, only `la_transfer_2060` (all three seeds), `205` and `1833` are certified with no
    base of any seed ever solving them. 1077 was solved by s1's base in J9.
- **Cut off.**
  - `la_transfer_1833` (s2) has 0.49 % of its J9 attempts cut off and 1648 (s2) 0.32 %.
  - J9 rows keep only the top-20 failure reasons. Up to 11 failures per theorem are not itemised, so these are
    lower bounds.
  - 1833's doubled-cap re-read (J2 t, 16,384) found 0.

**J10** (pend, 16,384 attempts per theorem on `transfer_long2`).
- The selection (r8 or r16 x0 solves, pend x2 0 / 256) reproduces: 13 / 16 / 16 theorems.
- **29 / 45 pairs (0.64) get ≥ 1 base success** (9 / 13, 10 / 16, 10 / 16).
- Cut off: 0.017 / 0.015 / 0.053 %.

### R14. Definitions, floors and agreement (`rv_defs.py`; Q14)

I re-implemented the run's 12 final definitions from the protocols in `cd_part3.py`'s docstring and code:

| key | definition |
|---|---|
| `eqk` | equal-k set |
| `cm` | pend 0 / 256 on the draw; over all standard-cap pend attempts n ≥ K_eval-set and p̂ < 1 / K |
| `rel` | `cm` and p̂_R ≥ ½ |
| `tfmax` | best known proof π_pend < 1 / K |
| `brk_ne` | H and not certified elicited at K, with a factor-2 margin |
| `irt` | DIF+ items that pend fails, from my own IRT |
| `schema` | key-step holdout250 family members, using my G4ip |
| `guided` | `cm` and pend's guided read 0 |
| `sharp` | ρ ≥ ½ |
| `npnt` | `cm` and R's rule sets absent from every pend-accepted proof |
| `chain` | `cm`, holdout250, first ladder round ≥ 2 |
| `ood` | no R proof uses a K12 rule set |

| set size | s0 r8 x0 | s1 r8 x0 | s2 r8 x0 | s0 r16 x1 | s1 r16 x1 | s2 r16 x1 |
|---|---|---|---|---|---|---|
| eqk | 54 | 51 | 60 | 61 | 65 | 61 |
| cm (cm0: base 0 in all) | 22 (18) | 21 (17) | 14 (8) | 25 (22) | 34 (30) | 17 (11) |
| rel | 12 | 9 | 5 | 12 | 14 | 8 |
| tfmax | 29 | 27 | 24 | 31 | 39 | 26 |
| brk_ne | 29 | 26 | 25 | 32 | 38 | 23 |
| irt | 26 | 26 | 30 | 33 | 37 | 35 |
| schema | 0 | 2 | 0 | 0 | 11 | 0 |
| guided | 19 | 17 | 13 | 23 | 30 | 16 |
| sharp | 48 | 42 | 46 | 55 | 59 | 50 |
| npnt | 5 | 4 | 0 | 4 | 11 | 2 |
| chain | 14 | 14 | 10 | 14 | 23 | 12 |
| ood | 14 | 20 | 20 | 14 | 29 | 23 |
| cm minus J7's solves | 18 | 17 | 14 | 22 | 32 | 16 |
| cm, no seed's pend ever succeeds | 4 | 5 | 5 | 6 | 15 | 8 |

- **Redraw Jaccard** (r8 x0 vs x1) is high for the budget definitions: cm 0.84 – 0.87, tfmax / brk_ne 0.84 – 0.89,
  sharp 0.91 – 0.93. For eqk it is 0.68 – 0.78.
- **Seed Jaccard** is low: 0.06 – 0.44 for all but ood (0.55 – 0.62).
- **Agreement (Q14)**, mean off-diagonal Jaccard over the 12: **0.29** (r8 x0) and **0.34** (r16 x1).
  - The least-agreeing pairs all involve `schema` (0.00 – 0.06).
  - The K_total bracket is not among the 12. Its created set is empty on every seed (R5), so its Jaccard with any
    non-empty set is 0.

**Threshold sensitivity** (`rv_sens.py`; r8 x0; K = m × K_eval-set; cm / tfmax / brk_ne):

| m | s0 | s1 | s2 |
|---|---|---|---|
| 0.1 | 38 / 42 / 43 | 36 / 41 / 40 | 36 / 42 / 37 |
| 0.3 | 33 / 34 / 36 | 28 / 34 / 34 | 28 / 32 / 32 |
| 1 | 22 / 29 / 29 | 21 / 27 / 26 | 14 / 24 / 25 |
| 3 | 21 / 26 / 25 | 20 / 24 / 23 | **3** / 21 / 19 (6 undetermined: n < K) |

### R15. Compute and spend (registry rows; `~/podhours.log`)

**Registry rows.** Every job family has `gpu_seconds`, and the read jobs also have `gen_tokens`, `attempts`, `actions`
and `lean_checks`. The training jobs (J4, J6, J6b, J7) also have `train_steps` and `train_tokens`.

| family | GPU-hours |
|---|---|
| J9 | 21.3 |
| J7 | 17.9 |
| J3 guided (`arm` = `logical`) | 9.1 |
| J2 B (J2b) | 6.6 |
| J8 | 4.5 |
| J2 | 4.0 |
| J6b | 3.0 |
| J6 | 2.4 |
| J4 | 2.2 |
| J1 | 2.1 |
| J5 | 1.9 |
| J10 | 1.9 |
| **total** | **77.0** |

- **Pods:** 11 A40 pods (cd-a … cd-k), **77.2 pod-hours, $37.84** at $0.49 / h. That is inside the $50 / 100 h budget
  and under the pre-registered $40 stop rule.
- **Peak memory** is recorded in every read summary: J2 18.8 – 25.3 GB at batch 2,048; J9 up to 38.0 GB.

### R16. Literature (L1, L2) — reviewer sub-audit (`review_cd/lit/LIT_AUDIT.md`, own scripts, no downloads)

| L1 quantity | value |
|---|---|
| unique papers in `screened.md` | 191 rows, 6 cross-reader duplicates: **185** |
| overlap with the two earlier reviews | **0**. Matched by arXiv id, DOI, URL, normalised / fuzzy title. Positive control: 109 / 109 earlier papers detected |
| in-depth notes | **57**, covering 60 papers. 41 read at section depth, 16 in full, 0 abstract-only. None is about an earlier-review paper |
| claim ledgers | 1,183 rows; **99.75 % V** (L1 100, L2 99.52, L3 100, L4 99.46, L5 100, L6 99.48 %). Two of the 3 UNVERIFIED rows are placeholders, not claims |
| executor's re-check | n = **32** (≥ 30 as pre-registered), **0 errors**. Reproducible only with an undocumented "status V" filter |
| sub-auditor's re-verification | **48 / 48** sampled V claims found verbatim (8 differ only in math markup), 0 location errors |
| automated scan of all 1,180 V rows | 1 wording change: "stumble" vs "stumbles" |
| REVIEW.md sentences traced to V rows | 12 / 12 sampled; 2 imprecise |

**Minor discrepancies (D1 – D11 in the sub-audit).**
- One counted paper (row 105, the AIJ version of row 104) was never read, so 184 if it is excluded.
- `screened.md` row 76 states 6 claims where the ledger has 5.
- REVIEW.md prints three phrases as quotations that are not verbatim in their sources: "mere possibility", "examples
  needed to reach a stated loss", and a crosscoder over-generalisation.
- Two notes alter paper wording inside quotation marks.

**L1: met. L2:** REVIEW.md concludes it held. Its strongest cited support is verified ledger rows: the RSP's "< 1 % of
training cost", Davidson's compute-equivalent gain, Mousavi-Hosseini & Erdogdu, Deeb & Roger. Caveat: "a population"
(IRT, a game database) and "a difficulty scale" go beyond L2's wording.

### R17. My scorecard of the pre-registered expectations (my values; phase 2 compares)

**Hit**
- Q1: r8 x0 54 / 51 / 60, inside 45 – 70; r16 x1 61 / 65 / 61, inside 55 – 85; redraw Jaccard 0.68 – 0.78.
- Q3: 0.74 / 0.59 / 0.73 of B certified elicited at K_total; 0 created.
- Q4: 0.06 / 0.00 / 0.13, at most 0.25.
- Q6: 0.41 / 0.29 / 0.37, at least 0.20.
- Q10: s1 r16 0.92 on lem39 and 6 / 6 on holdout250; s0 r16 0; pend 0.
- Q11: A16 0.95 / 0.87 / 0.95; C16 0.
- Q12: medians 4.7 – 15.6×, inside 3 – 30×.
- Q13: guided pend solves 0.50 / 0.55 / 0.60 of B.
- Q15: 0.98 / 0.94 / 0.93, inside 0.3 – 1.0.
- J1 stage-1 bound / p̂: 0.025 – 0.027, inside [0.01, 0.5].
- Replay failures < 1 %.
- J2 A′ at most 20 %.
- J2 B: at least 50 % of zeros stay 0.
- Doubled-cap re-reads: at most 1 success.
- J3: guided ≥ plain.
- J4 A0 at most 0.1.
- J5: r16 redraw Jaccard 0.68 – 0.78; cap-6 r16 ≥ r8.
- J6 (i): drops 0.06 – 0.10.
- J6 (iv) and J6b: "teachable" (within 0.2) on 3 / 3.
- J7 (iii): fewer solves than r8 on 3 / 3.
- J9: 7 / 9 stay at 0, against at least 6.
- Q8b: θ_r8 above every pretraining checkpoint's θ.
- Q8c: at least 3 of 6 in the top decile.
- Q14: mean pairwise Jaccard 0.29 / 0.34, at most 0.4.

**Miss**
- Q2: 0.47 / 0.37 against 60 – 95 %. Only s2 (0.62) hits.
- Q5: 0.33 – 0.45 nats, below 1. The executor predicted this miss before stage 2.
- Q7: 82 – 88 % of B pairs below a 2 % share, against at least 95 %.
- Q8a: Spearman 0.56 – 0.59, below 0.7.
- J10: 64 % of pairs got a base success, against at most 40 %.
- J8: not monotone on any seed. p1600 ≤ 25 % on 2 / 3 seeds (s1 0.33). pend ≥ 50 % holds.

**Partial**
- Q9: rel / eqk 1.31 / 1.22 / **1.00**; s2 misses 1.2 – 2.5.
- J4: A16's holdout250 solved@64 within ±3 % of A0 on 1 / 3 seeds (+5.9 / +7.2 / +2.4 %).
- J6 (ii): the knockout solves 0 / 40 on s1 only. s0 and s2 solve 1 / 40, the intuitionistic `la_transfer_882`;
  0 / 39 on all.
- J6 (iii): ratio 0.88 / 0.80 / 0.85, inside 0.85 – 0.97 on 2 / 3.
- J7 (i): θ gain ≥ 0.5 on 2 / 3 (+0.51 / +0.62 / +0.48).
- J7 (ii): 0.35 / 0.35 / 0.27, inside 30 – 70 % on 2 / 3.
- Q16 as pre-registered: BB within ±25 % for both EI models but −0.28 / −0.29 for both base models. ZIBB is not
  uniformly at least as good: same median on both bases, worse on EI s0 (−0.11 vs +0.06), better on EI s1 (−0.08 vs
  +0.10). Replicate by replicate, its |error| ≤ BB's in 38 / 12 / 44 / 68 %.
- Q14's second clause, "the least-agreeing pair includes the K_total bracket", is moot: that bracket is not among the
  final definitions.
- Not recounted in phase 1: L3 (critics break ≥ 1/3 of the cards), because the cards are write-ups. I check it in
  phase 2.

## §Compare (phase 2: the executor's write-ups against my recount)

**What I read.**
- `run_capability_defs.md`, `numbers.md` § capability-defs and the capability-defs part of `log.md`.
- `capability_defs/REPORT.md`, every card's §9, and the parts of cards that numbers point to.
- `capability_defs/analysis/out/{part3,bracket_all}.txt`, `INDEPENDENT_CHECK.md`, `STATUS.md` and `QUESTIONS.md`.

I read them on the run branch at 645aa4f0. That equals `origin/dan_capability-defs`, which is what the main checkout
`~/nd-takehome` sees for this run.

Verdicts used below:
- **R** reproduces;
- **D** differs, with by how much;
- **W** the number reproduces but the wording or label is wrong;
- **ND** not derivable from the files.

### C1. Headline claims (plain answer, run summary, `numbers.md`)

| # | claim (where) | my value | verdict |
|---|---|---|---|
| 1 | Equal-k "creates" 51–60 per seed (54 / 51 / 60); 14–22 survive K_eval-set (22 / 21 / 14); 8–20 net of the replay-only control; 4–5 out of every seed's base (REPORT §1, §3.2; run summary) | 54 / 51 / 60 → 22 / 21 / 14 → net 20 / 14 / 8 → no seed's base 4 / 5 / 5 (R14) | R |
| 2 | J9 certified 7 of 9; 4 (three distinct theorems) also survive every RL-free control | 7 / 9: 2060, 205, 1077 (s0); 1648, 2060 (s1); 1833, 2060 (s2). Survivors 205 (s0), 2060 (s1, s2), 1833 (s2) (R13) | R |
| 3 | RL r8 solves 12–21 more of 322 than the base reaches at K_eval-set (r16 14–32); replay-only 239 / 244 / 249; J7 220 / 215 / 219 | 286 − 265, 286 − 270, 293 − 281 = +21 / +16 / +12; r16 +24 / +32 / +14; controls identical | R |
| 4 | K_eval-set 19,281 / 21,107 / 23,310 (r8); K_per 777 / 731 / 954; K_total 3.29–4.29 M | Identical with the executor's 3.6 ms. With the measured 470 s / 131,072 = 3.586 ms: 19,357 / 21,190 / 23,402 | R. The ladder ran on RTX A6000 and the 3.6 ms per attempt is A40, so the budget mixes GPU classes; not stated |
| 5 | The known-proof sum recovers a median 0.98 / 0.94 / 0.93 of the measured p (calibration, T 0.8) | 0.982 / 0.940 / 0.925; IQR 0.90–1.02 / 0.85–1.00 / 0.85–0.95 | R |
| 6 | Random weights need e^290 to e^3,200 attempts | known-proof sum under init on the hard theorems: −289 to −3,228 nats at T 0.8 (medians −823 / −834 / −905) | R |
| 7 | "No RL excess at matched ability (IRT)" | My own 2PL, calibrated through p5000 (`rv_irt_matched.py`). Created items: EI r2 49 / 43 / 49 at Δθ 2.30 / 2.03 / 2.66; replay-only 50 / 49 / 55 at Δθ 2.09 / 2.07 / 2.12. EI's rate is below replay's on 3 / 3 (0.88 / 0.75 / 0.63 vs 1.04 / 0.80 / 0.74). Through pend: r8 26 / 26 / 30 at Δθ ≈ 2.0 vs replay-only 4 / 7 / 7 at ≈ 0.6 | R. The matching is approximate: s2's EI r2 is 0.5 θ above its placebo |
| 8 | Excluded middle "acquired by one seed's RL" is taught by 16 demonstrations even to a knockout pretrained without DN | knockout + A16: 35 / 37 / 37 of 39. J6b gain difference: +0.051 / −0.013 / −0.013 | R, but **W** on "one seed": s2's r16 also solves 13 / 39 lem instances (0.13 pass@1) and 1 / 6 holdout250 members (family share 0.26). Acquisition is full on s1 and partial on s2 |
| 9 | Run summary: "Expectations: most hit; misses: Q2, Q5, Q7, Q8a, J8 monotone, J10" | Also partly missed: Q9 (s2), J4 ±3 % (2 / 3), J6 (ii) (2 / 3), J6 (iii) (1 / 3), J7 (i) (s2), J7 (ii) (s2), J8 p1600 ≤ 25 % (2 / 3), Q14 second clause, and Q16 (ZIBB misses everywhere; BB misses s1 of the J2 adaptation and both base models of the pre-registered data). REPORT §3.9 lists most of these correctly | **W**: the summary's miss list is incomplete |

### C2. REPORT §3 claims

| # | claim (section) | my value | verdict |
|---|---|---|---|
| 10 | Bracket verdicts at K_eval-set, r8-solved hard theorems 55 / 45 / 52 (§3.1) | Elicited by sampling 17 / 17 / 21, by known-proof estimate 5 / 1 / 3. Found, not certifiable: 12 / 9 / 18. Not reached: 21 / 18 / 10. Undetermined: 0. Certified created: 3 / 2 / 2 | R (exact) |
| 11 | Median k-to-solve 10^4.6 / 10^5.3 / 10^4.5, range 10^2.3–10^16.8. "Found one to seven times" | 4.6 / 5.3 / 4.5; 2.3–16.8; found counts 1–7 | R |
| 12 | Measured theorems 59–71 per seed, 10th–90th percentile 0.16–1.34; above UB95 on 3 / 2 / 1 | 64 / 60 / 72 theorems (J9's two late successes add one each), percentiles 0.28 / 0.33 / 0.16 – 1.34 / 1.15 / 1.28 | R |
| 13 | "One proof carries a median 50–62 % of the sum" (§3.1) | 0.62 / 0.50 / 0.51 on the **calibration** theorems. On the hard theorems, where the creation question lives, 0.86 / 0.79 / 0.73 | **W**: name the population. The point is stronger on H |
| 14 | Created-set table: all 15 rows × r8 / net / r16 / redraw / seed (§3.2, `numbers.md`) | Every cell reproduces. Exception: IRT DIF+ at r16, where my fit gives 33 / 37 / 35 against their 33 / 35 / 37 (different IRT fits, ±2) | R |
| 15 | "Redraw floors are high (0.80–1.00 budgeted)" | Budgeted definitions: 0.67 (cm_recipe s2), 0.78 (cm0 s2) to 1.00 | W (0.67–1.00) |
| 16 | "Seed floors are low (0.06–0.39); exceptions rule-set novelty (0.55–0.62) and 'no seed's base' (0.38–0.50)" | The executor's own table and mine give "no seed's base" 0.29 / 0.29 / 0.43. IRT is 0.37–0.44 | **D**: the 0.38–0.50 is stale. "No seed's base" is not an exception |
| 17 | "`la_transfer_2060` is in all three seeds' strictest sets, `la_transfer_1077` and `la_transfer_1648` in two" (§3.2) | With the final data, the strictest set (`cm_recipe`) is s0 {205, 2060, 2110, `textbook_48e30…`}, s1 {1802, 2060, 2110, `textbook_03549…`, `textbook_f918…`}, s2 {1802, 1833, 2060, `textbook_48e30…`, `textbook_f918…`}. 2060 is in all three. **1077 and 1648 are in none** (other seeds' bases solved them). The ones in two seeds are 2110, 1802, `textbook_48e30…` and `textbook_f918…` | **D** (stale: it describes the J9 candidate lists, not the final sets) |
| 18 | Long pool: equal-k 13 / 15 / 16; the base finds 29 of "these 45" (64 %) | 29 / 45 of J10's selection: 13 / 16 / 16, one s1 theorem being r16-only | R |
| 19 | Mean off-diagonal Jaccard 0.31 (r8) / 0.36 (r16); `numbers.md` 0.305 / 0.355; least-agreeing pairs involve `npnt` | The executor's own final `out/part3.txt` and my recount give **0.291 / 0.342**. The least-agreeing pairs involve **`schema`** (rel–schema, irt–schema, schema–npnt all 0.00 at r8) | **D** (stale). Q14 ≤ 0.4 still holds |
| 20 | Two clusters: compute-matched, bracket, best known proof, guided-too and chain "agree at 0.6–0.9" | Chain–tfmax / brk_ne 0.47; the rest 0.61–0.90 | W (minor) |
| 21 | Guided-too rescues 3 / 4 / 1 of the compute-matched 22 / 21 / 14 | 22 − 19, 21 − 17, 14 − 13 | R |
| 22 | Examples 1–4: `textbook_245a…` pend 0 / 768, r8 733 / 768, J2 10 / 16,384, e^−6.9, replay 78 / 512, s2 pend 505 / 768. `la_transfer_629` pend 545 / 768. `la_transfer_1453` 0 / 66,560, e^−32.4, r16 435 / 512. `la_transfer_2060` 0 / 66,304, e^−18.2, 1,803 known proofs, r8 734 / 768, J7 7 / 512 | all identical; s1 + A4 solves 1453 117 / 256 | R |
| 23 | "RL's own proof is often the base's proof plus a vacuous detour (35 of 120 cases)" (§2; `tf-proof-prob` §9) | Of the 120 pairs (r8 x0 solves, log π_pend(eventual) < −ln K_total) I reproduce 120, 31 that pend solves at 256, and 63 with the reference ≥ 1 / K_total. **26** contain a self-built Or-detour, and the executor's own `detour()` in `cd_part3.py` also gives **26**. Looser rules give 53 – 55; no rule I tried gives 35 | **D**: 26 of 120. The point stands |
| 24 | Threshold-sensitivity table (§3.4) | identical, every cell | R |
| 25 | "512 or ≥ 768 base attempts instead of 256 remove 7–17 equal-k theorems" | 512: −4 / −9 / −11. All reads: −7 / −11 / −17 | W ("4–17") |
| 26 | Plain vs guided table (18 rows); +18 – 22 for pend, −1 to +4 for RL; gap 44 / 31 / 37 → 21 / 14 / 19; Q13 50 / 55 / 60 %, cap 6 40 / 38 / 44 % | identical | R |
| 27 | "Every proof-state model is read both ways" (§3.5) | Only pend / r8 / r16 (J3) were read guided. J4 / J6 / J6b fine-tunes and the J7 continuation were read plain only | **W**. AGENT_POLICY's guided default is not met for those models, and this is not stated |
| 28 | Families table (§3.6): round-1 and r16 training shares; held-out at budget | Training shares reproduce exactly on the key-step members (39 / 15 / 20 / 20 / 40 / 13 of 40). Excluded middle held-out 0 / 6, 6 / 6, 1 / 6 for r16; base 0 | R. "Share of the 40 trained-on members" should say key-step members |
| 29 | J4 / J6 / J6b table and "four demonstrations install the schema in every seed's base" | identical (36 / 33 / 36 with A4) | R |
| 30 | IRT matched-placebo table (§3.7) | My fit: Δθ within 0.03, counts within ±2, same ordering (C1 #7) | R |
| 31 | Update size: RL r8 0.28, replay-only 0.30, late PT 0.81, seed gap 1.43, cosine 0.45 | 0.282 / 0.297 / 0.809 / 1.426, cosine 0.452 (`rv_update.py`, CPU torch) | R |
| 32 | J7: 220 / 215 / 219; solves of B 19 / 18 / 16; of cm 4 / 4 / 0; θ +0.51 / +0.58 / +0.58 | Counts identical. θ gains over pend in my fit: +0.51 / +0.62 / +0.48 | R |
| 33 | J7 "used 60,863 of the ladders' 73,838 A40-seconds (82 %)" | The ladders' 73,838 s were on RTX A6000 (`trajectory` `compute.json`). J7's training logs: 18,308 / 20,494 / 21,824 s = 82 / 84 / 81 % | **W**: not A40-seconds; the match is across GPU classes |
| 34 | "pend had already seen each K12 proof ≈ 20 times" (§3.7; `compute-equivalent` card: 24,077 steps × 1,024 pairs / 1.24 M) | trajectory's Stage-1 logs: **3.69 / 3.72 / 3.72 epochs of pairs**. The best recipe batches by token budget, ≈ 190 pairs per step, not 1,024 | **D** (≈ 5× too high). The J7 result itself stands; the stated mechanism ("compute without new data buys little after 20 passes") needs rewording |
| 35 | J8 table (§3.7): new solves, elicited share at K_total, replay-only %, net | identical (e.g. s0 21 / 29 / 41 / 32 %, replay-only 83 / 63 / 66 / 53 %) | R |
| 36 | J9 table (§3.8): attempts, UB95, other seeds' bases, controls; "the estimate ranked them correctly"; the 1648 success is r8's shortest proof | identical. 1077 (s1) and 1648 (s2) had their seeds' highest estimates. The s2 proof is one of r8's 10-line proofs | R |
| 37 | The four survivors' estimates put k-to-solve at 10^10 to 10^13. They are held-out members of distribution, De Morgan with a double negation and Peirce | 10^10.2 – 10^13.2; schema labels `dist_and_over_or`, `demorgan_and_to_nor`, `peirce` | R |
| 38 | Compute table and spend (§3.10): 77.0 A40-hours, $37.84, 77.21 pod-hours | identical (registry rows, `~/podhours.log`) | R |
| 39 | "Composition: every rule RL uses occurs in ≥ 4 % of pretraining proofs"; "DN applied to a NEGI line: 16,703 records" | All 13 rules occur in ≥ 8.0 % of K12 records. 16,703 | R |
| 40 | Q16 / §4: "a beta-binomial … predicted how many J2 theorems the base solves in 16,384 attempts to within −7 to +13 %" | Those errors include the 30 calibration theorems per seed in both counts (sampled at 4,096, and certain because the small sample already had ≥ 3 successes). On the J2 theorems alone: **−1 / +31 / −13 %**; on the zero-small-sample subset −1 / +35 / −15 %. ZIBB: −68 / −55 / −61 % | **D**: within ±25 % on 2 / 3 seeds, not "−7 to +13 %" |
| 41 | `numbers.md` J2 line: "stage A 16,384 on the J2 theorems (87 / 89 / 85) with ≥ 1 success on 57 / 52 / 64" | J2 theorems are 57 / 59 / 55 at 16,384. The 87 / 89 / 85 include the 30 calibration theorems per seed, read at **4,096**. Stage A: 27 / 22 / 34 of 57 / 59 / 55 | **W** (the label is wrong; the hard-only numbers given beside it, 24 / 54, 20 / 57, 28 / 49, are on a third, unlabelled subset: the J2 theorems with 0 in all 768 earlier attempts) |
| 42 | J2 truncation (§3.9; log 12:11): `textbook_6997…` 2 / 16,384 at doubled caps, "0 at standard caps" (log: "0 in ≥ 65,536 at standard caps, so the read caps decide this theorem's verdict") | s2 stage B chunk `s2_b02` (standard caps 512 / 96, 49,152 attempts, seed 7302): **3 successes, 2 distinct proofs** | **D**: the base solves it at standard caps; the caps do not decide its verdict. The expectation (≤ 1) still holds |
| 43 | Cut-off reporting | REPORT and `numbers.md` give no per-stratum cut-off fraction. Only the log does, for J2 s0. My values (R4, R13, `rv_trunc.log`) exceed the policy's 0.1 % in several strata: J2 calibration 1.86 % (s0), J5 cap-6 r16 2.1 % (s0), J6b up to 2.5 %, J7 up to 1.1 %, J9 `la_transfer_1833` (s2) 0.49 % | **W** (policy gap). Cut-offs can only hide base successes, i.e. bias toward "not reached". The doubled-cap check covered only the stage-A zeros |
| 44 | Cards cite `support-curves` / `support-state` results ("survivor count fell 37 → 29", "flips 28 of 29") | Those are 3.2 M `lean_seq` / SN-state models, not best-cap12; Lean alone (support-curves pre-registration) | **W**: inherited numbers without the model label |

### C3. Pre-registered expectations: the executor's §3.9 against my recount

| item | executor's verdict | mine | agree? |
|---|---|---|---|
| L1, L2, L3 | hit, hit, hit (20 / 20) | L1 hit (sub-audit). L2 supported. L3: all 20 cards record a critic argument "accepted" (19 plainly, 1 "in substance") | yes |
| Q1, Q4, Q5, Q6, Q7, Q10, Q11, Q12, Q13, Q15 | as listed | same values (Q12: 6.1 / 4.7 / 7.0× set level; 7.2 / 5.3 / 15.6× per theorem, both inside 3–30×) | yes |
| Q2 | 1 / 3 | 1 / 3 (0.47 / 0.37 / 0.62) | yes |
| Q3 | hit, 76 / 71 / 85 % | hit, but on B as pre-registered: 0.74 / 0.59 / 0.73 (0.80 / 0.71 / 0.88 of the J1-scored). The executor's denominator is the 55 / 45 / 52 r8-solved hard theorems, not B | yes (denominator changed, not stated) |
| Q8 | a miss; b, c hit | a 0.571 / 0.592 / 0.561 (miss); b yes 3 / 3; c 3 – 5 of 6 depending on the residual | yes |
| Q9 | 2 / 3 | 2 / 3 (1.31 / 1.22 / 1.00) | yes |
| Q14 | first hit (0.31 / 0.36); second miss | first hit (**0.29 / 0.34**). Second: the K_total bracket is not among the final definitions; its set is empty | yes on verdicts, **values stale** (C2 #19) |
| Q16 | adapted; "BB hit (2 / 3 on the zero subset)"; ZIBB miss | Pre-registered data (feasible, R11): BB within ±25 % on both EI models, **misses both base models (−0.29 / −0.28)**; ZIBB not at least as good. Adapted: BB 2 / 3 (−1 / +31 / −13 %); ZIBB miss | **no**: the BB "hit" is not supported by either version. The stated reason for the swap ("support-curves data lack per-attempt sequences") does not hold for this test: counts suffice for exchangeable attempts |
| J1 stage 1 (median LB₁ / p̂ in [0.01, 0.5]) | not scored | 0.027 / 0.027 / 0.025: hit | omitted |
| J3 (guided ≥ plain at every checkpoint) | not scored separately | 18 / 18: hit | omitted |
| J2 A′, J2 B, J2 truncation (≤ 1), J4, J5, J6, J6b, J7, J9, J10 | as listed | same (J2 truncation wording, C2 #42) | yes |
| J8 | monotone miss; pend hit; p1600 1 / 3 | same. **Erratum to my §Recount R17:** I wrote "p1600 ≤ 25 % on 2 / 3". s2's share is 42 / 167 = 25.15 %, so it is 1 / 3, as the executor says | yes |

**Gate 0.** Every expectation was committed before its job (R0 table). The misses are reported as misses in REPORT §3.9.

### C4. Model labels and policy

- **Model labels.** REPORT and `numbers.md` open with a full model label: best-cap12 9.56 M `ALiBiGPT`, `lean_staten`,
  from scratch on K12, checkpoints named. Cap 6, the replay-only control and J7 are labelled. Exceptions:
  - the inherited `support-curves` / `support-state` numbers in cards (C2 #44);
  - the guided-tts cost ratio (1.8× tokens, 2.2× GPU), quoted without the model it was measured on (best-cap12 /
    cap-6 r8).
- **Checker.** Lean alone throughout. No comparison with a pre-2026-09-27 number in the report. `nd_verify` is
  unused (R0).
- **Compute.** Every family has registry rows and a per-family table. J7 is matched to 82 % of the ladder's GPU-seconds
  (within 1.25×, reported). Guided vs plain is not compute-matched; the report says so.
- **Seeds and noise floor.** Three training seeds everywhere, with per-seed values and redraw / seed Jaccard floors
  throughout. The pre-registration states no minimum detectable difference (AGENT_POLICY asks for one). The J6b
  decision thresholds (0.2 / 0.3) are the only pre-stated effect sizes. No IQM / bootstrap intervals are given; at
  n = 3 an IQM is the mean, so per-seed values suffice.
- **Split.** The K12 renaming of `textbook_3ed45280…` (R2) predates this run and is not mentioned. It concerns one
  s0 equal-k theorem, not a headline.

## §Verdict

**No hard-constraint violation, so no quarantine.**
- `nd_verify` and `TEST_RUN_DONE` are unchanged, and `nd_verify` judges nothing.
- No evaluation file is read in training.
- Every job's expectations were committed before it ran.
- Lean accepts all 3,710 counted proofs I re-checked, across 15 arms, with working negative controls.
- No training file shares a renaming class with textbook72, holdout250 or the held-out A ∨ ¬A instances. The one
  exception is the pre-existing K12 twin of `textbook_3ed45280…`.

**What stands.** Each item reproduces from the raw files with my own code; model = best-cap12 unless stated.
1. **The run's central measurement.** RL r8's equal-k "creations" (54 / 51 / 60 of 322) shrink:
   - to **22 / 21 / 14** when the base gets RL's GPU time as attempts (K_eval-set ≈ 2 × 10⁴);
   - to 20 / 14 / 8 net of the replay-only control;
   - to **4 / 5 / 5** that no seed's base ever solved.

   At set level, r8 at 256 attempts still solves **+21 / +16 / +12** more than the base reaches at K_eval-set. Neither
   RL-free control (replay-only 239 / 244 / 249, J7 220 / 215 / 219) closes that gap. Every created set, redraw floor,
   seed floor and threshold-sensitivity cell reproduces.
2. **The known-proof estimate is accurate on calibration theorems** (median 0.98 / 0.94 / 0.93 of measured p), but it
   is not a strict bound. It exceeds the sampling UB95 on a few theorems, so the factor-2 margin is justified.
   - J1 is sound: F(t) equals the union of every Lean-accepted read plus the references.
   - Its exact scores reproduce trajectory's to 5 × 10⁻⁵ nats.
   - The one-base bound never exceeds the exact score.
3. **J9 certifies 7 of 9 (theorem, seed) pairs relative to their own seed's base** (0 in 1.25–1.51 M attempts; UB95 below
   0.05 / K_eval-set). Four pairs, three theorems (`la_transfer_205`, `2060`, `1833`), also survive every RL-free control.
   Both J9 base successes are proofs already in F.
4. **Excluded middle is teachable, not latent.**
   - A no-DN knockout learns it from 16 demonstrations (35 / 37 / 37 of 39), as pend does.
   - The J6b gain difference is +0.05 / −0.01 / −0.01.
   - Four demonstrations give pend 33 – 36 of 39.
5. **Guided reading helps the base, not RL**: +18 to +22 holdout250 theorems for pend, −1 to +4 for RL. It rescues only
   3 / 4 / 1 of the compute-matched set.
6. **At matched ability gain, EI creates no more DIF+ items than RL-free training.** My own 2PL fit gives the same Δθ
   and counts to within 0.03 and ±2. The RL update is the size of the replay-only update (0.28 vs 0.30, cosine 0.45).
7. J7 is a lateral move (fewer solves than pend). J8's start dependence (not monotone) and J10 (64 % of long-pool
   pairs reached by the base) reproduce exactly.
8. **The literature deliverable meets L1** (185 new / 57 in depth / 99.75 % of claims verified). Critics landed a
   failure the executor accepted on 20 / 20 cards (L3).

**Must be reworded or corrected.** The numbers on file contradict these; the conclusions mostly survive.
1. **Agreement (REPORT §3.3 and §3.9 Q14, `numbers.md`, STATUS).**
   - Mean off-diagonal Jaccard is **0.29 / 0.34**, not 0.31 / 0.36 (0.305 / 0.355). The executor's own final
     `out/part3.txt` says 0.291 / 0.342.
   - The least-agreeing pairs involve `schema`, not `npnt`.
   - The "no seed's base" seed floor is 0.29 / 0.29 / 0.43, not "0.38–0.50", so it is not an exception.
2. **"`la_transfer_1077` and `la_transfer_1648` [are] in two seeds' strictest sets"** describes the J9 candidate lists.
   - With the final data both are in **none**: other seeds' bases solved them.
   - The theorems in two seeds' strictest sets are 2110, 1802, `textbook_48e30…` and `textbook_f918…`.
3. **"35 of 120" padded RL proofs → 26 of 120.** The executor's own `detour()` also gives 26.
4. **"pend had already seen each K12 proof ≈ 20 times" → ≈ 3.7 epochs of pairs** (trajectory's Stage-1 logs). The
   stated mechanism for J7's lateral move needs rewording.
5. **Q16 and §4's "a beta-binomial predicted … to within −7 to +13 %".**
   - Those errors include 30 calibration theorems per seed that were certain to be solved. On the J2 theorems it is
     **−1 / +31 / −13 % (2 / 3)**.
   - The pre-registered support-curves test was feasible from counts. On it, BB misses both base models (−0.29 / −0.28),
     and ZIBB is never uniformly at least as good.
   - Score Q16 as a miss, or 2 / 3 for the adapted BB. Drop the "lack per-attempt sequences" justification.
6. **`numbers.md` J2 line.** "Stage A 16,384 on the J2 theorems (87 / 89 / 85)" counts 30 calibration theorems per seed
   that got 4,096. The stage-A rate on the J2 theorems is 27 / 57, 22 / 59, 34 / 55.
7. **J2 truncation (§3.9, log 12:11).** `textbook_6997…` (s2) is **3 / 49,152 at standard caps** in stage B. It is not
   "0 at standard caps", and the read caps do not decide its verdict.
8. **GPU classes.** The r8 ladders ran on RTX A6000, not A40.
   - K_eval-set and J7's "82 % of the ladders' A40-seconds" divide or compare A6000 seconds with A40 costs.
   - Say so. Better: also give K_eval-set from attempts or with a same-class per-attempt cost.
9. **"Every proof-state model is read both ways" (§3.5).** Only pend / r8 / r16 were read guided. The J4 / J6 / J6b
   fine-tunes and the J7 continuation are plain-only. That departs from the guided-by-default policy and should be
   stated.
10. **Cut-off fractions per stratum are missing from REPORT and `numbers.md`.** Several strata exceed the policy's 0.1 %:
    J2 calibration 1.9 %, J5 cap-6 r16 2.1 %, J6b up to 2.5 %, J7 up to 1.1 %, and `la_transfer_1833`'s J9 attempts
    0.49 %. Every cut-off can only hide a base success, so it biases toward "not reached / created". Report them.
11. **Smaller wording fixes.**
    - Run summary: its list of misses omits the partial misses (Q9, J4, J6 ii / iii, J7 i / ii, J8 p1600, Q14 second
      clause, Q16).
    - "acquired by one seed's RL": s2's r16 also reaches 13 / 39.
    - "one proof carries 50–62 %" is on the calibration theorems; it is 73–86 % on the hard ones.
    - "Redraw floors 0.80–1.00": actually 0.67–1.00.
    - "512 or ≥ 768 attempts remove 7–17": actually 4–17.
    - "agree at 0.6–0.9": chain 0.47.
    - Q3's denominator is the 55 / 45 / 52 r8-solved hard theorems, not B. On B: 0.74 / 0.59 / 0.73, still a hit.
    - The families table's training shares are over key-step members, not "the 40 trained-on members".
    - The cards quote `support-curves` / `support-state` numbers without their 3.2 M model labels.
    - The J1 stage-1 and J3 "guided ≥ plain" expectations are not scored. Both hit.

**Not supported as written.**
- Q16 "BB hit".
- "The read caps decide `textbook_6997…`'s verdict".
- 1077 / 1648 in two seeds' strictest sets.
- The "≈ 20 passes over K12" mechanism.
- "35 of 120".

None of these touches the run's central measurement ("What stands", items 1–3) or its recommendation.

**Open: the next measurements that would settle it.**
1. **Truncation on the certified theorems.** Re-read `la_transfer_205` (s0), `2060` (s1, s2) and `1833` (s2) with pend at
   doubled caps (1,024 / 192) for ≥ 2 × 10⁵ attempts each (≈ 1 A40-hour each). That removes the only open caveat on
   the run's four "survives everything" pairs. 1833 has 0.49 % of its standard-cap attempts cut off.
2. **"No seed's base" with equal effort.** Give the other two seeds' pend the same ≈ 1.2 M attempts on the three
   survivors. Today 205 has only 66,560 (s1) and 17,408 (s2) other-seed attempts, and 1833 has 17,408 each.
3. **A same-GPU-class budget.** Measure the per-attempt pend cost on an RTX A6000 (or re-express K_eval-set in ladder
   attempts, ≈ 1.8–2.0 × 10⁶ / 322 ≈ 5.6–6.2 × 10³ per theorem). Restate the compute-matched set under both. The
   sensitivity table already shows it moves from 22 / 21 / 14 to 33 / 28 / 28 at 0.3× K.
4. **Guided reads of the J4 / J6b / J7 models** (policy). Then Q11 and J7 can be stated as best-system numbers too.
