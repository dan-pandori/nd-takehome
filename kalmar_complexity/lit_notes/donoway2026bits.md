---
written_on: 2026-10-20
written_by: agent:claude (literature arm, kalmar-complexity)
papers:
  - donoway2026bits
---

# Donoway, Joren, DeWeese, Perez, Schulman, Roger & Leike (2026), "Bits That Count: Quantifying and Predicting Capabilities of Language Models" (ICML 2026, PMLR 306:26127–26151)

Source: https://proceedings.mlr.press/v306/donoway26a.html (PDF read: §1–6, figure captions; appendices not read). This is the empirical companion that donoway2026excess cites. The nd-rl bib entry `donowayQuantifyingElicitationLatent` (NeurIPS 2025) is a different, earlier paper on trained-parameter counts. Its abstract does not mention EDL.

## Paper claims
- **Abstract.** "elicitation requires orders of magnitude less information than teaching to comparable performance". "a few bits in a single example—can unlock large fractions of models' maximum performance when capabilities are elicited".
- **Protocol (§2):**
  - §2.1: loss "only on designated label tokens".
  - §2.2: MDL is the pre-update batch loss summed over the first epoch. Footnote 1: "Accumulation over additional epochs would correspond to encoding redundant information".
  - §2.3: EDL = MDL − n·L_test(θ*). It "distinguishes generalization from memorization by excluding the generalization gap".
  - §2.5: "for multi-epoch training, MDL is computed only on the first epoch …, while test loss is computed using the final trained model (arbitrary epochs)". The same token masking applies to train and test.
- **Teaching (§4.2).** TinyStories-1B, which "must learn addition/subtraction from scratch", shows EDL per token entering "a phase of increasing returns", then diminishing returns once capability or capacity saturates. Elicitation (Llama 3.2 1B) shows monotone decrease. "The EDL learned per token remains over an order of magnitude smaller for Llama than for TinyStories variants" (§4.4).
- **Causal interventions (§5).** Pre-teaching multiplication via operator notation moves the capacity knee from EDL/P* ≈ **1.02 bits/param** (teaching) to ≈ **0.05** (elicitation), a 20-fold shift. Out-of-distribution pre-teaching (addition/subtraction → multiplication) does not: ≈ 1.56 bits/param.
- **Capacity (§1, §6).** "elicitation saturates around 0.01–0.1 bits per trainable parameter or fewer, while teaching requires roughly 1 bit per parameter or more".

## Evidence
Models: Llama 3.2 1B/3B, Llama 3.1 8B, Qwen2.5 1.5B/14B/32B, and TinyStories-1B (Llama 3.2 1B architecture). Tasks: DeepMind Mathematics subsets, R1 reasoning traces, Alpaca, BoolQ, ARC. LoRA ranks 1–512, with rank 512 as the full fine-tuning reference.

## Our interpretation
- B1 is this protocol: first-epoch MDL, residual from the final model's held-out loss (B1's option (b)), action/label tokens only.
- **Prediction for KAL-D (from scratch = teaching).** EDL/token should rise before it falls (the preregistered B2 shape). If the ~1 bit per trainable parameter knee carries over to a dense 9.56 M-parameter model, the absorbed bits saturate around 10⁷. This is a scale reference, not a bound. Their P counts LoRA adapter parameters on top of a pretrained model.

## Limits
Fine-tuning of pretrained models of ≥ 1 B parameters. The capacity thresholds are for LoRA adapters. The appendices (Tables 5–10, I.x) were not read.
