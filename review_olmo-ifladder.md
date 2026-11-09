# Review — olmo-ifladder (proposal 41)

Reviewer: agent:claude (role reviewer), a session independent of the executor. Run branch `dan_olmo-ifladder`,
reviewed at `fdb4c02b` (the executor's last commit, "done"). Kit: `review/olmo-ifladder-recount/` (README there; every
number below is in its `out/`). Phase 1 used the workspace `~/review/olmo-ifladder` (executor write-ups removed). It
did not open `log.md`, `QUESTIONS.md`, `STATUS.md`, `olmo_ifladder/{README.md, claim_check_*.md, classify.csv,
results.csv, summary.json, lengths.csv, handcheck.csv, handcheck_src.csv, handcheck_rule_addendum.md}`,
`artifacts/olmo_ifladder/{gate_status.csv, hand/, hand_src/}` (the executor's reader labels and confirmations) or the
bucket's `docs/`. **Disclosure:** before the recount I had seen headline numbers in the branch's commit messages
(`git log --oneline`: "lora_main elicits 40 of 48", "control LoRA elicits 0 of 48", "136 elicited at rung 2",
"rung 3 elicits 5", "rung 4 elicits 3", "rung 2 breaks s2300 on 8 of 31") and in my memory index (one line on this
run: 40/48 vs 0). My selection rules, reader instructions and adjudication rules were fixed in code before any of my
reader labels existed, and no executor label was used anywhere in phase 1.

**Models (every number below names one of these).**
- `dpo` = `allenai/Olmo-3-32B-Think-DPO` `main` @ `97604023`: 32 B, bf16, pretrained (Olmo 3 32B base → Think SFT
  → DPO).
- `s2300` = `allenai/Olmo-3.1-32B-Think` `main` @ `97ade57a`: `dpo` after 2,300 Think-RL steps.

  Both revisions are what the pod fetched (`logs/fetch_*.log`).
- `lora_main` = `dpo` + a rank-16 PEFT LoRA trained in this run on 16 hand-labelled-genuine `s2300` trajectories
  (thinking included) of 16 IFBench prompts outside the evaluation set. Adapter sha256 `9921a760…`.
- `lora_ctrl` = the same recipe on 16 `dpo` trajectories of the same 16 prompts. Adapter `4cf06004…`.

Format: natural-language chat, `olmo_thinker` template, vLLM 0.11.0, T 1.0, top-p 1.0, `max_tokens` 32,768, one H200.
The LoRAs ran through vLLM's LoRA path. Prompts: 48 "reach" prompts (42 IFBench `cd189a9c`, 6 IFEval `e6890f85`)
plus 10 IFBench calibration prompts. Checkers: the official strict / loose checkers (my fetch).

## §Recount (phase 1, blind)

### Hard constraints, judge and timing

| check | result |
|---|---|
| `nd_verify` unmodified | `nd_verify/__init__.py` and `verify.py` byte-identical to `origin/main` (`out/hygiene.txt` [4]) |
| `nd_verify` / Lean as a judge | not used and not applicable: no proofs (IFBench / IFEval answers); no `nd_verify` or `verify_text` reference in `olmo_ifladder/` or `pod/olmo_ifladder/` |
| `artifacts/TEST_RUN_DONE` | identical to `origin/main` |
| training code reading evaluation files | `lora.py` opens only `--manifest` (`train_manifest.jsonl`) and its own log. The 16 training and 8 held-out prompts are outside the 58 and are not `ifbench_281` (`out/train.txt` [2]) |
| weights in the bucket | none. The only `.safetensors` objects are the two adapters (537 MB each); no object > 1 GB |
| secrets | 1,283 bucket objects scanned (contents, gzip decompressed). 25 pattern hits, all benign (`out/hygiene_hit.txt`): 22 are hyphen-joined lowercase words in answers to the no-whitespace calibration prompt `ifbench_298` (`…ask-…`); 3 are chance `AKIA…` strings inside base64 token-id fields |
| bucket = MANIFEST = local | all 1,283 listed objects in my copy at their listed sizes. The 28 MANIFEST entries for the run match by sha256. 1,279 objects have a workspace file at the same path, all byte-identical; 4 do not (3 under `docs/` and `olmo_ifladder/plain_summary.md`: write-ups, not opened) |
| expectations before any pod | pre-registration and all 13 expected results committed `48840906` at 00:08:34 UTC; pod `ifl-a` ready 00:41:16 |
| hints before any hinted output | `interventions.py` written 00:01:09 (transcript), committed 00:08:34, never changed (sha256 `e3c28474…` = the pre-registered prefix). First hinted sample: job `S0r3` from 00:57:13 |
| exemplars before rung 4 | `exemplars.csv` / `problems_r4.jsonl` committed 02:06:01; `R4_dpo` started 14:27:42 |
| training manifest before training | committed 01:32:57; LoRA training 03:45–03:56. `lora.py`'s only later change (04:14) adds a `finish` command (NLL checks and merge from the saved adapter); the training code path is unchanged |

Stated writing times are wrong (minor). The pre-registration says "Written 2026-11-09 00:10–01:00 UTC". The
transcript's Write is at 00:07:49 and the commit at 00:08:34. `interventions.py` says "Written 2026-11-09
00:40-01:30 UTC"; it was written at 00:01:09. Both stated windows are later than the commit. The order of events is as
claimed: before any pod, and before any hinted sample.

### Provenance (`rvl_provenance.py` → `out/provenance.txt`)

- **Checkers:** the vendored IFBench / IFEval files are byte-identical to my fetch (10/10).
- **Prompt sets:** reach = olmo-iffu's 49 hinted IF prompts less `ifbench_281` (48: 42 IFBench, 6 IFEval).
  Calibration = the pre-registered 10. olmo-transplant's calibration file has 12; `ifbench_226` and `252` are reach
  prompts here.
- **Problems files:** every `prompt`, id list and kwargs equals the upstream record. Every user turn sent equals **my
  own rebuild** of the rung text from the pre-registration's wording: BREVITY / CHECK, the `HINTS` of the prompt's ids
  in list order, and DROP60 from the pre-registration's text. This holds for rungs 1 (calibration), 2, 3 and 4's final
  turn (0 mismatches over 58 + 58 + 58 + 8 rows).
- **Rung-4 turns:** each of the 58 targets has exactly two (user, assistant) turns.
  - Each user turn is the source prompt's upstream text.
  - Each assistant turn is the stored olmo-ifomega `s2300` answer, re-read from my bucket copies (sha256 = MANIFEST).
    116/116 match `exemplars.csv`, and all 116 are strict successes on their own source prompt.
  - Three slots are same-family fills, as the pre-registration allows: `ifbench_64` ← `ifbench_60`
    (`repeat:repeat_change`); `ifbench_280` ← `274` (`custom:csv_city`) and `277` (`custom:date_format_list`).
  - 13 sources are among the 58; none is its own target (`out/exemplars.txt`).
- **Prompt token hashes:** for all 13 jobs I rebuilt every pid's prompt token ids with my own template text and
  `tokenizers`, including rung 4's four prior turns. Each matches the job meta's `prompt_sha256_by_pid` and token count,
  and every row's `prompt_tokens`. Template = open-instruct `7e780f2fea` `olmo_thinker` (sha `eba6e269…`, all jobs).
- **Jobs:** seeds as pre-registered (9001; 9101; 9201 / 9202; 9301 / 9302; 9401 / 9402; 9501 / 9502; 9511 / 9512).
  Draws per pid as designed: 64 per rung cell, 16 sanity, 16 + 48 for LoRA calibration. No duplicate draw keys.
  Length cuts: 1 / 1 / 0 (`dpo` R2 / R3 / R4), 1 / 2 / 1 (`s2300` R2 / R3 / R4), 2 (`lora_main`), 4 (`lora_ctrl`).
  Both LoRA eval metas name the adapter files in the bucket (sha256 match).

### Re-grade (`rvl_regrade.py`, `rvl_sets.py` → `out/sets.txt`)

All 19,456 stored samples of the 13 jobs were re-graded with my driver: strict and loose, on the original prompt.
- My strict and loose grades agree with the executor's `graded/*.jsonl` on 19,456 / 19,456 rows.
- The stored text equals my decode of the stored ids on every row.
- 15 rows have no `</think>` (graded as failures); 82 contain a second `</think>` (`out/review_checks.txt`).

Strict successes on the 48 reach prompts:

| cell (model, rung) | prompts run | strict successes | prompts with ≥ 2 strict | loose: prompts with ≥ 2 |
|---|---|---|---|---|
| R2 (`dpo`) | 48 | 217 / 3,072 | 13 | 29 |
| R3 (`dpo`) | 31 | 30 / 1,984 | 6 | 16 |
| R4 (`dpo`) | 26 | 79 / 1,664 | 5 | 10 |
| `lora_main`, no hint | 48 | 1,052 / 3,072 (0.342) | 41 | 43 |
| `lora_ctrl`, no hint | 48 | 5 / 3,072 (0.002) | 0 | 11 |
| S2 / S3 / S4 (`s2300` sanity) | 48 / 31 / 26 | 523 / 341 / 323 | 44 / 30 / 26 | 45 / 31 / 26 |

R4's 79 strict successes contain only 17 distinct answers: `ifbench_280` gives 64/64, two strings of the multiples
of 7.

### The hints carry no answer content (the brief's first reviewer item; `rvl_hints.py`, `rvl_exemplars.py`, `rvl_copy.py`)

- I read all 36 hints against their constraint descriptions. Each is a method for the constraint type; none names
  content for any prompt.
  - The closest to content are `words:prime_lengths`, which lists the prime lengths 2–13, and `custom:multiples`,
    which says to test each number of the range for divisibility but does not list the multiples.
  - A mechanical screen of every hinted prompt finds only function words shared between a hint and the prompt's base
    request (`which`, `have`, `such`, `those`, `whole`, `rewrite`) and no shared numbers.
- In the executor's session, the only checker-source access before the hints were written was a regex extraction of
  the docstrings and `_description_pattern` strings (transcript 23:53:57). No `check_following` logic was printed.
- Rung 4 is a different matter: it shows two real answers to other prompts with the same constraint.
  - 80 of the 116 exemplar answers would already pass the target's own checker unchanged.
  - For the fixed-output `ifbench_64` (`repeat:repeat_simple`), the exemplar answer *is* the target's answer.
  - Rung 4 never ran on 64, because rung 3 elicits it first. No `dpo` rung-4 strict success copies an exemplar (0 of
    79 exact or near). `s2300` copied one in 3 of its 323 R4 strict successes.

### Training / evaluation overlap (the brief's second item; `rvl_overlap.py`, `rvl_train.py`)

My own method:
1. Cut each prompt's constraint text using the checkers' own `build_description` (exact or case-insensitive), then
   mask any 4-word run shared with the prompt's own descriptions.
2. Compare the remaining words: longest common run and token Jaccard.

Results:
- Training × the 58 (928 pairs): longest common run 5 words ("each sentence in your response", constraint residue),
  max Jaccard 0.18.
- Held-out × 58: 3 words.
- Exemplar source × target (116 pairs): 7 words ("write a descriptive fictional imaginative screenplay of", the generic
  WildChat opening the pre-registration names).

No training or held-out prompt shares its base request with an evaluation prompt. One thing is shared that is not a
base request: `lora_main`'s training prompt `ifbench_63` (`repeat:repeat_simple`) has the same fixed answer string
as evaluation prompt `ifbench_64`. All 4 of `lora_main`'s strict successes on 64 are that string verbatim; it is
`ifbench_63`'s training answer. 64 is prompt-elicitable at rung 3 in any case.

The manifest (`out/train.txt`):
- All 48 rows equal my bucket copies: ids, sha256(text), `n_tok`, `finish = stop`. Each is a strict success on its
  original prompt (my grade), and prompt + response ≤ 16,384 tokens.
- 16 training prompts, one per constraint id, covering 16 of the reach set's 27 distinct ids. Uncovered:
  `capital_word_frequency`, `english_capital`, `keywords_multiple`, `multiples`, `letter_frequency`, `sentence_words`,
  `alphabet`, `last_first`, `no_consecutive`, `odd_even_syllables`, `vowel`.
- Both LoRA metas train exactly the manifest's 16 trajectories of their writer.
- The recipe is as pre-registered: r 16, α 32, dropout 0.05, the 7 projections, lr 1e-4 with 4 warm-up steps then
  cosine to 10 % (max deviation from my schedule 0), 4 epochs = 64 steps, and the same per-epoch slot order in both
  arms.
- Training tokens differ: `lora_main` 332,936 vs `lora_ctrl` 235,880 = **1.41×**. Response tokens per epoch: 81,769
  `s2300` vs 57,505 `dpo`. Median answer words: 52 vs 164.
- Guards:
  - held-out `s2300`-trajectory NLL drops 15.1 % under `lora_main` (0.638 → 0.542), above the 2 % guard, so no
    retrain. `lora_ctrl` changes it by −0.7 %.
  - Held-out `dpo`-trajectory NLL *rises* under both: +16.9 % (`lora_main`), +1.4 % (`lora_ctrl`).
  - Merge check: 1.12 % (`lora_main`) / 0.88 % (`lora_ctrl`), hence the LoRA path (deviation 2), applied to both arms.

### My blind repeat of the hand gate (the brief's third item; `rvl_hand*.py` → `out/hand.txt`, `out/hand_report.txt`, `out/sensitivity.txt`)

**Protocol (mine, fixed in code before any label).** For every reach (prompt, cell) in R2, R3, R4, `lora_main`,
`lora_ctrl` and the `s2300` sanity cells S2–S4, my walk takes the strict successes (my re-grade) in draw order.
- It reads until 2 genuine and at least min(n, 4) draws, or until none are left.
- Identical whitespace-collapsed answers to the same prompt text share a label.
- My implementation of the pre-registered mechanical rule-1 screen labels 70 vacuous successes gamed without a reader:
  one-sentence answers to per-sentence constraints, one-line stairs, sub-bullets with no `*` line. These include the
  four rung-4 `ifbench_188` answers, whose lines carry no sentence punctuation, so "each sentence N words longer"
  holds for a single "sentence". I checked those by eye.

The readers:
- Readers are fresh general-purpose subagents, blinded to model, cell and selection, ≤ 4 at a time.
- Items show the final user turn as sent (rung items include the appended text; the pre-registered sentence about
  appended instructions is in the reader prompt), the constraints and the answer.
- Rules 1–6 are given, with rule 6 (ALL-CAPS title case) as a separate flag (`hand/reader_prompt.md`).
- A second reader read every outcome-deciding item:
  - in main cells, the first two genuine of an elicited cell, and every gamed read of a not-elicited cell with exactly
    one genuine;
  - in sanity cells, only fragile outcomes;
  - all 32 training trajectories.
- First/second disagreements went to a third reader (majority of three). I made no overrides (`hand/confirm.json`
  absent).

**Reads.** 876 reads (685 first, 188 second, 3 third) over 685 label groups.
- First and second readers agree on 185 of 188 items. The 3 splits are thin-answer cases, all resolved genuine 2–1:
  `lora_main` `ifbench_226`, S2 `ifbench_269`, and the training trajectory `s2300`/`ifbench_250`.
- 124 of the 146 deciding label groups have ≥ 2 reads. The 22 without are gamed reads in the two broken sanity cells
  of `ifbench_4` (S3, S4), which decide no reading.
- **All 32 training trajectories are genuine** (16 `s2300`, 16 `dpo`).

**Robustness.** Cell outcomes are identical under final, first-read-only and pessimistic labels (genuine only if
every read says genuine). Strict counting without the gate differs on 10 cells, all vacuous: `ifbench_188` / `189`
one-sentence answers, the S3 `166` cell, and `ifbench_4`'s S3 / S4 cells.

### Per-prompt classification (the brief's fourth item; `rvl_classify.py` → `out/classify_mine.*`, table `out/tables.md`)

Rung 1 is olmo-iffu's tests 2 / 2c from my own olmo-iffu review labels (16 elicited; identical to
`olmo_iffu/status.csv`). Rungs 2–4 and the LoRAs come from my walk.

| reading | prompts | which |
|---|---|---|
| prompt-elicitable at rung 1 | 16 | e1314 e2247 e2447 e2563, 19 78 133 173 179 186 187 220 226 252 253 290 |
| … at rung 2 | 1 | 136 |
| … at rung 3 | 5 | 64 79 128 204 211 |
| … at rung 4 | 4 | 154 189 267 280 |
| **teachable from RL's trajectories** (no rung; `lora_main` yes, `lora_ctrl` no) | **15** | e2350, 0 1 4 169 170 203 206 207 209 217 248 264 269 271 |
| teachable by any light fine-tune | 0 | — |
| `lora_ctrl` only | 0 | — |
| **neither** | **7** | e3478, 3 67 166 188 268 284 |

- **Cells:** `lora_main` elicits **40 / 48**; `lora_ctrl` **0 / 48** (its 5 strict successes are on 5 different
  prompts). Rung 2 elicits 13 of 48 (1 of the 32 rung-1-unelicited), rung 3 5 of 31, rung 4 4 of 26. Prompt-elicitable
  at some rung: **26 / 48**.
- **"Neither" flags:**
  - olmo-iffu test-3 survivors (0 genuine in 1,024): `ifbench_3`, `166`.
  - Failed rungs that also break `s2300` (uninformative there): `188` at R1–R4, `3` at R1–R3, `166` at R1 and R3.
  - So `188`'s "neither" rests on no informative rung (every rung failure breaks `s2300` too); `3`'s rests on rung 4
    only.
  - Robustness: the other four are label-robust, with ≤ 1 strict success in every rung and LoRA cell. `188`'s rests on
    the mechanical rule-1 labels of its 4 rung-4 strict successes.
- **The six test-3 survivors not elicited at rung 1:** 3 and 166 neither; 136 at rung 2; 211 at rung 3; 248 and 269
  teachable from RL's trajectories.
- **The four 1,024-survivors that the hint elicits (78 133 252 253):** elicited at rung 2 (4 / 4) and by `lora_main`
  (4 / 4; strict 42 / 62 / 49 / 26 of 64). `lora_ctrl` 0 / 4 (strict 0 / 1 / 0 / 0).
- **ALL-CAPS title case (rule 6) on `ifbench_290`:** rung 1 rests on ALL-CAPS answers (my olmo-iffu labels). The first
  four rung-2 reads were ALL-CAPS too.
  - I read all 12 rung-2 strict successes: 12 genuine, 3 not ALL-CAPS (each double-read).
  - Under the strict reading, 290 is prompt-elicitable at **rung 2** rather than rung 1. `lora_main` elicits it under
    both readings.
- **By family (binding-id prefix):**

  | family | n | rung 1 | rung 2 | rung 3 | rung 4 | teachable (RL) | neither |
  |---|---|---|---|---|---|---|---|
  | words | 17 | 4 | 0 | 2 | 1 | 9 | 1 |
  | format | 7 | 3 | 1 | 2 | 0 | 0 | 1 |
  | count | 5 | 1 | 0 | 0 | 0 | 3 | 1 |
  | ratio | 5 | 1 | 0 | 0 | 1 | 2 | 1 |
  | sentence | 5 | 3 | 0 | 0 | 1 | 0 | 1 |
  | keywords | 3 | 1 | 0 | 0 | 0 | 1 | 1 |
  | change_case | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
  | repeat | 2 | 0 | 0 | 1 | 0 | 0 | 1 |
  | custom | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
- **Fisher sensitivity (pre-registered; one-sided, own hypergeometric sum, scipy cross-check).** Genuine counts beyond
  the reads are unknown, so I used strict × the cell's read genuine share.
  - 35 of the 40 `lora_main`-elicited prompts give p < 0.05 against `lora_ctrl`.
  - Of the 15 "teachable" prompts, **12** do. `ifbench_169` (2 vs 0: p 0.25), `ifbench_0` and `170` (4 vs 0: p 0.060)
    do not.
  - On the gated lower bounds alone (2 genuine vs 0), no prompt reaches p < 0.05: 2 of 64 vs 0 of 64 is p 0.25.
- **The `lora_main` effect does not need the constraint in training:** it elicits 19 of the 23 prompts whose binding id
  no training prompt carries, and 21 of the 25 whose id one does. Of the 15 "teachable", 10 have an uncovered binding
  id.

### Gamed shares, calibration, lengths, sanity (`out/outcomes.txt`, `out/calib_lengths.txt`)

- **Gamed share** (pre-registered estimator: first min(n, 4) strict successes of every reach cell, mechanical labels
  counted gamed):

  | cell | share |
  |---|---|
  | R2 `dpo` | 8/59 = 0.136 |
  | R3 `dpo` | 4/21 = 0.190 |
  | R4 `dpo` | 5/19 = 0.263 |
  | `lora_main` | 13/164 = 0.079 |
  | `lora_ctrl` | 1/5 |
  | S2 / S3 / S4 (`s2300`) | 0.229 / 0.303 / 0.212 |

  Rung 1 by the same estimator on my olmo-iffu labels: `dpo` 8/48 = 0.167 (9 ranks unread there); the
  pre-registration's value is 0.125.
- **Calibration** (strict; `dpo` unhinted = olmo-ifomega fixed phase, 16 per prompt, my re-grade: 0.906).
  - `dpo` means by rung: R1 0.777 (8 prompts), R2 0.850, R3 0.861, R4 0.847.
  - Only `ifbench_298` falls below half its unhinted rate (R1 0.05, R2 0.19, R3 0.25, R4 0.20).
  - LoRA checks (16 / prompt): `lora_main` 0.963, `lora_ctrl` 0.894, both above the 0.5× fallback guard.
  - Calibration at 64 / prompt: `lora_main` 0.975, `lora_ctrl` 0.895.
- **Lengths** on the 48, no hints (thinking = response tokens through the first `</think>`; answer = words after the
  last). Values are median of per-prompt medians / pooled median.

  | model | thinking tokens | answer words |
  |---|---|---|
  | `dpo` (F, 16 / prompt) | 1,834 / 2,260 | 231 / 253 |
  | `s2300` (F, 8 / prompt) | 5,742 / 5,811 | 31.5 / 32 |
  | `lora_main` | 6,236 / 6,392 (3.40× `dpo`) | 69.5 / 74 |
  | `lora_ctrl` | 1,963 / 2,045 (1.07×) | 235 / 246 |

  For context, hinted `dpo` at R2 / R3 thinks 4,357 / 6,829 tokens and answers 68 / 68 words, yet elicits 1 / 5 new
  prompts. Long thinking and short answers together do not, by themselves, give `lora_main`'s reach (observational,
  post hoc).
- **`s2300` sanity** (< 2 genuine of 16 breaks the rung):
  - R2 breaks it on 5 of 48 (3 of the 40 non-DROP60: `19`, `64`, `189`; plus DROP60 `3`, `188`).
  - R3 on 5 of 31 (1 non-DROP60: `189`).
  - R4 on 2 of 26 (DROP60 `4`, `188`).

### Compute (`rvl_compute.py` → `out/compute.txt`)

One pod, one community H200 at $3.59/h, 17.23 h, $61.85 (`podbudget`; budget $80).

| arm / job | samples | generated tokens | GPU-s | other |
|---|---|---|---|---|
| S0r2 + S0r3 (stage 0) | 464 | 2.28 M | 1,639 | — |
| R1cal (`dpo`) | 512 | 0.73 M | 396 | — |
| R2 (`dpo`) | 3,712 | 16.25 M | 8,760 | — |
| R3 (`dpo`) | 2,624 | 15.00 M | 8,420 | — |
| R4 (`dpo`) | 2,304 | 11.89 M | 6,664 | prompt tokens 1.35 M (few-shot) |
| S2 / S3 / S4 (`s2300`) | 928 / 656 / 576 | 5.24 / 4.07 / 3.82 M | 2,943 / 2,524 / 2,553 | — |
| `lora_main` train + finish | — | — | 380 (failed save) + 117 | 64 steps, 332,936 tokens |
| `lora_ctrl` train + finish | — | — | 291 (failed save) + 109 | 64 steps, 235,880 tokens |
| Lchk_main / Lchk_ctrl | 288 / 288 | 1.46 / 0.89 M | 13 (failed) + 1,222 / 11 (failed) + 635 | — |
| Leval_main / Leval_ctrl | 3,552 / 3,552 | 24.63 / 14.33 M | 12 (failed) + 15,777 / 8,564 | — |

- Sampling total: 19,456 samples, 100.59 M generated tokens, 16.70 GPU-h. The meta token counts equal my row sums.
- **Flags (> 1.25× the comparator):** `lora_main` vs `lora_ctrl` training tokens 1.41×; evaluation generated tokens
  1.72× and GPU-s 1.84× (`lora_main` thinks longer). Matched axes: 16 examples, 64 steps, the same prompts, 64
  evaluation attempts per prompt.

### Expectations (pre-registered, committed before any pod; `out/expect.md`)

| # | expectation | my value | verdict |
|---|---|---|---|
| 1 | rung 2 elicits 3 (0–7) of the 32 | 1 | held |
| 2 | rung 3 elicits 4 (1–9) of the rest | 5 of 31 | held |
| 3 | rung 4 elicits 3 (0–8) of the rest | 4 of 26 | held |
| 4 | prompt-elicitable 26 (19–33) | 26 | held |
| 5 | `lora_main` 4 (0–10); `lora_ctrl` 2 (0–6); most prompt-elicitable anyway | 40 (25 of them prompt-elicitable); 0 | `lora_main` **missed** (far above); `lora_ctrl` held |
| 6 | teachable from RL 1 (0–4); any fine-tune 0 (0–2) | 15; 0 | **missed**; held |
| 7 | neither 21 (13–28); of the 6 survivors 4 (2–6) neither | 7; 2 | **missed**; held |
| 8 | gamed share: R2 = R1 + 5 pp (−10 to +20); R3 0.15 (0.05–0.40); R4 0.12 (0.03–0.35); `lora_main` 0.10 (0–0.35) | +1.1 pp; 0.19; 0.26; 0.08 | held (all four) |
| 9 | calibration ≥ 0.75 at every rung; ≤ 2 prompts below half; LoRAs ≥ 0.8× `dpo` unhinted | 0.777 min; 1 prompt; 0.975 / 0.895 vs 0.725 | held |
| 10 | `lora_main` answer words 140 (60–220); `lora_ctrl` ±25 %; both LoRAs' thinking ±35 % of `dpo` | 69.5; +1.8 %; `lora_main` 3.40×, `lora_ctrl` 1.07× | words held; **`lora_main` thinking missed** |
| 11 | the four survivors: ≥ 3 of 4 at rung 2 (2–4); 0 of 4 by either LoRA (0–2) | 4; `lora_main` 4, `lora_ctrl` 0 | rung 2 held; **LoRA part missed** |
| 12 | sanity breaks `s2300` on ≤ 3 (R2) / ≤ 5 (R3, R4) of the 40 non-DROP60 | 3 of 40; 1 of 23 run; 0 of 18 run | held. R3 / R4 are scorable only on the cut-2 subsets they ran on |
| 13 | stage 0: R2 4.5k (3–7k), R3 5k (3–8k) tokens / draw | 4,449; 5,361 | held |

Stage 0 projected $89.5 (full) / $75.5 (cut 1) / $65.9 (cuts 1 + 2). Cuts 1 + 2 were applied by the pre-registered
rule. Deviation 1 (the sanity arm restored at measured throughput) and deviation 2 (the LoRA path) are recorded in the
pre-registration and match what ran.

### Open points carried to phase 2

1. Whether the write-up reports 290's strict-reading rung (2, not 1).
2. Whether it flags `188` and `3` as neither-without-an-informative-rung.
3. The 3 "teachable" prompts that fail the pre-registered Fisher sensitivity (169, 0, 170).
4. The compute flags (1.41× training tokens; 1.72× evaluation tokens).
5. The uncovered-id generalisation.
6. The 64 / 63 fixed-string overlap.
7. Expectation 12 scored on subsets.
8. The stated writing times.
9. How the "neither" set and "what transfers" are worded, against n and against what was measured (only lengths and
   NLL, no mechanism test).

## §Compare (phase 2: the executor's claims against my recount)

Read in phase 2: `run_olmo_ifladder.md`, `olmo_ifladder/plain_summary.md`, `numbers.md` § olmo-ifladder, `log.md`
§ olmo-ifladder, `olmo_ifladder/{classify.csv, handcheck.csv, handcheck_rule_addendum.md}`, the registry rows. Checks:
`rvl_compare.py` → `out/compare.txt`, `rvl_phase2_checks.py` → `out/phase2_checks.txt`, `out/registry.txt`.

**Where the two hand gates differ.** The executor's labels join to my draw keys for all 706 of its items.
- On the 590 draws we both labelled, the labels agree on 488.
- 95 of the 102 disagreements are executor-gamed / mine-genuine; 7 go the other way.
- With the executor's labels in my walk, every executor cell outcome and gamed share is reproduced exactly: R2 12,
  R3 5, R4 3, `lora_main` 40, `lora_ctrl` 0; gamed shares 15/59, 7/21, 6/19, 35/164, 1/5. So on the cells both gates read,
  every difference is labelling standard, not protocol or arithmetic. The one protocol difference is scope: I gated
  every `s2300` sanity cell; the executor gated only the prompts no earlier rung had elicited.
- Where the label gap comes from (`out/phase2_checks.txt` [8]): 87 of the 95 are labels the executor's readers gave
  and the executor kept; 8 are executor overturns.
  - As pre-registered, the executor's readers saw only the reader prompt's genuine/gamed definitions. The executor
    then confirmed every label under rules 1–6 plus its addendum rules 7–9 (`handcheck_rule_addendum.md`, committed
    02:07, after the pre-registration, before any ladder read). Rule 7: a pass resting on a lenient checker reading is
    gamed. Rule 9: a slogan or restatement answering "explain / write" is gamed.
  - My readers were given rules 1–6 directly, including rule 4 (thin answers that serve the request are genuine) and
    rule 3 (tokenisation slack).
  - So the gap is the reading of thin answers and checker-artifact passes. The executor's readers and rules 7 / 9 are
    stricter; mine apply rules 3 and 4 literally.
- Only two `dpo` / LoRA cells change outcome: R4 `ifbench_154` (a reading changes) and R2 `ifbench_179` (no reading
  depends on it). Several `s2300` sanity cells change too (below).

| claim (source) | my value | verdict |
|---|---|---|
| 48 reach prompts, 10 calibration; `dpo` 0 genuine in 256 (run, numbers) | sets rebuilt: 48 = olmo-iffu's 49 less `ifbench_281`; calibration = pre-registered 10. "0 in 256" is olmo-ifomega's, reviewed there | reproduces (inherited part labelled) |
| 19,456 draws; 100.6 M tokens; $61.85 of $80; 17.23 pod-h, 1 × H200 community $3.59/h (run, numbers) | 19,456; 100,591,013; `podbudget` $61.85 / 17.23 h | reproduces |
| prompt-elicitable at rung 1 / 2 / 3 / 4 = 16 / 1 / 5 / 3; "prompting reaches 25 of 48"; "check line +1, method hints +5, exemplars +3" (run, numbers, plain) | blind 16 / 1 / 5 / **4** (26); **16 / 1 / 5 / 3 (25) after I adjudicate one item** (below) | reproduces after adjudication. It rests on one borderline rung-4 item (`ifbench_154`) |
| 290 at rung 2 if ALL CAPS is not title case (15 / 2 / 5 / 3) | all 12 rung-2 strict successes read: 3 genuine non-ALL-CAPS | reproduces |
| **teachable from RL's trajectories 16**; any light fine-tune 0; neither 7 (run, numbers, plain) | blind **15** (154 at rung 4); **16 after adjudication**; 0; 7, the same seven prompts | reproduces after adjudication |
| `lora_main` 40 / 48 with no hint; `lora_ctrl` 0 / 48 (run, numbers, plain) | 40 (the same 40 prompts); 0 (5 strict successes on 5 prompts) | reproduces. Outcomes are identical under first-read, majority and pessimistic labels |
| "16 beyond every rung (Fisher p < 0.05 vs the control on 12, estimated counts)"; not on 0, 170, 169, 264 (run, numbers) | under my labels 13 of 16 (not 0, 170, 169). `264` passes: my read genuine share 1.0 → estimated 6 vs 0, p 0.014; the executor's share gives 2 vs 0 | label-dependent; reproduces under the executor's labels |
| `lora_main` reaches 19 of the 23 prompts whose binding id it never saw; 21 of 25 it saw (run, numbers, plain) | 19 / 23; 21 / 25 | reproduces |
| lengths: `lora_main` thinking 6,236 (`dpo` 1,834, `s2300` 5,742), answers 70 (231 / 32), median of per-prompt medians; "+240 %"; "about three times as long" (run, numbers, plain) | 6,236.25 / 1,833.5 / 5,741.5; 69.5 / 231 / 31.5 | reproduces. "Three times" is the median of medians (3.40×); the mean per draw is 6,986 vs `lora_ctrl` 3,616 (executor 6,985 / 3,613) |
| **`lora_main` gamed share 0.21**; "about one pass in five still gamed the checker" (run, numbers, plain) | executor's labels 35/164 = 0.21; **my blind labels 13/164 = 0.08** | **differs 2.7×**, by reading standard. Say 0.08–0.21 depending on the standard, or name rules 7 / 9 |
| ladder gamed shares 15/59, 7/21, 6/19; R1 6/48 (7/48 with this run's pre-screen) (numbers) | executor labels: same. Mine 8/59, 4/21, 5/19; R1 on my olmo-iffu labels 8/48 (9 ranks unread) | reproduces under the executor's labels; mine lower. Expectation 8 holds under both |
| calibration 0.777–0.861 by rung, only 298 below half; LoRAs 0.975 / 0.895 vs `dpo` 0.906; checks 0.963 / 0.894 (numbers, run) | identical | reproduces |
| LoRA table: train tokens, loss first → last 4, held-out NLL (−15.1 % / +0.7 %; `dpo` trajectories +16.9 % / +1.4 %), merge 1.12 % / 0.88 % (numbers) | identical (`out/train.txt`) | reproduces |
| held-out slice strict 106 / 51 of 128, per prompt (numbers) | 106 / 51, every per-prompt value equal | reproduces |
| "34 % of tries pass, against the RL model's 66 %" (plain) | `lora_main` strict 1,052 / 3,072 = 0.342; `s2300` unhinted fixed phase 254 / 384 = 0.661 | reproduces; these are automatic strict passes, not genuine rates |
| neither: 3 and 166 survived 1,024 draws; `lora_main` 1 genuine on e3478 and 166, 0 on the other five (run, numbers) | same | reproduces |
| **"on 166 and 188 every rung breaks `s2300`"**; "only the fine-tune test informs" (run, numbers, plain) | 188: rungs 1–4 under both gates. **166: rungs 1 and 3 under my labels.** My S2 and S4 cells for 166 each have 2 genuine of 16 (thin three-sentence answers to a "top-10 list" prompt; the executor's readers call them gamed) | 188 reproduces; **166 is reader-dependent**. Say "on 188 every rung, on 166 rungs 1 and 3 (all four on the stricter reading)" |
| 3 uninformative at rungs 1–3, not 4; 284 at rung 1 only; e3478 / 67 / 268 at none (numbers) | 3: same. **284: my olmo-iffu review found exact span copies genuine (rule 5): `s2300` 2 genuine of 4 at rung 1, so not broken.** The run inherits olmo-iffu's 0/16, which mislabelled them | 3 reproduces; **284's flag rests on an inherited label error** (it also put 284 on DROP60) |
| sanity breaks: R2 8 (0 1 3 4 166 188 · 64 189), R3 6, R4 5; gamed 0.43 / 0.46 / 0.40 (numbers) | all 48 / 31 / 26 cells gated: R2 5 (3 188 19 · 64 189), R3 5 (3 4 166 188 · 189), R4 2 (4 188); gamed 0.23 / 0.30 / 0.21 over all my gated cells (the executor's shares are over its 31 / 26 / 23) | **differs** on 0 1 4 166 (R2), 206 (R3), 1 166 206 (R4): thin answers executor-gamed, mine genuine. No reading changes (all are DROP60 or teachable prompts, except 166) |
| expectation 12 "not determined (R2 ≥ 3, at the bound)" (numbers, run) | with every non-DROP60 R2 cell gated: exactly 3 (19, 64, 189); under my more lenient labels | the executor's gate leaves it open, as stated; mine says held at the bound |
| expectations 1–13 table (numbers); misses "all one way" (run) | same verdicts after the 154 adjudication (`out/expect.md`) | reproduces; misses are reported as misses |
| compute table and flags: 1.41× training tokens, 1.27× training GPU-time, 1.71× generated tokens and 1.85× GPU-h for check + evaluation; 16.86 job GPU-h; 128 steps / 568,816 tokens; 103 registry rows (numbers, run) | identical from metas and logs. Registry: 103 rows, GPU-s sum 60,697.8 = 16.86 h, generated tokens 100,591,013, train tokens 568,816 | reproduces; flagged as policy requires |
| deviations: sanity arm restored; LoRA path; "rules 10–12 added after all `dpo` / LoRA cells were decided" (run) | true. **Rules 7–9 are also additions to the pre-registered confirming rules** (rules 1–5 + 6): written after the pre-registration, not given to readers, and the main source of the label gap above. Listed in numbers.md's method line, not as a deviation | **incomplete**: list rules 7–9 as a deviation |
| models named with checkpoint / size / format / training (numbers' Models paragraph, run setup, plain) | every number names `dpo`, `s2300`, `lora_main` or `lora_ctrl`; the LoRAs' training data is stated | reproduces |

**Wording against n.**
- `lora_main` vs `lora_ctrl` is one training run per arm: one draw of 16 trajectories, one slot order, one seed.
- The per-prompt Fisher tests treat the 64 evaluation draws as the sample; they cannot see training-run variance.
- The gap is far outside anything a reseed is likely to close (40 vs 0 prompts; strict 0.342 vs 0.002). But by the
  policy's two-seed rule the claim is "one fine-tune per arm", and the write-up should say so. It names its other
  limits (the control moves `dpo` far less: held-out NLL 1 % vs 15 %; causality of the lengths untested).

**Not mentioned in the write-up (minor).**
1. All 4 of `lora_main`'s strict successes on `ifbench_64` are, verbatim, the training answer of `ifbench_63` (the
   same fixed `repeat:repeat_simple` sentence). 64 is prompt-elicitable at rung 3 anyway.
2. The stated writing times in the pre-registration ("00:10–01:00"), `interventions.py` ("00:40–01:30") and the
   addendum ("02:10") are later than their commits (00:08:34, 00:08:34, 02:07:50).

### Corrections to §Recount (phase 2; the §Recount text above is left as committed)

1. **R4 `ifbench_154`, my adjudication: gamed.** My blind readers both said genuine under rule 3 (draw 3/0). Reading
   the answer and the checker code (`SentBalanceChecker` requires equal counts):
   - The answer has 2 statements, 1 question and 1 exclamation, and its own appended tally says so.
   - It passes only because the sentence splitter reads "relative to E. Did …" as an initial, merging a statement into
     the question.
   - That is a pass on a checker artifact with the constraint unmet in substance, so it is gamed (rule 1's spirit; the
     executor's rule 7).
   - Consequence: R4 `154` is not elicited and `154` is "teachable from RL's trajectories". My counts become 16 / 1 /
     5 / 3, **25** prompt-elicitable, **16** teachable, 7 neither, matching the executor. Expectations 3 / 4 / 6 keep
     their verdicts. Fisher: 13 of the 16 "teachable" pass under my labels. Recomputed in `out/p2_adjusted.txt`
     (`rvl_p2_adjusted.py`, `hand/confirm_phase2.json`); the phase-1 outputs are unchanged.
2. **My readers lacked rules 7–9.** Some of my genuine labels are checker-artifact passes, e.g. R2 `179` draw 1/13:
   plain prose with no attempted alliteration that passes because the checker counts alliterative pairs. My gamed
   shares are therefore lower bounds under a rule-7 standard. Of my cell outcomes, only R2 179 (no reading depends on
   it) and the sanity cells above would change.

## §Verdict

**Stands.**
- Hard constraints hold: `nd_verify` and `TEST_RUN_DONE` are unchanged; no judge is involved; training reads only its
  manifest; no weights or secrets are in the bucket.
- The run did what it pre-registered: every prompt token sequence, rung text, exemplar turn, training trajectory and
  grade was rebuilt independently. The hints carry no answer content and predate every hinted sample. No training
  prompt shares a base request with an evaluation prompt.
- The headline holds under an independent blind hand gate. 16 genuine `s2300` trajectories in a LoRA of `dpo` reach
  **40 / 48** reach prompts with no hint; the control LoRA on `dpo`'s own successes reaches **0**.
  - The effect generalises to 19 of 23 prompts whose constraint type no training prompt carried.
  - `lora_main` takes on `s2300`'s lengths (thinking 3.4×, answers 0.30× `dpo`).
- Prompting reaches 25 / 48 (16 / 1 / 5 / 3 by rung). 16 prompts are teachable from RL's trajectories, 0 by any light
  fine-tune, and the "neither" set is the same 7 prompts (e3478, 3, 67, 166, 188, 268, 284). That set is label-robust
  except 188, which rests on the mechanical rule-1 labels of its 4 rung-4 one-sentence passes; I agree with those.
- The expectations were written before any pod, and every miss is reported as a miss.

**Must be reworded.**
1. "About one pass in five still gamed the checker" / gamed share 0.21. It is 0.21 under the executor's rules 7 / 9
   and 0.08 under the pre-registered rubric my blind readers used. Name the standard, or give the range.
2. "On 166 and 188 every rung breaks `s2300`". True for 188. For 166 it holds only under the stricter reading (rungs 1
   and 3 under mine). 284's "breaks at rung 1" (and its DROP60 membership) rests on olmo-iffu labels that my
   olmo-iffu review overturned (exact span copies are genuine under rule 5).
3. The deviations line: add rules 7–9. They post-date the pre-registration's confirming rules (1–6) and are the
   written form of the stricter standard behind the label gap. 87 of the 95 one-way disagreements are the executor's
   readers' own labels, kept under these rules.
4. State that the LoRA comparison is one training run per arm.

**Not supported.** Nothing in the headline. The one reading that moved under my blind gate (154) is decided by one
borderline item, and I side with the executor on it.

**What would settle the rest.**
- **A second training draw for both arms:** a new seed and slot order, and ideally a second disjoint set of 16
  trajectories. This is what the two-seed rule asks for. At ≈ $13 (two trainings plus two 48 × 32 evaluations ≈ 16.5 M tokens at the measured
  LoRA-path rates ≈ 3.5 H200-hours) it would show whether 40 vs 0 survives the choice of trajectories.
- **The control the executor names:** a `dpo`-trajectory LoRA trained until its held-out-NLL shift matches
  `lora_main`'s. This tests whether "any fine-tune that moves `dpo` as far" reaches the same prompts.
- **An `s2300` LoRA on answers only, or on non-IF trajectories:** this separates the thinking style from the IF
  content.
- **For the gamed share and 166's sanity flag:** one fixed written standard (rules 1–9) applied by fresh readers to
  the 102 disputed draws.
