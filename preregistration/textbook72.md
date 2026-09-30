# Pre-registration: textbook72 — the proof-state models on the group's 72 textbook problems

Run id `textbook72`. Written 2026-09-30 ~15:10 UTC by the executor, before any pod. Sampling read-outs of existing
checkpoints only; no training, no tuning.

## Question

How many of the group's 72 textbook problems (Robbie's set: dev58 + train14, from Dmitry's cap-comparison eval data)
do our proof-state models solve at pass@256, T 0.8 — the apples-to-apples number next to Robbie's naive pipeline
(13 / 72) and combined model (31 / 72)?

## Problems

`data/eval_only/textbook72/{textbook_dev,textbook_train}.jsonl` + `MANIFEST.json`, copied from nd-rl
`origin/robbie-experiments:code/experiments/current/factorial_20260929/textbook72/`; both sha256 match the manifest
(dev `1b04192d…`, train `e6a219e0…`). Eval only: never trained or tuned on (manifest rule). Reported dev58, train14 and
all 72. `reference_lines` exists on the 58 dev records only; the 14 train records have none and form their own bin.
Dev58 by `reference_lines`: 1–5: 5, 6–10: 24, 11–15: 16, 16+: 13 (max 33). Five problems involve `F`.

Contamination check (before sampling, no pod needed for the decision): renaming class (`gen.canon_key`, and a
premise-order-free variant) of the 72 against the cap-6 control set (`train_depth3_f0_a1.jsonl`), K12's cap-12 set
(`train_k12.jsonl`), `rl_targets.jsonl` (ladder and old), and the EI replay sets (`mix_1..8.jsonl` of every T1 run
scored). Overlapping problems are reported separately, never dropped.

## Models (12 checkpoints; all 3,216,384 params, `lean_staten`, from scratch)

| label | checkpoints | Stage-1 data | RL |
|---|---|---|---|
| SN-cap12 T1 | `state-cap12/ckpts/sc12/ladder/la_T1_SN12_s{0..3}_r8.pt` | K12 `train_k12.jsonl` (cap 12, 155 k) | 8 ladder EI rounds |
| SN-cap12 frozen | `state-cap12/ckpts/sc12/stage1_SN12_s{0..3}.pt` | same | none |
| SN-v2 cap-6 T1 | `state-env/ckpts/se/ladder/la_T1_SN_s{0,1}_r8.pt` | `p2/train_depth3_f0_a1.jsonl` (cap 6, 155 k) | 8 ladder EI rounds |
| SN-v2 cap-6 frozen | `state-env/ckpts/se/stage1_SN_s{0,1}.pt` | same | none |

"SN-v2" = these SN checkpoints sampled with `Env(canon=True, assign=True)` (the environment names introduced hypotheses),
which is `state_sample.env_generate`'s behaviour for a canonical tokenizer.

## Design

`state_eval.py --k 256 --temperature 0.8 --seed 0 --max_steps 96 --max_action 512 --batch 4096 --lenfield reference_lines`
on all 72 for each of the 12 checkpoints, same seed and settings for every arm (the state-readouts part-B settings).
Solved = ≥ 1 of 256 attempts accepted. **Primary judge: Lean alone** (`lean_judge`, strict `lean_seq` grammar + Lean).
Secondary, labelled, judges nothing: how many Lean-accepted proofs/problems `nd_verify` would reject (Robbie's reward is
Lean ∧ `nd_verify`). Reported: step-cap (96) and action-cap (512) hit rates, peak GPU memory, solved per checkpoint on
dev58 / train14 / 72, by `reference_lines` bin, problems no checkpoint solves, per-problem match to Robbie's combined
model if his files name them, 2–3 longest accepted proofs in Lean, lines and term size. Compute per checkpoint
(GPU-seconds + type, attempts, actions, generated tokens, Lean checks; no training) in the registry and a table.

## Expected results (per checkpoint, all 72; union over seeds in brackets)

Anchor: on the 760 textbook-schema instances (state-readouts § B, same settings) SN-cap12 T1 solves 513–552 (≈ 70 %),
frozen 275–361 (≈ 42 %); both have `L*` ≈ 12, and dev58 has 29 / 58 problems with `reference_lines` ≥ 11.

- **SN-cap12 T1: 36 / 72 per seed (range 28–44) [union 42].** Near-everything ≤ 10 reference lines and train14, about a
  third of 11–15, ≤ 2 of 16+ — the length wall at `L*` ≈ 12 dominates; Lean proofs can be shorter than ND references.
- **SN-cap12 frozen: 24 / 72 per seed (range 16–32) [union 30].** RL lifted the 760 pool by ≈ 28 points; the 72 are
  longer, so the gain here is smaller in problems.
- **SN-v2 cap-6 T1: 32 / 72 per seed (range 24–40).** Same `L*` (12) as SN-cap12 T1 and a similar transfer count, but
  cap-6 Stage-1 data has seen fewer long proofs.
- SN-v2 cap-6 frozen: 18 / 72 (range 10–26).
- Falsifiable: (a) T1 − frozen (SN-cap12, paired by seed) ≥ +6 on each seed; (b) no checkpoint solves more than 3 of the
  13 problems with `reference_lines` ≥ 16; (c) SN-cap12 T1's median seed ≥ 31 (Robbie's combined model); (d) step-cap and
  action-cap hit rates each ≤ 0.1 % of attempts; (e) the contamination check finds 0–5 overlaps, all with short problems.

## Noise floor

At n = 4 seeds per arm, paired by seed, with a per-seed SD of the difference ≈ 4 problems (from the 760-pool spread,
T1 SD ≈ 2.5 %, frozen ≈ 5 %, scaled to 72, plus Bernoulli noise), the MDD of the T1 − frozen mean difference is ≈ 8
problems (paired t, 80 % power, α 0.05). The predicted +12 is above it. SN-v2 has n = 2: descriptive only. The
comparison with Robbie's 31 is a single external number (different models, format, checker): descriptive only. Per-seed
values, IQM and stratified-bootstrap 95 % intervals are reported.

## Budget and stop rule

$3 / 6 pod-hours (`podbudget textbook72 --set 6 3`). One A40 (or 48 GB card; ≈ $0.49/h) running the 12 read-outs in
sequence; expected < 1.5 pod-hours. Stop: if the pod reaches 4 pod-hours or $2.50, finish the checkpoint in progress,
report what finished, and delete the pod. A 24 GB card runs batch 2,048 (settings held fixed across arms either way).
