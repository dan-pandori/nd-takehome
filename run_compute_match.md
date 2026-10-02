# compute-match: with best-cap12's GPU time, our 3.2 M recipe gains almost nothing, and the gap stays beyond the MDD

**Question.** `best-state`'s best-cap12 ladders used 1.6–1.9× the A40-seconds of ours. Does our recipe close the gap if
its ladder gets the same GPU time?

**Design** (`preregistration/compute-match.md`). Our Stage-1 was not extended: at cap 12 it already uses 1.74× best's
Stage-1 A40-seconds (2,247 vs 1,288 s). So the inherited SN-cap12 Stage-1 checkpoints (s0–s2) are reused, and the ladder's
k goes from 32 to **64**. That k was chosen from a one-round pilot, projecting 28,550 s against a 28,451 s target. Result:
29,129 A40-s per ladder (1.02× best12; 1.06× including Stage-1). Lean alone judges. Models: 3,216,384-param `lean_staten`
GPT from scratch on K12 (cm12, SN12) vs 9,560,832-param ALiBiGPT (best12).

| T1, seeds 0/1/2 | best12 (k 32) | **cm12 (k 64)** | SN12 (k 32) | best12 − cm12 | MDD |
|---|---|---|---|---|---|
| textbook72 /72 | 52 / 51 / 52 | 36 / 36 / 36 | 36 / 40 / 36 | **+15.7** | 6.5 |
| dev metric /1,108 | 1,058 / 1,050 / 1,055 | 934 / 995 / 972 | 927 / 972 / 961 | **+87.3** | 61 |
| holdout250 /250 | 239 / 237 / 237 | 220 / 224 / 225 | 217 / 221 / 223 | +14.7 | – |
| rr600 Q /380 | 377 / 375 / 376 | 232 / 295 / 320 | 227 / 293 / 317 | +93.7 | – |

**Outcome vs expectation.**
- **Falsifier not met.** Both gaps stay beyond the MDD; every best seed beats every cm12 seed. On the dev metric the
  bootstrap interval's lower end touches the MDD ([+61, +119]). Best-state's advantage comes from the recipe, not the extra
  GPU time.
- Doubling attempts did almost nothing (paired cm12 − SN12): textbook72 0 / −4 / 0 (I predicted +2.5), dev +7 / +23 / +11
  (predicted +25), Q +2 to +5 (I predicted cm12 Q ≈ 330; it is 282). Ladder targets solved at round 8 rose only
  +35 to +43 of 4,495.
- Hits: dev 967, holdout250 223, long2 12.3, held-out greedy 0.972, K = 64.

**Caveats.** Matched on GPU-seconds, not samples: cm12 used 1.8× the attempts and 1.4–1.6× the Lean checks (flagged).
n = 3 per arm. Cut-offs ≤ 0.17 %. Spend: 28.4 pod-hours, $13.93.
