# run lit-review — techniques from the literature we have not tried (2026-09-29)

No pods, no training, no counts. Deliverable: `lit_review/REVIEW.md` (ranked shortlist, rejections,
create-vs-elicit measurements, 58-paper screened table), 23 notes in `lit_review/notes/`,
`lit_review/to_add_to_zotero.md` (56 identifiers). Pre-registration `preregistration/lit-review.md` (`dae83e61`).

**Shortlist** (REVIEW.md §a):
1. Search as the EI expert in the state env (best-first, length-normalised; minimal-proof targets).
2. Frontier target supply: mutated or extended solved proofs and failed-attempt subgoals, filtered to p̂ ∈ (0, 1/4].
3. Support-expanding GRPO advantages (unlikeliness, pass@k, distinct-proof bonus).
4. Transductive EI on textbook theorems with programmatic variants.
5. A steps-to-go value token (after #1).
6. EI proof selection by least-likely proof.

**Do first:** score EI-found proofs of base-unreached theorems step by step under the base (§c1). It needs
no sampling and speaks directly to "new moves vs compounding reliability".

**Expectations vs outcomes.**
- Search ranked first, positional-encoding tricks ranked low, and pass@k objectives made the list: as expected.
- A learnability curriculum in the top 3: **wrong**. Ladder-A's T2 / T4 already did that and it did not help,
  so target *supply* replaced it.
- At least one wrong identifier: **wrong**. Every arXiv id was right; only metadata needed fixing.
- ≥ 90 % of claims verify: my independent re-check found 32 of 33 verified, and the one number not found is
  not cited.

**Main literature gap.** No paper compares a search-trained apprentice with a sampling-trained one at matched
compute, evaluated without search. We can run that experiment.

No checkpoints, artifacts or data, so nothing to upload.
