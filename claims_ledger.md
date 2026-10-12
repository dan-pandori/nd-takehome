# Claims ledger: run `create-or-elicit` (v1, inherited claims)

Written 2026-10-12 by a sub-agent of the `create-or-elicit` executor (pre-registration Phase 0.4). This is the input to the
writing run for "Did RL create it? Budgets, controls and a pretraining knockout in a from-scratch prover with exact
likelihoods". That run may use a number only if a row here traces it to a reviewed source, and it must quote the
corrected value and carry the caveat. **v1 covers inherited claims only.** The executor adds this run's own numbers
later. Phase 0.1 (estimator) and 0.2 (same-class budget) will supersede rows L5–L9 and L15–L16.

**Status legend**
- **reviewed-stands**: an independent reviewer re-derived it from the raw files, and it reproduces with its wording.
- **reviewed-corrected**: a review, or this run's 2026-10-12 re-check, found the number, its label or its wording
  wrong. Use the **bold** value after →, never the original. "(label)" / "(wording)" means the number reproduces but
  must be stated differently.
- **unreviewed**: no independent recount, e.g. this ledger's own computations or an executor-only file. Not for a
  headline until checked.
- **contradicted**: a later file contradicts it. Use it only to report the correction.
- **verified quote (V)** (literature rows only): the lit review's claim ledger found the quote verbatim at the stated
  location. This checks the citation, not the paper's correctness.

**Ledger check** (last part of the status cell):
- `copied`: taken from the reviewed write-up or the review table, not re-derived here.
- `file`: I read the value in the named raw output file.
- `recount`: I recomputed it from the named file (method given).

**Model labels**
- **M12** = best-cap12, the `state_env_october` recipe, `trajectory` seeds s0 / s1 / s2.
  - `best_model.ALiBiGPT` 6 × 384, 9,560,832 params. Interface `lean_staten`: proof-state environment that assigns names.
  - From scratch on K12 (`train_k12.jsonl`, 155,000 synthetic ND proofs, 2–12 lines).
  - Stage 1: 1,200 s on one A40, 24,077 / 24,345 / 24,328 steps ≈ 3.7 epochs of pairs.
  - **pend** = end of pretraining.
  - **r8** = 8 T1 expert-iteration rounds (k 32, T 0.8, 4,495 `rl_targets`, 600 fine-tune steps per round, K12
    replay) on **RTX A6000**. s2 resumed at r2 with batch 1,024 after an OOM.
  - **r16** = rounds 9–16 on **A40** (`rl-continue`; card `state_env_october_r16`).
- **M12-bs** = `best-state`'s three original best-cap12 seeds (same recipe, different seeds).
- **M6** = best-cap6: the same recipe on the cap-6 set (`trajectory-cap6`, `rl-continue-cap6`).
- **KO-DN** = `capability-defs` J6's no-DN knockout: the same recipe on K12 minus every record with a DN step.
  - 3 seeds; 24,227–24,495 steps in 1,201 s on an A40.
  - **Not this run's K12⁻.** K12⁻ removes σ⁺, is refilled, and keeps DN on premises and hypotheses.
- **RO** = the replay-only control (`rl-from-ckpt` c⟨s⟩_pend_r8): pend plus the ladder's 8 fine-tune rounds on K12
  replay, no RL proofs, mostly on RTX A6000.
- **J7** = a compute-matched continuation: pend trained further on K12 for 28,054 / 31,462 / 33,535 steps on an A40.
- **M3.2-WP / M3.2-SN** = the older 3.2 M organism, trained from scratch on `train_depth3_f0_a1` (cap 6).
  - **WP** (`support-curves`): whole-proof `lean_seq`, 3,214,336 params. Base `stage1_a1_seq_s0`; EI `la_T1_sc_s0_r8`
    (8 × k 32).
  - **SN** (`support-state` / `state-env`): 4 layers × 256, 3,216,384 params, `lean_staten`, `Env(canon, assign)`.
    Bases `stage1_SN_s{0,1}`; no RL.

**Reads and checker**
- **Reads.** *Plain* = `state_eval.py` with k 256, T 0.8, `max_steps` 96, `max_action` 512, sample seed x0 or x1.
  *Guided* = `--arm logical`, at most 10 redraws per attempt.
- **"The 322"** = textbook72 (scoring only) + holdout250, never trained on.
- **Checker.** Every proof count is Lean 4 core alone (`lean_judge` / state-env gate, the project's judge since
  2026-09-27). **No row uses `nd_verify`.** The suffix names the review's Lean re-check:

| suffix | run | proofs re-checked by the review | date |
|---|---|---|---|
| ·cd | capability-defs | 3,710 counted proofs across 15 arms, 0 rejected, negative controls working | 2026-10-05 |
| ·tj | trajectory | 1,350 / 1,350 sampled, plus 896 / 896 targets | 2026-10-01 |
| ·rc | rl-continue | 1,669, 0 rejected | 2026-10-04 |
| ·rc6 | rl-continue-cap6 | 1,864 / 1,864 | 2026-10-04 |
| ·bs | best-state | 1,200 / 1,200 | 2026-10-01 |
| ·gt | guided-tts | 5,211 texts | 2026-10-03 |
| ·rfc | rl-from-ckpt | 1,950 / 1,950 | 2026-10-02 |
| ·ss | support-state | in-loop Lean 4.34.0, re-check 4.34.1 | 2026-09-29 |
| ·sc | support-curves | WP side judged by Lean alone from 2026-09-27 | 2026-09-28 |

  "—" means the row is not a proof count (compute, scores, data). G4ip = `intuit.py` (the capability-defs reviewer's
  own G4ip agrees on 2,647 prompts).

**Source keys.** Every source is in git on the fork's `origin/dan_<run>` branch; local worktrees are `~/work/<run>`.

| key | path | ref and notes |
|---|---|---|
| `cd:` | `~/work/capability-defs/capability_defs/` | DONE 645aa4f0 |
| `cdR` | `~/work/capability-defs/review_capability-defs.md` | da11be78, 2026-10-05. C# = §Compare item; R# = §Recount section; V = §Verdict |
| `cdRC` | nd-rl `docs/project_strategy/capabilities/REPORT.md` | Reading copy (librarian, 2026-10-05). Carries every cdR correction, marked *[review]*. **Does not** carry corrections (a)–(c) of 2026-10-12 (rows L6, L7, L33) |
| `tj:` | `~/work/trajectory/` | `numbers.md` § trajectory l.1705+; `review_trajectory.md` 958f1842; `artifacts/tj/compute.json` |
| `rc:` | `~/work/rl-continue/` | |
| `rc6:` | `~/work/rl-continue-cap6/` | |
| `bs:` | `~/work/best-state/` | |
| `gt:` | `~/work/guided-tts/` | |
| `rfc:` | `~/work/rl-from-ckpt/` | |
| `ss:` | `origin/dan_support-state` | 2913f0e4 |
| `sc:` | `origin/dan_support-curves` | 44c4872a |
| `ca:` | `~/work/claim-audit/` | ad9116a5 |
| `coe:` | this worktree | |
| `lit:` | nd-rl `docs/literature/` | |
| cards | nd-rl `docs/models/` | |

## A. Budget and compute-matched sets

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L1 | At equal k (256 base attempts, draw x0) RL r8 "creates" (pend 0 / 256, r8 ≥ 1 / 256) **54 / 51 / 60** of the 322. | M12 pend vs r8 | Lean·cd | cd:REPORT.md §3.2 l.144; cdR R3, C1 #1; = tj group B (numbers.md l.1726) | reviewed-stands · copied | "Created at k" is a fact about n. 512 base attempts remove 4 / 9 / 11, all reads (≥ 768) 7 / 11 / 17 (cdR C2 #25: "4–17", not "7–17"). Redraw x1: 58 / 46 / 54. |
| L2 | At the compute-matched budget K_eval-set, **22 / 21 / 14** stay out of the base's reach at r8 (18 / 17 / 8 with 0 base successes); r16 (x1) 25 / 34 / 17. | M12 | Lean·cd | cd:REPORT.md §3.2 l.145–146, l.168–170; cdR C1 #1, C2 #14 | reviewed-stands · copied | K_eval-set is mislabelled (L5–L7). The set grows as K shrinks (L8). |
| L3 | Net of the replay-only control (theorems RO solves on the same draw removed): **20 / 14 / 8**. | M12 vs RO | Lean·cd | cd:REPORT.md §3.2 l.145; cdR C1 #1 | reviewed-stands · copied | RO is not token-matched: the ladders train on 1.3–1.6× its tokens (rfc review, Next measurement). |
| L4 | **4 / 5 / 5** of the compute-matched theorems were never solved by any seed's base (r16: 6 / 15 / 8). | M12 | Lean·cd | cd:REPORT.md §3.2 l.147, l.170; cdR C1 #1 | reviewed-stands · copied | Effort was unequal across seeds: other seeds' bases had as few as 17,408 attempts on some theorems (cdR V Open 2). |
| L5 | K_eval-set (ladder GPU-seconds ÷ (322 × 3.6 ms)) = **19,281 / 21,107 / 23,310** at r8, ≈ 4.8–5.0 × 10⁴ at r16. | M12 ladder (r1–r8 RTX A6000, r9–r16 A40); cost of pend on A40 | — | cd:REPORT.md §3.0 l.91–96; cdR C1 #4, R5 l.175–182, V reword 8; cdRC l.113–118 | reviewed-corrected (label) → **r1–r8 A6000 seconds are divided by an A40 per-attempt cost (mixed GPU classes)**; r9–r16 are A40. Recount (compute.json, sum of rounds 1–8 = 22,347 / 24,464 / 27,015 s): 19,278 / 21,104 / 23,305; r16 with rc's 33,261 / 32,844 / 31,471 A40-s: 47,971 / 49,437 / 50,454 | The numerator includes the ladder's eval phase (transfer k 32 sampling + greedy), 36 % of ladder attempts, which never feeds training. The reviewer's measured 3.586 ms gives 19,357 / 21,190 / 23,402. |
| L6 | **Correction (b).** 3.6 ms is one J2 chunk (s0_c00: 470 s / 131,072). Registry A40 averages for pend are higher: J2 + J2b **4.28 / 4.40 / 4.55 ms**, J9 **8.31 / 6.93 / 5.11 ms** per attempt. At the J2 + J2b average, K_eval-set = **16.2k / 17.3k / 18.5k** (−16 to −21 %). | M12 pend, A40 | — | cd:analysis/out/compute.txt l.24–29, l.49–51 (registry rows); cdR R5 l.180–181 | unreviewed (this run, 2026-10-12) · recount (gpu_seconds / attempts per job row; K = ladder s ÷ (322 × c)) | Process-level seconds include co-tenancy, batch effects and long chunks. Neither value is an A6000 cost; Phase 0.2 measures both classes. |
| L7 | **New in this ledger.** s2's r8 ladder seconds include the OOM'd first attempt at round 2: r2 logged 441,205 attempts and 4,726 GPU-s; every other round logged 224,245 attempts (s2 r1 2,024 s, r3 3,087 s). | M12 s2 | — | tj:artifacts/tj/compute.json key `T1 ladder\|2\|2`; tj:numbers.md l.1775 ("s2 incl. the OOM'd round") | unreviewed · recount (compute.json per round) | s2's K_eval-set counts one extra sampling phase (≈ 1.6–2.1 × 10³ GPU-s, 6–8 % of s2's K). Its batch-1,024 rounds are also slower. Part of s2's larger K is batch and OOM, not RL work: all seeds made the same 224,245 attempts per round. |
| L8 | Threshold sensitivity. Compute-matched set at K = 0.1 / 0.3 / 1 / 3 × K_eval-set: 38 / 36 / 36 → **33 / 28 / 28** → 22 / 21 / 14 → 21 / 20 / 3 (s2 at 3×: 6 undetermined). 0.3× = K 5,784 / 6,332 / 6,993. | M12 r8 x0 | Lean·cd | cd:REPORT.md §3.4 l.285; cd:analysis/out/part3.txt l.99–122 | reviewed-stands (cdR C2 #24, every cell) · file | "The budget is the dominant free parameter": a tenfold smaller K gives a 1.7–2.6× larger set. |
| L9 | In ladder attempts the r8 budget is 1,793,960 / 1,793,960 / 2,010,920 = **5,571 / 5,571 / 6,245 per theorem** ("≈ 5.6–6.2 × 10³", brief) = 0.29 / 0.26 / 0.27 × K_eval-set. So the compute-matched set at that budget is **≥ 33 / 28 / 28** (sets grow as K shrinks); it was not computed exactly. | M12 r8 ladder | — | cdR R5 l.177–178, V Open 3 l.741–743; tj compute.json | reviewed-stands (attempt counts) · recount (compute.json: 224,245 per round) | These are all ladder attempts: 143,840 training-target attempts per round (4,495 × 32), plus the eval phase (2,285 transfer × 32 + 7,285 greedy), plus s2's repeated r2. Training-target attempts alone are **3,574 per theorem** (this run's K_att(8) = 446.7 × 8). |
| L10 | Set level: r8 at 256 attempts solves 286 / 286 / 293 of the 322; the base reaches 265 / 270 / 281 within K_eval-set. **Δ_cov +21 / +16 / +12** at r8 and +24 / +32 / +14 at r16 (291 / 303 / 295 vs 267 / 271 / 281). | M12 | Lean·cd | cd:REPORT.md §3.2 l.162–166, l.171–173; cdR C1 #3 | reviewed-stands · copied | Base reach mixes sampling (p̂ ≥ 1 / K) with the known-proof estimate (≥ 2 / K). At a smaller corrected K the base reaches fewer theorems and Δ_cov grows. |
| L11 | Bracket verdicts at K_eval-set on the 55 / 45 / 52 r8-solved hard theorems: elicited by sampling 17 / 17 / 21; by the estimate 5 / 1 / 3; found but not certifiable 12 / 9 / 18; not reached (0 in ≥ 65,536) 21 / 18 / 10; certified created 3 / 2 / 2. | M12 pend vs r8 | Lean·cd | cd:REPORT.md §3.1 l.121–134; cdR C2 #10 | reviewed-stands (exact) · copied | "Not reached" is not a certificate; certification needs ≈ 60 K zero-success attempts. Stage B's 66,000 certify only K ≤ 1,100. |
| L12 | The base's median estimated k-to-solve on those theorems is 10^4.6 / 10^5.3 / 10^4.5 (range 10^2.3–10^16.8), right at K_eval-set ≈ 10^4.3. | M12 pend | Lean·cd + scores | cd:REPORT.md §3.1 l.114–115; cdR C2 #11 | reviewed-stands · copied | Rests on the estimator below its calibrated range (L15–L16). |
| L13 | Hard theorems (pend 0 / 512 on x0 + x1): **86 / 77 / 77** of the 322. | M12 pend | Lean·cd | cd:REPORT.md §3.0 l.99; cdR R3 l.134 | reviewed-stands · copied | |
| L14 | K_per = 777 / 731 / 954 per training target; K_total = 3.49 / 3.29 / 4.29 × 10⁶, i.e. ladder s ÷ the ladder's own read cost (6.40 / 7.45 / 6.30 ms). | M12 | — | cd:REPORT.md §3.0 l.95–96; cdR R5 l.177–178, C1 #4 | reviewed-stands · copied | Read costs come from reads on a mix of A6000 and A40. The K_total bracket was dropped as a creation budget (cdR C3 Q14). |

## B. Estimator (known-proof sum)

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L15 | The known-proof estimate (pend's teacher-forced probability at T 0.8, summed over every accepted proof any model found) recovers a median **0.98 / 0.94 / 0.93** of the measured p on 30 calibration theorems per seed (IQR 0.90–1.02 / 0.85–1.00 / 0.85–0.95). | M12 pend | Lean·cd (proof set) | cd:REPORT.md §3.1 l.107–108; cd:cards/_FRAME.md l.63–65; cdR C1 #5 (0.982 / 0.940 / 0.925) | reviewed-stands · copied | **Validated only on calibration theorems with 3–100 of 512 pend successes** (p ≈ 6 × 10⁻³–0.2; capability-defs prereg l.75–76), p from 4,864 attempts each (review_cd/rv_bracket.log). Brief ✓. |
| L16 | Over all theorems where pend's p is measured, the 10th–90th percentiles of estimate / p̂ are 0.28–1.34, 0.33–1.15 and 0.16–1.28 on 64 / 60 / 72 theorems (REPORT: "59–71 theorems, 0.16–1.34"). The estimate exceeds the sampling UB95 on 3 / 2 / 1. | M12 pend | Lean·cd | cd:REPORT.md §3.1 l.108; cdR C2 #12 | reviewed-stands · copied | Not a strict lower bound: the scorer conditions on canonical names, and the env renames ≈ 14 %. Hence the factor-2 margin. Accuracy per p̂ bin below 10⁻³ is not established; Phase 0.1 measures it. |
| L17 | One proof carries a median 50–62 % of the sum. | M12 pend | — | cd:REPORT.md §3.1 l.110–111; cdR C2 #13 | reviewed-corrected (wording) → **0.62 / 0.50 / 0.51 on calibration theorems; 0.86 / 0.79 / 0.73 on the hard theorems** · copied | Name the population. |
| L18 | Random weights need e^290 to e^3,200 attempts per proof (known-proof sum under init on the hard theorems: −289 to −3,228 nats; medians −823 / −834 / −905). | M12 init | — | cd:REPORT.md §1 l.17; cdR C1 #6 | reviewed-stands · copied | The sum is over the known proof set, at T 0.8. |
| L19 | J1 is sound: F(t) is the union of every Lean-accepted read plus the references. Its exact scores reproduce trajectory's to 5 × 10⁻⁵ nats, and the one-base bound never exceeds the exact score. | M12 | Lean·cd | cdR V stands 2 (l.661–665) | reviewed-stands · copied | |

## C. Certification (J9)

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L20 | J9 certifies **7 of 9** (theorem, seed) pairs as created relative to their own seed's base at K_eval-set: 0 successes in 1,245,952 / 1,377,024 / 1,508,096 pend attempts, UB95 2.4 / 2.2 / 2.0 × 10⁻⁶ < 0.05 / K = 2.6 / 2.4 / 2.1 × 10⁻⁶ (2060, 205, 1077 on s0; 1648, 2060 on s1; 1833, 2060 on s2). Pre-registered ≥ 6 / 9: hit. | M12 pend (A40) vs r8 | Lean·cd | cd:REPORT.md §3.8 l.447–462; cdR C1 #2, R13, V stands 3 | reviewed-stands · copied | **New in this ledger** (recount, UB95 = 1 − 0.05^(1/n)): the certificates have only **≈ 8–9 % margin in K**. They fail at these attempt counts if the same-class K_eval-set exceeds 20.8k / 23.0k / 25.1k, i.e. if the per-attempt cost is below ≈ 3.31–3.34 ms. They hold easily at the registry-average K (L6). Truncation: 0.49 % of 1833's attempts (cdR C2 #43). |
| L21 | Not certified: the base found 1077 (s1) and 1648 (s2) once each in ≈ 10⁶ attempts. These two had their seeds' highest known-proof estimates. | M12 pend | Lean·cd | cd:REPORT.md §3.8 l.463–469; cdR C2 #36 | reviewed-stands · copied | |
| L22 | Survives every RL-free control: **4 pairs on 3 theorems**. `la_transfer_205` (s0), `2060` (s1, s2), `1833` (s2). Estimates put their k-to-solve at 10^10.2–10^13.2. | M12 vs RO, J7, other seeds' pend | Lean·cd | cd:REPORT.md §3.8 l.470–473; cdR C1 #2, C2 #37 | reviewed-stands · copied | Other seeds' bases tried 205 only 66,560 (s1) / 17,408 (s2) times and 1833 17,408 each (cdR V Open 2); RO and J7 got 512 attempts. **New (recount, coe:data/coe/families.json):** only 1833 (Peirce) is classical-only. 205 (`dist_and_over_or`) and 2060 (`demorgan_and_to_nor`) are G4ip-provable, so the certified creations are mostly not about the classical step. |

## D. Do the definitions agree?

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L23 | Across 12 definitions of "created" (66 pairs), the mean off-diagonal Jaccard of their sets is **0.291 (r8, x0) and 0.342 (r16, x1)**. Pre-registered Q14 ≤ 0.4: hit. | M12 | Lean·cd | cd:analysis/out/part3.txt l.74, l.90; cdR C2 #19, V reword 1; cdRC l.219 | reviewed-corrected → **0.29 / 0.34**. REPORT §3.3 l.187 and `numbers.md` (0.31 / 0.36) are stale · file | The least-agreeing pairs involve `schema` (rel–schema, irt–schema, schema–npnt all 0.00 at r8), not `npnt`. |
| L24 | Two clusters. "Is the base out of reach?" (compute-matched, bracket, best known proof, guided-too, chain depth) agree at 0.6–0.9. "Did RL's behaviour change?" (equal-k, expansion share, IRT DIF) agree at 0.5–0.8. | M12 | — | cd:REPORT.md §3.3 l.188–193; cdR C2 #20 | reviewed-corrected (wording) → **0.61–0.90, except chain vs best known proof / bracket at 0.47** · copied | |
| L25 | Redraw floors (Jaccard between the two sample draws) and seed floors (Jaccard between seeds). | M12 | — | cd:REPORT.md §3.2 l.142–158, l.174–177; cdR C2 #15–16 | reviewed-corrected → **budgeted redraw 0.67–1.00 (not 0.80–1.00); equal-k redraw 0.68–0.78; seed floors 0.06–0.39, except rule-set novelty 0.55–0.62 and IRT 0.37–0.44; the "no seed's base" seed floor is 0.29 / 0.29 / 0.43 (not 0.38–0.50), so it is not an exception** · copied | Each seed's RL "creates" different theorems. |
| L26 | Strictest set (`cm_recipe`): `la_transfer_2060` is in all three seeds'; 2110, 1802, `textbook_48e30…` and `textbook_f918…` are in two. | M12 | Lean·cd | cdR C2 #17, V reword 2; cdRC l.206–209 | reviewed-corrected → **1077 and 1648 are in no seed's final strictest set**. REPORT §3.2 l.176–177's "in two" described the J9 candidate lists · copied | |
| L27 | Long pool (`transfer_long2`, 21 theorems): equal-k creates 13 / 15 / 16 at r8. Given 16,384 more pend attempts (J10), the base finds 29 of these 45 (64 %). | M12 | Lean·cd | cd:REPORT.md §3.2 l.178–179; cdR C2 #18 | reviewed-stands · copied | Equal-k only. J10's selection is 13 / 16 / 16 (one s1 theorem is r16-only). |

## E. Guided vs plain

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L28 | Guided reading at k 256 helps the base far more than RL: **+18 to +22** holdout250 theorems for pend (196 → 218, 205 → 223, 200 → 222) and **−1 to +4** for r8 / r16. The r8–pend gap shrinks from 44 / 31 / 37 (plain) to 21 / 14 / 19 (guided). Cap 6 pend: +30 / +39 / +47. | M12 pend / r8 / r16; M6 | Lean·cd | cd:REPORT.md §3.5 l.299–333; cdR C2 #26, V stands 5 | reviewed-stands · copied | Not compute-matched (L31). |
| L29 | pend's guided read solves 50 / 55 / 60 % of the equal-k set (Q13; cap 6: 40 / 38 / 44 %). It rescues only **3 / 4 / 1** of the compute-matched 22 / 21 / 14. | M12 pend | Lean·cd | cd:REPORT.md §3.5 l.330–333, §3.3 l.189–191; cdR C2 #21, #26 | reviewed-stands · copied | |
| L30 | "Every proof-state model is read both ways." | M12, KO-DN, J7 | — | cd:REPORT.md §3.5 l.301; cdR C2 #27, V reword 9 | reviewed-corrected (wording) → **only pend / r8 / r16 (J3) were read guided; the J4 / J6 / J6b fine-tunes and J7 are plain-only** · copied | L38–L40 and L45 are plain-only numbers. |
| L31 | A guided-logical attempt costs **1.78× the sampled tokens and 2.18× the sampling GPU-s** of a plain one at cap 12 (cap 6: 2.68× / 2.34×). On long theorems, guided tokens per attempt are 2.0–2.3× plain (cap 12) and 2.8–3.3× (cap 6). | M12 r8, M6 r8 (not pend) | — | coe:numbers.md § guided-tts l.1785–1797 (= gt:numbers.md); cdR C4 | reviewed-stands (guided-tts verdict; ratios not individually recounted) · file | capability-defs quotes "1.8× tokens, 2.2× GPU" without this model label (cdR C4). The cost on pend is not measured. |
| L32 | At matched sampled tokens (64 plain-equivalent attempts), guided-logical beats plain on long problems (90 release theorems > 10 lines) in **6 / 6** models: +5.2 to +10.3 pp (IQM +9.1 cap 12, +8.3 cap 6; MDD 2.7); +3.4 to +12.7 pp at 256. Guided-structural ≈ plain (\|Δ\| ≤ 1.2 pp). | M12 r8, M6 r8 | Lean·gt | gt:run_guided_tts.md l.13–17; gt:review_guided-tts.md §Verdict | reviewed-stands · copied | r8 models, on the release problems, not the 322. At k ≤ 2 logical loses on wall-clock at cap 12. `max_action` truncates 1.7–3.2 % of plain cap-6 attempts. Do not call the step checker "proof-level agreement" (gt reword 1). |

## F. Families, excluded middle, teachability

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L33 | **Correction (a).** capability-defs' families row "negated conditional, classical members: held-out at budget 5 / 5, 3 / 5, 5 / 5 of 5 → elicited on 3 / 3" was read on 5 **G4ip-provable** members. holdout250 has 5 `negated_conditional` members and **0** key-step (classical-only) ones; `cd_part3.py` l.139 falls back to all members when a family has none (`fam_key[f] = need if need else mem`). | M12 | G4ip + Lean·cd | cd:REPORT.md §3.6 l.347 (cdRC l.384 uncorrected); coe:preregistration/create-or-elicit.md l.100, l.111–113 | contradicted (this run, 2026-10-12) → **there is no held-out at-budget reading of the classical members; this run uses the 18 transfer key-step members** · recount (python on families.json: h250 members × `classical_only`; code read) | Training shares (20 key-step trained members) are unaffected (cdR C2 #28). |
| L34 | holdout250 key-step members per classical family: excluded_middle 6, peirce 2, peirce_sequent 3, negated_conditional 0, demorgan_nand_to_or 1, contraposition_conv 3 (15 in all; 123 in the transfer pool). | data | G4ip | coe:preregistration l.95–104; coe:data/coe/families.json | unreviewed (this run's file) · recount (families.json) | capability-defs' family table omits `contraposition_conv`, a classical family that the full bases mostly solve in round 1 (coe prereg l.243, unreviewed). |
| L35 | Excluded middle (A ∨ ¬A, 39 classical-only held-out instances). pend 0 / 39 on all seeds; holdout250 members 0 of 6 in 66,560 attempts each. r16: **0 / 36 (pass@1 0.70) / 13 (0.13)** of 39; holdout250 r16 0 / 6, 6 / 6, 1 / 6. | M12 | Lean·cd | cd:REPORT.md §3.6 l.344, l.359–362; cdR R7 l.236–250, C1 #8 | reviewed-corrected (wording) → **acquired in full on s1, partly on s2 (13 / 39, 1 / 6), not on s0** ("one seed's RL" is wrong) · copied | The brief's "one seed in three found it" needs the s2 qualifier. |
| L36 | s1's acquisition is a burst at rounds 13–14: excluded_middle pool instances 1 → 38 of 40. 34 of s1's 68 new r9–r16 targets are LEM instances; s0 solves **0** of those 34, s2 **8**. | M12 r9–r16 (A40) | Lean·rc | rc:review_rl-continue.md §Verdict (l.206+), reword 1; rc:run_rl_continue.md l.21 | reviewed-corrected → **0 / 8** (the run file's "1 / 9" counted the L_true-9 targets) · copied | One seed; how often the escape happens is unknown at n = 3. |
| L37 | Families at 32 attempts (training shares). r16: excluded middle 0.00 / 0.95 / 0.26; Peirce 0.00 / 0.27 / 1.00; Peirce sequent 0.30 / 0.05 / 1.00; negated conditional 1.00 / 0.65 / 1.00; De Morgan ¬(A ∧ B) 0.00 on all seeds. pend round 1 ≤ 0.05 for all. | M12 | Lean·cd | cd:REPORT.md §3.6 l.342–349; cdR C2 #28 | reviewed-corrected (wording) → **shares are over key-step trained members (39 / 15 / 20 / 20 / 40 / 13 of 40), not "the 40 trained-on members"** · copied | |
| L38 | Four demonstrations (s1's RL proofs of other LEM instances, one 600-step fine-tune) install the schema in every full base: pend + A4 **36 / 33 / 36** of 39 (pass@1 0.66 / 0.35 / 0.64); A16 37 / 34 / 37. Replay-only A0 and 16 non-LEM proofs (C16) give 0. | M12 pend + fine-tune | Lean·cd | cd:REPORT.md §3.6 l.365–378; cdR R7, C2 #29 | reviewed-stands · copied | Plain reads only. The demonstrations are other instances of the same schema. "Every base" here means the three full bases; the knockout was tested with 16 (L39). |
| L39 | KO-DN solves 0 of 39. With 16 LEM demonstrations and K12 replay (J6) it solves 35 / 37 / 37. In J6b (DN-free replay, 2 fine-tune seeds) the gain over matched non-LEM controls, pend vs knockout, is **+0.051 / −0.013 / −0.013**: teachable, not latent (pre-registered: latent if ≥ 0.3 apart on ≥ 2 / 3 seeds). | KO-DN, M12 pend | Lean·cd | cd:REPORT.md §3.6 l.373–384; cdR R7, C1 #8, V stands 4 | reviewed-stands · copied | KO-DN is not K12⁻. Teachability is not RL discovery. Plain reads only. |
| L40 | KO-DN general ability: held-out greedy 0.862 / 0.848 / 0.862 vs pend 0.921 / 0.936 / 0.962 (**−0.058 / −0.089 / −0.100**); holdout250 solved@256 **0.878 / 0.800 / 0.850 ×** pend's x1 count. | KO-DN vs M12 pend | Lean·cd | cdR R7 l.253–258; cd:cards/causal-ablation.md l.36–38 | reviewed-stands · copied | KO-DN removes every DN record. K12⁻ keeps DN on premises and hypotheses (3.29 % of records), so expect smaller drops (this run's E1: 4–12 pp). |
| L41 | Held-out members at budget (holdout250 key-step; the base reaches a member if p̂ ≥ 1 / K_eval-set), as base reaches / r16 solves per seed. Peirce: 0 / 0, 0 / 1, 1 / 2 of 2 (s1 borderline; s2 elicited). Peirce sequent: 1 / 2, 0 / 2, 3 / 3 of 3 (s1 created; s0, s2 elicited). De Morgan: 0 / 0 of 1 (never acquired). | M12 | Lean·cd | cd:REPORT.md §3.6 l.344–349; cdR C2 #28 | reviewed-stands (except the negated-conditional row, L33) · copied | 1–3 members per family, so one member decides a verdict. K is mislabelled (L5). |
| L42 | Every rule RL uses occurs in ≥ 8.0 % of K12 records (all 13 rules). DN applied to a NEGI line (σ) occurs in **16,703** K12 records. | data (K12) | — | cd:REPORT.md §2 l.70 ("≥ 4 %"); cdR C2 #39; coe:preregistration l.16–21 (re-derived, `coe_sigma.py`) | reviewed-stands · copied | "≥ 4 %" is true but weak; quote ≥ 8.0 %. |

## G. RL-free controls (replay-only, J7)

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L43 | Solved of the 322 at k 256 (x0): replay-only r8 **239 / 244 / 249**; J7 continuation **220 / 215 / 219**; pend 232 / 236 / 234; r8 286 / 286 / 293. | M12, RO, J7 | Lean·cd, ·rfc | cd:REPORT.md §3.2 l.164–166, §3.7 l.408–418; cdR C1 #3, C2 #32 | reviewed-stands · copied | RO trains 1.3–1.6× fewer tokens than the ladder and ran on A6000 (rfc review). |
| L44 | J7 used 60,863 GPU-s, **82 / 84 / 81 %** of the ladders' 73,838 GPU-s (18,308 / 20,494 / 21,824 s). | J7 (A40) vs M12 ladder (A6000) | — | cd:REPORT.md §3.7 l.411; cdR C2 #33, V reword 8 | reviewed-corrected (label) → **the ladders' seconds are RTX A6000 and J7's are A40: matched across GPU classes, not "A40-seconds"** · copied | |
| L45 | More pretraining on K12 is a lateral move. J7 gains 12–19 theorems pend misses and loses 30–42. It solves 19 / 18 / 16 of the equal-k sets and 4 / 4 / 0 of the compute-matched sets. θ +0.51 / +0.58 / +0.58 (reviewer's fit +0.51 / +0.62 / +0.48) vs r8 ≈ +2. | J7 | Lean·cd | cd:REPORT.md §3.7 l.408–419; cdR C2 #32 | reviewed-stands · copied | Plain read only. |
| L46 | "pend had already seen each K12 proof ≈ 20 times." | M12 pend | — | cd:REPORT.md §3.7 l.421; cdR C2 #34, V reword 4; cdRC l.460–461 | reviewed-corrected → **≈ 3.7 epochs of pairs (3.69 / 3.72 / 3.72; ≈ 190 pairs per step)** · copied | J7's stated mechanism ("compute without new data buys little after 20 passes") must be reworded. |
| L47 | At matched IRT ability gain, EI "creates" no more DIF+ items than RL-free training. EI r2: 48 / 41 / 48 at Δθ 2.33 / 2.05 / 2.69 (rate 0.86 / 0.72 / 0.62). RO r8: 50 / 49 / 54 at Δθ 2.12 / 2.09 / 2.14 (rate 1.04 / 0.80 / 0.73). | M12, RO | Lean·cd | cd:REPORT.md §3.7 l.392–404; cdR C1 #7, C2 #30 | reviewed-stands (reviewer's own 2PL: Δθ within 0.03, counts ±2) · copied | The matching is approximate: s2's EI r2 is 0.5 θ above its placebo. The older "26–30 vs 4–7" contrast compared Δθ 2.1 with 0.6. |
| L48 | Update size (relative Frobenius norm of the weight change, s0): RL r8 **0.28**, replay-only 0.30, late pretraining (step 20,000 → pend) 0.81, two seeds' bases 1.43. The RL and replay updates have cosine 0.45. | M12 s0, RO s0 | — | cd:REPORT.md §3.7 l.406; cdR C2 #31 | reviewed-stands (0.282 / 0.297 / 0.809 / 1.426; cos 0.452) · copied | One seed. |
| L49 | Replay alone recovers pretraining: the replay-only control from step 1,600 reaches 28–33 / 72 textbook72 and 195–202 / 250 holdout250 (the pend start gives 33–36 and 196–205). RL adds to replay at every start in every seed. | M12 checkpoints, RO | Lean·rfc | rfc:run_rl_from_ckpt.md l.11–14; rfc:review_rl-from-ckpt.md §Verdict | reviewed-stands · copied | The RL-vs-replay increment (+6 to +15 textbook72) is partly confounded with training length (1.3–1.6× tokens). Say "solves in neither sample seed at r8", not "never solves". |
| L50 | J8 start dependence. From step 1,600, r8 has 182 / 157 / 167 new solves, 21 / 33 / 25 % elicited at K_total, and replay-only from the same start solves 83 / 84 / 83 % of them. 21–47 remain net of replay at every start. | M12 checkpoints | Lean·cd | cd:REPORT.md §3.7 l.424–437; cdR C2 #35, C3 J8 | reviewed-stands · copied | Not monotone in the start. K_total mixes classes. |

## H. Interface (support-state, support-curves, claim-audit)

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L51 | "The 29 earlier creations": after 8 EI rounds, WP EI s0 solves 29 transfer theorems (p̂ 0.022–0.9995) that WP base s0 solved 0 times in 400,000 attempts (200k at T 0.8 + 200k at T 1.0). | M3.2-WP base s0 vs EI s0 | Lean·sc | sc:review_support-curves.md l.340–346 (44 / 37 / 35 / 33 / 30 / 29 at 10k / 40k / 50k / 100k / 150k / 200k per temperature); sc:`data/sc/falsifier_survivors.txt`; ca:audit/CLAIMS.md l.19 (C1) | reviewed-corrected → **37 at the pre-registered depth (≥ 40k per temperature), 29 at 200k; p̂ up to 0.9995 (not 1.000)**. The executor's "44 → 35 → 29" calls 35 the pre-registered depth (wrong) · copied | Defined against **one** WP base seed. A second base seed reaches 3 of the 29 in 200k; a 7.9× larger base reaches 0 and 2 (C1, "holds with caveats"). |
| L52 | "A proof-state base reaches **28 of the 29** with no RL": SN base s0 and s1 each reach 28 (misses `la_transfer_1893` / `_1110`); 26 / 23 within 10,000 attempts at T 0.8; median p̂ 0.19 (s0). | M3.2-SN bases s0, s1 (no RL) | Lean·ss | ss:run_support_state.md l.8; ss:numbers.md § support-state SS1 l.1323–1335; ss:review_support-state.md §Verdict l.185–189; ca:review_claim-audit.md l.203 | reviewed-stands (as a reach statement: claim-audit C2a "solid") · copied | **The older 3.2 M organism** (4 × 256, cap-6 data, no RL), 2 seeds per arm. "Reach" = ≥ 1 Lean-accepted attempt in ≤ 400k (200k T 0.8 + 200k T 1.0, stop at 5 hits). Do not set it against "EI solves 29" without saying the bars differ (L53). Brief ✓. |
| L53 | At EI's own bar for "solves" (p̂ ≥ 0.01, T 0.8), the SN base clears **21 (s0) / 14 (s1)** of the 29. ≥ 1 hit at T 0.8: 27 / 26. | M3.2-SN | Lean·ss (fresh re-sample in ca) | ca:audit/CLAIMS.md l.20 (C2a); ca:numbers.md l.1714–1717 (CA1); ca:review_claim-audit.md l.204 | reviewed-stands · copied | p̂ comes from early-stopped (`stop_at` 5) T 0.8 rows. s0's 21 was confirmed on a fresh re-sample; s1's 14 was not. One SN attempt is an episode, one WP attempt a whole-proof sample. Not the same as state-env's 21 / 18 at 256 attempts. Brief ✓. |
| L54 | "The whole-proof support expansion is, on these theorems, about state", "not the environment's naming". | M3.2-SN vs S (self-naming) | — | ss:run_support_state.md l.10; ca:audit/CLAIMS.md l.21 (C2b); ca:audit/C2.md l.63–65; ca:review_claim-audit.md l.205, l.234, l.250 | reviewed-corrected (wording) → **"A base acting through the proof-state *step interface* reaches 28 / 29 … the state and the step interface are not separated"** (C2b "weaker than stated"), with the label "3.2 M, from scratch, cap 6" · copied | The step interface = per-action generation, environment-written box-closing and Or.elim tokens, and early stop on a failed action; no arm has the steps without the state. "Not naming" is a null on reach at n = 2 (S reaches 28 and 25), yet S/SN median p̂ is 0.16 (s0) / 0.69 (s1). The reviewer did not re-derive the confound. The fix is applied only in nd-rl `docs/project_strategy/2026-10-03-claim-audit.md` l.33; the support-state write-up still says "about state". |
| L55 | The WP base's pass rate on the survivors is **< 7.5 × 10⁻⁶** (95 %). Teacher-forced base probability of EI's proofs: median 4.7 × 10⁻¹⁴ over 297 crux proofs; best on the survivors 9.5 × 10⁻⁸. | M3.2-WP base s0 | Lean·sc | sc:review_support-curves.md l.155–158, l.258, l.347–349 | reviewed-stands · copied | The teacher-forced value bounds that one proof only, not the theorem's p. |

## I. Exact likelihoods (`trajectory`)

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L56 | B's eventual proof (r8's most likely accepted x0 sample): worst step ≈ **−6.2** nats at the end of pretraining → ≈ **−1.3** at r8, mostly by r4. Totals at pend: −16.9 / −14.2 / −15.0. | M12 | Lean·tj | tj:numbers.md § trajectory (l.1705+); tj:review_trajectory.md Compare, Verdict (i) | reviewed-stands · copied | T 1.0, scored under canonical names. Env-assigned names are not scored, while the sampler conditions on its own names (R5a). |
| L57 | After Stage-1 step 1,600, B's eventual-proof worst step rises about as much in pretraining (Δ_PT +3.42 / +4.06 / +4.79, IQM 4.09) as in RL (Δ_RL +5.09 / +4.62 / +4.07, IQM 4.59). | M12 | Lean·tj | tj:review_trajectory.md Compare row "B Δ_RL", Verdict (ii), reword 1–2 | reviewed-corrected → **"not resolved at n = 3"** (the pre-registered falsifier fires on 1 / 3, so not "falsified"); **"after step 1,600"**, not "late" (8k → end: +1.8 / +2.8 / +3.2) · copied | The clean miss: Δ_PT was predicted at −1 to +3. |
| L58 | RL lifts B's fixed reference proofs too (+1.79 / +0.96 / +1.89; IQM 1.55, CI [0.79, 2.31]), about three times less than its own eventual proofs (+4.6). | M12 | Lean·tj | tj:review_trajectory.md Compare, Verdict (iii), reword 3 | reviewed-corrected → **"lifts the known proof too, three times less"**, not "not known ones" · copied | Eventual proofs are chosen as r8's argmax, so part of the gap is by construction. |
| L59 | Group C (neither pend nor r8 solves; 36 / 35 / 28 per seed): reference proofs do not improve under RL. The worst step stays near −9 to −10 nats (Δ_RL IQM −0.23; s0 −3.29). | M12 | Lean·tj | tj:review_trajectory.md Verdict (iv), reword 4–5 | reviewed-corrected → **"one bad step" is not supported: 55–86 % also have a second step below −4; the per-seed criteria miss in 2 / 3 and 1 / 3** · copied | Pretraining cut-offs reach 18.7 % on the C strata. |
| L60 | pend held-out greedy (p2/heldout, 5,000): **0.921 / 0.936 / 0.962**. Cumulative r8 targets: 4,383 / 4,365 / 4,407 of 4,495. | M12 | Lean·tj | tj:numbers.md l.1721–1723; tj:review_trajectory.md Compare row 3 | reviewed-stands · copied | Seed sd 0.021 (the basis of this run's MDD). |

## J. Model-card headline numbers

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L61 | `state_env_october` (plain, r8): textbook72 pass@256 **52 / 51 / 52** of 72; dev metric 1,058 / 1,050 / 1,055 of 1,108; holdout250 239 / 237 / 237; L_true 13–16 377 / 375 / 376 of 380; ≥ 17 lines 21 / 21 / 20 of 21. | M12-bs r8 | Lean·bs | cards/state_env_october.md l.31–40; bs:review_best-state.md §Verdict | reviewed-stands (source reviewed; the card itself was not reviewed) · copied | These are best-state's seeds, not trajectory's. Compare r16 against trajectory's r8 (L63). |
| L62 | Same card, from guided-tts (trajectory seeds, k 256, not compute-matched): textbook72 plain 48 / 48 / 53 vs guided **54 / 52 / 57**. At matched tokens guided beats plain by +5.4 pp (textbook72) and +9.1 pp (long). | M12 r8 | Lean·gt | cards/state_env_october.md l.41–50 | reviewed-stands (guided-tts reviewed) · copied | Cap-12 textbook72 has a 2-theorem renaming-class overlap with K12 (gt reword 5). |
| L63 | `state_env_october_r16` (plain, T 0.8). textbook72 pass@256 **51 / 57 / 56** (pend 34 / 33 / 36, r8 48 / 48 / 53). holdout250 240 / 246 / 239. `rl_targets` 4,403 / 4,433 / 4,429 of 4,495. Group C pass@256 0.167 / 0.486 / 0.143 (r8 0.083 / 0.029 / 0.036). r9–r16 used 31,471–33,261 A40 GPU-s per seed. | M12 r16 | Lean·rc | cards/state_env_october_r16.md l.29–46; rc:review_rl-continue.md §Verdict | reviewed-stands · copied | The pend / r8 columns are a different draw from trajectory's x0 (textbook72 32 / 32 / 38 and 48 / 49 / 54); draws differ by up to 4. Group C counts are lower bounds (cut-offs 0.1–1 % per stratum, rows up to 6.6 %). Plain only. |
| L64 | "RL is close to saturating its targets: 97.1–98.0 % solved by r8." | M12 r8 | Lean·tj | cards/state_env_october.md l.56 | contradicted (interpretation) → the percentages hold (4,365–4,407 of 4,495), but **rl-continue falsified "saturated" as pre-registered**: group C rose on 3 / 3 seeds and s1 added +68 targets (rc review §Verdict) | Use the r16 card's limits ("62–92 unsolved of 4,495"). |
| L65 | After the same T1 ladder, every best seed beats every 3.2 M seed: textbook72 margins cap 6 **+18.3** (MDD 9.3), cap 12 **+14.2** (MDD 6.5). Frozen at cap 12 the recipes are level (textbook72 +1.2). | M12-bs vs the 3.2 M lean_seq recipe | Lean·bs | bs:review_best-state.md §Verdict | reviewed-stands · copied | Not compute-matched. The best recipe's RL used 1.6–1.9× the GPU time on the same class (A40); "2×" mixes classes (bs reword 6; card l.60). |
| L66 | rl-continue-cap6: cap-6 r16 is below cap-12 r8 on all three seeds. Group C pass@256 rose +0.115 / +0.115 / +0.133 (r8 → r16). New targets r9–r16: +69 / +82 / +123. | M6 r16 | Lean·rc6 | rc6:run_rl_continue_cap6.md l.1–12; rc6:review_rl-continue-cap6.md §Verdict | reviewed-stands · copied | Say "has not yet reached" cap 12, not "stops below": the gap narrowed on every seed (126 → 77, 130 → 116, 203 → 102 targets). Group C levels are lower bounds (3–19 % cut-off). |

## K. Literature (only where a verified note or claim ledger exists; V = quote found verbatim at the stated place)

| id | claim | model | checker | source | review status | caveat for the paper |
|---|---|---|---|---|---|---|
| L67 | Yue et al. (2504.13837v5): "base models consistently surpass RLVR models across all benchmarks and LLM families as k increases" (Sec. 1). The base-✗ / RL-✓ fraction is tiny (Table 2). | LLMs | — | lit:2026-10-02-lit-review-2/claims.md l.10–12 | verified quote (V) | Equal k (≤ 1,024), no compute matching: the design this paper's L1 → L2 corrects. |
| L68 | Abdulsalam, Patel & Saxe (2607.07646v1): in a from-scratch rewrite-grammar organism whose pretraining excludes the shortcuts, "even at pass@1024, the pretrained policy gets 0% on Buckets 4–5, while RL later solves them at pass@16". Low-ρ pretraining "never reliably enters the macro or parallel regime". | 12-layer, d 512 transformer | — | lit:2026-10-02-lit-review-2/claims.md l.100–106; notes/abdulsalam-rl-compositional-rewrite.md | verified quote (V) | Their new behaviour is a new action type. Equal k (pass@1024), no compute-matched budget. |
| L69 | Tsilivis et al. (2510.11495v2), on parity: RL after NTP amplifies a rare long demonstration (STaR recursion p_n = 2p_{n−1} / (1 + p_{n−1})). Efficient "as long as the proportion of long demonstrations in the data mix is not exponentially small". | small transformers | — | lit:2026-10-02-lit-review-2/claims.md l.107–111; notes/tsilivis-rl-after-ntp-parity.md | verified quote (V) | "Tsilivis tests p_cot = 0" is **UNVERIFIED**: the lowest found is 0.01 (claims.md l.112). Zero exposure, the knockout's case, is untested there. |
| L70 | Interplay (2512.07783v1): 100 M model, from scratch on synthetic dependency-graph problems. RL raises pass@128 only at the edge of competence (op 11–14, where base pass@128 > 0). Context exposure of 0 % / 0.1 % gives no transfer; 1 % enhances it. | 100 M Qwen2.5-style | — | lit:2026-09-29-lit-review/REVIEW.md l.227 (V); notes/zhang2025-interplay-pre-mid-rl.md | verified quote (V) | Process-verified pass@k. The exposure result is about a context, not a rule. |
| L71 | Karan & Du (2510.14901v1): Metropolis–Hastings sampling from the base's power distribution p^α (α 4, no training) reaches MATH500 0.748 vs GRPO 0.785, at 8.84× the tokens. | LLMs | — | lit:2026-09-29-lit-review/REVIEW.md l.222–224 (V); notes/karan2025-power-sampling.md | verified quote (V) | |
| L72 | Ji et al., "Scalable Power Sampling" (2601.21590v1): a token-level approximation "matches or surpasses one-shot GRPO" at > 10× less latency than MCMC. | LLMs | — | lit:2026-10-02-lit-review-2/REVIEW.md l.66–68; claims.md l.176 | unreviewed: an abstract-level quote only, no in-depth note | The brief cites it for Phase 2. Verify before the paper relies on it. |

## The brief's precision points against this ledger

- **Interface.** It holds: L52–L54 (3.2 M organism, 2 seeds per arm, step-interface confound, 21 / 14 at p̂ ≥ 0.01). Two
  refinements:
  - The audit's confound is the whole step interface, not only step-by-step generation.
  - "The 29" were defined against one WP base seed (L51).
- **Estimator.** It holds for the 0.93–0.98 figure: calibration theorems with 3–100 / 512 (L15). A wider and much
  noisier comparison exists on 64 / 60 / 72 measured theorems (L16).
- **Budget.** It holds: A6000 ÷ A40 (L5); 5.6–6.2 × 10³ ladder attempts per theorem (L9); 33 / 28 / 28 at 0.3× (L8).
  Four refinements:
  - The 5.6–6.2 × 10³ counts eval-phase attempts; training-target attempts are 3.6 × 10³ per theorem.
  - The ladder-attempt budget is 0.26–0.29 × K, so its set is **≥** 33 / 28 / 28.
  - s2's budget includes an OOM'd round (L7).
  - The J9 certificates have only ≈ 8 % slack in K (L20).

## Not yet in this ledger (the executor adds them)

- This run's own numbers: K12⁻ shape, the families table, the old seeds' allocation shares, E1–E7, and Phase 0.1 / 0.2
  outputs.
- When Phase 0.2 measures the A6000 and A40 per-attempt costs, L5–L9, L20 and L41 must be restated.
