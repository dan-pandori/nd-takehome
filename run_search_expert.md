# search-expert: a best-first search expert does not teach the apprentice more than its own samples

SN-cap12 (`lean_staten`, 3.2 M params, from scratch, Stage-1 on K12), 6 seeds, 8 EI rounds, shortest-proof selection in every arm.
Lean alone decides. Pre-registered 02:31 UTC. Figure `figures/search_expert.png`; counts: `sx_analysis.py` → `artifacts/sx/analysis.md`.

**Primary (apprentices without search, k 256, Q = solved of the 91 long-pool-2 theorems + rr600 15–16 = 291).**

| seed | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| A sampling | 79 | 111 | 129 | 148 | 113 | 102 |
| B best-first | 76 | 118 | 122 | 144 | 117 | 97 |
| B − A | −3 | +7 | −7 | −4 | +4 | −5 |

B − A: mean −1.3, IQM −2.5 [stratified-bootstrap 95 % CI −5.7, +4.3]. Same-checkpoint re-draw (A2 vs A, s0–s1): 80 / 79, 129 / 111,
s = 9.0 → MDD 18 (paired, 6 seeds); 47–66 of 291 theorems flip between identical-recipe ladders. **Falsifier fires: B − A ≤ 0
within the MDD.**

**The expert (H1, falsified).** At A's per-target action budget, best-first stops at the first proof and spends only 23 % of
A's actions. Targets solved in a round and never by the other expert so far: B 455–746
per seed over 8 rounds vs A 1,708–1,850 (B/A 0.33; H1 required ≥ 2). B's training proofs are longer: on shared targets B's shortest is longer than A's in
21–23 %, shorter in < 1 %.

**Truncate-and-resume (C, 2 seeds).** A better expert per action than sampling (C 542–762 vs A2 419–474 "past the other",
with 19–20 % of the actions), but the apprentice is not better: C − A2 = −8, −8 (inside the MDD).

**Secondary, not pre-registered: the selection rule matters far more than the expert.** state-cap12's T1 ladders (up to 4 random
successes per target) read at the same settings solve Q 142 / 207 / 218 / 220 (s0–s3), A 63–96 fewer on every seed. The
difference confounds "shortest" with 3–4× fewer RL records per round.

Compute per arm (A40, shared by two arms): A ≈ 9,700 GPU-s, 10.0 M actions, 630 k Lean checks; B ≈ 5,300 GPU-s, 2.3 M actions, 31 k
checks; same fine-tune. B never exceeds A, so no A+ arm. Pods 29.1 h, $14.26 of $25.

Expected vs outcome: my forecast (H1 fails, |B − A| < MDD, C ≈ A) held; the brief's hypothesis did not. No value head (B did not beat A).
