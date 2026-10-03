# mcts-b — not run: `mcts-a`'s gate failed

**Why.** The brief makes Phase B conditional on `mcts-a`'s gate. `MCTS-A GATE: FAIL` (`origin/dan_mcts-a` `STATUS.md`,
02:52 UTC 2026-10-03), recomputed and let stand by the reviewer (nd-rl `experiment-summaries/2026-10-02-mcts-a-…`).
On group C at r8 (`trajectory` best-cap12 s0–s2, 9.56 M params, `lean_staten`, from scratch on K12; Lean alone), PUCT +
value vs k 256 sampling at matched GPU-seconds: 2 vs 4, 2 vs 2, 3 vs 4 (Δ −2 / 0 / −1); the falsifier fired. No pod was
created; $0 spent.

**What `mcts-a` suggests instead.**
1. Score the r8 value heads on group-C states directly (AUC on/off-track partial proofs from the 10× sampling read):
   ≈ 0.5 means the value cannot see rare steps; clearly higher points at search budget.
2. Search helped at end of pretraining on the long pool (rrQ100 +14.3), the gap EI already closes; a search expert
   there would need compute-matched comparison against EI's early rounds.
3. Any re-gate needs several draws per arm or a ≥ 150-theorem hard pool.
