# Review — radical-scoping (reviewer, 2026-10-02)

Reviewer session, independent of the executor. Phase 1 was done blind in `~/review/radical-scoping`, a copy without
`run*.md`, `numbers.md`, `STATUS.md` or `log.md`. I did not open `log.md`, `radical_scoping/SCOPING.md`, `fol_pilot/README.md`'s
results, `*_summary*.txt`, `lean_summary_1000.txt`, `neg_control.txt`, `mut_agreement.txt` or `p2_move_counts_train.txt`
in phase 1. **Disclosure:** `git diff --stat origin/dan...HEAD` showed me the *names* `run_radical_scoping.md`, `numbers.md`,
`STATUS.md`, `log.md` (not their contents), and I read the `fol_pilot/README.md` command lines to reproduce the pool.

This run is desk scoping plus three CPU pilots: no model was trained or sampled, and no pod was used. So "per arm" here
means "per pilot". Every proof I count below is a **generator / hand-written proof, not a model proof**. No checkpoint
is involved, so no model label applies. P2 is the exception: it counts rule usage in the training sets of the `lean_seq`
3.2 M from-scratch Stage-1 models (labelled below).

Reviewer code and outputs: `review/radical-scoping-recount/` (`rv_fol.py`, `fol_stats.py`, `p2_counts.py`,
`seq_provers.py`, `p2_nec_recount.py`, `split_overlap.py`, `p3_nolemma.lean`, `out/`). Lean is `~/.elan/bin/lean` (Lean 4
core, no Mathlib), and I ran it on the VPS with at most 3 processes.

## §Recount (phase 1, blind)

### Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72…` at `HEAD` = `origin/main` ✔ |
| `artifacts/TEST_RUN_DONE` | no commit on the run branch touches it ✔ |
| eval file read in training code | no training code in this run (no model trained) ✔ n/a |
| `nd_verify` as a judge | not used to judge anything. One indirect use: `p2_necessity.py` calls `minlen.minlen`, which self-checks every proof it finds with `nd_verify` and returns `None` (which the summary would count as "requires") if the check fails. That path never fired: **0 `*_err` fields in all 216 searches** (mine and the executor's file). So `nd_verify` had no influence, but the label pipeline depends on it in principle. This is a minor finding, not a violation. |
| pods / spend | `podbudget`: 0.00 h, $0.00 of $3 ✔ |
| files outside the run's dirs | only `preregistration/`, `radical_scoping/` and the executor's write-ups ✔ |

No hard-constraint violation, so no quarantine.

### Pre-registration (gate 0)

`preregistration/radical-scoping.md` was committed in `77e1a795` ("pre-registration and run start"), before the P1/P2
commit `57f7407a` (16:58 UTC). Its falsifiable expectations are:

- P1: ≥ 90 % of the verifier-accepted rendered proofs are accepted by Lean, and the generator is revived in ≤ 1 h (falsified at 2 h).
- P2: proof by contradiction is used in 5–25 % of pretraining proofs and ORE in 1–10 %; filtering leaves ≥ 70 % of the set; and ≥ 1 held-out family *requires* the move.
- Ranking: knockout and FOL are the top two, and self-play conjecturing ranks last.

### P1 — FOL generator and Lean 4 core

- `fol/{core,verify,tokenizer,gen_data}.py` are **byte-identical** to `~/nd-rl/code/experiments/archived/nd_sprints_20260609_11/fol/`
  (nd-rl `95c046a`); the only addition is an empty `__init__.py`. They run on stdlib Python on the VPS: 1,000 theorems in 3.2 s.
- **Reproducibility:** re-running the README command gives a *different* pool (13 / 1,000 texts in common with
  `pool1k.jsonl`). The generator iterates over Python sets, so its output depends on `PYTHONHASHSEED`: with
  `PYTHONHASHSEED=0`, two runs are byte-identical (md5 `98cf36ed…`), and seed 1 gives a different pool. The committed
  `pool1k.jsonl` is therefore the record. Regenerating it needs the hash seed, which was not recorded. This is minor.
- **Lean check, own renderer** (`rv_fol.py`). It has its own tokenizer, parser and instance matcher, renders inlined
  term-mode proofs with explicit constructor names and type ascriptions, and puts only the occurring symbols in the
  context. It does not use `fol2lean.py` or the sprint verifier. Each theorem gets a unique name and a `#print axioms`
  line, with a sentinel after it, in chunks of 50.

| set | n | rendered | Lean accepts | Lean rejects | axioms |
|---|---|---|---|---|---|
| `pool1k.jsonl` (all, not a 200 sample) | 1,000 | 1,000 | **1,000 (100 %)** | 0 | none: 992; `propext, Classical.choice, Quot.sound`: 8 (the 8 DN proofs) |
| regenerated pool (`PYTHONHASHSEED=0`) | 1,000 | 1,000 | 1,000 | 0 | — |
| negative control: mutate one predicate letter in the statement and the final line only | 1,000 | 994 | 51 | **943** | — |

  All 51 accepted mutants are legitimately valid: the final line is ORI1 in 49 (a fresh disjunct) and BOTE in 2 (ex
  falso). So the checker discriminates.
- **What the pool contains** (my own parse; # proofs using each rule, n = 1,000). IMPI 514, EXI 412, ANDI 378, ALLI 329,
  ORI2 202, ORI1 197, ALLE 145, ANDE2 61, ANDE1 56, IMPE 50, R 37, BOTE 19, NEGI 15, DN 8, NEGE 3, and **ORE 0, EXE 0**.
  731 proofs use a quantifier rule. The 329 proofs that use ALLI contain 358 ALLI lines. All 358 generalise a constant
  eigen-parameter, and none uses the bound-variable-as-parameter case (which the sprint verifier does not check for freshness).

  The generator's rule list (`core.py:436`) has **no ORE and no EXE** at all: it never emits ∨-elimination or
  ∃-elimination. The pool is also shallow: lines have quartiles 3 / 4 / 5 (max 16), and my inlined term size (rule
  nodes, PR/AS leaves = 1) has quartiles 3 / 4 / 5 (max 12, mean 4.3).

  For scoping this matters: the quantifier rules that need an eigen-parameter search (EXE) are absent, ALLE / EXI term
  choice is present, and the data are far shorter than the propositional pools.
- Verdict on the P1 expectation: **met**. Lean accepted 100 % ≥ 90 %, the generator ran unmodified, and no fixes were needed.

### P2 — skill-knockout feasibility

**Rule usage** (`p2_counts.py`, my own line parser over the `proof` text; `rules` field mismatches = 0). Per-proof
usage, % of proofs, and % left after filtering:

| rule / move | `data/p2/train_depth3_f0_a1.jsonl` (155,000; the Stage-1 set of the `lean_seq` 3.2 M from-scratch cap-6 models per `FAST_STAGE1.md` / `STATE_ENV.md`) | `data/train.jsonl` (154,990; original cap-6 set) |
|---|---|---|
| ORE | 2,256 = 1.46 % (left 98.54 %) | 2,277 = 1.47 % (98.53 %) |
| DN | 12,905 = 8.33 % (91.67 %) | 12,950 = 8.36 % (91.64 %) |
| classical reductio (DN applied to a NEGI line) | 10,547 = 6.80 % | 10,554 = 6.81 % |
| NEGI | 9.93 % | 10.37 % |
| any of NEGI / DN / BOTE | 13.35 % | 13.76 % |
| BOTE | 1.95 % | 1.90 % |
| ORE and DN in the same proof | 51 | 47 |

Pre-registered ranges: ORE 1–10 % ✔ (1.46 %), contradiction 5–25 % ✔ (DN 8.3 %, reductio 6.8 %, any 13.4 %), and ≥ 70 %
left ✔ (91.7 % / 98.5 %). The two sets agree within 0.5 pt, so whichever one the executor counted, the conclusion is the
same. Phase 2 checks which set they named.

In the `lean_seq` grammar the knockout is clean: `Or.elim` is the only ∨ eliminator and `Classical.byContradiction` the
only classical constant (`lean_tok.py`). Free-form Lean also has `Or.casesOn`, `Or.rec`, `Or.resolve_*`, `Classical.em`
and `Decidable.em` (`lean_check.py`), so a free-form knockout would have to block all of them.

**Which textbook72 targets require the move.** I re-ran `p2_necessity.py data/bs/textbook72.jsonl 12 20` and got output
**identical row for row** to the committed `p2_necessity_textbook72.jsonl` (0 / 72 rows differ). I then summarised it
with my own code and compared it with **exact, unbounded labels** from my own decision procedures (`seq_provers.py`):
classical G3c with and without L∨ for "needs ORE" (ND without OrE ≈ G3c + cut without L∨, and cut elimination adds no
L∨), and intuitionistic G4ip for "needs DN" (classically valid, not intuitionistically). Both pass 10 hand-labelled
unit cases.

| | bounded (minlen, bound 12, 20 s): requires / not needed / costlier / unknown | exact: needs |
|---|---|---|
| ORE | 14 / 37 / 0 / 21 (21 = full search failed; 6 of them timed out) | **21** |
| DN | 9 / 40 / 2 / 21 | **19** |
| both | 1 | 4 |

All 72 are classically valid. On the 51 problems where the full search succeeded, **the bounded label agrees with the
exact label in every case** (ORE: 14 requires = 14 exact-needs, 37 not = 37 exact-not; DN: 9 = 9, 42 = 42). The 21
"unknown" problems contain 7 more ORE-needing targets and 10 more DN-needing ones. So "≥ 1 family provably requires the
move" holds with margin, and the exact labels need no search bound.

**Renaming-class overlap** of textbook72 with training (`split_overlap.py`, order-free premise key):
`train_depth3_f0_a1` 0 / 72, and `data/train.jsonl` 1 / 72.

### P3 — induction / lemma probe (`ind_pilot/ind.lean`)

- The file checks as claimed. `z_add`, `s_add`, `add_comm` and `add_assoc` elaborate, `#print axioms` shows no axioms,
  and the three trivialisers on `add_comm` (`simp [add]`, `omega`, `decide`) fail.
- **Reviewer extension** (`p3_nolemma.lean`). Two findings:
  1. `add_comm` is provable as **one theorem with nested `induction` and no auxiliary theorem or `have`** (Lean accepts,
     no axioms). The file's comment "lemma invention is necessary: no direct induction works without them" is true only of
     a *single, un-nested* induction. The helper facts can be proved inline.
  2. `induction n <;> simp_all [add]` **proves both helper lemmas** `z_add` and `s_add` outright, though not `add_comm`.
     So "trivialisers fail" holds for `add_comm` but not for the lemmas a library-learning pilot would need the model to find.

### Lean re-check count

| pilot | proofs re-checked in Lean by me | rejected |
|---|---|---|
| P1 FOL (generator proofs) | 1,000 committed + 1,000 regenerated | 0 |
| P3 induction (hand-written by the executor, as a feasibility probe, not training data) | 4 theorems + my 1 | 0 |
| P2 | no proofs counted (labels only) | — |

## §Compare (phase 2)

Read after the phase-1 commit `5e826fb4`: `run_radical_scoping.md`, `numbers.md` § radical-scoping, `STATUS.md`,
`radical_scoping/SCOPING.md` and the pilot summary files. I also re-ran `neg_control.py` and `mut_agreement.py`; both print
to stdout and leave the committed files untouched.

| claim (where) | my independent value | verdict |
|---|---|---|
| Sprint FOL generator and verifier run unchanged, stdlib, 1,000 theorems in 3 s (SCOPING §B, numbers) | byte-identical to nd-rl archive; 3.2 s | reproduces |
| pool: mean 4.25 lines, 731 / 1,000 with a quantifier, no EXE (numbers) | 4.252; 731; EXE 0 | reproduces. **Also ORE 0, not stated.** The sampler's rule list (`core.py:436`) has neither ORE nor EXE, so "no ∃-elim, which matches the sprint's under-sampling" should read "the sampler *cannot* emit ∃-elim or ∨-elim". |
| Lean 4 core accepts 1,000 / 1,000 (`fol2lean.py`) | my independent renderer: 1,000 / 1,000, plus 1,000 / 1,000 on a regenerated pool; 943 / 994 of my own mutants rejected, and the 51 accepted are valid (ORI1 / BOTE) | reproduces |
| controls: 231 / 231 conclusion swaps, 41 / 41 eigenvariable clashes rejected; 578 one-line mutants, 577 agree (24 + 553), 1 verifier-reject / Lean-accept | re-run: identical. The one disagreement generalises `e`, which occurs in a premise only inside a conjunct the cited line discards; Lean is right to accept. | reproduces. "a premise constant that the cited line does not depend on" is loosely worded: the line depends on the premise but not on its `e`-part. |
| "All 272 mutants are rejected" (run md) | 272 = the two control families; the 578-mutant set has 24 valid mutants that both accept | reproduces, but the sentence is ambiguous next to the 578 |
| P2: ORE 2,277 (1.47 %), BOTE 2,951, DN 12,950 (8.36 %), NEGI 16,068 in `data/train.jsonl` (154,990) | identical | reproduces |
| `data/train.jsonl` is "the cap-6 Stage-1 set … source of the cap-6 `lean_seq` / `lean_staten` training sets" (numbers, SCOPING §A) | The `lean_seq` 3.2 M models (`FAST_STAGE1.md`) and the **9.56 M best-cap6 `lean_staten` model** that pilot A proposes to retrain (best-state summary) were trained on `data/p2/train_depth3_f0_a1.jsonl` (155,000), not `data/train.jsonl`. On that set: ORE 1.46 %, DN 8.33 %. | **mislabelled set**. The numbers move ≤ 0.05 pt and the conclusion stands, but pilot A must filter `train_depth3_f0_a1` and should quote its counts. |
| textbook72: 51 / 72 found within bound 12; 14 require ORE, 9 require DN, 1 both; 2 costlier | re-run identical (0 / 72 rows differ); own summary identical | reproduces |
| "The other 21 have no proof within the bound" | 15 have no proof in the search space; **6 timed out** | reword: "no proof found (6 timeouts)" |
| "a required pool exists" (14 ORE-required problems) | exact, unbounded labels: **21 / 72 need ORE, 19 / 72 need DN, 4 both**. All 14 + 9 bounded labels agree with the exact ones, with 0 disagreements on the 51 decided problems. | stands, and is stronger than written: the labels need no search bound (G3c − L∨ / G4ip) |
| `Or.elim` and `Classical.byContradiction` are single tokens, so the knockout is a filter | true in the `lean_seq` grammar. Free-form Lean also has `Or.casesOn` / `Or.rec` / `Or.resolve_*` / `Classical.em` / `Decidable.em` on `lean_check`'s allowlist. | stands for `lean_seq` / `lean_staten`; add the free-form caveat |
| P3: `z_add`, `s_add`, `add_comm`, `add_assoc` check with no axioms; `simp [add]`, `omega`, `decide` fail on `add_comm` | identical | reproduces |
| "so the core library cannot trivialise the domain" (SCOPING §C) | `induction n <;> simp_all [add]` proves `z_add` and `s_add` outright; it fails only on `add_comm` | **overstated**. The trivialisers fail on `add_comm`, not on the base lemmas. A tactic grammar for C must exclude `simp_all` (or `simp` with the definition), or the L0 / L1 lemma families can be closed by automation. |
| "add_comm has no direct inductive proof without [the two lemmas], or a nested induction" (§C); `ind.lean` comment "lemma invention is necessary" | a one-theorem nested-induction proof with no auxiliary statement checks | SCOPING's wording ("or a nested induction") stands. The comment in `ind.lean` is false as written: a lemma statement is not necessary. C's falsifier already counts nested induction as a non-lemma solve, which is consistent. |
| "minlen's complete search relies on [the subformula property]" (SCOPING, organising observation) | `minlen.py`'s own docstring: the space is *restricted* to S, and "None is NOT a proof that no ≤ bound-line proof exists" | **wrong word**: minlen is not complete. The subformula property holds for *normal* proofs, not for every shortest proof. So "every proof our RL finds is a re-ordering of objects already in the prompt" is an overstatement: it holds for normal proofs; Lean `have`s can introduce non-subformulas. |
| "A never-seen action cannot be sampled, so a non-zero solve rate is creation by construction" / "K0: 0 required solves (structural)" (§A) | Not measured here. A softmax LM gives the never-targeted `Or.elim` token a small but **non-zero** probability, because the token stays in the vocabulary. And K0+ε injects `Or.elim` through a hand-designed operator. | **reword**. The null is near-structural, not structural, so measure it: report the frozen K0 model's `Or.elim` log p at legal positions and its pass@N on the required pool at equal attempts. "Creation by construction" is also too strong for K0+ε: what it tests is whether RL can *adopt* a move that a non-learned proposer supplies. That is a legitimate question, but it is not unaided creation. |
| exact-permutation p: 3 v 3 ≥ 0.05, 5 v 5 = 0.004 | 1 / C(6,3) = 0.05; 1 / C(10,5) = 0.00397 | reproduces |
| costs: A40 $0.49/h; Stage-1 1,200 A40-s ≈ $0.16; pilot A ≈ $15 | best-state summary: 1,200 s on one A40, $0.49/h → $0.163; 6 × 0.16 + 6 × ≈ $2 ≈ $13 | reproduces (the ≈ $2 per half-ladder and "$3–4 per 8-round ladder" are inherited and I did not trace them) |
| `trajectory`: worst step −6.2 → −1.3 nats (best-cap12, 9.56 M `lean_staten`, 3 seeds); −15 nats total | summary: w1 r0 −6.21, r8 −1.29; total −15.3 | reproduces, labelled |
| "The 25 textbook72 problems that no checkpoint solves stay put" (in the `trajectory` bullet) | The 25 unsolved come from the `textbook72` run on **SN-cap12 T1 (3.2 M `lean_staten`)**, not best-cap12. | **model label missing / wrong**: name the model |
| prior knockouts: "`round2-run5`: reductio stays 0/300 at f = 0" | round2-run5 summary: s1 and s2 are 0/300, but **s0 ignites to 0.170 by round 4** | **cherry-picked**: 2 of 3 draws. All of round2-run2/5 are token-format, `nd_verify`-era numbers, and the checker is not named. |
| `round2-run2` 0 of 6 patterns; `run4-grpo-review` 67–71 % vacuous box | not traced in the time I spent | not checked |
| "The sprint's FOL was easy (pass@8 ≈ 0.94–0.96)" | sprint summary: 0.94 / 0.96 (eigenvariable vs not), 0.953 / 0.955 | value traces. **The model is unlabelled** (June sprint FOL model, sprint verifier, not Lean). |
| `frontier-supply` "+7.5, inside the MDD" | summary: +7.5 of 291, MDD 10.5 | reproduces; model unlabelled in SCOPING |
| LILO / Stitch / LEGO-Prover not in `references.bib`; EDL key present | nd-rl `references.bib`: 0 hits; `donoway2026…` present | reproduces |
| SCOPING ≤ 2,500 words, run md ≤ 200 | 2,500 / 200 (`wc -w`) | meets the limit exactly |
| "Every pre-registered expectation held … ranking as predicted" | P1 ≥ 90 % ✔ (100 %); P2 ranges ✔; required family ✔; ranking: knockout 1, FOL 2, self-play last ✔ | reproduces. The expectations were committed in `77e1a795`, before the pilot commit. |
| $0 pod spend; bucket `hf://…/radical-scoping/radical_scoping` | `podbudget` 0.00 h / $0; bucket listing has all files | reproduces |

Gate 0: pre-registration committed before results ✔. No misses to report: every expectation held. The ranges were wide,
which makes "every expectation held" weak evidence, though it is not wrong.

## §Verdict

**No hard-constraint violation.** `nd_verify` is unmodified and judged nothing. Its only path into a label (minlen's
self-check) never fired. `TEST_RUN_DONE` is untouched, there was no training, and $0 was spent.

**What stands.**
- **Every pilot number reproduces**, from my own code or an identical re-run. That covers the FOL Lean acceptance and
  controls, the rule counts, the bounded necessity labels and the induction file.
- P1's core feasibility claim is well supported: Lean 4 core checks the sprint's FOL proofs, and an independent second
  renderer agrees 1,000 / 1,000.
- P2's feasibility is **stronger than written**. Exact sequent-calculus labels show 21 / 72 textbook72 problems need ORE
  and 19 / 72 need DN, with no search bound and 0 disagreements against the executor's bounded labels.
- The ranking matches the pre-registration.

**What must be reworded.**
1. The P2 counts name the wrong training set. Pilot A's model (best-cap6, 9.56 M `lean_staten`) was trained on
   `data/p2/train_depth3_f0_a1.jsonl` (ORE 1.46 %), not `data/train.jsonl`. The numbers barely move, but the filter
   must be applied to the right file.
2. §A's "never-seen action cannot be sampled … creation by construction" and "K0 = 0 (structural)":
   - The probability is near zero, not zero. Measure the K0 base's `Or.elim` log p and its pass@N at equal attempts.
   - K0+ε tests whether RL adopts a move supplied by a hand-built proposer, not unaided creation.
3. The organising paragraph: minlen's search is not complete (its own docstring), and the subformula property holds
   for normal proofs, not for every proof RL finds.
4. §C: "the core library cannot trivialise the domain" — `induction <;> simp_all [add]` proves the helper lemmas.
   Restrict the tactic grammar. Separately, the comment in `ind.lean`, "lemma invention is necessary", is false:
   nested induction proves `add_comm` with no lemma.
5. §B gaps: the FOL sampler cannot emit **∃-elim or ∨-elim** at all. This is structural, not under-sampling, and the
   missing ORE is not mentioned.
6. Inherited evidence:
   - "round2-run5: reductio stays 0/300" holds for 2 of 3 draws (s0 ignited).
   - "25 textbook72 problems no checkpoint solves" belongs to SN-cap12 3.2 M, not the best-cap12 model it sits beside.
   - The sprint pass@8 and frontier-supply numbers lack model labels.
   - Pre-2026-09-27 numbers lack their checker.
7. "The other 21 have no proof within the bound" — 6 of the 21 timed out.

**Not supported.** Nothing central. The recommendation (A, then B) is a judgment call that the pilots make feasible,
not one they test. The claim closest to unsupported is A's "structural null", which is the premise of the
recommended pilot.

**Minor.**
- `pool1k.jsonl` cannot be regenerated byte-for-byte (`PYTHONHASHSEED` was not recorded), though the committed file
  makes every count reproducible.
- No compute rows were recorded. None are needed: no GPU was used, and the Lean checks took seconds.

**Next measurement that would settle what is open** (≈ $1, before pilot A's ≈ $15):
- Train one ORE-free best-cap6 Stage-1 (filter `train_depth3_f0_a1`, 1,200 A40-s ≈ $0.16).
- Report the frozen model's `Or.elim` probability at every legal position, and its pass@4,096 on the 21 exact-ORE
  textbook72 problems plus a `necessity.py` ORE-required pool.
- If the pass rate is > 0, the K0 null is not structural and pilot A needs a frozen-at-equal-attempts comparison
  rather than a "0 vs > 0" design.

For B, before any GPU spend: probe on CPU whether adding EXE / ORE / function symbols to the sprint generator yields
≥ 1 % multi-instance proofs.
