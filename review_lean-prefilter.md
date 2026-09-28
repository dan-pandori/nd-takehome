# Review — lean-prefilter (reviewer, independent session)

Reviewer session started 2026-09-28T18:30Z. Phase 1 was done in `~/review/lean-prefilter`, a copy with the executor's
write-ups removed. `LEAN_GATE.md` was still present there and I did not open it in phase 1. Phase 1 used the brief,
`preregistration/lean-prefilter.md`, the code and the raw artefacts under `artifacts/lp/`. The scripts are in `review_lp/`
(all mine; they import only the code under test, `lean_prefilter.reject_reason`, and the tokenizer's `statement`/`inverse`).
Lean verdicts I re-derived come from my own runner, `review_lp/rlean.py`: Lean 4.34.1 core, `-j 1`, one theorem per line,
with error lines mapped back to theorems. It is not the gate's `check_sources`. The pods used Lean 4.34.0.

**Model labels.** Every model here is 3,214,336 parameters, trained from scratch. T1: `ckpts/dsc/stage1_a1_s1.pt`
(`lean_seq`, trained on `data/dsc/train_a1.jsonl`, ds-composition). C1: the eight checkpoints in
`artifacts/lp/corpus/*.meta.json`: ds-composition a1_s1 and a3_s0, ds-generator g2_s0, lean-format ei_d3_seq_s0_r8,
lean-format stage1_a1_rand_s0 (`lean_rand`, the only non-`lean_seq` one), lean-format stage1_full_seq_s0, cap-horizon
stage1_k14_s0 and noise-floor stage1_p2_s3. All are sampled at T ∈ {0.8, 1.0, 1.2}, k 12 (first three) or 6, batch 4,096,
`max_new` 512, over the rl_targets, transfer and held-out pools. Checker: Lean alone throughout.

## §Recount (phase 1, committed before reading the write-up)

### Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72…` equals `origin/main:nd_verify` ✓ |
| `nd_verify` not used as a judge | none of the run's code (`lean_prefilter.py`, `lean_gate.py`, `lp_*.py`, `pod/lp/*`, the new test) imports it. The gate's verdict is Lean's, ANDed with the filter's in `on` mode ✓ |
| `artifacts/TEST_RUN_DONE` | unchanged (last touched in `ca93f83`) ✓ |
| evaluation files read in training code | the run's diff to `ladder_ei.py`, `sample.py`, `expert_iter.py` and `eval_set.py` only changes batch defaults, phase timers and the pipelined Gate. `train.py` is not touched by this run ✓ |
| expectations before the run | pre-registration committed `9238edc` at 16:27:41Z; first pod (`lp-t`) created 16:33:55Z ✓ |
| split disjointness by renaming class (my normaliser: minimum over the 24 permutations of P, Q, R, S) | train_a1 (155,000 classes), rl_targets (4,495), transfer (2,285) and held-out (5,000): **0** shared classes in all six pairs ✓ |
| pods | `lp-t` and `lp-k` are gone. `podbudget`: 2.67 h, $1.31 of 6 h / $3 ✓ |

No hard-constraint violation.

### (a) Soundness: 0 false rejects

`review_lp/recount.py` re-runs the **final** `reject_reason` (not the stored verdict) on every stored text and
de-duplicates (prompt, text) globally by hash. Lean's verdicts are the stored shadow-mode ones; below they are spot-checked
in my own Lean.

| corpus | rows | distinct | Lean ok | Lean rej | filter rejects of Lean-**accepted** texts | filter share of Lean's rejects | filter-passed texts Lean rejects |
|---|---|---|---|---|---|---|---|
| C1 model samples (8 ckpts) | 1,732,162 | **1,214,162** | 499,565 | 714,597 | **0** | 100.000 % | 0 |
| C2 edge corpus | 51,274 | 51,274 | 22,918 | 28,356 | **0** | 100.000 % | 0 |
| C2r (second edge file) | 25,007 | 25,007 | 9,991 | 15,016 | **0** | 100.000 % | 0 |
| C3 stored (disagree, test-5, leanrej) | 19,676 | 19,676 | 7,763 | 11,913 | **0** | 100.000 % | 0 |
| union | | **1,307,551** | | | **0** | | |

- The recomputed filter verdict never differs from the stored one. There are no duplicate-verdict conflicts and no null
  Lean verdicts (so shadow mode really sent every text to Lean).
- C1 exceeds the pre-registered ≥ 1,000,000 distinct pairs, and C2 exceeds ≥ 50,000. On all four corpora, **the filter
  and Lean agree on every text**: the filter is not just sound on this fragment but complete. Predicted share ≥ 95 %;
  measured 100 %.
- C1 reject reasons: app-arg 147,455; and-intro 135,142; or-intro 84,572; function-expected 64,281; … elim 5,071;
  ascription 21 (full list in `review_lp/recount.json`). The positive side is exercised: 54,141 Lean-accepted rows use
  `.elim`, 2,418 of them on a declared `¬` (the `Not.elim` skip-a-step class). All passed.
- **My own adversarial set** (`review_lp/adv.py`, independent of the executor's C2) has 32,256 in-grammar texts: each of
  18 term forms, against 15 premise types (declared both as `¬ A` and as `A → False`) and ~40 target types, including the
  shapes that `Not.elim` / `And.elim` / `Or.elim` field notation produce. Lean accepted 558 and rejected 31,698. The filter
  agreed on **every** text: 0 false rejects and 0 missed rejects. The accepted cases include `.elim` on False (224), on
  `¬ …` (136), on `∧` (23) and on `∨` (13). `.elim` on a declared `A → False` and on atoms is rejected by both.
- Code reading (soundness argument). Premise names `hK` reach the filter only as bare, in-order top-level restatements,
  because `lean_tok.inverse` rejects `h1.1` and `h1 n3`. So the filter's `premise-type` check cannot fire on an applied or
  projected premise. Grammar surprises are `_Pass`, and non-fully-parenthesised formulas are `_Pass`. The filter runs only
  on texts `inverse` parsed (`Gate.submit`). I found no false-reject path.
- **Lean re-check of stored verdicts** (`review_lp/relean.py`, my runner, Lean 4.34.1): 4,440 texts, **0 disagreements**.
  This includes ≥ 150 counted (accepted) proofs per T1 arm A/B/C/D plus 60 rejected per arm, 150 accepted + 150 rejected
  per C1 checkpoint, and 200 + 200 each from C2, C2r and C3.
- The executor's unit test `tests/test_lean_prefilter.py` passes locally.

### (b) Identical accepted sets, filter off vs on

`test_b.json`: 120,000 texts from `dump_A`, 14,816 accepted off and on, 0 differ. My re-derivation from stored verdicts:
on the first 120,000 rows, filter∧Lean accepts 14,816, the same as Lean alone. Over all 142,432 distinct `dump_A` texts,
the filter passes exactly the 19,915 texts Lean accepts. **Reproduces.**

### (c) One T1 round, old vs new (A40 pod, one job alone, n = 1 per arm)

From `t1/t1_*/round_1.json` (`secs`, `phase_s`) and `t1/gate_*.jsonl`. "Gate exposed" is the sum of `lean_wall_s`: main
thread inside `submit`/`finish`.

| arm | config (verified from `t1.sh` and the code at `57bff79`, which the pod ran) | round s | gate exposed s | gate share | Lean texts | Lean proc s | accepted (distinct) |
|---|---|---|---|---|---|---|---|
| A old | batch 512, 3 workers, filter off, no pipeline, compaction off, Lean default threads | **1,110.8** | 634.4 | **57.1 %** | 142,907 | 1,856.9 | 19,915 |
| B | batch 512, 7 workers, filter on, pipelined, compaction off, Lean default threads | 484.7 | 16.1 | 3.3 % | 19,934 | 112.6 | 19,915 |
| C (pre-registered) | batch 4,096, as B but compaction on (default) | **271.8** | 16.4 | **6.0 %** | 20,051 | 112.4 | 20,035 |
| D (added after the worker sweep) | as C, `lean -j 1` | **258.6** | 13.0 | 5.0 % (5.03) | 20,051 | 140.0 | 20,035 |

- **Accepted sets.** A = B exactly (0 symmetric difference), and `found_1.jsonl` / `found_transfer_1.jsonl` are
  byte-identical between A and B. C = D exactly (byte-identical found files). A vs C differ, as expected, because the
  batch changes the sample stream. On the 34,380 texts both A and C sampled, verdicts disagree 0 times.
- **Ratios.** C/A = **0.245**, D/A = 0.233, B/A = 0.436. The brief's target of ≤ 1/3 is met. The pre-registered prediction
  of **0.30–0.45 is missed, on the fast side**.
- **Gate share.** The prediction was "≈ 30 % (A) → ≤ 5 % (B, C)". A measured **57 %**, not ≈ 30 %: the A40's sampling at
  batch 512 (≈ 285 s of the 732 s targets phase) is much faster than on the brief's baseline hardware, so Lean's share is
  larger. B meets ≤ 5 % (3.3 %). **C misses at 6.0 %.** D is 5.03 %, at the line. The filter kills all of Lean's rejects
  (122,973 of 122,973 in B), so Lean sees 14 % of the distinct texts.
- **Truncation** (`no-eos` / samples): 0.032 % (A, B) and 0.033 % (C, D), under 0.1 %. The C1 corpus has strata over
  0.1 %: cap-horizon k14 is 0.28 % overall, with a worst stratum of 0.60 %; ds-generator g2 and full_seq are 0.23 %. This is
  harmless for a soundness corpus, since unparsed texts are not tested, but the policy flag applies.
- **Peak memory for C was pre-registered as "recorded" but is not in `t1_C.log`, `gate_C.jsonl` or `round_1.json`.** The
  only peak on file for batch 4,096 is from the C1 corpus runs: **16.76 GB** at `max_new` 512 on the same 3.2 M `lean_seq`
  architecture (A40). That is well above the ≈ 11 GB at `max_new` 288 quoted in the new `--batch` default's comment, and at
  `max_new` 512 only one such job fits on a 24 GB card.

### Worker sizing (pre-registered: throughput at quota workers ≥ 2× that at 3 workers, ≈ 7.6-CPU pod)

`workers*.jsonl`: 30,000 texts, quota 7, texts/s, n = 1–2 per cell.

| Lean threads | 3 workers | 5 | 7 (quota) | 8 | 10 | 14 |
|---|---|---|---|---|---|---|
| default (old; ≈ 96 threads) | 618, 290 | 549 | 298, 293 | 328 | 263 | 243 |
| `-j 1` | 358 | 684 | 745, 871 | 823, 865 | – | 466 |
| `-j 2` | 625 | 755 | 872, 776 | – | 633 | – |

- **Under the old thread setting, quota workers are not faster than 3; they are about 2× slower** (298 and 293 vs 618 and
  290). The 3-worker cell itself varies 2× between repeats.
- With `-j 1`, quota/3 = 745–871 / 358 = 2.1–2.4×, so the prediction holds only in that setting.
- Against the true old configuration (3 workers, default threads: 618 or 290), `-j 1` at quota gives 1.2–3.0×. It is not
  resolved at this n and noise.
- The ≥ 2× claim is supported only as "7 workers at `-j 1` vs 3 workers at `-j 1`". Most of the practical gain is the
  `-j 1` change plus the filter, not the worker count.

### Not applicable

Term size, line counts, frontiers, acquisition and base reachability: the run makes no proof-length or capability claims.
The T1 round's solve counts are by-products (A/B 1,189 targets solved and 1,533 new proofs; C/D 1,202 and 1,544). A vs C
is a sampling re-draw, not a finding.
