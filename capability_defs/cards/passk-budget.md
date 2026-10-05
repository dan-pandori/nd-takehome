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
- **The budget is tied to RL's own compute**, converted to base attempts (ladder GPU-seconds divided by the measured
  cost of one base attempt). *Revised after the critic pass (§9).* The headline budget is **K_eval-set**: RL's compute
  spread over the theorems being judged, i.e. "what if RL's GPU-seconds had been spent sampling the base on exactly
  the evaluation set":

  K_eval-set = ladder GPU-s / (N_eval × cost per base attempt),

  with N_eval = 322 (textbook72 + holdout250) and the cost measured on pend (3.6 ms per attempt on an A40, J2):
  ≈ 1.9 × 10⁴ attempts per theorem at r8 and ≈ 4.8 × 10⁴ at r16. J2's 16,384 nearly supplies it. Two reference
  budgets are reported beside it:
  - **K_per:** RL's compute per *training* target. It depends on how many targets RL trained on, which the judged
    theorems are not: 256 if counted in samples (8 rounds × 32), ≈ 780–1,400 if counted in GPU time.
  - **K_total:** all of RL's compute on one theorem. It can certify elicitation but never creation.

## 2. Decision rule

**Set level (the headline, after the critic).** Compare the RL model's solves at k_eval = 256 with the base's coverage
at the compute-matched K_eval-set, over the same theorems:

Δ_cov = #{t : R solves t at 256} − #{t : B solves t within K_eval-set}.

- RL **created coverage** if Δ_cov > 0 beyond the seed spread, on ≥ 2 / 3 seeds.
- RL **elicited** if the base's compute-matched coverage meets or exceeds RL's.

The theorems in the difference are the candidate created set. The test can come out either way.

**Per theorem (secondary).**

| verdict | rule |
|---|---|
| **created at K** | R solves t at k_eval, and UB95(p_B(t)) < 0.05 / K |
| **elicited at K** | p_B(t) ≥ 1 / K is certified, by the sampling lower bound or by `marginal-bracket` |
| **neither** | R does not solve t, or B already solves it at k_eval |
| **undetermined** | otherwise |

**Attribution.** The ladder also pretrains (≈ 476 M replay tokens). Every verdict is reported net of the replay-only
control (`rl-from-ckpt`'s c⟨s⟩_pend_r8: the same 8 rounds of fine-tuning with no RL proofs). It solves 16 / 18 / 24 of
the 86 / 77 / 77 hard theorems.

**Continuous version ("bits beyond search"):** β(t) = log₂ p_R(t) − log₂ p_B(t) − log₂ K. It does not agree with the cut
everywhere (§9), so report it as a separate scale.

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
  - J2 stage B: 65,536 attempts on the theorems still at 0. UB95 = 4.6 × 10⁻⁵ certifies "created" only for K ≤ ≈ 1,100
    (r8 K_per in GPU time at 6.4 ms, not at 3.6 ms or r16). About 1.5 A40-hours per seed.
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

**Strongest argument (critic): "a budget tied to RL's compute" is a menu of budgets, not one line, and the contested
theorems sit inside the menu.**
- K_per at r8 is 256 if RL's compute is counted in samples (8 rounds × 32 per target = k_eval, the equal-k case), 777 at
  6.4 ms per attempt, and 1,381 at 3.6 ms. It also scales with the number of *training* targets (4,495), and the judged
  theorems are not training targets.
- s0's 55 RL-solved hard theorems have known-proof estimates from e^−36.6 to e^−8.0 (median e^−15.7 ≈ 1 / K_total).
  `textbook_b98931f273313e2c32e7` (pend 1 / 17,152, r8 p̂ 0.90) is "created" at K_per and certified elicited at K_total.
- At K_total, certifying creation takes ≈ 2 × 10⁸ zero-success draws per theorem, so there the rule can only return
  elicited or undetermined.
- Secondary arguments:
  - *Attribution:* R is pend + ≈ 476 M replay tokens + RL. The replay-only control solves 16 / 18 / 24 of the 86 /
    77 / 77 hard theorems (e.g. `textbook_418e4b67e7e59d93fa6b` 146 / 512 against r8's 0.16).
  - *Certification arithmetic:* "created at K_per" needs 83k–124k zero-success draws, more than stage B's 65,536 at
    r16 and at 3.6 ms per attempt.
  - *Cut vs β:* the cut ignores p_R beyond one hit in 256 while K grows with RL's spend, so more RL can only weaken a
    verdict (`textbook_5758428c8c74f96345ad` rises 138× from r8 to r16 but can be certified only at r8).
- Smallest surviving change (critic): one set-level comparison at the experiment's own budget. Give base sampling the
  ladder's GPU-seconds over the same 322 evaluation theorems, and call it creation only if RL's solves at k_eval beat
  that compute-matched base coverage by more than seed noise.

**My answer: accepted; the card is revised as the critic proposes (§1–2).**
- The headline budget is **K_eval-set** = ladder GPU-s / (322 × 3.6 ms) ≈ 1.9–2.3 × 10⁴ (r8), 4.8–5.0 × 10⁴ (r16). It
  has no target-count denominator, and J2 stage A plus stage B (65,536 attempts on every RL-solved hard theorem)
  supply it.
- The decision is set level (Δ_cov), with the per-theorem verdicts secondary and every number reported net of the
  replay-only control. K_per and K_total are reported beside it, not used as creation budgets.
- β is kept as a separate continuous scale, not as "the rule without a cut".
- Certification at K_eval-set needs ≈ 60 K zero-success attempts per theorem; J9 buys it for 3 theorems per seed.
