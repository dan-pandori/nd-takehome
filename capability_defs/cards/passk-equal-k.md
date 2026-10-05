# Card: equal-k support (the field's standard: Yue et al.)

Family S. Slug `passk-equal-k`. Notation: `_FRAME.md`.

## 1. Definition, formally

- Sample k attempts from the base B and from the RL model R on theorem t, with the same protocol (plain, T 0.8, read
  caps, Lean).
- **R created a capability on t at k** if B has 0 successes in k attempts and R has ≥ 1.
- Set level: the share of theorems in the 2 × 2 table (base solves / RL solves) at equal k, and the pass@k curves of B
  and R over k ≤ n (unbiased estimator).
- The "reasoning boundary" claim is that B's curve crosses R's at large k.
- Here k = 256, the project's standard read. This is the A / B / C split of `trajectory`: B = "R solves, base does
  not".

## 2. Decision rule

| verdict | rule |
|---|---|
| **created** | c_B = 0 / k and c_R ≥ 1 / k, defined on one draw and confirmed on an independent draw |
| **elicited** | c_B ≥ 1 / k and R's pass@1 is materially higher (more reliable access to an existing capability) |
| **neither** | R fails |

Set-level reading: a crossover of the curves at some k ≤ n ("the base catches up") is evidence of elicitation; no
crossover up to the largest k is evidence (weak) of creation.

## 3. Null or floor

**None built in.** The budget is k_eval, which is not tied to any cost, so the rule is exposed to Dan's objection: a
larger k for the base turns "created" into "elicited", and it does so for any model including random weights (in
principle). In practice the project answers this with `passk-budget`'s compute-tied K, or by reading B at k far above
R's training budget (`support-curves` used 4 × 10⁵).

## 4. How to compute it here

- **Free.** Every checkpoint has two k 256 draws on textbook72 + holdout250. r16 has only x1; J5 adds x0.
- **First numbers** (cap 12, `out/defs_c12.txt`):
  - Created at r8: 54 / 51 / 60 of 322 (s0 / s1 / s2; draw x0). At r16 (x1): 61 / 65 / 61.
  - Redraw Jaccard (x0 vs x1): 0.78 / 0.70 / 0.68.
  - Seed Jaccard: 0.34–0.39.

## 5. Sensitivity

- **k:** the whole verdict. In `support-curves` the survivor count fell 37 → 29 as base attempts rose from 4 × 10⁴ to
  2 × 10⁵ per temperature. J2 chunk 0: 4 of 8 created-at-256 theorems get base successes at 16,384.
- **Temperature and decoding:** T 1.0 rescued 19 theorems T 0.8 missed (`support-curves`). Guided redraws change
  solves (+5–9 pp).
- **Representation:** whole-proof vs proof-state flips 28 of 29 survivors (`support-state`).
- **Renaming:** one prompt per theorem. A renamed instance can flip a borderline theorem.
- **Noise:** borderline theorems (pass@256 ≈ 0.1–0.3 at pend) flip between draws. Selection on one draw biases the
  base's estimate on that draw down (`trajectory` obs. 6).

## 6. Failure modes

- It conflates "rare" with "absent". The created set shrinks without limit as the base's k grows.
- It ignores RL's training compute: RL can spend 10⁴× more samples per theorem in training than k_eval.
- Created sets defined by one draw are partly selection (5–10 % of B flip to A on a redraw; `trajectory-cap6`).
- An RL model that only sharpens (raises pass@1) produces "created" theorems at small k, wherever the base's p ≈ 1 / k.

## 7. Relations

- The special case K = k_eval of `passk-budget`.
- The same verdicts as `marginal-bracket` at K = 256.
- Its created set is a superset of `passk-budget`'s at any K ≥ 256.
- At equal k, the extra theorems R solves are what `reliability` treats as access.

## 8. Literature anchor

- **Yue et al. 2025** (2504.13837v5; earlier review): base models "consistently surpass RLVR models across all
  benchmarks and LLM families as k increases" (Sec. 1, re-verified by me with `quote.py`).
- **Brown et al. 2024** (coverage grows with samples).
- **Kulal et al. 2019** (the origin of pass@k; screened by L1).
- **Dragoi et al. 2025** (Cover@τ; earlier review).

## 9. Critic's verdict

*(pending)*
