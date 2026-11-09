# Second-pass claim check: olmo-ifladder write-up, plain summary, `numbers.md` section

Adversarial re-check, 2026-11-09 (after commit `f42ca7a0`). Targets: `run_olmo_ifladder.md`,
`olmo_ifladder/plain_summary.md`, and `numbers.md` from "## olmo-ifladder (2026-11-09, executor; UNREVIEWED)" to the end
of the file (lines 2300–2443). None of the three changed during the check.

**How I checked.** I diffed every target against `6a1fd0ee`, the version the first two checks quoted. Every new or
reworded sentence and every number shared between files was recomputed from raw files:
- the graded and sample files of all 13 jobs (thinking tokens from `ids`);
- the 13 job metas and both LoRA reports;
- `handcheck.csv`, also as it stood at `b9d9c5d7`;
- olmo-iffu's T2 / T2c grades, samples and `handcheck.csv`;
- olmo-ifomega's F- and C-phase `s2300` / `dpo` grades;
- `prompts.csv`, `lengths.csv`, `train_manifest.csv`, `exemplars.csv`, `artifacts/MANIFEST.jsonl` and the local registry
  file.

Cell states come from my own import of `gate.walk` over the 8 gated jobs. They match `gate_status.csv` on all 189 cells
(0 differences). No tracked file was changed, and no pipeline script was run.

**Word counts.**
- `run_olmo_ifladder.md` without the figure line: **400** whitespace-split words (limit 400).
- `plain_summary.md`: **500** (`wc -w`; limit 500).

Both are met exactly, so every fix below is word-neutral for those two files.

**Result: 5 problems, all imprecise.** None is an error or an overstatement. Two are in `numbers.md` and three in the
write-up; the plain summary has none. All 12 counted findings of the numbers check and all 26 of the write-up check are
fixed. Two of those fixes introduced new imprecisions, P1 and P5 below.

## Problems

### P1 — `numbers.md`, `s2300` sanity paragraph (and expectation 12) — imprecise

> "Outside the gated prompts a cell is decided without reading only when `s2300` has < 2 strict successes: rung 2 on 19
> (0 of 16; rung-1-elicited) is a certain break, the other 16 / 4 / 2 non-`DROP60` cells there were not read"

Expectation 12 repeats the count: "16 / 4 / 2 non-`DROP60` cells outside the gate unread".

**What the data show** (`gate.walk`):
- Outside the gated scope there are 17 / 5 / 3 reach cells at R2 / R3 / R4, all of them non-`DROP60`.
- Two of them have ≥ 2 strict successes and were decided ("elicited", not a break) without any `s2300` read, by
  identity inheritance from read `dpo` answers:
  - **ifbench_64 at R3**: 5 strict, 5 inherited genuine.
  - **ifbench_280 at R4**: 16 strict, 16 inherited genuine.
- These are the two cells the first check's I3 flagged.
- So "decided without reading only when < 2 strict successes" is false for them. "The other 4 / 2" also silently drops
  them: there are 5 and 3 non-`DROP60` cells outside the gate.
- The 16 / 4 / 2 count is right as *undecided* cells (`summary.json` → `sanity.*.outside_scope_non_drop60_undecided`).
- No conclusion changes, because neither cell is a break.

**Fair wording:** "Outside the gated prompts no `s2300` answer was hand-read: rung 2 on 19 (0 strict of 16) is a
certain break; 64 (R3) and 280 (R4) are not breaks, by identity with read `dpo` answers; the other 16 / 4 / 2
non-`DROP60` cells are undecided." In expectation 12, write "undecided" instead of "unread".

### P2 — `numbers.md`, same paragraph — imprecise

> "206 is a break at rungs 3–4 under rule 10 (its first readers had 2 and 4 genuine run-on rewrites)."

**At R3 only one of the two genuine labels was a run-on.** In `handcheck.csv` at `b9d9c5d7` (before rule 10),
`R3_s2300` ifbench_206 had 2 genuine labels:
- **0.7**: "PCBMTL handles scarce sample counts Learning segmentation enhances …". This is an unpunctuated run-on,
  re-confirmed gamed under rule 10.
- **0.12**: "This method tackles sparse samples. Segmentation helps attribute learning. Loss aids imbalance. This beats
  existing approaches." This is punctuated and is still genuine.

The R3 cell breaks because rule 10 flipped 0.7 and the extra read 0.15 was gamed, leaving 1 genuine of 13.

At R4 the claim holds: the four first genuine labels (0.0–0.3) were all run-ons, and rule 10 flipped all four.

**Fair wording:** "(before rule 10 these cells had 2 and 4 genuine labels; rule 10 re-labelled the run-on rewrites
among them as gamed, 1 of 2 at rung 3 and 4 of 4 at rung 4, and later reads found no second genuine answer)".

### P3 — `run_olmo_ifladder.md`, finding 3 — imprecise (minor)

> "Gamed share 0.21 (`dpo`, rung 1: 0.13)"

The comparison mixes two estimators:
- `lora_main`'s 35 / 164 uses this run's estimator. It includes the mechanical rule-1 pre-screen: 4 of the 35 gamed
  labels among the first ≤ 4 are `gate.mech` labels.
- The same estimator applied to rung 1 gives **7 / 48 = 0.15**, which `numbers.md` now prints next to olmo-iffu's
  readers-only 6 / 48 = 0.13.
- Pairing 0.21 with 0.13 widens the apparent increase from about 6 pp to 8 pp.

**Word-neutral fix:** "(`dpo`, rung 1: 0.15)", or "0.13–0.15".

### P4 — `run_olmo_ifladder.md`, caveats — imprecise (minor)

> "`lora_main` used 1.41× its training tokens and generated 1.71× (flagged)."

- **The pronoun is wrong.** With `lora_main` as the subject, "its" refers to `lora_main` itself. The sentence then says
  it used 1.41× its own training tokens. The intended referent is the control: 332,936 / 235,880 = 1.41× training
  tokens, and 26,094,259 / 15,219,635 = 1.71× generated tokens.
- **Two flagged ratios are missing.** The other two ratios above the 1.25× flag go unmentioned: 1.27× training
  GPU-time (421.9 / 331.4 s) and 1.85× check + evaluation GPU-hours. "(flagged)" therefore reads as if only these two
  were flagged.

**Word-neutral fix (10 words):** "`lora_main` trained on 1.41× the control's tokens, generated 1.71× (flagged)."
Optionally add "(also 1.27× / 1.85× GPU-time)" if words allow.

### P5 — `run_olmo_ifladder.md`, deviations — imprecise

> "`s2300` sanity arm restored (read only where it decides a reading)"

The sanity arm never decides a reading:
- `analyze.py` derives every reading from the `dpo` rung cells and the two LoRA cells.
- `s2300` breaks only set the flag that a `dpo` failure at that rung is uninformative. The pre-registration says "a
  `dpo` failure at a rung that breaks `s2300` is reported as uninformative". Its deviation 1 says the arm "decides
  whether a failed rung is informative".
- The actual restriction was hand reads only on the prompts that no rung up to that one had elicited
  (`pids_sanity_r{2,3,4}.txt`, 31 / 26 / 23).

**Word-neutral fix (7 words in the parenthesis):** "(read only on prompts no rung had elicited)".

## Earlier findings: status

### `claim_check_numbers.md` (4 errors, 8 imprecise): all 12 fixed

| finding | status | how established |
|---|---|---|
| E1 stage 0 | **fixed** | 2.28 M / 4,905 / 0.45 h: 2,276,031 tokens / 464 draws; 1,623.4 s |
| E2 sanity GPU-h | **fixed** | 2.22 (7,996.8 s) |
| E3 total | **fixed** | 16.86 job GPU-hours (60,697.8 s from the 13 metas + 2 LoRA reports). The rows sum to 16.87, as the new parenthesis says. |
| E4 rung-1 gamed share | **fixed** | Both values shown; 7 / 48 = 0.146, +10.8 pp. See the note on E4 below the table. |
| I1 | **fixed** | 1.85× (16,975 / 9,152 s = 1.855) |
| I2 | **fixed** | 6,795 / 3,963 |
| I3 | **fixed** | 46 / 99 = 0.46 and 37 / 92 = 0.40, recomputed with `gate.walk` on the scope files; equal to `summary.json` → `sanity.*.gamed_share_first4_gated` |
| I4 | **fixed** | "not determined (R2 at the bound)": R2 ≥ 3 with 19 (0 / 16 strict). The 16 / 4 / 2 match `summary.json`; see P1 for the wording. |
| I5 | **fixed** | "Neither retraining fallback triggered (NLL drop 15.1 % ≥ 2 %; check calibration 0.963 / 0.894 ≥ 0.5 × 0.906); the merge-check fallback did" |
| I6 | **fixed** | 6,985.4 vs 3,613.3 mean thinking tokens on the reach evaluation (3,070 / 3,069 of 3,072 draws reach `</think>`) = 1.93×. The 3.2× is 6,236 / 1,963 = 3.18. |
| I7 (290 strict) | **fixed and settled** | See the t290 details below the table. |
| I8 | **fixed** | Header "(LoRAs 64 / prompt, `dpo` 16)": 624 / 640, 573 / 640 vs F_dpo 145 / 160 |

**E4.** The first check said 6 / 48 "cannot be reproduced", and that was too strong.
- olmo-iffu read at most 3 strict successes in 10 of the 19 cells. Its first four *labelled* items per cell give
  exactly 6 / 48. For ifbench_78 these are strict successes 1, 2, 3 and 5.
- So "6 / 48 = 0.13 (olmo-iffu)" and "+12.9 pp" are correct as labelled.
- Also, E4's readers-only "+12.6 pp" is really +12.7 (15 / 59 − 6 / 47 = 0.1266). That number appears in no target.

**I7 (the t290 round).** Round t290 read 8 items and gave 2 of them second reads.
- 3 genuine title-case answers: 1.4, 1.12 and 2.4, with upper-case letter shares 0.24 / 0.35 / 0.44.
- The strict-reading deciding items, 1.4 and 1.12, both have a second genuine read.
- 3 more ALL-CAPS answers were overturned to genuine on the primary reading, and 2 are gamed.
- `gate_status` therefore now shows R2_dpo 290 as 12 read: 10 genuine, 2 gamed.
- The rung-1 genuine answers are ALL CAPS (shares 0.91 / 1.00). "15 / 2 / 5 / 3, still 25" holds.

**Unverifiable and note items:**
- **U4 resolved.** `artifacts/MANIFEST.jsonl` is committed (`f42ca7a0`) with 28 `artifacts/olmo_ifladder/` rows: 13
  samples, 13 graded, 2 adapters. Bytes and sha256 match the local files for all 28.
- **U1.** The local registry file has 103 rows. U1–U3 remain unverifiable bucket-side or process-side offline.
- **N2.** Now stated, but with the P2 slip.
- **N4.** Now stated ("0.777 (8 prompts)").

### `claim_check_writeup.md` (1 error, 5 overstatements, 20 imprecise): all 26 fixed

**Write-up** (1 overstatement, 7 imprecisions):
- "What transfers is how RL answers" now reads "also takes on RL's lengths", with "Causality of the lengths is untested".
- The statistic is named ("median per-prompt thinking").
- "The rest fell in range" now reads "Undetermined: … (≥ 3 at rung 2, the bound)".
- The deviations now include the narrower sanity gate and rules 10–12; P5 is about the new wording.
- The 290 caveat is stated ("290 at rung 2 if ALL CAPS ≠ title case"), now settled.
- The caveat gives the 1.41× training tokens; P4 is about the wording.
- Fisher "estimated counts".
- "binding constraint type": 21 of 25 / 19 of 23 recounted from `train_manifest.csv` ids.

**Plain summary** (4 overstatements, 7 imprecisions), all reworded correctly:
- "Did not manage in 256 ordinary tries": `dpo`'s 256 are unhinted extension draws.
- Step 2 is no longer quoted.
- "Two example answers by the RL model to similar prompts".
- The cut-2 scope "(steps 3–4 only where earlier steps failed)".
- "Checked passing answers until two real ones were found", and the "one-word answers" gaming example is gone.
- "On a typical prompt … about three times as long": 3.40× median of medians, 2.89× median of per-prompt ratios.
- "As high as `dpo`'s on average": 0.975 vs 0.906.
- "Nothing we tried reached seven prompts".
- "On two of them (equal and growing sentences)": 166 and 188 break `s2300` at rungs 1–4.
- Habits "suggest", and knowledge transfer is called untested.
- "34 % vs 66 %": 1,052 / 3,072 = 34.2 % and F_s2300 254 / 384 = 66.1 %. `s2300`'s fresh C1 confirmation draws give
  the same 550 / 832 = 66.1 %, so selection does not inflate the 66 %.
- "Held-out likelihoods barely moved" (+0.7 % / +1.4 %).

**README** (1 error, 6 imprecisions), checked although it is outside the three targets:
- Rules 7–9 vs 10–12.
- Label origins 13 / 32 training trajectories and 23 / 116 exemplars (recounted from `label_src`).
- The table command's output argument.
- `../` paths.
- Merged weights "not kept … deleted on the pod".
- `order_r2.txt` listed.
- VPS-side `launch.sh`.
- matplotlib.

## Notes (not counted)

- **290 in the plain summary.** It still says "16 with the 60-word line", the primary reading. On the strict reading
  the split is 15 / 2 / 5 / 3, with the same 25 in total. The write-up states it, which is acceptable for the
  non-specialist text.
- **Expectation 12 at R3.** R3 is also formally open: ≥ 2 known breaks plus 4 undecided cells could exceed ≤ 5. That
  would need all four unread cells to break, and they have 16, 13, 11 and 16 strict successes of 16, so it is
  implausible. "(R2 at the bound)" is a fair summary.
- **"Its median per prompt 3.2×"** (`numbers.md` compute) is the ratio of medians of prompt medians. The median of
  per-prompt `lora_main` / `lora_ctrl` ratios is 2.8×. This is acceptable as worded.
- **Rules 10–12 in the write-up.** The write-up's deviation gives only their timing. It does not say that they changed
  5 labels, including one `lora_main` deciding item (gb2a9b9 on 206). No reading changed, and `numbers.md` says so.
- **Figure.** It prints only "2+" for elicited cells, so 290's `g_R2` change from 4 to 10 leaves the committed PNG
  correct.

## Verified correct (new or reworded text, and every number shared between files)

- **Hand gate (`numbers.md` header).**
  - `handcheck.csv` has 706 items and 24 overturned: 18 where every reader was overruled, 6 where the first reader was.
  - 251 items were read twice, with 14 splits.
  - Every row has a `my_note` and a final label.
  - Every read deciding item of the 123 elicited cells has 2 readers.
- **Sanity arm.**
  - Gated scopes 31 / 26 / 23; break lists as given; non-`DROP60` 2 / 2 / 1.
  - Rung 2's 48 / 111 is entirely in scope.
  - 19 at R2 has 0 / 16 strict and is rung-1-elicited.
  - `DROP60` = 0 1 3 4 166 170 188 284, so 40 prompts are non-`DROP60`.
  - Expectation 8: +12.9 / +10.8 pp.
- **Lengths** (median of per-prompt medians):
  - Thinking 6,236.25 / 1,833.5 / 5,741.5 tokens; `lora_ctrl` 1,962.75 (+7 %); `lora_main` +240 %.
  - Answer words 69.5 / 231 / 31.5; `lora_ctrl` 235.25.
- **Gaming.** `lora_main` 35 / 164 = 0.21. A pass-weighted estimate (each cell's gamed share × its strict count) gives
  223 of 1,052 = 0.212, so "about one pass in five" holds on either estimator.
- **Readings.**
  - 16 / 1 / 5 / 3 / 16 / 0 / 7; Fisher p < 0.05 on 12 of the 16; 40 / 0 of 48; 24 / 16 split.
  - The four 1,024-survivors: all elicited by `lora_main`, none by `lora_ctrl`.
  - The seven holdouts' rule types match their prompts:
    - e3478: "a" fewer than 2 times;
    - 268: three vowel types;
    - 67: an emoji per sentence;
    - 166: equal character counts;
    - 188: +n words per sentence;
    - 284: span copy;
    - 3: keyword counts.
  - `s2300` breaks: 3 at rungs 1–3, 166 / 188 at rungs 1–4, 284 at rung 1.
  - `lora_main` has 1 genuine of 64 on e3478 and on 166.
- **Calibration** (recomputed from grades): 0.777 (8 prompts) / 0.850 / 0.861 / 0.847; LoRAs 0.975 / 0.895; `dpo`
  0.906.
- **Compute** (all rows recomputed from the metas): 19,456 draws; 100,591,013 tokens; 1.71× / 1.85× / 1.41× / 1.27×;
  training 568,816 tokens.
- **Ladder table.** Cells with a strict success 21 / 9 / 8; draws 3,712 / 2,624 / 2,304.
- **Cross-file agreement.** The same values appear in all three files where they are repeated:
  - 25 / 40 / 16 / 7 of 48; 19 of 23;
  - 6,236 / 1,834 / 5,742 and 70 / 231 / 32;
  - 0.21; 0.975 (0.906); 1.41× / 1.71×; 1.12 %;
  - +240 %; 256 / 64 / 1,024 draws; 19,456; $61.85 of $80.

  The only exception is P3's 0.13, where `numbers.md` also gives 0.15.

## Resolution (executor, 2026-11-09, before publication)

P1 and P2 reworded in `numbers.md` as suggested (64 / 280 decided by identity outside the gate; "undecided" in
expectation 12; rule 10 re-labelled 1 of 2 and 4 of 4). P3: the write-up compares with rung 1's 0.15 (this run's
estimator). P4: "trained on 1.41× the control's tokens". P5: "read only on prompts no rung had elicited". The write-up
stays at 400 words.
