# Optimizer steps and learning rates per stage (olmo-weights)

Written 2026-11-25 before any weights were downloaded. Steps per interval come from the branch names in
`manifest/refs.json` (Hub API, 2026-11-25); everything else is cited. Sources, copied to `olmo_weights/sources/`:
- **OLMo-core** `src/scripts/official/OLMo3/*.py` and `src/olmo_core/optim/scheduler.py` at commit `3c1a108b`
  (`olmocore__*`);
- **OLMo-core SFT scripts** at the commits named in open-instruct's SFT scripts: `79a184cf` (32B, `OLMo-sft.py`) and
  `38f66526` (7B, `OLMo2-7B-sft.py`);
- **open-instruct** `scripts/train/olmo3/*.sh` at commit `fb18a8e8` (`oi__*`);
- **the Olmo 3 report**, arXiv 2512.13961v2 (PDF sha256 in `sources/olmo3_paper_sha256.txt`): Table 35 (base stages),
  Figs. 3–4 (stage-1 schedules), Table 47 (SFT), Table 48 (DPO), Table 49 (RL), §3.6 (stage-3 merge), §4.2 (SFT soup).

"Step" is one optimizer step. Stage-1 / 2 / 3 steps are global steps of that stage's run. SFT, DPO and RL steps count
from the start of that stage.

## Olmo 3 32B (32.23 B parameters, bf16)

| stage | steps (released checkpoints) | tokens / step | LR schedule | source |
|---|---|---|---|---|
| 1 pretraining | 0 – 656,000, every 1,000 (plus a few irregular saves) | 8,388,608 | linear warm-up 2,000 steps from 0 to 6e-4, then cosine to 10 % of peak over one epoch, stated as 5.93 T tokens (t_max ≈ 706,911 steps), truncated at 656,000 (5.5 T) | pretrain.py l. 42–44, 83; scheduler.py `CosWithWarmup` (alpha_f 0.1); report Table 35, Fig. 4 |
| 2 mid-training, each ingredient | 1,000 – 23,842, every 1,000 | 4,194,304 | 2.071e-4, no warm-up, linear to 0 at 23,842 (100 B tokens) | midtrain-ingredient-{1,2}.py l. 42–44, 84; Table 35 |
| 2 → 3 merge | 0 (not training) | – | average of the two ingredients' final checkpoints | model card; report §3.5 |
| 3 long-context | 1,000 – 11,921 | 8,388,608 | warm-up 200 steps to 2.071e-4, linear to 0 at 11,921 (100 B tokens) | long-context.py l. 41–44, 87; Table 35 |
| 3 merge (= base `main`) | 0 (not training) | – | merge of steps 10,000, 11,000 and 11,921 | report §3.6; branch name. The model card says "merged 4 final checkpoints". |
| SFT, two runs | 1,000 – 10,790, every 1,000; LR 1e-4 and 5e-5 | 4,194,304 | linear warm-up for 3 % of the run (≈ 324 steps), then linear to 0 at the end of 2 epochs (≈ 10,790) | OLMo-sft.py@79a184cf l. 441–443; 32b_think_sft.sh (lr, max_duration 2); Table 47 |
| SFT released `main` | = `5e-5-step8000` (by hash), LR there ≈ 1.33e-5 | | | `hash_checks.json` |
| DPO | one interval of ≈ 1,563 steps (200 K pairs, 1 epoch, batch 128) | | 7e-8, 10 % warm-up, linear decay; β = 5 | Table 48. Note that 32b_think_dpo.sh sweeps 7e-8 / 8e-8 / 9e-8 and starts from `32b-merge-configs/.../32b-1e-4-5e-5` |
| RL (Olmo 3.1 Think 32B) | 50 – 2,300, every 50 | – (64 or 128 prompts × 8) | 2e-6, constant; 1 minibatch, so 1 optimizer step per RL step | Table 49 (Olmo 3 Think 32B RL: 750 steps, 128 prompts); 32b_think_rl.sh (lr 2e-6, constant, 64 prompts) |

**Inconsistencies in the sources, as recorded:**
- **Stage-1 final LR.** The stated 32B schedule, a cosine over 5.93 T truncated at 656,000 steps, gives 6.69e-5 at the
  end. Fig. 4's caption says the real final LR is 6.210e-5, which would need t_max ≈ 683,000 steps (≈ 5.73 T). The
  overlay uses the stated schedule, and this note travels with it.
- **Stage-3 start.** The released long-context script loads `step656000` (the end of stage 1). The card and the report
  say long-context training started from the stage-2 merge. Job `b32_s3` measures both distances.
- **SFT soup.** The report (§4.2, Table 47) says the final 32B Think SFT is a mergekit soup of the 1e-4 and 5e-5
  runs, and the DPO script starts from a 1e-4 + 5e-5 merge. The Hub's SFT `main` is byte-identical to `5e-5-step8000`.
  Job `p32_sft` tests which weights DPO started from.

## Olmo 3 7B (7.30 B parameters, bf16)

| stage | steps (released checkpoints) | tokens / step | LR schedule | source |
|---|---|---|---|---|
| 1 pretraining | 0 – 1,413,814, every 1,000 (plus a few irregular saves) | 4,194,304 | warm-up 2,000 to 3e-4, then cosine over 5 T (t_max 1,192,092) up to step 597,046; from there the second half of a cosine stretched to end at one epoch (5.93 T = 1,413,814 steps) at 3e-5 | pretrain-1.py l. 40–42, 80, 99–102; pretrain-2.py l. 70–87; report Fig. 3, Table 35 (final 3.0e-5). pretrain-2.py's `max_duration` says 7 T, which would put the final LR at 3.93e-5; the report's 5.93 T matches the released last step exactly. |
| 2 mid-training | 1,000 – 47,684 | 2,097,152 | 2.074e-4 (script: 2.0712e-4), no warm-up, linear to 0 at 47,684 (100 B) | midtrain.py l. 40–43, 80; Table 35 |
| 3 long-context | 1,000 – 11,921 (= base `main`) | 4,194,304 | warm-up 200 to 2.074e-4, linear to 0 at 11,921 (50 B) | long-context.py l. 37–39, 81; Table 35 |
| SFT | 1,000 – 43,000, every 1,000; `main` matches no branch (tested by weights) | 1,048,576 | 5e-5, 3 % warm-up (≈ 1,299 steps), linear to 0 at the end of 2 epochs (45.4 B tokens ≈ 43,297 steps) | OLMo2-7B-sft.py@38f66526 l. 438–440; 7b_think_sft.sh; Table 47 |
| DPO | one interval of ≈ 1,172 steps (150 K pairs, 1 epoch, batch 128) | | 8e-8, 10 % warm-up, linear decay; β = 5 | Table 48; 7b_think_dpo.sh |
| RL (Olmo 3 7B Think) | 25 – 1,375, every 25; `main` matches no branch (Table 49: 1,400 steps) | – (64 prompts × 8) | 1e-6, constant, 1 minibatch | Table 49; 7b_think_rl.sh |
| RL-Zero IF / Math / Code (from base `main`) | 100 – 1,900 / 1,900 / 2,900, every 100 | – (32 prompts × 8) | 1e-6, constant, 1 minibatch | Table 49 (RL-Zero: 2,000 steps); 7b_rlzero_*.sh |

**Steps per interval** are the differences of the step numbers above. Interval types:
- **Boundary intervals.** From the last checkpoint of one stage to the first of the next. The step count is the
  first checkpoint's step in the new stage, for example 1,000 for stage 1 → stage 2.
- **Merges.** 0 training steps, drawn as hollow markers and left out of per-step rates.
- **SFT → DPO.** One interval of ≈ 1,563 (32B) / ≈ 1,172 (7B) steps.
- **DPO → RL.** 50 (32B) / 25 (7B) steps.
- **Stage 1.** Sampled as pairs (s, s + 1,000). The gaps between locations are counted in the sampled sequence's
  path length and labelled as such.
