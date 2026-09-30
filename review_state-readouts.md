# Review — state-readouts (reviewer: agent:claude, 2026-09-30)

Scripts and outputs: `artifacts/state-readouts/review/` (all written by the reviewer; none of the executor's analysis
code was run). Phase-1 workspace `~/review/state-readouts` (executor write-ups removed). Lean 4.34.1, core only.

**Models** (all from scratch, 4 layers, d 256, sampled at batch 4,096, fast decode path):
- Part A: **S** = `ckpts/sr/stage1_S_s{0,1}.pt` (`lean_state`, md5 `226b3d…` / `c89baf…`), **SH** =
  `ckpts/sr/stage1_SH_s{0,1}.pt` (`lean_stateh`, md5 `b8d6e9…` / `9ad2b7…`) — Stage-1 bases, 3,216,384 params
  (pre-registration), trained on `data/p2/train_depth3_f0_a1.jsonl`, cap 6. **SN** (inherited, `lean_staten`,
  `ckpts/se/stage1_SN_s{0,1}.pt`, same training set) — re-counted here from `origin/dan_support-state:artifacts/ss/`.
- Part B: **T1** = `ckpts/sr/la_T1_SN12_s{0-3}_r8.pt` and **Fz** = `stage1_SN12_s{0-3}.pt` (`lean_staten`,
  3,216,384 params, from scratch on `data/kh/train_k12.jsonl`, cap 12; T1 = + 8 ladder EI rounds on
  `data/ladder/rl_targets.jsonl`, per `state-cap12`'s `args.json`).

## Recount (phase 1, before reading the write-up)

### Part A — survivors reached (≥ 1 Lean-accepted attempt at T 0.8 or T 1.0), out of 29

Counted two ways that agree on every theorem: from the per-theorem rows (`H_*.s0.jsonl`, `n_ok`) and from the
Lean-gate dumps (`dump/H_*.jsonl.gz`, any `lean_ok` text for the theorem's prompt).

| arm | seed | reached | T 0.8 only | T 1.0 rows needed / run | median p̂ (T 0.8, unreached = 0) | attempts | `max_action` hit | step cap hit |
|---|---|---|---|---|---|---|---|---|
| S | s0 | **28** | 25 | 6 / 6 | 0.0054 | 2,568,640 | 0.042 % | 0 |
| S | s1 | **25** | 25 | 10 / 10 | 0.0144 | 3,941,376 | **0.753 %** | 0 |
| SH | s0 | **21** | 17 | 15 / 15 | 2.0e-5 | 6,066,944 | **0.297 %** | 0 |
| SH | s1 | **≥ 15** | 13 | 16 / **10** | 0 | 5,433,472 | **0.572 %** | 0 |
| SN (inherited) | s0 | 28 | — | — | 0.188 | — | 0.0005 % | — |
| SN (inherited) | s1 | 28 | — | — | 0.0088 | — | 0.055 % | — |

- **SH s1's T 1.0 phase is incomplete** (`A_SH_s1.fail`; log ends `Terminated` in theorem 11 of 16). Six theorems
  that failed at T 0.8 (200,000 attempts each) got no T 1.0 attempts: la_transfer_1858, 1893, 1932, 2038, 454, 87.
  SH s1's 15 is a lower bound; the protocol-complete value is unknown.
- Unreached: S s0 {1893}; S s1 {100, 1729, 588, 87}; SH s0 {1004, 1110, 149, 1858, 1893, 2038, 454, 87};
  SH s1 {100, 1004, 1110, 1437, 149, 1729, 1858, 1893, 1932, 2038, 381, 454, 588, 87}.
- Every theorem any S / SH seed reaches is reached by SN on the same seed or the other (A5: 0 exceptions; SN union
  29 / 29). Same-seed SN-reached-but-arm-missed: S s0 0, S s1 4, SH s0 7, SH s1 13.
- Settings checked from the rows: batch 4,096, `max_chunk` 8, `max_action` 256, `max_steps` 48, sampling seeds 1 / 2
  (s0) and 11 / 12 (s1) — identical to SN's in `support-state`.
- **Length caps (A6).** Step cap: 0 hits anywhere. Action cap: above the pre-registered 0.1 % on S s1, SH s0, SH s1.
  Concentrated in a few theorems; the unreached ones with heavy truncation: S s1 la_transfer_100 (5.7 % at T 0.8,
  8.7 % at T 1.0), SH s1 la_transfer_1858 (14.4 %, no T 1.0), SH s0 la_transfer_1004 (0.57 % / 1.40 %).
  The diagnostic `Hdiag_S_T08_ma1024_s1` (S s1, T 0.8, seed 11, `max_action` 1024) re-sampled S s1's four unreached
  theorems at 200,000 each: 0 accepted, 0 truncated. So truncation did not hide S s1's misses. No such diagnostic
  exists for SH (1858 on s1, 1004 on s0).
- Reading by the pre-registered bands (mean over seeds): S 26.5 → state band (≥ 20). SH 18.0 (≥ 18 with the
  lower bound) → middle band. The arms fall in different bands, so the pre-registration requires the reading per arm.
- Sizes of the distinct accepted proofs (my own measures from the Lean text: `have` count; term size = proof-term
  nodes with type ascriptions removed): median lines / term size S s0 7 / 21, S s1 6 / 21, SH s0 6 / 20,
  SH s1 6 / 20 (n = 69, 58, 35, 28 distinct normalised proofs). The rows' `term_size` field is a different quantity
  (formula nodes summed over the ND lines, premises included: medians 85 / 79 / 75 / 80).

### Part B — k 256, T 0.8, seed 0, `max_steps` 96, `max_action` 512, batch 4,096

Solved theorems (≥ 1 of 256 accepted). Rows, summary files and dumps agree on every file.

| ckpt | textbook transfer / 760 | dead schemata ≥ 5 / 12 | excluded_middle | `transfer_long` / 282 | long schemata ≥ 5 / 6 | action-cap hit (tb / tbl) |
|---|---|---|---|---|---|---|
| T1 s0 | 513 | 11 | 1 | 102 | 4 | 0.020 % / 0.006 % |
| T1 s1 | 552 | 11 | 0 | 125 | 4 | 0.002 % / 0.012 % |
| T1 s2 | 537 | 11 | 1 | 111 | 5 | 0.002 % / 0.004 % |
| T1 s3 | 514 | 11 | 1 | 113 | 4 | 0.002 % / 0.044 % |
| Fz s0 | 275 | 6 | 1 | 35 | 3 | 0.048 % / **0.129 %** |
| Fz s1 | 346 | 10 | 0 | 57 | 3 | 0.008 % / 0.004 % |
| Fz s2 | 361 | 10 | 0 | 56 | 3 | 0.032 % / 0.007 % |
| Fz s3 | 333 | 9 | 0 | 53 | 3 | 0.002 % / 0 % |

Step cap 96: 0 hits (max steps used 95, T1 s0 tb). Per-schema counts of the 12 dead schemata are in
`review/recount_b.json`. `transfer_long` per schema (T1 s0–s3): demorgan_nand_to_or 4/2/5/2, dist_and_over_or_conv
34/44/43/44, dist_or_over_and 24/37/34/33, dist_or_over_and_conv 4/7/8/16, negated_conditional 29/33/18/16, peirce 7/2/3/2.

**Classical-only** (not intuitionistically provable; my own G4ip decision procedure, 8 / 8 sanity controls, agrees
with `data/sr/intuit_labels.json` on all 1,242 theorems): the pools hold 39 classical-only excluded_middle, 47 peirce,
19 peirce_sequent, 39 negated_conditional, 23 contraposition_conv, 50 demorgan_nand_to_or instances (tb + tbl).
Classical-only solves:
- textbook transfer: excluded_middle **0** on every checkpoint; peirce **0** on every checkpoint; peirce_sequent
  **1 on T1 s3**, 0 elsewhere; contraposition_conv 22–23 (T1), 7–16 (Fz); negated_conditional 1–16.
- `transfer_long`: **peirce classical-only 6 on T1 s0** (0 on s1–s3 and Fz); negated_conditional 0–12.
- All excluded_middle solves (≤ 1 per checkpoint) are intuitionistic instances.
The 441 distinct accepted texts behind the classical-only peirce / peirce_sequent solves were all re-checked in Lean
and accepted (they go through `¬¬A` and `Classical.byContradiction`).

Sizes of distinct accepted texts (median `have` lines / term size): T1 tb 9 / 29–32, T1 tbl 13–15 / 48–56,
Fz tb 6–7 / 23–24, Fz tbl 12 / 40–45.

### Lean re-check (own harness, `review/leancheck.py`)

Theorem `rvN (atoms : Prop) (h1 : …) … : goal := by <literal lean_text>`, every atom that occurs in the theorem or
the text bound (a first version bound only the theorem's atoms and wrongly rejected 108 Part B texts that mention an
extra atom; kept as `recheck_v1_harness_bug.*` in the workspace, not a finding). Reject on any error, any `sorry`
warning, or an escape-hatch token.

| group | counted texts checked | Lean accepts |
|---|---|---|
| Part A S (all distinct accepted, s0 + s1, both T) | 3,583 / 3,583 | 3,583 |
| Part A SH (all, s0 + s1, both T) | 1,034 / 1,034 | 1,034 |
| Part B T1 (150 random per file, 8 files) | 1,200 | 1,200 |
| Part B Fz (150 random per file, 8 files) | 1,200 | 1,200 |
| classical-only peirce / peirce_sequent (T1) | 441 / 441 | 441 |
| **negative control**: texts the prefilter rejected (150 per Part A file, 60 per Part B file) | 2,310 | **0** |

No counted proof is rejected by Lean. The harness does fail (all 2,310 controls rejected). The dumps contain no text
that reached Lean and was rejected: every rejection in this run was made by the reject-only prefilter
(`lean_prefilter`), and the sample above found no prefilter rejection that Lean accepts.

### Hard constraints

- `nd_verify/` tree hash equals `origin/main`'s (`git diff --quiet origin/main HEAD -- nd_verify`). Not on any
  counting path: `ss_support.py` / `support.py` judge with `lean_gate.gate`; `lpool_reread.py` with
  `eval_set.judge` → `lean_judge.judge_many`; `sr_*` scripts do not import it.
- `artifacts/TEST_RUN_DONE` unchanged since the base `d3abe474`.
- No training in this run (no training script changed or run; `state_sample.py` change is the `texts_out` hook only).
- Split disjointness by renaming class (every injective atom map into P–U, premise multiset sorted; 175,818 eval
  variants of the 29 survivors + 760 + 282 textbook theorems): 0 collisions with `data/p2/train_depth3_f0_a1.jsonl`
  (155,000; S / SH / SN training set; copy from `~/review/state-env`, md5 `29276f24…`), with `train_k12.jsonl`
  (155,000; copy from `~/review/cap-horizon/data/kh/train_k12.jsonl.gz` — assumed identical to `state-cap12`'s, which
  is not in the bucket), and with `data/ladder/rl_targets.jsonl` (4,495; T1's EI targets). The T1 loop sampled
  `data/ladder/transfer.jsonl` in-loop but never trained on it (`state_ladder_ei.py` l. 28).
- Pre-registration committed `2026-09-30T02:15:23Z` (`11d8079f`); the first job's config is stamped `02:18:14Z`.

### Compute (from the rows' `wall_s` / summaries' `wall_s`; two jobs per A40 at a time, so wall ≠ exclusive GPU time)

| arm | job wall-hours | attempts |
|---|---|---|
| S s0 / s1 | 3.35 / 4.23 | 2.57 M / 3.94 M |
| SH s0 / s1 | 7.01 / 6.71 | 6.07 M / 5.43 M |
| S s1 diagnostic (ma 1024) | 0.67 | 0.80 M |
| T1 s0–s3 (tb + tbl) | 0.52–0.54 each | 266,752 each |
| Fz s0–s3 (tb + tbl) | 0.32–0.36 each | 266,752 each |

GPU: NVIDIA A40 (46 GB) per the setup log. `podbudget`: 22.67 of 24 pod-hours, $11.25 (at `podbudget`'s rate).
