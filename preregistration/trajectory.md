# Pre-registration — run `trajectory` (proposal 18: log-likelihood and pass@k of the eventual proofs, through pretraining and RL)

Written 2026-10-01 ~06:45 UTC, before the first pod. Executor (agent:claude). Policy: `AGENT_POLICY.md`. Lean alone decides
(the state environment's gate, `lean_judge`); `nd_verify` judges nothing.

## Question

For a proof best-cap12 eventually finds, when does that proof become likely: during pretraining, during RL, or only
at the end? Do theorems only RL solves (B) look different along the way from theorems pretraining already solves (A)?
And for theorems nothing solves (C), is there one step of a known proof that stays improbable throughout?

## Models (every number below names one of these)

`best-state`'s **best-cap12** recipe, 3 fresh seeds (0, 1, 2), unchanged except that checkpoints are kept:
- `ALiBiGPT` 6 × 384 (9,560,832 params), `lean_staten` (environment-assigned names), from scratch on K12
  `data/kh/train_k12.jsonl` (155,000 records, cap 12), Muon + AdamW, MTP 0.3, `state_train.py --recipe best
  --budget_secs 1200` on one A40. Same data, flags and seeds as `best-state`'s `stage1_best12_s{0,1,2}_b1200.pt`; a
  retrain is not bit-identical (wall-clock schedule, compile).
- **Pretraining checkpoints (14):** steps 0 (initialisation, before the first update), 50, 100, 200, 400, 800, 1,600,
  3,000, 5,000, 8,000, 12,000, 16,000, 20,000, and the last step (≈ 24k). Saving pauses the schedule clock, so the
  cosine schedule over 1,200 s of training is the one `best-state` ran. Every save is uploaded (`save_ckpt`).
- **T1 ladder:** `state_ladder_ei.py` with `best-state`'s invocation (`pod/bs/seed.sh`: 8 rounds × k 32, T 0.8,
  `rl_targets.jsonl`, replay from K12, `max_steps` 48, `max_action` 256, ladder batch 2,048). RL checkpoints r0 (= the
  last pretraining checkpoint) to r8; the ladder already keeps and uploads every round.
- 22 distinct checkpoints per seed, 66 in all.

## Theorems and targets

textbook72 (`data/bs/textbook72.jsonl`, all 72, dev58 + train14) and holdout250 (`data/bs/holdout250.jsonl`), read
as in `best-state`. Evaluation only; nothing trains or tunes on them.

- **Eventual proof** (per seed, theorems the final RL checkpoint r8 solves): among r8's distinct Lean-accepted
  seed-0 samples at k 256, the one with the highest log-likelihood under r8 (definition below).
- **Reference proof:** textbook72 has no reference proof *texts* (its records carry only `reference_lines`), and
  neither pool record carries a proof. So: holdout250 → the shortest known ND proof from the ladder-A labelling run
  (`minlen.py` output, bucket `ladder-A/data/ladder/raw_textbook_minlen.jsonl` for the 90 textbook-schema theorems,
  `pool_long_minlen.jsonl` for the 160 generator theorems; matched by prompt; 250 / 250 found, 250 / 250 convert with
  `decompose`). textbook72 → `minlen.py` run now on the 72 prompts (bound 14, 120 s), the same labeller that produced
  the pools' `L_true`. **Every reference proof is then checked by Lean** (`lean_judge.judge_many`); one Lean rejects or
  minlen cannot find is reported and left without a reference. minlen's own internal `nd_verify` call is the labeller's
  unchanged code path; it filters candidates, it does not decide any counted result. These are not hand- or
  LLM-written proofs and are used only as scoring targets.

## Scoring, per checkpoint (pretraining and RL alike)

**Teacher-forced log p** (`tj_score.py`, after `lm_m1.py` of lit-measures M1): the target's ND proof →
`decompose(canon=True)` → actions; replayed in `Env(canon=True, assign=True, base=b)` — the sampler's environment,
which assigns the names a step introduces — and every action must apply without renaming and reassemble the proof.
Prompt = state tokens, target = action tokens + `<eos>`; log p from one causal forward pass, natural logs.
- The sampler draws the name base b ~ U{0..32}, so the score is exactly marginalised over it:
  L(t) = logsumexp_b cum_b(t) − ln 33, step t's contribution = L(t) − L(t−1) (L(0) = 0). Contributions sum to
  log p(proof) under the sampler's base distribution; each is the posterior-weighted log p of that step.
- **Primary: T = 1.0** (the model's own distribution). T = 0.8 (the sampling temperature) is stored too.
- Per target: per-step log p; total; per-step mean; worst step w1 (value, index, kind — premise `have`, atomic-term
  `have` by head constant, box opener imp/neg/Or.elim, `exact`); second-worst w2; length in actions and term size.

**Samples** (`state_eval.py`): k 256, T 0.8, `max_steps` 96, `max_action` 512, batch 2,048 — `best-state`'s read-out
settings, held fixed for every checkpoint.
- **Seed 1 at every checkpoint** → pass@1, @8, @64, @256 (unbiased estimator, n = 256).
- **Seed 0 at r0 and r8 only** → group membership and the eventual proofs. (The brief's budget option; seed 0 at
  intermediate checkpoints is dropped.) Seed 0 at r0 / r8 uses `best-state`'s exact protocol, so it is the sanity check.

**Groups** (per training seed, seed-0 samples, made disjoint): **A** r0 solves; **B** r8 solves and r0 does not;
**C** neither solves. Theorems r0 solves and r8 does not stay in A and are counted separately ("A-lost").

## Expected results (numeric, per training seed unless stated; 322 theorems = 72 + 250)

1. **Sanity:** seed-0 r0 / r8 counts reproduce `best-state` best-cap12 within its spread ± the pre-registered MDD
   (textbook72 MDD 6.5): textbook72 Fz in 22–38 (best-state 32 / 27 / 27), T1 in 46–57 (52 / 51 / 52); holdout250 Fz
   175–205 (184 / 195 / 182), T1 230–245 (239 / 237 / 237). A miss on two of the three seeds means the retrain is not
   the same model, and the write-up says so.
2. **Group sizes:** A ≈ 216 (range 200–232), B ≈ 72 (55–90), C ≈ 32 (20–45), A-lost ≤ 4.
3. **B's eventual-proof worst step climbs mainly in RL (the headline prediction).** Median over B of w1 (T 1.0):
   ≤ −5 nats at r0 (range −12 to −3); ≥ −1.5 at r8. Define Δ_RL = w1(r8) − w1(r0) and Δ_PT = w1(r0) − w1(step
   1,600) (step 1,600 ≈ 7 % of pretraining, by which point the format is learned; init is uniform and degenerate).
   Predicted median_B Δ_RL ≈ +5 nats (range +3 to +10), median_B Δ_PT ≈ +1 (−1 to +3).
   **Falsifier:** median_B Δ_RL ≤ median_B Δ_PT in 2 of 3 seeds, or median_B w1(r0) ≥ −2.5 nats in 2 of 3 seeds
   (then B's proofs were already likely after pretraining and RL is sharpening).
4. **Totals:** median total log p of the eventual proof at r0: A ≈ −3 (−6 to −1), B ≈ −14 (−25 to −7); at r8: A ≈ −1.5,
   B ≈ −3 (−6 to −1). Per-step mean at r0: B lower than A by ≥ 0.5 nats.
5. **Concentration (as M1):** at r0, B's eventual proofs have one bad step: median w1 at least 4 nats below the median
   of their remaining steps' mean; w1 is a box opener (Or.elim / neg / imp) or an `exact` closing a box in ≥ 50 % of B.
6. **Late pretraining is flat for B:** median_B w1 changes by < 1.5 nats from step 8,000 to the end (A: < 1.0).
7. **C's reference proofs:** median w1 ≤ −8 nats at every checkpoint, and RL moves it by < 2 nats (r8 − r0).
8. **Reference vs eventual for B:** Δ_RL on B's reference proofs is smaller than on their eventual proofs (by ≥ 1 nat,
   2 of 3 seeds): RL lifts its own proofs more than a fixed known proof.
9. **pass@k (seed 1):** B at r0: mean pass@256 ≈ 0.15 (0.05–0.30), pass@1 ≈ 0.002; B at r8: pass@1 ≈ 0.3 (0.15–0.5),
   pass@256 ≈ 0.9. A: pass@1 ≈ 0.35 at r0, ≈ 0.6 at r8. C at r8: pass@256 ≈ 0.05.
10. **Pretraining pass@256 for B is monotone** within noise (no checkpoint before the last exceeds the last by > 0.10).
    A violation is a finding (pretraining first reaches, then loses, B).

## Noise and decision rule

Headline quantities are medians over a group's theorems, computed within each seed (paired, theorem-level), then
across seeds as per-seed values + IQM (= mean at n = 3) with a stratified bootstrap 95 % interval (theorems within
seed). No noise floor exists for these log-likelihood quantities; I expect a seed SD of a group median of ≈ 1 nat,
which gives an MDD of ≈ 3 nats for an across-seed one-sample comparison (n = 3, 80 % power). The predicted Δ_RL − Δ_PT
(≈ 4 nats) is above that, but only just, so the claim needs all three seeds in the same direction; otherwise it is
reported as "not resolved at n = 3". The group-size and count comparisons with `best-state` use its MDDs. The measured
seed SD is reported.

## Example theorems for the heatmaps (rule fixed now)

Per group, from training seed 0: the 4 theorems with the smallest `sha1(name)` among those whose tracked proof has
6–14 actions (A, B: eventual proof; C: reference proof). Heatmap = per-step log p (T 1.0) × checkpoint.

## Budget, compute record and stop rule

Budget **$30 / 60 pod-hours** (`podbudget trajectory --set 60 30`), A40 at $0.49/h. Plan ≈ 46 pod-hours ≈ $23:
3 trainer pods (Stage-1 0.4 h + T1 ladder ≈ 7–8.5 h + setup) ≈ 27 h; reader pods for 72 sampled reads (≈ 12–17 min
each from `best-state`'s logs) + teacher-forced scoring + minlen ≈ 19 h. Compute rows per arm and round
(`gpu_seconds`, `gen_tokens`, `train_steps`, `train_tokens`, `lean_checks`) from the scripts' registry rows and job logs.
**Stop rule:** if projected pod-hours exceed 56, drop seed-1 reads of pretraining checkpoints 50 and 200 and of RL
rounds 3, 5, 7 (in that order) before anything else; teacher-forced scoring is kept at every checkpoint. Pods are
deleted as their work is pulled. Balance floor $100.

## Deviations already known

- Seed-0 samples only at r0 / r8 (brief's budget option).
- Reference proofs from minlen labels, since no textbook reference texts exist (above).
- Read-out caps as `best-state` (`max_action` 512, `max_steps` 96). `best-state` measured 1–2 % truncation on best-cap12
  T1 textbook72, shown by its 2× cap diagnostic to be non-terminating actions (+≤ 2 solves). Truncation is reported per
  checkpoint and group; caps are not raised, so the endpoints stay comparable with `best-state`.
