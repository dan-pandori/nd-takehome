# Pre-registration — compute-record (executor, 2026-09-30)

**Question.** Can the scripts record their own compute (AGENT_POLICY 2026-09-29: `gpu_seconds`, `gen_tokens`,
`train_steps`, `train_tokens`, `lean_checks`, labelled `arm`, `seed`, `labels.round`) as registry rows, exactly and
at negligible cost, so later runs need not derive compute from job logs?

**Design.**
1. `record.compute(arm=, seed=, round=, **labels)` context manager: wall-clock × GPUs in use → `gpu_seconds`
   (`labels.gpu` = device name, `labels.n_gpu`; `labels.device=cpu` and `cpu_seconds` on CPU); counters
   `gen_tokens`, `attempts`, `actions`, `train_steps`, `train_tokens`, `lean_checks` (+ `labels.lean_s`); one row per
   non-zero metric at exit through `record()` (obeys `ND_OFFLINE`, `ND_REGISTRY`, `ND_REGISTRY_DIR`). A process-wide
   "current" block so library code (sampler, Lean gate) adds to whatever block is open, without new arguments.
2. Counting only real work: non-pad tokens trained on; tokens actually decoded (up to and including EOS, never pad
   after EOS); texts actually sent to a Lean process (cache hits and parse rejects excluded).
3. Instrument train.py, fast_train.py, state_train.py, sample.py, state_sample.py, ladder_ei.py, state_ladder_ei.py,
   expert_iter.py, grpo.py (per round: sample / finetune / judge blocks), lean_gate.py / lean_judge.py.
4. `registry_merge.py --compute`: per-arm table summed by run, arm, seed, round.
5. CPU test in CI: tiny train + sample + judge writes the rows; counters equal independent counts.
6. One GPU check (smallest pod, ≤ 15 min): a short train + sample job.

**Expected results (falsifiable).**
- Overhead of the helper < 1 % of step time (measured on CPU per call, and on the GPU job as instrumented vs
  uninstrumented step time).
- Counters match independent counts **exactly**: train tokens = non-pad tokens of the batches; gen tokens = tokens
  in the decoded samples (re-tokenised / counted from `raw`); lean_checks = texts sent to Lean from the gate log.
- GPU job: `gpu_seconds` within 5 % of the job's own wall-clock (`date` before/after the Python process; I expect
  the gap to be start-up/import time, 2–10 s, so within 5 % only for a job ≥ ~3 min — the job is sized so).
- CI stays green (local `ci/run_ci.sh` and GitHub Actions on `dan`).

**Budget and stop rule.** $2, 4 pod-hours; one GPU pod (smallest available, e.g. RTX A4000/3090), deleted as soon
as the job's files are pulled. Stop and report if the pod is not up in 30 min or the balance would drop below $100.
