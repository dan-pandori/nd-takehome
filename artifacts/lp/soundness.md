| corpus | distinct texts | Lean accepts | Lean rejects | filter rejects | **false rejects** | coverage of Lean rejects |
|---|---:|---:|---:|---:|---:|---:|
| C1 cap-horizon__stage1_k14_s0 | 250,905 | 143,094 | 107,811 | 107,811 | **0** | 100.00 % |
| C1 ds-composition__stage1_a1_s1 | 286,406 | 141,030 | 145,376 | 145,376 | **0** | 100.00 % |
| C1 ds-composition__stage1_a3_s0 | 302,734 | 168,541 | 134,193 | 134,193 | **0** | 100.00 % |
| C1 ds-generator__stage1_g2_s0 | 129,817 | 49,449 | 80,368 | 80,368 | **0** | 100.00 % |
| C1 lean-format__ei_d3_seq_s0_r8 | 173,949 | 103,487 | 70,462 | 70,462 | **0** | 100.00 % |
| C1 lean-format__stage1_a1_rand_s0 | 155,572 | 78,620 | 76,952 | 76,952 | **0** | 100.00 % |
| C1 lean-format__stage1_full_seq_s0 | 166,955 | 85,072 | 81,883 | 81,883 | **0** | 100.00 % |
| C1 noise-floor__stage1_p2_s3 | 140,331 | 72,646 | 67,685 | 67,685 | **0** | 100.00 % |
| C1 all checkpoints (distinct) | 1,214,162 | 499,565 | 714,597 | 714,597 | **0** | 100.00 % |
| C2 edge_unfold | 17,836 | 17,834 | 2 | 2 | **0** | 100.00 % |
| C2 all | 76,281 | 32,909 | 43,372 | 43,372 | **0** | 100.00 % |
| C2 edge_unfoldall | 9,566 | 9,563 | 3 | 3 | **0** | 100.00 % |
| C2 edge_retype | 11,832 | 23 | 11,809 | 11,809 | **0** | 100.00 % |
| C2 edge_elimins | 13,519 | 4,965 | 8,554 | 8,554 | **0** | 100.00 % |
| C2 edge_name | 1,822 | 71 | 1,751 | 1,751 | **0** | 100.00 % |
| C2 edge_inl | 4,535 | 201 | 4,334 | 4,334 | **0** | 100.00 % |
| C2 edge_atom | 11,997 | 3 | 11,994 | 11,994 | **0** | 100.00 % |
| C2 edge_proj | 807 | 90 | 717 | 717 | **0** | 100.00 % |
| C2 edge_appins | 4,190 | 159 | 4,031 | 4,031 | **0** | 100.00 % |
| C2 edge_elimty | 177 | 0 | 177 | 177 | **0** | 100.00 % |
| C3 disagree (Lean-only accepts) | 5,424 | 5,424 | 0 | 0 | **0** | – |
| C3 all | 19,676 | 7,763 | 11,913 | 11,913 | **0** | 100.00 % |
| C3 leanrej samples | 10,756 | 0 | 10,756 | 10,756 | **0** | 100.00 % |
| C3 lean-judge t5 dump | 3,496 | 2,339 | 1,157 | 1,157 | **0** | 100.00 % |

Lean-ACCEPTED texts by feature (all of them passed the filter unless false_rej > 0):
  C1 all checkpoints (distinct): {'arrow_false_written': 40890, 'elim_on_bot': 13017, 'elim_on_not': 70, 'elim_on_shadowed': 84}
  C2 all: {'arrow_false_written': 28419, 'elim_on_and': 1214, 'elim_on_bot': 658, 'elim_on_not': 1799, 'elim_on_or': 1792, 'elim_on_shadowed': 33}
  C3 all: {'arrow_false_written': 347, 'elim_on_bot': 44, 'elim_on_not': 1403, 'elim_on_shadowed': 19}

filter reasons (C1 distinct): {'app-arg': 147455, 'and-intro': 135142, 'or-intro': 84572, 'function-expected': 64281, 'by-contradiction': 50070, 'and-elim': 43851, 'fun-body': 37606, 'reiterate': 33298, 'app-result': 32551, 'projection': 25638, 'goal': 19600, 'anon-ctor': 10213, 'fun-binder': 7768, 'premise-type': 5613, 'elim': 5071, 'or-intro-target': 4647, 'or-elim-major': 3199, 'unknown-premise': 3120, 'fun-not-pi': 881, 'ascription': 21}
false rejects total: 0 ; stored filter field differs from recomputed: 0
