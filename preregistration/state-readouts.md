# Pre-registration — state-readouts (2026-09-30, written before any pod)

Run id `state-readouts`, fork branch `dan_state-readouts` (from `origin/dan` at `d3abe474`). Executor: agent:claude.
Brief: `state-readouts` (Dan, 2026-09-30). Sampling read-outs of existing checkpoints only; no training.
Judge: **Lean alone** (`lean_gate.gate` on the literal `lean_seq` text the environment assembles; `LEAN_GATE_DUMP` on
every job). `nd_verify` is on no counting path. All models below are from scratch, 4 layers, d 256.

## Part A — seeing the state, or environment-assigned names?

**Question.** `support-state` found that the SN base (`lean_staten`: sees the state, the environment names what a step
introduces) reaches 28 / 29 of `support-curves`' survivors per seed (s0, s1), where the whole-proof base reaches 0 / 29
at 400,000 attempts. Is that from *seeing the state* or from *not having to choose names*?

**Models** (all Stage-1 bases, 3,216,384 params, 6,000 steps × 128 on `data/p2/train_depth3_f0_a1.jsonl`, cap 6):
- **S** (`lean_state`: state in, one `lean_seq` step out, the policy writes its own names): `state-env`
  `ckpts/se/stage1_S_s{0,1}.pt`; if budget allows, `state-frontier` `ckpts/sf2/stage1_S_s{2,3}.pt`.
- **SH** (`lean_stateh`: the actions so far + the state; own names): `state-env` `ckpts/se/stage1_SH_s{0,1}.pt`.
- Inherited, not re-run: SN base s0 / s1 (28 / 28, `support-state` H, Lean alone, 2026-09-28); WP base
  `stage1_a1_seq_s0.pt` (`lean_seq`, 3,214,336 params; 0 / 29 at 400,000, `support-curves`, Lean alone, 2026-09-27).

**Design = `support-state` H exactly.** `ss_support.py` (taken unchanged from `origin/dan_support-state` except one
`record.save_config` line for compute rows) with `state_sample.env_generate` (its `texts_out` patch), 29 names of
`data/sc/falsifier_survivors.txt`, up to 200,000 attempts at T 0.8, stop at 5 successes; then up to 200,000 at T 1.0
for rows with < 5 successes. Batch 4,096, `max_chunk` 8, `max_action` 256, `max_steps` 48, fast decode path,
sampling seeds `10·s+1` (T 0.8) and `10·s+2` (T 1.0) — the same seeds `support-state` used for SN s0 / s1.
S and SH use `Env(prompt)` (no environment naming), which is what `env_generate` does for a non-canon tokenizer.

**Headline:** survivors reached (≥ 1 Lean-accepted attempt, either temperature) per arm and seed, out of 29.
Also p̂ per theorem (successes / attempts at each T), seed-labelled.

**Reading (the brief's, fixed now):** per arm, using the mean over its seeds:
- S and SH both ≥ 20 / 29 → *seeing the state is what matters*.
- S and SH both ≤ 5 / 29 → *environment naming is what matters*.
- otherwise → *both* (and I report which arm is where). If the two arms fall in different bands, the reading is
  stated per arm (S isolates naming against SN; SH adds history on top of S).

**Noise.** No noise floor exists for this quantity. SN's two seeds give 28 / 28 with 2 per-theorem disagreements,
but S seeds differ far more on held-out (0.958 / 0.801, `state-env`). The bands are 15 theorems apart so that the
reading does not hinge on a small difference; a between-arm difference of ≤ 5 theorems at n = 2 is not called a
finding. The per-theorem comparison with SN is paired (same 29 theorems, same sampling seeds).

**Expected (numeric):**
- A1. S reached per seed: **24** (80 % range 17–29) on each of s0 / s1. s1 at or below s0 (its held-out name failure).
- A2. SH reached per seed: **21** (80 % range 12–28) — SH's frozen transfer score is ≈ 0.6× S's.
- A3. Reading: P(state band) 0.65, P(both) 0.30, P(naming band) 0.05.
- A4. Median p̂ at T 0.8 (unreached = 0) below SN s0's 0.188 for every S / SH seed; within 10× of SN s1's 0.0088 on at
  least one S seed.
- A5. Every theorem that S reaches, SN reaches on at least one seed (S adds no survivor SN misses): 0 exceptions
  expected (SN union is 29 / 29, so this is trivially true; recorded for completeness).
- A6. Length caps: ≤ 0.1 % of attempts per arm hit `max_steps` or `max_action` (support-state: 0.014 % pooled).

## Part B — does SN-cap12 get past the textbook schemata no arm has moved?

**Models** (`state-cap12`, `lean_staten`, 3,216,384 params, from scratch on K12 = `data/kh/train_k12.jsonl`, cap 12):
SN-cap12 frozen `stage1_SN12_s{0-3}.pt` and T1 `la_T1_SN12_s{0-3}_r8.pt` (+ 8 ladder EI rounds, k 32, T 0.8).

**Pools:** the 760 textbook theorems of `data/ladder/transfer.jsonl` (19 schemata × 40, the pool behind
`ds-composition`'s D4b table) → `data/sr/textbook_transfer.jsonl`; the 282 textbook theorems of
`data/ladder/transfer_long.jsonl` (6 schemata, `L_true` 11–14) → `data/sr/textbook_long.jsonl`.
**Settings:** `lpool_reread.py` (from `origin/dan_state-cap12`), k 256, T 0.8, seed 0, `max_steps` 96, `max_action`
512, batch 4,096. Report solves (≥ 1 accepted of 256) per schema, per seed and arm.

**"Dead" schemata (defined now):** the 12 that are ≤ 2 / 40 in every arm of `ds-composition` D4b including A3 (cap 8):
demorgan_and_to_nor, demorgan_nor_to_and, demorgan_or_to_nand, dist_and_over_or, dist_and_over_or_conv,
dist_or_over_and, excluded_middle, import, negated_conditional, negated_conditional_conv, peirce, peirce_sequent.
(D4b numbers: T1 in-loop cumulative at 8 × k 32, seed 0, under Lean ∧ `nd_verify`, whole-proof `lean_seq` models.)

**What I looked at before writing this (disclosed):** the in-loop cumulative T1 solves per schema of `state-env`
(S / SH / SN, cap 6) and of `state-cap12` (SN-cap12 T1 s0–s3), from their `found_transfer_8.jsonl`
(`sr_schema_inherited.py`, `artifacts/state-readouts/inherited_schema.json`). SN-cap12 T1 in-loop already has 11 of the 12 dead
schemata at ≥ 5 on every seed; excluded_middle is 1 / 0 / 0 / 1. The cap-6 state arms already move some of them too
(e.g. demorgan_nor_to_and 36–40, peirce up to 22). So the brief's premise ("no arm has moved them") holds for the
whole-proof arms only, and this part is mostly a confirmation at a fixed k 256 on the final checkpoint.

**Expected (numeric):**
- B1. SN-cap12 T1, transfer textbook: dead schemata at ≥ 5 solves = **11** per seed (range 10–11); excluded_middle
  ≤ 2 on every seed.
- B2. SN-cap12 frozen, transfer textbook: dead schemata at ≥ 5 = **7** per seed (range 4–10).
- B3. Textbook totals / 760: T1 480–580 per seed; frozen 280–450.
- B4. `transfer_long` textbook / 282: T1 90–170 per seed, with ≥ 5 on at least 5 of its 6 schemata; frozen 30–110.
- B5. Step cap 96 hit on ≤ 0.1 % of samples per checkpoint (48 was hit 0.13–1.5 % on long-pool files).

## Compute, budget and stop rule

- Budget **$12, 24 pod-hours** (`podbudget state-readouts --set 24 12`), balance floor $100.
- Estimate at ≈ 300 attempts / s per job (support-state H on an RTX PRO 4500): Part A ≈ 3 M attempts per seed-arm if
  ≈ 24 are reached (≈ 2.8 GPU-h), up to 11.6 M (≈ 11 GPU-h) if few are; Part B ≈ 2.1 M attempts (≈ 2 GPU-h).
  Plan: 2 pods (48 GB class, 2 jobs each), ≈ 8 h, ≈ 16 pod-hours.
- **Priority when the budget binds:** (1) T 0.8 phase for S s0/s1 and SH s0/s1; (2) Part B, T1 then frozen; (3) T 1.0
  phase for the four core seed-arms; (4) S s2/s3. Stop launching new work at 20 pod-hours; at 23 pod-hours kill,
  pull and report what finished. A T 1.0 phase that is cut is reported per theorem with its attempts.
- Compute rows (`gpu_seconds`, `gen_tokens`, `attempts`, `actions`, `lean_checks`) are written by the scripts through
  `record.save_config` (arm = `S_base` / `SH_base` / checkpoint label, seed = model seed); the write-up has a per-arm
  table from `registry_merge.py --compute`. The arms of Part A are matched on the protocol (attempt caps and stop
  rule), not on total attempts — an arm that reaches fewer theorems spends more, by design.
