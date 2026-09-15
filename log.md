# log.md — dated log (UTC), in order, including dead ends

- 2026-09-15 03:17  Start. Read README, spec, verifier, validation set. Pod: 1×A40, torch 2.8 cu128, 96 cores.
- 03:25  Design decisions (written before any training):
  - Generator: forward random rule application with random box structure; premises may be introduced *lazily* when a rule needs a formula that is not available (this is what makes premises fit together, e.g. `(P>Q), P |- Q`); ORE second branch uses a goal-completion routine that never fails (falls back to a lazy premise). Every proof is dependency-pruned (only lines the conclusion transitively cites are kept) and then verified with nd_verify. Not a search: there is no target given to it and no backtracking.
  - Tokenizer: one symbol per token. Two modes to compare in Stage 1: `rel` (cite "k lines back" as `B<k>`, line numbers dropped and regenerated at decode) and `abs` (keep `N<i>`, but shift every proof by a random start offset during training so that N1..N64 are all trained tokens; the verifier accepts any start index). Hypothesis: in `abs` mode citing is *copying* an index token that is in context, which is length-agnostic; in `rel` mode the model must count line distance, and B7+ are never seen under cap 6. Both cheap; pick by evidence.
  - Positional scheme: RoPE (no learned absolute positions, so no untrained position rows beyond Stage-1 sequence lengths).
  - Splits: disjoint by atom-renaming class (stricter than by theorem string), validation-36 renaming classes removed from every training pool.
