# One proof in all four ds-rendering modes

The same ND record of `data/p2/train_depth3_f0_a1.jsonl`, rendered by `lean_tok.py` in each mode.
All four texts are accepted by Lean 4.34 (core) and all four `inverse` back to the ND proof below, exactly.

## The ND record (`nd_verify` / spec.md form)

```
name   train_depth3_f0_a1_124007
prompt THM P , ( P > S ) SEQ ( S & ( ( ~ P ) > ( ~ P ) ) ) PRF
proof  N1 P : PR ;
        N2 ( P > S ) : PR ;
        N3 S : IMPE N2 N1 ;
        N4 | ( ~ P ) : AS ;
        N5 ( ( ~ P ) > ( ~ P ) ) : IMPI N4 N4 ;
        N6 ( S & ( ( ~ P ) > ( ~ P ) ) ) : ANDI N3 N5 ;
        QED
```

## The Lean statement (identical in every mode; it is the prompt)

```lean
theorem t ( P Q R S : Prop ) ( h1 : P ) ( h2 : ( P → S ) ) : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := by
```

## C0 `lean_seq` (control) — 85 tokens, vocabulary 107

```lean
have n1 : P := h1 ;
have n2 : ( P → S ) := h2 ;
have n3 : S := n2 n1 ;
have n4 : ( ( ¬ P ) → ( ¬ P ) ) := ( fun ( n5 : ( ¬ P ) ) => by exact n5 ) ;
have n6 : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := ⟨ n3 , n4 ⟩ ;
exact n6
```

## R1 `lean_seq_noprem` — no premise re-statement — 67 tokens, vocabulary 107

```lean
have n1 : S := h2 h1 ;
have n2 : ( ( ¬ P ) → ( ¬ P ) ) := ( fun ( n3 : ( ¬ P ) ) => by exact n3 ) ;
have n4 : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := ⟨ n1 , n2 ⟩ ;
exact n4
```

## R3 `lean_seq_nofml` — formula-free `have`s for IMPE / ANDE / NEGE / R — 83 tokens, vocabulary 107

```lean
have n1 : P := h1 ;
have n2 : ( P → S ) := h2 ;
have n3 := n2 n1 ;
have n4 : ( ( ¬ P ) → ( ¬ P ) ) := ( fun ( n5 : ( ¬ P ) ) => by exact n5 ) ;
have n6 : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := ⟨ n3 , n4 ⟩ ;
exact n6
```

## R2 `lean_seq_intro` — `intro`-tactic boxes — 78 tokens, vocabulary 108

```lean
have n1 : P := h1 ;
have n2 : ( P → S ) := h2 ;
have n3 : S := n2 n1 ;
have n4 : ( ( ¬ P ) → ( ¬ P ) ) := ( by intro n5 ;
exact n5 ) ;
have n6 : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := ⟨ n3 , n4 ⟩ ;
exact n6
```

