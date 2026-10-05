# Shared frame for the definition cards (read this first)

Every card uses the notation and budgets below, so their decision rules can be compared.

## Objects

- **Theorem** t: a propositional sequent. **Proof** y: a sequence of actions (proof-state models, `lean_staten`) or a
  whole Lean proof text (`lean_seq`). **V(t, y) ∈ {0, 1}**: Lean 4 accepts y as a proof of t (Lean alone decides).
- **Model** θ with policy π_θ(y | t): the probability that one plain attempt writes y. For proof-state models this is the
  product over actions of π_θ(action | state), with the names the environment assigns not scored and the sampler's 33
  name bases marginalised (`tj_score.py`).
- **Solve probability** p_θ(t) = Σ_y π_θ(y | t) V(t, y): the probability that one attempt succeeds. It is a sum over
  *every* valid proof, so the probability of any single proof is a lower bound on it.
- **pass@k** = 1 − (1 − p)^k; unbiased estimate from n ≥ k attempts with c successes: 1 − C(n−c, k) / C(n, k)
  (Chen et al. 2021). **k-to-solve** = 1 / p (expected attempts to the first success).
- **Models compared:** π_0 = random initialisation (step 0), π_B = base (end of pretraining, "pend"), π_R = after RL
  (r8 or r16). A **null** is a model that should have no capability: π_0, or a policy uniform over the grammar's legal
  next tokens.

## Budgets (the answer to "at some k even random weights solve it")

Every sampling-based or probability-based rule needs a budget K: "within reach" means p_θ(t) ≥ 1/K, i.e. the model
solves t with probability ≥ 1 − 1/e ≈ 0.63 if given K attempts. The cards use four budgets, from most to least
generous to RL:

| budget | meaning | value (cap-12 r8, per seed) |
|---|---|---|
| k_eval | the evaluation budget, equal for base and RL (Yue et al.) | 256 |
| K_per | RL's compute per training target, converted to base attempts | ≈ 10³ (to be measured from compute rows) |
| K_total | **all** of RL's compute, given to one theorem as base attempts | ≈ 10⁶–10⁷ (to be measured) |
| K_null | attempts random weights need: 1 / p_0(t) | ≈ e^(hundreds to thousands) |

K_null ≫ K_total for every theorem we have, so tying K to RL's compute settles the random-weights objection: random
weights solve nothing within any budget RL itself could afford. The real question is where the **base** sits relative
to K_per and K_total.

## The three verdicts

For a pair (base, RL) and a theorem or family:
- **created (at budget K):** the base cannot solve it within K (p_B < 0.05 / K, i.e. < 5 % chance in K attempts) and
  RL can at the evaluation budget (pass@k_eval ≥ τ).
- **elicited (at budget K):** RL solves it and the base could too within K (p_B ≥ 1 / K) — RL turned something the
  base could reach with compute into default behaviour.
- **neither:** RL does not solve it, or the base already solves it at k_eval.
- **undetermined:** the evidence does not place p_B on either side of the line (common: certifying p_B < 0.05 / K by
  sampling needs ≈ 60 K attempts with no success).

## Bracketing p_B (used by several cards)

- **Upper bound:** n base attempts with c successes give a one-sided 95 % Clopper–Pearson bound; with c = 0 it is
  ≈ 3 / n.
- **Lower bound:** Σ_{y ∈ F(t)} π_B(y | t), summed over F(t), the set of distinct Lean-accepted proofs of t that any model
  ever found. It holds deterministically, with no sampling error, because p_B is a sum over all valid proofs.

## Families

S sampling / support · L likelihood · N null-relative · E elicitation cost · T transfer / invariance · R reliability ·
P psychometric · C compute equivalence · D distribution shift / update size · M mechanistic · X causal intervention.
