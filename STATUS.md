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
- 23:29 Step 1: `nd2lean.py` + agreement table (`artifacts/r1/agreement.md`): 181,464 / 181,464 verifier-accepted proofs
  Lean-accepted; 0 / 4,000 mutation disagreements; the only semantic divergence is Lean's `¬A ≡ A → False` (handcrafted cases).
- 01:20 Step 2: Qwen3-Coder-30B in-context, 236 theorems × 3 forms × 5 draws: greedy tokens 0.201 / lean 0.547 / english 0.225;
  paired lean − tokens +0.347 [+0.300, +0.393], flat across lengths; english − tokens +0.025 [−0.012, +0.061].

## Running on pods
- r1-a100 (A100-SXM4-80GB, $1.59 / h, created 23:02): step-3 scale ladder Qwen3 0.6B → 32B on the 208 class theorems
  (0.6B done 01:18, 0 / 208), then the Coder-30B token-format extra. Judged on the VPS as each model finishes.

## Ended 2026-09-18 (session lost Claude authentication ~08:00 UTC; pods pulled and deleted 17:20 UTC)
Partial results are on this branch; large artifacts were pulled to the host but are not committed. This replication was not completed.
