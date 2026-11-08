# Review — olmo-transplant (proposal 40)

Reviewer: agent:claude (role reviewer), a session independent of the executor. Run branch `dan_olmo-transplant`,
reviewed at `1b7fcebe` (the executor's last commit, 08:21 UTC, touched only write-ups). Kit:
`review/olmo-transplant-recount/` (README there; every number below is in `out/`). Phase 1 used the workspace
`~/review/olmo-transplant` (executor write-ups removed) and did not open `log.md`, `olmo_transplant/{README,compute,
mechanism}.md`, `results.csv`, `summary.json` or the registry's headline-rows file.

**Models (every number below is on one of these; no training in this run).** `dpo` = `allenai/Olmo-3-32B-Think-DPO`
`main` @ `97604023` (32 B, bf16, pretrained: Olmo 3 32B base → Think SFT → DPO). `s2300` = `allenai/Olmo-3.1-32B-Think`
`main` @ `97ade57a` (`dpo` after 2,300 Think-RL steps). Both revisions are the ones the pods fetched
(`logs/fetch_*.log`). Format: natural-language chat, `olmo_thinker` template; vLLM 0.11.0, T 1.0, top-p 1.0, bf16,
one H200 per job. Prompts: IFBench (`allenai/IFBench` test, 300 prompts, `cd189a9c`). Checker: the official IFBench
strict checker (my fetch). Thinking prefixes: stored `olmo-ifomega` samples of these two models.

## §Recount (phase 1, blind)

### Hard constraints and timing

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72` at HEAD = `origin/main` = the branch base; the workspace copy is identical |
| `nd_verify` / Lean as a judge | not used: no proofs in this run (IFBench answers); no `nd_verify`, `lean_check` or Lean call in `olmo_transplant/` or `pod/olmo_transplant/` |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064` = `origin/main` |
| training code reading evaluation files | no training in this run (0 steps, 0 tokens); no training script added |
| other runs' files | the run added only its own files (`olmo_transplant/`, `pod/olmo_transplant/`, `artifacts/olmo_transplant/`, `artifacts/olmo-transplant/`, its pre-registration, `run_olmo_transplant.md`, `figures/olmo_transplant.png`) and appended lines to `STATUS.md`, `log.md`, `numbers.md`, `artifacts/MANIFEST.jsonl` (0 deleted lines vs the base) |
| pre-registration before data | committed 05:35:16 (`0fea68ab`, header-time fix `15a4522d` 05:35:28, one line); first pod created 05:36:07, first job 05:43:18 |
| budget | registered 05:18 / 05:26 (`podbudget.log`); pods `ot-1` (2 × H200 community, $7.18/h, 1.218 h, $8.75) and `ot-2` (1 × H200 secure, $5.29/h, 1.715 h, $9.07): **$17.82** of $60 |

No hard-constraint violation.

### Provenance: the inserted traces are the stored ids (`rvt_provenance.py` → `out/provenance.txt`)

- **Problems.** The 51 IFBench prompts used (41 reach, 10 calibration) equal my upstream fetch (`IFBench_test.jsonl`
  @ `cd189a9c`) in prompt, instruction ids and kwargs; the run's vendored checker files are byte-identical to that
  commit.
- **Prompt sets.** Reach-41 = the `olmo-ifomega` review's 43 minus `ifbench_226` and `ifbench_252`, which have 0 `s2300`
  genuine final labels in `olmo_ifomega/handcheck.csv`; every other reach prompt has ≥ 1. Families (first instruction
  id) words 15, format 7, count 5, ratio 5, sentence 5, custom 2, repeat 2, as pre-registered. The 6 required prompts
  equal `olmo_iffu/status.csv`'s "survives 1,024" prompts that are not prompt-elicitable (3, 136, 166, 211, 248, 269);
  all 6 are in `brief20` (20 prompts, all in reach-41). Calibration: with my re-grade of `olmo-ifomega`'s fixed phase
  (`F_dpo_ifb` 16 / prompt, `F_s2300_ifb` 8 / prompt), not excluded, not a reach / reverse candidate, `dpo` ≥ 8 / 16
  and `s2300` ≥ 4 / 8 gives a pool of exactly **60**; the run's 10 are all in it, disjoint from reach; `prompts.csv`'s
  fixed-phase columns equal my re-grade on all 51; the 10 have **75** `s2300` strict successes (the 75 source
  candidates). I did not re-run the seeded stratified draws (they are the executor's RNG); I checked the criteria.
- **Traces.** All 328 rows of `traces.csv` were found in my own bucket copies of the four `olmo-ifomega` sample files.
  For every trace: my sha256 of the stored ids = `ids_sha256`; text = decode(ids) (my byte-level piece table); my
  `</think>` position = `think_k` and my sha256 of `ids[:think_k]` = `prefix_sha256`; closing ids `</` `think` then
  `>\n\n` (327) or `>\n` (1); the token before `</` ends in a newline 328 / 328. Reach `rl` traces: 115, every one
  genuine-labelled in `olmo_ifomega/handcheck.csv`, count = min(4, available) on every prompt (4 × 5, 3 × 24, 2 × 11,
  1 × 1). Under my re-grade all 115 reach and 36 calibration `rl` traces are strict successes and all 177 `dpo`
  traces strict failures.
- **Pre-registered trace statistics reproduce:** `rl` reach thinking c = think_k − 3 median 5,779, mean 6,286, max
  17,316; `dpo` reach median 2,786; cuts (c > N) 112 / 109 / 92 / 20 / 1 at 1k / 2k / 4k / 8k / 16k; my own pre-draft
  detector (first 40 whitespace-collapsed answer characters found in the thinking) finds 92 / 115 with the same token
  index as `draft_k` on every trace; position median 0.555, deciles 0.108 / 0.892.
- **Requests.** My enumeration of the pre-registered requests from the trace rows equals the four request files
  exactly (869 + 205 requests per writer; no missing, no extra), and every prefix rebuilt from the stored ids
  (`ids[:think_k]`; `ids[:N]` / `ids[:draft_k]` + `[198 if no trailing newline] + [524, 27963, 1363]`; T0
  `[198, 524, 27963, 1363]`) equals the file's prefix.
- **Every sampled answer was conditioned on exactly that input.** My prompt ids (the template text written out by me,
  tokenised with `tokenizers` from my own download of the tokenizer at both revisions; the two `tokenizer.json` files
  are identical) equal every job meta's prompt ids for all 51 prompts, and sha256(my prompt ids + request prefix) =
  `input_sha256` on all 17,184 answer rows (8 rows, i = 0…7, per request, no gaps); budgets = 32,768 − prefix length;
  every `length` finish is at the budget. F rows: phase-2 prefixes = the phase-1 ids through the first `</think>`, or
  (EOS dropped) + the closing; `natural` flags, thinking ≤ N and `input_sha256` all check (288 rows, 16 per prompt × N).
  The template is the one that generated the stored traces (same sha256 `eba6e269…` in `olmo_ifomega/sample.py`,
  `olmo_iffu/sample.py` and every job meta).
- **Template boundary, read by me** (`out/boundary_sample.txt`, 2 random rows per job × condition, 40 rows): the prompt
  ends `<|im_start|>assistant\n<think>`; the prefix starts with the stored thinking ("Okay, …"); every prefix ends
  `\n</think>\n\n`; answers start cleanly after it. Cuts fall mid-sentence or mid-word by design (e.g. a P cut after an
  opening quote `"`; a B1024 cut inside a drafted word); I saw no tokenisation seam.

### Re-grade (`rvt_regrade.py`, `rvt_sets.py` → `out/sets.txt`)

My driver around the upstream IFBench checker (original upstream prompt and kwargs, langdetect seeded) re-graded all
17,472 rows (17,184 answers + 288 fresh) and the 8,512 `olmo-ifomega` source rows. Joined with the executor's
`graded/*.jsonl`: **0 differences** in strict, per-constraint verdicts, loose and answer words; text = decode(ids) on
every row. Strict successes: R_dpo 204, R_s2300 2,600, C_dpo 1,456, C_s2300 1,499, F_s2300 123.

### Hand-gate protocol as run (`rvt_protocol.py` → `out/protocol.txt`)

`olmo_transplant/handcheck.csv` holds 425 read items (339 genuine, 86 gamed), all strict successes under my
re-grade. Every first-reader "gamed" got a second reader; 49 / 324 first-reader "genuine" (15.1 %) got one; every split
went to a third reader; no adjudication overrode a majority; no (prompt, run-condition) exceeds its read cap;
calibration B / P cells were not read (strict only, as registered). Three items on `ifbench_290` carry the rule-6
all-caps flag. Calibration source reads (75): the same protocol (14.8 % genuine re-read). Identity inheritance, as I
re-implemented it from the raw texts: of 2,804 reach strict successes, 348 are read, 1,026 equal a labelled source
answer on the same prompt, 261 equal an answer read in this run, 1,169 are unread (the cell's share applies); 0
label conflicts; every reach cell with a strict success has ≥ 1 labelled success (the 73 cells without one are
calibration B / P, strict only by design).

### My blind re-read of the deciding successes (`rvt_hand_items.py`, `rvt_hand.py`, `rvt_sharetest.py`, `rvt_vacuous.py`)

**Selection (mine, from the raw texts).** D1: every reach strict success in the cells the readings rest on — T1, T3,
T4, T0 (both writers), `dpo`'s B and P — that is not a verbatim copy of a labelled source answer (those copies carry
`olmo-ifomega`'s labels, which that run's review re-read). D2: every item the executor read in T2 and in `s2300`'s
B / P cells. D3: a seeded sample of unread `s2300` successes (30 each in B1024, B2048, B4096, P; 20 in T2), to test the
share rule. D4: every F2048 success, every F item the executor read, 15 unread each at F4096 and F8192. 827 samples →
799 distinct (prompt, answer) items, random ids, shuffled across cells, the pre-registered reader view (prompt,
constraints with the checker's verdicts, answer, word count) and rules 1–6 (rule 6 as a separate flag;
`hand/reader_prompt.md`). Readers (blinded Claude subagents barred from every other file): A on all 799; B on every
A-gamed item, a seeded 15 % of A-genuine items and every item where A differs from the executor's label (270); C on
every A/B split (21). Final = majority. A and B agree on 249 / 270 (92 %). Final labels 637 genuine, 162 gamed. My
adjudication rules were written before any C label (`hand/confirm_rules.md`); none of the disagreements rests on a
checkable factual error, so no majority was overridden (`hand/confirm.json` is empty).

**Agreement with the executor.** On the 376 samples the executor read and I re-read, labels agree on 365 (97.1 %:
284 both genuine, 81 both gamed); 10 executor-genuine / my-gamed (one each in T1 `ifbench_203`, T2 `253`, T3 `179`, T0-`s2300`
`1`, B1024 `203`, P `19`; two each in B2048 and B4096, on `187` and `268`) and 1 executor-gamed / my-genuine (P `203`).
The T3 `179` item is the one rule-3 borderline: my readers' observation (longest alliterative run 2 in both sentences)
is correct, but IFBench's `alliteration_increment` counts all alliterative pairs, so the checker's own count passes; I
left the majority (gamed) as my rules require. On 429 unread successes I read, the executor's share rule predicted
346.3 genuine and my readers found 355 (0.807 vs 0.828); by cell it is close everywhere except **fresh F4096**
(predicted 15.0 of 15, found 9) and T0-`s2300` (65.2 vs 76).

**A mechanical rule-1 failure of the share rule (`ifbench_136`).** IFBench's `format:sub-bullets` checker splits the
answer on `*` and only asks for a `-` in each chunk, so an answer with no `*` at all passes — the pre-registered rule
1's own example of a gamed answer. Across the three sub-bullet prompts (128, 133, 136), 85 of `s2300`'s 411 reach
strict successes, 17 of the 37 F successes and 4 of `dpo`'s 51 contain no `*`. Every one the executor's readers read
was labelled gamed, but the unread ones took their cell's share, which came from non-vacuous reads: 7 of 14 F4096 and
3 of 12 F8192 successes on 136, all unread, were counted genuine at share 1.0. With rule 1 applied mechanically (no-`*` answers gamed; shares from the remaining labels), the executor's labels
give fresh F4096 0.354 instead of 0.427, F8192 0.573 instead of 0.604 and F2048 0.167 instead of 0.182 (my labels:
F4096 0.318 as read, 0.330 with the mechanical rule; F8192 0.604 / 0.573; F2048 0.167 / 0.167). No reach-41
condition rate moves by more than 0.01 (B1024-`s2300` −0.009).

### Rates, contrasts and curves (`rvt_rates.py` → `out/rates_{strict,exec,mine,mine_vac}.txt`; tables by `rvt_tables.py`)

A condition's rate is the mean over prompts (equal weight) of the per-prompt rate; genuine = strict × the
(prompt, run-condition) genuine share applied to unread successes, as registered; 95 % percentile prompt bootstrap
(10,000 resamples, my seed). Columns: strict; genuine with the executor's labels (my re-implementation of its rules:
reads, identity inheritance, share); genuine with my blinded labels; my labels with rule 1 applied mechanically.
Primary B curve: every `rl` trace, traces with c ≤ N contributing their full-condition rows. The calibration genuine
columns rest on ≤ 1 executor read per (prompt, cell) that I did not re-read; calibration B / P are strict only.

**reach-41** (mean over prompts, 95 % prompt bootstrap)

| condition | strict | genuine (executor's labels) | genuine (my blinded labels) | genuine (my labels + rule 1 mechanical) |
|---|---|---|---|---|
| T2 | 0.935 [0.891, 0.971] | 0.924 [0.873, 0.966] | 0.922 [0.870, 0.964] | 0.922 [0.870, 0.964] |
| T1 | 0.139 [0.080, 0.211] | 0.139 [0.080, 0.211] | 0.138 [0.079, 0.211] | 0.138 [0.079, 0.211] |
| T3 | 0.101 [0.049, 0.162] | 0.060 [0.023, 0.110] | 0.060 [0.022, 0.111] | 0.060 [0.022, 0.111] |
| T4 | 0.001 [0.000, 0.002] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| T0-s2300 | 0.112 [0.051, 0.188] | 0.078 [0.030, 0.138] | 0.085 [0.037, 0.146] | 0.085 [0.037, 0.146] |
| T0-dpo | 0.003 [0.001, 0.006] | 0.001 [0.000, 0.002] | 0.001 [0.000, 0.002] | 0.001 [0.000, 0.002] |
| P-s2300 | 0.511 [0.410, 0.614] | 0.453 [0.345, 0.565] | 0.458 [0.358, 0.564] | 0.459 [0.358, 0.563] |
| P-dpo | 0.021 [0.010, 0.035] | 0.020 [0.009, 0.034] | 0.020 [0.009, 0.034] | 0.020 [0.009, 0.034] |
| B1024-s2300 | 0.269 [0.182, 0.365] | 0.209 [0.122, 0.310] | 0.208 [0.121, 0.309] | 0.199 [0.118, 0.293] |
| B2048-s2300 | 0.392 [0.305, 0.483] | 0.355 [0.262, 0.452] | 0.336 [0.248, 0.431] | 0.333 [0.247, 0.427] |
| B4096-s2300 | 0.587 [0.481, 0.690] | 0.530 [0.420, 0.640] | 0.518 [0.413, 0.623] | 0.518 [0.413, 0.623] |
| B8192-s2300 | 0.793 [0.688, 0.886] | 0.780 [0.669, 0.879] | 0.778 [0.667, 0.876] | 0.778 [0.667, 0.876] |
| B16384-s2300 | 0.931 [0.885, 0.967] | 0.919 [0.867, 0.963] | 0.917 [0.864, 0.960] | 0.917 [0.864, 0.960] |
| B1024-dpo | 0.032 [0.003, 0.084] | 0.029 [0.000, 0.080] | 0.029 [0.000, 0.080] | 0.029 [0.000, 0.080] |
| B2048-dpo | 0.038 [0.008, 0.091] | 0.038 [0.008, 0.091] | 0.037 [0.007, 0.090] | 0.037 [0.007, 0.090] |
| B4096-dpo | 0.062 [0.023, 0.119] | 0.057 [0.019, 0.113] | 0.061 [0.022, 0.118] | 0.061 [0.022, 0.118] |
| B8192-dpo | 0.124 [0.064, 0.196] | 0.124 [0.064, 0.196] | 0.124 [0.063, 0.195] | 0.124 [0.063, 0.195] |
| B16384-dpo | 0.139 [0.080, 0.211] | 0.139 [0.080, 0.211] | 0.138 [0.079, 0.211] | 0.138 [0.079, 0.211] |

**brief20** (mean over prompts, 95 % prompt bootstrap)

| condition | strict | genuine (executor's labels) | genuine (my blinded labels) | genuine (my labels + rule 1 mechanical) |
|---|---|---|---|---|
| T2 | 0.926 [0.857, 0.976] | 0.916 [0.832, 0.975] | 0.916 [0.832, 0.975] | 0.916 [0.832, 0.975] |
| T1 | 0.119 [0.048, 0.202] | 0.119 [0.048, 0.202] | 0.119 [0.048, 0.202] | 0.119 [0.048, 0.202] |
| T3 | 0.089 [0.019, 0.180] | 0.038 [0.005, 0.084] | 0.039 [0.003, 0.089] | 0.039 [0.003, 0.089] |
| T4 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| T0-s2300 | 0.103 [0.016, 0.223] | 0.047 [0.002, 0.125] | 0.056 [0.006, 0.134] | 0.056 [0.006, 0.134] |
| T0-dpo | 0.003 [0.000, 0.008] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| P-s2300 | 0.525 [0.356, 0.692] | 0.434 [0.264, 0.615] | 0.427 [0.271, 0.594] | 0.428 [0.272, 0.593] |
| P-dpo | 0.010 [0.002, 0.020] | 0.008 [0.000, 0.016] | 0.008 [0.000, 0.016] | 0.008 [0.000, 0.016] |
| B1024-s2300 | 0.221 [0.109, 0.351] | 0.145 [0.042, 0.277] | 0.145 [0.042, 0.277] | 0.128 [0.041, 0.233] |
| B2048-s2300 | 0.339 [0.232, 0.455] | 0.316 [0.208, 0.433] | 0.298 [0.197, 0.413] | 0.293 [0.196, 0.404] |
| B4096-s2300 | 0.534 [0.381, 0.684] | 0.502 [0.350, 0.651] | 0.471 [0.325, 0.623] | 0.471 [0.325, 0.623] |
| B8192-s2300 | 0.782 [0.627, 0.915] | 0.775 [0.620, 0.909] | 0.775 [0.620, 0.909] | 0.775 [0.620, 0.909] |
| B16384-s2300 | 0.917 [0.846, 0.971] | 0.906 [0.821, 0.969] | 0.906 [0.821, 0.969] | 0.906 [0.821, 0.969] |
| B1024-dpo | 0.005 [0.000, 0.014] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| B2048-dpo | 0.009 [0.000, 0.021] | 0.009 [0.000, 0.021] | 0.007 [0.000, 0.016] | 0.007 [0.000, 0.016] |
| B4096-dpo | 0.025 [0.000, 0.056] | 0.015 [0.000, 0.040] | 0.023 [0.000, 0.052] | 0.023 [0.000, 0.052] |
| B8192-dpo | 0.105 [0.034, 0.188] | 0.105 [0.034, 0.188] | 0.105 [0.034, 0.188] | 0.105 [0.034, 0.188] |
| B16384-dpo | 0.119 [0.048, 0.202] | 0.119 [0.048, 0.202] | 0.119 [0.048, 0.202] | 0.119 [0.048, 0.202] |

**calibration (10)** (mean over prompts, 95 % prompt bootstrap)

| condition | strict | genuine (executor's labels) | genuine (my blinded labels) | genuine (my labels + rule 1 mechanical) |
|---|---|---|---|---|
| T2 | 1.000 [1.000, 1.000] | 0.933 [0.800, 1.000] | 0.933 [0.800, 1.000] | 0.933 [0.800, 1.000] |
| T1 | 0.988 [0.969, 1.000] | 0.988 [0.969, 1.000] | 0.988 [0.969, 1.000] | 0.988 [0.969, 1.000] |
| T3 | 0.769 [0.594, 0.944] | 0.625 [0.287, 0.938] | 0.625 [0.287, 0.938] | 0.625 [0.287, 0.938] |
| T4 | 0.656 [0.425, 0.887] | 0.656 [0.425, 0.887] | 0.656 [0.425, 0.887] | 0.656 [0.425, 0.887] |
| T0-s2300 | 0.794 [0.606, 0.950] | 0.694 [0.459, 0.903] | 0.694 [0.459, 0.903] | 0.694 [0.459, 0.903] |
| T0-dpo | 0.713 [0.500, 0.900] | 0.613 [0.372, 0.834] | 0.613 [0.372, 0.834] | 0.613 [0.372, 0.834] |
| P-s2300 | 0.980 [0.964, 0.995] | n/a | n/a | n/a |
| P-dpo | 0.941 [0.858, 0.997] | n/a | n/a | n/a |
| B1024-s2300 | 0.922 [0.844, 1.000] | n/a | n/a | n/a |
| B2048-s2300 | 0.963 [0.931, 0.994] | n/a | n/a | n/a |
| B4096-s2300 | 0.994 [0.981, 1.000] | n/a | n/a | n/a |
| B8192-s2300 | 0.984 [0.953, 1.000] | n/a | n/a | n/a |
| B16384-s2300 | 0.997 [0.991, 1.000] | n/a | n/a | n/a |
| B1024-dpo | 0.947 [0.884, 0.994] | n/a | n/a | n/a |
| B2048-dpo | 0.969 [0.931, 0.997] | n/a | n/a | n/a |
| B4096-dpo | 0.991 [0.978, 1.000] | n/a | n/a | n/a |
| B8192-dpo | 0.988 [0.969, 1.000] | n/a | n/a | n/a |
| B16384-dpo | 0.988 [0.969, 1.000] | n/a | n/a | n/a |

**Paired contrasts by prompt** (mean [95 %]; realised SD; MDD = 2.80 SD / √n)

| set | contrast | strict | genuine (executor's labels) | genuine (my blinded labels) | genuine (my labels + rule 1 mechanical) |
|---|---|---|---|---|---|
| reach | Δ21 = T2 − T1 | 0.796 [0.722, 0.862]; SD 0.228; MDD 0.099 (n 41) | 0.785 [0.708, 0.853]; SD 0.238; MDD 0.104 (n 41) | 0.783 [0.705, 0.853]; SD 0.242; MDD 0.106 (n 41) | 0.783 [0.705, 0.853]; SD 0.242; MDD 0.106 (n 41) |
| reach | Δ34 = T3 − T4 | 0.100 [0.048, 0.162]; SD 0.190; MDD 0.083 (n 41) | 0.060 [0.023, 0.110]; SD 0.146; MDD 0.064 (n 41) | 0.060 [0.022, 0.111]; SD 0.147; MDD 0.064 (n 41) | 0.060 [0.022, 0.111]; SD 0.147; MDD 0.064 (n 41) |
| reach | Δ0 = T0s − T0d | 0.109 [0.049, 0.184]; SD 0.221; MDD 0.097 (n 41) | 0.077 [0.030, 0.136]; SD 0.173; MDD 0.076 (n 41) | 0.085 [0.036, 0.144]; SD 0.177; MDD 0.077 (n 41) | 0.085 [0.036, 0.144]; SD 0.177; MDD 0.077 (n 41) |
| reach | Δ30 = T3 − T0s | -0.011 [-0.059, 0.035]; SD 0.153; MDD 0.067 (n 41) | -0.018 [-0.055, 0.014]; SD 0.114; MDD 0.050 (n 41) | -0.025 [-0.061, 0.007]; SD 0.111; MDD 0.049 (n 41) | -0.025 [-0.061, 0.007]; SD 0.111; MDD 0.049 (n 41) |
| reach | T1 − T0d | 0.136 [0.078, 0.207]; SD 0.215; MDD 0.094 (n 41) | 0.138 [0.079, 0.210]; SD 0.217; MDD 0.095 (n 41) | 0.138 [0.079, 0.210]; SD 0.218; MDD 0.095 (n 41) | 0.138 [0.079, 0.210]; SD 0.218; MDD 0.095 (n 41) |
| reach | R1 = T1 / T2 | 0.149 [0.086, 0.225] | 0.151 [0.087, 0.227] | 0.150 [0.086, 0.227] | 0.150 [0.086, 0.227] |
| brief20 | Δ21 = T2 − T1 | 0.807 [0.714, 0.888]; SD 0.207; MDD 0.130 (n 20) | 0.796 [0.693, 0.886]; SD 0.229; MDD 0.143 (n 20) | 0.796 [0.693, 0.886]; SD 0.229; MDD 0.143 (n 20) | 0.796 [0.693, 0.886]; SD 0.229; MDD 0.143 (n 20) |
| brief20 | Δ34 = T3 − T4 | 0.089 [0.019, 0.180]; SD 0.194; MDD 0.121 (n 20) | 0.038 [0.005, 0.084]; SD 0.096; MDD 0.060 (n 20) | 0.039 [0.003, 0.089]; SD 0.104; MDD 0.065 (n 20) | 0.039 [0.003, 0.089]; SD 0.104; MDD 0.065 (n 20) |
| brief20 | Δ0 = T0s − T0d | 0.100 [0.013, 0.222]; SD 0.252; MDD 0.158 (n 20) | 0.047 [0.002, 0.125]; SD 0.163; MDD 0.102 (n 20) | 0.056 [0.006, 0.134]; SD 0.159; MDD 0.099 (n 20) | 0.056 [0.006, 0.134]; SD 0.159; MDD 0.099 (n 20) |
| brief20 | Δ30 = T3 − T0s | -0.014 [-0.091, 0.064]; SD 0.179; MDD 0.112 (n 20) | -0.009 [-0.058, 0.036]; SD 0.110; MDD 0.069 (n 20) | -0.017 [-0.059, 0.025]; SD 0.099; MDD 0.062 (n 20) | -0.017 [-0.059, 0.025]; SD 0.099; MDD 0.062 (n 20) |
| brief20 | T1 − T0d | 0.116 [0.047, 0.196]; SD 0.182; MDD 0.114 (n 20) | 0.119 [0.048, 0.202]; SD 0.186; MDD 0.116 (n 20) | 0.119 [0.048, 0.202]; SD 0.186; MDD 0.116 (n 20) | 0.119 [0.048, 0.202]; SD 0.186; MDD 0.116 (n 20) |
| brief20 | R1 = T1 / T2 | 0.129 [0.053, 0.216] | 0.130 [0.054, 0.219] | 0.130 [0.054, 0.219] | 0.130 [0.054, 0.219] |
| calib | Δ21 = T2 − T1 | 0.013 [0.000, 0.031]; SD 0.030; MDD 0.027 (n 10) | -0.054 [-0.191, 0.028]; SD 0.206; MDD 0.183 (n 10) | -0.054 [-0.191, 0.028]; SD 0.206; MDD 0.183 (n 10) | -0.054 [-0.191, 0.028]; SD 0.206; MDD 0.183 (n 10) |
| calib | Δ34 = T3 − T4 | 0.113 [0.019, 0.231]; SD 0.141; MDD 0.176 (n 5) | -0.031 [-0.206, 0.087]; SD 0.200; MDD 0.251 (n 5) | -0.031 [-0.206, 0.087]; SD 0.200; MDD 0.251 (n 5) | -0.031 [-0.206, 0.087]; SD 0.200; MDD 0.251 (n 5) |
| calib | Δ0 = T0s − T0d | 0.081 [-0.022, 0.225]; SD 0.222; MDD 0.196 (n 10) | 0.081 [-0.022, 0.225]; SD 0.222; MDD 0.196 (n 10) | 0.081 [-0.022, 0.225]; SD 0.222; MDD 0.196 (n 10) | 0.081 [-0.022, 0.225]; SD 0.222; MDD 0.196 (n 10) |
| calib | Δ30 = T3 − T0s | 0.081 [-0.056, 0.219]; SD 0.183; MDD 0.229 (n 5) | -0.062 [-0.475, 0.219]; SD 0.471; MDD 0.590 (n 5) | -0.062 [-0.475, 0.219]; SD 0.471; MDD 0.590 (n 5) | -0.062 [-0.475, 0.219]; SD 0.471; MDD 0.590 (n 5) |
| calib | T1 − T0d | 0.275 [0.094, 0.478]; SD 0.329; MDD 0.291 (n 10) | 0.375 [0.159, 0.606]; SD 0.384; MDD 0.340 (n 10) | 0.375 [0.159, 0.606]; SD 0.384; MDD 0.340 (n 10) | 0.375 [0.159, 0.606]; SD 0.384; MDD 0.340 (n 10) |
| calib | R1 = T1 / T2 | 0.988 [0.969, 1.000] | 1.058 [0.972, 1.238] | 1.058 [0.972, 1.238] | 1.058 [0.972, 1.238] |

**Retained gain F(N) = (G(N) − G(0)) / (G(full) − G(0))**, primary curve, reach-41

| writer | N | strict | genuine (executor's labels) | genuine (my blinded labels) | genuine (my labels + rule 1 mechanical) |
|---|---|---|---|---|---|
| s2300 | 1024 | 0.190 | 0.155 | 0.147 | 0.136 |
| s2300 | 2048 | 0.340 | 0.328 | 0.299 | 0.297 |
| s2300 | 4096 | 0.577 | 0.534 | 0.517 | 0.517 |
| s2300 | 8192 | 0.827 | 0.830 | 0.828 | 0.828 |
| s2300 | 16384 | 0.994 | 0.995 | 0.995 | 0.995 |
| s2300 | P | 0.485 | 0.444 | 0.446 | 0.446 |
| dpo | 1024 | 0.213 | 0.202 | 0.203 | 0.203 |
| dpo | 2048 | 0.259 | 0.272 | 0.266 | 0.266 |
| dpo | 4096 | 0.431 | 0.404 | 0.435 | 0.435 |
| dpo | 8192 | 0.892 | 0.894 | 0.893 | 0.893 |
| dpo | 16384 | 1.000 | 1.000 | 1.000 | 1.000 |
| dpo | P | 0.133 | 0.139 | 0.140 | 0.140 |

**Pre-registered readings (reach-41, genuine).** The verdicts are the same under every label column above, under
rule 6's strict reading (`out/rates_{exec,mine}_r6.txt`) and under a natural sub-bullet reading (`out/rates_mine_sb.txt`):

1. *In the thinking:* R1 = 0.150 [0.086, 0.227] (needs ≥ 0.75) and T1 − T0-`dpo` = 0.138 (needs ≥ 0.30): **no**.
2. *Answer writing:* R1 ≤ 0.40 holds, but T3 = 0.060 (needs ≥ 0.22) and Δ34 = 0.060 (needs ≥ 0.15): **no**.
3. *Partly:* **holds, through its "neither 1 nor 2" clause** — R1 is far below the 0.40–0.75 band. Δ21 = 0.783,
   Δ34 = 0.060, Δ0 = 0.085.
4. *Needs long search:* F_s2300(2,048) = 0.299 (needs ≤ 0.25) and G_s2300(2,048) = 0.336 (needs ≤ T0-`dpo` + 0.10 =
   0.101) fail; F_s2300(8,192) = 0.828 ≥ 0.60 and fresh F(2,048) = 0.27 × natural ≤ 0.5 hold: **no**.
5. *Flat:* T0-`s2300` = 0.085 against T2 − 0.10 = 0.822: **no**. 6. *Graded:* **yes**.
7. *P:* F_dpo(P) = 0.140 ≤ 0.25 → for `dpo` "the success rests on the drafted answer" (denominator G(full) − G(0) =
   0.138, just above the 0.10 floor); F_s2300(P) = 0.446 → neither threshold (0.263 strict if re-thought answers count
   as failures, below).

**Expected results (pre-registered table) against my values** (`rvt_expect.py` → `out/expect_mine.md`; my labels,
reach-41; the fresh-F and calibration rows are strict as registered):

| quantity | expected | range | reviewer (mine labels; reach-41 unless named) | verdict | note |
|---|---|---|---|---|---|
| T2 | 0.8 | 0.65–0.95 | 0.922 | within |  |
| T1 | 0.55 | 0.3–0.8 | 0.138 | below |  |
| R1 = T1 / T2 | 0.7 | 0.45–0.95 | 0.150 | below |  |
| T3 | 0.08 | 0.01–0.25 | 0.060 | within |  |
| T4 | 0.02 | 0.0–0.08 | 0.000 | within |  |
| T0-s2300 | 0.08 | 0.0–0.25 | 0.085 | within |  |
| T0-dpo | 0.02 | 0.0–0.06 | 0.001 | within |  |
| G_s2300(1024) | 0.12 | -0.03–0.27 | 0.208 | within |  |
| G_s2300(2048) | 0.2 | 0.05–0.35 | 0.336 | within |  |
| G_s2300(4096) | 0.4 | 0.25–0.55 | 0.518 | within |  |
| G_s2300(8192) | 0.7 | 0.55–0.85 | 0.778 | within |  |
| G_dpo(1024) | 0.05 | -0.1–0.2 | 0.029 | within |  |
| G_dpo(2048) | 0.1 | -0.05–0.25 | 0.037 | within |  |
| G_dpo(4096) | 0.25 | 0.1–0.4 | 0.061 | below |  |
| G_dpo(8192) | 0.45 | 0.3–0.6 | 0.124 | below |  |
| F_s2300(2,048) | 0.2 | 0.05–0.45 | 0.299 | within |  |
| F_s2300(P) | 0.35 | 0.1–0.7 | 0.446 | within |  |
| F_dpo(P) | 0.25 | 0.1–0.7 | 0.140 | within |  |
| draft in cut prefix − not, s2300 (pooled points) | >= 0.30 | 0.15–0.6 | 0.255 | within |  |
| draft in cut prefix − not, s2300 (prompt-weighted) | >= 0.30 | 0.15–0.6 | 0.288 | within |  |
| draft in cut prefix − not, dpo (pooled points) | >= 0.30 | 0.15–0.6 | 0.026 | below |  |
| draft in cut prefix − not, dpo (prompt-weighted) | >= 0.30 | 0.15–0.6 | 0.020 | below |  |
| fresh F(2048) / natural strict (fixed phase) | 0.3 | 0.05–0.55 | 0.383 | within | all olmo-ifomega s2300 draws: 0.33 |
| fresh F(4096) / natural strict (fixed phase) | 0.6 | 0.35–0.85 | 0.683 | within | all olmo-ifomega s2300 draws: 0.58 |
| fresh F(8192) / natural strict (fixed phase) | 0.9 | 0.65–1.15 | 0.983 | within | all olmo-ifomega s2300 draws: 0.83 |
| calibration T1 (strict) | 0.9 | 0.7–1.1 | 0.988 | within |  |
| calibration T2 (strict) | 0.9 | 0.7–1.1 | 1.000 | within |  |
| calibration T0-dpo (strict) | 0.6 | 0.4–0.8 | 0.713 | within |  |
| calibration T0-s2300 (strict) | 0.6 | 0.4–0.8 | 0.794 | within |  |
| answers cut at the budget | < 1 % in every condition | – | max 3.12 % (C_s2300 B8192) | miss | C_s2300 P 5/184; C_s2300 B4096 4/136; C_s2300 B8192 2/64 |

With the executor's labels the verdicts are the same except G_s2300(2,048) = 0.355, just **above** its 0.05–0.35
range (`out/expect_exec.md`). Misses: T1 and R1 (far below), G_dpo(4k) and G_dpo(8k) (below), the `dpo` draft split
(below), and the budget-cut share (three calibration `s2300` cells above 1 %; every reach cell ≤ 0.27 %).

### Mechanism checks the pre-registration did not ask for (post hoc; `rvt_mech.py`, `rvt_copy.py`, `rvt_lengths.py`)

- **The writer often keeps thinking after the forced `</think>`.** A sampled answer that itself contains `</think>`
  means the writer wrote more reasoning after the supplied closing, closed again, and the grader took the text after
  the second closing. On reach this happens in 28.4 % of `s2300`'s P samples (209 / 736; median 2,431 extra tokens),
  7.8 / 8.8 / 3.7 / 10.0 % of its B1024 / B2048 / B4096 / B8192 samples (median 4,725–8,456 extra tokens), 7.4 % of
  its T0 samples, 0 % of T2 and 0.6 % of T3. Among `s2300`'s strict successes, 152 / 397 in P, 42 / 245 in B1024,
  45 / 345 in B2048 and 11 / 147 in T0 are such re-thought answers. `dpo` re-thinks in 4–10 % of its cut / P samples
  but almost never succeeds that way (8 of its 17 P successes; 0 in B). Counting re-thought answers as failures
  ("budget held"), the strict `s2300` curve becomes G(1k / 2k / 4k / 8k) 0.221 / 0.339 / 0.574 / 0.779 (F 0.141 / 0.283
  / 0.566 / 0.812, from 0.190 / 0.340 / 0.577 / 0.827), and **F_s2300(P) falls from 0.485 to 0.263** (G(P) 0.511 →
  0.322). Fresh F(2,048) falls from 0.240 to 0.177. So "thinking capped at N" is not enforced by the forced closing
  for `s2300`; the P reading and the small-N end of the curve depend on how re-thought answers are counted.
- **Copies.** Given its own successful thinking (T2), `s2300` reproduces the trace's final answer verbatim in 611 /
  920 samples (66 %; whitespace-collapsed equality) and near-verbatim (word 3-gram Jaccard ≥ 0.8) in 75 more: 681 of
  its 867 T2 strict successes (79 %) are exact or near copies. `dpo` given the same thinking (T1) copies exactly in
  43 / 920 and nearly in 11; 53 of its 137 T1 strict successes (39 %) are exact or near copies, 73 (53 %) share
  < 0.5 of their 3-grams with the trace's answer. `dpo`'s T1 answers are long (median 126 words; `s2300`'s source
  answers: median 26) — given RL's thinking, `dpo` mostly writes its own answer rather than the one drafted.
- **Secondary curves (cut traces only)** are much flatter than the primary curve: `s2300` strict 0.250 / 0.377 / 0.514
  / 0.384 at 1k / 2k / 4k / 8k (the same traces' full rate 0.93–0.94; 0.915 at 8k, 11 prompts). The primary curve's
  0.793 at 8k comes from the 95 of 115 traces that are not cut there. By N / c (post hoc, pooled points), `s2300`
  strict 0.239 / 0.325 / 0.563 / 0.734 in quarters of the trace; `dpo` 0.004 / 0.007 / 0.034 / 0.048.

### Compute (`rvt_compute.py` → `out/compute.txt`)

| job (writer, set) | GPU (all H200, TP 1) | wall GPU-s (every attempt) | samples | generated tokens | input tokens submitted | checker calls |
|---|---|---|---|---|---|---|
| R_dpo (`dpo`, reach) | `ot-1` | 3,326 (513 killed stage-0 run + 12 failed start + 2,801) | 6,952 | 4,796,394 | 2,735,529 | 6,952 |
| R_s2300 (`s2300`, reach) | `ot-2` | 2,509 | 6,952 | 3,309,001 | 2,735,529 | 6,952 |
| C_dpo (`dpo`, calibration) | `ot-1` | 446 | 1,640 | 823,570 | 581,278 | 1,640 |
| C_s2300 (`s2300`, calibration) | `ot-2` | 1,646 | 1,640 | 1,631,474 | 581,278 | 1,640 |
| F_s2300 (`s2300`, fresh) | `ot-2` | 1,153 | 288 | 1,275,080 (1,189,805 thinking + 85,275 answers) | – | 288 |
| **total** | | **9,080 (2.52 GPU-h)** | 17,472 | 11,835,519 | | 17,472 |

Billed: `ot-1` 2 × H200 for 1.218 h (every job log shows `gpu=0`; its second GPU ran no job) and `ot-2` 1 × H200 for 1.715 h = 4.15 GPU-h, **$17.82**
(rate × hours reproduces both reap-log dollar figures). No training, no Lean. Against the projection (≈ 17,600 answers
+ 288 fresh, ≈ 5.3 M generated tokens, $8–20): 17,184 + 288 samples, 11.8 M generated tokens (answers ≈ 2× longer
than projected), $17.82 — inside the dollar range. The meta files' `max_mem_alloc_gb` is 0.0 (vLLM allocates in its
engine process); the `*_smi.log` files are the only memory record.

### Bucket, MANIFEST, secrets (`rvt_hygiene.py`, `rvt_hygiene_hit.py`)

The 17 MANIFEST entries the run added (samples, graded rows, requests, the source index, the two registry files)
match their bucket objects byte for byte (sha256 and size) and the local files I analysed. A secret-pattern scan of
the contents of all 629 objects under `hf://buckets/dan-pandori/nd-rl/olmo-transplant/` (gzip members decompressed)
has one hit, a 20-character `AKIA…` run inside a base64 `ids` field of `samples/R_dpo.jsonl.gz` — token ids, not a
credential. No fetch failed.

### Deviations from the pre-registration seen in phase 1

- F (fresh forcing) used one engine seed (8103) for both phases; the pre-registration names 8103 (thinking) / 8104
  (answers). Calibration jobs used seeds 8111 / 8112 (not named). Neither changes the sampling distribution.
- R_dpo was killed after its stage-0 part (513 s, 1,384 rows kept, 0 partial requests dropped) and resumed with 24
  groups in flight under the same engine seed; the row checks above cover both parts.
- Readers' rule 6 and inheritance were applied as registered; calibration B / P were strict only, as registered.

Phase 1 ends here, committed before I opened the executor's write-ups. One disclosure: while checking that the
shared files are append-only (after every number above was computed) I printed the `STATUS.md` diff and so saw
the executor's two-line status summary (its T1 / T2 headline); nothing above was changed after that.

## §Compare (phase 2: the executor's claims against my recount)

Read after the §Recount commit (`e80ba754`): `run_olmo_transplant.md`, `numbers.md` § olmo-transplant,
`olmo_transplant/{plain_summary,summary,mechanism,compute}.md`, `results.csv`, `summary.json`, `log.md`, `STATUS.md`,
the registry rows and the figure. Checks: `rvt_phase2_checks.py` → `out/phase2_checks.txt`; facts outside the sample
files (hashes, times, template fields): `rvt_facts.py` → `out/facts.txt`. "Exec labels" = the executor's labels
through my code; "mine" = my blinded labels. `results.csv` (918 rows) against my per-prompt tables: strict 918 / 918
and genuine 845 / 845 equal to 6 × 10⁻⁵ (900 condition rows + 18 fresh-forcing rows; the 73 calibration B / P cells
that are strict-only by design are excluded, see #24).

| # | claim (where) | my value | verdict |
|---|---|---|---|
| 1 | Setup: two models, 41 reach + 10 calibration, thinking re-inserted by token ids, "only answers were sampled (17,472)", $17.82 (run) | provenance checks all pass; 17,184 answers after supplied thinking + 288 fresh-forcing samples whose thinking was sampled too; $17.82 | reproduces ("only answers" holds for 17,184 of the 17,472) |
| 2 | T0 0.00 / 0.08 [0.03, 0.14]; T4 / T3 0.00 / 0.06 [0.02, 0.11]; P 0.02 / 0.45 [0.34, 0.56]; T1 / T2 **0.14** [0.08, 0.21] / **0.92** [0.87, 0.97] (run table) | exec labels 0.001 / 0.078, 0.000 / 0.060, 0.020 / 0.453, 0.139 / 0.924; mine 0.001 / 0.085, 0.000 / 0.060, 0.020 / 0.458, 0.138 / 0.922 | reproduces (intervals differ only by bootstrap seed) |
| 3 | `dpo` 0 on 20 of 41 prompts with RL's full thinking (run 1) | 20 / 41 (strict, exec, mine) | reproduces |
| 4 | `dpo`'s T1 answers 126 words (median) vs RL's 26; 183 of the 256 that contain RL's drafted answer verbatim add constraint-breaking text (run 1); `mechanism.md` 43 exact copies, 726 > 1.5×; T2 611 / 641 / 10 / 14 | 126 / 26; 256 contain, 183 fail strict, all 183 longer than RL's answer; 43; 726; T2 611 / 641 / 10 / 14 | reproduces |
| 5 | Calibration T1 vs T2 0.99 vs 1.00 strict (run 1) | 0.988 / 1.000 | reproduces |
| 6 | "Nor does RL's answer writing alone: 0.08 without thinking, 0.06 after `dpo`'s failed thinking. It takes both." (run 2) | 0.078 / 0.060 (mine 0.085 / 0.060); Δ0 = T0-`s2300` − T0-`dpo` 0.077 [0.030, 0.136] (mine 0.085 [0.036, 0.144], above its MDD 0.077) | reproduces; see #13 for "necessary" |
| 7 | Budget graded: RL cut at 1k / 2k / 4k / 8k 0.21 / 0.36 / 0.53 / 0.78; `dpo` never exceeds 0.14 (run 3) | exec 0.209 / 0.355 / 0.530 / 0.780; mine 0.208 / 0.336 / 0.518 / 0.778; `dpo` max 0.139 | reproduces (primary curve). The pre-registered cut-only curve is missing (#23); the run write-up's prose mentions re-opened thinking only for P, although 8–9 % of B1k / B2k answers re-open it and carry 17 % / 13 % of the strict successes (`numbers.md` gives the post-hoc value for every cell) |
| 8 | Fresh forcing 0.27 / 0.62 / 0.88 of `s2300`'s natural rate (run 3; numbers: genuine 0.27 [0.12, 0.40] / 0.62 [0.37, 0.86] / 0.88 [0.63, 1.04], strict 0.33 / 0.58 / 0.83) | natural genuine baseline 0.685 (mine; the executor's `summary.md` states the same 0.685); exec labels 0.27 / 0.62 / 0.88; strict 0.33 / 0.58 / 0.83; **mine 0.24 / 0.46 / 0.88; exec labels + rule 1 mechanical 0.24 / 0.52 / 0.84** | **differs at 4k**: 7 of the 14 strict F4096 successes on `ifbench_136` contain no `*` (vacuous under rule 1) and were counted genuine through that cell's 2 genuine reads; the 6 unread F4096 successes on 136 that I read are all gamed under my labels (5 of them vacuous). Strict ratios reproduce |
| 9 | "The draft helps but is not required. P gives 0.45, or 0.28 if answers that re-open thinking (28 %) count as failures (post hoc)" (run 4) | 0.453 (mine 0.458); 0.283; 209 / 736 = 28.4 %. On the executor's own F(P) definition (G(0), G(P), G(full) over the 38 prompts with a P cell): F_s2300(P) 0.453 as graded; **0.258 (exec labels) / 0.250 (mine) with re-opened thinking counted as failure** | numbers reproduce; **reword**: under the post-hoc count `s2300` sits on reading 7's "rests on the drafted answer" threshold (≤ 0.25), on one side or the other depending on the labels; as graded it is "neither" |
| 10 | Readings: 1 and 2 fail, leaving 3 ("partly") with a graded curve (6); "needs long search" fails, 0.33 of the gain at 2k > 0.25 (run; log; STATUS) | same verdicts under every label variant; F_s2300(2k) exec 0.328, mine 0.299; `brief20`: R1 0.130, T3 0.038 (mine 0.039), F_s2300(2k) 0.310 (mine 0.282) → readings 3 and 6 | reproduces. Reading 3 holds through its "neither 1 nor 2" clause: R1 = 0.15 lies in reading 2's R1 range, not in the 0.40–0.75 "partly" band; worth saying |
| 11 | Reading 7 (P) | not stated in the write-up. On the executor's definition: F_dpo(P) 0.146 (exec and mine; 0.073 post hoc) ≤ 0.25 → "the success rests on the drafted answer" for `dpo`; F_s2300(P) 0.453 / 0.454 (neither), 0.258 / 0.250 post hoc | **omitted** pre-registered reading |
| 12 | `brief20` agrees (run deviations; log) | as #10 | reproduces |
| 13 | "RL's thinking is necessary but not sufficient" (run; STATUS); "The thinking is necessary (more of it, more success)" (plain) | not sufficient: T1 0.14 vs T2 0.92; but with **no** thinking `s2300` reaches 0.08 genuine where `dpo` has 0.001, and Δ0 is above its MDD | **reword**: "carries most of the gain, not all of it" (the plain summary's own "part answer-writing discipline" says as much) |
| 14 | Against expectations: below T1, T1 / T2, `dpo`'s curve at 4k and 8k, its draft effect (+0.03); above RL at 2k; all else inside (run) | same misses; G_s2300(2k) 0.355 (exec labels, above 0.35) but 0.336 with mine (inside) | reproduces; "above at 2k" is label-sensitive by 0.02 |
| 15 | RL's draft effect +0.16 (expected ≥ 0.30) (run); draft covariate `s2300` 0.546 (n 808) vs 0.390 (n 2,600), `dpo` 0.037 vs 0.012 (numbers) | reproduces when the P cuts are pooled into "without" (0.390, n 2,600); B cuts only: 0.546 vs 0.330 (+0.215; prompt-weighted +0.27; mine genuine +0.26 / +0.29); `dpo` +0.029 | reproduces under its definition; inside the registered 0.15–0.60 range either way |
| 16 | "Two calibration cells had > 1 % of answers cut at the response cap (2.7 %, 1.4 %)" (run); "calibration up to 2.7 % (`s2300` P 5 / 184, B4096 4 / 288)"; reach 0–0.22 % (numbers) | per condition as sampled: calibration `s2300` P 5 / 184 (2.7 %), **B4096 4 / 136 (2.9 %), B8192 2 / 64 (3.1 %)**; reach max 2 / 736 (0.27 %, B4096-`dpo`) | **differs**: B cuts were divided by the primary-curve cell (sampled + substituted full rows); three calibration cells exceed 1 %, max 3.1 % |
| 17 | Conditions table (strict, genuine, post-hoc re-opened = fail), contrasts, retained gains, calibration strict (numbers; `summary.md`) | every cell of the conditions table reproduces to 3 decimals with exec labels, including the post-hoc column (21 / 21, my `exec_held` mode); contrasts and F(N) reproduce; F(P) reproduces on the executor's definition (0.453 / 0.146; `brief20` 0.449 / 0.061) — my §Recount's 0.444 used G(0), G(full) over all 41 prompts | reproduces |
| 18 | Hand gate: 425 items 339 / 86, readers per item 275 / 132 / 18; rule 6 strict changes means ≤ 0.002 (numbers); per-family means (`summary.md`) | 425, 339 / 86, 275 / 132 / 18; ≤ 0.002; family table identical to mine | reproduces; my blind re-read agrees on 97.1 % of shared samples |
| 19 | Compute: 17,472 answers, 11.84 M generated tokens, **2.35 H200-hours in jobs**, 17,472 checker calls; $17.82, 2.93 pod-hours (numbers; registry compute rows) | 11,835,519 tokens; 17,472 calls; $17.82; 2.93 pod-h; job wall time over every attempt 9,080 s = **2.52 GPU-h** | **differs**: 2.35 h is each job's last-attempt `t_load + t_gen` (registry sum 8,477.7 s); it omits R_dpo's killed stage-0 attempt (513 s, whose 1,384 rows are kept) and its 12 s failed restart (with them 2.50 h; the last 77 s is job overhead). The registry's R_dpo `gpu_seconds` (2,770 s) is 16.7 % below its 3,326 s of job wall time |
| 20 | Pre-registration before any pod; F seed 8103 for both phases and calibration seeds 8111 / 8112 disclosed (log) | prereg 05:35:16; first pod created 05:35:50 (executor's log) / registered 05:36:07 (`~/pods.log`); seeds in `log.md` | reproduces (the seed deviations are in the log, not the write-up's deviation line) |
| 21 | Bucket: 17 bulk files with sha256 in MANIFEST; credential scan of 613 objects, 0 hits (numbers; log) | 17 / 17 match; my scan of 629 objects: 1 pattern hit, inside a base64 `ids` field (not a credential) | consistent in substance (no credential found by either); the scans differ in patterns and object count |
| 22 | Plain summary: "never succeeded genuinely in 256 tries", 14 % vs 92 %, "often copies it", "about five times longer", 8 % / 6 %, 21 / 36 / 53 / 78 %, "Fresh thinking … looks similar", "(99 %)" on easy prompts, ≈ 44 % everyday rate, re-opened-thinking caveat | 0.139 / 0.924; 28 % of `dpo`'s T1 answers contain RL's answer, 4.7 % copy it exactly; 126 / 26 = 4.8×; 0.078 / 0.060; 0.209 / 0.355 / 0.530 / 0.780; fresh strict share of natural 0.33 / 0.58 / 0.83 vs B retained gain 0.34 / 0.58 / 0.83; 0.988; 0.604 × 0.73 = 0.44 | reproduces; "often copies it" fits "contains" (28 %), not exact copies; "looks similar" holds as a share of the natural rate, not in absolute rates; the "256 tries" figure is `olmo-ifomega`'s and is not attributed in the plain summary (the ≈ 44 % is) |
| 23 | Pre-registered "two B curves" (the secondary, cut traces only) and "against N / c, post hoc in bins" | absent from the write-up, `numbers.md`, `summary.md`, `summary.json`, `results.csv` and the figure. Mine: `s2300` cut-only 0.19 / 0.32 / 0.43 / 0.35 (genuine, mine; 40 / 40 / 37 / 11 prompts), against the same traces' full rate 0.92–0.93 (0.88 at 8k); strict 0.25 / 0.38 / 0.51 / 0.38 against 0.93–0.94 (0.92 at 8k); by N / c quarters, strict, 0.24 / 0.33 / 0.56 / 0.73 (`dpo` 0.004 / 0.007 / 0.034 / 0.048) | **omitted** pre-registered analyses. They matter for "graded": the primary curve's 0.78 at 8k comes from the 95 of 115 traces that are not cut there |
| 24 | `results.csv` column `genuine_rate` | its 118 calibration B / P rows with strict successes (strict-only cells by design) still carry a number; in 75 it is below the strict rate because unread successes count as not genuine (e.g. `ifbench_115` B1024-`dpo`: strict 1.0, genuine 0.0, 32 unlabelled) | file defect; no write-up uses these values. Blank them |

**Model labels.** `numbers.md` names checkpoint, revision, size, precision, lineage (pretrained, DPO / RL), format and
"no training" for every number; the write-up and plain summary name the two models (the write-up without revision
hashes). In the registry, the 108 strict / genuine rate rows carry the checkpoint, but all 96 `contrast` rows have
`ckpt` empty, including single-writer retained gains (F_s2300(N), F_dpo(N)), and the 168 compute rows name the writer
only through `arm`. The plain summary's "never succeeded genuinely in 256 tries" is `olmo-ifomega`'s number (same two
models) without an attribution. Nothing is attributed to the wrong model.

**Expectations and misses.** The expectations were committed at 05:35:16, before any pod. The write-up reports the
misses it found (T1, R1, `dpo`'s curve at 4k / 8k, `dpo`'s draft effect, RL at 2k, the calibration cuts; RL's draft
effect +0.16 is listed next to them although it is inside its 0.15–0.60 range). It under-counts the calibration cut
cells (#16), and "RL at 2k" depends on the labels (#14).

### Corrections to §Recount (found after the phase-1 commit; the §Recount text above is left as committed)

The adversarial check of this review (`out/adversarial_check.md`, an independent subagent, 25 findings) found these
errors in §Recount; all other findings are fixed in §Compare / §Verdict above.

1. The cut-traces-only B curve and the N / c bins are **pre-registered** ("Two B curves"; "Also against N / c, post hoc
   in bins"), not "mechanism checks the pre-registration did not ask for" (§Recount, third bullet of that list).
2. Reading 4's fresh clause: genuine F(2,048) over the genuine natural rate is 0.167 / 0.685 = **0.24** (my labels);
   the 0.27 divided by the strict fixed-phase rate. Strict over strict: 0.38 (fixed phase) or 0.33 (all draws). The
   clause (≤ 0.5) holds either way.
3. "First pod created 05:36:07": 05:36:07 is `~/pods.log`'s registration; the executor's log gives creation at
   05:35:50. Both follow the pre-registration commit (05:35:16).
4. "`dpo` re-thinks in 4–10 % of its cut / P samples but almost never succeeds that way (8 of its 17 P successes; 0 in
   B)" → never in B, but in P 8 of its 17 strict successes are re-thought answers (strict F_dpo(P) 0.133 → 0.067).
5. "Copies carry `olmo-ifomega`'s labels, which that run's review re-read" → that review re-read **78 of the 115**
   reach `rl` trace labels (by sample key; `out/phase2_checks.txt` [12]); the other 37 rest on `olmo-ifomega`'s
   readers alone.
6. Share test: besides F4096 and T0-`s2300`, R_dpo B4096 is off (predicted 10.0 of 14, found 14), which moves
   F_dpo(4096) from 0.404 to 0.435.
7. "Every number below is in `out/`": the git hashes, commit / pod / job times, the template field per job meta and
   the R_dpo resume line are now in `out/facts.txt`. "The same sha256 in … every job meta" holds for the four
   answer-sampling jobs; the F job's meta has no template field (its prompt ids equal mine).
8. F_s2300 input tokens: 1,210,335 (phase 1 counted once per (prompt, N) request), matching the executor's 1.21 M;
   §Recount's table showed "–".
9. The calibration genuine columns also rest on identity inheritance from the executor's 75 calibration-source labels,
   not only on ≤ 1 read per (prompt, cell).
10. The T3 `ifbench_179` alliteration item is a judgement call (my rule 2 allows an override for a constraint the
    answer "verifiably meets", and the checker's own count passes); I left the majority (gamed). Either label moves T3
    by < 0.001.

## §Verdict

**Stands.** The data are what the pre-registration says: every inserted thinking prefix equals the stored ids, and
every one of the 17,184 answers was sampled after exactly the registered input; grades reproduce with 0 differences;
every per-prompt rate in `results.csv` and every condition rate, contrast and retained gain in `numbers.md` reproduces.
My independent blind re-read of 799 deciding items agrees with the executor's labels on 97.1 % of shared samples; with
my labels every reach-41 condition rate is within 0.02 of the executor's (the 6-prompt fresh-forcing F4096 rate is not:
#8), and no pre-registered reading changes. The headline holds: given `s2300`'s own successful thinking, `dpo` writes a
genuine answer 0.14 of the time against `s2300`'s 0.92 (R1 = 0.15 [0.09, 0.23]); `s2300` with no thinking or with
`dpo`'s failed thinking scores 0.06–0.09; readings 1, 2, 4 and 5 fail and 3 and 6 hold, also on `brief20`. The T1
mechanism counts reproduce exactly: 256 of `dpo`'s 920 T1 answers (28 %) contain RL's drafted answer verbatim, and 183
of those fail, every one by adding words. Cost $17.82 of $60. No hard-constraint violation.

**Must be reworded or added.**
1. Fresh forcing at 4k: "0.62 of its natural rate" → 0.46–0.52 (my labels / rule 1 applied mechanically), or report
   the strict 0.58. Unread vacuous `ifbench_136` answers were counted genuine (#8); F8192's 0.88 is 0.84 with rule 1.
2. State reading 7: `dpo` F(P) = 0.15 ≤ 0.25, "the success rests on the drafted answer"; `s2300` 0.45, neither
   threshold, as graded, but 0.25–0.26 — on the copying threshold — when answers that re-open thinking count as
   failures. "The draft helps but is not required" needs that qualifier (#9, #11).
3. "RL's thinking is necessary" → "carries most of the gain": `s2300` without any thinking still scores 0.08–0.09 where
   `dpo` scores 0.00 (#13).
4. Report the pre-registered cut-only B curve and N / c bins (#23): on cut traces `s2300` is 0.19 / 0.32 / 0.43 / 0.35
   at 1k–8k against 0.88–0.93 for the same traces in full (genuine, my labels), so the primary curve's "graded" rise at 4k–8k is mostly uncut
   traces entering at their full value.
5. Budget-cut misses: three calibration cells, 2.7 / 2.9 / 3.1 % of the answers actually sampled (#16).
6. Compute: 2.52 GPU-h of job time (2.35 omits R_dpo's kept stage-0 attempt); add 525 s to R_dpo's registry
   `gpu_seconds` (#19). Blank `results.csv`'s calibration B / P `genuine_rate` (#24); put `ckpt` on the registry's
   single-writer contrast rows.
7. Worth saying (not errors): the forced `</think>` does not cap `s2300`'s thinking — 28 % of P and 8–9 % of
   B1k / B2k answers re-open it, a confound for every "capped at N" reading (numbers.md has the post-hoc column; the
   run write-up's prose names it for P only); reading 3 holds through its "neither" clause (#10); the draft split
   pools P cuts into "without" (#15); the plain summary's "256 tries" needs its source.

**Not supported.** No headline claim. Wrong as stated: the 4k fresh-forcing ratio (#8), the calibration cut-share
figures (#16) and the job GPU-hours (#19). Omitted: reading 7 and the cut-only curve with the N / c bins (#11, #23).

**Next measurements.** (1) Enforce the budget: re-sample the B, P and F answers with a second `</think>` banned (or
generation stopped at it) so "thinking capped at N" holds, and re-read P under that. (2) Test the T1 mechanism
directly: T1 with the `olmo-iffu` brevity instruction ("answer in at most 60 words"), or with RL's drafted answer
supplied as the answer's first line; if `dpo` then approaches T2, the transplant gap is answer-writing discipline, not
missing search. (3) Read (or rule-1 filter) every unread strict success on the three sub-bullet prompts, so the share
rule cannot carry vacuous answers.
