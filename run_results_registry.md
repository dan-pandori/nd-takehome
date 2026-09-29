# results-registry — one results table; checkpoints to the bucket on save

**Built.**
- `save_ckpt` uploads to `hf://…/<ND_RUN_ID>/ckpts/` before returning. It records the md5 and URI, and raises on
  failure.
- Training scripts check `ND_RUN_ID` and `hf` before the first step.
- `record.py` writes one row per headline number (run, arm, seed, role, SHA, config, data md5, checkpoint md5 +
  URI, source file).
- Instrumented: `train`, `eval_set`, `sd_eval`, `coverage`, and the EI / ladder / state / GRPO drivers.
- `registry_merge.py` merges and queries the rows. The backfill covers 32 reviewed runs (298,943 rows).
- See `REGISTRY.md`.

**Expected vs measured** (`numbers.md`):

| check | expected | measured |
|---|---|---|
| checkpoint URI → recorded md5 | 100 % | 5 / 5 |
| negative controls fail | 3 / 3 | 3 / 3 |
| control held-out accuracy by run | ≥ 8 runs | 25 |
| headlines reproduced exactly | 3 / 3 | 3 / 3 (one pre-named substitute) |
| cost | < 5 ms/row, < 30 s/ckpt | 0.06 ms, 3–7 s |

The smoke models are throwaways: a 3.2 M `lean_seq` model trained for 300 steps, and two 30-step EI fine-tunes of
fast-stage1's `fast1_s0`.

**Deviation.** Rows go to one file per process: with a single per-run file, a pull from a second pod overwrites it.

**Limits.**
- Backfilled rows have no checkpoint md5.
- `summary:` rows are only as well labelled as each run's summary file.
- lean-prefilter's 1,310,119 is a sum over selected corpus rows, not a stored value.
- The proposed policy text is in `QUESTIONS.md`.

Spend: 0.21 pod-hours, $0.10.
