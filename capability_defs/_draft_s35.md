### 3.5 Families: the classical schemata and the excluded-middle case

**Family-level verdicts.**
- Families are the 19 textbook schemata of `rl_targets` / transfer, with 40 trained-on and 40 held-out members each.
- After the critic, classical families keep only the members that need the classical step (not provable by the G4ip
  decision procedure).
- Shares are the per-round fraction of the family's training targets with ≥ 1 success in 32 attempts; round 1
  samples pend.

| family (key-step members) | pend, round 1 (s0 / s1 / s2) | r16 | verdict | cap 6 r16 |
|---|---|---|---|---|
| excluded middle (39) | 0.00 / 0.00 / 0.00 | 0.00 / **0.95** / 0.26 | created on s1 only | 0.00 / 0.00 / 0.00 |
| Peirce (15) | 0.00 / 0.00 / 0.00 | 0.00 / 0.27 / **1.00** | created on s2 only | 0.00 / 0.00 / 0.00 |
| Peirce sequent (20) | 0.00 / 0.00 / 0.05 | 0.30 / 0.05 / **1.00** | created on s2 only | 0 |
| negated conditional, classical members (20) | 0.05 / 0.00 / 0.00 | 1.00 / 0.65 / 1.00 | created on 3 / 3 | 0.10 / 0.10 / 0.05 |
| distribution ∧ over ∨ (40; intuitionistic) | 0.00 / 0.00 / 0.00 | 0.97 / 1.00 / 0.93 | created on 3 / 3 | 0.93 / 0.50 / 0.97 |
| De Morgan ¬(A ∧ B) ⊢ ¬A ∨ ¬B, classical members (13) | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | never acquired | 0 |

These verdicts are relative to pend's 32 round-1 attempts. The held-out members agree where read:
- excluded middle at r16, 39 classical-only held-out instances at k 256: 0 / 36 / 13 solved (s0 / s1 / s2);
- the six holdout250 excluded-middle members: pend 0 / 6 at ≥ 768 attempts on every seed; s1 r16 6 / 6.

**Each seed acquires different families.** Excluded middle appears on one seed (bursting at rounds 13–14), Peirce on
another. That is the strongest evidence in this run that RL *can* produce a family-level capability its own base
lacks. It is also a warning: "RL creates X" is a per-run event, not a property of the recipe, at n = 3.

**Is the excluded-middle schema latent or teachable?** (J4, J6, J6b; 39 classical-only held-out instances, k 256)

| model (cap 12) | s0 | s1 | s2 |
|---|---|---|---|
| pend | 0 | 0 | 0 |
| pend + fine-tune on replay only (A0) | 0 | 0 | 0 |
| pend + 16 non-LEM proofs (C16) | 0 | 0 | 0 |
| **pend + 4 LEM proofs (A4)** | **36** (0.66) | **33** (0.35) | **36** (0.64) |
| **pend + 16 LEM proofs (A16)** | **37** (0.79) | **34** (0.68) | **37** (0.83) |
| RL r16 | 0 | 36 (0.70) | 13 (0.13) |
| no-DN knockout (pretrained without any classical step) | 0 | 0 | 0 |
| knockout + 16 LEM proofs, full-K12 replay | 35 (0.71) | 37 (0.72) | 37 (0.70) |
| knockout + 16 LEM proofs, DN-free replay (J6b) | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ |

Cells: solved of 39, with mean pass@1 in parentheses.

- Four demonstrations, taken from s1's RL proofs of *other* instances and used in one ladder-style fine-tune, install
  the schema on every seed's base. That includes s0, whose own RL never found it in 16 rounds.
- A model that never saw a classical step in pretraining learns it just as fast from the same 16 demonstrations.
- The same 16 demonstrations also raise holdout250 solved@64 by +12 / +15 / +5 over the replay-only fine-tune.

**What RL "created" here is the discovery of an instance, not a hard-to-learn ability.** Once a proof exists, the
pattern is cheap to teach.
