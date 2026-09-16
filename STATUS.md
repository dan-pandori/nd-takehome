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
- p1 = RTX 3090 24 GB ($0.50/h, zel7y1am7auj6u): depth-3 a1 seeds 2–6 (Stage-1 → EI) + coverage a1 s0/s1, a0 s0/s1, a1 s2–6.
- p2 = A100 80 GB ($1.59/h, luonpo569opsq1): depth-3 a1 seeds 7–9 + reductio seeds 3–4; coverage a2/a3 s0/s1 + new.
- p3 = A100 80 GB ($1.59/h, dreiq5frmuu0xt): reductio seeds 5–10; coverage reductio s0–2 + new.
- DEVIATION: no A40 in stock (all CUDA versions, Secure Cloud, 18:38–18:53 UTC); one 3090 and two A100s used instead. Cost ≈ $3.7/h for three pods. An orphan duplicate A100 (z2d9kk2bej4q0n, created by a timed-out attempt) was deleted at 18:53, ≈ 2 min of billing.

## Next step
Poll the pods; write the analysis script while Stage-1 and coverage run; interventions after round 4 of the arms.
