# Pre-registration: grpo-state — GRPO in the proof-state environment, with support-expanding advantages

Run id `grpo-state`. Written 2026-09-30 by the executor of the **code phase**, before any pod. The code phase builds
and tests `grpo_state.py` and runs one ≤ 30-min GPU smoke; it measures nothing below. **The experiment in this file
is not run in this session.** It waits for Dan's RunPod top-up and is queued as a separate run, which should commit
an addendum with anything it changes before its first pod. The costing (§ 9) is filled in from the GPU smoke as an
addendum; everything above § 9 is fixed now.

Judge: **Lean alone decides** (the fork's `dan` judge `lean_judge.py`: strict `lean_seq` grammar + Lean on the
literal assembled text). No `nd_verify` anywhere. Proof lengths are reported in lines and term size; the pools'
`L_true` labels are ND-derived upper bounds.

## 1. Question

The strongest "beyond the base" evidence in the project is run 4's: GRPO acquired the depth-3 pattern from zero-rate
draws in 40 / 40 surviving arms against EI's 6 / 8. That was the token format, cap 6, under Lean ∧ `nd_verify`, and
its checkpoints are lost (`run4-grpo-review`). The strongest models are now proof-state policies, and step-level
credit is the natural home for policy gradient. Two questions:

- **Q1 (frontier and support).** Does GRPO in the state environment move the frontier, or the support, differently
  from EI at equal target attempts?
- **Q2 (support-expanding advantages).** Do advantages that credit *rare* correct proofs (unlikeliness rank penalty,
  pass@k advantage) expand support relative to the default group-mean advantage, rather than sharpen?

## 2. Models

Every number in the experiment is measured on descendants of **SN-cap12 Stage-1**: `lean_staten` (proof-state
input, environment-assigned names), 4 layers, d 256, 8 heads, **3,216,384 parameters**, from scratch, trained on
`data/kh/train_k12.jsonl` (155,000 generator proofs, flat lengths 2–12; bucket `cap-horizon/data/kh/`) with
`state_train.py --mode lean_staten --steps 6000 --recs 128 --cap 12` (run `state-cap12`, `pod/sc12/sn_seed.sh`).
- Seeds s0–s3 exist: `hf://buckets/dan-pandori/nd-rl/state-cap12/ckpts/sc12/stage1_SN12_s{0..3}.pt`.
- **s4 and s5 do not exist** and are trained by the experiment with the same command (`--seed 4`, `--seed 5`).
  The brief asks for 6 seeds; this is the only way to get them.

## 3. Arms (all from the same Stage-1 checkpoint per seed; same seeds in every arm)

| arm | driver | what differs |
|---|---|---|
| **EI** | `state_ladder_ei.py` T1 (state-cap12's command) | s0–s3: **inherited** `la_T1_SN12_s{0..3}` (bucket `state-cap12/ckpts/sc12/ladder/`, same settings as below, Lean alone). s4, s5: run here. |
| **GRPO-default** | `grpo_state.py --adv default` | A = R − mean(R) over the group |
| **GRPO-unlikely** | `--adv unlikely --beta_rank 0.25` | He et al. 2506.02355v2 §4.1: correct rollouts ranked by sequence log-prob; the most likely keeps 1 − β, the least likely 1 − β/G |
| **GRPO-pass@k** | `--adv passk --passk_k 4` | Chen et al. 2508.10751v1 §2.4 analytic pass@4 advantage (PKPO-equivalent up to a per-group baseline and scale) |

The distinct-proof bonus (`--adv distinct`) is built and tested but is **not an arm** (the brief's four arms); it
is the first addition if the budget allows, with the same seeds.

Shared settings, all arms: targets `data/ladder/rl_targets.jsonl` (4,495), transfer `data/ladder/transfer.jsonl`
(2,285), held-out `data/p2/heldout.jsonl`; 8 rounds (round-equivalents for GRPO), k 32; temperature 0.8;
`max_action` 256, `max_steps` 48; decode batch 2,048 (state-cap12's; peak 13.4 GB allocated / 17.5 GB reserved in
its round 8); fast decode path (`ND_SAMPLE_PATH=fast`). EI finetune: state-cap12's defaults (600 steps × 128 proofs,
lr 3e-4, retain 20,000, max_per_thm 4, rl_weight 4).

GRPO settings, fixed now: G = 8, 256 theorems per update (2,048 rollouts per update, one decode batch), so
8 × 32 × 4,495 / 2,048 = **561 updates**; AdamW lr **3e-5** (run 4's lr that kept held-out greedy at 0.75–0.87;
1e-4 dropped it to 0.58–0.72), β (0.9, 0.95), no weight decay, grad-norm clip 1.0; fixed loss divisor
P · G · 400; **no KL** (run 4's setting; `--kl` exists); no std normalisation (`--adv_std` off: all variants share
the default's scale). One update per sampled batch, on-policy.

## 4. What the arms are matched on (compute)

- **Matched:** target attempts (1,150,720 per ladder), transfer attempts at each round / boundary (2,285 × 32),
  greedy evaluations, temperature, action and step caps, decode batch.
- **Not matched, recorded:** generated tokens and actions (they follow the policy), training steps (EI 4,800 steps of
  128 proofs; GRPO 561 updates of up to 2,048 rollouts), training tokens, Lean checks, GPU-seconds. The drivers write
  `gpu_seconds`, `gen_tokens`, `attempts`, `actions`, `train_steps`, `train_tokens`, `lean_checks` per (phase, round)
  (`record.phase`). The write-up flags any arm above 1.25× its comparator on any of them.
- Boundary evaluations differ in timing: GRPO's boundary r evaluates the policy after round-equivalent r, the EI
  ladder's round r evaluates the checkpoint it samples from (after r − 1 fine-tunes). The read-outs below are all on
  the final checkpoints (EI `_r8`, GRPO `_r8`) with one script, so this does not enter them.

## 5. Read-outs (all on final checkpoints and the Stage-1 base, same script and settings per seed)

1. **`transfer_long2` + calibration** (91 theorems; `data/ladder/transfer_long2{,_calib}.jsonl`, read together per
   POOLS.md): solves at k 256, T 0.8, seed 0, `max_action` 512, `max_steps` 96 (`lpool_reread.py`, as long-pool-2),
   by stratum (exact 17 / exact 18 / ≥ 18). Inherited reference (SN-cap12, long-pool-2): T1 34 / 59 / 58 / 61,
   frozen 11 / 16 / 21 / 23 for s0–s3.
2. **Long pool Q** (generator theorems at `L_true` 13–16, 380, rr600, k 256; state-cap12's read-out). Inherited: T1
   233 / 295 / 320 / 317, frozen 134 / 212 / 228 / 216.
3. **Support (the `support-curves` protocol, adapted).** Pool: the 471 theorems of 1 + 2. Per seed, the base
   (Stage-1) theorems unsolved at k 256 are deepened to **10,000 attempts at T 0.8 plus 10,000 at T 1.0**, stopping a
   theorem at its first success (`ss_support.py`, stop_at 1). *Base-unreached* = 0 of 20,000 + 256. Headline:
   **the number of base-unreached theorems each arm solves at k 256**, paired per seed (and per theorem for the
   list). This is a smaller deepening than support-curves' 400k (cost); the write-up states the bound it gives
   (a theorem at 0 / 20,256 has base p < 1.5 × 10⁻⁴ at 95 %), and the pairs that survive get 200k per temperature
   if the budget allows.
4. **Held-out greedy** (`data/p2/heldout.jsonl`, 5,000) on every final checkpoint; **distinct proofs per solved
   theorem** on the targets (start-index normalised, `found_8.jsonl`).
5. From the ladders' own files: targets-cumulative and transfer-cumulative solved and `L*` per round.

## 6. Noise floor, seeds and statistics

SN-cap12 has no measured floor; `NOISE_FLOOR.md`'s floor is cap-6 `lean_seq`. I use its formula (MDD = c · sd,
80 % power, α 0.05, c = 1.794 at n = 6) with the **between-seed sd of the four SN-cap12 T1 ladders** (inherited
numbers above), which is conservative for a paired design:

| quantity | SN-cap12 T1 values (s0–s3) | sd | MDD at n = 6 per arm |
|---|---|---|---|
| `transfer_long2` + calib solves (of 91) | 34 / 59 / 58 / 61 | 12.7 | **23** |
| long pool Q (of 380) | 233 / 295 / 320 / 317 | 40.4 | **72** |
| transfer solved (of 2,285) | 1,960 / 2,027 / 2,024 / 1,985 | 32.4 | **58** |
| held-out greedy (Stage-1) | 0.969 / 0.977 / 0.978 / 0.974 | 0.004 | **0.7 pp** |

The support headline (§ 5.3) is a paired ratio per seed; its test is the sign count over 6 seeds (≥ 5 of 6 in one
direction: one-sided sign-test p = 0.109; 6 of 6: p = 0.016) plus the paired exact permutation test on the
differences (sign-flip, 2⁶ = 64 relabellings: minimum two-sided p = 2/64 = 0.031). A difference inside the floor is reported as "no difference
resolved", not as a finding. Report per-seed values, and the IQM with a stratified-bootstrap 95 % interval
(Agarwal et al. 2021). Seeds s0–s5 in every arm; GRPO sampling seed = the Stage-1 seed.

## 7. Expected results (falsifiable, committed before any run)

- **E1 (Q1, frontier).** GRPO-default and EI solve the same number of `transfer_long2` + calib theorems within the
  floor (|Δ| < 23) in the IQM, and GRPO-default's per-seed value is below EI's in ≥ 4 of 6 seeds. *Reason:* the
  target pool is nearly saturated for SN-cap12 (T1 solves 4,171–4,228 of 4,495), so most groups are all-correct
  and carry no gradient; GRPO sharpens what EI also trains on.
- **E2 (Q1, support).** EI solves more base-unreached theorems (§ 5.3) than GRPO-default in ≥ 4 of 6 seeds.
  *Reason:* EI trains on up to 4 distinct found proofs per theorem including rare ones; the default advantage
  concentrates on already-likely proofs (He et al.'s rank bias).
- **E3 (Q2).** GRPO-pass@4 solves ≥ 1.1× GRPO-default's base-unreached theorems in ≥ 4 of 6 seeds;
  GRPO-unlikely is within ± 10 % of GRPO-default in ≥ 4 of 6 seeds (it only acts on mixed groups, and only
  reorders credit among correct rollouts). The literature's expectation (≥ 1.2× in ≥ 5 of 6, lit shortlist #3) is
  stated for comparison; I predict it fails for unlikely and is borderline for pass@k.
- **E4 (cost).** Every GRPO arm's held-out greedy is within 2 pp of EI's on the same seed (lr 3e-5, no KL). If any
  GRPO arm drops > 5 pp below its Stage-1, it is reported as collapsed (see stop rule), which would refute E4.
- **E5 (mechanics).** In GRPO-default the fraction of groups with reward variance is 0.10–0.35 averaged over each
  run, and ≥ 0.5 of groups are all-correct by round-equivalent 4.
- **Falsifiers of the project claim.** If a GRPO arm solves more base-unreached theorems than EI by more than the
  floor in ≥ 5 of 6 seeds, GRPO in the state environment expands support beyond EI's at equal attempts — the
  run-4 finding reproduced on the current model family.

## 8. Stop rule

- Budget: the experiment run registers its own budget with `podbudget grpo-state-exp --set …` from § 9.
- Collapse: a GRPO run whose held-out greedy at boundary 2 is below 0.85 is stopped and reported as collapsed at
  lr 3e-5. It is **not** re-run at another lr inside this pre-registration; an lr change is an addendum.
- Incomplete seeds: if the budget runs out, drop seeds from the top (s5, then s4) for all arms together, never
  arms for some seeds only; the MDD is re-stated for the n that ran.

## 9. Costed pod plan

*Filled in from the code phase's GPU smoke (addendum below).*

## Addendum 1 (2026-09-30 02:45 UTC, after the GPU smoke; § 1–8 unchanged except the support deepening depth, last paragraph)

### What the smoke measured
Model: SN-cap12 Stage-1 s0 (`stage1_SN12_s0.pt`, 3,216,384 params, `lean_staten`, from scratch on `train_k12`).
One RTX 3090 (24 GB, billed $0.50/h, cgroup quota ≈ 31 CPUs), `grpo_state.py` at the pre-registered settings
(256 × G 8, decode batch 2,048, lr 3e-5, no KL), `--no_eval`. Sources: `artifacts/grpo_state/smoke_*/steps.jsonl`,
`artifacts/grpo_state/logs/`, compute rows `artifacts/grpo-state/registry/` (table: `python3 gs_compute.py
artifacts/grpo-state/registry`).

| run | updates | s / update (sampling + Lean, update) | peak alloc | mean reward | groups with variance | groups with A ≠ 0 |
|---|---|---|---|---|---|---|
| default, alone | 8 | 18.6 (16.0, 2.6) | 8.60 GB | 0.465 | 0.565 | 0.565 |
| unlikely, alone | 4 | 19.8 (17.0, 2.8) | 8.05 GB | 0.462 | 0.591 | 0.591 |
| pass@4, alone | 4 | 19.2 (17.5, 1.7) | 8.15 GB | 0.463 | 0.606 | 0.320 |
| distinct, alone | 4 | 20.7 (17.6, 3.1) | 8.09 GB | 0.463 | 0.601 | 0.664 |
| default + pass@4, **two jobs on one card** | 6 each | 26.5 / 26.4 | 8.92 / 8.61 GB | 0.456 / 0.441 | 0.573 / 0.608 | — |

Two jobs per card give 2 × 19.5 / 26.5 ≈ **1.47×** throughput. Per update ≈ 1.1 M training tokens (default),
≈ 0.65 M (pass@4, which zeroes groups where every 4-subset already succeeds).

**Seen after § 7 was committed, stated so the reviewer can weigh it:** the base's per-sample reward on the targets
is ≈ 0.46 and ≈ 0.6 of groups have reward variance at the start, well above E5's pre-registered 0.10–0.35 run
average. E5 stays as written (it is about the run average, and may still come out either way); E1's stated reason
("most groups are all-correct") is contradicted at the start of training. E1–E4 are not changed.

### Costed plan (RTX 3090 at $0.50/h billed; two jobs per card)
| item | count | pod-h (effective) | $ |
|---|---|---|---|
| GRPO ladder: 561 updates × 19.5 s × 1.15 (EI rounds slowed ≈ 25 % over 8 rounds) + 8 boundary evals (80 k rollouts each, ≈ 400 s) ≈ 4.4 h alone, ÷ 1.47 | 18 (3 arms × 6 seeds) | 54 | 27.0 |
| EI T1 ladder s4, s5 (state-cap12: 3.5–3.6 h on a 3090) | 2 | 5 | 2.5 |
| Stage-1 s4, s5 (`state_train`, 6,000 steps; estimate) | 2 | 1.5 | 0.8 |
| read-outs § 5.1, 5.2, 5.4 on 30 final checkpoints (≈ 125 k rollouts each) | 30 | 5 | 2.5 |
| support deepening § 5.3 (base only, stop at first success; ≈ 250 theorems / seed) | 6 | 8.5 | 4.3 |
| **total** (+ 15 % margin) | | **74 (85)** | **37 (43)** |

This is above the brief's ≈ $10–20. Cheaper plans, in the order I would cut:
- **Plan B (≈ $24):** seeds s0–s3 only (EI inherited, no new Stage-1). 12 GRPO ladders (36 pod-h), read-outs on 16
  checkpoints, support on 4 seeds. MDD at n = 4: c = 2.37, so 30 on `transfer_long2` + calib, 96 on Q.
- **Plan C (≈ $16):** Plan B with two GRPO arms (default, pass@4): Q1 plus the stronger half of Q2.
- A 16 GB card (e.g. RTX A4000) holds one job (peak 8.9 GB); if it bills ≈ half a 3090 it cuts every plan by up to
  ≈ 2× at one job per card. Measure s / update on it first.
The support deepening in § 5.3 is **5,000 + 5,000** attempts (was 10,000 + 10,000), to fit the budget: a theorem at
0 / 10,256 has base p < 2.9 × 10⁻⁴ at 95 %. Question and default in `QUESTIONS.md` (2026-09-30).
