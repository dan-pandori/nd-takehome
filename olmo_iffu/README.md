# olmo_iffu — code and results of run olmo-iffu

Is olmo-ifomega's "reach" (Olmo 3.1 Think 32B RL `step_2300` confirmed, its DPO start with no genuine success in 256)
a token budget, a brevity habit, or a sampling budget? Write-up `../run_olmo_iffu.md`; numbers `../numbers.md`
§ olmo-iffu; pre-registration `../preregistration/olmo-iffu.md` (design and binding expectations before any pod; the
test-2c addition before any of its samples; deviations at the end); log `../log.md` § olmo-iffu; plain summary
`plain_summary.md`. Bulk files (every sample's text and token ids, every grade) are in
`hf://buckets/dan-pandori/nd-rl/olmo-iffu/artifacts/olmo_iffu/` and listed in `../artifacts/MANIFEST.jsonl`
(`python3 fetch_artifacts.py artifacts/olmo_iffu/`). No weights were stored off the pods.

Models: `dpo` = `allenai/Olmo-3-32B-Think-DPO` `main` (`97604023`); `s2300` = `allenai/Olmo-3.1-32B-Think` `main`
(`97ade57a` = `step_2300`); `s0750` = the same repository at `step_0750` (`418fb274`). 32 B, bf16, pretrained (Olmo 3
32B base → Think SFT → DPO → RL). Decoding as olmo-ifomega (`olmo_thinker` template, T 1, top-p 1, vLLM 0.11.0).

| file | what |
|---|---|
| `subsets.py` → `manifest.csv` | the review's 43 IFBench hand-reach prompts; test 2's seeded subset (seed 20261106, from the 42 left after excluding `ifbench_281`) and test 3's (seed 20261107, from the other 33); the three geometry and six IFEval prompts |
| `label_check.py` | the three geometry labels recomputed two ways (`--pairs` lists the reference pair sets): perp_055 = 15 (stored 17), 068 = 23, 069 = 14 |
| `build_problems.py` → `problems_geo.jsonl`, `problems_hint.jsonl`, `problems_hint2c.jsonl` | test 1's prompts (055 relabelled), the hinted prompts of tests 2 and 2c (`prompt_sample` = prompt + "\n\nAnswer in at most 60 words."; grading uses `prompt`) |
| `sample.py` | `olmo_ifomega/sample.py` + `--fill_context` (budget = 65,536 − prompt tokens) + `prompt_sample`; rows carry `prompt_tokens` and `max_tokens` |
| `grade_trunc.py` | test 1's grades at a 32,768-token truncation of each response |
| `jobs.csv` | every sampling job: model, test, engine seed, problems, n, prompts, pod |
| `results.csv` (`analyze.py`) | one row per job × prompt: draws, cut, token quantiles, grades, hand counts, budgets |
| `handcheck.csv` (`handcheck.py table artifacts/olmo_iffu/hand`) | every hand-read response: blinded item, job, prompt, draw, model, reader label and evidence, my confirmation; items, key and reader files in `../artifacts/olmo_iffu/hand/` |
| `handcheck_prompt_if.md`, `handcheck_prompt_omega.md` | the reader prompts (olmo-ifomega's, plus the hint note and the geometry crux question) |
| `handcheck_rule_omega.md`, `handcheck_rule_if_addendum.md` | my confirming rules, not given to readers (IF rules 1–5: `../olmo_ifomega/handcheck_rule_if.md`; rule 6 here) |
| `lengths_hint.csv` (`lengths_hint.py`) | answer words with and without the hint (`dpo`, `s2300`) |
| `status.csv` (`status.py`; `explanation` column added by the write-up's categorisation, see `../log.md`) → `../figures/olmo_iffu_status.png` (`figures.py`) | each reach prompt's status before and after each test |
| `summary.py` → `summary_tables.md` | the write-up's per-prompt tables (test 1 with binomial intervals; test 2 / 2c per prompt) from the files above |
| `compute_rows.py` | registry compute rows per job |

Pod scripts: `../pod/olmo_iffu/` (`setup.sh`, `job.sh`, `runq.sh`, `start.sh`, job specs in `jobs/`, the VPS-side
`poll_pod.sh`, `reap.sh`, `launch_t4.sh`, `launch_t2c.sh`, `finish_b.sh`, and the pod-side `cap32.sh`).

**Recompute** (repository root, after `python3 fetch_artifacts.py artifacts/olmo_iffu/` and, for `lengths_hint.py`,
`python3 fetch_artifacts.py artifacts/olmo_ifomega/samples/F_dpo_ifb.jsonl.gz artifacts/olmo_ifomega/samples/F_s2300_ifb.jsonl.gz
artifacts/olmo_ifomega/samples/F_dpo_ife.jsonl.gz artifacts/olmo_ifomega/samples/F_s2300_ife.jsonl.gz`):
`python3 olmo_iffu/handcheck.py table artifacts/olmo_iffu/hand && python3 olmo_iffu/analyze.py && python3
olmo_iffu/status.py && python3 olmo_iffu/lengths_hint.py && python3 olmo_iffu/figures.py && python3 olmo_iffu/summary.py`.
Re-grade a samples file (pod; the checkers need nltk / langdetect): `python3 olmo_ifomega/grade.py <samples.jsonl.gz>
<problems.jsonl> <out.jsonl>`, with test 1's `olmo_iffu/problems_geo.jsonl` (label 15) and test 2's hinted files.
