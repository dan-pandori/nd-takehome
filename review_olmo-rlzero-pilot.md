# Review — olmo-rlzero-pilot (proposal 34)

Reviewer: agent:claude, reviewer role, 2026-11-03. Run branch `dan_olmo-rlzero-pilot`. Brief: nd-rl
`docs/proposals/followups/BRIEF_olmo-rlzero-pilot.md`. Pre-registration: `preregistration/olmo-rlzero-pilot.md`, Part A
(255151cd, 01:20:39 UTC) and Part B (01d95ecc, 03:33:40 UTC).

Phase 1 was done in `~/review/olmo-rlzero-pilot`, where the executor's write-ups had been removed. My own code is in
`review/olmo-rlzero-pilot-recount/`:
- `rv_core.py` runs AI2's verifier from upstream source, and holds my integer read-out and the loaders.
- `rv_regrade.py` re-grades every stored text. `rv_table.py` builds the per-cell table.
- `rv_stats.py` computes pass@k, dynamics, reach and the verdict inputs. `rv_ll.py` checks the likelihood phase.
- `rv_contam.py` is the Dolci scan. `rv_tables.py` writes the markdown tables.

Their outputs are in `out/`. Every table below is pasted from `out/tables.md` or printed from the `out/*.json` files.

## Disclosure: what I saw before or during phase 1

- **Commit subjects.** The session's start-up context printed the run's last five commit subjects, including "DONE —
  reach 0 / reverse 0 at K<=512 (all 17 RL-only solves fall to the base), likelihood in support, step_0100 half, …"
  and "pass 2 done (base solved 2 of 3 more; 1 reach, 1 reverse at K=256)". So I knew the headline result before I
  recounted.
- **Auto-memory.** My session started with a memory note the executor had written at 16:20 UTC
  (`elicitation-verdict-rule-design`). It says:
  - the verdict came out "inconclusive";
  - the pass@8 gap was 0.26;
  - all 17 RL-only solves fell to the base within 383 samples;
  - 2 of 16 candidates failed confirmation;
  - one "loss" vanished under the symmetric extension.
- **Executor comments in code I read to learn the formats.**
  - `ll_plan.py`: F_base's texts "were lost with pod orz-a".
  - `compute_rows.py`: orz-a was "lost ~07:54 (host restart)", and F_s0100b was "stopped 08:57 for budget".
  - `half_subset.py`: step_0100 ran on "a seeded random half … budget rule".
  - `after_d2.sh`: the reason for aime2025_22's symmetric extension.
- **Executor-derived files I read.**
  - `results.csv`, compared cell by cell only after I had built my own table.
  - `compute_axis.csv`, after I had computed mine.
  - Also: `exclusions.csv`, `jobs.csv`, the `plan/*.txt` pid lists, all `meta/*.json`, the job logs, the head (two
    AIME 2023 rows) of `manifest.csv`, the pod scripts, and the registry rows.
- **Not read in phase 1:**
  - the write-ups: `run_olmo_rlzero_pilot.md`, `numbers.md`, `log.md`, `STATUS.md`, `QUESTIONS.md`,
    `olmo_pilot/README.md`, `decision_32b.md` and the plain summary;
  - the result tables: `passk.csv`, `passk_lb.csv`, `reach.csv`, `dynamics.csv`, `lengths.csv`, `half_subset.csv`,
    `candidates.csv`, `likelihood.csv`, `stage0_summary.json`, `plan/summary.json`;
  - the contamination files: `contamination_*.csv`, `nearest_embed.csv`;
  - the figures, and the docs in the bucket.

# §Recount (phase 1, blind)

## 0. Models every number below refers to

All four models are 7.3 B `Olmo3ForCausalLM`, pretrained (not from scratch), bf16.
- **base**: `allenai/Olmo-3-1025-7B` @ `main`.
- **step_0100 / step_0500 / step_2800**: `allenai/Olmo-3.1-7B-RL-Zero-Math` at those branches. These are RLVR straight
  from the base on `allenai/Dolci-RL-Zero-Math-7B`; `step_2800` = `main` (per the pre-registration's shard hashes).

Sampling used vLLM 0.11.0 with the `olmo_thinker_rlzero` template, T 1.0, top-p 1.0, at most 16,384 tokens, EOS stop
only. Every evaluation job used n-gram speculation (4 draft tokens); Stage 0 was plain.

The evaluation problems are MathArena AIME 2024, 2025 and 2026 (90). The headline set is 83 after the 7 exclusions.
The grade is `rl` (see §1) unless a row says otherwise.

## 1. Inputs and settings, checked independently

- **Problems and answers.** I fetched MathArena's six AIME parquet files at the revisions in `problems.jsonl`. All
  120 statements and answers match byte for byte.
- **Template.** The sampler's template equals `olmo_thinker_rlzero` verbatim. I fetched open-instruct
  `dataset_transformation.py` at bb58c66 myself to check.
  - All 17 jobs' meta files carry the same template sha256 (`4380e622…`).
  - The prompt tokens of all 250 likelihood items equal my own tokenisation of that template.
  - The base and step_2800 `tokenizer.json` files are identical, and neither `generation_config.json` sets sampling
    defaults.
- **Decoding.** Every job's meta has T 1.0, top-p 1.0 and max_tokens 16,384. I read the vLLM engine line in 17 job logs:
  - every one has dtype bf16, kv_cache auto and prefix caching on;
  - every evaluation job (F, C, E, P) has `SpeculativeConfig(method='ngram', num_spec_tokens=4)`;
  - the Stage 0 jobs have none.

  The gate that adopted speculation reproduces from the graded rows:
  - throughput 758.7 / 557.2 = 1.36 (rule: ≥ 1.25);
  - pass@1 difference CI [−0.035, 0.054];
  - mean-length difference CI [−1,131, 729] tokens.

  Both intervals contain 0, so the speculation was adopted by the pre-registered rule.
- **What RL rewarded.** I checked this from upstream code I fetched myself (bb58c66).
  - The RL reward decodes with `skip_special_tokens=True` and calls `MathVerifier.async_call`, which is
    `loop.run_in_executor(None, …)`, a worker thread.
  - There `is_equiv`'s `signal.alarm` timeout raises `ValueError`, and its `except Exception` returns False. So only
    `hendrycks_is_equiv` can reward. The executor's reading is correct.
  - The vendored `oi_math_utils.py` is upstream `math_utils.py` with only the logger import changed.
  - The script's dataset name `allenai/Dolci-RLZero-Math-7B` resolves to `allenai/Dolci-RL-Zero-Math-7B` @ 93b5e498.
    Its last data upload was 2025-11-19, and later commits change only the README.

  One consequence shapes everything below. The verifier never reads an `Answer: N` line, which is what the prompt
  asks for. It rewards only `\boxed{}`, a Minerva phrase, the last `$…$` pair, or the whole output. With my harness:
  - "Answer: 60" earns 0;
  - "…where $\angle B = 60^\circ$, we get…" earns 1 when the answer is 60.

## 2. Re-grade of every stored sample text

`rv_regrade.py` runs AI2's `MathVerifier.__call__`, extracted by `ast` from upstream `ground_truth_utils.py`. It runs it
through `run_in_executor` (`rl`) and in the main thread (`main`). It also re-decodes each sample's stored token ids
with the Olmo tokenizer.

**Result: 4,572 samples with stored text (914 `rl`-correct), 0 disagreements with the executor's graded rows** on
`rl`, `main`, `n_tok` and `finish`. Every stored text equals the decode of its token ids.

The texts below are **missing from the repository and the bucket**:

| job | what it is | samples | texts kept |
|---|---|---|---|
| F_base | the base's entire phase-F evaluation budget | 1,440 | 0 |
| P_base | the base's Dolci probe | 64 | 0 |
| g_spec_base | the speculation gate (AIME 2023) | 240 | 0 |
| s0_base | Stage 0 (AIME 2023) | 480 | 384 |

So **137 of the base's 155 counted successes (all its phase-F ones) cannot be re-graded or read**. Every RL arm's
counted successes were all re-graded from text: step_2800 389, step_0500 225, step_0100 104. The base's 18 extension
successes were also re-graded.

## 3. My per-cell table against `results.csv`

`rv_table.py` assigns phases from job names, orders each cell's samples by (chunk, i), and uses my re-grade wherever a
text exists. That gives 315 (model × problem) cells with 0 key collisions across jobs.

**All 315 cells match `results.csv` exactly** on these fields:
- attempts, n_fixed;
- `rl` successes overall, in F and in C;
- first `rl` success, `main` successes and first `main` success;
- mean tokens.

The executor's `ansline` and my integer read-out are different extractors by design. My first version disagreed with
theirs on 13 RL cells, because it took the number after a "**Final Answer:**" header. My corrected version takes
whichever comes last: an integer on an `answer:` line, or a boxed integer. It agrees within 0–2 per job.

## 4. pass@k (Chen estimator on phase-F samples, problem bootstrap)

| model (7.3 B, pretrained) | problems | pass@1 | pass@8 | pass@16 |
|---|---|---|---|---|
| base `Olmo-3-1025-7B` main | all (n=83) | 0.094 [0.066, 0.125] | 0.364 [0.275, 0.455] | 0.458 [0.349, 0.566] |
|  | aime2024 (n=24) | 0.107 [0.060, 0.156] | 0.448 [0.274, 0.625] | 0.542 [0.333, 0.750] |
|  | aime2025 (n=30) | 0.096 [0.046, 0.154] | 0.326 [0.179, 0.480] | 0.400 [0.233, 0.567] |
|  | aime2026 (n=29) | 0.082 [0.039, 0.134] | 0.335 [0.197, 0.482] | 0.448 [0.276, 0.621] |
| RL-Zero-Math `step_0100` | all (n=42) | 0.301 [0.208, 0.399] | 0.643 [0.500, 0.786] | — |
|  | aime2024 (n=17) | 0.316 [0.162, 0.478] | 0.588 [0.353, 0.824] | — |
|  | aime2025 (n=10) | 0.300 [0.100, 0.525] | 0.600 [0.300, 0.900] | — |
|  | aime2026 (n=15) | 0.283 [0.150, 0.433] | 0.733 [0.533, 0.933] | — |
| RL-Zero-Math `step_0500` | all (n=83) | 0.304 [0.223, 0.390] | 0.506 [0.398, 0.614] | — |
|  | aime2024 (n=24) | 0.417 [0.250, 0.583] | 0.667 [0.458, 0.833] | — |
|  | aime2025 (n=30) | 0.263 [0.133, 0.408] | 0.433 [0.267, 0.600] | — |
|  | aime2026 (n=29) | 0.254 [0.134, 0.388] | 0.448 [0.276, 0.621] | — |
| RL-Zero-Math `step_2800` (= main) | all (n=83) | 0.419 [0.330, 0.509] | 0.627 [0.518, 0.723] | — |
|  | aime2024 (n=24) | 0.536 [0.365, 0.703] | 0.750 [0.583, 0.917] | — |
|  | aime2025 (n=30) | 0.342 [0.200, 0.496] | 0.533 [0.367, 0.700] | — |
|  | aime2026 (n=29) | 0.401 [0.254, 0.556] | 0.621 [0.448, 0.793] | — |

step_0100 was sampled on only 45 of the 90 problems (42 headline). On that same subset:

| model | pass@1 | pass@8 |
|---|---|---|
| base | 0.116 [0.074, 0.161] | 0.450 [0.323, 0.577] |
| step_0100 | 0.301 [0.208, 0.399] | 0.643 [0.500, 0.786] |
| step_0500 | 0.402 [0.283, 0.524] | 0.643 [0.500, 0.786] |
| step_2800 | 0.562 [0.440, 0.685] | 0.786 [0.667, 0.905] |

**Mean response length** (phase F, headline, per sample), and the share cut at 16,384 tokens:

| model | mean tokens | share cut | on the half |
|---|---|---|---|
| base | 5,863 | 15.2 % | 5,593 |
| step_0100 | 11,309 | 31.5 % | — |
| step_0500 | 11,755 | 24.2 % | — |
| step_2800 | 11,745 | 18.1 % | — |

The cap is the RL recipe's response length, so truncation is part of the protocol. RL ran with
`mask_truncated_completions False`, and 2 of the 17 base first-successes below are cut samples whose `\boxed{}`
came earlier. The share cut is large in every stratum.

**Stage 0** (AIME 2023 pilot) reproduces Part B's B1 table exactly:
- base: pass@1 0.085, pass@4 0.221, pass@16 0.367; mean 6,353 tokens (median 4,206); 17.5 % cut, none of them correct;
- step_2800: pass@1 0.383, pass@2 0.467; mean 12,249 tokens; 21.7 % cut, 2 of them correct;
- formats: 2 of the base's 41 integer-correct samples fail `rl`. `rl` and `main` differ on 1 sample; `rl` and
  `ansline` on 4.

## 5. Matched k = 8: expected entries and exits

| comparison | problems | entries | exits |
|---|---|---|---|
| step_0500 vs base | all83 (83) | 14.04 | 2.27 |
| step_2800 vs base | all83 (83) | 22.77 | 1.00 |
| step_2800 vs step_0500 | all83 (83) | 12.00 | 2.00 |
| step_0100 vs base | half (42) | 9.88 | 1.77 |
| step_0500 vs base | half (42) | 8.61 | 0.50 |
| step_2800 vs base | half (42) | 14.61 | 0.50 |
| step_0500 vs step_0100 | half (42) | 3.00 | 3.00 |

The paired problem bootstrap of the entry differences vs base (`out/entries_growth.json`):

| difference | problems | value [95 %] | |
|---|---|---|---|
| step_2800 − step_0500 | 83 | 8.73 [2.97, 15.23] | grows |
| step_0500 − step_0100 | 42 | −1.27 [−5.50, 2.50] | no growth between 100 and 500 |
| step_2800 − step_0100 | 42 | 4.73 [1.23, 8.73] | grows |

## 6. Reach both ways round, the extension protocol, and the verdict rule

| checkpoint | reach (c's F) | reach (c's F+C) | strong reach | reverse (c's whole budget) | reach / reverse under `main` | under my integer read-out |
|---|---|---|---|---|---|---|
| step_0100 | 0 | 0 | 0 | 7 | 0 / 7 | 0 / 6  |
| step_0500 | 0 | 0 | 0 | 13 | 0 / 13 | 0 / 12  |
| step_2800 | 0 | 0 | 0 | 0 | 0 / 0 | 1 / 0 ['aime2025_14'] |

The intermediates' "reverse" counts are at 8 samples of c. They are not symmetric: only step_2800 got the reverse
extension.

**Candidates and how they resolved.** A reach candidate is a headline problem where step_2800 or step_0500 has ≥ 1
`rl` success in F and the base has 0 of 16. There are **17**, the same 17 as `plan/E_base.txt`. The extension
followed its rule exactly:
- chunks were sequential, and each problem stopped at its first correct chunk;
- the budget was 128, then 256 for the three still unsolved, then 512 for one;
- the attempt totals equal the chunk arithmetic for every problem.

**Every candidate fell to the base.** The base's first-success positions were 18, 25, 31, 39, 45, 46, 64, 73, 73, 77,
79, 83, 91, 104, 168, 248 and 383 (median 73). Each of these first successes is also integer-correct.

The reverse candidates were the problems where the base had ≥ 1 in F and step_2800 had 0 of 8:
- **aime2024_29** fell to step_2800 at its 53rd sample.
- **aime2025_14** fell at its 280th of 288.
- **aime2025_22** was a reach candidate that only step_0500 had solved; the base then solved it in its extension.
  step_2800 got the symmetric extension and solved it at its 12th sample.

step_0100's six F solves where the base had 0 in F are all among the 17 candidates, so the base was extended on every
one.

**At K = 128 the picture was different.** Three candidates were still unsolved by the base after its first 128
samples: aime2024_10, aime2024_26 and aime2025_25. Each had step_2800 F + C successes of 1 + 3, 3 + 3 and 1 + 3. All
three met the strong-reach definition at K* = 128.
- Reverse stood at 1 (aime2025_14), or 2 counting aime2025_22, whose symmetric extension came in pass 2.
- So after pass 1 the pre-registered rule sat on its "RL extended reach" threshold: ≥ 3 strong, and strong exceeding
  reverse by ≥ 2.
- Passes 2 and 3 removed all three: first successes at 168, 248 and 383. Both passes were pre-registered and
  budget-gated.

**The verdict by the pre-registered rule, as amended in Part B**, is **"inconclusive at this budget"**.
- **Not "extended":** strong reach is 0 and reverse is 0.
- **"Elicitation only" fails its second clause.** Clause (a) holds, since strong reach is 0. Clause (b) needs the base's
  pass@k to reach the final's within the 95 % interval at matched k = 8, and it does not:
  - base 0.364 [0.275, 0.455];
  - final 0.627 [0.518, 0.723];
  - final − base 0.262 [0.179, 0.352].
- On the candidate problems at the extension budget, clause (b) would hold, because the base solved all 17 within
  512.

## 7. Hand-check of the 20 decision-relevant successes, and 10 more

The brief asks for a hand-check of 20 counted successes. I chose the 20 that decide the headline:
- the base's first success on each of the 17 candidates;
- step_2800's resolving success on the 3 reverse or symmetric problems.

Six reader sub-agents of this session read each full text and checked the mathematics, mostly by script. I confirmed
two verdicts by my own reading: base aime2024_20 and step_2800 aime2025_14. **In all 30 texts the verifier matched the
response's own last `\boxed{}`**, so there are no extraction artefacts. The derivations vary (`out/hand_check.json`):

| problem | sample | tokens | role | derivation |
|---|---|---|---|---|
| aime2024_09 | base E1 c5 i2 | 15,922 | 1st base success (83rd) | FLAWED: limit direction backwards, invalid algebra; boxes 480 |
| aime2024_10 | base E2 c10 i7 | 6,784 | (168th) | GENUINE |
| aime2024_14 | base E1 c6 i7 | 12,340 | (104th) | GENUINE |
| aime2024_18 | base E1 c1 i1 | 4,071 | (18th) | GENUINE (minor slips) |
| aime2024_20 | base E1 c4 i14 | 8,263 | (79th) | **GUESS**: tries formulas until one gives a clean number ("not sure… tentatively… 80") |
| aime2024_26 | base E3 c19 i30 | 13,566 | (383rd) | FLAWED: assumes a coordinate equals 100; the count is right |
| aime2025_12 | base E1 c4 i8 | 9,041 | (73rd) | FLAWED: two sign errors pick the mirror region (same area) |
| aime2025_21 | base E1 c1 i14 | 16,384 (cut) | (31st) | FLAWED (borderline genuine): proceeds "without resolving the contradiction" |
| aime2025_22 | base E1 c4 i8 | 9,075 | (73rd) | GENUINE |
| aime2025_24 | base E1 c2 i6 | 8,872 | (39th) | FLAWED: n = 140, t = 9 instead of 139, 10, and the errors cancel |
| aime2025_25 | base E2 c15 i7 | 16,384 (cut) | (248th) | GENUINE (later self-retracted, then truncated) |
| aime2025_29 | base E1 c3 i15 | 14,535 | (64th) | GENUINE |
| aime2026_03 | base E1 c2 i12 | 7,438 | (45th) | GENUINE |
| aime2026_22 | base E1 c4 i12 | 8,207 | (77th) | GENUINE |
| aime2026_23 | base E1 c5 i10 | 10,169 | (91st) | GENUINE |
| aime2026_24 | base E1 c1 i8 | 12,766 | (25th) | GENUINE |
| aime2026_26 | base E1 c2 i13 | 14,212 | (46th) | FLAWED: right candidates {12, 132}, miscounts, takes the greatest |
| aime2024_29 | step_2800 E1 c3 i12 | 14,140 | reverse resolved (53rd) | GENUINE |
| aime2025_14 | step_2800 E3 c17 i23 | 11,321 | reverse resolved (280th) | **GUESS**: computes m+n+p = 24+7+3 = 34, then boxes 60 |
| aime2025_22 | step_2800 E2 c9 i3 | 10,664 | symmetric extension resolved (12th) | GENUINE |

The base's tally is **10 genuine, 6 flawed but arriving, 1 guess**.

For the two weakest base resolutions, I also had **every RL success on the same problem** read:
- **aime2024_20.** All 5 are guesses: 3 from step_2800, 2 from step_0500. They land on 1/s = Σ 1/a without deriving
  it, just as the base did.
- **aime2026_26.** None of the 5 is genuine: 3 from step_2800, 2 from step_0100. Each reaches the S = 0 candidates and
  takes the larger without verifying the count, the same flaw as the base's.

So on these two problems RL raised the rate of the same incomplete answer: 3/24 vs 1/80, and 3/24 vs 1/48. It did not
produce a better derivation.

My reader rubric for aime2026_26 wrongly required that n = 12 be shown to fail. Both n = 12 and n = 132 give seven
values, and the problem asks for the greatest n. I reclassified the base's sample from the reader's "guess
(borderline)" to FLAWED after reading the statement.

## 8. aime2025_14: the base's only credit is probably a verifier false positive

The pre-registration rule treats this as a reverse candidate, resolved at step_2800's 280th sample. Neither side's
credit holds up:
- **The base's credit.** Its only `rl` success in 16 samples (F_base chunk 0, i 9) is 549 tokens long, has no integer
  read-out (`ans` = None), and is not `ansline`-correct.
- **Why that is suspicious.** The statement contains `$\angle B=\angle E=60^{\circ}$` and the answer is 60. The
  verifier strips `^{\circ}` and accepts a response whose last `$…$` restates that angle (§1). Its text is among the
  lost F_base texts, so it cannot be read.
- **step_2800's credit** is a confirmed guess (§7).

On the evidence neither model solves aime2025_14. It is the one problem whose solved status hinges on an `rl`-correct
base sample with no correct stated integer.

Six other base samples share that property: 1 each on aime2024_25, aime2025_01, aime2025_02 and aime2026_08, and 2 on
aime2025_17. Their problems all have other integer-correct base successes, and aime2026_01 is excluded. Under my
integer read-out, step_2800 has 1 reach problem (aime2025_14), but the base had only 16 samples there.

## 9. Likelihood (phase L, 250 scored items)

**Integrity is clean** (`rv_ll.py`):
- every item's `resp_ids` equals the stored sample's token ids;
- every item is `rl`-correct in my re-grade;
- every prompt equals my template tokenisation;
- the stored per-token log-probs reproduce `n_tok`, `mean_lp` and `sum_lp`.

The selections hold **no "reach" group**: there are no reach problems. The substitute is "late", the RL solutions on
the 17 candidates.

| group | items (problems) | base mean log p / token (median) | own (median) | gap own − base, median [p10, p90] | summed gap, median (nats) | inside base_own range | inside base_own + pilot | inside, other problems only |
|---|---|---|---|---|---|---|---|---|
| late | 78 (17) | -0.546 | -0.492 | 0.053 [0.006, 0.066] | 646 | 1.00 | 1.00 | 1.00 |
| ckpt_other | 135 (37) | -0.454 | -0.431 | 0.043 [0.005, 0.060] | 192 | 0.90 | 1.00 | 0.90 |
| base_own | 18 (17) | -0.435 | -0.435 | 0.000 [0.000, 0.000] | 0 | 0.89 | 0.94 | 0.83 |
| base_own_pilot | 19 (9) | -0.334 | -0.334 | 0.000 [0.000, 0.000] | 0 | 0.37 | 0.95 | 0.37 |

The control ranges:
- **base_own** (the base's own correct solutions, all on the 17 candidates): −0.915 to −0.345, n = 18.
- **base_own + pilot** (adding AIME 2023, which is contaminated): −0.936 to −0.246, n = 37.

Part A asked for controls "on other problems". The base_own controls are on the same problems. My leave-same-problem-out
variant gives the same 1.00 for "late".

The per-token criterion is weak evidence of "support". A 0.053 nats/token gap over a median 12,566 tokens per "late"
solution is a median **646 nats** per solution: the base is about e^−646 less likely than the generator to write that exact text.
step_0100's solutions were never scored, because phase L ran before step_0100's phase F.

## 10. Contamination

- **Dolci, my own scan** (`rv_contam.py`). I used three measures: word 8-gram containment, 8-gram containment with
  numbers masked (to catch digit-changed variants), and character 50-grams.
  - Among the 90 evaluation problems, those at ≥ 0.3 on any measure are aime2024_13 (masked 1.00, a digit-changed
    copy), aime2024_22 (0.40), aime2024_24 (0.31) and aime2026_01 (verbatim, same answer, in a dataset uploaded
    2025-11-19). All four are excluded.
  - aime2026_14 (0.375) matches only boilerplate: its match is a tetrahedron problem. It is rightly kept.
  - I read the aime2024_22 match: "smallest … changes to 8" against the problem's "greatest … changed to 1". It is a
    variant.
- **Midtraining.** I could not re-scan 36 M documents on the VPS. Instead I re-aggregated the executor's raw per-shard
  output (`midscan_shards.jsonl.gz`): 6,465 shards, 35,963,968 documents, 14 subsets, no duplicate shards.
  - Every evaluation problem at ≥ 0.5 is excluded: aime2024_16 (1.00), aime2024_27 (0.82), aime2024_28 (0.52),
    aime2026_01 (1.00).
  - Below that line I read the best snippets for aime2024_26 (0.39), aime2025_04 (0.43), aime2025_12 (0.32), and the
    others at ≥ 0.3. All are boilerplate or shared polynomials, not variants.
  - The web and code subsets of midtraining, and the pretraining mix, were not scanned. The pre-registration says so.

## 11. Compute axis

I recomputed the axis with my own lengths:

| model | Dolci probe, mean response tokens | AIME F, mean response tokens |
|---|---|---|
| base | 4,868 | 5,872 |
| step_0100 | 9,854 | 11,284 |
| step_0500 | 9,332 | 11,790 |
| step_2800 | 9,743 | 11,712 |

The accounting is rl-compute-share's: 6ND with N = 7.3e9 and D = 6.08e12, and 32 × 8 episodes per step. The low bound
uses the probe lengths, oversampling 1, no extra forward pass and no prompt tokens. The high bound uses the AIME
lengths, oversampling 3, 1 extra forward pass and 180 prompt tokens.

| step | low | high | geometric mean |
|---|---|---|---|
| 100 | 4.15e-05 | 8.56e-05 | 5.96e-05 |
| 500 | 2.57e-04 | 5.43e-04 | 3.73e-04 |
| 2800 | 1.49e-03 | 3.22e-03 | 2.19e-03 |

This equals `compute_axis.csv` to 4 significant figures. The oversampling of 1–3 for active sampling is an assumption,
not a measurement.

## 12. Spend and compute rows

- **Spend.** `podbudget` shows 26.52 pod-hours and **$40.26 of $50**. The budget was registered at 01:04 UTC, before
  the first pod at 01:21. `~/podhours.log` lists the pods:

  | pod | GPU | hours | cost | rate |
  |---|---|---|---|---|
  | orz-a | A100-SXM4 | 7.05 | $9.80 | $1.39/h |
  | orz-a (re-created) | A100-SXM4 | 0.11 + 0.09 | $0.27 | |
  | orz-b | H200 | 0.23 | $0.82 | |
  | orz-c | A100 PCIe | 7.21 | $12.90 | $1.79/h |
  | orz-d | A100-SXM4 | 11.85 | $16.47 | |

  None of the run's pods is live.
- **Compute rows.** The registry has 156 rows (`artifacts/olmo-rlzero-pilot/registry/`, also in the bucket). Each
  job's gpu_seconds, gen_tokens and attempts equal its meta file, for 18 jobs.
  - The sampling rows total 24.55 GPU-h and 55.8 M generated tokens.
  - The two void step_0100 runs are recorded with GPU-seconds but **gen_tokens 0**. F_s0100b's own log shows
    2,050,941 tokens at 08:55 UTC, so the rows understate generated tokens by at least ≈ 2 M.
  - P_base is an estimate; its row says so.

## 13. Timing, and deviations visible in the artefacts

- **Timing.** Part B was committed at 03:33:40 UTC. The speculation gate followed at 03:34–04:07, on AIME 2023 only,
  and phase F started at about 04:09. The exclusions were in the Part B commit. So the pre-registration preceded all
  evaluation sampling.
- **Phase C budget.** Part B registers 24 fresh samples per solving checkpoint, and `plan_next.py` writes `:24`. The
  plan files and `runqCE.sh` used **16 for step_2800 and 8 for step_0500**. step_0100's confirmation was never run.
- **step_0100.** Phase F ran on 45 of 90 problems (42 headline). The first run was lost with orz-a, and the second was
  stopped "for budget" after 160 samples on 20 problems; I checked that neither is used in any count.
  - The 45-problem "seeded random half" is not reproducible from committed code. I tried 5 common draw methods × 5,000
    seeds.
  - It is not stratified by year: 20 / 10 / 15.
- **Weight distance.** `weight_dist.jsonl` holds only rl100–base (2.59e-4) and rl200–rl100 (3.37e-4). Part A's
  comparison "≥ 10× smaller than to another base revision" was **not measured**. So the start revision is consistent
  with base `main` but not discriminated from a neighbouring stage-3 checkpoint.
- **Lost texts.** F_base (1,440), P_base and g_spec_base texts were not pulled back (§2).
- **Likelihood controls.** They are on the same problems, not "on other problems", and include contaminated AIME 2023.
  This does not change the result (§9).

## 14. Hard constraints

- `nd_verify` tree 9437bb72 is identical at HEAD, `origin/main` and `origin/dan`.
- `artifacts/TEST_RUN_DONE` blob 1d5cf064 is identical at all three.
- The run trains nothing, so there is no evaluation file in training code.
- Lean and `nd_verify` are not involved, since answers are checked by AI2's math verifier as the brief requires.
- The run's added lines mention textbook72 nowhere (0 matches), and `olmo_pilot/` and `artifacts/olmo_pilot/` mention it
  in no file.
- No pods are live.

**No hard-constraint violation.**

## 15. Pre-registered expectations against my values (B4; `rl` grade, 83 headline problems)

| expectation | my value | |
|---|---|---|
| base pass@1 0.03–0.08 | 0.094 | miss (above) |
| base pass@8 0.12–0.28 | 0.364 | miss (above) |
| base pass@16 0.18–0.35 | 0.458 | miss (above) |
| step_2800 pass@1 0.10–0.25 | 0.419 | miss (above) |
| step_2800 pass@8 0.25–0.50 | 0.627 | miss (above) |
| step_0100 pass@1 within ± 0.03 of the base's | 0.301 vs 0.116 (same 42) | miss |
| step_0500 between base and final | 0.304 | hit |
| step_2800 mean length ≥ 1.4 × base | 2.00 × | hit |
| step_0100 mean length within ± 20 % of base | 2.02 × (same 42) | miss |
| step_2800 reach 2–8 after pass 1 | 3 after pass 1 (0 after pass 3) | hit |
| strong reach 0–3 | 0 (3 at K* = 128) | hit |
| reverse 1–5 | 1 after pass 1, 0 at the end | hit after pass 1, miss at the end |
| entries vs base grow 0100 < 0500 < 2800 | 0100 9.88 vs 0500 8.61 (same 42), then 2800 14.61 | miss for 0100 < 0500 |
| 0500 → 2800 growth within noise | +8.73 [2.97, 15.23] | miss (outside noise) |
| ≥ 75 % of reach solutions in support; gap 0.05–0.3 nats | no reach solutions; "late" substitute 100 %, gap 0.053 | not testable as registered |
| verdict: inconclusive ≈ 55 % | inconclusive | the most probable outcome |
| spend ≤ $45 | $40.26 | hit |
| speculative decoding adopted (≈ 60 %) | adopted | — |

## Phase-1 findings (before reading the write-up)

1. **R1: the headline reproduces under the RL reward.** Reach is 0, strong reach 0 and reverse 0 for step_2800 at the
   full budget. All 17 RL-only solves fall to the base, by sample 383 at most (median 73). The pre-registered verdict
   is "inconclusive at this budget", because clause (b) fails at matched k = 8 (gap 0.262 [0.179, 0.352]).
2. **R2: what "the base solves it" means.** Read by hand, the base's resolving solutions are 10 genuine, 6 flawed but
   arriving, and 1 guess (aime2024_20). On aime2024_20 the RL solutions are guesses too (5/5). On aime2026_26 they have
   the base's flaw (5/5).
3. **R3: aime2025_14.** The base's only credit is probably a verifier false positive. The answer 60 is the angle in the
   statement; the sample has no stated integer and its text is lost. step_2800's resolving success is a confirmed
   guess. The reverse count does not change, but neither model can be said to solve the problem.
4. **R4: lost base texts.** F_base's 1,440 sample texts are gone, so 137 of the base's 155 counted successes cannot be
   re-graded or read.
5. **R5: deviations** (§13):
   - confirmation budget 16 / 8 instead of 24;
   - step_0100 on a 45-problem half not reproducible from code, with no confirmation and no likelihood;
   - the base-revision weight comparison not measured;
   - likelihood controls not "on other problems" (harmless).
6. **R6: compute rows.** The void step_0100 runs record gen_tokens 0 despite ≈ 2 M generated tokens.
7. **R7: hard constraints.** None violated.

# §Compare (phase 2: after reading the write-ups)

I read the following after the phase-1 commit (dfb3a406, 16:49:55 UTC):
- `run_olmo_rlzero_pilot.md`;
- the run's sections of `numbers.md`, `log.md`, `STATUS.md` and `QUESTIONS.md`;
- `olmo_pilot/plain_summary.md`, `decision_32b.md` and `README.md`;
- the three figures.

The checks added in phase 2 are in `out/sensitivity_templated.json`, plus the inline checks described below.

## Corrections to my §Recount

- **Weight distance (§13, R5).** I wrote that the comparison with another base revision was "not measured". According to
  `log.md` (04:08 UTC) it was measured:
  - step_0100 to `stage3-step11000`: 1.2e-2;
  - step_0100 to `stage2-step47684`: 0.31.

  `pod/olmo_pilot/wd.sh` computes 7 pairs. But the pulled-back `meta/weight_dist.jsonl` holds only the 2 rows from the
  run on orz-a that was killed at 03:44. So the claim is **measured but not reproducible from the pulled-back files**,
  not "unmeasured".
- **step_0100's half (§13, R5).** It reproduces exactly as `random.Random(20261103).sample(eval_pids, 45)`. The seed is
  stated in `log.md` (08:56, 10:59), not in code. The rule was declared at 08:56, before any step_0100 result was used.
  The point is resolved.

## Claims against my recount

### `run_olmo_rlzero_pilot.md`

| claim | my value | verdict |
|---|---|---|
| base `main` is RL-Zero's start: "step_0100 is 2.6 × 10⁻⁴ from it" | 2.59e-4 in `weight_dist.jsonl`; base `main` = `stage3-step11921` (identical LFS oids, checked) | number reproduces; the "start" inference rests on the log-only 1.2e-2 / 0.31 rows |
| 83 problems, 7 excluded for contamination | my Dolci scan flags the same 4 RL-data problems; the midtraining re-aggregation flags the same 3, plus aime2026_01 in both | reproduces |
| RL's template, T 1, top-p 1, 16,384; vLLM 0.11 bf16, n-gram speculation | same in every meta file and vLLM engine line | reproduces |
| "gate: 1.36×, outputs unchanged" | 1.36×; pass@1 and length differences have CIs containing 0 | the gain reproduces; **"outputs unchanged" overstates**: the gate shows no detectable change, and speculative sampling is exact only in exact arithmetic |
| pass@1 / 8 / 16 table | base 0.094 / 0.364 / 0.458; step_0500 0.304 / 0.506; step_2800 0.419 / 0.627 | reproduces. step_2800 pass@8 is 52/83 = 0.6265, written 0.626. CIs differ by ≤ 1 bootstrap step (2,000 vs my 10,000 resamples) |
| "RL raises pass@1 4.5×" | 4.46× | reproduces |
| "at k = 8 step_2800 gains 22.8 expected problems and loses 1.0" | 22.77 / 1.00 | reproduces |
| step_0100 on a random 42-problem half: pass@1 0.30 (base 0.12), at 4–9 × 10⁻⁵ of pretraining | 0.301 vs 0.116; axis 4.15e-5 – 8.56e-5 | reproduces (n = 1 RL run, 42 problems) |
| "all 17 … were solved by the base when re-sampled, at draw 18–383 (median 73)" | the same 17, the same draws | **reproduces under RL's verifier**. Read by hand, the 17 resolving solutions are 10 sound, 6 flawed but arriving, 1 a guess (aime2024_20) — see the Verdict |
| "the 3 problems the base solved and step_2800 did not fell to step_2800 at draws 12–280" | 12, 53, 280 | reproduces under the verifier. **The draw-280 success (aime2025_14) is a guess**: it computes m+n+p = 34, then boxes 60 |
| strong reach 0, reverse 0 | 0, 0 (also under `main`) | reproduces |
| "RL's solutions are in the base's support": all 78 late-solved RL solutions inside the base's range; per-token gap 0.057 (step_2800) and 0.006 (step_0500) | 100 % under all three of my control definitions; 0.057 and 0.006 | numbers reproduce; **the wording needs the criterion**: it is the pre-registered per-token range. The whole-solution gap is a median 731 nats at step_2800 |
| candidates no closer by n-gram (p = 0.33); by embedding 0.71 vs 0.65 (p = 0.02) | 0.082 vs 0.066, p 0.33 (two-sided); 0.706 vs 0.653, p 0.018; my own n-gram measures show no excess | reproduces from the stored statistics. I did not recompute the embeddings; the check was not pre-registered |
| Expectations vs outcomes (5 items) | the 5 items reproduce | **incomplete**: see the misses row below |
| verdict by the rule: inconclusive, k = 8 gap 0.26 [0.18, 0.35] | inconclusive; 0.262 [0.179, 0.352] | reproduces |
| "By reach: elicitation only, up to 512 samples" | reach 0 at K ≤ 512 under `rl` | stands as an informal reading **under RL's verifier**; needs the aime2025_14 and confirmation caveats (Verdict) |
| deviations: step_0100 half, confirmation 24 → 16 / 8, aime2025_22 symmetry, base phase-F texts lost | all seen in the artefacts | reproduces, but **incomplete**: see the deviations row below |
| cost $39.36 of $50, 26.5 pod-hours | balance delta $39.36 (log); `podbudget` $40.26; 26.52 h | reproduces. The two dollar figures are the balance delta and podbudget's estimate |
| 32B memo ≈ $110–320 | M0's fixed phase ($55) reproduces from the memo's inputs; the rest is a model | a projection; not derivable as a measurement |

The **misses** the expectations line omits (§15):
- base pass@8 0.364 against 0.12–0.28, and base pass@16 0.458 against 0.18–0.35;
- step_2800 pass@8 0.627 against 0.25–0.50;
- step_0100 pass@1 0.30 against "base ± 0.03";
- step_0100 length 2.0× against "± 20 %";
- step_0500 → step_2800 entry growth +8.7 [3.0, 15.2], against "within noise".

The step_0100 misses are informative: most of the change happens in the first 100 steps.

The **deviations** the write-up does not list:
- extension chunks of 16, not the pre-registered 32 (in the log);
- no confirmation and no likelihood phase for step_0100;
- likelihood controls on the same problems plus contaminated AIME 2023, against "on other problems" (harmless, §9);
- the weight-distance rows absent from the artefact;
- the templated-relatives sensitivity, promised in the log (05:20), never reported. Its effect is ≤ 0.015 on any pass@k and none on reach.

The write-up is 476 words by `wc` including the table; the brief's limit is 400 words plus figures.

### `numbers.md` § olmo-rlzero-pilot (labelled UNREVIEWED)

| claim | my value | verdict |
|---|---|---|
| base `main` = `stage3-step11921`, 7.30 B | identical shard LFS oids | reproduces |
| Stage 0 and gate numbers | identical; gate CIs within bootstrap noise | reproduces |
| pass@2 / pass@4 / pass@1 by set / solved in F (38, 42, 52) / mean tokens and cut (90 problems) | 0.165 / 0.261 (base), 0.373 / 0.435, 0.491 / 0.556; the same by-set values; 38 / 42 / 52; 5,872 (15.3 %), 11,790 (25.1 %), 11,712 (17.8 %) | reproduces |
| paired pass@8 difference 0.262 [0.176, 0.348] | 0.262 [0.179, 0.352] | reproduces |
| the 17 candidates "solved all 17 … every one is a complete solution of 4,071–16,384 tokens with a correct 'Answer:' line (`ansline` agrees)" | **none of the 17 has an `Answer:` line**. All box the right integer, so `ansline` agrees through its `\boxed{}` fallback. 2 are cut at 16,384 tokens (aime2025_21, aime2025_25). By hand: 10 sound, 6 flawed, 1 guess | **differs**: "complete solution" and "correct 'Answer:' line" are not true of these samples |
| reverse candidates "solved all 3 (first correct draw 53, 12, 280; the base's were 14, 73, 10)" | the same draws | reproduces (the order is 29 / 22 / 14, not the listed 29 / 14 / 22). The draw-280 success is a guess |
| under `ansline` aime2025_14 becomes step_2800 reach; the base's only success is a 549-token response with no `Answer:` line, text lost | same; also: the verifier credits a restated `$\angle B=60^\circ$` (demonstrated), and step_2800's own success there is a guess | reproduces; **the conclusion goes further**: on the evidence neither model solves aime2025_14 |
| confirmation: step_2800 ≥ 1 fresh correct on 14 of 16; step_0500 5 of 8 | 14 / 16, 5 / 8 | reproduces |
| likelihood: range [−0.936, −0.246], medians −0.546 / −0.492, 100 % inside, gaps 0.057 / 0.053 / 0.006 / 0.006, whole-solution 731 / 388 / 76 / 46, p < 10⁻³ share 0.19–0.26 % | all identical (the share is the per-group medians for late and ckpt_other) | reproduces |
| nearest RL prompt; compute axis | as above; identical to 4 significant figures | reproduces |
| step_0100 table (42 problems) | pass@k and entries/exits identical. The mean-tokens column mixes phases: for step_0500 and step_2800 it averages F + C + E samples per problem (10,918 / 10,992); phase F alone gives 10,998 / 10,970 | reproduces; label the length column |
| per-arm compute (GPU-h, tokens, samples) | re-derived for base F 3.04 / extension 4.28, step_2800 F 3.58 / C 1.51 / E 1.97; registry rows equal the meta files | reproduces. The void runs record 0 generated tokens, but F_s0100b's log shows ≈ 2.05 M (R6) |
| pods and dollars; lost texts listed | `podhours.log` rates and hours match; the lost texts are listed exactly as found | reproduces |

### `olmo_pilot/plain_summary.md` and `decision_32b.md`

| claim | my value | verdict |
|---|---|---|
| plain: 9 % → 30 % → 42 % on one attempt; 36 % vs 63 % at 8 | 0.094 / 0.304 / 0.419; 0.364 / 0.627 | reproduces |
| plain: the base solved all 17 "with complete worked solutions, not lucky guesses" | 10 sound, 6 flawed, 1 guess (aime2024_20, the base's only success there); 2 truncated | **not supported** |
| plain: the RL model solved the 3 reverse problems with more attempts | its aime2025_14 success is a guess | needs the caveat |
| plain: "every correct RL solution falls inside the range of the base's own correct solutions" | 213 of the RL checkpoints' 718 successes were scored. ckpt_other is 90 % inside the range of the base's own extension solutions; 100 % only once the AIME 2023 pilot is added | **overgeneralised**: say "every scored RL solution …, against the base's own solutions including the AIME 2023 pilot" |
| plain: "about 5 % less probable per token" | e^0.057 = 1.059 | reproduces |
| plain: "inconclusive only because one clause asked the base to match RL at 8 attempts, which sharpening alone never does" | the clause fails (0.262 [0.179, 0.352]) | the fact reproduces; "never" is too strong |
| memo §1 price table ($0.69, $0.51, $0.50, $0.53, $0.75 per M tokens; likelihood $0.03) | identical from the meta files and billed rates | reproduces |
| memo: 32B architecture (64 layers, 16 full + 48 sliding, 8 KV heads × 128) | `config.json` of `Olmo-3.1-32B-Think` | reproduces |
| memo: 3.1 `step_0050 / 0300 / 0750` = Olmo 3 `step_050 / 300 / 750`; Olmo 3 `main` = `step_750` | I checked `step_0300`, `step_0750` and `main`: 14/14 identical LFS oids each | reproduces (checked 3 of the 4 identities) |
| memo: 32B RL settings `olmo_thinker`, T 1, 32,768 tokens, 64 × 8 | `32b_think_rl.sh` at bb58c66 and at `main` | reproduces |
| memo: 14 % of GPU-hours; the step-750 FLOP bounds 1.8e-3 – 7.4e-3 | rl-compute-share `REVIEW.md` and `compute_table.csv` (Olmo 3 Think 32B row) | reproduces; the inherited numbers carry their model label |
| memo: "every price … measured …; none is a catalogue price" | the B200 ($5.98/h) and 2 × H100 ($5.38/h) rates were never billed in this pilot | minor wording |
| memo: AIME 2024 "three variants in the RL data, three verbatim in midtraining" | the midtraining containments are 1.00, 0.82 and 0.52 | "three in midtraining", not all verbatim |
| memo: "2 of step_2800's 16 candidates and 3 of step_0500's 8 had no fresh success" | 2 / 16, 3 / 8 | reproduces |

### Model labels, wording and pre-registration

- **Model labels.** Every number names its model: base, `step_0100` / `0500` / `2800`, or the Olmo 3.1 Think 32B
  rows, which are inherited and labelled. No unlabelled number was found.
- **n and strong words.** There is one RL run (AI2's), so every RL claim is n = 1 trajectory. The plain summary says
  so ("One model, one RL run, 83 problems"). The words to soften are "never" in "sharpening alone never does" and
  "genuinely new problems never appeared". Each holds only at ≤ 512 samples on 83 problems, and the latter only under
  RL's verifier.
- **The pre-registration** came before the pods (Part A) and before any evaluation sampling (Part B). The budget rule
  cutting confirmation was declared at 07:56, before any C or E result. The step_0100 half was declared at 08:56,
  before any step_0100 result was used. Misses are reported as misses where reported, but the list is incomplete (see
  above).
- **AGENT_POLICY items with gaps.**
  - The write-up has no per-arm compute table. It is in `numbers.md` as prose, and that is also where the base's
    > 1.25× samples are flagged ("by design").
  - The pre-registration states no minimum detectable difference for its headline quantity.

# §Verdict

**Stands** (under RL's verifier, the pre-registered primary grade, on 83 AIME 2024–26 problems; models: base
`Olmo-3-1025-7B` `main`, RL-Zero-Math `step_0100` / `0500` / `2800`, 7.3 B, pretrained):
- **pass@k and dynamics.** Every pass@k, the matched-k entries and exits, and the compute axis reproduce. Their source
  table (`results.csv`) equals my table built from the raw rows, and all 4,572 stored texts re-grade identically.
- **The 17 candidates.** All 17 RL-only solves were credited to the base by RL's verifier within 383 samples (median
  73). Strong reach, reach and reverse are all 0 at K ≤ 512.
- **The verdict.** The pre-registered verdict is "inconclusive", correctly derived and correctly reported.
- **Likelihood.** The 78 late-solved RL solutions sit inside the base's per-token log-probability range.
- **Contamination.** The exclusions are right under the stated rule: my independent Dolci scan agrees, and so does the
  midtraining re-aggregation.
- **Spend.** $39–40 of $50. No hard-constraint violation.

**Must be reworded:**
1. **"Complete solutions" (plain summary and `numbers.md`).** The claims "with complete worked solutions, not lucky
   guesses" and "every one is a complete solution … with a correct 'Answer:' line" are wrong. Replace them with the
   hand-check:
   - Of the 17 resolving base solutions, 10 are sound, 6 reach the official answer through a flawed step, and 1
     (aime2024_20) is a guess.
   - None has an `Answer:` line; all box their answer, and 2 are cut at 16,384 tokens.
   - On aime2024_20, all 5 RL successes are guesses too. On aime2026_26, all 5 share the base's gap: none verifies the
     seven-value count.
2. **aime2025_14.** Say that step_2800's draw-280 success is a guess: it computes 34, then boxes 60. The base's only
   credit there is probably the verifier accepting a restated 60° angle (its text is lost). So on the evidence neither
   model solves aime2025_14. The reverse count stays 0, but not because step_2800 can solve it.
3. **"In the base's support".** Qualify it as the pre-registered per-token range. Add the whole-solution gap: a median
   731 nats for step_2800's late-solved solutions. Change "every correct RL solution" to "every scored RL solution
   (213 of 718), against the base's own solutions including AIME 2023".
4. **"Outputs unchanged"** (write-up and memo) → "no detectable change in pass@1 or length (exact speculative
   sampling)".
5. **Expectations vs outcomes.** Add the five omitted misses (§Compare), especially step_0100's: pass@1 already 0.30,
   and 2× length at 4–9 × 10⁻⁵ of pretraining compute.
6. **Smaller items.**
   - Label the step_0100 table's length column.
   - Put the 7 weight-distance pairs into an artefact, or call them log-only.
   - Report or drop the promised templated-relatives sensitivity.
   - Fix the memo's "three verbatim" and "none is a catalogue price".
   - Change "sharpening alone never does" to "generally does not".

**Not supported:**
- "Not lucky guesses" (above).
- Any reading of "reach 0" stronger than **"credited by RL's verifier"**. A single base success removed 16 of the 17
  candidates from reach: only aime2025_25 had 2 base successes. RL's strong reach needed ≥ 2 successes including a
  fresh one. The rule is asymmetric, and one of those single base successes is a guess.

  This weakens no number. It limits the inference: "the base can do everything RL can" is shown at the level of the
  verifier's credit. At the level of sound derivations it is shown for 10–16 of the 17 problems. On the other two the
  RL solutions are no better.

**Next measurements that would settle what is left open:**
1. **Confirm the base's resolutions symmetrically** (≈ $6–9 at this pilot's measured $0.50–0.75 per M tokens).
   - Re-sample the base on the 17 candidates until a second `rl`-correct success, up to 512. That is about 1,650
     samples, since the first-success positions sum to 1,647, at ≈ 7,200 tokens each.
   - Re-sample it on aime2025_14 (256 samples).
   - Hand-check each resolving solution, or grade it with a final-answer-only reading. This would turn "credited"
     into "confirmed", and it uses the same rule as RL's confirmation.
2. **Change the 32B design.** Add to it:
   - a pre-registered secondary grade that reads only the response's final stated answer;
   - a blinded hand-check (or a judge) of every candidate-resolving solution;
   - the symmetric confirmation rule above.

   Without these, a verifier that credits a restated angle, plus AIME's 0–999 integer answers at base budgets of
   hundreds of samples, can manufacture "base solves it".
