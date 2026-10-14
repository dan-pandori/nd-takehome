# Phase-1 sub-audit: paper RESULTS + CHECKS (clean vs marked)

- **Part:** §3 Results (`sections/05_results.tex`) and Appendix I (`sections/11_checks.tex`).
- **Compared:** `review_pc/marked/sections/{05_results,11_checks}.tex` (17 + 7 `\rv` marks, all found) against
  `paper/sections/…` (clean). I used `review_pc/prereview/` to see what each mark corrected.
- **Diff:** 20 line-hunks in 05 and 9 in 11. Besides the 24 mark folds there are 10 substantive edits: 9 task-2 fixes
  and 1 referent clarification.
- **Counts (my files):** 35 rows: **25 EQUIV, 9 FIX?, 0 MUST-FIX, 1 MINOR**. Two more rows (O1, O2) cover task-2
  candidates in other files that I was asked to check.
- **Result:** all 24 marks fold verbatim. Every reviewed qualifier survives, word for word: same-seed / independent
  draws; T 0.8 and the pre-registered 106; four plain draws plus one guided; earlier full ladders s0–s2; 3.2M Run-3
  organism under the older checker; Lean gate only and 72–88 %; Holm; 53 vs 72; rows vs distinct texts; 0.095; 0.020;
  per distinct text; five C1 counts; s3/s5. No leftover `\rv`. Every `\ref` label still exists.

Abbreviations: 05 = `paper/sections/05_results.tex`, 11 = `paper/sections/11_checks.tex`. "≡" = clean text identical
to the marked text with the `\rv{}` removed.

| # | clean loc | marked (quote) | clean (quote) | numbers | strength | caveat | verdict |
|---|---|---|---|---|---|---|---|
| 1 | 05:4–5 | "judged by Lean alone \rv{} (except the earlier organism's seeding result quoted for contrast in §nulls, which is labelled there)" | ≡ | same | same | kept (P8 scope) | EQUIV |
| 2 | 05:59–62 | "\rv{} The three UNDETERMINED verdicts at p = 0.034 rest on the Holm correction … without the correction those three families would meet NEEDS EXPOSURE" | ≡ | same | same | kept (P10) | EQUIV |
| 3 | 05:62–63 | "Holm is the conservative reading, and the review applied it too." | "…and the experiment's review applied it too." | same | same | n/a | EQUIV. This only clarifies the referent. P10 says "as the create-or-elicit review applied it". "The experiment" means create-or-elicit throughout the paper (05:144, 05:243; 04:8 "create-or-elicit review"). |
| 4 | 05:137–138 | "only seed 0's base is certified out of reach \rv{} (the pre-registered expectation of certificates on at least five of six bases missed; …)" | ≡ | same | same | kept (P2 miss) | EQUIV |
| 5 | 05:141–142 | "\rv{} The certificate is also specific to T=0.8: plain sampling at T=1.0 proved la_transfer_916 on this base (and on seed 1's…)" | ≡ | same | same | kept (P2). The "106 theorems … as pre-registered" scope is unchanged at 05:136. | EQUIV |
| 6 | 05:196 | "the probability rises to \rv{} 0.020, and the expected number of seeds to 0.74" | ≡ | same | same | n/a | EQUIV |
| 7 | 05:203–204 | "\rv{} The proofs are those the earlier full ladders (s0--s2) found, not the scored ladders' own." | ≡ | same | same | kept (P7) | EQUIV |
| 8 | 05:254–255 | "1019 … which \rv{} two of the four plain r16 draws had already proved once (the guided draw, twice)" | ≡ | same | same | kept (P6) | EQUIV |
| 9 | 05:263 | "Seed 5's base proved 1811;" | "Seed 5's base proved 1811 and the Peirce-sequent member 1142;" | added: 1142 | same (adds a fact) | n/a | **FIX?** (task-2). Supported by three sources. `review_coep/members.log` lists base s5's early-stopped successes as {1142: [1, 3072], 1811: [1, 13312]}. `review_coe/out_families.json` gives `family_of` 1142 = peirce_sequent and 1811 = contraposition_conv. Table 2's s5 column has 1 converse-contraposition success and 1 Peirce-sequent success, and Table 3's s5 row shows 2 (2). |
| 10 | 05:264 | "\rv{} in four and three of the four plain r16 draws respectively" | ≡ | same | same | kept (P6) | EQUIV |
| 11 | 05:265 | "and 1811 in none." | "and neither 1811 nor 1142 in any." | added: 1142 | same | n/a | **FIX?** Supported. In members.log, every s5 r16 draw (x0, x1, C1 std, C1 dbl, guided) contains only 1246 and/or 2256. |
| 12 | 05:266–267 | "1096 in both fresh draws (one of which also found 1963)" | "1096 in the other three plain r16 draws (one of which also found 1963)" | changed: 2 → 3 draws with 1096 | same (corrects an undercount) | n/a | **FIX?** (task-2). Supported by members.log for s2: x0 {1963}; x1 {1096: 2}; std {1096}; dbl {1096, 1963}; guided {}. This matches Table 1 (x1 = 1, g = 0). "One of which" (dbl) is still right. |
| 13 | 05:277 | "it also makes each constituent three to four times rarer." | "it also makes DN 4.2 times and ¬-introduction 2.9 times rarer." | changed: 3–4× → 4.2× / 2.9× | same | n/a | **FIX?** (task-2). Supported by the paragraph's own numbers: 13.73/3.29 = 4.17 and 15.21/5.19 = 2.93. Applied the same way in the abstract ("2.9–4.2"), intro, 08 and blog. |
| 14 | 05:283 | "textbook72 keeps −2.5 \rv{} on its 53 intuitionistic theorems (−7.5 on all 72)" | ≡ | same | same | kept (P12) | EQUIV |
| 15 | 05:289 | "one-sided Mann--Whitney \rv{} p = 0.095 (exact, allowing for the one tie; this paper)" | ≡ | same | same | n/a | EQUIV |
| 16 | 05:295–296 | "The general costs are a few theorems out of hundreds." | "The general costs are a few theorems: at r0, 4.3 of holdout250's 225 and 4.0 of textbook72's 53 intuitionistic theorems (2.5 of the 53 at r16)." | added: 4.3/225, 4.0/53, 2.5/53 (all from 05:281–283) | weaker (drops the understating "out of hundreds") | n/a | **FIX?** (task-2). The librarian listed this phrase in §6 (07:28). The identical sentence here was fixed too. Supported: 4.0 of 53 is not "out of hundreds" (earlier sub-audit `review_coep/phase2/results.md` row 138). Greedy −6.88 pp is left out, correctly: it sits entirely on σ-reference theorems (05:280–281). |
| 17 | 05:311–313 | "\rv{} One full seed (s3) is higher within families than overall, and one (s5) is below 0.5 (0.47) … holds on three of the four full seeds" | ≡ | same | same | kept | EQUIV |
| 18 | 05:327 | "\rv{} (the 3.2M-parameter whole-proof models of round 2 run 3, judged by the project's older checker, not by Lean alone)" | ≡ | same | same | kept (P8) | EQUIV |
| 19 | 05:345 | "It rejected all 150 re-submitted Lean rejections," | "It rejected all 150 re-submitted texts that the gate had rejected (all by its pre-filter)," | same (150) | same | n/a | **FIX?** (task-2). Supported, with a nit (Note A). The 150 are the reads' `LEANREJ` fail-examples (`review_coe/recheck_collect.py` l.38–39, l.106–107). `lean_gate.py` l.270 tags both pre-filter and Lean rejections as LEANREJ. None of the 1,303 gate-log lines under `artifacts/coe/` has rej ≠ filter, and earlier sub-audit row 160 agrees. |
| 20 | 05:346–349 | "\rv{} Every Lean-gate rejection … 72--88% of attempts (77--89% with cut-offs) end earlier … only 10--23% reach it. Neither check below covers those earlier failures." | ≡ | same | same | kept (P9) | EQUIV |
| 21 | 05:351–352 | "(\rv{} 222,135 rejected rows in rounds 1--16: 210,151 distinct texts, 21,055 of them on a by-contradiction step)" | ≡ | same | same | kept (rows vs texts) | EQUIV |
| 22 | 05:353 | "at \rv{} 1.4×10⁻⁵ per distinct text (1.4×10⁻⁴ on by-contradiction steps; one-sided 95%; C5)" | ≡ | same | same | kept ("per distinct text") | EQUIV |
| 23 | 05:355 | "\rv{} An independent checker written for this paper's review also accepted none of the 210,151 distinct texts." | ≡ | same | same | n/a | EQUIV |
| 24 | 05:360–363 | "\rv{} Same-seed re-evaluations … differ by at most one strict theorem per checkpoint …; they are independent draws, so these ±1 differences are sampling, not cap effects" | ≡ | same | same | kept (P1) | EQUIV |
| 25 | 11:5 | "\rv{} Same-seed evaluations of ten r16 checkpoints" | ≡ | same | same | kept (P1) | EQUIV |
| 26 | 11:7 | "assumed the \rv{} two draws would be paired, that is, would differ only where a cap binds. They do not" | ≡ | same | same | kept (P1) | EQUIV |
| 27 | 11:11–12 | "which is why \rv{} five of the ten counts differ … 3 here against 2 … 57, 40 and 28 against 58, 39 and 30 … 22 against 23" | ≡ | same | same | n/a | EQUIV |
| 28 | 11:48–49 | "with no early stopping and new sampling seeds." | "with no early stopping, new sampling seeds and batch 1,024." | added: batch 1,024 | same | n/a | **FIX?** (task-2). Supported: `artifacts/coe_paper/c4/ko_s1.json.args.json` has batch 1024, stop_successes 0 and seed0 9500. Every C1–C3 args file has batch 512, so 11:3's "batch 512 … unless stated" now holds. |
| 29 | 11:50 | "Knockout seed 3's base drew 18,432 on 916." | "…on 916, also at batch 1,024." | added: batch 1,024 | same | n/a | **FIX?** Supported: `c4/ko_s3.json.args.json` has batch 1024. |
| 30 | 11:62–63 | "\rv{} 222,135 rejected rows over 13 reasons, 22,522 … by-contradiction step; 210,151 distinct texts, 21,055 …" | ≡ | same | same | kept | EQUIV |
| 31 | 11:66–68 | "\rv{} 1.4×10⁻⁵ per distinct text overall and 1.4×10⁻⁴ on by-contradiction steps (the pre-registration's 1.3×10⁻⁵ and 1.3×10⁻⁴ were computed on rows)" | ≡ | same | same | kept | EQUIV |
| 32 | 11:68 | "Lean decided every other \rv{} row (2,132,659 accepted, none rejected)" | ≡ | same | same | n/a | EQUIV |
| 33 | 11:71–72 | "\rv{} An independent checker written for this paper's review, sharing no code with the checker above, also accepted none of the 210,151 distinct texts." | ≡ | same | same | n/a | EQUIV |
| 34 | 11:75–77 | "with their scripts in paper/scripts/ (figures.py prior, a3_member_prior.py, a4_first_solve.py, a5_waiting_time.py)" | "Their scripts are in paper/scripts/: … a3b_member_prior_gained.py, … a5_waiting_time.py and, for A5b, round2_extra.py" | added: 2 scripts | same | n/a | **FIX?** (task-2). Supported: both scripts exist. `paper/data/a3b_member_prior_gained.json` gives 0.83–0.93 (full) and 0.74–0.84 (dose). The `round2_extra.py` docstring describes A5b. |
| 35 | 11:77 vs 05:196 | (A5b script not named) | "for A5b, round2_extra.py" | — | same | n/a | **MINOR.** The newly named script prints jeffreys_106 = 0.0188 (a 20,000-draw Monte Carlo; `paper/data/round2_extra.json`), which rounds to 0.019. 05:196 gives 0.020, the review's exact posterior-predictive value (0.0199). Anyone who re-runs the listed script gets 0.019. Possible fix: "(a Monte Carlo, 0.019; exact 0.020)". |

**Task-2 candidates outside my files** (asked to check; the owning sub-auditor should cross-check):

| # | clean loc | marked | clean | numbers | strength | caveat | verdict |
|---|---|---|---|---|---|---|---|
| O1 | 02_related.tex:26 | "mastery is not sufficient for EI at this scale;" | "mastery is not sufficient for EI at this scale within 16 rounds;" | same | weaker | n/a | **FIX?** (task-2). Supported (the result is at r16). The same sentence's "a quarter to a third of their former frequency" is 1/4.2 = 0.24 to 1/2.9 = 0.34, so it agrees with row 13. |
| O2 | 10_appendix.tex:121–123; 08_limitations.tex:66–68 | "They kept no proof text, so their 1--2 successes could not be re-checked in Lean." | "Those of full s0 and s1 and knockout s0 kept no proof text … The others stored their accepted proofs (knockout s1's one, and the 8 and 15 distinct proofs behind the positive control's 6/17 and 13/17): Lean 4.34.1 accepts all 24 and rejects all 24 with the goal negated (this paper)." | added: 24 (1 + 8 + 15), a new Lean result | changes the claim (see Findings) | n/a | **FIX?** This is the **opposite** of the librarian's item. The storage split is backed by data; the new Lean result is unverified (Findings 1). |

## Findings

**MUST-FIX: none.** Every `\rv` correction in 05 and App. I is folded verbatim. No number changed except the task-2
fixes, no claim got stronger, and no reviewed caveat was dropped.

**FIX? items needing the reviewer's attention (data checks done):**

1. **O2: power-sampling comparators** (outside my files: `10_appendix.tex:121–123`, `08_limitations.tex:66–68`).
   - **Librarian's premise is wrong.** The librarian's task-2 item said the positive control's comparator solves (6/17,
     13/17) "also kept no proof text". The clean text says the opposite and adds a new Lean re-check: "Lean 4.34.1
     accepts all 24 and rejects all 24 with the goal negated (*this paper*)". 08 adds that they "all re-check".
   - **The storage split is right.** In `artifacts/coe/power/`, the `p2b_pc_plainT0.8.json` and
     `p2b_pc_plainT1.0.json` rows carry an `accepted` field: 8 and 15 distinct (theorem, text) entries over 6 and 13
     solved theorems. `p2_ko_s1_plainT1.0.json` stores 1. The `p2_{full_s0,full_s1,ko_s0}_plainT*.json` files have no
     `accepted` field. So the split and the 1 + 8 + 15 = 24 count are backed by data.
   - **The Lean outcome is not verified.** "24/24 accepted, 0/24 goal-negated" is a new result created during the
     cleaning run. I found no artefact for it in `paper/data/`. It may sit under `artifacts/paper_clean/`, which I may
     not open. The reviewer should confirm that an artefact exists before accepting it. Without one, revert to the
     cautious "kept no proof text" only for full s0/s1 and ko s0, and drop the re-check claim.
2. **05:263–267: knockout s5's 1142 and s2's draws.** These are correct against `review_coep/members.log` and
   `review_coe/out_families.json` (rows 9, 11, 12). No action is needed.
3. **05:345: "150 re-submitted texts that the gate had rejected (all by its pre-filter)".** Correct.
   - **Note A (nit, optional):** the 150 were checked as re-renderings of the stored ND strings (kind `nd` in
     `review_coe/recheck_collect.py` l.106–107), not as the literal sampled texts. "Texts" is as loose as the marked
     "Lean rejections" was.
4. **05:277: "DN 4.2 times and ¬-introduction 2.9 times rarer"**, and **05:295–296**, where "out of hundreds" is
   replaced by the actual denominators. Both are correct from the paper's own numbers (rows 13, 16).
5. **11:48–50: C4 at batch 1,024**, and **11:75–77: the A3b/A5b scripts**. Both are correct (rows 28, 29, 34).

**MINOR:**

- **11:77 (row 35).** The newly named A5b script, `round2_extra.py`, yields 0.0188 ≈ 0.019. The text's 0.020 is the
  review's exact value. Optionally say so in App. I.

**Not changed, noted only.** 05:113's "about 2.6 times the cost per attempt" (earlier sub-audit item 14) is untouched
and was not on the task-2 list. No action is needed here.
