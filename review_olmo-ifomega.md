# Review: olmo-ifomega (reviewer session, 2026-11-06)

Run `olmo-ifomega` (brief: nd-rl `docs/proposals/followups/BRIEF_olmo-ifomega.md`, proposal 36). Models, as the run
labels them, used throughout:
- `dpo` = `allenai/Olmo-3-32B-Think-DPO` `main` (`97604023`), the RL start;
- `s0100` / `s0750` / `s2300` = `allenai/Olmo-3.1-32B-Think` `step_0100` / `step_0750` / `main` (`e7b80281` /
  `418fb274` / `97ade57a`; `main` = `step_2300`, identical weights).

All four are 32 B, bf16, pretrained (Olmo 3 32B base → Think SFT → DPO; the three RL checkpoints then RLVR on
`Dolci-Think-RL-32B`), producing natural-language text. Every number below is measured on these models and on this
run's prompts unless it says otherwise:
- IFBench test, 300 prompts, headline 218 non-excluded;
- IFEval, a seeded 150-prompt subset;
- OMEGA explorative `test_out`, 100 problems from 10 families.

Kit: `review/olmo-ifomega-recount/` (code I wrote; every number below is in its `out/` or `hand/`). Lean does not
apply to this run: there are no proofs. IF answers are judged by the official IFBench / IFEval checkers, and OMEGA
answers by OLMES's exact match and open-instruct's MathVerifier. In place of the brief's Lean re-check I did three
things:
- re-graded every stored text with each grader, running the upstream code at the pinned commits;
- checked every OMEGA candidate's official label by computing the answer myself;
- repeated the hand check blind on the deciding responses.

## §Recount (phase 1: written before reading `run_olmo_ifomega.md`, `numbers.md` or `log.md`)

### R0. What I read, and how blind this is

**Read:**
- the run brief;
- `preregistration/olmo-ifomega.md`: Part A, Part B, its addendum, the deviations list 1–20 and Part C;
- the code (`olmo_ifomega/*.py`, `vendor/`);
- the raw artefacts: 39 sample files (46,434 texts with token ids), the executor's per-sample grade rows (`graded/`,
  for the row-by-row comparison only), job meta and vLLM logs, the plan files (`plan/*.pids`, `*.prior`, `*.stop`),
  and the contamination scans;
- `exclusions.csv` and `contamination.csv`, which the brief asks me to check;
- `compute_extra.csv`, `compute_rows.py` and the registry rows, to check the compute record.

**Not read:**
- `run_olmo_ifomega.md`, `numbers.md`, `log.md`, the plain summary, `STATUS*`, `olmo_ifomega/README.md`,
  `scaleup_memo.md`;
- the executor's derived tables: `results.csv`, `passk.csv`, `candidates*.csv`, `verdict.csv`, `dynamics.csv`,
  `compute_axis.csv`, `lengths_mix.csv`, `constraints*.csv`, `ifeval_misses.csv`, `failures_*`;
- any hand-check file: `handcheck*.{csv,py,md}`, `handcheck_rule_if.md`, `artifacts/olmo_ifomega/hand/`.

My readers' rubrics (`hand/reader_prompt_{if,omega}.md`) were written from the pre-registration's definitions alone.

**Limits on blindness:**
1. Session start showed the last five git subjects, which name outcomes:
   - "step_0100 on IFBench restored (pass@1 0.315 …)";
   - "IFEval done (strict and hand Reach, 6 prompts …)";
   - "geometry_basic_010 … (o19, o20: 1 sound of 7)";
   - "geometry_basic_010 o17/o18 (guess, flawed)".
2. The pre-registration's deviations, written during the run, state some outcomes:
   - 49 IFBench reach prompts where `dpo` has 0 strict successes in 256;
   - IFEval's 8 reach and 1 reverse candidates;
   - 11 IFBench prompts left open by a stopping rule for hand-checking challengers;
   - `dpo`'s first four doubly-credited `geometry_basic_010` successes read as a guess and three flawed;
   - the `geometry_perpendicular_intersection_055` label error;
   - `step_0750` adding `geometry_basic_010` as a candidate.
3. The plan files' `.prior` counts encode the executor's hand-gate state for nine jobs (e.g. `ifbench_47:0`).
4. A memory note on the VPS mentions a restart failure in this run (process only, no result).

I re-derived every one of these myself. My hand-check readers saw none of them.

### R1. Hard constraints and rules

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72…` at HEAD = `origin/main`; the workspace copy is identical; `git status` clean |
| `nd_verify` unused as a judge | no `olmo_ifomega/` file imports or calls it; the run grades natural-language answers |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064…` = `origin/main`'s |
| evaluation data in training code | the run trains nothing |
| Lean | not applicable (no proofs); the judges are the official checkers, pre-registered |

No hard-constraint violation.

### R2. Prompts, models, decoding, storage

**Prompts** (`rv_provenance.py`, `out/provenance.txt`; my own fetch of every pinned input):
- **IFBench.** All 300 prompts equal the IFBench repo's `IFBench_test.jsonl` @ `cd189a9c` and the HF parquet
  `allenai/IFBench_test` @ `ed7c1245` on prompt, instruction list and kwargs. 256 have one constraint and 44 have two,
  across 58 instruction ids.
- **IFEval.** The 150 evaluation prompts and 40 Stage-0 prompts are exactly the seeded draw the pre-registration names
  (`random.Random(int(sha256("20261104|ifeval")[:16], 16))` over the key-sorted 541). All 150 equal `google/IFEval`
  @ `966cd895`.
- **OMEGA.** All 240 problems (200 evaluation + 40 Stage-0) equal their `omega-explorative` @ `b04ae8d4` row: prompt,
  original text and label. No label carries surrounding whitespace.
  - 31 families have ≥ 100 distinct RL prompts. The seeded family draw reproduces the ten families, and the problem
    draws reproduce in all 20 family × split cells with my own normaliser and renaming-class key.
  - No chosen problem equals an RL prompt, an OMEGA train / compositional / transformative problem, or a
    single-letter renaming of one.
  - Pool sizes match the pre-registration (combinatory 59 / 57 `test_in`, 46 / 48 `test_out`).
  - 33 `test_in` problems across all families equal an RL prompt, as stated.
  - All 10,870 distinct RL OMEGA prompts equal an OMEGA train problem, and 40 of 41 explorative families occur
    (not `logic_zebralogic`), as stated.
- Stage-0 and evaluation prompts are disjoint.

**Models** (Hub metadata):
- The commits match the pre-registration.
- `main` and `step_2300` of `Olmo-3.1-32B-Think` have identical LFS sha256 on all 14 weight shards; only
  `README.md`, `.eval_results` and the index json differ.
- `config.json` is identical across the four checkpoints except `use_cache` (`dpo` True, RL False), which vLLM does
  not read.
- `tokenizer.json`, `vocab.json`, `merges.txt` and `special_tokens_map.json` share blobs. `tokenizer_config.json`
  differs only in an embedded `chat_template` (absent in `dpo`), which the sampler overrides.

**Decoding and template.**
- All 37 job meta records report T 1.0, top-p 1.0, 32,768 max tokens, vLLM 0.11.0, one H200 at TP 1, and the same
  template sha256 `eba6e269…`. That sha equals open-instruct `CHAT_TEMPLATES["olmo_thinker"]` @ `7e780f2fea`, byte for
  byte (my own extraction).
- The two Stage-0 jobs carry no meta, and Stage 0 is never evaluated.
- Decoding and template are the same across all four models.

**Storage** (`rv_decode.py`, `out/decode_check.txt`). Over all 46,434 stored samples:
- `text` == `decode(ids, skip_special_tokens=True)` with the shared tokenizer, and `len(ids)` == `n_tok`;
- every `stop` row ends in EOS 100257;
- every `length` row (2,195) has exactly 32,768 tokens;
- 358,143,850 generated tokens in all.

Gzip integrity: two files have a second gzip member (`E1_dpo_oo3`, `F_s0750_oo`). Both read to their end with no
partial line, and no (job, chunk, index) key is duplicated.

### R3. Re-grade of every stored text (`rv_graders.py`, `rv_regrade.py`, `rv_gradecmp.py`)

My graders run the upstream code itself:
- **IF:** IFBench `evaluation_lib` @ `cd189a9c` and google-research `instruction_following_eval` @ `e6890f85`. My fetch
  is byte-identical to the run's `vendor/` (all 11 sha256 match).
- **OMEGA `omega`:** OLMES @ `5a51f502`. `GenericTask._extract_answer`, `extract_answer` and `exact_match_hf_evaluate`
  are taken from the files by `ast` and run with the `omega_*:0-shot-chat` metric kwargs parsed from
  `oe_eval/configs/tasks.py`.
- **OMEGA `rl`:** open-instruct `MathVerifier` @ `7e780f2fea` through `async_call`, as RL ran it.
- The answer is the text after the last `</think>`, stripped (pre-registered). langdetect is seeded as in the run.

Joined row by row with the executor's grade rows (46,434 rows, none missing on either side):

| grade | rows | disagreements |
|---|---|---|
| IF `strict` / `loose` / `rlview` / per-constraint | 40,774 | 12 / 15 / 11 / 15, **all on `ifeval_1122`** |
| OMEGA `omega` / `rl` / `doubly` | 5,650 | 0 / 0 / 0 (the 11 stored `omega_ans` strings that differ are my 120-character truncation of theirs) |
| `n_tok`, `finish`, `think_end` | 46,434 | 0 |

**Finding (minor): `ifeval_1122`'s grade is a random draw.** The prompt asks for "at least 4 '#'". IFEval's
`LetterFrequencyChecker` accepts only a–z, so it replaces '#' with `random.choice(string.ascii_letters)` on every
check. The prompt's strict grade is therefore random in both the executor's grading and mine. The run seeds langdetect
but not this, so "re-grading reproduces" does not hold for this prompt. It is not a reach or reverse candidate, and it
moves IFEval pass@1 by at most 1/150.

My own final-answer diagnostic for OMEGA (`own`: last `\boxed{}` of the answer, numeric compare) gives the same
candidate sets and verdict as `omega` (R4–R5).

### R4. Cell table and fixed-phase pass@k (`rv_cells.py`, `rv_stats.py`; `out/cells.csv`, `out/stats.json`)

1,950 model × prompt cells. Draw order is fixed phase → extension (E1 < E2 < E3) or confirmation (C1 < C2 < C3). No
model is both defender and challenger on a prompt (asserted). Unbiased pass@k, 10,000-resample prompt bootstrap for
k = 1 and 8 (2,000 for the others). Fixed phase only: `dpo` 16 and each RL checkpoint 8 per prompt.

| task (prompts) | grade | model | samples | pass@1 [95 % CI] | pass@8 [95 % CI] | pass@16 |
|---|---|---|---|---|---|---|
| ifbench headline (218) | strict | dpo | 3488 | 0.290 [0.237, 0.345] | 0.461 [0.395, 0.527] | 0.509 [0.440, 0.578] |
| ifbench headline (218) | strict | s0100 | 1744 | 0.315 [0.263, 0.371] | 0.505 [0.445, 0.573] | – |
| ifbench headline (218) | strict | s0750 | 1744 | 0.512 [0.460, 0.562] | 0.794 [0.743, 0.849] | – |
| ifbench headline (218) | strict | s2300 | 1744 | 0.683 [0.635, 0.732] | 0.885 [0.844, 0.927] | – |
| ifbench headline (218) | loose | dpo | 3488 | 0.347 [0.292, 0.403] | 0.552 [0.488, 0.611] | 0.619 [0.555, 0.683] |
| ifbench headline (218) | loose | s0100 | 1744 | 0.373 [0.318, 0.427] | 0.583 [0.518, 0.647] | – |
| ifbench headline (218) | loose | s0750 | 1744 | 0.549 [0.494, 0.600] | 0.812 [0.757, 0.862] | – |
| ifbench headline (218) | loose | s2300 | 1744 | 0.707 [0.660, 0.755] | 0.904 [0.867, 0.940] | – |
| ifbench all (300) | strict | dpo | 4800 | 0.280 [0.238, 0.324] | 0.439 [0.389, 0.490] | 0.480 [0.427, 0.533] |
| ifbench all (300) | strict | s0100 | 2400 | 0.297 [0.254, 0.342] | 0.483 [0.427, 0.537] | – |
| ifbench all (300) | strict | s0750 | 2400 | 0.478 [0.436, 0.523] | 0.757 [0.707, 0.807] | – |
| ifbench all (300) | strict | s2300 | 2400 | 0.676 [0.636, 0.715] | 0.880 [0.840, 0.913] | – |
| ifeval headline (150) | strict | dpo | 2400 | 0.768 [0.712, 0.817] | 0.908 [0.865, 0.948] | 0.927 [0.880, 0.967] |
| ifeval headline (150) | strict | s0750 | 1200 | 0.884 [0.839, 0.922] | 0.947 [0.907, 0.980] | – |
| ifeval headline (150) | strict | s2300 | 1200 | 0.935 [0.900, 0.964] | 0.973 [0.947, 0.993] | – |
| ifeval headline (150) | loose | dpo | 2400 | 0.809 [0.760, 0.853] | 0.948 [0.914, 0.976] | 0.960 [0.927, 0.987] |
| ifeval headline (150) | loose | s0750 | 1200 | 0.914 [0.879, 0.946] | 0.980 [0.953, 1.000] | – |
| ifeval headline (150) | loose | s2300 | 1200 | 0.947 [0.912, 0.973] | 0.980 [0.953, 1.000] | – |
| omega_out headline (100) | omega | dpo | 1600 | 0.274 [0.206, 0.344] | 0.521 [0.434, 0.601] | 0.610 [0.520, 0.700] |
| omega_out headline (100) | omega | s0750 | 800 | 0.550 [0.466, 0.629] | 0.710 [0.620, 0.800] | – |
| omega_out headline (100) | omega | s2300 | 800 | 0.624 [0.540, 0.708] | 0.730 [0.640, 0.810] | – |
| omega_out headline (100) | rl | dpo | 1600 | 0.302 [0.233, 0.375] | 0.557 [0.468, 0.639] | 0.640 [0.540, 0.730] |
| omega_out headline (100) | rl | s0750 | 800 | 0.566 [0.484, 0.641] | 0.710 [0.620, 0.800] | – |
| omega_out headline (100) | rl | s2300 | 800 | 0.632 [0.549, 0.715] | 0.730 [0.640, 0.810] | – |
| omega_out headline (100) | own | dpo | 1600 | 0.276 [0.207, 0.347] | 0.530 [0.446, 0.615] | 0.620 [0.530, 0.710] |
| omega_out headline (100) | own | s0750 | 800 | 0.552 [0.472, 0.631] | 0.720 [0.630, 0.810] | – |
| omega_out headline (100) | own | s2300 | 800 | 0.635 [0.552, 0.719] | 0.740 [0.660, 0.820] | – |

Matched-k entries and exits at k = 8 (expected: Σ pass@8_c (1 − pass@8_dpo) and Σ (1 − pass@8_c) pass@8_dpo, bootstrap intervals; observed sets against `dpo`'s first 8 draws and against its 16):

| task | grade | checkpoint | expected entries @8 [CI] | expected exits @8 [CI] | observed entries / exits (vs dpo's first 8) | (vs dpo's 16) |
|---|---|---|---|---|---|---|
| ifbench | strict | s0100 | 19.92 [12.87, 27.58] | 10.51 [5.19, 15.93] | 21 / 11 | 14 / 15 |
| ifbench | strict | s0750 | 75.64 [62.97, 89.22] | 3.23 [0.77, 6.46] | 76 / 3 | 67 / 5 |
| ifbench | strict | s2300 | 98.27 [84.61, 112.72] | 5.86 [2.23, 10.18] | 98 / 5 | 90 / 8 |
| ifeval | strict | s0750 | 6.7 [2.66, 11.26] | 0.96 [0.0, 2.88] | 7 / 1 | 4 / 1 |
| ifeval | strict | s2300 | 10.7 [5.29, 16.79] | 0.96 [0.0, 2.88] | 11 / 1 | 8 / 1 |
| omega_out | omega | s0750 | 19.87 [14.07, 26.74] | 1.0 [0.0, 2.5] | 21 / 0 | 12 / 2 |
| omega_out | omega | s2300 | 21.37 [15.08, 28.86] | 0.5 [0.0, 1.5] | 23 / 0 | 13 / 1 |
| omega_out | rl | s0750 | 16.61 [11.27, 22.93] | 1.27 [0.0, 3.3] | 18 / 1 | 9 / 2 |
| omega_out | rl | s2300 | 17.84 [12.24, 24.58] | 0.5 [0.0, 1.5] | 19 / 0 | 10 / 1 |

Lengths (fixed phase):

| task | model | samples | mean tokens | cut at 32,768 | closes `</think>` |
|---|---|---|---|---|---|
| ifbench | dpo | 4800 | 4,391 | 0.0004 | 1.0000 |
| ifbench | s0100 | 2400 | 4,326 | 0.0000 | 0.9996 |
| ifbench | s0750 | 2400 | 5,650 | 0.0013 | 1.0000 |
| ifbench | s2300 | 2400 | 6,487 | 0.0000 | 0.9996 |
| ifeval | dpo | 2400 | 2,508 | 0.0000 | 1.0000 |
| ifeval | s0750 | 1200 | 3,291 | 0.0000 | 1.0000 |
| ifeval | s2300 | 1200 | 4,536 | 0.0067 | 0.9933 |
| omega_out | dpo | 1600 | 24,709 | 0.2175 | 0.7937 |
| omega_out | s0750 | 800 | 22,030 | 0.1150 | 0.9000 |
| omega_out | s2300 | 800 | 20,873 | 0.0512 | 0.9575 |

### R5. Candidates, extension audit, automatic verdicts

Candidates (Design 2), per grade:
- reach R = `dpo` 0/16 and some RL checkpoint ≥ 1/8;
- reverse V = `dpo` ≥ 1/16 and `s2300` 0/8.

Fates, all within 256 draws per model:
- **reach:** `s2300` confirmed (≥ 2 successes, ≥ 1 fresh) and `dpo` 0 in a full 256;
- **dpo resolved:** `dpo` ≥ 2;
- **dissolved:** every challenger complete and unconfirmed;
- **open:** anything else, by reason.

| task | grade | \|R\| | reach (s2300 confirmed, dpo 0 in 256) | dpo resolved (≥ 2 in 256) | open | \|V\| | reverse | s2300 resolved | V open | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ifbench|headline | strict | 94 | 49 | 33 | 12 (dpo_one_success 12) | 8 | 2 | 5 | 1 | Reach |
| ifbench|headline | loose | 73 | 24 | 35 | 14 (dpo_one_success 12, dpo_incomplete 2) | 8 | 2 | 4 | 2 | Reach |
| ifbench|headline | rlview | 94 | 49 | 33 | 12 (dpo_one_success 12) | 8 | 2 | 5 | 1 | Reach |
| ifbench|all | strict | 133 | 49 | 33 | 51 (dpo_incomplete 39, dpo_one_success 12) | 8 | 2 | 5 | 1 | Reach |
| ifeval|headline | strict | 8 | 6 | 1 | 1 (dpo_one_success 1) | 1 | 1 | 0 | 0 | Reach |
| ifeval|headline | loose | 6 | 5 | 1 | 0 () | 3 | 1 | 0 | 2 | Reach |
| omega_out|headline | omega | 14 | 3 | 9 | 2 (dpo_one_success 2) | 1 | 0 | 1 | 0 | Reach |
| omega_out|headline | rl | 11 | 2 | 8 | 1 (dpo_one_success 1) | 1 | 0 | 1 | 0 | Inconclusive |
| omega_out|headline | doubly | 14 | 3 | 9 | 2 (dpo_one_success 2) | 1 | 0 | 1 | 0 | Reach |
| omega_out|headline | own | 14 | 3 | 9 | 2 (dpo_one_success 2) | 1 | 0 | 1 | 0 | Reach |

- **IFBench, strict (headline 218):**
  - 94 reach candidates and 8 reverse.
  - **49** prompts where `s2300` is confirmed and `dpo` has 0 strict successes in 256 (matches the deviations' 49).
  - 33 resolved for `dpo`.
  - 12 open: in each, `dpo` has exactly one success in 256 and `s2300` is confirmed.
  - The 39 reach candidates among the 82 excluded prompts were never extended (`open_dpo_incomplete` in the all-300
    row).
  - `rlview` equals `strict` on every IFBench row.
- **IFEval:** 8 reach candidates; 6 reach, 1 resolved (`ifeval_3326`), 1 open (`ifeval_2447`, one `dpo` success).
  One reverse, `ifeval_2785`: `s2300` 0/256, `dpo` 19/48 with 15 fresh.
- **OMEGA `test_out`:**
  - Under `omega`: 14 R, 1 V. Reach: 055, 068, 069. Open with one `dpo` success: 011, 073. Resolved: 9.
  - Under `rl`: 11 R. 069 is resolved there by two `rl`-only `dpo` credits (draws 69 and 237), and 073 by three.
  - Reverse: `arithmetic_list_prime_factors_045`, resolved for `s2300` (4/56).
  - Every `omega` credit is also an `rl` credit, so `doubly` = `omega` everywhere.

**Extension audit** (`rv_ext.py`, `out/ext.txt`; 204 extended cells):
- No cell exceeds 256 draws.
- Defender jobs E1 run chunks of 48 with one chunk in flight. Every E1 cell stops at the chunk in which its count
  reaches 2, or at 256.
- The 21 cells with draws after the count reached 2 are of two kinds:
  - hand-gate continuations (E2/E3, C2/C3: `ifbench_47/125/137/180/158/166/214/266/80/88`,
    `func_intersection_coords_011`, `geometry_basic_010`);
  - chunks of 16 already in flight in the inflight-2/3 confirmation jobs (`C1_dpo_rev`, `C1_s2300_oo{,2}`,
    `C1_dpo_ifevrev`).
- `geometry_perpendicular_intersection_068`'s extension was split across `E1_dpo_oo3` (48, then a budget stop) and
  `E1_dpo_oo4` (192). It totals 256.

### R6. OMEGA labels, computed independently (`rv_labels.py`, `out/labels.txt`)

I computed every candidate problem's answer myself:

| problem | method | result |
|---|---|---|
| 9 perpendicular-diagonal problems | regular n-gon; chords (a,b) ⟂ (c,d) iff a+b−c−d ≡ n/2 (mod n), checked numerically | all agree with their labels except `055` |
| 3 combinatory probabilities | exact enumeration | agree (1/120 → 121, 1/9 → 10, 9/14 → 23) |
| `numbertheory_lte_qr_023` | direct count | N = 4, M = 22,629 → 22,633 |
| `arithmetic_list_prime_factors_045` | factorisation | 281 · 487 · 5,393 → 487 |
| `algebra_func_intersection_coords_011` | root search | first intersection x = 1.468 → 1; the second, 1.712, rounds to 2 |
| `geometry_basic_010` | construction | FE = 13.154925 → 13.15, 0.000075 below the rounding boundary |

**`geometry_perpendicular_intersection_055` is mislabelled, as the run found.** The official 17 counts every
perpendicular pair of the drawn diagonals. Only 15 meet "within the polygon's interior or on its boundary"; two pairs
meet outside. In every other perpendicular-diagonal candidate, all perpendicular pairs meet inside, so the labels are
consistent there.

With the label corrected to 15:

| model | draws | `omega` credits | `rl` credits | cut at the cap |
|---|---|---|---|---|
| `s2300` | 40 | 16 | 20 | 14 |
| `dpo` | 256 | 0 | 0 | **255** |
| `s0750` | 8 | 0 | 1 (`rl` only) | 6 |

`s2300`'s label-15 credits all come from confirmation draws. Under label 17 it has 2 of 40. So under the correct
label 055 is no candidate under `omega` (no RL checkpoint credited in the fixed phase), and a candidate under `rl` only
through `s0750`'s one credit. `dpo` essentially never finishes on this problem within 32,768 tokens.

### R7. Hand check, blind (`rv_hand_items.py`, `rv_hand.py`, `rv_hand_tables.py`; `hand/`)

**Design.**
- **Rubrics:** `hand/reader_prompt_if.md` and `hand/reader_prompt_omega.md`. I wrote them from the pre-registration's
  definitions before opening any executor hand-check file. IF: genuine / gamed / unsure. OMEGA: sound / flawed /
  guess / unsure, plus the reader's own check of the official label.
- **Readers:** blinded sub-agents. An IF reader saw the prompt, the constraint ids with kwargs, and the final answer
  only. An OMEGA reader saw the problem, the official answer and the full response. No reader saw the model, the
  phase, the side, or why an item was chosen. OMEGA readers verified the decisive steps in Python.
- **Items** are the deciding successes, chosen from *my* candidate sets in draw order within 256:
  - **Round 1** is the pre-registered gate. The defender's first two successes (its only one if it has one). The
    challenger's first fixed-phase success and first two fresh ones, where the defender has fewer than 2 checker
    successes. Both sides on reverse candidates.
  - **Rounds 2–4** read further successes of whichever side was short of its status: up to 4 more for a defender,
    up to 6 for a challenger, fresh first.
- **Challenger stopping rule** (mine, fixed at 08:15 UTC before reading any executor hand file): after ≥ 9 reads,
  ≥ 6 of them fresh, with ≤ 1 genuine, the prompt stays open.
- **OMEGA "success"** is a response credited by `omega` or `rl` (union), with the doubly-credited view beside it.
- **Unsure** maps both ways: `strict` (= not good) and `lenient` (= good).
- **Controls:** 10 duplicate items in other batches, 8 swapped-prompt items (a real success shown under another prompt
  with the same constraint ids and kwargs, re-checked to pass the checker; its main request is not done), and my own
  blind reads.
- **My overrides** (`hand/confirm.json`), each with its reason:
  - `ifeval_2447`'s only `dpo` success: gamed. A rubric poem written entirely in Chinese, which meets "the letter w
    fewer than 2 times" without attempting the lipogram. Borderline.
  - A split duplicate pair on `ifeval_1130`: gamed. Three fragment yes/no trivia questions offered as a "logic quiz".
    Borderline.
  - Five `ifbench_284` items the readers called unsure: genuine. Its only constraint, `repeat:repeat_span`, is checked
    by *equality* with the span, so the bare span is the only possible way to satisfy it; the readers called the other
    equality-checked repeat prompts genuine. This rule was written after I saw these items.

Items read: 586 (r1 370, r2 176, r3 31, r4 6, r5 3); real 568, duplicates 10, swapped-prompt controls 8; labelled 586; reviewer overrides 8.
Controls: duplicate pairs agree 9/10; swapped-prompt controls labelled gamed 8/8.
My own blind reads of a seeded sample of 10 round-1 IF items (5 the readers called genuine, 5 gamed): 10/10 agree.

| task | model | side | items | genuine / sound | gamed | flawed | guess | unsure | not good |
|---|---|---|---|---|---|---|---|---|---|
| ifbench | dpo | challenger | 15 | 12 | 3 | 0 | 0 | 0 | 0.20 |
| ifbench | dpo | defender | 93 | 72 | 21 | 0 | 0 | 0 | 0.23 |
| ifbench | s2300 | challenger | 340 | 198 | 138 | 0 | 0 | 4 | 0.42 |
| ifbench | s2300 | defender | 14 | 12 | 2 | 0 | 0 | 0 | 0.14 |
| ifeval | dpo | challenger | 3 | 3 | 0 | 0 | 0 | 0 | 0.00 |
| ifeval | dpo | defender | 3 | 2 | 1 | 0 | 0 | 0 | 0.33 |
| ifeval | s2300 | challenger | 27 | 24 | 3 | 0 | 0 | 0 | 0.11 |
| omega_out | dpo | challenger | 1 | 0 | 0 | 1 | 0 | 0 | 1.00 |
| omega_out | dpo | defender | 47 | 33 | 0 | 12 | 2 | 0 | 0.30 |
| omega_out | s2300 | challenger | 21 | 16 | 0 | 5 | 0 | 0 | 0.24 |
| omega_out | s2300 | defender | 4 | 2 | 0 | 2 | 0 | 0 | 0.50 |

| task | OMEGA success | unsure → | hand reach | dpo resolved | open (reasons) | reverse | s2300 resolved | V open | hand verdict |
|---|---|---|---|---|---|---|---|---|---|
| ifbench|headline | – | strict | 43 | 31 | 20 (other 2, challenger_unextended 2, dpo_one_good 8, gamed_dominated 8) | 2 | 5 | 1 | Reach |
| ifeval|headline | – | strict | 7 | 1 | 0 () | 1 | 0 | 0 | Reach |
| omega_out|headline | union | strict | 1 | 10 | 3 (other 1, challenger_unextended 1, dpo_one_good 1) | 0 | 1 | 0 | Inconclusive |
| ifbench|headline | – | lenient | 43 | 31 | 20 (other 2, challenger_unextended 2, dpo_one_good 8, gamed_dominated 8) | 2 | 5 | 1 | Reach |
| ifeval|headline | – | lenient | 7 | 1 | 0 () | 1 | 0 | 0 | Reach |
| omega_out|headline | union | lenient | 1 | 10 | 3 (other 1, challenger_unextended 1, dpo_one_good 1) | 0 | 1 | 0 | Inconclusive |
| omega_out|headline | doubly | strict | 2 | 8 | 4 (other 1, challenger_unextended 1, dpo_one_good 2) | 0 | 1 | 0 | Inconclusive |
| omega_out|headline | doubly | lenient | 2 | 8 | 4 (other 1, challenger_unextended 1, dpo_one_good 2) | 0 | 1 | 0 | Inconclusive |

Per prompt, ifeval|headline (strict mapping; OMEGA under union / doubly):

| prompt | side | status (union) | status (doubly) | dpo credited / read / good | s2300 credited / read / good (fresh) |
|---|---|---|---|---|---|
| `ifeval_1130` | R | reach | – | 0 / 0 / 0 | 24 / 9 / 6 (5) |
| `ifeval_1314` | R | reach | – | 0 / 0 / 0 | 22 / 3 / 3 (2) |
| `ifeval_2247` | R | reach | – | 0 / 0 / 0 | 24 / 3 / 3 (2) |
| `ifeval_2350` | R | reach | – | 0 / 0 / 0 | 24 / 3 / 3 (2) |
| `ifeval_2447` | R | reach | – | 1 / 1 / 0 | 22 / 3 / 3 (2) |
| `ifeval_2563` | R | reach | – | 0 / 0 / 0 | 24 / 3 / 3 (2) |
| `ifeval_2785` | V | reverse | – | 19 / 3 / 3 | 0 / 0 / 0 (0) |
| `ifeval_3326` | R | dpo_resolved | – | 5 / 2 / 2 | 8 / 0 / 0 (0) |
| `ifeval_3478` | R | reach | – | 0 / 0 / 0 | 10 / 3 / 3 (2) |

Per prompt, omega_out|headline (strict mapping; OMEGA under union / doubly):

| prompt | side | status (union) | status (doubly) | dpo credited / read / good | s2300 credited / read / good (fresh) |
|---|---|---|---|---|---|
| `algebra_func_intersection_coords_test_out_011` | R | dpo_resolved | dpo_resolved | 21 / 6 / 4 | 8 / 1 / 1 (0) |
| `arithmetic_list_prime_factors_test_out_045` | V | s2300_resolved | s2300_resolved | 1 / 1 / 0 | 4 / 4 / 2 (2) |
| `combinatory_probability_exactly_n_specific_fixed_test_out_027` | R | dpo_resolved | dpo_resolved | 3 / 2 / 2 | 8 / 0 / 0 (0) |
| `combinatory_probability_exactly_n_specific_fixed_test_out_047` | R | dpo_resolved | dpo_resolved | 7 / 6 / 5 | 8 / 0 / 0 (0) |
| `combinatory_probability_no_specific_letter_fixed_test_out_004` | R | dpo_resolved | dpo_resolved | 5 / 2 / 2 | 8 / 0 / 0 (0) |
| `geometry_basic_test_out_010` | R | open_challenger_unextended | open_challenger_unextended | 9 / 9 / 0 | 0 / 0 / 0 (0) |
| `geometry_perpendicular_intersection_test_out_011` | R | open_dpo_one_good | open_dpo_one_good | 1 / 1 / 1 | 20 / 3 / 3 (2) |
| `geometry_perpendicular_intersection_test_out_033` | R | dpo_resolved | dpo_resolved | 4 / 3 / 3 | 8 / 0 / 0 (0) |
| `geometry_perpendicular_intersection_test_out_055` | R | open | open | 0 / 0 / 0 | 2 / 2 / 0 (0) |
| `geometry_perpendicular_intersection_test_out_057` | R | dpo_resolved | dpo_resolved | 8 / 5 / 5 | 8 / 0 / 0 (0) |
| `geometry_perpendicular_intersection_test_out_068` | R | reach | reach | 0 / 0 / 0 | 33 / 3 / 3 (2) |
| `geometry_perpendicular_intersection_test_out_069` | R | dpo_resolved | reach | 2 / 2 / 2 | 29 / 9 / 6 (6) |
| `geometry_perpendicular_intersection_test_out_073` | R | dpo_resolved | open_dpo_one_good | 3 / 2 / 2 | 19 / 3 / 3 (2) |
| `geometry_perpendicular_intersection_test_out_075` | R | dpo_resolved | dpo_resolved | 4 / 4 / 4 | 7 / 0 / 0 (0) |
| `numbertheory_lte_qr_test_out_023` | R | dpo_resolved | dpo_resolved | 10 / 5 / 3 | 2 / 0 / 0 (0) |

IFBench hand-reach prompts (strict mapping, 43): `ifbench_0`, `ifbench_1`, `ifbench_128`, `ifbench_133`, `ifbench_136`, `ifbench_154`, `ifbench_166`, `ifbench_169`, `ifbench_170`, `ifbench_173`, `ifbench_179`, `ifbench_186`, `ifbench_187`, `ifbench_188`, `ifbench_189`, `ifbench_19`, `ifbench_203`, `ifbench_204`, `ifbench_206`, `ifbench_207`, `ifbench_209`, `ifbench_211`, `ifbench_217`, `ifbench_220`, `ifbench_226`, `ifbench_248`, `ifbench_252`, `ifbench_253`, `ifbench_264`, `ifbench_267`, `ifbench_268`, `ifbench_269`, `ifbench_271`, `ifbench_280`, `ifbench_281`, `ifbench_284`, `ifbench_290`, `ifbench_3`, `ifbench_4`, `ifbench_64`, `ifbench_67`, `ifbench_78`, `ifbench_79`
IFBench open (3): `ifbench_214`, `ifbench_266`, `ifbench_83`
IFBench open_challenger_unextended (2): `ifbench_126`, `ifbench_47`
IFBench open_dpo_one_good (8): `ifbench_13`, `ifbench_155`, `ifbench_222`, `ifbench_225`, `ifbench_250`, `ifbench_287`, `ifbench_89`, `ifbench_92`
IFBench open_gamed_dominated (8): `ifbench_158`, `ifbench_200`, `ifbench_201`, `ifbench_202`, `ifbench_215`, `ifbench_272`, `ifbench_49`, `ifbench_80`

**Findings.**
1. **Gaming is common among `s2300`'s IFBench successes.** In round 1, whose selection is not adaptive, 36–37 % of
   `s2300`'s challenger successes on IFBench reach candidates read as gamed (fixed 21/58, fresh 43/122), against 14 %
   (11/78) of `dpo`'s defender successes. Over all deciding IF successes in round 1, 83 of 311 (27 %) are gamed;
   the pre-registered expectation was ≤ 10 %. Typical gamed answers:
   - an alphabet word-salad ("Able builders craft designs enabling far greater hardware innovation" as the answer to
     how small a Cray-1 replica could be);
   - three-vowel or consonant-cluster text that drops the question;
   - truncation to meet a Japanese-word count;
   - stacked `*- ` markers posing as sub-bullets.
2. **IFBench by hand is still Reach.** Under `strict`, 43 prompts have `s2300` confirmed by ≥ 2 genuine successes
   (≥ 1 fresh) and no genuine `dpo` success in 256; the checker gave 49. 31 are resolved for `dpo`. 20 are open:
   - 8 dominated by gaming under the stopping rule;
   - 8 where `dpo` has exactly one genuine success;
   - 2 where `s2300`'s genuine successes are all fixed-phase and it was never sampled further (`dpo` had two checker
     successes, one gamed);
   - 2 (`ifbench_214`, `266`) where `s2300`'s confirmation stopped short of 256 with ≤ 1 genuine.
   The `lenient` mapping gives the same counts. Reverse: 2 hold by hand, 5 are resolved for `s2300`, and 1 is open.
3. **IFEval by hand is Reach.** 7 of the 8 reach candidates are hand-reach and `ifeval_3326` is resolved for `dpo`.
   `ifeval_1130` became reach after round 4, with 5 of 6 further `s2300` successes genuine. `ifeval_2447` is reach only
   because its single `dpo` success, the Chinese poem, is gamed; under the lenient reading it would be open. The
   reverse candidate `ifeval_2785` holds by hand: `dpo` 3/3 genuine, `s2300` 0 in 256.
4. **OMEGA `test_out` by hand is Inconclusive under both success definitions. No further reading can change that.**
   - **068 is hand-reach** (`dpo` 0 credited in 256; three of `s2300`'s successes sound). That rules out
     "No reach at 256".
   - Under doubly, **069** is hand-reach too: `dpo` has no doubly-credited success, and 6 of 9 `s2300` successes read
     are sound. No other prompt can become hand-reach (each has a sound `dpo` success, an unconfirmable challenger, or
     only flawed challenger successes), so "Reach" (≥ 3) is ruled out. Final counts: union 1 reach / 10 resolved /
     3 open; doubly 2 / 8 / 4. The reverse candidate 045 is resolved for `s2300` by hand (2 sound of 4).
   - **055:** both of `s2300`'s credited answers (17) are flawed. Both readers, blind, judged the official label wrong
     (their own answer 15). That reproduces the label error by a third route, so 055 stays open under the
     pre-registered label.
   - **069 and 073:** `dpo`'s `rl`-only credits read as sound enumerations. Their text after `</think>` holds no
     extractable answer, so `omega` finds nothing; RL's verifier credits the `\boxed{}` inside the reasoning. For
     example, 069's draw 69 stops mid-word in its answer section ("### Slo", then EOS), and draw 237 is cut at the cap
     inside the reasoning. These responses resolve 069 and 073 for `dpo` under union, but not under doubly.
   - **`func_intersection_coords_011`:** resolved for `dpo` under both definitions. Under union, 4 of the 6 read are
     sound, including the fixed-phase `rl`-only draw 12, which places the first crossing at x ≈ 1.468. Under doubly,
     2 of the 4 doubly-credited ones read are sound.
   - **`geometry_basic_010`:** open. **None** of `dpo`'s 9 credited successes is sound (all read: 7 doubly-credited
     and 2 `rl`-only; 8 flawed, 1 guess). FE = 13.154925 sits 0.000075 below the rounding boundary, and every reading
     reaches 13.15 through arithmetic slips or approximations. `s2300` is 0/8, and `s0750`, its only fixed-phase
     solver, was never extended.
5. **Every OMEGA prompt that is reach or open is a perpendicular-diagonal problem on which `dpo` almost never
   finishes.** 99.5 % of `dpo`'s failures on those problems (1,586 / 1,594) are cut at 32,768 tokens
   (`out/partc_mech.txt`). On the other OMEGA candidates the share is 22 %, and on IFBench reach prompts 0.08 %. So any
   OMEGA reach here is reach at RL's token cap.

### R8. Contamination (`rv_contam.py`, `rv_contam_report.py`; `out/contam_report.txt`, `out/contam_mine.csv`)

My own scan of every IF evaluation prompt (and every OMEGA problem against RL):
- word 8-gram containment, lower-cased `[a-z0-9]+` tokens;
- *content* containment over the prompt's 8-grams that occur in fewer than 20 RL prompts, the pre-registered
  definition;
- corpora: all 102,026 `Dolci-Think-RL-32B` prompts, the `prompt` of all 200,000 `Dolci-Think-DPO-32B` rows, and the
  user and system turns of all 2,253,679 `Dolci-Think-SFT-32B` conversations. Each remote file was streamed, scanned and
  deleted, 25 min for SFT.

The executor also scanned SFT assistant turns and DPO responses; I did not.

**Agreement with the executor's per-prompt maxima.** RL: median |difference| 0.000, maximum 0.001 (650 prompts).
DPO and SFT agree except where their extra turns matched.

**The exclusions** (pre-registered rule: content ≥ 0.5, raw ≥ 0.8, or a variant confirmed by reading among matches
≥ 0.3). The executor's 82 IFBench exclusions break down as follows:
- **67** are over the automatic thresholds in my scan: SFT 67, RL 5, DPO 1, overlapping. No IF prompt is over them and
  *not* excluded.
- **14** sit in my 0.3–0.5 band. I read each pair. In all 14 the document holds the IFBench request **verbatim** without
  IFBench's appended constraint, e.g. `ifbench_50` "Please generate a detailed literature review on modern state on
  blockchain usage in Identity Verification"; `ifbench_229`, `244`, `263`, `289` likewise. So all 14 are correct
  exclusions.
- **1** (`ifbench_131`): my user / system-turn scan finds no overlap. I fetched the matched conversation
  (`wildchat-r1-p2-repetition-filter_31099`, `train-00152`). The quoted blurb that IFBench asks the model to shorten
  appears there as an earlier *assistant* turn (an Amazon Kindle description); the request itself does not appear. A
  conservative exclusion, and harmless: excluding prompts only shrinks the headline set.

Non-excluded prompts in my 0.3 band: `ifbench_43`, `291`, `60`, `61` and six IFEval prompts. I read all ten.
- `60`, `61`, `291` and the IFEval six match only constraint boilerplate (content containment ≤ 0.39, and 0 for `60` / `61`). For
  example, RL's "Repeat the request without change … and do not answer the actual request!" against IFBench's
  "Repeat the request, but change the first word …".
- `43` reuses a WildChat user's paraphrase template with a different sentence to paraphrase.

Keeping all ten is right. IFEval has no exclusion, and none is warranted by my scan.

**OMEGA.** `test_out` problems' best RL raw containment: median 0.30, maximum 0.78 (the generator templates). No
`test_out` problem equals an RL prompt or a renamed copy (R2).

**Finding (minor, affects nothing sampled):** `omega_in_logic_gridworld_knight_move_test_in_145` has raw containment
**1.0**. It equals RL prompt `omega-combined-no-boxed_filtered-request-555-77` minus that prompt's last sentence, "(Assume
you cannot move off the grid.)". The pool filter tests whole-text equality, so a superstring passes. `test_in` was cut
before sampling.

### R9. Per-constraint analysis (Design 6; `rv_constraints.py`, `out/constraints.txt`)

RL's IF data: 29,847 prompts with dataset `['ifeval']` and 54 distinct instruction ids (my parse of `ground_truth`), as
stated.

- **IFBench.** No binding constraint (the one the losing model fails most, over its 256 draws) of the 49 strict-reach
  prompts is an RL IF id, as expected by construction. The binding ids:
  - `words:consonants` 7, `words:vowel` 7, `words:alphabet` 5;
  - `count:keywords_multiple` 4, `ratio:sentence_words` 4;
  - `format:sub-bullets` 3, `sentence:increment` 3;
  - 16 others once each.
- **IFEval.** All 6 strict-reach prompts' binding constraints are RL IF ids: `keywords:letter_frequency` 3,
  `change_case:english_capital` 2, `change_case:capital_word_frequency` 1.
- The RL data's "Repeat the request without change … and do not answer the actual request!" is a near relative of
  IFBench's "Repeat the request, but change the first word …" (`ifbench_60` / `61`, raw containment 0.42 / 0.37, all of
  it that boilerplate).

### R10. Stage 0, compute axis and compute record (`out/stage0.txt`, `rv_compute.py`, `out/registry_check.txt`)

**Stage 0** reproduces Part B. `dpo` `test_out`:
- 80/80 finished, mean 22,567 tokens, median 21,967;
- 14/80 = 17.5 % cut, 66/80 close `</think>`;
- `omega` 0.325, `rl` 0.3625; 3 disagreements, all `rl`-only.

Other Part-B figures also match: `dpo` `test_in` 36/80 finished (mean 17,754); `s2300` 6 `test_out`, 8 `test_in`,
6 IFEval and 2 RL-IF finished (means 9,513 / 6,167 / 1,272 / 1,982); `strict` = `rlview` on all IF rows.

**Compute axis.** The pre-registered inputs, my arithmetic: PT = 6ND = 1.094e24 FLOPs, 976,896 GPU-h.

The middle estimate uses RL's prompt mix (30.2k maths, 29.8k IF, 42.0k other, my count from the RL parquet) at my
measured fixed-phase means: OMEGA `test_out`, IFBench, and their mean for the rest. That gives L = 14,590 / 14,378 /
13,872 / 13,708 tokens (`dpo` / `s0100` / `s0750` / `s2300`), with `s0100`'s maths length interpolated.

| step | FLOPs ratio low | middle | high | GPU-h | GPU-h ratio |
|---|---|---|---|---|---|
| 100 | 1.20e-4 | 3.47e-4 | 9.81e-4 | 3,584 | 0.0037 |
| 750 | 8.98e-4 | 2.55e-3 | 7.36e-3 | 26,880 | 0.0275 |
| 2,300 | 2.76e-3 | 7.67e-3 | 2.26e-2 | 139,776 | 0.1431 |

**Compute record.** The registry has 280 rows: 7 metrics for 39 jobs, plus one more set for the earlier `F_s0750_oo`
segment from `compute_extra.csv`. Tokens and attempts equal my row counts for 33 of the 39 jobs. The six exceptions are listed here. The F_s0750_oo
segment closes `F_s0750_oo` exactly (732 + 68 = 800 samples, 16,327,507 + 1,296,569 = 17,624,076 tokens). The two
Stage-0 rows are discussed below.

**Finding (minor):** three resumed jobs are recorded with their last segment only:

| job | samples recorded / stored | tokens recorded / stored | GPU-seconds missing (at the job's rate) |
|---|---|---|---|
| `E1_dpo_oo3` | 384 / 624 | 12.58 M / 20.25 M | ≈ 8,100 |
| `F_dpo_ifb` | 4,008 / 4,800 | 17.89 M / 21.08 M | ≈ 1,700 |
| `F_s2300_ifb` | 2,356 / 2,400 | 15.52 M / 15.57 M | small |

In all, 1,076 samples, 10.9 M tokens (3.0 % of the 358.1 M generated) and ≈ 9,900 GPU-seconds are unrecorded. The
Stage-0 rows count tokens generated by sequences that were stopped unfinished (3.23 M and 1.72 M), not the stored
finished samples (2.47 M and 0.12 M). That is the right count of compute, but the registry should say so.

### R11. Pre-registered expectations against the recount (`rv_expect.py`, `out/expect.md`)

| quantity | pre-registered | recount | |
|---|---|---|---|
| IFBench dpo pass@1 | 0.30 (0.20–0.40) | 0.290 | within |
| IFBench dpo pass@8 | 0.62 (0.50–0.75) | 0.461 | below |
| IFBench s0100 pass@1 / @8 | 0.32 / 0.64 | 0.315 | no interval stated |
| IFBench s0750 pass@1 | 0.44 (0.32–0.56) | 0.512 | within |
| IFBench s0750 pass@8 | 0.76 | 0.794 | no interval stated |
| IFBench s2300 pass@1 | 0.60 (0.45–0.72) | 0.683 | within |
| IFBench s2300 pass@8 | 0.86 (0.75–0.93) | 0.885 | within |
| IFBench \|R\| | 30 (12–55) | 94 | above |
| IFBench \|V\| | 5 (1–15) | 8 | within |
| IFBench dpo resolves (≥ 2 strict in 256), share of R | 50 % (25–75 %) | 0.351 | within |
| IFBench s2300 confirmed (strict) on the rest | 90 % | 1.000 | no interval stated |
| IFBench expected entries @8 (s2300 vs dpo) | 55 (35–75) | 98.270 | above |
| IFBench expected exits @8 | 5 (1–12) | 5.860 | within |
| test_out dpo pass@1 (omega) | 0.32 (0.20–0.45) | 0.274 | within |
| test_out dpo pass@8 | 0.62 (0.45–0.78) | 0.521 | within |
| test_out s2300 pass@1 | 0.40 (0.25–0.55) | 0.624 | above |
| test_out s2300 pass@8 | 0.66 (0.50–0.80) | 0.730 | within |
| test_out s0750 pass@1 (addendum) | 0.36 (0.22–0.52) | 0.550 | above |
| test_out s0750 pass@8 (addendum) | 0.64 | 0.710 | no interval stated |
| test_out \|R\| (omega) | 8 (3–15) | 14 | within |
| test_out \|V\| (omega) | 5 (1–10) | 1 | within |
| test_out expected entries @8 | 6 (2–12) | 21.370 | above |
| test_out expected exits @8 | 3 (1–7) | 0.500 | below |
| test_out dpo resolves, share of extended R (omega) | 50 % (20–80 %) | 0.643 | within |
| test_out \|omega − rl\| pass@1, dpo | ≤ 0.04 | 0.028 | within |
| test_out \|omega − rl\| pass@1, s0750 | ≤ 0.04 | 0.016 | within |
| test_out \|omega − rl\| pass@1, s2300 | ≤ 0.04 | 0.009 | within |
| IFEval dpo pass@1 (addendum) | 0.78 (0.70–0.86) | 0.768 | within |
| IFEval s0750 pass@1 | 0.84 | 0.884 | no interval stated |
| IFEval s2300 pass@1 | 0.88 (0.80–0.94) | 0.935 | within |
| IFEval \|R\| | 4 (1–10) | 8 | within |
| IFEval \|V\| | 2 (0–5) | 1 | within |
| IFEval dpo resolves, share of R | 75 % | 0.125 | no interval stated |
| IFBench dpo mean tokens | 1.5–4k | 4391 | above |
| IFBench s0100 mean tokens / dpo | within ±40 % | 0.985 | within |
| IFBench s0750 mean tokens / dpo | within ±40 % | 1.287 | within |
| IFBench s2300 mean tokens / dpo | within ±40 % | 1.477 | above |
| IFEval dpo mean tokens | 1.5–4k | 2508 | within |
| IFEval s0750 mean tokens / dpo | within ±40 % | 1.312 | within |
| IFEval s2300 mean tokens / dpo | within ±40 % | 1.809 | above |
| test_out dpo mean tokens | 18–26k | 24709 | within |
| test_out dpo cut share | 10–25 % | 0.217 | within |
| test_out s0750 mean tokens | 18–26k | 22030 | within |
| test_out s0750 cut share | 10–25 % | 0.115 | within |
| test_out s2300 mean tokens | 18–26k | 20873 | within |
| test_out s2300 cut share | 10–25 % | 0.051 | below |
| hand: IF deciding strict successes gamed | ≤ 10 % | 0.267 (83 / 311, round 1) | above |
| hand: OMEGA doubly-credited deciding successes sound | ≥ 70 % | 0.724 (21 / 29, round 1; 40 / 60 over all rounds) | within (round 1) |
| hand: `dpo` resolves by hand vs strict (IFBench) | "one or two fewer" | 31 vs 33 | as expected |

Misses outside the stated intervals:
- IFBench `dpo` pass@8 (0.461, below 0.50–0.75);
- IFBench |R| (94 vs 30, 12–55);
- IFBench expected entries @8 (98.3 vs 55, 35–75);
- `test_out` `s2300` pass@1 (0.624 vs 0.40, 0.25–0.55) and `s0750` pass@1 (0.550 vs 0.36, 0.22–0.52);
- `test_out` expected entries (21.4 vs 6, 2–12) and exits (0.5 vs 3, 1–7);
- IFEval `dpo` resolving 1 of 8 (vs 75 %);
- lengths: IFBench `dpo` 4,391 (vs 1.5–4k), `s2300` 1.48× and IFEval `s2300` 1.81× `dpo` (vs ± 40 %), `test_out`
  `s2300` cut 5.1 % (vs 10–25 %).
- the hand check: 27 % of IF deciding successes gamed (vs ≤ 10 %).


### R12. Phase-1 summary

Verdicts by the pre-registered rule, from my recount:

| task | grade | \|R\| | reach / dpo resolved / open | verdict (my recount) |
|---|---|---|---|---|
| ifbench | strict | 94 | 49 / 33 / 12 | **Reach** |
| ifbench | hand |  | 43 / 31 / 20 | **Reach** |
| ifeval | strict | 8 | 6 / 1 / 1 | **Reach** |
| ifeval | hand |  | 7 / 1 / 0 | **Reach** |
| omega_out | omega | 14 | 3 / 9 / 2 | **Reach** |
| omega_out | rl | 11 | 2 / 8 / 1 | **Inconclusive** |
| omega_out | hand (union) |  | 1 / 10 / 3 | **Inconclusive** |
| omega_out | hand (doubly) |  | 2 / 8 / 4 | **Inconclusive** |

The automatic `omega` "Reach" rests on exactly three prompts, 055, 068 and 069. 055's label is wrong (R6); with it
corrected to 15, 055 is no `omega` candidate, two reach prompts remain, and 011 and 073 are open, so `omega` becomes
**Inconclusive** like `rl`.

All counts are on the headline sets: IFBench 218, IFEval 150, OMEGA `test_out` 100. Hand rows use the `strict`
mapping of unsure; the `lenient` mapping gives the same verdicts and counts except where R7 says otherwise.

Other findings, all minor:
- `ifeval_1122`'s grade is a random draw (R3).
- The compute record misses three resumed segments: 1,076 samples and 10.9 M tokens (R10).
- The OMEGA pool filter misses superstring RL prompts. One `test_in` problem is affected, never sampled (R8).

Confirmed:
- every pinned input, seeded draw, template, decoding setting and stored text (R2);
- the official graders, reproduced row by row (R3);
- the candidate sets and the extension discipline (R5);
- the 055 label error, by three routes (R6, R7);
- the 82 contamination exclusions (R8).
