# Literature audit of run `capability-defs` against pre-registered L1 (and L2)

Sub-auditor, 2026-10-05. Inputs read: `capability_defs/lit/` (all files), the two earlier reviews
(`~/nd-rl/docs/literature/2026-09-29-lit-review/`, `2026-10-02-lit-review-2/`), `~/cd_sources/` (no downloads).
Not read: REPORT.md, cards/, numbers.md, run_capability_defs.md, log.md, STATUS*.md. Every number below is printed
by a script in this folder (output files named in each section).

## Summary

screened.md has 191 rows, **185 unique papers** (the same 6 cross-reader duplicates the file marks). Matching
every file of both earlier reviews by arXiv id (± version), DOI, URL and normalised or fuzzy title finds **0
overlaps** (positive control: 109/109 earlier papers detected), so "185 unique papers new to the earlier reviews"
holds. Caveats: 22 are non-arXiv items, and row 105 was never read. **57 in-depth notes**; each matches a
screened row read at sections (41) or full (16) depth; **0 abstract-only**; none is about an earlier-review paper.
Ledgers: 1,183 rows, V share L1 100 %, L2 99.52 %, L3 100 %, L4 99.46 %, L5 100 %, L6 99.48 %, **overall 99.75 %**.
The executor's re-check has **n = 32 and 0 errors**, and it can be reproduced 32/32. My re-verification of **48** V claims
(8 per reader) found **48 verbatim** (8 differ only by math markup), **0** paraphrase, **0 not found**, **0** source
missing and **0 location problems**. An automated scan of all 1,180 V rows found every quoted fragment, with one
inflection change. **12/12** sampled REVIEW.md sentences trace to V ledger rows; 2 of them are imprecise. The
L1 literature criteria are met.

## 1. Screened, new, in depth (`s1_screened.py`, `s1b_controls.py`, `s1c_notes.py`, `s2_claims.py`)

| quantity | count | note |
|---|---|---|
| numbered rows in screened.md | 191 | L1 32, L2 30, L3 36, L4 35, L5 29, L6 29; 1:1 with the six `_screen_L*.md` tables |
| duplicate rows across readers | 6 | rows 33, 82, 100, 134, 163, 164; my union-find (arXiv id, DOI, URL, normalised title) finds exactly these |
| **unique papers** | **185** | 163 with an arXiv id, 22 without (blogs: Epoch, METR, Thinking Machines, Transformer Circuits; 2 SEP entries; Anthropic RSP; Baker textbook; JSS papers; Rasch memos; Nature papers) |
| overlaps with the two earlier reviews | **0** | 40 files scanned (107 distinct arXiv ids, 2 DOIs); title substring over all files, pre-colon title, fuzzy title ≥ 0.8 vs 189 table cells |
| positive control (earlier papers fed through the same matcher) | 109 / 109 detected | 108 by id/DOI, 98 by title |
| author + year co-occurrence scan (looser) | 20 hits, all different papers | e.g. "Qin 2025" = 2505.22756 vs Chen, Qin et al. 2508.10751 |
| **unique new papers** | **185** | matches the file's claim |
| best depth per unique paper | sections 91, full 21, abstract 72, none 1 | row 78 counted as abstract (its cells are shifted, see D1); "none" = row 105 |
| in-depth notes | **57** | all named in a screened title cell; all have the template front matter, 3 section headings and 4 required bullets; 715–1,365 words (median 1,008) |
| notes whose matched rows say sections / full / abstract-only | 41 / 16 / **0** | 4 notes' papers were also screened at abstract level by another reader (dup rows 31/33, 32/100, 89/134, 93/163); the in-depth row is the dup |
| notes about an earlier-review paper | **0** | mousavihosseini2026barrier.md names 2510.15020 and 2503.07453 only as context |
| other note checks | — | each arXiv-based note's main source is a full text in `~/cd_sources`; each of the 54 notes with an arXiv id has ≥ 5 ledger claims located outside the abstract; 3 notes cover two papers (rows 42+43, 104+105, 169+170), so the notes cover 60 unique papers, 59 of them read |

`_prior_screened.tsv` (109 rows) contains every arXiv id in the earlier reviews' screened tables. The one arXiv id
that appears in the earlier reviews but not in the TSV, 2512.17351 (LR2 `claims.md` line 133, "seen in search
only"), is not among the 185.

## 2. Claim ledgers (`s2_claims.py`)

| reader | rows | V | UNVERIFIED | other | V share |
|---|---|---|---|---|---|
| L1 | 205 | 205 | 0 | 0 | 100 % |
| L2 | 209 | 208 | 1 | 0 | 99.52 % |
| L3 | 228 | 228 | 0 | 0 | 100 % |
| L4 | 184 | 183 | 1 | 0 | 99.46 % |
| L5 | 165 | 165 | 0 | 0 | 100 % |
| L6 | 192 | 191 | 1 | 0 | 99.48 % |
| **all** | **1,183** | **1,180** | **3** | 0 | **99.75 %** |

The V count includes two qualified rows: "V (as quoted by the paper)" (L2 #27) and "V (secondary)" (L6 #175, Wired).
Row numbering has no gaps or duplicates. There are 209 distinct paper-id strings in the ledgers (`s2b_sources.py`).
136 resolve to a full text in `~/cd_sources` and 70 to an abstract only. 3 have no file, and these are exactly the 3
UNVERIFIED rows. No V row with a non-abstract location relies only on an abstract file (`s4b_population.txt`).

## 3. Executor's re-check (`s2_claims.py`, `s3_recheck_reproduce.py`)

`_executor_recheck.md` has **32 rows** (L1 7, L2–L6 5 each). Status: 32 V, **0 errors**. Every row traces to a
ledger row. The sample is reproducible: `shuf -n K --random-source=<(yes S)` with K = 7, S = 42 for L1 and K = 5, S = 7
for L2–L6 redraws the same 32 rows in the same order, **but only if the input is first filtered to rows whose status is exactly
"V"**. The file does not state this filter. Without it, 24/32 match. See D5.

## 4. My re-verification (`s4_reverify.py`, `s4_controls.py`, `s4_verdicts_build.py`, `s4_tally.py`)

**Method.**
- Sample: `random.Random(20261005).sample(V rows of each reader sorted by #, 8)` for L1…L6 in order, 48 claims in all.
- Matcher: my own, independent of the run's `quote.py`. It normalises NFKC, unicode quotes and dashes, LaTeX markup,
  line-break hyphenation, case and whitespace, then tries an alphanumeric-only match, then a fuzzy token window.
- Controls: a verbatim quote and LaTeX `10\,000` both match. A one-word change, a changed number and a fabricated
  sentence never match exactly (fuzzy 0.94, 0.93 and 0.36; `s4_controls.txt`), so every fuzzy hit was inspected by
  hand.
- Every unquoted number or formula was searched in the raw text, and every location was compared with the nearest
  section heading, page marker or caption (`ctx.py`, `near.py`).

**Result (48 claims).**

| finding | count |
|---|---|
| found verbatim | **48** (40 exact or punctuation-only, 8 differing only by math markup such as τ vs `\tau`) |
| found with paraphrase-level differences | **0** |
| not found | **0** |
| source missing | **0** |
| stated location wrong | **0** (48 / 48 plausible) |

**Supplementary population checks** (automated; `s4b_population_scan.py`, `s4c_fuzzy_diffs.py`,
`s4e_wording_resolutions.py`, `s4d_location_scan.py`):
- *Quotes.* Of the 1,180 V rows, 1,032 match exactly and 56 match after dropping punctuation and markup. 54 more
  reach fuzzy ≥ 0.85, 5 score 0.60–0.85, 8 score below 0.60 or are not found, and 25 have no quoted fragment.
  I inspected all 32 low-scoring or wording-flagged rows by hand. Exactly one is a real wording change, an
  inflection: L1 #149, "stumble in the dark" against the source's "stumbles". The others are markup (24),
  fragments too short for the fuzzy matcher (6), window edges (4), PDF artefacts (4), nested quotes (2) and one
  editorial `[s]`.
- *Locations.* Of the 1,180 V rows, 1,012 are consistent with the stated Sec./App./Abstract automatically. Another
  40 were checked by hand: 33 heuristic flags caused by web "(4.3)" headings, TeX `\section` and split PDF headings,
  plus 7 rows the heuristic could not locate. That gives **1,052 consistent and 0 inconsistent**. The remaining 128
  were not checkable by the heuristic (figure, table or page locations, or no quote).

<!-- TABLE4 -->

## 5. REVIEW.md spot-check (`s5_review_sample.py`, `s5_verdicts_build.py`)

Population: 72 sentences that cite a paper, in Bottom line and §§1–6 (`s5_candidates.txt`). Sample:
`random.Random(20261005).sample(range(72), 12)`. **Traced 10, traced but imprecise 2, not traced 0.**

<!-- TABLE5 -->

## 6. L2 (summary, ≤ 150 words)

REVIEW.md (Bottom line 1) concludes **L2 held**: no definition of "new capability" is free of k or budget. Each
needs a budget (k, compute, fine-tuning data, "1 % of training cost"), a reference model, a population (IRT, a game
database) or a difficulty scale. The principled budgets are compute-tied: the RSP's "< 1 % of training cost",
Davidson's compute-equivalent gain, Mousavi-Hosseini & Erdogdu's query barrier. The nearest exceptions, Deeb &
Roger's controls and Korbak's conditioning, still need a reference model. Its strongest citations are V rows whose
quotes my scan found:
- RSP L2 #167/#169 (pp. 6–7, page markers checked); van der Weij L2 #27; Hofstätter L2 #40.
- Davidson L1 #75/#76/#82; Mousavi-Hosseini & Erdogdu L5 #105–#115.
- Deeb & Roger L2 #58/#61/#62; Korbak L5 #4.

Caveats: population and difficulty scale go beyond L2's wording; REVIEW.md §2 itself calls the 1 % rule unjustified
in the texts read.

## 7. Supplementary: quotes in notes and REVIEW.md (`s6_quotes_notes_review.py`, `s6b_note_misses.py`, `s6c_classify.py`)

**Notes.** The notes hold 1,021 double-quoted fragments of ≥ 4 words.
- 892 are found exactly in a fetched source.
- 49 more reach fuzzy ≥ 0.85 against the note's own source.
- Of the remaining 80:
  - 48 are the readers' own scare-quoted phrases ("any k solves it", "more of the same").
  - 20 are text between two quotations, mis-paired because a note has unbalanced quote marks.
  - 9 differ by markup and 1 is a PDF artefact.
  - 2 are paper wording altered inside quotation marks (D10).

**REVIEW.md.** It holds 35 such fragments.
- 26 are found exactly.
- Of the other 9, 6 are own phrases, 2 differ by markup and 1 is a near-quote (D9).

## Discrepancies (file, row / line)

- **D1** `screened.md` line 84 (row 78, 2109.09234v1): the escaped pipe in "I_V(R → Y \| B)" became `\ |`. That
  splits the definition cell, so depth reads "3" and the claims cell "4 / 4" is lost. `_screen_L3.md` line 28 is
  correct.
- **D2** `screened.md` line 82 (row 76, 2005.10283v2) states claims "6 / 6", but `_claims_L3.md` has 5 rows for this
  paper (#148–152).
- **D3** `screened.md` line 111 (row 105, AIJ 2019 Martínez-Plumed): depth is "none" (publisher 403) and claims are
  0/1. It is the journal version of row 104 and was not read at all. It is still counted in the 185; without it the
  count is 184.
- **D4** Two of the three UNVERIFIED ledger rows are placeholders, not claims: `_claims_L2.md` line 161 (#153,
  "no claim taken from the book") and `_claims_L4.md` line 89 (#80).
- **D5** The `_executor_recheck.md` method line gives `yes 42` for all readers, while the result line gives
  `yes 7`. The undocumented status-V filter is needed to reproduce the sample. With a constant random source, shuf
  takes the same positions (5, 26, 48, 53, 128) in each of L2–L6.
- **D6** `_claims_L1.md` line 157 (#149, 2207.08799v3 abstract) quotes "stumble in the dark". The source says
  "stumbles". This is the only wording change among the 1,180 V rows.
- **D7** REVIEW.md line 131 (R35) prints "mere possibility" as a quotation, but the phrase is not in SEP
  "Abilities". The verified sentence ("this sort of possibility is a sufficient condition", L2 #100) is in Sec. 4.1,
  not 4.3.
- **D8** REVIEW.md lines 217–218 (R70) say crosscoder "model-only" features are mostly artefacts. Minder et al.'s
  finding is for L1-loss crosscoders. The cited ledger row L6 #134 (`_claims_L6.md` line 143) also says "most
  BatchTopK chat-only latents are genuinely chat-specific", and REVIEW.md leaves this out.
- **D9** REVIEW.md line 150 prints "examples needed to reach a stated loss" (Whitney et al.) as a quotation. The
  source says "the number of samples required to reach that loss tolerance" (2009.07368 line 97).
- **D10** Two notes alter paper wording inside quotation marks:
  - `vanderweij2024sandbagging.md` has "Best currently available elicitation"; the source says "best currently
    available capability elicitation techniques".
  - `voita2020mdlprobing.md` has "how much a representation encodes property Y"; the source says "how well
    pretrained representations encode some linguistic property".
- **D11** Minor items:
  - REVIEW.md lines 49–50 attach "(Sec. 3.2)" to Deeb & Roger's "a reliable baseline for comparison", which is in
    Sec. 2 (source line 194; L2 #62 has it right).
  - `_claims_L4.md` lines 77 and 152 contain unescaped `|` inside claims, so the table gets an extra column.

## Files

Scripts: `common.py`, `s1_screened.py`, `s1b_controls.py`, `s1c_notes.py`, `s2_claims.py`, `s3_recheck_reproduce.py`,
`s4_reverify.py`, `s4_controls.py`, `s4b_population_scan.py`, `s4c_fuzzy_diffs.py`, `s4d_location_scan.py`,
`s4_verdicts_build.py`, `s4e_wording_resolutions.py`, `s4_tally.py`, `s5_review_sample.py`, `s5_verdicts_build.py`,
`s6_quotes_notes_review.py`, `s6b_note_misses.py`, `s6c_classify.py`, `s7_render.py`, `s8_assemble.py`; helpers
`ctx.py`, `near.py`, `lg.py`. Outputs: `s1_summary.txt`, `s1b_controls.txt`, `s1c_notes.txt/.tsv`,
`s1_screened_rows.tsv`, `s2_claims.txt/.json`, `s3_recheck_reproduce.txt`, `s4_sample.json`, `s4_evidence.txt`,
`s4_verdicts.tsv`, `s4_tally.txt`, `s4b_population.txt/.tsv`, `s4c_fuzzy_diffs.txt`, `s4d_location.txt`,
`s4d_resolutions.tsv`, `s4e_resolutions.tsv`, `s4e_tally.txt`, `s5_candidates.txt`, `s5_sample.txt`,
`s5_verdicts.tsv`, `s5_tally.txt`, `s6_quotes.txt`, `s6b_note_misses.txt`, `s6c_classes.txt`, `s7_tables.md`.
