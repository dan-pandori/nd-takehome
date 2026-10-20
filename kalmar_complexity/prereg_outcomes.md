| pre-registered (point; range) | outcome | verdict |
|---|---|---|
| K-sl algorithm, Python raw / DEFLATE / xz bytes: 1,300 (900–1,900) / 650 (450–900) / 650 (450–950) | 1,907 / 864 / 906 | raw just above the range; DEFLATE, xz inside |
| K-sl rendering to `lean_seq`, Python DEFLATE: 350 (200–600) | 562 | inside |
| K-tt (algorithm + Lean), Python DEFLATE: 600 (400–850) | 866 | just above |
| K-sl algorithm, Qwen3 tokens: 450 (300–700) | 897 | above |
| K-sl algorithm, BLC: 3,000 (1,500–5,000) | 5,443 | **above** |
| K-tt algorithm, BLC: 2,300 (1,200–4,000) | 1,636 | inside |
| rendering, BLC: 1,000 (400–2,500) | K-sl 616 / K-tt 4,204 | K-sl inside; K-tt above |
| binary CL / BLC ratio: 2.5 (1.5–4) | Kalmár 4.4–4.5; calibration 2.0–3.5 | Kalmár above (plain bracket abstraction) |
| RASP-L per-step policy: 130 ops (70–250) / depth 15 (8–30) | 492 ops / depth 41 (effective 4–33, recursion steps 17.2 mean) | **missed, ≈ 4× and ≈ 3×** |
| decision procedure: 35 leaves (15–80) / 400 bits (150–1,000) | 46 leaves / 626 bits | inside |
| feature extractor, Python DEFLATE: 500 (300–800) | ≤ 3,962 (mechanical, with all of policy.py) | above as measured (upper bound); "most of the algorithm sits in the features" holds |
| calibration, BLC: copy 4 / reverse 50 / parity 50 / addition 200 / sort 250 / eval 200 / taut 350 | 4 / 87 / 82 / 375 / 257 / 273 / 410 | all within 2×; mostly under-estimated |
| Kalmár rank 1 in Python-DEFLATE, BLC, binary CL, RASP-L; ≥ 5× the next item in BLC | rank 1 in all four; K-sl 13× taut | held (K-tt alone would be 4×) |
| K12 generator larger than K-sl (1.2–3×), Python DEFLATE | 2.2× (mechanical vs mechanical) | held |
| rank agreement Python-DEFLATE vs BLC ≥ 0.8; RASP-L disagrees on parity / addition | +0.97; RASP-L vs BLC +0.86 (parity needs a scratchpad in RASP-L: rank 5 vs 8) | held; disagreement only on parity |
| B1 KAL-D first-epoch prequential code: 1.5 × 10^7 (0.5–4 × 10^7) (not blind for s0) | 1.24–1.26 × 10^7 | inside |
| B1 KAL-D EDL, residual = final train loss: 6 × 10^6 (10^6–2 × 10^7) | 6.8–7.3 × 10^6 | inside |
| B1 control EDL: 2 × 10^6 (10^5–10^7); KAL-D > control (60 %) | 1.9–2.6 × 10^6 (final train) / 1.5–1.7 × 10^6 (held-out); KAL-D ≈ 4× control | held |
| absorbed bits / K-sl BLC bits ≈ 2,000 (100–20,000); ≥ 100 for every estimate | B1 1,150–1,300 (held-out residual); B2: B2 195–270× (EDL 1.06–1.46 × 10^6) | held (≥ 100 everywhere) |
| B2 Kalmár L over 8,192 theorems: 3 × 10^6 (0.6–12 × 10^6) | 1.37 × 10^6 bits | inside the range |
| B2: K12's EDL below Kalmár's at equal theorems; eval's below both | at 16,384 theorems, EDL Kalmár 1.1–1.5 × 10^6 > K12 1.8–3.2 × 10^5 > eval 0.8–1.5 × 10^5 at every size | held |
| B2 size dependence: L < M < S for Kalmár | at 8,192: S 2.35 / 2.44, M 1.40 / 1.44, L 1.37 × 10^6 | M, L < S held; L < M not resolved (inside the seed spread) |
| B2 bits per occurrence highest for ∧+, ∨+, ¬⊥, →I-B-true; lowest for close, lem, split | highest ∧ true, ∨ true, ¬⊥, →I-A-false (→I-B-true mid-table); lowest excluded middle, close, split | mostly held (→I-B-true wrong) |
| B2 EDL per token: Kalmár rises then falls; K12 and eval fall monotonically | Kalmár and K12 fall monotonically; eval plateaus, then falls | **missed** (the teaching-like shape is eval's, not Kalmár's) |
| best predictor of per-step-type error: computational demand (declared-formula length or evaluation height), ρ ≥ 0.6 | best: RASP-L decision depth +0.85, in-scope lookups +0.82, target height +0.78; declared length +0.42, focus height +0.49 | the class (demand) held; the two named sub-measures were not the best (declared length fails the bar) |
| program length (any language) vs per-type error: \|ρ\| < 0.4 | Python code bytes −0.55 (p 0.04); given frequency −0.08 | raw ρ outside (negative, = frequency); no predictive value once frequency is controlled |
| frequency baseline ρ between −0.4 and −0.7 | −0.60 | held |
| B2 per-type bits vs KAL-D error: ρ ≥ 0.7 | +0.82 (L), +0.85 (M), +0.82 (S) | held |
| state level: demand adds to step type, LR p < 0.01 in each seed | LR χ² 6,043–7,651 (df 9), p ≈ 0 in all three seeds | held |
| B1-snap per-type code of final KAL-D ranks types like TF error, Spearman ≥ 0.8 (addendum) | +0.73 (seeds +0.64 to +0.78) | missed |
| recommendation: a learner-relative EDL plus a per-step demand profile, not program length | see `run_kalmar_complexity.md` | as expected |
| B3 (addendum 2): opener error falls ≥ 50 % (FOC vs STD) | −94 % (31.96 → 1.94 %) | held |
| B3: other-state error changes < 30 % | −30 % as pre-registered (−53 % without first states) | **missed** narrowly: FOC also helps the other steps |
| B3: ∧ true, ∨ true, ¬⊥, →I-B-true each fall ≥ 40 % | −93 / −89 / −100 / −87 % | held |
| B3: across-type ρ(error, lookups) ≥ 0.6 under STD, ≤ 0.3 under FOC | +0.61 → −0.02 (first states out +0.92 → +0.27) | held |
| B3 falsified if opener error falls < 25 % | −94 % | not falsified |
