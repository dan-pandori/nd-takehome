---
written_on: 2026-10-20
written_by: agent:claude (literature arm, kalmar-complexity)
papers:
  - whitney2020evaluating
---

# Whitney, Song, Brandfonbrener, Altosaar & Cho (2020), "Evaluating representations by the complexity of learning low-loss predictors"

Source: arXiv 2009.07368 (read: §1–5).

## Paper claims
- **Loss-data framework (§2).** Validation accuracy (VA), mutual information (MI) and MDL are slices or integrals of the validation-loss vs dataset-size curve along the data axis. The proposed measures are slices or integrals along the loss axis.
- **Size dependence (§3.1).** VA and MDL depend on the evaluation-set size n, so "the ranking of representations given by these evaluation metrics can change as n increases". The parity example: a noisy-label representation wins at n ≪ d, raw bits win at n ≫ d.
- **Definitions (§4).**
  - Def. 1: SDL = Σ_{i≥1} [L(A,i) − H(Y|X)].
  - Def. 2: SDL_ε = Σ_i [L(A,i) − ε]₊.
  - Def. 3: εSC = min{n : L(A,n) ≤ ε}.
  - "When the true distribution p is a delta, the entire length of a code under p̂ is surplus" (§4.1).
  - If ε is not reached with the available data, the estimate "is only a lower bound" (§4.1). Choose ε as part of the specification (§4.3).
- **Table 1 (MNIST; their code lengths are in nats, footnote 1).**
  - n = 60: MDL 122.75 (CIFAR representation) / 147.34 (pixels) / 93.8 (VAE), so the VAE ranks best.
  - n = 31,936: MDL 2,165.1 / 5,001.57 / 4,898.37, so the CIFAR representation ranks best.
  - SDL at ε = 0.1: 260.6 / 1,837.08 / > 1,704.77. εSC at ε = 0.1: 3,395 / 31,936 / > 31,936.

## Our interpretation
- Kalmár's next action is a deterministic function of the proof state, so H(Y|X) = 0. With ε = 0, SDL equals the whole prequential code. With finite data (B2: 16,384 theorems) any SDL is a lower bound unless the loss curve has flattened.
- **Report at a stated ε and a stated n.** Comparisons between Kalmár, K12 and eval, and between B1 (155,000 theorems) and B2 (16,384), are only meaningful at matched n or at a common tolerance ε. Candidate tolerances: the per-token loss at which teacher-forced agreement reaches 95 %, or the loss of the final KAL-D.
- εSC per step type (the number of theorems before that step type's loss falls below ε) is a cheap, interpretable companion to bits per occurrence.

## Limits
Written for representation evaluation with probes. It assumes monotone learning curves (L(A, i+1) ≤ L(A, i)).
