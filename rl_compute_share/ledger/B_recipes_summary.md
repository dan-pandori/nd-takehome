# Agent B summary: open RL recipes and lab technical reports (run rl-compute-share, 2026-10-19)

Every value below carries its ledger claim id in brackets (`B_recipes.tsv`; 366/366 quotes verified). "n.r." means not
reported in the source text I read. Lines starting with **Interp.** are my reading, not the source's. No FLOP ratios
are computed here: the tables give raw fields, plus any ratio the source itself states.

## Statements that directly compare RL / post-training compute with pretraining compute (quoted)

| source (grade) | quote | claim |
|---|---|---|
| DeepSeek-V3.2, 2512.02556v1 §1 (B) | "Notably, this framework allocates a post-training computational budget exceeding 10% of the pre-training cost, unlocking advanced capabilities." | B-V32-ratio_stated-intro |
| DeepSeek-V3.2, §4.1 (B) | "Over recent months, we have observed consistent performance improvements correlating with extended RL training budget, which already exceeds 10% of the pre-training cost." | B-V32-ratio_stated-results |
| DeepSeek-V3, 2412.19437v2 §1 (B) | "The subsequent training stages after pre-training require only 0.1M GPU hours." (with Table 1: "in H800 GPU Hours \| 2664K \| 119K \| 5K \| 2788K") | B-V3-ratio_stated, B-V3-gpu_hours-table |
| ScaleRL, 2510.13786v1 §1 (C: Meta authors computing a ratio for DeepSeek) | "For instance, Deepseek-R1-Zero used 100,000 H800 GPU hours for RL training – 3.75% of its pre-training compute (Guo et al., 2025)." | B-SRL-ratio_stated-r1 |
| ScaleRL §1 (C, cited) | "...with more than 10 \times increase from o1 to o3 (OpenAI, 2025) and a similar leap from Grok-3 to Grok-4 (xAI Team, 2025)." | B-SRL-o1-o3 |
| Olmo 3, 2512.13961v2 §2 (B, qualitative) | "While pretraining accounts for the majority of total GPU hours, a non-trivial share is consumed by post-training and by the repeated checkpoint evaluations required when transitioning between major training stages." | B-OL3-ratio-qual |
| Lambert, RLHF book 2504.12501v12 (C) | "DeepSeek R1, famous for popularizing RLVR, used only about 5% of their overall compute in post-training – 147K H800 GPU hours for RL training on R1 [...], relative to 2.8M GPU hours for pretraining the underlying DeepSeek V3 base model" | B-RLHFB-ratio-r1 |
| Reflection, Beam blog, Oct 2026 (A; GPU-weeks for both stages, no ratio sentence) | "Beam was pretrained end-to-end in under four weeks on a cluster of 6,144 NVIDIA GB300 NVL72 GPUs." / "we deployed 10.5K NVIDIA GB300 GPUs for four weeks generating more than 100 million rollouts with a maximum context length of 256K tokens." | B-BEAM-pretrain-hardware, B-BEAM-rl-hardware |

Related, but not against pretraining: Qwen3 states that on-policy distillation needs "approximately only 1/10 of the GPU
hours" of RL on Qwen3-8B (17,920 vs 1,800 GPU-h) [B-QW3-ratio_stated, B-QW3-8b-rl-gpu_hours, B-QW3-8b-opd-gpu_hours].
INTELLECT-2 reports inference vs training FLOPs of ~4.5x [B-I2-ratio-train-infer]; Beam reports inference-to-training
GPU ratios of 3.9:1 to 5.4:1 [B-BEAM-rl-split]; Olmo 3 reports ~5x more GPU for inference than training [B-OL3-inference-share].

**Interp. (consistency check, not a ratio).** The secondary figures do not match the primary tables. Lambert's
"147K ... for RL training" is the R1 table's total, which includes R1-Zero (101K) and 5K for SFT-data creation
[B-R1-gpu_hours]. His "2.8M" is V3's full training including context extension and post-training; pre-training alone
is 2,664K [B-V3-gpu_hours-table]. ScaleRL's "100,000" matches R1-Zero only.

---

## 1. DeepSeek-R1 (R1-Zero and R1)

Sources: arXiv 2501.12948v2 (4 Jan 2026; carries the Supplementary Information as appendices); Nature 645, 633–638
(2025) [B-R1nat-pub] with Supplementary Information PDF (MOESM1). The Nature SI gives the same cost table
[B-R1natSI-gpu_hours, B-R1natSI-cost_usd, B-R1natSI-wallclock], so the "$294K" figure is in both.

| field | R1-Zero | R1 (final) |
|---|---|---|
| base model | DeepSeek-V3-Base [B-R1-base-model] | V3-Base + cold-start SFT [B-R1-coldstart] |
| params total / active | 671B / 37B [B-R1-base-params] | same |
| base D | 14.8T [B-R1-base-pretrain_tokens, B-V3-pretrain_tokens], plus a 2×1000-step YaRN extension (32K×1920 seqs, then 128K×480) [B-V3-ctxext-steps, B-V3-ctxext, B-V3-ctxext2] | same |
| base pretraining compute | 2,664K H800 GPU-h pre-training + 119K context extension [B-V3-gpu_hours-table] | same |
| RL algorithm | GRPO [B-R1-rl-algo] | GRPO, 2 RL stages |
| unique prompts | RL pool, Table 4: math 26K, code 17K, STEM 22K, logic 15K [B-R1-train_prompts-math/-code/-stem/-logic]; R1-Zero subset n.r. | + general 66K [B-R1-train_prompts-general] |
| epochs | 1.6 [B-R1-zero-epochs] | n.r. |
| steps | 10,400 [B-R1-zero-steps; Nature B-R1nat-zero-steps] | stage 1 n.r.; stage 2 1,700 [B-R1-stage2-steps] |
| prompts per step | 32 (512 responses) [B-R1-zero-prompts_per_step] | 32 (stage 1) [B-R1-stage1-group_size] |
| group size | 16 [B-R1-zero-group_size] | 16 [B-R1-stage1-group_size] |
| max response length | 32,768, then 65,536 after step 8.2k [B-R1-zero-max_resp_len] | 32,768 (stage 1) [B-R1-stage1-group_size] |
| mean response length | not given in text; Fig. 1(b) y-axis 0–20,000 tokens [B-R1-zero-mean_resp_len] | n.r. |
| prompt length | mean 122 tokens (math), 161 (STEM), ~420 (logic) [B-R1-prompt_len-math/-stem/-logic] | same pool |
| KL / reference | yes: 0.001; reference reset every 400 steps [B-R1-zero-kl] | yes: 0.001, clip ratio 10 [B-R1-stage1-clip] |
| critic | no [B-R1-critic] | no |
| off-policy / over-generation | 8,192 outputs per rollout, split into 16 minibatches, 1 inner epoch [B-R1-zero-rollout_batch]; no over-generation stated | same |
| GPUs / GPU-h | 512 H800, ~198 h; 101K H800 GPU-h; $202K [B-R1-zero-hardware-wallclock, B-R1-gpu_hours, B-R1-cost_usd] | 512 H800, ~80 h; 41K GPU-h; $82K. SFT-data creation 5K; total 147K GPU-h = $294K at $2/GPU-h [B-R1-r1-hardware-wallclock, B-R1-gpu_hours, B-R1-cost_usd, B-R1-cost_basis] |
| excluded compute | A100 preparatory runs on a 30B model, not costed [B-R1-prep-a100] | same |
| create-vs-elicit | no test. Framing: "pre-trained checkpoints inherently possess substantial potential" [B-R1-verdict]; RL "identify and optimize" base candidates [B-R1-verdict-select]. k max 64: R1 Pass@64 90.0% vs Pass@1 79.8% on AIME 2024, R1 only, no base-model curve [B-R1-kmax, B-R1-eval-k] | same |
| contamination | V3-Base web data contains OpenAI-model outputs [B-R1-base-contam]; exposed to "a significant volume of reasoning trace data" [B-R1-base-reasoning-exposure] | + cold start (thousands of long-CoT samples) and ~800k SFT samples between the RL stages [B-R1-coldstart, B-R1-sft800k] |

**Interp.** The 41K GPU-h for "the training phase of DeepSeek-R1" does not say whether it includes the two SFT runs. The
first-stage step count of R1 is not given, so per-stage token counts cannot be reconstructed.

## 2. DeepSeek-V3 (base-model compute; V3-chat post-training)

| field | value |
|---|---|
| arXiv | 2412.19437v2 |
| params | 671B / 37B [B-V3-params] |
| D | 14.8T at 4K sequence length [B-V3-pretrain_tokens]; batch ramps from 3,072 to 15,360 sequences [B-V3-pretrain_batch] |
| GPU-h | pre-training 2,664K; context extension 119K; post-training 5K; total 2,788K H800 GPU-h [B-V3-gpu_hours-table]; 180K GPU-h per trillion tokens on 2,048 H800 [B-V3-gpu_hours-per-T]; $5.576M at $2/h [B-V3-cost_usd, B-V3-cost_basis]; official run only [B-V3-cost-scope] |
| post-training | SFT on 1.5M instances [B-V3-sft-instances]; GRPO, no critic [B-V3-rl-algo]; reasoning distilled from the R1 series [B-V3-r1-distill]; RL steps, batch and lengths n.r. |
| verdict | none stated |

## 3. DeepSeek-V3.2 (and V3.1 base)

| field | value |
|---|---|
| arXiv | 2512.02556v1 |
| base | DeepSeek-V3.1-Terminus base checkpoint plus DSA continued pre-training [B-V32-base]. V3.1-Base = V3 base + 630B tokens (32K) + 209B tokens (128K) [B-V31-cpt-tokens]. CPT: 2.1B (indexer warm-up) + 943.7B (sparse stage) [B-V32-cpt-warmup, B-V32-cpt-sparse] |
| params | not restated in V3.2 (V3 lineage 671B / 37B [B-V3-params]) |
| RL | GRPO with unbiased KL, off-policy sequence masking, keep-routing [B-V32-rl-algo]; per-domain RL-trained specialists [B-V32-specialists]; mixed RL for "thousands of steps" [B-V32-steps]; rollout batch split into minibatches [B-V32-offpolicy]; agentic: >1,800 environments, 85,000 prompts [B-V32-agent-env] |
| prompts/step, group, max/mean length, epochs, GPUs | n.r. (128K context only) |
| ratio stated | post-training / RL budget > 10% of pre-training cost [B-V32-ratio_stated-intro, B-V32-ratio_stated-results]; more compute hypothesised to help [B-V32-more-compute] |
| verdict | none stated |
| contamination | final model trained on data distilled from RL-trained specialists [B-V32-specialists] |

The authors also write "due to fewer total training FLOPs, the breadth of world knowledge in DeepSeek-V3.2 still lags
behind" [B-V32-fewer-flops].

## 4. DeepSeek-V4 (2606.19348v1)

Params: Flash 284B / 13B; Pro 1.6T / 49B [B-V4-params-flash, B-V4-params-pro]. D: Flash 32T, Pro 33T
[B-V4-pretrain_tokens]. Max batch 75.5M / 94.4M tokens [B-V4-pretrain_batch-flash, B-V4-pretrain_batch-pro].
Post-training: per-domain specialists (SFT, then GRPO with R1/V3.2 hyper-parameters) [B-V4-specialist-grpo]; the mixed RL
stage is "entirely replaced by On-Policy Distillation" [B-V4-posttrain-opd]. RL compute, steps and any ratio: none
disclosed [B-V4-rl-compute]. Verdict: none.

## 5. DeepSeek-V4.1-Flash technical report (HF PDF)

Params: 552B backbone + 196B Engram; 8B active at prefill, 16B at decode [B-V41F-params, B-V41F-params-decode]. D: 45T
multimodal tokens at a fixed 100.6M-token batch [B-V41F-pretrain_tokens]. Post-training: SFT, then asynchronous RL,
then OPD from >40 teachers, "no algorithmic innovation" [B-V41F-posttrain-recipe, B-V41F-opd-teachers]. RL compute: only
"Cumulative RL steps" figure axes (ticks 500–2000) for agentic runs [B-V41F-rl-steps], with a qualitative scaling claim
[B-V41F-rl-scaling]. No GPU-h and no ratio. Verdict: framing only ("to elicit") [B-V41F-verdict].

## 6. Open-Reasoner-Zero (2503.24290v2)

| field | value |
|---|---|
| base | Qwen2.5-32B base (also 0.5B / 1.5B / 7B) [B-ORZ-base]; D = 18T (Qwen2.5 report) [B-QW25-pretrain_tokens] |
| RL | vanilla PPO, GAE λ=γ=1, no KL [B-ORZ-rl-algo, B-ORZ-kl]; critic: yes [B-ORZ-critic] |
| prompts | 57k [B-ORZ-train_prompts] (repo: 129k + 13k hard [B-ORZ-train_prompts-repo]) |
| steps | Fig. 2 axis 0–1000 [B-ORZ-steps-fig]; 32B: ≥1,100 steps + 100 annealing steps [B-ORZ-anneal, B-ORZ-anneal2]; "1/10 of the training steps" of R1-Zero-Qwen-32B [B-ORZ-steps-vs-r1]; repo default num_episodes 20 [B-ORZ-episodes-config] |
| prompts/step × group | 128 × 64 [B-ORZ-prompts_per_step] |
| max response | n.r. in paper; repo config generate_max_len 8000 ("TODO: change to larger later") [B-ORZ-max_resp_len-config]; prompt max 2048 [B-ORZ-prompt_len-config] |
| mean response | figure only, axis to 10k [B-ORZ-mean_resp_len-fig] |
| off-policy | strictly on-policy actor; critic takes 12 minibatch steps [B-ORZ-onpolicy] |
| GPUs | 32B on 16 nodes [B-ORZ-hardware-readme]; config: 32 actor/ref + 32 critic/reward GPUs + 16 vLLM engines × TP4 [B-ORZ-hardware-config]; GPU type n.r. (A800/H800 named only for 0.5B [B-ORZ-hardware-small]); GPU-h n.r. |
| verdict / k | none stated |

**Interp.** Fig. 2 response lengths near 10k exceed the repo's 8,000-token cap, so the repo default may not be the paper run.

## 7. Skywork-OR1 (2505.22312v2)

| field | value |
|---|---|
| base | DeepSeek-R1-Distill-Qwen-7B / -32B [B-SKY-base]. These are Qwen2.5-Math-7B / Qwen2.5-32B [B-R1D-7b, B-R1D-32b] SFT'd on 800k R1 samples [B-R1D-sft]. D = 18T [B-QW25-pretrain_tokens] (+ >1T math CPT for the 7B [B-QW25M-cpt_tokens]) |
| RL | MAGIC (modified GRPO) [B-SKY-rl-algo]; no KL [B-SKY-kl]; on-policy [B-SKY-onpolicy]; critic no |
| prompts | ~105K math + 13.7K code [B-SKY-train_prompts-math, B-SKY-train_prompts-code] |
| 32B schedule | steps 0–760: 16K, batch 256, group 16; steps 760–1130: 24K, batch 160, group 32 [B-SKY-32b-stage1, B-SKY-32b-stage2]; released at step 1000 [B-SKY-released-steps] |
| 7B schedule | 0–660: 16K, 256 × 16; 660–1320: 32K, 160 × 32 [B-SKY-7b-stage1, B-SKY-7b-stage2] |
| prompt length | 2048 (script) [B-SKY-script-prompt_len] |
| filtering | offline and online pass-rate filters; zero-advantage groups rejected; no over-generation stated [B-SKY-filter] |
| wall-clock | 32B: 309 h per 1000 steps (rollout 223 h) [B-SKY-wallclock-32b, B-SKY-wallclock-32b-caption]; GPU count for the final runs n.r. (script default 1 node × 8 [B-SKY-script-nodes]); ablations on 32 H800 [B-SKY-ablation-gpus] |
| mean response, verdict | n.r.; none stated (avg@32 only) |

## 8. POLARIS (HKU NLP blog + GitHub ChenxinAn-fdu/POLARIS + HF card)

| field | value |
|---|---|
| base | Qwen3-4B (post-trained) [B-POL-base-4b], itself strong-to-weak distilled [B-QW3-s2w-models]; D = 36T [B-QW3-pretrain_tokens]. 7B: DeepSeek-R1-Distill-Qwen-7B [B-POL-base-7b] |
| RL | GRPO-based [B-POL-algo]; no KL, no entropy loss, clip-high [B-POL-kl, B-POL-kl-script] |
| prompts | 4B: 30K; 7B: 53K [B-POL-train_prompts-4b, B-POL-train_prompts-7b] |
| prompts/step × group | 128 × 8 [B-POL-compute, B-POL-group_size] |
| max response (4B stages) | 39,936 / 48,128 / 52,224; prompt 1,024 [B-POL-max_resp_len-s1, -s2, -s3, B-POL-prompt_len] |
| steps | 4B/7B n.r.; 1.7B: 500 [B-POL-steps-1.7b]; blog mentions "800 steps" [B-POL-steps-fig] |
| over-generation | none: in-batch duplication of informative samples plus a rollout-rescue buffer [B-POL-dynamic] |
| GPUs | 4B: 10 days on 32 H800 (~0.33 h/step) [B-POL-compute] |
| verdict | none stated |

**Interp.** 10 days at ~0.33 h/step implies roughly 700+ steps (derived, not stated).

## 9. MiniMax-M1 (2506.13585v1) + MiniMax-Text-01 (2501.08313v1)

| field | value |
|---|---|
| params | 456B / 45.9B, 32 experts [B-M1-params, B-TXT01-params] |
| base D | Text-01: 7.2T + 3.2T + 1T (LR phases) [B-TXT01-pretrain-lr-phases, B-TXT01-pretrain-decay]; long context 300B + 32B + 26B [B-TXT01-longctx-128k/-512k/-1m]. M1 CPT: +7.5T (2.5T constant LR + 5T decay) [B-M1-cpt_tokens, B-M1-cpt_schedule] |
| base pretraining compute | n.r. (cluster of 1,500–2,500 H800 [B-TXT01-cluster]) |
| RL | CISPO + DAPO dynamic sampling and length penalty, no KL [B-M1-rl-algo]; critic no [B-M1-critic] |
| prompts | math ~50K, logic ~53K, code 30K, SWE several thousand, general 25K [B-M1-train_prompts-*] |
| steps | Fig. 4 axis 0–4000 [B-M1-steps-fig]; prompts/step, group size, epochs n.r. |
| max response | 40K (M1-40k); 80K run staged 40K→48K→…→80K [B-M1-max_resp_len, B-M1-length-stages] |
| mean response | eval lengths on AIME/LCB >20,000 tokens [B-M1-mean_resp_len]; training mean n.r. |
| GPUs | full RL: 512 H800 × 3 weeks, $534,700 [B-M1-rl-compute, B-M1-rl-compute-intro] |
| verdict | none stated |
| contamination | CPT mix 70% STEM/code/book/reasoning with "strictly avoiding" synthetic data [B-M1-cpt_mix, B-M1-cpt_nosynth]; long-CoT SFT before RL, source n.r. [B-M1-sft] |

## 10. Qwen3 (2505.09388v1)

| field | value |
|---|---|
| D | 36T [B-QW3-pretrain_tokens]: S1 >30T, S2 ~5T, S3 hundreds of billions [B-QW3-pretrain-s1, -s2, -s3]; trillions of synthetic tokens included [B-QW3-contam-synth] |
| params | flagship 235B / 22B [B-QW3-params-flagship] |
| reasoning RL | 3,995 query-verifier pairs, GRPO [B-QW3-rl-prompts]; "large batch size", many rollouts, off-policy (no numbers) [B-QW3-rl-batch]; 170 steps (235B-A22B) [B-QW3-rl-steps]; max/mean lengths, GPUs n.r. |
| general RL | 20+ tasks, no numbers [B-QW3-generalrl] |
| compute | 8B RL from an off-policy-distilled checkpoint: 17,920 GPU-h vs 1,800 for on-policy distillation [B-QW3-8b-rl-gpu_hours, B-QW3-8b-opd-gpu_hours, B-QW3-ratio_stated] |
| verdict | elicit-type evidence: "reinforcement learning does not lead to any improvement in pass@64 scores" (8B; AIME'24 90.0→90.0, AIME'25 83.3→83.3; k max 64) [B-QW3-verdict, B-QW3-kmax] |
| contamination | cold start on QwQ-32B outputs [B-QW3-coldstart]; small models strong-to-weak distilled [B-QW3-s2w-models] |

## 11. Kimi k1.5 (2501.12599v4)

No compute disclosure: no params, pretraining tokens or GPU-h [B-K15-pretrain]. RL context 128k with partial rollouts
[B-K15-rl-context]. Mirror-descent-style objective; reference = current policy each iteration [B-K15-ref-reset]; no
value function [B-K15-critic]. ~1M-example vanilla SFT [B-K15-sft]; synthetic cooldown data [B-K15-pretrain-cooldown].
Verdict: none.

## 12. ScaleRL (2510.13786v1, only version)

| field | value |
|---|---|
| models | 8B dense (unnamed, pretraining n.r.) and 17B×16 Llama-4 Scout [B-SRL-runs, B-SRL-base-scout]. Scout: ~40T tokens, 109B total / 17B active, 5.0M H100 GPU-h pre-training (Meta card) [B-L4-scout-tokens, B-L4-scout-params, B-L4-scout-gpu_hours, B-L4-gpu_hours-scope] |
| pre-RL SFT | 32B tokens, ~4 epochs, 32 H100 nodes, curated reasoning traces [B-SRL-sft] |
| compute | >400,000 GB200 GPU-h study [B-SRL-total-gpu_hours, B-SRL-hardware]; 80 GB200 per run (64 generators + 16 trainers) [B-SRL-gpus-per-run]; 8B 100k GPU-h / 7,400 steps; Scout 50k / 7,100 [B-SRL-runs, B-SRL-steps] |
| batch | default 48 prompts × 16 = 768 [B-SRL-batch]; largest 8B run "batch size of 2048 prompts" (ambiguous unit) [B-SRL-bs2048] |
| lengths | 14K generation (12K think + 2K answer), 32K variant; 16,384 sequence incl. 2,048 prompt [B-SRL-genlen, B-SRL-seqlen]; mean response n.r. |
| data / epochs | Polaris-53K (+ DeepCoder) [B-SRL-data]; "multiple epochs", count n.r. [B-SRL-epochs] |
| algorithm | PipelineRL (8-step off-policy), CISPO, FP32 logits, zero-variance filtering, No-Positive-Resampling [B-SRL-recipe, B-SRL-offpolicy, B-SRL-npr]; no KL [B-SRL-kl]; critic no |
| fits | sigmoid on mean@16 [B-SRL-fit-window]. ScaleRL A=0.610, B=1.92, C_mid=2542; 32k A=0.645; Scout A=0.710; bs2048 A=0.645 [B-SRL-fit-table-*]; ±0.02 [B-SRL-fit-variance]; 100k run fit B=1.70, A=0.645 [B-SRL-fit-100k] |
| claims | Scout beats 8B with 1/6 of the RL compute [B-SRL-scout-vs-8b]; design details mostly move efficiency, not the asymptote [B-SRL-asymptote-claim] |
| verdict | none (mean@16 only, no large-k pass@k) [B-SRL-validation]; pretraining-compute scaling laws left to future work [B-SRL-future-pretrain] |

## 13. Olmo 3 (2512.13961v2) + open-instruct RL-Zero scripts

| field | value |
|---|---|
| D | up to 5.9T pre-training + 100B mid-training + 50B (7B) / 100B (32B) long context [B-OL3-stages]; 7B 5.93T [B-OL3-7b-pretrain_tokens]; 32B truncated at 5.5T [B-OL3-32b-pretrain_tokens] |
| pre-training hardware | 7B: 512 H100 at 7.7K TPS/device; 32B: 1,024 H100 at 2.0K [B-OL3-7b-pretrain-throughput, B-OL3-32b-pretrain-throughput] |
| 32B wall-clock | ~56 days on 1,024 H100, $2.75M [B-OL3-32b-wallclock-total, B-OL3-32b-cost]. Pre-training ~47 days (5.5T phase 9.5 d on 512, then 35 d on 1,024) [B-OL3-32b-pretrain-days]; mid-training ~1.5 d [B-OL3-32b-midtrain-days]; post-training ~9 d [B-OL3-32b-posttrain-days]; final RL ~5 d [B-OL3-32b-rl-days]; 3.1 Think: +21 d on 224 GPUs [B-OL31-32b-rl-days] |
| RL (Table 49: 7B Think / 32B Think / 7B Instruct / 7B RL-Zero) | prompts 104,869 / 104,869 / 171,950 / 13,314 [B-OL3-rl-table-header]; steps 1,400 / 750 / 450 / 2,000 [B-OL3-rl-steps]; prompts/step 64 / 128 / 64 / 32 [B-OL3-rl-prompts]; group 8 [B-OL3-rl-group]; response 32,768 / 32,768 / 8,192 / 16,384 [B-OL3-rl-resp_len]; prompt 2,048 [B-OL3-rl-prompt_len]; learner + actor GPUs 16+56 / 64+160 / 8+56 / 8+64 [B-OL3-rl-learners]; asynchrony 1 / 8 / 8 / 8 [B-OL3-rl-async] |
| algorithm | OlmoRL (GRPO-based) [B-OL3-algo]; no KL [B-OL3-kl]; critic no; active sampling refills zero-advantage slots [B-OL3-active-sampling] |
| mean response | reasoner rollouts average >10K tokens (32K max) [B-OL3-rollout-len] |
| 7B Think RL wall-clock | ~15 d (old infra) / 6 d (new) [B-OL3-7b-think-rl-days] |
| RL-Zero scripts | d928a7c predates the file. 3.0 (3af17aacff): 16 × 16, 12,000 tokens, 512,000 episodes, 8 nodes, DAPO-17k + MATH-3000 [B-OL3rz-script0-*]. 3.1 (bb58c664fb): 32 × 8, 16,384 tokens, 768,000 episodes, 9 nodes, Olmo-3-1025-7B + Dolci-RLZero-Math [B-OL3rz-script1-*]. Changes stated in the paper [B-OL3-rlzero-31-changes] |
| verdict | RL-Zero math: pass@32 improves; "RLVR pushes the model beyond its initial capabilities" (AIME 2024/25, k max 32) [B-OL3-rlzero-verdict, B-OL3-rlzero-kmax]; spurious-reward control flat [B-OL3-rlzero-spurious] |
| contamination | mid-training includes reasoning traces, e.g. QwQ (1.87B tokens), "to lay the foundation" for RL-Zero [B-OL3-midtrain-traces, B-OL3-midtrain-traces-purpose]; Think SFT 45B tokens [B-OL3-think-sft-tokens] |

**Interp.** Table 49's caption says "GPU hours assume NVIDIA H100", but neither the HTML nor the PDF table has a GPU-hours
row. RL-Zero wall-clock is not stated; Fig. 38 plots GPU hours on a 0–30,000 axis [B-OL3-rlzero-vs-dapo].

## 14. Screening (item 12)

| paper | include? | key fields |
|---|---|---|
| AceReason-Nemotron 2505.16400v3 | yes (GPU-h only from a figure axis) | Base R1-Distill-Qwen-7B/14B [B-ACE-base] (Qwen2.5-Math-7B / Qwen2.5-14B [B-R1D-7b, B-R1D-14b]). 128 H100 [B-ACE-hardware]; batch 128, G 8 or 16, KL 0 [B-ACE-batch]; on-policy [B-ACE-onpolicy]; 8K→24K math, then 24K→32K code [B-ACE-schedule]; 49K math + 8,520 code prompts [B-ACE-train_prompts-math, -code]; Fig. 3(b) GPU-h axis 0.6–1.6×10⁴ [B-ACE-gpu_hours-fig]; mean length 4K→6.5K [B-ACE-resp-len]. **Verdict:** ~10% above the SFT model at all pass@k, k=1…1024, LCB v6 [B-ACE-verdict, B-ACE-kmax] |
| Phi-4-reasoning 2504.21318v1 | yes (bound: no wall-clock) | Phi-4 14B: ~10T + 250B mid-training [B-PHI4-params, B-PHI4-pretrain_tokens, B-PHI4-midtrain_tokens]. SFT 8.3B tokens on o3-mini traces [B-PHI4R-sft, B-PHI4R-contam]. GRPO on 32 H100, batch 64, G=8, KL 0.001, 32k [B-PHI4R-rl-config, B-PHI4R-max_len]; 90 steps [B-PHI4R-steps]; 72,401-prompt seed pool [B-PHI4R-rl-prompts] |
| Llama-Nemotron 2505.00949v5 | yes | LN-Ultra RL ~140k H100 h [B-LN-ultra-rl-gpu_hours] on 72×8 H100 [B-LN-ultra-rl-hardware]; 72 prompts × 16, batch 576, 2 updates per rollout [B-LN-ultra-rl-batch]; 24k context [B-LN-ultra-maxlen]; KD 65B + CPT 88B on a NAS of Llama-3.1-405B-Instruct [B-LN-ultra-kd-cpt]; Llama 3.1: ~15T tokens, 405B 30.84M H100 GPU-h [B-L31-tokens, B-L31-405b-gpu_hours]; R1-generated SFT [B-LN-contam-r1] |
| INTELLECT-2 2505.07291v1 | bound only | QwQ-32B base [B-I2-base, B-QWQ-base]; 256 × 16 = 4,096 samples per step [B-I2-batch]; 32K [B-I2-maxlen]; ~21–22 min/step [B-I2-steptime]; two weeks of runs, GPU count n.r. [B-I2-duration] |
| INTELLECT-3 (tech report PDF) | yes | GLM-4.5-Air-Base [B-I3-base] (106B/12B; GLM-4.5 23T [B-GLM45-params, B-GLM45-tokens]); SFT + RL on 512 H200 over two months incl. ablations [B-I3-compute-total]; RL 60×8 H200 [B-I3-rl-nodes]; ~1500 s/step [B-I3-steptime]; 256 × 16, 65,536 context [B-I3-batch]; step axis 0–600 [B-I3-steps-fig]; R1-0528 SFT traces [B-I3-sft-contam] |
| GLM-4.5 2508.06471v1 | no RL compute | 23T [B-GLM45-tokens]; single-stage 64K RL [B-GLM45-rl] |
| JustRL 2512.16649v1 | yes | 32 A800 × ~15 days per model [B-JRL-hardware]; 4,380 / 3,440 steps [B-JRL-steps-ds, B-JRL-steps-nem]; 256 × 8, 15k response [B-JRL-batch, B-JRL-group, B-JRL-maxlen]; no KL [B-JRL-kl]; DAPO-Math-17k [B-JRL-data]; token budgets 1.4e8 k / 1.1e8 k [B-JRL-token-budget-ds, -nem]; bases from Qwen2.5-Math-1.5B [B-R1D-1.5b, B-OMN-base] |
| Demystifying RL Post-Training 2608.24949v2 | no (toy runs, single A100/L40s [B-DMY-hardware]) | **Verdict:** pass@k-prior limits are "artifacts of the exploration bottleneck caused by sparse, binary reward functions" [B-DMY-verdict] |
| Apertus 1.5 2610.15542v1 | no (RL GPU-h excluded) | CPT GH200 GPU-h: ~225k (8B), 1.50M (70B), ~2M total; post-training excluded [B-APX15-cpt-gpu_hours, B-APX15-scope]; RL 480 / 180 steps [B-APX15-rl-steps] |
| Reflection Beam (blog, Oct 2026; weights on HF, report "coming") | yes (grade A) | 501B / 23B [B-BEAM-params]; 23.8T tokens [B-BEAM-pretrain_tokens]; pre-training <4 weeks on 6,144 GB300 [B-BEAM-pretrain-hardware]; RL 10.5K GB300 × 4 weeks, >100M rollouts, 256K context [B-BEAM-rl-hardware, B-BEAM-rl-intro]; ~1M environments [B-BEAM-envs]; no plateau (lab claim) [B-BEAM-rl-scaling]; HF card [B-BEAM-weights] |
| Lambert RLHF book 2504.12501v12 | secondary statements | R1 "about 5%" [B-RLHFB-ratio-r1]; Olmo 3.1 RL "4 weeks on 200 GPUs" [B-RLHFB-olmo31]; elicitation view [B-RLHFB-elicitation] |

## UNVERIFIED and caveats

- **Reflection CEO "more FLOPs on RL than pretraining"** (No Priors podcast, reported 9 Oct 2026): seen only in search
  snippets. The press page returned 403 (also via r.jina.ai) and no transcript was found, so this is not in the ledger.
  The blog's GPU × weeks figures for both stages are verified, grade A.
- The open-instruct commit d928a7c (2025-10-10) predates `scripts/train/olmo3/7b_rlzero_math.sh`; the file was first
  added in 3af17aacff (2025-11-20). Both later versions are recorded.
- MiniMax-M1's $534,700 "full RL" does not say whether it covers the 40k run, the 80k run or both.
- R1's 41K GPU-h scope (RL only, or RL plus SFT) is not stated.
- Skywork-OR1's 309 h has no GPU count.
- ScaleRL's 8B base is unnamed; its "2048 prompts" conflicts with the paper's completion-count batch convention.
