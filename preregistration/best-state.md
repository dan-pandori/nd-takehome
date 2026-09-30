---
written_on: 2026-09-30
written_by: agent:claude (executor, run best-state)
---

# Pre-registration: best-state — Robbie's network and pretraining recipe in the proof-state format, cap 6 and cap 12

Brief: run brief `best-state` (Dan, 2026-09-30); proposal nd-rl `docs/proposals/2026-09-30-best-network-proof-state.md`.
Policy: `AGENT_POLICY.md`. **Lean alone decides** everything counted here (`lean_judge`, via the state environment's
gate). Written before any pod of this run.

## Question

With the proof-state interface (`lean_staten`, environment-assigned names, SN-v2) and our state RL (the T1 ladder) held
fixed, does Robbie's network and pretraining recipe beat our 3.2M recipe at cap 6 and at cap 12? Does the cap-12
advantage survive, grow or shrink on the better network?

## Design (2 × 2; two cells inherited)

| cell | Stage-1 data | recipe | seeds |
|---|---|---|---|
| **best-cap6** (new) | cap-6 control set `data/p2/train_depth3_f0_a1.jsonl` (155,000; md5 29276f24…) | best | 0, 1, 2 |
| **best-cap12** (new) | K12 `data/kh/train_k12.jsonl` (155,000; md5 800b5486…) | best | 0, 1, 2 |
| SN-v2 cap-6 (inherited, `state-env`) | the cap-6 control set | ours: 4 × 256 RoPE, AdamW, 6,000 steps × 128 proofs | 0, 1 |
| SN-cap12 (inherited, `state-cap12`) | K12 | ours | 0, 1, 2, 3 |

**The best recipe (port of Robbie's `pretrain_best.py`, factorial_20260929 — his code, credited):** 6 × 384, 8 heads,
MLP 1280, Peri-LN, 4 ALiBi + 4 NoPE heads; Muon (Polar Express, lr 0.01, momentum 0.95) on block matrices, head and MTP
matrices, AdamW (1e-3, wd 0.1) on the rest; MTP at weight 0.3 (training only); token-budget batches of 128 × 144 padded
tokens; warmup 200, cosine to 0.3 × lr over a wall-clock budget. State trainer's data path and loss mask (action tokens
only), one name offset per pair, checkpoint format of `model.save_ckpt` (with `cfg.arch = 'best'`). Deviations from his
loop: the unit is a (state, action) pair, not a proof; the clock starts after the pairs are on the GPU; val loss is on
the state trainer's held-out pairs (`data/p2/heldout.jsonl`, first 2,000 records), not a slice of the training set.
~10.3M parameters vs 3.2M. All Stage-1 runs on one GPU class (A40) so a wall-clock budget means the same thing.

**Stage-1 budget rule (stated before the pilot).** Pilot seed 0 at cap 6 with budgets 300 s and 1,200 s. Measure
held-out greedy (`state_eval.py`, `data/p2/heldout.jsonl`, 5,000, k 1, T 0) and final val loss. Choose 1,200 s if its
held-out greedy is ≥ 1.0 pp above 300 s's, or within ±1.0 pp with val loss ≥ 1 % lower; otherwise 300 s. The chosen
budget is used for all six new models; the pilot model at that budget is seed 0 of best-cap6. Never chosen on
textbook72, the transfer pool or the long pools.

**T1:** exactly `state-cap12`'s protocol: `state_ladder_ei.py`, 8 rounds, k 32, T 0.8, `rl_targets.jsonl`, replay from the
cell's own Stage-1 data, `--heldout data/p2/heldout.jsonl`, `max_steps` 48, `max_action` 256, fine-tune AdamW (the
ladder's defaults, unchanged, applied to the bigger network). One pod per ladder, six in parallel.
Sampling batch: the largest that fits, measured on the pilot (peak `max_memory_allocated` reported). A batch change is a
sampling re-draw only (`NOISE_FLOOR.md`; per-row seeding), not a protocol change.

## Read-outs (every model: new frozen + T1; inherited where not already on file)

1. **textbook72** (`data/eval_only/textbook72`, 72 = dev58 + train14): `state_eval.py`, k 256, T 0.8, seed 0,
   `max_action` 512, `max_steps` 96, `--lenfield reference_lines` — the `textbook72` run's settings. Inherited values
   are that run's (reviewed files on `dan_textbook72`), not re-read.
2. **Robbie's dev metric:** dev half of `data/ladder/transfer.jsonl` by his `dev_split` (sha1(key) even; 1,108, md5 of
   transfer identical to his fork commit 51604b3), 64 samples, T 0.8, solved at L_true ≥ 7 (all 1,108 are ≥ 7), read in
   the state environment (`state_eval.py`, `max_action` 512, `max_steps` 96). Read here for all 12 inherited checkpoints
   and the 12 new ones. **holdout250** (his `passk.py`: holdout half sorted by sha1("passk:"+key), first 250), k 256.
3. **Long pools:** `transfer_long_rr600.jsonl` (headline Q = rr600 generator theorems at L_true 13–16, /380, as in
   `state-cap12`) and `transfer_long2.jsonl` (21), `lpool_reread.py`, k 256, T 0.8, seed 0, `max_action` 512, `max_steps` 96.
   Inherited SN-cap12 values from `state-cap12` / `long-pool-2`; SN-v2 cap-6 on `transfer_long2` read here.
4. **Held-out greedy** (p2 held-out, 5,000).
5. **Compute** per arm (and per round for T1): GPU-seconds + GPU type, generated tokens, training steps and tokens, Lean
   checks, as registry rows and a table. **Recipe against recipe, not compute-matched**: the bigger network costs more
   per sample and per step; the write-up flags every > 1.25× difference.

`L_true` labels are ND-derived upper bounds under Lean. Proof length reported in lines and term size.

## Noise floor and MDD

`NOISE_FLOOR.md` has no textbook72 or dev-metric row, so pooled per-seed SDs are taken from existing cells:
textbook72 sd 2.44 (the four `textbook72` cells), dev metric sd 23.1 (Robbie's eight factorial cells, 3 seeds each).
Two-sample t, 80 % power, α 0.05: **textbook72 MDD ≈ 9.3 at cap 6 (3 vs 2), ≈ 6.5 at cap 12 (3 vs 4); dev metric MDD
≈ 88 at cap 6, ≈ 61 at cap 12.** A 3-vs-2 permutation test cannot go below p = 0.2, so significance rests on the
parametric MDD. The new cells' SD is unknown; if it is larger than the pooled one, the MDD grows and I say so.

## Expected results (numbers are 3-seed IQM, which at n = 3 is the mean (`tb72_analysis.iqm`))

| cell | textbook72 frozen | textbook72 T1 | dev metric frozen | dev metric T1 | held-out greedy |
|---|---|---|---|---|---|
| ours cap 6 (inherited; dev read here) | 15 | 19 | ≈ 380 (my guess) | ≈ 700 (guess) | ≈ 0.95 |
| **best-cap6** | **19 (12–26)** | **24 (16–32)** | **480 (350–650)** | **780 (650–900)** | ≥ 0.94 |
| ours cap 12 (inherited; dev read here) | 27.5 | 37.5 | ≈ 780 (guess) | ≈ 930 (guess) | 0.97 |
| **best-cap12** | **30 (24–36)** | **39 (34–44)** | **830 (720–920)** | **950 (900–1,000)** | ≥ 0.96 |

Sign of (best − ours): **positive at cap 6** (frozen and T1, textbook72 and dev metric); **positive at cap 12 frozen,
≈ 0 to positive at cap 12 T1** (inside the MDD). Q (rr600 13–16): best-cap12 T1 ≥ ours (306 IQM) − 20. The cap-12
advantage (cap12 − cap6, textbook72 T1) **shrinks** on the best network: ≈ 15 vs 18.5 for ours.

**Falsifiers.**
- "Robbie's recipe helps in the state format" is **refuted** if best − ours ≤ 0 on textbook72 IQM and on the dev metric
  mean at both caps, frozen and T1 (8 comparisons, none positive); and **reversed** if best − ours ≤ −MDD on either
  headline at either cap.
- It is **supported** if best − ours ≥ MDD on textbook72 or the dev metric at either cap (frozen or T1), with no
  comparison ≤ −MDD. Anything else is "not resolved at this seed count".
- "The cap-12 advantage shrinks": (best cap12 − best cap6) < (ours cap12 − ours cap6) on textbook72 T1. Reported as an
  observation: the interaction's MDD (≈ 12) is larger than the predicted difference.

## Budget and stop rule

$55 / 110 pod-hours (registered with `podbudget`), RunPod balance floor $100 (balance $159 at start). A40 ($0.49/h).
Plan: pilot 2 pods × ≈ 1 h; 6 ladder pods × ≈ 10–14 h (the 3.2M ladders took ≈ 6–7 h; the network is 3× larger);
read-out pods ≈ 12 h total. **Stop rules:** if the six ladders' projected total passes 24 h wall-clock or the run's
projection passes 100 pod-h / $50, cut the ladders to 6 rounds (read at round 6) and write it in `QUESTIONS.md`. Never
take the balance below $100. Delete each pod when its outputs and checkpoints are pulled/uploaded.
