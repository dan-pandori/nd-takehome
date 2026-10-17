# peer-rl-review — the other mentees' RL work against ours (2026-10-17; UNREVIEWED)

Report: `peer_rl_review/REPORT.md`. Numbers: `numbers.md` § peer-rl-review. No pod, no sampling, no training.

**Result.** Leon's proof-state system leads ours by a wide margin on a shared protocol: our stored samples scored with
his estimator, files, T, step caps and Lean judge (9.6M proof-state models).

| set, pass@1 | his recipe | ours |
|---|---|---|
| Charles149 | 70.5 | 31.8 (r8) |
| textbook72 | 74.0 | 42.9 (r16) |

His K12 base and ours agree: 17.2 vs 15.2. Most of the gap traces to Stage-1 on search-found proofs: +14 before RL,
and about +21 after the same EI on the same pool (his single-seed control). His dev58-designed pool (up to +9),
thinking and GRPO over EI (+5) are smaller.

Robbie, Dmitry and Charles report no RL gain over ours.

**Priors:**
- P1 supported.
- P2 mixed: Leon's GRPO − EI holds at pass@5, and at k 64 only on textbook72.
- P3 not testable: no published checkpoints.
- P4 mixed.
- P5 supported: our models share the premise wall.

**Next.** Search-proof Stage-1 on our ladder, tested at 5 seeds.
