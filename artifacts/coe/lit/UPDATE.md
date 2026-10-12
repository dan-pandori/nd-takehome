# Literature update for the create-or-elicit paper ("Did RL create it?"), 2026-10-12

Written by a sub-agent of the `create-or-elicit` executor. The brief asked for up to 12 papers in four buckets that are not
already covered:

- (a) pretraining-data ablation or dose-response before RL;
- (b) RL vs sharpening, power sampling or test-time-scaling nulls;
- (c) compute-matched or budget-aware pass@k comparisons of RL vs base sampling;
- (d) RL finding new compositions in theorem proving or formal math, with likelihood analyses.

"Already covered" means anything in nd-rl `docs/literature/` (2026-09-29 lit-review, 2026-10-02 lit-review-2,
2026-10-04 capabilities) or capability-defs `lit/`, plus the key papers named in the brief. 2025-07 or later was preferred.

**Method.**
- About 20 web searches. 21 candidates were opened: 14 full texts and 7 abstract pages. The DeepSeek-Prover-V1.5 abstract
  was also opened, for one fact check.
- I checked that none of the 12 selected papers appears in the local folders, by arXiv id and by title keyword.
- Texts were fetched from arXiv HTML at the version given, using capability-defs' `fetch.py` / `quote.py`. Copies of the
  scripts are in `/tmp/coe_lit`; the texts are in `~/coe_lit_sources/`, outside the repo.
- Every quote below was matched verbatim in that text. The match ignores case, runs of whitespace and dash style.
  Result: 12 / 12 verified, 0 UNVERIFIED.
- Where the HTML has LaTeX, the quote shows it in Unicode (π_α).
- "Our reading" marks inferences that the papers themselves do not make.

## Bottom line

1. **The most important implication: the power-sampling null must show that it actually samples p^α.**
   - Talwar, Nemeth & Moss (2610.13653, posted 9 Oct 2026) find that MCMC and SMC power samplers do not converge to π_α
     at realistic budgets. They behave as likelihood-guided search, and a likelihood-graded best-of-N reproduces most of
     their gains.
   - Yang, Sun & Ma (2608.14420) find that one fixed α applies a very different "dose" of sharpening to each problem.
   - Our base's exact sequence log-likelihoods make three checks cheap:
     - (i) show that the sampled log p shifts with α as π_α requires, or use exact importance resampling from a base pool
       at the matched token budget;
     - (ii) sweep α;
     - (iii) add a positive control: the same sampler should reach theorems that are elicited, i.e. rare but not
       negligible under the base.
   - Without these checks, "power sampling reaches none of the theorems RL creates" is a null for our sampler, not for
     sharpening.
   - The check matters because the null is close to guaranteed (our reading). Raising p to α > 1 removes mass from
     correct proofs whenever they are less likely than the base's wrong proofs (2603.08660's "confidence–correctness"
     condition). Importance resampling from a pool also cannot output a proof the pool lacks.
2. **The pretraining knockout is still new.** None of the 12 papers removes a single composition from pretraining. The
   nearest designs are:
   - chess models trained from scratch, which vary pretraining *scale*, not content (2607.16097);
   - a strategy knockout at the SFT stage on Qwen2.5-1.5B, where GRPO does not create the missing strategy (2606.13125);
   - a knockout from the *RL data* in Countdown, where GRPO does re-create the held-out pattern family (2512.01775);
   - a reasoning-data dose of 20 % of tokens at 8B scale (2510.03264).

   The two knockouts point in opposite directions. Neither reports the base likelihood of the knocked-out behaviour,
   which is the measurement our paper adds.
3. **Budget maps and confidence bands are becoming the standard for "created".**
   - Sun et al. (2609.01274) fit an exchange rate N_Base ≈ α·N_RL^β (β = 0.60 on Math500, 0 on AIME), but only up to
     16 samples.
   - Yang & Chen (2609.22547) find that visible pass@k crossovers are often not statistically established. They also
     find that base success rate alone does not determine what RL does to a prompt.
   - Our five allocations would read better as one curve per theorem (the base budget needed to match RL), with paired
     confidence bands on the "created" set.
4. **"Created" claims elsewhere rest on small k, or on the likelihood of the RL model's own outputs.**
   - Burton (2601.16172) attributes DeepSeek-Prover-V1.5's proving ability to RL because the base solves 0 / 244 at
     ≤ 64 samples. But 58.8 % of base outputs are `sorry` or echo the statement, and the Base→RL contrast also spans an
     SFT stage.
   - MaxRL (2602.02710) argues for creation from 15 RL-found solutions with high base perplexity. That is a lower bound
     on the base's success probability, not an upper bound.
   - MaxRL also offers an alternative account worth a sentence. Its maximum-likelihood gradient is "the average gradient
     from successful trajectories only", which is what expert iteration (EI) computes per theorem (our reading). It
     reports that this kind of training widens coverage where GRPO does not.

## Summary table

| # | arXiv id | title | first author, v1 date | bucket | bearing on our paper |
|---|---|---|---|---|---|
| 1 | 2607.16097v2 | Understanding Reasoning from Pretraining to Post-Training | Shen, 2026-07-17 | a, d | design to compare with |
| 2 | 2606.13125v1 | Select and Improve: Understanding the Mechanics of Post-Training for Reasoning | Krishnamurthy, 2026-06-11 | a | supports (expected knockout null) |
| 3 | 2510.03264v1 | Front-Loading Reasoning: The Synergy between Pretraining and Post-Training Data | Akter, 2025-09-26 | a | supports |
| 4 | 2512.01775v1 | How Does RL Post-training Induce Skill Composition? A Case Study on Countdown | Park, 2025-12-01 | d | complicates / design to compare with |
| 5 | 2610.13653v1 | A Critical Look at Power Sampling when Test Time Sharpening LLMs | Talwar, 2026-10-09 | b | complicates (sharpening null) |
| 6 | 2608.14420v1 | More Correct Mass, Worse Answers: Why Power Sampling Can Fail and How to Fix It | Yang, 2026-08-14 | b | complicates (sharpening null) |
| 7 | 2605.06241v3 | Rethinking RL for LLM Reasoning: It's Sparse Policy Selection, Not Capability Learning | Akgül, 2026-05-07 | b, d | alternative explanation (testable) |
| 8 | 2609.01274v1 | From Base Rollouts to RL Reasoning: A Budgeted Search Perspective | Sun, 2026-09-01 | c | supports / design to compare with |
| 9 | 2609.22547v2 | RLVR is a Kernel, Not a Function: Statistical Inference for pass@k Crossovers | Yang, 2026-09-18 | c | complicates (measurement) |
| 10 | 2601.16172v3 | Inference-Time Diversity in RL-Trained Lean Theorem Provers: A Diagnostic Study | Burton, 2026-01-22 | d | complicates the field's claims; supports our framing |
| 11 | 2602.02710v3 | Maximum Likelihood Reinforcement Learning | Tajwar, 2026-02-02 | d (likelihood) | alternative explanation / design to compare with |
| 12 | 2603.08660v1 | How Far Can Unsupervised RLVR Scale LLM Training? | He, 2026-03-09 | b | supports (logic of the null) |

## Papers

### 1. 2607.16097v2: Understanding Reasoning from Pretraining to Post-Training

**Paper.**
- Authors: Jingyan Shen, Ang Li, Salman Rahman, Yifan Sun, Micah Goldblum, Matus Telgarsky, Pavel Izmailov.
- Dates: v1 2026-07-17, v2 2026-08-09. Buckets (a), (d).

**Summary.**
- *Design.* Transformers of 5M–1B parameters are pretrained from scratch on human chess games (10 sizes, 11 compute
  budgets), fine-tuned (SFT) on synthetic reasoning traces, and trained with RL on puzzles with verifiable rewards. There
  are 36 pretraining–RL combinations.
- *Scaling.* Pretraining loss predicts post-RL pass@1 (ρ = −0.93 to −0.99, Fig. 3). The RL slope grows roughly linearly
  with log pretraining tokens. For larger models pass@16 stays nearly flat under RL, and more pretraining beats more RL.
- *Per-position analysis.* This uses a 50M model trained on 4.6B tokens.
  - A pure power transform of the SFT policy explains RL only moderately: global slope 0.99 → 1.13, R² 0.68 → 0.56
    from RL step 50 to step 750 (Table 13).
  - On hard puzzles, RL promotes correct moves from the "tail" (SFT probability < 0.05) into the top 3. It also
    amplifies wrong modes (§4.1, Table 14).

**Quote** (Abstract), verified: "RL does not simply sharpen the SFT policy: on easy puzzles it amplifies correct moves
the SFT policy already preferred, while on hard puzzles it surfaces correct moves that were nearly absent under SFT"

**Bearing: design to compare with.**
- This is the closest from-scratch organism with exact per-step likelihoods.
- Its "nearly absent" means p < 0.05 at one position, so a sampler finds the move in about 20 tries there. Every budget
  allocation in our paper would call that elicited.
- Its regression of centred RL log-probabilities on SFT log-probabilities is a cheap sharpening test we can run per
  proof step.

### 2. 2606.13125v1: Select and Improve: Understanding the Mechanics of Post-Training for Reasoning

**Paper.**
- Authors: Akshay Krishnamurthy, Audrey Huang, Nived Rajaraman.
- Date: 2026-06-11. Bucket (a).

**Summary.**
- *Design.* Qwen2.5-1.5B-Instruct (LoRA) is fine-tuned on a finite-field arithmetic task with relabelled symbols. The
  SFT solutions use forward-only (F), backward-only (B) or mixed (FB) strategies. GRPO then trains on harder 6–9-step
  problems, for 500–1,000 steps and 3 seeds.
- *Results (§3.1).*
  - F-only and B-only models improve only on the problem type their strategy suits ("The other problem type sees
    essentially no improvement in performance over RL training"). They plateau at about 60 % and about 50 %.
  - FB reaches ≥ 95 % on both types, by routing each problem to the right strategy.
- *Discussion (§4).* The authors report no setting in which RL induces a new reasoning capability.

**Quote** (§1 Introduction), verified: "strategy selection—the largest driver of performance in our experiments—requires
that the pre-training data contains reasoning patterns to select among; we do not observe novel patterns emerging
through reinforcement learning"

**Bearing: supports, and a design to compare with.**
- This is the expected null for our knockout. But the knockout is at the SFT stage of a pretrained LLM, and the paper
  gives no likelihood for the missing strategy.
- Our version is stricter: the composition is removed from pretraining, likelihoods are exact, and EI runs 16 rounds ×
  6 seeds.
- If σ is re-created in our knockout runs, that contradicts this paper's picture.

### 3. 2510.03264v1: Front-Loading Reasoning: The Synergy between Pretraining and Post-Training Data

**Paper.**
- Authors: Syeda Nahida Akter, Shrimai Prabhumoye, Eric Nyberg, Mostofa Patwary, Mohammad Shoeybi, Yejin Choi, Bryan
  Catanzaro.
- Date: 2025-09-26. Bucket (a).

**Summary.**
- *Design.* 8B hybrid Mamba–Transformer models are pretrained from scratch for 1T tokens, either without reasoning data
  or with 20 % of the mix taken from reasoning datasets of varying scale, diversity and quality. Each model then gets SFT
  and then GRPO.
- *Results.* Reasoning data in pretraining gives a lead that heavier SFT does not erase. After RL, the
  reasoning-pretrained model leads the baseline by 18.57 % on average and by 39.32 % on AIME (§4, Table 3).
- Metrics are average accuracies. There is no pass@k and no likelihood.

**Quote** (§4 Experiments and Results, RL phase), verified: "The most striking results appear on the highly challenging
AIME competition math problems, where the reasoning-pretrained models deliver a 39.32% improvement over the baseline."

**Bearing: supports.**
- It shows that pretraining content sets the post-RL ceiling at 8B scale.
- But the intervention is a bulk dose (20 % of tokens, many skills), not the removal of one composition. It cannot
  separate "RL could not create it" from "RL had less to amplify". Our single-σ knockout with likelihoods can.

### 4. 2512.01775v1: How Does RL Post-training Induce Skill Composition? A Case Study on Countdown

**Paper.**
- Authors: Simon Park, Simran Kaur, Sanjeev Arora.
- Date: 2025-12-01. Bucket (d).

**Summary.**
- *Design.* Qwen2.5 1.5B / 3B / 7B are trained with GRPO on Countdown with n = 3, 4 numbers. Solutions are parsed into
  canonical expression trees ("patterns").
- *Generalization (§4.1–4.3).* Models generalize to n = 5, 6 and to unseen tree shapes. They master shallow balanced
  trees before deep unbalanced ones; right-heavy trees are hardest.
- *Knockout (§4.4, Figs. 5, 24, 25: three runs of the 1.5B model).* A/B+C, every pattern containing it, and every
  pattern reducible to it are removed from the RL training set. The 1.5B model still learns to produce the whole
  held-out family.
- The text contains no likelihood or perplexity analysis.

**Quote** (§4.4), verified: "Qwen2.5-1.5B trained on this dataset successfully learns to generate the held-out
patterns despite zero training exposure"

**Bearing: complicates, and a design to compare with.**
- RL re-creates a held-out composition here. But "zero training exposure" means zero in the RL data only; Qwen's
  pretraining very likely contains such expressions.
- It is the precedent any positive knockout result of ours will be compared with. Removal from pretraining, plus base
  likelihoods, is what it lacks.

### 5. 2610.13653v1: A Critical Look at Power Sampling when Test Time Sharpening LLMs

**Paper.**
- Authors: Abiel Malkani Talwar, Christopher Nemeth, Henry Moss.
- Date: 2026-10-09. Bucket (b).

**Summary.**
- *Setting.* Qwen2.5-7B (Base, Instruct) and Phi-3.5-mini-Instruct, on MATH500 and GPQA Diamond.
- *Samplers fail to reach π_α (§3, Figs. 1–3).*
  - As α grows, MCMC chains stagnate and accept almost only higher-likelihood proposals.
  - In SMC, the effective sample size falls from 64 to ≈ 8 within 64 tokens, and the final particles share 6 prefixes.
  - The log-likelihoods of sampled sequences are insensitive to α.
- *Best-of-N baseline.* A best-of-N that keeps the top 4 of 16 partial sequences by log-probability every 64 tokens
  recovers most of the samplers' gains.
- *Power-RLOO (§4–5).* Fine-tuning the base to match π_α approximates the target far better. Its gains are noisy and
  specific to some models and tasks, and pass@k rises after modest fine-tuning.

**Quote** (Abstract), verified: "We show that these samplers fail to converge to π_α under realistic compute budgets,
and that their gains are largely recreated via simple Best-of-N with appropriate grading"

**Bearing: complicates the sharpening null.**
- A null run with an approximate sampler is a null for likelihood-guided search, not necessarily for p^α.
- With a 9.56M model and exact sequence log p, convergence is checkable: compare the sampled log p across α, or replace
  the sampler with exact importance resampling at matched tokens. We should report this check.
- The paper's conclusion, that power sampling extracts "sequences the base model already deems likely", also explains
  why a null on low-likelihood σ proofs is expected.

### 6. 2608.14420v1: More Correct Mass, Worse Answers: Why Power Sampling Can Fail and How to Fix It

**Paper.**
- Authors: Haohui Yang, Jiaxing Sun, Xiujun Ma.
- Date: 2026-08-14. Bucket (b).

**Summary.**
- *Finding.* Replacing base sampling with power sampling (α = 4) in 8-sample self-consistency lowers accuracy in 7 of 9
  model–benchmark settings, by up to 18.5 points, even though power sampling raises the mass on correct trajectories.
- *Two causes.*
  - Coverage mismatch: sharpening concentrates mass on a few dominant paths, so a high pass@k can coexist with lost
    support.
  - Dose mismatch: a fixed α changes some problems' distributions far more than others.
- *Repair.*
  - Raw likelihood is replaced by within-prompt rank, and gains are saturated at the top.
  - The repaired target is realized as importance-weighted aggregation over one shared base pool, at the same budget.

**Quote** (Abstract), verified: "Dose mismatch arises because a fixed exponent induces drastically different amounts of
distributional change across problems."

**Bearing: complicates the sharpening null.**
- One α is not one intervention. The null should be reported across an α sweep, or with α calibrated per theorem.
- Their same-budget importance weighting over a shared base pool is a matched-token implementation we can copy. Caveat:
  it cannot output a proof the pool lacks (our reading).

### 7. 2605.06241v3: Rethinking RL for LLM Reasoning: It's Sparse Policy Selection, Not Capability Learning

**Paper.**
- Authors: Ömer Faruk Akgül, Rajgopal Kannan, Willie Neiswanger, Viktor Prasanna.
- Dates: v1 2026-05-07, v3 2026-09-06. Buckets (b), (d).

**Summary.**
- *Design.* Public base/RL checkpoint pairs (GRPO, PPO and RLOO; several model families) are compared token by token.
- *Results (§3).*
  - RL changes the top token at only 1–3 % of positions, concentrated where base entropy is high.
  - The promoted token is always within the base's top 5, and is rank 2 on average.
  - Forcing RL's choice only at those positions recovers much of RL's gain; random edits do not.
- *ReasonMaxxer (§5).* An RL-free method applies a contrastive loss at entropy-gated positions, using a few hundred base
  rollouts. It matches or beats full RL across 3 families, 6 scales and 6 math benchmarks, at about 1,000× lower
  training cost.

**Quote** (Abstract), verified: "Only 1–3% of token positions are affected, the promoted token always lies within the
base model's top‑5 alternatives, and targeted corrections at those few positions causally recover a large fraction of
RL's accuracy gain, while random corrections fail."

**Bearing: an alternative explanation that we can test exactly.**
- In knockout-base EI runs that acquire σ, are the tokens of the first σ step inside the knockout base's top 5 at each
  position?
- If RL acquires a σ step outside the base's top k in a from-scratch organism, that is a counterexample to "selection,
  not acquisition".
- If the step is inside, the knockout result reads as selection.

### 8. 2609.01274v1: From Base Rollouts to RL Reasoning: A Budgeted Search Perspective

**Paper.**
- Authors: Wenhe Sun, Cunxiang Wang, Zijun Yao, Yixin Cao.
- Date: 2026-09-01. Bucket (c).

**Summary.**
- *Design.* Token sampling, beam-like, tree and sequence-level (MCMC-like) search over a frozen base are expressed as
  budgeted operating points. The question is whether an RL model's default pass@k curve (SimpleRL-Zoo pairs) can be
  matched by a low-complexity path of base operating points.
- *Results.* The fitted rule N_Base ≈ α·N_RL^β has β = 0.60 on Math500 and a floor β = 0 on AIME (§6.2). It transfers
  with these errors:
  - 3.41 pp on Qwen2.5-7B (95 % CI 2.32–5.53);
  - 3.28–4.87 pp on checkpoints added after fitting, across ten models from four families;
  - 5.03 pp on four benchmarks it was not fitted on.
- Budgets are 1, 2, 4, 8 and 16 samples (§4).

**Quote** (Abstract), verified: "These results support a qualified internalized-search reading: under the recipe we
test, much of the measured RL gain corresponds to a change in sampling efficiency, toward operating points the base
model can already reach under search."

**Bearing: supports, and a design to compare with.**
- A per-theorem exchange-rate curve would present our five budget allocations as one object.
- But their budgets stop at 16 samples, far below the budgets and ≈ 10⁻⁴ success probabilities where our
  created/elicited boundary sits. So they say nothing about the tail our paper is about.

### 9. 2609.22547v2: RLVR is a Kernel, Not a Function: Statistical Inference for pass@k Crossovers

**Paper.**
- Authors: Chen Yang, Jun Chen.
- Dates: v1 2026-09-18, v2 2026-09-25. Bucket (c).

**Summary.**
- *Method.* Paired confidence bands across k that require evidence of both an early RL gain and a later loss.
- *Crossings.* On five public RLVR/base pairs, no crossing is established in the initial evaluations. For example,
  ProRL's visible crossing at k = 56 has p = .20 at 1,000 prompts × 256 generations. A 32k-token evaluation on fresh
  prompts locates a crossing, with the first loss between 11 and 61 samples.
- *The kernel.* Prompts with equal base success rates have different post-RL success rates, and these differences repeat
  across independent halves of the generations. RL's effect is therefore a conditional distribution of post-RL success
  given base success (a kernel), not a single curve.
- *Power analysis.* It favours more prompts over more samples per prompt.

**Quote** (Abstract), verified: "Across five public RLVR pairs no crossing is statistically established in the initial
evaluations, while a 32k-token evaluation on fresh prompts locates a reversal with first loss between 11 and 61
samples"

**Bearing: complicates our measurement section.**
- Our created/elicited sets under each budget are point classifications.
- This paper argues for reporting them with paired uncertainty, and for showing the distribution of RL outcomes
  conditional on the likelihood-estimated base p rather than a threshold rule.

### 10. 2601.16172v3: Inference-Time Diversity in RL-Trained Lean Theorem Provers: A Diagnostic Study

**Paper.**
- Author: Zachary Burton.
- Dates: v1 2026-01-22, v3 2026-06-26. Bucket (d).

**Summary.**
- *RL plateau.* DeepSeek-Prover-V1.5-RL on miniF2F-test (temperature 0.6) solves 38 theorems at k = 16, 42 at k = 32
  and 42 at k = 64.
- *Skeletons.* Prefixing 15 fixed tactic skeletons raises the k = 16 count to 55 (mean +12.3 ± 4.2 over 3 seeds).
- *Base.* V1.5-Base solves 0 theorems with or without skeletons, at up to 64 attempts. 58.8 % of its outputs are
  `sorry`, and others echo the statement (§4.4).
- *Conclusion drawn.* The paper attributes proof capability to RL.
- *Other provers (§4.5).* RL-trained V2-7B gains 3 theorems that no i.i.d. baseline reaches. SFT-only Goedel-Prover
  loses 10.0 ± 4.4 with skeletons.

**Quote** (Abstract), verified: "V1.5-Base proves zero theorems regardless of intervention, identifying RL as the stage
that creates the proof capability which subsequently collapses"

**Bearing: complicates the field's claims, and supports our framing.**
- This formal-math "created by RL" claim rests on a 64-sample read of a base that mostly emits `sorry`, which is a
  format or propensity failure.
- The Base→RL contrast also spans V1.5's SFT stage. V1.5's own abstract (2408.08152) describes SFT followed by RLPAF,
  and this paper never mentions V1.5-SFT (our check).
- It is a worked example of why our design fixes the output format, has Lean judge both models, and brackets base
  success with likelihoods.

### 11. 2602.02710v3: Maximum Likelihood Reinforcement Learning

**Paper.**
- Authors: Fahim Tajwar, Guanning Zeng, Yueer Zhou, Yuda Song, Daman Arora, Yiding Jiang, Jeff Schneider, Ruslan
  Salakhutdinov, Haiwen Feng, Andrea Zanette.
- Dates: v1 2026-02-02, v3 2026-08-21. Bucket (d), with a likelihood analysis.

**Summary.**
- *Theory.* With a binary terminal reward, expected-reward RL is a first-order approximation to maximizing
  log p(success). MaxRL is a compute-indexed family of objectives that approaches maximum likelihood. Its gradient is the
  average score over successful samples only (§4: "the maximum likelihood gradient is the average gradient from
  successful trajectories only").
- *Main results.* MaxRL Pareto-dominates GRPO on pass@1 and pass@k, with up to 20× better test-time-scaling efficiency.
- *App. M.3.* With 4,096 samples per AIME 2025 problem:
  - Qwen3-4B-Base and its GRPO model each solve 23 / 30 problems; MaxRL solves 27 / 30, including 3 that neither of the
    others solves.
  - MaxRL's 15 correct rollouts on those 3 problems have high perplexity under the base and GRPO models.

**Quote** (Appendix M.3), verified: "Specifically, Fig. 31 shows that on the 3 problems from AIME 2025 that only our
MaxRL-trained checkpoint could solve, the 15 correct rollouts have very high perplexity under the base and GRPO trained
checkpoint."

**Bearing: an alternative explanation, and a design to compare with.**
- EI's update fine-tunes on each theorem's successful proofs. That is the success-averaged score MaxRL identifies as the
  maximum-likelihood gradient (our reading).
- So MaxRL predicts that EI widens coverage more than expected-reward RL does. That is an account of why EI "creates"
  that needs no exploration bonus.
- Their likelihood evidence is a weaker version of our bracket.
  - The perplexity of solutions the RL model found is only a *lower* bound on base success.
  - The upper side comes from the 4,096-sample base read: zero successes bound base p below about 7 × 10⁻⁴ at 95 % (our
    arithmetic).

### 12. 2603.08660v1: How Far Can Unsupervised RLVR Scale LLM Training?

**Paper.**
- Authors: Bingxiang He, Yuxin Zuo, Zeyuan Liu, Shangziqi Zhao, Zixuan Fu, Junlin Yang, Cheng Qian, Kaiyan Zhang,
  Yuchen Fan, Ganqu Cui, Xiusi Chen, Youbang Sun, Xingtai Lv, Xuekai Zhu, Li Sheng, Ran Li, Huan-ang Gao, Yuchen Zhang,
  Bowen Zhou, Zhiyuan Liu, Ning Ding.
- Date: 2026-03-09. Bucket (b).

**Summary.**
- *Taxonomy.* Label-free RLVR rewards are classified as intrinsic (majority vote, self-certainty, entropy) or external.
- *Theory.* Majority-vote training provably converges, geometrically, to the base distribution restricted to its initial
  majority answer (Theorem 1). The other intrinsic rewards reduce to the same sharpening (App. A).
- *Experiments.* On Qwen3-1.7B-Base with DAPO-17k, all five intrinsic rewards rise and then collapse. Even the most
  stable settings collapse around 1,000 steps (about 4 epochs). Per-problem analysis shows training amplifies existing
  preferences rather than correcting them.
- *External rewards.* An external self-verification reward shows preliminary sustained improvement.

**Quote** (Abstract), verified: "This sharpening mechanism succeeds when initial confidence aligns with correctness but
fails catastrophically when misaligned."

**Bearing: supports the logic of the null, and implies a positive control.**
- Sharpening, whether by training or by p^α sampling, helps only where the base's high-likelihood outputs are correct.
- σ-dependent theorems in knockout bases are, by construction, where they are not (our reading). So a null there is
  expected, and informative only beside a positive control where confidence and correctness do align.

## Screened, not included

Opened but not selected:

- 2603.22446v1, *Sparse but Critical* (Qwen Pilot Team, ICLR 2026). Inserting a few RL-sampled tokens into base
  generations recovers RL's gains (cross-sampling). Read in full; it overlaps #7.
- 2607.20543v1, *When RLVR Shrinks the Reasoning Boundary* (Zhou). Pass@k inversion on "boundary prompts", whose rare
  correct trajectories are too sparse for finite rollout groups. Read in full; it is about lost theorems, not created
  ones.
- 2606.09926v1 (EGPS) and 2602.10273v3 (Power-SMC). Faster power samplers (abstracts only); about samplers, not about
  RL.
- 2607.13389v1, *Where Should RL Post-Training Compute Go?* FLOP accounting for GRPO, with no comparison against the base
  (abstract).
- 2511.16231v1, *Pass@k Metric for RLVR*. The pass@k gradient is a reweighted pass@1 gradient (abstract).
- 2606.26050v1, *Natural Ungrokking*. Which rules survive pretraining is predicted by how often the corpus shows the rule
  winning (abstract). Pretraining only, but useful background on whether σ survives pretraining at low frequency.
- 2606.01861v1 (theory of self-play theorem proving) and 2606.29315v2 (experimentalist agents). Not relevant
  (abstracts).

Seen in search results but not opened:

- 2605.30327, 2609.12243 and 2605.02427: power-sampling variants.
- 2601.18795: PrefixRL, which is close to the already-covered POPE.
