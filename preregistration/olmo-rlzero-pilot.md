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
