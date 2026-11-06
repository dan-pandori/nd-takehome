### pass@k

| task (prompts) | grade | model | samples | pass@1 [95 % CI] | pass@8 [95 % CI] | pass@16 |
|---|---|---|---|---|---|---|
| ifbench headline (218) | strict | dpo | 3488 | 0.290 [0.237, 0.345] | 0.461 [0.395, 0.527] | 0.509 [0.440, 0.578] |
| ifbench headline (218) | strict | s0100 | 1744 | 0.315 [0.263, 0.371] | 0.505 [0.445, 0.573] | – |
| ifbench headline (218) | strict | s0750 | 1744 | 0.512 [0.460, 0.562] | 0.794 [0.743, 0.849] | – |
| ifbench headline (218) | strict | s2300 | 1744 | 0.683 [0.635, 0.732] | 0.885 [0.844, 0.927] | – |
| ifbench headline (218) | loose | dpo | 3488 | 0.347 [0.292, 0.403] | 0.552 [0.488, 0.611] | 0.619 [0.555, 0.683] |
| ifbench headline (218) | loose | s0100 | 1744 | 0.373 [0.318, 0.427] | 0.583 [0.518, 0.647] | – |
| ifbench headline (218) | loose | s0750 | 1744 | 0.549 [0.494, 0.600] | 0.812 [0.757, 0.862] | – |
| ifbench headline (218) | loose | s2300 | 1744 | 0.707 [0.660, 0.755] | 0.904 [0.867, 0.940] | – |
| ifbench all (300) | strict | dpo | 4800 | 0.280 [0.238, 0.324] | 0.439 [0.389, 0.490] | 0.480 [0.427, 0.533] |
| ifbench all (300) | strict | s0100 | 2400 | 0.297 [0.254, 0.342] | 0.483 [0.427, 0.537] | – |
| ifbench all (300) | strict | s0750 | 2400 | 0.478 [0.436, 0.523] | 0.757 [0.707, 0.807] | – |
| ifbench all (300) | strict | s2300 | 2400 | 0.676 [0.636, 0.715] | 0.880 [0.840, 0.913] | – |
| ifeval headline (150) | strict | dpo | 2400 | 0.768 [0.712, 0.817] | 0.908 [0.865, 0.948] | 0.927 [0.880, 0.967] |
| ifeval headline (150) | strict | s0750 | 1200 | 0.884 [0.839, 0.922] | 0.947 [0.907, 0.980] | – |
| ifeval headline (150) | strict | s2300 | 1200 | 0.935 [0.900, 0.964] | 0.973 [0.947, 0.993] | – |
| ifeval headline (150) | loose | dpo | 2400 | 0.809 [0.760, 0.853] | 0.948 [0.914, 0.976] | 0.960 [0.927, 0.987] |
| ifeval headline (150) | loose | s0750 | 1200 | 0.914 [0.879, 0.946] | 0.980 [0.953, 1.000] | – |
| ifeval headline (150) | loose | s2300 | 1200 | 0.947 [0.912, 0.973] | 0.980 [0.953, 1.000] | – |
| omega_out headline (100) | omega | dpo | 1600 | 0.274 [0.206, 0.344] | 0.521 [0.434, 0.601] | 0.610 [0.520, 0.700] |
| omega_out headline (100) | omega | s0750 | 800 | 0.550 [0.466, 0.629] | 0.710 [0.620, 0.800] | – |
| omega_out headline (100) | omega | s2300 | 800 | 0.624 [0.540, 0.708] | 0.730 [0.640, 0.810] | – |
| omega_out headline (100) | rl | dpo | 1600 | 0.302 [0.233, 0.375] | 0.557 [0.468, 0.639] | 0.640 [0.540, 0.730] |
| omega_out headline (100) | rl | s0750 | 800 | 0.566 [0.484, 0.641] | 0.710 [0.620, 0.800] | – |
| omega_out headline (100) | rl | s2300 | 800 | 0.632 [0.549, 0.715] | 0.730 [0.640, 0.810] | – |
| omega_out headline (100) | own | dpo | 1600 | 0.276 [0.207, 0.347] | 0.530 [0.446, 0.615] | 0.620 [0.530, 0.710] |
| omega_out headline (100) | own | s0750 | 800 | 0.552 [0.472, 0.631] | 0.720 [0.630, 0.810] | – |
| omega_out headline (100) | own | s2300 | 800 | 0.635 [0.552, 0.719] | 0.740 [0.660, 0.820] | – |

### entries / exits

| task | grade | checkpoint | expected entries @8 [CI] | expected exits @8 [CI] | observed entries / exits (vs dpo's first 8) | (vs dpo's 16) |
|---|---|---|---|---|---|---|
| ifbench | strict | s0100 | 19.92 [12.87, 27.58] | 10.51 [5.19, 15.93] | 21 / 11 | 14 / 15 |
| ifbench | strict | s0750 | 75.64 [62.97, 89.22] | 3.23 [0.77, 6.46] | 76 / 3 | 67 / 5 |
| ifbench | strict | s2300 | 98.27 [84.61, 112.72] | 5.86 [2.23, 10.18] | 98 / 5 | 90 / 8 |
| ifeval | strict | s0750 | 6.7 [2.66, 11.26] | 0.96 [0.0, 2.88] | 7 / 1 | 4 / 1 |
| ifeval | strict | s2300 | 10.7 [5.29, 16.79] | 0.96 [0.0, 2.88] | 11 / 1 | 8 / 1 |
| omega_out | omega | s0750 | 19.87 [14.07, 26.74] | 1.0 [0.0, 2.5] | 21 / 0 | 12 / 2 |
| omega_out | omega | s2300 | 21.37 [15.08, 28.86] | 0.5 [0.0, 1.5] | 23 / 0 | 13 / 1 |
| omega_out | rl | s0750 | 16.61 [11.27, 22.93] | 1.27 [0.0, 3.3] | 18 / 1 | 9 / 2 |
| omega_out | rl | s2300 | 17.84 [12.24, 24.58] | 0.5 [0.0, 1.5] | 19 / 0 | 10 / 1 |

### candidates

| task | grade | \|R\| | reach (s2300 confirmed, dpo 0 in 256) | dpo resolved (≥ 2 in 256) | open | \|V\| | reverse | s2300 resolved | V open | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ifbench|headline | strict | 94 | 49 | 33 | 12 (dpo_one_success 12) | 8 | 2 | 5 | 1 | Reach |
| ifbench|headline | loose | 73 | 24 | 35 | 14 (dpo_one_success 12, dpo_incomplete 2) | 8 | 2 | 4 | 2 | Reach |
| ifbench|headline | rlview | 94 | 49 | 33 | 12 (dpo_one_success 12) | 8 | 2 | 5 | 1 | Reach |
| ifbench|all | strict | 133 | 49 | 33 | 51 (dpo_incomplete 39, dpo_one_success 12) | 8 | 2 | 5 | 1 | Reach |
| ifeval|headline | strict | 8 | 6 | 1 | 1 (dpo_one_success 1) | 1 | 1 | 0 | 0 | Reach |
| ifeval|headline | loose | 6 | 5 | 1 | 0 () | 3 | 1 | 0 | 2 | Reach |
| omega_out|headline | omega | 14 | 3 | 9 | 2 (dpo_one_success 2) | 1 | 0 | 1 | 0 | Reach |
| omega_out|headline | rl | 11 | 2 | 8 | 1 (dpo_one_success 1) | 1 | 0 | 1 | 0 | Inconclusive |
| omega_out|headline | doubly | 14 | 3 | 9 | 2 (dpo_one_success 2) | 1 | 0 | 1 | 0 | Reach |
| omega_out|headline | own | 14 | 3 | 9 | 2 (dpo_one_success 2) | 1 | 0 | 1 | 0 | Reach |

### lengths

| task | model | samples | mean tokens | cut at 32,768 | closes `</think>` |
|---|---|---|---|---|---|
| ifbench | dpo | 4800 | 4,391 | 0.0004 | 1.0000 |
| ifbench | s0100 | 2400 | 4,326 | 0.0000 | 0.9996 |
| ifbench | s0750 | 2400 | 5,650 | 0.0013 | 1.0000 |
| ifbench | s2300 | 2400 | 6,487 | 0.0000 | 0.9996 |
| ifeval | dpo | 2400 | 2,508 | 0.0000 | 1.0000 |
| ifeval | s0750 | 1200 | 3,291 | 0.0000 | 1.0000 |
| ifeval | s2300 | 1200 | 4,536 | 0.0067 | 0.9933 |
| omega_out | dpo | 1600 | 24,709 | 0.2175 | 0.7937 |
| omega_out | s0750 | 800 | 22,030 | 0.1150 | 0.9000 |
| omega_out | s2300 | 800 | 20,873 | 0.0512 | 0.9575 |
