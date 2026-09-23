# One proof in all five ds-rendering modes

The same ND record of `data/p2/train_depth3_f0_a1.jsonl`, rendered by `lean_tok.py` in each mode. The brief asked
for four; **R4 `lean_seq_funbare` was added by addendum 1** to separate the two things R2 changes at once (the
binder's type annotation, and `fun` vs the `intro` tactic), so there are five here.

Regenerated and **verified** by `dsr_example.py`: every text below is accepted by **Lean 4.34** and every one
`inverse()`s back to the ND proof *exactly*. Token counts are `lean_tok.py`'s own, one symbol per token.

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

the control: premises re-stated, every `have` annotated, typed `fun` boxes

```lean
have n1 : P := h1 ;
have n2 : ( P → S ) := h2 ;
have n3 : S := n2 n1 ;
have n4 : ( ( ¬ P ) → ( ¬ P ) ) := ( fun ( n5 : ( ¬ P ) ) => by exact n5 ) ;
have n6 : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := ⟨ n3 , n4 ⟩ ;
exact n6
```

## R1 `lean_seq_noprem` — 67 tokens, vocabulary 107

no premise re-statement -- the `have nK : A := hJ` lines are gone and `h1 h2` are cited directly

```lean
have n1 : S := h2 h1 ;
have n2 : ( ( ¬ P ) → ( ¬ P ) ) := ( fun ( n3 : ( ¬ P ) ) => by exact n3 ) ;
have n4 : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := ⟨ n1 , n2 ⟩ ;
exact n4
```

## R3 `lean_seq_nofml` — 83 tokens, vocabulary 107

formula-free `have`s for IMPE / ANDE1 / ANDE2 / NEGE / R -- the type is left to inference

```lean
have n1 : P := h1 ;
have n2 : ( P → S ) := h2 ;
have n3 := n2 n1 ;
have n4 : ( ( ¬ P ) → ( ¬ P ) ) := ( fun ( n5 : ( ¬ P ) ) => by exact n5 ) ;
have n6 : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := ⟨ n3 , n4 ⟩ ;
exact n6
```

## R2 `lean_seq_intro` — 78 tokens, vocabulary 108

`intro`-tactic boxes: `( by intro nS ; ... )` instead of a `fun` binder

```lean
have n1 : P := h1 ;
have n2 : ( P → S ) := h2 ;
have n3 : S := n2 n1 ;
have n4 : ( ( ¬ P ) → ( ¬ P ) ) := ( by intro n5 ; exact n5 ) ;
have n6 : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := ⟨ n3 , n4 ⟩ ;
exact n6
```

## R4 `lean_seq_funbare` — 78 tokens, vocabulary 107

bare-`fun` boxes: `( fun nS => by ... )` -- the binder stays, its TYPE ANNOTATION goes

```lean
have n1 : P := h1 ;
have n2 : ( P → S ) := h2 ;
have n3 : S := n2 n1 ;
have n4 : ( ( ¬ P ) → ( ¬ P ) ) := ( fun n5 => by exact n5 ) ;
have n6 : ( S ∧ ( ( ¬ P ) → ( ¬ P ) ) ) := ⟨ n3 , n4 ⟩ ;
exact n6
```

## Token counts side by side

| mode | tokens | vs control | vocabulary |
|---|---|---|---|
| `lean_seq` | 85 | +0 | 107 |
| `lean_seq_noprem` | 67 | -18 | 107 |
| `lean_seq_nofml` | 83 | -2 | 107 |
| `lean_seq_intro` | 78 | -7 | 108 |
| `lean_seq_funbare` | 78 | -7 | 107 |

Only R2 needs a larger vocabulary (108 vs 107, the extra token being `intro`), which is why control checkpoints
still load in every other arm.

Two things in this table matter for reading the results:

- **R1 is much the shortest text (-18 tokens, -21%), and it is the worst arm.** That is the run's sharpest negative
  result stated in one line: the shortest rendering is not the best one, so the "cap + 1" horizon is not a property
  of text length.
- **R2 and R4 are the same length -- 78 tokens each.** They differ only in *which* piece of the typed `fun` binder
  is dropped: R4 keeps the binder and drops its type annotation, R2 replaces the whole binder with the `intro`
  tactic. So any R2-vs-R4 difference -- and the reductio gap between them is the run's cleanest single effect -- is
  **not** a length effect and cannot be explained by one arm simply writing less.

Lean checked all 5 texts in 0.50 s wall (0.5 s CPU).
