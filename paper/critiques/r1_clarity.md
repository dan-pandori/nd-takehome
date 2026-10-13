# r1 — Clarity and presentation (reviewer 2)

Scope: the paper (`paper/main.tex`, `paper/sections/*.tex`, compiled `paper/main.pdf`, 27 pages) and the blog
(`paper/blog.md`, `paper/figures/blog_fig*.png`). Page numbers refer to the current PDF. Word counts strip LaTeX.

## Overall assessment

The paper is honest, carefully hedged and numerically precise. Its sentence-level prose is mostly crisp, and several
elements are exemplary: Table 2 (arms), Table 5 (certificates), the per-family heat map (Fig. 3b) and Appendix F
(pre-registered expectations against outcomes). As a NeurIPS/ICLR paper, though, its presentation is not ready.

- **Length.** The main text is about 10,000 words with 7 figures and 6 tables (19 PDF pages at 11 pt), roughly 1.6–1.8
  times what fits in 9 pages.
- **Buried result.** The headline result first appears as Figure 3 on page 10. Before it come a Lean listing, 950
  words of related work and a 1,400-word §4 that reports results on *different* seeds before the reader knows what the
  knockout is for.
- **Split central concept.** The key distinction is spread over six overlapping terms (σ, σ⁺, lemma route, free
  positive reductio, classical-only, strict), with four spellings of the operative one. The abstract and introduction
  call the knockout bases "σ-free" a sentence or two before saying they "were not σ-free".
- **Internal vocabulary.** "Ladder" appears 51 times and is never defined. Also undefined or internal: "pend" (17
  uses), "K12", "T1", "read", "the 322", "group C", "rrQ100", "long2", "capability-defs", "chunk", "naming offsets".
- **Unreadable tuples.** 56 per-seed slash tuples in §4–§7 (for example "+4/−1/+6") make §4 and §6 very hard to read.
- **Loose ends.** The Table 4 caption shows "Table ??" and Appendix H is a placeholder. §9 de-anonymises the authors.

None of this needs new experiments. A restructure, a concept table, displayed definitions and one "funnel" table would
fix most of it.

The blog is in better shape: the "so what" comes first, the language is plain, and it has 4 figures with good captions.
But its opening overstates the paper. It conflates σ with its free positive form, which contradicts §5.4. It omits the
paper's GRPO caveat and the implications for evaluation and data filtering. And it is 2,547 words by `wc` against a
cap of 2,500.

**Score: 5/10 for clarity and presentation (fixable, but needs restructuring rather than polishing). Confidence: 4/5.**

---

## Paper

### Major

**1. [major] The central concept is split across six terms, and "σ-free" contradicts itself.**
*Location:* abstract ("no σ-free base acquired a classical theorem family … The knockout bases were not σ-free");
§1 ("no σ-free ("knockout") base acquired any classical family … The knockout bases were not σ-free in behaviour");
§3 ("σ⁺ widens this to a DN step that cites any derived line … The lemma route proves ¬¬G → G …"); Fig. 4 caption
(first definition of "free positive reductio"); §5.4 (a second definition); §5.5 and §7 ("free reductio"); §5.6
("free-σ proof"); App. A ("… is not a subformula of the theorem, by any route").
*Problem:*
- The paper's crux is the distinction between "absent" and "rare". It rests on six terms whose relations are never
  shown in one place.
- The operative term, the free positive reductio, is first defined inside a figure caption in §5.2. It is then
  restated three slightly different ways.
- The glossary's "by any route" contradicts "DN on a derived line": the lemma route avoids DN on a derived line. Yet
  §5.5 counts lemma-route proofs among seed 1's free-reductio proofs ("σ (32 proofs), other σ⁺ (24) and the lemma
  route (7)").
- "σ-free" is used for the data in one sentence and denied for behaviour in the next, so the abstract reads as
  self-contradictory on first pass.
- The abstract and intro say "four of six wrote σ proofs". That is about the *free positive* form on held-out members.
  §5.4 says "Every knockout ladder wrote σ and σ⁺ proofs in round 1, 6–13 distinct σ proofs per ladder". A reader
  cannot reconcile the two. The blog gets this wrong as a result (blog issue 2).

*Fix:*
- Put a concept table in §3, immediately after Fig. 1. Give one row per term, with its definition, how it relates to
  the others, its count in K12 and a one-line example:

  | term | definition | relation |
  |---|---|---|
  | σ | DN applied to a ¬¬G that the proof built by ¬-introduction | σ ⊂ σ⁺ |
  | σ⁺ | DN applied to any *derived* line (made by a rule, not a premise or assumption) | |
  | lemma route | prove ¬¬G → G in a box, then apply it | not in σ⁺ |
  | free positive reductio | σ⁺ (and the lemma route?) used for a G that is not a negation and whose ¬¬G the theorem does not supply | needed by every strict member |
  | classical-only | no intuitionistic proof (G4ip) | |
  | strict | classical-only, and no ¬¬ subformula in the sequent | |

- Decide whether the free positive reductio includes the lemma route. Then use one name everywhere: "free positive
  reductio", or a symbol such as σ_free.
- Reserve "σ-free" for data. Say "knockout base (pretrained without σ)" for the models.
- Rewrite the intro's sentence:
  > "The knockout bases were never trained on σ, but they still write it. All six used σ in round 1 on theorems that
  > supply ¬¬G, and four of six used its free positive form on held-out family members at large sample sizes. Only
  > the two that never did are certified out of reach at RL's budget."

**2. [major] The abstract does not pass the 60-second test.**
*Location:* abstract.
*Problem:*
- The busy reader gets about 15 numbers but cannot interpret them. "Acquired a classical theorem family" is not
  defined; the bar is given only in §1.
- "Certified out of reach" is not defined.
- The "σ-free … not σ-free" contradiction (issue 1) appears here.
- The measurement sentence ("of the 51–60 theorems per seed …") silently switches to three *other* full-exposure seeds
  at r8.
- The sentence "four of six wrote σ proofs …, only two are certified out of reach …, and the one knockout run that
  made progress did so …" changes tense and subject three times.

*Fix:* a rewrite of about the same length (≈255 words by `wc`, against 252 now; drop the second p-value if a hard
250-word limit applies). It makes no claim stronger than the paper:
> Whether reinforcement learning (RL) against a verifier creates capabilities or raises the probability of behaviour
> the base already had is contested, and large-model studies can rarely change what the base saw. We study it in a
> 9.56M-parameter prover trained from scratch on 155,000 synthetic propositional-logic proofs, judged only by Lean 4,
> with exact likelihoods for any proof. We delete one two-rule pattern from pretraining, the classical reductio σ
> (assume ¬G, refute it, eliminate the double negation), refill the data to the same size, and run 16 rounds of expert
> iteration (EI). A model *acquires* a classical theorem family if it proves at least half its held-out members in 256
> attempts. In a pre-registered test, no knockout seed acquired a family (0/6), against 6/6 seeds pretrained with σ
> (one-sided Boschloo p = 0.00024); 5/6 vs 0/6 counting only families acquired during RL (p = 0.0032). Restoring σ in
> 1% of pretraining restored acquisition on 3/3 seeds. Yet the knockout bases still use σ, rarely: four of six proved
> held-out members with it 1–6 times in 1.1–1.4 million attempts; only the other two are certified (Clopper–Pearson)
> out of reach at RL's compute budget. The one knockout run that progressed did so mostly on members its base could
> already reach. Measurement matters too: in three full-exposure runs, 51–60 theorems per run look RL-created at equal
> sample counts; 14–21 remain when the base gets RL's compute as attempts. In this organism EI amplified a pattern
> pretraining had exposed, even at 1%, but did not build it in 16 rounds from a base never trained on it.

**3. [major] The headline result is buried, and the section order works against the reader.**
*Location:*
- Figure 1 is a Lean listing (p. 6). The main result is Figure 3 (p. 10); the intro points to it eight pages ahead.
- §2 related work (950 words) comes before the organism.
- The pre-registered decision rule that defines the primary test sits at the *end* of §4 ("The knockout decision rule
  (pre-registered)").
- §6 (test-time compute) sits between the results and the discussion, although "Neither comparison below is part of
  the knockout".

*Problem:* §4 makes the reader absorb five budget allocations, an estimator calibration, certificates, two controls,
an IRT analysis and a Jaccard comparison, all on s0–s2 at r8, before seeing the experiment the title is about. §6 then
interrupts the path from results to discussion with a third set of models and analyses.
*Fix:*
- Reorder as follows:
  1. Introduction, with a teaser figure: the current Fig. 3a plus a three-arm schematic (issue 27).
  2. Organism and knockout design: current §3 plus the decision rule.
  3. Definitions: capability at a cost, within reach, certificate (≈400 words; issue 4).
  4. Knockout results: current §5.
  5. "How much did RL create in full-exposure models?": the §4 empirics and §6, condensed.
  6. Related work.
  7. Discussion.
  8. Limitations.
- Make the endpoint figure Figure 1. Move the full Lean listing to §3's end or to the appendix, keeping a five-line
  informal sketch in the main text.
- If the authors want to keep measurement first, at least move the decision rule into §3 and the s0–s2 empirics to
  after §5.

**4. [major] §4 is far too dense for its role, and its key funnel cannot be reconstructed.**
*Location:* §4, especially "Budgets matched to RL's compute", "k-to-solve intervals …", "Certificates" and "RL-free
controls".
*Problem:*
- §4 has 1,380 words, 24 slash tuples and about 60 numbers. Its job is to (a) define what §5 uses and (b) show that
  "created" shrinks.
- The shrinkage from 54/51/60 to "4 pairs on 3 theorems" is spread over three paragraphs, and some steps cannot be
  followed:
  - "Only 4/5/5 were never solved by *any* seed's base": 4/5/5 of what, the 20/14/8 or the 22/21/14?
  - How were the 9 pairs sampled at 1.1–1.5 million chosen?
  - Are the 4 surviving pairs a subset of the 7 certified ones?
- Forward references: "the replay-only control solves (below)". The Certificates paragraph uses the controls that the
  *next* paragraph defines.
- Several sentences arrive without motivation:
  - "At matched gains in IRT ability, EI flags no more items as differentially improved than replay-only training."
  - "The weight update of eight RL rounds is about as large as replay-only's (relative norm 0.28 vs 0.30, one seed)."
  - "Twelve operational definitions of 'created' agree poorly" (the twelve are never listed).
  - "a 'within reach if E ≥ 2/K' rule": the rule appears from nowhere.
  - "It is a statement about n": n is undefined.

*Fix:*
- (i) Give the definitions as five displayed equations. They replace about 150 words of prose:
  - p_M(t)
  - k-to-solve = 1/p_M(t)
  - within reach at K ⇔ p̂ ≥ 1/K with n ≥ K
  - certified out of reach at K ⇔ UB₉₅ < 0.05/K
  - C(K) = S_RL \ R_base(K) (the compute-matched set) and Δ_cov(K) = |S_RL| − |R_base(K)|. These two quantities are
    currently easy to confuse: at K_pub, 22/21/14 versus +21/+16/+12.
- (ii) Replace the narrative with one funnel table. Rows are filters; columns are s0/s1/s2 and total pairs. Make the
  branch points explicit:

  | row | s0/s1/s2 |
  |---|---|
  | equal k | 54/51/60 |
  | K_att | 34/33/33 |
  | K_pub | 22/21/14 |
  | all five allocations | 21/20/14 |
  | net of replay-only (at K_pub) | 20/14/8 |
  | never solved by any seed's base | 4/5/5 |
  | sampled 1.1–1.5 M times | 9 pairs (state the selection rule) |
  | certified | 7 |
  | survive every RL-free control | 4 pairs on 3 theorems (1 classical-only) |

- (iii) Move to the appendix: the estimator calibration medians, IRT, weight norms, and the 12 definitions with their
  Jaccard. Keep one sentence in the text: "the estimator is usable in aggregate to about 10⁻⁴ and runs 2–3-fold low
  below".
- (iv) Put the controls before the certificates.

**5. [major] Length and the balance between main text and appendix.**
*Location:* whole paper. Stripped word counts: intro 900, related 950, setup 1,380, §4 1,380, §5 2,940, §6 590, §7
990, §8 490, §9 420.
*Problem:* about 10,000 words plus 13 floats is roughly 15 pages at venue density. Everything is presented at the same
level of detail, so the reader cannot tell primary from secondary results.
*Fix:* a cut plan to about 5,500 words.
- **§2: 950 → 450.** Drop the four-bullet Abdulsalam comparison, which §7 repeats. Compress "Sharpening",
  "Elicitation", "Measuring rare behaviour" and "EI for theorem proving" to one or two sentences each.
- **§3: 1,380 → 900.** Move to the appendix:
  - the seeds' hardware and batch provenance ("rounds 1–8 ran on RTX A6000 cards at sampling batch 2,048 (s2 at 1,024
    from round 2) …");
  - the refill details that App. B already repeats;
  - the pre-filter rates;
  - "An older in-house checker is not used for any number here".
- **§4: 1,380 → 600** (issue 4).
- **§5: 2,940 → 2,000.**
  - §5.1 side effects: four sentences and a table pointer.
  - §5.6 nulls: one short paragraph each.
  - §5.7 robustness: move to the appendix, with one sentence left in the text.
  - Within-family AUCs and Spearman values: move to the appendix.
- **§6: 590 → under 200**, folded into the case study, or moved to the appendix (issue 23).
- **§7:** move "Interface" to Limitations and cut the related-work repeats (issue 18).
- **§9:** two sentences and a link in the text; Table 6 goes to the appendix.

**6. [major] Undefined project-internal vocabulary.**
*Location:* throughout. Counts are for the main text.
*Problem → fix:*
- **"Ladder" (51 uses, never defined).** First use is §1, "The one knockout ladder that made progress". Define it in
  §3 ("the 16-round EI run from one pretrained seed; we call it a ladder") or say "RL run". It also collides with §7's
  "evidence ladder"; rename that an "evidence hierarchy".
- **"pend" (17 uses).** It is opaque, and with "rN" already defined, "r0 (the base)" is free.
- **"K12", "K12⁻", "K12^1%".** These are unexplained internal names. Rename them (D_full, D_ko, D_1%) or explain them.
- **"T1 expert iteration … the variant with uniform allocation".** "T1" is a lab label, and the paper never says
  uniform allocation of *what*. Write "expert iteration with the same sampling budget on every training theorem".
- **"read", "plain read", "guided read", "x0/x1".** Using "read" as a noun is lab slang. Use "evaluation (256
  samples)", "guided evaluation" and "sample seed a/b".
- **"the 322", "rl_targets", "p2/heldout".** These are file names doing the work of set names. Name the sets
  (Eval-322, Train-4,495, General-5k). Keep theorem IDs such as `la_transfer_916` to the figure and appendix.
- **"group C" (§6, Fig. 7), "long rrQ100" and "long2 (21)" (Fig. 7b axis).** "long2" appears nowhere in the text.
  Define all three or relabel them (issue 12).
- **"the value capability-defs published", "one A40 chunk's per-attempt cost" (§4), "(run guided-tts; …)" (§3),
  "Phase 0/2" (App. I), "results-registry rows" (Table 6), "Lean-gate dumps", "pods/pod-hours" (§9).** Describe what
  each thing is. Keep run names in App. I only.
- **"naming offsets" (§4, §5.4, Fig. 5) and "the sampler conditions on its own names".** These are undefined, though
  they drive two caveats. Add one sentence to §3: "The environment numbers proof lines from one of 33 random starting
  offsets, so each proof has 33 spellings; E sums over them, while the Fig. 5 scores use one, understating by at most
  ln 33 ≈ 3.5 nats."
- **"both renaming-invariant keys", "renaming class", "premise-order-invariant key" (§3, §5.7).** Define them once.
- **IRT, PUCT, G4ip, Boschloo.** Expand and cite each once (Dyckhoff 1992 for G4ip; Boschloo 1970; a PUCT source).
- **The glossary is never cited.** App. A is never referenced from the main text. Add "(glossary: Appendix A)" at the
  start of §3.

**7. [major] K_pub, the reference budget for several headline numbers, is defined through an internal run.**
*Location:* §4 ("or the value capability-defs published (K_pub; it divides RTX A6000 seconds by one A40 chunk's
per-attempt cost)"); Table 3 ("as published (mixed GPU classes)").
*Problem:* K_pub is the budget behind "20/14/8 net of replay", "+21/+16/+12", "7 of 9 certify", "4 pairs on 3
theorems" and the guided "3/4/1". Yet its definition rests on:
- the name of an internal run, which is not a publication;
- a unit ("chunk") that appears nowhere else;
- a phrase ("mixed GPU classes") that reads as an inconsistent conversion with no stated reason to prefer it.

An outside reader cannot tell what K_pub charges or why it is the reference.
*Fix:*
- Rename it, since "pub" implies an external publication, and define it by what it charges. For example: "K_mixed:
  all ladder GPU time on the RTX A6000s where rounds 1–8 ran, converted at the A40's per-attempt cost without a class
  correction. It is the budget of our earlier report and the largest non-adaptive allocation, so we use it as the
  reference below." The authors should substitute the true rationale.
- Say what "uni" in K_uni stands for, or rename it K_gpu.
- Define the notation K_train(16) (§5.4), which is used but never introduced.

**8. [major] A broken reference and a placeholder appendix.**
*Location:*
- Table 4 caption: "(the other reads, run by this paper, are in Table ??)" (p. 11).
- App. H: "[Pending: the pre-registered checks C1–C3 are running …]".
- App. H is cited from §5.7 ("This paper adds a paired re-read with doubled caps (§H)"), from §8 and from §9.

*Problem:* there is a visible "??" in the main results table and four pointers to an empty appendix. The cut-off
robustness argument rests on that appendix.
*Fix:* fill App. H with the C1–C3 table, labelled `tab:checks`, or remove all four pointers before any circulation.
Add a final check for "??" in the PDF text.

**9. [major for submission; trivial to fix] Anonymity breaches and process artifacts.**
*Location:*
- The author line, "Dan Pandori et al.".
- §9: "fork dan-pandori/nd-takehome", "hf://buckets/dan-pandori/…"; App. I's branch names.
- The rendered references carry notes such as "Version read: v1 (abstract only)" (pp. 20–23).
- §2: "we have read only its abstract"; "the lowest share in the notes we verified is 0.01".
- §7: "as far as the quotes we verified go".
- App. G, which reports a fix to an internal script ("reported 0.0020").
- "An independent reviewer …" (§5.7, §9).

*Problem:* the links break double-blind review, which risks a desk reject. The reading-provenance hedges and the
internal-review story read as lab notes. A venue reader will take "the reviewer" to mean a peer reviewer.
*Fix:*
- Anonymise the links (anonymous repository or supplementary material).
- Strip the "Version read" notes from the .bib.
- Read the cited papers, or cite them only for what their abstracts say, without commenting on what was read.
- Rephrase the reviewer references as "an internal audit by a team member who did not write the analysis code, using
  separate code".
- Reduce App. G to one footnote: "three exploratory p-values in an internal report used a transposed table; all values
  here are recomputed".

### Minor

**10. [minor] Fig. 2 (budget) leaves out its own starting point.**
*Location:* Fig. 2; caption: "Lines end where the base data stop deciding membership."
*Problem:*
- The x-axis starts at 1,000, so the equal-k point is off the plot: K = 256, 54/51/60. That is the abstract's "51–60"
  and the steepest drop.
- The legend's labels ("target attempts", "training phases") differ from Table 3's ("ladder sampling attempts on
  training theorems", "sampling + fine-tuning GPU time").
- "K_att" and the other subscripts are set as plain text.
- The three seeds are drawn in three similar blues.
- The caption's last sentence is cryptic.

*Fix:*
- Extend the axis to 200 and mark equal k.
- Use Table 3's names and mathtext subscripts.
- Give each seed a distinct line style.
- Caption: "Curves stop at 66,304 attempts, the most any theorem received; beyond it, 'within reach' cannot be
  decided."

**11. [minor] Fig. 5 and §5.4 report a single full-exposure comparator while plotting four.**
*Location:* Fig. 5 caption ("The full-exposure point at pend is seed 0's base."); §5.4 ("under full seed 0's base it
is −19.2", "against −10.5 under the full base").
*Problem:*
- Fig. 5 shows four full-exposure points at pend: s3 at −15.4, s4 and s5 at about −20.3 and −20.9, and the outlined
  s0 at −19.2. The caption therefore reads as wrong.
- The text compares the knockout bases with one full base when four are scored. The blog copies "−19" (blog issue 5).
- Why 101 of the 106 members are scored is not said.

*Fix:*
- Caption: "Lines: full s3–s5, dose s0–s2, knockout s0–s5, scored at r0, r4, …, r16. Outlined point: full s0's base,
  whose ladder was not rescored. 101 of the 106 strict members have a known σ proof."
- Text: "under the four scored full bases it is −15.4 to −20.9" (and likewise for the box-opening step, if available).

**12. [minor] Fig. 7 (test-time compute) uses undefined categories, and its title overreaches.**
*Location:* Fig. 7b x-axis ("group C (28–36)", "long rrQ100", "long2 (21)"); y-label ("PUCT + value − sampling");
title ("Test-time compute helps the base, not the RL model").
*Problem:*
- "rrQ100" and "long2" are defined nowhere, and "long2" is not in the text at all. PUCT is never expanded.
- Panel (a) is not compute-matched (2.2 times the GPU time), but the bold title asserts the conclusion for both panels.
- Blue shades here encode the checkpoint, whereas blue means the full arm in Figs. 3–6.

*Fix:*
- Relabel the pools ("unsolved by r0 and r8", "textbook72", "holdout250", "long-100 (13–16 lines)"). Drop "long2" or
  define it.
- Expand PUCT.
- Title: "Test-time compute helps the base more than the RL model (panel a not compute-matched)".
- Use a grey ramp for checkpoints.

**13. [minor] Small defects in Figs. 3 and 4.**
- **Missing "=":** the Fig. 3a x-label reads "plain read, k 256", the Fig. 4b y-label "(k 32 sample)" and the Fig. 7a
  y-label "at k 256".
- **Fig. 3b colour bar:** unlabelled. Label it "share of strict held-out members solved".
- **Fig. 4a y-label:** "strict trained targets solved" means "with at least one accepted proof in training samples so
  far". That is not "solved" in a read. Write "… with an accepted proof so far (cumulative)".
- **Fig. 4a legend:** it overlaps the green and blue lines at rounds 8–12.
- **Fig. 4b:** the symlog axis turns the knockout ladders' 0↔1 counts into a sawtooth that hides which seed is which.
  Use small multiples per seed, or mark each seed's first-occurrence round.
- **"1 %":** the figures write "1 %" where the text writes "1%".

**14. [minor] Table 4 cannot be checked against the RL-only claim.**
*Location:* Table 4; §5.2 ("families that reach the bar at r16 but were not there at pend: 5/6").
*Problem:*
- The table lists families at the bar only at r16. The reader cannot verify the RL-only reading, or "converse
  contraposition at the bar at pend on 5/6".
- The parentheticals "em (36/37)" and "pe (6/12)" are unexplained.
- Old seeds (s0–s2) and new seeds (s3–s5) are not distinguished, although §5.2 makes an argument on the new seeds
  alone.

*Fix:* add an "at the bar at r0" column, or bold the r16 families acquired during RL. Explain the parentheticals in the
caption. Mark the old seeds with †.

**15. [minor] "Within reach" is used in a way its own definition rules out, and two counts disagree.**
*Location:* §4 ("within reach at K if … p̂ ≥ 1/K, with at least K attempts made"); §5.4 ("Knockout seed 1's base has 4
of its 18 strict converse-contraposition members within reach at its budget (p̂ = 1.0–3.3×10⁻⁴ ≥ 1/17,189)"); §5.5,
the intro and the abstract ("members its base could already reach").
*Problem:*
- Table 5 gives 1,120,378 pooled attempts over 105 members for seed 1. That is about 10,700 per member, which is below
  K = 17,189. As written, these members fail the "at least K attempts" clause, so a careful reader will conclude that
  either the claim is wrong or the definition changed silently.
- Table 5's successes sum to 12, but §5.4 says "All 14 base successes on strict members". The other two are on
  `la_transfer_916`, which the table excludes.

*Fix:* state the per-member attempts. Then either write "p̂ ≥ 1/K on about 10,700 attempts each (fewer than K, so
within reach in the rate sense only)" or relax the definition explicitly. Write "12 on the 105 family members (Table
5) and 2 on la_transfer_916". The soundness reviewer should also see this.

**16. [minor] Terminology collisions.**
- **"Reach."** App. G says "'reach' is used only in its technical sense". But the text also says "reached the
  pre-registered bar" (§1), "No family reaches the bar" (§5.5), "Guided reading does not reach most of the
  compute-matched creations" and "Neither method reaches the theorems" (§6). Use "meets the bar" and "recovers".
- **"Bar."** It means the family criterion (50%), but also "a pre-registered bar of 0.7" for the AUC (§5.4) and "EI's
  own bar of p̂ ≥ 0.01" (§7). Keep "bar" for the family criterion only.
- **"Acquired" / "at the bar" / "earns 'needs exposure'".** One concept has three names. Use "acquired" everywhere.
- **"Created".** It names both the §4 measurement sets ("RL 'creates'") and a pre-registered verdict ("created: at
  least 2 of 6 knockout seeds …"). Set the verdicts in small caps and call the §4 sets "RL-only solves at budget K".
- **"Seed" and "seeded".** Training seeds s0–s5 and sample seeds x0/x1 sit next to "Seeding one proof" (proof
  injection): "Seeded minus control … Seed 2's two were single successes". Call it "proof injection".
- **"Solved".** In a read it means at least 1 success in 256. In Fig. 4a and §5.2 ("had been solved at least once,
  cumulatively") it means a proof found in training samples.
- **Classical-only.** §5.1 also says "classically valid but intuitionistically unprovable", and one sentence calls the
  complement both "225 non-classical" and "53 intuitionistic". Use "classical-only" and "intuitionistically provable".
- **Converse contraposition.** It is also "contrap. conv." (Table 1, Fig. 3b, App. C), "cc" (Table 4) and "classical
  contraposition" (blog).

**17. [minor] Per-seed slash notation.**
*Location:* 24 instances in §4, 17 in §5, 12 in §6 and 3 in §7. Examples: "+8/+10/+12 to the base, +6/+4/+3 at r8 and
+4/−1/+6 at r16"; "by round 16 0/5/1/0/0/2 had been solved"; "+29/+31/+35/+37/+26/+21".
*Problem:* the reader has to track which seed set each tuple refers to (old s0–s2, new s3–s5 or knockout s0–s5).
Signs inside tuples are hard to parse.
*Fix:* move per-seed values into tables; most already exist or fit an appendix table. In the text, give a range or
mean ("+3 to +6 at r8") and name the seed set once per paragraph.

**18. [minor] Redundancy.**
- **The power-sampling caveat** ("fails its own positive control") appears in §1, §2, §5.6 and §8, and again in App.
  E. Keep it in §5.6, with one line in §8.
- **The Abdulsalam et al. comparison** (a new action type versus a composition; GRPO versus plateauing RFT) appears in
  §2, as four bullets, and again in §7. Tsilivis and Interplay are also each discussed twice. Keep them in §7.
- **Repeated facts:**
  - The knockout construction appears in §3, in §5.1's first paragraph and in App. B.
  - "a 0.1% set is built but unused" appears in §5.3, §7 and App. B.
  - "e^289–e^3,228" appears in §1 and §4.
  - "−6 → −1 nats" appears in §4 and §6.
- **Abstract and intro:** the intro's "Main result" paragraph repeats the abstract almost verbatim. Trade part of it
  for the teaser figure and the implications (issue 20).

**19. [minor] Inconsistent statements about the estimator, and counts that do not add up.**
*Location:* §4 ("Below that it runs about two-fold low"; "Across 196 (seed, theorem) pairs … (106 pairs) … (52) …
(36)"); §8 ("runs two- to four-fold low below 10⁻⁴").
*Problem:*
- The medians are 0.454 and 0.36 (Fig. 8b), that is 2.2-fold and 2.8-fold low. No reported median supports
  "four-fold".
- The listed bins sum to 194. The n = 2 bin below 10⁻⁵ is drawn in Fig. 8 but never mentioned.
- The likelihood analyses use T = 1 ("Exact likelihoods along RL") and T = 0.8 (the estimator and §5.4) without saying
  why.

*Fix:* write "about 2–3-fold low (medians 0.45 and 0.36)" in both places. Add "and 0.36 for p̂ < 10⁻⁵ (2 pairs)". Add
one sentence explaining the temperature choice.

**20. [minor] The "so what" is on page 18, and one implication is in tension with the paper's own threshold.**
*Location:* §7 "Implications for evaluation and data filtering": "a capability that is absent at k = 256 … can still
be present at 10⁻⁶ per attempt, and RL is the kind of process that can amplify such rates".
*Problem:*
- The two most transferable lessons come only at the end of the paper.
- The "amplify such rates" clause sits awkwardly beside the paper's own amplification threshold. In the knockout, EI
  "does nothing visible with one the base produces at 10⁻⁶". What it did amplify were rates around 10⁻⁴ on specific
  members (seed 1).

*Fix:* end the introduction with two sentences:
> "Two practical lessons follow, with the caveat of scale: evaluations that aim to show a capability is absent need
> rare-event estimates, not pass@k at modest k; and filtering a composition from pretraining kept this RL from
> acquiring it, but a 1% leak undid the filter."

In §7, write "RL can amplify rates near 10⁻⁴ (knockout seed 1), though not, within 16 rounds, rates near 10⁻⁶".

**21. [minor] Wording in the intro and contributions.**
- **Item 1.** "For our models at random initialisation the known proofs alone bound the expected attempts needed from
  above at e^289 to e^3,228" is hard to parse, the direction of the bound confuses, and the number is not used again.
  Rewrite: "Every proof has positive probability under a softmax policy, even at random initialisation (for our
  hardest theorems at least e^−3228 per attempt), so 'the base cannot' must mean 'cannot within K attempts', with K
  tied to what RL spent." Also, exponents should not contain thousands commas.
- **Contribution 2.** "It adds k-to-solve intervals from sampling and a known-proof likelihood estimator, calibrated
  down to p ≈ 10⁻⁴, Clopper–Pearson certificates of unreachability, and RL-free controls" is a garden-path list.
  Rewrite: "It brackets each theorem's attempts-to-solve between a sampling bound and a likelihood estimate (calibrated
  to p ≈ 10⁻⁴), certifies unreachability with Clopper–Pearson bounds, and nets out RL-free controls."
- **Contribution 4.** "Null and negative results at their strength" should read "… reported at their actual
  strength".
- **Order.** The knockout is the headline but is listed as contribution 3. List it first.

**22. [minor] §3 sentences that need rewording or removal.**
- "A change of sampling batch only re-draws samples, because Lean checks every sample." → "Changing the sampling batch
  changes which samples are drawn, not how they are judged."
- "An older in-house checker is not used for any number here." → delete it, or move it to the appendix.
- Fig. 1(a), "one of knockout seed 1's base's rare large-k successes" → "one of the rare successes of knockout seed
  1's base in large-k sampling".
- "the generated theorem": every family member is generated too → "one non-family theorem (la_transfer_916)".
- "derived line" is undefined → "a line produced by a rule, as opposed to a premise or an assumption".
- "832 tracked held-out theorems": say what the 832 are made of.
- EI paragraph: say whether each round fine-tunes the previous round's model, and what "each weighted four times"
  means.

**23. [minor] §6 and §7's "Interface" paragraph are off the main line.**
*Location:* §6 (full s0–s2 from earlier runs; "Neither comparison below is part of the knockout"); §7 "Interface" (a
3.2M organism, a whole-proof interface, "EI's own bar of p̂ ≥ 0.01", "the state cannot be separated from step-by-step
generation").
*Problem:* §6 interrupts the path from results to discussion, and its first panel is not compute-matched. "Interface"
brings a new organism, a new bar and an uninterpretable sentence into the Discussion.
*Fix:* merge §6 into the measurement case study (issue 3) or move it to the appendix, leaving one sentence in §7. Move
"Interface" to Limitations as one sentence with an appendix pointer.

**24. [minor] Hard-to-parse sentences, with rewrites.**
- §5.2, "and by round 16 0/5/1/0/0/2 had been solved at least once, cumulatively" → "by round 16 the knockout ladders
  had found proofs for 0, 5, 1, 0, 0 and 2 of them (s0–s5)".
- §5.2, "The interquartile means are 53.75 [30.5, 73.5] and 0.75 [0, 1.75] …". It is unclear whether the brackets are
  confidence intervals or interquartile ranges → "Interquartile means: 53.75 (95% bootstrap CI 30.5–73.5) vs 0.75
  (0–1.75)".
- §5.4, "Their medians at r16 are no closer. Four of six fall, and the largest rise is 3.7 nats". "No closer" is
  followed by a "rise" → "By r16, four of six knockout medians have fallen; the largest rise is 3.7 nats (s0), against
  10.3 for full s3 and 16.6 for dose s0."
- §5.4, "We sampled each knockout base about 1.1–1.5 million times, pooled over the 105 strict family members, at its
  own RL budget K_train(16)". This conflates sample size with budget → "We drew 1.1–1.5 million samples from each
  knockout base, spread over the 105 strict family members, and tested the pooled rate against that seed's RL budget K
  (K_train at r16)."
- §5.5, "Its share of converse contraposition among strict training targets reached 0.33 from round 21. But its strict
  training targets stalled at 9" → "From round 21 it had proofs for a third of the strict converse-contraposition
  training targets, but its total stalled at 9 of the 123 strict targets."
- §5.6, "with and without four copies of knockout seed 1's base's own free-σ proof of the generated theorem" → "with
  and without four copies of one free positive reductio proof (of la_transfer_916) written by knockout seed 1's base".
- §5.7, "None of 150 of the reads' own Lean rejections passed, none of 60 proofs under another theorem, … and sorry
  failed." → "Lean rejected all 150 re-submitted rejections, all 60 proofs paired with the wrong theorem, all 40
  strict knockout proofs with Classical.byContradiction removed, and sorry."
- §5.7, "The pre-filter decided every rejection in knockout seed 1's 2.35 million distinct texts." Say why this
  matters: every rejection there rests on the pre-filter, whose false-reject rate is bounded next.
- §5.7, "They cross the 0.1% cut-off line in 4 of 27 reads" → "Guided reads exceed the pre-registered 0.1% cut-off
  threshold in 4 of 27 reads".
- §7, "The dose arm locates the threshold between 0% and 1% of pretraining records". The threshold was just defined
  on the per-attempt-rate axis (10⁻⁶ versus "moderate"), so name both axes.

### Nits

**25. [nit] Typography and citations.**
- Write "e^{3228}", without a thousands comma in the exponent.
- Fig. 8b's tick labels use "1e-4–1e-3"; the text uses 10⁻⁴.
- Fig. 6's knockout labels for s0, s2, s3 and s4 overlap.
- Cite ALiBi, NoPE, Muon and PUCT.
- Table 1's header "contrap. conv." should be "conv. contrap.".
- The per-family p is given as "0.0002", while the abstract has "0.00024" for the same 6-vs-0 table. Use one
  precision.
- "pod-hours" → "GPU-instance hours".

**26. [nit] The subtitle lists methods.** The outline's alternative is results-forward and better for the busy
reader: "Expert Iteration Amplifies What Pretraining Exposed: A Composition Knockout in a From-Scratch Theorem Prover".

**27. [nit] There is no schematic of the design.** A small diagram would let a non-logician grasp the design in ten
seconds: three pretraining sets (full, knockout, 1% dose) → identical EI → evaluation on the strict held-out members,
with the σ step highlighted. Place it beside the endpoint plot as the new Fig. 1.

**28. [nit] There are no displayed equations.** The five definitions in issue 4 would make §4 skimmable and settle the
C(K) versus Δ_cov ambiguity.

---

## Blog (`paper/blog.md`)

It is strong on structure. The "short version" puts the result first, the "'Absent' is not quite right" section is the
best explanatory writing in either document, and the captions are plain. The issues below are about fidelity to the
paper and about length.

**1. [major] The opening overstates the paper.**
*Location:* "The short version": "With the move in its training data, the prover learned to prove a whole class of
classical theorems on six seeds out of six. Without it, it learned none of them on any of six seeds, in 16 rounds of
RL." Also: "In this organism, RL amplified what pretraining had exposed."
*Problem:*
- (a) "A whole class" means, in the paper, at least half of *one* family's held-out members.
- (b) "learned … on six seeds" credits RL with 6/6. But on five of the six runs, one family was at the bar *before*
  RL. The paper's RL-only reading is 5/6, and 2/3 vs 0/6 (p = 0.034) on the new seeds alone.
- (c) "learned none of them": the knockout runs solved 0–2 of the 106.
- (d) "RL amplified" generalises from one algorithm. The paper says "this EI" throughout; its list of corrections
  (App. G) exists to enforce exactly that.
- (e) The 1% dose comparison is labelled exploratory in the paper but stated here without a hedge.

*Fix:* rewrite the first paragraph:
> We trained a tiny theorem prover from scratch, twice: once on data containing a particular classical reasoning move,
> and once with every example of that move deleted and the data topped back up to the same size. Then we ran the same
> simple form of reinforcement learning (RL), expert iteration, on both: six independent training runs ("seeds")
> each. With the move in its data, every run finished able to prove at least half of some family of held-out classical
> theorems, and five of the six picked up a new family during RL. Without it, no run picked up any family in 16 rounds
> (the best solved 2 of 106 held-out theorems). Putting the move back into just 1% of the data restored this on three
> runs out of three, in an exploratory comparison.

Then change "RL amplified" to "this form of RL amplified".

**2. [major] σ is conflated with its free positive form, which contradicts the paper.**
*Location:* §4: "One knockout run kept producing more σ proofs, a few per round from round 9 and 123 per round by round
24", and "RL can only reinforce what it samples, and it almost never sampled σ."
*Problem:* paper §5.4 says "Every knockout ladder wrote σ and σ⁺ proofs in round 1, 6–13 distinct σ proofs per
ladder", on theorems that supply ¬¬G or have a negated goal. What was rare, and what began in round 9 for seed 1, is
the *free positive reductio*. The counts 11 → 123 are free-positive-reductio proofs, not σ proofs. A reader who sees
both documents finds a contradiction about the central mechanism.
*Fix:* introduce the distinction once, in §2 of the blog:
> "σ shows up in two situations. Sometimes the problem already hands you a double negation, or asks you to prove a
> negation; that use is easy, and the knockout models made it from round 1. The genuinely classical use proves a
> positive statement with no double negation supplied, and it is the only way to prove the held-out theorems."

Then write "One knockout run started making the genuinely classical use in round 9 and was writing 123 such proofs per
round by round 24 …" and "… it almost never sampled the classical use of σ on these theorems."

**3. [major] The "so what" for outsiders and the paper's main caveat are both missing.**
*Location:* whole post; §7 "One RL algorithm, 16 rounds"; §8.
*Problem:*
- The paper's broadest takeaways, from §7 "Implications for evaluation and data filtering", are absent: pass@k at
  modest k cannot show a capability is absent, and a 1% leak undid a pretraining filter.
- So is the paper's main interpretive caveat. The closest controlled study (Abdulsalam et al.) found GRPO creating
  behaviour absent from pretraining, while rejection-sampling fine-tuning, the family the paper's EI belongs to,
  plateaued. The paper concludes "Our null may therefore be specific to EI".
- Without these, the post reads as "RL can't create", which the paper does not claim. The brief asks for the "so what"
  first and the same evidence as the paper.

*Fix:* after the short version, add a short "Why it matters" paragraph:
> "If a model fails a task in 1,000 tries, it may still succeed once in a million, so claims that a capability is
> absent need far more attempts, or likelihood estimates. And deleting a skill from pretraining kept this RL from
> learning it, but putting 1% back undid the deletion."

In §7, add: "A closely related study found the opposite with a different RL algorithm (GRPO); the family of methods we
used plateaued there. Our result may be specific to expert iteration." Add "GRPO from the knockout models" to §8.

**4. [minor] The post is over length.**
*Location:* whole post. `wc -w blog.md` gives 2,547; without the code block, 2,466.
*Problem:* the cap is 2,500, and fixes 1–3 add about 150 words.
*Fix:* cut about 200 words:
- Leave the "Draft for Dan" line out of the count.
- Compress §2's list of three data versions into two sentences.
- Merge §5's last two paragraphs.
- Drop "The rest of this post explains …" (28 words).
- Shorten the note under the code block.

**5. [minor] The text and its own figures disagree.**
- **The "−19" figure.** §4 says "the full-data model before RL gives a median log-probability of about −19". Blog
  Fig. 2 has no −19 point: its full-data lines start at −15.4, −20.3 and −20.9. The −19.2 is full s0's base, which
  only the paper plots. Either add that point to the figure and say "the one full-data model we scored before RL", or
  describe the plotted range. Then recompute "between about a thousand and twenty million times less likely".
- **The "51 to 60" count.** §5 says equal attempts label "51 to 60 of 322 evaluation theorems as created". Fig. 3's
  x-axis starts at 1,000, and its curves top out at 38. Extend the axis to 256 and label that point "same attempts as
  RL's evaluation (256)".
- **Counts versus families.** Fig. 1 shows counts of theorems, while the text's claims are about families acquired.
  Add to the caption: "A run acquires a family when it solves at least half of that family's held-out theorems."

**6. [minor] Some terms are used before, or without, a definition.**
- "seeds" (short version) is defined only in the Fig. 1 caption → "independent training runs (seeds)".
- "organism" (short version, §1) → "a model organism: a small system we can fully control".
- "intuitionistic logic" (§2) → add "logic without this kind of proof by contradiction".
- ¬ and → appear in "from ¬S → ¬P and P, conclude R → S" before they are explained → add "(¬ is 'not', → is
  'implies')".
- The family names (Peirce's law, negated conditional) → give one example, such as "excluded middle: 'P or not P'".
- "at the bar" (§3: "was already at the bar before RL started") → "was already acquired before RL".
- "the published budget" (§5) → drop it, or say "at one of the larger budgets".
- "nats" (Fig. 2 axis) → "natural-log units".

**7. [minor] Statements stronger than the paper.**
- **Epistemic status.** "An independent reviewer recounted every number from the raw files" → "every count in the
  knockout experiment". The paper's reviewer re-derived the §5 counts; §4 and §6 are reviewed results of earlier runs.
- **Seed counts.** "Six training seeds per condition" → "six per main condition (three for the 1% dose)".
- **"Exactly".** "We can compute exactly how likely it is to write any given proof" needs the paper's two caveats.
  The scores use one of 33 line-naming variants, which understates them by up to about 3.5 nats. And the scored proofs
  come from the full-data runs, so a knockout model with its own spelling need not move toward them.
- **Pre-registration.** "The difference is very unlikely to be chance: we pre-registered the test, and it gives
  p = 0.00024". Pre-registration does not make a difference unlikely to be chance. Write "The test was pre-registered;
  it gives p = 0.00024 (…)".
- **"Back-of-envelope … explains".** "A back-of-envelope calculation explains why RL rarely got started" → "is
  consistent with".
- **"Public".** The last line, "The paper draft, all code, data and model checkpoints are public", contradicts "Not for
  circulation" → "will be public".

**8. [minor] Caveats the paper gives and the blog omits.**
- (a) The strict held-out sets replaced the original ones through an amendment made after the first knockout round.
  The original sets give the same result. One parenthetical would cover it.
- (b) The old and new full runs differ in GPU and batch for rounds 1–8. On the new runs alone, acquisition during RL is
  2/3 vs 0/6 (p = 0.034).
- (c) The knockout's deficit on textbook problems persisted after RL. This belongs in §7's "isn't perfectly clean".
- (d) Fig. 4's guided panel is not compute-matched (about twice the compute per attempt). Say so in the caption, since
  the figure title states the conclusion.

**9. [nit] Figures.**
- **Fig. 1:** the title "Without σ in pretraining, RL did not learn the classical theorems" lacks "in 16 rounds", and
  the dashed line's round-20 point has no tick label.
- **Fig. 4:**
  - the right panel has no y-axis label;
  - "hardest" is undefined (add "theorems neither model solved in an earlier evaluation");
  - the left panel has no legend (the caption covers it).
- **Fig. 3:** say "five dots per run".

**10. [nit] Voice and wording.**
- The epistemic status says "I"; the rest of the post says "we".
- The Lean comment "-- drop the double negation: σ" labels a single step as σ, while the text defines σ as the
  composition → "-- σ: refute ¬S, then drop the double negation".
- "We hold out 106 of their instances": the 106 are 105 family members plus one other theorem → "106 held-out
  theorems".
- §6, "Tree search, at equal time, added about 44% of what eight RL rounds add on a set of long theorems for the base
  model" → "For the base model, tree search at equal time recovered about 44% of what eight RL rounds add on a set of
  long theorems."
