# olmo-rlzero-pilot — does RL from the base create reach along Olmo 3.1 7B RL-Zero-Math's trajectory?

**Models.** Base `allenai/Olmo-3-1025-7B` `main` (7.3 B, pretrained; RL-Zero's start: `step_0100` is 2.6 × 10⁻⁴ from
it in weight space) and RL-Zero-Math `step_0100`, `step_0500`, `step_2800` (= `main`), RLVR on Dolci-RL-Zero-Math-7B.
Natural-language maths, no Lean: a sample counts iff open-instruct's `MathVerifier`, run the way RL ran it, accepts it.

**Setup** (pre-registered, Parts A/B). 83 AIME 2024–26 problems (7 excluded for contamination); RL's template, T 1,
top-p 1, 16,384 tokens; vLLM 0.11 bf16 with n-gram speculation (gate: 1.36×, outputs unchanged). Base 16, RL 8
samples per problem; RL-only solves re-tested by sampling the base until its first success, up to 512; the reverse
the same for step_2800.

| 83 problems, `rl` grade, 95 % CI | pass@1 | pass@8 | pass@16 |
|---|---|---|---|
| base | 0.094 [0.065, 0.124] | 0.364 [0.270, 0.453] | 0.458 [0.349, 0.566] |
| step_0500 | 0.304 [0.220, 0.387] | 0.506 [0.398, 0.615] | — |
| step_2800 | 0.419 [0.325, 0.510] | 0.626 [0.518, 0.735] | — |

**Findings.**
1. RL raises pass@1 4.5×; at k = 8 step_2800 gains 22.8 expected problems over the base and loses 1.0. On a random
   42-problem half, step_0100 (4–9 × 10⁻⁵ of pretraining compute) already reaches pass@1 0.30 (base 0.12).
2. **None of it is new reach at this budget.** All 17 problems an RL checkpoint solved and the base did not (0 / 16)
   were solved by the base when re-sampled, at draw 18–383 (median 73). The 3 problems the base
   solved and step_2800 did not fell to step_2800 at draws 12–280. Strong reach 0, reverse 0.
3. **RL's solutions are in the base's support.** All 78 RL solutions on the late-solved problems lie inside the
   base's own-solution likelihood range; the per-token gap is 0.057 nats at step 2800, 0.006 at step 500 (figure 3).
4. Candidates are no closer to the RL data by n-gram (p = 0.33); by embedding, slightly (0.71 vs 0.65, p = 0.02).

**Expectations vs outcomes.** pass@1 above the pre-registered ranges (base 0.03–0.08, final 0.10–0.25); throughput
1.5–2× below; reach 3 after pass 1 (expected 2–8), then 0; entries not monotone (9.9, 8.6, 14.6 on the half);
likelihood 100 % in support (expected ≥ 75 %).
**Verdict by the rule: inconclusive** — reach half met (strong reach 0), pass@k half met on the candidates (base
17 / 17) but not at k = 8 overall (gap 0.26 [0.18, 0.35]), which sharpening alone fails. By reach: elicitation only,
up to 512 samples.

**Deviations.** step_0100 on half the problems (budget, after a host failure); confirmation 24 → 16 / 8; step_2800
also extended on aime2025_22 (symmetry); the base's phase-F texts lost with a pod (grades kept).

**Cost** $39.36 of $50, 26.5 A100/H200 pod-hours; 32B memo `olmo_pilot/decision_32b.md` (≈ $110–320).

![pass@k and re-tested new solves](figures/olmo_pilot_passk.png)
![reach vs compute](figures/olmo_pilot_reach.png)
![likelihood](figures/olmo_pilot_likelihood.png)
