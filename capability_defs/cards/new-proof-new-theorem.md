# Card: new proof vs new theorem

Family L / S. Slug `new-proof-new-theorem`. Notation: `_FRAME.md`.

## 1. Definition, formally

Two binary properties for each theorem t that R solves, at budget K:

- **New theorem (NT).** The base cannot prove t within K: certified p_B(t) < 0.05 / K (`marginal-bracket` upper bound),
  or (weaker) the lower bound is < 1 / K.
- **New proof (NP).** RL's typical proofs of t are routes the base would not take within K. Formally, the share of R's
  success mass on proofs with π_B(y) < 1 / K is at least 1/2:

  ρ(t) = Σ_{y ∈ F(t), π_B(y) < 1/K} π_R(y) / Σ_{y ∈ F(t)} π_R(y) ≥ 1/2,

  computed after **removing vacuous detours** (a self-built disjunction immediately eliminated, an unused box).
  Padding must not count as novelty (`tf-proof-prob` critic).

| | NP: no (RL uses base routes) | NP: yes (RL uses new routes) |
|---|---|---|
| **NT: no** (base can prove t) | sharpened access (elicitation) | new proof of an old theorem |
| **NT: yes** (base cannot) | impossible in principle (a base route within K would make NT false) | **new theorem**: the creation cell |

## 2. Decision rule

| verdict | rule |
|---|---|
| **created** | NT ∧ NP |
| **elicited** | ¬NT ∧ ¬NP |
| **"new route, old theorem"** | ¬NT ∧ NP: reported separately, not counted as capability creation |
| **neither** | R fails |

## 3. Null or floor

- Both properties are budget-relative; random weights fail NT for every theorem at any feasible K.
- The detour filter is a floor on "new route": a proof is not new just because it is longer.

## 4. How to compute it here

- J1 gives π_B and π_R for every known proof of each seed's hard and calibration theorems (stage 1 at one base; stage
  2 exact for the top proofs).
- J2 gives the sampling upper bound for NT.
- The detour filter is a syntactic pass over the ND proof:
  - an ORI whose disjunction is the major premise of an ORE that immediately follows;
  - unused assumptions (the reads' `pruned` form).
- **First numbers** (existing scores, theorem level; `out/defs_c12.txt`; T 0.8; r8, draw x0):
  - RL's eventual proof is below 1 / K_total under pend for 46 / 34 / 40 theorems, but pend itself solves many of them
    at k 256. Of the 120 (seed, theorem) pairs the `tf-proof-prob` critic examined: 31 solved by pend at k 256, 63 with
    a reference ≥ 1 / K_total, 35 with an Or-detour.
  - So most "new proofs" sit in the "new route, old theorem" or "elicited" cells. The NT ∧ NP cell needs J1 + J2 and
    is computed in Part 3.
- **Cost:** CPU, once J1 / J2 are pulled.

## 5. Sensitivity

- **K** moves both lines. At K_total almost no hard theorem is NT-certified (sampling cannot certify it).
- **Temperature:** T 0.8 for both π terms.
- **Proof set F:** ρ uses F as a stand-in for R's support. The coverage check Σ_F π_R / p̂_R must be high, or ρ is
  undefined.
- **Representation and renaming:** as in `tf-proof-prob`.
- **Noise:** ρ is deterministic given F. NT inherits binomial noise.

## 6. Failure modes

- **What counts as a "different route"** (detours, line order, redundant restatements) is a definitional choice, and ρ
  changes with the filter.
- **Selection.** F is built from RL's own samples, so it over-represents R's routes. That is fine for ρ (it measures R's
  mass), but it means the base's best route may be missing from F. Add the base's own J2 samples.
- **NT is rarely certifiable** (see `passk-budget`), so the creation cell is mostly "undetermined".

## 7. Relations

- The theorem axis is `marginal-bracket` / `passk-budget`; the proof axis is `tf-proof-prob` (route tag) and
  `sharpen-expand` (ρ is the expansion share).
- The four cells are the cleanest way to explain why "RL's proofs are improbable under the base" (reading group,
  2026-09-17) and "RL created a capability" are different claims.

## 8. Literature anchor

- **Yue et al. 2025** (earlier review): base perplexity of RL outputs, Sec. 4.
- **Korbak et al. 2022 (2205.11275):** pure conditioning keeps the base's odds among correct outputs (Sec. 5; L5
  note).
- **Shin et al. 2023 (2303.07462):** novelty = the first point where a sequence leaves the database, read with engine
  quality (L6 note).
- **Silver et al. 2017 (AlphaGo Zero):** stronger play that predicts human moves worse (Extended Data Table 1; L6 note).
- **Reading group 2026-09-17:** "Can we quantify the novelty of a proof, relative to prior proofs seen?"

## 9. Critic's verdict

*(pending)*
