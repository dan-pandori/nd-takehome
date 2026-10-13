# Provenance of the snapshots in paper/data/

| file | source | commit | sha256 (first 16) |
|---|---|---|---|
| `capdefs_j3.json` | fork branch `dan_capability-defs`, `capability_defs/analysis/out/j3.json` (capability-defs J3 plain vs guided reads; = the reviewer's `review_cd/rv_j3.log`) | branch head `da11be78` (file last changed in `e84c9431`) | f9a7dec20b5257a5 |
| `mcts_a_summary.json` | fork branch `dan_mcts-a`, `artifacts/mcts/summary.json` | branch head `5e70afbd` (file last changed in `e288991e`) | 4d992ead1c19efe8 |

Computed by this run: `a3_member_prior.json` (`scripts/a3_member_prior.py`), `stats_extra.json` (`scripts/stats_extra.py`),
`lean_examples.json` (`scripts/lean_examples.py`), `checks_c1c3.json` (`scripts/checks_c1c3.py`).
