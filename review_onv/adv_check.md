# Adversarial check of review_olmo-novelty.md: §Fresh search, §Compare (phase 2), §Verdict

Scope: lines 160–375 of `/home/dan/work/olmo-novelty/review_olmo-novelty.md` (commit 4263c2af, 15:26:57 UTC).
Evidence is local only. I re-ran `review_onv/phase2_checks.py` (6 s) and `fresh_check.py`, and read `corr_out.json`,
olmo32/olmo_ifomega/olmo_iffu files, the ledgers and sources, and the three agents' transcripts
(`~/.claude/projects/-home-dan-work-olmo-novelty/75c3e162-…/subagents/agent-{a85a1d79 RA, add2b29d RB, a4ceae50 RC}.jsonl`).

## Findings (most consequential first)

1. **"results returned 15:15–15:33 UTC"** (§Fresh search heading): WRONG. The agents' last replies are at 15:15:27 (RC),
   15:19:14 (RA) and 15:20:49 (RB). The section was committed at 15:26:57, so "15:33" is a time after the commit.
   Fix: "15:15–15:21 UTC".
2. **"42 is the olmo-ifomega executor's set (`verdict.csv`; the hint test is on 42)"** (Compare 6): WRONG. The hint
   test's 42 IFBench prompts (`olmo_iffu/problems_hint.jsonl` + `problems_hint2c.jsonl`; iffu README: "from the 42
   left after excluding `ifbench_281`") are the reviewer's 43 minus ifbench_281. They share 39 prompts with
   verdict.csv's 42: only verdict.csv has 49, 214 and 281; only the hint set has 166, 226 and 252. So there are three
   sets, not two, and REVIEW's "12 of 42" is not on verdict.csv's 42. The same problem affects Next measurement 2:
   "the 33 hand-reach prompts never tested at 1,024" counts within the 43. On verdict.csv's 42 the figure is 34,
   because test 3 included 166 and 252. Fix: name all three sets.
3. **'So "RL barely moves it" …'** (Compare 2): WRONG attribution. The phrase is not in the brief, the claims sheet,
   REVIEW, the run summary, numbers.md or log.md. It is the reviewer's own wording in `review_onv/fresh/SHARED.md`
   ("RL barely moves maths."). Fix: quote C2's actual text, "pass@1 0.716 → 0.746".
4. **"smaller than the lab's gain"** (Compare 2) and **Next measurement 3** ("re-grade … grader, sampling or
   problem-set"): OVERCLAIM and incomplete. The same `olmo32/results.csv` also stores a final-answer grade
   (`succ_fixed_final`). Under that grade, AIME 2025 goes 0.667 → 0.738 (+7.1), about the lab's +7.4; AIME 2026 goes
   0.707 → 0.741 (+3.4). Most of the +4.6 vs +7.4 gap therefore comes from RL's checker: on AIME 2025 it credits
   `dpo` 0.696, against 0.667 under the final-answer grade. Re-grading cannot test sampling: ours is T 1 / top-p 1
   (numbers.md:1906), the lab's T 0.6 / top-p 0.95. The AIME 2025 problems are the same 30 in both, none excluded.
   Fix: add the final-grade split; reword Next measurement 3 to say the grader question is largely answered and
   sampling needs pods.
5. **"Zhai 2604.14877 is the only per-problem non-maths RL-only count"** (C3 row): WRONG, passed on from RA without
   correction. RA's own row 7 is a counterexample: What Outcome RL Buys checks 144 physics RL-only problems [IL-99].
   Yoon's Fail→Pass prompts [IF-60] are another, per prompt on IF at k ≈ 1. The reviewer corrected RA on HiR but
   not here. Fix: correct it, or attribute it as "the only one RA found".
6. **C1 row "RC: no large-k per-problem test of this model pair"**: UNCLEAR (omission). RC's reply states
   "Verdict: novel." The table never reports that verdict. Fix: give RC's label and say why the pre-registered
   definition keeps "replicates".
7. **"knocked down no 'novel' label"** (Verdict) and **"The fresh search (RB) agrees"** (Compare 1): OVERCLAIM. RB's
   top line is "Only C6 looks new …; C4 and C7 extend earlier results". RB labels C4 "extends" and calls only the
   reach-boundary measurement new. RB also never found Wei. Fix: "RB labels C4 'extends'; its narrow form survives".
8. **"fixed there but not in §4"** (Compare 3): UNCLEAR (incomplete). C5 is still ranked "replicates" wholesale in
   five places: §4, Table B C5 (REVIEW:94, citing IF-22 and NV-13 as "replicate"), §7's L-6 gloss (REVIEW:229),
   STATUS.md:390–391, and run_olmo_novelty.md ("C5 and C8's test 1 replicate finishing"). Fix: list all five places.
9. **"RA wrongly listed HiR as having no large-k analysis"** (C3 row): true but not traceable. RA's reply says
   "None has a large-k analysis: HiR 2512.23457 …", and HiR Fig. 3a does plot IFBench pass@k at k = 1…1,024. But
   RA.tsv has no HiR row, so the committed record cannot show RA's claim. Fix: cite RA's reply.
10. **"Pass 2 (part 2, #18) only noted …"** (Compare 1): WRONG detail. Pass 2 #1 (`_claim_check2.md:57`) also cites
    Wei's 73.5 % as an existing IF gaming audit, and pass 1 #34 labelled the number. "Neither asked for it in the
    bottom line" is still true. Fix: "#1 and #18 cite it; neither asks for it in the bottom line".
11. **"numbers.md should say 24"**: UNCLEAR. All 25 NV sources are distinct additions to the screen (175 → 200; none
    appears in another screen file), and one of them is prior (2312.01552). So "25 of them" is right if "them" means
    the 200 screened, and 24 if it means the 176 new. Fix: "25 of the 200 (24 new)".
12. **"Independent code and a real-draw split … point estimates within 0.003"** (Verdict): UNCLEAR. The real split
    gives −0.503 / −0.523, and −0.523 is 0.019 from −0.504. Fix: state the two checks separately.
13. Minor points (all NIT):
    - (a) "bootstrap noise" for IFEval per type: the executor's upper bound is −0.082. The reviewer's own code gives
      −0.018 to −0.059 over six seeds (12–17), so −0.082 is just outside that range.
    - (b) "the scoring of every pre-registered expectation" stands: the run summary's L-5 does not (Compare 5).
    - (c) "464 / 465 sampled quotes": these are all the quotes citing the 14 re-fetched sources, not a sample.
    - (d) "Matrix A names every … size": Yue's row gives no size.
    - (e) "≤ 700 words each": holds only without front matter; by `wc -w`, 7 of the 20 notes have 705–709 words.
    - (f) "'the first large-k IF comparison'" is RA's phrase; no run text claims it.
    - (g) "the brief's claims": SHARED.md uses the claims-sheet wording (3 × 10⁻³, 36 %, ~11, 42–43) plus glosses.
    - (h) The Verdict's minor list drops Compare 7's sentence on ProRL's R².
    - (i) "−0.769 with one type per prompt" is not produced by the committed code. It does reproduce (−0.769, 47
      types).

## Verified OK (selected)

- **Olmo 3 report and AIME split.** Table 14 (SFT 66.2, DPO 70.7, 3.0 72.5, 3.1 78.1 on AIME 2025; AIME 2024 76.0 →
  80.6; +7.4 and +4.6) matches. The `rl`-grade per-year split matches: 0.696 → 0.742 and 0.737 → 0.750 (29 problems
  for 2026), and 0.716 → 0.746 overall.
- **Wei and the bottom line.** Wei's App. C.2 quotes (73.5 %; 4.5 % → 40.1 %) are in the source, on the same page.
  Bottom line 1 cites Wei only through IF-47, and the 73.5 % appears only in Table B and §6.
- **Write-up claims.** §4 does rank C5 "replicates" wholesale. L-5 is "partly held" in REVIEW §7, the log and STATUS,
  but "failed" in the run summary. The olmo-ifomega review's 43 (40 shared) and test 4 on 43 check out, as does
  33 = 43 − 10.
- **Errata and other checks.** Erratum R1 holds: two `-X POST` calls, both Semantic Scholar batch queries. Erratum
  R5 holds: dice sits in Fig. 4's "Sustained" row, and IL-32 is Table 15. The crossovers note cites IL ids only (36
  bracketed citations). QUESTIONS.md is unchanged by the run.
- **Numbers table.** Every row matches `corr_out.json`, the phase-2 output and numbers.md, including the loose-credit
  counts, the gain bins and shares, ρ(x, RL), 2.97 s per draw, K ≈ 7.8 × 10⁵ and 5,442 / 4,448 tokens.
  `compute_table.csv` matches: row 28 is 1.4 × 10⁵ GPU-h, and the Matrix A shares (Yue 7.12e-6…3.03e-2, own runs
  ≤ 2.0e-4; ProRL; Olmo 3 7B; DAPO; Olmo 3 32B) all agree. There are 46 `step_*` branches.
- **Fresh-search rows.** 54 rows, 54 / 54 quotes found, 0 / 54 altered-quote controls passing, maximum 25 words.
  31 distinct ids, 27 of them screened by the run. The 4 unscreened ids and the AceReason 1.1 figures (8.3 % → 1.2 %,
  +5 % on LiveCodeBench v6) match. 2610.20639's date (2 Oct) and 82 % match. The agents stayed blind: none of
  their tool calls touched the run's files.
- **Counts and quotes.** 74 cited ledger ids; 3,000 / 2,834 words; "No KL loss" is in the source; 2611.02574 is dated
  2 Nov 2026.

## Tally

I checked about 230 statements, counting table numbers individually. 21 are flagged:
- WRONG: 5 (#1, #2, #3, #5, #10);
- OVERCLAIM: 2 (#4, #7);
- UNCLEAR: 5 (#6, #8, #9, #11, #12);
- NIT: 9 (#13a–i).

About 209 statements were OK.
