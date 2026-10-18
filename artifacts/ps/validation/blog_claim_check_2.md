# Claim check 2: `proof_strategies/blog.md` (revision committed in 51c71b73, 2026-10-18 21:13 UTC)

Second adversarial pass, sentence by sentence. Sources: `TABLES.md` (§ 11 = the recount), `artifacts/ps/rl_found.json`,
`rl_found.py`, `summary/*.json`, `tables.json`, `theorem_totals.txt`, `TAXONOMY.md`, `EXAMPLES.md`, `numbers.md`
(§ proof-strategies, § create-or-elicit), `run_create_or_elicit.md`, `log.md` 2026-10-18, plus `review_create-or-elicit.md`,
`state_ladder_ei.py`, `spot_compare.py`, `rl_mix.json` (for its per-kind split only) and the three figures.

Re-run or recomputed here:
- `blog_lean_check.py`: 13 / 13 snippets accepted (1 schematic skipped).
- Every snippet matches an EXAMPLES.md "shortest clean" K12 record, with hypotheses renamed: 132941, 95938, 55304, 16853,
  42672, 47528, 24177, 43479, 104971, 70566, 44059. The two reductio blocks are 108482 and 131990.
- The second implementation's final labels (`second_impl_v1.2final_k12.jsonl.gz`) against the current
  `labels/k12.jsonl.gz`. The current file was regenerated at 20:27, after that program's 20:18 comparison. Result: 0
  differences in uses, primary or any shared sub-type, on 155,000 / 155,000. The program's extra id
  `contradiction.sigma` is the 16,703 strict σ.
- All RL statements recomputed from `rl_found.json` (table at the end).
- `state_ladder_ei.py`:
  - found files hold every distinct (normalised) accepted target proof, uncapped, each with its first round;
  - T1 allocation is uniform, k 32 per target per round.

**Most important new findings:** N1 (the knockout did not remove "the classical step"); N2 (the short version and a
figure legend misdefine "working"); N3 (the knockout's 72–772 are mostly reductios that lean on a double negation the
problem states, and they clash with create-or-elicit's 1–34); N6, N7, N8. Among the first-pass items, #16 and #33 are only
partly fixed.

## (a) Status of the 37 first-pass findings

| # | status | note |
|---|---|---|
| 1 | FIXED | "AI agents … 260 / 260 (before their notes tightened two rules)" and "a program … agrees on all 155,000 K12 proofs". Re-verified against the current label file (0 differences). Residual scope note: N17. |
| 2 | FIXED | "(173 minimal ones found by search, 14 written by hand)"; caveat "a search's or Charles's". Residual: the third caveat still says "the minimal proofs we classified" (N13). |
| 3 | FIXED | "We labelled every proof with the strategies …"; "the K12 shares below overlap". |
| 4 | FIXED | "split into cases where one case never uses its own assumption, so the split could be deleted". |
| 5 | FIXED | "almost never does any work". |
| 6 | FIXED | "K12 minus the 16,961 proofs with σ or a close variant, topped up". |
| 7 | FIXED | "Textbook problems use what K12 lacks"; 21 / 0.04, 38 / 2 (working ¬I both sides), 12 / 0.05. |
| 8 | FIXED | "The full (non-knockout) models". |
| 9 | NO LONGER APPLIES | The rule count was dropped. |
| 10 | PARTLY | The glossary now covers `example`, `fun`, `.elim`, `⟨a, b⟩`, `h.1`, `Or.inl/inr`, `¬`, `False.elim`, `Classical.byContradiction`. Item 13's `have … := …;` is still unglossed. |
| 11 | FIXED | "about 14,100". |
| 12 | FIXED | `state_env_october` gone; pretraining, expert iteration / RL and seed are glossed. Residual: K12⁻ is never called "the knockout arm" where it is defined (N15). |
| 13 | NO LONGER APPLIES | "Primary" was dropped. |
| 14 | FIXED | Item 4: "No classical step here, since 'not S' is given". Item 12: "by contradiction; classical". |
| 15 | FIXED | "below, 'reductio' means 10". |
| 16 | PARTLY | "Grey: proofs in which every instance of the strategy is idle" and the blue legend are fixed. But the next two bullets (28 %, 38 %) count proofs with *any* idle instance, while the grey bars show 22.1 % (→I: 42.95 − 20.80) and 35.4 % (∨E: 44.16 − 8.79). A reader looking for 28 % and 38 % in the grey will not find them. Add "(at least one idle instance; the grey bars count proofs where every instance is idle)". |
| 17 | FIXED | Idle splits 35 % → 0; unused assumptions 29 % → 23 %; contradictory premises 6 % → 16 %. Also checked "a goal 'if A then B' … forces one": 215 of the 226 shortest proofs with an unused assumption have a →I at the root (the goal is an implication). |
| 18 | FIXED | "We sorted each proof by its best reductio"; legend relabelled. `figures.py` now ranks working > supplied/pointless > vacuous; K12 vacuous shows 48 % (= best kind). Residuals: the cap-6 row is never mentioned in the text, and the dose row comes before the dose is introduced. The blue legend misdefines "working" (N2). |
| 19 | FIXED | "usually from contradictory premises". |
| 20 | FIXED | "A common K12 instance, of the supplied kind (vacuous ones are as common)". By best kind: vacuous 48 %, supplied or pointless 52 %. |
| 21 | FIXED | Both cases described correctly; "all 59 … provable without the classical rule (48 prove a 'not')". |
| 22 | FIXED | "were all proved by double-negation elimination or a template reductio"; σ-covered defined with "so that every proof needs a working reductio". |
| 23 | FIXED | "collected by a colleague (Charles)". |
| 24 | FIXED | "from our RL training and held-out problem pools". |
| 25 | FIXED | "never train on or print"; "(for 58 of the 72)". Residual on "never train on": N11. |
| 26 | FIXED | Header "187 textbook problems". |
| 27 | FIXED | "(they share some laws)". |
| 28 | FIXED | "(half its held-out instances solved)", "(5 before RL)", "(exploratory)". Residuals in N12. |
| 29 | FIXED | Recounted from the found files: 76 / 32 / 52, exact; "the three full models we read". |
| 30 | FIXED | 26,450 / 9,082 / 6,951 = distinct working-reductio proofs first found in rounds 2–16 (verified). |
| 31 | FIXED | 0–2, then 72–772, verified. But these now look inconsistent with create-or-elicit's own count (N3). |
| 32 | FIXED | "rarely before RL (0.2–0.5 % …) and more often by round 16 (1.4–4.5 %)" verified. Wording: N5. |
| 33 | PARTLY | The dose set is now cited and both arms' ¬I is stated. But "close to a 'templates only' test" has lost its referent and is not supported (N6). The new sentence "the knockout removed the classical step" is wrong (N1). |
| 34 | FIXED (caveat only) | The caveat is right. The short version and the reductio figure legend repeat the old loose definition (N2). |
| 35 | FIXED | "15 models … 6 full, 6 knockout, 3 dose; our RL counts use 12". |
| 36 | NO LONGER APPLIES | Counts now come from the complete found files (every distinct proof), not the capped mixes. |
| 37 | FIXED | TABLES.md header and § 9 say v1.2. `tables.py` no longer hardcodes v1.1. |

## (b) New findings

**N1. WRONG.** "Both arms saw working proofs of a negation (2 % of each pretraining set): the knockout removed the classical
step, not refutation."
- *Problem:* K12⁻ still contains the classical rule. The post itself defines double-negation elimination as the one
  classical rule (setting; item 11), so a reader concludes that the knockout models never saw it.
- *Source:*
  - DNE on a double negation the problem supplies is in 5,102 K12⁻ proofs (3.29 %): on a premise 1,299, on an assumption
    3,819 (`summary/k12ko.json`; numbers.md § coe K12⁻: "DN 5,102 records (3.29 %)").
  - 2,094 K12⁻ classical-only theorems are proved by DNE alone (TABLES § 4).
  - What the knockout removed is the *combination*: σ⁺ = proof by contradiction ∪ DNE on a derived ¬¬ (TAXONOMY § 5).
  - The ¬I half is right: working ¬I is 2.15 % of K12 and 2.25 % of K12⁻.
- *Fix:* "Both arms saw both halves: working proofs of a negation (2 % of each set) and double-negation elimination on a
  double negation the problem states (3 %). The knockout removed only their combination."

**N2. WRONG (as worded).** Short version: "only 59 of those 16,717 use the assumption "not G" to reach a contradiction".
Same slip in the `reductio_kinds.png` legend: "working: at least one reductio uses ¬G to reach ⊥".
- *Problem:* The supplied and pointless templates also use "not G" to reach the contradiction, by an immediate clash. Only
  the vacuous kind never uses it. This contradicts the post's own caveat, which has it right ("more than a clash with G or
  a supplied 'not not G'"). In the figure, the orange "template" bar is defined by such a clash, so it overlaps the blue
  definition.
- *Source:*
  - K12 proofs with a scaffolded reductio: 7,693. With a pointless one: 1,082 (TABLES § 3).
  - The post's supplied example uses the assumption (`h1 a1`), and so does EXAMPLES' pointless example (`a1 h1`).
- *Fix:* "only 59 of those 16,717 use 'not G' for more than an immediate clash (with G itself, or with a 'not not G' the
  problem states)". Legend: "working: ¬G does more than clash at once with G or a supplied ¬¬G".

**N3. MISLEADING.** "**Knockout models**: 0–2, then 72–772, proving at most 5 σ-covered problems." and "Models without
the form wrote working reductios an order of magnitude less often."
- *Problem:* "Working" also covers two kinds that σ-covered problems cannot use: reductios that lean on a double negation
  the problem states (scaffolded, not immediate) and reductios whose goal is a negation. The knockout's 72–772 appear to be
  mostly these two kinds. A reader of both write-ups also sees 72–772 here and "1–34" in `run_create_or_elicit.md` for the
  same ladders, with nothing to reconcile them. `rl_found.json` has no per-kind split, so the post cannot show this yet.
- *Source:*
  - (i) The round-16 fine-tune samples (`rl_mix.json`) are capped at 4 per problem but are the only per-kind split. There,
    the knockout ladders' 74 working-reductio records include at most 23 with a free instance (0 / 17 / 1 / 0 / 0 / 5). The
    full ladders' 1,093 include 894 (556 / 170 / 168).
  - (ii) Create-or-elicit counts free positive reductio proofs over 16 rounds: 0 / 34 / 4 / 1 / 2 / 16 per knockout ladder,
    against 49,600 / 20,384 / 17,429 for full s3–s5 (numbers.md § coe Phase 1). `run_create_or_elicit.md` says "1–34
    proofs in 16 rounds; full ladders 17–50 thousand".
- *Fix:* Re-run `rl_found.py` keeping the kind (it already calls `analyse()`, so this is ≈ 12 min). Then add: "mostly
  leaning on a double negation the problem states; free ones 0–34 per knockout seed vs 17,000–50,000 per full seed
  (create-or-elicit's count)".

**N4. OK-BUT-NOTE.** "an order of magnitude less often".
- *Problem:* This understates the gap. It is a floor, not a typical value.
- *Source:*
  - Seed for seed, every full ladder's working share is at least 9.7× every knockout ladder's:
    - round 16: 1.39–4.47 % vs 0.012–0.143 %;
    - rounds 2–16: 1.14–4.08 % vs 0.011–0.110 %;
    - round 1: 0.17–0.53 % vs 0–0.013 %.
  - Arm means: about 33× (round 16) and 39× (rounds 2–16).
  - Counts, rounds 2–16: 9–367× (6,951–26,450 vs 72–772).
  - With N3 taken into account, the gap for free reductios is about three orders of magnitude.
- *Fix:* "10 to 300 times less often (about 35 times on average)".

**N5. OK-BUT-NOTE.** "rarely before RL (0.2–0.5 % of new proofs) and more often by round 16 (1.4–4.5 %)".
- *Problem:* The values are correct for the three full models, but there are three wording problems.
  - (a) "By round 16" reads as cumulative. The figures are for round 16 alone.
  - (b) "New proofs" is undefined. It means proofs not found in any earlier round, so round 16's denominator leaves out
    re-found proofs.
  - (c) "The models" comes right after the dose models are listed, but the ranges cover the full models only.
- *Source:*
  - Full models, round 1: 76 / 14,212, 32 / 18,463, 52 / 17,212 = 0.53 / 0.17 / 0.30 %.
  - Round 16 alone: 2,263 / 50,640, 805 / 51,988, 686 / 49,332 = 4.47 / 1.55 / 1.39 %.
  - Rounds 1–16 together: 4.00 / 1.37 / 1.12 %.
  - Dose models: round 1 0.04–0.33 %, round 16 1.88–2.58 %.
- *Fix:* "the full models … rarely before RL (0.2–0.5 % of their proofs) and more often in round 16 (1.4–4.5 % of the
  proofs first found that round)".

**N6. MISLEADING / UNDEFINED-TERM.** "in the 1 % dose set, 5 of 1,550, close to a "templates only" test, and its seeds
acquired families anyway."
- *Problem:*
  - (a) "A 'templates only' test" no longer refers to anything. The experiment the first draft proposed was cut.
  - (b) The dose set is no closer to "templates only" than K12 in proportion. What is smaller is the absolute number of
    working reductios (5 vs 59 in 155,000 proofs).
- *Source:* Working share among reductio proofs: dose set 5 / 1,550 = 0.32 %, K12 59 / 16,717 = 0.35 %.
- *Fix:* "the 1 % dose set holds only 5 working reductios (K12: 59), and its seeds acquired families anyway".

**N7. MISLEADING (wording).** "3 of 3 seeds with 1 % of σ put back (exploratory)".
- *Problem:* This reads as "1 % of the σ proofs put back", which would be about 170 proofs.
- *Source:* The dose set is K12⁻ with 1,550 refill records swapped for σ records. So σ is 1.0 % of the set, about 9 % of
  K12's 16,961 (numbers.md § coe Phase 3).
- *Fix:* "3 of 3 seeds pretrained with σ put back at 1 % of the set (K12: 10.8 %)".

**N8. MISLEADING (mild).** "We classified every distinct proof create-or-elicit's RL runs found".
- *Problem:* The caveat says 12, but this sentence, and "the three full models we read", do not say why.
- *Source:*
  - It is 12 of create-or-elicit's 15 ladders. Full s0–s2 were not read; they came from earlier runs (trajectory r1–r8,
    rl-continue r9–r16; numbers.md § coe Models).
  - Only proofs of the 4,495 training problems were classified (`found_16.jsonl`), not the held-out reads.
- *Fix:* "every distinct proof that 12 of create-or-elicit's 15 RL runs found for their training problems (the other three
  full runs came from an earlier experiment)".

**N9. OK-BUT-NOTE.** No denominator for "proving 17, 15 and 20 σ-covered problems", "78, 33 and 36 σ-covered problems by
round 16" or "at most 5 σ-covered problems".
- *Source:* All three are out of 123 σ-covered training problems (TABLES § 4, § 11). The values match create-or-elicit's
  independent counts exactly.
- *Fix:* Add "(of 123)" once.

**N10. OK-BUT-NOTE.** "the models put it to real use".
- *Problem:* By the post's own standard, a working reductio need not be a necessary one: K12's 59 are all avoidable. Only
  the σ-covered counts show necessary use.
- *Source:* σ-covered problems solved: 17–20 in round 1 and 33–78 by round 16, of 123. `rl_found.json` does not say how
  many of the 7,003–26,526 working-reductio proofs are on classical-only problems.
- *Fix:* "put it to work, and to necessary use on 33–78 of the 123 σ-covered problems".

**N11. OK-BUT-NOTE.** "textbook72, 72 textbook problems we never train on or print."
- *Problem:* K12, the pretraining set of both arms, holds a premise-reordered twin of one textbook72 theorem.
- *Source:* `textbook_3ed45280…`; `review_create-or-elicit.md` line 48: "textbook72 1 / 0 (the known … twin)". The
  peer-rl-review note that `rl_targets` holds schema instances of textbook72 laws was not re-verified here.
- *Fix:* "72 textbook problems held out from all training (one has a premise-reordered twin in K12)".

**N12. OK-BUT-NOTE.** "a family was acquired (half its held-out instances solved) on 6 of 6 full seeds (5 before RL), … and
3 of 3 seeds with 1 % of σ put back (exploratory)".
- *Problem:*
  - (a) The bar is *at least* half of the family's σ-covered held-out problems, solved within 256 attempts.
  - (b) "Before RL" is counted for the full seeds only. One dose seed was also at the bar before RL, although all three dose
    seeds acquired some family during RL.
- *Source:*
  - (a) numbers.md: "≥ 50 % of strict held-out members", plain k 256.
  - (b) Dose s1 had contraposition_conv at 17 / 18 at pend (numbers.md § Phase 3; `review_create-or-elicit.md` l. 366).
- *Fix:* "(at least half of its held-out σ-covered problems solved in 256 tries) … 3 of 3 dose seeds (1 before RL)".

**N13. OK-BUT-NOTE.** "The textbooks' own proofs might use other strategies than the minimal proofs we classified."
- *Problem:* 14 of Charles's 187 reference proofs are hand-written, not minimal, as the post says earlier.
- *Fix:* "than the proofs we classified (mostly minimal ones)".

**N14. UNSOURCED (mild).** "Every proof is also a proof in Lean, the proof checker that decides what counts."
- *Problem:* This is true of the ND→Lean translation by construction, but this run did not Lean-check K12's 155,000 proofs.
- *Source:*
  - This run checked 6,268 searched proofs, 30 canonical examples, a 587-proof renderer sample and the 13 snippets
    (TAXONOMY § 6).
  - Create-or-elicit checked K12⁻'s 16,961 refill records.
- *Fix:* "Every proof translates into a Lean proof", or cite the checks.

**N15. UNDEFINED-TERM.** Terms a reader outside logic or ML will trip on:
- (a) "G" first appears in the short version ("the assumption 'not G'") before it is defined. Gloss it at first use: "the
  goal G".
- (b) "¬I" in "a negation introduction (¬I or a reductio)" is never introduced. Item 7 lacks the symbol, though the figures
  use it.
- (c) "The schemata and textbook72 …": "schemata" is not introduced; the list says "instances of textbook laws".
- (d) K12⁻ is not called "the knockout arm" where it is defined, though "knockout" is used throughout.
- (e) `have … := …;` (item 13) is not in the Lean glossary (residual of #10).
- (f) Lesser: "held-out", "topped up", "modus ponens" (item 1), "decide" ("a bounded search could decide"), and "the
  examples are from K12" while item 12 points to an EXAMPLES.md example that comes from the pools.

**N16. OK-BUT-NOTE.** "**Much of K12 idles.**"
- *Problem:* The evidence is that 38 % of proofs contain one deletable case split, not that much of the data does nothing.
  A lay reader may take it as "most of the training set is useless".
- *Fix:* "Many K12 proofs contain steps that do no work."

**N17. OK-BUT-NOTE.** "AI agents applying the rules by hand agreed with the classifier on 260 / 260 proofs".
- *Problem:* The 260 / 260 is narrower than it sounds.
  - Each proof was compared on two labels: whether it uses the strategy it was sampled for, and its primary label
    (`spot_compare.py`). It was not compared on all 13 labels.
  - The 260 include textbook-schema proofs where K12 had too few positives (log 19:56).
- *Fix:* "on the sampled strategy and the main label of each of 260 proofs".

**N18. OK-BUT-NOTE.** "They produced 32–76 each in their first round of RL sampling and 6,951–26,450 over the next 15
rounds."
- *Problem:*
  - (a) "They" refers to "the full (non-knockout) models", which a reader takes as all 6 full seeds. The counts are for 3.
  - (b) Round 1 is called "RL sampling" here but "before RL" and "the pretrained models" later.
- *Fix:* "The three full models we analysed wrote 32–76 working ones before any RL update and 6,951–26,450 more over 15
  rounds of RL."

**N19. OK-BUT-NOTE.** "(we use those of *forall x: Calgary*, a free textbook)".
- *Problem:* Several names are not forall x's: "direct reasoning", "lemma reuse", "proof of a negation" (Bauer),
  "conditional proof" (Copi). TAXONOMY cites seven sources.
- *Fix:* "mostly those of forall x".

**N20. OK-BUT-NOTE (trivial).** "Items 6 and 8 are special cases of 5 and 7."
- *Problem:* Classical modus tollens sits inside a proof by contradiction (#10), not inside #7.
- *Source:* 9 of K12's 76 modus-tollens proofs contain a classical one (`mod_tollens.classical`; `second_impl_v1.2.md`).
- *Fix:* "mostly special cases", or leave as is.

### Notes on the sources (not the post)

- **S1.** `EXPECTATIONS.md` l. 51 and log 21:10 grade "round 16 ≥ 10 × round 1" as a hit on counts (29.8 / 25.2 / 13.2×).
  But round 16 has about 3× as many new proofs as round 1 (49k–52k vs 14k–18k). As shares of new proofs, the rise is only
  8.4 / 8.9 / 4.6×, under the bar. The post rightly uses shares; the ledger should say which quantity it graded.
- **S2.** `rl_found.py` silently drops proofs that `analyse()` cannot parse, and records no count of them. Its σ-covered
  counts match create-or-elicit's independent ones exactly (17 / 15 / 20 → 78 / 33 / 36; knockout 0 / 5 / 1 / 0 / 0 / 2),
  which supports the pipeline. Log the drop count, and add the per-kind split (N3).

## RL recount from `rl_found.json` (working-reductio proofs / new distinct proofs)

Internal check: reductio = working + template-only, every round, every ladder.

| ladder | round 1 | round 16 alone | rounds 2–16 | σ-covered: r1 → by r16 (of 123) |
|---|---|---|---|---|
| full_s3 | 76 / 14,212 (0.53 %) | 2,263 / 50,640 (4.47 %) | 26,450 / 648,404 (4.08 %) | 17 → 78 |
| full_s4 | 32 / 18,463 (0.17 %) | 805 / 51,988 (1.55 %) | 9,082 / 647,166 (1.40 %) | 15 → 33 |
| full_s5 | 52 / 17,212 (0.30 %) | 686 / 49,332 (1.39 %) | 6,951 / 607,197 (1.14 %) | 20 → 36 |
| dose1_s0 | 15 / 14,359 (0.10 %) | 1,633 / 63,289 (2.58 %) | 16,970 / 738,096 (2.30 %) | 2 → 69 |
| dose1_s1 | 45 / 13,649 (0.33 %) | 1,066 / 51,926 (2.05 %) | 11,057 / 627,454 (1.76 %) | 17 → 46 |
| dose1_s2 | 7 / 15,729 (0.04 %) | 950 / 50,404 (1.88 %) | 9,969 / 623,007 (1.60 %) | 2 → 41 |
| ko_s0 | 1 / 13,838 (0.007 %) | 38 / 48,992 (0.078 %) | 358 / 554,262 (0.065 %) | 0 → 0 |
| ko_s1 | 0 / 13,597 (0) | 32 / 48,413 (0.066 %) | 399 / 583,264 (0.068 %) | 0 → 5 |
| ko_s2 | 1 / 16,984 (0.006 %) | 84 / 58,772 (0.143 %) | 772 / 703,010 (0.110 %) | 0 → 1 |
| ko_s3 | 0 / 14,210 (0) | 27 / 50,878 (0.053 %) | 169 / 618,526 (0.027 %) | 0 → 0 |
| ko_s4 | 2 / 14,967 (0.013 %) | 6 / 50,865 (0.012 %) | 72 / 649,595 (0.011 %) | 0 → 0 |
| ko_s5 | 1 / 18,786 (0.005 %) | 49 / 52,675 (0.093 %) | 375 / 669,078 (0.056 %) | 0 → 2 |

Template-only share of reductio proofs, full: round 1 91–95 %, round 16 51–57 %.

## Verified correct

- **Short version:** 155,000; 38 % (37.64); 10.8 % (16,717); 59; "none on a theorem that needs it" (0 of 59 on
  classical-only); 187; 21 / 0.04, 38 / 2 (working ¬I 2.15), 12 / 0.05; 32–76; 6,951–26,450 over 15 rounds.
- **Setting:** DN is the only classical rule; about 14,100 per length (14,091 / 14,090); 16,961 = 16,717 + 244, refilled
  (138,039 kept); k 32; seed.
- **Field guide:** all 13 "uses" shares (51, 33, 43, 44, 44, 0.03, 4.7, 0.05, 8, 10.8, 3.1, 0.03, 12 %); the K12 record
  behind every snippet; item 11's "supplied" matches TAXONOMY #11; the Bauer reference.
- **K12 habits:** 28 % (28.20), 38 %, 24 % (23.53); 990; a third shorter (7.00 → 4.69); 35 % → 0; 43 % → 6 %;
  29 % → 23 %; 6 % → 16 %.
- **Reductio section:** 16,658 / 16,717; the three kinds; "vacuous as common" (48 % vs 52 % by best kind); 59; 48
  negative goals; 6,238 classical-only (4,279 template reductio + 1,959 DNE only); σ-covered 0.
- **Textbooks:** 173 + 14; 1,610 (760 + 760 + 90); 72 / 58; the gap table (20.9 / 0.04, 11.8 / 0.05, 14.4 / 0.03,
  38.0 / 2.15, 33.7 / 8.79); the same direction in the schemata and textbook72 on all five rows; 19 % (35 / 187); 124
  decided; 37 % (46 / 124); 3.7 % (22 / 594).
- **Knockout section:**
  - 16 rounds; 6 / 6 (5 at pend), 0 / 6, 3 / 3 exploratory (p 0.0033); 59 / 16,717; 5 / 1,550.
  - Every RL count in the post: 76 / 32 / 52, 17 / 15 / 20, 26,450 / 9,082 / 6,951, 78 / 33 / 36, 15 / 45 / 7,
    9,969–16,970, 0–2, 72–772, ≤ 5, 0.2–0.5 %, 1.4–4.5 %.
  - "2 % of each pretraining set" (2.15 %, 2.25 %).
- **Caveats:** classical-only exact (G4ip), necessity bound 12 lines; 15 = 6 + 6 + 3, 12 = 3 + 6 + 3; 9.6 M (9,560,832).
- **Figures:**
  - `k12_mix.png` matches the text's "every instance idle".
  - `reductio_kinds.png` is ranked by best instance (K12 52 / 48 %, working 59).
  - `k12_vs_textbooks.png` ratios ×548 / ×520 / ×240 / ×18 / ×4 are right.
