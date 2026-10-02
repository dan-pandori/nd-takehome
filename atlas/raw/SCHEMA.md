# evidence-atlas raw-part schema (shared by all extraction agents)

Each part `<P>` writes, under `atlas/raw/`:

## `<P>_map.csv` — one row per experiment (csv, quoted with Python csv module)
columns:
`id,date,title,area,owner,model,params,format,init,train_set,cap,protocol,checker,headline,review_status,source`
- `id`: short kebab slug, unique (e.g. `support-curves`, `robbie-factorial-0929`).
- `date`: YYYY-MM-DD (start or report date).
- `area`: one of `create_vs_elicit`, `data_caps`, `format`, `pretrain_recipe`, `rl_algorithm`, `interface`,
  `search_exploration`, `infrastructure`, `measurement` (noise floor, judges, metrics), `llm_pretrained` (big pretrained LLMs), `other`.
  Pick the primary one; a secondary may be appended after `;`.
- `owner`: `dan-agents` (the fork / nd-rl dan runs), `dan-codex` (June sprints / Sept imports), `robbie`, `leon`, `dmitry`, `charles`, or other name.
- `model`: checkpoint label(s), e.g. `SN-cap12 s0-s3 Stage-1 + T1 ladder`, `Qwen3-8B`.
- `params`: e.g. `3.2M`, `9.56M`, `25M/85M`, `8B`.
- `format`: `lean_seq`, `lean_staten` (proof-state), `token` (ND token), `free-form Lean`, `text`, mixed → list with `/`.
- `init`: `scratch` or `pretrained:<name>`.
- `train_set`: short label (e.g. `cap-6 control 155k`, `K12 155k`).
- `cap`: training-proof length cap if relevant (e.g. `6`, `12`), else blank.
- `protocol`: pool(s), k, temperature, seeds, e.g. `textbook72 pass@256 T1.0; 2 seeds`.
- `checker`: `lean_only`, `lean_and_ndverify`, `nd_verify`, `lean_check(free-form)`, `other:<x>`, or `n/a`.
- `headline`: one sentence with the key number(s), copied faithfully with units.
- `review_status`: `reviewed`, `reviewed-findings` (review found result-changing issues), `unreviewed`, `n/a`.
- `source`: `<repo>:<branch>:<path>` (repo = `nd-rl` or `fork`).

## `<P>_metrics.csv` — long-format numbers usable in figures (only where a metric is on a shared axis)
columns:
`family,model_label,params,format,init,train_set,cap,stage,seed,pool,n_pool,metric,k,temperature,value,checker,judge,date,provenance,source_file`
- `family`: model-family label used on a shared axis (e.g. `ours-3.2M-SN-cap12`, `best-9.56M-cap6`, `robbie-factorial:<cell>`).
- `stage`: `frozen` (Stage-1 only), `T1` (after the T1 / ladder RL), `rlN` (round N), or method name.
- `metric`: `solved` (number of pool theorems with ≥ 1 accepted proof among k samples), `pass_at_k_frac`,
  `dev_metric` (Robbie's dev metric), `L_star`, `long_solves`, `greedy_acc`, or other named metric.
- `value`: numeric. For `solved` give the count, with `n_pool` the pool size.
- `provenance`: `recomputed` (you computed it from per-theorem/per-sample files: name them) or `copied` (from a summary's text/table).
- `source_file`: the file you computed from or copied from, as `<repo>:<branch>:<path>` or `hf://buckets/...`.
- one row per seed when per-seed values exist; do NOT average across seeds in this file.

## `<P>_notes.md` — ≤ 600 words
protocol differences you noticed (checker, k, temperature, pool versions, judge versions, seeds), comparisons that are /
are not apples to apples, open questions the evidence makes visible, and anything you could not find.

Rules: read-only on every source; never push, never comment on PRs; never run `test_run_once.sh`. Run shell commands
one at a time (the VPS allows at most 4 processes in total across all agents; do not use `&`, `xargs -P` or parallel
tool calls). Read only the parts of files you need (grep, line ranges). Downloads (`hf buckets cp ...` / `hf download`)
go to `/tmp/atlas/cache/` and must be small (per-theorem/per-sample summaries, not checkpoints); check `df -h /` stays < 80 %.
Never print tokens. Be faithful: a number not found is left blank and named in notes, never guessed.
