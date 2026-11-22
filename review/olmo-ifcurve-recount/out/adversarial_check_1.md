# Adversarial check 1 (read-only sub-agent, 2026-11-22 ≈ 10:00–10:34 UTC, on the first phase-2 draft `a5c5a571`)

33 findings: 10 WRONG, 5 OVERCLAIM, 7 UNCLEAR, 11 MINOR. Verified correct: arm-A pass@k, lengths, §7 emergence table
(48 rows), gaming tables, compute, hygiene, §Compare rows 1–3, 6–8, 10, 12–13, 15, 19–21. [§R] = in the committed
§Recount (addressed in "Corrections to §Recount").

WRONG
1. [§R] "Every split went to a third reader (36)": 39 splits; 3 `ifbench_268` s2300 splits (B7 second reads after
   ADJ4 confirmations) never got a third read; they sit in a 7-of-20 cell where one flip moves F25. → fixed: round C7
   (third reads), two flips to genuine by majority of three, then B9; numbers updated in Corrections.
2. [§R] "executor's labels opened only … after my labels were final": R5 / ADJ4 / B7 came after the first agreement
   table. → disclosure addendum.
3. "47 by a content answer plus one fixed-output copy": `ifbench_64` (`repeat_simple`) is also fixed-output (all 40
   successes the literal sentence). → row 5 / verdict (c): 46 + 2.
4. [§R] "64 draws across dpo, 100, 750, 1100, 1600, 2300" → 56 (16 + 5×8); 72 over all nine checkpoints.
5. [§R] "1–2 each on eight more prompts" → nine.
6. Run doc does not name the DPO repository / size / format ("plus its DPO start (step 0)"). → minor finding (g).
7. "s2300 counts sit at 44 / 40" → 44 / 41 (thresholds 44 / 40).
8. Row 11 "interval rests on the late side's spread" → the early side (16 items, 1 gamed) drives the width.
9. [§R] "late set dominated by the slow prompts' many strict passes" → slow prompts 32 % of late items, 59 % of late
   gamed (recomputed after C7: 30 % / 56 %).
10. hand_report printed 229 rejected proposals (counted policy-string characters); 16 proposals on 15 items; 5 of 6 ADJ4
    rejections against two agreeing reads. → script fixed, text corrected.

OVERCLAIM
11. Expectation 4 at s2300 "holds" / "the only overstatement": 44 sits on the threshold; 43 in r7literal / firstread /
    noR5; needs rules 1–12 for `ifbench_0` and `ifbench_1`. → "not established either way".
12. Genuine pass@1 "≈ 0.45–0.50 from 750 is what both support": the executor's series is 0.410 at 750, 0.505 at 1,100;
    my 20 draws are the first half of its 40 (same draws; executor 5 gamed vs my 2 at s0750). → 0.41–0.51, neither
    claim established.
13. Differences blamed on "labels" partly come from my acceptance policy (10 of 32 deciding disagreements; policy
    written after the ADJ2 proposals). → stated in rows 9 / 17 and finding 5; adjall reported.
14. "selection rules, reader instructions and confirmation rules were fixed in code before any labels": only the
    reader prompt and rules 1–12 were. → disclosure addendum.
15. "pass@8 near the ceiling": 0.885 vs 208 / 218 = 0.954. → Corrections.

UNCLEAR
16. Expectation-9 correction: the run's 14.8 % comes from counting no-`</think>` draws as all-thinking, not from the
    last `</think>`; §2's 109 rows = 70 multi-close + 39 no-close. → Corrections.
17. Variants `adjall` / `noADJ4` / `noR5` have incomplete walks (F1* coded never; "never reached" lines false);
    `noR5` also drops ADJ4. → Corrections.
18. Pre-registered confirmation ("I read every split myself"; cross-checkpoint same-shape audits) not followed: an
    adjudicator with a confidence policy and a mechanical audit of two constraint shapes. → finding 6.
19. "Not supported: nothing … only overstatement (a)" conflicts with rewordings (c) / (d). → verdict aligned.
20. X4 called both "outside the design" and "consistent with the design". → one reading (finding 4).
21. F2 "per cell in the pre-registration": the walk's rule (b) supports the cumulative reading; ambiguous. → row 7,
    finding 1.
22. Disclosure incomplete: 06:38 hand-file headers and line counts, 06:55 two screen.csv rows. → disclosure addendum.

MINOR
23. SE 0.07–0.10 → 0.05–0.10. 24. 0.899 / 0.79 not in out/ → 0.898 / 0.78 (`out/agree_variants.txt`).
25. s1600 arm A 1.245 is below 1.25. 26. 1.53 is arm B vs s0050, arm A max 1.42. 27. Row 16 bounds differ by up to
0.005 (s2300 pass@8). 28. s0500 pass@8 is a scored hit (amendment 5). 29. Expectation 6's rate scope (48 vs F25
prompts). 30. Some numbers not in out/ (overlap, arm-C reproduction, 0 of 336) → `out/misc_facts.txt`.
31. Cross-references (§7 → §6, §8 → §7, "§3"). 32. s0350 refines the P median, not T / N. 33. "readings, thresholds
and expectations were never changed": amendments 1 / 3 / 4 changed which parts could be scored.
