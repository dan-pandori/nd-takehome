# run radical-scoping — departures for the capability-emergence question (draft for Dan)

Deliverable: [`radical_scoping/SCOPING.md`](radical_scoping/SCOPING.md). CPU pilots, $0 pods. Numbers:
`numbers.md` § radical-scoping. No model was trained or sampled.

**Recommendation.**
1. Rule knockout × exploration: an `Or.elim`-free Stage-1, with ε-legal-action exploration vs none. Run it as
   proposal 20's target.
2. FOL with function symbols, as the domain departure.

Induction arithmetic is the follow-on; library mining and EDL are cheap measures; self-play is dropped.

**Pilots.**
- **FOL:** the June sprint's generator runs unchanged.
  - Lean 4 core accepts 1,000 / 1,000 of its proofs, rendered by a new translator.
  - All 272 mutants are rejected.
  - Lean and the verifier agree on 577 / 578 mutants.
  - Gaps: no function symbols, no ∃-elim in the sampler.
- **Knockout:** ORE is in 1.47 % of cap-6 Stage-1 proofs. 14 textbook72 problems require it (minlen, bound 12).
- **Induction:** custom-`N` induction proofs check in Lean core; `simp`, `omega` and `decide` fail on them.

**Expected vs outcome.** Every pre-registered expectation held: FOL Lean acceptance 100 % (≥ 90 %); ORE 1.47 %
(1–10 %); DN 8.36 % (5–25 %); 98.5 % of the set retained (≥ 70 %); a required family exists; ranking as predicted.
