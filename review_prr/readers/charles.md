# Charles Yu: data work and how it bears on RL (reader notes)

Reader: research assistant for the peer-rl-review reviewer, 2026-10-17. Everything was read with `git -C ~/nd-rl show / ls-tree / grep / log` on `origin/charles/main` = **`297dcbd`** (2026-10-12 20:26 −0700). Nothing in ~/nd-rl was written.

**Citations.** The format is `297dcbd:<path>:L<n>`. I checked each line number with `cat -n`, `grep -n` or `sed -n`, and the quoted fragment is copied from the file. "Re-derived ✓" means I recomputed the number myself, with stdlib Python, from a committed per-item file (CSV, JSON or JSONL row file). "Not re-derivable" means the per-item output was never committed. **Review status:** only `experiments/ws3/exp-00*/review.md` exist on the branch. No experiment in this slice has a review, so every Charles number below is unreviewed executor output. The sealed-72 content is not on the branch, and I did not look for it.

**Abbreviations.**
- **Models.**
  - r8s0 = Dan `la_T1_best12_s0_r8`: sha a992485e…, 9,560,832 params, `lean_staten` proof-state format, a cap-12 Stage-1 followed by 8 rounds of T1 expert iteration.
  - r8s1 = `la_T1_best12_s1_r8` (fa9d2528…).
  - S1 = Dan `stage1_best12_s0_b1200` (2a2a9407…, 9,560,832).
  - R384 = Robbie `scale-d384-p1200_s0/pretrain.pt` (447fab6c…, 9,557,760, lean_seq).
  - R768 = Robbie `scale-d768-p1200_s0` (5297ea76…, 37,989,888).
- **Samplers.**
  - env = Dan's `state_sample.env_generate` at nd-takehome 0c492902: plain sampling, at most 48 steps and at most 256 tokens per action, no guided decoding.
  - state_eval = Dan's `state_eval.py`, which is env plus a Lean 4.34.1 gate.
  - lean_seq = Robbie's whole-proof sampling, `max_new` 400 lean_seq tokens.
- **Judge.** ndv = the pinned nd_verify called through `strict_verify.safe_verify`.

---

## 1. Inventory of documents read (newest first)

| date | commits | what I read |
|---|---|---|
| 2026-10-12 | 297dcbd, 1afc7b9, e5194f6, 3b6ec09, f521945 | **`data/pretrain_data/release_2026-10-12_textbook72_distract2/`:** README.md (only the follow-up section L240–323; the reviewer has read the rest), MANIFEST.json, metrics/summary.json. `metrics/dan.metrics.jsonl` is the same git blob (357849aa) as `experiments/pretrain-data/textbook72_distract2/run/metrics.jsonl`. **`experiments/pretrain-data/textbook72_distract2/`:** results.md (Mechanism and "Could RL teach the premise block?" sections), status.md, run/metrics_envpr.jsonl. **`data/pretrain_data/screens/`:** elementary_prem_la_T1_best12_s0_r8.json, elementary_prem_scale-d384-p1200_s0.json, elementary_forced_la_T1_best12_s0_r8.json, elementary_envpr_la_T1_best12_s0_r8.json. **Code:** `code/pretrain_data/{elementary_prem, elementary_forced, elementary_envpr, textbook72_distract_eval_dan}.py`. **Docs:** docs/pretrain-data/log.md L469–510, pools.md L730–743, questions.md L72–78 |
| 2026-10-10 | 1f2eb39 | `experiments/finetuning/edl_mock/{proposal,status}.md`; `docs/finetuning/log.md` L74–116; notes.md L77–85 |
| 2026-10-10 | 01f909a | pools.md L714–728 (the premise-stratified check); `code/pretrain_data/distract_by_premises.py`; log.md L461–467 |
| 2026-10-09 | 632a2c9, 193711e | `experiments/pretrain-data/textbook72_distract2/`: proposal.md, results.md L1–67, run/metrics.jsonl, run/robbie_d{384,768}/{metrics.jsonl,status.md} |
| 2026-10-09 | 4683f6e | **`data/pretrain_data/release_2026-10-09/`:** README.md, MANIFEST.json, screens.json, matched_distract.json. **`docs/pretrain-data/`:** pools.md (L1–220, 271–330, 400–478, 479–560, 633–743), screens_analysis.md (§1–3, §7), questions.md (all), log.md (L329–467), plan.md L14–31, hard_problems.md L1–30. **Code:** `code/pretrain_data/{screen_ckpt.py (header and arguments), screen_ckpt_dan.py, matched_distract.py}` |
| 2026-10-02 | 5d0084a | **`data/textbook_problem/release_2026-10-02/`:** README.md, MANIFEST.json, baselines.md, removed.jsonl; I also computed counts and distributions on every row file. **Eval analysis:** `experiments/textbook-problem/eval_dan_best_state/analysis/per_problem.csv` (401 rows). **Docs:** docs/textbook-problem/log.md L449–468. **Code:** `code/textbook_problem/dan_metrics.py`, `release_1002.py` (audit keys only) |
| 2026-10-02 | 6898cdc, 2c5d69c | **`experiments/textbook-problem/eval_dan_best_state/`:** proposal.md, launch.sh, results.md, and in `run_best12_r8/`: metrics.jsonl, log.txt, leak_audit.md, status.md, ckpt_sha256.txt, s0/v0.summary.json. **`experiments/textbook-problem/eval_scale_pretrain/`:** proposal.md, results.md, run_d{384,768}_s0/metrics.jsonl |
| 2026-09-30 (edited 2026-10-02 in 5d0084a) | 2d6bcd0, 08ee84c, 5d0084a | `data/textbook_problem/release_2026-09-30/{README.md, MANIFEST.json}` and its row files (distributions computed) |
| not read, or out of the slice | — | ws3 (2026-09-20..28, Charles's RL-library experiments, the only reviewed work on the branch). Headline only: "length-7 average solve rate went from 0.12 to 0.39–0.43 with GRPO, and to 0.55 with EI" (`297dcbd:docs/ws3/week_summary_2026-09-27.md:L20`); "the textbook set does not move" (L25); "Everything below is one seed per run." (L12). Also not read: ideas.md; the diversification and second-reader sheets; the `.gz` slices (not decompressed); the elementary_trace output (not committed) |

---

## 2. What Charles built and measured, and what it shows for RL

### 2.1 Textbook problem releases (data)

**release_2026-09-30** (`data/textbook_problem/release_2026-09-30/`):
- **candidate_v0, 104 problems.** "Syracuse 39, Calgary 26, Mississippi State 16; the Carnap Book 23" (README.md:L12).
- **candidate_v1, 80 problems.** "Roy, *Symbolic Logic*, section 6.2 (76); Carr, *The Natural Deduction Pack* (4)" (L13).
- **unsolved, 14 problems.** Roy 10 and Pelletier 4; the proof search found nothing within 40 lines (L14).
- **Lean.** All 184 proofs were accepted: "**Checked by Lean 4.34.1** … all 184 theorems with proofs are accepted" (L30–31).
- **Comparison table (L62–79).** The median shortest proof is "10 | 8 | 9.5" lines (sealed 72 / v0 / v1). Theorems with no premises: "16 | 13 | 30 | 9". "3 or more premises | 4 | 17 | 9 | 1".
- **Re-derived ✓ from the row files.**
  - v0: premises 0/1/2/3/4 = 13/41/33/14/3. `min_lines` median 8, mean 9.6, max 29; length bins 1/3/15/34/10/21/14/6, which matches L79.
  - v1: premises 30/13/28/8/1; median 9.5, mean 11.4, max 28; bins 0/3/8/19/18/6/9/17, which matches.
- **Caveats Charles records.** The frozen-model baseline was not run at release: "the frozen-model baseline (T5) has not been run" (L97). "5 candidate_v1 reference proofs exceed 400 tokens" (L104).

**release_2026-10-02** (`data/textbook_problem/release_2026-10-02/`) supersedes the 09-30 release. It has "412 problems in five files" (README.md:L3):
- candidate_v0: 87, "Syracuse 31, Calgary 24, Mississippi State 15; the Carnap Book 17 … Was 104" (L12).
- candidate_v1: 72, "Roy … (68); Carr … (4) … Was 80" (L13).
- hand_proved_14: Roy 10 and Pelletier 4, with "Hand-written proofs of 20 to 102 lines, verified; not minimal" (L14).
- batch3: 14, "Pelletier 1986 (4 …), forall x R³ (8), the Oxford *Logic Manual* booklet (2)" (L15).
- derived: 225, "21 task nuances built from the sets above by proof surgery" (L16).

My checks:
- The sha256 of all 8 committed files and every row count match MANIFEST.json.
- removed.jsonl, re-counted ✓: v0 11, v1 6, derived 4, batch3 1.
- Derived rows tagged `curried_twin_of`, re-counted ✓: 144 of 225.
- Lean: "Lean: 408 of 412 accepted, 4 not renderable" (L59).
- Second reader: "**Not done** for batch 3, the hand-proved 14 or the derived set" (L61–62).

**Audits.**
- **Curry-aware audit of the 10-02 sets.** The 10-02 sets were checked against the sealed 72, the test files, validation_36, heldout, transfer, rl_targets and train. Sealed matches were "removed and counted only (v0 6, v1 2, batch 3 2, derived 3)"; pool and within-release twins were removed (v0 11, v1 6, batch 3 1, derived 4) (L29–31).
- **K12 is not in that audit's pool list.**
- **Separate audit against Dan's training pools.** This one was run on the *pre-re-cut* sets (`experiments/textbook-problem/eval_dan_best_state/run_best12_r8/leak_audit.md`):
  - K12 is "155,000 generator proofs, lengths 2–12" (L8).
  - The method is "renaming class by `canonical_theorem` or `canon_key`" (L15). The audit code is not committed.
  - Hits in a K12 class: v0 2, lean_v2 3, derived_plain 1, textbook72 1. Hits in rl_targets: v0 1, v1 1. Hits in transfer_v1: v1 1 (L18–26).
  - Verdict: "overlap is at most 3 problems in any set" (L28).

**Premise and length distributions of the 10-02 rows** (my computation from the prompts and `reference_lines`):

| set | n | premises 0/1/2/3/≥4 | reference lines, median (max) |
|---|---|---|---|
| candidate_v0 | 87 | 4/36/31/13/3 | 9 (29) |
| candidate_v1 | 72 | 24/12/27/8/1 | 10 (28) |
| hand_proved_14 | 14 | 9/3/1/1/0 | 45.5 (102), range 20–102 |
| batch3 | 14 | 3/2/1/7/1 | 10.5 (19) |
| sealed 72 (Charles, aggregate) | 72 | 16/30/22/3/1 | median 10 (09-30 README L64) |

The sealed-72 premise counts come from "The 72 have 0 / 1 / 2 / 3 / 4 premises for 16 / 30 / 22 / 3 / 1 problems" (`297dcbd:experiments/pretrain-data/textbook72_distract2/proposal.md:L15`).

### 2.2 Model scores on the textbook sets (2026-10-02)

**Pretrains (R384, R768).**
- Scorer: `eval_ckpt.py`, with "k = 32, temperature 1.0, max_new 400 lean_seq tokens, seed 0, batch 256" (`297dcbd:experiments/textbook-problem/eval_scale_pretrain/proposal.md:L36`).
- Judge: ndv only. "Lean is not consulted." (L25)

**Dan's RL checkpoints (r8s0, r8s1).**
- Scorer: Dan's `state_eval.py --k 32 --temperature 1.0 --batch 256 --seed 0`, which samples through env ("max 48 steps, 256 tokens per action") "and gates through Lean 4.34.1" (`297dcbd:experiments/textbook-problem/eval_dan_best_state/proposal.md:L24–26`).
- In launch.sh the s0/s1 labels are **checkpoint training seeds**, and both use sampling `--seed 0` (launch.sh:L15–16). Seed 2 was "cancelled by request, never written" (`run_best12_r8/status.md:L3`).
- The avg solve rate is "the mean over problems of n_ok / n_tried as Lean counted it". ndv only re-judges the distinct accepted proofs (`297dcbd:code/textbook_problem/dan_metrics.py:L7–9`). Two Lean/ndv disagreements were kept in the counts (`experiments/textbook-problem/eval_dan_best_state/results.md:L81`).

**Which sets were scored.**
- These were the sets "as they stood before the curry-aware re-cut (candidate_v0 104, candidate_v1 80)" (`297dcbd:data/textbook_problem/release_2026-10-02/baselines.md:L3`).
- The scored batch3 is "21 incl. the 4 hand-proved" (baselines.md:L10). My check: 4 batch3 input prompts are exact duplicates of hand14 input rows.

**Headline numbers.** They are in baselines.md L7–14 and are re-derived in §3.
- All six RL columns reproduce from per_problem.csv (v0, v1, hand14, batch3, lean_v2, both checkpoints).
- derived_plain reproduces only after the structural check. Before it the counts are 70 and 68; `struct_fail_rows` 1 and 2 bring them to 69 and 66.
- Robbie's columns reproduce from `run_d*_s0/metrics.jsonl`.

**Per-problem findings.** Charles states them in `297dcbd:docs/textbook-problem/log.md:L464`; I re-derived all of them ✓ from per_problem.csv (269 scraped problems):

| finding | value |
|---|---|
| Problems solved by RL (either checkpoint) | 183 |
| Problems solved by either pretrain | 51 (R384 alone 44; Charles's "pretrain solved 44 of 269" means R384 only) |
| Solved by a pretrain but not by RL | 0 |
| RL solved, by reference length | ≤10 lines 143/156; 11–13 lines 27/43; 14–20 lines 12/36; 21+ lines 1/31 |
| RL solved, by nesting depth | depth 2: 60/82; depth 3: 13/37 (plan.md:L24) |
| Four-premise problems | **0/7** for all four checkpoints. They are v0 3, v1 1, batch3 1, lean_v2 2, with references of 5–15 lines |
| RL's shortest accepted proof ≤ the reference | 132 of 183 |

**Padding and containment.**
- RL proofs are padded: "mean written length 13.4 lines against reference minima of 5–10" (`experiments/textbook-problem/eval_dan_best_state/results.md:L70–71`). This comes from 20 samples Charles read.
- "every problem a pretrain solved the RL model solved" (log.md:L459). The pretrain here is Robbie's lean_seq model, not Dan's Stage-1. So this is not a comparison between RL and its own base.

**Dan's own figure, quoted by Charles and not re-measured:** "textbook72 pass@256 IQM 51.7 / 72" (eval_dan_best_state/proposal.md:L15–16).

### 2.3 Pretrain-data release 2026-10-09: pools and screens

**Status.** "**50 candidate pools built and screened without training; no pool has been trained on; no GPU spent.**" (`297dcbd:data/pretrain_data/release_2026-10-09/README.md:L4`).

**Format.** Every pool is "K12 with a slice replaced" (L18). Only the new records are shipped. `assemble.py` rebuilds each pool from Dan's K12 and checks the result against a hash (L18–26).

**K12 facts (Dan's Stage-1 data), from `docs/pretrain-data/pools.md`.**
- Premises {0: 9263, 1: 40330, 2: 74839, 3: 30568}, so never four. Lines run 2–12, flat. Depth is at most 2 (L90).
- "**K12's long half is 89 % padding**" (L44).
- "unused-premise share 0.0000" (L72).

**Published slices and the reason Charles gives for each (README.md:L39–46).**

| slice | size | content and stated reason |
|---|---|---|
| `k12_prem4_10`, `_1e2`, `_1e3` | 15,500 / 155 / 15 | Generator problems with 4–5 premises. MANIFEST.json L24–35 shows them almost all 10–12 lines long ("12": 7050; by_prem "4": 15076, "5": 424) |
| `k12_distract10`, `_30`, `k12_minimal_distract10` | 15,500 / 46,500 / 15,500 | K12 problems with 1–2 unused premises added. The distract10 slice has premise counts 1/2/3/4/5 = 662/3,169/6,109/4,458/1,102 (MANIFEST.json L92–97), so **36 % of its rows have four or more premises** |
| `k12_joins1`, `k12_joins10`, `k12_minimal_joins10` | — | Built from 12,295 join problems |
| `k12_jdist10`, `k12_jsubst10`, `k12_long16_10` | — | Joins plus distractors; joins at wider formula width; 13–16-line generator proofs |
| `k12_dial_1e1` … `_1e4` | 15,500 / 1,550 / 155 / 16 | ↔-elimination problems. dial_1e1 is "source": 1114 plus "perms": 14386 (pools.md:L170) |
| `k12_minimal` | 84,700 shortened rows | "n_shorter": 84700 (MANIFEST.json:L14) |

**Screens.**
- **Data screens (no model).** The predictor-perplexity screen was withdrawn because it failed the `k12_wrong100` negative control: "fails its negative control and is withdrawn as a loss proxy" (pools.md:L188).
- **Checkpoint screens on R384.** 160 prompts × 32 samples, T 1.0, lean_seq `max_new` 400, judged by ndv (`code/pretrain_data/screen_ckpt.py:L10`, arguments at L195–198).
- **Checkpoint screens on S1 and r8s0.** At most 128 prompts × 32 samples, env at "T 1.0, max 48 steps, 256 action tokens", "judged by the PINNED nd_verify … not by Dan's Lean judge" (`code/pretrain_data/screen_ckpt_dan.py:L8–10`).
- The README states: "One checkpoint per screen, no seeds." (README.md:L67)

**README screen table (L69–80).** I checked it against screens.json: every published-pool cell matches screens.json after rounding. The K12 row (L71: "0.51 | 0.89 | 0.98 | 1.00") is not in screens.json, where every pass@32 for k12 is `null` (screens.json:L8, L11). It comes from the references quoted in pools.md:L412–413 and L460. Examples:
- distract10: 0.55 (R384), 0.63 (S1), 0.69 (r8s0) (L73).
- joins10: 0.19, 0.36, 0.69 (L74).
- dial_1e1: 0.26, 0.35, 0.77 (L79).
- prem4_10: 0.00 on R384; never screened on Dan's checkpoints (L72; screens.json L31–33 are `null`).

**What eight RL rounds did, per slice (S1 → r8s0).** Same screen protocol (pools.md:L464–476; screens_analysis.md:L222–238):

| slice | pass@32, S1 → r8s0 | Δ |
|---|---|---|
| K12 rows | 0.98 → 1.00 (pass@1 0.67 → 0.94) | — |
| dial_1e1 | 0.35 → 0.77 | +0.41 |
| joins10 | 0.36 → 0.69 | +0.33 |
| sub10 | 0.54 → 0.84 | +0.30 |
| minimal_joins10 | 0.30 → 0.55 | +0.26 |
| joins1 | 0.45 → 0.68 | +0.23 |
| pairs1 | 0.63 → 0.85 | +0.22 |
| tail10 | 0.87 → 1.00 | +0.13 |
| distract10 | 0.63 → 0.69 | +0.05 |
| aux10 | 0.00 → 0.00 | 0 |

- For the K12 rows Charles writes "RL sharpened in-distribution without changing pass@32" (`docs/pretrain-data/log.md:L338–339`).
- I re-derived ✓ both Spearman figures from the pools.md table. R384 against S1 pass@32 gives ρ = 0.93 (n 14). Δ against S1 pass@32 gives ρ = −0.89 (n 11, excluding aux10). Charles has the same numbers at screens_analysis.md:L209–210 and L242–243.

### 2.4 The "premise-count wall" (2026-10-09 to 10-12)

**(a) Matched distractor check, on R384 only** (`code/pretrain_data/matched_distract.py`). 200 random distract10 slice rows were scored against their own originals.
- **Re-derived ✓ from `release_2026-10-09/matched_distract.json` (L1):**
  - distracted pass@32 0.53 against 0.915 for the originals;
  - 105 solved both ways, 78 only undistracted, 1 only distracted, 16 neither;
  - one distractor: 0.71 against 0.93; two distractors: 0.20 against 0.89.
  - Charles has these at pools.md:L694–696.
- **The split by total premise count is not re-derivable.** The table is 4 premises: n 50, 0.00 against 0.86 for the originals; 5 premises: n 21, 0.00 against 0.76 (pools.md:L703–704). The JSON has no premise field, and the committed script does no premise split (it dumps `n, hd, hb, k, lines`, matched_distract.py:L48). This table is the source of the "0 of 71" in README.md:L82–84.

**(b) Premise-stratified check, on three models** (`code/pretrain_data/distract_by_premises.py`, 2026-10-10).
- Design: 120 rows at 4 premises, 60 at 5 and 120 at ≤3, drawn with row-sample seed 1. Pass@32, T 1.0, judged by ndv.
- Result: "0 of 180 four-plus prompts on every model, 0 of 5,760 samples each" (pools.md:L725).
- At ≤3 premises (pools.md:L721–723):

| model | solved of 120 | per-sample rate |
|---|---|---|
| R384 | 101 | 0.55 |
| S1 | 112 | 0.48 |
| r8s0 | 119 | 0.85 |

- The `distract_by_prem_*.json` outputs are **not committed**, so this is not re-derivable.

**(c) Sealed 72 with two unused premises each** (textbook72_distract2; k 32, T 1.0, seed 0, ndv; n = 71; 25 problems cross to ≥4 premises).
- r8s0: 49/71 → 28/71; the crossing problems go 17 → 0; the problems staying at ≤3 premises go 32 → 28 (`experiments/pretrain-data/textbook72_distract2/run/metrics.jsonl:L2`).
- S1: 25 → 12; crossing 8 → 0 (L1).
- Robbie's models: R384 12/72 → 5/71; R768 11/72 → 6/71 (`run/robbie_d{384,768}/metrics.jsonl`:L1–2).
- Every model is at **0 on the crossing problems**, inside the pre-registered "0–3" (proposal.md:L60).

**(d) Mechanism: a trivial premise ladder** (`data/pretrain_data/screens/elementary_prem_*.json`). Re-derived ✓:

| model | 2 premises | 3 premises | 4 premises | 5 premises |
|---|---|---|---|---|
| r8s0 | 154/160 | 111/128 | 0/320 | 0/64 |
| R384 | 115/160 | 90/128 | 0/320 | 0/64 |

- **r8s0 failures.** In the model-written-block arm of the envpr run, all 384 samples at four or five premises die at the environment's "PR position" check (elementary_envpr_la_T1_best12_s0_r8.json:L313, `"PR position": 384`).
- **R384 failures.** Over the 384 samples at four or five premises, 258 are "premise block does not match declared premises". The rest are lean_seq parse failures (see §5, item 9).

**(e) Can RL reach it?** All measured on r8s0 (`experiments/pretrain-data/textbook72_distract2/results.md`):
- The round-8 training mix has "89,724 rows … 14,279 / 37,807 / 28,454 / 9,184 rows at 0 / 1 / 2 / 3 premises and none at four or more" (L107–108). This is Charles reading Dan's bucket; I did not re-check it.
- Teacher-forced, the whole premise block has probability 3.99e-24 under canonical names with base 0. The product of shares is 7.66e-15 (elementary_forced JSON L133–134).
- 0 of 1,024 samples verify at T 1.0, and 0 of 1,024 at T 1.5 (JSON L314, L328).

### 2.5 "The environment writes the premise block" diagnostic (2026-10-12)

**Code.** `code/pretrain_data/elementary_envpr.py` is Charles's re-implementation of env ("mirrors state_sample.env_generate", L34). The environment applies h1..hn before the model acts. The judge is **ndv, not Lean**: "every finished proof is judged by the pinned verifier" (L3; `safe_verify` at L91). Dan's environment still applies its own action checks during sampling.

**Where each per-set number comes from.**

| set | env-written block | baseline it is compared with |
|---|---|---|
| Elementary ladder | 153/160, 106/128, **252/320**, **57/64**. Source: `data/pretrain_data/screens/elementary_envpr_la_T1_best12_s0_r8.json`, key `ladder_env_premises`. Re-derived ✓ | Model-written arm `ladder_model_premises` (JSON L161 onward), re-run by the same re-implementation. It reproduces the env-based elementary_prem JSON exactly, problem by problem, on all 21 problems (my check; a good fidelity control) |
| Generator distract10 (stratified sample) | 4 premises: 118/120, pass@1 0.828 (JSON L342–347). 5 premises: 55/60, pass@1 0.741 (L349–354). ≤3 premises: 120/120. Re-derived ✓ | The 2026-10-10 model-written run (0/180). It exists only in pools.md:L723, because its JSON is not committed |
| Distracted 72 | Original 48/71, distracted 38/71, crossing 16 → 10 (`experiments/pretrain-data/textbook72_distract2/run/metrics_envpr.jsonl:L1`). Aggregates only; the per-problem hits are in a gitignored file | `run/metrics.jsonl:L2` (49 → 28; crossing 17 → 0). That baseline comes from a different script (`textbook72_distract_eval_dan.py`) and a different run |

- The release's `metrics/` folder contains **no** envpr file. The README's env-written rows (README.md:L269, L276) are backed only by the experiment folder.
- Charles logs this as a protocol change and uses it as a diagnostic only. The default followed is "diagnostic only; no training run and no headline number uses it" (`docs/pretrain-data/questions.md:L77–78`).

### 2.6 Was any slice used to train a Stage-1 or RL model?

**No.**
- "Not done: any Stage-1 run, any ladder" (`data/pretrain_data/release_2026-10-09/README.md:L89`).
- "Nothing here has been trained on." (L102)
- Questions.md item 10 again says no training run (questions.md:L77–78).
- The only prediction on record is "distracted-72 ≥ 40 of 71 after the ladder, against 28 now" for a Stage-1 trained on the premise pool (`docs/pretrain-data/log.md:L458–459`).

### 2.7 Post-10-02 items not in the brief

**`experiments/finetuning/edl_mock` (2026-10-10).** A prequential excess-description-length (EDL) measurement on Dan's base and r2, r4, r8 seed-0 checkpoints, using "never-solved" `rl_targets` proofs taken from the seed-1 ladder.
- Status: "RUNNING 2026-10-10T23:51:48Z" (status.md:L3). **No results are committed.**
- Scratch timing figures (unreviewed, not pre-registered): "Base on held-out proofs of theorems it never solved: 0.081 nats/token" and "≈ 29 bits per whole never-found proof before training. The elicitation gap per proof is a few bits." (`docs/finetuning/log.md:L91–93`).
- Its proofs are Lean-judged and "not yet re-judged by the pinned verifier" (L84–85).
- This bears directly on the question of whether RL creates new capability or elicits rare behaviour, but it has no result yet.

**Other post-10-02 pools.** The hard-problem gap analysis (hard_problems.md), the § K pools and the atom pools (pools.md L479–556) are data-only, screened on R384 only. They contain no numbers on Dan's models beyond those above.

### 2.8 Reading for RL (my synthesis; one seed throughout)

1. **The only Stage-1-versus-RL comparison on textbook problems under one protocol.**
   - Setup: env sampler, k 32, T 1.0, ndv judge, n = 71 sealed problems, one seed.
   - Result: any-of-32 goes **25 → 49** and the per-sample rate **0.124 → 0.378** (run/metrics.jsonl L1–2).
   - At k = 32 this cannot separate sharpening from new coverage, because the base was never sampled at large k.
2. **On generator slices, RL mostly sharpens in-distribution and raises out-of-distribution coverage at k 32.**
   - K12 rows: pass@1 0.67 → 0.94 while pass@32 stays at 0.98 → 1.00.
   - Slices: pass@32 rises +0.22 to +0.41 where S1 sat at 0.30–0.63.
   - The gain is anti-correlated with S1's own pass@32 (ρ −0.89).
3. **The four-premise zero is an interface artefact, not missing reasoning.**
   - Under the standard interface no model ever writes a fourth premise line: 0/7 textbook problems, 0/25 crossing problems, 0/180 generator prompts, 0/320 trivial prompts.
   - The RL training mix never poses such a prompt, and sampling never yields a reward (0/2,048). So expert iteration cannot discover it.
   - Once the environment writes the block, the same r8s0 solves 118/120 at four premises with no training.
   - For the research question, this is a case where a hard zero under the eval interface is neither "absent capability" nor "elicitable by RL". A non-RL interface change unlocks it.
4. **The "RL does not lift distractors" reading is superseded.**
   - The distract10 slice is 36 % four-plus-premise rows, and those are unsolvable by the PR-block habit.
   - At ≤3 premises, RL lifts distracted problems from 112 to 119 of 120 solved, and the per-sample rate from 0.48 to 0.85.
5. **Reach tracks the Stage-1 data's limits.**
   - Lengths: the knee is at about 12 reference lines, which is K12's cap, and only 1/31 problems at 21+ lines are solved. That single solve is 1/32 on r8s1 alone.
   - Depth: 3+ is rare in K12, and the RL solve rate drops at depth 3.
6. **None of the data hypotheses has been tested.** No pool has been trained on.

---

## 3. Headline-number table

The "reviewed?" column says "no" throughout, because there is no review.md in the slice. It also records whether I could re-derive the number.

| value + metric | set (n) | k | T | sampler / interface | judge | model | seeds | reviewed? | citation + quote |
|---|---|---|---|---|---|---|---|---|---|
| 49/72 solved (avg 0.371) | sealed textbook72 (72, aggregate) | 32 | 1.0 | state_eval (env, 48 steps, 256 tok/action, batch 256) | Lean 4.34.1 gate; ndv re-check: 1 disagreeing proof | r8s0 (Dan, 9.56M, lean_staten) | ckpt s0, sampling seed 0 | no; consistent with metrics.jsonl L7 | `297dcbd:experiments/textbook-problem/eval_dan_best_state/results.md:L27` "\| textbook72 (sealed; aggregate only) \| 72 \| 0.371 \| 0.088 \| 49 (68%) \|" |
| 47/72 (avg 0.378) | textbook72 (72) | 32 | 1.0 | state_eval | Lean | r8s1 | ckpt s1, sampling seed 0 | no | `297dcbd:experiments/textbook-problem/eval_dan_best_state/run_best12_r8/metrics.jsonl:L14` "\"avg_solve_rate\": 0.378 … \"any_of_k\": 47" |
| 76/104 (0.341) and 73/104 (0.344) | candidate_v0, pre-re-cut (104) | 32 | 1.0 | state_eval | Lean | r8s0 / r8s1 | 2 ckpt seeds | no; **re-derived ✓** (per_problem.csv) | `297dcbd:data/textbook_problem/release_2026-10-02/baselines.md:L7` "\| candidate_v0 \| 104 \| 0.111 / 22 \| 0.086 / 17 \| 0.341 / 76 \| 0.344 / 73 \|" |
| 49/80 (0.356) and 50/80 (0.362) | candidate_v1, pre-re-cut (80) | 32 | 1.0 | state_eval | Lean | r8s0 / r8s1 | 2 | no; re-derived ✓ | baselines.md:L8 "\| candidate_v1 \| 80 \| 0.050 / 11 \| 0.058 / 11 \| 0.356 / 49 \| 0.362 / 50 \|" |
| 10/21 and 12/21; hand14 0/14 | batch3 (21, includes 4 hand14 duplicates); hand14 (14) | 32 | 1.0 | state_eval | Lean | r8s0 / r8s1 | 2 | no; re-derived ✓ | baselines.md:L10 "\| batch3 (21 incl. the 4 hand-proved) \| 21 \| 0.000 / 0 \| 0.002 / 1 \| 0.298 / 10 \| 0.327 / 12 \|" |
| 22/104 (0.111); 12/72 (0.104) | v0 (104); textbook72 (72) | 32 | 1.0 | lean_seq, max_new 400 | ndv only | R384 (Robbie, 9.56M) | 1 | no; matches run metrics | `297dcbd:experiments/textbook-problem/eval_scale_pretrain/results.md:L20` "\| 104 \| 0.111 \| 0.052 \| 22 (21%) \|" and L26 "\| 72 \| 0.104 \| 0.064 \| 12 (17%) \|" |
| 17/104 (0.086); 11/72 (0.129) | v0; textbook72 | 32 | 1.0 | lean_seq 400 | ndv | R768 (38.0M) | 1 | no | eval_scale_pretrain/results.md:L95 "\| v0 \| 104 \| 0.086 \| 0.045 \| 17 (16%) \|" and L101 "\| textbook72 \| 72 \| 0.129 \| 0.073 \| 11 (15%) \|" |
| 0/7 four-premise problems solved | scraped sets (7 of 269) | 32 | 1.0 | state_eval and lean_seq | Lean / ndv | r8s0, r8s1, R384, R768 | 2 + 1 + 1 | no; **re-derived ✓** | `297dcbd:data/pretrain_data/release_2026-10-09/README.md:L39` "the RL model fails all 7 four-premise textbook problems" |
| RL solved: ≤10 lines 143/156; 11–13: 27/43; 14–20: 12/36; 21+: 1/31 | scraped (269) | 32 | 1.0 | state_eval | Lean | r8s0 ∪ r8s1 | 2 | no; re-derived ✓ | `297dcbd:docs/textbook-problem/log.md:L464` "RL holds 79–100 % through 10 reference lines, 55–67 % at 11–13, 12 of 36 at 14–20, 1 of 31 at 21+" |
| RL 183 solved, pretrains 51, pretrain-only 0 | scraped (269) | 32 | 1.0 | mixed | mixed | union of 2 RL ckpts vs union of R384 and R768 | — | no; re-derived ✓ (Charles's "44" is R384 alone) | log.md:L464 "pretrain solved 44 of 269 scraped problems, RL 183 (either seed), pretrain-only 0" |
| 25/71 → 12/71 (avg 0.124 → 0.040); crossing 8 → 0 | sealed 72 original → distracted (71) | 32 | 1.0 | env | ndv | S1 (Dan Stage-1, 9.56M) | 1 | no; aggregates only | `297dcbd:experiments/pretrain-data/textbook72_distract2/run/metrics.jsonl:L1` "\"original\": {\"avg_solve_rate\": 0.1241, \"any_of_k\": 25" |
| 49/71 → 28/71 (0.378 → 0.140); crossing 17 → 0; staying 32 → 28 | same (71) | 32 | 1.0 | env | ndv | r8s0 | 1 (s1 and s2 never run) | no | run/metrics.jsonl:L2 "\"crossing_to_4plus\": {\"n\": 25, \"orig_solved\": 17, \"dist_solved\": 0}" |
| 12/72 → 5/71; 11/72 → 6/71 | same | 32 | 1.0 | lean_seq 400 | ndv | R384; R768 | 1 each | no | `297dcbd:experiments/pretrain-data/textbook72_distract2/run/robbie_d384/metrics.jsonl:L1–2` "\"any_of_k\": 12" / "\"any_of_k\": 5" |
| env-written block: 48/71 → 38/71 (0.374 → 0.210); crossing 16 → 10 | same | 32 | 1.0 | Charles's re-implementation of env; the environment applies h1..hn | ndv | r8s0 | 1 | no; aggregates only | `297dcbd:experiments/pretrain-data/textbook72_distract2/run/metrics_envpr.jsonl:L1` "\"distract2\": {\"avg_solve_rate\": 0.2104, \"any_of_k\": 38" |
| distracted pass@32 0.53 against 0.92 for the originals; 4–5 total premises 0/71 against 0.83 | matched distract10 rows (200) | 32 | 1.0 | lean_seq 400 | ndv | R384 | 1 | no. Overall split re-derived ✓; **the premise split is not re-derivable** | `297dcbd:docs/pretrain-data/pools.md:L694` "Paired: distracted pass@32 0.53 vs 0.92"; L703 "\| 4 \| 50 \| **0.00** \| 0.86 \|" |
| 0/180 at four-plus premises; ≤3 premises: 101 / 112 / 119 of 120 | stratified distract10 (300) | 32 | 1.0 | lean_seq (R384) / env (Dan) | ndv | R384, S1, r8s0 | 1 each | no; **not re-derivable** (JSONs not committed) | pools.md:L725 "0 of 180 four-plus prompts on every model, 0 of 5,760 samples each" |
| 118/120 at 4 premises (pass@1 0.828); 55/60 at 5 (0.741) | same stratified sample, block written by the environment | 32 | 1.0 | re-implemented env | ndv | r8s0 | 1 | no; **re-derived ✓** | `297dcbd:data/pretrain_data/screens/elementary_envpr_la_T1_best12_s0_r8.json:L344` "\"solved\": 118," and L351 "\"solved\": 55," |
| 154/160, 111/128, **0/320**, 0/64 samples verified | elementary ladder (21 problems) | 32 | 1.0 | env | ndv | r8s0 | 1 | no; re-derived ✓ | `297dcbd:experiments/pretrain-data/textbook72_distract2/results.md:L78` "\| Dan r8 s0 \| 154 / 160 \| 111 / 128 \| **0 / 320** \| 0 / 64 \|" |
| 115/160, 90/128, 0/320, 0/64 | elementary ladder | 32 | 1.0 | lean_seq | ndv | R384 | 1 | no; re-derived ✓ | results.md:L79 "\| Robbie d384 base \| 115 / 160 \| 90 / 128 \| **0 / 320** \| 0 / 64 \|" |
| env-written block: 153/160, 106/128, 252/320, 57/64 | elementary ladder | 32 | 1.0 | re-implemented env | ndv | r8s0 | 1 | no; re-derived ✓ | results.md:L130 "\| environment writes the block \| 153 / 160 \| 106 / 128 \| **252 / 320** \| **57 / 64** \|" |
| p(block) 3.99e-24; share product 7.66e-15; 0/1,024 at T 1.0 and 0/1,024 at T 1.5 | P, Q, R, S ⊢ P | 1,024 (search) | 1.0 / 1.5 | teacher-forced with canonical names, base 0; env for the search | ndv | r8s0 | 1 | no; matches JSON | `297dcbd:data/pretrain_data/screens/elementary_forced_la_T1_best12_s0_r8.json:L133` "\"p_block\": 3.992894588593074e-24"; L314 and L328 "\"verified\": 0" |
| pass@32 S1 → r8s0: dial_1e1 0.35 → 0.77; joins10 0.36 → 0.69; distract10 0.63 → 0.69; tail10 0.87 → 1.00 | slice rows (≤128 sampled prompts each) | 32 | 1.0 | env | ndv (not Lean) | S1, r8s0 | 1 checkpoint each | no; screens.json matches for the published pools | pools.md:L474 "\| k12_distract10 \| … \| 0.6328 \| 0.585 \| 0.6875 \| +0.05 \| 0.55 \|"; L473 "+0.41" |
| K12 rows: pass@1 0.67 → 0.94, pass@32 0.98 → 1.00 | 128 sampled K12 training rows | 32 | 1.0 | env | ndv | S1 → r8s0 | 1 | no | `297dcbd:docs/pretrain-data/log.md:L338–339` "Stage-1 K12 loss 0.067, pass@1 0.67, pass@32 0.98; round-8 0.057 / 0.94 / 1.00" |
| R384 pass@32: prem4 0.00 at every fraction; distract10 0.55; joins10 0.19; jdist10 0.05; long16 0.69 | ≤160 prompts per slice | 32 | 1.0 | lean_seq 400 | ndv | R384 | 1 | no; matches screens.json | `297dcbd:data/pretrain_data/release_2026-10-09/README.md:L72` "\| `k12_prem4_10` \| 0.69 \| 0.00 \| — \| — \|" |
| Spearman ρ 0.93 (R384 vs S1, n 14); ρ −0.89 (Δ vs S1 pass@32, n 11) | the 14 slices above | — | — | — | — | — | — | no; **re-derived ✓** from pools.md L464–477 | `297dcbd:docs/pretrain-data/screens_analysis.md:L210` "Dan's Stage-1 pass@32 is 0.93"; L243 "(ρ −0.89, n = 11)" |
| pass@256 IQM 51.7/72 (Dan's figure, quoted) | textbook72 | 256 | (Dan's) | (Dan's) | (Dan's) | r8 | (Dan's) | Charles calls it "unreviewed" | `297dcbd:experiments/textbook-problem/eval_dan_best_state/proposal.md:L15–16` "Dan's own read-outs (unreviewed, `run_best_state.md`): textbook72 pass@256 IQM 51.7 / 72" |

---

## 4. Protocol notes for every number on Dan's models

Our usual protocol is Lean alone, k 256, T 0.8, in both plain and guided sampling. Charles never uses k 256, T 0.8 or guided decoding. He uses the Lean judge only in the 2026-10-02 evaluation.

| experiment (script) | Dan checkpoints | k / T | sampler | judge | limits | seeds | differences from our protocol |
|---|---|---|---|---|---|---|---|
| eval_dan_best_state (`state_eval.py`, Dan's branch 0c492902) | r8s0, r8s1. s2 was fetched but cancelled | 32 / 1.0 | env, plain, batch 256 | Lean 4.34.1 in the loop. The rate is n_ok/n_tried as Lean counted. ndv re-checks only the distinct accepted proofs, and the 2 disagreements stay counted | 48 steps, 256 tokens per action | checkpoint seeds 0 and 1; sampling seed 0 for both | k 32 instead of 256, T 1.0 instead of 0.8, no guided arm. v0 and v1 are the pre-re-cut 104/80 sets. Laptop CPU |
| Pool screens (`screen_ckpt_dan.py`) | S1, r8s0 | 32 / 1.0 | env | ndv, explicitly "not by Dan's Lean judge" | 48 / 256 | seed 0; ≤128 prompts per slice from one RNG shared across pools | Judge is ndv. pass@1 means the per-sample rate. Resolution is 1/128. Prompt draws are probably unpaired between S1 and r8s0 for some slices (§5, item 13) |
| textbook72_distract2 (`textbook72_distract_eval_dan.py`) | S1, r8s0. s1 and s2 never run | 32 / 1.0 | env | ndv | 48 / 256 | 1 | Judge is ndv. n = 71: one sealed problem was dropped from the distracted set |
| distract_by_premises | S1, r8s0 | 32 / 1.0 | env (through `textbook72_distract_eval_dan.pass_hits`) | ndv | 48 / 256 | sampling seed 0; row-sample seed 1, paired across models | Judge is ndv; the per-row outputs are not committed |
| elementary_prem | r8s0 | 32 / 1.0 | env | ndv | 48 / 256 | 1 | 21 hand-made non-sealed problems |
| elementary_forced | r8s0 | teacher-forced; search at 1,024 samples, T 1.0 and 1.5 | env, with canonical names and base 0 for the forced probabilities | ndv | 48 / 256 | 1 | The absolute probabilities depend on the name base. Charles says the "shares … are the robust numbers" (`experiments/pretrain-data/textbook72_distract2/results.md:L153–154`) |
| elementary_envpr | r8s0 | 32 / 1.0 | Charles's re-implementation of env, with the environment writing the premise block | ndv | 48 / 256 | seed 0 | **This changes the task the model is given.** Not comparable with any standard-protocol number (questions.md:L77–78) |
| edl_mock (finetuning) | S1 and the r2, r4, r8 seed-0 ladder checkpoints | — | fine-tunes on Dan's seed-1 `found_8` proofs | the proofs are Lean-judged; the ndv re-judge is still pending | — | — | No results committed |

**Notes.**
- **The 48-step cap.** In the hand14 run, 6 of the 14 hand proofs are longer than 48 lines. In practice the cap barely binds: on r8s0, hand14 ended with `"step_cap": 5` out of 448 samples (`297dcbd:experiments/textbook-problem/eval_dan_best_state/run_best12_r8/log.txt:L9`). The failures are syntax errors and Lean rejections.
- **The judge only mattered at the margin.** Lean and ndv disagree on 1–2 proofs per set, never resolved: "Pinned-verifier vs Lean: 1–2 disagreeing proofs per set (Dan's loose ⊥E rendering class)" (`297dcbd:docs/finetuning/notes.md:L84`).

---

## 5. Suspicious items

1. **Judge mislabelled in baselines.md.**
   - L3 says "every proof judged by the pinned nd_verify through strict_verify". But the RL columns' rates are Lean's `n_ok/n_tried`, and ndv re-checks only distinct accepted proofs, without changing any rate (`297dcbd:code/textbook_problem/dan_metrics.py:L7–9`).
   - eval_dan_best_state/results.md:L91–92 also says "avg solve rate is per the pinned re-judging in `dan_metrics.py`", which contradicts both its own L11 ("as Lean counted") and the code.
   - So the RL columns are Lean-judged while the pretrain columns are ndv-judged, under different interfaces.
2. **The pretrain and RL columns sit side by side but are not comparable.**
   - Pretrains: lean_seq whole proofs, 400 tokens, ndv. RL: state environment, 48 × 256 tokens, Lean.
   - Charles disclaims any comparison (`experiments/textbook-problem/eval_dan_best_state/results.md:L79–80`). Yet his log turns it into "3–6× more problems solved at least once" (`docs/textbook-problem/log.md:L459`). Robbie's models are also not the RL model's base.
3. **The scored sets are not the released sets.**
   - The 2026-10-02 scores are on v0 104 and v1 80 (baselines.md:L3). Those sets include the 6 + 2 problems the curry-aware audit later removed as sealed-72 twins (release_2026-10-02/MANIFEST.json L5–10), plus 17 pool or within-release twins.
   - The scored batch3 (21) contains 4 exact duplicates of hand14 rows (my check), so "269 scraped problems" double-counts 4.
   - None of this is a training leak. It does mean v0/v1 and the 72 are not disjoint under the curry rule.
4. **The 09-30 README is internally stale and was edited after publication.**
   - "194 propositional natural deduction problems … 184 with a verified reference proof and 14 valid problems" (`release_2026-09-30/README.md:L4–5`) adds up to 198. Commit 5d0084a's diff changed "10" to "14" and left "194" alone.
   - The 4 Pelletier problems come from a journal paper, not a textbook.
   - The release "stays as published" (10-02 README:L6), yet its unsolved.jsonl went from 10 to 14 rows in that same commit.
   - Its no-overlap claim (L5–6) is superseded by the curry-aware audit.
5. **"Same evaluators" is not literally true.**
   - The distract2 results say the original-set numbers "reproduce the earlier figures under the same evaluators (… r8 seed 0 49 of 72 on 2026-10-02 with Lean gating)" (`experiments/pretrain-data/textbook72_distract2/results.md:L47–48`). The 10-12 README says "so the judge did not move the number" (`data/pretrain_data/release_2026-10-12_textbook72_distract2/README.md:L322–323`).
   - The 10-09 run used env with ndv on 71 problems. The 10-02 run used state_eval with the Lean gate on 72. Equal counts on different sets, runs and judges do not isolate the judge's effect.
6. **Superseded readings that were never corrected.**
   - The 10-09 README:L40 still says distract10 is "the one slice eight RL rounds do not lift". questions.md:L54–57 and screens_analysis.md:L242–245 keep "Premise selection among distractors is the thing the ladder does not learn".
   - The later stratified check shows the deficit is the four-plus-premise rows (36 % of the slice), which every model fails. At ≤3 premises RL goes 112 → 119 of 120 (pools.md:L722–723).
   - Charles notes this only in passing: "the round-8 model's slice figure came from a draw with fewer four-plus rows" (L725–726).
7. **Overstated ranges in the 10-09 README.**
   - "every other slice +0.2 to +0.4" (L40): dial_1e1 is +0.41, tail10 +0.13, and the ceiling pools +0.01 to +0.02 (pools.md:L464–476).
   - "base pass@32 0.14–0.19, coverage 0.74–0.76" for the join pools (L41): k12_joins1 is 0.20 / 0.69 (screens.json:L91, L96).
   - The README says "Dan's two checkpoints on 10" pools; the Stage-1 table has 14 rows.
8. **Numbers with no committed per-item source.**
   - The K12 row of the screen table (README:L71) has `null` in screens.json (L8, L11).
   - The "0 of 71" premise split: the JSON has no premise field and the script has no split (matched_distract.py:L48). Its docstring (L4–5) states the result anyway.
   - The "0 of 180": the `distract_by_prem_*.json` files are not committed.
   - All Dan-checkpoint screen numbers: the `ckpt_dan_*.json` files are not committed.
   - The mix_8 premise counts, and the trace counts "25 to 32 of 32" (`experiments/pretrain-data/textbook72_distract2/results.md:L90–91`).
   - The leak-audit code.
9. **The mechanism is over-generalised for R384.**
   - `experiments/pretrain-data/textbook72_distract2/results.md:L85–86` says "28 to 32 of 32 samples per four-premise problem fail with this reason" (the PR-block mismatch).
   - In the committed JSON only 5 of the 10 four-premise problems are in that range. The others: pick_4 1, pick_4_last 11, and_4_ends 20, mp_4_mid 9, chain_4_rev 18. Across the four- and five-premise samples it is 258 of 384; the rest are lean_seq `LEANPARSE` failures (unbound, name, no-eos).
   - The 0/320 result stands. The mechanism explains about two thirds of Robbie's failures. For r8s0 it explains all 384, since every one fails at "PR position".
10. **The "1e-24" headline is an artefact of the naming convention.**
    - The README and results cite "near 1e-24" (`data/pretrain_data/release_2026-10-12_textbook72_distract2/README.md:L244`) and "about 4e-24" (`experiments/pretrain-data/textbook72_distract2/results.md:L116`). That figure is the raw probability under canonical names with base 0.
    - Under the same forcing, even the correct first premise line on 1-, 2- and 3-premise prompts gets only about 0.018 (forced JSON, first entries), although sampling solves those prompts.
    - The share product is 7.66e-15 (JSON L134). The robust evidence is 0/2,048 samples. The conclusion holds either way.
11. **Two different stories about what Robbie's base was trained on.**
    - pools.md:L411 and screen_ckpt.py:L1 call `scale-d384-p1200_s0` "Robbie's K12 Stage-1". pools.md:L439 says "the padded originals it was trained on", and screens_analysis.md:L37 says "the pool the model was trained on for 20 epochs".
    - But pools.md:L3 and L7 say cap6 is "the pool every one of Robbie's pretrains saw". L505 says "Robbie's cap-6 base", and screens_analysis.md:L211 says "cap-6-era lean_seq".
    - R384's K12 "training rows" loss (0.1705) equals its held-out-head loss (0.1696) (pools.md:L635), which fits K12 being unseen by that model.
    - If R384 saw only cap6, the "padding is noise, with a matched-row proof" reading (screens_analysis.md:L33–39) does not show that padding is hard to learn. Dan's K12-trained Stage-1 shows the opposite: minimal proofs cost 1.95× its K12 loss (L215).
    - This should be settled against Robbie's run config, which is the Robbie reader's slice.
12. **Single seeds everywhere after 10-02.**
    - textbook72_distract2 stopped after r8s0; s1 and s2 were "NOT launched" (`experiments/pretrain-data/textbook72_distract2/status.md:L14–15`).
    - The screens are "One checkpoint per screen, no seeds" (`data/pretrain_data/release_2026-10-09/README.md:L67`).
    - The 10-02 evaluation has two checkpoint seeds and Charles says that supports "signs of life" only (`experiments/textbook-problem/eval_dan_best_state/results.md:L105`).
    - The binomial SE at n = 160 is about ±0.04 (screens_analysis.md:L102). The +0.05 on distract10 and the +0.13 on tail10 are near that noise.
13. **Per-slice RL deltas are probably unpaired for some slices (inference from the code and the log; not checkable).**
    - `screen_ckpt_dan.py` draws every slice's 128 prompts from one `random.Random(seed)` shared across pools (L203, L244).
    - The two checkpoint runs were resumed with different pool lists (`docs/pretrain-data/log.md:L342–351`). So tail10, wrong100, pairs1, sub10 and aux10 were almost certainly screened on different random draws for S1 and for r8s0.
    - The first five list pools (joins10, minimal_joins10, distract10, minimal, dial_1e1) are probably paired.
14. **The environment-written-block comparisons cross runs, and the "0 of 64" in the 10-07 docs is a different unit.**
    - Envpr: the 28 → 38 compares `textbook72_distract_eval_dan.py` with `elementary_envpr.py`, and the original set moved 49 → 48 between them. The ladder comparison is clean, because both arms ran in one script and the model-written arm exactly reproduces env.
    - The 10-07 docs speak of "7 four-premise problems at 0 of 64". That means per problem across 2 seeds × 32 samples (hard_problems.md:L5: "never solved by either RL seed (64 samples each)"), not 0 of 64 in total.
15. **Minor.**
    - "RL gain is at 7–20 reference lines, nothing at 21+" (`docs/textbook-problem/log.md:L459`) against "1 of 31 at 21+" (L464). The one solve is Roy T6.27 (28 lines) at 1/32 on r8s1 only, from per_problem.csv.
    - The K12 leak audit (leak_audit.md:L15) does not say it is curry-aware, unlike the release audit, and its code is not committed.
    - 144 of the 225 derived rows are curried twins of kept bases. Derived scores are therefore not independent of base-set scores.
