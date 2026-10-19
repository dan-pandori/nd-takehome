# R3: create-vs-elicit papers. RL compute and verdicts

Ledger `R3.tsv` has 334 rows. Every quote is a verbatim single-line substring of its source (checked by script). Numbers in parentheses are R3 row ids. n.r. = not reported. G = group size.

## A. Compute configuration

|run|base (D)|steps|prompts×G|max len|hardware / GPU-h|
|---|---|---|---|---|---|
|ProRL-v1|R1-Distill-Qwen-1.5B ← Qwen2.5-Math-1.5B: 18T + >1T math CPT + 800k R1 SFT (1,2,5–8)|~2,000 (12,13)|256×16; 32 in runs 6–7 (15–17)|8k; 16k for the last ~200 steps (19,20)|32 H100, ~16k GPU-h (28,29)|
|ProRL-v2|v1 checkpoint (40)|3,000 total (47)|512?×16 (48,49)|8K (51)|n.r. (57,58)|
|BroRL|ProRLv2 checkpoint (76)|+191 per paper, 419 per model card (83,84)|128×512 (85,86)|16,384 (88)|64 H100, 173.8 h (94,95)|
|BroRL control, N=16|same|+535 (101)|512×16 (102)|16,384|133.8 h (103)|
|RL Squeezes|released checkpoints only (105–107)|n.r. (108)|n.r.|n.r.|none (114)|
|Invisible Leash|released checkpoints (115); own DAPO run on R1-Distill-1.5B (123,124)|own run: 300 (125)|n.r. (126)|n.r.|n.r.|
|Negative RL|Qwen2.5-Math-7B (+Qwen3-4B, Llama-3.1-8B-Instruct) (132,135–138)|~120 from figure axis (142)|1,024×8 (143,144)|4,096 context (146)|8 H200 (153)|
|f(g(x))|Llama-3.1-8B-Instruct (pretrained, ~15T) + RFT (162,163,166)|~600 from figure axis (171)|16×16, 1 update/step (172–174)|8,192 (175)|n.r. (181,182)|
|Interplay|100M from scratch, 10B tokens (189,192)|200; App. A.10: 50–954 (197)|1,024×6 (198,199)|1,024 (201)|FLOP-equivalents only (208)|
|Two-stage|Qwen2.5-Math-7B (+Llama-3.2-3B) (219,222–224)|~42 from figure axis (228)|1,024×8 (229,230)|4,096 context (232)|4 A100 (238)|
|Echo Chamber|150M/1B from scratch, tokens n.r. (245,248)|10 epochs of GSM8K (252,253)|64×8 (254,255)|1,024 (257)|n.r.|
|Curriculum RL|5 bases (270)|n.r. (273)|n.r.|n.r.|n.r.|
|RL compositional|12-layer from scratch (278)|~20k iterations from figure axis (282)|?×4 (280)|256 (281)|4 H100 (283)|
|Diversity collapse|Qwen2.5-Math-7B (287)|140 (289)|1,024×8 (290,291)|3,072 (292)|4 H100 (293)|
|RL's Razor|Qwen2.5-3B-Instruct (297)|1 epoch (301)|8×64 (299,300)|n.r.|n.r.|
|Path Not Taken|3 bases (306)|150–320 (308–310)|256×12–16 (307)|8k–20k context (311)|8–32 H200|
|RL subnetworks|Qwen2.5-Math-7B, PRIME (314)|15 epochs (317,318)|64×4 (315,316)|n.r.|n.r.|
|RL after NTP|from-scratch models; Llama 3.2 3B (321,322)|n.r. (326)|1×32 (324,325)|n.r.|8 A100, 31–35 h per run (327)|

## B. Verdicts

|run|verdict|method (max k, equal k?)|scale_vary|
|---|---|---|---|
|ProRL-v1|create, task-dependent; math diminishes (31,32)|pass@128 from 256 samples, equal k (33,34)|base/intermediate/final: sustained on code and OOD, diminishes on math (35,36)|
|ProRL-v2|create (60); Invisible Leash measures net shrinkage, 48 gained vs 175 lost (61)|k n.r. (62)|0/2K/3K steps (63)|
|2507.12507|none: pass@1 only (73,74)|—|ablations only (75)|
|BroRL|not tested; theory leans create (97)|pass@1 only (98)|N=16 plateaus, N=512 keeps improving (99,104)|
|RL Squeezes|elicit (SFT expands) (109,110)|n=256 (111,112)|no (113)|
|Invisible Leash|elicit (117–119)|k≤8192 math, ≤16384 Reasoning Gym, equal k (120)|0–300 steps at k=256: boundary shrinks (129)|
|Negative RL|none stated; works by refining the prior (156–158)|k≤256, equal k (159)|partial (160)|
|f(g(x))|create (184)|k≈1000–1024 vs RFT base (185,186)|steps tracked at low k only (187)|
|Interplay|both (210–212,334)|pass@128, process-verified (213)|exposure, hard data, RL compute: more RL raises OOD-hard pass@128 (214–216)|
|Two-stage|both (241)|k≤256, equal k (242)|no, for the LLM (243)|
|Echo Chamber|elicit/amplify (266)|pass@64 (267)|pass@64 falls late in training (268)|
|Curriculum RL|create, via teacher; vanilla RLVR does not expand (274)|k≤256 (275)|3 rounds (276)|
|RL compositional|create (284)|base pass@1024 vs RL pass@16 (285)|rises through training (286)|
|Diversity collapse|both (294)|k≤256 (295)|epoch 5→20: pass@256 75.2→70.6, pass@1 flat (296)|
|RL's Razor / Path Not Taken / RL subnetworks|none (303,313,319)|no large k|no|
|RL after NTP|none; amplification (329)|greedy accuracy (330)|RL from different checkpoints (331)|

## C. Stated vs interpreted

Each run's values are stated in the source unless listed here.

- **Read from figure axes:** step counts in rows 142, 171, 228 and 282.
- **My derivations:**
  - ProRL-v1 epochs ≈ 3.8 (11).
  - BroRL GPU-h = wall-clock h × 64, i.e. ~11.1k and ~8.6k (95,103); over-generation ≈ 1.6× vs 2.4× (93).
  - Interplay: 102.4k unique prompts (195).
  - updates/step = batch ÷ mini-batch (145,200,231,290).
  - Echo Chamber ≈ 1,170 steps (253).
- **2507.12507:** same model as ProRL; it adds KL β = 1e-4 (66,67).

## UNVERIFIED / conflicts

- **Parameter counts:** exact values not in sources; only nominal sizes.
- **ProRL-v2 batch:** "512" comes from BroRL's Baseline row and may describe only the continuation. v2 GPU-h and k values are n.r.
- **ProRL-v1:**
  - Steps: 2,000 vs 2,500 (13,14).
  - Context: "16K" per the v2 blog vs 8k for most of training per the paper (21).
  - 2507.12507 claims "hundreds of thousands of steps" (69).
- **BroRL:** +191 steps (paper) vs 419 (model card) (84).
- **Invisible Leash:** which revision "ProRL-1.5B" refers to is unclear (333).
- **Interplay:** §5 equal-compute pairing contradicts Table 3 (217).
- **Batch units:** whether batch counts prompts or samples is unclear for ProRL (15) and Echo Chamber (256).
- **Not reported:** Invisible Leash DAPO configs, Curriculum RL's RL config and teacher model, Echo Chamber pretraining tokens.
- **Not looked up:** pretraining tokens for AceReason, Skywork, Phi4 and OLMo-2.
