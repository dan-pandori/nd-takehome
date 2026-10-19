# next_steps — kalmar-pretrain (2026-10-19; UNREVIEWED)

What this run leaves open (`numbers.md` § kalmar-pretrain):
- Pretraining a 9.56 M proof-state model on Kalmár proofs of K12's theorems (3.68 epochs) gives 94.5 % per-state
  agreement with the algorithm and 32.6 % greedy Lean-valid proofs on held-out theorems. The control, trained on K12's
  own short proofs, reaches 92 %.
- Agreement was still rising when training stopped.
- The errors are bookkeeping, not truth values: the next subformula, or a copying slip in a long formula.

Costs below use this run's prices (community RTX 3090 $0.22/h for training, A40 $0.59/h for sampled reads).

## 1. Train longer, or larger — ≈ $5–15 per arm
- **Question:** is "not learned" a data-scale or capacity limit? The learning curve (86.6 → 94.5 % agreement, greedy
  6.6 → 32.6 %) has not flattened.
- **Arms:**
  - KAL-D at 2× the steps (≈ 20 h per seed on a 3090, ≈ $4.5 per seed);
  - a ≈ 25 M model at 1× (≈ 2.5× the per-step time).
- **Read-out:** teacher-forced agreement and greedy exact-follow on `tf1200`. These are cheap: greedy reads only, 15
  min per model.
- **Decision value:** if agreement passes ≈ 99 % with 2× data, the construction is learnable at this scale and the
  bottleneck was compute. If it saturates near 95 %, the format or the model is the limit.

## 2. Let the environment restate premises — ≈ $1 (re-reads only)
- **Finding here:** the K12 control solves 177–191 of 200 four- and five-premise problems at k 32 once the environment
  writes the premise lines. Without that help it solves 0–26. The "premise-count wall" (peer-rl-review) is the untrained
  `h4` / `h5` token, not reasoning.
- **Proposal:** the environment applies premise lines itself, for every model. Premise lines carry no choice.
- **Cost and value:** a code change plus a re-read of the standard sets. It removes a wall for every existing
  checkpoint without retraining.

## 3. A shorter, state-friendlier construction — ≈ $10 per arm
- **The two error classes point at two fixes:**
  - "wrong next subformula" (45 %): show the pending sub-goal in the state, so the recursion's place is visible;
  - "corrupted formula" (31 %): cut copying, e.g. cite subformula lines instead of restating whole formulas.
- **A shorter proof:**
  - close a branch as soon as a premise is false under the partial valuation (early ex falso);
  - split only the atoms the remaining formulas need.
  - The builder (`kalmar/kalmar.py`) makes these one-line changes. Measure the length first; the dataset rebuilds in
    17 min on the VPS.
- **Decision value:** separates "Kalmár is too long for this model" from "the format hides the recursion's state".

## 4. Hybrid pretraining (K12 + K12-Kalmár) — ≈ $10
- **Question:** does a model keep K12's short proofs and gain the uniform fallback? Here KAL-D is ahead of the control
  only on the classical families (guided pass@32 30 vs 16 of 106).
- **Arm:** a mix (e.g. 90 % K12, 10 % K12-Kalmár by tokens) at the control's step count.
- **Read-outs:** the control's sets plus G3.

## 5. EI ladder from a Kalmár base, done properly — ≈ $15 per seed
- **Issue here:** the ladder's fine-tune (600 steps × 128 proofs) costs 14× more per step on Kalmár proofs than on
  K12's, which forced the cut to 4 rounds.
- **Proposal:** a token-budgeted fine-tune (the best recipe's 18,432 tokens per step), 8 rounds, 2 seeds, EI against
  frozen. It answers the brief's item 7 at full length.

---

# next_steps — create-or-elicit (final, 2026-10-13; UNREVIEWED)

Costed proposals beyond this run's $190, ranked by what they would teach us. Costs at this run's A40 price ($0.59 / h)
and measured times: a 16-round ladder with its reads beside it ≈ 15 A40-hours ≈ $9 per seed; with the post-ladder work
this run did (three k 256 reads, timing, large-k certificate, standard A) ≈ 22–27 pod-hours ≈ $13–16 per seed.

What this run leaves open (numbers in `numbers.md` § create-or-elicit): σ-free bases do not acquire the classical families
in 16 rounds of EI (0 / 6 vs 6 / 6), yet 5 / 6 of their ladders write the free reductio on their own, rarely; knockout
s1's grew from r9 to 123 proofs per round at r24, while its strict training targets stalled at 9 / 123 and its r24 read
solves the same 5 / 106 held-out members as at r20. A 1 % σ dose restores acquisition on 3 / 3 seeds (58 / 39 / 30 of 106
held-out members at r16), so the threshold lies below 1 %.

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
- Knockout s1's free reductio kept growing after r16 (29 → 123 proofs per round at r17–r24), yet its strict training
  targets stalled at 9 from r21. Running every knockout seed to r32 would say whether onset ever turns into acquisition
  on its own and at what cost — the "needs exposure" verdict is a statement about 16 rounds.

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
