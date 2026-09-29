# Results registry and checkpoint upload on save

Run `results-registry` (2026-09-29; proposal 15 §5). Code: `record.py`, `registry_merge.py`, `registry_backfill.py`,
`registry_acceptance.py`, `tests/test_registry.py`.

## What changed for every run

- **`save_ckpt` uploads before it returns** to `hf://buckets/dan-pandori/nd-rl/<ND_RUN_ID>/ckpts/<path below ckpts/>`,
  checks the bucket copy's size, writes `<ckpt>.upload.json` `{md5, bytes, uri, utc, upload_s}` and a `ckpt_saved`
  row. It **raises** if the upload fails (the file stays on disk; re-upload with `python3 record.py publish <ckpt>`).
- **Scripts that save checkpoints check first** (`record.preflight()`: `train.py`, `state_train.py`, `grpo.py`, and
  the EI drivers unless `--no_train`): no `ND_RUN_ID` or no `hf` CLI stops the script before training.
- So every pod job exports `ND_RUN_ID=<run id>` and has `huggingface_hub` installed and the token installed
  (`podtoken`). Tests and local scratch set `ND_OFFLINE=1`.
- Measured on an RTX 3090 pod: 3.4–7.4 s per 12.9 MB checkpoint and 6.0 s for a 38.6 MB resumable state file.
  `record()` costs 0.06 ms per row.

| env | meaning |
|---|---|
| `ND_RUN_ID` | run id: the bucket prefix for checkpoints and the registry directory. Required for uploads |
| `ND_OFFLINE=1` | no uploads and no syncs; rows are still written |
| `ND_REGISTRY=0` / `ND_REGISTRY_SYNC=0` | write no rows / write rows but never sync them |
| `ND_ARM`, `ND_SEED`, `ND_ROLE` | default labels (a label passed in code wins). The EI drivers set `ND_ARM` for their `train.py` children |
| `ND_GIT_SHA` or `.git_sha` | commit, for code copied without `.git` (`pod/rr/sync.sh` writes `.git_sha`) |
| `ND_REGISTRY_SYNC_S` | seconds between syncs (default 120; always synced at exit) |

## Where rows go

Each process appends to `artifacts/<run-id>/registry/<utc>_<host>_<pid>.jsonl`, and that file is synced to
`hf://…/registry/<run-id>/<same name>`. There is one file per process, so two pods, or two jobs on one pod, never
overwrite each other's rows when pulled. Pull `artifacts/<run-id>/registry/` with the rest of the artifacts.

## Schema (one JSON object per row, `schema: 1`)

`run_id, metric, value, n, arm, seed, role, split, ckpt, ckpt_md5, ckpt_uri, data, data_md5, source, script,
git_sha, git_dirty, config, labels{…}, host, utc, backfilled`

- `seed` is the model's **training** seed where the checkpoint records it; a sampling seed is `labels.sample_seed`.
- `role`: `stage1` (from-scratch `train.py` checkpoint), `finetune` (`train.py --init`), `init` (an RL driver's
  round measured on its starting checkpoint), `rl` (a round checkpoint), `frozen` (`--no_train` control).
- `split` is the evaluated file's stem (`data/p2/heldout.jsonl` → `heldout`, `heldout_B_d3.jsonl` → `heldout_B_d3`).
  The EI drivers' targets and transfer rows use `targets` / `transfer`. `data` holds the exact file and its md5.
- `config` is the script's full argparse config. `source` is the file the number can be re-derived from.
- `labels`: `L` (length bin; absent = all lengths), `slice`, `round`, `k`, `decode`, `solved`, `ci`, `n_params`,
  `format`, `step`, `checker`, `kind`, …

Metrics: `<split>_greedy_acc`, `<split>_pass@<k>`, `<split>_solved_cum` / `_union`, `<split>_lstar_<…>`,
`<split>_sample_acc`, `<split>_mean_term_size`, `<split>_mean_written_lines` (sd_eval), `coverage_pass@<B>`,
`coverage_solved_frac`, `coverage_sample_rate`, `train_loss`, `val2k_loss`, `val_loss`, `ckpt_saved`
(value = bytes); backfilled headline leaves are `summary:<json/path>`.

## Instrumented scripts

`train.py` / `fast_train.py` / `state_train.py` (final losses and every checkpoint), `eval_set.py`, `state_eval.py`,
`sd_eval.py` (overall and per length / slice), `coverage.py` (per shard, at the end), `expert_iter.py`,
`ladder_ei.py`, `state_ladder_ei.py`, `grpo.py` (each round's headline stats; per-length detail stays in
`round_<r>.json`). A new script calls `record.save_config(vars(args), out)` once (since run repo-hygiene: it is
`set_config` plus a file — `<out>.args.json`, or `<outdir>/args.json` when `out` ends in `/` — holding `vars(args)` and
a `_meta` key {script, argv, run_id, git_sha, git_dirty, host, utc}; every later row names it as label `config_file`),
then `record.record(metric, value, n=…, **labels)`, or `record.summary_rows` / `record.round_stats` for the standard
shapes. CI (`tests/test_configs.py`) fails if a script that takes `--out`/`--outdir` does not call `save_config`.

## Backfill

`registry_backfill.py --fetch` downloads the result files of 32 reviewed runs. That is every run with a digest in
nd-rl `experiment-summaries/`, plus the fork's `followup` and `ignition`; `podjob` has no result files. They go to
`artifacts/results-registry/backfill_src/` (not committed: re-fetchable). `registry_backfill.py` then writes
`artifacts/results-registry/registry/backfill_<run>.jsonl.gz`: **298,943 rows**, `backfilled: true`, with
`labels.checker` = `lean+nd_verify` (runs before 2026-09-27) or `lean`. It reads four kinds of file:

- EI / GRPO `round_<r>.json` go through `round_stats`, the same code live runs use.
- `eval_set` summaries and `sd_eval` summaries. The latter carry the model label: `n_params`, format, training seed.
- Every numeric leaf of each `summary*.json` becomes a row with metric `summary:<path>`.
- Other files are counted as skipped in `artifacts/results-registry/backfill_report.json`.

Backfilled rows have no md5 (the old checkpoints were not re-downloaded). `labels.ckpt_uri_backfill` is set where
the bucket listing has the checkpoint. Role is inferred from `args.json` (`--init`, `--no_train`). For
ds-composition and novelty-campaign rounds there is no `args.json`, so the role is inferred from the round files
(`labels.role_from`).

## Querying

```
python3 registry_merge.py --bucket --no_local --out /tmp/reg      # every run's rows from the bucket -> .jsonl + .csv
python3 registry_merge.py --q metric=heldout_greedy_acc role=stage1,init,frozen L= slice= \
        --cols run_id,arm,seed,role,data,value,n,ckpt              # held-out greedy of every control checkpoint
python3 registry_merge.py --q run_id=state-env metric=transfer_solved_cum arm=la_T1_S_s0 --cols round,value,solved
```

The syntax is `key=a,b` (one of), `key=` (missing), `key!=a`, `key~sub` (contains). Keys are columns or label
names. Exact duplicate rows are dropped. Caveats:

- A held-out number is only comparable across rows with the same `data`.
- `frozen` arms re-measure the same checkpoint every round.
- `stage1` includes stage1-dynamics' intermediate `step` checkpoints.
- `summary:` rows are only as well labelled as the run's summary file.
