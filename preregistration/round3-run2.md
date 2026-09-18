# Pre-registration: round3-run2 — the 8-line reductio stratum and the derived-ORE base-rate dependence

Written 2026-09-18 05:13 UTC (commit time), before any pod exists. Executor branch `dan_round3-run2`. Brief: `BRIEF_stratum-ignition.md`;
policy: `AGENT_POLICY.md`. Prior results this run builds on: `run5.md`, `review_round2-run5.md` (§Verdict, "Next measurement").

## Question

On the required reductio pool, every igniting run-5 arm solved the 7-line stratum (51–53 of 52) and ≤ 1 of the 248
targets at 8–10 lines in 8 rounds, while the same checkpoints had acquired 25–31 eight-line targets on the 606 pool.
(1) What is the per-run probability that the 8-line stratum ignites, and is it a matter of rounds, of samples per
round, or of f? (2) Does a 6-line stratum (inside the pretraining length) change anything for zero-rate draws?
(3) For strict derived-ORE (cap 8, not a submission result): is EI acquisition at f = 0 proportional to the draw's base
reachability, and is the f-dependence monotone over three points (0, 10⁻³, 10⁻²)?

## Design as run

**Reductio pool** `data/r3_2/targets_reductio_req6.jsonl` — **345** = run 5's `targets_reductio_req.jsonl` (300, records
unchanged, `stratum` := `min_lines_ub`: 7 / 8 / 9 / 10 = 52 / 133 / 82 / 33) + the **45** six-line required candidates of
`data/p2/run5_reductio_nec.jsonl` (all schema `nor_neg_ante`, `~(~A v B) ⊢ A`; `stratum` 6). Built by `r3_2_pool.py`;
`data/r3_2/pool_report.json` records the checks, all passed before this commit: every oracle proof verifies under
`nd_verify` and contains `patterns.reductio` (345 / 345, transfer 150 / 150); all 345 + 150 classically valid and
G4ip-unprovable (`review_run5_logic.py`, so `DN` is required unboundedly); class overlap with `train_reductio_f0`,
`train_reductio_f0.1`, `heldout`, validation-36 and the transfer set: 0 / 0 / 0 / 0 / 0; five six-liners hand-checked
(assume ¬A, ORI1, NEGE against the premise, NEGI, DN — the strict reductio shape, positive conclusion, no `~~` in the
sequent). Transfer set `data/p2/transfer_reductio_req.jsonl` unchanged (150; strata 7 / 8 / 9 / 10 = 27 / 67 / 41 / 15).

**Reductio arms** (`expert_iter.py`, T = 0.8, retain 20k, `--max_per_thm 4`, batch 768; acquisition = targets with a
normalised proof containing `patterns.reductio`, min-round rule; every solved target must be solved with the pattern —
violations are oracle errors and are reported). All arms use the 345 pool.
- **A** — Stage-1 models `stage1_reductio_f0_s0`, `stage1_reductio_f0.1_s0`, `stage1_reductio_f0.1_s1` × sampling seeds
  {0, 1} × **16 rounds at k = 32** (6 arms; names `ei16_reductio_<model>_ss<seed>`).
- **B** — the same 3 models × sampling seed 0 × **8 rounds at k = 64** (3 arms; same attempts as A, half the training
  steps; names `ei8k64_reductio_<model>_ss0`).
- **C** — zero-rate draws `stage1_reductio_f0_s1`, `stage1_reductio_f0_s2` × 8 rounds at k = 32 on the 345 pool (2 arms),
  plus `coverage.py --k 10000` on the 45 six-line targets for s1, s2 (and s0 as the non-zero-rate reference).
- **Frozen controls** (`--no_train`): 16 × 32 for every (model, sampling seed) of A (6 arms, 512 attempts per target,
  equal to A and to B — B's control is the same-seed frozen arm at equal attempts); 8 × 32 for the two C draws.
- Reported per stratum (6 / 7 / 8 / 9 / 10) and per schema per round: cumulative acquired targets, first-proof round,
  ignition (≥ 10 targets of the stratum with a strict reductio proof); transfer per stratum; heldout greedy.

**Derived-ORE, cap 8 (label: "cap 8, not a submission result")** — pool `data/p2/targets_derived_ore_req.jsonl` (300),
transfer (65), unchanged from run 5. Stage-1 draws to train (`train.py --mode abs --steps 6000 --bs 128 --cap 8`):
`stage1_derived_ore_strict_f0.001_c8_s1` (seed 1 on `train_derived_ore_strict_f0.001_c8.jsonl`), `stage1_derived_ore_strict_f0_c8_s2`
and `_s3` (seeds 2, 3 on `train_derived_ore_strict_f0_c8.jsonl`). Base strict reachability of s2, s3: `coverage.py --k 10000`
on the 300 targets (never co-scheduled with another job on a 24 GB card). Keep rule (fixed now): both fresh draws are
kept if their strict reachability (targets with a strict derived-ORE proof at pass@10⁴) differs from 27 / 300 by ≥ 5
targets; otherwise seeds 4, 5 are trained and the deviation disclosed. Arms: EI k = 32 × 8 rounds + frozen for f = 10⁻³
s0 (existing checkpoint) and s1, and for the kept f = 0 draws. Reported: acquisition, frozen, base reachability, EI-only
targets (solved by EI, not base-reachable at 10⁴), monotonicity over f ∈ {0, 10⁻³, 10⁻²} using run 5's f = 0 and 10⁻² arms.

## Pre-registered expected results

- **E1 (A, 16 rounds, k = 32).** The 8-line stratum (133 targets) ignites (≥ 10 targets with a strict reductio proof)
  in **3–5 of the 6** arms; the first 8-line proof falls between rounds 6 and 12; the 9- and 10-line strata (82 + 33)
  stay ≤ 3 targets in every arm. The f = 0.1 arms ignite the 8-line stratum no more often than the f = 0 s0 arms.
- **E2 (B, k = 64 × 8 rounds).** The 8-line stratum ignites in **≤ 1 of 3** arms: training rounds matter more than
  attempts per round.
- **E3 (6-line stratum).** Zero-rate draws s1 and s2: **0 hits** on the 45 six-line targets at pass@10⁴ and **0 / 345**
  after 8 rounds. The f = 0 s0 draw solves ≥ 30 of the 45 six-liners by round 2 in both A arms.
- **E4 (derived-ORE, cap 8).** f = 10⁻³ acquisition **0.08–0.16** for both seeds (between run 5's f = 0 0.080–0.087 and
  f = 10⁻² 0.160–0.210). For each kept fresh f = 0 draw with base reachability r (targets / 300): EI acquisition within
  **0.5–1.5 × r**, EI ≈ 2 × frozen, EI-only targets 5–10.
- **E5 (added; consistency with run 5).** The A seed-0 arms' 7-line stratum over rounds 1–8 reproduces run 5's curve
  (51–53 of 52 at round 8, ± 2); the 6-line stratum does not change the 7-line result.

**What would falsify the standing rule.** E1 at 0 of 6 with E2 at 0 of 3: a real length wall for elicited rule
sequences — clause (2) tightens and "spreads across lengths" is dropped. E3 with any six-line hit in a zero-rate draw
followed by ignition: the wall was length-gated, not pattern-gated. E4 outside 0.5–2 × base reachability: "amplification
in proportion to the base rate" is dropped; EI-only ≥ 20 would mean RL adds substantially beyond the base's reach.

## Budget and stop rule

Three RTX 3090 pods ($0.50 / h; A40 or A100 if none are in stock). Estimate: reductio 6 × ≈ 1 h + 3 × 0.5 h + 2 × 0.3 h +
8 frozen × 0.3 h + 3 short coverage runs ≈ 12 GPU-hours at 3 concurrent jobs per pod ≈ 4–5 pod-hours per pod; derived-ORE
3 Stage-1 × 20 min + 2 coverage × 1.5 h + 8 arms × 0.4 h ≈ 7 pod-hours. **Total ≈ 14–16 pod-hours ≈ $8**, ceiling $50.
Stop at 16 rounds for A or at $30 spent on this run. Pods deleted when their work is pulled. Balance at writing: $274.
Kill switch (Dan's account-wide cron, 2026-09-19 18:00 UTC) left as is.

## Counting rules (fixed now)

Acquisition per stratum from `found_<last>.jsonl` with the min-round rule over (theorem, normalised proof) pairs;
`stratum` from the pool file; ignition threshold 10 targets; first-proof round = min round of any strict reductio proof
in the stratum. Frozen at equal attempts. Differences quoted only with ≥ 2 seeds. Every number in `numbers.md` names its
source file; `r3_2_analysis.py` → `artifacts/r3_2/summary.json`.
