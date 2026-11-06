# olmo-ifomega — does Olmo 3.1 Think 32B's RL create reach where RL moved it?

**Models.** RL start `allenai/Olmo-3-32B-Think-DPO`; `allenai/Olmo-3.1-32B-Think` `step_0750`, `main` (= `step_2300`).
Think RL template and decoding (T 1, top-p 1, 32,768 tokens). IFBench (218 headline prompts; 82 with an SFT/DPO/RL
copy excluded), IFEval (150), OMEGA `test_out` (100). Grades: official IF checkers (strict); OMEGA exact match and RL's
verifier; blinded hand check (465 items, all confirmed).

| pass@1 [95 %] / pass@8 | DPO | step 750 | step 2,300 |
|---|---|---|---|
| IFBench strict | 0.29 [0.24, 0.34] / 0.46 | 0.51 / 0.79 | 0.68 [0.64, 0.73] / 0.89 |
| IFEval strict | 0.77 / 0.91 | 0.89 / 0.95 | 0.93 / 0.97 |
| OMEGA `test_out` | 0.27 [0.21, 0.35] / 0.52 | 0.55 / 0.71 | 0.62 [0.54, 0.71] / 0.73 |

**Findings.**
1. **IFBench: Reach** (pre-registered rule). On 42 prompts (hand; 49 strict) step 2,300 is confirmed with genuine
   answers while DPO has none in 256 samples. DPO resolved 30 of 94 candidates. Gaming is common on both sides:
   36 % of step 2,300's first-checked credited answers are gamed (minimal text that meets the constraint), and on 11
   more prompts its strict "reach" is gaming only.
2. **OMEGA `test_out`: inconclusive by hand** — 2 reach prompts (perp_068, perp_069), both **reach at RL's token cap**:
   DPO hits 32,768 tokens on 255 of 256 samples each. DPO resolved 8 of 13 candidates, three geometry ones despite
   ≥ 93 % cut. One official answer is wrong (perp_055: 17, should be 15); corrected, it is a third reach prompt.
3. **IFEval** (in-distribution control): IFEVAL_LINE
4. **DPO's failures are substantive, not format**: on IFBench's 49 zero-success prompts 93 % miss the binding
   constraint by far or ignore it (3 % near misses); on geometry 99 % are the token cap.
5. Reach is not concentrated on constraint types near RL's IF data (48 % of hand-reach prompts' binding constraints
   have no RL analogue vs 38 % overall).

**Verdicts:** IFBench Reach (strict, hand); `test_out` Reach under exact match (through the wrong label), inconclusive
under RL's verifier and by hand; IFEval IFEVAL_VERDICT. RL is 0.8 % of pretraining FLOPs at step 2,300.

**Expectations vs outcomes.** pass@1 inside ranges except RL on `test_out` (0.62 vs 0.40; step 750 0.55 vs 0.36);
IFBench candidates 94 vs 30 and entries 98 vs 55 (above); verdicts modal (IFBench Reach, `test_out` inconclusive);
gaming far above the ≤ 10 % expected; failure modes more substantive than expected (93 % vs 60 %).

**Deviations.** `step_0100` and `test_in` cut; intermediate checkpoints not confirmed; budget raised twice ($225,
$325); pods deleted by the watchdog once (driver cap), work resumed; hand rule 5 added (fixed-output constraints).

**Cost** COST_LINE. Memo: `olmo_ifomega/scaleup_memo.md`.

![entries, exits and reach against RL compute](figures/olmo_ifomega_reach.png)
