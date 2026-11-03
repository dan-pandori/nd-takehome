### pass@k (rl grade, phase F samples, Chen estimator, problem bootstrap 95 %)

| model (7.3 B, pretrained) | problems | pass@1 | pass@8 | pass@16 |
|---|---|---|---|---|
| base `Olmo-3-1025-7B` main | all (n=83) | 0.094 [0.066, 0.125] | 0.364 [0.275, 0.455] | 0.458 [0.349, 0.566] |
|  | aime2024 (n=24) | 0.107 [0.060, 0.156] | 0.448 [0.274, 0.625] | 0.542 [0.333, 0.750] |
|  | aime2025 (n=30) | 0.096 [0.046, 0.154] | 0.326 [0.179, 0.480] | 0.400 [0.233, 0.567] |
|  | aime2026 (n=29) | 0.082 [0.039, 0.134] | 0.335 [0.197, 0.482] | 0.448 [0.276, 0.621] |
| RL-Zero-Math `step_0100` | all (n=42) | 0.301 [0.208, 0.399] | 0.643 [0.500, 0.786] | — |
|  | aime2024 (n=17) | 0.316 [0.162, 0.478] | 0.588 [0.353, 0.824] | — |
|  | aime2025 (n=10) | 0.300 [0.100, 0.525] | 0.600 [0.300, 0.900] | — |
|  | aime2026 (n=15) | 0.283 [0.150, 0.433] | 0.733 [0.533, 0.933] | — |
| RL-Zero-Math `step_0500` | all (n=83) | 0.304 [0.223, 0.390] | 0.506 [0.398, 0.614] | — |
|  | aime2024 (n=24) | 0.417 [0.250, 0.583] | 0.667 [0.458, 0.833] | — |
|  | aime2025 (n=30) | 0.263 [0.133, 0.408] | 0.433 [0.267, 0.600] | — |
|  | aime2026 (n=29) | 0.254 [0.134, 0.388] | 0.448 [0.276, 0.621] | — |
| RL-Zero-Math `step_2800` (= main) | all (n=83) | 0.419 [0.330, 0.509] | 0.627 [0.518, 0.723] | — |
|  | aime2024 (n=24) | 0.536 [0.365, 0.703] | 0.750 [0.583, 0.917] | — |
|  | aime2025 (n=30) | 0.342 [0.200, 0.496] | 0.533 [0.367, 0.700] | — |
|  | aime2026 (n=29) | 0.401 [0.254, 0.556] | 0.621 [0.448, 0.793] | — |

Same-subset (step_0100's half, headline n = 42):

| model | pass@1 | pass@8 |
|---|---|---|
| base | 0.116 [0.074, 0.161] | 0.450 [0.323, 0.577] |
| step_0100 | 0.301 [0.208, 0.399] | 0.643 [0.500, 0.786] |
| step_0500 | 0.402 [0.283, 0.524] | 0.643 [0.500, 0.786] |
| step_2800 | 0.562 [0.440, 0.685] | 0.786 [0.667, 0.905] |

### matched k = 8 expected entries / exits

| comparison | problems | entries | exits |
|---|---|---|---|
| step_0500 vs base | all83 (83) | 14.04 | 2.27 |
| step_2800 vs base | all83 (83) | 22.77 | 1.00 |
| step_2800 vs step_0500 | all83 (83) | 12.00 | 2.00 |
| step_0100 vs base | half (42) | 9.88 | 1.77 |
| step_0500 vs base | half (42) | 8.61 | 0.50 |
| step_2800 vs base | half (42) | 14.61 | 0.50 |
| step_0500 vs step_0100 | half (42) | 3.00 | 3.00 |

### full-budget reach / reverse (headline 83)

| checkpoint | reach (c's F) | reach (c's F+C) | strong reach | reverse (c's whole budget) | reach / reverse under `main` | under my integer read-out |
|---|---|---|---|---|---|---|
| step_0100 | 0 | 0 | 0 | 7 | 0 / 7 | 0 / 6  |
| step_0500 | 0 | 0 | 0 | 13 | 0 / 13 | 0 / 12  |
| step_2800 | 0 | 0 | 0 | 0 | 0 / 0 | 1 / 0 ['aime2025_14'] |

### likelihood (phase L, 250 scored items)

| group | items (problems) | base mean log p / token (median) | own (median) | gap own − base, median [p10, p90] | summed gap, median (nats) | inside base_own range | inside base_own + pilot | inside, other problems only |
|---|---|---|---|---|---|---|---|---|
| late | 78 (17) | -0.546 | -0.492 | 0.053 [0.006, 0.066] | 646 | 1.00 | 1.00 | 1.00 |
| ckpt_other | 135 (37) | -0.454 | -0.431 | 0.043 [0.005, 0.060] | 192 | 0.90 | 1.00 | 0.90 |
| base_own | 18 (17) | -0.435 | -0.435 | 0.000 [0.000, 0.000] | 0 | 0.89 | 0.94 | 0.83 |
| base_own_pilot | 19 (9) | -0.334 | -0.334 | 0.000 [0.000, 0.000] | 0 | 0.37 | 0.95 | 0.37 |

control ranges: base_own -0.915 to -0.345 (n = 18); + pilot -0.936 to -0.246 (n = 37)

### compute axis (RL ÷ pretraining 6ND = 2.663e23)

| step | low | high | geometric mean |
|---|---|---|---|
| 100 | 4.15e-05 | 8.56e-05 | 5.96e-05 |
| 500 | 2.57e-04 | 5.43e-04 | 3.73e-04 |
| 2800 | 1.49e-03 | 3.22e-03 | 2.19e-03 |

verdict inputs: base pass@8 0.364 [0.275, 0.455]; final 0.627 [0.518, 0.723]; final − base 0.262 [0.179, 0.352]
