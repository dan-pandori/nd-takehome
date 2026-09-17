# STATUS — proposals round 2 (runs 5, 2, 3, 1, 4)

Started 2026-09-17. Brief: BRIEF_ROUND2.md. Policy: AGENT_POLICY.md. Previous: STATUS_campaign1.md, STATUS_followup.md, STATUS_handoff.md.

## Run 5
- 2026-09-17 19:08 UTC  Started. Oracle (`minlen.py --forbid`, `necessity.py`) written and tested; plan + expectations in log.md; reductio candidates being labelled on the VPS; pods next.
- 2026-09-17 22:05 UTC  Done. Required pools built (reductio 300 + 150; cap-8 strict derived-ORE 300 + 65; ten hand-checked each), 9 + 8 arms + 5 base pass@10⁴ runs. Reductio: f = 0 zero-rate draws 0 / 300, igniting draw and both f = 0.1 arms ≈ 52 / 300 = the two 7-line schemata only; derived-ORE (cap 8): f = 0 0.087 / 0.080 → f = 10⁻² 0.160 / 0.210, 10× block C, base-reachable on 27 / 300. 0 oracle violations in 9,600 target-arm pairs. `run5.md`, `figures/run5_*.png`, `numbers.md` §Run 5, `artifacts/r5/summary.json`; bucket `hf://buckets/dan-pandori/nd-rl/round2/run5/{artifacts,ckpts,data}`. Pods p1 + p2 (3090) ≈ 5.6 h ≈ $3.
- RUN5 DONE 2026-09-17 22:05 UTC

## Run 2
- 2026-09-17 22:05 UTC  In progress: classes and expectations pre-registered (log.md 19:47); six pools built (three from generator knobs / schemata, disclosed in QUESTIONS.md); four sets assembled (f = 0 asserted); 8 Stage-1 done or finishing; 12 EI arms launched 21:58–22:01 on p1–p3.

## Run 3
- 2026-09-17 22:18 UTC  Started (in parallel with run 2's tail): plan + expectations log.md 22:14; 30 injection arms (5 arms × 6 conditions) on p4 (depth-3) and p5 (reductio), RTX 3090s.

## Run 1

## Run 4
