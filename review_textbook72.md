# Review: run textbook72 (reviewer, 2026-09-30)

Reviewer session, independent of the executor. Phase 1 below was written from the blind workspace
`~/review/textbook72` (executor write-ups removed) before I read `run_textbook72.md`, `numbers.md`, `log.md` or
`STATUS.md`. I did not read the executor's `summary.json`, `analysis_stdout.txt`, `contam.json` or `long_proofs.md`
in phase 1 either. Scripts and outputs: `review_tb72/` (`review_tb72_recount.py`, `review_tb72_lean_recheck.py` +
`review_tb72_lean_lib.py`, `review_tb72_ndv_secondary.py`; `recount.json`, `lean_recheck.json`, `ndv_secondary.json`).
None of them import the executor's `tb72_*.py`.

**Models.** I read every checkpoint's pickled `extra` with a stubbed unpickler (no torch), after downloading all 12 from the
bucket. Each md5 equals the `ckpt_md5` in that read-out's registry row. All 12 have 3,216,384 parameters, format
`lean_staten`, and were trained from scratch (`init None` in Stage 1):
SN-cap12 frozen = `state-cap12/.../stage1_SN12_s{0..3}.pt` (Stage 1 on `data/kh/train_k12.jsonl`);
SN-cap12 T1 = `la_T1_SN12_s{0..3}_r8.pt` (ladder EI round 8, last mix `artifacts/sc12/la_T1_SN12_s*/mix_8.jsonl`);
SN-v2 cap-6 frozen = `state-env/.../stage1_SN_s{0,1}.pt` (Stage 1 on `data/p2/train_depth3_f0_a1.jsonl`);
SN-v2 cap-6 T1 = `la_T1_SN_s{0,1}_r8.pt`. This matches the pre-registration table. Every number below is for one of
these four models and names it.

**Settings (all 12, from the args files).** `state_eval.py`, k 256, T 0.8, sampling seed 0, batch 4,096, max_action 512,
max_steps 96, the same in every arm. All 72 prompts equal `dev58 + train14` (the registry `data_md5` of `all72.jsonl`
equals the md5 of the two eval files concatenated; both sha256 match `MANIFEST.json`). GPU: one A40 (setup log).

## §Recount (phase 1, blind)

### Hard constraints

| check | result |
|---|---|
| `nd_verify/` tree hash equals `origin/main`'s | yes (identical in `origin/main`, `d7411772`, `HEAD`) |
| `artifacts/TEST_RUN_DONE` unchanged | yes (same blob `1d5cf064` as `origin/main`) |
| eval files read in training code | no training in this run. The diff `d7411772..ba2a3f1c` outside artifacts touches only `tb72_*.py`, `pod/tb72/*.sh`, the eval-only data dir and docs. No other `.py` references `textbook72` / `eval_only` |
| `nd_verify` used as a judge | no. Acceptance is `state_eval` → `lean_gate` (`"judge": "lean-only"` in every gate record). `tb72_analysis.py` imports `nd_verify.verify_text` for the pre-registered, labelled secondary count only |
| gate 0 (expectations before the run) | pre-registration committed `51c97089` at 14:51:47 UTC. First read-out START is 14:55:03 (queue log) and the file was not changed afterwards. Its header says "written ~15:10 UTC", which is wrong but harmless: the commit time is what counts |

No quarantine.

### Lean re-check (Lean 4.34.1 core on the VPS)

Every stored accepted proof of every checkpoint was checked, not a sample: 6,128 distinct proofs (T1_SN12 878 / 1,033 /
1,387 / 941; Fz_SN12 371 / 487 / 367 / 392; T1_SN6 152 / 52; Fz_SN6 37 / 31). That is ≥ 100 per arm; the SN-v2 frozen
arm has only 68 distinct accepted proofs in total, and all of them were checked. Each proof got two renderings: my own
ND → Lean term translator, and the `lean_tok` `lean_seq` rendering. One theorem per line, `#print axioms` after it, and
axioms allowed only from {propext, Classical.choice, Quot.sound}. The error regex was fixed for Lean 4.34's
`error(code):` form.

| rendering | accepted |
|---|---|
| mine | **6,128 / 6,128** |
| lean_seq | **6,128 / 6,128** |
| control: proof under a different prompt (same premise count) | 0 / 300 |
| control: final `exact` replaced by `sorry` | 0 / 100 (caught by the axiom check) |
| control: first ORI1↔ORI2 / ANDE1↔ANDE2 swapped | 14 / 300. All 14 are on symmetric formulas (`Q ∨ Q`, `(P→Q) ∨ (P→Q)`, `Q ∧ Q`, …), where the swap is still valid |

The stored text is the environment's clean ND rendering. The accepted `lean_seq` texts themselves are not stored:
`gate/lean_gate.leanrej.jsonl.gz` keeps only the rejected ones. So "stored literal text" here means the ND string that
Lean accepted after rendering. No counted proof is rejected. The stored-proof set equals the `solved` flag on all 864
(checkpoint, problem) rows.

Labelled secondary (pre-registered; Lean ∧ `nd_verify`, judges nothing): **0** of the 6,128 Lean-accepted proofs are
rejected by `nd_verify`, so the per-checkpoint Lean ∧ `nd_verify` solved counts equal the Lean counts.

### Solved per checkpoint (Lean alone, pass@256)

Bins by `reference_lines` (dev58): 1–5: 5, 6–10: 24, 11–15: 16, 16+: 13; train14 has no reference length.

| checkpoint (model) | all 72 | dev58 | train14 | 1–5 | 6–10 | 11–15 | 16+ | action-cap % | step-cap % | max steps seen | peak alloc GB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1_SN12_s0 (SN-cap12 T1) | 37 | 30 | 7 | 5 | 18 | 5 | 2 | **0.157** | 0 | 60 | 24.5 |
| T1_SN12_s1 | 38 | 32 | 6 | 5 | 18 | 7 | 2 | 0.000 | 0 | 60 | 24.1 |
| T1_SN12_s2 | 36 | 30 | 6 | 5 | 18 | 4 | 3 | 0.005 | 0 | 76 | 26.6 |
| T1_SN12_s3 | 38 | 32 | 6 | 5 | 19 | 6 | 2 | 0.005 | 0 | 73 | 28.2 |
| Fz_SN12_s0 (SN-cap12 frozen) | 26 | 20 | 6 | 5 | 12 | 2 | 1 | 0.087 | 0 | 42 | 24.8 |
| Fz_SN12_s1 | 29 | 23 | 6 | 5 | 14 | 4 | 0 | 0.087 | 0 | 56 | 23.4 |
| Fz_SN12_s2 | 32 | 26 | 6 | 5 | 17 | 4 | 0 | 0.054 | 0 | 43 | 25.0 |
| Fz_SN12_s3 | 26 | 21 | 5 | 5 | 13 | 3 | 0 | 0.000 | 0 | 50 | 25.4 |
| T1_SN6_s0 (SN-v2 cap-6 T1) | 22 | 18 | 4 | 5 | 12 | 1 | 0 | 0.005 | 0 | 44 | 20.9 |
| T1_SN6_s1 | 16 | 12 | 4 | 5 | 7 | 0 | 0 | 0.005 | 0 | 57 | 21.7 |
| Fz_SN6_s0 (SN-v2 cap-6 frozen) | 16 | 13 | 3 | 5 | 8 | 0 | 0 | 0.005 | 0 | 23 | 21.7 |
| Fz_SN6_s1 | 14 | 12 | 2 | 5 | 7 | 0 | 0 | 0.043 | 0 | 20 | 20.4 |

Every per-checkpoint total equals the `SOLVED` line of the queue log and the summary json. Cap rates are over the
18,432 attempts from the summaries' `env_end` counters. The step cap (96) was never hit: the longest attempt took 76
steps. The action cap (512) was hit by 29 attempts (0.157 %) on T1_SN12_s0, above the 0.1 % bar; every other
checkpoint is ≤ 0.087 %. The diagnostic re-run `diag/T1_SN12_s0_a1024` (not pre-registered; same seed, max_action
1,024) settles it: truncations fall from 29 to 6, the 23 freed attempts all end in syntax errors, `done` stays at 14,711,
and the solved set, the distinct proofs (878) and the accepted samples (3,317) are identical. The cap cost nothing.
Peak memory is `torch.cuda.max_memory_allocated` at batch 4,096: 20–28 GB.

### Arms

Per-seed values, mean, IQM with a bootstrap 95 % interval over seeds (10,000 resamples), and the union over seeds:

| arm (model) | per seed (72) | dev58 per seed | train14 per seed | mean | IQM [95 % CI] | union 72 (dev58) | union by bin 1–5/6–10/11–15/16+/train |
|---|---|---|---|---|---|---|---|
| SN-cap12 T1 | 37, 38, 36, 38 | 30, 32, 30, 32 | 7, 6, 6, 6 | 37.25 | 37.5 [36, 38] | 46 (38) | 5 / 21 / 9 / 3 / 8 |
| SN-cap12 frozen | 26, 29, 32, 26 | 20, 23, 26, 21 | 6, 6, 6, 5 | 28.25 | 27.5 [26, 32] | 36 (30) | 5 / 17 / 7 / 1 / 6 |
| SN-v2 cap-6 T1 (n = 2) | 22, 16 | 18, 12 | 4, 4 | 19 | — | 22 (18) | 5 / 12 / 1 / 0 / 4 |
| SN-v2 cap-6 frozen (n = 2) | 16, 14 | 13, 12 | 3, 2 | 15 | — | 18 (15) | 5 / 10 / 0 / 0 / 3 |

Paired by seed, SN-cap12 T1 − frozen = **+11, +9, +4, +12** (mean +9.0, SD 3.56, paired t = 5.06, df 3, two-sided
p ≈ 0.015). At that SD the n = 4 paired MDD (80 % power, α 0.05) is ≈ (3.18 + 0.98) × 3.56 / 2 ≈ 7.4, against ≈ 8 in the
pre-registration; +9 clears it. SN-v2 paired: +6, +2 (n = 2, descriptive). Only one problem that some SN-cap12 frozen
seed solves is solved by no T1 seed (`textbook_8244c4b1…`); 11 are solved by some T1 seed and by no frozen seed.

All 12 checkpoints together solve 47 / 72. **25 problems are solved by no checkpoint**: 10 of the 13 in 16+, 6 of the 16 in 11–15, 3 of the 24 in 6–10 (`0824150e`, `5758428c`, `a104fab3`) and 6 of train14. The most
16+ problems any single checkpoint solves is 3 (T1_SN12_s2).

### Pre-registered predictions (my values)

| prediction | outcome |
|---|---|
| SN-cap12 T1 36 / 72 per seed (range 28–44) [union 42] | 36–38, mean 37.25: **in range**. Union 46 (above the 42 predicted) |
| SN-cap12 frozen 24 (16–32) [union 30] | 26–32, mean 28.25: **in range**. Union 36 (above) |
| SN-v2 cap-6 T1 32 (24–40) | 22, 16: **miss (below range)** |
| SN-v2 cap-6 frozen 18 (10–26) | 16, 14: in range |
| T1: "near-everything ≤ 10 reference lines and train14" | ≤ 10: 23–24 / 29 per seed (yes). train14: 6–7 / 14 per seed (union 8): **miss** |
| T1: "about a third of 11–15" | 4–7 / 16 per seed (25–44 %): roughly yes |
| T1: "≤ 2 of 16+" | 2, 2, 3, 2: s2 misses by one |
| (a) T1 − frozen ≥ +6 on each SN-cap12 seed | +11, +9, **+4**, +12: **miss on seed 2** (the mean holds) |
| (b) no checkpoint solves > 3 of the 13 with reference_lines ≥ 16 | max 3: **holds** |
| (c) SN-cap12 T1 median seed ≥ 31 | 37.5: **holds** |
| (d) step-cap and action-cap each ≤ 0.1 % of attempts | step cap 0 everywhere. Action cap **0.157 % on T1_SN12_s0 (miss)**, ≤ 0.087 % elsewhere; no effect on solved (a1024 diag) |
| (e) contamination 0–5 overlaps, all short | 1 overlap, reference 7 lines: **holds** (see below) |

### Contamination (my own renaming-class keys)

I used two keys. The ordered key renames atoms by first occurrence, keeping premise order. The order-free key is the
minimum over atom bijections of (sorted premise multiset, conclusion). The textbook set's atoms are P, Q, R, S (and F).
The 72 are 72 distinct classes under both keys.

| training set | records | ordered hits | order-free hits |
|---|---|---|---|
| cap-6 control `p2/train_depth3_f0_a1.jsonl` (SN-v2 Stage 1) | 155,000 | 0 | 0 |
| K12 `kh/train_k12.jsonl` (SN-cap12 Stage 1) | 155,000 | 0 | **1** (`textbook_3ed45280…`, dev, 7 ref lines) |
| `data/ladder/rl_targets.jsonl` | 4,495 | 0 | 0 |
| `data/rl_targets.jsonl` (old) | 3,000 | 0 | 0 |
| SN-cap12 ladder `mix_1..8` × 4 seeds (32 files) | 2,546,384 | 0 | 1 (the same problem) |
| SN-v2 ladder `mix_1..8` × 2 seeds (16 files) | 752,444 | 0 | 0 |

The one overlap is a premise-order permutation of a K12 Stage-1 theorem. It carries into the SN-cap12 mixes, which
replay Stage-1 data. Some checkpoint solves it, so the SN-cap12 counts include at most one contaminated problem. Without
it, per-seed counts drop by at most 1.

### Robbie's per-problem results (read from nd-rl `origin/robbie-experiments:…/2026-09-28-combined-model/charts/passk.csv`, not the executor's copy)

Robbie's pool is `textbook72`, n = 256 attempts per problem, and the problem names equal ours. He used a different model,
format and checker (Lean ∧ `nd_verify`), so the comparison is descriptive only.

- Combined model `fact-lean-best-leon_s{0,1,2}`: 32, 30, 32 (mean 31.3), union 36.
- `fact-abs-naive-ei_s{0,1,2}`: 7, 11, 9 (mean 9 = 12.5 %), union 13. The file also has `fact-lean-naive-*` (8, 6, 10 and
  12, 10, 9) and `fact-abs-naive-leon_*` (11, 12, 13). Which of these is "the naive pipeline (13 / 72)" cannot be read
  from the file. "13" matches the 3-seed union of `abs-naive-ei` and also that arm's mean rate (9 / 72 = 12.5 % ≈ 13 %).
  No naive arm has a per-seed mean of 13 problems.
- SN-cap12 T1 union (46) vs combined-model union (36): 34 in common. 12 are ours only (6–10: 3, 11–15: 4, 16+: 3,
  train14: 2); 2 are his only (`0824150e`, 6–10; `3d573ac4`, 11–15). No checkpoint of ours solves either of those two.
- Same-index seeds (his s*i* vs our T1_SN12_s*i*): 29, 26, 27 problems in common.

### Proof length (my measures)

Lines = numbered ND lines of the stored proof. Term size = inference nodes reachable from the conclusion through
citations, excluding PR and R. This is my own measure, not `lean_check`'s elaborated-term size. Per problem I take the
minimum over every accepted proof of every checkpoint.

- Of the 39 solved dev problems, the shortest accepted proof is shorter than `reference_lines` on 7, equal on 28 and
  longer on 4. Term size is below `reference_lines` on 32.
- Longest problem solved: `textbook_b98931f2…` (`¬(P → Q) ⊢ P ∧ ¬Q`, reference 18 lines). Solved by 5 checkpoints,
  including frozen Fz_SN12_s0. Shortest proof 16 lines, term size 14:

```lean
theorem tb_b98931 (P Q R S : Prop) (h1 : ¬ (P → Q)) : P ∧ ¬ Q := by
  have n1 : ¬ (P → Q) := h1
  have n8 : ¬ ¬ P := fun (n2 : ¬ P) => by
    have n6 : P → Q := fun (n3 : P) => by have n4 : False := n2 n3; have n5 : Q := n4.elim; exact n5
    have n7 : False := n1 n6; exact n7
  have n9 : P := Classical.byContradiction (fun hh => n8 hh)
  have n15 : ¬ Q := fun (n10 : Q) => by
    have n13 : P → Q := fun (n11 : P) => by have n12 : Q := n10; exact n12
    have n14 : False := n1 n13; exact n14
  exact ⟨n9, n15⟩
```

- The largest minimum term size is 16, on 3 problems (`757636e8`: 10 ref lines but 19 lines at best; `49c48adc`: 13 ref,
  18 lines; `fef8f88a`: 13 ref, 19 lines). Other 16+ problems solved: `418e4b67` (16 ref, 16 lines, term 15) and
  `48e30865` (16 ref, 14 lines, term 12).
- Accepted proofs often pad with `X ∨ X` / `X ∧ X` detours (ORI then ORE on the same disjunct). Lean accepts them.
  They inflate line counts but not solved counts.

### Compute (from the registry rows `state_eval.py` wrote; my derivation)

GPU: one NVIDIA A40. No training (0 train steps / tokens). Per checkpoint: `gpu_seconds` 43–109 (T1_SN12 101–109;
Fz_SN12 73–87; SN6 43–58); 18,432 attempts; actions 108 k–245 k; generated tokens 1.5 M–3.3 M; Lean checks
325–2,898. The `actions` counts equal the `rows` field of each summary's `env` block. Sum of the 12 read-outs is
936.9 GPU-s; with the a1024 diagnostic it is 1,053.7 GPU-s (≈ 0.29 GPU-h). Queue wall clock 14:55:03 → 15:11:07 (16 min).
The T1 arms spend ≈ 1.3× the frozen arms' GPU-seconds and generated tokens at equal attempts, because RL'd policies take
more steps per attempt. This is an evaluation at matched attempts, so the flag is informational. The registry `seed`
field of T1 rows is 8 / 1008 / 2008 / 3008 (`record.model_seed` of a ladder checkpoint), not the Stage-1 seed 0–3. That
is a labelling quirk; the `ckpt` field is right.
