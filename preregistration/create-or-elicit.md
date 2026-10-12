# Pre-registration — run `create-or-elicit` (proposal 27: the experiments for "Did RL create it?")

Written 2026-10-12 05:45–06:30 UTC, **before any pod exists for this run** (`podbudget create-or-elicit` set to
300 h / $140 at this commit; `~/pods.log` has no line for this run). Executor: agent:claude. Branch
`dan_create-or-elicit` (from the fork's `origin/dan` 4dcd0e4f). Brief: `BRIEF_create-or-elicit.md` (nd-rl
`docs/proposals/paper/`, Dan 2026-10-11). Policy: `AGENT_POLICY.md`. Lean alone decides every count.
Scripts: `coe/` (analysis, data), `pod/coe/` (pod jobs). Bulk files: `hf://buckets/dan-pandori/nd-rl/create-or-elicit/`.
Each later item (Phase 2 details, Phase 3) gets its own dated addendum below **before** its pods start.

## The question

Does expert iteration (EI) produce a classical capability its base never had, or does it only raise the probability of
one the base already had at low probability? Earlier runs measured this without intervening; here we **remove one
composition from pretraining** and ask whether RL brings it back.

**σ** = double negation (`DN`, Lean `Classical.byContradiction`) applied to a line obtained by negation introduction
(`NEGI`): classical proof by contradiction. In K12 (`cap-horizon/data/kh/train_k12.jsonl.gz`, md5 of the gz
c5a8cd37…; 155,000 records) σ occurs in **16,703** records (`patterns.reductio`), written form = pruned form for every
record (`coe/coe_sigma.py`, `artifacts/coe/sigma_k12.json`). DN occurs in 21,274 records (13.7 %); the line a DN step
cites is a NEGI line 17,387 times, a hypothesis (AS) 3,689, a premise (PR) 1,474, IMPE 182, ORE 101, BOTE 9, DN 6,
ANDE1 1.

## Models (every number names one)

All `best_model.ALiBiGPT` 6 × 384, **9,560,832 parameters**, `lean_staten` (proof-state environment, environment-assigned
names), from scratch, `state_env_october`'s recipe: `state_train.py --recipe best --mode lean_staten --cap 12
--budget_secs 1200` on one **NVIDIA A40**, then T1 EI (`state_ladder_ei.py`: k 32, T 0.8, 600 fine-tune steps per
round at lr 3e-4 → 3e-5, 128 records per step, ≤ 4 proofs × 4 copies per target, 20,000 replay records, 4,495
`rl_targets`), **16 rounds**.

| arm | data | seeds | source |
|---|---|---|---|
| **full, old** | K12 | s0, s1, s2 | `trajectory` (pend; r1–r8 on RTX A6000, batch 2,048, s2 1,024 from r2) + `rl-continue` (r9–r16 on A40) |
| **full, new** | K12 | s3, s4, s5 | this run, every round on A40 |
| **knockout** | K12⁻ (below) | s0–s5 | this run, every round on A40 |

pend = end of pretraining; r8 / r16 = after 8 / 16 EI rounds. Seeds are the same numbers in both arms (policy: same
seeds in every arm); a knockout and a full model with the same seed share the initial weights' RNG seed and the
per-round sampling seeds (S·1000 + r), not their data.

## The knockout set K12⁻ (`coe/coe_assemble.py`; built on the VPS before any pod; report `data/coe/train_k12ko_assemble_report.json`)

- **Removed:** every K12 record in which a DN step cites a *derived* double negation (`patterns.derived_dn`, "σ⁺") in
  the written **or** the pruned proof: the 16,703 σ records plus **258** whose DN cites an IMPE / ORE / BOTE / DN / ANDE
  line. Reason for the 258 (stricter than the brief's σ): they include indirect routes to σ, e.g. an Or-elimination whose
  branches each build ¬¬G by NEGI, or a reiteration of a NEGI line. A third route — an IMPI box that applies DN to its
  own ¬¬X hypothesis, used by IMPE on a NEGI-built ¬¬X (the "lemma route") — occurs in **0** K12 records and is asserted
  absent from the refill. **DN stays** where it cites a premise or a box hypothesis (4,313 records); **NEGI stays**
  everywhere. Total removed **16,961** (10.94 %).
- **Refilled to 155,000**, per pruned length exactly as many as were removed from that length (4: 19, 5: 2,453,
  6: 2,381, 7: 1,215, 8: 1,047, 9: 1,906, 10: 1,853, 11: 3,007, 12: 3,080), drawn uniformly (seed 0) from the records
  of **K12's own source pools that K12 did not use**: lengths ≤ 6 from `lean-format/data/p2/train_depth3_f0_a1.jsonl`
  (K12's short bins are a uniform subsample of it), lengths ≥ 7 from `cap-horizon/data/kh/pool_long_kh.jsonl` (K12's
  long bins are a uniform draw from its eligible records). So the refill is the same generator, the same settings and
  the same filters, minus σ⁺.
- **Filters on every refill record:** K12's own (`kh_assemble.py`: same length, box depth ≤ 2 in pruned and written
  form, outside K12's 11 exclusion pools, long bins outside the a1 set's classes) plus: σ⁺-free in both forms, no lemma
  route, not the renaming class of **any** K12 record (kept or removed), not in **any** evaluation pool of the fork
  (91 `.jsonl` files under `data/`, `targets/`, `data/eval_only/textbook72/`, including textbook72, holdout250,
  dev1108, the transfer and long pools and the take-home test prompts), under `gen.canon_key` **and** a
  premise-order-invariant key (minimum over the 24 atom bijections of (sorted premises, conclusion)); distinct among
  themselves under both keys.
- **Lean:** every refill record is checked by Lean (`lean_judge.judge_many`, the record's ND proof translated by
  `nd2lean`) on the first pod before any training; a rejection is replaced by the next eligible record and reported.
  The kept K12 records are K12's own (used by every earlier best-cap12 model).
- **Known inherited overlap, kept for comparability:** K12's premise-swapped twin of `textbook_3ed45280…` (disjunctive
  syllogism, no σ) stays in K12⁻ as in K12.
- **Built (2026-10-12 05:49 UTC, before this commit):** `data/coe/train_k12ko.jsonl.gz` (gz md5 6326ebdd…; 155,000
  records = 138,039 kept + 16,961 refill, per-length counts identical to K12; 155,000 distinct `canon_key` classes,
  154,491 premise-order-invariant classes, all 509 collisions inherited from K12's kept records). Overlap with the
  evaluation pools under the premise-order-invariant key (`artifacts/coe/k12_eval_overlap.txt`), K12 → K12⁻, all
  inherited from K12, the refill adds 0: `rl_targets` 6 → 4, transfer 2 → 2, holdout250 0, textbook72 1 → 1 (the
  known twin), dev1108 1 → 1, `p2/heldout` 22 → 21; under `canon_key` 0 everywhere. (K12 also matches 300 theorems of
  the older `data/heldout.jsonl`, which no read in this run uses.)
- **What else shifts** is reported from `coe/coe_shape.py` (rule shares, premises, term size, box depth,
  classical-only share). Pre-registered expectations: per-length counts identical; DN share of records 13.7 % →
  2.5–3.5 %; NEGI share drops by 8–12 points; classical-only (G4ip) theorem share drops by ≥ 70 % relative; mean term
  size within ±1.5 nodes of K12's; premise-count shares within ±2 points.

- **Shape, computed 05:53 UTC after the expectations above were written** (`artifacts/coe/shape_k12_vs_ko.md`): DN
  records 13.73 % → 3.29 % (hit); NEGI 15.21 % → 5.19 % (−10.0 points, hit); mean term size 35.91 → 36.25 (hit); premise
  shares within 0.8 points (hit); classical-only (G4ip, 20,000-record sample) 4.13 % → 1.33 %, a 68 % relative drop
  (expected ≥ 70 %: **miss**, the remainder is DN on ¬¬ premises and hypotheses). Other shifts: IMPI +5.1 points, ORE
  +2.8, R +2.1, BOTE +1.3, NEGE −3.1.

## Families (`coe/coe_families.py` → `data/coe/families.json`)

Families are the 19 generator schemata of `rl_targets` (40 trained-on members each) and the transfer pool (40 held-out
members each, never trained on: the ladder samples them but trains only on `rl_targets` proofs and replay). A family is
classical if any trained member is not provable by G4ip (`intuit.py`); classical families keep only their
classical-only members (**key-step members**). A member is **σ-covered** if it is classical-only and no premise is
itself a double negation (then a DN step cannot cite a premise; it must cite a derived line — σ⁺ — or a box
hypothesis ¬¬X — the lemma route).

| family | trained: all / key-step / σ-covered | held-out (transfer): all / key-step / σ-covered | key-step held-out in holdout250 |
|---|---|---|---|
| excluded_middle (A ∨ ¬A) | 40 / 39 / 39 | 40 / 39 / 39 | 6 |
| peirce | 40 / 15 / 15 | 40 / 13 / 13 | 2 |
| peirce_sequent | 40 / 20 / 20 | 40 / 19 / 19 | 3 |
| negated_conditional | 40 / 20 / 20 | 40 / 18 / 18 | **0** |
| demorgan_nand_to_or | 40 / 13 / 13 | 40 / 11 / 11 | 1 |
| contraposition_conv | 40 / 29 / 29 | 40 / 23 / 23 | 3 |
| **total** | 136 key-step | **123** key-step | 15 |

Plus non-schema ("generated") classical-only theorems: 189 `rl_targets` (155 σ-covered) and 72 transfer (55 σ-covered).
**Answer to the brief's "confirm that every classical-only key-step family needs σ":** every key-step member of all six
classical families is σ-covered — no premise is a double negation — so its classical step is DN on a derived ¬¬
(σ⁺) or the lemma route; nothing else in the rule set is classical. σ⁺ does **not** cover classical theorems with a
¬¬ premise (34 generated `rl_targets`, 17 transfer: DN can cite the premise), and it does not exclude the lemma route
in the model's own proofs. Every accepted proof of a key-step member in this run is classified (σ / σ⁺ / lemma route /
other DN) so that a σ-free acquisition would be visible. Noted from the capability-defs re-check: holdout250 has **no**
key-step member of negated_conditional, so capability-defs' "negated conditional, classical members, elicited 3/3" row
was read on G4ip-provable members; this run uses the 123 transfer-pool key-step members instead.

## Thresholds for the whole run (pre-registered)

- **Solves (RL):** ≥ 1 Lean-accepted proof in 256 plain attempts (T 0.8, 96 steps, 512 tokens per action), defining
  draw x0 (sample seed 0); x1 (seed 1) gives the redraw floor.
- **Budget K (compute-matched, per seed and round R):** `K_train(R)` = Σ_{r≤R} (sample-phase + fine-tune-phase GPU
  seconds of that ladder) / (N_eval × c_base), with N_eval = 322 and c_base = the seed's own base's measured seconds per
  plain attempt (sampling + Lean judging) **on the same GPU class at the same batch**, measured in this run's
  large-k base reads. The ladder's eval phase (transfer sampling, greedy reads) is excluded because it never feeds
  training. Also reported: `K_att(R)` = ladder target attempts / 322 = 446.7 · R, and for old seeds capability-defs'
  `K_eval-set` restated with a same-class attempt cost (Phase 0.2).
- **Within reach at K:** p̂ ≥ 1 / K by sampling, or known-proof estimate ≥ 2 / K (factor-2 margin), i.e. log p ≥ −ln K.
- **Not reached:** 0 successes in ≥ K attempts. **Certified out of reach:** one-sided 95 % Clopper–Pearson upper bound
  UB95 < 0.05 / K (the base's chance of a proof within K attempts < 5 %); with 0 successes this needs n ≥ 59.9 K.
  **Family-level certificate:** pooled over the family's m held-out key-step members, 0 successes in n_tot attempts
  with UB95(mean p) < 0.05 / K.
- **Family acquired (the bar):** ≥ 50 % of the family's held-out key-step members solved at k 256 (plain, x0).
  **Base reaches a family:** > 5 % of its held-out key-step members within reach at K.
- **Training share (per round):** share of the family's trained key-step members with ≥ 1 accepted proof among that
  round's 32 attempts (`alloc_r.json` differences). **Round of first acquisition:** the first round whose training
  share ≥ 0.5; separately, the first round with any accepted σ⁺ proof on any target.

## Phase 0 (≤ $5)

**0.1 The estimator at small p** (no pod; capability-defs J1/J2/J9 artefacts from the bucket; `coe/coe_estimator.py`).
On every (seed, theorem) with ≥ 1 base success in J2/J9 (34 / 30 / 42 hard theorems; p̂ down to 7 × 10⁻⁷) and the 30
calibration theorems per seed, compare the known-proof estimate Σ_F π_pend (T 0.8) with p̂ = c / n (exact intervals),
binned by p̂ (≥ 10⁻³, 10⁻⁴–10⁻³, 10⁻⁵–10⁻⁴, < 10⁻⁵). Unseen mass:
(i) **coverage** — the share of the base's large-k successes whose proof was already known from another source (any
other model or draw), i.e. what the known set would have captured had the base's own samples not been added;
(ii) **Good–Turing** M̂₀ = f₁ / N on the base's own successes where multiplicities are recoverable (c ≤ distinct + 1
per chunk), and on this run's own large-k reads, which store every success with its multiplicity;
(iii) the corrected estimate Σ_F π / (1 − M̂₀) where defined. Expectations: median ratio estimate / p̂ in
[0.7, 1.2] for p̂ ≥ 10⁻³ (calibration: 0.93–0.98); ratio's 10–90 % range wider than [0.3, 3] for p̂ < 10⁻⁴; coverage
≥ 0.6 for p̂ ≥ 10⁻⁴ and undetermined (≤ 3 successes) below 10⁻⁵. The output is a statement of where the estimator can
be trusted (p̂ range and coverage), not a pass / fail.

**0.2 The budget in base attempts, GPU class measured** (one RTX A6000 pod and one A40 pod, ≈ 1 h each; `pod/coe/timing.sh`).
The same plain read (pend s0–s2, 322 theorems, k 256, batch 2,048 and 1,024) on both classes → seconds per attempt
per class. Restate old seeds' `K_eval-set` (A6000 seconds for r1–r8 ÷ A6000 attempt cost; A40 for r9–r16) and
`K_train`, and recount capability-defs' compute-matched sets (cd_part3 logic, reimplemented in `coe/coe_budget.py`,
checked against the published 22 / 21 / 14 at the published K). Expectations: A6000 per-attempt cost 0.8–1.2 × A40's;
restated r8 `K_eval-set` within ±30 % of 19,281 / 21,107 / 23,310; `K_train(8)` 0.55–0.8 × `K_eval-set`;
compute-matched r8 sets at `K_train` between the published sizes and the 0.3 × K sizes (33 / 28 / 28).

**0.3** These thresholds. **0.4** `claims_ledger.md`: every number the paper might use, with source file and review
status; the claims inherited from `capability-defs`, `support-*`, `trajectory`, `rl-continue` re-audited by a critic
subagent (expectation: ≥ 3 inherited numbers need a correction or a narrower label, as the capability-defs review and
the 2026-10-12 re-check already found several).

## Phase 1: the causal experiment (≈ $90–100)

**Pods and protocol.** One A40 (SECURE) per new seed; each pod: Lean-check the refill (first pod only) → Stage 1
(1,200 s, `--budget_secs 1200`, steps recorded) → pend reads → 16-round ladder in one call (`--rounds 16`, no
segmentation) → r8 / r16 reads beside or after it. Identical code and settings across the 9 new ladders; replay
`--train` = the arm's own pretraining set (K12 or K12⁻), so σ can enter the knockout only through RL's own accepted
proofs. `LEAN_GATE_DUMP` set (literal sampled text, gzipped before upload).

**Deviations from the old seeds' ladders (training identical; measurement only):**
1. `--batch 1024` from round 1 (s0 peaked at 43.4 GB of 44.4 at 2,048 on an A40; s2 OOM'd at 2,048). Batch changes
   only bf16 reduction order: a sampling re-draw (`NOISE_FLOOR.md`; ≈ 1 row in 128 decodes differently).
2. The per-round eval phase is slimmed: transfer sampling at k 32 on **832** transfer theorems
   (`data/coe/transfer_track832.jsonl`: the 760 schema members, i.e. every held-out family member, plus the 72
   generated classical-only theorems) instead of all 2,285, and greedy on 1,000 of the 5,000 `p2/heldout` theorems
   (`data/coe/heldout1000.jsonl`, seeded subset) instead of all. Checked in the code: `found_transfer` and the greedy
   statistics never enter the fine-tune mix, and the round's Python RNG (`Random(S·7919)`, used only for the mix) is
   not consumed by the eval phase; sampling seeds are per round. Saves ≈ 20–25 % of ladder time.
3. Continuous 16-round call; the old seeds were resumed at r9 / r13, which restarted the replay RNG.

**Read-outs.**
- Per round (from ladder files, `coe/coe_rounds.py`): family training shares; per-round held-out family rates (k 32 on
  the 832); number of σ-covered classical targets solved; share of accepted target proofs per round using σ, σ⁺, the
  lemma route, DN on a premise / hypothesis; round of first σ⁺ proof and of first acquisition; replay-free check that
  σ⁺ never appears in the knockout's mix files except in RL proofs.
- pend, r8, r16 of every new seed, and pend / r8 / r16 of s0–s2 on the family sets: plain k 256 (`guided_eval.py --arm
  plain`, seed 0) on R322 ∪ TRACK832 (textbook72 scoring only + holdout250 + the 732 tracked transfer theorems not in
  holdout250, `data/coe/fam_extra.jsonl`; 1,054 theorems);
  guided (`--arm logical`, max_rej 10) at pend and r16; plain x1 (seed 1) at pend and r16. Batch 512 for every read in
  this run (reads share a card with a ladder); old seeds' existing R322 reads (batch 2,048) are reused, labelled.
- General ability, knockout vs full bases: held-out greedy on `p2/heldout` (5,000; and its non-σ subset), holdout250
  pass@256, textbook72 pass@256 (dev58 / train14 / combined).
- **Knockout bases on the classical families:** large-k plain sampling on the 178 σ-covered held-out classical members
  (123 family key-step + 55 generated), n per member chosen so the pooled n ≥ 59.9 · `K_train(16)` of that seed
  (≈ 10,000 per member at K ≈ 30,000), a member stopping at its first success; every success stored with its text and
  multiplicity. This certifies the **pooled** statement (mean p over the 178 < 0.05 / K, i.e. the base reaches < 5 % of
  them within K in expectation); per family the UB95 and the largest K it certifies are reported. The trained σ-covered
  targets (136 + 155) get the base's own round-1 sample (k 32) for free. Second estimate: the knockout base's
  teacher-forced log p of known σ proofs of those members (from the full arm's found files), if the scorer ports.
- **Compute-matched reach on the 322 (standard A)** for every new seed: base 512 attempts (x0 + x1), then on every
  theorem r16 solves and the base fails, more attempts up to n ≥ `K_train(16)`; sampling verdicts primary,
  known-proof estimate secondary where ported. New seeds have no RL-free controls (no replay-only ladder): their sets
  are reported "not netted against RL-free controls".
- **Certification:** every theorem or family a headline sentence rests on gets the certificate above, paid for.

**Decision rule (exact version).**
- **Created (σ acquired from a σ-free base):** on ≥ 2 of 6 knockout seeds, RL r16 acquires a σ-covered classical
  family at the bar, the knockout base is certified out of reach on that family at the seed's K (pooled certificate),
  and the knockout model's accepted proofs of its held-out members use σ⁺ or the lemma route (stated which).
- **Needs exposure:** acquisitions of a family on ≤ 1 knockout seed, and the full arm acquires it on more seeds with a
  one-sided Boschloo exact test p ≤ 0.05 (6 full vs 6 knockout seeds).
- **Neither:** no seed of either arm acquires the family.
- Otherwise (e.g. knockout acquires on 1 seed, full on 2) **undetermined**, reported with the counts and the exact
  test. A negative knockout result is worded "not acquired by this EI from this base", never "RL cannot".
- **Primary test** (one, pre-specified): per seed, "acquired ≥ 1 σ-covered classical family at r16", full vs
  knockout, Boschloo one-sided α 0.05. **Secondary:** per family (Holm-corrected over 6); the number of σ-covered
  held-out members solved at r16 (of 178), exact one-sided Mann–Whitney (critical U at 6 vs 6, α 0.05: U ≤ 7).

**Power, stated before running** (`coe/coe_power.py`, exact). With 6 vs 6 seeds and a one-sided Boschloo test at
α 0.05, the primary test rejects at (full, knockout) acquisitions ≥ (3, 0), (5, 1) or (6, 2). Power:

| per-seed acquisition rate, full \ knockout | 0.00 | 0.10 | 0.20 | 0.33 |
|---|---|---|---|---|
| 1.00 | 1.00 | 1.00 | 0.98 | 0.90 |
| 0.90 | 1.00 | 0.90 | 0.78 | 0.62 |
| 0.67 | 0.90 | 0.62 | 0.41 | 0.23 |
| 0.50 | 0.66 | 0.39 | 0.22 | 0.10 |
| 0.33 | 0.31 | 0.17 | 0.09 | 0.03 |

So the comparison is powered (≥ 0.9) only for families the full arm acquires on ≥ 2/3 of seeds; **excluded middle
alone (1 seed in 3 so far) is not testable at these seed counts** and is reported descriptively. P(≥ 2 of 6 knockout
seeds acquire | per-seed rate q) = 0.11 / 0.34 / 0.64 / 0.89 for q = 0.1 / 0.2 / 0.33 / 0.5: the "created" rule has
little power if creation is rarer than one seed in five, and a 0 / 6 outcome bounds q below 0.39 (one-sided 95 %).
General-ability differences (knockout vs full bases, 6 vs 6): pend held-out greedy sd across seeds 0.021
(`trajectory`: 0.921 / 0.936 / 0.962), MDD ≈ 1.794 · sd ≈ 3.7 pp (`NOISE_FLOOR.md`'s n = 6 constant; that floor was
measured on the 3.2 M model, so this is this model's own seed spread used in its formula).

**What the full arm already does (old seeds, training side; `coe/coe_alloc_shares.py` on `trajectory` + `rl-continue`
`alloc_r.json`; per-round share of trained key-step members with ≥ 1 success in that round's 32 attempts; s0 / s1 / s2).**
- The full **bases** (round 1 = pend's own sample) already solve the σ-covered classical targets that need only σ:
  generated σ-covered targets 0.90 / 0.95 / 0.96 of 155, contraposition_conv 0.76 / 0.03 / 0.97 (s1 0.93 at r2).
- RL then acquires (first round with share ≥ 0.5): negated_conditional r4 / r13 / r4; peirce – / – / r3;
  peirce_sequent – / – / r5; excluded_middle – / r14 / –; demorgan_nand_to_or never (0.00 throughout).
- So in the full arm "≥ 1 σ-covered family acquired" holds on 3 / 3 seeds from round 1–2 (contraposition_conv), and the
  per-seed rate q_full for the primary test is ≈ 1: power ≥ 0.98 if the knockout rate is ≤ 0.2. For the rarer families
  (peirce, peirce_sequent, excluded_middle: 1 / 3 each; demorgan: 0 / 3) the arm comparison has power ≤ 0.31 and they are
  descriptive. In the knockout, σ is the only missing piece for the 155 + 29 targets the full bases already solve, so
  "σ discovered at all" is the event that decides the primary test.

**Expected results (numeric, falsifiable).**
- E1 Knockout bases: held-out greedy (`p2/heldout`, 5,000; 679 have a σ reference proof) 4–12 pp below the full bases',
  within ±2.5 pp on its 4,321 non-σ theorems; holdout250 pass@256 0.88–1.0 × the full bases'; textbook72 within ±4.
- E2 Knockout bases: round-1 share of the 291 σ-covered trained targets with ≥ 1 success ≤ 0.02 on 6 / 6 seeds (full
  bases: ≈ 0.6–0.7 of them); 0 successes on the 178 σ-covered held-out members at k 256 on ≥ 5 / 6; pooled certificate at
  `K_train(16)` met on ≥ 5 / 6; if scored, the median over members of the best known σ proof's log p ≤ −15 nats.
- E3 Full arm, new seeds s3–s5 at r16 (held-out bar): contraposition_conv on 3 / 3, negated_conditional on ≥ 2 / 3;
  peirce, peirce_sequent, excluded_middle each on 0–2 / 3; demorgan_nand_to_or on 0 / 3; ≥ 80 % of the 55 generated
  σ-covered held-out members solved; full arm (6 seeds) acquires ≥ 1 σ-covered family on 6 / 6.
- E4 Knockout arm at r16: acquires ≥ 1 σ-covered family on **0–1 of 6** seeds (my median 0); the first σ⁺ proof, if any,
  appears after round 4; σ⁺ share of accepted target proofs ≤ 1 % on ≥ 5 / 6 knockout seeds at r16.
- E5 Primary test rejects (needs exposure) at p ≤ 0.05; σ-covered held-out members solved at r16 (of 178): full median
  ≥ 80, knockout median ≤ 5.
- E6 Non-classical ability converges: at r16 the knockout seeds' holdout250 pass@256 on non-classical theorems is within
  ±8 of the full seeds' (median).
- E7 Compute-matched reach (new full seeds, `K_train(16)`): Δ_cov > 0 on 3 / 3, in the range +8 to +35.
Any of E1–E7 can miss; misses are reported as misses.

## Phase 2: a sharpening null (≈ $10–20; details in an addendum before its pods)

Sequence-level power sampling of the pretrained bases, target p^α (Karan & Du 2025, Metropolis–Hastings with suffix
resampling from the base at token temperature 1/α, block-wise; `coe/power_sample.py`), on 2 full and 2 knockout bases,
on R322 ∪ the σ-covered held-out classical members, at **matched sampled tokens** (every proposal token counted).
Expectation: at matched tokens power sampling reaches **≤ 3** of each full base's compute-matched "created" theorems
(those the base cannot reach at K by plain sampling) and **0** σ-covered classical members from knockout bases.

## Phase 3 (pre-registered separately, in order of preference, if the budget allows)

A small-dose arm (σ⁺ at 1 % of pretraining, 3 seeds; the first point of a dose-response curve), exploration on
knockout bases if EI never finds σ (guided rollouts / ε after return / reference-prefix starts that stop before the σ
step), an interface pilot, a harder target pool. Costed alternatives go to `next_steps.md`.

## Compute recording

Per arm, seed and round: GPU-seconds and class, generated tokens and attempts, training steps and tokens, Lean checks —
as registry rows (`record.py`; the ladder and readers write them; `coe/coe_compute.py` tabulates and fills gaps from logs,
saying how). Arms are matched on protocol (attempts, steps, tokens per round), not on GPU-seconds; any arm using > 1.25×
its comparator's compute on any recorded quantity is flagged in the write-up.

## Budget and stop rule

$140 / 300 pod-hours (`podbudget create-or-elicit --set 300 140`), A40 SECURE at $0.59 / h (RunPod's billed rate,
recorded per pod by `podnew`). Plan: Phase 1 ladders ≈ $75 (9 × ≈ 14 h), reads ≈ $12, base large-k / certification
≈ $15, Phase 0 ≈ $2, Phase 2 ≈ $12; ≈ $25 reserve for Phase 3 or reruns. RunPod balance kept above $35.
- If A40 stock gives fewer than 9 pods, the 6 knockout ladders start first and the 3 full ladders follow; ladders never
  change GPU class (reads may, labelled).
- A ladder that fails is resumed once from its last complete round (`--resume`); a second failure drops that seed and
  is reported.
- If spend reaches $110 before Phase 2, Phase 2 shrinks to one base per arm; Phase 3 starts only if Phase 1 and 2 are
  complete with ≥ $20 left.
- Hard stop 120 h after the run start (2026-10-17 05:14 UTC).

## Addendum 1 (2026-10-12 06:26 UTC; no ladder round and no read of a new model has finished)

**The per-attempt cost in K depends on which theorems are sampled.** First Phase 0.2 measurement (coe-r0, A40, alone on the
GPU): trajectory's pend s0 on the 322 at k 256, batch 2,048 = 595 s / 82,432 attempts = **7.2 ms per attempt** (sampling
+ Lean), against the 3.6 ms capability-defs used (one J2 chunk on hard theorems, whose attempts fail early). So the
budget needs a stated allocation:
- **Headline, uniform allocation:** `K_train` with c_base = the base's mean seconds per attempt **over the 322**, alone on
  the GPU, batch 1,024, same GPU class as the ladder (every evaluation theorem gets K attempts). For the new bases this is
  a dedicated timing read after each ladder (pend on the 322, k 256, batch 1,024, nothing else on the card).
- **Upper end, adaptive allocation:** `K_adapt` = attempts per hard theorem if the base first spends 512 attempts on every
  one of the 322 and the remaining training-phase GPU-seconds evenly on the theorems it failed in those 512, at their own
  measured per-attempt cost (from the large-k reads).
- Both are reported for the old seeds as well (with the same-class costs of Phase 0.2), next to capability-defs'
  published `K_eval-set` and to `K_att` (ladder target attempts / 322). Verdicts that change between `K_train` and
  `K_adapt` are listed as budget-dependent, not as findings.
- Expectation (Phase 0.2, revised before any further timing): on the 322, the A40 per-attempt cost of the old pend models
  at batch 2,048 is 6–8 ms (s0: 7.2); A6000 0.8–1.2 × A40; restated uniform-allocation `K_eval-set` at r8 is 0.4–0.6 × the
  published 19,281 / 21,107 / 23,310, so the compute-matched r8 sets grow to between the published sizes and the
  0.3 × K sizes (33 / 28 / 28); J9's certificates (slack ≈ 8–9 % in K per the 2026-10-12 ledger check) then hold with
  more margin under the uniform allocation and fail under the adaptive one.

## Addendum 2 (2026-10-12 07:06 UTC; after round 1 of the first ladder (knockout s0), before any acquisition outcome): the σ-covered set

**What happened.** The pre-registered "σ-covered" rule (classical-only and no premise is *itself* a double negation)
does not do what it was written for. Knockout s0's base, in its own round-1 sample, solved 136 of the 155 "σ-covered"
generated targets — with proofs that apply DN to a ¬¬ the sequent supplies (e.g. premise `R → ¬¬Q`, then IMPE and DN;
or a goal `¬¬P → …` whose ¬¬P is assumed and eliminated): 337 such proofs (DN on a premise or hypothesis) and 13 with DN
on a premise-derived line (σ⁺ only), 0 with σ. None of these needs the removed composition. In fact **none of the 189
generated classical-only targets** (and 71 of the 72 transfer ones) is free of ¬¬ subformulas: every generated
classical theorem gets its classical power from a double negation written in the sequent. So "generated σ-covered"
was never a σ test, and the E2 expectation ("round-1 share of the 291 σ-covered trained targets ≤ 0.02") is **missed as
written** (reported as a miss, with this cause).

**Corrected definition (primary from now on; the pre-registered one is reported alongside):** a member is **σ-covered**
iff it is classical-only (G4ip) **and its sequent contains no ¬¬ subformula anywhere**. In a normal proof every formula
is then a subformula of the sequent, so a DN step must cite a double negation the proof itself built: by NEGI (σ), by
another rule from such a line (σ⁺), or via an assumed ¬¬X in a lemma (the lemma route). Counts (`data/coe/families.json`,
keys `strict_trained` / `strict_heldout`): trained 123 (contraposition_conv 27, demorgan_nand_to_or 9,
excluded_middle 38, negated_conditional 16, peirce 15, peirce_sequent 18); held-out 105 (18, 4, 37, 15, 12, 19) plus 1
generated transfer theorem = **106** (`data/coe/sigma_heldout_strict.txt`). Generated classical targets: 0.

**What changes:** every "σ-covered" count in the decision rule, E2–E5 and the certificate uses the strict sets
(families: the six classical families on their strict members; family acquired = ≥ 50 % of its strict held-out members
solved at k 256). E2 becomes: knockout bases' round-1 share of the 123 strict σ-covered trained targets ≤ 0.02 on 6 / 6
seeds; 0 successes on the 106 strict held-out members at k 256 on ≥ 5 / 6. E5: of 106 (full median ≥ 40, knockout
median ≤ 3). The certificate's pooled n is 59.9 · K over the 106. The pre-registered 178 / 291 sets are reported once,
as the secondary line, so the change is visible.

## Addendum 3 (2026-10-12 07:51 UTC; before any Phase 2 production run): the sharpening null

**Pilot (development data, not scored as a result):** trajectory's pend s0 on 32 random non-schema `rl_targets`,
`coe/power_sample.py`, α 4, 16 chains, blocks of 4 steps, 8 MH steps per block: 26 / 32 theorems, 75 % of chains end in a
Lean-accepted proof, acceptance 0.90; plain T 0.8 at the same decoded tokens (≈ 352 attempts per theorem) 31 / 32 (54 %
per attempt), T 1.0 31 / 32 (42 %). The sampler's α = 1 self-test passes (Σ log Z vanishes).

**Production design.**
- Bases: full s0, s1 (`trajectory` pend; old seeds, whose compute-matched sets are known) and knockout s0, s1 (this run's
  pend). Theorems: full bases — their compute-matched r8 set at **K_train** (Phase 0.2; s0 33, s1 27 theorems:
  `data/coe/phase2_cm_ktrain_s{0,1}.txt`); knockout bases — the 106 strict σ-covered held-out members.
- Power sampling at α 4 and α 2: 32 chains per theorem, blocks of 4 steps, 8 MH steps per block. Comparator: plain T 0.8
  (the standard read) and T 1.0, each theorem given exactly the decoded tokens its α-4 run used (`--mode plain
  --budget_from`). Solved = some chain's final state (power) / some attempt (plain) is Lean-accepted. "Visited" proofs are
  reported separately and are not counted.
- **Expectations:** at matched tokens, α-4 power sampling reaches **≤ 3** theorems of each full base's K_train set, and at
  most 2 more than plain T 0.8 at the same tokens; on the knockout bases **0 of 106** for every sampler. Per-chain success
  of power sampling on those sets ≤ 0.02 (the theorems' p under the base is < 1 / K_train by construction). The cost is ≈
  2 A40-hours on coe-r1.
