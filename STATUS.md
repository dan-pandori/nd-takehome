# STATUS — round3-run1

Brief: BRIEF_pool-composition.md. Policy: AGENT_POLICY.md. Run id: round3-run1.

## round3-run1 — pool composition or pattern class? (executor)

- 2026-09-18 05:09 UTC: started. Pre-registration `preregistration/round3-run1.md` committed 05:09:48 UTC (gate 0 passes; no pod yet). Plan: pools → 16 Stage-1 draws → pre-RL samples → req / mix / drift arms.
- 2026-09-18 05:55 UTC: pools built and committed (`data/r3_1/`: depth-3 300 required@8 + 100 transfer + 300 neighbours; reductio 300 required + 150 transfer + 300 NEGI-closing neighbours; prereg amendment 05:50 on the neighbour definition). 16 Stage-1 draws training on r31a/r31b (A40); pre-RL samples and `req` / `mix` arms queued on r31a–r31d, guarded on the checkpoints. Spend so far ≈ $1.
- 2026-09-18 08:15 UTC: all 16 pre-RL samples, all 16 `req`, 16 `mix` and 16 `drift` arms done; n₀ = 6 (depth-3) / 5 (reductio). Remaining: drift-checkpoint sampling (34 of 64 coverage jobs) on r31a–r31d, ≈ 2 h. Spend so far ≈ $6 of the $50 ceiling. Headline so far: depth-3 zero-rate draws ignite 0 / 6 on `req`, 3 / 6 on `mix`; reductio zero-rate draws 0 / 5 on `req`, 1 / 5 on `mix` (s21, 52 / 300), and that draw's neighbours-only drift arm reaches 151 / 300k on the required pool at round 6 with every pattern proof excluded from training.
