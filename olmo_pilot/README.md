# olmo_pilot — code and results of run olmo-rlzero-pilot

Write-up: `../run_olmo_rlzero_pilot.md`; numbers: `../numbers.md` § olmo-rlzero-pilot; pre-registration:
`../preregistration/olmo-rlzero-pilot.md`; log: `../log.md`; plain summary: `plain_summary.md`; 32B memo:
`decision_32b.md`. Bulk files (samples, grades, likelihood scores) are in the bucket
`hf://buckets/dan-pandori/nd-rl/olmo-rlzero-pilot/artifacts/olmo_pilot/` and listed in `../artifacts/MANIFEST.jsonl`
(`python3 fetch_artifacts.py artifacts/olmo_pilot/`).

| file | what |
|---|---|
| `problems.jsonl`, `manifest.csv` | 120 problems (AIME 2023 pilot + 90 evaluation) with source, answer, contamination scores and flags |
| `exclusions.csv` | the 7 excluded evaluation problems and why |
| `contamination_dolci.csv`, `contamination_midtrain.csv`, `nearest_embed.csv` | n-gram / IDF / embedding matches against the RL data and the midtraining math subsets |
| `jobs.csv` | every sampling job: model, step, phase (pilot / fixed / confirm / extension / probe / void), seed |
| `results.csv` | one row per model × problem: attempts, successes under each grade (all / fixed phase / confirmation), first correct draw, tokens, cut-offs |
| `passk.csv`, `reach.csv`, `dynamics.csv`, `candidates.csv` | pass@k with bootstrap CIs; reach / reverse / expected entries and exits; fate of every candidate |
| `likelihood.csv` | per scored solution: generator, group, mean / sum log-prob under the base and its generator |
| `lengths.csv`, `compute_axis.csv` | mean lengths and cumulative RL ÷ pretraining compute (low / high) |
| `gate_spec.json`, `stage0_summary.json` | speculative-decoding gate; Stage-0 measurements |

Code: `sample.py` (vLLM sampler, RL settings; `--seq_stop` = sequential extension), `grade.py` + `oi_math_utils.py`
(open-instruct's MathVerifier, vendored, run as RL ran it), `analyze.py`, `candidates.py`, `ll_items.py`,
`score_ll.py`, `ll_plan.py`, `contam.py`, `midscan.py`, `nearest_embed.py`, `lengths.py`, `compute_axis.py`,
`cost_model.py`, `compute_rows.py`, `figures.py`; pod scripts in `../pod/olmo_pilot/`.

**Recompute** (from the repository root, after fetching the bucket files): `python3 olmo_pilot/analyze.py --kstar 512`
→ `results.csv`, `passk.csv`, `reach.csv`, `dynamics.csv`; `python3 olmo_pilot/candidates.py`;
`python3 olmo_pilot/ll_plan.py table` → `likelihood.csv`; `python3 olmo_pilot/lengths.py` → `compute_axis.csv`;
re-grade any sample with `python3 olmo_pilot/grade.py <samples.jsonl.gz> olmo_pilot/problems.jsonl <out.jsonl>`.
Caveat: the sample texts of `F_base`, `P_base` and `g_spec_base` were lost with pod `orz-a` (host failure); their
grades (`graded/*.jsonl`, with the extracted "Answer:" integer) survive.
