---
written_on: 2026-10-19
written_by: agent:claude
papers:
  - yueDoesReinforcementLearning2025
  - liuProRLProlongedReinforcement2025
  - guoDeepSeekR1IncentivizesReasoning2025
---

# How much RL do create-vs-elicit papers run, relative to pretraining? (run `rl-compute-share`, 2026-10-19)

This review extends `lit-review`, `lit-review-2` and `capabilities` and does not re-screen them.
- **Coverage.** Four parallel agents and I screened **96 sources**: 52 arXiv papers and 44 web posts or reports. That
  is above the brief's 30–45, because Q3 rests on many short lab statements. **13 were read in depth**
  ([`notes/`](notes/); Yue et al. in full).
- **Verification.** Every number has a verbatim quote in [`ledger/*.tsv`](ledger/).
  - `verify_ledger.py` finds 1,204 / 1,204 quotes in their fetched sources.
  - `check_quotes.py` finds 124 / 124 quotations in this file and the notes.
  - Both fail on altered controls. My check that the values match their quotes passed 41 / 41.

**Method.**
- **Pretraining** = 6·N·D, with N the active parameter count.
- **RL** = 2·N per generated token, plus 6·N per trained token, plus 2·N per extra forward pass (reference model or
  old policy), plus a critic where there is one.
- **N cancels** when RL runs on the pretrained model itself, so the ratio is a weighted token ratio.
- **Attention FLOPs are ignored**, which undercounts long-context RL by at most ≈ 2×.
- **Unreported mean lengths** are bounded by ¼–1 × the maximum or by a figure's axis range.

All rows are in [`compute_table.csv`](compute_table.csv), with observed values, estimates and interpretation in separate
columns; the plot is [`figures/ratio.pdf`](figures/ratio.pdf).

![RL / pretraining compute](figures/ratio.png)

## Bottom line

1. **Yue et al.'s RL is 7 × 10⁻⁶ to 3 × 10⁻² of pretraining FLOPs; the median is 1.2 × 10⁻⁴.** That is 3.4–4.2 orders
   of magnitude below the frontier's H2 2025–2026 central estimate (0.3–2), and 2–3 below 2024's (0.01–0.1).
2. **No create-vs-elicit test on a pretrained LLM exceeds 4.3 × 10⁻².** The largest open runs (ProRL + BroRL,
   MiniMax-M1, JustRL, Open-Reasoner-Zero, R1-Zero) sit near 10⁻², and most of them test nothing about creation.
3. **No frontier lab states its ratio.** The graded estimate is 0.01–0.1 in 2024 (C), 0.3–1 in H2 2025 (D) and ≈ 1–2
   in 2026 (D). Divide statements made in GPU-time by 5–8 to get FLOPs: that is the gap measured on R1-Zero, Olmo 3
   and our runs.
4. **Within studies, more RL plateaus or narrows large-k reach.** Creation, where found, follows how RL is allocated,
   not how much is run.
5. **Our runs spend 0.9–39× pretraining FLOPs on RL**, at or above the frontier band. There, more RL raised equal-k
   reach on theorems the base does not solve at k 256. But at 3–10× pretraining, RL did not bring a pattern removed
   from pretraining to the acquisition bar, although one seed's rare rediscovery grew slowly.

**Verdict: partly supported.** The papers test very small RL and cannot rule out creation at frontier scale, as Yue et
al. concede. But the scale evidence, ours included, does not favour creation emerging from more RL alone.

## Q1. Yue et al. in numbers

Yue evaluates nine third-party or baseline checkpoints and trains at least eleven runs of its own. RLOO, Reinforce++
and ReMax share the GRPO-150 row's volume.

| model (base, D) | RL run | RL / PT FLOPs |
|---|---|---|
| SimpleRL-Zoo Qwen2.5-7B/14B/32B, Llama-3.1-8B (18T; 15T) | ~100–150 steps × 1,024 × 8, max 8,192 | 4.6 × 10⁻⁵ – 1.1 × 10⁻³ |
| Oat-Zero-7B (Qwen2.5-Math, 19T) | 27 h × 8 A100 | 8 × 10⁻⁶ – 8 × 10⁻⁵ (GPU-hours) |
| DAPO-32B (18T) | 512 × 16, max 20,480; 312 or 5,000 rollout steps | 2.4 × 10⁻⁴ – 3.0 × 10⁻² |
| CodeR1-Zero-7B (Instruct-1M) | 832 × 16 × 16, max 4,096 | 2.4 × 10⁻⁵ – 9.7 × 10⁻⁵ |
| DeepCoder-14B (R1-Distill) | 32 H100 × 2.5 weeks, mean 8K → 17.5K tokens | 3.6 × 10⁻⁴ – 1.9 × 10⁻³ |
| Yue's VeRL runs, Qwen2.5-7B, 6 algorithms | 150–450 steps × 256 × 8; n = 32 for 220 steps | 1.1 × 10⁻⁵ – 2.0 × 10⁻⁴ |
| Yue's EasyR1 run, Qwen2.5-VL-7B | defaults assumed | 7 × 10⁻⁶ – 3 × 10⁻⁵ |
| Qwen2.5-Math-7B-Instruct (Fig. 7) | 66K queries × 32, steps assumed | 2.3 × 10⁻⁴ – 2.7 × 10⁻³ |
| Magistral-Medium | base size, steps, GPU-hours undisclosed | not computable |

- **DAPO's step count is ambiguous.** Its axis is captioned "gradient update steps" with 16 updates per rollout step;
  that reading caps it at 1.9 × 10⁻³ [A-DAPO-steps-unit, A-DAPO-minibatch].
- **Tokens and GPU-hours.** Rollout tokens are ≤ 5.5 × 10⁻² of D (median high bound 2.5 × 10⁻⁴). Four runs state
  216–13,440 GPU-hours; the only base with stated GPU-hours, Llama-3.1-8B, used 1.46M [A-LLAMA-gpu-hours].
- **Contamination.**
  - Qwen2.5 pretraining contains synthetic maths from Qwen2(-Math)-72B-Instruct [A-Q25-synth].
  - Code-R1, EasyR1 and Magistral start from instruct models.
  - DeepCoder starts from an R1 distillation [A-R1D-card].
- **Yue's own caveat.** "Whether this trend persists as more compute, such as pre-training scale budgets, is dedicated
  to RL training remains a critical question" [Y-yue-open-question]. Their near-frontier model, Magistral-Medium, shows
  "little or no improvement at higher k" [Y-yue-magistral-result].

## Q2. The wider literature

The 34 runs on pretrained LLMs, grouped by the verdict about each model (geometric midpoints; `analysis_out.txt`):

| verdict | n | median | examples (low – high) |
|---|---|---|---|
| elicit / narrows | 17 | 1.2 × 10⁻⁴ | Yue's models; spurious rewards 7 × 10⁻⁶ – 7 × 10⁻⁵; one-shot RLVR 1.3 – 6.6 × 10⁻⁴ |
| create / expands | 3 | 1.0 × 10⁻³ | f(g(x)) 1.4 × 10⁻⁵ – 1.4 × 10⁻⁴; Olmo 3 RL-Zero 4.6 × 10⁻⁴ – 2.3 × 10⁻³ (pass@32); AceReason-7B 7 × 10⁻⁴ – 2 × 10⁻² |
| mixed | 4 | 2.9 × 10⁻³ | ProRL v1 2.6 × 10⁻³ – 1.2 × 10⁻²; ProRL v2 + BroRL 1.0 – 4.3 × 10⁻²; NSR; GRPO-N |
| no test | 10 | 4.2 × 10⁻³ | MiniMax-M1 5 × 10⁻³ – 5 × 10⁻²; JustRL ≈ 10⁻²; ORZ-32B, R1-Zero 3 × 10⁻³ – 1.5 × 10⁻²; Skywork, Olmo 3 Think, INTELLECT-3, ScaleRL-Scout, Polaris, Phi-4 |

- **The verdict medians barely differ.** The create median is only 8.9× the elicit median, with n = 3. The largest
  recipes report pass@1 or avg@k only.
- **Interplay is the one paper whose RL reaches the frontier band.** It trains a 100M model from scratch, with RL at
  0.1–2× pretraining, stated in token equivalents [C-INTER-ratio_stated, C-INTER-budget_row_20].
  - In-distribution pass@128 never improves [C-INTER-verdict_id].
  - Out-of-distribution pass@128 at the edge of competence rises by up to 42–60 % [C-INTER-plus42].
- **Lab disclosures:**

  | lab | basis | RL / pretraining | claims |
  |---|---|---|---|
  | DeepSeek-R1 | GPU-hours | 1.5–5.3 % | B-R1-gpu_hours, B-V3-gpu_hours-table |
  | DeepSeek-V3.2 | cost of post-training | > 10 % | B-V32-ratio_stated-intro |
  | Llama-Nemotron-Ultra | GPU-hours | 0.45 % | B-LN-ultra-rl-gpu_hours, B-L31-405b-gpu_hours |
  | Olmo 3.1 Think 32B | GPU-hours | 14 % | B-OL31-32b-rl-days, B-OL3-32b-pretrain-days |
  | Reflection Beam (Oct 2026) | GPU-time | ≥ 1.7 | B-BEAM-rl-hardware, B-BEAM-pretrain-hardware |

## Q3. Frontier reference points (graded)

| date | source | statement | grade |
|---|---|---|---|
| 2024-09 | OpenAI, o1 | performance rises with RL train-time compute (no axis values) | A [D-oai-o1-rlscaling] |
| 2025-01 | Amodei | RL spend "small for all players"; "$1M instead of $0.1M" | A-informal [D-ant-amodei-rlsmall] |
| 2025-01 | Epoch (Erdil) | R1's RL ≈ 6.1 × 10²³ FLOP, ≈ 20 % of V3 | C [D-epoch-r1-rlflop] |
| 2025-04 | OpenAI, o3 | "an additional order of magnitude" of training compute via RL | A, relative [D-oai-o3-10x] |
| 2025-07 | xAI, Grok 4 | RL "at pretraining scale" on 200k GPUs | A [D-xai-grok4-ptscale] |
| 2025-10 | Epoch | GPT-5 RL assumed 10–200 % of pretraining; early 2025 1–10 % | C [D-epoch-gpt5notes-range] |
| 2025-12 | DeepSeek-V3.2 | post-training > 10 % of pre-training cost | B [B-V32-ratio_stated-intro] |
| 2026-02 | Cursor, Composer 1.5 | post-training exceeds the base's pretraining | A, not frontier [D-cursor-c15-ratio] |
| 2026-08 | OpenAI | "largest planned frontier RL run remains on hold" | A, qualitative [D-oai-pause-frontierrl] |
| 2026-10 | SemiAnalysis, fleet shares | post-training 42 % vs pretraining 23 % (1Q26) | D [D-oc-sa-posttrain] |

**Graded per-model range** ([`frontier_ranges.csv`](frontier_ranges.csv)):

| period | central | range | grade |
|---|---|---|---|
| 2024 | 0.01–0.1 | 0.003–0.3 | C |
| H1 2025 | 0.05–0.2 | 0.02–0.5 | C |
| H2 2025 | 0.3–1 | 0.1–2 | D |
| 2026 | 1–2 | 0.3–5 | D |

That is a rise of 1–2 orders of magnitude, roughly 10× per generation.

**Cautions.**
- **Units.** "Compute" in lab statements is unspecified, and GPU-time overstates RL's FLOP share 5–8×. R1-Zero is
  3.6 % by GPU-hours but 0.3–1.5 % by FLOPs. Beam's ≥ 1.7 means trainer-side GPU-time of ≥ 0.27–0.35 of pretraining
  [D-refl-beam-split].
- **Fleet shares** include experiments and inference.
- **Independent estimates can be far off.** Epoch's pre-disclosure R1 figure, computed "if the RL phase had a similar
  MFU to pretraining" [D-epoch-r1-rlflop], needs ≈ 490K H800-hours at V3's measured 1.2 × 10¹⁸ FLOP per GPU-hour.
  That is 5× the 101K DeepSeek later disclosed. Our token count (1.0–4.8 × 10²² FLOP) is 13–60× below Epoch's figure.

## Q4. Does the verdict depend on RL scale?

**For scale dependence:**
- ProRL's pass@128 gains are sustained on code and boxnet [C-PRORL-sustained].
- In Interplay, more RL helps on out-of-distribution hard problems [C-INTER-heavyrl].
- In Abdulsalam et al.'s from-scratch model, gains "emerge late" [C-ABD-late].
- Ours: going from 8 to 16 rounds raised group-C pass@256 from 0.049 to 0.265, i.e. 5 → 27 of 99 theorems that the
  end-of-pretraining base solves 0 of at k 256 (nd-rl `experiment-summaries/2026-10-03-rl-continue-cap12…`, Group C
  table).
- Knockout s1, continued from r16 to r24, went from 11 to 123 free-reductio proofs per round and from 5 to 9 strict
  training targets. Its held-out members stayed at the same 5 / 106 (`numbers.md` § create-or-elicit, Knockout s1
  r17–24).

**Against (the strongest):**
- **Invisible Leash re-tests the longest open RL at k 4,096–16,384.**
  - ProRL v1 gains 36 problems and loses 163. v2, 1,000 steps later, gains 48 and loses 175 [C-LEASH-prorlv1_row,
    C-LEASH-prorlv2_row].
  - ProRL's "no capability" boxnet base reaches 0.345 vs 0.492 [C-LEASH-boxnet16384].
- **Ring-Zero** (1T parameters, 3,600 steps): pass@1024 "increases during the initial phase of training but eventually
  plateaus" [C-RING-verdict].
- **Yue's 150 → 450 steps**: pass@256 falls from 66.3 to 64.3 while pass@1 rises [Y-yue-verl-step450].
- **Leash's DAPO checkpoints** are net negative on 5 of 6 benchmarks [C-LEASH-ckpt_5of6].
- **Qwen3**'s RL leaves pass@64 unchanged [B-QW3-verdict].
- **Our knockout** (3–10× pretraining): 0 / 6 seeds reach a family bar in 16 rounds, against 6 / 6 full seeds. Five
  wrote the free reductio only 1–34 times, against 17k–50k in the full arm. A 1 % dose restores acquisition
  (`numbers.md` § create-or-elicit).
- **Creation follows allocation, even at tiny RL:**
  - composition data: f(g(x)) at ≤ 1.4 × 10⁻⁴ [C-FGX-verdict];
  - negative samples [C-DEBATE-aime25_grpon];
  - rollout width [C-BRORL-revive];
  - pretraining seeds, since "RL cannot synthesize capabilities from a void" [C-INTER-seeds].
- **Spurious Rewards scopes itself** to "the compute scales of open-source post-training pipelines" [C-SPUR-verdict].

**Which normaliser?**
- **Trained tokens and FLOPs agree within 2–3×** for on-policy RL on the same model: the ratio is (generated +
  3·trained + extra passes) / 3D.
- **Gradient steps are not comparable**: samples per step run from 256 to 65,536.
- **GPU-hours** overstate the FLOP share 5–8×.
- **FLOPs overstate RL's information share by about 10³.** Policy gradient gets "O(1) bits per episode" [C-LORA-bits],
  so R1-Zero's 5.3M episodes carry ≈ 5.3M bits [C-LORA-r1zero_bits]. Updates are also KL-minimal [C-RAZOR-principle].
- **Exploration volume is separate from compute.** RL samples each training problem 2–2,400 times (median ≈ 100),
  while evaluations use k = 128–16,384.
- **Recommendation: report the FLOP ratio**, since it is N-free, convertible from GPU-time, and comparable with lab
  statements. Pair it with samples per training problem versus the evaluation k. For create-vs-elicit claims, add a
  base read at RL's compute: in `capability-defs` that cut RL's 51–60 equal-k "creations" per seed to 14–22.

## Q5. Where do our runs sit?

All our runs use `best_model.ALiBiGPT` 6 × 384, 9,560,832 params, `lean_staten`, trained from scratch.
- Stage 1: K12 (or cap 6), 4.4 × 10⁸ tokens, 2.5 × 10¹⁶ FLOP, 1,200 s on an A40.
- Then T1 expert-iteration ladders.
- Numbers from `our_runs.py`, which reads the five runs' registries and round files without modifying them.

| run | rounds | RL / PT FLOPs (RL-only, decoded – as run) | GPU-time ratio |
|---|---|---|---|
| trajectory / -cap6 | 8 | 1.5–2.9 / 0.9–2.0 | 12–14 / 9 |
| rl-continue / -cap6 (cumulative) | 16 | 3.3–6.3 / 2.3–4.8 | 29–30 / 22–26 |
| rl-from-ckpt, starts p16000 → p1600 | 8 | 2.2–4.3 → 18–39 | 20 → 152–182 |
| create-or-elicit full / dose1 / knockout | 16–24 | 3.2–6.4 / 3.1–6.2 / 3.1–9.7 | 33–54 |

Two costs inflate the as-run numbers:
- Each action re-reads the proof state, so prefill is ≈ 4.8× the decoded tokens in a sampled round.
- Each round replays 20,000 K12 records.

The low column therefore counts decoded tokens and the RL share of the fine-tune mix only. Even so, we sit at or above
the frontier band, ≈ 4–5.5 orders of magnitude above Yue's median. The model is tiny, but the hypothesis is about the
ratio.

## Verdict on the hypothesis: partly supported

**Supported.**
- Every create-vs-elicit study on a pretrained LLM runs RL at ≤ 4.3 × 10⁻² of pretraining FLOPs (Yue's median 10⁻⁴).
- The frontier has been ≥ 0.1 since H2 2025 (grade D).
- So the papers answer whether a small amount of RL creates, and the authors concede it.

**Weakened.**
- From 10⁻⁵ to 4 × 10⁻², the within-study trend is plateau or narrowing at large k.
- Existing creation results come from allocation at tiny RL.
- The one controlled test at or above frontier share, with the skill absent from pretraining (our knockout), finds
  "needs exposure".

The gap is real, but it is a missing measurement, not evidence that more RL creates.

## Implications for our project (ranked by value)

1. **Frame our results as large-RL-share results.** Our RL is 1–10× pretraining FLOPs, above the frontier band, and
   our "needs exposure" finding is the only controlled create-vs-elicit test in that regime.
2. **Measure the scale curve from existing reads.** Plot equal-k and large-k reach (group C, knockout members) against
   cumulative RL FLOPs per round; ladder rounds 1–24 span ≈ 0.2–10. A sub-round arm at ≈ 10⁻³ would test Dan's
   hypothesis directly.
3. **Report the RL-only ratio, and consider a no-replay arm.** Replay is continued pretraining (`rl-from-ckpt`).
4. **Pair every "RL created X" claim** with samples per target versus the evaluation k, and with a compute-matched base
   read (`capability-defs`).
5. **Quote the frontier as a graded range with units**, never as one number.

## Pre-registered expectations vs outcomes (`12753dbd`)

| # | expected | outcome |
|---|---|---|
| 1 | Yue median high < 10⁻³; SimpleRL-Zoo < 10⁻⁴; largest 10⁻³–5 × 10⁻² | median held (2.0 × 10⁻⁴); **SimpleRL-Zoo falsified** (to 1.1 × 10⁻³); DAPO 3.0 × 10⁻² held |
| 2 | ≥ 4 decades; no low ≥ 0.1; biggest open runs in 10⁻³–10⁻¹; create ≥ 10× elicit | **3.9 decades** (5.4 with Interplay); held for pretrained LLMs, but Interplay reaches 0.1; held except ScaleRL (6 × 10⁻⁴); **8.9×** |
| 3 | no absolute OpenAI / xAI figure; 2025–26 from ≥ 10⁻² to ≈ 1; 2024 ≤ 0.1 | held; **upper edge 2–5** (D); 2024 central held, range to 0.3 |
| 4 | none ≥ 0.1 at k ≥ 1,024; ProRL / BroRL at k ≤ 256; a ≥ 10⁻³ study narrows; ScaleRL tests no creation | held; ProRL held, **BroRL has no large-k test**; held; held |
| 5 | ours ≥ 0.1 (8 rounds), ≥ 1 (16+); ≥ 10× GPU-time | held, except trajectory-cap6 at 9× GPU-time |
| 6 | partly supported (60 %) | partly supported |
| 7 | FLOP headline, trained tokens second | FLOP headline; samples per problem and compute-matched reads second |

## Screened sources (96; in-depth reads in bold)

Full rows (type, grade, depth, claims, contribution): [`screened.md`](screened.md). Zotero list:
[`to_add_to_zotero.md`](to_add_to_zotero.md).

| Q | sources |
|---|---|
| Q1 (15) | **Yue 2504.13837v5**; **SimpleRL-Zoo 2503.18892v3**; Oat-Zero 2503.20783v2; **DAPO 2503.14476v2**; Code-R1 (GitHub); DeepCoder (blog); EasyR1 (GitHub); **Magistral 2506.10910v1**; Mistral Medium 3 (post); Qwen2.5-Math 2409.12122v1; Qwen2.5 2412.15115v2; Llama 3 2407.21783v3; Qwen2.5-VL 2502.13923v1; Qwen2.5-1M 2501.15383v1; **DeepSeek-R1 2501.12948v2 + Nature** |
| Q2 (42) | DeepSeek-V3 2412.19437v2, V3.2 2512.02556v1, V4 2606.19348v1, V4.1-Flash (report); ORZ 2503.24290v2; Skywork-OR1 2505.22312v2; POLARIS (blog); **MiniMax-M1 2506.13585v1**; MiniMax-01 2501.08313v1; Qwen3 2505.09388v1; Kimi k1.5 2501.12599v4; **ScaleRL 2510.13786v1**; **Olmo 3 2512.13961v2**; AceReason 2505.16400v3; Phi-4-reasoning 2504.21318v1; Phi-4 2412.08905v1; Llama-Nemotron 2505.00949v5; INTELLECT-2 2505.07291v1; INTELLECT-3 (report); GLM-4.5 2508.06471v1; JustRL 2512.16649v1; Demystifying RL 2608.24949v2; Apertus 1.5 2610.15542v1; Reflection Beam (blog); Lambert RLHF book 2504.12501v12; **ProRL 2505.24864v1**; ProRL v2 (NVIDIA blog, page); **BroRL 2510.01180v1**; **RL Squeezes 2509.21128v2**; **Invisible Leash 2507.14843v5**; NSR 2506.01347v2; f(g(x)) 2509.25123v3; Interplay 2512.07783v1; Debate 2510.04028v1; Echo Chamber 2504.07912v2; Spurious Rewards 2506.10947v2; one-shot RLVR 2504.20571v3; Tsilivis 2510.11495v2; Abdulsalam 2607.07646v1; Ring-Zero 2607.12395v2; overtraining 2606.15455v1 |
| Q3 (34; **frontier note**) | OpenAI: o1, o3, GPT-5 and RL-pause posts, Roberts talk; xAI: Grok 3, 4, 4.1; Anthropic: Amodei 2025 and 2026, Douglas & Bricken; Google: Gemini 2.5 2507.06261v6, Vinyals (press); Cursor: Composer 1.5; Epoch AI: 8 pieces; Ord: 2; Lambert: 3; SemiAnalysis: 2; Sutskever interview; press: Gigazine, The Decoder, Startup Fortune, OfficeChai |
| Q4 (5) | LoRA Without Regret (blog); RL's Razor 2509.04259v1; RL subnetworks 2505.11711v2; Path Not Taken 2511.08567v1; APRIL 2509.18521v3 |
