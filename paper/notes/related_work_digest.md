# Related-work digest for "Did RL create it?" (create-or-elicit paper)

Written 2026-10-13 by a sub-agent (agent:claude) from local files only. arXiv abstract pages were opened only to confirm
author lists and primary classes for `paper/refs.bib`. Every row below traces to a local note, review, claim ledger or
fetched source text; nothing here re-reads a paper. Companion file: `paper/refs.bib` (89 entries, one per row).

**Inputs read.** nd-rl lit reviews 1 (`2026-09-29`), 2 (`2026-10-02`) and 3 (`2026-10-04-capabilities`), with notes,
claim ledgers and screened tables; `artifacts/coe/lit/UPDATE.md` (12 newer papers) and its fetched texts; ledger section
K (L67–L72), whose caveats are binding here; the `create-or-elicit` review's §Verdict (it takes precedence over the
ledger for this run's own numbers).

**Path abbreviations** (line numbers are as of 2026-10-13):

| tag | path |
|---|---|
| LR1 | `/home/dan/nd-rl/docs/literature/2026-09-29-lit-review/` |
| LR2 | `/home/dan/nd-rl/docs/literature/2026-10-02-lit-review-2/` |
| CAP | `/home/dan/nd-rl/docs/literature/2026-10-04-capabilities/` |
| UPD | `/home/dan/work/create-or-elicit-paper/artifacts/coe/lit/UPDATE.md` |
| CDS | `/home/dan/cd_sources/` (fetched arXiv texts used by lit review 3) |
| COES | `/home/dan/coe_lit_sources/` (fetched arXiv texts used by UPD) |
| LEDGER | `/home/dan/work/create-or-elicit-paper/claims_ledger.md` |
| REV | `/home/dan/work/create-or-elicit-paper/review_create-or-elicit.md` |

**Verification marks.**
- **V-ledger**: marked V (verbatim at the stated location) in a review's claim ledger (LR2 `claims.md`; CAP
  `_claims_L*.md`). LR2's reviewer re-verified 106 / 106 checkable rows; CAP's re-verified 48 / 48 sampled rows.
- **V-recheck**: in LR1's executor re-check table (`LR1/REVIEW.md` §d, l.200–234). Some rows there paraphrase.
- **V-upd**: matched verbatim in the fetched text by UPD's agent (UPD l.20–21).
- **src**: I found the quote at that line of the local fetched text during this run.
- **note-quote**: a quotation inside an LR1 note. LR1's per-agent ledgers are not in the local folders; LR1's reviewer
  verified 43 / 43 checked claims, but these particular quotes were not re-checked here.
- **abstract**: the notes cover the abstract only.

**Section labels** (our paper): Intro; RW-a … RW-g (themes of §2 below); Setup; Meas (budgets, k-to-solve, estimator,
certification); Ctrl (RL-free controls and the power-sampling null); Res (knockout results); TTC (test-time compute);
Disc; Lim.

---

## 1. Per-paper table (89 papers)

Each paper appears once, under its main theme; the "§" column lists every section where it is useful.

### 1a. Does RL expand what the base can do? (RL vs base in pretrained LLMs)

| key | id / venue | short title | what it claims | strongest verified quote (location) | relation | § | flags |
|---|---|---|---|---|---|---|---|
| yue2025doesrl | arXiv 2504.13837v5 | Does RL Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model? | RLVR wins at small k, but bases overtake RLVR models as k grows (to 1,024 on AIME24); base-unsolved, RL-solved problems are 0.0 % (AIME24, k 1,024) and 1.0 % (MATH500, k 128). RL outputs lie in the lower-perplexity part of the base's own samples. | "base models consistently surpass RLVR models across all benchmarks and LLM families as $k$ increases" — `LR2/claims.md:10` (V-ledger); `CDS/2504.13837v5.txt:100` (src); LEDGER L67 | contrasts (equal k, no compute matching, unknown pretraining); we extend its Fig. 6 to per-theorem likelihoods | Intro, RW-a, Meas | L67 caveat binding: equal k ≤ 1,024, no compute matching. The likelihood evidence rests on 2 problems × 16 responses (`LR2/claims.md:14`) |
| liu2025prorl | arXiv 2505.24864v1 | ProRL | Prolonged RL (> 2k steps, KL penalty, reference resets) solves tasks where the base fails at every k tried. Gains are largest where the base is weakest. | "including scenarios where base models fail entirely regardless of the number of attempts" — `LR2/claims.md:16` (V-ledger) | contrasts | RW-a, Disc | Boundary read at k 128 only, no likelihoods, no seeds reported (`LR2/notes/liu2025-prorl.md:24-25`); base "struggles with formatting" (`LR2/claims.md:19`) |
| hu2025brorl | arXiv 2510.01180v1 | BroRL | Raising rollouts per prompt to hundreds revives ProRL models that had plateaued. | "BroRL revives models saturated after 3K ProRL training steps and demonstrates robust, continuous improvement" — `LR2/claims.md:38` (V-ledger) | contrasts (a caution: our EI is 16 rounds × k 32) | Lim | abstract |
| yao2025twostage | arXiv 2510.04028v1 | The Debate on RLVR Reasoning Capability Boundary | Early RL can shrink the reasoning boundary; prolonged training can expand it. | "over-exploitation during the exploitation stage may lead to capability boundary shrinkage, whereas prolonged training into the exploration stage can promote an expansion" — `LR2/claims.md:39` (V-ledger) | contrasts (caution on our 16 rounds) | Lim | abstract |
| wu2025invisibleleash | arXiv 2507.14843v4 | The Invisible Leash | Accounts for support preserved, expanded or shrunk by RLVR at k up to 16,384; states the unseen-in-k bound. | "SRR ≈ 0.93–0.99", "NDR ≤ 0.04" (§4.2) and (1 − p)^k ≤ ζ (App. C.4) — `LR1/REVIEW.md:216-217` (V-recheck) | tool (zero-success bound behind certification) | RW-a, RW-e, Meas | No in-depth note (method + Table 1 read, `LR1/REVIEW.md:277`); SRR / NDR are not defined in the local notes |
| wen2025cotpassk | arXiv 2506.14245v2 | RLVR Implicitly Incentivizes Correct Reasoning in Base LLMs | With CoT-Pass@K (answer and reasoning both checked), RLVR extends the reasoning boundary. | "RLVR can extend the reasoning boundary for both mathematical and coding tasks" — `LR2/claims.md:31` (V-ledger) | tool (Lean makes our pass@k a CoT-pass@k, `LR2/REVIEW.md:96`) | Meas | abstract |
| shao2025spurious | arXiv 2506.10947v2 | Spurious Rewards | Random rewards nearly match true rewards on Qwen2.5-Math-7B; the effect depends on the model. | "improves MATH-500 performance for Qwen2.5-Math-7B by 21.4 percentage points using randomly assigned rewards, nearly matching the 29.1-point gain" — `LR2/claims.md:35` (V-ledger) | agrees (motivates controlled pretraining) | Intro, RW-a | abstract |
| wu2025contamination | arXiv 2507.10532v3 | Reasoning or Memorization? | Contamination makes LLM RL results unreliable; on a clean synthetic generator only accurate rewards lift performance past the base. | "only accurate reward signals yield steady improvements that surpass the base model's performance boundary in mathematical reasoning" — `LR2/claims.md:37` (V-ledger) | agrees (clean generator) | RW-a | abstract |
| he2025unlikely | arXiv 2506.02355v2 | Rewarding the Unlikely | In GRPO on a Lean prover, low-probability correct proofs are rarely uplifted, so gains fade at large N. A rank penalty on likely correct samples lifts pass@N up to N 512. | "GRPO substantially boosts pass@1 to pass@16, but the improvement diminishes for larger N" — `LR1/notes/he2025-rewarding-unlikely.md:12` (note-quote); numbers `LR1/REVIEW.md:212-213` (V-recheck) | extends (EI analogue of rank bias) / contrasts | RW-a, RW-f | Its intro claim of "substantially outperforming standard expert iteration" has no EI experiment (note l.22): do not cite it for EI. N ≤ 512; solvable-only training set |
| zhu2025nsr | arXiv 2506.01347v2 | The Surprising Effectiveness of Negative Reinforcement | RLVR splits into positive- and negative-sample terms; negative-only training keeps base pass@256, positive-only lowers it (MATH 91.2 vs base 96.9). | NSR "suppress[es] incorrect generations and redistribut[es] probability mass toward other plausible candidates, guided by the model's prior beliefs" — `LR1/notes/zhu2025-negative-reinforcement.md:19` (note-quote); table at l.15 | contrasts (EI is pure positive reinforcement, note l.28, our reading) | RW-a, Disc | Large-k gains over base only on AIME25 (30 problems); seeds not checked |
| chen2025passktraining | arXiv 2508.10751v1 | Pass@k Training | A closed-form pass@k group advantage shifts RL effort to harder prompts and raises pass@k. | "Pass@k Training focuses on optimizing harder problems." — `LR1/notes/chen2025-passk-training.md:16` (note-quote); Enigmata 12.9/21.3 → 17.9/29.8 `LR1/REVIEW.md:214` (V-recheck) | contrasts (no gradient when every attempt fails, note l.23, our reading) | RW-a | "pass@k" means k ≤ 8 (≤ 32 on Maze) |
| walder2025pkpo | arXiv 2505.15201v5 | Pass@K Policy Optimization | An unbiased pass@k reward transform for any k ≤ n; ARC cumulative training solve rate 12 → 84 % (Gemma2-9B). | "our transformations are the first to enable robust optimization of the pass@k for any arbitrary k ≤ n" — `LR1/notes/walder2025-pkpo.md:12` (note-quote) | contrasts (zero reward when no sample succeeds, note l.19) | RW-a | k_eval ≤ 16 |
| tuyls2025repexp | arXiv 2510.11686v2 | Representation-Based Exploration for LMs | An elliptical bonus on pretrained hidden states preserves large-k pass@k and yields responses less likely under the base; weak models do not benefit. | "responses from RepExp tend to be less likely under the base model" — `LR2/claims.md:67` (V-ledger); "weaker models (e.g., Qwen-2.5-0.5B) experience no benefit or even degradation" — l.64 | contrasts (needs a pretrained prior, `LR2/notes/tuyls2025-representation-exploration.md:24`) | RW-a, RW-c | Lower base likelihood is not zero support (note l.23) |
| qu2026pope | arXiv 2601.18779v1 | POPE | On hard problems on-policy RL sees no correct rollout, and entropy, clipping or pass@k objectives do not fix it; oracle-solution prefixes do, and transfer back unguided. | "On hard problems, on-policy RL rarely explores even a single correct rollout, yielding zero reward and no learning signal" — `LR2/claims.md:73` (V-ledger) | agrees (σ is rare in knockout bases) | RW-a, Disc | partial read (abstract + 2 sections) |
| yuan2025fgx | arXiv 2509.25123v3 | From f(x) and g(x) to f(g(x)) | RL on depth-2 compositions of known string functions generalises to depths 3–6; iterative RFT on the same data does not. | RFT on Level 3 "never surpasses 2.6 %" — `LR1/REVIEW.md:222` (V-recheck) | contrasts (their RFT, close to our EI, fails to compose; our EI acquires σ only with exposure) | RW-a, RW-b | Pretrained Llama-3.1-8B-Instruct; seeds not reported (`LR1/notes/fgx-rl-composition-2025.md:17`) |
| qin2025decomposing | arXiv 2505.22756v1 | What "Math" Does RL Teach? | GRPO mainly improves execution on problems the model can already solve ("temperature distillation"); at K 64 it solves no new test problems. | "on the test set, GRPO fails to solve any new problems" — `CAP/_claims_L1.md:132` (V-ledger); `CDS/2505.22756.txt:145` (src) | agrees (elicitation at small K) | RW-a | No in-depth note (sections read, 5 / 5 claims V); "coverage wall" measured at K 64 |
| sun2026budgeted | arXiv 2609.01274v1 | From Base Rollouts to RL Reasoning | Much of RL's pass@k gain matches base search operating points; fitted exchange rate N_Base ≈ α·N_RL^β (β 0.60 Math500, 0 AIME). | "much of the measured RL gain corresponds to a change in sampling efficiency, toward operating points the base model can already reach under search" — `UPD:287-289` (V-upd); `COES/2609.01274.txt:68` (src) | agrees / we extend (per-theorem budgets at 10⁴–10⁶ attempts) | RW-a, RW-e, TTC | Budgets stop at 16 samples (`UPD:293`) |
| yang2026kernel | arXiv 2609.22547v2 | RLVR is a Kernel, Not a Function | On five public RLVR pairs no pass@k crossover is statistically established at first; RL's effect is a distribution of post-RL success given base success. | "Across five public RLVR pairs no crossing is statistically established in the initial evaluations, …" — `UPD:312-314` (V-upd); `COES/2609.22547.txt:42` (src) | tool (paired uncertainty on "created" sets) | Meas, RW-e | — |
| akgul2026sparse | arXiv 2605.06241v3 | Rethinking RL for LLM Reasoning: Sparse Policy Selection | RL changes the top token at 1–3 % of positions, always within the base's top 5; an RL-free contrastive method matches RL at about 1,000× lower cost. | "Only 1–3% of token positions are affected, the promoted token always lies within the base model's top‑5 alternatives, …" — `UPD:259-261` (V-upd); `COES/2605.06241.txt:46` (src) | contrasts (alternative account; testable per σ step, `UPD:263-268`) | RW-c, Disc | LLM base / RL checkpoint pairs |
| tajwar2026maxrl | arXiv 2602.02710v3 | Maximum Likelihood Reinforcement Learning | Binary-reward RL approximates maximum likelihood, whose gradient averages successful trajectories only. MaxRL solves 3 AIME 2025 problems that base and GRPO miss at 4,096 samples. | "the maximum likelihood gradient is the average gradient from successful trajectories only" — `COES/2602.02710.txt:323` (src); App. M.3 quote `UPD:366-368` (V-upd) | contrasts (alternative account: EI computes a success-averaged gradient, UPD's reading) | RW-a, RW-f, Disc | Perplexity of RL-found solutions only lower-bounds base success (`UPD:375-377`) |

### 1b. Controlled from-scratch organisms

| key | id / venue | short title | what it claims | strongest verified quote (location) | relation | § | flags |
|---|---|---|---|---|---|---|---|
| abdulsalam2026rewrite | arXiv 2607.07646v1 (arXiv comments: ICML 2026 Compositional Learning workshop) | RL Post-Training Builds Compositional Reasoning Strategies | Pretraining on primitive rewrites excludes the shortcuts; the base gets 0 % on Buckets 4–5 at pass@1024 while RL solves them at pass@16, and RFT plateaus. Low-ρ pretraining never reliably enters the macro or parallel regime. | "even at pass@1024, the pretrained policy gets $0\%$ on Buckets 4–5, while RL later solves them at pass@16" — `LR2/claims.md:101` (V-ledger; re-checked l.155); LEDGER L68 | contrasts (closest design; new action type; equal k; no likelihoods) | Intro, RW-b, §3 | 16 problems per bucket, 3 seeds (`LR2/REVIEW.md:40`); parameter count is only the note-writer's estimate (`LR2/notes/abdulsalam-rl-compositional-rewrite.md:15`) |
| tsilivis2025rlntp | arXiv 2510.11495v2 | How RL After Next-Token Prediction Facilitates Learning | With an exact share p_cot of long parity demonstrations, next-token training alone does not generalise and RL amplifies the long mode (STaR recursion p_n = 2p_{n−1}/(1+p_{n−1})). Learning is efficient in theory unless the share is exponentially small in d. | "as long as the proportion of long demonstrations in the data mix is not exponentially small in the input dimension $d$" — `LR2/claims.md:110` (V-ledger); LEDGER L69 | agrees (dose) / we extend (the knockout case) | RW-b, RW-g, §3 | **"Tests p_cot = 0" is UNVERIFIED** (lowest found 0.01, `LR2/claims.md:112`); elicitation by construction (`LR2/notes/tsilivis-rl-after-ntp-parity.md:25`) |
| zhang2025interplay | arXiv 2512.07783v1 | On the Interplay of Pre-Training, Mid-Training, and RL | A 100M model trained from scratch on synthetic dependency graphs: RL lifts pass@128 only at the edge of competence. With 0 % or 0.1 % pretraining exposure to a new context RL does not transfer; with ≥ 1 % it does. | "0 % / 0.1 % exposure: no transfer; 1 % enhances it" (§4) — `LR1/REVIEW.md:227` (V-recheck, a paraphrased row); "no improvement on pass@128" — `LR1/notes/zhang2025-interplay-pre-mid-rl.md:12` (note-quote); LEDGER L70 | agrees (dose-response) / contrasts (a context, not a rule) | RW-b, RW-g, §3 | Figure-level; no seed counts or error bars seen (note l.18); process-verified pass@k |
| wang2025rlplanning | arXiv 2509.22613v2 | Benefits and Pitfalls of RL for LM Planning | On graph path-finding with a 1-layer transformer, 0/1-reward policy gradient without KL equals SFT on its own successes, yet finds paths absent from the SFT data; without KL it collapses to one path per pair. | "it can explore and discover new correct paths that were absent from the initial training set" — `LR2/claims.md:115` (V-ledger) | agrees (EI is the STaR / RFT case) / contrasts (new combinations of seen edges) | RW-b, RW-f | Tiny stylised setting (`LR2/notes/wang-rl-planning-graph.md:23-24`) |
| zhao2025echochamber | arXiv 2504.07912v2 (arXiv comments: COLM 2025) | Echo Chamber | In 150M and 1B models pretrained from scratch on controlled mixtures, RL quickly converges on one pretraining style, not always the best one; EI retrained from the base underperforms PPO. | RL "amplifies a specific mode … while collapsing the others" — `LR1/REVIEW.md:226` (V-recheck) | agrees (RL amplifies pretraining content) | RW-b | Mostly single runs (`LR1/notes/zhao2025-echo-chamber.md:16`) |
| lee2025selfimproving | arXiv 2502.01612v2 | Self-Improving Transformers | A 14M from-scratch transformer extends to harder and longer instances by training on its own filtered outputs, one difficulty step per round. | "too difficult … is detrimental" (§7.1) — `LR1/REVIEW.md:221` (V-recheck) | extends (an EI-like loop on a small from-scratch model) | RW-b | Arithmetic, string and maze tasks; greedy self-labels |
| poesia2024minimo | arXiv 2407.00695v2 (arXiv comments: NeurIPS 2024 oral) | Learning Formal Mathematics From Intrinsic Motivation (Minimo) | An ≈ 8.45M from-scratch model conjectures and proves (propositional logic among its domains), using proof log-likelihood as difficulty; longest propositional proofs grow 5 → 11 steps. | "GPT-2-style character-level Transformer models totalling approximately 8.45M parameters" — `LR1/notes/minimo-intrinsic-conjecturing.md:15` (note-quote); `LR1/REVIEW.md:228-229` (V-recheck) | tool (closest in scale and logic; log-likelihood difficulty) | RW-b, RW-f, Setup | 5 iterations, tiny budgets, no generator baseline (note l.20) |
| shen2026chess | arXiv 2607.16097v2 | Understanding Reasoning from Pretraining to Post-Training | In 5M–1B chess transformers trained from scratch, pretraining loss predicts post-RL pass@1; on hard puzzles RL surfaces moves the SFT policy gave < 0.05 probability. | "RL does not simply sharpen the SFT policy: … on hard puzzles it surfaces correct moves that were nearly absent under SFT" — `UPD:106-107` (V-upd); `COES/2607.16097.txt:66` (src) | contrasts (varies pretraining scale, not content; their "nearly absent" would count as elicited under our budgets, `UPD:111-112`) | RW-b, RW-g | Closest from-scratch organism with exact per-step likelihoods (`UPD:110`) |
| ranmilo2026outcomerl | arXiv 2601.15158v4 | Outcome-Based RL Provably Leads Transformers to Reason, but Only With the Right Data | Theory for a single-layer transformer on graph traversal: outcome-reward policy gradient needs training data with mass on simple examples. | "when this mass vanishes, policy gradient learning becomes infeasible" — `LR2/claims.md:119` (V-ledger) | agrees (analogy to the removed σ mass, our reading) | RW-b, RW-g | abstract |
| cheng2025atomicskills | arXiv 2512.01970v3 | Atomic Skills are the Prerequisite | In SFT-then-RL on synthetic biographies (Qwen-2.5-1.5B), RL synthesises composite strategies only after the atomic skills were mastered. | "it synthesizes new composite strategies only when the base model has first mastered the independent atomic skills via SFT" — `LR2/claims.md:121` (V-ledger) | agrees (σ's atoms, DN and NEGI, stay in our knockout data) | RW-b, RW-g | Pretrained Qwen, not from scratch (`LR2/claims.md:122`); abstract + grep |

### 1c. Sharpening, power sampling and coverage theory

| key | id / venue | short title | what it claims | strongest verified quote (location) | relation | § | flags |
|---|---|---|---|---|---|---|---|
| karan2025power | arXiv 2510.14901v1 | Reasoning with Sampling | Metropolis–Hastings sampling from the base's power distribution p^α (α 4), with no training, reaches MATH500 0.748 vs GRPO 0.785 at 8.84× the tokens; at large k its pass@k converges to the base's. | "8.84×" tokens (§5.3) and "0.748 vs 0.785" (Table 1) — `LR1/REVIEW.md:223-224` (V-recheck); LEDGER L71 | tool (our MH null implements it) | RW-c, Ctrl | Compared at matched model, not matched per-problem sampling compute (`LR1/notes/karan2025-power-sampling.md:17`) |
| ji2026scalablepower | arXiv 2601.21590v1 | Scalable Power Sampling | A token-level approximation to p^α matches or beats one-shot GRPO with > 10× less latency than MCMC. | "matches or surpasses one-shot GRPO" — `LR2/REVIEW.md:67-68` (abstract quote; not in a claim ledger, `LR2/claims.md:176`) | tool (a cheaper null) | RW-c | **abstract-level only, no note** (LEDGER L72: verify before relying) |
| talwar2026power | arXiv 2610.13653v1 | A Critical Look at Power Sampling | MCMC and SMC power samplers do not converge to π_α at realistic budgets and act as likelihood-guided search; a graded best-of-N recovers most of their gains. | "these samplers fail to converge to $\pi_{\alpha}$ under realistic compute budgets, and that their gains are largely recreated via simple Best-of-$N$ with appropriate grading" — `UPD:208-209` (V-upd); `COES/2610.13653.txt:40` (src) | agrees (consistent with our sampler failing its positive control) | RW-c, Ctrl | Posted 2026-10-09 |
| yang2026correctmass | arXiv 2608.14420v1 | More Correct Mass, Worse Answers | Power sampling (α 4) lowers 8-sample self-consistency accuracy in 7 of 9 settings; a fixed α changes problems by very different amounts. | "Dose mismatch arises because a fixed exponent induces drastically different amounts of distributional change across problems." — `UPD:235-236` (V-upd); `COES/2608.14420.txt:41` (src) | contrasts (one α is not one intervention: sweep α) | RW-c, Ctrl | — |
| he2026unsupervisedrlvr | arXiv 2603.08660v1 | How Far Can Unsupervised RLVR Scale LLM Training? | Intrinsic-reward RLVR provably sharpens toward the base's initial majority answer; it helps only when confidence and correctness align. | "This sharpening mechanism succeeds when initial confidence aligns with correctness but fails catastrophically when misaligned." — `UPD:397-398` (V-upd); `COES/2603.08660.txt:119` (src) | agrees (logic of the sharpening null; implies a positive control) | RW-c | — |
| huang2024sharpening | arXiv 2412.01951v2 | Self-Improvement in LMs: The Sharpening Mechanism | A statistical framework for self-improvement as sharpening with sample access. | "It is impossible for this self-improvement to create information that is not already in the model" — `LR2/claims.md:32` (V-ledger) | agrees (theory frame) | RW-c | abstract |
| tomihari2026powerdistribution | arXiv 2605.04542v1 | Power Distribution Bridges Sampling, Self-Reward RL, and Self-Distillation | p^α is the closed-form optimum of KL-regularised RL that rewards the model's own sequence log-probability. | "the closed-form optimizer of KL-regularized RL when the model's sequence-level log-probabilities are used as the reward" — `LR2/REVIEW.md:68-69` (abstract quote) | tool (theory link) | RW-c | abstract-level only; not in a claim ledger |
| korbak2022rlkl | Findings of EMNLP 2022; arXiv 2205.11275v2 | RL with KL penalties is better viewed as Bayesian inference | The KL-regularised RL optimum is π0·exp(r/β)/Z; with a binary reward it conditions the base on success and keeps the other strings' relative odds. | "all other strings keep the original probability \pi_0(x) up to Z (hence no degeneration)" — `CAP/_claims_L5.md:13` (V-ledger); `CDS/2205.11275.txt:177` (src) | agrees (exact form of "pure elicitation", `CAP/REVIEW.md:79-81`) | RW-c, Disc | — |
| shenfeld2025rlrazor | arXiv 2509.04259v1 | RL's Razor | On-policy RL prefers KL-minimal solutions; 1–0 REINFORCE equals SFT on correct samples; KL(q‖π_B) splits into log 1/p_B plus a reshaping term. | "RL constrains learning to outputs already given non-negligible probability by the base model" — `CAP/_claims_L3.md:126` (V-ledger); `CDS/2509.04259.txt:66` (src) | agrees (EI ≈ 1–0 REINFORCE, l.128) | RW-c, Disc | — |
| huang2025bestofn | arXiv 2503.21878v2 | Is Best-of-N the Best of Them? | What inference-time selection can reach is set by the base policy's coverage of high-quality responses. | "is determined by the base policy's coverage over high-quality responses" — `CAP/_claims_L5.md:34` (V-ledger); `CDS/2503.21878.txt:214` (src) | agrees (theory) | RW-c, TTC | — |
| chen2025coverage | arXiv 2510.15020v2 | The Coverage Principle | Coverage (mass the model under-weights by ≥ N) is necessary and sufficient for best-of-N and generalises faster than cross-entropy; its role for GRPO is only conjectured. | "We prove that a good coverage profile is necessary and sufficient for Best-of-N to succeed" — `LR2/claims.md:25` (V-ledger) | tool (the threshold log p ≥ −ln k, `LR2/notes/chen2025-coverage-principle.md:32`) | RW-c, Meas | The GRPO statement is a belief, not a proof (`LR2/claims.md:28`) |
| foster2025goodfoundation | arXiv 2503.07453v2 | Is a Good Foundation Necessary for Efficient RL? | Base coverage lower-bounds RL runtime in their framework; multi-turn exploration needs only token-level coverage. | "coverage, while not necessary for data efficiency, lower bounds the runtime of any algorithm in our framework" — `LR2/claims.md:29` (V-ledger) | agrees (theory; step-level search vs whole-proof sampling) | RW-c, TTC | Abstract + §1 only |
| xie2024xpo | ICLR 2025; arXiv 2405.21046v1 | Exploratory Preference Optimization (XPO) | Passive on-policy methods cannot find actions the reference model barely covers without exponentially many iterations; an exploration bonus can leave the support. | "Passive exploration is intuitively insufficient, as we are unlikely to generate novel and correct proofs by chance" — `CAP/_claims_L5.md:23` (V-ledger); `CDS/2405.21046.txt:118` (src) | agrees (theory) | RW-c | — |
| mousavihosseini2026barrier | arXiv 2603.06957v2 | Post-Training with Policy Gradients: the Base Model Barrier | Outcome-reward policy gradient needs about 1 / (base likelihood quantile) reward queries; going beyond the base's support can cost exponentially many. Process rewards depend on a token-level quantile. | "However, a barrier arises for going beyond the support of the base model" — `CAP/_claims_L5.md:114` (V-ledger); `CDS/2603.06957.txt:35` (src) | agrees (theory) | RW-c, Disc | "Support" is defined against the uniform policy (`CAP/_claims_L5.md:118`) |

### 1d. Elicitation vs latent capability

| key | id / venue | short title | what it claims | strongest verified quote (location) | relation | § | flags |
|---|---|---|---|---|---|---|---|
| greenblatt2024passwordlocked | arXiv 2405.19550v1 | Stress-Testing Capability Elicitation With Password-Locked Models | A few demonstrations unlock deliberately hidden capabilities; expert iteration can bootstrap from lucky samples, but RL from a weak policy can fail to explore. 18M models locked from scratch need 2–4× more data yet still unlock. | "starting from a worse policy results in poor exploration, which slows down and sometimes entirely prevents learning" — `CAP/_claims_L2.md:21` (V-ledger); `CDS/2405.19550.txt:384` (src) | tool (positive control only; no never-had-it control, `CAP/notes/greenblatt2024passwordlocked.md:59`) | RW-d, Meas | — |
| vanderweij2024sandbagging | arXiv 2406.07358v4 | AI Sandbagging | Actual capability is the best performance under the best available elicitation (prompting, fine-tuning); the 1 %-of-training-cost convention is quoted from Anthropic's RSP. | "actual capability to be the best performance on a certain task it can achieve, given the best currently available capability elicitation techniques such as prompting and fine-tuning" — `CAP/_claims_L2.md:34` (V-ledger); `CDS/2406.07358.txt:105` (src) | tool (budget-relative definition) | RW-d | The note alters quoted wording (`CAP/REVIEW.md:19-20`): quote the ledger, not the note |
| hofstatter2025elicitation | ICML 2025; arXiv 2502.02180v3 | The Elicitation Game | A latent capability shows with low probability by default and is revealed by small changes; fine-tuning should be the evaluator's method of choice. | "is one that a model exhibits with low probability by default, but can be revealed through small changes to the context, activations, or weights" — `CAP/_claims_L2.md:47` (V-ledger); `CDS/2502.02180.txt:151` (src) | tool (definition) | RW-d | — |
| lin2023unlocking | ICLR 2024; arXiv 2312.01552v1 | The Unlocking Spell on Base LLMs (URIAL) | Base and aligned LLMs share top-ranked tokens at most positions; alignment mostly changes style, and three in-context examples can stand in for it. | "77.7% of the tokens are at such unshifted positions, which increases to 92.2% when including marginal positions" — `CAP/_claims_L3.md:102` (V-ledger); `CDS/2312.01552.txt:192` (src) | agrees (elicitation in LLM alignment) | RW-d | Alignment tuning, not verifier RL; authors say coding and maths may still need tuning (`CAP/_claims_L3.md:108`) |
| prakash2024finetuning | arXiv 2402.14811v1 | Fine-Tuning Enhances Existing Mechanisms | Base and fine-tuned models use the same entity-tracking circuit; fine-tuning improves its handling of positional information. | "fine-tuning enhances, rather than fundamentally alters, the mechanistic operation of the model" — `CAP/_claims_L6.md:56` (V-ledger); `CDS/2402.14811.txt:52` (src) | agrees (mechanistic elicitation) | RW-d | SFT, not RL |
| jain2023mechanistically | arXiv 2311.12786v2 | Mechanistically analyzing the effects of fine-tuning | Fine-tuning learns a "wrapper" over pretraining capabilities, which revive within a few steps; a never-had-it control needs far longer. | a 'wrapper' "is typically learned on top of the underlying model capabilities, creating the illusion that they have been modified" — `CAP/_claims_L6.md:32` (V-ledger); `CDS/2311.12786.txt:67` (src); revival 0.1–3K vs 4.5K iterations `CAP/_claims_L6.md:40` | tool (never-had-it control) / agrees | RW-d, RW-g | Toy settings (Tracr, PCFG, TinyStories) |
| venhoff2025base | arXiv 2510.07364v4 | Base Models Know How to Reason, Thinking Models Learn When | Steering the base at the right tokens recovers ≈ 76 % of the RL base-to-thinking gap but 11 % of the SFT-distillation gap. | "RL primarily teaches heuristics for orchestrating pre-existing base mechanisms, whereas SFT-distillation installs new ones" — `CAP/_claims_L6.md:92` (V-ledger); `CDS/2510.07364.txt:51` (src) | agrees (for LLM RL) | RW-d | v1's "up to 91 %" was walked back; cite v4 (`CAP/REVIEW.md:242-243`) |
| ward2025reasoning | arXiv 2507.12638v1 | Reasoning-Finetuning Repurposes Latent Representations | A base-model direction induces backtracking in a distilled reasoning model but not in the base. | "this direction does not induce backtracking in the base model, suggesting that the reasoning finetuning process repurposes pre-existing representations to form new behavioral circuits" — `CAP/_claims_L6.md:73` (V-ledger); `CDS/2507.12638.txt:46` (src) | contrasts (repurposing is neither pure elicitation nor creation) | RW-d | Distillation (SFT), not RL |
| donoway2026edl | arXiv 2601.04728v1 | Excess Description Length | Prequential code length minus residual code length (EDL) separates teaching from eliciting; elicitation should show monotonically falling EDL per token. | "Elicitation shows monotonically decreasing EDL/token with dataset size; teaching shows an initial increasing phase" — `LR2/claims.md:22` (V as stated) | tool (a candidate measure) | RW-d | Empirics in a companion paper **UNVERIFIED** (`LR2/claims.md:22-23`); SFT-only theory (l.24) |
| harding2024capability | Brit. J. Philos. Sci. 2024 (doi 10.1086/732153); arXiv 2405.08989v1 | What is it for a ML Model to Have a Capability? | Conditional analysis: a model has a capability when it would reliably succeed if it "tried"; reliability is evidence. | "a machine learning model has a capability to X just when it would reliably succeed at doing X if it 'tried'" — `CAP/_claims_L2.md:80` (V-ledger); `CDS/2405.08989.txt:43` (src) | tool (definition) | Intro, RW-d | Journal version not read |
| li2026elicitcreate | arXiv 2605.08368v1 | On Distinguishing Capability Elicitation from Capability Creation in Post-Training | Defines "accessible support", the behaviours producible under finite budgets; reweighting within it is elicitation, changing it is creation, relative to base, decoding, signal and budget. | accessible support = "the set of behaviors that a model can practically produce under finite budgets" — `CAP/_claims_L2.md:185` (V-ledger); `CDS/2605.08368.txt:37` (src) | agrees (the closest conceptual frame to our budget-relative "created") | Intro, RW-d, Meas | No in-depth note (abstract, §1, 2.3, 4 read; 3 / 3 claims V) |
| gandhi2025cognitive | arXiv 2503.01307v2 | Cognitive Behaviors that Enable Self-Improving Reasoners | Priming Llama with examples of reasoning behaviours enables substantial RL improvements (a Qwen vs Llama contrast). | "priming Llama with examples containing these reasoning behaviors enables substantial improvements during RL" — `LR2/claims.md:33` (V-ledger) | agrees (priming resembles our 1 % dose, our reading) | RW-d, RW-g | abstract |
| hewitt2019designing | arXiv 1909.03368v1 | Designing and Interpreting Probes with Control Tasks | Probe accuracy means little without a control task only the probe can learn; report selectivity. | "By construction, these tasks can only be learned by the probe itself." — `CAP/_claims_L6.md:11` (V-ledger); `CDS/1909.03368.txt:43` (src) | tool (control logic) | RW-d, Meas | Probing, not RL |
| phuong2024dangerous | arXiv 2403.13793v2 | Evaluating Frontier Models for Dangerous Capabilities | "Expert bits", the help an agent needs before it succeeds (unguided cost ⌈−log₂ ρ⌉), grade how close a model is to a capability. | "By measuring how much information the agent needs, we can distinguish between agents very close to having a capability from those very far away" — `CAP/_claims_L2.md:164` (V-ledger); `CDS/2403.13793.txt:1458` (src) | tool (an analogue of k-to-solve) | RW-d, RW-e | — |

### 1e. Measuring rare behaviour and budgets

| key | id / venue | short title | what it claims | strongest verified quote (location) | relation | § | flags |
|---|---|---|---|---|---|---|---|
| brown2024monkeys | arXiv 2407.21787v3 | Large Language Monkeys | Coverage grows with samples over four orders of magnitude; any model with full support eventually covers everything. | "With unlimited samples, any model that assigns a non-zero probability to every sequence will achieve perfect coverage" — `CAP/_claims_L1.md:19` (V-ledger); `CDS/2407.21787.txt:86` (src) | tool (the budget is the question) | Intro, RW-e, Meas | — |
| chen2021evaluating | arXiv 2107.03374v2 | Evaluating LLMs Trained on Code (Codex) | Gives the unbiased pass@k estimator 1 − C(n−c,k)/C(n,k); the plug-in estimator underestimates. | plug-in 1−(1−p̂)^k "results in a consistent underestimate" — `CAP/_claims_L1.md:12` (V-ledger); `CDS/2107.03374.txt:1995` (src) | tool | Meas | Estimator sections only |
| kazdan2025passk | arXiv 2510.05197v1 | Efficient Prediction of Pass@k Scaling | Fits a beta-binomial to raw counts to forecast large-k pass@k. Chen's estimator needs n ≥ k. | Chen et al. estimators "are only defined when the number of samples taken for each problem is greater than or equal to the number of attempts k" — `CAP/_claims_L1.md:44` (V-ledger); `CDS/2510.05197.txt:155` (src) | tool | Meas | A beta cannot tell impossible from hard (`CAP/REVIEW.md:112-113`) |
| schaeffer2025powerlaws | arXiv 2502.17578v1 | How Do Large Language Monkeys Get Their Power (Laws)? | Aggregate power-law pass@k arises iff per-problem p has a power-law left tail; problems with p below 1/n are unresolved. | "due to finite sampling, we lack the resolution to measure" — `CAP/_claims_L1.md:36` (V-ledger); `CDS/2502.17578.txt:381` (src); the iff statement at `CDS/2502.17578.txt:293` | tool (set-level extrapolation) | Meas | — |
| hu2023passuntil | arXiv 2310.03262v3 | Predicting Emergent Abilities with Infinite Resolution Evaluation (PassUntil) | Sample until r successes; PU = r/K is the maximum-likelihood estimate and works where a random baseline scores zero. | "PU is a maximum likelihood estimate for P(s)" — `CAP/_claims_L1.md:61` (V-ledger); `CDS/2310.03262.txt:160` (src) | tool (stop-at-first-success reads) | Meas | — |
| jones2025forecasting | arXiv 2502.16797v1 | Forecasting Rare Language Model Behaviors | Gumbel-tail extrapolation of per-query elicitation probabilities forecasts deployment-scale rates. | forecasts "across up to three orders of magnitude of query volume" — `CAP/_claims_L1.md:118` (V-ledger); `CDS/2502.16797.txt:76` (src) | tool | Meas | — |
| wu2024rareoutputs | arXiv 2410.13211v2 | Estimating the Probabilities of Rare Outputs | Importance sampling estimates probabilities too small for naive sampling and is unbiased when reweighted. | "If we re-weight our observations properly, this gives an unbiased estimator for the true probability" — `CAP/_claims_L1.md:121` (V-ledger); `CDS/2410.13211.txt:195` (src) | tool (our known-proof sum lies between a one-proof bound and IS, `CAP/REVIEW.md:60-66`) | Meas | Single-token outputs (`CAP/_claims_L1.md:125`) |
| schaeffer2023mirage | arXiv 2304.15004v2 | Are Emergent Abilities of LLMs a Mirage? | Apparent emergence comes from nonlinear or discontinuous metrics; continuous metrics change smoothly. | "nonlinear or discontinuous metrics produce apparent emergent abilities, whereas linear or continuous metrics produce smooth, continuous, predictable changes" — `CAP/_claims_L1.md:73` (V-ledger); `CDS/2304.15004.txt:42` (src) | contrasts (a caution: our ≥ 50 %-of-family bar is a threshold) | Res, Disc | — |
| schaeffer2025generative | arXiv 2509.24012v2 | Pretraining Scaling Laws for Generative Evaluations | pass@k is predictable from gold-reference log-likelihoods across ≈ 5 orders of magnitude, for reasons the authors call unclear. | "it is not immediately obvious why the likelihood of the specific benchmark-provided gold reference correlates so strongly with the pass rate" — `CAP/_claims_L1.md:142` (V-ledger); `CDS/2509.24012.txt:397` (src) | agrees / tool (our known-proof estimator) | Meas | Open "under heavy optimization pressure" (`CAP/REVIEW.md:128-130`) |
| truong2026irsl | arXiv 2606.07616v1 | Item Response Scaling Laws | IRT on repeated-sampling success probabilities gives pass@k as a function of ability θ, with θ linear in log FLOP. | "This tensor is averaged across the sample dimension to yield an empirical probability response matrix" — `CAP/_claims_L4.md:102` (V-ledger); `CDS/2606.07616.txt:234` (src) | tool | Meas | — |
| polo2024tinybenchmarks | ICML 2024; arXiv 2402.14992v2 | tinyBenchmarks | A multidimensional 2PL IRT model calibrated on 395 LLMs estimates benchmark performance from about 100 items per scenario. | θ_l "denotes the unobserved abilities of LLM l" — `CAP/_claims_L4.md:11` (V-ledger); `CDS/2402.14992.txt:172` (src) | tool | RW-e | — |
| martinezplumed2016making | ECAI 2016 (FAIA 285, pp. 1140–1148; doi 10.3233/978-1-61499-672-9-1140) | Making Sense of IRT in Machine Learning | IRT estimates classifier ability and instance difficulty jointly at the instance level. | "IRT shows a dual behaviour in the way that classifier ability and instance difficulty are estimated at the same time, both depending on the other classifiers and instances" — `CAP/_claims_L4.md:76` (V-ledger); `CDS/martinezplumed2016irt-ecai.txt:76` (src) | tool | RW-e | The AIJ 2019 journal version was never read (UNVERIFIED, `CAP/REVIEW.md:13`, l.40): cite ECAI 2016 |
| davidson2023retraining | arXiv 2312.07413v1 | AI capabilities can be significantly improved without expensive retraining | Compute-equivalent gain (CEG) prices an enhancement in training compute; CEG is not meaningful when no scaling reaches the gain. | CEG = "how much additional training compute would be needed to improve performance by the same amount as the enhancement" — `CAP/_claims_L1.md:83` (V-ledger); `CDS/2312.07413.txt:46` (src); "the CEG is not meaningful" `CDS/2312.07413.txt:1053` | tool (precedent for pricing RL in base compute) | Meas | — |
| jones2021boardgames | arXiv 2104.03113v2 | Scaling Scaling Laws with Board Games | Train- and test-time compute trade off: each 10× of training compute removes about 15× of test-time search. | "for each additional 10× of train-time compute, about 15× of test-time compute can be eliminated, down to a floor of a single-node tree search" — `CAP/_claims_L1.md:93` (V-ledger); `CDS/2104.03113.txt:371` (src) | agrees (context for our TTC result) | TTC | Hex, AlphaZero-style agents |
| dragoi2025beyondpassk | arXiv 2510.08325v2 | Beyond Pass@k | Large-k pass@k on discrete answers rewards luck; proposes Cover@τ. | "Pass@k at large k reflects the increasingly higher chance of success in the limit of the number of trials rather than genuine reasoning" — `LR2/claims.md:34` (V-ledger) | contrasts (does not apply to Lean-checked proofs, `LR2/notes/yue2025-doesrl-pass-at-k.md:33`) | Meas | abstract |

### 1f. Expert iteration and RL for theorem proving

| key | id / venue | short title | what it claims | strongest verified quote (location) | relation | § | flags |
|---|---|---|---|---|---|---|---|
| anthony2017exit | arXiv 1705.08439v4 | Thinking Fast and Slow with Deep Learning and Tree Search (ExIt) | An MCTS expert trains a network apprentice; in Hex this beats REINFORCE at matched network evaluations. | "compared to REINFORCE, ExIt learns stronger policies faster" — `LR1/notes/exit-anthony2017.md:12` (note-quote) | tool (our EI is the degenerate expert with no lookahead, note l.20) | RW-f, Setup | Baseline is REINFORCE, not sampling EI (note l.17) |
| polu2020gptf | arXiv 2009.03393v1 | Generative Language Modeling for Automated Theorem Proving (GPT-f) | Best-first search on cumulative log-probability with an outcome-token value; policy and value retrained on found proofs. | no verified quote in local files (screened row `LR1/REVIEW.md:245`) | tool (lineage) | RW-f | Screened row only |
| polu2022curriculum | arXiv 2202.01344v1 | Formal Mathematics Statement Curriculum Learning | Expert iteration with best-first search and a proof-size value, compared with sampling only. | no verified quote (`LR1/REVIEW.md:246`: "partial (Table 1 garbled in PDF text)") | tool (lineage of "expert iteration" in formal maths) | RW-f | Screened row only; EI-vs-sampling numbers unverified |
| lample2022htps | arXiv 2205.11491v1 | HyperTree Proof Search | AND-OR PUCT search with a soft critic and online training; training on minimal proofs beats all proofs (78.1 vs 40.6 on Equations). | "Learning only from the minimal proofs always leads to improved performance" — `LR1/REVIEW.md:206` (V-recheck) | tool (lineage; TTC) | RW-f, TTC | 440–600M arXiv-pretrained models; single runs (`LR1/notes/htps-lample2022.md:16`) |
| xin2024deepseekprover | arXiv 2408.08152v1 | DeepSeek-Prover-V1.5 | GRPO on whole proofs with a Lean reward (RLPAF), plus RMaxTS tree search; the RL and search gains are "orthogonal". | single-pass 58.4 vs RMaxTS 59.6 at 4 × 6,400 — `LR1/REVIEW.md:230` (V-recheck); "orthogonal" `LR1/notes/deepseek-prover-v15.md:14` (note-quote) | contrasts (on TTC, search helps our base more than our RL model) | RW-f, TTC | Search gains ≈ 1–2.5 points (note l.16) |
| xin2025bfsprover | arXiv 2502.03438v3 | BFS-Prover | Length-normalised best-first search plus expert iteration with beam filtering reaches 70.83 % ± 0.89 on miniF2F. | BFS-Prover 70.83 % ± 0.89 — `LR1/REVIEW.md:203` (V-recheck) | tool (lineage) | RW-f | No ablation of α or the filter (`LR1/notes/bfs-prover.md:16`) |
| wu2024internlmstepprover | arXiv 2410.15700v2 | InternLM2.5-StepProver | Critic-guided best-first search finds longer proofs than log-probability best-first; large-scale EI. | BF mean found length 1.66 vs critic-guided 4.44 — `LR1/REVIEW.md:209` (V-recheck) | tool (lineage; TTC) | RW-f, TTC | Critic vs BF not compute-matched (`LR1/notes/internlm25-stepprover.md:17`) |
| dong2025stp | arXiv 2502.00212v4 | STP: Self-play LLM Theorem Provers | A conjecturer supplies barely provable targets because EI on a stalled pool gets almost no successes. | "only 131 out of 2.5M generated proofs of the unproved statements are correct" — `LR1/notes/stp-self-play-conjecturer.md:17` (note-quote); `LR1/REVIEW.md:210-211` (V-recheck) | agrees (EI stalls without successes) | RW-f | Its 13.2 % EI baseline is another paper's number, not an equal-budget run (note l.16) |
| bansal2019deepholzero | arXiv 1905.10501v3 | Learning to Reason in Large Theories without Imitation (DeepHOL-Zero) | A from-scratch HOL Light prover stalls at 7.0 % without exploration and reaches 56.3 % with tf-idf premise injection kept on throughout. | "With no new training data, the learning process would stall." — `LR2/claims.md:68` (V-ledger); 7.0 % vs 56.3 % l.70 | agrees (no-signal stall; an outside source supplies signal) | RW-f | Random-init policy, not pretrained (`LR2/notes/bansal2019-deephol-zero.md:24`) |
| burton2026diversity | arXiv 2601.16172v3 | Inference-Time Diversity in RL-Trained Lean Theorem Provers | DeepSeek-Prover-V1.5-RL plateaus by k 32–64; tactic skeletons help; the base proves zero theorems, so the paper credits RL with creating the capability. | "V1.5-Base proves zero theorems regardless of intervention, identifying RL as the stage that creates the proof capability which subsequently collapses" — `UPD:337-338` (V-upd); `COES/2601.16172.txt:38` (src) | contrasts (creation claimed from ≤ 64 samples of a base that mostly emits `sorry`; the Base→RL contrast spans SFT, `UPD:341-344`) | Intro, RW-f | — |
| schut2023alphazeroconcepts | arXiv 2310.16410v1 | Bridging the Human-AI Knowledge Gap (AlphaZero concepts) | Finds concepts in AlphaZero's latent space that are absent from human games and teachable; four grandmasters improved after study. | novelty = "whether it contains some information that is not present in human games" — `LR2/claims.md:53` (V-ledger); scores l.54 | contrasts (tabula-rasa RL + search; novelty vs human data, not vs a base) | RW-f | n = 4 players, no control group (`LR2/notes/schut2023-alphazero-concepts.md:21`) |
| silver2017alphazero | arXiv 1712.01815v1 | Mastering Chess and Shogi by Self-Play (AlphaZero) | Self-play RL with MCTS from random play reaches superhuman play and rediscovers common human openings. | "Starting from random play, and given no domain knowledge except the game rules" — `LR2/claims.md:59` (V-ledger) | contrasts (no pretraining; enumerable moves with root noise) | RW-f | Targeted grep read; no noise ablation in the paper (`LR2/claims.md:60`) |

### 1g. Pretraining-data ablations, dose, unlearning / relearning

| key | id / venue | short title | what it claims | strongest verified quote (location) | relation | § | flags |
|---|---|---|---|---|---|---|---|
| akter2025frontloading | arXiv 2510.03264v1 | Front-Loading Reasoning | 8B models pretrained from scratch with 20 % reasoning data keep a lead through SFT and RL (+39.32 % on AIME). | "The most striking results appear on the highly challenging AIME competition math problems, where the reasoning-pretrained models deliver a 39.32% improvement over the baseline." — `UPD:158-159` (V-upd); `COES/2510.03264.txt:527` (src) | agrees / contrasts (bulk dose; no pass@k or likelihood) | RW-g | — |
| park2025countdown | arXiv 2512.01775v1 | How Does RL Post-training Induce Skill Composition? (Countdown) | GRPO generalises to larger Countdown instances and unseen tree shapes; with a pattern family removed from the RL data, Qwen2.5-1.5B still learns to produce it. | "Qwen2.5-1.5B trained on this dataset successfully learns to generate the held-out patterns despite zero training exposure" — `UPD:182-183` (V-upd); `COES/2512.01775.txt:446` (src) | contrasts (a positive knockout, but from RL data only; pretraining "very likely" has the patterns, `UPD:186-187`) | RW-g, Disc | No likelihood analysis (`UPD:180`) |
| krishnamurthy2026select | arXiv 2606.13125v1 | Select and Improve | With one reasoning strategy removed at SFT (Qwen2.5-1.5B), GRPO improves only problems the remaining strategy suits; no new pattern emerges. | "we do not observe novel patterns emerging through reinforcement learning" — `UPD:132-134` (V-upd); `COES/2606.13125.txt:69` (src) | agrees (the expected knockout null); we extend (pretraining removal, likelihoods) | RW-g | SFT-stage knockout of a pretrained LLM; no likelihood (`UPD:137-138`) |
| deeb2024unlearning | arXiv 2410.08827v3 | Do Unlearning Methods Remove Information from LM Weights? | Fine-tuning on facts T recovers independent unlearned facts V (> 88 % for pretrained information), so they were hidden, not removed; relearning-time tests lack a baseline. | "The main problem with this approach is the lack of a reliable baseline for comparison" — `CAP/_claims_L2.md:70` (V-ledger); `CDS/2410.08827.txt:194` (src); control model 31.2 % `CAP/_claims_L2.md:74` | tool (control logic; our dose arm is relearning-like) | RW-g, Meas | The quote is in Sec. 2, not 3.2 (`CAP/REVIEW.md:75-76`) |

---

## 2. Themes (draft positioning prose; keys are `refs.bib` keys)

**(a) Does RL expand what the base can do?** (192 words)
The standard test of whether RL with verifiable rewards adds ability is equal-k pass@k. Yue et al. [yue2025doesrl] find
that base models overtake their RLVR descendants as k grows (to 1,024 on AIME24), that base-unsolved, RL-solved
problems are rare (0.0 % and 1.0 % in their Table 2), and, on two problems, that RL outputs lie in the base's
high-likelihood region. ProRL [liu2025prorl] reports gains "where base models fail entirely regardless of the number of
attempts", but reads the boundary at k = 128 on tasks where the base also struggles with formatting; abstract-level
follow-ups tie the answer to training length and rollout width [hu2025brorl, yao2025twostage]. GRPO mainly improves
execution on problems a model already solves [qin2025decomposing], much of RL's measured gain corresponds to operating
points the base reaches under search at up to 16 samples [sun2026budgeted], and visible pass@k crossovers are often not
statistically established [yang2026kernel]. All of these use pretrained LLMs with unknown training data, where reward and
contamination controls change conclusions [shao2025spurious, wu2025contamination]. We keep the question and change the
instrument: Lean judges both models, base budgets are matched to RL's compute, and likelihood brackets are given per
theorem.

**(b) Controlled from-scratch organisms.** (193 words)
Designs that control pretraining and then intervene on it separate creation from elicitation best. Abdulsalam et al.
[abdulsalam2026rewrite] pretrain a 12-layer transformer on primitive rewrites that exclude later shortcuts: the base
scores 0 % on the two hardest buckets at pass@1024 while RL (GRPO) solves them at pass@16, RFT plateaus, and low-ρ
pretraining "never reliably enters the macro or parallel regime" (16 problems per bucket, 3 seeds, no likelihoods).
Tsilivis et al. [tsilivis2025rlntp] set the share of long parity demonstrations exactly and show RL amplifying that mode,
efficiently in theory unless the share is exponentially small in the input dimension; the lowest share the notes found
tested is 0.01. Interplay [zhang2025interplay] finds that RL transfers to a new context only when the context made up at
least 1 % of pretraining. Other organisms show policy gradient finding graph paths absent from its SFT data
[wang2025rlplanning], RL collapsing onto one pretraining style [zhao2025echochamber], and RL surfacing chess moves with
SFT probability below 0.05 [shen2026chess]; Minimo [poesia2024minimo] is the nearest prover in scale and logic. We add a
single-composition knockout with a matched refill, a dose arm, and likelihoods of arbitrary proofs at every checkpoint.

**(c) Sharpening and power sampling as an RL-free alternative.** (184 words)
If RL only sharpens the base, an RL-free sharpener should match it. Karan and Du [karan2025power] sample the base's
power distribution p^α by Metropolis–Hastings and approach GRPO on MATH500 (0.748 vs 0.785) at 8.84× the tokens. A
token-level approximation reportedly matches one-shot GRPO with over 10× less latency than MCMC [ji2026scalablepower],
and p^α is the optimum of KL-regularised RL that rewards the model's own log-probability
[tomihari2026powerdistribution]; both are abstract-level reads. Two 2026 papers complicate the null: practical MCMC and
SMC samplers do not converge to π_α at realistic budgets and act as likelihood-guided search [talwar2026power], and one
α sharpens different problems by very different amounts [yang2026correctmass]. Theory frames the limit: with a binary
reward, the KL-regularised optimum is the base conditioned on success, which keeps the base's odds among correct outputs
[korbak2022rlkl]; on-policy RL prefers KL-minimal solutions [shenfeld2025rlrazor]; and coverage bounds best-of-N and
policy-gradient query counts [chen2025coverage, huang2025bestofn, mousavihosseini2026barrier]. Our MH sampler, at matched
decoded tokens, solved none of RL's compute-matched new solves but also found fewer rare base solves than plain sampling,
so it is a null for this sampler, not for p^α.

**(d) Elicitation vs latent capability.** (181 words)
Safety evaluation defines capability relative to elicitation: "actual capability" is the best performance under the
best available elicitation techniques [vanderweij2024sandbagging], and a latent capability is one a model shows with
low probability by default that small changes reveal [hofstatter2025elicitation]. Password-locked models show that a
few demonstrations, or expert iteration from lucky samples, recover deliberately hidden skills, while RL from a weak
policy can fail to explore [greenblatt2024passwordlocked]. Mechanistic studies find fine-tuning enhancing or wrapping
existing mechanisms [prakash2024finetuning, jain2023mechanistically], RL-trained reasoning models orchestrating base
mechanisms [venhoff2025base], and alignment leaving most token positions unshifted [lin2023unlocking]. Conceptually, a
capability is reliable success, not a lucky one [harding2024capability], and creation can be defined as changing the
support a model reaches under a stated budget, decoding policy and signal [li2026elicitcreate]. The strongest "it was
already there" arguments compare against a control that lacks the capability [deeb2024unlearning,
jain2023mechanistically, hewitt2019designing]; password-locking supplies only the positive half. Our σ-free bases are
such a control for one composition, with the caveat that they still write σ rarely, so our statements are relative to a
stated budget, not claims of absence.

**(e) Measuring rare behaviour and budgets.** (172 words)
Sampling-based capability is coverage at a budget: with unlimited samples, any model with full support covers
everything [brown2024monkeys], so the field reports per-problem success probabilities and their distribution
[schaeffer2025powerlaws, kazdan2025passk]. The unbiased pass@k estimator needs at least k samples per problem
[chen2021evaluating, kazdan2025passk], and success probabilities below 1/n are not resolved by n samples; PassUntil
samples until r successes [hu2023passuntil], and importance sampling or tail extrapolation reach rarer events
[wu2024rareoutputs, jones2025forecasting]. A single proof's likelihood bounds the success probability from below, and
gold-reference likelihoods predict pass@k, though whether that holds under heavy optimisation is open
[schaeffer2025generative]. Zero successes in k attempts bound p through (1 − p)^k ≤ ζ [wu2025invisibleleash], the logic
behind our Clopper–Pearson certificates; pass@k crossovers need paired inference [yang2026kernel]; and thresholded
metrics can manufacture jumps [schaeffer2023mirage], so our family bar should be read beside continuous rates.
Compute-equivalent gain [davidson2023retraining] and IRT [truong2026irsl, polo2024tinybenchmarks,
martinezplumed2016making] offer other common scales. Because Lean checks every step, our pass@k is a CoT-pass@k
[wen2025cotpassk], and lucky-guess critiques of large-k pass@k [dragoi2025beyondpassk] do not apply.

**(f) Expert iteration and RL for theorem proving.** (198 words)
Our loop is expert iteration in its simplest form: sample 32 proofs per target, keep what Lean accepts, fine-tune. ExIt
[anthony2017exit] paired a search expert with a network apprentice and beat REINFORCE at matched network evaluations in
Hex; neural provers run the same loop with best-first or tree search as the expert [polu2020gptf, polu2022curriculum,
lample2022htps, wu2024internlmstepprover, xin2025bfsprover] or with GRPO on a Lean reward [xin2024deepseekprover]. The
loop stalls when hard targets yield no successes: a from-scratch HOL prover stays at 7 % without injected exploration
[bansal2019deepholzero], and STP saw 131 correct proofs in 2.5 M attempts on unproved statements [dong2025stp]. At least
one formal-math creation claim rests on a small budget: Burton [burton2026diversity] credits RL with
DeepSeek-Prover-V1.5's ability because its base proves nothing in 64 attempts, while 58.8 % of the base's outputs are
`sorry`. AlphaZero offers the strongest evidence in the notes that RL with search produces knowledge absent from human
play [silver2017alphazero, schut2023alphazeroconcepts], but it starts from random play over enumerable moves, and the
human study had four players and no control. DeepSeek-Prover-V1.5 found RL and search gains "orthogonal"
[xin2024deepseekprover]; in our organism, guided redraws and PUCT/MCTS help the base far more than the RL model.

**(g) Pretraining-data ablations, dose and unlearning / relearning.** (199 words)
Pretraining-data interventions point the same way across scales. A 20 % reasoning-data share in 8B pretraining leaves a
lead that survives SFT and RL [akter2025frontloading]; RL transfers to a new context only after at least 1 % pretraining
exposure [zhang2025interplay]; and learning from long parity demonstrations is efficient unless their share is
exponentially small [tsilivis2025rlntp]. A theory paper finds outcome-reward policy gradient infeasible when the data's
mass on simple examples vanishes [ranmilo2026outcomerl], and an SFT-then-RL study finds RL composing new strategies only
from atomic skills already mastered [cheng2025atomicskills]. Two knockouts disagree: removing a strategy at the SFT stage
of a 1.5B model leaves GRPO improving only what the remaining strategy suits [krishnamurthy2026select], whereas a pattern
family removed from Countdown's RL data is still produced after GRPO [park2025countdown], plausibly because pretraining
contains it; neither reports the knocked-out behaviour's base likelihood. Unlearning work supplies the control logic:
facts recovered after fine-tuning on other, independent facts were hidden rather than removed, and relearning speed needs
a never-trained baseline [deeb2024unlearning, jain2023mechanistically]. Our knockout removes one composition from
pretraining with a matched refill, keeps its atoms, measures the base's rate and likelihood for it, and adds a 1 %
put-back arm, which restores acquisition.

Sources for "our" sentences: the brief's design summary; LEDGER L79 (knockout set), L85–L86 and REV l.505, l.516
(power-sampling null and its rewording), L88–L89 and REV l.485 (primary result), L97 and REV l.490 (dose), REV l.492
(σ rare, not absent).

---

## 3. Exactly how our design differs

**Abdulsalam, Patel & Saxe [abdulsalam2026rewrite].** *Manipulation:* they pretrain a transformer from scratch on chained
single-step primitive rewrites of a known grammar, which exposes "local grammar-consistent rewrite dynamics, but not to
the later non-primitive shortcuts", with a contraction weight ρ setting the pretraining distribution (`LR2/claims.md:100`;
`LR2/notes/abdulsalam-rl-compositional-rewrite.md:15`). Post-training contracts a word to its target symbol under a
256-token budget, so harder buckets need shortcuts, and compares GRPO with RFT on the same prompts under a binary
outcome reward (note l.16). *Budget:* the base is read at pass@1024 and RL at pass@16 (`LR2/claims.md:101`), on 16
problems per bucket with 3 seeds (`LR2/REVIEW.md:40`), at equal k with no compute-matched budget (LEDGER L68) and with no
likelihood of the composed procedures under the base (note l.26). *Zero exposure:* tested for the shortcut actions,
which pretraining never shows and RL builds; that is a new action type, not a new arrangement of rules already shown
(note l.30; LEDGER L68), and low-ρ pretraining "never reliably enters the macro or parallel regime"
(`LR2/claims.md:105`). *Scale:* 12 layers, hidden size 512, 8 heads (`LR2/claims.md:106`); the "tens of M" parameter
count is the note-writer's estimate (note l.15). We instead remove one composition whose rules stay in pretraining and
refill to the same size (LEDGER L79), compare at compute-matched budgets with Lean as the only judge, and see the
opposite outcome: 0 / 6 knockout seeds acquire a family within 16 rounds (LEDGER L89; REV l.485).

**Tsilivis et al. [tsilivis2025rlntp].** *Manipulation:* small GPT-2- and Mistral-style transformers are trained from
scratch, online, on a mixture of short parity examples and long chain-of-thought demonstrations, with the long fraction
p_cot set exactly (`LR2/notes/tsilivis-rl-after-ntp-parity.md:15`). *Budget:* success is greedy accuracy; next-token
training alone does not generalise "even with access to ~10^7 training samples" (`LR2/claims.md:107`), while GRPO,
REINFORCE or STaR move greedy accuracy from chance to 100 % after a handful of sequences (note l.17), over 3 seeds
(note l.24). *Zero exposure:* not tested; the lowest p_cot the notes found is 0.01, and "Tsilivis tests p_cot = 0" is
UNVERIFIED (`LR2/claims.md:112`; LEDGER L69). The successful long behaviour is present in pretraining by construction,
so their result is amplification (note l.25). *Scale:* depth 2, 4 or 8 and width 128 or 256 (note l.15). Our knockout is
the near-zero case they leave open, for a proof composition rather than a response length, and it is near-zero rather
than zero: the knockout bases still write σ proofs of family members at low rates (REV l.492, l.514).

**Interplay [zhang2025interplay].** *Manipulation:* a 100M Qwen2.5-style model is pretrained on 10B tokens of synthetic
GSM-Infinite dependency-graph problems (op 2–10) and trained with GRPO (`LR1/notes/zhang2025-interplay-pre-mid-rl.md:10`);
the share of a new context in pretraining is set to 0 %, 0.1 % or ≥ 1 % (note l.13), and mid-training vs RL compute is
also varied (note l.14). *Budget:* success is process-verified pass@k, where every step of the parsed graph must match,
reported at pass@128; RL raises pass@128 only at the edge of competence, where base pass@128 is already above zero (note
l.11–12; LEDGER L70). *Zero exposure:* tested for a context: 0 % and 0.1 % give no RL transfer and ≥ 1 % does
(`LR1/REVIEW.md:227`; note l.13), but this concerns a context, not a rule (LEDGER L70), and the results are figure-level
with no seed counts or error bars seen (note l.18). *Scale:* 100M parameters (note l.10). Our exposure manipulation
targets one rule composition in a 9.56M model, with 6 knockout and 6 full seeds, 3 dose seeds and a pre-registered test,
and reads base rates over 1.1–1.4 M pooled attempts rather than at k 128 (LEDGER L88, L89, L97; REV l.485, l.490).

---

## 4. Gaps and cautions

### 4.1 Claims the notes do not support

1. **"First to remove pretraining content before RL."** Interplay set a context's pretraining exposure to 0 %
   (`LR1/REVIEW.md:174-175`), and Abdulsalam et al. excluded the shortcuts from pretraining (`LR2/claims.md:100`). The
   defensible version is narrower: among the papers screened in the three reviews and UPD, none removes a *single
   composition* from pretraining and measures the base's likelihood of it (`UPD:43-51`). LR2's "Creation at p = 0 would
   be new to the literature" (`LR2/REVIEW.md:154`) is about creation, which we did not observe.
2. **"The only organism with exact likelihoods."** LR2 says ours is the only organism with likelihoods of arbitrary
   proofs along the trajectory (`LR2/REVIEW.md:138-140`), but Shen et al. have exact per-step likelihoods in a
   from-scratch chess organism (`UPD:110`), and Minimo scores difficulty by proof log-likelihood
   (`LR1/notes/minimo-intrinsic-conjecturing.md:12`). Say "likelihoods of arbitrary proofs at every checkpoint".
3. **"RL cannot create what pretraining lacks."** Other organisms contradict it: RL builds shortcut actions absent from
   pretraining (`LR2/claims.md:101`), policy gradient finds paths absent from SFT data (`LR2/claims.md:115`), GRPO
   produces a pattern family absent from its RL data (`UPD:182-183`), and exploration lifts a from-scratch HOL prover
   from 7 % to 56 % (`LR2/claims.md:70`). Our result is "not acquired by this EI from a σ-free base within 16 rounds
   (0 / 6 seeds; one seed acquiring slowly by r24)" (REV l.509), and 0 / 6 bounds the per-seed creation rate only below
   0.39 (REV l.536).
4. **"σ is absent from the knockout bases" or "≈ 10⁻⁶ per attempt".** The review asks for "write σ proofs of family
   members (1–6 in 1.1–1.4 M pooled attempts)" and notes 2 / 6 certified bases (REV l.492, l.514).
5. **"Sharpening the base is not RL."** Our null holds for one MH sampler (α 1.5–4) at matched decoded tokens, which also
   failed its positive control (REV l.516, l.532). Samplers may not converge to π_α [talwar2026power], one α is not one
   intervention [yang2026correctmass], and the scalable sampler [ji2026scalablepower] is abstract-level only (LEDGER L72).
6. **"Tsilivis et al. tested p_cot = 0."** UNVERIFIED (`LR2/claims.md:112`; LEDGER L69).
7. **"Interplay shows a 1 % threshold for rules."** It concerns a context, with process-verified pass@128 and no seed
   counts seen (LEDGER L70; `LR1/notes/zhang2025-interplay-pre-mid-rl.md:18`).
8. **"Yue et al. show with likelihoods that RL stays in the base's support."** That evidence is two problems with 16
   responses each (`LR2/claims.md:14`); their main design is equal k ≤ 1,024 without compute matching (LEDGER L67).
9. **"ProRL shows RL creating ability."** The base is read at k 128 on tasks where it "struggles with formatting"
   (`LR2/claims.md:19`; `LR2/notes/liu2025-prorl.md:20`).
10. **"Unlikeliness rewards beat expert iteration."** He et al. claim it but run no EI experiment
    (`LR1/notes/he2025-rewarding-unlikely.md:22`).
11. **"STP doubles expert iteration."** Its 13.2 % comes from another paper, not an equal-budget run
    (`LR1/notes/stp-self-play-conjecturer.md:16`).
12. **"EI underperforms PPO" (Echo Chamber)** applies to EI that retrains from the fixed base each round, mostly in single
    runs (`LR1/notes/zhao2025-echo-chamber.md:14`, l.16).
13. **"Steering recovers up to 91 % of the RL gap."** Walked back; v4 says ≈ 76 % (`CAP/REVIEW.md:242-243`).
14. **"EDL has been validated empirically."** The companion paper was not found (`LR2/claims.md:22-23`), and the theory
    is SFT-only (l.24).
15. **"RL created DeepSeek-Prover-V1.5's ability."** That rests on ≤ 64 base samples, mostly `sorry`, and the Base→RL
    contrast spans an SFT stage (`UPD:331-344`).
16. **"MaxRL shows the base cannot solve those problems."** High base perplexity of RL-found solutions only lower-bounds
    base success (`UPD:375-377`).
17. **"Power sampling matches GRPO at matched compute."** Karan & Du compare at matched model, at 8.84× the tokens
    (`LR1/notes/karan2025-power-sampling.md:17`; `LR1/REVIEW.md:223`).
18. **AlphaZero "novelty"** is relative to human games, with four grandmasters and no control
    (`LR2/notes/schut2023-alphazero-concepts.md:21`).
19. **Model sizes and venues.** Abdulsalam et al.'s parameter count is an estimate (note l.15); Martínez-Plumed et al.'s
    AIJ 2019 version was never read (`CAP/REVIEW.md:13`); Harding & Sharadin's journal version was not read.
20. **Our own numbers** must use the review's wording where it differs from the ledger, e.g. Boschloo p 0.0032 (not
    0.0020) for the RL-only reading (REV l.489, l.525).

### 4.2 Worth reading in full before relying on them (the notes cover them only partly)

- **Abstract-level only:** Ji et al. 2601.21590 (LEDGER L72), Tomihari & Sato 2605.04542, Huang et al. 2412.01951,
  Ran-Milo et al. 2601.15158 (the vanishing-mass theory closest to our knockout), Gandhi et al. 2503.01307 (priming as a
  dose), BroRL 2510.01180, Yao et al. 2510.04028, Wen et al. 2506.14245, Dragoi et al. 2510.08325, Shao et al.
  2506.10947, Wu et al. 2507.10532.
- **Partial reads without an in-depth note:** Li & Liu 2605.08368 (conceptually the closest; write a note), Qin et al.
  2505.22756, the Invisible Leash 2507.14843 (SRR / NDR definitions), POPE 2601.18779, Foster et al. 2503.07453, Cheng
  et al. 2512.01970, Polu & Sutskever 2009.03393 and Polu et al. 2202.01344 (no local verified quote).
- **Gaps inside full reads:** Interplay's seeds and error bars; Tsilivis et al.'s appendix (any p_cot = 0 run) and their
  Llama experiments (§5, not reviewed); Abdulsalam et al.'s per-bucket counts at other k.
- **Screened but not in the table** (no verified quote): Natural Ungrokking 2606.26050 (which rules survive pretraining
  at low frequency; `UPD:419-420`); Sparse but Critical 2603.22446 and When RLVR Shrinks the Reasoning Boundary
  2607.20543 (read by UPD's agent, no notes; `UPD:409-413`); Power-SMC 2602.10273 and EGPS 2606.09926 (`UPD:414-415`);
  Donoway et al., "Quantifying Elicitation of Latent Capabilities in Language Models" (NeurIPS 2025, OpenReview; abstract
  only; `CAP/screened.md:52`); Physics of LMs Part 4.1, 2512.17351 (seen in search only; `LR2/claims.md:133`); AlphaProof
  (Nature, DOI 10.1038/s41586-025-09833-y; read for techniques in LR1, not for create-vs-elicit).

### 4.3 Bibliography notes

- `refs.bib` has 89 entries, one per table row; BibTeX (plainnat) runs on it without errors. Author lists come from the
  local fetched texts or the arXiv abstract pages; two long lists use "and others" (Chen et al. 2021; Phuong et al.
  2024). Venues appear as inproceedings / article only where a note states them (Korbak: Findings of EMNLP 2022; Xie:
  ICLR 2025; Hofstätter: ICML 2025; Lin: ICLR 2024; Maia Polo: ICML 2024; Martínez-Plumed: ECAI 2016; Harding &
  Sharadin: Brit. J. Philos. Sci. 2024). Venues seen only in arXiv comments (Abdulsalam: ICML 2026 workshop; Zhao: COLM
  2025; Zhu: NeurIPS 2025; Tuyls: ICLR 2026; Poesia: NeurIPS 2024; Wu: AAAI 2026) stay in the note field of a misc entry.
- Keys already used in `paper/sections/*.tex` are kept: `abdulsalam2026rewrite`, `anthony2017exit`, `karan2025power`,
  `liu2025prorl`, `talwar2026power`, `tsilivis2025rlntp`, `yue2025doesrl`, `zhang2025interplay`.
- Mapping to citekeys in the notes / nd-rl `references.bib`: `yue2025doesrl` = yueDoesReinforcementLearning2025;
  `liu2025prorl` = liuProRLProlongedReinforcement2025; `donoway2026edl` = donoway2026excessdescriptionlengthlearning;
  `poesia2024minimo` = poesia2024learningformalmathematicsintrinsic; `abdulsalam2026rewrite` =
  abdulsalam2026rlcompositional; `tsilivis2025rlntp` = tsilivis2025rlafterntp. The other notes' keys are reused as they are.
