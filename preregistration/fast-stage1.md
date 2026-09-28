# Pre-registration — run `fast-stage1` (proposal 15, item 1)

Written 2026-09-28 ~16:25 UTC, before any pod. Executor, branch `dan_fast-stage1` (fork, from `origin/dan`).

## Question

Can Stage-1 training (`train.py`) produce **the same models ≥ 5× faster** (aim 10×) on one GPU, and
how many seeds can share one GPU? "The same models" is an equivalence claim, tested below.

## Model every number is about

3,214,336-parameter from-scratch GPT (4 layers, d 256, 8 heads), `lean_seq`, cap 6, trained on
`data/p2/train_depth3_f0_a1.jsonl` (155,000 records, 31,000 per length 2–6, 0 depth-3), cosine
schedule, `--steps 6000 --bs 128 --lr 1e-3 --min_lr 1e-4 --warmup 200 --wd 0.1`, `--val_bins`.
This is `stage1-dynamics` arm C's command (which is the noise-floor control's).

## Design

**New path.** `train.py --impl fast` (the old code stays as `--impl legacy`, the default until the
acceptance test passes; CLI and checkpoint format unchanged):

1. Pre-tokenise the training set once (cached next to the data, keyed on file size/mtime + mode + cap)
   into GPU-resident tensors; the old per-record checks run when the cache is built.
2. Sample batches on the GPU with the old semantics: one shuffled permutation per epoch, `bs` indices
   per step without replacement, the < `bs` remainder dropped at the epoch end.
3. Name augmentation on the GPU with **the same distribution**: `lean_seq`/`abs`, one offset per row
   uniform on {0 … 64 − mx}; `lean_rand`, a uniform random injective map (first `mx` of a random
   permutation). Tested: exact transform for a given offset, and χ² of the drawn offsets per `mx` against
   uniform (and a direct comparison with `shift_abs` draws).
4. **Pack** each batch's 128 sequences end to end into one stream with document-causal attention
   (`flex_attention` block mask) and per-document RoPE positions, so no pad tokens are computed. If
   `flex_attention` is unavailable or slower, fall back to padding to a fixed length bucket; the choice is
   logged. Loss is unchanged: mean cross-entropy over the batch's proof tokens.
5. `torch.compile`, fused AdamW, bf16 autocast as before; the per-length validation is run on
   pre-tokenised GPU tensors with the same fixed presentation (`VAL_SHIFT_SEED`) and the same metric
   definitions.

**Same recipe.** Batch 128, 6,000 steps, same schedule: same tokens (≈ 78 M presented), same epochs
(4.95), same final LR. Each step's loss is mathematically the same function of the same kind of batch;
only float order and the RNG streams differ. A batch-size sweep (bs 512, LR ×2, 1,500 steps = equal
tokens) is **exploratory only**, run if budget allows, and not part of the acceptance test.

**Equivalence test.** New arm: `--impl fast`, seeds 0–7 (n = 8). Old arm: stage1-dynamics arm C,
seeds 0–7 (n = 8), same command and data, trained on A40s with the legacy code; its metrics and
held-out evaluations are on file (`origin/dan_stage1-dynamics:artifacts/sd/{m_c_s*.jsonl,ev/c_s*.json}`,
copied to `artifacts/fs/old/`). Arm R (8 same-command replicates of seeds 0/1) is reported as a second
old-recipe reference, not used for the pass/fail. Held-out greedy is measured with arm C's exact
`sd_eval.py` settings (batch 512, max_new 400, fast sampler path; judge: Lean alone) so the sampler
settings are held fixed across arms.

**Pass criterion (all must hold).** At step 6000, for each slice S in {all, len2, len3, len4, len5, len6,
6-line non-depth-3}:
- held-out greedy: |mean_new − mean_C| < MDD = 1.506 × (NOISE_FLOOR.md pooled sd for S). 1.506 is
  NOISE_FLOOR's formula `(t.975 + t.80) · sqrt(2/n)` at n = 8 per arm (df 14). MDDs: all 4.6 pp, len2
  0.47 pp, len3 0.73 pp, len4 2.28 pp, len5 2.26 pp, len6 22.9 pp, 6-line non-depth-3 5.5 pp.
- validation loss (`--val_bins`, whole held-out file, per bin): |mean_new − mean_C| < 1.506 × sd_C(S),
  sd_C taken from arm C's 8 seeds (NOISE_FLOOR has no val-loss floor). With sd_C: all 0.0023, len2
  0.0003, len3 0.0005, len4 0.0005, len5 0.0008, len6 0.0077, 6-line non-depth-3 0.0009.
The depth-3 slice is bimodal and not resolvable at n = 8 (NOISE_FLOOR): reported as the high-mode
count (> 0.44) new vs C, not a criterion. Under a true null each comparison exceeds its MDD with
p ≈ 0.01, so 14 comparisons give ≈ 13 % chance of a spurious failure; a failure on one slice will be
re-tested with 8 more new seeds (8–15) before it is called, and that is the only re-test allowed.

**Speed measurements (A40, the baseline's class).** Wall-clock per model (with and without
`--val_bins`), ms/step, useful (non-pad) tokens/s, model FLOP/s as a fraction of the A40's 149.7
TFLOP/s bf16 dense peak (6 · params · tokens + attention), padding waste (computed tokens / useful
tokens), compile time, and aggregate throughput with N = 1, 2, 4, 8 concurrent seed processes on one
GPU (and CUDA MPS if the pod allows it). The legacy path is re-timed on the same pod for 1,000 steps.

## Expected results (falsifiable)

- Legacy on the pod: 180–230 ms/step (brief: 215 ms on an A40); padding waste 1.8–2.0×.
- Fast path, one model, bs 128: ≤ 25 ms/step, i.e. **≥ 8× per step**; a full 6,000-step model with
  `--val_bins` in ≤ 4 min including compilation (≥ 5×, target 10×); padding waste ≤ 1.1×.
- Single model still uses ≤ 10 % of bf16 peak (it is small and launch-bound); aggregate over N seeds per
  GPU rises to ≥ 2× the single-model throughput by N = 4 and saturates by N = 8.
- Equivalence: **pass on all 14 comparisons**; I expect every |Δ| under half its MDD.
- If the batch sweep runs: bs 512 at equal tokens is within the MDD on lengths 2–5 but I do not predict
  the 6-line bin.

## Budget and stop rule

`podbudget fast-stage1 --set 10 5` before the first pod: **$5, 10 pod-hours**, A40 (≈ $0.49/h billed; the
rate is recorded from `podnew`). Stop and report if spend reaches $4.50 or the fast path cannot get
under 50 ms/step after 2 pod-hours of work. If the equivalence test fails after the one re-test, the
fast path is not merged into `dan` and the write-up says so.
