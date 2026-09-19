# STATUS — round3-run4b

Brief: BRIEF_scale.md (this executor runs the **4b** half). Policy: AGENT_POLICY.md. Run id: round3-run4b.

## round3-run4b (executor) — started 2026-09-18 17:50 UTC

- 17:55 UTC  Pre-registration `preregistration/round3-run4b.md` written before any pod. Pool: run 1's required@8 depth-3 pool (`data/r3_1/depth3_req.jsonl`, checked out from `origin/dan_round3-run1`). Note for Dan: on that pool the like-for-like 3.2M row is 2 / 8 non-zero draws and no ignition (acquisition ≤ 0.017), not the brief's 10 / 16 and 0.30–0.36 (those are the optional pool). Pods: A40 ($0.49/h), one per draw, instead of two A100s.
- 17:57 UTC  Pre-registration committed c1ad029 (17:54:40Z), pushed. `gate0` prints FAIL because the shared `~/pods.log` has `la-6` (ladder-A's pod, 17:53:21Z) after my start time; no pod of this run existed at the commit. See `QUESTIONS.md`. This run's pods are named `r34b-*`.
- 19:06 UTC  Interim: both sizes miss the E5 gate on the first schedule (25M 0.885–0.891, 85M 0.886–0.891; same 6-line-bin deficit as 3.2M) — pre-registered retry running. 25M: 3 / 3 draws zero-rate on the required pool (0 / 600k), `req` arms 0 / 300. 85M samples in progress (0 proofs so far). Six pods (4 A40 + 2 A6000), $3.02/h, ≈ $4 spent.
- 01:00 UTC (09-19)  Result: size bought nothing on this data (held-out greedy 0.885–0.891 at 25M / 85M vs 0.871–0.893 at 3.2M); larger bases are zero-rate *more* often (required pool: 0 / 3, 1 / 3 retry, 0 / 3, 0 / 3 retry; 3.2M 2 / 8); "or nothing" holds on the required pool at every size (11 / 11 zero-rate draws never train); with neighbours the retry-schedule draws ignite (25M 2 / 3, 85M 1 / 3), the first-schedule draws do not (0 / 6); EI-only fraction ≈ 1 (230 / 230, 230 / 231, 206 / 206 at pass@10⁴). 85M misses the quality gate on both schedules. Pods all deleted 00:48; spend ≈ $23.5. `run4b.md`, `numbers.md` §Round 3 run 4b, bucket `round3-run4b/`.

RUN3-4b DONE 2026-09-19T01:00:16Z
