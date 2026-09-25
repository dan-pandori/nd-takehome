# Review — run `noise-floor` (proposal 11, run 2)

Reviewer: agent:claude, a session independent of the executor. Started 2026-09-25 07:30 UTC.
`AGENT_POLICY.md` governs. Phase-1 workspace `~/review/noise-floor`; my own code in
`~/review/noise-floor/rv/` (copied to `review_nf_*.py` in this checkout). Phase 2 begins below §Recount.

**Independence caveat, stated up front.** The phase-1 workspace was built by removing `run*.md`,
`*_summary*.md`, `campaign.md`, `followup.md`, `ignition.md`, `phase*.md`, `numbers.md` and
`STATUS*.md`. **`NOISE_FLOOR.md` is not on that list and was therefore present**, and it is the
run's derived-numbers deliverable — I read it while orienting, before recounting. Everything in
§Recount is nonetheless computed by my own code from raw artefacts (`heldout_*.jsonl`,
`found_*.jsonl`, `round_*.json`, `cov_*.jsonl`, `gate_*.jsonl`, the 52 checkpoints, the four
155,000-record training sets), not copied; but a reader should know that this recount was not blind
to `NOISE_FLOOR.md`'s table. It *was* blind to `run_noise_floor.md`, `numbers.md`, `log.md` and
`STATUS.md`. The removal list should gain `NOISE_FLOOR.md` (or any future root-level results file)
for the next run.

---

## §Recount

### What I re-derived, and with what

My own code, written for this review:

| file | what it computes independently |
|---|---|
| `review_nf_heldout.py` | re-runs `nd_verify` on **every recorded proof in all 52 held-out cells** (260,000 records, 243,975 proofs) and rebuilds each cell's solved counts from my own slice predicates joined to `data/p2/heldout.jsonl`; does not read the `solved` flag or the `.json` summaries |
| `review_nf_ladder_cov.py` | own dedup-by-name over `found_transfer_*.jsonl` / `found_*.jsonl`, own `L*`, own distinct-proof and term-size counters, own coverage hit counter; re-verifies every counted ladder and coverage proof with `nd_verify` |
| `review_nf_stats.py` | own pooled sd, own two-way variance decomposition, own bimodality coefficients, own t quantiles (bisection on the incomplete beta; cross-checked against SciPy elsewhere) and own MDD constants |
| `review_nf_floor.py` | assembles the floor table and the high-mode proportions |
| `review_nf_splits.py` | own renaming-class normaliser (atoms renamed by order of first appearance) plus a premise-order-insensitive variant; full training × evaluation disjointness matrix |
| `review_nf_shape.py` | own box-depth, rule-share and `ORE`-share recount over all 4 × 155,000 training records |

Plus: `nd2lean.py --check` as the run shipped it, and **`lean_check.py`** (proposal 9, from the
sibling `efficiency` worktree — it does not exist on this branch) with its allowlist, axiom and
elaborated-term-size checks, on a 2,105-proof counted sample.

### Hard constraints

| constraint | check | result |
|---|---|---|
| `nd_verify` hash equals `origin/main`'s | `git ls-tree -r` on `nd_verify/` at `origin/main`, at `HEAD`, and `git hash-object` on the worktree files | **identical** — `__init__.py` `dfa3bc3`, `verify.py` `1cfed53` at all three. Pass |
| `artifacts/TEST_RUN_DONE` unchanged | blob `1d5cf064` at `origin/main` and at `HEAD`; last touched by `ca93f83` (2026-09-15) | **unchanged**. Pass |
| no evaluation file read in training code | `grep` of `train.py` for every eval pool name | the only hit is `--heldout`, loaded at `train.py:93` as `load(...)[:2000]` and used **only** for a printed validation loss (`train.py:116–123`); it never enters `loss.backward()`/`opt.step()` and there is no checkpoint selection on it (the final step is always saved). Pass |
| `nd2lean.py`, `train.py`, `eval_set.py`, `coverage.py`, `ladder_ei.py`, `expert_iter.py` unmodified | md5 against `origin/dan_ds-generator` (the base branch) | unchanged. Pass |
| no hand-written or LLM-written training proofs | all training records come from `gen.py` via `make_coverage_sets.py`/`dsg_assemble.py`; `assemble` provenance in `artifacts/nf/premise.json` names `data/nf/pool_p<i>.jsonl` only | Pass |
| cap 6 on supervised data | all 52 checkpoints carry `cap: 6`; my own length histogram of each training set is flat 31,000 × lengths 2–6 and **zero** records at length 7+ | Pass |

**No quarantine condition.**

### The model every number below applies to

Read from the 52 checkpoints themselves (zip + pickle, no torch on this host):
all 52 are the **same configuration** — `n_params` **3,214,336**, `tok_mode`/`--mode` **`lean_seq`**,
`init: None` (from scratch), `--steps 6000 --bs 128 --cap 6`, `lr 1e-3`, 4 layers, `d` 256, 8 heads,
`vocab` 107, `max_len` 1024, `--heldout data/p2/heldout.jsonl`. The 52 `(data, seed)` pairs are
exactly P1–P4 × seeds 0–12 with **no duplicates**. Total Stage-1 GPU time recorded in the
checkpoints: **17.36 h** (per-run 507–1,486 s).

Equal attempts, verified from the artefacts rather than the scripts:
* every frozen-ladder cell: `rounds 8, k 32, temperature 0.8, batch 512, max_new 512, alloc uniform, no_train true`, all 11 runs identical;
* every coverage cell: `k 2000, temperature 0.8, seed 0, batch 1000`, and my own count confirms **600,000 samples** in each of the 16 cells;
* every held-out cell: `k 1, temperature 0` on the same 5,000 theorems.
`ND_SAMPLE_COMPACT=0` and `CUDA_MEM_FRACTION=0.21` are set in `pod/nf/job.sh`, through which both
the seeds-0–2 matrix (`pod/nf/jobs.py`) and the addendum-2 seeds-3–12 chains
(`pod/nf/jobs_seeds.py`) are launched. Coverage ran with `--procs 2`, not the pre-registered
`--procs 4`; `--procs` is the CPU verification fork-pool only (`coverage.py:58`), does not touch
sampling, and is identical in all 16 cells, so it cannot affect any comparison.

### Splits

My own renaming-class normaliser, every training file × every evaluation pool:

| | heldout (5,000) | ladder targets (4,495) | ladder transfer (2,285) | redreq (300) | d3req (300) | targets_depth3 (1,000) | transfer_depth3 (500) | transfer_redreq (150) | d3req_transfer (100) |
|---|---|---|---|---|---|---|---|---|---|
| train_p1…p4, exact theorem | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| train_p1…p4, renaming class | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** |

All four sets have 155,000 records, 155,000 distinct theorems and 155,000 distinct renaming
classes. **Disjoint by renaming class from every evaluation pool used.** Under a stricter class
that also ignores premise *order*, 9 / 15 / 11 / 13 of 5,000 held-out theorems collide (0.18–0.30 %);
the same residue appears in all four pools, so it cannot create a difference between cells. Not a
violation — but it is a real 0.2 % of the held-out pool whose premise permutation is in training.

Pairwise class overlap between the four assembled sets: **5.82 / 5.84 / 5.82 / 5.85 / 5.95 / 5.95 %**
(Jaccard 3.0 %). The ≤ 6-line class universe is finite, so the pools are not disjoint from each other;
they are also nowhere near the 30–70 % the pre-registration expected (E14 below).

### Premise check (are P1–P4 replicates?) — my own recount over 4 × 155,000 records

| quantity | P1 | P2 | P3 | P4 | spread | `ds-composition` C0 published |
|---|---|---|---|---|---|---|
| records / per length 2–6 | 155,000 / 31,000 | 155,000 / 31,000 | 155,000 / 31,000 | 155,000 / 31,000 | 0 | 155,000 / 31,000 |
| box depth 0 / 1 / 2 / 3 (%) | 53.11 / 35.52 / 11.37 / 0.00 | 53.26 / 35.33 / 11.41 / 0.00 | 53.28 / 35.46 / 11.26 / 0.00 | 53.30 / 35.44 / 11.26 / 0.00 | ≤ 0.19 pp | 53.2 / 35.4 / 11.4 / — |
| proofs containing `ORE` (%) | 1.419 | 1.485 | 1.455 | 1.461 | 0.066 pp | 1.46 |
| proofs containing `AS` (%) | 46.89 | 46.74 | 46.72 | 46.70 | 0.19 pp | 46.8 |
| proofs containing `R` / `DN` (%) | 2.75 / 7.97 | 2.71 / 7.93 | 2.82 / 7.91 | 2.70 / 8.05 | 0.12 / 0.14 pp | — |
| depth-3 records | 0 | 0 | 0 | 0 | 0 | 0 (excluded) |

**The four pools are replicates.** No pool has to be reported as an arm.

### Acceptance: `nd_verify` and Lean

* **Every counted proof I could reach, re-verified with `nd_verify` by my own loop:** 243,975 held-out
  proofs, 4,155 ladder transfer proofs and 20,258 ladder target proofs across the 11 ladder cells,
  1,796 coverage proofs. **Zero rejections. Zero disagreements with the recorded `solved` flag in
  all 52 held-out cells.**
* **My own Lean recheck**, 2,105 counted proofs sampled to give **≥ 200 per arm** (8 P-arms: 219–235
  each; plus 60 per gap-closer and 180 spread over seeds 3–12) drawn from held-out, frozen ladder and
  both coverage pools:
  * `nd2lean.py --check` as the run shipped it: **2,105 / 2,105 nd_ok ∧ lean_ok**, 0 either-way disagreements.
  * `lean_check.py --check` (allowlist; axioms ⊆ {`propext`, `Classical.choice`, `Quot.sound`}; no
    `sorryAx`; term size from the elaborated value): **2,105 / 2,105 accepted**, 0 disagreements.
    Its 33-case self-test passes on this host.
* **In-loop gate** (`LEAN_GATE_LOG`), aggregated by me over all 404 gate records (de-duplicating the
  three identical re-runs of `gate_heldout_p1_s2` and the two of `p3_s2`; the 32 lines per ladder cell
  are 8 rounds × 4 independent batches and are summed):

  | | samples | distinct checked | both accept | nd-only | **Lean-only** | rate |
  |---|---|---|---|---|---|---|
  | held-out cells | 260,000 | 248,158 | 235,869 | **0** | 52 | 210 per million |
  | ladder cells | 19,733,560 | 11,768,230 | 1,725,813 | **0** | 749 | 64 per million |
  | total | 19,993,560 | 12,016,388 | 1,961,682 | **0** | **801** | **67 per million** |

  Strictly one-directional. Worst single cell 603 per million.
* **Term size, re-derived** (Lean inference nodes of the elaborated value, beside ND written lines):

  | group | n | ND lines mean / max | Lean size mean / max | ratio |
  |---|---|---|---|---|
  | held-out counted proofs | 1,140 | 3.82 / 6 | 2.18 / 6 | 0.57 |
  | frozen-ladder transfer proofs | 660 | 8.17 / 11 | 4.43 / 10 | 0.54 |
  | coverage proofs | 305 | 7.53 / 9 | 5.03 / 7 | 0.67 |

  Across the eight P-cells the frozen-ladder proofs are the **same size in every cell** (ND lines
  7.83–8.38, Lean size 4.20–4.63) while the solve count moves 4.3×. The spread is a count, not a
  change in what the proofs look like.

### Per-cell values (all from raw artefacts, by my own counters)

| cell | overall /5000 | 6-line /1000 | depth-3 /500 | 6-line no-pat /247 | frozen transfer /2285 | `L*` | frozen targets /4495 | redreq /300 | req@8 /300 |
|---|---|---|---|---|---|---|---|---|---|
| P1 s0 | 4363 | 487 | 43 | 205 | 117 | 9 | 1036 | 31 | 89 |
| P1 s1 | 4681 | 850 | 409 | 193 | 262 | 9 | 1715 | 19 | 242 |
| P1 s2 | 4725 | 869 | 428 | 196 | — | — | — | — | — |
| P1 s3 | 4559 | 670 | 216 | 209 | — | — | — | — | — |
| P1 s4 | 4685 | 838 | 396 | 201 | — | — | — | — | — |
| P1 s5 | 4709 | 843 | 395 | 206 | — | — | — | — | — |
| P1 s6 | 4484 | 629 | 182 | 208 | — | — | — | — | — |
| P1 s7 | 4519 | 653 | 201 | 210 | — | — | — | — | — |
| P1 s8 | 4356 | 455 | 16 | 206 | — | — | — | — | — |
| P1 s9 | 4365 | 479 | 30 | 204 | — | — | — | — | — |
| P1 s10 | 4435 | 514 | 53 | 217 | — | — | — | — | — |
| P1 s11 | 4316 | 578 | 158 | 176 | — | — | — | — | — |
| P1 s12 | 4650 | 775 | 330 | 204 | — | — | — | — | — |
| P2 s0 | 4729 | 812 | 353 | 213 | 200 | 9 | 1512 | 39 | 205 |
| P2 s1 | 4385 | 508 | 53 | 208 | 96 | 9 | 823 | 43 | 61 |
| P2 s2 | 4376 | 558 | 108 | 200 | — | — | — | — | — |
| P2 s3 | 4434 | 550 | 97 | 208 | — | — | — | — | — |
| P2 s4 | 4773 | 877 | 427 | 203 | — | — | — | — | — |
| P2 s5 | 4694 | 820 | 371 | 202 | — | — | — | — | — |
| P2 s6 | 4547 | 666 | 239 | 202 | — | — | — | — | — |
| P2 s7 | 4383 | 488 | 32 | 207 | — | — | — | — | — |
| P2 s8 | 4387 | 491 | 34 | 211 | — | — | — | — | — |
| P2 s9 | 4638 | 833 | 384 | 204 | — | — | — | — | — |
| P2 s10 | 4709 | 841 | 393 | 205 | — | — | — | — | — |
| P2 s11 | 4670 | 852 | 425 | 189 | — | — | — | — | — |
| P2 s12 | 4685 | 801 | 357 | 196 | — | — | — | — | — |
| P3 s0 | 4340 | 473 | 20 | 206 | 62 | 9 | 714 | 6 | 71 |
| P3 s1 | 4429 | 556 | 102 | 210 | 174 | 9 | 1298 | 46 | 172 |
| P3 s2 | 4569 | 688 | 232 | 212 | — | — | — | — | — |
| P3 s3 | 4526 | 658 | 200 | 211 | — | — | — | — | — |
| P3 s4 | 4727 | 867 | 420 | 207 | — | — | — | — | — |
| P3 s5 | 4629 | 794 | 346 | 199 | — | — | — | — | — |
| P3 s6 | 4673 | 835 | 396 | 196 | — | — | — | — | — |
| P3 s7 | 4382 | 493 | 43 | 208 | — | — | — | — | — |
| P3 s8 | 4727 | 829 | 374 | 209 | — | — | — | — | — |
| P3 s9 | 4370 | 458 | 5 | 209 | — | — | — | — | — |
| P3 s10 | 4347 | 454 | 6 | 206 | — | — | — | — | — |
| P3 s11 | 4566 | 742 | 310 | 182 | — | — | — | — | — |
| P3 s12 | 4475 | 577 | 122 | 209 | — | — | — | — | — |
| P4 s0 | 4358 | 494 | 45 | 205 | 177 | 9 | 1187 | 34 | 144 |
| P4 s1 | 4815 | 920 | 459 | 214 | 265 | **10** | 1765 | 27 | 238 |
| P4 s2 | 4210 | 421 | 4 | 172 | — | — | — | — | — |
| P4 s3 | 4421 | 535 | 86 | 204 | — | — | — | — | — |
| P4 s4 | 4728 | 843 | 399 | 197 | — | — | — | — | — |
| P4 s5 | 4520 | 631 | 178 | 212 | — | — | — | — | — |
| P4 s6 | 4378 | 502 | 61 | 201 | — | — | — | — | — |
| P4 s7 | 4478 | 638 | 204 | 190 | — | — | — | — | — |
| P4 s8 | 4468 | 576 | 124 | 208 | — | — | — | — | — |
| P4 s9 | 4635 | 768 | 316 | 209 | — | — | — | — | — |
| P4 s10 | 4747 | 847 | 389 | 213 | — | — | — | — | — |
| P4 s11 | 4525 | 700 | 261 | 200 | — | — | — | — | — |
| P4 s12 | 4569 | 670 | 213 | 212 | — | — | — | — | — |

Gap-closers (all three are `--no_train` except the T1 row), my own recount:
`la_frozen_dsg_g1_s0` (`ckpts/dsg/stage1_g1_s0.pt`, generator flags `--ore_steps 3 --ore_boxes`) —
transfer **62**, `L*` **9**, targets **612**.
`la_frozen_dsc_a1_s1` (`ckpts/dsc/stage1_a1_s1.pt`) — transfer **194**, `L*` **9**, targets **1,456**.
`la_T1_dsc_a1_s1` (same checkpoint, EI) — transfer **847**, `L*` **11**, targets **2,693**.

### The floor, my numbers

`MDD` at n = 2 per arm = `(t_{0.975,2} + t_{0.80,2})·s·√(1/2+1/2)` = **5.3633 s**; the "as a ratio"
column is `1 + MDD/mean`. My t machinery agrees with SciPy to 10 decimals. Bimodality
`b = (g₁²+1)/(g₂+3)` with the sample-corrected (SAS/Pfister) moments; `b > 5/9 = 0.5556` is
bimodal-consistent.

| quantity | cells | min – max | max/min | pooled sd | MDD n = 2 | / mean | ratio | b |
|---|---|---|---|---|---|---|---|---|
| frozen ladder, transfer solved (of 2,285) | 8 | 62 – 265 | 4.274 | 74.06 | **397.2** | 2.349 | 3.35× | 0.546 |
| frozen ladder, transfer `L*` | 8 | 9 – 10 | 1.111 | 0.3536 | **1.896** | 0.208 | 1.21× | 0.818 |
| frozen ladder, RL targets solved (of 4,495) | 8 | 714 – 1,765 | 2.472 | 391.2 | **2,098** | 1.670 | 2.67× | 0.623 |
| `targets_reductio_req` pass@2,000 (of 300) | 8 | 6 – 46 | 7.667 | 13.23 | **70.98** | 2.318 | 3.32× | 0.515 |
| `r3_1/depth3_req` pass@2,000 (of 300) | 8 | 61 – 242 | 3.967 | 73.27 | **392.9** | 2.572 | 3.57× | 0.875 |
| held-out greedy, overall (5,000) | 52 | 0.8420 – 0.9630 | 1.144 | 0.03038 | **16.3 pp** | 0.180 | 1.18× | 0.557 |
| held-out greedy, 6-line bin (1,000) | 52 | 0.4210 – 0.9200 | 2.185 | 0.1523 | **81.7 pp** | 1.224 | 2.22× | 0.677 |
| held-out greedy, depth-3 slice (500) | 52 | 0.0080 – 0.9180 | 114.75 | 0.3053 | **164 pp — not resolvable** | 3.720 | 4.72× | 0.697 |
| held-out greedy, 6-line no-pattern (247) | 52 | 0.6964 – 0.8785 | 1.262 | 0.03667 | **19.7 pp** | 0.239 | 1.24× | 0.603 |
| held-out greedy, 5-line bin (1,000) | 52 | 0.8770 – 0.9560 | 1.090 | 0.01502 | **8.1 pp** | 0.087 | 1.09× | 0.423 |
| held-out greedy, 4-line bin (1,000) | 52 | 0.8920 – 0.9790 | 1.098 | 0.01512 | **8.1 pp** | 0.085 | 1.08× | 0.510 |
| held-out greedy, 3-line bin (1,000) | 52 | 0.9760 – 0.9970 | 1.022 | 0.00486 | **2.6 pp** | 0.026 | 1.03× | 0.498 |
| held-out greedy, 2-line bin (1,000) | 52 | 0.9870 – 1.0000 | 1.013 | 0.003128 | **1.7 pp** | 0.017 | 1.02× | 0.648 |

MDD constants: n = 2 → **5.3633**, n = 6 → **1.7939**, n = 13 → **1.1456** (n = 12 → 1.1970).
The exact two-sided permutation test at 2 vs 2 has 6 label assignments and 3 distinct statistic
values, so its minimum attainable p is **1/3** — confirmed.

Held-out at 8 and 12 cells, for anyone who already quoted those: overall sd **0.03899** (n = 8) and
**0.03918** (n = 12); 6-line bin **0.1887** / **0.1805**; depth-3 slice **0.374** / **0.354**.

### Bimodality and the depth-3 slice

| cells | high mode (> 0.44) | gap (0.11–0.44) | low (< 0.11) | proportion high | Wilson 95 % | half-width |
|---|---|---|---|---|---|---|
| 52 | 24 | 15 | 13 | **0.4615** | [0.333, 0.595] | 0.131 |
| 12 | 5 | 2 | 5 | 0.4167 | [0.193, 0.680] | 0.244 |
| 8 | 3 | 1 | 4 | 0.3750 | [0.137, 0.694] | 0.279 |

Per pool at 13 seeds: P1 **5/13 = 0.385**, P2 **8/13 = 0.615**, P3 **6/13 = 0.462**, P4 **5/13 = 0.385**.

### Variance decomposition, my own two-way fit (4 pools × 13 seeds, one observation per cell)

`σ²_pool = (MS_pool − MS_resid)/13`, `σ²_seed = (MS_seed − MS_resid)/4`, df 3 / 12 / 36. The
pool × seed interaction is confounded with error.

| held-out quantity | MS_pool | MS_seed | MS_resid | F_pool (p) | F_seed (p) | σ²_pool | resid % | seed % |
|---|---|---|---|---|---|---|---|---|
| overall | 2.736e-4 | 1.084e-3 | 9.231e-4 | 0.296 (0.83) | 1.175 (0.34) | **−5.00e-5** | 95.8 | 4.2 |
| 6-line bin | 6.646e-3 | 2.838e-2 | 2.283e-2 | 0.291 (0.83) | 1.243 (0.29) | **−1.25e-3** | 94.3 | 5.7 |
| depth-3 slice | 2.727e-2 | 1.186e-1 | 9.026e-2 | 0.302 (0.82) | 1.314 (0.25) | **−4.85e-3** | 92.7 | 7.3 |
| 6-line no-pattern | 2.227e-4 | 2.646e-3 | 1.004e-3 | 0.222 (0.88) | **2.635 (0.012)** | −6.01e-5 | 71.0 | **29.0** |
| 5-line bin | 7.763e-6 | 4.625e-4 | 1.646e-4 | 0.047 (0.99) | **2.810 (0.008)** | −1.21e-5 | 68.8 | **31.2** |
| 4-line bin | 1.157e-4 | 4.738e-4 | 1.563e-4 | 0.740 (0.54) | **3.031 (0.005)** | −3.12e-6 | 66.3 | **33.7** |
| 3-line bin | 2.279e-5 | 4.062e-5 | 1.802e-5 | 1.264 (0.30) | **2.254 (0.030)** | **+3.67e-7** | 75.0 | 23.5 |
| 2-line bin | 1.282e-6 | 1.434e-5 | 8.976e-6 | 0.143 (0.93) | 1.597 (0.14) | −5.92e-7 | 87.0 | 13.0 |

At 4 × 2 on the expensive quantities (seed df = 1): frozen ladder transfer σ²_pool **−1,079**,
σ²_seed **+248**, σ²_resid **6,268**; frozen targets **−6.23e4 / −1.18e4 / 2.13e5**; `redreq`
**−84.2 / −49.3 / 275.5**; `req@8` **−3,401 / −899 / 8,796**; `L*` **0 / 0 / 0.125**.

Two things my fit says that are not the obvious summary:

1. **σ²_pool is negative on seven of the eight held-out quantities — not all eight.** The 3-line bin's
   pool component is **positive** (+3.67e-7, 1.5 % of total variance, F = 1.26, p = 0.30, i.e. still
   indistinguishable from zero). The direction of the conclusion is safe; the word "every" is not.
2. **The seed main effect is not negligible on the precise bins.** On the 4-line bin (p = 0.005),
   5-line bin (p = 0.008), 6-line no-pattern slice (p = 0.012) and 3-line bin (p = 0.030) the seed
   component is **23–34 % of total variance — 31–51 % of the residual**, not "a few per cent". A given
   `--seed j` is correlated across all four pools (the initialisation is seeded identically), so on
   the saturated bins seeds behave as a *block*, not as independent replicates. This is good news for
   any future run that pairs seeds across arms, and it means the residual share is **95.8 %** on
   held-out overall and **66–75 %** on the short bins, not ≈ 99 %.

### Pre-registered expectations, scored by me

| # | expectation | my value | verdict |
|---|---|---|---|
| E1 | held-out overall sd ≤ 0.02, max−min ≤ 5 pp | sd 0.0390 (n = 8) / 0.0304 (n = 52); range 9.5 / 12.1 pp | **miss — spread ~2× wider** |
| E2 | 6-line bin sd 0.04–0.10 | 0.1887 (n = 8) / 0.1523 (n = 52) | **miss — above band** |
| E3 | 2-line bin sd ≤ 0.005 | 0.00239 / 0.00313 | met |
| E4 | depth-3 bimodal; 5–8 of 8 high; sd ≥ 0.20 | bimodal (b 1.30 at n = 8); **3 of 8** high; sd 0.374 | **part miss** (high-mode count below band) |
| E5 | `redreq` max/min 1.5–3× | **7.67×** | **miss — above band** |
| E6 | `req@8` max/min 1.5–3× | **3.97×** | **miss — above band** |
| E7 | `targets_depth3` max/min 1.2–2× | **not measured** — no `cov_d3_*` result file exists | **not derivable** |
| E8 | frozen ladder max/min 1.4–2.5×; sd ≥ 25 % of mean | **4.27×**; sd 43.8 % of mean | **part miss** (ratio above band), part met |
| E9 | `L*` spread 9–11 (2 points of noise) | **9–10, one point** | **miss — narrower than predicted** |
| E10 | frozen-ladder n = 2 resolvable difference ±40–60 % | **±235 %** | **miss — 4–6× worse** |
| E11 | pool shapes agree; `ORE` 1.2–1.8 %; box depth within ±2 pp | agree; `ORE` 1.42–1.49 %; depths within 0.2 pp | met |
| E12 | σ²_seed ≥ σ²_pool on the frozen ladder | −1,079 vs +248 → yes | met (but see §Verdict: seed df = 1) |
| E13 | 0 Lean/`nd_verify` disagreements on counted proofs; gate 0–1,000 per million, Lean-only | 0 in 2,105 (both translators, both checkers); gate **67 per million**, strictly Lean-only | met |
| E14 | inter-pool renaming-class overlap 30–70 % | **5.8–6.0 %** pairwise (Jaccard 3.0 %) | **miss — an order of magnitude below** |
| E15 | depth-3 high-mode proportion 0.30–0.55, Wilson half-width ≤ 0.15 | 0.4615, half-width 0.131 | met |
| E16 | cells in the gap 0.11–0.44 ≤ 25 % of 52 | **15/52 = 28.8 %** | **miss — narrowly above** |
| E17 | held-out overall pooled sd at 52 cells 0.030–0.050 | 0.03038 | met (at the band edge) |
| E18 | σ²_pool for held-out overall ≤ 20 % of σ²_resid | negative | met |
| E19 | the four pools' high-mode proportions within ±0.20 | 0.385 / 0.615 / 0.462 / 0.385 → **spread 0.23** | **miss — narrowly above** |

**The falsifier did not fire.** It required the frozen ladder's max/min to be under 1.2×; it is
**4.27×**. Every null spread is at or above its predicted band except `L*` (narrower) and E14
(far below). Proposal 11's premise stands.

### Pre-registered work that was not delivered

Reconstructed from the artefact inventory and the job scripts, without reading the write-ups:

| pre-registered | delivered | evidence |
|---|---|---|
| coverage on `data/p2/targets_depth3.jsonl` (1,000), 8 cells | **none** — 8 `cov_d3_*.log` files exist, each containing only a `START` line and an `until [ -f … ]` waiter; no `cov_d3_*.jsonl` | `artifacts/nf/logs/cov_d3_p*_s*.log` |
| addendum 1: seed-2 frozen ladder (4 cells) and `redreq`/`req@8` coverage (8 cells) | **none** — same waiter-only logs for `cov_red_p*_s2` / `cov_req8_p*_s2`, no `la_frozen_p*_s2` | `artifacts/nf/logs/cov_{red,req8}_p*_s2.log` |
| gap-closers: `ds-composition` C0 and A1, T1 + frozen, both Stage-1 seeds (4 ladder cells × 2 rungs) | **1 checkpoint, 2 rungs** (`la_{T1,frozen}_dsc_a1_s1`). C0's checkpoints (`ckpts/lf/stage1_a1_seq_s{0,1}.pt`) and A1 s0 (`ckpts/dsc/stage1_a1_s0.pt`) were fetched and are on disk, unused | `ckpts/`, `artifacts/nf/la_*` |

The scope cut is documented in `pod/nf/jobs.py`'s header comments, dated 2026-09-24 17:45 and
cross-referenced to `log.md` and `QUESTIONS.md`, with measured per-job costs as the reason; and
commit `a4a1510` ("orphaned job waiters found and killed") records the disposal. Whether the
write-ups report these as misses is §Compare's business.

### Gate 0

`preregistration/noise-floor.md` committed **e8f4c3b 2026-09-24 16:05:09 UTC**; the first pod appears
in `~/runs/noise-floor/podnew.log` at **16:06**; the first result artefact is committed at
**16:24:58**. Addendum 1 committed **16:27:35**, and the earliest held-out artefact
(`gate_heldout_p1_s0`) is stamped **16:42:53** — so addendum 1 genuinely precedes every outcome it
extends. Addendum 2 committed **2026-09-25 03:33:31**; the earliest seed-3+ artefact is **05:21**.
Expectations were written down before the run and before each extension. Pass.

One arithmetic slip inside addendum 2: "At 12 cells my high-mode proportion is 3/8 with a Wilson
95 % interval of [0.137, 0.694]". 3/8 and [0.137, 0.694] are the **8-cell** values; at 12 cells it is
**5/12 = 0.417, [0.193, 0.680]**. The argument for spending on more seeds is unaffected.
