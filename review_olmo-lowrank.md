# Review: olmo-lowrank (reviewer, 2026-11-27)

Reviewer session, separate from the executor. Brief: nd-rl `docs/proposals/followups/BRIEF_olmo-lowrank.md`.
Pre-registration: `preregistration/olmo-lowrank.md`. My kit: `review/olmo-lowrank-recount/` (my own code; no executor
module is imported).

**Models.** Every number below is measured on released AI2 checkpoints: pretrained bf16 weights, none trained here,
Think chat format.
- 32B: `base` = Olmo-3-1125-32B `main` (c2b61dae; same shard hashes as stage3-step11921+11000+10000-nooptim fbc60636);
  `sft` = Olmo-3-32B-Think-SFT `main` (a6d7f3cf; = 5e-5-step8000 83ac724f); `dpo` = Olmo-3-32B-Think-DPO `main`
  (97604023); `sNNNN` = Olmo-3.1-32B-Think `step_NNNN`; `s2300` = `main` (97ade57a; = step_2300 29884259).
- 7B: Olmo-3-1025-7B (`main` a81bae42 = stage3-step11921 4b32e100), Olmo-3-7B-Think-SFT / -DPO, Olmo-3-7B-Think
  `step_NNNN`, Olmo-3-7B-RL-Zero-IF `main`.
- Part-2 arms are served by vLLM 0.11.0 in bf16 on one H200: `dpo` 32B plus rank-k LoRAs (T_k, C16), or `dpo` with
  the 448 matrices replaced by s2300's (F448).

**Phase-1 exposure.** I saw results before recounting, without trying to. At session start (05:38 UTC) the harness's
git context, and then my own `git log`, showed the executor's commit subjects. They include
"DONE — spectra (RL's change is spikes on a floor), truncation arms (k50 = 64; no pre-registered reading holds)",
"dpo arm sampled (reach strict 0/768)" and the hand-gate round sizes. My `git log --stat` also listed file names, not
contents. I read no write-up, `README.md`, `results.csv`, `summary.json`, `hand_cells.csv`, `hand_arm_summary.csv`,
`tables/` file or registry row before this section was committed. I read the executor's per-item hand labels
(`olmo_lowrank/handcheck.csv`, `hand/screen.csv`) only after my own labels were final (§6), to compute agreement. My
readers saw only item files.

## §Recount (phase 1)

### 1. Provenance

- **Shard hashes, `main` against the pinned branch** (`rvr_plan.py`, Hub LFS trees read today). 32B base, 32B SFT,
  32B s2300 and 7B base: 4 / 4 have identical file names and sha256. The pre-registration's commit hashes equal the
  Hub's current `main`.
- **Seeded raw-weight sample** (`random.Random("olmo-lowrank review 2026-11-27 32B" / "… 7B")`):
  - 32B layers 6, 8, 42, 43 and 7B layers 19, 31, all 7 matrix types: 28 + 14 matrices.
  - Tensors were located from each file's own safetensors header.
  - 52 shard files (252.8 GB) were fetched at the manifest's commits; 52 / 52 passed sha256 (`pod_out/files.csv`).
- **Prompts.** All 224 prompts (48 reach, 218 arm A, 42 in both) equal the upstream IFBench / IFEval records, text and
  instruction lists.
- **Prompt token ids** (`rvr_provenance.py`, my own rendering of the olmo_thinker template plus the DPO
  `tokenizer.json`):
  - 224 / 224 prompts per arm and 48 / 48 for B_s2300 match every meta's `prompt_sha256_by_pid` and length.
  - Every row of the 8 arms and of B_s2300 carries my prompt length.
  - The olmo-ifomega F_* rows store no ids. Their meta has the same template sha256.
  - Boundary by hand (8 rows): the prompt ends `<|im_start|>assistant\n<think>`, and the responses open inside the
    thinking ("Okay, so the user …").
- **Decoding.** All 8 arms ran at T 1, top-p 1, a 32,768-token budget, vLLM 0.11.0, TP 1, one H200, engine seed 62026,
  the same template sha (eba6e269…) and the DPO tokenizer. The stored endpoints use the same settings with their own
  seeds: B_s2300 48300, F_s2300_ifb 3004, F_dpo_ifb 3001. They also use chunk 4 instead of 8, a prefix-cache batching
  difference. The run's copies of the three endpoint files are byte-identical to my earlier bucket copies.
- **Adapters.**
  - Each arm's served `lora_sha256` equals the bucket file's sha256: T1, T4, T16, T64, T256 and C16 (6 / 6).
  - T1 and T4 were served at `max_lora_rank` 8 (zero padding), T256 at 256.
  - `lora_main` / `lora_ctrl` sha256 = 9921a760… / 4cf06004…, as in `artifacts/MANIFEST.jsonl`.
- **F448** (`meta/f448_check.json`, the executor's tensor-by-tensor check; the served weights are gone with the pod).
  448 tensors come from s2300 and 259 from DPO: embeddings, all norms and `lm_head`. All 259 of those differ between
  DPO and s2300.
- **Zero-delta check.**
  - The stored pair (`stage0/zero_plain.json`, `zero_lora.json`) is not bitwise equal. Over 1,451 tokens, 62 match and
    the largest log-prob difference is 0.25 nats. Run-to-run noise between two plain runs is 0.23 nats.
  - The second pair, reported bitwise identical in `stage0/zero2_diff.txt`, was run with `VLLM_ATTENTION_BACKEND=FLASH_ATTN`.
    Its raw files (`zero2_*.json`) were not pulled, so the "identical" result cannot be re-derived from stored files.
  - Both pairs support "the LoRA path adds nothing beyond run-to-run noise".
- **Draws.** No duplicate draws: no repeated response id sequence within a prompt and no repeated (pid, chunk, i), in
  any of the 11 jobs. T256 is its stage-0 throughput run (240 draws on 24 prompts) plus the continuation (1,232), as
  pre-registered.

### 2. Re-grade

My driver around the upstream IFBench (cd189a9c) and IFEval checkers graded 20,512 rows: 8 arms × 1,472, B_s2300
1,536, F_s2300_ifb 2,400 and F_dpo_ifb 4,800. It disagrees with the run's grade files on 0 strict and 0 loose
verdicts, and every row's stored ids decode to its stored text.

| job | reach draws | reach strict | other draws | other strict | rows | strict / loose disagreements |
|---|---|---|---|---|---|---|
| dpo | 768 | 0 | 704 | 251 | 1472 | 0 / 0 |
| T1 | 768 | 2 | 704 | 250 | 1472 | 0 / 0 |
| T4 | 768 | 5 | 704 | 268 | 1472 | 0 / 0 |
| T16 | 768 | 65 | 704 | 359 | 1472 | 0 / 0 |
| T64 | 768 | 264 | 704 | 452 | 1472 | 0 / 0 |
| T256 | 768 | 422 | 704 | 493 | 1472 | 0 / 0 |
| F448 | 768 | 511 | 704 | 517 | 1472 | 0 / 0 |
| C16 | 768 | 216 | 704 | 427 | 1472 | 0 / 0 |
| B_s2300 | 1536 | 1066 | 0 | 0 | 1536 | 0 / 0 |
| F_s2300_ifb | 336 | 213 | 1408 | 979 | 2400 | 0 / 0 |
| F_dpo_ifb | 672 | 0 | 2816 | 1011 | 4800 | 0 / 0 |

**Draw counts.** Each arm has 48 reach prompts × 16 and 176 other prompts × 4. F_dpo_ifb has 16 per prompt and
F_s2300_ifb 8 per prompt on the 176.

**Budget.** Cut share (finish = length) per arm: dpo 0.20 %, T1 0 %, T4 0.68 %, T16 0.95 %, T64 0.14 %, T256 0.14 %,
F448 0 %, C16 0.07 %.

**Bounds on zeros.** `dpo`: 0 strict in 768 reach draws, so its reach rate is below 0.39 % at 95 % (≤ 0 of 16 on
every prompt). T1: 2 strict, both gamed, so 0 genuine in 768 and the same bound.

### 3. Spectra: my raw-weight recompute against the stored values (same 42 matrices, every change)

My recompute is `pod/rvr_pod.py` on an A100. It is independent of the run's engine:
- singular values from a float64 QR of the tall orientation, then the SVD of the triangular factor;
- my own bf16 round-to-nearest-even, checked against torch's cast on 13 M values (4 M random, 1 M exact ties, 8 M
  rescaled; 0 mismatches), with truncation as a failing control (2.0 M of 4 M mismatch);
- my own floor bisection, my own seeds, my own Gaussian and random rank-16 baselines.

Comparison (`rvr_spectra_cmp.py`) over 532 (change, matrix) pairs:

| quantity | run's value | max relative deviation from mine (median) |
|---|---|---|
| ‖ΔW‖²_F | exact | 2.5e-13 (2.2e-16) |
| all singular values (Gram route, `full_*.npz`) | full | max abs. error 5.6e-8 σ₁ |
| top-k shares from the full spectra, k = 1 … 256 | | ≤ 1.1e-7 |
| σ₁, randomized (p 64, q 16) | top 256 | 6.5e-6 (1.1e-7) |
| share₁₆, randomized | | 3.2e-5 (3.3e-7) |
| share₂₅₆, randomized | | 3.4e-3 (1.2e-4) |
| floor A σ₁ (independent random draws; same target norms to 2.6e-15) | 42 matrices | 1.0 % (0.03 %) |
| floor B σ₁ (independent draws) | 308 pairs | 0.92 % (0.31 %) |
| signal rank (theirs: their spectrum vs their floor A; mine: mine vs mine) | | equal in 257 / 532; max diff 24 (905 vs 881); median relative diff 0.04 % |
| spike count (floor B) | | equal in 76 / 308; max diff 14 |
| LoRA overlaps, main and ctrl, left and right (N100, N1100, N2300) | 84 rows each | ≤ 4.3e-5 |
| ⟨ΔW_lora, D⟩ / ⟨ΔW_lora, D₁₆⟩ | | ≤ 4.8e-5 / ≤ 8.2e-3 |
| ⟨ΔW_lora, D₂₅₆⟩ | | up to 28 % (main) and 393 % (ctrl, inner products near 0); median 0.07 % / 1.5 % |
| Gaussian top-k shares, 5 shapes | | ≤ 0.4 % |

- **Signal ranks and spike counts** move by a few units where the spectrum is dense near the threshold: a 1 % change
  in the floor's σ₁ shifts them.
- **The k = 256 inner products** use the randomized top-256 vectors, which are not exact at the cut. That affects only
  the "share of ⟨ΔW_lora, ΔW⟩ in D₂₅₆" diagnostic.
- **Accuracy target met.** The pre-registered target (randomized shares within 2 % for k ≤ 64 and 5 % at 256, σ₁
  within 0.1 %) holds on my sample.

### 4. Part 1 over every matrix (my code on the stored per-matrix spectra, validated in §3)

The table is from `rvr_part1.py`.
- S_k = energy-weighted whole-model top-k share.
- "Gaussian" uses my own simulation, 3 seeds per shape.
- Signal rank counts σ_i(D) above σ₁ of the run's floor A, uncensored.
- Spike count counts σ_i(D) above σ₁ of the run's floor B (same norm as the change).
- "Energy in spikes" is the energy-weighted share of ‖D‖² above floor B.

| model | change | S₁ | S₁₆ | S₆₄ | S₂₅₆ | S₁₆ ÷ Gaussian | S₁₆ ÷ floor A | median signal rank [IQR] | share ≥ 256 | median spike count [IQR] | energy in spikes | median stable rank |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 32B | N50 | 0.0082 | 0.0329 | 0.0718 | 0.1690 | 4.4 | 4.4 | 1 [1, 3] | 0.00 | 124 [51, 191] | 0.13 | 77.9 |
| 32B | N100 | 0.0098 | 0.0406 | 0.0874 | 0.1946 | 5.4 | 5.4 | 12 [3, 25] | 0.00 | 166 [75, 262] | 0.18 | 64.1 |
| 32B | N500 | 0.0116 | 0.0477 | 0.1052 | 0.2296 | 6.4 | 6.4 | 392 [216, 788] | 0.70 | 222 [102, 359] | 0.26 | 51.8 |
| 32B | N750 | 0.0139 | 0.0572 | 0.1242 | 0.2628 | 7.7 | 7.6 | 1005 [515, 2064] | 0.93 | 241 [106, 416] | 0.32 | 45.2 |
| 32B | N1100 | 0.0185 | 0.0718 | 0.1458 | 0.2949 | 9.7 | 9.6 | 1552 [692, 3589] | 0.99 | 251 [109, 456] | 0.37 | 37.4 |
| 32B | N1600 | 0.1126 | 0.2650 | 0.3404 | 0.4686 | 35.4 | 35.3 | 1948 [824, 4770] | 1.00 | 212 [93, 332] | 0.49 | 9.3 |
| 32B | N2300 | 0.0895 | 0.2182 | 0.2940 | 0.4282 | 29.3 | 29.1 | 2305 [932, 5101] | 1.00 | 227 [101, 360] | 0.46 | 11.8 |
| 32B | I_early (50→100) | 0.0071 | 0.0285 | 0.0638 | 0.1569 | 3.8 | 3.8 | 2 [1, 5] | 0.00 | 114 [61, 171] | 0.11 | 95.8 |
| 32B | I_mid (1100→1150) | 0.1520 | 0.2214 | 0.2572 | 0.3343 | 29.5 | 29.5 | 580 [264, 1426] | 0.77 | 94 [42, 125] | 0.28 | 7.0 |
| 32B | I_late (2250→2300) | 0.0070 | 0.0255 | 0.0578 | 0.1476 | 3.5 | 3.4 | 38 [14, 78] | 0.00 | 144 [82, 185] | 0.11 | 104.0 |
| 32B | K (1100→2100) | 0.1291 | 0.2918 | 0.3524 | 0.4536 | 39.2 | 38.9 | 2102 [842, 4842] | 1.00 | 158 [65, 234] | 0.44 | 8.3 |
| 32B | SFT | 0.0047 | 0.0333 | 0.0917 | 0.2380 | 4.6 | 4.4 | 4925 [1024, 5120] | 1.00 | 344 [158, 519] | 0.36 | 149.1 |
| 32B | DPO | 0.1694 | 0.3501 | 0.4003 | 0.4934 | 37.4 | 46.7 | 13 [8, 19] | 0.00 | 74 [37, 192] | 0.43 | 6.4 |
| 7B | N25 | 0.0163 | 0.0401 | 0.0786 | 0.2047 | 3.4 | 3.3 | 0 [0, 1] | 0.00 | 11 [7, 20] | 0.04 | 120.9 |
| 7B | N100 | 0.0158 | 0.0467 | 0.0904 | 0.2181 | 4.0 | 3.8 | 7 [5, 12] | 0.00 | 44 [33, 58] | 0.08 | 89.0 |
| 7B | N500 | 0.0199 | 0.0661 | 0.1281 | 0.2689 | 5.7 | 5.4 | 1559 [1431, 2602] | 1.00 | 127 [113, 153] | 0.19 | 57.9 |
| 7B | N1000 | 0.0214 | 0.0757 | 0.1472 | 0.2980 | 6.5 | 6.2 | 2248 [2036, 3596] | 1.00 | 156 [134, 184] | 0.24 | 51.3 |
| 7B | N1375 | 0.0210 | 0.0779 | 0.1539 | 0.3103 | 6.7 | 6.3 | 2470 [2237, 3872] | 1.00 | 171 [145, 201] | 0.26 | 51.6 |
| 7B | I_early (25→50) | 0.0073 | 0.0254 | 0.0634 | 0.1907 | 2.2 | 2.1 | 0 [0, 1] | 0.00 | 9 [6, 18] | 0.03 | 205.2 |
| 7B | I_mid (500→525) | 0.0031 | 0.0169 | 0.0530 | 0.1783 | 1.5 | 1.4 | 43 [29, 76] | 0.01 | 18 [11, 24] | 0.02 | 390.5 |
| 7B | I_late (1350→1375) | 0.0022 | 0.0148 | 0.0503 | 0.1750 | 1.3 | 1.2 | 530 [454, 929] | 1.00 | 17 [12, 21] | 0.02 | 562.7 |
| 7B | K (500→1375) | 0.0133 | 0.0537 | 0.1147 | 0.2570 | 4.6 | 4.4 | 2416 [2178, 3787] | 1.00 | 141 [119, 164] | 0.19 | 81.8 |
| 7B | SFT | 0.0059 | 0.0358 | 0.1009 | 0.2804 | 3.2 | 2.9 | 4081 [3683, 4096] | 1.00 | 266 [240, 316] | 0.31 | 200.3 |
| 7B | DPO | 0.1451 | 0.3328 | 0.3932 | 0.5012 | 27.9 | 27.1 | 1034 [701, 1392] | 0.96 | 62 [46, 79] | 0.39 | 7.4 |
| 7B | ZIF (base→RL-Zero-IF) | 0.0845 | 0.2334 | 0.3559 | 0.5152 | 20.2 | 19.0 | 2898 [2612, 4095] | 1.00 | 142 [118, 197] | 0.46 | 11.5 |

Observations, 32B:
- **One interval carries most of the top direction.** In I_mid (1,100 → 1,150) the top direction alone holds 15 % of
  the interval's energy (S₁ 0.152, median stable rank 7.0). From then on S₁ of the net change jumps: 0.0185 at 1,100,
  then 0.113 at 1,600 and 0.090 at 2,300. My raw-weight recompute reproduces this on all 28 sampled matrices.
- **Floor A is crossed early.** RL's net change passes floor A, which is sized to a single interval, in almost every
  direction from step 500 on, so signal rank is ≥ 256 in 100 % of matrices at 2,300.
- **Above the matched-norm floor.** About 220 directions per matrix stand above floor B, and they carry 46 % of
  N2300's energy.

LoRA overlap (32B, overlap = mean of left and right; random = mean of 4 seeded rank-16 bases; the inner products are
the run's, validated on my sample within 1e-4 for k ≤ 16):

| change | lora_main median overlap (left / right) | lora_ctrl | random | cos(ΔW_main, D) | cos(ΔW_main, D₁₆) | share of ⟨ΔW_main, D⟩ in D₁₆ |
|---|---|---|---|---|---|---|
| N50 | 0.0155 (0.0216 / 0.0081) | 0.0110 | 0.0030 | 0.0008 | 0.0036 | 0.84 |
| N100 | 0.0156 (0.0226 / 0.0080) | 0.0110 | 0.0030 | 0.0011 | 0.0044 | 0.82 |
| N500 | 0.0189 (0.0282 / 0.0084) | 0.0115 | 0.0030 | 0.0028 | 0.0105 | 0.82 |
| N750 | 0.0207 (0.0307 / 0.0085) | 0.0117 | 0.0030 | 0.0037 | 0.0128 | 0.83 |
| N1100 | 0.0213 (0.0313 / 0.0082) | 0.0118 | 0.0030 | 0.0045 | 0.0140 | 0.84 |
| N1600 | 0.0139 (0.0196 / 0.0068) | 0.0064 | 0.0030 | 0.0047 | 0.0068 | 0.74 |
| N2300 | 0.0156 (0.0237 / 0.0068) | 0.0070 | 0.0030 | 0.0052 | 0.0086 | 0.77 |

Expectations scored as pre-registered (32B unless stated):

| expectation | my value | scored |
|---|---|---|
| P1 (a) median spike count of N2300 ≥ 1 **and** (b) each 50-step interval's S₁₆ ≤ 1.5 × floor A's | (a) 227; (b) 3.79, 29.5 and 3.40 × floor A | **miss** ((a) hits, (b) misses) |
| P3 lora_main median overlap at 2,300 ≥ 0.052 | 0.0156 | **miss** |
| E1 S₁₆(N2300) ≤ 3 × Gaussian **and** median signal rank ≥ 256 (censored) | 29.3 × Gaussian; signal rank ≥ 256 in 100 % of matrices | **miss** (the first part misses) |
| E2 S₁₆(SFT) > S₁₆(N2300) | 0.033 vs 0.218 | **miss** |
| E3 S₁₆ of N_t rises with t (Spearman ρ > 0, 7 steps) | ρ = 0.96 | hit |
| E5 main ≥ 3 × ctrl **and** ≥ 3 × random **and** < 0.052 | main 0.0156 = 2.2 × ctrl (0.0070), 5.2 × random (0.0030) | **miss** (fails ≥ 3 × ctrl) |
| E6 S₁₆(7B N1375) < S₁₆(32B N2300) | 0.078 vs 0.218 | hit |

### 5. Do the adapters equal their truncations? (28 sampled 32B matrices, N2300)

I compared B·A from the bucket adapters with my float64 U_k Σ_k V_kᵀ:

| adapter | config (r, α) | ‖BA − D_k‖ / ‖D_k‖, max (median) | after a bf16 cast of B and A | ‖D − BA‖² vs ‖D‖² − Σ_{i≤k} σ_i², max relative gap |
|---|---|---|---|---|
| T1 | 1, 1 | 8.6e-4 (2.6e-4) | 2.5e-3 (2.4e-3) | 5.5e-8 |
| T4 | 4, 4 | 7.3e-4 (3.9e-4) | 2.5e-3 (2.4e-3) | 1.0e-7 |
| T16 | 16, 16 | 1.2e-3 (4.7e-4) | 2.6e-3 (2.4e-3) | 2.7e-7 |
| T64 | 64, 64 | 7.4e-3 (5.8e-4) | 7.8e-3 (2.4e-3) | 5.7e-7 |
| T256 | 256, 256 | 3.0e-3 (8.5e-4) | 3.8e-3 (2.5e-3) | 1.2e-6 |
| C16 | 16, 16 (B = −U₁₆Σ₁₆) | 1.2e-3 (4.7e-4) | 2.6e-3 (2.4e-3) | 2.7e-7 |
| Z8 | 8, 8 | max abs. of B·A = 0 | | |

- **The adapters are the truncations.** They come from an fp32 SVD and agree with the exact truncation to about
  1e-3, below the error of vLLM's bf16 cast of the factors (about 2.4e-3).
- **The one large error is a near-tie.** The T64 maximum (7.4e-3, layer 43 up_proj) sits where σ₆₄ / σ₆₅ − 1 =
  0.05 %, so any fp32 SVD rotates the 64th and 65th directions there.
- **The pre-registered 1e-6 check is a self-check.** It compares the factors with the executor's own fp32 SVD, not
  with an exact SVD, so it does not measure this error.

### 6. Hand gate, repeated blind with my own readers

**Design.**
- Scope (pre-registered): per cell (arm × reach prompt), the first min(strict, 8) strict successes in draw order;
  for s2300, the same in B_s2300's 32 draws. That is 1,474 draws, which collapse to 1,434 groups of identical answers
  per prompt.
- Readers got the pre-registered reader prompt (`olmo_lowrank/handcheck_prompt_if.md`, identical to olmo-ifcurve's
  apart from the run name). They saw only item files: prompt, constraints with my checker's verdicts, and the answer.
- My label policy (`hand/POLICY.md`) was written after the first reads and before any second read or adjudication.
  - Mechanical rule-1 screen: 35 groups. These are the same 35 draws as the executor's screen in this scope; readers
    called 18 of them genuine, so the screen is not redundant.
  - Second reads: all T1 / T4 / T16 groups, a seeded quarter of the rest, and every checker disagreement (405).
  - Third reads: every split (37).
  - Adjudication under rules 1–14 by sub-agents with the rule files: every group of the rule-10–14 prompts, the
    fixed-output groups, the checker disagreements and the majority-of-3 groups (214 groups). I accepted the 205
    high- or medium-confidence proposals and rejected the 9 low-confidence ones.

**Agreement.**
- First-to-second read: 368 / 405 = 0.909. Second readers confirmed 80 / 95 first-read gamed labels and 288 / 310
  genuine ones.
- Reads in total: 1,876.

| job | strict on reach | labelled | genuine | gamed | gamed share | prompts with ≥ 1 genuine |
|---|---|---|---|---|---|---|
| dpo | 0 | 0 | 0 | 0 | — | 0 |
| T1 | 2 | 2 | 0 | 2 | 1.00 | 0 |
| T4 | 5 | 5 | 4 | 1 | 0.20 | 4 |
| T16 | 65 | 65 | 57 | 8 | 0.12 | 24 |
| T64 | 264 | 218 | 179 | 39 | 0.18 | 40 |
| T256 | 422 | 298 | 212 | 86 | 0.29 | 44 |
| F448 | 511 | 335 | 214 | 121 | 0.36 | 44 |
| C16 | 216 | 183 | 156 | 27 | 0.15 | 32 |
| s2300 (B_s2300) | 1066 | 368 | 233 | 135 | 0.37 | 42 |

**Agreement with the executor's labels**, draw by draw over the same 1,474 draws (its final item labels, its screen,
and identity inheritance on (pid, answer), re-implemented in `rvr_agree.py`):
- 1,370 / 1,474 = 0.929. By arm: T16 64 / 65, T64 206 / 218, T256 277 / 298, F448 307 / 335, C16 169 / 183,
  B_s2300 340 / 368.
- The disagreements lean one way. In 82 draws I say gamed and the executor genuine; in 22 the reverse. The most
  affected prompts are ifbench_264 (10), ifbench_1 (9), ifbench_267 (8) and ifbench_209 (8).
- My labels on the 233 B_s2300 draws that carry olmo-ifcurve final labels agree with those labels on 200 (0.858).

### 7. G and the readings (my labels, my bootstrap: paired over prompts, 10,000 replicates, seed 20261127)

R: the 48 reach prompts' estimated genuine rate (`dpo` = fresh arm, s2300 = B_s2300). A: the 218 prompts' strict
pass@1, with `dpo` pooled with F_dpo_ifb on the 176 and s2300 = F_s2300_ifb on the 176 plus B_s2300 on the 42.

| arm | R rate | G on R [95 %] | R strict rate | G on R strict | A rate | G on A [95 %] | G on A, fresh dpo only |
|---|---|---|---|---|---|---|---|
| dpo | 0.0000 | — | 0.0000 | — | 0.2895 (pooled), 0.2878 (fresh) | — | — |
| T1 | 0.0000 | 0.000 [0, 0] | 0.0026 | 0.004 | 0.2873 | −0.005 [−0.045, 0.034] | −0.001 |
| T4 | 0.0052 | 0.012 [0.003, 0.023] | 0.0065 | 0.009 | 0.3085 | 0.047 [0.001, 0.093] | 0.051 |
| T16 | 0.0742 | 0.167 [0.109, 0.234] | 0.0846 | 0.122 | 0.4292 | 0.348 [0.277, 0.419] | 0.351 |
| T64 | 0.2835 | 0.638 [0.524, 0.758] | 0.3438 | 0.495 | 0.5834 | 0.733 [0.661, 0.806] | 0.734 |
| T256 | 0.4020 | 0.904 [0.799, 1.021] | 0.5495 | 0.792 | 0.6717 | 0.953 [0.898, 1.011] | 0.953 |
| F448 | 0.4145 | 0.933 [0.857, 1.026] | 0.6654 | 0.959 | 0.7173 | 1.067 [1.012, 1.128] | 1.067 |
| C16 | 0.2401 | 0.540 [0.411, 0.678] | 0.2812 | 0.405 | 0.5378 | 0.619 [0.543, 0.699] | 0.621 |
| s2300 | 0.4445 | 1 | 0.6940 | 1 | 0.6905 | 1 | |

**Readings** (scored on point estimates, separately on R and A):

| reading | R | A | final |
|---|---|---|---|
| 1. "Low-rank carries it" (G(T16) ≥ 0.5 and G(C16) ≤ 0.2) | no (0.167; 0.540), firm | no (0.348; 0.619), firm | does not hold |
| 2. "High-rank" (G(T256) < 0.5 and G(F448) ≥ 0.75) | no (T256 0.904, firm; F448 0.933 holds) | no (0.953; 1.067) | does not hold |
| 3. "Outside the 448 matrices" (G(F448) < 0.75) | no (0.933), firm | no (1.067), firm | does not hold |
| 4. Otherwise: k₅₀ | **64** (T16 firmly below 0.5, T64 lower bound 0.524) | **64** (T64 lower bound 0.661) | k₅₀ = 64 |

Set beside Part 1, k₅₀ = 64 compares with N2300's median spike count (floor B) of 227 [101, 360] and a median signal
rank (floor A) of 2,305, which is ≥ 256 (censored) in every matrix. T64 keeps S₆₄ = 29 % of RL's ‖ΔW‖²; T256 keeps
43 %.

Further observations:
- **The parts are not additive.** C16 holds 78 % of the energy and recovers G 0.54 on R; T16 holds 22 % and recovers
  0.17. Together, 0.71 is less than F448's 0.93.
- **F448 beats s2300 on A.** On the 218-prompt strict rate F448 is above s2300 (G 1.067, CI above 1), but not on R
  genuine (0.933).
- **A is strict only.** It is not hand-gated, and the strict and genuine G differ on reach: T256 0.79 vs 0.90.

Expectations from Part 2:
- **P2** (0.3 ≤ G(T16) ≤ 0.7, scored on R): 0.167, **miss**. On A it is 0.348, inside.
- **E4** (G(T16) < 0.3, G(T256) < 0.5, G(F448) ≥ 0.75 and G(C16) ≥ 0.5, all on R, i.e. reading 2): T16 hit, T256
  **miss** (0.904), F448 hit, C16 hit but tentative (0.540 [0.411, 0.678]). Reading 2 does not hold, so **E4 misses**.

**Sensitivity of G on R to the labels** (my walk throughout):

| label variant | T16 | T64 | T256 | F448 | C16 | k₅₀ |
|---|---|---|---|---|---|---|
| main (policy) | 0.167 | 0.638 | 0.904 | 0.933 | 0.540 | 64 |
| first read only | 0.174 | 0.645 | 0.918 | 0.932 | 0.555 | 64 |
| no mechanical screen | 0.164 | 0.631 | 0.898 | 0.938 | 0.536 | 64 |
| rule-6 strict (1 ALL-CAPS item gamed) | 0.168 | 0.641 | 0.908 | 0.937 | 0.542 | 64 |
| low-confidence proposals accepted | 0.166 | 0.634 | 0.899 | 0.931 | 0.537 | 64 |
| **the executor's labels** | 0.158 | 0.613 [0.501, 0.732] | 0.895 | 0.936 | 0.502 [0.375, 0.636] | 64 |

With the executor's labels the R rates are higher (s2300 0.477 vs my 0.445) but G hardly moves. The readings are the
same under every variant.

### 8. Compute and cost (from the job logs and `~/podhours.log`)

| arm | GPU | GPU-seconds (JOB_START → JOB_DONE, every attempt) | draws | generated tokens | × dpo | cut |
|---|---|---|---|---|---|---|
| dpo | H200 | 3,834 | 1,472 | 6,720,092 | 1.00 | 3 (0.20 %) |
| T1 | H200 | 4,513 | 1,472 | 6,856,209 | 1.02 | 0 |
| T4 | H200 | 4,590 | 1,472 | 6,920,863 | 1.03 | 10 (0.68 %) |
| T16 | H200 | 5,931 | 1,472 | 8,419,961 | **1.25** (flag) | 14 (0.95 %) |
| T64 | H200 | 6,714 | 1,472 | 9,160,345 | **1.36** (flag) | 2 (0.14 %) |
| T256 | H200 | 9,629 (stage 0 1,658 + 7,971) | 1,472 | 9,290,432 | **1.38** (flag) | 2 (0.14 %) |
| F448 | H200 | 5,439 | 1,472 | 9,390,637 | **1.40** (flag) | 0 |
| C16 | H200 | 6,706 | 1,472 | 9,577,410 | **1.43** (flag) | 1 (0.07 %) |

- **Matching.** All arms are matched on prompts and draws. Five arms used more than 1.25 × the dpo arm's generated
  tokens, which the pre-registration says to flag.
- **Part 1.** Three jobs on one H100 80GB HBM3: R32 2,438 s, S32 527 s, R7 962 s.
- **Pods.** 15.33 pod-hours, $55.98:
  - lr-a, H200, 6.48 h, $23.27 ($3.59/h);
  - lr-b, H200, 7.20 h, $25.85;
  - lr-e, H100, 1.16 h, $5.10 ($4.39/h);
  - lr-d and an early lr-e, 0.49 h, $1.76.
- **Totals.** This matches `podbudget` ($55.98 of $80). My reviewer pod (A100 80GB, 1.43 h, $3.13) brings the run to
  $59.11.

### 9. Policy checks

- **Same comparison conditions.** Same chat template, tokenizer, decoding and budget for every compared arm and
  endpoint (§1). Template boundary checked by hand.
- **The hand gate runs both ways.** Every arm and s2300 get the same reach cells, the same 8-per-cell scope and the
  same rules; no arm gets extra tries.
- **Bounds on zeros.** For "dpo never solves a reach prompt": 0 strict in 768 draws (16 per prompt), a rate below
  0.39 % at 95 %.
- **Not gated.** The A metric rests on strict passes only, by design.
- **Not re-checked.** I did not repeat a scan of the evaluation prompts against Olmo 3's RL data; this run reuses
  olmo-ifcurve's prompt sets.
- **Not a prover run.** No Lean or nd_verify judge is involved.

### Errata to §Recount

Found by an adversarial check of this review (a sub-agent re-derived every number from my kit) after §Recount was
committed. The text above is left as committed; these corrections apply.

1. **§4 "Floor A is crossed early" is wrong as written.** The median signal rank passes the 256 censoring point from
   step 500 (392; ≥ 256 in 70 % of matrices at 500, 93 % at 750, 99 % at 1,100, 100 % at 2,300). But N2300 is above
   floor A in nearly every direction only in the MLP matrices (median 5,120 / 5,041 / 5,116 of 5,120). Elsewhere it is
   not: q 2,230 / 5,120, o 1,926 / 5,120, k 711 / 1,024, v 825 / 1,024. At step 500 the type medians are 132–911.
2. **§1 "Models" mis-describes C16.** C16 is F448 plus a negative rank-16 LoRA (model dir `f448`, LoRA rank 16), not
   `dpo` plus a LoRA.
3. **§1 zero-delta.** The run-to-run reference (plain run 1 vs run 2, max 0.23) also uses the unstored second-pair file
   (`zero2_plain.json`), as does the batched-vs-single reference. Only the stored pair's numbers are derivable from
   stored files: max 0.25 nats, 62 / 1,451 tokens identical. The sentence on `VLLM_ATTENTION_BACKEND=FLASH_ATTN` does
   not distinguish the pairs: both used that backend.
4. **§1 "The olmo-ifomega F_* rows store no ids."** They store response ids (decoded in §2) but no prompt ids or
   `prompt_tokens`.
5. **§3 accuracy target.** On my sample I compared the randomized σ₁, share₁₆ and share₂₅₆ directly. k = 1, 4, 64 are
   covered only through the run's `accuracy.csv` (max 1.9e-4).
6. **§4 LoRA preamble.** "Validated within 1e-4 for k ≤ 16" should read: within 1.3e-4 (main) and 8.2e-3 (ctrl, whose
   inner products are near zero), as §3's table says.
7. **§4 "One interval carries most of the top direction" overstates.** I did not measure alignment between the
   interval's and the net change's top directions. In energy, I_mid's top directions (Σ_m σ₁²) are about a quarter of
   N1600's or N2300's (8.2 vs 31). Supported: I_mid is unusually concentrated in one direction per matrix (S₁ 0.152
   against 0.007), and S₁ of the net change jumps after it.
8. **§4 "About 220 directions"** should read 227 (median).
9. **§7 table: dpo's pooled A rate is 0.2894** (0.28945), not 0.2895.

## Phase 2: comparison with the executor's write-up

Read from 07:47 UTC, after §Recount was committed (74c8f64b): `run_olmo_lowrank.md`, `numbers.md` § olmo-lowrank,
`log.md` § olmo-lowrank, `olmo_lowrank/plain_summary.md`, `olmo_lowrank/README.md`, `STATUS.md` § olmo-lowrank, the
figure and the tables. "Mine" means my independent value from §Recount. "My walk, its labels" means my cell walk and
bootstrap run on the executor's hand labels (`rvr_execlabels.py`).

### Claims

| # | claim (where) | my value | verdict |
|---|---|---|---|
| 1 | Models: released AI2 checkpoints, bf16, none trained; Olmo 3 32B base / SFT / DPO, 3.1 Think RL 50–2,300, s2300 = `main`; 7B for spectra (run, numbers) | §1: the commits, the `main` = pinned shard hashes and the 52 / 52 sampled shard sha256 all match | reproduces |
| 2 | Top 16 / 256 pieces hold 22 % / 43 % of ‖ΔW‖² of RL's net change; noise baselines 0.75 % / 11 % (run, numbers, STATUS) | 0.218 / 0.428; Gaussian 0.74 % / 10.9 %, floor A 0.75 % / 11.0 % | reproduces |
| 3 | Median matrix has 227 directions above same-norm rounded noise (run) | 227 [101, 360]; independent floor-B draws move individual counts by ≤ 14 | reproduces |
| 4 | It grows over RL, 3.3 % → 22 % (run); 5 % at step 500 (plain) | 0.033 → 0.218, 0.048 at 500; Spearman 0.96. Not monotone at the end: N1600 0.265 > N2300 0.218 | reproduces |
| 5 | "Partly via a near-rank-1 jump at steps 1,100–1,150" (run, plain); "rank-1-dominated" (log) | I_mid S₁ = 0.152, against 0.007 in the early and late intervals. Per matrix, though, the top piece holds a median 14 % of the interval's change (max 61 %; 1.6 % of matrices above 50 %, carrying 1.2 % of its energy). It is largest in late-layer v / o projections (medians 0.46–0.53 in layers 56–63) | **reword**: a jump concentrated in one direction per matrix (~15 % of the interval's ‖ΔW‖², 20× the other intervals), not near-rank-1 |
| 6 | Mid interval is "3× the late interval's size" (log) | 3.04× in ‖ΔW‖², 1.74× in ‖ΔW‖ | holds in squared norm; say which |
| 7 | SFT diffuse (3.3 %), DPO most concentrated (35 %), 7B agrees (run, STATUS) | 0.033 / 0.350; 7B 0.036 / 0.333 (RL 0.078) | reproduces |
| 8 | SFT moved the weights 31× more (32B, olmo-weights) (plain) | 30.6× in ‖ΔW‖ over these 448 matrices | reproduces (labelled inherited number) |
| 9 | Randomized top-256 accuracy, every matrix: σ₁ 5.5e-5, shares (k ≤ 64) 1.9e-4, k = 256 3.8e-3 (numbers) | the run's `accuracy.csv` gives the same; on my sample against my exact SVD, ≤ 6.5e-6 / 3.2e-5 / 3.4e-3. The log's 22:16 line ("σ₁ ≤ 7e-6, shares ≤ 1.3e-5") understates the run's own maxima | reproduces; log line inconsistent (minor) |
| 10 | LoRA: lora_main median overlap 0.016 (random 0.003, ctrl 0.007); cosine 0.0052, with the top 16 0.0086; 77 % of ⟨ΔW_lora, ΔW⟩ in the top 16 (run, numbers, log) | 0.0156 / 0.0030 / 0.0070; 0.00525 / 0.00865; 0.77; per-matrix overlaps within 4.3e-5 of my recompute | reproduces |
| 11 | T_k built from the "exact SVD" (run, numbers); "B A = U_k Σ_k V_kᵀ exactly in fp32" (log); `adapters_svd/` holds the "exact spectra of RL's change" (numbers, README) | The factors come from an fp32 SVD, which is what the pre-registration specified ("exact SVD (fp32, full)"). Against my float64 truncation they agree to ~1e-3 (median 3–9e-4; max 7.4e-3 at a near-tied σ₆₄ / σ₆₅). The "exactly" check compares the factors with the same fp32 SVD. The stored `adapters_svd` spectra deviate from my float64 values by up to 4.2e-4 σ₁; the Gram-route `full_*.npz` deviate by 5.6e-8 σ₁. Served after vLLM's bf16 cast: ~2.4e-3 | reword: "fp32 SVD; ~0.1 % from the exact truncation, ~0.24 % after the bf16 cast" |
| 12 | G on R: T1 0.00, T4 0.01, T16 0.16, T64 0.61, T256 0.89, F448 0.94, C16 0.50 (run, numbers, STATUS) | my walk, its labels: 0.000 / 0.011 / 0.158 / 0.613 / 0.895 / 0.936 / 0.502, equal to `numbers.md` to 3 dp. Mine: 0.000 / 0.012 / 0.167 / 0.638 / 0.904 / 0.933 / 0.540 | reproduces; with independent labels it differs by ≤ 0.04, inside every interval |
| 13 | G on A: −0.01 / 0.05 / 0.35 / 0.73 / 0.95 / 1.07 / 0.62; fresh-dpo and R_strict variants (run, numbers) | −0.005 / 0.047 / 0.348 / 0.733 / 0.953 / 1.067 / 0.619; the variants equal mine to ≤ 0.001 | reproduces (`numbers.md`'s T4 0.048 vs 0.0475 is double rounding) |
| 14 | 95 % half-widths ≤ 0.13 (run) | largest: C16 on R, 0.13 (its labels) or 0.134 (mine) | reproduces |
| 15 | Readings: none holds, all firm; k₅₀ = 64 on R and A (run, numbers, STATUS) | same under my labels and under every label variant (§7); T16 firmly below 0.5, T64 firmly above on both metrics | reproduces |
| 16 | "Low-rank carries it fails: T16 recovers too little and **the floor alone (C16)** too much" (run) | C16 removes only the top 16 pieces. By the run's own Part 1, D − D₁₆ still holds ~210 of the median 227 above-floor directions per matrix, and 24 % of N2300's energy lies in above-floor directions beyond the top 16. C16 is "RL's change minus its top 16", not the floor. The wording is inherited: the brief asks "does the floor alone, C16, recover anything?" and the pre-registration calls C16 "the floor only". The plain summary words it correctly | **reword** (fault in the design's label, not the executor's arithmetic) |
| 17 | k₅₀ = 64, below the median spike count 227 (run) | yes, on the {1, 4, 16, 64, 256} grid; k₅₀ lies in (16, 64] | reproduces |
| 18 | Expectations: hits E3, E6; misses P1, P2, P3, E1, E2, E5; E4: T16 < 0.3 hit, T256 < 0.5 miss, F448 ≥ 0.75 hit, C16 ≥ 0.5 hit (tentative), "high-rank" call missed (run, numbers) | identical scoring (§4, §7). C16 is 0.502 (its labels) or 0.540 (mine), interval [0.38–0.41, 0.63–0.68] | reproduces. The C16 component sits inside the pre-registration's own ≈ 0.10 resolution, so "unresolved" is the better word than "hit (tentative)" |
| 19 | Gate: 1,400 items, 1,802 reads, 90 % double-read agreement; 367 read twice (332 agree), 35 thrice, 35 screened, 39 inherited, 119 confirmations (run, numbers) | recounted from `handcheck.csv`, `confirm.csv`, `screen.csv` and the label files: 1,400 / 1,802 / 367 / 332 / 35 / 119, and the same 35 screened draws as mine | reproduces |
| 20 | Gamed share 0.11–0.32 in arms with ≥ 65 successes (run); "A third of RL's checker-passing answers on the hard prompts were gamed; the truncated models game less (11–23 %)" (plain) | my blind readers: 0.12–0.37 (s2300 0.37; T16 / T64 / T256 0.12 / 0.18 / 0.29; F448 0.36; C16 0.15). Agreement with its labels 0.929; one-sided (82 gamed-by-me / genuine-by-it against 22 the other way; most on ifbench_264, 209, 267; ifbench_1 goes the other way) | the direction reproduces; the levels depend on the reader standard: report "0.11–0.32 (second team 0.12–0.37)" or similar |
| 21 | Cross-run calibration 206 / 231 (89 %) with olmo-ifcurve's B_s2300 labels, balanced 12 / 13 (numbers, log) | mine against olmo-ifcurve's: 200 / 233 (86 %), 22 gamed-by-me / genuine-there vs 11 | its number is its own; mine is consistent with a stricter second team |
| 22 | Rule 6 (one ALL-CAPS s2300 item): the strict reading moves G by < 0.01 (numbers) | ≤ 0.004 under my labels (its labels' rule-6 variant not recomputed) | consistent |
| 23 | Zero-delta: plain vs zero LoRA bitwise identical in the second pair; run-to-run max 0.23 (numbers, log) | The second pair's raw files (`zero2_*.json`) are not stored, only the diff summary. That summary's noise references (run 1 vs run 2, batched vs single) also use them. The stored first pair alone shows plain vs zero-LoRA differing by up to 0.25 nats (median 6e-5; 62 / 1,451 tokens identical). Independent support that the LoRA path changes nothing material: T1 (a rank-1 adapter) matches dpo on the 176 other prompts (250 vs 251 strict of 704) and on A (G −0.005) | "bitwise identical" and "run-to-run max 0.23" are not derivable from stored files. Upload `zero2_*.json` |
| 24 | Compute: 1,472 draws per arm; T16–C16 flagged at 1.25–1.43× dpo's tokens, ≤ 2.51× H200-seconds (run); GPU-seconds table (numbers) | tokens identical; GPU-seconds from job wall are 0.17–0.42 % above the meta `t_load + t_gen` sums (e.g. dpo 3,834 vs 3,820); T256 / dpo 2.51× either way. The flags appear only in the run doc; `numbers.md`'s table has no token ratios | reproduces |
| 25 | Spend $55.98 of $80; pods and billed rates (run, numbers, STATUS) | ledger: lr-a $23.27, lr-b $25.85, lr-e (H100) $5.10, faulty-GPU pods $1.76; total $55.98 / 15.33 h | reproduces. My reviewer pod adds $3.13 (A100, 1.43 h) |
| 26 | Cut share at 32,768 tokens per arm (numbers) | identical (dpo 3, T4 10, T16 14, …) | reproduces |
| 27 | "48 hard instruction-following prompts that DPO never solved" (plain) | dpo: 0 genuine in the ≥ 256 stored draws per prompt that selected the set, and 0 strict in 768 fresh draws here (16 per prompt, so < 0.39 % at 95 %) | **reword**: state the tries and the bound (policy) |
| 28 | "Copying the 448 matrices from the RL model recovers everything; the other weights do not matter" (plain) | G(F448) 0.93–0.94 [0.86, 1.03] on R and 1.07 [1.01, 1.13] on A: F448 exceeds s2300's strict rate | **reword**: "the other weights' RL changes are not needed for the gain" ("do not matter" is too strong when F448 differs from s2300 on A) |
| 29 | "More than half the change is spread over thousands of directions" (plain) | energy-weighted 54 % lies below the floor-B level, the run's aggregate convention; for the median matrix 48 % | holds (energy-weighted); optional: "about half" |
| 30 | Top 1 or 4 pieces "do nothing" (plain) | T1 0.00 / −0.005; T4 0.012 / 0.047, with the A interval [0.001, 0.093] by mine, [−0.000, 0.093] by its | "nearly nothing" is more exact; fine as a plain-language summary |
| 32 | "An adapter trained earlier on 16 RL answers points into RL's top directions five times more than chance, but only slightly" (plain) | 5.2× random holds. But the matched control adapter (16 dpo answers) already sits at 2.3× random, so the RL-specific excess is 2.2× (why E5 missed) | add the control |
| 33 | Part-2 table: R rate of T16 0.075 (numbers) | 0.0755 (`results.csv`); the hand table in the same file gives 0.076 | double rounding (nit) |
| 31 | Pre-registration before any pod; misses reported as misses | pre-registration committed 20:03:04 (02a6af37), first pod create attempt 20:09:59 (`~/pods.log`); every miss is listed as a miss | holds |

### Policy checks on the write-up

- **Model labels.** Every number in `run_olmo_lowrank.md`, `numbers.md` and the plain summary names its model. The one
  inherited number (31× SFT move, plain summary) names olmo-weights; I re-derive it as 30.6× over these 448 matrices.
  The cosine 0.0052 is this run's own measurement (0.00525); only the log notes that it reproduces olmo-weights.
- **Strict and genuine side by side, with the label sources** (`numbers.md` hand table: readers / screen / inherited).
  Yes. A rests on strict passes only by design; R_strict is reported beside R.
- **Token budget and cut share per model.** Reported.
- **The same confirmation rule both ways.** Yes: the same 8-per-cell scope in every arm and in s2300.
- **"Never".** The run doc states 0 / 768. The plain summary's "never solved" does not state tries (claim 27).
- **Overlap with RL training data.** The write-up does not report a scan of the evaluation prompts against Olmo 3's RL
  data (the prompt sets are olmo-ifcurve's). That is minor, since every arm uses the same prompts, but the policy asks
  for it.
- **Compute.** Rows exist in `hf://buckets/dan-pandori/nd-rl/registry/olmo-lowrank/`. `numbers.md` has a per-arm
  table; the 1.25× flags are in the run doc.
- **Pre-registration deviation not labelled.** The pre-registration says "Per-prompt consistency audits by sub-agents
  after each round". The executor ran them once, after the last arm was read (u1–u4; log 00:27, policy fixed before
  them). Neither the write-up nor the log calls this a deviation.
- **Reproducibility.** Everything recounted here comes from git or the bucket, with two exceptions: the zero-delta
  second pair (claim 23), and the cost and pod-time figures, which come from the host's ledgers (`~/podhours.log`,
  `~/pods.log`).
- **No hard-constraint violation.** The judge is the official checkers plus the hand gate. Results reproduce from
  stored files. The secret scan of 341 tracked files and 1,553 bucket objects (every object except the binary adapter
  tensors) found 0 hits (`out/secret_scan.txt`).

## Verdict

**What stands.**
- **Part 1.**
  - Every number reproduces: S_k, baselines, stable / signal / spike medians, the LoRA overlaps and cosines, and the
    expectation scoring. I recomputed 42 seeded matrices from the raw weights with my own float64 code, and my
    aggregates over all 672 matrices come from the stored spectra that this recompute validates.
  - RL's net change at 2,300 is far more concentrated than noise: S₁₆ 29× Gaussian, and a median 227 directions per
    matrix stand above same-norm rounded noise, carrying 46 % of the energy.
  - SFT's change is diffuse and DPO's the most concentrated.
  - lora_main overlaps RL's top-16 subspaces 5× more than chance, but only 2.2× more than lora_ctrl.
- **Part 2.**
  - G on A reproduces exactly. G on R reproduces exactly from the executor's labels.
  - My blind second team gives G within 0.04 of it on every arm.
  - Under every label variant, none of the three pre-registered readings holds (each failing condition firm), and
    k₅₀ = 64 on both metrics.
  - The truncations are what they claim to be (0.1 % from exact; served adapters sha-identical to the bucket), and F448
    was built as specified.
- **Expectations.** P1, P2, P3, E1, E2 and E5 missed; E4's high-rank call missed; E3 and E6 hit. All reported as such.

**Must be reworded.**
1. "Near-rank-1 jump" at 1,100–1,150 (run doc, plain summary; "rank-1-dominated" in the log). Say instead: a jump
   concentrated in one direction per matrix (~15 % of the interval's ‖ΔW‖², about 20× the other intervals), strongest
   in late-layer v / o projections.
2. "The floor alone (C16)" (run doc). C16 is RL's change minus its top 16 pieces. By the run's own spike counts it keeps
   ~210 above-floor directions per matrix and 24 % of the energy above floor B, so the "low-rank carries it" test
   cannot say whether the floor itself carries anything.
3. "Exact SVD" / "exactly in fp32" for the adapters, and "exact spectra" for `adapters_svd/`. The pre-registration
   specified an fp32 SVD, so the method is as planned; only the word "exact" overstates. Say: fp32 SVD, ≈ 0.1 % from
   the exact truncation, ≈ 0.24 % after vLLM's bf16 cast.
4. Zero-delta "bitwise identical" and its run-to-run reference rest on files that were not stored. Upload
   `zero2_*.json`, or cite what the stored pair shows: ≤ 0.25 nats, median 6e-5. The T1 arm is independent evidence
   that the LoRA path itself shifts nothing.
5. Plain summary:
   - "never solved": give the tries and the bound;
   - "the other weights do not matter": say "are not needed for the gain";
   - the LoRA's "five times more than chance": add that the control adapter is at 2.3×.
6. Gamed shares: say they depend on the reader standard (my blind team: 0.12–0.37 against 0.11–0.32). By the
   pre-registration's own ≈ 0.10 resolution, two near-threshold values are unresolved rather than hits or misses: E4's
   C16 component (0.50 / 0.54 against 0.5) and P2 on A (0.348 against 0.3).
7. Unlabelled deviation: the consistency audits ran once at the end, not after each round as pre-registered.

**Not supported.** Nothing that a conclusion rests on. The only claims not derivable from stored files are the
second-pair zero-delta identity and its noise references (item 4).

**Next measurement.**
- **Does the floor carry anything?** The direct test of reading (b) the spectra invite is spike-matched arms:
  - a variable-rank LoRA keeping each matrix's own above-floor directions (median 227);
  - its complement, F448 minus those directions, which is the floor proper.

  If the complement recovers little (G ≲ 0.2) while the spike arm recovers most, the gain sits in the spikes. If the
  complement still recovers a lot, the gain needs the floor too.
- **Locate k₅₀.** T32 would place it inside (16, 64].
- **Check F448 > s2300 on A.** A fresh s2300 arm at engine seed 62026 would show whether the firm excess (G 1.07)
  survives matched sampling.
