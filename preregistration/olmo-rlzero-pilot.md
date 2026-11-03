# Pre-registration — olmo-rlzero-pilot (proposal 34)

Written 2026-11-03 01:05–01:20 UTC by the executor, before any pod (Part A committed 01:20:39 UTC, 255151cd). Brief: `nd-rl` proposal 34 (Dan, 2026-11-02, ≤ $50).
This file is committed in two parts, as the brief requires: **Part A** (this commit, before the first pod) fixes the
question, the definitions, the verdict rules and Stage 0. **Part B** (an addendum, committed after Stage 0's
throughput measurement and before any sampling on the evaluation set) fixes the sampling budget per checkpoint and the
numeric expectations for the evaluation set.

## Question

Along Olmo 3.1 7B RL-Zero-Math's RL trajectory (RLVR straight from the base, no SFT/DPO), does RL make problems
solvable that the base does not solve within a large sampling budget ("reach"), or does it only raise the probability
of solutions the base already produces ("elicitation")? Second deliverable: a measured cost per generated token and a
costed design for the same test on Olmo 3.1 Think 32B.

## Models, data, recipe (verified 2026-11-03 01:05–01:35 UTC)

- RL checkpoints `allenai/Olmo-3.1-7B-RL-Zero-Math`, branches `step_0100` … `step_2800` (28) and `main`. `main` is
  `step_2800`: the three safetensors shards have identical LFS sha256 (`c2cc7984cd63…`, `bc03dcc0a929…`,
  `cad83510bc38…`). 7.3 B parameters, bf16, `Olmo3ForCausalLM` (32 layers, 8 full-attention + 24 sliding-window
  4,096; 32 KV heads).
- Base `allenai/Olmo-3-1025-7B` `main` = `stage3-step11921` (identical shard sha256). Its weights are unchanged since
  before RL-Zero 3.1 was uploaded (revision `18b40a1e89`, 2025-12-03, has the same shards). The RL script loads
  `allenai/Olmo-3-1025-7B` with no revision, so the start is `main` — *assumed*; AI2's README says the launch specs used
  internal paths. Stage 0 checks it: step_0100 must be far closer in weight space to base `main` than to another base
  revision.
- RL data `allenai/Dolci-RL-Zero-Math-7B` @ `93b5e498`: 13,314 prompts, all with verifier `math`.
- Recipe: open-instruct `scripts/train/olmo3/7b_rlzero_math.sh` — the Olmo 3.1 recipe from PR #1261 (merge commit
  `bb58c664fb2d`, 2026-01-23; same flags on `main` `6b8e6ca1034`, 2026-11-02, apart from removed infrastructure flags):
  chat template `olmo_thinker_rlzero`, temperature 1.0, top_p 1.0 (`vllm_top_p` default), response length 16,384,
  no stop strings, 32 prompts × 8 samples per step, `total_episodes` 768,000 (3,000 steps), active sampling with
  `no_resampling_pass_rate` 0.875, lr 1e-6 constant, β = 0. open-instruct pinned vLLM 0.11.0 for RL; I sample with it.
- **What RL rewarded.** `MathVerifier` (boxed → Minerva → last `$…$` → whole output; `is_equiv` or
  `hendrycks_is_equiv`) on the response decoded with `skip_special_tokens=True`, run through `async_call` →
  `run_in_executor`, i.e. **off the main thread**. There `is_equiv`'s `signal`-based timeout raises, is caught, and
  returns False, so only string equivalence (`hendrycks_is_equiv`) can reward. Vendored as `olmo_pilot/oi_math_utils.py`
  + `olmo_pilot/grade.py` (unit-checked: `\boxed{\frac{2}{4}}` vs `\frac{1}{2}` is rejected in the RL mode and accepted
  in the main-thread mode). The verifier code is semantically identical at `70b0472` (2025-11-22), `bb58c66` and `6b8e6ca`.

## Definitions (fixed now)

- **Correct** = the RL-mode grade `rl` accepts the sample (primary; "what RL rewarded"). Reported beside it:
  `main` (same verifier with sympy live) and `ansline` (integer on the last `Answer:` line or in the last `\boxed{}`
  equals the answer; format-robust). Every answer in the evaluation set is an integer.
- **Evaluation set.** AIME 2024 I+II, AIME 2025 I+II, AIME 2026 I+II from MathArena (90 problems, all held after the
  Dec 2023 data cutoff). AIME 2023 (30 problems) is used **only** for Stage 0 and is never part of a reported
  evaluation number. Near-duplicates of RL training prompts (n-gram check, Part B) are excluded from the headline and
  reported.
- **Matched-k solved set** S_m(k): problems with ≥ 1 correct sample among model m's first k samples; expected sizes
  from unbiased pass@k (Chen et al.) per problem, with problem-bootstrap 95 % intervals.
- **Reach problem of checkpoint c**: ≥ 1 correct sample of c in its fixed budget, and **0** correct samples of the
  base in the base's whole budget on that problem (fixed phase + adaptive extension). **Reverse ("base-only")
  problem**: ≥ 1 correct base sample and 0 correct samples of c, with c given the same extension rule. Reach is
  reported both ways round, at matched k and at full budget, under `rl` and under `ansline`.
- **Strong reach**: a reach problem where c has ≥ 2 correct samples, the base has 0 `ansline`-correct samples too
  (so the base is not merely failing the answer format), the base budget on it is ≥ 512, and it is not flagged as
  contaminated.

## Verdict rules (at the budget Part B fixes)

- **"RL extended reach beyond the base"** if the final checkpoint has **≥ 3 strong-reach problems** and strong reach
  exceeds the reverse count (base-only problems of the final, under the same extension) by **≥ 2**.
- **"Elicitation only"** if the final checkpoint has **0 strong-reach problems**, or strong reach ≤ the reverse count,
  and the base's pass@k reaches the final's within the 95 % interval at the largest k measured for both.
- Anything else is reported as **inconclusive at this budget**, with the budget that would decide it.
- The likelihood check is descriptive: per correct reach solution, base log-likelihood per token vs the checkpoint's
  own, beside the same quantity on the base's own correct solutions and on the checkpoint's non-reach solutions.
  A reach solution counts as "in the base's support" if its base mean log-prob per token lies inside the
  2.5–97.5 % range of the base's own correct solutions on other problems.

## Stage 0 (≤ $3)

One A100-SXM4-80GB pod (community $1.39/h; fallback secure $1.79/h, or another ≥ 80 GB GPU), vLLM 0.11.0, bf16.
Base (`main`) and final (`step_2800`), **16 samples on each of the 30 AIME 2023 problems** at the RL settings; grade;
measure steady-state generated tokens/s, mean response length, the share cut at 16,384, and the likelihood-scoring
speed on a few correct solutions; compare step_0100 with base `main` and one other base revision in weight space.

**Expectations (Stage 0):**
- Steady-state throughput on one A100-80GB: **800–2,000 generated tokens/s** per checkpoint (KV-bandwidth bound: MHA
  with 32 KV heads costs ≈ 0.5 MB/token in full-attention layers + 1.5 GB per sequence in the windowed ones), i.e.
  **$0.2–0.6 per million generated tokens**.
- Mean response length on AIME 2023: final **4,000–10,000** tokens; base **1,500–6,000**. Cut at 16,384: final
  **2–15 %**, base **3–25 %**.
- AIME 2023 pass@1 (`rl`): base **2–12 %**, final **15–40 %**; pass@16: base **20–45 %**, final **35–65 %**.
- Format: on the base, **10–50 %** of `ansline`-correct samples fail `rl`; on the final, < 5 %.
- The brief's suggested design (k = 512 on base and final, k = 64 on 6 intermediates, base extension to 2,048) is
  projected at **> $150**, so I expect Part B to shrink it.
- step_0100's relative weight distance to base `main` is **< 10⁻³** and ≥ 10× smaller than to another base revision.

**Gate and stop rule.** Stage 0 stops at $3 whatever it has measured. From its measurement I re-cost the brief's
design and mine. If the design I would run projects above **$45** in total, I write a question in `QUESTIONS.md` with
the default of running the largest design that fits in $45, and proceed on that default. Whole-run hard stops: $50
spent (pods deleted by `pod_budget_watch`), 72 h, or the RunPod balance falling to $35.

---

# Part B — addendum after Stage 0 (committed before any sampling on the evaluation set)

## B1. Stage 0 results (AIME 2023 pilot; never an evaluation number)

One A100-SXM4-80GB (RunPod community, billed $1.39/h), vLLM 0.11.0, torch 2.8.0, bf16 weights and KV cache,
FLASH_ATTN; the RL settings (template `olmo_thinker_rlzero`, T 1.0, top_p 1.0, 16,384 tokens). Pod `orz-a`, created
01:21:38 UTC; Stage 0 ran 01:26–03:31:48 UTC; pod time from creation 2.17 h = **$3.02**. Files: `artifacts/olmo_pilot/{graded,meta,logs}/s0_*`.

| | base `main` | step_2800 |
|---|---|---|
| samples | 480 (16 × 30) | 60 (2 × 30; all finished before the 03:31 stop) |
| generated tokens / sample, mean (median) | 6,353 (4,206) | 12,249 (13,331) |
| cut at 16,384 | 17.5 % (84; none correct) | 21.7 % (13; 2 correct) |
| job-average throughput | 557 tok/s (91 min) | 472 tok/s (25 min; integrated from vLLM's log, the job was stopped before writing its meta file) |
| resident sequences in steady state | 17–27 (KV cache full) | 18–21 |
| pass@1 / pass@4 / pass@16 (`rl`) | 0.085 / 0.221 / 0.367 | 0.383 / pass@2 0.467 / — |

- **Price: $0.69 per million generated tokens** (base, job average; `meta/s0_base.json`), ≈ $1.0/M for step_2800's
  longer sequences. Throughput is KV-bound: with 32 KV heads every token costs 0.5 MB of cache across the 32 layers
  until a sequence passes the 4,096-token window (≈ 2.1 GiB per 5k-token sequence), so 80 GB holds ≈ 25 long
  sequences and each decode step re-reads ≈ 72 GB. Throughput per dollar then follows memory bandwidth per dollar,
  and the community A100 is the best NVIDIA class on RunPod (H100/H200/B200 within ≈ 10–15 %); MI300X would be
  ≈ 1.5× better but only a vLLM 0.10.2 ROCm image exists and 0.10.2 has no `Olmo3ForCausalLM`.
- Grades agree: `rl` vs `main` differ on 1 of 480 base samples, `rl` vs `ansline` on 4.
- **Against the Part A expectations:** throughput (expected 800–2,000 tok/s) and price (expected $0.2–0.6/M)
  were **wrong** — too optimistic by ≈ 1.5–2×; base mean length 6,353 is just above the expected 1,500–6,000; base
  cut 17.5 % inside 3–25 %; base pass@1 0.085 inside 2–12 %, pass@16 0.367 inside 20–45 %; the format expectation
  (10–50 % of the base's `ansline`-correct samples fail `rl`) was **wrong**: 2 of 41. step_2800: mean length 12,249 and cut 21.7 % are **above** the expected 4,000–10,000 and 2–15 % (wrong); pass@1 0.383 is inside 15–40 %; pass@16 was not measured. Both models are trained on most of AIME 2023 (21 of 30 in the RL data, 25 in midtraining), so these pass rates are not indicative of the evaluation set.
- Deviations from Part A's Stage 0: step_2800 was cut from 16 to 2 samples per problem and stopped at 03:31 (the $3
  rule) because the base job took 91 min, not ≈ 30; the likelihood-scoring test and the weight-distance check move into
  the main run (they need no new sampling).

## B2. Re-costing and the question to Dan

At these prices the brief's design (k = 512 on base and final, 6 × 64 intermediates, base extension to 2,048) is
≈ 1.2 × 10⁹ generated tokens ≈ **$1,000**; a fuller design (base 64, final 32, 4 intermediates × 16, extension to
1,024) ≈ $190. Both exceed $45, so per the brief I ask in `QUESTIONS.md` and proceed on the default below.

## B3. Default design (projected ≈ $43 including Stage 0)

- **Problems.** All 90 evaluation problems are sampled in phase F; the **headline set is 83**: 7 are excluded for
  contamination (`olmo_pilot/exclusions.csv`, decided 02:30 UTC before any evaluation sampling): aime2024_13
  (RL-data variant, 8-gram containment 0.71), aime2024_16 (midtraining `cranemath`, 1.00), aime2024_22 and aime2024_24
  (RL-data variants confirmed by reading, containment 0.40 / 0.31, IDF-weighted 5-gram 0.44 / 0.34), aime2024_27
  (midtraining OpenThoughts2 traces, 0.82), aime2024_28 (midtraining `megamatt`, 0.52), aime2026_01 (verbatim in both
  the RL data and the midtraining `general_reasoning_mix`, same answer). Rule: 8-gram containment ≥ 0.5 against
  `Dolci-RL-Zero-Math-7B` or the 14 math / reasoning / instruction subsets of `dolma3_dolmino_mix-100B-1025`
  (6,465 shards, 36.0 M documents scanned), or a variant confirmed by reading among IDF-weighted matches ≥ 0.3. Web
  and code subsets of the midtraining mix and the pretraining mix were not scanned.
- **Checkpoints.** base (`main` = `stage3-step11921`), RL `step_0100`, `step_0500`, `step_2800` (= `main`).
  100 → 500 → 2,800 is log-even (×5.3 per interval).
- **Speculative-decoding gate (before phase F).** vLLM n-gram prompt-lookup speculation is exact speculative
  sampling (it changes no output distribution in exact arithmetic) and should help most on the long repetitive
  samples. Test: base, AIME 2023 pilot, 8 × 30 samples, `num_speculative_tokens` 4, `prompt_lookup_max` 4, min 2.
  **Adopted for every model and phase iff** its job-average throughput is ≥ 1.25 × 557 tok/s **and** its pass@1 and
  mean length are each inside the 95 % problem-bootstrap interval of the Stage-0 difference test (i.e. the 95 %
  interval of (gate − Stage 0) contains 0). Otherwise all sampling is plain, as in Stage 0.
- **Phase F (fixed budget, all 90 problems, hard problems first):** base **16**, step_2800 **8**, step_0100 **8**,
  step_0500 **8** samples per problem. Matched k for every between-model comparison = **8**.
- **Phase C (confirmation, fresh samples):** for each headline reach candidate (≥ 1 `rl`-correct sample from any RL
  checkpoint in F, 0 from the base), the RL checkpoint(s) that solved it get **24 fresh samples** (step_2800 to 32;
  intermediates likewise), so that "c solves it" is not a winner's-curse selection.
- **Phase E (adaptive extension, headline problems):** reach candidates → the base, in chunks of 32, until the first
  `rl`-correct chunk or K total base samples; reverse candidates (base ≥ 1 in F, step_2800 0 in F) → step_2800
  likewise. **Pass 1: K = 128.** Pass 2 (K = 256) and pass 3 (K = 512) run, for all unresolved candidates at once,
  only if the projected total spend stays ≤ $45 (projection = spend so far + remaining samples × that model's mean
  failing length × measured $/token).
- **Phase P (compute-axis probe):** 64 seeded Dolci prompts (`olmo_pilot/probe_prompts.jsonl`) × 1 sample per
  checkpoint → mean response length on RL training prompts (low bound of the x-axis); the AIME means give the high
  bound (`olmo_pilot/compute_axis.py`; oversampling 1–3, extra forward 0–1).
- **Phase L (likelihood):** every `rl`-correct sample of an RL checkpoint on a reach problem (≤ 8 per problem and
  checkpoint) and controls (≤ 2 correct samples per problem: the base's own, and the checkpoint's on non-reach
  problems), teacher-forced under the base and under the generating checkpoint.

**Amendment to Part A.** Strong reach needs the base budget on the problem to be ≥ K*, the extension budget actually
reached (128, 256 or 512), instead of ≥ 512, and c's ≥ 2 correct samples to include ≥ 1 from the fresh
confirmation samples. "The largest k measured for both" in the elicitation rule is the matched-k = 8 comparison
plus, on the candidate problems, the extension budget.

## B4. Expectations (83 headline problems; `rl` grade unless stated)

- **Base:** pass@1 **0.03–0.08**; pass@8 **0.12–0.28**; pass@16 **0.18–0.35** (AIME 2023 is contaminated, so lower).
- **step_2800:** pass@1 **0.10–0.25**; pass@8 **0.25–0.50**. **step_0100** within ± 0.03 of the base's pass@1;
  **step_0500** between base and final.
- **Mean length:** step_2800 ≥ 1.4 × the base's; step_0100 within ± 20 % of the base's.
- **Reach of step_2800 at the full budget:** **2–8** problems after pass 1; strong reach **0–3**; reverse **1–5**.
- **Expected entries vs base at k = 8** grow with RL compute (step_0100 < step_0500 < step_2800), but the growth is
  within noise between 0500 and 2800 (≈ 60 %).
- **Likelihood:** ≥ 75 % of the reach solutions are "in the base's support" (Part A criterion); the base's mean
  log-prob per token on them is 0.05–0.3 nats below the generating checkpoint's.
- **Verdict:** "inconclusive at this budget" ≈ 55 %, "elicitation only" ≈ 30 %, "RL extended reach" ≈ 15 %.
- **Spend:** ≤ $45 total; the gate adopts speculative decoding (≈ 60 %).
