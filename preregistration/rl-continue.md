# Pre-registration — rl-continue: is the cap-12 RL saturated? Rounds 9–16 on the same targets

Run id `rl-continue`, executor, branch `dan_rl-continue` (from the fork's `origin/dan`). Written 2026-10-03 17:25 UTC,
before the first pod. Authorised by Dan 2026-10-03 ("Let's first do the cheap direct check").

## Question

`trajectory`'s three cap-12 T1 ladders add few new targets in r6–r8 (+18/+14/+5, +20/+9/+9, +27/+13/+12 for s0/s1/s2).
Is the RL saturated — do 8 more rounds on the same targets add only a few targets and transfer theorems and leave
the hard group C where it is — or does it keep finding new things?

## Models (every number below is on one of these)

`trajectory`'s T1 ladders, seeds 0–2: ALiBiGPT 9,560,832 params (`best-state`'s best recipe), `lean_staten`, from
scratch on K12 (`data/kh/train_k12.jsonl`, cap 12), Stage-1 1,200 s on an A40, then 8 EI rounds
(`state_ladder_ei.py`, k 32, T 0.8, 600 fine-tune steps at lr 3e-4, 128 proofs/step, replay 20,000 K12 records,
≤ 4 proofs/target × weight 4, 4,495 `rl_targets`, 2,285 `transfer`). r8 checkpoints:
`hf://buckets/dan-pandori/nd-rl/trajectory/ckpts/tj/ladder/la_T1_best12_s{0,1,2}_r8.pt`
(md5 f9afd386… for s0; all three checked against `trajectory`'s `artifacts/tj/score/ckpts_s*.md5`). Lean alone decides.

## Design (what I will run)

- **Continue each ladder for r9–r16** with `state_ladder_ei.py --resume --start_round 9`, after placing `trajectory`'s
  `found_8.jsonl`, `found_transfer_8.jsonl`, `alloc_8.json` and the r8 checkpoint at the resume paths. Same name
  (`la_T1_best12_s<S>`), same flags as `trajectory`'s `args.json`; ladder sampling batch as each seed ran its r8
  (s0, s1: 2,048; s2: 1,024 after an OOM resume in `trajectory`). One ladder per 48 GB card (A40, or RTX A6000 if
  A40 stock is out). An OOM resumes from the last finished round at batch 1,024 (a sampling re-draw, logged).
- The ladder is run as r9–r12, then the r12 read-outs, then `--resume --start_round 13` for r13–r16 on the same pod.
  The resume re-creates the replay/shuffle RNG (`random.Random(seed*7919)`) at r9 and again at r13; the per-round
  sampling seeds (`seed*1000 + r`) and the fine-tune seed are as in a continuous run. `trajectory`'s s2 itself was
  resumed at r2 the same way.
- **Seamlessness checks:** (1) md5 of the checkpoint r9 samples from equals `trajectory`'s r8 md5; (2) the resume
  line's proof count equals `found_8.jsonl`'s line count; (3) r9's `targets_cum` ≥ r8's and every r8-solved target is
  still solved (the found set is only added to).
- **Read-outs** with `trajectory`'s `pod/tj/read.sh` (k 256, T 0.8, max_action 512, max_steps 96, batch 2,048 with the
  1,024 OOM retry) and `best-state`'s `pod/bs/read.sh` settings for rr600 / long2 (`lpool_reread.py`, same flags):
  - r12 and r16, every seed: textbook72 and holdout250 at sample seeds 1 and 0 (seed 1 = `trajectory`'s pass@k seed;
    seed 0 defines its groups).
  - r8 and r16, every seed: `rr600` rows with `L_true_lb` 13–16 (400 theorems; `data/rc/rr600_13_16.jsonl`, a filter of
    `data/ladder/transfer_long_rr600.jsonl`) and `transfer_long2` (21), sample seed 0. `trajectory` did not read these at
    r8, so its r8 checkpoints are read here as the baseline.
  - Group C = `trajectory`'s per-seed group C (seed-0 samples: not solved at end of pretraining nor at r8), taken from
    its pend/r8 read files with its `tj_analysis.groups` code. The C pass@256 read-out uses sample seed 1 (seed 0 is
    biased to 0 at r8 by construction).

**Deviation from the brief (budget):** the brief lists rr600/long2 at r12 and r16 with both sampling seeds. At
≈ 3,500 s per round (r8 timings) the 24 ladder-rounds alone are ≈ 24–25 pod-hours of the 30-hour ceiling, so rr600/long2
are read at one sampling seed, at r8 and r16 (the endpoints of the question) and not at r12. Priority if the budget
binds: ladders > r16 reads > r12 textbook72/holdout250 seed 1 > r8 rr600/long2 > r12 seed 0. A request for $3 more is in
`QUESTIONS.md`; if granted, r12 rr600/long2 and seed 1 of rr600/long2 are added.

## Expected results (falsifiable)

Per seed, r9–r16 against r8 (all Lean alone; the r1–r8 numbers are also Lean-alone, measured 2026-10-01):

| quantity | r8 (s0 / s1 / s2) | expected at r16, per seed |
|---|---|---|
| new `rl_targets` solved, r9–r16 | — | **+20 to +40** (cumulative 4,383 / 4,365 / 4,407 of 4,495 → ≈ 4,405–4,445) |
| new transfer theorems (`transfer_cum`), r9–r16 | 2,185 / 2,170 / 2,190 of 2,285 | **+10 to +20** |
| new targets per round | +5 / +9 / +12 at r8 | declining, mostly ≤ +8 per round by r13–r16 |
| target sample accuracy | 0.918 / 0.918 / 0.924 | 0.92–0.95 |
| group C pass@256 (seed 1) | ≈ 0.05 (pooled tb72 + h250) | unchanged within the r8 seed spread |
| textbook72 solved (seed 1) | 48 / 48 / 53 | within ±3 of r8 |
| holdout250 solved (seed 1) | 240 / 236 / 237 | within ±3 of r8 |
| rr600 13–16 / long2 solved | (read here at r8) | within ±10 / ±1 of r8 |

**Falsifiers of "saturated" (either):**
1. ≥ 60 new targets over r9–r16 on ≥ 2 of 3 seeds. (The r6–r8 three-round sums are 37 / 38 / 52, SD ≈ 8; 60 is
   ≥ 2 SD above the extrapolation's upper end.)
2. Group C pass@256 (sample seed 1, mean over each seed's C theorems, textbook72 + holdout250) at r16 exceeds r8 by
   more than the r8 seed spread (max − min of the three per-seed r8 values), in the mean over seeds, with ≥ 2 of 3 seeds
   rising.

Noise: n = 3 training seeds, one continuation each, compared with its own r8. This is a within-run design; the
quantities are counts, reported per seed. A textbook72 difference of ≤ 3 theorems at k 256 is within the sampling
re-draw spread seen in `trajectory` (x0 vs x1 at r8: 0–1); `NOISE_FLOOR.md`'s MDD for textbook72 across training seeds
is larger, so no cross-seed claim is made from a ≤ 3 change.

## Compute, budget, stop rule

Budget **$15 / 30 pod-hours** (registered with `podbudget` before the first pod). Three pods (one ladder each),
≈ 10.5 h each projected incl. reads (≈ $15.5 at $0.49/h). Per-arm compute rows (GPU-seconds, generated tokens, fine-tune
steps/tokens, Lean checks) per seed and round come from the ladder's own `record.py` rows (`ND_RUN_ID=rl-continue`) and
the read logs. Stop rule: the run ends after r16 and its reads; if the projected spend passes $15 before then, the
lowest-priority reads above are dropped first; ladders are never cut before r16 unless a pod fails twice.
