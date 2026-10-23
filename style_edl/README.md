# style_edl — does EDL rise with proof style when capability is fixed? (run `style-edl`, proposal 32)

Pre-registration: `preregistration/style-edl.md` (+ Addendum 1). Write-up: `run_style_edl.md`, `run_style_edl_plain.md`,
`numbers.md` § style-edl, `figures/style_edl.png`.

| file | what |
|---|---|
| `common.py` | proof → (state, action) pairs with one name base per theorem; scoring in bits, names the environment assigns not coded; A_ES (`finetune_es`) and A_fixed (`finetune`) |
| `split.py` | theorem sampling and the stream / test split by renaming class; literal `lean_seq` text → tokens |
| `pilot_own.py` | the S_own pilot on the VPS CPU, run before the pre-registration |
| `search_short.py` | S_short's proofs (`minlen.Search`, bound 14, as `proof_strategies/search_proofs.py`) |
| `build_streams.py` | eligibility, the 256 theorems, six streams × three seeds, Lean on every candidate, `streams_manifest.json` |
| `edl_run.py` | the prequential EDL runner for one seed × stream: every lr and order, per-proof bits per block, θ* saving, ℓ_V with `--vset` |
| `make_cap_queue.py`, `make_lv_queue.py` | the capability-read and ℓ_V queues, from the chosen lrs (`artifacts/style_edl/chosen_lr.json`) |
| `build_vset.py` | V(x): every distinct Lean-valid proof collected for each theorem |
| `analyze.py` | `results.csv` from the stored losses: EDL, EDL_c, cross-fit, A1 attribution, ℓ_V, re-fit check, capability |
| `verdict.py` | the pre-registered decision rule → `artifacts/style_edl/verdict.json` |
| `term_sizes.py` | term size (`lean_check`) of every stream proof; re-checks them with Lean (638 / 638) |
| `compute_rows.py` | compute per arm from the results-registry rows → `artifacts/style_edl/compute.csv` |
| `numbers_section.py` (+ `numbers_header.md`, `numbers_footer.md`) | the `numbers.md` section |
| `figure.py` | `figures/style_edl.png` |
| `streams_manifest.json` | theorem ids, split, classes, sources, sha256 of every proof and file |
| `results.csv` | one row per learner seed × stream |

**Order of the run** (`pod/sedl/`): `q1_reads.sh` and `q1_minlen.sh` → `build_streams.py` (VPS) → `q2_pilot.sh` (S_own,
seed 0) → `q3_edl.sh` (+ `q3k_kal.sh` on the second pod) → `q3x_xfit.sh` / `q3x2.sh` (cross-fit) → `make_cap_queue.py` →
`q4_cap.sh` / `q4k_cap.sh` → `build_vset.py` → `make_lv_queue.py` → `q5_lv_a.sh` / `q5_lv_b.sh` → `q6_redo.sh` (one guided
read redone after an OOM) → `analyze.py --fixed_E 4`, `verdict.py`, `compute_rows.py`, `numbers_section.py`, `figure.py`.

**For the reviewer.**
- Rebuild a stream: run `build_streams.py` on the bucket's `artifacts/style_edl/reads/` and compare with the manifest's
  sha256.
- Lean: `term_sizes.py` re-checks every stream proof.
- EDL from the stored per-block losses: `analyze.run_stats` (EDL, EDL_c) and `lv_stats` (ℓ_V), from
  `artifacts/style_edl/{edl,edl_x,lv}/s{s}/{stream}.json`.
- Class disjointness of stream and test: asserted in `split.sample_and_split`; the classes are in the manifest's `pkey`.
- θ* behind each pass@32: `artifacts/style_edl/cap/s{s}_{stream}__plain_k32_seed2.json.args.json` names the checkpoint.
