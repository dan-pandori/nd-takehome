---
written_on: 2026-10-17
written_by: agent:claude (reviewer, independent of the executor)
run: peer-rl-review
---

# Review of run `peer-rl-review`

Reviewer session, 2026-10-17, started 21:54 UTC. The brief is nd-rl `docs/proposals/claude-heavy/BRIEF_peer-rl-review.md`, plus the reviewer role
brief and `AGENT_POLICY.md`. The run is a *reading* run:

- **Part A:** it reviews other mentees' RL work against ours.
- **Part B:** it adds CPU-only re-scores of our stored per-attempt reads. No pod was used.

**Phase 1** (this section) was done in `~/review/peer-rl-review`, without the executor's write-ups:

- `REPORT.md`, `peer_rl_review/notes/*`, `peer_rl_review/out/*`, `numbers.md`, `log.md` and `run_peer_rl_review.md`
  were not opened;
- the executor's four scripts were grepped only for imports and judges (§R1).

The method has two parts:

- **Readers.** Six read-only reader agents read the mentees' branches straight from `~/nd-rl`. They were barred from
  every path of this run and from `docs/project_strategy/2026-10-17*`. Their notes are in `review_prr/readers/`. I
  re-checked their most consequential citations with `git show … | sed -n` myself (marked ✔ below).
- **Own code.** Everything else is my own code in `review_prr/`, run on the VPS (CPU, ≤ 2 processes at a time):

  | file | what it does |
  |---|---|
  | `fml.py` | formula parser, substitution matcher, premise-order-invariant renaming key; self-tests |
  | `overlap.py` | exposure check |
  | `reads.py` | loaders |
  | `passk.py` | unbiased pass@k |
  | `leanrc.py` | Lean harness and an own ND→Lean renderer |
  | `recheck.py` | controls and re-check |
  | `flipcheck.py` | inspects the single-flip controls Lean still accepts |

## §Recount (phase 1, before reading the executor's write-ups)

### R0. What the pre-registration promised

The pre-registration is `preregistration/peer-rl-review.md`, 20:15 UTC, with addendum 1 at 21:36.

- **Part A:**
  - per-person notes, every number with `branch:path:Lline`;
  - the protocol behind each headline number;
  - a comparison table with an apples-to-apples verdict, under a stated definition;
  - explanations marked *established* or *hypothesis*;
  - the executor's own check of every table number.
- **Part B (addendum: no pod), all CPU re-scores:**
  - our checkpoints on Leon's read-out protocol, from stored per-attempt files;
  - a substitution-instance check of our RL targets against textbook72 / Charles173;
  - failure shares on our textbook72 reads.
- **Priors P1–P5,** to be scored in the report.

The recount re-derives each of these independently below. The comparison table and the prior scores come from my own
extraction; they are compared with the executor's in phase 2.

### R1. Hard constraints: all hold

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72…` on HEAD = `origin/main` = `origin/dan`; `git diff origin/main HEAD -- nd_verify` empty |
| `artifacts/TEST_RUN_DONE` unchanged | blob `1d5cf064…` on HEAD = `origin/dan` = `origin/main`; last touched 2026-09-29 (`cf5924e2`) |
| `nd_verify` not used as a judge | the run's four scripts (`charles149_premises.py`, `lean_reject_share.py`, `ours_on_leon_passk.py`, `schema_overlap.py`) import only `collections, gzip, itertools, json, math, os, random, sys`; no `nd_verify`, no Lean, no torch |
| no evaluation file read in training code | the run has no training code at all |
| no pods / spend | `podbudget peer-rl-review` → used 0.00 h, $0.00 (ceiling 60 h / $30). `~/pods.log` has no pod after 2026-10-13. Note: `~/podbudget.log` shows the budget **was** registered (`2026-10-17T20:10:13Z peer-rl-review set HOURS=60 USD=30`, the launcher's timestamp) |

**No quarantine.**

### R2. Provenance of the stored reads

- **Same bytes as the bucket.** I downloaded every per-attempt file the run used from the bucket myself, one at a
  time. All **33** files in the executor's `scratch/` are byte-identical (sha256) to my copies:
  - `best-state/artifacts/bs/eval/{T1,Fz}_best12_s{0,1,2}__tb72.jsonl`;
  - `guided-tts/artifacts/gt/eval/best12_s{0,1,2}_{plain,logical}.rows.jsonl.gz`;
  - `capability-defs/artifacts/cd/j3/s{0,1,2}_r16_logical.rows.jsonl.gz`;
  - `rl-continue/artifacts/rc/eval/s{0,1,2}_r16__tb72_x1.jsonl`;
  - `grpo-best/artifacts/gb/eval/gb_{default,passk,unlikely}_s{0,1,2}_r8__tb72_x1.jsonl`.
- **Draws used.** The run used the grpo-best **x1** draws only. I also pulled the **x0** draws, for a re-draw check.
- **Read settings, from the `.args.json` files:**
  - k 256, T 0.8, `max_action` 512, `max_steps` 96;
  - guided-tts and capability-defs: `max_rej` 10;
  - sampling seed 0 (best-state) or 1 (all others).

  These are Leon's read caps too (§R4).

### R3. Our textbook72 counts (pass@256 plain or guided, T 0.8, Lean alone; my loaders)

All rows are the 9,560,832-parameter ALiBiGPT (`state_env_october` family): proof-state interface `lean_staten`, from
scratch, Stage 1 on K12 (155,000 proofs, 2–12 lines), RL = T1 expert iteration on the 4,495 `rl_targets`. Values are
solved / 72 per seed (s0 / s1 / s2).

| model / read | textbook72 | dev58 | train14 |
|---|---|---|---|
| Stage-1 only, best-state seeds (`Fz_best12`) | 32 / 27 / 27 | 27 / 22 / 21 | 5 / 5 / 6 |
| r8 plain, best-state seeds (`T1_best12`) | 52 / 51 / 52 | 42 / 44 / 42 | 10 / 7 / 10 |
| r8 plain, trajectory seeds (guided-tts `plain`) | 48 / 48 / 53 | 40 / 38 / 42 | 8 / 10 / 11 |
| r8 guided, trajectory seeds (guided-tts `logical`) | 54 / 52 / 57 | 43 / 41 / 45 | 11 / 11 / 12 |
| r16 plain (rl-continue `x1`) | 51 / 57 / 56 | 42 / 45 / 44 | 9 / 12 / 12 |
| r16 guided (capability-defs j3 `logical`) | 55 / 56 / 62 | 45 / 45 / 50 | 10 / 11 / 12 |

Checks on these rows:

- They reproduce the model cards (`docs/models/state_env_october*.md`): 52/51/52, 48/48/53, 54/52/57 and 51/57/56.
- Every file has 256 attempts for every theorem.
- `solved == (n_ok > 0)` on every row.
- In the guided rows, `Σ accepted counts == n_ok` on every row.

**Cut-offs (policy: re-raise `max_new` above 0.1 % per stratum).** These are inherited, not caused by this run, but
they make several pass@256 counts lower bounds.

| read | overall cut-off | textbook72 theorems above 0.1 % | worst theorem |
|---|---|---|---|
| best-state r8 s1 | 2.0 % | 25 / 72 | 39.5 %, `textbook_3d2b05bca4cbb83ed73b`, solved 0 |
| best-state r8 s2 | 1.4 % | 28 / 72 | |
| r16 plain s0 / s1 / s2 | 0.4 / 0.5 / 0.1 % | 18 / 23 / 9 | |
| r8 plain (guided-tts) | | 5 / 13 / 4 | |
| guided reads | ≤ 0.3 % (`step_cap` only) | 0 | |

### R4. Ours on Leon's read-out protocol

**Leon's protocol** (reader `leon_recipe_eval.md` §4, citations re-checked ✔ `origin/leon/main:…/RECIPE.md:L30-39,
L221-237`):

- per-step proof-state model (`S1g3`, ≈ 9.6M, the vendored `danstate` environment);
- n = 64 attempts per problem on textbook72 and Charles149, T 0.8, `max_action` 512, `max_steps` 96;
- plain read (an environment rejection ends the attempt) and guided read (`logical`, ≤ 10 redraws per attempt);
- judge: Lean alone;
- metric: the unbiased pass@k for k = 1 and 5, averaged over problems and seeds;
- Charles149 = Charles173 minus 24 names in Leon's `charles_eval/charles_clean.report.json` (re-derived: 24 distinct
  names, all in Charles173; 149 kept).

**Ours, re-scored from the stored 256-attempt reads.** Same estimator; values are % of the set, mean of 3 seeds
(IQM at n = 3 = mean), with per-seed values in brackets.

| our model / read | textbook72 pass@1 | textbook72 pass@5 | Charles149 pass@1 | Charles149 pass@5 |
|---|---|---|---|---|
| Stage-1 only (best-state seeds) | 15.2 [14.8 / 14.0 / 16.7] | 23.0 | — | — |
| r8 plain (best-state seeds) | 39.2 [39.6 / 39.0 / 39.0] | 53.6 | — | — |
| r8 plain (trajectory seeds) | 39.2 [38.9 / 36.0 / 42.6] | 53.1 | 31.8 [29.5 / 29.8 / 36.1] | 48.5 |
| r8 guided (trajectory seeds) | 47.0 [45.7 / 44.9 / 50.4] | 61.1 | 43.4 [41.7 / 40.9 / 47.6] | 60.9 |
| r16 plain | 42.9 [40.9 / 43.6 / 44.2] | 57.6 | not read | not read |
| r16 guided | 50.7 [48.7 / 50.5 / 52.9] | 64.7 | not read | not read |
| grpo-best GRPO arms, r8, x1 (default / passk / unlikely) | 41.0 / 37.3 / 42.0 | 49.8 / 51.4 / 51.2 | — | — |

**Leon's corresponding numbers** (✔ `…/matched_eval/v2_results_ynez.md:L24, L209-220`; `RECIPE.md:L38-39`):

| Leon model | textbook72 plain | Charles149 plain | textbook72 guided | Charles149 guided |
|---|---|---|---|---|
| final recipe (GRPO "merged + KL 0") | **74.0 / 82.3** | **70.5 / 78.9** | pass@1 78.0 / 83.6 / 79.2 per seed (mean 80.3); pass@5 mean 86.5 | 77.4 / 84.1 |
| his EI baseline | 68.4 / 77.9 | 62.2 / 73.8 | | |

Values are pass@1 / pass@5, in %.

What the comparison rests on:

- **Leon's own Stage-1 reads** 43.8 / 39.6 / 32.3 % textbook72 pass@1 (`RECIPE.md:L71-72`; read protocol not
  stated). Ours is 15.2 %.
- **Protocol differences that remain:**
  - n 256 vs 64: the estimator is unbiased either way;
  - sampling seed;
  - Leon's model thinks (B64), so his attempts are longer. The match is per attempt, not per token;
  - our r16 Charles reads do not exist.
- **A second measurement of one of our models by someone else.** Robbie's temperature sweep scored
  `la_T1_best12_s0_r16` on textbook72 under Lean alone, at T 0.8, 64 attempts. He got pass@1 0.407 and oracle@64
  0.653 (✔ `origin/robbie-experiments:…/temp_sweep_20261006/results_table.md`, textbook72, T 0.8 row). My
  re-score of r16 s0 gives 40.9 % and unbiased pass@64 67.2 %, consistent within one draw.

### R5. Exposure: our training sets against textbook72 and Charles's sets (own matcher, `review_prr/overlap.py`)

**Definitions.**
- *Instance:* some training sequent is σ(E) for the evaluation sequent E, with σ mapping atoms to formulas and
  premises matched as a multiset.
- *Renaming twin:* σ is an atom bijection; premise order is ignored.

**Results.**

| training file | textbook72 dev58 / train14 | Charles `candidate_v0` (87) / `v1` (72) / `batch3` (14) / `hand14` |
|---|---|---|
| `data/ladder/rl_targets.jsonl` (4,495, the RL targets of every ladder) | **10** instances (9 / 1), 40 targets each, all textbook-schema rows; 0 renaming twins | 0 / 0 / 0 / 0 instances; 0 twins. One `batch3` theorem (`textbook_2db1a03407fe63d072d5`) is itself an instance of a target schema |
| K12 `train_k12.jsonl.gz` (155,000, Stage 1 of every model above) | 13 instances (9 / 4); 1 renaming twin with premises swapped (`textbook_3ed45280e6c686e76ac6`, the known disjunctive-syllogism twin) | 16 / 3 / 3 / 0 instances; 1 twin (`textbook_9d21fcccbcd6c3ebf207`, also on Leon's removal list) |

The 10 instance-exposed textbook72 theorems are:
- dist ∧/∨ (both directions, plus the converse);
- three De Morgan forms;
- negated conditional;
- import;
- disjunctive syllogism;
- Peirce (train14).

What the exposure means for the counts:

- **Solves on the exposed 10.** Stage-1 solves 6 / 5 / 3 of them and r8 solves 9 / 9 / 10. Of RL's +20 / +24 / +25
  textbook72 gain (best-state seeds), +3 / +4 / +7 is on schemata it trained on.
- **Leaving the 10 out.** On the other 62, ours solves 43 / 42 / 42 (r8, best-state seeds) and 42 / 47 / 46 (r16).
- **Leaving them out of the pass@1 comparison.** On `tb72_clean62` our pass@1 is 35.4 (r8 plain), 38.5 (r16 plain)
  and 46.6 (r16 guided), 3.8–4.4 points below the full-set values.

### R6. Failure shares on our textbook72 reads

Shares are of all 18,432 attempts per read. Three categories:

- *Lean-rejected:* a finished proof rejected at the gate. With the prefilter on, this is the prefilter's decision; see
  R8 C2.
- *env:* the strict grammar / environment rejected a step.
- *cut-off:* `action truncated` or step cap.

| read (s0 / s1 / s2) | ok | Lean-rejected | env | cut-off | Lean-rejected / finished |
|---|---|---|---|---|---|
| Stage-1 (best-state) | .148 / .140 / .167 | .484 / .491 / .557 | .368 / .367 / .275 | .000 / .002 / .000 | .77 / .78 / .77 |
| r8 plain (best-state) | .396 / .390 / .390 | .113 / .174 / .162 | .491 / .415 / .435 | .001 / .020 / .014 | .22 / .31 / .29 |
| r16 plain | .409 / .436 / .442 | .106 / .135 / .193 | .481 / .424 / .364 | .004 / .005 / .001 | .21 / .24 / .30 |
| GRPO default r8 x1 | .362 / .412 / .455 | .281 / .179 / .194 | .357 / .410 / .351 | .000 / .000 / .000 | .44 / .30 / .30 |
| GRPO passk r8 x1 | .365 / .352 / .402 | .322 / .189 / .275 | .313 / .458 / .323 | .000 / .001 / .000 | .47 / .35 / .41 |
| GRPO unlikely r8 x1 | .376 / .416 / .468 | .228 / .198 / .212 | .396 / .386 / .320 | .000 / .000 / .000 | .38 / .32 / .31 |

`len(reasons) == n_tried − n_ok` holds on every row. My "env" excludes truncations; a definition that counts every
`lean_seq parse:` reason as env would add the cut-off column to it.

### R7. Premise count and prior P5

**Charles's distract2 release, on our checkpoints** (✔ `origin/charles/main:data/pretrain_data/
release_2026-10-12_textbook72_distract2/metrics/dan.metrics.jsonl`; README L20-28):

- Protocol: k 32, T 1.0, his CPU environment sampler, one seed.
- **Judge: the pinned `nd_verify`, not Lean** (README L149, L322-323).
- `la_T1_best12_s0_r8`: problems crossing to ≥ 4 premises go from 17 solved to **0** after two unused premises.
  "Solved both" is 0 in the 2→4 and 3→5 bins.
- `stage1_best12_s0_b1200`: 8 → 0.

So on Charles's measurement, the share of crossing problems still solved among those solved undistracted is
**0 / 17 = 0 %** (r8 s0) and 0 / 8 (Stage 1). That is ≤ 10 %: **P5 holds** (one seed, `nd_verify` judge).

The failure is the environment's `PR position` rule on the first action (README L221-224). It happens before any
judge sees the proof, so it is judge-independent for our environment. That is my inference from his trace, not a
Lean measurement.

**Our own reads, by premise count (pass@256, s0 / s1 / s2).** No seed of ours solves a 4-premise problem, plain or
guided:

| read | textbook72, 4 premises (n 1) | Charles173, 4 premises (n 5) | Charles173, 3 premises (n 28) |
|---|---|---|---|
| r8 plain | 0 / 0 / 0 | 0 / 0 / 0 | 20 / 19 / 22 |
| r8 guided | 0 / 0 / 0 | 0 / 0 / 0 | 26 / 25 / 24 |

### R8. Lean re-check: controls first, then counted proofs (`review_prr/recheck.py`, `out/recheck.txt`)

**Harness.**

- Lean 4.34.0 (`~/.elan/toolchains/leanprover--lean4---v4.34.0`), `lean -DmaxErrors=100000000`.
- Each file holds 250 theorems, one per line, each followed by `#print axioms`.
- A theorem is accepted iff three things hold: no error on its line, no `sorry` warning, and its axioms are a subset of
  {propext, Classical.choice, Quot.sound}.
- Theorem names are renumbered at file-write time, inside the recursive split.
- My own statement renderer writes `theorem tK (P Q R S : Prop) (h1 : …) … : C := by <text>`.

**Negative and positive controls (all as required):**

| control | checked | accepted | expected |
|---|---|---|---|
| C1 untouched accepted literal texts | 300 | 300 | all pass |
| C2 gate-dump texts the prefilter rejected (best-state dumps, 28,662 such rows) | 600 | **0** | all fail |
| C3 accepted text paired with another theorem with the same premise count | 300 | 0 | all fail |
| C4 one `Or.inl`↔`Or.inr` or `.1`↔`.2` flip | 300 | 20 | nearly all fail |
| C4′ 400 `Or.inl`↔`Or.inr` flips, inspected (`flipcheck.py`) | 400 | 16, **all inside an `( X ∨ X )` step** | benign no-ops only |
| C4″ 400 `.1`↔`.2` flips, inspected (`flipcheck2.py`; the projected name's nearest binding) | 400 | 11, **all on an `( X ∧ X )` hypothesis** | benign no-ops only |
| C5 bare `sorry` | 20 | 0 (all `sorry`) | all fail |
| C6 final `exact` removed / C7 cut at a random token | 300 / 200 | 0 / 0 | all fail |
| V1 own ND→Lean rendering of 800 Lean-accepted dump proofs | 800 | 800 | all pass |
| V2 own rendering of prefilter-rejected dump proofs | 595 | 0 | all fail |
| V3 own rendering after one ORI1↔ORI2 flip in the ND | 300 | 17 | nearly all fail |

**Counted proofs.** Each arm-seed contributes one proof per solved theorem plus random fill to ≥ 150; the totals below
are per arm, over 3 seeds. Where literal text is stored (guided-tts and capability-defs `accepted` dicts, best-state
gate dumps), that text is checked. Where only ND strings are stored (rl-continue, grpo-best; neither run kept a gate
dump), my own rendering is checked.

| arm | checked | accepted |
|---|---|---|
| r8 plain, trajectory seeds (literal; textbook72 + Charles sets) | 538 | 538 |
| r8 guided, trajectory seeds (literal) | 589 | 589 |
| r16 guided (literal; textbook72 + holdout250) | 901 | 901 |
| r8 plain, best-state seeds (literal, dump) | 450 | 450 |
| Stage-1, best-state seeds (literal, dump) | 450 | 450 |
| r16 plain (own rendering) | 450 | 450 |
| GRPO default / passk / unlikely, x0 and x1 (own rendering) | 6 × 450 | all |

**Total: 6,078 of 6,078 counted proofs accepted.** No finding. (Erratum: the phase-1 commit message said 6,328, a summing slip. The per-arm rows here add to 6,078, as `out/recheck.txt` does.)

### R9. Peer numbers re-extracted (readers' notes; protocol in brackets)

**Leon** (`readers/leon_recipe_eval.md`, `readers/leon_grpo.md`):

- **Models.** Per-step proof-state models on our vendored environment (`danstate`), ≈ 9.6M, from scratch. Stage 1 =
  S1g3, honest-search thinking traces over K12, with textbook72 excluded by class.
- **RL.** Dr. GRPO, L2 (10–12-line) → L3 (13–15-line) curriculum, 39 iterations × 4,096 attempts per stage, KL 0 in
  L3. The verifier "stop" sampler is used in training.
- **Judge:** Lean alone.
- **Headline:** the final recipe reads 13–20 32.1 / 57.8, textbook72 74.0 / 82.3, Charles149 70.5 / 78.9 (pass@1 /
  pass@5, 3 seeds, plain).
- **Against EI:**
  - level on 13–20 (+0.6 / −0.1);
  - ahead on textbook72 (+5.6 / +4.4) and Charles149 (+8.4 / +5.1);
  - the Charles149 lead shrinks at matched tokens (+7.3 at 1k → +1.7 at 8k).
- **No review** of any of it.
- **Caveats the readers found, with citations:**
  - dev58 was the design set for the generator of his RL pools (`gap_analysis/README.md:L8-10`);
  - textbook72 was read in the single-seed pilots that chose the merged recipe's components (`RECIPE.md:L313-314`);
  - EI had about 4–5 unanalysed pilots against GRPO's about 15;
  - seed 1's final weights are "it 30 plus one iteration";
  - his checkpoints and rows are on his machine (`/scratch`), so P3 cannot be tested.
- **The earlier decision went the other way.** On 2026-10-08 EI was chosen ("EI is the RL method"). In v1 GRPO led
  in distribution at pass@1 (+10 to +16) and tied at pass@5.

**Robbie** (`readers/robbie.md`):

- **Retry-EI** (multi-attempt episodes with Lean error tokens): every variant is below plain EI on his dev metric
  (`iid` 771; `resume` 762, `blank` 718, `retry` 712, `repair` 706, `resume_rl` 619; 590 control 792).
- **Factorial:**
  - Leon's EI recipe on the best pretraining lowers held-out pass@1 43.8 → 30.1 % and raises pass@64 58.9 → 79.1 %.
  - textbook72 pass@256 27.8 → 43.5 %.
  - Re-derived by the reader from `passk.csv`; I re-checked ✔ `combined-model/README.md:L113-120`.
- **c005, test-time scaling.** textbook72 plain pass@1 17.6 % and pass@256 41.7 % (30 / 72); resampling 26.0 /
  50.5 %.
- **GRPO wall** (2026-10-14): post-hoc model-diff analysis of a long-RL run. The run itself is not committed: no
  recipe, compute or judge in git.
- **Temperature sweep** (on our r16 s0, Lean alone): T 0.8 is fine.
- **Judges:**
  - Robbie's whole-proof numbers are **Lean ∧ `nd_verify`**, through fork 51604b3's gate, in all of his own
    harnesses;
  - the proof-state-recipe comparison and the temperature sweep are **Lean alone**.
- **Dev metric:** one draw of any-of-64 on the 1,108-theorem dev half of `transfer.jsonl`, T 0.8, `max_new` 512. Not
  textbook72's dev58.

**Dmitry** (`readers/dmitry.md`; re-checked ✔ on the reader's own recomputation from committed JSON):

- **Models.** Every number is on **our** r16 checkpoints, mostly s0. Judge: Lean alone.
- **Sprint A** (selection and stopping on a frozen r16), textbook72 / holdout250, k 64, T 0.8:
  - random pick (= pass@1): 0.405 / 0.836;
  - own-likelihood choice of 1 of 8: 0.540 / 0.918;
  - pairwise-trained sibling judge: 0.582 / 0.933;
  - oracle pass@8: 0.594 / 0.940.

  Selection cannot change pass@1 or coverage. It moves single-answer accuracy at a budget towards pass@m.
- **Stopping.** The trained-judge threshold closes about half of the count-to-oracle gap at a matched attempt count.
- **Sprint B** (learned allocation, joint REINFORCE):
  - feature-logistic selection reads 87.5 % on a 400-theorem synthetic test;
  - joint RL raises first-proof accuracy +12.6 pp in distribution, but its retry policy is ≤ its own first proof;
  - on textbook72 nothing beats first proof (41.4 vs 41.7 %).
- **Not committable:** the per-item data of Sprint B are not in git.
- **His r16 s0 baselines agree with my re-score of the same checkpoint:**

  | quantity, textbook72 | Dmitry | mine |
  |---|---|---|
  | pass@1 | 0.405 | 0.4095 |
  | pass@8 | 0.594 | 0.5985 |
  | pass@64 | 0.694 (one draw) | 0.672 (unbiased) |

**Charles** (`readers/charles.md`):

- **Data.** Release 2026-10-02 (87 / 72 / 14 / 14 + 225 derived), audited curry-aware against textbook72.
- **Scores of our r8 s0 / s1, at k 32, T 1.0, Lean gate, 48 steps / 256 tokens per action:**

  | set | r8 s0 | r8 s1 |
  |---|---|---|
  | textbook72 | 49 / 72 | 47 / 72 |
  | `candidate_v0`, pre-re-cut | 76 / 104 | 73 / 104 |
  | `candidate_v1`, pre-re-cut | 49 / 80 | 50 / 80 |

  My expected pass@32 of best-state r8 s0 at T 0.8 is 48.0 / 72.
- **The four-premise zero** (0 / 7 four-premise problems, all models).
- **The pool screens** (`nd_verify`, k 32, T 1.0, one checkpoint each).
- **The distract2 result** (R7).
- **The "environment writes the premise block" diagnostic:** 118 / 120 four-premise generator problems and 38 / 71
  distracted textbook72 problems, with the same checkpoint and no training. Judge `nd_verify`; a diagnostic only.
- **Untrained:** no pool of his has been trained on.

**Our side** (`readers/ours.md`): the anchors are the model cards, reproduced in R3. Further facts this review leans on:

- **Two trainings share one name.** `state_env_october` names two trainings of one recipe: best-state seeds (52 / 51 / 52)
  and trajectory seeds (48 / 48 / 53, A6000 ladders).
- **dev metric:** best-state r8 1,058 / 1,050 / 1,055, Lean alone, k 64, one draw.
- **grpo-best,** equal attempts against EI (trajectory seeds):
  - default and unlikely arms lose more theorems than they gain against EI over the 322 (15 vs 38, 15 vs 44);
  - pass@4 arm: +7.7 on group C, unresolved at n = 3.
- **The textbook72 MDD at cap 12 is 6.5.** It was pre-registered in `best-state` (3 vs 4 seeds, two-sample t), not in
  `NOISE_FLOOR.md`, which has no textbook72 row.
- **Robbie's factorial cells are not RL-trained on train14.** The atlas says they "were RL-trained on 14 of the 72
  textbook72 theorems" (`ATLAS.md:L61-62`). Robbie's code says otherwise:
  - `factorial_20260929/passk.py:L5-7`: "never trained on"; `split` is only the source file;
  - the RL pools of `leon_rl.py` are `rl_targets` (1,500 seeded, or the full 4,495), checked ✔.

  So that atlas line looks wrong. Robbie's RL **does** share our 10 schema-exposed textbook72 theorems, through the same
  `rl_targets` file (R5).

### R10. Prior scores (mine, from the extraction above; compared with the executor's in phase 2)

- **P1** (≥ half the comparison rows differ in k, set, plain/guided or judge): it depends on which rows a table
  includes. My table (R11) has 17 rows:
  - **6** differ in one of those four items (rows 8, 9, 10, 12, 16, 17);
  - **1** differs only in T and caps (row 15);
  - **1** has an unstated protocol (row 7);
  - **9** are apples to apples.

  That makes 6–7 of 17, short of half. Scored against the executor's own table in phase 2.
- **P2** (Leon's GRPO − EI gap at his largest k < half the pass@1 gap): his largest reported k is 5 on every v2 set.
  - On his primary v2 set (13–20, 3 seeds), recipe − EI is +0.6 → −0.1. That technically holds, but the pass@1 gap is
    zero within its interval [−1.9, +3.7], so the test is vacuous.
  - On the sets where GRPO does lead, pass@5 keeps 79 % (textbook72, +5.6 → +4.4) and 61 % (Charles149, +8.4 → +5.1)
    of the gap. **Falsified there.**
  - In v1 (hard12, in distribution) it holds clearly: +12.3 → −0.4.
  - The prior's mechanism, a shrinking lead with more samples, shows only on the token axis: Charles149 +7.3 at 1k
    tokens → +1.7 at 8k.
  - **My score: falsified as worded on his human-written headline sets; holds on 13–20 only vacuously.**
- **P3:** **untestable.** Leon's checkpoints are machine-local; no pod was run.
- **P4** (Robbie's retry-EI and Dmitry's selection / allocation improve budgeted, low-k numbers more than large-k
  coverage):
  - **Dmitry: holds, by construction.** Selection and stopping act on single-answer accuracy at a budget; coverage
    (pass@m) is unchanged. Sprint B's joint RL raised first-proof accuracy in distribution (+12.6 pp) and not coverage.
  - **Retry-EI: not supported.** It improved nothing at any k: every arm sits below plain EI's 771 on the k-64 dev
    metric, and attempt-2 success is ≤ the independent rate.
  - **Robbie's other work cuts both ways:**
    - his inference-time resampling is a low-k gain (+26 pp at k 1 on held-out, +8–9 on textbook72 at every k), which fits
      the prior's direction;
    - his RL recipe (Leon's EI port) does the opposite: large-k coverage up, held-out pass@1 down.
  - **My score: half supported** (Dmitry yes, retry-EI no).
- **P5:** **holds** (R7): 0 / 17 on Charles's measurement of our r8 s0.

### R11. My comparison table (closest comparable numbers; verdict under the pre-registration's definition)

The pre-registration's definition: **apples to apples** = same judge, same theorems, same k, same T, same plain/guided,
same compute basis (here: attempts per theorem).

| # | theirs (model; protocol) | ours (model; protocol) | protocol differences | verdict |
|---|---|---|---|---|
| 1 | Leon GRPO recipe: textbook72 74.0 / 82.3 (pass@1 / pass@5; n 64, T 0.8, plain, Lean) | r16 42.9 / 57.6; r8 39.2 / 53.6 (same estimator from n 256) | none at read-out; Leon's attempts carry B64 think tokens | apples to apples |
| 2 | Leon recipe, guided: textbook72 80.3 / 86.5 | r16 guided 50.7 / 64.7 | none (same `logical` arm, ≤ 10 redraws per attempt) | apples to apples |
| 3 | Leon recipe: Charles149 70.5 / 78.9, plain | r8 plain 31.8 / 48.5 (r16 not read on Charles's sets) | none at read-out; our r8, not r16 | apples to apples |
| 4 | Leon recipe, guided: Charles149 77.4 / 84.1 | r8 guided 43.4 / 60.9 | as row 3 | apples to apples |
| 5 | Leon EI baseline: textbook72 68.4 / 77.9 | our EI r8 39.2 / 53.6 | none at read-out | apples to apples |
| 6 | Leon GRPO − EI, textbook72: +5.6 / +4.4 | our GRPO − EI, textbook72, same draw seed (trajectory seeds): default +1.8 / −3.4, unlikely +2.8 / −1.9, pass@4 −1.8 / −1.8 | none at read-out; RL budgets differ (his 2 × 159,744 vs our 1.79 M attempts) | apples to apples |
| 7 | Leon Stage-1 S1g3: textbook72 pass@1 43.8 / 39.6 / 32.3 % | our Stage-1 15.2 % (best-state seeds) | his read protocol not stated (probably B256) | not comparable as stated |
| 8 | Robbie c005: textbook72 pass@1 17.6 %, pass@256 41.7 % (Lean ∧ `nd_verify`, whole proof) | r8 39.2 % / 71.8 % (52 / 51 / 52) | judge | same set, different protocol |
| 9 | Robbie factorial best cell: textbook72 32 / 30 / 32 of 72 | r8 52 / 51 / 52 | judge | same set, different protocol |
| 10 | Robbie c005 dev metric 904.3 | best-state r8 1,058 / 1,050 / 1,055 | judge | same set, different protocol |
| 11 | Robbie 198 proof-state recipe, dev 852 / 824 / 798 (Lean alone) | 1,058 / 1,050 / 1,055 | none at read-out; RL 4 rounds vs 8 | apples to apples |
| 12 | Robbie resampling gain on c005, textbook72 k 1: +8.4 pp | our guided − plain at k 1: +7.8 (r8 and r16) | judge; mechanism (line resampling vs `step_check` redraw) | same set, different protocol |
| 13 | Robbie's temperature sweep of **our** r16 s0: textbook72 pass@1 0.407, oracle@64 0.653 | my re-score: 40.9 %, pass@64 67.2 % | none (same model) | apples to apples; reproduces |
| 14 | Dmitry on **our** r16 s0: textbook72 pass@1 0.405, pass@8 0.594, pass@64 0.694 | 0.4095 / 0.5985 / 0.672 | none | apples to apples; reproduces |
| 15 | Charles on our r8 s0: textbook72 49 / 72 at k 32 (T 1.0, Lean gate, 48 / 256 caps) | expected pass@32 48.0 / 72 at T 0.8 (96 / 512 caps) | T, caps | same set, different protocol (not in P1's four items) |
| 16 | Charles distract2 on our r8 s0: 49 / 71 originals (k 32, T 1.0, `nd_verify`) | 52 / 72 at k 256, T 0.8, Lean | k, T, judge, set (71 of 72) | not comparable |
| 17 | Charles: four-premise problems 0 / 7 (k 32) | ours 0 / 1 textbook72, 0 / 5 Charles173 at k 256, every seed, plain and guided | k, T | same direction; not comparable as a rate |

**What the table shows.**

- Leon's model is far ahead under an identical read-out: 31 points of textbook72 pass@1 over our best plain model, and
  30 points guided.
- His **EI** baseline is ahead by the same margin (68.4 vs 39.2), so the gap is not GRPO against EI.
- It is already present at Stage 1. His S1g3 reads 32–44 % pass@1 (protocol unstated); ours reads 15 %.
- The leading explanations in his own documents are:
  - honest-search thinking traces in Stage 1 (`OVERNIGHT_20261008.md:L173-177`);
  - L2/L3 RL pools of 10–15-line problems from a generator designed on dev58 failures, which makes textbook72 a design
    set for him;
  - the textbook72 reads of his single-seed pilots.

  I have not tested any of these.

### R12. Notes on the kit and on visibility

- `review_prr/scratch/` (the bucket copies, ≈ 57 MB including K12) is not committed. Every file can be re-pulled from
  the paths in R2 and from `cap-horizon/data/kh/train_k12.jsonl.gz`.
- The reader notes quote mentees' nd-rl branches. nd-rl is private and the fork is public. They follow the precedent
  the executor asked Dan about (`QUESTIONS.md`, 2026-10-17, item 2, default: keep on the fork branch). Nothing goes to
  the bucket.
- textbook72 theorems are named by id only in my outputs: `overlap.py` strips their sequents.

## §Phase 2 — the executor's claims against the recount

Read after `875e60d9` was pushed:
- `peer_rl_review/REPORT.md` (at `0f92c381`), `numbers.md` § peer-rl-review, `run_peer_rl_review.md`;
- `log.md` § peer-rl-review, the STATUS lines and the pre-registration addendum;
- the four scripts and `peer_rl_review/out/*`;
- `notes/report_check.md`;
- the executor's transcript (`~/runs/peer-rl-review/executor.claude_1.jsonl`), only to time the pre-registration.

Extra checks run for this phase:
- **Leon's files**, via `git show`: `stage1_stats/tb72.md`, `OVERNIGHT_20261008.md`, `matched_eval/{matched_tb72,
  tts_uplift_tables, confusion_tb72, confusion_charles149, v2_results, v2_results_ynez}.md`, `THINKING_UPLIFT.md`,
  `curriculum/README.md`, `gap_analysis/README.md` and `EXPERIMENT_QUEUE.md`.
- **Leon's vendored code**, compared by blob hash.
- **Robbie's public HF summaries** for `long-rl-20261014-*`: 16 `summary.json` files, read-only.
- **Dmitry's `phase5.py`.**
- **My own hierarchical bootstrap** (`review_prr/boot.py`).

Verdict codes: **R** reproduces · **D** differs (by how much) · **W** reword (number right, wording or inference not
supported as written) · **N** not derivable.

### The numbers (all † values, `numbers.md` and `out/*`)

| # | claim (location) | my value / check | verdict |
|---|---|---|---|
| 1 | Every † pass@1 / pass@5 cell: frozen, r8-bs, r8-tj plain and guided, r16 plain and guided, GRPO arms, on textbook72 / `tb72_clean62` / Charles149 (`numbers.md` table; REPORT rows 1–9) | identical to R4 / `review_prr/out/passk_generic.txt` and `ours_on_leon.txt` at one decimal, every cell | R |
| 2 | Paired GRPO − EI, textbook72: default +1.8 / −3.4, unlikely +2.8 / −1.9, pass@4 −1.8 / −1.8 | same point values (R11 row 6) | R |
| 3 | Bootstrap intervals, e.g. frozen 15.2 [10.9, 19.7]; default − EI [−3.3, +6.8] | The executor's `hier_boot` resamples problems **independently within each resampled seed**. Leon's method, which the report compares against, shares one theorem resample across seeds and arms. Mine (shared): frozen [8.7, 22.5], default − EI [−4.6, +8.2], r16 [33.7, 52.4]. Every textbook72-level conclusion is unchanged | D (intervals ≈ 21–36 % narrower than shared-resample: widths 8.8 vs 13.8, 10.1 vs 12.8, 11.9 vs 18.7). Leon's own differencing of different models also resamples seeds independently per arm, which widens them further: default − EI [−5.9, +9.2] (checker's re-run). Conclusions R | |
| 4 | "On `tb72_clean62`, unlikely is +4.5 [+0.5, +9.0] at pass@1" (`numbers.md`) | point value +4.5 ✓. Shared-resample interval [−0.6, +10.5]; [−2.4, +11.6] with seeds resampled per arm as in Leon's `stats.py`. It is also a post-hoc subset | W: not resolved; label exploratory |
| 5 | Exposure: 400 of 4,495 targets (10 schemata × 40) are instances of 10 textbook72 theorems (9 dev58 / 1 train14); 0 renamings; 0 Charles173 | same 10 ids (`tb72_with_target_instances.json` = mine), same counts (R5) | R |
| 6 | Failure shares, frozen Lean-rejected .484 / .491 / .557; r8 .113 / .174 / .162; env-rejected (truncations included) | identical (R6; my env column excludes truncations, theirs includes them) | R |
| 7 | Charles149 has 5 four-premise problems; our r8 accepts 0 of 256 on each, every seed, plain and guided. Pass@1 by premise count (s0) 31.1 / 38.7 / 30.9 / 14.6; tokens per attempt 235.0 / 226.8 / 211.2 plain, 382.1 / 361.2 / 345.9 guided | all reproduced (`review_prr/out/premise_tokens.txt`); all 5 four-premise Charles173 problems are in Charles149 | R |
| 8 | textbook72 files byte-identical to `data/eval_only/textbook72/`; Charles149's 24 removed names | sha256 `1b04192d…` / `e6a219e0…` = `data/eval_only` = Charles's and Dmitry's sealed hashes. Our `data/gt/candidate_*`, `batch3`, `hand_proved_14` = Charles's 2026-10-02 MANIFEST hashes. The 24 names are identical | R |
| 9 | Inputs and settings (k 256, T 0.8, 96 / 512 caps, seeds) | `.args.json` files; 33 / 33 inputs sha256-identical to the bucket | R |
| 10 | Compute: CPU only, no pods, $0 | `podbudget` 0.00 h / $0; no pod in `pods.log` since 10-13 | R |
| 11 | Bucket: `peer-rl-review/{out,data}` | 6 files present (`hf buckets list`) | R |

### REPORT summary and per-person sections

| # | claim | my value / check | verdict |
|---|---|---|---|
| 12 | Charles149 pass@1 70.5 (his recipe) vs 31.8 (our r8); textbook72 74.0 vs 42.9 (our r16) | ✔ `RECIPE.md:L38-39`; mine 31.8 / 42.9 | R |
| 13 | His pass@5 82.3 % beats our plain coverage at 256 (71–79 %) | r16 51 / 57 / 56 of 72 = 70.8–79.2 % | R |
| 14 | "His no-think K12 base reads 17.2 % and ours 15.2 %, so the pipelines agree" | ✔ `stage1_stats/tb72.md:L11` (T0, 3 seeds, k 256, B0, 17.2 [10.4, 25.1]); ours 15.2 | R |
| 15 | **"Most of the gap is Stage-1 data, not the RL algorithm"**: +14 before RL, ≈ +21 after the same EI (single seeds) | All numbers ✔: OVERNIGHT L176 (+14.4 [+8.0, +21.4]); L234 / L271 (52.4 / 53.6); `matched_tb72.md` L14 / L21 (30.8 / 32.4). "Not the RL algorithm" is established by his EI baseline: 68.4 / 62.2 on textbook72 / Charles149 against our 39.2 / 31.8. "Most of the gap is Stage-1 data" rests on one unreviewed pipeline: 2–3 seeds before RL and single seeds after. The ordered decomposition (T0 → T0S → pool → curriculum → thinking + GRPO) is not unique | W: say "in his own ablations the largest single step is Stage-1 proof style" |
| 16 | Pool "up to 9"; thinking "4–12 per attempt at ≈ 3× tokens"; GRPO "≈ 5 over EI" | ✔ OVERNIGHT L265-277 (+9.3 [+3.8, +15.2], +7.2); `tts_uplift_tables.md` (+4.2 / +11.7 / +8.6; 2.73–2.90×; 1k tokens −0.9 / +5.4 / +1.5); `RECIPE.md:L277` | R |
| 17 | "Robbie, Dmitry and Charles report no RL gain over ours" (run summary) | true on textbook72. Dmitry's REINFORCE gains +12.6 pp first-proof accuracy in distribution on a synthetic set | W: add "on textbook72" |
| 18 | §1.1 search-proof Stage-1: +14.4 and +26.0 hard12; Lean rejections 55.4 → 17.8 % | ✔ OVERNIGHT L176, L179-181 ("of attempts") | R |
| 19 | §1.1 redraw arm 14.9 vs plain GRPO 29.3 | ✔ values, but s0 only against s0 + s1 pooled. The paired s0 difference is −14.2 [−15.7, −12.6] (`v2_results.md:L343`) | W (minor) |
| 20 | §1.1 "pilots that lost (§7–8, L1116–1274)" | the list is right. The unseen prior is §3 (L867); "half the learning rate" is a serrano result (`EXPERIMENT_QUEUE.md`), not in `v2_results_ynez.md` | W (citation) |
| 21 | §1.1 rerun noise: Charles149 pass@5 +3.7 [+1.2, +6.4]; "on 13–20 three components beat that control: +2.1 to +3.9 against +1.3" | ✔ values. Unlikeliness +2.1 [+1.0, +3.2] against control +1.3 [+0.2, +2.4] is not a resolved difference | W (minor) |
| 22 | §1.2 c005 904.3; resampling 17.6 → 26.0, 30 → 36; retry-EI all arms < 771; TTRL 1,020 / 1,079 / 1,088 | ✔ (Robbie reader, re-checked `combined-model` L113-120, L191-197; `combined-pipeline` L27-31) | R |
| 23 | §1.2 "proof state over whole proof … +111 to +178" | ✔ `state_recipes README.md:L103`, but those are raw medians. Robbie's compute-matched gaps are +46 to +156 and upper bounds (L106-108) | W (add the matched range) |
| 24 | §1.2 / §3.3 unpublished 3-hour GRPO runs: EI 852–929 vs GRPO 272–593 on dev1108 at k 16 | Robbie's HF `summary.json` files: `eval.old_dev` k 16, n 1,108; `RL_SECS` 10,800. EI v2 / v4 852–929, GRPO v3 / v4 272–593. The same-harness pair v4 is EI 925 / 859 against GRPO 276 / 272. EI v5 runs (993–1,020) are omitted, which strengthens the claim | R |
| 25 | §1.3 Dmitry selection table 0.405 / 0.540 / 0.567 / 0.582 / 0.594 | ✔ | R |
| 26 | **§1.3 / §3.4 "sampling to the first valid proof reaches the pool's ceiling of 0.653, using up to 64 attempts"** | Dmitry's `phase5.py:L3-9`: every stopping policy, the oracle included, sees **16 of the 64 attempts** ("N_max 16; R = 50 seeded orderings of the first 16 attempts"). 0.653 is the 3-generator mean of that 16-attempt oracle, at 7.2 attempts. The 64-attempt pool ceiling is 0.694 for s0. The paragraph also sets s0-only selection numbers against a 3-generator mean. The executor's own checker endorsed the 64-attempt reading (`report_check.md` item 11) | D: "up to 16 attempts (mean 7.2); the 64-attempt ceiling is 0.694 (s0)" |
| 27 | §1.3 REINFORCE +12.6 in distribution; textbook72 41.44 vs 41.67 | ✔ | R |
| 28 | §1.4 distract2 on our r8 s0: k 32, T 1.0, 48 steps, `nd_verify`; 25 crossing, 17 → 0; 0 / 120 generator; 118 / 120 with the block written by the environment | ✔ (R7; Charles reader) | R |
| 29 | §1.4 "0 of 320 samples on 21 hand-built elementary problems" | 0 / 320 covers the **four-premise** samples, 10 of the 21 problems. At 2 / 3 premises the same model verifies 154 / 160 and 111 / 128 | W |
| 30 | §1.4 block probability ≈ 4·10⁻²⁴ | ✔ (Charles `results.md:L116`). It depends on the naming convention; the robust evidence is 0 / 2,048 samples | R (caveat) |

### The comparison table (REPORT §2)

| # | row | my check (R11) | verdict |
|---|---|---|---|
| 31 | 1–3 (Leon recipe vs ours, plain and guided, textbook72 / Charles149), AA | same read-out: vendored code byte-identical, same files, caps, T, estimator. My R11 rows 1–4 agree | R |
| 32 | 4 (T0 17.2 vs frozen 15.2), AA | ✔ | R |
| 33 | 5 (T0 → EI r1 / r2 30.8 / 32.4; Charles149 24.8 vs our r8 39.2 / 31.8), "AA; similar level" | ✔ values. Ours is +6.8 (textbook72) and +7.0 (Charles149) higher, after 8 EI rounds against 2 | W: "ours higher at the point estimate, at 4× the rounds". Leon's single-seed EI_T0_r2 interval [23.4, 41.9] contains our 39.2 |
| 34 | 6 (S1g3 43.8 / 39.6 / 32.3 vs r16), AA | His Stage-1 read protocol is not stated in `RECIPE.md:L70-72` or `EXPERIMENT_QUEUE.md:L140`. Serrano's matching 41.8 is B 256; the RL reads are B 64 | W: AA not established |
| 35 | 7, 8 (T0S → EI; S1g3 → EI r2 s1 90.3 % = 65 / 72 at 64; our expected-at-64 48.4–58.5) | ✔ `tts_uplift_tables.md` L22, L24 | R |
| 36 | 9 (his GRPO − EI vs ours) | ✔ (intervals: see #3) | R |
| 37 | 10, 11 (Robbie), SP | ✔ | R |
| 38 | 12 (proof state vs whole proof) | ✔ the atlas has state ahead in all 8 dev / holdout cells (3.2M, Lean alone) | R |
| 39 | 13, 14 (Robbie's and Dmitry's reads of our r16 s0) | ✔ (R11 rows 13, 14) | R |
| 40 | 15 (Codex REINFORCE 41.44 vs 41.67 against our +3.7 from 8 more EI rounds), "NC; same direction" | the two moves are −0.2 and +3.7, not the same direction | W: drop "same direction" |
| 41 | 16 (Charles distract2) | ✔ | R |
| 42 | "Rows 4, 13 and 14 put the same model kind through both pipelines … therefore the gaps in rows 1–3 are differences between the models" | Rows 13 / 14 test Robbie's and Dmitry's harnesses on our model, not Leon's. The inference rests on row 4 and the code audit. That audit checks out: 19 of 21 vendored files are blob-identical to `origin/dan`, the other 2 are his provenance files, and all were last changed ≤ 2026-10-03, at or before the code of every compared read | R, with that correction |

### §3–§5

| # | claim | my check | verdict |
|---|---|---|---|
| 43 | §3.1 ladder table (17.2 · 30.8 / 32.4 (24.8) · 31.6 · 52.4 / 53.6 · 62.8 · 63.5 (54.4) / 68.1 (59.6) · 74.0 (70.5) / 68.4 (62.2)) | all ✔ at source | R |
| 44 | §3.1 cause 1 "T0 has 3 seeds, T0S 2" | T0's 17.2 is the 3-seed `stage1_stats` value. The +14.4 interval comes from OVERNIGHT's table, which says "2 seeds each" | W (minor) |
| 45 | §3.1 mechanism: frozen 48–56 % Lean-rejected (Leon T0 55.4 %), r8 11–17 %, 44–49 % env-rejected | ✔ same unit (share of all attempts) as Leon's | R |
| 46 | §3.1 cause 2 (+9.3; curriculum +0.1 / +2.0, +2.7 / +4.5) | ✔ `v2_results.md:L548-558` | R |
| 47 | §3.1 "ruled out": judge, files, settings, seed noise, compute per attempt, RL attempts (320k vs 1.15M) | Judge, files and settings ✔ (#8, #42). Seed noise holds even with shared-resample intervals. Compute per attempt is right as worded (his no-think arms 141–181 tokens vs our 211–235). His thinking arms spend ≈ 434–488 tokens per attempt on textbook72, ≈ 2× ours. These are the EI-lineage B64 arms in `tts_uplift_tables.md`; the final recipe's tokens per attempt are not tabulated. His no-think v2 arms are also far ahead (63.5 / 68.1, s0). 1.15M = 8 × 32 × 4,495 RL-target attempts ✔ (the ladder's 1.79M adds transfer and greedy reads) | R |
| 48 | §3.1 exposure: our clean62 42.9 → 38.5; his pools checked against Charles173 by renaming and curried class; ≤ 3.4 points of the Charles149 gap in its 5 four-premise problems | ✔. Unstated but symmetric: K12, the Stage-1 data of **both** sides, contains substitution instances of 14 Charles149 and 13 textbook72 theorems (R5) | R |
| 49 | §3.2 Robbie: 904 vs 1,054; 30 vs 52; cap 37.3 vs 51.7; judge 909 vs 281,817; 13 / 11 / 13 rounds in 2,192–2,298 s | ✔ (`numbers.md:L1542`; best-state; lean-judge README L86-101; combined-pipeline) | R |
| 50 | §3.3 GRPO vs EI across people, marked hypothesis | ✔ rows (#24; grpo-best sign tests p 0.0022 / 0.0002) | R |
| 51 | §3.4 the premise wall "is caused by the data" | The evidence is two things. First, no ≥ 4-premise prompt exists in K12 or the round-8 mix. Second, the environment-written-block diagnostic (Charles's re-implementation, judged by `nd_verify`), which locates the failure at the premise-listing step. No premise-pool Stage-1 has been trained | W: hypothesis, strongly suggested, untested |
| 52 | §4 "Never use redraws in training" | rests on serrano s0 arms (thinking and no-think), one seed each | W: "collapsed in his single-seed arms" |
| 53 | **§5 P1 "supported. 15 of 16 rows differ"** | The count compares their numbers with our **previously published** pass@256 counts ("as first reported"). P1 refers to "the rows in the comparison table". In the table as built, 11 of 16 rows are AA (1–9, 13, 14). Strictly, only rows 10, 11 and 16 differ in one of P1's four items (row 12 differs in models, row 15 in caps): 3 of 16. My table: 6–7 of 17 | D: **not supported as worded**. The "as first reported" reading is post hoc |
| 54 | §5 P2 "mixed" | ✔ 79 % / 61 % at pass@5. At k 64 (serrano v2 pairs, s0, not the final recipe): Charles149 +1 / −1 of 149 against +5.0 pp; textbook72 +2 / +3 of 72 against +4.7 / +7.7 pp. On 13–20, his primary set, the pass@1 gap is ≈ 0 and the test is vacuous | R |
| 55 | §5 P3 not testable; on reported numbers it would fail (62 and 66 of 72 at k 64) | ✔ `confusion_tb72.md:L13, L15` | R |
| 56 | §5 P4 "mixed" | ✔ (R10) | R |
| 57 | §5 P5 "supported … 0 of 25" | The prior's quantity is crossing problems that **stay** solved among those solved undistracted: 0 of 17. One seed, `nd_verify` judge | R (use 0 / 17) |

### Pre-registration and process

| # | claim | my check | verdict |
|---|---|---|---|
| 58 | Prereg "written 20:15 UTC … before reading the mentees' result documents (… branch names, commit subjects, and the first two paragraphs of Leon's [summary])" | The executor's own calls before the 20:15:15 write include `git show …/2026-10-05-thinking-traces/README.md \| head -80` (20:12:03). Those 80 lines contain the recipe paragraph, the 10-08 status and "What is settled so far". That section has "Most 'wildly OOD' axes (≥4 premises, …) fail on format", which bears on **P5**. Reader subagents launched 20:13:43–20:14:42 read Leon's summary and RECIPE in full before 20:15, but the first one completed at ≈ 20:29, after the commit, so they did not inform the priors. The brief already named "the premise-count wall" | W: the disclosure understates what was seen; P5 was partly informed |
| 59 | Addendum: "`podbudget` was not registered because nothing was spent" | `~/podbudget.log`: `2026-10-17T20:10:13Z peer-rl-review set HOURS=60 USD=30` (launcher). 0 used | D (trivial) |
| 60 | P3 cites "our MDD (6.5 theorems at cap 12, `NOISE_FLOOR.md`)" | 6.5 is `preregistration/best-state.md:71` (3 vs 4 seeds). `NOISE_FLOOR.md` has no textbook72 row | D (attribution) |
| 61 | Log times and STATUS DONE line | consistent with commit and file times spot-checked (20:44–20:50 inputs, 21:07 overlap, 21:10 GRPO pairs, 21:53 DONE) | R |
| 62 | Model labels on every number; judge labels across 2026-09-27 | every comparison names model, size, interface and judge. Robbie's Lean ∧ `nd_verify` and Charles's `nd_verify` are labelled where they enter | R |

## §Verdict

**Hard constraints:** all hold (R1). `nd_verify` is unmodified and unused, `TEST_RUN_DONE` is unchanged, no training,
no pods. **No quarantine.**

**What stands:**
- **The central result, re-derived exactly on stored files.** Under Leon's read-out protocol, his GRPO recipe is far
  ahead of ours:
  - textbook72 pass@1 74.0 vs 42.9 (r16);
  - Charles149 pass@1 70.5 vs 31.8 (r8);
  - guided reads 80.3 vs 50.7 and 77.4 vs 43.4.
- **The protocol is the same.** I confirmed it independently: 19 vendored files blob-identical to ours, identical
  textbook72 and Charles files, the same 24 removed names, and the same caps, T and estimator.
- **Every † point value** in `numbers.md` and the REPORT reproduces to one decimal. The bootstrap intervals beside them
  do not (#3).
- **Supporting checks reproduce:**
  - the exposure check: 10 textbook72 theorems with 400 target instances; 0 for Charles173;
  - the failure shares;
  - the premise-count facts;
  - P2 "mixed", P3 untestable, P4 "mixed" and P5 "supported" (with 0 / 17).
- **Lean.** 6,078 / 6,078 of the counted proofs behind these numbers pass my Lean re-check. My harness rejects every
  must-fail control. The single-flip controls accept only no-ops in the samples I inspected (C4′ / C4″); the 20 C4 and
  17 V3 acceptances themselves were not inspected one by one.
- **The gap is not GRPO against EI.** That is established by Leon's own EI baseline (68.4 / 62.2).
- **Peer facts.** The per-person summaries of Robbie, Dmitry and Charles are accurate, with the exceptions below.

**Must be reworded** (numbers are right, the sentence is not):
1. **P1.** Not supported on the comparison table as built: 11 of 16 rows are apples to apples. "As first reported" is
   a post-hoc criterion (#53).
2. **Dmitry's 0.653.** It is a 16-attempt, three-generator first-valid oracle at 7.2 attempts, not "up to 64
   attempts" or "the pool's ceiling". The ceiling at 64 is 0.694 for s0 (#26).
3. **"Most of the gap is Stage-1 data".** Attribute it to Leon's unreviewed ablations: 2–3 seeds before RL, single
   seeds after (#15). Mark row 6's AA as not established (#34). Rows 5 and 15 need the wording fixes in #33 and #40.
4. **Charles's wall "caused by the data".** A well-supported hypothesis, not tested by training (#51). "0 of 320
   samples on 21 problems" → on its 10 four-premise problems (#29). P5's denominator is 17, not 25 (#57).
5. **The pre-registration's disclosure.** The executor saw 80 lines of Leon's summary, including the ≥ 4-premise format
   observation, before writing P5 (#58). Also two trivial slips: the podbudget statement (#59) and the MDD source
   (#60).
6. **The bootstrap.** It understates theorem-level uncertainty against Leon's shared-resample method. The one
   "resolved" GRPO − EI difference (+4.5 [+0.5, +9.0] on the post-hoc `tb72_clean62`) is not resolved under it (#3,
   #4).
7. **The Summary's "Charles149 (clean for both sides)".** It is clean of renaming and curried overlap, but it is a
   KL-0 selection set for Leon (`RECIPE.md:L308-309`; the report says so in row 2 and §1.1). Also, K12, the Stage-1
   data of both sides, holds substitution instances of 14 of its theorems (#48).
8. **Minor:** redraw seed sets (#19); pilot citations (#20); unlikeliness vs the noise control (#21); Robbie's
   compute-matched interface range (#23); "never" for redraws (#52); "no RL gain" scoped to textbook72 (#17); T0 / T0S
   seed counts (#44).

**Not supported:**
- P1's "supported" (#53).
- The "up to 64 attempts" description of Dmitry's oracle (#26).
- Row 15's "same direction" (#40).

Nothing else in the report falls. A read-only adversarial check of this review (subagent, 23:16–23:40 UTC) found one
wrong number of mine (the Lean total, now 6,078) and the overstatements fixed above.

**Model labels and judges:** complete at section level. A few bullets (TTRL 1,020 / 1,079 / 1,088; GRPO 272–593)
inherit the model from their section header. Pre-2026-09-27 and `nd_verify`-judged numbers are labelled.

**Next measurements that would settle what is open:**
1. **The Stage-1 hypothesis on our side.** The report's own next step: regenerate K12's proofs with Leon's honest
   search, retrain Stage-1, and run the unchanged T1 ladder.
   - At least 5 seeds per arm.
   - Read pass@1 / pass@5 / pass@256, plain and guided, Lean alone.
   - Pre-registered against an MDD computed for pass@1 at that seed count. The best-state 6.5 is for pass@256
     counts.
2. **"Theirs on ours" and a creation test on Leon's recipe.** Needs his S1g3 / T0S and final L3 checkpoints (the
   `QUESTIONS.md` item). Then:
   - textbook72 and Charles149 at k 256, plain and guided;
   - base pass@k at large k on the theorems the recipe newly solves.
3. **Cheap, no GPU.** Re-score trajectory's stored pretraining-only reads on Leon's protocol. That gives the Stage-1
   pass@1 of the seeds behind r16, against which the r8 → r16 chain should be read.
4. **P5 under our own judge.** Our r8 on the distract2 set through our Lean-alone pipeline at k 256, T 0.8. The
   environment's `PR position` rule predicts 0 on every crossing problem; this would confirm it judge-independently.
