# olmo_ifcurve — code and results of run olmo-ifcurve

How instruction following changes over Olmo 3.1 Think 32B's RL run (proposal 46). Write-up `../run_olmo_ifcurve.md`;
numbers `../numbers.md` § olmo-ifcurve; pre-registration `../preregistration/olmo-ifcurve.md` (written before any pod;
amendments 1–5 during the run, each before the draws it changes); log `../log.md` § olmo-ifcurve; plain summary
`plain_summary.md`; figure `../figures/olmo_ifcurve.png`. Bulk files (every sample's text and token ids, every grade)
are in `hf://buckets/dan-pandori/nd-rl/olmo-ifcurve/artifacts/olmo_ifcurve/` (`samples/`, `graded/`). The stored
olmo-ifomega / olmo-iffu samples it reuses are in those runs' bucket paths (`python3 fetch_artifacts.py
artifacts/olmo_ifomega/samples/F_dpo_ifb.jsonl.gz …`; list in `reuse_inventory.csv`). No weights were stored off the pods.

| file | what |
|---|---|
| `checkpoints.csv` | every model revision: commit, LFS digest of the 14 weight shards, tokenizer / config / template blob ids (`main` = `step_2300` by shard hashes) |
| `pids_armA.txt`, `pids_reach.txt`, `plan/` | the 218 arm-A prompts, the 48 reach prompts; every job's pid:n spec and the pod queues |
| `reuse_inventory.csv` | which stored draws are reused per checkpoint and arm, and why others are re-sampled |
| `jobs.csv`, `compute.csv` | sampling jobs; per job run: GPU-seconds (load + generation, 1 × H200, TP 1), generated tokens, draws (registry rows via `compute_rows.py`) |
| `results.csv` | one row per arm × checkpoint × prompt cell: draws, strict, cut, tokens; arm B: genuine / gamed labelled, unlabelled, first-4 labels, estimated genuine rate, extension counts |
| `passk.csv` | arm A strict pass@1 / 2 / 4 / 8 per checkpoint, overall and per family, prompt-bootstrap 95 % |
| `emergence.csv` | per reach prompt: class (and the ifbench_154 rule-3 class), F1, F2, F1\*, F25, category, rate at F1\*, the extension cell, estimated genuine rate per checkpoint |
| `gaming.csv` | arm C sample and arm B first-4 gamed shares per checkpoint |
| `lengths.csv` | arm D medians (thinking / answer tokens and words), cut and no-`</think>` shares per checkpoint and set |
| `summary.json`, `gate_summary.json` | the readings with their intervals; hand-gate volumes |
| `handcheck.csv` | every hand-read item: draw, checkpoint, reads, final label, state, my note (adjudications) |
| `handcheck_prompt_if.md` | the reader prompt (olmo-ifladder's, run name changed) |
| `handcheck_rule_addendum.md` | dated rules 13–14 (keyword stuffing on ifbench_0 / 1 / 4) and the audit record; rules 1–12 are olmo-ifomega's, olmo-iffu's and olmo-ifladder's |
| `stage0_projection.json` (in `../artifacts/olmo_ifcurve/meta/`) | stage-0 measurements and the re-cost |

Code: `cells.py` (row caches from samples + grades; the cell definitions and the reuse order), `hand.py` (rule-1
screen, identity inheritance, the arm-B walk, the arm-C sample, item kit and rounds), `adjudicate.py` (adjudication and
consistency-audit tasks for sub-agents; my accepted proposals go to `../artifacts/olmo_ifcurve/hand/confirm.csv`),
`analyze.py`, `figures.py`, `stage0.py`, `compute_rows.py`, `numbers_section.py`, `reader_task.sh`. Pod scripts:
`../pod/olmo_ifcurve/` (`setup.sh` with the GPU health gate, `job.sh`, `worker.sh`, `start.sh`, `launch.sh`, `reap.sh`;
pod creation over RunPod REST v2: `rp2.py`, `podnew2.sh`, `podrm2.sh`, `orphans.sh`, `poll_pod2.sh`, `acquire*.sh`).
Sampler: `../olmo_ifladder/sample.py`, unchanged. Grader: `../olmo_ifomega/grade.py`.

**Recompute** (repository root; fetch the samples first: `python3 fetch_artifacts.py artifacts/olmo_ifcurve/ ` plus the
stored jobs in `reuse_inventory.csv`): `python3 olmo_ifcurve/cells.py rows <job> …` for every job in `jobs.csv` and the
stored ones → `python3 olmo_ifcurve/hand.py screen <job> …` → `python3 olmo_ifcurve/hand.py status` (0 pending) →
`python3 olmo_ifcurve/hand.py table` → `python3 olmo_ifcurve/analyze.py --reps 10000` → `python3 olmo_ifcurve/figures.py`.
Re-grade a samples file with `python3 olmo_ifomega/grade.py <samples.jsonl.gz> olmo_ifomega/problems.jsonl <out.jsonl>`.
