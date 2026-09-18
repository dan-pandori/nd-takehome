# STATUS — round3-run3

Brief: BRIEF_base-generalisation.md. Policy: AGENT_POLICY.md. Run id: round3-run3.

## round3-run3 — base generalisation by pattern class, 24 seeds per set, no RL (executor)

- 2026-09-18 05:32 UTC: started 05:07. Pre-registration `preregistration/round3-run3.md` committed before any pod (gate 0). f = 0 verified for all three sets (`artifacts/r3_3/f0_check.log`). Plan: code additions (per-rule held-out loss, first-half predicates) → derived-ORE oracle → 72 Stage-1 draws → pass@2000 coverage over the full pools → analysis.
- 2026-09-18 05:34 UTC: three RTX 3090 pods (r33a depth-3, r33b reductio, r33c derived-ORE) running the Stage-1 → coverage queues. Derived-ORE strict cap-6 pool built and oracle-labelled (25 required / 275 optional, 0 inconsistencies, 10 hand-checked). Gate-0 note: the shared `~/pods.log` shows sibling run 2's pod r32a (05:15:15) before my pre-registration commit (05:16:17); my first pod is r33a at 05:23 — see QUESTIONS.md.
- 2026-09-18 12:50 UTC: main pass (72 draws) and pre-registered deep pass complete; all four pods deleted after listing diffs; pod cost ≈ $14. Result: depth-3 15 / 24 (0.41–0.81), reductio 12 / 24 (0.29–0.71), strict derived-ORE 0 / 24 (0–0.14); intervals of depth-3 and reductio overlap (E2 fails); with the deep pass 19 / 24 and 17 / 24. Write-up `run3-3.md` (`run3.md` is round 2's), numbers `numbers.md` §Round 3 — Run 3, bucket `hf://buckets/dan-pandori/nd-rl/round3-run3/`.
- Gate notes for the orchestrator / reviewer: (1) gate 0 reads the shared `~/pods.log`; the pod it flags (r32a, 05:15:15) is round3-run2's — my pre-registration commit is 05:16:17 and my first pod r33a 05:23 (QUESTIONS.md). (2) gate 1's `TEST_RUN_DONE mtime changed` is a worktree artefact: the file's mtime here is the worktree checkout time (05:07:30, before this session started at 05:07:45), it is unmodified in git, and the test file was not run. (3) gate 1's missing-path warnings come from earlier sections whose gitignored files live in `~/nd-takehome`, and from `<tag>` placeholders in this run's citations; every concrete path of this run's section exists.

RUN3-3 DONE 2026-09-18 12:50 UTC
