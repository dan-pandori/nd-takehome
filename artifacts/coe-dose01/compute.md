# coe-dose01 — compute (`coe/d01_compute.py`)

GPU-hours (process wall-clock on one NVIDIA A40, from 740 registry rows; processes sharing a card each count in full, so the sum exceeds pod time).

| model | pretrain | heldout_greedy | rl | read_plain | read_guided | total | gen tokens (M) | attempts (M) | train steps | train tokens (M) | Lean checks (M) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dose01_s0 | 0.36 | 0.01 | 15.28 | 2.56 | 2.96 | 21.2 | 866 | 3.57 | 33,518 | 1989 | 2.37 |
| dose01_s1 | 0.36 | 0.01 | 16.41 | 2.81 | 3.98 | 23.6 | 898 | 3.57 | 33,610 | 2068 | 2.42 |
| dose01_s2 | 0.36 | 0.01 | 17.29 | 2.64 | 2.84 | 23.1 | 872 | 3.57 | 33,831 | 2008 | 2.39 |
| ko_s1 | – | – | 10.17 | 1.31 | – | 11.5 | 482 | 1.65 | 4,800 | 960 | 1.38 |

## RL ladder vs the 1 % arm (policy flag at 1.25×)

| ladder | gpu_seconds | gen_tokens | attempts | train_steps | train_tokens | lean_checks |
|---|---:|---:|---:|---:|---:|---:|
| dose01_s0 ÷ mean(dose1 s0–s2) | 0.976 | 0.963 | 1.000 | 1.000 | 0.940 | 0.986 |
| dose01_s1 ÷ mean(dose1 s0–s2) | 1.048 | 0.994 | 1.000 | 1.000 | 0.987 | 1.001 |
| dose01_s2 ÷ mean(dose1 s0–s2) | 1.104 | 0.983 | 1.000 | 1.000 | 0.947 | 0.994 |
| dose1 mean (absolute) | 56,392 | 675,654,601 | 2,756,736 | 9,600 | 1,649,182,894 | 2,182,005 |

## Knockout s1, rounds 25–32 (this run)

| round | gpu_seconds | gen_tokens | attempts | train_steps | train_tokens | lean_checks |
|---|---:|---:|---:|---:|---:|---:|
| 25 | 3,442 | 48,871,115 | 172,296 | 600 | 118,512,322 | 151,568 |
| 26 | 3,610 | 48,923,424 | 172,296 | 600 | 118,988,464 | 152,009 |
| 27 | 3,609 | 49,439,946 | 172,296 | 600 | 119,206,540 | 151,919 |
| 28 | 3,626 | 49,172,898 | 172,296 | 600 | 119,569,882 | 151,655 |
| 29 | 3,585 | 48,972,634 | 172,296 | 600 | 120,106,828 | 152,149 |
| 30 | 3,666 | 49,693,907 | 172,296 | 600 | 120,769,222 | 152,491 |
| 31 | 3,707 | 49,927,511 | 172,296 | 600 | 121,381,130 | 152,418 |
| 32 | 11,353 | 49,972,755 | 172,296 | 600 | 121,635,601 | 152,590 |

## Pod time (what the run paid)

| pod | GPU | role | hours | $ |
|---|---|---|---:|---:|
| cd01-k1 | NVIDIA A40  | knockout s1 r25-32 + r32 read | 11.65 | 6.87 |
| cd01-s0 | NVIDIA A40  | dose01 s0: Stage 1 + ladder + reads | 17.16 | 10.12 |
| cd01-s1 | NVIDIA A40  | dose01 s1: Stage 1 + ladder + reads | 18.50 | 10.91 |
| cd01-s2 | NVIDIA A40  | dose01 s2: Stage 1 + ladder + reads | 19.40 | 11.45 |
| **total** | | | 66.70 | 39.35 |
