# Equivalence check, second pass: the passages changed after the first pass

Independent check, 2026-10-14. Read-only except for this file.

- **Scope:** `git diff 4e972d0f 40264b03 -- paper/sections paper/blog.md`. That is 14 edits, grouped by paragraph into
  **10 passages**: 7 in `paper/blog.md`, 1 each in `00_abstract.tex`, `07_discussion.tex` and `11_checks.tex`. No other
  file under `paper/sections/` and nothing else in `paper/blog.md` changed.
- **MARKED:** `git show 11d07d13:paper/blog.md` and `git show 11d07d13:paper/sections/<file>`. Line numbers are **M**.
- **CLEAN:** commit `40264b03`, the same as the working tree. Line numbers are **C**.
- **Motivating findings:** `equivalence_paper.md` M1–M3. From `equivalence_blog.md`, must-fix M1–M2 and minor m1–m5.
  m6–m10 called for no text change in these files.

## Summary

- **Passages checked: 10** (blog 7, paper 3). All 10 pass all four checks.
- **First-pass findings resolved: all 10 that asked for a text change.**
  - Paper: M1, M2 (both parts: the pool and "the required pools") and M3.
  - Blog must-fix: 1 (power sampling) and 2 ("statistically").
  - Blog minor: m1 ("But"), m2 ("implementation of"), m3 ("the experiment's numbers"), m4 ("more random") and m5 (the
    comparison's baseline).
  - Blog must-fix 2, m1 and m2 now match the marked copy word for word.
- **Numbers:** every number in each marked passage is still present and unchanged. A script compared digits and number
  words per passage and found 0 lost. All added numbers are listed fixes in CLEANUP §2:
  - "106" and "two … two" (item 13);
  - "105" and seed numbers (item 9);
  - "1,024" (item 8).
- **Strength:** no claim is stronger than in the marked copy, and no hedge or scope was dropped.
  - Causal readings weakened: in the abstract, "amplified" and the first clean version's "under EI" are gone. In Checks,
    "moved" became "differed".
  - Scopes kept: "In this organism" and "within 16 rounds" (abstract); "at our usual temperature" and the one budget
    conversion (§4 of the blog); "on the 106" (Checks); "A null we can't interpret" and "a failure of our sampler" (power
    sampling).
  - Scope added: "on the 105 family members" (discussion).
- **Blog length:**
  - `wc -w paper/blog.md`: **2,493**.
  - Without the YAML front matter (lines 1–4): **2,487**.
  - Both are ≤ 2,500, which leaves 13 words of headroom on the pre-registered count.
  - This commit added 5 words net. The restorations and fixes added 13: power sentence +3, Checks baseline +3,
    "statistically" +2, "more random" +2, "implementation of" +2, "the experiment's" +1. The trims removed 8: alt text −3,
    "widely used" −2, "that … the" −2, "that runs" → "run" −1.
- **Abstract length:** `wc -w paper/sections/00_abstract.tex` = **250** (≤ 250).
- **Findings: 0 must-fix, 3 minor.** One is a readability point in the abstract. Two are about `CLEANUP.md`'s record of
  this commit.

## Method

1. Listed every edit with `git diff --word-diff=plain 4e972d0f 40264b03 -- paper/sections paper/blog.md`. Grouped the
   edits by paragraph.
2. Read each clean passage beside the matching marked passage, ignoring the `\rv{}` / *[review]* marks. A script
   compared the two number multisets (digits and number words).
3. Re-read each first-pass finding against the new text.
4. Checked blog claims against the clean `paper/sections/*.tex`. Some claims were also checked against data:
   - power sampling against `artifacts/coe/power/p2_*.json` and `p2b_pc_*.json` and their `.args.json` (`ckpt`,
     `--names`, `solved`, per-row `solved`);
   - C4 against `artifacts/coe_paper/c4/ko_s3.json{,.args.json}` and `data/coe_paper/c4_ko_s3.jsonl`;
   - the discussion against `paper/data/a5_waiting.json`.
5. Counted words with `wc -w`. The front matter (the first `---` … `---` block) was removed with an awk filter, which
   gives the same count as `sed 1,4d`.
6. Sanity check: `pdftotext` of the rebuilt `paper/main.pdf` (committed in `40264b03`) contains all three paper fixes.

## Table: one row per changed passage

| # | File (M → C) | Marked text (`11d07d13`) | Clean text (`40264b03`) | Verdict |
|---|---|---|---|---|
| 1 | blog.md, Epistemic status (M16–18 → C11–12) | "The main test was pre-registered, and someone who had not written the experiment's code recounted its numbers from the raw files. Some analyses here were added later and are labelled so." | "The main test was pre-registered, and someone who had not written the code recounted the experiment's numbers from the raw files; later analyses are labelled." | **OK** (blog m3). No numbers. The recount again covers the experiment's numbers, so "the numbers" no longer reads as every number in the post. Supported by `05_results` l.6–7 ("An analyst who had not written the experiment's code recounted the experiment's counts from the raw files"). Not stronger, because "the code" can only mean the experiment's code here. See the note after the findings. |
| 2 | blog.md §2 (M61 → C38–39) | "A proof counts only if Lean, a widely used proof checker, accepts it." | "… and a proof counts only if Lean, a proof checker, accepts it." | **OK.** A length trim, listed in CLEANUP §4. "widely used" describes Lean. It is not a hedge or a reviewed caveat, and removing it strengthens nothing. |
| 3 | blog.md §3 "Checks" (M121–125 → C93–97) | "*[review]* **Checks.** Length limits cut off up to 9% of a run's attempts on the 106; doubling them for ten models after 16 rounds moved each count by at most one theorem and changed no family result, though most cut-off attempts stayed cut off, missing a pre-registered prediction. Independent Lean re-checks accepted every counted proof they examined. A quick syntax filter that runs before Lean rejected no Lean-valid proof among the 210,151 distinct texts it rejected in one knockout run's RL; section 4's million-try samples kept no rejected texts to check." | "**Checks.** Length limits cut off up to 9% of a run's attempts on the 106. Fresh evaluations of ten models after 16 rounds with standard and with doubled limits differed by at most one theorem per model and in no family result, though most cut-off attempts stayed cut off (missing a pre-registered prediction). Independent Lean re-checks accepted every counted proof they examined, and a syntax filter run before Lean rejected no Lean-valid proof among the 210,151 distinct texts it rejected in one knockout run's RL; section 4's million-try samples kept no rejected texts to check." | **OK** (blog m5; "that runs" → "run" is a length trim). Kept: 9 %, 106, ten, 16, one and 210,151; the missed prediction; "one knockout run's RL"; the million-try caveat. Weaker than marked (no causal "moved"). m5 is resolved: both sides of the comparison are named. Sources: `05_results` l.360–363 ("Same-seed re-evaluations of ten r16 checkpoints with standard and doubled caps … differ by at most one strict theorem per checkpoint and in no family verdict; they are independent draws"); App. I C1 table (`11_checks` l.14–28: the largest standard-vs-doubled difference is 1, families identical); `11_checks` l.31–33 ("Most cut attempts do not terminate, and they stay cut at twice the budget"; the five-fold expectation missed on 9 of 10). "Fresh" fits both draws, because C1 (l.10) says the standard-cap read is itself a fresh draw. The filter: §3.8 l.350–358 and C5; `03_setup` l.8 calls it a "syntactic pre-filter". |
| 4 | blog.md §4 certificate (M132–137 → C105–108) | "Only one model had zero successes in 1.5 million tries, enough to certify statistically that its average rate is below what RL's compute could find, but only for plain sampling *[review]* at our usual sampling temperature (at a higher, more random setting, plain sampling did prove the one extra held-out theorem on this model and on one other; we had predicted that at least five of the six models would certify) and one way of counting the budget *[review]* (how many attempts RL's compute is worth; section 5)." | "Only one model had zero successes in 1.5 million tries, enough to certify statistically that its average rate is below what RL's compute could find, but only for plain sampling at our usual temperature and for one way of turning RL's compute into a budget of attempts (section 5): at a higher, more random temperature, plain sampling proved the one extra held-out theorem on this model and on one other. We had predicted at least five of six would certify." | **OK** (blog must-fix 2 and m4; "that … the" is a length trim). The certificate clause matches the marked text word for word again, and the temperature gloss "more random" is back. Kept: both reviewed scopes (plain sampling at the usual temperature; one budget conversion), the missed five-of-six prediction, and one, zero, 1.5 million, five and six. Source: `05_results` l.136–142 and Table `tab:certs`. Seed 0 had 0 successes in 1.50M, with UB95 < 0.05/K; the certificate holds for plain sampling only and is specific to T = 0.8; T = 1.0 proved `la_transfer_916` on this base and on seed 1's. `p2_ko_s{0,1}_plainT1.0.json` confirm that each solve is `la_transfer_916`. |
| 5 | blog.md Fig. 2 alt text (M155 → C126) | "![How likely each model is to write the classical proofs, along RL](figures/blog_fig2_logp.png)" | "![Log-probability of known σ proofs along RL, 12 of 15 runs](figures/blog_fig2_logp.png)". Before this commit: "… of the known σ proofs along RL, for 12 of the 15 runs". | **OK.** A length trim of the alt text from CLEANUP item 13. "12 of 15" is item 13's listed fix. It matches the caption (C128–129, "for 12 of the 15 runs …", which is review item B6) and `05_results` l.203 ("the twelve new ladders"). See minor m3 for CLEANUP's out-of-date quote. |
| 6 | blog.md §6 (M209–210 → C167–169) | "*[review]* But with guided redraws the base proves only 3, 4 and 1 of the 22, 21 and 14 theorems still counted as created at one of section 5's budgets." | "But with guided redraws the base proves only 3, 4 and 1 of the 22, 21 and 14 theorems still counted as created at one of section 5's budgets." | **OK** (blog m1). Matches the marked text word for word. Source: `04_measurement` l.96–97 ("Guided decoding does not recover most of the compute-matched creations: the guided base proves 3/4/1 of the 22/21/14 at K_pub"). |
| 7 | blog.md §7 power sampling (M232–234 → C190–193) | "**A null we can't interpret.** Our implementation of "power sampling", which sharpens the base model without training, found none of RL's new solves. It also did worse than plain sampling on theorems the base solves rarely, so we count it as a failure of our sampler." | "**A null we can't interpret.** Our implementation of "power sampling", which sharpens the base model without training, proved none of RL's new solves (two earlier full runs' bases) or of the 106 held-out classical theorems (two knockout bases). It also did worse than plain sampling on theorems the base solves rarely, so we count it as a failure of our sampler." | **OK** (blog must-fix 1 and m2; CLEANUP item 13). Kept: "Our implementation of", "A null we can't interpret" and "a failure of our sampler". "two" and "106" are item 13's listed addition. Must-fix 1 is resolved: the knockout bases are described by the theorems they were actually sampled on. Source: `05_results` l.333–338: "proved none of the theorems RL r8 proves beyond the base's reach (0/33, 0/27), and none of the 106 strict theorems for knockout bases s0 and s1"; the positive control 0/17 against 6/17 and 13/17; "a null for this sampler". Also App. F. The run arguments agree. Full bases: `ckpts/coe/old/stage1_best12_s{0,1}_b1200.pt` with `--names @data/coe/phase2_cm_ktrain_s{0,1}.txt` (33 and 27 theorems; `solved` 0 at α = 2 and 4). Knockout bases: `ckpts/coe/stage1_ko_s{0,1}.pt` with `--names @data/coe/sigma_heldout_strict.txt` (106 theorems; `solved` 0 at α = 2 and 4). Positive control `p2b_pc_*`, on the earlier full s0 base: power 0/17; plain 6/17 at T 0.8 and 13/17 at T 1.0. |
| 8 | `00_abstract.tex` (M14–15 → C14–15) | "In this organism EI amplified a composition pretraining had exposed, but within 16 rounds did not acquire the classical families without it." | "In this organism, seeds pretrained with the composition acquired classical families, and within 16 rounds of EI seeds without it acquired none." | **OK; see minor m1 (a comma).** From CLEANUP item 4, then paper M1. "In this organism", "within 16 rounds" and the number 16 are kept. The causal "amplified" and the first clean version's "under EI" are gone, so the sentence is weaker than marked and no longer credits EI with the full seeds' families. M1 is resolved. True as stated: the same abstract (l.7–8) gives 6/6 full seeds with a family, the pre-registered contrast and largely present before RL; l.10 gives 3/3 dose seeds, exploratory; and 0/6 knockout seeds by round 16. 250 words. |
| 9 | `07_discussion.tex` (M80–81 → C80–83) | "The knockout fits these results only partly. As there, the base rate predicts which seeds move, and no ladder that started at a pooled rate near `$10^{-6}$` acquired a family." | "The knockout fits these results only partly. As in the required pools, a zero base rate (on the 105 family members) predicted no movement (seeds 0 and 3) and the highest rate the most (seed 1); unlike there, seed 4, with the second-highest rate, never proved a strict training theorem, while seed 2, with the lowest non-zero rate, did. No ladder that started at a pooled rate near `$10^{-6}$` acquired a family." | **OK** (CLEANUP item 9, then both parts of paper M2). `$10^{-6}$` is kept. Weaker than marked, because the counter-example is now stated. The pool is named, as M2 asked. Both "As in" and "unlike there" now point to the required pools, which fits: there, zero-rate bases stayed at 0 of 606 and exactly the four non-zero bases ignited (C63–65). `paper/data/a5_waiting.json` gives these rates on the 105: s0 0; s3 0; s1 5.36e-6 (first strict training success in round 9); s4 2.21e-6 (none); s5 1.41e-6 (round 14); s2 7.47e-7 (round 14). `05_results` l.144–145 and l.194 confirm the 105-member plug-in pool and seed 3's `916` success on the 106. |
| 10 | `11_checks.tex` C4 (M49 → C50) | "Knockout seed 3's base drew 18,432 on `\texttt{916}`." | "Knockout seed 3's base drew 18,432 on `\texttt{916}`, also at batch 1,024." | **OK** (CLEANUP item 8, then paper M3). 18,432 is kept, and 1,024 is item 8's listed fix. `artifacts/coe_paper/c4/ko_s3.json.args.json` has n 18432, batch 1024, T 0.8 and stop_successes 0, for the one theorem `la_transfer_916`. These are the same settings as `ko_s1`'s, so "also" is right. App. I's default "batch 512 … unless stated" (l.3) no longer misdescribes this draw. M3 is resolved. |

## Findings

### Must-fix

None. Every changed passage keeps each number and caveat of its marked passage, apart from listed fixes. Each fixes
the first-pass finding it targets, and each blog claim is supported by the clean paper and, where named, by the run
arguments.

### Minor

**m1. `00_abstract.tex` l.14–15: a garden-path sentence.**
- "… and within 16 rounds of EI seeds without it acquired none" can be parsed as "16 rounds of EI seeds" until the
  verb arrives.
- Fix: put a comma after "EI": "within 16 rounds of EI, seeds without it acquired none". This costs 0 words, and the
  abstract stays at 250.

**m2. CLEANUP §2 item 4's last sentence is no longer accurate.**
- Item 4 was edited in this commit but still ends "The blog's matching sentence is reworded to the same descriptive
  contrast".
- After M1, the abstract's first clause no longer credits EI: "seeds pretrained with the composition acquired
  classical families".
- The blog's short version (C24–25, not changed in this commit) still reads "this form of RL learned classical
  families when pretraining had exposed the move, and did not, within 16 rounds, learn them without it".
- The blog sentence needs no change for accuracy:
  - it is not stronger than the marked one ("this form of RL amplified what pretraining had exposed");
  - in the blog, "learned" refers to the during-RL comparison labelled two sentences earlier. That is five of six, "a
    comparison we chose after seeing the data", plus the dose's three of three, "exploratory".
- But the two sentences are no longer "the same descriptive contrast".
- Fix: reword the CLEANUP sentence, for example: "The blog's matching sentence keeps 'this form of RL learned …',
  which there refers to the labelled during-RL comparison". Alternatively, align the blog, but that sentence is outside
  this pass's changed passages.

**m3. CLEANUP's record of this commit's length trims is incomplete.**
- Item 13 still quotes the Fig. 2 alt text as "… for 12 of the 15 runs". The alt text now reads "… 12 of 15 runs". The
  caption keeps "for 12 of the 15 runs", so B6 still holds.
- §4's trim list was extended for first-pass m10. It names "a widely used", which this commit removed, but not this
  commit's other three trims:
  - the alt text's "the", "for" and "the";
  - "that runs" → "run" (the syntax filter);
  - "We had predicted that at least five of the six" → "We had predicted at least five of six".
- All three remove function words only and change no meaning, so this is bookkeeping.

### Note (no action needed)

- Row 1: the marked wording, "someone who had not written the experiment's code recounted its numbers", would be exact
  and one word shorter than the current wording, if the editor wants a word back.
