# r2 — Clarity and presentation (reviewer 2, round 2)

Scope:
- the revised paper: `paper/main.tex` and `paper/sections/*.tex`, the compiled `paper/main.pdf` (29 pages: main text pp. 1–20,
  references pp. 20–25, appendices pp. 25–29) and `paper/figures/fig*.png`;
- the blog: `paper/blog.md` and `paper/figures/blog_fig*.png`.

Section numbers are the compiled ones: §1 Intro, §2 Organism, §3 Results, §4 Measurement, §5 Related, §6 Discussion,
§7 Limitations, §8 Reproducibility. Figure numbers are the compiled ones too: Fig. 1 overview, Fig. 3 endpoint, Fig. 4
dynamics, Fig. 5 log p, Fig. 6 prior, Fig. 7 budget, Fig. 8 test-time compute, Fig. 9 estimator. "(pending)" placeholders
and the "Dan" placeholders are not counted.

## Overall assessment

The revision fixes the structural problems of round 1:
- A reader now meets the design and the result on page 2 (Fig. 1).
- The six σ-terms are in one table (Table 1), and the definitions are displayed.
- The decision rule comes before the results, and the measurement funnel is a table (Table 6).
- The abstract defines "acquired" and leads with the contrasts that are specific to RL.
- The "??" and the empty appendix are gone.

These are real gains, and Table 1, Table 4 (with r0 and underlined r0 families), Table 5 (with K_max) and the waiting-time
framing all work.

Three problems would still draw comments at a venue:

- **The figures were not revised.** The files behind Figs. 3–9 predate the round-1 critique: they were written at
  19:37–19:38, and the critique at 20:24. Only `fig0_overview` is new. Since the text was cleaned up and the figures were
  not, the figures now contradict the text they illustrate. They still say "pend", "plain read, k 256", "at the bar",
  "targets", "knockout (no σ)", "Free reductio", "as published" and "rrQ100". Every round-1 figure defect apart from the
  captions is still there.
- **The central terms still slip.**
  - The abstract says "The knockout bases were not σ-free", but §3.1 and §7 speak of "a σ-free base".
  - The intro's null predicts "at most 0.02 σ proofs per round", one paragraph before "the knockout ladders wrote σ from
    round 1".
  - "Free reductio" survives in three places.
  - "Acquire", now a defined family-level term, is also used for compositions and for theorem counts.
  - Two different contrasts, each 5/6 against 0/6 with p = 0.0032, sit in adjacent paragraphs.
- **The length is unchanged.**
  - The main text is about 10,000 words on 20 pages, the same as round 1 and about twice a 9-page venue. Stripped word
    counts: intro 1,010, §2 1,650 (with floats), §3 3,060, §4 1,120, §5 770, §6 1,190, §7 500, §8 360.
  - The Discussion has gained a new results section (earlier organisms) written in lab shorthand ("ignited", "dead arms",
    "draws", "Interplay").
  - The reordering created new forward references: the five budget allocations and K_train(16) are defined in §4 but used
    in §2 and §3.

The blog is close to done. It is 2,495 words by `wc -w` (2,414 without the code block), has 4 figures, puts the "so what"
first and claims nothing stronger than the paper. It does have four problems:
- it names the decisive family wrongly;
- it states one number the paper no longer contains;
- it omits three caveats that the paper gives;
- it has no word budget left for fixes.

**Score: 6/10 for clarity and presentation, up from 5. The structure is now right; the figures, the terminology and the
length are not. Confidence: 4/5.**

---

## Round-1 issues: status

### Paper

| # | round-1 issue | status | evidence |
|---|---|---|---|
| 1 | central concept split; "σ-free" contradicts itself | partly | Table 1 defines all six terms and their relations, and §3.3 separates easy σ from the free positive reductio. But the abstract's "were not σ-free" is contradicted by "a σ-free base" in §3.1 and §7, and "free reductio" remains in §3.4, §6 and the Fig. 4b title (new 2) |
| 2 | abstract fails the 60-second test | fixed | "acquired" is defined inline, the RL-specific contrasts are labelled not pre-registered, and tense and subject are stable. Residue: the σ-free sentence, the dose's missing "exploratory" label (new 2, 12) and "knockout" never introduced (new 20) |
| 3 | headline buried; section order | fixed | Fig. 1 (design and result) is on p. 2; the order is setup → results → measurement → related → discussion; the decision rule is in §2. The move created forward references (new 4) |
| 4 | §4 too dense; funnel cannot be reconstructed | partly | Three of four fix parts are done: displayed definitions, Table 6 as the funnel, IRT, norms and Jaccard moved to App. D. Not done: the controls are still defined after their first use, and Table 6's branch points, "net of" and "strictest set" are implicit (new 9) |
| 5 | length and balance | not | About 10,000 words and 20 pages, as before. §3 grew to 3,060 words and §6 to 1,190 (new 5) |
| 6 | internal vocabulary | partly | The text now defines ladder, rN, evaluation and the line-numbering offsets, and drops "pend", "T1" and nearly every noun use of "read" (two remain, in §6 and App. G). "pend" and "read" survive in Figs. 3, 5, 6, 8 and 9. Also still present: "K12", now colliding with K (new 4); "results-registry rows", "Lean-gate dumps", "writing run" and "reviewed reports"; undefined "renaming-invariant keys"; and App. A is still never cited |
| 7 | K_pub defined through an internal run | partly | It is now defined by what it charges. It is still called "pub", Fig. 7's legend still says "as published", and nothing says why it is the reference for Table 6's lower rows and for the guided "3/4/1". "uni" in K_uni and the "(16)" in K_train(16) are unexplained |
| 8 | "Table ??"; placeholder appendix | fixed | No "??" in the PDF; App. I holds C1–C5 |
| 9 | anonymity breaches and process artifacts | partly | "The reviewer" is gone. Remaining: 53 "Version read" notes in the rendered references, at least six of them "(abstract only)"; "(this paper)" ×11 and "run for this paper" ×4; "This writing run"; App. H's "The review's ten rewordings". The links are declined for now |
| 10 | budget figure (now Fig. 7) | partly | The caption now explains the equal-k point and the stop at 66,304. The figure file is unchanged: the axis starts at 1,000, the legend names differ from Table 6 ("target attempts", "training phases", "as published"), the subscripts are plain text and the three blues are similar |
| 11 | log-p figure (now Fig. 5) reports one comparator | partly | The caption names the outlined point and the text gives the four-base range. Still open: why 101 of the 106 theorems are scored; the box-step comparison still uses one full base (−10.5); "pend" on the axis; the title "Distance to the reductio" |
| 12 | test-time-compute figure (now Fig. 8) | partly | The caption defines group C, rrQ100 and long2, softens the title and states that panel (a) is not compute-matched. The axis labels and the "pend" legend are unchanged, PUCT is never expanded or cited, and "k 256" remains |
| 13 | small defects in Figs. 3 and 4 | not | Both figure files are unchanged: "plain read, k 256", "(k 32 sample)", unlabelled colour bar, "strict trained targets solved", legend over the lines in 4a, "1 %" |
| 14 | Table 4 cannot be checked against the RL-only claim | fixed | It has an r0 column, underlined r0 families, † for old seeds and a gain column. Residue: "(r20: 5; r24: 5)" sits in the families column, and the guided column's checkpoint is not stated (new 8) |
| 15 | "within reach" against its own definition; 12 vs 14 | fixed | The definition is now rate-only with a weak-evidence flag; §3.4 gives 7,168–10,240 attempts per member; the text says "twelve of the fourteen are on family members" |
| 16 | terminology collisions | partly | "Bar" and "at the bar" are gone from the text, and the verdicts are in small caps. Still: at least 6 non-technical uses of "reach", against App. H's claim (new 15); "seeded" next to "seeds" (new 14); "contrap. conv." in Fig. 3b; "classical contraposition" in the blog |
| 17 | per-seed slash tuples | partly | §3 now uses comma lists, though still of six numbers each. §4 keeps about 15 slash tuples ("34/33/33 to 21/20/14", "232/236/234", "3/4/1 of the 22/21/14") |
| 18 | redundancy | partly | The power-sampling caveat and the Abdulsalam comparison are consolidated, but there are new repeats (new 13) |
| 19 | estimator statements; counts that do not add up | fixed | "2–3-fold" is used consistently, and all four bins are listed, including n = 2. Residue: T = 1 (§4) against T = 0.8 (§3.3 and the estimator) is still unexplained (new 10) |
| 20 | "so what" late; tension with "amplify" | fixed | The intro's "What transfers" gives both lessons, and §6 says EI amplified rates near 10⁻⁴ (one seed) but not 10⁻⁶ |
| 21 | intro wording and contributions | fixed | e^3228 is gone, contribution 2 is reworded and the knockout comes first. Contribution 1 now over-claims "along every RL run" (new 11) |
| 22 | §3 sentences | fixed | The batch sentence, "derived line" and the EI paragraph are fixed. Residue: "one generated theorem" (every member is generated), and "The training budget is the same for every theorem" is vague (new 21) |
| 23 | §6 and "Interface" off the main line | fixed | Test-time compute is folded into §4 and Interface moved to §7, but the Interface sentence still does not parse (new 15) |
| 24 | hard-to-parse sentences | fixed | Most rewrites were adopted. The pre-filter sentence lost its scope (new 11) |
| 25 | typography and citations | partly | Thousands commas are gone from the exponents, p precision is unified and "instance-hours" replaces "pod-hours". ALiBi, NoPE, PUCT, G4ip, Boschloo and Clopper–Pearson are still uncited, Fig. 9 still has "1e-4" ticks, and Fig. 6's labels still overlap |
| 26 | subtitle lists methods | partly | The new main title is a question the design cannot answer (CREATED is unreachable), and the subtitle still lists methods (new 24) |
| 27 | no schematic | fixed | Fig. 1a, with small accuracy problems (new 6) |
| 28 | no displayed equations | fixed | Three displayed definitions. 𝒞(K) and Δ_cov are still prose and are ambiguous (new 4) |

### Blog

| # | round-1 issue | status | evidence |
|---|---|---|---|
| 1 | opening overstates the paper | fixed | It leads with 5/6 vs 0/6 during RL, defines learning a family, says the best knockout run proved 2 of 106, labels the dose exploratory and says "this kind of RL" |
| 2 | σ conflated with its free positive form | fixed | The "σ shows up in two situations" paragraph and "genuinely classical use" throughout. The Lean comment still labels one step "σ" (B5) |
| 3 | "so what" and the GRPO caveat missing | fixed | "Why it matters" paragraph, a GRPO bullet in §7 and GRPO in §8 |
| 4 | over length | fixed | 2,495 words by `wc -w`. It is at the cap, so every fix below needs an offsetting cut |
| 5 | text and figures disagree | fixed | "−19" is gone, the equal-k point is noted as off the edge and the family definition is in the Fig. 1 caption. Fig. 1's round-20 point still has no tick (B9) |
| 6 | terms used before definition | fixed | Seeds, ¬ and →, intuitionistic and model organism are defined. Residue: "organism" appears in the short version before §1 defines it; "pre-registered" is undefined (B7) |
| 7 | statements stronger than the paper | fixed | Recount scope, seed counts, pre-registration wording, "consistent with" and "public" are all fixed. The second likelihood caveat (the scored proofs are the full runs' own) is missing |
| 8 | caveats the paper gives | partly | (d), the compute mismatch, is in the text but not the caption. Still missing: (a) the amendment, (b) old vs new full runs (2/3 vs 0/6, p = 0.034) and (c) the textbook deficit persisting; the replay confound is missing too (B3) |
| 9 | figure nits | partly | Fig. 1's title now says "in 16 rounds". Unchanged: the round-20 tick, Fig. 4's right-panel y-label and the undefined "hardest" |
| 10 | voice and wording | partly | The tree-search sentence is fixed. "I" in the epistemic status, the Lean comment and "106 of their instances" are unchanged |

---

## New issues: paper

### Major

**1. [major] Figs. 3–9 were not regenerated, so they now contradict the text.**
*Location:* `figures/fig1_endpoint`, `fig2_dynamics`, `fig3_logp`, `fig4_budget`, `fig5_estimator`, `fig6_prior` and
`fig7_ttc` (paper Figs. 3, 4, 5, 7, 9, 6 and 8). All were written at 19:37–19:38, before the critique.
*Problem:* a reader moving between text and figure meets two vocabularies.
- **"pend" for r0** in five figures: the Fig. 3a and Fig. 5 x-axes, Fig. 6 ("base (pend)"), the Fig. 8a and 8b legends,
  and the Fig. 9a title ("pend s0–s2").
- **Sampling labels:** "plain read, k 256" (Fig. 3a), "(k 32 sample)" (Fig. 4b) and "at k 256" (Fig. 8a).
- **The acquisition criterion:** Fig. 3b's title says "at the bar, ≥ 50 %" where the text says "acquired". Fig. 3a is
  titled "Acquisition of the classical families" over a plot of theorem counts. Its y-axis reads "family members solved
  (of 106)", but la_transfer_916 is not a family member.
- **Fig. 4a:** titled "Targets that need the reductio", y-axis "strict trained targets solved (of 123)". The caption says
  "Strict training theorems (of 123) with an accepted proof so far".
- **Fig. 4b:** titled "Free reductio proofs per round".
- **Legends "knockout (no σ)"** (Figs. 4a and 6): these contradict §3.3's "rare, not absent", since those models write σ
  from round 1.
- **Fig. 5's title, "Distance to the reductio":** a log-probability is not a distance.
- **Fig. 7's legend:** "target attempts", "training phases" and "as published" do not match Table 6's row names, and the
  subscripts are typed "K_att".
- **Fig. 8b's axis:** "long rrQ100", "long2" and "group C" are defined only in the caption.
- **Family abbreviation:** "contrap. conv." (Fig. 3b) against "conv. contrap." (Table 2, App. C).
- **Spacing:** "1 %" in the figures, "1%" in the text.
- **Unfixed round-1 defects:** the unlabelled colour bar (3b), the legend lying over the lines at rounds 2–5 (4a),
  overlapping labels for s0, s2, s3 and s4 (6), and "1e-4–1e-3" ticks (9b).

*Fix:* one pass through `scripts/figures.py` with a label map, then rebuild.

| old label | new label |
|---|---|
| pend | r0 |
| plain read, k 256 | evaluation, k = 256 |
| at the bar | acquired (≥ 50%) |
| targets | training theorems |
| free reductio | free positive reductio |
| knockout (no σ) | knockout (σ removed from pretraining) |
| family members (of 106) | strict held-out theorems (of 106) |
| Distance to the reductio (Fig. 5) | log-probability of known σ proofs along each ladder |
| Fig. 7 legend | Table 6's row names, with `$K_{\rm att}$` mathtext |
| Fig. 8b ticks | "unsolved by r0 and r8 (28–36)", "textbook72", "holdout250", "long (100)", "longer (21)" |

Also: label the colour bar "share of strict held-out members proved", move Fig. 4a's legend to the lower right, repel
Fig. 6's labels and use 10⁻⁴ tick labels in Fig. 9b. Before building, grep the figure script for the old labels.

**2. [major] "σ-free" still contradicts itself, and σ still means two things in the intro.**
*Location:*
- abstract ("The knockout bases were not σ-free");
- §3.1 ("from a σ-free base below 0.39") and §7, "Seeds and power" ("from a σ-free base");
- §1, "Two objections" ("should find at most 0.02 σ proofs per round");
- "free reductio" in §3.4's first sentence, §6's reading 3 and the Fig. 4b title.

*Problem:*
- **"σ-free" for models.** The abstract denies that the bases are σ-free, while §3.1 and §7 call them σ-free bases.
  REVISIONS C1 says "σ-free" is kept only for data, yet all three of its uses in the text describe models.
- **σ in the intro.** The null says the bases should find "at most 0.02 σ proofs per round". The next paragraph says the
  ladders "wrote σ from round 1" (6–13 per ladder in round 1, §3.3). Both are true only because the first means σ on
  strict theorems, that is, a free positive reductio. A reader who has just learnt Table 1's distinction sees the intro
  ignore it.
- **Spelling.** "Free reductio" is a fourth name for the free positive reductio.

*Fix:*
- Abstract: "The knockout bases were never trained on σ, yet five of six proved held-out theorems with it 1–7 times in
  1.1–1.5 million attempts."
- §3.1 and §7: "from a knockout base".
- Intro: "… should find at most 0.02 proofs of strict theorems per round".
- Replace "free reductio" with "free positive reductio" in all three places. Then `grep -n 'free reductio\|sig-free base'
  sections/*.tex` should return nothing.

**3. [major] Two different "5/6 against 0/6, p = 0.0032" contrasts sit in adjacent paragraphs.**
*Location:*
- §3.1, paragraph 2: "Applied to the bases, the indicator already gives 5/6 against 0/6 (p = 0.0032)".
- §3.1, paragraph 3: "Counting only families acquired between r0 and r16, it is 5/6 against 0/6 (p = 0.0032)".
- The abstract and intro quote the second. The blog does the same (B11).

*Problem:* the paper's RL-specific headline, families acquired during RL, has the same split and the same p as the r0
indicator, which the paper itself calls "a weak statement about RL". A reader will conclude either that the during-RL
result restates the r0 result or that one of the two is a typo. In fact different seeds produce the two splits:
- full s1 had no family at r0 and acquired three during RL;
- full s4 had converse contraposition at r0 and acquired nothing new.

*Fix:*
- After the second test in §3.1, add: "The split equals the r0 split, but with different seeds: full s1 had no family at r0
  and acquired three during RL, while full s4 had one at r0 and acquired nothing new."
- In Table 4, bold the families acquired during RL as well as underlining the r0 families, so the reader can count the
  5/6 directly.

**4. [major] The reorder left definitions behind, and several symbols are overloaded.**
*Location:* §2 ("Budgets, reach and certificates" and the decision rule), §3.3, Table 5, §3.5, §4 ("The budget") and §6
("1/(rkN)").
*Problem:*
- **Forward reference.** K_att, K_train, K_uni, K_pub and K_adapt are defined in §4, after the §2 decision rule, §3.3,
  Table 5 and §3.5 have all used K_train(16). The "(16)" index is never explained; it is the budget charged through round
  16. App. D gives r16 values but not the notation.
- **The reach states do not cover the cases.** §2 defines three states: within reach (p̂ ≥ 1/K), not reached (c = 0 with
  n ≥ K) and certified. They are not complementary: a theorem with 0 < p̂ < 1/K is in none of them. §2 then defines 𝒞(K)
  as the theorems "its base cannot reach within K" without saying which state that means. "Not reached" is never used
  again in the main text.
- **c and C.** One paragraph uses c (successes), c_base (cost per attempt), C_RL (compute) and 𝒞(K) (a set).
- **K and K12.** The pretraining sets are called K12, K12⁻ and K12^{1%}, while K is the budget (K_att, K_max,
  "K = 17,189"). "K12⁻" reads like a budget.
- **r and N in §6.** "1/(rkN)" uses r for a rate, though r8 is a checkpoint, and N for problems, though rN uses N for
  rounds. r is never defined.

*Fix:*
- Move the four allocation sentences from §4 into §2 and define the index: "K_a(N) is allocation a's budget for a ladder
  run to round N; §4 uses N = 8 and drops the index."
- Display both definitions:
  - 𝒞(K) = {t : RL proves t and p̂_base(t) < 1/K}, decidable only where n ≥ K or a success exists;
  - Δ_cov(K) = #{t : RL proves t} − #{t : p̂_base(t) ≥ 1/K}.

  Drop "not reached", or use it in Table 6's row "no base success in ≥ 66,304 attempts".
- Rename the successes s (or the cost κ), and the set 𝓜(K), the "matched set".
- Rename the data sets D_full, D_ko and D_1%, in the figures too.
- §6: "about 1/(p k N) rounds, where p is the per-attempt rate, k = 32 the attempts per theorem per round, and N the number
  of training theorems that need the step".

**5. [major] Length and balance are unchanged, and the Discussion now carries new results in lab shorthand.**
*Location:* whole paper; §6, "Earlier organisms point the same way, and further"; §3.5–3.8; §4, "Test-time compute".
*Problem:*
- **Balance.** The paper has 20 pages of main text and 5 of appendix, which is the wrong way round for a venue.
  Secondary analyses sit in the main text: §3.6's AUCs and Spearman values, §3.7's nulls, §3.8, §4's test-time-compute
  paragraph with Fig. 8, and Table 7.
- **New results in the Discussion.** §6 introduces four bulleted results from other organisms (rates, rounds, 12/12 vs
  1/3) that appear nowhere in §3 or §4.
- **Undefined shorthand.** "ignition"/"ignited", "dead arms", "dead seeds", "a sibling's found proofs", "reductio and
  depth-3", "depth-3 box-nesting habit", "a rare 85M draw that read 0 of 300", "paired EI", "the checkpoints are lost".
  "Interplay" (§6, "EI or RL?") is a nickname for Zhang et al. that is never introduced.
- **Two sentences do not parse.**
  - "On the full bases, replay alone, or 16 proofs of other theorems, gave none." None of what? And why full bases, in an
    experiment on no-DN bases? Why 39 members, when excluded middle has 40 held-out members (37 strict)?
  - "a pattern the base produces rarely or not at all is acquired when it is injected, even as one proof given a few
    rounds, or found by GRPO."

*Fix:*
- Move the earlier-organism bullets to a new appendix, with the older-checker caveat. Keep three sentences in §6:
  > "In earlier whole-proof organisms (3.2M–85M parameters, an older checker), EI took off on exactly the bases that
  > already emitted the reductio (4 of 11). A single injected proof started it on bases that did not, and GRPO acquired a
  > related pattern in 12 of 12 runs where EI did in 1 of 3 (App. K). Here, bases pretrained with no DN at all learned
  > excluded middle from 16 demonstrations (35–37 of 39 members, three seeds), while the controls gained none."

  Check the control sentence against LEDGER P129.
- Replace "Interplay" with "Zhang et al.".
- Cut plan to about 6,500 words (about 13 pages) without losing a result:

  | cut | words saved |
  |---|---|
  | intro "Results" bullets to one line each | ≈250 |
  | data shares in §3.2 and §3.5 → columns of Table 3 (new 13) | ≈120 |
  | delete §3.5 "What this means" (it repeats §6's reading 4) | ≈90 |
  | §3.6 to three sentences plus an appendix | ≈200 |
  | §3.7 and §3.8 to two sentences each plus an appendix | ≈350 |
  | §4's test-time compute and Fig. 8 to an appendix, one sentence left | ≈300 |
  | §6's earlier organisms to an appendix | ≈300 |
  | merge §6's "What transfers" with the intro's | ≈150 |
  | Table 7 to the appendix | — |

  The same plan, applied harder, reaches about 5,000 words for a 9-page venue.

**6. [major, quick fix] Figure 1 overstates the design and plots counts while claiming families.**
*Location:* Fig. 1 and its caption (p. 2).
*Problem:*
- **"Differ only in σ."** The caption says "Three pretraining sets that differ only in the classical reductio σ". §3.5
  says the knockout also makes each constituent "three to four times rarer" and removes two thirds of the classical-only
  theorems. The most-read figure states the cleaner design that the paper itself disclaims.
- **σ vs σ⁺.** Panel (a) reads "Knockout: σ records removed (16,961)". The 16,961 are σ⁺ records; there are 16,703 σ
  records (§2). The Full box says "σ or a variant", and the Knockout box should too.
- **"K12"** appears before §2 defines it.
- **Counts, not families.** Panel (b) plots theorem counts, while the caption's claim is "No knockout seed acquires a
  classical family". Nothing in the panel shows a family.
- **Duplicate.** Panel (b) shows the same data as Fig. 3a, so the paper plots it twice.
- **Missing step.** The schematic stops at EI, without the 106 held-out strict theorems.
- **Footnote size.** σ's definition sits in a grey italic footnote of about 5 pt in print.

*Fix:*
- Caption (a): "Three pretraining sets of 155,000 proofs: full; knockout, with every proof that uses σ or a variant (σ⁺)
  removed and replaced; and a 1% dose with σ restored. The knockout also makes ¬-introduction and DN 3–4 times rarer
  (§3.5)."
- Knockout box: "16,961 σ/σ⁺ records removed, refilled to 155,000". Drop "K12" from the boxes.
- Panel (b): draw each seed's r16 marker filled if the seed acquired a family and open otherwise, and add the dashed s1
  continuation to r24.
- Add a final box: "evaluate on 106 held-out strict theorems (never trained on); acquired = ≥ 50% of a family".
- Set the footnote in black at 7 pt or more.
- Drop Fig. 3a and make Fig. 3 the full-width heat map.

### Minor

**7. [minor] "Acquire" is a defined term, but it is also used for compositions and for theorem counts.**
*Location:*
- abstract, last sentence ("did not acquire it", where "it" is the composition);
- §3.6's title, "The base's prior predicts what RL acquires" (what it predicts is theorems proved);
- Fig. 6's title, "Base prior and later acquisition", over a y-axis of theorems proved;
- §6: "exposure decides whether this EI acquires it" and "a pattern … is acquired when it is injected".

*Problem:* §2 defines acquiring a family as proving at least 50% of its strict held-out members in one evaluation. Using
the same verb for a composition, which is never defined, and for theorem counts lets a reader take §3.6 to be about
families.
*Fix:*
- Define the composition sense once in §2: "EI acquires the composition if the ladder acquires at least one family that
  needs it."
- §3.6's title: "The base's prior predicts what RL proves (exploratory)". Fig. 6's title: "Base prior and theorems proved
  at r16".

**8. [minor] Table 4 needs four small fixes.**
- **The s1 continuation.** "– (r20: 5; r24: 5)" sits in the "acquired at r16" column, where it reads as five families.
  Move it to a footnote: "Knockout s1 continued: 5 strict theorems at r20 and r24, no family."
- **The guided column.** It is at r16, but §3.1 cites the guided evaluation at r0 ("6/6 in the guided evaluation"), which
  the table does not show. Change the header to "r16 guided" and give the r0 guided indicator in the caption.
- **Dose rows.** The x1 and guided cells are blank, although App. I has 56/39/30 and 58/42. Fill them in (s2 guided
  "pending").
- **During-RL families.** Bold them (new 3).

**9. [minor] Table 6 reads as one funnel, but it branches.**
*Location:* Table 6 and §4, "Brackets, certificates and controls".
*Problem:*
- **Alternatives, not filters.** Rows 2–6 are alternative budgets. The row "𝒞(K_pub) net of the replay-only control"
  then jumps back from K_adapt to K_pub.
- **Undefined terms.** "Net of" is never defined (does it mean removing the theorems the control proves?), and nor is the
  caption's "each seed's strictest set".
- **Order.** The controls are defined after Table 6 and after the sentence that uses them.
- **Shrink factor.** The caption says the sets shrink "by a factor of 3–4". By the table's own numbers it is 2.6–4.3
  (54→21, 51→20, 60→14).
- **Reference budget.** Nothing says why K_pub is the reference for the lower rows.

*Fix:*
- Split the table into panel A, "Budgets (alternatives)", and panel B, "Filters applied to 𝒞(K_pub)". Add one sentence
  on why K_pub is the reference (give the true reason).
- Define the term: "net of the replay-only control: theorems that control proves are removed". Name the actual set in
  place of "strictest set" (for example 𝒞(K_adapt)).
- Write "by a factor of 2.6–4.3", and move the two control bullets above the table.

**10. [minor] §4 and §3.3 use terms they never define.**
- **§4, test-time compute:**
  - "the ceiling" (250, or the union over models?);
  - "six r8 models" (the section is about s0–s2);
  - "by 5.2–10.3 points" (points of what?);
  - "its pre-registered gate" (what gate?);
  - "compute-matched creations" (this is 𝒞(K_pub));
  - "The cheaper control": write "Replay-only, the cheaper control, …".
- **The known-proof estimate sentence splits its own noun phrase.** Rewrite: "The known-proof estimate E(t) is the base's
  total probability of every Lean-accepted proof of t that any model found, summed over the 33 line-numbering offsets
  (teacher-forced, T = 0.8)." E is the symbol Fig. 9 already uses.
- **Temperature.** T = 1 in §4's "Likelihoods along RL" against T = 0.8 in §3.3 and the estimator is still unexplained.
  Add "(T = 1, the model's own distribution; elsewhere T = 0.8, the sampling temperature)", if that is the reason.
- **§3.3, "Likelihood":** say why 101 of the 106 are scored ("the 101 with a known σ proof"). The box-step comparison
  quotes one full base (−10.5), while the median quotes four.

**11. [minor] Four statements say more than their sources.**
- **Contribution 1** promises "likelihoods of known proofs along every RL run". The full s0–s2 ladders were not rescored
  (Fig. 5 caption). Write "along 12 of the 15 ladders".
- **§3.8** says "Every rejection in the experiment was the pre-filter's". Its source (LEDGER P83) is knockout s1's dump.
  Write "In knockout s1's ladder every rejection was the pre-filter's (Lean accepted every text that passed it), so …".
- **The Fig. 4 caption** says "Four knockout ladders write a few, late". By §3.3, s5's first free positive reductio came
  in round 2, and five knockout ladders write at least one. Write "Knockout s2–s5 write 1–16 in 16 rounds (s5 from round
  2); s0 writes none."
- **§3.3** says "The two certified-on-105 bases (s0, s3) never produced one". s3 did produce a free positive reductio
  (round 15); "one" means a strict training success. Write "… never proved a strict training theorem." Also state that the
  waiting-time rates are pooled over the 105 family members, which is why s3's rate is zero, while Table 5 uses 106.

**12. [minor] The dose result is hedged in §3.2 but not in the abstract or the intro.**
*Location:* abstract ("Restoring σ in 1% of pretraining restored acquisition (3/3 seeds)"); the intro bullet "One
percent is enough"; §3.2's heading.
*Problem:* §3.2 calls the arm exploratory, and §7 says two doses cannot locate a threshold. The abstract and the heading
drop the hedge, and "Restoring … restored" is clumsy.
*Fix:*
- Abstract: "Putting σ back into 1% of pretraining records restored acquisition on 3/3 seeds (exploratory)."
- Heading: "A 1% dose restored acquisition (exploratory)".

**13. [minor] The same numbers appear two or three times.**
- **Data shares.** The DN, ¬-introduction and classical-only shares appear in §3.2, again in §3.5, and in part in §7. Add
  them to Table 3 as three columns and cite the table.
- **"What transfers".** The intro's paragraph and §6's "What transfers to larger models" with its two bullets say the
  same thing. They differ in the rate ("up to about 5×10⁻⁴" against "near 10⁻⁴") and the subject ("this RL" against
  "this EI"). Keep §6's version, leave one sentence in §1, and use "this EI" and one rate in both.
- **Interpretation.** §3.5's "What this means for the interpretation" repeats §6's reading 4.
- **Intro bullets.** The "Results" bullets restate about 15 of the abstract's numbers.
- **Figures.** Fig. 1b duplicates Fig. 3a (new 6).

**14. [minor] Seeds come in four kinds and several spellings.**
*Location:* throughout, including App. I's C2.
*Problem:*
- **Four kinds.** Training seeds (s0–s5); "sampling seeds" (Arms: "share initial weights and sampling seeds"); the
  evaluation "sample seeds" x0 and x1, which App. I calls "sample seed 0/1"; and the "seeded round".
- **Spellings.** A training seed is written "knockout seed 1" (8×), "knockout s1" (3×), "full seed 0", "full s3", "dose
  seeds 0 and 2" and "dose s0", and very often as a bare "seed N" with the arm left implicit.
- **Collisions.**
  - App. I's C2: "A second plain evaluation (sample seed 1) of dose r16 seeds 0, 1 and 2".
  - §3.7: "Seeded minus control was +0, … on seeds 0, 1, 2, 3 and 5".
  - The same intervention is "seeded" in §3.7 and App. G but "injected" in §3.7's last sentence and in §6.

*Fix:*
- Always write a training seed as "arm s#" ("knockout s1", "full s3").
- Always write the evaluations as x0 and x1.
- Say "sampling RNG" for "sampling seeds".
- Call the §3.7 intervention "proof injection" ("Injected minus control was …").

**15. [minor] "Reach" still has non-technical uses, contrary to App. H.**
*Location:*
- §1 and §6: "reached a strict training theorem" (three times);
- §4: "Neither method reaches most of the compute-matched creations";
- §6: "none of six knockout bases reached it in 16 rounds" (bases do not change over rounds; ladders do);
- §6: "reaching 44 and 65 targets";
- §7, "Interface": "reached most of the theorems".

App. H claims "reach" is used "only in its technical sense".
*Fix:*
- Use "first proved a strict training theorem", "recovers", "none of the six knockout ladders got there in 16 rounds" and
  "proving 44 and 65 training theorems".
- Rewrite the Interface bullet:
  > "In an earlier 3.2M organism, giving the base the proof-state interface let it reach most theorems that whole-proof EI
  > had 'created' (two seeds per arm). The interface changed two things at once, the visible proof state and step-by-step
  > generation, so their effects are not separated."

**16. [minor] Process artifacts a venue reader will stumble on.**
- **References.** 53 rendered references carry "Version read: vN", at least six of them "(abstract only)" and others
  "(abstract and two sections)" or "(method and selected tables)". REVISIONS N11 says these hedges were removed, but they
  are still in the `.bib` `note` fields (88 entries). Strip them.
- **Session labels.** "(this paper)" appears 11 times and "run for this paper" 4 times in §3. Also: "This writing run"
  (App. I), "reviewed reports" (§4), "the experiment's reports" and "The review's ten rewordings" (App. H), and
  "results-registry rows" and "Lean-gate dumps" (§8).

  A reader cares whether an analysis was pre-registered, not which work session computed it. Replace "(this paper)" with
  one mark meaning "not in the original pre-registration". Describe the earlier reports once ("our earlier internal
  reports, App. J"), and cut App. H's last two sentences.
- **Bibliography.** Havrilla et al. [13] and Singh et al. [40] lack a venue or arXiv id.

**17. [minor] Four appendices are never referenced from the text.**
No `\ref` points to App. A (glossary), App. B (knockout construction), App. C (first-family rounds) or App. G
(pre-registered expectations against outcomes, which round 1 called exemplary).
*Fix:*
- Put "(glossary: App. A)" at the start of §2.
- Cite App. B in the Arms bullet, and App. C after "No knockout ladder ever had proofs for half of any family's strict
  training theorems".
- Cite App. G in §8's "Pre-registration" paragraph.

**18. [minor] App. I's C1 baseline does not reproduce Table 4, and nothing says why.**
*Location:* the C1 table against Table 4, §3.8 and §7.
*Problem:*
- **Counts.** C1's standard-cap counts are knockout s1 3 and dose s2 28, where Table 4 has 2 and 30.
- **Cut-off shares.** C1's standard-cap shares (5.09% and 9.30%) exceed the maxima in §3.8 and §7 (4.97% and 8.84%; "up to
  8.8%").

A careful reader will conclude that one of the tables is wrong.
*Fix:* add one sentence to C1: "The standard-cap run is a fresh batch-512 draw, so its counts and cut-off shares differ
slightly from Table 4's evaluation (knockout s1: 3 vs 2; dose s2: 28 vs 30). The comparison is paired within C1." Then
change §7's "up to 8.8%" to "up to 9.3%".

**19. [minor] App. E's listing (a) cannot be read: ∧ and ∨ do not render.**
*Location:* pp. 26–27. The PDF shows "((S   R)   R)", and pdftotext returns U+FFFD there. The listings `literate` option
maps U+2227 and U+2228, but the glyphs are still missing, probably because the typewriter font lacks them under tectonic.
*Fix:* load a monospace font that has the glyphs (via fontspec), or replace the symbols in the listing. Verify with
`pdftotext main.pdf - | grep -c $'\xef\xbf\xbd'` → 0.

**20. [minor] The abstract and intro, for a reader outside logic.**
- **Why σ matters.** Neither says it. Add one sentence: "Without DN, natural deduction is intuitionistic logic, in which
  excluded middle and Peirce's law are unprovable; σ is the most direct way a proof recovers them."
- **"Knockout"** is used (abstract: "No knockout seed"; intro: "the knockout bases") before it is introduced as the arm's
  name in §2. Abstract: "We remove … from pretraining (the knockout), keep both of its rules (¬-introduction and DN) …".
  "Both of its rules" currently follows a three-step gloss, so name the rules.
- **"Ladder"** is used in the intro's "Results" bullets before §2 defines it. Say "RL run" in the intro.
- **"Model organism"** (intro, paragraph 3): add "(a small system we can fully control)".
- **Intro, bullet 1:** "which bounds the per-seed rate below 0.39" → "which bounds below 0.39 the per-seed probability
  that this EI acquires a family from a knockout base".

**21. [minor] Sentence-level rewrites.**
- **§3.1, the amendment** (a five-line parenthetical inside a sentence). Move it to a footnote:
  > "The pre-registration first named looser held-out sets (178 theorems). After round 1 of the first knockout ladder,
  > that base was found to prove 136 of 155 generated 'classical' targets through a ¬¬ the sequent supplied, so a dated
  > amendment replaced the looser sets with the strict ones. The result is the same on the original sets."
- **§3.3, early stopping.** "with sampling on a theorem paused after its first success in each block of 1,024" → "Attempts
  were drawn in blocks of 1,024 per theorem, and a block stopped at its first success, so each block contributes at most
  one success per theorem." Use the same wording in §3.4 ("without early stopping") and §7.
- **§3.3, first rounds.** "first in rounds never, 9, 12, 15, 15 and 2" → "first in rounds 9, 12, 15, 15 and 2 (s1–s5;
  s0 never)".
- **§3.5, "General ability".** The units switch from counts to proportions and back: "By r16 the holdout250 gap closes
  (0.996 vs 0.996), while textbook72 keeps −2.5." → "By r16 both arms prove 99.6% of holdout250's 225 intuitionistically
  provable theorems, while on textbook72's 53 the knockout still trails by 2.5." Use "intuitionistically provable" in App.
  G too, which says "non-classical".
- **§3.7, "Power sampling".** "(0/33, 0/27)" and "proved 1–2" have no referents. Say which seeds and which sets, for
  example "none of the 33 and 27 theorems RL r8 proves beyond its base's reach (full s0, s1) … plain sampling with the
  same decoded tokens proved 1–2 of the 106".
- **§2, EI.** "The training budget is the same for every theorem." → "Every training theorem gets the same 32 attempts
  per round."
- **§2, decision rule.** "and the knockout base is certified out of reach on it": there are six bases. Say which: per
  seed, or pooled over the family's members, as the pre-registration states.
- **§5.** "Pretraining at a low contraction weight ρ 'never reliably enters the macro or parallel regime'" is opaque
  without their paper → "with few shortcut-adjacent examples in pretraining (low ρ), their models never reliably learn
  the shortcuts".
- **§6's heading "EI or RL?".** The abstract calls EI a form of RL → "Specific to EI?".
- **§8.** "were pre-registered as well … Two of them are post hoc" → "were pre-registered, except two post hoc analyses
  (A2, A5), labelled as such".
- **§3.1.** "Holm-corrected over six families, 0.0015" → "Holm-corrected p = 0.0015".
- **"One generated theorem"** (§2, Table 2, §3.3): every member is generated → "one non-family theorem".

### Nits

**22. [nit] Layout.**
- **Table 1:** the 3.0 cm term column hyphenates "reduc-tio" twice (p. 5). Widen it to 3.6 cm with `\raggedright`.
- **p. 16:** the heading "Four readings of the null." is stranded at the foot of the page.
- **p. 10:** the captions of Figs. 5 and 6 start at different heights. Use `minipage[t]` with images of equal height.
- **Arm order** varies:

  | where | order |
  |---|---|
  | Fig. 1 | full, dose, knockout |
  | Table 3 | full, knockout, dose |
  | §2, Arms | knockout, dose, full |
  | Table 4 | full, knockout, dose |
  | Fig. 3b | full, dose, knockout |

  Pick one.

**23. [nit] Table 1 details.**
- σ⁺'s parenthetical lists "→-introduction, ∨-elimination, …". App. B lists the 258 non-σ records as citing
  "→-elimination, ∨-elimination, ⊥-elimination, DN or ∧-elimination" lines. App. E(b) says no pretraining set contains DN
  on a →-introduction line. Give one list.
- "Strict member" is defined for family members, but the text counts "106 strict held-out theorems", which include
  la_transfer_916. Add a row for "strict theorem".

**24. [nit] Small inconsistencies.**
- **Pretraining time:** "1,200 s" (§2) against "≈1,280 GPU-seconds" (Table 7 caption).
- **"Held-out" names three sets:** 5,000 generator theorems, holdout250 and the 106. Name all three in §2, and introduce
  "textbook72" and "holdout250" where §2 first describes the 322; they are first named in §3.5.
- **App. C** uses "–" (per seed) and "never" (whole row) without saying so. Its title ("When each ladder first trained on
  each family") does not describe its content (the first round with proofs for half a family's strict training
  theorems).
- **Fig. 9b:** "106 pairs" collides with the 106 theorems → "106 (seed, theorem) pairs".
- **Citations:** ALiBi, NoPE, PUCT, G4ip (Dyckhoff 1992), Boschloo and Clopper–Pearson are uncited. Expand GRPO at first
  use (§1).
- **Title:** "Did Expert Iteration Create It?" asks the question the design cannot answer (§2: CREATED "could not be
  returned"), and "It" stays unresolved until the subtitle. A declarative title gives the busy reader the result, for
  example "Expert Iteration Amplifies but Does Not Acquire a Composition Removed from Pretraining: A Knockout in a
  From-Scratch Prover".

---

## Blog (`paper/blog.md`)

It is 2,495 words by `wc -w` (2,414 without the code block), has 4 figures and is in plain language with "so what"
first. The round-1 fixes landed. The remaining problems are fidelity and three omitted caveats.

**B1. [minor] The decisive family has the wrong name.** §3's first bullet says "One family (classical contraposition)".
The paper's family is converse contraposition, the subject of its only NEEDS EXPOSURE verdict. → "converse contraposition
(from 'not B implies not A', conclude 'A implies B')".

**B2. [minor] A number the paper does not contain.**
- **The gap.** §6 says "Guided redraws closed about half of the gap between the base and the RL model on one held-out
  set". The revised paper no longer states this (LEDGER P87: 44/31/37 → 21/14/19 on holdout250). Either restore one
  clause in paper §4, or write "added 18–22 held-out theorems for the base and −1 to +4 after RL".
- **The ceiling.** The Fig. 4 caption's "236–240 of the 250" and the paper's "within 3–14 theorems of the ceiling" should
  give the same numbers.

**B3. [minor] Caveats the paper gives and the blog omits.** The brief asks for the same evidence, nulls included.
- (a) The three older full-data runs used other hardware for rounds 1–8. On the three new ones alone, the during-RL
  contrast is 2 of 3 against 0 of 6 (p = 0.034). Add this to §3's Statistics bullet.
- (b) The design cannot separate pretraining exposure from the replay of pretraining data during RL. Add it to §7's "isn't
  perfectly clean" bullet.
- (c) The seeded-round null in this organism: one extra round with four copies of a classical proof gave +0 on four runs
  and +2 on one, and one round is too short to test seeding. Add it before "In our own earlier, smaller models…".
- (d) Fig. 4's caption: add "Guided redraws cost about twice the compute per attempt."

Each addition is 25 words or fewer.

**B4. [minor] "A few units at most" understates the paper.** §4, "Likelihoods mostly agree": "the rest, knockout runs
included, moved a few units at most, up or down". The paper gives −7.6 to +3.7 nats for the knockout ladders, with
several rising 5–8.5 by round 4 and then falling back. → "the rest moved less, up or down (the knockout runs by −8 to
+4)".

**B5. [nit] σ still names a single step in two places.** "We call that last combination σ" can be read as the final step
alone, and the Lean comment "-- drop the double negation: σ" labels one step. → "We call the whole pattern σ (sigma)" and
"-- σ: refute ¬S, then drop the double negation".

**B6. [nit] "Acquire" appears only once, and wrongly.** "this kind of RL … did not, within 16 rounds, acquire it from
models pretrained without it": RL does not acquire. → "and, within 16 rounds, did not teach it to models pretrained
without it". The blog's word elsewhere is "learn".

**B7. [nit] Terms used before definition.**
- "organism" (the short version; §1 defines it);
- "pre-registered" (epistemic status: "we wrote the test down before running it");
- "non-classical theorems" (§7: "ordinary theorems that don't need σ");
- "K" in Fig. 3's caption (the axis says "budget", so drop K).

**B8. [nit] An attempt range the paper does not give.** §4 says "in roughly 2,000 to 10,000 tries each". The paper gives
7,168–10,240 for the converse-contraposition members and no figure for la_transfer_916, whose 2,048 is the "2,000". Add
the 916 count to paper §3.4, or write "in up to about 10,000 tries each".

**B9. [nit] Figures.**
- Fig. 1's round-20 point has no tick label, and the caption mentions only round 24.
- Fig. 4's right panel has no y-axis label, and "hardest" is undefined ("unsolved by both models in an earlier
  evaluation"). The left panel has no legend.

**B10. [nit] Voice and counts.** The epistemic status says "I would not generalise"; the rest of the post says "we". "We
hold out 106 of their instances" → "We hold out 106 theorems" (one is not a family member).

**B11. [nit] The 5/6 coincidence, for lay readers.** §3's first bullet says one family was learned before RL "on five of
the six", and the during-RL comparison is "five of six against zero of six". Add "(not the same five runs)".

**Word budget.** B1–B11 add about 100 words to a post already at 2,495. Offsets:
- drop §5's first sentence ("Before the knockout, we spent a lot of effort…"): −21;
- shorten the note under the code block to "(Simplified from the model's output; Lean accepts both and rejects the same
  proof of the opposite claim.)": −10;
- §4: "Whether that counts as eliciting a rare behaviour or creating a new one is, honestly, borderline." → "Elicitation
  or creation? Borderline.": −11;
- merge §7's "Six runs per main condition" bullet into one sentence: −15;
- §6: drop "We tried two ways." and fold the two definitions into the bullets: −10;
- §8: shorten the closing line to "Code, data and checkpoints are public.": −8;
- §4: drop its opening sentence ("The knockout models were not simply missing σ, and the details are the interesting
  part."): −14;
- §3's Statistics bullet: "and new families give five of six against zero of six (p = 0.0032)" → "and the new-family
  count gives p = 0.0032", since the Full-data bullet already gives the split: −6;
- the "Draft for Dan" line goes before publication anyway: −8.

These offsets total about 105 words. Re-run `wc -w` after editing.

---

## Pre-circulation checks (each a one-liner)

- `grep -n -E 'free reductio|sig-free base|reached a strict' sections/*.tex` → none.
- `pdftotext main.pdf - | grep -c -E '\?\?|Version read|pend\b'` → 0. This needs regenerated figures (new 1) and a
  stripped `.bib`.
- `pdftotext main.pdf - | grep -c $'\xef\xbf\xbd'` → 0 (new 19).
- Every `\label{app:…}` has at least one `\ref` (new 17).
- Run `wc -w blog.md` after the blog edits.
