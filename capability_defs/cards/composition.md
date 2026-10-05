# Card: composition of skills that each exist in the base

Families T / N. Slug `composition`. Notation: `_FRAME.md`.

## 1. Definition, formally

A proof is a sequence of moves; a move is a (state → action) decision.

- **Step-level support of the base:** move a_j at state s_j is "known" if π_B(a_j | s_j) ≥ ε_step. ε_step is the
  per-step budget: with guided redraws up to 10 rejections per step, ε_step ≈ 1/10–1/30; for plain sampling the step
  must also fit in the whole-proof budget.
- **A composite capability on t is "a new composition"** if, for RL's proof y_R (detours removed):
  - every move is in the base's step-level support (w1 under π_B ≥ log ε_step);
  - yet the whole proof is outside the base's reach (log π_B(y_R) < −ln K, and the theorem-level bracket agrees).
- **"A new move"** if some move of y_R is outside step-level support at its state.
- **Multiplicative null** (Okawa et al.): if components succeed independently with probabilities p_j, the composite
  succeeds with ≈ Π_j p_j. A composite whose base probability is far below the product of its components' base
  probabilities (in the contexts where they occur) has an interaction cost.

## 2. Decision rule

| verdict | rule |
|---|---|
| **created by composition** | all moves known (w1 ≥ log ε_step) and the theorem out of reach at K. RL created the capability by composing old skills, the most common kind of "creation" this definition expects |
| **created by a new move** | some move outside step support (w1 < log ε_step) and the theorem out of reach |
| **elicited** | the theorem within reach at K |
| **neither** | R fails |

## 3. Null or floor

- The multiplicative model is the null for "emergence" of composites: sudden jumps in composite success are expected
  when every component improves smoothly.
- Random weights fail every step (per-step log p ≈ −200 nats at init).

## 4. How to compute it here

- **Step log p** of RL's proofs under pend: J1 (per-step at one base, stage 1; exact for the top proofs). Trajectory's
  scores give the eventual proofs' worst steps at pend.
- **Existing numbers** (`trajectory`, B group at cap 12, IQM): worst step at pend −6.2 nats (≈ 1 in 500), with
  everything else in the proof ≈ 7–9 nats. **By this card, most of B is "new composition of known moves", or elicited**:
  no single step is beyond a guided budget of 1 / 500, but the product is ≈ e^(−15).
- At cap 6 the worst step at pend was ≈ 1 in 22,000–25,000 (`trajectory-cap6`; `claim-audit` C5b), so more "new move"
  cases there.
- **Excluded middle:** is the DN step (`Classical.byContradiction` on a ¬¬-goal) in pend's step support at those states?
  This is answered by J1 for the holdout250 members.

## 5. Sensitivity

- **ε_step:** the decoder decides it (plain vs guided).
- **Route:** another proof of t may have no out-of-support step.
- **Representation:** in the proof-state interface the environment writes some tokens (box closings), so the moves
  differ from whole-proof moves.
- **Temperature:** T 0.8.
- **Name conditioning** (scorer vs sampler; `tf-proof-prob`).

## 6. Failure modes

- **"Known move" is state-relative:** a move known in some states may be unknown in the RL proof's states. The test is
  per state, as defined.
- **Compositions can be trivial** (padding).
- **The multiplicative null assumes independence,** which proofs violate (later steps depend on earlier choices).

## 7. Relations

- Splits the created cell of `passk-budget` / `marginal-bracket` into two kinds.
- `tf-proof-prob`'s step level gives the moves.
- `schema-acquisition` says which compositions recur.
- `chain-reachability` explains how compositions are found: one step of reach at a time.

## 8. Literature anchor

- **Okawa et al. 2023 (2310.09336):** "Compositional Abilities Emerge Multiplicatively", P(n) = (1 − (1 − p)^t)^n
  (Sec. 4; L5 note).
- **Arora & Goyal 2023 (2307.15936):** skill tuples and competence (Def. 7, Cor. 13).
- **Yu et al. 2023, Skill-Mix (2310.17567).**
- **Mousavi-Hosseini & Erdogdu 2026 (2603.06957):** process-reward RL is limited by the base's worst-token quantile,
  which is our w1 (Sec. 4).
- **Earlier review:** Yuan et al. 2025 "From f(x) and g(x) to f(g(x))" (RL composes old skills).
- **Project:** `lit-measures` (one bad step), `trajectory` (worst step), `organism-analysis` (hard steps).

## 9. Critic's verdict

*(pending)*
