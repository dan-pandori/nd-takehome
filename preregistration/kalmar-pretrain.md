# Pre-registration — kalmar-pretrain (proposal 29)

Run id `kalmar-pretrain`, executor, fork branch `dan_kalmar-pretrain` (from `origin/dan_create-or-elicit`). Written
2026-10-19 ≈ 01:50 UTC, **before any pod** (none of this run's pods exists at commit time; `~/pods.log` is shared with
other runs, so gate 0 compares this commit with the first `kal-*` pod).
Policy: `AGENT_POLICY.md`; brief: `docs/proposals/state-env/BRIEF_kalmar-pretrain.md` (nd-rl). Lean alone decides.

## Question

Can pretraining on proofs produced by Kalmár's construction (nd-rl `dan:code/tools/tt_prover.py`) teach a proof-state
model to execute the construction, over the long horizons it needs, and does that generalise beyond K12's
distribution? Kalmár's construction is a uniform decision procedure, and each of its steps is a function of the
visible proof state. A model that learned it locally could prove every theorem in the domain.

## What was measured before this commit (VPS, no GPU)

Builder `kalmar/kalmar.py` (+ `kalmar/build.py`): the prover's construction as an ND record (spec.md format).
- Atoms in the order P, Q, R, S. X ∨ ¬X is derived as the prover derives it (¬I box giving ¬¬(X ∨ ¬X), then DN: 9
  lines) and split by ∨E.
- At a leaf, the first false premise closes the branch by ex falso. Otherwise the goal is proved by Kalmár's lemma,
  case by case as in `prove()`.
- **Memo:** a formula already on a line in scope is cited, not re-derived. This keeps each step a function of the
  state; the term prover has no shared lines, so this is the one choice it does not make.
- Rendered by `lean_tok` to `lean_seq` and cut by `state_env.decompose` (canonical names, arm SN).

On the first 2,000 K12 records:

| | K12 (its own proofs) | Kalmár, shared lemma (**sl**) | Kalmár, per branch (**pb**, the prover's) |
|---|---|---|---|
| lines, mean / p99 / max | 7.0 / 12 / 12 | 110 / 299 / 527 | 154 / 398 / 626 |
| state-env actions, mean / max | ≈ 8.0 (1,239,995 pairs / 155,000) | 111 / 528 | 155 / 627 |
| training tokens per proof (Σ state + action) | ≈ 700 | 21,880 | 29,319 |
| longest state / action (tokens) | — | 566 / 133 | 566 / 133 |
| largest canonical name | — | n29 | n29 |
| term size (lean_check node count), mean / max | 35.9 (create-or-elicit) | 94 / 423 | 138 / 522 |
| decompose + replay failures | — | 0 / 2,000 | 0 / 2,000 |

- **Lean:** 200 / 200 sl texts accepted (literal canonical text, `lean_gate.check_sources`). The text parses back
  (`lean_tok.inverse`) to exactly the record's ND proof.
- **Evaluation sets:** every theorem gets a sl proof that decomposes. The longest algorithm proof is 476 actions;
  the longest state is 804 tokens (hand_proved_14). The largest canonical name is n30.
- **Primary variant: sl.** It is the same algorithm and every step is just as local. It has 29 % fewer actions
  and 25 % fewer training tokens; for four atoms it derives 4 instead of 15 excluded-middle lemmas. pb is built
  and its statistics are reported, but it is not trained.
- **Vocabulary limits:**
  - `lean_seq` has 64 name tokens. sl's canonical names stay ≤ n30, and the sampler's random name base is ≤ 32,
    so 62 ≤ 64.
  - `state_env.canonicalise` now reads a text whose first-appearance numbering passes n64. The canonical names it
    writes are still checked against 64; the existing tests pass.
  - K12 has ≤ 3 premises, so `h4`, `h5` are untrained tokens (see G1).

## Design

**Data.**
- `data/kalmar/train_kal_sl.jsonl`: one sl proof per K12 record, same 155,000 theorems, same order.
- Every record is checked: decompose + replay in the environment, and Lean on the literal canonical text. The full
  Lean check runs on the first pod, before any training on the data; any rejection stops the run until fixed.
- pb statistics are reported on the full set.

**Arms**, seeds 0, 1, 2 each; recipe `state_train.py --recipe best --mode lean_staten`: 9,560,832-param ALiBiGPT
6 × 384, Muon + AdamW, MTP 0.3, token budget 128 × 144, from scratch.
- **KAL-D (data-matched, headline).** The same passes over its pairs as the control: `--best_steps N_D`, with
  N_D = round(3.675 × batches_per_epoch). 3.675 is the control's mean epochs (3.667 / 3.668 / 3.690). Estimate:
  17.3 M pairs, ≈ 190 k batches per epoch, so N_D ≈ 700 k steps, ≈ 29× the control's 24,020.
  Intermediate checkpoints at steps 24,020 / 100 k / 200 k / 350 k / 500 k give a learning curve. These are
  mid-schedule checkpoints, not short runs.
- **KAL-C (compute-matched).** `--best_steps 24,020`, the control's mean step count (23,951 / 23,987 / 24,123). That
  is the same number of padded training tokens as the control's 1,200 A40-seconds. Defining it by steps makes it
  independent of the GPU it runs on.
- **Control.** best-cap12 Stage-1 `best-state/ckpts/bs/stage1_best12_s{0,1,2}_b1200.pt`, frozen (9,560,832 params,
  `lean_staten`, 1,200 s on an A40, K12 `data/kh/train_k12.jsonl` md5 800b5486…).

**Caps.**
- `max_steps` 1,024 actions: 2.15× the longest algorithm proof on the evaluation sets (476); about 2× for G2 by
  construction.
- `max_action` 512, the control's read protocol (the algorithm's longest action is 133 tokens).
- Training token budget unchanged; the longest pair (≈ 700 tokens) is far below 18,432.
- Cut-off fractions (step cap, action truncation) are reported per arm and per set. If more than 0.1 % of any
  reported stratum hits a cap, it is re-read at 2× that cap.

**Read-outs.** T 0.8 for sampled reads. Batch fixed across all new reads: 2,048 if it fits in memory, else 1,024 for
every new read; peak memory recorded in the first job. Lean on the literal text for every count.
- **E1 Teacher-forced agreement.**
  - TF set: 1,200 held-out theorems from `data/p2/heldout.jsonl` (150 one-atom, 350 each with 2 / 3 / 4 atoms),
    disjoint from K12 under a premise-order-invariant key, with their sl proofs.
  - At every state of the algorithm's trajectory: is the model's greedy action equal to the algorithm's action,
    after the environment assigns names from a random base as in sampling?
  - Broken down by step type (lem, split, efq, leaf by connective and polarity, reit, close, pr, end), box depth,
    position decile and atom count.
  - All 9 models, and the KAL-D intermediate checkpoints.
- **E2 Greedy free generation** (k 1, T 0) on the TF set:
  - Lean success by atom count.
  - Exact-follow rate: the attempt's action sequence equals the algorithm's.
  - First deviation: step type, depth, position.
  - Deviating attempts that are still valid: their share, and their length against the algorithm's (shortcuts).
- **E3 Sampled free generation** (T 0.8, k 8) on the TF set: exact-follow share per attempt; valid-deviation share.
- **E4 Solve rates**, plain and guided (`guided_eval.py`; guided = logical arm, ≤ 10 rejections per attempt).
  - Sets: holdout250; rr600 (L_true 13–16 = "Q", and 11–12); ≥ 17 (`transfer_long_ge17` 70 + `transfer_long2` 21);
    Charles's release (`candidate_v0` 87, `candidate_v1` 72, `batch3` 14, `hand_proved_14` 14); textbook72
    (scoring only, never printed).
  - **Plain, control:** k 256. The stored best-state reads are reused for holdout250 / rr600 / long2 / textbook72:
    same protocol (k 256, T 0.8, `max_action` 512), and their 96-step cap never bound (0 attempts reached 90
    steps). New k 256 reads for the other sets.
  - **Plain, KAL arms:** k 32 per theorem, then 224 more attempts on every theorem still unsolved. "Solved within
    256 i.i.d. attempts" is the same random variable as in a k 256 read. pass@1 / 8 / 32 come from the first 32
    (unbiased estimator); pass@256 from both rounds. KAL-C gets k 32 only, unless budget remains at the end.
  - **Guided, every model:** k 32 (cost); pass@1 / 8 / 32.
  - Broken down by atom count and by the algorithm's proof length (and L_true; L_true labels are ND-derived upper
    bounds under Lean).
- **E5 Generalisation** (both arms; plain k 32 and greedy; guided k 32 where `guided_eval.py` applies):
  - **G1 more premises.** 200 generated theorems: `p2/heldout` theorems with 2–3 premises, plus random distractor
    premises over their own atoms, giving 100 with 4 premises and 100 with 5. Also the release's 5 four-premise
    problems.
    - Read (a) as is, and (b) with the premise lines supplied: the environment applies the algorithm's
      premise-line actions before the model acts.
    - (b) is needed because no K12 theorem has a 4th premise, so `h4` / `h5` are untrained tokens.
      peer-rl-review reports 0 / 256 for our K12 models on every 4-premise problem.
  - **G2 larger formulas.** ≈ 240 generated valid sequents (≤ 3 premises, ≤ 4 atoms) in total-size bins
    [40, 49], [50, 59], [60, 79] (nodes, ¬ counted). K12: p99 39, max 71; per formula max 65, depth ≤ 9.
    Constraints: algorithm proof ≤ 1,000 actions; largest canonical name ≤ 32.
  - **G3 classical.** `data/coe/sigma_heldout_strict.txt`: 106 held-out σ-covered classical theorems from
    create-or-elicit, whose classical step needs a working reductio. K12 contains 59 working reductios in 155,000
    proofs (proof-strategies).

## Expected results (numeric, per seed unless "IQM")

- **E1 (TF agreement, TF set).**
  - KAL-D ≥ 99.5 % overall, and ≥ 98 % on every step type with ≥ 500 states. The lowest will be the leaf choices that
    need a truth value not yet on any line: the ex-falso decision, the ∨+ disjunct, the ∧− conjunct. Agreement
    falls with formula depth.
  - KAL-C 97–99.5 %.
  - Control ≤ 40 %: premise lines and a few single steps. It has never seen a ¬¬(X ∨ ¬X) derivation.
- **E2 (greedy, Lean).**
  - KAL-D full-proof success: 1 atom ≥ 98 %, 2 atoms ≥ 95 %, 3 atoms ≥ 90 %, 4 atoms ≥ 75 %. Exact-follow within 5
    points of success at each atom count, because deviations rarely end in a valid proof.
  - KAL-C: 1–2 atoms 80–95 %, 3 atoms 50–80 %, 4 atoms 20–60 %.
  - Control, its own proofs, on the same theorems: ≈ 0.90–0.95 (its `p2/heldout` greedy is 0.926 / 0.951 / 0.903).
- **E3:** KAL-D exact-follow ≥ 60 % of T 0.8 attempts.
- **E4 (plain pass@256, IQM; control values are the stored reads).**
  - holdout250: KAL-D ≥ 235 / 250, control 187 (184 / 195 / 182).
  - rr600 Q: KAL-D ≥ 350 / 380, control 241 (271 / 237 / 216).
  - ≥ 17: KAL-D ≥ 80 / 91; control long2 is 10 / 5 / 4 of 21.
  - Release, excluding the 5 four-premise problems: KAL-D ≥ 160 / 182. hand_proved_14: KAL-D ≥ 10 / 14, control
    0 / 14 (guided-tts, T1 models; frozen expected 0 too).
  - textbook72: KAL-D ≥ 60 / 72, control 28.7 (32 / 27 / 27).
  - pass@1 on holdout250: KAL-D ≥ 0.75; the control's is computed from its stored rows (expected 0.3–0.5).
  - KAL-C: below the control on holdout250 at pass@32; above it on hand_proved_14.
  - Guided ≥ plain at k 32 for every arm. KAL-D's guided gain ≤ 3 points; the control's 3–9 points (guided-tts).
- **E5.**
  - G1 (a) as is: ≤ 5 % for both arms (the `h4` wall).
  - G1 (b) premise lines supplied: KAL-D greedy ≥ 60 %, control pass@32 ≤ 20 %.
  - G2: KAL-D greedy success ≥ 60 / 40 / 20 % in bins [40, 49] / [50, 59] / [60, 79], declining with proof length.
    Control pass@32 ≤ KAL-D's pass@32 in every bin.
  - G3: KAL-D pass@32 ≥ 90 / 106; control pass@256 ≤ 30 / 106.

## What counts as "learned the construction" and "generalises" (judged on KAL-D; the same table for KAL-C)

- **Learned the construction** (in distribution, TF set), per seed:
  - (i) TF agreement ≥ 99 % overall and ≥ 95 % on every step type with ≥ 500 states;
  - (ii) greedy exact-follow ≥ 90 % on 1–2-atom theorems and ≥ 60 % on 4-atom theorems.
  - (i) and (ii) on 3 / 3 seeds → **learned**. (i) only → **learned the steps, not the horizon**. Neither →
    **not learned**.
- **Generalises** is judged for each of G1(b), G2 (per bin), G3, and the long sets (hand_proved_14, ≥ 17).
  - **Generalises:** KAL-D's rate is ≥ 0.7 × its in-distribution rate at the same atom count (greedy success on
    the TF set), **and** it exceeds the control's pass@32 by more than the MDD below.
  - **Does not generalise:** below 0.3 × its in-distribution rate.
  - Between the two → **partially**.

**Resolution.** At n = 3 vs 3, a two-sample t-test (80 % power, α 0.05, two-sided) needs a difference of 3.04 × sd.
With the control's own seed sd:

| quantity | control sd | MDD | predicted effect |
|---|---|---|---|
| holdout250 pass@256 | 7.2 | 22 | +48 |
| rr600 Q | 27.7 | 84 | +109 |
| textbook72 | 2.9 | 9 | +31 |
| held-out greedy | 0.024 | 7 pp | — |

hand_proved_14 is 0 / 14 for the control, so any KAL-D count ≥ 3 on every seed is visible. An exact permutation test
at 3 vs 3 cannot reach p < 0.05 (its minimum is 0.1). I report per-seed values and the IQM with a stratified-
bootstrap 95 % interval. A predicted effect inside its MDD is not claimed. `NOISE_FLOOR.md`'s table is for a
different model (3.2 M, cap 6); I quote it only for the settings-change rule.

## Compute, budget, stop rules

- **Budget** $50 / 90 pod-hours, registered with `podbudget kalmar-pretrain --set 90 50` before the first pod. RunPod
  balance at start: $297; floor $35.
- **GPUs.** Community RTX 4090 ($0.34 / h, 24 GB) is the primary. A40 ($0.59 / h, 48 GB) is the fallback. Each
  pod's billed rate is recorded.
- **Plan (estimates; pod-hours):**

  | item | pod-hours |
  |---|---|
  | data Lean check + loader equivalence test | 1 |
  | KAL-C, 3 seeds | 2 |
  | KAL-D, 3 seeds (≈ 700 k steps each; 50 ms / step measured on A40 for the control; 4090 expected faster) | 21–30 |
  | control reads | 4 |
  | KAL-C reads | 5 |
  | KAL-D reads | 9 |
  | overheads | 5 |
  | **total** | **≈ 47–56 (≈ $20–30)** |

- **Compute rows** (`record.py`): gpu_seconds, gen_tokens, attempts, actions, train_steps, train_tokens,
  lean_checks, per arm and seed, plus a per-arm table in the write-up. KAL-D uses ≈ 29× the control's training
  compute; this is flagged (> 1.25×) by design. KAL-C is matched on steps × token budget.
- **Stop rules.**
  1. **Pilot.** KAL-C s0 measures ms / step and peak memory on the chosen GPU. If 3 KAL-D seeds project to
     > 40 pod-hours, KAL-D runs at the largest step count that keeps 3 seeds ≤ 36 pod-hours, labelled with its
     epochs. Data-matched stays the target if it fits.
  2. **Spend gates.** At $35 spent: drop the KAL-C guided reads and the k extension. At $45: launch nothing new;
     pull, upload, write.
  3. **Time.** Hard stop 96 h (2026-10-23 01:20 UTC); writing starts no later than 72 h.
  4. **EI ladder (brief item 7).** Only if ≥ $15 and ≥ 30 h remain after E1–E5, and only after a pre-registered
     addendum.

## Deviations from the brief (with reasons)

- **sl is primary, not the prover's per-branch layout:** materially shorter, same algorithm.
- **Memo (in-scope reuse):** keeps the algorithm a function of the visible state.
- **Guided reads at k 32,** not 256 (cost).
- **KAL plain reads at k 32 + 224 on unsolved,** which is the same pass@256 random variable.
- **Compute-matched defined by steps** (= padded tokens) rather than wall-clock.
- **G1 adds a premise-lines-supplied read** (untrained `h4` / `h5`).
- **Code changes, made only so that ≈ 700-token pairs and 17 M-pair sets fit:**
  - `state_env` reads > 64 first-appearance names.
  - `state_train` decomposes in parallel and copies the pair matrix to the device in chunks; the tensors are
    identical, which is checked on a subset before KAL training.
  - Intermediate checkpoints (`--save_at`).

## Addendum 1 (2026-10-19 03:30 UTC, before any ladder pod) — the optional EI ladder (brief item 7)

Authorised by Dan 2026-10-19 03:24 UTC (inbox / QUESTIONS.md): the $50 is the only limit; pod-hour figures are advice.
Written before KAL-D has finished training and before any KAL-D read-out exists.

**Question.** Starting from a model that writes Kalmár proofs, does expert iteration against Lean keep the algorithm,
or does it drift to shorter proofs?

**Design.** `state_ladder_ei.py` with its defaults, except where stated:
- Base: KAL-D s0 final (`ckpts/kalmar/stage1_kalD_s0.pt`); 8 rounds; seed 0.
- Targets: `data/kalmar/ei_targets1000.jsonl`, 1,000 of `data/ladder/rl_targets.jsonl` drawn with random seed 0. A
  full ladder round of 4,495 targets plus 2,285 transfer theorems at k 32 would be ≈ 217 k Kalmár attempts ≈ 5
  A40-hours.
- Sampling: k 16, T 0.8, `max_steps` 1,024, `max_action` 512, batch 2,048 (A40).
- Transfer: `data/kalmar/ei_transfer200.jsonl` (200 of `transfer.jsonl`, random seed 1), k 16.
- Held-out greedy: `data/kalmar/val300_kal_sl.jsonl`.
- Fine-tune (ladder defaults): 600 steps, lr 3e-4, 128 proofs per step, `max_per_thm` 4, `rl_weight` 4, retain 20,000
  K12-Kalmár records per round as replay.
- **Frozen arm** (`--no_train`, same seed, same attempts) **if** at least $8 of the $50 remains once the EI arm is
  projected. It shows what sampling more from the base gives without training.
- A second EI seed (KAL-D s1) only if $10 more remains after that.

**Read-outs.**
- Per round, over the distinct Lean-accepted target proofs first found in that round (`found_<r>.jsonl`):
  - the share that is exactly the algorithm's proof (ND string equal to the sl proof of that theorem);
  - the actions per accepted proof against the algorithm's;
  - the share of deviating proofs shorter than the algorithm's.
- Cumulative targets solved, EI against frozen.
- After round 8: TF agreement and greedy exact-follow on tf1200, against the base.

**Expectations.**
- Round 1 solves ≥ 90 % of the 1,000 targets.
- The exact-Kalmár share of new accepted proofs is ≥ 70 % in round 1, and stays within ±15 points of it through round 8.
- Actions per accepted proof stay within ±10 % of the algorithm's.
- After round 8, TF agreement is ≥ base − 1 point and greedy exact-follow ≥ base − 5 points.
- EI's cumulative solved count at round 8 exceeds frozen's by ≤ 3 points of the 1,000.
- Reasoning: 20,000 replayed Kalmár proofs per round, and plain EI has no length pressure.

**Criteria.**
- **Keeps the algorithm:** at round 8, ≥ 50 % of new accepted proofs are exact Kalmár, and TF agreement has fallen
  ≤ 1 point.
- **Finds shorter proofs:** at round 8, the mean accepted length is ≥ 15 % below the algorithm's, or ≥ 30 % of new
  accepted proofs are shorter deviations.
- Both can hold.

**Cost** (estimates; to be measured in round 1):
- EI arm: ≈ 19 k attempts per round + fine-tune ≈ 50–60 min per round → ≈ 8 A40-hours ≈ $5.
- Frozen arm: ≈ $3.
- Projected run total with the ladder: ≈ $38 of $50.
- Stop rule: if round 1 projects the EI arm above $10, cut it to 4 rounds.
