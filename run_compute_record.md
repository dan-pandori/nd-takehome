# run compute-record: the scripts record their own compute

**What.** `record.save_config()` now opens a process-level compute block. At exit it writes registry rows
`gpu_seconds` (wall-clock × GPUs, clock from process start; `labels.gpu`, or `labels.device = cpu`). It also writes
each non-zero counter: `gen_tokens`, `attempts`, `actions`, `train_steps`, `train_tokens`, `lean_checks`.
The sampler, trainers and Lean judge fill the counters. The RL drivers split each round into
`sample` / `eval` / `finetune` (GRPO: `update`) rows with `labels.round`. Time is exclusive, so sums never double
count. `registry_merge.py --compute` prints the per-arm table.

**Expected vs outcome** (A40; 3.2 M `lean_seq` from-scratch mechanics model `ckpts/cr/fast_s0.pt`; `numbers.md`):

| pre-registered | outcome |
|---|---|
| overhead < 1 % of step time | **met**: 0.025 % (49.7 µs per 201.7 ms legacy step); fast path counts once per run |
| counters = independent counts exactly | **met**: 20 / 20 checks equal (tokens, steps, attempts, Lean checks; EI, GRPO) |
| `gpu_seconds` within 5 % of wall-clock (jobs ≥ ~3 min) | **met**: 0.989 (6 min), 0.975 (2 min). Shorter jobs miss by a fixed ~1.5–2 s a process, the row upload at exit: 0.96 (1 min), 0.94 (80 s, 3 processes), 0.92 (27 s) |
| CI green | **met**: GitHub Actions green, compute checks included (runs in `log.md`) |

**Limits.** GPU-seconds are seconds a GPU was *held*, not utilisation: five co-tenant jobs on one card count 5×. A
process killed by a signal writes no rows. Validation and prefill tokens are not counted.
