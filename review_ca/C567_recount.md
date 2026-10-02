# C5–C7 independent recount (prefix C567_)

Raw files: bucket → `rv/C567_raw/`, md5 4/4 = `~/work/<run>`. Param counts are from the summaries (no torch to verify).

## C5: trajectory / trajectory-cap6

**Models.**
- cap12: best-cap12 s0–s2, ALiBiGPT 6×384, 9.56 M params, `lean_staten`, from scratch on K12.
- cap6: best-cap6, same architecture, trained on the cap-6 set.

| quantity | stated | mine |
|---|---|---|
| A/B/C groups, both runs | as in summaries | identical |
| cap12 B eventual w1(r0), IQM | −6.21 [−6.80, −5.85] | −6.21 [−6.79, −5.82], i.e. **1-in-495** |
| cap12 Δ_RL own / ref | 4.59 / 1.55 (≈3×) | 4.59 / 1.55 (2.97×) |
| cap6 w1(r0); Δ_RL own / ref | −10.0; 8.81 / 5.12 | −10.14 (1-in-25,000); 8.81 / 5.12 (1.72×) |

**Selection effects**
- **Group labels.** The groups were pre-registered and are measured on the same x0 draw. On the independent x1 draw, r0 still solves 4/54, 9/51 and 11/60 of the B theorems (B is defined from the x0 draw), which is regression-to-the-mean exposure. w1(r0) is robust to this: redefining B from x1, or requiring failure in both draws, gives 1-in-360 to 1-in-820.
- **"Three times" depends on self-selection** (the eventual proof is r8's own argmax). My control, not reported for cap 12, scores the other cap-12 seeds' eventual proofs (`rev12_s<S>`):

| target (cap-12 B) | w1 r0 | Δ_RL | Δ_PT |
|---|---|---|---|
| own eventual | −6.21 | 4.59 | 4.09 |
| other seeds' eventual | −6.84 | **2.62** | 3.19 |
| cap-6 eventual | −7.38 | 2.05 | 3.19 |
| reference | −5.82 | 1.55 | 3.07 |

≈2 of the 3-nat own−ref gap is selection (per seed 1.7/2.2/2.0, ≈ MDD).

- **"One improbable step".** At r0 the median number of B steps below −4 nats is 1, but the other steps together cost 7–9 nats. The whole proof is about e⁻¹⁵.
- **Cross-run pair.** trajectory-cap6 re-scored the cap-12 proofs under the same checkpoints: |Δw1| = 0 exactly. The scores are bit-identical, so this is not independent evidence.

**Rating:** holds with caveats.
- Write "≈1-in-500 worst step, cap 12 only".
- Write "≈1.7× on unselected proofs" instead of 3×.

## C6: rl-from-ckpt

**Model:** best-cap12 ladders from Stage-1 checkpoints. Data: x1 reads at r8. All 30 cells and the reach table match the summary exactly.

| start | tb72 (s0/s1/s2) | pend−start tb72 [paired t95] | pend−start h250 [t95] |
|---|---|---|---|
| p1600 | 38/34/38 | +13.0 [6.4, 19.6] | +18.7 [6.9, 30.4] |
| p5000 | 48/44/46 | +3.7 [−5.1, 12.4] | +2.3 [−6.4, 11.1] |
| p12000 | 45/51/46 | +2.3 [−10.2, 14.8] | +4.0 [−3.5, 11.5] |
| p16000 | 49/47/51 | +0.7 [−3.1, 4.5] | **+4.7 [3.2, 6.1]** |
| pend | 48/48/53 | | |

- **MDD.** NOISE_FLOOR does not apply (different model). This run's own seed sd gives MDD = **7.8 tb72 / 5.7 h250** at n = 3.
- **Same checkpoint, x0 vs x1:** all |z| ≤ 0.49.
- **"Level" means "not resolvable", not equivalence.** Gaps of up to 12–15 tb72 are not excluded. On h250, pend beats p16000 in 3 out of 3 seeds, with a paired CI that excludes 0.
- **"No early start beyond it" is supported.** Strict reach: 11 vs 21, 7 vs 24 and 9 vs 20 theorems.

**Rating:** holds with caveats.

## C7: lit-measures M2

**Model:** 3.21 M GPT, `lean_seq`, from scratch, cap 6, trained on `train_p1`. Read-out: depth-3 held-out slice (500 theorems).

| | stated | mine |
|---|---|---|
| grid of 64 cells, mean / sd | 0.496 / 0.305 | same |
| 9 re-runs, sd | 0.225 | same |
| variance ratio | 0.55 | **0.543**, F95 [0.23, 2.05], bootstrap [0.02, 1.07] |
| init / data / residual | 0.17 / 0.02 / 0.81 | same |

- NOISE_FLOOR's depth-3 sd for this recipe is 0.3053, consistent with the grid's 0.305.
- **Caveats.**
  - All re-runs are one cell on one pod, with 8/9 in the high mode.
  - The distributions are bimodal.
  - Brown-Forsythe p = 0.033.
  - On overall accuracy the ratio is 0.68 [0.28, 2.58].

**Rating:** weaker than stated. "About half" is only a point estimate; the 95 % CI runs from about ¼ to all of the spread.

## Lean re-check

**How it was checked.**
- **Rendering:** C5 proofs come from the stored literal action text, replayed with `Env(canon=True)`. C6 and C7 proofs are converted with `nd2lean.translate`.
- **Acceptance:** exit code 0, no error or sorry, axioms ⊆ {propext, Classical.choice, Quot.sound}.
- **Term size:** the count of rule applications (fun, ⟨⟩, .1/.2/.elim, Or.*, byContradiction, `nA nB`).
- **Steps:** the count of have/exact.

| set | accepted | steps median [range] | term size median [range] |
|---|---|---|---|
| C5 eventual (30 cap12 + 20 cap6) | 50/50 | 11 [5–21] | 6.5 [2–19] |
| C6 early-start r8 | 35/35 | 13 [5–27] | 9 [2–28] |
| C7 re-run depth-3 | 35/35 | 7 [6–7] | 3 [2–3] |

**Negative controls: 88/88 rejected.**

| control | rejected |
|---|---|
| drop final `exact` | 30/30 |
| other theorem's statement | 30/30 |
| swap hypothesis | 16/16 |
| drop cited line | 12/12 |
