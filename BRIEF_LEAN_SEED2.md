# Run brief: lean-seed2 — second Stage-1 seed for `lean_seq` on the ladder rung, after the BOTE fix

Run id `lean-seed2`. Repository `~/work/lean-seed2` (branch `dan_lean_seed2`, worktree from
`origin/dan_lean_format`, which has the proposal-8 code). `AGENT_POLICY.md` governs. Budget $6–10;
hard stop 20 h. Dan authorised this run as an exception to the pause.

1. **Fix `nd2lean.py`'s `BOTE` rendering first** (the executor's `QUESTIONS.md` default): render
   ex-falso explicitly (e.g. `absurd`/`False.elim` on a `False` hypothesis) so Lean cannot
   resolve it to `Not.elim`. Re-run the checker agreement on the 460 known "Lean yes,
   `nd_verify` no" texts from `lean-format` and on a 20k-proof sample of the pools; report the
   counts; commit before any training.
2. Train one more `lean_seq` Stage-1 model (seed 2; same set, schedule and size as proposal 8),
   report held-out greedy, then run ladder rung T1 and its frozen control on the ladder transfer
   pool with the identical protocol. Pre-register in `preregistration/lean-seed2.md` (commit
   before the first pod): transfer `L*` for this seed (proposal 8 got 11 on one model), theorems
   at `L_true` ≥ 11, held-out accuracy.
3. Report `L*` with both seeds side by side; state plainly whether "`L*` = 11" now rests on two
   Stage-1 models or one.

Deliverables: `run_lean_seed2.md` (≤ 300 words + one figure), `numbers.md`/`log.md` sections,
bucket upload to `hf://buckets/dan-pandori/nd-rl/lean-seed2/`, `STATUS.md` ending
`LEAN-SEED2 DONE <UTC>`, `touch ~/runs/lean-seed2/executor.done`. Pods deleted first.
