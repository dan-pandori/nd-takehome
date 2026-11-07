# Reviewer kit: olmo-iffu (2026-11-07)

Reviewer code, independent of `olmo_iffu/` and `olmo_ifomega/` (no executor module is imported). It reads the run's
raw sample files read-only from the phase-1 workspace `~/review/olmo-iffu` (hard links: never write there). Scratch is
`~/review/oiffu_rv/` (not committed): my upstream fetches, tokenizer / config files, nltk data, hand-check item texts,
the reader batch lists and the readers' raw output.

**Python:** `~/review/oiffu_venv` (uv, Python 3.12) with the pod's grader versions: nltk 3.9.2, langdetect 1.0.9,
emoji 2.15.0, syllapy 0.8.0, immutabledict 4.2.2, absl-py 2.3.1, sympy 1.13.3, antlr4-python3-runtime 4.11.0,
tokenizers 0.22.2, numpy. Stdlib-only scripts run with plain `python3`.

**Upstream (my fetch, `gh api …/contents/<path>?ref=<sha>`):** IFBench `cd189a9c` (incl. `ifbench/data/IFBench_test.jsonl`),
google-research `instruction_following_eval` `e6890f85` (incl. `data/input_data.jsonl`), OLMES `5a51f502` (omega task,
`utils.extract_answer`, configs, `exact_match`), open-instruct `7e780f2fea` (`ground_truth_utils.py`, `math_utils.py`,
`dataset_transformation.py`). Every grader file is byte-identical to the run's `olmo_ifomega/vendor/` copy (IFEval has
no upstream `__init__.py`; the vendored one is empty). Tokenizer / config: `hf download` of each model's
`tokenizer.json`, `tokenizer_config.json`, `config.json` (no weights).

| script | what it does | output |
|---|---|---|
| `rvi_core.py` | streaming loaders, id decoding, the pre-registered answer split | — |
| `rvi_graders.py` | my driver around the upstream checkers: IF strict / loose, OMEGA `omega` (OLMES extraction + exact_match_flex, functions taken by `ast`), `rl` (MathVerifier body by `ast`, worker thread) and `rl_main` | unit checks inline |
| `rvi_labels.py` | my own answers for the three geometry prompts (chord rule and float geometry) | `out/labels.{json,txt}` |
| `rvi_regrade.py` | re-grades all 12,816 stored texts; text == decode(ids); test 1 also at the 32,768-token truncation | `out/regrade/*.jsonl.gz` |
| `rvi_provenance.py` | subsets vs seeds (both list orders), sets sampled, problems vs upstream, hint wording, template sha, prompt tokens, budgets, seeds / TP / revisions | `out/provenance.{txt,json}` |
| `rvi_stats.py` | per-test automatic statistics (cut shares, lengths, strict / loose, answer words, stop-rule audit) | `out/stats.{txt,json}` |
| `rvi_before.py` | olmo-ifomega's raw IF samples (bucket, streamed) re-graded for the 49 reach prompts: dpo / s2300 / s0750 draws and strict successes | `out/before.{txt,json}` |
| `rvi_hand_items.py` | blinded items from raw texts (random ids, shuffled across arms and models), rounds 1–6 (5 and 6 in phase 2: second reads the B pass missed after adjudication); `T3_prior` = olmo-ifomega's strict success on a test-3 prompt | `hand/key_r*.json`, `hand/batches_r*.json` |
| `rvi_hand.py` | reader labels + my adjudications → per (arm, prompt) reading walk, statuses, next needs | `out/hand.{json,txt}`, `hand/need_r*.json` |
| `rvi_hand_b.py` | second-reader (B) set: every deciding IF item | `hand/batches_b.json` |
| `rvi_sensitivity.py` | outcomes under A-only, B, final labels; every A/B disagreement and my decision | `out/sensitivity.{txt,json}` |
| `rvi_outcomes.py` | per-prompt outcomes by the pre-registered rules, Clopper–Pearson bounds, status table, expectations | `out/outcomes.{json,md}`, `out/expect.md` |
| `rvi_compute.py` | per-job samples / tokens / GPU-s, pod hours and dollars, registry rows vs mine | `out/compute.{txt,json}` |
| `rvi_secrets.py` | secret-pattern scan of every file in the run's bucket folder (contents) | `out/secrets.txt` |
| `rvi_compare_hand.py` (phase 2) | the executor's `handcheck.csv` joined to my items by draw key: coverage, agreement, every disagreement with both evidences, per (arm, prompt) walk differences | `out/hand_compare.{txt,json}` |
| `rvi_lengths.py` (phase 2) | answer words without the hint (olmo-ifomega fixed phase, streamed) vs with it, median over the 48 hinted prompts | `out/lengths.{txt,json}` |
| `rvi_phase2_checks.py` | every inline check re-run: hard constraints, MANIFEST / bucket, timing, `results.csv` vs my re-grade, `s2300` hinted vs unhinted strict rates, CP intervals, length quantile methods, test-3 per-constraint passes, predecessor re-grade counts | `out/phase2_checks.txt` (also `out/results_compare.txt`) |

**Hand-check files.** `hand/reader_prompt_{if,omega}.md`: the readers' instructions (the pre-registered rubric with
rules 1–5, an ALL-CAPS flag for rule 6, and the OMEGA crux question; the reference pair sets are not given).
`hand/reader_labels/*.json`: the readers' JSON verbatim (`r<k>_*` first readers, `b_*` / `*_b` second readers,
`c_*` third reader; rounds 4–6 have a `_b` second reader). `hand/confirm.json`: my adjudication of every A/B disagreement, with the rule (written before
deciding) and a note per item. Item texts are regenerable with `rvi_hand_items.py <round>` and are not committed.

Order to reproduce: `rvi_labels` → `rvi_regrade` → `rvi_provenance` → `rvi_stats` → `rvi_before` → `rvi_compute` →
`rvi_hand_items 1` … (readers) … `rvi_hand` → `rvi_hand_b` → `rvi_sensitivity` → `rvi_outcomes` → `rvi_secrets`.
