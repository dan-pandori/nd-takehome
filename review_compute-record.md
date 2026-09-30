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
