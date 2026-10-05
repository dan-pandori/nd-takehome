# Pre-registration — run `capability-defs` (proposal 26: what should "capability" mean, and how do we measure it?)

Written 2026-10-05, **before any pod exists for this run** (`~/pods.log` has no `cd-*` line; `podbudget capability-defs`: ceiling 100 h / $50, 0 h used at this commit). Executor: agent:claude, `--effort max`. Branch
`dan_capability-defs` (from the fork's `origin/dan`). Brief: run brief `capability-defs` (Dan, 2026-10-04). Policy:
`AGENT_POLICY.md` (Lean alone decides; plain + guided read-outs; every number names its model; compute rows).

## Question

The project asks whether RL against a verifier **creates** a capability or **elicits** one the pretrained model already
had. "Capability" has never been defined precisely enough to answer that. Dan's objection to pass@k: at some k even
random weights solve every theorem. This run (1) surveys how other fields define and measure capability and tell a new
capability from better access to an old one; (2) writes ≥ 15 candidate definitions as cards, each with a decision
rule, a null, a cost, sensitivities, failure modes and a critic's verdict; (3) computes ≥ 6 of them on the same model
comparisons and reports how much they agree; (4) recommends 2–4 as the project standard.

## Notation used below

π_θ(y | t): probability that model θ writes proof y for theorem t (one attempt, plain sampling, T 1.0 for scoring,
T 0.8 for sampling as in every read). V(t, y) ∈ {0, 1}: Lean accepts. **p_θ(t) = Σ_y π_θ(y | t) V(t, y)**: the
single-attempt solve probability (the marginal over every valid proof). pass@k = 1 − (1 − p)^k. K: an attempt budget.
"pend" = end of pretraining; r8 / r16 = after 8 / 16 rounds of expert iteration (EI); "init" = step 0 (random weights).

## Design

**Part 1 (literature).** Six thread groups (sampling and compute-equivalence; elicitation practice and philosophy;
information, learnability and likelihood; psychometrics; RL theory and composition; mechanistic and games), read by
subagents (≤ 3 at a time, downloads one at a time). Targets: ≥ 60 papers new to the two earlier reviews screened,
≥ 20 read in depth, every cited claim checked against the fetched text (`capability_defs/lit/quote.py`, location
recorded) or marked UNVERIFIED. I re-check ≥ 30 of the agents' claims myself.

**Part 2 (catalogue).** ≥ 15 cards in `capability_defs/cards/`, including Dan's two notions made strict:
(a) teacher-forced probability of specific proofs and (b) pass@k at large k. One critic subagent per card argues the
definition fails; its strongest argument and my answer go on the card.

**Part 3 (quantification).** Models (all Lean alone; labels carried into every table):
- **cap 12:** `trajectory`'s best-cap12 seeds s0–s2 (`best_model.ALiBiGPT`, 9,560,832 params, `lean_staten`, from
  scratch on K12 `data/kh/train_k12.jsonl`, 155,000 records): init, pretraining checkpoints, pend (r0), r8; and
  `rl-continue`'s r12 / r16.
- **cap 6:** `trajectory-cap6`'s best-cap6 seeds and `rl-continue-cap6`'s r16 (same network, cap-6 Stage-1 set).
- `rl-from-ckpt` ladders where they add a comparison.

Sets: holdout250 and textbook72 (**scoring only**, under its manifest rule: never trained or tuned on, dev58 / train14
reported separately and combined), group C (per seed), `rl_targets` (ladder records), the long pools where read.

Definitions I will quantify (≥ 6, from different families; exact protocols in the cards):
1. **Equal-k support** (Yue-style): base 0 / k and RL ≥ 1 / k at k = 256, defined on one sample draw and checked
   on the independent one.
2. **Budgeted support with a bracketed base solve probability** (Dan's (b) made strict): p_pend(t) is bounded above
   by direct sampling (Clopper–Pearson) and below by the summed teacher-forced probability of every distinct
   Lean-accepted proof of t found by any model, Σ_{y∈F(t)} π_pend(y | t). Decision at a budget K tied to RL's compute:
   K_per (RL's compute per training target, in base-attempt equivalents) and K_total (all of RL's compute given to one
   theorem). Elicited if the lower bound ≥ 1/K; created if the upper bound < 0.05/K; otherwise undetermined.
3. **Teacher-forced probability of specific proofs** (Dan's (a) made strict): reference (shortest known), RL's own
   (eventual) and best known proof; total, per-step mean and worst step; base vs RL; threshold −ln K.
4. **Bits over a null**: log π(y) relative to the random-init checkpoint; RL's share of the bits.
5. **IRT ability**: a binomial 2PL over every checkpoint × theorem read; RL checkpoints projected onto the
   pretraining-only scale; items whose RL success exceeds the 1-D prediction (differential item functioning).
6. **Reliability** (pass@1 thresholds and consistency across seeds).
7. **Schema acquisition** over a family (excluded middle and the other classical schemata in group C).
8. **Pretraining-compute equivalent**: how far the pretraining trajectory of p_θ(t) would have to be extrapolated to
   reach the RL value.
9. If the scoring job runs: **sharpening vs expansion** — the share of RL's success mass on proofs with
   π_pend(y) < 1/K.
10. If the fine-tune job runs: **elicitation by small fine-tuning** (sample complexity) for the excluded-middle schema.

For each: the created set per seed, its size, its redraw spread (x0 vs x1) and seed spread, an agreement matrix
(Jaccard) across definitions, threshold sensitivity, and the largest disagreements with examples in Lean. Plain and
guided numbers are labelled and never mixed.

**Pod jobs** (each is also logged in `log.md` before launch; compute rows via `record.py`; models cap 12 unless
stated; all Lean alone; checkpoints from the bucket paths in `capability_defs/analysis/INVENTORY.md` § C):
- **J1, teacher-forced scoring** (`tj_score.py` from `dan_trajectory`, fp32, 33 name bases, T 1.0 and T 0.8). Targets:
  F(t), every distinct Lean-accepted proof found by any read of any model (trajectory and trajectory-cap6 reads, all
  checkpoints and draws; rl-continue r12 / r16; mcts-a; references), for t in the **hard set** H_s = {t ∈ tb72 ∪ h250 :
  pend_s solves t in neither x0 nor x1} plus a **calibration set** of up to 30 theorems per seed with pend pooled n_ok in
  [3, 100] of 512. Checkpoints: init, pend, r8, r16 of each seed. A per-theorem cap of 400 proofs if F(t) is larger
  (priority: references, proofs found by pretraining checkpoints, then r8, r16, others), stated per theorem. ≈ 4–8 GPU-h.
- **J2, large-k base sampling** (`state_eval.py`, trajectory's read settings: T 0.8, `max_steps` 96, `max_action` 512,
  batch 2,048, fresh sample seed 7): pend_s on J2_s = {t ∈ H_s : r8_s or r16_s solves t in some read} plus the
  calibration set. Stage A: 16,384 attempts per theorem. Stage B (if the budget allows): theorems with 0 successes after
  stage A get 65,536 in all. Truncation reported per stratum. ≈ 8–25 GPU-h.
- **J3, guided and plain-with-counts reads** (`guided_eval.py`, plain + logical arms, k 256, T 0.8, sample seed 1, the
  guided-tts settings): pend, r8, r16 of each seed on tb72 + h250 (cap 12; cap 6 if the budget allows). ≈ 5–10 GPU-h.
- **J4, excluded-middle elicitation fine-tunes**: one ladder-style fine-tune step (600 steps, lr 3e-4, 20,000 K12
  replay records, `state_ladder_ei.py`'s trainer) from pend_s0 and pend_s2 with N ∈ {0, 4, 16} premise-free A ∨ ¬A
  proofs taken from s1's `found_16` on `rl_targets` (never textbook72 or a renaming of it; class overlap checked
  first), plus a control with 16 non-LEM proofs of matched length; read on held-out A ∨ ¬A instances (holdout250's and
  the unused `rl_targets` ones) at k 256. ≈ 2–4 GPU-h.

## Expected results (falsifiable; scored in the write-up)

Literature and catalogue:
- L1. ≥ 60 new papers screened and ≥ 20 in depth; ≥ 90 % of the agents' cited claims verified; my re-check of ≥ 30
  claims finds ≤ 2 errors.
- L2. No surveyed quantitative definition separates creation from elicitation without either a budget / threshold or a
  reference model; the principled budgets found are tied to compute.
- L3. Critics break (a failure I accept as serious, recorded on the card) ≥ 1/3 of the cards.

Quantification (cap 12, pend vs r8 unless stated; "B" = equal-k created set defined on draw x0; budgets K_per and
K_total are computed from the ladders' compute rows as base-attempt equivalents, roughly K_per ≈ 4×10² (attempts) to
8×10² (GPU time) and K_total ≈ 1.8×10⁶ to 3.5×10⁶ at r8):
- Q1. Equal-k created set: 45–70 of 322 theorems per seed at r8; 55–85 at r16 (x1). Redraw Jaccard (x0- vs
  x1-defined) 0.45–0.80.
- Q2. In J2 stage A (16,384 attempts), 60–95 % of each seed's J2 theorems get ≥ 1 base success.
- Q3. Bracket at K_total: the known-proof lower bound (T 0.8) certifies **40–85 %** of B as elicited; **0** theorems are
  certifiable as created at K_total (it would need ≈ 60 K_total base samples).
- Q4. Bracket at K_per: the known-proof lower bound alone certifies **≤ 25 %** of B as elicited.
- Q5. Marginal vs specific proof: median over B of log Σ_{y∈F} π_pend(y) − max_y log π_pend(y) **≥ 1 nat**.
- Q6. "New proof, old theorem" (RL's eventual proof below 1/K_total under pend while the lower bound is at or above it):
  **≥ 20 %** of B.
- Q7. RL's share of the bits over the random-init null is **< 2 %** for ≥ 95 % of B's theorem–seed pairs.
- Q8. IRT: the pretraining-only 1-D model ranks r8's per-theorem success with Spearman **≥ 0.7**; r8's ability exceeds
  every pretraining checkpoint's on 3 / 3 seeds; s1 r16's top decile of positive residuals contains **≥ 3** of the six
  holdout250 A ∨ ¬A instances it newly solves.
- Q9. Reliability: the set "p_pend < 0.05 and p_r8 ≥ 0.5" is **1.2–2.5×** the size of the equal-k set.
- Q10. Excluded middle: s1 r16 held-out instance pass@256 ≥ 0.5; s0 ≤ 0.1; pend ≤ 0.05 on every seed.
- Q11. J4: 16 excluded-middle demonstrations raise pend's held-out excluded-middle pass@256 to ≥ 0.5 on ≥ 1 of the 2
  seeds; the matched control stays ≤ 0.1.
- Q12. Pretraining-compute equivalent of r8's gain on B: median multiplier 3×–30× the pretraining length.
- Q13. J3 guided reads of pend solve ≥ 10 % of B (k 256), so guided elicitation shrinks the created set.
- Q14. Agreement: mean pairwise Jaccard of the created sets across definitions **≤ 0.4**; the least-agreeing pair
  includes the K_total bracket.
- Q15. Calibration: on the calibration set, the median of Σ_{y∈F} π_pend(y) / p̂_pend (T 0.8) is **0.3–1.0**: the known
  proofs carry a large share of the true marginal where it can be measured directly.
- Q16. Extrapolation backtest (3.2 M support-curves data, 383 theorems): a beta-binomial fitted to the first 256
  attempts per theorem predicts the number of theorems solved at 10,000 attempts within ±25 %; a zero-inflated variant
  does at least as well.

## Budget and stop rule

Pods: $50 / 100 pod-hours (optional); `podbudget capability-defs` shows the ceiling already registered (100 h, $50)
and 0 h used at this commit. **The binding constraint is the RunPod balance: $122.55 at 2026-10-05 05:45 UTC against the
$100 floor**, so at most ≈ $20 can be spent unless Dan tops it up (asked in `QUESTIONS.md`). Order of priority: J1, J3
(cap 12), J4, J2 stage A, then J3 cap 6 and J2 stage B. Stop pod work when `rpbalance` would fall below $103, at $40
spent, or when the jobs are done, whichever comes first. The VPS runs ≤ 4 processes; literature downloads one at a
time. The run stops at the 72-hour hard stop (2026-10-08 04:56 UTC) or when every deliverable is written, whichever
comes first. Checkpoints in `STATUS.md` after each part.
