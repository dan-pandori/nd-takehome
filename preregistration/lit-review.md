# Pre-registration: lit-review (techniques from the literature we have not tried yet)

Written 2026-09-29 ≈ 03:35 UTC, before any paper was screened. Executor: agent:claude. No pods.

## Question
Which techniques that published provers and RL-for-reasoning work rely on, and that this project has not
used, have the highest expected value for moving `L*`, support expansion, or Stage-1 seed variance on the
3.2 M `lean_seq` / state-env setup?

## Design
- Screen 30–40 papers (abstract, method, main results table) in six clusters: search/value as the EI expert;
  self-generated curricula; support-expanding RL objectives; length/compositional generalisation in small
  transformers; truncate-and-resume error feedback; create-vs-elicit measurement.
- Read 8–12 in depth. Every cited claim is checked against the fetched source text (`lit_review/fetch.py`,
  arXiv HTML or PDF, grep of the section) and quoted with section/table/figure; unverifiable claims are
  marked unverified.
- Map each candidate onto real files/functions on the fork's `dan`, cost it, rank it.

## Expected results (falsifiable)
1. Top-ranked technique: **search as the EI expert over the state-env step environment** (best-first or
   MCTS with a learned value / log-prob score, HTPS / BFS-Prover / ExIt style). Falsified if, after reading,
   the evidence for search helping *training* (not only test-time pass rate) at fixed compute is weak enough
   that something else ranks first.
2. A **learnability-weighted / frontier curriculum** (sample targets where p(success) is intermediate;
   STP-style conjecturing) ranks in the top 3.
3. **Positional-encoding length-generalisation techniques** (position coupling, Abacus, NoPE) rank **low**,
   because our length frontier is in proof structure (depth, box nesting), not in raw sequence length beyond
   training; falsified if a source shows a transfer to structured, variable-format outputs like ours.
4. Pass@k-style objectives (Rewarding the Unlikely, pass@k training) make the shortlist, ranked below search.
5. At least one identifier the run brief gives "from memory" is wrong or needs correction.
6. ≥ 90 % of the claims I cite verify against the source text; the rest are marked unverified, none misquoted.

## Budget and stop rule
Pod budget $0.50 / 1 h registered as a guard; expected spend $0. Stop screening at 40 papers or when the
remaining clusters return no new candidate of relevance ≥ 2. Deliverables per the run brief.
