# olmo_lowrank — code and results of run olmo-lowrank (proposal 49)

Is RL's change to Olmo 3's weights low-rank, and does its low-rank part carry RL's IFBench gain? Write-up
`../run_olmo_lowrank.md`; numbers `../numbers.md` § olmo-lowrank; pre-registration `../preregistration/olmo-lowrank.md`;
log `../log.md` § olmo-lowrank; plain summary `plain_summary.md`; figure `../figures/olmo_lowrank.png`.

Models: released AI2 checkpoints only (bf16, pretrained; none trained here). Every checkpoint with repo, branch, commit
and shard sha256: `manifest_checkpoints.csv` (from `olmo_weights/manifest/checkpoints.csv`); every adapter with its
bucket path and sha256: `manifest_adapters.csv`.

## Part 1: spectra (pod: `spectra.py`; VPS: `analyze_spectra.py`)

| file | what |
|---|---|
| `plan_spectra.py` → `plan/spectra_jobs.json` | jobs R32 (32B RL: dpo + 10 RL steps), S32 (32B base / SFT / DPO), R7 (7B, 12 checkpoints), the changes of each |
| `linalg.py` | randomized SVD (p 64, q 16 chosen at stage 0), float64 Gram spectra, rounding floors A / B, overlaps |
| `spectra.py` | the engine: downloads at pinned commits with sha256 checks, per matrix and change: exact norm, top-256, full spectrum, floor B; floor A; LoRA overlaps; `--selftest` (planted subspaces, sign-flip control) |
| `tables/matrices_<job>.csv.gz` | one row per change × matrix (= `artifacts/olmo_lowrank/spectra/<job>/rows.csv`) |
| `tables/overlap_R32.csv.gz` | LoRA overlaps and inner products per net change × matrix × adapter |
| `tables/changes.csv`, `by_type.csv`, `by_depth.csv`, `accuracy.csv`, `lora.csv`, `expectations_part1.json` | aggregates (`analyze_spectra.py`) |
| `stage0_svd.py` | stage-0 SVD timing and accuracy (`../artifacts/olmo_lowrank/stage0/svd_timing.json`) |

Full spectra (`full_*.npz`) and top-256 values (`sigma_*.npz`) are in the bucket under
`artifacts/olmo_lowrank/spectra/<job>/`; the exact SVD spectra of RL's change used for the adapters are under
`artifacts/olmo_lowrank/adapters_svd/`.

## Part 2: truncation arms

| file | what |
|---|---|
| `adapters.py` | exact SVD of D = s2300 − dpo, the T_k / C16 / Z8 adapters (PEFT, fp32), their check, the F448 builder and its check |
| `zero_check.py` | the zero-delta check of vLLM's LoRA path (`../artifacts/olmo_lowrank/stage0/zero2_diff.txt`) |
| `plan/arm.pids` | each arm's prompts and draws (48 reach × 16, 176 others × 4) |
| `cells.py` | row caches (`cells.py rows <job>`), draw counts (`cells.py check`) |
| `hand.py`, `adjudicate.py`, `reader_task.sh`, `handcheck_prompt_if.md` | the hand gate (screen, rounds, cells, calibration) and the audits |
| `handcheck.csv`, `hand_cells.csv`, `hand_arm_summary.csv` | every hand-read item; per cell and per arm genuine estimates |
| `analyze.py` → `results.csv`, `summary.json` | G per arm and metric with paired prompt-bootstrap intervals; the readings |
| `compute_rows.py` → `compute.csv` | registry compute rows |
| `figures.py`, `numbers_section.py`, `mdd_sim.py` | the figure, the numbers.md section, the pre-registration power check |

Pod scripts: `../pod/olmo_lowrank/` (`setup.sh`, `bringup0/1/2.sh`, `stage0.sh`, `after0.sh`, `job.sh`, `worker.sh`,
REST v2 pod creation `podnew2.sh` / `podrm2.sh` / `rp2.py`).

## Recompute (repository root)

1. `python3 fetch_artifacts.py artifacts/olmo_lowrank/`.
2. Fetch the stored endpoints: `artifacts/olmo_ifcurve/samples/B_s2300.jsonl.gz`, its graded file, and olmo-ifomega's
   `F_dpo_ifb` / `F_s2300_ifb`.
3. `python3 olmo_lowrank/cells.py rows dpo T1 T4 T16 T64 T256 F448 C16 B_s2300 F_s2300_ifb F_dpo_ifb`.
4. `python3 olmo_lowrank/hand.py screen dpo T1 T4 T16 T64 T256 F448 C16 B_s2300 && python3 olmo_lowrank/hand.py status`
   (0 pending).
5. `python3 olmo_lowrank/hand.py cells && python3 olmo_lowrank/hand.py table && python3 olmo_lowrank/analyze.py --reps 10000`.
6. Spectra: `python3 olmo_lowrank/analyze_spectra.py`.
7. `python3 olmo_lowrank/figures.py`.

To re-grade a samples file: `python3 olmo_ifomega/grade.py <samples.jsonl.gz> olmo_ifomega/problems.jsonl <out.jsonl>`.

**Reviewer checks:**
- Recompute a seeded matrix's spectrum from the raw weights: download the two checkpoints at the commits in
  `manifest_checkpoints.csv`, take float32 differences, and compare with `tables/matrices_<job>.csv.gz`.
- Check an adapter: B A against the exact SVD truncation of D.
