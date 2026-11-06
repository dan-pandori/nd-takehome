# olmo_ifomega — code and results of run olmo-ifomega

Write-up `../run_olmo_ifomega.md`; numbers `../numbers.md` § olmo-ifomega; pre-registration
`../preregistration/olmo-ifomega.md` (Part A before any pod, Part B after Stage 0 and before any evaluation sampling,
Part C before the failure analysis's reading, deviations at the end); log `../log.md`; plain summary
`plain_summary.md`; scale-up memo `scaleup_memo.md`. Bulk files (every sample's text, grades, contamination scans) are
in `hf://buckets/dan-pandori/nd-rl/olmo-ifomega/artifacts/olmo_ifomega/` and listed in `../artifacts/MANIFEST.jsonl`
(`python3 fetch_artifacts.py artifacts/olmo_ifomega/`). No weights were stored off the pods.

| file | what |
|---|---|
| `problems.jsonl`, `pids_*.txt`, `families.csv` | the evaluation prompts (IFBench 300, IFEval 150, OMEGA explorative `test_out` 100 and `test_in` 100 — `test_in` was cut) at pinned revisions, the per-task id lists, the OMEGA family census |
| `contamination.csv`, `exclusions.csv`, `manifest.csv` | 8-gram containment of each prompt in Dolci-Think-RL-32B / DPO-32B / SFT-32B; the 82 IFBench prompts excluded from the headline (base request in the Think SFT data); one row per prompt with its flags |
| `jobs.csv` | every sampling job: model, phase (s0 / fixed / ext / confirm), seed, draw order, n, prompt list, pod |
| `results.csv` | one row per model × prompt: draws, successes under each grade (all / fixed), first and second success draws, tokens, cut-offs |
| `passk.csv`, `dynamics.csv` | unbiased pass@k with prompt-bootstrap intervals; matched-k expected entries / exits vs `dpo` |
| `candidates_fixed.csv`, `candidates.csv`, `verdict.csv` | candidates from the fixed phase; each candidate × model at the 256 cap under each grade; the pre-registered verdict per task and grade |
| `handcheck.csv` (+ `handcheck_rule_if.md`, `handcheck_prompt_if.md`, `handcheck_prompt_omega.md`) | every hand-checked response: blinded item id, job, sample, model, side, role, reader label and evidence, my confirmation |
| `constraints.csv`, `constraints_by_id.csv`, `constraints_summary.csv`, `rl_if_ids.csv`, `ifbench_rl_map.csv` | per-constraint analysis (Design 6): binding constraint of each candidate, per-id rates per model, similarity of each IFBench constraint to RL's IF data |
| `failures_if.csv`, `failures_if_by_id.csv`, `failures_omega.csv` (+ `failure_rubric_if.md`, `failure_rubric_omega.md`) | failure-mode analysis (Part C, secondary): `dpo`'s failures on the reach prompts by class, per constraint id and family |
| `compute_axis.csv`, `lengths_mix.csv`, `compute_extra.csv` | cumulative RL ÷ pretraining compute at steps 100 / 750 / 2,300 (low / middle / high); response lengths in RL's prompt mix; compute of jobs without a final meta |
| `stage0_summary.json`, `stage0_problems.jsonl` | Stage-0 measurements (never an evaluation number) |

Code: `build_problems.py`, `contam.py` (+ `contam_template_df20.json`), `exclusions.py`, `manifest.py`, `stage0.py`,
`project.py`, `sample.py` (vLLM sampler at the Think RL rollout settings; `--stop_after` sequential stopping,
`--stop_file` budget stops), `grade.py` (official IFBench / IFEval checkers in `vendor/`, OLMES-style exact match and
open-instruct's MathVerifier via `../olmo32/grade.py`), `analyze.py`, `plan_ext.py`, `plan_confirm.py`,
`ext_state.py`, `verdict.py`, `handcheck.py`, `constraints.py`, `failures.py`, `lengths_mix.py`, `compute_axis.py`,
`figures.py`, `compute_rows.py`, `peek.py`, `repair_gz.py`, `vllm_log_tokens.py`; pod scripts in
`../pod/olmo_ifomega/` (`runq.sh` job queue, `job.sh`, `restart_after_chunk.sh`, `runq_after.sh`, `w.sh`).

**Recompute** (repository root, after `python3 fetch_artifacts.py artifacts/olmo_ifomega/`):
`python3 olmo_ifomega/analyze.py` → results / passk / dynamics / candidates_fixed; `python3 olmo_ifomega/verdict.py`
→ candidates / verdict; `python3 olmo_ifomega/handcheck.py table artifacts/olmo_ifomega/hand` → handcheck.csv;
`python3 olmo_ifomega/constraints.py`; `python3 olmo_ifomega/failures.py table_if artifacts/olmo_ifomega/failures_if` (and `table_omega
artifacts/olmo_ifomega/failures_omega`);
`python3 olmo_ifomega/lengths_mix.py && python3 olmo_ifomega/compute_axis.py olmo_ifomega/lengths_mix.csv`;
`python3 olmo_ifomega/figures.py`. Re-grade a samples file with `python3 olmo_ifomega/grade.py <samples.jsonl.gz>
olmo_ifomega/problems.jsonl <out.jsonl>`.
