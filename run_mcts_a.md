# run mcts-a: PUCT with a learned value at test time, against sampling (proposal 22, Phases 0 + A)

**Models:** `trajectory` cap-12 seeds s0–s2: ALiBiGPT 9.56M, `lean_staten`, from scratch on K12. *pend* is the end of
pretraining; *r8* is after 8 T1 EI rounds. The policy is frozen. **Checker:** Lean only.

**Built** (`mcts.py`, `value_head.py`, CPU tests pass):
- PUCT over proof states (AlphaProof's c(s), state-deduplicated samples, progressive sampling), many trees per GPU
  batch: GPU util 72 %, against sampling's 63 %.
- A value head on the frozen trunk (solvable logit plus γ-discounted steps-to-go), trained on rollouts on rl_targets
  and K12. Held-out AUC 0.74–0.82, steps-to-go Spearman 0.69–0.83.

**Test:** each search job gets the matching k 256 sampling job's wall clock (same A40).

| solved (s0 / s1 / s2) | sample | PUCT prior | PUCT + value |
|---|---|---|---|
| **group C, r8 (gate)** | 4 / 2 / 4 | 2 / 1 / 3 | 2 / 2 / 3 |
| group C, pend | 0 / 0 / 0 | 0 / 1 / 0 | 0 / 1 / 1 |
| textbook72, r8 / pend | 49 50 55 / 32 32 36 | 44 44 54 / 29 34 34 | 47 49 57 / 35 37 37 |
| rr600 L13–16 (100), r8 / pend | 96 93 92 / 59 65 60 | 96 94 88 / 76 69 66 | 96 96 90 / 78 75 74 |
| holdout250, pend | 199 207 204 | 215 212 212 | 206 216 203 |

**MCTS-A GATE: FAIL.**
- Group C at r8: PUCT + value solves 2 / 2 / 3, sampling 4 / 2 / 4. Predicted: 4–8, about a
  45 % chance to pass. The falsifier fires.
- An exploratory run at 10× the budget stays level: 9 / 5 / 7 for PUCT + value against 10 / 7 / 5 for sampling at
  k 2,560.

**Where search did help:**
- At pend, on rr600 L13–16, PUCT + value beats sampling by **+14.3** (95 % CI +9.7 to +19.3), still climbing
  (`figures/mcts_a.png`).
- That is about 45 % of what 8 EI rounds add on this pool.
- At r8, PUCT + value is within ±2 of sampling on every pool.

**My reading:**
- Search pays where the frozen policy is unreliable over many steps, which EI already fixes.
- On group C the needed steps are too rare among the policy's samples. A value trained on that policy's rollouts
  cannot point to them.
- `mcts-b` should not run as specified.

**Caveats:**
- Two bugs were fixed before any evaluation read-out, and the tuning grid was widened (addendum 1); see `log.md`.
- Sampling truncates 0.22 % of attempts (trajectory's protocol).
- Search proofs are first-found, so they are longer.
- Compute: read-outs 6.8 GPU-h (equal per arm), tuning 2.2, value data 2.5. 17.7 pod-h, $8.66.
