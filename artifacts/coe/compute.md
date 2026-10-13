# create-or-elicit — compute (`coe/coe_compute.py`)

GPU-hours (process wall-clock on one NVIDIA A40, from 3,817 registry rows; processes sharing a card each count in full, so the sum exceeds pod time). Model = the checkpoint family the process ran (full s0–s2 = the old best-cap12 seeds, read here only).

| model | pretrain | heldout_greedy | rl | read_plain | read_guided | timing | certificate | stdA | large_k_t916 | phase2_power | phase3a | scoring | phase0_replica | total | gen tokens (M) | attempts (M) | Lean checks (M) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_s0 | – | – | – | 6.03 | 4.10 | 0.52 | – | – | – | 1.52 | – | – | 0.55 | 12.7 | 488 | 1.96 | 0.71 |
| full_s1 | – | – | – | 6.47 | 4.28 | 0.57 | – | – | – | 0.44 | – | – | 0.54 | 12.3 | 514 | 1.96 | 0.73 |
| full_s2 | – | – | – | 3.32 | 2.56 | 0.47 | – | – | – | – | – | – | – | 6.3 | 447 | 1.74 | 0.62 |
| full_s3 | 0.36 | 0.01 | 15.39 | 7.52 | 6.35 | 0.20 | – | 1.92 | – | – | – | – | – | 31.7 | 1327 | 5.68 | 3.02 |
| full_s4 | 0.36 | 0.01 | 15.85 | 8.33 | 6.53 | 0.16 | – | 1.97 | – | – | – | – | – | 33.2 | 1403 | 5.85 | 2.97 |
| full_s5 | 0.36 | 0.01 | 15.30 | 7.53 | 5.70 | 0.22 | – | 1.74 | – | – | – | – | – | 30.9 | 1383 | 5.48 | 2.98 |
| dose1_s0 | 0.36 | 0.01 | 14.89 | 5.97 | 3.38 | 0.15 | – | – | – | – | – | – | – | 24.8 | 1041 | 4.19 | 2.62 |
| dose1_s1 | 0.36 | 0.01 | 16.34 | 6.98 | 3.82 | 0.24 | – | – | – | – | – | – | – | 27.7 | 1010 | 4.19 | 2.58 |
| dose1_s2 | 0.36 | 0.01 | 15.77 | 6.85 | 3.46 | 0.17 | – | – | – | – | – | – | – | 26.6 | 1029 | 4.19 | 2.56 |
| ko_s0 | 0.36 | 0.01 | 14.23 | 6.51 | 4.77 | 0.14 | 2.40 | 1.73 | 0.76 | 0.84 | 0.66 | – | – | 32.4 | 1700 | 8.16 | 2.90 |
| ko_s1 | 0.36 | 0.01 | 22.43 | 10.10 | 5.71 | 0.19 | 2.51 | 1.46 | – | 1.42 | 0.92 | – | – | 45.1 | 2098 | 8.87 | 4.38 |
| ko_s2 | 0.36 | 0.01 | 16.02 | 8.04 | 5.93 | 0.17 | 1.62 | 1.34 | – | – | 1.11 | – | – | 34.6 | 1557 | 7.50 | 2.86 |
| ko_s3 | 0.36 | 0.01 | 13.47 | 6.68 | 5.05 | 0.14 | 1.44 | 1.82 | – | – | 0.77 | – | – | 29.7 | 1554 | 7.73 | 2.85 |
| ko_s4 | 0.36 | 0.01 | 15.85 | 8.53 | 7.14 | 0.16 | 2.17 | 1.79 | – | – | – | – | – | 36.0 | 1715 | 7.65 | 2.82 |
| ko_s5 | 0.36 | 0.01 | 15.72 | 7.91 | 6.12 | 0.15 | 2.68 | 1.53 | – | – | 0.86 | – | – | 35.4 | 1692 | 7.44 | 2.89 |
| other | – | – | – | – | – | – | – | – | – | – | – | 0.40 | – | 0.4 | 0 | 0.00 | 0.00 |
| **all** | 4.3 | 0.1 | 191.2 | 106.8 | 74.9 | 3.6 | 12.8 | 15.3 | 0.8 | 4.2 | 4.3 | 0.4 | 1.1 | 419.9 | | | |

## Pod time (what the run paid; `~/podhours.log` and live pods at the time of writing)

| pod | GPU | role | hours | $ |
|---|---|---|---:|---:|
| coe-t6 | NVIDIA RTX A6000 | Phase 0.2 RTX A6000 timing (stuck initialising; deleted) | 0.27 | 0.16 |
| coe-r1 | NVIDIA A40 | Phase 0.2 replica (A6000 / A40 ratio); Phase 2; E2 scoring | 5.14 | 3.03 |
| coe-r2 | NVIDIA A40 | Phase 2b | 1.17 | 0.69 |
| coe-r0 | NVIDIA A40 | Phase 0.2 A40 timing; old full s0–s2 reads on the tracked set; old-ladder analysis | 19.41 | 11.45 |
| coe-f5 | NVIDIA A40 | full s5: as full s3 | 22.09 | 13.03 |
| coe-f3 | NVIDIA A40 | full s3: Stage 1, 16-round ladder, reads, post (timing, standard A, scoring) | 22.51 | 13.28 |
| coe-k3 | NVIDIA A40 | knockout s3: as knockout s0 | 22.69 | 13.39 |
| coe-k0 | NVIDIA A40 | knockout s0: Stage 1, ladder, reads, post (timing, certificate, standard A, scoring), top-up, Phase 3a | 23.39 | 13.80 |
| coe-f4 | NVIDIA A40 | full s4: as full s3 | 24.30 | 14.34 |
| coe-k2 | NVIDIA A40 | knockout s2: as knockout s0 | 26.66 | 15.73 |
| coe-k5 | NVIDIA A40 | knockout s5: as knockout s0 | 26.60 | 15.69 |
| coe-k4 | NVIDIA A40 | knockout s4: as knockout s0 (no Phase 3a) | 27.53 | 16.24 |
| coe-d0 | NVIDIA A40 | 1 % dose s0: Stage 1, ladder, reads (no r16 g0 / x1), timing, scoring | 16.66 | 9.83 |
| coe-d2 | NVIDIA A40 | 1 % dose s2: as dose s0 | 18.07 | 10.66 |
| coe-d1 | NVIDIA A40 | 1 % dose s1: as dose s0 | 18.18 | 10.72 |
| coe-k1 | NVIDIA A40 | knockout s1: as knockout s0, plus the r17–r24 extension and r20 / r24 reads; dose s1 / s2 per-round analysis | 34.69 | 20.46 |
| **total** | | | 309.34 | 182.50 |
