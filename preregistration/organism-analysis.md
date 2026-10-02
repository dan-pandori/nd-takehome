# Pre-registration: organism-analysis — what predicts RL success, and what RL learns, from data already on disk

Run id `organism-analysis` (executor, 2026-10-02). Brief: proposal 21 (Dan, 2026-10-02). Policy: `AGENT_POLICY.md`.
Budget **$8 / 16 pod-hours**, forward passes on stored checkpoints only. **No training.** Lean alone decides
everything counted here; every count is inherited from Lean-judged reads (`lean_judge`); `nd_verify` judges nothing.

## Inputs (all inherited, all reviewed; labels carried)

| tag | model | checkpoints used | source |
|---|---|---|---|
| **c12** | best-cap12: `best_model.ALiBiGPT` 6×384, 9,560,832 params, `lean_staten`, from scratch on K12 `data/kh/train_k12.jsonl` (155k, cap 12), Stage-1 1,200 s A40; seeds 0–2 | pretraining p0…p20000, pend (= r0); T1 EI ladder r1–r8 (8 × k32, T 0.8) | `trajectory` |
| **c6** | best-cap6: same network/recipe on cap-6 `train_depth3_f0_a1.jsonl` (155k); seeds 0–2 | same 22 per seed | `trajectory-cap6` |
| **rfc** | c12 seeds 0–2, EI ladders started from pretraining steps 1,600 / 5,000 / 12,000 / 16,000 | start (= r0), r2, r4, r8 | `rl-from-ckpt` |

Per-theorem data: sampled reads (k 256, T 0.8, `max_steps` 96, `max_action` 512; sample seeds x0, x1) on textbook72 +
holdout250 (322 theorems; evaluation only, never trained on — the analysis fits *predictors of RL outcomes* on them,
not a policy), and teacher-forced per-step log p (T 1.0, name-base marginalised, env-assigned names unscored) of the
315 shortest-known reference proofs (`minlen`, ND-derived) and of each run's eventual proofs.
`grpo-best` is not DONE at the time of writing; it is included only if its summary is recorded before the analysis
starts, otherwise the write-up says it was not included.

## Q1. What predicts RL success?

- **Unit:** (theorem, seed, start) for the 315 theorems with a reference proof. Starts: c12 pend, c6 pend, rfc
  p1600 / p5000 / p12000 / p16000. **Population (primary):** units the start does not solve (x0 read at the start,
  `n_ok` = 0). **Target:** solved by the x0 read at r8 (`n_ok` > 0). Robustness: same with x1.
- **Features, all from the reference proof under the start checkpoint** (the eventual proof exists only when the target
  is 1, so it is excluded as leakage): worst, 2nd, 3rd worst step log p (w1, w2, w3); number of steps < −4 and < −8;
  total log p; ND lines; Lean term size (`tj_score`'s `term_size`) and number of actions; kind of the worst step
  (box:imp / box:neg / box:orelim / ∧-projection / application / Or.intro / ⟨⟩ / prem / exact / other); slope of w1
  over the last pretraining checkpoints: OLS of w1 on log10(step) over the start and the two pretraining checkpoints
  before it (pend: p16000, p20000, pend).
- **Models:** logistic regression (standardised, L2, C = 1) and a small gradient-boosted model (sklearn
  `HistGradientBoostingClassifier`, max_depth 3, 100 iterations, lr 0.1); fixed hyper-parameters, no tuning.
  Baselines: w1 alone (logistic) and a single threshold on w1.
- **Cross-validation:** (i) within run, folds = held-out seed × held-out theorem fold (5 hash folds), so no seed and no
  theorem is in both train and test; (ii) across caps: train c12 pend → test c6 pend, and the reverse; (iii) across
  starts: train c12 pend → test each rfc start. Metric: AUC (and log loss, Brier); 95 % interval by bootstrap over
  theorems; per-seed values reported. Feature importance: standardised logistic coefficients and permutation
  importance (AUC drop) of the GBM on held-out folds.
- **"Does one worst-step threshold suffice?"** Yes iff the full logistic model's CV AUC exceeds the w1-only model's by
  less than 0.03 *and* the paired-bootstrap 95 % interval of the difference includes 0.03 or less.
- **Expected:** w1-only AUC 0.75–0.88 in c12 pend and c6 pend; full logistic adds ≤ 0.04 (w2 / n<−4 the next
  features); GBM within ±0.03 of logistic; w1 is the top feature in both models; worst-step kind adds < 0.02.
  The fitted 50 % point of w1 lies between −16 and −9 nats (rfc's x50 −11 to −15). Transfer c12 → c6: AUC drops by
  ≤ 0.05 but the 50 % point shifts by ≥ 1.5 nats (calibration differs between caps; c6's C references sit near −12.8
  vs c12's −9). Transfer c12 pend → rfc starts: AUC ≥ 0.70 at p5000–p16000, lower at p1600.

## Q2. What RL learns, step by step

- **Hard step:** a reference-proof step with log p < −4 nats at r0. **Taxonomy** from the action text: box:imp,
  box:neg, box:orelim, ∧-projection (`n .1` / `n .2`), application (`n m`, →E / ¬E), Or.inl / Or.inr, ⟨⟩ (∧I),
  premise restatement, exact, other (absurd / False.elim / byContradiction …). Per class and round: median per-step
  log p of hard steps (c12, c6 r0–r8; rfc r0/r2/r4/r8).
- **Transfer:** for each class, compare per-step gain Δ = lp(r8) − lp(r0) of hard steps in theorems **never solved by
  any read r1–r8** (x0 ∪ x1; "never sampled") with (a) same-class hard steps in solved theorems and (b) a **matched
  control**: hard steps of other classes in never-solved theorems, matched on r0 log p (1-nat bins) and run/seed.
  Also: across classes, Spearman of the class's gain in never-solved vs solved theorems; and partial R² of class
  in Δ ~ r0 log p + class. Exposure: count of steps of each class in each round's EI training records (`mix_<r>`
  RL part), done on the pod, related to the class's gain.
- **Expected:** box openers + ∧-projections make up ≥ 60 % of hard steps in both caps. Every class with ≥ 20 hard steps
  gains on average in solved theorems (> +2 nats c12, > +4 nats c6). In never-solved theorems hard steps gain less
  (median < +1.5 nats c12) but same-class steps gain more than matched other-class controls by ≥ 0.5 nats in at least
  half the classes; class partial R² ≥ 0.05; cross-class Spearman (never-solved vs solved gain) > 0.4.
- **Gallery rule** (12–20 examples, fixed before looking): for each of the 6 most frequent hard-step classes (pooled
  c12 + c6), the solved (B) theorem of seed 0 whose class hard-step gain is the median of its class (c12 and c6 →
  up to 12) and, for the 4 most frequent classes, the never-solved theorem with the median gain (c12) → up to 16.
  Each rendered in Lean (`nd2lean`) with per-step log p at r0 and r8; for B also r8's eventual proof.

## Q3. Entropy and diversity (the only GPU use)

- **Forward passes** (one pod, RTX-class GPU) on c12, c6 (p16000, p20000, pend, r1–r8; 3 seeds) and rfc (r2, r4, r8;
  12 ladders): (a) teacher-forced per-token entropy (T 1.0 and T 0.8, scored tokens only) on the reference and
  eventual proofs at name base 0; (b) on-policy entropy: 4 attempts × 1,024 fixed RL targets
  (`data/ladder/rl_targets.jsonl`, random subset, seed 0) at T 0.8 with the stored sampler, mean entropy of the T 1.0
  and T 0.8 distributions over all generated action tokens. Batch 2,048; peak memory and truncation reported.
- **Diversity:** distinct Lean-accepted proofs per theorem from the stored reads (distinct ND strings as stored, and
  distinct after `gen.canon_key`-free normalisation of whitespace), per round, per group.
- **Cui fit:** per ladder, R(r) = −a·e^{H(r)} + b, r = 0…8, H = on-policy entropy (T 0.8), R = (i) EI training-target
  sample accuracy (`round_<r>.json`, r ≥ 1) and (ii) x1 pass@1 on the 322 eval theorems. Report a, b, R², and b − a.
- **Collapse vs stall:** stall round = first round at which group-C solved count (x0 ∪ x1 cumulative) reaches its r8
  value; collapse round = first round at which median distinct proofs per A-theorem falls below 50 % of its maximum.
  "Diversity collapses before C stalls" iff collapse round < stall round, per ladder.
- **Expected:** on-policy entropy falls monotonically from r0 to r8 in ≥ 5/6 c12 + c6 ladders, by ≥ 30 %; most of the
  drop in r1–r2. Hard-step entropy falls more than easy-step entropy. Cui fit R² ≥ 0.8 on training accuracy for
  ≥ 4/6 ladders, with b − a (predicted R at H = 0) within 0.1 of the r8 value. Distinct proofs per A-theorem peak at
  r1–r2 and fall ≥ 30 % by r8. Collapse round ≤ stall round in ≥ 4/6 ladders.

## Noise, seeds, MDD

Three seeds per arm (inherited; no new seeds possible without training). The measured seed SD of a group median of w1
is 0.5–0.7 nats (`trajectory`), MDD ≈ 2 nats at n = 3: Q2 per-class differences under 2 nats in per-seed medians are
reported as not resolved. For AUC, the seed spread of per-seed CV AUC sets the MDD (computed and stated); AUC
differences inside it are not findings. Per-seed values plus IQM with stratified-bootstrap 95 % intervals.

## Stop rule and budget

One pod; stop when the 108 checkpoints are scored or at $6 spent, whichever is first; if the on-policy pass is too
slow, drop to 512 targets (stated). `podbudget organism-analysis --set 16 8` before the pod. Compute (GPU-s, generated
tokens, forward tokens) recorded per job as registry rows. No training, no `test_run_once.sh`.
