# Pre-registration — run `trajectory-cap6` (the `trajectory` analysis on the cap-6 model organism)

Written 2026-10-01 ~20:00 UTC, before the first pod. Brief: nd-rl `docs/proposals/state-env/BRIEF_trajectory-cap6.md`
(which applies `BRIEF_trajectory.md` unchanged except for the points below). Proposal: nd-rl
`docs/proposals/2026-10-01-learning-trajectory.md`. Template: `preregistration/trajectory.md` (cap 12; run reviewed,
`review_trajectory.md`, verdict "stands" with rewording). **Lean alone decides.**

## Question

When does the proof a model eventually finds become likely — in pretraining or in RL — and how does that differ between
a model pretrained on short proofs (cap 6) and one pretrained on longer proofs (cap 12)? In particular: for theorems
that are **B at cap 6** (only RL solves them) **but A at cap 12** (pretraining alone solves them), what does RL do at cap
6 that longer training proofs do at cap 12?

## Models (every number below names one of these)

- **best-cap6 s0 / s1 / s2 (new, fresh):** `best-state`'s best-cap6 cell — Robbie's recipe ported as `state_train.py
  --recipe best` (ALiBiGPT 6 × 384, 9,560,832 params), `lean_staten`, from scratch on the cap-6 control set
  (`hf://buckets/dan-pandori/nd-rl/state-env/data/p2/train_depth3_f0_a1.jsonl`, 155,000 records), `--cap 6`, Stage-1
  1,200 s on an A40, held-out greedy on `data/p2/heldout.jsonl`. Kept checkpoints (as `trajectory`): steps 0, 50, 100,
  200, 400, 800, 1,600, 3,000, 5,000, 8,000, 12,000, 16,000, 20,000 and the end (`pend` = r0). Then the T1 ladder,
  `state_ladder_ei.py` defaults (8 rounds × k 32, T 0.8, replay from the same cap-6 set), every round kept (r1–r8).
  Scripts: `pod/tj6/` (generated from `pod/tj/` by path / cap substitution; `pod/tj6/seed.sh`).
- **best-cap12 s0 / s1 / s2 (inherited from `trajectory`)**, K12, same recipe, for the comparison only; their
  per-theorem records are read from `hf://buckets/dan-pandori/nd-rl/trajectory/artifacts/` and keep their label.
- Sanity reference: `best-state`'s best-cap6 s0–s2 (`numbers.md` § best-state).

## Theorems, targets, scoring — exactly as `trajectory`

textbook72 (72) + holdout250 (250), evaluation only. Reference proofs: `trajectory`'s 315 (`data/tj/ref_targets.jsonl`,
copied unchanged to `data/tj6/`; 65 / 72 textbook72 + 250 / 250 holdout250; model-independent). Eventual proof: r8's
highest-likelihood (T 1.0) distinct Lean-accepted seed-0 sample at k 256. Teacher-forced log p (`tj_score.py`,
unchanged): environment name assignment, names the environment assigns are not scored, base-marginalised over the 33
name bases, fp32, T 1.0 primary. Samples (`state_eval.py`): k 256, T 0.8, `max_steps` 96, `max_action` 512, batch
2,048 (retry at 1,024 on OOM), **both sampling seeds (0 and 1) at all 22 checkpoints** of every training seed (budget
allows; Dan prefers completeness). Groups per training seed from seed 0: **A** r0 solves; **B** r8 solves, r0 does not;
**C** neither; A-lost counted separately. pass@1/8/64/256 from seed 1 (unbiased estimator, n = 256).

**Added for this run (scored under all 22 checkpoints of each cap-6 seed, `pod/tj6/score_cross.sh`):**
- **Cross-seed eventual proofs:** each cap-6 seed's eventual proofs scored under the *other* cap-6 seeds' checkpoints.
  This is the review's next measurement (a): an eventual proof not selected by the model that scores it.
- **cap-12 eventual proofs** (`trajectory`'s, 3 seeds) scored under the cap-6 checkpoints: the same fixed proof under
  both pretraining distributions.

**Cap-6 vs cap-12 theorem sets** (fixed now): a theorem is **A12** if it is in A in ≥ 2 of 3 `trajectory` seeds, **B6** if
it is in B in ≥ 2 of 3 cap-6 seeds (likewise A6, C6, B12, C12). **B6∩A12** is the comparison set.
**Joint figure** (`figures/tj6_joint.png`): for theorems tracked in both runs, median (IQR) of the eventual proof's worst
step, total and per-step mean by group, cap 6 and cap 12 on the same axes (x = pretraining log steps, then r1–r8); one panel
row for B6∩A12 with: cap-6 own eventual proof under cap 6, cap-12 eventual proof under cap 6, cap-12 eventual proof under
cap 12 (from `trajectory`'s records).

## Expected results (per training seed unless stated; 322 theorems)

1. **Sanity** vs `best-state` best-cap6 (seed-0 reads, x0), within its spread ± its cap-6 textbook72 MDD (9.3):
   textbook72 r0 in 9–29 (best-state 19 / 18 / 20), r8 in 24–49 (39 / 40 / 33); holdout250 r0 in 105–165 (149 / 125 /
   122), r8 in 210–245 (226 / 229 / 227). A miss in 2 of 3 seeds means the retrain is not the same model, and I say so.
2. **Group sizes:** A ≈ 150 (125–180), B ≈ 110 (85–135), C ≈ 58 (40–80), A-lost ≤ 6. B is larger than at cap 12
   (54 / 51 / 60) in 3 / 3 seeds.
3. **Headline: at cap 6, B's eventual-proof worst step climbs more in RL than in pretraining.** Δ_RL = w1(r8) − w1(r0),
   Δ_PT = w1(r0) − w1(step 1,600), medians over B within seed. Predicted median_B w1(r0) ≈ −7 (−12 to −4), w1(r8) ≥ −1.5,
   Δ_RL ≈ +6 (+3 to +10), Δ_PT ≈ +3 (0 to +5). **Falsifier:** median_B Δ_RL ≤ median_B Δ_PT in ≥ 2 of 3 seeds.
   **Decision rule:** "RL-dominated" needs Δ_RL > Δ_PT in all 3 seeds *and* the IQM difference ≥ 2 nats (≈ the MDD
   from `trajectory`'s measured seed SD of 0.5–0.7 nats per group median at n = 3); otherwise "not resolved at n = 3".
   The same contrast is reported, with the same rule, on two selection-free targets: B's **reference** proofs and B's
   **cross-seed** eventual proofs. Prediction: reference Δ_PT ≥ Δ_RL (as at cap 12, 3 / 3) — i.e. the RL-over-PT
   excess, if any, is on the model's own kind of proof; cross-seed Δ_RL lies between reference and own (≥ +2).
4. **Cap 6 vs cap 12 on B6∩A12** (pooled over seeds; size predicted ≈ 70, range 45–100):
   a. Proof length: median action count of the cap-6 eventual proof on B6∩A12 exceeds that on A6∩A12 by ≥ 2.
   b. At the end of pretraining, cap-12's eventual proof is improbable under cap 6: median worst step ≤ −4 nats under
      cap-6 pend, vs ≥ −3 under cap-12 pend (`trajectory`'s records).
   c. Where cap 6 is bad: the cap-6 pend worst step of B6∩A12's own eventual proof is at action index ≥ 7 (1-based) in
      ≥ 50 % of (theorem, seed) pairs — the bad step is past the length the cap-6 set trains.
   d. RL closes the gap: under cap-6 r8, the cap-12 eventual proof's median worst step is ≥ 2 nats higher than under
      cap-6 pend (RL raises the long proof another run found, not only its own).
   e. On B6∩A12 the cap-12 model's worst step on its own eventual proof rises ≥ 3 nats from step 1,600 to pend
      (pretraining does at cap 12 what RL does at cap 6).
5. **Totals (r0):** median total log p, A ≈ −4 (−7 to −1), B ≈ −17 (−30 to −8); r8: A ≈ −2, B ≈ −3 (−6 to −1).
6. **C's reference proofs:** median w1 ≤ −8 at every RL checkpoint r0–r8; |Δ_RL| < 2 (per seed).
7. **pass@k (seed 1):** B at r0 pass@256 ≈ 0.12 (0.03–0.30); B at r8 pass@1 ≈ 0.45 (0.25–0.65), pass@256 ≥ 0.85;
   A pass@1 ≈ 0.35 at r0, ≈ 0.8 at r8; C pass@256 at r8 ≤ 0.10.

## Noise and decision rule

As `trajectory`: within-seed medians (paired, theorem level), then per-seed values + IQM (= mean at n = 3) with a
stratified bootstrap 95 % interval. Measured seed SD of a group median at cap 12 was 0.5–0.7 nats → MDD ≈ 2 nats for
the headline contrast at n = 3. A difference below that is not a finding. The cap-6 vs cap-12 comparisons (4) are
pooled across seeds (theorem sets by majority) and reported with per-seed values where defined.

## Heatmap examples (rule fixed now)

As `trajectory`: per group, cap-6 training seed 0, the 4 theorems with the smallest `sha1(name)` whose tracked proof has
6–14 actions. Plus 4 from B6∩A12 by the same rule (eventual proof), shown under cap 6 and cap 12.

## Budget, compute record and stop rule

Budget **$40 / 80 pod-hours** (registered: `podbudget trajectory-cap6`). Plan ≈ 55 pod-hours ≈ $28: 3 trainer pods
(A40; Stage-1 0.4 h + ladder ≈ 5–6 h at cap 6, from `best-state`'s 16,900–20,100 GPU-s) ≈ 19 h; 132 sampled reads
(≈ 12–17 min each) + scoring ≈ 36 h on reader pods (A40 / RTX A6000). Compute rows per arm (seed) and round: GPU-seconds
and GPU type, generated tokens, attempts, training steps / tokens, Lean checks (`tj6_compute.py` from registry rows and
job logs). **Stop rule:** if projected pod-hours exceed 72, drop seed-0 reads at pretraining steps 50 / 200 / 400 and RL
rounds 3 / 5 / 7 (in that order); seed 0 at r0 / r8, seed 1 everywhere and all teacher-forced scoring are kept. Balance
floor $100.

## Deviations already known

- Read-out caps held at `best-state`'s (`max_action` 512, `max_steps` 96) for comparability with `best-state` and
  `trajectory`; truncation is reported **per stratum** (pool × group × checkpoint), as the cap-12 review asked. Caps are
  not raised; truncation can only move theorems from C to B (or B to A).
- Reference proofs are minlen labels (ND-derived; their lengths are upper bounds under Lean), as `trajectory`.
- Stage-1 on an A40 (wall-clock budget, GPU-dependent); ladders and reads may use RTX A6000 (same GA102) if A40 stock
  runs out — a sampling re-draw, not a correctness change (`NOISE_FLOOR.md`).
