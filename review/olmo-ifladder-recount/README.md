# Reviewer kit: olmo-ifladder (2026-11-09)

Reviewer code, independent of `olmo_ifladder/`, `olmo_ifomega/`, `olmo_iffu/` and `olmo_transplant/` (no executor
module is imported; `interventions.py` is read as data with `ast`, never executed). It reads the run's raw files
read-only from the phase-1 workspace `~/review/olmo-ifladder` (hard links: never write there). Scratch is
`~/review/oifl_rv/` (not committed): links to my earlier upstream fetch / tokenizer files / NLTK data, bucket copies
of the olmo-ifomega source samples (`src/`, sha256 = MANIFEST), my full copy of the run's bucket folder
(`bucket_copy/`), blinded item texts (`items/`), reader task files (`batches/`) and the readers' raw JSON (`labels/`,
copied into `hand/reader_labels/`).

**Python:** `~/review/oiffu_venv` (uv, Python 3.12; nltk 3.9.2, langdetect 1.0.9, emoji, syllapy, immutabledict,
absl-py, tokenizers 0.22.2, numpy) for the grader scripts; plain `python3` for the rest. **Upstream checkers:**
IFBench `cd189a9c` and google-research `instruction_following_eval` `e6890f85` (my `gh api` fetch, made for the
olmo-iffu review), byte-identical to `olmo_ifomega/vendor/` (`out/provenance.txt` [1]). **Template:** open-instruct
`7e780f2fea` `olmo_thinker`. **Tokenizer:** `allenai/Olmo-3-32B-Think-DPO` @ `97604023` `tokenizer.json`.

| script | what it does | output |
|---|---|---|
| `rvl_core.py` | loaders, my byte-level piece table and `</think>` finder, the answer split, hashes, upstream records | — |
| `rvl_graders.py` | my driver around the upstream IFBench / IFEval strict and loose checkers (original prompt + kwargs) | — |
| `rvl_regrade.py` | re-grades every stored sample of all 13 jobs; text == decode(ids) | `out/regrade/*.jsonl.gz` |
| `rvl_sets.py` | my grades vs the executor's `graded/`; per (cell, prompt) strict counts and draw-order strict lists | `out/sets.{txt,json}`, `out/strict_lists.json` |
| `rvl_provenance.py` | vendored = upstream; prompt sets; rung texts rebuilt from the pre-registration; rung-4 turns vs stored exemplar answers; every job's prompt-token sha vs my own template + tokenisation; seeds, draws, decoding, template, adapters | `out/provenance.{txt,json}` |
| `rvl_exemplars.py` | exemplar answers strict on their source prompts; same-family fills; exemplar answers that already pass the target's checker | `out/exemplars.txt` |
| `rvl_hints.py` | every hint with its description; hint words / numbers found in a prompt's base request; hint commit vs first hinted job | `out/hints.txt` |
| `rvl_train.py` | training manifest vs bucket copies (ids, sha, finish, my strict grade, token cap); sets; LoRA metas (data, order, schedule, recipe); NLL guards | `out/train.{txt,json}` |
| `rvl_overlap.py` | base-request overlap (constraint text removed with the checkers' own descriptions + a fuzzy 4-gram mask): training / held-out / exemplar sources vs the 58 | `out/overlap.{txt,json}` |
| `rvl_copy.py` | rung-4 answers vs the target's exemplar answers; LoRA answers vs their arm's 16 training answers | `out/copy.txt` |
| `rvl_calib_lengths.py` | calibration strict rates per rung / LoRA vs `dpo`'s unhinted fixed-phase rate; thinking tokens and answer words (LoRAs vs `dpo` / `s2300` fixed phase) | `out/calib_lengths.{txt,json}` |
| `rvl_compute.py` | per-job GPU-seconds (JOB_START / JOB_DONE, failed starts included), tokens, LoRA training, podbudget, matched-axis ratios | `out/compute.{txt,json}` |
| `rvl_hygiene.py`, `rvl_hygiene_pat.py`, `rvl_hygiene_hit.py` | bucket listing vs my copy vs MANIFEST vs local; secret-pattern scan of every object's contents; hit locations (field / character class only); weights; `nd_verify` / `TEST_RUN_DONE` / training-code reads | `out/hygiene.txt`, `out/hygiene_hit.txt` |
| `rvl_hand_items.py <ROUND>` | blinded items for a round (random ids, shuffled across cells and models) | `hand/key_<R>.json`, `hand/batches_<R>.json` |
| `rvl_reader_task.py <ROUND> <k>` | one reader's task text (`hand/reader_prompt.md` + item paths + output path) | — |
| `rvl_hand.py need / needB / needC / status` | mechanical rule-1 screen; label merge (majority of three, my adjudications); the per-(prompt, cell) draw-order walk; next reads | `hand/need_<R>.json`, `out/hand.{txt,json}`, `out/my_labels.json`, `out/mech_labels.json` |
| `rvl_classify.py [mine\|strict]` | per-prompt classification by the pre-registered readings, families, test-3 and sanity flags | `out/classify_<mode>.{txt,json,csv}` |
| `rvl_outcomes.py` | gamed shares, Fisher sensitivity (own hypergeometric, scipy cross-check), sanity breaks, expectations 1–13 | `out/outcomes.{txt,json}`, `out/expect.md` |
| `rvl_sensitivity.py` | cell outcomes under final / first-read / pessimistic / strict-only labels; reader agreement by group | `out/sensitivity.{txt,json}` |
| `rvl_hand_report.py` | reads by round and cell, label groups, deciding items with second reads, splits, training trajectories, rule-6 reading of `ifbench_290` | `out/hand_report.txt` |
| `rvl_tables.py` | the per-prompt and by-family tables | `out/tables.md` |
| `rvl_facts.py` | commit / transcript / pod / job times and model revisions cited in the review | `out/facts.txt` |
| `rvl_compare.py` (phase 2) | `classify.csv` vs mine; the executor's `handcheck.csv` joined to my draw keys (agreement, every disagreement with both evidences); my walk re-run with the executor's labels | `out/compare.{txt,json}` |
| `rvl_phase2_checks.py` (phase 2) | executor hand-gate stats, held-out slice, `s2300`'s unhinted strict rate, mean thinking per draw, Fisher on the executor's teachable set, olmo-iffu rung-1 break flags, source of the one-way label disagreements | `out/phase2_checks.txt` |
| `rvl_p2_adjusted.py` (phase 2) | my labels with the one phase-2 adjudication (`hand/confirm_phase2.json`, R4 `ifbench_154`) applied in memory: readings, Fisher, expectations | `out/p2_adjusted.txt` |

**Hand-check files.** `hand/reader_prompt.md`: the readers' instructions (the pre-registered rubric, rules 1–6 with
rule 6 as a separate ALL-CAPS flag, and the pre-registered sentence about appended instructions).
`hand/reader_labels/*.json`: the readers' JSON verbatim. `hand/key_*.json` maps item ids to sample keys (kept from
readers). Phase 1 made no adjudications (no `hand/confirm.json`); `hand/confirm_phase2.json` holds the one phase-2
adjudication, applied only by `rvl_p2_adjusted.py`. Rounds: A1–A6 first reads (A4 inside M1), B1 / B2 / B5 second
reads (B3 inside M1), M1 = the last first, second and third reads in one batch, T1 = the 8 remaining rung-2
`ifbench_290` strict successes (rule-6 strict reading). Item texts are regenerable with `rvl_hand_items.py <ROUND>`.

Order to reproduce: `rvl_regrade` (all jobs) → `rvl_sets` → `rvl_provenance` → `rvl_exemplars` → `rvl_hints` →
`rvl_train` → `rvl_overlap` → `rvl_copy` → `rvl_calib_lengths` → `rvl_compute` → `rvl_hygiene` (after `hf buckets
sync` of the run folder) → `rvl_hygiene_hit` → `rvl_hand need A1 --src` → `rvl_hand_items A1` → readers → (`rvl_hand
need / needB / needC`, items, readers) until nothing is needed → `rvl_hand status` → `rvl_classify mine|strict` →
`rvl_outcomes` → `rvl_tables` → `rvl_sensitivity` → `rvl_hand_report` → `rvl_facts`; phase 2: `rvl_compare` →
`rvl_phase2_checks` → `rvl_p2_adjusted`.
