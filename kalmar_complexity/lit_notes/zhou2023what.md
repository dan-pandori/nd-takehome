---
written_on: 2026-10-20
written_by: agent:claude (literature arm, kalmar-complexity)
papers:
  - zhou2023what
---

# Zhou et al. (2023; ICLR 2024), "What Algorithms can Transformers Learn? A Study in Length Generalization"

Source: arXiv 2310.16028v1 (read: §1–7 and App. F listings).

## Paper claims
- **RASP-Generalization Conjecture (abstract, §2).** "Transformers tend to length generalize on a task if the task can be solved by a short RASP program which works for all input lengths". The three conditions are realizability, simplicity (writable in RASP-L) and diversity.
  - "the above features are empirically correlated with: (1) generalization to longer lengths out-of-distribution, and (2) faster train optimization in-distribution".
  - The conjecture is "primarily phenomenological, as opposed to mechanistic".
- **Toy model (§1).** "Transformers tend to learn the shortest RASP-L program which fits the training set."
- **RASP-L (§3.2, App. E).** Causal RASP restricted to int8 values; indices only compared or shifted by ±1 (no index arithmetic); no loops; adds min/max aggregation. "each line of RASP-L compiles into at most one Transformer layer" (§1).
- **Results, Fig. 1a (exact match at +10 tokens over the training length):**
  - Count 100 %, mode 100 %, unique copy 96 %, sort 96 %.
  - Mode (hard) 0 %, repeat copy 0 %, addition 0 %, parity 0 %.
  - Reformatted "new" addition (index hints, reversed output) 100 %, and parity with a scratchpad 100 %.
  - A "natural" mode scratchpad hurts (Fig. 3c).
  - Training speed follows RASP-L difficulty in 3 comparisons (Fig. 6: forward vs reverse addition, parity scratchpads, mode with/without scratchpad).
- **Program sizes (App. F, my count of statements):**
  - Sort: 1 line, `kqv(x, x, x, gt, reduction='min')` (Listing 7).
  - Copy with unique tokens: 1 line, `induct(seq, seq, offset=1)`, using the library `induct` (Listing 6).
  - Mode: 3 lines (Listing 5).
  - Count: ≈ 7 statements (Listing 4).
  - Reverse-order addition with index hints: ≈ 26 statements plus 2 helpers (Listing 9, lines 18–56).
  - Forward-order addition: the patch (Listing 10) replaces 7 statements with 14, giving ≈ 33.
  - Parity without a scratchpad: no RASP-L program.
- **Limits stated (§7).** "RASP program length does not perfectly correspond to Transformer-complexity". Suggested refinements are "parallel depth" or the minimum weight norm. The minimum RASP-L length is likely intractable to compute, "similar … that Kolmogorov complexity is uncomputable".

## Our interpretation
- RASP-L is the most transformer-relevant program-length measure with published learnability evidence. That evidence is mostly binary (a short program exists or does not) and concerns length generalization. For in-distribution learning speed it rests on 3 pairwise comparisons.
- Kalmár on K12 is an in-distribution task: KAL-D fails exact execution in distribution. The conjecture's direct claim therefore does not apply. Its "faster train optimization" corollary and the scratchpad analysis do apply: a step is easy if its next-token function is a short, shallow RASP-L program given what is already written in the state.
- The scratchpad lesson (§5.2: "turning a next-token problem that requires n sequential steps into n next-token problems that are each only one step") predicts that Kalmár steps whose needed sub-results already appear in the state are easy. Steps that must re-derive a truth value from the formula (writing a true conjunction, choosing the true disjunct) are harder.
- Line counts are an imperfect proxy (one line ≠ one layer). The preregistration's plan to report both primitive-op count and attention depth matches the paper's own suggested refinement.

## Limits
Small task set (about 10 variants). Learned positional embeddings, packed contexts, and a training distribution tuned for diversity. No statistical test.
