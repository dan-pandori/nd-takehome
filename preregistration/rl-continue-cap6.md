# Pre-registration — rl-continue-cap6: the cap-6 ladders, rounds 9–16 on the same targets

Run id `rl-continue-cap6`, executor, branch `dan_rl-continue-cap6` (from the fork's `origin/dan`). Written 2026-10-03
≈ 17:55 UTC, before the first pod. Authorised by Dan 2026-10-03 as the cap-6 companion to `rl-continue` (same protocol
on cap 12). Brief: `nd-rl/docs/proposals/state-env/BRIEF_rl-continue-cap6.md` (+ `BRIEF_rl-continue.md`).

## Question

Does cap-6 RL converge towards cap 12's ceiling, or stop below it? `trajectory-cap6`'s three T1 ladders still add
targets in r6–r8 (+53/+20/+16, +46/+32/+25, +52/+43/+31 for s0/s1/s2) and stand at 4,257 / 4,235 / 4,204 of 4,495
`rl_targets` (94.7 / 94.2 / 93.5 %) and 2,071 / 2,055 / 2,031 of 2,285 transfer (90.6 / 89.9 / 88.9 %). Cap 12's r8
(`trajectory`, Lean alone): 4,383 / 4,365 / 4,407 targets (97.1–98.0 %), 2,185 / 2,170 / 2,190 transfer (95.0–95.8 %).

## Models (every number below is on one of these)

`trajectory-cap6`'s T1 ladders, seeds 0–2: ALiBiGPT 6 × 384, 9,560,832 params (`best-state`'s recipe), `lean_staten`,
from scratch on the cap-6 set (`data/p2/train_depth3_f0_a1.jsonl`, 155,000 records, cap 6), Stage-1 1,200 s on an A40,
then 8 EI rounds (`state_ladder_ei.py`, k 32, T 0.8, max_new 512, max_action 256, max_steps 48, 600 fine-tune steps at
lr 3e-4, 128 proofs/step, replay 20,000 cap-6 records, ≤ 4 proofs/target × weight 4, ladder batch 2,048 on every seed).
r8 checkpoints: `hf://buckets/dan-pandori/nd-rl/trajectory-cap6/ckpts/tj6/ladder/la_T1_best6_s{0,1,2}_r8.pt`
(s0 md5 586baf0b…, from `trajectory-cap6`'s ladder log). Lean alone decides (state-env Lean gate).

## Design (what I will run)

- One A40 pod per seed (`rc6-s0..2`; RTX A6000 if A40 stock is out). `pod/rc6/setup.sh` places `trajectory-cap6`'s
  `found_8.jsonl`, `found_transfer_8.jsonl`, `alloc_8.json`, `round_8.json` and the r8 checkpoint at the resume paths;
  `pod/rc6/run.sh` runs `state_ladder_ei.py --resume --start_round 9 --rounds 8` with `trajectory-cap6`'s flags
  (`args.json`), name `la_T1_best6_s<S>`, outdir `artifacts/rc6`. An OOM resumes from the last finished round at
  batch 1,024 (a sampling re-draw, logged). The resume re-creates the replay RNG (`random.Random(seed*7919)`) at r9;
  per-round sampling seeds (`seed*1000 + r`) and fine-tune seeds are as in a continuous run.
- **Seamlessness checks:** (1) the checkpoint md5 r9 samples from equals `trajectory-cap6`'s r8 md5; (2) the
  `resumed round 8: N target proofs` line equals `found_8.jsonl`'s line count; (3) `targets_cum` / `transfer_cum` at
  r9 ≥ r8 and every r8-solved target is still in the found set.
- **Read-outs (core):** r16, every seed, textbook72 + holdout250 at k 256, sample seed 1 (`trajectory-cap6`'s pass@k
  seed), `trajectory-cap6`'s `pod/tj6/read.sh` settings (T 0.8, max_action 512, max_steps 96, batch 2,048, one retry at
  1,024 on OOM). Group C = `trajectory-cap6`'s per-seed C (seed-0 samples: unsolved at `pend` and at r8; 52 / 52 / 60,
  recomputed here from its eval rows with its `tj6_analysis.groups` rule). Its r8 seed-1 reads are the baseline.
- **Deviation from `rl-continue` (budget):** `trajectory-cap6`'s r8 rounds took 2,789–2,978 s on an A40, so the 24
  rounds are ≈ 21–23 of the 24 pod-hours. The r12 reads, the seed-0 r16 reads and rr600 13–16 / long2 (r8 + r16) are
  **optional**, added in that order only if the projected spend leaves room (request in `QUESTIONS.md`).

## Expected results (falsifiable)

Per seed, r9–r16 against r8 (all Lean alone; `trajectory-cap6`'s r1–r8 are Lean-alone too):

| quantity | r8 (s0 / s1 / s2) | expected over r9–r16, per seed |
|---|---|---|
| new `rl_targets` (`targets_cum` r16 − r8) | 4,257 / 4,235 / 4,204 | **+40 to +70** |
| new transfer (`transfer_cum` r16 − r8) | 2,071 / 2,055 / 2,031 | **+30 to +60** |
| new targets per round | +16 / +25 / +31 at r8 | declining, ≤ +8 per round on most seeds by r14–r16 |
| target sample accuracy | 0.902 / 0.899 / 0.889 | 0.90–0.93 |
| `targets_cum` at r16 | — | **below cap 12's r8 (4,365) on all three seeds** (≈ 4,275–4,325) |
| group C pass@256 (seed 1) | 0.077 / 0.038 / 0.050 (4 / 2 / 3 of 52 / 52 / 60) | unchanged within the r8 spread (0.038) |
| textbook72 / holdout250 solved (seed 1) | 43 / 43 / 39; 225 / 226 / 221 | within ±3 / ±5 of r8 |

**Falsifiers of "saturating" (either):**
1. ≥ 100 new targets over r9–r16 on ≥ 2 of 3 seeds.
2. Group C pass@256 (sample seed 1, mean over each seed's C, tb72 + h250) rises at r16 by more than the r8 seed spread
   (0.038) in the mean over seeds, with ≥ 2 of 3 seeds rising.

A further check of the cap-6-vs-cap-12 question: if any seed's r16 `targets_cum` reaches 4,365 (cap 12's lowest r8),
"cap 6 stops below cap 12" is refuted for that seed.

Noise: n = 3 training seeds, each compared with its own r8 (within-run). Counts are reported per seed; group C changes
of 1–2 theorems per seed are inside the k = 256 sample re-draw spread, so falsifier 2 is evaluated on the seed mean
against the across-seed spread. No cross-seed claim is made below `NOISE_FLOOR.md`'s MDD.

## Compute, budget, stop rule

Budget **$12 / 24 pod-hours**, registered with `podbudget` before the first pod. Three A40s at $0.49/h, ≈ 7.6 h each
(8 rounds at ≈ 3,000–3,300 s, setup, r16 reads) ≈ $11.2. Per-arm compute rows per seed and round (GPU-seconds,
generated tokens, fine-tune steps/tokens, Lean checks) from the ladder's own `record.py` rows (`ND_RUN_ID=rl-continue-cap6`)
and the read logs. Stop rule: the run ends after r16 and the core reads. Ladders have priority over every read; if the
projection exceeds $12 before r16, I extend only within the declared budget and otherwise ask in `QUESTIONS.md`.
