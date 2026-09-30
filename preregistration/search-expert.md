# Pre-registration — search-expert (executor, 2026-09-30)

Written before any pod of this run. Brief: run brief `search-expert` (proposal 16 item 2), Dan 2026-09-29; primary
quantity changed on Dan's suggestion of 2026-09-30 02:11 UTC (log.md). `AGENT_POLICY.md` governs. Lean alone decides.

## Question

Our EI expert is the network's own independent samples. Replace it with best-first search over proof states at
matched compute (generated actions). Does the apprentice, **evaluated without search**, then prove more on the long
pool?

## Model

SN-cap12 (`lean_staten`, 3,216,384 params, 4 layers d 256, from scratch; Stage-1 on K12 = `cap-horizon`'s
`train_k12.jsonl`, cap 12, 155,000 proofs; `state_train.py --mode lean_staten --cap 12 --steps 6000 --recs 128`).
Seeds 0–3: `state-cap12`'s `stage1_SN12_s{0-3}.pt` from the bucket. Seeds 4–5: trained here with the same recipe
(`pod/sx/pair.sh`; `frontier-supply` has not run, so there are none to reuse).

## Design (what will actually run)

Every arm, from the seed's Stage-1 checkpoint, `state_ladder_ei.py`: 8 rounds, the 4,495 `rl_targets.jsonl`, T 0.8,
`max_steps` 48, `max_action` 256, batch 2,048, fine-tune 600 steps lr 3e-4 128 proofs/step, replay 20,000 K12
records. Held fixed in every arm (deviations from `state-cap12`'s ladder, the same in every arm):
- **Selection: the shortest found proof per target** (fewest lines, then tokens), weight 4 (`--select shortest
  --max_per_thm 1 --rl_weight 4`), over all rounds so far (HTPS Table 4).
- **Step filter** (`--step_filter`): an attempt / branch ends at a `have` whose term Lean is certain to reject
  (`lean_prefilter`'s checker, applied per step). It never accepts anything; every counted proof is Lean-checked from its
  literal text. CPU pilot (Stage-1 s0, 288 attempts): 0 attempts it stopped were Lean-accepted, 0 Lean rejects it missed,
  and it stops ≈ 60–70 % of attempts early. Without it, the environment does not type-check terms, so search could not
  prune dead branches; with it, arm A stops wasting actions after a certain error, which lowers the budget B is given.
- **No per-round transfer / greedy evals** (`--no_eval`): cost; they do not feed training.

Arms:
- **A, sampling expert** (6 seeds): 32 independent attempts per target per round.
- **B, best-first search expert** (6 seeds; `state_search.search_generate`). Priority Σ log p / L (α = 1; log p = model
  log-probability at T 1 of the action tokens). Expand the best node with 4 actions sampled at T 0.8, deduplicated;
  children the environment/filter rejects, or whose state this tree has already reached, are dropped; a finished child
  ends the theorem. When every node has been expanded, expanded nodes return to the frontier (sampling is stochastic).
  Budget: **per target, A's generated actions on that target in the same round and seed** (every sampled action counts,
  duplicates included). Unspent budget is not reallocated. Expansions batched across targets (2,048 rows per decode).
- **C, truncate-and-resume** (seeds 0, 1; `resume_generate`): 4 chains per target; after a failed action the next
  attempt starts from the state before it; after 4 consecutive failures from one state, or at the step cap, restart.
  Budget: per target, **A2's** actions in the same round (C runs beside A2 — an identically distributed re-draw of A).
- **A2, same-checkpoint re-draw of A** (seeds 0, 1): A with `--seed_offset 50` (sampling, mix and fine-tune seeds).
- A′ (all successes) and A+ (sampling at B's GPU-seconds) are not planned; A+ is run on 2 seeds only if B's
  GPU-seconds exceed A's by > 25 % and the budget allows.

Pods: one A40 per seed for A ∥ B (concurrent on one GPU; B waits for A's round-r budget file), one A40 per seed for
A2 ∥ C (seeds 0, 1). 8 pods.

## Read-out (final round-8 checkpoints, no search)

`lpool_reread.py`, k 256, T 0.8, seed 0, batch 2,048, `max_action` 512, `max_steps` 96, on
`transfer_long2` + calibration (the 91; file `transfer_long2_91.jsonl`) and rr600 `L_true` 13–16 (400; `rr600_13to16.jsonl`).

- **Primary Q** (Dan's suggestion, shared with frontier-supply): per seed, theorems with ≥ 1 Lean-accepted sample in
  256 on the 91 plus rr600 generator theorems at `L_true` 15–16 (200): **291 theorems**. B vs A paired per seed and per
  theorem (the two directions of discordant theorems reported).
- Secondary: exact-17 (61) and ≥ 18 (30) separately; rr600 13–14; `L*` (expected ≥ 18 in every arm, the pool's ceiling:
  it cannot separate arms); length of found proofs in lines **and** term size.
- Per round (the expert, not the apprentice): targets solved by one arm's expert in round r that the other arm's expert
  has never solved (rounds 1..r), and total new target solves.
- Compute per arm and round: generated actions, gen tokens, fine-tune steps/tokens, Lean checks, GPU-seconds (record.py
  rows; GPU type A40; two jobs share a GPU, the same way in every pair).

## Statistics

- Same-checkpoint spread: s = RMS of (A − A2)/√2 over seeds 0, 1 on Q. Paired sd of a B − A difference with no
  effect ≈ √2·s. **MDD (6 pairs, paired t, α 0.05 two-sided, 80 % power) = (2.571 + 0.920)/√6 · √2·s ≈ 2.0 s.**
  Provisional value before measurement: the reviewer's per-theorem flip rate between identical reads (6–11 of 70) plus
  EI re-draw, guessed s ≈ 12 → MDD ≈ 24 theorems of 291. The measured value replaces it; if the measured s is from
  2 pairs only, I also report the MDD with the between-seed sd of (B − A) itself.
- Per-seed values, IQM with stratified-bootstrap 95 % CI (Agarwal et al. 2021), same seeds in every arm.

## Expected results (numeric, falsifiable)

The brief's hypothesis, which this run tests:
- H1 (expert): B's expert finds ≥ 2× A's new solves per round on targets past A's cumulative frontier at equal actions.
- H2 (apprentice): B − A on Q > MDD (mean over 6 seeds).
- Falsifier: B − A ≤ 0 within the MDD, or B's expert finds no more than A's at equal actions.
- A guess, not from a source: B's found proofs are longer (the one length-specific source favours a critic).

**My own forecast, from the CPU pilot** (Stage-1 s0, 12 targets `L_true` ≥ 9, at the sampler's per-target actions of
k 32): best-first solved 5–6 / 12 vs sampling 7 / 12, spending ≈ 60 % of the budget; truncate-and-resume 7 / 12. The
policy is peaked: ≈ 50 % of best-first's sampled actions are duplicates. So I forecast **H1 fails** (ratio 0.7–1.5) and
**B − A on Q within ±MDD** (|B − A| < 24, mean). C ≈ A within the MDD. B's proofs of the same targets are no longer
than A's shortest (median line difference 0).

## Budget and stop rule

$25 / 50 pod-hours, registered with `podbudget` before the first pod. Estimate ≈ 36 pod-hours ≈ $18 at A40 $0.49/h.
Stop: all ladders and read-outs done, or 45 pod-hours reached (then finish the read-outs of completed ladders only).
A ladder that fails twice is dropped and reported. Never run `test_run_once.sh`.
