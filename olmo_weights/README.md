# olmo_weights/ — run olmo-weights (Proposal 47)

How much Olmo 3's weights move between consecutive released checkpoints, for the 32B and 7B pipelines. Write-up:
`run_olmo_weights.md`. Numbers: `numbers.md` § olmo-weights. Pre-registration: `preregistration/olmo-weights.md`.
Plain summary: `plain_summary.md`.

## Manifest (Hub API only; no weights)

| file | what |
|---|---|
| `list_refs.py` → `manifest/refs.json` | every branch and commit of the 12 repos (2026-11-25) |
| `fetch_trees.py` → `manifest/trees/` | each revision's files with LFS sha256 and size |
| `hash_checks.py` → `manifest/hash_checks.json` | `main` / branch equalities and duplicates by shard hash |
| `check_headers.py` → `manifest/headers/` | real safetensors headers via range requests; layout check of all 453 checkpoints |
| `manifest.py` | stage-1 location rule, checkpoint list and jobs |
| `manifest/checkpoints.csv` | 453 checkpoints: label, repo, branch, **commit**, step, shard files, sizes, sha256 |
| `manifest/jobs.json` | 13 jobs, 469 downloads: members, chains with stage starts, pairs, Gram sets, LoRA |
| `manifest/stage1_locations.json` | the stage-1 locations, fixed before any download |
| `manifest/index/` | the index JSONs per layout |
| `steps_lr.md`, `lr.py`, `sources/` | optimizer steps and learning rates per stage, with sources (scripts at pinned commits) |

## Statistics (on pods)

**`engine.py`** streams one job shard file by shard file:
- downloads with hf_xet;
- checks each file's sha256 against the manifest;
- keeps whole shard files as bf16 on the GPU, with Belady eviction.

It writes per-tensor CSVs (float32 from bf16, float64 sums) to `artifacts/olmo_weights/stats/<job>/shard_<k>/`:
- **`iv`:** ‖Δ‖², ‖θ_a‖², ‖θ_b‖², numel, bitwise-equal and ≤ 1-ulp counts;
- **`lag`:** ⟨Δ_i, Δ_{i−L}⟩ for L = 1–3;
- **`st`:** ‖θ − θ_start‖², equal / ≤ 1-ulp counts against the start, ⟨Δ_i, θ_{i−1} − θ_start⟩;
- **`gram`:** Gram matrices of offsets;
- **`lora`:** ⟨θ_t − θ_DPO, ΔW⟩ for `lora_main`, `lora_ctrl` and 8 random rank-16 matrices.

Further files under `stats/<job>/`:
- `files.csv`: every file's download time and sha256 result;
- `summary.json`: wall time, compute time, bytes;
- `JOB_DONE`.

**Checks:**
- **`selftest.py`:** synthetic checkpoints against numpy, with negative controls. PASS on CPU, on GPU, and with a 4 KB
  cache.
- **`realcheck.py`:** numpy from the raw safetensors bytes. PASS on 8 tensors of two real pairs
  (`artifacts/olmo_weights/stage0/stage0.log`).
- **`restage.py`:** re-shards the one checkpoint stored in another layout (`32B/sft5e-5/8000` = SFT `main`) byte for
  byte (`artifacts/olmo_weights/restage/`).

Pod scripts are in `pod/olmo_weights/`: `setup.sh`, `stage0.sh`, `run_jobs.sh`, `run_p32_sft.sh`, `bringup.sh`,
`podnew2.sh`.

## Analysis (VPS; csv + numpy + matplotlib)

| script | output in `artifacts/olmo_weights/tables/` |
|---|---|
| `agg.py`, `analyze.py` | `intervals.csv`, `modules.csv`, `layers.csv`, `chains.csv`, `tests.json`, `expectations.json`, `lora*.csv` |
| `report_tables.py` | `summary.md`, `stages.csv` |
| `figures.py` | `artifacts/olmo_weights/figures/fig1_32B.png`, `fig1_7B.png`, `fig2`–`fig7` |
| `compute_rows.py` | registry rows (compute per job) |

**To recompute an interval from the raw weights**, download the two checkpoints at the commits in
`manifest/checkpoints.csv` and compare with the job's `iv.csv.gz` rows (one per tensor). The interval's relative
change is √(Σ d2 / Σ na2) over the tensors.
