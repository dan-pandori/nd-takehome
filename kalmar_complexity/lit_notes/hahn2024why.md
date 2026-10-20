---
written_on: 2026-10-20
written_by: agent:claude (literature arm, kalmar-complexity)
papers:
  - hahn2024why
---

# Hahn & Rofin (2024), "Why are Sensitive Functions Hard for Transformers?" (ACL 2024)

Source: arXiv 2402.09963v4 (read: §1–7, theorem statements; proofs not checked).

## Paper claims
- **Abstract.** "Transformers whose output is sensitive to many parts of the input string inhabit isolated points in parameter space, leading to a low-sensitivity bias in generalization".
- **Def. 3 (§3).** Average sensitivity as_n(f) is the mean over inputs of the number of single-bit flips that change f (total influence). It is related to the degree profile by as_n(f) = Σ_i i·d_i (eq. 17).
- **Thm 6 (§5).** For a transformer with d > 12L: lim_{ρ→0} liminf_n L_{ρ,n}(T) ≥ liminf_n as_n(T)/(2n) − L·exp(−Ω(d)).
  - "when as_n(T_θ) ∼ n, then even tiny perturbations to the parameters will, in expectation, lead to a substantial change in predictions on long inputs". The Hessian at such minima has unboundedly large entries.
  - "For functions with sublinear average sensitivity, Theorem 6 entails no nontrivial lower bound on sharpness" (§6).
- **Thm 7 (§6).** "Simulating an automaton with scratchpad has sensitivity O(1) for each autoregressive step."
- **Experiments (§7, Fig. 1).** Sharpness grows with input length for PARITY but not for MAJORITY.
- The paper stresses a "disconnect between expressive capacity and learnability".

## Our interpretation
- For Kalmár, a step's next action is a function of the proof state. Its sensitivity is how many state positions (atoms in the branch valuation, cited lines, formula symbols) can flip the action. This can be estimated with the builder: perturb one position, re-run the builder, and see whether the action changes. It is a literature-backed "computational demand" predictor that complements the preregistration's evaluation height and declared-formula length.
- Thm 7 says sensitivity collapses when intermediate results are written down. This predicts that the hard step types are those where the proof does *not* already contain the sub-results the action depends on.

## Limits
Asymptotic in input length n and stated for Boolean inputs. The experiments are encoder-only transformers fitting fixed-length functions. No sample-complexity or bits estimate. At K12 sizes (short states) the asymptotic bound may be loose.
