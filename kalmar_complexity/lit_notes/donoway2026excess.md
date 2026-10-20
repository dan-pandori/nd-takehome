---
written_on: 2026-10-20
written_by: agent:claude (literature arm, kalmar-complexity)
papers:
  - donoway2026excess
---

# Donoway, Joren, Roger & Leike (2026), "Excess Description Length of Learning Generalizable Predictors"

Source: arXiv 2601.04728v1 (read: §1–7 in full, proofs skimmed). This extends lit-review-2's note `notes/donoway2026-edl.md`, which read §1, 5 and 7. The empirical companion that the earlier note could not find is **donoway2026bits** (see that note).

## Paper claims
- **Def. 3.1 (eq. 6).** Prequential MDL = Σ_i ℓ(θ_{i−1}; x_i, y_i), with batch losses taken before the update. The order matters, and MDLs should be compared under the same ordering (§3.1).
- **Def. 3.2 (eq. 7).** EDL = MDL − n·L_test(θ*), using the **test loss** of the final model, "whether by convergence, early stopping, or a fixed compute budget". Equivalently EDL = Σ_i [ℓ(θ_{i−1}) − L_test(θ*)] (eq. 9).
- **Normalizations (§3.4).** Per example, per token (label tokens), per trainable parameter.
- **§3.5 (eq. 10).** EDL = SDL + n·(L* − L_test(θ*)) ≤ SDL, with equality when the learner reaches the optimum.
- **Thm 4.2.** E[EDL] ≥ 0 for "population-monotonic" algorithms. The condition may be violated by "Large learning rates that cause oscillation" or by training far past early stopping (Def. 4.1, Remark 4.3).
- **Thm 4.6.** EDL → SDL under consistency. Rates are given for finite and parametric classes; "We do not claim rates for neural networks" (Remark 4.7).
- **Thm 4.8.** E[EDL]/n bounds the improvement attributable to learning during training.
- **Prop. 4.9.** EDL depends on the training algorithm. "When comparing EDL across settings, the algorithm should be held fixed or explicitly varied".
- **Toy models (§5):**
  - Random labels give EDL ≈ 0 (§5.1).
  - Hypothesis collapse (Prop. 5.2): one example contributes at most min(log|Y|, log m) bits to EDL. "the model can gain at most as much generalizable information as the train data contains (i.e., EDL = MDL)".
  - Coupon-collector coverage (Prop. 5.4): EDL accelerates as k → n·log n.
  - Format learning (Prop. 5.5): early transients; "score only designated output tokens".
- **Parameter capacity (§6.4).** Elicitation ≈ 0.01–0.1 bits/param, teaching ≈ 1+ bits/param ("see companion empirical paper").
- **Limitations (§7.2).** Algorithm dependence; "not a semantic measure"; supervised fine-tuning only; simplified toy models.

## Our interpretation
- **B1's residual.** The definition uses held-out loss, so B1's option (b) (val300 loss of the final model) is EDL proper. Option (a) (final train loss) gives a larger number that also counts memorized bits. Report (b) as primary and (a) as an upper variant.
- **Monotonicity risk.** KAL-D's learning rate is still high at the end of epoch 1 (preregistration). Thm 4.2's population-monotonicity can fail under oscillation, so B1's sign and size are not guaranteed. Report the logged loss curve's non-monotone segments.
- **Coverage.** K12-Kalmár's step-type mix has rare step types (frequency baseline), which is a coverage problem. Prop. 5.4 predicts that per-type EDL accelerates only once rare types have been seen enough times. This is consistent with the preregistered "teaching" (rise-then-fall) shape.
- **Format.** The action format (template tokens) is learned early. Scoring only content tokens (formulas, pointers) separates format from capability bits.

## Limits
A theory paper with conceptual toy models. Its setting is fine-tuning of pretrained models; our setting is training from scratch, which is the "teaching" extreme.
