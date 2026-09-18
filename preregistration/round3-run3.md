# Pre-registration: round3-run3 — base generalisation by pattern class, many seeds, no RL

Written 2026-09-18 05:40 UTC, before any pod of this run was created (gate 0). Executor:
agent:claude. Branch `dan_round3-run3`. Governing brief: `BRIEF_base-generalisation.md`
(round-3 proposal §3); policy: `AGENT_POLICY.md`. Edits to the numbers below get a dated
reason in §Amendments at the end of this file.

## Question

With what probability does a cap-6 Stage-1 draw trained at f = 0 emit a pattern at all
before any RL, at what per-sample rate, over the full required pool — and do the
structural (depth-3) and rule-sequence (reductio) classes differ at the base level with
95 % intervals that separate? What property of a draw predicts whether it generalises?
Current numbers rest on n = 16 (depth-3, 10 generalise) and n = 11 (reductio, 4), sampled
on 300-target subsets that missed some draws' reachable targets (review_ignition.md,
refinement 3; review_followup.md, block B caution).

## Design I will run

**No training step beyond Stage 1. No RL.**

**Draws.** 24 fresh Stage-1 models per set, seeds 30–53, identical command to the follow-up
and ignition studies, `train.py --mode abs --steps 6000 --bs 128 --cap 6 --heldout
data/p2/heldout.jsonl`, on

- `data/p2/train_depth3_f0_a1.jsonl` (155,000; re-classified 05:35 UTC: depth3 0, max
  length 6),
- `data/p2/train_reductio_f0.jsonl` (155,000; reductio 0),
- `data/p2/train_derived_ore_f0.jsonl` (155,000; derived_ore 0, derived_ore_strict 0 — so
  no set is assembled; `f0_check.py`, `artifacts/r3_3/f0_check.log`).

Checkpoints `ckpts/r3_3/stage1_{depth3_f0_a1,reductio_f0,derived_ore_f0}_s<seed>.pt`, logs
`artifacts/r3_3/train_<set>_s<seed>.log`. `train.py` gets a per-rule held-out breakdown at the
final eval (mean cross-entropy over the tokens of lines whose rule is R, for every rule; plus
the loss at the rule-name position only). Existing output lines unchanged; the addition is
tested on the pod with a short run before the 72 draws start.

**Pools** (all committed under `data/r3_3/`):

- Depth-3: the whole campaign pool `data/p2/targets_depth3.jsonl` (1,000 targets), sampled
  in two parts per draw: part 1 = the first 300 (the length-ordered shortest 300, i.e. the
  ignition study's sample, 166 × 7-line and 134 × 8-line), part 2 = the remaining 700
  (8–12 lines). The **required@8 stratum** = the 142 targets whose depth-≤ 2 search at
  bound 8 fails without timeout (`targets_depth3_maxdepth2.jsonl`) while the unrestricted
  minimum is ≤ 8 (97 of them are in part 1); it is reported separately. If run 1 commits
  `data/r3_1/depth3_req` before my depth-3 coverage phase starts it is sampled as a further
  pool, reported separately, never pooled.
- Reductio: `data/p2/targets_reductio_req.jsonl` (300; the whole required pool of run 5,
  16 schemata; 7-line schemata are `nand_neg` 26 and `negimp_to_pos` 26).
- Derived-ORE, cap 6, strict: the 363 targets of `data/p2/targets_derived_ore.jsonl` whose
  generating proof is strict derived-ORE (`patterns.derived_ore_strict` on the pruned
  proof; 318 with minimum 7, 37 with minimum 8, 8 unknown; `derived_ore_strict_cands.jsonl`),
  labelled with `necessity.py --pattern derived_ore_strict --bound 10 --time 60` (forbid =
  `ORE_DERIVED`). Pool = 300: required ones first (ordered by `min_lines_ub`, then file
  order), then reachable non-required ones in the same order. Accept only 0 `oracle_ok`
  failures and 0 `restriction_ok` failures; ten targets hand-checked (proof read, verifier
  re-run, pattern label recomputed) and logged before sampling.

**Sampling.** `coverage.py --k 2000 --temperature 0.8 --batch 2000 --procs 4 --seed 0` per
draw and pool (600k samples over 300 targets; the depth-3 tail adds 1.4M), one coverage job
at a time per 24 GB card. Output `artifacts/r3_3/cov_<set>_s<seed>[_p1|_p2].s0.jsonl` with
every distinct verified proof, its hit count and pattern labels (unchanged format). New
fields added to each record, computed on every distinct decoded sample whether or not it
verifies: `n_parsed` and `fh_by_pred` / `fh_ok_by_pred` = sample-weighted counts of the
first-half predicates below (new functions in `patterns2.py`, verifier-checked tests).

**First-half predicates** (on the written, unverified, unpruned sample; G = the prompt's goal):

- depth-3: `d3_written` (a line at depth ≥ 3 — a third box is opened, valid or not; primary),
  `d3_as_as` (an AS at depth 2 immediately followed by an AS at depth 3), `d2_two_boxes`
  (two or more boxes opened at depth 2).
- reductio: `negi_neggoal_nodn` (a NEGI closing a box whose hypothesis is `~G`, so it yields
  `~~G`, with no DN citing it; primary), `negi_neggoal` (with or without DN), `neg_goal_hyp`
  (an AS line `~G` anywhere).
- derived-ORE strict: `derived_disj` (a line obtained by a rule other than PR/AS whose formula
  is a disjunction with distinct disjuncts; primary), `ore_on_derived` (an ORE whose
  disjunction line is not PR/AS).

**Definitions.** A draw *generalises* a pattern iff ≥ 1 verified sample over the pool
carries the pattern (`patterns.classify` on the pruned proof, the campaign's predicates;
depth-3 on part 1 + part 2). Per-sample rate = Σ pattern hits / Σ samples, re-derived from
the per-proof `count` fields. Frozen@256 = targets whose first pattern hit index ≤ 256.
Clopper–Pearson 95 % intervals (`ignition_analysis.clopper_pearson`). Predictors: final
held-out loss, per-rule losses, first-half rates; Spearman ρ against the generalisation
indicator and against log rate among generalisers, with a 10,000-draw permutation p.
External stratum: the ignition study's 16 depth-3 and 11 reductio draws (`artifacts/ign`,
300-target samples), tabulated beside the new draws, never pooled.

## Expected results (numeric; the run tests these)

- **E1 generalisation counts** (≥ 1 hit over the full pool, 24 draws each): depth-3
  **12–18 / 24**; reductio **5–11 / 24**; strict derived-ORE **18–24 / 24**.
- **E2 separation:** the depth-3 and reductio Clopper–Pearson 95 % intervals do not
  overlap (expected ≈ 0.41–0.81 vs 0.13–0.53 at the point estimates 15 / 24 and 8 / 24).
- **E3 rates:** among generalising draws the per-sample rate spans ≥ 2 orders of magnitude
  (10⁻⁶–10⁻³) for depth-3 and for reductio; every reductio hit is on a 7-line `nand_neg` or
  `negimp_to_pos` target, none on an 8-line-or-longer schema.
- **E4 predictors:** final held-out loss does not predict generalisation (|ρ| < 0.3 for
  each pattern); the primary first-half rate does (ρ > 0.5 for depth-3 and reductio).
- **E5 full-pool effect (depth-3):** at most 2 of the 24 draws with 0 hits on part 1 (the
  300 shortest) have ≥ 1 hit on part 2; ≥ 90 % of all depth-3 hits fall in part 1.
- **E6 derived-ORE pool:** fewer than 50 of the 363 strict candidates are `requires` at
  bound 10 (the follow-up found the pattern rarely necessary at cap 8); 0 oracle
  inconsistencies.
- **E7 attempt vs success:** in every generalising draw the primary first-half rate exceeds
  the verified pattern rate by ≥ 10×; in zero-hit depth-3 draws the `d3_written` rate is
  below 10⁻⁴.

## What would falsify the standing rule

- E2 failing (overlap at n = 24 each) kills "structural patterns are generalised more
  readily by the base"; the class difference would then rest on RL-side behaviour only.
- Reductio ≥ 14 / 24: most draws generalise the sequence; clause (2)'s "or nothing" is the
  minority case and must be stated as such.
- Any reductio hit on an 8-line-or-longer schema before RL contradicts the "7-line entry"
  picture from run 5 and the ignition study.

## Budget and stop rule

RTX 3090 pods at $0.50/h (A40 / A100 fallback if none; disclosed). Estimate: Stage-1 72 ×
≈ 12 min (2 concurrent per pod) ≈ 8–14 pod-h; coverage 48 × 300 targets × ≈ 12 min + 24 ×
1,000 targets × ≈ 45 min ≈ 28 pod-h; total ≈ 36–42 pod-h ≈ **$20**; ceiling $50 (policy).
Order of work: Stage-1 for all three sets; then coverage reductio and derived-ORE (300 each)
and depth-3 part 1 for every draw; depth-3 part 2 last. **Stop** at 24 draws per pattern
fully sampled or at $35 spent on this run, whichever first; if short, cut in this order:
depth-3 part 2 (report part 1 for all draws and disclose), derived-ORE to 12 draws. Reductio
is never cut. Pods deleted when their files are pulled and checked; kill switch cron
re-armed to ≤ 30 h ahead before the first pod job.

## Deliverables

`run3.md` (≤ 400 words + figures), `numbers.md` §Round 3 run 3, `artifacts/r3_3/summary.json`,
all coverage files, `data/r3_3/` pools with oracle labels, `STATUS.md` `RUN3-3 DONE <UTC>`,
bucket `hf://buckets/dan-pandori/nd-rl/round3-run3/{artifacts,ckpts,data}` (all 72
checkpoints), `~/runs/round3-run3/executor.done`.

## Amendments

(none yet)
