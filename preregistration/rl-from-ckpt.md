# Pre-registration: rl-from-ckpt — the T1 ladder from earlier pretraining checkpoints

Run `rl-from-ckpt` (executor, 2026-10-02). Brief: `~/runs/rl-from-ckpt` run brief; proposal 19
(nd-rl `docs/proposals/2026-10-02-rl-from-pretraining-checkpoints.md`). Fork branch `dan_rl-from-ckpt`.
Checker: **Lean alone** (`lean_judge` in the state environment); `nd_verify` judges nothing.

## Question

Does RL (expert iteration, the T1 ladder) only finish what pretraining started — solving a theorem only when its
hardest step is already likely enough at the start of RL — or can RL from a less-pretrained checkpoint solve theorems
whose hardest step is far below that threshold?

## Models (every number below)

`trajectory`'s three best-cap12 seeds: `best_model.ALiBiGPT` 6 × 384, **9,560,832 params**, `lean_staten`, from
scratch on K12 (`data/kh/train_k12.jsonl`, 155,000 records, cap 12), Stage-1 1,200 s on an A40 (≈ 24,100 steps).
Starts: kept checkpoints `ckpts/tj/stage1_best12_s{0,1,2}_b1200_step{0,1600,5000,12000,16000}.pt` (bucket
`trajectory/`), plus the end checkpoint (`pend`, 100 %), whose ladders `la_T1_best12_s{0,1,2}` (r1–r8, with reads and
scores) are `trajectory`'s and are reused, not re-run. Inherited numbers carry this label.

## Design (what will run)

1. **15 T1 ladders** `la_T1_best12_s<S>_<start>`, start ∈ {p0, p1600, p5000, p12000, p16000}, seeds 0–2:
   `state_ladder_ei.py` with `trajectory`'s exact flags (defaults: 8 rounds × k 32, T 0.8, `data/ladder/rl_targets.jsonl`
   4,495 targets, `--retain` 20,000 K12 replay records, `max_per_thm` 4, `rl_weight` 4, 600 fine-tune steps × 128
   proofs at lr 3e-4 → 3e-5; ladder batch 2,048, one fallback resume at 1,024 on a sampling OOM as `trajectory` s2).
   One ladder per pod (RTX A6000 / A40). Every round's checkpoint kept (uploaded on save).
   - **Stop rule, p0 only:** run rounds 1–2; if they accept no target proof, stop and report the counts.
2. **Added: replay-only controls** `rc_best12_s<S>_<start>` for start ∈ {p1600, p5000, p12000, p16000, pend}
   (`rfc_replay.py`; 15 runs; also p0 if its ladder trains). **Why (deviation from the brief):** the ladder's
   fine-tune trains on `--retain` 20,000 random K12 Stage-1 records every round (whenever ≥ 1 proof is accepted), and
   the ladder's 4,800 fine-tune steps carry ≈ 750 M training tokens (`trajectory`'s compute table) against ≈ 445 M
   for all of Stage-1. From an early checkpoint the ladder is therefore also substantial *further pretraining*, so a
   solve from low x at the start cannot be read as RL creating anything. The control runs the same 8 fine-tunes
   (same flags, per-round seeds, 20,000 fresh replay records per round) with no sampling and no RL records. It sees
   replay more often than any ladder (the ladder's mix also holds 10k–70k RL records), so it over-states the replay
   effect: conservative for a "creation" reading. Cost ≈ 1 GPU-h each.
3. **Read-outs** (`trajectory`'s `state_eval.py` settings: k 256, T 0.8, `max_steps` 96, `max_action` 512, batch
   2,048, retry at 1,024 on OOM; textbook72 + holdout250 = 322; evaluation only, never trained on):
   - each ladder at r2, r4, r8, sample seeds 0 and 1; r0 = the start, reused from `trajectory`;
   - reproducibility: seed 0's four non-trivial starts re-read with sample seed 1 and compared per theorem;
   - each control at r8, sample seeds 0 and 1.
4. **Teacher-forced log p** (`tj_score.py`, T 1.0, 33-base marginalisation, env-assigned names masked): the 315
   reference proofs (`trajectory`'s `ref_targets.jsonl`) and each ladder's own eventual proof (`tj_targets.py`: the
   most likely of r8's distinct accepted sample-seed-0 proofs) under r0, r2, r4, r8 of that ladder and under the
   control's r8; the references also under seed 0's starts as a re-score check against `trajectory`.

**Arms are matched on** the RL protocol (rounds, k, targets, fine-tune steps and mix size), not on compute: weaker
starts may generate more tokens per attempt. Compute rows (GPU-s, gen tokens, attempts, train steps/tokens, Lean
checks) per arm and round; any arm > 1.25× the pend arm on a measure is flagged.

## Definitions for the analysis

- **x_start** = worst-step log p (nats, T 1.0) of the theorem's reference proof under the start checkpoint
  (`trajectory`'s `artifacts/tj/score/{s,new8_s}<S>/`). **x_ctrl** = the same under that start's control r8.
  **x_ev** = worst step of `trajectory`'s eventual proof (end-arm r8's own, where it exists) under the start.
- **y** = solved by the ladder's r8 at k 256, sample seed 1 (Lean-accepted, any proof).
- **Fits:** logistic P(y | x), x clipped at −40, per start and per seed; pooled with seed as a fixed effect;
  threshold x50 where P = 0.5; IQM over seeds with a stratified-bootstrap 95 % interval.
- **Null curve:** the end arm's own fit (`artifacts/rfc/prereg_numbers.txt`, from `trajectory`'s records):
  b0 = 5.34, b1 = 0.482, **x50 = −11.1** (per seed −10.9 / −11.3 / −11.1). Under it the expected number of
  r8 solves among pairs with x_start < −12 is p1600 20.9 (of 120 pairs), p5000 10.4 (66), p12000 8.4 (50),
  p16000 9.4 (43): **49.1 in total** (279 pairs). The end arm itself solves 7 of its 25 such pairs (4.7 expected).

## Expected results (numeric; r8, sample seed 1, k 256, per seed)

| start | textbook72 /72 | holdout250 /250 | control r8 tb72 | control r8 h250 |
|---|---|---|---|---|
| p0 | stop rule fires (P ≈ 0.9): 0 / 0 | 0 | — | — |
| p1600 | 40 [28, 52] | 225 [195, 242] | 28 [15, 40] | 185 [130, 220] |
| p5000 | 45 [34, 55] | 232 [212, 243] | 31 [20, 40] | 195 [160, 222] |
| p12000 | 47 [38, 56] | 235 [222, 244] | 33 [24, 42] | 200 [175, 225] |
| p16000 | 48 [40, 56] | 236 [225, 244] | 34 [26, 42] | 205 [185, 228] |
| pend (inherited) | 48 / 48 / 53 | 240 / 236 / 237 | 35 [28, 44] | 208 [195, 228] |

- r8 rises with the start in rank order (p1600 ≤ p5000 ≤ … ≤ pend on the IQM); the gap pend − p1600 on textbook72
  ≈ +8 (range 0 to +20).
- Ladder minus control (RL's own increment) > 0 at every start: ≈ +12 textbook72, +30 holdout250.
- **Threshold test, brief's literal form (x_start):** the curves do **not** coincide; x50 moves down for earlier
  starts — p16000 ≈ −14, p12000 ≈ −16, p5000 ≈ −18, p1600 ≈ −22 (end −11.1). Solves from x_start < −12 over the
  four starts and three seeds: **≈ 110 [70, 170]** against the 49.1 the end-arm curve predicts. I expect this to be
  produced by the ladder's replay pretraining, not by RL.
- **Replay-corrected form (x_ctrl), the decisive one:** P(y | x_ctrl) for every start lies on the end arm's curve
  within the MDD; x50 within ±2.5 nats of −11.1 at every start.
- **Group C** (`trajectory`'s per-seed hard set, neither r0 nor r8 of the end arm solves): an early-start ladder
  solves ≤ 4 C theorems per seed at r8 (sample seed 1; the end arm: 3 / 1 / 1 of 36 / 35 / 28).
- **Analysis 2:** RL does not substitute for pretraining at the compute it costs: a ladder ≈ 25,000 A6000-s,
  ≈ 18× all of Stage-1 (1,350 A40-s); skipping 93 % of pretraining (p1600) costs ≈ 8 textbook72 theorems at r8.
- **Reproducibility:** re-read solved counts at seed 0's starts within ±3 per pool of `trajectory`'s; re-scored
  reference worst steps within 1e-3 nats.
- Truncation (action cap 512 / step cap 96) per stratum ≤ 2 % at RL checkpoints; up to ≈ 20 % at early starts
  (`trajectory`); reported per stratum.

## Falsifiers

- **"RL only finishes what pretraining started" (H_E) is falsified** if, on the replay-corrected form, the excess
  E = (pairs with x_ctrl < −12 solved by the ladder's r8) − (Σ of the end-arm curve's P over those pairs), summed over
  starts p1600–p16000 and 3 seeds, is **≥ 15**, with a positive excess (≥ 3) in at least 2 of 3 seeds.
  *Why 15:* the null sum's binomial SD is ≤ √(Σ p(1−p)) ≈ 5 for ≈ 50–150 such pairs at p ≈ 0.1–0.3, so 15 ≈ 3 SD;
  sampling noise alone flips 13 / 966 (1.3 %) end-arm r8 solves between sample seeds, ≈ 4 over 300 pairs.
  The same rule on x_start (brief's literal form) fires at ≥ 49.1 + 15 = 64; I predict it fires and that the
  replay-corrected one does not. If both fire, the reading is creation; if only the literal one fires, the low-x
  solves are attributed to the ladder's replay; if neither fires, elicitation in the strict form.
- Independently: if early-start ladders solve ≥ 10 group-C theorem-seed pairs more than the end arm (3 seeds pooled),
  that is creation-direction evidence on theorems pretraining never made solvable.
- The step-0 arm: any accepted proof in rounds 1–2 is reported as such; if it trains, its control runs too.

## MDDs (from `trajectory`'s seed spread, n = 3 per arm, two-arm difference ≈ 2.3 σ)

- r8 textbook72: σ ≈ 2.9 (48 / 48 / 53) → **MDD ≈ 7 theorems**; holdout250: σ ≈ 2.1 → **≈ 5**. Early starts have
  wider spread (start-checkpoint σ up to 19 on holdout250 at p5000); MDDs are recomputed from the observed per-start σ
  and differences inside them are called "not resolved".
- x50: end-arm σ 0.2 nats → MDD ≈ 0.5; for early starts I assume σ ≤ 1 → **2.5 nats**; shifts inside are not called.
- Paired designs: the ladder-vs-control comparison is paired by seed and start.

## Budget and stop rule

Budget **$90 / 180 pod-hours** (registered with `podbudget` before the first pod). Plan ≈ 140 pod-hours ≈ $72:
13 ladder pods × ≈ 7 h, controls ≈ 15 GPU-h (two per 48 GB card), ≈ 100 reads × ≈ 0.2 h, scoring ≈ 10 h.
If projected spend passes $85, drop in order: control sample-seed-0 reads; r2 reads; r4 sample-seed-0 reads.
Ladders and r8 reads are not dropped. Balance floor $100.
