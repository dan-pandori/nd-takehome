# cap-horizon sets (`kh_assemble.py`; every record re-verified by `nd_verify`, its cap asserted, its `lean_seq` round trip checked, depth-3 excluded in the pruned **and** the written form)

**Every arm here is above the take-home's cap-6 rule and is labelled "cap N" in every table. None is proposed for adoption as a take-home submission.**

## Sources

- **Bins of length ≤ 6: K6's own training set** `data/p2/train_depth3_f0_a1.jsonl` (the `ds-composition` control C0 = `lean-format`'s a1 set, 155,000 records, 31,000 per pruned length 2–6, pulled from `hf://buckets/dan-pandori/nd-rl/lean-format/`). `k8add` takes **all 155,000 records, byte-identical lines**; `k10`/`k12`/`k14` take a **uniform per-bin subsample (seed 0)**. So every arm's short bins are a *subset of the control's exact records*: "short proofs removed" is pure subsetting and there is no re-draw noise below the cap.
- **Bins of length ≥ 7: `data/kh/pool_long_kh.jsonl`** (`kh_gen.py`). Generator: gen.sample_one short mode, Gen(max_prem=3, max_depth=3), probabilities untouched. Filter: pruned length in [7,14]; per-length storage caps {7: 45000, 8: 45000, 9: 30000, 10: 30000, 11: 30000, 12: 30000, 13: 30000, 14: 30000}; no per-pattern cap. There is deliberately **no per-pattern cap** (`make_coverage_sets.py gen`'s `--cap_np` / `--cap_pat`): those caps are what pattern-enriched the pool behind `ds-composition`'s 07:10 confound. Within a length bin the stored records are the first N encountered, an unbiased sample of that length's natural distribution, so a uniform draw from the bin **is** the natural-rate draw.
  - worker seed 31000: 7,638,294 tries, 692 s, stored per length {'7': 45000, '8': 45000, '9': 30000, '10': 30000, '11': 30000, '12': 30000, '13': 30000, '14': 30000}
  - worker seed 31001: 7,674,660 tries, 686 s, stored per length {'7': 45000, '8': 45000, '9': 30000, '10': 30000, '11': 30000, '12': 30000, '13': 30000, '14': 30000}
  - merged: **518,843 distinct renaming classes**, 21,157 cross-worker duplicate classes dropped; per length {'7': 84048, '8': 85002, '9': 57414, '10': 57697, '11': 58317, '12': 58552, '13': 58803, '14': 59010}

**Disclosed difference from K8flat (`ds-composition`'s A3).** A3's 7–8-line bins came from `data/p2/pool_cap8.jsonl`, which is in no bucket and no longer on this host. K8add's 7–8 bins are therefore a **fresh draw from the same generator settings**, not the same records. This is exactly the manipulation the sibling `noise-floor` run is measuring, and the K8add-vs-K8flat comparison is read against its table.

## Per-length achieved counts

| length | k8add (cap 8) | k10 (cap 10) | k12 (cap 12) | k14 (cap 14) |
|---|---|---|---|---|
| 2 | 31,000 (14.3 %) | 17,223 (11.1 %) | 14,091 (9.1 %) | 11,924 (7.7 %) |
| 3 | 31,000 (14.3 %) | 17,223 (11.1 %) | 14,091 (9.1 %) | 11,923 (7.7 %) |
| 4 | 31,000 (14.3 %) | 17,222 (11.1 %) | 14,091 (9.1 %) | 11,923 (7.7 %) |
| 5 | 31,000 (14.3 %) | 17,222 (11.1 %) | 14,091 (9.1 %) | 11,923 (7.7 %) |
| 6 | 31,000 (14.3 %) | 17,222 (11.1 %) | 14,091 (9.1 %) | 11,923 (7.7 %) |
| 7 | 31,000 (14.3 %) | 17,222 (11.1 %) | 14,091 (9.1 %) | 11,923 (7.7 %) |
| 8 | 31,000 (14.3 %) | 17,222 (11.1 %) | 14,091 (9.1 %) | 11,923 (7.7 %) |
| 9 | 0 | 17,222 (11.1 %) | 14,091 (9.1 %) | 11,923 (7.7 %) |
| 10 | 0 | 17,222 (11.1 %) | 14,091 (9.1 %) | 11,923 (7.7 %) |
| 11 | 0 | 0 | 14,091 (9.1 %) | 11,923 (7.7 %) |
| 12 | 0 | 0 | 14,090 (9.1 %) | 11,923 (7.7 %) |
| 13 | 0 | 0 | 0 | 11,923 (7.7 %) |
| 14 | 0 | 0 | 0 | 11,923 (7.7 %) |
| **total** | **217,000** | **155,000** | **155,000** | **155,000** |

`k8add` is the **only arm whose set size differs** (217,000 against 155,000). Every table that shows it says so, and the K8add-vs-K8flat comparison is reported as the confound break it is (A3 added 7–8-line proofs *and* removed 8,857 proofs per ≤ 6-line bin; K8add adds without removing), not as a set-size result.

## Fill disclosure

- **k8add**: none: every long bin filled from its own length
- **k10**: none: every long bin filled from its own length
- **k12**: none: every long bin filled from its own length
- **k14**: none: every long bin filled from its own length

## Long-bin eligibility scan (the pool, per arm)

| arm | pool read | in range | excluded: eval-pool class | excluded: control-set class | excluded: depth-3 | eligible |
|---|---:|---:|---:|---:|---:|---:|
| k8add | 518,843 | 169,050 | 253 | 3,723 | 23,656 | 141,418 |
| k10 | 518,843 | 284,161 | 333 | 5,637 | 43,032 | 235,159 |
| k12 | 518,843 | 401,030 | 369 | 6,536 | 77,721 | 316,404 |
| k14 | 518,843 | 518,843 | 401 | 7,077 | 121,223 | 390,142 |

## Overlap / disjointness (renaming class)

| arm | records | distinct renaming classes | distinct rendered texts | records over cap | depth-3 records | overlap with the 11 evaluation pools |
|---|---:|---:|---:|---:|---:|---:|
| k8add | 217,000 | 217,000 | 217,000 | 0 | 0 | **0** |
| k10 | 155,000 | 155,000 | 155,000 | 0 | 0 | **0** |
| k12 | 155,000 | 155,000 | 155,000 | 0 | 0 | **0** |
| k14 | 155,000 | 155,000 | 155,000 | 0 | 0 | **0** |

Exclusion set: 14,026 renaming classes over `heldout.jsonl`, `targets_depth3.jsonl`, `transfer_depth3.jsonl`, `targets_reductio_req.jsonl`, `transfer_reductio_req.jsonl`, `depth3_req.jsonl`, `depth3_req_transfer.jsonl`, `rl_targets.jsonl`, `transfer.jsonl`, `validation_36.jsonl`, `targets_depth3_sub250.jsonl`. Asserted at assembly for every emitted record.

## Shape

| quantity | k8add | k10 | k12 | k14 |
|---|---|---|---|---|
| records | 217,000 | 155,000 | 155,000 | 155,000 |
| mean term size (pruned) | 29.04 | 32.33 | 35.91 | 39.50 |
| median term size | 26 | 29 | 32 | 35 |
| max term size | 127 | 132 | 178 | 226 |
| written box depth 0 | 84,835 | 47,253 | 38,617 | 32,791 |
| written box depth 1 | 91,566 | 68,685 | 66,669 | 64,089 |
| written box depth 2 | 40,599 | 39,062 | 49,714 | 58,120 |
| depth ≥ 3 (pruned or written) | 0 | 0 | 0 | 0 |
| proofs classified `reductio` | 15,297 (7.05 %) | 12,951 (8.36 %) | 16,703 (10.78 %) | 19,481 (12.57 %) |
| proofs classified `derived_ore` | 8,066 (3.72 %) | 15,353 (9.91 %) | 23,216 (14.98 %) | 30,963 (19.98 %) |
| proofs classified `derived_ore_strict` | 6,974 (3.21 %) | 13,511 (8.72 %) | 20,680 (13.34 %) | 28,036 (18.09 %) |
| proofs classified `derived_dn` | 15,525 (7.15 %) | 13,158 (8.49 %) | 16,961 (10.94 %) | 19,797 (12.77 %) |
| proofs using `AS` | 60.91 % | 69.51 % | 75.09 % | 78.84 % |
| proofs using `IMPI` | 40.24 % | 41.22 % | 42.95 % | 44.11 % |
| proofs using `IMPE` | 42.34 % | 43.71 % | 45.44 % | 46.77 % |
| proofs using `NEGI` | 10.94 % | 12.66 % | 15.21 % | 17.29 % |
| proofs using `DN` | 9.19 % | 10.90 % | 13.73 % | 15.73 % |
| proofs using `NEGE` | 14.97 % | 18.44 % | 22.18 % | 25.30 % |
| proofs using `ANDI` | 25.81 % | 29.19 % | 32.57 % | 35.15 % |
| proofs using `ORI1` | 21.38 % | 23.02 % | 24.12 % | 25.82 % |
| proofs using `ORI2` | 20.53 % | 22.60 % | 24.39 % | 25.88 % |
| proofs using `R` | 74.48 % | 76.57 % | 78.98 % | 81.14 % |
| proofs using `ORE` | 16.77 % | 32.76 % | 44.16 % | 52.38 % |
| proofs using `ANDE1` | 3.09 % | 3.73 % | 4.41 % | 5.11 % |
| proofs using `ANDE2` | 2.96 % | 3.62 % | 4.17 % | 4.80 % |
| proofs using `BOTE` | 3.24 % | 5.81 % | 8.04 % | 9.99 % |

### Term size by pruned length

| length | k8add mean / max | k10 mean / max | k12 mean / max | k14 mean / max |
|---|---|---|---|---|
| 2 | 18.2 / 97 | 18.1 / 97 | 18.1 / 97 | 18.1 / 97 |
| 3 | 20.7 / 55 | 20.7 / 55 | 20.7 / 55 | 20.7 / 52 |
| 4 | 27.1 / 127 | 27.0 / 124 | 27.0 / 127 | 27.0 / 127 |
| 5 | 31.7 / 97 | 31.6 / 92 | 31.7 / 97 | 31.6 / 92 |
| 6 | 32.5 / 115 | 32.5 / 115 | 32.6 / 94 | 32.8 / 115 |
| 7 | 36.0 / 117 | 35.9 / 124 | 35.7 / 124 | 35.8 / 115 |
| 8 | 37.1 / 127 | 37.1 / 109 | 37.0 / 126 | 37.4 / 127 |
| 9 | — | 41.9 / 127 | 42.0 / 127 | 41.8 / 121 |
| 10 | — | 46.1 / 132 | 46.2 / 136 | 46.3 / 132 |
| 11 | — | — | 50.5 / 135 | 50.3 / 135 |
| 12 | — | — | 53.4 / 178 | 53.4 / 142 |
| 13 | — | — | — | 57.7 / 155 |
| 14 | — | — | — | 60.7 / 226 |

### Per-length pattern shares (the natural rates the uniform draw reproduces)

| length | k8add reductio / derived-`ORE` | k10 reductio / derived-`ORE` | k12 reductio / derived-`ORE` | k14 reductio / derived-`ORE` |
|---|---|---|---|---|
| 2 | 0.00 % / 0.00 % | 0.00 % / 0.00 % | 0.00 % / 0.00 % | 0.00 % / 0.00 % |
| 3 | 0.00 % / 0.00 % | 0.00 % / 0.00 % | 0.00 % / 0.00 % | 0.00 % / 0.00 % |
| 4 | 0.00 % / 0.00 % | 0.00 % / 0.00 % | 0.00 % / 0.00 % | 0.00 % / 0.00 % |
| 5 | 17.34 % / 0.09 % | 16.75 % / 0.08 % | 17.31 % / 0.09 % | 17.07 % / 0.09 % |
| 6 | 16.68 % / 0.20 % | 16.82 % / 0.17 % | 16.77 % / 0.17 % | 16.03 % / 0.21 % |
| 7 | 8.11 % / 6.55 % | 8.08 % / 5.94 % | 8.47 % / 6.00 % | 8.55 % / 6.29 % |
| 8 | 7.22 % / 19.19 % | 7.04 % / 18.87 % | 7.29 % / 18.82 % | 7.32 % / 18.45 % |
| 9 | — | 13.21 % / 29.06 % | 13.28 % / 29.29 % | 13.82 % / 28.41 % |
| 10 | — | 13.30 % / 35.02 % | 12.82 % / 35.09 % | 13.35 % / 35.25 % |
| 11 | — | — | 21.01 % / 37.34 % | 20.87 % / 37.80 % |
| 12 | — | — | 21.60 % / 37.96 % | 21.56 % / 38.41 % |
| 13 | — | — | — | 23.73 % / 45.22 % |
| 14 | — | — | — | 21.09 % / 49.56 % |
