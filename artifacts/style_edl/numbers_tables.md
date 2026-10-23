Per-seed values are s0 / s1 / s2; "mean" is the mean over the three seeds (n = 3: the IQM is the mean). Bits per proof unless stated; names the environment assigns are not coded. EDL and EDL_c include log₂ 3 bits for the lr choice.

**Table 1 — streams and the learner (before training).**

| stream | identical to the learner's greedy proof (of 256) | actions per proof | coded tokens per proof | TF agreement (per action) | learner bits per proof, test (L0) | starting loss (block [0, 8)) |
|---|---|---|---|---|---|---|
| S_own | 1.000 / 1.000 / 1.000 | 4.52 / 4.55 / 4.44 | 79.4 / 79.7 / 78.0 | 0.9965 / 0.9974 / 0.9982 | 0.37 / 0.27 / 0.24 | 0.58 / 0.52 / 0.47 |
| S_own2 | 0.910 / 0.926 / 0.934 | 4.71 / 4.74 / 4.68 | 82.0 / 82.7 / 82.0 | 0.9776 / 0.9860 / 0.9800 | 0.66 / 0.61 / 0.61 | 1.56 / 0.56 / 0.74 |
| S_seed | 0.941 / 0.938 / 0.941 | 4.55 / 4.44 / 4.52 | 79.7 / 78.0 / 79.4 | 0.9862 / 0.9859 / 0.9844 | 0.43 / 0.40 / 0.35 | 0.81 / 1.94 / 0.88 |
| S_RL | 0.945 / 0.922 / 0.938 | 4.64 / 4.64 / 4.52 | 81.3 / 81.3 / 79.6 | 0.9848 / 0.9756 / 0.9836 | 0.78 / 0.87 / 1.26 | 1.83 / 1.26 / 1.43 |
| S_short | 0.871 / 0.848 / 0.883 | 4.26 / 4.26 / 4.26 | 74.3 / 74.3 / 74.3 | 0.9578 / 0.9578 / 0.9633 | 0.94 / 0.79 / 1.07 | 3.29 / 2.83 / 3.18 |
| S_Kal | 0.000 / 0.000 / 0.000 | 116 / 116 / 116 | 1716 / 1716 / 1716 | 0.2736 / 0.3123 / 0.2273 | 1283 / 1236 / 1339 | 1340 / 1255 / 1411 |

**Table 2 — EDL (A_ES, lr chosen per seed × stream by prequential code).**

| stream | lr (s0 / s1 / s2) | θ* test loss L_test | EDL per proof | EDL_c per proof | mean EDL_c | EDL_c per action | cross-fit EDL per proof (exploratory) | A_fixed (E = 4) EDL_c |
|---|---|---|---|---|---|---|---|---|
| S_own | 1e-05 / 1e-05 / 1e-05 | 0.13 / 0.19 / 0.11 | 0.10 / 0.02 / 0.06 | 0.04 / -0.00 / 0.04 | 0.03 | 0.009 / -0.001 / 0.008 | 0.07 / 0.01 / 0.05 | 0.07 / 0.03 / 0.05 |
| S_own2 | 1e-05 / 1e-05 / 1e-05 | 0.58 / 0.56 / 0.59 | 0.22 / -0.01 / 0.09 | 0.05 / 0.04 / 0.01 | 0.04 | 0.011 / 0.008 / 0.003 | 0.02 / 0.04 / -0.01 | 0.06 / 0.02 / 0.01 |
| S_seed | 1e-05 / 1e-05 / 1e-05 | 0.18 / 0.24 / 0.22 | 0.10 / 0.27 / 0.22 | 0.05 / 0.07 / 0.07 | 0.06 | 0.010 / 0.014 / 0.016 | 0.06 / 0.05 / 0.09 | 0.07 / 0.07 / 0.08 |
| S_RL | 1e-05 / 1e-05 / 1e-05 | 0.52 / 0.76 / 1.55 | 0.55 / 0.20 / -0.90 | 0.12 / 0.08 / -0.37 | -0.06 | 0.024 / 0.017 / -0.079 | 0.05 / 0.05 / -0.22 | 0.10 / 0.08 / 0.03 |
| S_short | 0.0001 / 0.0001 / 0.0001 | 0.17 / 0.24 / 0.23 | 0.97 / 0.91 / 0.95 | -0.34 / -0.05 / 0.07 | -0.10 | -0.079 / -0.011 / 0.017 | 0.21 / 0.10 / 0.32 | -0.30 / -0.13 / -0.03 |
| S_Kal | 0.0001 / 0.0001 / 0.0001 | 88.4 / 96.6 / 89.9 | 224 / 190 / 240 | 179 / 182 / 177 | 179 | 1.533 / 1.561 / 1.514 | 214 / 185 / 225 | 199 / 215 / 237 |

**Table 3 — capability on the 128 test theorems (k 32, T 0.8, sample seed 2; θ* = A_ES at the chosen lr, order 0).** Learner before: plain pass@32 1.000 / 1.000 / 1.000, pass@1 0.966 / 0.976 / 0.972; guided pass@32 1.000 / 1.000 / 1.000, pass@1 0.993 / 0.997 / 0.997.

| stream | plain pass@32 after | plain pass@1 after | guided pass@32 after | guided pass@1 after | capability fixed? |
|---|---|---|---|---|---|
| S_own | 1.000 / 1.000 / 1.000 | 0.985 / 0.988 / 0.983 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | yes (3 / 3) |
| S_own2 | 1.000 / 1.000 / 1.000 | 0.980 / 0.981 / 0.978 | 1.000 / 1.000 / 1.000 | 0.999 / 1.000 / 0.998 | yes (3 / 3) |
| S_seed | 1.000 / 1.000 / 1.000 | 0.988 / 0.987 / 0.986 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | yes (3 / 3) |
| S_RL | 1.000 / 1.000 / 1.000 | 0.985 / 0.978 / 0.983 | 1.000 / 1.000 / 1.000 | 0.999 / 0.998 / 1.000 | yes (3 / 3) |
| S_short | 0.992 / 1.000 / 1.000 | 0.979 / 0.970 / 0.959 | 1.000 / 1.000 / 1.000 | 1.000 / 0.998 / 0.995 | yes (3 / 3) |
| S_Kal | 0.383 / 0.352 / 0.250 | 0.029 / 0.047 / 0.015 | 0.602 / 0.602 / 0.594 | 0.118 / 0.136 / 0.103 | no (0 / 3) |

**Table 4 — the style-blind score ℓ_V (same fits, re-run at the chosen lr).**

| stream | ℓ_V of the learner, test (bits) | ℓ_V θ*, test | ℓ_V EDL per proof | ℓ_V EDL_c per proof | single-string EDL_c of the same re-fits |
|---|---|---|---|---|---|
| S_own | 0.220 / 0.146 / 0.156 | 0.036 / 0.032 / 0.046 | 0.063 / 0.056 / 0.049 | 0.042 / 0.038 / 0.039 | 0.043 / -0.005 / 0.037 |
| S_own2 | 0.220 / 0.146 / 0.156 | 0.114 / 0.077 / 0.134 | 0.054 / 0.046 / 0.013 | 0.033 / 0.028 / 0.003 | 0.054 / 0.039 / 0.014 |
| S_seed | 0.220 / 0.146 / 0.156 | 0.034 / 0.043 / 0.049 | 0.069 / 0.076 / 0.058 | 0.048 / 0.058 / 0.048 | 0.046 / 0.065 / 0.073 |
| S_RL | 0.220 / 0.146 / 0.156 | 0.059 / 0.076 / 0.055 | 0.098 / 0.040 / 0.073 | 0.076 / 0.023 / 0.063 | 0.116 / 0.082 / -0.370 |
| S_short | 0.220 / 0.146 / 0.156 | 0.069 / 0.099 / 0.083 | 0.181 / 0.221 / 0.211 | 0.160 / 0.203 / 0.200 | -0.341 / -0.045 / 0.076 |
| S_Kal | 0.220 / 0.146 / 0.156 | 12.9 / 13.1 / 12.4 | -5.095 / -5.560 / -3.961 | -5.116 / -5.578 / -3.971 | 179 / 182 / 177 |

**Table 5 — A1, the per-proof attribution (Addendum 1): proofs identical to the learner's greedy proof (*same*) and the rest (*differ*).**

| stream | differing proofs, stream / test | learner bits per differing test proof | θ* bits per differing test proof | EDL_c per differing proof | EDL_c per same proof | cross-fit, both directions pooled: per differing / per same proof (exploratory) |
|---|---|---|---|---|---|---|
| S_own2 | 12–11 / 12–7 / 10–7 | 4.24 / 7.03 / 7.50 | 4.74 / 7.57 / 7.71 | 0.15 / -0.21 / 0.13 | 0.026 / 0.023 / -0.015 | -0.30 / -0.13 / -0.12 / 0.038 / 0.033 / -0.000 |
| S_seed | 9–6 / 10–6 / 10–5 | 2.37 / 4.28 / 4.00 | 2.44 / 3.81 / 3.94 | -0.39 / -0.04 / 0.15 | 0.057 / 0.072 / 0.050 | -0.31 / -0.16 / 0.59 / 0.067 / 0.053 / 0.036 |
| S_RL | 10–4 / 11–9 / 9–7 | 14.3 / 9.52 / 19.3 | 12.6 / 8.83 / 26.7 | 1.22 / 0.97 / -7.94 | 0.084 / -0.005 / 0.063 | 0.66 / 0.53 / -5.24 / 0.071 / -0.002 / 0.032 |
| S_short | 21–12 / 26–13 / 21–9 | 6.93 / 6.08 / 12.5 | 1.07 / 1.44 / 1.44 | -0.53 / 1.52 / 5.92 | 0.154 / 0.119 / 0.146 | 0.60 / 0.93 / 4.16 / 0.141 / 0.081 / 0.101 |
| S_Kal | 128–128 / 128–128 / 128–128 | 1283 / 1236 / 1339 | 88.4 / 96.6 / 89.9 | 179 / 182 / 177 | — | 214 / 185 / 225 / — |

**Table 7 — the per-block curve (A_ES, chosen lr; seed means of the order means).** Block bits per proof for the blocks [0, 8) (the learner), [8, 16), [16, 32), [32, 64), [64, 128); then each fit's mean bits on the 128 test proofs (learner, after 8, 16, 32, 64, 128 proofs).

| stream | block bits per proof | test-set curve |
|---|---|---|
| S_own | 0.52 → 0.24 → 0.21 → 0.18 → 0.14 | 0.29 → 0.22 → 0.19 → 0.16 → 0.14 → 0.14 |
| S_own2 | 0.95 → 1.25 → 0.79 → 0.47 → 0.63 | 0.62 → 0.59 → 0.61 → 0.59 → 0.59 → 0.58 |
| S_seed | 1.21 → 0.69 → 0.43 → 0.28 → 0.31 | 0.39 → 0.33 → 0.32 → 0.27 → 0.24 → 0.21 |
| S_RL | 1.51 → 0.40 → 1.19 → 1.40 → 0.53 | 0.97 → 0.95 → 0.94 → 0.92 → 0.87 → 0.94 |
| S_short | 3.10 → 0.36 → 1.11 → 2.10 → 0.52 | 0.93 → 1.05 → 0.95 → 0.64 → 0.34 → 0.21 |
| S_Kal | 1335 → 310 → 372 → 285 → 178 | 1286 → 551 → 391 → 262 → 163 → 91.6 |

**Table 6 — compute per arm (results registry; GPU = RTX A5000, except one guided read redone on an A40; GPU-seconds are process wall time on a GPU sometimes shared by 2–3 jobs).** Summed over the three seeds.

| arm | phases | GPU-s | train steps | train tokens (M) | gen tokens (M) | Lean checks |
|---|---|---|---|---|---|---|
| S_Kal | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 26960 | 20084 | 3426.2 | 22.05 | 2071 |
| S_RL | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1730 | 12050 | 38.1 | 3.05 | 24103 |
| S_own | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1789 | 12683 | 39.0 | 3.01 | 23828 |
| S_own2 | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1529 | 8169 | 26.6 | 3.09 | 24332 |
| S_seed | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1676 | 12461 | 38.3 | 3.01 | 23921 |
| S_short | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1659 | 12841 | 36.1 | 2.87 | 23720 |
| learner | cap_logical, cap_plain | 485 | 0 | 0.0 | 3.18 | 24635 |
| shared | reads | 829 | 0 | 0.0 | 13.45 | 90915 |
| other | other | 78 | 12 | 0.0 | 0.00 | 0 |
