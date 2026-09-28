# Review of run `fast-stage1` (reviewer session, 2026-09-28)

Reviewer: an independent session. Phase 1 was done in `~/review/fast-stage1` (the executor's write-ups
removed) with code written for this review, in `review_fs/`. Phase 1 read only the brief,
`preregistration/fast-stage1.md`, the code, and the raw artefacts under `artifacts/fs/` and `ckpts/fs/`, plus
arm C's on-file per-record evaluations from `origin/dan_stage1-dynamics:artifacts/sd/ev/c_s*.jsonl`.

**Model every number below is about** (unless a row says otherwise): the 3,214,336-parameter from-scratch
GPT (4 layers, d 256, 8 heads), `lean_seq`, cap 6, trained 6,000 steps at batch 128 on
`data/p2/train_depth3_f0_a1.jsonl`, cosine 1e-3 → 1e-4 (stage1-dynamics arm C's command).
- **new** = this run's `--impl fast`, seeds 0–7, `ckpts/fs/{fast1_s0,fast2_s1,fast2_s2,fast4_s3..s6,fast1b_s7}.pt`
  (trained on one A40 pod, 1, 2, 4 and 1 at a time).
- **C** = `stage1-dynamics` arm C, legacy code, seeds 0–7, `ckpts/sd/c_s*.pt` (A40s).
Held-out greedy is judged by **Lean alone** for both arms (`sd_eval.py`, batch 512, max_new 400, fast
sampler); no number in this review is under `nd_verify`.

## §Recount (phase 1, written before reading the executor's write-up)

### Hard constraints

| check | result |
|---|---|
| `nd_verify/` unmodified | tree hash `9437bb72` at `HEAD` = `origin/main` ✔ |
| `nd_verify` not used as a judge | ✔ `sd_eval.py` (the only evaluator the run used) calls `lean_gate.lean_check` only. `nd_verify.verify_text` is still called by `train.load(check_verify=cap>0)`, which asserts that training records are valid when the cache is built. That is a data-integrity check inherited from legacy, not a judge. |
| `artifacts/TEST_RUN_DONE` unchanged | ✔ no diff against `97346ae4` (the run's base) or `origin/main` |
| no evaluation (test) file read by training code | ✔ `fast_train.py` / `train.py` read `--data` and `--heldout` only. The held-out file enters training only as the no-grad `--val_bins` loss, exactly as in legacy (`Val.per_record` is `@torch.no_grad()`). No `test_*` path in either file. |

No hard-constraint violation, so no quarantine.

### Code equivalence (read, not run)

I read `fast_train.py` against `train.py`'s legacy loop. These are the same: model and initialisation
(`torch.manual_seed(seed)` before `GPT(...)`, unchanged); the loss (mean CE over the batch's proof tokens:
`lm[t] = isproof[t+1] & same-doc` equals legacy `m[:, 1:]`); the optimiser (AdamW β = (0.9, 0.95), wd 0.1 on
all parameters, clip 1.0, `fused=True`, `capturable` under the graph); the LR schedule (`train.lr_at`); the
epoch semantics (a fresh permutation per epoch, `bs` without replacement, remainder dropped); augmentation
(one offset per record uniform on {0 … 64 − mx}, names in the proof only, `mx` over the proof only, as
`shift_abs`); per-document RoPE positions and document-causal masking. The block-mask construction is
correct for non-decreasing slot ids. Pad tail tokens are their own document and are masked out of the
loss. What differs is only the RNG streams (CUDA generators seeded from (seed, epoch) and (seed, step)
instead of `random.Random(seed)`) and float order. The warm-up steps before CUDA-graph capture are undone:
weights are snapshotted and restored, and the Adam moments and step are zeroed. `val2k` (the 2,000-record
val) is not comparable to a legacy log (documented in the docstring); `--val_bins` is.

Two points about the code, neither a violation:
- **`--impl auto` is now the default for every from-scratch GPU run.** That includes `lean_rand`, `abs`,
  `rel` and token modes, other batch sizes, `--sched wsd` and `--state_at`/`--resume`, none of which were in the
  equivalence test (only `lean_seq`, bs 128, cosine). `smoke.log` shows `lean_rand` and resume run without
  error. It does not show them to be equivalent.
- **Resume is not trajectory-exact.** In `smoke.log`, uninterrupted to step 400 gives loss 0.4055 / val 0.3342;
  resumed from the step-200 state it gives 0.4036 / 0.3315. The docstring's "a --resume state is just (weights,
  optimiser, step)" suggests exactness. Probably float non-determinism, but it is untested.

### Self-test coverage (`artifacts/fs/selftest.json`)

PASS as recorded: 0 transform mismatches, fp32 packed/padded loss vs `train.loss_on` max |Δ| 4.8e-7, gradient
rel |Δ| 5.6e-7, block mask identical to `create_block_mask`. **But the augmentation test covered only mx = 2.**
The test used the first 2,000 training records, and I checked that all 2,000 are 2-line proofs, because the
file is sorted by length. So `per_mx` has the single key `"2"`, and the uniformity and "vs `shift_abs`"
chi-squares say nothing about records with more names, which make up 80 % of training. The code path does
not depend on mx beyond `M − mx + 1`, so I expect no bug. The test's stated coverage ("per mx") is
overstated. Uniformity p = 0.046 at mx = 2 (400,000 draws, df 62; the two-sample test against `shift_abs`
gives p = 0.33) is one borderline p, not evidence against uniformity.

### The pre-registered equivalence test: 14 comparisons, recomputed

Per-slice rates were recomputed from the per-record `lean_ok` flags in `artifacts/fs/ev/*.jsonl` (new) and
`c_s*.jsonl` (C), with my own slicing from `data/p2/heldout.jsonl` (`n_lines`, `pat.depth3`). They equal the
executor's `.json` summaries exactly. Each new file's label was checked: `impl fast`, bs 128, 6,000 steps,
seed matches, batch 512, max_new 400. MDD = (t.975,14 + t.80,14)·√(2/8) · sd = **1.5064 · sd**
(the same formula gives 5.3633 at n = 2, NOISE_FLOOR's 5.364 ✔). The sd values are NOISE_FLOOR.md's pooled
values.

**Held-out greedy (Lean alone), mean of 8 seeds**

| slice | new | C | Δ (pp) | MDD (pp) | \|Δ\|/MDD | verdict |
|---|---|---|---|---|---|---|
| all (5,000) | 0.9001 | 0.9105 | −1.04 | 4.58 | 0.23 | within |
| len2 | 0.9939 | 0.9960 | −0.21 | 0.47 | 0.45 | within |
| len3 | 0.9879 | 0.9864 | +0.15 | 0.73 | 0.20 | within |
| len4 | 0.9537 | 0.9469 | +0.69 | 2.28 | 0.30 | within |
| len5 | 0.9189 | 0.9135 | +0.54 | 2.26 | 0.24 | within |
| len6 | 0.6459 | 0.7096 | −6.38 | 22.94 | 0.28 | within |
| 6-line non-depth-3 (500) | 0.8880 | 0.8770 | +1.10 | 5.52\* | 0.20 | within |

\* The pre-registration takes this MDD from NOISE_FLOOR's **"6-line no-pattern (247)"** sd (0.03667), a
different slice from the 500-record 6-line non-depth-3 one it tests. The per-arm sds of the tested slice
here are 0.0160 (new) and 0.0170 (C), so the borrowed floor is about 2× lenient. With MDD from the tested
slice's own pooled sd (1.5064 · 0.0165 = 2.49 pp), |Δ| = 1.10 pp is still within (0.44 MDD).

Per-seed values, IQM, and 95 % stratified-bootstrap interval of the IQM difference (10,000 resamples):

| slice | new s0–s7 | C s0–s7 | IQM new / C | IQM Δ [95 %] |
|---|---|---|---|---|
| all | .915 .928 .868 .913 .930 .869 .908 .869 | .923 .928 .926 .926 .941 .864 .905 .871 | .901 / .920 | −1.90 pp [−4.83, +2.33] |
| len6 | .744 .760 .493 .671 .807 .475 .726 .491 | .802 .789 .784 .814 .830 .494 .693 .471 | .659 / .767 | −10.9 pp [−26.9, +11.3] |
| 6-line non-d3 | .902 .884 .892 .910 .886 .892 .856 .882 | .868 .878 .886 .878 .894 .870 .844 .898 | .889 / .878 | +1.05 pp [−0.55, +2.65] |
| depth-3 (500) | .586 .636 .094 .432 .728 .058 .596 .100 | .736 .700 .682 .750 .766 .118 .542 .044 | .429 / .665 | −23.7 pp [−54.4, +20.7] |

Depth-3 (not a criterion, pre-registered as high-mode counts at > 0.44): **new 4/8, C 6/8** (Fisher two-sided
p = 0.61). New s3 sits at 0.432, just under the cut. Seeds 5 and 7 are in the low mode in both arms. The
two arms share initial weights per seed (same `torch.manual_seed` before `GPT()`) but not data order,
which hints that the mode depends partly on the initialisation. n = 8 cannot show that.

**Validation loss at step 6000 (`--val_bins`, token-weighted per slice)**, from `m_*.jsonl`'s last step
record. Of the 8 new metric files, each has one `args` record with `impl fast`, the matching seed, bs 128,
6,000 steps and the right data.

| slice | new | C | Δ | sd_C (mine) | MDD = 1.5064·sd_C | \|Δ\|/MDD |
|---|---|---|---|---|---|---|
| all | 0.05124 | 0.05101 | +0.00023 | 0.00146 | 0.00219 | 0.10 |
| len2 | 0.07824 | 0.07817 | +0.00007 | 0.00024 | 0.00036 | 0.20 |
| len3 | 0.06780 | 0.06780 | −0.00000 | 0.00030 | 0.00045 | 0.00 |
| len4 | 0.05111 | 0.05139 | −0.00028 | 0.00033 | 0.00049 | 0.57 |
| len5 | 0.03964 | 0.03958 | +0.00006 | 0.00051 | 0.00077 | 0.08 |
| len6 | 0.04322 | 0.04238 | +0.00084 | 0.00515 | 0.00775 | 0.11 |
| 6-line non-d3 | 0.04533 | 0.04551 | −0.00017 | 0.00056 | 0.00084 | 0.21 |

*Erratum (phase 2):* as first committed, this table's means and sds carried a fifth decimal I had
filled in by hand from a four-decimal printout. The rows above are re-printed at five decimals by
`review_fs/recount_val.py`. The Δ and |Δ|/MDD columns and the verdicts are unchanged.

**All 14 comparisons pass, recomputed independently.** One discrepancy to take to phase 2: the
pre-registration lists "sd_C" as all 0.0023, len2 0.0003, len3 0.0005, len4 0.0005, len5 0.0008, len6 0.0077,
6-line non-d3 0.0009. These are **1.506 × my sd_C**, i.e. they are the MDDs, not the sds. If the analysis
then multiplied them by 1.506 again, its val-loss thresholds were 1.5× too lenient. The outcome is the
same either way: the largest |Δ|/MDD under the correct MDD is 0.57 (len4).

Independent check of the logged val loss (my fp32 numpy forward pass over all 5,000 held-out records, with
the fixed presentation re-implemented from its definition, `random.Random(12345)` per record in file order),
on `fast1_s0`: the packed-stream validation **reproduces the logged step-6000 values to ≤ 0.16 % relative on every slice**: all 0.04924 vs 0.04925 logged, len2 0.07824 / 0.07823, len3 0.06779 / 0.06779, len4 0.05097 / 0.05097, len5 0.03985 / 0.03985, len6 0.03664 / 0.03667, depth-3 0.03103 / 0.03108, 6-line non-d3 0.04503 / 0.04502 (bf16 vs fp32). The fast path's `--val_bins` therefore measures the same quantity legacy did, and the val-loss comparison with C is like for like.

Scripts and outputs: `review_fs/` (they were run from `~/review/fast-stage1` with `rv/` = `review_fs/` and arm C's `c_s*.jsonl` in `rv/oldc/`). They are torch-free and ran on the VPS; the review used no pod.

### Lean re-check of counted proofs (≥ 100 per arm)

Harness `review_fs/leanrc.py` (mine): one theorem per line with `#print axioms` on the next line,
`lean -DmaxErrors=100000000` (Lean 4.34.1 on the VPS; the pod used 4.34.0). A theorem is accepted iff no
`error` falls on its lines and its axioms ⊆ {propext, Classical.choice, Quot.sound}. Names are assigned at
file-write time.

**Negative and positive controls first** (arm C stored texts; `review_fs/controls.txt`):
- untouched counted proofs: 60/60 accepted
- parsed-but-Lean-rejected samples as recorded: 0/60 accepted
- counted proof with one `Or.inl`↔`Or.inr` or `.1`↔`.2` flip: 3/60 accepted, all benign (`Or.inr` into `R ∨ R`)
- counted proof paired with a different theorem with the same number of premises: 0/60
- last 3 tokens dropped: 0/30
- bare `sorry`: 0/5

**Arm C: every parsed sample re-checked**, 38,676 stored literal texts over 8 seeds. My verdict equals the
recorded `lean_ok` on **38,676 / 38,676** (36,419 counted proofs accepted, 2,257 rejected).

**New arm: no counted proof text is stored.** `pod/fs/main.sh` ran `sd_eval.py` without `--texts`, so
`artifacts/fs/ev/*.jsonl` holds only verdicts, term size and `have` count. That is an auditability finding: the
brief's "re-check from their stored literal text" is impossible for this arm. In its place I regenerated
the samples with **my own torch-free fp32 numpy re-implementation of the model and greedy KV-cache decoding**
(`review_fs/npgpt.py`, weights read with a pickle/zip reader). That covers 150 held-out theorems × 8
checkpoints: 25 each from len2–len5, the 6-line non-depth-3 slice and the depth-3 slice, fixed seed. Results:

| | reviewer Lean accepts | reviewer Lean rejects |
|---|---|---|
| executor `lean_ok` = True (counted) | **1,038** | 3 |
| executor `lean_ok` = False | 4 | 155 |

Counted proofs per checkpoint in the subset: 132, 137, 124, 130, 139, 122, 133, 124 (≥ 100 each, 1,041 total).
Of the 1,038 agreeing counted proofs, 1,035 have my text's term size identical to the executor's recorded
`n_tok`, i.e. the same decode. All 7 disagreements (0.58 %) are 6-line or 3-line theorems whose fp32 greedy
decode had a top-2 logit margin of 0.0007–0.029 somewhere, i.e. a bf16 vs fp32 argmax flip producing a
different text, not a harness disagreement: on 38,676 arm-C texts the harness agrees 100 %. Rate ≈ 1 in
170, in line with the ≈ 1 in 128 bf16 re-draw rate in NOISE_FLOOR / AGENT_POLICY. **No counted proof was
found that Lean rejects.**

### Term size and lines of counted proofs (both arms, Lean alone)

| slice | new mean term size (n) | C mean term size (n) |
|---|---|---|
| all | 84.99 (36,002) | 86.44 (36,419) |
| len2 | 52.77 | 52.76 |
| len3 | 62.03 | 62.09 |
| len4 | 85.75 | 86.12 |
| len5 | 116.81 | 116.97 |
| len6 | 123.29 | 128.66 |
| written lines (`have` + 1), all | 4.16 | 4.15 |

Term size = whitespace tokens of the literal Lean text, as `sd_eval`'s `n_tok`. For C I recomputed it from
the text and it equals `n_tok` for every record. The len6 gap follows from the depth-3 mix: fewer depth-3
solves in the new arm, and those are the longer proofs.

### Split disjointness

`data/p2/train_depth3_f0_a1.jsonl` vs `data/p2/heldout.jsonl`, under a real canonical form (lexicographic
minimum over the 24 bijections of {P,Q,R,S} of (sorted premise multiset, conclusion)): **22 training
records fall in the renaming class of 21 held-out theorems**, 0 of them depth-3. This is the known
premise-order overlap of this training file, the same as in earlier reviews. It is not new to this run and
is identical in both arms, so it cannot bias the comparison. The 21 theorems fall 7 in len3, 7 in len4, 5 in len5 and 2 in len6, so they are worth ≤ 0.7 pp on any length bin and 0 on depth-3.

### Speed (recomputed from `artifacts/fs/m_*.jsonl`, `b*.jsonl`)

Steady-state ms/step = (Δ wall − Δ validation time) / Δ steps, from step 400 to the last step, so compile
time is excluded. GPU class from `logs/setup.log` (A40, main pod) and the `h100_*` / `a40_*` file prefixes.

| path, GPU | N concurrent | ms/step per process | aggregate steps/s |
|---|---|---|---|
| legacy, A40 | 1 | 48.5–50.2 (3 runs incl. the 6,000-step `legfull_s0`) | 20.3 |
| legacy, A40 | 2 | 102.9, 105.3 | 19.2 |
| legacy, A40 | 4 | 213.6–215.5 | 18.6 |
| fast, A40 | 1 | 16.6–17.3 (3 runs) | 59.2 |
| fast, A40 | 2 | 35.2–36.8 (4 runs, 2 experiments) | 55.2 |
| fast, A40 | 4 | 74.5 ×4 | 53.7 |
| fast, A40 | 8 | 147.8–149.3 | 53.7 |
| legacy, H100 | 1 | 28.2 | 35.5 |
| fast, H100 | 1 / 2 / 4 / 8 / 16 | 4.1 / 8.8 / 17.1 / 33.3 / 70.8 | 244 / 228 / 234 / 240 / 226 |
| fast bs 512, A40 / H100 (500-step timing runs) | 1 | 64.2 / 12.2 | 15.6 / 82.0 (bs 512 steps) |

Whole 6,000-step model with `--val_bins` on the A40: **legacy 313.2 s** (`legfull_s0`), **fast 125.8 s**
(`fast1_s0`: 14.7 s to the first step incl. compile, 10.4 s validation; plus 3.3 s setup) and 119.0 s (`fast1b_s7`).
That is **2.4–2.5× per model and 2.9× per step on the same A40; on the H100 4.1 vs 28.2 ms/step = 6.9×.**
Padding waste of the fast path is 1.08–1.13× (computed/useful tokens). The legacy pad-to-batch-max would be
1.96–1.97× (2.21× at bs 512). Peak memory is 0.41 GiB (A40, bs 128). Model FLOP/s at N = 1 on the A40:
6 · 3.214 M · 17,716 useful tokens/step / 16.9 ms = 20.2 TFLOP/s = **13.5 % of 149.7 TFLOP/s** (attention not
counted). Concurrency gives **no aggregate gain** on either GPU class: A40 fast N = 8 is 0.91× N = 1, and
H100 N = 16 is 0.93× N = 1. Legacy on the A40 does not scale either (N = 4 is 0.92×). Note that legacy at
N = 4 runs at 214 ms/step per process, which is the brief's "215 ms on an A40".

**Against the pre-registered expectations:**

| expectation | measured | verdict |
|---|---|---|
| legacy on the pod 180–230 ms/step | 48.5–50.2 ms/step alone; 214 ms only with 4 co-tenants | **miss** (the premise was a co-tenancy number) |
| legacy padding waste 1.8–2.0× | 1.96–1.97× | holds |
| fast ≤ 25 ms/step, ≥ 8× per step | 16.9 ms/step; **2.9×** per step vs legacy on the same A40 | ≤ 25 ms holds; **≥ 8× misses** |
| full model with `--val_bins` ≤ 4 min incl. compile | 2.1 min (+3 s setup) | holds |
| ≥ 5× per model (target 10×) | **2.5×** vs legacy on the same A40 | **miss** |
| fast padding waste ≤ 1.1× | 1.08–1.13× (the main-arm runs 1.098–1.113×) | borderline (2 of 8 main-arm seeds, s1 and s7, at 1.113) |
| single model ≤ 10 % of bf16 peak | 13.5 % (6N·tokens only) | **miss** (higher than predicted) |
| aggregate ≥ 2× by N = 4, saturating by N = 8 | 0.91× at N = 4 (A40), 0.96× (H100) | **miss** |
| equivalence: pass on all 14 | 14/14 | holds |
| every \|Δ\| under half its MDD | 13/14. Val-loss len4 is at 0.57 MDD with the correct sd_C. Under the pre-registered (MDD-as-sd) numbers it would be 0.38. | **miss on one** with correct MDDs |
| bs 512 at equal tokens within MDD on lengths 2–5 | not run to 6,000/1,500 steps; only 500-step bs-512 timing runs exist | not tested |

Spend: `podbudget fast-stage1` shows 1.49 pod-h, $1.47 of the $5 budget.

### Process observations for phase 2

- The run's three commits are already on **`origin/dan`** (its reflog shows a push of `1f97638b` at 17:44 UTC),
  before this review. The one-line summary of that commit says "--impl auto default", so every later
  from-scratch Stage-1 run on `dan` now uses the fast path. The executor's own stop rule reads: "If the
  equivalence test fails … the fast path is not merged into `dan`". It passed, so that rule does not
  forbid the merge. The policy has librarians merge into `dan` after review.

## §Compare (phase 2: the executor's `run_fast_stage1.md`, `FAST_STAGE1.md`, `numbers.md` § fast-stage1, `log.md`, `STATUS.md`)

All claims are about the model labelled at the top, and the executor labels it in every file (FAST_STAGE1
header, numbers.md "Model (every row)", run_fast_stage1 first line). The H100 rows are the same model on a
different GPU class and are labelled as such. **No unlabelled number found.**

| claim (where) | my independent value | verdict |
|---|---|---|
| Equivalence: 14/14 within the n = 8 MDD (all docs; FS1) | 14/14. Every mean, Δ, sd_used and MDD in `summary.json` equals mine to the printed digits | **reproduces** |
| 13 of 14 under ½ MDD; val-loss len4 at 0.57 (run_fast_stage1) | 0.57 (len4). All others ≤ 0.45 | **reproduces**. The miss of the "every Δ < ½ MDD" expectation is reported as a miss ✔ |
| Held-out overall 0.9001 vs 0.9105, Δ −1.04 pp, MDD 4.58; 6-line 0.6459 vs 0.7096 (FS1) | same | reproduces |
| Val loss all 0.05124 vs 0.05101, MDD 0.00219 (FS1) | same | reproduces. The pre-registration's "sd_C" list is really the MDDs (1.506 × sd). The analysis used the right sd (`sd_used` = 0.00146 for "all"), so this is a pre-registration wording slip only |
| "len 6 non-depth-3" MDD uses the 247-theorem no-pattern sd as a proxy (FAST_STAGE1 caveat) | the tested slice's own sd is ≈ 0.0165, which gives MDD 2.49 pp; |Δ| 1.10 pp is still within | reproduces. The caveat is disclosed, and the proxy is ≈ 2× lenient but does not change the verdict |
| Depth-3 high mode: fast 4/8, C 6/8, R 3/8 (FS2) | 4/8, 6/8, 3/8 (R from `old/ev_r6*.json`) | reproduces. With R at 3/8, 4/8 lies inside legacy's own spread |
| Self-test: "offsets vs `shift_abs` draws min p 0.33 **over all mx**" (log.md 16:31); "tested against `shift_abs`" (FAST_STAGE1) | `selftest.json` `per_mx` has only mx = 2. All 2,000 test records are 2-line (the file is length-sorted) | **not supported as worded.** The test covered one mx. Reword: "mx = 2 only (the first 2,000 records)". No bug is expected (the code has no mx-specific branch) |
| Legacy alone on an A40 48.9 ms/step; the brief's 215 ms was contention (all docs) | 48.5–50.2 ms/step alone; 213.6–215.5 ms/step with 4 legacy co-tenants | **reproduces**. The 4-co-tenant number is exactly the brief's 215 ms, which confirms the explanation |
| Fast 16.8 ms/step, 2.9× per step (run_fast_stage1) | 16.6–17.3; 2.92× vs legacy on the same A40 | reproduces |
| One model: legacy 345 s, fast 128–135 s process wall, 2.6–2.7× (FS3) | `waves.jsonl` walls 344.9 / 134.9 / 128.1 s. In-loop time (excl. process start-up, data load/cache) 313.2 vs 125.8 / 119.0 s = 2.5–2.6× | reproduces. The legacy wall includes its ≈ 30 s `nd_verify` data check, which the fast path skips on a cache hit. On a new data file the fast path pays it too (disclosed in FAST_STAGE1) |
| Padding waste 1.10× (legacy 1.97×) (FS4) | 1.098× on seed 0, 1.083–1.113× across runs; legacy pad-to-max 1.96–1.97× | reproduces (seed 0). Two main-arm seeds are at 1.113×, marginally over the ≤ 1.1 expectation |
| 11.9 % of bf16 peak, legacy 4.7 % (FS5) | 921k useful tok/s → 11.9 % (incl. compile); 13.5 % in steady state; legacy 4.66 % | reproduces. The pre-registered "≤ 10 %" is **missed** (higher), but run_fast_stage1's table lists 11.9 % without calling it a miss. Minor |
| A40 N seeds: fast 44.5 / 47.8 / 49.6 / 47.7 steps/s at N = 1/2/4/8, "N > 1 gains only ~10 %" (FS6, FAST_STAGE1) | wave arithmetic reproduces exactly. Steady-state training throughput per GPU **falls** with N: 59.2 / 55.2 / 53.7 / 53.7 (0.91× at N = 4) | reproduces as whole-job throughput. **Reword the mechanism:** the +11 % is concurrent processes overlapping each other's fixed costs (start-up, compile/capture ≈ 9–15 s, validation), not extra training throughput. The N = 8 wave is 2,000 steps against 6,000 for N ≤ 4, so it is not strictly comparable |
| Legacy N = 1/2/4: 11.9 / 14.0 / 15.6 steps/s; fast per-GPU "≈ 3.2× legacy's best" (FS6, STATUS, run_fast_stage1 headline "2.6–3.2×") | the legacy waves are **1,000 steps** and carry ≈ 30 s of data load each. The fast waves are 6,000 steps. Legacy's own 6,000-step wave (`legfull`) is 17.4 steps/s, so the per-GPU ratio with matched wave length is 49.6 / 17.4 = **2.85×**; steady state 59.2 / 20.3 = **2.9×** | **differs by ≈ 10 %**. "3.2×" compares waves of different lengths. Say ≈ 2.9× per GPU |
| H100: aggregate 65 / 125 / 133 / 179 / 188 steps/s at N = 1/2/4/8/16, "use N = 8–16", "≈ 3.8× an A40" (FS7, FAST_STAGE1) | the waves are 2,000 steps; at 4.1 ms/step that is 8 s of training inside a 31 s wave. Steady-state training throughput is **flat**: 244 / 229 / 234 / 240 / 226 steps/s | **reproduces as arithmetic but mis-describes the H100.** The N = 16 "2.9×" is overlap of ≈ 20 s per-process fixed cost in very short waves. For 6,000-step models I estimate ≈ 1.7× at N = 16 from the same logs (fixed ≈ 23 s + 6,000 × 4.1 ms alone, vs 16 × 6,000 / 226 + 28 s). The H100/A40 ratio of 3.8× compares a 2,000-step H100 wave with a 6,000-step A40 wave; in steady state it is 4.1× (N = 1), so the conclusion survives by coincidence. "≈ 1.9× cost per model" becomes ≈ 1.7× (7.1× price / 4.1× speed). **Reword** |
| bs 512 no faster per token (FS7, log 17:32) | A40 64.2 ms/step at bs 512 = 4 × 16.05 ms: 1.05× per token; H100 12.2 = 4 × 3.05: 1.34× per token | A40: reproduces. **H100: differs.** bs 512 is ≈ 1.3× more tokens/s than bs 128 alone on the H100, so "no gain per token on either GPU" is wrong for the H100 (single 500-step timing run each, and never equivalence-tested) |
| "Headline ≈ 10× against the brief's 1,288 s per model" (run_fast_stage1, STATUS) | 1,288 / 128–135 ≈ 9.5–10× is arithmetic, but 1,288 s is a contended-GPU number | not wrong, but **should not be the headline**. The like-for-like figure is 2.6× per model and ≈ 2.9× per GPU. Both docs give it, the headline order just inverts importance |
| 5× per GPU not met (STATUS, run_fast_stage1) | ≈ 2.9× | reproduces. The miss is reported as a miss ✔ |
| Resume "continues within run-to-run noise but is not bit-identical" (FAST_STAGE1, log 17:40) | smoke.log 0.3315 vs 0.3342 | reproduces, disclosed ✔ |
| `--impl legacy` reproduces an old trajectory exactly (FAST_STAGE1) | the legacy loop is byte-unchanged. The new argparse flags consume no RNG | plausible by inspection; not re-run |
| Cost 1.49 pod-h, $1.47 (A40 $0.49/h, H100 SXM $3.49/h) (FS8) | `podbudget`: 1.49 h, $1.47 | reproduces. Budget was registered at 16:23, before the first pod (16:28) ✔ |
| Bucket `hf://buckets/dan-pandori/nd-rl/fast-stage1/` (FS9) | `hf buckets ls` shows `artifacts/` and `ckpts/fs/` with the 8 fast checkpoints + `legfull_s0.pt` | reproduces |

**Gate 0 / expectations.** The pre-registration was committed at 16:23 (`f5a6cdd6`) before the first pod
(16:28) and before any result. Misses are reported as misses in `run_fast_stage1.md`'s expected-vs-observed
table: legacy ms/step, ≥ 8× per step, ≥ 2× by N = 4 on the A40, and ½-MDD on one comparison. The
per-model ≥ 5× miss is stated in the headline. The one unflagged miss is ≤ 10 % of peak (11.9 %).
The batch-size sweep was pre-registered as exploratory and was dropped with a stated reason (log 17:32). That
reason is right for the A40 and wrong for the H100 (row above).

**n and wording.** The equivalence claim rests on 8 vs 8 seeds, with the same seeds and the same held-out
settings in both arms ✔. It is correctly phrased as "within the MDD" rather than "identical". One nuance the
docs do not state: "within the MDD" means no difference ≥ the 80 %-power MDD was detected. It does not mean
differences below it are excluded. The IQM bootstrap intervals still admit sizeable gaps: overall
[−4.8, +2.3] pp; 6-line [−26.9, +11.3] pp. For any later experiment whose effect is that small on the
6-line bin, fast and legacy models must not be mixed across arms. That is already the policy's
same-settings rule.

**Process.** (1) The run's commits, including the `--impl auto` default, were pushed to `origin/dan` at
17:44 UTC, before review. The review found no correctness problem, so nothing needs reverting. But every
from-scratch Stage-1 run on `dan` since then uses a code path whose review was pending. (2) `sd_eval.py` was run
without `--texts`, so no counted proof of the new arm can be re-checked from its stored literal text (the
reviewer brief's requirement). I substituted an independent fp32 regeneration (§Recount); rerunning
`sd_eval.py --texts` on the 8 bucketed checkpoints would close the gap for about 3 GPU-minutes.

## §Verdict

**Stands.**
- `train.py --impl fast` trains the same kind of model as legacy for the tested configuration: `lean_seq`,
  bs 128, cosine, 6,000 steps, from scratch, 3.2 M parameters. All 14 pre-registered comparisons (7 held-out
  greedy slices under Lean alone, 7 val-loss slices) are within the n = 8 MDD, recomputed independently from
  per-record files. Depth-3 high-mode 4/8 lies between legacy's two 8-run samples (C 6/8, R 3/8). No
  counted proof Lean rejects: arm C 38,676/38,676 stored texts agree with my harness, and 1,038 of the new
  arm's 1,041 counted proofs in a 1,200-sample regeneration are Lean-accepted. The 3 others are bf16/fp32 decode
  flips at margins < 0.03 logits. The fast path's `--val_bins` numbers match my own fp32 forward pass to
  ≤ 0.16 %.
- Speed on an A40: 16.8 vs 48.9 ms/step (2.9×); 2.6× per model in process wall-clock (2.5× in-loop); padding
  waste 1.97× → 1.10×. The brief's 215 ms/step was legacy with ≈ 4 co-tenants, which the logs confirm directly.
- The 5×-per-GPU goal is not met on an A40, as the executor reports.
- No hard-constraint violation: `nd_verify` unchanged and unused as a judge, `TEST_RUN_DONE` unchanged,
  no test file in training code.

**Must be reworded.**
1. "per-GPU ≈ 3.2× legacy's best" / headline "2.6–3.2×": the ratio compares 6,000-step fast waves with
   1,000-step legacy waves. With matched lengths it is **≈ 2.9×**.
2. The H100 paragraph, "aggregate 65 → 188 steps/s at N = 16 … use N = 8–16 … ≈ 1.9× cost per model":
   steady-state H100 training throughput is flat in N (244 → 226 steps/s). The N-scaling is 2,000-step waves
   amortising ≈ 20 s of per-process start-up and compile. Say: "on an H100 one process runs at 4.1 ms/step
   (≈ 4.1× an A40); concurrency only overlaps start-up, which matters for short runs". Cost per model
   ≈ 1.7× an A40's.
3. "N > 1 gains only ~10 %" on the A40: true for whole jobs, but the mechanism is overlap of fixed costs.
   Steady-state throughput drops 9 %.
4. "bs 512 no faster per token on either GPU": true on the A40 (1.05×), not on the H100 (≈ 1.3×).
5. Self-test "min p 0.33 over all mx" / "tested against `shift_abs`": only mx = 2 was tested.
6. Put the uncontended 2.6× first. The ≈ 10× against the contended 1,288 s belongs in the premise
   correction, not the headline.
7. Pre-registration: the listed "sd_C" values are the MDDs (1.506 × sd). A wording slip only; the analysis
   used the right sds.
8. Expected-vs-observed: mark "≤ 10 % of bf16 peak" (11.9 %) as a miss.

**Not supported.** No claim is unsupported outright. The closest are the H100 concurrency
recommendation (item 2) and the "over all mx" self-test wording (item 5).

**Next measurements that would settle what is left open.**
- Rerun `sd_eval.py --texts` on the 8 bucketed fast checkpoints (≈ 3 GPU-min), so their counted proofs
  are re-checkable from literal text like every other arm's.
- Rerun `fast_train_selftest.py` with records sampled across all lengths (e.g. `--n 2000` drawn uniformly
  from the file) so the augmentation test covers every mx that occurs.
- If H100s are to be used: one 6,000-step wave at N = 1 and N = 16 on an H100, to replace the 2,000-step
  extrapolation with a measured per-model cost.
- Before `--impl auto` is relied on for `lean_rand`, token-format (`abs`/`rel`), bs ≠ 128 or `--sched wsd`
  runs: a small equivalence check (≥ 5 seeds against the MDD) in whichever of those a run first needs.
  Only `lean_seq` / bs 128 / cosine was tested, and `auto` already routes all of them to the fast path.
