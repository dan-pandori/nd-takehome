# STATUS — round3-run4a

Brief: BRIEF_scale.md (this executor runs the **4a** half). Policy: AGENT_POLICY.md. Run id: round3-run4a.

## round3-run4a (executor)
- RUN3-4a START 2026-09-18 17:55 UTC. Preregistration `preregistration/round3-run4a.md` committed before any pod. Deviation decided up front: `train_reductio_f0.jsonl` is not on this host or in the bucket, so an f = 0 reductio set is rebuilt with the same assembler from reachable generator sets (`data/r3_4a/train_reductio_f0_b1.jsonl`) and a same-set 3.2M control (3 draws) is added; see QUESTIONS.md.
- 19:15 UTC: Stage-1 done for 3.2M / 25M / 85M (config A); held-out gate structurally unreachable for f = 0 reductio models (reductio-labelled held-out theorems), retries (config B) run per the pre-registered rule and kept as separate cells.
- RUN3-4a DONE 2026-09-19 00:57 UTC. 19 draws. Non-zero pre-RL draws: 3.2M 1 / 3, 25M 5 / 6, 85M 9 / 10 — one 85M draw is zero-rate and stays at 0 / 300 ("or nothing" survives at 85M, less often). Every hit at every size is 7-line; EI saturates the 7-line stratum (52) and gets ≤ 1 of 133 eight-line targets at every size. EI-only fraction does not fall with size (0.84–0.88 / 0.67–0.85 / 0.75–0.92; brief's E4 and my P5 wrong). Spend ≈ $33.8 of $50; all six pods deleted. `run4a.md`, `numbers.md` §Round 3 — Run 4a, `artifacts/r3_4a/summary.json`, bucket `round3-run4a/`.
