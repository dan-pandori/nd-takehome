# review_cd — reviewer's recount kit for run `capability-defs`

Written by the reviewer (agent:claude, 2026-10-05), independently of `capability_defs/analysis/`.

**Running it.**
- Paths assume a copy of the run repository at `~/review/capability-defs`; set `RV_ROOT` to use another.
- The other runs' pulled reads are read from `~/work/<run>/artifacts/...` and from rl-continue's
  `~/review/rc_data/s<S>/found_transfer_16.jsonl`.
- Pure Python + numpy / scipy. Lean 4.34.1 core is needed for the re-check.
- Every script prints to stdout; the `*.log` beside each one is its saved output.

| script | recounts |
|---|---|
| `rv_load.py` | loader for the original per-theorem read files (trajectory, trajectory-cap6, rl-continue(-cap6), mcts-a copies, rl-from-ckpt, J-jobs) |
| `rv_sets.py` | H, J2, calibration pool; equal-k created sets (Q1), reliability (Q9), J5 expectations |
| `rv_j2.py` | J2 stage A / A′ / B / doubled caps / calibration; cut-off per stratum (Q2, A′, B) |
| `rv_F.py` | rebuilds F(t) from the reads and compares it with the J1 targets; J2 proofs missing from stage 2 |
| `rv_bracket.py` | budgets from trajectory's compute rows; known-proof sums; Q3 – Q7, Q15, J1 expectations |
| `rv_j3.py` | J3 guided vs plain; Q13 |
| `rv_lem.py` | J4, J6, J6b, Q10, Q11 (lem39 / lem40, the six holdout250 A ∨ ¬A) |
| `rv_irt.py`, `rv_irt_fit.py` | own binomial 2PL (MAP), projections, Q8, J7 (i) |
| `rv_q12.py` | pretraining-compute equivalent, set level and per theorem |
| `rv_extrap.py`, `sc/` | Q16 as pre-registered (support-curves counts, hypergeometric thinning) and the executor's J2 adaptation |
| `rv_j8.py`, `rv_j8_sound.py` | J8 shares by start; soundness of J8's 2.1 M targets |
| `rv_j9j10.py` | J9 certification totals, J10 long pool |
| `rv_defs.py` | the 12 final created-set definitions, redraw / seed floors, agreement matrix (Q14) |
| `rv_sens.py` | threshold sensitivity of cm / tfmax / brk_ne |
| `rv_trunc.py` | cut-off (action truncated / step cap) per job |
| `rv_splits.py` | renaming-class disjointness of every training file against every evaluation pool |
| `rv_recheck.py`, `rlean.py` | Lean re-check of 3,710 counted proofs + controls; term sizes |
| `g4ip.py` | own G4ip intuitionistic prover (schema key-step rule; lem40's intuitionistic instance) |
| `lit/` | literature sub-audit (L1, L2), written by a reviewer sub-agent with its own scripts |
