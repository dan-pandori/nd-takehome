# Review: paper-clean (clean paper and blog from the reviewed reading copy)

Reviewer: agent:claude (independent session), 2026-10-14, started 06:42 UTC. Run brief: nd-rl `9db656a`
(`docs/proposals/paper/BRIEF_paper-clean.md`). Pre-registration: `preregistration/paper-clean.md` (committed 05:27).
Run branch `dan_paper-clean` at `86b705ee`. Marked reading copy: nd-rl `7709669:docs/papers/create-or-elicit/`
(the run's first commit `11d07d13` copied it byte for byte; checked). Pre-review text: nd-rl `d841408`. Kit:
`review_pc/` (own scripts in `review_pc/kit/`, sub-auditor reports in `review_pc/phase1/`, outputs in `review_pc/`).

## §Recount (phase 1)

Phase 1 was done in `~/review/paper-clean` (write-ups removed). I did not open `run_paper_clean.md`, `numbers.md`,
`STATUS.md`, `log.md`, `paper/CLEANUP.md`, `paper/README.md`, `paper/next_steps.md` or
`artifacts/paper_clean/*.md`. Two exceptions:
- my sealed-class scanner was run over those files and printed only hit counts and textbook72 IDs;
- I read the run's four check scripts in `artifacts/paper_clean/*.py` (code, not results).

My session's start-up context showed the run branch's last five commit subjects; I used none of their numbers.

Four read-only sub-auditors compared clean against marked, claim by claim. They worked by part: front (00–04 and
`main.tex`), results (05, 11), back (07–10 and `refs.bib`) and the blog. They worked under the same independence rules
(`review_pc/phase1/AUDITOR_COMMON.md`). I re-derived every consequential row myself from the data, as listed below.

### Hard constraints: no violation

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72` = `origin/main`'s |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064`, unchanged since the base `1ad2a691` (= `origin/main`'s) |
| code touched | none. The run changed only `paper/`, `artifacts/paper_clean/`, `preregistration/paper-clean.md`, `log.md`, `numbers.md`, `STATUS.md`, `run_paper_clean.md`. No training or evaluation code changed, so the inherited "no evaluation file in training code" property is unchanged |
| `nd_verify` as a judge | not used. The run's four scripts do not import it; its Lean re-check calls `lean_judge` (Lean 4 core) |
| pods / spend | none |

### E1 — marks and numbers

- **Marks:** `\rv` fell from 60 in the marked sections, plus its definition in `main.tex`, to 0. *[review]* fell
  from 32 in the marked blog (31 in the body, 1 in the librarian's header) to 0. The rebuilt PDF's text has 0
  "[review]" and no reading-copy box.
- **Numbers:** `review_pc/kit/numdiff.py` aligns each file's number sequence, marked against clean, and prints every
  change in context (`review_pc/numdiff.txt`).
  - **Paper:** no number in `sections/` was removed. One changed: the abstract's "3--4" became "2.9--4.2". Every
    inserted number belongs to a task-2 item:
    - item 6: 2.9 and 4.2 in the intro, §3, §7 and Fig. 0;
    - item 7: `1142` and the r16 draws;
    - item 8: batch 1,024 and the a3b/A5b scripts;
    - item 9: 105, the seeds 0/3/1/4/2;
    - item 10: 4.3/225, 4.0/53, 2.5/53;
    - item 11: "within 16 rounds";
    - item 12: 1, 8, 15, 6/17, 13/17, 24, 24, Lean 4.34.1.

    `main.tex` lost only the reading-copy box, the date and the `\rv` colour.
  - **Blog:** each dropped number belongs to a cut passage (listed under E6). Three numbers changed: the draft date;
    Fig. 2's alt text, now "12 of 15 runs" (B6's own wording, already in the marked caption); and "three to four
    times" → "2.9 and 4.2" (item 6). No number changed value or referent.
- **E1 holds.**

### E2 — the librarian's 13 items, checked against the data

| # | item | what the clean text now says | my check | verdict |
|---|---|---|---|---|
| 1 | σ "for a positive goal G" | intro: "to prove a goal G" | Table 1 defines σ with no positivity condition; positivity belongs to "free positive reductio". In D (`create-or-elicit/data/coe/src/train_k12.jsonl.gz`), my own parser (`kit/sigma_polarity.py`) finds σ in 16,703 records (= the paper's count) on 17,387 lines. 1,741 of those lines (10.0 %, in 1,721 records) have a negated G | real error, fixed |
| 2 | 123 strict theorems "require the composition or a variant" | "need the composition, a variant or the lemma route of Table 1" | Table 1's strict-member row says the same (free positive reductio or lemma route). 123 unchanged | real, fixed |
| 3 | C4 sentence omits early-stopped successes | "…though two of those three had one success each in an earlier, early-stopped sample" | `review_coe/cert.log` l.35: s1 `1246` 1/7,168, `2256` 1/9,216. C4: 0/18,432 on `1019`, `1246`, `2256` (ledger P150) | real, fixed |
| 4 | abstract's last sentence states an interpretation | "seeds pretrained with the composition acquired classical families, and within 16 rounds of EI, seeds without it acquired none" | "acquired" is the abstract's own pre-registered indicator (6/6 full and 3/3 dose against 0/6; `acquired_during_rl.json` gives 5/6 against 0/6 for *new* families, stated separately). "EI amplified" is gone; both scope qualifiers stay. Not stronger | real, fixed |
| 5 | "150 re-submitted Lean rejections" | "150 re-submitted texts that the gate had rejected (all by its pre-filter)" | All 1,368 `[lean_gate]` summary lines in 121 log files under `artifacts/coe*` have rej = filter (12.9 M rejections, prefilter=on). The 150 are the reads' `LEANREJ` samples (create-or-elicit review l.272) | real, fixed |
| 6 | "three to four times rarer" | DN 4.2×, ¬-introduction 2.9× (abstract, intro, §3, §7, Fig. 0, blog) | `shape_k12_vs_ko.json`, share of records: DN 13.725 → 3.292 % (4.17×), NEGI 15.208 → 5.191 % (2.93×). The paper states record shares (05:273–277). By line share the old range would have held (3.90×, 3.03×) | real for the paper's metric, fixed. `02_related:26` keeps "a quarter to a third" (0.24 and 0.34; MINOR) |
| 7 | s5 base also proved `1142`; s2's x1 draw also proved `1096` | s5: "…neither `1811` nor `1142` in any" of the four plain draws. s2: "`1963` in the main evaluation and `1096` in the other three plain r16 draws (one of which also found `1963`)" | My per-row recount on `strict106`: s2 x0 {1963}, x1 {1096}, C1 std {1096}, C1 dbl {1096, 1963}. s5: `1246` in 4/4, `2256` in 3/4, `1811`/`1142` in 0/4. The s5 base: `cert.log` l.51 (`1142` 1/3,072, `1811` 1/13,312) and `certificates.json` (cc 1, Peirce sequent 1) | real, fixed exactly |
| 8 | App. I implies batch 512 everywhere; the script list omits A3b/A5b | C4 "…new sampling seeds and batch 1,024", s3 "also at batch 1,024". The opening keeps "batch 512 … unless stated". Lists `a3b_member_prior_gained.py` and, for A5b, `round2_extra.py` | `c4/ko_s{1,3}.json.args.json`: batch 1024. Both scripts exist and are the A3b/A5b code | real, fixed. MINOR: `round2_extra.py` prints A5b's Monte-Carlo 0.0188, while §3 quotes the review's exact 0.020 |
| 9 | "the base rate predicts which seeds move" | a zero rate predicted no movement (s0, s3) and the highest rate the most (s1); s4, with the second-highest rate, never proved a strict training theorem, while s2, with the lowest non-zero rate, did | `paper/data/a5_waiting.json`: s1 5.36e-6 (first r9, cum 5), s4 2.21e-6 (never by r16), s5 1.41e-6 (r14), s2 7.47e-7 (r14), s0 = s3 = 0. Same order in `certificates.json` pool105 | real, fixed |
| 10 | "a few theorems out of hundreds" | "a few theorems: at r0, 4.3 of holdout250's 225 and 4.0 of textbook72's 53 intuitionistic theorems (2.5 of the 53 at r16)" (§3 and §6) | Ledger P57 (reviewed). The model label is in §3.6 (05:282: "three full seeds against six knockout seeds") | real, fixed |
| 11 | "mastery is not sufficient" lacks the scope | "…at this scale within 16 rounds" | — | real, fixed |
| 12 | the power-sampling positive control's comparators "also kept no proof text" | only full s0/s1 and knockout s0 kept none; the others stored their accepted proofs (knockout s1: 1; positive control: 8 and 15 distinct): "Lean 4.34.1 accepts all 24 and rejects all 24 with the goal negated" | `artifacts/coe/power/*plainT*.json`: `accepted` texts exist only in `p2_ko_s1_plainT1.0` (1), `p2b_pc_plainT0.8` (8) and `p2b_pc_plainT1.0` (15). My own ND→Lean renderer (`kit/ndlean.py`): 24/24 accepted (Lean 4.34.1 and 4.35.0), 0/24 with the goal negated | the note was wrong; changed differently, and the new claim reproduces |
| 13 | blog: "hand-picked"; "simplest kind", "routinely"; power-sampling models unnamed; Fig. 2 alt text and title | "chosen in advance by a fixed rule"; "fine-tunes on its own successes (rejection-sampling fine-tuning)"; "routinely" gone; models named "two earlier full runs' bases" and "two knockout bases"; alt text and PNG title "12 of the 15 runs" | Paper 04:25–26 ("pre-selected as the most reliable r8 proofs"). The power files' `ckpt` fields are `ckpts/coe/old/stage1_best12_s{0,1}` and `stage1_ko_s{0,1}`, so the names are right. `figures.py` changed only the two title strings; the regenerated PNG shows 12 lines (3 full, 3 dose, 6 knockout) | real, fixed |

**E2 holds.** 12 items were real errors and are fixed; 1 (item 12) was changed differently because the note was
partly wrong. Pre-registered: 9–12 real and 1–4 other. No headline count of the abstract or the intro changed; the
abstract's descriptive rarity factor did.

### E3 — textbook72: no printed theorem in a sealed class

The kit is `kit/sealed.py`, my own code:
- a tokenizer and precedence parser for Unicode, LaTeX (including `lstlisting` escapes), Lean headers (balanced
  parentheses), generator syntax and the verbal "P or not P";
- an order-sensitive key (renaming by first appearance, the `gen.canon_key` notion) and a premise-order-invariant
  key (minimum over atom bijections of sorted premises plus goal);
- each printed formula is also read with the antecedents of its goal moved left, a conjunctive antecedent uncurried
  and conjunctive premises split.

Sources: `sections/*.tex`, `main.tex`, the rebuilt `main.pdf` text, the text of every `figures/*.pdf`, `blog.md` and
`lean/*.lean`. textbook72 has 72 classes under both keys. The output masks every hit.

- **Positive control (marked copy):** the §2 negated-conditional schema hits `textbook_b98931f2…` under both
  keys.
  - My first extractor missed it: prose words starting with a capital broke the spans. Only the control exposed
    this, and I fixed the extractor.
- **Clean copy:** 19 distinct printed sequents or formulas. They include the statements of the two Lean theorems:
  `la_transfer_916`'s (Fig. 1, App. (b), the blog, `lean/`) and `1246`'s (App. (a)). They also include the
  goal-negated control. 0 are in a textbook72 class as printed, under either key (`review_pc/sealed_clean.txt`).
- **E3 holds:** one class hit before the fix, none after.

Three notes on E3:
- **N1.** One broader reading also hits, in both copies. Table 1's lemma-route formula (`03_setup.tex:62`), read
  with its antecedent as a premise, is in `textbook_dd80d9db…`'s class. Under the brief's method (the printed
  sequent) it is not a hit. The paper cannot avoid this law: it is the subject of the paper, and the abstract states
  it in words.
- **N2.** The replacement is a verbal statement of the same law, which the brief allows. A reader can rebuild the
  class from it, as the front sub-auditor also noted.
- **F3.** The run's own record `artifacts/paper_clean/equivalence_paper.md`, committed to the public fork, prints a
  sequent in `textbook_b98931f2…`'s class: my scanner finds a primary hit under both keys. Masking it there is
  advised (details under Findings).

### E4 — blog length and caveats

- **Length:** `wc -w` of `paper/blog.md` is 2,493 with the front matter and **2,487 without** (the method the
  pre-registration names). The 79-word Lean block, alt texts and captions are included. That is ≤ 2,500. The
  marked copy was 3,143 without front matter, of which 63 words were the librarian's header.
- **The four named caveats are present with their qualifiers:**
  - the 16-round scope: l.22 "in 16 rounds", l.25 "did not, within 16 rounds, learn them without it", l.26 "may
    be specific to ours", and l.185–187 (only converse contraposition passes "needs exposure");
  - the sampler-specific null: l.190–193 "we count it as a failure of our sampler";
  - rare, not absent: l.23–24 and §4, l.101–110;
  - power limits: l.185 "not for most single-family tests" and l.105–110 (certification limits).
- **E4 holds** for length and the named caveats. Two cuts remove results the paper carries: F1 and F2 below.

### E5 — PDF rebuild

I rebuilt both copies in scratch directories (`tectonic -X compile`, 0.17.0).
- Both exit 0, with 0 undefined references; the only "undefined" line is a font-shape warning, present in both.
- Overfull boxes are the same three as in the reading copy, all under 2 pt: 0.655 pt (03:78–86), 0.959 pt
  (04:31–48) and 1.924 pt (10:49–53).
- One new *underfull* box (10:74–179, badness 4805) is cosmetic.
- The committed `paper/main.pdf` has the same text as my rebuild (`pdftotext`). It has 35 pages.
- **E5 holds.**

### E6 — equivalence, clean against marked (own sub-auditors, then my checks)

| part | rows | EQUIV | FIX? (substantive, data-backed) | MUST-FIX | MINOR | NOTE |
|---|---|---|---|---|---|---|
| front (00–04, `main.tex`) | 35 | 22 | 9 | 0 | 2 | 2 |
| results (05, 11) | 35 | 25 | 9 | 0 | 1 | 0 |
| back (07–10, `refs.bib`) | 27 | 18 | 7 | 0 | 0 | 2 |
| blog | 70 | 54 | 9 | 1 | 2 | 4 |
| **total** | **167** | **119** | **34** | **1** | **5** | **8** |

- **Paper:** each of the 60 marks is folded verbatim.
  - The only rewording beyond a fold is weaker: "Doubling the caps moved each strict count" → "With doubled caps,
    each strict count differed" (fits P1).
  - Every substantive change is one of the 12 paper items above, or the task-3 schema.
  - No number changed outside them, no claim got stronger, and no reviewed qualifier was lost (P1–P17, the
    precision and own-number items).
  - `refs.bib` and `lean/` are byte-identical to the marked copy, and the appendix listings are unchanged.
- **Blog:**
  - 29 of the 31 marks are folded in place with their meaning. R29's definition of "Hardest" moved from Fig. 4's
    caption into the text just before the figure, so it is still defined at first use (B8). R23 was cut with its
    paragraph (F1).
  - No model label and no post hoc, exploratory or pre-registered label was lost.
  - No claim got stronger.
  - Every new phrasing is in the paper.
- **Lean, where this run adds or prints proofs:**
  - My renderer is validated on 250 generator proofs from D: 250/250 accepted, 0/250 with the goal negated, 0/250
    cross-paired, 0/150 with DN changed to reiteration. 1/150 survived a shifted reference; its mutated step is
    itself valid, because the new referent also contradicts the premise.
  - All four Lean listings printed in the paper and the blog (Fig. 1, App. (a) and (b), the blog block, which equals
    `lean/blog_example.lean`) compile under Lean 4.34.1 and 4.35.0. They have no errors and use only standard
    axioms (no `sorryAx`). `lean/blog_example_negctl.lean` is rejected.
  - Term sizes: no proof-length claim changed, so there is nothing to re-derive.

### Phase-1 findings

- **F1 (should fix, blog): the "Seeding didn't help" paragraph is gone** (marked l.171–173, mark R23).
  - It carried a null result the paper still reports (05:323–331, seeded minus control +0/+0/+2/+0/+0) and its
    missed pre-registered expectation (10:152, "≥ 3 seeds", observed 1/5).
  - It also carried the older-checker caveat on the earlier-organism contrast.
  - The review's B2 held the blog to "the same evidence as the paper, including the negative and null results", and
    named this paragraph's caveat. Cutting it is not a cut of wordiness, and no claim got stronger.
  - Restoring one sentence (about 23 words) needs about 10 words trimmed elsewhere: the blog has 13 words of
    headroom.
- **F2 (recommended, blog): the RL-phase likelihood sentence is gone.** It read: "one full run and one dose run moved
  strongly toward these proofs; the rest … ended between 8 units lower and 4 units higher".
  - The paper keeps it (05:208–212, "the levels separate … the changes do not").
  - It was the blog's only reading of Fig. 2's trajectories, and it cuts against an amplification reading.
  - It was not a reviewed caveat.
- **F3 (records): `artifacts/paper_clean/equivalence_paper.md` prints the removed schema.** The scanner finds a
  primary hit on `textbook_b98931f2…`.
  - It is a run record on the public fork, not a circulated draft.
  - The schema is already in the fork's pre-review `paper/` history.
  - Mask it; keep it out of the HF bucket.
- **MINOR:**
  - `02_related:26` "a quarter to a third" sits beside the corrected 2.9×/4.2×.
  - App. I now names `round2_extra.py` for A5b, which prints 0.0188, while §3 says 0.020 (the review's exact value).
  - "early-stopped" is used first in the intro's new clause and is defined nowhere; the marked copy already used it
    seven times.
  - The blog's Fig. 4 caption no longer defines "Hardest" (the text does, at l.167).
  - The blog's "that only a genuinely classical step can prove" now attaches to the 105 only.
- **NOTES:**
  - N1 and N2 above.
  - The fork's root `log.md` (l.5, 116, 198; take-home commits `a1271b85`, `0d8bee4d`, `fe14f1f1`, 2026-09-15 to 17)
    prints formulas in two textbook72 classes (`textbook_44157a16…`, `textbook_0dd5ea3d…`). This predates the run.
  - The power-sampling positive control's 17 theorems include 2 textbook72 problems (`set: tb72`), solved at T 1.0.
    That is scoring use from create-or-elicit and is allowed. The 24/24 re-check includes their proofs; no text is
    printed.

## §Comparison (phase 2)

I read `run_paper_clean.md`, `STATUS.md`, this run's sections of `log.md` and `numbers.md`, `paper/CLEANUP.md`,
`paper/README.md`, the `next_steps.md` and `LEDGER.md` diffs, and the executor's equivalence reports (the last only
where they bear on F1 and F3).

| # | claim (where) | my independent value | verdict |
|---|---|---|---|
| 1 | 60 paper marks folded (summary, STATUS, README, CLEANUP §1) | 60 → 0; 57 verbatim, 3 smoothed (Settings, §8 word order, "the experiment's review"), all equal or weaker | reproduces |
| 2 | "31 blog *[review]* marks folded" (summary, STATUS, README) | 29 folded in place. R29 moved into the text before Fig. 4. R23 was **cut** with the seeding paragraph. CLEANUP §6 says so precisely ("30 survive, #23 went with the seeding paragraph") | differs by one mark: reword the summary, STATUS and README to "30 folded, 1 cut with its claim" |
| 3 | 12 of 13 possible errors real and fixed; item 12's note wrong (summary, STATUS, CLEANUP §2) | 12 real and fixed; item 12 changed differently (E2 table) | reproduces |
| 4 | σ on a negated goal: 1,721 of 16,703 σ records, 1,585 only negated; 1,741 of 17,387 lines (numbers.md, CLEANUP item 1) | identical, with my own parser on create-or-elicit's copy of D | reproduces exactly |
| 5 | 1,307 of 1,307 gate lines in `logs/` (60 files) have rej = filter; 12,217,252 rejections (numbers.md, CLEANUP item 5) | identical in `logs/`. Over all of `artifacts/coe*`: 1,368 of 1,368 lines in 121 files, 12,919,685 | reproduces exactly |
| 6 | DN 4.17×, ¬I 2.93× (CLEANUP item 6) | 4.169×, 2.930× (record shares) | reproduces |
| 7 | s5 base `1142` 1/3,072, `1811` 1/13,312; s2 ladder x0 {1963}, x1 {1096 ×2}, C1 std {1096}, C1 dbl {1096, 1963} (CLEANUP item 7) | identical (per-row recount on `strict106`; `cert.log`) | reproduces exactly |
| 8 | C1–C3 reads batch 512; C4 batch 1,024; scripts exist (CLEANUP item 8) | C4 args batch 1024 (both); scripts present | reproduces. MINOR: the A5b script prints 0.0188, the text 0.020 |
| 9 | A5 rates and first successes per seed (CLEANUP item 9) | identical (`a5_waiting.json`, `certificates.json`); s3's base proved `916` (1/2,048), so "zero on the 105" is right | reproduces |
| 10 | general cost 4.3/225, 4.0/53 at r0; 2.5/53 at r16 (CLEANUP item 10) | ledger P57; labelled in §3.6 | reproduces |
| 11 | power comparators: 8/8, 15/15, 1/1 accepted, 24/24 rejected when negated; full s0/s1 and knockout s0 store none; models named (numbers.md, CLEANUP item 12, App. F) | own renderer: 24/24 (4.34.1 and 4.35.0), 0/24 negated; storage pattern identical | reproduces (independent harness) |
| 12 | power-sampling models in the blog: "two earlier full runs' bases" and "two knockout bases" (CLEANUP item 13) | `ckpt` = `old/stage1_best12_s{0,1}` and `stage1_ko_s{0,1}`; the knockout runs were on the 106 | reproduces |
| 13 | textbook72: "0 of 8 printed theorems" in a class; positive control hits `b98931f2…` (summary, STATUS, numbers.md, CLEANUP §3) | 0 of 19 by a mechanical extraction (the executor's 8 plus fragments and `have` statements). Control hits under both keys. A broader premise-moving reading of Table 1's lemma-route formula hits `dd80d9db…` (N1). | reproduces; the denominator is the executor's hand list |
| 14 | "The textbook72 check's output and CLEANUP no longer print the sealed schema" (log) | true for both (no primary hit). But `artifacts/paper_clean/equivalence_paper.md` prints it (F3) | reproduces as stated; one record not covered |
| 15 | blog 2,487 words without front matter, 2,493 whole file; marked 3,080 / 3,049 / 3,143 / 3,112 (summary, numbers.md, CLEANUP §4) | 2,487 / 2,493; marked 3,143 incl. the 63-word note, so 3,080 without it; minus the 31 marks, 3,049 / 3,112 | reproduces |
| 16 | "Removing these left no reviewed caveat without the claim it qualifies" (CLEANUP §4) | true: R23 went with its claim. But the cut claim is a null result the paper carries (F1) | reproduces as worded. log.md's "No reviewed caveat was cut" overstates (R23 was cut) |
| 17 | the brief's four caveats are present (CLEANUP §4) | present, with their qualifiers (E4) | reproduces |
| 18 | PDF 35 pp., no undefined references, only the three sub-2 pt overfull boxes; a 4.4 pt box removed (summary, CLEANUP §5) | identical in a scratch rebuild; no 4.4 pt box. One new underfull box (cosmetic) | reproduces |
| 19 | only `fig0_overview` and `blog_fig2_logp` regenerated, for the label and title (CLEANUP §5, log) | `figures.py` changed 2 strings; pixel rows differ only in the title band (fig2, rows 20–43) and the ratio line (fig0, rows 604–621) | reproduces |
| 20 | abstract 250 words (log) | `wc -w` 250 (marked 255) | reproduces |
| 21 | E6: first pass 2 blog must-fix, fixed; second pass 0 (summary, STATUS, CLEANUP §6) | as a record of the executor's checks, consistent with its reports. My independent pass: paper 0 must-fix (agrees); blog F1 (should restore) and F2 (recommended). The executor's checker classed both as accepted (b)-cuts, and `next_steps.md` proposal 4 lists them | reproduces as a process record; differs in judgment on F1 |
| 22 | `next_steps.md` 1b re-costed: 12.35 ms per attempt, 2.4 × 10⁷ attempts ≈ 82 A40-h ≈ $48 | `c4/ko_s1.json`: 350,208 attempts in 4,325.6 s = 12.35 ms; 82.3 h | reproduces |
| 23 | `next_steps.md` proposal 6: the two missing blog labels cost "about ten words, which the 2,500-word cap no longer leaves" | 2,500 − 2,487 = 13 words remain | differs: the labels fit |
| 24 | LEDGER P8 marked superseded by C4 | matches P150 and the C4 drop rule; neither text states the reading | reproduces |
| 25 | bucket `paper-clean/artifacts/paper_clean/` holds the 4 scripts and outputs; equivalence reports in git only (numbers.md, log) | `hf buckets ls`: the 8 files, 06:26:44 | reproduces |
| 26 | no pod, $0 (summary, STATUS) | `podbudget.log` has only the 05:24 registration; no pod rows | reproduces |
| 27 | pre-registration before any text change (prereg header) | `11d07d13` 05:27:04 precedes the first text commit `325a05c9` 05:29:38. Log times match commit times; none is ahead of the clock | reproduces |
| 28 | `run_paper_clean.md` ≤ 200 words | 191 | reproduces |

**Model labels.**
- Every number this run added names its models:
  - item 7 and item 9: the knockout seeds;
  - item 10: labelled in §3.6;
  - item 12: full s0/s1, knockout s0/s1 and the positive control. numbers.md gives checkpoint, 9.56M, `lean_staten`,
    from scratch, K12 or K12⁻.
- No label was lost in the paper or the blog.
- The earlier-organism claim that remains in the blog (GRPO) keeps "3.2 million parameters, whole proofs, older
  checker". The other one went with the seeding paragraph.

**Wording against n.**
- The new §6 sentence describes single seeds: s4 "never proved a strict training theorem" holds for its 16 rounds,
  the scope the paper uses throughout. Adding "in 16 rounds" there would be cleaner.
- No new difference claim rests on one seed.

**Expectations.**
- E1–E6 were committed before the work and are all hits. My recount agrees on each.
- Under E4 and E6, the blog's no-caveat-dropped standard holds as the run worded it ("no reviewed caveat without its
  claim"). It does not hold as review B2 applied it (F1).

## §Verdict

**Hard constraints:** none violated (nd_verify = `origin/main`, TEST_RUN_DONE unchanged, no code touched, nd_verify
unused, no pod). No quarantine.

**What stands:**
- **The paper:** the clean version is equivalent to the marked reading copy.
  - Each of the 60 corrections is folded with its meaning.
  - No number changed except the task-2 fixes, and each of those reproduces from the data.
  - No claim is stronger. The one widened claim, item 12's "kept no proof text" narrowed to three comparators, rests
    on a new Lean re-check that I reproduced with an independent renderer: 24/24, 0/24 negated.
- **The 13 librarian items:** 12 were real errors and are correctly fixed. Item 12's note was wrong.
- **textbook72:** no printed theorem is in a textbook72 renaming class under either key.
- **The PDF:** builds clean (35 pp., the reading copy's three sub-2 pt boxes).
- **The blog:**
  - it is 2,487 words;
  - it keeps the four named caveats and every B1–B8 correction;
  - it names the power-sampling models correctly;
  - it claims nothing the paper does not.

**What should be reworded:**
- `run_paper_clean.md`, `STATUS.md` and `paper/README.md`: "31 blog marks folded" → "30 folded; 1 (R23) cut with
  the seeding paragraph it qualified" (as CLEANUP §6 says).
- `log.md` "No reviewed caveat was cut" → as CLEANUP §4 words it.
- `next_steps.md` proposal 6: 13 words remain, so the two labels (post hoc free-positive-reductio counts;
  exploratory r24 continuation) fit within the cap.

**What I would restore in the blog (Dan's call; the run disclosed both cuts):**
- **F1:** a one-sentence seeding null. Example: "One extra RL round seeded with a rare σ proof changed nothing
  measurable (an earlier, smaller model under an older checker had responded)."
  - The paper carries it as a null and a missed pre-registered expectation.
  - The review's B2 held the blog to the paper's negative and null results.
- **F2:** the RL-phase likelihood clause, which the executor also ranks first to restore.
- F1 alone (about 23 words) needs about 10 words cut elsewhere; F1 and F2 together (about 38 words) need about 25.

**Records:**
- **F3:** mask the removed schema in `artifacts/paper_clean/equivalence_paper.md`, by ID as the brief allows. It is
  in git on the public fork, not in the bucket. `data/bs/textbook72.jsonl` itself is in the same repository, so this
  is hygiene, not a leak.
- Noted (pre-existing, not this run): the fork's root `log.md` prints formulas in two textbook72 classes.

**Not supported:** nothing. Every claim in the run's write-ups reproduces or differs only in wording.

**Minor text items (optional):**
- App. I names `round2_extra.py` (0.0188) beside §3's exact 0.020: say "0.019 by Monte Carlo; 0.020 exact".
- "early-stopped" is never defined in the paper (now first used in §1).
- `02_related`'s "a quarter to a third" stays approximate beside 2.9×/4.2×.

**Next measurement:** none is needed to settle this run. Every open item is editorial. The paper's open scientific
question is the knockout ladders' σ rate along the run (`next_steps.md` 1b). With the corrected cost (12.35 ms per
attempt, ≈ 82 A40-hours ≈ $48), it is the measurement that would turn A5's waiting-time null into an observed rate.

Review time: 06:42–07:12 UTC (four sub-auditors in parallel during phase 1).
