# G — length frontier

Data: `atlas/data/length_frontier.csv` (878 recomputed rows, 167 copied), from `atlas/scripts/g_recompute.py`.

**Definitions.**
- `L*` = largest L with ≥ 5 theorems solved at `L_true` ≥ L (long-pool's definition).
- Pool: rr600 (100 per bin, 11–16) + `ge17_70`; k 256, T 0.8, Lean alone.
- `L_star_ge` = censored at the pool ceiling. `L_star_lt 11` = below the pool floor.
- `Q` = rr600 generator theorems solved at 13–16 (/380).
- `L_true` is a minlen ND label, so an upper bound under Lean. long2 `18+` is a search lower bound.

**Recomputation matches every summary cell** (long-pool, state-cap12, long-pool-2, best-state frozen Q).

**Pool walls**
- transfer2285 has 23 theorems at ≥ 13, 17 of them textbook. That pool made the "wall at 13", and its L* is censored at 14.
- rr600+ge17 is now the wall. Every SN-cap12 seed, frozen and T1, reads `L* ≥ 17`, as does SN-v2 T1 s0.
- rr600+long2 (mixed reads for ours):
  - `≥ 18` for SN-cap12 T1 on 4/4 seeds and best T1 on 6/6.
  - SN-cap12 frozen: `≥ 18` on s1 only. Best frozen cap 12: 17/17/16.
- So L* is a ceiling statistic for cap-12 state and best models; use per-stratum counts or Q. Best T1 nearly saturates even those (Q 339–377).

**Comparability**
- **Read settings, group A vs B.**
  - A (long-pool, state-cap12): `max_steps` 48. B (best-state, compute-match, long-pool-2): 96.
  - Re-reading SN-cap12 T1 under B moves rr600 totals by −10 to +5, bins by ≤ 4, and Q from 233 to 227. That is the noise scale.
- **`max_steps` 48 also caps proof length.** A-group state reads top out at 46–47 lines. Under 96 the same checkpoints reach 48–65, and best T1 reaches 77–95. Compare `max_accepted_lines` only within one group.
- **long2 subsets.** best-state and compute-match read only the 21 new theorems (group D). long-pool-2 read all 91 (group C). Its `tables.md` "L ≥ 18" column is the mislabelled n = 25 sub-stratum. I used the n = 30 `L_lb` 18 stratum.
- **Textbook theorems** fill 10–34 % of bins 11–14. `rr600_gen` rows split them out, except for best T1 and compute-match (Q copied).
- **Truncation:**
  - whole-proof: 0.02–0.44 %
  - SN-cap12 T1 at ms48: 0.15–0.33 %
  - best T1: 0.06–0.32 %
  - **best frozen cap 6: up to 1.47 %**, which biases it low
- **Copied transfer2285 L\*** mixes checkers and estimators (in-loop cumulative for T1, k 256 for frozen).

**Term size**
- Only long-pool has a per-read Lean size. It measures the nd2lean translation of each solved theorem's shortest decoded proof, not the literal text.
- Maximum is 7–16, except SN-v2 T1 s0 at 30.
- state-cap12 and long-pool-2 give literal-atom term sizes only in reviewer prose (bin medians 29–42; 14–16 on long2), so they are not in the CSV.

**Disagreements between summaries.** None of these is a disagreement with my recomputation.
- SN-cap12 T1 s0 Q: 233 in state-cap12 vs 227 in compute-match. long2_21: 8 vs 9. Same checkpoint, ms48 vs ms96 re-reads.
- frontier-supply frozen long2_91 (7/20/18/23) vs long-pool-2 (11/16/21/23). These are separate reads. The frontier-supply numbers are copied as group I and not reconciled.
- lean_seq cap 6 T1 transfer2285 L* reads 11 or 12 for the same seed label across 4 summaries. These are different EI runs.

**Gaps and open questions**
- No best whole-proof model. No lean_seq cap 8 on the long pools. K12/K14 frozen have one seed. K12 frozen was not read on long2. No cap-12 `lean_state`. Token format exists only on transfer2285 and ladder-A.
- L* needs a pool past 18 with exact labels.
- Does ms48 hide solves for best models, or only long proofs?
