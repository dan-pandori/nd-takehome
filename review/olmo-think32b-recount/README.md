# Reviewer kit: olmo-think32b (2026-11-04)

Reviewer code, independent of `olmo32/`. Run from this directory, on the VPS, after the run's artefacts are present
(`artifacts/olmo32/samples/*.jsonl.gz` come from the bucket). Python: system `python3` for the stdlib-only scripts;
`~/review/ot32_venv` (sympy 1.13.3, antlr4 4.11.0, tokenizers, pyarrow, numpy) for the verifier, tokenizer and parquet
ones; `~/.local/share/uv/tools/huggingface-hub/bin/python` for Hub metadata.

| script | what it does | output |
|---|---|---|
| `rv_upstream.py` | imports open-instruct's own `ground_truth_utils.py` / `math_utils.py` at 7e780f2fea (`upstream/`) through stubs; RL path = `async_call` (worker thread) | unit checks |
| `rv_regrade.py` | re-grades every stored text: `rl` (RL path), `main` (main thread), own final-answer grader, storage checks | `out/regrade_*.jsonl` |
| `rv_gradecmp.py`, `rv_gradectl.py` | row-by-row comparison with the executor's graded rows; wrong-label negative control | `out/gradecmp.json`, `out/gradectl.txt` |
| `rv_decode.py` | text == decode(ids, skip_special_tokens) for all 3,456 samples | `out/decode_check.txt` |
| `rv_template.py`, `rv_hub.py` | template vs upstream olmo_thinker and meta sha; Hub commits, tokenizer blobs, shard hashes | `out/template_check.txt`, `out/hub.json` |
| `rv_manifest.py`, `rv_manifest_sha.py` | problems vs MathArena; bucket manifest sha256 / sizes | `out/manifest_*.txt` |
| `rv_contam.py`, `rv_contam_show.py` | own 8-/5-gram containment over all Dolci-Think-RL-32B prompts | `out/contam_rl*.{json,txt}` |
| `rv_core.py` | loaders (my re-grade rows; draw order) | — |
| `rv_cells.py`, `rv_stats.py` | per-cell table; pass@k + bootstrap, entries/exits, candidates, lengths | `out/cells.csv`, `out/stats.json` |
| `rv_ext.py` | extension / confirmation chunk audit | `out/ext.json` |
| `rv_stage0.py`, `rv_compute.py`, `rv_ll.py`, `rv_registry.py` | Stage 0, compute axis, likelihood, registry rows | `out/*.json` |
| `rv_hand_items.py` | blinded hand-check items from raw texts (regenerable; `hand/items/` not committed) | `hand/key.json` |
| `hand/reader_prompt.md` | the readers' rubric, written before reading any executor hand-check file | — |
| `hand/reader_labels/*.json` | the 14 blinded readers' JSON, verbatim | — |
| `hand/confirm.json` | my uniform class per item (P / I / C / X / G) and labels under strict / middle / lenient | — |
| `rv_hand_quotes.py`, `rv_hand_scan.py`, `rv_hand_ctx.py` | quote check; ingredient scan; context viewer | `out/hand_scan.txt` |
| `rv_hand.py` | per-cell labels, confirmations and verdicts under reader / strict / middle / lenient | `out/hand.{json,txt}` |
| `rv_expect.py`, `rv_phase1_checks.py`, `rv_secrets.py` | expectations vs recount; ad-hoc claim checks; secret scan (+ positive control) | `out/*.txt` |
