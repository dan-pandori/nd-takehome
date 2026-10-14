# Phase-1 sub-audit: THE BLOG (marked -> clean equivalence)

- **Part:** blog. **Files:** MARKED `review_pc/marked/blog.md` (31 body *[review]* marks + 1 in the librarian header;
  `wc -w` 3,149 incl. front matter and header note) vs CLEAN `paper/blog.md` (`wc -w` 2,493 incl. front matter and the
  Lean block; under the 2,500 cap). Pre-review `review_pc/prereview/blog.md` used to see what each mark corrected.
- **Method:** claim map marked -> clean (Table A: one row per mark; Table B: every other marked claim that changed, moved
  or was dropped), reverse map clean -> marked (Table C: new claims/phrasings, each checked against the clean paper
  `paper/sections/*.tex` and data), a numeral-by-numeral check, the four required caveats, the librarian's blog items.
  Figures: md5 of all blog PNG/PDFs; only `blog_fig2_logp.{png,pdf}` changed; both PNGs viewed and pixel-diffed.
- **Counts:** 70 rows. **EQUIV 54, FIX? 9, MUST-FIX 1, MINOR 2, NOTE 4.**
- Only numerals that are new in the clean blog: 2.9 and 4.2 (data-backed, task 2). Only new referent: "106" in the
  power-sampling bullet (correct). No number changed value or referent otherwise.
- Not quoted anywhere below: the blog's example theorem or any family schema (task item 6).

Row legend: verdict per AUDITOR_COMMON. "verbatim" = mark removed, text unchanged.

## Table A: the 32 marks (M0 = librarian header; R1-R31 = the 31 body marks, in order)

| # | clean loc (blog.md:line) | marked (<= 30 words, quote) | clean (<= 30 words, quote) | numbers | strength | caveat | verdict |
|---|---|---|---|---|---|---|---|
| M0 | (removed) | header note "Reading copy (librarian ...). ... Each change is marked *[review]*. The corrections take it to 3,080 words" | removed | n/a | n/a | n/a | EQUIV (expected in a clean copy) |
| R1 | :15-16 | "one classical reasoning move *[review]* (a kind of proof by contradiction that weaker logics reject)" | verbatim | same | same | kept (B8 "classical move") | EQUIV |
| R2 | :16-17 | "every example of that move *[review]* and its close variants deleted" | verbatim | same | same | kept (P14 echo) | EQUIV |
| R3 | :20-21 | "learned a new family of classical theorems during RL *[review]* (a comparison we chose after seeing the data; the pre-registered test, 6 of 6 against 0 of 6, is mostly decided before RL)" | "learned a new family during RL (a comparison we chose after seeing the data; the pre-registered test, 6 of 6 against 0 of 6, is mostly decided before RL)" | same | same | kept (B1 post hoc label + pre-registered test) | EQUIV |
| R4 | :18-20 | "at least half of its unseen instances *[review]* that require the move, given 256 attempts each; a family is the set of instances of one classical law" | "A family is the set of instances of one classical law ...; a run learns it by proving at least half of the family's unseen instances that require the move, given 256 attempts each." | same | same | kept (P5 strict bar; B8 "family" now defined before first use) | EQUIV |
| R5 | short version dropped; content at :112-114 | "during RL they used it routinely on *[review]* problems that hand them a double negation ("not not"). RL rarely carried it over to the problems that require it." | §4: "every knockout run used σ or a variant on problems that supplied the double negation (thousands ...), and almost never the genuinely classical form" | same | weaker ("routinely" gone, librarian item) | kept (B5: "easy" not reintroduced) | EQUIV (moved to §4) |
| R6 | :24 | "In this small *[review]* model organism (a system we fully control), this form of RL amplified what pretraining had exposed" | "In this small model organism (a system we fully control), this form of RL learned classical families when pretraining had exposed the move" | same | mark: same (main clause: see C1) | kept (B8) | EQUIV (mark) |
| R7 | :21-23 (+ :25) | "Deleting a skill from pretraining kept this RL from learning it within 16 rounds, but putting 1% back *[review]* restored the learning (three runs; exploratory)." | "no run learned any family in 16 rounds, and putting it back into 1% of the data restored the learning in three runs of three (exploratory)" | same | same | kept (B5 "undid the deletion" not back; "exploratory", n = 3; 16-round scope also at :25) | EQUIV (merged with marked l.26-28) |
| R8 | :30 | "Reinforcement learning against a verifier *[review]* is now the standard way to improve reasoning models." | verbatim | n/a | same | n/a (B5) | EQUIV |
| R9 | :60-62 | "or asks you to prove a "not" statement; *[review]* that use is not the genuinely classical one." | "Using σ where a problem supplies a double negation, or asks for a "not" statement, is not genuinely classical." | n/a | same (next sentence: see C2) | kept (B5) | EQUIV |
| R10 | :86-87 | "(p = 0.012), *[review]* though the new-family count there is two of three against zero of six (p = 0.034)" | "(p = 0.012), though new families there are two of three against zero of six (p = 0.034)" | same | same | kept (B2 hardware-matched) | EQUIV |
| R11 | :93-97 | "*[review]* Checks. ... doubling them for ten models after 16 rounds moved each count by at most one theorem and changed no family result" | "Checks. ... Fresh evaluations of ten models after 16 rounds with standard and with doubled limits differed by at most one theorem per model and in no family result" | same (9%, ten, 16, one, 210,151) | paragraph kept; the C1 clause is weaker (see C3) | kept: missed pre-registered prediction, Lean re-checks, 210,151 distinct texts, million-try samples unchecked | EQUIV (mark); C3 |
| R12 | :101 | "We sampled each knockout model *[review]* (before any RL) 1.1 to 1.5 million times across the held-out theorems" | "Before RL, we sampled each knockout model 1.1 to 1.5 million times on the held-out theorems" | same | same | kept | EQUIV |
| R13 | :102 | "Five of six *[review]* (four, counting only family members) proved some of them" | verbatim | same | same | kept (P13 echo) | EQUIV |
| R14 | :105-108 | "only for plain sampling *[review]* at our usual sampling temperature (at a higher, more random setting, plain sampling did prove the one extra held-out theorem on this model and on one other; we had predicted ... five of the six" | "only for plain sampling at our usual temperature and for one way of turning RL's compute into a budget ... (section 5): at a higher, more random temperature, plain sampling proved the one extra held-out theorem on this model and on one other. We had predicted at least five of six would certify." | same | same | kept (P2: temperature scope; the higher-T proofs on two bases; the missed >= 5/6 expectation) | EQUIV (the colon now follows the budget clause; still reads as explaining the temperature scope) |
| R15 | :106-110 | "one way of counting the budget *[review]* (how many attempts RL's compute is worth; section 5). Our pre-registered rule could not have returned "created" ..." | "for one way of turning RL's compute into a budget of attempts (section 5) ... Our pre-registered rule could not have returned "created" ... none could be certified." | same (10,000) | same | kept (B8 "budget"; B2 rule) | EQUIV |
| R16 | :112 | "They practised it on *[review]* problems that hand them the double negation." | "They practised it where the double negation was given." | n/a | same | kept (B5) | EQUIV |
| R17 | :120 | "at most 3.5 *[review]* natural-log units lower, and may be higher" | verbatim | same | same | kept (B8) | EQUIV |
| R18 | :120-121 | "held-out theorem *[review]* (found by the three earlier full runs of section 5, not each model's own)" | verbatim | same | same | kept (B4 / P7) | EQUIV |
| R19 | :123-124 | "*[review]* The 1% dose models score −19 to −25, overlapping the full ones; the closest dose and knockout models are within 0.7 units of each other, yet one ... 58 ... the other 2." | "The 1% dose models score −19 to −25, overlapping the full ones, yet the closest dose and knockout models, within 0.7 units, went on to prove 58 and 2 of the 106." | same | same | kept (B4) | EQUIV |
| R20 | :128-129 (alt :126; PNG) | "[review] Drawn for 12 of the 15 runs, all but the three earlier full runs of section 5." | "for 12 of the 15 runs (all but section 5's three earlier full runs)" | same | same | kept (B6) | EQUIV |
| R21 | :133-134 | "early-stopped sample *[review]* (sampling on a theorem paused after its first success in each block of 1,024 tries)" | verbatim | same | same | kept (B8) | EQUIV |
| R22 | :135-137 | "*[review]* We had committed in advance to dropping the reading ... (at least 2 successes in 18,432 tries) if at most one of three named theorems ... passed that bar. Only one did" | verbatim | same | same | kept (B3) | EQUIV |
| R23 | **DROPPED** | "Seeding didn't help, at least briefly. One extra RL round seeded ... changed nothing measurable; in an earlier, smaller model *[review]* (3.2 million parameters, writing whole proofs, judged by an older checker)" | whole paragraph removed | dropped: 3.2 million (here) and the seeded-round null | n/a | DROPPED: the R23 older-checker caveat (B2 named this sentence, pre-review l.141-142) together with its host; the seeded-round null result goes with it | **MUST-FIX** (see Findings 1) |
| R24 | :143-144 | "On three earlier full-data runs *[review]* (three of the six in section 3, each base against its model after 8 RL rounds)" | verbatim | same | same | kept (B7) | EQUIV |
| R25 | :157-158 | "*[review]* Here, such a control (fine-tuning on replayed pretraining data alone) recovered 13% to 25% of RL's gain." | verbatim | same | same | kept (B2) | EQUIV |
| R26 | :162-163 | "Both helped the base model more than the RL model *[review]* (the same three runs as in section 5, before and after 8 RL rounds)" | "should help the base model more than the RL model. On section 5's three runs, before and after 8 RL rounds, it did." | same | same | kept (B7) | EQUIV |
| R27 | :166-167 | "For the RL model it was within ±3 theorems of plain sampling everywhere, *[review]* and it failed the test we had set in advance on the hardest problems (those neither model had solved)" | "for the RL model it stayed within ±3 theorems of plain sampling everywhere and failed the test we had set in advance on the hardest problems (those neither model had solved)" | same | same (paper 04_measurement:93-94 attaches the gate to the r8 sentence the same way) | kept (B2 MCTS gate) | EQUIV |
| R28 | :167-169 | "*[review]* But with guided redraws the base proves only 3, 4 and 1 of the 22, 21 and 14 theorems still counted as created at one of section 5's budgets." | verbatim | same | same | kept (B2) | EQUIV |
| R29 | :174 | "[review] "Hardest": theorems neither model had proved; "long": 100 theorems of 13–16 lines." | ""Long": 100 theorems of 13–16 lines." | same | same | "Hardest" definition dropped from the caption; it is still defined in the text at :167, four lines above the figure, and the PNG's x-axis shows "hardest" | MINOR |
| R30 | :181-182 | "in our earlier, smaller models *[review]* (3.2 million parameters, whole proofs, older checker; checkpoints since lost)" | verbatim | same | same | kept (B2 older checker) | EQUIV |
| R31 | :185-187 | "*[review]* Per family, only converse contraposition, ... passes our pre-registered "needs exposure" test; three more families, at 3 full runs against 0, stay undecided after correcting for six tests." | verbatim | same | same | kept (B2; power limits) | EQUIV |

## Table B: other marked claims that changed, moved or were dropped

| # | clean loc | marked (quote) | clean (quote) | numbers | strength | caveat | verdict |
|---|---|---|---|---|---|---|---|
| B-1 | :10-13 | "six training runs per main condition ... Some analyses here were added later and are labelled so." | "six runs per main condition ...; later analyses are labelled." | same | same | kept | EQUIV |
| B-2 | DROPPED (short version) | "The best proved 3 of 106 unseen classical theorems in any test, and 5 after we let it run longer." | none (§4 :132-133 keeps "the same five held-out theorems" at r20/r24; :82 gains 0 to 2) | dropped: 3 of 106 | n/a | n/a (a result, not a caveat) | NOTE |
| B-3 | :22-23 | "restored the learning on three runs out of three, in a smaller, exploratory comparison." | "restored the learning in three runs of three (exploratory)" | same | same | kept | EQUIV |
| B-4 | :23-24 | "were not completely unable to make it. Given about a million tries, most of them stumbled onto it a handful of times" | "Yet most models trained without the move could still make it, a handful of times in about a million tries." | same | same (qualifier attached) | kept (caveat c) | EQUIV |
| B-5 | :32-33 | "claims of absence need far more attempts or likelihood estimates" (Why it matters) | §1: ""the base can't" always means "can't within some number of attempts", and that number should be stated" | same (1,000; million) | same | "or likelihood estimates" dropped (a recommendation) | EQUIV |
| B-6 | :25-26 | "One caveat matters a lot: a closely related study found the opposite with another RL algorithm (GRPO), so our result may be specific to ours." | verbatim | n/a | same | kept | EQUIV |
| B-7 | DROPPED (§1) | how RL works; "Sample it 10 million times and you'll see about ten successes"; "You also can rarely retrain a frontier model ... A model organism ... lets us." | none | dropped: 10 million / ten (illustrative) | n/a | n/a ("model organism" still defined at :24) | EQUIV |
| B-8 | :37-41 | §2 model description, the example theorem sentence, "the proofs Lean accepts are added to its training data, and it is fine-tuned on them" | "is fine-tuned on the proofs Lean accepts" | same (9.6M, 155,000, 4,495, 32) | same | n/a (replay still stated at :90 and :183-184) | EQUIV |
| B-9 | :66-67 | "every proof using σ or a variant removed (16,961) ... though each became three to four times rarer" | "the 16,961 proofs ... replaced ... "Assume and refute" and "drop a double negation" still appear separately, 2.9 and 4.2 times more rarely" | changed: "three to four" -> 2.9 / 4.2 | same | n/a | FIX? (task 2; data-backed: `artifacts/coe/shape_k12_vs_ko.md` NEGI 0.1521/0.0519 = 2.93, DN 0.1373/0.0329 = 4.17; mapping matches clean intro:25-26) |
| B-10 | :70-71 | "We hold out 105 of their instances, plus one similar theorem, that can only be proved with a genuinely classical step, and never train on them." | "holding out 105 instances that only a genuinely classical step can prove, plus one similar theorem." | same | same | the restrictive clause now grammatically covers the 105 only (marked: all 106) | MINOR |
| B-11 | :77-78 | Fig. 1 caption ("Each line is one training run. The y-axis counts the 106 ...") | "Held-out classical theorems proved (of 106; 256 attempts each) by each run ..." | same | same | kept | EQUIV |
| B-12 | :80-87 | full bullet; statistics bullet | "Converse contraposition was already learned before RL on five of the six"; statistics punctuation only | same | same | kept ("pre-registered", "added afterwards") | EQUIV |
| B-13 | :90-91 | "One complication: RL also replays old pretraining data ..." | same, without "One complication:" | n/a | same | kept | EQUIV |
| B-14 | :112-117 | "123 training theorems that require such a step ... In a check added afterwards, three of the six runs did better than this arithmetic predicts" | "123 training theorems that need a genuinely classical step ... In a check added afterwards, three of the six runs did better than this predicts" | same (3,900; 123; 0.03) | same | kept ("added afterwards") | EQUIV |
| B-15 | :119-122 | "Because the model is small, we can compute ... the full models before RL give a median log-probability of −15 to −21, the knockout models −26 to −36" | "We can compute ... −15 to −21 for the full models before RL and −26 to −36 for the knockout models" | same | same | kept | EQUIV |
| B-16 | **DROPPED** | "During RL, one full run and one dose run moved strongly toward these proofs; the rest, from all three kinds of run, ended between 8 units lower and 4 units higher." | none | dropped: 8, 4 | n/a | DROPPED: the only text reading of Fig. 2's RL trajectories; the paper (05_results:208-212) keeps it ("the changes do not" separate the arms) | FIX? (see Findings 2) |
| B-17 | :128-129 | Fig. 2 caption "(higher = more likely; natural-log units) that each model writes the best known σ proof of a held-out classical theorem" | "(higher = more likely) of the best known σ proofs, from the end of pretraining through round 16" | same | same | "natural-log units" and "held-out" now only in the text (:119-121) | EQUIV |
| B-18 | :131-138 | knockout-s1 narrative ("kept writing more ...", "we let it run past the planned 16 rounds", "A first, early-stopped sample") | condensed ("wrote ever more", "past the planned 16", "An early-stopped sample") | same (9, 123, 24, 20, 1,024, 18,432, 2) | same | kept | EQUIV |
| B-19 | DROPPED | "Another knockout run whose model had proved three such theorems before RL learned none of them." | none | dropped: three | n/a | a member-level counter-observation to the elicitation reading; the paper (05_results:262-263, seed 4) keeps it but says single successes settle little | NOTE |
| B-20 | :142-144 | "calls anything the RL model solves and the base doesn't "created" ... as created by RL" | "calls anything only the RL model solves "created" ... as created" | same | same | n/a | EQUIV |
| B-21 | :146-148 | "Across five defensible conversions the count falls to between 14 and 34 per run, and only 14 to 21 count as created under all five." | "to 14 to 34 per run across five defensible ways of converting compute into attempts, and to 14 to 21 under all five" | same | same | kept (P3 "under all five") | EQUIV |
| B-22 | :148-149 | "On nine hand-picked theorem–run pairs sampled over a million times, four survive every control" | "Of nine theorem–run pairs chosen in advance by a fixed rule and sampled over a million times each, four survive every control" | same ("each" supported) | n/a (factual fix) | kept | FIX? (task 2; supported: clean 04_measurement:25-26 "pre-selected as the most reliable r8 proofs in each seed's strictest set and sampled 1.1--1.5 million times each") |
| B-23 | :153-154 | Fig. 3 caption "... crosses mark equal attempts (256), where 51–60 look "created"" | "... crosses: equal attempts (256)." | dropped from caption: 51–60 (still in text :144) | same | n/a | EQUIV |
| B-24 | :162-166 | "Guided redraws halved the gap ... though they use about twice the compute per attempt." | "Guided redraws ..., at about twice the compute per attempt, halved the gap between base and RL model on one held-out set." | same | same | kept (cost stated) | EQUIV |
| B-25 | :173-175 | Fig. 4 caption | condensed | same (8, 100, 13–16, 236–240, 250) | same | kept | EQUIV |
| B-26 | :180 | "Ours is the simplest kind." | "Ours fine-tunes on its own successes (rejection-sampling fine-tuning)." | n/a | n/a | n/a | FIX? (task 2; supported: clean 03_setup:22-24 "This is rejection-sampling fine-tuning ...", 08_limitations:17) |
| B-27 | :183-184 | "a variant that rewards coverage did about as well" | "a coverage-rewarding variant about as many" | n/a | same | n/a | EQUIV |
| B-28 | :190-192 | "Our implementation of "power sampling" ... found none of RL's new solves." | "... proved none of RL's new solves (two earlier full runs' bases) or of the 106 held-out classical theorems (two knockout bases)." | added: 106 (two knockout bases) | same (sampler scope kept, :193) | kept (caveat b) | FIX? (task 2; labels correct, see section 5 below) |
| B-29 | DROPPED (§8) | "GRPO and more exploratory RL from the knockout models. ... a 0.1% dose. More runs, for the single-family tests." | none | dropped: 0.1% | n/a | n/a (future work; the power limit stays in §7) | NOTE |
| B-30 | :195 | "Code, data and model checkpoints are in public repositories" | "Code, data and checkpoints are public" | n/a | same | n/a | EQUIV |
| B-31 | whole file | cross-references ("section 3/4/5/6"; §8 heading) | no dangling references: every "section N" cited (3, 4, 5, 6) exists; nothing cites the removed §8 | n/a | n/a | n/a | EQUIV |
| B-32 | :88, :101-104 | dose bullet; rare-success sentences (6.7 million, guided 4 of 6) | verbatim | same | same | kept | EQUIV |

## Table C: reverse map (clean claims or phrasings not in the marked blog)

| # | clean loc | marked (quote) | clean (quote) | numbers | strength | caveat | verdict |
|---|---|---|---|---|---|---|---|
| C1 | :24-25 | "this form of RL amplified what pretraining had exposed, and did not, within 16 rounds, learn the classical families without it." | "this form of RL learned classical families when pretraining had exposed the move, and did not, within 16 rounds, learn them without it." | same | weaker (the "amplified" mechanism is gone; describes the post hoc 5/6, labelled four lines earlier, and the exploratory 3/3) | kept (16 rounds, "this form of RL", organism) | FIX? (echo of the librarian's abstract item; the clean abstract says "seeds pretrained with the composition acquired classical families"; the blog credits RL, which the during-RL result supports) |
| C2 | :61-62 | "That step, or a roundabout variant of it, is the only way to prove the theorems we test." | "and only it, or a roundabout route to the same effect, proves the theorems we test." | n/a | weaker (admits the lemma route) | n/a | FIX? (task 2; supported: clean 01_intro:105 "the composition, a variant or the lemma route"; 03_setup:68) |
| C3 | :93-94 | "doubling them for ten models after 16 rounds moved each count by at most one theorem and changed no family result" | "Fresh evaluations of ten models after 16 rounds with standard and with doubled limits differed by at most one theorem per model and in no family result" | same | weaker (no causal effect of doubling) | kept | FIX? (P1 echo; outside the B list; supported: clean 05_results:360-363 and 11_checks:5-13. "Fresh" carries P1's independent-draws point; "±1 = sampling" is not spelled out) |
| C4 | :126; `figures/blog_fig2_logp.png` (+ .pdf) | alt "How likely each model is to write the classical proofs, along RL"; PNG title "How likely each model is to write known σ proofs" | alt "Log-probability of known σ proofs along RL, 12 of 15 runs"; title "How likely 12 of the 15 runs are to write known σ proofs" | same | same | kept (B6) | FIX? (task 2; correct: the pixel diff is confined to the title band, box (302,20)-(946,44); 12 lines = 3 full + 3 dose + 6 knockout; the PDF title matches) |
| C5 | :162-163 | "making the *base* model try harder at test time should recover part of RL's gain" | "extra compute at test time should help the base model more than the RL model" | n/a | same | n/a | EQUIV (matches clean 04_measurement:84-85) |
| C6 | :19-20 vs :61-62 | n/a | R4 keeps "unseen instances that require the move" while C2 now admits other routes | n/a | n/a | n/a | NOTE (consistent enough in the blog's simplified usage; changing R4 would alter a review correction) |

Rows: A 32 + B 32 + C 6 = 70.

## 3. Numbers (clean -> marked)

I extracted every numeral in the clean blog (script over `paper/blog.md`) and checked each against the marked text and
its referent. All are in the marked blog with the same referent, except:
- **2.9 and 4.2** (:67): new. "Assume and refute" = negation introduction = 2.93x, "drop a double negation" = DN =
  4.17x (`artifacts/coe/shape_k12_vs_ko.md` l.11-12). The order is correct. Task-2 fix, data-backed.
- **106** in the power-sampling bullet (:191): new referent, correct (`p2_ko_s0_*`/`p2_ko_s1_*`: n_theorems 106,
  solved 0 for alpha 2 and 4).
- Number-words also checked: "two earlier full runs' bases" and "two knockout bases" (section 5 below); "each" in
  "over a million times each" (paper 04_measurement:26: 1.1-1.5 M each); "three runs of three"; "five of six (four ...)";
  "12 of the 15 runs"; "3, 4 and 1 of the 22, 21 and 14". All the same as the marked text or supported.
- **Dropped numbers:** 3 of 106 and "5 after we let it run longer" (B-2; the five survive in §4); 8 lower / 4 higher
  (B-16); "three such theorems" (B-19); the seeded-round paragraph (R23); 10 million / ten (B-7, illustrative); 51–60 in
  Fig. 3's caption (B-23, still in the text); 0.1% (B-29, future work).
- Moved, unchanged: "within 0.7 units ... 58 and 2 of the 106" (dose s0 and knockout s1; the order is kept).

## 4. The four caveats the brief requires

- **(a) "Needs exposure" only within 16 rounds of this EI: KEPT.**
  - :21-22 "Without it, no run learned any family in 16 rounds".
  - :24-25 "In this small model organism ..., this form of RL learned classical families when pretraining had exposed
    the move, and did not, within 16 rounds, learn them without it."
  - :25-26 "so our result may be specific to ours".
  - :180 "One RL algorithm, 16 rounds."; :185-187 only converse contraposition "passes our pre-registered "needs
    exposure" test".
  - The qualifiers "within 16 rounds", "this form of RL" and "in this small model organism" all survive. The marked
    "Why it matters" restatement ("kept this RL from learning it within 16 rounds") is merged into :21-25.
- **(b) The sharpening null is specific to our sampler: KEPT.** :190-193 "A null we can't interpret. Our
  implementation of "power sampling" ... proved none of RL's new solves (...) or of the 106 ... It also did worse than
  plain sampling on theorems the base solves rarely, so we count it as a failure of our sampler." "Our implementation",
  "can't interpret" and "a failure of our sampler" are kept; the model labels added are correct.
- **(c) Rare, not absent: KEPT.**
  - :23-24 "Yet most models trained without the move could still make it, a handful of times in about a million tries."
  - §4 heading ""Absent" is not quite right" and :101-110, with "(four, counting only family members)", "almost all in
    one family", "one in 6.7 million", guided 4 of 6, and the certificate's limits (plain sampling, usual temperature,
    one budget, higher-temperature successes, the missed 5-of-6 prediction, "none could be certified").
  - Lost: the short version's "RL rarely carried it over to the problems that require it". Its content is in §4
    (:113-117).
- **(d) Power limits: KEPT.**
  - :185-187 "Enough for the main comparison, not for most single-family tests ... three more families, at 3 full runs
    against 0, stay undecided after correcting for six tests".
  - :10-11 run counts; :23 "three runs of three (exploratory)"; :86-87 hardware-matched 2/3 vs 0/6 (p = 0.034);
    :109-110 "at about 10,000 attempts per theorem none could be certified".
  - Lost: only the §8 future-work line "More runs, for the single-family tests".

## 5. The librarian's blog items (task 2)

- **J9 "hand-picked": FIXED, correct.** :148 now reads "chosen in advance by a fixed rule and sampled over a million
  times each". Clean (and marked) 04_measurement:25-26 say "9 (theorem, seed) pairs pre-selected as the most reliable r8
  proofs in each seed's strictest set and sampled 1.1--1.5 million times each".
- **"Ours is the simplest kind": FIXED, supported.** :180 now reads "Ours fine-tunes on its own successes
  (rejection-sampling fine-tuning)". Paper 03_setup:22-24 and 08_limitations:17 say the same.
- **"routinely": REMOVED.** The short-version sentence is gone, and §4 (:112-114) has no "routinely".
- **Power-sampling paragraph now names models: CORRECT.** :191-192 "(two earlier full runs' bases)" and "(two knockout
  bases)".
  - `artifacts/coe/power/p2_full_s{0,1}_a{2,4}.json`: `ckpt` = `ckpts/coe/old/stage1_best12_s0_b1200.pt` and
    `..._s1_b1200.pt`. These are the bases of earlier full runs s0 and s1, two of section 5's three earlier full runs.
    n_theorems 33 and 27, solved 0.
  - `p2_ko_s{0,1}_a{2,4}.json`: `ckpt` = `ckpts/coe/stage1_ko_s0.pt` and `stage1_ko_s1.pt`. n_theorems 106, solved 0.
  - Clean 05_results:333-335 says the same ("none of the theorems RL r8 proves beyond the base's reach (0/33, 0/27), and
    none of the 106 strict theorems for knockout bases s0 and s1"), and 08_limitations:66 names "full s0 and s1".
  - The positive control (`p2b_pc_*`, full s0 base) is still described without a model, as in the marked text; that is
    fine.
- **Fig. 2 alt text and PNG title "each model": FIXED.**
  - Alt text (:126): "Log-probability of known σ proofs along RL, 12 of 15 runs".
  - PNG title: "How likely 12 of the 15 runs are to write known σ proofs". The PDF title is the same.
  - Axes ("log-probability of the classical proof (median over theorems, nats)", "RL round", ticks from before RL to
    16), the line labels (full/dose/knockout) and all 12 trajectories are pixel-identical; only the title band differs.
  - The caption ("for 12 of the 15 runs (all but section 5's three earlier full runs)") matches the 3 blue + 3 green +
    6 orange lines.

## Findings

**MUST-FIX**

1. **The "Seeding didn't help" paragraph is gone, together with review mark R23** (marked blog.md l.171-173; clean: no
   counterpart; the cut falls between clean :138 and :140).
   - What was lost: "One extra RL round seeded with one of these rare proofs changed nothing measurable", plus the
     *[review]* older-checker caveat on the earlier-organism contrast. B2 named that sentence (pre-review l.141-142).
   - The caveat would be moot without its host, but the host is a negative result that the paper still carries. Clean
     05_results:323-331 reports seeded minus control +0, +0, +2, +0, +0. Clean 10_appendix:152 records a missed
     pre-registered expectation: "a seeded-round gain on ≥ 3 seeds (observed 1/5)".
   - B2's complaint was that the blog dropped negative results the paper carries, so this cut recreates a B2-type gap.
     It is not wordiness.
   - Fix: restore one sentence, e.g. "One extra RL round seeded with one of these rare proofs changed nothing
     measurable (an earlier 3.2M whole-proof organism, under an older checker, had responded within a round)."
   - If the reviewer reads "no caveat dropped" as covering only caveats whose claim survives, this drops to FIX?.

**FIX?** (all except 2 are task-2 changes I could check; all are supported)

2. **B-16, :123-124: a likelihood result was dropped without a mark.** The dropped sentence: "During RL, one full run
   and one dose run moved strongly toward these proofs; the rest, from all three kinds of run, ended between 8 units
   lower and 4 units higher."
   - The paper keeps it (05_results:208-212): full s3 +10.2, dose s0 +16.6, others +1.6 to +4.2, knockout −7.5 to
     +3.7, "the levels separate ... the changes do not".
   - It is the blog's only reading of Fig. 2's RL trajectories, and it cuts against an "RL amplifies exposed models"
     reading.
   - It was not a reviewed caveat, so it is not MUST-FIX by rule, but I recommend restoring one clause.
3. **C1, :24-25:** "amplified what pretraining had exposed" became "learned classical families when pretraining had
   exposed the move". It is weaker (no mechanism) and supported by the labelled post hoc 5/6 and the exploratory 3/3.
4. **C2, :61-62:** "roundabout variant of it" became "roundabout route to the same effect" (lemma route). Supported
   (01_intro:105).
5. **C3, :93-94 (P1 echo):** "doubling ... moved each count by at most one" became "Fresh evaluations ... with standard
   and with doubled limits differed by at most one theorem per model". Supported (05_results:360-363). Optional: add
   "(sampling noise, not the limit)".
6. **B-9, :67:** "three to four times rarer" became "2.9 and 4.2 times". Data-backed and in the right order.
7. **B-22, :148:** "hand-picked" became "chosen in advance by a fixed rule ... each". Supported (04_measurement:25-26).
8. **B-26, :180:** "simplest kind" became "rejection-sampling fine-tuning". Supported.
9. **B-28, :190-192:** the power-sampling models are named and correct (old full s0/s1 bases; knockout s0/s1 bases).
   The new 106-theorem null is supported.
10. **C4:** the Fig. 2 alt text and PNG/PDF title now say 12 of 15 runs. Correct; the data are unchanged.

**MINOR**

- R29 (:174): the Fig. 4 caption no longer defines "Hardest", which is an x-axis label in the PNG. It is defined in the
  text at :167.
- B-10 (:70-71): "that only a genuinely classical step can prove" now attaches to the 105 only, not to the extra
  106th theorem.

**NOTE**

- B-2: "best proved 3 of 106 in any test" dropped.
- B-19: "Another knockout run ... learned none of them" dropped. The paper says such single successes settle little.
- B-29: §8 "What's next" dropped.
- C6: R4's "instances that require the move" sits beside the widened C2. Acceptable.
- All 31 marks except R23 survive with their meaning, and every B1-B8 item and the P2/P5/P13/P14 echoes are intact.
- No claim got stronger. No model label was lost: B7 at :143-144 and :163; B4 at :121; B6 at :129.
- No post hoc, exploratory or pre-registered label was lost (:20-21, :23, :84, :116, :135, :186).
