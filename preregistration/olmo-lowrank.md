# Pre-registration: olmo-lowrank — is RL's change to Olmo 3's weights low-rank, and does its low-rank part carry RL's IFBench gain?

Written 2026-11-26 20:03 UTC (shell clock), before any pod of this run, any spectrum and any draw. Executor, run `olmo-lowrank`
(brief: nd-rl `followups/BRIEF_olmo-lowrank.md`; proposal 49, nd-rl `docs/proposals/2026-11-26-olmo-lowrank.md`;
authorised by Dan 2026-11-26, **$80 / 60 pod-hours, dollars binding**). Branch `dan_olmo-lowrank` (from
`origin/dan_olmo-weights`). Code and tables: `olmo_lowrank/`; bulk files: `artifacts/olmo_lowrank/` → bucket
`hf://buckets/dan-pandori/nd-rl/olmo-lowrank/`. Pod scripts: `pod/olmo_lowrank/`.

## Question

Part 1: for the 448 attention and MLP matrices of Olmo 3 32B (and the 224 of Olmo 3 7B), how concentrated in a few
singular directions is each training change, against a matched random matrix and a bf16-rounding floor? How much of
RL's top-16 subspace lies inside `olmo-ifladder`'s `lora_main`? Part 2: does DPO plus only the top-k pieces of RL's
change (per matrix) recover RL's IFBench gain, and does the floor alone (C16) recover anything?

## Models (every number names one of these)

Released AI2 checkpoints, pretrained (none trained here), bf16, Think chat format. Commits from `olmo_weights/manifest/`
(`checkpoints.csv`, `refs.json`; read from the Hub API on 2026-11-25); the pod verifies every downloaded shard's sha256
against `checkpoints.csv` / the revision's LFS tree.

| name | repo @ revision | commit | note |
|---|---|---|---|
| 32B `base` | `allenai/Olmo-3-1125-32B@main` | c2b61dae | = `stage3-step11921+11000+10000-nooptim` (fbc60636) by shard hash; 32.2 B params |
| 32B `sft` | `allenai/Olmo-3-32B-Think-SFT@main` | a6d7f3cf | = `5e-5-step8000`, the soup of both LR runs (olmo-weights); the SFT end point |
| `dpo` | `allenai/Olmo-3-32B-Think-DPO@main` | 97604023 | RL start |
| `sNNNN` | `allenai/Olmo-3.1-32B-Think@step_NNNN` | `checkpoints.csv` | NNNN ∈ {0050, 0100, 0500, 0750, 1100, 1150, 1600, 2100, 2250, 2300}; `s2300` = `main` (97ade57a) by shard hash |
| 7B `base` | `allenai/Olmo-3-1025-7B@main` | a81bae42 | = `stage3-step11921`; 7.3 B params |
| 7B `sft` / `dpo` | `allenai/Olmo-3-7B-Think-SFT@main` / `-DPO@main` | 6ff85758 / 7b18bf92 | |
| 7B `rNNNN` | `allenai/Olmo-3-7B-Think@step_NNNN` | `checkpoints.csv` | NNNN ∈ {0025, 0050, 0100, 0500, 0525, 1000, 1350, 1375} |
| 7B `zif` | `allenai/Olmo-3-7B-RL-Zero-IF@main` | 3cae007c | RL from the 7B base |
| `lora_main`, `lora_ctrl` | `hf://buckets/dan-pandori/nd-rl/olmo-ifladder/artifacts/olmo_ifladder/lora/{main,ctrl}/` | sha256 9921a760… / 4cf06004… | r 16, α 32 on `dpo` (olmo-ifladder); sha256 checked against `artifacts/MANIFEST.jsonl` before use |

**Lineage (olmo-weights' review):** 32B RL steps 150 and 200 lie on an abandoned branch; the released line is DPO → 50
→ 100 → 250 → … → 2,300, with a fresh-optimizer resume at 1,850 → 1,900. No change below uses 150 or 200, and no single
interval spans 100 → 250 or 1,850 → 1,900.

## Part 1: spectra

**Changes** (ΔW = float32(W_b) − float32(W_a), exact for bf16 values):

| id | 32B | 7B |
|---|---|---|
| RL net `N<t>` | `dpo` → s_t, t = 50, 100, 500, 750, 1,100, 1,600, 2,300 | `dpo` → r_t, t = 25, 100, 500, 1,000, 1,375 |
| single intervals `I_early/mid/late` | 50 → 100, 1,100 → 1,150, 2,250 → 2,300 | 25 → 50, 500 → 525, 1,350 → 1,375 |
| chord `K` | 1,100 → 2,100 | 500 → 1,375 |
| `SFT` total | `base` → `sft` | `base` → `sft` |
| `DPO` total | `sft` → `dpo` | `sft` → `dpo` |
| `ZIF` | — | `base` → `zif` |

Matrices: q, k, v, o, gate, up, down × 64 layers (32B: 5120×5120, 1024×5120, 1024×5120, 5120×5120, 27648×5120,
27648×5120, 5120×27648) and × 32 layers for 7B (shapes read from the headers).

**Method.** fp32 on GPU with TF32 off; ‖ΔW‖²_F exact (float64 sum). Randomized SVD for the top 256 (Halko et al.
subspace iteration: seeded Gaussian test matrix, oversampling p, q power iterations with QR between, then the small
SVD). Default p = 256, q = 8; stage 0 sets the final (p, q) as the cheapest setting that meets the accuracy target below
on two real matrices, and it is then fixed. **Full SVD** (all singular values, float64, cuSOLVER SVD or the
eigenvalues of the float64 Gram matrix on the short side — stage 0 picks by time; the Gram route is accurate to
≈ 1e-7 σ₁, far below every floor) on the seeded subset: layers ≡ 0 mod 8 (32B: 8 layers; 7B: 4), all 7 types, for every
change and floor. **Accuracy target:** on the subset, randomized top-k shares within 2 % (relative) of the full-SVD
values for k ≤ 64 and within 5 % for k = 256, and σ₁ within 0.1 %; misses are reported and the subset's full values are
used for those matrices. For `N2300` (32B) the exact SVD of all 448 matrices is computed anyway (Part 2), and it
validates the randomized values on every matrix of that change.

**Measures per change × matrix:** top-k shares s_k = Σ_{i≤k} σ_i² / ‖ΔW‖² (k = 1, 4, 16, 64, 256); stable rank
‖ΔW‖² / σ₁²; **signal rank** = #{i ≤ 256 : σ_i > σ₁(floor A)} (reported "≥ 256" when censored; the subset gives
uncensored counts); **spike count** = #{i : σ_i > σ₁(floor B)}. Aggregates: median and IQR across matrices by module
type and by depth (blocks of 8 layers), and the energy-weighted whole-model share S_k = Σ_m Σ_{i≤k} σ²_{m,i} /
Σ_m ‖ΔW_m‖² (the share of RL's ‖ΔW‖² that T_k keeps). Growth with steps: S_16 and the median signal rank / spike count
against t for the `N<t>` series.

**Baselines (constructions fixed here):**
- **Gaussian:** i.i.d. N(0, 1) of the same shape, scaled to ‖ΔW‖_F (shares and stable rank are scale-free; 3 seeded
  draws per shape, mean reported; σ₁ scales with the norm).
- **Floor A, bf16 rounding at RL's single-interval size** (the proposal's construction): per matrix,
  R_A = float32(bf16_rne(float32(W_dpo) + s·Z)) − float32(W_dpo), Z i.i.d. N(0, 1) seeded per matrix, s found by
  bisection on log s (fixed Z) so that ‖R_A‖²_F equals the mean of the matrix's three single-interval ‖ΔW‖²_F
  (32B: 50-step; 7B: 25-step intervals). It is the floor that one bf16 save of an update of RL's per-interval size
  produces. σ₁(R_A) defines the signal rank.
- **Floor B, matched-norm rounded noise:** per change × matrix, the same construction on the change's start weights
  with s calibrated to the change's own ‖ΔW‖_F. For a change much larger than the bf16 step it reduces to the
  Gaussian. It is added because floor A cannot tell accumulated sampling noise from signal: an unstructured change 4–5×
  the size of one interval (RL's net change at 2,300) clears floor A in most directions. The spike count is the number
  of directions standing above an unstructured change of the same size.

**LoRA overlap (32B, every `N<t>`; headline t = 2,300).** Per matrix: U₁₆, V₁₆ = RL's top-16 left and right singular
vectors; Q_B, Q_A = orthonormal bases of `lora_main`'s col(B) and row(A) (ΔW_lora = (α/r) B A = 2 B A). Overlap_left =
‖U₁₆ᵀ Q_B‖²_F / 16, overlap_right = ‖V₁₆ᵀ Q_A‖²_F / 16 (0–1; random ≈ 16 / n), overlap = their mean. Same for
`lora_ctrl` and 4 seeded random rank-16 subspaces. Diagnostic for reading (b): the whole-model cosine of ΔW_lora with
the truncation ΔW_k (k = 1 … 256) against its cosine with the full ΔW (olmo-weights: 0.0053), and the share of
⟨ΔW_lora, ΔW⟩ carried by the top-k pieces.

## Part 2: truncation arms (32B)

D = W_s2300 − W_dpo per matrix (fp32); exact SVD (fp32, full) if stage 0 projects ≤ 1 H200-hour for the 448 matrices,
otherwise the randomized top 256 (accuracy reported).

| arm | served model |
|---|---|
| `dpo` | DPO, plain weights (fresh matched control) |
| `T1`, `T4`, `T16`, `T64`, `T256` | DPO + rank-k LoRA, B = U_k Σ_k, A = V_kᵀ, α = r (scaling 1), on all 448 matrices |
| `F448` | DPO with the 448 matrices replaced by s2300's tensors (exact; embeddings, all norms and `lm_head` stay DPO's) |
| `C16` | F448 + rank-16 LoRA B = −U₁₆ Σ₁₆, A = V₁₆ᵀ (= DPO + D − D₁₆: the floor only) |
| `s2300` | stored rows (below) |

- No truncated change is merged into bf16 weights. Adapters are written in fp32 PEFT format; before use, every
  adapter's B A is checked against U_k Σ_k V_kᵀ on 8 seeded matrices (fp32, relative Frobenius error ≤ 1e-6), and the
  error after vLLM's cast of the factors to bf16 is recorded. F448 is checked tensor by tensor (bitwise equal to s2300
  on the 448, to DPO elsewhere; same tensor set).
- vLLM's LoRA path: `max_lora_rank` = the arm's rank rounded up to vLLM's allowed values (e.g. 8 for T1 / T4 if 1 and
  4 are not allowed; zero-padding does not change B A).
  If vLLM's maximum rank is below 256, T256 runs at the highest supported rank and is labelled with it.
- A zero-delta check (stage 0): `dpo` plain vs `dpo` + an all-zero LoRA, prompt log-probs on 4 prompts; the
  difference is recorded (expected at bf16 noise or 0). The plain `dpo` arm is the matched control for the T_k arms
  on the strength of this check.

**Prompts and draws (every arm, identical):** the 48 reach prompts (`olmo_ifcurve/pids_reach.txt`: 42 IFBench + 6 IFEval)
× 16 draws, and the 176 other arm-A prompts (`olmo_ifcurve/pids_armA.txt` minus the reach prompts) × 4 = 1,472 draws per
arm. The 218-prompt aggregate uses all of an arm's draws per prompt (16 on the 42 IFBench reach prompts, 4 elsewhere).
**Decoding = olmo-ifcurve's:** `olmo_ifladder/sample.py` unchanged (olmo_thinker template, T 1, top-p 1, 32,768
response tokens, no stop strings, vLLM 0.11.0, bf16, one H200, TP 1, prefix caching, chunk 8); one engine seed
(62026) for every arm; tokenizer from `dpo`. Cut share (finish = length) reported per arm.

**Endpoints (stored rows where the protocol matches, fresh otherwise):**
- `s2300` on the reach prompts: olmo-ifcurve's `B_s2300` (32 fresh draws per prompt, drawn after the set was fixed),
  re-gated by this run's readers inside this run's blinded batches (below). On the 176 other prompts: olmo-ifomega's
  `F_s2300_ifb` (8 per prompt). Same sampler path, template, vLLM version and decoding.
- `dpo`: the fresh `dpo` arm everywhere; on the 176 non-reach prompts pooled with olmo-ifomega's stored `F_dpo_ifb`
  (16 per prompt). The stored `dpo` draws on the reach prompts are not used: they selected the set (0 genuine in ≥ 256
  by definition). Robustness: G with the fresh `dpo` arm alone.

## Grading and hand gate

Strict = `olmo_ifomega/grade.py` (the official checkers), on the pod after each job; re-graded on the VPS side by the
reviewer. Hand gate on the reach prompts, `olmo-ifcurve`'s machinery and rules:
- **Scope (the deciding successes):** per cell (arm × reach prompt), the first min(strict, 8) strict successes in draw
  order (chunk, index) are labelled; for `s2300`, the first min(strict, 8) of `B_s2300`'s 32. Estimated genuine rate of
  a cell = (genuine labelled + unlabelled strict × genuine share of the labelled) / draws.
- Mechanical rule-1 screen (olmo-ifcurve's `hand.py screen`, gamed without a reader), identity inheritance within this
  run's labels (same prompt, identical answer after whitespace collapse); counted separately everywhere.
- Blinded reader sub-agents (`olmo_ifcurve/handcheck_prompt_if.md`, run name changed) see the prompt, the constraints
  with the checker's verdicts and the answer; no model, arm, step or thinking. Random item ids; key out of reader reach;
  batches are seeded shuffles across all arms and `s2300`.
- Second reads: a seeded 25 % of reader-labelled items, plus every reader-labelled item of the `dpo`, `T1` and `T4`
  arms; a split goes to a third reader; majority of three, and I read every split. My confirming rules: olmo-ifomega's
  1–5, olmo-iffu's 6, olmo-ifladder's 7–12, olmo-ifcurve's 13–14, unchanged; a new reading becomes a dated rule 15+
  applied to every item of that prompt (all arms and `s2300`), with the changes listed. Per-prompt consistency audits
  by sub-agents after each round, adjudicated by me.
- Cross-run calibration: on the `B_s2300` items that carry olmo-ifcurve final labels, the agreement with this run's
  labels is reported.
- Reported per arm: strict, genuine (estimated), gamed share among labelled, and how many labels came from readers,
  the screen and inheritance.

## G and readings (thresholds from the brief)

G(arm) = (r_arm − r_dpo) / (r_s2300 − r_dpo), with r = mean over prompts of the cell rate, on (R) the 48 reach prompts'
estimated genuine rate (primary) and (A) the 218 prompts' strict pass@1. Intervals: paired prompt bootstrap (all arms
and both endpoints resampled on the same prompts), 10,000 replicates, percentile 95 %.

1. **"Low-rank carries it":** G(T16) ≥ 0.5 and G(C16) ≤ 0.2.
2. **"High-rank":** G(T256) < 0.5 while G(F448) ≥ 0.75.
3. **"Outside the 448 matrices":** G(F448) < 0.75.
4. **Otherwise:** k₅₀ = the smallest k ∈ {1, 4, 16, 64, 256} with G(T_k) ≥ 0.5 (">256" if none), set beside Part 1's
   median signal rank and spike count of `N2300`.

Each reading is scored on point estimates, separately on R and A; it **holds** when it holds on both, "holds on R
only" / "on A only" otherwise. Each threshold comparison is **firm** when the 95 % interval lies on the same side of
the threshold, otherwise **tentative**. Readings are not exclusive; every one that holds is reported.

**Detection limit.** Simulated from the stored per-prompt rates (`olmo_lowrank/mdd_sim.py`; `dpo` / `s2300` rows of
olmo-ifcurve): the 95 % half-width of G is 0.04–0.07 on R and 0.05–0.06 on A when an arm tracks s2300 prompt by
prompt; with per-prompt deviations and hand-gate sampling, ≈ 0.10. A G within ≈ 0.10 of a threshold is not resolved,
and two arms' G are distinguishable at ≈ 0.14.

## Expected results (binding; a miss is reported as a miss)

The proposal's guesses (scored as written):
- **P1** RL's net change (`N2300`, 32B) shows spikes above the rounding floor — scored: median spike count (floor B)
  ≥ 1 across the 448 matrices — **and** single 50-step intervals are mostly floor — scored: their energy-weighted S₁₆
  ≤ 1.5 × floor A's.
- **P2** 0.3 ≤ G(T16) ≤ 0.7 (on R; also reported on A).
- **P3** `lora_main` overlaps RL's top-16 subspace far more than its 0.0052 cosine suggests — scored: the median
  overlap over the 448 matrices at t = 2,300 ≥ 0.052 (10× the cosine).

Mine (32B unless stated):
- **E1** `N2300` is high-rank: energy-weighted S₁₆ ≤ 3× the Gaussian baseline's, and median signal rank (floor A)
  censored at ≥ 256.
- **E2** SFT's total change is more concentrated than RL's: S₁₆(`SFT`) > S₁₆(`N2300`).
- **E3** S₁₆ of `N<t>` rises with t from 50 to 2,300 (Spearman ρ > 0 over the 7 steps).
- **E4** G(T16) < 0.3 on R; G(T256) < 0.5 on R; G(F448) ≥ 0.75 on R; G(C16) ≥ 0.5 on R — i.e. reading 2 ("high-rank").
- **E5** `lora_main`'s median overlap at 2,300 ≥ 3× `lora_ctrl`'s and ≥ 3× random, but < 0.052 (P3 misses).
- **E6** the 7B `N1375` has a lower S₁₆ than the 32B `N2300` (smaller total move, 0.08 % vs 0.36 % of ‖θ‖).

## Stage 0 (≤ $5) and the re-cost gate

One community H200 pod: (1) download throughput (`dpo` + `s2300`, hf_xet); (2) SVD time and accuracy for one 32B MLP
(gate, layer 32) and one attention matrix (q, layer 32) of D: full fp32 / fp64 and randomized top-256 at (p, q) ∈
{64, 256} × {4, 8, 16}; (3) vLLM's maximum LoRA rank (engine start with the real T256 adapter; then 128, 64 if it fails);
(4) draw throughput of T256 on a seeded 24 of the arm's prompts (`random.Random(4949)`; 12 reach × 16 + 12 others × 4),
appended to T256's output file and kept as part of the arm if the run continues (the continuation skips finished
requests and keeps seed 62026); (5) the zero-delta check. Re-cost =
stage 0 + Part 1 (measured download and SVD rates) + Part 2 (8 arms × 1,472 draws at the measured s / draw for T256 and
olmo-ifcurve's for plain models) + model loads + 10 %. If the projection exceeds $72, a dated question goes to
`QUESTIONS.md` with the default "apply the brief's cut order (7B spectra; the 176-prompt draws 4 → 2; T1 and T4;
single-interval spectra 3 → 1) until ≤ $72", applied after 1 h without an answer. T16, T256, F448 and C16 are always
kept.

## Budget, compute, stop rule

$80, dollars binding (`podbudget olmo-lowrank --set 60 80` before the first pod); RunPod balance kept above $35.
Compute per arm and per Part-1 job (GPU-seconds and GPU type with its billed rate, generated tokens, draws) as registry
rows (`record.py`) and a table in the write-up. All arms are matched on prompts and draws; generated tokens differ by
model and any arm above 1.25× the `dpo` arm's tokens is flagged. Hard stop 2026-11-28 19:44 UTC (48 h from the run's
start). Weights stay on pods; adapters, samples, grades and tables go to the bucket.
