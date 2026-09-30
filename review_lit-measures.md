# Review: lit-measures

Reviewer session, 2026-09-30 (UTC 03:00–). Phase 1 was done in `~/review/lit-measures` (executor write-ups removed)
with reviewer-written code (`artifacts/lit-measures/review/rv_*.py`; outputs next to them). Judge throughout: Lean
alone. No reviewer code calls `nd_verify`.

## §Recount (phase 1: written before reading run_lit_measures.md, numbers.md or log.md)

### Hard constraints

| check | result |
|---|---|
| `nd_verify/` identical to `origin/main` | yes (`git ls-tree -r` hashes equal; `git diff origin/main HEAD -- nd_verify` empty) |
| `nd_verify` used as a judge | no: no `nd_verify`/`verify_text` in `lm_*.py`, `pod/lm/*`, `tests/test_data_seed.py`; M2 held-out uses `eval_set.py` → `lean_judge` (reasons are `lean rejected` / `lean_seq parse:*`) |
| `artifacts/TEST_RUN_DONE` | unchanged against the merge base (still tracked) |
| evaluation file read in training | `train.py/fast_train.py --heldout data/p2/heldout.jsonl` is read only for validation loss (`val2k`, no grad, no checkpoint selection: every cell is the step-6,000 checkpoint). This is the noise-floor recipe unchanged, not a violation. |
| `test_run_once.sh` | not run (not in any log) |

No quarantine.

### `--data_seed` code

- The diff to `train.py` (legacy: `random.Random(a.data_seed)`) and `fast_train.py` (`plan(..., a.data_seed)`,
  `draw` seeded from `data_seed`) is correct: `torch.manual_seed(seed)` still sets the init only, and resume states carry
  `data_seed`.
- `tests/test_data_seed.py`: ALL PASS on the VPS CPU.
- My own check: `origin/dan`'s (merge-base `6b7b2f5e`) `train.py` and this branch's `train.py`, legacy, 20 CPU steps,
  `--seed 3`: bit-identical losses. So the default reproduces the old trainer exactly on CPU. On GPU the pod repro logs
  (`m2/repro/`) show `orig` vs `new` differing by about 1e-5 at step 10 and by 0.01–0.05 by step 100–300. `new`
  vs `newx` (same code, same seeds) drifts by as much, so the drift is GPU non-determinism, not the flag. The 6,000-step
  legacy `--seed 0` run ends at val 0.0724 against noise-floor's `stage1_p1_s0` 0.0729. I did not test the fast path.

### M1 (SN base s0 = `state-env/ckpts/se/stage1_SN_s0.pt`, md5 `ec3888d9…`, 3,216,384 params, `lean_staten`, from scratch, cap 6; scored proofs from SN EI s0 `la_T1_SN_s0_r8.pt` md5 `fb448247…`)

Inputs were fetched independently: support-state records from `origin/dan_support-state:artifacts/ss/`, and the
checkpoint from the bucket (md5 matches). **Sets.** Theorems SN EI solves and SN base never reaches: 52. Of those,
the ones with ≥ 200,000 base attempts at *each* temperature are exactly the 7 pre-registered (`1108 1185 1352 198
2089 394 988`). I rebuilt C1 with my own sampler (per `L_true`, `random.Random(0).sample` of sorted candidates,
5 per S theorem). It gives the same 35 theorems as the executor. Proof counts are S 91, C1 466, C2 86, and the
(set, name, proof) triples are identical to `m1/steps.jsonl`.

**Scoring.** I wrote my own replay and scorer (`rv_m1_score.py`). It replays in `Env(canon=True, base=b,
assign=True)` for every base b = 0…64 − max name, asserts that the environment's assigned names equal the shifted
canonical names, and records action tokens + `<eos>` log p at T = 0.8 and 1.0. I used four step-attribution variants:

| variant (T 0.8, best proof per theorem) | S labels | C1 labels | median w1 S / C1 | perm. p (one-sided) | S with w1 < ln(3/4e5) / ln(3/2e5) |
|---|---|---|---|---|---|
| executor's: log **Σ** over all bases (0…64−mx), name tokens scored | 7 conc. | 12 conc., 23 mixed | −14.71 / −1.56 | 0.0002 | 5/7 / 5/7 |
| sampler mixture: log **mean** over b = 0…32, env-overridden name tokens not scored | 7 conc. | 12 / 23 | −15.23 / −1.57 | 0.0001 | 5/7 / 5/7 |
| log mean over b = 0…32, name tokens scored | 7 conc. | 12 / 23 | −15.23 / −4.17 | < 1e-4 | 5/7 / 5/7 |
| base 0 only (the pre-registration's literal "names the environment assigns") | 7 conc. | 12 / 23 | −15.38 / −4.43 | 0.0007 | 5/7 / 6/7 |
| (T 1.0, executor's variant) | 6 conc., 1 mixed | 10 / 25 | −12.06 / −1.65 | 0.0001 | 4/7 / 4/7 |

- The executor's variant reproduces `m1/steps.jsonl` to |Δ| ≤ 1.1e-5 (total and w1, all 643 proofs, both T).
- Every E1 verdict is the same under all four variants at T 0.8. E1.1 holds (7/7 ≥ 5/7). E1.2 holds (gap 11–14
  nats ≥ 2; p < 0.001). E1.3 holds (5/7 ≥ 4/7). C1 has 2/35 below ln(3/4e5).
- Deviation to check in phase 2: the pre-registration says "no name marginalisation needed", but the executor sums
  over up to 56 bases. That is not the sampler's distribution (b ~ U[0, 32]). It approximates marginalising the name
  token the environment overrides, and my table shows the choice does not matter here.
- The worst step of all 7 S proofs is a box opener: 4 `Or.elim` openers, 2 `Classical.byContradiction` lines, and one
  `.2` projection (988).
- Part D recount (`d_summary_T08.json` `primary.rows[].w1`, whole-proof base `ckpts/lf/stage1_a1_seq_s0.pt` md5
  `9bde44c0`, `lean_seq`, 3,214,336 params): 19/29 below −11.80, 22/29 below −11.11. Labels 28 concentrated, 1 mixed.
- **Lean.** All 643 M1 proofs were re-checked. Literal `lean_text` through `lean_check --texts`: 643/643 accepted.
  ND → `nd2lean.translate(require_all_pr=False)` → `lean_check`: 643/643 accepted, and 200/200 corrupted controls
  rejected. Term size (lean_check inference nodes), median: S 10, C1 6, C2 5. The `term_size` field in the support-state
  records (medians 56 / 58.5 / 75.5), which `steps.jsonl` carries, is a different quantity. It must not be quoted as
  lean_check term size.

### M2 (64 cells: Stage-1 `lean_seq` GPT, 3,214,336 params, from scratch, cap 6, `train.py --impl fast` 6,000 × 128 on `data/nf/train_p1.jsonl` md5 `e80aaa0c`; init seeds 0–7 × data seeds 100–107; RTX 3090)

- **Recipe.** Every cell's metrics `args` were checked: seed, data_seed, `impl fast`, `lean_seq`, cap 6, 6,000 × 128,
  `train_p1`, last logged step 6,000. All 64 cells and all 8 replicates are present.
- **Depth-3 slice.** My own box-depth counter on the reference proofs gives 500 held-out theorems at depth ≥ 3, and it
  agrees with `pat.depth3` on 5,000/5,000.
- **Per-cell counts.** Solved = `solved` with a non-empty proof list, always consistent. The depth-3 grid is in
  `review/m2_recount.json`.

| quantity | mean | sd | range | init share [95 %] | data share [95 %] | residual | F-test p (init / data) |
|---|---|---|---|---|---|---|---|
| depth-3 | 0.496 | 0.305 | [0.006, 0.900] | 0.17 [0.00, 0.59] | 0.02 [0.00, 0.41] | 0.81 | 0.020 / 0.34 |
| overall | 0.913 | 0.033 | [0.852, 0.959] | 0.21 [0.00, 0.61] | 0.03 [0.00, 0.41] | 0.75 | 0.007 / 0.24 |
| val loss | 0.07262 | 0.00020 | [0.0722, 0.0731] | 0.21 [0.01, 0.55] | 0.32 [0.00, 0.67] | 0.48 | 0.001 / < 0.001 |

  Method: method-of-moments two-way random effects, one observation per cell. Intervals come from my own two-way
  bootstrap (4,000 draws, seed 12345, resampling init and data levels).
- **High mode** (depth-3 ≥ 0.5): 36/64. Row counts (init) 5 6 3 4 7 6 3 2; column counts (data) 5 5 3 3 7 4 5 4.
  Label-permutation p: rows 0.16, columns 0.61.
- **Replicates** of (init 0, data 100), 9 runs including the grid cell, identical seeds: depth-3 0.900 0.502 0.222
  0.726 0.796 0.832 0.850 0.850 0.874. sd 0.225, 8/9 high. Overall sd 0.027, val sd 0.00026. The replicate variance
  (0.051) is 0.55 of the grid's total depth-3 variance (0.093). GPU non-determinism alone produces most of the spread.
- **E-verdicts.** E2.1 (data ≥ 30 %): point estimate 0.02, a miss. The pre-registered falsifier (interval upper bound
  < 30 %) is not triggered (upper 0.41), so the result is inconclusive by its own rule, with the point estimate far
  below 30 %. E2.2 (data > init): data 0.02 < init 0.17, a miss. The intervals overlap, so the pre-registered falsifier
  is not met. E2.3: sd 0.305, range ⊇ [0.1, 0.8]; the fast path reproduces the bimodality. E2.4 (replicate sd ≥ 0.10):
  0.225, holds.
- **Lean.** 100 counted held-out proofs per cell were re-checked (half from the depth-3 slice where available): 72
  cells, 7,200 proofs, all accepted. 200/200 corrupted controls were rejected. Term size median is 3 on depth-3
  proofs and 2 on the rest (range 1–8).
- **max_new.** Samples that ended without `<eos>`: 90 of 360,000. 79 of them are on the depth-3 slice, which is
  0.22 % of 36,000 (worst cell 4/500). That is above the policy's ≈ 0.1 % threshold for a reported stratum. At most
  0.008 on one cell's depth-3 rate, so it is immaterial to the variance shares, but it is a policy miss. Peak memory is
  not in the eval logs.
- **Split.** Premise-order-sensitive renaming classes: 0 overlap between `train_p1` (154,613 classes) and
  `heldout.jsonl`. With premise order ignored, 19/5,000 held-out theorems are premise permutations of training
  theorems, none in the depth-3 slice. This data is inherited from noise-floor and shared by every cell, so it has no
  effect on the decomposition.
- **Compute.** `compute.tsv` has 73 training rows at 115–239 GPU-s (RTX 3090) plus 7 repro rows. My derivation from the
  logs agrees in form: train steps 6,000; train tokens are the logs' `useful_tokens`. Eval GPU time, gen tokens, M1 CPU
  time and M3 pod time are not rows.

### M3 (per-round found files of 111 ladders, streamed one at a time from the bucket)

I wrote my own summariser (`rv_m3_one.py`). It uses my own start-index normaliser (line labels renumbered by first
appearance), keys each proof by (name, normalised proof), keeps its earliest round, and applies my own box-depth
counter and rule counter.

- **Per-round counts.** Compared with the executor's `per_round.tsv`: 1,488 (ladder, round) cells, 1,364 identical.
  **All 124 differences are in `round3-run4b`.** Those found files store proofs at raw start indices (`N56 …`), and the
  executor counted every start-index variant as a separate proof. My raw-row count reproduces the executor's `n_new` on
  160/160 of those cells. After normalisation, for example, `ei_depth3_85M_s1_mix` has 4,377 rows but 115 distinct
  proofs, and `25Mr_s1_mix` has 14,235 rows but 479. This is the start-index-normalisation bug the policy lists. The
  depth shares of the round3-run4b arms (25M/85M-parameter models, not 3.2 M) are therefore weighted by the number of
  start-index variants in the executor's table.
- **E3.1 recomputed** (found pool, headline arms, within-arm pairs with an untied final ordering: 26 pairs, the
  executor's count too):

| round r | cumulative share (pre-registered) | same, ties not credited | share new in round r only | disjoint: rounds 1..r vs r+1..8 | frozen (no-RL) cumulative, 19 pairs |
|---|---|---|---|---|---|
| 1 | 19.5/26 = 0.75 | 18/26 = 0.69 | 0.75 | 0.56 | 0.84 |
| 2 | **19.5/26 = 0.75** | 18/26 = 0.69 | 0.56 | **13.5/26 = 0.52** | **0.89** |
| 3 | 0.85 | 0.85 | 0.65 | 0.62 | 0.89 |
| 8 | 1.00 (by construction) | | | | 1.00 |

  - The pre-registered number reproduces: 0.75 at round 2, even after deduplication. It is exactly at the threshold
    and holds only because ties count ½; strictly it is 0.69.
  - The cumulative share at round 2 is a subset of the final cumulative share, so agreement is partly built in (a
    part–whole artefact). With disjoint sets (the proofs found in rounds 1–2 against those found in rounds 3–8) the
    agreement is 0.52, which is chance.
  - The frozen ladders, which have no training at all, agree more than the trained arms (0.89 at round 2). So the
    round-2 "separation" in the cumulative statistic does not indicate RL separating modes.
  - The found_transfer pool gives 0.70 at round 2 (20 pairs).
- **Most arms have no modes to separate.** Within-arm final depth-≥3 shares differ by ≤ 0.03 in 13 of the 15
  whole-proof and state arms (e.g. ds-composition 0.607 vs 0.626). The only bimodal arms are round3-run4b's `25Mr_mix`
  (final 0.766, 0.770, 0.044) and `85Mr_mix` (0.009, 0.231, 0.760):
  - In 25Mr, the low seed is separated from round 1–2 (r2: 0.144, 0.390, 0.000).
  - In 85Mr, all three seeds are at 0.000 at round 2. They separate only at rounds 5–7 (s2: 0.048 at r5, 0.271 at r6,
    0.687 at r7).
  - The brief's question therefore gets one "by round 2" and one "only later", from two arms of 25M/85M models.
- **E3.2.** New-proof depth-≥3 share monotone (non-strict, either direction) over 8 rounds: 10/44 headline ladders. The
  "at least half" expectation misses.
- **Lean.** M3 counts found files that earlier runs judged; this run adds no new counted proofs. I did not re-check M3
  proofs in Lean. The earlier runs' reviews cover them.

## §Compare (phase 2: `run_lit_measures.md`, `numbers.md` § lit-measures, `log.md`)

Gate 0: the pre-registration was committed at `bd3b330e` 00:04:53 UTC, before the first pod (lm1 at ~00:06). M1 ran
at ~01:01 and M3 was committed at 00:40, both after it. Amendment 1 (the replicates) was committed at 00:40:07. Its text
says "~00:55", but the commit time is earlier, which is harmless. It was committed while lm2's first grid cells were
running. That no grid result had been read cannot be checked from files, but the amendment adds a read-out and changes
no hypothesis.

| # | claim (where) | independent value | verdict |
|---|---|---|---|
| 1 | S = 7 theorems the base never reaches in 400,000 attempts (run) | 7; 200,000 per temperature × 2, same 7 names | reproduces |
| 2 | M1 model label (SN base s0 `ec3888d9`, 3.2 M, `lean_staten`, from scratch) | md5 checked | reproduces |
| 3 | median worst step −14.7 nats (T 0.8), 7/7 concentrated, E1.1 ✓ (run, numbers) | −14.71 (executor's attribution); −15.23 (sampler mixture b ∈ [0, 32]); 7/7 under all 4 variants | reproduces |
| 4 | "remaining steps −1.5" (run) | median rest = total − w1 − w2 = −1.49, but w2 median is −4.63 and is left out | reproduces; **reword** ("second-worst −4.6, all others together −1.5") |
| 5 | 13 nats below C1, p 0.0002, E1.2 ✓ | 13.14, p 0.0002 (0.0001 under the sampler mixture) | reproduces |
| 6 | 4.1 nats below C1x, p 0.003; 31/35 C1x concentrated (post hoc, labelled) | from the executor's scored C1x rows (the same code reproduces to 1e-5 on S/C1/C2; I did not re-score C1x): −14.71 vs −10.59, 31/35; p not re-derived. C1x = 35 forward-crux theorems reached only in S2: checked. Lean: 728/728 C1x proofs accepted | reproduces (derived from the executor's scores) |
| 7 | E1.3 5/7 (4/7 at T 1.0); part D 19/29; 9/35 C1x below | 5/7, 4/7; 19/29 (22/29 at −11.11); 9/35 | reproduces |
| 8 | worst steps: 4/7 `Or.elim`, 2 `byContradiction` | same | reproduces |
| 9 | name base "marginalised as in part D" (log, report) | The pre-registration said "no name marginalisation needed", and the log does not call this a deviation. It also sums over b ≤ 64 − mx, where the sampler draws b ∈ [0, 32]. Every E1 verdict is unchanged under the sampler mixture and under base 0 (§Recount table) | deviation not labelled; immaterial |
| 10 | M2 shares: data 0.02 [0, 0.42], init 0.17 [0, 0.60], residual 0.81 [0.31, 0.99] | 0.02 [0, 0.41], 0.17 [0, 0.59], 0.81 [0.31, 1.00] (own bootstrap) | reproduces |
| 11 | E2.1 "not supported, not falsified" | point 0.02 against 30 %, upper bound 0.41 > 0.30 | reproduces; wording correct |
| 12 | "high mode follows neither seed" (p rows 0.16, cols 0.61) | same for the binary mode. On the continuous depth-3 rate the init F-test gives p = 0.020 (overall p = 0.007); data p = 0.34 | reproduces for the binary; **add** that the init seed has a detectable effect on the continuous rate and the data order has none |
| 13 | E2.2 (data share > init share) | data 0.02 < init 0.17, overlapping intervals: a miss, falsifier not met | **not reported** in run/numbers; must be stated as a miss |
| 14 | identical-seed re-runs 0.22–0.90, ≈ half the grid variance, E2.4 ✓ | 0.222–0.900, sd 0.225, 0.55 × grid variance | reproduces |
| 15 | E2.3 (bimodality reproduced on the fast path) | sd 0.305, range 0.006–0.900 ✓ | holds; not stated in run.md |
| 16 | legacy 6,000-step run vs noise-floor `stage1_p1_s0`: max \|Δ val\| 0.032 over steps 200–1,400 | 0.0318 at step 400; ≤ 0.0009 from step 2,000; final 0.0724 vs 0.0729 | reproduces |
| 17 | M2 model label (3,214,336, `lean_seq`, from scratch, cap 6, fast, `train_p1` `e80aaa0c`) | checked in all 72 metrics headers | reproduces |
| 18 | compute: grid 8,113 GPU-s, rep 995, repro 338; 384,000 + 48,000 steps; 360,000 Lean-judged attempts | 8,112.7 / 994.8 / 338.0; 64 × 6,000, 8 × 6,000; 72 × 5,000 | reproduces. Eval GPU-s, gen tokens, M1 CPU-s and M3 pod-s are not recorded, and there is no per-arm table in run.md (only in numbers/compute.tsv) |
| 19 | pod as nuisance factor (log 01:26) | depth-3 by pod parity: lm5 0.433 vs lm2/lm6 0.560, permutation p 0.09. It sits in the residual; the checkerboard keeps it off both factors | in the log only; **add a sentence** to the write-up |
| 20 | (not claimed) max_new | depth-3 stratum no-`<eos>` 0.22 % > 0.1 % policy line (worst cell 4/500) | **unreported policy miss**, immaterial to the shares |
| 21 | "19 EI arms, 41 seeds, 10 run families" (run) | 19 arms, 10 families, **44** seeds (numbers.md's own E3.2 denominator is 44) | differs by 3; fix |
| 22 | E3.1 = 0.75 at round 2, "met, but weakly"; new-proof share 0.56; frozen 0.89 (numbers) | 19.5/26 = 0.75 (after start-index dedup too); 0.56; 0.89. Also: ties uncredited 0.69; disjoint early vs late sets 0.52 | reproduces. The frozen 0.89 should be in run.md: it shows the cumulative statistic measures persistence of the base's style, not RL separating modes |
| 23 | per-round counts (`per_round.tsv`, all of M3) | 1,364/1,488 cells identical. **All 124 round3-run4b cells count start-index variants as distinct proofs** (my raw rows reproduce them 160/160; e.g. 4,377 rows = 115 distinct proofs) | **differs**: round3-run4b rows must be start-index-normalised |
| 24 | "EI arms whose seeds differ by > 0.05 at the end: 25Mr 0.65, 85Mr 0.54" (numbers) | deduplicated: 25Mr 0.726 (0.770 − 0.044), 85Mr 0.751 (0.760 − 0.009) | **differs** (consequence of #23); the qualitative claim stands |
| 25 | "only round3-run4b's r arms end bimodal; a seed takes off at rounds 2–3 (25Mr), 5–8 (85Mr), or never" | deduplicated trajectories agree: 25Mr s0/s1 take off r2–r4, s2 never (0.044); 85Mr s2 r5–r7, s1 r7–r8, s0 never | reproduces; **model label missing**: these are round3-run4b's 25 M / 85 M models, not 3.2 M |
| 26 | "clearer pattern is convergence": ds-generator g1/g2 seed spread 0.56 → 0.03 / frozen 0.56 → 0.51; 0.46 → 0.01 / 0.41 | g1 0.56 → 0.03 (EI) / 0.50 (frozen); g2 0.47 → 0.01 / 0.41. The low seed jumps from 0.05 to 0.62 (g1) and from 0.17 to 0.68 (g2) in one EI round | reproduces; **label post hoc** and scope it to ds-generator g1/g2 (2 arms of one family). The other arms' seeds start within ≈ 0.03 of each other, so there is nothing to converge |
| 27 | E3.2 5/44 (numbers) | non-flat increasing 4/44 after dedup (+ 6 constant-zero ladders), executor 5/44 | differs by 1 (dedup); both are **misses of E3.2** ("at least half"), which the write-up does not say |
| 28 | spend 3.75 pod-h, $1.50 + ≈ $0.05 unregistered | not independently billed; within the $3 / 6 h budget | plausible |
| 29 | deliverables | run_lit_measures.md 352 words (limit 350); STATUS line present; `--data_seed` not merged (correct: after review) | minor overrun |

## §Verdict

**Hard constraints:** clean. `nd_verify` is unmodified and on no path, `TEST_RUN_DONE` is unchanged, and no
evaluation file is used for training. No quarantine.

**Stands:**
- **M1, all three E1 expectations**, on SN base s0 (`ec3888d9`, 3.2 M, `lean_staten`, from scratch). They are robust to
  how the environment-assigned name base is attributed (four variants), and every scored proof is Lean-accepted.
- **M2:** the variance decomposition, and E2.1 "not supported, not falsified". The identical-seed replicate result is
  the most useful finding of the run: GPU non-determinism alone produces a depth-3 sd of 0.225, about 55 % of the grid's
  variance, on the fast `lean_seq` 3.2 M recipe. The `--data_seed` change is correct. The old and new trainer are
  bit-identical on CPU, and the change is fit to merge.
- **M3:** the qualitative reading. E3.1's 0.75 is on the letter only, and the round3-run4b `r` arms are the only
  bimodal ones.

**Must be reworded or added:**
- (a) M2: E2.2 is a miss (data 0.02 < init 0.17) and must be stated. Say that the init seed has a detectable effect on
  the continuous depth-3 rate (F p = 0.02) while the data order has none (p = 0.34). Add the pod nuisance (p 0.09, in the
  residual) and the 0.22 % depth-3 truncation.
- (b) M1: "remaining steps −1.5" must mention w2 (−4.6). Label the name-base marginalisation as a deviation from the
  pre-registration's "no marginalisation", noting that it is immaterial.
- (c) M3: put the frozen 0.89 and the disjoint-set 0.52 next to the 0.75, and state that E3.2 missed. Label the
  convergence finding post hoc and restrict it to ds-generator g1/g2. Give the round3-run4b model sizes (25 M / 85 M).
  Fix "41 seeds" to 44.

**Not supported as it stands:** round3-run4b per-round counts and depth shares in `per_round.tsv` / `numbers.md`
(#23, #24). They count start-index variants of one proof as distinct. They must be recomputed with start-index
normalisation. The corrected values are in `review/m3_analysis.txt`, and the E3.1 headline does not move.

**Next measurements:**
1. Whether the depth-3 mode is set by early training noise at all: 16–32 identical-seed replicates of 2–3 cells, one
   per GPU class, then fork replicates from a common step-k checkpoint (k = 500, 1,500, 3,000) to find when the mode is
   decided.
2. For M3, the one bimodal family that decides "by round 2 vs later": more seeds of round3-run4b's `85Mr_mix`/`25Mr_mix`
   (currently 3 each). Or a 3.2 M analogue started from bases in the low depth-3 mode, since ds-generator shows EI pulls a
   low-mode seed up in one round.
