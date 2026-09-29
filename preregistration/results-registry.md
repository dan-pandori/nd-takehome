# Pre-registration — results-registry (proposal 15 §5)

Run id `results-registry`. Executor. Written 2026-09-29 ≈ 00:45 UTC, before any pod. Budget $1, 2 pod-hours
(smoke tests only). Branch `dan_results-registry` of the fork, from `origin/dan` after `fast-stage1` and
`lean-prefilter`.

## Question

Can one structured registry replace "numbers in `numbers.md` prose + checkpoints uploaded by hand at the end"?
Concretely: (i) does every checkpoint a script saves reach the bucket before the script moves on, with an md5
that the downloaded copy matches; (ii) can a reader answer "every held-out accuracy of the control checkpoints, by
run" from one merged table without reading prose; (iii) does a backfill from the reviewed runs' summary files
reproduce their headline numbers exactly.

No model-quality number is produced here. The smoke-test model is a throwaway (few hundred steps) and every number
measured on it is labelled as such.

## Design (what will actually be built and run)

1. `model.save_ckpt` writes the file, computes its md5, uploads it to
   `hf://buckets/dan-pandori/nd-rl/<ND_RUN_ID>/ckpts/<path under ckpts/>` with `hf buckets cp`, retries, and
   **raises** if the upload fails or `ND_RUN_ID` is unset. `ND_CKPT_OFFLINE=1` is the explicit opt-out (tests,
   local scratch). A sidecar `<ckpt>.upload.json` holds `{md5, bytes, uri, utc}`, and a registry row
   `metric=ckpt_saved` is written for every checkpoint.
2. `record.py`: `record(metric, value, n=None, **labels)` appends one JSON row (schema in `REGISTRY.md`) with run id,
   arm, seed, git SHA, the calling script's full config, dataset file + md5, checkpoint md5 + URI, metric, value,
   n, source file, host, UTC. Rows go to `artifacts/<run-id>/registry/<utc>_<host>_<pid>.jsonl` — one file per
   process, so two pods or two jobs never clobber each other (a deviation from the brief's single
   `registry.jsonl`; a single file per run is overwritten by every pull from a second pod). Each file is synced to
   `hf://…/registry/<run-id>/<same name>` (throttled, and at exit). `registry_merge.py` builds one table (JSONL +
   CSV) from every file, local or bucket.
3. Instrumented: `train.py` / `fast_train.py` (final train and val loss, steps, seconds), `eval_set.py`
   (solved fraction overall and per length bin), `coverage.py` (per-shard pass@B and per-sample rate),
   `expert_iter.py`, `ladder_ei.py`, `state_ladder_ei.py`, `grpo.py` (per-round headline stats), `state_eval.py`,
   `state_train.py`. `support.py` is not merged into the fork's `dan`; skipped.
4. Backfill (`registry_backfill.py`): for every run with a librarian digest in `nd-rl/experiment-summaries/`
   (the list of reviewed runs), download its `summary*.json` from the bucket into
   `artifacts/rr/backfill_src/`, and write (a) one `backfilled` row per numeric leaf (metric = JSON path) and (b)
   curated rows with semantic labels for held-out greedy accuracy of Stage-1 / control checkpoints, where the
   summary holds them.
5. Smoke run on one RTX 3090 pod: `train.py --mode lean_seq --steps 300` (+ `--ckpt_every 150`), one greedy
   `eval_set.py` on 500 held-out theorems, one `coverage.py` job on 2 theorems at k = 256.

## Expected results (falsifiable)

- **E1.** Every `ckpt_saved` row from the smoke run (≥ 3: step 150, final, plus any state) has a URI that downloads to
  a file whose md5 equals the recorded md5: 100 %, no exceptions.
- **E2 (negative controls, must fail).** (a) A downloaded checkpoint with one byte flipped fails the md5 check;
  (b) `save_ckpt` with `ND_RUN_ID` unset raises; (c) `save_ckpt` pointed at a non-existent bucket raises (does not
  return). If any of these passes silently the harness is broken and E1 means nothing.
- **E3.** The merged table answers "every held-out accuracy of the control checkpoints, by run" with one filter
  (`metric == heldout_greedy_acc`, `role in {stage1, control, frozen}`) and returns rows for **≥ 8 reviewed runs**
  (my estimate of how many reviewed runs recorded a held-out greedy number in a summary file; the smoke run adds
  one more, labelled `smoke`).
- **E4.** Three headline numbers reproduced exactly (string-equal after `repr`) from the backfill:
  lean-format token-format held-out greedy `P1_heldout_greedy.token_full = 0.948`; ds-generator frozen ladder
  solves C0 = 158 and 114 (of 2,285); lean-prefilter 0 false rejects in 1,310,119 Lean-checked texts. If one of
  them is not in a summary file I will name the substitute before running the check.
- **E5 (cost).** `record()` adds < 5 ms per row excluding sync; the upload in `save_ckpt` adds < 30 s per
  checkpoint of the 3.2 M model on the pod.

## Stop rule

Stop at $0.80 or 1.5 pod-hours. One pod at a time; delete it as soon as its files are pulled.
