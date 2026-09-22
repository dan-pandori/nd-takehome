# STATUS — lean-only (proposal 9)

Brief: BRIEF_LEAN_ONLY.md. Run id: lean-only. Authorised by Dan 2026-09-22.

## lean-only — started 2026-09-22 05:55 UTC (executor agent:claude)
- 06:05  BOTE fix pulled from `dan_lean_seed2` (39bdc5b: `nd2lean.py`, `lean_tok.py`); pre-registration `preregistration/lean-only.md` committed before any `lo-*` pod (phase-1 expectations P1-1…P1-6, phase-2 predictions E1…E13). Next: pod `lo-1` (RTX 3090) for phase 1: `lean_check`, `term_size`, tests, agreement tables, throughput, pool relabelling.
- 06:40  Phase 1 done: `lean_check` 30/30 tests, 253,397/253,397 pool proofs agree with `nd_verify`, 0/4,012 negatives, 460 texts 206 rej / 254 acc (by kind as predicted), 85 proofs/proc-s; pools relabelled (`data/lo/`, `ts_minlen`); free-form renderer round-trips 155k proofs (8.0 tokens/proof). Pre-registration addendum written. Next: smoke test of the EI training path, then phase-2 jobs on `lo-1` … `lo-6`.
