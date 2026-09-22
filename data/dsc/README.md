# ds-composition sets (`dsc_assemble.py`, seed 0; every record re-verified by `nd_verify`, cap asserted, depth-3 excluded in the pruned and written form)

Pools: `data/p2/pool_cap6_recon.jsonl` (723,534 classes, the control's pool; full-pool length shares 10.42 / 12.63 / 15.53 / 20.60 / 40.82 %), `data/dsc/raw_ore*.w*.jsonl` (A2 ORE top-up: `make_coverage_sets.py gen --only rule:ORE`, unchanged generator, output filter only, 2 × 3,000,000 tries, 12,776 raw ORE proofs), `data/p2/pool_cap8.jsonl` (A3's 7–8-line records). Exclusions by renaming class: p2 held-out, `{targets,transfer}_depth3`, `{targets,transfer}_reductio_req`, `r3_1/depth3_req{,_transfer}`, ladder `rl_targets` / `transfer`, validation-36 (14,026 classes). Sets are stored gzipped (`train_<arm>.jsonl.gz`); the pods gunzip them; `train.py --cap` re-asserts the cap and the `lean_seq` round trip on every record.

## Shape table

| quantity | c0 | a1 | a2 | a3 | a4 |
|---|---|---|---|---|---|
| records | 155,000 | 155,000 | 155,000 | 155,000 | 155,000 |
| length 2 | 31,000 (20.0 %) | 16,145 (10.4 %) | 31,000 (20.0 %) | 22,142 (14.3 %) | 0 (0.0 %) |
| length 3 | 31,000 (20.0 %) | 19,575 (12.6 %) | 31,000 (20.0 %) | 22,143 (14.3 %) | 7,750 (5.0 %) |
| length 4 | 31,000 (20.0 %) | 24,079 (15.5 %) | 31,000 (20.0 %) | 22,143 (14.3 %) | 23,250 (15.0 %) |
| length 5 | 31,000 (20.0 %) | 31,925 (20.6 %) | 31,000 (20.0 %) | 22,143 (14.3 %) | 46,500 (30.0 %) |
| length 6 | 31,000 (20.0 %) | 63,276 (40.8 %) | 31,000 (20.0 %) | 22,143 (14.3 %) | 77,500 (50.0 %) |
| length 7 | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 22,143 (14.3 %) | 0 (0.0 %) |
| length 8 | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 22,143 (14.3 %) | 0 (0.0 %) |
| written box depth 0 | 82,393 | 57,152 | 77,770 | 57,705 | 36,885 |
| written box depth 1 | 54,883 | 78,864 | 64,367 | 70,364 | 95,467 |
| written box depth 2 | 17,724 | 18,984 | 12,863 | 26,931 | 22,648 |
| depth ≥ 3 (pruned or written) | 0 | 0 | 0 | 0 | 0 |
| proofs using `AS` | 46.84 % | 63.13 % | 49.83 % | 62.77 % | 76.20 % |
| proofs using `IMPI` | 36.35 % | 33.30 % | 29.56 % | 36.49 % | 37.66 % |
| proofs using `IMPE` | 40.24 % | 45.27 % | 39.39 % | 42.73 % | 49.30 % |
| proofs using `NEGI` | 9.93 % | 28.33 % | 11.55 % | 16.50 % | 36.67 % |
| proofs using `DN` | 8.33 % | 26.60 % | 10.90 % | 15.09 % | 34.43 % |
| proofs using `NEGE` | 12.03 % | 20.63 % | 13.01 % | 16.43 % | 26.11 % |
| proofs using `ANDI` | 22.93 % | 21.89 % | 16.13 % | 22.68 % | 25.12 % |
| proofs using `ORI1` | 20.56 % | 16.34 % | 18.70 % | 20.39 % | 13.37 % |
| proofs using `ORI2` | 20.28 % | 15.91 % | 18.43 % | 19.68 % | 13.05 % |
| proofs using `R` | 2.78 % | 2.73 % | 1.68 % | 8.19 % | 3.22 % |
| proofs using `ORE` | 1.46 % | 2.82 % | 10.00 % | 16.31 % | 3.49 % |
| proofs using `ANDE1` | 2.16 % | 2.18 % | 4.12 % | 2.92 % | 2.47 % |
| proofs using `ANDE2` | 2.13 % | 2.09 % | 4.01 % | 2.87 % | 2.32 % |
| proofs using `BOTE` | 1.95 % | 2.03 % | 5.00 % | 3.01 % | 2.52 % |
| proofs using `ANDE1` or `ANDE2` | 4.25 % | 4.21 % | 8.04 % | 5.63 % | 4.74 % |
| boxes inside an `ORE` branch (proofs) | 49 | 78 | 291 | 823 | 98 |
| 0 premises | 19,112 | 14,220 | 17,880 | 13,370 | 12,438 |
| 1 premises | 61,422 | 57,007 | 63,501 | 56,562 | 53,243 |
| 2 premises | 66,018 | 73,739 | 69,871 | 72,423 | 76,569 |
| 3 premises | 8,448 | 10,034 | 3,748 | 12,645 | 12,750 |
| classically unsatisfiable premise set | 16.7 % | 28.0 % | 16.6 % | 20.0 % | 33.0 % |
| conclusion is a premise | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % |
| derived-`ORE` proofs (pruned / written) | 88 / 88 | 1,458 / 1,458 | 3,284 / 3,284 | 4,717 / 4,717 | 1,813 / 1,813 |
| reductio proofs (pruned / written) | 10,547 / 10,547 | 38,994 / 38,994 | 15,101 / 15,101 | 20,404 / 20,404 | 50,499 / 50,499 |
| `lean_seq` tokens, prompt + proof mean | 54.2 + 84.3 = 138.4 | 54.3 + 96.7 = 150.9 | 53.5 + 83.4 = 136.9 | 55.2 + 99.8 = 155.0 | 54.7 + 106.9 = 161.7 |
| `lean_seq` tokens, proof max / total max | 328 / 464 | 398 / 558 | 323 / 462 | 324 / 434 | 398 / 558 |

"Classically unsatisfiable premise set": the premises have no satisfying valuation (truth tables), a wider definition than the proposal's 6.1 % "contradictory-premise theorems"; the same function is applied to every set.

## A2 quota report (`assemble_report_a2.json`)

| rule | quota | already in earlier quota picks | added | added by length | available by length |
|---|---|---|---|---|---|
| ORE | 15,500 | 0 | 15,500 | {'2': 0, '3': 0, '4': 17, '5': 708, '6': 14775} | {'2': 0, '3': 0, '4': 20, '5': 815, '6': 17010} |
| ANDE | 12,400 | 2,387 | 10,013 | {'2': 389, '3': 674, '4': 3426, '5': 2886, '6': 2638} | {'2': 877, '3': 1520, '4': 7719, '5': 6506, '6': 5947} |
| BOTE | 7,750 | 447 | 7,303 | {'2': 0, '3': 30, '4': 1575, '5': 2398, '6': 3300} | {'2': 0, '3': 42, '4': 2234, '5': 3400, '6': 4680} |

## Overlap with the evaluation pools (renaming classes; order-sensitive `key` / premise-order-insensitive)

| pool (n) | c0 | a1 | a2 | a3 | a4 |
|---|---|---|---|---|---|
| `data/p2/heldout.jsonl` (5,000) | 0 / 21 | 0 / 21 | 0 / 19 | 0 / 14 | 0 / 25 |
| `data/p2/targets_depth3.jsonl` (1,000) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `data/p2/transfer_depth3.jsonl` (500) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `data/p2/targets_reductio_req.jsonl` (300) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `data/p2/transfer_reductio_req.jsonl` (150) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `data/r3_1/depth3_req.jsonl` (300) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `data/r3_1/depth3_req_transfer.jsonl` (100) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `data/ladder/rl_targets.jsonl` (4,495) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 4 | 0 / 0 |
| `data/ladder/transfer.jsonl` (2,285) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 |
| `targets/validation_36.jsonl` (36) | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 0 |

Order-sensitive overlaps are 0 by construction (exclusion by `key`); the premise-order-insensitive count is the number of set classes that equal a pool class after sorting premises and minimising over the 24 atom permutations (the lean-format review's definition).

## Render check (3,000 records → `lean_seq` text → inverse; Lean on 1,000 literal texts; 300 statement-swapped negatives)

| set | rendered | inverse identical | Lean accepted (of 1,000) | negatives rejected (of 300) |
|---|---|---|---|---|
| c0 | 3000 | 3000 | 1000 | 300 |
| a1 | 3000 | 3000 | 1000 | 300 |
| a2 | 3000 | 3000 | 1000 | 300 |
| a3 | 3000 | 3000 | 1000 | 300 |
| a4 | 3000 | 3000 | 1000 | 300 |

## Assembly reports

- **a1**: counts {'2': 16145, '3': 19575, '4': 24079, '5': 31925, '6': 63276}; sources ['pool_cap6_recon.jsonl']; scan {"pool_cap6_recon.jsonl": {"read": 723534, "eligible": 586581, "depth3": 131953, "depth3_pruned": 131953, "excluded_class": 5000}}; 66 s.
- **a2**: counts {'2': 31000, '3': 31000, '4': 31000, '5': 31000, '6': 31000}; sources ['pool_cap6_recon.jsonl', 'raw_ore.w0.jsonl', 'raw_ore.w1.jsonl', 'raw_ore_b.w0.jsonl', 'raw_ore_b.w1.jsonl']; scan {"pool_cap6_recon.jsonl": {"read": 723534, "eligible": 586581, "depth3": 131953, "depth3_pruned": 131953, "excluded_class": 5000}, "raw_ore.w0.jsonl": {"read": 3184, "dup_class": 1488, "excluded_class": 12, "eligible": 1684}, "raw_ore.w1.jsonl": {"read": 3206, "dup_class": 1602, "eligible": 1594, "excluded_class": 10}, "raw_ore_b.w0.jsonl": {"read": 3257, "dup_class": 1661, "eligible": 1586, "excluded_class": 10}, "raw_ore_b.w1.jsonl": {"read": 3129, "dup_class": 1662, "eligible": 1454, "excluded_class": 13}}; 60 s.
- **a3**: counts {'2': 22142, '3': 22143, '4': 22143, '5': 22143, '6': 22143, '7': 22143, '8': 22143}; sources ['pool_cap6_recon.jsonl', 'pool_cap8.jsonl']; scan {"pool_cap6_recon.jsonl": {"read": 723534, "eligible": 586581, "depth3": 131953, "depth3_pruned": 131953, "excluded_class": 5000}, "pool_cap8.jsonl": {"read": 2435041, "dup_class": 7309, "eligible": 396249, "depth3": 70510, "depth3_pruned": 70510, "excluded_class": 304}}; 118 s.
- **a4**: counts {'2': 0, '3': 7750, '4': 23250, '5': 46500, '6': 77500}; sources ['pool_cap6_recon.jsonl']; scan {"pool_cap6_recon.jsonl": {"read": 723534, "eligible": 586581, "depth3": 131953, "depth3_pruned": 131953, "excluded_class": 5000}}; 99 s.
