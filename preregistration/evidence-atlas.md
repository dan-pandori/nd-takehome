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

## Addendum 1 (2026-10-02, before any pod): the re-score

**Gap.** The fork's whole-proof `lean_seq` models were never scored on textbook72, dev1108 or holdout250 (part F of the
atlas). Every fork row on those pools is a proof-state model (`lean_staten`), and every Robbie factorial `lean` cell is
whole-proof `lean_seq`. So no fork-vs-Robbie row is matched on format, and the interface effect (whole proof vs state)
on these pools is unmeasured.

**Read-out.** Eight existing checkpoints, all 3.2M (4 × 256), `lean_seq`, from scratch, Lean alone:
C0 cap-6 (cap-6 control set, depth3 f0 a1, 155k) frozen `lean-format/ckpts/lf/stage1_a1_seq_s{0,1}.pt` and T1
`ds-generator/ckpts/ladder/la_T1_c0_s{0,1}_r8.pt`; K12 cap-12 (`data/kh/train_k12.jsonl`, 155k) frozen
`cap-horizon/ckpts/kh/stage1_k12_s{0,1}.pt` and T1 `state-cap12/ckpts/ladder/la_T1_K12_s{0,1}_r8.pt`. Each on textbook72
(k 256), dev1108 (k 64) and holdout250 (k 256), T 0.8, sample seed 0, batch 4,096, max_new 512, with the unchanged
`eval_set.py` (wrapper `atlas/scripts/rescore.py` only sets max_new and records stop counts). One RTX 3090 (or A40)
pod via `podjob`, two jobs packed. Budget registered: `podbudget evidence-atlas --set 10 5`.

**Expected (per seed, solved counts):**

| model | textbook72 /72 | holdout250 /250 | dev1108 /1108 |
|---|---|---|---|
| C0 frozen | 4–12 | 30–90 | 100–400 |
| C0 T1 | 10–20 | 80–160 | 300–650 |
| K12 frozen | 15–28 | 120–190 | 450–750 |
| K12 T1 | 25–38 | 170–225 | 650–900 |

Falsifiable statements: (i) at matched cap and stage, whole-proof is **below** the proof-state model (SN-v2 cap 6 /
SN-cap12, same 3.2M size) on textbook72 and holdout250 in ≥ 3 of the 4 cap × stage cells; (ii) C0 T1 is **above**
Robbie's `lean-naive-ei` cells (textbook72 6–10, holdout250 37–45) on both pools; (iii) fewer than 0.1 % of samples
hit max_new 512. Cost ≤ $1.5. Seeds: 2 per cell (as inherited), so per-cell differences under ≈ 7 textbook72 problems
are read as inside the floor (`NOISE_FLOOR.md`; textbook72 MDD ≈ 6.5–9.3 at n = 2–3, from best-state).
