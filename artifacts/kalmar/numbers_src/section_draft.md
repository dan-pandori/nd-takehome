
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
| KAL-C | read | 31,147 | 3090 (greedy) / A40 (sampled) | 414,366,772 | 448,326 | 22,166,241 | 0 | 0 | 7,764 |
| KAL-C | train | 4,860 | RTX 3090 | 0 | 0 | 0 | 72,060 | 1,321,016,321 | 0 |
| KAL-D | read | 44,669 | 3090 (greedy) / A40 (sampled) | 542,803,368 | 473,526 | 26,675,872 | 0 | 0 | 18,494 |
| KAL-D | train | 109,305 | RTX 3090 | 0 | 0 | 0 | 1,968,855 | 36,092,382,461 | 0 |
| control | read | 11,710 | 3090 (greedy) / A40 (sampled) | 219,253,048 | 1,120,902 | 9,902,918 | 0 | 0 | 101,430 |
| ladder ei | ladder | 11,069 | A40 | 3,867,341 | 16,000 | 227,328 | 600 | 1,600,243,555 | 0 |
| ladder frozen | ladder | 7,257 | A40 | 68,951,655 | 75,100 | 4,091,326 | 0 | 0 | 2,151 |
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

LADDER_SECTION

**Pods and spend.**
- Community RTX 3090 ($0.22/h): training and greedy reads.
- A40 secure ($0.59/h): sampled reads, the ladder, and the anneal control (KAL-D+A s1 on an RTX 3090 secure, $0.50/h).
- Billed rates from `podnew` (RunPod `costPerHr`); spend from `podbudget`. Total SPEND_TOTAL of $50 (101.69 pod-hours;
  `podbudget` at 09:29 UTC, 2026-10-20). All pods deleted.

**Bucket:** `hf://buckets/dan-pandori/nd-rl/kalmar-pretrain/`.
- `ckpts/kalmar/`: KAL-D, KAL-C, snapshots, `ladder/`, `anneal/`.
- `data/kalmar/`: K12-Kalmár and the read sets.
- `artifacts/kalmar/`: read rows, ladder found files, dumps.
- Registry rows: `hf://buckets/dan-pandori/nd-rl/registry/kalmar-pretrain/`.
