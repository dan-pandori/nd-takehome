# Decision memo: the same test on Olmo 3.1 Think 32B — cost, design, and what to change

DRAFT — the pilot's findings (§4) are filled in when the pilot is done.

## 1. Measured price on this pilot (7B, the RL settings)

Hardware and software: one A100-SXM4-80GB on RunPod community cloud (billed $1.39/h), vLLM 0.11.0 (the version
open-instruct pinned for RL), bf16 weights and KV cache, temperature 1, top-p 1, 16,384-token responses.

| model (pilot set, AIME 2023) | tokens / sample | cut at cap | throughput | $ / M generated tokens |
|---|---|---|---|---|
| Olmo-3-1025-7B base, plain decoding | 6,353 | 17.5 % | 557 tok/s | 0.69 |
| same, n-gram speculative decoding (adopted) | 6,169 | 15.8 % | 759 tok/s | 0.51 |
| RL-Zero step_2800, plain | 12,249 | 21.7 % | 472 tok/s | 0.82 |
| evaluation set, all phases | PHASE_TABLE | | | |

Why the 7B is this expensive: 32 KV heads (no grouped-query attention) make the KV cache 0.5 MB per token across the
32 layers until a sequence passes the 4,096-token sliding window (≈ 2.1 GiB for a 5k-token sequence). An 80 GB GPU
holds ≈ 25 long sequences, and each decode step re-reads ≈ 72 GB (weights + cache) at ≈ 1.37 TB/s (67 % of the A100's
peak). Throughput per dollar therefore tracks memory bandwidth per dollar, which is about equal across RunPod's NVIDIA
classes; the community A100 is the cheapest per token.

## 2. Olmo 3.1 Think 32B: the model and its checkpoints

- 64 layers (16 full attention, 48 sliding-window 4,096), 8 KV heads × 128 (GQA): **64 KB of KV per token** in the
  full-attention layers plus 0.75 GB per sequence in the windowed ones — about half the 7B's per sequence. Weights
  64.5 GB (bf16), so it needs ≥ 141 GB on one GPU (H200, B200) or two 80 GB GPUs with tensor parallelism.
- RL settings (`32b_think_rl.sh`): template `olmo_thinker` (with `<think>`), temperature 1.0, **32,768-token
  responses**, 64 prompts × 8 samples per step. Its RL data is not Dolci-RL-Zero-Math; the contamination check must be
  redone against the Think RL data.
- Checkpoints: `allenai/Olmo-3-32B-Think-DPO` (the RL start) and `allenai/Olmo-3.1-32B-Think` `step_0050` …
  `step_2300` (46, every 50) with `main` = `step_2300`.
- **Step numbering.** `Olmo-3.1-32B-Think` `step_0050`, `step_0300`, `step_0750` are byte-identical (all 14 safetensors
  shards) to `Olmo-3-32B-Think` `step_050`, `step_300`, `step_750`, and Olmo 3 Think 32B's `main` is its `step_750`.
  So 3.1 is one continuous RL run from the DPO checkpoint: steps 1–750 are the original Olmo 3 Think 32B run and steps
  751–2,300 are the extra 21 days on 224 GPUs that produced 3.1.
- RL compute share: ≈ 0.14 of pretraining in GPU-hours at step 2,300 (rl-compute-share's Olmo 3.1 row; it overstates
  the FLOP share because rollouts run at low utilisation); in FLOPs ≈ 2 × 10⁻³–7 × 10⁻³ at step 750 (that row's
  bounds), so ≈ 6 × 10⁻³–2 × 10⁻² at step 2,300 — the top of the range the literature review found tested.

## 3. Cost of the 32B test

Throughput model calibrated on §1 (decode re-reads weights + resident KV at 67 % of peak bandwidth; resident sequences
= KV pool / KV per sequence; speculative decoding × 1.36 as measured here), at a mean response of 16k tokens (Think
models write > 10k; 8k–24k changes the totals by −40 % / +50 %):

| GPU (RunPod, community $/h) | resident seqs | tok/s plain | $ / M plain | $ / M speculative |
|---|---|---|---|---|
| 1 × H200 141 GB ($3.59) | ≈ 34 | ≈ 880 | 1.13 | 0.83 |
| 1 × B200 180 GB ($5.98; vLLM 0.11 on Blackwell untested) | ≈ 55 | ≈ 1,830 | 0.91 | 0.67 |
| 2 × A100-SXM4-80GB, TP 2 ($2.78) | ≈ 44 | ≈ 735 | 1.05 | 0.77 |
| 2 × H100 SXM, TP 2 ($5.38) | ≈ 44 | ≈ 1,200 | 1.24 | 0.91 |
| 1 × 80 GB GPU | ≈ 4 | ≈ 125 | ≈ 6 | — |

DESIGN_TABLE

## 4. What the pilot found, and what to change for the 32B

FINDINGS
