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

# lean-format (proposal 8) — Lean as the training format for the from-scratch model

Every number below is re-derived by `python3 lean_format_analysis.py` → `artifacts/lf/summary.json` (stdout copy `artifacts/lf/analysis_stdout.txt`) from pulled files under `artifacts/lf/`; token comparators from `artifacts/p2/{ei,frozen}_depth3_f0_a1_s{0,1}/`, `artifacts/stage1_*_transfer2_k16_norm.json` and `ladder.md` (branch `dan_ladder_a`). A Lean-format sample counts iff Lean accepts the literal sampled text **and** `nd_verify` accepts the ND proof it denotes; counts are distinct denoted proofs (numbered from N1). Formats: `lean_rand` (random labels, pre-registered primary), `lean_seq` (first-appearance order + random offset). Model 4 layers, d 256 in all arms; parameters differ only by vocabulary rows (107 vs 99).

## Sequence lengths (`artifacts/lf/seqlen.json`; one symbol per token)
| file | n | token `abs` prompt / proof / total mean (p95, max) | Lean prompt / proof / total mean (p95, max) | ratio total |
|---|---:|---|---|---:|
| `data/train.jsonl` | 154,990 | 36.9 / 72.1 / 109.1 (187, 516) | 51.8 / 82.8 / 134.5 (214, 537) | 1.233 |
| `data/p2/train_depth3_f0_a1.jsonl` | 155,000 | 39.1 / 73.6 / 112.6 (185, 444) | 54.2 / 84.3 / 138.4 (214, 464) | 1.229 |
| `data/heldout.jsonl` | 5,000 | 37.0 / 72.6 / 109.6 (191, 440) | 51.8 / 83.2 / 135.1 (215, 461) | 1.232 |
| `data/p2/heldout.jsonl` | 5,000 | 39.7 / 81.3 / 121.0 (212, 465) | 54.1 / 92.2 / 146.3 (238, 486) | 1.210 |

## P1 — Stage-1 held-out greedy (band: within 2 pp of token)
| Stage-1 set | token | `lean_seq` | `lean_rand` | source |
|---|---|---|---|---|
| a1 (depth-3 removed), seeds 0 / 1, `data/p2/heldout.jsonl` | 0.883 / 0.883 | **0.909 / 0.896** (in band) | **0.882 / 0.790** (s1 out of band, −9.3 pp) | `artifacts/lf/frozen_d3_<sch>_s<k>/round_1.json`; `artifacts/p2/ei_depth3_f0_a1_s<k>/round_1.json` |
| full cap-6 set, `data/heldout.jsonl` | 0.948 | **0.936** (−1.2 pp, in band) | **0.830** (−11.8 pp) | `artifacts/lf/stage1_full_<sch>_heldout_greedy.json` |
| full set, by proof length 2 / 3 / 4 / 5 / 6 | – | 1.000 / 0.988 / 0.950 / 0.888 / 0.852 | 0.999 / 0.979 / 0.864 / 0.645 / 0.662 | same |
- `lean_rand` failures are mostly wrong-name citations: of 851 failures on the full set, 813 parse and are rejected by both checkers (`nd_verify` reasons on the denoted proof: rule check ANDI 209, NEGE 174, IMPE 170, ORI 108, R 54, ANDE1 35, …), 38 are outside the grammar (36 `unbound`); `artifacts/lf/stage1_full_rand_heldout_greedy.jsonl`, log.md 03:17. `lean_seq --no_shift` full set: 0.939.

## P2 — depth-3 f = 0 dial, set a1, 8 rounds × 32 attempts (`phase2_metrics.arm_metrics`, pattern `depth3`, on `artifacts/lf/{ei,frozen}_d3_<sch>_s<k>/`)
| arm | targets solved / 1,000 | **acquisition** (theorems / depth-3 proofs / first round) | transfer solved / 500, acq | held-out greedy final |
|---|---|---|---|---|
| token EI s0 / s1 | 645 / 698 | **0.335 / 0.364** (335 / 409 / r1; 364 / 426 / r1) | 331, 0.372 / 337, 0.366 | 0.907 / 0.930 |
| token frozen s0 / s1 | 175 / 175 | 0.005 / 0.005 | 84, 0.004 / 93, 0.004 | 0.883 / 0.883 |
| `lean_seq` EI s0 / s1 | 715 / 736 | **0.476 / 0.479** (476 / 661 / r1; 479 / 710 / r1) | 369, 0.494 / 388, 0.512 | 0.965 / 0.969 |
| `lean_seq` frozen s0 / s1 | 409 / 326 | **0.206 / 0.134** (206 / 232; 134 / 168) | 206, 0.184 / 184, 0.156 | 0.909 / 0.896 |
| `lean_rand` EI s0 / s1 | 663 / 673 | **0.433 / 0.462** (433 / 619 / r1; 462 / 657 / r1) | 347, 0.472 / 344, 0.476 | 0.925 / 0.913 |
| `lean_rand` frozen s0 / s1 | 351 / 423 | **0.202 / 0.280** (202 / 241; 280 / 336) | 173, 0.198 / 233, 0.302 | 0.882 / 0.790 |
- Acquisition by round, `lean_seq` s0: 0.104 / 0.362 / 0.401 / 0.418 / 0.439 / 0.456 / 0.465 / 0.476; token s0: 0.002 / 0.008 / 0.117 / 0.259 / 0.299 / 0.317 / 0.327 / 0.335.
- **Base reachability**: the frozen Lean Stage-1 models (zero depth-3 proofs in pretraining) already solve 8.5–17.2 % of the targets with a depth-3 proof in the first 32 attempts and 13.4–28.0 % in 256; the token frozen controls: 0.5 % in 256. EI adds +0.27 / +0.35 (`lean_seq`) and +0.23 / +0.18 (`lean_rand`) over the frozen control at equal attempts (token: +0.33 / +0.36).

## P3 — ladder rung T1, 8 rounds × 32 attempts (`artifacts/lf/la_{T1,frozen}_<sch>_s<k>/found_transfer_8.jsonl`, `found_8.jsonl`; pools `data/ladder/`; `L*` = max L with ≥ 5 theorems solved at `L_true` ≥ L)
| arm | **`L*` transfer** | `L*` targets | transfer solved / 2,285 | by `L_true` 7 / 8 / 9 / 10 / 11 / 12 / 13 | targets solved / 4,495 | held-out greedy r1 → r8 | arm minutes (4 arms per GPU) |
|---|---:|---:|---:|---|---:|---|---:|
| token T1 s0 / s1 (on file) | 10 / 10 | 10 / 10 | 612 / 623 | 140, 137, 300, 34, 1, 0, 0 / 139, 138, 312, 34, 0, 0, 0 | 2,400 / 2,455 | 0.948 → 0.953 / 0.957 | 65 / 86 (2–3 per GPU) |
| token frozen s0 / s1 (on file) | 7 / 7 | 8 / 8 | 22 / 24 | 20, 2, 0 … / 21, 3, 0 … | 426 / 408 | 0.948 | – |
| `lean_seq` T1 s0 / s1 | **11 / 11** | 11 / 11 | **794 / 839** | 75, 161, 463, 83, 9, 3, 0 / 118, 162, 465, 81, 9, 3, 1 | 2,604 / 2,674 | 0.936 → 0.944 / 0.943 | 248 / 252 |
| `lean_seq` frozen s0 / s1 | **10 / 10** | 10 / 10 | 304 / 309 | 43, 113, 134, 14, 0 / 50, 111, 134, 14, 0 | 1,768 / 1,759 | 0.936 | 247 / 251 |
| `lean_rand` T1 s0 / s1 | **10 / 10** | 10 / 10 | 583 / 657 | 55, 131, 351, 44, 2 / 114, 139, 360, 40, 4 | 2,339 / 2,396 | 0.830 → 0.923 / 0.924 | 226 / 229 |
| `lean_rand` frozen s0 / s1 | **9 / 9** | 9 / 9 | 229 / 222 | 42, 89, 96, 2 / 41, 87, 93, 1 | 1,511 / 1,501 | 0.830 | 222 / 226 |
- `lean_seq` reaches transfer `L*` = 11 at round 5 in both seeds (`round_<r>.json` `transfer_cum.lstar`). Theorems solved at `L_true` ≥ 11: 12 / 13 (token 1 / 0); ≥ 12: 3 / 4. No pool label is contradicted by a shorter accepted proof (shortest written proof of the `L_true` ≥ 11 theorems: 11–13 lines), so `L*` is unchanged after relabelling.
- Unexplained and against the trend: the `L_true` = 7 bin is solved *less* often by Lean T1 arms (55–118 of 300) than by the token arms (139–140).

## P4 — mechanism test: Stage-1 base model on the full cap-6 set, pass@16 on `data/transfer.jsonl` (1,638; `artifacts/lf/stage1_full_<tag>_transfer2_k16.jsonl`)
| model | pass@16 | distinct verified proofs of written length 6 / 7 / 8 / ≥ 9 |
|---|---|---|
| token `abs` / `rel` / `abs-fixed` (on file) | 0.447 / 0.405 / 0.385 | 363 / 108 / 1 / 0 ; 332 / 79 / 0 / 0 ; 359 / 0 / 0 / 0 |
| `lean_seq` | **0.571** (935) | 333 / **266 / 130 / 18** |
| `lean_rand` | **0.524** (859) | 263 / **228 / 86 / 7** |
| `lean_seq --no_shift` (names n1… only) | 0.284 (466) | 229 / 37 / 0 / 0 |

## P5 — Lean vs `nd_verify` (`artifacts/lf/gate_*.jsonl`, `gate_*.disagree.jsonl`, `artifacts/lf/disagreement_kinds.json`, `artifacts/lf/record_*.json`)
- In the loop, every distinct grammar-valid sample of every job: 18,424,794 samples, 3,515,138 outside the strict grammar (19.1 %; `lean_rand` 20.7 %, `lean_seq` 17.4 %; mostly `unbound` = a name not in scope), **13,887,708 distinct checked by both: both accept 4,046,345, both reject 9,840,903, `nd_verify` accepts ∧ Lean rejects 0, Lean accepts ∧ `nd_verify` rejects 460** (33 per million; pre-registered expectation ≤ 10 per million: wrong).
- The 460, by cause: 206 `na.elim` on a non-`False` hypothesis (Lean resolves it to `Not.elim`; `nd2lean.py`'s BOTE rendering is looser than BOTE); 137 `¬A` ≡ `A → False` unfolding (NEGE 67, ORI 37, IMPI 30, ANDE / ANDI 3); 117 proofs that restate only some premises (legal Lean; ND requires every PR line — a gap in `lean_tok.inverse`'s strictness, not in Lean). None is counted anywhere.
- Checker of record (unmodified `nd2lean.py --check` + `nd_verify` on every counted proof, `found_8` and `found_transfer_8` of all 16 Lean arms): **41,840 / 41,840 both accept, 0 disagreements**.

## P6 — throughput and round time
- Lean 85.5 proofs per process-second in the loop (162,341 process-s for 13.89 M; 12 processes wide, 14,216 s wall over all jobs) vs `nd_verify` 14,497 per second on the same proofs: **≈ 170× slower per core**. Pod self-test on valid short proofs: 120–285 / s / core vs ≈ 20,000 / s.
- Solo like-for-like frozen round on the same pod, nothing else on the GPU (`artifacts/lf/timing_*/round_1.json`): depth-3 dial token 59 s / 64 s, `lean_rand` 105 s (**1.8×**), `lean_seq` 141 s (**2.2×**); ladder token 406 s / 402 s, `lean_rand` 594 s (**1.46×**), `lean_seq` 657 s (**1.64×**). Below the 3× stop rule. With four arms per 3090 a ladder round took 27–36 min.
- Cost: RunPod balance 127.78 → 121.56 (`rpbalance` at 03:03 and 08:04 UTC): **≈ $6.2** for ≈ 12.3 pod-hours on four RTX 3090 pods (`~/pods.log` lf-1 … lf-4, 03:04–08:03 UTC). Budget $30.

## Bucket
`hf://buckets/dan-pandori/nd-rl/lean-format/{ckpts,artifacts,data}` — `ckpts/lf` (Stage-1 models, depth-3 EI rounds), `ckpts/ladder` (ladder EI rounds), `artifacts/lf` (everything above incl. per-round found files), `data` (the a1 training set and the ladder pools used).


# ds-generator (proposal 9, run 2) — the generator's proof-shape distribution

**Every model here is a 3.3 M-parameter from-scratch GPT in the `lean_seq` Lean surface format**, Stage-1 =
`train.py --mode lean_seq --steps 6000 --bs 128 --cap 6 --seed <s>` on a 155,000-record set of **cap-6 generator
proofs, flat 31,000 per pruned length 2–6, depth-3 excluded**. The three sets differ only in the generator knobs
(`data/dsg/README.md`):

| arm | training set | Stage-1 checkpoints | generator |
|---|---|---|---|
| C0 | `data/p2/train_depth3_f0_a1.jsonl` | `ckpts/lf/stage1_a1_seq_s{0,1}.pt` (md5 `9bde44c0…`, `fc27e52d…`; trained 2026-09-21 on an RTX 3090, **not** retrained) | control knobs |
| G1 | `data/dsg/train_g1.jsonl` | `ckpts/dsg/stage1_g1_s{0,1}.pt` (retrained 2026-09-23/24 on A6000 / 4090) | `--ore_steps 3 --ore_boxes` |
| G2 | `data/dsg/train_g2.jsonl` | `ckpts/dsg/stage1_g2_s{0,1}.pt` (retrained 2026-09-23/24 on A6000 / 4090) | `--ladder --drop_contra --ore_boxes` (the ladder pools' strict long generator at cap 6) |

Sampler for every ladder number: this branch's decode path with the memoised RoPE table from run `efficiency`,
`ND_SAMPLE_COMPACT=0`, **batch 512, `--max_new` 512, T 0.8**, held fixed across all three arms and both seeds.
A proof counts only if `nd_verify` **and** Lean accept it. Source files are named per table; all are under
`artifacts/dsg/` unless said, and `dsg_analysis.py` regenerates every table below into `artifacts/dsg/summary.json`.

## G1 — held-out greedy (`heldout2_<arm>_s<k>.json`, `eval_set.py --k 1 --temperature 0 --batch 512`, `data/p2/heldout.jsonl`, 5,000)

| arm s | overall | 2 | 3 | 4 | 5 | 6 | none | pattern | depth-3 thms | 6-line none |
|---|---|---|---|---|---|---|---|---|---|---|
| c0 s0 | 0.909 | 0.994 | 0.989 | 0.951 | 0.924 | 0.686 | 0.952 | 0.770 | 0.488 | 0.818 |
| c0 s1 | 0.897 | 0.997 | 0.992 | 0.967 | 0.944 | 0.584 | 0.964 | 0.680 | 0.272 | 0.834 |
| g1 s0 | 0.861 | 0.998 | 0.984 | 0.947 | 0.923 | 0.451 | 0.951 | 0.569 | 0.014 | 0.830 |
| g1 s1 | 0.896 | 0.992 | 0.975 | 0.915 | 0.878 | 0.718 | 0.921 | 0.813 | 0.616 | 0.729 |
| g2 s0 | 0.608 | 0.996 | 0.963 | 0.525 | 0.417 | 0.138 | 0.737 | 0.193 | 0.076 | 0.332 |
| g2 s1 | 0.665 | 0.997 | 0.970 | 0.533 | 0.401 | 0.425 | 0.735 | 0.442 | 0.680 | 0.296 |

## G2 — coverage pass@2,000 (`cov_<pool>_<arm>_s<k>.s0.jsonl`, `coverage.py --k 2000 --temperature 0.8 --seed 0 --batch 1000`)

Measured 2026-09-22 **on the original G1 / G2 Stage-1 checkpoints**, which the host cleanup deleted; the ladder
rows below are on retrained replicas of the same (set, seed). See § G5 for how far a retrain moves a number.

| arm s | depth-3 1,000 | req8 300 | reductio-req 300 (7-line stratum; ≥ 8) | per-sample d3 / req8 / red | ≥ 8-line pattern proofs d3 / req8 / red | Lean rej |
|---|---|---|---|---|---|---|
| c0 s0 | 506 (280) / 1000 | 165 (164) / 300 | 31 (31) / 300 (31; 0) | 0.0926 / 0.0155 / 0.0016 | 179 / 177 / 0 | 0 |
| c0 s1 | 423 (197) / 1000 | 113 (113) / 300 | 27 (27) / 300 (27; 0) | 0.1003 / 0.0134 / 0.0091 | 96 / 129 / 0 | 0 |
| g1 s0 | 456 (247) / 1000 | 138 (138) / 300 | 38 (38) / 300 (38; 0) | 0.1025 / 0.0172 / 0.0110 | 153 / 175 / 0 | 0 |
| g1 s1 | 603 (391) / 1000 | 259 (259) / 300 | 31 (31) / 300 (31; 0) | 0.2579 / 0.3185 / 0.0028 | 384 / 356 / 0 | 0 |
| g2 s0 | 288 (65) / 1000 | 38 (38) / 300 | 0 (0) / 300 (0; 0) | 0.1022 / 0.0059 / 0.0000 | 42 / 45 / 0 | 0 |
| g2 s1 | 266 (69) / 1000 | 23 (23) / 300 | 0 (0) / 300 (0; 0) | 0.0812 / 0.0017 / 0.0000 | 24 / 25 / 0 | 0 |

## G3 — depth-3 dial (`{ei,frozen}_d3_<arm>_s<k>/`, `expert_iter.py --rounds 4 --k 32 --temperature 0.8 --batch 768`, targets `data/p2/targets_depth3.jsonl`)

C0's rows are `artifacts/lf_control/{ei,frozen}_d3_seq_s{0,1}/`, pulled from
`hf://buckets/dan-pandori/nd-rl/lean-format/artifacts/lf/`; their `args.json` confirms `--init
ckpts/lf/stage1_a1_seq_s<k>.pt --train data/p2/train_depth3_f0_a1.jsonl`, i.e. the same model and set as this
run's C0. G1 / G2 measured 2026-09-22 on the original checkpoints.

| arm s | EI | frozen | EI − frozen | EI acq by round | held-out r4 |
|---|---|---|---|---|---|
| c0 s0 | 0.418 | 0.163 | +0.255 | 0.104, 0.362, 0.401, 0.418 | 0.956 |
| c0 s1 | 0.408 | 0.116 | +0.292 | 0.085, 0.350, 0.392, 0.408 | 0.966 |
| g1 s0 | 0.403 | 0.165 | +0.238 | 0.120, 0.341, 0.379, 0.403 | 0.947 |
| g1 s1 | 0.436 | 0.322 | +0.114 | 0.297, 0.383, 0.421, 0.436 | 0.957 |
| g2 s0 | 0.415 | 0.032 | +0.383 | 0.020, 0.261, 0.378, 0.415 | 0.702 |
| g2 s1 | 0.396 | 0.034 | +0.362 | 0.022, 0.320, 0.382, 0.396 | 0.699 |

## G4 — ladder rung T1 and frozen, 8 rounds × 32 attempts (`la_{T1,frozen}_<arm>_s<k>/`, `ladder_ei.py`, pools `data/ladder/`, byte-identical to ladder-A's; `L*` = max L with ≥ 5 transfer theorems solved at `L_true` ≥ L)

Measured 2026-09-23/24, all arms on the same two pods, same sampler settings, same 2,285-theorem transfer pool.
`la_frozen_g1_s0` was **not run** — it was the pre-registered droppable tail and the $14 budget stopped at 11 of
12 jobs (`QUESTIONS.md`, 2026-09-24 08:35 UTC).

| arm s | rung | L* | solved | 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 | textbook | schemata ≥ 5 | held-out |
|---|---|---|---|---|---|---|---|
| c0 s0 | frozen | 9 | 158 | 42 / 69 / 44 / 3 / 0 / 0 / 0 / 0 | 6 |  | 0.909 → 0.909 |
| c0 s0 | T1 | 12 | 890 | 92 / 166 / 525 / 91 / 11 / 5 / 0 / 0 | 37 | contraposition 19, export 5 | 0.909 → 0.959 |
| c0 s1 | frozen | 9 | 114 | 44 / 47 / 22 / 1 / 0 / 0 / 0 / 0 | 13 | export 7 | 0.897 → 0.897 |
| c0 s1 | T1 | 11 | 965 | 145 / 165 / 531 / 106 / 15 / 3 / 0 / 0 | 89 | contraposition 30, disjunctive_syllogism 21, export 33 | 0.897 → 0.969 |
| g1 s0 | T1 | 12 | 916 | 133 / 158 / 522 / 87 / 11 / 5 / 0 / 0 | 80 | contraposition 39, disjunctive_syllogism 38 | 0.861 → 0.954 |
| g1 s1 | frozen | 9 | 170 | 35 / 72 / 61 / 2 / 0 / 0 / 0 / 0 | 2 |  | 0.896 → 0.896 |
| g1 s1 | T1 | 10 | 635 | 73 / 141 / 369 / 49 / 2 / 1 / 0 / 0 | 23 | disjunctive_syllogism 23 | 0.896 → 0.931 |
| g2 s0 | frozen | 9 | 44 | 18 / 18 / 8 / 0 / 0 / 0 / 0 / 0 | 1 |  | 0.608 → 0.608 |
| g2 s0 | T1 | 11 | 632 | 85 / 141 / 351 / 50 / 5 / 0 / 0 / 0 | 39 | disjunctive_syllogism 38 | 0.608 → 0.694 |
| g2 s1 | frozen | 9 | 125 | 30 / 64 / 31 / 0 / 0 / 0 / 0 / 0 | 0 |  | 0.665 → 0.665 |
| g2 s1 | T1 | 11 | 607 | 43 / 142 / 364 / 53 / 3 / 2 / 0 / 0 | 0 |  | 0.665 → 0.681 |

**Textbook schemata (`found_transfer_8.jsonl` joined to the transfer pool's `schema` field, 19 schemata × 40 = 760):**

| schema | n | C0 s0 | C0 s1 | G1 s0 | G1 s1 | G2 s0 | G2 s1 |
|---|---|---|---|---|---|---|---|
| constructive_dilemma | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| contraposition | 40 | **19** | **30** | **39** | 0 | 0 | 0 |
| contraposition_conv | 40 | 1 | 1 | 0 | 0 | 0 | 0 |
| demorgan_and_to_nor | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| demorgan_nand_to_or | 40 | 4 | 2 | 2 | 0 | 0 | 0 |
| demorgan_nor_to_and | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| demorgan_or_to_nand | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| disjunctive_syllogism | 40 | 4 | **21** | **38** | **23** | **38** | 0 |
| dist_and_over_or | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| dist_and_over_or_conv | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| dist_or_over_and | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| dist_or_over_and_conv | 40 | 1 | 0 | 0 | 0 | 0 | 0 |
| excluded_middle | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| export | 40 | **5** | **33** | 0 | 0 | 1 | 0 |
| import | 40 | 1 | 0 | 1 | 0 | 0 | 0 |
| negated_conditional | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| negated_conditional_conv | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| peirce | 40 | 1 | 1 | 0 | 0 | 0 | 0 |
| peirce_sequent | 40 | 1 | 1 | 0 | 0 | 0 | 0 |
| **total / 760** | 760 | 37 | 89 | 80 | 23 | 39 | 0 |
| **schemata at ≥ 5** | 19 | 2 | 3 | 2 | 1 | 1 | 0 |

## G5 — what a retrain and a hardware change are worth (`heldout_<arm>_s<k>.json` 2026-09-22 vs `heldout2_<arm>_s<k>.json` 2026-09-23/24)

C0's two rows are the **harness control**: byte-identical checkpoint (md5 verified), different GPU class, the new
decode path. G1 / G2's rows are a genuine retrain: same set, same seed, same command line.

| arm s | held-out greedy 2026-09-22 (RTX 3090) | held-out greedy 2026-09-23 (A6000 / 4090) | delta pp |
|---|---|---|---|
| c0 s0 | 0.909 | 0.909 | +0.00 |
| c0 s1 | 0.896 | 0.897 | +0.08 |
| g1 s0 | 0.875 | 0.861 | -1.44 |
| g1 s1 | 0.940 | 0.896 | -4.44 |
| g2 s0 | 0.626 | 0.608 | -1.78 |
| g2 s1 | 0.606 | 0.665 | +5.96 |

Every delta is concentrated in the 6-line bin: C0 s0 0.686 → 0.686, G1 s0 0.521 → 0.451, G1 s1 0.849 → 0.718,
G2 s0 0.205 → 0.138, G2 s1 0.101 → 0.425.

## G6 — checker of record (`record_<arm>_s<k>.json`, the unmodified `nd2lean.py --check` + `nd_verify` over every counted proof of the dial, the ladder and the three coverage runs)

- c0: 20426 counted proofs, both accept 20426, disagreements 0
- g1: 21162 counted proofs, both accept 21162, disagreements 0
- g2: 15425 counted proofs, both accept 15425, disagreements 0

**57,013 counted proofs, 57,013 accepted by both, 0 disagreements.** `coverage.py`'s in-line Lean check also
rejected 0 of the `nd_verify`-accepted distinct proofs in all six coverage runs. `nd_verify`, `nd2lean.py` and
`lean_gate.py` are unmodified in this run (`git diff origin/main HEAD -- nd_verify/ nd2lean.py` empty).

## G7 — sampler equivalence (`regress.json`, `dsg_regress.py`, 128 samples from `data/ladder/transfer.jsonl`, T 0.8)

`path='base'` with row-keyed rng, sample.py's default as configured here, and the fast path with compaction
explicitly off: **token streams and decoded proofs identical**, verdict PASS. With **compaction on**, 1 row of 128
differs, first at decode step 162 — which is why this run sets `ND_SAMPLE_COMPACT=0` and keeps batch 512.

## G8 — cost

`podbudget ds-generator`: **21.34 pod-hours, $13.02**, of a $14 / 28 pod-hour budget. `dsg-1` RTX A6000 48 GB,
11.56 h, $5.78 (billed $0.50/h); `dsg-2` RTX 4090 24 GB, 9.78 h, $7.24 ($0.74/h). Both deleted (`podls` empty of
`dsg-*`). RTX 3090 and A40 were out of stock throughout. The 2026-09-22 phase spent ≈ $2.5 of its own $20 ceiling.

## Bucket

`hf://buckets/dan-pandori/nd-rl/ds-generator/{artifacts/dsg,ckpts/dsg,ckpts/ladder,data/dsg}` — `data/dsg`
(the two 155,000-record sets and the three raw pools), `ckpts/dsg` (four Stage-1 checkpoints), `ckpts/ladder`
(per-round ladder checkpoints), `artifacts/dsg` (everything above, incl. every per-round `found_*.jsonl`).
The per-round training mixes `la_*/mix_<r>.jsonl` (263 MB) were not kept: no counted number reads them.

# noise-floor (proposal 11, run 2) — what difference can this project resolve?

Run id `noise-floor`, branch `dan_noise-floor`. **Interim numbers are published here as each stage
lands**, because the sibling run `cap-horizon` is running now and reads this section as its yardstick.

**Model behind every row below unless stated otherwise:** 3,214,336-parameter from-scratch GPT,
`lean_seq` Lean surface format, **cap 6**, `train.py --mode lean_seq --steps 6000 --bs 128 --cap 6
--seed {0,1}` — the same model, format and schedule as `ds-generator`'s C0/G1/G2 and
`ds-composition`'s C0/A1, which is what makes this floor quotable by those runs. Checkpoints
`ckpts/nf/stage1_p<i>_s<k>.pt`, training sets `data/nf/train_p<i>.jsonl`.

## N1. The four null pools are the same distribution (premise check)

Source: `artifacts/nf/premise.json` (built by `nf_premise.py` from `artifacts/nf/{shape,overlap,
assemble,render}_p<i>.json`; those were produced on the pods by `dsg_shape.py`, `dsg_overlap.py`,
`dsg_assemble.py`, `dsg_render_check.py`, all unmodified). Generation command in `log.md`
(2026-09-24 16:03) — `make_coverage_sets.py gen` with **no knob flags**, generator seeds
21000 / 22000 / 23000 / 24000, 6,000,000 tries each; the pods log `generator knobs: None`.

| quantity | P1 | P2 | P3 | P4 | max − min | C0 published (`data/dsg/README.md`) |
|---|---|---|---|---|---|---|
| records / length 2–6 | 155,000 / 31,000 each | same | same | same | 0 | 155,000 / 31,000 each |
| box depth 0 / 1 / 2 (%) | 53.11 / 35.52 / 11.37 | 53.26 / 35.33 / 11.41 | 53.28 / 35.46 / 11.26 | 53.30 / 35.44 / 11.26 | 0.19 / 0.19 / 0.15 | 53.2 / 35.4 / 11.4 |
| box depth 3 (%) | 0.00 | 0.00 | 0.00 | 0.00 | 0 | 0 (excluded by design) |
| proofs with `ORE` (%) | 1.42 | 1.48 | 1.45 | 1.46 | 0.07 | 1.46 |
| proofs with `AS` (%) | 46.89 | 46.74 | 46.72 | 46.70 | 0.19 | 46.8 |
| proofs with `IMPI` / `IMPE` (%) | 36.57 / 39.76 | 36.31 / 39.83 | 36.50 / 39.85 | 36.36 / 39.95 | 0.26 / 0.19 | 36.4 / 40.2 |
| proofs with `NEGI` / `NEGE` / `DN` (%) | 9.77 / 11.99 / 7.97 | 9.81 / 12.06 / 7.93 | 9.65 / 12.06 / 7.91 | 9.73 / 11.96 / 8.05 | 0.17 / 0.10 / 0.14 | 9.9 / 12.0 / 8.3 |
| proofs with `ANDI` / `R` / `BOTE` (%) | 22.83 / 2.75 / 2.15 | 22.76 / 2.71 / 2.18 | 22.80 / 2.82 / 2.13 | 22.82 / 2.70 / 2.12 | 0.07 / 0.12 / 0.06 | 22.9 / 2.8 / — |
| mean premises | 1.41 | 1.41 | 1.42 | 1.42 | 0.00 | 1.41 |
| contradictory-premise theorems (%) | 6.41 | 6.35 | 6.37 | 6.28 | 0.13 | 6.06 |
| reductio proofs | 9,980 | 9,973 | 9,853 | 10,072 | 219 | — |
| derived-`ORE` proofs | 69 | 71 | 74 | 76 | 7 | — |
| mean ND / Lean (`lean_seq`) tokens | 112.98 / 138.77 | 112.81 / 138.60 | 112.75 / 138.55 | 112.71 / 138.52 | 0.26 / 0.25 | — |
| fill fraction (%) | 0 | 0 | 0 | 0 | 0 | 0 |

**Verdict: all four are replicates, not arms.** Every share agrees across the four pools to
≤ 0.26 pp and with the control's published table to ≤ 0.4 pp. Pre-registered expectation **E11 is
met** (`ORE` share predicted 1.2–1.8 %, measured 1.42–1.48 %; box depth predicted within ±2 pp of
53.2 / 35.4 / 11.4, measured within ±0.2 pp). The only quantity slightly off the control is the
contradictory-premise share, 6.28–6.41 % against 6.06 % — **consistent across all four pools**, so it
is the pre-registered uncapped-pool deviation (the control's pool used `--cap_np 1500 --cap_pat 3000`
per worker), not a between-pool difference; it cannot produce a difference between P1–P4.

**Disjointness.** Against **all nine** evaluation / ladder pools used in this run
(`data/p2/heldout.jsonl`, `targets_depth3`, `transfer_depth3`, `targets_reductio_req`,
`transfer_reductio_req`, `data/r3_1/depth3_req{,_transfer}`, `data/ladder/{rl_targets,transfer}`):
**0 exact-`thm` and 0 renaming-class collisions for all four sets.** Residual, disclosed: 15–26
theorems per set match a `data/p2/heldout.jsonl` theorem only after *reordering the premises*
(0.3–0.5 % of the 5,000), identically across the four pools. Against the take-home's *other*
held-out set `data/heldout.jsonl` (**not used anywhere in this run**) there are 477–510 class
collisions per set, which is expected: that set was never excluded at assembly and this run never
evaluates on it.

**Pairwise renaming-class overlap between the four null sets: 5.8–6.0 %** (|A ∩ B| / 155,000).
Pre-registered expectation **E14 (30–70 %) is a miss, in the harmless direction** — the ≤ 6-line
class universe is far larger than I assumed, so the four pools are nearly disjoint draws and the
between-pool component below is not diluted by shared records.

**Render check** (`dsg_render_check.py`, per set): 3,000 / 3,000 ND → Lean → ND round-trips
identical, 3,000 / 3,000 denoted proofs re-verified by `nd_verify` at cap 6, 1,000 / 1,000 Lean
positives accepted, 300 / 300 theorem-swapped Lean negatives rejected — on every one of the four sets.

## N2. Held-out greedy — the eight null cells (source: `artifacts/nf/heldout_p<i>_s<k>.{json,jsonl}`, `artifacts/nf/summary.json` § `floors`)

Measured on `ckpts/nf/stage1_p<i>_s<k>.pt` — 3,214,336-parameter from-scratch GPT, `lean_seq`, cap 6,
trained on `data/nf/train_p<i>.jsonl`. Command: `eval_set.py --in data/p2/heldout.jsonl --k 1
--temperature 0 --batch 512` (5,000 theorems), identical in every cell.

| quantity | P1 s0 | P1 s1 | P2 s0 | P2 s1 | P3 s0 | P3 s1 | P4 s0 | P4 s1 | mean | **sd** | max/min | **MDD at n = 2** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| overall | 0.8726 | 0.9362 | 0.9458 | 0.8770 | 0.8680 | 0.8858 | 0.8716 | 0.9630 | 0.9025 | **0.0390** | 1.11× | **±20.9 pp** |
| 2-line bin | 0.9970 | 0.9930 | 0.9990 | 1.0000 | 0.9970 | 0.9940 | 0.9980 | 0.9980 | 0.9970 | 0.0024 | 1.01× | ±1.3 pp |
| 3-line bin | 0.9900 | 0.9810 | 0.9920 | 0.9930 | 0.9910 | 0.9910 | 0.9800 | 0.9910 | 0.9886 | 0.0051 | 1.01× | ±2.7 pp |
| 4-line bin | 0.9560 | 0.9450 | 0.9700 | 0.9650 | 0.9530 | 0.9660 | 0.9600 | 0.9680 | 0.9604 | 0.0086 | 1.03× | ±4.6 pp |
| 5-line bin | 0.9330 | 0.9120 | 0.9560 | 0.9190 | 0.9260 | 0.9220 | 0.9260 | 0.9380 | 0.9290 | 0.0135 | 1.05× | ±7.3 pp |
| **6-line bin** | 0.4870 | 0.8500 | 0.8120 | 0.5080 | 0.4730 | 0.5560 | 0.4940 | 0.9200 | 0.6375 | **0.1887** | **1.95×** | **±101 pp (unresolvable)** |
| **depth-3 slice (n = 500)** | 0.0860 | 0.8180 | 0.7060 | 0.1060 | 0.0400 | 0.2040 | 0.0900 | 0.9180 | 0.3710 | **0.3740** | **22.9×** | **±2.01 absolute (unresolvable)** |
| 6-line, no pattern (n = 247) | 0.8300 | 0.7814 | 0.8623 | 0.8421 | 0.8340 | 0.8502 | 0.8300 | 0.8664 | 0.8370 | 0.0265 | 1.11× | ±14.2 pp |

**Pre-registered expectations scored.** **E1 missed** — predicted sd ≤ 0.02 and max − min ≤ 5 pp;
measured **sd 0.039, range 9.5 pp**, roughly twice the predicted floor. **E2 missed in the same
direction** — 6-line bin predicted sd 0.04–0.10, measured **0.189**. **E3 met** — 2-line bin sd
0.0024 ≤ 0.005. **E4 partly met** — the depth-3 slice is bimodal and its sd is 0.374 ≥ 0.20 as
predicted, but only **3 of 8** cells are in the high mode against a predicted 5–8; high-mode
proportion **0.375, Wilson 95 % [0.137, 0.694]**.

**The bimodality is one phenomenon, not two.** All 500 depth-3 held-out theorems are 6-line
theorems (`data/p2/heldout.jsonl`: depth-3 by length = {6: 500} of the 1,000 6-line theorems), and
across the eight null cells the depth-3 slice and the 6-line bin correlate at **r = 0.9994**.
`ds-rendering`'s "bimodal depth-3 cell" and `ds-generator`'s "retrain spread is almost all in the
6-line bin" are the same thing seen twice: **a 6-line-bin mode that a single Stage-1 training run
lands in or does not.** Cells split 3 high / 4 low / 1 between on `ds-rendering`'s own boundaries.

**It is neither the pool nor the seed — it is the individual training run.** Two-way decomposition
(4 pools × 2 seeds, one observation per cell; the interaction is confounded with error):

| quantity | MS_pool | MS_seed | MS_resid | var_pool | var_seed | var_resid |
|---|---|---|---|---|---|---|
| overall | 0.000638 | 0.001352 | **0.002458** | −0.00091 | −0.00028 | **0.00246** |
| 6-line bin | 0.01428 | 0.04033 | **0.05532** | −0.0205 | −0.0037 | **0.0553** |
| depth-3 slice | 0.05832 | 0.1579 | **0.2154** | −0.0786 | −0.0144 | **0.2154** |

Both between-pool and between-seed components come out **negative** (i.e. indistinguishable from
zero) on every held-out quantity: within a pool, seed 0 and seed 1 land in *different* modes
(P1 0.487 / 0.850, P2 0.812 / 0.508, P4 0.494 / 0.920), and P3 is low on both. **E12's premise is
wrong for held-out accuracy in a way that matters: re-drawing the data set buys you no more
independence than re-seeding Stage-1, and neither factor explains the spread — the residual does.**
The practical consequence is that an arm's two seeds are two coin flips on the 6-line mode, so a
two-seed held-out comparison is a comparison of two coin flips.

## N3. Frozen ladder — the eight null cells (source: `artifacts/nf/la_frozen_p<i>_s<k>/round_8.json`)

Measured on `ckpts/nf/stage1_p<i>_s<k>.pt` (3,214,336-parameter `lean_seq` GPT, cap 6, trained on
`data/nf/train_p<i>.jsonl`). Command, identical in every cell and identical to `ds-generator`'s and
`ds-composition`'s: `ladder_ei.py --no_train --rounds 8 --k 32 --temperature 0.8 --batch 512
--max_new 512` on `data/ladder/` (4,495 RL targets, 2,285 transfer theorems), `ND_SAMPLE_COMPACT=0`.
A proof counts only if `nd_verify` **and** Lean accept.

| cell | P1 s0 | P1 s1 | P2 s0 | P2 s1 | P3 s0 | P3 s1 | P4 s0 | P4 s1 | mean | sd | max/min | **MDD at n = 2** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **transfer solved / 2,285** | 117 | 262 | 200 | 96 | 62 | 174 | 177 | 265 | 169.1 | **74.1** | **4.27×** | **±397 (±235 %)** |
| transfer `L*` | 9 | 9 | 9 | 9 | 9 | 9 | 9 | **10** | 9.125 | **0.354** | 1.11× | **±1.9 points** |
| RL targets solved / 4,495 | 1,036 | 1,715 | 1,512 | 823 | 714 | 1,298 | 1,187 | 1,765 | 1,256 | 391 | 2.47× | ±2,098 (±167 %) |

**This is the run's headline.** Eight models that differ only in a generator RNG seed and a Stage-1
seed span **62 to 265 solved transfer theorems, a 4.27× range**, sd = 43.8 % of the mean. The
control's own published frozen ladder — **158 (s0) and 114 (s1)**, `ckpts/lf/stage1_a1_seq_s{0,1}.pt`
— sits in the middle of that range, and so does **every** frozen-ladder value proposal 10 reported:
`ds-generator` G2 44 / 125 and G1 170, `ds-composition` A1 205 and A2 111. Pre-registered
**E8 missed** (max/min predicted 1.4–2.5×, measured **4.27×**; sd ≥ 25 % of the mean **met** at
43.8 %) and **E10 missed by ≈ 4×** (n = 2 resolvable difference predicted ±40–60 %, measured
**±235 %**).

**`L*` is the robust readout; the solve count is not.** Seven of the eight cells give `L*` = 9 and
one gives 10, sd 0.354, while the underlying solve count moves 4.27×. **E9 missed in the favourable
direction** (predicted 9–11, i.e. 2 points of pure noise; measured 9–10, **1 point**). The
resolvable `L*` difference at n = 2 is **±1.9 points**, so a 1-point `L*` difference is noise and a
2-point one is at the edge of resolution.

**Again the spread is the individual training run, not the pool or the seed** (4 × 2 unreplicated
decomposition): MS_pool 4,111, MS_seed 7,260, MS_resid **6,268** → var_pool **−1,079**, var_seed
**+248**, var_resid **6,268**. E12's ordering (σ²_seed ≥ σ²_pool) holds in sign but both components
are negligible beside the residual: **re-drawing the data set buys no more independence than
re-seeding Stage-1.** Bimodality coefficient 0.546 (< 5/9), so unlike the held-out 6-line bin the
frozen ladder is not bimodal — it is unimodal and very wide.

**What an n = 2 comparison of frozen-ladder solves can say.** Nothing below a **2.4× ratio**
(± 235 % of the mean). And non-parametrically, nothing at all: a two-sided exact permutation test at
2 vs 2 has minimum attainable p = **1/3**.

## N4. Coverage pass@2,000 — the eight null cells (source: `artifacts/nf/cov_{red,req8}_p<i>_s<k>.s0.jsonl`)

Measured on `ckpts/nf/stage1_p<i>_s<k>.pt` (3,214,336-parameter `lean_seq` GPT, cap 6). Command,
identical in every cell: `coverage.py --k 2000 --temperature 0.8 --seed 0 --batch 1000 --procs 2`.
A sample counts only if `nd_verify` **and** Lean accept. `targets_depth3` coverage was **dropped**
before it ran (the pre-registered first drop; see `log.md` 2026-09-24 17:45).

| pool (n targets) | P1 s0 | P1 s1 | P2 s0 | P2 s1 | P3 s0 | P3 s1 | P4 s0 | P4 s1 | mean | sd | max/min | **MDD at n = 2** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `targets_reductio_req` (300) | 31 | 19 | 39 | 43 | **6** | **46** | 34 | 27 | 30.6 | 13.2 | **7.67×** | **±71 (±232 %)** |
| `r3_1/depth3_req`, required@8 (300) | 89 | 242 | 205 | **61** | 71 | 172 | 144 | 238 | 152.8 | 73.3 | **3.97×** | **±393 (±257 %)** |

**E5 and E6 both missed, again with the floor far larger than predicted** (both predicted a max/min
ratio of 1.5–3×; measured **7.67×** and **3.97×**). The `redreq` pool is the worse of the two because
its counts are small: one null cell solves **6** of 300 and another **46**, and the control's own
published values (**31 / 27**) sit in the middle.

The published contrasts, against this floor:

| standing comparison | original | inside the null range? |
|---|---|---|
| `ds-generator` G1 s1 vs C0 s1, required@8 | 259 vs 113 (2.3×) | 259 is just outside the null range 61–242, but the ratio 2.29× is below the MDD's 3.57× — and G1 **is** a null arm, so this is the floor measuring itself |
| `ds-generator` G1 s0 vs C0 s0, required@8 | 138 vs 165 | **yes** |
| `ds-composition` A1 vs C0, `redreq` | 16 / 18 vs 28 / 26 | **yes** — the null range is 6–46 |
| `ds-composition` A2 s1 vs C0 s1, `redreq` | 4 vs 26 | **yes** |
| `ds-generator` G2 vs C0, `redreq` | **0 / 0** vs 31 / 27 | **zero on both seeds is below the null minimum of 6** — outside the null range; the ratio is infinite but the *difference* (30.6) is below the MDD of 71 |
| `ds-composition` A3 (cap 8) vs C0, `redreq` | 54 / 72 vs 28 / 26 | **both seeds are above the null maximum of 46**, but the ratio 2.33× is below the MDD's 3.32× — "outside the null range, but below the MDD" (see § N6 for the two criteria) |

**And again it is the individual training run.** `redreq`: var_pool **−84**, var_seed **−49**,
var_resid **276**. `required@8`: var_pool **−3,401**, var_seed **−899**, var_resid **8,796**. Both
between-factor components are indistinguishable from zero on both pools.

## N5. Gap-closer 1 — `ds-generator`'s missing `la_frozen_g1_s0` (source: `artifacts/nf/la_frozen_dsg_g1_s0/round_8.json`)

Model: `ckpts/dsg/stage1_g1_s0.pt` from `hf://buckets/dan-pandori/nd-rl/ds-generator/ckpts/dsg/` —
3,214,336-parameter `lean_seq` GPT, cap 6, trained on `ds-generator`'s **G1** set
(`gen.py --ore_steps 3 --ore_boxes`, a different generator flag set from P1–P4, shown by that run to
match the control's shape table to sampling noise). **Not retrained.** Same `ladder_ei` command,
same pools, same `--batch 512` as every cell above; run here on an A40.

| cell | transfer solved / 2,285 | transfer `L*` | RL targets solved / 4,495 |
|---|---|---|---|
| G1 seed 0 (**this run**) | **62** | 9 | 612 |
| G1 seed 1 (`ds-generator`) | 170 | 9 | — |

`ds-generator` reported the seed-1 value, 170, as *"larger than either C0 seed"* and flagged the
missing seed-0 cell as *"the run's most informative noise-floor cell is a one-seed estimate."* It is
now two seeds: **62 and 170, a 2.74× difference inside a single arm** whose data set is the
control's distribution by construction. G1's own two seeds **bracket C0's 158 / 114 and G2's
44 / 125 entirely**, which is the cleanest single demonstration in this project that the
frozen-ladder solve count cannot separate arms at two seeds. 62 is also exactly the minimum of my
own eight null cells.

Pooling G1's two seeds with the eight null cells gives **ten independent draws of the control's
distribution**: 62, 62, 96, 117, 170, 174, 177, 200, 262, 265 — mean 158.5, sd 73.6, **max/min
4.27×**. (Reported separately as well as pooled, because G1 is a different generator flag set and
its two cells were trained on different hardware; the pooled figures move the sd by under 2 %.)

## N6. Gap-closer 2 — `ds-composition`'s A1 ladder at Stage-1 seed 1 (source: `artifacts/nf/la_{T1,frozen}_dsc_a1_s1/round_8.json`)

Model: `ckpts/dsc/stage1_a1_s1.pt` from `hf://buckets/dan-pandori/nd-rl/ds-composition/ckpts/dsc/`,
training set `data/dsc/train_a1.jsonl` from the same bucket — 3,214,336-parameter `lean_seq` GPT,
cap 6, A1 = the pool's own length histogram. **Not retrained.** Same `ladder_ei` command, same pools,
same `--batch 512`. C0 seed 1 was **not** re-run: `ds-generator` measured the identical checkpoint
`ckpts/lf/stage1_a1_seq_s1.pt` with the identical command (T1 **965** / `L*` 11, frozen **114** /
`L*` 9).

| | C0 s0 | C0 s1 | A1 s0 | **A1 s1 (this run)** |
|---|---|---|---|---|
| T1 transfer solved / 2,285 | 856 *(`ds-composition`)* / 890 *(`ds-generator`)* | 965 | 965 | **847** |
| T1 transfer `L*` | 12 | 11 | 11 | **11** |
| frozen transfer solved | 158 | 114 | 205 | **194** |
| frozen transfer `L*` | 9 | 9 | 10 | **9** |
| frozen RL targets solved / 4,495 | — | — | — | **1,456** |

`ds-composition`'s **entire ladder was Stage-1 seed 0** and carried three headline claims. With seed 1
in hand:

1. **"A1's T1 ladder beats C0" (965 vs 856) — dead.** It reverses on seed 1: **A1 847 vs C0 965**.
   The sign is not stable across seeds, which is the strongest form of failure available.
2. **"A1's frozen ladder beats C0" (205 vs 158) — same sign on both seeds** (+30 % on s0, +70 % on
   s1) **but inside this run's floor**: the null cells span 62–265 and the MDD is 3.35×, against
   A1/C0 ratios of 1.30× and 1.70×. Reportable only as "consistent in sign at n = 2, not resolvable".
3. **"A1's frozen `L*` is 10 vs C0's 9" — dead.** On seed 1 both are 9. The `L*` floor is ±1.9 points.

**A free third measurement of harness noise.** C0 seed 0's frozen ladder was measured at **158** by
`ds-composition` and at **158** by `ds-generator`, on different pods and different GPU classes, from
the byte-identical checkpoint and the identical command — and its T1 ladder at **856** and **890**
(+4.0 %). So the *sampler and checker* contribute ≈ 0 to the frozen ladder and ≈ 4 % to a ladder
that trains; the 4.27× spread in § N3 is all data-draw + Stage-1-draw, i.e. all training.

## N7. Held-out greedy at 52 cells (4 pools × 13 Stage-1 seeds; pre-registration addendum 2)

Source: `artifacts/nf/heldout_p<i>_s<k>.{json,jsonl}` for `k` = 0…12, `artifacts/nf/summary.json`
§ `floors`. Models `ckpts/nf/stage1_p<i>_s<k>.pt`, all 52 the same 3,214,336-parameter `lean_seq`
GPT at cap 6, `train.py --steps 6000 --bs 128`, differing only in pool and Stage-1 seed. Held-out
command identical in every cell.

| quantity | cells | mean | sd | min | max | max/min | **MDD at n = 2** |
|---|---|---|---|---|---|---|---|
| overall | 52 | 0.9072 | **0.0304** | 0.8420 | 0.9630 | 1.14× | **±16.3 pp** |
| 2-line bin | 52 | 0.9963 | 0.0031 | 0.9870 | 1.0000 | 1.01× | ±1.7 pp |
| 3-line bin | 52 | 0.9883 | 0.0049 | 0.9760 | 0.9970 | 1.02× | ±2.6 pp |
| 4-line bin | 52 | 0.9567 | 0.0151 | 0.8920 | 0.9790 | 1.10× | ±8.1 pp |
| 5-line bin | 52 | 0.9272 | 0.0150 | 0.8770 | 0.9560 | 1.09× | ±8.1 pp |
| **6-line bin** | 52 | 0.6674 | **0.1523** | 0.4210 | 0.9200 | **2.19×** | **±81.7 pp (unresolvable)** |
| **depth-3 slice (500)** | 52 | 0.4402 | **0.3053** | **0.0080** | **0.9180** | **114.8×** | **±1.64 (unresolvable)** |
| 6-line, no pattern (247) | 52 | 0.8240 | 0.0367 | 0.6964 | 0.8785 | 1.26× | ±19.7 pp |

The eight pre-registered cells give sd 0.0390 on the overall rate; 52 cells give **0.0304**, so the
n = 8 figure already published in § N2 was ≈ 28 % high but the same size. **Nothing quoted from § N2
moves materially**; the ± 20.9 pp resolvable difference there becomes **± 16.3 pp** here.

**The depth-3 cell is bimodal, but less cleanly than `ds-rendering` at n = 26 suggested.** On that
run's own boundaries: **24 of 52 high (> 0.44), 13 low (< 0.11), 15 (28.8 %) in the gap**, bimodality
coefficient 0.697 (> 5/9). The right summary is the **probability a training run lands in the high
mode: 0.462, Wilson 95 % [0.333, 0.595]** — a coin flip, and now pinned to ±0.13 instead of ±0.28.

| pool | cells | high (> 0.44) | low (< 0.11) | in the gap | p(high) |
|---|---|---|---|---|---|
| P1 | 13 | 5 | 4 | 4 | 0.385 |
| P2 | 13 | 8 | 3 | 2 | 0.615 |
| P3 | 13 | 6 | 4 | 3 | 0.462 |
| P4 | 13 | 5 | 2 | 6 | 0.385 |

**Variance components at 52 cells** (balanced 4 × 13, one observation per cell):

| quantity | MS_pool | MS_seed | MS_resid | var_pool | var_seed | var_resid |
|---|---|---|---|---|---|---|
| overall | 2.74e−4 | 1.08e−3 | **9.23e−4** | **−5.0e−5** | +4.0e−5 | **9.23e−4** |
| 6-line bin | 6.65e−3 | 2.84e−2 | **2.28e−2** | **−1.2e−3** | +1.4e−3 | **2.28e−2** |
| depth-3 slice | 2.73e−2 | 1.19e−1 | **9.03e−2** | **−4.8e−3** | +7.1e−3 | **9.03e−2** |

With 3 and 12 degrees of freedom instead of 3 and 1, the answer does not change and is now firm:
**the pool contributes nothing measurable and the seed almost nothing; ≈ 99 % of the variance is the
individual training run.** Re-drawing the data set is not a stronger replicate than re-seeding
Stage-1 — a cheaper standard for future runs than the one proposal 11 feared.

## N8. Checker of record

Lean is the checker of record: a proof counts here only if the **unmodified** `nd2lean.py --check`
(official translation + Lean) **and** `nd_verify` accept it. `git diff origin/dan_ds-generator` is
empty for `nd_verify`, `nd2lean.py`, `lean_gate.py`, `train.py`, `eval_set.py`, `coverage.py`,
`ladder_ei.py`, `expert_iter.py`, `sample.py`, `model.py`, `prune.py`, `patterns.py`, `gen.py`,
`make_coverage_sets.py`, `dsg_assemble.py`.

| pass | proofs | both accept | `nd_verify`-only | **Lean-only** | source |
|---|---|---|---|---|---|
| ladder + coverage, every counted proof | 28,737 | **28,737** | 0 | 0 | `artifacts/nf/record_nf1.json`, `record_nf2.json` |
| held-out greedy, 200 sampled per cell × 52 | 10,400 | **10,400** | 0 | 0 | `artifacts/nf/record_heldout.json` (26 cells, Lean 4.34.0 on `nf-1`), `record_heldout_vps.json` (26 cells, Lean **4.34.1** on the VPS) |
| **total** | **39,137** | **39,137** | **0** | **0** | |

**0 disagreements on 39,137 counted proofs**, including 5,200 re-checked on a *different Lean patch
version* (4.34.1) from the one the pods ran (4.34.0) — disclosed, and it agrees.

**The in-loop gate's own rate, which `ds-generator`'s review asked every run to report** (source:
`artifacts/nf/summary.json` § `gate`, aggregated from all 408 `generate()`-call records in
`artifacts/nf/gate_*.jsonl` pulled back from both pods; the `_gate` blocks inside
`record_nf1.json` / `record_nf2.json` are the same count taken before the last few jobs finished):

| samples gated | parse failures | distinct checked by both | both accept | `nd_verify`-only | **Lean-only** |
|---|---|---|---|---|---|
| 20,010,560 | 6,500,782 | 12,033,100 | 1,977,301 | **0** | **808** |

**67.1 Lean-only acceptances per million distinct samples, 0 the other way** — one-directional, as in
every run that has measured it, and an order of magnitude below `ds-generator`'s 718 per million on
its heavier-premise workload (`lean-format` measured 33 per million). No counted proof is affected,
because acceptance is the conjunction. The individual disagreements are in
`artifacts/nf/gate_*.disagree.jsonl`.

## N9. Pre-registered expectations, scored

Every expectation from `preregistration/noise-floor.md` and its two addenda, scored against the
files above. The pattern is one-directional and is the run's second headline: **almost every miss is
the floor being larger than I predicted.**

| # | expectation | measured | verdict |
|---|---|---|---|
| E1 | held-out overall sd ≤ 0.02, max − min ≤ 5 pp | sd **0.0304** (0.039 at n = 8), range **12.1 pp** | **miss — floor ≈ 2× larger** |
| E2 | held-out 6-line bin sd 0.04–0.10 | **0.152** (0.189 at n = 8) | **miss — larger** |
| E3 | held-out 2-line bin sd ≤ 0.005 | 0.0031 | met |
| E4 | depth-3 slice bimodal; 5–8 of 8 high; sd ≥ 0.20 | bimodal (b = 0.697); **3 of 8** high; sd 0.305 | partly met — bimodal and wide, but fewer in the high mode |
| E5 | `redreq` max/min 1.5–3× | **7.67×** | **miss — larger** |
| E6 | `required@8` max/min 1.5–3× | **3.97×** | **miss — larger** |
| E7 | `targets_depth3` max/min 1.2–2× | **not run** (pre-registered first drop; see `log.md` 17:45) | not scored |
| E8 | frozen ladder max/min 1.4–2.5×; sd ≥ 25 % of mean | **4.27×**; sd 43.8 % | **ratio miss — larger**; sd met |
| E9 | frozen ladder `L*` spread 9–11 (2 points of noise) | **9–10 (1 point)** | **miss — smaller, the favourable direction** |
| E10 | n = 2 resolvable frozen-ladder difference ± 40–60 % | **± 235 %** | **miss — ≈ 4× larger** |
| E11 | pool shape tables agree; `ORE` 1.2–1.8 %; box depth within ±2 pp | all shares within 0.26 pp of each other; `ORE` 1.42–1.48 %; box depth within 0.2 pp | met |
| E12 | σ²_seed ≥ σ²_pool on the frozen ladder | var_seed **+248**, var_pool **−1,079** | met in sign, but both ≈ 0 against var_resid 6,268 |
| E13 | 0 Lean-vs-`nd_verify` disagreements on counted proofs; gate 0–1,000 per million, one-directional | **0 / 39,137**; gate **66.1 per million**, 789 Lean-only, 0 the other way | met |
| E14 | inter-pool renaming-class overlap 30–70 % | **5.8–6.0 %** | **miss — the pools are far more independent than assumed** |
| E15 | depth-3 high-mode proportion 0.30–0.55; Wilson half-width ≤ 0.15 | **0.462**, half-width **0.131** | met |
| E16 | ≤ 25 % of the 52 cells in the gap 0.11–0.44 | **28.8 %** (15 of 52) | narrow miss |
| E17 | held-out overall sd at 52 cells 0.030–0.050 | **0.0304** | met |
| E18 | var_pool ≤ 20 % of var_resid for held-out overall | var_pool **negative** (−5.0e−5 vs 9.23e−4) | met |
| E19 | the four pools' high-mode proportions within ±0.20 | 0.385 / 0.615 / 0.462 / 0.385 — spread **0.23** | narrow miss |

**The falsifier did not fire, decisively.** It required the frozen ladder's max/min to be **under
1.2×** across eight null cells, which would have meant `ds-generator`'s G1-vs-C0 gap was a real
effect of `--ore_steps 3 --ore_boxes` and would have reopened the shape account. Measured:
**4.27×** — more than three times the *upper* end of the pre-registered band, and 3.6× the
falsifier's threshold. The shape account stays dead.

## N10. The retrospective table (source: `nf_retro.py`, which reads `artifacts/nf/summary.json`)

Two criteria, both shown, because they disagree on four rows:

- **MDD** — the smallest difference a two-sample t-test at *n* seeds per arm has 80 % power to
  detect, `(t_{.975,2n-2} + t_{.80,2n-2}) · s · √(2/n)`, with `s` the pooled sd over the null cells.
  This is the **parametric best case**: at 2 vs 2 the exact two-sided permutation test cannot reach
  p < 0.05 at all (minimum attainable p = **1/3**).
- **null range** — does the arm's value fall outside the interval the null cells span? Weaker (one
  value outside the range of eight null draws is only about p = 0.22 one-sided) but distribution-free
  and it is the question a reader actually asks.

A finding is scored **survives** only if it clears the MDD.

| quantity | run | standing finding | original | null cells | MDD | verdict |
|---|---|---|---|---|---|---|
| `ladder_frozen_transfer_solved` | ds-composition | A3 (cap 8) frozen ladder beats C0 | 976 vs 158 (6.18×) | 62–265 | ±397 (3.35×) | **survives** |
| `ladder_frozen_transfer_solved` | ds-generator | G1 frozen ladder is above both C0 seeds | 170 vs 158/114 (1.25×) | 62–265 | ±397 (3.35×) | **inside the floor** |
| `ladder_frozen_transfer_solved` | ds-composition | A1 frozen ladder beats C0 (n = 1) | 205 vs 158 (1.30×) | 62–265 | ±397 (3.35×) | **inside the floor** |
| `ladder_frozen_transfer_solved` | ds-composition | A2 frozen ladder is below C0 (n = 1) | 111 vs 158 (1.42×) | 62–265 | ±397 (3.35×) | **inside the floor** |
| `ladder_frozen_transfer_solved` | ds-generator | G2 frozen ladder is above C0 on seed 1 | 125 vs 114 (1.10×) | 62–265 | ±397 (3.35×) | **inside the floor** |
| `ladder_frozen_transfer_solved` | ds-generator | G2 frozen ladder is far below C0 on seed 0 | 44 vs 158 (3.59×) | 62–265 | ±397 (3.35×) | outside the null range, but below the MDD |
| `ladder_frozen_transfer_lstar` | ds-composition | A3 (cap 8) frozen L* 11 vs C0 9 | 11 vs 9 (+2) | 9–10 | ±1.9 | **survives** |
| `ladder_frozen_transfer_lstar` | ds-composition | A1 frozen L* 10 vs C0 9 (n = 1) | 10 vs 9 (+1) | 9–10 | ±1.9 | **inside the floor** |
| `ladder_frozen_transfer_lstar` | lean-format | lean_seq ladder L* 11 vs token 10 | 11 vs 10 (+1) | 9–10 | ±1.9 | outside the null range, but below the MDD |
| `cov_red_solved` | ds-composition | A3 (cap 8) solves more `redreq` than C0 | 54/72 vs 28/26 (2.33×) | 6–46 | ±71 (3.32×) | outside the null range, but below the MDD |
| `cov_red_solved` | ds-composition | A1's reductio deficit vs C0 | 16/18 vs 28/26 (1.59×) | 6–46 | ±71 (3.32×) | **inside the floor** |
| `cov_red_solved` | ds-generator | G2 writes no `redreq` proof at all | 0/0 vs 31/27 (∞) | 6–46 | ±71 (3.32×) | outside the null range, but below the MDD |
| `cov_req8_solved` | ds-generator | G1 s1 required@8 is 2.3x C0 s1 | 259 vs 113 (2.29×) | 61–242 | ±393 (3.57×) | outside the null range, but below the MDD |
| `heldout_overall` | lean-format | lean_seq held-out beats the token format | 90.3 vs 88.3 (+2.0 pp) | 84.2–96.3 | ±16.3 pp | **inside the floor** |
| `heldout_overall` | ds-composition | A1 held-out beats C0 | 93.0 vs 90.3 (+2.7 pp) | 84.2–96.3 | ±16.3 pp | **inside the floor** |
| `heldout_overall` | ds-composition | A3 (cap 8) held-out beats C0 | 95.2 vs 90.3 (+5.0 pp) | 84.2–96.3 | ±16.3 pp | **inside the floor** |
| `heldout_len6_nopattern` | ds-composition | A1's 6-line no-pattern gain over C0 | 89.5 vs 82.6 (+6.9 pp) | 69.6–87.9 | ±19.7 pp | outside the null range, but below the MDD |
| `heldout_len6_nopattern` | ds-composition | A2's 6-line no-pattern deficit vs C0 | 77.5 vs 82.6 (-5.1 pp) | 69.6–87.9 | ±19.7 pp | **inside the floor** |
| `heldout_depth3_slice` | ds-rendering | R2 depth-3 held-out beats C0 (n = 6 each) | 66.1 vs 53.3 (+12.8 pp) | 0.8–91.8 | ±54.8 pp (n = 6) | **inside the floor** |
| `heldout_len6` | ds-generator | G2 6-line held-out is far below C0 | 28.1 vs 63.5 (-35.4 pp) | 42.1–92.0 | ±81.7 pp | **inside the floor** |

## N11. Cost, pods and artifacts

| pod | GPU | created | deleted | pod-hours | billed |
|---|---|---|---|---|---|
| `nf-1` (`kmol2dhu6iz9sw`) | NVIDIA A40 48 GB | 2026-09-24 16:05:45 UTC | 2026-09-25 07:05 UTC | 14.98 | $7.34 |
| `nf-2` (`a2vq56qgrp9e2z`) | NVIDIA A40 48 GB | 2026-09-24 16:06:22 UTC | 2026-09-25 05:26 UTC | 13.34 | $6.54 |
| **total** | | | | **28.32** | **$13.88** |

Real billed rate **$0.49/h**, read from `runpodctl pod list`'s `costPerHr` for both pods — which is
also what `podbudget` assumes for an A40, so for this run its dollar column is right (it is **not**
for A6000 or 4090). Ceiling as run: **42 h / $21** (raised from the brief's 36 h / $18 at 17:40 on
2026-09-24; `QUESTIONS.md`). RunPod balance after: **$151.21**, above proposal 11's $130 floor.

**Measured unit costs on an A40 at four concurrent jobs** (for future sizing — the brief's estimates
were low by 2–7×):

| job | cost |
|---|---|
| Stage-1, 6,000 steps, bs 128 | ≈ 5.3 pod-minutes |
| held-out greedy, 5,000 theorems, k = 1 | ≈ 1.2 pod-minutes |
| frozen ladder, 8 rounds × k 32 on `data/ladder/` | **≈ 1.94 pod-hours** |
| `pass@2,000` coverage, 300 targets | ≈ 0.7 pod-hours |
| `pass@2,000` coverage, 1,000 targets | ≈ 2.4 pod-hours |

Bucket: `hf://buckets/dan-pandori/nd-rl/noise-floor/{ckpts,artifacts,data}` —
`ckpts/nf/stage1_p<i>_s<k>.pt` (52), `artifacts/nf/` (per-cell held-out, coverage and ladder outputs,
`summary.json`, `premise.json`, the `record_*.json` checker passes, the `gate_*.jsonl` logs and their
`.disagree.jsonl`), `data/nf/train_p<i>.jsonl` (4 × 155,000) and `assemble_p<i>.json`.

---

# § lean-judge (2026-09-27) — Lean alone decides

Every count below is reproducible from files pulled back into `artifacts/lj/` (and the bucket) with the
commands named. The corpora are built by `python3 lj_regress.py collect` from the other runs' artifacts.

**Checker labels.** Stored verdicts in the source runs were produced under **Lean ∧ `nd_verify`**
(pre-2026-09-27). Every verdict computed in this run is under **Lean alone**. Lean versions: **4.34.1**
on the VPS, **4.34.0** on pod `lj1` (the version the stored data was produced under); both give the same
verdicts on every case measured here (`lean_check --selftest` 39/39 on both).

**Model labels.** No model was trained in this run. The numbers in L1–L4, L6, L8 are properties of
**stored samples** from runs `cap-horizon`, `noise-floor`, `ds-rendering`, `efficiency`, `lean-format` —
all **`lean_seq`**, **from-scratch**, ~19 M parameters, trained on this project's Stage-1 Lean-format
pools. L5, L7 are measured on **`ckpts/dsc/stage1_a3_s0.pt`** (run `ds-composition`, arm a3, seed 0:
`lean_seq`, from-scratch, ~19 M parameters, Stage-1 pool `train_a3`), pod `lj1` (NVIDIA A40, $0.49/h).

## L0 — the corpora

| quantity | value | source |
|---|---|---|
| `found*.jsonl` records read, Lean-gated arms (1,000 files) | 1,533,741 | `artifacts/lj/collect.json` |
| collected distinct `(prompt, proof)` pairs | 283,012 (282,393 from `found*`, 619 from 34 Lean-gated coverage files) | `artifacts/lj/collect.json`, `artifacts/lj/corpus_accepted.jsonl` (bucket only, 165 MB) |
| of those, **not ND proofs**: run `efficiency` (`artifacts/lo`) stores the **literal Lean text** in the `proof` field of its `found*.jsonl`, in both its free-form and its `lean_seq` arms | 1,195 (of 3,167 records from that directory; the other 1,972 are ND) | `artifacts/lj/t2_judge.rejected.jsonl` — all 1,195 rejected with `nd2lean: QED`, i.e. the string is not an ND proof |
| **distinct ND proofs the old gate counted** (the test-2 corpus) | **281,817** | `artifacts/lj/t2_judge.json` |
| `*.disagree.jsonl` records read (398 files) | 29,070, all `nd_rej & lean_ok` (0 `nd_ok & lean_rej`) | `artifacts/lj/collect.json` |
| distinct Lean-only records | **8,514** — 6,419 with an ND denotation, 2,095 without | `artifacts/lj/corpus_leanonly.jsonl` |

## L1 — acceptance test 1: no judging path calls `nd_verify`

26/26 checks pass, on the VPS and on pod `lj1`. Detection is by `ast`, not grep, over
`expert_iter.py`, `ladder_ei.py`, `coverage.py`, `eval_set.py`, `eval_targets.py`, `grpo.py`,
`lean_gate.py`, `lean_judge.py`: **0** imports of or attribute accesses on `nd_verify`.
Source: `python3 tests/test_lean_only_judge.py`; pod copy `artifacts/lj/setup.log`.

## L2 — acceptance test 2: zero regressions

| quantity | value | source |
|---|---|---|
| records judged | 283,012 | `artifacts/lj/t2_judge.json` |
| accepted by the new judge | **281,817** | same |
| rejected, all with reason `nd2lean: QED` (not ND proofs — see L0) | 1,195 | same, `artifacts/lj/t2_judge.rejected.jsonl` |
| Lean × `nd_verify` table | `nd=True,lean=True` **281,817**; `nd=False,lean=False` **1,195**; `nd=True,lean=False` **0**; `nd=False,lean=True` **0** | same, key `table_nd_lean` |
| **losses** (old gate counted, new judge did not) | **0** | the `nd=True, lean=False` cell |
| acceptance rate on the ND corpus | **281,817 / 281,817 = 100.000 %** | same |
| `n_lines` identical to `nd_verify`'s on proofs both accept (acceptance test 4) | **281,817 / 281,817 = 100 %**, 0 disagreements | same, keys `both_accept`, `n_lines_agree` |
| cost | 870 s Lean wall (3.075 s / 1,000), 19.9 s `nd_verify`, pod `lj1`, 6 workers | same |

The 1,195 are a **corpus-construction error of mine, not a regression**: `lj_regress.py collect` took every
`found*.jsonl` under a directory with a gate log, and run `efficiency`'s files store literal Lean text
(`( fun P => ( fun n1 => ( fun n2 => Or.inr h1 ) ) )`) where every other run stores an ND proof. `nd_verify`
rejects all 1,195, so the old `lean_seq` gate never counted them as ND proofs either. `collect` now skips any
`proof` that does not start with `N` and counts it under `not_nd_excluded`. Judging them properly is
`lean_check`'s job and needs run `efficiency`'s statement convention, which this run does not reimplement: a
spot check against a reconstructed `theorem t (P Q R S : Prop) (h1 : …)` statement accepts 567 and fails 628 on
elaboration (`artifacts/lj/t2_freeform.json`), which shows the statement form differs, not that the proofs are
bad. Not pursued further — out of this run's scope.

## L3 — acceptance test 3: the Lean-only class is now counted

| quantity | value | source |
|---|---|---|
| Lean-only records with an ND denotation | 6,419 | `artifacts/lj/t3_judge.json` |
| accepted by the new judge | **6,419 / 6,419 = 100 %** | same |
| excluded, no ND denotation (run `efficiency`'s `kind: no-denotation`) | 2,095 | same, key `skipped_no_nd` |

Classification of all 8,514 (`artifacts/lj/t3_classify.json`, `lj_regress.py classify`):

| class | n | fraction |
|---|---|---|
| omitted premise re-statement (`PR` lines fewer than declared premises) | 3,550 | 41.7 % |
| `BOTE` on a non-`F` line — i.e. `Not.elim` | 2,205 | 25.9 % |
| no ND denotation (excluded) | 2,095 | 24.6 % |
| other | 531 | 6.2 % |
| `NEGE` on `A` and `A > F` (Lean's `¬A` *is* `A → False`) | 133 | 1.6 % |

## L4 — pitfall 3 (coverage normalises before judging)

Lean's verdict on (i) the literal sampled text, (ii) `nd2lean(nd)`, (iii) `nd2lean(norm(nd))`, on all
6,419 Lean-only records that carry a literal text: **6,419 / 6,419 agree** (all three accept),
**0 disagreements**. So keying the verdict on the normalised string gives identical counts.
Source: `artifacts/lj/t3b_normform.json` (`lj_regress.py normform`, pod `lj1`).

## L5 — acceptance test 5: one expert-iteration round end to end

`expert_iter.py --init ckpts/stage1_a3_s0.pt --rounds 1 --k 16 --temperature 0.8 --relabel`, 200 depth-3
targets, 50 transfer, 200 held-out, retain 3,000, `ft_steps 50` (pod `lj1`).

| quantity | value | source |
|---|---|---|
| samples generated / grammar parse-failures / distinct texts Lean-checked | 4,250 / 476 / 3,506 | `artifacts/lj/t5_gate.jsonl` (4 gate calls) |
| Lean accepted (distinct) | 2,348 | same |
| registry conflicts (two texts, same ND proof, different verdicts) | **0** | same, key `registry_conflicts` |
| Lean cost for the round's gating | 11.5 s wall, 45.6 s process, 6 workers | same |
| **`LEAN*` markers in `found_1.jsonl`, `found_transfer_1.jsonl`, `mix_1.jsonl`** | **0, 0, 0** (228 / 56 / 3,912 records) | `artifacts/lj/t5_marker_grep.txt` |
| target / transfer sample acceptance | 0.5759 / 0.5975 | `artifacts/lj/t5_ei/round_1.json` |
| old gate's count on the same 3,506 samples (Lean ∧ `nd_verify`) | 2,348 | `artifacts/lj/t5_compare.json` |
| new judge's count (Lean alone) | 2,348 — **excess 0, losses 0** | same |

The excess is 0 on this round, which is consistent with the stored Lean-only rate: at 0.01–0.07 % of
distinct checked texts, 3,506 samples predict 0.4–2.5 such proofs, so 0 is the expected order. The
Lean-only class is evidenced at scale by L3, not by this round.

Hindsight relabelling on the round's real samples (`pod/lj/t5_relabel.py`, pitfall 2): of 3,506 dumped
samples, **246** yield a rewritten theorem that *differs* from the prompted one, reducing to 78 distinct
`(new theorem, proof)` pairs, none of which had a registered verdict (the gate never saw them) —
**166 accepted, 80 rejected** (1 untranslatable), 0.50 s of Lean.
Source: `artifacts/lj/t5_relabel.json`. One accepted relabel, checked by hand, in Lean:

```lean
theorem t (P Q R S : Prop) : ((¬(¬R)) → (((R ∨ Q) ∧ (S ∨ R)) → ((¬(¬R)) ∨ (¬(Q ∧ Q))))) := by
  have n5 : ((¬(¬R)) → (((R ∨ Q) ∧ (S ∨ R)) → ((¬(¬R)) ∨ (¬(Q ∧ Q))))) := (fun (n1 : (¬(¬R))) => by
    have n4 : (((R ∨ Q) ∧ (S ∨ R)) → ((¬(¬R)) ∨ (¬(Q ∧ Q)))) := (fun (n2 : ((R ∨ Q) ∧ (S ∨ R))) => by
      have n3 : ((¬(¬R)) ∨ (¬(Q ∧ Q))) := Or.inl n1
      exact n3)
    exact n4)
  exact n5
```

## L6 — acceptance test 6: throughput

20,000 stored accepted proofs, pod `lj1`, `LEAN_GATE_WORKERS=6` (`artifacts/lj/t6_throughput.json`):

| path | s / 1,000 strings |
|---|---|
| **old** `nd_verify` pass (dropped) | 0.0790 |
| **new** registry hit (what a loop sees after `generate()`) | **0.0123** |
| **new** marker (`LEANPARSE` / `LEANREJ`) | 0.0021 |
| **new** fallback: `nd2lean` + batched Lean (gate never saw the string) | **3.556** |

The Lean run on the literal texts is unchanged and is still done by the gate, so in the loop the new
judge is faster than the old one by exactly the dropped `nd_verify` pass: **6.4× faster on the judging
step**, 0.0667 s saved per 1,000 samples.

## L7 — acceptance test 7: `lean_check --selftest`

**39 / 39 pass**, VPS (Lean 4.34.1) and pod `lj1` (Lean 4.34.0).
Source: `artifacts/lj/lean_check_selftest.json`, `artifacts/lj/setup.log`.
Newly accepted: `h.elim a` on `h : ¬P` (term size 1), `Not.elim h a` (1), `Not.intro h` (1),
`And.elim` (5), `Iff.elim` (4), and the decision note's canonical example
`~P ⊢ P > Q` via `N1 (~P) : PR ; N2 (P>Q) : BOTE N1` → `have n2 : (P → Q) := n1.elim` (term size 1).
Still rejected: `sorry`, `sorry` inside a `have`, `simp`, `decide`, `Classical.em`, `Decidable.em`,
`Or.resolve_left`, `mt`, `not_not.mp`, `propext` as a term, `cases`, `match`, a truncated term.
The same canonical example is accepted by the `lean_seq` path: `lean_judge.verify_text` returns
`(True, '', 2)` where `nd_verify` returns
`(False, 'rule check failed: BOTE (line 2)', 2)` — asserted in `tests/test_lean_only_judge.py`.

## L8 — the grammar-as-allowlist claim

`lean_tok.LeanTokenizer('lean_seq').vocab_size` = **107** = 2 specials + 11 formula symbols + 6 prompt
symbols + 16 term/tactic symbols + `h1…h8` + `n1…n64`. The only tokens naming a Lean constant or
projection: `.1 .2 .elim Or.inl Or.inr Or.elim Classical.byContradiction` (plus the type formers
`P Q R S False Prop`). `sorry`, `simp`, `Classical.em` are not in the vocabulary.
Reproduce: the `print` in `LEAN_JUDGE.md` § "The grammar is the allowlist", or
`python3 -c "from lean_tok import LeanTokenizer; t=LeanTokenizer('lean_seq'); print(t.vocab_size, t.itos)"`.

## Bucket

`hf://buckets/dan-pandori/nd-rl/lean-judge/artifacts` — `artifacts/lj/` in full, including
`corpus_accepted.jsonl` (165 MB, gitignored) and `corpus_leanonly.jsonl`.

## fast-stage1 (2026-09-28)

**Model (every row):** 3,214,336-param from-scratch GPT (4L, d 256, 8H), `lean_seq`, cap 6, trained on
`data/p2/train_depth3_f0_a1.jsonl` (155,000 records, 0 depth-3), cosine 6,000 steps, bs 128, lr 1e-3 → 1e-4, warmup 200.
Old arm = `stage1-dynamics` arm C (legacy `train.py`, seeds 0–7; its files copied to `artifacts/fs/old/`). New arm =
`train.py --impl fast`, seeds 0–7 (`ckpts/fs/fast*_s{0..7}.pt`). Judge: Lean alone (`sd_eval.py`, batch 512, max_new 400).
All values recomputed by `python3 fs_analysis.py` → `artifacts/fs/summary.json`, `artifacts/fs/tables.md`.

- FS1 equivalence: 14 / 14 pre-registered comparisons within the n = 8 MDD (table in `FAST_STAGE1.md`). Held-out greedy
  overall 0.9001 fast vs 0.9105 legacy (Δ −1.04 pp, MDD 4.58 pp); 6-line 0.6459 vs 0.7096 (Δ −6.37 pp, MDD 22.94 pp);
  val loss all 0.05124 vs 0.05101 (MDD 0.00219). Sources: `artifacts/fs/ev/fast*_s*.json`, `artifacts/fs/m_fast*_s*.jsonl`,
  `artifacts/fs/old/{ev_c_s*.json,m_c_s*.jsonl}`.
- FS2 depth-3 high mode (> 0.44): fast 4/8, arm C 6/8, arm R 3/8 (`artifacts/fs/ev/`, `artifacts/fs/old/ev_r6*`).
- FS3 one model, A40 alone (billed $0.49/h): legacy 345 s process wall (`waves.jsonl` `legfull`; 48.9 ms/step), fast 135 s and
  128 s (`fast1`, `fast1b`; 16.8 / 17.3 ms/step; compile + capture 14.7 / 9.7 s). `m_legfull_s0.jsonl`, `m_fast1*_s*.jsonl`.
- FS4 tokens: 106,296,500 useful (non-pad) tokens per 6,000-step run of seed 0; fast computes 116,736,000 (1.098×, stream
  length 19,456); legacy pad-to-batch-max would compute 208,984,960 (1.966×) (`m_fast1_s0.jsonl` args record).
- FS5 in-loop useful tokens/s: fast 921k (11.9 % of A40 bf16 dense peak at 6·P per token), legacy 362k (4.7 %).
- FS6 seeds per A40, aggregate steps/s: fast 44.5 / 47.8 / 49.6 / 47.7 at N = 1 / 2 / 4 / 8; legacy 11.9 / 14.0 / 15.6 at N = 1 / 2 / 4
  (`waves.jsonl`; legacy waves are 1,000 steps incl. ≈ 30 s start-up). Peak GPU memory per fast process 0.44 GB.
- FS7 H100 SXM ($3.49/h, 2,000-step waves, `waves_h100.jsonl`): fast 4.1 ms/step alone; aggregate 64.9 / 125.0 / 133.0 / 179.2 /
  188.0 steps/s at N = 1 / 2 / 4 / 8 / 16; legacy alone 30.0 ms/step. bs 512: A40 64.0 ms/step, H100 12.2 ms/step (no gain per token).
- FS8 cost: 1.49 pod-hours, $1.47 (A40 `fs1` 1.24 h $0.61; H100 `fs2` 0.25 h $0.86).
- FS9 bucket: `hf://buckets/dan-pandori/nd-rl/fast-stage1/{artifacts,ckpts}` (the 8 fast checkpoints and `legfull_s0.pt`).

# § lean-prefilter (2026-09-28) — a sound reject-only pre-filter, quota-sized Lean, pipelined gate

Checker for every number: Lean 4.34 core alone (`nd_verify` not called). Pre-registration
`preregistration/lean-prefilter.md` (commit 9238edc). Details and tables: `LEAN_GATE.md`.

## P1 — soundness (test a)
Source: `artifacts/lp/soundness.{md,json}` from `lp_analysis.py` over the bucket files
`artifacts/lp/corpus/*.dump.jsonl.gz` (C1), `artifacts/lp/c2/c2*_checked.jsonl.gz` (C2),
`artifacts/lp/c3/c3_checked.jsonl.gz` (C3). C1 models: eight 3,214,336-parameter from-scratch checkpoints
(ds-composition a1 s1 / a3 s0, cap-horizon k14 s0, ds-generator g2 s0, lean-format a1_rand s0 [`lean_rand`],
full_seq s0, EI d3_seq s0 r8, noise-floor p2 s3), each trained on its own run's set.
- C1: 1,214,162 distinct texts, 499,565 Lean-accepted, 714,597 Lean-rejected; filter rejects 714,597;
  **false rejects 0**; coverage of Lean's rejects **100.00 %**.
- C2 (edge mutants): 76,281 texts, 32,909 accepted; false rejects 0; coverage 100.00 %.
- C3 (stored bucket records re-checked): 19,676 texts, 7,763 accepted (5,424 of them Lean-only accepts from
  `*.disagree.jsonl`); false rejects 0; coverage 100.00 %.
- Accepted texts exercising Lean-beyond-ND: `→ False` written 40,890 / 28,419 / 347 (C1 / C2 / C3);
  `Not.elim` 70 / 1,799 / 1,403; `And.elim` 0 / 1,214 / 0; `Or.elim` 0 / 1,792 / 0.

## P2 — identical accepted sets (test b)
Source: `artifacts/lp/test_b.json`. 120,000 texts of `artifacts/lp/t1/dump_A.jsonl.gz`: 14,816 accepted with
the filter off and on; 0 differ. Wall 421.4 s → 43.4 s (7 workers, A40).

## P3 — one T1 ladder round (test c)
Source: `artifacts/lp/t1/compare.json` (`lp_t1_compare.py`), `artifacts/lp/t1/{gate_*.jsonl,t1_*/round_1.json}`.
Model `ckpts/dsc/stage1_a1_s1.pt` (3,214,336 params, `lean_seq`, from scratch, `data/dsc/train_a1.jsonl`),
k 32, T 0.8, `max_new` 512, seed 1, one round, one RunPod A40 per arm, alone.
- Round wall-clock: A (old: batch 512, 3 workers, no filter, not pipelined) **1,111 s**; B (new, batch 512)
  **485 s** (0.436); C (new, batch 4,096) **272 s** (0.245); D (C + `lean -j 1` + faster filter) **259 s** (0.233).
- Gate share of the round: A 57.1 %, B 3.3 %, C 6.0 %, D 5.0 %.
- Accepted: A = B (19,915 texts, 1,533 found proofs); C = D (20,035, 1,544).
- Truncation at `max_new` 512: 0.027–0.045 % of samples per call.
- Peak memory batch 4,096 / `max_new` 512: 16.76 GB (`artifacts/lp/corpus/*.meta.json`).

## P4 — Lean workers (item 2)
Source: `artifacts/lp/workers{,_j,_j2}.jsonl`. 30,000 arm-A texts, A40 pod (7.65-CPU quota, 96 visible cores):
3 workers default threads 618 / 290 texts/s (two measurements); 7 workers default 298 / 293; 7 workers
`-j 1` 745 / 871; 8 workers `-j 1` 823 / 865; 7 workers `-j 2` 872 / 776; 14 workers `-j 1` 466.

## Spend
Pods `lp-t` (1.44 h, $0.71) and `lp-k` (1.22 h, $0.60), NVIDIA A40 secure at $0.49/h billed: **2.67 pod-hours,
$1.31** of $3 / 6 h. Bucket: `hf://buckets/dan-pandori/nd-rl/lean-prefilter/artifacts/lp/`.

# results-registry (2026-09-29)

Every number here is re-derived by `python3 registry_acceptance.py` → `artifacts/results-registry/acceptance.json`.
Bucket: `hf://buckets/dan-pandori/nd-rl/registry/<run>/` (rows), `registry_merged/` (merged table, .jsonl.gz and
.csv.gz), `results-registry/ckpts/rr/`, `results-registry/artifacts/{rr,results-registry}/`.

**Models (smoke run only; no model-quality claim).** `ckpts/rr/smoke_s0.pt` is 3.2 M parameters, `lean_seq`, from
scratch, 300 steps on `data/p2/train_depth3_f0_a1.jsonl`, seed 0: a throwaway, held-out greedy 4 / 500 on the first 500
held-out theorems (`artifacts/rr/heldout_greedy.json`). `ckpts/rr/ei_fast1_s0_r{1,2}.pt` are two 30-step EI
fine-tunes of fast-stage1's `ckpts/fs/fast1_s0.pt` (3.2 M, `lean_seq`, from scratch, 6,000 steps, same training
set; md5 ae3dfb40…).

| check (pre-registered) | expected | measured | source |
|---|---|---|---|
| E1 checkpoint URI → download md5 = row md5 | 100 %, ≥ 3 | **5 / 5** (final, step 150, state 150, EI r1, EI r2); local copies identical | acceptance.json `E1` |
| E2 negative controls must fail | 3 / 3 fail | **3 / 3**: flipped byte detected; no `ND_RUN_ID` raises; missing bucket raises (VPS and pod) | acceptance.json `E2_flip_detected`; `tests/test_registry.py`; `artifacts/rr/setup.log` |
| E3 held-out greedy of control checkpoints, one filter | ≥ 8 runs | **25 runs** (24 reviewed + this smoke run), 3,091 rows | acceptance.json `E3` |
| E4 three headline numbers exactly | 3 / 3 | **3 / 3** (+1 cross-check): lean-format 0.948; ds-generator 158 / 114; state-env 1,348 (substitute, log.md 01:05), also from its round-8 file via `round_stats` | acceptance.json `E4` |
| E5 cost | < 5 ms/row; < 30 s/ckpt | **0.058 ms/row** (VPS); **3.4–7.4 s** per 12.9 MB checkpoint, 6.0 s per 38.6 MB state (RTX 3090 pod) | acceptance.json `E5_*` |

Backfill: 32 reviewed runs → **298,943 rows**; 63 live smoke rows; the bucket alone gives the same 299,006
(`registry_merge.py --bucket --no_local`). Checker labels: `lean+nd_verify` for runs before 2026-09-27, `lean` from
then on. Per-run file and row counts are in `artifacts/results-registry/backfill_report.json`.

Spend: pod rr-1, RTX 3090 secure cloud, $0.50/h billed, 0.21 h, **$0.10** (`podbudget`).

## repo-hygiene (2026-09-29) — no model; repository and bucket counts
Sources: `hf://buckets/dan-pandori/nd-rl/repo-hygiene/artifacts/repo-hygiene/` (`index_pre.tsv`, `index_post.tsv`,
`inv_*.tsv`, `bucket_ls_*.json.gz`, `ci_green.log`, `ci_red.log`); `ARTIFACTS_INDEX.tsv`.
- Tracked under `artifacts/` at `3bfdec15`: 5,992 files, 4,159,751,936 bytes (of 4,394,344,736 tracked).
- Before upload (`index_pre.tsv`): 2,557 files at their run path, 1,454 same content elsewhere, 1,981 absent
  (2,889,875,938 bytes). After the mirror upload (`index_post.tsv`): 5,992 / 5,992 verified by size + xet hash. Lost: 0.
- New tip: 549 files, 235,990,671 bytes; fresh non-sparse worktree of `e844a8ea` 227 MB (`du -sh`).
- CI: clean-environment run green, 59 s of tests; `ci-broken` red, 5 failures. The smoke models are throwaway
  114 k-parameter `lean_seq` models (from scratch, on `tests/fixtures/proofs150.jsonl`); their numbers mean nothing
  else.

## repo-hygiene-2 (2026-09-29; no model — repository bookkeeping)

| quantity | value | source |
|---|---:|---|
| files untracked by repo-hygiene + repo-hygiene-2 | 6,006 | `rh2_acceptance.py` → `artifacts/repo-hygiene-2/acceptance_dan.md` |
| tracked again, same blob | 3,953 | same |
| manifest rows (bucket sha256 ok) | 2,054 (2,054) | `artifacts/MANIFEST.jsonl`, `artifacts/repo-hygiene-2/verify_bucket.tsv` |
| lost | 0 | same |
| fresh non-sparse `dan` worktree | 148.1 MB | `artifacts/repo-hygiene-2/fresh_worktree.txt` |
| credential-scan hits (6,023 bucket objects, 4.33 GB) | 0 | `artifacts/repo-hygiene-2/secret_scan_bucket.tsv` |
| noise-floor `nf_analysis.py` after fetch vs tracked summary | byte-identical | `artifacts/repo-hygiene-2/nf_summary_refetched.json`, `fetch_nf.log` |

Bucket: `hf://buckets/dan-pandori/nd-rl/repo-hygiene-2/` (`git_tip/` = the 9 moved ckpts/data files; `artifacts/repo-hygiene-2/`).

## compute-record (2026-09-30)

Model behind every GPU number: `ckpts/cr/fast_s0.pt` (`hf://buckets/dan-pandori/nd-rl/compute-record/ckpts/cr/fast_s0.pt`),
3,214,336 parameters, `lean_seq`, from scratch, 6,000 steps at bs 500 on `data/lj/train_retain.jsonl` (3,000 records,
seed 0); a mechanics check model, its accuracy means nothing here. GPU: one NVIDIA A40 (secure, $0.49/h billed). All
rows: `artifacts/compute-record/registry/*.jsonl` (bucket, `artifacts/MANIFEST.jsonl`); every number below is re-derived
by `python3 pod/cr/analyze.py` → `artifacts/compute-record/gpu/analysis.json`.

| check | counter | independent count | source |
|---|---:|---:|---|
| fast_train `train_tokens` (6,000 steps = 1,000 epochs) | 375,609,000 | 375,609,000 | `gpu/expect.json` (1,000 × 375,609 tokens an epoch) |
| legacy train.py `train_tokens` (600 steps = 100 epochs), ×2 | 37,560,900 | 37,560,900 | same |
| sampler `gen_tokens` (4,000 prompts, batch 4,096, max_new 288) | 513,325 | 513,325 | `gpu/sample_check.json` (sampled ids through `<eos>`) |
| sampler `attempts` | 4,000 | 4,000 | same |
| EI round (`ladder`) `lean_checks` | 189 | 189 | `gpu/ladder_gate.jsonl` (`lean_texts`) |
| 2-round EI (`ladder2`) `lean_checks` | 9,637 | 9,637 | `gpu/ladder2_gate.jsonl` |
| 2-round EI fine-tune `train_steps` (child train.py) | 600 | 600 | `--ft_steps 300` × 2 |
| fast_train counting per step (part 3, after review) `train_tokens` / `train_steps` | 37,560,900 / 600 | 37,560,900 / 600 | `gpu/expect.json`; `--steps 600` |
| `grpo.py` sample-phase `attempts`, rounds 1 / 2 | 1,536 / 1,536 | 1,536 / 1,536 | `grpo/round_<r>.json` (3 steps × 64 prompts × 8) |
| `grpo.py` `train_steps` (updates only), rounds 1 / 2 | 3 / 1 | 3 / 1 | `grpo/round_<r>.json` (steps with grad_norm ≠ 0) |
| `ND_COMPUTE=0` runs: rows written | 0 | 0 | registry |

| job | own wall-clock (s) | Σ `gpu_seconds` (s) | ratio | processes | source |
|---|---:|---:|---:|---:|---|
| fast train, 6,000 steps (clock from `save_config`) | 376.85 | 372.54 | 0.989 | 1 | `gpu/walls.jsonl`, registry |
| legacy train, 600 steps (clock from `save_config`), ×2 | 129.28 / 129.15 | 126.02 / 125.83 | 0.975 / 0.974 | 1 | same |
| fast train, 600 steps (clock from exec) | 59.26 | 56.94 | 0.961 | 1 | same |
| 2-round EI, `ladder_ei.py` (clock from exec) | 79.88 | 75.04 | 0.939 | 3 | same |
| fast train, 600 steps, per-step counting (part 3) | 64.32 | 61.45 | 0.955 | 1 | same |
| 2-round GRPO, 6 steps (part 3) | 27.47 | 25.26 | 0.920 | 1 | same |

Overhead: `train.py`'s per-step counter costs 49.7 µs at bs 500 (`gpu/expect.json`) against a 201.7 ms legacy step
on the A40: 0.025 %. Legacy runs, recording off / on: 121 s / 121 s each (log's integer seconds). `fast_train.py`
counts once at the end (no per-step cost); the sampler adds one `declen.sum()` per decode chunk. Sampling peak memory
11.24 GB (batch 4,096, max_new 288); 56 of 4,000 samples (1.4 %) hit max_new (a 6-min model; not a reported result).

Per-arm compute table of this run: `artifacts/compute-record/compute_table.tsv` (`registry_merge.py --compute --by
arm,seed,round,phase`). Pods: cr1 0.36 h + cr2 0.05 h, A40 at $0.49/h billed: $0.21. Bucket: `hf://buckets/dan-pandori/nd-rl/compute-record/`.

## grpo-state (code phase, 2026-09-30)

Model for every number here: SN-cap12 Stage-1 s0, `ckpts/sc12/stage1_SN12_s0.pt` (bucket
`state-cap12/ckpts/sc12/`), 3,216,384 params, `lean_staten`, from scratch on `data/kh/train_k12.jsonl` (155,000
generator proofs, cap 12). One RTX 3090 (24 GB, $0.50/h billed). Lean alone decides. These are smoke measurements of
the code (≤ 8 updates), **not results**: no claim about GRPO is made from them.

| run (`grpo_state.py`, 256 × G 8, batch 2,048, lr 3e-5, no KL) | updates | s / update | peak alloc | mean reward | groups with variance | source |
|---|---|---|---|---|---|---|
| default | 8 | 18.6 | 8.60 GB | 0.465 | 0.565 | `artifacts/grpo_state/smoke_default/steps.jsonl` |
| unlikely (β_rank 0.25) | 4 | 19.8 | 8.05 GB | 0.462 | 0.591 | `…/smoke_unlikely/steps.jsonl` |
| pass@4 | 4 | 19.2 | 8.15 GB | 0.463 | 0.606 | `…/smoke_passk/steps.jsonl` |
| distinct (bonus 0.5) | 4 | 20.7 | 8.09 GB | 0.463 | 0.601 | `…/smoke_distinct/steps.jsonl` |
| default + pass@4 concurrently (seed 1) | 6 each | 26.5 / 26.4 | 8.92 / 8.61 GB | 0.456 / 0.441 | 0.573 / 0.608 | `…/conc_{default,passk}/steps.jsonl` |

Compute rows (registry, `python3 gs_compute.py artifacts/grpo-state/registry`), per arm:

| arm | gpu_seconds | gen_tokens | attempts | actions | train_steps | train_tokens | lean_checks |
|---|---|---|---|---|---|---|---|
| smoke_default | 159 | 3,015,571 | 16,384 | 162,298 | 8 | 8,802,833 | 7,201 |
| smoke_unlikely | 94 | 1,556,538 | 8,192 | 83,476 | 4 | 4,728,533 | 3,567 |
| smoke_passk | 87 | 1,553,995 | 8,192 | 83,332 | 4 | 2,734,076 | 3,587 |
| smoke_distinct | 94 | 1,553,906 | 8,192 | 83,365 | 4 | 5,142,343 | 3,584 |
| conc_default | 169 | 2,275,190 | 12,288 | 121,103 | 6 | 6,731,648 | 5,320 |
| conc_passk | 168 | 2,307,410 | 12,288 | 123,320 | 6 | 3,989,653 | 5,165 |

| smoke2_default (A40, KL 0.02, subsets, with boundary evals) | 107 | 1,614,519 | 8,720 | 87,652 | 2 | 4,400,566 | 2,431 |
| smoke2_unlikely (A40, subsets, with boundary evals) | 97 | 1,621,632 | 8,720 | 88,139 | 2 | 2,429,445 | 2,436 |

(`attempts` counts rollouts, evaluation included; `lean_checks` counts distinct texts sent to Lean after the
prefilter.) Smoke 2 (after the review fixes; `artifacts/grpo_state/smoke2_*/round_{1,2}.json`) ran on subsets of 64
targets, 64 transfer and 200 held-out theorems (the first lines of each pool) only to exercise the boundary path.
Pods: `gs-smoke` RTX 3090 0.23 h $0.11, `gs-smoke2` A40 ($0.49/h) 0.09 h $0.05; total 0.32 h, $0.16. Bucket: `hf://buckets/dan-pandori/nd-rl/grpo-state/{artifacts/grpo_state,artifacts/grpo-state,ckpts/grpo_state}`
(rows in `artifacts/MANIFEST.jsonl`).


## best-state (2026-09-30 / 10-01)

**Models.** All `lean_staten` (proof-state format, SN-v2 naming), sampled in the proof-state environment, **Lean alone
decides** (state env gate, `lean_judge`).
- **best-cap6 s0–s2** (new): `ckpts/bs/stage1_best6_s{0,1,2}_b1200.pt`, 9,560,832 params, Robbie's recipe ported
  (`state_train.py --recipe best`: 6 × 384 Peri-LN, ALiBi/NoPE, Muon + AdamW, MTP 0.3, token budget 128 × 144), from
  scratch, 1,200 s on one A40 (≈ 24,000 steps, 6.8 epochs of pairs), on the cap-6 control set
  `data/p2/train_depth3_f0_a1.jsonl` (155,000; md5 29276f24…). T1 = + 8 ladder rounds:
  `ckpts/bs/ladder/la_T1_best6_s{0,1,2}_r8.pt`.
- **best-cap12 s0–s2** (new): `ckpts/bs/stage1_best12_s{0,1,2}_b1200.pt`, same recipe and budget (≈ 24,000 steps, 3.7
  epochs), on K12 `data/kh/train_k12.jsonl` (155,000; md5 800b5486…). T1: `ckpts/bs/ladder/la_T1_best12_s{0,1,2}_r8.pt`.
- **ours-cap6** (inherited): SN-v2 cap-6 Stage-1 / T1 s0–s1 (`state-env`), 3,216,384 params, `state_train.py` 6,000 × 128
  proofs, same cap-6 set. **ours-cap12** (inherited): SN-cap12 Stage-1 / T1 s0–s3 (`state-cap12`), 3,216,384 params, K12.
- T1 protocol for every cell: `state_ladder_ei.py` defaults (8 rounds, k 32, T 0.8, `rl_targets.jsonl`, replay from the
  cell's Stage-1 set, `max_steps` 48, `max_action` 256); new ladders at batch 2,048 (inherited: 2,048).
- Budget rule (pre-registered): pilot seed 0 cap 6, 300 s → held-out greedy 0.9424 / val 0.0709
  (`artifacts/bs/eval/heldout_best6_s0_b300.json`), 1,200 s → 0.9626 / 0.0715 → 1,200 s.

**Read-out settings.** textbook72: `state_eval.py` k 256, T 0.8, seed 0, `max_action` 512, `max_steps` 96 (= the
`textbook72` run; inherited values from its `summary.json` on `dan_textbook72`). Dev metric (Robbie's): dev half of
`data/ladder/transfer.jsonl` by `sha1(key) % 2 == 0` (1,108, all L_true ≥ 7; `data/bs/dev1108.jsonl`), k 64, solved count.
holdout250: his `passk.py` pool (`data/bs/holdout250.jsonl`), k 256. rr600 / transfer_long2: `lpool_reread.py` k 256,
`max_action` 512, `max_steps` 96 (inherited SN-cap12 / SN-v2 Q at `max_steps` 48 from `state-cap12`; inherited long2 from
`long-pool-2` except SN-v2 frozen, read here). Held-out greedy: `data/p2/heldout.jsonl` 5,000, k 1, T 0. Read batch 2,048
everywhere here (inherited reads used 2,048–4,096: a sampling re-draw, `NOISE_FLOOR.md`). Sources: new
`artifacts/bs/eval/<ckpt>__<read>.json(l)`; inherited dev / h250 / long2 / held `artifacts/bs/eval/{Fz,T1}_SN*__*.json(l)`;
literal texts of every sample in `hf://…/best-state/artifacts/bs/dump/*.jsonl.gz`. Tables: `python3 bs_analysis.py`
(→ `artifacts/bs/analysis_stdout.txt`, `summary.json`). IQM with stratified-bootstrap 95 % interval; at n = 3 the IQM is
the mean. L_true labels are ND-derived upper bounds under Lean.

### textbook72 all 72

| cell | frozen per seed | frozen IQM | T1 per seed | T1 IQM |
|---|---|---|---|---|
| ours-cap6 | 16 / 14 | 15 [14, 16] | 22 / 16 | 19 [16, 22] |
| best-cap6 | 19 / 18 / 20 | 19 [18, 20] | 39 / 40 / 33 | 37.3333 [33, 40] |
| ours-cap12 | 26 / 29 / 32 / 26 | 27.5 [26, 32] | 37 / 38 / 36 / 38 | 37.5 [36, 38] |
| best-cap12 | 32 / 27 / 27 | 28.6667 [27, 32] | 52 / 51 / 52 | 51.6667 [51, 52] |

### textbook72 dev58

| cell | frozen per seed | frozen IQM | T1 per seed | T1 IQM |
|---|---|---|---|---|
| ours-cap6 | 13 / 12 | 12.5 [12, 13] | 18 / 12 | 15 [12, 18] |
| best-cap6 | 13 / 13 / 15 | 13.6667 [13, 15] | 34 / 33 / 26 | 31 [26, 34] |
| ours-cap12 | 20 / 23 / 26 / 21 | 22 [20, 26] | 30 / 32 / 30 / 32 | 31 [30, 32] |
| best-cap12 | 27 / 22 / 21 | 23.3333 [21, 27] | 42 / 44 / 42 | 42.6667 [42, 44] |

### textbook72 train14

| cell | frozen per seed | frozen IQM | T1 per seed | T1 IQM |
|---|---|---|---|---|
| ours-cap6 | 3 / 2 | 2.5 [2, 3] | 4 / 4 | 4 [4, 4] |
| best-cap6 | 6 / 5 / 5 | 5.33333 [5, 6] | 5 / 7 / 7 | 6.33333 [5, 7] |
| ours-cap12 | 6 / 6 / 6 / 5 | 6 [5, 6] | 7 / 6 / 6 / 6 | 6 [6, 7] |
| best-cap12 | 5 / 5 / 6 | 5.33333 [5, 6] | 10 / 7 / 10 | 9 [7, 10] |

### dev metric (1,108, k 64, >= 7)

| cell | frozen per seed | frozen IQM | T1 per seed | T1 IQM |
|---|---|---|---|---|
| ours-cap6 | 405 / 329 | 367 [329, 405] | 746 / 663 | 704.5 [663, 746] |
| best-cap6 | 569 / 466 / 506 | 513.667 [466, 569] | 1002 / 986 / 1002 | 996.667 [986, 1002] |
| ours-cap12 | 745 / 782 / 804 / 781 | 781.5 [745, 804] | 927 / 972 / 961 / 940 | 950.5 [927, 972] |
| best-cap12 | 782 / 767 / 741 | 763.333 [741, 782] | 1058 / 1050 / 1055 | 1054.33 [1050, 1058] |

### holdout250 pass@256

| cell | frozen per seed | frozen IQM | T1 per seed | T1 IQM |
|---|---|---|---|---|
| ours-cap6 | 103 / 83 | 93 [83, 103] | 169 / 151 | 160 [151, 169] |
| best-cap6 | 149 / 125 / 122 | 132 [122, 149] | 226 / 229 / 227 | 227.333 [226, 229] |
| ours-cap12 | 183 / 188 / 198 / 185 | 186.5 [183, 198] | 217 / 221 / 223 / 219 | 220 [217, 223] |
| best-cap12 | 184 / 195 / 182 | 187 [182, 195] | 239 / 237 / 237 | 237.667 [237, 239] |

### rr600 Q (13-16, /380)

| cell | frozen per seed | frozen IQM | T1 per seed | T1 IQM |
|---|---|---|---|---|
| ours-cap6 | 3 / 0 | 1.5 [0, 3] | 102 / 28 | 65 [28, 102] |
| best-cap6 | 8 / 4 / 7 | 6.33333 [4, 8] | 350 / 346 / 339 | 345 [339, 350] |
| ours-cap12 | 134 / 212 / 228 / 216 | 214 [134, 228] | 233 / 295 / 320 / 317 | 306 [233, 320] |
| best-cap12 | 271 / 237 / 216 | 241.333 [216, 271] | 377 / 375 / 376 | 376 [375, 377] |

### transfer_long2 (/21)

| cell | frozen per seed | frozen IQM | T1 per seed | T1 IQM |
|---|---|---|---|---|
| ours-cap6 | 0 / 0 | 0 [0, 0] | 0 / 0 | 0 [0, 0] |
| best-cap6 | 0 / 0 / 0 | 0 [0, 0] | 18 / 18 / 17 | 17.6667 [17, 18] |
| ours-cap12 | 3 / 1 / 3 / 5 | 3 [1, 5] | 8 / 15 / 17 / 14 | 14.5 [8, 17] |
| best-cap12 | 10 / 5 / 4 | 6.33333 [4, 10] | 21 / 21 / 20 | 20.6667 [20, 21] |

### held-out greedy

| cell | frozen per seed | frozen IQM | T1 per seed | T1 IQM |
|---|---|---|---|---|
| ours-cap6 | 0.970 / 0.958 | 0.964 [0.958, 0.970] | 0.972 / 0.971 | 0.971 [0.971, 0.972] |
| best-cap6 | 0.963 / 0.967 / 0.955 | 0.962 [0.955, 0.967] | 0.992 / 0.996 / 0.994 | 0.994 [0.992, 0.996] |
| ours-cap12 | 0.969 / 0.977 / 0.978 / 0.974 | 0.976 [0.969, 0.978] | 0.963 / 0.976 / 0.973 / 0.979 | 0.975 [0.963, 0.979] |
| best-cap12 | 0.926 / 0.951 / 0.903 | 0.927 [0.903, 0.951] | 0.992 / 0.990 / 0.993 | 0.992 [0.990, 0.993] |

### best − ours (IQM difference; MDD from the pre-registration)

| quantity | cap | frozen | T1 | MDD |
|---|---|---|---|---|
| tb72 | 6 | +4.0 | +18.3 | 9.3 |
| tb72 | 12 | +1.2 | +14.2 | 6.5 |
| dev | 6 | +146.7 | +292.2 | 88 |
| dev | 12 | -18.2 | +103.8 | 61 |
| h250 | 6 | +39.0 | +67.3 | – |
| h250 | 12 | +0.5 | +17.7 | – |
| Q | 6 | +4.8 | +280.0 | – |
| Q | 12 | +27.3 | +70.0 | – |
| long2 | 6 | +0.0 | +17.7 | – |
| long2 | 12 | +3.3 | +6.2 | – |

### textbook72 by reference_lines (per seed)

| checkpoint | 1-5 | 6-10 | 11-15 | 16+ | train14 |
|---|---|---|---|---|---|
| Fz_SN6_s0 | 5 | 8 | 0 | 0 | 3 |
| Fz_SN6_s1 | 5 | 7 | 0 | 0 | 2 |
| T1_SN6_s0 | 5 | 12 | 1 | 0 | 4 |
| T1_SN6_s1 | 5 | 7 | 0 | 0 | 4 |
| Fz_best6_s0 | 5 | 8 | 0 | 0 | 6 |
| Fz_best6_s1 | 5 | 8 | 0 | 0 | 5 |
| Fz_best6_s2 | 5 | 10 | 0 | 0 | 5 |
| T1_best6_s0 | 5 | 22 | 6 | 1 | 5 |
| T1_best6_s1 | 5 | 20 | 7 | 1 | 7 |
| T1_best6_s2 | 5 | 18 | 2 | 1 | 7 |
| Fz_SN12_s0 | 5 | 12 | 2 | 1 | 6 |
| Fz_SN12_s1 | 5 | 14 | 4 | 0 | 6 |
| Fz_SN12_s2 | 5 | 17 | 4 | 0 | 6 |
| Fz_SN12_s3 | 5 | 13 | 3 | 0 | 5 |
| T1_SN12_s0 | 5 | 18 | 5 | 2 | 7 |
| T1_SN12_s1 | 5 | 18 | 7 | 2 | 6 |
| T1_SN12_s2 | 5 | 18 | 4 | 3 | 6 |
| T1_SN12_s3 | 5 | 19 | 6 | 2 | 6 |
| Fz_best12_s0 | 5 | 16 | 6 | 0 | 5 |
| Fz_best12_s1 | 5 | 15 | 2 | 0 | 5 |
| Fz_best12_s2 | 5 | 13 | 3 | 0 | 6 |
| T1_best12_s0 | 5 | 22 | 10 | 5 | 10 |
| T1_best12_s1 | 5 | 23 | 12 | 4 | 7 |
| T1_best12_s2 | 5 | 23 | 11 | 3 | 10 |

### textbook72, shortest accepted proof per solved problem (new checkpoints)

| checkpoint | solved | median lines | median term size | lean_check ok |
|---|---|---|---|---|
| Fz_best12_s0 | 32 | 8 | 6 | 32/32 |
| Fz_best12_s1 | 27 | 6 | 4 | 27/27 |
| Fz_best12_s2 | 27 | 6 | 4 | 27/27 |
| Fz_best6_s0 | 19 | 6 | 4 | 19/19 |
| Fz_best6_s1 | 18 | 6 | 4 | 18/18 |
| Fz_best6_s2 | 20 | 6 | 4 | 20/20 |
| T1_best12_s0 | 52 | 9 | 7 | 52/52 |
| T1_best12_s1 | 51 | 9 | 7 | 51/51 |
| T1_best12_s2 | 52 | 9 | 7 | 52/52 |
| T1_best6_s0 | 39 | 7 | 5 | 39/39 |
| T1_best6_s1 | 40 | 7 | 5 | 40/40 |
| T1_best6_s2 | 33 | 7 | 4 | 33/33 |

Term size = `lean_check`'s inference-node count of the shortest accepted proof's elaborated term (the `textbook72` run's
measure), median over the problems that checkpoint solves; lines = written `lean_seq` lines.

**Compute** (`python3 bs_compute.py` → `artifacts/bs/compute_stdout.txt`; registry rows `artifacts/best-state/registry/`).
Ladder rows include the sampling of aborted first attempts (OOM before the ALiBi memory fixes): s0 cap 6 two, the other
five one each (≈ 144k attempts each); a clean ladder is 1,794k attempts.

## Compute per arm and seed (A40 for every new job; `gpu_seconds` from record.compute)

| arm | seed | kind | GPU-s | gen tokens (M) | attempts (k) | train steps | train tokens (M) | Lean checks (k) |
|---|---|---|---|---|---|---|---|---|
| best-cap12 | 0 | T1 ladder (sampling, eval, fine-tune) | 25,876 | 419.1 | 1,938 | 4,800 | 767 | 1,282 |
| best-cap12 | 0 | read-outs | 8,609 | 172.3 | 635 | 0 | 0 | 226 |
| best-cap12 | 0 | stage1 | 1,292 | 0.0 | 0 | 23,951 | 440 | 0 |
| best-cap12 | 1 | T1 ladder (sampling, eval, fine-tune) | 30,524 | 395.5 | 1,938 | 4,800 | 723 | 1,292 |
| best-cap12 | 1 | read-outs | 10,855 | 170.2 | 635 | 0 | 0 | 226 |
| best-cap12 | 1 | stage1 | 1,283 | 0.0 | 0 | 23,987 | 441 | 0 |
| best-cap12 | 2 | T1 ladder (sampling, eval, fine-tune) | 28,952 | 393.4 | 1,938 | 4,800 | 707 | 1,299 |
| best-cap12 | 2 | read-outs | 8,719 | 156.4 | 635 | 0 | 0 | 217 |
| best-cap12 | 2 | stage1 | 1,290 | 0.0 | 0 | 24,123 | 443 | 0 |
| best-cap6 | 0 | T1 ladder (sampling, eval, fine-tune) | 20,057 | 365.8 | 2,225 | 4,800 | 556 | 1,123 |
| best-cap6 | 0 | pilot (300 s) | 382 | 0.0 | 0 | 5,028 | 92 | 0 |
| best-cap6 | 0 | read-outs | 6,300 | 145.7 | 711 | 0 | 0 | 166 |
| best-cap6 | 0 | stage1 | 1,261 | 0.0 | 0 | 24,178 | 444 | 0 |
| best-cap6 | 1 | T1 ladder (sampling, eval, fine-tune) | 16,881 | 330.0 | 1,794 | 4,800 | 500 | 1,060 |
| best-cap6 | 1 | read-outs | 5,197 | 129.4 | 635 | 0 | 0 | 144 |
| best-cap6 | 1 | stage1 | 1,275 | 0.0 | 0 | 23,974 | 441 | 0 |
| best-cap6 | 2 | T1 ladder (sampling, eval, fine-tune) | 17,885 | 349.8 | 1,938 | 4,800 | 517 | 1,077 |
| best-cap6 | 2 | read-outs | 5,065 | 131.6 | 635 | 0 | 0 | 143 |
| best-cap6 | 2 | stage1 | 1,267 | 0.0 | 0 | 23,999 | 441 | 0 |

## Inherited arms (from copied logs; see docstring)

| arm | seed | GPU | Stage-1 s | Stage-1 train tokens (M, est.) | ladder s (8 rounds) |
|---|---|---|---|---|---|
| ours-cap6 | 0 | RTX 3090 / RTX PRO 4000 (state-env pods) | 782 | 333 | 8,297 |
| ours-cap6 | 1 | RTX 3090 / RTX PRO 4000 (state-env pods) | 565 | 333 | 8,761 |
| ours-cap12 | 0 | RTX 3090 | 1,852 | 591 | 12,672 |
| ours-cap12 | 1 | RTX 3090 | 1,835 | 591 | 12,992 |
| ours-cap12 | 2 | A40 | 2,244 | 591 | 16,623 |
| ours-cap12 | 3 | A40 | 2,250 | 591 | 16,042 |

Recipe against recipe, **not compute-matched**. Flags (> 1.25× the comparator): best-cap6 Stage-1 ≈ 1,270 A40-s vs
565–782 s (3090 / RTX PRO 4000) for ours; every best T1 ladder in GPU-seconds. Not flagged: best-cap12 Stage-1 ≈ 1,290 s is
*less* than ours-cap12's 1,835–2,250 s (3090 / A40). T1 ladders 16.9–20.1k vs 8.3–8.8k s at cap 6 and 25.9–30.5k vs 12.7–16.6k s at cap 12), while ladder attempts are
equal by protocol (8 × k 32). Stage-1 training tokens: best 440–444M vs ours ≈ 333M (cap 6) and ≈ 591M (cap 12, estimated).

Pods: bs-p0..p5, bs-r0..r2, bs-d0, all A40 at $0.49/h; 60.1 pod-hours, $29.44 before the cap diagnostic. Bucket:
`hf://buckets/dan-pandori/nd-rl/best-state/{ckpts,artifacts}`.

**Cap diagnostics** (`pod/bs/capdiag.sh`, pod bs-d0 0.64 h $0.32): the four reads with the highest action-truncation /
step-cap rates re-read at `max_action` 1,024, `max_steps` 192 (`artifacts/bs/eval/*_cap.json(l)`):

| read | solved 512/96 → 1,024/192 | lost / gained | truncated | step cap |
|---|---|---|---|---|
| T1_best12_s1 textbook72 | 51 → 53 | 0 / 2 | 1.910 % → 1.817 % | 0.125 % → 0.005 % |
| T1_best12_s2 textbook72 | 52 → 53 | 0 / 1 | 1.172 % → 1.009 % | 0.174 % → 0 |
| T1_best6_s0 transfer_long2 | 18 → 18 | 0 / 0 | 0.186 % → 0.093 % | 0.335 % → 0 |
| Fz_best6_s2 rr600 | 23 → 23 | 0 / 0 | 1.472 % → 1.264 % | 0 |

Truncation barely falls at twice the action budget: these are non-terminating actions, not long proofs cut off. The
caps make the best-recipe numbers slightly low (≤ 2 textbook problems per checkpoint); no conclusion changes. Final spend
60.74 pod-hours, $29.76.

## guided-tts (2026-10-03, executor; UNREVIEWED)

**Models (every number here):** cap 12 = `trajectory`'s `la_T1_best12_s{0,1,2}_r8.pt`; cap 6 = `trajectory-cap6`'s
`la_T1_best6_s{0,1,2}_r8.pt`. All `best_model.ALiBiGPT` 6 × 384, 9,560,832 params, `lean_staten` (environment-assigned
names), Robbie's recipe from scratch (cap 12 on K12 `data/kh/train_k12.jsonl`, cap 6 on `train_depth3_f0_a1.jsonl`,
155,000 each), then the 8-round T1 ladder. md5s match those runs' records (`artifacts/gt/logs/setup_*.log`). No training.
**Checker: Lean alone** (post-2026-09-27): every finished proof's literal text through `lean_gate`; `nd_verify` not called.
**Problems:** textbook72 (dev58 + train14) and Charles's release `candidate_v0` 87, `candidate_v1` 72, `batch3` 14,
`hand_proved_14` 14 (sha256 checked; `data/gt/`), 259 theorems. **long** = release rows with `min_lines` > 10 (90).
**Settings (all arms):** k 256 attempts per theorem, T 0.8, `max_steps` 96 accepted actions, `max_action` 512, ≤ 10
rejections per attempt, sample seed 1, batch 2,048 on A40 (best12 s0 structural: batch 1,024 after an OOM; its
wall-clock is excluded from wall comparisons). Sources: `artifacts/gt/eval/<model>_s<S>_<arm>.{json,rows.jsonl.gz}`;
tables `gt_analysis.py` → `artifacts/gt/analysis_stdout.txt` / `analysis.json`; `gt_compute.py`, `gt_repeat.py`,
`gt_lengths.py` → `artifacts/gt/{compute,repeat,lengths}_stdout.txt`; checker gate `artifacts/gt/validate_s{0,1,2}.json`.

**Checker gate** (`step_check.py` vs Lean, distinct (state, step) pairs from the plain reads, each step a standalone
theorem): 106,505 / 109,151 / 98,885 pairs (314,541 in all; 186,036 Lean-accepted, 128,505 Lean-rejected); **0 false
rejects, 0 misses**. Proof level, all 12 plain + structural reads: every Lean-rejected finished proof carries a checker
flag (e.g. best12 s0 structural 22,910 = 22,910) and no flagged proof was Lean-accepted; no attempt wrote a
non-canonical formula. Guided-logical: 0 Lean-rejected finished proofs in all 6 reads.

**Solved@256 attempts (not compute-matched), per file** tb72 / v0 / v1 / batch3 / hp14 (of 72 / 87 / 72 / 14 / 14):

| model | plain | structural | logical |
|---|---|---|---|
| best12 s0 | 48 / 67 / 52 / 11 / 0 | 53 / 68 / 53 / 11 / 0 | 54 / 75 / 59 / 12 / 0 |
| best12 s1 | 48 / 65 / 51 / 8 / 0 | 50 / 66 / 52 / 8 / 0 | 52 / 71 / 57 / 10 / 0 |
| best12 s2 | 53 / 71 / 55 / 9 / 0 | 55 / 73 / 55 / 10 / 0 | 57 / 75 / 56 / 11 / 0 |
| best6 s0 | 43 / 58 / 44 / 7 / 0 | 47 / 60 / 44 / 7 / 0 | 48 / 65 / 49 / 9 / 0 |
| best6 s1 | 43 / 54 / 42 / 9 / 0 | 43 / 55 / 44 / 9 / 0 | 47 / 66 / 51 / 9 / 0 |
| best6 s2 | 39 / 52 / 35 / 8 / 0 | 41 / 58 / 40 / 8 / 0 | 45 / 62 / 47 / 9 / 0 |

Sanity vs `trajectory*` x0 textbook72 (48 / 49 / 54; 43 / 41 / 38): plain 48 / 48 / 53; 43 / 43 / 39 ✓ (± 3).

**Headline: solve rate at matched sampled tokens, arm − plain (pp), per seed s0 / s1 / s2, IQM [stratified bootstrap 95 %]**
(k = plain-equivalent attempts per theorem; MDD on long ≈ 2.7 pp at k 64, 3.7 at 256, from a bootstrap over attempts):

| group (n) | cap | k | plain | logical − plain | structural − plain |
|---|---|---|---|---|---|
| long (90) | 12 | 64 | 36.8 / 28.7 / 40.2 | +10.0 / +9.9 / +5.2 → +9.1 [+3.7, +13.5] | −1.2 / +0.9 / −1.1 → −0.8 [−3.0, +2.2] |
| long (90) | 12 | 256 | 42.2 / 34.4 / 46.7 | +11.1 / +12.7 / +3.4 → +10.0 [+2.4, +16.9] | −1.2 / +0.3 / −0.2 → −0.3 |
| long (90) | 6 | 64 | 21.8 / 24.1 / 17.9 | +7.4 / +8.1 / +10.3 → +8.3 [+4.1, +14.0] | +0.8 / +0.7 / +1.1 → +0.8 |
| long (90) | 6 | 256 | 26.7 / 27.8 / 21.1 | +6.6 / +8.0 / +11.4 → +8.4 [+3.5, +15.2] | −0.1 / −1.2 / +3.2 → +0.3 |
| Roy (78) | 12 / 6 | 64 | | +5.2 [+1.0, +9.1] / +7.5 [+2.5, +12.4] | −0.1 / +0.3 |
| batch3 (14) | 12 / 6 | 64 | | +11.8 [+1.2, +28.3] / +13.7 [+0.3, +30.5] | −0.3 / +6.4 |
| Pelletier (8) | 12 / 6 | 64 | | +10.7 [0, +32.0] / +2.7 [0, +15.7] | −0.5 / −0.1 |
| ≤ 10 lines (97) | 12 / 6 | 64 | | +2.6 [+0.4, +5.6] / +9.7 [+4.4, +14.6] | −0.8 / +1.6 |
| 11–20 (67) | 12 / 6 | 64 | | +10.3 [+4.5, +15.6] / +10.4 [+5.4, +17.5] | −0.8 / +1.1 |
| > 20 (23) | 12 / 6 | 64 | | +5.6 [−1.3, +14.0] / +2.1 [0, +7.0] | −0.4 / +0.1 |
| textbook72 (72) | 12 / 6 | 64 | | +5.4 [+1.5, +9.5] / +4.8 [+1.1, +10.3] | −0.1 / +0.2 |
| all (259) | 12 / 6 | 64 | 64.0 / 60.9 / 68.9; 53.2 / 53.4 / 47.7 | +5.6 [+3.0, +7.8] / +7.9 [+5.3, +11.0] | −0.5 / +1.1 |

Matched wall-clock (job seconds per attempt, one ratio per job; sampling loop + final Lean), long, k 64: logical +9.1
[+3.3, +14.8] (cap 12), +8.8 [+4.8, +14.1] (cap 6); structural −3.4 / +0.7. Not pre-registered, seconds shared out by
draws per theorem: logical +7.9 / +8.2. At k = 1 every guided arm loses on wall-clock (a guided attempt costs > 1 plain
attempt). Falsifier (logical ≤ plain at every k on long in ≥ 2 / 3 seeds at both caps): **not met** (0 / 3 seeds at each cap).

**Per attempt (not matched):** per-attempt acceptance plain / structural / logical: cap 12 32.3–38.1 % / 34.8–40.2 % /
42.2–47.6 %; cap 6 29.7–33.5 % / 33.6–38.0 % / 41.2–44.6 % (`accepted / 66,304`, `analysis_stdout.txt` jobs table).

**Rejections** (per draw; `analysis_stdout.txt`): plain: structural 2.8–3.0 % (cap 12), 4.3–4.9 % (cap 6), top causes
binder mismatch, `Or.elim` on a non-or, unbound name; logically wrong accepted steps 3.1–4.8 % of draws (top:
application argument mismatch, `⟨,⟩` mismatch, byContradiction, projection). Guided-logical: S 13.8–21.7 %, L 10.0–15.8 %
of draws; 52–59 % of attempts end at the 10-rejection cap. Truncated actions (512 tokens): plain 0.003–0.009 % (cap 12),
0.16–0.28 % (cap 6, above the policy's 0.1 %; non-terminating actions per `best-state`'s 2× diagnostic), guided cap 6
0.6–1.9 % of draws (redrawn, 512 tokens each, charged).

**With-replacement repeats** (`gt_repeat.py`): per redraw, P(a with-replacement draw repeats an already-rejected action)
mean 0.32–0.40 (cap 12 logical), 0.51–0.54 (cap 6 logical), 0.21–0.26 / 0.42–0.46 (structural); P > 0.9 for 13–15 %
(cap 12) and 27–30 % (cap 6) of logical redraws. Exact token sequences, so a repeat that differs only in an
environment-assigned name is not counted (an understatement).

**Proof length** (`gt_lengths.py`; shortest accepted proof per theorem, on theorems all three arms solve; lines =
`have` + `exact` actions; term size = `lean_check` elaborated inference nodes, 3,078 proofs, 0 rejected): cap 12 lines
10.96 / 10.93 / 11.04 plain vs 10.86 / 10.60 / 10.89 logical, term size 7.37 / 7.31 / 7.47 vs 7.28 / 7.01 / 7.33; cap 6
lines 10.28 / 9.96 / 9.90 vs 9.99 / 9.72 / 9.56, term size 6.64 / 6.39 / 6.32 vs 6.43 / 6.22 / 6.04. Guided proofs are
not longer.

**Compute per arm** (`gt_compute.py`; A40; mean over 3 model seeds; registry rows `artifacts/guided-tts/registry/`,
`gpu_seconds` / `gen_tokens` / `attempts` / `actions` / `lean_checks`; 0 training steps / tokens):

| cap, arm | GPU s (sampling) | sampled tokens | prefill tokens | actions | Lean checks | vs plain (GPU s, tokens) |
|---|---|---|---|---|---|---|
| 12 plain | 792 | 14.7 M | 87 M | 1.01 M | 17,054 | 1 |
| 12 structural | 2,507 | 27.7 M | 217 M | 1.82 M | 18,492 | 3.17×, 1.88× |
| 12 logical | 1,729 | 26.2 M | 166 M | 1.57 M | 22,724 | 2.18×, 1.78× |
| 6 plain | 714 | 11.4 M | 52 M | 0.73 M | 9,154 | 1 |
| 6 structural | 2,076 | 30.2 M | 126 M | 1.38 M | 10,606 | 2.91×, 2.65× |
| 6 logical | 1,672 | 30.7 M | 110 M | 1.30 M | 13,553 | 2.34×, 2.68× |

At equal attempts every guided arm used > 1.25× plain's compute (flagged); the comparisons above are at matched tokens /
matched wall-clock. Step checks: ≈ 1 checker call per structurally valid draw, 8–18 s per read (CPU); on long, guided
tokens per attempt are 2.0–2.3× plain (cap 12) and 2.8–3.3× (cap 6).
**Spend:** 4 A40 pods ($0.49/h), 9.07 pod-hours, $4.45 (`podbudget`). **Bucket:** `hf://buckets/dan-pandori/nd-rl/guided-tts/{artifacts/gt,artifacts/guided-tts,data/gt}`.

## create-or-elicit (2026-10-12 / 13, executor; UNREVIEWED; final at CREATE-OR-ELICIT DONE)

**Models.** All `best_model.ALiBiGPT` 6 × 384, **9,560,832 params**, `lean_staten` (environment-assigned names), from
scratch with `state_env_october`'s recipe (`state_train.py --recipe best`, 1,200 s on one A40), then T1 expert iteration
(`state_ladder_ei.py`: k 32, T 0.8, 600 fine-tune steps, 20,000 replay records from the arm's own pretraining set).
- **full, old (s0–s2):** `trajectory/ckpts/tj/stage1_best12_s{S}_b1200.pt` (pend; md5 2bf801fd / eaff7f4d / abca9c63),
  trajectory's ladder r1–r8 (RTX A6000) and rl-continue's r9–r16 (A40); trained on K12 (`train_k12.jsonl`, 155,000).
- **full, new (s3–s5)** and **knockout (s0–s5):** this run, `create-or-elicit/ckpts/coe/stage1_{full,ko}_s{S}.pt` and
  `ckpts/coe/ladder/la_{full,ko}_s{S}_r{1..16}.pt`; full on K12, knockout on **K12⁻** (`data/coe/train_k12ko.jsonl.gz`);
  every round on an NVIDIA A40, batch 1,024.
**Checker: Lean alone** throughout (post-2026-09-27). **Sets:** see `data/coe/README.md` (strict σ-covered members:
123 trained, 106 held-out; read set `read1054` = textbook72 (scoring only) + holdout250 + 732 tracked transfer theorems).

### K12⁻ (source `data/coe/train_k12ko_assemble_report.json`, `artifacts/coe/sigma_k12.json`, `artifacts/coe/shape_k12_vs_ko.md`)
- K12: σ (DN cites a NEGI line) in 16,703 records, written = pruned; σ⁺ (DN cites any derived line) 16,961; DN anywhere 21,274
  (13.7 %); lemma route 0.
- K12⁻ = 138,039 kept + 16,961 refill = 155,000, per-length counts identical; σ⁺ 0, DN 5,102 records (3.29 %), NEGI 5.19 %
  (K12 15.21 %), classical-only theorems 1.33 % (K12 4.13 %; 20,000-record G4ip sample), mean term size 36.25 (35.91).
- Refill Lean check 16,961 / 16,961 (`artifacts/coe/refill_lean_check.json`); controls 200 / 200 and 0 / 200
  (`artifacts/coe/refill_lean_negctl.json`).

### Phase 0.1 — the known-proof estimator at small p (source `artifacts/coe/estimator/REPORT.md`, `summary.json`)
Model: best-cap12 pend s0–s2 (old full). Observed / predicted base successes by estimate bin: ≥ 10⁻³ 1.11 [1.10, 1.13];
10⁻⁴–10⁻³ 1.10 [0.99, 1.22]; 10⁻⁵–10⁻⁴ 2.11 [1.66, 2.64]; 10⁻⁶–10⁻⁵ 3.71 [2.24, 5.80]; < 10⁻⁶ 3.45 [0.94, 8.83]. Significantly
too high on 1 of 330 theorems. Coverage of base large-k successes by proofs known from other sources: 0.70–0.86
(p̂ 10⁻⁴–10⁻³), 0.78 [0.63, 0.89] (10⁻⁵–10⁻⁴).

### Phase 0.2 — budgets restated (source `artifacts/coe/budget/SUMMARY.md`, `budget.json`, `recount*.txt`)
Model: best-cap12 pend and r8, old full s0 / s1 / s2. Per-attempt cost on the 322 (A40, alone, sampling + Lean): 7.22 / 8.04 /
6.36 ms at batch 2,048. A6000 / A40 on the same workload 0.90 / 0.96. r8 budgets (attempts per theorem) and compute-matched
sets: K_att 3,574 → 34 / 33 / 33; K_train 7,416 / 7,126 / 9,921 → 33 / 27 / 24; uniform same-class K_eval-set 10,314 /
10,141 / 14,150 → 28 / 26 / 24; published 19,281 / 21,107 / 23,310 → 22 / 21 / 14; K_adapt 44,570 / 43,427 / 56,509 →
21 / 20 / 14. J9 certificates 9 / 9 (K_train, K_att), 8 / 9 (uniform), 7 / 9 (published), 0 / 9 (K_adapt).

### Phase 2 — sharpening null (source `artifacts/coe/power/phase2_table.md`, `p2_*.json`)
Power sampling (p^α, α 4 and 2; 32 chains per theorem) vs plain at the same decoded tokens. Full s0 / s1 pend (old) on their
K_train compute-matched r8 sets (33 / 27): power 0 / 33, 0 / 27 at both α; plain T 0.8 1 / 33, 1 / 27; T 1.0 1 / 33, 2 / 27.
Knockout s0 / s1 pend on the 106 strict held-out members: power 0 / 106 at both α; plain T 0.8 0 / 106; T 1.0 1 / 106 each
(`la_transfer_916`). Pilot (development data): power α 4 75 % per chain vs plain T 0.8 54 % per attempt; 26 / 32 vs 31 / 32
theorems.

### Knockout bases on σ (source `artifacts/coe/rounds/la_*.json` round 1, `artifacts/coe/score/summary.json`, `artifacts/coe/large/t916_*.json`)
- Round 1 (each base's own k 32 sample): strict σ-covered training targets solved, knockout s0–s5 0 / 0 / 0 / 0 / 0 / 0, full
  s3–s5 17 / 15 / 20 (old full s0–s2: from `old_full_s*.json`); accepted proofs containing σ, knockout 6–13 (all with the
  double negation named in the theorem), full s3–s5 635–885.
- Teacher-forced log p (T 0.8, one name base) of the best known σ proof of a strict held-out member, median over 101: full s0
  pend −19.2; knockout s0–s5 −33.4 / −26.0 / −35.7 / −33.8 / −36.0 / −31.5; the bottleneck step (opening the ¬G box)
  −18.0 to −21.6 vs −10.5.
- `la_transfer_916` (the one generated strict member): knockout s0 base 0 / 131,072 at T 0.8; 1 / 131,072 + 1 / ≈ 1,200 at
  T 1.0 (one by DN on an IMPI line); knockout s1 base 1 / ≈ 1,400 at T 1.0 (free σ by NEGI).

### Phase 1 — the knockout vs full arm (sources: `artifacts/coe/compare_r16_{x0,x1,g0}.json`, `artifacts/coe/rounds/*.json`, `artifacts/coe/general.json`, `artifacts/coe/certificates.json`, `artifacts/coe/stdA.json`, `artifacts/coe/budget/k_*.json`)
Models: full s0–s2 (old, trajectory + rl-continue), full s3–s5 and knockout s0–s5 (this run, A40 batch 1,024); every
number at r16 unless stated; plain k 256, T 0.8, 96 steps, 512 tokens / action, batch 512, sample seed 0 (x0); Lean alone.
Strict σ-covered held-out members: 106 (contraposition_conv 18, demorgan 4, excluded_middle 37, negated_conditional 15,
peirce 12, peirce_sequent 19, generated 1).
- **Strict held-out members solved (of 106):** full s0–s5 42 / 75 / 77 / 65 / 23 / 33; knockout s0–s5 0 / 2 / 1 / 0 / 0 / 2.
  Redraw x1: 43 / 73 / 77 / 64 / 22 / 34 vs 0 / 2 / 1 / 0 / 0 / 1; guided: 44 / 75 / 80 / 64 / 24 / 33 vs 0 / 3 / 0 / 0 / 0 / 2.
- **Families acquired (≥ 50 % of strict held-out members):** full 6 / 6 seeds (contraposition_conv 6, negated_conditional 3,
  peirce 3, peirce_sequent 3, excluded_middle 1, demorgan 0); knockout 0 / 6. **Primary test 6 / 6 vs 0 / 6, one-sided
  Boschloo p = 2.4 × 10⁻⁴ (pre-registered verdict: needs exposure).** Mann–Whitney on members solved p = 0.0011. Per family
  (Holm over 6): contraposition_conv p 2.4 × 10⁻⁴ (Holm 0.0015); negated_conditional, peirce, peirce_sequent 3 vs 0, p 0.035
  (Holm 0.17); excluded_middle 1 vs 0, p 0.30.
- **Per round (k 32 samples, r1–r16 cumulative):** strict σ-covered training targets solved (of 123) full s3–s5 78 / 33 / 36,
  knockout 0 / 5 / 1 / 0 / 0 / 2 (round 1: knockout 0 on every seed, full s3–s5 17 / 15 / 20); free positive reductio proofs
  accepted full s3–s5 49,600 / 20,384 / 17,429, knockout 0 / 34 / 4 / 1 / 2 / 16 (first in r9 / r12 / r15 / r15 / r2; s0 never).
- **General ability (pend):** held-out greedy (p2/heldout 5,000) full median 0.960, knockout 0.883; non-σ subset (4,321)
  0.957 vs 0.950; σ subset (679) 0.966 vs 0.448. holdout250 pass@256 full s3–s5 199 / 193 / 200, knockout 186 / 195 / 188 / 176
  / 183 / 205; textbook72 pass@256 (scoring only) combined pend 33 / 34 / 36 vs 26 / 34 / 29 / 26 / 23 / 28, r16 55 / 54 / 51 vs
  49 / 50 / 44 / 44 / 43 / 45; dev58 pend 27 / 29 / 29 vs 21 / 28 / 25 / 21 / 18 / 23, r16 44 / 44 / 42 vs 39 / 40 / 38 / 36 / 35 /
  37; train14 pend 6 / 5 / 7 vs 5 / 6 / 4 / 5 / 5 / 5, r16 11 / 10 / 9 vs 10 / 10 / 6 / 8 / 8 / 8 (full s3–s5 vs knockout s0–s5;
  the old full seeds were not read on textbook72 in this run).
- **Knockout base certificates** (105 family members pooled at each seed's K_train(16) 17,189–23,322): s0 0 / 1,491,420 and
  s3 0 / 1,340,640 certified (UB95 < 0.05 / K); s1 6 / 1,120,378, s2 1 / 1,338,328, s4 3 / 1,360,222, s5 2 / 1,419,656 not
  certified (rare, ≈ 10⁻⁶ per attempt pooled, almost all on contraposition_conv; s1's six are free reductios on
  contraposition_conv members, ≈ 1 per 8,000 attempts on them).
- **Compute-matched reach on the 322 (K_train(16), r16 vs pend):** Δ_cov full s3 / s4 / s5 +37 / +36 / +32, knockout s0 / s1 /
  s2 / s3 / s4 / s5 +29 / +31 / +35 / +37 / +26 / +21.
- **Phase 3a (one extra EI round from r16, with vs without knockout s1's base's free-σ proof of `la_transfer_916`; plain k 256
  on the 105 strict family members; `artifacts/coe/p3a/`):** seeded vs control knockout s0 0 vs 0, s1 3 vs 3, s2 2 vs 0
  (contraposition_conv, 1 / 256 each; one-sided exact p 0.25), s3 0 vs 0, s5 0 vs 0 (s4 not run).

### Phase 3 — the 1 % σ dose arm (Addendum 5; sources `artifacts/coe/dose_summary.json` (`coe/coe_dose_summary.py`), `artifacts/coe/compare_{pend,r16}_x0.json`, `artifacts/coe/rounds/la_dose1_s*.json`, `artifacts/coe/general.json`, `artifacts/coe/budget/k_dose1_s*.json`)
**Models: M12d s0–s2** = the knockout recipe on `data/coe/train_k12dose1.jsonl.gz` (K12⁻ with 1,550 refill records swapped
for removed σ records: 1.0 %, K12's σ length mix), 1,200 s Stage 1 on an A40, 16-round T1 ladder at batch 1,024, replay
from the dose set; `create-or-elicit/ckpts/coe/stage1_dose1_s{S}.pt`, `ckpts/coe/ladder/la_dose1_s{S}_r{1..16}.pt`.
Reads as Phase 1 (plain k 256 x0 on `read1054`; Lean alone); **no r16 redraw / guided reads and no standard A** (budget cut,
log 2026-10-13 04:13).
- **Strict σ-covered held-out members solved (of 106):** pend 6 / 18 / 8; **r16 58 / 39 / 30** (full 23–77, median 53.5;
  knockout 0–2). Families at the bar at r16: s0 contraposition_conv 18 / 18, negated_conditional 14 / 15, peirce 6 / 12,
  peirce_sequent 19 / 19; s1 contraposition_conv 18 / 18 (17 / 18 at pend), negated_conditional 15 / 15; s2
  contraposition_conv 18 / 18, negated_conditional 10 / 15. Acquired during RL (at the bar at r16, not at pend): 3 / 3 seeds.
- **Exploratory tests (not pre-registered):** families acquired dose 3 / 3 vs knockout 0 / 6, one-sided Boschloo p = 0.0033
  (Fisher 0.012); members solved dose vs knockout Mann–Whitney p = 0.012; dose vs full two-sided p = 0.55.
- **Round 1 (each base's own k 32 sample):** strict training targets solved 2 / 17 / 2; accepted σ proofs 223 / 183 / 241
  (knockout 6–13, full s3–s5 635–885); free positive reductio proofs 213 / 170 / 219 (knockout 0; full 418–665). Strict
  training targets solved by r16, cumulative: 69 / 46 / 41 (of 123).
- **General ability:** held-out greedy (5,000) 0.917 / 0.945 / 0.929 (non-σ 0.937 / 0.948 / 0.959, σ 0.786 / 0.925 / 0.739);
  textbook72 (scoring only) pend 31 / 30 / 29 (dev58 26 / 25 / 23, train14 5 / 5 / 6), r16 53 / 53 / 44 (dev58 43 / 42 / 35,
  train14 10 / 11 / 9); holdout250 pass@256 pend 179 / 189 / 197, r16 240 / 238 / 234.
- **Cost:** c_base on the 322 (A40, batch 1,024) 6.54 / 10.35 / 7.18 ms; K_train(16) 22,018 / 15,152 / 20,903 (s1's timing is
  1.4–1.6× the others'; no dose number uses K). r16 read cut-offs 0.33 / 0.16 / 1.42 %.
- **Addendum 5 expectations:** round-1 strict targets 3–15 — miss on 3 / 3; σ proofs at r1 50–500 — hit 3 / 3; free positive
  reductio from r1 on ≥ 2 / 3 — hit 3 / 3; ≥ 1 family at r16 on ≥ 2 / 3 — hit 3 / 3; contraposition_conv the most likely —
  hit; r16 members between the knockout and full medians — 2 / 3 (s0 above).

### Along the ladder: log p of the known σ proofs (post-ladder scoring; `artifacts/coe/score/rounds_*/summary.json`, `coe/coe_score_summary.py`)
Teacher-forced log p (T 0.8, one name base; subtract ln 33 for a lower bound) of 9,501 known Lean-accepted proofs of the
strict held-out members (`data/coe/known_targets_heldout.jsonl.gz`, from the old full ladders); median over 101 members of
each member's best proof; checkpoints pend / r4 / r8 / r12 / r16.
- knockout s0 −33.4 / −28.3 / −28.8 / −31.6 / −29.7; s1 −26.0 / −33.6 / −34.6 / −32.4 / −33.6 (its best member −7.9 → −4.2); s2 −35.7 / −27.2 / −30.4 / −30.8 / −34.5; s3 −33.8 / −25.7 / −29.4 / −30.3 /
  −33.9; s4 −36.0 / −34.2 / −38.2 / −34.6 / −36.1; s5 −31.5 / −32.6 / −30.5 / −32.3 / −35.5. The worst step of that proof (opening
  the ¬G box on 100 / 101 members) −18.0 to −21.6 at pend, −24.2 to −27.3 at r16.
- full s3 −15.4 / −4.4 / −4.8 / −5.5 / −5.1; s4 −20.9 / −15.9 / −16.7 / −16.9 / −19.0; s5 −20.4 / −16.2 / −20.6 / −19.7 / −16.1.
- 1 % dose s0 −25.3 / −12.4 / −9.8 / −9.1 / −8.7; s1 −18.9 / −17.3 / −19.7 / −18.3 / −15.9; s2 −24.5 / −21.8 / −22.3 / −21.7 / −22.8.

### Replay check (pre-registered; `artifacts/coe/rounds/mix_la_ko_s*.json`, `coe/coe_mixcheck.py`)
Every fine-tune mix record of the knockout ladders, rounds 1–16, attributed by set membership (in K12⁻ → replay; in K12 but
not K12⁻ → leak; neither → the ladder's own RL proof) and classified: knockout s0, s2, s3, s4, s5 — 1.38–1.39 M records each
(20,000 replay per round), s1 rounds 1–24 — 2.09 M: **0 replay records with σ / σ via IMPI / σ⁺ / the lemma route, 0 leaked
K12 records** on 6 / 6 seeds; σ-like records from RL 3,348–6,964 per 16-round ladder, 9,416 on s1's 24 rounds (counted with
the mix's repeats).

### Knockout s1, rounds 17–24 (exploratory; Addendum 6 item 1; sources `artifacts/coe/rounds/la_ko_s1.json`, `artifacts/coe/eval/r{16,20,24}_ko_s1_x0.json[l.gz]`)
Model: M12⁻ s1, `ckpts/coe/ladder/la_ko_s1_r{17..24}.pt` (resumed at r17 and again at r21 after the r20 read; A40, batch 1,024).
- Free positive reductio proofs accepted per round: r9–r16 1 / 0 / 0 / 2 / 5 / 10 / 5 / 11; r17–r24 29 / 37 / 49 / 74 / 81 / 74 /
  98 / 123. Strict σ-covered training targets solved, cumulative: r16 5, r20 8, **r21–r24 9** (all contraposition_conv,
  share 9 / 27 = 0.33). Held-out strict members first solved in the k 32 transfer samples: 5 by r19, none after.
- Plain k 256 reads, strict held-out members solved: r16 2, r20 5, **r24 5** (the same five: contraposition_conv `1019`, `1246`,
  `1460`, `2256` and `la_transfer_916`); successes per 256 on them r16 → r20 → r24: 0 → 32 → 214, 0 → 23 → 126, 108 → 205 → 189,
  0 → 47 → 177, 10 → 14 → 33. No family at the bar. r20 accepted proofs of these members: σ 32, σ⁺-only 24, lemma route 7.
- Addendum 6 expectations: contraposition_conv training share 0.3–0.8 at r24 — hit (0.33); 2–12 of its 18 held-out members —
  hit (4); at the bar with probability ≈ 0.3 — no; no other family at the bar — hit.

### The executor's offline Lean re-check (`coe/coe_recheck.py` → `artifacts/coe/recheck.json`; not a review)
Lean 4 core through `lean_judge.judge_many` on the stored ND proofs (translated by `nd2lean`), strict held-out members only:
every knockout proof in the plain reads (pend, r8, r16, r20, r24; x0 and x1) 424 / 424 accepted; every knockout base large-k
success 13 / 13; every Phase 3a proof 25 / 25; a seeded sample of 50 per full r16 read file 450 / 450 and per dose r16 read
50 × 3 = 150 / 150. **1,062 / 1,062 accepted; the same proofs with the conclusion G replaced by ¬G: 1,062 / 1,062 rejected.**

### Compute (sources `artifacts/coe/compute.{md,json}` (`coe/coe_compute.py`, 3,817 compute rows in `artifacts/create-or-elicit/registry/`), `artifacts/coe/pod_hours.tsv` (`coe/coe_podhours.py`))
- **Paid:** 16 pods, **309.34 pod-hours, $182.50** (budget $190 / 330 h after Dan's extension; 15 NVIDIA A40 at $0.59 / h and
  one RTX A6000 0.27 h). Per arm: full s3–s5 22.1–24.3 h ($13.0–14.3) each; knockout s0, s2–s5 22.7–27.5 h ($13.4–16.2), s1
  34.7 h ($20.5, with the extension); dose s0–s2 16.7–18.2 h ($9.8–10.7); shared pods (Phase 0.2, old-seed reads, Phase 2 / 2b)
  26.0 h ($15.3).
- **Process GPU-hours (A40) by activity, all models:** pretraining 4.3 (1,200 s per seed), RL ladders 191.2 (16 rounds
  ≈ 13.5–16.3 h per seed; knockout s1 22.4 with 24 rounds), plain reads 106.8, guided reads 74.9, timing 3.6, knockout
  certificates 12.8, standard A 15.3, Phase 2 / 2b 4.2, Phase 3a 4.3, other 2.4 (held-out greedy, the `la_transfer_916`
  large-k runs, scoring, the Phase 0.2 replica); total 419.9 (processes sharing a card each count in full). Generated tokens per 16-round seed with its reads ≈ 1.0–1.7 × 10⁹.

### Where the files are
- Checkpoints: `hf://buckets/dan-pandori/nd-rl/create-or-elicit/ckpts/coe/` (`stage1_{full,ko,dose1}_s{S}.pt` 12,
  `ladder/la_{full,ko,dose1}_s{S}_r{R}.pt` 200, `p3a/ko_s{S}_{seeded,control}.pt`), uploaded on save; each registry row
  names its checkpoint's md5.
- Bulk artifacts (read rows, large-k chunks, scores, ladder found / mix files, registry rows): same bucket prefix, same
  repository paths; the files kept locally are listed with sha256 in `artifacts/MANIFEST.jsonl` (`python3 fetch_artifacts.py
  <path>`). Data: `data/coe/README.md`.

## kalmar-pretrain (2026-10-19 / 20, executor; UNREVIEWED)

**Models (every number here names one of these):**
- **KAL-D s0–s2** (data-matched): `ckpts/kalmar/stage1_kalD_s{0,1,2}.pt` (bucket `kalmar-pretrain/ckpts/kalmar/`).
  - Network and recipe: 9,560,832-param ALiBiGPT 6 × 384, `lean_staten`, `state_train.py --recipe best`, from scratch.
  - Data: K12-Kalmár sl (`data/kalmar/train_kal_sl.jsonl`, 155,000 Kalmár proofs of K12's theorems, md5 1e4cebf5…).
  - Training: 656,285 steps (3.675 epochs of pairs, the control's mean), ≈ 10 h on an RTX 3090.
  - md5: d2fdb9d9 / 166acebb / 396586c2 (from each run's upload line in `artifacts/kalmar/logs/train_kalD_s*.log`).
  - Snapshots `_step{24020,100000,200000,350000,500000}` are mid-schedule checkpoints.
- **KAL-C s0–s2** (compute-matched): same recipe and data, 24,020 steps (the control's mean; 0.13 epochs).
  `ckpts/kalmar/stage1_kalC_s{0,1,2}.pt`, md5 2c6bbc9b / 8dabdd30 / 8992b636.
- **control s0–s2:** best-state's best-cap12 Stage-1 `stage1_best12_s{0,1,2}_b1200.pt` (bucket `best-state/ckpts/bs/`).
  - Same network and recipe, from scratch on K12 (`data/kh/train_k12.jsonl`, md5 800b5486…).
  - 1,200 s on an A40, 23,951–24,123 steps; md5 9c436c35 / f7ae9a9e / 354c4428 (md5sum of the bucket copies, on the
    VPS at 01:35 and on kal-5 at 02:13, 2026-10-19; both matched).
- **Ladder (EI r1, r2):** `ckpts/kalmar/ladder/la_kal_ei_s0_r{1,2}.pt`, md5 aa8519c4 / 80ef2213. EI from KAL-D s0
  (pre-registration Addendum 1); the ladder stopped after round 3's sampling, so there is no r3.
- **KAL-D+A s0–s2** (exploratory, Addendum 3): `ckpts/kalmar/anneal/kalDA_s{0,1,2}.pt`, md5 4516a1f5 / a2ee6578 /
  cbf7a110. KAL-D plus the ladder's fine-tune on 20,000 replayed K12-Kalmár records, no EI proofs (see the
  exploratory section).

**Protocol.**
- **Checker.** Lean alone decides: the literal sampled text, `lean_gate` / `lean_judge`; `nd_verify` is never called.
  L_true labels are ND-derived upper bounds under Lean.
- **Caps.** `max_steps` 1,024 actions; `max_action` 512 tokens.
- **Greedy and teacher-forced reads.** Batch 1,024, every arm, on RTX 3090s. The 24 k / 100 k snapshot copies were
  re-read on an A40.
  - Deviation (Addendum 3 said 3090s): KAL-D+A s0 / s2 and EI r1 / r2 were read on A40s, as no 3090 was in stock
    (log 00:12, 10-20); KAL-D+A s1 on a 3090.
  - The A40 and 3090 copies of four snapshot greedy reads differed by at most 1 theorem of 1,200 (77 vs 78; log
    04:50 / 05:15, 10-19).
- **Sampled reads.**
  - T 0.8, sample seed 1.
  - Batch 2,048 for control and KAL-C. Batch 1,024 for KAL-D and the ladder: 2,048 OOMs on KAL-D's long attempts
    (Addendum 2); the batch effect is checked below.
  - Guided = `guided_eval.py --arm logical` (≤ 10 rejections per attempt).
  - pass@k is the unbiased estimator from the k 32 reads.
  - pass@256 is reported for the control only (stored best-state reads where they exist). KAL-D's k extension was
    dropped by the spend gate.
- **Aggregation.** Per-seed values, then the IQM with a bootstrap 95 % interval over seeds; at n = 3 the IQM is the
  mean.
- **Code.** Tables: `python3 kalmar/analysis.py` → `artifacts/kalmar/analysis_stdout.txt`, `artifacts/kalmar/summary.json`.

#### Data (sources `artifacts/kalmar/build_{sl,pb}.json`, `artifacts/kalmar/stats_k12_vs_kal.json`, `artifacts/kalmar/lean_check_train_sl.json`; details `data/kalmar/README.md`)

| per proof (155,000 K12 theorems) | K12 (its own proofs) | K12-Kalmár sl (trained) | K12-Kalmár pb (prover's layout) |
|---|---|---|---|
| ND lines mean / max | 7.0 / 12 | 107.9 / 527 | 150.6 / 626 |
| state-env actions mean / max | 8.0 / 13 | 108.9 / 528 | 151.6 / 627 |
| (state, action) pairs | 1,239,995 | 16,876,247 | 23,504,837 |
| pair tokens mean / total | 775 / 120 M | 21,121 / 3.27 B | 28,334 / 4.39 B |
| ND box depth mean / max | 1.1 / 2 | 4.2 / 6 | — |
| longest state per proof mean / max (tokens) | 104.5 / 386 | 229.3 / 655 | — / 655 |
| term size (lean_check inference nodes) mean / max | 4.5 / 14 | 92.2 / 423 | 135.0 / 522 |
| Lean (literal canonical text) | — | **155,000 / 155,000** | 30 / 30 (test sample) |

Decompose and replay failures: 0 / 155,000. State → action conflicts: 0 over 3.37 M states. Builder tests
(`kalmar/test_kalmar.py`): Lean 60 / 60; negative controls 60 / 60 rejected.

#### E1 teacher-forced agreement on tf1200 (% of states; source `artifacts/kalmar/tf/<model>__tf1200.json`)

| step type | KAL-D | KAL-C | control |
|---|---|---|---|
| all states | 94.6 / 93.8 / 95.0 (94.5 [93.8, 95.0]) | 93.8 / 93.2 / 93.4 (93.5 [93.2, 93.8]) | 27.8 / 30.2 / 22.8 (27.0 [22.8, 30.2]) |
| premise line | 87.0 / 93.1 / 94.3 (91.5) | 94.7 / 95.3 / 96.0 (95.3) | 99.9 / 99.9 / 99.8 (99.9) |
| X ∨ ¬X derivation | 99.9 / 99.1 / 99.8 (99.6) | 99.8 / 98.1 / 98.9 (98.9) | 13.7 / 11.0 / 11.2 (12.0) |
| split (∨E) | 96.6 / 97.7 / 96.7 (97.0) | 97.7 / 96.8 / 97.7 (97.4) | 0.2 / 0.9 / 0.1 (0.4) |
| ex falso | 98.6 / 98.2 / 98.4 (98.4) | 99.3 / 98.5 / 98.0 (98.6) | 0.8 / 2.7 / 2.9 (2.1) |
| leaf ∧ true | 60.4 / 61.5 / 74.4 (65.4) | 61.6 / 58.1 / 59.6 (59.8) | 7.3 / 14.2 / 11.1 (10.9) |
| leaf ∧ false | 93.2 / 89.4 / 89.8 (90.8) | 90.2 / 91.4 / 90.5 (90.7) | 0.9 / 0.4 / 1.6 (1.0) |
| leaf ∨ true | 72.3 / 71.5 / 79.0 (74.3) | 73.4 / 66.2 / 69.2 (69.6) | 11.1 / 17.3 / 10.3 (12.9) |
| leaf ∨ false | 92.7 / 89.5 / 92.5 (91.6) | 91.6 / 90.7 / 90.7 (91.0) | 1.3 / 0.1 / 1.4 (0.9) |
| leaf → (B true) | 81.8 / 83.1 / 85.4 (83.5) | 83.0 / 80.3 / 81.5 (81.6) | 17.2 / 19.7 / 12.5 (16.5) |
| leaf → (A false) | 89.7 / 89.0 / 89.4 (89.4) | 87.5 / 83.3 / 77.0 (82.6) | 4.6 / 7.4 / 3.9 (5.3) |
| leaf → false | 92.9 / 91.8 / 92.1 (92.3) | 87.2 / 88.7 / 90.1 (88.7) | 0.7 / 0.3 / 0.8 (0.6) |
| leaf ¬¬A | 92.1 / 89.3 / 91.0 (90.8) | 84.5 / 86.8 / 86.8 (86.1) | 1.5 / 1.4 / 2.0 (1.6) |
| leaf ¬⊥ | 64.0 / 77.0 / 81.5 (74.2) | 75.7 / 88.7 / 81.1 (81.8) | 0.2 / 0.2 / 0.0 (0.1) |
| box close | 99.7 / 98.6 / 99.4 (99.2) | 98.9 / 99.4 / 99.6 (99.3) | 66.4 / 73.1 / 52.8 (64.1) |
| 1 atom | 92.7 / 91.8 / 86.1 (90.2) | 91.7 / 89.7 / 89.0 (90.1) | 48.8 / 47.9 / 46.4 (47.7) |
| 2 atoms | 94.5 / 94.1 / 95.2 (94.6) | 93.8 / 92.9 / 93.3 (93.4) | 39.7 / 39.9 / 35.8 (38.5) |
| 3 atoms | 95.0 / 94.4 / 95.7 (95.0) | 93.9 / 93.7 / 93.5 (93.7) | 31.3 / 32.5 / 25.0 (29.6) |
| 4 atoms | 94.5 / 93.5 / 95.1 (94.4) | 93.9 / 93.3 / 93.6 (93.6) | 21.5 / 25.3 / 16.7 (21.1) |

Records whose every state agrees (of 1,200): KAL-D [170, 164, 192]; KAL-C [123, 81, 126]; control [0, 0, 0]

By box depth (frames open before the action), KAL-D: 0: 97.0 / 97.9 / 97.9 (97.6); 1: 98.7 / 97.8 / 98.0 (98.2); 2: 95.7 / 95.4 / 95.4 (95.5); 3: 91.9 / 91.7 / 93.0 (92.2); 4: 89.6 / 87.7 / 90.8 (89.4); 5: 98.8 / 97.9 / 98.8 (98.5); 6: 98.8 / 100.0 / 99.0 (99.3)

By position decile, KAL-D: 0: 98.5 / 97.9 / 99.2 (98.5); 1: 97.4 / 97.1 / 97.8 (97.4); 2: 94.6 / 93.8 / 95.1 (94.5); 3: 93.3 / 92.4 / 93.8 (93.2); 4: 92.8 / 91.9 / 93.4 (92.7); 5: 93.6 / 92.4 / 93.3 (93.1); 6: 93.3 / 92.0 / 93.3 (92.9); 7: 93.2 / 92.6 / 93.6 (93.2); 8: 93.5 / 92.8 / 93.9 (93.4); 9: 95.9 / 95.0 / 96.5 (95.8)

#### KAL-D learning curve (snapshots are mid-schedule checkpoints; source `artifacts/kalmar/{tf,free}/kalD_s<S>_step<N>__*`)

| step | TF agreement % | greedy tf1200 valid % |
|---|---|---|
| 24,020 | 87.5 / 86.4 / 85.8 (86.6) | 6.5 / 6.2 / 7.0 (6.6) |
| 100,000 | 87.1 / 87.8 / 88.1 (87.7) | 14.4 / 6.7 / 9.4 (10.2) |
| 200,000 | 89.9 / 87.5 / 87.7 (88.4) | 11.0 / 12.7 / 5.9 (9.9) |
| 350,000 | 90.8 / 91.2 / 90.6 (90.9) | 14.1 / 19.5 / 18.3 (17.3) |
| 500,000 | 93.4 / 92.6 / 92.8 (92.9) | 23.0 / 25.3 / 20.8 (23.0) |
| 656,285 | 94.6 / 93.8 / 95.0 (94.5) | 33.1 / 29.1 / 35.6 (32.6) |

#### Compounding (teacher-forced; theorems whose every state agrees, observed vs independent errors)

| algorithm actions | n | KAL-D observed % | KAL-D independent % | KAL-D disagreements / theorem | KAL-C observed % |
|---|---|---|---|---|---|
| 0-49 | 261 | 23.4 / 22.2 / 18.4 (21.3) | 22.1 / 19.8 / 28.1 (23.3) | 1.79 / 2.01 / 2.78 (2.19) | 17.6 / 11.5 / 16.9 (15.3) |
| 50-99 | 377 | 18.6 / 16.7 / 24.1 (19.8) | 5.5 / 3.8 / 6.5 (5.3) | 3.21 / 3.64 / 2.91 (3.26) | 13.8 / 10.1 / 13.3 (12.4) |
| 100-149 | 212 | 12.3 / 13.7 / 13.2 (13.1) | 0.9 / 0.4 / 0.9 (0.7) | 6.15 / 6.49 / 5.16 (5.93) | 7.5 / 5.2 / 10.4 (7.7) |
| 150-199 | 162 | 5.6 / 8.0 / 13.6 (9.1) | 0.3 / 0.1 / 0.2 (0.2) | 8.17 / 10.17 / 6.81 (8.38) | 4.3 / 0.6 / 4.9 (3.3) |
| 200-299 | 145 | 2.8 / 0.7 / 1.4 (1.6) | 0.0 / 0.0 / 0.0 (0.0) | 11.43 / 13.41 / 9.93 (11.59) | 1.4 / 0.7 / 1.4 (1.1) |
| 300-… | 43 | 0.0 / 0.0 / 2.3 (0.8) | 0.0 / 0.0 / 0.0 (0.0) | 34.49 / 39.14 / 33.56 (35.73) | 0.0 / 0.0 / 0.0 (0.0) |

#### Leaf steps by the depth of the formula the step writes (TF agreement %)

| depth | KAL-D | KAL-C | control |
|---|---|---|---|
| 0 | 98.6 / 98.5 / 98.2 (98.4) | 98.5 / 96.5 / 97.0 (97.3) | 2.1 / 1.3 / 3.3 (2.2) |
| 1 | 71.9 / 78.1 / 79.0 (76.4) | 73.6 / 69.0 / 72.1 (71.6) | 1.8 / 2.8 / 5.8 (3.5) |
| 2 | 81.0 / 72.0 / 78.5 (77.2) | 69.8 / 74.4 / 70.2 (71.5) | 3.0 / 5.0 / 2.9 (3.6) |
| 3 | 86.8 / 84.9 / 88.9 (86.9) | 84.7 / 84.1 / 82.5 (83.8) | 8.3 / 9.8 / 6.4 (8.2) |
| 4 | 83.7 / 79.3 / 85.5 (82.8) | 80.6 / 80.9 / 81.8 (81.1) | 15.7 / 18.0 / 13.2 (15.7) |
| 5 | 74.7 / 78.2 / 77.3 (76.7) | 80.4 / 76.7 / 79.0 (78.7) | 26.2 / 36.8 / 7.5 (23.5) |
| 6+ | 61.6 / 67.8 / 66.5 (65.3) | 63.7 / 53.8 / 51.0 (56.2) | 18.3 / 27.0 / 2.4 (15.9) |

#### E2 greedy free generation on tf1200 (% of theorems; Lean on the literal text; source `artifacts/kalmar/free/<model>__tf1200_greedy.json`)

| | KAL-D valid | KAL-D exact Kalmár | KAL-C valid | KAL-C exact Kalmár | control valid | control exact Kalmár |
|---|---|---|---|---|---|---|
| all | 33.1 / 29.1 / 35.6 (32.6) | 14.1 / 13.7 / 16.3 (14.7) | 26.9 / 14.1 / 22.2 (21.1) | 10.2 / 6.6 / 10.6 (9.1) | 91.8 / 94.4 / 90.5 (92.2) | 0.0 / 0.0 / 0.0 (0.0) |
| atoms=1 | 49.3 / 30.7 / 30.7 (36.9) | 19.3 / 17.3 / 8.0 (14.9) | 32.0 / 20.0 / 25.3 (25.8) | 12.7 / 6.7 / 12.7 (10.7) | 90.0 / 91.3 / 91.3 (90.9) | 0.0 / 0.0 / 0.0 (0.0) |
| atoms=2 | 39.1 / 33.7 / 38.6 (37.1) | 19.7 / 17.4 / 22.0 (19.7) | 31.4 / 15.4 / 26.3 (24.4) | 14.0 / 10.0 / 14.0 (12.7) | 93.4 / 93.7 / 91.4 (92.9) | 0.0 / 0.0 / 0.0 (0.0) |
| atoms=3 | 29.4 / 28.9 / 39.7 (32.7) | 13.7 / 14.3 / 19.7 (15.9) | 26.9 / 14.9 / 20.6 (20.8) | 10.9 / 7.4 / 10.6 (9.6) | 90.0 / 94.3 / 89.4 (91.2) | 0.0 / 0.0 / 0.0 (0.0) |
| atoms=4 | 23.7 / 24.0 / 30.6 (26.1) | 6.6 / 7.7 / 10.9 (8.4) | 20.3 / 9.4 / 18.6 (16.1) | 4.6 / 2.3 / 6.3 (4.4) | 92.9 / 96.6 / 90.3 (93.2) | 0.0 / 0.0 / 0.0 (0.0) |

Valid deviations (Lean-valid, not the algorithm's), % of theorems, and the shorter-than-algorithm part: KAL-D 19.0 / 15.4 / 19.2 (17.9) (shorter 11.2 / 9.8 / 13.2 (11.4)); KAL-C 16.8 / 7.5 / 11.7 (12.0) (shorter 10.5 / 4.8 / 7.2 (7.5)); control 91.8 / 94.4 / 90.5 (92.2) (shorter 91.8 / 94.4 / 90.5 (92.2))

E3 (T 0.8, k 8, tf1200; % of attempts): KAL-D valid 18.3 / 13.8 / 16.4 (16.2), exact Kalmár 6.8 / 6.0 / 6.2 (6.3); KAL-C valid 12.0 / 6.3 / 8.7 (9.0), exact Kalmár 4.0 / 2.4 / 3.9 (3.4); control valid 86.3 / 88.9 / 86.2 (87.2), exact Kalmár 0.0 / 0.0 / 0.0 (0.0)

#### E4 / E5 solve rates (theorems solved, unbiased pass@k; source `artifacts/kalmar/eval/<model>_{plain,logical}_k32.rows.jsonl.gz`)

| set (n) | arm | plain pass@1 | plain pass@8 | plain pass@32 | guided pass@1 | guided pass@32 | plain pass@256 |
|---|---|---|---|---|---|---|---|
| holdout250 (250) | KAL-D | 5.9 / 3.1 / 6.7 (5.2) | 21.1 / 12.2 / 24.5 (19.3) | 35.0 / 24.0 / 41.0 (33.3) | 15.7 / 11.1 / 19.6 (15.5) | 53.0 / 58.0 / 66.0 (59.0) | — |
| holdout250 (250) | KAL-C | 1.9 / 2.3 / 1.0 (1.7) | 11.2 / 11.2 / 5.6 (9.3) | 24.0 / 19.0 / 11.0 (18.0) | 7.8 / 8.4 / 5.5 (7.2) | 44.0 / 52.0 / 28.0 (41.3) | — |
| holdout250 (250) | control | 65.8 / 74.1 / 81.1 (73.7) | 137.2 / 143.3 / 138.5 (139.6) | 165.0 / 170.0 / 160.0 (165.0) | 119.5 / 133.2 / 131.1 (127.9) | 194.0 / 205.0 / 196.0 (198.3) | 184 / 195 / 182 (187) |
| rr600 (600) | KAL-D | 2.0 / 0.9 / 2.5 (1.8) | 9.0 / 4.7 / 13.1 (8.9) | 16.0 / 10.0 / 25.0 (17.0) | 9.9 / 7.5 / 14.3 (10.6) | 69.0 / 50.0 / 79.0 (66.0) | — |
| rr600 (600) | KAL-C | 0.4 / 0.7 / 0.2 (0.4) | 2.1 / 3.9 / 1.0 (2.4) | 6.0 / 9.0 / 2.0 (5.7) | 3.6 / 8.3 / 3.2 (5.0) | 34.0 / 48.0 / 37.0 (39.7) | — |
| rr600 (600) | control | 57.2 / 46.2 / 35.5 (46.3) | 191.2 / 156.3 / 124.7 (157.4) | 298.0 / 241.0 / 198.0 (245.7) | 186.4 / 176.7 / 160.2 (174.4) | 451.0 / 417.0 / 408.0 (425.3) | 401 / 356 / 311 (356) (Q 13–16: 271 / 237 / 216 (241)) |
| ge17 (70) | KAL-D | 0.0 / 0.0 / 0.1 (0.0) | 0.0 / 0.0 / 0.5 (0.2) | 0.0 / 0.0 / 2.0 (0.7) | 0.2 / 0.2 / 0.6 (0.3) | 3.0 / 1.0 / 8.0 (4.0) | — |
| ge17 (70) | KAL-C | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.2 / 0.2 / 0.0 (0.1) | 3.0 / 4.0 / 1.0 (2.7) | — |
| ge17 (70) | control | 1.1 / 1.6 / 0.8 (1.2) | 6.0 / 7.5 / 4.3 (5.9) | 13.0 / 15.0 / 12.0 (13.3) | 10.8 / 8.5 / 9.2 (9.5) | 43.0 / 39.0 / 38.0 (40.0) | 25 / 22 / 19 (22) |
| long2 (21) | KAL-D | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.4 / 0.2 / 0.7 (0.4) | 5.0 / 3.0 / 2.0 (3.3) | — |
| long2 (21) | KAL-C | 0.2 / 0.0 / 0.0 (0.1) | 0.9 / 0.0 / 0.0 (0.3) | 1.0 / 0.0 / 0.0 (0.3) | 0.4 / 0.1 / 0.0 (0.2) | 3.0 / 2.0 / 1.0 (2.0) | — |
| long2 (21) | control | 0.1 / 0.1 / 0.0 (0.1) | 1.0 / 0.4 / 0.2 (0.6) | 4.0 / 1.0 / 1.0 (2.0) | 3.7 / 2.3 / 1.8 (2.6) | 15.0 / 13.0 / 10.0 (12.7) | 10 / 5 / 4 (6) |
| candidate_v0 (87) | KAL-D | 6.0 / 3.5 / 4.3 (4.6) | 14.8 / 11.9 / 16.8 (14.5) | 19.0 / 21.0 / 24.0 (21.3) | 10.9 / 8.6 / 13.3 (10.9) | 31.0 / 31.0 / 40.0 (34.0) | — |
| candidate_v0 (87) | KAL-C | 1.6 / 0.5 / 1.7 (1.2) | 7.0 / 2.7 / 7.8 (5.8) | 11.0 / 5.0 / 14.0 (10.0) | 6.0 / 5.4 / 4.8 (5.4) | 30.0 / 21.0 / 16.0 (22.3) | — |
| candidate_v0 (87) | control | 10.5 / 10.3 / 8.5 (9.8) | 25.3 / 22.5 / 20.2 (22.7) | 33.0 / 28.0 / 28.0 (29.7) | 19.3 / 18.6 / 20.4 (19.4) | 46.0 / 44.0 / 46.0 (45.3) | 36 / 39 / 37 (37) |
| candidate_v1 (72) | KAL-D | 1.8 / 0.8 / 1.2 (1.2) | 5.3 / 2.6 / 4.3 (4.1) | 9.0 / 6.0 / 8.0 (7.7) | 3.0 / 2.1 / 3.2 (2.8) | 13.0 / 15.0 / 13.0 (13.7) | — |
| candidate_v1 (72) | KAL-C | 0.7 / 0.5 / 0.2 (0.5) | 2.5 / 1.0 / 1.8 (1.8) | 4.0 / 1.0 / 5.0 (3.3) | 1.3 / 2.7 / 0.7 (1.6) | 8.0 / 10.0 / 9.0 (9.0) | — |
| candidate_v1 (72) | control | 6.9 / 8.2 / 8.1 (7.7) | 15.4 / 14.7 / 16.5 (15.5) | 23.0 / 19.0 / 24.0 (22.0) | 14.7 / 14.4 / 17.3 (15.5) | 35.0 / 32.0 / 38.0 (35.0) | 31 / 28 / 32 (30) |
| batch3 (14) | KAL-D | 1.2 / 0.6 / 0.3 (0.7) | 3.8 / 1.2 / 2.1 (2.4) | 7.0 / 2.0 / 4.0 (4.3) | 2.5 / 1.3 / 2.1 (2.0) | 7.0 / 4.0 / 7.0 (6.0) | — |
| batch3 (14) | KAL-C | 0.2 / 0.0 / 0.1 (0.1) | 1.1 / 0.0 / 0.6 (0.6) | 2.0 / 0.0 / 1.0 (1.0) | 1.0 / 0.7 / 0.3 (0.6) | 4.0 / 2.0 / 3.0 (3.0) | — |
| batch3 (14) | control | 1.1 / 1.4 / 1.1 (1.2) | 3.0 / 3.3 / 3.0 (3.1) | 4.0 / 4.0 / 6.0 (4.7) | 3.5 / 3.3 / 4.6 (3.8) | 7.0 / 8.0 / 7.0 (7.3) | 5 / 4 / 7 (5) |
| hand_proved_14 (14) | KAL-D | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | — |
| hand_proved_14 (14) | KAL-C | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | — |
| hand_proved_14 (14) | control | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0 / 0 / 0 (0) |
| textbook72 (72) | KAL-D | 6.3 / 5.6 / 6.0 (6.0) | 15.2 / 13.9 / 15.1 (14.7) | 21.0 / 18.0 / 20.0 (19.7) | 12.1 / 11.8 / 15.3 (13.0) | 30.0 / 30.0 / 33.0 (31.0) | — |
| textbook72 (72) | KAL-C | 2.3 / 0.7 / 1.5 (1.5) | 8.8 / 3.6 / 7.0 (6.5) | 14.0 / 5.0 / 11.0 (10.0) | 7.0 / 5.7 / 4.8 (5.8) | 26.0 / 19.0 / 18.0 (21.0) | — |
| textbook72 (72) | control | 10.5 / 10.2 / 12.0 (10.9) | 19.1 / 17.2 / 20.1 (18.8) | 25.0 / 22.0 / 24.0 (23.7) | 16.8 / 16.4 / 18.0 (17.1) | 35.0 / 37.0 / 34.0 (35.3) | 32 / 27 / 27 (29) |
| g1_premises (200) | KAL-D | 5.2 / 1.6 / 2.2 (3.0) | 19.3 / 7.2 / 9.8 (12.1) | 35.0 / 15.0 / 17.0 (22.3) | 18.7 / 10.2 / 9.6 (12.8) | 54.0 / 40.0 / 35.0 (43.0) | — |
| g1_premises (200) | KAL-C | 0.9 / 0.5 / 0.4 (0.6) | 4.2 / 2.5 / 2.4 (3.0) | 7.0 / 5.0 / 6.0 (6.0) | 4.2 / 5.6 / 3.1 (4.3) | 25.0 / 38.0 / 24.0 (29.0) | — |
| g1_premises (200) | control | 0.0 / 4.8 / 13.3 (6.0) | 0.0 / 8.3 / 21.6 (10.0) | 0.0 / 11.0 / 26.0 (12.3) | 0.4 / 10.6 / 25.1 (12.0) | 3.0 / 21.0 / 50.0 (24.7) | 1 / 13 / 30 (15) |
| g2_large (240) | KAL-D | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.2 / 0.4 / 0.1 (0.2) | 2.0 / 2.0 / 1.0 (1.7) | — |
| g2_large (240) | KAL-C | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.2 / 0.0 (0.1) | 1.0 / 4.0 / 0.0 (1.7) | — |
| g2_large (240) | control | 0.0 / 1.0 / 0.4 (0.5) | 0.0 / 1.2 / 1.5 (0.9) | 0.0 / 2.0 / 3.0 (1.7) | 0.7 / 1.1 / 1.7 (1.1) | 6.0 / 3.0 / 5.0 (4.7) | 1 / 3 / 5 (3) |
| g3_classical (106) | KAL-D | 4.5 / 3.3 / 4.3 (4.0) | 14.7 / 11.1 / 13.2 (13.0) | 19.0 / 18.0 / 17.0 (18.0) | 9.4 / 9.2 / 8.8 (9.1) | 29.0 / 34.0 / 26.0 (29.7) | — |
| g3_classical (106) | KAL-C | 1.4 / 0.8 / 0.2 (0.8) | 7.5 / 4.0 / 1.6 (4.4) | 14.0 / 7.0 / 4.0 (8.3) | 4.7 / 4.3 / 0.8 (3.3) | 22.0 / 23.0 / 7.0 (17.3) | — |
| g3_classical (106) | control | 3.8 / 2.4 / 11.7 (5.9) | 8.7 / 6.3 / 18.9 (11.3) | 12.0 / 9.0 / 19.0 (13.3) | 5.7 / 5.5 / 15.5 (8.9) | 16.0 / 12.0 / 19.0 (15.7) | 17 / 14 / 20 (17) |

#### Plain pass@32 by atom count and by the algorithm's proof length (pooled: holdout250 + rr600 + ge17 + long2 + release, n = 1,128; % of theorems)

| stratum | KAL-D | KAL-C | control |
|---|---|---|---|
| 1 atom(s) | 29.4 / 29.4 / 35.3 (31.4) | 23.5 / 11.8 / 0.0 (11.8) | 52.9 / 70.6 / 47.1 (56.9) |
| 2 atom(s) | 23.4 / 16.5 / 25.9 (21.9) | 15.8 / 10.8 / 11.4 (12.7) | 51.9 / 44.9 / 48.7 (48.5) |
| 3 atom(s) | 8.2 / 5.0 / 10.3 (7.8) | 3.9 / 2.7 / 3.0 (3.2) | 45.3 / 41.7 / 34.6 (40.5) |
| 4 atom(s) | 1.6 / 1.9 / 2.3 (1.9) | 0.4 / 0.6 / 0.4 (0.5) | 48.6 / 41.2 / 37.4 (42.4) |
| 0-99 actions | 19.8 / 13.7 / 23.4 (18.9) | 13.3 / 9.4 / 9.0 (10.6) | 55.8 / 50.7 / 47.8 (51.4) |
| 100-149 actions | 7.7 / 5.3 / 9.3 (7.4) | 3.0 / 1.7 / 2.0 (2.2) | 43.3 / 39.0 / 32.7 (38.3) |
| 150-199 actions | 1.1 / 1.4 / 1.8 (1.4) | 0.4 / 1.1 / 0.4 (0.6) | 52.7 / 42.8 / 36.4 (43.9) |
| 200-299 actions | 2.0 / 2.0 / 2.4 (2.1) | 0.4 / 0.0 / 0.4 (0.3) | 41.6 / 37.6 / 36.4 (38.5) |
| 300-1024 actions | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 11.8 / 29.4 / 23.5 (21.6) |

#### Generalisation and long sets, greedy (% of theorems valid / exact Kalmár)

| set | KAL-D | KAL-C | control |
|---|---|---|---|
| g1_premises | 5.5 / 3.5 / 4.0 (4.3) / 0.0 / 0.0 / 0.0 (0.0) | 3.0 / 0.5 / 1.0 (1.5) / 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 3.0 / 8.5 (3.8) / 0.0 / 0.0 / 0.0 (0.0) |
| g2_large | 0.0 / 0.0 / 0.0 (0.0) / 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) / 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.4 / 0.4 (0.3) / 0.0 / 0.0 / 0.0 (0.0) |
| g3_classical | 10.4 / 8.5 / 11.3 (10.1) / 6.6 / 5.7 / 5.7 (6.0) | 0.9 / 3.8 / 1.9 (2.2) / 0.9 / 1.9 / 0.0 (0.9) | 3.8 / 2.8 / 15.1 (7.2) / 0.0 / 0.0 / 0.0 (0.0) |
| holdout250 | 6.4 / 5.2 / 10.4 (7.3) / 2.4 / 2.0 / 4.8 (3.1) | 1.2 / 3.6 / 2.8 (2.5) / 0.0 / 1.2 / 0.8 (0.7) | 34.4 / 40.4 / 39.6 (38.1) / 0.0 / 0.0 / 0.0 (0.0) |
| rr600 | 1.5 / 0.8 / 1.7 (1.3) / 0.2 / 0.3 / 0.3 (0.3) | 1.2 / 0.8 / 0.0 (0.7) / 0.3 / 0.3 / 0.0 (0.2) | 16.3 / 13.0 / 8.7 (12.7) / 0.0 / 0.0 / 0.0 (0.0) |
| hand_proved_14 | 0.0 / 0.0 / 0.0 (0.0) / 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) / 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) / 0.0 / 0.0 / 0.0 (0.0) |

G1 with the premise lines supplied (theorems solved of 200): greedy KAL-D 21 / 10 / 21 (17); greedy KAL-C 18 / 15 / 9 (14); greedy control 125 / 108 / 143 (125); k32 KAL-D 38 / 30 / 41 (36); k32 KAL-C 24 / 39 / 21 (28); k32 control 184 / 177 / 191 (184)

G2 by size bin (greedy % valid | plain pass@32 %): KAL-D 40-49: 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0); KAL-D 50-59: 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0); KAL-D 60-79: 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0); KAL-C 40-49: 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0); KAL-C 50-59: 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0); KAL-C 60-79: 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0); control 40-49: 0.0 / 1.2 / 1.2 (0.8) | 0.0 / 2.5 / 2.5 (1.7); control 50-59: 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 1.2 (0.4); control 60-79: 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0)

#### Cut-offs in the k 32 reads

- KAL-D plain: 167,616 attempts; step cap 0.0000%; ended by a truncated action 3.0057%; truncation events (guided redraws) 5,038
- KAL-D logical: 167,616 attempts; step cap 0.0000%; ended by a truncated action 0.0000%; truncation events (guided redraws) 40,245
- KAL-C plain: 167,616 attempts; step cap 0.0000%; ended by a truncated action 2.3548%; truncation events (guided redraws) 3,947
- KAL-C logical: 167,616 attempts; step cap 0.0000%; ended by a truncated action 0.0000%; truncation events (guided redraws) 29,872
- control plain: 167,616 attempts; step cap 0.0000%; ended by a truncated action 0.8651%; truncation events (guided redraws) 1,450
- control logical: 167,616 attempts; step cap 0.0000%; ended by a truncated action 0.0000%; truncation events (guided redraws) 14,747

#### Batch-effect check (Addendum 2): plain k 32, batch 2,048 vs 1,024, same checkpoint

| model | set | pass@1 b2048 | pass@1 b1024 | pass@32 b2048 | pass@32 b1024 |
|---|---|---|---|---|---|
| kalC_s0 | holdout250 | 1.9 | 1.6 | 24 | 18 |
| kalC_s0 | rr600 | 0.4 | 0.4 | 6 | 7 |
| kalC_s0 | ge17 | 0.0 | 0.0 | 0 | 1 |
| kalC_s0 | long2 | 0.2 | 0.2 | 1 | 1 |
| kalC_s0 | candidate_v0 | 1.6 | 2.7 | 11 | 17 |
| kalC_s0 | candidate_v1 | 0.7 | 0.5 | 4 | 2 |
| kalC_s0 | batch3 | 0.2 | 0.2 | 2 | 2 |
| kalC_s0 | hand_proved_14 | 0.0 | 0.0 | 0 | 0 |
| kalC_s0 | textbook72 | 2.3 | 2.5 | 14 | 13 |
| kalC_s0 | g1_premises | 0.9 | 0.8 | 7 | 6 |
| kalC_s0 | g2_large | 0.0 | 0.0 | 0 | 0 |
| kalC_s0 | g3_classical | 1.4 | 0.8 | 14 | 14 |
| ctl_s0 | holdout250 | 65.8 | 66.9 | 165 | 166 |
| ctl_s0 | rr600 | 57.2 | 56.4 | 298 | 295 |
| ctl_s0 | ge17 | 1.1 | 1.5 | 13 | 15 |
| ctl_s0 | long2 | 0.1 | 0.1 | 4 | 2 |
| ctl_s0 | candidate_v0 | 10.5 | 9.7 | 33 | 30 |
| ctl_s0 | candidate_v1 | 6.9 | 7.3 | 23 | 23 |
| ctl_s0 | batch3 | 1.1 | 1.2 | 4 | 5 |
| ctl_s0 | hand_proved_14 | 0.0 | 0.0 | 0 | 0 |
| ctl_s0 | textbook72 | 10.5 | 10.6 | 25 | 28 |
| ctl_s0 | g1_premises | 0.0 | 0.0 | 0 | 1 |
| ctl_s0 | g2_large | 0.0 | 0.0 | 0 | 1 |
| ctl_s0 | g3_classical | 3.8 | 3.7 | 12 | 13 |

#### What KAL-D writes when it disagrees (KAL-D s2, all 6,903 teacher-forced disagreements; `kalmar/error_classes.py` → `artifacts/kalmar/error_classes_kalD_s2.json`)

| class | share |
|---|---|
| a formula of the problem, not the next one due | 3077 (44.6 %) |
| a formula found nowhere in the problem (copy / substitution) | 2148 (31.1 %) |
| closes a box too early / too late | 450 (6.5 %) |
| same formula, other justification | 445 (6.4 %) |
| malformed formula / action | 429 (6.2 %) |
| no <eos> in 512 tokens | 175 (2.5 %) |
| polarity: F for ¬F or ¬F for F | 96 (1.4 %) |
| exact cites another name | 83 (1.2 %) |

By step type (`by_tag` in the json):
- Leaf steps: "not the next one due" and "corrupted" dominate.
- Split errors: malformed or corrupted formulas, 75 %.
- Ex-falso errors (150): mostly a justification other than the algorithm's for the same formula (35 %); malformed or
  corrupted 30 %.

**Errors that assert something false** (`kalmar/error_truth.py`). Valuation from the atom hypotheses; scored only
where every hypothesis is true, so that a correct step can only assert a true formula. That leaves 4,002 of the
6,903 disagreements; the algorithm's own formula is false in 0 of them.
- The model asserts a formula false in the branch in **671**: 16.8 % of the scored, ≥ 9.7 % of all.
- By class: other-subformula 414, corrupted 205, polarity 48, malformed 4.
- So direct F ↔ ¬F swaps (1.4 %) understate truth-value errors. Still, most disagreements (≥ 83 % of the scored)
  write a true formula at the wrong place, or a malformed one.

#### Pre-registered verdicts

**"Learned the construction"** (per seed, tf1200).
- Criterion (i): TF agreement ≥ 99 % overall and ≥ 95 % on every step type with ≥ 500 states.
- Criterion (ii): greedy exact-follow ≥ 90 % at 1–2 atoms and ≥ 60 % at 4 atoms.

| model | (i) overall | (i) worst step type | (ii) exact-follow 1 / 2 / 4 atoms | verdict |
|---|---|---|---|---|
| KAL-D s0 / s1 / s2 | 94.6 / 93.8 / 95.0 % | ∧ true 60.4 / 61.5 / 74.4 % | s0 19.3, 19.7, 6.6; s1 17.3, 17.4, 7.7; s2 8.0, 22.0, 10.9 % | **not learned** (3 / 3) |
| KAL-C s0 / s1 / s2 | 93.8 / 93.2 / 93.4 % | ∧ true 61.6 / 58.1 / 59.6 % | ≤ 14 % | not learned (3 / 3) |

**"Generalises"** (`kalmar/gen_verdicts.py` → `artifacts/kalmar/gen_verdicts.txt`).
- Generalises: KAL-D's greedy rate on the set is ≥ 0.7 × its tf1200 greedy rate at the same atom mix, **and** it beats
  the control's pass@32 by more than the MDD.
- Does not generalise: below 0.3 ×. Between the two: partially.
- Judged on the arm's ratio: the IQM of the per-seed ratios, i.e. the mean at n = 3, as every arm-level number here.

| set | KAL-D greedy (s0 / s1 / s2) | ratio to in-distribution | pass@32 KAL-D − control (MDD), plain / guided | verdict |
|---|---|---|---|---|
| G1, premise lines supplied | 10.5 / 5.0 / 10.5 % | 0.34 / 0.17 / 0.28 | control solves 177–191 / 200 at k 32 vs KAL-D 30–41 | does not (arm ratio 0.27) |
| G2 larger formulas | 0 / 0 / 0 % | 0 | −1.7 (3.3) / −3.0 (3.5) | does not |
| G3 classical | 10.4 / 8.5 / 11.3 % | 0.33 / 0.29 / 0.31 | +4.7 (11.2) / **+14.0 (11.5)** | partially (arm ratio 0.31); the guided read beats the control beyond the MDD |
| hand_proved_14 | 0 / 0 / 0 % | 0 | 0 / 0 | does not |
| ≥ 17 (ge17) | 0 / 0 / 1.4 % | ≤ 0.04 | **−12.7 (4.1) / −36.0 (9.6)** | does not; KAL-D is worse than the control |

The G3 guided comparison crosses batch sizes: KAL-D at 1,024, control at 2,048. The batch-effect check covered plain
reads only, where G3 moved by ≤ 1 theorem.

#### Expectations vs outcomes (pre-registration, item by item)

| expectation | outcome | |
|---|---|---|
| KAL-D TF ≥ 99.5 %, every step type ≥ 98 % | 94.5 %; split 97.0, leaf 65–92 | miss |
| lowest: ex-falso decision, ∨+ disjunct, ∧− conjunct; falls with formula depth | lowest ∧+ 65, ¬⊥ 74, ∨+ 74; ex falso 98.4; falls with box depth (97.6 → 89.4), not monotonic in formula depth | partial |
| KAL-C TF 97–99.5 % | 93.5 % | miss |
| control TF ≤ 40 % | 27.0 % | hit |
| KAL-D greedy ≥ 98 / 95 / 90 / 75 % (1–4 atoms); exact-follow within 5 points | 36.9 / 37.1 / 32.7 / 26.1 %; exact 14.7 vs valid 32.6 | miss |
| KAL-C greedy 80–95 / 80–95 / 50–80 / 20–60 % | 25.8 / 24.4 / 20.8 / 16.1 % | miss |
| control greedy ≈ 0.90–0.95 | 92.2 % (90.5–94.4) | hit |
| KAL-D exact-follow ≥ 60 % at T 0.8 | 6.3 % | miss |
| KAL-D pass@256: holdout250 ≥ 235, rr600 Q ≥ 350, ≥ 17 ≥ 80 / 91, release ≥ 160 / 182, hand_proved_14 ≥ 10, textbook72 ≥ 60 | not measured (k extension dropped); pass@32 33 / 17 of 600 / 0.7 / ≈ 33 / 0 / 20 | untested (at pass@32 far below) |
| control hand_proved_14 0 / 14 | 0 / 0 / 0 | hit |
| holdout250 pass@1: KAL-D ≥ 0.75; control 0.3–0.5 | KAL-D 0.021; control 0.27 / 0.31 / 0.32 (stored reads) | miss; mostly hit |
| KAL-C below the control on holdout250 pass@32; above it on hand_proved_14 | 18 vs 165; 0 vs 0 | hit; miss |
| guided ≥ plain at k 32 for every arm | yes, every arm, set and seed | hit |
| KAL-D guided gain ≤ 3 points; control's 3–9 points | KAL-D holdout250 +26 theorems (10 pp); control +13 pp on holdout250, +16 pp on textbook72 | miss; miss |
| G1 as is ≤ 5 % for both arms | greedy 4.3 / 3.8 % (hit); pass@32 11.2 / 6.2 % (miss) | mixed |
| G1 supplied: KAL-D greedy ≥ 60 %; control pass@32 ≤ 20 % | 8.7 %; control 92 % | miss; miss (the control generalises) |
| G2: KAL-D greedy ≥ 60 / 40 / 20 % per bin; control ≤ KAL-D in every bin | 0 / 0 / 0; control 1.7 / 0.4 / 0 % pass@32 | miss; miss |
| G3: KAL-D pass@32 ≥ 90 / 106; control pass@256 ≤ 30 | 18 plain / 29.7 guided; control 17 / 14 / 20 | miss; hit |

**Disclosures.**
- **pass@256 column.** The control's stored reads (holdout250, rr600, long2, textbook72) are best-state's
  `state_eval.py`, sample seed 0, `max_steps` 96 (0 attempts reached 90 steps). The new k 256 reads (other sets) are
  `guided_eval.py`, seed 1, `max_steps` 1,024. The two protocols agree within noise where both exist (log 05:45).
- **Q** = rr600 generator theorems at L_true 13–16, out of 380.
- **Pooled strata** = holdout250 + rr600 + ge17 + long2 + the release, n = 1,128.
- **Truncation.** The pre-registered cap rule fired: > 0.1 % of plain attempts ended in a truncated action (KAL-D
  3.01 %, KAL-C 2.35 %, control 0.87 %). No 2× re-read was run. The longest legitimate action is 305 tokens (G2;
  ≤ 219 in all training data), so these are non-terminating outputs, not real steps cut short. best-state measured
  2× the cap barely changing this model family (+≤ 2 solved).
- **Batch-effect check.** One seed, plain reads only. Its ≤ 6-theorem moves are large relative to KAL-C's counts and
  to the textbook72 (−4) and G3-plain (+4.7) gaps, so those gaps are not claimed. They are small against the
  holdout250 / rr600 / ≥ 17 gaps.

#### Compute (results-registry rows, `python3 kalmar/compute.py` → `artifacts/kalmar/compute.json`, `compute_stdout.txt`; seeds summed; snapshot reads under their arm)

| arm | phase | GPU-s | GPU | gen tokens | attempts | actions | train steps | train tokens | Lean checks |
|---|---|---|---|---|---|---|---|---|---|
| KAL-D | read | 44,669 | 3090 (greedy) / A40 (sampled) | 542,803,368 | 473,526 | 26,675,872 | 0 | 0 | 18,494 |
| KAL-D | read (Addendum 3) | 1,889 | A40 | 17,280,081 | 16,000 | 1,024,354 | 0 | 0 | 493 |
| KAL-D | train | 109,305 | RTX 3090 | 0 | 0 | 0 | 1,968,855 | 36,092,382,461 | 0 |
| KAL-C | read | 31,147 | 3090 (greedy) / A40 (sampled) | 414,366,772 | 448,326 | 22,166,241 | 0 | 0 | 7,764 |
| KAL-C | train | 4,860 | RTX 3090 | 0 | 0 | 0 | 72,060 | 1,321,016,321 | 0 |
| control | read | 11,710 | 3090 (greedy) / A40 (sampled) | 219,253,048 | 1,120,902 | 9,902,918 | 0 | 0 | 101,430 |
| ladder ei | ladder | 21,853 | A40 | 0 | 0 | 0 | 1,200 | 3,279,934,442 | 0 |
| ladder ei | ladder (OOM launch) | 337 | A40 | 3,867,341 | 16,000 | 227,328 | 0 | 0 | 0 |
| ladder ei | read | 679 | A40 | 14,166,408 | 2,700 | 583,451 | 0 | 0 | 1,978 |
| ladder frozen | ladder | 6,924 | A40 | 65,084,314 | 59,100 | 3,863,998 | 0 | 0 | 2,151 |
| ladder frozen | ladder (OOM launch) | 333 | A40 | 3,867,341 | 16,000 | 227,328 | 0 | 0 | 0 |
| KAL-D+A | read | 27,772 | A40 / RTX 3090 (s1 greedy) | 344,175,682 | 177,738 | 20,023,157 | 0 | 0 | 26,128 |
| KAL-D+A | read (Addendum 3) | 3,409 | A40 | 37,477,508 | 16,000 | 2,082,235 | 0 | 0 | 4,927 |
| KAL-D+A | train | 31,406 | A40 (s0, s2) / RTX 3090 (s1) | 0 | 0 | 0 | 1,800 | 4,881,133,433 | 0 |
| control (best-state, inherited) | train | 3 × ≈ 1,200 | A40 | — | — | — | 23,951 / 23,987 / 24,123 | ≈ 3 × 0.44 B padded | — |

KAL-D used ≈ 27× the control's training tokens and ≈ 30× its GPU-seconds (on a slower card); this is flagged as
> 1.25× by design (data-matched arm). KAL-C is matched on steps × token budget (440 M training tokens per seed vs
≈ 442 M padded for the control). Ladder EI vs frozen are matched on attempts (k 16 × 1,200 theorems per round).
KAL-D+A's fine-tune is 1.63 B tokens per seed (13.5 % of KAL-D's) in 600 steps of ≈ 2.71 M tokens.

**Registry gaps, ladder arms** (rows in `artifacts/kalmar-pretrain/registry/`).
- Both arms' first launch, at batch 2,048 (12:22–12:28, 10-19), ran out of memory in round 1. Its rows (≈ 335 GPU-s
  and 16,000 attempts per arm) are the `ladder (OOM launch)` phase.
- EI: none of the batch-1,024 ladder's sampling rows reached the registry. Recorded are its two fine-tunes (10,732 +
  11,121 GPU-s) and its held-out greedy accuracies. Wall clock from `artifacts/kalmar/logs/la_kal_ei_s0.log`: 13:10:40
  → ≈ 21:02 and 22:09:58 → 03:41:10, ≈ 13.4 A40-hours. The unrecorded ≈ 7.3 h are rounds 1–3's sampling (round 2
  twice) and the first round-2 fine-tune, killed after step 400.
- Frozen: rounds 1–3 recorded (6,924 GPU-s; 3 × 19,700 attempts). Round 4's rows were lost when the process was
  stopped at 15:47:12, right after the round (2,441 s by `round_4.json`). Wall clock 13:10:42 → 15:47:12 (2.6 h).
- The dollar spend is billed by pod time, so it is complete.

#### EI ladder from KAL-D s0 (pre-registered Addendum 1; `kalmar/ladder_analysis.py` → `artifacts/kalmar/ladder_summary.json`, `artifacts/kalmar/ladder_stdout.txt`)

**Protocol.** Addendum 1, at batch 1,024 (Addendum 2).
- Rounds: cut to 4 by the cost rule (log 14:30, 10-19). The EI arm then stopped after round 3's sampling, before its
  fine-tune (budget; log 01:15, 10-20).
- The EI process died once, in round 2's fine-tune (kal-12 restart, log 22:09). It resumed from round 1's checkpoint;
  round 2 was re-sampled with the same seed and gave identical counts.
- Frozen = KAL-D s0 with the same seeds and attempts, no training.
- Each round: k 16 at T 0.8 on the 1,000 targets; held-out greedy on `val300`.

| round | EI: targets solved this round / cumulative | frozen: this round / cumulative | EI held-out greedy (val300) |
|---|---|---|---|
| 1 (model KAL-D s0) | 135 / 135 | 135 / 135 | 87 / 300 |
| 2 (EI r1) | 572 / 576 | 138 / 164 | 215 / 300 |
| 3 (EI r2) | 668 / 673 | 146 / 183 | 223 / 300 |
| 4 | — | 119 / 188 | — |

Frozen held-out greedy: 87 / 300 every round. Round 3's EI numbers are from the log (its `round_3.json` is written
after the fine-tune, which did not run).

**New distinct Lean-accepted proofs per round** (`found_<r>.jsonl`; a proof counts in the round that first found it).
- Exact = the algorithm's ND proof, token for token. All 419 exact proofs in the EI arm's found files, and all 99 in
  the frozen arm's, have `written` equal to the algorithm's line count. So the shorter / longer columns compare like
  with like.
- Deduplication bias: a theorem's exact proof is new only once, so the exact share falls with the round.

**la_kal_ei_s0**

| round | targets solved (cum) | new proofs | exact Kalmár | shorter deviations | longer | mean lines (algorithm) | secs |
|---|---|---|---|---|---|---|---|
| 1 | 135 | 313 | 20.1 % | 39.6 % | 32.9 % | 96.0 (96.6) | 13001 |
| 2 | 576 | 2029 | 13.9 % | 41.2 % | 39.5 % | 135.8 (136.2) | 15065 |
| 3 | 673 | 2100 | 3.5 % | 43.0 % | 48.7 % | 157.7 (158.6) | — |

**la_kal_frozen_s0**

| round | targets solved (cum) | new proofs | exact Kalmár | shorter deviations | longer | mean lines (algorithm) | secs |
|---|---|---|---|---|---|---|---|
| 1 | 135 | 313 | 20.1 % | 39.6 % | 32.9 % | 96.0 (96.6) | 2222 |
| 2 | 164 | 213 | 7.5 % | 43.2 % | 40.4 % | 105.6 (106.7) | 2405 |
| 3 | 183 | 198 | 8.1 % | 40.4 % | 42.9 % | 104.2 (103.9) | 2293 |
| 4 | 188 | 154 | 2.6 % | 41.6 % | 48.1 % | 106.2 (105.7) | 2441 |

- la_kal_ei_s0_r1: TF agreement 98.70 %
- la_kal_ei_s0_r1: greedy tf1200 valid 71.2 %, exact-follow 52.9 %

- la_kal_ei_s0_r2: TF agreement 98.93 %
- la_kal_ei_s0_r2: greedy tf1200 valid 75.7 %, exact-follow 57.2 %

**After the ladder** (greedy reads on tf1200; source `artifacts/kalmar/{tf,free}/la_kal_ei_s0_r{1,2}__*`):
- EI r1: TF 98.7 %, valid 71.2 %, exactly Kalmár 52.9 %.
- EI r2: TF 98.9 %, valid 75.7 %, exactly Kalmár 57.2 %.
- KAL-D s0, the base: 94.6 / 33.1 / 14.1 %.
- Greedy, EI follows the algorithm more than its base did, and TF agreement rose.

**Pre-registered ladder verdicts** (Addendum 1; criteria set for round 8, applied at round 3, the last round run).

| criterion | EI, round 3 | frozen, round 4 | verdict |
|---|---|---|---|
| keeps the algorithm: ≥ 50 % of new proofs exact, and TF fallen ≤ 1 point | 3.5 % exact; TF +4.3 pp (r2 vs base) | 2.6 % exact | **not met** |
| finds shorter proofs: mean ≥ 15 % below the algorithm's, or ≥ 30 % shorter deviations | mean −0.6 %; 43.0 % shorter | mean +0.4 %; 41.6 % shorter | **met** (share clause) |

- Frozen sampling of the untrained base meets "finds shorter proofs" equally, and so does round 1 (39.6 %). So both
  verdicts describe T 0.8 sampling from KAL-D plus the deduplication bias, not something EI did.
- Expectations: round 1 solves ≥ 90 % of targets (13.5 %, miss); exact share ≥ 70 % in round 1 (20.1 %, miss);
  actions per accepted proof within ±10 % of the algorithm's (written lines −0.3 to −0.6 %, hit); TF ≥ base − 1 and greedy
  exact-follow ≥ base − 5 after the ladder (+4.3 / +43.1 pp, hit); EI's cumulative solved exceeds frozen's by ≤ 3
  points (673 vs 183 at round 3, +49 points, miss).
- The size of the gain is not RL's (next section).

#### Exploratory, NOT pre-registered (Addendum 3): the replay-only fine-tune (`kalmar/exploratory.py` → `artifacts/kalmar/exploratory_stdout.txt`)

**KAL-D+A s0–s2.**
- Construction: KAL-D plus exactly the ladder's fine-tune command, without EI proofs. That is `state_train.py --init
  <KAL-D> --steps 600 --lr 3e-4 --min_lr 3e-5 --warmup 50 --recs 128`, on 20,000 K12-Kalmár records drawn with
  `random.Random(seed)`.
- Checkpoints: `ckpts/kalmar/anneal/kalDA_s{0,1,2}.pt`, md5 4516a1f5 / a2ee6578 / cbf7a110.
- Training hardware: s0 and s2 on A40s, s1 on an RTX 3090; 9,881–10,800 GPU-s each.
- Reads:
  - greedy and teacher-forced at batch 1,024;
  - targets with `guided_eval.py --arm plain --k 16 --seed 2` (round 2's seed);
  - plain k 32 at batch 1,024 (KAL-D's protocol; the control's reads are at 2,048, see the batch-effect check).

**What the fine-tune changes, all at once** (not separated by this run):

| | KAL-D pretraining (best recipe) | the fine-tune (ladder's command) |
|---|---|---|
| optimizer | Muon on the matrices + AdamW (lr 1e-3 → floor 3e-4), MTP 0.3 | AdamW on every weight, lr 3e-4 → 3e-5, no MTP |
| batch | 18,432-token budget batches | 128 whole proofs, ≈ 2.71 M tokens (≈ 150×) |
| tokens per seed | 12.03 B (656,285 steps) | 1.63 B (600 steps; 13.5 % of KAL-D's) |

More tokens alone explain little. KAL-D was still improving at its end: its last 156,285 steps (2.86 B tokens) added
+1.5 pp TF and +9.6 pp greedy validity. The fine-tune's 1.63 B added +4.3 pp and +42.1 pp (means of 3 seeds).

**Exploratory (Addendum 3): annealing vs EI — teacher-forced agreement and greedy free generation**

| model | TF agreement % | tf1200 greedy valid % | exact Kalmár % | 4-atom valid % | val300 greedy valid % |
|---|---|---|---|---|---|
| KAL-D s0 | 94.6 | 33.1 | 14.1 | 23.7 | — |
| KAL-D s1 | 93.8 | 29.1 | 13.7 | 24.0 | — |
| KAL-D s2 | 95.0 | 35.6 | 16.3 | 30.6 | — |
| KAL-D+A s0 | 98.7 | 71.2 | 53.9 | 59.1 | 70.7 |
| KAL-D+A s1 | 98.7 | 74.2 | 56.5 | 65.1 | 72.0 |
| KAL-D+A s2 | 98.8 | 78.7 | 59.8 | 68.3 | 76.3 |
| EI r1 (from KAL-D s0) | 98.7 | 71.2 | 52.9 | 57.7 | 71.7 |
| EI r2 (from KAL-D s0) | 98.9 | 75.7 | 57.2 | 64.3 | — |

**"Learned" criteria** (≥ 99 % TF and ≥ 95 % per step type; exact-follow ≥ 90 % at 1–2 atoms, ≥ 60 % at 4):

- kalDA_s0: TF 98.7, worst step type leaf:and+ 87.3, exact-follow 1/2/4 atoms 64.7 / 63.1 / 43.4 -> not learned
- kalDA_s1: TF 98.7, worst step type leaf:bot- 88.9, exact-follow 1/2/4 atoms 63.3 / 64.3 / 44.6 -> not learned
- kalDA_s2: TF 98.8, worst step type leaf:bot- 88.3, exact-follow 1/2/4 atoms 64.7 / 69.1 / 50.9 -> not learned
- la_kal_ei_s0_r2: TF 98.9, worst step type leaf:and+ 90.3, exact-follow 1/2/4 atoms 64.7 / 66.0 / 47.4 -> not learned

**Targets (the ladder's 1,000 EI targets), solved at k 16**

- KAL-D s0 (seed-2 re-draw of round 1): 133 / 1000
- KAL-D+A s0: 578 / 1000
- EI ladder, targets solved in the round (round_<r>.json; round 3 from the log, its json was not written):
  - EI: round 1 (KAL-D s0) 135, round 2 (EI r1) 572, round 3 (EI r2) 668 of 1,000;
  - frozen (KAL-D s0, re-drawn each round): 135 / 138 / 146 / 119; held-out greedy (val300) 87 / 300 every round;
  - EI held-out greedy 87 → 215 → 223 / 300.

**Greedy suite, % of theorems Lean-valid (KAL-D vs KAL-D+A vs control)**

| set | KAL-D | KAL-D+A | control |
|---|---|---|---|
| holdout250 | 6.4 / 5.2 / 10.4 (7.3) | 33.2 / 34.4 / 42.4 (36.7) | 34.4 / 40.4 / 39.6 (38.1) |
| rr600 | 1.5 / 0.8 / 1.7 (1.3) | 17.7 / 13.8 / 24.3 (18.6) | 16.3 / 13.0 / 8.7 (12.7) |
| ge17 | 0.0 / 0.0 / 1.4 (0.5) | 8.6 / 14.3 / 21.4 (14.8) | 7.1 / 2.9 / 1.4 (3.8) |
| long2 | 0.0 / 0.0 / 4.8 (1.6) | 14.3 / 9.5 / 23.8 (15.9) | 9.5 / 4.8 / 4.8 (6.3) |
| candidate_v0 | 12.6 / 8.0 / 10.3 (10.3) | 44.8 / 32.2 / 36.8 (37.9) | 16.1 / 16.1 / 14.9 (15.7) |
| candidate_v1 | 4.2 / 2.8 / 5.6 (4.2) | 19.4 / 11.1 / 19.4 (16.7) | 8.3 / 18.1 / 12.5 (13.0) |
| batch3 | 14.3 / 7.1 / 14.3 (11.9) | 35.7 / 42.9 / 42.9 (40.5) | 14.3 / 21.4 / 7.1 (14.3) |
| hand_proved_14 | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) | 0.0 / 0.0 / 0.0 (0.0) |
| g1_premises | 5.5 / 3.5 / 4.0 (4.3) | 21.0 / 14.5 / 16.5 (17.3) | 0.0 / 3.0 / 8.5 (3.8) |
| g2_large | 0.0 / 0.0 / 0.0 (0.0) | 0.4 / 0.8 / 1.2 (0.8) | 0.0 / 0.4 / 0.4 (0.3) |
| g3_classical | 10.4 / 8.5 / 11.3 (10.1) | 30.2 / 34.0 / 41.5 (35.2) | 3.8 / 2.8 / 15.1 (7.2) |

G1 with premise lines supplied, greedy, theorems solved of 200: KAL-D [21, 10, 21], KAL-D+A [58, 40, 53], control [125, 108, 143]

**Plain k 32 (T 0.8, seed 1), theorems solved (unbiased pass@32; per seed, then mean)**

| set | n | KAL-D | KAL-D+A | control | KAL-D+A − control (MDD) |
|---|---|---|---|---|---|
| holdout250 | 250 | 35 / 24 / 41 (33.3) | 133 / 130 / 146 (136.3) | 165 / 170 / 160 (165.0) | -28.7 (21.2) |
| rr600 | 600 | 16 / 10 / 25 (17.0) | 195 / 175 / 238 (202.7) | 298 / 241 / 198 (245.7) | -43.0 (128.1) |
| ge17 | 70 | 0 / 0 / 2 (0.7) | 24 / 21 / 29 (24.7) | 13 / 15 / 12 (13.3) | +11.3 (9.3) |
| long2 | 21 | 0 / 0 / 0 (0.0) | 10 / 7 / 11 (9.3) | 4 / 1 / 1 (2.0) | +7.3 (5.8) |
| candidate_v0 | 87 | 19 / 21 / 24 (21.3) | 55 / 41 / 52 (49.3) | 33 / 28 / 28 (29.7) | +19.7 (17.0) |
| candidate_v1 | 72 | 9 / 6 / 8 (7.7) | 24 / 26 / 27 (25.7) | 23 / 19 / 24 (22.0) | +3.7 (6.6) |
| batch3 | 14 | 7 / 2 / 4 (4.3) | 10 / 7 / 7 (8.0) | 4 / 4 / 6 (4.7) | +3.3 (4.5) |
| hand_proved_14 | 14 | 0 / 0 / 0 (0.0) | 0 / 0 / 0 (0.0) | 0 / 0 / 0 (0.0) | +0.0 (0.0) |
| textbook72 | 72 | 21 / 18 / 20 (19.7) | 40 / 42 / 41 (41.0) | 25 / 22 / 24 (23.7) | +17.3 (3.9) |
| g1_premises | 200 | 35 / 15 / 17 (22.3) | 65 / 48 / 61 (58.0) | 0 / 11 / 26 (12.3) | +45.7 (33.9) |
| g2_large | 240 | 0 / 0 / 0 (0.0) | 2 / 2 / 3 (2.3) | 0 / 2 / 3 (1.7) | +0.7 (3.5) |
| g3_classical | 106 | 19 / 18 / 17 (18.0) | 52 / 58 / 59 (56.3) | 12 / 9 / 19 (13.3) | +43.0 (13.7) |

Notes:
- KAL-D s0's val300 greedy is 87 / 300 = 29.0 % (the ladder's round-1 held-out greedy, the same read). EI r2's is
  223 / 300 = 74.3 % (the ladder's round 3).
- The greedy suite reads all ran at batch 1,024 for every arm.
- MDD = 3.04 × the pooled per-seed sd (n = 3 per arm).
- Plain k 32 of KAL-D+A: batch 1,024 on A40s; 7,297 / 8,036 / 8,811 s per seed (s0 / s1 / s2).
  KAL-D's took 3,900–4,200 s.
- The control's reads are at batch 2,048. In the batch-effect check, that moved one checkpoint's pass@32 by ≤ 6
  theorems per set (KAL-C s0, control s0).
- Beyond the MDD: the control leads on holdout250 (−28.7). KAL-D+A leads on ge17, long2, candidate_v0, textbook72,
  G1 as is and G3; the textbook72 and G3 gaps (+17.3, +43.0) are also far beyond the batch effect. Exploratory, one
  fine-tune recipe, NOT pre-registered.

**Pods and spend.**
- Community RTX 3090 ($0.22/h): training and greedy reads.
- A40 secure ($0.59/h): sampled reads, the ladder, and the anneal control (KAL-D+A s1 on an RTX 3090 secure, $0.50/h).
- Billed rates from `podnew` (RunPod `costPerHr`); spend from `podbudget`. Total $46.04 of $50 (101.69 pod-hours;
  `podbudget` at 09:29 UTC, 2026-10-20). All pods deleted.

**Bucket:** `hf://buckets/dan-pandori/nd-rl/kalmar-pretrain/`.
- `ckpts/kalmar/`: KAL-D, KAL-C, snapshots, `ladder/`, `anneal/`.
- `data/kalmar/`: K12-Kalmár and the read sets.
- `artifacts/kalmar/`: read rows, ladder found files, dumps.
- Registry rows: `hf://buckets/dan-pandori/nd-rl/registry/kalmar-pretrain/`.

## kalmar-complexity (2026-10-20, executor; UNREVIEWED)

Pre-registration `preregistration/kalmar-complexity.md` (`68f7ada4`, 12:30 UTC; addendum 1 `a32add38`, 13:16), both
before the first pod (13:17:34). Tables below are generated from the result files by
`kalmar_complexity/numbers_tables.py` (assembled with `kalmar_complexity/assemble_numbers.py`). Lean is not called:
no proof is judged in this run; the builder's proofs are kalmar-pretrain's (155,000 / 155,000 Lean-accepted).

**Algorithms.**
- **K-sl:** K12-Kalmár, the shared-lemma variant with memo that kalmar-pretrain trained on (`kalmar/kalmar.py`, `sl`).
- **K-tt:** nd-rl `code/tools/tt_prover.py` (per-atom split, no memo, a Lean term).

**Models (every learned number names one).**
- **KAL-D s0–s2:** `kalmar-pretrain/ckpts/kalmar/stage1_kalD_s{0,1,2}.pt`. 9,560,832-param ALiBiGPT 6 × 384,
  `lean_staten`, from scratch on K12-Kalmár sl (155,000 proofs, 16,876,247 pairs), 656,285 steps.
- **Snapshots:** `_step{24020,100000,200000,350000,500000}`.
- **KAL-C:** `stage1_kalC_s*` (24,020 steps).
- **KAL-D+A:** `anneal/kalDA_s*` (KAL-D + 600 AdamW steps on replayed Kalmár proofs).
- **Control s0–s2:** best-state `stage1_best12_s{0,1,2}_b1200.pt`, the same network, from scratch on K12
  (`data/kh/train_k12.jsonl`, 155,000 proofs, 1,239,995 pairs), 23,951–24,123 steps.
- **B2 models:** trained here, from scratch, ALiBiGPT S 2 × 128 (0.4 M), M 4 × 256 (3.2 M), L 6 × 384 (9.6 M) on
  prefixes of the same data (below).

**Test protocol.** Every program reproduces its reference exactly:
- `kalmar.build` / `tt_prover.solve` on 1,000 K12 theorems (`kalmar_complexity/common.py`, seed 20261020) plus at
  least one fresh seed.
- Per-step programs reproduce every state the algorithm visits:
  - `policy.py` 109,072 + 546,991 states;
  - golfed `kpol.py` 109,072 + 326,761;
  - RASP-L 109,072 + 107,233, plus an executor re-check at seed 99, 22,018;
  - the decision tree 473 distinct rows of 4,000 theorems + a fresh 217,968 states + all 137,984 tf1200 states;
  - BLC 1,000 + 300 theorems, plus an executor re-check at seed 99, 150.

### Q1 — program length of Kalmár's construction (algorithm / rendering / parse reported separately)

| piece | Python raw B | Python DEFLATE B | Python xz B | Qwen3 tokens | GPT-2 tokens | BLC bits | binary CL bits |
|---|---|---|---|---|---|---|---|
| K-sl algorithm | 1,907 | 864 | 906 | 897 | 1,195 | 5,443 | 23,921 |
| K-sl rendering, ND text | 465 | 293 | 321 | 244 | 308 | 616 | 3,776 |
| K-sl rendering, lean_seq (canonical) | 977 | 562 | 596 | 475 | 615 | — | — |
| parse (prompt → sequent) | 251 | 153 | 162 | 122 | 156 | 800 | 2,900 |
| K-sl algorithm + ND rendering | 2,372 | 1,093 | 1,137 | 1,141 | 1,503 | 6,059 | 27,697 |
| K-sl parse + algorithm + ND rendering | 2,623 | 1,199 | 1,241 | 1,263 | 1,659 | 6,859 | 30,597 |
| K-sl parse + algorithm + lean_seq rendering | 3,135 | 1,453 | 1,485 | 1,494 | 1,966 | — | — |
| K-tt algorithm | 749 | 378 | 394 | 377 | 491 | 1,636 | 7,442 |
| K-tt rendering, Lean text | 1,024 | 571 | 600 | 514 | 655 | 4,204 | 24,245 |
| K-tt algorithm + rendering | 1,773 | 866 | 880 | 891 | 1,146 | 5,840 | 31,687 |
| K-tt parse + algorithm + rendering | 2,024 | 972 | 990 | 1,013 | 1,302 | 6,640 | 34,587 |
| K-sl per-step policy (state → action) | 3,794 | 1,654 | 1,658 | 1,838 | 2,387 | — | — |
| mechanical: kalmar/kalmar.py | 5,863 | 2,416 | 2,391 | 2,420 | 3,434 | — | — |
| mechanical: tt_prover.py | 3,474 | 1,685 | 1,698 | 1,384 | 1,885 | — | — |
| mechanical: policy.py | 7,453 | 2,761 | 2,713 | 3,166 | 4,386 | — | — |
| mechanical: gen.py (K12 generator, all knobs) | 17,076 | 5,324 | 5,131 | 6,188 | 8,706 | — | — |

- **Python:** hand-golfed (`kalmar_complexity/programs/python/`). DEFLATE = raw zlib level 9; xz = raw LZMA2 9e.
  - Tokens: Qwen3 / GPT-2. Our model's own tokenizer (`lean_tok`) cannot spell Python.
  - `mechanical:` rows are python-minifier upper bounds, unused code included.
- **BLC / binary CL:** Tromp's encodings (λ = 00, application = 01, variable i = 1^i 0; S = 00, K = 01,
  application = 1), from the agent-written toolchain `kalmar_complexity/programs/blc/`.
  - Data enter and leave as Scott-encoded terms; the encodings are stated in its README.
  - Binary CL is plain bracket abstraction of the golfed λ-term (an upper bound).
- **RASP-L** (per-step policy, H = 9 formula levels): decision 492 primitive ops, attention depth 41, 96 flagged
  non-RASP-L ops; rendering 52 ops (+3 layers); total 544 ops / 6,991 source tokens / 401 lines.
  - Scaling: ops = 240 + 28·H, depth = 5 + 4·H.
  - Effective depth per state (the smallest program that still decides it): 4 (premise lines), 8.0 (excluded
    middle), 9.5 (splits), 13.2 (fixed lemma-box steps), 14.4 (after-recursion steps), 17.2 [13, 33] (recursion
    steps). Source: `kalmar_complexity/programs/rasp/results.json`.
- **Decision procedure:** 21 generic state features → 40 action templates. The smallest exact tree found (beam 3)
  has 46 leaves / 45 tests / **626 bits** (`artifacts/kc/dtree/tree_u_b3.json`).
  - It is conditional on its feature extractor: `features.py` + `policy.py` is 3,962 B DEFLATE (mechanical upper
    bound). Most of the algorithm sits in the features.
- **Levin's Kt** = program bits + log2 running time adds 9–15 bits to programs of 1,600–11,000 bits. For whole
  proofs it carries no extra information:
  - Python: K-sl 6,921 (500 calls / theorem);
  - BLC: K-sl 5,458 (median 39,136 β-steps). Sources: `artifacts/kc/kt_python.json`, BLC `results.json`.

### Q2 — calibration (the same languages)

| algorithm | Python DEFLATE B (builtins / none) | BLC bits | binary CL bits | Kt (BLC bits + log2 median β) | RASP-L ops / attention depth |
|---|---|---|---|---|---|
| copy | 15 | 4 | 8 | 9 | 7 / 3 |
| reverse | 21 | 87 | 197 | 93 | 6 / 2 |
| parity | 22 / 43 | 82 | 185 | 89 | 31 / 5 (parity_sp) |
| sort | 11 / 87 | 257 | 749 | 266 | 14 / 2 (sort_rep) |
| addition (binary) | 19 / 100 | 375 | 1,163 | 384 | 60 / 7 |
| eval (formula truth value) | 105 | 273 | 713 | 279 | 61 / 13 |
| taut (truth-table validity) | 222 | 410 | 1,430 | 420 | 63 / 13 |
| Kalmár tt (algorithm) | 378 | 1,636 | 7,442 | 1,649 | — |
| Kalmár sl (algorithm) | 864 | 5,443 | 23,921 | 5,458 | 492 / 41 (per-step policy) |

- **Rank agreement** across the 9 items (Spearman, `artifacts/kc/rank_agreement.json`): Python DEFLATE vs BLC
  **+0.97**, vs binary CL +0.93, vs RASP-L +0.95; BLC vs RASP-L +0.86.
  - Python with builtins breaks it: vs BLC +0.75, vs binary CL +0.67. Builtins sort in 9 bytes.
- **Kalmár sl is the largest item in every language:** 13× taut in BLC, 3.9× in Python DEFLATE, 7.8× taut in
  RASP-L ops.
- **K12 generator** (`gen.py`, mechanical upper bound with all knobs): 5,324 B DEFLATE, against K-sl's mechanical
  2,416 B (2.2×). The proof style the control learns easily (92 % greedy) is *longer* to describe than Kalmár.
- **Learnability in our family** (from B2 below and kalmar-pretrain):
  - eval (273 BLC bits) still costs 0.25–0.28 bits/token on theorems 8,192–16,384 at every size; only M breaks
    through when trained on all 16,384 (0.024 bits/token on the next 500);
  - K12 is learned to 92 % greedy in 24k steps;
  - Kalmár (5,443 bits) is not learned exactly in 656k steps.

### Q3 — bits the network absorbs

**B1** (`kalmar_complexity/b1_preq.py` → `artifacts/kc/b1_preq.json`).
- Code: first-epoch prequential code from the logged training curves, L_preq = Σ_i loss_i × N × Δepochs_i / ln 2.
  - Curves are each checkpoint's `extra['curve']`: KAL-D every 600 s, the control every 30 s.
  - Each point is the mean of every 20th step's pre-update loss.
  - N = exact loss tokens (action + eos; `artifacts/kc/tokens_*.json`).
- EDL = L_preq − N × L∞. The headline residual is (b), the final model's held-out loss (val300 for KAL-D,
  p2/heldout for the control).

| model | N loss tokens (epoch) | first-epoch prequential code, bits | bits / token | L∞ final train / final held-out / end of epoch 1 (nats/token) | EDL (residual = final held-out) | EDL (final train) | EDL (end of epoch 1) | bias bound (steps 1–19) |
|---|---|---|---|---|---|---|---|---|
| KAL-D s0 | 255,006,351 | 1.26 × 10^7 | 0.0492 | 0.0152 / 0.0163 / 0.0296 | 6.54 × 10^6 | 6.97 × 10^6 | 1.67 × 10^6 | ≤ 1.81 × 10^5 |
| KAL-D s1 | 255,006,351 | 1.24 × 10^7 | 0.0488 | 0.0154 / 0.0168 / 0.0282 | 6.27 × 10^6 | 6.78 × 10^6 | 2.09 × 10^6 | ≤ 1.81 × 10^5 |
| KAL-D s2 | 255,006,351 | 1.24 × 10^7 | 0.0487 | 0.0139 / 0.0146 / 0.0280 | 7.06 × 10^6 | 7.31 × 10^6 | 2.12 × 10^6 | ≤ 1.81 × 10^5 |
| control s0 | 19,375,057 | 3.79 × 10^6 | 0.1955 | 0.0445 / 0.0830 / 0.0838 | 1.47 × 10^6 | 2.55 × 10^6 | 1.45 × 10^6 | ≤ 2.74 × 10^5 |
| control s1 | 19,375,057 | 3.64 × 10^6 | 0.1877 | 0.0612 / 0.0692 / 0.0741 | 1.70 × 10^6 | 1.93 × 10^6 | 1.57 × 10^6 | ≤ 2.94 × 10^5 |
| control s2 | 19,375,057 | 3.87 × 10^6 | 0.1997 | 0.0443 / 0.0808 / 0.0903 | 1.61 × 10^6 | 2.63 × 10^6 | 1.35 × 10^6 | ≤ 2.84 × 10^5 |

- **Absorbed bits:**
  - **KAL-D 6.3–7.1 × 10^6 bits** (0.66–0.74 bits per parameter), against the 5,443-bit BLC program: **×1,150–1,300**.
  - The control absorbed 1.5–1.7 × 10^6.
  - Within epoch 1 alone (residual (c)): KAL-D 1.7–2.1 × 10^6, the control 1.35–1.57 × 10^6.
- **What the logs cannot give:** per-step-type bits (only aggregate loss was logged), and steps 1–19 (never
  sampled; bounded above).
- **B1-snap** (`b1_snap.py` → `artifacts/kc/b1_snap.json`; per type `b1_snap_types.json`; an approximation):
  - Per-step-type held-out code of the 24 checkpoints on tf1200's 137,984 states, integrated over steps
    24,020–178,581 of epoch 1.
  - Its total is 1.13–1.20× the logged curve's code over the same window.
  - Per loss token the leaf steps absorb most (∧ true 0.06–0.10, ¬⊥ 0.06–0.07, ∨ true 0.05–0.07 bits/token);
    excluded middle, splits and ex falso least (0.01–0.02).

**B2** (pods; `b2_preq.py` → `artifacts/kc/b2/*.json`; summary `b2_summary.py`; per type `b2_per_type.py`).
- Block-wise prequential code over K12's first theorems; blocks at 64 · 2^k; the first block at the uniform code
  (log2 111 bits/token).
- Each block is coded by a fresh model trained (AdamW, early stopping on 10 % of the prefix) on everything before it.
- EDL = code − N × the last model's per-token code on 500 later theorems.
- **v1:** stop after 4 validations without improvement. **v2:** patience 3,000 steps, no stop before 5,000; added
  because v1 stopped the eval task after a few hundred steps.
- **The codes depend on the training budget.** Several blocks reached the step cap (20,000 steps or 30 epochs) while
  still improving, so these are upper bounds for this learner.

| run | task | size | seed | protocol | theorems | prequential bits | EDL bits | L∞ (bits/token) | prequential @ 8,192 | EDL @ 8,192 | train steps | job seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| eval_L_s0 | eval | L | 0 | v1 | 16,384 | 2.23 × 10^5 | 1.68 × 10^5 | 0.1051 | 1.19 × 10^5 | 16,153 | 23,750 | 4,242 |
| k12_L_s0 | k12 | L | 0 | v1 | 16,384 | 3.87 × 10^5 | 1.79 × 10^5 | 0.1012 | 2.70 × 10^5 | 1.54 × 10^5 | 28,666 | 5,007 |
| kal_L_s0 | kal | L | 0 | v1 | 8,192 | 1.37 × 10^6 | 1.06 × 10^6 | 0.0233 | 1.37 × 10^6 | 1.06 × 10^6 | 102,981 | 11,597 |
| kal_M_s0 | kal | M | 0 | v1 | 16,384 | 1.69 × 10^6 | 1.10 × 10^6 | 0.0217 | 1.39 × 10^6 | 1.10 × 10^6 | 122,333 | 9,926 |
| kal_M_s1 | kal | M | 1 | v1 | 16,384 | 1.77 × 10^6 | 1.08 × 10^6 | 0.0255 | 1.44 × 10^6 | 1.12 × 10^6 | 123,338 | 6,683 |
| kal_S_s0 | kal | S | 0 | v1 | 16,384 | 3.37 × 10^6 | 1.32 × 10^6 | 0.0756 | 2.35 × 10^6 | 1.32 × 10^6 | 122,755 | 4,621 |
| kal_S_s1 | kal | S | 1 | v1 | 16,384 | 3.38 × 10^6 | 1.46 × 10^6 | 0.0708 | 2.44 × 10^6 | 1.50 × 10^6 | 125,140 | 3,557 |
| v2_eval_L_s0 | eval | L | 0 | v2 | 16,384 | 1.72 × 10^5 | 1.17 × 10^5 | 0.1051 | 1.07 × 10^5 | 42,330 | 34,770 | 6,981 |
| v2_eval_M_s0 | eval | M | 0 | v2 | 16,384 | 1.63 × 10^5 | 1.50 × 10^5 | 0.0241 | 95,481 | 27,895 | 34,770 | 4,262 |
| v2_eval_S_s0 | eval | S | 0 | v2 | 16,384 | 1.77 × 10^5 | 78,237 | 0.1887 | 1.03 × 10^5 | 29,515 | 34,770 | 1,631 |
| v2_k12_L_s0 | k12 | L | 0 | v2 | 16,384 | 3.88 × 10^5 | 1.79 × 10^5 | 0.1014 | 2.69 × 10^5 | 1.52 × 10^5 | 35,308 | 7,211 |
| v2_k12_M_s0 | k12 | M | 0 | v2 | 16,384 | 4.23 × 10^5 | 2.18 × 10^5 | 0.0998 | 3.00 × 10^5 | 1.78 × 10^5 | 34,681 | 4,443 |
| v2_k12_S_s0 | k12 | S | 0 | v2 | 16,384 | 6.45 × 10^5 | 3.21 × 10^5 | 0.1574 | 4.65 × 10^5 | 2.88 × 10^5 | 38,130 | 2,149 |

- **Kalmár under the small learners:**
  - Over 16,384 theorems S codes 3.37 / 3.38 × 10^6 bits (EDL 1.32 / 1.46 × 10^6, seeds 0 / 1); M 1.69 / 1.77 × 10^6
    (EDL 1.10 / 1.08 × 10^6).
  - Over 8,192 theorems (the common prefix): S 2.35 / 2.44, M 1.40 / 1.44, L 1.37 × 10^6.
  - M and L are ≈ 40 % below S, far beyond the S and M seed spreads (3.8 %, 3.5 %). L vs M (1.5–5 %) is inside the
    spread: not resolved.
- **Absorbed bits:** EDL is 1.06–1.46 × 10^6, i.e. **195–270× the 5,443-bit BLC program**.
- **The asymptote is a floor that data barely moves.**
  - Held-out code after the last block: S 0.071–0.076, M 0.022–0.026, L 0.023 bits/token.
  - M trained on 16,384 theorems (10 % of K12) ends where KAL-D ends (9.6 M, all 155,000, 3.7 epochs): 0.0235
    bits/token held-out.
- **Reference tasks** (v2 protocol; one seed), over 16,384 theorems:
  - K12: prequential 3.9–6.4 × 10^5, EDL 1.8–3.2 × 10^5;
  - eval: 1.6–1.8 × 10^5, EDL 0.8–1.5 × 10^5.
  - Ordering Kalmár > K12 > eval, at every size.
  - Per theorem at 16,384 theorems: Kalmár 66–89 absorbed bits (S, M), K12 11–20, eval 5–9.
- **Shape** (excess bits per token by block, `b2_summary.json`):
  - Kalmár and K12 fall monotonically: Kalmár 0.9 → 0.2 bits/token after 128 theorems, then near 0.
  - eval plateaus at ≈ 0.28–0.35 for 6–8 blocks before falling, and only size M breaks through within the budget.
- **By step type** (`artifacts/kc/b2_per_type_table.json`; per loss token over the coded blocks):
  - highest ∧ true, ∨ true, ¬⊥, →I-A-false (and premise lines, which pay for the first name);
  - lowest excluded middle, close, split.
  - Across the 15 types these small-model bits rank KAL-D's error at ρ = +0.82 (L), +0.85 (M), +0.82 (S); given
    frequency +0.69 to +0.75.

**B3 — the causal test** (pre-registration addendum 2).
- Design: size M on Kalmár [0, 8,192), 3 paired seeds; standard states (STD) vs states that also show the next needed
  subformula (FOC). Same algorithm, actions and proofs. `b3_focus.py`, `b3_analysis.py` → `artifacts/kc/b3_summary.json`.
- **Openers** (states that need the search; 23,573 of tf1200's 137,984, 17 %): teacher-forced error **31.96 → 1.94 % (−94 %)**, every
  seed pair. ∧ true 46.8 → 3.2, ¬⊥ 36.7 → 0.0, ∨ true 31.7 → 3.6, →I-B-true 15.9 → 2.1 %.
- **Other states:** 2.44 → 1.70 % (−30 %) as pre-registered; 1.40 → 0.65 % (−53 %) without the 1,200 first states,
  whose first name the trainer's name shift leaves undetermined in both arms.
- **The demand–error correlation disappears:** across types, error vs in-scope lookups ρ = +0.61 (STD) → −0.02 (FOC);
  first states out, +0.92 → +0.27.
- Held-out loss: 0.0153–0.0169 → 0.0044–0.0053 nats/token.

### Q4 — which measure predicts where the model fails?

- **Outcome:** KAL-D's teacher-forced error per step type on tf1200 (kalmar-pretrain's stored verdicts; joined by
  `q4_join.py`, overall agreement reproduced exactly). 15 step types with ≥ 500 states.
- **Predictors** (`q4_states.py`, `q4_analysis.py`):
  - **explored:** the number of in-scope lookups the post-order search for the next needed subformula makes;
  - **log2_ops:** log2(1 + policy.py's operations) — Levin's Kt minus the constant program;
  - **target_h / focus_h:** formula heights;
  - **decl_len:** the tokens of the formula written;
  - **py_bytes:** the bytes of the code in `ksl_alg.py` that emits the step;
  - **rasp_*:** RASP-L depth / ops on the step's decision path;
  - **log_freq:** a data baseline.

| predictor (per step type) | ρ, KAL-D 3-seed mean (p) | ρ s0 / s1 / s2 | ρ, KAL-D+A mean |
|---|---|---|---|
| b2_bits_M | +0.85 (0.000) | +0.92 / +0.80 / +0.79 | +0.62 |
| rasp_eff_depth | +0.85 (0.000) | +0.74 / +0.87 / +0.89 | +0.90 |
| rasp_cone_depth | +0.84 (0.000) | +0.75 / +0.89 / +0.91 | +0.91 |
| b2_bits_S | +0.82 (0.000) | +0.86 / +0.78 / +0.79 | +0.63 |
| b2_bits_L | +0.82 (0.001) | +0.91 / +0.78 / +0.77 | +0.59 |
| rasp_cone_ops | +0.82 (0.000) | +0.73 / +0.87 / +0.89 | +0.89 |
| explored | +0.82 (0.000) | +0.77 / +0.86 / +0.88 | +0.85 |
| log2_ops | +0.78 (0.001) | +0.69 / +0.81 / +0.82 | +0.84 |
| target_h | +0.78 (0.001) | +0.72 / +0.79 / +0.83 | +0.79 |
| tree_path | -0.76 (0.001) | -0.65 / -0.80 / -0.82 | -0.85 |
| snap_final_nats_per_tok | +0.73 (0.003) | +0.78 / +0.68 / +0.64 | +0.56 |
| log_freq | -0.60 (0.020) | -0.68 / -0.61 / -0.50 | -0.56 |
| py_bytes | -0.55 (0.038) | -0.62 / -0.52 / -0.46 | -0.43 |
| py_tokens | -0.52 (0.048) | -0.62 / -0.50 / -0.44 | -0.41 |
| act_len | +0.52 (0.051) | +0.55 / +0.55 / +0.55 | +0.33 |
| focus_h | +0.49 (0.066) | +0.44 / +0.59 / +0.62 | +0.50 |
| decl_len | +0.42 (0.119) | +0.47 / +0.39 / +0.43 | +0.15 |
| depth | +0.27 (0.325) | +0.16 / +0.34 / +0.39 | +0.39 |
| rasp_descent | +0.25 (0.361) | +0.29 / +0.20 / +0.12 | +0.18 |
| state_len | +0.12 (0.658) | +0.07 / +0.15 / +0.25 | +0.25 |
| ref_dist | -0.06 (0.821) | -0.00 / -0.05 / -0.01 | -0.12 |

| seed | LR χ² (df 9), demand added to step type | p | best single measure (LR, df 1) |
|---|---|---|---|
| kalD_s0 | 6,687 | 0 | explored (5,751) |
| kalD_s1 | 7,651 | 0 | explored (6,374) |
| kalD_s2 | 6,043 | 0 | explored (4,936) |

- **Partial Spearman given log frequency** (KAL-D mean): RASP-L effective depth +0.85 (p < 0.001), lookups +0.79
  (p < 0.001), log2 ops +0.76 (p 0.001), target height +0.78 (p < 0.001), Python code bytes **−0.08** (p 0.77). The
  negative raw ρ of program length is frequency.
- **Error classes** (KAL-D s2, kalmar-pretrain's `error_classes`, 6,903 disagreements;
  `artifacts/kc/q4/error_classes.json`):
  - "other subformula" (45 %) rises with RASP-L depth (ρ = +0.94) and lookups (+0.93);
  - "corrupted" (31 %) with lookups (+0.76);
  - "malformed" (6 %) with the declared formula's length (+0.86).
- **False-formula assertions** (kalmar-pretrain's `error_truth.py` rule, by type; `q4_error_truth.py` →
  `artifacts/kc/q4/error_truth_by_type.json`):
  - Totals reproduced: 6,903 disagreements, 4,002 scored, 671 false.
  - Per 1,000 states: ∧ true 39.2, ∨ true 36.1, →I A-false 16.1, →I B-true 14.5, the other leaf types 4–8, structural
    steps 0.
  - Spearman: RASP-L depth +0.81, lookups +0.81, focus height +0.75, Python code bytes −0.27 (n.s.).

| step type | error KAL-D s0 / s1 / s2 | error KAL-D+A mean | rasp_eff_depth | rasp_cone_depth | explored | log2_ops | target_h | focus_h | decl_len | py_bytes | log_freq | snap_final_nats_per_tok | b2_bits_S | b2_bits_M | b2_bits_L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| leaf:and+ | 39.6 / 38.5 / 25.6 % | 10.2 % | 17.8 | 41 | 4.43 | 6.41 | 3.56 | 2.13 | 12.5 | 39 | 5.29 | 0.0513 | 0.33 | 0.126 | 0.171 |
| leaf:bot- | 36.0 / 23.0 / 18.5 % | 10.6 % | 18.2 | 41 | 3.45 | 5.91 | 3.59 | 0 | 4 | 33 | 4.78 | 0.0467 | 0.176 | 0.125 | 0.166 |
| leaf:or+ | 27.7 / 28.5 / 21.0 % | 7.1 % | 17.5 | 41 | 3.24 | 6.21 | 3.62 | 2.4 | 14.4 | 62 | 5.65 | 0.0396 | 0.301 | 0.116 | 0.146 |
| leaf:imp+B | 18.2 / 16.9 / 14.6 % | 2.5 % | 15.2 | 32 | 1.48 | 4.84 | 2.25 | 2.54 | 22 | 64 | 5.91 | 0.0197 | 0.12 | 0.0499 | 0.064 |
| leaf:imp+A | 10.3 / 11.0 / 10.6 % | 2.6 % | 15 | 29 | 1.18 | 3.77 | 1.46 | 2 | 9.96 | 78 | 5.57 | 0.0183 | 0.176 | 0.0694 | 0.082 |
| leaf:and- | 6.8 / 10.6 / 10.2 % | 3.0 % | 14.4 | 29 | 1.2 | 3.12 | 1.02 | 1.63 | 5.16 | 96 | 5.99 | 0.0188 | 0.128 | 0.0406 | 0.0505 |
| leaf:not+ | 7.9 / 10.7 / 9.0 % | 2.5 % | 15.1 | 32 | 1.79 | 3.77 | 1.88 | 2.25 | 6.94 | 82 | 5.88 | 0.0158 | 0.127 | 0.0489 | 0.0621 |
| pr | 13.0 / 6.9 / 5.7 % | 0.1 % | 4 | 4 | 0 | 0 | 0 | 0 | 12 | 23 | 5.45 | 0.173 | 0.317 | 0.213 | 0.228 |
| leaf:or- | 7.3 / 10.5 / 7.5 % | 2.4 % | 14.1 | 27.5 | 1.22 | 2.31 | 0.82 | 1.02 | 3.67 | 122 | 5.84 | 0.0171 | 0.115 | 0.0388 | 0.0515 |
| leaf:imp- | 7.1 / 8.2 / 7.9 % | 1.6 % | 14.1 | 29 | 1.25 | 3.07 | 1.1 | 2.64 | 7.69 | 66 | 5.89 | 0.013 | 0.141 | 0.049 | 0.068 |
| split | 3.4 / 2.3 / 3.3 % | 0.2 % | 10 | 10 | 0 | 1.16 | 0 | 0 | 22.1 | 108 | 6.08 | 0.00343 | 0.0396 | 0.0105 | 0.0176 |
| efq | 1.4 / 1.8 / 1.6 % | 0.2 % | 14.4 | 24 | 1 | 4.27 | 2.14 | 0 | 8.13 | 100 | 6.21 | 0.00411 | 0.104 | 0.0174 | 0.0295 |
| end | 0.4 / 1.9 / 0.6 % | 0.4 % | 9 | 9 | 0 | 1.85 | 0 | 0 | 0 | 8 | 5.19 | 0.0191 | 0.0672 | 0.0216 | 0.037 |
| close | 0.3 / 1.4 / 0.6 % | 0.2 % | 11.8 | 18 | 0.228 | 1.77 | 0.691 | 0.723 | 0 | 159 | 6.73 | 0.00961 | 0.0227 | 0.00601 | 0.00985 |
| lem | 0.1 / 0.9 / 0.2 % | 0.0 % | 8.05 | 8.29 | 0 | 0.572 | 0 | 0 | 6.29 | 206 | 6.5 | 0.0071 | 0.0239 | 0.00489 | 0.00771 |

### Pre-registered expectations against outcomes

| pre-registered (point; range) | outcome | verdict |
|---|---|---|
| K-sl algorithm, Python raw / DEFLATE / xz bytes: 1,300 (900–1,900) / 650 (450–900) / 650 (450–950) | 1,907 / 864 / 906 | raw just above the range; DEFLATE, xz inside |
| K-sl rendering to `lean_seq`, Python DEFLATE: 350 (200–600) | 562 | inside |
| K-tt (algorithm + Lean), Python DEFLATE: 600 (400–850) | 866 | just above |
| K-sl algorithm, Qwen3 tokens: 450 (300–700) | 897 | above |
| K-sl algorithm, BLC: 3,000 (1,500–5,000) | 5,443 | **above** |
| K-tt algorithm, BLC: 2,300 (1,200–4,000) | 1,636 | inside |
| rendering, BLC: 1,000 (400–2,500) | K-sl 616 / K-tt 4,204 | K-sl inside; K-tt above |
| binary CL / BLC ratio: 2.5 (1.5–4) | Kalmár 4.4–4.5; calibration 2.0–3.5 | Kalmár above (plain bracket abstraction) |
| RASP-L per-step policy: 130 ops (70–250) / depth 15 (8–30) | 492 ops / depth 41 (effective 4–33, recursion steps 17.2 mean) | **missed, ≈ 4× and ≈ 3×** |
| decision procedure: 35 leaves (15–80) / 400 bits (150–1,000) | 46 leaves / 626 bits | inside |
| feature extractor, Python DEFLATE: 500 (300–800) | ≤ 3,962 (mechanical, with all of policy.py) | above as measured (upper bound); "most of the algorithm sits in the features" holds |
| calibration, BLC: copy 4 / reverse 50 / parity 50 / addition 200 / sort 250 / eval 200 / taut 350 | 4 / 87 / 82 / 375 / 257 / 273 / 410 | all within 2×; mostly under-estimated |
| Kalmár rank 1 in Python-DEFLATE, BLC, binary CL, RASP-L; ≥ 5× the next item in BLC | rank 1 in all four; K-sl 13× taut | held (K-tt alone would be 4×) |
| K12 generator larger than K-sl (1.2–3×), Python DEFLATE | 2.2× (mechanical vs mechanical) | held |
| rank agreement Python-DEFLATE vs BLC ≥ 0.8; RASP-L disagrees on parity / addition | +0.97; RASP-L vs BLC +0.86 (parity needs a scratchpad in RASP-L: rank 5 vs 8) | held; disagreement only on parity |
| B1 KAL-D first-epoch prequential code: 1.5 × 10^7 (0.5–4 × 10^7) (not blind for s0) | 1.24–1.26 × 10^7 | inside |
| B1 KAL-D EDL, residual = final train loss: 6 × 10^6 (10^6–2 × 10^7) | 6.8–7.3 × 10^6 | inside |
| B1 control EDL: 2 × 10^6 (10^5–10^7); KAL-D > control (60 %) | 1.9–2.6 × 10^6 (final train) / 1.5–1.7 × 10^6 (held-out); KAL-D ≈ 4× control | held |
| absorbed bits / K-sl BLC bits ≈ 2,000 (100–20,000); ≥ 100 for every estimate | B1 1,150–1,300 (held-out residual); B2: B2 195–270× (EDL 1.06–1.46 × 10^6) | held (≥ 100 everywhere) |
| B2 Kalmár L over 8,192 theorems: 3 × 10^6 (0.6–12 × 10^6) | 1.37 × 10^6 bits | inside the range |
| B2: K12's EDL below Kalmár's at equal theorems; eval's below both | at 16,384 theorems, EDL Kalmár 1.1–1.5 × 10^6 > K12 1.8–3.2 × 10^5 > eval 0.8–1.5 × 10^5 at every size | held |
| B2 size dependence: L < M < S for Kalmár | at 8,192: S 2.35 / 2.44, M 1.40 / 1.44, L 1.37 × 10^6 | M, L < S held; L < M not resolved (inside the seed spread) |
| B2 bits per occurrence highest for ∧+, ∨+, ¬⊥, →I-B-true; lowest for close, lem, split | highest ∧ true, ∨ true, ¬⊥, →I-A-false (→I-B-true mid-table); lowest excluded middle, close, split | mostly held (→I-B-true wrong) |
| B2 EDL per token: Kalmár rises then falls; K12 and eval fall monotonically | Kalmár and K12 fall monotonically; eval plateaus, then falls | **missed** (the teaching-like shape is eval's, not Kalmár's) |
| best predictor of per-step-type error: computational demand (declared-formula length or evaluation height), ρ ≥ 0.6 | best: RASP-L decision depth +0.85, in-scope lookups +0.82, target height +0.78; declared length +0.42, focus height +0.49 | the class (demand) held; the two named sub-measures were not the best (declared length fails the bar) |
| program length (any language) vs per-type error: \|ρ\| < 0.4 | Python code bytes −0.55 (p 0.04); given frequency −0.08 | raw ρ outside (negative, = frequency); no predictive value once frequency is controlled |
| frequency baseline ρ between −0.4 and −0.7 | −0.60 | held |
| B2 per-type bits vs KAL-D error: ρ ≥ 0.7 | +0.82 (L), +0.85 (M), +0.82 (S) | held |
| state level: demand adds to step type, LR p < 0.01 in each seed | LR χ² 6,043–7,651 (df 9), p ≈ 0 in all three seeds | held |
| B1-snap per-type code of final KAL-D ranks types like TF error, Spearman ≥ 0.8 (addendum) | +0.73 (seeds +0.64 to +0.78) | missed |
| recommendation: a learner-relative EDL plus a per-step demand profile, not program length | see `run_kalmar_complexity.md` | as expected |
| B3 (addendum 2): opener error falls ≥ 50 % (FOC vs STD) | −94 % (31.96 → 1.94 %) | held |
| B3: other-state error changes < 30 % | −30 % as pre-registered (−53 % without first states) | **missed** narrowly: FOC also helps the other steps |
| B3: ∧ true, ∨ true, ¬⊥, →I-B-true each fall ≥ 40 % | −93 / −89 / −100 / −87 % | held |
| B3: across-type ρ(error, lookups) ≥ 0.6 under STD, ≤ 0.3 under FOC | +0.61 → −0.02 (first states out +0.92 → +0.27) | held |
| B3 falsified if opener error falls < 25 % | −94 % | not falsified |

### Compute (`kalmar_complexity/compute_rows.py` → registry rows, `artifacts/kc/compute_table.md`)

| arm | seed | GPU-seconds (A40, wall; shared card) | training steps | training tokens | generated tokens | Lean checks | source |
|---|---|---|---|---|---|---|---|
| B2 eval L | 0 | 4,290 | 23,750 | 431,051,916 | 0 | 0 | `artifacts/kc/b2/eval_L_s0.json` |
| B2 k12 L | 0 | 5,059 | 28,666 | 518,589,518 | 0 | 0 | `artifacts/kc/b2/k12_L_s0.json` |
| B2 kal L | 0 | 11,851 | 102,981 | 1,883,775,051 | 0 | 0 | `artifacts/kc/b2/kal_L_s0.json` |
| B2 kal M | 0 | 10,345 | 122,333 | 2,238,434,081 | 0 | 0 | `artifacts/kc/b2/kal_M_s0.json` |
| B2 kal M | 1 | 6,907 | 123,338 | 2,257,035,059 | 0 | 0 | `artifacts/kc/b2/kal_M_s1.json` |
| B2 kal S | 0 | 4,854 | 122,755 | 2,246,376,691 | 0 | 0 | `artifacts/kc/b2/kal_S_s0.json` |
| B2 kal S | 1 | 3,742 | 125,140 | 2,290,292,487 | 0 | 0 | `artifacts/kc/b2/kal_S_s1.json` |
| B2 eval L v2 | 0 | 7,039 | 34,770 | 631,930,880 | 0 | 0 | `artifacts/kc/b2/v2_eval_L_s0.json` |
| B2 eval M v2 | 0 | 4,301 | 34,770 | 631,930,880 | 0 | 0 | `artifacts/kc/b2/v2_eval_M_s0.json` |
| B2 eval S v2 | 0 | 1,652 | 34,770 | 631,930,880 | 0 | 0 | `artifacts/kc/b2/v2_eval_S_s0.json` |
| B2 k12 L v2 | 0 | 7,272 | 35,308 | 639,902,966 | 0 | 0 | `artifacts/kc/b2/v2_k12_L_s0.json` |
| B2 k12 M v2 | 0 | 4,486 | 34,681 | 628,406,847 | 0 | 0 | `artifacts/kc/b2/v2_k12_M_s0.json` |
| B2 k12 S v2 | 0 | 2,171 | 38,130 | 691,619,885 | 0 | 0 | `artifacts/kc/b2/v2_k12_S_s0.json` |
| B1-snap (24 checkpoints on tf1200) | — | 1,146 | 0 | 0 | 0 | 0 | `artifacts/kc/b1_snap.json` |
| B3 FOC M | 0 | 3,686 | 20,000 | 366,525,332 | 0 | 0 | `artifacts/kc/b3/FOC_s0.json` |
| B3 FOC M | 1 | 3,702 | 20,000 | 366,498,713 | 0 | 0 | `artifacts/kc/b3/FOC_s1.json` |
| B3 FOC M | 2 | 3,694 | 20,000 | 366,522,255 | 0 | 0 | `artifacts/kc/b3/FOC_s2.json` |
| B3 STD M | 0 | 3,674 | 20,000 | 366,541,223 | 0 | 0 | `artifacts/kc/b3/STD_s0.json` |
| B3 STD M | 1 | 3,700 | 20,000 | 366,578,704 | 0 | 0 | `artifacts/kc/b3/STD_s1.json` |
| B3 STD M | 2 | 3,688 | 20,000 | 366,536,069 | 0 | 0 | `artifacts/kc/b3/STD_s2.json` |

Spend: **$5.00 of $15, 8.46 pod-hours of 40** (`podrm` at deletion: kc-1 3.45 h $2.04, kc-2 3.86 h $2.28, kc-3 1.15 h $0.68;
three A40s, secure cloud, billed $0.59/h; community RTX 3090s were out of stock). RunPod's billing API showed $3.76 at
17:17 UTC (kc-1 $1.79, kc-2 $1.78, kc-3 $0.19; still settling); reconcile with `mcp__runpod__list-pod-billing` for pods s0bg3yd9udfgc7,
qgmm0ynsc8bjfn, 91q9okzxycqamz. Compute matching: B3's two arms are matched (20,000 steps, ≈ 3.67 × 10^8 training tokens
each); B2's sizes are not matched by design (a larger model costs more per step), and Kalmár L used 1.1–3.2× the GPU-seconds
of S / M (over half the theorems; flagged per policy). Lean checks: 0 (nothing is judged); generated tokens: 0.. Bucket: `hf://buckets/dan-pandori/nd-rl/kalmar-complexity/` (`artifacts/kc`, `data/kc`, the
programs and figures are in git).


## style-edl (2026-10-23, executor; UNREVIEWED)

**Question.** Does EDL rise with the style of the target proofs when the learner's capability on the theorems is held
fixed? Pre-registration: `preregistration/style-edl.md` (+ Addendum 1, committed before any stream but S_own was scored).

**Models (every number here names one of these):**
- **Learners L_s, s0–s2:** best-state's `ckpts/bs/stage1_best12_s{0,1,2}_b1200.pt` (bucket `best-state/ckpts/bs/`; md5
  9c436c35 / f7ae9a9e / 354c4428, checked on every pod). 9,560,832-param ALiBiGPT 6 × 384, `lean_staten`, from scratch
  on K12 (`data/kh/train_k12.jsonl`, 155,000, md5 800b5486…), 1,200 s on an A40. These are kalmar-pretrain's control.
- **EI r8 (S_RL's proofs only):** best-state's `ckpts/bs/ladder/la_T1_best12_s{0,1,2}_r8.pt` (md5 991a0ac8 / 164a6c17 /
  d43c0381): 8 EI rounds from L_s on `rl_targets.jsonl` (k 32, T 0.8). Learner s gets its own base's ladder.
- **θ\*:** L_s fine-tuned by A_ES on the 128 stream proofs of one stream, at the chosen lr, order 0:
  `ckpts/style_edl/s{s}/{stream}/theta_es_lr{lr}_E0_o0.pt`. All 54 (3 lrs per cell) are in the bucket.

**Protocol (as pre-registered unless marked).**
- **Checker.** Lean alone decides: `lean_gate` on the literal text for every sampled proof, and Lean on the literal
  canonical `lean_seq` text for every stream proof. All 1,598 candidate proofs were accepted, and all 638 used proofs
  were re-confirmed by `lean_check`. `nd_verify` is never called. L_true labels are not used.
- **Theorems.** tf1200 (`data/kalmar/tf1200_kal_sl.jsonl`, md5 b99c3b8d; none in a K12 renaming class).
  - 632 are eligible for all three seeds: ≥ 29 / 32 Lean-valid at T 0.8 (seed 1), base and r8 greedy proofs valid, a
    valid k 4 draw (seed 3), and a minlen proof.
  - 256 were sampled (seed 20261023) and split 128 stream / 128 test by premise-order-invariant renaming class, with
    atom-count strata balanced (stream 16 / 34 / 36 / 42, test 15 / 34 / 37 / 42 for 1 / 2 / 3 / 4 atoms).
- **Reads.** Caps `max_steps` 1,024 and `max_action` 512, batch 1,024 for every read.
  - Peak memory: 7.5–7.7 GB for the greedy reads (`kal_free.py`'s `peak_alloc_gb`). `guided_eval.py` does not record it.
    One guided read of a Kalmár-trained θ* ran out of memory at ≥ 15.6 GB while sharing a 24 GB card. It was redone
    alone on an A40 (below).
  - Truncation (`max_action` hit): 144 of 390,752 attempts (0.04 %). 108 are in seed 1's S_Kal θ* plain read (1.3 % of
    its 8,192, above the policy's 0.1 % line), 9 in the other S_Kal θ* reads, 24 in the learners' reads, 3 in the
    other θ* reads. `max_steps` was never hit. A truncated action is > 512 tokens, against the longest action of any
    Kalmár proof (219), so these attempts are degenerate loops; a larger cap would not make them valid.
- **Scoring.** Teacher-forced NLL of the action tokens + `<eos>` in bits (fp32). Environment-assigned names are not
  coded (`kalmar/tf_agree.masked`). One name base per theorem.
- **A_ES.**
  - Optimiser: AdamW (0.9, 0.95, wd 0), constant lr, clip 1, 8 proofs per batch, the Stage-1 name shift.
  - Early stopping: validated on a quarter of the prefix, ≤ 8 passes, patience 2, then a refit on the whole prefix.
  - lr ∈ {1e-5, 1e-4, 1e-3}, chosen per seed × stream by the mean prequential code over two orders, + log₂ 3 bits.
  - A_fixed: E = 4 passes, chosen on the S_own pilot.
- **EDL and EDL_c.** EDL = Σ block bits − 128 × L_test. EDL_c subtracts the learner's own stream / test mismatch (same
  expectation). Cross-fit = the same protocol with the halves swapped, averaged (exploratory, post hoc).
- **Capability.** k 32, T 0.8, sample seed 2 (not the selection seed), on the 128 test theorems. Reported plain
  (primary) and guided (`--arm logical`, ≤ 10 rejections).
- **ℓ_V.** −log₂ Σ_{y ∈ V(x)} p(y | x) over V(x) = 2,852 distinct Lean-valid proofs collected for the 256 theorems
  (`data/style_edl/vset.jsonl`). It is computed on re-fits of the chosen-lr runs.
  - Their single-string bits match phase 4 to ≤ 0.03 bits per proof per block on the short streams, and to ≤ 2.1 bits
    on Kalmár's ≈ 300-bit proofs (memory-efficient attention's backward is not bit-deterministic).
  - EDL_c agrees to ≤ 0.003 bits per proof (short streams) and ≤ 0.17 (Kalmár, of ≈ 180).
- **Aggregation.** Per-seed values; with n = 3 the IQM is the mean. Floor F = 0.1 bits per proof (the pre-registered
  minimum; the measured parts were ≤ 0.043).

Per-seed values are s0 / s1 / s2; "mean" is the mean over the three seeds (n = 3: the IQM is the mean). Bits per proof unless stated; names the environment assigns are not coded. EDL and EDL_c include log₂ 3 bits for the lr choice.

**Table 1 — streams and the learner (before training).**

| stream | identical to the learner's greedy proof (of 256) | actions per proof | coded tokens per proof | TF agreement (per action) | learner bits per proof, test (L0) | starting loss (block [0, 8)) |
|---|---|---|---|---|---|---|
| S_own | 1.000 / 1.000 / 1.000 | 4.52 / 4.55 / 4.44 | 79.4 / 79.7 / 78.0 | 0.9965 / 0.9974 / 0.9982 | 0.37 / 0.27 / 0.24 | 0.58 / 0.52 / 0.47 |
| S_own2 | 0.910 / 0.926 / 0.934 | 4.71 / 4.74 / 4.68 | 82.0 / 82.7 / 82.0 | 0.9776 / 0.9860 / 0.9800 | 0.66 / 0.61 / 0.61 | 1.56 / 0.56 / 0.74 |
| S_seed | 0.941 / 0.938 / 0.941 | 4.55 / 4.44 / 4.52 | 79.7 / 78.0 / 79.4 | 0.9862 / 0.9859 / 0.9844 | 0.43 / 0.40 / 0.35 | 0.81 / 1.94 / 0.88 |
| S_RL | 0.945 / 0.922 / 0.938 | 4.64 / 4.64 / 4.52 | 81.3 / 81.3 / 79.6 | 0.9848 / 0.9756 / 0.9836 | 0.78 / 0.87 / 1.26 | 1.83 / 1.26 / 1.43 |
| S_short | 0.871 / 0.848 / 0.883 | 4.26 / 4.26 / 4.26 | 74.3 / 74.3 / 74.3 | 0.9578 / 0.9578 / 0.9633 | 0.94 / 0.79 / 1.07 | 3.29 / 2.83 / 3.18 |
| S_Kal | 0.000 / 0.000 / 0.000 | 116 / 116 / 116 | 1716 / 1716 / 1716 | 0.2736 / 0.3123 / 0.2273 | 1283 / 1236 / 1339 | 1340 / 1255 / 1411 |

**Table 2 — EDL (A_ES, lr chosen per seed × stream by prequential code).**

| stream | lr (s0 / s1 / s2) | θ* test loss L_test | EDL per proof | EDL_c per proof | mean EDL_c | EDL_c per action | cross-fit EDL per proof (exploratory) | A_fixed (E = 4) EDL_c |
|---|---|---|---|---|---|---|---|---|
| S_own | 1e-05 / 1e-05 / 1e-05 | 0.13 / 0.19 / 0.11 | 0.10 / 0.02 / 0.06 | 0.04 / -0.00 / 0.04 | 0.03 | 0.009 / -0.001 / 0.008 | 0.07 / 0.01 / 0.05 | 0.07 / 0.03 / 0.05 |
| S_own2 | 1e-05 / 1e-05 / 1e-05 | 0.58 / 0.56 / 0.59 | 0.22 / -0.01 / 0.09 | 0.05 / 0.04 / 0.01 | 0.04 | 0.011 / 0.008 / 0.003 | 0.02 / 0.04 / -0.01 | 0.06 / 0.02 / 0.01 |
| S_seed | 1e-05 / 1e-05 / 1e-05 | 0.18 / 0.24 / 0.22 | 0.10 / 0.27 / 0.22 | 0.05 / 0.07 / 0.07 | 0.06 | 0.010 / 0.014 / 0.016 | 0.06 / 0.05 / 0.09 | 0.07 / 0.07 / 0.08 |
| S_RL | 1e-05 / 1e-05 / 1e-05 | 0.52 / 0.76 / 1.55 | 0.55 / 0.20 / -0.90 | 0.12 / 0.08 / -0.37 | -0.06 | 0.024 / 0.017 / -0.079 | 0.05 / 0.05 / -0.22 | 0.10 / 0.08 / 0.03 |
| S_short | 0.0001 / 0.0001 / 0.0001 | 0.17 / 0.24 / 0.23 | 0.97 / 0.91 / 0.95 | -0.34 / -0.05 / 0.07 | -0.10 | -0.079 / -0.011 / 0.017 | 0.21 / 0.10 / 0.32 | -0.30 / -0.13 / -0.03 |
| S_Kal | 0.0001 / 0.0001 / 0.0001 | 88.4 / 96.6 / 89.9 | 224 / 190 / 240 | 179 / 182 / 177 | 179 | 1.533 / 1.561 / 1.514 | 214 / 185 / 225 | 199 / 215 / 237 |

**Table 3 — capability on the 128 test theorems (k 32, T 0.8, sample seed 2; θ* = A_ES at the chosen lr, order 0).** Learner before: plain pass@32 1.000 / 1.000 / 1.000, pass@1 0.966 / 0.976 / 0.972; guided pass@32 1.000 / 1.000 / 1.000, pass@1 0.993 / 0.997 / 0.997.

| stream | plain pass@32 after | plain pass@1 after | guided pass@32 after | guided pass@1 after | capability fixed? |
|---|---|---|---|---|---|
| S_own | 1.000 / 1.000 / 1.000 | 0.985 / 0.988 / 0.983 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | yes (3 / 3) |
| S_own2 | 1.000 / 1.000 / 1.000 | 0.980 / 0.981 / 0.978 | 1.000 / 1.000 / 1.000 | 0.999 / 1.000 / 0.998 | yes (3 / 3) |
| S_seed | 1.000 / 1.000 / 1.000 | 0.988 / 0.987 / 0.986 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | yes (3 / 3) |
| S_RL | 1.000 / 1.000 / 1.000 | 0.985 / 0.978 / 0.983 | 1.000 / 1.000 / 1.000 | 0.999 / 0.998 / 1.000 | yes (3 / 3) |
| S_short | 0.992 / 1.000 / 1.000 | 0.979 / 0.970 / 0.959 | 1.000 / 1.000 / 1.000 | 1.000 / 0.998 / 0.995 | yes (3 / 3) |
| S_Kal | 0.383 / 0.352 / 0.250 | 0.029 / 0.047 / 0.015 | 0.602 / 0.602 / 0.594 | 0.118 / 0.136 / 0.103 | no (0 / 3) |

**Table 4 — the style-blind score ℓ_V (same fits, re-run at the chosen lr).**

| stream | ℓ_V of the learner, test (bits) | ℓ_V θ*, test | ℓ_V EDL per proof | ℓ_V EDL_c per proof | single-string EDL_c of the same re-fits |
|---|---|---|---|---|---|
| S_own | 0.220 / 0.146 / 0.156 | 0.036 / 0.032 / 0.046 | 0.063 / 0.056 / 0.049 | 0.042 / 0.038 / 0.039 | 0.043 / -0.005 / 0.037 |
| S_own2 | 0.220 / 0.146 / 0.156 | 0.114 / 0.077 / 0.134 | 0.054 / 0.046 / 0.013 | 0.033 / 0.028 / 0.003 | 0.054 / 0.039 / 0.014 |
| S_seed | 0.220 / 0.146 / 0.156 | 0.034 / 0.043 / 0.049 | 0.069 / 0.076 / 0.058 | 0.048 / 0.058 / 0.048 | 0.046 / 0.065 / 0.073 |
| S_RL | 0.220 / 0.146 / 0.156 | 0.059 / 0.076 / 0.055 | 0.098 / 0.040 / 0.073 | 0.076 / 0.023 / 0.063 | 0.116 / 0.082 / -0.370 |
| S_short | 0.220 / 0.146 / 0.156 | 0.069 / 0.099 / 0.083 | 0.181 / 0.221 / 0.211 | 0.160 / 0.203 / 0.200 | -0.341 / -0.045 / 0.076 |
| S_Kal | 0.220 / 0.146 / 0.156 | 12.9 / 13.1 / 12.4 | -5.095 / -5.560 / -3.961 | -5.116 / -5.578 / -3.971 | 179 / 182 / 177 |

**Table 5 — A1, the per-proof attribution (Addendum 1): proofs identical to the learner's greedy proof (*same*) and the rest (*differ*).**

| stream | differing proofs, stream / test | learner bits per differing test proof | θ* bits per differing test proof | EDL_c per differing proof | EDL_c per same proof | cross-fit, both directions pooled: per differing / per same proof (exploratory) |
|---|---|---|---|---|---|---|
| S_own2 | 12–11 / 12–7 / 10–7 | 4.24 / 7.03 / 7.50 | 4.74 / 7.57 / 7.71 | 0.15 / -0.21 / 0.13 | 0.026 / 0.023 / -0.015 | -0.30 / -0.13 / -0.12 / 0.038 / 0.033 / -0.000 |
| S_seed | 9–6 / 10–6 / 10–5 | 2.37 / 4.28 / 4.00 | 2.44 / 3.81 / 3.94 | -0.39 / -0.04 / 0.15 | 0.057 / 0.072 / 0.050 | -0.31 / -0.16 / 0.59 / 0.067 / 0.053 / 0.036 |
| S_RL | 10–4 / 11–9 / 9–7 | 14.3 / 9.52 / 19.3 | 12.6 / 8.83 / 26.7 | 1.22 / 0.97 / -7.94 | 0.084 / -0.005 / 0.063 | 0.66 / 0.53 / -5.24 / 0.071 / -0.002 / 0.032 |
| S_short | 21–12 / 26–13 / 21–9 | 6.93 / 6.08 / 12.5 | 1.07 / 1.44 / 1.44 | -0.53 / 1.52 / 5.92 | 0.154 / 0.119 / 0.146 | 0.60 / 0.93 / 4.16 / 0.141 / 0.081 / 0.101 |
| S_Kal | 128–128 / 128–128 / 128–128 | 1283 / 1236 / 1339 | 88.4 / 96.6 / 89.9 | 179 / 182 / 177 | — | 214 / 185 / 225 / — |

**Table 7 — the per-block curve (A_ES, chosen lr; seed means of the order means).** Block bits per proof for the blocks [0, 8) (the learner), [8, 16), [16, 32), [32, 64), [64, 128); then each fit's mean bits on the 128 test proofs (learner, after 8, 16, 32, 64, 128 proofs).

| stream | block bits per proof | test-set curve |
|---|---|---|
| S_own | 0.52 → 0.24 → 0.21 → 0.18 → 0.14 | 0.29 → 0.22 → 0.19 → 0.16 → 0.14 → 0.14 |
| S_own2 | 0.95 → 1.25 → 0.79 → 0.47 → 0.63 | 0.62 → 0.59 → 0.61 → 0.59 → 0.59 → 0.58 |
| S_seed | 1.21 → 0.69 → 0.43 → 0.28 → 0.31 | 0.39 → 0.33 → 0.32 → 0.27 → 0.24 → 0.21 |
| S_RL | 1.51 → 0.40 → 1.19 → 1.40 → 0.53 | 0.97 → 0.95 → 0.94 → 0.92 → 0.87 → 0.94 |
| S_short | 3.10 → 0.36 → 1.11 → 2.10 → 0.52 | 0.93 → 1.05 → 0.95 → 0.64 → 0.34 → 0.21 |
| S_Kal | 1335 → 310 → 372 → 285 → 178 | 1286 → 551 → 391 → 262 → 163 → 91.6 |

**Table 6 — compute per arm (results registry; GPU = RTX A5000, except one guided read redone on an A40; GPU-seconds are process wall time on a GPU sometimes shared by 2–3 jobs).** Summed over the three seeds.

| arm | phases | GPU-s | train steps | train tokens (M) | gen tokens (M) | Lean checks |
|---|---|---|---|---|---|---|
| S_Kal | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 26960 | 20084 | 3426.2 | 22.05 | 2071 |
| S_RL | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1730 | 12050 | 38.1 | 3.05 | 24103 |
| S_own | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1789 | 12683 | 39.0 | 3.01 | 23828 |
| S_own2 | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1529 | 8169 | 26.6 | 3.09 | 24332 |
| S_seed | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1676 | 12461 | 38.3 | 3.01 | 23921 |
| S_short | cap_logical, cap_plain, edl_es, edl_fixed, lv, xfit | 1659 | 12841 | 36.1 | 2.87 | 23720 |
| learner | cap_logical, cap_plain | 485 | 0 | 0.0 | 3.18 | 24635 |
| shared | reads | 829 | 0 | 0.0 | 13.45 | 90915 |
| other | other | 78 | 12 | 0.0 | 0.00 | 0 |

**Verdict (pre-registered rule; `style_edl/verdict.py` → `artifacts/style_edl/verdict.json`).**
- F = 0.1 bits per proof. The measured parts were |EDL_c(S_own) − EDL_c(S_own2)| ≤ 0.043 and order-to-order ≤ 0.031.
- Seeds (of 3) whose excess over S_own2 exceeds F, under EDL / EDL_c / cross-fit / ℓ_V EDL_c:
  - S_seed 2 / 0 / 0 / 0;
  - S_RL 2 / 0 / 0 / 0;
  - S_short 3 / 0 / 2 / 3;
  - S_Kal 3 / 3 / 3 / 0, with the capability criterion failed on 3 / 3 seeds.
- → **against**: no capability-fixed stream is above F under both EDL and EDL_c.
- Spearman ρ between style distance and the seed mean, over the six streams: EDL_c 0.14, EDL 0.71, cross-fit 0.54,
  ℓ_V EDL_c −0.20.

**Seed means with a bootstrap 95 % interval** (10,000 resamples of the three seeds; at n = 3 the interval is close to the seeds' min–max, `artifacts/style_edl/bootstrap.json`).

| stream | EDL per proof | EDL_c per proof | cross-fit EDL per proof | ℓ_V EDL_c per proof | plain pass@32 after |
|---|---|---|---|---|---|
| S_own | 0.058 [0.024, 0.095] | 0.025 [-0.005, 0.043] | 0.045 [0.011, 0.075] | 0.040 [0.038, 0.042] | 1.000 [1.000, 1.000] |
| S_own2 | 0.101 [-0.014, 0.225] | 0.035 [0.014, 0.054] | 0.018 [-0.007, 0.043] | 0.021 [0.003, 0.033] | 1.000 [1.000, 1.000] |
| S_seed | 0.195 [0.100, 0.269] | 0.061 [0.046, 0.073] | 0.065 [0.049, 0.088] | 0.051 [0.048, 0.058] | 1.000 [1.000, 1.000] |
| S_RL | -0.049 [-0.897, 0.555] | -0.057 [-0.370, 0.116] | -0.040 [-0.221, 0.053] | 0.054 [0.023, 0.076] | 1.000 [1.000, 1.000] |
| S_short | 0.943 [0.910, 0.968] | -0.105 [-0.340, 0.073] | 0.210 [0.098, 0.323] | 0.188 [0.160, 0.203] | 0.997 [0.992, 1.000] |
| S_Kal | 218 [190, 240] | 179 [177, 182] | 208 [185, 225] | -4.888 [-5.578, -3.971] | 0.328 [0.250, 0.383] |

**Pre-registered expectations against outcomes** (ranges were for the seed values; ✓ = all three seeds inside).

| stream | starting loss | EDL per proof | EDL_c per proof | style distance (1 − TF agreement) |
|---|---|---|---|---|
| S_own | 0.3–0.8 → 0.47–0.58 ✓ | −0.2–0.2 → 0.02–0.10 ✓ | −0.2–0.2 → −0.00–0.04 ✓ | ≤ 0.01 → 0.002–0.004 ✓ |
| S_own2 | 1.5–5 → 0.56–1.56 (1 / 3) | 0–0.5 → −0.01–0.22 (2 / 3) | 0–0.5 → 0.01–0.05 ✓ | 0.01–0.05 → 0.014–0.022 ✓ |
| S_seed | 1–3 → 0.81–1.94 (1 / 3) | 0–0.5 → 0.10–0.27 ✓ | 0–0.5 → 0.05–0.07 ✓ | 0.01–0.05 → 0.014–0.016 ✓ |
| S_RL | 1.5–8 → 1.26–1.83 (1 / 3) | 0.2–2 → −0.90–0.55 (1 / 3) | 0.2–2 → −0.37–0.12 (0 / 3) | 0.03–0.15 → 0.015–0.024 (0 / 3) |
| S_short | 5–25 → 2.83–3.29 (0 / 3) | 1–8 → 0.91–0.97 (0 / 3) | 1–8 → −0.34–0.07 (0 / 3) | 0.1–0.4 → 0.037–0.042 (0 / 3) |
| S_Kal | 200–800 → 1,255–1,411 (0 / 3) | 30–300 → 190–240 ✓ | 30–300 → 177–182 ✓ | 0.6–0.8 → 0.69–0.77 ✓ |

- **Ordering** S_own ≈ S_own2 ≈ S_seed < S_RL < S_short ≪ S_Kal. Only "≪ S_Kal" held: the seed-mean EDL_c are 0.025,
  0.035, 0.061, −0.057, −0.105 and 179. Per action, S_short and S_Kal were predicted within a factor of 3: −0.02 vs 1.54
  (missed). ρ ≥ 0.8: missed (0.14).
- **Capability.**
  - Before: plain pass@32 ≥ 0.99 ✓ (1.000).
  - After, plain pass@32 ≥ 0.98 on the five short streams ✓ (≥ 0.992); S_Kal 0.85–1.0 ✗ (0.25–0.38).
  - pass@1 before 0.93–0.98 ✓ (0.966–0.976). After: within ±0.03 for S_own / S_own2 / S_seed / S_RL ✓ (+0.002 to
    +0.022); S_short −0.10 to +0.02 ✓ (−0.013 to +0.013); S_Kal falling by 0.1–0.5 ✗ (it fell by 0.93–0.96).
- **ℓ_V.**
  - "Removes ≥ 60 % of S_short's and S_RL's EDL_c excess": not applicable, as neither had one. ℓ_V instead gives S_short
    an excess (+0.13 to +0.20, 3 / 3 above F). The intermediate fits put less mass on V(x) than the learner or θ* (e.g.
    block [16, 32), seed 0, order 1: 1.08 bits per theorem vs the learner's 0.24). Their own samples are not in V(x), so
    part of this dip may be valid proofs outside V; not checked.
  - S_Kal's EDL_V,c ≤ 20 % of its single-string EDL_c ✓ (−5.1 / −5.6 / −4.0, i.e. negative).
- **A_fixed:** the same ordering (EDL_c S_own 0.05, S_own2 0.03, S_seed 0.07, S_RL 0.07, S_short −0.15, S_Kal 217); its
  S_own EDL is positive at the chosen lr 1e-5 ✓.
- **Gate:** |EDL_c(S_own)| ≤ 0.3 on the pilot ✓ (0.043).
- **Addendum 1.**
  - S_short 0.1–1.5: EDL ✓ (0.91–0.97), EDL_c ✗ (−0.34 to 0.07), cross-fit ✓ (0.10–0.32). S_RL 0–0.8: EDL_c 2 / 3.
  - S_seed and S_RL do not clear F ✓; S_short at most even odds ✓ (it did not).
  - A1: differing proofs cost the learner 4–20 bits: S_own2 4.2–7.5 ✓, S_seed 2.4–4.3 (1 / 3; one at 3.999), S_RL 9.5–19.3 ✓,
    S_short 6.1–12.5 ✓.
  - EDL_c 0–4 bits per differing proof: single-direction −7.9 to 5.9 (4–13 differing test proofs: noisy); pooled
    cross-fit S_short 0.6 / 0.9 / 4.2, S_RL 0.7 / 0.5 / −5.2.
  - *same* proofs within ±0.2 ✓ (−0.015 to 0.154).

**Notes.**
- Table 6's "other" row is the VPS CPU smoke test of the runner (12 steps).
- S_Kal's arm used ≈ 90× the training tokens of the others, by design (its proofs are ≈ 25× longer; flagged per policy).
- The Kalmár proofs' TF agreement under the learners (0.27 / 0.31 / 0.23) reproduces kalmar-pretrain's E1 for the same
  checkpoints (0.278 / 0.302 / 0.228).
- Term size (`lean_check`, inference nodes; `artifacts/style_edl/term_sizes.json`), mean over seeds and halves:
  S_own 2.03, S_own2 2.20, S_seed 2.03, S_RL 2.11, S_short 1.88, S_Kal 96.4. ND lines: 3.50 / 3.71 / 3.50 / 3.60 / 3.26 /
  115.1.

**Sources.**
- `style_edl/results.csv`: one row per seed × stream, from `style_edl/analyze.py`.
- Per-block, per-proof losses: `artifacts/style_edl/edl/s{s}/{stream}.json`, `.fixed.json`, `edl_x/`, `lv/`.
- Capability rows: `artifacts/style_edl/cap/*.rows.jsonl.gz`.
- Reads: `artifacts/style_edl/reads/`. Streams: `data/style_edl/streams/`, `style_edl/streams_manifest.json`. V(x):
  `data/style_edl/vset.jsonl`.
- Compute: `artifacts/style_edl/compute.csv`, from the registry rows in `artifacts/style-edl/registry/`.
- Bucket: `hf://buckets/dan-pandori/nd-rl/style-edl/` (`artifacts/style_edl/`, `artifacts/style-edl/registry/`,
  `data/style_edl/`, `ckpts/style_edl/`).
