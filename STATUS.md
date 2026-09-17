# STATUS — run1-lean

Brief: BRIEF_*.md. Policy: AGENT_POLICY.md. Run id: run1-lean.

## run1-lean — ND → Lean 4; in-context surface forms; novelty by scale

Started 2026-09-17 22:50 UTC (executor). Pre-registration `preregistration/run1-lean.md` committed
22:57 UTC (cd817b9), no pod created before it. Hard stop 2026-09-19 04:50 UTC; killswitch 06:00.

## Plan
1. `nd2lean.py` + agreement table on all pools (VPS only, Lean 4.34.0 via elan) → commit.
2. One A100-80GB pod `r1-a100`: vLLM + Qwen3-Coder-30B-A3B-Instruct, 236 theorems × 3 forms × 5 draws,
   greedy + 8 samples; Lean / nd_verify judging.
3. Same pod: Qwen3 0.6B…32B at k = 16 in Lean on the three RL-found classes (60 / 88 / 60 theorems).

## Done
- 22:57 pre-registration committed and pushed.

## Running on pods
(none yet)
