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
- Pods: p1, p2 RTX 3090 $0.50/h from 19:12 / 19:20 UTC (shared with run 2 from 21:34); run-5 share ≈ 2 × 2.8 h ≈ $3. Balance 19:00 → 22:05: $121.40 → see log.
- Bucket: `hf://buckets/dan-pandori/nd-rl/round2/run5/artifacts/r5` (arm dirs with `round_*.json`, `found_8.jsonl`, `found_transfer_8.jsonl`, coverage files, `summary.json`), `…/run5/ckpts/r5` (round-8 EI checkpoints of the 7 arms that trained), `…/run5/data/r5` (the two pools, transfer sets, oracle labels and candidate files).

## Round 2 — Run 3: minimum outside data for ignition (2026-09-17/18; `run3_inject.py`, `run3_analysis.py` → `artifacts/r3/summary.json`; arms `artifacts/r3/<arm>_<cond>/round_{5..8}.json`, `found_8.jsonl`; injected records in `artifacts/p2/<arm>_<cond>_manifest.json`; injection files `data/r3/inject_*.jsonl`)
- Conditions per arm (from the round-4 state; one 600-step fine-tune on own found_4 ≤ 4/theorem ×4 + injected ×4 + 20k retained; then rounds 5–8, k = 32): sib1 / sib4 / sib16 = sibling pattern proofs of distinct theorems (depth-3 from a1 s2's found_4, reductio from s7's found_4); gen4 = 4 verifier-valid 6-line generator proofs with the pattern (class-disjoint from every target/transfer pool); other4 = 4 generator proofs of the other pattern; inv4 = 4 strings with the pattern's tokens and one corrupted citation (nd_verify reasons stored in the file; `train.py --cap 0` does not verify). Ignition threshold 20 / 1,000 (depth-3), 12 / 606 (reductio). Counts: cumulative pattern theorems per round (patterns.py on the normalised proof, min-round rule), acquisition at round 8. Depth-3 s5 inv4's round 8 and reductio s2 inv4 were re-run after OOM kills (the killed s2 inv4 attempt had reached 6 / 47 at rounds 5–6; the clean rerun is what is reported).
- ei_depth3_f0_a1_s4 (depth3; parent per round [0, 0, 0, 0, 0, 0, 1, 4]):
  - sib1: rounds 5–8 pattern theorems 8 / 91 / 195 / 264, solved 256 / 355 / 473 / 555, ignition round 6, round-8 acquisition 0.264; injected 1 (valid 1, with pattern 1), own proofs in the mix 910
  - sib4: rounds 5–8 pattern theorems 105 / 250 / 308 / 322, solved 361 / 522 / 591 / 613, ignition round 5, round-8 acquisition 0.322; injected 4 (valid 4, with pattern 4), own proofs in the mix 910
  - sib16: rounds 5–8 pattern theorems 236 / 303 / 336 / 344, solved 484 / 564 / 612 / 627, ignition round 5, round-8 acquisition 0.344; injected 16 (valid 16, with pattern 16), own proofs in the mix 910
  - gen4: rounds 5–8 pattern theorems 1 / 27 / 98 / 167, solved 252 / 294 / 397 / 480, ignition round 6, round-8 acquisition 0.167; injected 4 (valid 4, with pattern 4), own proofs in the mix 910
  - other4: rounds 5–8 pattern theorems 0 / 0 / 0 / 0, solved 253 / 289 / 312 / 333, ignition round None, round-8 acquisition 0.0; injected 4 (valid 4, with pattern 4), own proofs in the mix 910
  - inv4: rounds 5–8 pattern theorems 4 / 56 / 173 / 252, solved 250 / 312 / 444 / 537, ignition round 6, round-8 acquisition 0.252; injected 4 (valid 0, with pattern 4), own proofs in the mix 910
- ei_depth3_f0_a1_s5 (depth3; parent per round [0, 0, 0, 0, 0, 0, 0, 0]):
  - sib1: rounds 5–8 pattern theorems 23 / 135 / 198 / 262, solved 296 / 439 / 528 / 607, ignition round 5, round-8 acquisition 0.262; injected 1 (valid 1, with pattern 1), own proofs in the mix 968
  - sib4: rounds 5–8 pattern theorems 91 / 241 / 291 / 316, solved 372 / 541 / 618 / 661, ignition round 5, round-8 acquisition 0.316; injected 4 (valid 4, with pattern 4), own proofs in the mix 968
  - sib16: rounds 5–8 pattern theorems 143 / 250 / 294 / 312, solved 413 / 533 / 587 / 625, ignition round 5, round-8 acquisition 0.312; injected 16 (valid 16, with pattern 16), own proofs in the mix 968
  - gen4: rounds 5–8 pattern theorems 2 / 54 / 170 / 235, solved 276 / 351 / 496 / 583, ignition round 6, round-8 acquisition 0.235; injected 4 (valid 4, with pattern 4), own proofs in the mix 968
  - other4: rounds 5–8 pattern theorems 0 / 0 / 0 / 0, solved 276 / 303 / 335 / 346, ignition round None, round-8 acquisition 0.0; injected 4 (valid 4, with pattern 4), own proofs in the mix 968
  - inv4: rounds 5–8 pattern theorems 0 / 0 / 0 / 0, solved 272 / 300 / 321 / 339, ignition round None, round-8 acquisition 0.0; injected 4 (valid 0, with pattern 4), own proofs in the mix 968
- ei_depth3_f0_a1_s3 (depth3; parent per round [0, 0, 1, 3, 28, 166, 265, 295]):
  - sib1: rounds 5–8 pattern theorems 69 / 228 / 286 / 322, solved 311 / 479 / 553 / 599, ignition round 5, round-8 acquisition 0.322; injected 1 (valid 1, with pattern 1), own proofs in the mix 916
  - sib4: rounds 5–8 pattern theorems 101 / 258 / 298 / 326, solved 348 / 516 / 565 / 595, ignition round 5, round-8 acquisition 0.326; injected 4 (valid 4, with pattern 4), own proofs in the mix 916
  - sib16: rounds 5–8 pattern theorems 201 / 284 / 327 / 344, solved 447 / 537 / 588 / 610, ignition round 5, round-8 acquisition 0.344; injected 16 (valid 16, with pattern 16), own proofs in the mix 916
  - gen4: rounds 5–8 pattern theorems 84 / 238 / 290 / 322, solved 325 / 490 / 551 / 589, ignition round 5, round-8 acquisition 0.322; injected 4 (valid 4, with pattern 4), own proofs in the mix 916
  - other4: rounds 5–8 pattern theorems 42 / 197 / 274 / 294, solved 291 / 473 / 570 / 602, ignition round 5, round-8 acquisition 0.294; injected 4 (valid 4, with pattern 4), own proofs in the mix 916
  - inv4: rounds 5–8 pattern theorems 45 / 183 / 267 / 305, solved 288 / 436 / 532 / 579, ignition round 5, round-8 acquisition 0.305; injected 4 (valid 0, with pattern 4), own proofs in the mix 916
- ei_reductio_f0_s1_t2 (reductio; parent per round [0, 0, 0, 0, 0, 0, 0, 0]):
  - sib1: rounds 5–8 pattern theorems 6 / 24 / 31 / 44, solved 6 / 24 / 31 / 44, ignition round 6, round-8 acquisition 0.073; injected 1 (valid 1, with pattern 1), own proofs in the mix 0
  - sib4: rounds 5–8 pattern theorems 21 / 36 / 41 / 43, solved 21 / 36 / 41 / 43, ignition round 5, round-8 acquisition 0.071; injected 4 (valid 4, with pattern 4), own proofs in the mix 0
  - sib16: rounds 5–8 pattern theorems 51 / 62 / 75 / 80, solved 51 / 62 / 75 / 80, ignition round 5, round-8 acquisition 0.132; injected 16 (valid 16, with pattern 16), own proofs in the mix 0
  - gen4: rounds 5–8 pattern theorems 0 / 0 / 0 / 0, solved 0 / 0 / 0 / 0, ignition round None, round-8 acquisition 0.0; injected 4 (valid 4, with pattern 4), own proofs in the mix 0
  - other4: rounds 5–8 pattern theorems 0 / 0 / 0 / 0, solved 0 / 0 / 0 / 0, ignition round None, round-8 acquisition 0.0; injected 4 (valid 4, with pattern 4), own proofs in the mix 0
  - inv4: rounds 5–8 pattern theorems 0 / 0 / 0 / 0, solved 0 / 0 / 0 / 0, ignition round None, round-8 acquisition 0.0; injected 4 (valid 0, with pattern 4), own proofs in the mix 0
- ei_reductio_f0_s2_t2 (reductio; parent per round [0, 0, 0, 0, 0, 0, 0, 0]):
  - sib1: rounds 5–8 pattern theorems 17 / 43 / 61 / 65, solved 17 / 43 / 61 / 65, ignition round 5, round-8 acquisition 0.107; injected 1 (valid 1, with pattern 1), own proofs in the mix 0
  - sib4: rounds 5–8 pattern theorems 32 / 57 / 65 / 65, solved 32 / 57 / 65 / 65, ignition round 5, round-8 acquisition 0.107; injected 4 (valid 4, with pattern 4), own proofs in the mix 0
  - sib16: rounds 5–8 pattern theorems 50 / 66 / 72 / 95, solved 50 / 66 / 72 / 95, ignition round 5, round-8 acquisition 0.157; injected 16 (valid 16, with pattern 16), own proofs in the mix 0
  - gen4: rounds 5–8 pattern theorems 5 / 29 / 53 / 61, solved 5 / 29 / 53 / 61, ignition round 6, round-8 acquisition 0.101; injected 4 (valid 4, with pattern 4), own proofs in the mix 0
  - other4: rounds 5–8 pattern theorems 0 / 0 / 0 / 0, solved 0 / 0 / 0 / 0, ignition round None, round-8 acquisition 0.0; injected 4 (valid 4, with pattern 4), own proofs in the mix 0
  - inv4: rounds 5–8 pattern theorems 0 / 1 / 4 / 14, solved 0 / 1 / 4 / 14, ignition round 8, round-8 acquisition 0.023; injected 4 (valid 0, with pattern 4), own proofs in the mix 0
- Pods: p4 (depth-3 jobs, from 22:05) and p5 (reductio, from 22:17), RTX 3090s, shared with run 4 from 23:09; run-3 share ≈ 2 × 1.6 h ≈ $1.6. Bucket: `hf://buckets/dan-pandori/nd-rl/round2/run3/{artifacts/r3,data/r3,ckpts/r3}` (ckpts: the injected-step checkpoints `*_r4t.pt` and the round-8 checkpoints).

## Round 2 — Run 1: ND → Lean and novelty by scale (2026-09-17/18; `nd2lean.py`, `lean_prompts.py`, `run_vllm.py`, `scale_prompts.py`, `run1_analysis.py` → `artifacts/r1/summary.json`)
- Step 1 agreement (`artifacts/r1/lean_<pool>.jsonl`, one record per proof with nd_verify and Lean verdicts; Lean 4.34.0 core via elan on the VPS; `lean_check` 40 theorems per file, re-split on Lean's ~100-error cap):
  - examples: n 21, both accept 21, nd-only 0, Lean-only 0, both reject 0
  - found_targets16: n 137828, both accept 137828, nd-only 0, Lean-only 0, both reject 0
  - found_transfer16: n 75085, both accept 75085, nd-only 0, Lean-only 0, both reject 0
  - heldout: n 5000, both accept 5000, nd-only 0, Lean-only 0, both reject 0
  - negatives: n 4012, both accept 0, nd-only 0, Lean-only 0, both reject 4012
  - r2_depth4_found: n 15327, both accept 15327, nd-only 0, Lean-only 0, both reject 0
  - r5_c8_found: n 3264, both accept 3264, nd-only 0, Lean-only 0, both reject 0
  - r5_reductio_found: n 2271, both accept 2271, nd-only 0, Lean-only 0, both reject 0
  - rl_targets: n 3000, both accept 3000, nd-only 0, Lean-only 0, both reject 0
  - train10k: n 10000, both accept 10000, nd-only 0, Lean-only 0, both reject 0
  - transfer: n 1638, both accept 1638, nd-only 0, Lean-only 0, both reject 0
  - val36_ref: n 36, both accept 36, nd-only 0, Lean-only 0, both reject 0
  - The found_transfer16 row above is the corrected re-run (the first run rejected 67,773 proofs that start above N1 because premise hypotheses were named by line index; fixed 23:20 UTC). Negatives: 4,012 corrupted proofs (cited line ±k 508, rule swapped 874, atom swapped 874, box bar added/removed 874, line dropped 874, plus the 8 run-3 invalid strings), all rejected by nd_verify, all rejected by Lean or by the translator's structural mirror.
- Step 2 (`data/r1/prompts.jsonl`: 236 theorems = validation-36 + 200 transfer stratified by generating length 7–16 (21 per length, 11 at 16) × 5 example-set draws × 3 forms; 20 worked examples per draw = 12 held-out generator proofs (lengths 2–6) + 8 RL-found transfer proofs of 7–9 written lines, class-disjoint from the test theorems, identical across forms; Qwen3-Coder-30B-A3B-Instruct, vLLM 0.29 on p6 (A100 80 GB), greedy + 8 samples at T = 0.7, top-p 0.95, max 1,200 tokens; `artifacts/r1/gens_qwen30b.jsonl`, `scored_qwen30b.jsonl` (31,860 rows; Lean outputs checked with Lean, token and English outputs with nd_verify after a deterministic parse back to tokens)):
  - english|val36_<=6: n 60 (theorem × draw), greedy 0.500 [0.377, 0.623], pass@8 0.550 [0.425, 0.669]
  - english|val36_>6: n 120 (theorem × draw), greedy 0.100 [0.058, 0.167], pass@8 0.117 [0.071, 0.186]
  - english|transfer_7: n 105 (theorem × draw), greedy 0.276 [0.200, 0.368], pass@8 0.371 [0.285, 0.467]
  - english|transfer_8: n 105 (theorem × draw), greedy 0.400 [0.311, 0.496], pass@8 0.476 [0.383, 0.571]
  - english|transfer_9: n 105 (theorem × draw), greedy 0.219 [0.151, 0.307], pass@8 0.286 [0.208, 0.378]
  - english|transfer_10: n 105 (theorem × draw), greedy 0.381 [0.294, 0.476], pass@8 0.457 [0.365, 0.552]
  - english|transfer_11: n 105 (theorem × draw), greedy 0.238 [0.167, 0.328], pass@8 0.381 [0.294, 0.476]
  - english|transfer_12: n 105 (theorem × draw), greedy 0.248 [0.175, 0.338], pass@8 0.352 [0.268, 0.447]
  - english|transfer_13: n 105 (theorem × draw), greedy 0.390 [0.303, 0.486], pass@8 0.543 [0.448, 0.635]
  - english|transfer_14: n 105 (theorem × draw), greedy 0.314 [0.233, 0.408], pass@8 0.457 [0.365, 0.552]
  - english|transfer_15: n 105 (theorem × draw), greedy 0.276 [0.200, 0.368], pass@8 0.390 [0.303, 0.486]
  - english|transfer_16: n 55 (theorem × draw), greedy 0.273 [0.173, 0.402], pass@8 0.327 [0.218, 0.459]
  - english|all: n 1180 (theorem × draw), greedy 0.292 [0.267, 0.319], pass@8 0.386 [0.358, 0.414]
  - lean|val36_<=6: n 60 (theorem × draw), greedy 0.867 [0.758, 0.931], pass@8 0.900 [0.799, 0.953]
  - lean|val36_>6: n 120 (theorem × draw), greedy 0.458 [0.372, 0.547], pass@8 0.542 [0.453, 0.628]
  - lean|transfer_7: n 105 (theorem × draw), greedy 0.648 [0.553, 0.732], pass@8 0.762 [0.672, 0.833]
  - lean|transfer_8: n 105 (theorem × draw), greedy 0.600 [0.504, 0.689], pass@8 0.705 [0.612, 0.784]
  - lean|transfer_9: n 105 (theorem × draw), greedy 0.552 [0.457, 0.644], pass@8 0.733 [0.642, 0.809]
  - lean|transfer_10: n 105 (theorem × draw), greedy 0.600 [0.504, 0.689], pass@8 0.667 [0.572, 0.750]
  - lean|transfer_11: n 105 (theorem × draw), greedy 0.505 [0.411, 0.599], pass@8 0.657 [0.562, 0.741]
  - lean|transfer_12: n 105 (theorem × draw), greedy 0.552 [0.457, 0.644], pass@8 0.667 [0.572, 0.750]
  - lean|transfer_13: n 105 (theorem × draw), greedy 0.581 [0.485, 0.671], pass@8 0.686 [0.592, 0.767]
  - lean|transfer_14: n 105 (theorem × draw), greedy 0.562 [0.466, 0.653], pass@8 0.657 [0.562, 0.741]
  - lean|transfer_15: n 105 (theorem × draw), greedy 0.505 [0.411, 0.599], pass@8 0.600 [0.504, 0.689]
  - lean|transfer_16: n 55 (theorem × draw), greedy 0.382 [0.265, 0.514], pass@8 0.600 [0.468, 0.719]
  - lean|all: n 1180 (theorem × draw), greedy 0.563 [0.534, 0.591], pass@8 0.675 [0.647, 0.701]
  - tokens|val36_<=6: n 60 (theorem × draw), greedy 0.433 [0.316, 0.559], pass@8 0.517 [0.393, 0.638]
  - tokens|val36_>6: n 120 (theorem × draw), greedy 0.158 [0.104, 0.234], pass@8 0.200 [0.138, 0.280]
  - tokens|transfer_7: n 105 (theorem × draw), greedy 0.305 [0.225, 0.398], pass@8 0.333 [0.250, 0.428]
  - tokens|transfer_8: n 105 (theorem × draw), greedy 0.267 [0.191, 0.358], pass@8 0.343 [0.259, 0.438]
  - tokens|transfer_9: n 105 (theorem × draw), greedy 0.238 [0.167, 0.328], pass@8 0.324 [0.242, 0.418]
  - tokens|transfer_10: n 105 (theorem × draw), greedy 0.257 [0.183, 0.348], pass@8 0.305 [0.225, 0.398]
  - tokens|transfer_11: n 105 (theorem × draw), greedy 0.162 [0.104, 0.244], pass@8 0.295 [0.216, 0.388]
  - tokens|transfer_12: n 105 (theorem × draw), greedy 0.210 [0.143, 0.297], pass@8 0.257 [0.183, 0.348]
  - tokens|transfer_13: n 105 (theorem × draw), greedy 0.314 [0.233, 0.408], pass@8 0.400 [0.311, 0.496]
  - tokens|transfer_14: n 105 (theorem × draw), greedy 0.314 [0.233, 0.408], pass@8 0.362 [0.276, 0.457]
  - tokens|transfer_15: n 105 (theorem × draw), greedy 0.276 [0.200, 0.368], pass@8 0.343 [0.259, 0.438]
  - tokens|transfer_16: n 55 (theorem × draw), greedy 0.236 [0.144, 0.363], pass@8 0.345 [0.234, 0.477]
  - tokens|all: n 1180 (theorem × draw), greedy 0.258 [0.233, 0.283], pass@8 0.326 [0.300, 0.354]
  - paired Lean − tokens (greedy): mean 0.305, bootstrap 95 % [0.257, 0.354] over 236 theorems (per theorem: mean over 5 draws of the 0/1 difference)
  - paired greedy|val36_<=6: 0.433 (n 12)
  - paired greedy|val36_>6: 0.300 (n 24)
  - paired greedy|transfer_7: 0.343 (n 21)
  - paired greedy|transfer_8: 0.333 (n 21)
  - paired greedy|transfer_9: 0.314 (n 21)
  - paired greedy|transfer_10: 0.343 (n 21)
  - paired greedy|transfer_11: 0.343 (n 21)
  - paired greedy|transfer_12: 0.343 (n 21)
  - paired greedy|transfer_13: 0.267 (n 21)
  - paired greedy|transfer_14: 0.248 (n 21)
  - paired greedy|transfer_15: 0.229 (n 21)
  - paired greedy|transfer_16: 0.145 (n 11)
  - paired Lean − tokens (pass8): mean 0.348, bootstrap 95 % [0.298, 0.397] over 236 theorems (per theorem: mean over 5 draws of the 0/1 difference)
  - paired pass8|val36_<=6: 0.383 (n 12)
  - paired pass8|val36_>6: 0.342 (n 24)
  - paired pass8|transfer_7: 0.429 (n 21)
  - paired pass8|transfer_8: 0.362 (n 21)
  - paired pass8|transfer_9: 0.410 (n 21)
  - paired pass8|transfer_10: 0.362 (n 21)
  - paired pass8|transfer_11: 0.362 (n 21)
  - paired pass8|transfer_12: 0.410 (n 21)
  - paired pass8|transfer_13: 0.286 (n 21)
  - paired pass8|transfer_14: 0.295 (n 21)
  - paired pass8|transfer_15: 0.257 (n 21)
  - paired pass8|transfer_16: 0.255 (n 11)

## Round 2 — Run 2: six new patterns (2026-09-17/18; `patterns2.py`, `run2_sets.py`, `necessity.py`, `required_pool.py`, `run2_analysis.py` → `artifacts/r2/summary.json`; arms `artifacts/r2/<kind>_<pattern>_<tag>/`, coverage `artifacts/r2/cov_<pattern>_<tag>.s0.jsonl`, drift `artifacts/r2/drift_negi_ande_hyp_s1_r4.s0.jsonl`; sets `data/r2/train_r2_*.jsonl`, reports `data/r2/assemble_report_r2.json` (cap 6) and `assemble_report_r2_c8.json` (cap 8); pools `data/r2/targets_<pattern>.jsonl`, `transfer_<pattern>.jsonl`, oracle labels `data/r2/nec_<pattern>.jsonl`)
- Pre-registered classes (log.md 19:47 UTC): structural = depth4, impe_chain4, nested_ore; rule sequence = impi_ore, negi_ande_hyp, ori_ore (decoration control). Predicates: `patterns2.py` (15 verifier-checked tests).
- Sets (155,000 = 31,000 per length 2–6, uniform per length from `pool_cap6_recon` with 3,151 run-2 pool classes and the held-out set excluded; written-form counts identical to pruned): struct: excluded none, counts {'derived_ore': 436, 'reductio': 18866, 'depth3': 13902, 'impi_ore': 130, 'negi_ande_hyp': 11, 'ori_ore': 36}; impi_ore_f0: excluded impi_ore, counts {'derived_ore': 356, 'reductio': 18879, 'depth3': 14048, 'negi_ande_hyp': 14, 'ori_ore': 62}; negi_ande_hyp_f0: excluded negi_ande_hyp, counts {'derived_ore': 406, 'reductio': 18932, 'depth3': 14038, 'impi_ore': 128, 'ori_ore': 43}; ori_ore_f0: excluded ori_ore, counts {'derived_ore': 367, 'reductio': 18667, 'depth3': 13970, 'impi_ore': 118, 'negi_ande_hyp': 19}. Cap-8 addendum set c8_depth4_f0 (154,994 = 22,142 per length 2–8 from `pool_cap8` with depth-4 excluded — the pool itself has 0 depth-4 / chain-4 / nested-ORE proofs, `sets_c8.log`): counts {'derived_ore': 3802, 'reductio': 8280, 'depth3': 10435, 'depth4': 0, 'impe_chain4': 0, 'nested_ore': 0, 'nested_ore3': 0, 'impi_ore': 5327, 'negi_ande_hyp': 35, 'ori_ore': 2882}.
- Pools (`necessity.py`, bound 10 / 13; `requires` = restricted search fails within the bound, `uses` = shortest found proof contains the pattern): depth4 500 targets (generator with box-depth cap 5; 8/9/10 lines 269/53/178; 176 required) + 200 transfer; impe_chain4 500 (schemata; 8/9/10: 110/246/144; no restriction oracle) + 200; nested_ore 300 (schemata; all required; 11/12/13: 113/172/15) + 41; impi_ore 500 (generator; 7–10: 144/171/132/53; 109 required) + 200; negi_ande_hyp 400 (generator; 213/86/83/18; 97 required) + 94; ori_ore 400 (generator; generating proof contains it, shortest never does; 310/81/8/1) + 160.
- Arms: EI k = 32, 8 rounds, T = 0.8, retain 20k; frozen at equal attempts; pre-RL pass@2,000 on the 300 shortest targets (nested_ore: 269 at k = 2,000 for s0, 100 at k = 500 for s1; impe_chain4 s0: 96 targets, the run was cut). Acquisition = targets solved with a normalised proof containing the pattern (min-round rule); `viol` = required targets solved without it.
- **depth4** (structural; 500 targets, 176 required):
  - ei_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.957
  - ei_s1: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.959
  - frozen_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.957
  - frozen_s1: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.959
  - ei_c8ctl_s0: solved 485, pattern theorems 485 (0.970), pattern proofs 517, required solved / with pattern / violations 162 / 162 / 0, ignition round 1, first pattern proof round 1, per round [123, 312, 344, 381, 453, 479, 484, 485], solved per round [123, 313, 344, 381, 453, 479, 484, 485], transfer solved 187, held-out greedy 0.924
  - ei_c8ctl_s1: solved 481, pattern theorems 481 (0.962), pattern proofs 506, required solved / with pattern / violations 162 / 162 / 0, ignition round 1, first pattern proof round 1, per round [147, 280, 321, 348, 455, 475, 479, 481], solved per round [148, 281, 322, 349, 456, 476, 479, 481], transfer solved 189, held-out greedy 0.934
  - frozen_c8ctl_s0: solved 150, pattern theorems 148 (0.296), pattern proofs 151, required solved / with pattern / violations 0 / 0 / 0, ignition round 1, first pattern proof round 1, per round [123, 129, 136, 139, 143, 146, 147, 148], solved per round [123, 129, 137, 140, 144, 147, 149, 150], transfer solved 72, held-out greedy 0.918
  - frozen_c8ctl_s1: solved 202, pattern theorems 201 (0.402), pattern proofs 201, required solved / with pattern / violations 0 / 0 / 0, ignition round 1, first pattern proof round 1, per round [147, 165, 180, 187, 189, 195, 199, 201], solved per round [148, 166, 180, 187, 189, 195, 200, 202], transfer solved 85, held-out greedy 0.931
  - ei_c8f0_s0: solved 481, pattern theorems 481 (0.962), pattern proofs 515, required solved / with pattern / violations 161 / 161 / 0, ignition round 1, first pattern proof round 1, per round [174, 297, 331, 417, 469, 474, 479, 481], solved per round [174, 297, 331, 417, 469, 474, 479, 481], transfer solved 187, held-out greedy 0.923
  - ei_c8f0_s1: solved 482, pattern theorems 482 (0.964), pattern proofs 515, required solved / with pattern / violations 161 / 161 / 0, ignition round 1, first pattern proof round 1, per round [131, 297, 332, 338, 348, 414, 474, 482], solved per round [131, 297, 332, 338, 348, 414, 474, 482], transfer solved 187, held-out greedy 0.932
  - frozen_c8f0_s1: solved 180, pattern theorems 180 (0.360), pattern proofs 180, required solved / with pattern / violations 0 / 0 / 0, ignition round 1, first pattern proof round 1, per round [131, 151, 160, 167, 172, 174, 178, 180], solved per round [131, 151, 160, 167, 172, 174, 178, 180], transfer solved 77, held-out greedy 0.923
  - pre-RL s0: 300 targets, 600000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
  - pre-RL s1: 300 targets, 600000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
  - pre-RL c8ctl_s0: 300 targets, 600000 samples, targets with a pattern proof 110, pattern hits 78987 (rate 1.32e-01), within 256 attempts 87, targets solved at all 113
  - pre-RL c8ctl_s1: 300 targets, 600000 samples, targets with a pattern proof 134, pattern hits 68779 (rate 1.15e-01), within 256 attempts 113, targets solved at all 137
  - pre-RL c8f0_s0: 300 targets, 600000 samples, targets with a pattern proof 131, pattern hits 117063 (rate 1.95e-01), within 256 attempts 113, targets solved at all 132
  - pre-RL c8f0_s1: 300 targets, 600000 samples, targets with a pattern proof 128, pattern hits 63849 (rate 1.06e-01), within 256 attempts 106, targets solved at all 128
- **impe_chain4** (structural; 500 targets, 0 required):
  - ei_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.957
  - ei_s1: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.959
  - frozen_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.957
  - frozen_s1: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.959
  - pre-RL s0: 96 targets, 192000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
  - pre-RL s1: 300 targets, 600000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
- **nested_ore** (structural; 300 targets, 300 required):
  - ei_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.957
  - ei_s1: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.959
  - frozen_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.957
  - frozen_s1: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.959
  - pre-RL s0: 269 targets, 538000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
  - pre-RL s1: 100 targets, 50000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
- **impi_ore** (rule_sequence; 500 targets, 109 required):
  - ei_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.946
  - ei_s1: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.961
  - frozen_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.946
  - frozen_s1: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.961
  - ei_natctl_s0: solved 95, pattern theorems 95 (0.190), pattern proofs 98, required solved / with pattern / violations 4 / 4 / 0, ignition round 2, first pattern proof round 1, per round [5, 30, 51, 78, 88, 92, 92, 95], solved per round [5, 30, 51, 78, 88, 92, 92, 95], transfer solved 34, held-out greedy 0.966
  - ei_natctl_s1: solved 111, pattern theorems 111 (0.222), pattern proofs 116, required solved / with pattern / violations 4 / 4 / 0, ignition round 2, first pattern proof round 1, per round [9, 37, 53, 64, 89, 100, 105, 111], solved per round [9, 37, 53, 64, 89, 100, 105, 111], transfer solved 45, held-out greedy 0.963
  - frozen_natctl_s0: solved 10, pattern theorems 10 (0.020), pattern proofs 10, required solved / with pattern / violations 0 / 0 / 0, ignition round 8, first pattern proof round 1, per round [5, 6, 6, 6, 8, 9, 9, 10], solved per round [5, 6, 6, 6, 8, 9, 9, 10], transfer solved 2, held-out greedy 0.957
  - frozen_natctl_s1: solved 17, pattern theorems 17 (0.034), pattern proofs 20, required solved / with pattern / violations 0 / 0 / 0, ignition round 3, first pattern proof round 1, per round [9, 9, 12, 14, 16, 16, 16, 17], solved per round [9, 9, 12, 14, 16, 16, 16, 17], transfer solved 11, held-out greedy 0.959
  - pre-RL s0: 300 targets, 600000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
  - pre-RL s1: 300 targets, 600000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
  - pre-RL natctl_s0: 300 targets, 600000 samples, targets with a pattern proof 12, pattern hits 374 (rate 6.23e-04), within 256 attempts 7, targets solved at all 12
  - pre-RL natctl_s1: 300 targets, 600000 samples, targets with a pattern proof 26, pattern hits 777 (rate 1.29e-03), within 256 attempts 14, targets solved at all 26
- **negi_ande_hyp** (rule_sequence; 400 targets, 97 required):
  - ei_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.944
  - ei_s1: solved 59, pattern theorems 59 (0.147), pattern proofs 60, required solved / with pattern / violations 0 / 0 / 0, ignition round 5, first pattern proof round 4, per round [0, 0, 0, 1, 15, 40, 49, 59], solved per round [0, 0, 0, 1, 15, 40, 49, 59], transfer solved 12, held-out greedy 0.970
  - frozen_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.944
  - frozen_s1: solved 2, pattern theorems 2 (0.005), pattern proofs 2, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round 4, per round [0, 0, 0, 1, 2, 2, 2, 2], solved per round [0, 0, 0, 1, 2, 2, 2, 2], transfer solved 1, held-out greedy 0.973
  - ei_natctl_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.957
  - ei_natctl_s1: solved 11, pattern theorems 11 (0.028), pattern proofs 11, required solved / with pattern / violations 0 / 0 / 0, ignition round 7, first pattern proof round 4, per round [0, 0, 0, 1, 1, 3, 11, 11], solved per round [0, 0, 0, 1, 1, 3, 11, 11], transfer solved 3, held-out greedy 0.961
  - frozen_natctl_s0: solved 0, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [0, 0, 0, 0, 0, 0, 0, 0], transfer solved 0, held-out greedy 0.957
  - frozen_natctl_s1: solved 3, pattern theorems 3 (0.007), pattern proofs 3, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round 4, per round [0, 0, 0, 1, 1, 1, 2, 3], solved per round [0, 0, 0, 1, 1, 1, 2, 3], transfer solved 1, held-out greedy 0.959
  - pre-RL s0: 300 targets, 600000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
  - pre-RL s1: 300 targets, 600000 samples, targets with a pattern proof 2, pattern hits 3 (rate 5.00e-06), within 256 attempts 0, targets solved at all 2
  - pre-RL natctl_s0: 300 targets, 600000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 0
  - pre-RL natctl_s1: 300 targets, 600000 samples, targets with a pattern proof 4, pattern hits 7 (rate 1.17e-05), within 256 attempts 0, targets solved at all 4
  - drift s1_r4: {'targets': 300, 'samples': 600000, 'solved': 28, 'pattern_hits': 5138, 'targets_with_pattern': 28, 'rate': 0.008563333333333333, 'frozen256_pattern_targets': 22}
- **ori_ore** (rule_sequence; 400 targets, 0 required):
  - ei_s0: solved 217, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [118, 162, 180, 194, 202, 213, 216, 217], transfer solved 94, held-out greedy 0.967
  - ei_s1: solved 219, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [145, 183, 193, 207, 213, 217, 219, 219], transfer solved 97, held-out greedy 0.969
  - frozen_s0: solved 148, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [118, 126, 131, 136, 137, 140, 144, 148], transfer solved 66, held-out greedy 0.961
  - frozen_s1: solved 173, pattern theorems 0 (0.000), pattern proofs 0, required solved / with pattern / violations 0 / 0 / 0, ignition round None, first pattern proof round None, per round [0, 0, 0, 0, 0, 0, 0, 0], solved per round [145, 157, 162, 165, 165, 168, 171, 173], transfer solved 79, held-out greedy 0.968
  - pre-RL s0: 300 targets, 600000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 125
  - pre-RL s1: 300 targets, 600000 samples, targets with a pattern proof 0, pattern hits 0 (rate 0.00e+00), within 256 attempts 0, targets solved at all 148
- Control arms (not pre-registered, added 22:12 UTC): `c8ctl` = the follow-up's cap-8 f = 0 (strict derived-ORE) Stage-1 models on the depth-4 pool (their data has 0 depth-4 proofs; held-out `heldout_c8`, retained slice the cap-8 set); `c8f0` = the addendum set above; `natctl` = the `struct` models (impi_ore at 130 / 155k, negi_ande_hyp at 11 / 155k) on the impi_ore / negi_ande_hyp pools.
- Pods: p1–p3 (RTX 3090, $0.50/h) from 19:12 / 19:20 / 20:05 to 01:12 UTC (shared with run 5 until 22:05): ≈ 15 h ≈ $7.5 (run-2 share ≈ $6). Bucket: `hf://buckets/dan-pandori/nd-rl/round2/run2/{artifacts/r2,data/r2,ckpts/r2}`.
- Step 3 (`data/r1/scale_prompts.jsonl`: 106 theorems in the Lean form with draw-0's 20 examples — depth3_f0 40 (targets of `targets_depth3` solved with a depth-3 proof by the campaign's f = 0 arm a1 s0, drawn from 335), reductio_f0 40 (run 5's required targets solved by f = 0 s0, from 51), transfer9 26 (all transfer theorems whose take-home RL proof was written in 9 lines); Qwen3-{0.6B, 1.7B, 4B, 8B, 14B, 32B} instruct (thinking off), k = 16 at T = 0.7, Lean-checked; `artifacts/r1/gens_scale_<model>.jsonl`, `scored_scale_<model>.jsonl`, `scale_summary.json`):
  - depth3_f0 (n 40): smallest size that proves the theorem — {'Qwen3-14B': 12, 'Qwen3-4B': 12, 'Qwen3-8B': 14, 'Qwen3-32B': 2}; median Qwen3-8B; fraction proved by each size 0.6B 0.00, 1.7B 0.00, 4B 0.30, 8B 0.65, 14B 0.93, 32B 1.00; Spearman(first size, RL round of first proof) = 0.23
  - reductio_f0 (n 40): smallest size that proves the theorem — {'Qwen3-8B': 19, 'Qwen3-14B': 10, 'Qwen3-32B': 6, 'Qwen3-4B': 4, 'none': 1}; median Qwen3-8B; fraction proved by each size 0.6B 0.00, 1.7B 0.00, 4B 0.10, 8B 0.53, 14B 0.65, 32B 0.85; Spearman(first size, RL round of first proof) = 0.03
  - transfer9 (n 26): smallest size that proves the theorem — {'Qwen3-8B': 10, 'Qwen3-14B': 6, 'Qwen3-4B': 8, 'none': 1, 'Qwen3-0.6B': 1}; median Qwen3-8B; fraction proved by each size 0.6B 0.04, 1.7B 0.00, 4B 0.35, 8B 0.69, 14B 0.96, 32B 0.96; Spearman(first size, Phase-1 base log p at T = 0.8) = -0.24 over 26 theorems (negative = harder for the base ⇒ larger first size); Spearman(first size, RL round of first proof) = 0.38
- Pods: p6 (A100 80 GB PCIe, $1.59/h, 250 GB container disk) 23:22 → 01:30 UTC ≈ 2.1 h ≈ $3.4 (+ model downloads: 30B-A3B 57 GB, Qwen3 0.6B–32B ≈ 90 GB). Bucket: `hf://buckets/dan-pandori/nd-rl/round2/run1/{artifacts/r1,data/r1}` (generations, scored rows, agreement files, prompts).

## Round 2 — Run 4: GRPO vs expert iteration at f = 0 (2026-09-17/18; `grpo.py`, `run4_analysis.py` → `artifacts/r4/summary.json`; arms `artifacts/r4/grpo_g{8,32}_{a1,a2,a3}_s{0,1}/round_<r>.json`, `found_<r>.jsonl`; round-8 checkpoints `ckpts/r4/`)
- Algorithm: on-policy GRPO, binary verifier reward, group-mean baseline (no std normalisation), fixed loss divisor 400, no KL, AdamW lr 10⁻⁴ (β 0.9 / 0.95, clip 1.0), one update per batch of P × G samples at T = 0.8; G = 8 with P = 64, G = 32 with P = 16 (512 samples per step, 500 steps = 256,000 samples = EI's 8 × 32 × 1,000). Bookkeeping at 8 round-equivalents like `expert_iter.py` (every distinct verified proof sampled during training; transfer pass@32 at the boundary, never trained on; greedy on transfer and held-out). No retained pretraining data. Depth-3 acquisition = targets with a normalised proof of box depth ≥ 3 (min-round rule) — the same statistic as the follow-up's EI arms on the same six Stage-1 draws.
- Bookkeeping notes: grpo_g8_a1_s0's round-8 files were not pulled before p5 was deleted (its round-8 checkpoint was) — its numbers are at round-equivalent 7 (224,000 samples); grpo_g8_a2_s1's round_1.json is from a killed duplicate run (log.md 01:01) and is excluded from the per-round table; grpo_g32_a2_s0 was re-run from scratch after p4 was deleted before its pull (log.md 01:14).
- grpo_g32_a1_s0 (G = 32, draw a1_s0): round-equivalent 8: solved 728 / 1,000, **depth-3 acquisition 440 (0.440)** vs EI 0.335 (645 solved); pattern proofs 722; per round-equivalent [176, 321, 368, 389, 402, 415, 432, 440]; solved per round-equivalent [418, 600, 646, 670, 680, 695, 718, 728]; mean reward per round-equivalent [0.25, 0.44, 0.52, 0.55, 0.57, 0.59, 0.61, 0.63]; fraction of groups with reward variance [0.4, 0.47, 0.4, 0.37, 0.28, 0.25, 0.23, 0.22]; held-out greedy at the end 0.564 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 315 / 500, with depth-3 183; written-length histogram {'7': 615, '8': 432, '9': 161, '10': 8}
- grpo_g32_a1_s1 (G = 32, draw a1_s1): round-equivalent 8: solved 798 / 1,000, **depth-3 acquisition 467 (0.467)** vs EI 0.364 (698 solved); pattern proofs 746; per round-equivalent [251, 350, 387, 423, 440, 451, 458, 467]; solved per round-equivalent [521, 650, 706, 749, 770, 783, 790, 798]; mean reward per round-equivalent [0.34, 0.5, 0.55, 0.6, 0.63, 0.67, 0.67, 0.7]; fraction of groups with reward variance [0.49, 0.48, 0.44, 0.37, 0.35, 0.33, 0.28, 0.28]; held-out greedy at the end 0.643 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 353 / 500, with depth-3 202; written-length histogram {'7': 644, '8': 453, '9': 218, '10': 16, '11': 2}
- grpo_g32_a2_s0 (G = 32, draw a2_s0): round-equivalent 8: solved 737 / 1,000, **depth-3 acquisition 437 (0.437)** vs EI 0.350 (589 solved); pattern proofs 668; per round-equivalent [283, 342, 364, 372, 395, 415, 424, 437]; solved per round-equivalent [506, 605, 651, 665, 687, 711, 724, 737]; mean reward per round-equivalent [0.31, 0.45, 0.51, 0.55, 0.58, 0.6, 0.6, 0.63]; fraction of groups with reward variance [0.49, 0.47, 0.41, 0.33, 0.32, 0.29, 0.31, 0.26]; held-out greedy at the end 0.657 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 323 / 500, with depth-3 190; written-length histogram {'7': 617, '8': 378, '9': 162, '10': 7, '11': 2}
- grpo_g32_a2_s1 (G = 32, draw a2_s1): round-equivalent 8: solved 725 / 1,000, **depth-3 acquisition 404 (0.404)** vs EI 0.341 (652 solved); pattern proofs 584; per round-equivalent [124, 309, 351, 366, 376, 389, 399, 404]; solved per round-equivalent [390, 611, 667, 689, 697, 709, 719, 725]; mean reward per round-equivalent [0.24, 0.46, 0.5, 0.55, 0.57, 0.61, 0.6, 0.63]; fraction of groups with reward variance [0.38, 0.45, 0.36, 0.28, 0.26, 0.21, 0.22, 0.21]; held-out greedy at the end 0.610 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 338 / 500, with depth-3 188; written-length histogram {'7': 666, '8': 378, '9': 89, '10': 1}
- grpo_g32_a3_s0 (G = 32, draw a3_s0): round-equivalent 8: solved 710 / 1,000, **depth-3 acquisition 411 (0.411)** vs EI 0.361 (605 solved); pattern proofs 601; per round-equivalent [252, 337, 377, 384, 394, 402, 409, 411]; solved per round-equivalent [442, 581, 633, 651, 674, 694, 705, 710]; mean reward per round-equivalent [0.25, 0.42, 0.5, 0.53, 0.55, 0.59, 0.6, 0.61]; fraction of groups with reward variance [0.44, 0.49, 0.37, 0.27, 0.26, 0.23, 0.22, 0.22]; held-out greedy at the end 0.376 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 302 / 500, with depth-3 174; written-length histogram {'7': 629, '8': 373, '9': 104}
- grpo_g32_a3_s1 (G = 32, draw a3_s1): round-equivalent 8: solved 691 / 1,000, **depth-3 acquisition 395 (0.395)** vs EI 0.352 (583 solved); pattern proofs 554; per round-equivalent [201, 317, 357, 371, 377, 383, 389, 395]; solved per round-equivalent [449, 598, 644, 660, 668, 676, 685, 691]; mean reward per round-equivalent [0.27, 0.44, 0.51, 0.56, 0.58, 0.59, 0.6, 0.61]; fraction of groups with reward variance [0.45, 0.51, 0.46, 0.35, 0.26, 0.26, 0.23, 0.2]; held-out greedy at the end 0.521 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 313 / 500, with depth-3 183; written-length histogram {'7': 614, '8': 340, '9': 85, '10': 1}
- grpo_g8_a1_s0 (G = 8, draw a1_s0): round-equivalent 7: solved 778 / 1,000, **depth-3 acquisition 478 (0.478)** vs EI 0.335 (645 solved); pattern proofs 779; per round-equivalent [344, 375, 405, 436, 458, 471, 478]; solved per round-equivalent [593, 660, 697, 733, 755, 770, 778]; mean reward per round-equivalent [0.37, 0.56, 0.63, 0.68, 0.7, 0.72, 0.74]; fraction of groups with reward variance [0.31, 0.23, 0.12, 0.11, 0.1, 0.09, 0.08]; held-out greedy at the end 0.562 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 338 / 500, with depth-3 200; written-length histogram {'7': 604, '8': 403, '9': 217, '10': 36, '11': 2}
- grpo_g8_a1_s1 (G = 8, draw a1_s1): round-equivalent 8: solved 819 / 1,000, **depth-3 acquisition 505 (0.505)** vs EI 0.364 (698 solved); pattern proofs 816; per round-equivalent [357, 414, 453, 469, 483, 490, 501, 505]; solved per round-equivalent [648, 733, 767, 784, 798, 805, 814, 819]; mean reward per round-equivalent [0.42, 0.61, 0.7, 0.72, 0.74, 0.76, 0.77, 0.79]; fraction of groups with reward variance [0.33, 0.25, 0.14, 0.12, 0.09, 0.08, 0.07, 0.05]; held-out greedy at the end 0.644 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 381 / 500, with depth-3 229; written-length histogram {'7': 633, '8': 452, '9': 263, '10': 38, '11': 4}
- grpo_g8_a2_s0 (G = 8, draw a2_s0): round-equivalent 8: solved 777 / 1,000, **depth-3 acquisition 473 (0.473)** vs EI 0.350 (589 solved); pattern proofs 730; per round-equivalent [373, 400, 419, 433, 445, 454, 463, 473]; solved per round-equivalent [598, 640, 698, 724, 741, 755, 764, 777]; mean reward per round-equivalent [0.4, 0.55, 0.62, 0.66, 0.69, 0.71, 0.72, 0.73]; fraction of groups with reward variance [0.35, 0.24, 0.14, 0.12, 0.08, 0.08, 0.07, 0.06]; held-out greedy at the end 0.672 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 347 / 500, with depth-3 210; written-length histogram {'7': 604, '8': 406, '9': 203, '10': 18, '11': 3}
- grpo_g8_a2_s1 (G = 8, draw a2_s1): round-equivalent 8: solved 799 / 1,000, **depth-3 acquisition 472 (0.472)** vs EI 0.341 (652 solved); pattern proofs 790; per round-equivalent [329, 388, 402, 408, 433, 444, 467, 472]; solved per round-equivalent [605, 677, 710, 722, 751, 771, 793, 799]; mean reward per round-equivalent [0.38, 0.58, 0.64, 0.67, 0.69, 0.72, 0.74, 0.76]; fraction of groups with reward variance [0.31, 0.14, 0.12, 0.08, 0.1, 0.08, 0.09, 0.07]; held-out greedy at the end 0.621 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 351 / 500, with depth-3 207; written-length histogram {'7': 658, '8': 464, '9': 225, '10': 34}
- grpo_g8_a3_s0 (G = 8, draw a3_s0): round-equivalent 8: solved 747 / 1,000, **depth-3 acquisition 447 (0.447)** vs EI 0.361 (605 solved); pattern proofs 667; per round-equivalent [350, 381, 407, 421, 428, 435, 442, 447]; solved per round-equivalent [580, 647, 684, 705, 713, 726, 738, 747]; mean reward per round-equivalent [0.32, 0.53, 0.6, 0.65, 0.67, 0.68, 0.69, 0.71]; fraction of groups with reward variance [0.35, 0.23, 0.12, 0.08, 0.08, 0.08, 0.08, 0.07]; held-out greedy at the end 0.340 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 332 / 500, with depth-3 197; written-length histogram {'7': 628, '8': 365, '9': 151, '10': 10}
- grpo_g8_a3_s1 (G = 8, draw a3_s1): round-equivalent 8: solved 780 / 1,000, **depth-3 acquisition 472 (0.472)** vs EI 0.352 (583 solved); pattern proofs 749; per round-equivalent [325, 369, 395, 418, 433, 448, 465, 472]; solved per round-equivalent [572, 651, 678, 710, 731, 748, 768, 780]; mean reward per round-equivalent [0.35, 0.55, 0.61, 0.64, 0.67, 0.68, 0.71, 0.72]; fraction of groups with reward variance [0.33, 0.22, 0.12, 0.12, 0.1, 0.1, 0.09, 0.09]; held-out greedy at the end 0.531 (Stage-1 ≈ 0.87–0.95); transfer pass@32 at the end 330 / 500, with depth-3 192; written-length histogram {'7': 621, '8': 431, '9': 238, '10': 24}
- EI reference ei_depth3_f0_a1_s0: solved 645, acquisition 0.335, per round [2, 8, 117, 259, 299, 317, 327, 335], held-out greedy 0.907
- EI reference ei_depth3_f0_a1_s1: solved 698, acquisition 0.364, per round [4, 41, 175, 279, 311, 340, 354, 364], held-out greedy 0.930
- EI reference ei_depth3_f0_a2_s0: solved 589, acquisition 0.350, per round [3, 75, 199, 291, 308, 327, 341, 350], held-out greedy 0.945
- EI reference ei_depth3_f0_a2_s1: solved 652, acquisition 0.341, per round [0, 0, 8, 78, 242, 298, 317, 341], held-out greedy 0.903
- EI reference ei_depth3_f0_a3_s0: solved 605, acquisition 0.361, per round [1, 31, 185, 280, 319, 335, 348, 361], held-out greedy 0.945
- EI reference ei_depth3_f0_a3_s1: solved 583, acquisition 0.352, per round [7, 92, 227, 319, 338, 345, 346, 352], held-out greedy 0.919
- Summary: G = 8 acquisition mean 0.474 (range 0.447–0.505, n = 6), G = 32 mean 0.426 (0.395–0.467); EI mean 0.351 (0.335–0.364). Held-out greedy at the end: G = 8 [0.34, 0.53, 0.56, 0.62, 0.64, 0.67], G = 32 [0.38, 0.52, 0.56, 0.61, 0.64, 0.66].
- The 85M / relative-codec arm of the proposal was not run (no access to that code). Pods: p4 / p5 (RTX 3090) from 23:09 to 01:36 UTC ≈ 2 × 2.4 h ≈ $2.4 (shared with run 3). Bucket: `hf://buckets/dan-pandori/nd-rl/round2/run4/{artifacts/r4,ckpts/r4}`.

## Round 3 — Run 4a: reductio on the required pool vs model size (2026-09-18/19; `r3_4a_pool.py`, `make_coverage_sets.py assemble`, `r3_4a_indep.py`, `run4a_analysis.py` → `artifacts/r3_4a/summary.json`, `r3_4a_heldout_split.py` → `artifacts/r3_4a/heldout_split.json`, tables below printed by `run4a_tables.py`; job scripts `pod/r3_4a/`)

Sources. Stage-1: `artifacts/r3_4a/train_<draw>.log`, `heldout_greedy_<draw>.json` (+ `.jsonl`, bucket only). Pre-RL sample: `artifacts/r3_4a/cov_<draw>_pre.s0.jsonl` (300 targets × 2,000, T = 0.8, seed 0). EI / frozen: `artifacts/r3_4a/{ei,frozen}_<draw>/round_<r>.json`, `found_<r>.jsonl`, `found_transfer_<r>.jsonl`, `args.json`. Base pass@10⁴ on the EI-acquired targets: `data/r3_4a/acq_<draw>.jsonl` → `artifacts/r3_4a/cov_<draw>_b10k.s0.jsonl` (seed 1, fresh samples). 3.2M original-set row: `artifacts/r5/` (run 5, reviewed). Draw names: `m3` = 3.2M (4 × 256), `m25` = 25M (8 × 512), `m85` = 85M (12 × 768); suffix `B` = retry configuration (lr 1e-4, 12,000 steps), none = configuration A (lr 3e-4, 6,000 steps; `m3`: campaign command, lr 1e-3); `_s<seed>`.

- **Set (deviation).** `data/r3_4a/train_reductio_f0_b1.jsonl` (md5 333d1323…, bucket `round3-run4a/data/r3_4a/`): 155,000 = 31,000 × lengths 2–6, reductio **0** (pruned and written form; independent string-level recount `artifacts/r3_4a/indep_check_b1.log`: strict 0, DN-after-NEGI 0), derived-ORE 88, depth-3 5,687 (`data/r3_4a/assemble_report_b1.json`); source pool 466,088 classes from 775,000 records of five generator sets (`data/r3_4a/pool_cap6_r4a_report.json`); class overlap with targets / transfer / held-out / `targets_reductio_req6` / val-36: 0 / 0 / 0 / 0 / 0. The original `train_reductio_f0.jsonl` was unreachable (log.md 17:50).
- **Parameters** (printed by `train.py`): 3,210,240 / 25,321,472 / 85,208,064.
- **Quality gate.** Held-out greedy (5,000): 3.2M 0.867–0.877; 25M A 0.8926 / 0.8972 / 0.9078, B 0.9104 / 0.8972 / 0.9104; 85M A 0.8988 / 0.9134 / 0.8940 (+ extras), B 0.9160 / 0.9152 / 0.9148. The brief's 0.93 at 85M is not reachable by an f = 0 reductio model: 679 of the 5,000 held-out theorems are reductio-labelled and f = 0 models solve 178–308 of them; on the 4,321 others every 25M / 85M draw is at 0.982–0.988 (3.2M 0.957–0.971). Retry rule (fixed 19:02 UTC before the retries existed): B replaces A if seed-0 held-out greedy improves by > 0.01 → fired at both sizes (+0.0178, +0.0172), entirely on reductio-labelled theorems and inside the A seeds' own spread. Both configurations were run in full (3 draws each) and are reported as separate cells; B is the headline configuration by the rule, 85M is "gate missed (structural)".

### Per draw

| draw | params | Stage-1 steps / val | held-out greedy (all / non-reductio) | pre-RL strict hits / 600k (rate) | targets hit (7/8/9/10) | pass@256 targets | EI acquired (7/8/9/10) | per round | ignition round | trained rounds | frozen | transfer acq. (of 150) | solved w/o pattern (EI/frozen/cov) | base-reachable@1e4 of acquired | EI-only fraction |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| m3_s0 | 3210240 | 6000 / 0.0825 | 0.8668 / 0.9572 | 0 / 600,000 (0.0e+00) | 0 (0/0/0/0) | 0 | 0 (0/0/0/0) | 0 0 0 0 0 0 0 0 | – | 0 | 0 | 0 (0/0/0/0) | 0/0/0 | – | – |
| m3_s1 | 3210240 | 6000 / 0.0827 | 0.8770 / 0.9713 | 14 / 600,000 (2.3e-05) | 3 (3/0/0/0) | 1 | 32 (32/0/0/0) | 0 1 3 7 8 11 21 32 | 4 | 7 | 2 | 18 (18/0/0/0) | 0/0/0 | 5 / 32 | 27 / 32 = 0.84 |
| m3_s2 | 3210240 | 6000 / 0.0825 | 0.8712 / 0.9669 | 0 / 600,000 (0.0e+00) | 0 (0/0/0/0) | 0 | 0 (0/0/0/0) | 0 0 0 0 0 0 0 0 | – | 0 | 0 | 0 (0/0/0/0) | 0/0/0 | – | – |
| m25_s0 | 25321472 | 6000 / 0.0820 | 0.8926 / 0.9824 | 1872 / 600,000 (3.1e-03) | 11 (11/0/0/0) | 8 | 45 (44/1/0/0) | 4 13 32 38 40 45 45 45 | 2 | 8 | 7 | 21 (21/0/0/0) | 0/0/0 | 15 / 45 | 30 / 45 = 0.67 |
| m25_s1 | 25321472 | 6000 / 0.0829 | 0.8972 / 0.9861 | 830 / 600,000 (1.4e-03) | 10 (10/0/0/0) | 5 | 52 (52/0/0/0) | 4 20 37 49 52 52 52 52 | 2 | 8 | 7 | 25 (25/0/0/0) | 0/0/0 | 11 / 52 | 41 / 52 = 0.79 |
| m25_s2 | 25321472 | 6000 / 0.0822 | 0.9078 / 0.9877 | 14 / 600,000 (2.3e-05) | 3 (3/0/0/0) | 2 | 40 (39/1/0/0) | 0 1 15 29 36 38 39 40 | 3 | 7 | 1 | 23 (23/0/0/0) | 0/0/0 | 6 / 40 | 34 / 40 = 0.85 |
| m25B_s0 | 25321472 | 12000 / 0.0820 | 0.9104 / 0.9847 | 3 / 600,000 (5.0e-06) | 2 (2/0/0/0) | 0 | 0 (0/0/0/0) | 0 0 0 0 0 0 0 0 | – | 0 | 0 | 1 (1/0/0/0) | 0/0/0 | – | – |
| m25B_s1 | 25321472 | 12000 / 0.0820 | 0.8972 / 0.9801 | 0 / 600,000 (0.0e+00) | 0 (0/0/0/0) | 0 | 0 (0/0/0/0) | 0 0 0 0 0 0 0 0 | – | 0 | 0 | 0 (0/0/0/0) | 0/0/0 | – | – |
| m25B_s2 | 25321472 | 12000 / 0.0820 | 0.9104 / 0.9882 | 131 / 600,000 (2.2e-04) | 5 (5/0/0/0) | 3 | 48 (48/0/0/0) | 0 1 9 31 39 43 44 48 | 3 | 7 | 2 | 20 (20/0/0/0) | 0/0/0 | 10 / 48 | 38 / 48 = 0.79 |
| m85_s0 | 85208064 | 6000 / 0.0820 | 0.8988 / 0.9875 | 37 / 600,000 (6.2e-05) | 3 (3/0/0/0) | 2 | 53 (52/1/0/0) | 1 6 30 39 42 53 53 53 | 2 | 8 | 2 | 27 (27/0/0/0) | 0/0/0 | 4 / 53 | 49 / 53 = 0.92 |
| m85_s1 | 85208064 | 6000 / 0.0824 | 0.9134 / 0.9857 | 49 / 600,000 (8.2e-05) | 2 (2/0/0/0) | 2 | 52 (52/0/0/0) | 1 11 28 33 42 46 51 52 | 2 | 8 | 2 | 27 (27/0/0/0) | 0/0/0 | 5 / 52 | 47 / 52 = 0.90 |
| m85_s2 | 85208064 | 6000 / 0.0823 | 0.8940 / 0.9850 | 6 / 600,000 (1.0e-05) | 3 (3/0/0/0) | 0 | 0 (0/0/0/0) | 0 0 0 0 0 0 0 0 | – | 0 | 0 | 0 (0/0/0/0) | 0/0/0 | – | – |
| m85_s3 | 85208064 | 6000 / 0.0820 | 0.8962 / 0.9829 | 13 / 600,000 (2.2e-05) | 2 (2/0/0/0) | 1 | – | – | – | – | – | – | –/–/0 | – | – |
| m85_s4 | 85208064 | 6000 / 0.0822 | 0.9008 / 0.9826 | 2 / 600,000 (3.3e-06) | 1 (1/0/0/0) | 0 | – | – | – | – | – | – | –/–/0 | – | – |
| m85_s5 | 85208064 | 6000 / 0.0822 | 0.8956 / 0.9852 | 60 / 600,000 (1.0e-04) | 7 (7/0/0/0) | 5 | – | – | – | – | – | – | –/–/0 | – | – |
| m85_s6 | 85208064 | 6000 / 0.0824 | 0.9022 / 0.9831 | 8 / 600,000 (1.3e-05) | 5 (5/0/0/0) | 3 | – | – | – | – | – | – | –/–/0 | – | – |
| m85B_s0 | 85208064 | 12000 / 0.0820 | 0.9160 / 0.9919 | 0 / 600,000 (0.0e+00) | 0 (0/0/0/0) | 0 | 0 (0/0/0/0) | 0 0 0 0 0 0 0 0 | – | 0 | 0 | 0 (0/0/0/0) | 0/0/0 | – | – |
| m85B_s1 | 85208064 | 12000 / 0.0821 | 0.9152 / 0.9903 | 4 / 600,000 (6.7e-06) | 3 (3/0/0/0) | 0 | 0 (0/0/0/0) | 0 0 0 0 0 0 0 0 | – | 0 | 0 | 1 (1/0/0/0) | 0/0/0 | – | – |
| m85B_s2 | 85208064 | 12000 / 0.0821 | 0.9148 / 0.9877 | 1548 / 600,000 (2.6e-03) | 12 (12/0/0/0) | 6 | 52 (52/0/0/0) | 4 16 30 50 52 52 52 52 | 2 | 8 | 7 | 26 (26/0/0/0) | 0/0/0 | 13 / 52 | 39 / 52 = 0.75 |
| r5_s0 | – | run 5 | – | 113 / 3,000,000 (3.8e-05) | 6 (6/0/0/0) | 1 | 51 (51/0/0/0) | 2 11 25 47 51 51 51 51 | 2 | 8 | 4 | 25 (25/0/0/0) | 0/0/0 | 6 / 51 | 45 / 51 = 0.88 |
| r5_s1 | – | run 5 | – | 0 / 3,000,000 (0.0e+00) | 0 (0/0/0/0) | 0 | 0 (0/0/0/0) | 0 0 0 0 0 0 0 0 | – | 0 | 0 | 0 (0/0/0/0) | 0/0/0 | – | – |
| r5_s2 | – | run 5 | – | 1 / 3,000,000 (3.3e-07) | 1 (1/0/0/0) | 0 | 0 (0/0/0/0) | 0 0 0 0 0 0 0 0 | – | 0 | 0 | 0 (0/0/0/0) | 0/0/0 | – | – |

### Per cell (non-zero = ≥ 1 target with a strict-reductio sample among its first 2,000; the run-5 row is read from its 10⁴-per-target files with the same first-2,000 rule)

| cell | draws sampled | non-zero draws (≥ 1 strict hit in 600k) | rates of non-zero draws | igniting (EI ≥ 6 targets by round 8) | EI-only fractions |
|---|---|---|---|---|---|
| 3.2M same-set | 3 | 1 | 2.3e-05 | 1 | 0.84 |
| 25M config A | 3 | 3 | 3.1e-03, 1.4e-03, 2.3e-05 | 3 | 0.67, 0.79, 0.85 |
| 25M config B | 3 | 2 | 5.0e-06, 2.2e-04 | 1 | 0.79 |
| 85M config A | 3 | 3 | 6.2e-05, 8.2e-05, 1.0e-05 | 2 | 0.92, 0.90 |
| 85M config A EXTRA draws (exploratory, coverage only) | 4 | 4 | 2.2e-05, 3.3e-06, 1.0e-04, 1.3e-05 | – (no EI run) | – |
| 85M config B | 3 | 2 | 6.7e-06, 2.6e-03 | 1 | 0.75 |
| 3.2M original set (run 5) | 3 | 1 | 3.8e-05 | 1 | 0.88 |

- **Non-zero draws** (source: `cov_<draw>_pre.s0.jsonl`, `hits_by_pattern.reductio`): 3.2M same-set **1 / 3**; 25M **5 / 6** (A 3 / 3, B 2 / 3); 85M **9 / 10** (A 3 / 3 + 4 / 4 exploratory extra draws, B 2 / 3). Zero-rate draws (0 strict hits in 600,000): `m3_s0`, `m3_s2`, `m25B_s1`, `m85B_s0`. Every pre-RL hit at every size is on a 7-line target (`nand_neg` / `negimp_to_pos`); 0 hits on the 248 targets at 8–10 lines in 11.4M pre-RL samples (19 draws).
- **Zero-rate and low-rate draws under EI:** all four zero-rate draws: EI 0 / 300, frozen 0 / 300, 0 trained rounds. Three non-zero draws with rates ≤ 1.0·10⁻⁵ (`m25B_s0` 3 hits, `m85_s2` 6, `m85B_s1` 4) also end at 0 / 300 with 0 trained rounds (expected hits in 76,800 attempts: 0.4–0.8). Exploratory: `m85_s2` continued to round 16 (`x_ei_m85_s2_r9-16`): 0 through round 12, then 1 / 13 / 29 / 49 (49 seven-line, 0 longer).
- **Igniting draws (all 8 draws with rate ≥ 2.3·10⁻⁵):** ignition round 2–4; acquired 32–53; strata 7 / 8 / 9 / 10: at most **1 eight-line target** (`chain_neg`; `m25_s0`, `m25_s2`, `m85_s0`) and 0 at 9–10 lines in every arm; transfer 18–27 of the 27 seven-line theorems, 0 of 123 longer. Frozen twins 1–7 targets, all 7-line. Solved-without-pattern: 0 in all 30 pre-registered arms, the 2 exploratory arms and all 27 coverage files.
- **EI-only fraction** (acquired targets with no verified proof in 10⁴ fresh base samples ÷ acquired; `cov_<draw>_b10k.s0.jsonl`): 3.2M same-set 27 / 32 = **0.84** (run 5, original set: 45 / 51 = 0.88); 25M A 30 / 45 = 0.67, 41 / 52 = 0.79, 34 / 40 = 0.85; 25M B 38 / 48 = 0.79; 85M A 49 / 53 = **0.92**, 47 / 52 = **0.90**; 85M B 39 / 52 = 0.75. By base rate rather than size: the three draws with rate > 10⁻³ give 0.67 / 0.79 / 0.75, the five with rate ≤ 2.2·10⁻⁴ give 0.79–0.92.
- **Exploratory ft-lr check** (`x_ei_m85_s0_lr3e-5`, brief's suggested 3e-5 on `m85_s0`): 1 / 9 / 28 / 33 / 40 / 46 / 49 / 51 (50 seven-line + 1 eight-line) vs 1 / 6 / 30 / 39 / 42 / 53 / 53 / 53 at the 1e-4 used everywhere else at 25M / 85M.
- **EI settings actually used:** k = 32, 8 rounds, T = 0.8, retain 20,000, max 4 proofs per theorem × weight 4, `--ft_steps 600`, sampling batch 1024, `--ft_lr` 3e-4 (3.2M) / 1e-4 (25M, 85M); seed = Stage-1 seed (`args.json` per arm).
- **Pods and cost** (`~/pods.log`, deletion times in log.md): six A100-SXM4-80GB at $1.59/h — r4a-1 17:57–21:51, r4a-2 18:07–22:31, r4a-3 19:11–00:18, r4a-4 20:09–22:30, r4a-5 20:56–22:31, r4a-6 20:57–00:53 UTC = 21.3 pod-hours ≈ **$33.8** (pre-registered plan incl. the rule-mandated B cells ≈ $27; exploratory extras ≈ $6.7). Not re-derivable from repo files: pod spend.
- **Bucket:** `hf://buckets/dan-pandori/nd-rl/round3-run4a/{artifacts/r3_4a,ckpts/r3_4a,data/r3_4a}` — `ckpts/r3_4a/`: 19 Stage-1 checkpoints (`stage1_reductio_f0_b1_<draw>.pt`) and the round-8 checkpoint of every arm that trained; `data/r3_4a/`: the rebuilt set, its reports, `acq_<draw>.jsonl`; `artifacts/r3_4a/`: everything above plus the per-theorem held-out greedy files (gitignored). The per-round training mixes (`mix_<r>.jsonl`) were not pulled; their RL part is `found_<r>.jsonl` capped at 4 proofs per theorem × weight 4, the rest a seeded 20,000-record sample of the set.
