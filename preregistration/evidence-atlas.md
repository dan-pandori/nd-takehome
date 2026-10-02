---
written_on: 2026-10-02
written_by: agent:claude (executor, run evidence-atlas)
---

# Pre-registration: evidence-atlas — one harmonized map of what the project has measured

Brief: run brief `evidence-atlas` (Dan, 2026-10-02, proposal 21). Policy: `AGENT_POLICY.md`. Written before any pod
of this run (none is planned).

## Question

What has the project measured, under which protocol, and which cross-experiment comparisons are apples to apples?
Specifically: (a) one row per experiment by question; (b) textbook72 pass@k, Robbie's dev metric / holdout250, and the
length frontier across every model family that was scored; (c) the create-vs-elicit evidence with a strength rating.

## Design

CPU only, read-only sources: nd-rl `dan` (`experiment-summaries/`, `docs/`), the fork's run branches and the public
bucket (per-theorem files), and other members' nd-rl branches (read, never pushed to or commented on). Numbers are
recomputed from per-run / per-theorem files where they exist; otherwise copied from the summary with its source path and
marked `copied`. Every row carries model label (checkpoint, params, format, from scratch / pretrained, training set),
checker (Lean alone vs Lean ∧ `nd_verify`), k, temperature, pool, seeds and review status.

Optional re-score (≤ $5, `podbudget evidence-atlas --set 10 5` before any pod): only if one read-out makes a key
cross-family comparison apples to apples. Default: no pods.

## Expected results (falsifiable)

1. The experiment map has **≥ 55 rows** (≈ 60 summaries on nd-rl `dan` plus other members' work).
2. **textbook72:** the highest pass@k on file is best-cap12 T1 (≈ 52 / 72, Lean alone); no family in
   `robbie-experiments` exceeds it at the same k. Fewer than half of the families were scored at the same k and
   checker, so the one-axis figure needs a protocol marker on most points.
3. **Protocol table:** at least one headline comparison in `docs/STATE.md` or the digests mixes checkers
   (pre- vs post-2026-09-27) or k without saying so. Expected count 1–5.
4. **Create vs elicit:** no line of evidence is rated "strong for creation"; the strongest is support expansion
   (support-curves / followups) rated "moderate"; trajectory and rl-from-ckpt evidence rated "moderate for elicitation /
   amplification of pretraining-reachable behaviour".
5. **Pods:** 0 (probability ≈ 0.7). If a re-score is run, cost ≤ $2.

## Stop rule

Done when `atlas/ATLAS.md`, figures and CSVs are written and every figure point traces to a file; or at
2026-10-03 16:00 UTC, whichever is first, writing up what exists.
