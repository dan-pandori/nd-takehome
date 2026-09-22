# Run brief: lean-only — proposal 9, phases 1 and 2

Run id `lean-only`. Repository `~/work/lean-only` (branch `dan_lean_only`, worktree from
`origin/dan_lean_format`). `AGENT_POLICY.md` governs. The proposal is the design:
`~/nd-rl/docs/proposals/2026-09-22-lean-only-checking-and-term-size.md` (branch `dan`; read it
and the decision note it references). Budget $35 total ($5 phase 1, $30 phase 2); hard stop 36 h.
Dan authorised this run; everything not listed in `~/QUEUE.md` stays paused. A sibling run
`lean-seed2` on this host is fixing `nd2lean.py`'s `BOTE` rendering on branch `dan_lean_seed2` —
pull its fix when it lands (check that branch) rather than fixing it twice; if it has not landed
when you need it, apply the same fix and say so.

Phase 1 first, committed and pushed before any phase-2 pod: `lean_check` (term-allowlist +
axiom check on the elaborated term), `term_size`, tests against hand-written cases (an `em`
lemma use must be rejected; a `simp` proof rejected; a `sorry` rejected; a plain `And.intro`
term accepted), the 181k-proof agreement table, the 460-text disagreement table, throughput,
and the pools relabelled in both units. Then `preregistration/lean-only.md` with the
proposal's predictions as numbers, committed before the first phase-2 pod (gate 0). **Report
every length in lines and in term size**, lines first.

Deliverables: `run_lean_only.md` (≤ 400 words + figures), `numbers.md`/`log.md` sections, bucket
upload to `hf://buckets/dan-pandori/nd-rl/lean-only/`, `STATUS.md` ending `LEAN-ONLY DONE <UTC>`,
`touch ~/runs/lean-only/executor.done`. Pods deleted first.
