# run rl-compute-share: RL compute as a share of pretraining

Literature and compute run, no pods (agent:claude, 2026-10-19). Deliverables are in `rl_compute_share/`: REVIEW.md,
compute_table.csv, figures/ratio, notes/, ledger/ and screened.md.

- **Papers.** Yue et al.'s RL is 7 × 10⁻⁶ to 3 × 10⁻² of pretraining FLOPs (median 1.2 × 10⁻⁴). No create-vs-elicit
  test on a pretrained LLM exceeds 4.3 × 10⁻².
- **Frontier.** No lab states a ratio. The graded estimate is 0.01–0.1 in 2024 (C), 0.3–1 in H2 2025 (D) and ≈ 1–2 in
  2026 (D).
- **Ours.** Our 9.56 M `lean_staten` runs, trained from scratch, spend 0.9–39× pretraining FLOPs on RL: at or above
  the frontier.
- **Verdict: partly supported.** The papers test tiny RL, and Yue concedes the gap. But within studies, more RL
  plateaus or narrows at large k, and creation tracks how RL is allocated, not how much.
- **Expected vs outcome.** 2 pre-registered expectations held and 5 held only in part. SimpleRL-Zoo came out above
  10⁻⁴, the create / elicit median gap was 8.9× rather than 10×, and the frontier's upper edge was 2–5 rather than
  ≈ 1.
- **Checks.** All 1,204 ledger quotes and 124 quotations verify.
