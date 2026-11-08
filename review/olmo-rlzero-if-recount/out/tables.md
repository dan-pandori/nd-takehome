### T1. Fixed-phase pass@k, strict (loose in brackets for pass@1); prompt bootstrap 95 %

| prompt set | model | pass@1 | pass@8 | pass@16 | loose pass@1 |
|---|---|---|---|---|---|
| ifbench_h297 | base | 0.129 [0.103, 0.156] | 0.334 [0.287, 0.382] | 0.421 [0.364, 0.478] | 0.169 |
| ifbench_h297 | s0100 | 0.477 [0.428, 0.527] | 0.650 [0.596, 0.704] | — | 0.513 |
| ifbench_h297 | s0500 | 0.410 [0.364, 0.456] | 0.643 [0.586, 0.697] | — | 0.464 |
| ifbench_h297 | main | 0.469 [0.416, 0.521] | 0.576 [0.522, 0.633] | — | 0.528 |
| ifbench_all300 | base | 0.127 [0.102, 0.155] | 0.331 [0.285, 0.378] | 0.417 [0.360, 0.473] | 0.168 |
| ifbench_all300 | s0100 | 0.475 [0.426, 0.525] | 0.647 [0.593, 0.700] | — | 0.511 |
| ifbench_all300 | s0500 | 0.406 [0.361, 0.452] | 0.637 [0.580, 0.690] | — | 0.460 |
| ifbench_all300 | main | 0.467 [0.415, 0.519] | 0.573 [0.517, 0.630] | — | 0.525 |
| ifbench_s218 | base | 0.122 [0.094, 0.154] | 0.322 [0.268, 0.377] | 0.408 [0.344, 0.477] | 0.159 |
| ifbench_s218 | s0100 | 0.456 [0.399, 0.514] | 0.633 [0.569, 0.697] | — | 0.493 |
| ifbench_s218 | s0500 | 0.393 [0.341, 0.447] | 0.628 [0.564, 0.693] | — | 0.442 |
| ifbench_s218 | main | 0.448 [0.388, 0.509] | 0.555 [0.491, 0.619] | — | 0.511 |
| ifeval_all150 | base | 0.200 [0.160, 0.242] | 0.496 [0.425, 0.567] | 0.587 [0.507, 0.667] | 0.219 |
| ifeval_all150 | s0100 | 0.806 [0.748, 0.860] | 0.880 [0.827, 0.927] | — | 0.822 |
| ifeval_all150 | s0500 | 0.782 [0.728, 0.834] | 0.927 [0.880, 0.967] | — | 0.811 |
| ifeval_all150 | main | 0.817 [0.757, 0.872] | 0.860 [0.800, 0.913] | — | 0.842 |

### T2. Fixed-phase lengths (tokens)

| task | model | samples | mean | median | cut at 16,384 | `</think>` in text |
|---|---|---|---|---|---|---|
| ifbench | base | 4800 | 2510 | 854 | 146 (3.0%) | 27 |
| ifbench | s0100 | 2400 | 36 | 16 | 0 (0.0%) | 0 |
| ifbench | s0500 | 2400 | 162 | 30 | 5 (0.2%) | 0 |
| ifbench | main | 2400 | 29 | 12 | 0 (0.0%) | 0 |
| ifeval | base | 2400 | 2194 | 697 | 65 (2.7%) | 19 |
| ifeval | s0100 | 1200 | 98 | 28 | 1 (0.1%) | 0 |
| ifeval | s0500 | 1200 | 142 | 42 | 1 (0.1%) | 0 |
| ifeval | main | 1200 | 49 | 20 | 0 (0.0%) | 0 |

### T3. Candidates and strict fates at 256 (non-excluded)

| task | R | V | R (loose) | V (loose) | REACH | resolved | base 1 success at 256 | dissolved | open | strict verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ifbench | 109 | 38 | 72 | 33 | 9 | 11 | 5 | 7 | 76 | Reach |
| ifeval | 56 | 14 | 43 | 13 | 5 | 20 | 4 | 1 | 26 | Reach |

### T4. Hand fates (my blind gate + my confirmations), every candidate the base was drawn to 256 on

| prompt | strict fate | main reads (genuine) | main status | base strict successes (genuine) | hand fate |
|---|---|---|---|---|---|
| ifbench_100 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_101 | resolved | 3 (3) | confirmed | 2 (2) | **resolved** |
| ifbench_102 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_103 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_104 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_191 | dissolved | 0 (0) | unconfirmable | 1 (0) | **dissolved** |
| ifbench_218 | dissolved | 1 (0) | unconfirmable | 0 (0) | **dissolved** |
| ifbench_221 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifbench_241 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifbench_247 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifbench_249 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifbench_274 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_291 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifbench_296 | resolved | 3 (2) | confirmed | 5 (1) | **open** |
| ifbench_67 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifbench_70 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifbench_89 | base-1-at-256 | 4 (0) | unconfirmable | 1 (0) | **dissolved** |
| ifbench_97 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_1361 | resolved | 7 (2) | confirmed | 4 (1) | **open** |
| ifeval_1480 | base-1-at-256 | 7 (0) | open-gaming | 1 (1) | **open-gaming** |
| ifeval_1512 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_1691 | base-1-at-256 | 7 (1) | open-gaming | 1 (0) | **open-gaming** |
| ifeval_219 | resolved | 3 (3) | confirmed | 2 (2) | **resolved** |
| ifeval_2239 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifeval_2247 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_2649 | resolved | 7 (0) | open-gaming | 2 (1) | **open-gaming** |
| ifeval_2857 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_2880 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_3272 | resolved | 3 (3) | confirmed | 5 (0) | **REACH** |
| ifeval_3619 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_3724 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |

| task | hand states | hand verdict | gamed share of main's first reads |
|---|---|---|---|
| ifbench | {'REACH': 5, 'resolved': 1, 'dissolved': 10, 'open-gaming': 22, 'open': 70} | **Reach** (ifbench_100, ifbench_102, ifbench_103, ifbench_104, ifbench_274) | 189/205 = 92.2% |
| ifeval | {'open-gaming': 23, 'resolved': 2, 'open': 29, 'dissolved': 1, 'REACH': 1} | **Inconclusive** (ifeval_3272) | 103/110 = 93.6% |

### T6. Compute axis (cumulative RL ÷ pretraining FLOPs; pre-registered definitions, my lengths)

| step | low | high | geometric mean |
|---|---|---|---|
| 100 | 7.17e-06 | 1.01e-05 | 8.52e-06 |
| 500 | 8.43e-06 | 1.94e-05 | 1.28e-05 |
| 1900 | 1.30e-05 | 5.13e-05 | 2.58e-05 |
| 2000 | 1.33e-05 | 5.31e-05 | 2.65e-05 |
| 2100 | 1.35e-05 | 5.49e-05 | 2.73e-05 |

