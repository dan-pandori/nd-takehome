# Review: olmo-rlzero-if (reviewer session, 2026-11-08)

Run `olmo-rlzero-if` (brief: nd-rl `docs/proposals/followups/BRIEF_olmo-rlzero-if.md`, proposal 39). Models, as the
run labels them, used throughout. All are 7.3 B, bf16, natural-language text; none was trained in this run.
- `base` = `allenai/Olmo-3-1025-7B` @ `main` (`a81bae42`), the pretrained base, prompted with RL-Zero-IF's
  `olmo_thinker` template and **RL-Zero-IF's tokenizer** (the run's design);
- `base_btok` = the same weights with the base repository's own tokenizer (the run's diagnostic, not in any verdict);
- `s0100` / `s0500` / `main` = `allenai/Olmo-3-7B-RL-Zero-IF` @ `step_100` / `step_500` / `main` (`fcc5f4aa` /
  `faf7f48e` / `3cae007c`): RLVR straight from the base on `Dolci-RL-Zero-IF-7B`, no SFT or DPO;
- `math` = `allenai/Olmo-3-7B-RL-Zero-Math` @ `main` (`dee26a40`), RLVR from the base on math (optional arm).

Prompts: IFBench test, all 300 (headline 297 after 3 contamination exclusions; the 218 of `olmo-ifomega` beside it), and
`olmo-ifomega`'s seeded 150 IFEval prompts. Judges: the official IFBench / IFEval checkers on RL's own answer
extraction, and a blind hand gate. There are no proofs, so Lean does not apply. In place of the brief's Lean re-check I:
- re-graded every stored text with the upstream checkers, from my own fetches at the pinned commits;
- repeated the hand gate blind on the deciding responses;
- checked the template, decoding and tokenizer parity, and the contamination scan, from my own downloads.

Kit: `review/olmo-rlzero-if-recount/` (code I wrote; every number below is in its `out/` or `hand/`). Scratch
(upstream fetches, item texts, the pre-release dataset's prompts) is in `~/review/rzi_rv/` and is not committed.

## §Recount (phase 1: written before reading `run_olmo_rlzero_if.md`, `numbers.md`, `log.md` or `STATUS.md`)

### R0. What I read, and how blind this is

**Read:**
- the run brief;
- `preregistration/olmo-rlzero-if.md`: Part A, Part B and the as-run deviations 1–13;
- the code: `olmo_rlzero_if/*.py`, `olmo_ifomega/vendor/`, `olmo_pilot/compute_axis.py`, `pod/olmo_rlzero_if/*.sh`;
- the rubric files `olmo_ifomega/handcheck_rule_if.md`, `olmo_rlzero_if/handcheck_rule_if_addendum.md` (rules 6–7),
  `handcheck_prompt_if.md` and `failure_rubric_if.md`;
- `olmo_rlzero_if/README.md` (a file index; no numbers) and `jobs.csv`;
- the raw artefacts:
  - 27 sample files (143,176 texts with token ids);
  - the executor's per-sample grade rows (`graded/`, for the row-by-row comparison only);
  - job meta, pod env / tokenizer hashes, `meta/weight_dist.jsonl`;
  - the plan files `E2_base_ife.prior` / `.stop`, `E4_base.prior`, `C1_base_rev.prior` and the job pid lists.

**Not read:**
- `run_olmo_rlzero_if.md`, `numbers.md`, `log.md`, `STATUS*`, the plain summary;
- the derived tables (`results.csv`, `passk.csv`, `dynamics.csv`, `candidates*.csv`, `verdict.csv`, `hand_summary.csv`,
  `gate_status*.csv`, `failures_if.csv`, `compute_axis.csv`, `lengths_axis.csv`, `weight_dist.csv`,
  `contamination.csv`, `exclusions.csv`, `manifest.csv`);
- every hand-check file of the executor (`handcheck.csv`, `artifacts/olmo_rlzero_if/hand/`, `fail*/`);
- the plan files `tier1.txt`, `reach_hand_a.txt`, `base_read_pids.txt`, `tier2_*`.

**Limits on blindness (leaks I saw before or during phase 1):**
1. The session start showed the DONE commit subject: "tier 2 to 20 per task: strict Reach on both tasks; hand IFBench
   Reach, IFEval inconclusive". It also showed "intermediate reads on the remaining reach prompts".
2. The pre-registration's deviations state some outcomes:
   - the strict IFEval verdict "moved from inconclusive (2 reach prompts) to Reach (5)";
   - the base-tokenizer diagnostic ran "on all six hand-reach prompts (plus ifbench_296)";
   - the math arm ran on "each IFBench hand-reach prompt";
   - rule 7 overturned 12 labels.
3. Two memory notes on this VPS, written by the executor during this run, state results:
   - with RL's tokenizer the base closed its reasoning in 46 of 7,200 samples;
   - with its own tokenizer the base answered genuinely on 3 of 6 "reach" prompts;
   - RL-Zero-IF gives ≈ 40-token answers by step 100, and 94 % of its strict successes are gamed.
4. `jobs.csv` notes and the diagnostic jobs' pid lists name prompts:
   - `D_base_btok` = ifbench_100/102/103/104; `D_base_btok_b` = ifbench_274, ifbench_296, ifeval_3272;
   - "ifbench_274 and 296, main hand-confirmed";
   - "ifeval_3272: E2 stopped at 2 strict successes, both gamed".

I re-derived all of these myself. My readers saw none of them, and my rubric was written from the pre-registered rules
alone.

### R1. Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72…` at HEAD = `origin/main`; the workspace copy is identical |
| `nd_verify` unused as a judge | no `olmo_rlzero_if/` or `pod/olmo_rlzero_if/` file names it |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064…` = `origin/main`'s |
| evaluation data in training code | the run trains nothing |
| Lean | not applicable (no proofs); the judges are the pre-registered official checkers |

No hard-constraint violation.

### R2. Prompts, models, template, decoding, tokenizer, storage

**Prompts** (`rv_provenance.py`, `out/provenance.txt`):
- All 300 IFBench prompts equal the IFBench repo's `IFBench_test.jsonl` @ `cd189a9c` and the HF parquet
  `allenai/IFBench_test` @ `ed7c1245` on prompt, instruction list and kwargs. 256 have one constraint, 44 have two.
- The 150 IFEval and 40 Stage-0 IFEval prompts are exactly `olmo-ifomega`'s seeded draw (`sha256("20261104|ifeval")`
  seed). All 190 equal `google/IFEval` @ `966cd895`.
- All 450 rows equal `olmo_ifomega/problems.jsonl`; the 82 `ifomega_excl` flags equal its exclusion list.
- The 24 Stage-0 RL prompts are Dolci prompts (raw containment 1.0); Stage-0 and evaluation prompts are disjoint.

**Models** (my Hub reads, `rv_hub.py`):
- The five commits match the pre-registration.
- `main`'s three shards match the LFS sha256 of no `step_*` branch, as stated; its index metadata differs from
  `step_1900`'s.
- Base `main` = `stage3-step11921`: identical shard sha256.
- `config.json`, tokenizer files and `chat_template.jinja` are identical on all 20 RL-Zero-IF branches.

**Template and decoding parity.**
- The sampler's `TEMPLATE` equals `CHAT_TEMPLATES["olmo_thinker"]` @ `d928a7c`, byte for byte (my AST extraction):
  1,652 bytes, sha256 `6d549883…`. It also equals RL-Zero-IF's shipped `chat_template.jinja`.
- open-instruct's README @ `e25a27b8` says the IF run used `olmo_thinker` at `d928a7c`. It also says the
  launch-script snapshot (`7e780f2fea`) is a provenance reference, not proof of every setting.
- Settings from that snapshot: `--temperature 1.0`, `--response_length 16384`, `--stop_strings "</answer>"`.
- `grpo_fast.py` @ `d928a7c`: `vllm_top_p` 1.0; `include_stop_str_in_output=True`; `skip_special_tokens=False`; the
  reward text decoded with `skip_special_tokens=True`.
- No BOS: open-instruct asserts no `--add_bos` for `olmo` templates.
- All 26 job meta records report T 1.0, top-p 1.0, 16,384 max tokens, stop `</answer>`, vLLM 0.11.0, torch 2.8.0 and
  that template sha. Speculation was used only in Stage 0 (`spec_ngram` 4 in `s0_base_b` and `s0_main`).
- All seven pods' tokenizer hashes equal RL-Zero-IF `main`'s `tokenizer.json` (`a8c8767b…`) and its config. The two
  `D_base_btok*` jobs load the base repository's tokenizer.
- Every RL-Zero-IF answer is graded by RL's own extraction, `remove_thinking_section` @ `d928a7c`, which I executed
  from my own fetch of the file.

**Tokenizers.** RL-Zero-IF's tokenizer differs from the base's only in the names of 11 added tokens (ids 100256,
100266–100275: `<|system|>`, `<|user|>`, `<|assistant|>`, `<think>`, `</think>`, `<functions>`, …,
`<answer>`, `</answer>`). The vocab entries for those ids and `tokenizer_config`'s `bos_token` and
`model_max_length` also differ. The tokens are `special: false`, so decoding with `skip_special_tokens=True` keeps them.

**Storage** (`rv_regrade.py`, `out/decode_check.txt`):
- Over 143,176 stored samples, `text == decode(ids, skip_special_tokens=True)` with the tokenizer each job used,
  except one row the executor redacted (an `hf_`-like string the base generated, replaced and its ids dropped).
- `n_tok == len(ids)`; every `length` row (582) has exactly 16,384 tokens; every `stop` row ends in EOS or at
  `</answer>` (14 rows).
- 51,601,546 generated tokens in all.
- **No response contains token 100269 (`</think>`) or 100268 (`<think>`).** 379 responses contain the text
  `</think>`, spelled from ordinary pieces, 256 of them in `D_base_btok*`.
- No response contains `<|im_start|>` / `<|im_end|>`, so the pre-registered `t1` grade equals `strict` everywhere.

### R3. Contamination (`rv_contam.py`, `rv_contam_pre.py`, `out/contam_*.txt`)

- **Against Dolci-RL-Zero-IF-7B @ `c96e4e42`** (13,179 prompts; my download's sha256 equals the LFS oid), with word
  8-grams, raw and content containment (content grams in < 20 RL prompts):
  - exactly ifbench_196 / 228 / 285 meet the rule (content 0.509 / 0.787 / 0.514), all against
    `tulu_v3.9_wildchat_100k_29059`;
  - every other match ≥ 0.3 is constraint boilerplate ("First repeat the request…", "P.P.S"). That includes
    ifeval_2337 (raw 0.53, content 0.07), which is not in the pre-registration's read-and-kept list.
  - The exclusions reproduce.
- **Against the dataset the launch snapshot names**, `saurabh5/IF_multi_constraints_upto5_filtered_olmo_completions_filtered`
  @ `3a5ace2c` (88,556 rows; I read only its `key` and `messages` columns over HTTP):
  - all 13,179 Dolci prompts are in it;
  - one more eval prompt has a near-duplicate there: ifbench_238 (content 0.606, row `…wildchat_100k_98357`);
  - open-instruct `d928a7c`'s `select_samples(13314)` with its default `dataset_config_seed` 42 picks a set that
    contains all 13,179 Dolci keys and does not contain that row.
  - So Dolci is RL's sample (minus 135 rows), and ifbench_238 was not trained on. Scanning Dolci was the right
    reference.
- None of the six hand-reach prompts (R7) has a match above 0.14 raw. 218 Dolci prompts carry an "Answer with one of
  the following options" constraint, IFEval's form with other option strings. The IFBench option sets
  (yes/no/maybe, a)–d), "I know or I don't know") occur in none.

### R4. Re-grade (`rv_graders.py`, `rv_regrade.py`, `rv_gradecmp.py`, `out/gradecmp.txt`)

- My vendored-checker check: the executor's `olmo_ifomega/vendor/` files are byte-identical to my fetches of IFBench
  `cd189a9c` and google-research `e6890f85`.
- My grades (strict, loose, per-constraint, `</think>`, `t1`) agree with the executor's on **all 142,928** IFBench /
  IFEval rows: 0 disagreements. That is with `random` re-seeded before every check, as pre-registered; one IFEval prompt
  (ifeval_1122) draws a random letter.

### R5. Fixed phase (`rv_cells.py`, `rv_stats.py`; T1–T2 generated from `out/stats.json`)

**T1. Fixed-phase pass@k, strict; prompt-bootstrap 95 % (10,000)**

| prompt set | model | pass@1 | pass@8 | pass@16 | loose pass@1 |
|---|---|---|---|---|---|
| ifbench_h297 | base | 0.129 [0.103, 0.156] | 0.334 [0.287, 0.382] | 0.421 [0.364, 0.478] | 0.169 |
| ifbench_h297 | s0100 | 0.477 [0.428, 0.527] | 0.650 [0.596, 0.704] | — | 0.513 |
| ifbench_h297 | s0500 | 0.410 [0.364, 0.456] | 0.643 [0.586, 0.697] | — | 0.464 |
| ifbench_h297 | main | 0.469 [0.416, 0.521] | 0.576 [0.522, 0.633] | — | 0.528 |
| ifbench_all300 | base | 0.127 [0.102, 0.155] | 0.331 [0.285, 0.378] | 0.417 [0.360, 0.473] | 0.168 |
| ifbench_all300 | main | 0.467 [0.415, 0.519] | 0.573 [0.517, 0.630] | — | 0.525 |
| ifbench_s218 | base | 0.122 [0.094, 0.154] | 0.322 [0.268, 0.377] | 0.408 [0.344, 0.477] | 0.159 |
| ifbench_s218 | main | 0.448 [0.388, 0.509] | 0.555 [0.491, 0.619] | — | 0.511 |
| ifeval_all150 | base | 0.200 [0.160, 0.242] | 0.496 [0.425, 0.567] | 0.587 [0.507, 0.667] | 0.219 |
| ifeval_all150 | s0100 | 0.806 [0.748, 0.860] | 0.880 [0.827, 0.927] | — | 0.822 |
| ifeval_all150 | s0500 | 0.782 [0.728, 0.834] | 0.927 [0.880, 0.967] | — | 0.811 |
| ifeval_all150 | main | 0.817 [0.757, 0.872] | 0.860 [0.800, 0.913] | — | 0.842 |

(`s0100` / `s0500` on all300 / s218 are in `out/tables.md`.) Between `s0500` and `main`, IFBench pass@8 falls from
0.643 to 0.576 and IFEval pass@8 from 0.927 to 0.860. RL narrows the answers.

**T2. Fixed-phase lengths (tokens)**

| task | model | samples | mean | median | cut at 16,384 | `</think>` in text |
|---|---|---|---|---|---|---|
| ifbench | base | 4800 | 2510 | 854 | 146 (3.0%) | 27 |
| ifbench | s0100 | 2400 | 36 | 16 | 0 (0.0%) | 0 |
| ifbench | s0500 | 2400 | 162 | 30 | 5 (0.2%) | 0 |
| ifbench | main | 2400 | 29 | 12 | 0 (0.0%) | 0 |
| ifeval | base | 2400 | 2194 | 697 | 65 (2.7%) | 19 |
| ifeval | s0100 | 1200 | 98 | 28 | 1 (0.1%) | 0 |
| ifeval | s0500 | 1200 | 142 | 42 | 1 (0.1%) | 0 |
| ifeval | main | 1200 | 49 | 20 | 0 (0.0%) | 0 |

- The base closes its reasoning (as text) in 46 of 7,200 fixed-phase samples (0.6 %). Every RL checkpoint does so in
  none.
- `s0100` already answers in 16 tokens (median) on IFBench.
- The base's cut share of 3.0 % / 2.7 % exceeds the policy's ≈ 0.1 % guideline. This matters little here, because the
  base never closes its reasoning: a cut response's whole text is graded.

### R6. Candidates, extensions and strict fates (T3; `out/stats.txt`, `out/ext.txt`)

**T3. Candidates and strict fates at 256 (non-excluded)**

| task | R | V | R (loose) | V (loose) | REACH | resolved | base 1 success at 256 | dissolved | open | strict verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ifbench | 109 | 38 | 72 | 33 | 9 | 11 | 5 | 7 | 76 | **Reach** |
| ifeval | 56 | 14 | 43 | 13 | 5 | 20 | 4 | 1 | 26 | **Reach** |

- **R and V.** R = base 0/16 and some RL checkpoint ≥ 1/8; V = base ≥ 1/16 and `main` 0/8. One of the 109 IFBench R
  is excluded, leaving 108.
  - R by checkpoint: `s0100` 98, `s0500` 90, `main` 85 (IFBench); 51 / 54 / 55 (IFEval).
- **Strict reach prompts.** `main` has ≥ 2 strict successes, ≥ 1 fresh, within 256; the base has 0 strict in 256.
  - IFBench: ifbench_67, 97, 100, 102, 103, 104, 241, 247, 274.
  - IFEval: ifeval_1512, 2247, 2857, 2880, 3619. Three of these five come from the tier-2 resumption (`E4_base`), as
    deviation 7 says.
- **Draws.** `main` was drawn to exactly 256 on every candidate (8 fixed + 248 in `C1_main`). The base reached 256 on
  18 IFBench and 13 IFEval candidates. 82 IFBench candidates stayed at the fixed 16; every IFEval candidate got ≥ 32
  extension draws.
- **Extension audit.** Every sequential job (`E1`, `E2_ifb`, `E2_ife`, `E4`, `C1_base_rev`) follows the
  stop-at-2-strict rule, with at most two chunks after the deciding one (2 in flight).
  - Every stop below 2 strict is in `E2_base_ife`'s stop file (35 budget stops).
  - No model × prompt cell exceeds 256 draws outside the diagnostics.
  - The IFBench tier-2 sets are exactly positions 1–10 (E2) and 11–20 (E4) of the sha256("20261108:" + pid) order of
    the non-tier-1 candidates.
  - IFEval's kept set is positions 1–10, plus ifeval_219 extended outside the order (presumably tier 1).
  - `E4`'s IFEval prompts are positions 11–20 minus the two (2350, 3324) that E2 had already resolved.
- **Reverse (strict).** The base is confirmed (≥ 2 strict, ≥ 1 fresh) and `main` has 0 in 256 on:
  - IFBench 5: ifbench_127, 133, 137, 148, 193;
  - IFEval 7: ifeval_143, 1314, 1834, 2139, 2785, 2909, 3484.
  I did not hand-check reverse prompts; they are outside the verdict, as pre-registered.
- **Matched-k (k = 8) expected entries / exits, fixed phase:**
  - IFBench h297: `s0100` 116.2 / 22.4, `s0500` 108.5 / 16.7, `main` 102.1 / 30.3;
  - IFEval: 62.7 / 5.0, 67.2 / 2.5, 66.7 / 12.0.

### R7. Hand gate, repeated blind (`rv_hand_items.py`, `rv_hand.py`, `hand/`)

**Rubric.** `hand/reader_prompt_if.md` contains the pre-registered rules 1–6 and rule 7 as the run applied it
(deviation 6). It also says that null-like tokens ("0", "None") are not answers. Readers saw only a batch file and the
rubric: the prompt, the constraints (all judged followed), and the graded answer, with a note on whether the model closed
its reasoning. They saw nothing about model, side, rank or selection. Items were shuffled across models and prompts.

**Rounds** (all labels verbatim in `hand/reader_labels/`; 813 items in 29 batches):
1. Round 1, 441 items, non-adaptive:
   - `main`'s first two strict successes in the pre-registered reading order on every non-excluded R candidate
     (315 items; the "first-read" set);
   - every base strict success within 256 on every R candidate (110 items);
   - 8 swapped-prompt controls (a real success shown under another prompt with the same constraint ids and kwargs,
     re-checked to pass) and 8 duplicates.
2. Round 2, 112 items: five more `main` reads on the 23 candidates where the base was drawn to 256 with no genuine
   success and `main` was undecided.
3. Round 3, 76 items, diagnostics on the 7 diagnostic prompts:
   - every `base_btok` and `math` strict success;
   - `s0100` / `s0500` reads 1–4 in the reading order.
4. Round 4, 184 items: five more `main` reads on the 7 non-deciding candidates with ≥ 1 genuine in round 1, and on a
   seeded 15 + 15 of the 125 with none. This round only estimates the confirmed / open-by-gaming shares.

**Controls:** 8/8 swapped-prompt items called gamed; 8/8 duplicates agree with their twin.

**My confirmation.** I read every deciding item myself:
- all 30 base successes on the 31 prompts drawn to 256;
- all `main` reads on those prompts;
- the confirming reads on the hand-reach prompts;
- ifeval_3323 and ifbench_224.

I agree with every deciding label. My one override (`hand/confirm.json`) changes no status: a CSV whose Country column is
"A"–"G" is a placeholder (6d). I also re-classified a seeded 10 % of the format-check items (R8); 8/8 agree.

**T4. Hand fates, every candidate the base was drawn to 256 on (pasted from `out/tables.md`, generated from `out/hand.json`; `main` reads = reads up to the deciding one)**

| prompt | strict fate | main reads (genuine) | main status | base strict successes (genuine) | hand fate |
|---|---|---|---|---|---|
| ifbench_100 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_101 | resolved | 3 (3) | confirmed | 2 (2) | **resolved** |
| ifbench_102 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_103 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_104 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_191 | dissolved | 0 (0) | unconfirmable | 1 (0) | **dissolved** |
| ifbench_218 | dissolved | 1 (0) | unconfirmable | 0 (0) | **dissolved** |
| ifbench_221 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifbench_241 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifbench_247 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifbench_249 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifbench_274 | REACH | 3 (3) | confirmed | 0 (0) | **REACH** |
| ifbench_291 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifbench_296 | resolved | 3 (2) | confirmed | 5 (1) | **open** |
| ifbench_67 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifbench_70 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifbench_89 | base-1-at-256 | 4 (0) | unconfirmable | 1 (0) | **dissolved** |
| ifbench_97 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_1361 | resolved | 7 (2) | confirmed | 4 (1) | **open** |
| ifeval_1480 | base-1-at-256 | 7 (0) | open-gaming | 1 (1) | **open-gaming** |
| ifeval_1512 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_1691 | base-1-at-256 | 7 (1) | open-gaming | 1 (0) | **open-gaming** |
| ifeval_219 | resolved | 3 (3) | confirmed | 2 (2) | **resolved** |
| ifeval_2239 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |
| ifeval_2247 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_2649 | resolved | 7 (0) | open-gaming | 2 (1) | **open-gaming** |
| ifeval_2857 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_2880 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_3272 | resolved | 3 (3) | confirmed | 5 (0) | **REACH** |
| ifeval_3619 | REACH | 7 (0) | open-gaming | 0 (0) | **open-gaming** |
| ifeval_3724 | base-1-at-256 | 7 (0) | open-gaming | 1 (0) | **open-gaming** |

- Notation: "open-gaming" is Part B's "open, gaming" (≥ 7 read, ≥ 4 fresh, ≤ 1 genuine). "Dissolved" means `main` has
  < 2 strict successes within 256, so it cannot reach 2 genuine. `s0100` / `s0500` were drawn only 8 times there.
- **Hand verdict.**
  - **IFBench: Reach.** Five prompts: ifbench_100, 102, 103, 104, 274.
  - **IFEval: Inconclusive.** One prompt reaches (ifeval_3272); 29 candidates are open and 23 open-gaming.
  - "No reach at 256" is impossible on either task: 70 IFBench and 29 IFEval candidates are open, most never extended.
- **Gamed share of `main`'s first-read strict successes:** 189/205 = 92.2 % on IFBench and 103/110 = 93.6 % on IFEval
  (292/315 = 92.7 % pooled). That is against `olmo-ifomega`'s ≈ 36 % for `step_2300` (32B Think, IFBench).
- **What `main`'s genuine answers on the hand-reach prompts are** (all its strict successes counted, `rv` inline):
  - ifbench_100 / 103 (yes/no/maybe): bare option words;
  - ifbench_102 (a)–d), legal question; correct d)): 124 × a) and 119 × d) in 255;
  - ifbench_104 (a)–d), "which is not a WER error"; correct c)): 244 × a), 9 × d), 3 × b), never c) in 256;
  - ifbench_274: a 7-row CSV;
  - ifeval_3272: the repeated request plus two "brand <<Name>>" names.
  - Rules 4 and 7 count wrong options as genuine. A correctness requirement would remove ifbench_104 and leave IFBench
    at 4 ≥ 3: still Reach. Treating the four format:options prompts as format-only would leave IFBench at 1:
    Inconclusive.
- **Potential reach left open.** ifeval_3323 and ifbench_224 are candidates where my readers confirm `main` but the
  base was never drawn to 256:
  - ifeval_3323: `main` gives two fresh genuine rewrites; the base's 3 strict successes in 48 draws are all debris;
  - ifbench_224: telegraphic option picks such as "b accurate"; the base has 16 draws.
  Under Part B's tier-1 rule (`main` hand-confirmed → base extension to 2 genuine or 256), both were extendable.
  Neither changes a verdict at the current counts.
- **`main` status shares** (pre-registered expectation 25 % confirmed, 50 % open by gaming):
  - observed: confirmed 8/108 IFBench and 4/56 IFEval; open-gaming 22/108 and 23/56;
  - 68 IFBench and 28 IFEval candidates were read only twice, all gamed;
  - of the seeded 30 such candidates read to 7, 29 end open-gaming and 1 unconfirmable, none confirmed;
  - estimated: confirmed ≈ 7 %, open-gaming ≈ 79 % (IFBench) / 91 % (IFEval).

### R8. Format check, Design 6 (`rv_fail_items.py`, `rv_fail.py`, `out/fail.txt`, `rv_embed.py`)

My own seeded draw (`random.Random(20261108)`), classified blind with the pre-registered rubric:
- up to 4 base failures per prompt from different extension chunks, plus up to 2 `main` failures;
- headline set: my six hand-reach prompts; labelled apart: the nine strict-only reach prompts.

| set | base failures | (u) no usable answer | (a) ignored | (b) near miss | (c) far off | (d) other constraint |
|---|---|---|---|---|---|---|
| hand-reach (6 prompts) | 24 | 12 (50 %) | 5 (21 %) | 0 | 7 (29 %) | 0 |
| strict-only (9 prompts) | 36 | 17 (47 %) | 12 (33 %) | 0 | 7 (19 %) | 0 |

- The base's failures are ≥ 50 % (u) on ifbench_100, 102, 103 and 274: 4 of the 6 hand-reach prompts. That is reach a
  format repair would remove, by the pre-registered reporting rule. The `t1` route is empty: no response has a turn
  token.
- On ifbench_104 and ifeval_3272 the base mostly attempts and misses: (c), or (a) for "repeat the request first".
- **Embedded answers** (mine, not pre-registered): a line or block that passes the checker on its own appears in this
  share of the base's 256 failures:
  - ifbench_100: 19 %; ifbench_102: 1 %; ifbench_103: 38 %; ifbench_104: 7 %; ifbench_274: 16 % (a valid 7-row CSV
    inside planning or debris).
  - Some hits are option words inside debris, so these are upper bounds.
  - One read item shows the base reasoning to the correct "c). Negation" on ifbench_104, then failing on the
    explanation. `main` never gives c).
- `main`'s few failures on these prompts are (b) or (c), all short.

### R9. Diagnostics: the base's own tokenizer, embedding rows, math, intermediate checkpoints

- **`base_btok`** (64 samples on each of the 7 diagnostic prompts; `D_base_btok*`):
  - it closes its reasoning (as text) in 256/448 = 57 % of samples, against 0.6 % under RL's tokenizer;
  - its strict successes, all read and all **genuine**: ifbench_100 9/9 (yes / maybe / no after closed reasoning),
    ifbench_103 5/5, ifbench_104 4/4 (once the correct c)), ifbench_296 1/1;
  - it has 0 strict successes on ifbench_102, 274 and ifeval_3272.
  - So on 3 of the 6 hand-reach prompts the base answers genuinely within 64 samples once `<think>` is plain text. A
    genuine `base_btok` success on 100 / 103 / 104 means the reach there is partly a token artifact (the run's
    pre-registered reading). The diagnostic is outside the verdict.
- **Embedding rows** (`rv_weights.py`, HTTP range reads of the Hub shards):
  - in the base, the rows of every added token except EOS and the FIM tokens sit at initialisation scale: embedding
    norm 1.23–1.29 against 5.54 for ordinary tokens (ids 1000–1015); unembedding norm 0.835–0.836 across them, against 1.444.
    That includes `<think>` 100268 and `</think>` 100269, and also `<|im_start|>` 100264 and `<|im_end|>` 100265;
  - RL moved the input rows of tokens in its prompts (100264, 100265, 100268, 100270, 100271: Δ 0.002–0.003 by step 100);
  - it never moved `</think>`'s rows (Δ 0.0000): RL-Zero-IF itself never emits `</think>`.
  - So under both tokenizers the base reads a chat frame built from untrained `<|im_start|>` / `<|im_end|>` tokens. Its
    own tokenizer removes only the untrained `<think>` / `<functions>`. The diagnostic is therefore a partial
    de-artifacting, not a clean "base as pretrained".
- **`math`** (RL-Zero-Math `main`, 32 samples per prompt):
  - 0 strict successes on ifbench_100, 102, 103, 104 and 274;
  - 1 on ifbench_296 ("were", gamed);
  - mean 900–4,500 tokens; it never gives a bare option.
- **`s0100` / `s0500`** (32 more draws on the 7 prompts):
  - `s0100` is confirmed on all six hand-reach prompts (4/4 genuine, with fresh ones);
  - `s0500` is confirmed on the five IFBench ones; on ifeval_3272 it has 1 genuine of 4 (it copies the request twice
    with no names).
  - The hand-reach behaviour is present by step 100.

### R10. Compute (`rv_compute.py`, `out/compute.txt`)

- **Axis.** Pre-registered definitions: 6ND = 2.663e23; 32 × 8 samples per step; oversample 1; low bound on
  RL-prompt lengths, high bound on evaluation lengths plus my mean templated Dolci prompt of 281 tokens. My lengths:
  - RL prompts: base 2,533, `s0100` 45, `s0500` 67, `main` 47 tokens;
  - evaluation: 2,404, 57, 155 and 35.
- Cumulative RL ÷ pretraining:

  | checkpoint | low | high |
  |---|---|---|
  | step 100 | 7.2e-6 | 1.0e-5 |
  | step 500 | 8.4e-6 | 1.9e-5 |
  | `main` at step 2,000 | 1.3e-5 | 5.3e-5 |

  Most of step 100's compute comes from the linear interpolation between the base's 2.5k-token responses and step
  100's 45. The true length collapse was probably faster, so step 100's figure is an upper bound.
- **Per job.** Samples and generated tokens counted from the rows equal the meta counts for all 26 metered jobs (one
  meta row each, no resumed segments).
  - `F_math_void` has 8 rows, 5,381 tokens and no meta.
  - Evaluation jobs: 142,696 samples, 51.0 M tokens. All jobs' meta generation time sums to 17.9 h (load 0.4 h), every job on one A100-SXM4-80GB.
  - Billed GPU time is a pods.log question for phase 2.

### R11. Weight checks and Stage 0

- **Weights** (`out/weights.txt`). This uses rows 0–1,023 of four shard-2 matrices, not the executor's full shard, and
  reproduces every ordering:
  - `main`↔`step_1900` 1.01e-3 < `main`↔`step_1800` 1.22e-3;
  - `step_1900`↔`step_1800` 0.98e-3;
  - `step_100`↔base 1.96e-3 ≈ `step_200`↔`step_100` 1.91e-3;
  - the margin ratio is 6.2 (pre-registered ≥ 10×, reported 6.1×).
- **Stage 0** (`out/stage0.txt`):
  - means 2,358 / 2,260 / 51 tokens; IFEval strict 0.250 / 0.163 / 0.787;
  - speculation A/B: −98 [−1,092, +893] tokens and −0.087 [−0.188, +0.012] strict; throughput ratio 1.087.
  - All reproduce Part B; not adopting speculation follows its rule.

### R12. Pre-registered binding expectations against my recount (`out/expect.md`)

- **Inside:** base pass@1 on both tasks; `main` pass@1 / pass@8 on IFEval and pass@8 on IFBench; `s0500` on IFEval;
  candidates R; base lengths and cut shares; `s0500` lengths; the gamed share (92–94 % against 80 % (60–95 %)); hand-reach
  counts (IFBench 5, IFEval 1); format (u) 50 % against 45 %.
- **Misses:**
  - `s0100` pass@1 is 0.477 / 0.806 against 0.10 / 0.35, and its length is 36–98 tokens against 1,500: step 100 is
    already a gamer;
  - `s0500` IFBench pass@1 is 0.410 against 0.25 (0.10–0.40);
  - `main` IFBench pass@1 is 0.469 against 0.30 (0.15–0.45);
  - `main` IFBench length is 29 tokens against ≥ 30;
  - reverse V is 38 / 14 against 5 / 3;
  - `main` hand-confirmed share is ≈ 7 % against 25 % (10–45 %);
  - IFBench open-gaming observed share is 20 % (estimate ≈ 79 %) against 50 % (30–75 %).
- **Verdict odds:** the pre-registered by-hand verdicts were IFBench Reach 40 % and IFEval Inconclusive 40 %, against
  strict Reach 85 % on each. All three outcomes match the most-likely-or-second category.

### R13. Phase-1 position (to compare in phase 2)

1. **Strict:** Reach on both tasks: 9 IFBench prompts and 5 IFEval prompts.
2. **By hand:**
   - IFBench Reach: 5 prompts (100, 102, 103, 104, 274), 4 of them format:options questions answered with a bare
     option;
   - IFEval Inconclusive: 1 prompt, ifeval_3272, with 29 open candidates.
3. **Gamed share:** `main`'s first-read strict successes are ≈ 93 % gamed.
4. **Format:** on the hand-reach prompts, the base's failures are half "no usable answer". On 4 of 6 prompts, a format
   repair would remove the reach. The base's own tokenizer recovers 3 of 6 genuinely. The base's chat-frame tokens are
   untrained under both tokenizers.
5. **To check against the write-up:**
   - whether ifeval_3323 / ifbench_224 should have been tier-1 extended;
   - how rule 7 and the wrong-option answers (ifbench_104) are worded;
   - the GPU-hour record;
   - the `D_base_btok` rows' `model` field: it is "base", so a pipeline that keys cells by model would mix them in;
   - the reach-share figure's denominators.

## §Compare (phase 2: after reading `run_olmo_rlzero_if.md`, `numbers.md` § olmo-rlzero-if, `log.md`, the plain summary and the derived tables)

### C0. Errata to my phase-1 recount (found by joining the executor's `handcheck.csv` to my items; `rv_hand_compare.py`)

On the 670 items both of us read, the labels agree on 660; on the first-read set, 310 of 315. I looked at all 10
disagreements and adopted the executor's label on 8. These are now phase-2 overrides in `hand/confirm.json`
(`"phase": 2`). `RV_PHASE1=1 python3 rv_hand.py` reproduces the phase-1 state; `out/hand_phase2.json` holds the new
one. On the first, my reader was wrong; on the other three, my readers had been inconsistent with themselves:
- **ifeval_219, base draw 146: my reader was wrong.** The 67-word reply is not itself in quotes. The whole-response
  quotes hold only through the quoted restatement that opens the planning (rule 6c), so the executor's override
  `hdda638` stands. ifeval_219 is therefore open (1 genuine base success in 256), not resolved.
- **ifeval_3323**, three of `main`'s lossy "bust" rewrites. They drop the beard and mustache, the sentence's content;
  my round-4 readers called the same kind of rewrite gamed. With them gamed, `main` has 1 genuine of 7 reads and is
  open by gaming.
- **ifbench_224**, "accurate Excused" ×2. Two prompt words name no option ("b accurate" stays genuine), so `main` is
  open by gaming.
- **ifbench_277**, two dates for "all" of Napoleon's battles ×2: a degenerate list, as my round-4 readers said.
- My phase-1 point "potential reach left open (ifeval_3323, ifbench_224)" is withdrawn. Under consistent labels `main`
  is confirmed on neither, so neither was owed a tier-1 extension.

Two disagreements remain; both are non-deciding and I keep my labels:
- ifbench_296 `main` "n" (gamed for me, genuine for the executor);
- ifeval_1361 `main` "a world full of trouble…" (gamed for me, genuine for the executor).

**Phase-2 state:**
- **Gamed share:** 192/205 = 93.7 % (IFBench) and 105/110 = 95.5 % (IFEval), equal to the executor's.
- **`main` hand-confirmed** on exactly the executor's 10 (ifbench_100–104, 274, 296; ifeval_1361, 219, 3272).
- **Hand verdicts** unchanged: IFBench Reach (100, 102, 103, 104, 274); IFEval Inconclusive (3272).
- **Prompt-level fates** are identical except ifeval_1087. I resolve it by hand (2 genuine of its 5 base successes);
  the executor read base successes only on tier-1 prompts, by design. Naming also differs: the executor files my
  "dissolved" (`main` with < 2 strict successes in 256) under open / exhausted and reports 0 dissolved. That is
  defensible, since `s0100` / `s0500` were never drawn to 256 there.

Also checked (R13's list):
- `D_base_btok` rows carry `model` "base", but `candidates.csv` counts the base at 256 on every diagnostic prompt, and
  `handcheck.csv` labels them `base_btok`. No mixing.
- The figure reads this run's cell from `verdict.csv` and labels the three inherited cells with their models.

### C1. Claims against my recount

| claim (source) | my value | verdict |
|---|---|---|
| Models, revisions; `main` ≈ one increment past `step_1900` (run, numbers) | Hub sha: `main` ≠ any step; base `main` = `stage3-step11921`; spot check 1.01e-3 / 1.22e-3 / 0.98e-3 | reproduces |
| Recipe `olmo_thinker` @ d928a7c, T 1, top-p 1, 16,384, stop `</answer>`, RL's tokenizer for all (run, numbers) | template byte-identical; 26 meta records; 7 pods' tokenizer hashes | reproduces |
| IFBench 297 (3 RL near-duplicates excluded), IFEval 150; "IFEval none" (run, numbers) | same 3 (content 0.51 / 0.79 / 0.51); also scanned the 88,556-row pre-release dataset: ifbench_238 matches there but was not in RL's seed-42 sample | reproduces |
| Hand gate of 1,527 responses, 12 overturned (run, numbers) | 1,527 rows, 12 overturned (9 → gamed, 3 → genuine) | reproduces (count) |
| "every label confirmed" (numbers) | the log says genuine labels were read in full, gamed ones by their evidence, plus a seeded 10 % of gamed answers | **reword**: "confirmed (genuine in full, gamed by evidence + 10 %)" |
| pass@1 / pass@8 table, all 12 cells (run, numbers) | identical to 3 decimals (T1) | reproduces |
| "By step 100 answers shrink from ≈ 2,300 to ≈ 40 tokens" (run, plain) | base mean 2,404 (eval) / 2,533 (RL prompts); `s0100` 36 IFBench, 98 IFEval, 45 RL prompts | reproduces for IFBench / RL prompts; IFEval is 98: **reword** "≈ 40–100" |
| 94 % of `main`'s first-read strict successes gamed; 32B Think run 36 % (run) | 297/315 = 94.3 % (phase 2; blind phase 1 92.7 %) | reproduces |
| "94 % of the passing answers we read were empty shells" (plain) | the 94 % is on reach candidates (prompts the base failed 16/16), not all passes | **reword**: "on the prompts where only RL passed" |
| `main` hand-confirmed on 10 of 164; open by gaming 138, exhausted 16 (run, numbers) | the same 10 (phase 2); I read 95 candidates only twice, and a seeded 30 of them read to 7 gave 29 open by gaming, 0 confirmed | reproduces (10); consistent (138 / 16) |
| Verdict IFBench Reach: 5 by hand (100, 102, 103, 104, 274), 9 strict (run, numbers) | identical prompt sets | reproduces |
| IFEval inconclusive by hand (3272), Reach under strict (1512, 2247, 2857, 2880, 3619) (run, numbers) | identical | reproduces |
| Tier-2 outcomes (5 clean / 9 resolved / 6 one success; IFEval 5 / 11 / 4) (numbers) | identical, prompt by prompt | reproduces |
| "steps 100 and 500 already reach them" (run) | `s0100` confirmed on all 6; `s0500` on the 5 IFBench prompts but not ifeval_3272 (1 genuine of 4 reads; the executor's 1 of 2) | **reword**: "step 100 on all six, step 500 on the five IFBench ones" (numbers.md already says so) |
| Base closes its reasoning in 46 of 7,200; never answers bare (run) | 46/7,200; 0 single-token `</think>` anywhere | reproduces |
| "RL's tokenizer makes `<think>` a token the base never saw" (run) | base embedding row of 100268 at initialisation scale (1.27 vs 5.54) | reproduces. **Add**: `<|im_start|>` / `<|im_end|>` are equally untrained, under both tokenizers. |
| Base own tokenizer closes in "34–47 of 64" (numbers) | 34–47 on the first four prompts; 25–47 over all seven (ifbench_274: 25) | differs slightly: say "25–47" |
| Own tokenizer answers genuinely on 3 of the 6 (100, 103, 104); 0 on 102, 274, 3272 (run, numbers) | identical (18/18 genuine) | reproduces (labelled diagnostic) |
| "Half of it is a tokenizer artifact" (run) | 3 of 6 is a lower bound: the diagnostic leaves the untrained chat-frame tokens in place | supported as a lower bound |
| Base failures: no usable answer 54 %, ignored 21 %, far off 25 % (run, numbers) | my own draw: 50 / 21 / 29 % (24 items); my 8-item spot check of my readers agrees | reproduces |
| — the pre-registered "reach a format repair would remove" (Design 6: base failures ≥ 50 % (u) or a `t1` success) | executor's own `failures_if.csv`: 5 of 6 (100, 102, 103, 274, 3272); mine 4 of 6 | **not reported**: a pre-registered quantity is missing |
| RL-Zero-Math 0 / 160 on the IFBench reach prompts (run, numbers) | 0/160 (1/32 gamed on ifbench_296, outside the set) | reproduces |
| "3 robust format prompts of 447" (run; plain "about 3 prompts out of 447") | the 3 that survive the tokenizer diagnostic (102, 274, 3272) still meet the format-repair rule in the executor's own table (in mine, 2 of the 3) | **not supported** as "robust": drop the word or name the format-repair result |
| "The IF/math split looks like a property of SFT, not of the domain" (run, plain) | one RL run per cell; 7B vs 32B; different RL data and templates. Here the base's failures are mostly format or termination failures (R8, R9), so this cell measures whether the base can present a bare answer, which the post-SFT comparator could. | **not supported** beyond "consistent with"; the format confound must be named |
| Matched-k entries / exits: IFBench `main` 102.1 / 30.3, IFEval 66.6 / 12.0 (numbers) | 102.1 / 30.3; 66.65 / 11.98 | reproduces |
| Compute axis 7.2–9.7e-6 (step 100), 0.8–1.7e-5 (500), 1.3–4.4e-5 (`main`) (numbers) | low bounds and lengths identical; my high bounds 1.0e-5 / 1.9e-5 / 5.3e-5 | low reproduces; high differs by ≤ 20 %. Their high bound implies ≈ 200 prompt tokens (undocumented); the templated Dolci prompts average 281. |
| Weight checks 9.9e-4 / 9.4e-4 / 1.95e-3 / 1.18e-2, 6.1× (numbers) | spot check 1.01e-3 / 0.98e-3 / 1.96e-3 / 1.22e-2, 6.2× | reproduces |
| Stage 0 (Part B table) | every cell, A/B intervals within bootstrap noise | reproduces |
| Reverse: strict IFBench 5, IFEval 7 (numbers) | identical | reproduces |
| Reverse by hand: IFEval 3 (1834, 2785, 2787), IFBench 0 (numbers) | I did not hand-read reverse prompts | not derivable (outside the verdict) |
| IFBench rule types never trained on, IFEval's were (plain) | 0 of IFBench's 58 instruction ids occur in RL's 54; all 25 of IFEval's do | reproduces |
| Cost $28.74 of $40, 19.98 pod-hours, 51.6 M tokens, ≈ 18.4 GPU-h in jobs (run, numbers) | pod spans × rates consistent; 51,601,546 tokens; registry rows match my per-job counts on all 26 jobs (18.37 GPU-h) | reproduces |
| Expectations vs outcomes (run) | the stated misses are real | partly reported: s0500 IFBench pass@1 (0.410 vs ≤ 0.40), `main` IFBench pass@1 (0.469 vs ≤ 0.45), `s0100` length (36–98 vs ≥ 300) and `main` IFBench length (29 vs ≥ 30) are misses the write-up omits |
| Bucket and MANIFEST (numbers) | 55 MANIFEST rows, every sha256 matches the file; bucket listing present | reproduces |

### C2. Process checks

- **Expectations before the run.**
  - Part A was committed at 05:30:23, before the first pod (05:31:37).
  - Part B with the binding numbers was committed at 06:04:42, before the first evaluation sample (08:05).
  - After that, the pre-registration's body changed only by one timestamp correction and the appended deviations.
- **Rule 7** was added at 09:10, after the first batch, and it decides 4 of the 5 IFBench hand-reach prompts.
  - It restates the pre-registered rule 4 (quality is not graded) for option answers.
  - A rule that graded correctness would remove only ifbench_104, where `main` answers a) 244 times in 256 and never
    the correct c). IFBench would still be at 4 ≥ 3: Reach.
  - The verdict therefore does not hinge on rule 7. The write-up should still say that 4 of the 5 rest on bare-option
    answers, and that on ifbench_104 they are wrong.
- **Wording against n.** No difference claims rest on seeds (no training). "Never" is used for the base's single-token
  `</think>` (0 of 143,176, verified) and for RL never writing `</think>` (0 in all RL rows, verified).
- **Compute record.** Registry rows exist and match. The write-up has no per-arm compute table, which the policy asks
  for: the base used 46.2 M of the 51.6 M tokens over 19,904 samples; `main` used 4.1 M over 115,328.

## §Verdict

**Stands:**
- Every quantity the run measured reproduces from the raw files and my own code:
  - fixed-phase pass@k;
  - 108 + 56 reach and 38 + 14 reverse candidates;
  - the extension and stopping-rule audit;
  - the three contamination exclusions; the pre-release dataset adds none;
  - template, decoding and tokenizer parity;
  - lengths, Stage 0 and the compute rows.
- The **strict verdicts** stand: Reach on both tasks (9 IFBench, 5 IFEval prompts).
- The **hand verdicts** stand on my blind repeat: IFBench Reach (ifbench_100, 102, 103, 104, 274) and IFEval
  Inconclusive (ifeval_3272 only).
- RL-Zero-IF's checker gaming stands: ≈ 94 % of first-read passes gamed, `main` hand-confirmed on 10 of 164.
- The base-tokenizer diagnostic stands: 3 of 6 recovered genuinely. So does the math arm's 0/160.
- No hard-constraint violation.

**Must be reworded:**
1. The **"Answer"** sentence. "3 robust format prompts of 447" is not robust. By the pre-registered Design-6 rule,
   5 of the 6 hand-reach prompts (the executor's own table; 4 in mine) are reach "a format repair would remove". That
   includes all 3 that survive the tokenizer diagnostic (2 of them in mine).
   - Suggested: "every hand-reach prompt is an exact-format prompt. Three vanish when the base reads `<think>` as text.
     On 5 of 6, at least half of the base's sampled failures are unusable output, so format, not capability, separates base and RL."
2. **"IF/math split is a property of SFT, not of the domain."** Say "consistent with". Name the confound: this run's
   base cannot present a bare answer under RL's chat frame. Its `<think>`, `</think>`, `<|im_start|>` and
   `<|im_end|>` rows are untrained, and its failures are half "no usable answer". The post-SFT comparator had no such
   handicap. The 2 × 2 grid therefore compares different things in its two IF cells.
3. **Report the pre-registered format-repair set.** It is missing.
4. Small corrections:
   - "≈ 40 tokens" → "≈ 40–100";
   - "steps 100 and 500 already reach them" → step 500 is not confirmed on ifeval_3272;
   - "34–47 of 64" → "25–47";
   - "every label confirmed" → how gamed labels were confirmed;
   - the plain summary's "94 % of the passing answers" → "on the prompts only RL passed";
   - list the omitted expectation misses;
   - document the compute axis's prompt-token input (≈ 200 implied, 281 measured);
   - add a per-arm compute table.
5. **Name what the 4 option-prompt "reaches" are:** bare option letters or words. On ifbench_104 `main` is wrong every
   time; on ifbench_102 it is right about half the time (119 d) vs 124 a)).

**Not supported:** "robust" reach, and SFT as the cause of the IF/math split (beyond "consistent with").

**Next measurement that would settle what is open.**
1. **A format-controlled base arm** on the 6 hand-reach and 9 strict-only prompts, to 256 each:
   - the base with its own tokenizer, a plain-text chat frame it has seen in pretraining (no `<|im_start|>`), and a
     one-shot exemplar of a bare answer;
   - read like the run's base extension.
   If the base then answers the option and CSV prompts genuinely, the IFBench Reach dissolves. At the run's measured
   ≈ $0.63 per M tokens and ≈ 2.2k-token base responses, this is ≈ $5.
2. **IFEval cannot be settled within the pre-registered caps.**
   - ifeval_1361 and 219 have `main` confirmed and exactly one genuine base success in 256. They can never become reach
     or resolved under the rule.
   - "Open, gaming" counts as open, so with a gaming challenger "No reach at 256" is unattainable by design.
   - Reading `main` to the stop rule on the 28 candidates read only twice could add reach prompts only where `main`
     turns out confirmed; my seeded sample found none in 30.
   - A useful change is to the rule, for future runs: count "open, gaming" as "dissolved", as I argued for
     `olmo-rlzero-pilot` (a verdict rule must be satisfiable under each hypothesis it names).
3. **For the SFT question,** run the same protocol on a size-matched pair that differs only in SFT: Olmo 3 7B Think-SFT
   (or Instruct-SFT) against its RL successor, at a recipe where both close their reasoning. That separates "SFT
   supplies the capability" from "SFT supplies the answer format".
