# Pre-registration: olmo-weights (Proposal 47). How much do Olmo 3's weights move at each stage of training?

Written 2026-11-25 (UTC) by the executor, before the first pod and before any weights were downloaded. Brief: nd-rl
`followups/BRIEF_olmo-weights.md`; proposal: nd-rl `docs/proposals/2026-11-24-olmo-weight-trajectory.md`.

## Question

Across every released checkpoint of Olmo 3, how much do the weights change between consecutive checkpoints? The
stages are pretraining (stage 1), mid-training (stage 2), long-context (stage 3), SFT, DPO and RL. Do the switches
between kinds of training show? Secondary questions:
- direction: distance from each stage's start, straightness, consecutive cosines;
- where the change happens: modules and layers;
- how much does not change in bf16;
- the timing against `olmo-ifcurve`'s IFBench curve;
- whether `olmo-ifladder`'s 16-example LoRA points where RL went;
- 7B RL from the base against RL from DPO.

This is descriptive. Weight distance is not behaviour; Proposal 48 measures behaviour.

## Models (all pretrained releases by AI2, bf16 safetensors; none trained here)

- **32B pipeline, 32.23 B parameters** (707 tensors in 14 shards):
  - `allenai/Olmo-3-1125-32B` (stages 1–3; `main` = the stage-3 merge);
  - `allenai/Olmo-3-32B-Think-SFT`;
  - `allenai/Olmo-3-32B-Think-DPO`;
  - `allenai/Olmo-3.1-32B-Think` (RL).
- **7B pipeline, 7.30 B parameters** (355 tensors in 3 shards):
  - `allenai/Olmo-3-1025-7B` (stages 1–3; `main` = `stage3-step11921`);
  - `allenai/Olmo-3-7B-Think-SFT`;
  - `allenai/Olmo-3-7B-Think-DPO`;
  - `allenai/Olmo-3-7B-Think` (RL);
  - `allenai/Olmo-3-7B-RL-Zero-{IF,Math,Code}` (RL from the base).
- **LoRA adapters:** `olmo-ifladder`'s `lora_main` and `lora_ctrl`. They are rank 16, α 32 (scale 2), on
  q/k/v/o/gate/up/down of all 64 layers of the 32B DPO model. sha256 values are in `artifacts/MANIFEST.jsonl`:
  `9921a760…` for main and `4cf06004…` for ctrl.

## The exact checkpoint list (committed with this file)

`olmo_weights/manifest/` holds the following, built by `list_refs.py`, `fetch_trees.py`, `hash_checks.py` and
`manifest.py` from the Hub API on 2026-11-25:
- `checkpoints.csv`: 453 checkpoints, each with its branch, **commit hash** and every shard's LFS sha256 and size;
- `jobs.json`: 13 jobs, 469 downloads, 15.17 TB;
- `stage1_locations.json`;
- `refs.json`;
- `hash_checks.json`.

Downloads are pinned to the commit hashes.

**Steps and learning rates:** `olmo_weights/steps_lr.md`, with sources (OLMo-core and open-instruct scripts at pinned
commits, and the Olmo 3 report, arXiv 2512.13961v2).

| | 32B | 7B |
|---|---|---|
| stage 1 | 25 locations as pairs (s, s + 1,000), plus step 0 and the final step: 49 checkpoints | 30 locations as pairs, plus 0 and the final step 1,413,814: 59 |
| stage 2 | ingredient 1: all 24; ingredient 2: every 4th (4,000 … 23,842; 6); the merge | all 49 regular branches |
| stage 3 | all 12, plus the merge (= base `main`) | all 13 (11,921 = base `main`) |
| SFT | all 22 (1e-4 and 5e-5 runs) | all 43, plus `main` |
| DPO | final | final |
| RL | all 46 (50 – 2,300) | all 55 (25 – 1,375), plus `main` |
| RL from the base | – | IF 19 + `main`, Math 19 + `main`, Code 29 (its `main` = `step_300` by hash) |

**Stage-1 locations.** The rule, in `manifest.py:stage1_locations`, was fixed before any download:
- **early:** targets 0 and 1,000 · 2^k up to 64,000, each mapped to the nearest released pair start in log distance;
- **even:** the remaining locations spread evenly over (64,000, last pair start], each rounded to the nearest pair start.

The resulting locations:
- **32B:** 0, 1,000, 5,000, 8,000, 16,000, 32,000, 64,000, 97,000, 130,000, 162,000, 195,000, 228,000, 261,000, 294,000,
  327,000, 359,000, 392,000, 425,000, 458,000, 491,000, 524,000, 556,000, 589,000, 622,000, 655,000. Steps 2,000–4,000
  and 38,000–43,000 have no released pairs.
- **7B:** 0, 1,000, 2,000, 4,000, 8,000, 16,000, 32,000, 64,000, 125,000, 187,000, 248,000, 309,000, 370,000, 432,000,
  493,000, 554,000, 615,000, 677,000, 738,000, 799,000, 861,000, 922,000, 983,000, 1,044,000, 1,106,000, 1,167,000,
  1,228,000, 1,289,000, 1,351,000, 1,412,000.

**Pre-computed cut lists** (`manifest.py --cut7 1 --cut32 1`, early targets ×4), used only if a cut is needed:
- 32B (12 locations): 0, 1,000, 5,000, 16,000, 64,000, 150,000, 233,000, 317,000, 402,000, 486,000, 571,000, 655,000;
- 7B (15 locations): 0, 1,000, 4,000, 16,000, 64,000, 199,000, 334,000, 468,000, 603,000, 738,000, 873,000, 1,008,000,
  1,142,000, 1,277,000, 1,412,000.

**Left out, with reasons:**
- `stage3-…-nooptim-reshard32`: byte-identical to the merge.
- The 7B branches `stage2-step47684-mix-*-from-2T-ckpt`: three ablation runs from a 2 T-token checkpoint, in another
  shard layout, not on the pipeline path.
- `allenai/Olmo-3-32B-Think`: see the hash checks.
- Each SFT or base `main` that is byte-identical to a branch.

## Hash checks (Hub LFS sha256, no download; `hash_checks.py` → `hash_checks.json`)

- **32B base `main`** = `stage3-step11921+11000+10000-nooptim` (= `-reshard32`).
- **7B base `main`** = `stage3-step11921`.
- **32B SFT `main`** = `5e-5-step8000`. The released SFT is the 5e-5 run at step 8,000.
- **`allenai/Olmo-3-32B-Think`**: all 15 checkpoints equal the 3.1 run's `step_0050`–`step_0750` (15 / 15), and its
  `main` = `step_0750`. They are skipped.
- **3.1 `main`** = `step_2300`.
- **Mains that equal no branch** (downloaded; their distance to the last branch is measured): 7B SFT, 7B Think,
  RL-Zero IF, RL-Zero Math, both DPOs.
- **Byte-identical branch pairs, almost certainly upload name collisions:**
  - RL-Zero-Code: `step_100` = `step_1000`, `step_200` = `step_2000`, and `main` = `step_300`;
  - RL-Zero-IF: `step_100` = `step_1000`.

  **Rule:** each duplicated checkpoint belongs at the step where its distance from base `main` fits the
  neighbouring checkpoints (distance from the start is close to monotone in RL). The other name is excluded and
  reported as a collision.
- **"Starts from the same base `main`"** cannot be settled by hash, because no step-0 checkpoint is released. It is
  tested by weights. The first SFT and each first RL-Zero checkpoint must be nearer to base `main` than to
  `stage3-step11000`. The first-interval change per step must not exceed 3× the second interval's, or the case is
  flagged.
- **Added weight tests:**
  - **DPO-32B start.** The Gram matrix of the 22 SFT checkpoints and DPO, offsets from `5e-5-step8000`, gives the
    best two-checkpoint linear soup of a 1e-4 and a 5e-5 checkpoint. This is compared with the released SFT `main`.
  - **Stage-3 start.** Distance of `stage3-step1000` to the stage-2 merge and to stage-1 656,000.
  - **Merge residuals.** The stage-2 merge against the mean of the two ingredient finals; the stage-3 merge against
    the best combination of steps 9,000–11,921.

## Statistics (computed on pods; only these leave them)

`olmo_weights/engine.py` runs one job at a time.

**Streaming.** It streams shard file by shard file:
- Every member's shard k is downloaded with `huggingface_hub` / `hf_xet` (`HF_XET_HIGH_PERFORMANCE=1`).
- Its sha256 is checked against the manifest.
- The file is deleted once every statistic that needs it is done.
- So a pod holds a few shard files per job, never whole checkpoints, except for pinned Gram sets.

**Arithmetic.** float32 from the bf16 values (differences are exact); sums in float64.

**Per tensor:**
- **Every chain interval a → b:**
  - ‖Δ‖², ‖θ_a‖², ‖θ_b‖² and numel;
  - the bitwise-equal count;
  - the count with |Δ| ≤ 1 ulp(θ_a), where ulp = 2^(e − 7) for bf16 exponent e (zero and subnormals: 2^−133);
  - ⟨Δ_i, Δ_{i−L}⟩ for lags L = 1, 2, 3 (lag 2 pairs consecutive stage-1 locations).
- **Against the stage start s:** ‖θ_i − θ_s‖², the equal and ≤ 1-ulp counts, and ⟨Δ_i, θ_{i−1} − θ_s⟩.
- **Gram sets:** offsets from the set's first member.
- **RL, 32B:** ⟨θ_t − θ_DPO, ΔW⟩ and ‖ΔW‖² for each of the 448 LoRA-targeted matrices, with ΔW = 2 · B·A for
  `lora_main` and `lora_ctrl`. Also 8 random rank-16 matrices per matrix (seeded by tensor name), Gaussian factors
  scaled to ‖ΔW_main‖.

**Aggregation (`olmo_weights/analyze.py`, on the VPS).** Overall sums over all parameters; by module (embeddings,
lm_head, q, k, v, o, gate, up, down, q_norm, k_norm, the two layer norms, final norm); by layer. Derived quantities:
- **Relative change:** r = ‖Δ‖ / ‖θ_a‖.
- **Per optimizer step:** r / n_steps, and also ÷ LR where the LR is known.
- **Distance from the stage start:** ‖θ_t − θ_s‖ / ‖θ_s‖.
- **Straightness:** S = ‖θ_end − θ_start‖ / Σ ‖Δ_i‖ over native-spacing checkpoints.
- **Cosines:** between consecutive changes.
- **Unchanged / ≤ 1-ulp / larger fractions.**

Figures 1–7 follow the brief. Figure 5 overlays `olmo_ifcurve/passk.csv` (group `all`, k = 1 and 8) and the
`F1_step` rug from `olmo_ifcurve/emergence.csv`.

## Expectations (written before the data; each is scored hit / miss)

**From the proposal.** Definitions are fixed here.
- **E1, size per step.** The median r / n_steps over RL's within-stage intervals is ≥ 10× smaller than over SFT's.
  - 32B: RL 50 → … → 2,300 (45 intervals) against the 5e-5 SFT run 1,000 → … → 10,790 (10 intervals).
  - 7B: RL 25 → … → 1,375 (54) against SFT 1,000 → … → 43,000 (42).
  - Hit if it holds in both families.
- **E2, totals.** ‖θ_RLlast − θ_DPO‖ / ‖θ_DPO‖ < ‖θ_SFTmain − θ_base‖ / ‖θ_base‖.
  - RL last: 32B `step_2300`; 7B `main` if it lies beyond `step_1375`, else `step_1375`.
  - Scored per family.
- **E3, unchanged.** Over all parameters, more than 50 % of weights satisfy |θ_RLlast − θ_DPO| ≤ 1 ulp(θ_DPO).
  Scored per family.
- **E4, direction.** S_RL > S_SFT. This uses the chains above, from the stage start (DPO; base `main`).
  - Native spacing is the score.
  - Also reported: RL subsampled by even index spacing to SFT's interval count.
  - Scored per family.
- **E5, the LoRA.** Over the 448 targeted matrices at step 2,300, cos(ΔW_main, θ_2300 − θ_DPO) > cos(ΔW_ctrl, ·).
  - Both are below 0.1 in absolute value.
  - cos_main exceeds the random baseline's mean by more than 3 of its standard deviations.

**My own guesses** (labelled as the executor's, scored the same way):
- **G1.** In 32B RL intervals (50 steps), more than 50 % of weights are bitwise unchanged. In 32B SFT intervals
  (1,000 steps), fewer than 10 % are.
- **G2.** Per-step change ÷ LR is at least 2× larger for RL than for SFT, in both families. Two reasons:
  - noise-dominated changes grow like √steps, which favours short intervals;
  - bf16 rounding inflates changes smaller than 1 ulp.
- **G3.** The stage 1 → 2 and stage 2 → 3 boundary intervals have a larger r / n_steps than the last within-stage
  interval before them, in both families.
- **G4.** Merges are averages:
  - ‖merge₂ − (i1_end + i2_end)/2‖ < 1 % of ‖i1_end − i2_end‖;
  - the stage-3 merge's best fit is equal weights on 10,000 / 11,000 / 11,921 (not 4 checkpoints), with a residual
    below 1 % of ‖merge₃ − s3_11921‖.
- **G5.** 32B DPO did not start from the released SFT `main`. The best 1e-4 + 5e-5 soup fits θ_DPO with a residual
  below 50 % of ‖θ_DPO − θ_SFTmain‖.
- **G6.** In 32B RL intervals, the embedding matrix's bitwise-unchanged fraction exceeds that of every MLP matrix
  type.
- **G7 (weak).** At step 1,000, each 7B RL-Zero run is farther from its start, relative to ‖θ_start‖, than 7B RL from
  DPO is from DPO.

## Noise floor, seeds, and the language-model standards

**Noise floor and seeds.** Every statistic is a deterministic function of released weights; nothing is sampled.
- The minimum detectable difference is set by arithmetic, not by sampling: float64 sums of exact float32 differences,
  better than 1e-6 relative. So the seed and noise-floor standard does not apply.
- The one random element is the rank-16 baseline: 8 draws, reported as mean ± sd.

**Language-model standards.** No text is generated or graded. So the hand gate, the template and decoding matching,
the token budgets, two-way confirmation and the prompt-overlap scan do not apply. Every number is labelled with its
checkpoint (repo, branch, commit).

## Compute, budget, stages, stop rule

- **Budget:** $50 / 120 pod-hours, registered with `podbudget` before the first pod. The balance floor is $35.
- **Stage 0 (≤ $3), one pod:**
  - an engine self-test on synthetic tensors against a naive numpy implementation, with positive controls (known
    equal / ulp counts) and a negative control (one altered tensor must change the counts);
  - hf_xet download throughput at 1 / 2 / 4 / 8 concurrent files;
  - sha256 rate;
  - statistics time on GPU and CPU for one 7B pair (stage-1 1,000 → 2,000) and one 32B pair (stage-1 0 → 1,000).
- **Re-cost after stage 0:**
  - projection = 15.17 TB ÷ measured rate × the billed rate × 1.3, plus disk;
  - if it exceeds $45, I pause and ask in `QUESTIONS.md`;
  - the default if unanswered is the brief's cut order, applied until the projection is ≤ $45: 7B stage 1 to 15,
    32B stage 1 to 12, drop 32B ingredient 2, drop RL-Zero-Code.
- **Pod class:** stage 0 runs on an RTX A4000-class GPU pod ($0.17–0.25/h listed, inside the proposal's
  $0.2–0.6/h CPU-pod range). It times both CPU and GPU statistics, and the cheaper per-TB option is used for the rest.
- **Main run:** several pods in parallel, one job at a time per pod. Statistics CSVs are pulled after every job.
- **Compute rows** (`record.py`), per job (`arm` = job id):
  - `gpu_seconds`, the job's pod-seconds with the GPU type and billed rate;
  - `gen_tokens` 0, `train_steps` 0, `train_tokens` 0, `lean_checks` 0;
  - bytes downloaded in a label.
- **Stop:** all jobs done, pulled and analysed; or the 48 h hard stop (2026-11-27 04:27 UTC); or $50.

**Deviations from the brief, declared now:**
- **Pod type.** A GPU pod is used if stage 0 shows it is no more expensive per TB, because the GPU computes the
  statistics.
- **Downloader.** hf_xet instead of hf_transfer: the repos are Xet-backed, and huggingface_hub 1.x dropped
  hf_transfer.
- **Disk.** Shard-major streaming keeps less than one checkpoint per job, instead of "the previous checkpoint".
- **Stage-2 and stage-3 counts.** 7B stage 2 has 49 branches, not 52; 32B stage 3 has 13, not 14 (reasons above).
- **Added tests.** The DPO-start, stage-3-start, merge-residual, duplicate-name and `main`-equality tests.
