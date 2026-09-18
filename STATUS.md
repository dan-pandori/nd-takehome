# STATUS — round3-run1

Brief: BRIEF_pool-composition.md. Policy: AGENT_POLICY.md. Run id: round3-run1.

## round3-run1 — pool composition or pattern class? (executor)

- 2026-09-18 05:09 UTC: started. Pre-registration `preregistration/round3-run1.md` committed 05:09:48 UTC (gate 0 passes; no pod yet). Plan: pools → 16 Stage-1 draws → pre-RL samples → req / mix / drift arms.
- 2026-09-18 05:55 UTC: pools built and committed (`data/r3_1/`: depth-3 300 required@8 + 100 transfer + 300 neighbours; reductio 300 required + 150 transfer + 300 NEGI-closing neighbours; prereg amendment 05:50 on the neighbour definition). 16 Stage-1 draws training on r31a/r31b (A40); pre-RL samples and `req` / `mix` arms queued on r31a–r31d, guarded on the checkpoints. Spend so far ≈ $1.
