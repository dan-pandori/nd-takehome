# Pre-registration — run `efficiency`

Written 2026-09-23, before any pod of this run. Brief: `BRIEF_EFFICIENCY.md`. Policy: `AGENT_POLICY.md`.
Budget: pod-hour ceiling 10 h, $15 (`podbudget efficiency`). Repository `~/work/efficiency`, branch `dan_efficiency`.

## Question

Sampling is the dominant cost of every run in this project, and `ds-composition` measured that ~97 % of
base-model samples on 7–12-line Lean targets never emit `<eos>`, so a decode batch runs its full budget for
almost every row. **Why does the terminator not fire, and how much sampler and checker time can be recovered
without changing which proofs are accepted?** Lean remains the checker of record: every counted proof is
checked by `lean_check`, and `nd_verify` runs beside it for the agreement table.

## Fixed setup (identical before and after)

- Checkpoint: `stage1_full_seq_s0.pt` — the `lean_seq` Stage-1 model of run `lean-only`
  (`hf://buckets/dan-pandori/nd-rl/lean-only/ckpts/lo/stage1_full_seq_s0.pt`). Never retrained in this run.
- Targets: **200** records drawn from `data/ladder/transfer.jsonl` restricted to `L_true` 7–12 (2,262 of 2,285),
  stratified by `L_true` in pool proportion, `random.Random(0).sample` within each bin; written once to
  `artifacts/ef/targets200.jsonl` and reused verbatim by every measurement.
- Sampling: `k = 256` per target (**51,200 samples**, which is also the ≥ 50,000-sample correctness gate),
  temperature 0.8, `max_new = 512`, `batch = 512` (the ladder-EI settings, brief's batch).
- One RTX 3090 pod, nothing else on the GPU except where co-tenancy is the thing being measured.

## Measured, before and after (step 1 / step 4 of the brief)

samples per second; mean and p95 decoded tokens per sample; fraction of rows that ever emit `<eos>`; peak GPU
memory (`torch.cuda.max_memory_allocated` and `nvidia-smi`); wall clock; and for the Lean gate, accepted proofs
per process-second and per wall-second. Every number lands in a json file under `artifacts/ef/` and is named in
`numbers.md`.

## Expected results (numeric; each falsifiable)

- **E1** Baseline `<eos>` fraction on these 200 targets: **< 15 %** (I predict 2–10 %).
- **E2** Same checkpoint on in-distribution held-out prompts (`data/heldout.jsonl`, ≤ 6-line proofs):
  `<eos>` fraction **> 70 %**. This separates "the model never learned a terminator" (cause a) from
  "the terminator is out of reach on these prompts" (cause a'). Falsified if < 70 %.
- **E3** Baseline mean decoded tokens per sample **> 450** of 512; p95 **= 512**.
- **E4** Of the rows that never emit `<eos>`, **> 80 %** are at paren depth 0 in an unfinished `have` chain and
  have never emitted a top-level `exact`. Predicted cause: the model did learn `<eos>`, but in this grammar
  `<eos>` is only reachable after a top-level `have` states the goal, and on 7–12-line targets it rarely gets
  there. So the terminator is a *coverage* failure, not a tokenisation or sampler bug. Falsified if ≤ 80 %.
- **E5** No baseline-accepted sample uses more than **400** decoded tokens, so a `max_new` cap at the observed
  maximum plus margin costs nothing.
- **E6** Batch compaction *alone* buys **< 1.2 ×** at baseline, because almost no row finishes early. Written
  down in advance so that a small number is not read as a failure of the measurement.
- **E7** Forced-terminator early stop (a row stops as soon as a depth-0 `have` introduces the goal formula; the
  sampler appends `exact n<k>` and Lean checks the result, so a wrong guess costs a rejected sample, never a
  wrong accept) plus compaction: mean decoded tokens per sample falls **≥ 2 ×**, samples/s rises **≥ 2 ×**, peak
  GPU memory falls **≥ 1.5 ×**.
- **E8** Accepted proofs after the terminator fix: **0** targets solved at baseline are lost, and **≥ 1.5 ×** as
  many samples are accepted by Lean (the fix recovers rows that are currently discarded as `no-eos`).
- **E9** Correctness gate, ≥ 50,000 samples: for the **pure-speed** path (compaction + `max_new` cap + Lean
  batching changes, same token streams) the accepted set is **identical** — same texts, same counts, same
  targets. Any difference is a bug and is reported as one.
- **E10** Persistent Lean process/server: the fixed per-process cost is **< 10 %** of gate process-time at the
  current chunk size of 300, so the fix is **dropped** with that number stated. Falsified if ≥ 10 %.
- **E11** Co-tenancy: per-job throughput stops improving at **2** concurrent jobs per GPU.

## Deviation from the brief, stated up front

The brief asks (step 3) for a per-sequence early stop *and* (step 5) an identical accepted set. Under E4 these
cannot both hold: the early stop is what recovers the 97 % of rows that currently produce nothing, so it
*adds* accepted proofs by construction. I will therefore report two gates: the **identical-set** gate for the
pure-speed fixes, and an explicit **superset** comparison for the terminator fix (baseline-accepted targets
retained, newly accepted samples counted, every accept checked by Lean). Both on the same 51,200 samples.
To make the identical-set gate exact rather than statistical, sampling is made **per-row deterministic**
(counter-based Gumbel noise keyed by (row seed, step)), so that a row's token stream does not depend on how
the batch is packed; the old batch-wide `torch.multinomial` path stays available behind a flag.

## Stop rule

- Stop and report "not worth it" if, after the diagnosis and the first two fixes, the measured end-to-end
  (sample + gate) speed-up on this fixed workload is **< 1.3 ×**.
- Stop at **8 pod-hours** used (of the 10 h ceiling) regardless of stage, write up what is measured.
- Retraining a Stage-1 model with a different terminator is in scope only if it fits in the remaining budget
  after the above; otherwise it is written down as not done, with the estimate.
