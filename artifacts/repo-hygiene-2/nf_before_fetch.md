# noise-floor — the null cells (pool x Stage-1 seed)

| quantity | cells | mean | sd | min | max | max/min | MDD at n = 2 |
|---|---|---|---|---|---|---|---|
| `ladder_frozen_transfer_solved` | 8 | 169.125 | 74.06 | 62 | 265 | 4.27x | 397.2 (235 %) |
| `ladder_frozen_transfer_lstar` | 8 | 9.125 | 0.3536 | 9 | 10 | 1.11x | 1.896 (21 %) |
| `ladder_frozen_targets_solved` | 8 | 1256.25 | 391.2 | 714 | 1765 | 2.47x | 2098 (167 %) |

### the eight pre-registered cells (Stage-1 seeds 0 and 1), per cell

| quantity | p1 s0 | p1 s1 | p2 s0 | p2 s1 | p3 s0 | p3 s1 | p4 s0 | p4 s1 |
|---|---|---|---|---|---|---|---|---|
| `ladder_frozen_transfer_solved` | 117 | 262 | 200 | 96 | 62 | 174 | 177 | 265 |
| `ladder_frozen_transfer_lstar` | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 10 |
| `ladder_frozen_targets_solved` | 1036 | 1715 | 1512 | 823 | 714 | 1298 | 1187 | 1765 |

## variance components (unreplicated pools x seeds)

| quantity | MS_pool | MS_seed | MS_resid | var_pool | var_seed | var_resid | bimodality b |
|---|---|---|---|---|---|---|---|
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
 "disagree_lines": 0,
 "lean_only_per_million_distinct": null,
 "nd_only_per_million_distinct": null
}

written /tmp/nf_before.json
