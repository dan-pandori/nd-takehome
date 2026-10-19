# R1 summary (ledger `R1.tsv`, R1-1…R1-362)

Row numbers in parentheses; `[interp]` = my arithmetic; n.r. = not reported.

**DeepSeek-R1-Zero / R1** (base V3-Base: 671B/37B, 14.8T tokens; 2-5)
| field | R1-Zero | R1 |
|---|---|---|
| steps | 10,400 gradient steps, 1.6 epochs (17-20) | RL1 n.r.; RL2 1,700 (54) |
| batch | 32 questions × 16; 8,192-output rollouts, 16 minibatches, 1 epoch (21-23) | same (55-57) |
| length | 32,768 → 65,536 after step 8.2k (24) | 32,768 (58) |
| KL/critic | 0.001, reference reset every 400 steps / no critic (27-29) | same (60-61) |
| compute | 512 H800, 101K GPU-h, $202K (31-36) | 41K + 5K SFT-data GPU-h; $82K + $10K; total 147K / $294K (63-66) |
| verdict | elicit, framing only; pass@1 and cons@16 only (37-40) | same (67) |

V3 pretraining: 2,664K H800-h, $5.328M; all of V3 2,788K, $5.576M; excludes ablations (74-77).
*Interp:* R1-Zero RL = 3.8% of V3 pretraining GPU-h; R1 1.5%; program 5.5%. RL2 starts from V3-Base + 800K SFT, not the RL1 checkpoint (44-46).

**MiniMax-M1**
| field | value |
|---|---|
| base | Text-01 (456B/45.9B) + 7.5T CPT + SFT (78-83) |
| Text-01 tokens | no total: "7.2T", "remaining 3.2T", 1T decay, + 358B long-context (112-117) |
| algorithm | CISPO, no KL, dynamic sampling, 16 off-policy updates per batch (84, 95, 100, 102) |
| prompts | ~50K math, 53K logic, 30K code, several thousand SWE, 25K general (85-89) |
| steps/batch/G | n.r.; Fig. 4 axis 0–4000 steps (91-94) |
| length | 40K → 80K staged (96-98) |
| compute | 512 H800 × 3 weeks, $534,700 (103-105) |
| verdict | none (106) |

*Interp:* ≈258K GPU-h, ≈$2.07/h.

**Magistral**
| field | value |
|---|---|
| base | Medium: Mistral Medium 3 **Instruct** (118); Small: Small 3 Instruct 24B + Medium-trace SFT (145) |
| params/tokens | Medium undisclosed (120-122); Small 24B, tokens undisclosed (146-147) |
| batch | completions: 8k→4k→2k; Small 2,048 (129-130, 149) |
| updates/G/steps | 1 update per batch; G n.r.; steps n.r. (128, 131-132, 151) |
| length/KL | non-penalized 16k→32k; no KL (133-134, 150) |
| data/compute | 38k math + 35k code; compute n.r. (125-126, 137-139) |
| verdict | none (140, 153) |

**Qwen3**
| field | value |
|---|---|
| 235B-A22B | 36T (S1 >30T, S2 ~5T) (157-162) |
| reasoning RL | GRPO, 3,995 pairs, 170 steps; batch and rollouts unquantified; QwQ-32B cold start (156, 163-168) |
| compute | n.r. (172) |
| Qwen3-8B | RL 17,920 GPU-h vs distillation 1,800; RL pass@64 unchanged (90.0, 83.3) → **elicit** (178-182) |

**ScaleRL**
| field | value |
|---|---|
| bases | unnamed 8B dense (184); Llama-4 Scout 109B/17B, ~40T, 5.0M H100-h pretraining (185, 188-194) |
| compute | 8B 100k GB200-h, 7,400 steps; Scout 50k, 7,100 steps; study >400k (199-200, 215-217) |
| batch | default 48×16 = 768 completions per update; 100k run "2048 prompts", unit ambiguous (201-203) |
| length | 12,288 thinking + 2,048 answer (+2,048 prompt); 32k variant (207-209) |
| algorithm | CISPO, PipelineRL-8, no KL, zero-variance filter, drop prompts with pass rate ≥0.9 (195-196, 210, 212) |
| asymptote | A on mean@16 (held-out Polaris): 0.610 / 0.645 (bs2048) / 0.710 (Scout) (220-226) |
| verdict | none; no pass@k (219) |

*Interp:* 2,048 prompts × 7,400 steps ≈ 291 epochs over ~52K prompts; if 2,048 counts completions, ≈18.

**Olmo 3**
| field | value |
|---|---|
| RL-Zero base | Olmo-3-1025-7B: 5.93T + 100B mid + 50B long-context (228, 232-233) |
| RL-Zero config | 13,314 prompts, 2,000 steps, 32×8, 16,384 length, no KL (235-251) |
| RL-Zero compute | 8 learner + 64 actor H100; GPU-h n.r. (252-255) |
| verdict | **create**: pass@32 rises; k ≤ 32 (257-259) |
| contamination | midtraining traces from GPT-4.1 and o4-mini (261-263) |
| Think 32B | 750 steps (3.1: 2,300), 128×8, 32K length, 224 H100, ~5 days (+21 days) (264-276) |

*Interp:* Think RL ≈26.9K H100-h (+112.9K for 3.1); pretraining ≈977K (280).

**Kimi k1.5**: params, tokens, steps, batch, k, GPUs, cost undisclosed (284-299). Stated: 128k context, no value network (293, 295). Verdict: none (300).

**Ring-2.5-1T-Zero**
| field | value |
|---|---|
| base | Ling-2.5-1T-Base 1T/63B, no SFT; flash 104B/7.4B; tokens n.r. (304-309) |
| config | G=16; batch 512→256, minibatch 32 (unit unstated); length 4k→64k; KL 1e-4 in stage 1 (316-322) |
| steps/compute | 3,600 (1T), 5,200 (flash); 320 H200; GPU-h n.r. (313-315, 324-325) |
| verdict | **both**: AIME24 pass@1024 rises, then plateaus (≤2,000 steps) (327-332) |

**MiMo-V2.6**
| field | value |
|---|---|
| params/tokens | Pro 1.02T/42B, 30T; Flash 310B/15B, 48T (337-340) |
| RL | GRPO; 1,568×16 ≈ 25K sequences, 2.7–3.7B tokens per step; ~30 steps (read from figure) (342-347) |
| cost | Pro $2.6M, Flash $0.9M; basis and GPU type unstated (354-358) |
| verdict | none (359) |

## UNVERIFIED / ambiguous
- R1-Zero implies ≈208K unique prompts, but Table 4 lists 80–154K (8).
- R1's 41K: the text says both "4 days" and "80 hours"; unclear whether SFT is included (64).
- ScaleRL: batch unit, 8B identity, Scout batch unstated (184, 202-204).
- Text-01 total tokens: 8.2T or 11.4T (112).
- Ring-Zero batch unit (316).
- Olmo scripts disagree with Table 49 (244).
- Read only from figure axes: 25-26, 91, 254, 344.
