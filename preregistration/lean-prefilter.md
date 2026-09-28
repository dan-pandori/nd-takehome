# Pre-registration — lean-prefilter (proposal 15, items 3 and 4)

Written 2026-09-28 before any pod. Executor. Budget **$3, 6 pod-hours** (registered with `podbudget`).
Checker: Lean 4 core alone (policy 2026-09-27); `nd_verify` is not called anywhere in this run.

## Question

How much of the RL loop's Lean time can come off the critical path — by a sound, reject-only Python
pre-filter, by sizing the Lean worker pool to the machine, and by checking the previous decode chunk while
the GPU samples the next — without changing a single verdict?

## What is built (before the first pod; the prototype already exists)

1. `lean_prefilter.py`: `reject_reason(statement, text) -> None | reason`. A type checker for the strict
   `lean_seq` fragment, run only on texts `lean_tok.inverse` already parsed. In that fragment the only
   definitional unfolding is `¬A := A → False`, so defeq = syntactic equality after unfolding `¬`. It models
   what Lean accepts beyond ND (`¬A`/`A → False` interchangeable; `n.elim` by the *declared* head:
   `False.elim`, `Not.elim : A → c`, `And.elim`, `Or.elim`), rejects only on a certain error, and returns
   "pass" for anything unmodelled (a formula not in the fully parenthesised form, any grammar surprise).
2. `lean_gate.py`: `LEAN_PREFILTER=on|off|shadow` (default `on`). `shadow` runs the filter, sends every text
   to Lean anyway, and logs every filter-reject that Lean accepted (`*.filterbug.jsonl`). A `Gate` object
   accepts decode chunks as they finish (pipelining; `LEAN_GATE_PIPELINE=1` default) and the worker count
   defaults to the cgroup CPU quota (`cpu.max` ∩ affinity), not `cpu_count // 2` or the job scripts' 3.
3. Item 4: the loop scripts' `--batch` default raised to 4,096 (policy: largest that fits; `efficiency`
   measured ≈ 11 GB at `max_new` 288 on the 3.2 M `lean_seq` model); the gate log records the truncation
   rate (`no-eos` / samples) and warns above 0.1 %.

## Acceptance tests and expected results

**(a) Soundness — 0 false rejects.** Corpus, every text Lean-checked in this run (verdicts are
Lean 4.34.0 core via `lean_gate.check_sources`, the gate's own path):
- C1 model samples: shadow-mode sampling from 8 checkpoints (3.2 M-parameter from-scratch models, `lean_seq`
  and `lean_rand`; ds-composition a1/a3, ds-generator g2, lean-format a1_rand, full_seq and an EI round-8
  model, cap-horizon k14, noise-floor p2) on the ladder targets, transfer and held-out prompts at
  temperatures 0.8–1.2, until **≥ 1,000,000 distinct parsed (prompt, text)** pairs.
- C2 edge corpus: mutations of Lean-accepted texts built to hit the unfoldings Lean allows (`¬A` ↔
  `A → False` in declared types and binders, `.elim` on each head, reiterations through defeq types) and
  near misses (one name / projection / `Or.inl`↔`Or.inr` / atom swapped), ≥ 50,000 texts.
- C3 stored: every `*.disagree.jsonl` in the bucket (Lean-accepted texts `nd_verify` rejected: the
  skip-a-step class), `lean-judge`'s test-5 dump and the stored leanrej samples, re-checked in Lean.

Expected: **0** filter-rejects among Lean-accepted texts in all three. The filter passes a text Lean
rejects only for unmodelled forms; expected **filter share of Lean's reject load ≥ 95 %** on C1 (prototype:
100 % of 1,158 rejects in the test-5 dump). Any false reject is a bug: fixed, and the whole corpus re-run.

**(b) Identical accepted sets on a fixed stored sample.** The gate with `LEAN_PREFILTER=off` vs `on` over the
same C1 subset (≥ 100 k texts): expected identical accepted sets (a consequence of (a)).

**(c) One T1 ladder round, old path vs new.** Checkpoint `ckpts/dsc/stage1_a1_s1.pt` (3.2 M params,
`lean_seq`, from scratch, trained on `data/dsc/train_a1.jsonl`), `la_T1_dsc_a1_s1`'s arguments
(`noise-floor`: k 32, T 0.8, `max_new` 512, seed 1, uniform alloc), `--rounds 1`, one job alone on one pod:
- A (old): batch 512, `LEAN_GATE_WORKERS=3`, `LEAN_PREFILTER=off`, `LEAN_GATE_PIPELINE=0`.
- B (new, fixed batch): batch 512, filter on, pipelined, workers = quota. **Accepted set identical to A**
  (same sample stream at the same batch). If GPU nondeterminism changes the stream, the test is repeated on
  the texts both arms sampled, and that is reported.
- C (new, fast): batch 4,096, as B. Peak memory recorded.

Expected: gate share of the round from ≈ 30 % (A) to **≤ 5 %** (B, C). Round wall-clock C / A: the brief's
target is ≤ 1/3; **my prediction is 0.30–0.45**, i.e. the target may be missed, because sampling (≈ 60 % of
the old round) only gets ≈ 2.2× from the batch and fine-tuning (≈ 7 %) is untouched (sibling `fast-stage1`
owns `train.py`). Worker sizing: Lean throughput at quota workers ≥ 2× that at 3 workers on a ≈ 7.6-CPU pod.

Wall-clock numbers are single measurements (n = 1 per arm, the job alone on the pod); a difference under
10 % between two timings is not treated as a finding. The noise floor of `NOISE_FLOOR.md` concerns
solve-rate metrics and does not apply to verdict identity, which is deterministic.

## Stop rule

Stop when (a)–(c) are measured, or at $3 / 6 pod-hours. A false reject that cannot be fixed within the
budget means the filter ships `off` by default (shadow available) and the run reports it.
