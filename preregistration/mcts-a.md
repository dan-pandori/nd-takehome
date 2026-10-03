# Pre-registration — mcts-a (proposal 22, Phases 0 + A)

Written 2026-10-02 ~23:50 UTC, before any pod. Executor: agent:claude. Branch `dan_mcts-a`. Budget **$15 / 30 pod-hours**
(registered in `podbudget`). Policy: `AGENT_POLICY.md` (Lean alone decides; compute rows per arm).

## Question

At equal GPU-seconds per theorem, does PUCT search over proof states with a learned value solve theorems that plain
sampling from the same frozen policy does not? Above all, does it solve `trajectory`'s **group C**: theorems that neither
the end-of-pretraining nor the r8 checkpoint solves at k 256. Group C theorems have two or more hard steps. A tree can
resample at a hard state without redoing the prefix, so its cost should be closer to the *sum* of the hard steps' costs
than to their product, provided the value can tell that a partial proof is on track.

## Models (every number names one of these)

`trajectory`'s cap-12 seeds s0–s2. Each is Robbie's recipe, `best_model.ALiBiGPT` 6 × 384, **9,560,832 parameters**,
`lean_staten`, trained from scratch on K12 (155,000 generator proofs, cap 12):
- **pend** = `stage1_best12_s{S}_b1200.pt`, the end of pretraining;
- **r8** = `la_T1_best12_s{S}_r8.pt`, the T1 ladder after 8 rounds of EI on `rl_targets`.

Both come from `hf://buckets/dan-pandori/nd-rl/trajectory/ckpts/tj/`. The policy is frozen throughout; nothing in this run
trains it.

## Build (Phase 0): what was built and CPU-tested before this commit

- `mcts.py` is the PUCT search: one tree per theorem, many trees per GPU batch.
  - Selection is `Q + c(s)·P·√N(s)/(1+N(s,a))` with c(s) = c_init + log((N(s)+c_base+1)/c_base), using c_init 1.25 and
    c_base 19,652 (AlphaZero's values; AlphaProof's are unpublished).
  - The prior is π^{1/τ} with τ = 1. A child's π is the policy probability summed over the distinct sampled actions
    that reach its state.
  - Each expansion samples K actions. They are deduplicated by resulting state (the environment assigns names, so
    actions differing only in names merge).
  - **Progressive sampling:** a node gets K more samples when n(s) ≤ C·N(s)^α (C 1, α 0.5), up to 64 samples per node.
  - Virtual loss lets one tree send up to 8 leaves per round. Values back up with discount γ.
  - Invalid actions are discarded. The environment rejects the syntax, and a step whose term Lean is certain to reject
    is also discarded (`step_reject`, the per-step form of `lean_prefilter`'s sound check; it never rejects a correct
    step on 400 reference steps).
  - **Lean decides every finished proof** (`lean_gate.gate` on the literal text). A rejected proof is a dead leaf.
- `value_head.py` is an MLP on the **frozen** trunk. Its input is ln_f of the `<act>` token concatenated with ln_f of
  the mean hidden state over the state.
  - Outputs: a solvable logit (soft BCE on the fraction of the policy's rollouts through the state that Lean accepted;
    states on failed attempts count as unsolved) and steps-to-go (Huber, on states with a success).
  - Search value: v = σ(s)·γ^{d}, γ 0.95 (AlphaProof: Q = γ^{steps-to-go}).
  - Without the value, v = 0 at every non-terminal leaf.
- `mcts_value_data.py`: rollouts of the frozen checkpoint, k 16 at T 1.0, max 96 steps.
  - Theorems: all 4,495 `rl_targets` (`data/ladder/rl_targets.jsonl`) plus 1,500 K12 generator theorems.
  - Never textbook72, holdout250 or a transfer pool. The pools are disjoint from `rl_targets` under atom renaming
    (0/72, 0/250, 0/600, 0/21).
  - A tenth of the theorems (by name hash) is held out for calibration.
- `mcts_eval.py` / `pod/mcts/*.sh` hold the read-out pipeline. `tests/test_mcts.py` holds the CPU tests (all pass):
  clone, dedup, step check, scripted-policy search, a dead-end tree, widening, and the value-head round trip.

## Design (Phase A)

**Arms**, all on the same checkpoint, run one job at a time on the same GPU:
1. **sample.** `trajectory`'s k 256 protocol, re-run here: `state_eval.py`, T 0.8, max_action 512, max_steps 96,
   batch 2,048, sample seed **2** (a fresh draw; group C was defined from seed 0). A theorem counts as solved if at
   least one of its 256 attempts is Lean-accepted.
2. **prior.** PUCT with the prior and progressive sampling only (proposal 20's E1).
3. **value.** PUCT with the value head trained for this checkpoint.

**Matched compute.** For each (seed, checkpoint, pool), the sampling read's wall clock (sampling plus Lean) is that
job's GPU-seconds, and it is the budget for each search job on the same pool, GPU and pod. Search stops when the wall
clock reaches the budget, or earlier if every tree is solved or dead. Per-theorem GPU-seconds are therefore equal on
average across the pool. Search reallocates within the pool: a solved tree stops and frees its share. Both arms
include Lean and all CPU time in their wall clock.

**Pools**, run for each of 3 seeds × {pend, r8}:
- **group C** of that seed (36 / 35 / 28 theorems), the headline. It is run as its own pool so that its budget is
  sampling's budget on exactly those theorems.
- textbook72 (72) and holdout250 (250).
- `rr600` at L_true 13–16: a fixed random **100** of its 400 (`data/mcts/rrQ100.jsonl`, rng 20261002), sub-sampled for
  budget.
- `transfer_long2` (21).

**Tuning (pre-registered, before any read-out).** Run on s0 pend only, on 184 held-out `rl_targets` theorems with
L_true ≥ 9 (`data/mcts/tune200.jsonl`), never an evaluation pool. Four configs, (K, temp) ∈ {8, 16} × {1.0, 1.5}, are
run for each search arm at the matched sampling budget. Each arm gets its own winner (most solved; ties go to the
earlier config). Every other constant stays at the values above.

**Settings recorded:** batch, `max_action` (sampling 512, search 256) and the truncation fraction, peak memory, GPU
type and its billed rate, and GPU utilisation (nvidia-smi, 1 s).

## Gate (decides `mcts-b`)

Let Δ_s be the number of group-C theorems PUCT-with-value solves minus the number the matched sampling read (seed 2)
solves, at **r8**, for seed s.

**`MCTS-A GATE: PASS`** iff Δ_s ≥ 3 on at least 2 of 3 seeds, and on each of those seeds Δ_s also exceeds the
sampling arm's own re-draw spread on group C. The spread is |seed-2 count − `trajectory`'s seed-1 count|, where
seed-1 is 3 / 1 / 1. Otherwise **FAIL**. The verdict goes into `STATUS.md` with the numbers.

**Noise.** This is a paired, within-checkpoint comparison, so training-seed noise cancels and the noise is the sampling
re-draw. The search is also a draw.
- Sampling solves about 1–3 of group C at r8 (`trajectory` seed 1: 3 / 1 / 1). Treated as Poisson, a count has sd
  ≈ 1.4 and a per-seed difference has sd ≈ 2–2.5.
- MDD at 80 % power, two-sided α 0.05: ≈ **6–7 theorems per seed**, ≈ **4** on the 3-seed mean. The per-seed gate
  threshold of 3 is below the per-seed MDD, so the gate is a decision rule and not a significance test.
- Under the null (sd 2.4), P(Δ_s ≥ 3) ≈ 0.11 and P(≥ 2 of 3 seeds) ≈ 0.03. At a true Δ of +5 its power is ≈ 0.9.
- I report per-seed values, the mean, and IQM with a stratified-bootstrap 95 % interval over seeds × theorems.
  With n = 3 seeds, a seed-level interval is shown but is not called a finding.

## Expected results (numeric; committed before any pod)

Group C (36 / 35 / 28 theorems), solved at matched GPU-seconds:

| | sample (seed 2) | prior | value |
|---|---|---|---|
| r8, per seed | 1–3 | 2–5 | **4–8** (point guess 5) |
| pend, per seed | 0–1 | 0–2 | 0–3 |

- **Gate:** about 45 % PASS. My central expectation is a +2 to +4 gain from the value at r8, near the threshold.
- **prior vs sample:** within ±2 on group C. Dedup and prefix sharing help, but without a value there is no way to
  concentrate on promising partial proofs.
- **textbook72 at r8** (sample about 48–54): the search arms within ±4 of sampling. **At pend** (about 32–38): value
  +0 to +6.
- **holdout250 at r8** (about 237–240, near the ceiling): every arm within ±3.
- **rrQ100 and long2:** at r8 near the ceiling, with every arm within ±3. At pend: value ≥ sampling, gain 0–10 on
  rrQ100.
- **Value calibration** on held-out rl_targets / K12 states: AUC (solvable vs never) **0.80–0.92**, Brier below the
  constant predictor's, and steps-to-go Spearman **0.6–0.85** on states with a success.
- **Search statistics:** found proofs' hardest step (lowest prior) at depth ≥ 2 in most group-C solves. Prior rank of
  the hard step 2–8 among siblings.
- **GPU utilisation:** search 40–75 % against sampling 70–95 %. The search's Python environment loop is CPU-bound.

**Falsifier** (proposal 22): at matched GPU time, PUCT with the value solves no more of group C than sampling does
(Δ ≤ 0 on ≥ 2 seeds).

## Compute and stop rule

- **Estimate:**
  - value data: 6 checkpoints × about 30 min;
  - tuning: about 1.2 h;
  - read-outs: 6 × 3 arms × about 25 min.
  - Total about 12–14 GPU-hours on 3 pods (one per seed, A40, or RTX 3090 / A6000 if A40 is out), about $6–8.
- **Stop rules:**
  - At 80 % of the $15 budget, drop the pend `rrQ100` / `long2` / `h250` read-outs, in that order.
  - Never go below the $100 balance floor.
  - If the GPU smoke test (≤ 20 min) shows search throughput under 25 % of sampling's actions/s, fix batching before
    any read-out.

**Compute rows per arm**, written with `record.py` (metric names `gpu_seconds`, `gen_tokens`, `lean_checks`, plus
attempts/actions): GPU-s, generated tokens, sampled actions and expansions, Lean checks; no training steps (frozen
policy), except the value head's own training steps, which are recorded separately.

**Deviations** from this file will be written in `log.md` with the reason.

## Addendum 1 (2026-10-03 00:12 UTC, before any evaluation read-out)

The first tuning result (s0 pend, tune200, budget 466 s) is K 8 / T 1.0 PUCT-prior **105 / 184**, against sampling's
**140 / 184**. 57 % of the search's sampled actions duplicate an action already sampled at the same node. Each expansion
decodes K actions to go one step deeper. At a confident step that costs K× sampling for one distinct child, and
progressive sampling already adds breadth where visits accumulate. The pre-registered grid only has K ≥ 8.

**Change:** the tuning grid gains four configs, K ∈ {2, 4} × T ∈ {0.8, 1.0}, on the same set, checkpoint, pod and
budget. The four pre-registered configs are all still run. Each arm's winner is chosen over all eight by the same rule
(most solved; ties go to the earlier config in the order t0–t7). Nothing else changes: no evaluation pool has been
read, and the gate, the pools and the expectations above stand. The s0 r8 value head is trained on another pod (mc-2)
so that mc-0's extra tuning time does not delay its read-outs.
