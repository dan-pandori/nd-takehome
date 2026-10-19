# R2 summary: open reasoning-RL recipes (ledger R2.tsv, 424 rows)

P = prompts/step, G = responses/prompt, U = updates per rollout step, D = base pretraining tokens; (n) = R2 row ids; S: = stated, I: = my interpretation.

### Oat-Zero-7B (Dr. GRPO)
| Field | Value |
|---|---|
| base, D | Qwen2.5-Math-7B; 18T + >1T math-CPT corpus (1,5,7) |
| P×G, U, steps | 128×8; 1 PPO epoch, ~8 updates; steps not stated (12,14–17,11) |
| len, GPU | 3,000 resp; 27 h × 8 A100 = 216 A100-h (18,25) |
| verdict | elicit, qualitative; greedy accuracy only, no pass@k (27,29,31) |

I: U=8 from Oat code (train_batch_size counts responses).

### ORZ-32B
| Field | Value |
|---|---|
| base, D | Qwen2.5-32B base, 18T (41,45) |
| P×G, U, steps | 128×64; policy 1, critic 12; ≥1,100 + 100 annealing (56–59,53) |
| len, GPU | config 8,000 (TODO-flagged); 16 nodes, no hours (60,67) |
| verdict | none; avg@16 only (70,71) |

I: ~1,200 steps, ~128 GPUs; data 57k vs 129k ambiguous (49,50).

### Skywork-OR1-32B
| Field | Value |
|---|---|
| base, D | R1-Distill-Qwen-32B; 18T + 800k-sample distillation SFT (79,82,83) |
| P×G, U, steps | 256×16 (0–760, 16K), then 160×32 (760–1130, 24K); U=1; released at step 1000 (89–92,95) |
| GPU | 309 h wall-clock per 1,000 steps; GPU count not stated (105,106) |
| verdict | none; avg@32 (108,109) |

I: GPU-h not computable. 7B ablation baseline: 32 H800, 116 h/1,000 steps; line 799 says 64 H800 (116–118).

### Polaris-4B-Preview
| Field | Value |
|---|---|
| base, D | Qwen3-4B (post-trained, distilled), ~36T (120,124,149) |
| P×G, U, steps | 128×8; U=1; ~727 steps (I) (131–133,130) |
| len, GPU | 39,936 → 48,128 → 52,224; 10 d × 32 H800 = 7,680 H800-h (134–136,144) |
| verdict | none (146) |

I: steps = 240 h / 0.33 h.

### AceReason-Nemotron-14B
| Field | Value |
|---|---|
| base, D | R1-Distill-Qwen-14B; 18T + 800k SFT (153,156,157) |
| P×G, U | 128 × 8 (8K stage) or 16; U=1 (164–166) |
| steps, GPU | 7B math curves to ~3,500; 128 H100; final GPU-h not stated; 7B ablation axis 0.6–1.6×10⁴ H100-h (162,173,174) |
| verdict | both; pass@k up to k=64, and 1,024 on LCB v6 (176–178) |

I: pass@k only final RL vs SFT, not across steps (179).

### JustRL-DeepSeek-1.5B
| Field | Value |
|---|---|
| base, D | R1-Distill-Qwen-1.5B (Qwen2.5-Math-1.5B: 18T + >1T) (182,185,186) |
| P×G, U, steps | 256×8; mini-batch 64 → U=4 (I); 4,380 steps (190–193) |
| len, GPU | 15k resp; ~15 d × 32 A800 ≈ 11,500 A800-h (I) (194,201) |
| verdict | none (204) |

### 1-shot RLVR (Qwen2.5-Math-1.5B)
| Field | Value |
|---|---|
| P×G, U, steps | 128 copies of one example × 8; paper says 8 updates/step; 2,000 steps (220–222,219) |
| len, GPU | 3,072; 8 A100, hours not stated (223,229,230) |
| verdict | elicit; pass@8 max, falls after 200 steps for full set (232,234,235) |

### Spurious rewards (Qwen2.5-Math-7B)
| Field | Value |
|---|---|
| P×G, U, steps | 64×16; mini-batch 128 rollouts → U=8; 300 steps (248–250,247) |
| GPU | ~24 h × 8 A100 ≈ 192 A100-h per run (258) |
| verdict | elicit, model-dependent; pass@1 / avg@8 only (260–263) |

### INTELLECT-2 (QwQ-32B)
| Field | Value |
|---|---|
| base, D | QwQ-32B (32.5B; Qwen2.5-32B, 18T; SFT + RL already applied) (267,268,270,294) |
| P×G, U, steps | 256×16; 8 updates of 512; ~350 steps (277–279,276) |
| GPU | not stated; ~21 min/step; inference ≈ 4.5× training FLOPs (286–288) |
| verdict | none (291) |

### INTELLECT-3 (GLM-4.5-Air-Base, 106B/A12B)
| Field | Value |
|---|---|
| P×G, steps | 256×16, 65,536 context; ~600+ steps (Fig. 9) (300,383,301) |
| GPU | 60 nodes × 8 H200 at ~1,500 s/step → ~120k H200-h (I) (302,303) |

### Phi-4-reasoning-plus (RL stage)
| Field | Value |
|---|---|
| base, D | Phi-4-reasoning (o3-mini SFT); Phi-4 ~10T + 250B midtraining (306,309,310) |
| P×G, steps | 64×8; 90 steps (~6k prompts) (316,317,315) |
| len, GPU | 31k; 32 H100, hours not stated (319,325,326) |

### LN-Ultra (reasoning RL)
| Field | Value |
|---|---|
| base | 253B NAS derivative of Llama-3.1-405B-Instruct + 65B KD + 88B CPT; Llama pretraining D not stated (333,334,336,337) |
| P×G, U | 72×16; global batch 576 → 2 updates (342–344) |
| GPU | 72×8 H100; ~140k H100-h, RL only (351,352) |
| verdict | create (exceeds teacher); pass@1 only (354,355) |

APRIL (367–379): 32×8, 2× over-provisioning, 8 MI300/H100; no hours/steps. Demystifying (360–366): toy runs on one A100; verdict both (sparse elicits, dense creates); no compute.

## UNVERIFIED / caveats
- Oat `grad_acc_step` was not fetched; U≈8 is inferred (17).
- ORZ final data set (57k vs 129k), generation length (config 8,000 vs Fig. 2 axis to 10k) and GPU type.
- Skywork-OR1-32B GPU count; the Notion blog fetch was truncated.
- Polaris (and Skywork) verl KL-in-reward default: Polaris sets kl_coef=0.001 while the blog says no KL (139,140).
- verl mini-batch units vary by version; 1-shot RLVR's "8 updates" implies response-count semantics.
- "I:" GPU-hour figures assume the stated wall-clock is RL only.
