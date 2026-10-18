# Pre-registration — run `proof-strategies` (proposal 28: a taxonomy of the proof strategies in our pretraining data)

Written 2026-10-18 ≈ 18:50 UTC (committed right after), **before any pod exists for this run** and **before any strategy share has been
computed on any set**. Executor: agent:claude. Branch `dan_proof-strategies` (from `origin/dan_create-or-elicit`).
Brief: run brief `proof-strategies` (Dan, 2026-10-18). Policy: `AGENT_POLICY.md`. No model is trained or sampled.

**What I had seen when writing this.** The file formats (`spec.md`); the first K12 record; the field names of every
comparison set (textbook72: field names only, no theorem); Charles's release README and one `candidate_v0` row; the code
of `patterns.py`, `patterns2.py`, `coe/coe_sigma.py`, `intuit.py`, `necessity.py`, `minlen.py`. Known numbers carried in
from `create-or-elicit` (`numbers.md` § K12⁻; checker-independent, they are counts of proof steps): K12 σ (DN on a NEGI
line) 16,703 records, σ⁺ (DN on any derived line) 16,961, DN anywhere 21,274 (13.73 %), NEGI 15.21 %, classical-only
theorems 4.13 % (20,000-record G4ip sample); K12⁻ DN 3.29 %, NEGI 5.19 %.

## Question

Which proof strategies, under names a logician would recognise, do the proofs in our pretraining set K12 use, how
often, and how does that mix compare with textbook problems and our other sets? Deliverable: a semi-complete taxonomy
(≈ 10–20 strategies, finer variants as sub-types) with a checkable predicate for each, canonical examples, and shares.

## Data (no models)

| set | file (md5) | proofs classified |
|---|---|---|
| K12 (main) | `cap-horizon/data/kh/train_k12.jsonl.gz` → `data/ps/in/` (uncompressed md5 800b5486…), 155,000 | the generator proofs |
| cap-6 | `train_depth3_f0_a1.jsonl` (md5 29276f24…), 155,000 | generator proofs |
| K12⁻ | `create-or-elicit/data/coe/train_k12ko.jsonl.gz` (gz md5 6326ebdd…), 155,000 | generator proofs |
| RL targets / transfer | `data/ladder/rl_targets.jsonl` 4,495 (3,735 with a generator proof, 760 textbook-schema instances without), `data/ladder/transfer.jsonl` 2,285 (1,525 + 760) | generator proofs; schema instances get search proofs (below) |
| holdout250 | `data/bs/holdout250.jsonl` (160 + 90) | same |
| Charles's release | nd-rl `origin/charles/main` 297dcbdd, `data/textbook_problem/release_2026-10-02/`: 187 base problems (`candidate_v0` 87, `candidate_v1` 72, `batch3` 14, `hand_proved_14` 14) | their reference proofs (173 search-found minimal, 14 hand-written). The 225 derived rows are proof-surgery twins of these and are excluded. nd-rl is private: these files stay local (gitignored), only aggregates and row names are committed. |
| textbook72 | `data/bs/textbook72.jsonl` (scoring only; it holds no proofs) | search proofs (below). **Never printed**, never trained on. |

**Search proofs** for theorems without a proof: `minlen.Search` (bounded shortest-proof search, its restricted formula
space), bound 14 lines, 120 s per theorem; its internal `nd_verify` call is bypassed and **every found proof is checked by
Lean** (`nd2lean` + Lean core; Lean alone decides). Theorems without a Lean-accepted proof are reported as such and
excluded from proof-level shares (theorem-level labels still apply). Search proofs are shortest proofs, a different style
from generator proofs; to compare like with like I also search proofs for a K12 sample (1,000 records, stratified by length).

## Method

Classifier `proof_strategies/strategies.py`. Each ND proof is parsed (the parser of `nd_verify.verify`, which judges
nothing; `verify_text` is never called), dependency-pruned (`patterns.prune_lines`), and every predicate is evaluated on
the **pruned** proof; the written proof is classified too, to report strategies that occur only in dead lines.
Reiteration (R) is followed wherever a predicate looks at the line a rule cites ("origin").

### Taxonomy v0 (final definitions go to `proof_strategies/TAXONOMY.md`)

| # | strategy | standard name(s) | "uses" predicate (pruned proof) | classical? |
|---|---|---|---|---|
| 1 | Direct reasoning | forward chaining; modus ponens (→E), simplification (∧E) | an IMPE or ANDE line; sub-type *box-free proof*: no AS line at all | no |
| 2 | Conjunction introduction | ∧I, adjunction, "prove each conjunct" | an ANDI line | no |
| 3 | Conditional proof | →I, deduction theorem | an IMPI line; sub-types: vacuous discharge (hypothesis never cited), explosive conditional (box ends in ex falso), curried (box ends in IMPI), hypothetical syllogism (box ends in an →E chain from the hypothesis) | no |
| 4 | ∨-introduction | ∨I, addition | an ORI line; sub-types: at the root, inside a ∨E branch, feeding a ∨E | no |
| 5 | Proof by cases | ∨E, argument by cases | an ORE line; sub-types: derived disjunction (P1), nested (`patterns2.nested_ore`), constructive dilemma, trivial merge (X ∨ X), ∨I→∨E decoration, a case whose hypothesis is unused | no |
| 6 | Disjunctive syllogism | DS, modus tollendo ponens | an ORE line with exactly one *refuted* branch (its last line, after R, is BOTE whose ⊥ depends on the branch hypothesis) | no |
| 7 | Proof of a negation | ¬I; intuitionistic reductio (Bauer 2010: "proof of negation") | a NEGI line not consumed only by DN (i.e. not part of #10); sub-types: ¬¬-introduction, negated conjunction (`negi_ande_hyp`), negated disjunction, unused hypothesis | no |
| 8 | Modus tollens / contraposition | MT (modus tollendo tollens); contraposition | a NEGI box whose ⊥ is NEGE(B, ¬B) where one side is →E applied to the box hypothesis (directly; a chain is a sub-type) and the other side does not depend on the hypothesis; contraposition = an IMPI with hypothesis ¬B whose box ends in such an MT whose ¬B is that hypothesis | no |
| 9 | Ex falso | explosion, ex falso quodlibet, ⊥E | a BOTE line; sub-types by context (refuted case, explosive conditional, root, other) | no |
| 10 | **Proof by contradiction proper** | classical reductio ad absurdum (RAA), indirect proof (IP); **the knockout's σ** | a DN line whose cited line (after R) is a NEGI line (= σ strict ∪ σ chain); variant *built ¬¬*: DN on another derived line whose ¬¬G is not a subformula of the sequent (part of σ⁺) | **yes** |
| 11 | Double-negation elimination | DNE on a supplied ¬¬A | a DN line whose cited line (after R) is PR or AS, or a derived line whose ¬¬G is a subformula of the sequent | **yes** |
| 12 | Excluded middle | LEM, tertium non datur; cases on LEM | a derived line X ∨ ¬X (or ¬X ∨ X) whose derivation contains a DN step; sub-type: an ORE on it | **yes** |
| 13 | Lemma reuse | a lemma used twice (a shared derived line; a cut, in Gentzen's terms) | a line with rule ∉ {PR, AS, R} cited by ≥ 2 distinct later lines (R copies followed) | no |
| — | Trivial | the conclusion is a premise | primary only | no |

Relations fixed in advance: #10 = `coe_sigma` σ (strict ∪ chain) exactly; σ⁺ = #10 (incl. built-¬¬ variant) ∪ the
derived-line part of #11; `patterns.reductio` = σ strict; P1 `derived_ore` is a sub-type of #5. Every K12 count of #10
must reproduce 16,703 (consistency check, not a prediction).

**Primary label (one per proof), precedence rule.** Take the root = the last line, after R. By its rule:
DN → #10 if the DN is a #10 instance, else #11; ORE → #12 if the disjunction is a classical X ∨ ¬X, else #6 if exactly one
branch is refuted, else #5; NEGI → #8 if an MT instance, else #7; IMPI → #8 if a contraposition instance, else #3;
ORI → #4; ANDI → #2; BOTE → #9; IMPE / ANDE / NEGE → #1; PR → trivial. #13 is never primary. Anything else is
"unlabelled". A second, *curried* primary descends through root →I boxes first (the strategy of the curried sequent,
Charles's overlap rule: ⊢ A → B and A ⊢ B are one problem).

Refinement: v0 may change after it meets the data (new sub-types, tightened predicates). Every change is logged in
`log.md` with its reason and v0 counts stay in `TABLES.md` beside the final ones.

### Theorem level ("does the theorem require it?")

- Classical-only (G4ip, `intuit.py`) for every theorem of every set (a sample of ≥ 20,000 per 155,000-set if too slow).
- σ-covered = classical-only and no ¬¬ subformula anywhere in the sequent (create-or-elicit's definition): every proof
  must eliminate a double negation it built, i.e. use #10 or its built-¬¬ variant.
- Bounded necessity (`minlen` search space, bound 12, 60 s): does every proof within the bound need ∨E, NEGI (¬I or
  RAA), BOTE, DN? On 600 K12 theorems (stratified by length and primary) and all 187 textbook base problems within reach.

### Validation, examples, term size

- Spot-check: an independent subagent labels ≥ 20 proofs per strategy blind (random positives, random negatives and
  borderline cases); agreement reported per strategy. Second implementation: another subagent implements #10, #5 (with
  #6) and #8 from the written definitions only and recounts K12. Coverage: the unlabelled share, characterised.
- Canonical examples: per strategy the shortest clean K12 instance and one typical one, in ND and Lean (rendered,
  Lean-checked), with an English gloss. Guard: no example in a textbook72 renaming class, by `gen.canon_key` (nd-rl PR
  #26's `--sealed` method) **and** a premise-order-invariant key; matches are counted, never printed.
- Term size: lean_check's inference-node count, computed from the pruned ND proof by the documented per-rule weights,
  validated against `lean_check.py` on ≥ 300 sampled proofs.

## Expected results (falsifiable; K12, share of 155,000 records, pruned proofs)

- **E1 uses:** conditional proof 65–90 %; ∨-introduction 30–55 %; proof by cases 25–50 %; conjunction introduction
  30–55 %; ex falso 8–20 %; disjunctive syllogism 3–10 %; proof of a negation (#7) 4.4–7 %; modus tollens /
  contraposition 2–6 %; DNE (#11) 2.5–3.5 %; excluded middle < 0.5 %; lemma reuse 10–35 %; box-free proofs 3–12 %;
  vacuous discharge 15–40 % (the generator's lazy (Z > G) fallback).
- **E2 primary:** conditional proof 40–65 %; proof by contradiction 2–6 %; unlabelled < 1 %. Curried primary: proof by
  contradiction 5–9 %.
- **E3:** a strategy present only in dead lines (written but not pruned) in 5–20 % of records.
- **E4 K12⁻:** #10 = 0 exactly; #7 4–8 %; #11 2.5–3.5 %. **cap-6:** #10 3–10 %; nested cases < 2 %.
- **E5 textbooks (187 base problems):** classical-only 15–35 %; #10 uses 15–35 % (≥ 1.5 × K12's 10.8 %); vacuous discharge
  < 5 %; at least one strategy or sub-type has a textbook share ≥ 3 × K12's and ≥ 5 % absolute (candidates: excluded
  middle, proof by contradiction, modus tollens).
- **E6 theorem level:** of K12 records using #10, 20–40 % are classical-only theorems (most σ uses are optional); of
  K12's classical-only theorems, 50–90 % are proved with #10 rather than #11 alone. Shortest proofs of the 1,000-record
  K12 sample use #10 at less than half the generator proofs' rate.
- **E7 validation:** spot-check agreement ≥ 95 % (≥ 19 / 20) per strategy; second implementation ≥ 99.5 % per predicate on
  K12; term-size formula = lean_check on 100 % of the sample; canonical examples 100 % Lean-accepted.

## Budget, compute, stop rule

$20 / 40 pod-hours (`podbudget proof-strategies --set 40 20`). Planned spend **$0**: everything runs on the VPS with ≤ 2
worker processes. If the searches would take > 6 h there, they move to one pod, pre-registered in `log.md` first.
Compute recorded per step as VPS CPU-seconds (no GPU; registry rows only if a pod is used). Seeds / noise floor: not
applicable (no training or sampling). Stop: hard stop 2026-10-21 18:38 UTC; the taxonomy stops growing when the
unlabelled primary share is < 1 % and every strategy has ≥ 20 validated instances.
