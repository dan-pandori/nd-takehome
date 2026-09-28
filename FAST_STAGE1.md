# FAST_STAGE1.md — training Stage-1 models on the GPU (run `fast-stage1`, 2026-09-28)

**Model every number here is about:** the 3,214,336-parameter from-scratch GPT (4 layers, d 256, 8 heads),
`lean_seq`, cap 6, trained on `data/p2/train_depth3_f0_a1.jsonl` (155,000 records, 0 depth-3) with the
noise-floor control's recipe (`--steps 6000 --bs 128 --lr 1e-3 --min_lr 1e-4 --warmup 200`, cosine), `--val_bins`.
Raw files: `artifacts/fs/` (tables: `artifacts/fs/tables.md`, all numbers: `artifacts/fs/summary.json`,
recomputed by `python3 fs_analysis.py`). Pre-registration: `preregistration/fast-stage1.md`.

## How to train

One model (from scratch on a GPU, `--impl auto` picks the fast path; nothing else changes):

    python3 train.py --data data/p2/train_depth3_f0_a1.jsonl --heldout data/p2/heldout.jsonl \
        --mode lean_seq --steps 6000 --bs 128 --cap 6 --seed 0 --val_bins --out ckpts/x_s0.pt

N seeds on one GPU: separate processes, e.g. `for s in 0 1 2 3; do python3 train.py ... --seed $s --out ckpts/x_s$s.pt & done; wait`.
Each process holds ≈ 0.44 GB of GPU memory. **On an A40, N > 1 gains only ~10 %** (below); on an H100, use N = 8–16.

- `--impl auto` (default): fast for from-scratch training on CUDA — the case tested here. `--init` fine-tunes (expert
  iteration, ladder) and resuming legacy `--state_at` files use the legacy path unless `--impl fast` is given. `--impl legacy`
  reproduces a pre-2026-09-28 trajectory for a seed exactly.
- The training set is tokenised once and cached in `$ND_TRAIN_CACHE` (default `~/.cache/nd_train`); first use of a file
  runs the legacy checks (the legacy load, ≈ 30 s on the A40), after that ≈ 3 s.
- `--no_graph`, `--no_pack`, `--no_compile` switch off the CUDA graph, the packing, and compilation.
  `ND_COMPILE_MODE=max-autotune-no-cudagraphs` cut GPU time per step 14 % in a profile but adds ≈ 20 s of compilation and was not
  equivalence-tested.
- `--state_at` / `--resume` work on the fast path; a fast resume continues within run-to-run noise but is **not** bit-identical
  (smoke test: val 0.3315 resumed vs 0.3342 uninterrupted at step 400).
- The printed `val` (first 2,000 held-out records) is now token-weighted in the fixed `VAL_SHIFT_SEED` presentation; the legacy
  one used the training rng. `--val_bins` numbers have the same definition in both paths.

## What the fast path does (`fast_train.py`)

Same model init per seed, batch, schedule, loss (mean cross-entropy over the batch's proof tokens), AdamW settings,
clipping. Batches are drawn on the GPU with legacy's semantics (a permutation per epoch, remainder dropped); the name offset
is drawn on the GPU (uniform on {0 … 64 − mx}, tested against `shift_abs`); the 128 records are **packed** into one stream with
document-causal `flex_attention` and per-record RoPE positions; the loss is `torch.compile`d; AdamW is fused; the **whole step is
one CUDA graph**. `fast_train_selftest.py` passes (`artifacts/fs/selftest.json`): 0 transform mismatches, offset distribution vs
`shift_abs` min p 0.33, fp32 loss equal to legacy `loss_on` within 4.8e-7 and gradient within 5.6e-7 relative.

## Speed (A40, billed $0.49/h; one process unless N says otherwise)

| | legacy | fast |
|---|---|---|
| one 6,000-step model, process wall-clock | **345 s** | **128–135 s** (2.6–2.7×) |
| of which compile + graph capture | — | 9–15 s |
| training ms/step | 48.9 | 16.8 |
| useful tokens/s in the training loop (prompt + proof, non-pad; excl. validation, incl. compile) | 362k | 921k |
| model FLOP/s as % of A40 bf16 dense peak (6·P·tokens, 149.7 TFLOP/s) | 4.7 % | 11.9 % |
| computed / useful tokens (padding waste) | 1.97× | 1.10× |
| peak GPU memory | — | 0.44 GB |

Seeds per GPU, aggregate steps/s (A40): fast **44.5 / 47.8 / 49.6 / 47.7** at N = 1 / 2 / 4 / 8; legacy 11.9 / 14.0 / 15.6 at
N = 1 / 2 / 4 (1,000-step waves, incl. start-up). One fast process already keeps the A40 busy (profile: 16 ms of kernels per
16.6 ms step), so per-GPU throughput is **≈ 3.2× legacy's best**, not 10×. Batch 512 is no faster per token (64 ms/step).
H100 SXM ($3.49/h): 4.1 ms/step alone, aggregate 65 / 125 / 133 / 179 / 188 steps/s at N = 1 / 2 / 4 / 8 / 16 (2,000-step
waves) — ≈ 3.8× an A40, ≈ 1.9× the cost per model.

The brief's starting point (215 ms/step, 1,288 s/model) was legacy **sharing a GPU**: legacy alone on an A40 is 48.9 ms/step.
Against 1,288 s the fast path is ≈ 10× per model; against legacy alone it is 2.6×.

## Equivalence (new = `--impl fast` seeds 0–7; old = `stage1-dynamics` arm C seeds 0–7, legacy, same command)

Held-out greedy under Lean alone (`sd_eval.py`, batch 512, max_new 400, arm C's settings); validation loss at step 6000.
MDD at n = 8 per arm = 1.506 × NOISE_FLOOR sd (greedy) or × arm C's sd (val loss).

| quantity | slice | legacy | fast | Δ | MDD | within |
|---|---|---|---|---|---|---|
| greedy | all | 0.9105 | 0.9001 | −1.04 pp | 4.58 pp | yes |
| greedy | len 2 | 0.9960 | 0.9939 | −0.21 pp | 0.47 pp | yes |
| greedy | len 3 | 0.9864 | 0.9879 | +0.15 pp | 0.73 pp | yes |
| greedy | len 4 | 0.9469 | 0.9537 | +0.69 pp | 2.28 pp | yes |
| greedy | len 5 | 0.9135 | 0.9189 | +0.54 pp | 2.26 pp | yes |
| greedy | len 6 | 0.7096 | 0.6459 | −6.37 pp | 22.94 pp | yes |
| greedy | len 6 non-depth-3 | 0.8770 | 0.8880 | +1.10 pp | 5.52 pp | yes |
| val loss | all | 0.05101 | 0.05124 | +0.00023 | 0.00219 | yes |
| val loss | len 2 | 0.07817 | 0.07824 | +0.00007 | 0.00036 | yes |
| val loss | len 3 | 0.06780 | 0.06780 | 0.00000 | 0.00045 | yes |
| val loss | len 4 | 0.05139 | 0.05111 | −0.00028 | 0.00049 | yes |
| val loss | len 5 | 0.03958 | 0.03964 | +0.00006 | 0.00077 | yes |
| val loss | len 6 | 0.04238 | 0.04322 | +0.00084 | 0.00775 | yes |
| val loss | len 6 non-depth-3 | 0.04551 | 0.04533 | −0.00017 | 0.00084 | yes |

**14 / 14 within.** Depth-3 (bimodal, not a criterion): 4 / 8 fast seeds in the high mode (> 0.44) vs 6 / 8 arm C and 3 / 8 arm
R (legacy replicates). Per-seed values and IQMs with stratified-bootstrap 95 % intervals are in `summary.json`. Caveat: the
"len 6 non-depth-3" MDD uses NOISE_FLOOR's 247-theorem "6-line no-pattern" sd as a pre-registered proxy for this 500-theorem slice.
