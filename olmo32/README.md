# olmo32 — code and results of run olmo-think32b

Write-up `../run_olmo_think32b.md`; numbers `../numbers.md` § olmo-think32b; pre-registration
`../preregistration/olmo-think32b.md` (Part A before any pod, Part B before any evaluation sampling); log `../log.md`;
plain summary `plain_summary.md`; scale-up memo `scaleup_memo.md`. Bulk files (every sample's text, grades, likelihood
scores, contamination scans) are in `hf://buckets/dan-pandori/nd-rl/olmo-think32b/artifacts/olmo32/` and listed in
`../artifacts/MANIFEST.jsonl` (`python3 fetch_artifacts.py artifacts/olmo32/`).

| file | what |
|---|---|
| `problems.jsonl`, `manifest.csv`, `exclusions.csv` | the 60 AIME 2025–26 problems (MathArena, from the pilot), contamination scores against Dolci-Think-RL-32B / DPO-32B / SFT-32B and the pilot's inherited flags; the one exclusion |
| `contamination_think.csv` | per problem × corpus: max 8-gram containment, documents ≥ 0.5, 13-gram hits, best document |
| `jobs.csv` | every sampling job: model, phase (s0 / fixed / ext / confirm / L), seed, draw order, pod |
| `results.csv` | one row per model × problem: attempts, successes under each grade (all / fixed), first and second success draws, tokens, cut-offs |
| `passk.csv`, `dynamics.csv` | unbiased pass@k with problem-bootstrap intervals; matched-k (k = 8) expected entries / exits vs dpo |
| `candidates_fixed.csv`, `candidates.csv`, `verdict.csv` | candidates from the fixed phase; each candidate × model at the 256 cap under rl / final / hand / strict hand; the pre-registered verdict per grade |
| `handcheck.csv` | every hand-checked solution: blinded item id, job, sample, model, side, every reader's label, my label and note |
| `likelihood.csv` | per scored solution: group, generator, per-token mean and whole-solution log-prob under dpo |
| `compute_axis.csv`, `lengths.csv` | cumulative RL ÷ pretraining compute (FLOPs low / middle / high, GPU-hours) at steps 100 / 750 / 2,300 |
| `stage0_summary.json` | Stage-0 measurements (AIME 2024, dpo) |

Code: `sample.py` (vLLM sampler, Think RL settings; `--stop_after` = sequential stopping on doubly-credited samples),
`grade.py` + `oi_math_utils.py` (open-instruct's MathVerifier as RL ran it, the final-answer grade), `analyze.py`,
`plan_ext.py`, `verdict.py`, `handcheck.py` (+ `handcheck_prompt.md`, `handcheck_crux_aime2025_28.md`,
`handcheck_rule_aime2025_28.md`), `ll_items.py`, `score_ll.py`, `ll_table.py`, `contam32.py`, `compute_axis.py`,
`project.py`, `stage0.py`, `vllm_log_tokens.py`, `compute_rows.py`, `figures.py`; pod scripts in `../pod/olmo32/`.

**Recompute** (repository root, after `python3 fetch_artifacts.py artifacts/olmo32/`): `python3 olmo32/analyze.py`
→ results / passk / dynamics / candidates_fixed; `python3 olmo32/verdict.py` → candidates / verdict;
`python3 olmo32/handcheck.py table artifacts/olmo32/hand` → handcheck.csv; `python3 olmo32/ll_table.py` →
likelihood.csv; `python3 olmo32/compute_axis.py olmo32/lengths.csv`; `python3 olmo32/figures.py`. Re-grade any sample
file with `python3 olmo32/grade.py <samples.jsonl.gz> olmo32/problems.jsonl <out.jsonl>` (needs sympy and
antlr4-python3-runtime 4.11 for the diagnostic `main` grade). Regenerate a blinded item from its key row with
`handcheck.py prep`.
