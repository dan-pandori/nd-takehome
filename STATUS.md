# STATUS — efficiency

Brief: BRIEF_EFFICIENCY.md. Run id: efficiency. Pod-hour ceiling 10 h, budget $15 (podbudget efficiency).

## Run efficiency (executor)

- 2026-09-23 15:30 UTC  Pre-registration committed (`preregistration/efficiency.md`); gate 0 PASS. Pod `ef-1`
  (RTX 3090, $0.50/h) created 15:31 UTC.
- 2026-09-23 15:42 UTC  **Baseline measured, and the brief's premise does not reproduce on this checkpoint.**
  `stage1_full_seq_s0.pt` (`lean_seq` Stage-1), 200 ladder-transfer targets of `L_true` 7-12, k = 256
  (51,200 samples), T 0.8, `max_new` 512, batch 512: **99.99 % of rows emit `<eos>`** (6 of 51,200 do not),
  mean 143.4 decoded tokens, p95 236, peak 2.1 GB, 592 samples/s, sampler 86 s + Lean gate 19 s.
  The brief's "97 % of base-model samples never emit `<eos>` … 16-23 GB KV cache" (from `ds-composition`) is
  **not** what this Stage-1 model does; E1/E3/E4 of the pre-registration are falsified in the model's favour.
  The waste is elsewhere and is being measured: the decode batch runs to the *longest* row (~450 steps) while
  the mean row needs 143, and each step is kernel-launch-bound, so dropping finished rows buys nothing on its
  own (measured: 89.1 s vs 88.3 s).
- 2026-09-23 17:05 UTC  **EFFICIENCY DONE.** Sampler **2.35×** (592.5 → 1,394.8 samples/s), end to end **2.16×**
  (105.45 → 48.89 s) on the fixed 51,200-sample workload, with the accepted set **identical** before and after
  (2,022 samples / 56 distinct proofs / 31 targets, symmetric difference 0, `nd_verify` 56/56 with Lean) in three
  separate comparisons. What paid: batch 512 → 4,096 (2.13×), memoised RoPE (1.07×), `max_new` 512 → 288 (1.05×),
  and batch compaction — which buys 1.01× on its own but is what makes the large batch affordable (on the
  unchanged path batch 4,096 is *slower* than 512). Gate: canonicalise once per distinct text, 19.03 → 12.18 s.
  Dropped with numbers: both per-sequence early stops, worker-sized Lean chunks, a persistent Lean server,
  re-packing. Co-tenancy knee at **3** jobs per GPU; prefer one job at batch 4,096.
  The brief's `<eos>` premise does not hold for this checkpoint (99.988 % of rows terminate) — see `QUESTIONS.md`.
  `run_efficiency.md`, `numbers.md` §1–10, `log.md`, `figures/efficiency_before_after.png`. Pod deleted; 1.5314 h,
  $0.77. Bucket `hf://buckets/dan-pandori/nd-rl/efficiency/{artifacts,ckpts,data}`.

EFFICIENCY DONE 2026-09-23T17:05:00Z
