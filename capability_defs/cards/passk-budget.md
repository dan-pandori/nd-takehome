# Card: pass@k at a budget tied to RL's compute (Dan's notion (b), made strict)

Family S (sampling). Slug `passk-budget`. Notation: `_FRAME.md`.

## 1. Definition, formally

- **Quantity.** The single-attempt solve probability p_θ(t) of model θ on theorem t under a fixed protocol (plain
  sampling, T 0.8, the read caps `max_steps` 96 / `max_action` 512, Lean alone judges). From n attempts with c
  successes:
  - p̂ = c / n, with a one-sided 95 % Clopper–Pearson interval; with c = 0 the upper bound is ≈ 3 / n.
  - pass@k for k ≤ n by the unbiased estimator 1 − C(n − c, k) / C(n, k) (Chen et al. 2021, Eq. 1).
  - For k > n **no unbiased per-theorem estimate exists**. Beyond the sampled n, use the interval on p, the
    likelihood lower bound of `marginal-bracket`, or (for set-level statements only) a fitted distribution of p over
    theorems (beta-binomial or zero-inflated; Kazdan et al. 2025; Schaeffer et al. 2025).
- **k-to-solve** K_θ(t) = 1 / p_θ(t), the expected number of attempts to the first success. **Compute-to-solve** =
  K_θ(t) × the cost of one attempt. Measured for pend on hard theorems: 3.6 ms of A40 time per attempt (J2 chunk 0:
  131,072 attempts in 470 s).
- **The capability statement:** "θ can solve t within budget K" ⟺ p_θ(t) ≥ 1 / K, i.e. at least a 63 % chance of a
  proof in K attempts.
- **The budget is tied to RL's own compute**, converted to base attempts: ladder GPU-seconds divided by the measured
  cost of one read attempt (`cd_defs.budgets`; trajectory / rl-continue compute rows).
  - **K_per:** RL's compute per training target. Cap 12: 731–954 at r8 and 1,712–2,064 at r16 (seed range).
  - **K_total:** all of RL's compute given to this one theorem. Cap 12: 3.3–4.3 × 10⁶ at r8 and 7.7–9.3 × 10⁶ at r16.

## 2. Decision rule

For base B (pend) and RL model R (r8 or r16), per theorem:

| verdict | rule |
|---|---|
| **created at K** | R solves t at the evaluation budget (≥ 1 success in 256, or a stated p̂_R threshold), and the 95 % upper bound on p_B(t) is < 0.05 / K, i.e. the base would have < 5 % chance in K attempts |
| **elicited at K** | R solves t, and p_B(t) ≥ 1 / K is certified: the 95 % lower bound from sampling, or the `marginal-bracket` likelihood bound, is ≥ 1 / K |
| **neither** | R does not solve t, or B already solves it at k_eval = 256 |
| **undetermined** | otherwise |

- Report both budgets. **K_per answers "was RL necessary at matched compute?"** and is the headline. **K_total is the
  conservative bar:** creation there means not even all of RL's compute spent on base samples of this one theorem
  would find a proof.
- **Continuous version ("bits beyond search"):** β(t) = log₂ p_R(t) − log₂ p_B(t) − log₂ K. β > 0 means RL did better
  on t than spending its compute on base samples would. This is the same rule without a cut, and it supports an
  elicitation curve (the share created as a function of K).

## 3. Null or floor

- Random initialisation is the null. At init, 96 % of attempts fail to parse; the rl-from-ckpt ladder started at
  step 0 accepted 0 of 287,680 attempts; and init's teacher-forced log p of a reference proof is about −200 nats in
  its worst step alone (trajectory).
- So K_null = 1 / p_0(t) is of order e^(hundreds to thousands), while K_total ≈ e^15.
- **Dan's objection ("some k makes random weights solve everything") is true but irrelevant once K is tied to a real
  compute budget.** Random weights solve nothing within any budget RL itself could afford. The line that matters is
  where the base sits relative to K_per and K_total.

## 4. How to compute it here

- **Data.**
  - Existing per-theorem reads: pend and r8 at x0 + x1 (+ mcts-a x2, and x4 for C), k 256 each; r16 at x1.
  - J2: pend at 16,384 attempts on each seed's hard RL-solved theorems (57 / 59 / 55), and at 4,096 on 30
    calibration theorems per seed. About 1 A40-hour per seed, ≈ $0.5.
  - J2 stage B: 65,536 attempts on the theorems still at 0, which is what certifying "created at K_per" needs
    (UB95 = 4.6 × 10⁻⁵ < 0.05 / K_per). About 1.5 A40-hours per seed.
- **Analysis.** `capability_defs/analysis/cd_bracket.py` and `cd_defs.py`, a few CPU-seconds.
- **Structural limit.** Certifying creation at K_total needs ≈ 60 K_total ≈ 2 × 10⁸ base attempts per theorem. That
  is ≈ 200 A40-hours per theorem, so creation at K_total cannot be certified by sampling. Only elicitation can be
  certified there.

## 5. Sensitivity

- **Temperature and decoding.** p depends on T. Chen et al. find higher T better at large k (Sec. 3.3). Guided
  sampling (step-checked redraws) raised solves by 5–9 pp at matched tokens (`guided-tts`). The protocol must be named,
  and plain and guided are reported separately (AGENT_POLICY).
- **k and thresholds.** K_per and K_total differ by a factor of 4,495 (the number of training targets), and verdicts
  near either line flip. Hard theorems at pend sit at p ≈ 10⁻⁵–10⁻³ (J2 chunk 0: 0, 0, 0, 0, 1, 1, 2 and 10 successes
  in 16,384), which is exactly the region around 1 / K_per ≈ 1.3 × 10⁻³.
- **Representation.** The same 29 theorems were unreachable for the whole-proof base in 4 × 10⁵ attempts but reached by
  the proof-state base (`support-state`). p is a property of (model, interface, decoder).
- **Renaming, premise order, curried forms.** p is measured per prompt. A capability claim about a theorem should
  average p over its renaming class. The sampler's 33 name bases are already averaged over.
- **Seed and redraw noise.** Binomial sampling error is exact and small at large n. Seed-to-seed variation is large:
  for the k 256 version, the Jaccard of the created sets is 0.68–0.78 between redraws but 0.34–0.39 between training
  seeds (`out/defs_c12.txt`).

## 6. Failure modes

- **Budget choice is a modelling decision.** Should K count sampling only, or sampling plus training? Per target or in
  total? Should it include the replay pretraining that the ladder also does (≈ 476 M tokens, `rl-from-ckpt`)? Each
  choice moves the line by orders of magnitude.
- **Group selection.** If the created set is defined on one draw and p_B is estimated on the same draw, p_B is biased
  down. Define on one draw and estimate on an independent one.
- **Truncation caps** bias p down (C strata 1–19 % cut off in earlier runs; ≤ 3 per 16,384 in J2).
- **Population extrapolation cannot settle single theorems.** A beta fit cannot tell impossible from merely hard
  (Kazdan et al. App. D.2).
- **Creation at large K is uncertifiable by sampling** (§4): the rule's creation side is mostly "undetermined".

## 7. Relations

- Generalises `passk-equal-k` (K = k_eval = 256).
- Its elicited side is implied by `marginal-bracket` (the likelihood lower bound).
- `capability-vs-propensity` replaces plain sampling with the best elicitation method within the budget.
- `compute-equivalent` prices RL in pretraining compute instead of in base samples.
- `chain-reachability` explains how RL can be "created" here while every round is elicited relative to the previous
  round.

## 8. Literature anchor

- **Chen et al. 2021 (2107.03374v2).**
  - The unbiased estimator: Sec. 2.1, Eq. 1.
  - The plug-in estimator 1 − (1 − p̂)^k "results in a consistent underestimate" (App. A).
- **Brown et al. 2024 (2407.21787v3).**
  - "With unlimited samples, any model that assigns a non-zero probability to every sequence will achieve perfect
    coverage" and "repeated sampling is only practical if we can improve coverage with a feasible budget" (Sec. 1).
  - Coverage grows over four orders of magnitude of samples (abstract).
- **Schaeffer et al. 2025 (2502.17578v1).** Aggregate pass@k is a power law iff the distribution of p near 0 is one
  (Sec. 3, Thm 3.1–3.2); the left tail has to be fitted to the share of problems in (0, 1 / n) (Sec. 5).
- **Kazdan et al. 2025 (2510.05197v1).** Chen's estimators are "only defined when the number of samples taken for each
  problem is greater than or equal to the number of attempts k" (Sec. 3.1); impossible vs hard (App. D.2).
- **Hu et al. 2023 (2310.03262v3), PassUntil.** Sample until r successes; PU = r / K is the MLE (Sec. 4.1); "designed
  to be applicable when a random baseline achieves P(s)=0" (Limitations).
- **Earlier reviews:** Yue et al. 2025 (equal-k), Chen–Foster coverage (coverage ≈ mass ≥ 1 / k).
- All locations verified in `capability_defs/lit/_claims_L1.md`.

## 9. Critic's verdict

*(pending — filled in after the critic pass)*
