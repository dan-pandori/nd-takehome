## capability-defs (2026-10-05, executor; UNREVIEWED)

**Models (every number here unless labelled):** cap 12 = best-cap12, `best_model.ALiBiGPT` 6 × 384, 9,560,832 params,
`lean_staten` (environment-assigned names), trained from scratch on K12 (`data/kh/train_k12.jsonl`, 155,000 proofs,
md5 800b5486; Stage 1 1,200 s, A40). **pend** = `trajectory`'s `stage1_best12_s<S>_b1200.pt`; **r8** = its T1 ladder
`la_T1_best12_s<S>_r8.pt`; **r16** = `rl-continue`'s `la_T1_best12_s<S>_r16.pt`; **init** = step 0; seeds 0–2 (md5s in
`capability_defs/analysis/INVENTORY.md` § C and the pods' setup logs). **Cap 6** = the same network and recipe on the
cap-6 Stage-1 set (`trajectory-cap6`, `rl-continue-cap6`). **Replay-only control** = `rl-from-ckpt`'s
`c<S>_pend_r8` (8 ladder fine-tune rounds on K12 replay, no RL proofs). **Lean alone judges** (`lean_gate`;
`nd_verify` not called). **Evaluation theorems:** textbook72 (scoring only; dev58 / train14 in `out/j3.txt`) +
holdout250 = 322. **Reads:** plain sampling, T 0.8, `max_steps` 96, `max_action` 512, k 256 per draw (x0, x1);
guided = `guided_eval.py --arm logical`, k 256, seed 1, `max_rej` 10. Sources: `capability_defs/analysis/out/*`
(scripts named per line), pod outputs under `artifacts/cd/` (bucket paths below).

**Budgets** (`cd_defs.py` READ_S / LADDER_S; 3.6 ms per pend attempt on hard theorems, J2 chunk s0_c00: 131,072 in
470 s): K_eval-set = ladder GPU-s / (322 × 3.6 ms) = 19,281 / 21,107 / 23,310 (r8), 47,962 / 49,428 / 50,447 (r16);
K_per 777 / 731 / 954 (r8); K_total 3,493,886 / 3,285,882 / 4,287,918 (r8).

**Known-proof estimate** (`cd_bracket.py` → `out/bracket_all.txt`, `out/bracket.json`; J1 stage 1 at one name base
for every known accepted proof — 136,466 / 130,658 / 118,517 per seed — and stage 2 exact at 33 bases for 4,518 / 4,647 /
4,401 top proofs, 0 replay failures): calibration (30 theorems per seed, ≈ 4,900 pend attempts each) median
exp(LB) / p̂ **0.982 / 0.940 / 0.925** (IQR 0.904–1.020 / 0.848–0.998 / 0.851–0.948); all measured theorems (64 / 59 /
71) 10th / 50th / 90th percentiles 0.28 / 0.95 / 1.34, 0.38 / 0.91 / 1.15, 0.16 / 0.92 / 1.28; above the sampling UB95
on 3 / 2 / 1. Best single proof's share of LB: 0.62 / 0.50 / 0.51. Random-init null: median log LB_init on hard
theorems −823 / −834 / −905 nats (range −290 to −3,229).

**Bracket verdicts at K_eval-set** (r8-solved hard theorems):

| r8-solved hard theorems, verdict at K_eval-set | s0 | s1 | s2 |
|---|---|---|---|
| RL-solved hard theorems | 55 | 45 | 52 |
| elicited: sampling lower bound ≥ 1 / K | 17 | 17 | 21 |
| elicited: known-proof estimate ≥ 2 / K | 5 | 1 | 3 |
| base found it, but not certifiably within reach | 12 | 8 | 17 |
| not reached: 0 base successes in ≥ K attempts | 21 | 19 | 11 |
| undetermined (0 successes, fewer than K attempts) | 0 | 0 | 0 |
| certified created (UB95 < 0.05 / K) | 0 | 0 | 0 |

**Created sets** (`cd_part3.py` → `out/part3.txt`, `out/part3.json`; rendered by `cd_report_tables.py` →
`out/report_tables.md`):

| definition (card) | r8, x0: s0 / s1 / s2 | net of replay-only | r16, x1 | redraw Jaccard (r8) | seed Jaccard (r8, pairs) |
|---|---|---|---|---|---|
| equal-k (`passk-equal-k`) | 54 / 51 / 60 | 37 / 27 / 33 | 61 / 65 / 61 | 0.78 / 0.70 / 0.68 | 0.35 / 0.39 / 0.34 |
| compute-matched (`passk-budget`) | 22 / 21 / 14 | 20 / 14 / 8 | 25 / 34 / 17 | 0.84 / 0.86 / 0.87 | 0.19 / 0.16 / 0.25 |
| … of which 0 base successes | 18 / 18 / 9 | 17 / 12 / 6 | 22 / 31 / 12 | 0.85 / 0.84 / 0.80 | 0.24 / 0.17 / 0.23 |
| cm, no seed's base ever solves t | 5 / 6 / 6 | 5 / 4 / 5 | 7 / 16 / 9 | 0.83 / 0.83 / 0.71 | 0.38 / 0.38 / 0.50 |
| cm, J7 continuation fails t (draw x0) | 18 / 0 / 0 | 17 / 0 / 0 | 22 / 0 / 0 | 0.81 / – / – | 0.00 / 0.00 / – |
| reliable (`reliability`) | 12 / 9 / 5 | 10 / 6 / 3 | 12 / 14 / 8 | 1.00 / 1.00 / 0.83 | 0.11 / 0.06 / 0.27 |
| best known proof < 1 / K (`tf-proof-prob`) | 29 / 27 / 24 | 23 / 16 / 17 | 31 / 39 / 26 | 0.88 / 0.89 / 0.84 | 0.22 / 0.20 / 0.31 |
| not certified elicited (`marginal-bracket`) | 29 / 26 / 25 | 24 / 17 / 17 | 32 / 38 / 23 | 0.88 / 0.89 / 0.85 | 0.28 / 0.26 / 0.31 |
| guided read fails too (`capability-vs-propensity`) | 19 / 17 / 13 | 17 / 12 / 8 | 23 / 30 / 16 | 0.82 / 0.83 / 0.86 | 0.12 / 0.14 / 0.20 |
| family members (`schema-acquisition`) | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 11 / 0 | 0.00 / 0.00 / – | 0.00 / – / 0.00 |
| IRT DIF+ (`irt-ability`, unmatched) | 26 / 26 / 30 | 18 / 19 / 23 | 33 / 35 / 37 | 1.00 / 1.00 / 1.00 | 0.41 / 0.37 / 0.44 |
| expansion share ρ ≥ ½ (`sharpen-expand`) | 48 / 42 / 46 | 36 / 24 / 27 | 55 / 59 / 50 | 0.92 / 0.93 / 0.91 | 0.34 / 0.32 / 0.38 |
| new rule set + cm (`new-proof-new-theorem`) | 5 / 4 / 0 | 5 / 3 / 0 | 4 / 11 / 2 | 1.00 / 1.00 / 0.00 | 0.29 / 0.00 / 0.00 |
| chain depth ≥ 2 + cm (`chain-reachability`) | 14 / 14 / 10 | 12 / 8 / 5 | 14 / 23 / 12 | 0.88 / 0.93 / 1.00 | 0.17 / 0.14 / 0.26 |
| rule set not in K12 (`out-of-data-novelty`) | 14 / 20 / 20 | 8 / 9 / 11 | 14 / 29 / 23 | 0.81 / 0.85 / 0.82 | 0.62 / 0.55 / 0.60 |

**Set-level coverage** (r8 draw x0, r16 draw x1):

| seed | base within reach at K_eval-set (r8 / r16 budget) | replay-only r8, k 256 | J7 continuation, k 256 | r8, k 256 | r16, k 256 | Δ_cov r8 / r16 |
|---|---|---|---|---|---|---|
| s0 | 265 / 267 | 239 | 220 | 286 | 291 | +21 / +24 |
| s1 | 270 / 271 | 244 | – | 286 | 303 | +16 / +32 |
| s2 | 281 / 281 | 249 | – | 293 | 295 | +12 / +14 |

**Agreement** (mean Jaccard over seeds of the 12 definitions' sets): mean off-diagonal 0.305 (r8, x0), 0.355 (r16, x1);
highest brk_ne–tfmax 0.90, cm–guided 0.87, eqk–sharp 0.83; lowest pairs involve npnt (0.02–0.06).

**Plain vs guided** (`cd_j3.py` → `out/j3.txt`; J3 / J3c6, `guided_eval.py --arm logical`, k 256, T 0.8, seed 1,
max_rej 10, batch 2,048, cap-6 s1 r8 at batch 1,024 after an OOM):

| model | textbook72 dev58: plain / guided | train14 | holdout250 | guided tokens per attempt |
|---|---|---|---|---|
| cap 12 s0 pend | 28 / 36 | 6 / 6 | 196 / 218 | 307 |
| cap 12 s0 r8 | 40 / 43 | 8 / 11 | 240 / 239 | 322 |
| cap 12 s0 r16 | 42 / 45 | 9 / 10 | 240 / 240 | 354 |
| cap 12 s1 pend | 27 / 33 | 6 / 10 | 205 / 223 | 343 |
| cap 12 s1 r8 | 38 / 41 | 10 / 11 | 236 / 237 | 324 |
| cap 12 s1 r16 | 45 / 45 | 12 / 11 | 246 / 247 | 354 |
| cap 12 s2 pend | 30 / 38 | 6 / 10 | 200 / 222 | 315 |
| cap 12 s2 r8 | 42 / 45 | 11 / 11 | 237 / 241 | 308 |
| cap 12 s2 r16 | 44 / 50 | 12 / 12 | 239 / 241 | 331 |
| cap 6 s0 pend | 14 / 24 | 4 / 5 | 153 / 183 | 249 |
| cap 6 s0 r8 | 35 / 38 | 8 / 10 | 225 / 226 | 353 |
| cap 6 s0 r16 | 37 / 40 | 8 / 11 | 232 / 233 | 415 |
| cap 6 s1 pend | 15 / 19 | 3 / 4 | 126 / 165 | 334 |
| cap 6 s1 r8 | 38 / 39 | 5 / 8 | 226 / 230 | 335 |
| cap 6 s1 r16 | 36 / 38 | 5 / 8 | 233 / 235 | 327 |
| cap 6 s2 pend | 11 / 21 | 4 / 6 | 128 / 175 | 276 |
| cap 6 s2 r8 | 32 / 37 | 7 / 8 | 221 / 229 | 408 |
| cap 6 s2 r16 | 34 / 38 | 6 / 10 | 232 / 236 | 367 |

Q13: pend's guided read solves 27 / 54, 28 / 51, 36 / 60 of B (r8 x0) and 30 / 61, 29 / 65, 35 / 61 of the r16 x1
sets; cap 6: 40 / 101, 50 / 132, 54 / 122.

**Excluded-middle teachability** (`cd_lem.py` → `out/lem.txt`; 39 classical-only held-out A ∨ ¬A instances, k 256,
T 0.8, seed 1; solved of 39, mean pass@1): pend 0 / 0 / 0; A0 0; C16 0; A4 36 (0.66) / 33 (0.35) / 36 (0.64); A16 37
(0.79) / 34 (0.68) / 37 (0.83); r16 0 / 36 (0.70) / 13 (0.13); knockout 0; knockout + A16 (K12 replay) 35 (0.71) / 37
(0.72) / 37 (0.70); J6b (DN-free replay, fine-tune seeds f0, f1): pend + A16n 36, 36 / 36, 35 / 35, 36; knockout +
A16n 34, 34 / 36, 36 / 36, 36; + C16n 0 everywhere. Decision (pass@256 gain difference, pend − knockout): +0.051 /
−0.013 / −0.013 → teachable (pre-registered within 0.2). J4 holdout250 solved@64: A0 204 / 207 / 205, A16 216 / 222 /
210. Knockout: held-out greedy 0.862 / 0.848 / 0.862 (pend 0.921 / 0.936 / 0.962); holdout250 solved@256 172 / 164 /
170 (pend x1 196 / 205 / 200).

**J2** (pend, T 0.8, standard caps): stage A 16,384 on the J2 theorems (87 / 89 / 85) with ≥ 1 success on 57 / 52 / 64
(hard-only 24 / 54, 20 / 57, 28 / 49); A′ 16,384 on hard theorems no RL read solves: 0 / 29, 1 / 18, 0 / 22 get a
success; B 49,152 more on stage-A zeros: 23 / 30, 31 / 37, 14 / 21 stay at 0; truncation re-reads at doubled caps (2 /
1 / 3 theorems): 1 success (`textbook_6997656e16fb567550a6`, 2 / 16,384). Beta-binomial backtest (`out/extrap.txt`):
predicted 56.8 / 58.8 / 59.5 vs observed 57 / 52 / 64 J2 theorems with ≥ 1 success (−0 / +13 / −7 %); zero-inflated
38.7 / 39.8 / 43.1 (−32 / −23 / −33 %).

**J8** (`cd_j8.py` → `out/j8.txt`; rl-from-ckpt ladders from p1600 / p5000 / p12000 / p16000): new r8 solves 182 /
117 / 86 / 76 (s0), 157 / 123 / 109 / 48 (s1), 167 / 149 / 106 / 90 (s2); certified elicited at K_total 21 / 29 / 41
/ 32 %, 33 / 24 / 34 / 42 %, 25 / 22 / 34 / 34 %; replay-only from the same start solves 83 / 63 / 66 / 53 %, 84 / 62
/ 72 / 56 %, 83 / 69 / 73 / 61 %; net 31 / 43 / 29 / 36, 25 / 47 / 30 / 21, 29 / 46 / 29 / 35.

**J10** (long pool `transfer_long2`, 21 theorems; pend 16,384 more attempts on the theorems r8 or r16 solves at x0 and
pend fails at x2): 9 / 13, 10 / 16, 10 / 16 get ≥ 1 success (29 / 45).

**IRT** (`cd_irt.py` → `out/irt_c12.txt`; `cd_irt_matched.py` → `out/irt_matched.txt`): θ (pend = 0) r8 2.10 / 1.91 /
2.18, r16 2.45 / 2.34 / 2.24; replay-only r8 0.55 / 0.70 / 0.64; J7 ⟨⟩. Matched placebo from p5000: EI r2 created 48 /
41 / 48 at Δθ 2.33 / 2.05 / 2.69; replay-only r8 50 / 49 / 54 at Δθ 2.12 / 2.09 / 2.14.

**J7** (`artifacts/cd/j7/`): ⟨J7⟩

**J9** (`artifacts/cd/j9/`): ⟨J9⟩

**Compute per job family** (results registry rows, `cd_compute.py` → `out/compute.txt`; A40): ⟨compute⟩

**Spend:** ⟨spend⟩. **Bucket:** ⟨bucket⟩.

