# Phase-1 equivalence audit: PAPER FRONT

- **Part:** paper front.
- **Files:** `main.tex`, `sections/00_abstract.tex`, `01_intro.tex`, `02_related.tex`, `03_setup.tex`, `04_measurement.tex`. I compared `review_pc/marked/<f>` (reference) with `paper/<f>` (clean), using `review_pc/prereview/<f>` for context. Fig. 0 (`figures/fig0_overview.{png,pdf}`) is included because the intro uses it and it is the only front figure that changed. `fig7_ttc` is byte-identical.
- **Counts:** 35 rows: 22 EQUIV, 9 FIX?, 0 MUST-FIX, 2 MINOR, 2 NOTE.
- **Marks:** all 20 `\rv` marks in this part are folded verbatim (abstract 5, intro 9, related 1, setup 1, measurement 4). No `\rv` is left in `paper/main.tex` or in any `paper/sections/*.tex` (grep). `main.tex` no longer defines `\rv` and no longer has the reading-copy box.
- **Independence:** I opened none of the forbidden files. One disclosure: my session's start-up context showed a git-status snapshot of the executor's worktree, including its last five commit subjects. I did not use it. I found the Fig. 0 change by running `cmp` on `figures/`.
- **Sealed class:** this report quotes neither the negated-conditional schema nor its verbal replacement.

| # | clean loc (file:line) | marked (quote) | clean (quote) | numbers | strength | caveat | verdict |
|---|---|---|---|---|---|---|---|
| M1 | main.tex:34–35 | `\newcommand{\rv}{...[review]}` (and the librarian comment) | removed | same | same | n/a | EQUIV (required) |
| M2 | main.tex:45 | "\fbox{... Reading copy (librarian, 2026-10-14) ... Each change is marked \rv{}. No headline number changed...}" | removed | same | same | n/a | EQUIV (required) |
| M3 | main.tex:41 | "Draft of 2026-10-13; reading copy with the review's corrections, 2026-10-14. Not for circulation." | "Draft of 2026-10-14. Not for circulation." | n/a | same | kept ("Not for circulation") | NOTE |
| A1 | 00_abstract:5 | "eliminate the double negation) \rv{} and its variants" (P14) | "eliminate the double negation) and its variants" | same | same | kept | EQUIV |
| A2 | 00_abstract:5 | "keep both rules (each 3--4 times rarer)" | "keep both rules (each 2.9--4.2 times rarer)" | changed: 3–4 -> 2.9–4.2 | same (precision) | n/a | FIX? (task 2; supported, F2) |
| A3 | 00_abstract:7 | "(half its \rv{} strict held-out members proved in 256 attempts)" (P5) | "(half its strict held-out members proved in 256 attempts)" | same | same | kept | EQUIV |
| A4 | 00_abstract:11–12 | "with \sig{} \rv{} (four on family members, mostly one family), 1--7 times in 1.1--1.4M attempts" (P13) | same text without `\rv` | same (5/6, 4/6, 1–7, 1.1–1.4M) | same | kept | EQUIV |
| A5 | 00_abstract:13 | "In three earlier \rv{} 8-round full-exposure runs" (P3 label) | "In three earlier 8-round full-exposure runs" | same | same | kept | EQUIV |
| A6 | 00_abstract:13–14 | "at equal sample counts \rv{} and 14--34 at RL's compute as base attempts (14--21 under all five allocations)" (P3) | same text without `\rv` | same (51–60, 14–34, 14–21) | same | kept | EQUIV |
| A7 | 00_abstract:14–15 | "In this organism EI amplified a composition pretraining had exposed, but within 16 rounds did not acquire the classical families without it." | "In this organism, seeds pretrained with the composition acquired classical families, and within 16 rounds of EI, seeds without it acquired none." | same | weaker (drops the "EI amplified" interpretation) | kept ("In this organism", "within 16 rounds") | FIX? (task 2; supported, F3) |
| I1 | 01_intro:24 | "We remove a single inference composition \rv{} and its variants from pretraining" (P14) | same text without `\rv` | same | same | kept | EQUIV |
| I2 | 01_intro:25–26 | "though each becomes three to four times rarer." | "though negation introduction becomes 2.9 times rarer and double-negation elimination 4.2 times." | changed: 3–4 -> 2.9 (¬I), 4.2 (DN) | same (precision) | n/a | FIX? (task 2; supported, F2) |
| I3 | 01_intro:31 | "the classical reductio \sig{}: to prove a positive goal $G$, assume $\neg G$" | "the classical reductio \sig{}: to prove a goal $G$, assume $\neg G$" | same | weaker (broader definition; no claim depends on it) | n/a | FIX? (task 2; supported, F4) |
| I4 | 01_intro:33–34 | "\rv{} Its variants, which apply DN to other derived lines, are removed with it (together \sigp{}, 16,961 of the 155,000 records)." (P14) | same text without `\rv` | same (16,961; 155,000) | same | kept | EQUIV |
| I5 | 01_intro:68–69 | "including \rv{} seed 0, the only base ... certified out of reach under plain sampling at $T=0.8$ on the pre-registered pool of 106 theorems (at $T=1$ ... 916 on it)" (P2) | same text without `\rv` | same | same | kept (T 0.8, pre-registered 106, T 1 success) | EQUIV |
| I6 | 01_intro:72 | "(\rv{} $p = 0.006$--$0.020$ under the null)" (A5b precision) | "($p = 0.006$--$0.020$ under the null)" | same | same | kept | EQUIV |
| I7 | 01_intro:74–75 | "Its base had no success on three of the five in 18,432 fresh attempts each." | "...in 18,432 fresh attempts each, though two of those three had one success each in an earlier, early-stopped sample." | added: 2 of 3, one success each | weaker (adds a caveat) | added | FIX? (task 2; supported, F5) |
| I7b | 01_intro:75 | (the term was first used in §3.4) | "in an earlier, early-stopped sample" | n/a | same | n/a | MINOR: "early-stopped" is now first used in the intro and is defined nowhere in the paper (F9) |
| I8 | 01_intro:76–77 | "In three earlier full-exposure runs \rv{} (seeds s0--s2 of the same prover, after 8 rounds, on 322 evaluation theorems)" (P3) | same text without `\rv` | same | same | kept | EQUIV |
| I9 | 01_intro:77–79 | "\rv{} Between 14 and 34 remain ... depending on how that compute is counted; 14--21 remain under all five budget allocations we tried." (P3) | same text without `\rv` | same | same | kept | EQUIV |
| I10 | 01_intro:87–88 | "\rv{} The certificate expectation, at least five of six knockout bases certified, was missed: one of six on the pre-registered 106 ..., two of six on the 105" (P2) | same text without `\rv` | same (≥5/6; 1/6; 2/6) | same | kept | EQUIV |
| I11 | 01_intro:104–105 | "$N$ the number of training problems that require the composition or a variant (here 123 of 4,495)" | "$N$ the number of training problems that need the composition, a variant or the lemma route of Table~\ref{tab:concepts} (here 123 of 4,495)" | same (123, 4,495) | weaker (more routes allowed) | n/a | FIX? (task 2; supported, F6) |
| I12 | 01_intro:107 | "\rv{} \textbf{Cued practice did not yield a family within 16 rounds.}" (P15) | same text without `\rv` | same | same | kept ("within 16 rounds") | EQUIV |
| I13 | 01_intro:114–116 | "Our knockout bases \rv{} prove none of the 106 held-out strict theorems at $k=256$ under plain sampling in the pre-registered evaluation (one proves one in a second draw)" (P4) | same text without `\rv` | same | same | kept | EQUIV |
| I14 | Fig. 0 panel (a) footnote (`fig0_overview.png/.pdf`; intro l.42) | "(DN and ¬-introduction stay; 3–4× rarer in the knockout)" | "(DN and ¬-introduction stay; 4.2× and 2.9× rarer in the knockout)" | changed: 3–4× -> 4.2× (DN), 2.9× (¬I) | same (precision) | n/a | FIX? (supported, F2). `pdftotext` diff: only this line changed, plus layout offsets |
| R1 | 02_related:8–10 | "not statistically established \rv{} in the initial evaluations (a 32k-token evaluation on fresh prompts then located one, with the first loss between 11 and 61 samples)" (Yang & Chen's other half) | same text without `\rv` | same (32k; 11–61) | same | kept | EQUIV |
| R2 | 02_related:26 | "mastery is not sufficient for EI at this scale;" | "mastery is not sufficient for EI at this scale within 16 rounds;" | same | weaker (adds scope) | added | FIX? (task 2; supported, F7) |
| R3 | 02_related:26–27 (unchanged) | "rules at a quarter to a third of their former frequency are not mastered" | unchanged | same (1/4.17 = 0.24, 1/2.93 = 0.34) | same | n/a | MINOR: same rounding the task-2 fix removed elsewhere (F8) |
| S1 | 03_setup:31–34 | "\rv{} On plain reads of six earlier r8 models of the same network (run guided-tts: the full-exposure seeds s0--s2, and three seeds pretrained on proofs of at most six lines)" (P16) | same text without `\rv` | same (314,541) | same | kept | EQUIV |
| S2 | 03_setup:41–42 | [the negated-conditional schema: a formula, not quoted] | [a one-clause verbal statement of the same law, not quoted; see 03_setup:42] | same | same | n/a | FIX? (task 3; meaning kept, no error; F1) |
| S3 | 03_setup:42 | — | — | n/a | n/a | n/a | NOTE: the verbal statement determines the schema up to renaming (F10) |
| X1 | 04_measurement:85–86 | "\rv{} Unless stated otherwise, the models here are the earlier full-exposure seeds s0--s2 at r0, r8 and r16." (P16) | same text without `\rv` | same | same | kept | EQUIV |
| X2 | 04_measurement:96–97 | "\rv{} Guided decoding does not recover most of the compute-matched creations: the guided base proves 3/4/1 of the 22/21/14 at $\Kpub$." (P16, PUCT half dropped) | same text without `\rv` | same | same | kept (PUCT half stays dropped) | EQUIV |
| X3 | 04_measurement:104 | "each) for \rv{} the earlier full-exposure seeds s0--s2: the base (r0) and after 8 and 16 rounds" (P16, Fig. 7a) | same text without `\rv` | same | same | kept | EQUIV |
| X4 | 04_measurement:107 | "wall-clock \rv{} (the same seeds at r0 and r8)." (P16, Fig. 7b) | same text without `\rv` | same | same | kept | EQUIV |

## Findings

**MUST-FIX: none.** All 20 marks keep their correction's meaning; each is folded verbatim. No caveat or qualifier was dropped: "within 16 rounds", "on the pre-registered 106", "at $T=0.8$", "not pre-registered", "exploratory", "post hoc", "four on family members" and the model labels all survive. No claim got stronger. Every changed number has a data-backed reason.

**The lead's checklist.**
- **Abstract.**
  - P3 (00_abstract:13–14): kept, with the models labelled ("three earlier 8-round full-exposure runs"); "14--34 ... (14--21 under all five allocations)".
  - P5 (l.7): "strict" kept.
  - P13 (l.11–12): kept as "(four on family members, mostly one family), 1--7 times in 1.1--1.4M attempts".
  - P14 (l.5): "and its variants" kept.
- **Intro.**
  - P2 (01_intro:68–69, 87–88): kept.
  - P4 (114–116): kept.
  - P15 (107): kept.
  - P14 (24, 33–34; 16,961): kept.
- **§4 measurement:** P16 kept (85–86, 96–97, 104, 107).
- **§5 related:** Yang & Chen's other half kept (8–10).

**FIX? items, each a task-2/3 change that I checked:**

1. **F1. 03_setup:41–42 (task 3).**
   - The negated-conditional schema is replaced by a one-clause verbal statement of the same law (03_setup:42; not restated here).
   - I checked it against the removed schema. It is the same entailment in words, a correct classical law, and it matches the family name.
   - Elsewhere the paper refers to the family only by name or count: Table 2 "neg. cond." (16/15 strict), 05_results:16, 58, 128 and 10_appendix:37, 148. None of these uses the schema itself.
   - "substitution instances of the family's schema" (l.44) still reads correctly.
   - No error introduced, and no formula of this family remains in 03_setup.
2. **F2. Rarity factors: 00_abstract:5, 01_intro:25–26 and the Fig. 0 footnote.**
   - "3–4" becomes 2.9 for ¬-introduction and 4.2 for DN, as in the README's task-2 item.
   - The data supports this. `inputs/numbers_pre_run.md:1814–1816`: DN-containing records go from 21,274 (13.7 %) to 5,102 (3.29 %), which is 4.17×; NEGI goes from 15.21 % to 5.19 %, which is 2.93×. `review_coep/phase2/front.md` row A3 gives the same.
   - The new values are consistent with 05_results:277 and 08_limitations:31–32.
3. **F3. Abstract's last sentence (00_abstract:14–15).**
   - The clean text: "In this organism, seeds pretrained with the composition acquired classical families, and within 16 rounds of EI, seeds without it acquired none."
   - It is weaker than the marked text. It drops the unmeasured "EI amplified ..." interpretation and keeps both scopes.
   - It is supported by Table 3 (05_results:25–41): 6/6 full and 3/3 dose seeds acquired at least one family at r16; 0/6 knockout seeds did. It adds no claim beyond the abstract's own 0/6 vs 6/6.
   - It is almost the earlier reviewer's suggested wording (`review_coep/phase2/front.md` item 15).
   - Nit: "families" is a collective plural; full s4 acquired only converse contraposition.
4. **F4. σ definition (01_intro:31).**
   - The clean text: "to prove a goal $G$, assume $\neg G$, derive a contradiction, conclude $\neg\neg G$ ... and eliminate the double negation". "Positive" is gone.
   - This now matches Table 1 (03_setup:58–59), which has no positivity condition, and the data's σ (numbers_pre_run:1814, "DN cites a NEGI line").
   - "Positive" survives only in the separately defined "free positive reductio". No number depends on the change.
5. **F5. C4 sentence (01_intro:74–75).**
   - The clean text: "Its base had no success on three of the five in 18,432 fresh attempts each, though two of those three had one success each in an earlier, early-stopped sample."
   - This is correct. `review_coe/cert.log:35` gives knockout s1's base `1246` [1, 7168] and `2256` [1, 9216], and nothing on `1019`. LEDGER_pre_run P151 agrees.
   - It is consistent with 05_results:254–256. It adds a caveat, so it is weaker.
6. **F6. Null model's $N$ (01_intro:104–105).**
   - The clean text: "$N$ the number of training problems that need the composition, a variant or the lemma route of Table~\ref{tab:concepts} (here 123 of 4,495)".
   - This matches Table 1's strict-member row (03_setup:67–68: "by a free positive reductio or by the lemma route"). Knockout s1's ladder did prove strict held-out theorems by the lemma route at r20 (05_results:243–244, 7 proofs).
   - 123 is unchanged; `tab:concepts` exists (03_setup:53). Weaker.
7. **F7. 02_related:26.** "mastery is not sufficient for EI at this scale within 16 rounds". This adds the scope the README's task-2 list asked for. Weaker.

**MINOR**

- **F8. 02_related:26–27, unchanged.**
  - "rules at a quarter to a third of their former frequency" is the same rounding the task-2 fix corrected elsewhere: the factors are 0.24 for DN and 0.34 for ¬I.
  - The abstract, intro, Fig. 0, results and limitations now say 2.9×/4.2×, so §5 is the one place left on the old rounding.
  - Suggested wording: "at about a quarter (DN) and a third (¬-introduction) of their former frequency".
- **F9. 01_intro:75.**
  - The task-2 addition makes the intro the paper's first use of "early-stopped".
  - The term is defined nowhere: not in the glossary, and not at its other uses (05_results:112, 248, 262; 07_discussion:93; 11_checks:58).
  - A short gloss would fix it, e.g. "(sampling stopped at the first successes)".

**NOTE**

- **F10. 03_setup:42 (outside my brief; the lead's policy call).**
  - The verbal statement lets a reader reconstruct the negated-conditional schema exactly, up to renaming.
  - It therefore carries the same information as the removed formula.
  - If task 3 was meant to keep that renaming class (which it shares with a textbook72 problem) out of a circulated draft, a verbal restatement may not achieve it. Naming the family only, or using a non-sealed instance, would.
- **M3.** The date line changed to "Draft of 2026-10-14. Not for circulation."

Nothing outside the hunks broke in my files. No dangling references, and every changed sentence is grammatical. The new forward reference to `tab:concepts` from the intro resolves.
