# Review of run `proof-strategies` (reviewer, 2026-10-18)

Reviewer: agent:claude (role reviewer, a session separate from the executor). Run brief: nd-rl
`docs/proposals/claude-heavy/BRIEF_proof-strategies.md` (proposal 28). Pre-registration:
`preregistration/proof-strategies.md` (committed a30bc33b). Branch `dan_proof-strategies` at 441de472. Kit: `review_ps/`
(every number below is printed by a script there into `review_ps/out/`; the phase-2 ad hoc numbers by `phase2_numbers.py`; nothing is hand-summed).

**Model labels.** The run trains and samples no model. Every number in §Recount is a property of a data file or of
proofs found by a bounded search (`minlen.Search`), except §R12. That section counts proofs that create-or-elicit's
models wrote: its 9.56 M ALiBiGPT `lean_staten` policies, trained from scratch on K12 (full), K12⁻ (knockout) or K12⁻ + 1 % σ
(dose1), then run through 16 rounds of T1 expert iteration (A40), judged by Lean alone. Round 1 is samples of the pretrained model.

**Checker.** All Lean checks below use the reviewer's own harness (`review_ps/lean.py`): Lean 4.34.0 core with no imports.
A proof is accepted iff its theorem line has no error and `#print axioms` lists only {propext, Classical.choice,
Quot.sound}. ND proofs are rendered with my own ND→Lean renderer. `nd_verify` judges nothing here.

**Summary (written after phase 2, corrected after an adversarial check of this review).**
- **Every count recomputed from the labels reproduces.** That covers the run's numbers, tables, examples and RL counts:
  my blind re-implementation agrees with the classifier on every record of every set, and every Lean check passes in my
  own harness. The exceptions are labelling and definitional issues (§Verdict), plus two TABLES cells that rest on a
  different convention (textbook72 "decided" 54 vs 53; v0 modus tollens 64 vs 71).
- **No hard-constraint violation.**
- **Two definitional statements are wrong as stated:**
  - "No K12 theorem is σ-covered." This holds only when ¬X → ⊥ counts as a double negation. The pre-registration and
    create-or-elicit both define σ-covered by a syntactic ¬¬ test, under which K12 has 2,340. This is an unflagged
    deviation.
  - "Every proof of a σ-covered theorem needs a working reductio (#10)." In rounds 1–16 at least 573 Lean-accepted RL
    proofs of σ-covered targets eliminate a self-built ¬¬ through a box hypothesis (∨E case or →I "lemma route"). None
    of them gets a #10 label: 491 in one dose ladder, none in knockout ladders. Target-level results do not change;
    per-proof reductio counts would rise under a fixed #10.
- **The validation needs its version label.** "Blind spot-check 260 / 260" was against v1.1; the final DS and LEM
  rules were never blind-checked.
- **Smaller items.** A false "No models" header in TABLES, an inverted caption, three over-general example glosses, the
  blog's silence on RL-time replay of pretraining data, and a test-fixture file with three textbook72-class sequents
  that is also in the public bucket. Also, RL expectations were written a minute after the executor printed related
  create-or-elicit counts. None changes a reported number. Details in §Verdict.

## §Recount (phase 1, committed before I read `run_proof_strategies.md`, `numbers.md`, `log.md`, `TABLES.md`, `blog.md`, `EXPECTATIONS.md` or `EXAMPLES.md`)

**Independence.** I implemented the predicates from the pre-registration's v0 table and from `TAXONOMY.md` §1–§5. I
printed those sections with every percentage and large number masked; the numbered validation and limits sections
(§6–§7) I left for phase 2. I did not read `proof_strategies/strategies.py` or `test_strategies.py`. I read executor code
in four places only, each to learn *what* was computed, not how: `run_all.sh` (which file was classified with which
field), `rl_found.py` (the per-round quantities), `examples.py` (the selection rule for "shortest clean"), and
`search_proofs.py` / `minlen.py` (how the search bypasses `nd_verify`). I did look at the raw artefacts:
`artifacts/ps/labels/`, `theorem/`, `rl_found.json`, `summary/k12_v0.json`, `validation/spot_compare*.json` and the
pod logs.

### R1. Inputs

| set | file | records | hash (mine) | pre-registered |
|---|---|---:|---|---|
| K12 | `data/ps/in/train_k12.jsonl.gz` | 155,000 | uncompressed md5 800b5486ba37… | 800b5486… ✓ |
| cap-6 | `train_depth3_f0_a1.jsonl.gz` | 155,000 | uncompressed md5 29276f24e771… | 29276f24… ✓ |
| K12⁻ | `train_k12ko.jsonl.gz` | 155,000 | gz md5 6326ebddf560… | 6326ebdd… ✓ |
| K12⁻ + 1 % σ (dose1) | `train_k12dose1.jsonl.gz` | 155,000 | gz md5 7433f6ac0564… | (README) ✓ |
| RL targets / transfer / holdout250 | `data/ladder/`, `data/bs/` | 4,495 / 2,285 / 250 (3,735 / 1,525 / 160 with a generator proof) | | as pre-registered ✓ |
| Charles's release (private) | `data/ps/in/charles/charles_base_full.jsonl` (nd-rl 297dcbdd) | 187 base problems | | 187 ✓ |
| textbook72 (sealed) | `data/bs/textbook72.jsonl` | 72 (58 with a search proof) | | ✓ |

My own ND rule checker (`nd.py`, written from `spec.md`, used as a sanity check only) accepts every proof that was
classified in every set. That is 155,000 × 4 + 3,735 + 1,525 + 160 + 187 + 990 + 1,610 + 58 proofs.

### R2. The classifier, re-implemented blind (`cls.py`) — per-record agreement

My classifier implements all 13 strategies, the working / genuine flags, every sub-type, the root primary and the curried
primary. I compared it record by record with the executor's `artifacts/ps/labels/<set>.jsonl.gz` (`cmp.py`):

| set | records compared | uses (13) | working (#3, #5, #7, #10) | primary | curried primary | box-free | every sub-type |
|---|---:|---|---|---|---|---|---|
| K12 | 155,000 | identical | identical | identical | identical | identical | identical |
| cap-6, K12⁻, dose1 | 155,000 each | identical | identical | identical | identical | identical | identical |
| rl_targets_gen / transfer_gen / holdout250_gen | 3,735 / 1,525 / 160 | identical | identical | identical | identical | identical | identical |
| Charles base, k12_min990, tb_schema search, textbook72 search | 187 / 990 / 1,610 / 58 | identical | identical | identical | identical | identical | identical |

The rows without a proof (760, 760, 90 schema rows; 14 textbook72 theorems with no search proof) are skipped on both
sides. The second implementer's final per-record output (`validation/second_impl_v1.2final_k12.jsonl.gz`) is also
identical to mine on all 155,000 K12 records: uses, primary, and the →I / ∨E working flags. That makes three
implementations that agree on every record. The pre-registered consistency check holds: σ (DN citing, after R, a NEGI
line; pruned = written) = **16,703**; σ strict = 16,703; σ⁺ (DN citing a line that is not PR / AS) = **16,961**; σ⁺ =
#10 ∪ #11 `on_derived` with 0 records differing, in every set. The numbers carried in from create-or-elicit reproduce:
K12 DN anywhere 21,274 (13.73 %), NEGI anywhere 15.21 %; K12⁻ DN 3.29 %, NEGI 5.19 %. The unlabelled share is 0 in every
set (root and curried). **No record in any set has a dead line**: written = pruned everywhere, so "only in dead lines" is
0 %.

### R3. K12 (155,000 generator proofs, pruned)

| # | strategy | uses | uses % | working % | primary % | curried primary % |
|---|---|---:|---:|---:|---:|---:|
| 1 | direct | 79,284 | 51.15 | – | 9.71 | 15.29 |
| 2 | and_intro | 50,484 | 32.57 | – | 12.24 | 19.38 |
| 3 | cond_proof | 66,567 | 42.95 | 20.80 | 37.65 | 0.00 |
| 4 | or_intro | 68,606 | 44.26 | – | 14.08 | 20.50 |
| 5 | cases | 68,453 | 44.16 | 8.79 | 20.85 | 33.41 |
| 6 | disj_syll | 43 | 0.03 | – | 0.01 | 0.02 |
| 7 | neg_intro | 7,354 | 4.74 | 2.15 | 1.94 | 2.69 |
| 8 | mod_tollens | 76 | 0.05 | – | 0.04 | 0.04 |
| 9 | ex_falso | 12,455 | 8.04 | – | 0.52 | 1.58 |
| 10 | contradiction | 16,717 | 10.79 | 0.04 | 2.91 | 3.50 |
| 11 | dne | 4,743 | 3.06 | – | 0.05 | 0.33 |
| 12 | lem | 47 | 0.03 | – | 0.00 | 0.00 |
| 13 | lemma_reuse | 18,147 | 11.71 | – | 0.00 | 0.00 |
| – | trivial | – | – | – | 0.00 | 3.26 |
| – | box-free (no AS line) | 38,617 | 24.91 | | | |

The "uses" percentages here count a strategy anywhere in the proof. Sub-types (proof level, `out/summary_all.json`):
- →I: vacuous 28.20 %, working 20.80 %.
- ∨E: genuine 8.79 %, redundant 37.64 %, X ∨ X merges 2.14 %; nested ∨E: 0 records.
- #10, one kind per instance (a proof may hold several instances): vacuous 5.30 %, scaffolded 4.96 %, pointless 0.70 %,
  neg_goal 0.03 % (48 records), free 0.004 % (6). Template 10.75 %, working **59 records** (0.04 %).
- #11: on a hypothesis 2.10 %, on a premise 0.80 %, on a derived line 0.17 %.
- Ex falso from inconsistent premises: 6.23 %.

### R4. All sets (uses %, pruned proofs)

| strategy (uses %) | k12 (155,000) | cap6 (155,000) | k12ko (155,000) | k12dose1 (155,000) | rl_targets_gen (3,735) | transfer_gen (1,525) | holdout250_gen (160) | charles_base (187) | k12_min990 (990) | tb_schema_search (1,610) | textbook72_search (58) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| direct | 51.15 | 44.52 | 50.89 | 50.89 | 37.70 | 45.25 | 36.88 | 84.49 | 45.35 | 77.08 | 65.52 |
| and_intro | 32.57 | 22.93 | 33.40 | 33.33 | 40.91 | 52.26 | 60.62 | 47.59 | 24.75 | 37.14 | 31.03 |
| cond_proof | 42.95 | 36.35 | 48.02 | 47.54 | 97.00 | 95.41 | 93.75 | 52.41 | 39.80 | 42.86 | 44.83 |
| or_intro | 44.26 | 39.63 | 46.39 | 46.23 | 37.99 | 36.00 | 38.75 | 31.02 | 34.04 | 45.96 | 41.38 |
| cases | 44.16 | 1.46 | 46.96 | 46.71 | 41.85 | 44.59 | 43.75 | 33.69 | 6.06 | 38.26 | 27.59 |
| disj_syll | 0.03 | 0.00 | 0.03 | 0.03 | 0.35 | 0.79 | 0.00 | 14.44 | 0.20 | 5.59 | 6.90 |
| neg_intro | 4.74 | 3.13 | 5.19 | 5.15 | 6.43 | 10.30 | 13.75 | 37.97 | 1.21 | 39.57 | 32.76 |
| mod_tollens | 0.05 | 0.08 | 0.05 | 0.05 | 0.19 | 0.26 | 0.00 | 11.76 | 0.00 | 10.43 | 3.45 |
| ex_falso | 8.04 | 1.95 | 9.30 | 9.17 | 10.58 | 9.90 | 8.12 | 24.06 | 20.51 | 17.58 | 12.07 |
| contradiction | 10.79 | 6.81 | 0.00 | 1.00 | 3.48 | 5.05 | 5.62 | 20.86 | 2.22 | 20.75 | 17.24 |
| dne | 3.06 | 1.53 | 3.29 | 3.25 | 14.65 | 13.77 | 15.00 | 3.21 | 3.94 | 1.06 | 5.17 |
| lem | 0.03 | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.34 | 1.72 |
| lemma_reuse | 11.71 | 2.26 | 12.46 | 12.39 | 12.07 | 11.34 | 10.00 | 16.04 | 2.32 | 8.88 | 5.17 |
| working #10 | 0.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | 0.00 | 20.86 | 0.10 | 20.75 | 17.24 |
| primary #10 | 2.91 | 6.36 | 0.00 | 0.26 | 0.00 | 0.07 | 0.00 | 6.95 | 0.81 | 13.29 | 13.79 |
| vacuous →I (sub-type) | 28.20 | 24.41 | 31.50 | 31.18 | 88.73 | 89.77 | 84.38 | 10.70 | 22.83 | 5.78 | 10.34 |
| box-free | 24.91 | 53.16 | 25.84 | 25.75 | 0.03 | 0.00 | 0.00 | 11.76 | 53.43 | 0.56 | 12.07 |

### R5. Theorem level, my own G4ip (`ipc.py`, Dyckhoff's LJT) and truth tables, on every theorem of every set (no sampling)

| set | n | classical-only | dneg (semantic) | σ-covered (semantic dneg) | σ-covered (syntactic ¬¬ only) | inconsistent premises |
|---|---:|---:|---:|---:|---:|---:|
| k12 | 155,000 | 6,238 (4.02 %) | 45,630 (29.44 %) | 0 | 2,340 | 36,472 (23.53 %) |
| cap6 | 155,000 | 5,209 (3.36 %) | 38,339 (24.73 %) | 1 | 2,235 | 25,933 (16.73 %) |
| k12ko | 155,000 | 2,094 (1.35 %) | 41,879 (27.02 %) | 0 | 0 | 33,096 (21.35 %) |
| k12dose1 | 155,000 | 2,471 (1.59 %) | 42,217 (27.24 %) | 0 | 232 | 33,389 (21.54 %) |
| rl_targets | 4,495 | 325 (7.23 %) | 2,471 (54.97 %) | 123 | 123 | 216 (4.81 %) |
| transfer | 2,285 | 195 (8.53 %) | 1,096 (47.96 %) | 106 | 106 | 125 (5.47 %) |
| holdout250 | 250 | 25 (10.00 %) | 125 (50.00 %) | 12 | 12 | 12 (4.80 %) |
| charles_base | 187 | 42 (22.46 %) | 11 (5.88 %) | 35 | 35 | 9 (4.81 %) |
| textbook72 | 72 | 19 (26.39 %) | 6 (8.33 %) | 16 | 16 | 7 (9.72 %) |
| tb_schema | 1,610 | 274 (17.02 %) | 244 (15.16 %) | 240 | 240 | 91 (5.65 %) |

**Self-check.** No theorem with a DN-free generator proof was judged intuitionistically unprovable, and every theorem
is classically valid. That holds for all 4 × 155,000 + pool theorems, 0 exceptions, and is a completeness check on my
prover. My prover also passes 25 hand-picked sequents (LEM, Peirce, DNE, De Morgan, MT, …). Per record, my classical-only,
semantic-dneg, σ-covered and inconsistent-premises labels are **identical** to the executor's `artifacts/ps/theorem/*.jsonl.gz`
for all ten sets.
- E6: of the 16,717 K12 records using #10, **4,279 (25.60 %)** are classical-only theorems. Of the 6,238 classical-only K12
  theorems, **4,279 (68.60 %)** use #10 and 1,959 use #11 alone. None of the 59 working-#10 records is classical-only.
- **Definition note.** K12's σ-covered count is 0 only under the run's *semantic* dneg, which counts (¬X → ⊥) as a double
  negation. create-or-elicit's strict rule (no `( ~ ( ~` subformula; `coe/coe_rounds.py`) is syntactic. Under it K12 has
  **2,340** σ-covered theorems (1.51 %), cap-6 2,235, dose1 232. All 2,340 in K12 carry a (¬X → ⊥) subformula, which is
  ¬¬X in Lean. The pools, Charles and textbook72 are unaffected (the two definitions agree there).

### R6. Bounded necessity (`data/ps/nec/*.checked.jsonl`)

I recomputed `requires X` from the stored search fields: a free proof ≤ 12 lines was found, the ban search found none,
and it did not time out. The result is identical to the stored flags in all three sets (0 mismatches). K12 sample (594 =
54 per length 2–12): ORE 36, NEGI 22, BOTE 0, DN 32. Charles (124 of 187 with a free proof; 58 none, 5 timeouts): ORE 33,
NEGI 46, BOTE 11, DN 16. textbook72 (53 of 72): ORE 14, NEGI 23, BOTE 3, DN 9. Every classical-only theorem with a free
proof is flagged "requires DN" (K12 31, Charles 15, textbook72 9). The reverse fails once each in K12 and in Charles: an
intuitionistically provable theorem is flagged "requires DN", an artefact of the bound or of minlen's formula space. The
pre-registered K12 necessity sample was "600, stratified by length and primary"; the run used 594, stratified by length
only.

### R7. Lean re-check (my harness, controls first)

Controls (`controls.py`, `out/controls.json`):
- 300 / 300 untouched K12 proofs accepted.
- 0 / 200 statement swaps (the proof paired with another K12 theorem with the same premise count).
- 0 / 100 truncated proofs.
- 0 / 50 bare `sorry` (rejected by the axiom check).
- 5 / 200 single Or.inl↔Or.inr or .1↔.2 flips accepted. All 5 are no-ops (X ∨ X or X ∧ X).

Then (`recheck.py`, `out/recheck.json`), from the stored literal ND text:

| group | n | Lean-accepted | stored `lean_ok` disagrees |
|---|---:|---:|---:|
| search proofs k12_min990 / tb_schema / textbook72 | 990 / 1,610 / 58 | all | 0 |
| necessity free proofs K12 / Charles / textbook72 | 594 / 124 / 53 | all | 0 |
| necessity ban proofs K12 / Charles / textbook72 | 2,286 / 390 / 163 | all | 0 |
| Charles's reference proofs (private; classified, never shown) | 187 | all | – |
| generator proofs: K12 / cap-6 / K12⁻ / dose1 / rl_targets / transfer / holdout250 (random) | 1,000 / 300 / 300 / 300 / 300 / 300 / 160 | all | – |
| **total** | **9,115** | **9,115** | 0 |

The search and necessity proofs total **6,268**, as the run's commit message says. Structural checks: no ban proof uses
its banned rule; every proof is within its bound (search 14, necessity 12). RL proofs: §R12.

### R8. Term size

The documented per-rule formula on the pruned proof (IMPE / NEGE / ANDE / ANDI / ORI / BOTE / IMPI / NEGI = 1, ORE = 3,
DN = 3, PR / AS / R = 0) equals the executor's per-record `ts` on every record of K12, cap-6, K12⁻, Charles, k12_min990
and tb_schema (`tsize.py compare`). Medians: K12 5 (mean 4.53), cap-6 2, K12⁻ 4, Charles 8 (mean 10.79), k12_min990 2,
tb_schema 7. On 350 of **my own** Lean renderings (250 K12, 50 Charles, 50 tb_schema), `lean_check.py` accepts all 350,
and its node count equals the formula on **350 / 350**.

### R9. Canonical examples (`artifacts/ps/examples.json`, 30 examples)

`examples_check.py` checks each example against five things:
- its source record (K12 index or tb_schema index): prompt and proof identical, 30 / 30;
- my classifier: the example uses its strategy, 30 / 30;
- textbook72 classes, under every key I have (premise-order invariant, premise set, uncurried multiset / set,
  ¬A-as-A→⊥): 0 hits;
- Lean accepts the shown Lean text (`example` → theorem, axioms check), 30 / 30;
- the Lean statement is the ND sequent: my own restatement typechecks from it, 30 / 30. The negative control, restating
  with another example's sequent, fails 30 / 30.

I checked "shortest clean" with the executor's `CLEAN` rule (defined only in `examples.py`) plus my re-implementation of
its `readable` rule:
- **11 of the 12 K12 examples are minimal.**
- **The exception is disjunctive syllogism.** K12 has a 7-line clean instance (K12 index 139899), but it lies in a
  textbook72 renaming class (the premise-swapped twin noted in earlier reviews), so the guard skipped it and the example
  has 8 lines. That is the guard working; the label "shortest clean" should say "outside textbook72 classes".
- **Excluded middle's example is not from K12.** K12 has no clean instance, and the example is the shortest clean
  readable search proof among the textbook-schema instances (9 lines, minimal there).
- **Typical examples.** All 12 sit at the median pruned length of their pools. Excluded middle has no typical example,
  because no K12 proof has primary #12.
- **The five #10 kind examples** follow their stated rule: shortest *readable* proof with only that kind, primary if one
  exists.

### R10. Sealing and privacy

- **Committed files.** I extracted every ND prompt, `|-` sequent and Lean header (`leakscan.py`). Nine textbook72
  renaming classes occur, all in unit-test or self-test fixtures: `test_strategies.py` (8),
  `validation/second_impl.py` and `second_impl_fixtures_v1.2.jsonl` (3 each), `theorem_level.py` (2). All nine already
  occur in files committed before this run (`data/eval_only/textbook72/…`, `data/ladder/transfer.jsonl`, …), and
  `data/bs/textbook72.jsonl` is itself tracked in the public fork. So nothing new was exposed, but the fixtures do quote
  sealed-class sequents (hygiene).
- **Examples and data.** No canonical example, search or necessity file, spot-check file or pod input that was committed
  or uploaded holds a textbook72-class theorem.
- **Charles (private).** One exact Charles prompt occurs in a fixture: the 3-token identity sequent of a `removed.jsonl`
  row. It is a coincidence, not copied content. No reference proof occurs anywhere.
- **Bucket.** The public bucket `proof-strategies/` holds 89 files (`out/bucket_ls.txt`), none named `charles*` or
  `textbook72*` and no tarball. The per-record label and theorem files carry indices and labels only.
- **textbook72 guard keys.** Under the executor's three keys K12 has **6** records in textbook72 classes, as claimed
  (my uncurried multiset key). Looser equalities find more: 13 if duplicate premises are collapsed (A, A ⊢ B ≡ A ⊢ B),
  10 if ¬A is also uncurried as A → ⊥.

### R11. Validation records

- **Blind spot-check** (260 proofs, 20 per strategy: 12 positive, 4 negative, 4 borderline). The checkers' labels agree
  with the labels the classifier gave when the sample was drawn (v1.1) on **260 / 260** "uses" and **260 / 260**
  primary.
- **Against the final v1.2 definitions**, the same blind labels agree on **245 / 260** uses and 258 / 260 primary.
  Disjunctive syllogism agrees 10 / 20 on uses (18 / 20 primary) and excluded middle 15 / 20. Those two predicates were
  tightened *after* the spot-check, prompted by the checkers' own comments, so the final #6 and #12 were never hand-checked
  blind. The executor's `spot_compare_v1.2.json` records exactly these numbers.
- **Second implementation.** Identical to mine on K12 (R2).

### R12. RL's own proofs (create-or-elicit found files; models as in the header)

I streamed each ladder's `found_16.jsonl` from the bucket and JSON-parsed every line (no text prefilter). Every proof
with a DN line was classified with my classifier. Results (`rl_recount.py`, `out/rl_<arm>.json`):

| ladder | distinct proofs r1–16 | r1 (base model) | with #10 | working #10 r1 | working #10 r2–16 | free-working r2–16 | σ-covered targets with a working #10 (r1 / by r16) | cells = executor |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| full_s3 | 662,616 | 14,212 | 58,929 | 76 | 26,450 | 22,013 | 17 / 78 | yes |
| full_s4 | 665,629 | 18,463 | 24,441 | 32 | 9,082 | 7,886 | 15 / 33 | yes |
| full_s5 | 624,409 | 17,212 | 20,941 | 52 | 6,951 | 5,915 | 20 / 36 | yes |
| dose1_s0 | 752,455 | 14,359 | 28,988 | 15 | 16,970 | 15,731 | 2 / 69 | yes |
| dose1_s1 | 641,103 | 13,649 | 28,235 | 45 | 11,057 | 9,920 | 17 / 46 | yes |
| dose1_s2 | 638,736 | 15,729 | 22,952 | 7 | 9,969 | 9,047 | 2 / 41 | yes |
| ko_s0 | 568,100 | 13,838 | 794 | 1 | 358 | 0 | 0 / 0 | yes |
| ko_s1 | 596,861 | 13,597 | 1,039 | 0 | 399 | 32 | 0 / 5 | yes |
| ko_s2 | 719,994 | 16,984 | 1,490 | 1 | 772 | 2 | 0 / 1 | yes |
| ko_s3 | 632,736 | 14,210 | 441 | 0 | 169 | 1 | 0 / 0 | yes |
| ko_s4 | 664,562 | 14,967 | 465 | 2 | 72 | 0 | 0 / 0 | yes |
| ko_s5 | 687,864 | 18,786 | 965 | 1 | 375 | 12 | 0 / 2 | yes |

- **Reproduction.** In all 12 ladders, every per-round cell is **identical to the executor's
  `artifacts/ps/rl_found.json`**: new distinct proofs, proofs with #10, working, template-only, free-working and
  neg-goal-working, rounds 1–16. The σ-covered target sets and their first rounds are identical too. 7,855,065 distinct
  proofs in all, 0 duplicate (name, proof) lines, 0 unparsable, 0 prompts that differ from `rl_targets.jsonl`. Re-running
  three ladders gives byte-identical counts.
- **Base reachability.** Round 1 is samples of the pretrained model, before any RL update. Working #10 in round 1:
  full 76 / 32 / 52, dose1 15 / 45 / 7, K12⁻ 1 / 0 / 1 / 0 / 2 / 1. σ-covered targets with a working #10 already in round
  1: full 17 / 15 / 20 (of 78 / 33 / 36 by round 16), dose1 2 / 17 / 2 (of 69 / 46 / 41), K12⁻ 0 in all six ladders (by
  round 16: 0 / 5 / 1 / 0 / 0 / 2).
- **Knockout ladders.** After RL they write working reductios: 358 / 399 / 772 / 169 / 72 / 375 in rounds 2–16. These
  are almost never `free` (0 / 32 / 2 / 1 / 0 / 12) and only ko_s2 has `neg_goal` ones (113). The rest are `scaffolded`
  with a non-immediate route, meaning the theorem supplies ¬¬G.
- **Lean re-check of counted RL proofs** (`rl_recheck.py`): reservoir samples per ladder of 120 working-#10 proofs (all
  74 for ko_s4) plus 60 any-#10 proofs, 2,114 in all (1,694 working). **2,114 / 2,114 accepted.** Two of them (ko_s0,
  ko_s5) contain a `BOTE` line that cites a *negation*, not ⊥. That is the state-env's ND decoding of Lean's `n.elim` on
  `n : ¬A`, which is valid in Lean (Lean alone decides) but not ND's BOTE. My renderer first wrote it as `False.elim` and
  rejected both. Rendered as `Not.elim` (what the env ran), both pass. Controls re-run after the change are unchanged.
  The classifier counts such a line as an ex falso instance, though it is really a reiteration. That affects ≈ 1 in 1,000
  reductio proofs in my sample.

### R13. Pre-registered expectations, my values (`out/expectations.json`)

| | expectation | mine (K12 unless named) | |
|---|---|---:|---|
| E1 | conditional proof 65–90 % | 42.95 % | **miss** |
| E1 | ∨I 30–55 % / cases 25–50 % / ∧I 30–55 % | 44.26 / 44.16 / 32.57 % | hit |
| E1 | ex falso 8–20 % | 8.04 % | hit (barely) |
| E1 | disjunctive syllogism 3–10 % | final 0.03 % (v0 0.24 %) | **miss** |
| E1 | proof of a negation 4.4–7 % | 4.74 % | hit |
| E1 | MT / contraposition 2–6 % | final 0.05 % (v0: 0.05 % by my reading, 64 records by the executor's) | **miss** |
| E1 | DNE 2.5–3.5 % / LEM < 0.5 % / lemma reuse 10–35 % | 3.06 / 0.03 (v0 0.06) / 11.71 % | hit |
| E1 | box-free 3–12 % | 24.91 % | **miss** |
| E1 | vacuous discharge 15–40 % | 28.20 % | hit |
| E2 | primary conditional proof 40–65 % | 37.65 % | **miss** |
| E2 | primary #10 2–6 % / unlabelled < 1 % | 2.91 % / 0 | hit |
| E2 | curried primary #10 5–9 % | 3.50 % | **miss** |
| E3 | only in dead lines 5–20 % | 0 % (no dead lines anywhere) | **miss** |
| E4 | K12⁻ #10 = 0 / #7 4–8 % / #11 2.5–3.5 % | 0 / 5.19 / 3.29 % | hit |
| E4 | cap-6 #10 3–10 % / nested cases < 2 % | 6.81 % / 0 | hit |
| E5 | Charles: classical-only 15–35 % / #10 15–35 % and ≥ 1.5 × K12 | 22.46 % / 20.86 % (1.93 ×) | hit |
| E5 | Charles: vacuous discharge < 5 % | 10.70 % | **miss** |
| E5 | a strategy ≥ 3 × K12 and ≥ 5 % absolute | DS 14.44 vs 0.03 %; MT 11.76 vs 0.05 %; working #10 20.86 vs 0.04 %; ¬I 37.97 vs 4.74 % | hit |
| E6 | #10 users that are classical-only 20–40 % | 25.60 % | hit |
| E6 | classical-only proved with #10 50–90 % | 68.60 % | hit |
| E6 | shortest proofs use #10 at < ½ the generator rate | 2.22 % vs 10.00 % on the same 990 records (0.22 ×) | hit |
| E7 | spot-check ≥ 19 / 20 per strategy | v1.1: 20 / 20 all; v1.2: DS 10 / 20, LEM 15 / 20 | hit for v1.1; final #6 / #12 not blind-checked |
| E7 | second implementation ≥ 99.5 % | 100 % (identical on every record) | hit |
| E7 | term-size formula = lean_check 100 % / examples 100 % Lean | 350 / 350 / 30 / 30 | hit |

That is 8 misses.

### R14. Hard constraints

- `nd_verify/` tree at HEAD = `origin/main` (9437bb72…): unmodified.
- The run never calls `verify_text`. The search uses `minlen.Search.run` directly, which has no `nd_verify` call; only
  the `minlen()` wrapper has one. Every kept proof is Lean-checked, and my harness accepts all of them.
- `artifacts/TEST_RUN_DONE` blob 1d5cf064 = base = `origin/main`.
- No training code exists, so no evaluation file can be read by it.
- No test-file run.

**No hard-constraint violation.**

### R15. Compute

- One pod, `ps-c0` (RTX 3090, used for CPU only): 0.1958 billed h, $0.10 (`~/podhours.log`), 705 pod-seconds.
- The budget was registered (40 h / $20) at 18:23 and again at 18:52, before the pod was created at 19:16.
- Registry: 40 rows (`artifacts/proof-strategies/registry/`), per job J1–J6 (gpu_seconds 0, gen_tokens 0, train 0,
  lean_checks 1,610 / 58 / 990 / 2,880 / 514 / 216 = 6,268) plus the pod row. Everything else ran on the VPS.

## §Compare (phase 2: the executor's write-ups against §Recount)

*Errata to §Recount (found by the adversarial check; the phase-1 text is commit 0c306489):*
- The dose set is **K12⁻** + 1 % σ, not K12 + 1 % σ. This is fixed in the header and R1; R4's dose column, which tracks
  K12⁻, was always right.
- R15's billing source is `~/podhours.log`; the numbers were right.
- R10 missed that the fixture file `second_impl_fixtures_v1.2.jsonl` (3 textbook72 classes) is also uploaded to the
  public bucket (two copies). See §Verdict, hygiene.
- My own phase-1 commit had the hygiene problem I flag for the executor. `review_ps/ipc.py`'s G4ip unit tests quoted 9
  textbook72-class sequents (DS, Peirce, DNE, …), all 9 already in pre-run public files. The final commit replaces them
  with substitution instances (P := P ∧ R) that keep the expected results: 25 / 25 pass, 0 in a textbook72 class.

Read after §Recount was committed (0c306489): `run_proof_strategies.md`, `numbers.md` § proof-strategies, `log.md`
§ proof-strategies, `STATUS.md`, `proof_strategies/EXPECTATIONS.md`, `blog.md`, and (with three read-only
sub-auditors, whose consequential rows I re-derived) `TABLES.md`, `TAXONOMY.md` and `EXAMPLES.md`. Extra checks run in
phase 2: σ-covered RL targets proved *at all* (`rl_sigcov.py`), the 25 edge-case fixtures (`fixtures_check.py`), the
blog's Lean snippets, and the executor's unit tests (`test_strategies.py`: pass).

### C1. `run_proof_strategies.md` (199 words)

| claim | independent value | verdict |
|---|---|---|
| 13 named strategies, each a checkable predicate | 13; my blind re-implementation reproduces every label on every record (R2) | reproduces |
| "Lean checked every searched or shown proof" | 6,268 search / necessity proofs, 30 examples, 12 blog snippets: all accepted by my harness (R7, R9, C6) | reproduces |
| "Blind spot-check: 260 / 260" | 260 / 260 against the **v1.1** labels; against the final v1.2 definitions 245 / 260 uses (disjunctive syllogism 10 / 20, excluded middle 15 / 20), because those two rules were tightened after the check (R11) | **reword**: say "v1.1", and that the final #6 and #12 were not hand-checked blind (the second implementation does cover them) |
| "Independent second implementation: agrees on every record" | identical to mine on all 155,000 K12 records (R2) | reproduces |
| K12 →I 43 %, cases 44 % (38 % redundant), ∨I 44 %, proof by contradiction 10.8 % | 42.95 / 44.16 (37.64) / 44.26 / 10.79 % | reproduces |
| σ = the reductios via ¬I; σ⁺ adds DNE on a derived ¬¬ | 16,703 = #10 via NEGI; σ⁺ 16,961 = #10 ∪ #11 `on_derived`, 0 records differ (R2) | reproduces |
| "Only 59 of the 16,717 reductios do working reasoning, all on theorems that do not need one" | 59 of 16,717 *proofs* with a reductio; none of the 59 is classical-only (R5) | reproduces (they are proofs, not reductios: 17,405 reductio steps) |
| "no K12 theorem is σ-covered" | 0 when (¬X → ⊥) counts as a double negation (the run's semantic rule); **2,340** (1.51 %) under the pre-registered and create-or-elicit rule (no `( ~ ( ~` / "no ¬¬ subformula"), all with a (¬X → ⊥) subformula (R5) | **wrong as stated** (unflagged deviation from the pre-registered definition): name the rule |
| Textbooks: working reductio 21 %, ¬I 38 %, MT 12 %, DS 14 % | 20.86 / 37.97 (working; any 37.97) / 11.76 / 14.44 % | reproduces |
| RL: full 32–76 working reductios before RL, 6,951–26,450 in rounds 2–16; knockout 0–2, then 72–772, ≤ 5 σ-covered problems | 76 / 32 / 52; 26,450 / 9,082 / 6,951; knockout 1 / 0 / 1 / 0 / 2 / 1, then 358 / 399 / 772 / 169 / 72 / 375; σ-covered proved **at all** by r16 0 / 5 / 1 / 0 / 0 / 2 (every σ-covered target any ladder proved was proved with a working reductio; `rl_sigcov.py`) | reproduces; the model is not named in the summary (it is in `numbers.md`) |
| Expected vs outcome: 45 rows; misses →I, DS, MT, box-free, dead lines, requires-∨E, knockout round-1 zeros | my E1–E7 misses (R13) are all in the ledger; the summary's short list omits three ledger misses (E2 primary →I 37.65 %, E2 curried #10 3.50 %, E5 textbook vacuous discharge 10.7 %) and the knockout-r16 miss (84 > 50 on one seed) | **reword** (complete the miss list or say "e.g.") |

### C2. `numbers.md` § proof-strategies

Every number in the section reproduces at its stated precision (≈ 150 numbers; method: each against `review_ps/out/`):
- **K12 uses and sub-types.** 51.15 / 32.57 / 42.95 (20.80, 28.20) / 44.26 / 44.16 (8.79, 37.64) / 43 / 4.74 (2.15) / 76 /
  8.04 (6.23) / 16,717 / 3.06 / 47 / 11.71; box-free 24.91.
- **K12 primary and curried.** Primary 37.65 / 20.85 / 14.08 / 12.24 / 9.71 / 2.91; curried ≈ 33 (33.41) / 20.50 / 19.38 /
  3.50 / 3.26.
- **σ and reductio kinds.** σ 16,703 ⊂ 16,717; σ⁺ 16,961; working 59; all-template 16,658; kinds 8,209 / 1,082 / 7,693 /
  48 / 6.
- **K12 theorem level.** 6,238, 45,630, 36,472, 4,279 (25.6 %), 1,959.
- **990-theorem search sample.** Shorter on 534 (longer on 1); mean pruned lines 7.00 → 4.69; cases 42.5 → 6.1 %;
  #10 10.0 → 2.2 %; redundant / vacuous / pointless / vacuous ¬I → 0.
- **Necessity (594 sample).** 6.1 / 3.7 / 0 / 5.4 %; DN ban = G4ip 593 / 594; ∨E users needing ∨E 36 / 258 = 14.0 %.
- **Comparison sets.** cap-6 6.81 % (4 working), 1.46 %; K12⁻ 0 / 5.19 / 3.29; dose 1,550 (5 working, 2 free); Charles
  20.86 (free 20.32), 37.97, 11.76, 14.44, 33.69, 42 (22.5 %), 35 (18.7 %), NEGI 46 / 124 = 37.1 %; schemata 20.75,
  39.57, 10.43, 5.59, 5.34, σ-covered 240; textbook72 58 / 72, 17.2 % (all working), 32.8 %, 16 / 72.
- **RL ladders.** Every per-ladder count, including the round-16 shares 4.47 / 1.55 / 1.39 % vs 0.53 / 0.17 / 0.30 %
  (working) and free 38 / 27 / 45 then 22,013 / 7,886 / 5,915 etc.
- **Validation and compute.** 6,268 / 0 rejected; 400 / 400; 260 / 260 *labelled v1.1 here*; second implementation v1.2
  every record; $0.10 / 0.1958 h.

Only labelling issues:
- "σ-covered **0**" is wrong as stated without its definition (C1).
- The RL section names the model fully: create-or-elicit's 9.56 M ALiBiGPT `lean_staten`, from scratch on K12 / K12⁻ /
  dose, T1 on A40, Lean alone.

### C3. `log.md`, `STATUS.md`, pre-registration timing

- **Pre-registration.** a30bc33b at 18:52:50 UTC. The first strategy count (classifier v0) is in 82fa2c47 at 19:04:31.
  Before 18:52 the executor transcript shows only format, field-name and source-count inspection. Two commands
  (18:40:09, 18:40:17) read `textbook72.jsonl`: the first printed its non-sequent field values (hash, name, line count,
  role), the second counted keys. No theorem was shown. That matches the pre-registration's "what I had seen" paragraph.
- **Pod jobs** J1–J6 with expectations were committed at 19:15:40 (44939fda), and the pod was created at 19:16:09
  (`~/pods.log`). The log justifies the pod (VPS estimate 5–70 CPU-h > the pre-registered 6 h). Spend $0.10 of $20.
- **RL expectations** were committed 19:57:21 (9a8b2dd9), before this run's first RL count (run 19:59, committed 20:11).
  They were not written blind to related data. At 19:56:27–30 the executor printed create-or-elicit's per-round artefact
  for full_s3: 17 σ-covered targets in round 1, and its `pos_free` reductio counts by round (655 in round 1, rising every
  round). The RL expectations, including "round 16 ≥ 10 × round 1", were written a minute later. They therefore carry
  less weight as predictions; this is minor, but the ledger should say so.
- **The first RL count used the wrong data.** It came from the fine-tune mixes, a capped sample of the accumulated pool,
  which the executor's own claim check caught. The ledger re-evaluates the pre-registered rows on the found files and
  keeps the mix verdicts visible ("had missed on 2 / 3 seeds"). On the found files two RL rows are misses and are
  reported as misses. "≥ 10 ×" is "hit on counts, miss as shares", and both are stated; counts were the pre-registered
  quantity.
- **Deviations from the pre-registration not flagged as such:**
  1. **σ-covered.** The pre-registration defines it as "classical-only and no ¬¬ subformula anywhere in the sequent
     (create-or-elicit's definition)", a syntactic rule. `theorem_level.py` (965fb4ec, 19:35) and TAXONOMY §4 use a
     semantic rule that also counts (¬X → ⊥), ¬(X → ⊥) and ((X → ⊥) → ⊥), and `log.md` has no entry for the change.
     Under the pre-registered rule K12 has 2,340 σ-covered theorems, not 0. This is the most consequential deviation.
  2. **Like-for-like search sample:** pre-registered as 1,000 records, run as 990 (90 per length).
  3. **K12 necessity sample:** pre-registered as 600 stratified by length and primary, run as 594 stratified by length
     only. The 19:15 entry states the new designs for items 2 and 3 but not the changes.
  4. **Final DS change** (K12 47 → 43; e0511ae6, "other case must not be falsum") is not in `log.md`.
  5. **Compute** was not recorded "per step as VPS CPU-seconds".
- **STATUS.md.** The 20:37 entry says "blind spot-check 260 / 260" without the version (C1). It also says "RL's own
  proofs classified (create-or-elicit mixes)", superseded at 21:10. The 21:56 DONE line:
  - repeats "0 σ-covered theorems" (C1);
  - writes "proof by contradiction (= σ)" (16,717 vs 16,703);
  - says "vs ≤ 2 %" for K12 (working ¬I is 2.15 %);
  - asserts causally that "RL models wrote thousands of free reductios from that template", a reading the blog itself
    labels untested.

### C4. `blog.md` (1,999 words; my reading, cross-checked against the blog sub-auditor)

| line | claim | independent value | verdict |
|---|---|---|---|
| 10–13 | 260 proofs hand-checked "agreed with the classifier before their notes tightened two rules"; a program from the definitions alone agrees on all 155,000 | 260 / 260 vs v1.1; second implementation identical on 155,000 (R2, R11) | reproduces; this wording, unlike the run summary's, is exact |
| 18–19 | 38 % split into cases where one case never uses its assumption | 37.64 % | reproduces |
| 20–22 | #10 in 10.8 %; only 59 of 16,717 do more than clash at once with G or a stated ¬¬G; none on a theorem that needs it | 10.79 %; 59; 0 of 59 classical-only | reproduces ("clash at once" covers the vacuous kind too: there ¬G does nothing at all) |
| 23–24 | 187 textbook problems: working #10 21 % (K12 0.04 %), working ¬I 38 % (2 %), MT 12 % (0.05 %) | 20.86 / 0.04; 37.97 / 2.15; 11.76 / 0.05 | reproduces |
| 26–28 | full models wrote 27–45 free reductios before RL, 5,915–22,013 more in 15 rounds | 38 / 27 / 45; 22,013 / 7,886 / 5,915 (R12) | reproduces; base round 1 shown beside RL, as policy requires |
| 41 | ≈ 14,100 K12 proofs per length 2–12 | 14,091 (14,090 at 12) | reproduces |
| 42–45 | K12⁻ = K12 minus 16,961 σ / variant proofs; 32 tries per problem | σ⁺ 16,961; create-or-elicit `numbers.md` "k 32 samples" | reproduces |
| 52–76 | field-guide shares 51 / 33 / 43 / 44 / 44 / 0.03 / 4.7 / 0.05 / 8 / 10.8 / 3.1 / 0.03 / 12 % | 51.15 / 32.57 / 42.95 / 44.26 / 44.16 / 0.03 / 4.74 / 0.05 / 8.04 / 10.79 / 3.06 / 0.03 / 11.71 | reproduces; 12 / 12 Lean snippets accepted by my harness, none in a textbook72 class (any of my keys) |
| 77 | items 6 and 8 are (mostly) special cases of 5 and 7 | DS ⊂ ∨E always; MT includes σ boxes (classical MT) and contrapositions, not ¬I instances | reproduces ("mostly") |
| 86–88 | 28 % assume something never used; 38 % idle case split; 24 % contradictory premises | 28.20 / 37.64 / 23.53 % | reproduces |
| 90–92 | shortest proofs: a third shorter; idle splits 35 % → 0; cases 43 → 6 %; unused assumptions 29 → 23 %; contradictory premises used 6 → 16 % | 7.00 → 4.69 lines; 34.8 → 0; 42.5 → 6.1; 29.1 → 22.8; 5.9 → 16.3 % | reproduces |
| 100–104 | 16,658 of 16,717 template-only; vacuous ones "usually from contradictory premises" | 16,658; 7,300 of the 8,209 records with a vacuous reductio have unsatisfiable premises (88.9 %) | reproduces |
| 106–115 | the working example; all 59 on intuitionistically provable theorems; 48 prove a "not" | Lean-accepted; 0 classical-only; 48 `neg_goal` | reproduces |
| 117–119 | 6,238 classical-only theorems all state a double negation; none σ-covered; "so that every proof needs a working reductio" | 6,238; 0 under the run's semantic rule, 2,340 under the pre-registered / create-or-elicit literal rule (R5); ≥ 573 RL proofs of σ-covered targets carry no #10 (C7) | **wrong as stated** (both halves): name the rule; say "eliminates a double negation it built itself" |
| 124–129 | 187 problems (173 search-minimal, 14 hand-written); 1,610 law instances; textbook72 "never printed"; 6 K12 records match up to renaming, premise order or currying; 58 of 72 searched | 87 + 72 + 14 = 173 search-found (17 of them minimal per conjunct only), 14 hand; 1,610; 0 textbook72 class in the blog or examples, but 3 classes in an uploaded test-fixture file and 9 in committed fixtures (R10, errata); 6 under the uncurried multiset key (13 if duplicate premises are collapsed); 58 | numbers reproduce; "never printed" **overstated**: say "not shown here" |
| 133–139 | table: 21 / 0.04, 12 / 0.05, 14 / 0.03, 38 / 2, 34 / 9 % | 20.86 / 0.04, 11.76 / 0.05, 14.44 / 0.03, 37.97 / 2.15, 33.69 / 8.79 | reproduces |
| 141 | law instances and textbook72 agree | schemata: working #10 20.75, MT 10.43, DS 5.59, working ¬I 39.57 %; textbook72: 17.2, 3.4, 6.9, 32.8 % — all far above K12 | reproduces (direction) |
| 142 | 19 % of textbook problems σ-covered, none in K12 | 18.72 %; K12 0 (semantic) / 2,340 (pre-registered literal rule) | **wrong as stated**, as for 117–119 |
| 143–144 | of 124 decided textbook problems 37 % need ¬I / reductio; K12 sample 3.7 % | 46 / 124 = 37.1 %; 22 / 594 = 3.7 % (a length-stratified sample; K12 is uniform over lengths, so representative) | reproduces |
| 148–152 | families acquired: 6 / 6 full (5 before RL), 0 / 6 knockout, 3 / 3 dose (1 before RL); K12 59 working (6 free); dose set 5 (2 free) | create-or-elicit `numbers.md` r16 6 / 6 vs 0 / 6, dose 3 / 3; `artifacts/coe/compare_pend_x0.json` at pend: full 5 / 6, knockout 0 / 6, dose 1 / 3; 59 / 6; 5 / 2 | reproduces (inherited; create-or-elicit's checker is Lean alone, post 2026-09-27) |
| 154–162 | 12 of 15 ladders; round 1 free 38 / 27 / 45, σ-covered 17 / 15 / 20 of 123; rounds 2–16 22,013 / 7,886 / 5,915, 78 / 33 / 36; dose 13 / 43 / 7 then 9,047–15,731; knockout none in round 1, then 0–32, ≤ 5 σ-covered; "free working reductios, the kind σ-covered problems need" | all as in R12; 123 σ-covered targets; knockout σ-covered proved at all 0 / 5 / 1 / 0 / 0 / 2; but ≥ 573 proofs of σ-covered targets carry no #10 (C7) | numbers reproduce; "the kind σ-covered problems need" **wrong as stated** (C7) |
| 161–162 | knockout's other working reductios "mostly lean on a double negation the problem states" | rounds 2–16: 2,145 working, 47 free, 113 negated goal, the remaining 1,985 (93 %) scaffolded | reproduces |
| 164–166 | rarely before RL (0.15–0.27 % of the full models' proofs), more often in round 16 (1.2–3.9 % of that round's new proofs); 33–78 of 123 σ-covered | free r1 (s3 / s4 / s5) 0.267 / 0.146 / 0.261 %; free r16 3.86 / 1.36 / 1.19 %; 33–78 | reproduces; note the round-16 denominator is proofs *first found* in round 16, a different population from round 1's (the text says "new proofs") |
| 166–168 | both arms saw working ¬I (2 %) and DNE of a stated ¬¬ (3 %); "the knockout removed only their combination" | working ¬I 2.15 / 2.25 %; DNE 3.06 / 3.29 %; σ⁺ also removed DNE on derived ¬¬ lines not built by ¬I (#11 `on_derived`, 260 K12 records, 0.17 %) | **imprecise** (minor): "only their combination, plus DNE on a derived ¬¬ (0.17 %)" |
| 44 | expert iteration = "try each problem 32 times, keep what Lean accepts, fine-tune, repeat" | each round's fine-tune also replays 20,000 records from the arm's own pretraining set (`state_ladder_ei.py --retain 20000`; create-or-elicit `numbers.md`), so the full arm kept seeing K12's σ templates during RL | **imprecise**: bears on the "pretraining supplied the form" reading (lines 164–168); say it |
| 23, 121 | "Textbook problems use what K12 lacks" (also the section heading) | K12 has working ¬I in 2.15 % and genuine case splits in 8.8 %; only working reductios (59), MT (76) and DS (43) are near-absent | overstated (minor): "uses what is rare in K12" |
| 62, 137 | DS 0.03 % in K12 (×≈ 500 below textbooks) | 0.03 % under the final rule, tightened after the spot-check; 0.24 % under v0 (Charles 14.4 % either way) | minor: give the v0 value or say the rule was tightened |
| 125 | "173 minimal ones found by search" | 156 by whole-proof search, 17 minimal per conjunct only (`min_lines_method` "conjunct split") | minor |
| 168 | "This is our reading, not a tested result." | – | appropriate hedge |
| 172–176 | caveats: labels describe the proofs we have; 15 models, one architecture, 9.6 M; RL counts use 12 | create-or-elicit: 6 + 6 + 3 ladders, 9.56 M ALiBiGPT | reproduces; the format (`lean_staten` proof-state env) and checkpoints (round-1 = pend samples, found_16) are not named in the blog: **minor model-label gap** |

### C5. `TABLES.md` (sub-auditor; 65 rows, 1,890 cell checks; `review_ps/phase2/tables.md`)

Every table cell equals my recount except two definitional cells (#35, #50). I re-derived each consequential row
myself:

| item | finding | my check | severity |
|---|---|---|---|
| header (line 5) | "**No models**: these are properties of data files and of proofs found by a search" | § 11 reports 7,855,065 proofs written by 12 RL-trained model ladders | **wrong wording** (no number affected) |
| § 4 (lines 129, 132) | σ-covered and "double negation in the sequent" never say the rule is semantic | literal ¬¬ only (the pre-registered rule): K12 σ-covered 2,340 (not 0), dneg 40,550 (26.2 %, not 45,630) | **wrong as stated** (= C1) |
| § 5 caption (lines 174–176) | "how often the data proof uses a strategy the theorem does **not** require" | the "share" column is the share where it **is** required (36 / 258 = 14.0 %); the caption's quantity is 86.0 / 100 / 62.0 / 75.8 % | imprecise (inverted caption) |
| § 5 row (line 180) | "proof by contradiction (theorem classical-only) 27 / 71 (38.0 %)" | 27 = bounded requires-DN; G4ip classical-only is 26 / 71 (36.6 %) | minor mislabel |
| § 5 textbook72 "decided 54" | includes one trivial theorem (conclusion = premise) with no proof text, never Lean-checked | 53 with a proof → 26.4 / 43.4 / 5.7 / 17.0 % | minor |
| § 8 "shortest proofs" | on 1 of 990 theorems (K12 #68340) the search proof has 9 lines, the generator's 8 | shortest only within minlen's formula space | minor |
| § 9 v0 MT 0.04 % (64) | my reading of the v0 text gives 71 (0.05 %) | the cell matches its source (`k12_v0.json`) | minor (definitional) |
| § 11 (lines 304–306) | models named (9.56 M ALiBiGPT `lean_staten`, from scratch, sets, T1 on A40); no checkpoint | – | minor |
| § 11 (line 306) | "σ-covered = RL targets whose every proof needs a working reductio" | false under the taxonomy's own #10: ≥ 573 counterexamples (C7) | **wrong as stated** |
| layout | sections ordered 1–9, 12, 11, 10; `state_env_october` undefined; source "(bucket)" for unuploaded private / sealed nec files; mixed precision in one row | – | minor |

### C6. `TAXONOMY.md` and `EXAMPLES.md` (sub-auditor; 161 rows; `review_ps/phase2/taxonomy_examples.md`)

- The share table, §5 counts and §6 counts reproduce. That includes the 277 proofs v0 left unlabelled (exactly the
  root-¬E proofs) and the 39 / 39 unit tests, which pass when I run them.
- All 29 example blocks in EXAMPLES.md are string-identical to `examples.json`. `lean_check` (allowlist + axioms) accepts
  all 30 Lean texts and the 12 blog snippets, and its node counts equal the stated term sizes (30 / 30).

| item | finding | my check | severity |
|---|---|---|---|
| TAXONOMY §5 (line 204), §4 (line 189) | "σ-covered (create-or-elicit) … K12 records (both): 0" | 2,340 under create-or-elicit's (and the pre-registration's) literal rule | **wrong as stated** (the "both" column) |
| TAXONOMY §4 | "every proof must then eliminate a double negation it built itself: a working #10 (or #12)" | the first half is true; the "#10" half is false (C7) | **wrong as stated** |
| TAXONOMY §6 | spot-check reported for v1.1 only | 245 / 260 vs v1.2; final #6 / #12 not blind-checked | imprecise (= C1) |
| TAXONOMY §6 (lines 230–231) | `bot_case` listed among sub-types "the data never exercise" | 2,070 K12 records have it | minor |
| EXAMPLES cases "typical" gloss (line 145) | "Typical of K12: the premises are inconsistent, the split is on a disjunction obtained by explosion, and one case ignores its assumption" | among the 32,311 primary-cases K12 proofs: inconsistent premises 32.6 %, root split on an exploded disjunction 0.33 %, idle split 89.5 % | **wrong** gloss (only the idle split is typical) |
| EXAMPLES #10 "typical" gloss (line 341) | "Typical of K12: the premise already says ¬G → ⊥" | of the 4,516 primary-#10 K12 proofs, 1,413 (31.3 %) have a premise ¬G → ⊥ (995 a premise ¬¬G); any scaffolded reductio 53.3 %, any vacuous 46.3 % | **wrong** gloss (same severity as the cases gloss) |
| EXAMPLES →I "typical" gloss (line 82) | "two assumptions are opened and never used" | 4,395 of the 58,363 primary-→I K12 proofs (7.5 %) have ≥ 2 unused →I assumptions (the sub-auditor's narrower count: 7.3 %) | **wrong** gloss |
| EXAMPLES "shortest clean" | the readability filter that picks it is defined only in `examples.py` | shorter clean K12 instances exist for ∧I (2 vs 3 lines), →I (2 vs 3), ¬I (2 vs 5), ex falso (3 vs 4), lemma reuse (5 vs 6); the DS one skipped by the textbook72 guard is not mentioned | imprecise (say "shortest clean readable, outside textbook72 classes") |
| EXAMPLES term sizes | lean_check on the readable rendering, 2 below the per-rule formula used in TABLES for every example with a DN step (e.g. 8 vs 10) | – | minor (two "term size" figures for one proof) |
| EXAMPLES | 29 blocks shown for 30 examples: the `free` kind example is the same record as the #10 shortest clean one and is dropped silently | – | minor |

### C7. Classical proofs that #10 does not see (found in phase 2; extent from the adversarial check)

- **The two proofs that raised it.** In dose1_s0, 2 σ-covered targets were first proved one round *before* their first
  proof with a working #10. I re-downloaded the ladder and looked at those earlier proofs: `la_rl_targets_983` (round 9)
  and `la_rl_targets_70` (round 10), both Peirce-shaped. Both are proved by:
  - ¬I builds ¬¬P (assume ¬P, reach ⊥);
  - ∨I makes P ∨ ¬¬P;
  - ∨E splits on it, with DN applied to the **case hypothesis** ¬¬P.

  Both are Lean-accepted by my harness and valid ND by my checker. The classifier labels the DN #11 `on_hypothesis`
  ("DNE on a double negation the theorem supplies"), and the proofs contain no #10.
- **The extent.** create-or-elicit's own per-round proof classes for the same found files
  (`artifacts/coe/rounds/la_<arm>.json`, `proof_classes_by_round_sigma_targets`) cover the same 123 σ-covered targets.
  In rounds 1–16 they put **573** Lean-accepted proofs of σ-covered targets in classes where every DN cites a premise or
  a hypothesis (`dn_pr_as`, `lemma_route`), so none can carry #10 (`out/coe_no_sharp10_sigma_proofs.json`):
  - dose1_s0: 491 of its 11,767 σ-target proofs (4.2 %);
  - full s3 / s4 / s5: 5 / 11 / 49;
  - dose1 s1 / s2: 9 / 8;
  - knockout: 0.

  Knockout s1 has 29 lemma-route proofs, but only in rounds 18–24, beyond this run's scope.
- **A second route.** Besides the ∨E route there is create-or-elicit's →I **lemma route**: prove ¬¬X → X by DN on the
  box hypothesis, then apply it by →E to a ¬I-built ¬¬X. My classifier also labels that #11 `on_hypothesis` plus a
  working #7, with no #10.
- **Consequences:**
  - "σ-covered ⇒ every proof needs a working #10" is **wrong as stated**: TAXONOMY §4, TABLES § 11, blog lines 119 and
    155–156. The semantic statement, that every proof eliminates a double negation it built itself, is true. The pattern
    also escapes σ⁺ (DN citing an assumption).
  - **Target-level RL results do not change.** By round 16 every σ-covered target any ladder proved also has a
    working-#10 proof (`rl_sigcov.py`: proved at all = proved with a working #10 on all 12 ladders).
  - **Per-proof RL counts would change.** The counts with #10, working and free (R12, reproduced as defined) would rise
    under a #10 that includes these routes: by up to 573 among σ-covered targets, about 3 % of dose1_s0's free proofs.
    Proofs of other targets were not measured.
  - The knockout claims are unaffected (0 such proofs in rounds 1–16).
- **Pretraining sets.** `dn_on_hyp.py` finds DN on a self-introduced ¬¬ hypothesis in 37 K12, 11 K12⁻, 12 dose and 1
  cap-6 proofs, and 0 in Charles's and the schemata. Every ∨E-routed instance in these sets is on the case that never
  occurs (the ∨I built the other disjunct). So the knockout set holds no real disguised reductio, and no pretraining
  number changes.
- **Fix.** Extend #10 to DN on any box hypothesis ¬¬X that is not a subformula of the theorem, when the proof builds ¬¬X
  by ¬I. Recount the RL per-proof numbers and reword the σ-covered sentences to the semantic form.

## §Verdict

**No hard-constraint violation.**
- `nd_verify` is unmodified (tree = `origin/main`) and judges nothing: the search bypasses its call, and every kept
  proof is Lean-checked.
- `TEST_RUN_DONE` is unchanged. There is no training code and no test-file run.
- No canonical example, shown proof or blog snippet is in a textbook72 class.
- No Charles content is committed or uploaded. The one exact match is a 3-token identity sequent, a coincidence.
- Brief-level hygiene items below (fixtures quoting textbook72 classes) are not hard constraints.

**What stands (reproduced independently).**
- **The classification.** My blind third implementation of the 13-strategy taxonomy matches the executor's classifier
  on every record of all 11 classified sets: 4 × 155,000 generator proofs, the pools, Charles's 187 and the search
  proofs. It covers uses, working flags, every sub-type, primary and curried primary, and also matches the second
  implementer on all of K12 and the 25 edge-case fixtures. Every count in `numbers.md`, the run summary, `TABLES.md`
  (1,890 cells checked by a sub-auditor), TAXONOMY's share table and the blog follows from those labels and reproduces
  at its stated precision, except two convention cells in TABLES (textbook72 "decided" 54 vs 53; v0 MT 64 vs 71).
- **The σ mapping as defined.** σ = #10 via ¬I (16,703); σ⁺ = #10 ∪ DNE on a derived ¬¬ (16,961, 0 records differ).
- **K12 facts.** 59 of 16,717 reductio proofs do working reasoning, none on a classical-only theorem. 38 % of proofs
  have an idle case split, 28 % an unused →I assumption, 24 % inconsistent premises. There are no dead lines. A
  shortest-proof search on 990 theorems removes idle splits and cuts #10 from 10.0 % to 2.2 %.
- **Textbook contrast.** Charles's 187 problems vs K12: working reductio 20.9 vs 0.04 %, MT 11.8 vs 0.05 %, DS 14.4 vs
  0.03 % (DS 0.24 % in K12 under v0), working ¬I 38.0 vs 2.1 %.
- **Theorem level.** My own G4ip reproduces every theorem-level label on every record. Its completeness self-check holds:
  none of 580,962 DN-free proofs is of a theorem judged unprovable. The necessity flags reproduce from the stored searches.
- **Lean.** My independent harness, which rejects every negative control, accepts:
  - all 6,268 search and necessity proofs;
  - Charles's 187 reference proofs;
  - 2,660 sampled generator proofs;
  - the 30 examples (their Lean statements are the ND sequents);
  - the 12 blog snippets;
  - 2,114 sampled RL proofs.

  `lean_check`'s allowlist accepts the 30 examples and 12 snippets. The term-size formula equals `lean_check` on
  350 / 350 of my renderings.
- **RL.** The RL counts reproduce cell for cell on all 12 create-or-elicit ladders (7,855,065 distinct proofs), with
  round 1 (the pretrained model) beside every RL number. "Knockout models proved ≤ 5 σ-covered problems" holds for
  proofs of any kind (0 / 5 / 1 / 0 / 0 / 2).
- **Expectations.** The ledger reports every miss: 8 E-rows, J4 and two RL rows. It discloses the mix-data mistake and
  the hit-on-counts / miss-on-shares split. Spend: $0.10 of $20.

**Must be reworded (no reported count changes, except the RL per-proof counts flagged in item 2).**
1. **σ-covered is wrong as stated, and it deviates from the pre-registration.** Affected: "no K12 theorem is
   σ-covered", "σ-covered 0", "create-or-elicit's definition", TAXONOMY §5's "(both)" column, TABLES § 4, blog lines
   117–119 and 142, STATUS.
   - The 0 holds only under the run's semantic rule, which counts (¬X → ⊥) as a double negation.
   - The pre-registered rule ("no ¬¬ subformula anywhere in the sequent") is also create-or-elicit's, and it is
     syntactic. Under it K12 has 2,340 σ-covered theorems (1.51 %), all through a (¬X → ⊥) subformula. cap-6 has 2,235
     (2,234 such, plus 1 σ-covered under both rules) and the dose set 232.
   - Log the change and name the rule. The pools, Charles and textbook72 agree under both rules.
2. **"Every proof of a σ-covered theorem needs a working reductio (#10)" is wrong as stated.** Affected: TAXONOMY §4,
   TABLES § 11, blog lines 119 and 155–156.
   - In rounds 1–16, ≥ 573 Lean-accepted RL proofs of σ-covered targets eliminate a self-built ¬¬ through a box
     hypothesis and carry no #10. Two routes do this: the ∨E-case route and create-or-elicit's →I "lemma route".
     dose1_s0 has 491 of them; knockout ladders have 0 (C7).
   - Say "eliminates a double negation it built itself", or extend #10. Then the RL per-proof counts with #10 /
     working / free rise; target-level results do not change.
3. **"Blind spot-check: 260 / 260"** (run summary, STATUS). The 260 / 260 was against v1.1. The final DS and LEM
   predicates were tightened after the check and never hand-checked blind: the blind labels agree with them 10 / 20 and
   15 / 20, so only the second implementation validates them. TAXONOMY §6 should say so too.
4. **TABLES.**
   - The header "No models" is false for § 11.
   - The § 5 caption says the opposite of its share column.
   - The § 5 row "(theorem classical-only) 27" is bounded requires-DN; by G4ip it is 26.
5. **Blog, line 44.** Expert iteration also replays 20,000 pretraining records per round, so the full arm kept seeing σ
   templates during RL. Say so beside the "pretraining supplied the form" reading.
6. **EXAMPLES glosses.** Three "typical" glosses describe their one record, not K12:
   - cases: inconsistent premises 32.6 %, exploded disjunction 0.33 %; only the idle split is typical (89.5 %);
   - #10: a ¬G → ⊥ premise 31.3 %;
   - →I: "two assumptions never used" 7.5 %.

   "Shortest clean" relies on a readability filter stated only in code, and on the textbook72 guard (DS: a 7-line
   instance was skipped).
7. **Timing of the RL expectations.** They were written a minute after the executor printed create-or-elicit's per-round
   reductio counts for one ladder. "Committed before the counts" is true only of this run's own counts; the ledger
   should say so.
8. **Smaller wording items:**
   - the run summary's miss list omits four misses that the ledger has;
   - "the knockout removed only their combination" (blog line 167): it also removed DNE on a derived ¬¬ (0.17 %);
   - "textbook problems use what K12 lacks": the strategies are rare in K12, not absent;
   - "173 minimal" includes 17 proofs that are minimal per conjunct only;
   - "59 of the 16,717 reductios" counts proofs, not reductios;
   - the blog does not name the model format and checkpoints (numbers.md does);
   - two different "term size" figures are given for DN examples;
   - `bot_case` is wrongly listed as never exercised;
   - one "shortest" search proof is 1 line longer than the generator's;
   - the STATUS DONE line says "(= σ)" and "≤ 2 %", and asserts the RL reading causally.

**Hygiene and unflagged deviations.**
- **textbook72-class sequents in fixtures.**
  - Nine textbook72 renaming classes are quoted in committed unit-test / self-test fixtures.
  - One of those files, `second_impl_fixtures_v1.2.jsonl` (3 classes), is also in the public bucket, twice
    (`data/ps/validation/`, `artifacts/ps/validation/`).
  - All nine classes already appear in public pre-run files, and `textbook72.jsonl` is itself public, so nothing new is
    exposed. Still, the brief says "never printed": replace the fixtures with non-sealed variants and re-upload, or note
    the exception. (This review's phase-1 commit had the same issue in its own unit tests, now fixed; see errata.)
- **Pre-registration deviations not flagged in `log.md`:** the σ-covered rule (item 1); the search sample, 1,000 → 990;
  the necessity sample, 600 by length and primary → 594 by length; the final DS tightening (47 → 43); and compute not
  recorded per step.
- **`Not.elim` in RL proofs.** The state-env writes Lean's `Not.elim` as a `BOTE` citing a negation in RL proofs (2 of
  2,114 sampled). The classifier counts it as ex falso; the effect is negligible.

**Not supported.** No claim lacks data once reworded as above. The blog's knockout reading ("pretraining supplied the
form, the models put it to work") is explicitly labelled untested and stays so; RL-time replay of σ (item 5) is a
confound it should name.

**Next measurements.**
- Hand-check the final v1.2 DS and LEM predicates blind, 20 each.
- Extend #10 to DN on a self-built ¬¬ box hypothesis (C7) and recount the 12 found files. One pass takes ≈ 20 min on
  the VPS.
- **Test the knockout reading in two ways:**
  - Compare per-attempt round-1 rates of free reductios (k = 32 attempts per target, from the ladder logs) between full
    and dose bases. Their pretraining holds 6 vs 2 free and 16,658 vs 1,545 template-only reductio proofs.
  - Run a full-arm ladder whose replay excludes σ records, to separate "form from pretraining" from "form re-supplied
    during RL".
