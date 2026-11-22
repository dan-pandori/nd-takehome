# Review — olmo-ifcurve (proposal 46)

Reviewer: agent:claude (role reviewer), a session independent of the executor. Run branch `dan_olmo-ifcurve`, reviewed
at `0498d0cf` (the executor's last commit, 2026-11-22 06:23 UTC). Kit: `review/olmo-ifcurve-recount/` (README there;
every number below is in its `out/`). Phase 1 used the workspace `~/review/olmo-ifcurve` (executor write-ups removed)
and did not open `log.md`, `QUESTIONS.md`, `figures/olmo_ifcurve.png`, `olmo_ifcurve/{README.md, results.csv,
summary.json, emergence.csv, gaming.csv, passk.csv, lengths.csv, handcheck.csv, compute.csv, gate_summary.json,
claim_check*.md, handcheck_rule_addendum.md, numbers_section.py, figures.py, analyze.py, adjudicate.py}`,
`artifacts/olmo-ifcurve/registry/`, or the executor's hand-gate labels until my own labels were final.

**Disclosure (early exposure, with times).**
- 06:24 UTC, session start: my memory index carries one line on this run, which includes "results (sharpening from
  1,100; genuine plateau ≈ 0.50)". I did not open the memory file behind it.
- 06:25: the first five rows of `olmo_ifcurve/jobs.csv` (per-job draws, tokens, GPU-seconds; no outcome numbers).
- 06:56: while checking file formats, the first two rows of the executor's `hand/confirm.csv` (two adjudications to
  *gamed* under rules 2 / 7, items `c5427cc`, `cc51bd3`; I never looked up which draws they are) and the header of
  `hand/status.csv` (column names only).
- The branch's commit subjects (`git log`) name procedures, not outcomes ("amendment 3 (s0350 cancelled …)", "claim
  check (25 findings) and fixes").

My selection rules, reader instructions and confirmation rules were fixed in code before any of my reader labels
existed. No executor label was used for any of my labels; the executor's labels were opened only for the agreement
table (§Recount 7), after my labels were final.

**Models (every number below names one of these).** All are pretrained Olmo 3 / 3.1 32B (32.2 B parameters, bf16,
Think chat format), sampled with vLLM 0.11.0 on one H200 at T 1.0, top-p 1.0, `max_tokens` 32,768.
- `dpo` = `allenai/Olmo-3-32B-Think-DPO` `main` @ `97604023` (the RL start, step 0).
- `sNNNN` = `allenai/Olmo-3.1-32B-Think` @ `step_NNNN` (GRPO-style Think RL by AI2 on Dolci-Think-RL), for NNNN ∈
  {0050, 0100, 0200, 0500, 0750, 1100, 1600}; `s2300` = `main` @ `97ade57a` (weights identical to `step_2300` @
  `29884259`). `s0350` was cancelled (amendment 3) and has no draws.

Prompts: IFBench (`cd189a9c`) and IFEval (`e6890f85`), the original prompts, no hints. Checkers: the official strict
(and loose) checkers, from my own fetch of the upstream repositories.

## §Recount (phase 1, blind)

Written 2026-11-22 06:24–09:58 UTC, before I opened `run_olmo_ifcurve.md`, `numbers.md`, `log.md` or the executor's
analysis tables. In short:
- The checkpoints, prompts, reuse, decoding and template all check out, and every stored grade reproduces.
- Arm A, the lengths and the shape reading reproduce from the stored samples with my own code; the shape is
  sharpening from 1,100.
- My independent hand gate (2,124 blinded reads, my confirmations; 0.917 agreement with the executor's labels)
  gives:
  - timing: "no order" on F1 but "habit first" on F2;
  - gradual 7 / abrupt 0 of 32 F25 prompts;
  - arm-C gaming flat (0.16 → 0.27), while arm B's secondary share grows (0.06 → 0.34);
  - not brevity first.
- Expectations 1, 2, 3 and 8 hit. 5 (reading), 6 (gradual) and 7 (secondary) miss. 9 and 10 miss narrowly at s1600.
  4 hits on base cells.

### 1. Checkpoints, prompts and reuse (`rvc_hub.py`, `rvc_provenance.py`, `rvc_cells.py`)

- **Checkpoint manifest.** My own Hub API query (11 revisions) reproduces every commit hash, the 14-shard count, the
  weight bytes (64,467,127,296) and the `tokenizer.json` blob (`5fe17212`, identical in all eleven) of
  `olmo_ifcurve/checkpoints.csv`. `main` of Olmo-3.1-32B-Think and `step_2300` have identical shard names and LFS
  sha256 and an identical index weight map; only `README.md`, `.eval_results/lexam-hard.yaml` and the index file's
  blob differ. The ten distinct revisions have ten distinct weight sets. `main` last changed on 2026-06-25 (DPO repo)
  and 2026-10-13 (3.1 Think), both before the stored draws of 2026-11-04 to 11-07, so those draws came from the same
  weights. Every new job's `JOB_START` line records the Hub commit of its revision. I could not reproduce the
  `weights_digest` column with three candidate formulas. I checked the per-shard LFS hashes directly instead, so this
  costs nothing. Minor inaccuracy in the pre-registration: `generation_config.json` has **three** distinct blobs, not
  two (`dpo`'s has T 0.6 / top-p 0.95 without `do_sample`; 50 / 100 / 200 / 750 / 1100 / 2300 have them with
  `do_sample`; 350 / 500 / 1600 have none). This does not matter, because the sampler passes T 1 / top-p 1 explicitly
  with `generation_config="vllm"`.
- **Prompts.** `olmo_ifomega/problems.jsonl` is byte-identical to its 2026-11-04 bucket copy, uploaded before the
  stored jobs. For all 306 prompts any job used, the prompt, instruction ids and kwargs equal the upstream records.
  Arm A = `pids_ifbench.txt` (300) − `exclusions.csv` (82) = 218 = `pids_armA.txt`. Reach = `olmo_ifladder/classify.csv`
  = 48 (42 IFBench, all inside the 218) = `pids_reach.txt`. Classes from `classify.csv`'s `reading`: P 25 / T 16 / N 7,
  the pre-registered lists. Families: format 65, words 58, count 43, ratio 21, sentence 14, custom 11, repeat 6.
- **Decoding and template, every job.** All 33 metas (25 new jobs + 2 stage-0 metas + 6 reused jobs) have template
  sha256 `eba6e269…`, vLLM 0.11.0, torch 2.8.0+cu128, T 1.0, top-p 1.0, `max_tokens` 32,768, TP 1, no LoRA, no
  `fill_context`, problems `olmo_ifomega/problems.jsonl`, one H200, and the revision of their checkpoint. Every engine
  seed is distinct within a checkpoint. All 1,576 per-(job, prompt) `prompt_sha256_by_pid` values equal my own
  rendering of the `olmo_thinker` template + the DPO `tokenizer.json`. Every row's `prompt_tokens` (all jobs except the
  four olmo-ifomega `F_*` jobs, which predate the field) equals my rebuilt length. The stored `F_*` jobs used the same
  sampler `TEMPLATE` (byte-identical) and the same `--tokenizer /workspace/models/tok` launcher line. Only their
  scheduling order (`long_first` vs `given`) differs, and that does not change the sampling distribution.
- **Reuse inventory.** My cell builder, written from the pre-registration's table and amendments 1–5, puts every arm-A
  cell at the pre-registered size: `dpo` 16 (`F_dpo_ifb`); 4 at 50 / 200; 8 at 100 / 500 / 750 / 1100 / 1600 / 2300 (s0500:
  `M_s0500` chunk 0 + `T_s0500`). Every arm-B base cell is 32. At s0100: `F_s0100_ifb` 8 + `B_s0100` 24 on IFBench.
  At s0750: `T4_s0750` chunks 0–1, `T4b_s0750` chunk 1 for `ifbench_19`, and `B_s0750` 16 on exactly the 17 IFBench
  prompts with one T4 chunk. At s2300: `B_s2300`, all new. Every plan spec is matched exactly by its rows, all chunks
  complete. No two draws in any (checkpoint, prompt) have identical response ids (a seed-collision test over 34,320
  rows). The `T4_s0750` cells reuse a sequential-stopping job (stop at 2 strict, budget stop file). Taken as the
  pre-registered prefix (chunks 0–1, missing positions filled by new i.i.d. draws), they are still i.i.d.: whether
  chunk 1 exists depends only on chunk 0. No stored s0100 draw could have selected a reach prompt (0 of 336 strict,
  re-derived in §3). Extension cells: 49 cells of 128 (base 32 + X / X2 / X3 / X4 draws) on all 48 prompts.
  `ifbench_170` has two: s1600 (`X2_s1600` + `X3_s1600`, 96) and s1100 (`X4_s1100`, 96). X4 came after the last
  amendment (02:28) and no amendment covers it (§Recount 8).
- **Pre-registration timing.** Committed 2026-11-21 05:46:36 UTC (`75318677`), before the first pod (05:52, the
  orphaned `ifc-a` create) and before the first draw (`M_s0050` stage 0, 17:52:44). Each amendment was committed
  before the jobs it admitted: amendment 2 at 17:49:28 before the first draw; amendment 4 at 01:53:40 before the first
  X3 job (02:01:16); amendment 5 at 02:28:24 before `T_s0500` (02:38:10). No `M_s0350` log exists. Budget registered
  at 05:20:46 ($120), raised to $160 at 17:47:33.
- **RL-data overlap** (inherited from olmo-ifomega's `contamination.csv`, kind `rl` = Dolci-Think-RL-32B prompts, 4
  files / 102,026 docs): 0 of 218 and 0 of 48 at content containment ≥ 0.5 (max 0.382 arm A, 0.174 reach). 7 of the 218
  and 1 of the 48 share a 13-gram with some RL document. This is not a new scan.

### 2. Re-grade (`rvc_regrade.py`, `rvc_gradecmp.py`)

I re-graded all 34,320 rows (25 new jobs + 6 reused) with my own driver around the upstream IFBench / IFEval strict
and loose checkers. The input was the answer after the last `</think>`, stripped, against the original prompt and
kwargs. Every row's text equals my decode of its stored ids. Against the run's per-row `rows/*.csv`, **strict and loose
agree on 34,320 / 34,320**, as do `finish`, `</think>` presence and token count. The length columns differ only by
definition:
- `ans_tok` is 1 higher in the run's rows; the run counts the final EOS.
- `think_tok` / `think_words` differ on 109 / 110 rows. My count stops at the first `</think>`; on the 71 rows with
  two or more, the run's apparently stops at the last.
- `ans_words` is 0 instead of none on 39 rows that have no `</think>`.

### 3. Template boundary and token budget (`rvc_boundary.py`, `rvc_armA.py`)

- **Template boundary.** I rebuilt five full requests from my prompt ids plus the stored response ids, one each from
  `F_dpo_ifb`, `M_s0050`, `T4_s0750`, `B_s2300` and `X3_s1600`, and read them by hand. Each prompt ends
  `<|im_end|>\n<|im_start|>assistant\n<think>`, the response starts with thinking text ("Okay, …"), and the response
  ends `…<|endoftext|>`. Over all 34,320 rows:
  - none opens a second `<think>`;
  - every `finish stop` row (34,265) ends with the EOS 100257;
  - every other row (55) is `finish length`, cut at the cap with no EOS;
  - 18 rows (10 stop, 8 cut) contain stray chat special ids (100264 / 100265 / 100276) inside the response, which
    decoding with `skip_special_tokens` drops.
- **Same budget for every model:** `max_tokens` 32,768, no `fill_context`. Share of draws cut at the cap (arm-A
  cells): dpo 0.06 %, 50 0, 100 0, 200 0, 500 0.17 %, 750 0.17 %, 1100 0.46 %, **1600 0.63 %** (11 of 1,744), 2300 0.
  Reach base cells: up to 0.72 % (s1100). Draws with no `</think>`: at most 0.52 % (s1600 arm A) and 0.65 % (s1100
  reach).

### 4. Arm A, aggregate curve (`rvc_armA.py`; 218 IFBench prompts; strict; unbiased pass@k; 95 % prompt bootstrap, 10,000)

| ckpt | draws / prompt | pass@1 | pass@4 | pass@8 |
|---|---|---|---|---|
| dpo | 16 | 0.290 [0.239, 0.343] | 0.403 | 0.461 [0.400, 0.524] |
| s0050 | 4 | 0.296 [0.243, 0.351] | 0.422 | — |
| s0100 | 8 | 0.315 [0.263, 0.368] | 0.441 | 0.505 [0.440, 0.569] |
| s0200 | 4 | 0.347 [0.292, 0.405] | 0.482 | — |
| s0500 | 8 | 0.412 [0.357, 0.467] | 0.580 | 0.656 [0.592, 0.716] |
| s0750 | 8 | 0.512 [0.460, 0.564] | 0.714 | 0.794 [0.739, 0.844] |
| s1100 | 8 | 0.577 [0.528, 0.626] | 0.795 | 0.872 [0.826, 0.913] |
| s1600 | 8 | 0.646 [0.598, 0.694] | 0.830 | 0.872 [0.826, 0.913] |
| s2300 | 8 | 0.683 [0.635, 0.732] | 0.844 | 0.885 [0.844, 0.927] |

`dpo`'s first 8 draws give 0.290 / 0.459 (the pre-registered check). The stored values the pre-registration quotes are
reproduced: 0.290 / 0.315 / 0.512 / 0.683 (quoted 0.684; mine is 0.68349) and 0.461 / 0.505 / 0.794 / 0.885.
Adjacent paired differences in pass@1 (95 %): +0.006 (0→50), +0.019 (50→100), +0.033, +0.064, +0.100, +0.065,
+0.069, +0.037 (1600→2300). Only the first two intervals include 0. s1100 and s1600 have the same pass@8 by
coincidence: 190 of 218 prompts with ≥ 1 strict in 8 at each, with 11 prompts swapped each way. Ten prompts have no
strict success in any of the 64 draws across dpo, 100, 750, 1100, 1600 and 2300. Per-family pass@1 (and pass@8) are
in `out/armA.txt`. Every family rises; `custom` (11) and `repeat` (6) are flat or noisy after 750.

**Reading 5 (shape).** Paired 90 % intervals of D(c) = value(2300) − value(c):
- c = 750: D1 +0.171 [+0.138, +0.205], D8 +0.092 [+0.046, +0.138];
- c = 1100: D1 +0.106 [+0.080, +0.133], D8 +0.014 [−0.018, +0.046];
- c = 1600: D1 +0.037 [+0.018, +0.056], D8 +0.014 [−0.014, +0.041].

**Sharpening from 1,100** under the pre-registered criterion: from 1,100 on, pass@1 still rises detectably and pass@8
has no detectable gain. pass@8 sits at 0.87–0.89 from 1,100 on, near the ceiling set by the prompts no checkpoint
solves.

### 5. Arm D, lengths (`rvc_armA.py`, `rvc_boundary.py`; medians over all arm-A draws)

| ckpt | thinking tokens | answer tokens | thinking words | answer words | no `</think>` | cut at cap |
|---|---|---|---|---|---|---|
| dpo | 2,114 | 426 | 1,491 | 261 | 0 | 0.06 % |
| s0050 | 2,166 | 391 | 1,492 | 243 | 0.11 % | 0 |
| s0100 | 2,239 | 361 | 1,576 | 219 | 0.06 % | 0 |
| s0200 | 2,147 | 292 | 1,528 | 181 | 0 | 0 |
| s0500 | 3,039 | 218 | 2,053 | 135 | 0.06 % | 0.17 % |
| s0750 | 4,412 | 144 | 2,905 | 93 | 0 | 0.17 % |
| s1100 | 5,307 | 108 | 3,470 | 73 | 0.17 % | 0.46 % |
| s1600 | 4,501 | 83 | 2,908 | 57 | 0.52 % | 0.63 % |
| s2300 | 5,470 | 73 | 3,570 | 50 | 0 | 0 |

Thinking = ids wholly before the first `</think>` over draws that have one. With the last `</think>` instead, s0100
gives 2,247 and every other checkpoint is within 6 tokens; counting no-`</think>` draws as all-thinking gives s1100
5,312 and s1600 4,533. Reach base cells (`out/armA.txt`) think longer (s0050 2,598 … s2300 6,059) and answer shorter
at late steps (s2300 33 words). Thinking falls at s1600: 4,501 is 15.2 % below s1100's 5,307 (14.7 % if no-`</think>`
draws count as all-thinking).

**Brevity B** = the first checkpoint from which every later m(c) is within ±20 % of m(2300) = 50 words: **s1600**
(57 / 50; s1100's 73 is 46 % above). With answer tokens instead: s1600.

### 6. Hand gate, my blind repeat (`rvc_hand.py`, `rvc_hand_items.py`, `rvc_adjudicate*.py`, `rvc_confirm.py`, `rvc_rule5.py`, `rvc_audit.py`, `rvc_hand_report.py`)

**Readers.** Blinded general-purpose sub-agents, 1–21 items each. They got the run's pre-registered reader prompt
verbatim (`olmo_ifcurve/handcheck_prompt_if.md`: the two definitions, no rules). Each item file held the prompt, the
constraints with the strict checker's verdicts, and the answer. Ids were random and items shuffled across prompts,
checkpoints and arms; readers saw no model, step, arm, thinking or selection reason.

**Selection** (my code, from the pre-registered walk):
- the arm-B walk (a), (b), (c), (e), run in optimistic rounds;
- (f) each prompt's s2300 cell read until 2 genuine, for expectation 4;
- (d) the first min(strict, 4) of every arm-B cell, for the secondary gaming reading;
- an arm-C sub-sample: the first 20 of the pre-registered seeded 40 per checkpoint. My implementation of the
  pre-registered sampling rule (population sorted by draw key) reproduces the executor's sample: 349 of the 360 drawn
  draws are in its `hand/key.csv`, and the other 11 are answers identical to ones it read.

**Labels.**
- The mechanical rule-1 screen (the pre-registered literal test, unit-tested on 15 strings including emoji, `.</i>`
  and `.<br>` breaks) labelled 120 strict successes gamed. They are inline-`-` sub-bullets, unpunctuated per-sentence
  answers and one-line indent stairs.
- Identity inheritance covered 65 draws.
- Second reads went to:
  - every reader-labelled item of (a) and (e);
  - the genuine items that set F2;
  - "F25-fragile" items, which I added: cells at 7 or 8 genuine;
  - a seeded quarter of my arm-C sample.
- Every split went to a third reader (36), decided by majority of three.

**Volume.** 2,124 reads on 1,524 answer groups:
- 1,269 first reads (walk, arm C, rule f);
- 255 rule-(d) first reads;
- 564 second reads;
- 36 third reads.

First and second reads agree on 525 of 564 (0.931).

**My confirmation** (rules 1–12, in force before any of my labels):
- An adjudicator sub-agent got rules 1–12, the item and the reads. It proposed a label and rule for:
  - every group with a `checker_agrees = false` read or a split (90 groups);
  - every read group of ifbench_206 / 207 / 268 (102 groups). The olmo-ifladder addendum makes rules 10–12
    apply to every item of those prompts.
- I accepted proposals except low-confidence ones against two agreeing reads or a 2–1 majority (16 not accepted,
  `hand/adj_rejected.json`; the policy was fixed before any reading was computed from these labels).
- A mechanical rule-5 pass on the two fixed-output prompts (`ifbench_284` `repeat_span`, `ifbench_64`
  `repeat_simple`) moved one label group, every `ifbench_284` success (all the same 4-word span "code and theory
  behind"), from gamed to genuine.
- Net: 169 confirmations, 28 of which change a reader majority or a single read.
- **Disclosure:** I ran the rule-5 and the rule-10–12 passes only after my first agreement table with the executor's
  labels showed rule-5 and rule-10 cases my readers had labelled the other way (they agreed with each other and
  flagged no checker disagreement, so my first pass never reached them). Both apply pre-registered rules mechanically
  or through my adjudicator; neither copies an executor label. The readings without them are variants `noR5` /
  `noADJ4` (below).

**Audit.** I applied the checkers' own units to every labelled group with a per-sentence or sub-bullet constraint.
4 genuine answers are ones whose checker sees a single "sentence": `ifbench_189` ×2 (4/8/12 and 4/8/12/16/20 words,
each line in `<i>`, met in substance) and `ifbench_67` ×2 (each line ends in an emoji, no full stops). I kept them
genuine under rule 7's "not met in substance" test. Rule 7's literal example ("no sentence punctuation for a
per-sentence rule") would make them gamed; that is variant `r7literal`. Five rule-6 groups (all `ifbench_290`, ALL-CAPS
for title case) are genuine on the primary reading and not successes in variant `rule6strict`.

**Agreement with the executor's labels.** I opened them only after my labels were final; `rvc_compare.py` merges the
executor's reads with its `confirm.csv` and `screen.csv`.
- **Overall:** 1,607 draws labelled by both; 1,474 agree (0.917), Cohen's κ 0.82.
  - Mine gamed where the executor's is genuine: 100.
  - Mine genuine where the executor's is gamed: 33.
- **By part:** arm C 0.926 (κ 0.73, n 176), extension 0.925, walk 0.915.
- **By checkpoint:** lowest at s2300, 0.871.
- **Deciding items** (my walk's F1 / F2 / F25 / F1* sets): 32 of 566 disagree, 26 of them mine gamed against the
  executor's genuine.
  - `ifbench_203`: 9, thin "Absolutely …" answers inside an A–Z word chain.
  - `ifbench_170`: 5, three-word sentences.
  - `ifbench_268`: 3; `ifbench_271`: 3; 1–2 each on eight more prompts.
- Before the rule-5 and rule-10–12 passes the agreement was 0.899 (κ 0.79).

### 7. Arm B, reach emergence (`rvc_readings.py`; 48 prompts, base cells of 32, extension cells of 128; out/emergence.csv)

Every walk is complete: no needed item is unlabelled. Per prompt, under my labels (steps; F1* uses only the
pre-registered extension cell, the checkpoint before F1):

| class | prompts (F1 / F2 / F1* / F25) |
|---|---|
| P (25) | 220 100/500/50/750 · e2247 100/750/100/750 · 133 200/200/200/750 · 173 200/500/100/750 · 19 200/200/200/– · 204 200/200/200/750 · e2563 200/200/100/750 · 136 500/500/200/750 · 186 500/500/500/750 · 187 500/750/200/750 · 211 500/500/500/750 · 280 500/500/500/– · 78 500/500/500/750 · e1314 500/500/500/1100 · e2447 500/500/200/1100 · 128 750/750/500/1100 · 179 750/1100/750/– · 226 750/750/750/1100 · 253 750/1100/750/1600 · 267 750/750/500/750 · 290 750/750/500/1600 · 64 750/750/500/1100 · 79 750/1100/750/1100 · 252 1100/1100/750/1100 · 189 2300/–/1600/– |
| T (16) | 217 200/200/200/– · 248 200/500/200/750 · 206 500/500/500/– · 209 500/500/500/– · 269 500/500/500/750 · 0 750/1100/750/– · 1 750/1600/750/– · 154 750/750/750/1100 · 264 750/1100/500/1600 · 271 750/750/750/1100 · 4 750/1600/750/– · e2350 750/1100/750/1100 · 169 1100/1100/1100/2300 · 203 1100/1100/750/– · 170 2300/2300/1600/– · 207 2300/2300/1600/2300 |
| N (7) | 166 1100/–/1100/– · 284 1100/1100/750/– · 3 1100/1100/1100/2300 · e3478 1100/1100/1100/2300 · 188 1600/–/1600/– · 268 1600/1600/1600/– · 67 1600/1600/1600/2300 |

("–" = never within the sampled checkpoints; bare numbers are IFBench ids, `e…` IFEval.)

- **Never reached:** none. Before the rule-5 pass, `ifbench_284` was never reached: 0 genuine in 8 × 32 base draws +
  96 extension draws at s0750.
- **Extension placement:** for 46 of 48 prompts the run's extension cell is the checkpoint before my F1.
  - `ifbench_268`: my F1 is s1600 (its one s1100 success is gamed under two reads). The run extended s0750, the
    checkpoint before an F1 of s1100, so the s1100 cell has only 32 draws.
  - `ifbench_170`: my F1 is s2300, and the designed extension s1600 is present (7 genuine in 96). The run also drew
    an off-design 96-draw extension at s1100 (`X4_s1100`, started 04:14, after the last amendment). It has 5 genuine
    in 96. Under the pre-registered "no iteration" it is outside the design; counted, it would move F1* to s1100.
- **Earliest detectable rate** (genuine at F1*): median 1/32 = 0.031. 17 prompts' F1* is an extension cell at
  1–7 / 128.

**Reading 1 (timing; never = 9,999; stratified bootstrap, 10,000).**

| statistic | med P | med T | med N | med(T∪N) − med(P) | 90 % interval | reading |
|---|---|---|---|---|---|---|
| F1 | 500 | 750 | 1,100 | 250 | [0, 600] | **no order** |
| F1, 154 in P | 500 | 750 | 1,100 | 425 | [0, 600] | no order |
| F2 | 500 | 1,100 | 1,600 | 600 | [350, 850] | habit first |
| F2, 154 in P | 625 | 1,100 | 1,600 | 475 | [350, 850] | habit first |

The order condition holds on F1, but the interval condition does not: 9.5 % of replicates are ≤ 0, so the 5th
percentile is exactly 0. Resampling T ∪ N jointly gives the same result. The F1 reading is "no order" in all seven
label variants (final, rule6strict, r7literal, adjall, firstread, noADJ4, noR5), and the F2 reading is "habit first"
in all seven.

**Reading 2 (gradual / abrupt).** 32 prompts reach F25:
- gradual 7 (0.22);
- abrupt 0;
- intermediate 25.

16 more are slow (F1* ≤ 2,300, no F25).

By class:
- P: gradual 6, intermediate 15, slow 4;
- T: gradual 1, intermediate 7, slow 8;
- N: intermediate 3, slow 4.

No prompt qualifies as abrupt. Three prompts have F1 = F25 (267, 252, 207). Each had genuine successes in its
128-draw extension one checkpoint earlier (7, 4 and 6 of 128), so F1* < F25. The variants give gradual 0.19–0.24 and
abrupt 0. With eight sampled checkpoints, "≥ 2 checkpoints strictly between F1* and F25" is hard to
meet; most reached prompts go from F1* to F25 in one or two steps.

### 8. Gaming (reading 3; `rvc_readings.py`, `out/gamed_by_step.txt`)

Gamed / labelled among strict successes:

| ckpt | dpo | 50 | 100 | 200 | 500 | 750 | 1100 | 1600 | 2300 |
|---|---|---|---|---|---|---|---|---|---|
| arm C (my 20 / ckpt) | 3/20 | 4/20 | 3/20 | 3/20 | 1/20 | 2/20 | 5/20 | 5/20 | 6/20 |
| arm B, first min(strict, 4) per cell | – | 0/0 | 0/2 | 1/14 | 10/61 | 32/122 | 47/170 | 64/178 | 69/188 |

- **Primary (arm C):** early {0, 50, 100, 200} 0.163 (n 80) vs late {1100, 1600, 2300} 0.267 (n 60). Early − late =
  −0.104, prompt-cluster 90 % interval [−0.227, +0.014]: **flat**. The first-read-only variant gives 0.150 vs 0.267,
  also flat.
- **Secondary (arm B):** early {50, 100, 200} 0.062 (n 16) vs late 0.336 (n 536), difference −0.273 [−0.387, −0.139]:
  **gaming grows**. The early set is tiny, and the late set is dominated by the slow prompts' many strict passes.
- **Estimated genuine pass@1** (arm A strict × (1 − my arm-C share)): 0.246 (dpo), 0.237, 0.268, 0.295, 0.391, 0.461,
  0.433, 0.485, 0.478 (s2300). It rises to 0.46 by s0750 and then sits within 0.43–0.49. These are estimates from 20
  labels per checkpoint: each share carries a binomial SE ≈ 0.07–0.10.

### 9. Brevity (reading 4)

**B = s1600** (§5). **H = s0750**: prompts with F2 ≤ c: 0 / 0 / 5 / 18 / **27** / 39 / 43 / 45 at 50 … 2,300. B is
later than H, so **not brevity first** (also with answer tokens).

### 10. Expectations (pre-registered 2026-11-21 05:46, scored on my numbers)

| # | expectation | mine | verdict |
|---|---|---|---|
| 1 | pass@1 50 [.27,.34], 200 [.31,.42], 500 [.40,.51], 1100 [.53,.64], 1600 [.58,.68]; pass@8 1100 [.80,.89], 1600 [.82,.90] (500 / 350 / 200 / 50 pass@8 "not measured" per amendment 1) | 0.296, 0.347, 0.412, 0.577, 0.646; pass@8 0.872, 0.872 (s0500 pass@8 0.656, inside its original [.62,.78]) | **hit** (all inside) |
| 2 | no pass@1 drop > 0.03 | all adjacent differences positive | **hit** |
| 3 | sharpening from 1,100 or 1,600 | sharpening from 1,100 | **hit** |
| 4 | any genuine at s0050 / s0100 on ≤ 3 prompts; F1 ≤ 750 on 28–36; s2300 ≥ 1 genuine on ≥ 44, ≥ 2 on ≥ 40 | base cells 0 / 2 (with the extension draws, s0100 has 4); 35; 44 / 41 | **hit** on base cells (s0100 misses by one if the extension draws count); before the rule-5 pass 43 / 39, a miss |
| 5 | median F1 P ≤ 500, T ∈ {500, 750}, N ≥ 1,100; "habit first" | 500 / 750 / 1,100; no order | medians **hit**, reading **miss** (habit first only on F2) |
| 6 | of F25 prompts gradual ≥ 50 %, abrupt ≤ 20 %; median earliest rate ≤ 3/32 | 22 %, 0 %, 1/32 | gradual **miss**; abrupt and rate **hit** |
| 7 | arm C early and late in [0.05, 0.30], flat; arm B secondary "gaming first" | 0.163 / 0.267, flat; secondary gaming grows | primary **hit**; secondary **miss** (opposite direction) |
| 8 | B ∈ {1100, 1600}, H ∈ {750, 1100}; not brevity first | s1600, s0750, not brevity first | **hit** |
| 9 | thinking s0050 [1,900, 2,600], s1600 [4,500, 5,700], no checkpoint > 15 % below its predecessor; answer words 50 [200,270], 500 [90,180], 1100 [55,95], 1600 [45,75] | 2,166; 4,501; s1600 is 15.2 % below s1100 (5,307); 243, 135, 73, 57 | ranges **hit**; the "rising" clause **misses at s1600 by 0.2 pp** (14.7 % if no-`</think>` draws count as all-thinking) |
| 10 | cap hit by ≤ 0.5 % of arm-A draws at every checkpoint | s1600 0.63 % (11 / 1,744); others ≤ 0.46 % | **miss at s1600** |

### 11. Compute and cost (`rvc_compute.py`, `rvc_compute_ckpt.py`; job logs, metas, my rows, `~/podhours.log`)

- **New jobs** (25, every `JOB_START` / `JOB_DONE` pair; one H200 per job, TP 1): 73,103 s = **20.31 GPU-h**. The
  sampler's own `t_load + t_gen` is 20.22 h. 116,786,901 generated tokens (my sum of `n_ids`, equal to every meta's
  `gen_tokens`), 21,216 draws, 42,432 checker calls (strict + loose per draw). No training.
  - Arm A's own new draws (M-job non-reach cells + `T_s0500`): 5,632 draws, 28.6 M tokens, 4.69 GPU-h.
  - Arm B base: 10,880 draws, 60.5 M tokens, 9.83 GPU-h (the 42 IFBench reach prompts' arm-A draws are inside it).
  - Extension: 4,704 draws, 27.7 M tokens, 5.78 GPU-h.

  M jobs are split by tokens.
- **Reused stored draws** (compute belongs to olmo-ifomega / olmo-iffu): `F_dpo_ifb` 4,800 draws / 21.1 M tokens,
  `F_s0100_ifb` 2,400 / 10.4 M, `F_s0750_ifb` 2,400 / 13.6 M, `F_s2300_ifb` 2,400 / 15.6 M, `T4_s0750` 1,088 / 7.6 M,
  `T4b_s0750` 16 / 0.09 M. Of these, the cells use 218 × 16 / 8 / 8 / 8 arm-A draws and the reach prefixes.
- **Dollars** (`~/podhours.log`, 31 lines for the run): **$154.67 over 29.72 pod-hours**, within the $160 budget.
  - Sampling pods `ifc-a` … `ifc-h`: 22.41 h, about $118; secure H200 at $5.29/h after short community starts at
    $3.59/h. Job wall time is 91 % of their pod-hours.
  - Amendment 1's 17 orphaned pods: $34.84 over 7.30 h.
  - A $1.69 balance reconciliation and a $0.02 A100 tooling test.
- **Per-checkpoint compute at equal draws** (tokens per draw, all sources): arm A at s0750 / 1100 / 1600 / 2300
  generates 1.25 / 1.42 / 1.25 / 1.41 × `dpo`'s 4,448; arm-B base cells at those steps 1.42 / 1.53 / 1.31 / 1.51 ×
  s0050's. Later checkpoints use more than 1.25× the step-0 tokens per draw, as the pre-registration expected (≈ 1.4×).
  This is the models' own length under one cap; the design matches draws, not tokens.

### 12. Hygiene (`rvc_hygiene.py`, `rvc_hygiene_hit.py`)

- The bucket folder `olmo-ifcurve/` holds 2,147 objects (341.9 MB). All are in my full copy with their listed sizes,
  byte-identical to the workspace files, and the 50 MANIFEST entries' sha256 match.
- Every sample's text is in the bucket (25 new jobs). No object is over 1 GB, and there are no weight files.
- I scanned the contents of every object (gzip decompressed), plus the run's tracked code and its pre-registration:
  7 pattern hits, all false positives. Six are `AKIA…`-shaped runs inside the base64 `ids` field. One is the word
  "SECRET" in a model answer, matched only across a JSON escape. No secret.

### 13. Policy checks for a language-model run

- **Re-grade:** every row, with the upstream checkers (§2). Strict and loose agree with the run on 34,320 / 34,320.
- **Requests rebuilt from stored ids:** 1,576 prompt-token hashes match my own template + tokenisation, and five
  junctions were checked by hand (§3).
- **Same template, tokenizer, decoding and budget for every compared model:** yes (§1, §3). The only per-checkpoint
  difference is the models' own lengths. Later checkpoints use 1.25–1.53× the step-0 tokens per draw at equal draws.
- **Hand gate repeated blind:** yes (§6). It used the pre-registered reader prompt and the confirmation rules, with
  agreement reported.
- **Confirmation in both directions:**
  - The pre-registered second reads cover both the gamed items before F1 (a flip would move F1 earlier) and the
    genuine items that set F2 (a flip would move F2 later).
  - The extension cells sit only at the checkpoint before F1. That can only find earlier successes, so it works
    against "abrupt", the reading that needs evidence.
  - F25 had no pre-registered second reads; I added F25-fragile second reads.
- **"Never" with tries:** under my labels no reach prompt is unreached. Before the rule-5 pass, `ifbench_284` had 0
  genuine in 352 RL draws (8 × 32 base + 96 extension at s0750). The 95 % bounds per cell are < 2.3 % for the 0 / 128
  cell and < 8.9 % for each 0 / 32 cell. Any zero should carry its own cell's n.
- **Token budget and cut share per model:** §3.
- **RL-data overlap:** inherited scan, 0 of 218 / 0 of 48 (§1).
- **Hard constraints:** no other judge was used, my re-grade reproduces every stored grade, no secret is in the bucket
  and no weights were uploaded. **No QUARANTINE.**
