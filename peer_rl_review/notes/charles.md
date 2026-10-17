# Charles (`origin/charles/main`): textbook-problem sets, pretrain-data pools, the premise-count wall

Notes written 2026-10-17 by a read-only research assistant for `peer-rl-review`. Everything was read with
`git -C ~/nd-rl show origin/charles/main:<path>`, so `charles/main` is the only branch cited unless stated. No sealed
theorem statement appears here; the textbook72 problems are referred to only in aggregate. "derived" = my arithmetic,
shown in full. "recount" = I recomputed it from a committed raw JSON file (light python over `git show` output).

## 1. Files read (aliases used in the citations)

All paths below are on `origin/charles/main`.

| alias | path |
| --- | --- |
| T0930 | `data/textbook_problem/release_2026-09-30/README.md` (110 lines) |
| T1002 | `data/textbook_problem/release_2026-10-02/README.md` (73 lines) |
| BASE | `data/textbook_problem/release_2026-10-02/baselines.md` (24 lines) |
| T1002-files | `data/textbook_problem/release_2026-10-02/{candidate_v0,candidate_v1,hand_proved_14,batch3,derived}.jsonl` (recount of premise counts and `min_lines`) |
| EDB / EDBp | `experiments/textbook-problem/eval_dan_best_state/results.md` (105 lines) / `proposal.md` (81 lines) |
| ESP | `experiments/textbook-problem/eval_scale_pretrain/results.md` (146 lines) |
| TPLOG | `docs/textbook-problem/log.md` (L450, L462, L464 only) |
| R1009 | `data/pretrain_data/release_2026-10-09/README.md` (109 lines) |
| D2R | `data/pretrain_data/release_2026-10-12_textbook72_distract2/README.md` (333 lines, read in full) |
| MAN | `data/pretrain_data/release_2026-10-12_textbook72_distract2/MANIFEST.json` (keys `distracted_set`, `models`, `protocol`) |
| D2prop / D2res / D2stat | `experiments/pretrain-data/textbook72_distract2/{proposal.md,results.md,status.md}` (73 / 154 / 20 lines, read in full) |
| D2m / D2mE | `experiments/pretrain-data/textbook72_distract2/run/metrics.jsonl` / `run/metrics_envpr.jsonl` |
| D2r384 / D2r768 | `experiments/pretrain-data/textbook72_distract2/run/robbie_d{384,768}/{status.md,metrics.jsonl}` |
| SCR-prem-r8 / SCR-prem-384 | `data/pretrain_data/screens/elementary_prem_la_T1_best12_s0_r8.json` / `elementary_prem_scale-d384-p1200_s0.json` |
| SCR-forced | `data/pretrain_data/screens/elementary_forced_la_T1_best12_s0_r8.json` |
| SCR-envpr | `data/pretrain_data/screens/elementary_envpr_la_T1_best12_s0_r8.json` |
| POOLS | `docs/pretrain-data/pools.md` (L103, L440–560, L670–742) |
| PDPLAN | `docs/pretrain-data/plan.md` (L1–110) |
| PDLOG | `docs/pretrain-data/log.md` (L434–510) |
| PDQ | `docs/pretrain-data/questions.md` (L59–78) |
| X00c / X00cp | `experiments/ws3/exp-00c-lr-ei-cpu/results.md` (190 lines) / `proposal.md` (L8–60) |
| WS3W / WS3P | `docs/ws3/week_summary_2026-09-27.md` (L25–50) / `docs/ws3/plan.md` (L26) |
| EDL / EDLs | `experiments/finetuning/edl_mock/proposal.md` / `status.md` |
| FTPLAN / FTLOG | `docs/finetuning/plan.md` (L1–30) / `docs/finetuning/log.md` (L74–116) |
| code | `code/pretrain_data/{textbook72_distract_eval_dan.py, screen_ckpt_dan.py, elementary_envpr.py, distract_by_premises.py}`, `data/pretrain_data/release_2026-10-12_textbook72_distract2/apply_distractors.py`, `code/ws3/textbook72/fetch.sh`, `code/textbook_problem/derive.py` (L673–695) |
| ours | `/home/dan/work/peer-rl-review/peer_rl_review/notes/ours.md` (cross-reference only: L73, L310, L320, L334, L354) |

`experiment-summaries/` on charles/main: last commit 2026-09-20 (`29a4b2d`); folders `2026-06-09-nd-bootstrapping-sprint`,
`2026-06-10-proof-novelty-sprint`, `2026-06-11-fol-sprint`, `2026-09-08-r1-cot`, `2026-09-10-flop-adaptation`,
`2026-09-10-olmo-32b-pilot`, `2026-09-10-proof-cap-comparison`, `2026-09-10-proof-fragment-selection`, plus `README.md`,
`TEMPLATE.md`, `synthetic-cap6-proof-lengths.md`. **Nothing in it dates from after 2026-09-25**, so nothing there to
summarise. Charles's post-09-25 work lives in `data/`, `experiments/` and `docs/` (below). `origin/charles/main` is the only
Charles branch on the remote; its last commit is 2026-10-12 20:26 -0700 (`297dcbd`).

## 2. Timeline (commit times -0700, from `git log origin/charles/main`)

| date | commit | what |
| --- | --- | --- |
| 09-23 | `a0b2ec6`…`f4ac7d9` | ws3 exp-00 (GRPO local check on an older Robbie checkpoint), reviewed PASS |
| 09-24 | `71b4879` | ws3 fixed checkpoint re-pinned to Robbie's `039_muon-adamw-finish-5pct_s1` |
| 09-27 | `49aeea7`, `487f43d`…`2984fd6`, `f489806` | RL options (TRL GRPO, EI); exp-00c learning-rate sweep + EI on CPU, reviewed PASS WITH CORRECTIONS; week summary |
| 09-28 | `6c6ee0c`…`40a77a9` | textbook-problem workstream: candidate_v0 (105), transcriber, proof search |
| 09-29 | `2d6bcd0`, `08ee84c` | candidate_v1 (80), v0 amended to 104, release folder `release_2026-09-30`, comparison with the 72 |
| 10-02 | `2c5d69c`, `6898cdc`, `5d0084a` | eval_scale_pretrain and eval_dan_best_state proposals; `release_2026-10-02` (412 problems) with baselines |
| 10-09 16:59 | `4683f6e` | `release_2026-10-09`: 17 candidate Stage-1 pools (no training) |
| 10-09 21:31 | `632a2c9` | textbook72_distract2 proposal (pre-registration) + builder + evaluators |
| 10-09 23:38 | `193711e` | distract2 results: 0 of 25 crossing problems solved, all four models; PAUSED |
| 10-10 08:58 | `01f909a` | premise-stratified distractor check: 0 of 180 four-plus prompts, three models (`code/pretrain_data/distract_by_premises.py`, `docs/pretrain-data/pools.md`, `log.md`) |
| 10-10 16:51 | `1f2eb39` | finetuning workstream: `edl_mock` proposal, stream builder, EDL runner |
| 10-12 08:35 / 08:47 | `f521945`, `3b6ec09` | distract2 release folder; caveat on the absent problem |
| 10-12 19:31 | `e5194f6` | mechanism: the wall is the premise (PR) block; elementary 2–5 premise ladder; action traces |
| 10-12 20:13 | `1afc7b9` | can RL teach the block: mix has no 4-premise prompt, forced p(block) ~1e-24, 0/2,048 samples; environment-written block |
| 10-12 20:26 | `297dcbd` | distract2 README follow-up section (the three 10-12 results) |

## 3. Releases

### 3a. `data/textbook_problem/release_2026-09-30/` (superseded but kept as published, T1002:L6–8)
- Contents: `candidate_v0.jsonl` 104 (*forall x* Syracuse 39, Calgary 26, Mississippi State 16; Carnap Book 23),
  `candidate_v1.jsonl` 80 (Roy §6.2 76; Carr 4), `unsolved.jsonl` 14 (Roy 10, Pelletier 4; valid, no proof ≤ 40 lines
  found), `lean/*.lean`, MANIFEST (T0930:L12–16). Intro says "194 propositional natural deduction problems … 184 with a
  verified reference proof and 14 … no proof found" (T0930:L4–5); see §8 item 1 (104 + 80 + 14 = 198, derived).
- Format: textbook-72 fields plus provenance, `reference_proof` (passes pinned `nd_verify` via `strict_verify`), `min_lines`
  (upper bound), Lean fields rendered by the `lean_seq` tokenizer, checked with Lean 4.34.1 (T0930:L20–33). Prompts:
  `THM p1 , p2 SEQ goal PRF`, connectives `& v > ~`, `F` = ⊥, letters P Q R S (T0930:L35–36).
- Against the 72: shortest-proof median 10 (72) / 8 (v0) / 9.5 (v1) lines (T0930:L64); theorems with no premises 16 / 13 /
  30 / 9 (L69); 3 or more premises 4 / 17 / 9 / 1 (L70); 72's length bins 1–2 … 16+: 4 / 3 / 11 / 8 / 11 / 17 / 8 / 9
  (L78–79). 71 of the 72 have a reference proof (L60).
- Status: "Candidate sets, not releases under the plan: the frozen-model baseline (T5) has not been run"; second-reader
  sheets reviewed by Charles 2026-09-30 (L97–99). 5 candidate_v1 reference proofs exceed 400 tokens, the evaluator's
  default `max_new` (L104–105).

### 3b. `data/textbook_problem/release_2026-10-02/` (the current textbook-problem release)
- 412 problems in five files, every reference proof accepted by pinned `nd_verify` through `strict_verify` (T1002:L3–5):
  `candidate_v0` 87 ("Was 104"), `candidate_v1` 72 ("Was 80"), `hand_proved_14` 14 (hand proofs "of 20 to 102 lines,
  verified; not minimal"), `batch3` 14 (Pelletier 4, forall x R³ 8, Oxford booklet 2), `derived` 225 (21 nuances by proof
  surgery) (T1002:L12–16). 87 + 72 + 14 + 14 + 225 = 412 (derived). `removed.jsonl` 22; sealed matches counted only: 13
  (L17). Lean: 408 of 412 accepted, 4 hand proofs exceed the renderer's 64-name limit (L19, L59).
- Audit: curry-aware renaming class (⊢ A → B and A ⊢ B are one problem) against the 72, the test files and the named
  pools (`validation_36`, `heldout`, `transfer`, `rl_targets`, `train`) (L25–31). 144 derived rows are kept curried twins of
  their base, tagged `curried_twin_of`, "must never be used as if independent of their base" (L31–34). Leak audit against
  the RL model's pools (K12, rl_targets, transfer, heldout): "at most 3 problems per set share a class" (L63–64).
- Second-reader check of 20 random transcriptions: done for v0 and v1; "**Not done** for batch 3, the hand-proved 14 or
  the derived set" (L60–62).
- Derived nuances: prefix nuances feed sequent + given lines; repair and two clozes use marker words "no trained model has
  seen … they are a specification" (L41–44). `distractor_scaling` (12 rows, L47) = "k irrelevant premise(s) from other pool
  problems added, sharing letters, jointly satisfiable, never cited" (`code/textbook_problem/derive.py:L694`).
- Recount from T1002-files (my python over `prompt` and `min_lines`; derived):

  | file | n | premises 0/1/2/3/4 (5, 6) | min_lines min / median / max | min_lines > 10 | min_lines > 12 |
  | --- | --- | --- | --- | --- | --- |
  | candidate_v0 | 87 | 4 / 36 / 31 / 13 / 3 | 3 / 9 / 29 | 37 | 18 |
  | candidate_v1 | 72 | 24 / 12 / 27 / 8 / 1 | 3 / 10 / 28 | 32 | 26 |
  | hand_proved_14 | 14 | 9 / 3 / 1 / 1 / 0 | 20 / 46 / 102 (hand, not minimal) | 14 | 14 |
  | batch3 | 14 | 3 / 2 / 1 / 7 / 1 | 8 / 11 / 19 | 7 | 5 |
  | derived | 225 | 59 / 52 / 64 / 33 / 12 (5: 3, 6: 2) | 4 / 11 / 28 | — | 81 |

  So the four non-derived files hold 37 + 32 + 14 + 7 = **90 problems with min_lines > 10** (derived; this is presumably
  the "90 long theorems" figure, which is not written anywhere on charles/main) and 3 + 1 + 0 + 1 = 5 four-premise problems
  (derived).
- Intended use: the yardstick. "the textbook sets stay the yardstick and are not changed here" (PDPLAN:L4–5). The sealed 72
  "are not here and never will be; they are gitignored and used for scoring only" (T1002:L21).
- Licences: Roy CC BY-NC-SA (non-commercial); Carr and Oxford booklet no licence stated (6 problems) (T1002:L68–72).

### 3c. `data/pretrain_data/release_2026-10-09/`: candidate Stage-1 pools
- "**50 candidate pools built and screened without training; no pool has been trained on; no GPU spent.**" The release
  publishes the ones the screens single out (R1009:L3–6): 17 pools as slice files, 30.8 MB (PDLOG:L435–441).
- For whom / why: the RL model trained on Dan's K12 fails textbook problems where K12 has gaps ("no problem has more than
  three premises, no box is deeper than two, no proof is longer than twelve lines, and half of the long proofs are padded");
  hypothesis "data gaps, not capacity gaps"; network, RL ladder, tokenizer and verifier fixed (R1009:L10–14). The plan:
  Stage-1 with Robbie's recipe and Dan's T1 ladder held fixed, scored on the textbook sets (PDPLAN:L33–35).
- Format and size: "Every pool is **K12 with a slice replaced**": K12's 155,000 records in order, 1 %, 10 % or 30 % of rows
  outside the first 1,024 swapped; only the new records ship (with `pos`); `assemble.py` rebuilds from K12, fetched from
  Dan's bucket `hf://buckets/dan-pandori/nd-rl/cap-horizon/data/kh/train_k12.jsonl.gz` (R1009:L18–27). Records in K12's format
  (`prompt`, `proof`, `thm`, `key`, `n_lines`, `n_prem`, `rules`, `pool` + builder fields); every new proof verified by
  pinned `nd_verify` (R1009:L29–33). Cap: K12 is "flat 2–12" lines (PDPLAN:L49); premises ≤ 3 because the generator's
  `--max_prem` defaults to 3 (PDPLAN:L44).
- Pools (R1009:L37–46): `k12_prem4_10/_1e2/_1e3` (4–5 premises; 15,500 / 155 / 15), `k12_distract10/_30`,
  `k12_minimal_distract10` (1–2 unused premises; 15,500 / 46,500 / 15,500), `k12_joins1/10`, `k12_minimal_joins10`
  (1,550 / 15,500 / 15,500), `k12_jdist10`, `k12_jsubst10`, `k12_long16_10` (13–16 lines, box depth ≤ 3; 15,500 each),
  `k12_dial_1e1…1e4` (↔-elimination; 15,500 / 1,550 / 155 / 16), `k12_minimal` (84,700 minimal proofs replacing K12's).
- Screens only (R1009:L64–80), no seeds. Status: "Not done: any Stage-1 run, any ladder" (L88–90); "Nothing here has been
  trained on" (L102). Gate for claims: 3 seeds and a gain of at least 8 test-split problems beyond twice the baseline's
  seed spread (L103–104).
- Sealed parts: none shipped; K12 is Dan's and is not redistributed (L21–22, L108–109).

### 3d. `data/pretrain_data/release_2026-10-12_textbook72_distract2/`
- What: the sealed 72 (Dmitry's 58 `textbook_dev` + 14 `textbook_train`) with exactly two unused premises added to each
  (D2R:L14–15). 71 of 72 took two distractors (D2R:L20). The modified problems are **not committed** (they contain the sealed
  originals verbatim); the folder ships `distractors.jsonl` (71 rows: name, slice, the two premises, positions),
  `apply_distractors.py` (standard library; rebuilds from the sealed files and checks canonical sha256 `5f91d124…`),
  `examples.jsonl` (4 non-sealed *forall x: Calgary* exercises), `metrics/` (four models + `summary.json`), `MANIFEST.json`
  (D2R:L42–52).
- Construction (D2R:L64–84): builder `code/pretrain_data/textbook72_distract.py` (`distract_one`), seed 0, same
  construction as the `k12_distract` pools; distractors are random formulas of depth ≤ 2 over P Q R S, ≤ 9 tokens, not a
  subformula of any premise or goal, premise set stays satisfiable; inserted at random positions; shortcut check with
  `minlen` (bound minimal + 1, 10 s; up to 6 draws; timeout = "unknown", kept). Shortcut status `no_shortcut` 44, `unknown`
  27; prompts 28.1 → 45.4 tokens on average (D2R:L79–81; MAN `distracted_set`). Premises before → after: 0 → 2 for 16,
  1 → 3 for 30, 2 → 4 for 22, 3 → 5 for 3 (D2R:L84); 25 cross to ≥ 4, 46 stay at 2–3 (D2R:L20–21).
- Line lengths: "a proof of the modified problem is the original proof plus two lines" because every premise needs its own
  `PR` line (D2R:L77–79). The 72's shortest-proof median is 10 lines (T0930:L64).
- The absent problem is the only 4-premise original (inconsistent premises, 20-line reference proof; every draw flagged as a
  shortcut) (D2R:L316–321).
- Intended use: evaluation-only artefact; never trained on, never used as seed, reported only by premise-count bin (PDQ:L65–70).

## 4. Results table

Abbreviations used in the protocol column:
- **Models.** R384 = Robbie `scale-d384-p1200_s0/pretrain.pt`, 9,557,760 params, lean_seq whole-proof, pretrain only (no RL)
  (D2R:L131); trained on the fork's cap-6 Stage-1 set (PDPLAN:L48; "Robbie's cap-6 base", POOLS:L505). R768 =
  `scale-d768-p1200_s0`, 37,989,888 params, same format (D2R:L132). DS1 = Dan `stage1_best12_s0_b1200`, 9,560,832 params,
  `lean_staten` proof-state, cap 12, 1,200 s on K12, no RL (D2R:L133). DR8 = Dan `la_T1_best12_s0_r8`, same network after 8
  rounds of the T1 best-state ladder, seed 0 (D2R:L134); in our notes this is `state_env_october` = best-cap12 r8, best-state
  copy (ours:L73). DR8s1 = seed 1. M3 = Robbie `039_muon-adamw-finish-5pct_s1/pretrain.pt`, "3M-parameter" (X00cp:L14), `tok_mode='abs'`
  (WS3P:L26), whole-proof. No Leon model was tested anywhere on charles/main.
- **Interface / sampler.** RS = Robbie's free sampling in lean_seq tokens, `max_new` 400 (`eval_ckpt.py`). ENV = Dan's
  `state_sample.env_generate`, 48 steps, 256 tokens per action, batch 256, Dan's code at nd-takehome `0c492902` (D2R:L136,
  L145–146). ENVPR = environment writes the premise block first (Charles's re-implementation, `elementary_envpr.py:L33–53`).
- **Judge.** ND = pinned `nd_verify` through `strict_verify`. LEAN = Lean 4.34.1 in the loop (Dan's `state_eval.py`) with
  every accepted proof re-judged by ND (EDB:L3–13).
- **Reviewed.** No `review.md` exists for eval_scale_pretrain, eval_dan_best_state or textbook72_distract2; only the ws3
  experiments were independently reviewed. "pre-reg" = proposal committed before the run.

| # | claim / metric | value as reported | protocol (a) model (b) judge (c) k, T (d) set (e) seeds | source | reviewed? |
| --- | --- | --- | --- | --- | --- |
| 1 | candidate_v0 avg / solved | R384 0.111 / 22; R768 0.086 / 17; DR8 0.341 / 76; DR8s1 0.344 / 73 | (a) R384, R768 via RS; DR8, DR8s1 via ENV (b) ND for pretrains; LEAN for RL (c) k 32, T 1.0 (d) v0 **as before the re-cut, n 104** (e) 1 seed per pretrain, 2 RL seeds | BASE:L3, L7; EDB:L21 | pre-reg; unreviewed |
| 2 | candidate_v1 avg / solved | 0.050 / 11; 0.058 / 11; 0.356 / 49; 0.362 / 50 | as #1; n 80 (pre-re-cut) | BASE:L8 | pre-reg; unreviewed |
| 3 | hand_proved_14 | 0.000 / 0 for all four | as #1; n 14 | BASE:L9 | pre-reg; unreviewed |
| 4 | batch3 | 0.000 / 0; 0.002 / 1; 0.298 / 10; 0.327 / 12 | as #1; n 21 "incl. the 4 hand-proved" | BASE:L10 | pre-reg; unreviewed |
| 5 | Lean-sourced (not in the release) | 0.088 / 11; 0.091 / 9; 0.401 / 33; 0.383 / 31 | as #1; n 50 | BASE:L11 | pre-reg; unreviewed |
| 6 | derived | pretrains (202 rows, 18 feedable nuances) 0.038 / 20, 0.036 / 17; RL (132 rows, 13 plain nuances) 0.264 / 69, 0.287 / 66 | as #1; prefix + marker-word nuances not fed to the proof-state model | BASE:L12–13, L24 | pre-reg; unreviewed |
| 7 | textbook72, aggregate | 0.104 / 12; 0.129 / 11; 0.371 / 49; 0.378 / 47 | as #1; n 72 (sealed; scoring only) | BASE:L14; EDB:L27 | pre-reg; unreviewed |
| 8 | `distractor_scaling` nuance (derived set) | DR8 0.102 avg, 3 any-of-32; R384 0.000 / 0; R768 0.078 / 1 | as #1; 12 rows | EDB:L43; ESP:L41, L112 | unreviewed |
| 9 | per-problem RL vs pretrain | "pretrain solved 44 of 269 scraped problems, RL 183 (either seed), pretrain-only 0"; RL "79–100 % through 10 reference lines, 55–67 % at 11–13, 12 of 36 at 14–20, 1 of 31 at 21+; the knee at 12 lines matches the flat 2–12 cap of Dan's K12"; "all 7 four-premise problems unsolved by every model" | as #1; 269 = v0 104 + v1 80 + hand14 14 + batch3 21 + lean_v2 50 (derived) | TPLOG:L464 | unreviewed |
| 10 | distract2 headline: solved ≥ 1 of 32, original → distracted | R384 12 of 72 → 5 of 71; R768 11 of 72 → 6 of 71; DS1 25 of 71 → 12 of 71; DR8 49 of 71 → 28 of 71 | (a) R384, R768 via RS; DS1, DR8 via ENV (b) ND for all (c) k 32, T 1.0, sampling seed 0 (d) the 72 / the 71 distracted (2 unused premises each) (e) one seed per model | D2R:L23–28; D2res:L12–17; D2m; D2r384; D2r768 | pre-reg (632a2c9); unreviewed |
| 11 | crossing to ≥ 4 premises (25), original → distracted | 5 → **0**; 3 → **0**; 8 → **0**; 17 → **0** | as #10 | D2R:L25–28 | pre-reg; unreviewed |
| 12 | staying at ≤ 3 premises (46), original → distracted | 7 → 5; 8 → 6; 17 → 12; 32 → 28 | as #10 | D2R:L25–28 | pre-reg; unreviewed |
| 13 | avg solve rate ± 95 % (over problems), original → distracted, ratio | R384 0.104 ± 0.064 (n 72) → 0.027 ± 0.030 (n 71), 0.26; R768 0.129 ± 0.073 → 0.030 ± 0.030, 0.23; DS1 0.124 ± 0.061 → 0.040 ± 0.027, 0.32; DR8 0.378 ± 0.088 → 0.140 ± 0.061, 0.37 | as #10 | D2R:L163–168 | pre-reg; unreviewed |
| 14 | by original premise count 0 / 1 / 2 / 3 (n 16 / 30 / 22 / 3), solved original → distracted | R384 1→0, 6→5, 5→0, 0→0; R768 1→0, 7→6, 3→0, 0→0; DS1 5→4, 12→8, 7→0, 1→0; DR8 9→7, 23→21, 14→0, 3→0 | as #10 | D2R:L172–177; D2m | pre-reg; unreviewed |
| 15 | pre-registered prediction vs outcome | crossing solved predicted 0–1 / 0–1 / 0–2 / 0–3, observed 0 / 0 / 0 / 0; staying kept predicted 60–85 %, observed 71 %, 75 %, 71 %, 88 % (5/7, 6/8, 12/17, 28/32, derived) | as #10 | D2R:L187–189; D2prop:L56–66 | pre-reg; unreviewed |
| 16 | parse-fail fraction (Robbie only) | d384 0.324 → 0.430; d768 0.384 → 0.485 | as #10 | D2R:L183–184; D2r384; D2r768 | unreviewed |
| 17 | matched distractor check, generator rows | 200 `k12_distract10` rows vs their K12 originals: pass@32 0.53 vs 0.92; by total premises 1 / 2 / 3 / 4 / 5 (n 8 / 41 / 80 / 50 / 21): distracted solved 1.00 / 0.95 / 0.74 / **0.00** / **0.00**, original 1.00 / 0.95 / 0.96 / 0.86 / 0.76 | (a) R384 via RS (b) ND (c) 32 samples (POOLS:L694); T 1.0, max_new 400, seed 0 (`code/pretrain_data/matched_distract.py:L19, L27`) (d) generator rows (e) 1 checkpoint, no seeds | POOLS:L693–704; R1009:L82–84 | not pre-reg; unreviewed |
| 18 | premise-stratified distractor check (commit 01f909a) | ≤ 3 premises solved of 120 (per-sample): R384 101 (0.55), DS1 112 (0.48), DR8 119 (0.85); 4 premises 0 of 120 and 5 premises 0 of 60 on all three; "0 of 5,760 samples each" | (a) R384 via RS; DS1, DR8 via ENV (b) ND (c) pass@32 (d) 300 rows of `k12_distract10` (120 at 4, 60 at 5, 120 at ≤ 3) (e) one seed | POOLS:L714–728; PDLOG:L461–467; `distract_by_premises.py:L1–8` | not pre-reg; unreviewed; raw outputs not committed (§8) |
| 19 | 4–5-premise generator pool | `k12_prem4_10` base pass@32 0.00 "at every fraction" | (a) R384 (b) ND (c) 32 tries (d) 160 prompts of the 10⁻¹ slice, all 155 and 15 of the 10⁻² and 10⁻³ slices | R1009:L72; POOLS:L524, L536–537 | unreviewed |
| 20 | RL lift by slice on Dan's checkpoints (pass@32, Stage-1 → r8) | `k12_distract10` 0.6328 → 0.6875 (+0.05); `k12_joins10` 0.3594 → 0.6875 (+0.33); `k12_dial_1e1` 0.3516 → 0.7656 (+0.41); `k12_sub10` 0.5391 → 0.8359 (+0.30); `k12_tail10` 0.8672 → 1.0 (+0.13); cap6 set 0.9844 → 1.0 (+0.02) | (a) DS1 → DR8 via ENV (b) ND "not his Lean judge" (c) T 1.0, k 32 (d) 128 prompts per slice (R1009:L67) (e) one checkpoint | POOLS:L460–476 | unreviewed |
| 21 | elementary 2–5 premise ladder, samples verified | DR8 154 / 160, 111 / 128, **0 / 320**, 0 / 64; R384 115 / 160, 90 / 128, **0 / 320**, 0 / 64 (2 / 3 / 4 / 5 premises) | (a) DR8 via ENV; R384 via RS (b) ND (c) k 32, T 1.0, seed 0 (d) 21 non-sealed trivial problems, 5 / 4 / 10 / 2 at 2 / 3 / 4 / 5 premises (recount SCR-prem-r8) (e) one seed | D2R:L205–210; D2res:L76–81; recount SCR-prem-r8, SCR-prem-384 matches | not pre-reg; unreviewed; recount matches |
| 22 | failure reason at 4 premises | R384 writes three PR lines then a correct body; "28 to 32 of 32 samples per four-premise problem fail with this reason" ("premise block does not match declared premises"); adding the fourth PR line makes it verify. DR8: with 3 premises first actions `h1 h2 h3` in 30 of 32; with 4 premises first premise line cites `h2` in 25 to 32 of 32, environment rejects ("PR position") | as #21; DR8 32 traces per prompt | D2R:L214–224; D2res:L83–93 | unreviewed |
| 23 | round-8 training mix | `mix_8.jsonl` 89,724 rows: 14,279 / 37,807 / 28,454 / 9,184 at 0 / 1 / 2 / 3 premises, none at ≥ 4 | DR8 ladder (seed 0), Dan's bucket | D2R:L230–232; D2res:L107–109 | unreviewed |
| 24 | teacher-forced premise block, `P , Q , R , S ⊢ P` | step 1 `h1` 0.0011 (mass on `h2` 0.015); step 2 `h2` "below 1e-6" (`h3` 0.999); step 3 `h3` 0.31; step 4 `h4` "below 1e-6"; block "near 1e-24" (README) / "about 4e-24" (results). Recount: p_block 3.99e-24, share_block 7.66e-15; for the 1-, 2-, 3-premise prompts p_block 0.0177 / 0.0175 / 0.0174 | (a) DR8 via ENV, canonical names, base 0 (c) teacher forcing (e) one checkpoint | D2R:L234–244; D2res:L111–118, L152–154; recount SCR-forced `forced[*]` | not pre-reg; unreviewed |
| 25 | plain search on the same prompt | 0 of 1,024 at T 1.0 ("PR position" 1,022) and 0 of 1,024 at T 1.5 (991); "0 of 2,048" | (a) DR8 via ENV (b) ND (d) **one prompt** (recount: `search` has 2 entries, both `P , Q , R , S ⊢ P`) | D2R:L245–247; D2res:L118–120; SCR-forced `search` | unreviewed |
| 26 | environment writes the premise block: elementary ladder | 153 / 160, 106 / 128, **252 / 320**, **57 / 64**; at 4 premises "the four-step chain that needs every premise 0 / 32", reversed order 10 / 32 | (a) DR8 via ENVPR, no training (b) ND (c) k 32, T 1.0 | D2R:L254–261; D2res:L127–134; recount SCR-envpr matches | not pre-reg; diagnostic only (PDQ:L72–78); unreviewed |
| 27 | env-written block: stratified generator sample | ≤ 3: 120 / 120 (9 / 9, 33 / 33, 78 / 78 at 1 / 2 / 3); 4: **118 / 120** (pass@1 0.83); 5: **55 / 60** (pass@1 0.74); "0 / 180 before"; commit subject "173/180" (118 + 55 = 173, derived) | as #26; 300 rows as #18 | D2R:L266–269; D2res:L134–136; SCR-envpr `distract10_env_premises.by_prem` | unreviewed |
| 28 | env-written block: distracted 72 | original 48 of 71 (0.374); distracted **38 of 71** (0.210, was 28); crossing 16 → **10** (was 17 → 0); staying 32 → 28; by original premise count 9 → 7, 23 → 21, 13 → 9, 3 → 1 | as #26; n 71 | D2R:L273–278; D2mE | unreviewed |
| 29 | Charles's own RL (ws3 exp-00c): held-out length-7 avg solve rate | frozen 0.122; GRPO lr3e-5 0.430, lr1e-4 0.391, lr3e-4 0.333; EI 0.545; length 8: 0.000 → 0.005 / 0.013 / 0.011 / 0.266; textbook72 avg 0.101 → 0.113 / 0.119 / 0.084 / 0.108; greedy held-out lengths 2–6 0.978 → 0.982 / 0.978 / **0.881** / 0.978; pre-registered paired diff on the 39 frozen-solved +0.273 / **+0.325** / +0.163 / +0.245 | (a) M3, whole-proof (b) ND (`strict_verify`; reviewer re-verified 115,127 rows, 0 disagreements) (c) eval 32 samples, T 1.0; textbook k 32, T 1.0, max_new 400 (`experiments/ws3/exp-00c-lr-ei-cpu/configs/base.yaml:L6`) (d) 200 eval-half `rl_targets` prompts (160 at length 7, 40 at 8); training pool 198 prompts (e) one seed per arm | X00c:L18–24, L42–55, L90–92 | **reviewed: PASS WITH CORRECTIONS** (X00c:L3–9) |
| 30 | exp-00 / exp-00b | GRPO lr 1e-5 on lengths 3–5: "nothing moved" (KL 0.0017) / "inert: 90% of groups all-correct, KL 0.0003" | exp-00: old `share_pretrain_4l_seed0`; exp-00b: M3 | WS3W:L37–38 | exp-00 reviewed PASS; exp-00b not reviewed |

## 5. The premise-count wall

**What it is, exactly.** No model Charles tested has produced a proof the judge accepts for a prompt with four or more
premises, whether or not the extra premises are needed: "no model has produced an accepted proof under a prompt with four
or more premises in any run, needed or not" (POOLS:L726–728). Models: R384, R768 (whole-proof lean_seq pretrains, no RL),
DS1 and DR8 (Dan's proof-state Stage-1 and round-8 RL). Premise counts: 4 and 5 fail completely; 1–3 are solved at
ordinary rates (rows 17, 18, 21). Problem counts and rates:
- generator rows, R384: 0 of 71 at 4–5 total premises vs 0.83 on their undistracted originals (row 17; R1009:L83–84);
  0.83 = (0.86 × 50 + 0.76 × 21) / 71 = 0.830 (derived);
- stratified sample, three models: 0 of 180 four-plus rows on each model, against 101 / 112 / 119 of 120 at ≤ 3 (row 18);
- the distracted 72, four models: 0 of the 25 crossing problems solved, from 5 / 3 / 8 / 17 solved in original form;
  33 solves lost in total (5 + 3 + 8 + 17, derived; D2R:L310) while staying problems keep 71–88 % (rows 11, 12, 15);
- trivial problems: 0 of 320 samples at four premises and 0 of 64 at five on DR8 and R384, including `P , Q , R , S ⊢ P`
  (row 21).

**Mechanism (2026-10-12, `e5194f6`).** It is the premise block, not reasoning. The pinned verifier requires every proof to
open with one `PR` line per premise, in the prompt's order (D2R:L214–215; `nd_verify/verify.py:158`, D2res:L85). R384
writes a correct proof with three PR lines; DR8's environment rejects its first premise action because it cites `h2`
(row 22). Charles's reading: "The rule the model learned is positional: with k hypothesis lines in the state it emits the
premise line K12 would have next" (D2R:L244–245). DR8's RL also amplifies the effect: it loses 21 of its 49 textbook72
solves to two unused premises, all 17 crossing solves included (D2R:L30–31). 49 − 28 = 21 is the net loss; see §8 item 5.

**Is it a property of the pretraining data? Evidence for:**
1. No training data has more than 3 premises. K12 "has no problem with more than three premises" (D2R:L226). Every pool is
   capped at 3 ("generator `max_prem 3`", PDPLAN:L22; default `--max_prem` 3, PDPLAN:L44). Robbie's cap-6 data comes from the
   same generator. DR8's RL mix has none at ≥ 4 (row 23).
2. The failure is a deterministic positional habit at the first premise action: the block's teacher-forced probability is
   ≈ 4e-24, against ≈ 0.017 for 1–3-premise blocks under the same forcing (row 24 recount). It is not a reasoning failure.
3. Counterfactual: when the environment writes the block, the same untrained DR8 solves 118 of 120 four-premise and 55 of
   60 five-premise generator rows (row 27). The reasoning is there.

**What is not shown:**
- No Stage-1 has been trained on 4–5-premise data. `k12_prem4_10` is built but untrained (R1009:L88–90, L102), so the data
  hypothesis has not been tested by intervening on the training data. The recorded prediction is "a ladder on a premise-pool
  Stage-1 solves ≥ 40 of the 71 modified problems, against 28 here" (D2R:L305–306).
- The env-written-block test was run only on DR8. No analogous forced-prefix test was run on a whole-proof model.
- Longer prompts are a co-factor for Robbie's models: parse failures rise from 0.32 to 0.43 and from 0.38 to 0.48 (row 16).
  The trivial ladder rules this out as the main cause, because short four-premise prompts also fail.

**Can RL fix it? Measured feasibility, no RL run.** Nobody trained RL on four-premise prompts. The three measurements, all
on DR8 seed 0, CPU, one seed (D2res:L105–150), are:
1. The ladder never poses such a prompt (row 23).
2. If it did, reward would essentially never fire: forced p ≈ 4e-24, and plain search found 0 of 2,048 samples (row 25).
   That search used **one prompt**.

Charles concludes: "As the ladder stands, no … Expert iteration with the current environment would receive zero reward on
every four-premise prompt" (D2res:L141–142, L120). His two cheap fixes, either without any RL step, are (a) the
environment writes the block, and (b) Stage-1 exposure (the premise pool) (D2res:L143–147). After either, "RL has a dense
signal (pass@1 about 0.8 at four premises)". A genuine premise-selection residual remains: the all-premises chain (0 of 32),
and 6 of the 16 crossing textbook solves are still lost (D2res:L147–150). 37.5 % of crossing solves are lost vs 12.5 % of
staying ones (6/16 and 4/32, derived; reported as "37 %" and "12 %", D2R:L290–291). Fix (a) changes the task. It is
recorded as open question 10, with "**Default followed:** diagnostic only; no training run and no headline number uses it"
(PDQ:L72–78).

## 6. Bearing on RL performance and on Dan's models

- **Model overlap with us.** DR8 is our `state_env_october` seed 0, best-state copy (ours:L73; D2R:L134 hash `a992485e…`).
  Charles also measured the RL lift on it: DS1 → DR8 on textbook72 under ND, ENV, k 32, T 1.0 goes from 25 of 71 to 49 of 71,
  avg 0.124 → 0.378 (rows 10, 13). On the distracted 72 it goes 12 → 28.
- **Why his textbook72 count (49) is below ours (52 / 51 / 52 for the three best-state seeds, ours:L310).** The protocols
  differ: k 32 vs 256, T 1.0 vs 0.8, 48 steps / 256 tokens per action vs `--max_steps 96 --max_action 512` (ours:L320). The
  judge is ND vs Lean (Charles notes the original-set count matches the Lean-gated 49 of 72, D2R:L322–323), and his set is
  71 problems vs 72. The difference is protocol, not a contradiction.
- **How much the wall costs on our headline metric.** The 72 have 0 / 1 / 2 / 3 / 4 premises for 16 / 30 / 22 / 3 / 1
  problems (D2prop:L15). The single 4-premise problem has inconsistent premises and a 20-line reference (D2R:L316–319). So the
  wall can cost us at most 1 of 72 on textbook72 (derived). It matters for: distractor evaluations; textbook sets outside the
  72 (7 four-premise problems of 269, TPLOG:L464; 5 in the re-cut release files plus 17 derived rows at 4–6 premises, §3b
  recount); and any RL target pool, since none has ≥ 4 premises.
- **RL does not create what Stage-1 never showed.** The ladder's mix is 0–3 premises and reward is zero at 4, so EI cannot
  bootstrap the block (§5). This parallels our create-or-elicit result (ours COE row; not re-verified here). Charles's plan
  makes the same claim for other axes, with the RL failure table lining up with K12 gaps: four-premise cell, nesting depth 3
  (60/82 → 13/37), lengths past 12 lines, padding (PDPLAN:L20–27).
- **The "RL does not lift the distractor slice" reading (+0.05, row 20) is a composition effect.** The 4–5-premise rows are
  0 before and after RL. On ≤ 3-premise rows RL helps (DS1 112 → DR8 119 of 120; per-sample 0.48 → 0.85, row 18).
- **Proof-state vs whole-proof.** For Dan's environment the fix is one line of environment logic (apply `h1..hn`), and it
  is free at evaluation time: DR8 goes to 38 of 71 on the distracted 72 (row 28). For whole-proof models the verifier needs
  the block in the text. The analogue would be forcing the PR prefix at decode time, which was not tested.
- **Charles's own RL (exp-00c).** On a ≈ 3M whole-proof model, GRPO (lr 3e-5 to 1e-4) and EI give a large single-seed
  in-distribution lift on held-out length-7 generator problems (0.122 → 0.39–0.55). It does not transfer: "It does not reach
  the textbook set (0.101 to 0.084–0.119, inside the CIs …)" (X00c:L122–125). The lift is "one repaired step in the
  generator's nested-implication templates" (X00c:L175–176). This is also the pattern above: RL sharpens what the data's
  distribution already supports.
- **edl_mock (finetuning, commit `1f2eb39`)** is a CPU mock of prequential excess description length (EDL). It measures how
  many bits it takes to fine-tune Dan's Stage-1 base and ladder checkpoints (r2, r4, r8, seed 0) onto verified proofs of
  `rl_targets` theorems the base never solved (stream "new", 128 train / 128 held-out). A control stream holds theorems the
  base already solves. A restricted arm fine-tunes only 10,000 random weights (EDL:L1–15, L19–24, L35–38). The aim is to
  separate elicitation from new capability as a function of RL amount (FTPLAN:L11–15). Fine-tuning here is an instrument,
  never a model to report. Smoke test: first block 30.2 bits/example; status `RUNNING 2026-10-10T23:51:48Z` and no
  `results.md` committed (EDLs:L3–4). So there are no results yet. The scratch step sweep found base starting loss "0.081
  nats/token", ≈ 29 bits per never-found proof, so "The elicitation gap per proof is a few bits" (FTLOG:L91–93). It is
  unreviewed and not pre-registered.

## 7. How to run the distractor evaluation on another model

1. Restore the sealed 72: `bash code/ws3/textbook72/fetch.sh`. It copies `textbook_dev.jsonl` and `textbook_train.jsonl`
   from `origin/dmitry/cap-comparison-textbook-eval-data` and checks sha256 (`fetch.sh:L1–15`; D2R:L57).
2. Rebuild the distracted set: `uv run python data/pretrain_data/release_2026-10-12_textbook72_distract2/apply_distractors.py`.
   It writes `docs/textbook-problem/textbook72/textbook72_distract2.jsonl` (gitignored) and checks canonical sha256
   `5f91d124…` (D2R:L58–59; `apply_distractors.py:L1–10`). Rows carry `name, prompt, base_prompt, n_prem_orig, n_prem,
   n_distract, role, slice` (MAN `canonical_keys`). Prompts use the shared `THM … SEQ … PRF` format.
3. Whole-proof (Robbie-style lean_seq) models: `code/textbook_problem/eval_ckpt.py --sets textbook72,textbook72_distract2
   --k 32 --temp 1.0 --max-new 400` (D2R:L143–144). It loads the run's own `source/pretrain.py` on the fork at `51604b3`
   (D2R:L137; TPLOG:L450).
4. Proof-state (Dan-style `lean_staten`) models: `cd code && ND_REGISTRY=0 uv run python
   pretrain_data/textbook72_distract_eval_dan.py --ckpt <name> --out <dir>`
   (`textbook72_distract_eval_dan.py:L5–6`).
   - It needs Dan's worktree at `~/.cache/nd-rl/fork_dan` (nd-takehome `0c492902`) and the checkpoint in `dan_ckpts/`
     (`screen_ckpt_dan.py:L43–48`).
   - It samples with `env_generate` (T 1.0, 48 steps, 256 tokens per action, batch 256) and judges with ND, **not Lean**
     (`textbook72_distract_eval_dan.py:L71–82`).
   - It writes aggregates plus the crossing / staying split and bins.
   - So yes, proof-state models can be evaluated: two of the four models were proof-state.
   - Newer Dan checkpoints (r16, guided, …) may need a newer `state_sample` than `0c492902`. Inference: untested.
   - Dan's own `state_eval.py` reads jsonl rows with `name` and `prompt` (ours:L334), so the rebuilt file should feed it
     directly with the Lean judge. Inference: Charles did not run it that way.
5. Diagnostics (proof-state only, except the ladder):
   - `elementary_prem.py` (21-problem ladder, both interfaces);
   - `elementary_trace.py` (actions through Dan's environment);
   - `elementary_forced.py` (teacher-forced block probabilities);
   - `elementary_envpr.py --ckpt <ckpt>` (environment writes the block; runs the ladder, the stratified distract10 sample
     and the distracted-72 aggregates; `elementary_envpr.py:L1–9`).
6. Generator check: `distract_by_premises.py --model robbie` or `--model dan --ckpt <ckpt>` (`distract_by_premises.py:L5–6`).
   It needs the `k12_distract10` slice, assembled from `release_2026-10-09` plus K12 from Dan's bucket (R1009:L24–27).
7. **Report the crossing (≥ 4) and staying (≤ 3) subsets separately.** For any model whose Stage-1 had ≤ 3 premises, the
   crossing 25 measure the PR-block habit, not premise selection.

**Candidate common-protocol sets** (my assessment, from the facts above):
- candidate_v0 (87), candidate_v1 (72) and batch3 (14): non-sealed and licence-tagged; leak ≤ 3 per set against K12 and
  Dan's RL pools; both interfaces already ran them. They must be re-scored, because the published baselines used the
  pre-re-cut 104 / 80 / 21 (BASE:L3). Long problems are cap-limited for lean_seq at 400 tokens (ESP:L80–81).
- textbook72 and textbook72_distract2: common to everyone, aggregate only. Prefer dev58 for cross-person comparisons, since
  Robbie RL-trained on train14 (ours:L354–355).
- The derived set's 13 plain nuances can be fed to both interfaces. The 8 prefix nuances and the 3 marker-word nuances
  cannot be fed to the proof-state model (EDBp:L32–35; T1002:L41–44).
- hand_proved_14 (20–102 lines; 0 for every model, row 3) is only a ceiling probe.
- The 21-problem elementary ladder is a two-minute PR-block check for any new Stage-1.
- Use a fixed k, T, step budget and judge across people. Charles used k 32, T 1.0, ND; our textbook72 reads use k 256,
  T 0.8, Lean.

## 8. Ambiguities and inconsistencies found

1. T0930:L4–5 says "194 … problems … 184 with a verified reference proof and 14 … no proof found". The files hold 104 + 80
   + 14 = 198 (T0930:L12–14), and 184 + 14 = 198 (derived).
2. BASE:L3 says "every proof judged by the pinned nd_verify". For the RL columns, the judge of record was Lean in the loop
   with ND re-judging (EDB:L3–13, L81). EDB:L11 says avg = `n_ok / n_tried` "as Lean counted"; EDB:L91–92 says avg is "per
   the pinned re-judging". The two disagree on only 2 proofs (EDB:L81–82), so the numbers barely move, but the label is
   inconsistent.
3. BASE lists the hash of `la_T1_best12_s2_r8` (L22), but seed 2 was cancelled (EDB:L89–90).
4. Baselines are on the pre-re-cut sets (v0 104, v1 80, batch3 21 incl. 4 hand-proved; BASE:L3, L10), not on the released
   87 / 72 / 14 files.
5. D2R:L179–181 says "the problems that survive distraction are a subset of the problems solved before; distraction created
   no new solves". D2m contradicts this:
   - DS1 "both" = 3 + 7 + 0 + 0 = 10 vs 12 distracted solves;
   - DR8 "both" = 7 + 19 + 0 + 0 = 26 vs 28;
   - so each Dan checkpoint has **2 distracted-only solves**, both in the 1-premise bin for DR8 (21 − 19), one each in the
     0- and 1-premise bins for DS1 (derived).
   "loses 21 of its 49" (D2R:L30) is therefore net. Gross: 23 lost (49 − 26), 2 gained. The staying side is net 4, gross 6.
6. "keeping 10 of the 16 crossing problems" (D2R:L38) and "6 of 16 crossing solves lost" (D2R:L289–290) assume the 10 are a
   subset of the 16. D2mE has no `both` field, so this is not verifiable from committed files.
7. "K12, the Stage-1 data behind every model here" (D2R:L226, L301) is imprecise for R384 and R768, which are cap-6-set
   pretrains (PDPLAN:L48; POOLS:L505). Both sets cap premises at 3, so the inference stands. D2res:L100–101 has the same
   wording ("a shape K12 never shows").
8. The block probability is quoted as "near 1e-24" (D2R:L244) and "about 4e-24" (D2res:L116); the raw value is 3.99e-24.
   Absolute values are under canonical names with base 0. Even 1–3-premise blocks get only ≈ 0.017 (SCR-forced), so the
   robust contrast is the share (7.7e-15 vs 1.0), as D2res:L153–154 itself says.
9. "0 of 2,048 samples" is one prompt (`P , Q , R , S ⊢ P`), 1,024 samples at each of two temperatures (SCR-forced `search`).
10. The stratified check's raw outputs (`data/pretrain_data/screens/distract_by_prem_<label>.json`, per
    `distract_by_premises.py:L8`) are **not committed**. The 0-of-180 rests on POOLS:L719–723 and PDLOG:L466. The matched
    check's output is committed (`release_2026-10-09/matched_distract.json`).
11. R1009:L40 says distract10 is "the one slice eight RL rounds do not lift (0.63 → 0.69 …, every other slice +0.2 to
    +0.4)". The POOLS table shows `k12_tail10` +0.13, cap6 +0.02, `k12_minimal` +0.01, `k12_wrong100` +0.01 and
    `k12_aux10` +0.00 (POOLS:L464–477). Several of these are near ceiling, but "every other" is loose.
12. "at any fraction" (R1009:L39; POOLS:L524) means slices of different sizes were *sampled* on an untrained base. It is not
    about training exposure (POOLS:L536–537).
13. The proposal expected 26 crossing problems (D2prop:L16, L56); there are 25 because the one 4-premise original is absent
    (D2R:L316–321).
14. Robbie's and Dan's models use different samplers, token budgets and interfaces. Charles makes no between-model claim
    (D2R:L310–311), and the within-model paired drop is the result.
15. Dan's sampler reports no per-set parse-failure rate (D2R:L185). For DR8, though, the traces locate the failure at the
    first environment action (row 22).
16. ENVPR is a re-implementation of `env_generate` (`elementary_envpr.py:L33–35`). Its original-set count is 48 of 71 vs
    49 under `env_generate` (D2R:L275–276). This is a small sampler difference within the comparison.
17. R1009:L88–89 says "three screens on all of them", then "Robbie's base on 37, Dan's two checkpoints on 10".
18. `data/textbook_problem/candidates_derived/README.md`, cited for nuance definitions (T1002:L48), is not on charles/main.
19. The distract2 run is one seed per model. Dan's r8 seeds 1 and 2 were never run (D2stat:L14–20). The follow-up is one
    checkpoint (DR8 s0) and exploratory (no proposal).
20. "90 long theorems with min_lines > 10" is not written anywhere on charles/main. It reproduces as 37 + 32 + 14 + 7 = 90
    over the four non-derived 10-02 files (§3b recount). The hand-proved lengths are not minimal.
21. No other branch I checked (`main`, `robbie-experiments`, `leon/main`, `leon/grpo-v2`, `dan`) mentions `distract2` or
    the premise-count wall, apart from our own brief. Nobody else has used the release yet.
