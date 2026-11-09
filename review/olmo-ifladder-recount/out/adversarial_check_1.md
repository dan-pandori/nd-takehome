# Adversarial check 1 (independent read-only subagent, 2026-11-09 22:00–22:30 UTC)

Run on the 22:12 UTC draft of `review_olmo-ifladder.md` (§Recount committed `de1ba32e` + the first phase-2 draft
`ef510bcf`). Its findings, as returned (line numbers refer to that draft). How each was addressed is in the review:
§Compare "What changed in my recount before comparing", the rewritten §Compare / §Verdict, and "Corrections to
§Recount".

1. WRONG (most consequential): the mechanical rule-1 screen is not the pre-registered rule. The pre-registration counts
   an answer as one sentence only if there is "no `.`, `!` or `?` followed by more text"; the kit's `one_sentence()`
   required a letter or digit after the mark, so an emoji or HTML tag after a full stop hides the break: 29 of the 50
   "one sentence" labels are multi-sentence answers (`ifbench_67` sanity cells 18, S3 `188` 5, `189` 6). Several meet
   their constraint exactly (Leval_main 189 1/11: 4/8/12/16 words; R3_s2300 188 0/1, 0/10; R3_s2300 189 0/0), each in a
   cell with exactly one reader-genuine answer, so lora_main would elicit 41/48 and rung 3 would not break `s2300` on
   188 / 189. The executor's `gate.py:50` regex has the same blind spot for `.</i>` / `.<br>`. Fix: apply the literal
   rule, send the 29 to readers, restate 188's flag, the R3 sanity count and lora_main's count; flag the executor's
   screen. — *Addressed: screen fixed, 29 items read, all effects restated.*
2. WRONG: attributing the label gap and the 0.21 to rules 7–9 — 87 of the 95 one-way disagreements are the executor's
   readers' labels; the notes cite rule 7 twice and rule 9 never. — *Addressed: gap attributed to the reader pools'
   standard and instructions.*
3. OVERCLAIM: "0.08 under the pre-registered rubric my blind readers used" — the pre-registered procedure gives readers
   only the prompt and has the executor confirm; mine gave readers rules 1–6. — *Addressed.*
4. INCONSISTENT: "the one protocol difference is scope" — also reader instructions, confirmation, adjudication, and the
   sanity second reads (pre-registered for every deciding item). — *Addressed (five differences listed; second reads
   extended).*
5. OVERCLAIM / MISSING: the 166 sanity row rested on single reads; S2 166's walk read all 8 strict successes, so one
   flip breaks it; the executor's reader also said genuine on S4 0/1; the reverse disagreement S3 0/5 was not
   mentioned; Limit 2 too narrow. — *Addressed: all deciding sanity items second-read; row rewritten.*
6. WRONG: sanity row — 19 put on the DROP60 side; "except 166" (166 is DROP60); "thin answers" does not fit 206
   (rule 10) or 0/1/4 (keyword salad). — *Addressed.*
7. WRONG: secret hits are 20 text + 5 token-id hits, not 22 + 3. — *Corrections item 4.*
8. WRONG: 35 hints, not 36. — *Corrections item 5.*
9. WRONG (sign): `lora_ctrl` held-out NLL rises 0.7 %. — *Corrections item 6.*
10. INCONSISTENT: "same verdicts after the 154 adjudication (`out/expect.md`)" — expect.md is the blind table; E12
    differs. — *Addressed.*
11. OVERCLAIM: "differs on 10 cells, all vacuous" — some are reader-gamed. — *Corrections item 1.*
12. UNTRACEABLE: `phase2_checks.txt` [8] not printed by any script. — *Addressed (items 7–13 added to the script).*
13. UNTRACEABLE: losses, same-prompt token ratios, 537 MB, stage-0 dollars, 23:53:57, 02:07:50, the ≈ $13 estimate.
    — *Addressed (`rvl_train.py` [4], `rvl_phase2_checks.py` [9]–[10], `rvl_facts.py`).*
14. MISSING: the pre-registered detection limit (≤ 4 elicited prompts are not findings) is never applied; +1 and +3
    are within it; rung 2 re-elicits only 11–12 of rung 1's 16. — *Addressed.*
15. MISSING: "Rung 2 re-elicits 11 of rung 1's 16" depends on R2 179. — *Addressed (row added).*
16. MISSING: 170's DROP60 membership is in the same position as 284's. — *Addressed.*
17. OVERCLAIM: "The run did what it pre-registered"; "no weights in the bucket" (adapters are weights); "far outside
    anything a reseed is likely to close". — *Addressed.*
18. MINOR: lower bounds are 2–4 genuine (p 0.060 at 4 vs 0); 8 + 58 + 58 + 58 order; 13 slots from 10 prompts; 3 copies
    across 2 prompts; six of seven "neither" prompts label-robust; +1.1 pp vs −3.1 pp against my own R1; name the
    thinking-mean convention; neither 154 reader cited rule 3; "the control the executor names" is my design; compute
    flags omit training seconds (1.37×) and check jobs; the 95 by binding id; 60 of 152 descriptions not verbatim;
    numbers.md's "olmo-transplant's 10 calibration prompts". — *Addressed in Corrections / §Compare.*
19. MINOR: 188's slot-1 exemplar has no sentence punctuation and `dpo`'s four rung-4 answers copy that format.
    — *Added to "Not mentioned".*

Process note from the checker: it ran `python3 -c "import rvl_facts"`, which re-executed the script and rewrote
`out/facts.txt` with byte-identical content.
