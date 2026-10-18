# review_ps — reviewer kit for run proof-strategies (2026-10-18)

Independent of `proof_strategies/` (written from the pre-registration and TAXONOMY.md §1–§5 with numbers masked).
Run from this directory (`cd review_ps`); inputs are the run's `data/ps/in/` (copied, gitignored), `data/ladder/`, `data/bs/`,
`data/ps/search|nec/` and the executor's `artifacts/ps/` label files (bucket `proof-strategies/artifacts/ps/`).

| script | what |
|---|---|
| `nd.py` | ND formula / proof parser and an ND rule checker written from spec.md (sanity only) |
| `cls.py`, `run_sets.py`, `agg.py`, `summary.py` | the 13-strategy classifier (uses, working, sub-types, primary, curried, v0 variants); per-set labels and shares |
| `cmp.py`, `cmp_thm.py` | per-record comparison with the executor's labels / theorem files |
| `ipc.py`, `theorems.py` | own G4ip (Dyckhoff LJT) + truth tables: classical-only, dneg, σ-covered (both definitions), inconsistent premises |
| `lean.py`, `controls.py`, `recheck.py`, `rl_recheck.py` | own ND→Lean renderer + Lean 4.34 batch checker (axioms check), controls first, then every search / necessity proof, Charles's reference proofs, generator samples, RL samples |
| `tsize.py` | term-size formula vs executor `ts` and vs lean_check on own renderings |
| `sealkey.py`, `examples_check.py`, `leakscan.py` | textbook72 class keys; canonical-example checks; committed-file scan for sealed / private material |
| `rl_recount.py`, `rl_cmp.py` | RL found-file recount per ladder (streams create-or-elicit `found_16.jsonl`), comparison with `rl_found.json` |
| `tables_md.py` | the markdown tables of review §Recount, from `out/` |

Large per-record outputs (`labels_{k12,cap6,k12ko,k12dose1}`, `thm_*` of those sets) and anything about Charles's release
(private) or textbook72 (sealed) are not committed; each regenerates in < 1 min (`python3 run_sets.py k12 ../data/ps/in/train_k12.jsonl.gz proof`).
