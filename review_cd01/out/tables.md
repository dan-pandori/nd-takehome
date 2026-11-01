| round | 0.1 % s0 y / x | 0.1 % s1 y / x | 0.1 % s2 y / x |
|---|---|---|---|
| r1 | 0 / 0.11× | 0 / 0.10× | 3 / 0.09× |
| r2 | 0 / 0.40× | 0 / 0.40× | 12 / 0.37× |
| r3 | 3 / 0.70× | 0 / 0.72× | **15 / 0.69×** |
| r4 | 5 / 1.03× | 0 / 1.07× | 18 / 1.03× |
| r5 | **14 / 1.37×** | 0 / 1.42× | 18 / 1.38× |
| r6 | 17 / 1.73× | 6 / 1.80× | 18 / 1.75× |
| r7 | 21 / 2.09× | 13 / 2.18× | 18 / 2.12× |
| r8 | 23 / 2.47× | **14 / 2.58×** | 18 / 2.50× |
| r9 | 26 / 2.85× | 14 / 2.98× | 19 / 2.89× |
| r10 | 27 / 3.24× | 14 / 3.38× | 19 / 3.28× |
| r11 | 28 / 3.63× | 17 / 3.80× | 19 / 3.68× |
| r12 | 28 / 4.03× | 25 / 4.22× | 19 / 4.08× |
| r13 | 29 / 4.43× | 26 / 4.64× | 19 / 4.48× |
| r14 | 29 / 4.84× | 27 / 5.07× | 19 / 4.89× |
| r15 | 29 / 5.25× | 28 / 5.51× | 19 / 5.30× |
| r16 | 30 / 5.67× | 28 / 5.94× | 19 / 5.71× |
| after r16 incl. last fine-tune | x 5.91× | x 6.20× | x 5.95× |

| knockout s1 round | r24 | r25 | r26 | r27 | r28 | r29 | r30 | r31 | r32 |
|---|---|---|---|---|---|---|---|---|---|
| y (of 106) | 5 | 5 | 5 | 6 | 6 | 6 | 6 | 6 | 6 |
| x (after the round's sampling) | 9.52× | 9.97× | 10.43× | 10.90× | 11.36× | 11.82× | 12.29× | 12.76× | 13.23× |

knockout s1 x after r32 incl. its last fine-tune: 13.51×; y by family at r32: {'contraposition_conv': 5, 'generated': 1}.

| ladder (arm) | y r1 | y r16 | first round y ≥ 14 | x there |
|---|---|---|---|---|
| la_dose01_s0 (dose01) | 0 | 30 | r5 | 1.37× |
| la_dose01_s1 (dose01) | 0 | 28 | r8 | 2.58× |
| la_dose01_s2 (dose01) | 3 | 19 | r3 | 0.69× |
| la_dose1_s0 (dose1) | 3 | 58 | r2 | 0.39× |
| la_dose1_s1 (dose1) | 13 | 34 | r2 | 0.41× |
| la_dose1_s2 (dose1) | 2 | 30 | r3 | 0.73× |
| la_ko_s0 (ko) | 0 | 0 | not by r16 | – |
| la_ko_s1 (ko) | 0 | 3 | not by r16 | – |
| la_ko_s2 (ko) | 0 | 0 | not by r16 | – |
| la_ko_s3 (ko) | 0 | 1 | not by r16 | – |
| la_ko_s4 (ko) | 0 | 0 | not by r16 | – |
| la_ko_s5 (ko) | 0 | 0 | not by r16 | – |
| la_full_s3 (full) | 13 | 65 | r2 | – |
| la_full_s4 (full) | 10 | 22 | r2 | – |
| la_full_s5 (full) | 17 | 32 | r1 | – |

| read (k 256, T 0.8, batch 512, max_action 512, max_steps 96, read1054) | strict solved / 106 | by family (cc / dno / em / nc / pe / pes / gen) | acquired (≥ 50 %) | read1054 solved | cut-off share: strict 106 / all / worst family |
|---|---|---|---|---|---|
| dose01_s0 base_x0 | 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 | none | 566 | 0.00 % / 0.16 % / negated_conditional 0.0 % |
| dose01_s0 base_g0 | 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 | none | 746 | n/a (guided) |
| dose01_s0 r16_x0 | 31 | 18 / 0 / 0 / 10 / 0 / 2 / 1 | contraposition_conv, generated, negated_conditional | 919 | 1.56 % / 0.25 % / excluded_middle 3.6 % |
| dose01_s1 base_x0 | 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 | none | 523 | 1.13 % / 0.45 % / peirce 6.3 % |
| dose01_s1 base_g0 | 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 | none | 703 | n/a (guided) |
| dose01_s1 r16_x0 | 28 | 18 / 0 / 0 / 9 / 0 / 0 / 1 | contraposition_conv, generated, negated_conditional | 923 | 3.15 % / 0.70 % / excluded_middle 6.0 % |
| dose01_s2 base_x0 | 6 | 6 / 0 / 0 / 0 / 0 / 0 / 0 | none | 554 | 0.00 % / 0.06 % / contraposition_conv 0.0 % |
| dose01_s2 base_g0 | 9 | 9 / 0 / 0 / 0 / 0 / 0 / 0 | contraposition_conv | 729 | n/a (guided) |
| dose01_s2 r16_x0 | 19 | 18 / 0 / 0 / 0 / 0 / 0 / 1 | contraposition_conv, generated | 907 | 8.46 % / 1.28 % / excluded_middle 20.7 % |
| ko_s1 r32_x0 | 5 | 4 / 0 / 0 / 0 / 0 / 0 / 1 | generated | 895 | 3.78 % / 0.60 % / excluded_middle 10.4 % |

p2 held-out greedy (5,000; Stage-1 bases): s0 4467/5000 = 0.8934, s1 4326/5000 = 0.8652, s2 4176/5000 = 0.8352

| free positive reductio proofs (pos_free*, all targets), first found in round | r1 | r2 | r3 | r4 | r5 | r8 | r12 | r16 |
|---|---|---|---|---|---|---|---|---|
| 0.1 % s0 (proofs / targets) | 1 / 1 | 0 / 0 | 4 / 4 | 24 / 12 | 53 / 20 | 291 / 53 | 602 / 59 | 697 / 66 |
| 0.1 % s1 (proofs / targets) | 0 / 0 | 2 / 2 | 4 / 4 | 17 / 15 | 13 / 11 | 273 / 24 | 616 / 54 | 1116 / 69 |
| 0.1 % s2 (proofs / targets) | 2 / 2 | 35 / 20 | 116 / 28 | 143 / 29 | 253 / 36 | 406 / 35 | 424 / 35 | 464 / 36 |

knockout s1, r25–32 (proofs / targets): r25 152 / 9, r26 113 / 9, r27 148 / 9, r28 154 / 10, r29 139 / 9, r30 143 / 9, r31 136 / 9, r32 143 / 10

| ladder | distinct counted literal texts (dump, strict members, Lean-accepted in the run) | accepted by my harness | y_lean = y at every round | found_transfer strict rows without a dump text |
|---|---|---|---|---|
| la_dose01_s0 | 4522 | 4522 | yes (r1–r16) | 0  |
| la_dose01_s1 | 4597 | 4597 | yes (r1–r16) | 0  |
| la_dose01_s2 | 5571 | 5571 | yes (r1–r16) | 0  |
| la_ko_s1 | 713 | 713 | yes (r25–r32) | 85 (rounds 10, 17, 18, 19, 20, 21, 22, 23, 24; dump covers r25–32 only) |

| ladder | term size median (IQR), 150 sampled texts | pruned lines median (same texts) | written / pruned median, all distinct counted ND proofs | Spearman size vs pruned |
|---|---|---|---|---|
| la_dose01_s0 | 14 (11–19) | 13 | 17 / 17 (n 2401) | 0.921 |
| la_dose01_s1 | 12 (12–18) | 13 | 17 / 16 (n 3169) | 0.931 |
| la_dose01_s2 | 11 (8–13) | 12 | 13 / 13 (n 2719) | 0.784 |
| la_ko_s1 | 17.0 (14–22) | 15.0 | 20 / 17 (n 545) | 0.858 |

| ladder (A40) | attempts | gen_sample | gen_eval | prefill | ft_steps | ft_tokens | lean_sample | lean_eval | gpu_s_sample | gpu_s_eval | gpu_s_ft | gpu_s_total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| la_dose01_s0 (16 rounds) | 2.301e+06 | 5.351e+08 | 1.154e+08 | 3.176e+09 | 9600 | 1.55e+09 | 1.904e+06 | 2.48e+05 | 3.336e+04 | 8685 | 1.292e+04 | 5.497e+04 |
| la_dose01_s1 (16 rounds) | 2.301e+06 | 5.528e+08 | 1.186e+08 | 3.371e+09 | 9600 | 1.627e+09 | 1.924e+06 | 2.603e+05 | 3.625e+04 | 9688 | 1.311e+04 | 5.905e+04 |
| la_dose01_s2 (16 rounds) | 2.301e+06 | 5.421e+08 | 1.222e+08 | 3.341e+09 | 9600 | 1.562e+09 | 1.918e+06 | 2.513e+05 | 3.863e+04 | 1.06e+04 | 1.297e+04 | 6.22e+04 |
| la_ko_s1 (8 rounds) | 1.151e+06 | 3.231e+08 | 7.192e+07 | 2.105e+09 | 4800 | 9.602e+08 | 1.066e+06 | 1.503e+05 | 2.303e+04 | 5909 | 7629 | 3.657e+04 |
| la_dose1_s0 (16 rounds) | 2.301e+06 | 5.641e+08 | 1.191e+08 | 3.471e+09 | 9600 | 1.668e+09 | 1.94e+06 | 2.687e+05 | 3.3e+04 | 7194 | 1.337e+04 | 5.356e+04 |
| la_dose1_s1 (16 rounds) | 2.301e+06 | 5.532e+08 | 1.13e+08 | 3.346e+09 | 9600 | 1.631e+09 | 1.917e+06 | 2.61e+05 | 3.597e+04 | 8294 | 1.451e+04 | 5.878e+04 |
| la_dose1_s2 (16 rounds) | 2.301e+06 | 5.622e+08 | 1.153e+08 | 3.346e+09 | 9600 | 1.649e+09 | 1.911e+06 | 2.478e+05 | 3.451e+04 | 8423 | 1.381e+04 | 5.674e+04 |
| dose01 ÷ mean(1 %) | 1.00–1.00 | 0.96–0.99 | 1.00–1.06 | 0.94–0.99 | 1.00–1.00 | 0.94–0.99 | 0.99–1.00 | 0.96–1.00 | 0.97–1.12 | 1.09–1.33 | 0.93–0.94 | 0.98–1.10 |
