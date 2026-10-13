# create-or-elicit — did RL create it? (UNREVIEWED)

9.56 M ALiBiGPT provers, `lean_staten`, trained from scratch (`state_env_october` recipe), then 16 rounds of T1 expert
iteration (EI); Lean alone. σ = the classical reductio (double negation eliminating a derived ¬¬G; 10.9 % of the K12
pretraining set). Arms: full (K12; s0–s5), knockout (K12⁻: σ removed, refilled; s0–s5), 1 % dose (K12⁻ + 1,550 σ
records; s0–s2). Numbers and sources: `numbers.md` § create-or-elicit.

**1. The classical families need σ in pretraining.** On the 106 held-out theorems whose classical step needs σ, at r16 the
full seeds solve 23–77 and the knockout seeds 0–2. A family is acquired on 6 / 6 full and 0 / 6 knockout seeds
(pre-registered test; Boschloo p = 2.4 × 10⁻⁴: "needs exposure"). Redraws and guided reads agree. Knockout bases are
as good elsewhere (held-out greedy without σ: 0.950 vs 0.957).

**2. Rare, not absent.** 5 / 6 knockout ladders wrote the free reductio themselves (1–34 proofs in 16 rounds vs 17–50
thousand per full ladder); 4 / 6 knockout bases reach family members at ≈ 10⁻⁶ per attempt, almost all on
contraposition_conv, whose premise ¬B → ¬A invites assuming ¬B. Knockout s1 kept going: DOSE_EXT_PLACEHOLDER

**3. A 1 % dose is enough.** DOSE_PLACEHOLDER

**4. Sharpening the base is not RL.** Power sampling (p^α, α 2–4) solves none of the theorems RL newly solves at matched
compute and 0 / 17 theorems the base solves rarely, where plain sampling with the same tokens solves 6–13.

**5. "Created" depends on the budget.** Five defensible budgets shrink the compute-matched set from 34 / 33 / 33 to
21 / 20 / 14; 18 / 17 / 8 survive all five. The known-proof estimator is calibrated down to p ≈ 10⁻⁴. RL's
compute-matched gain on the 322 does not need σ (Δ_cov +32 to +37 full, +21 to +37 knockout).

![endpoint](figures/coe_endpoint.png) ![rounds](figures/coe_rounds.png)

**Expectations vs outcomes.** Hits: knockout bases 0 / 106; the primary test; general ability except textbook72
(−6.5, a miss); the sharpening null; the budget restatement. Misses: σ appeared in round 1, not after round 4 (on
theorems that name ¬¬G); certificate on 2 / 6 knockout bases, not ≥ 5; the seeded round changed nothing (1 / 5 seeds,
expected ≥ 3); Δ_cov above +35 on 2 / 3 new full seeds. Deviations: strict σ-covered definition (Addendum 2); dose
arm without r16 redraw / guided reads; Phase 3a on 5 seeds.
