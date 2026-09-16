# STATUS — hand-off run (orchestration proposal, then ignition study)

Started 2026-09-16 18:29 UTC. Brief: HANDOFF_BRIEF.md. Previous: STATUS_campaign1.md, STATUS_followup.md.

## Plan
1. Task 1 (no pods): orchestration proposal at ~/nd-rl/docs/proposals/2026-09-16-automated-research-orchestration.md on branch dan_orchestration, linked from docs/STATE.md; draft PR, no reviewers. Target: done by ~20:30 UTC.
2. Task 2 (pods, ≤ 3 A40, ≤ ~$80 more): ignition study on dan_novelty → ignition.md, figures/ignition_*.png, numbers.md + log.md sections. Expected results written to log.md before any arm runs.

## Done
- 18:33 Task 1: proposal committed to nd-rl (82775b2, branch dan_orchestration), draft PR https://github.com/chainik1125/nd-rl/pull/3 (no reviewers).
- 18:37 Task 2 plan + pre-registered expectations committed (fbdde13) before the first pod was created (18:41).
- 2026-09-16T18:30:31Z read CAMPAIGN_BRIEF, campaign, followup, review_campaign, review_followup, nd-rl AGENTS.md / docs layout / STATE.md; pod helpers; driver loop; no pods registered.

## Running on pods
(none — p2 deleted 21:41, p3 21:55, p1 21:58 UTC; `runpodctl pod list` = []). Pod time: p1 3090 3.3 h ≈ $1.7; p2 A100 3.0 h ≈ $4.8; p3 A100 3.05 h ≈ $4.9; orphan ≈ $0.1 → ≈ $11.5 this run (≈ $30 cumulative of the $100 policy).

## Interim observations (pod peeks, partly pulled)
- Depth-3 a1 (8 new seeds): s2 ignited r2 (336), s9 r2 (354), s8 r4–5 (312), s3 r5 (295), s4 never (4 theorems, first at r7), s7 never (0 through r8, 318 solved without a third box); s5, s6 running on p1.
- Reductio (8 new seeds): s7 ignited r1–2 (112/606 at r8); s5, s6 0/606 at r8; s3, s8, s9 0 at r5; s4, s10 early rounds.
- Interventions running: depth-3 s7 (p2), s3 (p2), s4 (p3); reductio s5, s6 (p3), s3 (p2), s8, s9 (p3). First result: sibling transfer ignited reductio s5 (91/606 at r8); k = 128 and T = 1.0 did not (0).
- Pre-RL pass@2000 × 300: depth-3 s2 and s7 both 0 depth-3 samples in 600k (so the 600k sample does not separate an r2 igniter from a never-igniter); reductio s5 0. The arms' round-1 counts (32 attempts on every target, pre-training) are recorded as a second base-rate measure.

## Next step
Poll the pods; write the analysis script while Stage-1 and coverage run; interventions after round 4 of the arms.
