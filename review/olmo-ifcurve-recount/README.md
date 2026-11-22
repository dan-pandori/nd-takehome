# Reviewer kit: olmo-ifcurve (2026-11-22)

Reviewer code, independent of `olmo_ifcurve/`, `olmo_ifomega/`, `olmo_iffu/`, `olmo_ifladder/` and `olmo_transplant/`
(no executor module is imported). Adapted from my olmo-ifladder kit (`review/olmo-ifladder-recount/`). It reads the
run's raw files read-only from the phase-1 workspace `~/review/olmo-ifcurve` (hard links: never write there).
Scratch is `~/review/oifc_rv/` (not committed):
- links to my earlier upstream fetch, tokenizer files and NLTK data;
- bucket copies of the reused source samples and their metas / logs (`src/`): olmo-ifomega `F_{dpo,s0100,s0750,s2300}_ifb`
  and olmo-iffu `T4_s0750`, `T4b_s0750`;
- olmo-ifomega's original `problems.jsonl` / `pids_ifbench.txt` / `exclusions.csv` (`ifomega/`);
- my full copy of the run's bucket folder (`bucket_copy/`);
- blinded item texts (`items/`), reader task files (`tasks/`) and the readers' raw JSON (`labels/`, copied verbatim
  into `hand/reader_labels/`).

**Python:** `~/review/oiffu_venv` (uv, Python 3.12; nltk, langdetect, emoji, syllapy, immutabledict, absl-py,
tokenizers, numpy) for the grader and tokenizer scripts; `~/.local/share/uv/tools/huggingface-hub/bin/python` for
`rvc_hub.py`; plain `python3` (numpy) for the rest. **Upstream checkers:** IFBench `cd189a9c` and google-research
`instruction_following_eval` `e6890f85` (my `gh api` fetch, made for the olmo-iffu review), byte-identical to
`olmo_ifomega/vendor/`. **Template:** open-instruct `7e780f2fea` `olmo_thinker`. **Tokenizer:**
`allenai/Olmo-3-32B-Think-DPO` @ `97604023` `tokenizer.json`.

| script | what it does | output |
|---|---|---|
| `rvc_core.py` | loaders (new jobs from the workspace, reused jobs from `src/`), my byte-level piece table and `</think>` finder, the answer split, hashes, upstream records | — |
| `rvc_graders.py` | my driver around the upstream IFBench / IFEval strict and loose checkers (original prompt + kwargs) | — |
| `rvc_regrade.py` | re-grades every row of the 31 jobs; text == decode(ids); thinking / answer tokens and words | `out/regrade/*.jsonl.gz` |
| `rvc_gradecmp.py` | my per-row grades and lengths vs the run's `rows/*.csv` | `out/gradecmp.txt` |
| `rvc_hub.py` | Hub API: commits, shards, LFS sha256, blobs of the 11 revisions; `main` = `step_2300`; history of `main` | `out/hub.{txt,json}`, `out/hub_genconfig.txt` |
| `rvc_provenance.py` | vendored = upstream; problems file vs its 2026-11-04 bucket copy and vs upstream; prompt sets and classes; every meta's settings, seed, revision, `JOB_START` sha; every prompt-token sha vs my template + tokenisation; plan specs vs rows | `out/provenance.{txt,json}`, `out/specinfo.json` |
| `rvc_cells.py` | my cells from the pre-registration's reuse table and amendments 1–5 (arm A, arm-B base 32, extension 128); duplicate-ids test | `out/cells.{txt,json}` |
| `rvc_boundary.py` | five full request junctions decoded by hand; response opener, EOS and stray special ids on every row; last-`</think>` thinking lengths | `out/boundary.txt`, `out/think_last.json` |
| `rvc_armA.py` | arm A pass@1 / 4 / 8 with prompt-bootstrap intervals, per family, adjacent differences, reading 5 (shape); arm D medians; brevity B | `out/armA.{txt,json}` |
| `rvc_answers.py` | caches the answers of every strict success the hand gate can touch; strict lists in draw order; my implementation of the pre-registered arm-C sample rule | `out/answers.json.gz`, `out/strict_lists.json` |
| `rvc_hand.py` | mechanical rule-1 screen (+ unit tests), label merge (majority of three, my confirmations), my walk of the pre-registered arm-B rules (a)(b)(c)(e) + (f) s2300 until 2 genuine, the arm-C sub-sample (20 per checkpoint), next first / second / third reads, status | `hand/need_*.json`, `out/hand.{txt,json}` |
| `rvc_hand_items.py` | blinded items (random ids, shuffled), batches, reader task files | `~/review/oifc_rv/items/`, `hand/key_*.json`, `hand/batches_*.json` |
| `rvc_readings.py [variant]` | readings 1–4, expectations 4–8, extension placement, never-reached bounds, estimated genuine pass@1; variants `rule6strict`, `r7literal`, `adjall`, `firstread`, `noADJ4`, `noR5` | `out/readings[_v].{txt,json}`, `out/emergence[_v].csv` |
| `rvc_adjudicate.py` | adjudicator tasks for every `checker_agrees = false` read and every split (rules 1–12, `hand/adjudicator_prompt.md`); `show` joins proposals to reads | `~/review/oifc_rv/tasks/ADJ*`, `hand/adj_ADJ*.json`, `out/adj_*.txt` |
| `rvc_adjudicate_prompt.py` | prompt-level pass under rules 10 / 11 / 12 over every read group of ifbench_206 / 207 / 268 | `ADJ4_*` tasks |
| `rvc_confirm.py ROUND [--reject …]` | writes my confirmations from the proposals I accept (`hand/confirm.json`; rejected ones in `hand/adj_rejected.json`) | `hand/confirm.json` |
| `rvc_rule5.py` | mechanical rule-5 pass on fixed-output prompts (repeat_span / repeat_simple) | `hand/confirm.json` (round R5) |
| `rvc_audit.py` | same-shape audit with the checkers' own sentence splitter / bullet lines | `out/audit.{txt,json}` |
| `rvc_hand_report.py` | reads by type, agreement, confirmations, sources | `out/hand_report.{txt,json}` |
| `rvc_compare.py` | agreement of my labels with the executor's (phase-1 requirement; run after my labels were final) | `out/compare.{txt,json}` |
| `rvc_misc_facts.py` | RL-data overlap (inherited), arm-C sample reproduction, `F_s0100_ifb` on the reach prompts, pass@8 ceiling | `out/misc_facts.txt` |
| `rvc_phase2_checks.py`, `rvc_phase2_exec.py` (phase 2) | executor hand-file counts, per-prompt F values vs mine, my walk and readings on the executor's labels (per-cell vs cumulative F2), registry sums, pods | `out/phase2_checks.txt`, `out/phase2_exec.{txt,json}` |
| `rvc_agree_variants.py`, `rvc_phase2_verify.py` (phase 2) | agreement under my label variants (final / first pass / adjall); numbers quoted in the rewritten §Compare | `out/agree_variants.txt`, `out/phase2_verify.txt` |
| `rvc_compute.py`, `rvc_compute_ckpt.py` | GPU-seconds per job from `JOB_START` / `JOB_DONE`, tokens, draws, per arm; podhours dollars; tokens per draw by checkpoint | `out/compute.{txt,json}`, `out/compute_ckpt.txt` |
| `rvc_hygiene.py`, `rvc_hygiene_hit.py` | bucket listing vs my copy vs workspace vs MANIFEST; secret-pattern scan of every object's contents; hit locations (masked) | `out/hygiene.txt`, `out/hygiene_hit.txt` |
| `rvc_facts.py` | commit, budget, pod and job times cited in the review | `out/facts.txt` |

**Hand-check files.** `hand/reader_prompt.md` is the readers' instructions: the run's pre-registered reader prompt
(`olmo_ifcurve/handcheck_prompt_if.md`), byte-identical. No rules 1–12 are given to readers. The task files add the
item paths, the output path and a one-line reply format. `hand/reader_labels/*.json` hold the readers' JSON verbatim.
`hand/key_*.json` maps item ids to draw keys and was kept from readers. `hand/confirm.json` holds my adjudications,
each with its reason and rule.

**Not committed (regenerable in seconds):** `out/answers.json.gz` (`rvc_answers.py`), `out/cells.json` (`rvc_cells.py`).

Order to reproduce: `rvc_regrade` (all jobs, `xargs -P 3`) → `rvc_gradecmp` → `rvc_hub` → `rvc_provenance` → `rvc_cells`
→ `rvc_boundary` → `rvc_armA` → `rvc_compute` → `rvc_compute_ckpt` → `rvc_hygiene` (after `hf buckets sync`) →
`rvc_hygiene_hit` → `rvc_facts` → `rvc_answers` → `rvc_hand.py need A1` → `rvc_hand_items.py A1` + `tasks` → readers →
(need / needB / needC rounds, `--x2` lookahead) until nothing is needed → `rvc_adjudicate tasks` → adjudicators →
`rvc_confirm` → `rvc_rule5` → `rvc_adjudicate_prompt` → `rvc_confirm ADJ4` → `rvc_hand.py status` → `rvc_audit` →
`rvc_hand_report` → `rvc_readings` (and variants) → `rvc_compare`.

**Adversarial check.** `out/adversarial_check_1.md` (33 findings on the first phase-2 draft) and `out/adversarial_check_2.md` (second pass); each finding is addressed in the review's §Compare / Corrections / §Verdict.
