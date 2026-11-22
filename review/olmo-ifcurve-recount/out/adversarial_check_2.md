# Adversarial check 2 (read-only sub-agent, 2026-11-22 ≈ 10:48–11:14 UTC, on the revision `da88b6a6`)

20 findings: 5 WRONG, 3 OVERCLAIM, 5 UNCLEAR, 7 MINOR. Verified: §Recount byte-identical to `7c23ec4b` apart from the
inserted addendum; disclosure line counts; §Compare rows 1–3, 5–7, 10–13, 15–16, 18–21; most Corrections bullets.
Of the 33 first-pass findings, 24 were fixed correctly and 9 only partly (see items below). Disposition in the final
text (`review_olmo-ifcurve.md`):

WRONG
1. The C7 / B9 corrections applied the acceptance policy in one direction only: two ADJ4 low-confidence "genuine"
   confirmations on `ifbench_268` s2300 (3,3) / (4,1) had two agreeing gamed reads after B9 → `rvc_policy.py` drops
   them; C7 and B9 cancel; committed §Recount values stand (reading 2 7 / 25 / 16, agreement 0.917, 32 of 566).
2. A 40th split (B_s2300 ifbench_268 5,3) had no third read → round C8 (gamed; a high-confidence rule-12 confirmation
   stands); "40 third reads, one per split".
3. Finding 4's timeline: X4 was decided at 02:27 before any s1600 extension item was read (executor's first extension
   reads 04:32) → X4 follows the placement rule for the executor's moved F1; §7 correction added.
4. "0.932 on its reader labels" was 0.930 after C7 → after the consistency pass it is 0.932 again.
5. Amendments that changed scoring are 1, 3, 4 and 5 (s0350 intervals; reading 2's grid) → fixed.

OVERCLAIM
6. Verdict (d) "no detectable trend at 40 labels" (executor's labels 0.410 → 0.505) → "label-dependent; no plateau
   onset established".
7. "independent blinded gate" → qualified (reads independent; confirmations qualified).
8. "variant runs bound their effect" → cites `out/phase2_exec.txt`; variants called approximate.

UNCLEAR
9. Disclosure missed 06:39 (arm-C ordering chosen by matching the executor's key) and 06:41 (reader_task.sh, batch
   ids, item c000216) → added; §6 correction added.
10. C7 / B9 were done after reading the run documents, triggered by the adversarial check → stated.
11. Expectation 9 "holds" is a definitional call (14.7–14.8 % with no-`</think>` draws as all-thinking; 15.2 %
    without) → reworded; verdict (h).
12. s0350 refines the P median, not the 500–750 gap; with s0350, five more prompts would be gradual (12 / 32) → row 8,
    verdict (f), next measurement.
13. `ifbench_189` is reached only under the rule-7 "in substance" reading → row 5, verdict (c).

MINOR
14. Numbers not in out/ (1,391; ifbench_64's 40; "10 prompts"; "18 among 46"; "15 distinct") → `rvc_phase2_verify.py`,
    `rvc_hand_report.py` fixed and re-run.
15. Superseded §Recount numbers (§8 s2300 arm-B 69 → 68 / 188; secondary 0.336 → 0.334) → Corrections.
16. 1.25× flag also covers s0750 (1.251) and arm B; "1.25–1.53×" is in §13 → finding 2, verdict (e), Corrections.
17. Pending walks also code F2 / F25 as never; `adjall` picked up policy-string characters → `rvc_readings.py` fixed;
    Corrections.
18. Rule 14's changes are not itemised in the addendum (confirmations cite "rule 7;13") → finding 3.
19. The run doc's "the rest held" includes expectation 4's s0100 part (holds on base draws only) → "Expectations".
20. README cited a missing `out/adversarial_check_2.md` → this file.
