# noise-floor — the null cells (pool x Stage-1 seed)

| quantity | cells | mean | sd | min | max | max/min | MDD at n = 2 |
|---|---|---|---|---|---|---|---|
| `heldout_overall` | 52 | 0.9072 | 0.03038 | 0.8420 | 0.9630 | 1.14x | 0.1629 (18 %) |
| `heldout_len2` | 52 | 0.9963 | 0.003128 | 0.9870 | 1.0000 | 1.01x | 0.01678 (2 %) |
| `heldout_len3` | 52 | 0.9883 | 0.00486 | 0.9760 | 0.9970 | 1.02x | 0.02607 (3 %) |
| `heldout_len4` | 52 | 0.9567 | 0.01512 | 0.8920 | 0.9790 | 1.10x | 0.0811 (8 %) |
| `heldout_len5` | 52 | 0.9272 | 0.01502 | 0.8770 | 0.9560 | 1.09x | 0.08053 (9 %) |
| `heldout_len6` | 52 | 0.6674 | 0.1523 | 0.4210 | 0.9200 | 2.19x | 0.8167 (122 %) |
| `heldout_depth3_slice` | 52 | 0.4402 | 0.3053 | 0.0080 | 0.9180 | 114.75x | 1.638 (372 %) |
| `heldout_len6_nopattern` | 52 | 0.8240 | 0.03667 | 0.6964 | 0.8785 | 1.26x | 0.1966 (24 %) |
| `cov_red_solved` | 8 | 30.625 | 13.23 | 6 | 46 | 7.67x | 70.98 (232 %) |
| `cov_req8_solved` | 8 | 152.75 | 73.27 | 61 | 242 | 3.97x | 392.9 (257 %) |
| `ladder_frozen_transfer_solved` | 8 | 169.125 | 74.06 | 62 | 265 | 4.27x | 397.2 (235 %) |
| `ladder_frozen_transfer_lstar` | 8 | 9.125 | 0.3536 | 9 | 10 | 1.11x | 1.896 (21 %) |
| `ladder_frozen_targets_solved` | 8 | 1256.25 | 391.2 | 714 | 1765 | 2.47x | 2098 (167 %) |

### the eight pre-registered cells (Stage-1 seeds 0 and 1), per cell

| quantity | p1 s0 | p1 s1 | p2 s0 | p2 s1 | p3 s0 | p3 s1 | p4 s0 | p4 s1 |
|---|---|---|---|---|---|---|---|---|
| `heldout_overall` | 0.8726 | 0.9362 | 0.9458 | 0.8770 | 0.8680 | 0.8858 | 0.8716 | 0.9630 |
| `heldout_len2` | 0.9970 | 0.9930 | 0.9990 | 1.0000 | 0.9970 | 0.9940 | 0.9980 | 0.9980 |
| `heldout_len3` | 0.9900 | 0.9810 | 0.9920 | 0.9930 | 0.9910 | 0.9910 | 0.9800 | 0.9910 |
| `heldout_len4` | 0.9560 | 0.9450 | 0.9700 | 0.9650 | 0.9530 | 0.9660 | 0.9600 | 0.9680 |
| `heldout_len5` | 0.9330 | 0.9120 | 0.9560 | 0.9190 | 0.9260 | 0.9220 | 0.9260 | 0.9380 |
| `heldout_len6` | 0.4870 | 0.8500 | 0.8120 | 0.5080 | 0.4730 | 0.5560 | 0.4940 | 0.9200 |
| `heldout_depth3_slice` | 0.0860 | 0.8180 | 0.7060 | 0.1060 | 0.0400 | 0.2040 | 0.0900 | 0.9180 |
| `heldout_len6_nopattern` | 0.8300 | 0.7814 | 0.8623 | 0.8421 | 0.8340 | 0.8502 | 0.8300 | 0.8664 |
| `cov_red_solved` | 31 | 19 | 39 | 43 | 6 | 46 | 34 | 27 |
| `cov_req8_solved` | 89 | 242 | 205 | 61 | 71 | 172 | 144 | 238 |
| `ladder_frozen_transfer_solved` | 117 | 262 | 200 | 96 | 62 | 174 | 177 | 265 |
| `ladder_frozen_transfer_lstar` | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 10 |
| `ladder_frozen_targets_solved` | 1036 | 1715 | 1512 | 823 | 714 | 1298 | 1187 | 1765 |

## variance components (unreplicated pools x seeds)

| quantity | MS_pool | MS_seed | MS_resid | var_pool | var_seed | var_resid | bimodality b |
|---|---|---|---|---|---|---|---|
| `heldout_overall` | 0.0002736 | 0.001084 | 0.0009231 | -4.997e-05 | 4.031e-05 | 0.0009231 | 0.557 **bimodal** |
| `heldout_len2` | 1.282e-06 | 1.434e-05 | 8.976e-06 | -5.919e-07 | 1.341e-06 | 8.976e-06 | 0.648 **bimodal** |
| `heldout_len3` | 2.279e-05 | 4.062e-05 | 1.802e-05 | 3.665e-07 | 5.649e-06 | 1.802e-05 | 0.498 |
| `heldout_len4` | 0.0001157 | 0.0004738 | 0.0001563 | -3.124e-06 | 7.938e-05 | 0.0001563 | 0.510 |
| `heldout_len5` | 7.763e-06 | 0.0004625 | 0.0001646 | -1.206e-05 | 7.449e-05 | 0.0001646 | 0.423 |
| `heldout_len6` | 0.006646 | 0.02838 | 0.02283 | -0.001245 | 0.001387 | 0.02283 | 0.677 **bimodal** |
| `heldout_depth3_slice` | 0.02727 | 0.1186 | 0.09026 | -0.004845 | 0.00709 | 0.09026 | 0.697 **bimodal** |
| `heldout_len6_nopattern` | 0.0002227 | 0.002646 | 0.001004 | -6.01e-05 | 0.0004104 | 0.001004 | 0.603 **bimodal** |
| `cov_red_solved` | 107.1 | 78.12 | 275.5 | -84.17 | -49.33 | 275.5 | 0.515 |
| `cov_req8_solved` | 1995 | 5202 | 8796 | -3401 | -898.6 | 8796 | 0.875 **bimodal** |
| `ladder_frozen_transfer_solved` | 4111 | 7260 | 6268 | -1079 | 248 | 6268 | 0.546 |
| `ladder_frozen_transfer_lstar` | 0.125 | 0.125 | 0.125 | 0 | 0 | 0.125 | 0.818 **bimodal** |
| `ladder_frozen_targets_solved` | 8.867e+04 | 1.659e+05 | 2.132e+05 | -6.226e+04 | -1.182e+04 | 2.132e+05 | 0.623 **bimodal** |

## gap-closers (existing bucket checkpoints; no retraining)

| run | checkpoint | transfer solved / 2,285 | transfer L* | targets solved / 4,495 |
|---|---|---|---|---|
| `la_frozen_dsg_g1_s0` | `ckpts/dsg/stage1_g1_s0.pt` | 62 | 9 | 612 |
| `la_T1_dsc_a1_s1` | `ckpts/ladder/la_T1_dsc_a1_s1_r7.pt` | 847 | 11 | 2693 |
| `la_frozen_dsc_a1_s1` | `ckpts/dsc/stage1_a1_s1.pt` | 194 | 9 | 1456 |

## in-loop Lean gate (both pods)

{
 "calls": 408,
 "samples": 20010560,
 "parse_fail": 6500782,
 "distinct_checked": 12033100,
 "both_ok": 1977301,
 "nd_ok_lean_rej": 0,
 "nd_rej_lean_ok": 808,
 "both_rej": 10054991,
 "disagree_lines": 808,
 "lean_only_per_million_distinct": 67.14811644547125,
 "nd_only_per_million_distinct": 0.0
}

written /tmp/nf_after.json
