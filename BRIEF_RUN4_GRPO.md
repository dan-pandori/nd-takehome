# Run brief: run4-grpo — does GRPO ignite from zero coverage?

Run id `run4-grpo`. Repository `~/work/run4-grpo` (branch `dan_run4_grpo`, a worktree of the fork).
`AGENT_POLICY.md` governs; this is proposal 4 of
`~/nd-rl/docs/proposals/2026-09-17-proposals-round-2.md` (read it), minus the 85M / relative-codec
arm (no access to that code — say so). Budget $50 of pods; hard stop in 30 h. Parallel executor
`run1-lean` shares this host; name your pods `r4-*`.

**Before the first pod**: `preregistration/run4-grpo.md` — question, design, numeric expectations
(does GRPO with groups of 8 ignite from a zero base rate? with groups of 32? at what fraction of
groups with reward variance?), budget, stop rule; commit and push.

Implement a minimal `grpo.py` on the existing model/sampler: on-policy, groups of G samples per
prompt (G = 8 and G = 32), binary verifier reward, group-mean baseline, fixed loss divisor, no
KL, one optimizer step per batch, same total sample budget as expert iteration's 8 rounds × 32.
Run it on the depth-3 f = 0 Stage-1 models that exist (`ckpts/p2/`, sets a1–a3; two seeds each
if budget allows) against `data/p2/targets_depth3.jsonl`, next to the matching expert-iteration
arms from the earlier runs (do not rerun them; cite their files). Record per update: the fraction
of groups with reward variance, pattern acquisition (normalised, model's proof classified), plain
solve rate, held-out greedy; base reachability of any depth-3 proofs GRPO finds, with the
Phase-1 method.

Deliverables: `run4.md` (≤ 400 words + figures), `numbers.md` and `log.md` sections, bucket
upload to `hf://buckets/dan-pandori/nd-rl/run4-grpo/`, `STATUS.md` ending `RUN4 DONE <UTC>`, then
`touch ~/runs/run4-grpo/executor.done`. Pods deleted first.


## Note 2026-09-18 02:20 UTC (from Dan, relayed)

The round-2 executor on the other host completed its own version of this run before it saw the instruction to stop (results on branch dan_novelty: run4.md, numbers.md, review_round2-run4.md). Your run therefore serves as an **independent replication** by a different executor with different code. Finish it as planned; in your write-up add a short section comparing your numbers with theirs, claim by claim, and say where they agree and disagree. Do not copy their code or numbers into yours.
