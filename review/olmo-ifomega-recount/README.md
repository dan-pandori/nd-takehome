# Reviewer kit: olmo-ifomega (2026-11-06)

Reviewer code, independent of `olmo_ifomega/`. It reads the run's raw sample files read-only from the phase-1 workspace
`~/review/olmo-ifomega` (hard links: never write there). Scratch goes to `~/review/oif_rv/` (not committed): pinned
datasets, contamination scans, `draws.json`, hand-check items.

**Python:** `~/review/oif_venv`, the pod's grader versions:
- nltk 3.9.2, langdetect 1.0.9, emoji 2.15.0, syllapy 0.8.0, immutabledict 4.2.2, absl-py 2.3.1;
- sympy 1.13.3, antlr4 4.11.0, numpy 2.1.2, tokenizers 0.22.2;
- pyarrow, huggingface_hub.

Recreate with `uv venv ~/review/oif_venv --python 3.12` and `uv pip install` of those versions. Plain `python3` is
enough for the stdlib-only scripts.

`upstream/` holds my fetches at the pinned commits:
- IFBench `cd189a9c` (`ifbench/`, `evaluation_lib.py`, `run_eval.py`, `IFBench_test.jsonl`);
- google-research `instruction_following_eval` `e6890f85`;
- OLMES `5a51f502` (OMEGA task, configs, `extract_answer`, ExactMatch, hf_evaluate `exact_match`);
- open-instruct `7e780f2fea` (`ground_truth_utils.py`, `math_utils.py`, `dataset_transformation.py`).

| script | what it does | output |
|---|---|---|
| `rv_core.py` | loaders (streaming multi-member gzip with damage report), the pre-registered answer split | — |
| `rv_graders.py` | the upstream graders run as-is: IF strict / loose (IFBench, IFEval), OMEGA `omega` (OLMES functions taken by `ast`), `rl` (MathVerifier via `async_call`), my own last-`\boxed` diagnostic | unit checks |
| `rv_regrade.py` | re-grades all 46,434 stored texts (+ ids length, EOS, `</think>`) | `out/regrade/*.jsonl` (local; committed as `out/regrade_all.jsonl.gz`), `out/regrade_damage.json` |
| `rv_gradecmp.py` | my grades vs the executor's `graded/` rows, row by row | `out/gradecmp.{txt,json}` |
| `rv_decode.py` | text == decode(ids), lengths, finish vs cap, EOS | `out/decode_check.txt` |
| `rv_provenance.py` | prompts vs pinned datasets; seeded IFEval subset; OMEGA family / problem draws and pool filters re-derived | `out/provenance.txt` |
| `rv_cells.py`, `rv_stats.py` | cell table in draw order; pass@k + bootstrap; entries / exits; candidates and fates per grade; automatic verdicts; lengths | `out/cells.csv`, `out/stats.{json,txt}` |
| `rv_ext.py` | extension / confirmation audit against the stopping rule and the 256 cap | `out/ext.{txt,json}` |
| `rv_labels.py` | independent answers for every OMEGA candidate (geometry, enumeration, root search, construction) | `out/labels.{txt,json}`, `out/label055.txt` |
| `rv_contam.py`, `rv_contam_report.py` | own 8-gram raw / content containment vs RL prompts, DPO prompts, SFT user+system turns; vs `exclusions.csv` | `out/contam_*.{txt,csv}` |
| `rv_constraints.py` | per-constraint rates on reach / reverse prompts; RL IF ids from the RL parquet | `out/constraints.{txt,json}`, `out/rl_if_ids.json` |
| `rv_compute.py` | compute axis (pre-registered inputs, own lengths); per-job tokens / samples / meta seconds | `out/compute.{txt,json}`, `out/registry_check.txt` |
| `rv_expect.py` | pre-registered binding expectations vs recount | `out/expect.md` |
| `rv_hand_items.py` | blinded hand-check items from raw texts (round 1 gate; later rounds from `hand/need_r*.json`); controls | `hand/key_r*.json`, `hand/batches_r*.json` |
| `rv_hand.py` | labels + overrides → hand status per candidate (unsure strict / lenient; OMEGA union / doubly); next-round needs | `out/hand{,_doubly}.{json,txt}`, `hand/need_r*.json` |
| `rv_hand_tables.py`, `rv_tables.py` | markdown tables for the review, generated from the json | `out/hand_tables.md`, `out/tables.md` |

**Hand-check files.**
- `hand/reader_prompt_{if,omega}.md`: the rubrics.
- `hand/reader_labels/*.json`: the readers' JSON, verbatim.
- `hand/confirm.json`: my overrides, each with a note.
- `hand/spot_check_r1.json`: my blind reads against the readers'.

The item texts are regenerable with `rv_hand_items.py` and are not committed.
