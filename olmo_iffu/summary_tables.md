### Test 1

| prompt | budget | cut | finished length q1 / median / q3 / max | credited any / doubly | sound any / doubly | `dpo` sound rate [95 %] | credited at 32,768 | label |
|---|---|---|---|---|---|---|---|---|
| perp_055 | 65290 | 0 / 64 | 43876 / 46865 / 50339 / 56969 | 2 / 1 | 1 / 1 | 0.016 [0.0004, 0.084] | 0 | one sound success |
| perp_068 | 65290 | 1 / 64 | 42458 / 45521 / 49030 / 57305 | 3 / 2 | 3 / 2 | 0.047 [0.0098, 0.131] | 0 | token budget |
| perp_069 | 65317 | 0 / 64 | 40191 / 45299 / 48426 / 60638 | 4 / 2 | 2 / 1 | 0.031 [0.0038, 0.108] | 0 | token budget |

### Test 2 / 2c (hint)

| prompt | set | `dpo` strict / 64 | `dpo` genuine (read) | `dpo` words: unhinted → hinted (median) | `s2300` strict / 16 | `s2300` genuine (read) | `s2300` words unhinted → hinted | label |
|---|---|---|---|---|---|---|---|---|
| ifeval_2350 | 2 | 0 | 0 (0) | 194.0 → 60.0 | 16 | 2 (2) | 11.5 → 13.5 | not elicited by the hint |
| ifeval_2447 | 2 | 2 | 2 (2) | 191.0 → 49.5 | 14 | 2 (2) | 35.0 → 20.0 | prompt-elicitable (brevity) |
| ifeval_3478 | 2 | 0 | 0 (0) | 218.0 → 59.0 | 15 | 2 (4) | 49.0 → 10.5 | not elicited by the hint |
| ifeval_1314 | 2 | 19 | 3 (3) | 370.5 → 68.5 | 12 | 2 (2) | 48.0 → 25.0 | prompt-elicitable (brevity) |
| ifeval_2247 | 2 | 29 | 3 (3) | 570.5 → 64.0 | 16 | 2 (2) | 275.5 → 43.5 | prompt-elicitable (brevity) |
| ifeval_2563 | 2 | 5 | 3 (3) | 199.5 → 58.5 | 15 | 2 (2) | 42.5 → 36.5 | prompt-elicitable (brevity) |
| ifbench_290 | 2 | 3 | 2 (3) | 600.0 → 94.5 | 13 | 2 (2) | 161.0 → 39.0 | prompt-elicitable (brevity) [literal reading; strict: not elicited] |
| ifbench_4 | 2 | 0 | 0 (0) | 431.0 → 83.0 | 15 | 1 (15) | 116.0 → 42.0 | not elicited; hint breaks s2300 |
| ifbench_64 | 2 | 0 | 0 (0) | 6.0 → 12.0 | 4 | 2 (2) | 9.0 → 9.0 | not elicited by the hint |
| ifbench_79 | 2 | 0 | 0 (0) | 526.5 → 64 | 14 | 2 (2) | 76.5 → 28.5 | not elicited by the hint |
| ifbench_170 | 2 | 0 | 0 (0) | 64.5 → 55.0 | 4 | 1 (4) | 20.5 → 14.5 | not elicited; hint breaks s2300 |
| ifbench_0 | 2 | 0 | 0 (0) | 438.5 → 67.0 | 14 | 0 (14) | 132.5 → 30.0 | not elicited; hint breaks s2300 |
| ifbench_188 | 2 | 0 | 0 (0) | 476.5 → 56.5 | 2 | 1 (2) | 71.5 → 35.0 | not elicited; hint breaks s2300 |
| ifbench_207 | 2 | 0 | 0 (0) | 366.5 → 61.0 | 6 | 2 (2) | 42.5 → 19.0 | not elicited by the hint |
| ifbench_179 | 2 | 2 | 2 (2) | 494.5 → 57.5 | 10 | 2 (4) | 18.0 → 10.5 | prompt-elicitable (brevity) |
| ifbench_268 | 2 | 0 | 0 (0) | 313.5 → 91.0 | 14 | 3 (4) | 20.0 → 11.0 | not elicited by the hint |
| ifbench_252 | 2c | 36 | 3 (3) | 708.5 → 73.0 | 16 | 2 (2) | 28.0 → 23.5 | prompt-elicitable (brevity) |
| ifbench_269 | 2c | 0 | 0 (0) | 133.0 → 65.5 | 13 | 2 (2) | 20.5 → 18.0 | not elicited by the hint |
| ifbench_253 | 2c | 43 | 3 (3) | 616.0 → 91.0 | 16 | 2 (2) | 55.0 → 30.0 | prompt-elicitable (brevity) |
| ifbench_3 | 2c | 0 | 0 (0) | 582.0 → 122.0 | 12 | 0 (12) | 360.0 → 40.5 | not elicited; hint breaks s2300 |
| ifbench_78 | 2c | 16 | 2 (5) | 607.0 → 64.5 | 12 | 2 (2) | 79.5 → 30.5 | prompt-elicitable (brevity) |
| ifbench_248 | 2c | 0 | 0 (0) | 258.0 → 46.0 | 16 | 2 (2) | 16.5 → 15.5 | not elicited by the hint |
| ifbench_211 | 2c | 1 | 1 (1) | 138.0 → 42.5 | 11 | 2 (2) | 10.0 → 6.5 | one genuine with the hint |
| ifbench_166 | 2c | 0 | 0 (0) | 67.0 → 51.0 | 9 | 0 (9) | 16.5 → 11.0 | not elicited; hint breaks s2300 |
| ifbench_136 | 2c | 1 | 1 (1) | 320.5 → 60.0 | 14 | 2 (5) | 54.0 → 26.0 | one genuine with the hint |
| ifbench_133 | 2c | 5 | 2 (3) | 424.5 → 87.0 | 16 | 2 (2) | 93.0 → 35.5 | prompt-elicitable (brevity) |
| ifbench_1 | 2c | 0 | 0 (0) | 243.0 → 61.0 | 12 | 1 (12) | 90.5 → 32.0 | not elicited; hint breaks s2300 |
| ifbench_19 | 2c | 2 | 2 (2) | 229.0 → 78.0 | 2 | 2 (2) | 49.0 → 36.0 | prompt-elicitable (brevity) |
| ifbench_67 | 2c | 0 | 0 (0) | 408.0 → 68.5 | 15 | 4 (5) | 117.5 → 32.5 | not elicited by the hint |
| ifbench_128 | 2c | 0 | 0 (0) | 292.0 → 83.5 | 12 | 2 (2) | 119.5 → 27.0 | not elicited by the hint |
| ifbench_154 | 2c | 0 | 0 (0) | 233.0 → 64.0 | 2 | 2 (2) | 16.5 → 12.0 | not elicited by the hint |
| ifbench_169 | 2c | 0 | 0 (0) | 68.5 → 55.5 | 10 | 2 (2) | 16.0 → 12.5 | not elicited by the hint |
| ifbench_173 | 2c | 4 | 3 (3) | 173.0 → 68.5 | 10 | 2 (2) | 8.5 → 11.0 | prompt-elicitable (brevity) |
| ifbench_186 | 2c | 2 | 2 (2) | 145.0 → 56.0 | 15 | 2 (2) | 40.5 → 24.0 | prompt-elicitable (brevity) |
| ifbench_187 | 2c | 2 | 2 (2) | 184.0 → 53.0 | 15 | 4 (5) | 28.0 → 55.0 | prompt-elicitable (brevity) |
| ifbench_189 | 2c | 0 | 0 (0) | 228.5 → 58.0 | 6 | 2 (2) | 42.0 → 40.0 | not elicited by the hint |
| ifbench_203 | 2c | 0 | 0 (0) | 193.0 → 56.0 | 13 | 5 (13) | 8.0 → 5.0 | not elicited by the hint |
| ifbench_204 | 2c | 2 | 1 (2) | 68.5 → 43.5 | 16 | 4 (5) | 24.5 → 14.0 | one genuine with the hint |
| ifbench_206 | 2c | 0 | 0 (0) | 172.5 → 49.0 | 13 | 5 (13) | 8.5 → 16.0 | not elicited by the hint |
| ifbench_209 | 2c | 0 | 0 (0) | 158.5 → 43.0 | 13 | 3 (5) | 9.5 → 8.5 | not elicited by the hint |
| ifbench_217 | 2c | 0 | 0 (0) | 207.0 → 51.0 | 10 | 4 (5) | 7.5 → 5.0 | not elicited by the hint |
| ifbench_220 | 2c | 8 | 3 (3) | 276.0 → 72.5 | 16 | 2 (2) | 48.5 → 31.0 | prompt-elicitable (brevity) |
| ifbench_226 | 2c | 9 | 3 (3) | 409.5 → 58.0 | 16 | 0 (5) | 20.0 → 9.0 | prompt-elicitable (brevity) |
| ifbench_264 | 2c | 0 | 0 (0) | 176.5 → 68.5 | 14 | 4 (5) | 22.0 → 13.5 | not elicited by the hint |
| ifbench_267 | 2c | 0 | 0 (0) | 154.0 → 56.0 | 16 | 3 (5) | 25.5 → 19.0 | not elicited by the hint |
| ifbench_271 | 2c | 0 | 0 (0) | 121.5 → 69.0 | 16 | 5 (16) | 24.0 → 16.0 | not elicited by the hint |
| ifbench_280 | 2c | 0 | 0 (0) | 140.5 → 38.5 | 7 | 2 (2) | 82.0 → 15.0 | not elicited by the hint |
| ifbench_284 | 2c | 0 | 0 (0) | 458.0 → 58.5 | 4 | 0 (4) | 4.0 → 4.0 | not elicited; hint breaks s2300 |

### Test 3

| prompt | new draws | strict | binding-constraint passes | genuine in 1,024 | one-sided 95 % bound |
|---|---|---|---|---|---|
| ifbench_133 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |
| ifbench_136 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |
| ifbench_166 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |
| ifbench_211 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |
| ifbench_248 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |
| ifbench_252 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |
| ifbench_253 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |
| ifbench_269 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |
| ifbench_3 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |
| ifbench_78 | 768 | 0 | see log | 0 / 1,024 | 0.00292 |

### Test 4
 {'': 9, 's0750 confirmed': 26, 's0750 not confirmed': 17}

### Compute (job metas)

| job | samples | tokens | t_load + t_gen (s) | tp | tok/s |
|---|---|---|---|---|---|
| T1_dpo | 192 | 8.80 M | 132 + 5006 | 2 | 1758 |
| T2_dpo | 1,024 | 3.40 M | 313 + 886 | 2 | 3843 |
| T2_s2300 | 256 | 1.35 M | 246 + 509 | 2 | 2652 |
| T2c_dpo | 2,048 | 9.16 M | 75 + 5112 | 1 | 1791 |
| T2c_s2300 | 512 | 2.85 M | 84 + 1578 | 1 | 1807 |
| T3_dpo | 7,680 | 33.30 M | 82 + 17753 | 1 | 1876 |
| T4_s0750 | 1,088 | 7.64 M | 79 + 4825 | 1 | 1583 |
| T4b_s0750 | 16 | 0.09 M | 85 + 178 | 1 | 478 |
