# Reviewer kit: olmo-rlzero-if (2026-11-08)

Reviewer code, independent of `olmo_rlzero_if/`. It reads the run's raw sample files read-only from the phase-1 workspace
`~/review/olmo-rlzero-if` (hard links: never write there). Scratch goes to `~/review/rzi_rv/` (not committed): upstream
fetches (`fetch_upstream.sh`), Hub files, the Dolci parquet, the pre-release dataset's prompts, hand-check item texts.

Python: `~/review/oif_venv` (nltk 3.9.2, langdetect 1.0.9, emoji 2.15.0, syllapy 0.8.0, immutabledict 4.2.2,
absl-py 2.3.1, tokenizers 0.22.2, pyarrow, huggingface_hub; see `review/olmo-ifomega-recount/README.md` on
`dan_olmo-ifomega`). Stdlib-only scripts run under plain `python3`.

| script | what it does | output |
|---|---|---|
| `fetch_upstream.sh` | IFBench `cd189a9c`, google-research `e6890f85`, open-instruct `d928a7c` / `7e780f2fea` / `e25a27b8` | `~/review/rzi_rv/upstream/` |
| `rv_hub.py` | Hub refs, file blobs and LFS sha256 of every branch (main vs step_*, base main vs stage3) | `~/review/rzi_rv/hf/hub_tree.json` |
| `rv_core.py` | loaders, RL's `remove_thinking_section` executed from my fetch of `ground_truth_utils.py` @ `d928a7c` | — |
| `rv_graders.py` | upstream IFBench / IFEval strict + loose, `random` re-seeded per check | unit checks |
| `rv_regrade.py` | re-grades all 143,176 texts; ids checks (decode == text, cap, EOS, tag-token counts), own `t1` | `out/regrade/*.jsonl` (local; committed as `out/regrade_all.jsonl.gz`) |
| `rv_gradecmp.py` | my grades vs the executor's `graded/` rows; storage integrity summary | `out/gradecmp.txt`, `out/decode_check.txt` |
| `rv_provenance.py` | prompts vs pinned datasets, the seeded IFEval subset, `ifomega_excl` | `out/provenance.txt` |
| `rv_contam.py` | own 8-gram raw / content containment vs Dolci-RL-Zero-IF-7B | `out/contam_mine.csv`, `out/contam_report.txt` |
| `rv_contam_pre.py` | the same vs the launch snapshot's pre-release dataset; seed-42 subsample reproduction | `out/contam_pre.txt` |
| `rv_cells.py`, `rv_stats.py` | cells in draw order; pass@k + bootstrap; lengths; candidates; strict fates and verdict; reverse; entries / exits | `out/cells.json(.gz)`, `out/stats.{json,txt}` |
| `rv_ext.py` | sequential-job stopping-rule audit, 256 cap | `out/ext.txt` |
| `rv_hand_items.py`, `rv_hand.py`, `rv_show.py` | blinded items by round; labels + my overrides -> hand status, verdict, gamed share, next needs; item viewer | `hand/key_r*.json`, `hand/batches_r*.json`, `hand/need_r*.json`, `out/hand.{json,txt}` |
| `rv_fail_items.py`, `rv_fail.py` | format-check draw and summary (Design 6) | `hand/fail_*.json`, `out/fail.{json,txt}` |
| `rv_embed.py` | embedded-answer diagnostic on the option / CSV hand-reach prompts (mine) | `out/embed.{json,txt}` |
| `rv_compute.py` | compute axis (pre-registered definitions, my lengths); per-job samples / tokens / time | `out/compute.{json,txt}` |
| `rv_weights.py` | weight-distance spot check and added-token embedding rows over HTTP range reads | `out/weights.{json,txt}` |
| `rv_stage0.py` | Stage-0 recount and the speculation A/B | `out/stage0.txt` |
| `rv_hand_compare.py` (phase 2) | the executor's `handcheck.csv` joined to my items on (job, pid, chunk, i): agreement, every disagreement with both evidences | `out/hand_compare.{txt,json}` |
| `rv_expect.py`, `rv_tables.py` | binding expectations vs recount; markdown tables generated from the json | `out/expect.md`, `out/tables.md` |

Hand-check files: `hand/reader_prompt_if.md` and `hand/failure_rubric_if.md` (the rubrics), `hand/reader_labels/` and
`hand/fail_labels/` (readers' JSON verbatim), `hand/confirm.json` (my overrides), `hand/fail_spot_check.json` (my reads
of a seeded 10 % of the format-check items). Item texts are regenerable with `rv_hand_items.py` / `rv_fail_items.py`.

**Phase 1 and phase 2.** `out/hand.{json,txt}` and `out/tables.md` are the phase-1 state as committed; `RV_PHASE1=1
python3 rv_hand.py` reproduces it. Phase-2 overrides in `hand/confirm.json` carry `"phase": 2`; `out/hand_phase2.{json,txt}`
hold the state with them.
