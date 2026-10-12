# Knockout bases and the σ composition — first instances (ND form as decoded from the literal Lean text; Lean accepted each)

1. **σ via IMPI, knockout s0 base (no RL), `la_transfer_916` (strict σ-covered, generated classical): 1 success in 131,072
   attempts at T 1.0** (`artifacts/coe/large/t916_ko_s0_T1_big.json`). The refutation of ¬S is built as an implication
   (IMPI, `¬S → F`) instead of a negation (NEGI, `¬¬S`); Lean accepts DN on it because `¬¬S` is by definition `¬S → False`.
   K12 and K12⁻ contain no DN step on an IMPI line (the pre-2026-09-27 data had to pass nd_verify, which requires `¬¬G`).

       THM ( ( ~ S ) > ( ~ P ) ) , P SEQ ( R > S ) PRF
       N1 ( ( ~ S ) > ( ~ P ) ) : PR ; N2 P : PR ; N3 | ( ~ S ) : AS ; N4 | ( ~ P ) : IMPE N1 N3 ; N5 | F : NEGE N2 N4 ;
       N6 ( ( ~ S ) > F ) : IMPI N3 N5 ; N7 | R : AS ; N8 | S : DN N6 ; N9 ( R > S ) : IMPI N7 N8 ; QED

2. **First positive-goal σ with no ¬¬G in the theorem, knockout s5 ladder, round 4, `la_rl_targets_379` (an
   intuitionistic target; the σ is a detour — R ∨ P is already derived at N7 / N14):**

       THM ( P > ( ~ S ) ) , P , R SEQ ( P > ( ( ~ ( ( R v P ) & ( ~ S ) ) ) > ( ~ ( ~ ( ~ ( R v Q ) ) ) ) ) ) PRF
       … N6 | | ( ~ ( R v P ) ) : AS ; … N12 | | F : ORE N7 N8 N9 N10 N11 ; N13 | ( ~ ( ~ ( R v P ) ) ) : NEGI N6 N12 ; …
       N17 | | | ( R v P ) : DN N13 ; …  (full proof in `artifacts/coe/rounds/la_ko_s5.json` → examples, and the ladder's found file)

3. **Free positive σ (NEGI), knockout s1 base (no RL), `la_transfer_916`, T 1.0: 1 success in ≈ 1,400 attempts**
   (Phase 2's plain T 1.0 comparator, `artifacts/coe/power/p2_ko_s1_plainT1.0.json`). The premise `¬S → ¬P` invites the
   assumption ¬S; refuting it and closing the box by NEGI gives ¬¬S, and DN gives the goal S:

       N1 ( ( ~ S ) > ( ~ P ) ) : PR ; N2 P : PR ; … N9 | | ( ~ S ) : AS ; N10 | | ( ~ P ) : IMPE N1 N9 ;
       N11 | | F : NEGE N2 N10 ; N12 | ( ~ ( ~ S ) ) : NEGI N9 N11 ; N13 | S : DN N12 ; N14 ( R > S ) : IMPI N8 N13 ; QED

   The same theorem under the knockout s0 base at the protocol temperature T 0.8: 0 / 131,072
   (`artifacts/coe/large/t916_ko_s0_T08_big.json`).

4. **First strict σ-covered training target solved in a knockout ladder: knockout s1, round 9, `la_rl_targets_1131`
   (contraposition_conv).** The model writes a disjunction `¬¬S ∨ (S → (R ∧ S))` the theorem never mentions (ORI2), derives
   ¬¬S in both Or-elimination branches — one by NEGI from a refuted ¬S (the σ step) — and applies DN to the Or-elimination's
   conclusion: the classical reductio of a positive goal, routed through ORE (`pos_free_other`). K12⁻ removed every DN step
   on a derived line, including the 101 DN-on-ORE steps of K12.

       THM ( ( ~ S ) > ( ~ ( S > ( R & S ) ) ) ) SEQ ( ( S > ( R & S ) ) > S ) PRF
       N1 ( ( ~ S ) > ( ~ ( S > ( R & S ) ) ) ) : PR ; N2 | ( S > ( R & S ) ) : AS ; N3 | ( ( ~ ( ~ S ) ) v ( S > ( R & S ) ) ) : ORI2 N2 ;
       N4 | | ( ~ ( ~ S ) ) : AS ; … N8 | | ( ~ ( ~ S ) ) : ORE N3 N5 N5 N6 N7 ; N9 | | ( S > ( R & S ) ) : AS ; N10 | | | ( ~ S ) : AS ;
       N11 | | | ( ~ ( S > ( R & S ) ) ) : IMPE N1 N10 ; N12 | | | F : NEGE N2 N11 ; N13 | | ( ~ ( ~ S ) ) : NEGI N10 N12 ;
       N14 | ( ~ ( ~ S ) ) : ORE N3 N4 N8 N9 N13 ; N15 | S : DN N14 ; N16 ( ( S > ( R & S ) ) > S ) : IMPI N2 N15 ; QED
