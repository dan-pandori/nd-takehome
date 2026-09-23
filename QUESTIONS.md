# Questions for Dan (round 2). Each has the default I follow if unanswered.

- **2026-09-17 20:30 UTC (run 2)** — The generator cannot produce three of the six proposed patterns at all (box depth ≥ 4: `Gen(max_depth=3)`; IMPE chain ≥ 4: 0 in 9.4M tries even with 6 premises; nested ORE: 0). Default: depth-4 targets come from the unchanged generator with its depth cap raised to 5 (target pools only, pretraining sets untouched); IMPE-chain and nested-ORE targets are schema instances with random sub-formulas (`chain_pool.py`, `ore_pool.py`), oracle-labelled. Both disclosed in run2.md. Alternative if you prefer generator-only targets: drop those three patterns and report the other three.
- **2026-09-17 20:30 UTC (run 2)** — Nested ORE's shortest instances are 11–12 lines, beyond every written length these models have reached; the arm is pre-registered as length-limited (expected ≈ 0). Default: run it anyway (one pod-hour) so the negative is measured rather than assumed. Say if you would rather spend that hour on a third seed for depth-4 / IMPE-chain.
- **2026-09-17 20:30 UTC (run 5)** — Only 3 of the 4 planned reductio f = 0 draws exist as checkpoints (seed 7 from the ignition study was never pulled). Default: s0, s1, s2; no retrain (a fresh seed 7 would be a different draw).
- **2026-09-17 23:25 UTC (account)** — `runpodctl pod list` shows seven pods I did not create and do not touch: `r4-1`…`r4-6` (RTX 3090, $0.50/h each) and `r1-a100` (A100, $1.59/h), all RUNNING since ≈ 23:00 UTC (≈ $4.6/h together). They look like another agent working on runs 4 and 1 of this brief. Two consequences you should know: (a) the shared balance is the hard cap for everyone ($113 at 23:24); (b) `~/bin/killswitch` (cron 2026-09-19 00:00 UTC) deletes **every** pod on the account, not only mine — I left it unchanged because it is your safety net; say if you want it restricted to pods registered by this VPS. Default: unchanged; my own pods are deleted per run as before.
- **2026-09-17 23:25 UTC (token)** — a `podbg` quoting error echoed the remote command line, which `podrun` builds with `export HF_TOKEN=…`, into my session output (not into any file or commit). If the agent transcript is stored anywhere shared, rotate the HF token. Default: I continue; nothing was written to disk or git.
- **2026-09-18 01:45 UTC (run 4)** — The proposal's 85M / relative-unary-codec GRPO arm was not run (no access to the sprint's code). My `grpo.py` on the 3.3M models finds the opposite of the sprint's "saw nothing": faster and higher depth-3 acquisition than EI on all six draws, with in-distribution collapse. If the sprint's `nd_grpo.py` can be dropped into this repo (same target files, same verifier), one arm per group size on set a1 would settle whether the difference is the model / codec or the algorithm. Default: not run.
- **2026-09-18 01:45 UTC (run 4)** — `grpo_g8_a1_s0`'s round-8 files were lost when p5 was deleted (its round-7 numbers and round-8 checkpoint are in the bucket). Re-running that arm costs ≈ $0.40 and 40 min; say if you want the table completed at round 8. Default: reported at round-equivalent 7, marked.

# Questions for Dan (lean-format, proposal 8). Each has the default I follow if unanswered.

- **2026-09-21 04:40 UTC (lean-format, checker of record)** — `nd2lean.py` renders BOTE as `na.elim`. Lean resolves `.elim` by the head type of `na`, so on a negation it is `Not.elim`, and Lean then accepts e.g. `have n : ¬Q := n6.elim` with `n6 : ¬Q` — not a BOTE step; `nd_verify` rejects the denoted proof. Sampled Lean-format proofs hit this (49 of 2.39 M distinct checked samples so far; another 107 are the known `¬A ≡ A → False` definitional-unfolding kind; all 156 are "Lean accepts, `nd_verify` rejects", none the other way). The 181k / 181k agreement and the 4,000 mutated negatives never exercised it because they start from ND proofs. Default: I do **not** modify `nd2lean.py` (it is the checker of record); in this run a proof counts only if Lean **and** `nd_verify` accept, so no count depends on it. Proposed one-line fix for whoever owns the translator: render BOTE as `False.elim na` (and, if the `¬A`/`A → False` looseness matters, state `R`/`ORI`/`ANDI` results with `show`-free exact types — it cannot be closed in Lean, only by keeping `nd_verify` in the loop).
- **2026-09-21 04:40 UTC (lean-format, scope of the verdict)** — the proposal did not fix how hypotheses are named; `nd2lean`'s `n<i>` are line indices. I pre-registered two schemes (`lean_rand` random labels, primary; `lean_seq` first-appearance order + random offset). Interim: `lean_seq` passes the in-distribution band, `lean_rand` does not (held-out greedy 0.79–0.88 vs token 0.883; wrong-name citations), both beat the token format on the depth-3 dial. Default: the write-up gives the verdict per scheme and recommends `lean_seq` if the ladder confirms; the decision stays yours.

# Questions for Dan (lean-only, proposal 9). Each has the default I follow if unanswered.

- **2026-09-22 06:05 UTC (lean-only, gate 0 / pod naming)** — My pods are `lo-*`; the sibling run's `ls2-*` pods (05:46, 05:47 UTC) precede my pre-registration commit in the host-wide `~/pods.log`. Phase 1 needs a pod (the VPS takes 14 s and 1.5 GB per `import Lean`), so I committed the full pre-registration — phase-1 expectations and phase-2 predictions — *before* the phase-1 pod; any phase-2 number that phase 1 changes is appended as a dated addendum before the first phase-2 pod. Default: proceed on that reading of "before the first phase-2 pod".
- **2026-09-22 06:05 UTC (lean-only, the "181,464 pool proofs")** — The number in the proposal is round-2 run-1's summary figure; the pulled `artifacts/r1/lean_*.jsonl` files hold 253,397 distinct `nd_verify`-accepted (prompt, proof) pairs. Default: I validate `lean_check` on all 253,397 (a superset) and say so.

## 2026-09-23 — run `efficiency`: the brief's `<eos>` premise does not reproduce on the from-scratch model

`BRIEF_EFFICIENCY.md` is built on a `ds-composition` measurement: "97 % of base-model samples on 7–12-line Lean
targets never emit `<eos>`", a coverage pass at ≈ 21 s per target at k = 2,000, and a 16–23 GB KV cache. On the
checkpoint the brief names (`stage1_full_seq_s0.pt`, the `lean_seq` Stage-1 model of run `lean-only`), on 200
ladder-transfer targets of `L_true` 7–12 at k = 256, T 0.8, `max_new` 512, batch 512, I measure the opposite:
**99.988 % of rows emit `<eos>`** (6 of 51,200 do not), mean 143 decoded tokens, peak 2.1 GB, 1.7 ms per sample
(≈ 6× faster per sample than the brief's arithmetic implies). Source: `artifacts/ef/base_orig.json`.

The arithmetic suggests `ds-composition`'s figure came from a much larger model (≈ 6× the per-sample cost), i.e.
a **pretrained** model sampled in the Lean surface form, not this 3.2 M-parameter from-scratch one. If so, the
`<eos>` problem is real but belongs to the pretrained-model path, and the from-scratch sampler's waste is a
different thing entirely (it is: the decode batch runs to its *longest* row, and each step is kernel-launch-bound,
so the batch size — not the terminator — is the lever).

**Question:** is the 97 % figure from a pretrained model (Qwen-family) rather than the `lean_seq` Stage-1 model?
If it is, would you rather I spend the remaining budget (a) finishing the from-scratch sampler work, which every
`lean_seq` run inherits, or (b) reproducing and fixing the `<eos>` failure on the pretrained path?

**Default I am following:** (a). I am completing the from-scratch measurement and fixes, reporting the falsified
premise plainly, and keeping the terminator fixes in the patched `sample.py` behind flags so that whoever hits the
pretrained-path problem inherits them. I will not start a pretrained-model run under this brief's budget.

