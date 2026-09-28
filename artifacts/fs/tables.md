| quantity | slice | legacy (C) mean | fast mean | Δ | MDD (n=8) | within |
|---|---|---|---|---|---|---|
| held-out greedy | all | 0.9105 | 0.9001 | -1.04 pp | 4.58 pp | yes |
| held-out greedy | len2 | 0.9960 | 0.9939 | -0.21 pp | 0.47 pp | yes |
| held-out greedy | len3 | 0.9864 | 0.9879 | 0.15 pp | 0.73 pp | yes |
| held-out greedy | len4 | 0.9469 | 0.9537 | 0.69 pp | 2.28 pp | yes |
| held-out greedy | len5 | 0.9135 | 0.9189 | 0.54 pp | 2.26 pp | yes |
| held-out greedy | len6 | 0.7096 | 0.6459 | -6.37 pp | 22.94 pp | yes |
| held-out greedy | nodepth3_len6 | 0.8770 | 0.8880 | 1.10 pp | 5.52 pp | yes |
| val loss | all | 0.05101 | 0.05124 | 0.00023 | 0.00219 | yes |
| val loss | len2 | 0.07817 | 0.07824 | 0.00007 | 0.00036 | yes |
| val loss | len3 | 0.06780 | 0.06780 | -0.00000 | 0.00045 | yes |
| val loss | len4 | 0.05139 | 0.05111 | -0.00028 | 0.00049 | yes |
| val loss | len5 | 0.03958 | 0.03964 | 0.00006 | 0.00077 | yes |
| val loss | len6 | 0.04238 | 0.04322 | 0.00084 | 0.00775 | yes |
| val loss | nodepth3_len6 | 0.04551 | 0.04533 | -0.00017 | 0.00084 | yes |
PASS | depth-3 high mode (>0.44): [4, 8] new vs [6, 8] C

| wave | gpu | impl | N | steps | wall s | s/model | ms/step/model | agg steps/s | agg useful tok/s | agg % bf16 peak (A40) | pad waste |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fast1 | NVIDIA A40 | fast | 1 | 6000 | 135 | 126 | 16.8 | 44.5 | 788k | 10.2 | 1.098 |
| fast2 | NVIDIA A40 | fast | 2 | 6000 | 251 | 236 | 35.2 | 47.8 | 846k | 10.9 | 1.113 |
| fast4 | NVIDIA A40 | fast | 4 | 6000 | 484 | 475 | 74.3 | 49.6 | 879k | 11.3 | 1.098 |
| fast1b | NVIDIA A40 | fast | 1 | 6000 | 128 | 119 | 17.3 | 46.9 | 830k | 10.7 | 1.113 |
| thr8 | NVIDIA A40 | fast | 8 | 2000 | 335 | 324 | 147.7 | 47.7 | 845k | 10.9 | 1.084 |
| leg1 | NVIDIA A40 | legacy | 1 | 1000 | 84 | 53 | 49.2 | 11.9 | 236k | 3.0 | 2.002 (legacy) |
| leg2 | NVIDIA A40 | legacy | 2 | 1000 | 143 | 109 | 103.4 | 14.0 | 276k | 3.6 | 2.002 (legacy) |
| leg4 | NVIDIA A40 | legacy | 4 | 1000 | 257 | 223 | 214.3 | 15.6 | 308k | 4.0 | 2.002 (legacy) |
| legfull | NVIDIA A40 | legacy | 1 | 6000 | 345 | 313 | 48.9 | 17.4 | 344k | 4.4 | 2.002 (legacy) |
| a40_fast1 | NVIDIA A40 | fast | 1 | 2000 | 56 | 46 | 16.6 | 35.7 | 633k | 8.2 | 1.084 |
| a40_bs512 | NVIDIA A40 | fast | 1 | 500 | 63 | 54 | 64.0 | 8.0 | 564k | 7.3 | 1.037 |
| a40_fast2 | NVIDIA A40 | fast | 2 | 2000 | 95 | 85 | 36.2 | 42.1 | 745k | 9.6 | 1.084 |
| a40_leg1 | NVIDIA A40 | legacy | 1 | 500 | 59 | 27 | 50.3 | 8.5 | 168k | 2.2 | 2.002 (legacy) |
| h100_fast1 | NVIDIA H100 80GB HBM3 | fast | 1 | 2000 | 31 | 24 | 4.1 | 64.9 | 1150k | — | 1.098 |
| h100_bs512 | NVIDIA H100 80GB HBM3 | fast | 1 | 500 | 29 | 22 | 12.2 | 17.5 | 1242k | — | 1.037 |
| h100_fast2 | NVIDIA H100 80GB HBM3 | fast | 2 | 2000 | 32 | 26 | 8.6 | 125.0 | 2216k | — | 1.098 |
| h100_leg1 | NVIDIA H100 80GB HBM3 | legacy | 1 | 500 | 44 | 16 | 30.0 | 11.3 | 223k | — | 2.002 (legacy) |
| h100_fast4 | NVIDIA H100 80GB HBM3 | fast | 4 | 2000 | 60 | 52 | 16.6 | 133.0 | 2356k | — | 1.084 |
| h100_fast8 | NVIDIA H100 80GB HBM3 | fast | 8 | 2000 | 89 | 79 | 32.9 | 179.2 | 3174k | — | 1.098 |
| h100_fast16 | NVIDIA H100 80GB HBM3 | fast | 16 | 2000 | 170 | 158 | 70.0 | 188.0 | 3331k | — | 1.098 |
