# Review — style-edl (proposal 32)

Reviewer: agent:claude, reviewer role, 2026-10-23. Run branch `dan_style-edl`; brief nd-rl
`docs/proposals/followups/BRIEF_style-edl.md`; pre-registration `preregistration/style-edl.md` (main body + Addendum 1).
Phase 1 was done in `~/review/style-edl` (executor write-ups removed) with my own scripts in
`review/style-edl-recount/`: `rv_core.py` and `r1_*.py` … `r11_tables.py`. Their outputs are in
`review/style-edl-recount/out/`. Every table below is generated from those files by `r11_tables.py`
(`out/r11_tables.md`); no number was typed in by hand.

## Disclosure: what I saw before or during phase 1

- **Commit subjects.** The session's start-up context printed the run's last commit subjects. They include "style-edl:
  results — EDL by proof style at fixed capability (pre-registered verdict: against)". So I knew the executor's verdict
  before I recounted.
- **Auto-memory.** My session started with a memory note that the executor session had written on 2026-10-23
  (`edl-finetune-gotchas`). It says:
  - the S_own gate EDL_c is ≈ 0.04 bits per proof;
  - on S_short the split gives "0.9 bits per proof of pure artefact", and EDL_c or a cross-fit fixes it;
  - names carry 6.2 of 6.7 bits per own proof;
  - Kalmár fits reach the 8-pass cap, and ℓ_V scoring is expensive.

  I read it before the recount.
- **Pre-registration Addendum 1** gives the stream-build facts by design: 632 eligible theorems, the exclusion counts,
  the atom mix, the identity fractions and the mean actions.
- **Raw artefacts I printed while learning the formats:**
  - the run lines of `edl/s0/S_own.json` (lr 1e-5, order 0: `summary` preq 27.6, L_test 0.131, EDL/proof 0.085);
  - the six run lines of `edl/s0/S_Kal.json` (per-run EDL/proof 423.6, 406.1, 230.3, 218.2, 372.5, 325.9);
  - the 18 run lines of the A_fixed pilot `edl/s0/S_own.fixed.json`;
  - every pod script, the job logs, the gate logs and the registry rows.
- **Not read in phase 1:**
  - `run_style_edl.md`, `run_style_edl_plain.md`, `numbers.md`, `log.md`, `STATUS.md`;
  - from `style_edl/`: `README.md`, `numbers_header.md`, `numbers_footer.md`, `numbers_section.py`, `results.csv`,
    `analyze.py`, `verdict.py`, `figure.py`, `compute_rows.py`, `term_sizes.py`, `make_cap_queue.py`,
    `make_lv_queue.py`;
  - from `artifacts/style_edl/`: `verdict.json`, `bootstrap.json`, `numbers_tables.md`, `compute.csv`,
    `term_sizes.json`, `chosen_lr.json`;
  - `figures/style_edl.png`.

  None of my numbers uses the `summary` fields of the edl json files. Everything is recomputed from the per-proof lists.

# §Recount (phase 1, blind)

## 0. Models every number below refers to

| label | checkpoint | size, architecture | format | from scratch? | trained on |
|---|---|---|---|---|---|
| learner L_s, s = 0, 1, 2 (best-state) | `ckpts/bs/stage1_best12_s{s}_b1200.pt`; md5 9c436c35 / f7ae9a9e / 354c4428 (= the pre-registration and the pod setup log) | 9,560,832, ALiBiGPT `best`, 6 × 384 | `lean_staten` (state → action) | yes | K12 (`data/kh/train_k12.jsonl`, 155,000 theorems, md5 800b5486…, cap 12) |
| r8_s (source of S_RL) | `ckpts/bs/ladder/la_T1_best12_s{s}_r8.pt` (best-state T1 EI ladder, round 8 of 8) | 9.56 M, same | `lean_staten` | no: EI from L_s | `data/ladder/rl_targets.jsonl` (4,495), k 32, T 0.8 |
| θ*(s, S) | `ckpts/style_edl/s{s}/{S}/theta_es_lr{lr*}_E0_o0.pt` (bucket `style-edl/ckpts/style_edl/`) | 9.56 M | `lean_staten` | no: fine-tuned from L_s | the 128 stream proofs of stream S; A_ES at lr*; data order 0 |
| block models | not saved | 9.56 M | `lean_staten` | no: fine-tuned from L_s | the first n stream proofs, n ∈ {8, 16, 32, 64} |

All reads use theorems of tf1200 (`data/kalmar/tf1200_kal_sl.jsonl`, md5 b99c3b8d, 1,200 held-out theorems) at T 0.8,
`max_steps` 1,024, `max_action` 512 and batch 1,024. Code lengths are in bits, with the environment-assigned names not
coded.

## 1. Hard constraints, timing, spend — no violation

- **`nd_verify`.**
  - Its tree in HEAD equals `origin/main`'s (`9437bb72…`).
  - No `style_edl/` script imports it. `search_short.py` calls `minlen.Search`, whose internal check is not used to
    judge.
  - Every Lean gate record of the run (`logs/lean_gate_{reads,cap,build}.jsonl`) says `judge: lean-only`.
- **`artifacts/TEST_RUN_DONE`.** It is unchanged: md5 `e2eea349…`, the same as `origin/main`.
- **Shared code.** Against the base branch `origin/dan_kalmar-complexity` the run changed only its own directories plus
  `STATUS.md`, `log.md`, `numbers.md`, `run_style_edl*.md`, `artifacts/MANIFEST.jsonl` and `.gitignore`.
- **textbook72.** It is not read anywhere: grep of `style_edl/` and `pod/sedl/`.
- **No evaluation data in training** (`r7_score_cpu.py --what tokens`). For every one of the 540 fits (18 cells × 6
  (lr, order) runs × 5 fits):
  - `train_tokens` equals p* × the pair tokens of exactly the first n stream proofs of that data order;
  - `steps` equals p* × ⌈n / 8⌉;
  - `es_tokens` is a whole multiple of the tokens of the ES training subset.

  The test files are only scored. The data orders are consistent: order 0 is the identity in every file, and order 1
  is one fixed permutation, the same in all 372 run records (A_ES, A_fixed, cross-fit, ℓ_V).
- **Expectations before measurements.**
  - Budget registered 03:18:11 (again 04:05:27).
  - Pre-registration committed in `793a95e0` at 04:05:37. The first pod (sedl1) started at 04:06:45.
  - Addendum 1 committed in `dfa286d9` at 04:26:02. The first scored stream (`edl_s0_S_own`, git_sha `dfa286d9`)
    started at 04:26:25.
  - The pilot queue finished at 04:29:13, and `q3_edl.sh` (A_fixed fixed at E = 4) was last modified at 04:30:00.
  - The cross-fit queue (`q3x_xfit.sh`, which says "Exploratory (post hoc, log ~04:55)") was written at 04:59:55. That
    was after S_short's EDL (04:46–04:50), so the cross-fit is post hoc.
  - `common.py` (A, scoring) was last modified at 04:01:27 and `edl_run.py` at 04:09:08. Neither changed after scoring
    began.
- **Spend.** $1.86 of the $10 budget, from `~/podhours.log`:
  - sedl1: RTX A5000, 3.81 h, $1.03;
  - sedl2: RTX A5000, 2.77 h, $0.75;
  - sedl3: A40, 0.14 h, $0.08. This pod redid the guided S_Kal s2 read, after the first try ran out of GPU memory on
    sedl2 (RC 1). It is the only failed job.

## 2. Pool, split and streams, rebuilt from the raw reads (`r1_rebuild.py`, `r8_splits.py`)

- **Eligibility.** My own reading of the flags and my own parse of every candidate proof give **632** eligible
  theorems. The exclusions are:
  - selection read < 29 / 32: 358 / 295 / 278 (s0 / s1 / s2);
  - base greedy proof invalid: 98 / 67 / 115;
  - r8 greedy proof invalid: 5 / 14 / 12;
  - no valid attempt in the k 4 draw: 50 / 39 / 92;
  - minlen proof missing: 0. minlen found 1,200 / 1,200 with 0 timeouts, and its longest proof is 6 lines.
- **Sample and split.** All 256 used theorems are in my eligible set, and their prompts equal tf1200's.
  - The halves have 0 shared names and **0 shared renaming classes**. My key is atom permutation × premise multiset.
  - Atom mix: eligible 71 / 175 / 190 / 196 (1 / 2 / 3 / 4 atoms); stream 16 / 34 / 36 / 42; test 15 / 34 / 37 / 42.
    These equal Addendum 1.
- **Disjointness against training data** (my key):
  - tf1200, the 256 used theorems, test128 and stream128 share **0** classes with K12, which the learners were trained
    on (155,000 records, 154,382 classes).
  - They share 0 classes with the ladder targets behind r8 (4,495) and 0 with `data/rl_targets.jsonl` (3,000).
- **The streams.** I rebuilt them from the reads with my own literal-`lean_seq` → ND parser:
  - S_own = L_s greedy;
  - S_own2 = the first accepted attempt of L_s's k 4 draw;
  - S_seed = L_{s+1} greedy;
  - S_RL = r8_s greedy;
  - S_short = the minlen file;
  - S_Kal = tf1200's `proof` field.

  Every stored stream proof equals my rebuild: **4,608 / 4,608** (18 cells × 256), and the ND string is byte-identical
  to my own renderer's output.
- **S_short is minimal among the proofs held.** No other proof in the run's sets (the five other streams of all seeds)
  is shorter in ND lines than the minlen proof of the same theorem: 0 cases.
- **S_Kal fits the caps.** At most 381 actions (cap 1,024); the longest action is 77 tokens (cap 512).

### T1. Streams (my rebuild; per seed s0 / s1 / s2; 256 theorems = stream + test halves)

| stream | identical to own greedy | mean actions | mean ND lines | mean term size (mine) | TF agreement (learner, 256 proofs) |
|---|---|---|---|---|---|
| S_own | 1.000 / 1.000 / 1.000 | 4.52 / 4.55 / 4.44 | 3.52 / 3.55 / 3.44 | 2.34 / 2.36 / 2.27 | 0.9965 / 0.9974 / 0.9982 |
| S_own2 | 0.910 / 0.926 / 0.934 | 4.71 / 4.74 / 4.68 | 3.71 / 3.74 / 3.68 | 2.49 / 2.53 / 2.43 | 0.9776 / 0.9860 / 0.9800 |
| S_seed | 0.941 / 0.938 / 0.941 | 4.55 / 4.44 / 4.52 | 3.55 / 3.44 / 3.52 | 2.36 / 2.27 / 2.34 | 0.9863 / 0.9859 / 0.9844 |
| S_short | 0.871 / 0.848 / 0.883 | 4.26 / 4.26 / 4.26 | 3.26 / 3.26 / 3.26 | 2.09 / 2.09 / 2.09 | 0.9578 / 0.9578 / 0.9633 |
| S_RL | 0.945 / 0.922 / 0.938 | 4.64 / 4.64 / 4.52 | 3.64 / 3.64 / 3.52 | 2.43 / 2.41 / 2.32 | 0.9848 / 0.9756 / 0.9836 |
| S_Kal | 0.000 / 0.000 / 0.000 | 116.13 / 116.13 / 116.13 | 115.13 / 115.13 / 115.13 | 110.22 / 110.22 / 110.22 | 0.2736 / 0.3123 / 0.2273 |

How the columns are defined:
- **Actions** = ND lines + 1, matching `state_env`'s pairs.
- **My term size** counts the inference nodes of the lines the conclusion uses: each used rule application is 1;
  IMPI and NEGI add a lambda, ORE adds two; PR, AS and R count 0. The run's term-size convention may differ, so compare
  these only with one another.
- **TF agreement** is the fraction of actions in which every coded token is the learner's teacher-forced argmax
  (stored per proof; my CPU scorer gives identical counts, §4).
- **Style distance** = 1 − TF agreement, as seed means: S_own 0.0026, S_own2 0.0188, S_seed 0.0145, S_short 0.0403,
  S_RL 0.0187, S_Kal 0.7289.

## 3. Lean — every counted proof I could find re-checked (Lean 4.35.0, VPS; pods ran 4.34.1)

- **Stream proofs.** All **638** distinct stream proofs were rendered by my own ND → Lean translator (`have` per line,
  boxes as `A → B` lambdas, core constants only) and accepted: **638 / 638**. Every (seed, stream) cell is 256 / 256.
- **The literal texts the streams were cut from.** These are the greedy texts of L_s and r8_s and the first accepted
  k 4 text of L_s, for the 256 theorems × 3 seeds. Wrapped as theorems, Lean accepted **2,304 / 2,304**. All of them
  are inside the strict `lean_seq` vocabulary, with no sorry, admit or automation.
- **Negative controls.** All **239 / 239** were rejected: 120 ND proofs whose last line claims the negated conclusion,
  and 119 literal texts with one atom changed in the first `have`.
- **Capability reads (counted proofs).**
  - 120 accepted texts per arm on the test theorems, one per theorem, for the 3 learners and 15 θ* × plain and guided:
    **4,320 / 4,320** accepted.
  - For the six S_Kal θ* arms, fewer than 100 test theorems had an accepted attempt, so I checked **every distinct
    accepted text** (plain on all 256, guided on test): 232 + 473 + 269 + 537 + 140 + 420 = **2,071 / 2,071** accepted.
    s2 S_Kal plain has only 63 accepted samples on test in total.
  - Across all reads, no accepted text contains a forbidden token.
- **V(x)** (`data/style_edl/vset.jsonl`, 2,852 proofs). My strict renderer accepts 2,849.
  - The other 3 (heldout_1503 once, heldout_4196 twice) use BOTE on a negation: `n.elim` with `n : ¬S`, i.e.
    `Not.elim`.
  - Lean accepts all three when BOTE is rendered as `.elim`. This is the divergence the policy counts as valid, so V(x)
    is 2,852 / 2,852 Lean-valid.
- **The gate's rejections.** Every rejection was by the prefilter (`lean_proc_rej` = 0 in every record). I re-checked
  600 of the 2,001 cap rejections and 600 of the 6,261 read rejections in Lean: **0 / 1,200 are Lean-valid**, so I
  found no false rejections in the sample.

## 4. Scoring re-done on the CPU with my own loop (`r7_score_cpu.py`)

My loop uses only the repository's shared `state_env.decompose`, tokenizer and model loader. The rest is my own code:
- the per-theorem name base, sha1(`style-edl:<name>`) mod 33;
- the name shift;
- the mask of the environment-assigned names (the `have` name, and the binder of a box or of the first Or.elim branch);
- fp32 log-softmax sums and argmax agreement.

Results:
- **Learners.** My bits equal the stored learner bits on every proof. I scored all 256 proofs for 15 cells, and the 6
  shortest stream proofs plus the 6 shortest test proofs for S_Kal. The maximum absolute difference is
  **1.5 × 10⁻⁴ bits per proof**, and the per-proof agreement counts are identical. My coded-token counts equal the
  stored ones in all 18 cells; for example S_own s0 has 79.48 coded tokens per proof. With every action token coded, the
  same proofs cost 6.64 bits per proof against 0.42 with the names masked (stream half, s0).
- **θ*.** The 18 downloaded θ* checkpoints are those of lr*, order 0, and each one's `extra` names its stream, lr and
  order. Scored on its own test file, each reproduces the stored θ*-on-test bits to within **1.1 × 10⁻⁴ bits per
  proof**. These are the checkpoints the capability reads loaded (§6), so **pass@32 after training was read with the
  trained θ*.**

## 5. EDL from the stored per-block losses (`r3_edl.py`)

Definitions, as pre-registered:
- preq = Σ blocks of the per-proof block bits; L_test = the mean of θ*'s test bits.
- lr* = argmin over lr of the mean over orders of preq.
- EDL = mean over orders of (preq − 128 L_test), + log₂ 3.
- M = Σ learner stream bits − 128 × the mean learner test bits.
- EDL_c = EDL − M.

The protocol checks out:
- The blocks are [0, 8), [8, 16), [16, 32), [32, 64), [64, 128).
- Block [0, 8) equals the learner's bits for those proofs in every run: 3,552 / 3,552 checked across the A_ES,
  A_fixed and cross-fit files.
- **lr*** is 1e-5 for S_own, S_own2, S_seed and S_RL, and 1e-4 for S_short and S_Kal, in every seed. The closest call is
  s2 S_RL: 81.6 bits at 1e-5 against 82.0 at 1e-4.
- **Pilot.** For A_fixed, the best lr per E gives mean preq E = 1: 37.6 (1e-4), E = 2: 33.5 (1e-4), E = 4: 30.3 (1e-5).
  E = 4 wins by 3.2 bits, more than the 1-bit tie rule, so **E = 4** is correct, and every other cell uses it.
- **Gate.** For S_own s0, EDL_c = **0.043** bits per proof (orders 0.045 / 0.041), within the ≤ 0.3 limit: **pass**.
- **Floor F = 0.100.** It is the pre-registered minimum. The measured components are all smaller:
  - |EDL_c(S_own) − EDL_c(S_own2)| = 0.011 / 0.043 / 0.024;
  - order differences ≤ 0.031.

### T2. EDL (A_ES, names not coded, bits per proof; per seed s0 / s1 / s2)

| stream | lr* | start (block [0, 8)) | learner mean, 256 | L_test (θ*) | EDL / proof | EDL_c / proof | EDL / action | EDL_c / action | M / proof |
|---|---|---|---|---|---|---|---|---|---|
| S_own | 1e-05 / 1e-05 / 1e-05 | 0.58 / 0.52 / 0.47 | 0.392 / 0.283 / 0.250 | 0.127 / 0.186 / 0.109 | 0.095 / 0.024 / 0.056 | 0.043 / -0.005 / 0.037 | 0.0206 / 0.0053 / 0.0123 | 0.0093 / -0.0010 / 0.0082 | 0.052 / 0.029 / 0.018 |
| S_own2 | 1e-05 / 1e-05 / 1e-05 | 1.56 / 0.56 / 0.74 | 0.745 / 0.581 / 0.645 | 0.582 / 0.564 / 0.595 | 0.225 / -0.014 / 0.093 | 0.054 / 0.039 / 0.014 | 0.0468 / -0.0029 / 0.0193 | 0.0113 / 0.0081 / 0.0028 | 0.171 / -0.052 / 0.079 |
| S_seed | 1e-05 / 1e-05 / 1e-05 | 0.81 / 1.94 / 0.88 | 0.453 / 0.501 / 0.419 | 0.185 / 0.236 / 0.222 | 0.100 / 0.269 / 0.215 | 0.046 / 0.065 / 0.073 | 0.0218 / 0.0592 / 0.0467 | 0.0100 / 0.0143 / 0.0158 | 0.054 / 0.204 / 0.142 |
| S_short | 0.0001 / 0.0001 / 0.0001 | 3.29 / 2.83 / 3.18 | 1.594 / 1.271 / 1.507 | 0.171 / 0.239 / 0.226 | 0.968 / 0.910 / 0.951 | -0.340 / -0.047 / 0.073 | 0.2238 / 0.2102 / 0.2197 | -0.0786 / -0.0108 / 0.0169 | 1.309 / 0.957 / 0.878 |
| S_RL | 1e-05 / 1e-05 / 1e-05 | 1.83 / 1.26 / 1.43 | 1.003 / 0.931 / 0.999 | 0.521 / 0.760 / 1.546 | 0.555 / 0.196 / -0.897 | 0.116 / 0.082 / -0.370 | 0.1142 / 0.0413 / -0.1926 | 0.0238 / 0.0171 / -0.0794 | 0.439 / 0.115 / -0.527 |
| S_Kal | 0.0001 / 0.0001 / 0.0001 | 1340.33 / 1254.83 / 1410.82 | 1305.975 / 1240.171 / 1370.711 | 88.441 / 96.561 / 89.948 | 224.261 / 190.358 / 239.777 | 178.889 / 182.142 / 176.732 | 1.9218 / 1.6312 / 2.0547 | 1.5330 / 1.5608 / 1.5145 | 45.372 / 8.216 / 63.045 |

Starting loss per action, block [0, 8): S_Kal 11.5 / 10.8 / 12.1 bits; S_short 0.76 / 0.65 / 0.74; S_own 0.13 / 0.11 /
0.10. Per-proof EDL ÷ the stream's actions gives the per-action columns. The stream half's actions per proof are 4.61
(S_own s0) … 116.70 (S_Kal).

### T3. Excess over S_own2 (bits per proof; s0 / s1 / s2), F = 0.100

| stream | EDL excess | > F in 3 / 3 | EDL_c excess | > F in 3 / 3 | capability criterion on 3 / 3 seeds |
|---|---|---|---|---|---|
| S_own | -0.130 / 0.038 / -0.037 | False | -0.011 / -0.043 / 0.024 | False | True |
| S_seed | -0.125 / 0.283 / 0.123 | False | -0.008 / 0.027 / 0.059 | False | True |
| S_short | 0.744 / 0.923 / 0.858 | True | -0.395 / -0.085 / 0.060 | False | True |
| S_RL | 0.330 / 0.210 / -0.989 | False | 0.062 / 0.043 / -0.383 | False | True |
| S_Kal | 224.036 / 190.372 / 239.685 | True | 178.835 / 182.104 / 176.719 | True | False |

### T9. Per-block curve: bits per proof of each coding block (A_ES at lr*, mean over 3 seeds × 2 orders); last column θ* on test

| stream | [0, 8) learner | [8, 16) | [16, 32) | [32, 64) | [64, 128) | θ* test | fits with p* = 8 (cap) |
|---|---|---|---|---|---|---|---|
| S_own | 0.521 | 0.240 | 0.210 | 0.175 | 0.138 | 0.141 | 23 / 30 |
| S_own2 | 0.951 | 1.246 | 0.788 | 0.474 | 0.630 | 0.580 | 7 / 30 |
| S_seed | 1.209 | 0.686 | 0.428 | 0.278 | 0.312 | 0.215 | 22 / 30 |
| S_short | 3.103 | 0.356 | 1.105 | 2.105 | 0.524 | 0.212 | 9 / 30 |
| S_RL | 1.506 | 0.400 | 1.192 | 1.401 | 0.526 | 0.942 | 20 / 30 |
| S_Kal | 1335.3 | 310.5 | 372.0 | 284.8 | 178.4 | 91.6 | 30 / 30 |

For the short streams, the block means follow where the few differing proofs fall more than they follow learning; see
S_short's [32, 64). **Every S_Kal fit (30 / 30 at lr*) stopped at the 8-pass cap**, so A_ES is truncated for S_Kal and
its EDL depends on `max_passes`.

## 6. Capability (`r4_cap.py`)

I recounted from the rows, filtered to the 128 test theorems.
- The plain reads covered all 256 theorems and the guided reads test128. Each used k 32, sample seed 2, T 0.8 and the
  caps above; the selection read was seed 1.
- Every after-read loaded exactly θ*(lr*, order 0) from §4, and every before-read loaded L_s.
- "Within 0.03" is read as |after − before| ≤ 0.03.

### T4. Capability on the 128 test theorems (k 32, T 0.8, sample seed 2; s0 / s1 / s2)

| model | plain pass@32 | plain pass@1 | guided pass@32 | guided pass@1 | criterion |
|---|---|---|---|---|---|
| learner L_s | 1.000 / 1.000 / 1.000 | 0.966 / 0.976 / 0.972 | 1.000 / 1.000 / 1.000 | 0.993 / 0.997 / 0.997 | – |
| θ*(S_own) | 1.000 / 1.000 / 1.000 | 0.985 / 0.988 / 0.983 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | pass / pass / pass |
| θ*(S_own2) | 1.000 / 1.000 / 1.000 | 0.980 / 0.981 / 0.978 | 1.000 / 1.000 / 1.000 | 0.999 / 1.000 / 0.998 | pass / pass / pass |
| θ*(S_seed) | 1.000 / 1.000 / 1.000 | 0.988 / 0.987 / 0.986 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | pass / pass / pass |
| θ*(S_short) | 0.992 / 1.000 / 1.000 | 0.979 / 0.970 / 0.959 | 1.000 / 1.000 / 1.000 | 1.000 / 0.998 / 0.995 | pass / pass / pass |
| θ*(S_RL) | 1.000 / 1.000 / 1.000 | 0.985 / 0.978 / 0.983 | 1.000 / 1.000 / 1.000 | 0.999 / 0.998 / 1.000 | pass / pass / pass |
| θ*(S_Kal) | 0.383 / 0.352 / 0.250 | 0.029 / 0.047 / 0.015 | 0.602 / 0.602 / 0.594 | 0.118 / 0.135 / 0.103 | FAIL / FAIL / FAIL |

- **The stricter pass@1 reading** (within 0.05) also passes for every stream but S_Kal. S_Kal's pass@1 falls by
  0.937 / 0.929 / 0.957.
- **Truncation.** It is ≤ 0.1 % of attempts in every capability read except θ*(S_Kal) s1 plain, at **1.32 %**
  (108 / 8,192). Among the build reads, the selection and k 4 reads are ≤ 0.05 %, and the s0 and s1 base greedy reads
  have 2 / 1,200 each (0.17 %; those theorems were excluded).
  Even if every truncated attempt on test had been valid, θ*(S_Kal) plain pass@32 would be at most
  0.398 / 0.539 / 0.258. So S_Kal's failure is not caused by the caps.
- **What θ*(S_Kal) proves.** Its accepted proofs are 15–43 ND lines on average (per arm), and 20–55 % of them contain
  a DN-derived P ∨ ¬P line, the first Kalmár split.

## 7. The style-blind score ℓ_V (`r5_lv.py`)

- **V(x) rebuilt independently.** I rebuilt V(x) from every source the pre-registration names: the 18 stream files, the
  selection and k 4 reads, and the plain capability reads of the 3 learners and the 18 θ*. It equals
  `vset.jsonl` on **256 / 256** theorems: 2,852 proofs, mean 11.1 per theorem (2–56), with 0 duplicates.
- **Every stream proof is in V(x).** 252 Kalmár proofs and 14 r8 proofs occur in V(x) only because they are stream
  proofs.
- **The ℓ_V runs repeat the primary fits closely but not exactly.** Their single-string per-proof bits differ from the
  primary fits' by ≤ 0.08 bits per proof on the lr-1e-5 streams, ≤ 0.34 on S_short and ≤ 8.0 on S_Kal (out of
  ~90–1,300). The EDL from the ℓ_V runs differs from the primary by ≤ 0.003 per proof, and by 0.03–0.16 per proof on
  S_Kal.
- **ℓ_V ≤ the single-string code holds** wherever both are stored, up to 2 × 10⁻⁵ bits of batching noise.

### T5. Style-blind score ℓ_V (bits per proof; s0 / s1 / s2)

| stream | EDL_V | EDL_V,c | EDL_c (single string) | EDL_V,c excess over S_own2 | single-string EDL_c excess |
|---|---|---|---|---|---|
| S_own | 0.063 / 0.056 / 0.049 | 0.042 / 0.038 / 0.039 | 0.043 / -0.005 / 0.037 | 0.009 / 0.010 / 0.036 | -0.011 / -0.043 / 0.024 |
| S_own2 | 0.054 / 0.046 / 0.013 | 0.033 / 0.028 / 0.003 | 0.054 / 0.039 / 0.014 | – | – |
| S_seed | 0.069 / 0.076 / 0.058 | 0.048 / 0.058 / 0.048 | 0.046 / 0.065 / 0.073 | 0.015 / 0.030 / 0.045 | -0.008 / 0.027 / 0.059 |
| S_short | 0.181 / 0.221 / 0.211 | 0.160 / 0.203 / 0.200 | -0.340 / -0.047 / 0.073 | 0.127 / 0.175 / 0.197 | -0.395 / -0.085 / 0.060 |
| S_RL | 0.098 / 0.040 / 0.073 | 0.076 / 0.023 / 0.063 | 0.116 / 0.082 / -0.370 | 0.044 / -0.006 / 0.060 | 0.062 / 0.043 / -0.383 |
| S_Kal | -5.095 / -5.560 / -3.961 | -5.116 / -5.578 / -3.971 | 178.889 / 182.142 / 176.732 | -5.149 / -5.606 / -3.974 | 178.835 / 182.104 / 176.719 |

"Share of the spread ℓ_V removes", from the seed means:
- **S_Kal.** EDL_c excess 179.2 → EDL_V,c excess −4.9. EDL_V,c / EDL_c = −0.029 / −0.031 / −0.022: ℓ_V removes all of
  it and turns it negative. Training on Kalmár proofs costs valid mass.
- **S_short and S_RL.** Their single-string EDL_c excesses are *negative* (−0.140 and −0.093), so a "share removed" is
  not defined.
  - Under ℓ_V their excesses are **positive**: S_short +0.166 (0.127 / 0.175 / 0.197, above F in 3 / 3) and S_RL
    +0.033.
  - On the uncorrected EDL, ℓ_V takes S_short's excess from 0.842 to 0.166 (80 % removed).

## 8. Secondary and exploratory analyses (`r3_edl.py`, `r6_attr.py`)

### T6. Secondary: A_fixed (E = 4), cross-fit (exploratory) — EDL and EDL_c per proof (s0 / s1 / s2)

| stream | A_fixed lr* | A_fixed EDL | A_fixed EDL_c | cross-fit EDL (swapped) | cross-fit EDL_c (swapped) | mean of directions, EDL | mean of directions, EDL_c |
|---|---|---|---|---|---|---|---|
| S_own | 1e-05 / 1e-05 / 1e-05 | 0.120 / 0.055 / 0.066 | 0.068 / 0.026 / 0.048 | 0.054 / -0.002 / 0.043 | 0.107 / 0.027 / 0.061 | 0.075 / 0.011 / 0.049 | 0.075 / 0.011 / 0.049 |
| S_own2 | 1e-05 / 1e-05 / 1e-05 | 0.229 / -0.028 / 0.087 | 0.059 / 0.025 / 0.007 | -0.191 / 0.099 / -0.106 | -0.021 / 0.047 / -0.027 | 0.017 / 0.043 / -0.007 | 0.017 / 0.043 / -0.007 |
| S_seed | 1e-05 / 0.0001 / 1e-05 | 0.129 / 0.273 / 0.219 | 0.074 / 0.069 / 0.076 | 0.017 / -0.172 / -0.040 | 0.071 / 0.032 / 0.103 | 0.059 / 0.049 / 0.088 | 0.059 / 0.049 / 0.088 |
| S_short | 0.0001 / 0.0001 / 0.0001 | 1.011 / 0.829 / 0.852 | -0.297 / -0.128 / -0.026 | -0.548 / -0.713 / -0.305 | 0.761 / 0.243 / 0.573 | 0.210 / 0.098 / 0.323 | 0.210 / 0.098 / 0.323 |
| S_RL | 1e-05 / 1e-05 / 1e-05 | 0.538 / 0.199 / -0.495 | 0.099 / 0.084 / 0.032 | -0.449 / -0.102 / 0.455 | -0.010 / 0.012 / -0.072 | 0.053 / 0.047 / -0.221 | 0.053 / 0.047 / -0.221 |
| S_Kal | 0.001 / 0.001 / 0.001 | 244.846 / 223.035 / 299.603 | 199.473 / 214.819 / 236.558 | 204.029 / 179.581 / 209.454 | 249.401 / 187.797 / 272.499 | 214.145 / 184.969 / 224.616 | 214.145 / 184.969 / 224.616 |

The last two columns are equal by construction: swapping the halves flips the sign of M, so the mean of the two
directions cancels the split mismatch exactly.

**Cross-fit result (exploratory).** S_short's mean-of-directions excess over S_own2 is **+0.193 / +0.055 / +0.330**,
above F in 2 / 3 seeds. S_seed's is +0.042 / +0.006 / +0.095 and S_RL's +0.036 / +0.004 / −0.214.

**A_fixed** (secondary, E = 4) gives the same signs as A_ES for S_short (negative EDL_c) and S_Kal (large). S_RL's
EDL_c is positive in all three seeds under A_fixed.

### T7. Addendum-1 attribution (per class; s0 / s1 / s2): n stream + n test, learner bits per proof (stream), EDL_c per class proof

| stream | same: n | same: EDL_c / proof | differ: n | differ: learner bits / proof | differ: θ* test bits / proof | differ: EDL_c / differing proof |
|---|---|---|---|---|---|---|
| S_own2 | 116+117 / 116+121 / 118+121 | 0.026 / 0.023 / -0.015 | 12+11 / 12+7 / 10+7 | 5.41 / 3.77 / 5.95 | 4.74 / 7.57 / 7.71 | 0.15 / -0.21 / 0.13 |
| S_seed | 119+122 / 118+122 / 118+123 | 0.057 / 0.072 / 0.050 | 9+6 / 10+6 / 10+5 | 2.43 / 5.05 / 3.97 | 2.44 / 3.81 / 3.94 | -0.39 / -0.04 / 0.15 |
| S_short | 107+116 / 102+115 / 107+119 | 0.154 / 0.119 / 0.146 | 21+12 / 26+13 / 21+9 | 11.79 / 7.82 / 10.79 | 1.07 / 1.44 / 1.44 | -0.53 / 1.52 / 5.92 |
| S_RL | 118+124 / 117+119 / 119+121 | 0.084 / -0.005 / 0.063 | 10+4 / 11+9 / 9+7 | 11.38 / 8.84 / 7.73 | 12.56 / 8.83 / 26.65 | 1.22 / 0.97 / -7.94 |

- **The split puts more differing proofs in the stream half than in the test half:** S_short 21 vs 12, 26 vs 13 and
  21 vs 9. This is the whole of S_short's M (1.31 / 0.96 / 0.88 bits per proof): 21 × 11.8 − 12 × 6.9 ≈ 165 bits ≈
  1.29 per proof for s0.
- **The per-class EDL_c of the 4–26 differing proofs is noise-dominated.** It ranges from −7.9 to +5.9 bits per
  differing proof, and it rests on 4–13 differing test proofs.
- **S_RL s2's negative EDL_c (−0.370) comes from four test proofs.** θ* got worse on them by +17.7 (heldout_4557),
  +16.7 (heldout_4440), +7.7 (heldout_4830) and +7.4 (heldout_3995) bits.

### T8. Seed summaries: IQM (n = 3, so the IQM is the mean) and bootstrap 95 % interval over seeds, bits per proof

| stream | EDL: IQM [95 % CI] | EDL_c: IQM [95 % CI] |
|---|---|---|
| S_own | 0.058 [0.024, 0.095] | 0.025 [-0.005, 0.043] |
| S_own2 | 0.101 [-0.014, 0.225] | 0.035 [0.014, 0.054] |
| S_seed | 0.195 [0.100, 0.269] | 0.061 [0.046, 0.073] |
| S_short | 0.943 [0.910, 0.968] | -0.105 [-0.340, 0.073] |
| S_RL | -0.049 [-0.897, 0.555] | -0.057 [-0.370, 0.116] |
| S_Kal | 218.132 [190.358, 239.777] | 179.255 [176.732, 182.142] |

- **Spearman ρ(style distance, EDL_c)** over the six streams (seed means) = **0.143**; ρ with EDL = 0.714. The
  pre-registration expected ρ ≥ 0.8.
- **EDL_c ordering** (seed means): S_short (−0.105) < S_RL (−0.057) < S_own (0.025) < S_own2 (0.035) < S_seed (0.061)
  ≪ S_Kal (179.3).

## 9. Compute (`r9_compute.py`, from the registry rows the jobs wrote and the job logs)

- **Registry.** 542 rows: `gpu_seconds`, `train_steps`, `train_tokens`, `gen_tokens`, `attempts`, `actions` and
  `lean_checks`, with arm and seed. Three rows come from a VPS smoke test (`/tmp/se_smoke.json`) and should be left
  out.
- **GPU.** All jobs ran on an RTX A5000 except the redone guided S_Kal s2 read, which ran on an A40.
- **Per A_ES cell.** A short stream takes 38–88 GPU-s, 0.5–1.7 k steps and 1.8–4.8 M training tokens. S_Kal takes
  1,958–3,004 GPU-s and 434–442 M training tokens, ≈ 100× the short streams. The pre-registration flags it as
  > 1.25× by design.
- **Capability reads.** About 35–165 GPU-s each and 0.32–0.73 M generated tokens per arm. θ*(S_Kal) used 2.3–4.9 M.

## 10. Pre-registered expectations against my recount

| pre-registered expectation | recount | hit? |
|---|---|---|
| gate: \|EDL_c(S_own) s0\| ≤ 0.3 | 0.043 | hit |
| F ≈ 0.2–0.5 | 0.100 (the floor; measured components ≤ 0.043) | miss (lower) |
| S_own: start 0.3–0.8; EDL and EDL_c −0.2 to 0.2; distance ≤ 0.01 | start 0.58 / 0.52 / 0.47; EDL 0.095 / 0.024 / 0.056; EDL_c 0.043 / −0.005 / 0.037; 0.0026 | hit |
| S_own2: start 1.5–5; EDL 0–0.5; EDL_c 0–0.5; distance 0.01–0.05 | 1.56 / 0.56 / 0.74; −0.014 for s1; EDL_c 0.054 / 0.039 / 0.014; 0.0188 | start miss; EDL marginal miss (s1); EDL_c and distance hit |
| S_seed: start 1–3; EDL, EDL_c 0–0.5; distance 0.01–0.05 | 0.81 / 1.94 / 0.88; EDL 0.10 / 0.27 / 0.22; EDL_c 0.046 / 0.065 / 0.073; 0.0145 | start miss (2 / 3); rest hit |
| S_RL: start 1.5–8; EDL, EDL_c 0.2–2; distance 0.03–0.15 | 1.83 / 1.26 / 1.43; EDL 0.555 / 0.196 / −0.897; EDL_c 0.116 / 0.082 / −0.370; 0.0187 | miss |
| S_short: start 5–25; EDL, EDL_c 1–8; distance 0.1–0.4 | 3.29 / 2.83 / 3.18; EDL 0.968 / 0.910 / 0.951; EDL_c −0.340 / −0.047 / 0.073; 0.0403 | miss |
| S_Kal: start 200–800 (2–6 per action); EDL 30–300 (0.3–3 per action); EDL_c 30–300; distance 0.6–0.8 | 1,340 / 1,255 / 1,411 (10.8–12.1 per action); EDL 224 / 190 / 240 (1.63–2.05 per action); EDL_c 179 / 182 / 177; 0.729 | start miss (higher); EDL, EDL_c, distance hit |
| EDL_c ordering S_own ≈ S_own2 ≈ S_seed < S_RL < S_short ≪ S_Kal | S_short < S_RL < S_own < S_own2 < S_seed ≪ S_Kal | miss, except S_Kal ≫ |
| per action: S_short and S_Kal within 3×, both above S_RL | EDL_c per action −0.024 vs 1.536; S_short below S_RL (−0.013) | miss |
| ρ(distance, EDL_c) ≥ 0.8 | 0.143 | miss |
| plain pass@32 before ≥ 0.99 | 1.000 / 1.000 / 1.000 | hit |
| pass@32 after ≥ 0.98 for S_own, S_own2, S_seed, S_RL, S_short | ≥ 0.992 everywhere | hit |
| S_Kal pass@32 after 0.85–1.0 ("even odds of failing") | 0.383 / 0.352 / 0.250 | miss; fails the criterion |
| pass@1 before 0.93–0.98 | 0.966 / 0.976 / 0.972 | hit |
| pass@1 after within ±0.03 for S_own, S_own2, S_seed, S_RL | +0.002 … +0.021 | hit |
| S_short pass@1 change −0.10 to +0.02 | +0.013 / −0.006 / −0.014 | hit |
| S_Kal pass@1 falls by 0.1–0.5 | falls by 0.937 / 0.929 / 0.957 | miss (larger) |
| ℓ_V removes ≥ 60 % of S_short's and S_RL's EDL_c excess | those excesses are negative (−0.140, −0.093); under ℓ_V they are +0.166 and +0.033 | not met (premise failed) |
| S_Kal EDL_V,c ≤ 20 % of EDL_c | −2.2 % to −3.1 % | hit |
| A_fixed: same ordering; S_own EDL negative unless lr* = 1e-5 | lr* = 1e-5 and EDL 0.12 / 0.055 / 0.066; ordering S_short < S_own2 < S_own < S_RL < S_seed < S_Kal | lr part hit; ordering differs from A_ES (S_RL moves) |
| Addendum 1: S_seed, S_RL, S_short within ≈ 1 bit per proof of S_own2 (S_short 0.1–1.5, S_RL 0–0.8) | EDL excess: S_short 0.74–0.92, S_RL 0.33 / 0.21 / −0.99, S_seed ≤ 0.28 | hit on EDL, except S_RL s2 |
| A1: differing proofs cost the learner 4–20 bits (< 1 for same proofs) | 2.4–11.8 bits (S_seed s0 2.4, S_own2 s1 3.8); same proofs 0.2–0.4 | mostly hit |
| A1: differing proofs' EDL_c 0–4 bits per proof; same proofs within ±0.2 | differing −7.9 … +5.9; same −0.015 … +0.154 | differing: miss; same: hit |

## 11. The pre-registered decision, from my numbers

- **"Inflated by style at fixed capability"** needs a stream that passes the capability criterion on 3 / 3 seeds and
  exceeds S_own2 by more than F under **both** EDL and EDL_c in 3 / 3 seeds. Addendum 1 makes S_Kal a candidate on
  the same terms. Stream by stream:
  - **S_seed:** passes capability; exceeds F under neither EDL nor EDL_c.
  - **S_RL:** passes capability; exceeds F under neither.
  - **S_short:** passes capability; exceeds F under EDL (0.74 / 0.92 / 0.86) but not under EDL_c
    (−0.40 / −0.09 / +0.06).
  - **S_Kal:** exceeds F under both by ~180–240 bits per proof, but fails capability on 3 / 3 seeds (pass@32
    0.25–0.38).
- **"Against"** holds on both of its pre-registered grounds:
  - no capability-fixed stream exceeds S_own2 by more than F in 3 / 3 seeds;
  - S_short's excess "appears in EDL but not in EDL_c".

  **My recount reproduces the pre-registered verdict: against.**

## 12. Observations to take into phase 2 (not yet compared with the write-up)

1. **The test had little power for the hypothesis it was built for.**
   - The streams that keep capability fixed are the learner's own greedy proofs on 85–95 % of theorems: style
     distance 0.015–0.040, against S_Kal's 0.73.
   - Their EDL_c varies across seeds by 0.41 (S_short) and 0.49 (S_RL) bits per proof, about 4–5× F.
   - F was built from S_own and S_own2, which have few differing proofs and choose lr 1e-5, so it understates the
     noise of the streams being tested.
   - "Against" therefore means "no detectable style cost for streams that differ on 6–15 % of theorems". It is not
     evidence that EDL ignores style.
2. **The only large style change (S_Kal) also changed capability.** pass@1 fell by 0.93–0.96. So this run cannot
   separate style from capability for a large style shift. The A_ES fits for S_Kal are also truncated at the 8-pass
   cap in 30 / 30 fits.
3. **EDL_c is not an unbiased correction either when the halves differ in composition.** S_short's stream half has
   about twice as many differing proofs as its test half. EDL_c subtracts the learner's cost mismatch but not the
   learnability mismatch, and its result swings from −0.34 (primary) to +0.76 (swapped) on s0. The post-hoc cross-fit,
   which cancels the mismatch exactly, gives S_short +0.19 / +0.06 / +0.33 over S_own2. ℓ_V also gives S_short a
   positive excess in 3 / 3 seeds, +0.13 / +0.18 / +0.20, above F. Both are exploratory or secondary, but they lean
   the other way from EDL_c.
4. **lr* depends on the stream:** 1e-4 for S_short and S_Kal, 1e-5 for the rest. So part of any EDL difference
   between S_short and S_own2 comes from a different amount of training.
5. **Things phase 2 must check in the write-up:**
   - the S_Kal capability failure is reported as a miss (expected "even odds", observed 0.25–0.38);
   - ρ = 0.14, against the ≥ 0.8 expected;
   - every number carries its model label (L_s, r8_s or θ*);
   - plain and guided reads are labelled;
   - the cross-fit is labelled exploratory and post hoc;
   - S_Kal compute is flagged as > 1.25×;
   - term sizes are reported;
   - IQM and CI are given with n = 3.
