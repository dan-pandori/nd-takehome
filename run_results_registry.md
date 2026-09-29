# results-registry — one results table; checkpoints to the bucket on save

**Built.**
- `save_ckpt` uploads each checkpoint to `hf://…/<ND_RUN_ID>/ckpts/` before returning. It records the md5 and URI,
  and raises if the upload fails.
- Training scripts check `ND_RUN_ID` and the `hf` CLI before the first step, not at the first save.
- `record.py` writes one row per headline number, with run, arm, seed, role, git SHA, config, data md5,
  checkpoint md5 + URI and source file.
- Instrumented: `train`, `eval_set`, `sd_eval`, `coverage`, the EI / ladder / state / GRPO drivers.
- `registry_merge.py` merges and queries every run's rows. `registry_backfill.py` loaded 32 reviewed runs:
  298,943 rows.
- Details are in `REGISTRY.md`.

**Expected vs measured** (pre-registered; `numbers.md` § results-registry):

| | expected | measured |
|---|---|---|
| checkpoint URIs download to the recorded md5 | 100 % | 5 / 5 |
| negative controls fail | 3 / 3 | 3 / 3 |
| control held-out accuracy by run, one filter | ≥ 8 runs | 25 runs |
| headline numbers reproduced exactly | 3 / 3 | 3 / 3 (one substitute named in advance) |
| cost | < 5 ms/row, < 30 s/ckpt | 0.06 ms, 3–7 s |

The smoke models are throwaways, not results. They are a 3.2 M `lean_seq` Stage-1 model trained for 300 steps,
and two 30-step EI fine-tunes of fast-stage1's `fast1_s0`.

**Deviation.** Rows go to one file per process, not one per run, because pulls from a second pod overwrote a
single per-run file.

**Limits.**
- Backfilled rows carry no checkpoint md5.
- Rows from `summary:` leaves are only as well labelled as each run's summary file.
- The lean-prefilter headline (1,310,119) is a sum over selected corpus rows, not a stored value, so the registry
  does not hold it directly.
- Proposed policy text is in `QUESTIONS.md`.

Spend: 0.21 pod-hours, $0.10.
