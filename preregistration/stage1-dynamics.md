# Pre-registration — run `stage1-dynamics`

Written 2026-09-27, before any pod of this run exists. Executor: agent:claude. Repository
`~/work/stage1-dynamics`, branch `dan_stage1-dynamics` (worktree from the fork's `origin/dan`).
Governed by `AGENT_POLICY.md` (nd-rl canonical copy). Budget **$15 / 30 pod-hours**, registered
`podbudget stage1-dynamics --set 30 15` before the first pod.

## The question

Dan's reading of the 52 noise-floor training curves: **`train.py`'s validation loss only ever
measured 2- and 3-line proofs** (the first 2,000 records of a length-sorted held-out file), it is
flat by step 6,000, and its final value is uncorrelated with the 6-line and depth-3 accuracies that
actually vary across runs (1.4 % spread in loss against 0.42–0.92 and 0.008–0.918 in accuracy). So:

1. Past 6,000 steps, do 6-line and depth-3 held-out accuracy keep rising **within the same run**?
   Does validation loss on long proofs keep falling, flatten, or turn up?
2. When is a run's depth-3 mode decided — early, or do low-mode runs cross over with more training?
3. At an equal 6,000 steps, does warmup-stable-decay differ from the current cosine?
4. Is a gain from longer training a gain from **steps**, or from repeating the same 155,000 proofs?
5. Is **per-length** validation loss a usable proxy for per-length accuracy, unlike the 2k loss?

## The model every number below is about

A **3,214,336-parameter from-scratch GPT** (4 layers, d 256, 8 heads), Lean surface format
**`lean_seq`**, **cap 6**, `--bs 128 --lr 1e-3 --min_lr 1e-4 --warmup 200` — the noise-floor control
configuration, so the 52-cell floor applies. Arms C and W train on the control's own set
`data/p2/train_depth3_f0_a1.jsonl` (155,000 records, flat 31,000 per length 2–6, depth-3 excluded);
arm F trains on `data/sd/train_fresh.jsonl`. Every table in the write-up will repeat this label.

## Design actually being run

**Judging: Lean alone** (`AGENT_POLICY.md`, Dan 2026-09-27). A sample counts iff the literal sampled
text parses in the strict `lean_seq` grammar **and** Lean 4 core accepts that literal text as a proof
of the theorem (`sd_eval.py`, which imports `lean_gate.lean_check` and never calls `nd_verify`). The
noise-floor baselines quoted below were measured under **Lean ∧ `nd_verify`**, which differs from
Lean alone by ≈ 67 per million on held-out greedy; every comparison across that boundary is labelled.

**Instrumentation** (`train.py`, committed before the first pod; all of it opt-in, so the default
command line trains bit-identically to before):
`--val_bins` reports validation loss on the **whole** held-out file per length bin (2–6), on the
depth-3 slice (500 records, all 6-line) and on the 6-line non-depth-3 complement, every
`--log_every` = 200 steps, on a fixed name-shift presentation drawn from its own rng so that it
consumes nothing from the training rng; the old first-2,000 number is still printed as `val` and
recorded as `val2k`. `--metrics FILE` writes one json line per logged step. `--sched wsd
--decay_frac 0.2`. `--ckpt_every`, `--state_at`, `--resume` (weights + optimiser + step + rng).

**Arms, paired seeds 0–7 in C and W (the same seed list, as `NOISE_FLOOR.md` correction 2
recommends):**

| arm | schedule | steps | data | seeds |
|---|---|---|---|---|
| **C** | cosine 1e-3 → 1e-4 (the current recipe) | 6,000 | control set | 0–7 |
| **W** | WSD: warmup 200, constant 1e-3, linear decay to 1e-4 over the last 20 % | 24,000 (decay from 19,200) | control set | 0–7 |
| **W-6k** | resume W's step-4,800 state, decay 4,800 → 6,000 | 6,000 | control set | 0–7 |
| **W-12k** | resume W's step-9,600 state, decay 9,600 → 12,000 | 12,000 | control set | 0–7 |
| **F** | WSD as W | 24,000 | fresh set | 0–3 (extend to 7 if the budget allows) |

Because the learning rate does not affect which batch a step sees, **C and W-6k on the same seed see
the identical 6,000 batches in the same order from the identical initialisation** and differ only in
the learning-rate schedule. That is the tightest schedule comparison available and it is the whole
point of the paired-seed design.

**Fresh set** (`sd_pool.py`, run before the first pod, `data/sd/pool_fresh.json`): the union of the
four noise-floor pools `data/nf/train_p{1..4}.jsonl` (620,000 records), de-duplicated by
atom-renaming class — **572,759 records** survive (47,241 duplicate classes dropped; **0** records
collide with a held-out class). Its composition is 18.4 / 20.4 / 20.4 / 20.4 / 20.5 % at lengths
2/3/4/5/6, against the control's flat 20 % each: the length-2 class universe is smaller, so more of
its draws collide. At 24,000 steps × 128 that is **5.36 epochs**, against the control set's 4.95
epochs at 6,000 steps — the same repetition, which is what makes F−W a steps-vs-repetition contrast.

**Measurements.** Held-out greedy (`data/p2/heldout.jsonl`, 5,000 theorems, k = 1, T = 0, sampler
batch fixed at 512, `max_new` 400), per length bin and on the depth-3 slice, at **every 1,000-step
checkpoint of W** (24 per seed; the trajectory, and the heart of questions 1–2), at every 2,000-step
checkpoint of F, and at the final checkpoint of every arm. Validation losses every 200 steps in
every run. W's trajectory checkpoints up to 19,000 are stable-phase (undecayed); 20,000–24,000 are
inside the decay, and the write-up will say so. No ladder, no coverage, no RL.

## Expected results, with falsifiers

Baselines, all from `noise-floor`'s 52 cells at 6,000 steps under Lean ∧ `nd_verify`
(`artifacts/nf/summary.json`): overall **0.907 ± 0.030**, 6-line bin **0.667 ± 0.152**, 5-line
**0.927 ± 0.015**, depth-3 slice **0.440 ± 0.305** with 24/52 above 0.44, 6-line non-depth-3
**0.824 ± 0.037**. `NOISE_FLOOR.md`'s n = 2 MDDs: 6-line **±81.7 pp**, depth-3 **not resolvable**,
overall **±16.3 pp**, 5-line ±8.1 pp, 3-line ±2.6 pp, 2-line ±1.7 pp — which is exactly why every
comparison below is **within seed**.

### Q1 Saturation

- **E1 (the headline).** 6-line bin, within seed: median(W-24k − W-6k) = **+12 pp** (I will call
  +5 to +25 pp a hit), and **≥ 7 of 8** seeds improve by > 2 pp.
  *Pre-registered falsifier of "long proofs are not saturated at 6k": dead if W-12k and W-24k are
  both within ±2 pp of W-6k on the 6-line bin on ≥ 6 of 8 seeds.*
- **E2.** The cross-seed sd of the 6-line bin **falls from 0.152 at 6k to < 0.10 at 24k** — most of
  the 2.19× spread the floor measures is runs at different distances from the same asymptote.
- **E3.** Overall held-out, within seed: median(W-24k − W-6k) = **+3 to +5 pp**, landing near 0.945.
- **E4.** 2-line and 3-line bins move by **< 1 pp** between 6k and 24k (inside their own floors).
- **E5.** 6-line validation loss at 24k is **below** its 6k value in ≥ 7 of 8 seeds, and no seed ends
  more than 2 % above its own minimum. *Falsifier of "long-proof loss keeps falling": ≥ 3 of 8 seeds
  end > 2 % above their own minimum (memorisation turn-up).* I put ≈ 25 % on that happening by
  20 epochs.
- **E6.** The old `val2k` stays flat while capability moves: **|val2k(24k) − val2k(6k)| < 0.01** in
  ≥ 6 of 8 seeds while the same seeds' 6-line bin moves ≥ 5 pp.

### Q2 When is the depth-3 mode decided

- **E7 (the headline).** High mode = depth-3 accuracy > 0.44 (`NOISE_FLOOR.md`'s cut). At 6,000
  steps **3–5 of 8** W seeds are in the high mode; at 24,000 steps **7 or 8 of 8** are. Hence
  **≥ 2 of 8 seeds change mode after step 6,000 — I expect "the mode is set early" to die.**
  Reported per seed with Wilson intervals on 500 records, never as a mean.
- **E8.** No seed regresses: depth-3 at 24k ≥ depth-3 at 6k − 5 pp for all 8.
- **E9.** Depth-3 accuracy at step 2,000 does not predict the 24k value: Spearman |ρ| over the 8
  seeds **< 0.6**.

### Q3 Schedule at equal steps

- **E10.** W-6k vs C, same seed, same 6,000 batches: **median |Δ| ≤ 3 pp on the 6-line bin** and
  **≤ 1.5 pp overall**, with **≤ 6 of 8** seeds in the same direction (no sign-test signal).
  *Falsifier of "WSD and cosine are equivalent at equal steps": median |Δ| > 5 pp on the 6-line bin,
  or 8 of 8 seeds in one direction.* Prior (the brief's and mine): little difference.

### Q4 More steps or more data

- **E11 (the headline).** Within arm, stable-phase trajectory: **F's 6k → 24k gain on the 6-line bin
  is ≥ 0.6 × W's** — i.e. the gain is bought by steps, not by re-seeing the same proofs.
  *Falsifier: F's gain < 0.5 × W's.*
- **E12.** F-24k − W-24k on the 6-line bin is **+2 to +8 pp** (fresh data helps, modestly), and
  **not** more than +15 pp. More than +15 pp would mean repetition, not steps, is the binding
  constraint at 20 epochs.
- **E13.** F's per-bin validation loss is **higher** than W's at step 24,000 in ≥ 3 of 4 seeds
  (fewer repeats, less memorisation) while its accuracy is equal or better — the cleanest possible
  demonstration that this loss is not the quantity to select on.

### Q5 Is per-length loss a usable proxy

- **E14.** Along the trajectory (8 seeds × 24 checkpoints), Spearman **ρ(6-line val loss, 6-line
  accuracy) ≤ −0.85** pooled and ≤ −0.80 within every seed; ρ(depth-3 val loss, depth-3
  accuracy) ≤ −0.80.
- **E15 (the one that matters).** *Ranking models at a fixed budget*: across the 8 seeds at step
  24,000, **|ρ(val2k, 6-line accuracy)| < 0.5** while **|ρ(6-line val loss, 6-line accuracy)| >
  0.8**. *Falsifier of "per-length loss is a usable proxy": |ρ(6-line val loss, 6-line accuracy)|
  < 0.5 across seeds at a fixed step — then neither loss ranks runs and the only readout is accuracy.*

### Instrumentation cost

- **E16.** Validation on all 5,000 held-out records per bin every 200 steps costs **5–9 %** of
  training wall time (the brief's estimate is ≈ 6 %). Measured and reported per run from
  `--metrics`.

## Budget, stop rule, and the balance floor

- **$15 and 30 pod-hours**, registered before the first pod. GPU class and its **real billed** rate
  recorded in `log.md`; pods deleted as soon as their work is pulled.
- **Drop order if the budget binds:** F seeds 3 and 2, then F entirely, then W's trajectory thinned
  from every 1,000 to every 2,000 steps, then W seeds 7 and 6. C, W and the two decay branches are
  the core and are dropped last.
- **Balance floor $130.** `rpbalance` was **$151.11** at 2026-09-27 17:50 UTC and the sibling run
  `lean-judge` holds a $4 budget, so my headroom is $17 and the $15 budget fits with $2 to spare. I
  check `rpbalance` before creating each pod and stop if a pod would take the account below $136.
- Projection to be corrected by measurement: ≈ 365,000 training steps and ≈ 264 held-out
  evaluations ≈ 30 GPU-hours of work, ≈ 10–12 pod-hours at 4 concurrent jobs per GPU, ≈ $6.

## What would make this run worthless

If the 6-line bin turns out to be already saturated at 6,000 steps (E1's falsifier fires) **and**
depth-3 modes never change (E7's falsifier fires), the run answers "yes, we train to saturation, the
schedule is fine" — which is a useful negative, not a worthless one. The genuine failure mode is a
within-seed comparison that is not within seed: if `--resume` does not reproduce the stable run's
data order, W-6k and W-12k stop being branches of W and inherit the ±81.7 pp cross-run floor. I test
`--resume` for exact continuation (a resumed 200 steps must match the unresumed run's loss trace to
the last decimal) before launching the arms, and record the test in `log.md`.
