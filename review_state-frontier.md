# Review — run `state-frontier` (reviewer, 2026-09-29)

Reviewer session, independent of the executor. Phase 1 ran in `~/review/state-frontier` (executor write-ups
removed) using only the brief, `preregistration/state-frontier.md`, code, data, raw artefacts, and the bucket
dumps `hf://buckets/dan-pandori/nd-rl/state-frontier/artifacts/sf2/dumps/` (literal sampled text + verdict, one
file per job). All recount code is mine and lives in `review_sf/`: `rv_lean.py` is my own Lean harness (my own
statement translator; the literal stored text is the tactic body; any Lean error or warning, or any axiom outside
{propext, Classical.choice, Quot.sound}, rejects; `sorry`, `axiom`, `#`, … reject outright), `rv_resample.py`
covers design A, `rv_splits.py` covers disjointness, and `rv_misc.py` covers Q1 readings, truncation, the lottery,
ladders and negative controls. Lean 4.34.1 on the VPS (the pods ran 4.34.0). Outputs are `review_sf/resample.json`
and `review_sf/ladders.json`.

**Model labels used below.** All models have 4 layers, d 256, 8 heads, and are trained from scratch. Stage-1 used
`data/p2/train_depth3_f0_a1.jsonl` (155,000 records, cap 6, md5 `29276f24…`, the same file in every worktree).
- **S**: `lean_state`, 3,216,384 params.
- **SN**: `lean_staten`, `Env(assign=True)`, 3,216,384 params.
- **C0**: whole-proof `lean_seq`, 3,214,336 params.
- **G1**: whole-proof `lean_seq`, trained on `train_g1` (155,000), 3,214,336 params.

T1 is the 8-round state or whole-proof expert-iteration ladder (r8 checkpoint). The `src_ckpt` of every
re-sample job matches the pre-registration's table. I did not re-derive parameter counts (no torch on the VPS).

## §Recount

### Hard constraints — all pass
- `nd_verify` tree hash is `9437bb72…`, the same in HEAD and `origin/main`. The run's diff against its base
  `d90da191` does not touch `nd_verify`.
- `artifacts/TEST_RUN_DONE` blob is `1d5cf064…`, the same in HEAD, `origin/main` and `origin/dan`.
- **`nd_verify` is not used as a judge.** The run's only code changes are `eval_set.py` (a `--max_new` flag and
  a truncation counter), `sf_analysis.py`, `sf_figures.py` and `pod/sf/*`. None imports or calls `nd_verify`. The
  `lean_ok` verdicts in the dumps come from `lean_gate`. My Lean re-check agrees with them on every row I sampled
  (below).
- **No evaluation file is read for training.**
  - `state_train.py` reads `--heldout` only for a validation loss (first 2,000 rows). That code predates this run
    and was not changed by it.
  - `state_ladder_ei.py` trains only on target finds and excludes every transfer, held-out, validation-36 and
    reserve key (`eval_keys`, lines 201–205).
  - The transfer pool is sampled for evaluation only.
- The pre-registration was committed once (`20dfa0f1`, 18:23 UTC), before the first job. The first re-sample dump
  finished at 18:40 after a 292 s wall, so it started at about 18:35.

### Split disjointness — by renaming class, my own canonicaliser
I checked two class definitions: order-sensitive (premises in order, then goal) and order-insensitive (distinct
premises, minimum over permutations).

| training file | vs `sf2/long` (224) | vs `ladder/transfer` (2,285) | vs `p2/heldout` (5,000) |
|---|---|---|---|
| Stage-1 `train_depth3_f0_a1` | 0 / 0 | 0 / 0 | 0 / **21** |
| ladder `rl_targets` (T1 training) | 0 / 0 | 0 / **2** (`la_transfer_307`, `_842`, L 9) | 0 / 0 |
| G1 `train_g1` | 0 / 0 | 0 / 0 | 0 / 22 |

Only the order-insensitive definition finds any overlap. The 21 held-out overlaps are proofs of 3–6 lines, none of
them depth-3, so the lottery slice is clean. The two transfer overlaps are at L 9, outside `long`. The pool
`data/sf2/long.jsonl` is exactly the 224 transfer theorems with `L_true` ≥ 11 (99 / 102 / 13 / 10 at 11 / 12 / 13 /
14; prompts match `transfer.jsonl`). The pool is clean.

### Lean re-check (literal stored text, my harness)
- **Negative controls: 201 / 201 rejected.** The mutations were: text truncated at half, wrong final `exact`, text
  paired with another theorem, `.1`→`.2` / `inl`→`inr` flips, and appended `sorry`.
- **Rejected rows:** 30 rejected rows per re-sample model, 780 in all. Every one was also rejected by my harness.
- **Re-sample (A), 26 jobs:**
  - Every distinct accepted text at `L_true` ≥ 13 was re-checked: 575 texts, 575 accepted.
  - Plus 100 random accepted texts per job (all of them where fewer exist): 1,768 accepted, 0 rejected.
  - Per arm, well over 100: S T1 400 + 300 at ≥ 13; SN T1 200 + 271; C0 T1 300 + 2; G1 T1 168; S base 330; SN
    base 370 + 2 at ≥ 13.
  - The accepted-theorem set in the dump equals the `n_ok > 0` set in `rs/*.jsonl` for all 26 jobs, with 0
    mismatches.
- **Ladders, the 8 new runs:**
  - The theorems with a Lean-accepted transfer text in each dump equal the cumulative `found_transfer_8.jsonl`
    names exactly (symmetric difference 0). For `la_frozen_SN_s5` the comparison is at round 5.
  - 100 random accepted texts per ladder, plus every text at ≥ 13 (59): **859 / 859 accepted.**
- **Held-out greedy for the lottery, 6 new seeds:** the dump agrees with `heldout_*.jsonl` on every theorem (0
  mismatches). 100 depth-3 accepted texts per seed: **600 / 600 accepted.**
- **No counted proof that I checked was rejected by Lean.** One caveat: the dumps store *distinct* texts, so I
  checked distinct proofs. The success counts `n_ok` come from `rs/*.jsonl`. I confirmed that
  `n_ok = 256 − len(reasons)` on every row, and that no theorem has more distinct accepted texts than `n_ok`.

### Design A — re-sample of the 224 `L_true` ≥ 11 theorems, k = 256, T 0.8, seed 0
The table uses my recount. "Trunc" is the share of samples that hit a length cap (`action truncated`, `step cap`,
or `eof`), taken from per-sample reasons, per stratum.

| model | N13 | succ ≥13 | rate ≥13 | solved 11–12 | trunc 11–12 | trunc ≥13 |
|---|---|---|---|---|---|---|
| T1 S s0 | 1 | 7 | 0.0012 | 40 | 0.002 % | 0 |
| T1 S s1 | 3 | 188 | 0.0319 | 40 | 0.017 % | 0.034 % |
| T1 S s2 (new) | 4 | 13 | 0.0022 | 57 | 0.004 % | 0 |
| T1 S s3 (new) | 3 | 143 | 0.0243 | 70 | 0.008 % | 0 |
| T1 SN s0 | 5 | 269 | 0.0457 | 67 | 0.049 % | 0 |
| T1 SN s1 | 1 | 129 | 0.0219 | 48 | 0.010 % | **0.170 %** |
| T1 C0 s0 | 1 | 2 | 0.0003 | 21 | (0.08 % eof) | 0.017 % |
| T1 C0 s1 (max_new 512) | 0 | 0 | 0 | 21 | 144 hit max_new overall (0.25 %) | ? |
| T1 C0 s1 (max_new 1,024 re-run) | 0 | 0 | 0 | 22 | 42 hit overall (0.07 %) | ? |
| T1 G1 s0 / s1 | 0 / 0 | 0 | 0 | 19 / 6 | 11 / 51 hit overall | ? |
| base S s0 / s1 / s2 / s3 (max_action 256) | 0 / 0 / 0 / 0 | 0 | 0 | 5 / 3 / 6 / 14 | **0.225 %** / 0.056 / 0.012 / **0.187 %** | 0 / 0.017 / 0 / 0 |
| base S s0 / s3 re-run at max_action 512 | 0 / 0 | 0 | 0 | 3 / 17 | 0.078 / 0.041 % | 0 |
| base SN s0 / s1 / s2 / s3 / s4 / s5 | 0 / 0 / 0 / 1 / 0 / 0 | s3: 1 | — | 10 / 6 / 6 / 10 / 2 / 6 | s3 **0.356 %**, others ≤ 0.019 % | s4 **0.476 %**, s1 0.034, s0 0.017 |
| base SN s3 re-run at max_action 512 | 1 | 1 | — | 13 | 0.002 % | 0 |
| base C0 s0 / s1 | 0 / 0 | 0 | 0 | 0 / 0 | 0 / 45 hit overall | ? |

Whole-proof jobs store only the overall `hit_max_new`. Their per-stratum truncation is **not derivable**
from the artefacts ("?").

**Truncation findings, checked against the pre-registered rule "> 0.1 % in a reported stratum → re-run":**
- **base SN s4 at ≥ 13 (0.476 %) was not re-run.** 28 of its 5,888 samples in that stratum were cut off, and its
  N13 = 0 is therefore capped by the length limit.
- **T1 SN s1 at ≥ 13 (0.170 %) was not re-run.**
- base S s0 / S s3 / SN s3 at 11–12 were re-run at `max_action` 512. After the re-run, the ≥ 13 results are
  unchanged and 11–12 moves by −2 / +3 / +3.
- C0 s1 was re-run at `max_new` 1,024. It went from 21 to 22 solved at 11–12, and 42 rows still hit 1,024.
- The state `step cap` (48 steps) is also a length cap. It hit 24 samples of T1 SN s0 and 4 of T1 S s3, all at
  11–12, all below 0.1 %.

**Q1, my own readings against the pre-registered rules:**
- **Rule "a real, low rate" (≥ 3 distinct ≥ 13 theorems, each solved by ≥ 2 of the 6 state T1 finals): holds.**
  Four theorems qualify. The counts below list successes out of 256 per model, in the order S s0–s3, SN s0, SN s1.

  | theorem | L_true | successes /256 | models that solve it |
  |---|---|---|---|
  | 1126 | 13 | 7 / 127 / 4 / 2 / 48 / 129 | 6 |
  | 1198 | 13 | 0 / 60 / 3 / 139 / 165 / 0 | 4 |
  | 978 | 14 | 0 / 0 / 5 / 2 / 4 / 0 | 3 |
  | 735 | 13 | 0 / 1 / 1 / 0 / 5 / 0 | 3 |

  1696 (L 14) is solved by T1 SN s0 only (47). The "one lucky theorem" rule fails: 1126's share of the 749
  state-T1 successes at ≥ 13 is **0.423**, against the rule's 0.80.
- **735 is thin.** Two of its three models solved it once in 256.
- **978 is base-reachable.** It was reached by base SN s3 (1 / 256, in both the 256 and 512 runs) and by the
  **frozen** SN s3 ladder. That leaves 1126, 1198 and 735 as ≥ 13 theorems that no state base reached (10 bases ×
  256 attempts) and that no frozen ladder reached (S s0–s3, SN s0–s5). 1126 was also reached by T1 C0 s0 (2 / 256).
- **Pooled state-T1 success rate at ≥ 13 is 749 / 35,328 = 2.12 %** (S alone 1.49 %). The pre-registered
  expectation was 0.1–1 %, so this is a miss on the high side. It is dominated by 1126 and 1198, which together
  account for 684 of the 749 successes.
- **Sign test, state T1 vs C0 T1, per theorem.** Counts are per-model means; ties are excluded.
  - At ≥ 13: state better on 5 theorems, C0 on 0; **p = 0.0625**, not significant at 0.05.
  - At 11–12: 86 vs 7, p = 2 × 10⁻¹⁸.
  - Using C0 s1 at max_new 512 or at 1,024 makes no difference.
- **N13 per state T1 final:** 1, 3, 4, 3, 5, 1 (median 3). The expected range was 2–6: 4 of 6 seeds fall inside it,
  and S s0 and SN s1 fall below. 1126 is solved by all 6 ✓.
- **Other pre-registered expectations:**
  - C0 T1 N13 of 1 / 0 (expected 0–1) ✓; G1 0 / 0 ✓; state bases 0–1 ✓; C0 bases 0 ✓.
  - At 11–12: state T1 40–70 (expected 40–100) ✓; C0 T1 21 / 22 (expected 15–45) ✓; C0 bases 0 ✓.
  - **State bases at 11–12: S 3–17, SN 2–13. The expected range was 10–40, so most seeds fall below it — a miss.**
- **Length of the ≥ 13 proofs.** Every accepted proof's ND denotation has at least `L_true` lines (13 or 14), so
  the labels are not beaten under Lean on these theorems. Lean line counts (`have` + `exact`) are 8–13 and term
  sizes 33–100. My term-size definition: proof-term tokens after deleting every type ascription. Minimum per
  theorem: 1126 = 33, 735 = 35, 1198 = 36, 978 = 41, 1696 = 42. C0's 1126 proofs have the same minimum (33).

### Design B — ladders (cumulative transfer after 8 rounds; L* = largest L with ≥ 5 solved at `L_true` ≥ L)

| arm | per seed (solved) | L* | ≥ 13 names | IQM [my 95 % bootstrap] | sd |
|---|---|---|---|---|---|
| T1 S (s0, s1 on file; s2, s3 new) | 1,348 / 1,389 / 1,546 / 1,630 | 12 × 4 | {1126}, {1126, 1198}, {1198, 735, 978}, {1126, 1198, 735, 978} | 1,467.5 [1,348, 1,630] | 132 |
| frozen S | 779 / 787 / 858 / 996 | 11 / 10 / 11 / 11 | none | 822.5 [779, 996] | 100 |
| T1 SN (on file) | 1,557 / 1,403 | 12 / 12 | {1126, 1198, 978}, {1126} | — (n = 2) | 109 |
| frozen SN, s0–s4 at 8 rounds | 975 / 801 / 841 / 1,009 / 723 | 11 / 11 / 11 / 11 / 10 | s3: {978} | 869.2 [746, 999] | 120 |
| frozen SN s5 | **759 after 5 rounds only** | 11 | none | | |

- **Against the expectations:**
  - T1 S L* is 12 ✓.
  - **T1 S solved: s2 = 1,546 and s3 = 1,630, above the expected 1,250–1,500 (miss, high).**
  - **frozen S: s2 = 858 and s3 = 996, above the expected 700–850 (miss, high).**
  - frozen SN: the 5 complete seeds fall in 650–1,050 ✓, IQM 869 ≈ 850 ✓, sd 120 ≤ 130 ✓.
  - **Only 5 of the pre-registered 6 SN frozen seeds completed.** s5 stopped at round 5, as the stop rule allows
    (spend 22.17 h / $10.94 of 24 h / $12, and `BUDGET_WARNING` at 19.6 h).
- Every frozen SN seed is above C0's on-file frozen range (114–158).
- **The ≥ 13 theorems the T1 ladders found:** 1126, 1198, 735, 978. Only 978 appears in any frozen ladder, and it
  is base-reachable.

### Design C — depth-3 lottery (own depth counter: max `|` depth of the reference ND proof ≥ 3; 500 theorems, identical to `pat.depth3`)
- **New seeds, held-out greedy depth-3 rate:**

  | seed | S s2 | S s3 | SN s2 | SN s3 | SN s4 | SN s5 |
  |---|---|---|---|---|---|---|
  | rate | 0.936 | 0.960 | 0.944 | 0.934 | 0.908 | 0.924 |

  **All 6 are in the high mode (> 0.44); the falsifier does not fire.**
- On-file state-env seeds, same predicate: S 0.922 / 0.882, SN 0.956 / 0.902, SH 0.860 / 0.880. 12 / 12 in all.
- Wilson intervals: 12 / 12 gives [0.758, 1.00]; 6 / 6 new gives [0.610, 1.00]. Under the control's P(high) =
  0.462, P(6 / 6) = 0.0097. (I did not recompute the control's 0.462 or its Wilson interval [0.333, 0.595]; they are
  inherited from `NOISE_FLOOR.md`, which measured whole-proof `lean_seq` Stage-1 models.)
- The spread of depth-3 rates across the 12 state seeds is sd 0.031, against the predicted < 0.05 ✓.
- Held-out overall: S s2 0.960, S s3 **0.882** (84 `unbound`-name failures), SN 0.955–0.971. The expected range was
  0.80–0.97 ✓.

## §Compare (phase 2: `run_state_frontier.md`, `numbers.md` § state-frontier, `log.md`, read after the §Recount commit `ed0da394`)

| # | claim (source) | my independent value | verdict |
|---|---|---|---|
| 1 | Six state T1 finals solve **5 distinct** of the 23 ≥ 13 theorems; 4 of them are solved by ≥ 2 finals (run) | 5 (1126, 1198, 735, 978, 1696); 4 of them by ≥ 2 finals | reproduces |
| 2 | Per-final N13: S 1 / 3 / 4 / 3, SN 5 / 1; successes 7 / 188 / 13 / 143 / 269 / 129 (numbers) | identical | reproduces |
| 3 | `1126` carries 42 % (317) of 749 successes (run, numbers) | 317 / 749 = 0.423 | reproduces |
| 4 | Reading "a real, low rate" (run) | pre-registered rule met: 4 theorems (≥ 3 required) | reproduces. See wording item W3 |
| 5 | Pooled rate at ≥ 13: state 2.1 %, C0 0.017 % (run) | 2.12 %; C0 2 / 11,776 = 0.017 % | reproduces |
| 6 | "Stage-1 bases score 0, except SN s3 with 1 / 256" (run) | same (SN s3 solves 978) | reproduces, with one caveat: base SN s4's ≥ 13 stratum is 0.48 % cut off and was not re-run (item W4) |
| 7 | Paired by theorem, "state beats C0" at 11–12 on 86 of 93 (p = 2 × 10⁻¹⁸) and at ≥ 13 on 5 of 5 (p = 0.06) (run) | 86 / 7, p = 2.1 × 10⁻¹⁸; 5 / 0, p = 0.0625 | numbers reproduce. **Wording:** at ≥ 13 this is not significant at 0.05, so "beats" is not supported there (W1) |
| 8 | Solved at 11 / 12 per model (numbers table) | all 13 rows match (for example T1 S s3 53 / 17 = 70; C0 s1 at 1,024 16 / 6 = 22) | reproduces |
| 9 | "Cut off ≤ 0.03 %" for T1 S and T1 SN; bases ≤ 0.20 / 0.32 % (numbers) | these are **overall** fractions. By stratum: T1 SN s1 ≥ 13 = **0.170 %**; base SN s4 ≥ 13 = **0.476 %**; base S s0 / S s3 / SN s3 at 11–12 = 0.225 / 0.187 / 0.356 % | **differs in kind.** The policy threshold is per stratum. Two ≥ 13 strata exceed it and were not re-run, and three base rows exceed it at 11–12 and stay at 256 (W4) |
| 10 | C0 T1 s1 re-run at `max_new` 1,024: 144 → 42 cut off; N13 0 → 0; 11–12 21 → 22 (numbers, log) | same | reproduces. Whole-proof per-stratum truncation is not derivable from the stored artefacts |
| 11 | `max_action` 512 diagnostics: S s0 116 → 40, S s3 96 → 21, SN s3 183 → 1; N13 unchanged (numbers) | same; 11–12 moves −2 / +3 / +3 | reproduces |
| 12 | "Shortest ≥ 13 proofs: 13–14 lines, term size 8–12" (run) | ND lines: minimum = `L_true` (13 / 14) on every theorem ✓. My term size (token count after removing ascriptions) gives minima 33 / 35 / 36 / 41 / 42 for 1126 / 735 / 1198 / 978 / 1696, the same ordering as the executor's 8 / 8 / 9 / 11 / 12 | lines reproduce. The term-size values use a different definition (`lean_check`'s elaborated inference-node count), so I cannot reproduce the absolute values, but the ordering agrees. Note that they were computed on the `nd2lean` re-translation of the ND denotation, not on the literal sampled text |
| 13 | All four S ladders reach `L*` 12 with 1–4 theorems at ≥ 13 (run) | 12 × 4; 1 / 2 / 3 / 4 | reproduces |
| 14 | T1 S 1,348 / 1,389 / 1,546 / 1,630, IQM 1,467.5 [1,348, 1,630] (numbers) | identical (my bootstrap agrees) | reproduces |
| 15 | Frozen S 779 / 787 / 858 / 996, IQM 822.5; frozen SN (n = 5) IQM 869.2 [746.4, 998.8] (numbers, run) | identical | reproduces |
| 16 | Frozen SN s5 is partial (759 at round 5) and excluded (numbers) | 759 at round 5 | reproduces; correctly labelled as partial |
| 17 | Frozen SN s3 solves `978` with no RL (numbers) | yes, and base SN s3 samples it too | reproduces |
| 18 | "C0 scores 114–158" (run, floor) | on-file values; not recomputed | **unlabelled.** These are C0 frozen ladders from `ds-generator` / `noise-floor`, measured under **Lean ∧ `nd_verify`** before 2026-09-27, and the run doesn't say so (W2). `review_state-env.md` row 18 measured the checker effect on these C0 ladders as +7 / +2, so the conclusion is not at risk |
| 19 | Q2: 6 / 6 new seeds high (0.908–0.960); p = 0.0097; falsifier did not fire (run) | 6 / 6; P = 0.462⁶ = 0.0097 | reproduces |
| 20 | 12 / 12 state seeds high, Wilson [0.757, 1.00]; SD 0.032 (run) | 12 / 12, [0.758, 1.00]; sd 0.0316 | reproduces |
| 21 | Control P(high) 0.462 [0.333, 0.595] (run, numbers) | inherited from `NOISE_FLOOR.md` (2026-09-25) | **unlabelled.** The run doesn't name the control's model (3.2 M whole-proof Stage-1, 4 pools × 13 seeds) or its checker (Lean ∧ `nd_verify`, pre-2026-09-27) (W2). `review_state-env.md` measured the depth-3 checker effect on C0 as +0.000, so the comparison stands |
| 22 | "The state removes the lottery" (run headline) | 0 low-mode seeds in 12; the one-sided 95 % upper bound on P(low) is ≈ 0.24 | **reword** (W3): the data exclude the control's rate, not a lottery at up to ≈ 20 % |
| 23 | S s3 held-out 0.882, 358 of 588 failures are Lean rejections (run) | 358 `lean rejected`, 109 `exact not last`, 84 `unbound` | reproduces |
| 24 | Misses listed: N13 = 1 for two finals, pooled 2.1 %, bases at 11–12 2–14, S T1 above 1,500, frozen S above 850 (run) | the same five misses | reproduces. Misses are reported as misses. With the 512 re-draws, bases at 11–12 run up to 17; still a miss |
| 25 | Stop rule fired at 21.4 h; frozen SN s4 kept as a stated deviation; 22.17 h, $10.94 (run, log) | `podbudget` 22.17 h / $10.94; `BUDGET_WARNING` at 19.6 h | reproduces. The deviation is disclosed. The log says the 20 h line passed unnoticed |
| 26 | Pre-registration before the run (gate 0) | committed once at 18:23:14; first job about 18:35 | reproduces |
| 27 | Mixed GPUs with billed rates; peak memory recorded (numbers) | four pods with rates; peak 8.9–16.1 GB is in the job JSONs | reproduces. Batch 2,048 is not "the largest that fits" (policy), but it was pre-registered for comparability with `state-env` |
| 28 | Model labels (numbers § Models) | S / SN / C0 / G1 checkpoints, parameter counts, format, from scratch, training sets: all present | labelled correctly, except rows 18 and 21 |

## §Verdict

**Stands.**
- **Q1 (pre-registered reading "a real, low rate").** The state T1 finals solve 4 theorems at `L_true` ≥ 13
  that are each hit by ≥ 2 finals, and 1126 carries 42 % of the successes, not ≥ 80 %. Every counted proof I
  re-checked is accepted by Lean from its literal text. That is all 575 distinct ≥ 13 texts plus 1,768 others, and
  my harness rejected 201 / 201 negative controls.
- **Base reachability is reported.** 978 is base-reachable (base SN s3, frozen SN s3). 1126, 1198 and 735 were
  reached by no state base and no frozen ladder.
- **State ≫ C0 at 11–12.**
- **Q2.** 6 / 6 new state seeds are in the high depth-3 mode, and 12 / 12 overall, which excludes the control's
  P(high) = 0.462.
- **Ladder and floor numbers.** Every ladder and floor number reproduces from the found files, and the found files
  equal the Lean-accepted sets in the dumps.
- **Process.** No hard-constraint violation. The pools are disjoint by renaming class. Expectations were committed
  before the run, and the misses are reported as misses.

**Must be reworded.**
- **W1.** "At ≥ 13 on 5 of 5 (p = 0.06)" should not be read as "state beats C0" at ≥ 13. It is a non-significant
  sign test on 5 theorems. Say "5 / 0, not significant".
- **W2.** Label the inherited control numbers with their model and checker:
  - C0 frozen 114–158 and P(high) 0.462 [0.333, 0.595] come from 3.2 M whole-proof `lean_seq` Stage-1 models,
    measured under **Lean ∧ `nd_verify`**, before 2026-09-27.
  - Cite `review_state-env.md` row 18 for the size of the checker effect (≈ 0).
- **W3.** Reword "the state removes the lottery" to "no low-mode seed in 12 state seeds; P(high) ≥ 0.76 (95 %),
  against the control's 0.46". "Removes" claims a zero that 12 seeds cannot show. Similarly for "a real, low rate":
  add that 684 of the 749 successes are on two theorems, and that 735 rests on single hits (1 / 256 twice, 5 / 256
  once).
- **W4.** The "cut off" column should be per stratum, as the policy requires, not overall.
  - At ≥ 13: T1 SN s1 is 0.17 % and base SN s4 is 0.48 %. Neither was re-run.
  - At 11–12: base S s0 / S s3 / SN s3 are 0.19–0.36 %; they were re-drawn at 512 but the 256 rows were kept.
  - Report this as a deviation from the policy. The effect on reported numbers is small (N13 unchanged in the three
    re-draws; 11–12 moves by at most 3), but base SN s4's N13 = 0 and T1 SN s1's N13 = 1 are length-capped.

**Not supported.** Nothing beyond W1 and W3.

**Next measurements.**
1. **Re-run T1 SN s1 and base SN s4 at `max_action` 512.** About 10 GPU-minutes each. This closes W4 for the ≥ 13
   stratum.
2. **Per-theorem rates at ≥ 13 instead of hit counts.** Sample the 23 ≥ 13 theorems at k = 4,096 for the 6 state T1
   finals and both C0 T1 finals. Test state vs C0 per theorem with the paired per-model rates, rather than a sign test
   over the 5 theorems that k = 256 happened to solve. The current p = 0.06 is limited by the 5 theorems, not by the
   effect size.
3. **For Q2, more state seeds.** About 30 state seeds would bound P(low) below 0.1 at 95 % (0 / 30 → upper bound
   0.095). That is what "removes" would require.
4. **Store per-sample `hit_max_new` flags in `eval_set.py` rows,** so that whole-proof truncation is auditable per
   stratum.
