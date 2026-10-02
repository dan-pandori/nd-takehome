# Pre-registration: grpo-best — GRPO against expert iteration on the model organism, from the same starting checkpoints

Run id `grpo-best`. Written 2026-10-02 before any pod. Brief: run brief `grpo-best` (nd-rl literature shortlist item 3,
on Robbie's recipe). It adapts `preregistration/grpo-state.md` (on `origin/dan_grpo-state`) to `trajectory`'s
checkpoints and EI ladders. Judge: **Lean alone decides** (the fork's `dan` judge: strict `lean_seq` grammar + Lean on
the literal assembled text, state-environment gate). No `nd_verify` anywhere. Proof length is reported in actions and
Lean term size. The pools' `L_true` labels are ND-derived upper bounds.

## 1. Question

Does GRPO, and in particular the variants that credit rare correct proofs, solve theorems that expert iteration from the
**same checkpoint** could not? The run-4 finding (GRPO acquired the depth-3 pattern from zero where EI mostly did not) was on
the token format, under Lean ∧ `nd_verify`, and its checkpoints are lost. `trajectory` gives a clean comparator: three
starting checkpoints, an EI ladder from each with per-theorem read-outs, and group C (never solved by EI).

## 2. Models (every number in this run)

- **Base:** `trajectory`'s fresh best-cap12 s0 / s1 / s2 at the end of pretraining:
  `hf://buckets/dan-pandori/nd-rl/trajectory/ckpts/tj/stage1_best12_s{0,1,2}_b1200.pt`. Robbie's `best_model.ALiBiGPT`
  6 × 384, **9,560,832 params**, `lean_staten` (environment-assigned names), from scratch on K12
  `data/kh/train_k12.jsonl` (155,000 generator proofs, lengths 2–12), `state_train.py --recipe best --budget_secs 1200`
  on one A40.
- **EI arm (inherited, not re-run):** `trajectory`'s T1 ladders `ckpts/tj/ladder/la_T1_best12_s{S}_r{1..8}.pt`
  (`state_ladder_ei.py` defaults: 8 rounds × k 32 on `data/ladder/rl_targets.jsonl` (4,495), T 0.8, `max_action` 256,
  `max_steps` 48, fine-tune 600 steps × 128 proofs per round with AdamW lr 3e-4 → 3e-5 (wd 0.1), retain 20,000 K12
  records, max 4 proofs per theorem, RL weight 4; RTX A6000). Its read-outs (below) are `trajectory`'s files.
- **GRPO arms (new):** from the same base checkpoint per seed, `grpo_state.py`, loading the ALiBiGPT through
  `model.load_ckpt` (the path `state_ladder_ei` uses). Tested before the first pod by CI on a tiny ALiBiGPT
  (`ND_GRPO_TEST_ARCH=best tests/test_grpo_state.py`: gradient = autograd of −Σ A log π at T, chunk-size independence,
  sampled tokens = teacher-forced argmax at T 0.01, smoke per variant).

## 3. Arms (3 seeds each: s0, s1, s2; GRPO sampling seed = the base seed)

| arm | command difference |
|---|---|
| EI (inherited) | `trajectory` T1 ladder |
| GRPO-default | `--adv default` (A = R − group mean) |
| GRPO-unlikely | `--adv unlikely --beta_rank 0.25` (He et al. 2506.02355 §4.1) |
| GRPO-pass@k | `--adv passk --passk_k 4` (Chen et al. 2508.10751 §2.4; PKPO-equivalent) |
| GRPO-distinct (optional) | `--adv distinct --bonus 0.5`; only if § 9's measured cost leaves ≥ $12 after the three arms and their read-outs |

Shared GRPO settings (grpo-state's, unchanged): G 8, 256 theorems per update (2,048 rollouts = one decode batch), targets
`data/ladder/rl_targets.jsonl`, transfer `data/ladder/transfer.jsonl`, held-out `data/p2/heldout.jsonl`; T 0.8,
`max_action` 256, `max_steps` 48 (the EI ladder's caps); 8 round-equivalents, k 32 → 1,150,720 // 2,048 = **561 updates**.
**Optimizer for the RL updates: AdamW, lr 3e-5 constant, β (0.9, 0.95), weight decay 0, grad-norm clip 1.0**; fixed loss
divisor 256 · 8 · 400; no KL; no std normalisation; one on-policy update per sampled batch; log-probs at the sampling
temperature. `lp_batch` (pairs per forward/backward chunk) is set from the smoke to fit memory; it does not change the
gradient (CI test 2). Fast decode path (`ND_SAMPLE_PATH=fast`).

## 4. Compute matching

- **Matched:** sampled attempts. EI's clean ladder = 1,793,960 = 8 × 32 × (4,495 targets + 2,285 transfer) + 8 × (2,285
  + 5,000) greedy. GRPO: 561 × 2,048 = 1,148,928 target rollouts (1,792 = 0.16 % fewer than EI's 1,150,720) + the same
  boundary transfer pass@32 and greedy evaluations = 1,792,168. Temperature, action and step caps are equal.
- **Not matched, recorded** (`record.phase` rows, per round-equivalent): GPU-seconds (GPU type), generated tokens, actions,
  training steps, training tokens, Lean checks. EI's per seed (`trajectory` `tj_compute.py`): 22,350 / 24,467 / 27,021
  GPU-s on RTX A6000, 754 / 783 / 751 M train tokens, 4,800 train steps. The write-up flags any GRPO arm above 1.25× EI
  on any of these. EI's training also replays 20,000 K12 records per round (≈ 480 M tokens of further pretraining,
  `rl-from-ckpt`); GRPO trains only on its own rollouts. This favours EI on retention and is stated with every result.

## 5. Read-outs (matching `trajectory`)

- **Sampled:** textbook72 + holdout250 (322), `state_eval.py` k 256, T 0.8, `max_steps` 96, `max_action` 512, batch 2,048
  (1,024 retry on OOM), **sample seeds 0 and 1**, on each GRPO arm's `_r2`, `_r4`, `_r8` checkpoints (round-equivalents of
  EI's r2, r4, r8: the same number of target attempts trained on). EI's are `trajectory`'s files (`pod/tj/read.sh`,
  same settings).
- **End:** the dev metric (`data/bs/dev1108.jsonl`, k 64, T 0.8, seed 0, solved; best-state's `pod/bs/read.sh dev`) and
  held-out greedy (`data/p2/heldout.jsonl`, 5,000, k 1, T 0) on every r8 checkpoint, **EI r8 included** (read here, same
  script).
- Groups (`gb_groups.py`, reproduced from `trajectory`'s files: A / B / C = 232 / 54 / 36, 236 / 51 / 35, 234 / 60 / 28):
  A = end-of-pretraining solves on sample seed 0, B = EI-r8-only, C = neither.

## 6. Analysis and statistics

- **Headline (support):** C theorems solved at k 256 by each arm's r8, per seed. Because C is defined by EI's own seed-0
  failures, EI's seed-0 count is 0 by construction; the comparison uses **sample seed 1** for both arms (a fresh draw for
  EI: 3 / 1 / 1 of 36 / 35 / 28). Also reported: C solved over both sample seeds. Paired per seed with EI.
- **Bias-free companion** (`rl-from-ckpt`'s lesson): over all 322 theorems, theorems solved by the GRPO arm's r8 on either
  sample seed and by EI's r8 on neither, against the reverse; exact two-sided sign test on the discordant theorem-seed
  pairs, pooled over seeds. This is the within-run test that n = 3 seeds cannot give.
- **Sharpening vs support:** pass@1 and pass@256 (unbiased, sample seed 1) by group, per arm, at r2 / r4 / r8.
- **Retention:** held-out greedy, and group A pass@1 / pass@256 at r8.
- **Mechanics:** fraction of groups with reward variance, all-fail fraction, targets cumulative solved, per round-equivalent.
- **Statistics:** per-seed values, IQM with a stratified-bootstrap 95 % interval (Agarwal et al. 2021). **MDD** (two-sample
  t, 80 % power, α 0.05, n = 3 per arm: 3.03 · sd, using EI's between-seed sd):

| quantity | EI per seed (s0 / s1 / s2) | sd | MDD (n = 3) |
|---|---|---|---|
| C solved at r8, sample seed 1 | 3 / 1 / 1 | 1.15 | **3.5** |
| all 322 solved at r8, sample seed 1 | 288 / 284 / 290 | 3.1 | **9.3** |
| textbook72 solved at r8, sample seed 0 (`trajectory`) | 48 / 49 / 54 | 3.2 | **9.8** |
| held-out greedy (Stage-1, `trajectory`) | 0.921 / 0.936 / 0.962 | 0.021 | **6.3 pp** |

  A seed-level difference inside its MDD is reported as "not resolved". The pooled theorem-level sign test (above) is the
  sharper test for the headline; with 99 C theorem-seed pairs it resolves differences of ≈ 8 discordant pairs or more.

## 7. Expected results (falsifiable)

- **E1 (headline).** No GRPO arm solves more C theorems than EI by ≥ the MDD (3.5) in the IQM at r8 on sample seed 1.
  Per seed, each GRPO arm solves **0–5** C theorems (EI 3 / 1 / 1). *Reason:* `trajectory` found C's reference worst step
  at ≈ −9 nats throughout EI; C theorems are not in the RL targets, so any GRPO solve is transfer, and 561 updates at lr 3e-5
  move the policy less than EI's 4,800 fine-tune steps at 3e-4.
- **E2 (variants).** GRPO-pass@k ≥ GRPO-default on C (summed over seeds and both sample seeds) and GRPO-unlikely within
  ± 2 of GRPO-default; neither difference exceeds the MDD. The literature's claim (support-expanding advantages
  ≥ 1.2× default) is stated for comparison; I expect it to be unresolvable at these counts.
- **E3 (bias-free companion).** For GRPO-default, the discordant pairs (GRPO-only vs EI-only, all 322, pooled seeds) do
  **not** favour GRPO at p < 0.05; I expect EI-only ≥ GRPO-only.
- **E4 (sharpening vs support).** At r8, every GRPO arm's group-B pass@1 is below EI's (0.56) and in 0.15–0.55; group-B
  pass@256 in 0.6–0.95 (EI 0.96). Group-A pass@1 rises from 0.40 (end of pretraining) to 0.55–0.85.
- **E5 (retention).** Every GRPO arm's held-out greedy at r8 is within 3 pp of its Stage-1 base (0.921 / 0.936 / 0.962),
  and EI r8's is ≥ GRPO-default's in ≥ 2 of 3 seeds (K12 replay).
- **E6 (mechanics).** GRPO-default's fraction of groups with reward variance averages 0.25–0.60 over a run; mean reward
  rises by ≥ 0.15 from update 1 to update 561.
- **E7 (compute).** Each GRPO ladder's GPU-seconds are within 0.6–1.25× of EI's on the same GPU class; train tokens
  within 0.5–1.25× of EI's.
- **What would change the project's story:** a GRPO arm beating EI on C by more than the MDD in IQM *and* on the pooled
  sign test (p < 0.05) would be RL from this checkpoint reaching theorems EI could not, the run-4 finding reproduced on
  the current model family.

## 8. Stop rule

- **Budget: $45, 90 pod-hours** (`podbudget grpo-best --set 90 45` before the first pod). Balance floor $100.
- **Smoke first** (one RTX A6000, ≤ 45 min): s / update for one job and for two jobs per card, peak memory, `lp_batch`.
  Its projection is written as an addendum before the nine ladders are launched.
- **Cuts if the projection exceeds $42**, in this order: (1) r2 reads on sample seed 1 only; (2) r4 likewise; (3) drop
  GRPO-unlikely for all seeds. Never seeds for some arms only.
- **Collapse:** a GRPO run whose held-out greedy at boundary 2 is below 0.80 is stopped and reported as collapsed at
  lr 3e-5; no re-run at another lr inside this pre-registration.
- **Failures:** an OOM'd run resumes or restarts at decode batch 1,024 (recorded); anything else is reported, not retried
  more than once.

## 9. Costing

Estimate before the smoke: a GRPO ladder ≈ the EI ladder's 22–27 k GPU-s on an RTX A6000 (same sampling, ≈ equal train
tokens) ≈ 7 h × $0.53 ≈ $3.7, × 9 = $33; read-outs 9 × 3 checkpoints × 2 sample seeds × ≈ 9.5 min ≈ 8.6 h ≈ $4.5;
end reads (dev + held-out greedy, 12 checkpoints) ≈ 2 h ≈ $1; smoke + setup ≈ $2. **≈ $41**. The smoke replaces these
with measurements (addendum).
