# numbers.md — every number in writeup.md and where it comes from

## Data / generator
| number | value | source |
|---|---|---|
| cap-6 raw proofs generated / verifier rejects | 160,000 / 0 | `gen.py` stdout (log.md 03:30); `VERIFIER_REJECT` counter absent from stats |
| long raw proofs (strict) / rejects | 7,000 / 0 | same, `data/raw_long.jsonl` run |
| train / heldout / rl_targets / transfer sizes | 154,990 / 5,000 / 3,000 / 1,638 | `data/splits_stats.json` |
| per-length counts | train ~31k each 2–6; heldout 1,000 each; targets 300 each 7–16; transfer 125–200 each | `data/splits_stats.json` |
| renaming-only duplicates inside generator run | 78,931 (≈33% of distinct strings) | `gen.py` stats `dup_renaming_only` (log.md 03:30) |
| validation-class hits removed | 10 (cap-6), 6 (long) | `data/splits_stats.json` |
| trivial-pattern audit | 1,382/160k (0.9%) | `data/splits_stats.json` `cap6_trivial_pattern` |
| contradictory premise pairs | 9,803/160k cap-6 (6.1%); 1,896/7,000 long removed | `data/splits_stats.json` |
| parameters | 3,210,240 | `train.py` stdout (`artifacts/train_stage1_abs.log`) |
| Stage-1 training wall-clock | 722 s (rel), ~15 min (abs), sharing the GPU | `artifacts/train_stage1_*.log` |

## Stage 1 (greedy, held-out n=5000)
| number | value | source |
|---|---|---|
| rel by length 2..6 | 99.8 / 99.1 / 97.1 / 92.9 / 88.6 %, all 95.5% [94.9,96.0] | `artifacts/stage1_rel_heldout_greedy.json` |
| abs by length 2..6 | 99.8 / 98.6 / 96.2 / 92.0 / 87.3 %, all 94.8% [94.1,95.4] | `artifacts/stage1_abs_heldout_greedy.json` |
| abs failure reasons | ANDI 71, IMPE 45, ORI2 25, NEGE 24, IMPI 17, wrong conclusion 15 | same file, `reasons` |
| abs failure rate by rule / n_prem | ANDE2 24%, ORE 20%, ANDE1 16%; 3 premises 16% | computed from `artifacts/stage1_abs_heldout_greedy.jsonl` + `data/heldout.jsonl` (log.md) |

## Frozen Stage-1 beyond the cap (transfer v2, n=1638)
| number | value | source |
|---|---|---|
| greedy rel / abs | 26.4% [24.3,28.6] / 32.2% [30.0,34.5] | `artifacts/stage1_{rel,abs}_transfer2_greedy.json` |
| pass@16 rel / abs | 40.5% [38.2,42.9] / 44.7% [42.3,47.1] | `artifacts/stage1_{rel,abs}_transfer2_k16.json` |
| distinct len-7 / len-8 proofs rel / abs (start-index normalised; raw abs count was 501/1) | 79/0 vs 108/1 | `artifacts/stage1_{rel,abs}_transfer2_k16_norm.json` |
| transfer v1 (n=1600) pass@16 rel / abs | 33.2% / 37.8% | `artifacts/stage1_{rel,abs}_transfer_k16.json` |
| validation-36 greedy rel / abs | 10/36 / 7/36; >6 bin 0/24 both | `artifacts/stage1_{rel,abs}_val36_greedy.txt` |

## Stage 2, seed 0 (`artifacts/ei_abs_s0/round_<r>.json`, `artifacts/frozen_abs_s0/round_<r>.json`; tables in `artifacts/tables_s0.md`)
| number | value | source |
|---|---|---|
| transfer cumulative solved, round 8 (256 attempts) EI / frozen | 82.8% [80.9,84.6] / 55.3% [52.9,57.7] (n=1638) | round_8.json `transfer_cum` |
| transfer per-round pass@32, round 8 EI / frozen | 77.3% / 48.6% | round_8.json `transfer_round` |
| transfer greedy, round 8 EI / frozen | 64.2% [61.9,66.5] / 32.2% [30.0,34.5] | round_8.json `transfer_greedy` |
| RL targets cumulative, round 8 EI / frozen | 81.4% / 54.0% (n=3000) | round_8.json `targets_cum` |
| held-out greedy round 8 EI / frozen; EI minimum (round 4) | 94.9% / 94.8%; 93.1% | round_r.json `heldout_greedy` |
| robust frontier transfer written/pruned EI / frozen (start-index normalised) | 9/9 / 8/8 | `artifacts/ei_abs_s0_norm/round_8.json`, `artifacts/frozen_abs_s0_norm/round_8.json` `transfer_cum.frontier_*` |
| robust frontier targets written/pruned EI / frozen (normalised) | 9/9 at r8 (4 ten-line proofs), 10/10 from r15 / 8/8 | `artifacts/ei_abs_s0_norm/round_8.json`, `artifacts/ei_abs_s0_cont_norm/round_{15,16}.json` `targets_cum.frontier_*` |
| distinct transfer proofs written ≥8 / ≥9, EI / frozen (normalised; raw 2028 / 195 vs 54 / 0) | 193 / 20 vs 13 / 0 | `artifacts/*_norm/round_8.json` `transfer_cum.ge`; `artifacts/normalized_summary.md` |
| per-round table (rounds 1-8) | see writeup table | `artifacts/tables_s0.md` |
| padding: written>pruned fraction, mean excess (round 1 transfer, normalised; raw per-sample 41.7%, 1.07) | 51%, 0.58 lines | `artifacts/ei_abs_s0_norm/round_1.json` `transfer_cum.pad_frac/pad_gap` |
| transfer breakdown by depth / premises / ORE (EI r5 vs frozen r4) | see writeup table | `analyze_transfer.py` output, log.md 04:47 |
| greedy failure reasons round 8 EI / frozen | listed in writeup | round_8.json `transfer_greedy.reasons` |
| validation-36 per round greedy / pass@32 | r1 8/10, r2 9/11, r3 9/10, r4 7/11, r5 8/10, r6 10/11, r7 10/11, r8 9/11 | `artifacts/ei_abs_s0_r<r>_val36_greedy.txt`, `_val36_k32.json` |
| contraposition proof | 7 lines, round 7 greedy | `artifacts/ei_abs_s0_r7_val36_greedy.jsonl` |
| abs-fixed ablation held-out / transfer greedy / pass@16 / proofs ≥7 | 95.4% / 27.2% / 38.5% [36.2,40.9] / 0 of 26,208 samples | `artifacts/stage1_absfixed_{heldout,transfer2}_greedy.json`, `_transfer2_k16.json` |

## Stage 2, all arms (final rounds) — `artifacts/<arm>/round_<r>.json`; per-round tables `artifacts/tables_all.md`; merged 16-round dirs `artifacts/{ei,frozen}_abs_s0_all/`
| number | value | source |
|---|---|---|
| EI seed 1 r8: transfer cum / round / greedy / held-out | 82.6% [80.7,84.4] / 77.6% / 64.6% [62.2,66.9] / 94.9% | `artifacts/ei_abs_s1/round_8.json` |
| frozen seed 1 r8 | 55.5% [53.1,57.9] / 48.0% / 32.2% / 94.7% | `artifacts/frozen_abs_s1/round_8.json` |
| EI-long r8 | 82.1% [80.1,83.8] / 75.3% / 62.2% [59.8,64.5] / 95.1%; written ≥8 208, ≥9 21 (normalised; raw 2338 / 120) | `artifacts/ei_abs_long_s0_norm/round_8.json` |
| EI s0 r16 (512 attempts) | 86.1% [84.4,87.7] / 79.4% / 66.8% [64.5,69.0] / 95.3%; written ≥8 271, ≥9 29 (26 theorems), ≥10 0; targets ≥10: 13 (9 theorems), ≥11: 0 (normalised; raw 3628 / 397 / 0; 151) | `artifacts/ei_abs_s0_cont_norm/round_16.json` |
| frozen s0 r16 | 57.3% [54.9,59.7] / 48.4% / 32.2% / 94.7%; written ≥8 17, ≥9 0 (normalised; raw 92 / 0) | `artifacts/frozen_abs_s0_cont_norm/round_16.json` |
| seed-1 written ≥8 / ≥9 EI vs frozen (normalised; raw 2204 / 176 vs 54 / 0) | 205 / 22 vs 14 / 0 | `artifacts/ei_abs_s1_norm/round_8.json`, `artifacts/frozen_abs_s1_norm/round_8.json` |
| round time | 610–670 s with 2–3 jobs on the A40; 930–980 s with 5 jobs | `=== round` lines in `artifacts/*.log` |

## Test set (run once, 07:38 UTC) — `artifacts/test_scores.txt`, `artifacts/TEST_RUN_DONE`
| number | value | source |
|---|---|---|
| Stage 1 short / long | 73.0% (195/267; CI 67.4–78.0) / 9.8% (52/532; CI 7.5–12.6) | `artifacts/test_scores.txt` |
| final (EI s0 r16) short / long | 73.0% (195/267; CI 67.4–78.0) / 14.5% (77/532; CI 11.7–17.7) | `artifacts/test_scores.txt` |
| validation-36 final greedy / pass@32 | 9/36 / 11/36 | `artifacts/ei_abs_s0_cont_r16_val36_greedy.txt`, `_k32.json` |
| padding by round, cumulative distinct transfer proofs (padded fraction / mean written−pruned), normalised | r1 0.51/0.58; r8 0.61/0.85; r16 0.64/0.96; frozen r16 0.57/0.72 (superseded per-sample values: r1 0.42/0.45, r8 0.56/0.69, r16 0.61/0.84; frozen 0.47/0.53) | `artifacts/*_norm/round_<r>.json` `transfer_cum.pad_frac/pad_gap` |
| transfer breakdown by generating length / depth / premises (r8, r16) | table | `artifacts/transfer_breakdown.md` |
| pruned ≥9-line transfer proofs, final (normalised; raw 272 / 397) | 17 (written 29) | `artifacts/ei_abs_s0_cont_norm/round_16.json` `transfer_cum.ge_pruned` |
| validation >6 greedy attempt lengths, final | 2–7, median 5, 21/24 ≤6 | `artifacts/ei_abs_s0_cont_r16_val36_greedy.jsonl` + verifier |
| EI-long validation-36 r8 greedy / pass@32 | 8/36 / 9/36 | `artifacts/ei_abs_long_s0_r8_val36_*` |
| pass@128 one shot (seed 7), final / Stage 1 | 82.6% [80.7,84.4] / 52.9% [50.4,55.3]; written 8/9/10 (normalised): 188/33/2 vs 11/0/0 (raw 2215/335/2 vs 32/0/0); frontier 9 / 8 | `artifacts/final_transfer_k128_norm.json`, `artifacts/stage1_transfer_k128_norm.json` |

## Post-run review corrections (2026-09-15) — `normalize.py`, `audit_test_overlap.py`
| number | value | source |
|---|---|---|
| share of "distinct" proofs that were start-index variants of another proof | ~96% (e.g. EI s0 r16 transfer: 75,085 raw → 3,330 normalised; frozen: 47,393 → 1,724) | `artifacts/normalized_summary.md` |
| theorems with a written 8 / 9 / 10-line proof, EI s0 r16 transfer / targets | 180 / 26 / 0 ; 246 / 46 / 9 | `artifacts/ei_abs_s0_cont_norm/round_16.json` `*_cum.theorems_at_written` |
| theorems with a written 8 / 9-line proof, frozen s0 r16 transfer / targets | 14 / 0 ; 31 / 0 | `artifacts/frozen_abs_s0_cont_norm/round_16.json` |
| Stage-1 pass@16 length-7 / 8 proofs, abs / rel / abs-fixed (normalised; raw abs 501 / 1) | 108 / 1 ; 79 / 0 ; 0 / 0 | `artifacts/stage1_{abs,rel,absfixed}_transfer2_k16_norm.json` |
| test-short prompts whose renaming class is in Stage-1 train / exact string | 119 of 267 (45%) / 9 | `artifacts/test_overlap.json` |
| test-long prompts whose renaming class is in Stage-1 train / exact string | 6 of 532 (1%) / 1 | `artifacts/test_overlap.json` |
| validation-36 overlap with any pool | 0 | `artifacts/test_overlap.json` |

## Novelty campaign (branch dan_novelty, 2026-09-15/18) — Phase 1
| number | value | source |
|---|---|---|
| normalised-distinct proofs scored: final transfer / final targets / final val36 / EI-any-round val36 / frozen transfer / frozen targets | 3,330 (1,411 thms) / 4,506 (2,570) / 14 (11) / 26 (13) / 1,724 / 3,149 | `artifacts/novelty_phase1_proofs.jsonl` (`novelty.py`) |
| final transfer proofs with base p(T=0.8) < 1e-5, by written length 7 / 8 / 9 | 328/784, 212/242, 29/29 | `artifacts/phase1_tables.md` (reachability tables) |
| final transfer theorems (shortest found proof 8 / 9 lines) below the 1e-5 line by their found proofs | 83/87, 14/14 | same, per-theorem table |
| frozen transfer proofs (found in 512 attempts) with base p >= 1/512 | 1,463/1,724; < 1e-5: 7 | same, calibration table |
| contraposition: predicted base p (T=0.8) / measured at k=1e5 | 1.8e-4 (log -8.64) / 14 hits, first at sample 5,681 | `novelty_phase1_theorems.jsonl`, `artifacts/cov_base_val36_k1e5.s0.jsonl` |
| export: predicted base p / measured at k=1e5 | 6e-8 (log -16.6) / 0 hits | same |
| validation-36 base model k=1e5: solved / >6 bin solved | 14/36 / 1/24 (contraposition; explosion 57 hits, 5-line proofs) | `artifacts/cov_base_val36_k1e5.s0.jsonl` |
| minlen (bound 8): val36 labelled / agree with reference bound | 20/36 / 20/20 | `artifacts/minlen_val36.jsonl` |
| minlen: transfer labelled / with <=6-line proof; RL targets labelled / <=6 | 1,573/1,638 / 1,149 (70%); 2,860/3,000 / 2,071 (69%) | `artifacts/minlen_transfer.jsonl`, `artifacts/minlen_rl_targets.jsonl` |
| pattern rates in take-home cap-6 pool (n=160k): derived_ore / reductio / depth3 | 91 (0.057%) / 10,887 (6.8%) / 5,870 (3.7%); len-5/6 only | `patterns.py --stats data/raw_cap6.jsonl` (log.md 19:40) |
| pattern rates in take-home long pool (n=7,000) | 35.8% / 14.1% / 39.4% | `patterns.py --stats data/raw_long.jsonl` |

## Novelty campaign — Phase 2 pools (2026-09-15 20:05 UTC)
| number | value | source |
|---|---|---|
| cap-6 raw pool: distinct classes (len 2/3/4/5/6) | 820,125 (75,526 / 91,482 / 113,123 / 161,186 / 378,808); class duplicates dropped 848,626 | p1 `artifacts/…` merge stdout (log.md 20:05) |
| cap-6 pool pattern classes: derived_ore / reductio / depth3 | 3,531 / 158,590 / 193,577 | same |
| natural per-length pattern rates used as the held-fixed baseline (from the take-home's unfiltered pool) | reductio 17.34% (len 5) / 16.68% (len 6); depth3 18.34% (len 6); derived_ore 0.088% / 0.197% | `make_coverage_sets.py assemble` NATURAL |
| long strict pool (7-12 lines): classes / with a <=6-line proof (minlen) / without | 89,533 / 69,756 / 19,777 | `data/p2/pool_long_minlen.jsonl` |
| P1 f_max | 0.02 (3,100 proofs of 3,531 available) | assemble_report.json |
| achieved frequencies per set (derived_ore / reductio / depth3) | | |
| derived_ore_f0 | 0.00000 / 0.06805 / 0.03669 | `data/p2/assemble_report.json` |
| derived_ore_f0.0001 | 0.00010 / 0.06805 / 0.03669 | `data/p2/assemble_report.json` |
| derived_ore_f0.001 | 0.00100 / 0.06805 / 0.03669 | `data/p2/assemble_report.json` |
| derived_ore_f0.01 | 0.01000 / 0.06805 / 0.03669 | `data/p2/assemble_report.json` |
| derived_ore_f0.02 | 0.02000 / 0.06805 / 0.03669 | `data/p2/assemble_report.json` |
| targets_derived_ore: n / gen-length range / min_lines_ub 7,8,None / other patterns | 1000 / 10-9 / 654,219,127 / {'derived_ore': 1000, 'reductio': 43, 'depth3': 640} | `data/p2/targets_summary.json` |
| transfer_derived_ore: n / gen-length range / min_lines_ub 7,8,None / other patterns | 500 / 11-12 / 403,65,32 / {'derived_ore': 500, 'reductio': 31, 'depth3': 357} | `data/p2/targets_summary.json` |
| targets_reductio: n / gen-length range / min_lines_ub 7,8,None / other patterns | 972 / 10-9 / 452,286,234 / {'derived_ore': 9, 'reductio': 972, 'depth3': 402} | `data/p2/targets_summary.json` |
| transfer_reductio: n / gen-length range / min_lines_ub 7,8,None / other patterns | 332 / 10-9 / 174,86,72 / {'derived_ore': 1, 'reductio': 332, 'depth3': 137} | `data/p2/targets_summary.json` |
| targets_depth3: n / gen-length range / min_lines_ub 7,8,None / other patterns | 1000 / 10-9 / 575,240,185 / {'derived_ore': 0, 'reductio': 0, 'depth3': 1000} | `data/p2/targets_summary.json` |
| transfer_depth3: n / gen-length range / min_lines_ub 7,8,None / other patterns | 500 / 10-9 / 296,110,94 / {'derived_ore': 13, 'reductio': 0, 'depth3': 500} | `data/p2/targets_summary.json` |
| targets_none: n / gen-length range / min_lines_ub 7,8,None / other patterns | 1000 / 10-9 / 608,252,140 / {'derived_ore': 0, 'reductio': 0, 'depth3': 0} | `data/p2/targets_summary.json` |
| transfer_none: n / gen-length range / min_lines_ub 7,8,None / other patterns | 500 / 10-9 / 306,124,70 / {'derived_ore': 0, 'reductio': 0, 'depth3': 0} | `data/p2/targets_summary.json` |
