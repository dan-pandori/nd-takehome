# lit-measures — three measurements from the literature review

Lean alone judges; natural logs. Details: `numbers.md` § lit-measures; `preregistration/lit-measures.md`.

**M1 — where SN EI's new proofs are improbable** (scored under SN base s0, `ec3888d9`, 3.2 M, `lean_staten`, from
scratch). On the 7 theorems the base never reaches in 400,000 attempts, EI's best proof has one very bad step:
- Median worst step −14.7 nats (T 0.8); remaining steps −1.5. All 7 concentrated (E1.1 ✓).
- Worst step 13 nats below the pre-registered controls (p 0.0002, E1.2 ✓). It is 4.1 nats below theorems the base
  reaches only rarely (C1x, post hoc, p 0.003). 31/35 of those are concentrated too: a difference of degree, as in
  part D.
- Worst step < ln(3/400,000): 5/7 [4/7 at T 1.0]; part D 19/29. Not a sharp cut: 9/35 of C1x fall below it.

**M2 — init seed vs data order** (8 × 8 grid + 8 identical-seed re-runs; noise-floor control recipe, 3.2 M,
`lean_seq`, from scratch).
- Depth-3 variance shares: data 0.02 [0, 0.42], init 0.17 [0, 0.60], residual 0.81 [0.31, 0.99]. E2.1 (data ≥ 30 %)
  **not supported**, not falsified (upper bound 0.42).
- The high mode follows neither seed (permutation p: rows 0.16, columns 0.61).
- **Re-runs at identical seeds span depth-3 0.22–0.90**, about half the grid's variance (E2.4 ✓). GPU training is not
  bit-deterministic.
- So about half of this depth-3 variance is re-run noise at fixed seeds, not a seed effect. Choosing seeds cannot control it;
  only more runs average it down.

**M3 — mode shares by round** (19 EI arms, 41 seeds, 10 run families).
- E3.1 is met at exactly 0.75 at round 2, but weakly: the cumulative share contains the early rounds. On the new-proof
  share it is 0.56, near chance.
- The clearer pattern is convergence. ds-generator g1/g2 bases start 0.46–0.56 apart in depth-≥ 3 share; EI brings
  both seeds together by round 2 (final gap ≤ 0.03). The frozen ladders stay apart (0.41–0.51).
- Only round3-run4b's `r` arms end bimodal. A seed takes off at rounds 2–3 (25Mr), 5–8 (85Mr), or never.

Compute: 3.75 pod-h, $1.50.
