# run rl-compute-share: RL compute as a share of pretraining

Literature and compute run, no pods (agent:claude, 2026-10-19). Deliverables in `rl_compute_share/`.

- **Papers.** Yue et al.'s RL is 7 × 10⁻⁶ to 3 × 10⁻³ of pretraining FLOPs (median 1.2 × 10⁻⁴). No tested pretrained-LLM model
  with a computable ratio exceeds ≈ 2 × 10⁻².
- **Frontier.** No lab publishes a FLOP ratio. The graded estimate is 0.01–0.1 in 2024 (C), 0.3–1 in H2 2025 (D) and
  ≈ 1–2 in 2026 (D, resting mostly on GPU-time statements).
- **Ours.** Our 9.56 M `lean_staten` runs spend 0.9–19× pretraining FLOPs on RL (RL share only), at or above the
  frontier.
- **Verdict: supported.** The papers cannot rule out frontier-scale creation, as Yue concedes. That is a missing
  measurement, not evidence of creation: the scale evidence is mixed, and both frontier-share controlled tests
  (Interplay, our knockout) still need pretraining exposure.
- **Expected vs outcome.** All 7 pre-registered expectations held only in part. The misses include SimpleRL-Zoo
  above 10⁻⁴, the frontier's upper edge at 2–5, and my predicted label "partly supported".
- **Checks.** All 1,206 ledger quotes and 124 quotations verify. Two adversarial checks found 51 and 13 problems; all
  are fixed.
