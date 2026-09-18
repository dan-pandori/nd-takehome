# STATUS — ladder-A

Brief: BRIEF_LADDER_A.md. Policy: AGENT_POLICY.md. Run id: ladder-A.

## ladder-A — RUN START 2026-09-18 01:08 UTC (executor: agent:claude, branch dan_ladder_a, worktree ~/work/ladder-A)
- 01:14 pre-registration written (`preregistration/ladder-A.md`), committed before the first pod.
- Plan: pool pod (3090) builds `data/ladder/` (strict long generator + textbook schemata, `minlen.py` bound 14); then frozen + T1 (2 seeds), then T2, T4, T6, T3, T5.
- 01:40 pools built and committed (`data/ladder/POOLS.md`): transfer 2,285 / targets 2,295 theorems with `L_true` 7–14 (generator 63,342 + textbook 3,797 labelled, bound 14, 4 unresolved). Driver `ladder_ei.py` smoke-tested on la-2. Launching frozen + T1 (la-1 seed 0, la-2 seed 1) and T2 (la-3) next.
- 01:50 round 1 killed (OOM at batch 1024; 16/2,295 targets accepted). Target pool amended to 4,495 (prereg §Amendment); all queues relaunched at batch 512.
- 04:42 all arms finished on la-1…la-5 except T3 s0 (crashed in round 6, `relabel` IndexError). ~08:00 session ended (auth expiry); 17:20 pods deleted by Dan after pulling files.
- 17:50 RESUMED. Audit: 15/16 arm directories complete; stale pod copies of `pools_summary.json` / `pools.log` restored from git. Plan: one 3090 to resume T3 s0 rounds 6–8 from its round-5 checkpoint, then `ladder.md`, figures, `run_ladder_A.md`, upload.
- 18:22 T3 s0 rounds 6–8 resumed and finished on la-6; la-6 deleted. No ladder-A pods remain.
- Result: transfer `L*` = 10 for every rung T1–T6 on both seeds, frozen control 7 (+3 everywhere; wall at `L_true` 11). Only T6 beats T1 on both seeds in theorems solved at `L_true` ≥ 9. See `run_ladder_A.md`, `ladder.md`, `numbers.md` §ladder-A, `figures/ladder_*.png`.
- Phase B trigger met → question in `QUESTIONS.md` (default: not started). Cost ≈ $39 of $50 (≈ $32 idle pods during the outage).
- Bucket: `hf://buckets/dan-pandori/nd-rl/ladder-A/{data/ladder,artifacts/ladder,ckpts/ladder}` (64 / 837 / 112 files).
- LADDER-A DONE 2026-09-18T18:27Z
