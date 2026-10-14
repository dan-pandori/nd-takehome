# Equivalence check: clean paper vs. the marked reading copy

Independent check, 2026-10-14. Base: commit `11d07d13` (marked, 60 `\rv{}` marks). Compared with: the working tree's
`paper/main.tex` and `paper/sections/*.tex`. No `.tex` file differs between the working tree and HEAD `4e972d0f`.
Line numbers: **M** = marked copy, **C** = clean copy.

## Summary

- **Changed spans checked: 85.** That is main.tex 3, abstract 7, intro 13, related 2, setup 2, measurement 4,
  results 24, discussion 8, limitations 11, repro 1, appendix 1 and checks 9. They are:
  - 60 mark removals. Two of them also carry one of CLEANUP §1's smoothings.
  - 1 further §1 smoothing (the Holm sentence).
  - 20 spans from task-2 items 1 to 12.
  - 1 textbook72 span (§3).
  - 3 main.tex spans.
  `refs.bib` is unchanged, and no other `.tex` file feeds the build.
- **`\rv{}` spans confirmed: 60 / 60.** I took each mark's full corrected text from the review commit
  (`git diff 1ad2a691 11d07d13`) and searched for it in the clean copy.
  - 57 survive word for word.
  - 3 were reworded by the smoothings CLEANUP §1 lists. Every number, qualifier and caveat in them is kept.
  - None is dropped or weakened.
- **Must-fix: 0. Minor: 3.** M1 is the "under EI" wording in the abstract. M2 is that the discussion's "zero base rate"
  does not name its pool. M3 is that C4's batch size is stated for seed 1's draw only. There are also 6 notes that
  need no action (N1–N6).
- **Numbers.** I extracted every number from both copies, after removing labels, references and citations.
  - Number multisets: every digit added or removed comes from task-2 items 4–12 or from main.tex's box and date line.
  - Number words: every change ("three to four", "hundreds", "both", "none" and others) also maps to a listed item.
  - No unlisted number changed.
- **Hedges.** These qualifiers have the same count in both copies: post hoc 9, exploratory 9, pre-registered 56,
  not pre-registered 6, T = 0.8 15, T = 1 8, "106" 28, about 40, may/might/could/perhaps/likely 24, only 58,
  this organism 6, "independent draws" 2. Three gained one occurrence each: "this paper" (24 → 25),
  "within 16 rounds" (7 → 8) and "early-stopped" (6 → 7). "amplif-" lost one (10 → 9), the abstract's causal
  "amplified" (item 4).
- **main.tex.** Only three things changed: the `\rv` macro and its comment, the date line, and the reading-copy box.
- **CLEANUP.md's account matches the diff.** Every `.tex` change has a listed cause, and every listed paper change is
  present. Item 13 is blog-only and has no `.tex` change.

## Method

1. `git diff --word-diff=plain 11d07d13 -- paper/main.tex paper/sections/` gives every changed span.
   `git diff --stat 11d07d13 -- paper/` and `git ls-tree` confirm that the 12 `.tex` files are the only build inputs.
2. Number multisets per file, before and after, as digits and as number words.
3. Mark extents. Commit `11d07d13` applied the review's corrections to its parent `1ad2a691`. So
   `git diff 1ad2a691 11d07d13` shows each mark's full corrected text. Each corrected region, with `\rv{}` removed and
   whitespace normalised, was searched for in the clean copy (57 hits). The 3 misses were read by hand.
4. Counts of qualifiers and hedges across all sections.
5. Each task-2 change was read in context against the paper's own tables and other sections. Three spot-checks
   against data were cheap enough to run:
   - item 7 against `review_coep/members.log`;
   - item 8 against `artifacts/coe_paper/c4/ko_s{1,3}.json.args.json`;
   - item 12 against `artifacts/coe/power/p2*_plain*.json` and `artifacts/paper_clean/power_comparator_recheck.json`.
6. The new cross-references (`tab:concepts`, `sec:side`, `app:power`) all resolve to existing labels.
   Abstract length: 250 words by raw `wc -w`. The marked copy has 255 = 250 + five `\rv{}` tokens.

## Table: one row per changed span

Mark removals are written `X \rv{} Y`, meaning the mark was deleted and X and Y are unchanged. "Kept" in the caveats
column means the mark's full corrected text is still present.

| # | File: M → C | Marked → clean | Numbers OK? | Claim strength | Caveats OK? | Source | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | main.tex: 35–36 → — | comment and `\newcommand{\rv}{…[review]…}` removed | n/a | n/a | n/a | §1 | OK |
| 2 | main.tex: 43 → 41 | `Draft of 2026-10-13; reading copy with the review's corrections, 2026-10-14.` → `Draft of 2026-10-14.` | date only | n/a | n/a | §1 | OK |
| 3 | main.tex: 48–49 → — | reading-copy `\fbox` (commit ids, "Each change is marked \rv{}. No headline number changed …") removed | box only | n/a | n/a | §1 | OK |
| 4 | 00_abstract: 5 → 5 | `negation) \rv{} and its variants,` | yes | same | kept | rv 1 | OK |
| 5 | 00_abstract: 5 → 5 | `(each 3--4 times rarer)` → `(each 2.9--4.2 times rarer)` | 3, 4 → 2.9, 4.2 | same, more exact | n/a | item 6 | OK |
| 6 | 00_abstract: 7 → 7 | `half its \rv{} strict held-out members` | yes | same | kept | rv 2 | OK |
| 7 | 00_abstract: 11 → 11 | `\sig{} \rv{} (four on family members, mostly one family), 1--7 times in 1.1--1.4M` | yes | same | kept | rv 3 | OK |
| 8 | 00_abstract: 13 → 13 | `three earlier \rv{} 8-round` | yes | same | kept | rv 4 | OK |
| 9 | 00_abstract: 13 → 13 | `counts \rv{} and 14--34 at RL's compute as base attempts (14--21 under all five allocations)` | yes | same | kept | rv 5 | OK |
| 10 | 00_abstract: 14–15 → 14–15 | `In this organism EI amplified a composition pretraining had exposed, but within 16 rounds did not acquire the classical families without it.` → `In this organism, bases pretrained with the composition acquired classical families under EI, and within 16 rounds bases without it acquired none.` | 16 kept | weaker: causal "amplified" gone; "In this organism" and "within 16 rounds" kept | n/a | item 4 | **Minor M1** |
| 11 | 01_intro: 24 → 24 | `composition \rv{} and its variants` | yes | same | kept | rv 6 | OK |
| 12 | 01_intro: 25–26 → 25–26 | `though each becomes three to four times rarer.` → `though negation introduction becomes 2.9 times rarer and double-negation elimination 4.2 times.` | → 2.9 / 4.2 (15.21/5.19 = 2.93; 13.73/3.29 = 4.17, from §3 Data) | same, more exact | n/a | item 6 | OK |
| 13 | 01_intro: 31 → 31 | `to prove a positive goal $G$` → `to prove a goal $G$` | none | definition now matches Table 1 (σ has no positivity condition); not a hedge | n/a | item 1 | OK |
| 14 | 01_intro: 33 → 33 | `\rv{} Its variants, which apply DN to other derived lines, … (together σ⁺, 16,961 of the 155,000 records)` | yes | same | kept | rv 7 | OK |
| 15 | 01_intro: 68 → 68 | `including \rv{} seed 0, … at $T=0.8$ on the pre-registered pool of 106 theorems (at $T=1$, … 916 on it)` | yes | same | kept | rv 8 | OK |
| 16 | 01_intro: 72 → 72 | `(\rv{} $p = 0.006$--$0.020$ under the null)` | yes | same | kept | rv 9 | OK |
| 17 | 01_intro: 74 → 74–75 | `… 18,432 fresh attempts each.` → `… each, though two of those three had one success each in an earlier, early-stopped sample.` | adds "two", "one" (words) | weaker: caveat added | n/a | item 3 | OK (style N6) |
| 18 | 01_intro: 75 → 76 | `runs \rv{} (seeds s0--s2 of the same prover, after 8 rounds, on 322 evaluation theorems)` | yes | same | kept | rv 10 | OK |
| 19 | 01_intro: 76 → 77 | `counts. \rv{} Between 14 and 34 … depending on how that compute is counted; 14--21 … all five …` | yes | same | kept | rv 11 | OK |
| 20 | 01_intro: 86 → 87 | `amendment. \rv{} The certificate expectation, … was missed: one of six on the pre-registered 106 …, two of six on the 105 …` | yes | same | kept | rv 12 | OK |
| 21 | 01_intro: 104 → 105 | `problems that require the composition or a variant (here 123 of 4,495)` → `problems that need the composition, a variant or the lemma route of Table~\ref{tab:concepts} (here 123 of 4,495)` | 123, 4,495 kept | weaker: no longer says σ⁺ is required | n/a | item 2 | OK |
| 22 | 01_intro: 106 → 107 | `\item \rv{} \textbf{Cued practice did not yield a family within 16 rounds.}` | yes | same | kept | rv 13 | OK |
| 23 | 01_intro: 113 → 114 | `bases \rv{} prove none of the 106 … in the pre-registered evaluation (one proves one in a second draw)` | yes | same | kept | rv 14 | OK |
| 24 | 02_related: 9 → 9 | `established \rv{} in the initial evaluations (a 32k-token … between 11 and 61 samples)` | yes | same | kept | rv 15 | OK |
| 25 | 02_related: 26 → 26 | `at this scale;` → `at this scale within 16 rounds;` | adds 16 | weaker: scope added | n/a | item 11 | OK |
| 26 | 03_setup: 31 → 31 | `per attempt. \rv{} On plain reads of six earlier r8 models … (run guided-tts: …)` | yes | same | kept | rv 16 | OK |
| 27 | 03_setup: 42 → 42 | `($\neg(A\to B) \vdash A \land \neg B$)` → `(a negated implication entails its antecedent and the negation of its consequent)` | none | same | n/a | §3 | OK (N5) |
| 28 | 04_measurement: 85 → 85 | `(Fig. ttc). \rv{} Unless stated otherwise, the models here are the earlier full-exposure seeds s0--s2 at r0, r8 and r16.` | yes | same | kept | rv 17 | OK |
| 29 | 04_measurement: 96 → 96 | `textbook72. \rv{} Guided decoding does not recover most of the compute-matched creations` | yes | same | kept | rv 18 | OK |
| 30 | 04_measurement: 104 → 104 | `for \rv{} the earlier full-exposure seeds s0--s2:` | yes | same | kept | rv 19 | OK |
| 31 | 04_measurement: 107 → 107 | `wall-clock \rv{} (the same seeds at r0 and r8)` | yes | same | kept | rv 20 | OK |
| 32 | 05_results: 4 → 4 | `alone \rv{} (except the earlier organism's seeding result … labelled there)` | yes | same | kept | rv 21 | OK |
| 33 | 05_results: 59 → 59 | `no model proves. \rv{} The three undetermined verdicts at $p = 0.034$ rest on the Holm correction …` | yes | same | kept | rv 22 | OK |
| 34 | 05_results: 62–63 → 62–63 | `Holm is the conservative reading, and the review applied it too.` → `… and the experiment's review applied it too.` | none | same: names which review, matching the review's P10 row ("as the create-or-elicit review applied it") and App. "the experiment's reports and their review" | kept | §1 smoothing (inside rv 22) | OK |
| 35 | 05_results: 137 → 137 | `reach \rv{} (the pre-registered expectation of certificates on at least five of six bases missed; …)` | yes | same | kept | rv 23 | OK |
| 36 | 05_results: 141 → 141 | `member. \rv{} The certificate is also specific to $T=0.8$: plain sampling at $T=1.0$ proved 916 on this base (and on seed 1's; …)` | yes | same | kept | rv 24 | OK |
| 37 | 05_results: 196 → 196 | `rises to \rv{} 0.020` | yes | same | kept | rv 25 | OK |
| 38 | 05_results: 203 → 203 | `(Fig. logp). \rv{} The proofs are those the earlier full ladders (s0--s2) found, not the scored ladders' own.` | yes | same | kept | rv 26 | OK |
| 39 | 05_results: 254 → 254 | `which \rv{} two of the four plain r16 draws had already proved once (the guided draw, twice)` | yes | same | kept | rv 27 | OK |
| 40 | 05_results: 263 → 263 | `Seed 5's base proved 1811;` → `Seed 5's base proved 1811 and the Peirce-sequent member 1142;` | adds 1142 | same; count corrected (Table fambase already had Peirce sequent 1 success, at seed 5) | n/a | item 7 | OK (N3) |
| 41 | 05_results: 264 → 264 | `r20, \rv{} in four and three of the four plain r16 draws respectively` | yes | same | kept | rv 28 | OK |
| 42 | 05_results: 265 → 265 | `and 1811 in none.` → `and neither 1811 nor 1142 in any.` | adds 1142 | same; the zero is confirmed in members.log | n/a | item 7 | OK (N3) |
| 43 | 05_results: 266–267 → 266–267 | `1096 in both fresh draws (one of which also found 1963)` → `1096 in the other three plain r16 draws (one of which also found 1963)` | "both" → "other three" | same; count corrected (x1, C1 std, C1 dbl) | n/a | item 7 | OK (N3) |
| 44 | 05_results: 277 → 277 | `makes each constituent three to four times rarer` → `makes DN 4.2 times and ¬-introduction 2.9 times rarer` | → 4.2 / 2.9, from the same paragraph's 13.73 → 3.29 % and 15.21 → 5.19 % | same | n/a | item 6 | OK |
| 45 | 05_results: 283 → 283 | `−2.5 \rv{} on its 53 intuitionistic theorems (−7.5 on all 72)` | yes | same | kept | rv 29 | OK |
| 46 | 05_results: 289 → 289 | `Mann--Whitney \rv{} $p = 0.095$ (exact, allowing for the one tie; this paper)` | yes | same | kept | rv 30 | OK |
| 47 | 05_results: 295 → 295–296 | `a few theorems out of hundreds.` → `a few theorems: at r0, 4.3 of holdout250's 225 and 4.0 of textbook72's 53 intuitionistic theorems (2.5 of the 53 at r16).` | adds 4.3, 225, 4.0, 53, 2.5, all as in General ability (C 281–283) | weaker: the denominators are now explicit; "out of hundreds" made the cost look smaller | n/a | item 10 | OK |
| 48 | 05_results: 310 → 311 | `(dose). \rv{} One full seed (s3) … and one (s5) is below 0.5 (0.47) … holds on three of the four full seeds …` | yes | same | kept | rv 31 | OK |
| 49 | 05_results: 326 → 327 | `\rv{} (the 3.2M-parameter whole-proof models of round 2 run 3, judged by the project's older checker, not by Lean alone)` | yes | same | kept | rv 32 | OK |
| 50 | 05_results: 344 → 345 | `all 150 re-submitted Lean rejections,` → `all 150 re-submitted texts that the gate had rejected (all by its pre-filter),` | 150 kept | same; re-describes what the 150 were | n/a | item 5 | OK (N2) |
| 51 | 05_results: 345 → 346 | `sorry. \rv{} Every Lean-gate rejection … 72--88% … (77--89% with cut-offs) … only 10--23% reach it. Neither check below covers …` | yes | same | kept | rv 33 | OK |
| 52 | 05_results: 350 → 351 | `(\rv{} 222,135 rejected rows in rounds 1--16: 210,151 distinct texts, 21,055 …` | yes | same | kept | rv 34 | OK |
| 53 | 05_results: 352 → 353 | `at \rv{} $1.4\times10^{-5}$ per distinct text ($1.4\times10^{-4}$ …)` | yes | same | kept | rv 35 | OK |
| 54 | 05_results: 354 → 355 | `theorem. \rv{} An independent checker written for this paper's review also accepted none of the 210,151 …` | yes | same | kept | rv 36 | OK |
| 55 | 05_results: 359 → 360 | `attempts. \rv{} Same-seed re-evaluations … differ by at most one … they are independent draws, … sampling, not cap effects` | yes | same | kept | rv 37 | OK |
| 56 | 07_discussion: 8 → 8 | `De Morgan. \rv{} These per-family verdicts rest on the pre-registered Holm correction; uncorrected, three … ($p = 0.034$) …` | yes | same | kept | rv 38 | OK |
| 57 | 07_discussion: 19 → 19 | `plain sampling \rv{} at $T = 0.8$ (plain sampling at $T = 1$ proved 916 on it)` | yes | same | kept | rv 39 | OK |
| 58 | 07_discussion: 23 → 23 | `predicts \rv{} ($p = 0.006$--$0.020$)` | yes | same | kept | rv 40 | OK |
| 59 | 07_discussion: 28 → 28–29 | `a few theorems out of hundreds,` → `a few theorems (at r0, 4.3 of holdout250's 225 and 4.0 of textbook72's 53 intuitionistic theorems; §\ref{sec:side}),` | adds 4.3, 225, 4.0, 53, as in §3.7 | weaker | n/a | item 10 | OK |
| 60 | 07_discussion: 53 → 53 | `succeed \rv{} on seed 1, then on seed 4: … 0.29, 0.13, 0.085 and 0.046 on seeds 1, 4, 5 and 2. EI first succeeded on seeds 1, 2 and 5.` | yes | same | kept | rv 41 | OK |
| 61 | 07_discussion: 80–81 → 80–83 | `As there, the base rate predicts which seeds move, and no ladder …` → `As there, a zero base rate predicted no movement (seeds 0 and 3) and the highest rate the most (seed 1); unlike there, seed 4, with the second-highest rate, never proved a strict training theorem, while seed 2, with the lowest non-zero rate, did. No ladder …` | seed numbers only | weaker: the counter-example is now stated | n/a | item 9 | **Minor M2** |
| 62 | 07_discussion: 90 → 92 | `2256; \rv{} 1019 already once in two of four plain r16 draws, and twice in the guided one` | yes | same | kept | rv 42 | OK |
| 63 | 07_discussion: 104 → 106 | `bases \rv{} prove no strict theorem in the pre-registered plain evaluation at $k=256$ (one proves one in a second draw)` | yes | same | kept | rv 43 | OK |
| 64 | 08_limitations: 10 → 10 | `after RL: \rv{} the r8 models of the earlier full seeds s0--s2 … 277--303 … (303: the earlier full seed s1, in its x1 evaluation)` | yes | same | kept | rv 44 | OK |
| 65 | 08_limitations: 13 → 13 | `(at most 80 of 106). \rv{} One textbook72 problem (textbook_3ed45280…) has a premise-swapped twin …` | yes | same | kept | rv 45 | OK |
| 66 | 08_limitations: 26 → 26 | `($p = 0.034$). \rv{} The free positive reductio … is also a post hoc measure: … after round 3 … not pre-registered.` | yes | same | kept | rv 46 | OK |
| 67 | 08_limitations: 31–32 → 31–32 | `DN and ¬-introduction three to four times rarer` → `DN 4.2 times and ¬-introduction 2.9 times rarer` | → 4.2 / 2.9 | same | n/a | item 6 | OK |
| 68 | 08_limitations: 32 → 32 | `theorems. \rv{} It costs general ability (§): at r0 … 6.88 points … 679 … 4.0 fewer of textbook72's 53 … 4.3 fewer of holdout250's 225.` | yes | same | kept | rv 47 | OK |
| 69 | 08_limitations: 38 → 38 | `margin. \rv{} That holds at $T = 0.8$ on the pre-registered 106 … (two of six certify on the 105 …); plain sampling at $T = 1$ … seeds 0 and 1, and the pre-registered expectation … missed.` | yes | same | kept | rv 48 | OK |
| 70 | 08_limitations: 43 → 43 | `there; \rv{} in one knockout ladder (seed 1, rounds 1--16), none of the 222,135 rows … (210,151 distinct texts) … $1.4\times10^{-5}$ … (72--88% …) are outside this check.` | yes | same | kept | rv 49 | OK |
| 71 | 08_limitations: 55 → 55 | `use \rv{} the earlier full ladders' (s0--s2) known proofs, not each scored ladder's own,` | yes | same | kept | rv 50 | OK |
| 72 | 08_limitations: 58 → 58 | `allocation. \rv{} $K$ also rests on one timing read per base … co-tenancy was not recorded … seed 0's certificate, with its 8% margin, depends on it.` | yes | same | kept | rv 51 | OK |
| 73 | 08_limitations: 63–64 → 63–64 | `Doubling the caps moved each strict count by at most one theorem (App.), \rv{} but cut the cut-off share only 1.0--2.2-fold on nine of ten checkpoints` → `With doubled caps, each strict count differed by at most one theorem (App.), but the cut-off share fell only 1.0--2.2-fold on nine of ten checkpoints` | 1.0, 2.2, nine of ten, 1,024, ±1 all kept | weaker: causal "moved" gone, in line with the span's own "independent draws, … not cap effects" | kept: the rest of the span is unchanged | rv 52 + §1 smoothing | OK |
| 74 | 08_limitations: 66–67 → 66–68 | `The power-sampling comparators kept no proof text, so their few successes were not re-checked in Lean.` → `The power-sampling comparators of full s0 and s1 and knockout s0 kept no proof text, so their few successes were not re-checked in Lean; the other comparators' stored proofs, including the positive control's, all re-check (App. F).` | seed numbers only | **stronger**: the caveat now covers 3 comparators, not all, and a re-check result is added. Attributable to item 12, and the evidence was spot-checked | kept for the 3 | item 12 | OK, flagged (N1) |
| 75 | 09_repro: 21–22 → 21–22 | `\rv{} Post hoc are A2, A5 and Addendum 5 (A3b, A5b and descriptives …), as are the statistics …` → `A2, A5 and Addendum 5 (A3b, A5b and descriptives …) are post hoc, as are the statistics …` | yes | same | kept: the rest of the span, including "A3's two extensions and A4 were registered as exploratory …", is unchanged | rv 53 + §1 smoothing | OK |
| 76 | 10_appendix: 121 → 121–123 | `They kept no proof text, so their 1--2 successes could not be re-checked in Lean.` → `Those of full s0 and s1 and knockout s0 kept no proof text, so their 1--2 successes could not be re-checked in Lean. The others stored their accepted proofs (knockout s1's one, and the 8 and 15 distinct proofs behind the positive control's 6/17 and 13/17): Lean~4.34.1 accepts all 24 and rejects all 24 with the goal negated (this paper).` | adds 8, 15, 6/17 and 13/17 (as in §3.9, C 336–337), 24, 24 and 4.34.1 | **stronger**: a new re-check result, tagged *this paper*. Attributable to item 12 | n/a | item 12 | OK, flagged (N1) |
| 77 | 11_checks: 5 → 5 | `hide.} \rv{} Same-seed evaluations of ten r16 checkpoints` | yes | same | kept | rv 54 | OK |
| 78 | 11_checks: 7 → 7 | `assumed the \rv{} two draws would be paired, that is, would differ only where a cap binds` | yes | same | kept | rv 55 | OK |
| 79 | 11_checks: 11 → 11 | `which is why \rv{} five of the ten counts differ from Table: knockout s1 shows 3 here against 2, dose … 57, 40 and 28 against 58, 39 and 30, … full s4 shows 22 against 23` | yes | same | kept | rv 56 | OK |
| 80 | 11_checks: 48 → 48–49 | `with no early stopping and new sampling seeds.` → `with no early stopping, new sampling seeds and batch 1,024.` | adds 1,024 | same, more exact | n/a | item 8 | **Minor M3** |
| 81 | 11_checks: 61 → 62 | `rounds 1--16: \rv{} 222,135 rejected rows over 13 reasons, 22,522 …; 210,151 distinct texts, 21,055 …` | yes | same | kept | rv 57 | OK |
| 82 | 11_checks: 65 → 66 | `is \rv{} $1.4\times10^{-5}$ per distinct text … (the pre-registration's $1.3\times10^{-5}$ and $1.3\times10^{-4}$ were computed on rows)` | yes | same | kept | rv 58 | OK |
| 83 | 11_checks: 67 → 68 | `every other \rv{} row (2,132,659 accepted, none rejected)` | yes | same | kept | rv 59 | OK |
| 84 | 11_checks: 70 → 71 | `theorem. \rv{} An independent checker written for this paper's review, sharing no code with the checker above, also accepted none of the 210,151 …` | yes | same | kept | rv 60 | OK |
| 85 | 11_checks: 74–75 → 75–77 | `(figures.py prior, a3_member_prior.py, a4_first_solve.py, a5_waiting_time.py)` → `: figures.py prior, a3_member_prior.py, a3b_member_prior_gained.py, a4_first_solve.py, a5_waiting_time.py and, for A5b, round2_extra.py` | script names only | same | n/a | item 8 | OK: both scripts exist (`round2_extra.py` l.9 and l.69 are labelled A5b) |

## Findings in detail

### Must-fix

None. Three things hold:
- No number changed outside CLEANUP §2 and §3 and main.tex's box and date line.
- No claim got stronger, except item 12's narrowed caveat. That change is listed, backed by evidence and spot-checked here (N1).
- No reviewed caveat was lost.

### Minor

**M1. `00_abstract.tex` l.14–15 (item 4): "acquired classical families under EI" can be read as EI producing the families.**
- Marked: "In this organism EI amplified a composition pretraining had exposed, but within 16 rounds did not acquire the
  classical families without it."
- Clean: "In this organism, bases pretrained with the composition acquired classical families under EI, and within 16
  rounds bases without it acquired none."
- The new sentence is not stronger than the marked one. The causal "amplified" is gone, "In this organism" and "within
  16 rounds" are kept, and the text is the one CLEANUP item 4 gives.
- But the same abstract (l.7–8) says the pre-registered 6/6-vs-0/6 contrast was "largely present before RL".
  `05_results.tex` l.54 says converse contraposition is acquired before RL on 5/6 full bases.
- So "acquired … under EI" can be read as crediting EI with the full bases' families. What happened during EI is
  "5/6 against 0/6 acquired a new family", and that comparison is labelled "not pre-registered".
- Optional fix: "acquired new classical families under EI". This needs one word cut elsewhere to stay at 250, for
  example "In this organism," → "Here,".

**M2. `07_discussion.tex` l.80–83 (item 9): the "zero base rate" for seed 3 holds only on one pool, and the sentence
does not say which.**
- Marked: "As there, the base rate predicts which seeds move, and no ladder …"
- Clean: "As there, a zero base rate predicted no movement (seeds 0 and 3) and the highest rate the most (seed 1);
  unlike there, seed 4, with the second-highest rate, never proved a strict training theorem, while seed 2, with the
  lowest non-zero rate, did."
- The clean claim is weaker, as CLEANUP intends. Its ordering matches the paper's own numbers: discussion l.54–55 gives
  0.29, 0.13, 0.085 and 0.046 for seeds 1, 4, 5 and 2, and the first strict successes came on seeds 1, 2 and 5
  (`05_results.tex` l.195).
- But seed 3's rate is zero only on the waiting-time null's plug-in pool, the 105 family members (`05_results.tex`
  l.193–194). On the pre-registered 106, seed 3's base proved `la_transfer_916`:
  - Table `tab:fambase` lists it as "0, 1, 0, 1, 0, 0" by seed;
  - `05_results.tex` l.144–145 says "seed 3 is also certified; the difference is its success on la_transfer_916";
  - the paper says five of six knockout bases proved strict theorems at large k.
- Suggested fix: "a zero base rate on the 105 family members".
- A secondary point, already in the marked copy: "there" fits the earlier *required* pools, where zero-rate bases
  stayed at 0 of 606. It does not fit the *mixed* pools in the bullet just above (l.75–76), where EI ignited a habit
  from zero on three of five bases.

**M3. `11_checks.tex` l.46–50 (item 8): batch 1,024 is stated for seed 1's C4 draw only.**
- Clean: "Knockout seed 1's base drew 18,432 attempts … with no early stopping, new sampling seeds and batch 1,024.
  Knockout seed 3's base drew 18,432 on `916`."
- The appendix opens with "batch 512 … unless stated" (l.2–3). Read by that rule, seed 3's draw ran at batch 512.
- In fact it ran at batch 1,024 (`artifacts/coe_paper/c4/ko_s3.json.args.json`: batch 1024, n 18432, T 0.8).
- Suggested fix: state the batch once for both draws.

### Notes (no action needed)

**N1. Item 12 (`08_limitations.tex` l.66–68; `10_appendix.tex` l.121–123).**
- This is the only place where a caveat's scope shrinks. The marked copy said that all comparators kept no proof
  text. The clean copy limits that to full s0, full s1 and knockout s0, and adds a positive re-check.
- It is attributable to item 12, and I spot-checked it:
  - in `artifacts/coe/power/`, an `accepted` field exists only in `p2_ko_s1_plain*.json` and `p2b_pc_plain*.json`;
  - `power_comparator_recheck.json` has 1 + 8 + 15 = 24 proofs, 24 accepted and 24 rejected with the goal negated.
    This matches App. F, which is tagged *this paper*.
- App. F's "their 1--2 successes" now refers to the three named comparators. Their solves per run are 1 and 1 (full
  s0), 1 and 2 (full s1), and 0 and 1 (knockout s0). The range was already loose in the marked copy, where it covered
  all comparators, and §3.9 says "0–2". Nothing new is wrong.

**N2. Item 5 (`05_results.tex` l.345).**
- The 150-text control is now described as texts that the pre-filter rejected and that Lean also rejected.
- This fits the next sentence ("Every Lean-gate rejection in the experiment was the pre-filter's") and fits C5. The
  count is unchanged.
- It makes the control read as a small pre-filter check rather than a Lean consistency check. CLEANUP's evidence
  covers this (`artifacts/paper_clean/gate_rejections.{py,json}`, gate logs).

**N3. Item 7 checked against `review_coep/members.log`.**
- Knockout s5 at r16: x0 {1246: 2, 2256: 1}, x1 {1246: 2}, C1 std {1246: 1, 2256: 2}, C1 dbl {1246: 2, 2256: 1}. So
  `1246` appears in 4 of 4 draws, `2256` in 3 of 4, and neither `1811` nor `1142` in any.
- Knockout s2 at r16: x0 {1963}, x1 {1096 ×2}, C1 std {1096}, C1 dbl {1096, 1963}. So `1096` appears in the other
  three draws, and one of them also found `1963`.
- Base s5: `1142` 1 / 3,072 and `1811` 1 / 13,312.
- All of this agrees with Table `tab:fambase` (Peirce sequent: 1 success, at seed 5) and with the abstract's "four on
  family members, mostly one family".

**N4. Unchanged text stays consistent with item 3.**
- Discussion l.91–92 says three members "its base did not reach in 18,432 attempts each". That is still true, because
  "reach" is the technical term for at least two successes.
- The single early-stopped successes are given in `05_results.tex` l.255–256 and now in intro l.74–75.

**N5. textbook72 (`03_setup.tex` l.42).**
- The verbal description is correct for ¬(A→B) ⊢ A ∧ ¬B. It no longer shows that the conclusion is a single
  conjunction, which is the intended trade-off.
- No other `.tex` file prints the schema. I searched for ¬(A→B) and for ∧¬ / `\land \neg` patterns.

**N6. Style.**
- Intro l.74–75 repeats "each": "… 18,432 fresh attempts each, though two of those three had one success each …".

## CLEANUP.md's claims, checked

- **§1. The marks.**
  - 60 marks were removed: abstract 5, intro 9, related 1, setup 1, measurement 4, results 17, discussion 6,
    limitations 9, repro 1, checks 7. All counts confirmed, with 0 `\rv` left.
  - "Each mark sat at the start of a corrected span, so removing it left the correction's text unchanged": true for
    57 spans. The 3 smoothed sentences are exactly the three in §1's table, and their meaning is kept.
    - The limitations sentence's "moved" → "differed" also removes a causal reading, which is a weakening.
    - The Holm attribution ("the experiment's review") matches the review's P10 row.
  - main.tex: confirmed.
- **§2, item by item (paper only).** Each change says what CLEANUP says. The checks were:
  - item 1: matches Table 1;
  - item 2: matches Table 1's "strict member" row;
  - item 3: matches §3.5 and C4;
  - item 4: abstract still 250 words;
  - item 5: as in N2;
  - item 6: 2.9 and 4.2 match §3 Data's percentages and are mapped to the right rules everywhere, including Fig. 0's
    label in `scripts/figures.py`. "A quarter to a third" (§5) is consistent with them;
  - item 7: as in N3;
  - item 8: as in M3; both scripts exist;
  - item 9: as in M2;
  - item 10: matches §3.7;
  - item 11: as listed;
  - item 12: as in N1.
  Item 13 touches only the blog and figures; there is no `.tex` change.
- **§3. textbook72.** The text is as stated. The removed schema is printed nowhere else in the `.tex`.
