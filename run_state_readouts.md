# state-readouts (2026-09-30), no training

Lean alone; 3.2 M-param from-scratch state policies; `numbers.md` § state-readouts. 22.67 pod-hours, $11.25.

## A. State or environment naming?

Stage-1 bases, 29 survivors, support-state's protocol:

| arm | names | reached s0 / s1 |
|---|---|---|
| whole-proof (inherited) | own | 0 |
| **S** (state) | own | **28 / 25** |
| **SH** (state + history) | own | **21 / 15**† |
| SN (inherited) | environment | 28 / 28 |

† T 1.0 phase cut at 10 of 16 rows by the pre-registered budget line (≤ 21).

S differs from SN only in naming and reaches 28 / 25, so **seeing the state is what matters**. Naming is worth ≤ ≈ 3
theorems at n = 2. SH (≥ 18) misses the joint "both ≥ 20" rule, so the letter reads "in between"; SH names like S, so its shortfall
is from history, not naming.

## B. SN-cap12 on the dead textbook schemata

k 256, T 0.8, `max_steps` 96. Of the 12 schemata at ≤ 2 in every whole-proof arm, **11 reach ≥ 5 on every T1 seed**
(frozen 6 / 10 / 10 / 9). Excluded middle stays at 0–1.

Post hoc, classical-only instances (`intuit.py`): **0 / 39 excluded middle, 0 / 13 Peirce, 0–1 / 19 Peirce-sequent**, in
all 8 checkpoints. The Peirce solves are its intuitionistic instances. The one excluded-middle solve is degenerate:

```lean
theorem t (Q R : Prop) : ((Q ∧ R) ∧ ¬R) ∨ ¬((Q ∧ R) ∧ ¬R) := by
  have n27 : ¬((Q ∧ R) ∧ ¬R) := fun n28 => by
    have n29 : Q ∧ R := n28.1; have n30 : R := n29.2; have n31 : ¬R := n28.2
    exact n31 n30
  exact Or.inr n27
```

Classical steps occur elsewhere (contraposition_conv 22–23 / 23; 6 long Peirce instances, T1 s0).

## Expected vs outcome

- Hits: A1 (S 24, 17–29), A2 (SH 21, 12–28), A4, B1, B2, B5.
- A3: the joint reading is "in between", not the state band (0.65).
- A6 action cap ≤ 0.1 %: **miss** (S s1 0.75 %, SH 0.30 / 0.57 %). At cap 1,024, S s1's zeros stay zero. SH s1's
  `1858` (14 % cut) is unchecked.
- B3: frozen s0 275 < 280, miss. B4: ≥ 5 on 5 of 6 long schemata, **miss on 3 of 4 seeds**.

Limits: n = 2 per arm in A; no noise floor here.
