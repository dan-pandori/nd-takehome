# olmo_rlzero_if — code and results of run olmo-rlzero-if

Write-up `../run_olmo_rlzero_if.md`; numbers `../numbers.md` § olmo-rlzero-if; pre-registration
`../preregistration/olmo-rlzero-if.md` (Part A before any pod, Part B after Stage 0 and before any evaluation sampling);
log `../log.md`; plain summary `plain_summary.md`. Bulk files (every sample's text and token ids, the graded rows, the
hand-check items and reader labels) are in `hf://buckets/dan-pandori/nd-rl/olmo-rlzero-if/artifacts/olmo_rlzero_if/`
and listed in `../artifacts/MANIFEST.jsonl` (`python3 fetch_artifacts.py artifacts/olmo_rlzero_if/`). No weights
were stored off the pods.

| file | what |
|---|---|
| `problems.jsonl`, `pids_*.txt`, `stage0_problems.jsonl` | the 450 evaluation prompts (IFBench 300, IFEval 150: `olmo_ifomega/problems.jsonl` rows, plus `ifomega_excl`); Stage-0 prompts (never evaluated) |
| `contamination.csv`, `exclusions.csv`, `manifest.csv` | 8-gram raw / content containment of every prompt in `Dolci-RL-Zero-IF-7B`; the 3 excluded and 6 read-and-kept prompts; one row per prompt with its flags |
| `jobs.csv` | every sampling job: model, phase (s0 / fixed / ext / confirm / diag), seed, draw order, n, prompt list, pod |
| `results.csv`, `passk.csv`, `dynamics.csv` | per model × prompt draws and successes by grade; unbiased pass@k with prompt-bootstrap intervals per prompt set (IFBench `h297` headline, `all300`, `s218`; IFEval `all150`); matched-k entries / exits |
| `candidates_fixed.csv`, `candidates.csv`, `verdict.csv` | candidates from the fixed phase; each candidate × model at 256 under `strict` and by hand; the verdict per task and grade |
| `handcheck.csv` (+ `handcheck_prompt_if.md`, `handcheck_rule_if_addendum.md`) | every hand-checked response: blinded item id, job, sample, model, side, role, reader label and evidence, my confirmation |
| `hand_summary.csv`, `gate_status*.csv` | gamed share of first-read strict successes; per candidate × model reading status |
| `failures_if.csv` (+ `failure_rubric_if.md`) | the format check (Design 6): classified base failures on the reach prompts |
| `weight_dist.csv`, `compute_axis.csv` | Stage-0 weight checks (`main` vs `step_1900`, the start revision); cumulative RL ÷ pretraining compute |

Code: `build_problems.py`, `contam.py`, `manifest.py`, `sample.py` (vLLM sampler at the RL-Zero-IF rollout settings),
`grade.py` (official IFBench / IFEval checkers on RL's answer extraction), `stage0.py`, `project.py`, `analyze.py`,
`interim_cands.py`, `partial.py`, `gate.py`, `handcheck.py`, `confirm_view.py`, `plan_ext.py`, `plan_confirm.py`,
`ext_state.py`, `verdict.py`, `summary.py`, `failures.py`, `figures.py`, `compute_rows.py`; pod scripts in
`../pod/olmo_rlzero_if/`.

**Recompute** (repository root, after fetching the bucket files): `python3 olmo_rlzero_if/analyze.py` (results, passk,
dynamics, candidates_fixed); `python3 olmo_rlzero_if/handcheck.py table artifacts/olmo_rlzero_if/hand`;
`python3 olmo_rlzero_if/verdict.py`; `python3 olmo_rlzero_if/summary.py`; `python3 olmo_rlzero_if/failures.py
table_if artifacts/olmo_rlzero_if/fail1`; `python3 olmo_rlzero_if/figures.py`. Re-grade any samples file with
`python3 olmo_rlzero_if/grade.py <samples.jsonl.gz> olmo_rlzero_if/problems.jsonl <out.jsonl>` (needs the IF checkers'
dependencies: langdetect, nltk with punkt / punkt_tab / stopwords / averaged_perceptron_tagger_eng, emoji, syllapy,
absl-py, immutabledict).
