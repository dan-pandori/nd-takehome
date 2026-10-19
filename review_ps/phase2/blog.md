# Phase 2 sub-audit: `proof_strategies/blog.md` (branch `dan_proof-strategies` at 441de472), claim by claim

Auditor: read-only sub-auditor. Nothing under `/home/dan/work/proof-strategies` was modified.

**Sources.** Independent values come from the reviewer's phase-1 outputs (`review_ps/out/`: `summary_all.json`,
`labels_*.jsonl.gz`, `thm_*.jsonl.gz`, `rl_<arm>.json`, `rl_breakdown.json`, `necessity.json`, `spot_recount.json`,
`examples_check.json`, `k12_tb72_hits.json`, `rl_sigcov.log`). Every number below was printed by a script in
`phase2/scripts/`:
- `s1_summary.py`: per-set shares;
- `s2_rl.py`: RL per-round counts;
- `s3_bylen.py`: per-length counts;
- `s4_k12_records.py`: per-record K12 joins (reductio kinds, classical-only, the 990 re-proofs);
- `s5_lean_snippets.py`: Lean, textbook72 classes and K12 source for every snippet;
- `s6_best_instance.py`: figure 2;
- `s7_charles_overlap.py` / `s7b_which_file.py`: Charles classes, reporting counts and file names only.

Inherited create-or-elicit facts are taken from `run_create_or_elicit.md`, `numbers.md` §create-or-elicit and
`review_create-or-elicit.md`, and the "free" definition from `coe/coe_rounds.py`.

**Model behind every RL number below.** create-or-elicit's 9,560,832-parameter `best_model.ALiBiGPT` (6 × 384):
- format `lean_staten` (Lean proof-state environment), trained from scratch;
- trained on K12 (full s3–s5), K12⁻ (knockout s0–s5) or K12⁻ + 1 % σ (dose1 s0–s2);
- Stage 1 took 1,200 s on an A40; then 16 rounds of T1 expert iteration on A40 (k 32, T 0.8, 600 fine-tune steps,
  20,000 replay records per round from the arm's own pretraining set);
- round 1 is samples of the pretrained model;
- full s0–s2 are older (`trajectory` r1–r8 on A6000, then `rl-continue` r9–r16 on A40) and are not in the RL counts.

**Lean.** I used Lean 4.34.0 core. Each snippet was taken verbatim, `example` renamed to `theorem tbk`, run with
`#print axioms`, and accepted only with no error and axioms ⊆ {propext, Classical.choice, Quot.sound}. The harness
rejected all 3 negative controls I ran: an invalid `.1` projection on an `Or`, a bare `sorry` (`sorryAx`), and the
example term with its goal swapped to ¬R.

| # | blog line | claim (short quote) | independent value / evidence | verdict | note |
|---|---|---|---|---|---|
| 1 | 10 | "counts over data files, plus one section re-reading our models' proofs" | One RL section (R12-type counts); the rest are data counts | reproduces | |
| 2 | 11–12 | "AI agents checking 260 proofs by hand (two labels each) agreed with the classifier before their notes tightened two rules" | Spot-check against v1.1: uses 260 / 260, primary 260 / 260. Against the final v1.2 rules: uses 245 / 260 (disjunctive syllogism 10 / 20, excluded middle 15 / 20), primary 258 / 260 | reproduces, **IMPRECISE** | The sentence is true as written, but a reader cannot tell that the final #6 and #12 rules were never blind-checked, or that the blind labels disagree with them on 10 / 20 and 5 / 20 |
| 3 | 12 | "a program written from the definitions alone agrees on all 155,000 K12 proofs" | Second implementation v1.2 is identical on every K12 record (R2: uses, primary, →I / ∨E working). TAXONOMY §6 scope covers the #10 kinds and routes, DNE, cases, DS, ¬I, MT, LEM and primary | reproduces | "From the definitions alone" is documented (TAXONOMY §6), not independently verifiable |
| 4 | 15–16 | "Our small theorem provers are pretrained (trained from scratch…) on K12: 155,000 … proofs written by a program" | K12 = 155,000 generator proofs | reproduces, **IMPRECISE** (model label) | The size appears only at l. 175. Format (`lean_staten`) and checkpoints are never named. The knockout and dose models were pretrained on K12⁻ and its 1 % variant, not on K12 |
| 5 | 18–19 | "38 % split into cases where one case never uses its own assumption, so the split could be deleted" | `cases.redundant` 58,345 = 37.64 %. TAXONOMY #5 defines redundant as "a branch proves the goal without its case" | reproduces | |
| 6 | 20 | "Proof by contradiction, the move our knockout experiment removed (called σ there)" | #10 = 16,717; σ (DN citing a NEGI) = 16,703; knockout removed σ⁺ = 16,961 (= #10 ∪ #11 on_derived); create-or-elicit quotes "σ … 10.9 % of K12" | reproduces approximately | MINOR: #10 ≠ σ exactly (+14), and the knockout removed σ⁺ (+244) |
| 7 | 21 | "It appears in 10.8 % of proofs" | 16,717 / 155,000 = 10.79 % | reproduces | |
| 8 | 21–22 | "only 59 of those 16,717 … 'not G' do[es] more than clash at once with G or a stated 'not not G'" | 59 working. By kind: 48 neg_goal, 6 free, 5 scaffolded with a non-immediate route. None of the 59 has route `immediate`. Template-only: 16,658 | reproduces | |
| 9 | 22 | "none on a theorem that needs it" | 0 of the 59 are classical-only (G4ip) | reproduces | |
| 10 | 23 | "Textbook problems use what K12 lacks." (also section heading l. 121) | K12 has 3,330 working ¬I proofs (2.15 %) and 13,623 genuine case splits (8.79 %). Only working #10 (59), MT (76) and DS (43) are near-absent | **OVERSTATED** (minor) | "Lacks" fits three of the five rows |
| 11 | 23–24 | "In 187 textbook problems, 21 % use a working proof by contradiction (K12: 0.04 %)" | Charles 39 / 187 = 20.86 %; K12 59 = 0.038 % | reproduces | |
| 12 | 24 | "38 % a working proof of a negation (2 %)" | Charles working ¬I 71 / 187 = 37.97 % (all 71 users are working); K12 3,330 = 2.15 % | reproduces | |
| 13 | 24 | "12 % modus tollens (0.05 %)" | 22 / 187 = 11.76 %; K12 76 = 0.049 % | reproduces | |
| 14 | 26–27 | "The full … models thus saw the form …, almost never its use, and wrote working ones anyway" | K12: 16,717 with the form, 59 working (6 free). Full s3–s5 round 1: 76 / 32 / 52 working, 38 / 27 / 45 free | reproduces | Base (round-1) numbers given; the model label is incomplete (#4) |
| 15 | 27 | "the three we analysed wrote 27–45 *free* ones each … before any RL update" | Free working in round 1: full s3 38, s4 27, s5 45 | reproduces | |
| 16 | 28 | "and 5,915–22,013 more over 15 rounds of RL" | Free working r2–16: 22,013 / 7,886 / 5,915 | reproduces | |
| 17 | 34 | "Exactly one rule is classical: double-negation elimination" | spec: DN is the only classical rule | reproduces | |
| 18 | 35 | "Every proof can be written in Lean …; Lean decides what counts" | R7: all 9,115 rendered proofs accepted | reproduces | |
| 19 | 37–39 | Lean notation glossary (`h.elim`, `⟨a,b⟩`, `h.1`, `Or.inl/inr`, `have`, `¬A`, `False.elim`, `Classical.byContradiction`) | Consistent with how every snippet uses these | reproduces | |
| 20 | 41 | "K12 has about 14,100 proofs at each length from 2 to 12 lines" | 14,091 at each length 2–11; 14,090 at length 12 | reproduces | |
| 21 | 41–43 | "pretrained models on K12 (full) or on K12⁻ (knockout): K12 minus the 16,961 proofs with σ or a close variant, topped up to 155,000" | σ⁺ = 16,961. K12⁻: n = 155,000, #10 = 0, #11 on_derived = 0. create-or-elicit: "σ removed, refilled" | reproduces | MINOR: full s0–s2 were pretrained in `trajectory`, not by create-or-elicit |
| 22 | 44 | "expert iteration …: try each training problem 32 times, keep what Lean accepts, fine-tune, repeat" | create-or-elicit: k 32 per round, 600 fine-tune steps, **plus 20,000 replay records per round from the arm's own pretraining set** | k 32 reproduces; **IMPRECISE** | The replay is omitted. During RL the full arm keeps training on K12, including its σ templates, and the knockout arm does not. That bears on the l. 164 reading |
| 23 | 45 | "A *seed* is one trained model." | definition | – | |
| 24 | 52–53 | Direct reasoning 51 %; snippet `(h : P ∧ Q) : P := h.1` | 51.15 %. Lean: accepted, no axioms. Statement = K12 #132941 prompt (exact). textbook72 hits: 0 (4 keys) | reproduces | |
| 25 | 54–55 | ∧-introduction 33 %; snippet | 32.57 %. Lean ok, no axioms; K12 #95938 exact; textbook72 0 | reproduces | |
| 26 | 56–57 | Conditional proof 43 %; snippet | 42.95 %. Lean ok; K12 #55304 exact; textbook72 0 | reproduces | |
| 27 | 58–59 | ∨-introduction 44 % "(no classical step: 'not S' is given)" | 44.26 %. Lean ok, no axioms; K12 #16853 exact; textbook72 0 | reproduces | |
| 28 | 60–61 | Proof by cases 44 %; snippet | 44.16 %. Lean ok; K12 #42672 exact; textbook72 0 | reproduces | |
| 29 | 62–63 | Disjunctive syllogism 0.03 %; snippet | 43 = 0.028 % under the final v1.2 rule. v0 gives 372 = 0.24 %. The blind labels agree with the final rule on 10 / 20. Lean ok, no axioms; K12 #47528 exact; textbook72 0. This is the 8-line instance; the 7-line #139899 is in a textbook72 class | reproduces, **IMPRECISE** | The share rests on a rule tightened after the blind check and never re-checked (see #2, #64) |
| 30 | 64–65 | Proof of a negation 4.7 %; snippet proves ¬¬R by assuming ¬R | 4.74 %. Lean ok, no axioms; K12 #24177 exact; textbook72 0 | reproduces | |
| 31 | 66–67 | Modus tollens 0.05 %; snippet | 0.049 %. Lean ok, no axioms; K12 #43479 exact; textbook72 0 | reproduces | |
| 32 | 68–69 | Ex falso 8 %; snippet `(h1 : Q) (h2 : ¬Q) : R` | 8.04 %. Lean ok, no axioms; K12 #104971 exact; textbook72 0 | reproduces | Location note only: this sequent shares a renaming class, under the two uncurrying keys only, with one row of Charles's private `removed.jsonl` (not among the 187). It is the generic explosion law and the snippet comes from K12, so this is a coincidence and nothing was copied. No action needed |
| 33 | 70 | Proof by contradiction 10.8 % | 10.79 % | reproduces | |
| 34 | 71–72 | DNE "on a double negation the problem supplies", 3.1 %; snippet | 3.06 %. TAXONOMY #11 is DN on a premise, a hypothesis, or a derived ¬¬G in Sub. Lean ok, axioms {propext, Classical.choice, Quot.sound}; K12 #70566 exact; textbook72 0 | reproduces | |
| 35 | 73 | Excluded middle 0.03 % (example in EXAMPLES.md) | 47 = 0.030 % under v1.2 (v0: 99 = 0.06 %); blind labels agree with the final rule on 15 / 20 | reproduces | EXAMPLES.md's example is a textbook-schema search proof, because K12 has no clean instance. The blog does not show it |
| 36 | 74–75 | Lemma reuse 12 %; snippet | 11.71 %. Lean ok, no axioms; K12 #44059 exact; textbook72 0 | reproduces | |
| 37 | 50 | "examples are from K12 unless noted" | All 12 snippet statements equal their K12 record's prompt (premise order and formulas) | reproduces | |
| 38 | 77–78 | "Items 6 and 8 are (mostly) special cases of 5 and 7 … only 10 is classical" | TAXONOMY: every DS instance is an ∨E; MT is a NEGI with route `mt` (a #7, or inside a #10) or a contraposition →I | reproduces | |
| 39 | 82–85 | Fig. 1 `k12_mix.png`; "Grey: proofs in which every instance is idle (the 28 % and 38 % … count proofs with any idle step)" | File exists. Every printed value matches R3: 51.2, 44.3, 44.2 / 8.8, 42.9 / 20.8, 32.6, 11.7, 10.8 / 0.04, 8.0, 4.7 / 2.1, 3.1, 0.05, 0.03, 0.03. Grey = uses − working: ∨E 35.4 %, →I 22.1 %, consistent with the caption | reproduces | |
| 40 | 86 | "28 % of proofs assume something they never use (… 'if A then B' without using A)" | →I vacuous: 43,715 = 28.20 % | reproduces | |
| 41 | 87 | "38 % contain a case split in which one case ignores its own assumption" | 37.64 % | reproduces | |
| 42 | 88 | "24 % of the problems have contradictory premises" | 36,472 = 23.53 % (truth tables) | reproduces | |
| 43 | 90 | "Re-proving 990 K12 problems with a shortest-proof search shortens proofs by a third" | On the same 990 records: mean pruned lines 7.00 → 4.69 (× 0.670) | reproduces | |
| 44 | 90–91 | "removes the idle splits (35 % → 0; proof by cases 43 % → 6 %)" | Redundant ∨E 34.85 % → 0.00 %; cases 42.53 % → 6.06 % | reproduces | |
| 45 | 91–92 | "most unused assumptions stay (29 % → 23 %; a goal 'if A then B' with an irrelevant A forces one)" | Vacuous →I 29.09 % → 22.83 % (78 % of the rate kept) | numbers reproduce | MINOR: the "forces one" explanation is plausible (→I is the only way to introduce →) but not quantified |
| 46 | 92 | "the problems' contradictory premises get used more (6 % → 16 %)" | Ex falso from inconsistent premises: 5.86 % → 16.26 %. Same problems (24.44 % inconsistent in both) | reproduces | |
| 47 | 98 | Fig. 2 `reductio_kinds.png` (each proof by its best instance) | File exists. K12: n 16,717, working 59, non-vacuous template 8,687 (52.0 %), vacuous only 7,971 (47.7 %). Dose: n 1,550, working 5, 829 (53.5 %) and 716 (46.2 %). Law instances n 334, Charles 39 and textbook72 10, all working | reproduces | |
| 48 | 100 | "16,658 of the 16,717 proofs with a reductio contain only templates" | 16,658 | reproduces | |
| 49 | 101 | "Vacuous: the absurdity, usually from contradictory premises, never uses 'not G'" | 8,209 records with a vacuous instance; 7,300 (88.9 %) have inconsistent premises | reproduces | |
| 50 | 102–103 | "Supplied: 'not G' clashes at once with a 'not not G' the problem states" | Equals the taxonomy's `scaffolded` with an immediate route (¬¬G or ¬G → ⊥ in Sub) | reproduces (definition) | The blog's name "supplied" differs from the files' `scaffolded` |
| 51 | 104 | "Pointless: G had already been proved" | definition | reproduces | |
| 52 | 106 | "Each kind has an example in EXAMPLES.md" | `examples.json` #25–29: vacuous, pointless, scaffolded, neg_goal, free | reproduces | |
| 53 | 106–112 | "One of the 59 working ones" (Lean block) | K12 #131990: #10 working, kind `free`. Lean ok, axioms {propext, Classical.choice, Quot.sound}. Statement is exact; textbook72 0; Charles 0 | reproduces | |
| 54 | 114 | "It splits on the first premise: R contradicts 'not R', and the other case the second premise" | Matches the term | reproduces | |
| 55 | 114–115 | "all 59 working reductios are on theorems provable without the classical rule (48 prove a 'not')" | 0 / 59 classical-only; 48 neg_goal, all among the 59 | reproduces | |
| 56 | 117 | "K12's 6,238 classical-only theorems" | 6,238 (4.02 %) | reproduces | |
| 57 | 117–118 | "all state a double negation and were proved by eliminating it or by a template reductio" | Semantic double negation: 6,238 / 6,238. Literal ¬¬: 3,898; the other 2,340 carry (¬X → ⊥) instead. Proofs: 4,279 use #10, all template-only; 1,959 use #11 alone | proof part reproduces; **IMPRECISE** | "State a double negation" is true only if ¬X → ⊥ counts as ¬¬X, as it does in Lean. The blog never says so |
| 58 | 118–119 | "None is σ-covered (classical-only with no double negation anywhere, so that every proof needs a working reductio)" | Semantic rule: 0. create-or-elicit's own (literal, syntactic) rule: **2,340 (1.51 %)**, all through a (¬X → ⊥) subformula. Under the semantic reading the "every proof needs a working reductio" clause is right, since a scaffolded template suffices for those 2,340 | **IMPRECISE** (material) | The blog uses create-or-elicit's term with a different, unstated definition. The two agree on the RL pools (123), transfer (106), Charles (35) and textbook72 (16) |
| 59 | 124–125 | "187 problems from logic textbooks such as *forall x*, collected by … Charles, with his reference proofs (173 minimal ones found by search, 14 written by hand)" | 187 problems from 9 sources, 78 of them *forall x* editions. `min_lines_method`: whole search 154 + 2 (1,800 s) + conjunct split 17 = 173; hand proofs 14 (marked "not minimal") | reproduces | MINOR: 17 of the 173 are minimal per conjunct, not searched whole |
| 60 | 126 | "1,610 instances of textbook laws … from our RL training and evaluation pools" | 760 `la_rl_targets` + 850 `la_transfer` = 1,610 | reproduces | |
| 61 | 127 | "textbook72, 72 textbook problems held out from training and never printed" | 72. But R10 finds 9 textbook72 renaming classes in this run's committed test fixtures, and `data/bs/textbook72.jsonl` is tracked in the public fork | **OVERSTATED** (minor) | "Never printed" is literally false of the run's files. The blog itself prints none, as checked here (12 / 12 snippets: 0 hits) |
| 62 | 127 | "(6 K12 records match some up to renaming, premise order or currying)" | 6 under that equivalence (uncurried multiset key). 13 if duplicate premises collapse; 10 if ¬A is also uncurried | reproduces | MINOR: the count depends on the key |
| 63 | 129 | "our search found Lean-checked shortest proofs (for 58 of the 72)" | 58 / 72 textbook72 and 1,610 / 1,610 law instances; all accepted by the reviewer's harness (R7) | reproduces | "Shortest" means within 14 lines and minlen's formula space |
| 64 | 131 | Fig. 3 `k12_vs_textbooks.png`, right-hand ratios ×548, ×520, ×240, ×18, ×4 | File exists. Ratios recomputed as **Charles ÷ K12**: 20.86 / 0.038 = 548; 14.44 / 0.0277 = 520; 11.76 / 0.049 = 240; 37.97 / 2.15 = 18; 33.69 / 8.79 = 3.8. Points match R4 | reproduces | MINOR: the axis says "textbooks ÷ K12" while two textbook series are plotted. ×520 depends on the tightened DS rule (v0 K12 0.24 % gives ≈ ×60) |
| 65 | 135 | table: working proof by contradiction 21 % vs 0.04 % | 20.86 / 0.038 % | reproduces | |
| 66 | 136 | table: modus tollens 12 % vs 0.05 % | 11.76 / 0.049 % | reproduces | |
| 67 | 137 | table: disjunctive syllogism 14 % vs 0.03 % | 14.44 / 0.028 % (Charles is 14.44 % under v0 too; K12 v0 0.24 %) | reproduces | IMPRECISE as #29 |
| 68 | 138 | table: working proof of a negation 38 % vs 2 % | 37.97 / 2.15 % | reproduces | |
| 69 | 139 | table: genuine case analysis 34 % vs 9 % | 63 / 187 = 33.69 %; 13,623 = 8.79 % | reproduces | |
| 70 | 141 | "The law instances and textbook72 agree (they share some laws)" | Law instances / textbook72 (Charles): working #10 20.75 / 17.24 % (20.86); MT 10.43 / **3.45** % (11.76); DS **5.59 / 6.90** % (14.44); working ¬I 39.57 / 32.76 % (37.97); genuine ∨E 38.26 / 27.59 % (33.69) | **IMPRECISE** (minor) | They agree in direction, every row far above K12, but MT and DS run 2–3.5× below Charles. "Share some laws" cannot be checked without opening textbook72 |
| 71 | 142 | "19 % of the 187 textbook problems are σ-covered, against none in K12" | Charles 35 / 187 = 18.72 % (both rules). K12 0 (semantic) or 2,340 = 1.51 % (create-or-elicit's literal rule) | **IMPRECISE** (as #58) | |
| 72 | 143–144 | "Of the 124 textbook problems a bounded search could settle, 37 % need a negation introduction (¬I or a reductio) in every short proof; of a K12 sample, 3.7 %" | 124 / 187 have a free proof ≤ 12 lines (58 none, 5 time-outs). Requires NEGI: 46 / 124 = 37.10 %. K12 sample: 22 / 594 = 3.70 %. Flags recomputed from the stored search fields with 0 mismatches | reproduces | MINOR: the K12 sample is 594 stratified by length only; the pre-registration said 600 by length and primary. The blog does not say |
| 73 | 148 | "Create-or-elicit found that the classical *families* … need σ in pretraining" | create-or-elicit's pre-registered verdict "needs exposure": 6 / 6 vs 0 / 6, Boschloo p = 2.4 × 10⁻⁴ | reproduces (inherited, attributed) | |
| 74 | 149–150 | "a family was acquired (at least half its held-out σ-covered instances solved in 256 tries) on 6 of 6 full seeds (5 before RL)" | numbers.md: ≥ 50 % of strict held-out members, plain k 256, r16, full 6 / 6. review_create-or-elicit: 5 / 6 full bases already at the bar at pend (plain read; the guided read gives 6 / 6) | reproduces | Model label partial (l. 175 gives size only). Full s0–s2 come from older runs |
| 75 | 150 | "0 of 6 knockout seeds" | 0 / 6 | reproduces | |
| 76 | 150–151 | "3 of 3 seeds pretrained with σ at 1 % … (1 before RL; exploratory)" | Dose 3 / 3, Boschloo p 0.0033 (exploratory). Dose s1 has contraposition_conv at 17 / 18 at pend | reproduces | |
| 77 | 151 | "K12 holds 59 working reductios (6 free); the 1 % dose set holds 5 (2 free)" | K12 59 / 6; dose1 5 / 2 (other 3 neg_goal) | reproduces | |
| 78 | 151 | "and its seeds acquired families anyway" | Dose families at r16: s0 4, s1 2, s2 2 | reproduces | |
| 79 | 154 | "every distinct proof found by 12 of create-or-elicit's 15 RL runs (three are older)" | 12 ladders, 7,855,065 distinct proofs, 0 unparsable (R12); full s0–s2 not analysed | reproduces | |
| 80 | 155–156 | "free working reductios, the kind σ-covered problems need (positive goal, no double negation supplied)" | Logically right for ND proofs. With no ¬¬ in Sub, every DN step is #10. If all #10 steps were templates or neg_goal, the proof could be made intuitionistic, so at least one free one is needed. Data: on every ladder, σ-covered targets proved at all by r16 equal those proved with a working #10 (parent's `rl_sigcov`) | reproduces | **Open note for the parent:** in dose1_s0, 2 σ-covered targets were first proved in an *earlier round* than their first working-#10 proof. Those earlier Lean-accepted proofs carry no working reductio as decoded, perhaps a decoding artefact (`Not.elim`). Not resolvable here: the found files are not local and I have no network |
| 81 | 157–158 | "Round 1 (the pretrained models): the three full models wrote 38, 27 and 45, proving 17, 15 and 20 of the 123 σ-covered problems" | Free r1: 38 / 27 / 45. σ-covered targets proved in r1: 17 / 15 / 20 (any proof = with a working one). 123 = σ-covered RL training targets under both rules | reproduces | **IMPRECISE** (minor): the blog never says the 123 are the RL *training* pool's (of 4,495) |
| 82 | 159 | "Rounds 2–16: 22,013, 7,886 and 5,915 more; 78, 33 and 36 σ-covered problems by round 16" | 22,013 / 7,886 / 5,915; 78 / 33 / 36 | reproduces | |
| 83 | 159–160 | "Dose models: 13, 43 and 7, then 9,047–15,731" | Free r1: 13 / 43 / 7; r2–16: 15,731 / 9,920 / 9,047 | reproduces | |
| 84 | 161 | "Knockout models: none in round 1, then 0–32, proving at most 5 σ-covered problems" | Free r1: 0 on all six. r2–16: 0 / 32 / 2 / 1 / 0 / 12. σ-covered proved by r16: 0 / 5 / 1 / 0 / 0 / 2 (any proof) | reproduces | Round-1 working, non-free: 1 / 0 / 1 / 0 / 2 / 1 (correctly not called free) |
| 85 | 161–162 | "Their other working reductios mostly lean on a double negation the problem states" | Working r2–16: 358 / 399 / 772 / 169 / 72 / 375. Excluding free and neg_goal (113, ko_s2 only), 1,985 of 2,098 non-free (94.6 %) are scaffolded with a non-immediate route | reproduces | |
| 86 | 162 | "(Create-or-elicit's larger 'free' counts include templates.)" | create-or-elicit "free positive" r1–16: full 49,600 / 20,384 / 17,429 vs 22,051 / 7,913 / 5,960 here; knockout 0 / 34 / 4 / 1 / 2 / 16 vs 0 / 32 / 2 / 1 / 0 / 12. `coe_rounds.sigma_subtype` splits scaffold / free by the prompt only (vacuous and pointless not separated) | reproduces | MINOR: it also counts σ⁺ routes (`_impi`, `_other`) and classifies only the first derived-DN step, so templates are the main but not the only difference |
| 87 | 164 | "So pretraining supplied the *form* …, and the models put it to work" | Full: 27–45 free in r1, 5,915–22,013 after. Knockout: 0 in r1, 0–32 after. Hedged at l. 168 | causal reading, hedged | The full arm replayed 20,000 K12 records per RL round (#22), so the "form" kept being supplied during RL |
| 88 | 165 | "rarely before RL (0.15–0.27 % of the full models' proofs)" | Free / distinct in r1: 38 / 14,212 = 0.267 %, 27 / 18,463 = 0.146 %, 45 / 17,212 = 0.261 % | reproduces | |
| 89 | 165–166 | "more often in round 16 (1.2–3.9 % of that round's new proofs)" | 1,955 / 50,640 = 3.86 %, 707 / 51,988 = 1.36 %, 587 / 49,332 = 1.19 % | reproduces | These are shares of newly found distinct proofs, not of samples, as the blog says |
| 90 | 166 | "and where needed on 33–78 of the 123 σ-covered problems" | 78 / 33 / 36 | reproduces | |
| 91 | 166–167 | "Both arms saw both halves …, working proofs of a negation (2 % of each set) and eliminations of a stated double negation (3 %)" | Working ¬I: K12 2.15 %, K12⁻ 2.25 %. #11: K12 3.06 %, K12⁻ 3.29 % | reproduces | |
| 92 | 167 | "the knockout removed only their combination" | The knockout removed σ⁺ = #10 ∪ #11 on_derived. K12⁻ has 0 DN on a derived ¬¬G (K12: 260) | MINOR | |
| 93 | 168 | "This is our reading, not a tested result." | – | appropriate hedge | |
| 94 | 172–173 | "theorem-level checks guard against this (classical-only exactly, necessity within 12 lines)" | G4ip is exact. Necessity is bounded at 12 lines and minlen's formula space, with one bound artefact each in K12 and Charles (R6) | reproduces | |
| 95 | 174 | "'Working' means the assumption does logical work; for a reductio, more than a clash with G or a supplied 'not not G'" | Matches TAXONOMY: route ≠ vacuous; not pointless or scaffolded-immediate | reproduces | Defined only here, after first use at l. 21 and l. 24 |
| 96 | 175–176 | "15 models of one small architecture (9.6 million parameters): 6 full, 6 knockout, 3 dose; our RL counts use 12 (3 full, 6 knockout, 3 dose)" | 9,560,832 parameters; 6 / 6 / 3; 12 = full s3–s5, knockout s0–s5, dose1 s0–s2 | reproduces; **IMPRECISE** (model label) | Format (`lean_staten`, Lean proof-state), the seed identities, and the fact that RL proofs are Lean proofs decoded to ND before classification are never stated (policy: every model number names checkpoint, size, format, from scratch, training set) |
| 97 | all | 12 Lean snippets | 12 / 12 accepted by Lean 4.34.0 (10 with no axioms, 2 with {propext, Classical.choice, Quot.sound}). 12 / 12 statements equal the cited K12 prompts. 0 / 12 in a textbook72 class (premise-order, set, uncurried and ¬-uncurried keys). Each proves what its text says | reproduces | |
| 98 | all | terms defined at first use | Late definitions: "knockout" (l. 20, defined l. 41–43); "modus tollens" (l. 24, l. 66); "working" for ¬I (l. 24, l. 174). Never defined: "currying" (l. 127), "held-out" (l. 150), "a bounded search could settle" (l. 143) | MINOR | Everything else is defined at or before first use; "free" is announced as "defined below" |
| 99 | – | length | 1,999 words from the title on | – | |

## Summary of discrepancies

**No number in the blog is wrong.** All of the following reproduce exactly: every share, count, range and ratio, all
three figures, all twelve Lean snippets and every RL number. No item is WRONG.

### OVERSTATED

- **O1 (l. 23 and heading l. 121, minor): "Textbook problems use what K12 lacks".** K12 has 3,330 working proofs of a
  negation (2.15 %) and 13,623 genuine case splits (8.8 %). Only working reductios (59), modus tollens (76) and
  disjunctive syllogism (43) are near-absent.
  *Reword:* "Textbook problems lean on what is rare in K12"; heading "What textbooks use that K12 rarely does".
- **O2 (l. 127, minor): textbook72 "never printed".** This run's committed unit-test fixtures quote 9 textbook72
  renaming classes (R10), and the file is tracked in the public fork. The blog itself prints none: 0 hits in 12
  snippets.
  *Reword:* "held out from training and not shown here".

### IMPRECISE

- **I1 (l. 117–119, l. 142; the most material item): "None is σ-covered", "all state a double negation", "against
  none in K12".**
  - These hold only if ¬X → ⊥ counts as a double negation. That is Lean's own reading (¬¬X := ¬X → False), but the
    blog never states it.
  - Under create-or-elicit's own literal rule for the same term, K12 has 2,340 σ-covered theorems (1.51 %), all
    through a (¬X → ⊥) subformula.
  - Only 3,898 of the 6,238 classical-only theorems write ¬¬ literally.
  - The two rules agree on every RL, transfer and textbook set.
  - *Reword l. 118–119:* "None is σ-covered (classical-only with no double negation anywhere, counting ¬X → ⊥, which
    is ¬¬X in Lean; then every proof needs a working reductio). Under create-or-elicit's literal-¬¬ rule 2,340
    (1.5 %) are, all through a ¬X → ⊥ premise that supplies the double negation, so a template suffices."
  - *Reword l. 142:* "…against none in K12 (1.5 % under create-or-elicit's literal rule)."
- **I2 (l. 11–12): spot-check.**
  - The 260 / 260 agreement is against v1.1. The tightened final rules for disjunctive syllogism and excluded middle
    were never re-checked blind, and the blind labels agree with them on only 10 / 20 and 15 / 20 (245 / 260
    overall).
  - *Add:* "the two tightened rules were not re-checked blind (the blind labels agree with them on 10 / 20 and
    15 / 20)".
- **I3 (l. 44): expert iteration description omits replay.**
  - Each round also fine-tunes on 20,000 records replayed from the arm's own pretraining set. So the full arm keeps
    seeing K12's σ templates throughout RL; this matters for the l. 164 reading.
  - *Reword:* "…keep what Lean accepts, fine-tune on it together with 20,000 records replayed from the model's
    pretraining set, repeat."
- **I4 (l. 15, 26–28, 154–162, 175–176): model labels incomplete.**
  - The blog gives size (9.6 M, only at l. 175) and training sets. It never gives the format (`lean_staten`, Lean
    proof-state environment), the checkpoints (full s3–s5, knockout s0–s5, dose1 s0–s2; full s0–s2 older), or the
    fact that RL proofs are decoded to ND before classification.
  - *Add one line to the RL section:* "Models: create-or-elicit's 9.56 M-parameter ALiBiGPT provers in the Lean
    proof-state format (`lean_staten`), trained from scratch on K12 (full s3–s5), K12⁻ (knockout s0–s5) or K12⁻ + 1 % σ
    (dose1 s0–s2), then 16 rounds of T1 expert iteration on A40; their Lean proofs are decoded to natural deduction for
    classification."
- **I5 (l. 62, l. 137, Fig. 3): disjunctive syllogism depends on the post-check rule.**
  - K12's 0.03 % (and ×520) rests on the rule tightened after the blind check. The v0 rule gives 0.24 % (≈ ×60);
    Charles's 14.4 % is unchanged under either.
  - *Add:* "(0.24 % under the rule before the spot-check tightened it)".
- **I6 (l. 141): "the law instances and textbook72 agree".** They agree in direction only.
  - Modus tollens is 10.4 % and 3.4 %, and disjunctive syllogism 5.6 % and 6.9 %, against Charles's 12 % and 14 %.
  - *Reword:* "agree in direction (every row far above K12), with less modus tollens and disjunctive syllogism".
- **I7 (l. 158, l. 166): "the 123 σ-covered problems" is never identified.** *Reword:* "of the 123 σ-covered problems
  in the RL training pool (4,495 problems)".

### MINOR

- **l. 20:** #10 (16,717) is not exactly σ (16,703); the knockout removed σ⁺ (16,961), which create-or-elicit quotes
  as 10.9 %.
- **l. 167:** "removed only their combination". K12⁻ also lost every DN on a derived, supplied ¬¬G (260 K12 records).
- **l. 125:** 17 of the "173 minimal" reference proofs are minimal per conjunct only.
- **l. 127:** "6 K12 records" holds under the stated equivalence; there are 13 if duplicate premises collapse and 10
  if ¬A is uncurried.
- **Fig. 3:** the ratio label "textbooks ÷ K12" means Charles's 187 ÷ K12.
- **l. 91–92:** "a goal 'if A then B' with an irrelevant A forces one" is an explanation, not a measured share.
- **l. 162:** create-or-elicit's larger "free" counts also include σ⁺ routes, not only templates.
- **l. 143–144:** the K12 necessity sample is 594 stratified by length only (pre-registered: 600 by length and
  primary). This is unreported, but not a blog error.
- **l. 41–43:** full s0–s2 were pretrained in `trajectory`, not by create-or-elicit.
- **Terms not defined at first use:** knockout, modus tollens, working-¬I; never defined: currying, held-out, "settle".
- **Location only (privacy), l. 69:** the ex falso snippet's sequent (K12 #104971) shares a renaming class, under the
  two uncurrying keys only, with one row of Charles's private `removed.jsonl`. It is the generic explosion law, a
  coincidence; nothing was copied and no action is needed.

### Open for the parent

- **dose1_s0 anomaly (l. 119, l. 155–156).** `rl_sigcov` shows 2 σ-covered targets first proved in an earlier round
  than their first working-#10 proof.
  - The blog's claim that a free working reductio is what σ-covered problems need holds for ND proofs; I argue it
    above (row 80).
  - Those earlier Lean-accepted proofs, as decoded, carry none.
  - This is worth one look; a likely cause is the `Not.elim` → BOTE decoding.
  - It changes no blog number: by r16, proved = proved with a working #10 on every ladder.
