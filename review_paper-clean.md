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
  marked copy was 3,143 without front matter, of which about 60 words were the librarian's header.
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
  - Restoring one sentence (about 25 words) needs about 12 words trimmed elsewhere: the blog has 13 words of
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
