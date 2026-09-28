# Pre-registration — run `state-frontier` (executor, 2026-09-28)

Written before the first pod. Brief: settle `state-env`'s length question, and test the depth-3 "lottery" finding.
Budget **$12 / 24 pod-hours** (`podbudget state-frontier --set 24 12`). Lean alone decides (`lean_judge`: strict
`lean_seq` grammar + Lean 4 core); `nd_verify` judges nothing. `LEAN_GATE_DUMP` is set for every job (literal sampled
text + verdict, one file per job). `L_true` labels are ND-derived upper bounds under Lean.

## Models (all 4 layers, d 256, 8 heads, from scratch, Stage-1 on `data/p2/train_depth3_f0_a1.jsonl`, 155,000 records, cap 6, depth-3 f = 0)

| label | checkpoints | params | format | source |
|---|---|---|---|---|
| S base / T1 | `state-env/ckpts/se/stage1_S_s{0,1}.pt`, `…/ladder/la_T1_S_s{0,1}_r8.pt` | 3,216,384 | `lean_state` (state in, one `lean_seq` step out) | state-env |
| SN base / T1 | `stage1_SN_s{0,1}.pt`, `la_T1_SN_s{0,1}_r8.pt` | 3,216,384 | `lean_staten`, sampled with `Env(assign=True)` (SN-v2) | state-env |
| C0 base / T1 | `lean-format/ckpts/lf/stage1_a1_seq_s{0,1}.pt`, `ds-generator/ckpts/ladder/la_T1_c0_s{0,1}_r8.pt` | 3,214,336 | `lean_seq` whole proof | lean-format / ds-generator |
| G1 T1 (secondary whole-proof reference, **different training set** `train_g1`) | `ds-generator/ckpts/ladder/la_T1_g1_s{0,1}_r8.pt` | 3,214,336 | `lean_seq` | ds-generator |
| **new** S s2, s3 | Stage-1 + T1 r8 (this run, `ckpts/sf2/`) | 3,216,384 | `lean_state` | this run |
| **new** SN s2–s5 | Stage-1 (this run) | 3,216,384 | `lean_staten` | this run |

New models use the unchanged `state-env` commands (`state_train.py` 6,000 steps × 128 proofs; `state_ladder_ei.py`
8 rounds × k 32, T 0.8, batch 2,048, `--max_action` 256, `--max_steps` 48), so they are comparable to the on-file seeds.

## Design

**A. Re-sample (question 1).** Pool `data/sf2/long.jsonl` = the 224 transfer theorems with `L_true` ≥ 11
(99 at 11, 102 at 12, 13 at 13, 10 at 14; never trained on). Every model above at **k = 256, T 0.8, sampling seed 0**:
state models in the environment (`state_eval.py`, batch 2,048, `--max_action` 256, `--max_steps` 48, as `state-env`);
whole-proof models with `eval_set.py` (batch 2,048, `max_new` 512 as in their ladders; the fraction of samples that
hit `max_new` is recorded; > 0.1 % in a reported stratum → re-run that model at 1,024). Output: per-theorem success
counts `n_ok / 256`, paired across models by theorem. The state and whole-proof samplers necessarily differ; flags are
held fixed within each family.

**B. More seeds.** S s2, s3: Stage-1 → held-out greedy (in the environment) → T1 → frozen (question 1 at n = 4 for S's
ladder readouts). SN s2–s5: Stage-1 → held-out greedy → frozen ladder (a state-model base-reachability floor at
n = 6 for SN frozen). All new Stage-1 bases and new T1 finals join design A.

**C. Lottery (question 2).** Depth-3 slice (`pat.depth3`, 500 theorems) of held-out greedy for each new Stage-1 seed
(S s2, s3, SN s2–s5: **6 new state-conditioned seeds**), read as high mode iff rate > 0.44, against the control
configuration's P(high) = 0.462, Wilson [0.333, 0.595] (`NOISE_FLOOR.md`, 52 cells).

## Question 1 — does the state reach `L_true` ≥ 13 at a real rate, or was it one lucky theorem?

Headline quantity: **N13** = number of the 23 `L_true` ≥ 13 theorems with ≥ 1 Lean-accepted proof at k = 256, per
final T1 checkpoint; plus the pooled per-theorem success rate at ≥ 13.

Expected (numbers I would bet on):
- State T1 finals (S s0–s3, SN s0/s1): N13 **2–6 each** (median 3); `la_transfer_1126` solved by all 6; pooled
  success rate at ≥ 13 **0.1–1 %** of attempts.
- C0 T1 finals: N13 **0–1** each. G1 T1: 0–2.
- Stage-1 bases: S / SN **0–2**, C0 **0**.
- At `L_true` 11–12 (201): state T1 finals 40–100 solved each; C0 T1 15–45; state bases 10–40; C0 bases 0–10.
- New S T1 ladders (s2, s3): cumulative transfer `L*` 12 (11–13), T1 solved 1,250–1,500, frozen 700–850;
  held-out greedy overall 0.80–0.97.

Readings (fixed now):
- **"One lucky theorem"** is supported if `la_transfer_1126` carries ≥ 80 % of all state-T1 successes at ≥ 13
  **and** no other ≥ 13 theorem is solved by ≥ 2 of the 6 state T1 finals.
- **"A real, low rate"** is supported if ≥ 3 distinct ≥ 13 theorems are each solved by ≥ 2 of the 6 state T1 finals.
- In between: "narrow" — reported as such.
- **State vs whole-proof at ≥ 13**: paired per theorem (state T1 pooled vs C0 T1 pooled success counts; sign test over
  the theorems either family solves).

Minimum detectable difference. No noise floor exists for N13. Using the `state-env` ladder's own spread of the
closest quantity (cumulative ≥ 13 theorems per T1 run: 1, 2, 3, 1; sd 0.96) as a stand-in, a two-sample t-test at
80 % power has MDD ≈ **3.1 theorems** for S (n = 4) vs C0 (n = 2) and ≈ **5.1** for SN (n = 2) vs C0 (n = 2). My
predicted S − C0 difference (≈ 2.5) is **inside** that MDD, so the seed-level comparison is not the test: the
decision rules above are per-theorem and pooled over seeds (a paired, within-theorem design limited by sampling
noise at k = 256), and the seed-level N13 values are reported per seed as descriptive. A 23-theorem stratum cannot
give a tight rate; this run can tell "one theorem" from "several", not measure the rate precisely.

## Question 2 — does the state remove the depth-3 lottery?

Expected: **all 6 new seeds in the high mode** (depth-3 rate 0.85–0.97). Pooled with `state-env`'s 6: 12 / 12,
Wilson [0.757, 1.00], disjoint from the control's [0.333, 0.595].

- **Falsifier:** "the state removes the lottery" is **dead if ≥ 2 of the 6 new seeds land in the low mode** (≤ 0.44).
  Under the control's rate, P(≥ 5 of 6 high) = 0.078 and P(6 of 6) = 0.0097; so 6 / 6 new is a replication at
  p ≈ 0.01 on fresh seeds alone, 5 / 6 is "reduced, not removed".
- MDD: the quantity is a proportion of seeds; at 12 state seeds, P(high) = 1.0 vs 0.462 is detectable (Wilson
  intervals disjoint at 12 / 12 and 11 / 12; not at 10 / 12). A shift smaller than ≈ 0.45 in P(high) is not detectable.
- Secondary: the spread of the depth-3 rate among state seeds (predicted sd < 0.05) and of held-out overall
  excluding S's `unbound`-name failures.

## Base-reachability floor (reviewer's step 2)

SN frozen transfer solved at n = 6 (on file 975 / 801). Expected: all 6 in 650–1,050, IQM ≈ 850, sd ≤ 130; every
cell above C0's on-file frozen range (114–158, and `NOISE_FLOOR.md`'s null range 62–265). S frozen at n = 4: 700–850.

## Pods, budget, stop rule

RTX 3090 (≈ $0.50/h), 3–4 pods, one sampling job per card. Estimate ≈ 19 pod-hours: S s2/s3 chains ≈ 4.3 h each,
SN Stage-1 ×4 ≈ 1 h, SN frozen ×4 ≈ 7.2 h, re-sampling 22 models ≈ 2 h. **Stop rule:** if spend reaches 20 h / $10,
drop the remaining SN frozen ladders (lowest priority), then S frozen s3; the re-sample and the lottery seeds are
never dropped. Balance floor $100 (now $253). If the S s2/s3 T1 ladders cannot finish inside budget, question 1 is
answered from the re-sample alone and the n = 4 ladder readout is reported as not run.
