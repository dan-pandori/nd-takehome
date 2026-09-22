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
| written box depth 0 | 82,393 | 63,617 | 78,926 | 60,616 | 45,054 |
| written box depth 1 | 54,883 | 66,028 | 62,579 | 64,951 | 79,273 |
| written box depth 2 | 17,724 | 25,355 | 13,495 | 29,433 | 30,673 |
| depth ≥ 3 (pruned or written) | 0 | 0 | 0 | 0 | 0 |
| proofs using `AS` | 46.84 % | 58.96 % | 49.08 % | 60.89 % | 70.93 % |
| proofs using `IMPI` | 36.35 % | 42.89 % | 31.45 % | 40.75 % | 50.12 % |
| proofs using `IMPE` | 40.24 % | 44.89 % | 38.99 % | 42.47 % | 48.69 % |
| proofs using `NEGI` | 9.93 % | 14.82 % | 8.91 % | 10.37 % | 19.30 % |
| proofs using `DN` | 8.33 % | 12.35 % | 8.09 % | 8.60 % | 16.06 % |
| proofs using `NEGE` | 12.03 % | 17.36 % | 12.38 % | 14.93 % | 21.90 % |
| proofs using `ANDI` | 22.93 % | 29.04 % | 17.32 % | 25.83 % | 34.28 % |
| proofs using `ORI1` | 20.56 % | 17.80 % | 19.25 % | 21.09 % | 15.33 % |
| proofs using `ORI2` | 20.28 % | 17.44 % | 18.99 % | 20.34 % | 14.99 % |
| proofs using `R` | 2.78 % | 3.65 % | 1.83 % | 8.58 % | 4.35 % |
| proofs using `ORE` | 1.46 % | 2.97 % | 10.00 % | 16.38 % | 3.66 % |
| proofs using `ANDE1` | 2.16 % | 2.62 % | 4.12 % | 3.10 % | 3.05 % |
| proofs using `ANDE2` | 2.13 % | 2.50 % | 4.01 % | 3.06 % | 2.90 % |
| proofs using `BOTE` | 1.95 % | 2.79 % | 5.00 % | 3.33 % | 3.49 % |
| proofs using `ANDE1` or `ANDE2` | 4.25 % | 5.05 % | 8.04 % | 5.99 % | 5.87 % |
| boxes inside an `ORE` branch (proofs) | 49 | 112 | 291 | 831 | 139 |
| 0 premises | 19,112 | 15,686 | 18,613 | 14,180 | 14,353 |
| 1 premises | 61,422 | 56,086 | 59,879 | 54,436 | 51,140 |
| 2 premises | 66,018 | 68,395 | 72,302 | 71,701 | 70,852 |
| 3 premises | 8,448 | 14,833 | 4,206 | 14,683 | 18,655 |
| classically unsatisfiable premise set | 16.7 % | 22.0 % | 17.2 % | 18.1 % | 25.8 % |
| conclusion is a premise | 0.00 % | 0.00 % | 0.00 % | 0.00 % | 0.00 % |
| derived-`ORE` proofs (pruned / written) | 88 / 88 | 153 / 153 | 3,284 / 3,284 | 3,833 / 3,833 | 194 / 194 |
| reductio proofs (pruned / written) | 10,547 / 10,547 | 16,091 / 16,091 | 10,547 / 10,547 | 9,961 / 9,961 | 20,991 / 20,991 |
| `lean_seq` tokens, prompt + proof mean | 54.2 + 84.3 = 138.4 | 55.0 + 95.0 = 150.1 | 53.3 + 82.3 = 135.6 | 55.4 + 98.7 = 154.1 | 55.6 + 104.6 = 160.2 |
| `lean_seq` tokens, proof max / total max | 328 / 464 | 398 / 558 | 323 / 462 | 398 / 558 | 398 / 558 |

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
| `data/p2/heldout.jsonl` (5,000) | 0 / 21 | 0 / 26 | 0 / 20 | 0 / 14 | 0 / 27 |
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

- **a1**: counts {'2': 16145, '3': 19575, '4': 24079, '5': 31925, '6': 63276}; sources ['pool_cap6_recon.jsonl']; scan {"pool_cap6_recon.jsonl": {"read": 723534, "eligible": 586581, "depth3": 131953, "depth3_pruned": 131953, "excluded_class": 5000}}; 58 s.
- **a2**: counts {'2': 31000, '3': 31000, '4': 31000, '5': 31000, '6': 31000}; sources ['pool_cap6_recon.jsonl', 'raw_ore.w0.jsonl', 'raw_ore.w1.jsonl', 'raw_ore_b.w0.jsonl', 'raw_ore_b.w1.jsonl']; scan {"pool_cap6_recon.jsonl": {"read": 723534, "eligible": 586581, "depth3": 131953, "depth3_pruned": 131953, "excluded_class": 5000}, "raw_ore.w0.jsonl": {"read": 3184, "dup_class": 1488, "excluded_class": 12, "eligible": 1684}, "raw_ore.w1.jsonl": {"read": 3206, "dup_class": 1602, "eligible": 1594, "excluded_class": 10}, "raw_ore_b.w0.jsonl": {"read": 3257, "dup_class": 1661, "eligible": 1586, "excluded_class": 10}, "raw_ore_b.w1.jsonl": {"read": 3129, "dup_class": 1662, "eligible": 1454, "excluded_class": 13}}; 60 s.
- **a3**: counts {'2': 22142, '3': 22143, '4': 22143, '5': 22143, '6': 22143, '7': 22143, '8': 22143}; sources ['pool_cap6_recon.jsonl', 'pool_cap8.jsonl']; scan {"pool_cap6_recon.jsonl": {"read": 723534, "eligible": 586581, "depth3": 131953, "depth3_pruned": 131953, "excluded_class": 5000}, "pool_cap8.jsonl": {"read": 2435041, "dup_class": 7309, "eligible": 396249, "depth3": 70510, "depth3_pruned": 70510, "excluded_class": 304}}; 118 s.
- **a4**: counts {'2': 0, '3': 7750, '4': 23250, '5': 46500, '6': 77500}; sources ['pool_cap6_recon.jsonl']; scan {"pool_cap6_recon.jsonl": {"read": 723534, "eligible": 586581, "depth3": 131953, "depth3_pruned": 131953, "excluded_class": 5000}}; 59 s.
