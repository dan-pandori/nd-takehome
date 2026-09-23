# Run brief: efficiency — make sampling and checking cheap, measured before and after

Run id `efficiency`. Repository `~/work/efficiency` (branch `dan_efficiency`, worktree from
`origin/dan_lean_only` if it exists, else `origin/dan_lean_format`). `AGENT_POLICY.md` governs.
**Pod-hour ceiling 10 h, budget $15** — already set (`podbudget efficiency`); you may extend it
yourself within the budget: `podbudget efficiency --extend <hours> "reason"`. A warning file
`~/runs/efficiency/BUDGET_WARNING` appears at 80 %; check for it between stages.

## Why this run exists

A third of all pod spend so far was idle pods (now fixed by a watchdog), and inside runs the
sampler is the dominant cost. Measured by `ds-composition`: **97 % of base-model samples on
7–12-line Lean targets never emit `<eos>`**, so with batch 512 a single unterminated row makes
the whole batch decode its full 400–512 steps; a coverage pass costs ≈ 21 s per target at
k = 2,000, about **3× the brief's arithmetic**; and unterminated rows grow the KV cache to
16–23 GB, which caused CUDA OOMs and forced jobs to run sequentially. Every future run pays
this. The goal is a measured speed-up that every later run inherits, not a new result.

## Method — measure, fix, measure again

1. **Baseline, committed first.** On one pod, with a fixed checkpoint (a `lean_seq` Stage-1
   model) and a fixed set of 200 targets from the ladder transfer pool at k = 256: samples per
   second, mean and p95 decoded tokens per sample, fraction of rows that ever emit `<eos>`,
   peak GPU memory, wall-clock, and the same for the Lean gate (proofs per process-second).
   Commit the numbers and the script before changing anything.
2. **Diagnose the `<eos>` failure.** Is it (a) the model never learned a terminator, (b) the
   rendering does not end with one, (c) the prompt is longer than anything in training, or
   (d) the sampler ignores it? Decide from the data: the training set's last tokens, the
   model's probability of `<eos>` at the true end, and the distribution of what it emits
   instead. Report the cause before the fix.
3. **Fix, in this order, keeping each one separable and reversible:**
   - **per-sequence early stop**: end a row when its Lean term is syntactically complete
     (balanced delimiters and the proof's final step), not only on `<eos>`; a candidate stop
     must still be checked by Lean, so a wrong guess costs a rejected sample, never a wrong
     accept;
   - **batch compaction**: drop finished rows from the decode batch (or re-pack) so finished
     rows stop consuming compute and cache;
   - whatever step 2 indicates for the terminator itself (retraining a Stage-1 model with a
     reliable end token is in scope if it is cheap; say so if it is not);
   - a **persistent Lean process/server** for the gate if per-call startup is material.
4. **Re-measure exactly as in step 1**, same checkpoint, same targets, same k. Report the
   ratio per fix and cumulatively. A fix that does not pay for its complexity should be
   dropped and said to be dropped.
5. **Correctness gate:** on ≥ 50,000 samples, the set of accepted proofs must be identical
   before and after (same texts accepted, same counts); any difference is a bug, not a
   speed-up. State the comparison explicitly.
6. **Co-tenancy:** measure round time at 1, 2, 3 and 4 concurrent jobs per GPU and state the
   point where per-job throughput stops improving; put the recommendation in one line for the
   next brief.

## Deliverables

`run_efficiency.md` (≤ 400 words + one figure: tokens per sample and samples/s before and
after), the patched `sample.py` (and whatever else changed) with the old path available behind
a flag, `numbers.md` and `log.md` sections, bucket upload to
`hf://buckets/dan-pandori/nd-rl/efficiency/`, `STATUS.md` ending `EFFICIENCY DONE <UTC>`, then
`touch ~/runs/efficiency/executor.done`. Pods deleted first. A reviewer session will re-derive
the before/after numbers and the correctness gate.
