# next_steps — create-or-elicit (draft 2026-10-12 15:20 UTC; revised at DONE)

Costed proposals beyond this run's $140, ranked by what they would teach us. Costs at today's A40 price ($0.59 / h) and
this run's measured ladder time (16 rounds ≈ 14–16 A40-hours with reads beside the ladder; ≈ $9 per seed).

## 1. Dose-response on σ (the crossover) — ≈ $30 per dose level (3 seeds), $60 for two
- **Question:** below which share of σ in pretraining does EI stop acquiring the classical families? Full exposure is
  10.8 % (16,703 / 155,000 records); the knockout is 0 %. Interplay (2512.07783) found RL transfers only above ≈ 1 %
  atomic exposure; our dose is a *composition*, both of whose atoms stay at full exposure.
- **Design:** `coe/coe_dose.py` builds K12^d by swapping refill records for removed σ records with K12's length mix
  (1 % set already built: `data/coe/train_k12dose1.jsonl.gz`, in the bucket). Doses 1 % and 0.1 %, 3 seeds each, the same
  16-round protocol, the same read-outs (strict σ-covered held-out members at k 256, σ subtypes per round).
- **Decision value:** locates the threshold between "needs exposure" and "elicited" on a log scale.

## 2. Exploration from the knockout bases — ≈ $30–60
- The knockout bases *can* write the free reductio (≈ 10⁻⁵ per attempt at T 1.0 on a theorem whose premise invites ¬G),
  and the ladders amplify scaffolded σ, yet EI at T 0.8 never trains on a free σ proof of a strict target. Three cheap
  levers, each a 6-seed, 16-round arm or a continuation of this run's r16 checkpoints:
  - **T 1.0 rollouts** (the base's free-σ hits happen at T 1.0, never in 131,072 at T 0.8);
  - **guided rollouts** (proposal 24 Part B: step-checked redraws in RL; ≈ $15–20 per 3 seeds at 8 rounds);
  - **ε after return** at states with a positive goal (proposal 20): replace the next action by "assume ¬G" with prob ε.
- **Decision value:** separates "this EI cannot create σ" from "RL with exploration creates σ from a σ-free base".

## 3. Seeded-round transfer (Phase 3a here, if run) at scale — ≈ $10
- If one self-found free-σ proof in one EI round teaches the families (Phase 3a), repeat with each knockout seed's own
  first σ proofs and with proofs from different families, to measure how much of a family one instance unlocks.

## 4. GRPO vs EI from the knockout bases — ≈ $40 (3 seeds × 16 rounds)
- Abdulsalam et al. (2607.07646) find GRPO creates shortcuts that RFT-style training plateaus on; our EI is RFT-like.
  `grpo_state.py` exists (run `grpo-state`). Same knockout bases, same targets, matched attempts per round.

## 5. More seeds for the arm comparison — ≈ $9 per seed
- The primary test is powered for families the full arm acquires on most seeds; excluded middle and Peirce (1 seed in 3
  in the full arm) need ≈ 12–15 seeds per arm for 80 % power.

## 6. Harder target pool from our own generator — ≈ $20
- 13–20-line, classical-heavy, disjoint by renaming class; tests the "targets are ≈ 98 % saturated" objection.

## 7. Interface pilot (whole proof vs proof state, same data and RL) — ≈ $25
- The older 3.2 M organism's "a proof-state base reaches 28 of 29" confounds the state with step-by-step generation.
