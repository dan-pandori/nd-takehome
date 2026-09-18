# Pre-registration: round3-run1 — pool composition or pattern class?

Written 2026-09-18 05:09 UTC, before any pod of this run was created (gate 0). Executor:
agent:claude. Branch `dan_round3-run1`. Governing brief: `BRIEF_pool-composition.md` (the
round-3 proposal, §1); policy: `AGENT_POLICY.md`. Edits to the numbers below get a dated
reason in §Amendments at the end of this file.

## Question

Zero-rate reductio draws never ignite; three of five zero-rate depth-3 draws did. The two
pools differed in one thing besides the pattern: the depth-3 pool rewarded depth-≤ 2 proofs of
673 of its 1,000 targets (neighbours of the pattern), while every reductio target needed `DN`
and the zero-rate reductio arms never took a training step. Is the asymmetry in clause (3) of
the rule of thumb ("ignition is predictable from the pre-RL base rate for rule sequences and
not for structural patterns") a property of the pattern class, or of whether the pool rewards
neighbours of the pattern?

## Design I will run

**Patterns.** depth-3 (`patterns.depth3`, box depth ≥ 3 in the dependency-pruned proof) and
reductio (`patterns.reductio`, strict `NEGI(~G) … DN` shape).

**Pools** (all in `data/r3_1/`, every record carries `stratum` ∈ {required, neighbour} and the
oracle fields; every pool class-disjoint by renaming key from `train_depth3_f0_a1.jsonl`,
`train_reductio_f0.jsonl`, both held-out sets and `targets/validation_36.jsonl`):

- `depth3_req` — depth-3 required@8 targets: `minlen.py --max_depth 2 --bound 8` fails with no
  timeout and the unrestricted minimum is ≤ 8 lines. Start from the 142 such targets in
  `data/p2/targets_depth3_maxdepth2.jsonl` ∩ `targets_depth3.jsonl`, add generator candidates
  (depth-3 generating proof, unrestricted min length 7–8) labelled the same way; target 300
  targets + 100 transfer; if fewer than 300 are found the pool is what was found (≥ 250 is the
  pre-registered minimum, E1). For every target the bound-10 depth-≤ 2 alternative
  (`--max_depth 2 --bound 10`) is recorded.
- `depth3_nb` — 300 depth-3-optional neighbours: targets of the same generator family with a
  depth-≤ 2 proof at 7–8 lines (from the 673 in `targets_depth3_maxdepth2.jsonl`), disjoint
  from `depth3_req`.
- `reductio_req` — `data/p2/targets_reductio_req.jsonl` (300, reviewer-certified: every
  target intuitionistically unprovable) and `transfer_reductio_req.jsonl` as transfer.
- `reductio_nb` — 300 reductio neighbours: conclusion `( ~ ( ~ X ) )`, `minlen.py --forbid DN
  --bound 10` finds a proof (so `DN` is not required), `intuit.py` says provable, unrestricted
  min length 7–8. Source: generator long pool (`make_coverage_sets.py gen --long`) filtered on
  the conclusion.

Ten required@8 depth-3 targets and ten neighbours of each pattern hand-checked and logged
before any arm runs.

**Stage-1 draws.** `train.py --mode abs --steps 6000 --bs 128 --cap 6` on
`train_depth3_f0_a1.jsonl` seeds 20–27 and on `train_reductio_f0.jsonl` seeds 20–27 (16 new
models). The existing reductio f = 0 s1 and s2 checkpoints (ignition study, both 0 hits in
3·10⁶) may be added as two more zero-rate reductio draws (disclosed if used).

**Pre-RL sample.** `coverage.py --k 2000 --temperature 0.8 --batch 2000` over all 300
required targets of each pattern per draw (600k samples per draw), per-proof hit counts kept.
A draw is *zero-rate* if it has 0 pattern hits over all required targets; n₀ = number of
zero-rate draws per pattern. If n₀ < 3 for a pattern, train 4 more seeds (28–31) and disclose.

**Arms** (`expert_iter.py --rounds 8 --k 32 --temperature 0.8`, retain 20k, seed = model seed),
per draw and pattern:

1. `req` — required pool only (300 targets).
2. `mix` — required + neighbours (600 targets); the two strata reported separately.
3. `drift` — neighbours only, with the new opt-in `--exclude_pattern <depth3|reductio>` flag
   in `expert_iter.py` (any found proof whose dependency-pruned form has the pattern is
   dropped from the training mix; count logged). After rounds 2, 4, 6, 8, `coverage.py --k
   1000` on the 300 required targets from the saved round checkpoint (300k samples per
   checkpoint).

All three arms for every zero-rate draw; `req` and `mix` for non-zero draws; `drift` for at
most two non-zero draws per pattern as a reference. Frozen control = the pre-RL sample
restricted to the first 256 attempts per target, reported next to each `req` and `mix` arm.

**Counts.** Acquisition = required targets with a verified proof whose pruned form has the
pattern, cumulative over rounds, from `found_<r>.jsonl` after start-index normalisation, round
= minimum over raw records of a normalised proof; `nd_verify` re-run on every counted pattern
proof. Ignition = ≥ 20 (depth-3) / ≥ 12 (reductio) required targets, cumulative.
Solved-without-pattern counted per stratum. Held-out greedy per round from the arm's
`round_<r>.json`.

## Pre-registered expectations

Expected n₀ ≈ 3–5 of 8 for depth-3 and ≈ 4–5 of 8 for reductio.

- **E1 pools.** ≥ 250 depth-3 required@8 targets (0 timeouts); ≥ 90 % of them have a 9-line
  depth-≤ 2 alternative and ≤ 5 % have none at bound 10. ≥ 250 reductio neighbours. 0 oracle
  inconsistencies (a required target solved without the pattern by any model, or a neighbour
  whose `--forbid DN` proof fails `nd_verify`). Every draw solves ≥ 40 % of the neighbour
  stratum of its `mix` pool by round 8.
- **E2 depth-3, `req`.** Zero-rate draws ignite in **0 of n₀** and solve ≤ 5 required targets
  in 8 rounds. Non-zero draws ignite in ≥ 80 % by round 5.
- **E3 depth-3, `mix`.** Zero-rate draws ignite on the required stratum in ≥ 40 % of n₀, and
  only after ≥ 1 round with neighbour-only successes.
- **E4 reductio, `mix`.** Proposer's expectation: **1–2 of n₀** zero-rate draws ignite (≥ 12
  required targets with a strict reductio proof) by round 8. The standing rule predicts 0.
  Non-zero draws ignite on both pools, as in run 5.
- **E5 `drift`.** Depth-3: the required-pool rate rises from 0 to ≥ 10⁻⁵ (≥ 3 hits in 300k) by
  round 8 in ≥ 2 of n₀ zero-rate arms. Reductio: ≤ 1 hit in 300k at every checkpoint in every
  zero-rate arm.
- **E6 route choice.** Required@8 depth-3 targets solved without a depth-3 proof ≤ 5 % of
  solved required targets in every arm. Reductio required targets solved without the strict
  pattern: 0.

## What would falsify the standing rule

- Clause (3) dies if E2 holds: without neighbours, structural ignition is as base-rate-gated
  as reductio.
- Clause (2) ("amplifies what the base model already generalised to, or nothing") dies if ≥ 2
  zero-rate reductio draws ignite on `mix`, or if any zero-rate reductio `drift` arm reaches
  ≥ 10⁻⁵.
- The rule survives unchanged only if zero-rate depth-3 draws ignite on `req` at the `mix`
  rate and no zero-rate reductio draw moves in either condition.

## Budget and stop rule

Three RTX 3090 pods at $0.50/h (A40 if 3090s are out of stock). Estimate ≈ 26 pod-hours ≈ $13;
per-run ceiling $50. Stop when every arm has 8 rounds, or at $40 spent, whichever first; at
$40 the `req` and `mix` arms of zero-rate draws are finished before anything else; if pod
time is short, `drift` for non-zero draws is dropped first, then `mix` for non-zero draws.
Never co-schedule a coverage run with another job on a 24 GB card. Kill switch re-armed at
≤ 30 h. Pods deleted when their work is pulled.

## Deliverables

`run1.md` (≤ 400 words + figures), `numbers.md` §Round 3 run 1, `artifacts/r3_1/summary.json`,
pools in `data/r3_1/`, `STATUS.md` ending `RUN3-1 DONE <UTC>`, bucket
`hf://buckets/dan-pandori/nd-rl/round3-run1/{artifacts,ckpts,data}` with all 16 Stage-1
checkpoints, `~/runs/round3-run1/executor.done`.

## Amendments

- **2026-09-18 05:50 UTC (before any `mix` or `drift` arm ran; `req` arms had started at 05:44).** Reductio-neighbour
  definition tightened: besides "conclusion `( ~ ( ~ X ) )`, `--forbid DN` finds a ≤ 10-line proof, `intuit.py` provable,
  unrestricted min 7–8", the shortest no-DN proof must **close with NEGI of an assumed `( ~ X )`** (the reductio shape
  minus its DN step). Reason: the hand-check of the first build (`reductio_nb` v1, 159 → 300 of 1,264 candidates) showed
  that about 40 % of the shortest no-DN proofs obtain `( ~ ( ~ X ) )` by explosion (`BOTE`) from contradictory premises,
  which rewards nothing adjacent to reductio. 759 of the 1,264 candidates satisfy the tightened rule; the pool is 300 of
  them (seed 0). No expectation number changed.
