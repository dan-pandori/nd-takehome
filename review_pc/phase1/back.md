# Phase-1 sub-audit: PAPER BACK (equivalence, marked -> clean)

- **Part:** paper back matter.
- **Files** (MARKED `review_pc/marked/` vs CLEAN `paper/`, PRE-REVIEW `review_pc/prereview/` used to read what each mark corrected):
  - `sections/07_discussion.tex` (PDF section 6): 6 `\rv{}` marks, 6 diff hunks.
  - `sections/08_limitations.tex` (section 7): 9 marks, 3 hunks.
  - `sections/09_repro.tex` (section 8): 1 mark, 1 hunk.
  - `sections/10_appendix.tex`: 0 marks, 1 hunk (+45 words).
  - `refs.bib`: byte-identical.
- **Note on `\rv`:** in the marked preamble `\rv` takes no argument; it prints "[review]" *before* the corrected passage. So a fold means deleting `\rv{}` and keeping the text that follows.
- **Counts:** 27 rows: EQUIV 18, FIX? 7, MUST-FIX 0, MINOR 0, NOTE 2.
- **Marks:** all 16 marks are folded verbatim, apart from one reworded lead-in clause in §7 Settings, which is weaker.

| # | clean loc (file:line) | marked (quote) | clean (quote) | numbers | strength | caveat | verdict |
|---|---|---|---|---|---|---|---|
| D1 | 07:8-10 | P10 mark: "\rv{} These per-family verdicts rest on the pre-registered Holm correction; uncorrected, three of the undetermined families ($p = 0.034$) would meet NEEDS EXPOSURE" | identical without `\rv{}` | same | same | kept | EQUIV |
| D2 | 07:18-20 | P2 mark: "only for plain sampling \rv{} at $T = 0.8$ (plain sampling at $T = 1$ proved la_transfer_916 on it), at one budget and with an 8% margin" | identical | same | same | kept | EQUIV |
| D3 | 07:23 | A5b precision mark: "sooner than this null predicts \rv{} ($p = 0.006$--$0.020$)" | identical | same (0.020) | same | kept | EQUIV |
| D4 | 07:28-29 | "The general costs are a few theorems out of hundreds" (unmarked; task-2 item in the README notes l.123) | "The general costs are a few theorems (at r0, 4.3 of holdout250's 225 and 4.0 of textbook72's 53 intuitionistic theorems; §\ref{sec:side})" | added: 4.3/225, 4.0/53 at r0 | weaker: explicit denominators replace "out of hundreds", which belittled it | n/a | FIX? (supported) |
| D5 | 07:53-55 | P11 mark: "first succeed \rv{} on seed 1, then on seed 4: ... 0.29, 0.13, 0.085 and 0.046 on seeds 1, 4, 5 and 2. EI first succeeded on seeds 1, 2 and 5" | identical | same | same | kept | EQUIV |
| D6a | 07:80-81 | "As there, the base rate predicts which seeds move" (unmarked; task-2, README l.121-122) | "As in the required pools, a zero base rate (on the 105 family members) predicted no movement (seeds 0 and 3) and the highest rate the most (seed 1)" | added: 105, seed IDs | weaker (only the zero vs non-zero split and the top seed are now claimed) | n/a | FIX? (supported) |
| D6b | 07:81-83 | (same marked sentence) | "unlike there, seed 4, with the second-highest rate, never proved a strict training theorem, while seed 2, with the lowest non-zero rate, did. No ladder ... acquired a family." | added: seeds 4 and 2 | weaker (admits the ordering failed) | the "No ladder ... near $10^{-6}$" clause kept verbatim | FIX? (supported) |
| D7 | 07:92 | P6 mark: "\rv{} 1019 already once in two of four plain r16 draws, and twice in the guided one" | identical | same | same | kept | EQUIV |
| D8 | 07:106-107 | P4 mark: "Our knockout bases \rv{} prove no strict theorem in the pre-registered plain evaluation at $k=256$ (one proves one in a second draw)" | identical | same | same | kept | EQUIV |
| L1 | 08:10-11 | smaller-item mark: "\rv{} the r8 models of the earlier full seeds s0--s2 prove 236--240 ... r16 models 277--303 of the 322 (303: the earlier full seed s1, in its x1 evaluation)" | identical | same | same | kept | EQUIV |
| L2 | 08:13-16 | P17 mark: "\rv{} One textbook72 problem (textbook_3ed45280...) has a premise-swapped twin in every pretraining set ... (no order-sensitive one) ... none shares a class with the strict theorems" | identical (named by ID only) | same | same | kept | EQUIV |
| L3 | 08:26-27 | P17 mark: "\rv{} The free positive reductio ..., used for the ladder dynamics, is also a post hoc measure: defined after round 3 ..., not pre-registered" | identical | same | same | kept | EQUIV |
| L4 | 08:31-32 | "It makes DN and ¬-introduction three to four times rarer" (unmarked; task-2, README l.117) | "It makes DN 4.2 times and ¬-introduction 2.9 times rarer" | changed: 3-4 -> 4.2 / 2.9 | same (more precise; the old range excluded both values) | n/a | FIX? (supported) |
| L5 | 08:32-35 | P17 mark: "\rv{} It costs general ability: at r0 ... 6.88 points worse at greedy decoding of 5,000 ..., all of it on the 679 ... with 256 attempts ... 4.0 fewer of textbook72's 53 ... 4.3 fewer of holdout250's 225" | identical | same | same | kept | EQUIV |
| L6 | 08:38-41 | P2 mark: "\rv{} That holds at $T = 0.8$ on the pre-registered 106 ... (two of six certify on the 105 ...); plain sampling at $T = 1$ proved 916 on the bases of seeds 0 and 1, and the ... expectation ... missed" | identical | same | same | kept | EQUIV |
| L7 | 08:43-46 | P9 + precision mark: "\rv{} ... none of the 222,135 rows ... (210,151 distinct texts) is Lean-accepted ... $1.4\times10^{-5}$ per distinct text ($1.4\times10^{-4}$ ...) ... 72--88% ... outside this check" | identical | same | same | kept | EQUIV |
| L8 | 08:55 | P7 mark: "use \rv{} the earlier full ladders' (s0--s2) known proofs, not each scored ladder's own" | identical | same | same | kept | EQUIV |
| L9 | 08:58-60 | P17 mark: "\rv{} $K$ also rests on one timing read per base of its cost per attempt ... co-tenancy was not recorded ... seed 0's certificate, with its 8% margin, depends on it" | identical | same | same | kept | EQUIV |
| L10 | 08:63 | "Doubling the caps moved each strict count by at most one theorem (Appendix)" (pre-review text, just before the mark) | "With doubled caps, each strict count differed by at most one theorem (Appendix)" | same | weaker (drops the causal "moved", consistent with P1) | kept | EQUIV |
| L11 | 08:63-66 | P17/P1 mark: "\rv{} but cut the cut-off share only 1.0--2.2-fold on nine of ten checkpoints: ... runaway generations ... independent draws, not a paired comparison ... sampling, not cap effects" | "but the cut-off share fell only 1.0--2.2-fold on nine of ten checkpoints: ..." (rest identical) | same | same | kept | EQUIV |
| L12 | 08:66-68 | "The power-sampling comparators kept no proof text, so their few successes were not re-checked in Lean." | "The power-sampling comparators of full s0 and s1 and knockout s0 kept no proof text, ...; the other comparators' stored proofs, including the positive control's, all re-check (Appendix~\ref{app:power})." | added claim (re-check) | caveat narrowed to the 3 comparators it is true of | kept for those 3 | FIX? (supported; see F5) |
| R1 | 09:21-25 | mark: "\rv{} Post hoc are A2, A5 and Addendum 5 (A3b, A5b and descriptives ...), as are the statistics marked *this paper* that no pre-registration lists (...)" | "A2, A5 and Addendum 5 (A3b, A5b and descriptives ...) are post hoc, as are the statistics marked *this paper* ..." | same | same (word order only) | kept (full list, A3/A4 exploratory sentence kept) | EQUIV |
| A1 | 10:121 | "They kept no proof text, so their 1--2 successes could not be re-checked in Lean." | "Those of full s0 and s1 and knockout s0 kept no proof text, so their 1--2 successes could not be re-checked in Lean." | same | scope narrowed (true for the 3 named) | kept for those 3 | FIX? (supported) |
| A2 | 10:122-123 | (nothing) | "The others stored their accepted proofs (knockout s1's one, and the 8 and 15 distinct proofs behind the positive control's 6/17 and 13/17): Lean 4.34.1 accepts all 24 and rejects all 24 with the goal negated (*this paper*)." | added: 1, 8, 15, 24 | new claim (new check) | n/a | FIX? (supported; re-run by me, see F5) |
| A3 | 10_appendix.tex (whole) | Lean listings (a) and (b), family table, expectations list | unchanged. The diff has one hunk, this paragraph only; no printed proof or theorem changed; the negated-conditional family is named, its schema is not printed | same | same | kept | NOTE |
| B1 | refs.bib | marked = librarian's version (singh2023restem given arXiv:2312.06585; havrilla2024teaching / zelikman2022star still without identifier) | byte-identical to marked; every key cited in 07-10 resolves | same | same | kept | EQUIV |
| N1 | 07 (whole) | P16 (unlabelled TTC models, PUCT half of "neither method ...") | no P16 mark and no PUCT / "neither method" sentence in 07-10, marked or clean. P16 lives in §3/§4 and Fig. 7 (another sub-auditor's part) | n/a | n/a | n/a | NOTE |

## Findings

**MUST-FIX:** none. Every mark in 07, 08 and 09 survives with its numbers and qualifiers. The qualifiers checked: T 0.8, the pre-registered 106, two of six on the 105, rows vs distinct texts, 1.4e-5 per distinct text, 72-88 %, earlier full s0-s2, the 303 of 322, 1.0-2.2-fold on nine of ten, independent draws, one c_base read per base, post hoc, the ID-only twin and "(one proves one in a second draw)". No claim got stronger.

**FIX? items** (F1-F3 and F5 are task-2 changes, each supported by the authorities or the data; F4 is an EQUIV rewording, listed here for completeness):

1. **F1. Discussion, reading 4 (07:28-29).** Clean text: "The general costs are a few theorems (at r0, 4.3 of holdout250's 225 and 4.0 of textbook72's 53 intuitionistic theorems; §\ref{sec:side})". The marked text was "a few theorems out of hundreds".
   - The numbers match LEDGER_pre_run P57 ("pass@256 at pend: holdout250 non-classical −4.3 of 225; textbook72 −4.0 of 53"), the clean §3.5 and the §7 P17 limitation.
   - Strength: weaker than the marked text, never stronger.
   - What it leaves out, all of which §3.5 and §7 keep: "with 256 attempts", "three full seeds against six knockout seeds", the r16 residual of −2.5 of 53, and the greedy −6.88 pp. The −6.88 pp falls entirely on the 679 σ-reference theorems, so leaving it out of a sentence about *general* costs is defensible.
2. **F2. Discussion, earlier-organisms comparison (07:80-83).** This replaces the claim "the base rate predicts which seeds move". It checks against the review's §Recount A5 and the paper's Table 1:
   - P(success by r16) on the 105 family members is 0, .286, .046, 0, .130, .085 for s0-s5. The observed first strict training successes were s1 at r9, s2 at r14 and s5 at r14.
   - Seeds 0 and 3 have a zero rate and show no movement. Seed 4 has the second-highest rate and never succeeded. Seed 2 has the lowest non-zero rate and did.
   - "The highest rate the most (seed 1)" holds on the earliest first success, x1 (2 vs 1), guided (3 vs 2) and r20 (5). It ties seed 5 on r16 x0 (2 vs 2).
   - The text is weaker than the marked one and the sentence is grammatical. "Unlike there" is followed by "Unlike the required pools" in the next sentence; that is stylistic only.
3. **F3. Limitations, the knockout is not surgical (08:31-32).** "three to four times rarer" became "DN 4.2 times and ¬-introduction 2.9 times rarer". The arithmetic holds: 13.73/3.29 = 4.17 and 15.21/5.19 = 2.93, from LEDGER P55 (reviewed). The old range excluded both values. The clean §3.5 matches.
4. **F4. Limitations, Settings lead-in (08:63).** "Doubling the caps moved each strict count" became "With doubled caps, each strict count differed". I rate this EQUIV, not a fix: it removes a causal reading that the P1 mark next to it contradicts. The numbers are unchanged.
5. **F5. Power-sampling comparators (08:66-68; 10:121-123).** This is the one change in my part that **goes against the librarian's task-2 note**. README l.125 says the positive control's comparator solves (6/17, 13/17) "also kept no proof text". The data says the note is wrong and the clean text is right:
   - **Which runs stored proofs.** In `artifacts/coe/power/`, the rows of `p2_ko_s1_plainT{0.8,1.0}.json` and `p2b_pc_plainT{0.8,1.0}.json` carry an `accepted` {proof text: count} field. The rows of `p2_full_s0_*`, `p2_full_s1_*` and `p2_ko_s0_*` do not.
   - **Their 1-2 successes.** Full s0: 1 and 1. Full s1: 1 and 2. Knockout s0: 0 and 1 (`la_transfer_916` at T 1.0).
   - **The distinct stored proofs:**
     - knockout s1 (T 1.0): 1 (`la_transfer_916`);
     - positive control, T 0.8: 8 (8 successes on 6 theorems);
     - positive control, T 1.0: 15 (16 successes on 13 theorems);
     - total 24, as printed.
   - **My own Lean re-run.** I used the earlier reviewer's own harness (`review_coep/lean4.py`, independent of nd2lean) with Lean 4.34.1 via `--stdin`; no files were written. It accepts 24/24 and accepts 0/24 with the goal negated, which confirms "accepts all 24 and rejects all 24".
   - **The limitation is narrowed, not dropped.** It still holds, in full, for the three comparators named.
   - **Listing (b) is not a contradiction.** Appendix listing (b), knockout s0's T 1 proof of 916, comes from a separate 131,072-attempt T 1.0 sample (`artifacts/coe/examples/knockout_first_sigma.md` item 1), not from the comparator.
   - **NOTE.** The development-pilot comparators (`pilot_plainT*_pend_s0.json`, 31/32) also kept no proof text and are not named. The paper reports none of their solves, so no printed claim depends on them.
   - **For the reviewer.** This adds a new "this paper" check and number (24). §8's sentence on *this paper* statistics covers it as post hoc.

**Appendix (10_appendix):** the only change is F5's paragraph. It is not a listing or caption fix. No printed proof, theorem or family schema changed, and none of the negated-conditional family's formulas appears in 10.

**Unchecked:** nothing in my part. The LaTeX build and cross-references are the reviewer's job. The labels `sec:side` and `app:power` exist.
