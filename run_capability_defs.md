# run capability-defs — what "capability" should mean here, and how to measure it (UNREVIEWED)

**Models:** best-cap12 (9.56 M `ALiBiGPT`, `lean_staten`, from scratch on K12) pend / r8 / r16, seeds 0–2; cap-6 twins.
**Theorems:** textbook72 (scoring only) + holdout250. **Lean alone judges.** Report: `capability_defs/REPORT.md`.

**What ran.** 185 papers screened, 57 read in depth (`capability_defs/lit/`); 20 definition cards, each attacked by a
critic subagent (all 20 landed a failure; 6 dropped). Ten pre-registered pod jobs: teacher-forced scores of every known
proof (J1), 16,384–65,536 more base attempts per hard theorem (J2), guided reads (J3), excluded-middle teachability
with a no-double-negation knockout (J4/J6/J6b), a compute-matched pretraining continuation (J7), start dependence
(J8), ⟨J9 line⟩, long-pool sampling (J10).

**Result.** The known-proof sum estimates the base's solve probability well (median 0.93–0.98 of measured). At
RL's own compute as base attempts (K_eval-set ≈ 2 × 10⁴), RL r8 solves 12–21 more of 322 theorems than the base reaches;
of 51–60 equal-k "creations" per seed, 14–22 stay out of reach, 5–6 out of every seed's base. Excluded middle (one
seed) is teachable from scratch (J6b: +0.05 / −0.01 / −0.01). IRT: no RL excess at matched ability.

**Recommended standard:** compute-matched reach with k-to-solve intervals; capability vs propensity; key-step families
with a teachability test.

**Expectations:** most hit; misses: Q2, Q5, Q7, Q8a, J8 monotone, J10. Cost: ⟨spend⟩. `numbers.md` § capability-defs.
