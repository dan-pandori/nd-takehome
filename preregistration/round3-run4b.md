# Pre-registration: round3-run4b — does "or nothing" survive model size? (depth-3 half)

Written 2026-09-18 17:55 UTC, before any pod of this run was created (gate 0). Executor:
agent:claude. Branch `dan_round3-run4b`. Governing brief: `BRIEF_scale.md` (run4b half);
policy: `AGENT_POLICY.md`. Edits to the numbers below get a dated reason in §Amendments.

## Question

Every result so far is on a 3.2M-parameter model. At ≈ 25M (8 layers, d = 512) and ≈ 85M
(12 layers, d = 768), trained on the same cap-6 f = 0 depth-3 set (`train_depth3_f0_a1.jsonl`,
no depth-3 proof in pretraining): how often does a Stage-1 draw emit depth-3 proofs before
RL, at what rate, and how much does expert iteration add beyond the base's reach (targets
acquired that the base does not reach at pass@10⁴) — and does that fraction grow or shrink
with size?

## What I found before writing this (changes the 3.2M row the brief quotes)

The brief's 3.2M reference numbers for depth-3 (10 / 16 non-zero draws; plateau 0.30–0.36)
are from the ignition study's pool — the 300 shortest of `targets_depth3.jsonl`, where
depth-3 is *optional* (673 of 1,000 targets have a depth-≤ 2 proof). This run uses run 1's
**required@8** pool (`data/r3_1/depth3_req.jsonl`, committed on `origin/dan_round3-run1`,
checked out here unchanged; 300 targets, min 7 / 8 lines: 6 / 294; depth-≤ 2 alternative at
9 / 10 lines / none: 288 / 1 / 11). On *that* pool the reviewed 3.2M row
(`numbers.md` §Round 3 run 1 on that branch; files `artifacts/r3_1/cov_depth3_s2?.s0.jsonl`,
`artifacts/r3_1/ei_depth3_s2?_req/`, checked out here) is:

- non-zero draws **2 of 8** (s22 3.3·10⁻⁶, s24 4.3·10⁻⁵; six draws 0 hits in 600k);
- `req` arms: **no ignition in 8 of 8**; required targets with a pattern proof at round 8:
  0, 0, 0, 0, 5 (s24), 0, 0, 0 of 300 — i.e. acquisition ≤ 0.017, not 0.30–0.36;
- the six zero-rate arms never took a training step.

So the like-for-like 3.2M comparison is "2 / 8 non-zero, acquisition ≈ 0", and the brief's E4
for run4b ("rises above 0.30–0.36 to ≥ 0.5") compares across pools. I keep the required pool
(the brief's first choice, and the only one where "EI-only" means the pattern) and state my
expectations against the like-for-like row. The 3.2M row has no pass@10⁴ sample, so its
EI-only fraction is reported as acquired 5, base-reachable at 2,000: 3 (s24), not as a fraction
at 10⁴.

## Design I will run

**Stage-1.** `train.py --mode abs --cap 6 --bs 128 --steps 6000 --lr 3e-4 --min_lr 3e-5
--warmup 500` on `data/p2/train_depth3_f0_a1.jsonl`, `--heldout data/p2/heldout.jsonl`;
`--n_layer 8 --d 512 --n_head 8` (25M) and `--n_layer 12 --d 768 --n_head 12` (85M); seeds
0, 1, 2 per size → 6 models, `ckpts/r3_4b/stage1_depth3_f0_a1_{25M,85M}_s{0,1,2}.pt`.
Parameter count printed by `train.py` and recorded.

**E5 gate.** `eval_set.py --temperature 0` on all 5,000 of `data/p2/heldout.jsonl` per
checkpoint. If a size's **median** over the three seeds misses the gate, one retry for that
size (`--lr 1e-4 --min_lr 1e-5 --steps 12000`, same seeds); if the retry also misses, the size
is reported as untrained and still run through the pipeline (the measurement is cheap and the
miss is itself informative), marked as such.

**Pool.** `data/r3_1/depth3_req.jsonl` (300 required@8) and `depth3_req_transfer.jsonl` (100).
Pattern = `patterns.depth3` on the dependency-pruned proof, start-index normalised distinct
proofs, min-round rule — `r3_1_analysis.py`'s counting, reused unchanged so the 3.2M row and
the new rows are counted by the same code.

**Per draw.**
1. Pre-RL: `coverage.py --k 2000 --temperature 0.8 --seed 0` on the 300 targets (600k
   samples). Zero-rate = 0 pattern hits. `frozen@256` read from the same file (first-hit
   index ≤ 256), as in run 1.
2. `req` arm: `expert_iter.py --rounds 8 --k 32 --temperature 0.8 --retain 20000
   --ft_steps 600`, seed = model seed; `--ft_lr 1e-4` at 25M, `--ft_lr 3e-5` at 85M (the 3.2M
   arms used 3e-4 = 0.3 × their Stage-1 peak lr of 1e-3; 1e-4 is the same ratio for 3e-4; the
   brief asks for 3e-5 at 85M). Batch as memory allows (recorded in `args.json`).
3. Frozen control: same command with `--no_train` (equal attempts, 8 × 32 = 256 per target).
4. pass@10⁴ (`coverage.py --k 10000`, 3·10⁶ samples) from the Stage-1 checkpoint for every
   draw whose `req` arm ignites; for non-igniting draws the 600k sample stands in.
5. **Conditional `mix` arm** (added by me; run 1's design): for every draw whose `req` arm
   does not ignite, the same EI on `data/r3_1/depth3_mix.jsonl` (300 required + 300 depth-≤ 2
   neighbours), budget permitting. At 3.2M, 3 of 6 zero-rate draws ignited on `mix` and 0 of 6
   on `req`; this tells whether a zero at scale is again pool composition.

**Definitions.** Ignition (run 1's): first round with ≥ 20 of 300 required targets holding a
pattern proof, cumulative; I also report the ignition study's ≥ 2 % (6 targets).
Acquisition = required targets with a pattern proof by round 8 ÷ 300. EI-only fraction =
(acquired targets with no pattern proof in the base's 10⁴ samples) ÷ acquired. Every counted
proof re-verified with the unmodified `nd_verify`.

## Expected results (numeric / falsifiable)

My own expectations; the brief's are quoted for comparison. Confidence is low on E1–E2: the
training set contains no depth-3 proof at any size, and a larger model could fit the
"depth ≤ 2" regularity *more* tightly rather than less.

- **E1 non-zero draws** (≥ 1 pattern hit / 600k). Brief: 3 of 3 at both sizes. Mine:
  **≥ 2 of 3 at each size** (3.2M like-for-like: 2 / 8). Wrong if ≤ 1 of 3 at either size.
- **E2 rates.** Brief: ≥ 10× per size step at the median. The 3.2M median is 0, so I restate:
  median per-sample rate **≥ 1·10⁻⁵ at 25M and ≥ 1·10⁻⁴ at 85M**, and the 85M median
  ≥ 3× the 25M median. Wrong if either median is below its threshold.
- **E3 zero-rate draws** stay at 0 / 300 on `req` through 8 rounds and never take a training
  step. (If every draw is non-zero, E3 is vacuous — reported as such.)
- **E4a ignition on `req` is rate-gated:** a draw ignites within 8 rounds **iff** its pre-RL
  rate is ≥ 1·10⁻⁴ (≥ 60 hits / 600k); draws between 0 and 10⁻⁴ acquire ≤ 20 targets (3.2M
  s24 at 4.3·10⁻⁵: 5). I expect **1–2 of 3** 85M draws to ignite by round 3, not the brief's
  3 of 3, and **≥ 1 of 3** at 25M to ignite by round 8.
- **E4b plateau:** every igniting arm reaches **≥ 0.60** of the 300 required targets by round
  8 (brief: ≥ 0.5 at 85M; the 3.2M `mix` arms reached 0.70–0.85 of the required stratum once
  ignited). Frozen control ≤ 0.10 for the same draws.
- **E4c EI-only fraction:** **≥ 0.5 for every igniting draw** (the base's 10⁴ reach is
  concentrated on few targets), and **lower at 85M than at 25M** when both sizes have an
  igniting draw (higher base rate → more base-reachable targets). The brief's falsifier —
  the fraction *growing* with size — is the outcome I do not expect; two igniting draws per
  size are needed before I call a direction (policy: two seeds).
- **E4d 9-line alternative:** 0 required targets solved without the pattern in any arm at
  25M; at 85M **≤ 5 %** of solved targets use the 9–10-line depth-≤ 2 route (bigger models
  write longer proofs; the pool is required@8, not required@10).
- **E5 gate.** Brief: ≥ 0.90 at 25M, ≥ 0.93 at 85M. Mine: 25M **0.90–0.93** (passes); 85M
  **0.91–0.95** with the gate at risk (data-limited: 155k cap-6 records, 6,000 steps) — I
  give the 85M median a 50 % chance of clearing 0.93 on the first schedule.
- **E6 conditional `mix`:** of the draws that do not ignite on `req`, **≥ half ignite on
  `mix`** by round 8 (3.2M: 3 / 6 zero-rate, 2 / 2 non-zero).

**What would change the project's answer.** All six draws non-zero with E3 vacuous → "or
nothing" restated as a small-model regime (on this pool 3.2M is mostly zero-rate). A zero-rate
draw at 85M that stays 0 / 300 on `req` → the clause survives at the sprint's size. EI-only
fraction rising with size across ≥ 2 igniting draws per size → against the elicitation
reading.

## Budget and stop rule

Ceiling **$50**, stop at **$45** (pods of this run only; `rpbalance` $185.50 at 17:52 UTC,
shared with run4a and `la-6`; checked before each pod, alert line in `~/ALERTS.md` if < $50).
Deviation from the brief's suggestion, decided now: **A40 48 GB pods ($0.49/h), one per draw
(up to 6), instead of two A100s ($1.59/h)** — these models are ≤ 85M, the jobs are
sampling-bound and independent per draw, and 6 × $0.49 < 2 × $1.59 with three times the
parallelism; fallback card RTX A6000 ($0.53) or RTX 3090 ($0.50) if A40 stock fails. Estimate:
6 draws × ≈ 7 h × $0.49 ≈ $21 plus ≈ $5 for `mix` arms. Pods are created sequentially and
deleted as soon as their files are pulled and listed. If short: drop the 25M pass@10⁴ runs
first, then the 25M frozen arms, then `mix`. Stop when the 85M cell has 3 draws through 8
rounds and the pass@10⁴ samples of its igniting draws are pulled, or at $45.

## Amendments

- **A1, 2026-09-18 19:00 UTC — optional-pool pre-RL sample added (not yet run when written).** Reason: the brief's 3.2M
  reference (10 / 16 non-zero, rates 0–1.9·10⁻³) is on the ignition study's pool — the first 300 of `data/p2/targets_depth3.jsonl`
  (7 / 8 lines: 166 / 134; depth-3 optional; 44 of its classes are also in the required pool) — so a like-for-like E1 / E2 needs the
  same sample from the new draws: `coverage.py --in data/p2/targets_depth3.jsonl --limit 300 --k 2000 --temperature 0.8 --seed 0`
  per draw → `artifacts/r3_4b/optcov_depth3_<size>_s<seed>.s0.jsonl`. **What I had already seen when writing this:** all six
  first-schedule models miss the E5 gate (0.885–0.891); the three 25M `req` arms are 0 / 300 after 8 rounds; the required-pool
  samples in progress have 0 verified proofs; the writing diagnostic (log.md 18:55) shows the larger models open a third box and
  exceed 6 lines *less* often than the 3.2M draws. **Expectation given that:** non-zero draws on the optional pool **≤ 1 of 3 at
  25M and 0 of 3 at 85M** (3.2M: 10 / 16), every rate < 2.5·10⁻⁴ — i.e. the brief's E1 / E2 fail in the direction opposite to
  the one it guarded against. Wrong if ≥ 2 of 3 are non-zero at either size.
- **A2, same time — E6 (`mix`) stands as written, but for the record my guess after the diagnostic is lower:** I now expect
  ≤ 1 of 3 to ignite on `mix` at 85M (the models write ≤ 6 lines in 95–99 % of samples and the neighbours need 7–8), and I would
  not be surprised by 0 of 6. The pre-registered E6 (≥ half) is what gets scored.
