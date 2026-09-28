# Review — run `ckpt-avg`

Reviewer: agent:claude (role reviewer), independent session. Phase 1 was done in `~/review/ckpt-avg`, a copy of
the run with the executor's write-ups removed (no `run_ckpt_avg.md`, `numbers.md`, `log.md`, `STATUS.md`), and I did
not open the executor's derived `summary.json`, `tables.txt` or `redraw.json`. All code is mine, in `review_ca/`,
and reads only per-theorem evaluation rows, checkpoints, the half-A loss file and the data. Judge: **Lean alone**
throughout; `nd_verify` is not called anywhere.

**Model label for every number below**, unless a line says otherwise: run `stage1-dynamics`' checkpoints, a
3,214,336-parameter GPT (4 layers, d 256, 8 heads), **from scratch**, `lean_seq`, **cap 6**, WSD schedule.
- **Arm W**: seeds 0–7, trained on `data/p2/train_depth3_f0_a1.jsonl` (155,000 records; I confirmed the count on
  the bucket copy).
- **Arm F**: seeds 0–3, trained on `data/sd/train_fresh.jsonl` (572,759).
- **Arm R**: stage1-dynamics' RL-branch checkpoints, trained on the arm-W data per each `.json`'s `train_args`.

The label is read from each evaluation `.json`'s `model.train_args`: 289 W evaluations and 64 F evaluations, all
3,214,336 parameters. Accuracies are greedy decodes on **half B** (`data/ca/heldout_B.jsonl`, 2,500 theorems, 250 of
them depth-3) at batch 2,500, `max_new` 400, fast path, compaction on. I checked these settings in all 353 `.json`s.

## §Recount

### R1. Integrity of the 353 evaluations (`review_ca/recount.py`)
- 353 evaluations: the 256 stage1-dynamics checkpoints the plan uses, plus 97 averages. Each has 2,500 rows in
  half-B order, and `name`, `n_lines` and `depth3` agree row by row with `heldout_B.jsonl`.
- Every counted row (`lean_ok`) is `parsed` and has non-empty literal `text`.
- The per-slice `solved` counts in each `.json` equal my counts from the rows (len2, len6, depth3, all). **0 issues.**
- Peak GPU memory: `peak_alloc_gb` = 9.02 GB in every evaluation, at batch 2,500.

### R2. The averages are what the plan says (`review_ca/ptread.py`, `check_avg.py`, torch-free)
From the bucket I downloaded 22 stage1-dynamics checkpoints and recomputed 8 averages myself:
- W: `w_s3` A24_K2, A24_K4, A24_K8, T24_3 and T24_5.
- F: `f_s1` A24_K4 and A24_K8.
- The control `w_s0.CTRL_self19000`.

In every case, max |stored average − float64 mean of members| ≤ 1.9e-7, i.e. float32 rounding. The members are the
right steps, and they are all stable-phase (< 19,200) for A24: for example, W A24_K8 is steps 12k–19k and F A24_K8
is steps 4k–18k. Each average moves its weights up to 0.04–0.9 from its last member. The `avg_of` metadata in the
checked files matches `ca_plan.py averages`.

### R3. Split (`review_ca/splits.py`, my own class key)
My class key: premises as a set (order- and multiplicity-insensitive), atoms P/Q/R/S renamed by first appearance,
`F` kept as falsum, minimum over premise permutations.

| pair | shared renaming classes |
|---|---|
| half A ∩ half B | **0** (2,499 / 2,500 classes) |
| train W ∩ half B | **5** theorems (len 3/4/4/4/6, **0 depth-3**) |
| train W ∩ half A | 16 |
| train F ∩ half B | **30** theorems (len3 12, len4 7, len5 5, len6 6, **0 depth-3**) |
| train F ∩ half A | 36 |

Strata per half: 500 each of len2–len5, 250 len6 non-depth-3, 250 depth-3 — as pre-registered.

Every train∩eval overlap I inspected is a **premise-permutation** renaming: 21 of 21 for W, and the F examples
likewise. It is invisible to `gen.canon_key`; 0 of the 30 F overlaps share the executor-visible `key` field. This is
inherited from stage1-dynamics' data (the gap its review flagged), not introduced here, and it touches none of the
depth-3 slice. At most 30 of the 2,250 non-depth-3 rows (1.3 %), in bins that sit at 0.97–1.00, so it cannot move a
headline. It is a finding only in that the split record (`split.json`) reports A/B disjointness and says nothing
about train/eval overlap.

Note on my own first pass: my key initially treated `F` as an atom. That produced 3 spurious A/B collisions, which
I traced and fixed.

### R4. Lean re-check (`review_ca/lean_recheck.py`)
- One file per proof. My own statement builder: only the atoms that occur, `F` ↦ `False`, premises `h1..hn` in
  order. Plain `lean` (4.34, core).
- Accept = exit code 0 with no `error` and no `sorry` in the output. `#print axioms` recorded.
- Random sample (seed 4242) from the counted rows of each arm: 100 depth-3 plus 60 others.

| arm | counted pool | re-checked | Lean accepts |
|---|---|---|---|
| W (all 289 W evaluations, half B) | 627,868 | 160 (100 depth-3) | **160** |
| F (64 F evaluations, half B) | 142,423 | 160 (100 depth-3) | **160** |
| R (`ev_r`, full held-out, batch 512) | 45,678 | 160 (100 depth-3) | **160** |

- **Negative controls — the harness can fail:** 160 of 160 rejected.
  - 60 rows the executor's Lean rejected (`parsed ∧ ¬lean_ok`): all rejected here too, so the two harnesses agree
    in both directions.
  - 40 proofs paired with another theorem's statement.
  - 40 with the final `exact` removed.
  - 20 `sorry`.
- Axioms on accepted proofs: 449 use none; 31 use `propext, Classical.choice, Quot.sound`
  (`Classical.byContradiction`). None use `sorryAx`.
- Token whitelist: every counted text uses only the grammar's tokens (`have`, `exact`, `fun`, `Or.inl/inr/elim`,
  `Classical.byContradiction`, `⟨,⟩`, `.1`, `.2`, `.elim`, and the untyped binder `hh`). The `lean_recheck.out` line
  saying "39 violations" was from my first whitelist, before I added `hh`, `.1`, `.2` and `.elim`; re-scored, it is 0.

### R5. Half-A losses and the LS selections (`review_ca/rvload.py`, `npval.py`)
- `valloss_A.jsonl` has 353 lines, all on `data/ca/heldout_A.jsonl`. `ca_valloss.py` asserts it never reads half B.
- I re-derived two of its losses with my own numpy forward pass (fp32; the pod ran under bf16 autocast):

  | checkpoint | depth3 loss rel. diff | len6 loss rel. diff |
  |---|---|---|
  | `w_s3.step19000` | 2.3e-3 | 1.6e-3 |
  | `w_s3.step12000` | 9.3e-4 | 5.4e-4 |

  So the file holds genuine half-A losses, with ≈ 1e-3 bf16 noise.
- My argmin over each run's candidates (W: 23 trajectory checkpoints plus the E24, E12 and E6 endpoints = 26;
  F: 11 + E24 = 12) picks these:

| run | LS6 pick | LSd3 pick | LSd3 margin to 2nd |
|---|---|---|---|
| w_s0 | step14000 | step14000 | 4.2 % |
| w_s1 | E24 | E24 | 2.2 % |
| w_s2 | E24 | **step04000** | **0.24 %** (2nd = E24) |
| w_s3 | step20000 | step20000 | 3.0 % |
| w_s4, w_s5, w_s6 | E24 | E24 | 4.3 / 13 / 18 % |
| w_s7 | step22000 | step22000 | 5.7 % |
| f_s0 | E24 (margin 0.41 %) | step20000 | 3.5 % |
| f_s1 | step08000 | **step08000** | **0.08 %** (2nd = step06000) |
| f_s2 | step12000 | step12000 | 70 % |
| f_s3 | step22000 | step22000 | 2.4 % |

Two LSd3 picks (w_s2, f_s1) and one LS6 pick (f_s0) are inside the bf16 noise of the loss itself (≈ 0.1–0.2 %). A
recomputation at another precision could flip them.

Flipping w_s2 to E24 would move W LSd3's depth-3 mean by +0.0095 and make LSd3 identical to LS6 on arm W. It does
not change the adoption verdict below, because LS6 also fails (i).

Loss selection does not track accuracy at the per-checkpoint level. `w_s3`'s loss-minimising step20000 solves 0.304
of depth-3; its neighbours step21000 and step16000 solve 0.816 and 0.832, and their losses are 1–3 % higher.

### R6. Per-variant results, half B (`recount.out`)
Mean / across-seed sd (ddof 1). The variant set is fixed by `ca_plan.py` (`A*` = uniform averages, `T*` = averages
across the decay phase, `LS*` = loss-selected checkpoints).

**Arm W, n = 8:**

| variant | len2 | len3 | len4 | len5 | len6 | depth-3 | 6-line non-d3 | all |
|---|---|---|---|---|---|---|---|---|
| **E24** | .9995 | .9990 | .9925 | .9838 | .7970 / .152 | **.6160 / .306** | .9780 | .9544 |
| A24_K2 | .9977 | .9962 | .9890 | .9705 | .6370 / .172 | .3080 / .342 | .9660 | .9181 |
| A24_K4 | .9995 | .9982 | .9915 | .9752 | .6195 / .174 | .2640 / .350 | .9750 | .9168 |
| A24_K8 | .9995 | .9982 | .9928 | .9730 | .6000 / .187 | .2270 / .374 | .9730 | .9127 |
| T24_3 | .9992 | .9983 | .9932 | .9817 | .7802 / .181 | .5760 / .361 | .9845 | .9506 |
| T24_5 | .9995 | .9985 | .9935 | .9820 | .7595 / .185 | .5355 / .368 | .9835 | .9466 |
| LS6 | .9985 | .9968 | .9857 | .9723 | .8268 / .128 | .6925 / .236 | .9610 | .9560 |
| LSd3 | .9958 | .9920 | .9662 | .9557 | .8115 / .137 | .6830 / .239 | .9400 | .9443 |

**Depth-3 per seed, arm W (s0…s7):**

| variant | s0 | s1 | s2 | s3 | s4 | s5 | s6 | s7 |
|---|---|---|---|---|---|---|---|---|
| E24 | .068 | .936 | .644 | .448 | .916 | .936 | .504 | .476 |
| A24_K8 | .036 | .872 | .012 | .024 | .792 | .048 | .016 | .016 |
| T24_3 | .280 | .940 | .480 | .176 | .920 | .944 | .096 | .772 |
| LS6 | .532 | .936 | .644 | .304 | .916 | .936 | .504 | .768 |
| LSd3 | .532 | .936 | .568 | .304 | .916 | .936 | .504 | .768 |

**IQM of depth-3 over the 8 W seeds**, bootstrap over seeds, 5,000 resamples, 95 %:

| variant | IQM [95 % CI] |
|---|---|
| E24 | .635 [.38, .92] |
| A24_K2 | .207 [.03, .63] |
| A24_K4 | .112 [.02, .55] |
| A24_K8 | .031 [.02, .60] |
| T24_3 | .613 [.23, .93] |
| T24_5 | .566 [.17, .88] |
| LS6 | .715 [.50, .92] |
| LSd3 | .696 [.49, .92] |

Every interval overlaps E24's.

**Secondary W (endpoint vs averages at the shorter decay points):**

| variant | depth-3 mean / sd |
|---|---|
| E12 | .258 / .353 |
| A12_K2 | .183 / .325 |
| A12_K4 | .177 / .303 |
| A12_K8 | .068 / .144 |
| E6 | .326 / .310 |
| A6_K2 | .275 / .282 |
| A6_K4 | .115 / .127 |

The only large sd reductions (A12_K8, A6_K4) come with the mean collapsing towards 0. On `all`, A6_K4 drops to
0.77 against E6's 0.90.

**Arm F, n = 4 (secondary), depth-3 mean / sd:**

| variant | depth-3 mean / sd |
|---|---|
| E24 | .379 / .397 |
| A24_K2 | .411 / .462 |
| A24_K4 | .367 / .390 |
| A24_K8 | .326 / .352 |
| T24_3 | .412 / .467 |
| LS6 | .755 / .123 |
| LSd3 | **.737 / .092** |

- F LS6/LSd3 len6: .849 / .835, against E24's .684.
- F LSd3 per seed: .848 / .760 / .628 / .712. Its len5 is 0.9375, against E24's 0.989 (−5.2 pp).

### R7. Adoption rule (arm W, point estimates, against E24)
The rule: (i) depth-3 sd ≤ ½ of E24's; (ii) len6 sd < E24's; (iii) no bin (len2..len6, depth-3) more than 2 pp
below E24's mean.

| candidate | d3 sd ratio [F-test 95 % CI, df 7,7] | (i) | (ii) len6 sd vs .1515 | (iii) worst drop | adopt |
|---|---|---|---|---|---|
| A24_K2 | 1.12 [0.50, 2.50] | ✗ | .172 ✗ | −30.8 pp (d3) ✗ | no |
| A24_K4 | 1.14 [0.51, 2.56] | ✗ | .174 ✗ | −35.2 pp (d3) ✗ | no |
| A24_K8 | 1.22 [0.55, 2.73] | ✗ | .187 ✗ | −38.9 pp (d3) ✗ | no |
| T24_3 | 1.18 [0.53, 2.63] | ✗ | .181 ✗ | −4.0 pp (d3) ✗ | no |
| T24_5 | 1.20 [0.54, 2.69] | ✗ | .185 ✗ | −8.1 pp (d3) ✗ | no |
| LS6 | 0.77 [0.34, 1.72] | ✗ | .128 ✓ | −1.15 pp (len5) ✓ | no — fails (i) only |
| LSd3 | 0.78 [0.35, 1.75] | ✗ | .137 ✓ | −2.8 pp (len5) ✗ | no |

**No candidate meets the rule.** Every sd-ratio interval contains 1, so at n = 8 no variant is shown to change the
across-seed sd in either direction.

### R8. Pre-registered expectations, scored by me

| # | expectation | my value | verdict |
|---|---|---|---|
| 1 | every A/T within 3 pp of its constituents' mean on len2–5, overall ≥ 0.80; falsified if > 5 pp below its worst constituent | 60/96 within 3 pp; all 36 others are **above** (averages beat their members by +0.2 to +11.6 pp); 0 more than 5 pp below the worst member; overall min 0.752 (`w_s1.A6_K4`); **all 8 A6_K4 runs < 0.80** (0.752–0.780) | not falsified; the "within 3 pp" and "≥ 0.80" parts miss, in the benign direction and for A6_K4 respectively |
| 2a | A24_K8 d3 sd in [0.18, 0.35] | 0.374 | miss (just above) |
| 2b | sd ratio < 2 for A24_K2/4/8, T24_3/5 | 1.12–1.22 | holds |
| 2c | average above its constituents' mean on d3 in ≥ 6/8 W seeds | A24_K2 4/8, A24_K4 4/8, **A24_K8 2/8**, T24_3 5/8, T24_5 5/8 | **miss** — averaging does not act like lr decay here |
| 2d | below the constituents' max in ≥ 6/8 | A24_K2 5/8, K4 6/8, K8 6/8 (T24_3 4/8, T24_5 7/8) | holds for K4/K8, misses for K2 |
| 3 | LSd3 d3 mean ≥ 0.75 and sd ≤ 0.15, meets the rule; LS6 d3 sd ≤ 0.20 | LSd3 .683 / .239; LS6 sd .236 | **falsified** (sd > 0.15); mean is above E24's (.683 > .616), so the second falsifier does not fire |
| 4 | T24_3/T24_5 ≈ E24, sd ratio < 1.3 | 1.18, 1.20 | holds |
| 5 | self-average control reproduces step 19000 exactly | identical `lean_ok` **and identical text** on 2,500/2,500 rows | holds |
| 6 | arm F: LSd3 has the smallest d3 sd | .092 (LS6 .123; all others ≥ .35) | holds (n = 4) |

### R9. `max_new` truncation (pre-reg: "raise it if > 0.1 % of any stratum")
- Over all 353 × 2,500 rows, 547 rows never emitted `<eos>`: 451 depth-3, 53 len4, 17 len5, 15 len6 non-d3, 11 len2.
  The `.json`s' `hit_max_new` sums to 549; 2 rows ended with `<eos>` in the last slot.
- **241 of 2,118 evaluation × stratum cells exceed 0.1 %.** On a 250-row depth-3 slice a single truncated row is
  0.4 %.
- In the reported variants, summed over runs, the depth-3 truncations are: E24 6, A24_K2 5, A24_K4 5, A24_K8 0,
  T24_3 4, T24_5 1, LS6 10, LSd3 12.
- `max_new` was **not** raised. Instead the executor re-ran the three worst checkpoints' depth-3 slices at `max_new`
  400 / 800 / 1600 (batch 250) in `artifacts/ca/maxnew_diag/`. I recounted that diagnostic:
  - 0 of 53 main-run truncated rows become solved at any cap.
  - Solved counts are identical across 400/800/1600 (30, 1 and 0).
  - Most truncated rows stay unterminated even at 1,600 (25, 4 and 8 remain). They are degenerate loops.
- So the truncation plausibly biases nothing. But it is a **deviation from the pre-registered rule**, and phase 2 must
  check it is reported as one.

### R10. Arm R literal texts (the stage1-dynamics review's open gap)
- `artifacts/ca/ev_r/`: 10 checkpoints, full held-out file (5,000), batch 512, `max_new` 400 — stage1-dynamics'
  settings.
- Against stage1-dynamics' `artifacts/sd/ev/r*.jsonl`: **0 verdict differences in 50,000 rows**, identical per-slice
  counts, and a literal text on every one of the 45,678 counted rows. 160 of them re-check in Lean (R4).
- **The gap is closed.** The match is exact rather than within re-draw noise, consistent with the same GPU class and
  settings.

### R11. Re-draw against stage1-dynamics at the other batch
The 28 checkpoints evaluated in both runs are the endpoints. Restricted to half-B rows, 49 of 70,000 verdicts differ
(1 in 1,429) between batch 2,500 (here) and batch 512 (stage1-dynamics). The largest is `w_s7`, 9 rows. That is
within `NOISE_FLOOR.md`'s re-draw scale (≈ 1 row in 128 decodes differently; most such differences do not change the
verdict).

### R12. Proof length: lines and term size (`review_ca/termsize.py`)
My term size: parse the text, drop every type ascription, inline each `have` at its uses (unused ones vanish), and
count one node per constant or variable occurrence, `fun` binder, `⟨,⟩`, `.1`, `.2` and `.elim`. It parses all
770,291 counted proofs with 0 failures.

| arm W, depth-3 | E24 | A24_K2 | A24_K4 | A24_K8 | T24_3 | T24_5 | LS6 | LSd3 |
|---|---|---|---|---|---|---|---|---|
| inlined term size | 4.03 | 4.05 | 4.07 | 4.06 | 4.03 | 4.04 | 4.03 | 4.02 |
| `n_tok` | 161.2 | 162.5 | 156.4 | 161.0 | 160.1 | 159.3 | 164.5 | 165.7 |
| written lines | 4.02 | 4.02 | 4.02 | 4.03 | 4.02 | 4.02 | 4.02 | 4.01 |

On 6-line non-depth-3, every W variant is at 6.2 inlined / 108 `n_tok` / 5.8 lines; arm F is the same.

- **No variant changes proof length.**
- The depth-3 slice's Lean proofs are ≈ 4 written lines and ≈ 4 term nodes: a three-deep `fun` nest ending in a
  variable, against the ND label's 6 lines.
- `sd_eval`'s `n_tok` is whitespace tokens of the literal text, nearly all of it type ascriptions on this slice. It is **not**
  invariant to premise re-statement, so on its own it is not the term size the policy asks for.

### R13. Hard constraints
- `nd_verify` tree hash `9437bb72…` equals `origin/main`'s; `artifacts/TEST_RUN_DONE` blob `1d5cf064…` likewise.
- The only shared-code change from `origin/dan_stage1-dynamics` is `sd_eval.py` (+3 lines: `hit_max_new`,
  `sampler_stats`). It is output-only and does not affect the judge.
- `nd_verify`/`verify_cli` are not called by `sd_eval.py`, `lean_gate.py` or any `ca_*.py`. The executor's judge
  field is `lean_alone` in all 363 `.json`s.
- No training in this run. Selection (`ca_valloss.py`) reads half A only and asserts it. No code reads half B for
  selection.
- Pre-registration commit `1694e108` is dated 2026-09-28T04:21:40Z, and `pipeline.out`'s first line is `setup
  04:23:55Z`. The pre-registration's own text says "Written ~04:45 UTC", which cannot be right for a file committed
  at 04:21. I read it as a typo, and the gate-0 record is checked in phase 2.
- Spend: `podbudget ckpt-avg` shows 0.86 h / $0.42 against a ceiling of 4 h / $2. The GPU was an A40 (`setup.log`).
  $0.42 = 0.86 × $0.49, which looks like podbudget's $0.50/h fallback, so phase 2 checks whether the executor
  recorded the real A40 rate.

**No hard-constraint violation. No quarantine.**

## §Compare (executor's `run_ckpt_avg.md`, `numbers.md` § ckpt-avg CA1–CA5, `log.md`, `STATUS.md`)

Phase-2 checks were run with `review_ca/phase2.py`. The executor states its sd ratios as E24 / variant, the inverse
of my R7 ratios; I converted before comparing.

### Numbers

| claim (where) | my value | verdict |
|---|---|---|
| **CA1, arm W** | | |
| E24 len4/len5/len6/d3/all 0.992/0.984/0.797 (0.151)/0.616 (0.306)/0.954 | .9925/.9838/.7970 (.1515)/.6160 (.3062)/.9544 | reproduces |
| A24_K2/K4/K8 d3 0.308/0.264/0.227, sd 0.342/0.350/0.374; len6 0.637/0.619/0.600 | same | reproduces |
| T24_3/T24_5 d3 0.576/0.535 (sd .361/.368) | same | reproduces |
| LS6/LSd3 d3 0.693/0.683 (sd .236/.239), len6 .827/.811 | same | reproduces |
| sd ratios E24/variant 0.89/0.87/0.82/0.85/0.83/1.30/1.28 with F-test CIs | reciprocals of mine: 1/1.118 … 1/0.782, CIs likewise | reproduces |
| high-mode seeds (d3 ≥ 0.44): 7, 3, 2, 2, 5, 5, 7, 7 of 8 | same from my per-seed values | reproduces |
| E12/A12/E6/A6 rows, incl. A12_K8 d3 .067 (sd .144) and A6_K4 .115 (sd .127) | same (.0675/.1436, .1150/.1273) | reproduces |
| len2 ≥ 0.982, len3 ≥ 0.977 except A6_K2 len3 .958 and A6_K4 .918 | same | reproduces |
| paired d3 vs E24 (t 95 %): A24_K8 −38.9 [−63.9, −13.9], T24_3 −4.0 [−23.7, +15.7], LS6 +7.7 [−8.9, +24.2], LSd3 +6.7 [−10.4, +23.8] | identical | reproduces |
| "LSd3 costs len4 −2.6, len5 −2.8 pp" | −2.62 / −2.80 | reproduces |
| "LS6 costs ≤ 1.2 pp on every bin" | ≤ 1.15 pp on the rule's bins (len2–6, d3); **−1.70 pp on 6-line non-depth-3** (LSd3 −3.8 there) | reword: "on every bin of the rule" |
| LS picks (W and F) | identical to my argmin (R5) | reproduces |
| "Adoption rule: met by no candidate" | same (R7) | reproduces |
| **CA2, arm F (n = 4)** | | |
| E24 d3 .379 (.397); LS6 .755 (.123); LSd3 .737 (.092); ratios 3.23, 4.31 [1.10, 17.0]; LS len5 −4.5/−5.1, len4 −2.6/−2.9 | same | reproduces; see verdict on the 4.3× |
| **CA3, averages vs constituents** | | |
| "len2–len5: every average within 0.2 pp of or above its constituents' mean (min −0.2 pp, T24_3), never below its worst constituent" | min −0.20 pp (`w_s6.T24_3`, len3); 0 averages below their worst constituent on any of len2–5 | reproduces |
| A24_K8 between min and max in 6/8, above the mean in 2/8; A24_K2 4/8, K4 4/8, T24_3 5/8; F A24_K8 2/4 | 6/8; 2/8, 4/8, 4/8, 5/8; F 2/4 | reproduces |
| trajectory-mean readout: W d3 mean 0.273 sd 0.110; F 0.267, 0.127 | 0.273 / 0.110; 0.267 / 0.127 (trajectory checkpoints only, endpoints excluded) | reproduces; post hoc (see verdict) |
| **CA4, checks** | | |
| self-average control identical | identical verdicts **and** texts | reproduces |
| re-draw vs stage1-dynamics: 1,176 / 640,000 (0.18 %), depth-3 268 / 64,000 | 1,176 / 640,000, 268 / 64,000 (256 checkpoints) | reproduces. R11 first read only the 28 uncompressed files; this row supersedes it. |
| Spearman(half-A d3 loss, half-B d3 accuracy), 208 W checkpoints: −0.896 | −0.896 | reproduces |
| `max_new`: 549 hits, max 32 / 2,500 in one evaluation; diagnostic 29/26/25, 12/4/4, 11/8/8; 0 verdicts change | 549; max 32; same diagnostic counts; 0 changes | reproduces |
| peak memory 9.02 GB | 9.02 in all 353 | reproduces |
| term size of solved d3: E24 154.9, LSd3 165.6, A24_K8 137.7 "Lean tokens"; 6-line 126.8 / 131.2 | same as the mean over seeds of `sd_eval`'s per-checkpoint `n_tok` means | reproduces arithmetically; see finding F3 |
| **CA5, arm R** | | |
| 0 / 50,000 verdicts differ; slices identical; 49,983 rows with text (17 no `<eos>`) | same; 17 empty, and every one of the 45,678 counted rows has text | reproduces |
| **Cost** | | |
| A40 at $0.49/h, 0.86 h, $0.42 | `podbudget`: 0.86 h / $0.42; the real rate is recorded | reproduces |
| **Gate 0** | | |
| pre-registration committed and pushed 04:21:40Z, first pod 04:22:02Z; "~04:45" was a mis-estimate | commit 04:21:40Z; remote ref updated 04:21:42Z (reflog); `pipeline.out` setup 04:23:55Z | reproduces. Expectations were on the remote before the pod existed. |

### Wording and scope against n and evidence

- **"Uniform weight averaging makes depth-3 worse"** (run md): n = 8, paired CIs exclude 0 for A24_K2/K4/K8.
  **Stands.**
- **"and no quieter"**: the sd point estimates are 1.12–1.22× E24's, and every CI contains 1. "No quieter" is fair
  as "not shown quieter"; the data do not show it is *louder* either. **Stands.**
- **"the oscillation alternates between distinct solutions, and averaging doesn't smooth it out"**: this is a
  mechanism. Nothing in the run measures whether the checkpoints lie in distinct basins (no interpolation curve, no
  loss barrier between members). What was measured is that the average is not above its members' mean on depth-3.
  **Reword** as a hypothesis ("consistent with …"); the loss-barrier measurement below would test it.
- **"Loss-based selection helps, but not enough on W"**: the +7/+8 pp is a point estimate whose CIs span 0 (the
  run md says so in parentheses), and the sd ratio CIs contain 1. At n = 8, "helps" is not supported. **Reword**:
  "loss-based selection moves W's depth-3 mean +7/+8 pp and its sd 1.3× in the right direction; neither is
  distinguishable from 0 / 1 at n = 8."
- **"On F (n = 4), LSd3 cuts the sd 4.3× (0.40 → 0.09)"**: the F-test CI [1.10, 17.0] excludes 1, but n = 4 and
  the run labels it as secondary. One of the four LSd3 picks (f_s1: step08000 over step06000, loss margin 0.08 %)
  is inside the bf16 noise of the loss (R5). With the runner-up, that seed's depth-3 is 0.604 instead of 0.760 and
  the ratio is 3.6×. **Stands with n = 4 and "secondary" attached**; add the pick-fragility caveat.
- **"The quietest readout is the mean over a run's trajectory evaluations (depth-3 sd 0.11)"**: reproduces, but it
  was not pre-registered. A mean over 23 checkpoints is expected to have a smaller across-seed sd than any single
  checkpoint. The run already says it is "a different quantity". It should also say "post hoc", and that it costs 23
  evaluations per run.
- **Expectations summary (run md)**. Misses must be reported as misses; four sub-misses are not:
  - Exp. 1 is reported "met". Its falsifier did not fire, but the pre-registered "overall ≥ 0.80" clause misses: all
    8 A6_K4 runs are at 0.752–0.780. The "within 3 pp" clause misses in 36/96 averages, in the benign direction (the
    averages are *above* their members, up to +11.6 pp).
  - Exp. 2a (A24_K8 sd in [0.18, 0.35]) **missed**: 0.374. Not mentioned.
  - Exp. 2d ("below the constituents' max in ≥ 6/8") **missed for A24_K2** (5/8). Not mentioned.
  - Exp. 3's "LS6 depth-3 sd ≤ 0.20" **missed** (0.236). Only LSd3's miss is reported.
  - Exp. 6 (F: LSd3 has the smallest sd) **holds**. Not scored in the run md.
- **Model labels**: the run md, `numbers.md` and `STATUS.md` all carry the model label (checkpoint family, 3.2 M,
  `lean_seq`, from scratch, cap 6, training set per arm). Arm R's numbers in CA5 name their checkpoints. The
  comparison with stage1-dynamics is Lean-alone on both sides (both after 2026-09-27), so no checker-mixing label is
  needed. **No unlabelled number found.**

### Findings not in the executor's files
- **F1. LS picks inside the loss noise.** Two LSd3 picks (w_s2 0.24 %, f_s1 0.08 %) and one LS6 pick (f_s0 0.41 %)
  are separated from the runner-up by about the bf16 error of `val_bins` (≈ 1e-3 relative; R5). The W verdict does
  not depend on them. The F 4.3× does, modestly (3.6× with the runner-up).
- **F2. Train/eval overlap by premise permutation**, inherited from stage1-dynamics' data: 5 half-B theorems in train
  W's renaming classes, 30 in train F's, 0 depth-3 (R3). `split.json` documents A/B disjointness only. Impact on any
  headline is nil (≤ 1.3 % of non-depth-3 rows, all in bins at 0.97–1.00).
- **F3. Proof length.** The policy asks for lines *and* term size.
  - `numbers.md` CA4 reports only `n_tok`, calls it "Lean tokens", and says "Lines are not re-reported (`L_true`
    labels are ND-derived upper bounds)". But the model's own written lines are measured in every `.json`
    (`mean_written_lines`); they are not the `L_true` labels.
  - `n_tok` counts whitespace tokens of the literal text, nearly all of them type ascriptions. It is therefore not
    invariant to premise re-statement.
  - The 137.7 vs 165.6 gap between A24_K8 and LSd3 is a composition effect: an unweighted mean over seeds, some of
    which solve 3–4 depth-3 theorems.
  - My inlined term size is 4.02–4.07 on depth-3 and 6.2 on 6-line non-depth-3 in every variant, and lines are
    4.01–4.03 (R12). **No variant changes proof length.** That is worth one sentence in the write-up in place of
    the `n_tok` line.
- **F4. IQM not reported.** The policy asks for per-seed values plus an IQM with a bootstrap CI. Per-seed values
  and paired t-CIs are there; the IQM is not. Mine (R6): E24 .635 [.38, .92], LS6 .715 [.50, .92], A24_K8 .031
  [.02, .60]. They change no conclusion.
- **F5. `max_new` deviation** — reported, with a sound diagnostic (log.md ~04:30Z; CA4). It is not in the run md's
  summary. One line there would make the deviation visible where the headline is read.

## §Verdict

**Hard constraints: none violated.**
- `nd_verify` is unmodified and unused.
- `TEST_RUN_DONE` is unchanged.
- Nothing reads half B for selection.
- Lean alone judges, and 480/480 re-checked counted proofs are accepted, with 160/160 negative controls rejected.
- The pre-registration was pushed before the first pod.

**What stands:**
1. **No averaging or selection variant meets the pre-registered adoption rule on arm W (n = 8, half B).**
   Reproduced from the rows, the losses and my own argmin.
2. Uniform stable-phase averages (A24_K2/K4/K8) **lower** W's depth-3 by 31–39 pp (paired CIs exclude 0), and do not
   shrink its across-seed sd.
3. Averaging across the decay phase (T24_3/T24_5) is indistinguishable from E24.
4. The averages are not broken on easy bins: on len2–5 they sit at or above their constituents' mean.
5. Half-A depth-3 loss tracks half-B depth-3 accuracy across checkpoints (ρ = −0.896), yet selecting on it does not
   meet the rule. Within a run the loss minimum can be a low-accuracy checkpoint (`w_s3` step20000: 0.30, beside
   0.82–0.83).
6. The self-average control is byte-identical.
7. The re-draw rate against stage1-dynamics is 0.18 % of verdicts.
8. **The arm-R literal-text gap from the stage1-dynamics review is closed** (0 / 50,000, texts on all counted rows,
   160 of them Lean-re-checked).
9. No variant changes proof length (my inlined term size and lines).

**Must be reworded:**
- (a) "Loss-based selection helps" → "moves the mean +7/+8 pp and the sd 1.3×, neither distinguishable from no
  change at n = 8".
- (b) "the oscillation alternates between distinct solutions" → a hypothesis, not a finding.
- (c) "LS6 costs ≤ 1.2 pp on every bin" → "on every bin of the rule" (the 6-line non-depth-3 complement is −1.7 pp).
- (d) The expectations summary should list the four unreported sub-misses: Exp. 1's ≥ 0.80 clause (A6_K4), Exp. 2a
  (A24_K8 sd 0.374), Exp. 2d for A24_K2 (5/8), and Exp. 3's LS6 sd clause (0.236). It should also record Exp. 6 as
  held.
- (e) Label the trajectory-mean readout "post hoc".
- (f) Attach to F's "4.3×": n = 4, secondary, and one pick inside the loss's bf16 noise (3.6× with the runner-up).
- (g) Replace the `n_tok`-only length line with lines and an ascription-free term size (F3).
- (h) Mention the `max_new` deviation in the run md.

**Not supported:** nothing the run claims as a finding is contradicted. The mechanism sentence in (b) is the only
claim with no measurement behind it.

**Next measurements that would settle what is left open:**
1. **Loss barrier between members.** Evaluate half-A loss and half-B depth-3 along the linear path between two W
   checkpoints of opposite mode, for 2–3 seeds; for example `w_s3` step20000 (0.30) ↔ step21000 (0.82). This costs
   ~10 half-B evaluations per pair. A barrier supports "distinct solutions"; a flat path means averaging fails for
   another reason (e.g. the depth-3 behaviour is fragile under any weight change).
2. **The F 4.3× at a seed count that can see it.** The adoption question for loss selection on the fresh-data arm
   rests on n = 4. Once fast Stage-1 training is merged, 8–10 F seeds with trajectory checkpoints, and half-A losses
   recomputed in fp32 so that near-ties like f_s1's are resolved, would decide whether LSd3 meets the rule off arm W.
   Its len5 cost (−5 pp at n = 4) already fails clause (iii) as it stands.
