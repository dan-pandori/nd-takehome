# review_kal — reviewer's recount kit for run `kalmar-pretrain`

Reviewer code (agent:claude, 2026-10-20). It is written independently of the executor's `kalmar/` package: nothing here
imports `kalmar/`, `lean_judge`, `gen` or `nd_verify`.

Project code is used only as infrastructure:
- `state_env.decompose`, for the environment's canonical states and names;
- `model.load_ckpt` and `sample.generate_ids_fast`, on CPU;
- `lean_check.check`, the project's term-size definition.

**Running.**
- Paths assume a copy of the run repository at `~/review/kalmar-pretrain`; set `RV_ROOT` to override.
- Python 3: pure Python, except `tf_cpu.py`, which needs torch (`~/venv-cpu`).
- Lean 4.34.1, the pods' toolchain (`rlean.LEAN_BIN`; `LEAN=` for `lean_check`).
- Checkpoints come from the bucket into `~/review/kal_big/ckpts`.
- Every script writes its result to `out/` (the `*.log` / `*.txt` files are its saved stdout).

| script | recounts |
|---|---|
| `kc.py` | own formula parser, truth tables, renaming-class keys, **own Kalmár construction** (sl / pb) with per-action step tags and depths, pass@k |
| `rebuild.py` | K12-Kalmár and every read set rebuilt and compared with the stored proofs and tags (155,000 / 155,000 identical) |
| `lean_train.py` | own builder → own ND→Lean renderer → own harness on 614 theorems, with controls |
| `termsize.py`, `termsize_dev.py` | `lean_check` term size of training proofs (vs stored) and of deviating greedy proofs (vs the algorithm's) |
| `stats.py` | dataset statistics for all 155,000 theorems: K12, sl, pb |
| `tf.py`, `tf_cpu.py` | E1 from the stored verdict strings with own tags / depths / positions; verdicts re-derived on CPU for 1,727 states × 4 models |
| `free.py` | E2 / E3 / G1(b) and the greedy suites: success, exact-follow (text equality), deviations, cut-offs |
| `solve.py` | E4 solve tables (plain / guided / control k 256 / stored best-state reads), pass@k, strata, cut-offs |
| `gen.py` | G1–G3 construction checks; the pre-registered generalisation rule |
| `ladder.py` | Addendum 1 EI / frozen ladder from `found_<r>.jsonl`; Addendum 3 targets reads |
| `recheck.py`, `rlean.py` | Lean re-check of 1,050 counted literal texts and negative controls; prefilter rejects |
| `splits.py` | renaming-class disjointness of the training files and EI targets against every pool |
| `compute.py` | per-arm compute from the registry; training logs |
| `hygiene.py` | textbook72 sequents in the run's files (prints names only) |
| `phase2_checks.py` | phase 2: rr600 Q (380 vs 400), pooled atom / length strata, pooled cut-offs, TF compounding, leaf agreement by formula depth |
| `err_classes.py` | phase 2: own classification of KAL-D s2's 6,903 teacher-forced disagreements, and of the formulas they assert as false |
| `phase2_extra.py` | numbers found by the adversarial check of the review: PR-position shares, full-set term sizes (sl stored; K12 by a per-rule formula = lean_check 120 / 120), truncation bounds for rr600 Q, base-strata cut-off counts, guided = plain cells, longest algorithm action per set, replay pairs |
