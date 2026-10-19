# Screening agent A: RL models evaluated by Yue et al. (2504.13837v5), configs and bases

Written 2026-10-19 by agent:claude for run rl-compute-share. Every value has a row in
[`A_yue.tsv`](A_yue.tsv) (claim IDs below; `verify_ledger.py`: 324 / 324 quotes found).
Conventions: **[interp.]** = my interpretation, not a source statement; **not reported** = searched,
not found; **ASSUMED** = EasyR1 default used as a stand-in for Yue's unstated config. Yue's own VeRL runs
(§4.3–4.4) are not covered here. No FLOPs or ratios are computed.

Yue measures every model the same way: pass@k with n = k_max samples (unbiased estimator, A-YUE-estimator); T = 0.6,
top-p 0.95, max 16,384 generated tokens (A-YUE-eval). k_max: 128 for GSM8K/MATH500/Minerva (Olympiad for Qwen) and
1024 for AIME24/AMC23 (Olympiad for Llama) (A-YUE-kmax-math). Overall verdict: RLVR "does not introduce
fundamentally new reasoning capabilities" (A-YUE-verdict). Yue v1 is dated 2025-04-18 (A-YUE-v1-date).

---

## 1. SimpleRL-Zoo: Llama-3.1-8B, Qwen2.5-7B, Qwen2.5-14B, Qwen2.5-32B

Zeng et al., *SimpleRL-Zoo*, arXiv **2503.18892v3** (6 Aug 2025, A-SRZ-version-date). Proposed key `zengSimpleRLZooInvestigatingTaming2025`.

| Field | Llama-3.1-8B | Qwen2.5-7B | Qwen2.5-14B | Qwen2.5-32B |
|---|---|---|---|---|
| Checkpoint | `hkust-nlp/Llama-3.1-8B-SimpleRL-Zoo` (A-SRZ-ckpt-llama8b) | `hkust-nlp/Qwen-2.5-7B-SimpleRL-Zoo` (A-SRZ-ckpt-qwen7b) | `hkust-nlp/Qwen-2.5-14B-SimpleRL-Zoo` (A-SRZ-ckpt-qwen14b) | `hkust-nlp/Qwen-2.5-32B-SimpleRL-Zoo` (A-SRZ-ckpt-qwen32b) |
| Base | Llama-3.1-8B base (A-YUE-SRZ-bases) | Qwen2.5-7B base | Qwen2.5-14B base | Qwen2.5-32B base |
| Params total / active (dense) | 8,030,261,248 (A-LLAMA-params) | 7.61B; non-emb 6.53B (A-Q25-7b-params, -nonemb) | 14.7B; 13.1B (A-Q25-14b-params, -nonemb) | 32.5B; 31.0B (A-Q25-32b-params, -nonemb) |
| Base D | ~15T (A-LLAMA-tokens, A-LLAMA-herd-tokens) | 18T (A-Q25-tokens) | 18T | 18T |
| RL algorithm | GRPO, token-level length-rectified loss, from base, verl (A-SRZ-algo, A-SRZ-loss, A-SRZ-framework) | same | same | same |
| Unique prompts | "Easy" = GSM8K + MATH lv1, "roughly 8,000" (A-SRZ-data-llama, A-SRZ-data-levels) | "Hard" = MATH lv3–5, ~8,000 (A-SRZ-data-qwen) | same as 7B | same as 7B |
| Epochs | not reported; script cap 20 (A-SRZ-script-epochs) | same | same | same |
| Steps | not reported; Fig. 1 x-axis 0–100 (A-SRZ-steps-axis-llama) | "approximately 100 steps" (README, A-SRZ-hw-7b-14b); x-axis 0–100 (A-SRZ-steps-axis-qwen7b) | "approximately 100 steps" (A-SRZ-hw-7b-14b), but Fig. 11 x-axis 0–150 (A-SRZ-steps-axis-qwen14b) | not reported; x-axis 0–150 (A-SRZ-steps-axis-qwen32b) |
| Prompts / step | 1,024 (A-SRZ-prompts-per-step) | 1,024 (A-SRZ-cmd-7b) | 1,024 | 1,024 (A-SRZ-cmd-32b) |
| Group size | 8 (A-SRZ-group-size) | 8 | 8 | 8 |
| Max response | 8,192 (A-SRZ-max-resp-len) | 8,192 | 8,192 | 8,192 |
| Mean response | training mean not reported; eval-length axis 0.5–2.0K (A-SRZ-len-axis-llama) | eval axis 0.7–1.0K (A-SRZ-len-axis-qwen7b) | not reported (Fig. 11 not parsed) | eval axis 0.5–0.8K (A-SRZ-len-axis-qwen32b) |
| Prompt length | max 1,024 (A-SRZ-script-promptlen); simple prompt (A-SRZ-prompt-simple) | max 1,024; boxed prompt (A-SRZ-prompt-boxed) | same | same |
| KL reference | yes, KL loss 1e-4 (A-SRZ-kl, A-SRZ-script-klref) | yes, 1e-4 | yes, 1e-4 | yes, 1e-3 |
| Critic | no (A-SRZ-critic) | no | no | no |
| Off-policy / dyn. sampling | none; mini-batch 256 (A-SRZ-minibatch) | same | same | same |
| GPU / time | not reported | 2×8 H100-80G, ~15 h (A-SRZ-hw-7b-14b) | 2×8 H100-80G, ~15 h (same sentence) | 8×8 H100-80G, 1.5 days (A-SRZ-hw-32b) |

- **Paper's verdict:** leans towards "create". Zero RL "is not just reranking ... it enhances the model's fundamental
  reasoning abilities" (A-SRZ-verdict). The evidence is pass@k up to k = 128 on the AIME24 + AMC23 average for
  **Mistral-Small-24B only** (A-SRZ-verdict-metric), a model Yue did not test.
- **Yue:** uses the released SimpleRL-Zoo models (A-YUE-SRZ-models) on all six math benchmarks, k_max 128/1024 (A-YUE-kmax-math). The base overtakes the RL model at large k.
- **Caveats.** The HF cards are empty (license only; the 14B repo has no README) (A-SRZ-hfcard-empty), so the step of each
  released checkpoint is unknown. "~100 steps / 15 h" is one README sentence covering both 7B and 14B. The figure axes
  give the plotted range, not the final step. The response-length axes are eval-time lengths averaged over 6 benchmarks
  (16K eval budget, A-SRZ-eval-len) and are axis ranges, not means. [interp.] Under verl semantics, 1,024 prompts with
  mini-batch 256 means 4 optimizer updates per rollout step; ~100 steps × 1,024 prompts / ~8K prompts ≈ 12 passes.
  The HF data repo has 50,100 train rows across 6 folders (3 levels × 2 prompt formats) (A-SRZ-data-hf-rows, A-SRZ-data-formats).

## 2. Oat-Zero-7B

Liu et al., *Understanding R1-Zero-Like Training: A Critical Perspective*, arXiv **2503.20783v2** (6 Oct 2025, COLM 2025; A-OAT-version-date, A-OAT-venue). Proposed key `liuUnderstandingR1ZeroLikeTraining2025`.

| Field | Value |
|---|---|
| Checkpoint | `sail/Qwen2.5-Math-7B-Oat-Zero` (A-OAT-hf-base); Yue's legend "Qwen-2.5-Math-7B-Oat-Zero" (A-YUE-OAT-legend) |
| Base | `Qwen/Qwen2.5-Math-7B` (A-OAT-hf-base, A-OAT-script-base) |
| Params | 7,615,616,512, dense (A-QMATH-params) |
| Base D | Qwen2.5-7B 18T (A-Q25-tokens) + continued pretraining on Qwen Math Corpus v2, "over 1T" tokens (corpus size; tokens actually trained not stated) (A-QMATH-corpus-v2, A-QMATH-init) |
| RL algorithm | Dr. GRPO, Qwen-Math template (A-OAT-recipe, A-OAT-hf-template, A-OAT-script-template) |
| Unique prompts | MATH level 3–5 (A-OAT-hf-data); folder `math_lvl3to5_8k` (A-OAT-script-data). Exact count not reported ([interp.] ~8K from the folder name) |
| Epochs / steps | not reported (script cap: 20 prompt epochs, A-OAT-script-epochs) |
| Prompts / step | 128 (A-OAT-script-prompts; dataloader semantics A-OAT-learner-semantics) |
| Group size | 8 (A-OAT-group-size, A-OAT-script-n) |
| Max response / prompt | 3,000 (A-OAT-max-resp-len, A-OAT-script-genmax) / 1,024 (A-OAT-script-promptmax) |
| Mean response | not reported for the 7B run |
| KL / critic | no / no (A-OAT-kl, A-OAT-critic-script) |
| Off-policy | 1 inner update epoch (A-OAT-update-epochs); [interp.] train batch of 128 responses vs 1,024 responses per step means 8 optimizer steps per policy step (A-OAT-script-trainbs, A-OAT-script-buffer); no dynamic sampling |
| GPU / time | **27 h on 8 × A100** (A-OAT-gpu-hours, A-OAT-gpu-hours-readme); all experiments ran on 8 × A100 in about a day (A-OAT-hw-all) |
| Paper's verdict | leans towards "elicit": templates destroy the base capability and RL reconstructs it; "be more conservative" about pure-RL gains; RL works by "reinforcing useful reasoning behaviors instead of infusing new knowledge" (A-OAT-verdict, A-OAT-verdict-2). Measured with greedy pass@1 averaged over 5 benchmarks (A-OAT-script-evaltemp, A-OAT-benchmarks), on Qwen2.5-Math-1.5B for the template study (A-OAT-verdict-model); no pass@k |
| Yue | AIME24, k up to 1024 (A-YUE-OAT-DAPO-models, A-YUE-OAT-DAPO-kmax): the base eventually overtakes the RL model (A-YUE-OAT-DAPO-verdict). Also in Fig. 7 (Minerva, k ≤ 128) |

## 3. DAPO-32B

Yu et al., *DAPO*, arXiv **2503.14476v2** (20 May 2025, A-DAPO-version-date). Proposed key `yuDAPOOpenSourceLLM2025` (≠ `tongDAPORecipe2025`).

| Field | Value |
|---|---|
| Checkpoint | `BytedTsinghua-SIA/DAPO-Qwen-32B`, the full-DAPO run (50%+ on AIME24) (A-DAPO-ckpt, A-DAPO-ckpt-full); Yue's legend "DAPO-32B" vs "Qwen-2.5-Base-32B" (A-YUE-DAPO-legend) |
| Base | Qwen2.5-32B **base** (A-DAPO-base, A-DAPO-hf-base); 32.5B, non-emb 31.0B (A-Q25-32b-params, -nonemb); D = 18T (A-Q25-tokens) |
| RL algorithm | DAPO (GRPO family; clip-higher 0.2/0.28; token-level loss; overlong shaping; dynamic sampling) (A-DAPO-clip, A-DAPO-overlong, A-DAPO-dynsamp) |
| Unique prompts | 17K (A-DAPO-data). The HF file has 1,791,700 rows (A-DAPO-data-hf-rows); [interp.] the prompts are duplicated |
| Epochs | not reported in the paper; the current verl-recipe copy sets `total_epochs=1` over the 1.79M-row file (A-DAPO-recipe-epochs) |
| Steps | **not stated in text.** Fig. 1 x-axis runs 0–10,000 "Training Steps" and the caption says "gradient update steps" (A-DAPO-steps-axis, A-DAPO-steps-unit). Fig. 7 (the DAPO run) runs 0–5,000 (A-DAPO-len-axis). With 16 gradient updates per rollout step (A-DAPO-minibatch), **the rollout-step count is ambiguous by a factor of 16** [interp.] |
| Prompts / step; group | 512; 16 (A-DAPO-prompts-per-step, A-DAPO-group-size) |
| Max response / prompt | 20,480 = 16,384 + 4,096 soft cache (A-DAPO-max-resp-len, A-DAPO-overlong) / 2,048 (recipe, A-DAPO-recipe-promptlen) |
| Mean response | not in text; Fig. 7(a) y-axis spans 1,000–4,000 tokens (A-DAPO-len-axis) |
| KL / critic | no / no (A-DAPO-kl, A-DAPO-critic) |
| Dynamic sampling | yes: over-sample, then drop groups with accuracy 0 or 1 (A-DAPO-dynsamp). The cost "is dynamic" and is not quantified for this run (A-DAPO-dynsamp-cost). The recipe uses generation batches of 3 × 512 = 1,536 prompts, at most 10 per step (A-DAPO-recipe-genbs, A-DAPO-recipe-maxgen). Yue's own VeRL DAPO runs needed ~3–6× more samples (A-YUE-dyn-oversample; a different run) |
| GPU / time | **128 H20 GPUs** (project page, A-DAPO-hw); wall-clock not reported. Recipe default is 16 nodes × 8 (A-DAPO-recipe-nodes) |
| Paper's verdict | leans towards "create", qualitatively: RL "gradually gives rise to entirely new modes of reasoning that were initially absent" (A-DAPO-verdict). Case study only; the reported metric is AIME avg@32 (A-DAPO-eval). The paper also claims 50 on AIME24 with 50% of R1-Zero-Qwen-32B's steps (A-DAPO-claim-steps) |
| Yue | AIME24, k up to 1024: the base overtakes DAPO-32B (A-YUE-OAT-DAPO-kmax, A-YUE-OAT-DAPO-verdict) |

Caveat: the paper's recipe link (verl branch `gm-tyx/puffin/main`) (A-DAPO-orig-recipe-link) now returns 404 and no Wayback copy exists. The
script cited here is the current `verl-project/verl-recipe` copy, which may differ from the paper's run.

## 4. CodeR1-Zero-Qwen2.5-7B

Liu & Zhang 2025, GitHub `ganler/code-r1` (no paper). Proposed key `liuCodeR1ReproducingR12025`.

| Field | Value |
|---|---|
| Checkpoint | `ganler/CodeR1-Zero-Qwen2.5-7B-12k-832`, 832 steps (A-CR1-ckpt); matches Yue's "12K ... 832 steps" (A-YUE-CR1). Uploaded 2025-03-02; the HF repo has no model card (A-CR1-ckpt-created) |
| Base | Qwen2.5-7B-**Instruct**-1M (A-CR1-base, A-YUE-CR1-legend); 7.61B, non-emb 6.53B (A-Q1M-params, -nonemb) |
| Base D | an intermediate Qwen2.5-7B base (≤ 18T) + 5-stage long-context continued pretraining (**token count not reported**) + 2-stage SFT + offline RL (A-Q1M-init, A-Q1M-stages, A-Q1M-lens, A-Q1M-sft, A-Q1M-rl) |
| RL algorithm | GRPO (A-CR1-script-algo) |
| Unique prompts | 12K = 2K LeetCode + 10K TACO-verified (A-CR1-data, A-CR1-data-taco); HF train split has 12,458 rows (A-CR1-data-hf-rows) |
| Epochs | cap 8 (A-CR1-script-epochs); [interp.] 832 × 16 = 13,312 prompt draws ≈ 1.07 passes |
| Steps | 832 (A-CR1-ckpt) |
| Prompts / step; group | 16; 16 (A-CR1-script-prompts, A-CR1-script-n; same in the pre-release script, A-CR1-prerelease-prompts) |
| Max response / prompt | 4,096 / 2,048 (A-CR1-script-resplen, A-CR1-script-promptlen) |
| Mean response | not reported (the wandb report is not machine-readable) |
| KL / critic | yes, KL loss 0.001 low_var_kl (A-CR1-script-kl) / no (GRPO) |
| Off-policy | none stated; mini-batch = GPUs × 8 × 4 (A-CR1-script-minibatch) |
| GPU / time | script "optimized for single-node 8x H200" (A-CR1-hw); wall-clock not reported |
| Verdict | none; reports LCB v5 29.7 (A-CR1-result). Yue reproduced 28.6 (A-YUE-CR1-repro) |
| Yue | LCB v5 (279 problems), HumanEval+, MBPP+; k up to 128 (A-YUE-code-vl-kmax) |

Caveat: `main_grpo.sh` was edited on 2025-03-03, after the checkpoint upload (lr 1e-6 → 5e-7; micro-batch 32 × grad-acc 1 → 8 × 4, i.e. the same 256 on 8 GPUs)
(A-CR1-script-change, A-CR1-prerelease-lr, A-CR1-script-lr, A-CR1-prerelease-microbatch, A-CR1-prerelease-gradacc, A-CR1-script-microbatch, A-CR1-script-gradacc, A-CR1-script-prerelease-date). The prompts, group size, lengths, KL and epochs are identical in both versions.

## 5. DeepCoder-14B-Preview

Luo et al. 2025, together.ai / Agentica blog (grade A), HF card, rllm `deepcoder` branch scripts (committed 2025-04-08, A-DC-script-date). Proposed key `luoDeepCoderFullyOpenSource2025`.

| Field | Value |
|---|---|
| Checkpoint | `agentica-org/DeepCoder-14B-Preview` (Yue's legend "Deepcoder-14B-Preview (RL)", A-YUE-DC-legend) |
| Base | DeepSeek-R1-Distill-Qwen-14B (A-DC-card-base, A-YUE-DC); 14,770,033,664 params (A-R1D-params) |
| Base D | Qwen2.5-14B 18T (A-R1D-base, A-Q25-tokens) + SFT on 804,745 R1-generated samples (mean 5,355.3 tokens) for 2–3 epochs (A-R1D-samples, A-R1D-epochs) |
| RL algorithm | GRPO+ (no entropy loss, no KL, overlong filtering, clip-high) + iterative context lengthening (A-DC-algo); ε_high 0.28 and entropy coefficient 0 (A-DC-16k-cliphigh, A-DC-16k-entropy) |
| Unique prompts | 24K = 7.5K TACO-Verified + 16K SYNTHETIC-1 + 600 LCB (A-DC-data, A-DC-card-data) |
| Epochs | not reported (script cap 100, A-DC-16k-epochs) |
| Steps | **total not reported in text.** The switch from 16K to 32K happens at step 180 (A-DC-ctx-switch); steps take 1,200–2,500 s and the run took 2.5 weeks in total (A-DC-step-time); README says ~2,000 s/step (A-DC-readme-gpus) |
| Prompts / step | 16K stage: 32; 32K stage: 128 (A-DC-16k-prompts, A-DC-32k-prompts). The blog says "1024 problems" per iteration (A-DC-batch-blog); [interp.] this matches 128 × 8 samples |
| Group size | 8 (A-DC-16k-n) |
| Max response / prompt | 16,384 → 32,768 (A-DC-16k-len, A-DC-32k-len, A-DC-card-ctx) / 2,048 (A-DC-16k-promptlen) |
| Mean response | **8K rising to 17.5K tokens** over training (A-DC-mean-len) |
| KL / critic | no / no (A-DC-kl, A-DC-16k-kl, A-DC-16k-algo) |
| Off-policy / dyn. sampling | no dynamic sampling; offline difficulty filtering instead (A-DC-card-filter). The blog's one-off pipelining samples one iteration ahead (A-DC-oneoff), but the blog says it was applied to DeepCoder-**1.5B** (A-DC-pipeline-1p5b); not stated for the 14B run |
| GPU / time | **32 H100 for 2.5 weeks** (A-DC-gpu-time) |
| Verdict | none (claims generalisation to 64K context) |
| Yue | LiveCodeBench only, k ≤ 64, 32k response length (A-YUE-DC, A-YUE-DC-kmax) |

Caveat: the 16K script sets `nnodes=1` but carries a "4 nodes, 8 A100-80GB" comment, and the README says 32 GPUs for
both stages (A-DC-16k-nodes, A-DC-16k-comment, A-DC-readme-gpus).

## 6. Yue's own EasyR1 run: Qwen2.5-VL-7B on Geometry3K (config **ASSUMED**)

Yue states no hyperparameters (A-YUE-EZ). Its legend names the base "Qwen2.5-VL-7b-Instruct" (A-YUE-EZ-legend).
The values below are EasyR1's example defaults at commit 174da500 (2025-04-14, the last `config.yaml` change before Yue v1 on 2025-04-18;
the next change was on 2025-04-22) (A-EZ-config-commit, A-EZ-config-next-commit). They are unchanged on `main` today (A-EZ-main-prompts, A-EZ-main-n, A-EZ-main-promptlen, A-EZ-main-resplen, A-EZ-main-gbs, A-EZ-main-epochs). Proposed key `zhengEasyR1EfficientScalable2025`.

| Field | Value |
|---|---|
| Base | `Qwen/Qwen2.5-VL-7B-Instruct` (A-EZ-model); 8,292,166,656 params incl. ViT (A-QVL-params) |
| Base D | Qwen2.5 LLM 18T (A-QVL-init, A-Q25-tokens) + 4.1T multimodal tokens (1.5T ViT-only + 2T + 0.6T) (A-QVL-tokens, A-QVL-stages, A-QVL-stage-trainable) + SFT on ~2M entries + DPO (A-QVL-sft, A-QVL-post) |
| RL algorithm | GRPO (A-EZ-algo) ASSUMED |
| Unique prompts | Geometry3K train = 2,101 (A-EZ-geo3k-train, A-EZ-data) ASSUMED split |
| Epochs | 15 (A-EZ-epochs, A-EZ-main-epochs) ASSUMED |
| Steps | not reported; [interp.] 15 × ⌊2101/512⌋ = 60 (or ~62 without drop_last) |
| Prompts / step; group | 512; 5 (A-EZ-prompts, A-EZ-n) ASSUMED |
| Max response / prompt | 2,048 / 2,048 (A-EZ-resplen, A-EZ-promptlen) ASSUMED |
| Mean response | not reported |
| KL / critic | yes, KL loss low_var_kl 1e-2 (A-EZ-kl, A-EZ-klloss) / no. ASSUMED |
| Off-policy | actor global batch 128 = verl's ppo_mini_batch (A-EZ-gbs, A-EZ-main-gbs); [interp.] 4 updates per step |
| GPU / time | not reported; default 8 GPUs per node (A-EZ-gpus); README estimate of 8×40GB for 7B is a requirement, not a run record (A-EZ-hw-estimate) |
| Yue | filtered MathVista-TestMini and MathVision-TestMini, k ≤ 128 (A-YUE-EZ, A-YUE-code-vl-kmax) |

## 7. Magistral Medium (and Magistral Small)

Rastogi et al. (Mistral-AI), *Magistral*, arXiv **2506.10910v1** (12 Jun 2025, the only version; A-MAG-version-date). Proposed key `rastogiMagistral2025`.

| Field | Value |
|---|---|
| Model in Yue | the Magistral-Medium-2506 API vs "Mistral-Medium-3 (Base)" (A-YUE-MAG, A-YUE-MAG-kmax) |
| Starting checkpoint | **Mistral Medium 3 Instruct** (A-MAG-start), i.e. not a pretrained base; multimodal with a vision encoder (A-MAG-multimodal) |
| Params / D | **undisclosed.** Yue: "the model size is not disclosed" (A-YUE-MAG). Mistral only says it deploys on "four GPUs and above" (A-MAG-m3-deploy). No pretraining-token or compute statement found |
| RL algorithm | GRPO, modified: no KL, no critic, zero-advantage groups filtered out, ε_high 0.26–0.28; Clip-Higher and soft length penalty taken from DAPO (A-MAG-kl, A-MAG-critic, A-MAG-filter, A-MAG-clip, A-MAG-cliphigher-dapo, A-MAG-softlen-dapo) |
| Unique prompts | 38k math (after 699k → 501k → 38k filtering) + 35k code (A-MAG-math-data, A-MAG-code-data); the subset changes by stage (A-MAG-stages) |
| Epochs / steps | not reported |
| Batch | in **completions**, not prompts: 8k → 4k → 2k (A-MAG-batch-sched, A-MAG-batch-unit); n_batch = n_minibatch, so one update per batch (A-MAG-minibatch) |
| Group size | not reported |
| Max response | non-penalised length l_max − l_cache went 16k → 24k → 32k (A-MAG-len-sched); l_max itself not given |
| Mean response | not reported for Medium |
| Off-policy | asynchronous generators with weights swapped mid-generation (A-MAG-async); n_async/n_batch ≤ 2 (A-MAG-minibatch). Groups with zero advantage are generated then dropped; fraction not reported |
| GPU / time | not reported |
| Paper's verdict | no create-vs-elicit test. "increasing completion length is the main resource" (A-MAG-verdict). AIME24 pass@1/maj@64 went from 26.8/43.4 to 73.6/90.0, averaged over 64 runs (A-MAG-aime, A-MAG-eval-runs) |
| Yue | AIME24 and AIME25, k ≤ 1024, 40k context (A-YUE-MAG-kmax, A-YUE-MAG-ctx): "significant gains at low k, but little or no improvement at higher k" (A-YUE-MAG-verdict) |

**Magistral Small:** starts from Mistral Small 3 Instruct (24B). It gets 4 epochs of SFT on Magistral Medium traces
(including 10% general instruction data), then RL with batch 2,048 sequences, 32k non-penalised length and ε_high 0.3
(A-MAG-small-sft, A-MAG-small-instr, A-MAG-small-rl, A-MAG-small-eps, A-MAG-small-params). It is therefore distilled
from an RL-trained model. AIME24 maj@64: SFT 90.0, RL-only 86.7, SFT+RL 83.3. RL raised pass@1 but lowered maj@64 (A-MAG-small-maj).

## 8. Qwen2.5-Math-7B-Instruct (Yue Fig. 7 baseline: Minerva, k ≤ 128; A-YUE-QMI, A-YUE-QMI-bench, A-YUE-QMI-kmax)

Yang et al., *Qwen2.5-Math Technical Report*, arXiv **2409.12122v1**. Proposed key `yangQwen25MathTechnicalReport2024`.

| Field | Value |
|---|---|
| Base | Qwen2.5-Math-7B: initialised from Qwen2.5 base, then continued pretraining on Math Corpus v2 (>1T tokens, 4K context); post-training follows (A-QMATH-init, A-QMATH-corpus-v2, A-QMATH-ctx, A-QMATH-posttrain) |
| SFT | 2,000K EN + 500K ZH CoT samples; TIR 190K + 205K problems; 3 epochs at 4,096 tokens (A-QMATH-sft-cot, A-QMATH-sft-tir, A-QMATH-sft) |
| RL algorithm | GRPO with reward = reward model + rule verifier (A-QMATH-rl-algo, A-QMATH-rl-reward); no critic (A-QMATH-critic) |
| Unique prompts | 66K queries (A-QMATH-rl-queries) |
| Steps / epochs | not reported |
| Group size | 32 (A-QMATH-rl-group) |
| Samples per episode | 4,096 for 7B (A-QMATH-rl-episode); [interp.] = 128 queries; global batch 512 (A-QMATH-rl-gbs) |
| Max response | not reported (SFT sequence length 4,096; 4K context) |
| KL | yes, 1e-3 (A-QMATH-rl-kl) |
| GPU / time | not reported |

## 9. Bases: N and D

| Base checkpoint | Used by | Params total (non-emb) | Pretraining tokens D | Training after pretraining, before the RL studied | IDs |
|---|---|---|---|---|---|
| Qwen2.5-7B | SimpleRL-Zoo-7B | 7.61B (6.53B) | 18T, last stage at 32K ctx | none | A-Q25-tokens, A-Q25-longctx, A-Q25-7b-* |
| Qwen2.5-14B | SimpleRL-Zoo-14B; R1-Distill-14B | 14.7B (13.1B) | 18T | none | A-Q25-14b-* |
| Qwen2.5-32B | SimpleRL-Zoo-32B; DAPO | 32.5B (31.0B) | 18T | none | A-Q25-32b-* |
| Qwen2.5-Math-7B | Oat-Zero-7B; Qwen2.5-Math-7B-Instruct | 7,615,616,512 | 18T + CPT on >1T-token corpus (trained tokens not stated) | none | A-QMATH-params, A-QMATH-corpus-v2 |
| Llama-3.1-8B | SimpleRL-Zoo-Llama | 8,030,261,248 | ~15T ("15T+"); **1.46M H100-80GB GPU-hours**, defined as the "total GPU time required for training each model" | none | A-LLAMA-tokens, -tokens-table, -gpu-hours, -gpu-hours-def, -params |
| Qwen2.5-7B-Instruct-1M | Code-R1 | 7.61B (6.53B) | intermediate Qwen2.5 base + 5-stage long-context CPT (tokens **not reported**) | 2-stage SFT + offline RL | A-Q1M-* |
| Qwen2.5-VL-7B-Instruct | Yue's EasyR1 run | 8,292,166,656 (incl. ViT) | Qwen2.5 LLM (18T) + 4.1T multimodal | SFT on ~2M entries + DPO | A-QVL-* |
| DeepSeek-R1-Distill-Qwen-14B | DeepCoder | 14,770,033,664 | Qwen2.5-14B (18T) | SFT on 804,745 samples × mean 5,355.3 tokens × 2–3 epochs | A-R1D-* |
| Mistral Medium 3 Instruct | Magistral Medium | undisclosed | undisclosed | instruct tuning (undisclosed) | A-YUE-MAG, A-MAG-start |

## 10. Contamination and provenance flags

- **Qwen2.5 bases (SimpleRL Qwen models, DAPO, and indirectly Code-R1, DeepCoder and EasyR1):**
  - Pretraining "incorporate[s] training data from Qwen2.5-Math ... and Qwen2.5-Coder" (A-Q25-mathcode-data).
  - Synthetic math, code and knowledge data come from Qwen2-72B-Instruct and Qwen2-Math-72B-Instruct (A-Q25-synth).
  - SimpleRL-Zoo: Qwen2.5 "already exhibit[s] instruction-following abilities and reflective behaviors" (A-SRZ-flag-qwen).
  - Oat: Qwen2.5 bases "readily serve as chat models even without any template" and are "likely to be pretrained on concatenated question-response texts" (A-OAT-flag-chat, A-OAT-flag-qa).
  - Oat: the aha moment already appears in base models (A-OAT-aha).
- **Qwen2.5-Math-7B (Oat-Zero):** Corpus v2 includes data synthesised by a post-trained Qwen2-Math-72B-Instruct and generated math Q&A pairs (A-QMATH-synth, A-QMATH-synth-qa).
- **Llama-3.1-8B:** the data mix is 25% "mathematical and reasoning tokens" (A-LLAMA-mix). It was annealed on high-quality math and code with no benchmark training sets (A-LLAMA-anneal, A-LLAMA-anneal-nobench). The card's 25M synthetic examples are fine-tuning data, not base data (A-LLAMA-ft-synth).
- **RL starts from an instruct model, not a base:**
  - Code-R1: Qwen2.5-7B-Instruct-1M, SFT + DPO-like (A-Q1M-stage, A-Q1M-rl).
  - EasyR1: Qwen2.5-VL-7B-Instruct, SFT + DPO (A-QVL-post); its pretraining includes multimodal mathematics (A-QVL-math).
  - Magistral Medium: Mistral Medium 3 Instruct (A-MAG-start).
- **Distilled bases:**
  - DeepCoder starts from R1-Distill-Qwen-14B, SFT-only on DeepSeek-R1 outputs, i.e. distilled from an RL-trained model (A-R1D-card, A-R1D-sftonly).
  - Magistral Small is SFT'd on traces from the RL-trained Magistral Medium (A-MAG-small-sft).
- **Reward model in RL:** Qwen2.5-Math-7B-Instruct's RL reward includes a learned RM (A-QMATH-rl-reward).

## 11. Not found / UNVERIFIED / surprising

- **Not reported:**
  - SimpleRL-Zoo: per-model final steps, training mean length, Llama GPU time.
  - Oat-Zero-7B: steps, exact prompt count, mean length.
  - DAPO: wall-clock and GPU-hours, over-generation factor.
  - Code-R1: mean length, wall-clock.
  - DeepCoder: total steps.
  - Magistral: group size, steps, hardware, mean length, Medium 3 size and pretraining compute.
  - Qwen2.5-Math RL: steps, max length.
  - Qwen2.5-1M: long-context CPT tokens.
- **DAPO step unit:** the caption says "gradient update steps" and there are 16 updates per rollout step. Resolve this before using 5,000–10,000 as rollout steps.
- **SimpleRL 14B:** README says ~100 steps but the plot axis reaches 150.
- **DeepCoder scripts:** the 16K stage uses 32 prompts × 8 samples, not the blog's "1024 problems".
- **Mean response lengths from figure axes** (SimpleRL eval lengths, DAPO Fig. 7) are axis ranges, not means.
- **UNVERIFIED:** none of the values above is unverified. These are failed fetches, so no values were taken from them: the DAPO original recipe branch (404), the wandb training logs (JavaScript-only), and the Oat-Zero Notion blog (only partial text).

## 12. Proposed citekeys

`zengSimpleRLZooInvestigatingTaming2025`, `liuUnderstandingR1ZeroLikeTraining2025`, `yuDAPOOpenSourceLLM2025`,
`liuCodeR1ReproducingR12025`, `luoDeepCoderFullyOpenSource2025`, `zhengEasyR1EfficientScalable2025`,
`rastogiMagistral2025`, `yangQwen25MathTechnicalReport2024`, `yangQwen25TechnicalReport2024`,
`grattafioriLlama3Herd2024`, `baiQwen25VLTechnicalReport2025`, `yangQwen251MTechnicalReport2025`.
Existing key: `guoDeepSeekR1IncentivizesReasoning2025` (R1-Distill details; source fetched was 2501.12948v2).
