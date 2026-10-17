# peer-rl-review — the other mentees' RL work against ours (2026-10-17; UNREVIEWED)

Report: `peer_rl_review/REPORT.md`. Numbers: `numbers.md` § peer-rl-review. No pod, no sampling, no training.

**Result.** Leon's proof-state system leads ours by a wide margin, on a protocol both sides share. That protocol is our
stored samples scored with his estimator, on the same files, at the same T, step caps and Lean judge. The models are 9.6M
proof-state models; Lean alone judges.

| set, pass@1 | his recipe | ours |
|---|---|---|
| Charles149 | 70.5 | 31.8 (r8) |
| textbook72 | 74.0 | 42.9 (r16) |

His K12 base and ours agree: 17.2 vs 15.2. Most of the gap traces to Stage-1 on search-found proofs: +14 before RL,
and his search-proof RL arms reach 54–75 % where K12-based arms reach 25–43 %. GRPO over EI (+5) and thinking are
smaller.

Robbie, Dmitry and Charles report no RL gain over ours.

**Priors:**
- P1 supported.
- P2 falsified: Leon's GRPO − EI holds at pass@5.
- P3 not testable: no published checkpoints.
- P4 mixed.
- P5 supported: our models share the premise wall.

**Next.** Search-proof Stage-1 on our ladder, tested at 5 seeds.
