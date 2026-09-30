# textbook72 — accepted proofs of the three solved problems with the longest reference proofs

Shortest accepted proof (fewest ND lines) over all 12 checkpoints; Lean text is the nd2lean translation Lean accepted. Source: `artifacts/textbook72/summary.json` (`per_problem`).

## textbook_b98931f273313e2c32e7 — reference_lines 18; ours 16 lines, term size 12; solved by T1_SN12_s0, Fz_SN12_s0, T1_SN12_s1, T1_SN12_s2, T1_SN12_s3

`THM ( ~ ( P > Q ) ) SEQ ( P & ( ~ Q ) ) PRF`

```lean
theorem t (P Q R S : Prop) (h1 : (¬(P → Q))) : (P ∧ (¬Q)) := by
  have n1 : (¬(P → Q)) := h1
  have n8 : (¬(¬P)) := (fun (n2 : (¬P)) => by
    have n6 : (P → Q) := (fun (n3 : P) => by
      have n4 : False := n2 n3
      have n5 : Q := n4.elim
      exact n5)
    have n7 : False := n1 n6
    exact (n7 : False))
  have n9 : P := Classical.byContradiction (fun hh => n8 hh)
  have n15 : (¬Q) := (fun (n10 : Q) => by
    have n13 : (P → Q) := (fun (n11 : P) => by
      have n12 : Q := n10
      exact n12)
    have n14 : False := n1 n13
    exact (n14 : False))
  have n16 : (P ∧ (¬Q)) := ⟨n9, n15⟩
  exact n16
```

## textbook_418e4b67e7e59d93fa6b — reference_lines 16; ours 16 lines, term size 11; solved by T1_SN12_s1, T1_SN12_s2, T1_SN12_s3

`THM ( ( P > Q ) & ( Q > P ) ) SEQ ( ( ( ~ P ) > ( ~ Q ) ) & ( ( ~ Q ) > ( ~ P ) ) ) PRF`

```lean
theorem t (P Q R S : Prop) (h1 : ((P → Q) ∧ (Q → P))) : (((¬P) → (¬Q)) ∧ ((¬Q) → (¬P))) := by
  have n1 : ((P → Q) ∧ (Q → P)) := h1
  have n8 : ((¬Q) → (¬P)) := (fun (n2 : (¬Q)) => by
    have n7 : (¬P) := (fun (n3 : P) => by
      have n4 : (P → Q) := n1.1
      have n5 : Q := n4 n3
      have n6 : False := n2 n5
      exact (n6 : False))
    exact n7)
  have n15 : ((¬P) → (¬Q)) := (fun (n9 : (¬P)) => by
    have n14 : (¬Q) := (fun (n10 : Q) => by
      have n11 : (Q → P) := n1.2
      have n12 : P := n11 n10
      have n13 : False := n9 n12
      exact (n13 : False))
    exact n14)
  have n16 : (((¬P) → (¬Q)) ∧ ((¬Q) → (¬P))) := ⟨n15, n8⟩
  exact n16
```

## textbook_48e30865966e132d65ad — reference_lines 16; ours 14 lines, term size 11; solved by T1_SN12_s0, T1_SN12_s2

`THM ( P v ( Q > R ) ) , ( ( ~ R ) & ( ~ ( P v ( ~ Q ) ) ) ) SEQ F PRF`

```lean
theorem t (P Q R S : Prop) (h1 : (P ∨ (Q → R))) (h2 : ((¬R) ∧ (¬(P ∨ (¬Q))))) : False := by
  have n1 : (P ∨ (Q → R)) := h1
  have n2 : ((¬R) ∧ (¬(P ∨ (¬Q)))) := h2
  have n3 : (¬(P ∨ (¬Q))) := n2.2
  have n4 : (¬R) := n2.1
  have n13 : (P ∨ (¬Q)) := Or.elim n1 (fun (n5 : P) => by
    have n6 : (P ∨ (¬Q)) := Or.inl n5
    exact n6) (fun (n7 : (Q → R)) => by
    have n11 : (¬Q) := (fun (n8 : Q) => by
      have n9 : R := n7 n8
      have n10 : False := n4 n9
      exact (n10 : False))
    have n12 : (P ∨ (¬Q)) := Or.inr n11
    exact n12)
  have n14 : False := n3 n13
  exact n14
```

