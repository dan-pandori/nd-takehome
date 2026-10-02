# Pre-registration: compute-match — our 3.2 M recipe given the GPU time Robbie's recipe used

Run id `compute-match`, branch `dan_compute-match` (fork, from `origin/dan` at `0c492902`). Executor, 2026-10-02.
Checker: **Lean alone** (`lean_judge`, the state environment's gate). `nd_verify` judges nothing.

## Question

`best-state` found best-cap12 T1 (Robbie's 9.56 M recipe + our T1 ladder) beats SN-cap12 T1 (our 3.2 M recipe + the
same ladder) by +14.2 on textbook72 and +103.8 on the dev metric. But each best-cap12 ladder used 1.6–1.9× the
A40-seconds of ours. **If our recipe's T1 ladder gets the A40-seconds best-cap12's ladder used, does the gap close?**

## The compute numbers this rests on (from `artifacts/bs/compute_stdout.txt`, all on A40)

| | Stage-1 A40-s | T1 ladder A40-s (8 rounds) |
|---|---|---|
| best-cap12 s0 / s1 / s2 (record.compute rows) | 1,292 / 1,283 / 1,290 — **mean 1,288** | 25,876 / 30,524 / 28,952 — **mean 28,451** |
| SN-cap12 s2 / s3 (A40, from logs) | 2,244 / 2,250 | 16,623 / 16,042 |

## Deviation from the run brief (and why)

1. **No compute-matched Stage-1 training.** The brief asks to train our Stage-1 until its A40-seconds equal best-cap12's
   mean Stage-1 time (1,288 s). Our 6,000-step SN-cap12 Stage-1 already takes **2,244–2,250 A40-s** (1.74× best's), so
   at cap 12 the premise "ours got less Stage-1 compute" is false: matching would mean *stopping early* (~3,400 steps),
   which handicaps ours and is not the question. (The brief's 565–782 s are the **cap-6** arm's numbers.) So Stage-1 stays
   at the SN-cap12 recipe (6,000 steps × 128 proofs, `state_train.py` control recipe) and is flagged in the compute
   table as ours > best by 1.74×.
2. **Stage-1 checkpoints reused, not retrained.** Since Stage-1 is unchanged, I start the ladders from the inherited
   `state-cap12` checkpoints `stage1_SN12_s{0,1,2}.pt` (bucket `state-cap12/ckpts/sc12/`; 3,216,384-param GPT, 4 × 256,
   `lean_staten`, from scratch on K12 `train_k12.jsonl`). Seeds 0, 1, 2 = best-cap12's seeds (policy: same seeds in
   every arm). This makes the k effect **paired within seed**: SN12 T1 at k 32 (inherited ladder) vs k matched (new),
   same Stage-1. The frozen ("unmatched control") read-outs of these checkpoints already exist in `best-state` and
   `textbook72`; they are inherited with their labels, not re-read. Stage-1 A40-s for s0/s1 are taken as the A40 value
   for s2/s3 (2,244–2,250 s; s0/s1 themselves ran on RTX 3090s, 1,835–1,852 s).

## Design

- **Arm `cm12` (new):** `state_ladder_ei.py`, `state-cap12`'s protocol unchanged (8 rounds, T 0.8, `rl_targets.jsonl`,
  replay from K12, `max_steps` 48, `max_action` 256, ft 600 steps/round, batch 2,048) **except `--k K`**. One ladder per
  A40 pod, nothing else on the GPU while it runs, so its wall-clock is its GPU-seconds (same as both comparators).
- **Choosing K (pilot).** The inherited A40 ladders spend ≈ 2.57 k s on fine-tuning (fixed) and ≈ 13.76 k s on k-
  proportional sampling / Lean / transfer eval. Prior projection: K ≈ 60 matches 28,451 s. Pilot = round 1 of the s2
  ladder at **K = 64** on an A40. With its measured round-1 time I scale the inherited s2/s3 k-proportional time by
  (pilot k-proportional round-1 time) / (inherited round-1 k-proportional time) and pick the multiple of 8 whose projected
  8-round total is closest to **28,451 s**. If that is 64, the pilot ladder simply continues as `cm12` s2; otherwise it is
  killed and s2 restarts at K. **K is written in `STATUS.md` and committed before s0 and s1 launch.**
- **Read-outs, exactly as `best-state` (`pod/bs/read.sh` settings, batch 2,048):** textbook72 k 256, dev1108 k 64,
  holdout250 k 256, rr600 Q and transfer_long2 k 256 (`max_action` 512, `max_steps` 96), held-out greedy — on the three
  `cm12` T1 round-8 checkpoints.
- **Secondary (paired control at identical settings):** re-read the inherited SN12 T1 s0–s2 on textbook72, rr600 and long2
  at the settings above (best-state used inherited textbook72 at batch 4,096 and Q at `max_steps` 48 for them).
- **Compute rows:** `record.compute` registry rows (ND_RUN_ID compute-match, ND_ARM cm12) per round / phase; per-arm table
  with GPU-s, gen tokens, attempts, train steps / tokens, Lean checks. Flag any arm > 1.25× its comparator.

## Quantities and MDDs

- **Headline:** Δ = best-cap12 T1 − cm12 T1 (seed means, n 3 vs 3) on textbook72 (/72) and the dev metric (/1,108).
  MDDs: `best-state`'s pre-registered cap-12 MDDs, **6.5** (textbook72) and **61** (dev).
- Secondary: cm12 T1 − SN12 T1 (k 32), paired per seed, on all pools; holdout250, Q, long2, held-out greedy gaps.

## Expected results (falsifiable)

- cm12 T1 (seed mean): textbook72 **40** (range 37–44); dev **975** (950–1,010); holdout250 **224** (218–230);
  Q (rr600, /380) **330** (300–360); long2 **16** (12–20); held-out greedy ≈ 0.975.
- cm12 − SN12 T1 at k 32: textbook72 **+2.5** (0 to +6); dev **+25** (0 to +60). Doubling attempts per round mainly helps
  the hardest targets; ladder cumulative targets solved at round 8 ≈ 4,260 (vs 4,196–4,215).
- **Headline expectation: the gap stays beyond the MDD.** best-cap12 T1 − cm12 T1 ≈ **+12 textbook72** (≥ 6.5) and
  ≈ **+80 dev** (≥ 61).
- **Falsifier** for "the recipe, not the compute, explains `best-state`": the textbook72 gap closes to < 6.5 **or** the dev
  gap to < 61. If both close: compute explains it. If one closes: mixed, reported as such.
- Chosen K: 56 or 64 (prior projection 60).

## Budget and stop rule

$30, 60 pod-hours (`podbudget compute-match --set 60 30` before the first pod). A40 only (≈ $0.49/h billed; record the
real rate). Plan ≈ 3 × (8.5 h ladder + 1.5 h reads) + 1 h inherited re-reads + 1 h pilot overhead ≈ 32 pod-hours, ≈ $16.
Stop rule: if A40s are unavailable for > 6 h, ask in `QUESTIONS.md` and wait; if a ladder fails twice, report the
other seeds (n 2) and say so. Balance floor $100 respected (balance at start $280.88).
