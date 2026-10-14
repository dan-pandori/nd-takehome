# review_pc — reviewer kit for run paper-clean (2026-10-14)

Own code. Paths are those of the reviewer's phase-1 workspace (`~/review/paper-clean`, a copy of the run branch with
the executor's write-ups removed). `marked/` (nd-rl `7709669:docs/papers/create-or-elicit/`) and `prereview/` (nd-rl
`d841408`) were extracted there with `git archive` and are deliberately not committed (the marked §2 prints a theorem in
a sealed textbook72 class).

| file | what |
|---|---|
| `kit/numdiff.py` | number-by-number diff, marked vs clean (`\rv` / *[review]* unwrapped); output `numdiff.txt` |
| `kit/sealed.py` | own textbook72 sealed-class check (own parser, order-sensitive and premise-order-invariant keys, readings, masked hits); outputs `sealed_clean.txt`, `sealed_marked.txt` (positive control) |
| `kit/sigma_polarity.py` | own count of σ by goal polarity in D (item 1) |
| `kit/ndlean.py` | own ND → Lean 4 renderer + checker (no nd2lean, no lean_judge) |
| `kit/lean_checks.py` | harness controls, the 24 stored power-comparator proofs (item 12), the printed listings; output `out_lean.json` |
| `phase1/*.md` | four read-only sub-auditor reports (front, results, back, blog), clean vs marked, claim by claim |
