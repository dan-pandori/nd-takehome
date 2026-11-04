# Reviewer kit: olmo-think32b (2026-11-04)

Reviewer code, independent of `olmo32/`. Run from this directory, on the VPS, after the run's artefacts are present
(`artifacts/olmo32/samples/*.jsonl.gz` come from the bucket). Python: system `python3` for the stdlib-only scripts;
`~/review/ot32_venv` (sympy 1.13.3, antlr4 4.11.0, tokenizers, pyarrow, numpy) for the verifier, tokenizer and parquet
ones (recreate: `uv venv ~/review/ot32_venv --python 3.12 && uv pip install --python ~/review/ot32_venv/bin/python sympy==1.13.3 antlr4-python3-runtime==4.11.0 mpmath==1.3.0 tokenizers pyarrow numpy requests`, the pod's sympy / antlr4 versions); `~/.local/share/uv/tools/huggingface-hub/bin/python` for Hub metadata. `out/tokcfg/tokenizer.json` (7 MB, not committed) is `allenai/Olmo-3-32B-Think-DPO` `main`'s; `rv_contam.py` takes the directory of the four Dolci-Think-RL-32B parquet files (rev d581ecde, 759 MB, not kept).

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
| `hand/confirm.json` | my class per item (P / T / S / C / X / G; set after reading my readers' labels, T / S in phase 2), labels under strict / exec_rule / lenient, `read_by_reviewer` | — |
| `rv_hand_quotes.py`, `rv_hand_scan.py`, `rv_hand_ctx.py` | quote check; ingredient scan; context viewer | `out/hand_scan.txt` |
| `rv_hand.py` | per-cell labels, confirmations and verdicts under reader / strict / exec_rule / lenient | `out/hand.{json,txt}` |
| `rv_expect.py`, `rv_phase1_checks.py`, `rv_secrets.py` | expectations vs recount; ad-hoc claim checks; secret scan (+ positive control) | `out/*.txt` |
| `rv_hand_compare.py`, `rv_phase2_checks.py` | phase 2: executor's hand-check table joined to my items (reader / uniform / strict); write-up numbers recomputed | `out/hand_compare.txt`, `out/phase2_checks.txt` |
| `rv_cells_compare.py` | phase 2: my per-cell table vs the executor's `olmo32/results.csv` | `out/cells_compare.txt` |
| `rv_secrets_bucket.py` | phase 2: secret scan over all 272 bucket files (local copies where sizes match, else fetched) | `out/secrets_bucket.txt` |
| (inline, saved) | phase 2: provenance facts (pod ledger, git blobs and times, balance, word counts); unit test; LL checks; all 105 registry rows; pass@k, likelihood and exec-rule label comparisons | `out/provenance.txt`, `out/upstream_unit.txt`, `out/ll_checks.txt`, `out/registry_all.txt`, `out/passk_compare.txt`, `out/ll_compare.txt`, `out/hand_compare_exec_rule.txt` |
