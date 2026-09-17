# Pre-registration: run4-grpo — does GRPO ignite from zero coverage?

Written 2026-09-17 23:00 UTC (committed 23:00:11), before any pod of this run was created (gate 0: compare this
file's commit time with `~/pods.log`). Executor: agent:claude. Branch `dan_run4_grpo`.

## Question

Expert iteration (EI, keep-any-verified-success then supervised fine-tune) crosses zero
pretraining coverage of the depth-3 box pattern in most Stage-1 draws (ignition study, 7 of
10 `a1` draws; 13 of 16 f = 0 draws). Is that a property of EI's keep-any-success rule, or of
RL against a verifier in general? Concretely: does on-policy group-relative policy gradient
(GRPO) with binary verifier reward ignite the depth-3 pattern from a zero base rate, at the
same total sample budget as EI's 8 rounds × 32 samples per target, with groups of 8 and 32?
And what fraction of groups carry any reward variance (the quantity the sprint diagnosed as
the reason its GRPO "saw nothing")?

## What exists and what does not (state found at 22:55 UTC)

- `ckpts/p2/` with the depth-3 f = 0 Stage-1 models (sets a1–a3) does **not** exist on this
  VPS, on the HF bucket (`round2/run5/ckpts/r5/` only) or on the five pods the account runs
  (they hold run-2/run-3 work and `ei_depth3_f0_a1_s{3,4,5}_r4.pt` only). Those pods were
  deleted after the ignition study; the checkpoints were never uploaded.
- The `a1` pretraining set survives on pod p4 (`data/p2/train_depth3_f0_a1.jsonl`, 133 MB,
  Sep 16 01:37). The `a2`/`a3` sets and the pool they were assembled from
  (`pool_cap6_recon.jsonl`) do not survive anywhere; rebuilding the pool is a multi-hour CPU
  job outside this run's scope.
- The 85M / relative-codec arm: the sprint's `nd_grpo.py` is vendored in
  `~/nd-rl/code/experiments/current/r1_cot/vendor/`, but its model/data/codec code
  (`nd_model.py`, `nd_data.py`, the 85M checkpoints) is on Dmitry's machine, not here.
  **Not run**, as the brief allows; its settings (binary reward, group baseline, fixed
  `max_new_tokens` loss divisor, T = 0.8, no KL in the r1-cot runs) are what `grpo.py` copies.

**Deviation from the brief, with the reason.** New Stage-1 draws must be trained, all on set
`a1` (the only surviving set), with new seed numbers (20–25) so they cannot be confused with
the ignition study's s0–s9. Because ignition is draw-dependent (the ignition study's main
finding), GRPO on a new draw next to EI on an old draw would confound algorithm with draw.
So EI **is rerun on the same new draws** as the paired control (≈ $0.40 per arm), and the
earlier EI arms (`artifacts/p2/ei_depth3_f0_a1_s{0..9}`, `numbers.md` §Ignition) are cited
as the prior distribution of EI outcomes on this set, not as the paired comparison.

## Design

Set: `data/p2/train_depth3_f0_a1.jsonl` (155,000 records, cap 6, depth-3 count 0 asserted in
`data/p2/assemble_report_a1.json`). Targets: `data/p2/targets_depth3.jsonl` (1,000, 7–12
generator lines, every one uses a depth-3 box). Transfer: `data/p2/transfer_depth3.jsonl`
(500). Held-out: `data/p2/heldout.jsonl` (5,000). All evaluation pools are class-disjoint from
the set (assembled that way; not re-derived here — the reviewer can recompute from the files).

1. **Stage-1 draws** s20–s25 (six), exactly the ignition study's command:
   `train.py --data data/p2/train_depth3_f0_a1.jsonl --heldout data/p2/heldout.jsonl --mode abs
   --steps 6000 --bs 128 --cap 6 --seed <s>` → `ckpts/r4/stage1_depth3_f0_a1_s<s>.pt`.
2. **Base rate per draw** (Phase-1 / ignition method): `coverage.py --k 2000 --temperature 0.8
   --limit 300 --seed 0` on the first 300 targets (600,000 samples; per-proof hit counts and
   pattern labels) → `artifacts/r4/cov_depth3_f0_a1_s<s>.s0.jsonl`. Rate = depth-3 hits / 600,000.
   A draw is *zero-rate* if it has 0 depth-3 hits in that sample. Note: the first 300 targets
   of the file have a per-sample solve rate ≈ 3·10⁻³ against 5–8·10⁻² over all 1,000 (EI
   round-1 `target_sample_acc`), so they are a hard subset; this is the same subset the
   ignition study used, kept for comparability.
3. **Frozen control at equal attempts**: `expert_iter.py --no_train --rounds 8 --k 32
   --temperature 0.8 --seed <s>` per draw → `artifacts/r4/frozen_depth3_f0_a1_s<s>` (256
   attempts per target on all 1,000 targets and 500 transfer theorems).
4. **EI, paired**: `expert_iter.py --rounds 8 --k 32 --temperature 0.8 --batch 768` with
   `--seed <s>` (seed = draw seed, as in the ignition study) and a second seed `<s>+100` →
   `artifacts/r4/ei_depth3_f0_a1_s<s>` and `..._s<s>_e2`. 12 arms.
5. **GRPO** (`grpo.py`, new, ≈ 250 lines on the existing `model.py` / `sample.py`):
   - policy = softmax(logits / T), T = 0.8 (the sampling distribution; log-probabilities in
     the gradient are of this tempered policy, as in the sprint's code);
   - groups of G ∈ {8, 32} samples of one prompt; reward 1 iff `nd_verify.verify_text(prompt +
     proof)` accepts (a proof of the prompted sequent), else 0; unterminated samples (400 new
     tokens) get 0;
   - advantage = reward − group mean (no std normalisation); zero-variance groups contribute
     exactly zero gradient;
   - loss = −(1 / (N_samples · 400)) · Σ_samples A_i · Σ_t log π(a_t) — fixed divisor
     N_samples · max_new_tokens; AdamW lr 1e-4 constant, β (0.9, 0.95), weight decay 0,
     grad-norm clip 1.0; **no KL, no PPO clip, one optimizer step per batch, strictly
     on-policy** (each batch is sampled from the current weights);
   - batch = 800 samples per update (100 groups at G = 8, 25 groups at G = 32); 40 updates
     per "round" = 32,000 target samples = 32 per target per round, exactly EI's per-round
     attempts; 8 rounds = 320 updates = 256,000 samples = EI's total budget. Prompts cycle
     through a per-round shuffle of the 1,000 targets (G = 32: each target once per round;
     G = 8: four times per round);
   - **per update** (`artifacts/r4/<arm>/updates.jsonl`): number of groups, groups with
     reward variance, all-zero groups, all-one groups, verified-sample rate, samples and
     groups containing a depth-3 proof (model's proof, `patterns.classify` on the pruned,
     start-index-normalised proof), mean response length, loss, grad norm, seconds;
   - **per round** (EI-format `round_<r>.json`, `found_<r>.jsonl`, checkpoint `_r<r>.pt`):
     cumulative distinct verified target proofs from the *training* samples with the round of
     first appearance (so `phase2_metrics.arm_metrics(arm, 'depth3')` — the same code as
     every earlier arm — gives pattern acquisition, normalised); transfer pass@32 (16,000
     evaluation-only samples, as EI does), transfer greedy, held-out greedy;
   - arms: per draw, G = 8 and G = 32, two GRPO seeds each (sampling/shuffle seed = draw seed
     and draw seed + 100): `artifacts/r4/grpo_g{8,32}_depth3_f0_a1_s<s>[_e2]`. 24 arms.
   - **exploratory lr check, pre-declared**: on draw s20 only, G = 8 and G = 32 at lr 3·10⁻⁵
     and 3·10⁻⁴ (4 arms, `_lr3e-5` / `_lr3e-4`). Reported separately; the primary comparison
     is at lr 1e-4 regardless of what these show.
6. **Base reachability** of every depth-3 proof any GRPO arm finds: `novelty.py` under the
   draw's own Stage-1 model (T = 0.8, start-index marginalised) → `artifacts/r4/novelty_<arm>_
   proofs.jsonl`; and the draw's coverage file (step 2) for the pass@2,000 view.

Ignition = first round with ≥ 20 target theorems (2 %) solved by a depth-3 proof
(cumulative, normalised, model's proof classified) — the ignition study's definition.
Acquisition = fraction of the 1,000 targets solved with ≥ 1 depth-3 proof by round 8.

Pods: RTX 3090 (≈ $0.50/h), 3–4 pods named `r4-*`, 3 jobs per pod; A40/A100 only if no
3090 is in stock (written down if so).

## Expected results (numeric; each can fail)

- **E1 (draws).** Of 6 new `a1` draws, 2–4 are zero-rate (0 depth-3 hits in 600,000) — the
  prior is 5 zero-rate of 10 `a1` draws and 6 of 16 f = 0 draws.
- **E2 (EI, paired).** EI ignites by round 8 in 4 or 5 of the 6 draws (prior 7/10 on `a1`);
  igniting arms reach acquisition 0.30–0.37 at round 8; non-igniting arms ≤ 0.01. The two
  EI seeds of a draw agree on ignition (both or neither) in ≥ 5 of 6 draws.
- **E3 (GRPO G = 8 at lr 1e-4).** At update 1 the fraction of groups with reward variance is
  0.04–0.12 (targets the base solves within 8 attempts) and the fraction of groups containing
  a depth-3 proof is 0 on zero-rate draws and < 0.005 on the others. **Prediction: no
  zero-rate draw ignites** (0 of them reach 20 depth-3 theorems by round 8; acquisition
  ≤ 0.01). On draws with a base rate ≥ 2.5·10⁻⁴, G = 8 ignites in at most half of the arms,
  and where it does, ≥ 2 rounds later than the paired EI arm.
- **E4 (GRPO G = 32).** Ignites on the non-zero-rate draws that EI ignites, later than EI
  (ignition round ≥ EI's + 1); at most 1 of the zero-rate draws ignites with either seed;
  round-8 acquisition of igniting G = 32 arms 0.10–0.30, below EI's.
- **E5 (variance fraction).** In arms that ignite, the fraction of groups with reward
  variance rises above 0.30 by the ignition round; in arms that never ignite it stays below
  0.15 for all 320 updates. G = 32 has a higher variance fraction than G = 8 at every update
  on every draw (it is monotone in G for fixed per-sample rates).
- **E6 (plain solve rate).** Cumulative targets solved at least once by round 8: GRPO
  reaches 50–85 % of the paired EI arm's count (EI prior: 580–700 of 1,000); G = 32 ≥ G = 8
  in ≥ 5 of 6 draws.
- **E7 (in-distribution).** Held-out greedy stays within 0.05 of the draw's Stage-1 value
  (0.86–0.89 at EI round 1 on prior draws) for every lr 1e-4 GRPO arm at round 8; a fall
  below 0.80 is reported as collapse. The lr 3e-4 arms are the ones most likely to collapse.
- **E8 (reachability).** Depth-3 proofs that GRPO finds on zero-rate draws have base
  log-probability (T = 0.8, marginalised over start index) below log(1/256) for ≥ 80 % of
  distinct proofs — the same "unreachable by sampling, reached by training" picture as EI.
- **E9 (mechanism, the answer to the question).** If E3/E4 hold, the answer is that crossing
  zero coverage at this budget is EI's supervised step on non-pattern successes, not RL
  against a verifier in general. If instead G = 8 or G = 32 ignites on ≥ 2 zero-rate draws,
  the answer is that on-policy policy gradient also drifts the prior on depth ≤ 2 proofs and
  the sprint's null result had another cause (its codec, model or lr) — reported as such.

## Budget and stop rule

- Pods: ≤ $50 (expected ≈ $15–25: 6 Stage-1 ≈ 1.2 GPU-h, 6 coverage ≈ 4.5, 6 frozen ≈ 3,
  12 EI ≈ 9, 28 GRPO ≈ 21, novelty < 1, on 3090s with co-tenant slowdown). If projected
  spend exceeds $50, drop in this order: the lr check, the second EI seed, draws s25, s24.
- Hard stop 2026-09-19 04:50 UTC (30 h from the session start at 22:50). Everything pulled
  and every `r4-*` pod deleted before `RUN4 DONE`. The account-wide `killswitch` cron
  (Sep 19 06:00 UTC) is the backstop.
- No arm is stopped early on its result. An arm whose held-out greedy falls below 0.5 is
  left to finish and reported as collapsed.
- Counts: every number in `numbers.md` names its file; acquisition via
  `phase2_metrics.arm_metrics` (normalised, min-round rule) on the pulled `found_<r>.jsonl`.

## Amendment 1 — 2026-09-17 23:10 UTC (before any Stage-1 draw finished; no arm has started)

The smoke test of `grpo.py` on the take-home `stage1_abs.pt` (transfer pool as targets, batch 512, G = 8,
lr 1e-4, 6 updates) moved the policy fast: held-out greedy 0.964 → 0.818, 26 depth-3 targets in 6 updates.
With Adam the fixed loss divisor scales the gradient but not the step, so every update with at least one
variance group moves each weight by ≈ lr. To keep "lr was wrong" from being the explanation of either
outcome, the primary GRPO design becomes **two learning rates on every draw and both seeds: lr 1e-4
(arm names as before) and lr 3e-5 (`_lr3e-5` suffix)**; the exploratory check on s20 becomes lr 1e-5 and
3e-4. Expectations E3–E6, E8 apply to each lr separately; E7 (held-out within 0.05 of Stage-1) is
expected to hold at 3e-5 and is at risk at 1e-4. One pod per draw (six `r4-*` 3090 pods). Expected pod
spend rises to ≈ $25–30; the drop order under the $50 cap is unchanged (lr check first, then second
seeds, then draws s25, s24).

## Amendment 2 — 2026-09-17 23:21 UTC (commit d0d5ed0) (after round 1 of the first arms, before any coverage / base-rate file exists)

Round 1 of the s20 arms (40 updates, 32,000 samples) already shows 365 / 327 / 240 depth-3 target
theorems (G = 8 lr 1e-4 / G = 8 lr 3e-5 / G = 32 lr 1e-4; `found_1.jsonl` re-verified with `run4_check.py`:
0 failures). E3/E4 are on course to fail in the direction "GRPO ignites faster than EI". Two additions,
declared now so they are not chosen on the base-rate results:

1. **Zero-rate draws.** The question is about ignition from a *zero* base rate. If fewer than 2 of the 6
   draws s20–s25 are zero-rate (0 depth-3 hits in the 600,000-sample coverage file), train 6 more draws
   (s26–s31, same command), screen each with the same coverage job, and run the primary GRPO arms
   (G = 8 and 32, lr 1e-4 and 3e-5, one seed) plus paired EI on every zero-rate draw found (≤ $6 for the
   screen, ≈ $2 per zero-rate draw). Expectation: GRPO ignites on zero-rate draws too, with the first
   depth-3 sample appearing after the policy has moved on depth ≤ 2 successes (first pattern sample at
   update ≥ 5 rather than ≤ 2), and EI ignites on a subset of them as before (ignition study: 3 of 5).
2. **Sprint-sized budget.** The sprint's GRPO ran 100 steps × 4 prompts × 8 samples = 3,200 samples. One
   exploratory arm per draw with exactly that shape (`--batch 32 --group 8 --updates_per_round 100
   --rounds 1`) at lr 1e-4 and at the sprint's lr 1e-5 (`grpo_sprint_<tag>_lr<lr>`; 12 arms, ≈ 3 min each).
   Expectation: at lr 1e-4, ≥ 1 depth-3 theorem in 5 of 6 draws but < 20 (no ignition by the 2 % rule)
   because 100 updates of 4 groups carry ≈ 30 signal-bearing updates; at lr 1e-5, 0 depth-3 theorems in
   ≥ 5 of 6 draws — the sprint's null reproduced by budget and lr alone.

## Amendment 3 — 2026-09-17 23:30 UTC (exploratory mechanism ablations, declared before their arms start)

GRPO ignites within round 1 on the first draws, and even the sprint-sized budget (3,200 samples) gave 60
depth-3 targets on s20 at lr 1e-4. To say *why* GRPO is faster than EI at equal samples, two cheap
ablations on draws s20 and s21 (one seed each, ≈ $0.40 per arm):
- `ei_<tag>_noretain`: `expert_iter.py --retain 0` — EI without the 20,000 retained Stage-1 records in each
  fine-tuning mix (everything else identical). Expectation: ignites in round 1–2 and reaches acquisition
  ≥ 0.30 by round 4, i.e. the retained cap-6 slice is what slows EI; held-out greedy falls below 0.85.
- `grpo_g8_<tag>_posonly`: `grpo.py --pos_only` — advantage = reward (verified samples weight 1, failures
  0; no group baseline, so it is on-policy positive-only REINFORCE, the closest policy-gradient analogue of
  EI's keep-any-success rule). Expectation: acquisition curve within 0.05 of the G = 8 lr 1e-4 arm at every
  round (the negative half of the group baseline is not what makes GRPO fast).
