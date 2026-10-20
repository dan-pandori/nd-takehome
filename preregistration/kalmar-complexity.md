# Pre-registration — kalmar-complexity (proposal 31)

Run id `kalmar-complexity`, executor, fork branch `dan_kalmar-complexity` (from `origin/dan_kalmar-pretrain`). Written
2026-10-20 ≈ 12:45 UTC, **before any pod, before any program of this run was written or measured, and before any B1
number was computed**. Policy: `AGENT_POLICY.md`; brief: nd-rl `docs/proposals/state-env/BRIEF_kalmar-complexity.md`.
Lean alone decides wherever a proof is judged (here only the builder's proofs, which kalmar-pretrain checked:
155,000 / 155,000 Lean-accepted). Budget $15 / 40 pod-hours; hard stop 2026-10-23 12:20 UTC.

## Question

How many bits is Kalmár's construction, and which measure of that predicts how hard it is for our models to learn?
Dan's handle is the length of a program. The run measures program length in several languages, a decision procedure,
transformer-native (RASP-L) length, per-step computational demand, Levin's Kt and prequential (online) code length,
and tests which of them predicts where kalmar-pretrain's models fail.

## What I read before writing this, and what I saw

- kalmar-pretrain: `run_kalmar_pretrain.md`, the review's §Recount models / E1–E3 / §Verdict, `kalmar/kalmar.py`
  (the builder), `data/kalmar/README.md`, nd-rl `code/tools/tt_prover.py`, the proposal and brief, lit-review-2's
  note on excess description length.
- **Known outcome** (so the Q4 predictions below are not blind to it): KAL-D's per-step-type teacher-forced agreement
  (review E1): close / lem ≈ 0.99, efq 0.98, split 0.97, ¬(A→B) / ∧− / ∨− / ¬¬A ≈ 0.89–0.93, →I-A-false 0.89,
  →I-B-true 0.82–0.85, ∨+ 0.71–0.79, ¬⊥ 0.64–0.82, ∧+ 0.60–0.74; 76 % of KAL-D s2's errors are wrong or corrupted
  formulas. No predictor below has been computed.
- **B1 is not blind for KAL-D s0:** checking the log format I saw the first 30 lines of
  `artifacts/kalmar/logs/train_kalD_s0.log` (the logged train loss through epoch 1.07: 0.079 for steps 1–10,995,
  then 0.029–0.037). I have not looked at KAL-D s1 / s2 or at any control curve, and computed nothing from them.
- **What was logged** (code read, `state_train_best.py`): the logged `train_loss` is the mean of the pre-update
  next-token loss (nats per action token, token-weighted within a batch) sampled every 20th step between log points.
  KAL-D logged every 600 s (≈ 10,000–11,000 steps; ≈ 17 points in its first epoch of 178,581 steps). The control
  (best-state `stage1_best12_s*_b1200`) has its curve only inside the checkpoint (`extra['curve']`, default 30 s). This
  is enough for a coarse total first-epoch code length, **not** for a per-step-type breakdown (only aggregate loss was
  logged) — see B1-snap below.

## Design

### Algorithms (Q1)

- **K-sl**: K12-Kalmár, shared-lemma variant with memo (`kalmar/kalmar.py`, `sl`) — what kalmar-pretrain trained on.
- **K-tt**: `tt_prover.py`'s construction: excluded middle derived inside every branch that splits an atom (per-atom
  split), no memo, a Lean term as output.
- (K-pb, kalmar.py's per-branch variant with memo, only where it is free.)

Each program is split into **algorithm** (structured input: formula trees; structured output: the proof as a tree of
lines / terms with rule names, formulas and references) and **rendering** (that tree → the token text: ND, Lean term,
or `lean_seq` / state-env actions). Every table reports algorithm, rendering and their sum.

### Languages (Q1)

1. **Minified Python 3** (hand-golfed; behaviour identical): raw bytes, raw DEFLATE (zlib level 9, no header), raw LZMA2
   (xz preset 9e, `FORMAT_RAW`, no container), and tokens. *Interpretation of "our tokenizer":* the project's models use
   a one-symbol-per-token domain vocabulary (`lean_tok`), which cannot spell Python. I report Python in the tokens of
   **Qwen3** (the pretrained family this project uses; via the `tokenizers` library), plus GPT-2 BPE as a second
   tokenizer, and report the *rendered outputs* in `lean_tok` tokens.
2. **Binary lambda calculus (BLC, Tromp)**: a closed λ-term whose application to the Scott-encoded input normalises to
   the Scott-encoded output; exact bits (λ = 00, application = 01, de Bruijn index i = 1^i 0). The same terms
   bracket-abstracted to **binary combinatory logic** (S = 00, K = 01, application = 1) as a second fixed universal
   language. Data encodings are fixed and stated once and shared by all algorithms. Exactness of the count is the
   point: the encoder is the checker.
3. **RASP-L (Zhou et al. 2023)** for the **per-step policy** (proof state → next action): a numpy interpreter of the
   RASP-L primitives (`tok_map`, `seq_map`, causal `select`, `aggregate`, `selector_width`-free where possible,
   fixed-offset shifts). The program reads the state's token sequence and outputs, at the last position, the action's
   content (template id, a pointer to the formula span or the atom, pointers to the cited hypotheses); rendering those
   into tokens is a separate, shared program. Length = number of primitive operations and source tokens; depth = the
   longest chain of select–aggregate (attention layers).
4. **Decision procedure**: the smallest exact decision list / tree I can find over a stated set of proof-state
   features (box type of the innermost frame, the focus node picked by a fixed generic rule, its connective and truth
   value, its children's truth values and in-scope flags, phase flags). Size in bits under a stated tree code
   (structure 1 bit per node + log2 #features per test + log2 #labels per leaf), reported **with** the Python length of
   the feature extractor it is conditional on.

**Tests.** Every program reproduces the builder's output exactly on ≥ 1,000 K12 theorems (all of a fixed random
sample; K-sl against `kalmar.build(…, 'sl')`'s proof and tags, K-tt against `tt_prover.solve`), and the RASP-L policy
and decision procedure reproduce every action on every state of those theorems.

### Calibration set (Q2)

Measured in the same languages where feasible: copy, reverse, sort, parity, multi-digit addition, **eval** (a K12
formula's truth value under a valuation), **taut** (truth-table validity check of a sequent), the **K12 generator**
core (`gen.py`, Python only — its stochastic proof style is what the control imitates), K-sl, K-tt. Python is
reported with builtins and, for sort / addition, without (explicit algorithm), to show the language constant at work.
Learnability facts: published RASP-L / transformer results (Zhou et al.; Weiss et al.; Delétang et al.) and our own
model family (K12 control learns K12 to 92 % greedy at 24k steps; KAL-D learns Kalmár to 33 % greedy / 14 % exact at
656k steps; B2 below).

### Absorbed bits (Q3)

- **B1 (logs; no pods).** For KAL-D s0/s1/s2 and the control s0/s1/s2, first epoch only (each pair scored before the
  update that uses it): `L_preq = Σ_intervals mean_loss × action tokens in the interval / ln 2`, tokens from the epoch
  fraction × the data set's total action tokens (counted from the rebuilt data). Residual `L_res = N × L∞` with
  L∞ = (a) the final train loss, (b) the final held-out (val300) loss. **Absorbed bits** `EDL = L_preq − L_res`
  (Donoway 2026; Whitney et al. 2020 "surplus"). Stated limitations: 600 s granularity, every-20th-step sampling, the
  learning rate is still high at the end of epoch 1, KAL-D trains 2.7 more epochs.
- **B1-snap (extension; one cheap GPU job).** Per-step-type teacher-forced loss of KAL-D's saved snapshots (steps
  24,020 / 100k / 200k / 350k / 500k / final, 3 seeds) on tf1200's 137,984 states, integrated over the epoch-1 stream
  (trapezoid) as a per-step-type prequential approximation from step 24,020 on. Labelled an approximation.
- **B2 (pods).** Block-wise prequential code (Blier & Ollivier 2018; Voita & Titov 2020). Data ordered by theorem
  (K12's order), boundaries at 64 · 2^k theorems, k = 0 … 8 (64 … 16,384); the first block costs the uniform code
  (log2 of the action vocabulary per token); each later block is coded by a fresh model trained to early stopping
  (10 % of the prefix's theorems held out) on all earlier blocks. Three sizes of the kalmar-pretrain architecture
  (ALiBiGPT, `lean_staten`): **S** 2 × 128, **M** 4 × 256, **L** 6 × 384 (= KAL-D's 9.56 M). Tasks: **Kalmár sl**
  (state, action), **K12** (the control's own (state, action) pairs, same theorems), **eval** (a K12 formula and a
  valuation → its truth value; 16 valuations per theorem). Code length per action token is recorded with its step-type
  tag, so bits break down by step type (atom split, excluded middle, leaf by connective, ex falso). Absorbed bits
  = prequential code − (N × the last block's per-token code).

### Which measure predicts difficulty? (Q4)

- **Outcome:** KAL-D's per-step-type teacher-forced error on tf1200 (1 − agreement, mean of 3 seeds; the step types
  with ≥ 500 states), and per state (the stored per-state verdict strings) for a state-level test; secondary,
  KAL-D+A and the first-deviation / error-class tables (`kalmar/error_truth.py`).
- **Predictors per step type:** Python / BLC / RASP-L length of the code that produces that step; the decision
  procedure's path length to that action; computational demand (the height of the formula subtree whose truth values
  decide the action; the number of tokens of the formula the action writes; the number of in-scope lookups); Kt
  (program bits + log2 of the builder's elementary operations for that step); B2 prequential bits per occurrence;
  **baseline:** log frequency of the step type in K12-Kalmár.
- **Test:** Spearman ρ across step types (n ≈ 13–15, so only |ρ| ≥ 0.55 is distinguishable from 0 at p ≈ 0.05; I
  report the permutation p and the interval) and a per-state logistic regression of error on step type + the
  computational-demand measures (does demand add to step type? likelihood-ratio test, per seed).

### Literature (Q5)

Screen 15–25 sources, read 5–8 in depth: Kolmogorov / Levin complexity and invariance; MDL and prequential coding of
neural networks; RASP, RASP-L, length generalisation; simplicity bias; excess description length.

## Expected results (numeric; written before any measurement)

| quantity | expected (point; range) |
|---|---|
| K-sl algorithm, minified Python: raw / DEFLATE / xz bytes | 1,300 (900–1,900) / 650 (450–900) / 650 (450–950) |
| K-sl rendering to `lean_seq` actions, Python DEFLATE bytes | 350 (200–600) |
| K-tt (tt_prover), minified Python, DEFLATE bytes (algorithm + Lean rendering) | 600 (400–850) |
| K-sl algorithm, Qwen3 tokens | 450 (300–700) |
| K-sl algorithm, BLC bits | 3,000 (1,500–5,000) |
| K-tt algorithm, BLC bits | 2,300 (1,200–4,000) |
| rendering, BLC bits | 1,000 (400–2,500) |
| binary CL / BLC size ratio | 2.5 (1.5–4) |
| K-sl per-step policy, RASP-L: primitive ops / attention depth | 130 (70–250) / 15 (8–30) |
| decision procedure: leaves / bits (given its features) | 35 (15–80) / 400 (150–1,000) |
| feature extractor, Python DEFLATE bytes | 500 (300–800) — i.e. most of the algorithm sits in the features |
| calibration, BLC bits: copy / reverse / parity / addition / sort / eval / taut | 4 / 50 / 50 / 200 / 250 / 200 / 350 |
| Kalmár's rank (largest = 1) among copy, reverse, parity, sort, addition, eval, taut | 1 in Python-DEFLATE, BLC, binary CL and RASP-L; ≥ 5× the next item in BLC |
| K12 generator core vs K-sl, Python DEFLATE | generator larger (1.2–3×): the easily learned K12 style is *not* shorter to describe |
| rank agreement across languages (Spearman over the calibration items) | Python-DEFLATE vs BLC ≥ 0.8; RASP-L disagrees on parity / addition (no short RASP-L program without hints) |
| B1 KAL-D first-epoch prequential code (not blind for s0) | 1.5 × 10^7 bits (0.5–4 × 10^7) |
| B1 KAL-D absorbed bits (EDL, residual = final train loss) | 6 × 10^6 (10^6–2 × 10^7) |
| B1 control absorbed bits | 2 × 10^6 (10^5–10^7); KAL-D > control (60 %) |
| absorbed bits / K-sl BLC program bits | ≈ 2,000 (100–20,000); **≥ 100 for every estimate (B1 and B2)** |
| B2 Kalmár, size L, prequential code over 16,384 theorems / absorbed bits | 5 × 10^6 (1–20 × 10^6) / 3 × 10^6 (0.5–10 × 10^6) |
| B2 size dependence | larger models give the shorter Kalmár code (L < M < S) |
| B2 bits per occurrence, Kalmár | highest for ∧+, ∨+, ¬⊥, →I-B-true; lowest for close, lem, split |
| B2 EDL per token vs data size | Kalmár rises then falls ("teaching" shape); K12 and eval fall monotonically |
| best predictor of per-step-type error (Spearman across types) | a computational-demand measure (declared-formula length or evaluation height), ρ ≥ 0.6 |
| program length (any language) vs per-step-type error | |ρ| < 0.4 — no predictive value |
| frequency baseline | ρ between −0.4 and −0.7 (rarer types fail more) |
| B2 per-type bits vs KAL-D error | ρ ≥ 0.7 (a learner-relative measure, not a priori) |
| state level | computational demand adds to step type (LR test p < 0.01 in each seed) |

**Recommendation I expect to make:** state "how much there is to learn" as a learner-relative prequential / EDL
number with a per-step demand profile, not as a program length: program length is ~10^3 bits in every language and
does not rank-predict where the model fails; the model absorbs ~10^6–10^7 bits.

## Compute, budget, stop rules

- Pods only for B1-snap and B2: RTX 3090 / A40 class, one job per `podrun`, ≤ 2 jobs per 24 GB card. Estimate
  B1-snap 1 GPU-h; B2 ≈ 10–15 GPU-h (Kalmár L dominates). `podbudget kalmar-complexity --set 40 15` before the first
  pod. Compute rows (`record.py`: `gpu_seconds`, `gen_tokens`, `train_steps`, `train_tokens`, `lean_checks`) per arm.
- **Stop rules:** B2 stops launching at $12 spent; it is cut in this order: Kalmár L above 8,192 theorems, the eval
  task, size S. Programs: BLC and RASP-L stop at the first version that passes the 1,000-theorem test plus at most
  one golfing pass; I report the version that passed. Write-up starts by 2026-10-23 00:00 UTC whatever is unfinished.
- VPS: ≤ 4 concurrent processes; heavy jobs on pods. textbook72 is not used (scoring only; nothing printed).

## Deviations from the brief (with reasons)

- Python token counts use Qwen3 / GPT-2 tokenizers, not our model tokenizer, which cannot spell Python (above).
- K12 proof style enters the calibration through the generator's Python length and through B2's K12 task; no BLC or
  RASP-L program for it (a stochastic generator has no single per-step policy).

## Addendum 1 (2026-10-20 ≈ 13:25 UTC, before any pod and before any B1 number)

Measured since the main commit (VPS only): the Python programs (`artifacts/kc/python_sizes.txt`), the explicit
per-step policy and the decision tree (`artifacts/kc/dtree/`). B1 is still uncomputed (the exact token count of
K12-Kalmár is running). Details of the pod work, fixed now:

- **B2 training** (`kalmar_complexity/b2_preq.py`): AdamW (lr 1e-3 → 1e-4 cosine, warmup 100, wd 0.1, betas
  0.9 / 0.95, clip 1), bf16, the trainer's token-budget batches (18,432 padded tokens) and random name shift;
  validation every min(steps per epoch, 1,000) steps on the prefix's held-out 10 % of theorems; the best validation
  checkpoint codes the next block; stop after 4 validations without improvement or at max(300, min(30 epochs, 20,000))
  steps. *Deviation from KAL-D's recipe* (Muon + MTP, no early stopping): early stopping is what block-wise
  prequential coding needs, and the architecture, data format and batch are kalmar-pretrain's. The code lengths are
  therefore those of this learner, not of KAL-D's run (B1 is KAL-D's).
- **Scope:** size L to 8,192 theorems (the pre-registered first cut, applied up front: L costs ≈ 10× S); S and M to
  16,384. Sizes are compared at 8,192 theorems. Seed 0 everywhere; seed 1 for Kalmár S and M, to measure the
  seed-to-seed spread of the prequential total. A size difference counts only if it exceeds that spread.
- **Expected (B2):** Kalmár L over 8,192 theorems: prequential code 3 × 10^6 bits (0.6–12 × 10^6); EDL ≥ 100 × the K-sl
  BLC program. K12's EDL below Kalmár's at equal theorems; eval's below both.
- **B1-snap:** 24 checkpoints (KAL-D s0–s2 at steps 24,020 / 100k / 200k / 350k / 500k / final; KAL-C; KAL-D+A) on
  tf1200's 137,984 states at name base 0. Expected: per-step-type code of the final KAL-D models ranks the step types
  like their teacher-forced error (Spearman ≥ 0.8).
- Pods: RTX 3090 community cloud (`kc-1`: Kalmár L + B1-snap; `kc-2`: the rest), one queue per pod.

## Addendum 2 (2026-10-20 ≈ 16:10 UTC, before this experiment's first job) — B3, a causal test of the Q4 finding

Not in the brief; added because Q4's result is correlational. Q4 so far (computed, committed): KAL-D's per-step-type
error tracks per-step search demand (RASP-L decision depth ρ = +0.85, in-scope lookups +0.82), not program length.

- **Manipulation:** remove the search, keep the algorithm. **FOC** states = the standard state with `<nl>` and the
  focus subformula inserted before `<act>`, at leaf-frame states where the target's line is not yet in scope. The
  focus is the first needed node, in post-order, whose literal is not in scope — the decision tree's `fc` node. All
  other states are unchanged. **STD** = the standard states. The program, the actions and the proofs are identical.
- **Models:** B2's size M (4 × 256, 3.2 M), from scratch, on the Kalmár pairs of K12 theorems [0, 8,192), seeds 0 / 1
  / 2 per arm (paired: same seed, same data order and early-stopping split). B2 v1 training (AdamW, early stopping,
  ≤ 20,000 steps).
- **Read-out:** tf1200's 137,984 states (FOC-transformed for FOC models), teacher-forced. Error = the greedy action is
  not exactly the algorithm's (some action token's argmax is wrong given the correct prefix). Measured per step type
  and per state class: **opener** = a state that gets a focus under FOC; **other** = all the rest.
- **Expected:**
  - Opener error falls by ≥ 50 % (relative, 3-seed means), FOC vs STD.
  - Other-state error changes by < 30 % relative.
  - ∧ true, ∨ true, ¬⊥ and →I-B-true each fall by ≥ 40 %.
  - The across-type Spearman of error with lookups drops from ≥ 0.6 (STD) to ≤ 0.3 (FOC).
- **Falsified if** opener error falls by < 25 %: then search is not what makes those steps hard for this learner.
- **Cost:** 6 models ≈ 3 A40-hours on a third pod `kc-3` ($0.59/h); within the $15 budget.
