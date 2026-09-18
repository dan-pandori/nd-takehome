# STATUS — round3-run2

Brief: BRIEF_stratum-ignition.md. Policy: AGENT_POLICY.md. Run id: round3-run2.

## round3-run2 (executor)
- RUN3-2 START 2026-09-18 05:07 UTC. Preregistration `preregistration/round3-run2.md` committed before any pod. Pool `data/r3_2/targets_reductio_req6.jsonl` (345) built and checked (`data/r3_2/pool_report.json`).
- 05:58 UTC: 3 RTX 3090 pods (r32a, r32b, r32c); arm A batch 1 at round 15, arms B and C done at 8 rounds, cap-8 Stage-1 draws done. Interim: f = 0.1 s0 ignited the 8- and 9-line strata; zero-rate draws s1, s2 acquire six-liners (s2 fully ignited). C arms extended to 16 rounds.
- RUN3-2 DONE 2026-09-18 08:40 UTC. E1 1 of 6 (8-line stratum ignites rarely, needs rounds not samples); E3 falsified (zero-rate draws have six-line base rates and s2 ignites 8- and 9-line strata); E4 f = 1e-3 in band, proportionality holds as a trend (r = 0.81) but 2 of 6 f = 0 draws reach 2× base with ≥ 25 EI-only targets. Spend ≈ $4.7. run2.md, numbers.md §Round 3 run 2, artifacts/r3_2/summary.json, bucket round3-run2/.
