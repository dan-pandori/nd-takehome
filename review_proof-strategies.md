# Review of run `proof-strategies` (reviewer, 2026-10-18)

Reviewer: agent:claude (role reviewer, a session separate from the executor). Run brief: nd-rl
`docs/proposals/claude-heavy/BRIEF_proof-strategies.md` (proposal 28). Pre-registration:
`preregistration/proof-strategies.md` (committed a30bc33b). Branch `dan_proof-strategies` at 441de472. Kit: `review_ps/`
(every number below is printed by a script there into `review_ps/out/`; nothing is hand-summed).

**Model labels.** The run trains and samples no model. Every number in §Recount is a property of a data file or of
proofs found by a bounded search (`minlen.Search`), except §R12. That section counts proofs that create-or-elicit's
models wrote: its 9.56 M ALiBiGPT `lean_staten` policies, trained from scratch on K12 (full), K12⁻ (knockout) or K12 + 1 % σ
(dose1), then run through 16 rounds of T1 expert iteration (A40), judged by Lean alone. Round 1 is samples of the pretrained model.

**Checker.** All Lean checks below use the reviewer's own harness (`review_ps/lean.py`): Lean 4.34.0 core with no imports.
A proof is accepted iff its theorem line has no error and `#print axioms` lists only {propext, Classical.choice,
Quot.sound}. ND proofs are rendered with my own ND→Lean renderer. `nd_verify` judges nothing here.

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
| K12 + 1 % σ (dose1) | `train_k12dose1.jsonl.gz` | 155,000 | gz md5 7433f6ac0564… | (README) ✓ |
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

- One pod, `ps-c0` (RTX 3090, used for CPU only): 0.1958 billed h, $0.10 (`~/podbudget.log`), 705 pod-seconds.
- The budget was registered (40 h / $20) at 18:23 and again at 18:52, before the pod was created at 19:16.
- Registry: 40 rows (`artifacts/proof-strategies/registry/`), per job J1–J6 (gpu_seconds 0, gen_tokens 0, train 0,
  lean_checks 1,610 / 58 / 990 / 2,880 / 514 / 216 = 6,268) plus the pod row. Everything else ran on the VPS.

## §Compare (phase 2)

(pending — written after §Recount was committed)
