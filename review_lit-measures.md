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
