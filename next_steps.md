# next_steps — create-or-elicit (final, 2026-10-13; UNREVIEWED)

Costed proposals beyond this run's $190, ranked by what they would teach us. Costs at this run's A40 price ($0.59 / h)
and measured times: a 16-round ladder with its reads beside it ≈ 15 A40-hours ≈ $9 per seed; with the post-ladder work
this run did (three k 256 reads, timing, large-k certificate, standard A) ≈ 22–27 pod-hours ≈ $13–16 per seed.

What this run leaves open (numbers in `numbers.md` § create-or-elicit): σ-free bases do not acquire the classical families
in 16 rounds of EI (0 / 6 vs 6 / 6), yet 5 / 6 of their ladders write the free reductio on their own, rarely, and
knockout s1's spread after r9 (DOSE_EXT_NEXT). A 1 % σ dose DOSE_NEXT.

## 1. The 0.1 % dose arm — ≈ $33 (3 seeds × 16 rounds, reads at pend and r16 only)
- **Question:** where between 0 % and 1 % does EI stop acquiring the families? The set is built and in the bucket
  (`data/coe/train_k12dose01.jsonl.gz`, 155 σ records; `coe/coe_dose.py`), the protocol is Addendum 5's.
- **Decision value:** a three-point dose curve on a log scale (0, 0.1 %, 1 %, 10.8 %). If 0.1 % behaves like 0 %, the
  "needs exposure" verdict has a threshold between 155 and 1,550 σ records in 155,000.

## 2. Exploration from the knockout bases — ≈ $30–60
- The knockout bases write the free reductio at ≈ 10⁻⁶ per attempt pooled over the family members (4 / 6 seeds) and at
  ≈ 10⁻³ on `la_transfer_916` at T 1.0. EI's k 32 gives ≈ 4,000 attempts per round on the 123 strict training targets,
  so ≈ 0.004 expected free-σ proofs per round at the base's rate. Three levers, each a 6-seed continuation from this
  run's r16 checkpoints (8 rounds ≈ $5 per seed) or a fresh 16-round arm:
  - **T 1.0 rollouts** (the bases' free-σ hits on `la_transfer_916` came at T 1.0; none in 131,072 at T 0.8 on s0);
  - **larger k on the targets the ladder fails** (k 256 on the ≈ 300 unsolved targets per round ≈ +25 % sampling time);
  - **ε after return** at states with a positive goal (proposal 20): replace the next action by "assume ¬G" with prob ε.
- **Decision value:** separates "EI as run cannot create σ" from "RL with more exploration creates σ from a σ-free base".

## 3. Longer knockout ladders — ≈ $5 per seed per 8 rounds
- Knockout s1's free reductio accelerated after r16 (29 → 74 proofs per round at r17–r20). Running every knockout seed to
  r32 would say whether onset turns into acquisition on its own, and how many rounds that costs — the "needs exposure"
  verdict is a statement about 16 rounds.

## 4. Exposure during RL instead of pretraining — ≈ $30 (3 seeds)
- Add the 1,550 dose records to the knockout ladders' replay (not to pretraining). If the families follow, exposure need
  not be in pretraining; if not, the base's prior is what matters. Same reads as the dose arm.

## 5. GRPO vs EI from the knockout bases — ≈ $40 (3 seeds × 16 rounds)
- Abdulsalam et al. (2607.07646) report GRPO finding behaviours RFT-style training plateaus on; our EI is RFT-like.
  `grpo_state.py` exists (run `grpo-state`). Same knockout bases, same targets, matched attempts per round.

## 6. More seeds for the per-family tests — ≈ $13–16 per seed
- The primary test is powered for families the full arm acquires on most seeds. Excluded middle (1 / 6 full seeds) and
  the 3 / 6 families (Holm 0.17) need ≈ 12–15 seeds per arm for 80 % power.

## 7. A harder target pool from our own generator — ≈ $20
- 13–20-line, classical-heavy, disjoint by renaming class; tests the "targets are ≈ 98 % saturated" objection.

## 8. Interface pilot (whole proof vs proof state, same data and RL) — ≈ $25
- The older 3.2 M organism's "a proof-state base reaches 28 of 29" confounds the state with step-by-step generation.

## Dropped
- **Phase 3a at scale.** One self-found free-σ proof added to one EI round changed nothing on 4 / 5 knockout seeds
  (s2: 2 vs 0 of 105, p 0.25). Seeding with a single proof is not the bottleneck; item 4 tests seeding at volume.
