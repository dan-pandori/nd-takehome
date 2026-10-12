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
