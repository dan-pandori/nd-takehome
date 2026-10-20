# next_steps — kalmar-complexity (2026-10-20; UNREVIEWED)

This run's finding: Kalmár's construction is a few kilobits long in every language (BLC 5,443 bits for the K-sl
algorithm), but KAL-D absorbed ≈ 6.6 × 10^6 bits in its first epoch, and where it fails is predicted by what one
step must compute (RASP-L decision depth ρ = +0.85, in-scope lookups +0.82 across 15 step types; within types too),
not by the length of the code for that step (ρ = −0.55). The tests below turn that correlation into causal claims
and set up the pretraining-vs-RL bits study.

## 1. Lower the per-step demand, keep the program — ≈ $10 (3 seeds × 2 arms, KAL-D recipe at 1/4 of its steps)
- **Arm F (focus given):** the environment adds the next needed subformula and its children's truth values to the
  state (the features the decision tree reads). Program length is unchanged; the decision depth falls from 13–33
  (effective RASP-L layers) to a constant.
- **Arm U (search unrolled):** every in-scope lookup becomes its own action (a "check" step the environment answers),
  so one step never needs more than one lookup. Same program; ≈ 3× more actions.
- Predict: ∧ true / ∨ true / ¬⊥ errors fall to the level of the structural steps (≤ 3 %), and exact-follow rises
  sharply; if they do not, demand is not the cause.

## 2. Depth, not size — ≈ $8 (3 seeds × 12 and 24 layers at KAL-D's parameter count, 1/4 schedule)
- The RASP-L program needs 41 attention layers (13–18 effective); KAL-D has 6. Same parameters, more layers.
- Predict: error falls most on the high-depth step types; per-type error vs RASP-L depth flattens.

## 3. Tie B1 and B2 to one learner — ≈ $5
- B2 at size L with KAL-D's own recipe (Muon + MTP), so the block-wise code and the logged first-epoch code describe
  the same learner; extend B2 to 65,536 theorems at size M (the EDL curve had not yet turned down).

## 4. The pretraining-vs-RL bits study (out of scope here; what it should measure)
- **Units:** bits, with the protocol fixed as here: prequential code of the action tokens of fixed external targets
  (not the model's own samples, which are biased low), residual = the final model's held-out loss, EDL = their
  difference; also bits per parameter.
- **Pretraining's share:** this run's numbers — KAL-D 6.3–7.1 × 10^6 bits (first epoch), the K12 control
  1.5–1.7 × 10^6; B2's small-model curves.
- **RL's share:** per round, the change in teacher-forced code of fixed targets (Kalmár proofs of tf1200, and
  reference proofs of the ladder's targets) under the round-start vs round-end model, summed over rounds; and the
  prequential code of the accepted proofs with Donoway's on-policy correction. Compare with the replay-only
  fine-tune (KAL-D+A), which kalmar-pretrain showed matches EI round 1 → 2.
- **Where the bits go:** break both shares down by step type and by this run's demand measures (lookups, RASP-L
  depth). The question to answer: does RL supply bits on the high-demand steps that pretraining left unlearned, or
  only sharpen the low-demand ones?
- **Program length as the floor:** report every share against the 5.4-kbit BLC program and the 0.6-kbit decision
  tree, so "how many bits were instilled" has a lower reference point.

## 5. Finish the per-step program-length table — VPS only
- BLC bits per case (the term each step type comes from), and a strict int8 RASP-L memo lookup (+≈ 100 ops), so the
  "program length does not predict errors" result holds in all three languages, not only Python.

# next_steps — kalmar-pretrain (2026-10-20; UNREVIEWED)

What this run leaves open (`numbers.md` § kalmar-pretrain):
- **Pre-registered result.** Kalmár pretraining (KAL-D, 3.68 epochs) is far below the K12 control. Teacher-forced
  agreement is 94.5 % and greedy proofs are 32.6 % valid.
- **Exploratory result** (Addendum 3). The ladder's 600-step fine-tune on 20,000 replayed Kalmár proofs, without EI
  proofs (KAL-D+A), lifts that to 98.7 % and 71–79 %. Greedily, it about matches the control on holdout250 and beats
  it on the classical families and the release. With 32 samples it trails the control on holdout250 (136 vs 165) and
  leads beyond the MDD on textbook72, ≥ 17, long2, the release's candidate_v0, G1 and G3 (batch 1,024 vs 2,048).
- **The EI ladder.** Its jump (135 → 572 of 1,000 targets) is that same anneal: replay alone gives 578.
- **Still short.** Exact-follow at 1–2 atoms is 63–69 % against the 90 % bar.

Costs below use this run's prices (RTX 3090 $0.22–0.50/h for training, A40 $0.59/h).

## 1. Find out what the anneal does — ≈ $15
- **Why first:** it is exploratory and changes the run's conclusion. Pre-register it, then test it.
- **Confounded in KAL-D+A.** The ladder's fine-tune changed four things at once:
  - learning rate: 3e-4 → 3e-5, against the recipe's 3e-4 floor;
  - batch: 128 whole proofs (≈ 2.7 M tokens) per step, against 18,432 tokens;
  - optimizer: AdamW on every weight and no MTP, against Muon on the matrices and MTP 0.3;
  - extra data: 1.6 B tokens, 13.5 % of KAL-D's.
- **Arms** (from KAL-D s0–s2, 1.6 B tokens each, ≈ 3 h per seed):
  - the best recipe continued at its floor (more tokens only);
  - the best recipe decayed from the floor to ≈ 0 (learning rate only);
  - the best recipe at the floor with 128-proof batches (batch only).
  - KAL-D from scratch with a schedule that decays to ≈ 0 (`state_train_best.MIN_LR_FRAC`), if the learning rate is
    the lever.
- **Read-outs:** TF, greedy, plain and guided reads at matched batch.
- **The same question for the K12 control:** does the same fine-tune on K12 replay lift it too?
  - This matters for every best-recipe result in the project: every best-cap12 / best-cap6 model, and every ladder
    whose gains include replay.
  - Cost: ≈ $1 per seed on a 3090, plus greedy reads.
- **Decision value:** if K12 models gain as much, the project's RL-vs-pretraining comparisons need an annealed
  baseline.

## 2. Separate RL from annealing in every ladder — ≈ $2 per ladder
- **Finding:** here a replay-only fine-tune reproduces an EI round's gain: 578 vs 572 targets; TF 98.7 vs 98.7 %.
- **Proposal:** for any ladder whose fine-tune replays pretraining data, run a replay-only arm with the same steps and
  learning rate. My notes from `rl-from-ckpt` already flagged "ladder replay is pretraining".

## 3. Let the environment restate premises — ≈ $1 (re-reads only)
- **Finding:** the K12 control solves 177–191 of 200 four- and five-premise problems at k 32 once the environment
  writes the premise lines; 0–26 without. Most failed attempts break the premise-line order at the first actions.
- **Proposal:** the environment applies premise lines itself (they carry no choice). That removes this wall for every
  checkpoint without retraining.

## 4. A shorter, state-friendlier construction — ≈ $10 per arm
- **Bookkeeping errors remain after annealing:** the wrong next subformula, copying. The fix is to show the pending
  sub-goal in the state, and to close branches as soon as a premise is falsified (early ex falso).
- **Cost:** the builder (`kalmar/kalmar.py`) makes these small changes; the dataset rebuilds in 17 min.

## 5. Hybrid pretraining (K12 + K12-Kalmár) — ≈ $10
- **Question:** keep K12's short proofs and gain the uniform fallback? KAL-D+A beats the control on the classical
  families (greedy 35 vs 7 %) and the release.
- **Arm:** a 90 / 10 token mix at the control's steps, plus an anneal.

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
