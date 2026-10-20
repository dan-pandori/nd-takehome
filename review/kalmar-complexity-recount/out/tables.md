
<!-- py -->

| program (hand-golfed Python) | raw bytes | raw DEFLATE | gzip -9 | raw xz (9e) | Qwen3 tokens | GPT-2 tokens |
|---|---:|---:|---:|---:|---:|---:|
| K-sl algorithm | 1,907 | 864 | 882 | 906 | 897 | 1,195 |
| K-sl render ND | 465 | 293 | 311 | 321 | 244 | 308 |
| K-sl render lean_seq | 977 | 562 | 580 | 596 | 475 | 615 |
| parse | 251 | 153 | 171 | 162 | 122 | 156 |
| K-sl alg + lean_seq render | 2,884 | 1,347 | 1,365 | 1,381 | 1,372 | 1,810 |
| K-sl alg + ND render | 2,372 | 1,093 | 1,111 | 1,137 | 1,141 | 1,503 |
| K-tt algorithm | 749 | 378 | 396 | 394 | 377 | 491 |
| K-tt render Lean | 1,024 | 571 | 589 | 600 | 514 | 655 |
| K-tt alg + Lean render | 1,773 | 866 | 884 | 880 | 891 | 1,146 |
| K-sl per-step policy kpol | 3,794 | 1,654 | 1,672 | 1,658 | 1,838 | 2,387 |
| calib copy | 13 | 15 | 33 | 17 | 5 | 7 |
| calib reverse | 19 | 21 | 39 | 23 | 7 | 12 |
| calib parity | 20 | 22 | 40 | 24 | 9 | 12 |
| calib parity_nb | 42 | 43 | 61 | 46 | 20 | 23 |
| calib sort | 9 | 11 | 29 | 13 | 4 | 5 |
| calib sort_nb | 94 | 87 | 105 | 100 | 40 | 55 |
| calib add | 17 | 19 | 37 | 21 | 7 | 11 |
| calib add_nb | 116 | 100 | 118 | 113 | 60 | 79 |
| calib eval | 138 | 105 | 123 | 115 | 74 | 88 |
| calib taut | 320 | 222 | 240 | 239 | 152 | 188 |

<!-- blc -->

| program | BLC bits | binary CL bits (own bracket abstraction) | CL / BLC | fresh-sample check |
|---|---:|---:|---:|---|
| parse (prompt word → sequent) | 800 | 2,900 | 3.6 | 1000/1000 |
| K-sl algorithm | 5,443 | 23,921 | 4.4 | 1000/1000 (alone); 1000/1000 end to end |
| K-sl rendering (ND) | 616 | 3,776 | 6.1 | 1000/1000 end to end |
| K-tt algorithm | 1,636 | 7,442 | 4.5 | 1000/1000 end to end |
| K-tt rendering (Lean) | 4,204 | 24,245 | 5.8 | 1000/1000 end to end |
| K-sl algorithm + rendering (+ parse) | 6,059 (6,859) | 27,697 (30,597) | | |
| K-tt algorithm + rendering (+ parse) | 5,840 (6,640) | 31,687 (34,587) | | |
| calibration copy | 4 | 8 | 2.0 | 300/300 own random cases |
| calibration reverse | 87 | 197 | 2.3 | 300/300 own random cases |
| calibration parity | 82 | 185 | 2.3 | 300/300 own random cases |
| calibration add | 375 | 1,163 | 3.1 | 300/300 own random cases |
| calibration sort | 257 | 749 | 2.9 | 300/300 own random cases |
| calibration eval | 273 | 713 | 2.6 | 300/300 own random cases |
| calibration taut | 410 | 1,430 | 3.5 | 300/300 own random cases |

<!-- b1 -->

| model | N loss tokens / epoch (own count) | pairs | curve points in epoch 1 | L_preq bits (interval mean) | bits/token | L_preq, next-point variant | EDL (a) final train | EDL (b) final held-out | EDL (c) end-of-epoch-1 train |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KAL-D s0 | 255,006,351 | 16,876,247 | 17 | 1.26e+07 | 0.0492 | 1.14e+07 | 6.97e+06 | 6.54e+06 | 1.67e+06 |
| KAL-D s1 | 255,006,351 | 16,876,247 | 17 | 1.24e+07 | 0.0488 | 1.13e+07 | 6.78e+06 | 6.27e+06 | 2.09e+06 |
| KAL-D s2 | 255,006,351 | 16,876,247 | 16 | 1.24e+07 | 0.0487 | 1.12e+07 | 7.31e+06 | 7.06e+06 | 2.12e+06 |
| control s0 | 19,375,057 | 1,239,995 | 12 | 3.79e+06 | 0.1955 | 2.56e+06 | 2.55e+06 | 1.47e+06 | 1.45e+06 |
| control s1 | 19,375,057 | 1,239,995 | 12 | 3.64e+06 | 0.1877 | 2.45e+06 | 1.93e+06 | 1.7e+06 | 1.57e+06 |
| control s2 | 19,375,057 | 1,239,995 | 12 | 3.87e+06 | 0.1997 | 2.59e+06 | 2.63e+06 | 1.61e+06 | 1.35e+06 |

<!-- b2 -->

| job | task | size | seed | protocol | L_preq bits | N loss tokens | L∞ bits/token | EDL bits | block-0 share of L / of EDL | at 8,192 thm: L / EDL | blocks at the step cap | training GPU-h (sum of block `secs`) |
|---|---|---|---:|---|---:|---:|---:|---:|---|---|---:|---:|
| eval_L_s0 | eval | L | 0 | v1 (4 evals) | 2.227e+05 | 524,288 | 0.1051 | 1.676e+05 | 0.06 / 0.08 | 1.194e+05 / 1.615e+04 | 5/9 | 1.18 |
| k12_L_s0 | k12 | L | 0 | v1 (4 evals) | 3.873e+05 | 2,055,332 | 0.1012 | 1.792e+05 | 0.14 / 0.29 | 2.7e+05 / 1.538e+05 | 4/9 | 1.39 |
| kal_L_s0 | kal | L | 0 | v1 (4 evals) | 1.374e+06 | 13,541,714 | 0.0233 | 1.059e+06 | 0.56 / 0.73 | 1.374e+06 / 1.059e+06 | 3/8 | 3.22 |
| kal_M_s0 | kal | M | 0 | v1 (4 evals) | 1.69e+06 | 27,100,176 | 0.0217 | 1.102e+06 | 0.46 / 0.70 | 1.395e+06 / 1.1e+06 | 4/9 | 2.76 |
| kal_M_s1 | kal | M | 1 | v1 (4 evals) | 1.771e+06 | 27,100,176 | 0.0255 | 1.078e+06 | 0.44 / 0.71 | 1.444e+06 / 1.118e+06 | 5/9 | 1.86 |
| kal_S_s0 | kal | S | 0 | v1 (4 evals) | 3.369e+06 | 27,100,176 | 0.0756 | 1.319e+06 | 0.23 / 0.58 | 2.346e+06 / 1.325e+06 | 5/9 | 1.28 |
| kal_S_s1 | kal | S | 1 | v1 (4 evals) | 3.375e+06 | 27,100,176 | 0.0708 | 1.457e+06 | 0.23 / 0.52 | 2.436e+06 / 1.497e+06 | 5/9 | 0.99 |
| v2_eval_L_s0 | eval | L | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 1.717e+05 | 524,288 | 0.1051 | 1.166e+05 | 0.08 / 0.12 | 1.07e+05 / 4.233e+04 | 9/9 | 1.94 |
| v2_eval_M_s0 | eval | M | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 1.631e+05 | 524,288 | 0.0241 | 1.505e+05 | 0.09 / 0.09 | 9.548e+04 / 2.79e+04 | 9/9 | 1.18 |
| v2_eval_S_s0 | eval | S | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 1.772e+05 | 524,288 | 0.1887 | 7.824e+04 | 0.08 / 0.17 | 1.033e+05 / 2.951e+04 | 9/9 | 0.45 |
| v2_k12_L_s0 | k12 | L | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 3.877e+05 | 2,055,332 | 0.1014 | 1.793e+05 | 0.14 / 0.29 | 2.692e+05 / 1.518e+05 | 7/9 | 2.00 |
| v2_k12_M_s0 | k12 | M | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 4.234e+05 | 2,055,332 | 0.0998 | 2.183e+05 | 0.12 / 0.24 | 3.004e+05 / 1.784e+05 | 7/9 | 1.23 |
| v2_k12_S_s0 | k12 | S | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 6.449e+05 | 2,055,332 | 0.1574 | 3.215e+05 | 0.08 / 0.16 | 4.654e+05 / 2.876e+05 | 9/9 | 0.60 |

<!-- b3 -->

| quantity | STD s0 / s1 / s2 | FOC s0 / s1 / s2 | 3-seed means STD → FOC | relative change (of means; per seed) |
|---|---|---|---|---|
| opener-state error (23,573 states) | 0.3349 / 0.3079 / 0.3160 | 0.0154 / 0.0232 / 0.0196 | 0.3196 → 0.0194 | -0.939; -0.954, -0.925, -0.938 |
| other-state error (114,411) | 0.0248 / 0.0194 / 0.0289 | 0.0161 / 0.0183 / 0.0165 | 0.0244 → 0.0170 | -0.303; -0.349, -0.058, -0.429 |
| all states | 0.0777 / 0.0687 / 0.0780 | 0.0160 / 0.0191 / 0.0170 | 0.0748 → 0.0174 | -0.768; -0.794, -0.722, -0.782 |
| other states without `pr` | 0.0167 / 0.0113 / 0.0210 | 0.0081 / 0.0103 / 0.0085 | 0.0163 → 0.0089 | -0.453; -0.518, -0.087, -0.597 |
| `pr` states (1,409) | 0.669 / 0.671 / 0.664 | 0.662 / 0.659 / 0.663 | | |

| step type | states | opener states | STD error (mean) | FOC error (mean) | relative change | mean `explored` |
|---|---:|---:|---:|---:|---:|---:|
| close | 44,290 | 0 | 0.0044 | 0.0019 | -0.56 | 0.23 |
| efq | 9,286 | 0 | 0.0167 | 0.0072 | -0.57 | 1.00 |
| end | 1,200 | 0 | 0.0233 | 0.0183 | -0.21 | 0.00 |
| leaf:and+ | 1,427 | 1,427 | 0.4681 | 0.0315 | -0.93 | 4.43 |
| leaf:and- | 9,336 | 3,112 | 0.0975 | 0.0088 | -0.91 | 1.20 |
| leaf:bot- | 639 | 639 | 0.3672 | 0.0000 | -1.00 | 3.45 |
| leaf:imp+A | 5,295 | 1,765 | 0.1324 | 0.0254 | -0.81 | 1.18 |
| leaf:imp+B | 11,908 | 5,954 | 0.1590 | 0.0205 | -0.87 | 1.48 |
| leaf:imp- | 6,240 | 2,080 | 0.1170 | 0.0129 | -0.89 | 1.25 |
| leaf:not+ | 5,884 | 2,942 | 0.1801 | 0.0039 | -0.98 | 1.79 |
| leaf:or+ | 4,520 | 4,520 | 0.3174 | 0.0360 | -0.89 | 3.24 |
| leaf:or- | 4,536 | 1,134 | 0.1132 | 0.0167 | -0.85 | 1.22 |
| lem | 23,086 | 0 | 0.0239 | 0.0149 | -0.38 | 0.00 |
| pr | 1,409 | 0 | 0.6681 | 0.6615 | -0.01 | 0.00 |
| split | 8,900 | 0 | 0.0336 | 0.0112 | -0.67 | 0.00 |

Spearman across the 15 types of error vs mean `explored`: STD_0 +0.60 (p 0.021); STD_1 +0.63 (p 0.015); STD_2 +0.62 (p 0.017); STD_mean +0.61 (p 0.020); FOC_0 -0.11 (p 0.695); FOC_1 -0.08 (p 0.776); FOC_2 -0.13 (p 0.633); FOC_mean -0.02 (p 0.947)

Training steps / cap (best validation step): FOC_s0 20,000/20,000 (best 19,000), FOC_s1 20,000/20,000 (best 20,000), FOC_s2 20,000/20,000 (best 20,000), STD_s0 20,000/20,000 (best 19,000), STD_s1 20,000/20,000 (best 20,000), STD_s2 20,000/20,000 (best 20,000)

<!-- q4 -->

| step type | states | KAL-D s0 / s1 / s2 error | mean | KAL-D+A mean | KAL-C s0 |
|---|---:|---|---:|---:|---:|
| close | 44,290 | 0.0035 / 0.0142 / 0.0064 | 0.0081 | 0.0015 | 0.0113 |
| efq | 9,286 | 0.0141 / 0.0181 / 0.0162 | 0.0161 | 0.0021 | 0.0074 |
| end | 1,200 | 0.0042 / 0.0192 / 0.0058 | 0.0097 | 0.0039 | 0.0100 |
| leaf:and+ | 1,427 | 0.3959 / 0.3854 / 0.2558 | 0.3457 | 0.1023 | 0.3840 |
| leaf:and- | 9,336 | 0.0679 / 0.1065 / 0.1016 | 0.0920 | 0.0302 | 0.0978 |
| leaf:bot- | 639 | 0.3599 / 0.2300 / 0.1847 | 0.2582 | 0.1064 | 0.2426 |
| leaf:imp+A | 5,295 | 0.1027 / 0.1095 / 0.1058 | 0.1060 | 0.0258 | 0.1246 |
| leaf:imp+B | 11,908 | 0.1816 / 0.1689 / 0.1460 | 0.1655 | 0.0255 | 0.1704 |
| leaf:imp- | 6,240 | 0.0712 / 0.0822 / 0.0787 | 0.0774 | 0.0161 | 0.1276 |
| leaf:not+ | 5,884 | 0.0785 / 0.1074 / 0.0901 | 0.0920 | 0.0249 | 0.1547 |
| leaf:or+ | 4,520 | 0.2770 / 0.2854 / 0.2095 | 0.2573 | 0.0715 | 0.2657 |
| leaf:or- | 4,536 | 0.0725 / 0.1052 / 0.0754 | 0.0844 | 0.0240 | 0.0836 |
| lem | 23,086 | 0.0014 / 0.0094 / 0.0015 | 0.0041 | 0.0000 | 0.0022 |
| pr | 1,409 | 0.1299 / 0.0688 / 0.0575 | 0.0854 | 0.0007 | 0.0525 |
| split | 8,900 | 0.0343 / 0.0226 / 0.0330 | 0.0300 | 0.0023 | 0.0227 |

| predictor (per step type, n = 15) | source | ρ vs KAL-D mean error (perm. p) | s0 / s1 / s2 | vs KAL-D+A mean | partial ρ given log frequency (p) |
|---|---|---|---|---|---|
| b2_bits_per_occ_S | own | +0.85 (0.000) | +0.91 / +0.83 / +0.84 | +0.60 | +0.78 (0.001) |
| exec_rasp_eff_depth | executor (`rasp_per_type.json`) | +0.85 (0.000) | +0.74 / +0.87 / +0.89 | +0.90 | +0.85 (0.000) |
| exec_rasp_cone_depth | executor (`rasp_per_type.json`) | +0.84 (0.000) | +0.75 / +0.89 / +0.91 | +0.91 | +0.84 (0.000) |
| b2_bits_per_occ_L | own | +0.84 (0.000) | +0.93 / +0.80 / +0.80 | +0.55 | +0.75 (0.003) |
| b2_bits_per_occ_M | own | +0.82 (0.001) | +0.92 / +0.77 / +0.77 | +0.52 | +0.71 (0.004) |
| exec_rasp_cone_ops | executor (`rasp_per_type.json`) | +0.82 (0.000) | +0.73 / +0.87 / +0.89 | +0.89 | +0.81 (0.000) |
| explored | own | +0.82 (0.000) | +0.77 / +0.86 / +0.88 | +0.85 | +0.79 (0.000) |
| exec_log2_ops | executor (`states_tf1200`, policy ops) | +0.78 (0.001) | +0.69 / +0.81 / +0.82 | +0.84 | +0.76 (0.001) |
| target_h | own | +0.78 (0.001) | +0.72 / +0.79 / +0.83 | +0.79 | +0.78 (0.001) |
| tree_path | own | -0.76 (0.002) | -0.65 / -0.80 / -0.82 | -0.85 | -0.71 (0.002) |
| log_freq | own | -0.60 (0.018) | -0.68 / -0.61 / -0.50 | -0.56 | — |
| py_bytes | own | -0.55 (0.038) | -0.62 / -0.52 / -0.46 | -0.43 | -0.08 (0.771) |
| act_len | own | +0.52 (0.049) | +0.55 / +0.55 / +0.55 | +0.33 | +0.59 (0.019) |
| focus_h | own | +0.49 (0.069) | +0.44 / +0.59 / +0.62 | +0.50 | +0.59 (0.016) |
| decl_len | own | +0.42 (0.121) | +0.47 / +0.39 / +0.43 | +0.15 | +0.53 (0.041) |
| depth | own | +0.27 (0.332) | +0.16 / +0.34 / +0.39 | +0.39 | +0.48 (0.066) |
| exec_rasp_descent | executor (`rasp_per_type.json`) | +0.25 (0.364) | +0.29 / +0.20 / +0.12 | +0.18 | -0.19 (0.503) |

State level (logistic regression, type dummies ± 6 standardised demand measures, LR test, df 6): kalD_s0 LR 6,530 (p 0); best single: explored 5,751, target_h 4,884, act_len 1,764; kalD_s1 LR 7,502 (p 0); best single: explored 6,374, target_h 4,852, act_len 2,315; kalD_s2 LR 5,888 (p 0); best single: explored 4,936, target_h 4,057, act_len 1,767

Per-state measures equal to the executor's on all 137,984 states: explored 137,984, focus_h 137,984, target_h 137,984, decl_len 137,984, act_len 137,984, depth 137,984
