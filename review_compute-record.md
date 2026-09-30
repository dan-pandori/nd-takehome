# Review — compute-record (reviewer, 2026-09-30)

Run: `compute-record` (branch `dan_compute-record`, HEAD `3fc57e41`, merged into `dan`). An infrastructure run: the
scripts record their own compute as registry rows (`record.compute` / `record.phase` / `record.child`, counters in the
samplers, trainers and Lean gate). No proof counts, rates or frontiers are claimed. The pre-registration promised
four falsifiable results: (1) helper overhead < 1 % of step time, (2) counters **exactly** equal to independent counts,
(3) on the GPU job `gpu_seconds` within 5 % of the job's own wall-clock for a job ≥ ~3 min, (4) CI green.

Every GPU number below comes from one pod: **NVIDIA A40** (46 GB). Model for the GPU check: `ckpts/cr/fast_s0.pt`,
3,214,336 parameters, `lean_seq`, trained from scratch in this run (6,000 steps, bs 500, on `data/lj/train_retain.jsonl`,
3,000 records). The model matters only as a work generator; no accuracy is claimed. CPU numbers: GitHub Actions
`ubuntu-latest` (torch 2.8.0+cpu) and the 2-vCPU VPS.

Reviewer code: `review/compute-record-recount/` — `rows.py` (compute rows per job vs `walls.jsonl`), `table.py` (my
sums vs `registry_merge.compute_table`), `train_replay.py` (replays train.py's batch draw without torch),
`rv_ci.py` (CPU sampler / trainer counter checks, run in Actions on the throwaway branch `ci-review-compute-record`,
run 36654170471; output in `rv_ci.out`), `term.py` (which rows survive exception / SIGTERM / SIGINT), `bench.py`
(cost of the per-step counter).

## Recount (phase 1, blind)

**Leak disclosure.** Before phase 1, the session's git-status context showed the executor's last five commit subjects,
including "GPU check part 3 … 20/20 checks equal". While locating the run's commits I also read the other commit
subjects (e.g. "review fixes — CUDA errors at exit cannot lose rows; only the process block syncs; fast_train counts
per step"). I did not open `run_compute_record.md`, `numbers.md`, `STATUS.md`, `log.md`, `analysis.json`,
`sample_check.json`, `expect*.json` or `compute_table.tsv` in phase 1.

### Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72` = `origin/main`'s |
| `nd_verify` used as a judge | no new use in the run's diff (`git diff 6b7b2f5e HEAD -- '*.py'`: no `nd_verify` / `verify_text` line added) |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064` = `origin/main`'s; no commit of the run touches it |
| evaluation files read in training code | none added. The GPU-check jobs trained on `data/lj/heldout200.jsonl` (ladder2 targets, GRPO targets) — throwaway checkpoints `ckpts/ladder/cr_ladder2_r*.pt`, `ckpts/cr_grpo_r*.pt`; no result is drawn from them, but they must never be reused as models (they have seen `heldout200`). |
| Lean re-check of ≥ 100 counted proofs per arm | not applicable: the run counts no proofs. |

### Counters vs my independent counts

| quantity | where | counter | my count | how I counted | verdict |
|---|---|---|---|---|---|
| `train_tokens`, `train.py` (legacy), 3 steps × bs 100 over 150 records | CI (mine) | 39,441 | 39,441 | replayed train.py's `random.Random(seed)` batch draw (refill when < bs remain, one `shift_abs` draw per record) | exact |
| `train_tokens`, fast path, 6,000 steps × bs 500 | pod, `fast_s0` | 375,609,000 | 375,609,000 | 1,000 epochs × 375,609 tokens (my tokenisation of `train_retain`) | exact |
| `train_tokens`, 600 steps × bs 500, seeds 0 (legacy ×2), 1 (fast), 2 (fast, per-step counter) | pod | 37,560,900 each | 37,560,900 each | replay | exact |
| `train_tokens`, ladder2 child `train.py` fine-tunes, 300 steps × bs 128 | pod, `mix_1/2.jsonl` from the bucket | 4,540,890; 4,563,097 | 4,540,890; 4,563,097 | replay with the logged seeds 1, 2 | exact |
| `train_steps` | all train jobs | 6,000 / 600 / 300 | same | args | exact |
| `train_steps`, GRPO | pod | r1 3, r2 1 | 3, 1 | steps with `frac_groups_with_variance > 0` in `round_*.json` (steps 4, 5 had no variance → no update) | exact |
| `train_tokens`, GRPO | pod | 4,778; 808 | — | completions not stored | not derivable |
| `gen_tokens`, `sample.generate`, fast+compact / fast no-compact / base, max_new 40 (47/60 rows cut off) | CI (mine) | 2,285 ×3 | 2,285 ×3 | per row: first `<eos>` + 1, else max_new, from `raw` | exact on every path |
| `gen_tokens`, fast, max_new 200 | CI (mine) | 4,644 | 4,644 | same | exact |
| `gen_tokens`, fast, `early='exact'` | CI (mine) | 3,881 | 3,898 | same | differs by 17: the shortcut writes `<eos>` the model never decoded (see findings) |
| `gen_tokens` on the pod (sample check, ladder, ladder2, GRPO) | pod | 513,325 … | — | raw ids not stored | not derivable from files |
| `attempts` | pod | ladder sample 6,400; eval 1,850; GRPO sample 1,536/round, eval 450; sample check 4,000 | 200×32; 50×32+50+200; 3 steps×64×8; 50×4+200+50; 200×20 | args | exact |
| `lean_checks` vs the gate log's `lean_texts` | pod | ladder eval 189; ladder2 r1 4,766, r2 4,871; sample check 0 | 189; 4,766; 4,871; 0 | `*_gate.jsonl` sums in the block's time window | exact |
| `lean_checks`, GRPO (`judge_many`, no gate log) | pod | 199; 12 | — | not logged | not derivable |
| `lean_checks`, CI sampler | CI (mine) | 0 | 0 | my 150-step model got nothing past the prefilter | vacuous — Lean path not exercised by my test |

### `gpu_seconds` vs the job's wall-clock (`walls.jsonl`, `date` around the Python process)

| job | wall s | Σ gpu_seconds | ratio | code |
|---|---|---|---|---|
| train_fast (6,000 steps) | 376.8 | 372.5 | 0.989 | `4c34eb85` (clock from `save_config`) |
| legacy_on_1 / _2 | 129.3 / 129.2 | 126.0 / 125.8 | 0.975 / 0.974 | `4c34eb85` |
| train_fast_short | 59.3 | 56.9 | 0.961 | labelled `4c34eb85`, see below |
| ladder (1 round, no fine-tune) | 16.9 | 14.0 | 0.831 | `4c34eb85` |
| ladder2 (2 rounds + 2 child `train.py`) | 79.9 | 75.0 | 0.939 | labelled `4c34eb85` |
| train_fast_perstep | 64.3 | 61.5 | 0.955 | `7fd4ddb1` |
| grpo (2 rounds) | 27.5 | 25.3 | 0.920 | `7fd4ddb1` |

The one job ≥ 3 min is within 5 % (1.1 %), as pre-registered. Short jobs miss by a fixed 2.4–4.9 s. That is n = 1 job
for the pre-registered criterion, and it ran the code *before* the process-age fix.

**Provenance finding.** Every part-2 row (train_fast_short, ladder2, expect2) carries `git_sha 4c34eb85`, but part 2
existed to test the process-age clock (`_proc_age`, added in `9f970a9f`, absent from `4c34eb85`). The rows cannot
be from `4c34eb85` alone: part 1's `expect` job wrote benchmark rows (train_steps 200, train_tokens 12,496,799,
`phase=bench`, `device=cpu`, arm/seed None), part 2's identical `expect2` wrote none, and ladder's process block grew
from 0.91 s to 3.66 s. So the pod's `.git_sha` file was stale after the code re-sync (podsync excludes `.git`). Part-2
rows' code version is mislabelled, and cannot be determined from the rows.

**Spurious rows in the published registry.** Part 1's `expect` benchmark wrote the rows above into
`artifacts/compute-record/registry/`. They are in the bucket, and any `registry_merge --compute --q run_id=compute-record`
table shows a row (arm None, seed None) of 200 steps / 12.5 M training tokens that is not work.

### Overhead

- Per-step counter (`train.py`, bs 500, `train_retain`): **103 µs/step** on the VPS CPU (`bench.py`). The pod's legacy
  steps take ≈ 202 ms (121 s / 600), so ≈ 0.05 % — under 1 %, as pre-registered.
- Legacy A/B on one host, alternated, n = 2 each: walls 128.10, 128.05 (off) vs 129.28, 129.15 (on) → **+1.14 s per
  process (0.89 % of a 2-min job)**. Step time printed as 121 s in all four. 600 × 103 µs = 0.06 s, so the +1.1 s is
  a fixed per-process cost, not the counter. The likely source is the process block's own extra `sync()` at exit (a
  second bucket upload); I did not verify this. It is ≈ 1 s a process, so it matters only for many short child processes.
- `fast_train` per-step counting: no on/off A/B. The only comparison is train_fast_short (count at end, host
  `2f2c9a71bc21`) against train_fast_perstep (per step, host `c03af612d063`). Excluding the first step: 33.3 s vs
  33.4 s; useful tok/s 777,640 vs 756,343 (−2.7 %). These ran on different pods, so the overhead is not measured.
  The counter reads a CPU tensor (`tot`), so no extra CUDA sync is expected.

### Behaviour under failure (`term.py`, CPU)

| how the process ends | rows written |
|---|---|
| normal exit | all |
| uncaught exception | all; the phase blocks say `status: ok` (only the process block says `exit`, never `error`) |
| SIGINT | all |
| **SIGTERM** (`kill`, `timeout`, a pod deleted by the budget watch) | only blocks already closed (earlier rounds). The open round's phase block and the process block are lost; a single-process `train.py` loses everything |

REGISTRY.md does say "A process killed by a signal (no `atexit`) writes nothing". The rows survive for SIGINT, and
for closed rounds under SIGTERM, so the sentence is partly too pessimistic. It is also a real gap: the restartable pod
runners stop jobs with a plain `kill`, which sends SIGTERM.

### Code audit (instrumentation coverage and definitions)

- `train_tokens` in `train.py` / `state_train.py` = `len(p) + len(q)` per record. `shift_abs` / `shift_pair` keep the
  length, so this equals the non-pad tokens of `x`. The GRPO count matches `seq_logprobs`' sequences (prompt +
  completion through the first `<eos>`, rows with a non-zero advantage).
- `gen_tokens` = `declen`, which is set once per row (`fin = ~done & eos`). It is correct on base and fast, with and
  without compaction (CI above). Under `ND_SAMPLE_EARLY=exact|goal`, the 1 (exact) or 3 (goal: `exact n <eos>`) injected
  tokens are not counted, although the code comment says "decoded tokens up to and including `<eos>`". The count is
  defensible (the model did not decode them), but it is not what `raw` holds. The default is `eos`.
- `lean_checks`: `Gate` counts distinct keys sent to Lean per `generate()` call (plus shadow-mode texts);
  `check_sources` and `lean_check.check` count `len(sources)`. **Duplicates are counted in `lean_check.check`**, where
  REGISTRY.md says "distinct texts". Bisection re-runs after a Lean crash add `lean_s`, not `lean_checks`.
- Not instrumented: `run_vllm.py` (vLLM decodes outside `sample.py`, so no `gen_tokens` / `attempts`; with
  `--tp > 1`, `n_gpu` stays 1 unless `ND_N_GPU` is set; if the main process never initialises CUDA, it writes no row at
  all). Analysis scripts that sample without `save_config` (`peek_samples.py`, `lp_b.py`, `dsg_regress.py`) count nothing
  (`count()` is a no-op with no open block). Neither was in the pre-registered list.
- `gpu_seconds` is occupancy (wall-clock × GPUs while the process holds CUDA), including CPU-side Lean time. With
  ≈ 5 jobs per card (the usual CPU-bound pod layout), Σ `gpu_seconds` is ≈ 5× the billed GPU time. REGISTRY.md says so.
  A comparison of arms that shared cards differently needs billed GPU-hours as well.
- REGISTRY.md is stale in two places: "`fast_train.py` at the end" (it now counts per step), and "Python start-up and
  imports before `save_config` (≈ 2–5 s) not counted" (the process-age clock now counts them).
- Stage-1 `train.py` jobs have no `arm` unless one is given, so the default table merges `fast_s0` (6,000 steps) with
  the two legacy A/B jobs of the same seed into one row (arm None, seed 0: 7,200 steps).
- `registry_merge.compute_table` agrees with my own sums on every (arm, seed, round) group of the pod's rows
  (`table.py`: no difference).

### Tests

- `tests/test_registry.py` locally (VPS, no torch): ALL PASS, including the 4 new compute cases.
- GitHub Actions on `dan` at `3fc57e41` (= run HEAD, merged): success.
- My own CPU checks (Actions run 36654170471): results in the tables above.

## Compare (phase 2)

Read after committing phase 1 (`22025128`): `run_compute_record.md`, the compute-record sections of `numbers.md` and
`log.md`, `artifacts/compute-record/compute_table.tsv`.

| claim (executor) | my independent value | verdict |
|---|---|---|
| overhead < 1 % of step time: 0.025 % (49.7 µs per 201.7 ms legacy step) | 103 µs on the VPS CPU → 0.05 %; A/B walls +1.14 s a process (0.89 % of a 2-min job), a fixed cost, not per step | **reproduces** (< 1 %). The write-up reports the A/B only as "121 s / 121 s" and leaves out the +1.1 s fixed cost the same runs show |
| "fast path counts once per run" (run md); "`fast_train.py` counts once at the end (no per-step cost)" (numbers.md) | code at HEAD counts per step (`fast_train.py:460`); numbers.md's own part-3 row says per step | **must be reworded** — stale since the review fix. The per-step fast-path overhead was never A/B'd (the only comparison is across two pods, −2.7 % tok/s) |
| counters = independent counts: 20 / 20 equal | every derivable counter reproduces exactly: train tokens of 7 train jobs (incl. the two ladder2 child fine-tunes, which the executor checked only by step count), steps, attempts, GRPO update steps, `lean_checks` vs gate logs (189; 4,766 + 4,871 = 9,637); my CPU `gen_tokens` test is exact on base, fast and fast-without-compaction, including cut-off rows | **reproduces**. Not derivable from files: pod `gen_tokens` (raw ids not stored; the executor's `sample_check` is its own count), GRPO `train_tokens` and `lean_checks`. Two definition edges outside the checks: `ND_SAMPLE_EARLY=exact/goal` rows (the counter excludes injected tokens: 3,881 vs 3,898 in `raw`), and duplicates counted by `lean_check.check` although REGISTRY.md says "distinct" |
| `gpu_seconds` within 5 % for jobs ≥ ~3 min: 0.989 (6 min), 0.975 (2 min) | same values | **reproduces**, but the pre-registered criterion rests on **one** job ≥ 3 min, run with the superseded clock (from `save_config`). The final clock (from exec) can only raise the ratio, but it was never run on a ≥ 3-min job |
| shorter jobs miss by a fixed ~1.5–2 s a process, "the row upload at exit" | gaps 2.3 s (1 proc), 2.9 s (1), 2.2 s (1), 4.9 s (3 procs) | sizes **reproduce**; the cause is asserted, not measured |
| CI green, compute checks included | Actions on `dan` at `3fc57e41`: success; `tests/test_registry.py` passes locally | **reproduces** |
| "A process killed by a signal writes no rows" | SIGINT: all rows; SIGTERM: blocks already closed (earlier rounds) survive, the open round's and the process block are lost | **reword**: too pessimistic for SIGINT and closed rounds. It understates the practical gap: `kill` (SIGTERM) is how the pod runners stop jobs, and a killed single-process `train.py` loses everything |
| log.md: "rows say `git_sha` 34693ad2 while the code was 4c34eb85 (part 1) and 9f970a9f (part 2)" | all 97 part-1/2 rows (and both ladder `args.json`) say `4c34eb85`; part 3's 36 say `7fd4ddb1` | **differs**. Part 1 is labelled correctly. Part 2 is mislabelled `4c34eb85` (not 34693ad2) while running 9f970a9f code. My phase-1 evidence agrees: `expect2` wrote no bench rows; the process block grew |
| bench row "is in the registry; it is not work" (log.md) | the row is also in the published `compute_table.tsv` (arm None, seed None, `bench`, 200 steps, 12,496,799 tokens), which numbers.md cites without the caveat | **disclosed in log only**; flag it next to the table or drop it from the table |
| model label on every number | numbers.md and run md name `ckpts/cr/fast_s0.pt`, 3.2 M, `lean_seq`, from scratch, training set, seed; GPU A40 at $0.49/h billed | **stands** |
| budget: $0.21 of $2; pre-registration before the pod | pre-registration `34693ad2` 00:10:29Z; `pods.log`: cr1 00:19:26Z, cr2 00:54:25Z | **stands** (job 16 min vs ≤ 15 min, disclosed) |
| per-arm compute table (policy) | `compute_table.tsv` = my sums (`table.py`: no difference vs `registry_merge.compute_table`) | **stands**; the default grouping merges the 6,000-step `fast_s0` job and the two legacy A/B jobs into one row (arm None, seed 0, 7,200 steps) because `train.py` jobs carry no arm |

Wording against n: there are no comparative claims between arms. The overhead A/B is n = 2 per side, and the write-up
does not call it more than that.

## Verdict

**Stands.** The instrumentation is correct where it can be checked from files or by rerunning the code. Every counter
I could re-derive matches exactly: tokens trained on (seven jobs, including the child fine-tunes), steps, attempts,
Lean checks against the gate logs, and decoded tokens on all three decode paths. Time is exclusive: the per-job sums
never exceed the wall-clock, and `registry_merge --compute` equals my own sums. The per-step cost is ≈ 0.05 %. Hard
constraints are clean.

**Reword:**
1. "fast path counts once per run" / "`fast_train.py` counts once at the end": it counts per step since part 3, and
   that overhead was not measured on one host. REGISTRY.md has the same stale sentence, plus "start-up before
   `save_config` not counted", which the process-age clock made false.
2. The gpu_seconds criterion: "met on the one job ≥ 3 min (6 min, 0.989), run before the clock change".
3. The signal limit: SIGTERM loses the open blocks (all of a single-process job); SIGINT and exceptions keep them.
   Exceptions leave phase rows with `status: ok`.
4. log.md's `git_sha` sentence: part-2 rows say `4c34eb85`, not 34693ad2, and part 1 is correct.
5. Flag the `bench` row in `compute_table.tsv` / numbers.md.
6. REGISTRY.md: `lean_check.check` counts duplicates; under `ND_SAMPLE_EARLY=exact|goal`, `gen_tokens` excludes the
   injected tokens.

**Not supported / not measured:** the overhead of per-step counting on the fast (CUDA-graph) path; the cause of the
fixed ~2 s a process; pod `gen_tokens`, GRPO `train_tokens` and GRPO `lean_checks` from stored files.

**Before later runs rely on it:** a SIGTERM handler in `job_compute` (e.g. turn SIGTERM into `SystemExit` so `atexit`
runs), since budget-watch deletions and runner kills would otherwise drop the current round's compute. Also note that
`run_vllm.py` records no `gen_tokens` / `attempts`, and records `n_gpu = 1` under tensor parallelism.

**Next measurement** (one pod, ~15 min): (a) fast_train 600 steps with `ND_COMPUTE=0` vs on, alternated on one host
(fast-path overhead); (b) one ≥ 3-min job on the final code (clock from exec); (c) `kill -TERM` of a `ladder_ei.py`
mid-round, before and after a SIGTERM handler, counting rows; (d) GRPO with its completions stored, to recount
`train_tokens` and `lean_checks`.
