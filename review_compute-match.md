# Review: compute-match

Reviewer session, 2026-10-02. Run branch `dan_compute-match`. Scripts and json: `review/compute-match-recount/`
(`rlean.py` is the textbook72 reviewer's own ND → Lean 4 translator, with Lean 4.34's `error(code):` form handled; I wrote
everything else for this review).

## §Recount (phase 1, blind)

I worked from `~/review/compute-match`, with the executor's write-ups removed. I read: the brief
(`nd-rl/docs/proposals/state-env/BRIEF_compute-match.md`), `preregistration/compute-match.md` (one commit, `0e1d9fdf`,
01:31Z), the code and pod scripts, the raw artefacts (eval `*.jsonl`, ladder `found_*`, `round_*.json`, logs, registry
rows), and the K-decision commit `c72cd6e9` (its `STATUS.md` / `log.md` diff only). I did not open `summary.json`,
`analysis_stdout.txt`, `compute_stdout.txt`, `compute.json`, `log.md` or `STATUS.md`.
Comparator files: best-cap12's T1 read-outs, pulled raw from the bucket (`best-state/artifacts/bs/eval/T1_best12_s*__*.jsonl`)
and recounted the same way. Its ladder compute rows come from `origin/dan_best-state:artifacts/bs/compute.json`. The
inherited SN12 ladder counts come from the state-cap12 reviewer's `review_sc12/ladder_recount.json`.

**Models.**
- **cm12** = `la_T1_cm12k64_s{0,1,2}_r8.pt`: 3,216,384-param GPT, `lean_staten`, from scratch, Stage-1 = inherited
  `stage1_SN12_s{0,1,2}.pt` (K12 `train_k12.jsonl`, 6,000 steps × 128), then the T1 ladder at **k 64**.
- **SN12** = inherited `la_T1_SN12_s{0,1,2}_r8.pt`: same Stage-1, T1 ladder at k 32 (state-cap12).
- **best12** = best-state's `la_T1_best12_s{0,1,2}_r8.pt`: Robbie's 9.56 M recipe, Stage-1 1,200 s, same T1 ladder at k 32.

All read-outs use T 0.8, batch 2,048, `max_action` 512, `max_steps` 96. I diffed the argument files of all six reads
for cm12 against best12 and they are identical apart from paths.

### Hard constraints — all pass
- `nd_verify` tree hash `9437bb72` = `origin/main` = base. `artifacts/TEST_RUN_DONE` blob `1d5cf064` = `origin/main`. Neither
  is touched in any commit or in the staged index.
- The run's code diff is `pod/cm/*.sh`, `cm_analysis.py` and `cm_compute.py` only. `state_ladder_ei.py` and `state_train.py`
  are unchanged.
- No judge uses `nd_verify`: `lean_gate.py` does not call it. `state_env.py` imports only `parse_formula` from it, as a
  formula parser.
- No evaluation file is read in training code. `state_ladder_ei.py` reads the transfer, held-out and target pools only to
  sample and evaluate them, and it adds their keys to `eval_keys` so they are excluded from replay. textbook72, dev1108,
  holdout250, rr600 and long2 appear only in `pod/cm/read.sh`.
- The pre-registration (01:31:19Z) precedes the first pod (setup logs 01:33–01:35Z). K = 64 was committed at 02:24:03Z,
  before the s0 ladder (02:24:13Z) and the s1 ladder (02:26:47Z). Only the s2 pilot ran earlier (01:33Z), as
  pre-registered.

### Lean re-check (Lean alone decides)
1. **Solved counts, from the stored ND proofs** (`r1_evals.py`). For every target a file marks solved, I checked stored
   proofs with my own translator until one was accepted. That covers every solved target in every read: 21,072 targets
   for cm12 and the SN12 re-reads, and 20,685 for best12.
   - All are accepted except one. Held-out greedy cm12 s1 `heldout_4919` is rejected by my translator, but its literal
     text (`n5 n4` with `n5 : ¬((X) → False)`, `n4 : ¬X`) is accepted by Lean. The fault is my translator's
     argument-order heuristic, so the file's 4,885 stands.
   - No file marks a target unsolved while storing proofs for it, and no prompt differs from its pool entry.
2. **Literal sampled text** (`LEAN_GATE_DUMP`, pulled from the bucket; `r2_literal.py`). I sampled 150 gate-accepted texts
   per dump (all of them where fewer exist) across 15 dumps: tb72 and long2 for all 6 T1 checkpoints, plus dev for
   cm12 × 3. Lean accepts **2,079 / 2,079**.
   - Negative control: 600 gate-rejected texts (40 per dump), all prefilter rejections. Lean accepts **0 / 600**, so the
     prefilter dropped no valid proofs in this sample.
   - None of the accepted texts contains `sorry`, `admit`, a tactic or decision procedure, or an `exact?`-style call.
   - The prompts with an accepted text are exactly the targets the eval file marks solved, in all 15 dumps.
   - Lean imports only `propext`, `Classical.choice` and `Quot.sound`.
3. **Ladder proofs** (`r4_ladder.py`). I checked 150 random proofs from `found_8` and 150 from `found_transfer_8` per seed:
   900 / 900 accepted.

### Read-outs (Lean-recounted; per seed s0 / s1 / s2 → mean)

| quantity | best12 T1 | cm12 T1 (k 64) | SN12 T1 (k 32) |
|---|---|---|---|
| textbook72 /72 (k 256) | 52 / 51 / 52 → **51.67** | 36 / 36 / 36 → **36.00** | 36 / 40 / 36 → 37.33 (re-read here) |
| dev metric /1,108 (k 64) | 1058 / 1050 / 1055 → **1054.33** | 934 / 995 / 972 → **967.00** | 927 / 972 / 961 → 953.33 (best-state file, same settings) |
| holdout250 /250 (k 256) | 239 / 237 / 237 → 237.67 | 220 / 224 / 225 → 223.00 | 217 / 221 / 223 → 220.33 (best-state file) |
| Q = rr600 gen L_true 13–16 /380 | 377 / 375 / 376 → 376.0 | 232 / 295 / 320 → 282.33 | 227 / 293 / 317 → 279.00 (re-read here) |
| rr600 all /600 | 575 / 570 / 572 → 572.33 | 379 / 462 / 483 → 441.33 | 365 / 459 / 471 → 431.67 |
| long2 /21 | 21 / 21 / 20 → 20.67 | 11 / 11 / 15 → 12.33 | 9 / 14 / 18 → 13.67 |
| held-out greedy /5,000 | .9920 / .9900 / .9930 → .9917 | .9642 / .9768 / .9758 → .9723 | .9634 / .9756 / .9734 → .9708 (best-state file) |

textbook72 splits into dev58 + train14: cm12 28+8 / 30+6 / 30+6, SN12 29+7 / 32+8 / 30+6, best12 42+10 / 44+7 / 42+10.
holdout250 pass@1 is 0.49 / 0.59 / 0.59 for cm12 and 0.78 / 0.80 / 0.80 for best12.

### Contrasts (`recount_tables.json`; 95 % CI = bootstrap over seeds within arm, n = 3 per arm, so coarse)

| contrast | textbook72 | dev | h250 | Q | long2 | held |
|---|---|---|---|---|---|---|
| **best12 − cm12** | **+15.67** [15, 16] | **+87.3** [60.3, 119.3] | +14.7 | +93.7 | +8.3 | +.019 |
| best12 − SN12 (same settings) | +14.33 | +101.0 | +17.3 | +97.0 | +7.0 | +.021 |
| cm12 − SN12, paired per seed | −1.33 (0, −4, 0) | +13.7 (+7, +23, +11) | +2.7 (+3, +3, +2) | +3.3 (+5, +2, +3) | −1.3 (+2, −3, −3) | +.0015 |

- **Headline.** The pre-registered MDDs are 6.5 (textbook72) and 61 (dev). best12 − cm12 is beyond both, so **the
  falsifier is not met**: compute-matching our ladder does not close the gap. The dev gap's lower CI bound (60.3) sits at
  the MDD.
- **MDD design.** The MDDs were computed in `best-state` for a 3-vs-4 design. At 3 vs 3 the same pooled SD gives about
  6.9 and 65. That does not change the verdict.
- **Doubling k.** On textbook72, raising k from 32 to 64 changed nothing (−1.3, inside the MDD). On dev, cm12 is higher
  than SN12 on all three paired seeds, but +13.7 is well inside the MDD of 61. On Q, holdout250 and held-out greedy cm12
  is higher on every seed but by small amounts, and on long2 it is mixed.

### Ladder (`recount_ladder.json`; cumulative at round 8, distinct targets with a Lean-valid stored proof)

| | s0 | s1 | s2 | mean |
|---|---|---|---|---|
| cm12 targets solved /4,495 | 4,206 | 4,268 | 4,258 | 4,244 |
| SN12 (k 32, state-cap12 reviewer) | 4,171 | 4,228 | 4,215 | 4,205 |
| cm12 transfer solved /2,285 | 2,019 | 2,082 | 2,070 | 2,057 |
| SN12 transfer | 1,960 | 2,027 | 2,024 | 2,004 |
| cm12 distinct normalised target proofs | 313,348 | 428,752 | 472,126 | |

- cm12 − SN12 per seed: targets +35 / +40 / +43, transfer +59 / +55 / +46.
- Most targets are first solved in round 1 (3,719 / 3,823 / 3,791). Rounds 2–8 add 487 / 445 / 467.

### Compute (A40, 1 ladder per pod, nothing else on the GPU during the ladder)

I checked that the ladders ran alone using the read hosts and timestamps. The SN12 re-reads on the s0 and s1 pods ended
before those ladders started (02:02Z and 02:26:20Z), and the s2 pod ran only the ladder until 10:05Z.

| per ladder (8 rounds) | cm12 s0 / s1 / s2 → mean | best12 mean (best-state rows) | ratio |
|---|---|---|---|
| A40-s (Σ "round done in", log) | 27,486 / 29,222 / 30,676 → **29,128** | 28,451 | **1.02×** |
| registry gpu_seconds (sample + eval + fine-tune) | 27,485 / 29,226 / 30,675 | | matches the logs |
| attempts | 3,529,640 each (= 8 × (4,495·64 + 2,285·64 + 2,285 + 5,000)) | 1,937,800 | **1.82×** |
| gen tokens | 756.3 M / 772.8 M / 770.7 M → 766.6 M | 402.7 M | **1.90×** |
| Lean checks | 1.80 M / 2.05 M / 2.08 M → 1.98 M | 1.29 M | **1.53×** |
| train steps / tokens | 4,800 / 699–731 M (mean 720 M) | 4,800 / 732 M | 1.00× / 0.98× |

- **Matched on A40-seconds as designed; not matched on attempts, generated tokens or Lean checks.** cm12 used 1.5–1.9×
  best12's attempts, tokens and Lean checks, because the 3.2 M model samples faster. The write-up must flag this (policy:
  more than 1.25× on any quantity).
- **Pilot arithmetic.** (2,988 − 289) / (1,709 − 280) = 1.889, and 2,574 + 1.889 · 13,759 = 28,565 ≈ the committed
  28,550. The realised mean is 2.4 % above the 28,451 target.
- **Stage-1 not re-derived.** Stage-1 A40-s (2,244 / 2,250 for SN12 s2 / s3; s0 and s1 ran on RTX 3090s) are inherited
  labels, not recounted here.
- **Read-outs.** 2,602 / 2,730 / 2,826 A40-s per cm12 seed (registry `cm12k64 job` rows; 317,320 attempts =
  72·256 + 1,108·64 + 5,000 + 250·256 + 600·256 + 21·256).
- **Peak memory.** 7.7–16.9 GB per read at batch 2,048 (`peak_alloc_gb`); ladder round 1 13.2 GB.

### Cut-off fraction (policy: ≤ ≈ 0.1 % per reported stratum)
- Whole-read fractions (`truncated` + `step_cap`) are ≤ 0.05 % except **SN12 s0 tb72 at 0.168 %** (31 / 18,432) and
  **cm12 s0 h250 at 0.145 %** (93 / 64,000).
- Ladder target sampling is cut 0.05–0.08 %.
- These are the pre-registered best-state settings, so the comparison is fair. Two reads are over the policy threshold
  and should be reported with it. Per-stratum fractions are not derivable from the summaries.

### Term size (`recount_termsize.json`; shortest stored proof per solved target; term size = rule applications, excluding PR/AS/R)
- **On the targets all 9 checkpoints solve, the three arms' proofs are the same size.**
  - tb72 (28 common targets): lines 5.3 / 5.0 / 5.0 and term 4 / 4 / 4 for cm12 / SN12 / best12.
  - rr600 (289 common targets): lines 12.3 / 12.3 / 11.7 and term 7.3 / 7.3 / 7.0.
- **The gap is in which targets are solved, not in proof size.** Over all solved tb72 targets best12's median rises to
  8.8 lines / term 5.3, against 6.7 / 4.0 for cm12, because it solves longer theorems.

### Splits (`r3_splits.py`, my own renaming key: all 24 atom maps, premises sorted as a multiset)
I compared the training side (`train_k12` 154,382 classes, `rl_targets` 4,495) with every evaluation pool:
- **With premise order kept** (the project's renaming class), they are **disjoint**.
- **Order-free**, there are 29 overlaps, all premise permutations of an eval item (`recount_splits_detail.json`):
  - textbook72: 1, `textbook_3ed45280…` = (P ∨ Q), ¬P ⊢ Q (disjunctive syllogism), with `train_k12` holding ¬P, (P ∨ Q) ⊢ Q;
  - dev1108: 2 (`la_transfer_307`, also in `rl_targets`; `la_transfer_396`);
  - held-out: 22;
  - transfer: 4.
- All of this is inherited data shared by every arm, so it does not affect the contrasts.

### Smaller findings (phase 1)
1. `pod/cm/read.sh` uploads its dumps to **`best-state/artifacts/cm/dump`**, another run's bucket namespace. This is a
   copy-paste slip; the same files are also under `compute-match/artifacts/cm/dump`.
2. Registry labels:
   - The ladder rows carry `arm` = the ladder name (`la_T1_cm12k64_s0`), not `cm12k64`, except the fine-tune rows.
   - Some read rows carry `seed` 8 / 1008 / 2008 for seeds 0 / 1 / 2.
   - Aggregating by `arm` therefore splits each ladder into two arms.
3. Ladder `round_*.json`, `args.json` and registry rows have `git_sha: null`.

### Pre-registered expectations vs recount (for phase 2)
| expectation | recount | |
|---|---|---|
| cm12 textbook72 40 (37–44) | 36.0 | miss (below range) |
| cm12 dev 975 (950–1,010) | 967.0 | hit |
| cm12 holdout250 224 (218–230) | 223.0 | hit |
| cm12 Q 330 (300–360) | 282.3 | miss (below range) |
| cm12 long2 16 (12–20) | 12.3 | hit (at the edge) |
| held-out greedy ≈ 0.975 | 0.972 | hit |
| cm12 − SN12 textbook72 +2.5 (0 to +6) | −1.3 | miss |
| cm12 − SN12 dev +25 (0 to +60) | +13.7 | hit |
| ladder cumulative ≈ 4,260 | 4,244 | close |
| best12 − cm12 ≈ +12 tb72 (≥ 6.5) and ≈ +80 dev (≥ 61) | +15.7, +87.3 | hit (gap stays) |
| K 56 or 64 | 64 | hit |

## §Compare (phase 2)

I read `run_compute_match.md`, `numbers.md` § compute-match and `log.md` § compute-match after committing §Recount
(`08fd1236`).

**Disclosure.** Before that commit, `git log` showed me the executor's DONE commit subject ("k 64 ladders (1.02x best12
A40-s)"). I had already derived 1.02× from the logs.

| claim (write-up / numbers) | my value | verdict |
|---|---|---|
| per-seed textbook72, dev, holdout250, Q, long2, held-out greedy for best12 / cm12 / SN12 (both tables) | identical, every cell (Lean-recounted from the raw files, best12 from the bucket) | reproduces |
| best12 − cm12: textbook72 +15.7 [+15.0, +16.0], dev +87.3 [+61.0, +119.3] | +15.67 [15, 16], +87.3 [60.3, 119.3] | reproduces |
| "every best seed beats every cm12 seed" | textbook72 51–52 vs 36; dev 1,050–1,058 vs 934–995 | reproduces |
| paired cm12 − SN12: textbook72 0 / −4 / 0, dev +7 / +23 / +11, h250 +3 / +3 / +2, Q +5 / +2 / +3, long2 +2 / −3 / −3 | same | reproduces |
| ladder cumulative 4,206 / 4,268 / 4,258 vs 4,171 / 4,228 / 4,215; "+35 to +43" | same (mine from `found_8`; SN12 from the state-cap12 reviewer) | reproduces |
| ladder A40-s 27,485 / 29,226 / 30,675, mean 29,129, 1.02× best12 | logs 27,486 / 29,222 / 30,676; registry 27,485 / 29,226 / 30,675 | reproduces |
| 1.06× including Stage-1 | (29,129 + 2,247) / (28,451 + 1,288) = 1.055 | reproduces (Stage-1 values inherited) |
| attempts 1.82×, gen tokens 1.9×, Lean checks 1.4–1.6× (flagged) | 1.82×, 1.90×, 1.40–1.62× per seed | reproduces |
| best12 attempts "1,938 k (1,794 clean)" | 8 × (4,495·32 + 2,285·32 + 7,285) = 1,793,960 | reproduces |
| pilot: 2,988 s vs 1,709 s, projection 28,550 s | (2,988 − 289) / (1,709 − 280) = 1.889, giving 28,551–28,565 | reproduces |
| K = 64 chosen before s0 / s1 | commit 02:24:03Z, ladders 02:24:13Z / 02:26:47Z | reproduces |
| "Cut-offs ≤ 0.17 %" | max 0.168 % (SN12 s0 tb72), 0.145 % (cm12 s0 h250) | reproduces; see wording |
| textbook72 shortest proof: cm12 and SN12 median 7–8 lines, term size 5–6 | my definitions differ (PR lines excluded; term = rule applications excluding AS/R): 6.7 / 4.0 vs 6.7 / 4.3; on the common set they are equal | consistent; not derivable at their definition |
| spend 28.43 pod-hours, $13.93 | not derivable (podbudget) | – |
| models: 3,216,384-param `lean_staten` GPT (cm12, SN12) vs 9,560,832-param ALiBiGPT (best12) | Stage-1 md5 21d74747… for s2 in the s2 log; the rest inherited labels | labels present |

**Wording, n and expectations.**
- Every between-arm claim has n = 3 per arm, and the write-up says so. The two headline gaps are beyond the
  pre-registered MDDs. Those MDDs were computed for 3 vs 4 seeds; at 3 vs 3 they are about 6.9 and 65, which changes
  nothing.
- The pre-registration was committed before the first pod. The misses are reported (paired textbook72, cm12 Q 282 vs 330).
- The cm12 textbook72 *level* also missed (36 against a predicted 40, range 37–44). The write-up shows this only through
  the paired miss, not as its own line. Minor.
- **"Best-state's advantage comes from the recipe, not the extra GPU time" is too broad.** What was tested is extra
  *ladder* GPU time spent as more samples per round (k 32 → 64). Our Stage-1 already had more GPU time. Supported
  wording: "giving our ladder best12's GPU time, as twice the samples per round, does not close the gap. The remaining
  difference sits in the recipe (model size and architecture, Stage-1 procedure), which this run does not separate."
  Matching on GPU-seconds gave cm12 1.8× the attempts, which favours cm12, so the conclusion is conservative in that
  direction.
- **Cut-offs.** "Cut-offs ≤ 0.17 %" is accurate, but two reads exceed the policy's ≈ 0.1 % threshold, and the write-up
  does not say so. best-state's cap diagnostic shows these are non-terminating actions and that raising the caps changes
  ≤ 2 textbook72 solves. Citing it would close the point.

**Not reported by the executor (from §Recount):**
1. `pod/cm/read.sh` copies its dumps into **`best-state/artifacts/cm/dump`** in the bucket, another run's namespace.
2. Registry rows: the ladder rows carry `arm = la_T1_cm12k64_s<seed>`. `cm_compute.py` works around this and the log
   says so. Some read rows also carry `seed` 8 / 1008 / 2008; that is not mentioned. `git_sha` is null throughout.
3. Order-free renaming overlaps: 1 textbook72 and 2 dev1108 items are premise permutations of training theorems. This is
   inherited and shared by every arm, so it is immaterial here.

## §Verdict

- **No hard-constraint violation.** `nd_verify` is unmodified and judges nothing, `TEST_RUN_DONE` is unchanged, and no
  evaluation file is read in training. Every counted proof I re-checked is accepted by Lean: every solved target in all
  read files has a Lean-valid proof, 2,079 / 2,079 literal sampled texts are accepted, 900 / 900 ladder proofs are
  accepted, and the negative control rejects 0 / 600 wrongly. Splits are disjoint by the project's renaming class.
- **What stands.** Every number in the write-up and in `numbers.md` reproduces.
  - At matched ladder A40-seconds (1.02×), best-cap12 T1 still beats cm12 T1 by +15.7 textbook72 and +87.3 dev. Both are
    beyond the pre-registered MDDs, with every seed separated, so the falsifier is not met.
  - Doubling k from 32 to 64 moved nothing beyond the noise floor. The paired dev, Q and holdout250 differences are all
    small and positive; textbook72 is 0 / −4 / 0.
  - The compute table is correct, and the over-1.25× quantities are flagged.
- **Reword.**
  - The causal sentence "comes from the recipe, not the extra GPU time" should be narrowed to extra *ladder* compute as
    more samples (see above).
  - The two over-threshold cut-off reads should be flagged as such, citing best-state's cap diagnostic.
- **Fix (housekeeping).** Remove or relabel the `best-state/artifacts/cm/dump` copies, and note the registry seed labels
  8 / 1008 / 2008.
- **Next measurement.** This run cannot say which part of the recipe carries the gap. The clean next step is a 2 × 2 on
  Stage-1, one change at a time from SN12, each through the same k 32 ladder with 3 seeds:
  - our 3.2 M model on Robbie's Stage-1 procedure;
  - Robbie's 9.56 M ALiBiGPT on our K12 data and `state_train` schedule.

  Separately, a ladder that spends the extra GPU time on more fine-tune steps per round, rather than more samples, would
  test the other way to use the compute.
