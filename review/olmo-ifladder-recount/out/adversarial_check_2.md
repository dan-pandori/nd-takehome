# Adversarial check 2 (independent read-only subagent, 2026-11-09 23:45 – 2026-11-10 00:14 UTC)

Second pass, on the phase-2 part of the review after the first rewrite (commit `5e5c5ea8`). 21 findings: 4 WRONG,
5 INCONSISTENT, 4 OVERCLAIM, 2 UNTRACEABLE, 6 MINOR. Most numbers traced exactly, including:
- the 706 / 607 / 506 / 101 agreement counts and phase-2 checks [8], [11], [12], [13];
- the 272 / 1,148 reads, 317 / 318 deciding groups and 379 / 397 first-two agreement;
- the cost estimate, the registry and compute numbers.

How each was addressed in the final text:

1. WRONG — `lora_main` 189: only 1/11 is a screen-hidden genuine answer; 2/11 is gamed; 2/4 is genuine in both gates.
   *Fixed.*
2. WRONG — Corrections item 2 quoted text not in §Recount and omitted the S4 `ifbench_4` flip, the "two broken cells"
   statement and the 18 splits. *Fixed (real quote; all listed).*
3. WRONG — Corrections item 1 mixed second-read effects (R4 breaks, S4 share) into the screen item. *Fixed (split into
   items 1 and 2; shares labelled "both changes").*
4. WRONG — the executor's gate scope is "no rung up to and including that one", not "no earlier rung" (136). *Fixed.*
5. INCONSISTENT — §Recount statements left uncorrected (robustness, 35 of 41, 22 of 25, E5's 26, 188's informative
   rung). *Added to Corrections.*
6. INCONSISTENT — "increments within the detection limit" vs +5. *Fixed: +1 / +3 within, +5 just outside.*
7. INCONSISTENT — the adjudication standard was applied selectively: 154 was overturned under rule 7, 179's same
   pattern was not, and rule 3 / rule 7's last sentence point the other way. *Fixed: 154 is shown as a rule-3 vs
   rule-7 call (26 / 15 vs 25 / 16), no adjudication; `hand/confirm_phase2.json` is now labelled a "rule-7 variant".*
8. INCONSISTENT — R4 gamed share under the 154 change is 6/19. *Added (`out/p2_adjusted.txt`).*
9. INCONSISTENT — the moving flags include 188 (DROP60, "neither") and 19 (rung-1 prompt). *Fixed.*
10. OVERCLAIM — only 16 of the 29 screen-released items were read; 13 lie beyond their walks. *Stated, and added to
    Limits.*
11. OVERCLAIM — several sanity genuine labels rest on 3–1 or 2–2 splits. *Stated.*
12. OVERCLAIM — "before comparing" / "blind counts": the changes came after a first comparison draft. *Heading and
    wording fixed.*
13. OVERCLAIM — "measures that noise" → "illustrates". *Fixed.*
14. UNTRACEABLE — the 1.273 / 1.714 / 1.855 ratios. *Added as `rvl_phase2_checks.py` [14].*
15. UNTRACEABLE — 170's olmo-iffu counts. *Added as [15].*
16. MINOR — 188 at rung 3: the executor's screen took 6 of 7; 0/14 is genuine in both gates. *Fixed.*
17. MINOR — the reverse disagreement S3 166 0/5, and the R3 166 break resting on six single reads. *Stated.*
18. MINOR — the single-read S3 206 item decides that cell's flag. *Fixed.*
19. MINOR — "I confirmed none" vs the one item. *Fixed (shown under both rules).*
20. MINOR — 60 descriptions are not found even after normalising (3 more only after). *Fixed.*
21. MINOR — sanity gamed shares under the executor's labels were not printed; the cost of a 48 × 32 re-run changes the
    threshold. *`out/compare.txt` now prints them: numerators match, denominators within 4. Like-for-like 64-draw
    cost added ([10]).*
