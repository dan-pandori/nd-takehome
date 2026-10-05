# Card: the bracketed base solve probability

Families S + L (the bridge between sampling and likelihood). Slug `marginal-bracket`. Notation: `_FRAME.md`.

## 1. Definition, formally

The quantity is the base model's single-attempt solve probability p_B(t) = Σ_y π_B(y | t) V(t, y), bracketed from both
sides. No new modelling assumption is needed; each side is valid on its own.

- **Lower bound (likelihood).** LB(t) = Σ_{y ∈ F(t)} π_B(y | t).
  - F(t) is the set of distinct Lean-accepted proofs of t found by any model in any read: every pretraining checkpoint,
    every RL round, every seed, both caps, references, and the base's own large-k samples.
  - Each π_B(y | t) is teacher-forced at the sampler's temperature (T 0.8), with the 33 name bases marginalised.
  - LB holds deterministically: p_B is a sum of non-negative terms over all valid proofs, and F(t) is a subset of
    them.
  - With one name base scored, each term may be replaced by its own lower bound π_B(y | b = 0) / 33 (J1 stage 1).
- **Upper bound (sampling).** UB(t) is the one-sided 95 % Clopper–Pearson bound from every independent base attempt
  on t: draws x0, x1, x2 (and x4 for group C) at k 256 each, plus J2's 16,384 or 65,536.
- **Point estimate where the base succeeds often enough:** p̂ = c / n.
- **Importance-sampling estimate (optional).** For a large enough sample from R,
  p̂_IS(t) = (1/n) Σ_{i : y_i ∼ π_R} V(t, y_i) π_B(y_i) / π_R(y_i). It is unbiased when π_R covers the base's solution
  set, which holds for softmax policies.
- **RL's coverage by F:** Σ_{y ∈ F(t)} π_R(y | t) / p̂_R(t), the share of RL's success mass that the known proofs
  carry. This checks how complete F is.

## 2. Decision rule

At a budget K from `_FRAME.md` (K_per, K_total), for each theorem that R solves at k 256:

| verdict | rule |
|---|---|
| **elicited at K** | LB(t) ≥ 1 / K, or the sampling lower bound ≥ 1 / K |
| **created at K** | UB(t) < 0.05 / K |
| **undetermined** | neither |

The bracket's width, log UB − log LB, is reported for every theorem. It says how far the evidence is from a verdict.

## 3. Null or floor

- The same bracket for random initialisation: LB_init is computed in J1 (init is scored), and UB_init = 3 / n from init
  reads (0 solves).
- LB_init is about e^(−10³). The bracket puts random weights below any compute-tied budget by hundreds of orders of
  magnitude, so the random-weights objection is answered numerically.

## 4. How to compute it here

- **Inputs.** Existing reads, J1 (every known proof under init / pend / r8 / r16, ≈ 1.3 × 10⁵ proofs per seed) and J2
  (pend's large-k samples).
- **Cost.**
  - J1 stage 1 ≈ 0.4 A40-hours for all seeds.
  - J1 stage 2 (exact 33-base rescoring of the top proofs per theorem, plus every proof pend itself found in J2):
    ≈ 4,000 proofs per seed, about 20 min per seed.
  - J2 ≈ 1 A40-hour per seed (stage A).
  - Analysis: `cd_bracket.py`, CPU-seconds.
- **First numbers** (s0, stage 1, the deliberately loose b0 − ln 33 bound; `out/bracket.json`):
  - On 30 calibration theorems where pend's p is measurable, exp(LB₁) / p̂ has median 0.025 [IQR 0.020, 0.032]. With
    the ln 33 penalty removed that would be ≈ 0.8; stage 2 will measure it exactly.
  - The best single proof carries 66 % of the bound.
  - Of the 55 hard theorems that r8 solves (pend 0 / 512), 24 (44 %) are already certified elicited at K_total; 29 of
    55 (53 %) for r16.
  - None is certified either way at K_per.

## 5. Sensitivity

- **Temperature.** Use T 0.8 (the sampler's) for the bound that is compared with sampling budgets. At T 1.0 the bound
  describes the model's distribution, not the sampler's.
- **Decoding.** A guided decoder has a different p. Bracket it separately, or not at all: its probability of a proof
  is not a product of plain π terms.
- **Completeness of F.** LB grows as F grows; adding the base's own J2 successes matters most. F is drawn from every
  model, so LB is a lower bound whichever model found the proofs.
- **Representation.** The bracket is per interface (proof-state here). Whole-proof models need their own scores.
- **Renaming / premise order.** Bracket each prompt. A renaming class gets the minimum (for creation) or the maximum
  (for elicitation) over its members.
- **Noise.** LB has no sampling noise. UB has exact binomial noise. Across seeds, p_B differs by large factors
  (`support-state`: median p̂ 20× apart between two base seeds).

## 6. Failure modes

- **Name conditioning.** The scorer conditions on canonical names, not on the model's own sampled name tokens, so π_B
  is not exactly the sampler's probability (unquantified; `trajectory`). A bias here could move LB either way.
- **Creation is rarely certifiable** (≈ 60 K samples needed); most hard theorems at K_per may end "undetermined".
- **Truncation.** Read caps cut some attempts; UB is then an upper bound for the capped sampler, not the uncapped one.
- **Validity of F's members.** Every term must be a Lean-accepted proof. F is built only from proofs accepted by Lean
  on the literal sampled text. The canonical rendering is re-derived by `decompose` and must replay exactly, or the
  term is dropped (24 of 136,466 for s0).

## 7. Relations

- Makes `tf-proof-prob` (theorem level) and `passk-budget` decidable.
- LB ≥ max_y π_B(y) ≥ π_B(y_ref).
- Its elicited side implies "elicited" for `passk-budget`; its created side is the same rule.
- Its components feed `sharpen-expand` and `new-proof-new-theorem`.

## 8. Literature anchor

- **Wu & Hilton 2024 (2410.13211v2).** Importance sampling gives "an unbiased estimator for the true probability"
  (Sec. 3.1). "As long as the required importance sampling ratios can be computed, any method for red-teaming can be
  turned into an importance sampling method" (Sec. 6.2).
- **Zhao et al. 2024 (2404.17546).** Sequential Monte Carlo bounds on the probability of satisfying a constraint
  (screened by L3).
- **Brown et al. 2024 and Kazdan et al. 2025.** Why sampling alone cannot resolve small p (`passk-budget`).
- **Chen & Foster et al.'s coverage principle** (earlier review). Coverage is sequence-level mass on correct outputs.
- **Our construction.** The deterministic lower bound by summing known proofs is our own. The literature we found uses
  importance sampling or SMC estimates, not this bound.

## 9. Critic's verdict

*(pending)*
