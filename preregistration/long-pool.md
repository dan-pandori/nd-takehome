# Pre-registration: long-pool — a transfer pool that can measure the length frontier

Run id `long-pool`, executor, fork branch `dan_long-pool` (from `origin/dan` `d90da19`). Written 2026-09-28 ≈ 19:00 UTC,
before the first pod. Budget **$8, 16 pod-hours** (`podbudget long-pool --set 16 8`). Balance floor $100.

## Question
Every length claim reads `L*` (max L with ≥ 5 solved at `L_true` ≥ L) off `data/ladder/transfer.jsonl`, which has only
23 theorems at `L_true` ≥ 13 and none above 14, so `L*` ≥ 13 is barely measurable and `L*` > 14 cannot be measured at all.
Build `data/ladder/transfer_long.jsonl` with ≥ 100 theorems per `L_true` bin 11–16 from the ladder's generator family,
then re-read existing checkpoints on it (no training) and report per-bin solve rates and an uncensored `L*`.

## What the local probe (VPS, before any pod) already showed
- `textbook_pool.py` schemata have a **fixed length per schema** (ladder raw labels): only `dist_or_over_and_conv`
  reaches 13 and only `demorgan_nand_to_or` reaches 14; none reaches 15 or 16. The textbook source can fill 11–14 at
  ≤ 40 instances per schema per bin (the ladder's cap) and **cannot supply 15–16**.
- The strict long generator (`make_coverage_sets.py gen --long`, unchanged knobs) with the generated-length filter
  raised to 12–40 lines: ≈ 2 % of accepted theorems have `L_true` ≥ 11 (bound-10 search, 900 probe theorems, three knob
  settings indistinguishable at this n); of 11 survivors labelled at bound 16: 9 at 11, 1 at 12, 1 at 13. Ladder data
  (63,342 generator theorems, generated length ≤ 16) give 140 / 40 / 8 / 4 at 11 / 12 / 13 / 14.
- Cost on the VPS core: bound 10 ≈ 0.07 s per theorem; bound 16 on a survivor 1–136 s.

## Design
1. **Generation.** (a) Generator: `make_coverage_sets.py gen --long --min 12 --max 40` (strict long generator,
   take-home knobs max_prem 3 / max_depth 3, contradictory-premise theorems dropped, pattern caps off — the ladder's
   command with only the output length filter changed), fresh seeds (base 31000), merged by renaming class.
   (b) Textbook: `textbook_pool.py` (unchanged schemata and sub-formula sampler), fresh seed, schemata that can reach
   ≥ 11 only. A pilot of ~100k generator theorems on the pod measures survival by generated length first; if the
   ≥ 13 yield per CPU-second is ≥ 2× higher in a sub-range (e.g. generated length ≥ 20) the full run keeps only that
   range (an output filter, recorded). Knob changes (ds-generator G1 `--ore_boxes`, `--gen_max_prem 4`) are used **only
   if** the pilot shows ≥ 2× the ≥ 15 yield per CPU-second; every record carries its `gen_knobs`.
2. **Labelling (`minlen.py`, unchanged search).** Stage A bound 10 / 5 s on everything (labels ≤ 10 final → dropped);
   B bound 12 / 30 s on the None-at-10; C bound 14 / 120 s on the None-at-12; D bound 16 / 600 s on the None-at-14.
   Label L is final when the search at every smaller bound terminated; a **timeout at any stage = label unknown,
   excluded, counted per bin/stage**. None-at-16 without timeout is recorded as `L_true ≥ 17` (lower bound only, not
   binned). Each labelling proof is checked by `minlen.py`'s built-in verifier call (labelling tool, as in POOLS.md)
   **and** by Lean via `lean_check` on its Lean rendering; a label whose proof Lean rejects is excluded. Term size of
   the found proof is recorded. `L_true` stays an ND-derived upper bound under Lean (stated with every table).
3. **Disjointness.** Renaming-class disjoint from: validation-36; Stage-1 control set (`data/p2/train_depth3_f0_a1`,
   the C0 / state-env set) and its held-out; cap-horizon K8add / K8flat / K10 / K12 / K14 training sets;
   ds-composition A1–A4 sets; the take-home `data/train.jsonl`; every jsonl under `data/` in git (ladder transfer,
   rl_targets, held-out, target/transfer pools); the ladder reserve and generator pool. Reported as a count table.
4. **Assembly.** Per bin 11–16: all generator theorems up to a cap of 300 per bin, plus textbook ≤ 40 per schema per bin
   (bins 11–14 only); source mix per bin reported. Seed 0 stratified sampling when over cap.
5. **Re-read (no training).** k = 256 per theorem, T 0.8, fast sampler defaults, batch/`max_new` fixed across every
   model and truncation fraction reported; Lean alone decides (`eval_set.py` / `state_eval.py` → `lean_judge`).
   Models, priority order: state-env S T1 r8 s0/s1 and SN-v2 T1 r8 s0/s1; C0 whole-proof T1 r8 s0/s1
   (`ds-generator/ckpts/ladder/la_T1_c0_s*_r8.pt`); state-env S / SN Stage-1 (frozen) s0/s1; C0 Stage-1
   (`lf/stage1_a1_seq_s*`). cap-horizon's K12/K14 **T1** checkpoints are **not in the bucket** (only Stage-1), so K12 /
   K14 Stage-1 s0 are read instead, labelled frozen. Note: the ladder's T1 transfer number is cumulative over 8 rounds'
   checkpoints; this re-read samples only the final checkpoint, so it is not the same quantity.

## Expected results (falsifiable)
- **Pool counts.** 11: ≥ 300 (cap), 12: ≥ 300, 13: 150–300, 14: 100–250, **15: 40–150, 16: 10–80**. I expect to meet
  ≥ 100 in bins 11–14 and **to miss ≥ 100 in bin 16** (and possibly 15) within the budget; if so, the per-bin yield
  and the cost per extra theorem are reported so the gap can be bought later. Stage-D timeout rate 5–25 %.
  Generator share at 13–14 ≥ 60 %.
- **Disjointness:** 0 overlaps after filtering (asserted); raw collisions before filtering < 1 %.
- **Re-read `L*` on the new pool** (≥ 5 solved at `L_true` ≥ L; below 11 reported as "< 11"):
  S T1 **13** (12–14), SN-v2 T1 **13** (12–14), C0 T1 **12** (11–12), S / SN frozen **12** (11–12),
  C0 frozen **< 11 or 11**, K12 / K14 frozen **12** (11–13). Solve rate at 11 for S/SN T1 15–40 %, at 13 1–8 %,
  at ≥ 15 < 3 %. Ordering S ≈ SN > C0 on every bin ≥ 12. No model has ≥ 5 solved at ≥ 16.
- Because each bin has ~100–300 theorems (vs 23 at ≥ 13 before), an `L*` of 13 now needs a ≈ 2–5 % rate, not ≈ 20 %;
  cross-pool `L*` comparisons are therefore not like for like, and I will report rates as well as `L*`.

## Stop rule / budget
Labelling on one 32-vCPU CPU pod (cpu3c/cpu5c, ≈ $0.96–1.12/h), ≤ 4.5 h, ≤ $5; generation stops when bins 11–14 are full
and the 15/16 yield per hour × remaining labelling time can no longer reach 100 — then assemble what exists. Re-read on
one or two GPU pods, ≤ $3; models dropped in reverse priority order if the budget runs short. Hard stop at $8 / 16 h.
