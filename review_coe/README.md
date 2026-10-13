# review_coe — reviewer's recount kit for run `create-or-elicit`

Written by the reviewer (agent:claude, 2026-10-13), independently of `coe/`. Nothing here imports `coe/`, `patterns.py`,
`gen.py`, `intuit.py`, `lean_judge.py` or `nd_verify`.

**Running it.** Paths assume a copy of the run repository at `~/review/create-or-elicit` (`RV_ROOT` overrides) and a
scratch directory `~/review/coe_big` for bucket files. Pure Python + scipy / numpy; Lean 4.34.1 (the pods' version, pinned
in `rlean.LEAN_BIN`) for the re-check. Other runs' files are read from `~/work/trajectory`, `~/work/rl-continue` and the
reviewer's own capability-defs outputs (`~/review/capability-defs/review_cd/out_{bracket,sets}.json`). Every script prints
to stdout; the `*.log` beside it is its saved output, `out_*.json` its machine-readable result.

| script | recounts |
|---|---|
| `common.py` | own formula / ND parsers, G4ip, truth tables, σ / σ⁺ / lemma-route detectors, pruning, renaming-class keys |
| `k12ko.py`, `dose.py` | K12⁻ construction (removal, refill sources and filters, keys vs 100 data / target files, shape); dose sets |
| `families.py` | classical families, key-step / strict / original σ-covered member sets (vs the run's name lists) |
| `acq.py`, `analysis.py` | acquisition tables per read (x0 / x1 / guided; old seeds' e + h merged), exact tests, cut-offs per stratum; acquired during RL |
| `shares.py` | per-round training shares from `alloc_<r>.json`, first acquisition rounds |
| `found.py`, `found_all.sh` | every distinct accepted ladder proof (bucket `found_*`) classified by round: σ, σ⁺, σ via IMPI, lemma route, free positive reductio |
| `mixcheck.py` | every fine-tune mix record of the knockout / dose ladders attributed by identity (replay / K12-only / RL) |
| `cert.py` | K_train(16) from registry rows (incl. the fine-tune child), pooled and per-family certificates |
| `stdA.py` | compute-matched reach on the 322 (standard A) |
| `general.py` | held-out greedy (σ / non-σ), holdout250, textbook72 |
| `score.py` | teacher-forced log p of known σ proofs (E2, along the ladders) |
| `phase01.py`, `budget08.py` | Phase 0.1 ratio table; Phase 0.2 K values and compute-matched r8 sets at the five allocations |
| `recheck_collect.py`, `recheck_run.py`, `rlean.py` | Lean re-check of counted proofs + negative controls + the refill; term sizes |
| `dumpcheck.py` | the ladder's literal-text dump (knockout s1): accepted texts and prefilter rejects re-checked in Lean |
| `splits.py` | renaming-class disjointness of every training file vs every evaluation pool |
| `compute.py`, `iqm.py` | compute per arm from registry rows; IQM + bootstrap intervals |
