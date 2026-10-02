# lit-review-2: create vs elicit, exploration outside support, model organisms (executor, 2026-10-02)

Deliverables: `lit_review_2/REVIEW.md`, 11 notes in `lit_review_2/notes/`, `claims.md` (110 ledger claims + 33-claim
independent re-check, all verbatim), `screened.md`, `to_add_to_zotero.md` (47 ids). Pre-registration `d024bd0e`.
No pods, no model runs, no new numbers.

**Expected vs outcome.** 5 of 7 pre-registered expectations held. #4 was partly falsified: out-of-support exploration
also comes from heuristic injection, oracle prefixes and LLM evolution, not only from tabula-rasa search. #7 was not
met as an error: our documents needed qualifications, not corrections. The screen covered 51 papers, more than the
40 planned (disclosed in `log.md`).

**Findings.**
- The field's standard is equal-k pass@k (Yue). Our A/B/C split falls below it: the base is read only at k 256, and
  the threshold was calibrated post hoc. The fix is reads only: an equal-budget re-read plus a pre-registered
  coverage threshold.
- The closest published organism (2607.07646v1, from-scratch rewrite grammar) shows RL solving what the base misses
  at pass@1024, and RFT (our ladder's family) plateauing. It reports no likelihoods.
- For group C, the literature supports reference-prefix starts and exploration kept on throughout. That suggests
  revisions to proposal 20, E2 and E3 (DeepHOL-Zero, Go-Explore, POPE).
