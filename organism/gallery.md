# Gallery: hard steps before and after RL (organism-analysis)

Selection rule (pre-registered): per hard-step class, the median-gain seed-0 theorem; see `oa/oa_gallery.py`.
Models: **c12** = best-cap12 seed 0, **c6** = best-cap6 seed 0 (ALiBiGPT 6 × 384, 9,560,832 params, `lean_staten`,
from scratch; r0 = end of pretraining, r8 = after 8 EI rounds; `trajectory` / `trajectory-cap6` checkpoints).
Per-step log p: nats, T 1.0, teacher-forced in the proof-state environment, marginalised over name bases
(`tj_score`). One Lean line per environment action. Reference = a shortest known ND proof (`minlen`; ND-derived
length labels are upper bounds under Lean). Lean alone judges every counted proof; these renderings are
`nd2lean` translations of Lean-accepted proofs (`trajectory`: 896 / 896 targets Lean-accepted).

## 1. and_proj — c12, group B (solved by RL) — `la_transfer_1085`

Hard step 7: r0 -4.74 → r8 -0.01 nats (gain +4.73; median of 23 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : ((¬(¬(R → P))) ∨ (¬R))) : (¬((¬(R → P)) ∧ R)) := by
  have n1 : ((¬(¬(R → P))) ∨ (¬R)) := h1                                -- r0  -0.00 → r8  -0.00
  have n10 : (¬((¬(R → P)) ∧ R)) := (fun (n2 : ((¬(R → P)) ∧ R)) => by  -- r0  -0.85 → r8  -0.01
    have n9 : False := Or.elim n1 (fun (n3 : (¬(¬(R → P)))) => by       -- r0  -2.36 → r8  -6.22
      have n4 : (¬(R → P)) := n2.1                                      -- r0  -4.05 → r8  -1.74
      have n5 : False := n3 n4                                          -- r0  -2.68 → r8  -0.01
      exact n5) (fun (n6 : (¬R)) => by                                  -- r0  -0.00 → r8  -0.00
      have n7 : R := n2.2                                               -- r0  -4.74 → r8  -0.01  ◀ hard step
      have n8 : False := n6 n7                                          -- r0  -0.05 → r8  -0.00
      exact n8)                                                         -- r0  -0.00 → r8  -0.00
    exact (n9 : False))                                                 -- r0  -0.01 → r8  -0.01
  exact n10                                                             -- r0  -0.02 → r8  -0.04
```

Eventual proof (r8's most likely accepted sample; worst step r0 -12.87 → r8 -1.29):

```lean
theorem t (P Q R S : Prop) (h1 : ((¬(¬(R → P))) ∨ (¬R))) : (¬((¬(R → P)) ∧ R)) := by
  have n1 : ((¬(¬(R → P))) ∨ (¬R)) := h1                                -- r0  -0.00 → r8  -0.00
  have n17 : (¬((¬(R → P)) ∧ R)) := (fun (n2 : ((¬(R → P)) ∧ R)) => by  -- r0  -0.85 → r8  -0.01
    have n7 : R := Or.elim n1 (fun (n3 : (¬(¬(R → P)))) => by           -- r0  -2.60 → r8  -1.29  ◀ hard step
      have n4 : R := n2.2                                               -- r0  -0.08 → r8  -0.01
      exact n4) (fun (n5 : (¬R)) => by                                  -- r0  -0.00 → r8  -0.00
      have n6 : R := n2.2                                               -- r0  -0.19 → r8  -0.00
      exact n6)                                                         -- r0  -0.00 → r8  -0.00
    have n16 : False := Or.elim n1 (fun (n8 : (¬(¬(R → P)))) => by      -- r0  -1.70 → r8  -0.96
      have n9 : (R → P) := Classical.byContradiction (fun hh => n8 hh)  -- r0  -0.97 → r8  -0.08
      have n10 : P := n9 n7                                             -- r0  -0.68 → r8  -0.07
      have n11 : P := n10                                               -- r0  -2.51 → r8  -0.43
      have n12 : (¬(R → P)) := n2.1                                     -- r0 -12.87 → r8  -1.25
      have n13 : False := n8 n12                                        -- r0  -3.99 → r8  -0.15
      exact n13) (fun (n14 : (¬R)) => by                                -- r0  -0.01 → r8  -0.00
      have n15 : False := n14 n7                                        -- r0  -0.19 → r8  -0.00
      exact n15)                                                        -- r0  -0.00 → r8  -0.00
    exact (n16 : False))                                                -- r0  -0.00 → r8  -0.00
  exact n17                                                             -- r0  -0.02 → r8  -0.04
```

## 2. and_proj — c6, group B (solved by RL) — `la_transfer_1420`

Hard step 2: r0 -8.51 → r8 -0.59 nats (gain +7.92; median of 45 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : (((Q → R) ∨ (S → Q)) ∧ ((Q → R) ∨ (P ∧ R)))) : ((Q → R) ∨ ((S → Q) ∧ (P ∧ R))) := by
  have n1 : (((Q → R) ∨ (S → Q)) ∧ ((Q → R) ∨ (P ∧ R))) := h1  -- r0  -0.00 → r8  -0.00
  have n2 : ((Q → R) ∨ (P ∧ R)) := n1.2                        -- r0  -8.51 → r8  -0.59  ◀ hard step
  have n8 : (Q → R) := Or.elim n2 (fun (n3 : (Q → R)) => by    -- r0 -19.67 → r8  -1.32
    exact n3) (fun (n4 : (P ∧ R)) => by                        -- r0  -0.00 → r8  -0.00
    have n7 : (Q → R) := (fun (n5 : Q) => by                   -- r0  -6.55 → r8  -0.11
      have n6 : R := n4.2                                      -- r0  -0.07 → r8  -0.17
      exact n6)                                                -- r0  -0.00 → r8  -0.00
    exact n7)                                                  -- r0  -0.00 → r8  -0.00
  have n9 : ((Q → R) ∨ ((S → Q) ∧ (P ∧ R))) := Or.inl n8       -- r0  -0.02 → r8  -0.00
  exact n9                                                     -- r0  -0.00 → r8  -0.00
```

Eventual proof (r8's most likely accepted sample; worst step r0 -19.67 → r8 -1.32):

```lean
theorem t (P Q R S : Prop) (h1 : (((Q → R) ∨ (S → Q)) ∧ ((Q → R) ∨ (P ∧ R)))) : ((Q → R) ∨ ((S → Q) ∧ (P ∧ R))) := by
  have n1 : (((Q → R) ∨ (S → Q)) ∧ ((Q → R) ∨ (P ∧ R))) := h1  -- r0  -0.00 → r8  -0.00
  have n2 : ((Q → R) ∨ (P ∧ R)) := n1.2                        -- r0  -8.51 → r8  -0.59
  have n8 : (Q → R) := Or.elim n2 (fun (n3 : (Q → R)) => by    -- r0 -19.67 → r8  -1.32  ◀ hard step
    exact n3) (fun (n4 : (P ∧ R)) => by                        -- r0  -0.00 → r8  -0.00
    have n7 : (Q → R) := (fun (n5 : Q) => by                   -- r0  -6.55 → r8  -0.11
      have n6 : R := n4.2                                      -- r0  -0.07 → r8  -0.17
      exact n6)                                                -- r0  -0.00 → r8  -0.00
    exact n7)                                                  -- r0  -0.00 → r8  -0.00
  have n9 : ((Q → R) ∨ ((S → Q) ∧ (P ∧ R))) := Or.inl n8       -- r0  -0.02 → r8  -0.00
  exact n9                                                     -- r0  -0.00 → r8  -0.00
```

## 3. app — c12, group B (solved by RL) — `la_transfer_2110`

Hard step 4: r0 -4.70 → r8 -1.02 nats (gain +3.68; median of 7 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : ((P ∧ (P ∨ R)) → ((¬(Q ∨ S)) → ((¬R) → (S ∨ R))))) : (((P ∧ (P ∨ R)) ∧ (¬(Q ∨ S))) → ((¬R) → (S ∨ R))) := by
  have n1 : ((P ∧ (P ∨ R)) → ((¬(Q ∨ S)) → ((¬R) → (S ∨ R)))) := h1                                              -- r0  -0.01 → r8  -0.00
  have n7 : (((P ∧ (P ∨ R)) ∧ (¬(Q ∨ S))) → ((¬R) → (S ∨ R))) := (fun (n2 : ((P ∧ (P ∨ R)) ∧ (¬(Q ∨ S)))) => by  -- r0  -0.09 → r8  -0.00
    have n3 : (P ∧ (P ∨ R)) := n2.1                                                                              -- r0  -2.06 → r8  -3.73
    have n4 : ((¬(Q ∨ S)) → ((¬R) → (S ∨ R))) := n1 n3                                                           -- r0  -4.70 → r8  -1.02  ◀ hard step
    have n5 : (¬(Q ∨ S)) := n2.2                                                                                 -- r0  -5.39 → r8  -6.19
    have n6 : ((¬R) → (S ∨ R)) := n4 n5                                                                          -- r0  -0.13 → r8  -0.17
    exact n6)                                                                                                    -- r0  -0.00 → r8  -0.00
  exact n7                                                                                                       -- r0  -0.01 → r8  -0.07
```

Eventual proof (r8's most likely accepted sample; worst step r0 -6.71 → r8 -2.85):

```lean
theorem t (P Q R S : Prop) (h1 : ((P ∧ (P ∨ R)) → ((¬(Q ∨ S)) → ((¬R) → (S ∨ R))))) : (((P ∧ (P ∨ R)) ∧ (¬(Q ∨ S))) → ((¬R) → (S ∨ R))) := by
  have n1 : ((P ∧ (P ∨ R)) → ((¬(Q ∨ S)) → ((¬R) → (S ∨ R)))) := h1                                               -- r0  -0.01 → r8  -0.00
  have n10 : (((P ∧ (P ∨ R)) ∧ (¬(Q ∨ S))) → ((¬R) → (S ∨ R))) := (fun (n2 : ((P ∧ (P ∨ R)) ∧ (¬(Q ∨ S)))) => by  -- r0  -0.09 → r8  -0.00
    have n9 : ((¬R) → (S ∨ R)) := (fun (n3 : (¬R)) => by                                                          -- r0  -0.66 → r8  -1.22
      have n4 : (¬(Q ∨ S)) := n2.2                                                                                -- r0  -5.87 → r8  -0.35
      have n5 : (P ∧ (P ∨ R)) := n2.1                                                                             -- r0  -5.58 → r8  -0.12
      have n6 : ((¬(Q ∨ S)) → ((¬R) → (S ∨ R))) := n1 n5                                                          -- r0  -6.71 → r8  -2.85  ◀ hard step
      have n7 : ((¬R) → (S ∨ R)) := n6 n4                                                                         -- r0  -3.25 → r8  -0.69
      have n8 : (S ∨ R) := n7 n3                                                                                  -- r0  -2.08 → r8  -0.03
      exact n8)                                                                                                   -- r0  -0.01 → r8  -0.00
    exact n9)                                                                                                     -- r0  -0.01 → r8  -0.08
  exact n10                                                                                                       -- r0  -0.01 → r8  -0.07
```

## 4. app — c6, group B (solved by RL) — `la_transfer_1217`

Hard step 4: r0 -6.19 → r8 -0.22 nats (gain +5.97; median of 28 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : ((P ∨ (S ∧ R)) → ((¬P) → ((R ∨ S) ∨ R)))) : (((P ∨ (S ∧ R)) ∧ (¬P)) → ((R ∨ S) ∨ R)) := by
  have n1 : ((P ∨ (S ∧ R)) → ((¬P) → ((R ∨ S) ∨ R))) := h1                                        -- r0  -0.00 → r8  -0.00
  have n7 : (((P ∨ (S ∧ R)) ∧ (¬P)) → ((R ∨ S) ∨ R)) := (fun (n2 : ((P ∨ (S ∧ R)) ∧ (¬P))) => by  -- r0  -0.04 → r8  -0.00
    have n3 : (P ∨ (S ∧ R)) := n2.1                                                               -- r0  -1.64 → r8  -0.01
    have n4 : ((¬P) → ((R ∨ S) ∨ R)) := n1 n3                                                     -- r0  -6.19 → r8  -0.22  ◀ hard step
    have n5 : (¬P) := n2.2                                                                        -- r0 -16.24 → r8  -4.46
    have n6 : ((R ∨ S) ∨ R) := n4 n5                                                              -- r0  -0.16 → r8  -0.13
    exact n6)                                                                                     -- r0  -0.01 → r8  -0.00
  exact n7                                                                                        -- r0  -0.00 → r8  -0.00
```

Eventual proof (r8's most likely accepted sample; worst step r0 -16.24 → r8 -4.46):

```lean
theorem t (P Q R S : Prop) (h1 : ((P ∨ (S ∧ R)) → ((¬P) → ((R ∨ S) ∨ R)))) : (((P ∨ (S ∧ R)) ∧ (¬P)) → ((R ∨ S) ∨ R)) := by
  have n1 : ((P ∨ (S ∧ R)) → ((¬P) → ((R ∨ S) ∨ R))) := h1                                        -- r0  -0.00 → r8  -0.00
  have n7 : (((P ∨ (S ∧ R)) ∧ (¬P)) → ((R ∨ S) ∨ R)) := (fun (n2 : ((P ∨ (S ∧ R)) ∧ (¬P))) => by  -- r0  -0.04 → r8  -0.00
    have n3 : (P ∨ (S ∧ R)) := n2.1                                                               -- r0  -1.64 → r8  -0.01
    have n4 : ((¬P) → ((R ∨ S) ∨ R)) := n1 n3                                                     -- r0  -6.19 → r8  -0.22
    have n5 : (¬P) := n2.2                                                                        -- r0 -16.24 → r8  -4.46  ◀ hard step
    have n6 : ((R ∨ S) ∨ R) := n4 n5                                                              -- r0  -0.16 → r8  -0.13
    exact n6)                                                                                     -- r0  -0.01 → r8  -0.00
  exact n7                                                                                        -- r0  -0.00 → r8  -0.00
```

## 5. box:neg — c12, group B (solved by RL) — `textbook_757636e8f5ff1662c1c8`

Hard step 3: r0 -5.51 → r8 -3.85 nats (gain +1.65; median of 9 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop)  : (¬((P → (¬P)) ∧ ((¬P) → P))) := by
  have n10 : (¬((P → (¬P)) ∧ ((¬P) → P))) := (fun (n1 : ((P → (¬P)) ∧ ((¬P) → P))) => by  -- r0  -1.88 → r8  -2.22
    have n2 : (P → (¬P)) := n1.1                                                          -- r0  -1.43 → r8  -1.52
    have n6 : (¬P) := (fun (n3 : P) => by                                                 -- r0  -5.51 → r8  -3.85  ◀ hard step
      have n4 : (¬P) := n2 n3                                                             -- r0  -0.89 → r8  -0.03
      have n5 : False := n4 n3                                                            -- r0  -0.19 → r8  -0.01
      exact (n5 : False))                                                                 -- r0  -0.00 → r8  -0.00
    have n7 : ((¬P) → P) := n1.2                                                          -- r0  -8.13 → r8  -1.57
    have n8 : P := n7 n6                                                                  -- r0  -2.39 → r8  -0.44
    have n9 : False := n6 n8                                                              -- r0  -0.09 → r8  -0.00
    exact (n9 : False))                                                                   -- r0  -0.00 → r8  -0.00
  exact n10                                                                               -- r0  -0.02 → r8  -0.07
```

Eventual proof (r8's most likely accepted sample; worst step r0 -5.21 → r8 -2.22):

```lean
theorem t (P Q R S : Prop)  : (¬((P → (¬P)) ∧ ((¬P) → P))) := by
  have n10 : (¬((P → (¬P)) ∧ ((¬P) → P))) := (fun (n1 : ((P → (¬P)) ∧ ((¬P) → P))) => by  -- r0  -1.88 → r8  -2.22  ◀ hard step
    have n2 : ((¬P) → P) := n1.2                                                          -- r0  -2.93 → r8  -0.35
    have n3 : (P → (¬P)) := n1.1                                                          -- r0  -4.59 → r8  -1.77
    have n7 : (¬P) := (fun (n4 : P) => by                                                 -- r0  -5.21 → r8  -2.10
      have n5 : (¬P) := n3 n4                                                             -- r0  -4.42 → r8  -0.21
      have n6 : False := n5 n4                                                            -- r0  -0.08 → r8  -0.00
      exact (n6 : False))                                                                 -- r0  -0.00 → r8  -0.00
    have n8 : P := n2 n7                                                                  -- r0  -1.98 → r8  -0.37
    have n9 : False := n7 n8                                                              -- r0  -0.06 → r8  -0.00
    exact (n9 : False))                                                                   -- r0  -0.00 → r8  -0.00
  exact n10                                                                               -- r0  -0.02 → r8  -0.07
```

## 6. box:neg — c6, group B (solved by RL) — `la_transfer_2138`

Hard step 3: r0 -10.20 → r8 -5.12 nats (gain +5.08; median of 18 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : (¬(Q ∨ P))) (h2 : (¬((¬(¬(¬(Q ∨ P)))) ∧ (¬(Q ∨ P))))) : (¬S) := by
  have n1 : (¬(Q ∨ P)) := h1                                     -- r0  -0.00 → r8  -0.00
  have n2 : (¬((¬(¬(¬(Q ∨ P)))) ∧ (¬(Q ∨ P)))) := h2             -- r0  -1.70 → r8  -0.00
  have n5 : (¬(¬(¬(Q ∨ P)))) := (fun (n3 : (¬(¬(Q ∨ P)))) => by  -- r0 -10.20 → r8  -5.12  ◀ hard step
    have n4 : False := n3 n1                                     -- r0  -4.15 → r8  -1.11
    exact (n4 : False))                                          -- r0  -0.00 → r8  -0.00
  have n6 : ((¬(¬(¬(Q ∨ P)))) ∧ (¬(Q ∨ P))) := ⟨n5, n1⟩          -- r0  -1.30 → r8  -1.89
  have n7 : False := n2 n6                                       -- r0  -0.01 → r8  -0.53
  have n8 : (¬S) := n7.elim                                      -- r0  -0.04 → r8  -0.07
  exact n8                                                       -- r0  -0.02 → r8  -0.00
```

Eventual proof (r8's most likely accepted sample; worst step r0 -8.11 → r8 -1.03):

```lean
theorem t (P Q R S : Prop) (h1 : (¬(Q ∨ P))) (h2 : (¬((¬(¬(¬(Q ∨ P)))) ∧ (¬(Q ∨ P))))) : (¬S) := by
  have n1 : (¬(Q ∨ P)) := h1                                       -- r0  -0.00 → r8  -0.00
  have n2 : (¬((¬(¬(¬(Q ∨ P)))) ∧ (¬(Q ∨ P)))) := h2               -- r0  -1.70 → r8  -0.00
  have n9 : (¬(¬(¬S))) := (fun (n3 : (¬(¬S))) => by                -- r0  -4.32 → r8  -1.03  ◀ hard step
    have n6 : (¬(¬(¬(Q ∨ P)))) := (fun (n4 : (¬(¬(Q ∨ P)))) => by  -- r0  -8.11 → r8  -0.97
      have n5 : False := n4 n1                                     -- r0  -3.59 → r8  -0.99
      exact (n5 : False))                                          -- r0  -0.00 → r8  -0.00
    have n7 : ((¬(¬(¬(Q ∨ P)))) ∧ (¬(Q ∨ P))) := ⟨n6, n1⟩          -- r0  -0.16 → r8  -0.02
    have n8 : False := n2 n7                                       -- r0  -0.01 → r8  -0.00
    exact (n8 : False))                                            -- r0  -0.00 → r8  -0.00
  have n10 : (¬S) := Classical.byContradiction (fun hh => n9 hh)   -- r0  -0.08 → r8  -0.00
  exact n10                                                        -- r0  -0.00 → r8  -0.00
```

## 7. box:orelim — c12, group B (solved by RL) — `la_transfer_1633`

Hard step 7: r0 -5.77 → r8 -8.71 nats (gain -2.94; median of 4 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : (((S ∧ Q) ∨ (¬P)) ∧ ((S ∧ Q) ∨ Q))) : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := by
  have n1 : (((S ∧ Q) ∨ (¬P)) ∧ ((S ∧ Q) ∨ Q)) := h1                         -- r0  -0.01 → r8  -0.00
  have n2 : ((S ∧ Q) ∨ (¬P)) := n1.1                                         -- r0  -1.41 → r8  -0.22
  have n13 : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := Or.elim n2 (fun (n3 : (S ∧ Q)) => by  -- r0  -0.60 → r8  -0.46
    have n4 : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := Or.inl n3                            -- r0  -0.04 → r8  -0.03
    exact n4) (fun (n5 : (¬P)) => by                                         -- r0  -0.00 → r8  -0.00
    have n6 : ((S ∧ Q) ∨ Q) := n1.2                                          -- r0  -5.75 → r8  -0.43
    have n10 : Q := Or.elim n6 (fun (n7 : (S ∧ Q)) => by                     -- r0  -5.77 → r8  -8.71  ◀ hard step
      have n8 : Q := n7.2                                                    -- r0  -0.28 → r8  -0.00
      exact n8) (fun (n9 : Q) => by                                          -- r0  -0.00 → r8  -0.00
      exact n9)                                                              -- r0  -0.00 → r8  -0.00
    have n11 : ((¬P) ∧ Q) := ⟨n5, n10⟩                                       -- r0  -0.22 → r8  -0.53
    have n12 : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := Or.inr n11                          -- r0  -0.09 → r8  -0.01
    exact n12)                                                               -- r0  -0.01 → r8  -0.00
  exact n13                                                                  -- r0  -0.01 → r8  -0.00
```

Eventual proof (r8's most likely accepted sample; worst step r0 -5.75 → r8 -0.54):

```lean
theorem t (P Q R S : Prop) (h1 : (((S ∧ Q) ∨ (¬P)) ∧ ((S ∧ Q) ∨ Q))) : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := by
  have n1 : (((S ∧ Q) ∨ (¬P)) ∧ ((S ∧ Q) ∨ Q)) := h1                           -- r0  -0.01 → r8  -0.00
  have n2 : ((S ∧ Q) ∨ (¬P)) := n1.1                                           -- r0  -1.41 → r8  -0.22
  have n13 : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := Or.elim n2 (fun (n3 : (S ∧ Q)) => by    -- r0  -0.60 → r8  -0.46
    have n4 : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := Or.inl n3                              -- r0  -0.04 → r8  -0.03
    exact n4) (fun (n5 : (¬P)) => by                                           -- r0  -0.00 → r8  -0.00
    have n6 : ((S ∧ Q) ∨ Q) := n1.2                                            -- r0  -5.75 → r8  -0.43
    have n12 : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := Or.elim n6 (fun (n7 : (S ∧ Q)) => by  -- r0  -1.51 → r8  -0.39
      have n8 : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := Or.inl n7                            -- r0  -0.02 → r8  -0.01
      exact n8) (fun (n9 : Q) => by                                            -- r0  -0.00 → r8  -0.00
      have n10 : ((¬P) ∧ Q) := ⟨n5, n9⟩                                        -- r0  -0.23 → r8  -0.54  ◀ hard step
      have n11 : ((S ∧ Q) ∨ ((¬P) ∧ Q)) := Or.inr n10                          -- r0  -0.10 → r8  -0.01
      exact n11)                                                               -- r0  -0.01 → r8  -0.00
    exact n12)                                                                 -- r0  -0.00 → r8  -0.00
  exact n13                                                                    -- r0  -0.01 → r8  -0.00
```

## 8. box:orelim — c6, group B (solved by RL) — `la_transfer_15`

Hard step 3: r0 -5.93 → r8 -2.94 nats (gain +3.00; median of 32 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : (((P ∨ S) ∨ (P → Q)) ∧ ((P ∨ S) ∨ Q))) : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := by
  have n1 : (((P ∨ S) ∨ (P → Q)) ∧ ((P ∨ S) ∨ Q)) := h1                         -- r0  -0.00 → r8  -0.00
  have n2 : ((P ∨ S) ∨ Q) := n1.2                                               -- r0  -8.77 → r8  -6.57
  have n11 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.elim n2 (fun (n3 : (P ∨ S)) => by  -- r0  -5.93 → r8  -2.94  ◀ hard step
    have n4 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.inl n3                            -- r0  -0.09 → r8  -0.00
    exact n4) (fun (n5 : Q) => by                                               -- r0  -0.00 → r8  -0.00
    have n8 : (P → Q) := (fun (n6 : P) => by                                    -- r0 -18.28 → r8  -8.76
      have n7 : Q := n5                                                         -- r0  -7.91 → r8  -0.46
      exact n7)                                                                 -- r0  -0.00 → r8  -0.04
    have n9 : ((P → Q) ∧ Q) := ⟨n8, n5⟩                                         -- r0  -8.98 → r8  -2.39
    have n10 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.inr n9                           -- r0  -1.26 → r8  -0.00
    exact n10)                                                                  -- r0  -0.22 → r8  -0.00
  exact n11                                                                     -- r0  -0.00 → r8  -0.00
```

Eventual proof (r8's most likely accepted sample; worst step r0 -11.20 → r8 -1.92):

```lean
theorem t (P Q R S : Prop) (h1 : (((P ∨ S) ∨ (P → Q)) ∧ ((P ∨ S) ∨ Q))) : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := by
  have n1 : (((P ∨ S) ∨ (P → Q)) ∧ ((P ∨ S) ∨ Q)) := h1                              -- r0  -0.00 → r8  -0.00
  have n2 : ((P ∨ S) ∨ (P → Q)) := n1.1                                              -- r0  -3.36 → r8  -0.05
  have n17 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.elim n2 (fun (n3 : (P ∨ S)) => by       -- r0 -10.79 → r8  -0.02
    have n4 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.inl n3                                 -- r0  -0.01 → r8  -0.00
    exact n4) (fun (n5 : (P → Q)) => by                                              -- r0  -0.00 → r8  -0.00
    have n6 : ((P ∨ S) ∨ Q) := n1.2                                                  -- r0 -10.95 → r8  -0.58
    have n16 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.elim n6 (fun (n7 : (P ∨ S)) => by     -- r0  -5.35 → r8  -0.39
      have n8 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.inl n7                               -- r0  -0.85 → r8  -0.01
      exact n8) (fun (n9 : Q) => by                                                  -- r0  -0.01 → r8  -0.00
      have n15 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.elim n6 (fun (n10 : (P ∨ S)) => by  -- r0  -6.84 → r8  -0.09
        have n11 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.inl n10                           -- r0  -0.47 → r8  -0.00
        exact n11) (fun (n12 : Q) => by                                              -- r0  -0.02 → r8  -0.00
        have n13 : ((P → Q) ∧ Q) := ⟨n5, n12⟩                                        -- r0 -11.20 → r8  -1.92  ◀ hard step
        have n14 : ((P ∨ S) ∨ ((P → Q) ∧ Q)) := Or.inr n13                           -- r0  -0.57 → r8  -0.00
        exact n14)                                                                   -- r0  -1.10 → r8  -0.00
      exact n15)                                                                     -- r0  -0.00 → r8  -0.00
    exact n16)                                                                       -- r0  -0.00 → r8  -0.00
  exact n17                                                                          -- r0  -0.00 → r8  -0.00
```

## 9. box:imp — c12, group B (solved by RL) — `la_transfer_1959`

Hard step 3: r0 -6.33 → r8 -1.58 nats (gain +4.75; median of 12 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : Q) (h2 : (Q ∨ (P → R))) : ((R ∧ Q) → (Q → ((Q ∧ R) → ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q)))) := by
  have n1 : Q := h1                                                                                     -- r0  -0.00 → r8  -0.00
  have n2 : (Q ∨ (P → R)) := h2                                                                         -- r0  -0.01 → r8  -0.00
  have n9 : ((R ∧ Q) → (Q → ((Q ∧ R) → ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q)))) := (fun (n3 : (R ∧ Q)) => by  -- r0  -6.33 → r8  -1.58  ◀ hard step
    have n8 : (Q → ((Q ∧ R) → ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q))) := (fun (n4 : Q) => by                  -- r0  -3.46 → r8  -3.30
      have n7 : ((Q ∧ R) → ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q)) := (fun (n5 : (Q ∧ R)) => by                -- r0  -1.92 → r8  -0.26
        have n6 : ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q) := Or.inr n4                                          -- r0  -0.37 → r8  -3.82
        exact n6)                                                                                       -- r0  -0.00 → r8  -0.00
      exact n7)                                                                                         -- r0  -0.00 → r8  -0.00
    exact n8)                                                                                           -- r0  -0.00 → r8  -0.01
  exact n9                                                                                              -- r0  -0.01 → r8  -0.00
```

Eventual proof (r8's most likely accepted sample; worst step r0 -6.33 → r8 -1.58):

```lean
theorem t (P Q R S : Prop) (h1 : Q) (h2 : (Q ∨ (P → R))) : ((R ∧ Q) → (Q → ((Q ∧ R) → ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q)))) := by
  have n1 : Q := h1                                                                                      -- r0  -0.00 → r8  -0.00
  have n2 : (Q ∨ (P → R)) := h2                                                                          -- r0  -0.01 → r8  -0.00
  have n10 : ((R ∧ Q) → (Q → ((Q ∧ R) → ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q)))) := (fun (n3 : (R ∧ Q)) => by  -- r0  -6.33 → r8  -1.58  ◀ hard step
    have n4 : (Q ∨ (S ∨ (Q ∨ (P → R)))) := Or.inl n1                                                     -- r0  -5.06 → r8  -0.77
    have n9 : (Q → ((Q ∧ R) → ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q))) := (fun (n5 : Q) => by                   -- r0  -2.35 → r8  -1.05
      have n8 : ((Q ∧ R) → ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q)) := (fun (n6 : (Q ∧ R)) => by                 -- r0  -1.86 → r8  -0.17
        have n7 : ((Q ∨ (S ∨ (Q ∨ (P → R)))) ∨ Q) := Or.inl n4                                           -- r0  -0.07 → r8  -0.11
        exact n7)                                                                                        -- r0  -0.00 → r8  -0.00
      exact n8)                                                                                          -- r0  -0.00 → r8  -0.00
    exact n9)                                                                                            -- r0  -0.00 → r8  -0.00
  exact n10                                                                                              -- r0  -0.01 → r8  -0.00
```

## 10. box:imp — c6, group B (solved by RL) — `la_transfer_1390`

Hard step 5: r0 -9.31 → r8 -1.44 nats (gain +7.88; median of 19 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : (P → R)) (h2 : P) (h3 : (((¬P) ∨ (P → P)) ∨ ((P → P) ∧ Q))) : ((¬(¬P)) → (((¬P) ∨ (P → P)) ∧ R)) := by
  have n1 : (P → R) := h1                                                     -- r0  -0.00 → r8  -0.00
  have n2 : P := h2                                                           -- r0  -0.00 → r8  -0.00
  have n3 : (((¬P) ∨ (P → P)) ∨ ((P → P) ∧ Q)) := h3                          -- r0  -0.01 → r8  -0.00
  have n10 : ((¬(¬P)) → (((¬P) ∨ (P → P)) ∧ R)) := (fun (n4 : (¬(¬P))) => by  -- r0  -0.24 → r8  -1.27
    have n6 : (P → P) := (fun (n5 : P) => by                                  -- r0  -9.31 → r8  -1.44  ◀ hard step
      exact n5)                                                               -- r0  -0.02 → r8  -0.95
    have n7 : ((¬P) ∨ (P → P)) := Or.inr n6                                   -- r0  -0.62 → r8  -0.49
    have n8 : R := n1 n2                                                      -- r0  -0.56 → r8  -0.01
    have n9 : (((¬P) ∨ (P → P)) ∧ R) := ⟨n7, n8⟩                              -- r0  -0.11 → r8  -0.00
    exact n9)                                                                 -- r0  -0.05 → r8  -0.00
  exact n10                                                                   -- r0  -0.00 → r8  -0.00
```

Eventual proof (r8's most likely accepted sample; worst step r0 -4.80 → r8 -0.82):

```lean
theorem t (P Q R S : Prop) (h1 : (P → R)) (h2 : P) (h3 : (((¬P) ∨ (P → P)) ∨ ((P → P) ∧ Q))) : ((¬(¬P)) → (((¬P) ∨ (P → P)) ∧ R)) := by
  have n1 : (P → R) := h1                                                         -- r0  -0.00 → r8  -0.00
  have n2 : P := h2                                                               -- r0  -0.00 → r8  -0.00
  have n3 : (((¬P) ∨ (P → P)) ∨ ((P → P) ∧ Q)) := h3                              -- r0  -0.01 → r8  -0.00
  have n4 : R := n1 n2                                                            -- r0  -1.68 → r8  -0.67
  have n12 : ((¬(¬P)) → (((¬P) ∨ (P → P)) ∧ R)) := (fun (n5 : (¬(¬P))) => by      -- r0  -0.00 → r8  -0.00
    have n10 : ((¬P) ∨ (P → P)) := Or.elim n3 (fun (n6 : ((¬P) ∨ (P → P))) => by  -- r0  -4.80 → r8  -0.04
      exact n6) (fun (n7 : ((P → P) ∧ Q)) => by                                   -- r0  -0.08 → r8  -0.00
      have n8 : (P → P) := n7.1                                                   -- r0  -4.02 → r8  -0.82  ◀ hard step
      have n9 : ((¬P) ∨ (P → P)) := Or.inr n8                                     -- r0  -0.06 → r8  -0.00
      exact n9)                                                                   -- r0  -0.47 → r8  -0.00
    have n11 : (((¬P) ∨ (P → P)) ∧ R) := ⟨n10, n4⟩                                -- r0  -0.11 → r8  -0.00
    exact n11)                                                                    -- r0  -0.00 → r8  -0.00
  exact n12                                                                       -- r0  -0.00 → r8  -0.00
```

## 11. or_intro — c12, group B (solved by RL) — `la_transfer_980`

Hard step 6: r0 -4.33 → r8 -2.02 nats (gain +2.31; median of 1 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : ((S ∨ (Q ∨ S)) ∧ (S ∨ Q))) : (S ∨ ((Q ∨ S) ∧ Q)) := by
  have n1 : ((S ∨ (Q ∨ S)) ∧ (S ∨ Q)) := h1                        -- r0  -0.00 → r8  -0.00
  have n2 : (S ∨ Q) := n1.2                                        -- r0  -1.74 → r8  -0.48
  have n9 : (S ∨ ((Q ∨ S) ∧ Q)) := Or.elim n2 (fun (n3 : S) => by  -- r0  -0.51 → r8  -0.11
    have n4 : (S ∨ ((Q ∨ S) ∧ Q)) := Or.inl n3                     -- r0  -0.25 → r8  -0.02
    exact n4) (fun (n5 : Q) => by                                  -- r0  -0.00 → r8  -0.00
    have n6 : (Q ∨ S) := Or.inl n5                                 -- r0  -4.33 → r8  -2.02  ◀ hard step
    have n7 : ((Q ∨ S) ∧ Q) := ⟨n6, n5⟩                            -- r0  -8.67 → r8  -7.95
    have n8 : (S ∨ ((Q ∨ S) ∧ Q)) := Or.inr n7                     -- r0  -0.05 → r8  -0.01
    exact n8)                                                      -- r0  -0.00 → r8  -0.00
  exact n9                                                         -- r0  -0.00 → r8  -0.00
```

Eventual proof (r8's most likely accepted sample; worst step r0 -4.80 → r8 -1.43):

```lean
theorem t (P Q R S : Prop) (h1 : ((S ∨ (Q ∨ S)) ∧ (S ∨ Q))) : (S ∨ ((Q ∨ S) ∧ Q)) := by
  have n1 : ((S ∨ (Q ∨ S)) ∧ (S ∨ Q)) := h1                           -- r0  -0.00 → r8  -0.00
  have n2 : (S ∨ Q) := n1.2                                           -- r0  -1.74 → r8  -0.48
  have n14 : (S ∨ ((Q ∨ S) ∧ Q)) := Or.elim n2 (fun (n3 : S) => by    -- r0  -0.51 → r8  -0.11
    have n4 : (S ∨ ((Q ∨ S) ∧ Q)) := Or.inl n3                        -- r0  -0.25 → r8  -0.02
    exact n4) (fun (n5 : Q) => by                                     -- r0  -0.00 → r8  -0.00
    have n6 : (S ∨ (Q ∨ S)) := n1.1                                   -- r0  -4.34 → r8  -0.25
    have n13 : (S ∨ ((Q ∨ S) ∧ Q)) := Or.elim n6 (fun (n7 : S) => by  -- r0  -4.80 → r8  -1.43  ◀ hard step
      have n8 : (S ∨ ((Q ∨ S) ∧ Q)) := Or.inl n7                      -- r0  -0.02 → r8  -0.00
      exact n8) (fun (n9 : (Q ∨ S)) => by                             -- r0  -0.00 → r8  -0.00
      have n10 : Q := n5                                              -- r0  -0.15 → r8  -0.13
      have n11 : ((Q ∨ S) ∧ Q) := ⟨n9, n10⟩                           -- r0  -4.70 → r8  -0.24
      have n12 : (S ∨ ((Q ∨ S) ∧ Q)) := Or.inr n11                    -- r0  -0.12 → r8  -0.00
      exact n12)                                                      -- r0  -0.02 → r8  -0.00
    exact n13)                                                        -- r0  -0.00 → r8  -0.00
  exact n14                                                           -- r0  -0.00 → r8  -0.00
```

## 12. or_intro — c6, group B (solved by RL) — `la_transfer_977`

Hard step 4: r0 -7.97 → r8 -1.41 nats (gain +6.56; median of 12 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : ((R → R) ∧ (S ∧ R))) : ((¬(¬Q)) → ((¬(P ∨ ((R → R) ∧ (S ∧ R)))) → (¬Q))) := by
  have n1 : ((R → R) ∧ (S ∧ R)) := h1                                                                  -- r0  -0.00 → r8  -0.00
  have n8 : ((¬(¬Q)) → ((¬(P ∨ ((R → R) ∧ (S ∧ R)))) → (¬Q))) := (fun (n2 : (¬(¬Q))) => by             -- r0  -0.37 → r8  -0.09
    have n7 : ((¬(P ∨ ((R → R) ∧ (S ∧ R)))) → (¬Q)) := (fun (n3 : (¬(P ∨ ((R → R) ∧ (S ∧ R))))) => by  -- r0  -0.27 → r8  -0.02
      have n4 : (P ∨ ((R → R) ∧ (S ∧ R))) := Or.inr n1                                                 -- r0  -7.97 → r8  -1.41  ◀ hard step
      have n5 : False := n3 n4                                                                         -- r0  -2.81 → r8  -1.56
      have n6 : (¬Q) := n5.elim                                                                        -- r0  -2.12 → r8  -0.08
      exact n6)                                                                                        -- r0  -0.08 → r8  -0.15
    exact n7)                                                                                          -- r0  -0.00 → r8  -0.00
  exact n8                                                                                             -- r0  -0.00 → r8  -0.00
```

Eventual proof (r8's most likely accepted sample; worst step r0 -7.97 → r8 -1.41):

```lean
theorem t (P Q R S : Prop) (h1 : ((R → R) ∧ (S ∧ R))) : ((¬(¬Q)) → ((¬(P ∨ ((R → R) ∧ (S ∧ R)))) → (¬Q))) := by
  have n1 : ((R → R) ∧ (S ∧ R)) := h1                                                                  -- r0  -0.00 → r8  -0.00
  have n9 : ((¬(¬Q)) → ((¬(P ∨ ((R → R) ∧ (S ∧ R)))) → (¬Q))) := (fun (n2 : (¬(¬Q))) => by             -- r0  -0.37 → r8  -0.09
    have n8 : ((¬(P ∨ ((R → R) ∧ (S ∧ R)))) → (¬Q)) := (fun (n3 : (¬(P ∨ ((R → R) ∧ (S ∧ R))))) => by  -- r0  -0.27 → r8  -0.02
      have n4 : (P ∨ ((R → R) ∧ (S ∧ R))) := Or.inr n1                                                 -- r0  -7.97 → r8  -1.41  ◀ hard step
      have n7 : (¬Q) := (fun (n5 : Q) => by                                                            -- r0  -4.11 → r8  -0.26
        have n6 : False := n3 n4                                                                       -- r0  -1.51 → r8  -0.02
        exact (n6 : False))                                                                            -- r0  -0.06 → r8  -0.01
      exact n7)                                                                                        -- r0  -0.03 → r8  -0.33
    exact n8)                                                                                          -- r0  -0.00 → r8  -0.00
  exact n9                                                                                             -- r0  -0.00 → r8  -0.00
```

## 13. and_proj — c12, never solved r1–r8 — `textbook_9fa52f90369a7b6286f7`

Hard step 3: r0 -5.54 → r8 -0.84 nats (gain +4.71; median of 1 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop) (h1 : ((P → (¬(¬Q))) ∧ ((¬(¬Q)) → P))) : ((P → Q) ∧ (Q → P)) := by
  have n1 : ((P → (¬(¬Q))) ∧ ((¬(¬Q)) → P)) := h1               -- r0  -0.01 → r8  -0.00
  have n6 : (P → Q) := (fun (n2 : P) => by                      -- r0  -2.57 → r8  -4.62
    have n3 : (P → (¬(¬Q))) := n1.1                             -- r0  -5.54 → r8  -0.84  ◀ hard step
    have n4 : (¬(¬Q)) := n3 n2                                  -- r0  -2.58 → r8  -0.28
    have n5 : Q := Classical.byContradiction (fun hh => n4 hh)  -- r0  -0.17 → r8  -0.12
    exact n5)                                                   -- r0  -0.00 → r8  -0.00
  have n13 : (Q → P) := (fun (n7 : Q) => by                     -- r0  -1.30 → r8  -0.47
    have n8 : ((¬(¬Q)) → P) := n1.2                             -- r0  -5.27 → r8  -6.99
    have n11 : (¬(¬Q)) := (fun (n9 : (¬Q)) => by                -- r0  -6.40 → r8  -7.71
      have n10 : False := n9 n7                                 -- r0  -0.15 → r8  -0.00
      exact (n10 : False))                                      -- r0  -0.00 → r8  -0.00
    have n12 : P := n8 n11                                      -- r0  -0.18 → r8  -0.01
    exact n12)                                                  -- r0  -0.00 → r8  -0.00
  have n14 : ((P → Q) ∧ (Q → P)) := ⟨n6, n13⟩                   -- r0  -0.83 → r8  -0.03
  exact n14                                                     -- r0  -0.00 → r8  -0.01
```

## 14. app — c12, never solved r1–r8 — `la_transfer_795`

Hard step 7: r0 -4.51 → r8 -1.62 nats (gain +2.90; median of 3 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop)  : (((R ∨ P) → (¬P)) ∨ (¬((R ∨ P) → (¬P)))) := by
  have n8 : (¬(¬(((R ∨ P) → (¬P)) ∨ (¬((R ∨ P) → (¬P)))))) := (fun (n1 : (¬(((R ∨ P) → (¬P)) ∨ (¬((R ∨ P) → (¬P)))))) => by  -- r0  -3.80 → r8 -23.50
    have n5 : (¬((R ∨ P) → (¬P))) := (fun (n2 : ((R ∨ P) → (¬P))) => by                                                      -- r0  -7.54 → r8  -9.98
      have n3 : (((R ∨ P) → (¬P)) ∨ (¬((R ∨ P) → (¬P)))) := Or.inl n2                                                        -- r0  -0.61 → r8  -0.03
      have n4 : False := n1 n3                                                                                               -- r0  -4.31 → r8  -0.73
      exact (n4 : False))                                                                                                    -- r0  -0.00 → r8  -0.00
    have n6 : (((R ∨ P) → (¬P)) ∨ (¬((R ∨ P) → (¬P)))) := Or.inr n5                                                          -- r0  -1.07 → r8  -0.03
    have n7 : False := n1 n6                                                                                                 -- r0  -4.51 → r8  -1.62  ◀ hard step
    exact (n7 : False))                                                                                                      -- r0  -0.00 → r8  -0.00
  have n9 : (((R ∨ P) → (¬P)) ∨ (¬((R ∨ P) → (¬P)))) := Classical.byContradiction (fun hh => n8 hh)                          -- r0  -0.03 → r8  -0.00
  exact n9                                                                                                                   -- r0  -0.00 → r8  -0.01
```

## 15. box:neg — c12, never solved r1–r8 — `la_transfer_2097`

Hard step 2: r0 -7.83 → r8 -9.04 nats (gain -1.21; median of 14 such theorems).

Reference proof:

```lean
theorem t (P Q R S : Prop)  : ((((S ∧ Q) → (¬R)) → (S ∧ Q)) → (S ∧ Q)) := by
  have n11 : ((((S ∧ Q) → (¬R)) → (S ∧ Q)) → (S ∧ Q)) := (fun (n1 : (((S ∧ Q) → (¬R)) → (S ∧ Q))) => by  -- r0  -0.64 → r8  -0.00
    have n9 : (¬(¬(S ∧ Q))) := (fun (n2 : (¬(S ∧ Q))) => by                                              -- r0  -7.83 → r8  -9.04  ◀ hard step
      have n6 : ((S ∧ Q) → (¬R)) := (fun (n3 : (S ∧ Q)) => by                                            -- r0 -11.04 → r8  -0.31
        have n4 : False := n2 n3                                                                         -- r0  -3.24 → r8  -0.31
        have n5 : (¬R) := n4.elim                                                                        -- r0  -0.12 → r8  -0.25
        exact n5)                                                                                        -- r0  -0.00 → r8  -0.00
      have n7 : (S ∧ Q) := n1 n6                                                                         -- r0  -0.58 → r8  -0.01
      have n8 : False := n2 n7                                                                           -- r0  -0.24 → r8  -0.00
      exact (n8 : False))                                                                                -- r0  -0.00 → r8  -0.00
    have n10 : (S ∧ Q) := Classical.byContradiction (fun hh => n9 hh)                                    -- r0  -0.78 → r8  -0.00
    exact n10)                                                                                           -- r0  -0.00 → r8  -0.05
  exact n11                                                                                              -- r0  -0.01 → r8  -0.29
```

