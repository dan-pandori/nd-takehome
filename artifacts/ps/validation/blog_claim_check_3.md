# Claim check 3: `proof_strategies/blog.md` (HEAD 9fcab777, 2026-10-18 21:44 UTC)

Third pass, kept short. It re-checks the items left from pass 2 and every number in the passages listed in the brief.

**Sources:**
- `TABLES.md` § 2–5, § 8 and § 11
- `artifacts/ps/rl_found.json`, recomputed here for all 12 ladders
- `summary/k12.json`, `k12ko.json` and `k12dose1.json`
- numbers.md § proof-strategies and § create-or-elicit
- `review_create-or-elicit.md`
- `coe/coe_rounds.py` (`sigma_subtype`)
- `sealed_selftest.json`
- `EXAMPLES.md`
- `figures.py` and the committed PNG

**Re-run and internal checks:**
- `blog_lean_check.py`: 12 / 12 snippets accepted, 1 schematic skipped.
- `rl_found.json`, every ladder and every round:
  - reductio = working + template-only;
  - free ≤ working;
  - 0 unparsable proofs.

**Verdict:** All numbers in the checked passages match their sources. Two wording problems remain, R1 and R2 below.

## 1. Status of the pass-2 items

| # | status | note |
|---|---|---|
| N1 | FIXED | "Both arms saw both halves … working proofs of a negation (2 % of each set) and double-negation elimination on a stated double negation (3 %). The knockout removed only their combination." Working ¬I is 2.15 % in K12 (3,330) and 2.25 % in K12⁻ (3,481). DNE on a premise or hypothesis is ≤ 2.91 % in K12 and 3.29 % in K12⁻ (5,102, none on a derived line). |
| N2 | FIXED | The short version, the figure legend ("working: ¬G does more than clash at once with G or a supplied ¬¬G"; the PNG is regenerated) and the caveat now agree. |
| N3 | PARTLY | The knockout is now counted in free reductios (0–32), so the core problem is fixed. Two residuals: the sentence about "other" working reductios is not true of one seed (R2), and nothing reconciles these counts with create-or-elicit's 17–50 thousand / 1–34 (R3). |
| N4 | FIXED (removed) | The "order of magnitude" sentence is gone. |
| N5 | FIXED | "0.15–0.27 % of the full models' new proofs" and "1.2–3.9 % of the proofs first found that round". |
| N6 | FIXED | "K12 holds 59 working reductios; the 1 % dose set holds only 5". "Templates only" is gone. |
| N7 | FIXED | "pretrained with σ at 1 % of the set". |
| N8 | FIXED | "12 of create-or-elicit's 15 RL runs (the other three are older)". Terse, but adequate. |
| N9 | FIXED | "of the 123 σ-covered problems" appears twice. |
| N10 | FIXED | "with necessary use on 33–78 of the 123 σ-covered problems". |
| N11 | FIXED | "held out from training and never printed (6 K12 records are renamed twins of some)". The source is `sealed_selftest.json` `k12_records_in_sealed_classes: 6`. Wording nit in R7. |
| N12 | FIXED | "at least half its held-out σ-covered instances solved in 256 tries"; "(1 before RL)" for dose (s1: contraposition_conv 17 / 18 at pend); "(5 before RL)" for full (review l. 103: 5 / 6 at the bar at pend). |
| N13 | FIXED | The sentence is gone. The caveat says "a search's or Charles's". |
| N14 | FIXED | "Every proof can be written in Lean". |
| N15 | PARTLY | (a)–(e) are fixed: "G the goal", "(¬I: …)" in item 7, "law instances", "(the knockout arm)", and `have` is in the glossary. (f) remains (R6). |
| N16 | FIXED | "Many K12 proofs contain idle steps." |
| N17 | FIXED | "260 proofs by hand (two labels each)". |
| N18 | FIXED | "the three we analysed … before any RL update … over 15 rounds of RL". The numbers it now quotes are *free* counts, labelled "working" (R1). |
| N19 | FIXED | "mostly *forall x: Calgary*'s". |
| N20 | FIXED | "(mostly) special cases". |
| #10 | FIXED | `have l : X := t; …` is glossed. |
| #16 | FIXED | "Grey: proofs in which every instance is idle (the 28 % and 38 % below count proofs with any idle step)". The `figures.py` legend matches. |
| #33 | FIXED | Both residuals (N1, N6) are resolved. |

## 2. Numbers checked (all match)

**Epistemic status:**
- 260 / 260 on two labels (numbers.md: "uses and primary", v1.1);
- 155,000 / 155,000 for the second implementation.

**Short version:**
- 155,000; 38 % (37.64);
- 10.8 % (16,717); 59; none on a classical-only theorem;
- textbook problems: 187; 21 / 0.04, 38 / 2 (2.15), 12 / 0.05;
- 27–45 (free r1 38 / 27 / 45) and 5,915–22,013 (free r2–16 22,013 / 7,886 / 5,915). See R1.

**K12 section:**
- 28 % (28.20), 38 % (37.64), 24 % (23.53);
- grey bars 22.1 % (→I) and 35.4 % (∨E), which are not the 28 % and 38 %, and the note now says so;
- 990 problems; a third shorter (7.00 → 4.69);
- 35 → 0; 43 → 6 (42.5 = 421 / 990 → 6.1); 29 → 23; 6 → 16.

**Template section:**
- 16,658 / 16,717; three kinds, each with an `EXAMPLES.md` example (558, 359, 137);
- the working example is K12 record 131990 (free kind), and the text's description of both cases is right;
- 59 of 59 are on theorems provable without the classical rule; 48 have a negated goal;
- 6,238 classical-only = 4,279 with a reductio + 1,959 DNE only; σ-covered 0.

**Textbooks:**
- 173 + 14; 1,610; 72 (58 searched); 6 twins (`sealed_selftest.json`);
- table: 21 / 0.04, 12 / 0.05, 14 / 0.03, 38 / 2, 34 / 9;
- law instances and textbook72 point the same way on all 5 rows;
- 19 % (35 / 187); 124 decided; 37 % (46 / 124); 3.7 % (22 / 594).

**Knockout section:**
- 6 / 6 (5 at pend), 0 / 6, 3 / 3 (1 at pend); 59 vs 5.
- Free working reductios:
  - full r1 38 / 27 / 45, r2–16 22,013 / 7,886 / 5,915;
  - dose 13 / 43 / 7, then 9,047–15,731;
  - knockout r1 0 on every seed, r2–16 0 / 32 / 2 / 1 / 0 / 12 (range 0–32).
- Knockout working, r2–16: 358 / 399 / 772 / 169 / 72 / 375 (range 72–772).
- σ-covered: 17 / 15 / 20 → 78 / 33 / 36; knockout ≤ 5 (0 / 5 / 1 / 0 / 0 / 2) of 123.
- Free shares:
  - round 1: 0.267 / 0.146 / 0.261 %, so 0.15–0.27 %;
  - round 16 alone: 1,955 / 50,640, 707 / 51,988, 587 / 49,332 = 3.86 / 1.36 / 1.19 %, so 1.2–3.9 %.
- "2 %" and "3 %" as in N1.

**Caveats:**
- 15 = 6 + 6 + 3 models; 12 = 3 + 6 + 3;
- 9.6 M parameters (9,560,832);
- classical-only is exact (G4ip); necessity is bounded at 12 lines.

## 3. Remaining problems

**R1. MISLEADING (mild).** The short-version paragraph says the full models "wrote working ones anyway: the three we analysed wrote 27–45 each before any RL update and 5,915–22,013 more".
- These are the *free* counts. All working reductios are 76 / 32 / 52 and 26,450 / 9,082 / 6,951 (32–76; 6,951–26,450).
- "Free" is defined only in the knockout section, so a reader who quotes the short version will mislabel the numbers.
- *Fix:* "wrote 27–45 free ones each (positive goal, no double negation supplied: the kind classical-only problems need) before any RL update and 5,915–22,013 more over 15 rounds". Alternatively, quote the working numbers.

**R2. WRONG (minor).** "Their other working reductios (72–772 in all) lean on a double negation the problem states."
- Knockout s2's 770 non-free working reductios in rounds 2–16 include **113 with a negated goal** (`neg_goal_working_by_round`). The other five knockout seeds have 0.
- "72–772" is all working reductios in rounds 2–16, free ones included. The "other" ones are 72–770 (74–771 over rounds 1–16).
- numbers.md § proof-strategies repeats the claim: "the knockout's other working ones lean on a supplied double negation".
- *Fix:* "Their other working reductios (72–772 per seed in rounds 2–16, free ones included) mostly lean on a double negation the problem states; one seed also wrote 113 that prove a 'not'."

**R3. OK-BUT-NOTE (cross-document; residual of N3).** Create-or-elicit counts "free positive reductio" proofs from the same found files and gets higher numbers. A reader of both write-ups sees two different sets under the same word, "free".

| | create-or-elicit | this post (free, rounds 1–16) |
|---|---|---|
| full s3–s5 | 49,600 / 20,384 / 17,429 | 22,051 / 7,913 / 5,960 |
| knockout | 0 / 34 / 4 / 1 / 2 / 16 ("5 / 6 knockout ladders", "1–34") | 0 / 32 / 2 / 1 / 0 / 12 (4 / 6 ladders) |
| round 1, full | 418–665 | 27–45 |
| round 1, dose | 213 / 170 / 219 | 13 / 43 / 7 |

- *Cause* (`coe_rounds.sigma_subtype`): create-or-elicit's `pos_free*` is any DN on a derived line with a positive goal and no ¬¬G in the prompt. It does not require ¬G to be used, so it includes vacuous and pointless reductios. The post's "free" is the subset of those that are also working. Every create-or-elicit count is ≥ the post's.
- The 21:41 log calls the knockout counts "≈ create-or-elicit's own" but is silent on the full arm, where the gap is 2–3×.
- *Fix (one footnote):* "Create-or-elicit's 'free positive reductio' counts (17–50 thousand per full ladder, 0–34 per knockout) also include template ones; ours keep only working ones."

**R4. OK-BUT-NOTE.** The models are counted in *free* working reductios, but the pretraining is quoted in all working ones (K12 59, dose 5).
- The like-for-like numbers are K12 6 free, dose set 2 free, K12⁻ 0 (TABLES § 3). Using them makes the contrast exact, and stronger.
- *Fix:* "K12 holds 59 working reductios (6 free); the 1 % dose set holds 5 (2 free)".

**R5. OK-BUT-NOTE (figure).** In `reductio_kinds.png`:
- The row label "K12 + 1 % dose" misdescribes the set. It is K12⁻ with 1,550 refill records swapped for σ records (numbers.md § coe Phase 3). TABLES § 11 has the same slip: "K12 + 1 % σ (dose)".
- The cap-6 row is still never mentioned in the text.
- The K12 row's "n = 16,717 (working 59)" is clipped at the right edge.
- *Fix:* label the row "dose set (K12⁻, σ at 1 %)", widen the right margin, and drop or mention cap-6.

**R6. OK-BUT-NOTE (residual of N15 f).**
- "Examples are from K12", but item 12's `EXAMPLES.md` example is a textbook-schema instance from the RL pools (record 819).
- "Held-out", "topped up", "modus ponens" and "a bounded search could decide" are still unglossed.
- *Fix:* "examples are from K12 unless noted", plus short glosses or plainer words.

**R7. Nit.** "6 K12 records are renamed twins of some".
- `sealed.py` counts a match under any of three keys: `canon_key`, renaming plus premise order, and the curried normal form. So "renamed" undersells.
- *Fix:* "6 K12 records match some up to renaming, premise order or currying".

## RL recount (from `rl_found.json`; free working / all working)

| ladder | r1 free / working / new | r2–16 free / working | r16 free / new | non-free r2–16 with a negated goal |
|---|---|---|---|---|
| full_s3 | 38 / 76 / 14,212 | 22,013 / 26,450 | 1,955 / 50,640 | 4,360 of 4,437 |
| full_s4 | 27 / 32 / 18,463 | 7,886 / 9,082 | 707 / 51,988 | 1,009 of 1,196 |
| full_s5 | 45 / 52 / 17,212 | 5,915 / 6,951 | 587 / 49,332 | 784 of 1,036 |
| dose1_s0 | 13 / 15 / 14,359 | 15,731 / 16,970 | 1,527 / 63,289 | 514 of 1,239 |
| dose1_s1 | 43 / 45 / 13,649 | 9,920 / 11,057 | 961 / 51,926 | 661 of 1,137 |
| dose1_s2 | 7 / 7 / 15,729 | 9,047 / 9,969 | 859 / 50,404 | 353 of 922 |
| ko_s0 | 0 / 1 / 13,838 | 0 / 358 | 0 / 48,992 | 0 of 358 |
| ko_s1 | 0 / 0 / 13,597 | 32 / 399 | 11 / 48,413 | 0 of 367 |
| ko_s2 | 0 / 1 / 16,984 | 2 / 772 | 0 / 58,772 | **113 of 770** |
| ko_s3 | 0 / 0 / 14,210 | 1 / 169 | 0 / 50,878 | 0 of 168 |
| ko_s4 | 0 / 2 / 14,967 | 0 / 72 | 0 / 50,865 | 0 of 72 |
| ko_s5 | 0 / 1 / 18,786 | 12 / 375 | 5 / 52,675 | 0 of 363 |

σ-covered targets with a working reductio, round 1 → by round 16 (of 123):

| arm | seeds |
|---|---|
| full | 17 → 78, 15 → 33, 20 → 36 |
| dose | 2 → 69, 17 → 46, 2 → 41 |
| knockout | 0 → 0, 0 → 5, 0 → 1, 0 → 0, 0 → 0, 0 → 2 |
