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

## Novelty campaign — Phase 2 row 1 (arms as they finish; all normalised-distinct; `phase2_metrics.py`, `artifacts/p2/metrics_*.json`)
| arm (8 rounds, k=32) | targets solved / n | acquisition (thms with a pattern proof) / pattern proofs / first round | transfer solved / acq | held-out greedy | source |
|---|---|---|---|---|---|
| ei_reductio_f0_s0 | 609/972 | 0 / 0 / – | 222/332 / 0 | 0.886 | `artifacts/p2/ei_reductio_f0_s0/` |
| ei_reductio_f0_s1 | 170/972 | 0 / 0 / – | 68/332 / 0 | 0.885 | `artifacts/p2/ei_reductio_f0_s1/` |
| ei_reductio_f0.1_s0 | 193/972 | 13 (0.013) / 13 / 1 | 72/332 / 0 | 0.970 | `artifacts/p2/ei_reductio_f0.1_s0/` |
| ei_depth3_f0.1_s0 | 594/1000 | 355 (0.355) / 424 / 2 | 310/500 / 0.382 | 0.964 | `artifacts/p2/ei_depth3_f0.1_s0/` |
| ei_depth3_f0.1_s1 | 607/1000 | 316 (0.316) / 388 / 1 | 320/500 / 0.348 | 0.962 | `artifacts/p2/ei_depth3_f0.1_s1/` |
| frozen_reductio_f0_s0 (control, 256 samples/target) | 96/972 | 0 / 0 / – | 39/332 / 0 | 0.886 | `artifacts/p2/frozen_reductio_f0_s0/` |
| frozen_reductio_f0.1_s0 (control) | 74/972 | 11 (0.011) / 11 / 1 | 24/332 / 0 | 0.968 | `artifacts/p2/frozen_reductio_f0.1_s0/` |
| ei_derived_ore_f0_s0 | 364/1000 | 9 (0.009) / 9 / 3 | 328/500 / 0.002 | 0.973 | `artifacts/p2/ei_derived_ore_f0_s0/` |
| ei_derived_ore_f0_s1 | 330/1000 | 2 (0.002) / 2 / 7 | 311/500 / 0.004 | 0.970 | `artifacts/p2/ei_derived_ore_f0_s1/` |
| ei_derived_ore_f0.02_s0 | 572/1000 | 242 (0.242) / 294 / 1 | 329/500 / 0.022 | 0.965 | `artifacts/p2/ei_derived_ore_f0.02_s0/` |
| frozen_depth3_f0.1_s0 (control) | 127/1000 | 12 (0.012) / 17 / 1 | 66/500 / 0.012 | 0.966 | `artifacts/p2/frozen_depth3_f0.1_s0/` |
| ei_reductio_f0.001_s0 (row 2) | 212/972 | 13 (0.013) / 13 / 4 | 82/332 / 0 | 0.953 | `artifacts/p2/ei_reductio_f0.001_s0/` |
| ei_reductio_f0.001_s1 (row 2) | 374/972 | 0 / 0 / – | 156/332 / 0 | 0.948 | `artifacts/p2/ei_reductio_f0.001_s1/` |
| ei_derived_ore_f0.02_s1 | 660/1000 | 293 (0.293) / 305 / 1 | 359/500 / 0.042 | 0.974 | `artifacts/p2/ei_derived_ore_f0.02_s1/` |
| frozen_derived_ore_f0_s0 (control) | 180/1000 | 1 (0.001) / 1 / 1 | 193/500 / 0 | 0.971 | `artifacts/p2/frozen_derived_ore_f0_s0/` |
| frozen_derived_ore_f0.02_s0 (control) | 136/1000 | 10 (0.010) / 11 / 1 | 134/500 / 0.002 | 0.967 | `artifacts/p2/frozen_derived_ore_f0.02_s0/` |
| derived_ore f=0 arms: strict derived-ORE (rule-derived disjunction, distinct disjuncts) theorems | 0 (all 11 EI proofs and the 1 frozen proof are the ( X v X ) one-line-box form) | `phase2_metrics.py` acq_strict |
| ei_depth3_f0_s0 | 628/1000 | 341 (0.341) / 400 / 3 | 323/500 / 0.366 | 0.940 | `artifacts/p2/ei_depth3_f0_s0/` |
| ei_depth3_f0_s1 | 587/1000 | 271 (0.271) / 327 / 5 | 296/500 / 0.280 | 0.911 | `artifacts/p2/ei_depth3_f0_s1/` |
| frozen_depth3_f0_s0 (control) | 55/1000 | 0 / 0 / – | 30/500 / 0 | 0.874 | `artifacts/p2/frozen_depth3_f0_s0/` |
| ei_depth3_f0.001_s0 (row 2) | 631/1000 | 364 (0.364) / 443 / 1 | 324/500 / 0.384 | 0.964 | `artifacts/p2/ei_depth3_f0.001_s0/` |
| depth3 f=0 s0: depth-3 proofs found by EI / with base p(T=0.8, own Stage-1 model) < 1/256 / < 1e-5 / most probable | 610 / 610 / 610 / log p = −21.8 (round 4) | `artifacts/p2/novelty_depth3_f0_s0_proofs.jsonl` |
| depth3 f=0 s1: same | 491 / 491 / 485 / log p = −7.1 (round 6) | `artifacts/p2/novelty_depth3_f0_s1_proofs.jsonl` |
| depth3 f=0: max-surprisal token of the depth-3 proofs is the third `\|` | s0 608/610, s1 475/491 | same |
| ei_derived_ore_f0.001_s0 (row 2) | 583/1000 | 248 (0.248) / 281 / 1 | 327/500 / 0.028 | 0.968 | `artifacts/p2/ei_derived_ore_f0.001_s0/` |
| ei_depth3_f0.001_s1 (row 2) | 660/1000 | 339 (0.339) / 429 / 2 | 333/500 / 0.366 | 0.952 | `artifacts/p2/ei_depth3_f0.001_s1/` |
| ei_derived_ore_f0.001_s1 (row 2) | 583/1000 | 245 (0.245) / 268 / 2 | 330/500 / 0.022 | 0.972 | `artifacts/p2/ei_derived_ore_f0.001_s1/` |
| ei_reductio_f0.01_s0 (row 3) | 494/972 | 11 (0.011) / 11 / 4 | 190/332 / 0 | 0.966 | `artifacts/p2/ei_reductio_f0.01_s0/` |
| ei_reductio_f0.0001_s0 (row 3) | 203/972 | 3 (0.003) / 3 / – | – | – | `artifacts/p2/ei_reductio_f0.0001_s0/`, `artifacts/p2/metrics_reductio.json` |
| main figure (all arms finished so far) | figures/phase2_acquisition.png | `phase2_figure.py` |
| base derived_ore_f0_s0 pass@1e4 (284 P1 targets): solved / with derived-ORE proof / strict | 3 / 2 / 0 | `artifacts/p2/cov_derived_ore_f0_s0_targets.s0.jsonl` |
| Phase 3 frozen_textbook (256 samples/target): solved by minlen length 2/3/4/5/6/7/8/unlabelled | 47/47, 2/2, 48/48, 5/9, 55/82, 4/118, 0/32, 0/285 (161/623) | `artifacts/p3/frozen_textbook/round_8.json` |
| base reductio_f0_s0 pass@1e4 (300 P2 targets): solved / within 512 / with a reductio proof | 82 / 51 / 0 | `artifacts/p2/cov_reductio_f0_s0_targets.s0.jsonl` |
| base derived_ore_f0_s0 pass@1e4 (300 P1 targets, final): solved / with derived-ORE proof / strict | 3 / 2 / 0 | `artifacts/p2/cov_derived_ore_f0_s0_targets.s0.jsonl` |
| ei_depth3_f0.0001_s0 (row 3; resumed from r5 after an OOM) | 605/1000 | 354 (0.354) / 433 / 2 | 314/500 / 0.368 | 0.959 | `artifacts/p2/ei_depth3_f0.0001_s0/` |
| targets provably needing the pattern (bounded, <=8-line restricted search): depth3 / derived_ore / reductio | 142 of 815 labelled (max box depth 2) / 372 of 873 (ORE over premises only) / 56 of 972 (classical-only) | `data/p2/targets_depth3_maxdepth2.jsonl`, `data/p2/targets_derived_ore_noderived.jsonl`, `data/p2/targets_reductio_intuit.jsonl` |
| ei_depth3_f0.01_s0 (row 3) | 663/1000 | 363 (0.363) / 421 / 2 | 343/500 / 0.402 | 0.969 | `artifacts/p2/ei_depth3_f0.01_s0/` |
| ei_derived_ore_f0.0001_s0 (row 3) | 555/1000 | 222 (0.222) / 275 / 2 | 323/500 / 0.022 | 0.967 | `artifacts/p2/ei_derived_ore_f0.0001_s0/` |
| ei_derived_ore_f0.01_s0 (row 3) | 610/1000 | 272 (0.272) / 371 / 1 | 340/500 / 0.040 | 0.970 | `artifacts/p2/ei_derived_ore_f0.01_s0/` |
| Phase 3 EI arms, targets solved r8: ei_textbook / ei_textbook_precursor / frozen | see phase3.md | `artifacts/p3/*/round_8.json` |

## Novelty campaign — Phase 3 (textbook-shaped curriculum; `artifacts/p3/`)
| number | value | source |
|---|---|---|
| textbook pool: theorems / schemata / with a <=6-line proof (minlen) / min_lines_ub 7 / 8 / none <=8 | 623 / 26 / 188 / 118 / 32 / 285 | `data/p3/textbook_targets.jsonl` |
| precursor set (generator proofs matching a sub-step template of a schema): records / by length 2-6 / schemata covered | 9,455 / 1,326, 1,666, 2,100, 2,757, 1,606 / 23 | `data/p3/precursors.jsonl` (`precursors.py`) |
| targets solved per round, frozen / ei_textbook / ei_textbook_precursor | 153..161 / 153,180,193,200,202,203,207,213 / 153,186,198,207,216,222,222,222 | `artifacts/p3/*/round_r.json` |
| schemata moved by EI (r8, /24 each): contraposition / consequentia_mirabilis / export / hypothetical_syllogism | frozen 3, 9, 0, 22; ei 24, 24, 12, 24; ei+precursor 24, 24, 19, 24 | `artifacts/p3/*/found_8.jsonl` by schema |
| schemata at 0-2/24 for every arm | De Morgan x4, distribution x4, constructive_dilemma, disjunctive_syllogism, negated_conditional(_conv), peirce, peirce_sequent, contraposition_conv, import (2-4), excluded_middle (1) | same |
| validation-36 per round (greedy / pass@32, >6 bin): ei_textbook | >6 greedy 1/24 from r2 (contraposition), pass@32 1/24 every round; <=6 pass@32 10-11/12 | `artifacts/p3/ei_textbook_r*_val36_*` |
| validation-36 per round: ei_textbook_precursor | >6 pass@32 2/24 from r4 (contraposition, export); greedy >6 2/24 at r6; <=6 pass@32 10-11/12 | `artifacts/p3/ei_textbook_precursor_r*_val36_*` |
| validation theorems newly solved vs Stage-1 pass@32 (any round): ei_textbook / ei+precursor | consequentia_mirabilis, contraposition, explosion / consequentia_mirabilis, contraposition, export | same |
| transfer greedy r8 / held-out greedy r8: frozen, ei, ei+precursor | 0.322 / 0.947, 0.324 / 0.954, 0.338 / 0.952 | round_8.json |
| base depth3_f0_s0 pass@1e4 (first 180 of 300 P3 targets, running): solved / with a depth-3 proof | 1 / 0 | `artifacts/p2/cov_depth3_f0_s0_targets.s0.jsonl` |
| base depth3_f0_s0 pass@1e4 (300 P3 targets, final): solved / within 512 / with a depth-3 proof | 3 / 1 / 0 | `artifacts/p2/cov_depth3_f0_s0_targets.s0.jsonl` |

## Follow-up run (2026-09-16/17) — block A: depth-3 replication sets (`data/p2/assemble_report_{a1,a2,a3,b1,b2}.json`, `artifacts/fu/indep_check.log`)
- Pool: `data/p2/pool_cap6_recon.jsonl` = union of the 12 local raw shards + the 15 campaign-1 training sets + held-out, dedup by class, val-36 dropped: 723,534 classes (len 2/3/4/5/6: 75,365 / 91,375 / 112,399 / 149,025 / 295,370; depth-3 132,454; reductio 125,296; derived-ORE 3,744). Subset of the campaign-1 pool (820,125).
- New sets (155,000 each, 31,000 per length, campaign-1 held-out reused and excluded, depth-3 target/transfer classes excluded; assembler seeds 1 / 2 / 3 / 11 / 12): depth3_f0_a1, _a2, _a3: depth-3 **0 / 0 / 0** (pruned and written form; independent written-form counter 0 / 0 / 0), reductio 10,547 (0.0681), derived-ORE 88 (0.00057), strict derived-ORE 2 / 1 / 2. depth3_f0.1_b1, _b2: depth-3 15,500 (0.1000; independent count 15,500 / 15,500), reductio 10,547, derived-ORE 88. Class overlap with the campaign-1 f = 0 set: 47,352 / 47,580 / 47,269 (a1–a3), 42,968 / 42,595 (b1–b2) of 155,000.

## Follow-up — block B pool (`reductio_pool.py`, `data/p2/targets_reductio2.jsonl`, `transfer_reductio2.jsonl`, `reductio2_cands_minlen.jsonl`, `artifacts/fu_blockB_pool.log`, `fu_blockB_pool2.log`)
- Generator-native attempt: 20M tries (long mode, 7–12 lines, filter reductio ∧ no `( ~ ( ~`): 23,523 raw → 19,099 classes (len 7/8/9/10/11/12: 8,072 / 996 / 1,477 / 1,284 / 2,630 / 4,640); classical-only (`intuit.py`): **7** (0.04%); minlen (bound 8): 6 labelled {6: 1, 7: 2, 8: 3}, 1 unlabelled → 6 usable (min_lines_ub ≥ 7 or None).
- Schema pool: 21 classical-only schemata without double negation × 45 instances = 945 candidates (all truth-table valid and intuitionistically unprovable, asserted per instance; class-disjoint from the reconstructed cap-6 pool, held-out, old reductio pools, validation-36); minlen bound 8 / 10 s: labelled 365 {6: 45, 7: 90, 8: 230}, 580 unlabelled → 900 with min_lines_ub ≥ 7 or None.
- **targets_reductio2: 606** (600 schema = 30 per schema + 6 generator-native), min_lines_ub 7 / 8 / None = 62 / 158 / 386; **transfer_reductio2: 300** (15 per schema), 30 / 75 / 195. Hand check of ten printed targets (log.md 02:05): every one needs the negated goal assumed (excluded middle, Peirce, `~(X>Y) |- X`, case split on an atom via `A>B, ~A>B |- B`, …).

## Follow-up — block A arms as they finish (`followup_analysis.py` → `artifacts/fu/blockA_summary.json`; per-arm dirs `artifacts/p2/ei_depth3_*`; acquisition = target theorems solved with a written proof whose pruned form has box depth ≥ 3, normalised-distinct)
- depth3_f0_a1 s0: 645/1000 solved, **acq 0.335** (335 theorems / 409 depth-3 proofs / first round 2); transfer 0.372; held-out greedy 0.907.
- depth3_f0_a1 s1: 698/1000, **acq 0.364** (364 / 426 / r1); transfer 0.366; held-out greedy 0.930.

## Follow-up — block B arms (`phase2_metrics.py --pattern reductio`, `artifacts/fu/metrics_reductio2*.json`; targets_reductio2 n = 606, transfer 300; strict = `patterns.reductio`, loose = `patterns.derived_dn`, both on the model's normalised proof)
- reductio_f0 s0 (_t2): solved 58/606; **strict 58 (0.096), loose 58, any-DN 58**; 60 distinct proofs; first strict proof round 2 (1 theorem), then 11 / 24 / 36 / 55 / 58 / 58 at rounds 3–8; transfer 30/300 solved, strict 30 (0.100). Solved by schema: nand_neg 29/30, negimp_to_pos 27/30, generator-native 2/6, every other schema 0. Held-out greedy 0.893, transfer greedy 0.097.
- reductio_f0 s1 (_t2): solved **0/606** (8 rounds × 32 = 256 attempts per target), transfer 0/300; held-out greedy 0.871.
- depth3_f0_a2 s0: 589/1000 solved, **acq 0.350** (350 / 430 depth-3 proofs / first round 2); transfer acq 0.368; held-out greedy 0.945.
- depth3_f0_a2 s1: 652/1000 solved, **acq 0.341** (341 / 426 depth-3 proofs / first round 4); transfer acq 0.358; held-out greedy 0.903.
- depth3_f0_a3 s0: 605/1000 solved, **acq 0.361** (361 / 435 depth-3 proofs / first round 2); transfer acq 0.386; held-out greedy 0.945.
- depth3_f0.1_b2 s0: 604/1000 solved, **acq 0.352** (352 / 410 depth-3 proofs / first round 3); transfer acq 0.388; held-out greedy 0.965.
- depth3_f0.1_b2 s1: 596/1000 solved, **acq 0.347** (347 / 428 depth-3 proofs / first round 2); transfer acq 0.380; held-out greedy 0.971.
- depth3_f0_a3 s1: 583/1000 solved, **acq 0.352** (352 / 425 / first round 1); transfer acq 0.378; held-out greedy 0.919.
- **f = 0, all 8 arms** (4 sets × 2 seeds): 0.341, 0.271 (campaign-1 set a0), 0.335, 0.364 (a1), 0.350, 0.341 (a2), 0.361, 0.352 (a3): mean 0.339, SD 0.029, min 0.271, max 0.364.
- reductio_f0.1 s0 (_t2): solved 95/606, **strict 95 (0.157), loose 95, any-DN 95**, first round 1 (15 theorems), per round 15 / 46 / 61 / 64 / 71 / 77 / 81 / 95; transfer 40/300 solved, strict 40 (0.133); held-out greedy 0.970. Solved by schema: negimp_to_pos 30/30, nand_neg 30/30, neg_both 22/30, chain_neg 11/30, generator-native 2/6; the 16 longer schemata 0.
- reductio_f0.1 s1 (_t2): solved 63/606, **strict 63 (0.104), loose 63**, first round 1 (17), per round 17 / 48 / 61 / 62 / 62 / 63 / 63 / 63; transfer 30/300 (strict 30); held-out greedy 0.973. By schema: negimp_to_pos 30/30, nand_neg 30/30, chain_neg 2, generator-native 1.
- Block B frozen controls (256 attempts per target): reductio_f0 s0 **3/606 solved, all 3 strict reductio** (nand_neg), transfer 1/300; f0 s1 0/606; f0 s2 0/606; f0.1 s0 25/606 (strict 25: nand_neg 20, negimp_to_pos 5), transfer 15/300; f0.1 s1 29/606 (strict 29: nand_neg 18, negimp_to_pos 11), transfer 10/300. (`artifacts/fu/blockB_summary.json`)
- Block B base log-probs of the strict reductio proofs under each arm's own Stage-1 model (T = 0.8, start-index marginalised; `novelty_reductio_*_t2_proofs.jsonl`): f0 s0: 60 proofs, max log p −5.6 (round 4), median −21.2, 60 / 52 / 44 below 1/256 / 10⁻⁴ / 10⁻⁵, 0 theorems above 1/256; f0.1 s0: 96 proofs, max −1.4, median −13.1, 25 theorems above 1/256; f0.1 s1: 63 proofs, max −0.35, median −6.4, 26 theorems above 1/256.

## Follow-up — block C (cap 8; `artifacts/p2/ei_derived_ore_strict_*_c8_*`, `artifacts/fu/metrics_c8_*.json`; targets_c8 n = 500, transfer 250; acquisition = solved with a proof containing `patterns.derived_ore_strict`)
- derived_ore_strict_f0_c8 s1: 200/500 solved, **strict acq 0.008** (4 theorems / 5 proofs / first round 2); transfer 118/250, strict 0.004; held-out (cap 8) greedy 0.936; transfer greedy 0.208.
- derived_ore_strict_f0_c8 s0: 197/500 solved, **strict acq 0.008** (4 / 5 / first round 3); transfer 120/250, strict 0.004; held-out greedy 0.926; transfer greedy 0.176.
- Block B base pass@10⁴ (`coverage.py`, stage1_reductio_f0_s0, T = 0.8, first 300 targets of targets_reductio2, 3,000,000 samples; every distinct verified proof stored with its hit count and pattern labels, `hits_by_pattern` asserted = n_ok): **5/300 targets solved** (2 within 512, 3 within 1,000), 92 verified samples of 3·10⁶, all 92 with the strict reductio shape (5 distinct proofs), all 5 targets instances of `~(~A & B), B |- A` (nand_neg): per-sample rates 3.8·10⁻³, 3.6·10⁻³, 1.4·10⁻³, 2·10⁻⁴, 2·10⁻⁴ (first hits at samples 348 / 524 / 309 / 2,905 / 7,344). 0 depth-3, 0 derived-ORE samples. `artifacts/p2/cov_reductio_f0_s0_t2_targets.s0.jsonl`.
- depth3_f0.1_b1 s1: 484/1000 solved, **acq 0.122** (122 / 141 / first round 2); depth-3 theorems per round 1 / 2 / 2 / 2 / 2 / 5 / 27 / 122 (late ignition; sibling b1 s0: 3 / 86 / 198 / 262 / 298 / 332 / 340 / 349); transfer acq 0.124; held-out greedy 0.979.
- **f = 0.1, all 6 arms**: 0.355, 0.316 (b0), 0.349, 0.122 (b1), 0.352, 0.347 (b2): mean 0.307, SD 0.092 (without the late-igniting b1 s1: mean 0.344, SD 0.016).
- Frozen controls (256 attempts/target), depth-3 theorems: a0 s0 0, a1 s0 5, a1 s1 5, a2 s0 4, a2 s1 0, a3 s0 1, a3 s1 10; b0 s0 12, b1 s0 5, b1 s1 2, b2 s0 0, b2 s1 10 (frozen solve counts 55 / 175 / 175 / 166 / 144 / 98 / 127; 127 / 137 / 173).
- derived_ore_strict_f0.001_c8 s0: 202/500 solved, **strict acq 0.022** (11 / 17 / first round 4; per round 2 / 2 / 4 / 4 / 5 / 7 / 8 / 11); transfer 124/250, strict 0.004; held-out greedy 0.929.
- derived_ore_strict_f0.01_c8 s0: 218/500 solved, **strict acq 0.022** (11 / 14 / first round 3; per round 2 / 4 / 6 / 7 / 8 / 9 / 9 / 11); transfer 126/250, strict 0.008; held-out greedy 0.933. Written-length histogram of the solved targets' proofs: 9: 397, 10: 77, 11: 4 (targets have no ≤ 8-line proof); 150–162 of the ~200 solved targets are solved with depth-3 proofs.
- Block C base log-probs (novelty.py, each arm's own cap-8 Stage-1 model, T = 0.8, `novelty_derived_ore_strict_*_c8_*_proofs.jsonl`): median base log p of ALL target proofs found by the arms −4.0 to −4.3 (the cap-8 targets are largely reachable by the cap-8 base); strict proofs: f0 s0 5 proofs, max −1.2 (round 6), median −5.5, 2 below 1/256, 0 below 10⁻⁵, 2 theorems above 1/256; f0 s1 5 proofs, max −2.9, median −4.7, 2 below 1/256, 0 below 10⁻⁵; f10⁻³ 17 proofs, max −0.6, median −8.5, 13 below 1/256, 5 below 10⁻⁵; f10⁻² 14 proofs, max −1.9, median −5.3, 6 below 1/256, 1 below 10⁻⁵. Max-surprisal line: the `AS` opening an ORE box, or the `IMPE`/`ANDE` deriving the disjunction.
- Block C frozen controls (cap 8, 256 attempts/target): f0 s0 159/500 solved, strict 3 theorems (0.006, 4 proofs), transfer 94/250 (strict 1); f0 s1 161/500, strict 2 (0.004, 4 proofs), transfer 97/250 (strict 1). EI f = 0 arms: 197 / 200 solved, strict 4 / 4.
- First round with a depth-3 proof, recomputed with the min-round fix (log.md 05:10): a0 s0 (f=0): 2; a0 s1 (f=0): 4; a1 s0 (f=0): 1; a1 s1 (f=0): 1; a2 s0 (f=0): 1; a2 s1 (f=0): 3; a3 s0 (f=0): 1; a3 s1 (f=0): 1; b0 s0 (f=0.1): 1; b0 s1 (f=0.1): 1; b1 s0 (f=0.1): 1; b1 s1 (f=0.1): 1; b2 s0 (f=0.1): 2; b2 s1 (f=0.1): 1.
- Frozen depth-3 proofs (distinct, normalised): a0 s0 0, a1 s0 5, a1 s1 5, a2 s0 4, a2 s1 0, a3 s0 1, a3 s1 11; b0 s0 17, b1 s0 5, b1 s1 2, b2 s0 0, b2 s1 10. Variance decomposition f = 0 (4 sets x 2 seeds): sd_set 0.012, sd_seed 0.027, set share 17%, F = 1.4; f = 0.1 (3 x 2): sd_set 0, sd_seed 0.094. f = 0 vs f = 0.1 difference of means +0.033, permutation p = 0.46; 6/8 f = 0 arms inside the f = 0.1 range, 5/6 f = 0.1 arms inside the f = 0 range. `artifacts/fu/blockA_summary.json`.
- Block C base pass@10⁴ (`coverage.py`, stage1_derived_ore_strict_f0_c8_s0, first 300 targets_c8, 3·10⁶ samples): **118/300 solved** (87 within 512), 213,129 verified samples (582 distinct proofs); strict derived-ORE proofs on **7 targets** (3,780 hits: targets 8 [3,675 hits, p ≈ 0.37, first at sample 5], 49 [49], 7 [36], 33 [16], 0 [2], 2 [1], 194 [1]); depth-3 proofs 138,198 hits. EI f = 0 s0 acquired 4 strict targets (7, 8, 33, 50) in 256 attempts per target. `artifacts/p2/cov_derived_ore_strict_f0_c8_s0_targets.s0.jsonl`.

## Ignition study (2026-09-16, HANDOFF_BRIEF Task 2; `ignition_analysis.py` → `artifacts/ign/summary.json`, `summary_table.md`, `summary_examples.md`; job files `pod/ign/`; pod logs `artifacts/ign/podlogs_p{1,2,3}/`)
- Stage-1: `train.py --mode abs --steps 6000 --bs 128 --cap 6`, depth-3 `a1` seeds 2–9 (`ckpts/p2/stage1_depth3_f0_a1_s{2..9}.pt`), reductio f = 0 seeds 3–10 (`stage1_reductio_f0_s{3..10}.pt`); held-out greedy at EI round 1: 0.863–0.886 (a1 s0–s9), from `artifacts/p2/ei_depth3_f0_a1_s*/round_1.json`.
- Pre-RL samples (`coverage.py --k 2000 --temperature 0.8 --limit 300 --batch 2000 --seed 0 --procs 4`; first 300 targets of `targets_depth3.jsonl` / `targets_reductio2.jsonl`; `artifacts/ign/cov_<model>.s0.jsonl`, 300 records each, per-proof hit counts and pattern labels; rate = Σ pattern hits / 600,000). Depth-3 a1 s0–s9: **2.5·10⁻⁴ (152 hits, 6 targets), 6.2·10⁻⁴ (370, 7), 0, 0, 1.7·10⁻⁶ (1, 1), 0, 5.0·10⁻⁶ (3, 1), 0, 0, 1.9·10⁻³ (1,112, 29)**; other f = 0 draws a0 s0/s1, a2 s0/s1, a3 s0/s1: see `summary.json` `depth3.coverage` (a2 s0: 301 hits, 8 targets). Reductio s0–s10: **3.1·10⁻⁵ (92 / 3·10⁶, 5 targets; the follow-up's pass@10⁴ file `cov_reductio_f0_s0_t2_targets.s0.jsonl` copied to `cov_reductio_f0_s0.s0.jsonl`), 0, 0, 2.0·10⁻⁵ (12, 3), 0, 0, 0, 2.3·10⁻⁴ (137, 11), 0, 8.3·10⁻⁶ (5, 1), 0**. Every reductio hit is on a `nand_neg` target.
- Frozen control at matched attempts (first pattern-proof sample index ≤ 256, on the 300 sampled targets): depth-3 a1 s0–s9 **4, 3, 0, 0, 0, 0, 1, 0, 0, 16**; reductio s0–s10 **0, 0, 0, 2, 0, 0, 0, 8, 0, 1, 0**. EI round-8 pattern theorems on the same 300 targets (`artifacts/ign/ei_r8_first300.json`): depth-3 251, 263, 253, 238, 4, 0, 253, 0, 241, 260; reductio 34, 0, 0, 11, 0, 0, 0, 64, 0, 29, 0.
- EI arms (`expert_iter.py --rounds 8 --k 32 --temperature 0.8 --batch 768`, seed = model seed; `artifacts/p2/ei_depth3_f0_a1_s{2..9}`, `ei_reductio_f0_s{3..10}_t2`, all `found_<r>.jsonl` kept; counts normalised, min-round rule). Depth-3 cumulative pattern theorems per round, s0–s9: s0 [2, 8, 117, 259, 299, 317, 327, 335]; s1 [4, 41, 175, 279, 311, 340, 354, 364]; s2 [0, 6, 88, 239, 278, 309, 327, 336]; s3 [0, 0, 1, 3, 28, 166, 265, 295]; s4 [0, 0, 0, 0, 0, 0, 1, 4]; s5 [0 × 8]; s6 [0, 1, 13, 166, 279, 313, 325, 330]; s7 [0 × 8]; s8 [0, 0, 1, 15, 114, 254, 292, 312]; s9 [8, 132, 281, 329, 338, 346, 351, 354]. Round-8 theorems / proofs / solved: s2 336/410/677, s3 295/368/589, s4 4/4/323, s5 0/0/357, s6 330/401/601, s7 0/0/318, s8 312/375/582, s9 354/433/602. **Ignition round (≥ 20 theorems)**: s0 3, s1 2, s2 3, s3 5, s4 never, s5 never, s6 4, s7 never, s8 5, s9 2; first pattern proof: 1, 1, 2, 3, 7, never, 2, never, 3, 1.
- Reductio per round, s0–s10: s0 [0, 1, 11, 24, 36, 55, 58, 58]; s3 [0, 0, 0, 0, 0, 1, 4, 16]; s7 [4, 34, 47, 51, 59, 82, 99, 112]; s9 [0, 0, 0, 0, 0, 1, 19, 49]; s1, s2, s4, s5, s6, s8, s10 [0 × 8]. Round-8 theorems / proofs: s3 16/16, s7 112/112, s9 49/51 (all strict, `patterns.reductio`). **Ignition round (≥ 12)**: s7 2, s0 4, s9 7, s3 8, others never; first proof: s7 1, s0 2, s3 6, s9 6. Untrained rounds (no proof found → no training; a frozen sample of all 606 targets): s3 5 rounds = 96,960 samples, s9 5 = 96,960, seven never-igniters 8 = 155,136 each, 0 pattern hits.
- Predicted first-proof round 1/(r·k·N) vs observed: reductio s7 0.23 → 1, s0 1.7 → 2, s3 2.6 → 6, s9 6.2 → 6; depth-3 s9 0.02 → 1, s1 0.05 → 1, s0 0.12 → 1, s6 6.3 → 2, s4 18.8 → 7; zero-rate depth-3 draws: 2, 3, 3, never, never.
- Rule "ignites by round 8 iff ≥ 1 pattern hit in the pre-RL sample": reductio 11/11 correct; depth-3 6/10 (s4 has 1 hit and did not ignite; s2, s3, s8 have 0 hits and did).
- Interventions (from the round-4 state; `artifacts/p2/<arm>_iv{K,T,S}`; K: round 5 at k = 128 then k = 32; T: round 5 at T = 1.0 then 0.8; S: one fine-tuning step on own found_4 + sibling found_4 (`ignition_transfer_mix.py`, `<arm>_ivS_transfer.json`: sibling proofs 204 for reductio s7's found_4; depth-3 sibling s2), then 4 rounds). Cumulative pattern theorems rounds 5–8 — depth-3 s3: K [40, 177, 279, 311], T [34, 197, 290, 319], S [297, 320, 330, 336] (parent [28, 166, 265, 295]); s4: K [0, 0, 0, 0], T [0, 0, 0, 0], S [286, 310, 326, 330]; s5: K 0, T [0, 0, 0, 1], S [300, 322, 330, 335]; s7: K 0, T 0, S [349, 351, 351, 352]. Reductio s3: K [2, 14, 28, 49], T [0, 1, 5, 14], S [56, 60, 71, 79] (parent [0, 1, 4, 16]); s9: K [0, 1, 13, 37], T [0, 1, 10, 27], S [60, 66, 66, 67] (parent [0, 1, 19, 49]); s4, s5, s6, s8, s10: K 0, T 0, S [63, 73, 94, 107] / [60, 65, 72, 91] / [69, 91, 101, 111] / [65, 83, 93, 109] / [61, 72, 93, 102]. **S ignited 11/11 at round 5 (r8 acquisition depth-3 0.330–0.352, reductio 0.111–0.183); K 2/11 (s3 r6, s9 r7), T 2/11 (s3 r8, s9 r8); 0/9 zero-rate arms for K and T.** Attempts per target by round 8: parent 256, K 352, T/S 256 (+ outside data for S).
- Base generalisation (≥ 1 pattern sample in 600k): depth-3 **10 of 16** f = 0 draws (a0 s0/s1, a1 s0–s9, a2 s0/s1, a3 s0/s1; Clopper–Pearson 95 % 0.35–0.85); reductio **4 of 11** (0.11–0.69). Round-1 EI sample (32 × N, pre-training): depth-3 3/10, reductio 1/11.
- Self-check (`log.md` 22:10): every counted reductio pattern proof and 100 per depth-3 arm re-verified with `nd_verify` against its prompt; coverage pattern proofs of four files re-verified — failure counts in log.md.
- Pods: RTX 3090 (p1, $0.50/h, 3.3 h) + 2 × A100 80 GB (p2, p3, $1.59/h, 3.0 h + 3.05 h); no A40 in stock. ≈ $11.5.

## Round 2 — Run 5: target pools that REQUIRE a pattern (2026-09-17; `necessity.py`, `required_pool.py`, `run5_analysis.py` → `artifacts/r5/summary.json`; arms `artifacts/r5/<arm>/round_*.json`, `found_8.jsonl`; pools `data/p2/targets_{reductio,derived_ore}_req.jsonl`, `transfer_*_req.jsonl`; oracle labels `data/p2/run5_*_nec.jsonl`)
- Oracle: `minlen.py --forbid` (DN | ORE_DERIVED | ORE_DERIVED_LOOSE | ORE_IN_IMPI | ANDE_NEGI_HYP | ORE_IN_ORE), 37-case verifier-checked selftest. requires := unrestricted search finds a proof ≤ bound (10) AND restricted search fails within the bound without timeout. Consistency flags stored per record (`oracle_ok`, `restriction_ok`): 0 inconsistencies in 945 + 1,568 + 1,381 + 5,040 labellings; 0 timeouts.
- Reductio candidates (`reductio2_cands.jsonl`, 945 classical-only schema instances, no `( ~ ( ~`): `--forbid DN` proves **0 / 945**; unrestricted ≤ 10 for 559 (6/7/8/9/10: 45/90/230/140/54). Pool **targets_reductio_req 300** (7/8/9/10 lines: 52/133/82/33; 16 schemata, 26 each for 11 of them) + **transfer 150**; class overlap with train_reductio_f0, f0.1, heldout, val-36: 0/0/0/0.
- Cap-8 derived-ORE candidates (generator theorems, 12–16-line generating proofs, no ≤ 8-line proof): 1,568 existing + 1,381 (`raw_long_c8c`, 15M tries, 87,232 classes) + 5,040 (`raw_long_c8d`, 54M tries, 300,774 classes); reachable at ≤ 10: 1,441 / 1,283 / 4,660; **required 120 / 68 / 196** (7.7 / 4.9 / 3.9 %). Pool **targets_derived_ore_req 300** (9/10 lines: 126/174) + **transfer 65**; overlap with the three cap-8 sets, heldout_c8, val-36: 0.
- Reductio arms (k = 32, 8 rounds, T = 0.8; acquisition = targets solved with a normalised proof containing `patterns.reductio`; min-round rule; solved-without-pattern = oracle violations):
  - EI f = 0 s0: **51 / 300 solved, 51 pattern (0.170)**, 52 proofs, first round 1, per round 2/11/25/47/51/51/51/51, written 7-line 51 + 8-line 1, transfer 25/150 (all pattern), heldout greedy 0.891, violations 0. By schema: nand_neg 26/26, negimp_to_pos 25/26, all 14 others 0.
  - EI f = 0 s1: **0 / 300**; s2: **0 / 300** (transfer 0/150; heldout 0.871 / 0.894).
  - EI f = 0.1 s0: **53 (0.177)**, per round 14/39/51/53/53/53/53/53, transfer 27/150; by schema nand_neg 26, negimp_to_pos 26, chain_neg 1. s1: **52 (0.173)**, per round 17/40/51/52/…, transfer 27; nand_neg 26, negimp_to_pos 26.
  - Frozen (256 attempts): f = 0 s0 **4** (nand_neg), s1 0, s2 0; f = 0.1 s0 **27** (nand_neg 21, negimp_to_pos 6), s1 **21**.
  - Base pass@10⁴ on all 300 targets (`artifacts/r5/cov_reductio_f0_s{0,1,2}_req.s0.jsonl`, 3·10⁶ samples each): s0 **6 targets** (113 hits, all strict reductio, all nand_neg; first hits 139/257/388/392/3,428/4,899; 1 within 256), s1 **0**, s2 **1 target, 1 hit** (3.3·10⁻⁷ per sample). Violations 0.
- Cap-8 derived-ORE arms (acquisition = `patterns.derived_ore_strict` on the model's proof):
  - EI f = 0 s0: **26 / 300 solved, 26 pattern (0.087)**, 35 proofs, first round 1, per round 8/12/16/20/22/24/25/26, written 9-line 25 + 10-line 10, transfer 8/65, heldout 0.927, violations 0. s1: **24 (0.080)**, 34 proofs, 7/11/13/14/16/18/21/24, transfer 8/65, violations 0.
  - EI f = 10⁻² s0: **48 (0.160)**, 57 proofs, 14/26/33/34/37/42/44/48, transfer 13/65; s1: **63 (0.210)**, 96 proofs, 20/30/37/42/52/57/61/63, written 9/10/11-line 52/41/3, transfer 14/65. Violations 0.
  - Frozen: f = 0 s0 **13** (21 proofs), s1 **11**; f = 10⁻² s0 **21**, s1 **28**.
  - Base pass@10⁴ f = 0 s0 (`cov_derived_ore_strict_f0_c8_s0_req.s0.jsonl`): **27 / 300 targets** (17,043 hits of 3·10⁶ = 5.7·10⁻³ per sample, all strict; 13 within 256; hit counts per target 5,601 / 4,133 / 2,664 / 1,257 / 1,224 / 711 / …). EI f = 0 s0's 26 solved targets: 18 base-reachable at 10⁴, **8 EI-only**. s1 (`cov_derived_ore_strict_f0_c8_s1_req.s0.jsonl`): **27 / 300** (16,044 hits, 5.3·10⁻³ per sample, 11 within 256; per-target hits 6,746 / 4,261 / 2,584 / 1,600 / 365 / …); EI s1's 24 solved = 17 base-reachable + **7 EI-only**.
- Campaign numbers on the non-required pools, for the side-by-side: block B reductio2 (606) EI f = 0 s0/s1/s2 0.096/0/0, f = 0.1 0.157/0.104, frozen 0.005/0/0, 0.041/0.048; block C c8 (500) strict acquisition f = 0 0.008/0.008, f = 10⁻³ 0.022, f = 10⁻² 0.022, frozen 0.006/0.004, plain solve 0.39–0.44.
- Pods: p1, p2 RTX 3090 $0.50/h from 19:12 / 19:20 UTC (shared with run 2 from 21:34); run-5 share ≈ 2 × 3 h ≈ $3.
