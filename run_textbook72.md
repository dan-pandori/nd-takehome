# run textbook72 — the proof-state models on the group's 72 textbook problems

**Models:** 3.2 M-param, from-scratch, `lean_staten`, sampled in the proof-state environment (SN-v2 naming).
SN-cap12 = Stage-1 on K12 (cap 12); SN-v2 cap-6 = Stage-1 on the cap-6 control set; T1 = + 8 ladder EI rounds; frozen = no RL.
**Protocol:** k 256, T 0.8, `max_steps` 96, `max_action` 512, batch 4,096, seed 0, one A40. **Lean alone decides.** Details and
sources: `numbers.md` § textbook72.

| arm | per seed, all 72 | IQM | union | dev58 per seed | train14 per seed |
|---|---|---|---|---|---|
| SN-cap12 T1 | 37 / 38 / 36 / 38 | 37.5 | 46 | 30 / 32 / 30 / 32 | 7 / 6 / 6 / 6 |
| SN-cap12 frozen | 26 / 29 / 32 / 26 | 27.5 | 36 | 20 / 23 / 26 / 21 | 6 / 6 / 6 / 5 |
| SN-v2 cap-6 T1 | 22 / 16 | 19 | 22 | 18 / 12 | 4 / 4 |
| SN-v2 cap-6 frozen | 16 / 14 | 15 | 18 | 13 / 12 | 3 / 2 |
| *Robbie combined (his checker Lean ∧ nd_verify)* | *32 / 30 / 32* | *31.3 mean* | *36* | | |

**SN-cap12 T1 solves 36–38 of 72 per seed**, against Robbie's combined model at 30–32 per seed. That compares different
models, formats and checkers. Our Lean ∧ `nd_verify` count is identical to our Lean count: 0 of 6,128 distinct accepted
proofs fail `nd_verify`. Per problem, we solve 34 of the 36 problems his seeds solve between them. He alone solves 2
(reference 6 and 11 lines). We alone solve 13, including all three solved problems with reference ≥ 16 lines. Robbie's
"naive 13" is 13 %, i.e. 9 problems.

By `reference_lines`: all 1–5; T1 18–19 of 24 at 6–10; 4–7 of 16 at 11–15; 2–3 of 13 at 16+. That is the length wall at
`L*` ≈ 12 again. 25 of 72 problems are solved by no checkpoint. The step cap was never hit. Contamination: none with premise
order kept. Ignoring premise order, one problem (disjunctive syllogism) matches a K12 set; every model solves it.

**Expected vs outcome:**

| pre-registered | outcome |
|---|---|
| SN-cap12 T1 36 (28–44), union 42 | 37.5, union 46: **hit** |
| SN-cap12 frozen 24 (16–32), union 30 | 27.5, union 36: **hit** (union higher) |
| SN-v2 cap-6 T1 32 (24–40) | 22 / 16: **miss**, cap-6 Stage-1 is far weaker on long problems (1 and 0 solved at ≥ 11 lines) |
| SN-v2 cap-6 frozen 18 (10–26) | 16 / 14: **hit** |
| (a) T1 − frozen ≥ +6 on every seed | +11 / +9 / +4 / +12: **miss** on s2 (mean +9, just over the MDD of ≈ 8) |
| (b) ≤ 3 of 13 at 16+ | max 3: **hit** |
| (c) T1 median ≥ 31 | 37.5: **hit** |
| (d) cap hits ≤ 0.1 % | step 0 %; action cap 0.157 % on T1 s0: **miss**. Re-run at 1,024 gives the identical solved set. |
| (e) 0–5 overlaps, short | 1 (reference 7): **hit** |

Spend: 0.36 pod-hours, $0.18.
