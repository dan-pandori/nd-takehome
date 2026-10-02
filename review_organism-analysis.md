# Review: organism-analysis

Reviewer session, 2026-10-02 (started 18:34 UTC). Run branch `dan_organism-analysis` at `7c5f9688`. Kit:
`review_oa/` (own code; the Lean harness `rlean.py` is reviewer code carried from `review_rfc` on `dan_rl-from-ckpt`).
Phase 1 was done in `~/review/organism-analysis` with the executor's write-ups removed, and committed before phase 2.
I did not open `organism/ANALYSIS.md`, `organism/gallery.md`, `log.md` or the executor's `q*_results.json` / `q*_stdout`
files during phase 1.

**Models (labels used throughout).** All runs use `best_model.ALiBiGPT` 6×384, 9,560,832 params, `lean_staten`
format, trained from scratch for 1,200 s (Stage 1), seeds 0–2.
- **c12**: best-cap12, trained on K12 `train_k12.jsonl` (cap 12). Ladders: `trajectory`'s T1 EI ladders r1–r8.
- **c6**: best-cap6, trained on cap-6 `train_depth3_f0_a1.jsonl`. Ladders: `trajectory-cap6`'s.
- **rfc**: the c12 seeds' EI ladders started at pretraining steps 1,600, 5,000, 12,000 and 16,000 (`rl-from-ckpt`).

Every count is inherited from Lean-judged `state_eval` reads (k 256, T 0.8), compacted by `oa/oa_compact_read.py`.

## §Recount (phase 1, before reading the write-up)

### Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72` equals `origin/main`'s ✔ |
| `nd_verify` used as a judge | no: `oa/` never references it, and every count comes from Lean-judged reads ✔ |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064`, the same on `origin/main` and `origin/dan` ✔ |
| training / test file | no training code was added; branch diff is `oa/`, `pod/oa/`, `tj_score.py` (copied from `dan_trajectory`), `organism/` and the write-ups; no `test_run_once.sh` ✔ |
| pre-registration before first pod | committed 17:03:26 UTC (`3ac05e64`); first pod `oa-p0` started 17:09:27 (`~/pods.log`); file unchanged since ✔ |
| pod use | 2 A40 pods (the pre-registration said one RTX-class pod): 1.00 + 0.90 pod-h, $0.49 + $0.44 (`~/podhours.log`), within $8 |

No hard constraint was violated. There is no quarantine.

### Split disjointness

I used my own canonical class: the lexicographic minimum over the 24 bijections of {P,Q,R,S} of (sorted premise
multiset, conclusion), with F treated as falsum. Script: `review_oa/splits.py`.

| file | records | evaluation theorems hit (of 322) |
|---|---|---|
| `data/ladder/rl_targets.jsonl` (EI targets; on-policy entropy prompts) | 4,495 | 0 |
| cap-6 `train_depth3_f0_a1.jsonl` | 155,000 | 0 |
| K12 `train_k12.jsonl` | 155,000 | 1 (`textbook_3ed45280…`, inherited; it is in the c12 Q1 population, 1 of 246 units) |

The analysis fits *predictors of RL outcomes* on the 322 evaluation theorems, which is the design. No policy is
trained on them.

### Lean re-check (`review_oa/recheck.py`; log in `review_oa/rv/recheck.log`)

The stored reads hold ND strings. I rendered them with my own ND→Lean renderer and checked them with `lean`, and
`#print axioms` had to be a subset of {propext, Classical.choice, Quot.sound}.

I ran the negative controls first. They behaved as they should:
- 60/60 untouched counted proofs pass.
- 5/60 pass after a flip of one ORI line (expected benign `A ∨ A` no-ops).
- 0/60 pass when paired with a different statement.
- A bare `sorry` fails.

Nothing in the compacted reads was recorded as Lean-rejected, so that control was not available.

| arm (counted = r8 x0 proofs of Q1-positive units) | counted | checked | Lean ok | median Lean expr size | median ND lines |
|---|---|---|---|---|---|
| c12 r8 | 9,224 | 150 (30 longest-distinct + 120 random) | **150** | 79 | 20.5 |
| c6 r8 | 9,140 | 150 | **150** | 44.5 | 17 |
| rfc r8 (4 starts pooled) | 77,445 | 150 | **150** | 62 | 18 |
| 315 reference proofs (`minlen`) | 315 | 315 | **315** | 26 | 9 |
| eventual proofs (c12 + c6, random) | 1,664 | 150 | **150** | 29 | 10 |

None of the 915 checked proofs was rejected.

**Term size depends on the definition.** My size counts every node of the elaborated value, including the formulas
in `have` types. The project's `lean_check` term size counts inference nodes, with variables and types counted as 0.
These are different quantities:
- My full size has Spearman 0.69 with `tj_score`'s `term_size` on the 315 references.
- An independent inference count (rule applications in the pruned ND proof, AS/PR/R excluded) has Spearman 0.84.

See Q1 for why this matters.

### Q1: what predicts RL success (`review_oa/q1.py`)

Each unit is (theorem, seed, start) over the 315 references. The population is units the start's x0 read does not
solve. The target is solved at r8 (x0). My features are taken from the inherited per-step scores; the worst-step class
comes from my own classifier on `actions_b0`. My theorem folds use sha1 (the executor uses md5), so fold assignment
differs.

| | c12 pend | c6 pend |
|---|---|---|
| units (per seed) | 246 (84/80/82) | 501 (147/178/176) |
| solved at r8 (= group B, per seed) | 165 (54/51/60) | 355 (101/132/122) |
| CV AUC, w1 only | **0.794** [0.72, 0.86] | **0.651** [0.58, 0.71] |
| CV AUC, full logistic | 0.826 [0.75, 0.89] | 0.787 [0.72, 0.84] |
| CV AUC, GBM | 0.904 [0.85, 0.95] | 0.813 [0.74, 0.87] |
| per-seed AUC w1 / logit / GBM | .70 .84 .88 / .82 .86 .81 / .92 .89 .91 | .74 .63 .62 / .74 .83 .79 / .80 .85 .81 |
| seed SD of w1 AUC | 0.093 | 0.055 |
| logit − w1 (paired bootstrap 95 %) | +0.032 [−0.04, +0.105] | +0.136 [+0.074, +0.196] |
| GBM − logit | +0.078 [+0.035, +0.129] | +0.026 [−0.012, +0.067] |
| w1 50 % point (all seeds; per seed) | −9.8 (−10.6, −9.7, −10.2) | **−19.1** (−19.1, −18.7, −19.4) |
| top standardised logit coefficients | term size −1.51, w1 +1.23, total +0.83, worst=box:neg −0.58 | term size −0.91, worst=box:neg −0.70, n<−4 −0.64, worst=bycontra +0.56 |
| GBM permutation importance (AUC drop) | term size .128, total .072, kind .031, w1 .027 | term size .143, kind .051, total .027, w1 .012 |
| raw single-feature AUC: w1 / term size / total / own inference count / my full Lean size | .811 / **.840** / .845 / .787 / .625 | .690 / **.797** / .731 / .782 / .672 |
| solve rate, term size ≥ 9 vs < 9 | 38 % (n 125) vs 97 % | 35 % (n 162) vs 88 % |

- **"One worst-step threshold suffices" (pre-registered rule):** it fails in both caps. In c12, logit − w1 = +0.032 is
  just over 0.03 (its interval includes 0, but the rule needs the point estimate below 0.03) and GBM adds +0.11. In c6
  the difference is +0.136, with its interval excluding 0.03.
- **w1 is not the top feature.** Term size is, in both models and both caps. w1 in c6 is weak (AUC 0.65, below the
  expected 0.75–0.88).
- **Term-size definition.** The term-size result holds with the project's inference-node size and with my independent
  inference count (0.79 / 0.78). It does not hold with a full expression size (0.63 / 0.67).
- **Transfer,** trained on all of one source and tested on the target. The "disjoint" row trains on theorem folds ≠ f
  and tests on fold f.

  | | w1 | logit | GBM |
  |---|---|---|---|
  | c12 → c6 (same theorems; disjoint) | 0.690; 0.684 | 0.812; 0.786 | 0.829; 0.801 |
  | c6 → c12 | 0.811; 0.756 | 0.891; 0.876 | 0.897; 0.843 |
  | c12 → rfc p1600 (n 703, 519 pos) | 0.774; 0.770 | 0.863; 0.823 | 0.841; 0.821 |
  | c12 → rfc p5000 (509, 411) | 0.742; 0.735 | 0.846; 0.812 | 0.860; 0.827 |
  | c12 → rfc p12000 (425, 321) | 0.691; 0.685 | 0.866; 0.830 | 0.905; 0.859 |
  | c12 → rfc p16000 (323, 223) | 0.703; 0.697 | 0.850; 0.819 | 0.858; 0.811 |

  - Own-start w1 50 % points (rfc): −13.0, −16.0, −15.8, −11.7.
  - The c12 and c6 50 % points differ by 9.3 nats, which is "≥ 1.5 nats" by a wide margin.
  - The c12 → c6 logit AUC drop (0.826 → 0.786–0.812) is within 0.05.
  - The pre-registered "AUC ≥ 0.70 at p5000–p16000, lower at p1600" holds for the full models. It does not hold for
    w1 alone: p1600 is the *highest*, and p12000 / p16000 sit at ≈ 0.69–0.70.
- **x1 robustness** (`rv/q1_x1.json`). The same conclusions hold:
  - c12: w1 0.771, logit 0.796, GBM 0.829.
  - c6: w1 0.659, logit 0.775, GBM 0.783.
  - Term size is still the top permutation feature in both.

### Q2: hard steps (`review_oa/q2.py`)

A hard step is a reference-proof step with log p < −4 at r0 (pend; rfc: the start). Classes come from my own
classifier.
- **Never solved:** not solved by any x0 or x1 read in r1–r8 (rfc: r2, r4, r8 only).
- **Solved:** the complement. **B:** r0 x0 unsolved and r8 x0 solved.
- Δ = lp(r8) − lp(r0).

| | c12 | c6 | rfc |
|---|---|---|---|
| hard steps | 711 | 1,438 | 5,093 |
| top classes | and_proj 177, box:neg 147, app 107, box:imp 74, or_intro 50, false_elim 49, box:orelim 48, and_intro 39 | and_proj 311, app 298, box:orelim 191, box:neg 185, or_intro 138, box:imp 131, and_intro 79 | and_proj 1208, app 1116, box:neg 686, box:imp 672 |
| box openers + ∧-proj share | **64.7 %** | **59.5 %** | 58.9 % |
| never-solved hard steps; median Δ (per seed) | 169; **+2.55** (1.36, 3.06, 3.09) | 441; +4.39 (5.38, 4.24, 3.91) | 1,511; +3.14 |
| classes beating matched control by ≥ 0.5 nats | 6/8 | 9/12 | 7/11 |
| Spearman across classes, never-solved vs solved median Δ (n classes ≥ 5 never-solved steps) | 0.09 (p 0.87, 6) | 0.50 (p 0.17, 9) | 0.10 (p 0.78, 10) |
| partial R² of class in Δ ~ lp0 + class: never-solved; all hard steps | 0.25; 0.11 | 0.38; 0.23 | 0.34; 0.16 |

Per-class median Δ in solved theorems, with mean (per-seed medians):
- **c12:**
  - and_proj +2.49 (2.79; 3.69, 2.65, 1.57)
  - box:neg +1.01 (1.25)
  - app +1.48 (1.16)
  - box:imp +3.52 (2.74)
  - or_intro +1.54 (2.05)
  - false_elim +0.72 (0.76)
  - **box:orelim −0.76 (−0.65)**
  - and_intro +2.40 (3.13)
- **c6:**
  - and_proj +6.05
  - app +5.03
  - box:orelim +4.19
  - **box:neg +2.94 (mean 2.30; seeds 4.47, 3.12, 1.20)**
  - or_intro +4.97
  - box:imp +5.67
  - and_intro +5.67
  - false_elim +4.40
  - bycontra +5.49

**box:neg does not move.** Its median log p by round, r0 → r8, is:
- c12: −7.33 → −6.88
- c6: −9.36 → −9.25
- rfc: −7.58 → −8.28

In never-solved theorems, box:neg trails its matched controls by −3.6 (c12), −6.4 (c6) and −4.8 (rfc) nats. It is the
largest never-solved class in every run (80/169, 127/441, 452/1,511). c12 box:orelim also falls in solved theorems.

Pre-registered expectations:
- ≥ 60 % share: holds for c12. c6 is 59.5 %, a miss by 0.5 pp.
- Every class with ≥ 20 hard steps gains > +2 (c12) / > +4 (c6) in solved theorems: misses. c12 box:neg, app,
  or_intro, false_elim and box:orelim fall short; c6 box:neg falls short.
- Never-solved median < +1.5 (c12): misses (+2.55).
- Matched-control rule: holds (≥ half the classes).
- Partial R² ≥ 0.05: holds.
- Spearman > 0.4: misses for c12 and rfc. c6 is 0.50, but not significant.

**Gallery rule.** The six most frequent classes, pooled c12 + c6, are and_proj, app, box:neg, box:orelim, box:imp and
or_intro. This matches `artifacts/oa/gallery.json`'s `classes`. Taking the per-theorem mean class gain over seed-0 B
theorems, my median picks agree with the executor's for:
- c12 app / box:imp / box:orelim / or_intro
- c6 or_intro

They differ for c12 and_proj and box:neg, and c6 and_proj / app / box:neg / box:orelim / box:imp. The candidate counts
mostly agree (23, 7, 9, 4, 1; c6 45 vs my 46, 28 vs 29, 18 vs 19, 32, 19, 12). So the difference is in how a theorem's
gain is defined when it has several steps of the class (see phase 2).

### Q3: entropy and diversity (`review_oa/q3.py`; entropies from the pod's `artifacts/oa/entropy/*.json`)

**On-policy token entropy at T 0.8, r0 → r8:**

| ladder | r0 | r1 | r8 | drop | monotone |
|---|---|---|---|---|---|
| c12 s0 | 0.0464 | 0.0349 | 0.0365 | 21 % | no |
| c12 s1 | 0.0500 | 0.0369 | 0.0389 | 22 % | no |
| c12 s2 | 0.0489 | 0.0378 | 0.0374 | 23 % | no |
| c6 s0 | 0.0373 | 0.0314 | 0.0360 | **3 %** | no |
| c6 s1 | 0.0460 | 0.0320 | 0.0343 | 25 % | no |
| c6 s2 | 0.0398 | 0.0322 | 0.0334 | 16 % | no |

- All of the drop happens at r0 → r1. Entropy then rises slowly in 5/6 ladders.
- Pre-registered "monotone in ≥ 5/6, ≥ 30 % drop": misses (0/6 monotone, 0/6 at ≥ 30 %).
- rfc (r0, r2, r4, r8): the drop is 20–59 %, largest from p1600, and all of it falls in r0 → r2.

**Teacher-forced entropy on the reference proofs, T 1.0.** Hard steps (lp < −4 at r0) fall far more than easy steps.
In c12 s0 hard steps go 0.113 → 0.045 while easy steps go 0.042 → 0.021 → 0.036. In c6 s1 hard steps go
0.139 → 0.041. Holds.

**Cui fit.** R = −a·e^H + b. The pre-registration does not say which accuracy pairs with which entropy:
- Pairing A: H of checkpoint r with `round_{r+1}.json`'s `target_sample_acc`, which is sampled *by* checkpoint r.
- Pairing B, the literal reading: H(r) with `round_r`.

| ladder | R² (A) | b − a (A) | acc r8 | R² (B) | R² on x1 pass@1 | b − a (pass@1) | pass@1 r8 |
|---|---|---|---|---|---|---|---|
| c12 s0 | 0.82 | 2.15 | 0.92 | 0.78 | 0.75 | 1.87 | 0.72 |
| c12 s1 | 0.86 | 2.06 | 0.92 | 0.31 | 0.81 | 1.73 | 0.70 |
| c12 s2 | 0.93 | 2.18 | 0.92 | 0.04 | 0.90 | 1.92 | 0.73 |
| c6 s0 | 0.18 | 1.82 | 0.90 | 0.58 | 0.04 | 1.04 | 0.68 |
| c6 s1 | 0.74 | 2.08 | 0.90 | 0.41 | 0.65 | 1.60 | 0.65 |
| c6 s2 | 0.85 | 2.68 | 0.89 | 0.04 | 0.74 | 2.09 | 0.63 |

- Under pairing A, R² ≥ 0.8 holds in 4/6 ladders. Under B it holds in 0/6.
- b − a, the predicted R at H = 0, is 1.8–2.7: an accuracy above 1, never within 0.1 of r8.
- The fits are driven by one point. The entropy range after r1 is ≈ 0.003 nats, so a and b are ≈ 30–60 and
  ill-conditioned.

**Diversity.** Median distinct accepted proofs per group-A theorem (x0) rise every round in every ladder. They peak at
r7–r8 and never fall: c12 s0 runs 7 → 66, c6 s0 runs 2 → 21.

**Collapse vs stall.** Collapse means falling below 50 % of the maximum *after* the peak. It never happens (0/6). Stall
rounds (cumulative group-C solves, x0 ∪ x1) are 5, 7, 8 (c12) and 5, 8, 6 (c6). C solved by r8: 10/36, 8/35, 9/28 and
7/52, 7/52, 13/60. So "collapse ≤ stall in ≥ 4/6" misses: no diversity collapse, as in `trajectory`.

**Measurement facts.**
- 111 entropy checkpoint files.
- Peak memory 12.1–22.6 GB at batch 2,048.
- On-policy action truncation is above 0.1 % of *attempts* in 42/111 checkpoints: up to 3.5 % at c12 s0 p1600,
  c6 s1 pend and c12 s1 p5000.
- The per-action `trunc_rate` is above 0.1 % in 14/111.
- Truncated actions (up to 512 tokens) are included in the token mean, so r0 entropies, where truncation
  concentrates, may be inflated. This is a caveat on the size of the r0 → r1 drop.

### Compute (derived from the pod outputs)

| | value |
|---|---|
| on-policy entropy | 111 checkpoint jobs, Σ `secs_onpol` + `secs_tf` = 7,165 s on A40, 92.6 M tokens generated (4,096 attempts per checkpoint) |
| pods | 2 × A40, 1.90 pod-h, $0.93 |
| training | none |

## §Comparison (phase 2: `run_organism_analysis.md`, `organism/ANALYSIS.md`, `numbers.md` § organism-analysis, `log.md`)

**The main source of disagreement is the theorem set.**
- **The cause.** The executor's loader (`oa_load.ref_inputs`) reads `tj/targets/targets_s0.jsonl`. That file holds 307
  references. It predates the 8 references that `trajectory` added later (`new8`): textbook theorems with term size
  11–16.
- **The write-up's reason is wrong.** It says "307 replay in the environment". In the scorer's own `targets.jsonl`, all
  315 have `replay_ok` and `lean_ok`, under every seed and run, and my Lean re-check accepts all 315. The 8 were dropped
  by a file choice.
- **These theorems are mostly never solved.** 74 of their 82 c12 hard steps and 144 of 156 c6 hard steps are in
  never-solved theorems. Adding them raises c12's never-solved theorems from 10–15 to 16–22 per seed.
- **The executor's arithmetic is right.** With my own code restricted to the executor's 307 theorems, I reproduce their
  numbers:
  - Q1: c12 223 units, w1 / logit / GBM 0.757 / 0.767 / 0.871 vs 0.765 / 0.774 / 0.872, 50 % point −10.54 vs −10.5;
    c6 −21.6 vs −21.6.
  - Q2: 629 / 1,282 hard steps; matched app +7.22, →I +6.45, ¬I −6.79 / −7.56; ρ 0.80 over 4 classes and 0.39 over 7.
  - ¬I medians −7.17 → −6.41 and −9.34 → −8.82; ¬¬X split +0.90 / −1.46 with per-seed −0.67 / −2.12 / −0.76.

  The table therefore gives my 315-theorem value, with the 307 value where it differs.

| claim (executor) | my value | verdict |
|---|---|---|
| "Of their reference proofs … 307 replay in the environment" | 315/315 replay and are Lean-accepted; 8 omitted by loader file choice | **wrong; reword and rerun on 315** |
| Q1 c12 CV AUC w1 / logit / GBM 0.765 / 0.774 / 0.872; n 223 | 315: 0.794 / 0.826 / 0.904, n 246 (307: 0.757 / 0.767 / 0.871) | reproduces on 307; differs by +0.03–0.05 on 315 |
| c6 0.634 / 0.754 / 0.805; n 477 | 315: 0.651 / 0.787 / 0.813, n 501 (307: 0.601 / 0.751 / 0.791) | reproduces in substance |
| "One worst-step threshold suffices only at cap 12 … (by the pre-registered rule)"; run summary "works about as well as any model" | rule: logit − w1 = +0.032 on 315 (fails; needs < 0.03), +0.010 on 307 (passes). GBM − w1 = +0.11 on both sets; seed SD of c12 w1 AUC 0.09 (MDD ≈ 0.09–0.15, executor's own table) | **not supported as stated.** The rule's 0.03 margin sits far inside the MDD, and its verdict flips with 8 theorems. Say "at c12 no model beats w1 resolvably at n = 3 (GBM +0.10, inside MDD); at c6 and the early starts they do" |
| Cap 6 / early starts: multi-feature models add 0.10–0.16 AUC | c6 logit +0.136, GBM +0.162; rfc starts logit 0.85–0.87 vs w1 0.69–0.77 | reproduces |
| Top feature = reference term size, by coefficient and permutation importance | term size is first in both models in c12 and c6 on 315, 307 and x1 | reproduces; holds with an independent inference count (AUC 0.79 / 0.78), not with a full expression size (0.63 / 0.67). Name the measure ("inference nodes") |
| P(solve) 0.80–1.0 at term size ≤ 8, 0.39–0.47 at ≥ 9 | 315: 0.97 / 0.88 / 0.91 vs 0.38 / 0.35 / 0.41 (c12 / c6 / rfc) | reproduces in substance (≥ 9 band 0.35–0.41 on 315) |
| POST HOC reductio ∧ size ≥ 9 → P 0.31 / 0.22 / 0.26 | not recounted | labelled post hoc ✔ |
| 50 % point −10.5 (c12) vs −21.6 (c6): calibration does not transfer | 315: −9.8 vs −19.1; 307: −10.5 vs −21.6 | reproduces (gap 9–11 nats) |
| c12 → c6 logit 0.766, GBM 0.791; c12 → rfc logit 0.78–0.80 at every start | 307, fold-disjoint: 0.747 / 0.773; rfc 0.76–0.78. 315: 0.786 / 0.801; rfc 0.81–0.83 | reproduces (±0.03) |
| "Lower AUC at p1600" missed (0.80) | p1600 is among the highest by w1 (0.77) and logit | reproduces the miss |
| Hard steps 629 / 1,282 / 4,585; box + ∧E 65 / 60 / 59 % | 315: 711 / 1,438 / 5,093; 64.7 / 59.5 / 58.9 % | reproduces on 307. On 315 the c6 share is 59.5 %: the "≥ 60 %" hit is a 0.5 pp miss |
| c6 →I / app / ∧E / ∨I rise 6–7 nats, mostly r1–r2 | class medians r0 → r8: →I −6.8 → −0.5, app −7.2 → −1.1, ∧E −8.7 → −2.9, ∨I −8.9 → −1.3; most of it by r2 | reproduces |
| ∨E boxes fall at c12 (−5.2 → −6.8) | −5.34 → −7.05 | reproduces |
| ¬I boxes do not move (c12 −7.2 → −6.4; c6 −9.3 → −8.8) | 315: −7.33 → −6.88; −9.36 → −9.25; rfc −7.58 → −8.28 | reproduces (stronger on 315) |
| POST HOC ¬¬X boxes: c6 −1.46 (−0.67 / −2.12 / −0.76), c12 +0.9; others +4.3 / +2.4 | own parse, 315: c6 −1.50 (−0.39 / −1.66 / −1.75), c12 +0.15 (−3.05 / +0.97 / +1.38); others +4.3 / +2.7 | reproduces. The c6 3/3-seed sign holds on 315. Labelled post hoc ✔ |
| ¬¬X = 48.3 % / 36.1 % of RL training negation boxes | arithmetic in `q2_exposure_stdout.txt` consistent; the counts (pod, EI mixes) were not recounted | not re-derived |
| Never-solved hard steps still gain (+0.5 / +2.8 / +3.4 c12; +4.5 / +2.9 / +3.0 c6, per-theorem medians) | per-step medians on 315: c12 +1.36 / +3.06 / +3.09, c6 +5.38 / +4.24 / +3.91 | reproduces in direction; the c12 s0 value is small in both |
| Class partial R² 0.12 / 0.37 (c12), 0.18 / 0.35 (c6) | 315, without the seed term: 0.11 / 0.25, 0.23 / 0.38 | reproduces (≥ 0.05) |
| Matched controls: app +7.2 / +3.2, →I +6.5 / +3.4, ∨I +1.9 / +6.5; ¬I −6.8 / −7.6 | 315: app +2.1 / +2.8, →I +2.5 / +3.1, ∨I +3.0 / +4.8; ¬I −3.6 / −6.4 | **sign reproduces, size does not.** The c12 values are 2–3× smaller once the 8 omitted (mostly never-solved) theorems are in. The c12 app / →I cells rest on 6–7 steps on 307 |
| Cross-class ρ 0.80 (c12, 4 classes) = hit; c6 0.39 = miss | executor definition (rl-solved vs never, ≥ 5 each), 315: c12 0.90 (5 classes), c6 0.40 (8). With "solved" including group A: 0.09 / 0.50 | "hit" stands only under the rl-solved definition and on 4–5 classes (ρ over 4 points has p ≈ 0.2). Report n and that it is not resolved |
| Entropy drops 16–30 % at r1, then flat (c12) or rising (c6); r0 → r8 −21…−24 % (c12), −3.5…−25 % (c6) | r0 → r1: 25 / 26 / 23 % and 16 / 30 / 19 %; r0 → r8 21–23 % and 3–25 % | reproduces exactly (same pod files) |
| Hard-step TF entropy falls more than easy-step | c12 s0 hard 0.113 → 0.045, easy 0.042 → 0.036 | reproduces (my levels differ: 315 and mean vs the executor's median) |
| **Cui fit: "R² ≥ 0.8 in ≥ 4/6" missed (3/6)** | the executor's own `q3_entropy_stdout.txt`: 0.815, 0.864, 0.931, 0.179, 0.743, 0.851, which is **4/6** ≥ 0.8; mine identical (pairing ckpt r with `round_{r+1}`) | **miscounted.** By the letter the expectation is a hit. The executor's substantive point stands: the fit rests on the r0 → r1 jump, and b − a = 1.8–2.7 is impossible |
| Within-RL (r1–r8) fit: a < 0 in 5/6 | executor's stdout: a = −52, −38, +33, −25, −30, −23 | reproduces |
| Diversity rises every round; no collapse, so no collapse before stall; stall rounds 5 / 7 / 8, 5 / 8 / 6 | raw distinct per A-theorem: c12 7 / 12 / 9 → 66 / 70.5 / 70, c6 2 / 2 / 2 → 21 / 15 / 12; no collapse in any ladder; stall rounds identical | reproduces |
| "action truncation ≤ 0.67 %" | that is per action. Per attempt: > 0.1 % in 42/111 checkpoints, up to 3.5 % (c12 s0 p1600, c6 s1 pend) | reword. Truncated actions enter the token-mean entropy, mostly at r0, so the r0 → r1 drop may be overstated |
| Compute 6,991 A40 GPU-s, 92.6 M tokens, 1.90 pod-h, $0.93; registry rows | Σ job secs 7,165 s (incl. TF passes); 92.6 M tokens; pods.log / podhours.log agree; registry rows under `artifacts/organism-analysis/registry/` | reproduces (2.5 % accounting difference) |
| Model labels | every section names c12 / c6 / rfc with checkpoint family, 9.56 M, `lean_staten`, from scratch, training set | ✔ |
| Gallery: 15 examples by the pre-registered median rule | same 6 classes; the code takes each theorem's *worst* hard step of the class, then the lower median. My per-theorem mean gives different picks for 7/15 | a reasonable reading of the rule; state it in `gallery.md` |
| Expectations before the run | pre-registration committed 6 min before the first pod; misses reported as misses (except the Cui count, which is reported as a miss but is a hit) | ✔ |

## §Verdict

**What stands.**
- **Q1, rankings.** Term size of the reference (inference nodes) is the strongest single predictor of "solved at r8"
  in both caps. The worst step alone is weak at cap 6 (AUC 0.60–0.65). The 50 % point of the worst step does not
  transfer between caps (≈ −10 vs ≈ −19 to −22 nats), while rankings do transfer (AUC 0.75–0.83 across caps and starts).
- **Q2, the immovable class.** ¬I boxes are the one class whose hard steps do not move under EI in any run. The
  post-hoc ¬¬X split falls in 3/3 c6 seeds on both theorem sets.
- **Q2, transfer by class.** Hard steps in theorems RL never solved still gain, and class explains part of the gain.
- **Q3.** On-policy entropy falls once, at r1, and then flattens or rises. The Cui fit is degenerate. Distinct accepted
  proofs per theorem rise every round with no collapse.
- **Process.** Every Lean re-check I ran passed (915 proofs and controls). There are no hard-constraint violations.

**Must be reworded.**
1. "307 replay in the environment" is false. All 315 replay and are Lean-accepted. Rerun Q1/Q2 on 315, or say that 8
   large, mostly never-solved theorems were left out by a loader file.
2. Q2 matched-control magnitudes at c12 (app +7.2, →I +6.5, ¬I −6.8) fall to +2.1 / +2.5 / −3.6 on 315. Quote the
   signs, or the 315 values.
3. "One worst-step threshold suffices at cap 12 / works about as well as any model". The pre-registered rule passes on
   307 (+0.010) and fails on 315 (+0.032), and its 0.03 margin is inside the MDD (0.09). Say it is **not resolved** at
   c12. The finding is that at c6 and the early starts the extra features do help.
4. The Cui "R² ≥ 0.8 in ≥ 4/6" expectation was met by the letter (4/6, by the executor's own numbers), not 3/6.
   Correct the count and keep the degeneracy caveat.
5. The c12 cross-class ρ "hit" (0.80) rests on 4 classes and on the rl-solved definition. Report it as unresolved.
6. "Truncation ≤ 0.67 %" is per action. Per attempt it is up to 3.5 %, so caveat the r0 entropy level.
7. On 315, c6's box + ∧E share is 59.5 %, so the "≥ 60 %" expectation is a narrow miss there.

**Not supported.** Nothing beyond the items above. The post-hoc reductio and ¬¬X findings are correctly labelled as
hypotheses.

**Next measurement.**
- Rerun `oa_q1_models.py` / `oa_q2.py` with the 315-target `targets.jsonl` from the scorer, not
  `tj/targets/targets_s0.jsonl` (minutes on the VPS, no GPU).
- For the one open Q1 question (does anything beat w1 at c12?), use more seeds, or pool c12 + rfc p16000 as a
  within-model replicate. At n = 3 the MDD (≈ 0.09–0.15 AUC) is larger than any plausible gain.
- The ¬¬X hypothesis needs a pre-registered test: a held-out set of ¬¬-introduction theorems scored across a fresh EI
  ladder, or a ladder with ¬¬X boxes up-weighted.
