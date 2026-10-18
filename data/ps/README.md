# data/ps — inputs and searched proofs of run proof-strategies

Inputs were copied (not linked) into `data/ps/in/` (gitignored):

| file | origin | check |
|---|---|---|
| `train_k12.jsonl.gz` | `best-state/data/kh/` = `hf://buckets/dan-pandori/nd-rl/cap-horizon/data/kh/train_k12.jsonl.gz` | uncompressed md5 800b5486… (155,000) |
| `train_depth3_f0_a1.jsonl.gz` | gzip of `best-state/data/p2/train_depth3_f0_a1.jsonl` (= `state-env/data/p2/` in the bucket) | uncompressed md5 29276f24… (155,000) |
| `train_k12ko.jsonl.gz` | `create-or-elicit/data/coe/` (bucket `create-or-elicit/data/coe/`) | gz md5 6326ebdd… (155,000) |
| `train_k12dose1.jsonl.gz` | `create-or-elicit/data/coe/` | gz md5 7433f6ac… (155,000) |
| `charles/*.jsonl` | nd-rl `origin/charles/main` 297dcbdd, `data/textbook_problem/release_2026-10-02/` | **private (nd-rl): local only, never uploaded** |

Tracked in git: the pools `data/ladder/rl_targets.jsonl`, `data/ladder/transfer.jsonl`, `data/bs/holdout250.jsonl`, and
`data/bs/textbook72.jsonl`, which is sealed (scoring only; never printed).

- `pod/`: inputs of the pod jobs (log.md, 2026-10-18).
  - `k12_min990.jsonl`: 90 K12 records per length 2–12, seed 0.
  - `k12_nec594.jsonl`: 54 per length, seed 1.
  - `tb_schema.jsonl`: the 1,610 textbook-schema instances of the three pools.
  - `charles_base.jsonl` (private) and `textbook72.jsonl` (sealed) are gitignored.
- `search/*.jsonl`: `proof_strategies/search_proofs.py` output.
  - `*.checked.jsonl` add the Lean verdict (`check_search.py`).
  - Uploaded to the bucket except `textbook72*`, whose proofs stay local.
- `nec/*.jsonl`: `proof_strategies/necessity_ps.py` output.
  - `*.checked.jsonl` add Lean verdicts.
  - Uploaded except `charles*` (private) and `textbook72*` (sealed).
- `validation/`: blind spot-check sample, checker labels and key; the second implementer's fixtures.

Bucket: `hf://buckets/dan-pandori/nd-rl/proof-strategies/data/ps/` (the uploadable files above) and
`…/proof-strategies/artifacts/ps/` (label files, theorem-level files, RL-mix inputs are NOT re-uploaded: they are
create-or-elicit's, under `create-or-elicit/artifacts/coe/ladder/`).
