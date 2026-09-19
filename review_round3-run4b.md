# Review: round3-run4b — does "or nothing" survive model size? (depth-3 half)

Reviewer: agent:claude (separate session from the executor). Policy: `AGENT_POLICY.md`.

## Recount

Written 2026-09-19 01:20 UTC in `~/review/round3-run4b/` (executor write-ups removed), **before** reading
`run4b.md`, `numbers.md`, `STATUS.md` or `log.md`. What I had read: `BRIEF_scale.md`,
`preregistration/round3-run4b.md` (with amendments A1–A3), `QUESTIONS.md` (its last two entries state the
executor's gate-1 note and post-hoc "schedule, not size" reading — unavoidable, it is not on the removal list), the pod scripts, and
the raw artefacts. Code: `review_run4b_lib.py` (my parser, start-index normaliser, dependency-cone pruner, depth counter,
renaming-class key), `review_run4b_recount.py`, `review_run4b_splits.py`; outputs in `artifacts/r3_4b/review/`. I did not import
`patterns.py`, `prune.py`, `normalize.py` or `r3_*_analysis.py`. My pattern predicate: a proof has the depth-3 pattern iff
some line in the dependency cone of its last line sits at box depth ≥ 3.

### Hard constraints

| check | result |
|---|---|
| `nd_verify` equals `origin/main` | tree `9437bb7` on both; `verify.py` blob `1cfed53`, `__init__.py` blob `dfa3bc3` identical in `origin/main`, `HEAD`, the worktree and the review copy — **pass** |
| `artifacts/TEST_RUN_DONE` unchanged | blob `1d5cf06` in `origin/main`, `HEAD`, worktree, review copy; only commit touching it is `ca93f83` (the original test run); no commit of this run touches `score_test.py`, `test_run_once.sh` or `targets/` — **pass** |
| no evaluation file read in training code | `train.py` reads `--heldout` only for a validation-loss print (first 2,000 rows, no gradient); `expert_iter.py` builds `mix_<r>.jsonl` from `found[targets]` + a sample of `--train` only — transfer and held-out proofs are judged and written to `found_transfer_*`, never to the mix; no `targets/test_*` reference in `train.py`, `expert_iter.py`, `coverage.py` or `pod/r3_4b/*` — **pass** |
| cap 6 on supervised data | `train_depth3_f0_a1.jsonl`: 155,000 records, 31,000 each at 2–6 lines, none longer; written box depth 0 / 1 / 2: 82,393 / 54,883 / 17,724, **0 proofs at depth ≥ 3** — pass |
| inherited code / pools unchanged | `expert_iter.py`, `patterns.py`, `coverage.py`, `r3_1_analysis.py`, `depth3_req.jsonl`, `depth3_mix.jsonl`, `depth3_req_transfer.jsonl` are blob-identical to `origin/dan_round3-run1` |
| bucket hygiene | `hf://buckets/dan-pandori/nd-rl/round3-run4b/{artifacts,ckpts,data}` exist (1,012 / 25 / 8 entries). The upload includes the pod job logs `artifacts/r3_4b/q/*.log`; I grepped every file under `artifacts/r3_4b` for `hf_…`, `rpa_…`, `sk-ant-`, `ghp_…`, `HF_TOKEN`: **0 matches** |

No hard-constraint violation; no quarantine.

### Split disjointness (my renaming-class key: least text over the 24 atom permutations; premises in order / premises sorted)

| training file → pool | shared classes (ordered / sorted) |
|---|---|
| Stage-1 train (155,000) → required pool (300) | 0 / 0 |
| Stage-1 train → required transfer (100) | 0 / 0 |
| Stage-1 train → neighbours (300) | 0 / 0 |
| Stage-1 train → optional pool (first 300 of `targets_depth3.jsonl`) | 0 / 0 |
| Stage-1 train → held-out (5,000) | 0 / **21** (premise-order permutations of a training class; inherited split, key is premise-ordered) |
| EI pool (`depth3_mix`, 600 = required ∪ neighbours) → required transfer | 0 / 0 |
| EI pool → held-out | 0 / 0 |
| EI pool → optional pool | 130 / 130 (the neighbours were drawn from `targets_depth3`; harmless here because the optional-pool sample is taken only from Stage-1 checkpoints, never from an EI-trained one) |
| required ↔ neighbours, required ↔ transfer, duplicates inside any pool | 0 |

The 21 held-out theorems move no gate verdict (table below, last column). The test prompt files are not read by this run (they share 57 / 1
ordered classes with the Stage-1 set at 2–3 lines; inherited, not this run's evaluation).

Reproducibility note: `data/p2/train_depth3_f0_a1.jsonl` is git-ignored and, in the worktree, a **symlink into another run's worktree**
(`/home/dan/work/run4-grpo/…`). The bucket copy (133,670,628 bytes) is what makes the Stage-1 set recoverable.

### E5 gate — every greedy held-out output re-verified (12 × 5,000 `nd_verify` calls; my verdict equals the file's `solved` flag on all 60,000)

Parameters printed by `train.py`: **25,321,472** and **85,208,064**. "r" = pre-registered retry schedule (12,000 steps, lr 1e-4).

| draw | solved / 5,000 | rate | 6-line bin | rate without the 21 shared classes |
|---|---|---|---|---|
| 25M s0 / s1 / s2 | 4435 / 4424 / 4456 | 0.8870 / 0.8848 / 0.8912 | 0.489 / 0.485 / 0.495 | 0.8867 / 0.8847 / 0.8907 |
| 25Mr s0 / s1 / s2 | 4579 / 4492 / 4554 | 0.9158 / 0.8984 / 0.9108 | 0.619 / 0.541 / 0.590 | 0.9156 / 0.8982 / 0.9106 |
| 85M s0 / s1 / s2 | 4442 / 4453 / 4431 | 0.8884 / 0.8906 / 0.8862 | 0.495 / 0.495 / 0.485 | 0.8881 / 0.8903 / 0.8859 |
| 85Mr s0 / s1 / s2 | 4485 / 4518 / 4462 | 0.8970 / 0.9036 / 0.8924 | 0.516 / 0.544 / 0.487 | 0.8968 / 0.9032 / 0.8919 |

Medians: 25M 0.8870 (**miss**, gate 0.90) → retry 0.9108 (**pass**; one of the three draws, s1, is itself below 0.90); 85M 0.8884 (**miss**,
gate 0.93) → retry 0.8970 (**miss**). By the pre-registered rule 85M is "untrained" at both schedules. All of the deficit is in the
6-line bin (2–5-line bins ≥ 0.967 everywhere).

### Pre-RL samples (k = 2,000 × 300 = 600,000 per draw; every stored proof re-verified; hits = Σ `count` over proofs with my predicate)

Required@8 pool (`depth3_req.jsonl`: 7 / 8 lines 6 / 294; flat alternative at 9 / 10 / none 288 / 1 / 11 — as pre-registered):

| draw | pattern hits | rate | targets hit | valid non-pattern samples |
|---|---|---|---|---|
| 25M s0, s1, s2 | 0, 0, 0 | 0 | 0 | 0 |
| 25Mr s0, s1, s2 | 0, **9**, 0 | 0, **1.5·10⁻⁵**, 0 | 0, 1 (`d3req_204`, first hit at sample 135), 0 | 0 |
| 85M s0, s1, s2 | 0, 0, 0 | 0 | 0 | 0 |
| 85Mr s0, s1, s2 | 0, 0, 0 | 0 | 0 | 0 |

Non-zero draws: **0 / 3, 1 / 3, 0 / 3, 0 / 3** (first schedule: 0 of 6; retry: 1 of 6). A zero in 600,000 bounds the per-sample rate at
≈ 5·10⁻⁶ (95 %). The 85Mr files are merges of a forward and a reverse half with 13 / 6 / 10 targets sampled by both halves; the merged
file keeps 2,000 per target and all halves have 0 hits, so the merge cannot move a count.

Optional pool (A1; first 300 of `targets_depth3.jsonl`):

| draw | pattern hits | rate | targets hit |
|---|---|---|---|
| 25M s0, s1, s2 | 0, 0, 0 | 0 | 0 |
| 25Mr s0, s1, s2 | 75, **7,961**, 0 | 1.25·10⁻⁴, **1.33·10⁻²**, 0 | 6, 24, 0 |
| 85M s0, s1, s2 | 0, 0, 0 | 0 | 0 |
| 85Mr s0, s1, s2 | 0, 1, 0 | 0, 1.7·10⁻⁶, 0 | 0, 1, 0 |

Non-zero on the optional pool: 0 / 3, 2 / 3, 0 / 3, 1 / 3. (Valid depth-≤ 2 proofs exist in every optional-pool sample: 30–5,128 samples
on 2–12 targets — the pool is optional, as the pre-registration says.)

### EI arms (k = 32 × 8 rounds; required stratum; min-round; start-index-normalised distinct proofs; ≥ 150 counted proofs per arm re-verified, or all if fewer — 0 failures anywhere)

`req` arms (300 required targets only):

| draw | required targets with a pattern proof, rounds 1–8 | rounds that trained | frozen arm |
|---|---|---|---|
| 25M s0, s1, s2 | 0 throughout | 0 | run: 0 throughout (3 arms) |
| 25Mr s0, s2 | 0 throughout | 0 | not run (skipped as identical) |
| 25Mr s1 | 0,0,0,0,0,0,0,**1** (`d3req_204`, round 8) | 1 (after round 8, so no sample ever came from a trained model) | run: `found_8.jsonl` **byte-equal** to the req arm's |
| 85M s0, s1, s2 | 0 throughout | 0 | directory holds `args.json` only — **not run** |
| 85Mr s0, s1, s2 | 0 throughout | 0 | not run |

Ignition on `req`: **0 of 12**. Acquisition ≤ 1 / 300. A `req` arm that never trains is a frozen control by construction (same seed, same
checkpoint; confirmed byte-equal on 25Mr s1), so the missing frozen arms lose nothing — but only 4 of the 12 pre-registered frozen arms
exist as files. Required targets solved *without* the pattern (E4d): **0 in every arm**, req and mix.

`mix` arms (300 required + 300 neighbours; `ft_lr` 1e-4 at 25M, 3e-5 at 85M; all 8 rounds trained in every arm):

| draw | required targets with a pattern proof, rounds 1–8 | ignition (≥ 20) | ≥ 6 | neighbours solved r8 | transfer (100) with pattern | distinct / counted proofs |
|---|---|---|---|---|---|---|
| 25M s0 | 0 ×8 | – | – | 129 | 0 | 0 |
| 25M s1 | 0 ×8 | – | – | 121 | 0 | 0 |
| 25M s2 | 0 ×8 | – | – | 145 | 0 | 0 |
| 25Mr s0 | 0, 2, 15, 106, 205, 224, 226, **230** | r4 | r3 | 214 | 81 | 259 / 4,795 |
| 25Mr s1 | 0, 13, 113, 194, 219, 229, 230, **231** | r3 | r2 | 207 | 82 | 253 / 6,035 |
| 25Mr s2 | 0,0,0,0,0,0,0, **3** | – | – | 131 | 0 | 3 / 10 |
| 85M s0 | 0 ×8 (rounds 5–8 resumed from `_r4.pt` after an OOM, batch 384) | – | – | 103 | 0 | 0 |
| 85M s1 | 0 ×8 | – | – | 110 | 0 | 0 |
| 85M s2 | 0 ×8 | – | – | 119 | 0 | 0 |
| 85Mr s0 | 0, 0, 1, 1, 1, 1, 1, **1** | – | – | 112 | 0 | 1 / 27 |
| 85Mr s1 | 0, 0, 0, 0, 0, 2, 4, **11** | – | r8 | 146 | 11 | 11 / 138 |
| 85Mr s2 | 0, 0, 1, 1, 3, 16, 130, **206** | r7 | r6 | 195 | 76 | 228 / 3,573 |

Ignition on `mix`: first schedule **0 / 3 and 0 / 3**; retry **2 / 3 (25Mr) and 1 / 3 (85Mr)**. Two 85Mr curves are still rising at round 8
(s1: 2 → 4 → 11; s2: 130 → 206), i.e. the 8-round window censors the 85M retry cell. The partial OOM directories (`*.oom1`, `.oom2`)
contain 0 required-pattern proofs and are not counted. There is **no frozen control on the mix pool**; the equal-attempts control for the
required stratum is the never-trained `req` arm of the same draw (0, 1, 0 for the three igniters).

### pass@10⁴ from the Stage-1 checkpoint (A3; 300 × 10,000 = 3·10⁶ samples; every stored proof re-verified)

| draw | pattern hits | base-reachable targets | acquired by `mix` | EI-only | fraction |
|---|---|---|---|---|---|
| 25Mr s0 | 0 | 0 | 230 | 230 | 1.000 |
| 25Mr s1 | 29 (`d3req_204` only) | 1 | 231 | 230 | 0.996 |
| 85Mr s2 | 0 | 0 | 206 | 206 | 1.000 |

Adding the independent 600k sample to the base's reach changes nothing (the only reachable target is `d3req_204` in both). The 25Mr shards
overlap (16 and 110 targets sampled by both shards; `d3req_204` has 29 and 30 hits in the two); the merged file keeps 10,000 per target.

### 3.2M reference row, recounted from run 1's files with the same code

| seed | pre-RL hits / 600k | `req` r8 | `mix` required r1–r8 | ignition |
|---|---|---|---|---|
| s20 | 0 | 0 | …, 1 | – |
| s21 | 0 | 0 | 0,0,2,75,202,229,238,241 | r4 |
| s22 | 2 (3.3·10⁻⁶) | 0 | 0,1,1,2,8,84,178,211 | r6 |
| s23 | 0 | 0 | 0,0,5,55,183,239,250,255 | r4 |
| s24 | 26 (4.3·10⁻⁵) | 5 (trained 7 rounds) | 0,15,136,193,215,224,231,233 | r3 |
| s25 | 0 | 0 | 0 ×8 | – |
| s26 | 0 | 0 | 0,21,169,209,227,237,238,239 | r2 |
| s27 | 0 | 0 | 0 ×8 | – |

Non-zero 2 / 8; `req` ignition 0 / 8; `mix` ignition **5 / 8** (3 of 6 zero-rate, 2 of 2 non-zero) — the pre-registration's 3.2M row
reproduces. Mix-acquired targets absent from the base's 600k sample: 241 / 241, 210 / 211, 255 / 255, 230 / 233, 239 / 239.

### Pre-registered expectations, scored from my counts

| | expectation | my count | verdict |
|---|---|---|---|
| E1 (mine) | ≥ 2 / 3 non-zero at each size | 0 / 3, 0 / 3 (retry 1 / 3, 0 / 3) | **miss** (brief's 3 / 3: miss) |
| E2 | medians ≥ 10⁻⁵ (25M), ≥ 10⁻⁴ (85M) | medians 0 at every size and schedule | **miss** |
| E3 | zero-rate draws stay 0 / 300 on `req`, never train | 11 of 11 zero-rate draws: 0 / 300, 0 training steps | **holds** |
| E4a | ignite on `req` iff rate ≥ 10⁻⁴; 1–2 of 3 85M ignite; ≥ 1 of 3 25M | no draw ≥ 10⁻⁴, none ignites (iff trivially true); the two count predictions **miss** | mixed |
| E4b / E4c | plateau ≥ 0.60; EI-only ≥ 0.5, lower at 85M | vacuous on `req` (A3 says so) | vacuous |
| E4d | 0 non-pattern solutions at 25M, ≤ 5 % at 85M | 0 everywhere | holds |
| E5 | 25M 0.90–0.93 passes; 85M 0.91–0.95, 50 % to clear 0.93 | 25M 0.887 miss → retry 0.911 pass; 85M 0.888 → 0.897, below the predicted range | 25M **miss on first schedule**; 85M **miss** |
| E6 | ≥ half of non-igniting draws ignite on `mix` | 0 / 6 first schedule; 3 / 6 retry; 3 / 12 overall | **miss** (retry cell alone: exactly half) |
| A1 | optional pool non-zero ≤ 1 / 3 at 25M, 0 / 3 at 85M; rates < 2.5·10⁻⁴ | first schedule 0 / 3, 0 / 3 (holds); retry 2 / 3 with 1.3·10⁻², and 1 / 3 at 85Mr | holds for the draws it was written for; **fails on the retry draws** |
| A3 | base-reachable ≤ 10 targets; EI-only ≥ 0.95 | 0, 1, 0 targets; 1.000, 0.996, 1.000 | **holds** (n = 2 draws at 25Mr, 1 at 85Mr) |

### What I could not derive

- Writing diagnostic (`diag_*.json`): the files are summaries (60 targets × 64 samples); the raw samples were not pulled, so the
  histograms cannot be recounted. From the summaries: fraction of samples opening a third box — 3.2M 0.001–0.088 (8 draws), 25M
  0.0005–0.021, 25Mr 0.005–0.080, 85M 0–0.0005, 85Mr 0–0.002 (no file for 85Mr s0).
- Spend: no pod log in the review copy (checked in phase 2).
- Parameter counts are read from the training logs (no torch on this host).

### Things I will look for in the write-up

1. n: the only like-for-like size contrast with ≥ 2 igniting draws is 3.2M (5) vs 25Mr (2); 85Mr has **one** igniter. No direction of the
   EI-only fraction with size can be called (pre-registration agrees: two igniting draws per size).
2. "Schedule, not size" rests on 3 / 6 vs 0 / 6 (Fisher exact one-sided p = 0.09, two-sided 0.18), was not pre-registered, and the
   proposed mediator (held-out 6-line bin) does not order the draws: 85Mr s2 ignites with the *lowest* retry 6-line bin (0.487, equal to the
   first-schedule draws) while 25Mr s2 (0.590) and 85Mr s1 (0.544) do not.
3. Size is confounded with `ft_lr` (3e-4 / 1e-4 / 3e-5) and the 8-round window censors 85Mr.
4. 85M is "untrained" by the pre-registered gate at both schedules; any 85M statement must carry that label.

## Compare (phase 2)

Written 2026-09-19 ≈ 01:45 UTC after committing §Recount (75e3232). Read now: `run4b.md`, `numbers.md` §Round 3 run 4b, `log.md`
§round3-run4b, `STATUS.md`, `figures/r3_4b_fractions.png`, `~/pods.log`. Additional checks made in this phase: **all** counted proofs
re-verified (`artifacts/r3_4b/review/review_run4b_verify_all.out`), final validation losses read from the twelve `q/s1_*.log`, the 3.2M
held-out numbers read from run 1's `round_1.json`, pod-hours recomputed from `~/pods.log` + the log's deletion times, Fisher exact tests.

| # | claim (where) | my independent value | verdict |
|---|---|---|---|
| 1 | Parameters 25,321,472 / 85,208,064 (numbers) | same, from 12 training logs | reproduces |
| 2 | Held-out greedy 25M 0.887 / 0.885 / 0.891; 25Mr 0.916 / 0.898 / 0.911 (median 0.911, passes); 85M 0.888 / 0.891 / 0.886; 85Mr 0.897 / 0.904 / 0.892 (misses → "gate-missing") | 4435 / 4424 / 4456; 4579 / 4492 / 4554; 4442 / 4453 / 4431; 4485 / 4518 / 4462 of 5,000, all 60,000 outputs re-verified | reproduces |
| 3 | Deficit is the 6-line bin; 25M s0 0.999 / 0.997 / 0.980 / 0.970 / 0.489; 25Mr s0 0.619; 85Mr s1 0.544 | same | reproduces |
| 4 | 3.2M greedy 0.871–0.893, 6-line 0.47–0.58 | 0.8708–0.8934; 0.466–0.579 (run 1's `round_1.json`, not re-verified by me) | reproduces |
| 5 | Final val loss 0.0819–0.0822 for all twelve | 0.0819–0.0822 | reproduces |
| 6 | Non-zero draws, required pool: 0 / 3, 1 / 3, 0 / 3, 0 / 3; 9 hits in 7.2·10⁶ | same; the 9 hits are one distinct proof of `d3req_204` | reproduces |
| 7 | Optional pool: first schedule 0 / 6; 25Mr 2 / 3 (75; 7,961 hits); 85Mr 1 / 3 (1 hit) | same | reproduces |
| 8 | "(3.2M: 10 / 16)" on the optional pool | not recounted here (ignition study's files; reviewed there) | not derived in this review |
| 9 | Third-box samples "3–337 of 3,840 at 3.2M, 0–2 at 85M" (run4b.md) | summaries give 3.2M 3–337 ✓; 85M first schedule 0 / 2 / 1 ✓, but 85Mr s2 = **6** (numbers.md has it) | reword: "0–2 (first schedule), 0–6 with the retry draws"; raw samples not pulled, so summary-level only |
| 10 | `req`: 11 of 11 zero-rate draws 0 / 300, no training step; 0 of 12 `req` arms ignite | same; 25Mr s1 (the non-zero draw) gets 1 target in round 8 | reproduces |
| 11 | Frozen arms: run for 25M ×3 and 25Mr s1; elsewhere "= req (skipped)", bit-identical where checked | 4 frozen arms exist; 25Mr s1 frozen `found_8.jsonl` byte-equal to req's; 85M frozen dirs hold `args.json` only | reproduces; the substitution is valid (a never-trained `req` arm *is* the frozen control). run4b.md's Design line lists "frozen" without saying 8 of 12 were not run |
| 12 | `mix` curves, ignition rounds (≥ 20; ≥ 6), neighbours solved, for all 12 draws | identical in every cell (230 / 231 / 3; 0 ×6; 1 / 11 / 206; ignition r4, r3, r7) | reproduces |
| 13 | 3.2M row: non-zero 2 / 8 (28 hits / 4.8·10⁶), `req` 0 / 8, `mix` 5 / 8, r8 values 0, 0, 1, 211, 233, 239, 241, 255 | same, from run 1's raw files with my predicate | reproduces |
| 14 | pass@10⁴: 0 / 3·10⁶ (0 targets); 29 / 3·10⁶ (1 target); 0 / 3·10⁶ | same; base-reachable target is `d3req_204` in both of 25Mr s1's samples | reproduces |
| 15 | EI-only 230 / 230, 230 / 231, 206 / 206 | same | reproduces |
| 16 | "All 14,580 counted proofs re-verify"; 3.2M row 25,309, 0 failures | **14,580** and **25,309** counted by my predicate, each re-verified against the *pool's* prompt: 0 failures | reproduces exactly (so my depth-3 predicate and `patterns.depth3` agree on every counted proof) |
| 17 | Required targets solved without the pattern: 0 everywhere (E4d) | 0 in all 28 arm directories that hold files (12 req, 4 frozen, 12 mix) | reproduces |
| 18 | Class overlap required pool ↔ training set: 0 | 0 (ordered and premise-sorted key); also 0 for transfer, neighbours, optional pool | reproduces |
| 19 | Spend: nine pods, 46.8 pod-hours, ≈ $23.5 | creation times in `~/pods.log` match; 24.38 h + 9.10 h A40 × $0.49 + 13.32 h A6000 × $0.53 = **$23.47**; under the $50 ceiling | reproduces |
| 20 | Gate 0: pre-registration c1ad029 17:54:40Z before first pod `r34b-1` 17:56:28Z; `gate0` FAIL caused by `la-6` | `pods.log`: `la-6` 17:53:21Z (another run), `r34b-1` 17:56:28Z; commit time confirmed | reproduces; expectations were written before the run |
| 21 | A1 / A2 committed 18:57:53Z before the optional-pool jobs; A3 20:59:57Z before any pass@10⁴ job | first optional-pool attempt (the failed `nofile` log) 19:53Z; first pass@10⁴ log after 21:20Z | reproduces. Both amendments say what had already been seen — they are informed guesses, correctly labelled |
| 22 | Bucket paths recorded; token scan clean | bucket has all three dirs; my scan of `artifacts/r3_4b` (incl. the uploaded `q/*.log`): 0 token-like strings | reproduces |

### Wording against n

| statement (run4b.md / STATUS.md) | evidence | verdict |
|---|---|---|
| "**Larger bases are zero-rate more often, not less.**" / "these bigger bases had *less* to elicit" | Required pool: 2 / 8 vs 1 / 12 (Fisher two-sided 0.54; vs first schedule 0 / 6: 0.47) — **no difference**. Optional pool: 10 / 16 vs first-schedule 0 / 6 (p = 0.015) is a difference, but the same seeds at 25M on the retry schedule are 2 / 3 non-zero with a rate of 1.3·10⁻² — seven times the largest 3.2M rate the brief quotes (1.9·10⁻³). | **reword.** Supported: "larger bases were *not more often* non-zero (E1 / E2 failed at both sizes); on the optional pool the first-schedule draws and both 85M cells were less often non-zero than 3.2M, the 25M retry draws were not." "Less to elicit" is true of 9 of the 12 draws, not of "bigger bases". |
| "**With neighbours, ignition follows the schedule, not the size.**" | 3 / 6 (retry) vs 0 / 6 (first): Fisher one-sided 0.09, two-sided 0.18; post hoc (the caveat line says so). 3 seeds per cell. | **reword** to the observation: "all three igniters are retry-schedule draws (3 / 6 vs 0 / 6, not significant at n = 6, post hoc)". The heading states a cause; the data are a suggestion. |
| "…beyond base reach at 10⁴, **gated by Stage-1 quality**." | Held-out greedy does not order ignition: 85Mr s2 ignites at 0.892 (6-line bin 0.487 — the *lowest* retry value, equal to first-schedule draws), 25Mr s2 does not at 0.911 (0.590), 85Mr s1 does not by round 8 at 0.904 (0.544). Across cells: 3.2M draws at 0.871–0.893 ignite 5 / 8, first-schedule 25M / 85M draws at the *same* greedy (0.885–0.891) ignite 0 / 6 (Fisher two-sided **0.03** — the largest between-cell contrast in the run, and it runs against a quality gate). | **not supported.** The schedule may matter; "quality" as measured here does not explain which draws ignite. |
| "EI-only fraction ≈ 1 at every size … **flat in size**" | 5 igniters at 3.2M (base sampled at 2,000 only), 2 at 25Mr, **1** at 85Mr (gate-missing). The pre-registration requires two igniters per size before calling a direction. The fraction is at its ceiling at the smallest size, so on this pool it could not have risen: the brief's falsifier (fraction growing with size) is untestable here; only a fall could have shown, and none did. | **reword**: "≈ 1 in all three igniting draws; no fall; one 85M igniter, so no trend is called, and a rise could not be seen on a required pool". |
| "**Size bought nothing.**" | Greedy and val loss identical across 3.2M / 25M / 85M on the first schedule (n = 8 / 3 / 3, ranges overlap fully). | stands as a statement about held-out greedy on this 155k-record set; say so (the log's "data-limited, not capacity-limited" is the accurate version). |
| "'Or nothing' holds at every size on the required pool" | 11 / 11; by construction an arm with no accepted proof cannot train, so the content is "zero-rate at 600k ⇒ nothing at 256 attempts × 300", which held. 85M carries the gate-missing label in run4b.md. | stands |
| "Scale does not retire the clause" | true for these twelve draws; 85M is "untrained" by the pre-registered gate at both schedules, and size is confounded with `ft_lr` (3e-4 / 1e-4 / 3e-5) and with Stage-1 lr (1e-3 at 3.2M) | stands with the label; the `ft_lr` confound and the 8-round censoring of 85Mr (s1: 2 → 4 → 11, s2 130 → 206 at round 8) belong in the caveats — run4b.md mentions "rising", not the lr |
| "Expectations. E1, E2, E5 (85M), E6 wrong; E3, E4d, A3 held." | numbers.md's table is complete and honest (E4a "half / wrong", E5 25M "right only after retry", A1 "wrong for the retry draws"). run4b.md's one-line list leaves out three misses: **E4a's counts** (1–2 of 3 85M and ≥ 1 of 3 25M `req` ignitions: 0), **E5 at 25M on the first schedule** (predicted 0.90–0.93, got 0.887), **A1 on the retry draws**. | **reword** the list in run4b.md; misses are reported as misses in numbers.md |

No use of "bistable", "wall" or "never" beyond "never train / never trained", which is literal (0 training records in every round file).

### Process notes (not defects of the numbers)

- `data/p2/train_depth3_f0_a1.jsonl` is a symlink into another run's worktree and git-ignored; the bucket copy is the durable one. A future
  clean-up of `~/work/run4-grpo` would break this checkout.
- Held-out set: 21 of 5,000 theorems are premise-order permutations of a Stage-1 training class (inherited split). No gate verdict moves (§Recount).
- Interrupted samplers were resumed with a re-seeded generator and forward / reverse halves overlap on 6–110 targets; merged files keep one
  record per target. All affected cells are 0 hits or a single target, so no count depends on the merge rule. Disclosed in log and numbers.
- Only 4 of 12 frozen arms exist and there is no frozen arm on the `mix` pool; the never-trained `req` arm is an exact equal-attempts control
  for the required stratum, so nothing is lost.
- `gate0` / `gate1` failures are harness artefacts as the executor says (`la-6` is not this run's pod; marker blob identical to `origin/main`).

## Verdict

**What stands (every number reproduces from raw files with independent code; 0 verification failures in 14,580 + 25,309 proofs; hard
constraints pass; expectations pre-registered before the first pod; spend $23.5):**

1. At 25M and 85M, on the cap-6 f = 0 depth-3 set, **no first-schedule draw and 1 of 6 retry draws emits a depth-3 proof on the required
   pool in 600k samples** (9 hits, one target). The brief's E1 / E2 and the executor's fail at both sizes.
2. **Zero-rate ⇒ nothing on the required pool: 11 of 11** draws, no training step; the one non-zero draw acquires 1 target. No `req` arm
   ignites at any size (0 / 12; 3.2M 0 / 8).
3. **With neighbours in the pool, 3 of 12 new draws ignite** (25Mr s0, s1; 85Mr s2 — 230, 231, 206 of 300 required targets; 76–82 of 100
   transfer targets), all through the pattern (0 non-pattern solutions), and **what they acquire is not in the base's 10⁴ reach:
   230 / 230, 230 / 231, 206 / 206.** A3 held.
4. Held-out greedy does not improve with size on this data (0.885–0.891 vs 3.2M's 0.871–0.893; val loss 0.082 everywhere); 25M passes the gate
   only on the retry schedule; **85M is gate-missing on both schedules** and every 85M statement carries that label.

**What must be reworded:** "larger bases are zero-rate more often" (required pool shows no difference; the optional-pool contrast reverses
at 25M on the retry schedule); "ignition follows the schedule, not the size" (3 / 6 vs 0 / 6, p = 0.18, post hoc → an observation, not a
finding); "flat in size" (one 85M igniter; fraction at ceiling, so the brief's falsifier cannot be tested on a required pool); the
expectations line in run4b.md (add E4a's counts, E5 at 25M first schedule, A1 on retry draws); "0–2 at 85M" (0–6 with the retry draws);
add `ft_lr` and the 8-round window to the caveats.

**What is not supported:** "gated by Stage-1 quality". Within the retry cells held-out greedy and the 6-line bin do not order the igniters
(85Mr s2 ignites with the lowest values; 25Mr s2 does not with nearly the highest), and at matched greedy the 3.2M draws ignite 5 / 8
against 0 / 6 for first-schedule 25M / 85M (p = 0.03). Something separates those cells, but this run cannot say whether it is size, the
Stage-1 learning rate (1e-3 vs 3e-4 vs 1e-4), the fine-tune learning rate, or chance in which draws open a well-formed third box.

**For the project's question:** the run adds nothing against the elicitation-or-nothing reading and one clean point for the other half —
with rewarded neighbours, EI reaches required depth-3 targets that the base does not reach in 3·10⁶ samples, at 25M as at 3.2M. It does not
show how that depends on size: the size axis is confounded with schedule and learning rates, the 85M cell is untrained by the run's own
gate, and the cell counts are 3.

**Next measurements that would settle what is open (cheapest first):**

1. *Is 85Mr 1 / 3 or more?* Continue `ei_depth3_85Mr_s1_mix` and `_s0_mix` from their round-8 checkpoints (in the bucket) to round 16
   (`--start_round 9 --resume_found`). ≈ 2 × 1.5 A40-hours ≈ $1.5. s1 at 2 → 4 → 11 is on the curve s2 followed one round earlier.
2. *Schedule or chance?* 25M, seeds 3–8, both schedules, `mix` arm only (the only arm that discriminates), plus the writing
   diagnostic with its raw samples kept. 12 draws ≈ 12 × (0.3–1.1 h Stage-1 + 1 h mix) ≈ $9. With 0 / 9 vs ≥ 5 / 9 the schedule effect is real
   (p < 0.03); with a first-schedule igniter it is gone. The executor's proposed 3.2M two-schedule test (8 + 8 seeds, ≈ $3) answers the
   complementary question — whether 3.2M's 5 / 8 survives the lr change — and should run alongside, with `ft_lr` held at the same ratio to
   the Stage-1 peak in every cell.
3. *Can the EI-only fraction move with size at all?* On the required pool it is pinned at 1. Run the brief's measurement where the base has
   something: pass@10⁴ on the **optional** pool for 25Mr s1 (base rate 1.3·10⁻²), 25Mr s0, and two 3.2M igniters, with a `mix`-style arm on
   that pool; only there can "falls with size" or "grows with size" be observed.
