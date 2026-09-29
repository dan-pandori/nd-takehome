# Distinct-proof statistics with start-index normalisation

Recounted from the saved `found_*.jsonl` files by `normalize.py`. "raw" = as originally counted (start-index variants counted separately).

| arm | round | attempts | pool | distinct proofs raw → norm | written ≥8 raw → norm | ≥9 raw → norm | ≥10 raw → norm | theorems with an 8 / 9 / 10-line proof | frontier written/pruned (norm) | padded frac (norm) |
|---|---:|---:|---|---|---|---|---|---|---|---:|
| ei_abs_s0 | 4 | 128 | targets | 80,197 → 3,320 | 1,819 → 171 | 69 → 12 | 0 → 0 | 128 / 9 / 0 | 9 / 9 | 0.56 |
| ei_abs_s0 | 4 | 128 | transfer | 40,765 → 2,115 | 765 → 102 | 31 → 6 | 0 → 0 | 83 / 5 / 0 | 9 / 9 | 0.58 |
| ei_abs_s0 | 8 | 256 | targets | 109,008 → 3,875 | 4,205 → 275 | 375 → 37 | 30 → 4 | 190 / 26 / 2 | 9 / 9 | 0.59 |
| ei_abs_s0 | 8 | 256 | transfer | 56,530 → 2,659 | 2,028 → 193 | 195 → 20 | 0 → 0 | 141 / 19 / 0 | 9 / 9 | 0.61 |
| ei_abs_s0_cont | 16 | 512 | targets | 137,828 → 4,506 | 7,643 → 380 | 1086 → 70 | 151 → 13 | 246 / 46 / 9 | 10 / 10 | 0.61 |
| ei_abs_s0_cont | 16 | 512 | transfer | 75,085 → 3,330 | 3,628 → 271 | 397 → 29 | 0 → 0 | 180 / 26 / 0 | 9 / 9 | 0.64 |
| frozen_abs_s0 | 4 | 128 | targets | 56,494 → 2,489 | 191 → 31 | 0 → 0 | 0 → 0 | 24 / 0 / 0 | 8 / 8 | 0.55 |
| frozen_abs_s0 | 4 | 128 | transfer | 31,209 → 1,346 | 32 → 8 | 0 → 0 | 0 → 0 | 7 / 0 / 0 | 8 / 7 | 0.54 |
| frozen_abs_s0 | 8 | 256 | targets | 73,510 → 2,796 | 333 → 37 | 0 → 0 | 0 → 0 | 27 / 0 / 0 | 8 / 8 | 0.57 |
| frozen_abs_s0 | 8 | 256 | transfer | 40,237 → 1,528 | 54 → 13 | 0 → 0 | 0 → 0 | 10 / 0 / 0 | 8 / 8 | 0.56 |
| frozen_abs_s0_cont | 16 | 512 | targets | 87,412 → 3,149 | 512 → 48 | 0 → 0 | 0 → 0 | 31 / 0 / 0 | 8 / 8 | 0.58 |
| frozen_abs_s0_cont | 16 | 512 | transfer | 47,393 → 1,724 | 92 → 17 | 0 → 0 | 0 → 0 | 14 / 0 / 0 | 8 / 8 | 0.57 |
| ei_abs_s1 | 4 | 128 | targets | 81,398 → 3,314 | 1,885 → 160 | 42 → 9 | 0 → 0 | 123 / 8 / 0 | 9 / 9 | 0.57 |
| ei_abs_s1 | 4 | 128 | transfer | 41,576 → 2,059 | 881 → 95 | 26 → 5 | 0 → 0 | 77 / 5 / 0 | 9 / 9 | 0.56 |
| ei_abs_s1 | 8 | 256 | targets | 109,854 → 3,881 | 4,795 → 278 | 385 → 31 | 31 → 3 | 194 / 22 / 3 | 9 / 9 | 0.59 |
| ei_abs_s1 | 8 | 256 | transfer | 57,412 → 2,657 | 2,204 → 205 | 176 → 22 | 0 → 0 | 141 / 20 / 0 | 9 / 9 | 0.60 |
| frozen_abs_s1 | 4 | 128 | targets | 56,765 → 2,496 | 194 → 28 | 0 → 0 | 0 → 0 | 22 / 0 / 0 | 8 / 8 | 0.55 |
| frozen_abs_s1 | 4 | 128 | transfer | 31,277 → 1,355 | 33 → 9 | 0 → 0 | 0 → 0 | 8 / 0 / 0 | 8 / 7 | 0.55 |
| frozen_abs_s1 | 8 | 256 | targets | 73,464 → 2,807 | 317 → 38 | 0 → 0 | 0 → 0 | 25 / 0 / 0 | 8 / 8 | 0.56 |
| frozen_abs_s1 | 8 | 256 | transfer | 40,225 → 1,532 | 54 → 14 | 0 → 0 | 0 → 0 | 11 / 0 / 0 | 8 / 7 | 0.56 |
| ei_abs_long_s0 | 4 | 128 | targets | 82,174 → 3,268 | 2,120 → 165 | 48 → 9 | 0 → 0 | 129 / 9 / 0 | 9 / 9 | 0.55 |
| ei_abs_long_s0 | 4 | 128 | transfer | 41,268 → 2,121 | 950 → 108 | 10 → 5 | 0 → 0 | 88 / 5 / 0 | 9 / 8 | 0.57 |
| ei_abs_long_s0 | 8 | 256 | targets | 109,074 → 3,777 | 4,854 → 274 | 354 → 30 | 4 → 2 | 190 / 24 / 2 | 9 / 9 | 0.57 |
| ei_abs_long_s0 | 8 | 256 | transfer | 56,905 → 2,680 | 2,338 → 208 | 120 → 21 | 0 → 0 | 152 / 17 / 0 | 9 / 9 | 0.60 |

## pass@k evaluation files (eval_set.py outputs)

| file | theorems solved | distinct proofs raw → norm | written 7 / 8 / 9 / 10 (norm) | frontier written/pruned (norm) |
|---|---:|---|---|---|
| final_transfer_k128 | 1353/1638 | 45,059 → 2,434 | 563 / 188 / 33 / 2 | 9 / 9 |
| stage1_transfer_k128 | 866/1638 | 31,185 → 1,356 | 211 / 11 / 0 / 0 | 8 / 7 |
| stage1_abs_transfer2_k16 | 732/1638 | 6,920 → 926 | 108 / 1 / 0 / 0 | 7 / 7 |
| stage1_rel_transfer2_k16 | 664/1638 | 817 → 817 | 79 / 0 / 0 / 0 | 7 / 7 |
| stage1_absfixed_transfer2_k16 | 631/1638 | 774 → 774 | 0 / 0 / 0 / 0 | 6 / 6 |
| stage1_abs_transfer_k16 | 605/1600 | 5,525 → 804 | 120 / 1 / 0 / 0 | 7 / 7 |
| stage1_rel_transfer_k16 | 532/1600 | 669 → 669 | 79 / 0 / 0 / 0 | 7 / 7 |
