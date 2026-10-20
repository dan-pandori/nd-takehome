- **Kalmár under the small learners:**
  - Over 16,384 theorems S codes 3.37 / 3.38 × 10^6 bits (EDL 1.32 / 1.46 × 10^6, seeds 0 / 1); M 1.69 / 1.77 × 10^6
    (EDL 1.10 / 1.08 × 10^6).
  - Over 8,192 theorems (the common prefix): S 2.35 / 2.44, M 1.40 / 1.44, L 1.37 × 10^6.
  - M and L are ≈ 40 % below S, far beyond the S and M seed spreads (3.8 %, 3.5 %). L vs M (1.5–5 %) is inside the
    spread: not resolved.
- **Absorbed bits:** EDL is 1.06–1.46 × 10^6, i.e. **195–270× the 5,443-bit BLC program**.
- **The asymptote is a floor that data barely moves.**
  - Held-out code after the last block: S 0.071–0.076, M 0.022–0.026, L 0.023 bits/token.
  - M trained on 16,384 theorems (10 % of K12) ends where KAL-D ends (9.6 M, all 155,000, 3.7 epochs): 0.0235
    bits/token held-out.
- **Reference tasks** (v2 protocol; one seed), over 16,384 theorems:
  - K12: prequential 3.9–6.4 × 10^5, EDL 1.8–3.2 × 10^5;
  - eval: 1.6–1.8 × 10^5, EDL 0.8–1.5 × 10^5.
  - Ordering Kalmár > K12 > eval, at every size.
  - Per theorem at 16,384 theorems: Kalmár 66–89 absorbed bits (S, M), K12 11–20, eval 5–9.
- **Shape** (excess bits per token by block, `b2_summary.json`):
  - Kalmár and K12 fall monotonically: Kalmár 0.9 → 0.2 bits/token after 128 theorems, then near 0.
  - eval plateaus at ≈ 0.28–0.35 for 6–8 blocks before falling, and only size M breaks through within the budget.
- **By step type** (`artifacts/kc/b2_per_type_table.json`; per loss token over the coded blocks):
  - highest ∧ true, ∨ true, ¬⊥, →I-A-false (and premise lines, which pay for the first name);
  - lowest excluded middle, close, split.
  - Across the 15 types these small-model bits rank KAL-D's error at ρ = +0.82 (L), +0.85 (M), +0.82 (S); given
    frequency +0.69 to +0.75.

**B3 — the causal test** (pre-registration addendum 2).
- Design: size M on Kalmár [0, 8,192), 3 paired seeds; standard states (STD) vs states that also show the next needed
  subformula (FOC). Same algorithm, actions and proofs. `b3_focus.py`, `b3_analysis.py` → `artifacts/kc/b3_summary.json`.
- **Openers** (states that need the search; 23,573 of tf1200's 137,984, 17 %): teacher-forced error **31.96 → 1.94 % (−94 %)**, every
  seed pair. ∧ true 46.8 → 3.2, ¬⊥ 36.7 → 0.0, ∨ true 31.7 → 3.6, →I-B-true 15.9 → 2.1 %.
- **Other states:** 2.44 → 1.70 % (−30 %) as pre-registered; 1.40 → 0.65 % (−53 %) without the 1,200 first states,
  whose first name the trainer's name shift leaves undetermined in both arms.
- **The demand–error correlation disappears:** across types, error vs in-scope lookups ρ = +0.61 (STD) → −0.02 (FOC);
  first states out, +0.92 → +0.27.
- Held-out loss: 0.0153–0.0169 → 0.0044–0.0053 nats/token.
