# Review — state-cap12 (reviewer session, 2026-09-29)

Reviewer: independent session, role reviewer. Brief: `~/nd-rl/docs/proposals/state-env/BRIEF_state-cap12.md`.
Pre-registration: `preregistration/state-cap12.md` (commit `c34abbfb`, 02:34:31 UTC; first pod `sc-s0` 02:36:16 UTC → written before any pod).
Code and outputs: `review_sc12/` (my own scripts `rv_*.py`; outputs `*.json`, `lean_result_*.jsonl.gz`). Checker for every
number below: **Lean 4 core alone** (v4.34.1 locally; pods used v4.34.0).

## §Recount (phase 1: written before I read `run_state_cap12.md`, `numbers.md`, `log.md` or `artifacts/sc12/tables.md` / `summary.json`)

### Inputs and method

- Workspace `~/review/state-cap12` (executor write-ups removed). Raw inputs: `artifacts/sc12/rr/*.jsonl|json` (long-pool
  re-reads), `artifacts/sc12/la_T1_*/found_*.jsonl, round_*.json` (ladders), `heldout_SN12_s*.jsonl`, gate records,
  `artifacts/sc12/lp_rr2/` (comparator re-reads copied from `long-pool`), pools under `data/ladder/`, `data/kh/train_k12.jsonl.gz`.
- **Literal Lean text**: the executor set `LEAN_GATE_DUMP` for every re-read and ladder. The dumps are not in the local
  checkout; I pulled them from the bucket (`hf://buckets/dan-pandori/nd-rl/state-cap12/artifacts/sc12/dump/`: all 32 `rr_*`
  files, and the six `la_T1_*` ladder dumps, one at a time).
- My own code: `rv_common.py` (prompt parser, Lean header, premise-order- and renaming-invariant class key, term size),
  `rv_rr.py` (re-read recount from dumps), `rv_ladder.py` (ladder recount: every counted ND proof matched to an accepted literal
  text), `rv_lean.py` (Lean re-check: one theorem per line, reject on any error, any `sorry`, or any token outside the grammar
  alphabet), `rv_neg.py` (negative controls), `rv_comp.py` (comparators), `rv_splits.py` / `rv_overlap.py` (disjointness),
  `rv_stats.py` (Q, IQM, bootstrap, L*).
- Definitions. **Q** = generator (`source == 'gen'`) theorems of `transfer_long_rr600.jsonl` with `L_true` 13–16 (my count of
  the pool: 90/90/100/100 = 380) that have ≥ 1 Lean-accepted sample at k 256. **L\*** = largest L with ≥ 5 solved theorems
  of `L_true` ≥ L (the ladder's rule; the ≥ 17 file counts as L = 17). `L_true` values are ND-derived upper bounds under Lean.
  **Term size** (mine) = number of proof-term atoms in the literal text after removing every type ascription (hypothesis
  names, constants such as `Or.elim`, `⟨`, bound names); invariant to line layout. It is not the same measure as the pool's
  `label_term_size` (elaborated-term size), so only compare my term sizes with one another.

### Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72` at HEAD = `origin/main`'s; the run's 6 commits touch no file under `nd_verify/` |
| `nd_verify` unused as a judge | the run's code (`sc12_*.py`, `lpool_reread.py`, `pod/sc12/*.sh`) never imports it; judging goes through `eval_set.judge` → `lean_judge` / `lean_gate` (Lean only). `state_env.py` imports only `nd_verify.verify.parse_formula` (a formula parser, not a judge) |
| `artifacts/TEST_RUN_DONE` unchanged | **not tracked at HEAD.** Commit `e844a8ea` (repo-hygiene on `dan`, 01:39 UTC, before this run and not by this run) untracked all of `artifacts/`, including the guard; the file is also absent on disk in the run worktree, so `test_run_once.sh`'s refuse-twice guard would not fire here. This run did not run `test_run_once.sh` or read `targets/test_*` (grep of the run's code and of the executor transcript). **Finding for `dan`, not a violation by this run** (see memory "artifacts untrack kills test guard") |
| evaluation files read in training code | `state_train.py` reads the K12 file plus `data/p2/heldout.jsonl` for held-out evaluation only; `state_ladder_ei.py` / `ladder_ei.py` samples `data/ladder/transfer.jsonl` each round for its read-out and never adds those proofs to the mix. No training script mentions `transfer_long*`. The ladder's replay filter drops K12 records whose exact `key` matches transfer / held-out / targets, but not permutations of premises (see disjointness) |
| budget | `podbudget state-cap12 --set 40 20` at 02:30:04 UTC, before the first pod. Used 30.17 h / $14.91 (A40 ×4 pods, RTX 3090 ×2 pods at the `podhours.log` rates) — within $20 and within the $15 stop rule |

No hard-constraint violation by this run → no quarantine.

### Accounting: the executor's rows are reproducible from the literal-text dumps

- **Re-reads (32 files):** for every `rr_*` dump, the set of prompts with ≥ 1 Lean-accepted literal text **equals** the
  set of `solved: true` rows in the matching `artifacts/sc12/rr/*.jsonl` (32/32 set-equal, no prompt outside its pool).
- **Ladders (6):** every counted proof in `found_transfer_8.jsonl` and `found_8.jsonl` matches an accepted literal text in
  that ladder's dump (SN12 s0: 45,114 transfer and 136,125 target proofs, 0 unmatched; the other five also 0 unmatched).
  The solved counts equal `round_8.json`'s `transfer_cum` / `targets_cum`. One theorem (SN12 s2) is accepted in the dump
  only through a greedy decode and is not counted, which is conservative.
- All gate rejections in the re-read dumps come from the pre-Lean prefilter (`filter` ≠ null, `lean` = null); none come
  from Lean itself. A prefilter false reject would under-count, and none of my 150 sampled prefilter rejects is accepted by Lean.

### Lean re-check of counted proofs (literal text)

| group | accepted texts re-checked | rejected by my Lean check |
|---|---|---|
| SN12 T1 r8 re-reads, s0–s3 (rr600 + ge17 + ms96 diag.) | 882 | 0 |
| SN12 Stage-1 re-reads, s0–s3 (rr600 + ge17 + orig + ms96 diag.) | 1,188 | 0 |
| K12 T1 r8 re-reads, s0–s1 (rr600 + ge17) | 225 | 0 |
| SN12 T1 ladders, in-loop counted (transfer 110 + targets 60 per seed) | 680 | 0 |
| K12 T1 ladders, in-loop counted | 340 | 0 |
| **total** | **3,315** (≥ 112 per arm/seed) | **0** |

Negative controls, which must fail (the harness has to be shown able to reject): 150 prefilter-rejected literal texts,
75 accepted texts under another theorem's header, 75 accepted texts with the last step removed → **300 / 300 rejected**.
The first pass of my check also rejected 1,004 correct texts because my token allowlist lacked the grammar's `hh`
(DN binder) and `nX.elim`. I widened it to the grammar's alphabet (`lean_tok.TSYMS`) and all 3,315 passed. The only axiom
the grammar can reach is `Classical.byContradiction` (DN), and no text contains `sorry`.

### Primary quantity Q (rr600 generator theorems, L_true 13–16, /380), k 256, final checkpoints

| arm (model) | per seed | mean | IQM [stratified-bootstrap 95 % CI] |
|---|---|---|---|
| SN12 T1 r8 (`ckpts/sc12/ladder/la_T1_SN12_s{0-3}_r8.pt`; 3.2 M `lean_staten`, from scratch, Stage-1 on K12 + ladder T1) | 233 / 295 / 320 / 317 | 291.3 | 306.0 [233, 320] |
| SN12 Stage-1 (`ckpts/sc12/stage1_SN12_s{0-3}.pt`; same model, before the ladder) | 134 / 212 / 228 / 216 | 197.5 | 214.0 [134, 228] |
| K12 whole-proof T1 r8 (`ckpts/ladder/la_T1_K12_s{0,1}_r8.pt`; 3.2 M `lean_seq`, from scratch, cap-horizon K12 Stage-1 + ladder here) | 79 / 72 | 75.5 | — (n = 2) |
| SN-v2 cap-6 T1 r8 (state-env, via long-pool `lp_rr2`) | 102 / 28 | 65.0 | — |
| SN-v2 cap-6 Stage-1 (state-env) | 3 / 0 | 1.5 | — |
| K12 Stage-1 s0 (cap-horizon) | 38 | — | — |

- Pre-registered falsifier: "compounding supported only if mean Q(SN12 T1) exceeds max(mean SN-v2 cap-6 T1, mean K12 T1)
  by more than MDD ≈ 119". Recount: 291.3 − 75.5 = **215.8** > 119 (bootstrap 95 % of that difference [168, 243]). By the
  pre-registered rule, **supported**. My MDD recomputation matches (sd 37 from pooled S / SN-v2 pairs; t-based, df 4:
  (2.776 + 0.941) × 37 × √(1/4 + 1/2) = 119; 2 vs 2: 199).
- Secondary ("the cap lever transfers to the state policy" refuted if SN12 frozen Q ≤ 3 + 10 on ≥ 3 of 4 seeds): SN12
  Stage-1 Q is 134–228 on 4/4 seeds → **not refuted**.
- T1 − Stage-1 per seed (paired, same seed): +99 / +83 / +92 / +101.
- Brief's falsifier (T1 L\* on the long pool ≤ max comparator L\*): see L\* below; as the pre-registration says, it cannot
  discriminate at the ceiling.

### Per-bin rates, totals, the ≥ 17 file, L\*, step-cap (rr600 unless stated)

| model | rr600 /600 | gen 13 / 14 / 15 / 16 % | ≥ 17 /70 | L\* | textbook solved (of 73) | step-cap hits (ms 48) rr600 / ge17 | action truncated rr600 |
|---|---|---|---|---|---|---|---|
| SN12 T1 s0 | 375 | 66 / 71 / 63 / 47 | 25 | ≥ 17 | 29 | 0.13 % / 0.98 % | 0.027 % |
| SN12 T1 s1 | 454 | 81 / 84 / 75 / 71 | 42 | ≥ 17 | 30 | 0.16 % / 0.81 % | 0.021 % |
| SN12 T1 s2 | 476 | 86 / 88 / 86 / 78 | 42 | ≥ 17 | 27 | 0.30 % / 1.46 % | 0.022 % |
| SN12 T1 s3 | 472 | 83 / 89 / 91 / 71 | 46 | ≥ 17 | 28 | 0.31 % / 1.26 % | 0.026 % |
| SN12 Stage-1 s0 | 248 | 49 / 46 / 31 / 18 | 10 | ≥ 17 | 10 | 0.003 % / 0.045 % | 0.037 % |
| SN12 Stage-1 s1 | 338 | 61 / 67 / 52 / 45 | 15 | ≥ 17 | 17 | 0.002 % / 0.011 % | 0.033 % |
| SN12 Stage-1 s2 | 356 | 67 / 68 / 63 / 44 | 19 | ≥ 17 | 14 | 0.001 % / 0.028 % | 0.004 % |
| SN12 Stage-1 s3 | 344 | 62 / 64 / 57 / 45 | 18 | ≥ 17 | 14 | 0.001 % / 0.017 % | 0.006 % |
| K12 T1 s0 | 160 | 36 / 28 / 15 / 7 | 3 | 16 | 0 | — (whole-proof: `max_new` 1536 hit 0.044 % / 0.022 %) | — |
| K12 T1 s1 | 151 | 24 / 24 / 21 / 7 | 2 | 16 | 0 | — (0.032 % / 0.028 %) | — |

- Settings: all state re-reads batch 2,048, `max_action` 512, `max_steps` 48, k 256, T 0.8, seed 0; whole-proof batch 1,024,
  `max_new` 1,536 — identical to the comparators in `lp_rr2` (checked from their summaries). Peak memory 12–18.7 GB.
- **Step cap:** the SN12 T1 re-reads hit `max_steps` 48 on 0.13–0.31 % of rr600 samples and 0.8–1.5 % of ≥ 17 samples, above
  the policy's ≈ 0.1 % and against the pre-registered "0.0 % step-cap hits" expectation (a **miss**). The dumps do not record
  step-capped attempts, so I cannot split the rate by bin. The `ms96` diagnostic (max_steps 96, s0–s1 only) moves Q
  233 → 231 and 295 → 296, and ≥ 17 25 → 25 and 42 → 42. Those changes are sampling re-draws, so at k 256 the cap does not
  change the headline. It was not run on s2–s3, which have the higher cap rates.
- The pre-registration says textbook theorems are excluded "because every model solves ≈ none of them". This holds for
  K12 and the cap-6 comparators (0–6), but not for SN12 (T1 27–30 of 73, Stage-1 10–17). Q excludes them as pre-registered.
- Term size (mine) of the shortest accepted text, median per bin 11 / 12 / 13 / 14 / 15 / 16: SN12 T1 s0
  29 / 37 / 34 / 38 / 41 / 42, other seeds within ±3. K12 T1 28 / 29 / 31 / 31 / 35 / 36. Term size rises with `L_true`
  in every arm, so the bins stay ordered in difficulty under Lean. K12's accepted proofs are ≈ 3–6 atoms smaller in the
  same bins, measured on its own (easier) solved subsets.

### Original transfer pool (`data/ladder/transfer.jsonl`, 2,285)

| model | solved | L\* (≥ 5) | solved with L_true ≥ 13 (13 / 14) |
|---|---|---|---|
| SN12 T1, in-loop cumulative 8 × 32 (s0–s3) | 1,960 / 2,027 / 2,024 / 1,985 | 13 / 13 / 13 / 13 | 5 / 5 / 6 / 7 |
| SN12 Stage-1, k 256 re-read (s0–s3) | 1,661 / 1,769 / 1,796 / 1,727 | 12 / 12 / 13 / 12 | 4 / 4 / 5 / 3 |
| K12 T1, in-loop cumulative (s0–s1) | 1,703 / 1,634 | 13 / 13 | 5 / 5 |

Targets (`data/ladder/rl_targets.jsonl`, 4,495) in-loop cumulative: SN12 T1 4,171 / 4,228 / 4,215 / 4,196; K12 T1
3,893 / 3,811. Ladder held-out greedy at r8: SN12 0.962 / 0.976 / 0.977 / 0.977; K12 0.954 / 0.958. The original pool
holds only 13 + 10 theorems at `L_true` 13–14, so L\* 13 there reflects 3–7 solved theorems and should be treated as
ceiling-limited, not as a frontier.

### Held-out greedy, Stage-1 (`data/p2/heldout.jsonl`, 5,000)

SN12 Stage-1 s0–s3: 0.9688 / 0.9768 / 0.9778 / 0.9744 (spread 0.9 pp). Pre-registered expectation (≥ 0.93 on every seed,
spread < 4 pp): **met**. No literal-text dump exists for the held-out pass, so these are the gate's Lean verdicts, recounted
from the row files and not re-checked in Lean by me.

### Gates on K12 (records, not re-run)

`gate13_canon_k12.json`: 155,000 records, gate 1 + gate 3 failures 0. Gate 1b: 3,000 checked, 0 rejected. **Note:** gate 1b
goes through `lean_judge.judge_many`'s fallback (`nd2lean` translation of the ND string; `lean_judge_stats.fallback = 3000`),
so it checks the ND proof's Lean translation, not the reassembled `lean_seq` literal text. That design is inherited from
`state-env`. It is covered in practice, because every in-loop accepted sample is checked in Lean from its literal text.
`gate2_canon_k12ge7.json`: 1,500 / 1,500 cuts agree (≥ 7-line proofs). I did not re-run the gates.

### Split disjointness by renaming class (my key: invariant to atom renaming **and** premise order)

| training file × evaluation pool | shared classes | evaluation items affected |
|---|---|---|
| K12 (155,000; 154,382 classes) × rr600 / ≥ 17 | 0 / 0 | 0 |
| K12 × original transfer (2,285) | 2 | 2 (both `L_true` 9) |
| K12 × p2 held-out (5,000) | 22 | 22 (0.44 %; n_lines 3–6) |
| ladder `rl_targets` (4,495) × rr600 / ≥ 17 / held-out | 0 / 0 / 0 | 0 |
| ladder `rl_targets` × original transfer | 2 | 2 |

Every shared pair is a premise permutation plus renaming. None matches on the repo's (premise-order-sensitive) `key`, which
is why the ladder's replay filter and earlier split checks miss them. They come from cap-horizon's K12 and from the ladder
pools, not from this run. They affect at most 0.44 pp of held-out and 2 of 2,285 original-pool theorems, and none of the
long pool that carries the headline.
