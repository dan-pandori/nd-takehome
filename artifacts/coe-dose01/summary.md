Bar: 14 of 106 (median of the full bases at round 1).

| ladder | arm | rounds | y r1 | y r16 | first round ≥ bar (x) | x at r16 | x incl. last ft | pos-free σ r1 | first pos-free | y last |
|---|---|---|---|---|---|---|---|---|---|---|
| old_full_s0 | full | 1-16 | 15 | 44 | r1 (0.10×) | 5.97 | 6.24 | 581 | 1 | 44 |
| old_full_s1 | full | 1-16 | 2 | 73 | r2 (0.43×) | 6.05 | 6.31 | 418 | 1 | 73 |
| old_full_s2 | full | 1-16 | 19 | 73 | r1 (0.10×) | 5.84 | 6.09 | 551 | 1 | 73 |
| la_full_s3 | full | 1-16 | 13 | 65 | r2 (0.39×) | 5.80 | 6.05 | 665 | 1 | 65 |
| la_full_s4 | full | 1-16 | 10 | 22 | r2 (0.39×) | 5.82 | 6.07 | 541 | 1 | 22 |
| la_full_s5 | full | 1-16 | 17 | 32 | r1 (0.02×) | 4.01 | 4.28 | 535 | 1 | 32 |
| la_dose1_s0 | dose1 | 1-16 | 3 | 58 | r2 (0.39×) | 5.73 | 5.97 | 213 | 1 | 58 |
| la_dose1_s1 | dose1 | 1-16 | 13 | 34 | r2 (0.41×) | 5.95 | 6.21 | 170 | 1 | 34 |
| la_dose1_s2 | dose1 | 1-16 | 2 | 30 | r3 (0.73×) | 5.93 | 6.19 | 219 | 1 | 30 |
| la_dose01_s0 | dose01 | 1-16 | 0 | 30 | r5 (1.37×) | 5.67 | 5.91 | 1 | 1 | 30 |
| la_dose01_s1 | dose01 | 1-16 | 0 | 28 | r8 (2.58×) | 5.94 | 6.20 | 0 | 2 | 28 |
| la_dose01_s2 | dose01 | 1-16 | 3 | 19 | r3 (0.69×) | 5.71 | 5.95 | 2 | 1 | 19 |
| la_ko_s0 | knockout | 1-16 | 0 | 0 | not reached | 5.84 | 6.09 | 0 | None | 0 |
| la_ko_s1 | knockout | 1-32 | 0 | 3 | not reached | 5.93 | 13.51 | 0 | 9 | 6 |
| la_ko_s2 | knockout | 1-16 | 0 | 0 | not reached | 5.90 | 6.15 | 0 | 12 | 0 |
| la_ko_s3 | knockout | 1-16 | 0 | 1 | not reached | 5.58 | 5.82 | 0 | 15 | 1 |
| la_ko_s4 | knockout | 1-16 | 0 | 0 | not reached | 6.13 | 6.40 | 0 | 15 | 0 |
| la_ko_s5 | knockout | 1-16 | 0 | 0 | not reached | 5.99 | 6.24 | 0 | 2 | 0 |

| arm | n | crossed by r16 | y r1 (IQM [95 %]) | y r16 (IQM [95 %]) |
|---|---|---|---|---|
| full | 6 | 6 | [13, 10, 17, 15, 2, 19] (13.75 [7.25, 17.50]) | [65, 22, 32, 44, 73, 73] (53.50 [30.00, 71.00]) |
| dose1 | 3 | 3 | [3, 13, 2] (6.00 [2.00, 13.00]) | [58, 34, 30] (40.67 [30.00, 58.00]) |
| dose01 | 3 | 3 | [0, 0, 3] (1.00 [0.00, 3.00]) | [30, 28, 19] (25.67 [19.00, 30.00]) |
| knockout | 6 | 0 | [0, 0, 0, 0, 0, 0] (0.00 [0.00, 0.00]) | [0, 3, 0, 1, 0, 0] (0.25 [0.00, 1.75]) |

| read (k 256, plain) | strict solved / 106 | families acquired | cut-off share, strict stratum |
|---|---|---|---|
| pend_dose01_s0_x0 | 0 | – | 0.0000 |
| r16_dose01_s0_x0 | 31 | contraposition_conv, negated_conditional | 0.0156 |
| pend_dose01_s1_x0 | 0 | – | 0.0113 |
| r16_dose01_s1_x0 | 28 | contraposition_conv, negated_conditional | 0.0315 |
| pend_dose01_s2_x0 | 6 | – | 0.0000 |
| r16_dose01_s2_x0 | 19 | contraposition_conv | 0.0846 |

Tests: {
 "crossed_by16_dose01_vs_knockout": {
  "dose01": "3/3",
  "knockout": "0/6",
  "alternative": "greater",
  "p_boschloo": 0.003251536859218616
 },
 "y_r16_dose01_vs_knockout": {
  "dose01": [
   30,
   28,
   19
  ],
  "knockout": [
   0,
   3,
   0,
   1,
   0,
   0
  ],
  "alternative": "greater",
  "p_mann_whitney_exact": 0.011904761904761904
 },
 "crossed_by16_dose01_vs_dose1": {
  "dose01": "3/3",
  "dose1": "3/3",
  "alternative": "less",
  "p_boschloo": 1.0
 },
 "y_r16_dose01_vs_dose1": {
  "dose01": [
   30,
   28,
   19
  ],
  "dose1": [
   58,
   34,
   30
  ],
  "alternative": "less",
  "p_mann_whitney_exact": 0.1
 }
}

Reading rule: graded (crosses, later than the 1 % arm: median 1.37x > 0.73x)
