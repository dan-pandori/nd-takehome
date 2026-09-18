# STATUS — proposals round 2 (runs 5, 2, 3, 1, 4)

Started 2026-09-17. Brief: BRIEF_ROUND2.md. Policy: AGENT_POLICY.md. Previous: STATUS_campaign1.md, STATUS_followup.md, STATUS_handoff.md.

## Run 5
- 2026-09-17 19:08 UTC  Started. Oracle (`minlen.py --forbid`, `necessity.py`) written and tested; plan + expectations in log.md; reductio candidates being labelled on the VPS; pods next.
- 2026-09-17 22:05 UTC  Done. Required pools built (reductio 300 + 150; cap-8 strict derived-ORE 300 + 65; ten hand-checked each), 9 + 8 arms + 5 base pass@10⁴ runs. Reductio: f = 0 zero-rate draws 0 / 300, igniting draw and both f = 0.1 arms ≈ 52 / 300 = the two 7-line schemata only; derived-ORE (cap 8): f = 0 0.087 / 0.080 → f = 10⁻² 0.160 / 0.210, 10× block C, base-reachable on 27 / 300. 0 oracle violations in 9,600 target-arm pairs. `run5.md`, `figures/run5_*.png`, `numbers.md` §Run 5, `artifacts/r5/summary.json`; bucket `hf://buckets/dan-pandori/nd-rl/round2/run5/{artifacts,ckpts,data}`. Pods p1 + p2 (3090) ≈ 5.6 h ≈ $3.
- RUN5 DONE 2026-09-17 22:05 UTC

## Run 2
- RUN2 DONE 2026-09-18 01:30 UTC — `run2.md`, numbers.md §Run 2, `figures/run2_acq.png`, `run2_curves.png`; uploaded to `hf://buckets/dan-pandori/nd-rl/round2/run2/{artifacts/r2,data/r2,ckpts/r2}`. No f = 0 arm crossed zero except one NEGI draw with a non-zero base rate; depth-4 is a base generalisation at cap 8 (11–20 % of samples from zero-coverage data) and unreachable at cap 6 (length).
- 2026-09-17 23:25 UTC  NOTE: seven pods not created by this session (`r4-1`…`r4-6`, `r1-a100`) are running on the account since ≈ 23:00 UTC; see QUESTIONS.md (kill switch scope, HF token echo).
- 2026-09-17 22:05 UTC  In progress: classes and expectations pre-registered (log.md 19:47); six pools built (three from generator knobs / schemata, disclosed in QUESTIONS.md); four sets assembled (f = 0 asserted); 8 Stage-1 done or finishing; 12 EI arms launched 21:58–22:01 on p1–p3.

## Run 3
- RUN3 DONE 2026-09-18 01:06 UTC — uploaded to `hf://buckets/dan-pandori/nd-rl/round2/run3/{artifacts/r3,data/r3,ckpts/r3}`.
- 2026-09-18 01:01 UTC  All 30 arms done; `run3.md`, numbers.md §Run 3, `figures/run3_ignition.png` written; upload pending (checkpoints pulling). One proof ignites every arm; the other pattern never; invalid strings with the box tokens ignite one depth-3 draw.
- 2026-09-17 22:18 UTC  Started (in parallel with run 2's tail): plan + expectations log.md 22:14; 30 injection arms (5 arms × 6 conditions) on p4 (depth-3) and p5 (reductio), RTX 3090s.

## Run 1
- 2026-09-18 01:01 UTC  Step 1 done: `nd2lean.py`, agreement 100 % on 95k+ positives and 4,012 negatives (75,085 RL transfer proofs re-checked after a premise-naming fix). Step 2 generated (Qwen3-Coder-30B-A3B on p6, A100), scoring; step 3 running (0.6B, 1.7B done).

## Run 4
- 2026-09-18 01:01 UTC  `grpo.py` written; 12 arms running on p4 / p5 (8 finished). First arm: acquisition 0.48 vs EI 0.34 on the same draw, held-out greedy 0.87 → 0.56.
