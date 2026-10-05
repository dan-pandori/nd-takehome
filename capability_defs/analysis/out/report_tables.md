## created sets

| definition (card) | r8, x0: s0 / s1 / s2 | net of replay-only | r16, x1 | redraw Jaccard (r8) | seed Jaccard (r8, pairs) |
|---|---|---|---|---|---|
| equal-k (`passk-equal-k`) | 54 / 51 / 60 | 37 / 27 / 33 | 61 / 65 / 61 | 0.78 / 0.70 / 0.68 | 0.35 / 0.39 / 0.34 |
| compute-matched (`passk-budget`) | 22 / 21 / 14 | 20 / 14 / 8 | 25 / 34 / 17 | 0.84 / 0.86 / 0.87 | 0.19 / 0.16 / 0.25 |
| … of which 0 base successes | 18 / 17 / 8 | 17 / 11 / 5 | 22 / 30 / 11 | 0.85 / 0.83 / 0.78 | 0.21 / 0.18 / 0.14 |
| cm, no seed's base ever solves t | 4 / 5 / 5 | 4 / 3 / 5 | 6 / 15 / 8 | 0.80 / 0.80 / 0.67 | 0.29 / 0.29 / 0.43 |
| cm, J7 continuation fails t (draw x0) | 18 / 17 / 14 | 17 / 13 / 8 | 22 / 32 / 16 | 0.81 / 0.84 / 0.80 | 0.17 / 0.14 / 0.24 |
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

## coverage

| seed | base within reach at K_eval-set (r8 / r16 budget) | replay-only r8, k 256 | J7 continuation, k 256 | r8, k 256 | r16, k 256 | Δ_cov r8 / r16 |
|---|---|---|---|---|---|---|
| s0 | 265 / 267 | 239 | 220 | 286 | 291 | +21 / +24 |
| s1 | 270 / 271 | 244 | 215 | 286 | 303 | +16 / +32 |
| s2 | 281 / 281 | 249 | 219 | 293 | 295 | +12 / +14 |

## bracket verdicts at K_eval-set

| r8-solved hard theorems, verdict at K_eval-set | s0 | s1 | s2 |
|---|---|---|---|
| RL-solved hard theorems | 55 | 45 | 52 |
| elicited: sampling lower bound ≥ 1 / K | 17 | 17 | 21 |
| elicited: known-proof estimate ≥ 2 / K | 5 | 1 | 3 |
| base found it, but not certifiably within reach | 12 | 9 | 18 |
| not reached: 0 base successes in ≥ K attempts | 21 | 18 | 10 |
| undetermined (0 successes, fewer than K attempts) | 0 | 0 | 0 |
| certified created (UB95 < 0.05 / K) | 3 | 2 | 2 |

## threshold sensitivity

| threshold (r8, x0) | s0 | s1 | s2 |
|---|---|---|---|
| cm at K = 0.1 × K_eval-set | 38 | 36 | 36 |
| tfmax at K = 0.1 × K_eval-set | 42 | 41 | 42 |
| brk_ne at K = 0.1 × K_eval-set | 43 | 40 | 37 |
| cm at K = 0.3 × K_eval-set | 33 | 28 | 28 |
| tfmax at K = 0.3 × K_eval-set | 34 | 34 | 32 |
| brk_ne at K = 0.3 × K_eval-set | 36 | 34 | 32 |
| cm at K = 1 × K_eval-set | 22 | 21 | 14 |
| tfmax at K = 1 × K_eval-set | 29 | 27 | 24 |
| brk_ne at K = 1 × K_eval-set | 29 | 26 | 25 |
| cm at K = 3 × K_eval-set | 21 | 20 | 3 (6 undet.) |
| tfmax at K = 3 × K_eval-set | 26 | 24 | 21 |
| brk_ne at K = 3 × K_eval-set | 25 | 23 | 19 |
| equal-k, base sample: 256 (x0) | 54 | 51 | 60 |
| equal-k, base sample: 512 (x0+x1) | 50 | 42 | 49 |
| equal-k, base sample: all reads | 47 | 40 | 43 |
| reliable, p̂_R ≥ q (within cm): 0.1 | 13 | 14 | 11 |
| reliable, p̂_R ≥ q (within cm): 0.25 | 12 | 11 | 8 |
| reliable, p̂_R ≥ q (within cm): 0.5 | 12 | 9 | 5 |
| reliable, p̂_R ≥ q (within cm): 0.75 | 9 | 6 | 5 |
| expansion share ρ ≥ q: 0.25 | 50 | 42 | 48 |
| expansion share ρ ≥ q: 0.5 | 48 | 42 | 46 |
| expansion share ρ ≥ q: 0.75 | 44 | 39 | 40 |
| expansion share ρ ≥ q: 0.9 | 37 | 38 | 36 |
| schema, pend ≤ lo / RL ≥ hi: 0.0/0.3 | 3 | 2 | 0 |
| schema, pend ≤ lo / RL ≥ hi: 0.0/0.5 | 0 | 2 | 0 |
| schema, pend ≤ lo / RL ≥ hi: 0.0/0.7 | 0 | 0 | 0 |
| schema, pend ≤ lo / RL ≥ hi: 0.05/0.3 | 3 | 2 | 0 |
| schema, pend ≤ lo / RL ≥ hi: 0.05/0.5 | 0 | 2 | 0 |
| schema, pend ≤ lo / RL ≥ hi: 0.05/0.7 | 0 | 0 | 0 |
| schema, pend ≤ lo / RL ≥ hi: 0.1/0.3 | 3 | 2 | 0 |
| schema, pend ≤ lo / RL ≥ hi: 0.1/0.5 | 0 | 2 | 0 |
| schema, pend ≤ lo / RL ≥ hi: 0.1/0.7 | 0 | 0 | 0 |

## plain vs guided

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

## J9

| seed | theorem | r8 pass@1 (x0) | own base: successes / attempts | known-proof estimate | UB95 vs 0.05 / K_eval-set | certified at K_eval-set? | other seeds' bases | replay-only (512) | J7 continuation (512) |
|---|---|---|---|---|---|---|---|---|---|
| s0 | `la_transfer_2060` | 0.95 | 0 / 1,245,952 | 10^-7.9 | 2.4e-06 vs 2.6e-06 | yes | s1 0 / 1,377,024, s2 0 / 1,508,096 | 0 / 512 | 7 / 512 |
| s0 | `la_transfer_205` | 0.79 | 0 / 1,245,952 | 10^-13.2 | 2.4e-06 vs 2.6e-06 | yes | s1 0 / 66,560, s2 0 / 17,408 | 0 / 512 | 0 / 512 |
| s0 | `la_transfer_1077` | 0.62 | 0 / 1,245,952 | 10^-8.8 | 2.4e-06 vs 2.6e-06 | yes | s1 1 / 1,377,024, s2 0 / 66,304 | 0 / 512 | 0 / 512 |
| s1 | `la_transfer_1648` | 0.95 | 0 / 1,377,024 | 10^-8.1 | 2.2e-06 vs 2.4e-06 | yes | s0 5 / 66,304, s2 1 / 1,114,880 | 0 / 512 | 0 / 512 |
| s1 | `la_transfer_1077` | 0.80 | 1 / 1,377,024 | 10^-7.7 | 3.4e-06 vs 2.4e-06 | no: base found it | s0 0 / 1,245,952, s2 0 / 66,304 | 0 / 512 | 0 / 512 |
| s1 | `la_transfer_2060` | 0.61 | 0 / 1,377,024 | 10^-12.7 | 2.2e-06 vs 2.4e-06 | yes | s0 0 / 1,245,952, s2 0 / 1,508,096 | 0 / 512 | 0 / 512 |
| s2 | `la_transfer_1648` | 0.91 | 1 / 1,114,880 | 10^-6.2 | 4.3e-06 vs 2.1e-06 | no: base found it | s0 5 / 66,304, s1 0 / 1,377,024 | 0 / 512 | 0 / 512 |
| s2 | `la_transfer_1833` | 0.82 | 0 / 1,508,096 | 10^-10.2 | 2.0e-06 vs 2.1e-06 | yes | s0 0 / 17,408, s1 0 / 17,408 | 0 / 512 | 0 / 512 |
| s2 | `la_transfer_2060` | 0.30 | 0 / 1,508,096 | 10^-12.4 | 2.0e-06 vs 2.1e-06 | yes | s0 0 / 1,245,952, s1 0 / 1,377,024 | 0 / 512 | 0 / 512 |

## compute

| job | A40-hours (process level) | attempts | generated tokens | training tokens | Lean checks |
|---|---|---|---|---|---|
| J1 teacher-forced scores (stage 1 + 2) | 2.1 | 0.00 M | 0 M | 0.00 B | 0 |
| J2 stage A + calibration | 4.0 | 3.17 M | 469 M | 0.00 B | 10,509 |
| J2 stages A', B, truncation | 6.6 | 5.55 M | 752 M | 0.00 B | 60 |
| J3 guided reads (both caps) | 9.1 | 1.57 M | 513 M | 0.00 B | 641,571 |
| J4 demonstration fine-tunes + reads | 2.2 | 0.28 M | 55 M | 0.72 B | 53,450 |
| J5 missing plain draws | 1.9 | 0.44 M | 121 M | 0.00 B | 265,013 |
| J6 no-DN knockout pretraining + fine-tunes + reads | 2.4 | 0.35 M | 62 M | 1.70 B | 64,284 |
| J6b DN-free-replay fine-tunes + reads | 3.0 | 0.25 M | 46 M | 1.38 B | 19,457 |
| J7 compute-matched continuation + reads | 17.9 | 0.49 M | 87 M | 9.32 B | 55,606 |
| J8 start-dependence scores | 4.5 | 0.00 M | 0 M | 0.00 B | 0 |
| J9 certification sampling | 21.3 | 11.40 M | 2,122 M | 0.00 B | 2 |
| J10 long-pool sampling | 1.9 | 0.87 M | 197 M | 0.00 B | 441 |
| **total** | **77.0** | 24.4 M | 4.43 B | 13.1 B | 1,110,393 |
