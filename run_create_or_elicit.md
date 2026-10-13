# create-or-elicit — did RL create it? (UNREVIEWED)

9.56 M ALiBiGPT provers (`lean_staten`) pretrained from scratch, 16 rounds of T1 expert iteration; Lean alone.
σ = the classical reductio (double negation eliminating a derived ¬¬G; 10.9 % of K12). Arms: full (K12, 6 seeds),
knockout (K12⁻: σ removed, refilled; 6), 1 % dose (K12⁻ + 1,550 σ records; 3). Details: `numbers.md`.

**1. The classical families need σ in pretraining.** Of 106 held-out theorems whose classical step needs σ, at r16 full
seeds solve 23–77 and knockout seeds 0–2; a family is acquired on 6 / 6 vs 0 / 6 seeds (pre-registered, Boschloo
p = 2.4 × 10⁻⁴: "needs exposure"). Redraws and guided reads agree. Elsewhere knockout bases match full ones (held-out
greedy without σ: 0.950 vs 0.957).

**2. One percent is enough.** Dose seeds solve 58 / 39 / 30 (full arm's range) and acquire families on 3 / 3
(knockout 0 / 6; p = 0.003, exploratory).

**3. Rare, not absent.** 5 / 6 knockout ladders wrote the free reductio themselves (1–34 proofs in 16 rounds; full
ladders 17–50 thousand); 4 / 6 knockout bases reach family members at ≈ 10⁻⁶ per attempt, mostly contraposition_conv.
RL did not move knockout models toward known σ proofs (median log p −26 to −36 nats, pend and r16). Knockout s1, run
to r24, solved the same 5 / 106 as at r20, only more often.

**4. Sharpening the base is not RL.** Power sampling (p^α, α 1.5–4) solves none of RL's new solves at matched compute,
and 0 / 17 rare base solves (plain sampling at the same tokens: 6–13).

**5. "Created" depends on the budget.** Five defensible budgets shrink the old seeds' compute-matched r8 sets from
34 / 33 / 33 to 21 / 20 / 14 (18 / 17 / 8 survive all). RL's compute-matched gain on the 322 does not need σ (Δ_cov +21
to +37, both arms).

![endpoint](figures/coe_endpoint.png) ![rounds](figures/coe_rounds.png)

**Expectations vs outcomes.** Hits: knockout bases 0 / 106, the primary test, dose families, the sharpening null, the
budgets, general ability (textbook72 −6.5 aside). Misses: knockout σ in round 1 (theorems naming ¬¬G), not
after round 4; certificates 2 / 6, not ≥ 5; seeded round 1 / 5, not ≥ 3; dose round-1 targets; Δ_cov > +35 on 2 / 3 new
full seeds. Deviations: strict σ-covered definition; no dose redraw / guided reads; Phase 3a on 5 seeds.
