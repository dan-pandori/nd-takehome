---
written_on: 2026-10-20
written_by: agent:claude (literature arm, kalmar-complexity)
papers:
  - voita2020information
---

# Voita & Titov (2020), "Information-Theoretic Probing with Minimum Description Length" (EMNLP 2020)

Source: arXiv 2003.12298 (read: §1–3 in full, §4 skimmed).

## Paper claims
- **Online (prequential) code (§2.2.2, eq. 4).** L_online = t₁·log₂K − Σ_i log₂ p_θi(y over block i+1). Footnote 4: "the timesteps correspond to 0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.25, 12.5, 25, 50, 100 percent of the dataset". "The online code is related to the area under the learning curve."
- **Model cost (§2.3).** "we can still evaluate model cost by interpreting the difference between the cross-entropy of the model trained on all data and online codelength as the cost of the model".
- **Table 2 (POS tagging, 950,028 training targets; kbits; linguistic task / control task):**
  - Layer 0: accuracy 93.7 / **96.3 %**, online code **173 / 302**.
  - Layer 1: 97.5 / 91.9 %, online code 96 / 515.
  - Layer 2: 97.3 / 89.4 %, online code 115 / 717.
  - "for LAYER 0, accuracy for the control task is higher, but the code is twice longer than for the linguistic task". "codelength characterizes how hard it is to achieve this accuracy" (§3.2).
- Variational and online codes agree in trends. Results are stable across seeds and probe settings (§3.3).

## Our interpretation
- KAL-D's 94–95 % teacher-forced step agreement says little about how much had to be learned. Code length can rank two tasks in the opposite order to accuracy. This supports reporting B2 bits per step type next to per-step-type accuracy, rather than inferring difficulty from accuracy.
- Their block schedule (0.1 % → 100 %, doubling) is close to B2's 64 → 16,384 theorems (0.4 % → 100 %).

## Limits
Probing: small classifiers on frozen representations, with control tasks defined over word types. This is not a from-scratch generative policy, and the labels are not deterministic functions of the input.
