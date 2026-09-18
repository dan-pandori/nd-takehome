# Run brief: run1-lean — cast natural deduction into Lean; measure novelty by model scale

Run id `run1-lean`. Repository `~/work/run1-lean` (branch `dan_run1_lean`, a worktree of the fork).
`AGENT_POLICY.md` governs; this is proposal 1 of
`~/nd-rl/docs/proposals/2026-09-17-proposals-round-2.md` (read it). Budget $50 of pods; hard stop
in 30 h. This run is one of two parallel executors on this host; the other (`run4-grpo`) has its
own worktree, pods named `r1-*` are yours, `r4-*` are not.

**Before the first pod**: `preregistration/run1-lean.md` with question, design, numeric
expectations (the Lean − token accuracy delta you expect, by proof length; how you expect
scale-of-first-success to relate to the base log-probabilities), budget, stop rule; commit and
push. Gate 0 checks its commit time against `~/pods.log`.

1. `nd2lean.py`: deterministic translation of spec.md proofs into Lean 4 terms (atoms as `Prop`
   variables, premises as hypotheses; `ANDI`→`And.intro`, `IMPE`→application, `IMPI`→`fun h => …`,
   `ORE`→`Or.elim`, `NEGE`→application to `False`, `NEGI`→`fun h => …` at `¬`, `BOTE`→`False.elim`,
   `DN`→`Classical.byContradiction` / `not_not`). Lean via `elan` on this VPS, core only, no Mathlib.
   Check every proof in `data/train.jsonl.gz`, `data/heldout.jsonl`, and the found-proof files:
   `nd_verify` accepts ⇔ Lean accepts; report every disagreement with an example. Commit the
   translator and the agreement table before step 2.
2. In-context v0 with **Qwen3-Coder-30B-A3B-Instruct served by vLLM on one A100 pod** (no hosted
   API; `pip install vllm` on the pod; HF_TOKEN is passed by `podrun`): 20 worked examples in
   context, one fresh theorem, greedy + 8 samples at T = 0.7; three surface forms — Lean 4, the
   take-home token format, plain-English rule names (control); validation-36 + 200 transfer
   theorems stratified by generating length; 5 example-set draws. Verify Lean output with Lean,
   token output with `nd_verify`; same theorems and same (translated) examples across forms.
   Report accuracy by form and length, the paired Lean − tokens delta with an interval.
3. Novelty by scale: for the campaign's RL-found proof classes (depth-3 from f = 0, reductio from
   f = 0, 9-line transfer proofs; ≥ 30 theorems each, from `artifacts/`), the smallest Qwen3
   instruct model (0.6B, 1.7B, 4B, 8B, 14B, 32B; same prompt, k = 16) that proves the theorem in
   Lean; compare the ordering with the Phase-1 base log-probabilities (`artifacts/novelty_phase1_*`).

Deliverables: `run1.md` (≤ 400 words + figures), `numbers.md` and `log.md` sections, bucket upload
to `hf://buckets/dan-pandori/nd-rl/run1-lean/`, `STATUS.md` ending `RUN1 DONE <UTC>`, then
`touch ~/runs/run1-lean/executor.done`. Pods deleted first.


## Note 2026-09-18 02:20 UTC (from Dan, relayed)

The round-2 executor on the other host completed its own version of this run before it saw the instruction to stop (results on branch dan_novelty: run1.md, numbers.md, review_round2-run1.md). Your run therefore serves as an **independent replication** by a different executor with different code. Finish it as planned; in your write-up add a short section comparing your numbers with theirs, claim by claim, and say where they agree and disagree. Do not copy their code or numbers into yours.
