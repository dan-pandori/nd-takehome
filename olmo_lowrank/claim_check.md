# Claim check: olmo-lowrank write-up

Documents: `run_olmo_lowrank.md` and `olmo_lowrank/plain_summary.md` (line numbers are those files' lines). Checked 2026-11-27
against the run's own files. Every value below was recomputed with python from `olmo_lowrank/tables/changes.csv`, `lora.csv`,
`expectations_part1.json`, `matrices_R32.csv.gz`, `overlap_R32.csv.gz`, `artifacts/olmo_lowrank/spectra/R32/full_*.npz`,
`olmo_lowrank/results.csv`, `summary.json`, `hand_cells.csv`, `hand_arm_summary.csv`, `handcheck.csv`,
`artifacts/olmo_lowrank/rows/*.csv`, `compute.csv`, `artifacts/olmo_lowrank/stage0/adapters_verify.json`,
`artifacts/olmo_lowrank/meta/f448_check.json` and `preregistration/olmo-lowrank.md`. The spend ($55.98) was taken as given.

**Totals: 84 claims. 3 WRONG, 6 FLAG, 11 ROUNDING, 64 OK.**
- WRONG: a value or a stated basis that the files contradict.
- FLAG: the number is right, but the statement gets the scope, the model or the pre-registered scoring wrong, or claims more
  precision than the data have.
- ROUNDING: fine; how it rounds is noted.
- OK: reproduced, with notes where useful.

The source tables themselves reproduce from the raw files:
- N2300 S16 0.2182 / S256 0.4282, median spike count 227 and median signal rank 2,305 come out of the full float64 spectra
  (with `floorB_s1` and floor A's σ₁).
- The LoRA medians and cosines come out of `overlap_R32.csv.gz`.
- The R rates and G come out of `hand_cells.csv`. Labelled = min(strict, 8) in all 432 cells. Every item that was read is
  among its cell's first 8 strict successes in (chunk, i) order, and the cells' strict counts match `rows/*.csv`.
- The A rates and G come out of `rows/*.csv`, with `dpo` pooled with `F_dpo_ifb` on the 176 non-reach prompts.
- An independent paired prompt bootstrap on R (10,000 replicates) reproduces `results.csv`'s intervals to ±0.003.

## run_olmo_lowrank.md

### WRONG
- **WRONG** L24, table row R, T256 "0.90". G_R(T256) = 0.8946 (`results.csv`, `summary.json`; recomputed as 0.8946 from `hand_cells.csv`), which is **0.89** to 2 dp. The 0.90 comes from rounding twice: numbers.md's 0.895 rounded again (log.md 05:36 has the same 0.90).
- **WRONG** L37 "P1 (intervals 3.4–3.8× floor A)". The S16 of the three single 50-step intervals is 3.80× floor A's 0.0075 for I_early (0.0285), **29.5×** for I_mid (0.2214) and 3.40× for I_late (0.0255) (`expectations_part1.json` P1b; `changes.csv`). The range 3.4–3.8× covers only the early and late intervals; the full range is 3.4–29.5×. The verdict is right (P1b misses, so P1 misses).
- **WRONG** L37 "E1–E2 (RL more concentrated than SFT)". That is E2's criterion only (SFT S16 0.0333 < N2300 0.2182). E1 was pre-registered as "S16(N2300) ≤ 3× the Gaussian's **and** median signal rank (floor A) ≥ 256". It misses because S16 is **29.3×** the Gaussian's (0.2182 / 0.00745; `expectations_part1.json`); its signal-rank clause holds (2,305 ≥ 256). The verdict is right, but the reason given for E1 is wrong.

### FLAG
- **FLAG** L3–4, the model list "… DPO (`dpo`), 3.1 Think RL step 2,300 (`s2300`)". Part 1 also uses the 32B RL checkpoints at steps 50, 100, 500, 750, 1,100, 1,150, 1,600, 2,100 and 2,250 (N<t>, I_*, K; the pre-registration's models table; numbers.md "steps 50–2,300"). L11's "3.3 % → 22 %" and "steps 1,100–1,150" rest on them. The list is incomplete, not wrong.
- **FLAG** L36 "Hits: … E4's T16 < 0.3, F448 ≥ 0.75 and C16 ≥ 0.5 (tentative)". The values are right: G_R 0.158 [0.101, 0.221], 0.936 [0.864, 1.019] and 0.502 [0.376, 0.634]; only C16 is tentative.
  - E4 was pre-registered as one expectation ("i.e. reading 2"). It misses because G_R(T256) = 0.89 ≥ 0.5, and the pre-registration defines no partial hits.
  - The line lists three sub-clauses under Hits, but the failing clause (T256 < 0.5) is never named under Misses; only "E4's 'high-rank' call" is.
  - P1a and E1's signal-rank clause also hold, yet they are not listed as partial hits.
- **FLAG** L42, compute. The pre-registration says "any arm above 1.25× the dpo arm's tokens is flagged". All five arms from T16 to C16 are above it: T16 1.253×, T64 1.363×, T256 1.382×, F448 1.397×, C16 1.425× (`compute.csv` gen_tokens / dpo's 6,720,092). The write-up gives only the maximum and raises no flag; numbers.md's compute table does not flag them either.

### ROUNDING
- **ROUNDING** L42 "≤ 2.5× its H200-seconds". The maximum is T256: (7,948.8 + 1,639.8 stage-0) / 3,819.9 = **2.510×** (`compute.csv`). That exceeds the stated bound by 0.01; write "≤ 2.51×" or "≈ 2.5×". The others: T16 1.55×, T64 1.75×, F448 1.42×, C16 1.75×.

### OK
- **OK** L1, title "spikes on a floor": S16 0.218 vs the Gaussian's 0.0075 (29×); the median matrix has 227 directions above matched-norm rounded noise; 57 % of ‖ΔW‖² lies beyond each matrix's top 256 (`changes.csv` N2300).
- **OK** L1, title "its top 64–256 pieces carry the gain": G(T64) 0.61 on R / 0.73 on A, G(T256) 0.89 / 0.95 (`results.csv`). This is an interpretation: the floor alone (C16) also recovers 0.50 / 0.62.
- **OK** L3 "bf16, none trained here", "32.2 B": the pre-registration's models table; log 20:48.
- **OK** L4 "$55.98 of $80": as given. It equals numbers.md's pod lines (23.27 + 25.85 + 5.10 + 1.76).
- **OK** L6: the figure `figures/olmo_lowrank.png` exists, and its curves and points match `changes.csv` / `results.csv`. Cosmetic: panel 2's title says "IFBench gain", but R includes 6 IFEval prompts.
- **OK** L8 "448 matrices": `changes.csv` has matrices = 448 for every 32B change.
- **OK** L9 "top 16 / 256 … 22 % / 43 % of ‖ΔW‖²": energy-weighted S_16 0.2182 and S_256 0.4282 (`changes.csv` N2300; recomputed from `full_*.npz`).
- **OK** L9 "noise and bf16-rounding baselines: 0.75 % / 11 %": Gaussian / floor A S_16 0.00745 / 0.00750 and S_256 0.1089 / 0.1089. The slash pairs k = 16 / 256, not noise / rounding; the two baselines agree.
- **OK** L10 "median matrix has 227 directions above same-norm rounded noise": med_spike_count 227 (recomputed as 227 from the full spectra against `floorB_s1`).
- **OK** L11 "grows over RL (3.3 % → 22 %)": S_16 0.0329 at N50 → 0.2182 at N2300; Spearman ρ 0.964 over the 7 net changes. It is not monotone: N1600 is at 0.265, above N2300.
- **OK** L11 "partly via a near-rank-1 jump at steps 1,100–1,150".
  - The data: I_mid has S_1 0.152 out of S_16 0.221 (I_early and I_late have S_1 0.007), a median stable rank of 7.0 and 3.0× I_late's ‖ΔW‖². Between N1100 and N1600, S_16 goes from 0.072 to 0.265.
  - "Near-rank-1" is a characterisation: the spike is rank-1-dominated (the log's word), but 78 % of the interval's ‖ΔW‖² lies outside its top 16.
  - "Partly via" rests on timing alone; no direction overlap between I_mid and N1600 or N2300 was computed.
- **OK** L13 "SFT's change is diffuse (3.3 %)": S32 SFT S_16 0.0333.
- **OK** L13 "DPO's most concentrated (35 %)": S_16 0.3501, the highest of the 13 32B changes.
- **OK** L13 "7B agrees": 7B SFT 0.0358 < RL N1375 0.0779 < DPO 0.3328 (DPO is the highest of the 12 7B changes).
- **OK** L15 "median overlap … 0.016": 0.01563 (`lora.csv` N2300 main; recomputed from `overlap_R32.csv.gz`).
- **OK** L15 "(random 0.003, lora_ctrl 0.007)": r0–r3 0.00297–0.00303; ctrl 0.00702.
- **OK** L15–16 "cosine with RL's change: 0.0052, and 0.0086 against the top 16": cos_full 0.0052497 and cos_k16 0.0086477 (`lora.csv`; recomputed).
- **OK** L18 "exact SVD, as a LoRA", plus the F448 and C16 definitions: `adapters_verify.json` has rel_err_fp32 = 0 on every check; `f448_check.json` has from_rl 448, from_dpo 259, pass.
- **OK** L19–20 "R (48 reach prompts …; fresh dpo 0 / 768) and A (218 prompts, strict pass@1)": `rows/dpo.csv` has 0 strict in 768 reach draws; `pids_reach.txt` lists 48 prompts and `pids_armA.txt` 218.
- **OK** L24, the rest of row R (T1 0.00, T4 0.01, T16 0.16, T64 0.61, F448 0.94, C16 0.50): 0.0000, 0.0109, 0.1582, 0.6127, 0.9362, 0.5022 (`results.csv`; recomputed from `hand_cells.csv`).
- **OK** L25, row A (−0.01, 0.05, 0.35, 0.73, 0.95, 1.07, 0.62): −0.0054, 0.0475, 0.3484, 0.7330, 0.9532, 1.0668, 0.6193 (`results.csv`; recomputed from `rows/*.csv`).
- **OK** L27 "95 % half-widths ≤ 0.13": the largest (hi − lo)/2 is 0.129 (C16 on R, [0.376, 0.634]); the largest one-sided distance is 0.131, on the upper side of the same interval.
- **OK** L29 "none holds (all firm)": in `summary.json` all three readings are false on both R and A, and every condition is firm.
- **OK** L30, low-rank reading fails: G(T16) 0.16 / 0.35 < 0.5 and G(C16) 0.50 / 0.62 > 0.2, with the intervals clear of both thresholds.
- **OK** L31 "T256 recovers nearly everything": 0.89 [0.80, 1.01] on R, 0.95 [0.90, 1.01] on A.
- **OK** L32 "F448 recovers everything": 0.94 [0.86, 1.02] on R (the interval contains 1), 1.07 [1.01, 1.13] on A.
- **OK** L33 "k₅₀ = 64": `summary.json` k50 is 64 on R and on A.
- **OK** L33 "below the median spike count (227)": 227. The pre-registration also sets k₅₀ beside the median signal rank (2,305), which is not quoted here.
- **OK** L36, E3 hit: Spearman ρ 0.964 > 0 (`expectations_part1.json`).
- **OK** L36, E6 hit: 7B N1375 S16 0.0779 < 32B N2300 S16 0.2182.
- **OK** L37 "P2 (T16 0.16)", miss: G_R(T16) 0.1582 is outside 0.3–0.7. On A, 0.348 would fall inside; that value is in the table but not in this line.
- **OK** L37 "P3 (overlap 0.016)", miss: 0.0156 < 0.052.
- **OK** L38 "E4's 'high-rank' call", miss: reading 2 does not hold (G_R(T256) 0.89 ≥ 0.5).
- **OK** L38 "E5 (main only 2.2× ctrl)": 0.01563 / 0.00702 = 2.23 < 3. The other two clauses hold (5.2× random, and < 0.052).
- **OK** L40 "1,400 items, 1,802 reads": `handcheck.csv` has 1,400 rows and Σ n_reads = 1,802. These are reader items only; 35 screened and 39 inherited labels come on top, 1,474 labelled in all.
- **OK** L40 "90 % of double reads agree": the first two reads agree on 332 of 367 items (90.5 %). Trap: the `reads` column is sorted lexically (r10 before r8 / r9), so a naive first-two parse gives 336. In chronological order it is 332, and every 3-read item is one where the first two reads split.
- **OK** L40 "gamed share 0.11–0.32 (arms with ≥ 65 successes)": T16 7/65 = 0.108, C16 0.148, T64 0.151, T256 0.232, F448 0.308, B_s2300 117/368 = 0.318 (`hand_arm_summary.csv`; re-aggregated from `hand_cells.csv`).
- **OK** L42 "1,472 draws per arm": `compute.csv` (T256 = 1,232 + 240 stage-0 draws); `rows/*.csv` has 1,472 per arm.
- **OK** L42 "T16–C16 used ≤ 1.43× dpo's tokens": the maximum is C16, 9,577,410 / 6,720,092 = 1.425.

## olmo_lowrank/plain_summary.md

### WRONG
- (none)

### FLAG
- **FLAG** L17 "(31–185×, measured in olmo-weights)". 31× is the 32B ratio and 185× the 7B one (run_olmo_weights.md L23; numbers.md olmo-weights E2: 0.113 / 0.00364 = 31 and 0.15 / 0.000806 ≈ 186). But the sentence's other numbers (3 %, 35 %) are 32B, and the 7B comes separately in the next sentence ("The 7B model shows the same order"). For 32B the figure is 31×. This run's own matrices agree: ‖ΔW_SFT‖ / ‖ΔW_N2300‖ = 30.6× over the 448 32B matrices, and 175× over the 224 7B ones.
- **FLAG** L23 "applied exactly through an adapter". The adapter is exact in fp32 (`adapters_verify.json` rel_err_fp32 = 0), but vLLM served the factors in bf16, which gives 0.23–0.24 % relative error in B A (rel_err_bf16_factors; log 20:48). The run doc's "exact SVD, as a LoRA" is the accurate wording.
- **FLAG** L33 "About 64 pieces per matrix carry half the gain". k₅₀ = 64 is the smallest k on the grid {1, 4, 16, 64, 256} with G ≥ 0.5. The top 64 carry 0.61 (R) / 0.73 (A) and the top 16 carry 0.16 / 0.35, so half the gain is reached somewhere between 16 and 64 pieces (log-linear interpolation gives ≈ 45 on R and ≈ 28 on A; not measured). Say "between 16 and 64", or "64 carry 61–73 %".

### ROUNDING
- **ROUNDING** L13 "about 230 pieces above same-size noise": median spike count 227.
- **ROUNDING** L15 "5 % at step 500": S_16 at N500 is 0.0477 (4.8 %).
- **ROUNDING** L17–18 "3 % in the top 16": SFT S_16 0.0333 (7B: 0.0358).
- **ROUNDING** L19 "about five times more than chance": 0.01563 / 0.00299 (the mean of r0–r3) = 5.2×.
- **ROUNDING** L28 "a sixth of the gain on the hard prompts": G_R(T16) 0.158 (1/6 = 0.167).
- **ROUNDING** L28 "(a third on IFBench)": G_A(T16) 0.348.
- **ROUNDING** L29 "the top 64 two thirds": 0.613 on R, 0.733 on A.
- **ROUNDING** L31 "still recovers half": G_R(C16) 0.502; 0.619 on A.
- **ROUNDING** L34 "A third of RL's checker-passing answers … were gamed": 117 / 368 = 0.318 of the labelled answers; about 31 % of its 1,066 strict passes are estimated gamed (1 − 0.477 / 0.694).
- **ROUNDING** L34 "the truncated models game less (11–23 %)": T16 0.108, C16 0.148, T64 0.151, T256 0.232, against s2300's 0.318. T4 (0.20) falls inside the range; T1 does not (both of its 2 labelled answers were gamed); F448 (0.308) is not a truncated model.

### OK
- **OK** L3–4 "RL turned … DPO model into a better instruction follower (Olmo 3.1 32B Think, step 2,300)": A strict 0.289 → 0.691, R 0.000 → 0.477 (`results.csv`).
- **OK** L4 "by changing each of its 448 big weight matrices a little": true, though RL also changed all 259 other tensors (the embeddings, every norm and lm_head; `f448_check.json` `dpo_rl_differ_outside`).
- **OK** L7–10, the method (rank-1 pieces; random noise of the same size; bf16 rounding noise): matches the pre-registration's Gaussian baseline and floors A and B.
- **OK** L12 "neither low-rank nor noise": S16 is 29× the Gaussian's, and S256 is 0.43, so 57 % lies beyond the top 256.
- **OK** L12 "top 16 … hold 22 % of it (noise: 0.75 %)": 0.2182; 0.00745 / 0.00750.
- **OK** L13–14 "more than half … spread over thousands of directions": 1 − S256 = 0.572. 98 % of the change's energy is in matrices whose short side is 5,120 (4,864 directions past 256); median signal rank 2,305.
- **OK** L15 "22 % at 2,300": 0.218. The peak is 0.265 at step 1,600, so the build-up is not monotone.
- **OK** L15–16 "one near-rank-1 jump between steps 1,100 and 1,150": same as the run doc's L11 (a rank-1-dominated spike on a floor; "partly" is inferred from timing).
- **OK** L17 "Supervised fine-tuning moved the weights far more": over the 448 matrices, 32B SFT's ‖ΔW‖² is 330,490 against RL's 352.
- **OK** L18 "DPO's change is the most concentrated (35 %)": 0.350.
- **OK** L18 "The 7B model shows the same order": 0.036 < 0.078 < 0.333.
- **OK** L19 "An adapter trained earlier on 16 RL answers": lora_main was trained on 16 genuine s2300 trajectories (numbers.md, olmo-ifladder LoRA table).
- **OK** L19–20 "but only slightly": the median overlap is 0.016 on a 0–1 scale.
- **OK** L22–23 "k = 1 to 256": T1, T4, T16, T64, T256.
- **OK** L23–24 "48 hard ones that DPO never solved": fresh dpo is 0 / 768 strict, and the set was selected for 0 genuine in ≥ 256 stored dpo draws (pre-registration). Wording: "RL's instruction-following prompts" are IFBench / IFEval evaluation prompts (olmo-ifcurve's reach set and arm A), not RL's training prompts.
- **OK** L24 "218 IFBench ones": `pids_armA.txt` lists 218 prompts, all `ifbench_*` (42 of them also in the reach set).
- **OK** L24 "G … (0 = DPO, 1 = RL)": the pre-registered definition.
- **OK** L24–26 "blinded readers checked the first eight checker-passed answers per prompt and model": labelled = min(strict, 8) in all 432 cells, all within the first 8 strict successes in draw order. 1,400 of the 1,474 labels came from readers (35 from the screen, 39 inherited).
- **OK** L28 "The top 1 or 4 pieces do nothing": T1 0.00 / −0.01. T4 is 0.011 [0.003, 0.021] on R (the interval excludes 0) and 0.048 [−0.000, 0.093] on A: a 1–5 % effect, fair to call "nothing" in plain words.
- **OK** L29 "the top 256, only 43 % of the change, nearly all": S256 0.428; G 0.89 / 0.95.
- **OK** L30 "Copying the 448 matrices … recovers everything": 0.94 [0.86, 1.02] on R, 1.07 [1.01, 1.13] on A.
- **OK** L30 "embeddings, norms and the output layer do not matter": an inference from F448 (those tensors did change). On R, the interval does not rule out up to ≈ 0.14 of the gain coming from them.
- **OK** L31 "neither part works alone": T16 0.16 / 0.35, C16 0.50 / 0.62.
- **OK** L32–33 "none of the three pre-registered explanations fits": `summary.json` final has all three as "does not hold".
- **OK** L36–37, Limits: consistent with the design (one RL run, IFBench / IFEval only, one k for every matrix).
