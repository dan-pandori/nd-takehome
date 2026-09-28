# Pre-registration — run `ckpt-avg`

Written 2026-09-28 ~04:45 UTC, before any pod of this run exists and before any evaluation.
Executor: agent:claude. Repository `~/work/ckpt-avg`, branch `dan_ckpt-avg` (from
`origin/dan_stage1-dynamics`). Governed by `AGENT_POLICY.md` (nd-rl canonical). Brief: proposal 14,
item 8. Budget **$2 / 4 pod-hours**, registered `podbudget ckpt-avg --set 4 2` before the first pod.
No training: evaluations of saved checkpoints only.

## Question

`stage1-dynamics` found the depth-3 "mode" is an oscillation along each run (all 12 of its
24,000-step runs crossed the 0.44 cut 1–10 times). Does **uniform weight averaging of a run's late
checkpoints**, or **choosing the checkpoint by per-length validation loss**, remove that oscillation —
collapse the across-seed sd — and at what cost to the mean?

## Material and model label

Every number is for run `stage1-dynamics`' checkpoints (`hf://buckets/dan-pandori/nd-rl/stage1-dynamics/ckpts/sd/`):
3,214,336-parameter GPT (4 layers, d 256, 8 heads), **from scratch**, `lean_seq`, **cap 6**, WSD
schedule (lr 1e-3 after 200 warmup steps, linear decay to 1e-4 over the last 20 % of `--steps`).
- **Arm W**, seeds 0–7, trained on `data/p2/train_depth3_f0_a1.jsonl` (155,000 records, 0 depth-3):
  trajectory `w_s{k}.step{1000..23000}.pt` (every 1,000; stable phase ends at 19,200), decayed
  endpoints `w_s{k}.pt` (24k), `w12_s{k}.pt` (decay 9,600→12,000), `w6_s{k}.pt` (4,800→6,000).
- **Arm F**, seeds 0–3, trained on `data/sd/train_fresh.jsonl` (572,759 records, 0 depth-3):
  `f_s{k}.step{2000..22000}.pt` (every 2,000), `f_s{k}.pt` (24k).
- Arm C (cosine 6k, finals only) is not used; arm R is not a subject (see "addition" below).

## Split (committed before any evaluation)

`ca_split.py`: `data/p2/heldout.jsonl` (5,000) → `data/ca/heldout_A.jsonl` / `heldout_B.jsonl`, 2,500
each, stratified by (length, depth-3): per half 500 each of len2–len5, 250 len6 non-depth-3, **250
depth-3**. Unit of assignment = renaming class under a premise-order-insensitive key (4,999 classes,
0 shared between halves). Seed 20260928. **Half A** is used only for the validation loss that selects
(LS6, LSd3); **every reported accuracy is on half B**.

## Variants (fixed in `ca_plan.py`)

Per run: **E24/E12/E6** decayed endpoints; **A{D}_K{K}** uniform average of the last K stable-phase
trajectory checkpoints before decay point D (W: A24 K=2,4,8 over steps ≤19k; A12 K=2,4,8 over ≤9k;
A6 K=2,4 over ≤4k. F: A24 K=2,4,8 at 2k spacing, so K=8 spans 4k–18k); **T24_3/T24_5** the decayed
24k endpoint averaged with its 2/4 preceding decay-phase checkpoints (across-decay averaging; W only
for T24_5); **LS6 / LSd3** the run's own checkpoint (any of its trajectory + endpoints, 26 for W, 12
for F) with the lowest half-A loss on the 6-line bin / depth-3 slice (`train.py`'s `val_bins`). A
control `w_s0.CTRL_self19000` (step 19000 averaged with itself) must reproduce step 19000's half-B
result exactly.

**Evaluation:** `sd_eval.py`, greedy, Lean alone (strict `lean_seq` grammar + Lean 4 core; `nd_verify`
never called), `--texts`, on half B, batch 2,500 (the whole half in one batch), `max_new` 400 (as
`stage1-dynamics`; I report the fraction of rows hitting it and raise it if > 0.1 % of any stratum),
fixed for every checkpoint. Peak GPU memory recorded. Proof length reported in lines and term size.

## Adoption rule (the brief's, made exact)

Primary population: **arm W, 8 seeds, half B**; baseline **E24** (what `stage1-dynamics` reports).
A variant becomes the Stage-1 standard iff
(i) across-seed sd on the depth-3 slice ≤ ½ of E24's, (ii) across-seed sd on the 6-line bin < E24's,
(iii) mean on every bin (len2..len6) and the depth-3 slice ≥ E24's mean − 2 pp.
Candidates: A24_K2/K4/K8, T24_3, T24_5, LS6, LSd3 (7 candidates; point estimates, n = 8, so I also
report an F-test 95 % CI on each sd ratio and say plainly that the rule is judged on point estimates
with ~±50 % uncertainty on an sd at n = 8). A12/A6 vs E12/E6 and arm F (n = 4) are secondary,
reported, not part of the rule.

## Expected results (falsifiable)

Reference, from `stage1-dynamics` on the full held-out set (my half-B numbers will be a re-draw of these
by half): W E24 depth-3 per seed 0.06/0.94/0.64/0.40/0.92/0.94/0.49/0.47 → mean ≈ 0.61, sd ≈ 0.31.

1. **Averages are not broken**: every A and T variant is within 3 pp of the mean of its constituents on
   len2–len5 (overall ≥ 0.80). Falsified if any average falls > 5 pp below its worst constituent on len2–len5.
2. **Uniform averages do not meet the rule.** A24_K8 depth-3 across-seed sd between 0.18 and 0.35;
   sd ratio vs E24 < 2 for A24_K2/K4/K8 and T24_3/T24_5. The average lands **above the mean of its
   constituents** on depth-3 in ≥ 6/8 W seeds (averaging acts like lr decay, which raised the mean from
   ≈ 0.3 along the stable trajectory to ≈ 0.6 at E24) but **below the constituents' max** in ≥ 6/8.
3. **LSd3 wins and meets the rule**: depth-3 mean ≥ 0.75 and sd ≤ 0.15 on W, 6-line sd below E24's, no
   bin down > 2 pp. LS6 is second (depth-3 sd ≤ 0.20). Rationale: stage1-dynamics measured within-run
   ρ ≈ −0.89 between depth-3 loss and depth-3 accuracy, and every run's trajectory max is ≥ 0.49.
   Falsified if LSd3's depth-3 sd > 0.15 or its mean < E24's.
4. T24_3/T24_5 ≈ E24 (depth-3 sd ratio < 1.3).
5. The self-average control reproduces step 19000 exactly (identical per-theorem verdicts).
6. Arm F (secondary) shows the same ordering: LSd3 has the smallest depth-3 sd of the variants.

My confidence: (1) 85 %, (2) 70 %, (3) 55 %, (4) 70 %.

## Addition beyond the brief

The `stage1-dynamics` review's one open gap: arm R's counted proofs have no literal text. On the same
pod, after the main evaluation, `sd_eval.py --texts` on the ten arm-R checkpoints, **full held-out
file at stage1-dynamics' settings** (batch 512, max_new 400) → `artifacts/ca/ev_r/`. Expected: per-slice
counts equal to stage1-dynamics' `artifacts/sd/ev/r*.json` within ≈ 1 row in 128 (re-draw), exactly
if the GPU class and settings match.

## Budget and stop rule

One A40 (or RTX 3090), ≈ 352 half-B evaluations + 10 full ones + half-A losses: expected ≈ 1–1.5
pod-hours, ≈ $0.75. Stop at 4 pod-hours / $2 whatever the state; delete the pod as soon as its files
are pulled. RunPod balance never below $100.
