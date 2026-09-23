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
