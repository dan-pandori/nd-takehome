# STATUS — ladder-A

Brief: BRIEF_LADDER_A.md. Policy: AGENT_POLICY.md. Run id: ladder-A.

## ladder-A — RUN START 2026-09-18 01:08 UTC (executor: agent:claude, branch dan_ladder_a, worktree ~/work/ladder-A)
- 01:14 pre-registration written (`preregistration/ladder-A.md`), committed before the first pod.
- Plan: pool pod (3090) builds `data/ladder/` (strict long generator + textbook schemata, `minlen.py` bound 14); then frozen + T1 (2 seeds), then T2, T4, T6, T3, T5.
- 01:40 pools built and committed (`data/ladder/POOLS.md`): transfer 2,285 / targets 2,295 theorems with `L_true` 7–14 (generator 63,342 + textbook 3,797 labelled, bound 14, 4 unresolved). Driver `ladder_ei.py` smoke-tested on la-2. Launching frozen + T1 (la-1 seed 0, la-2 seed 1) and T2 (la-3) next.
