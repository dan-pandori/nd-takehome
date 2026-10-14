# review_coep — reviewer's recount kit for run `create-or-elicit-paper`

Written by the reviewer (agent:claude, 2026-10-14), independently of `coe/`, `paper/scripts/`, `review_coe/rlean.py`,
`lean_gate`, `lean_judge`, `nd2lean`, `lean_tok` and `nd_verify`. Paths assume a copy of the run repository at
`~/review/create-or-elicit-paper` (`RV_ROOT` overrides) and bucket files in `~/review/coep_big`. Pure Python; Lean 4.34.1
(`RV_LEAN`). Each script prints to stdout; the `*.log` beside it is its saved output, `out_*.json` its result.

| script | recounts |
|---|---|
| `common.py` | loaders: strict 106, families, bars, reads, cut-offs |
| `checks.py` | C1 (std vs dbl caps), C2 (dose x1 + guided), C3 (textbook72 pend, 6-vs-6 gap) |
| `paired.py`, `cutoff_types.log` | whether C1's two reads are paired draws; cut-offs by cap |
| `c4.py` | C4 per-member successes at n = 18,432 and the pre-registered expectations |
| `lean4.py` | own Lean harness: statement builder, ND→Lean renderer, chunked checker with `#print axioms` |
| `harness_controls.py`, `flipcheck.py` | positive / negative controls of the harness |
| `c5_sample.py`, `c5_full.py` | C5: the knockout s1 dump's rows, distinct pre-filter rejects, all of them through Lean |
| `recheck.py` | Lean re-check of counted proofs per arm (every solved member of every read), line counts, term sizes |
| `prior.py` | A2, A3, A3b, A4, A5, A5b |
| `descr.py` | addendum-5 descriptives; own one-sided Boschloo |
| `splits.py` | renaming-class disjointness of the evaluation pools vs every training file |
| `compute.py` | GPU-seconds, attempts, tokens, Lean texts per check |
