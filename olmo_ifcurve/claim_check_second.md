# Second-pass claim check: olmo-ifcurve write-ups (after the first pass's fixes)

Checked 2026-11-22 against commit d0156a22. Documents: `run_olmo_ifcurve.md` (run doc), `olmo_ifcurve/plain_summary.md`
(plain), `numbers.md` § olmo-ifcurve (numbers). Sources: summary.json, passk.csv, emergence.csv, gaming.csv, lengths.csv,
results.csv, compute.csv, gate_summary.json, handcheck.csv, `hand.Labels()` / `hand.needed()` / `hand.armc_sample()` on
the local row caches, `~/podhours.log` and the pre-registration with amendments 1–5. Every number was recomputed in
python at full precision.

**Result: 7 findings.** Two were introduced or kept by the rewrite in the run doc (1, 2). Two are first-pass findings
that were only partly fixed (3, 4). One is a pre-existing error the first pass missed (5). Two are minor wording or
rounding issues (6, 7). No reading changes.

## Findings

**1. Count of labelled late reach wins misstated (run doc; new wording for first-pass finding 7).**
- Quote: "On the reach prompts it **grows**: 0.06 of 16 early wins vs 0.31 of 536 late wins labelled."
- Files (`results.csv`, arm B late cells 1,100 / 1,600 / 2,300):
  - 2,504 strict successes, of which **1,096 carry labels** (432 gamed, share 0.394).
  - 536 is the subset of first ≤ 4 strict successes per cell (`gaming.csv` 170 + 178 + 188; 164 gamed = 0.306). This
    is the pre-registered secondary measure.
- "536 late wins labelled" therefore gives the wrong labelled count. It also invites reading 0.31 as the share among all
  labelled late wins, which is 0.39. (The early side is right: all 16 early strict successes are labelled.)
- Fix: "…vs 0.31 of the first ≤ 4 wins per late cell (536 of 2,504 late wins)".

**2. Expectations line drops "≥ 1 / ≥ 2", so a held part reads as a miss (run doc; first-pass findings 10 and 12 not
fully fixed).**
- Quote: "Missed: … step-2,300 genuine on ≥ 44 / ≥ 40 prompts (40 / 36), cap share at 1,600 (0.63 %). The rest held."
- Pre-registration, expectation 4: "≥ 1 genuine on ≥ 44 of 48 and ≥ 2 on ≥ 40".
  - As written, the second part says "genuine on ≥ 40 prompts". The data meet that: 40 prompts have an established
    genuine success.
  - 36 is the count with **≥ 2** genuine, but the sentence presents it as the count with any genuine success.
- Both counts are lower bounds (`results.csv` s2300):
  - 660 strict successes are unlabelled.
  - The first-4 estimate gives 40 / 39; the upper bounds are 44 / 43.
  - The run doc says none of this, although first-pass finding 10 quoted the run doc.
  - Numbers row 4 now says "lower bounds" and gives the estimate, but still omits the first pass's "not excluded (upper
    bounds 44 / 43)".
- "The rest held" also covers:
  - parts that were **not measured**: expectation 1 at s0350, and pass@8 at 50 / 200 (amendments 1 and 3);
  - expectation 4's early part, which holds only on the 32 base draws. With the extension draws, s0100 has 4 > 3.
- The cap entry lost its threshold (≤ 0.5 %).
- Fix, run doc: "step-2,300 ≥ 1 genuine on ≥ 44 and ≥ 2 on ≥ 40 (40 / 36 established; lower bounds, upper 44 / 43),
  cap share ≤ 0.5 % (0.63 % at 1,600). The rest held (expectation 4's early part on base draws) or was not measured
  (s0350, pass@8 at 50 / 200)."
- Fix, numbers row 4: add "not excluded (upper bounds 44 / 43)".

**3. "Stops gaining" is still in the plain summary, and the headline has no noise hedge (plain; first-pass finding 18
not fixed there).**
- Quote: "**The checker score climbs at every snapshot.** … After step 1,100 the share passed within eight tries stops
  gaining while pass@1 keeps rising".
- Files (`passk.csv`, `summary.json`): pass@8 is 0.8716 at 1,100, 0.8716 at 1,600 and 0.8853 at 2,300. Δpass@8 from
  1,100 is +0.014, 90 % [−0.018, 0.046]. That is "no detectable gain", not "stops gaining".
- The first pass flagged "stops rising". The rewrite only swapped the verb.
- The headline also drops the run doc's hedge. 0 → 50 (+0.006) and 50 → 100 (+0.019) are inside the pre-registered
  ≈ 0.03 noise floor.
- Fix: "**The checker score rises at every snapshot** (the first two steps within noise)…" and "…shows no clear further
  gain while pass@1 keeps rising".

**4. "On ordinary prompts … with no clear trend" (plain; first-pass finding 20 only partly fixed).**
- Quote: "On ordinary prompts the gamed share stays between 0.05 and 0.28 per snapshot, with no clear trend."
- The range was fixed. "Ordinary prompts" was kept.
- The arm-C sample (`hand.armc_sample()`) includes the IFBench reach ("hard") prompts:
  - 18 of 360 items (s0750 2, s1100 4, s1600 6, s2300 6);
  - 16 of the 120 late items, 6 of them gamed.
- The 0.28 maximum (s2300, 11 / 40) contains 2 gamed reach items. On non-reach prompts alone:
  - the per-snapshot range is 0.05–0.265;
  - the late share is 0.192 (20 / 104).
- "With no clear trend" brings back the "no change" reading that the first pass warned against.
  - The two latest snapshots have the highest shares (0.25 and 0.275).
  - The pooled share goes 0.14 → 0.22.
  - The 90 % interval of early − late, [−0.175, 0.015], only just reaches 0.
  - "Flat" is the pre-registered label for |Δ| < 0.2.
- Fix: "On a random sample of all checker passes (mostly ordinary prompts) the gamed share stays between 0.05 and 0.28 per
  snapshot: 0.14 early vs 0.22 late, inside the pre-registered 'flat' band."

**5. "Other strict successes carry no label" is false (numbers, hand gate; pre-existing, missed by the first pass).**
- Quote: "The 1559 strict successes the gate needed got their labels from: read 1440, inherited 45, screen 74 (1079
  genuine, 480 gamed). Other strict successes carry no label (estimated rates use the first-4 share)."
- Files (`handcheck.csv` vs `hand.needed()`): 342 of the 1,782 read items are **outside** the 1,559 needed draws. All of
  them are strict successes.
  - 305 are reach-prompt items at s0500–s2300 read beyond the walk's stopping points (s0500 5, s0750 89, s1100 77, s1600
    67, s2300 67).
  - 37 are the superseded s0500 arm-C sample, which amendment 5 re-drew.
- Among arm-B strict successes, 379 labels lie outside the needed set (305 read, 46 screen, 28 inherited). `results.csv`
  counts them.
  - At s2300, ifbench_1 has 25 labels (18 needed) and ifbench_4 has 27 (20 needed).
  - So row 4's "ifbench_1 / 4 all strict successes gamed" rests partly on these "other" labels.
- Fix: "A further 342 read items lie outside that set. 305 are extra reach reads, counted in `results.csv`; 37 come from
  the superseded s0500 arm-C sample and are unused. Further screened / inherited draws also carry labels. The remaining
  strict successes carry no label."

**6. "The rest unlabelled" (numbers, strict-vs-genuine line; rewrite wording).**
- Quote: "40 strict successes labelled per step (arm C: 349 of 360 read, 11 inherited from identical answers), the rest
  unlabelled".
- Files (`hand.Labels()`): outside the arm-C sample, **638 of the 6,698** arm-A strict successes carry labels.
  - Screened or inherited labels appear at every checkpoint (dpo: 45 inherited, 2 screen).
  - Reads: s0200 1; s0500 48 (37 from the superseded sample, 11 reach); s1100 94; s1600 115. These are arm-B base draws of
    reach prompts.
- The old "the rest unread" was also inexact. The new word is inexact too.
- Fix: "the rest not used in the estimate".

**7. Same quantity shown two ways (numbers; first-pass finding 22 only partly fixed).**
- Quotes: Arm C bullet "arm B (secondary): early 0.062 (n 16)" vs row 7 "early 0.0625 on 16 items".
- 1 / 16 = 0.0625. The bullet still rounds half to even. The new note "half-values rounded half to even" appears only in
  the Arm D header.
- Fix: write "0.0625" in the bullet, or move the rounding note to the section's opening paragraph.

## Confirmed fixed (no residual)

- First-pass findings 1, 2, 3, 5, 6, 8, 9, 11, 13, 14, 15, 16, 17 (the "read" → "labelled" headers), 19, 21, 23, 24
  and 25.
- 4 is fixed: 26 of 48 prompts go from F1\* to F25 in 1–2 checkpoints, and abrupt is 0.
- 12 is partly fixed: see finding 2.

Re-verified values:
- Arm A pass@1 / 4 / 8 and their intervals, and the per-family values.
- Genuine estimates 0.254 … 0.505 … 0.496.
- F1 counts per class; F2 ≤ 750 on 29 (≤ 500 on 17, so H = 750).
- F1\* < F1 on 18, all one checkpoint earlier.
- Median earliest rate 0.0391 over 48 and 0.0430 over the 36 with F25.
- Categories 10 / 26 / 12, and the F1\* → F25 step counts 14 / 12 / 8 / 2.
- s2300: 40 / 36 established, estimate 40 / 39, upper bounds 44 / 43, 660 unlabelled.
- Expectation 4's early part: 0 / 2 on base draws, 1 / 4 with extension draws.
- Arm-C quarter agreement 88 / 90, and 349 read + 11 inherited.
- Hand-gate counts: 1,782 items, 2,104 reads, 296 / 26, 272 agree, 209 confirmed / 103 changed.
- 64 batch files plus 11 adjudication / audit tasks.
- Compute: 27 job runs, 20.22 GPU-h, 116.8 M tokens, 21,216 draws.
- Spend: $154.67, 29.72 h, 17 orphans = $34.84, $0.86, $1.69, $117.28 at $5.29/h.
- All Arm D values and the half-to-even note within Arm D.
- The 14.8 % thinking drop.

## Resolution (executor, 2026-11-22 06:11 UTC)

All 7 accepted and fixed:
1. Run doc: "0.31 of the first ≤ 4 late wins per cell (536)".
2. Run doc: "step-2,300 prompts with ≥ 1 / ≥ 2 genuine (40 vs ≥ 44; 36 vs ≥ 40)".
3. Plain: "rises at every snapshot (within noise early on)" and "shows no detectable gain".
4. Plain: "On a random sample of checker passes … (flat by our advance test)".
5. Numbers: the 342 further labelled strict successes outside the needed set are stated.
6. Numbers: "the arm-C gamed share uses only these 40".
7. Numbers: "0.0625".

Word counts after the fixes: run doc 400, plain summary 499.
