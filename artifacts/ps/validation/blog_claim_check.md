# Claim check: `proof_strategies/blog.md` (draft of 2026-10-18)

Adversarial check of every number and factual claim, sentence by sentence. Sources: `TABLES.md`, `artifacts/ps/summary/*.json`,
`artifacts/ps/rl_mix.json`, `theorem_totals.txt`, `tables.json`, `TAXONOMY.md`, `EXAMPLES.md` / `examples.json`, `numbers.md`
(§ proof-strategies, § create-or-elicit), `log.md` (2026-10-18), `run_create_or_elicit.md`. Extra evidence: `review_create-or-elicit.md`,
`state_ladder_ei.py`, `spec.md`, `spot_compare_v1.2.json`, and read-only views of create-or-elicit's ladder `args.json` / `round_*.json`
(`~/work/create-or-elicit/artifacts/coe/ladder/`). Ad-hoc recounts were run on `artifacts/ps/labels/k12.jsonl.gz`, `artifacts/ps/theorem/k12.jsonl.gz`
and the `artifacts/ps/scratch/mix_*` files. `blog_lean_check.py` was re-run: 13 / 13 snippets accepted.

**Most important:** #30, #31 (the RL counts come from capped, cumulative training mixes, not from "what the models wrote after
15 rounds"), #17 ("removes all of this" is false for two of the three habits), #24, #1, #7, #29, #21, #2.

## Findings (in the post's order)

1. **MISLEADING.** "a blind hand-check of 260 proofs and a second program … agree with the classifier on every strategy label".
   (a) Three AI subagents did the "hand-check" (TAXONOMY §6, log 19:56). People did not. (b) The 260 / 260 is against the **v1.1**
   labels. The checkers' notes then changed disjunctive syllogism and excluded middle (v1.2). Against the published v1.2 labels the
   same hand labels agree on 245 / 260 "uses" (DS 10 / 20, LEM 15 / 20) and 258 / 260 primary (`spot_compare_v1.2.json`;
   numbers.md also says "(v1.1)"). Only the second program checked the v1.2 DS and LEM definitions. (c) The second program agreed
   on K12 and the 1,610 schema proofs only. **Fix:** "a blind check of 260 proofs by three AI agents applying the written
   definitions (260 / 260 before their notes tightened two definitions) and an independently written program (every label, all
   155,000 K12 and 1,610 schema proofs, final definitions)".
2. **WRONG (minor).** "uses short proofs found by a search program" and "Charles's reference proofs (minimal proofs found by
   search)". Of the 187 reference proofs, 173 were found by search and 14 were written by hand (TABLES.md header; pre-registration
   data table). The hand-written ones are 20–102 lines long, and Charles's MANIFEST marks 4 of the 14 `lean_not_rendered`. The
   caveat "a search's for the textbook problems" has the same slip. **Fix:** "(173 minimal proofs found by search, 14 written by
   hand)".
3. **MISLEADING (mild).** "We sorted every proof into thirteen strategies" and "The thirteen, with their shares of K12". These are
   not a partition. A proof gets every strategy it uses, and the 13 shares add up to 254 %. **Fix:** "We labelled every proof with
   the strategies it uses (a proof can use several)". Say the field-guide shares are "uses".
4. **OK-BUT-NOTE.** "38 % of proofs contain a case split that one of its cases never needed". The 37.64 % is right, but the wording
   is garbled. **Fix:** "a case split in which one case never uses its own assumption, so the split could be deleted".
5. **MISLEADING.** Headline: "… (called σ there) does no work in K12". The next sentence says 59 proofs do work. **Fix:** "almost
   never does any work in K12".
6. **MISLEADING (minor).** "That move is proof by contradiction. It appears in 10.8 % of K12 proofs" and "knockout models were
   pretrained on K12 minus every proof containing σ". The knockout actually removed σ⁺: 16,961 proofs, 10.9 %, which is the figure
   `run_create_or_elicit.md` quotes for σ. That is the 16,717 proofs by contradiction plus 244 that eliminate a double negation
   built some other way. The set was then refilled to 155,000 with σ-free generator proofs (numbers.md § K12⁻: 138,039 kept +
   16,961 refill; TAXONOMY §5; review_create-or-elicit §1). **Fix:** one clause, e.g. "the knockout removed 16,961 proofs (the
   16,717 proofs by contradiction and 244 close relatives) and refilled the set with other generated proofs".
7. **MISLEADING.** "Textbook problems need exactly what K12 lacks … proof of a negation in 38 % (2 %), and modus tollens in 12 %".
   (a) These are shares of reference proofs that *use* a strategy. "Need" is supported only for proof by contradiction (19 % of the
   problems are σ-covered) and for negation introduction (37 % of decided problems in the bounded search). Nothing tests whether a
   problem needs modus tollens, which is a special case of ¬I. (b) The K12 "2 %" is *working* ¬I (2.15 %). K12 *uses* ¬I in 4.74 %,
   and the field guide prints 4.7 %, so the pair compares a uses share with a working share. **Fix:** "Textbook problems use what
   K12 lacks: a working proof by contradiction in about 20 % of 187 textbook problems (K12: 0.04 %), a working proof of a negation
   in 38 % (2 %), modus tollens in 12 % (0.05 %)."
8. **MISLEADING (wording).** "So the knockout's full models were pretrained on the form …". This is easily read as "the knockout
   models", which saw no reductio at all. **Fix:** "the full (non-knockout) models".
9. **OK-BUT-NOTE.** "Our system has fourteen rules". `spec.md` lists "the 15 rule names" (PR, AS, R, ANDI, ANDE1/2, IMPE, IMPI,
   ORI1/2, ORE, NEGE, NEGI, BOTE, DN). The count is 14 only if PR is left out. **Fix:** "fifteen rules (counting premise and
   assumption lines)", or drop the number.
10. **UNDEFINED-TERM.** The Lean glossary covers `fun`, `.elim`, `¬` and `False`. The snippets also use: the `example (h : A) : B :=`
    statement form, `h.1` / `c.2`, `⟨_, _⟩`, `Or.inl` / `Or.inr`, `False.elim`, `have … := …;` and `Classical.byContradiction`.
    The last one appears in item 11 but is explained only in the next section. **Fix:** extend the glossary sentence, e.g. "`⟨a, b⟩`
    proves an 'and' from both halves, `h.1` takes its first half, `Or.inl` / `Or.inr` prove the left / right side of an 'or',
    `False.elim` is ex falso, `Classical.byContradiction` is the classical step".
11. **OK-BUT-NOTE (trivial).** "14,091 generated proofs at each length from 2 to 12". Length 12 has 14,090 (TABLES §6). **Fix:**
    "about 14,100".
12. **UNDEFINED-TERM.** `state_env_october` is an internal model name, and "arm", "pretraining / pretrained", "seeds" (§ knockout)
    are not glossed. "RL" is only expanded. Here it means expert iteration: 32 attempts per problem, keep the Lean-accepted proofs,
    fine-tune on them plus 20,000 pretraining records, 16 rounds (numbers.md coe "Models"). **Fix:** drop `state_env_october`
    ("our current prover"). Add one clause each for pretraining, RL as used here, and seed (an independently trained copy).
13. **OK-BUT-NOTE.** "its *primary* strategy is the one that takes the last step". It is defined but never used again in the post.
    Drop it.
14. **MISLEADING (mild).** Item 4's example proves `S ∨ ¬S` with no classical step, since ¬S is given. Item 12 glosses excluded
    middle as "prove 'X or not X', classical". EXAMPLES.md flags this ("excluded middle's shape without its classical content"), but
    the post drops the flag. **Fix:** gloss #12 as "prove 'X or not X' by contradiction, with nothing given about X", and add the
    EXAMPLES remark to item 4, or use the other ∨I example.
15. **UNDEFINED-TERM.** "both are often called 'reductio'". After this, "reductio" means only item 10: "16,717 proofs with a
    reductio", "working reductios", "¬I or a reductio". **Fix:** "Below, 'reductio' means item 10."
16. **MISLEADING (mild).** "The grey parts are instances that do no logical work" plus the bullets "28 %" and "38 %". The grey bar
    is *proofs* using the strategy with no working instance: →I 22.1 %, ∨E 35.4 % (`figures.py`; recomputed). The bullets count
    proofs with at least one idle instance (28.2 %, 37.6 %), so a reader sees 22 vs 28 and 35 vs 38. The blue legend "does logical
    work" also covers strategies whose idle uses were never measured (∨I, ex falso, DNE). **Fix:** "Grey: proofs in which every
    instance is idle". Note that the bullets count proofs with any idle instance. Make the blue label "not split" for untested
    strategies.
17. **WRONG.** "Re-proving 990 K12 problems with a shortest-proof search removes all of this." Only the idle splits go: 34.8 % → 0.0 %
    on these 990. Unused assumptions remain: →I vacuous 29.1 % → 22.8 %, mostly forced by goals "if A then B" whose A is irrelevant.
    Contradictory premises belong to the problems, so re-proving cannot remove them, and the shortest proofs use them *more*: ex
    falso from inconsistent premises 5.9 % → 16.3 % (TABLES §8; `tables.json` like_for_like). **Fix:** "… removes the idle splits
    (35 % → 0) but not the unused assumptions (29 % → 23 %, mostly forced by the goal). The contradictory premises belong to the
    problems, and shortest proofs exploit them more (6 % → 16 %)."
18. **MISLEADING (mild) / UNDEFINED-TERM.** "We sorted every instance by whether the assumption does any work:" and figure
    `reductio_kinds.png`. (a) The figure sorts *proofs*, not instances. (b) Its legend calls only supplied + pointless "template"
    and shows vacuous separately, while the text counts all three kinds as templates. (c) The axis says "by the best reductio they
    contain", but the code ranks vacuous above template: K12 vacuous is 49.1 % that way vs 47.7 % by best kind
    (`sigma_instances_k12.txt`). (d) It shows rows the post never introduces: "cap-6", "RL targets, generator", "transfer,
    generator". **Fix:** say "proofs", relabel the legend ("template: supplied or pointless" / "template: vacuous"), and drop or
    explain the extra rows.
19. **OK-BUT-NOTE.** "Vacuous: the absurdity comes from contradictory premises". This holds for 7,300 of the 8,209 K12 proofs with a
    vacuous reductio (89 %). In the rest, ⊥ comes from other open assumptions. **Fix:** "usually from contradictory premises".
20. **OK-BUT-NOTE.** "The typical K12 instance". In EXAMPLES.md "typical" means the median-length example. The supplied kind it shows
    is not the commonest: instances are vacuous 8,356, supplied (scaffolded, immediate) 7,887, pointless 1,098
    (`sigma_instances_k12.txt`). **Fix:** "A common K12 instance (the 'supplied' kind; 'vacuous' is as common)".
21. **WRONG (description) + missing point.** "To prove R, it assumes 'not R' and checks both cases of the first premise against it."
    Only the case R is refuted by "not R". The case ¬R ∨ ¬S is refuted by the second premise h2, without using "not R"; the
    EXAMPLES.md gloss of record 131990 says this correctly. Also, this theorem has a proof with no classical step (case split on h1,
    the second case is explosion). That is true of every working K12 reductio. My recount: 0 of the 59 working-reductio records are
    on classical-only theorems, 48 of the 59 have a negated goal, and 5 of the 6 "free" ones have contradictory premises.
    **Fix:** "… and refutes both cases of the first premise: R against 'not R', the other against the second premise. Even this is
    avoidable: all 59 working reductios in K12 are on theorems provable without the classical rule."
22. **OK-BUT-NOTE (reasoning gap).** "Every one of them states a double negation somewhere. So no K12 theorem needs a working proof by
    contradiction." Having a double negation somewhere in a problem does not, by itself, make a working reductio avoidable. The
    conclusion does hold, for another reason: none of the 59 working reductios is on a classical-only theorem. So each of the 6,238
    has a generator proof that uses only DNE (1,959) or a template reductio (4,279; TABLES §4), and every template can be replaced.
    Also "Create-or-elicit called the theorems that do need one σ-covered": σ-covered (classical-only, no double negation in the
    problem) is sufficient for needing one, not a definition. **Fix:** add "and the generator proved each of them with DNE or a
    template". Write "σ-covered: classical-only with no double negation anywhere, so every proof needs a working one."
23. **UNDEFINED-TERM.** "Charles's reference proofs". The reader does not know Charles. **Fix:** "a colleague's (Charles's) set of
    187 problems taken from logic textbooks such as *forall x*".
24. **WRONG.** "1,610 instances of textbook laws … from the pools RL trains on". Only 760 are in `rl_targets`, which is trained on.
    The other 760 are in `transfer` and 90 in `holdout250`, both held-out evaluation pools (log 19:15 J1; numbers.md § comparison
    sets). **Fix:** "from the problem pools of our RL experiments (training and held-out)".
25. **OK-BUT-NOTE.** "textbook72, a sealed test set, counted but never printed" and "The last two got shortest proofs". The search
    found proofs for 58 of the 72 (TABLES §2), so textbook72's proof shares are over 58. "Sealed" is a scoring discipline only:
    `data/bs/textbook72.jsonl` sits in the public fork (paper-clean review). **Fix:** "a test set of 72 textbook problems that we
    never train on or print (58 got a search proof)".
26. **MISLEADING (mild).** Gap-table column "textbooks". The column is Charles's 187 only (20.9 / 11.8 / 14.4 / 38.0 / 33.7 %). The
    schemata and textbook72 differ, e.g. DS 5.6 % and 6.9 %, MT 10.4 % and 3.4 %. **Fix:** header "187 textbook problems (Charles)".
27. **OK-BUT-NOTE.** "The textbook schemata and textbook72 show the same pattern." The direction holds on all five rows, but the sets
    are not independent. The peer-rl-review review found `rl_targets` holds 400 schema instances of 10 textbook72 theorems (not
    re-verified here). **Fix:** "… show the same pattern (they share some laws)".
28. **OK-BUT-NOTE / UNDEFINED-TERM.** "After 16 rounds of RL, families were acquired on 6 of 6 full seeds, 0 of 6 knockout seeds,
    and 3 of 3 seeds with 1 % of σ put back." The numbers are correct (numbers.md coe Phase 1 / Phase 3). Three gaps: (a) "acquired"
    is undefined; it means at least half of the family's held-out problems solved at 256 attempts. (b) 5 of the 6 full seeds already
    had one family (contraposition) at the bar before any RL: "the primary indicator is decided before RL starts"
    (review_create-or-elicit §3). This supports "needs σ in pretraining", but "after RL" invites a causal reading. (c) The dose
    comparison was exploratory (p = 0.003, not pre-registered). **Fix:** "By the end of RL (16 rounds), at least one family
    (≥ half its held-out problems solved) on 6 / 6 full seeds — 5 of them before RL — 0 / 6 knockout, 3 / 3 dose (exploratory)".
29. **MISLEADING.** "Before any RL update, the three new full models wrote 67, 29 and 48 distinct working reductios." (a) "New" is
    unexplained: the full arm had 6 seeds, and the other 3 came from an earlier run whose mixes were not read. (b) The counts come
    from the round-1 fine-tune mix. That mix keeps at most 4 distinct proofs per problem: 10,361 of the 14,212 distinct accepted
    proofs for full s3 and 11,544 of 18,463 for s4 (coe `round_1.json`; mix histograms). So 67 / 29 / 48 are lower bounds. The
    σ-covered counts (17 / 15 / 20) are exact. **Fix:** "the three full models trained in that experiment wrote at least 67, 29 and
    48 …".
30. **WRONG.** "After 15 rounds of RL, they wrote 690, 199 and 204." The round-16 mix is not round 16's output. It is built from the
    *cumulative* pool of distinct accepted proofs from rounds 1–16, at most 4 per problem: `state_ladder_ei.py` "fine-tune on the
    accumulated target proofs (<= --max_per_thm per theorem)"; coe `args.json` max_per_thm 4, rl_weight 4. At round 16, 4,429 of
    4,430 solved problems are at the cap, and the mix holds 17,718 of the ≈ 662,600 distinct proofs full s3 found over 16 rounds
    (≈ 2.7 %). Each full mix_16 shares 339–392 proofs with its mix_1. So 690 / 199 / 204 are counts in a ≈ 3 % per-problem sample of
    everything found in rounds 1–16. Create-or-elicit counts 17,000–50,000 free reductio proofs per full ladder, under a looser
    definition that includes vacuous ones. **Fix:** compare shares of the mix, not counts: "working reductios were 3.9 %, 1.1 % and
    1.2 % of the round-16 training mix (four proofs per problem from all rounds so far) vs 0.65 %, 0.25 % and 0.43 % in round 1". Or
    recount from the bucket's `found_16.jsonl`, which carries each proof's round.
31. **WRONG (the "0") / MISLEADING.** "Knockout models wrote at most one before RL, and 0 to 22 after." These are the same capped,
    cumulative samples. The 0 is knockout s4. Its round-1 working reductio is in its pool, but it was not drawn into the round-16
    mix: that problem's 4 slots went to other proofs (checked on `mix_ko_s4_{1,16}`). Create-or-elicit counts 2 free reductios for
    s4 (first in r15) and 0 / 34 / 4 / 1 / 2 / 16 for s0–s5 over 16 rounds (numbers.md coe Phase 1; review §5). **Fix:** "at most one
    in the round-1 training mix and 0–22 in the round-16 mix; over all 16 rounds, 0–34 per seed (create-or-elicit's count)".
32. **OK-BUT-NOTE.** "rarely at first and routinely after RL". "Routinely" means 1–4 % of the round-16 mix. 60–69 % of the RL proofs
    with a reductio are still template-only at round 16 (log 20:11), and the pre-registered "≥ 10× round 1" missed on 2 / 3 seeds.
    **Fix:** "more often after RL (1–4 % of RL proofs, vs 0.3–0.7 %)".
33. **OK-BUT-NOTE.** "almost never on its use … Knocking out just the 59 working examples, or a dose of templates only, would test
    whether they mattered." The 1 % dose set is already 99.7 % templates (5 working of 1,550). Its seeds wrote 15 / 41 / 6 working
    reductios before RL and acquired families on 3 / 3 (TABLES §11), which is close to the proposed test and worth citing. Also,
    "use" of a refuted assumption was not absent: both K12 and K12⁻ contain working proofs of a negation (2.15 %, 2.2 %). The arms
    differed in the form, not in that use.
34. **MISLEADING.** Caveat: "'Working' means the step uses its assumption". For proof by contradiction, pointless and supplied
    reductios do use their assumption (in an immediate clash) yet count as templates (TAXONOMY #10). **Fix:** "'Working' means the
    assumption does logical work: it is used, and (for proof by contradiction) not just clashed at once with G or a supplied ¬¬G".
35. **OK-BUT-NOTE.** "rests on 3 + 3 + 6 seeds of one small model". 3 + 3 + 6 = 12 is the RL-proof ladders. The family result cited
    above rests on 6 + 6 + 3 = 15. "One small model" reads as a single model. **Fix:** "on 15 separately trained models of one small
    architecture (9.6 M parameters): 6 full, 6 knockout, 3 dose (the RL-proof counts use 3 + 6 + 3)".
36. **Missing caveat.** The RL section and the epistemic note ("re-reads proofs our models wrote") should say the proofs read are
    samples of up to four per problem per round, drawn from the training mixes. Round 16's sample is drawn from all rounds (see #30).
37. **OK-BUT-NOTE (source, not the post).** `TABLES.md`, which the post cites for its numbers, says "taxonomy v1.1" in its header and
    §9, but the numbers are v1.2 final: DS 43 records, where v1.1 had 372. `tables.py` hardcodes the label (lines 47, 262, 266).

## Verified correct (≈ 75 values)

- Short version and setting: 155,000; thirteen; 38 % (37.64); 10.8 % (16,717); 59; ≈ 20 % (20.86); 0.04 % (59 / 155,000); 38 %
  (37.97); 2 % (working ¬I 2.15); 12 % (11.76); 0.05 % (76); classical rule = DN only.
- Field-guide "uses" shares, all 13: 51, 33, 43, 44, 44, 0.03, 4.7, 0.05, 8, 10.8, 3.1, 0.03, 12 %. Every K12 proof has a primary
  label (0 unlabelled).
- Examples "from K12" match EXAMPLES.md records 132941, 95938, 55304, 16853, 42672, 47528, 24177, 43479, 104971, 70566, 44059. The
  reductio blocks are records 108482 (scaffolded, immediate) and 131990 (one of the 59, kind free). Item 12's example is a pool
  schema instance (record 819), as stated. All 13 snippets were re-checked by `lean_check`: 13 / 13 accepted.
  (`blog_lean_check.py`'s docstring promises a textbook72 guard that the code does not run. The snippet theorems are EXAMPLES.md's,
  which `sealed.py` checked.)
- K12 habits: 28 % (28.20), 38 % (37.64), 24 % (23.53), 990; "a third shorter" (7.00 → 4.69); no idle split (0.0 %); cases 43 → 6 %
  (42.5 → 6.1).
- Reductio section: 16,658 of 16,717; 59; 6; 6,238 classical-only; σ-covered 0.
- Textbooks: 187; 1,610; gap table 21 / 0.04, 12 / 0.05, 14 / 0.03, 38 / 2, 34 / 9; 19 % σ-covered (35 / 187); 124 decided; 37 %
  (46 / 124); 3.7 % (22 / 594). Same direction in schemata and textbook72. The K12 shortest proofs keep the gap (0.1 / 0.0 / 0.2 /
  1.2 / 6.1 %).
- Knockout section: 16 rounds; 6 / 6, 0 / 6, 3 / 3; 16,717 / 59; 1,550 / 5. As mix counts: 67 / 29 / 48, 17 / 15 / 20 (exact),
  690 / 199 / 204, ≤ 1 and 0–22. Bound 12 lines; 9.6 M parameters (9,560,832).
