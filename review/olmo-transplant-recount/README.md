# Reviewer kit: olmo-transplant (2026-11-08)

Reviewer code, independent of `olmo_transplant/`, `olmo_ifomega/` and `olmo_iffu/` (no executor module is imported).
It reads the run's raw files read-only from the phase-1 workspace `~/review/olmo-transplant` (hard links: never write
there). Scratch is `~/review/otr_rv/` (not committed): my bucket copies of the four `olmo-ifomega` source sample files,
my upstream IFBench fetch, my tokenizer downloads, NLTK data, blinded item texts, batch lists and the readers' raw JSON
(copied into `hand/reader_labels/`).

**Python:** `~/review/oiffu_venv` (uv, Python 3.12; nltk 3.9.2, langdetect 1.0.9, emoji, syllapy, immutabledict,
absl-py, tokenizers 0.22.2, numpy). **Upstream:** IFBench `cd189a9c2889526d8af901d2103fd3e1ffcea6df`
(`evaluation_lib.py`, `ifbench/*.py`, `ifbench/data/IFBench_test.jsonl`), fetched with `gh api …/contents/<path>?ref=`;
byte-identical to `olmo_ifomega/vendor/`. **Tokenizer / config:** `hf download` of `allenai/Olmo-3-32B-Think-DPO`
@ `97604023` and `allenai/Olmo-3.1-32B-Think` @ `97ade57a` (`tokenizer.json` identical). **Source samples:**
`hf buckets cp hf://buckets/dan-pandori/nd-rl/olmo-ifomega/artifacts/olmo_ifomega/samples/{F_s2300_ifb,C1_s2300_ifb,
C2_s2300_ifb,F_dpo_ifb}.jsonl.gz`.

| script | what it does | output |
|---|---|---|
| `rvt_core.py` | streaming loaders, my byte-level piece table and `</think>` finder, the answer split, hashes | — |
| `rvt_graders.py` | my driver around the upstream IFBench strict / loose checker (original upstream prompt + kwargs) | — |
| `rvt_regrade.py` | re-grades every run row (`run`) and every source row (`src`); text == decode(ids) | `out/regrade/*.jsonl.gz` |
| `rvt_provenance.py` | problems vs upstream; prompt sets; traces vs stored ids; my pre-draft cut; requests rebuilt; prompt ids + `input_sha256` on every row; F prefixes; boundary sample | `out/provenance.{txt,json}`, `out/traces_mine.csv`, `out/boundary_sample.txt` |
| `rvt_sets.py` | re-grade vs executor grades; trace strictness; calibration criteria and pool | `out/sets.{txt,json}` |
| `rvt_labels.py` | label sources for every strict success (read / identity-inherited / unread), my labels' precedence | `out/labels_summary.txt` |
| `rvt_protocol.py` | the executor's hand-gate protocol from `handcheck*.csv` (second / third readers, caps) | `out/protocol.txt` |
| `rvt_rates.py <mode>` | per-prompt rates, prompt bootstrap, paired contrasts, R1, B curves and F(N), secondary curves, N / c bins, draft split, copies, cut shares, fresh F(N), families, readings. Modes: `strict`, `exec` (executor's labels), `exec_r6`, `mine` (my blinded labels), `mine_r6`, `exec_vac` / `mine_vac` (+ rule 1 applied mechanically to sub-bullet answers with no `*`), `mine_sb` (natural sub-bullet reading), `exec_held` / `mine_held` (answers that re-open thinking count as failures, post hoc) | `out/rates_<mode>.{txt,json}`, `out/per_prompt_<mode>.csv` |
| `rvt_tables.py <modes>` | the review's tables, generated from `out/rates_<mode>.json` | `out/tables.md` |
| `rvt_sharetest.py` | the share rule's predicted genuine count vs my labels on unread successes I read; agreement on samples both labelled | `out/sharetest.txt` |
| `rvt_vacuous.py` | sub-bullet answers with no `*` (rule 1, vacuous) by cell and label source | `out/vacuous.txt` |
| `rvt_mech.py` | answers that contain a second `</think>` (the writer kept thinking after the forced close): share, extra length, strict curves with them counted as failures | `out/mech.{txt,json}` |
| `rvt_copy.py` | word 3-gram Jaccard of each answer with its trace's own final answer (exact / near / partial / own) | `out/copy.{txt,json}` |
| `rvt_lengths.py` | answer lengths by writer and cell | `out/lengths.txt` |
| `rvt_expect.py <mode>` | the pre-registered expected-results table vs my values | `out/expect_<mode>.md` |
| `rvt_compute.py` | per-job GPU-seconds from every JOB_START / JOB_DONE, tokens, checker calls, pod hours and dollars | `out/compute.{txt,json}` |
| `rvt_hygiene.py` | MANIFEST entries vs bucket objects (sha256) vs local; secret-pattern scan of every bucket object's contents | `out/hygiene.txt` |
| `rvt_facts.py` | facts cited outside the sample files: git hashes and commit times, pod / job times, template field per job meta, the R_dpo resume line | `out/facts.txt` |
| `rvt_hygiene_hit.py` | locates the one pattern hit (prints its JSON field, never the match) | `out/hygiene_hit.txt` |
| `rvt_protocol.py` | the executor's hand-gate protocol from `handcheck*.csv` | `out/protocol.txt` |
| `rvt_phase2_checks.py` (phase 2) | the executor's mechanism counts, prompts with T1 = 0, its draft-split and cut-share definitions, fresh-forcing natural baseline and ratios, F(P) under its post-hoc count, `results.csv` vs my per-prompt rates | `out/phase2_checks.txt` |
| `rvt_hand_items.py A` | my blinded items (selection D1–D4 in its docstring), random ids, shuffled | `hand/key_A.json`, `hand/batches_A.json` |
| `rvt_reader_task.py` | one reader's task text | — |
| `rvt_hand.py need_B / need_C / final` | merges A / B / C reader labels, second / third reader sets, agreement with the executor | `out/my_labels{,_r6}.json`, `out/hand.{txt,json}` |

**Hand-check files.** `hand/reader_prompt.md`: the readers' instructions (the pre-registered rubric, rules 1–6, rule 6
as a separate all-caps flag). `hand/reader_labels/*.json`: the readers' JSON verbatim (`A_*` first readers, `B_*`
second, `C_*` third). `hand/key_A.json` maps items to sample keys (kept from readers). `hand/confirm_rules.md`: my
adjudication rules, written before any third read; `hand/confirm.json`: my overrides (none). Item texts are
regenerable with `rvt_hand_items.py A` and are not committed.

Order to reproduce: `rvt_regrade run` → `rvt_regrade src` → `rvt_provenance` → `rvt_sets` → `rvt_labels` →
`rvt_protocol` → `rvt_rates strict|exec|exec_r6` → `rvt_mech` → `rvt_copy` → `rvt_lengths` → `rvt_compute` →
`rvt_hygiene` → `rvt_hand_items A` → readers → `rvt_hand need_B` → readers → `rvt_hand need_C` → readers →
`rvt_hand final` → `rvt_rates mine|mine_r6|exec_vac|mine_vac|mine_sb` → `rvt_vacuous` → `rvt_sharetest` →
`rvt_tables strict exec mine mine_vac` → `rvt_expect mine|exec|mine_vac`.

**Adversarial check.** `out/adversarial_check.md`: an independent read-only subagent's check of the review draft
(25 findings: 5 wrong, 5 inconsistent, 6 overclaims, 1 untraceable, 8 minor; none in the run's numbers that changed a
verdict). Each is addressed in the review: §Compare / §Verdict were rewritten, and the errors in the committed §Recount
are listed under "Corrections to §Recount".
