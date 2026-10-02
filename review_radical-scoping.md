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
