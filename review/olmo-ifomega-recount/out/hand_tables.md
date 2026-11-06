Items read: 586 (r1 370, r2 176, r3 31, r4 6, r5 3); real 568, duplicates 10, swapped-prompt controls 8; labelled 586; reviewer overrides 8.
Controls: duplicate pairs agree 9/10; swapped-prompt controls labelled gamed 8/8.
My own blind reads of a seeded sample of 10 round-1 IF items (5 the readers called genuine, 5 gamed): 10/10 agree.

| task | model | side | items | genuine / sound | gamed | flawed | guess | unsure | not good |
|---|---|---|---|---|---|---|---|---|---|
| ifbench | dpo | challenger | 15 | 12 | 3 | 0 | 0 | 0 | 0.20 |
| ifbench | dpo | defender | 93 | 72 | 21 | 0 | 0 | 0 | 0.23 |
| ifbench | s2300 | challenger | 340 | 198 | 138 | 0 | 0 | 4 | 0.42 |
| ifbench | s2300 | defender | 14 | 12 | 2 | 0 | 0 | 0 | 0.14 |
| ifeval | dpo | challenger | 3 | 3 | 0 | 0 | 0 | 0 | 0.00 |
| ifeval | dpo | defender | 3 | 2 | 1 | 0 | 0 | 0 | 0.33 |
| ifeval | s2300 | challenger | 27 | 24 | 3 | 0 | 0 | 0 | 0.11 |
| omega_out | dpo | challenger | 1 | 0 | 0 | 1 | 0 | 0 | 1.00 |
| omega_out | dpo | defender | 47 | 33 | 0 | 12 | 2 | 0 | 0.30 |
| omega_out | s2300 | challenger | 21 | 16 | 0 | 5 | 0 | 0 | 0.24 |
| omega_out | s2300 | defender | 4 | 2 | 0 | 2 | 0 | 0 | 0.50 |

| task | OMEGA success | unsure → | hand reach | dpo resolved | open (reasons) | reverse | s2300 resolved | V open | hand verdict |
|---|---|---|---|---|---|---|---|---|---|
| ifbench|headline | – | strict | 43 | 31 | 20 (other 2, challenger_unextended 2, dpo_one_good 8, gamed_dominated 8) | 2 | 5 | 1 | Reach |
| ifeval|headline | – | strict | 7 | 1 | 0 () | 1 | 0 | 0 | Reach |
| omega_out|headline | union | strict | 1 | 10 | 3 (other 1, challenger_unextended 1, dpo_one_good 1) | 0 | 1 | 0 | Inconclusive |
| ifbench|headline | – | lenient | 43 | 31 | 20 (other 2, challenger_unextended 2, dpo_one_good 8, gamed_dominated 8) | 2 | 5 | 1 | Reach |
| ifeval|headline | – | lenient | 7 | 1 | 0 () | 1 | 0 | 0 | Reach |
| omega_out|headline | union | lenient | 1 | 10 | 3 (other 1, challenger_unextended 1, dpo_one_good 1) | 0 | 1 | 0 | Inconclusive |
| omega_out|headline | doubly | strict | 2 | 8 | 4 (other 1, challenger_unextended 1, dpo_one_good 2) | 0 | 1 | 0 | Inconclusive |
| omega_out|headline | doubly | lenient | 2 | 8 | 4 (other 1, challenger_unextended 1, dpo_one_good 2) | 0 | 1 | 0 | Inconclusive |

Per prompt, ifeval|headline (strict mapping; OMEGA under union / doubly):

| prompt | side | status (union) | status (doubly) | dpo credited / read / good | s2300 credited / read / good (fresh) |
|---|---|---|---|---|---|
| `ifeval_1130` | R | reach | – | 0 / 0 / 0 | 24 / 9 / 6 (5) |
| `ifeval_1314` | R | reach | – | 0 / 0 / 0 | 22 / 3 / 3 (2) |
| `ifeval_2247` | R | reach | – | 0 / 0 / 0 | 24 / 3 / 3 (2) |
| `ifeval_2350` | R | reach | – | 0 / 0 / 0 | 24 / 3 / 3 (2) |
| `ifeval_2447` | R | reach | – | 1 / 1 / 0 | 22 / 3 / 3 (2) |
| `ifeval_2563` | R | reach | – | 0 / 0 / 0 | 24 / 3 / 3 (2) |
| `ifeval_2785` | V | reverse | – | 19 / 3 / 3 | 0 / 0 / 0 (0) |
| `ifeval_3326` | R | dpo_resolved | – | 5 / 2 / 2 | 8 / 0 / 0 (0) |
| `ifeval_3478` | R | reach | – | 0 / 0 / 0 | 10 / 3 / 3 (2) |

Per prompt, omega_out|headline (strict mapping; OMEGA under union / doubly):

| prompt | side | status (union) | status (doubly) | dpo credited / read / good | s2300 credited / read / good (fresh) |
|---|---|---|---|---|---|
| `algebra_func_intersection_coords_test_out_011` | R | dpo_resolved | dpo_resolved | 21 / 6 / 4 | 8 / 1 / 1 (0) |
| `arithmetic_list_prime_factors_test_out_045` | V | s2300_resolved | s2300_resolved | 1 / 1 / 0 | 4 / 4 / 2 (2) |
| `combinatory_probability_exactly_n_specific_fixed_test_out_027` | R | dpo_resolved | dpo_resolved | 3 / 2 / 2 | 8 / 0 / 0 (0) |
| `combinatory_probability_exactly_n_specific_fixed_test_out_047` | R | dpo_resolved | dpo_resolved | 7 / 6 / 5 | 8 / 0 / 0 (0) |
| `combinatory_probability_no_specific_letter_fixed_test_out_004` | R | dpo_resolved | dpo_resolved | 5 / 2 / 2 | 8 / 0 / 0 (0) |
| `geometry_basic_test_out_010` | R | open_challenger_unextended | open_challenger_unextended | 9 / 9 / 0 | 0 / 0 / 0 (0) |
| `geometry_perpendicular_intersection_test_out_011` | R | open_dpo_one_good | open_dpo_one_good | 1 / 1 / 1 | 20 / 3 / 3 (2) |
| `geometry_perpendicular_intersection_test_out_033` | R | dpo_resolved | dpo_resolved | 4 / 3 / 3 | 8 / 0 / 0 (0) |
| `geometry_perpendicular_intersection_test_out_055` | R | open | open | 0 / 0 / 0 | 2 / 2 / 0 (0) |
| `geometry_perpendicular_intersection_test_out_057` | R | dpo_resolved | dpo_resolved | 8 / 5 / 5 | 8 / 0 / 0 (0) |
| `geometry_perpendicular_intersection_test_out_068` | R | reach | reach | 0 / 0 / 0 | 33 / 3 / 3 (2) |
| `geometry_perpendicular_intersection_test_out_069` | R | dpo_resolved | reach | 2 / 2 / 2 | 29 / 9 / 6 (6) |
| `geometry_perpendicular_intersection_test_out_073` | R | dpo_resolved | open_dpo_one_good | 3 / 2 / 2 | 19 / 3 / 3 (2) |
| `geometry_perpendicular_intersection_test_out_075` | R | dpo_resolved | dpo_resolved | 4 / 4 / 4 | 7 / 0 / 0 (0) |
| `numbertheory_lte_qr_test_out_023` | R | dpo_resolved | dpo_resolved | 10 / 5 / 3 | 2 / 0 / 0 (0) |

IFBench hand-reach prompts (strict mapping, 43): `ifbench_0`, `ifbench_1`, `ifbench_128`, `ifbench_133`, `ifbench_136`, `ifbench_154`, `ifbench_166`, `ifbench_169`, `ifbench_170`, `ifbench_173`, `ifbench_179`, `ifbench_186`, `ifbench_187`, `ifbench_188`, `ifbench_189`, `ifbench_19`, `ifbench_203`, `ifbench_204`, `ifbench_206`, `ifbench_207`, `ifbench_209`, `ifbench_211`, `ifbench_217`, `ifbench_220`, `ifbench_226`, `ifbench_248`, `ifbench_252`, `ifbench_253`, `ifbench_264`, `ifbench_267`, `ifbench_268`, `ifbench_269`, `ifbench_271`, `ifbench_280`, `ifbench_281`, `ifbench_284`, `ifbench_290`, `ifbench_3`, `ifbench_4`, `ifbench_64`, `ifbench_67`, `ifbench_78`, `ifbench_79`
IFBench open (3): `ifbench_214`, `ifbench_266`, `ifbench_83`
IFBench open_challenger_unextended (2): `ifbench_126`, `ifbench_47`
IFBench open_dpo_one_good (8): `ifbench_13`, `ifbench_155`, `ifbench_222`, `ifbench_225`, `ifbench_250`, `ifbench_287`, `ifbench_89`, `ifbench_92`
IFBench open_gamed_dominated (8): `ifbench_158`, `ifbench_200`, `ifbench_201`, `ifbench_202`, `ifbench_215`, `ifbench_272`, `ifbench_49`, `ifbench_80`
