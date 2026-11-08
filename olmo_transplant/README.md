# olmo_transplant/ — run olmo-transplant (proposal 40)

Is Olmo 3.1 Think 32B's IFBench reach capability in its thinking? Stored thinking of `s2300` (genuine successes) and
`dpo` (failures) is re-inserted by token ids, and only the answer is sampled. Pre-registration
`preregistration/olmo-transplant.md`; write-up `run_olmo_transplant.md`; numbers `numbers.md` § olmo-transplant;
plain summary `plain_summary.md`.

## Pipeline (in order)

| step | script | output |
|---|---|---|
| index stored samples (VPS) | `scan_src.py` (needs `artifacts/olmo_transplant/src/*.jsonl.gz`, see below) | `src/index.jsonl` |
| prompts | `select_prompts.py` (seed 20261108) | `prompts.csv` |
| calibration source reads | `select_traces.py prep`, `handcheck.py` | `handcheck_src_items.csv`, `handcheck_src.csv` |
| trace manifest | `select_traces.py build` | `traces.csv` (source job / chunk / i, ids and prefix sha256, think_k, c, draft_k) |
| requests | `build_requests.py reach|calib` (asserts every prefix = stored ids [+ closing]) | `artifacts/olmo_transplant/requests/*.jsonl.gz` |
| sampling (pod) | `sample_prefix.py` (thinking prefix → answer), `fresh_bf.py` (F) via `pod/olmo_transplant/job.sh`, `fresh.sh` | `samples/<job>.jsonl.gz`, `meta/<job>.json`, `meta/<job>_boundary.txt` |
| grading (pod) | `grade_rows.py` (`olmo_ifomega/grade.py`, unchanged) | `graded/<job>.jsonl` |
| hand gate | `select_reads.py r1 / c1`, `handcheck.py prep / batch / table`; reader prompt `handcheck_prompt.md` | `artifacts/olmo_transplant/hand/run/` (items, key, labels), `handcheck.csv` |
| analysis | `analyze.py`, `mechanism.py`, `figures.py`, `numbers_section.py` | `results.csv`, `summary.md/.json`, `mechanism.md`, `figures/olmo_transplant.png` |
| compute | `compute_rows.py`, `headline_rows.py` (registry rows) | `compute.md`, `artifacts/olmo-transplant/registry/` |

Jobs: `R_dpo` / `R_s2300` (reach, writer = dpo / s2300, seeds 8101 / 8102), `C_dpo` / `C_s2300` (calibration, 8111 /
8112), `F_s2300` (fresh budget forcing, 8103). Tokenizer helper for the VPS (no transformers): `tok.py`.

## Source data

`artifacts/olmo_transplant/src/{F_s2300_ifb,C1_s2300_ifb,C2_s2300_ifb,F_dpo_ifb}.jsonl.gz` and `*_graded.jsonl` are
unmodified copies of `hf://buckets/dan-pandori/nd-rl/olmo-ifomega/artifacts/olmo_ifomega/{samples,graded}/` (not
re-uploaded; fetch with `hf buckets cp <uri> artifacts/olmo_transplant/src/<name>`).

## For the reviewer

- **Inserted traces = stored ids:** each request row (`requests/*.jsonl.gz`) carries `src` (job|pid|chunk|i), `cut` and
  `prefix` (base64 int32). The prefix is the stored `ids[:think_k]` (full), or `ids[:N]` / `ids[:draft_k]` + closing
  `[198 if the kept text does not end in a newline] + [524, 27963, 1363]`. T0 is `[198, 524, 27963, 1363]`. Every
  sample row carries `input_sha256` of (prompt ids + prefix) as int32 bytes. The job meta stores each pid's prompt ids
  (`prompt_ids`, base64).
- **Template boundary:** `meta/R_dpo_boundary.txt`, `meta/R_s2300_boundary.txt` (decoded prompt tail, prefix head,
  input tail for the first requests of every condition). `tok.py` decodes ids without transformers.
- **Re-grade:** `grade_rows.py` on any samples file (pod or any machine with the IFBench checker dependencies).
- **Hand gate:** `handcheck.csv` (one row per read item: key `job|rid|i`, all reader labels, majority, final);
  identity inheritance is by `(pid, whitespace-collapsed answer)`; `select_reads.py` logs what was inherited.
- **Paired contrasts:** `analyze.py` (bootstrap seed 1, 10,000 resamples) from `results.csv`-level counts.
