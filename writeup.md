# Bootstrapping a natural-deduction prover past its training length

> **EXECUTIVE SUMMARY — DRAFT, TO BE REWRITTEN BY THE HUMAN.** Everything below the summary is filled in
> with method details, tables and figures; every number is traceable via `numbers.md`.

## Executive summary (draft)

_(filled in at the end; see section "Headline" below for the current numbers)_

## 1. Setting and question

- Logic and format: `spec.md`; `nd_verify` is the only judge. A proof's length is its number of lines, premises included.
- Cap: every supervised training proof has verifier length ≤ 6 (asserted at load time, `train.py --cap 6`).
- Question: after training only on ≤ 6-line proofs, how far past 6 can RL against the verifier push the
  **robust frontier** L = the longest written length at which the model produced ≥ 5 distinct verifier-accepted
  proofs, and how does that compare with the same model simply resampled the same number of times (P)?

## 2. Stage 1 — data and supervised model

### 2.1 Generator (`gen.py`)
_(method text: forward mode, goal mode, lazy premises, ORE completion, dependency pruning, verification; histograms)_

### 2.2 Splits (`make_splits.py`)
_(disjoint by atom-renaming class; validation classes removed; renaming-overlap estimate; trivial fraction)_

### 2.3 Tokenisation: the choice that decides whether length generalisation is possible
_(rel vs abs with random start offset; results table)_

### 2.4 Model and training
_(4L d256 RoPE, 3,210,240 params, hyper-parameters, wall-clock; held-out by length; failure analysis)_

## 3. Stage 2 — expert iteration against the verifier
_(protocol, arms, control; per-round table; figures)_

## 4. Stage 3 — evaluation
_(the table; validation-36 by bin; test set lines verbatim)_

## 5. What limits the frontier
_(evidence)_

## 6. Limitations

## 7. What I would do next with another week

## Appendix: reproduction
See `README.md` (Reproduction section), `numbers.md`, `log.md`.
