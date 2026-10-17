# Leon: Stage-1 results, thinking / test-time uplift, OOD checks, matched-eval tables

Notes for `peer-rl-review` (written 2026-10-17 by a read-only research sub-agent). Scope: Leon's Stage-1 arms,
the thinking-trace uplift question, the OOD headroom check and the `matched_eval/` tables. RL-method comparisons
(GRPO vs EI, RECIPE.md, v2_results*) are another slice; they appear here only where my files report them.

**Citation shorthand** (every number below carries one):
- `L:` = `origin/leon/main:` in `~/nd-rl` (tip `690817d8`, 2026-10-16 09:13 UTC).
- `D/` = `code/experiments/current/thinking_traces_20261005/`; `SUM/` = `experiment-summaries/2026-10-05-thinking-traces/`.
- `DAN:` = `origin/dan:` in `~/nd-rl` (tip `bf27b27e`). `FORK@4dcd0e4f:` = Dan's fork (nd-takehome repo, the
  commit Leon vendored and cites), read in this worktree's repo.
- "derived" = my arithmetic, shown. Percentages are quoted exactly as written in the source.

---

## 1. Files read

Core slice (all on `L:`):
- `D/OOD_CHECK.md` (86 lines, fully), `D/ood_check/EVAL_SPEC.md` (32, fully).
- `D/STAGE1_STATS.md` (347, fully); `D/stage1_stats/`: `tb72.md`, `tb72_seeds_only.md`, `tb72_null_T0e.md`,
  `tb72_goalstack.md`, `ood_charles.md`, `ood_clustered.md`, `ood_theorems.md`, `ood_textbook_dev.md`,
  `hard12_seed_control.md` (arm tables, key difference / matched-token tables, commands).
- `D/THINKING_UPLIFT.md` (315, fully); `D/ADAPTIVITY.md` (242, fully); `D/adaptivity/compare_3ckpt.md` (tables).
- `D/matched_eval/`: `final_tables.md` (fully), `matched_tb72.md`, `matched_h12.md`, `tts_uplift_tables.md`
  (fully), `confusion_tb72.md`, `confusion_charles149.md` (fully), `length_split_ynez.md` (main tables + headers),
  `source_split_ynez.md` (feature shares, closeness, headers).
- `D/PROPOSAL.md` (status, Summary, §0); `D/TRACE_AUDIT.md` (verdict, v2 addendum).

Needed for definitions / provenance (read narrowly):
- `L:SUM/README.md` (Stage-1 per-seed table, OOD summary, baseline figure of Dan's checkpoints).
- `L:D/OVERNIGHT_20261008.md` L164-307 (the only place with Stage-1 reads of the search-proof arms S1g3 / T0S).
- `L:D/EXPERIMENT_QUEUE.md` L121-147 (ynez retrain of S1g3 / T0S); `L:D/RECIPE.md` L26-72, L226-246.
- `L:D/search_traces/README.md` L6-51, L386-445; `L:D/pipeline/arms.yaml`; `L:D/pipeline/README.md` L193-198;
  `L:D/pools/hard12/README.md` L6-40; `L:D/hard712/README.md` L6-30; `L:D/test_13_20/README.md` L6-18;
  `L:D/graded_traces/README.md` L6-22; `L:D/LIT_CRITIQUE.md` L12-47, L305-328.
- `L:D/matched_eval/confusion_tb72.py` L1-16, L43-125; `L:D/matched_eval/ceiling_fig.py` L1-60;
  `L:D/matched_eval/final_tables.py` L1-38; `L:D/matched_eval/length_split.py` L90, L124.
- `L:SUM/figures/fig_ceiling_tb72.json` (textbook72 at k up to 512; numbers only exist in this JSON + figure).
- `L:code/ndbench/dash/dan_only.py` L1-21, L232, L445-446 (Leon's ndbench page of Dan's checkpoints).
- Dan sources to verify Leon's quotes: `DAN:docs/models/state_env_october.md` L1-62;
  `FORK@4dcd0e4f:artifacts/gt/analysis_stdout.txt` L40-64, L110-114, L158-164, L264-268.

---

## 2. Timeline (commit times from `git log` on `L:`; UTC unless marked)

| when | commit | what |
|---|---|---|
| 2026-10-05 21:34 | 673e763 | `OOD_CHECK.md`, `ood_check/EVAL_SPEC.md`, `PROPOSAL.md`, CPU-tested pipeline |
| 2026-10-05 23:52 | 5a8eff0 | programmatic trace generator v2, `TRACE_AUDIT.md`, 20% emptying, `arms.yaml` |
| 2026-10-06 03:15 | f6f1f40 | Stage-1 results (4 arms × 3 seeds) into `SUM/README.md` (incl. Dan Stage-1 guided line L179-180) |
| 2026-10-06 21:47 | 8644bf4 | `STAGE1_STATS.md` + `stage1_stats/` (responds to `LIT_CRITIQUE.md` C1/C3/C4, same commit) |
| 2026-10-07 06:16 | a7301e1 | `ADAPTIVITY.md`, `adaptivity/compare_3ckpt.md`, `hard12_seed_control.md`, `tb72_goalstack.md` |
| 2026-10-07 23:58 | 4608e60 | `matched_tb72.md`, `matched_h12.md` |
| 2026-10-08 05:01 | ace2ff6 | `matched_eval/final_tables.md` (first RL phase, old T0/T1v1e lineage) |
| 2026-10-08 (afternoon, PDT) | fdc77af (2026-10-09 00:02) | OVERNIGHT log: Stage 1 on honest-search proofs (S1g3, T0S) "a large win"; EI pilot |
| 2026-10-09 07:07 | be062f3 | OVERNIGHT: EI round 2 on hard712 |
| 2026-10-09 16:28 → 2026-10-10 04:44 | 25e210b, 8009299, 4418e67, 88fdf2b | `THINKING_UPLIFT.md` + `tts_uplift_tables.md`; 512-attempt ceilings; seed-1 r3; seed-2 replication |
| 2026-10-09 23:45 → 2026-10-11 05:22 | fb9b4e1 … fdf3e8f | `confusion_tb72.md`, `confusion_charles149.md` (Charles149 set introduced) |
| 2026-10-11 "about 4:48 am" (zone not stated) | — | serrano down; everything redone on ynez; S1g3/T0S retrained 2026-10-13 (`L:D/EXPERIMENT_QUEUE.md:L121-142`) |
| 2026-10-13 19:28 → 23:25 PDT | 7c1534b, 83fe63a, a538e2b | `length_split_ynez.md`, `source_split_ynez.md` |
| 2026-10-16 08:54 | 1218c35 | GRPO primary recipe (`RECIPE.md`); EI retired (RL slice) |

---

## 3. Stage-1 arms and their numbers

### 3.0 Common protocol (all Stage-1 arms)

- **Model**: from scratch, "Dan's best recipe", 24,000 steps on one RTX 3090, 41-60 min a run
  (`L:SUM/README.md:L133`). Architecture = `state_env_october` (ALiBiGPT 9.56M; `L:D/PROPOSAL.md:L23`): 6 layers,
  d 384, 8 heads, d_ff 1280 (`L:D/RECIPE.md:L61`); Dan's card gives 9,560,832 parameters
  (`DAN:docs/models/state_env_october.md:L16`). Vocabulary `lean_thinkn`, 114 ids (111 + `<think> </think> <no>`)
  (`L:SUM/README.md:L53`); S1g3 uses effort tokens (`lean_thinke`, max_len 1,024; `L:D/search_traces/README.md:L433-434`).
  One size-sweep pair at 35.6M (`L:D/OVERNIGHT_20261008.md:L214-225`).
- **Interface**: proof-state environment, per-step Markov think block, `state <think> … </think> action <eos>`
  (`L:SUM/README.md:L41`). B = per-step think budget: 0 forces an empty block, 256 "effectively free" (training
  blocks ≤ 240 tokens) (`L:SUM/README.md:L135-136`). Later reads use line forcing: close at the first line end past
  B, hard cap B + 64 (`L:D/ADAPTIVITY.md:L217-218`).
- **Data**: K12 (155k synthetic ND proofs, 2-12 lines; `DAN:docs/models/state_env_october.md:L19`); full build
  1,239,820 pairs, max 394 tokens (`L:SUM/README.md:L54-55`). Excluded by renaming class: 5 OOD tier files,
  textbook_dev58, heldout, plus textbook_train14 (`L:D/pipeline/arms.yaml:L5-6`; `L:D/pipeline/README.md:L195-198`).
  20% of traced copies emptied (`L:SUM/README.md:L98`).
- **Judge**: Lean gate on every finished (environment-completed) proof (`L:D/pipeline/README.md:L28`;
  `L:D/THINKING_UPLIFT.md:L49`; `L:SUM/figures/fig_lengthbin_baseline.caption.md:L1`). "Env accepts" ≠ "Lean
  accepts" matters a lot here: for the old T0-style models, Lean rejected 36.9% (hard12) and 55.4% (textbook72) of
  environment-accepted attempts, falling to 14.0% / 17.8% with search-proof training (`L:D/OVERNIGHT_20261008.md:L179-181`).
- **Estimator**: unbiased pass@k = 1 − C(n−c,k)/C(n,k), mean over seeds and theorems (`L:D/STAGE1_STATS.md:L28-30`).
  Temperature 0.8 (`L:SUM/README.md:L135`), max_steps 96, max_action 512, max_rej 10 (`L:D/pipeline/arms.yaml:L8`).
- **No RL** in any row of 3.1-3.3.

### 3.1 Arm definitions

| arm | Stage-1 data / trace design | source |
|---|---|---|
| T0 | K12, bare actions, no think tags ("no-think control, identical final actions, same vocabulary") | `L:D/pipeline/arms.yaml:L10-11` |
| T0e | K12, every step carries an empty `<think> </think>` block (format control) | `L:D/pipeline/arms.yaml:L12-13` |
| T1 (v2) | programmatic traces v2 (`prog_traces_v2.jsonl`) on every proof, 20% emptied | `L:D/pipeline/arms.yaml:L14-15` |
| T1v1 (v1) | the audited v1 traces (plan names the action, ex-falso padding), 20% emptied | `L:D/pipeline/arms.yaml:L16-17`; `L:D/TRACE_AUDIT.md:L14-25` |
| T0g / T1v1g | goal-stack variants of T0 / T1v1 (1 seed each) | `L:D/stage1_stats/tb72_goalstack.md:L9-19` |
| T1v1g4 ("old staged thinking, graded") | v1 traces re-written at 4 graded lengths with effort tokens `<e0..e256>` | `L:D/graded_traces/README.md:L6-22`; `L:D/OVERNIGHT_20261008.md:L67, L172` |
| **T0S** | the honest search's own proofs (`searchtrace.py`, e256 proofs emitted as plain K12-style records), bare actions | `L:D/search_traces/README.md:L388-389, L400-402, L419-422` |
| **S1g3** | honest-search thinking traces on the same proofs, effort levels 0/64/256 mixed 20/40/40, textbook72 excluded | `L:D/search_traces/README.md:L416-418`; `L:D/RECIPE.md:L56-60`; `L:D/THINKING_UPLIFT.md:L31` |

Search proofs differ from K12 references: identical to the reference in 35%, mean length 0.85× the reference's
(`L:D/search_traces/README.md:L37`); genuine (non-ex-falso) dead ends in only 12.9% of e256 decision blocks, so the
generator "fails G2" (`L:D/search_traces/README.md:L28-31`).

### 3.2 Main table (Stage 1, before any RL)

T = 0.8 where stated (textbook72 Stage-1 reads `L:SUM/README.md:L135`; THINKING_UPLIFT L46; ADAPTIVITY L217); the
OOD / hard12 / OVERNIGHT reads do not restate T (T column: "n.s." = not stated). "tb72" = textbook72 (72); "Charles long" = Tier A `charles_long_reach` (80 of Charles's 90
long theorems, see §6); hard12 = sealed `hard12_test_1k`; 13–20 = 986 valid items. pass@1 / pass@5 / pass@k-max.

| arm | data / trace design | textbook72 | Charles long (Tier A, 80) | hard12 test (1,000) | 13–20 (986) | k | T | seeds | source |
|---|---|---|---|---|---|---|---|---|---|
| T0 | K12 no think | 17.2% [10.4, 25.1] / 26.0% / pass@256 45.4% (s0/s1/s2 pass@256 43.1 / 47.2 / 45.8%) | 1.4% / 3.5% / pass@16 5.6% | T0 s1-2: 42.4% / 75.2%; T0 s0 (pool filter model): 27.8% / 71.6% | 0.8% pass@1 | tb72 256; Charles 16; hard12 32 | 0.8 (tb72); others not restated | tb72 3; Charles 2 (s0,s1); hard12 2+1 | `L:D/stage1_stats/tb72.md:L11`; `L:SUM/README.md:L143`; `L:D/stage1_stats/ood_charles.md:L11`; `L:D/stage1_stats/hard12_seed_control.md:L11-12`; `L:D/OVERNIGHT_20261008.md:L171` |
| T0e | K12, empty think | 13.6% / 20.7% / 39.4% (37.5 / 37.5 / 43.1%) | 1.1% / 2.5% / 3.8% | – | – | 256; 16 | 0.8 (tb72) | 3; Charles 1 | `L:D/stage1_stats/tb72.md:L12`; `L:SUM/README.md:L144`; `L:D/stage1_stats/ood_charles.md:L16` |
| T1 B0 | v2 traces, think forced empty | 13.1% / 20.7% / 38.9% (41.7 / 36.1 / 38.9%) | 0.2% / 1.0% / 1.9% | – | – | 256; 16 | 0.8 (tb72) | 3; 2 | `L:D/stage1_stats/tb72.md:L13`; `L:SUM/README.md:L145`; `L:D/stage1_stats/ood_charles.md:L12` |
| T1 B64 | v2 traces | – | 0.2% / 1.1% / 2.5% | – | – | 16 | n.s. | 2 | `L:D/stage1_stats/ood_charles.md:L13` |
| T1 B256 | v2 traces | 15.6% / 27.9% / 51.4% (54.2 / 47.2 / 52.8%) | 0.5% / 2.0% / 3.8% | – | – | 256; 16 | 0.8 (tb72) | 3; 2 | `L:D/stage1_stats/tb72.md:L14`; `L:SUM/README.md:L146`; `L:D/stage1_stats/ood_charles.md:L14` |
| T1v1 B0 | v1 traces, think forced empty | 13.1% / 20.2% / 36.1% (34.7 / 34.7 / 38.9%) | – | 30.2% / 61.7% | – | 256; 32 | 0.8 (tb72) | 3 | `L:D/stage1_stats/tb72.md:L15`; `L:SUM/README.md:L147`; `L:D/stage1_stats/hard12_seed_control.md:L13` |
| T1v1 B256 | v1 traces | 16.8% / 29.3% / **56.0%** (59.7 / 51.4 / 56.9%); seed 0 alone 19.1% / 33.3% | 1.4% / 5.3% / 10.0% | 42.6% / 80.8% | – | 256; 16; 32 | 0.8 (tb72) | 3; Charles 1 | `L:D/stage1_stats/tb72.md:L16`; `L:SUM/README.md:L148`; `L:D/stage1_stats/tb72_goalstack.md:L17`; `L:D/stage1_stats/ood_charles.md:L17`; `L:D/stage1_stats/hard12_seed_control.md:L14` |
| T0 guided (logical redraws) | T0 + `step_check` redraws | – | **4.9%** / 10.6% / 16.2% | – | – | 16 | n.s. | 2 | `L:D/stage1_stats/ood_charles.md:L15` |
| T1 guided + B256 | T1 + redraws | – | 4.6% / **14.1%** / **23.8%** | – | – | 16 | n.s. | 1 | `L:D/stage1_stats/ood_charles.md:L18` |
| T0g / T1v1g B0 / T1v1g B256 | goal stack | 15.3% / 22.9%; 14.2% / 19.4%; 17.1% / 25.8% | – | – | – | 256 | 0.8 (tb72) | 1 | `L:D/stage1_stats/tb72_goalstack.md:L12, L14, L16` |
| T1v1g4 (graded e256) | graded v1 traces | 17.1% pass@1 | – | 48.7% | 0.7% | not stated | n.s. | "2 seeds each" | `L:D/OVERNIGHT_20261008.md:L166, L172` |
| **T0S** | search proofs, no think | **31.6%** pass@1 (serrano s0/s1 30.8 / 32.3; ynez s0/s1/s2 30.9 / 33.3 / 31.0) | not read | **68.4%** | **4.7%** | not stated | n.s. | 2 (ynez: 3) | `L:D/OVERNIGHT_20261008.md:L173`; `L:D/EXPERIMENT_QUEUE.md:L141-142` |
| **S1g3, B256** | search proofs + search-trace thinking | **41.8%** pass@1 (serrano s0/s1 40.7 / 43.0; ynez s0/s1/s2 43.8 / 39.6 / 32.3) | not read | **75.9%** | **7.3%** | not stated | n.s. | 2 (ynez: 3) | `L:D/OVERNIGHT_20261008.md:L174`; `L:D/EXPERIMENT_QUEUE.md:L140, L142`; `L:D/RECIPE.md:L70-72` |

Checks (derived): serrano means (40.7 + 43.0)/2 = 41.85 → 41.8 and (30.8 + 32.3)/2 = 31.55 → 31.6 match the OVERNIGHT
table. Per-seed pass@256 means: (59.7 + 51.4 + 56.9)/3 = 56.0; (54.2 + 47.2 + 52.8)/3 = 51.4; (43.1 + 47.2 + 45.8)/3
= 45.37. In 72ths: 59.7% = 43/72, 51.4% = 37/72, 56.9% = 41/72, 43.1% = 31/72, 47.2% = 34/72, 45.8% = 33/72.

Other Stage-1 reads:
- **textbook72 by reference length** (pass@256, 3-seed means; bins 1-5 / 6-10 / 11-15 / 16+ / train14): T0 100 / 72 /
  27 / 0 / 43%; T1 100 / 79 / 29 / 8 / 52%; T1v1 100 / 88 / 38 / 3 / 57% (`L:SUM/README.md:L162-166`).
- **OOD 840** (charles_long_reach + 4 generated families, k 16, theorems clustered): T0 1.8% / 5.1% pass@16 (140
  tokens/attempt); T1 B0 1.1% / 4.3%; T1 B256 1.3% / 5.1% (370); T0 guided 4.1% / 11.7% (426); T1v1 B256 (1 seed)
  1.6% / 6.2% (634); T1 guided + B256 (1 seed) 4.1% / 15.5% (1328) (`L:D/STAGE1_STATS.md:L171-178`;
  `L:D/stage1_stats/ood_clustered.md:L11-18`).
- **textbook_dev inside the OOD reads** (58, k 16): T0 16.3% / pass@16 31.9%; T1 B256 13.7% / 37.1%; T0 guided 26.0% /
  43.1%; T1v1 B256 (1 seed) 17.7% / 44.8%; T1 guided B256 (1 seed) 30.5% / 55.2% (`L:D/stage1_stats/ood_textbook_dev.md:L11-18`).
- **Old SUM summary of OOD** (k 16, pass@16, "all 898 theorems" = 840 + dev58): T0 s0/s1 7.0% / 6.7%; T1 B256 8.4% /
  5.9%; T1v1 s0 B256 8.7%; T0 guided 13.7% / 13.7%; T1 s0 guided + B256 18.0% (`L:SUM/README.md:L168-177`).
- **hard712 dev** (500, k 8, pass@1 / solved within 8): S1g3 37.7 / 72.2; T0S 30.2 / 59.8 (`L:D/OVERNIGHT_20261008.md:L248-252`).
- **35.6M pair (seed 0)**: thinking gain (S1g3 − T0S, pass@1) 13–20 +1.5 [+0.2, +2.6], hard12 +13.8, textbook72
  +8.1, vs 9.6M (2 seeds) +2.6 [−0.7, +6.0], +7.5, +10.3 (`L:D/OVERNIGHT_20261008.md:L217-222`). Read: size not
  the binding constraint (`L:D/OVERNIGHT_20261008.md:L224-225`).

### 3.3 What Stage-1 trace design does (answer to the slice question)

- **Search proofs (proof style), T0S − T0, pass@1**: +26.0 [+22.8, +29.4] hard12, **+14.4 [+8.0, +21.4] textbook72**,
  +3.9 [+2.4, +5.5] 13–20 (`L:D/OVERNIGHT_20261008.md:L176`). Mechanism claimed: Lean rejections of env-accepted proofs
  fall (36.9 → 14.0% hard12; 55.4 → 17.8% textbook72) (`L:D/OVERNIGHT_20261008.md:L179-181`).
- **Search-trace thinking, S1g3 (B256) − T0S, pass@1, per attempt (not compute-matched)**: +7.5 [+2.3, +12.6] hard12,
  **+10.3 [+3.7, +17.2] textbook72**, +2.6 [−0.7, +6.0] 13–20 (not resolved) (`L:D/OVERNIGHT_20261008.md:L177-178`).
  Combined S1g3 vs T0 on textbook72: 41.8 vs 17.2% pass@1 (derived difference +24.6 pp; mixes seed sets: T0 is
  3 seeds, S1g3 2).
- **Programmatic (v1/v2) thinking on K12 proofs (T1/T1v1 vs T0)**: no resolved gain at pass@1 or pass@5; resolved only
  T1v1 B256 at pass@256, +10.6 [+3.7, +18.1] (`L:D/STAGE1_STATS.md:L110-118, L289-290`). Forcing the block empty
  costs 12.5 pp (T1) and 19.9 pp (T1v1) at pass@256 (`L:SUM/README.md:L183-184`), i.e. the models use the think block.
- **Charles's long set**: no S1g3 / T0S Stage-1 read on any Charles set exists in Leon's files (searched
  `v2_results*.md`, `RECIPE.md`, OVERNIGHT, EXPERIMENT_QUEUE). For T0/T1 on Tier A (k 16) plain thinking is not
  better: T1 B256 − T0 at pass@1 −0.8 [−2.5, +0.2] (`L:D/STAGE1_STATS.md:L223`); guided redraws are what help
  (T0 guided − T0 at pass@16 +10.6 [+2.5, +20.0], t-check [−7.7, +28.9], not resolved; `L:D/STAGE1_STATS.md:L224`).
  Only 25 of 80 Tier-A theorems are informative (55 at 0% in all 8 cells) (`L:D/STAGE1_STATS.md:L235`).

### 3.4 After RL, for reference (models built on these Stage-1 inits)

S1g3 → EI and T0S → EI lineage ("current"): EI r1 on rl_hard12, r2 on hard712 5k sample (a), r3 on disjoint 5k (b)
(`L:D/THINKING_UPLIFT.md:L34`). Thinking read at B64, baseline at B0; textbook72 at k 64 (`L:D/THINKING_UPLIFT.md:L44-47`).

| model (seed) | textbook72 pass@1 | textbook72 pass@64 | 13–20 pass@1 (k: think 32 / base 64) | 13–20 pass@k-max | source |
|---|---|---|---|---|---|
| S1g3 → EI r2, B64 (s0) | 67.0% [57.4, 76.3] | 83.3% | 30.2% | 73.0% (k32) | `L:D/matched_eval/tts_uplift_tables.md:L11, L21` |
| T0S → EI r2, B0 (s0) | 62.8% [53.1, 72.2] | 77.8% | 24.3% | 71.1% (k64) | `…tts_uplift_tables.md:L12, L22` |
| S1g3 → EI r2, B64 (s1) | 71.8% [62.8, 80.2] | **90.3%** | 31.0% | 76.8% | `…tts_uplift_tables.md:L14, L24` |
| T0S → EI r2 (s1) | 60.1% [50.1, 69.9] | 81.9% | 24.2% | 65.4% | `…tts_uplift_tables.md:L15, L25` |
| S1g3 → EI r3, B64 (s1) | **73.3%** [64.0, 81.8] | 86.1% | 34.5% | 79.8% | `…tts_uplift_tables.md:L19, L26` |
| T0S → EI r3 (s1) | 64.7% [55.3, 73.8] | 83.3% | 25.5% | 68.0% | `…tts_uplift_tables.md:L20, L27` |
| S1g3 → EI r3, B64 (s2) | – (per attempt +6.3 over base) | – | 37.9% | – | `L:D/THINKING_UPLIFT.md:L302, L306` |
| T0S → EI r3 (s2) | – | – | 27.6% | – | `L:D/THINKING_UPLIFT.md:L302` |

Textbook72 512-attempt ceiling read (EI r2 s0 pair; only in a figure JSON; `L:D/matched_eval/ceiling_fig.py:L6-12, L44-52`):
thinking B64 pass@1 0.667 (L15), pass@64 0.828 (L51), **pass@256 0.845 (L63)**, pass@512 0.847 = 61/72 (L69);
baseline B0 pass@1 0.631 (L77), pass@64 0.773 (L113), pass@256 0.785 (L125), pass@512 0.792 = 57/72 (L131);
tokens/attempt 483.2 vs 177.6 (L8-9); at 512: only thinking 4, only baseline 0, both 57 (L1026-1028) — all in
`L:SUM/figures/fig_ceiling_tb72.json`. Derived: neither = 72 − 61 = 11.

Old lineage (T0 / T1v1e → EI / GRPO on `rl_hard_filtered`, 2026-10-07/08), textbook72 pass@1 at most ~35%: e.g. EI
no-think r2 32.4%, GRPO no-think it78 32.6%, EI effort r2 B256 31.6%, GRPO one budget + token cost it78 34.7%
(`L:D/matched_eval/final_tables.md:L175, L181, L179, L199`); 13–20 pass@1 at most 12.8% (GRPO graded it78 B64;
`…final_tables.md:L247`). The jump to 60-75% comes with the search-proof Stage 1 plus hard712 (see §7 caveat:
hard712 was designed from a dev58 gap analysis).

### 3.5 Leon's best numbers per k (my slice files)

| set | k | best value | checkpoint / protocol | source |
|---|---|---|---|---|
| textbook72 | 1 | Stage 1: 41.8% (S1g3 B256, 2 seeds); best single Stage-1 seed 43.8% (ynez s0) | pre-RL | `L:D/OVERNIGHT_20261008.md:L174`; `L:D/EXPERIMENT_QUEUE.md:L140` |
| textbook72 | 1 | post-RL EI: 73.3% (S1g3 → EI r3 s1, B64, k64 read) | 1 seed | `L:D/matched_eval/tts_uplift_tables.md:L26` |
| textbook72 | 1 | post-RL GRPO: 75.5% (v2 thinking + verifier (stop), seed 0, B64); 3-seed 74.8% [65.1, 83.8] | RL slice | `L:D/matched_eval/confusion_tb72.md:L15`; `L:D/matched_eval/length_split_ynez.md:L51` |
| textbook72 | 5 | Stage 1: 29.3% (T1v1 B256, 3 seeds); 33.3% (T1v1 s0); S1g3/T0S pass@5 not reported | pre-RL | `L:D/stage1_stats/tb72.md:L16`; `L:D/stage1_stats/tb72_goalstack.md:L17` |
| textbook72 | 5 | post-RL: 82.1% [73.4, 89.5] (plain GRPO v2 thinking, 3 seeds, B64); RECIPE.md arm 82.3% | RL slice | `L:D/matched_eval/length_split_ynez.md:L143`; `L:D/RECIPE.md:L38` |
| textbook72 | 64 | EI: 90.3% (= 65/72; S1g3 → EI r2 s1, B64); GRPO: 66/72 = 91.7% (derived: 62 both + 4 GRPO-only; v2 thinking + verifier (stop) s0) | 1 seed each | `…tts_uplift_tables.md:L24`; `L:D/matched_eval/confusion_tb72.md:L12, L15` |
| textbook72 | 256 | Stage 1: 56.0% (T1v1 B256, 3 seeds; s0 59.7%); post-RL: 84.5% (S1g3 → EI r2 s0, B64, 512-attempt read) | | `L:D/stage1_stats/tb72.md:L16`; `L:SUM/figures/fig_ceiling_tb72.json:L63` |
| Charles long (Tier A 80) | 1 / 5 / 16 | 4.9% (T0 guided, 2 seeds) / 14.1% / 23.8% (T1 guided + B256, 1 seed); plain best 1.4% / 5.3% / 10.0% | Stage 1, k 16 max; no k ≥ 64 read | `L:D/stage1_stats/ood_charles.md:L11-18` |
| Charles149 | 1 | 70.2% [63.5, 76.7] (GRPO + verifier (stop), 3 seeds); EI best 63.7% (EI + verifier, 3 seeds); RECIPE arm 70.5% | RL, B64, k64 reads | `L:D/matched_eval/length_split_ynez.md:L57`; `L:D/RECIPE.md:L39` |
| Charles149 | 5 | 79.1% [73.0, 84.8] (plain GRPO, 3 seeds); EI 75.9% (EI + verifier) | RL | `…length_split_ynez.md:L149, L57` |
| Charles149 | 64 | 132/149 = 88.6% (derived: 121 + 11; "current" GRPO seed 1); EI best 124/149 = 83.2% (derived: 120 + 4; v2 EI thinking curriculum-only s0) | 1 seed | `L:D/matched_eval/confusion_charles149.md:L12, L13` |
| Charles149 | 256 | no read | | |

---

## 4. Thinking / test-time uplift findings (and what is matched)

### 4.1 Stage 1, T1/T1v1 vs T0 on textbook72 (`STAGE1_STATS.md`; 3 vs 3 seeds; k 256; hierarchical bootstrap + t-check)

- **Matched on**: sampled tokens per theorem = think + `</think>` + action + rejected redraws, prefill excluded;
  k* = X / tokens-per-attempt, log-k interpolation (`L:D/STAGE1_STATS.md:L66-71`).
- Per attempt vs T0 (pp): T1 B256 −1.6 [−5.0, +1.5] pass@1, +1.9 pass@5, +6.0 [−0.9, +13.4] pass@256; T1v1 B256 −0.4,
  +3.4 [−2.1, +9.2], **+10.6 [+3.7, +18.1]** (`L:D/STAGE1_STATS.md:L112-113`).
- Within model, B256 − B0: T1 +2.5 / +7.1 / +12.5 (all resolved); T1v1 +3.7 (t-check not resolved) / +9.2 / +19.9
  (`L:D/STAGE1_STATS.md:L124-125`).
- Matched tokens vs T0 at 1k / 3k / 10k / 29k: T1 B256 −4.7 (p 0.06) / −1.6 / +1.5 / +2.3†; T1v1 B256 −5.0 (p 0.04) /
  −1.8 / +2.3 / +4.5† (`L:D/STAGE1_STATS.md:L147-148`). † = T0 clamped at pass@256 in 43% of draws, favouring thinking
  (`L:D/STAGE1_STATS.md:L153-155`). Conclusion: "no support at any budget at Stage 1"
  (`L:D/STAGE1_STATS.md:L311-312`).
- Null check: T0e (never thinks) B256 − B0 at pass@1 / 5 / 256: −0.2 / −0.6 / +2.1 pp, all covering 0
  (`L:D/STAGE1_STATS.md:L78-83`).
- T0 − T0e = 3.6 pp at pass@1 is "the same size as every thinking effect against T0" (`L:D/STAGE1_STATS.md:L313-314`).
- Power: ~9 seeds per arm needed to resolve 3 pp at pass@1 on textbook72 (`L:D/STAGE1_STATS.md:L268-271`).

### 4.2 Stage 1, OOD 840 (k 16; 2 seeds for T0/T1/T0 guided, 1 for others)

- T1 B256 − T0: −0.5 pp pass@1 (resolved), −1.7 pp at matched 0.5-2k tokens (resolved) (`L:D/STAGE1_STATS.md:L184, L195, L301-302`).
- T0 guided − T0: +2.3 / +4.5 / +6.5 pp at pass@1/5/16 (resolved); guided beats T1 B256 at every k and budget
  (`L:D/STAGE1_STATS.md:L187-188, L304`). "At equal tokens, thinking is worth less than more samples"
  (`L:D/STAGE1_STATS.md:L305-306`).

### 4.3 Stage 1, hard12 seed control (k 32; 1,000 sealed 7–12-line items)

T1v1 B256 − T0 s1-2: +0.2 [−3.0, +3.2] pass@1, +5.6 [+2.9, +8.5] pass@5; matched tokens −15.2 at 1k, −4.5 at 3k
(`L:D/stage1_stats/hard12_seed_control.md:L24-25, L48`). T0 s0 is the pool's filter model and is depressed by 14.7 pp
at pass@1 (`…hard12_seed_control.md:L20`).

### 4.4 S1g3 vs T0S, Stage 1 and early EI (per attempt only)

Stage 1: see §3.3. After EI r1 (rl_hard12): thinking − no-think 13–20 +1.3 [−0.8, +3.3] pass@1, +4.2 [+1.0, +7.5]
pass@5, +2.3 [+0.3, +4.3] at B64; textbook72 +5.2 n.s.; hard12 +1.1 n.s. (`L:D/OVERNIGHT_20261008.md:L241-246`).
After r2 on hard712: +3.2 [+1.1, +5.5] pass@1 at B256, +6.4 [+4.3, +8.6] at B64 (13–20, k 8 reads)
(`L:D/OVERNIGHT_20261008.md:L279-281`).

### 4.5 THINKING_UPLIFT (S1g3 → EI vs T0S → EI, the headline TTS question)

- **Design**: pair differs only in Stage-1 traces; same EI rounds (`L:D/THINKING_UPLIFT.md:L27-36`). One training seed
  per arm per cell; intervals = 4,000 problem bootstraps, no seed variance (`L:D/THINKING_UPLIFT.md:L54-55`).
- **Matched on**: sampled tokens per problem (prefill excluded) (`L:D/THINKING_UPLIFT.md:L49-57`); sensitivity with
  forward tokens (sampled + prefill) (`L:D/THINKING_UPLIFT.md:L128-142`); wall-clock check: k 32 thinking ≈ k 64
  baseline time (`L:D/THINKING_UPLIFT.md:L198-199`). Cost ratio: thinking attempt = 2.45–3.05× sampled tokens
  (`L:D/THINKING_UPLIFT.md:L59`), 1.36–1.67× forward tokens (`L:D/THINKING_UPLIFT.md:L130`).
- **13–20 (986), thinking B64 − baseline (pp)**, per attempt / 1k / 2k / 4k / 8k / 16k:
  r1 s0 +1.3 / −11.1 / −9.6 / −7.2 / −4.7 / −2.3; r2 s0 +5.9 / −8.5 / −6.1 / −3.9 / −2.5 / −1.6; r2 s1 +6.8 / −6.5 /
  −3.4 / +0.7 / **+4.6** / **+7.6**; r3 s0 +2.9 / −13.9 / −12.6 / −10.7 / −8.8 / −7.1
  (`L:D/THINKING_UPLIFT.md:L71-74`); r3 s1 +9.0 / −5.0 / −1.4 / +2.6 / **+6.2** / **+8.2** (`L:D/THINKING_UPLIFT.md:L279-280`);
  r3 s2 +10.3 (37.9 vs 27.6%) / −4.8 / −0.1 / +3.9 / **+6.8** / **+8.4** (`L:D/THINKING_UPLIFT.md:L302-304`).
- Round-3 pooled mean curve (problem bootstrap only): −7.9 at 1k, −4.7 at 2k, −1.4 at 4k, +1.4 at 8k,
  **+3.2 [+0.8, +5.7] at 16k** (`L:D/THINKING_UPLIFT.md:L309-311`).
- **textbook72**: r2 s0 +4.2 per attempt, +3.5 [+0.4, +7.5] at 8k; r2 s1 +11.7 per attempt, +5.4 to +6.2 from 1k to 8k
  (`L:D/THINKING_UPLIFT.md:L75-76`); r3 s1 +8.6 per attempt, +1.5 to +3.0 matched (n.s.) (`L:D/THINKING_UPLIFT.md:L282`);
  r3 s2 +6.3 [+0.1, +12.8] per attempt, −0.1 to +6.0 matched (n.s.) (`L:D/THINKING_UPLIFT.md:L306`). 16k cells clamped
  (baseline's 64 attempts cost < 16k) (`L:D/THINKING_UPLIFT.md:L82-85`).
- **hard712 dev (in-distribution)**: behind at 1k (−3.0, −2.5), tied from 2k (`L:D/THINKING_UPLIFT.md:L160-161`).
- **Thinking off (B0) / best-budget envelope**: r2 s0 B0 24.0% vs baseline 24.3% per attempt, best budget −3.1 at 1k,
  −1.1 at 16k; r2 s1 B0 15.9%; textbook72 r2 s0 B0 47.9% (−14.9 vs baseline) (`L:D/THINKING_UPLIFT.md:L100-109`).
- **Why B64**: per attempt on 13–20 (k 8 reads) r2 s0: B0 24.0%, B64 30.7%, B256 27.6%, baseline 24.3%
  (`L:D/THINKING_UPLIFT.md:L117-120`); chosen on the same sets (`L:D/THINKING_UPLIFT.md:L183-187`).
- **512-attempt ceilings** (r2 s0, random 250 of 986 13–20 problems): pass@1 32.6 vs 26.1%; pass@512 89.2 vs 83.2%,
  +6.0 [+0.4, +11.6]; equal tokens 1k −8.5, 16k +2.2 [−3.4, +8.0], 150k +2.5 [−2.9, +8.0]
  (`L:D/THINKING_UPLIFT.md:L240-264`).
- **Verdict (3 seeds)**: baseline ahead or tied at ≤ 2k tokens for every seed; at 8–16k thinking ahead by ~7–8 pp in
  2 of 3 seeds and behind in the third; "which Stage-1 seed you get decides it" (`L:D/THINKING_UPLIFT.md:L313-315`).

### 4.6 ADAPTIVITY (old T1v1e lineage; 672 targets, k 16; effort levels e0/e16/e64/e256)

- Not compute-matched; per-level pass@1 / pass@5 over 672 targets: it0 (effort-expanded T1v1, never trained on effort
  tokens) e0 24.1 / 49.1, e256 38.6 / 69.4; EI r1 e0 62.0 / 78.9, e256 69.7 / 88.7; GRPO it39 e0 77.9 / 83.4, e256
  79.5 / 88.1 (`L:D/ADAPTIVITY.md:L145-150`). e256 gain over e0: +14.5 / +7.8 / +1.6 pp; think tokens per attempt
  420 / 484 / 41 (`L:D/ADAPTIVITY.md:L156-158`).
- Low budgets hurt: e16 − e0 = −10.9 pp (it0), −25.7 pp (EI r1) (`L:D/ADAPTIVITY.md:L172-173`).
- Caveats: 600 of 672 targets are RL training targets (`L:D/ADAPTIVITY.md:L209-213`); grpo_it39 used the buggy
  full-vocabulary GRPO loss (`L:D/ADAPTIVITY.md:L139-141`).
- textbook-dev rows (58; outside the RL pool): e256 − e0 gain +8.8 (it0), +11.0 (EI r1), +6.7 (GRPO it39)
  (`L:D/adaptivity/compare_3ckpt.md:L86`).

### 4.7 matched_eval tables (old T0/T1v1e lineage; single seeds unless noted)

- "Matched" has two meanings: (a) training attempts (EI round r ↔ GRPO iteration 39r) (`L:D/matched_eval/final_tables.md:L10`;
  `L:D/matched_eval/confusion_tb72.md:L3-4`); (b) sampled tokens per problem at inference (`…final_tables.md:L76-78`).
- Thinking (B256) − no-think GRPO at matched tokens, textbook72: −11.2 to +5.2 pp at 1k/2k, no interval excluding 0 in
  thinking's favour (`…final_tables.md:L96-109`); hard12: at most +2.1 [+0.9, +3.5] (`…final_tables.md:L84`).
- Stage-1 reference rows in `matched_tb72.md`: T0 s0 18.6% / 27.0%, T1v1 B256 19.1% / 33.3%; EI_T0_r2 32.4% / 44.8%
  (`L:D/matched_eval/matched_tb72.md:L11-21`). `matched_h12.md`: T0 s1-2 42.4% / 75.2%; T1v1 B256 (1 seed) 43.2% /
  81.1%; GRPO_T0_it78 92.8% / 96.6% (`L:D/matched_eval/matched_h12.md:L11-21`).
- `length_split_ynez.md` / `source_split_ynez.md` (3 seeds, GRPO recipe v2 vs EI, thinking at B64): GRPO's gain over EI
  is on human-written sets (textbook72 + Charles149, +5.8 [+1.3, +10.1] pass@1 for the verifier pair;
  `L:D/matched_eval/length_split_ynez.md:L74`) and negative on generated 13–20 (−1.9 [−3.7, −0.1]; L62); the
  human − generated gap at equal length is +9.6 [−0.8, +19.2] on 13–20 (p 0.066; L86). RL slice; noted for completeness.

---

## 5. Numbers of Dan's models quoted in Leon's files

### 5.1 `OOD_CHECK.md` (written 2026-10-05; "No GPU job was run for this note; every number comes from stored results or CPU-only analysis", `L:D/OOD_CHECK.md:L8-11`)

| quoted (Leon) | Dan checkpoint / protocol | provenance | verified? |
|---|---|---|---|
| textbook72 k256: 72.2 / 70.8 / 72.2% (`L:D/OOD_CHECK.md:L38`) | best-state r8 s0/s1/s2 (`la_T1_best12_s{0,1,2}_r8`), plain, 256 attempts, judge "Lean 4 core alone" | copied from `docs/models/state_env_october.md`, which states **52 / 51 / 52 of 72** (`DAN:docs/models/state_env_october.md:L21, L26, L33-34`) | yes: 52/72 = 72.2%, 51/72 = 70.8% |
| holdout250 239/250 (95.6%), long pool 377/380 (99.2%), ≥17 lines 21/21, RL targets 4,369/4,495 (97.2%), all pass@256 (`L:D/OOD_CHECK.md:L15-16`) | best-state seed 0, r8 | same card: 239 / 377 of 380 / 21 of 21 (s0) (`DAN:…state_env_october.md:L36-38`); card gives RL targets as "97.1–98.0% solved by r8" (L56) | first three yes; 4,369/4,495 not checked per seed (consistent range) |
| textbook_dev (58) pass@1 40.8% (best-state s0 RL) / 12.8% (pretrained); k2048 79.3% / 51.7% (`L:D/OOD_CHECK.md:L20, L39`) | `la_T1_best12_s0_r8` and `stage1_best12_s0_b1200` | **Leon's own ndbench measurement** ("ndbench `dash_danonly_v6` Fig. 3"): ndbench's Dan-only page runs Dan's twelve best-state checkpoints, judge "Lean (lean_v2)" (`L:code/ndbench/dash/dan_only.py:L1-8, L232`); k = 2048 runs are **adaptive** ("draw more for unsolved theorems, so their samples are not item-uniform", L445-446) | figure/store not in git; 79.3% = 46/58, 51.7% = 30/58 (derived) |
| Charles long (>10 lines, n 90), trajectory r8 s0/s1/s2, plain pass@1 8.5 / 7.7 / 13.0%, k256 42.2 / 34.4 / 46.7%; guided-logical 16.3 / 13.4 / 20.9%, k256 55.6 / 50.0 / 52.2% "(not compute-matched)" (`L:D/OOD_CHECK.md:L18, L40-41`) | Dan's guided-tts, trajectory seeds r8, 256 attempts | copied from "fork `artifacts/gt/analysis.json`" | yes: `FORK@4dcd0e4f:artifacts/gt/analysis_stdout.txt:L264` (k=1) and `:L268` (k=256) carry exactly these values, in the "attempt-matched" block (header L263); the "tokens-matched" block (header L59) gives logical 10.3/9.3/15.3 at k=1 and 53.3/47.1/50.1 at k=256 (L60, L64) |
| "+9.1 pp from guided redraws at matched tokens" (`L:D/OOD_CHECK.md:L18-19`) | best12 (cap 12) long, IQM over 3 seeds at k 64 plain-equivalent | guided-tts | yes: `FORK@4dcd0e4f:artifacts/gt/analysis_stdout.txt:L63` (tokens-matched block, header L59; ΔL IQM +9.1 [+3.7, +13.5]) |
| Charles >20 lines (n 23): r8 plain 0.3–1.1 / logical 2.9–3.3% pass@1; k256 8.7% / 8.7–17.4% (`L:D/OOD_CHECK.md:L42`) | trajectory r8 | "same" (guided-tts analysis) | not checked (8.7% = 2/23, 17.4% = 4/23, derived) |
| hand_proved_14: 0% at k256, every arm (`L:D/OOD_CHECK.md:L43`) | r8 | guided-tts `numbers.md` | card: 0 of 14 (`DAN:…state_env_october.md:L47`) |
| group C (36/35/28): pass@1 ≈0; k256 11.1 / 5.7 / 14.3%; k2560 27.8 / 20.0 / 17.9% (`L:D/OOD_CHECK.md:L44`) | r8 | "mcts-a summary" | not checked (= 4/36, 2/35, 4/28; 10/36, 7/35, 5/28, derived) |
| laws s=4/6/8 (240/240/211), best-state s0 r8: pass@1 38.3 / 11.9 / 2.4%; k16 56.7 / 25.8 / 10.0% (`L:D/OOD_CHECK.md:L45`) | best-state s0 r8 | ndbench store (Leon's measurement) | not checked |
| reorder_or n=4 (40): 0.5% / k16 2.5%; reorder_and n=4/5: 6.7 / 0.2%, k16 37.5 / 2.6% (`L:D/OOD_CHECK.md:L46-47`) | r8 | ndbench store | not checked |
| ≥4 premises: ≤2.3% pass@1 (`L:D/OOD_CHECK.md:L48`) | r8 | ndbench Table 1 | not checked |

Purpose: a headroom survey ("Where the SOTA fails today"), not a head-to-head with Leon's models. The calibration eval
that would have measured Dan's `la_T1_best12_s0_r8` and `stage1_best12_s0_b1200` (plain vs logical, k 64, T 0.8,
max_action 512, max_steps 96, max_rej 10, on Tier A + Tier B + case_product, 840 theorems) is "proposed, not run;
needs Leon's approval" (`L:D/OOD_CHECK.md:L77-86`; `L:D/ood_check/EVAL_SPEC.md:L1, L10-18`).

### 5.2 Other places

- `L:D/PROPOSAL.md:L96-101`: Dan's guided-tts, logical redraws beat plain at matched sampled tokens on 90 long theorems,
  "IQM +9.1 pp at cap 12 and +8.3 pp at cap 6, in 6 of 6 models"; structural redraws "|Δ| ≤ 1.2 pp". Copied from
  Dan's guided-tts summary. +9.1 and +8.3 verified at tokens-matched k 64 (`FORK@4dcd0e4f:artifacts/gt/analysis_stdout.txt:L59, L63, L113`);
  the "≤ 1.2" bound holds at k 64 (ΔS −0.8 / +0.8) but not at every k in the same file (best12 long k=1 ΔS IQM −1.5,
  L60) — it presumably refers to the summary's headline k.
- `L:D/PROPOSAL.md:L109-113` and `L:SUM/README.md:L32-36` re-quote OOD_CHECK (pass@1 7.7–13.0%, textbook_dev 40.8%,
  "95.6-100% at pass@256" in-distribution).
- `L:SUM/README.md:L179-180`: "Dan's Stage-1 checkpoint with guided redraws at k 64 (about 24k tokens) gets 20.0% and
  23.8%" (on Charles's long problems and commute), compared with Leon's T1 guided + B256 "23.8% on Charles's long
  problems and 25.0% on commute, at about 21k tokens per theorem" (L179). Added 2026-10-06 03:15 (commit f6f1f40).
  **No table, run directory or command in git documents the Dan numbers**; they match the EVAL_SPEC arm
  `stage1_best12_s0_b1200 … --arm logical --k 64` that OOD_CHECK called "not run" a day earlier. Unverifiable.
- `L:SUM/README.md:L282-289` ("Dmitry's progress figure for Dan's checkpoints"): textbook72 pass@256, plain, 3 seeds,
  solved if any sample is accepted by Lean (`L:SUM/figures/fig_lengthbin_baseline.caption.md:L1`), by reference length
  1–5 / 6–10 / 11–15 / 16+ / train14: pretraining only 100 / 58 / 29 / 0 / 38%; after RL (round 8) 100 / 92 / 69 / 28 / 67%.
  Derived totals (bins n = 5 / 24 / 16 / 13 / 14, from the caption): pretraining-only ≈ (5 + 13.9 + 4.6 + 0 + 5.3)/72 ≈
  40%; after RL ≈ (5 + 22.1 + 11.0 + 3.6 + 9.4)/72 ≈ 71% (rounding-limited; consistent with 52/51/52).
- Dan's architecture/recipe is Leon's base (`L:D/PROPOSAL.md:L23`; `L:SUM/README.md:L133`); Dan's `train_k12` and
  `heldout` files are used for training/holdout (`L:D/RECIPE.md:L66`).
- No Dan number appears in `STAGE1_STATS.md`, `stage1_stats/*`, `THINKING_UPLIFT.md`, `ADAPTIVITY.md`,
  `compare_3ckpt.md` or any `matched_eval/*.md` (grep for Dan / best-state / best12 / state_env_october / trajectory /
  guided-tts / r8: no hits outside OOD_CHECK).

### 5.3 Is any comparison with Dan's models made, and is it protocol-matched?

- **OOD_CHECK**: no head-to-head; it surveys Dan's numbers to pick testbeds.
- **SUM/README.md:L179-180**: the only explicit Leon-vs-Dan comparison. Roughly matched on sampled tokens (~21k vs
  ~24k per theorem), both Stage-1 (pre-RL), guided redraws in both, but Leon's arm adds thinking and is read at k 16
  vs Dan's k 64, one seed each, and Dan's side has no recorded source. Not protocol-matched in k; set identity is
  implied (Tier A 80 and `ood_commute`) but not stated.
- **Implicit**: Leon's Stage-1 textbook72 pass@256 by length bin (`L:SUM/README.md:L160-166`) uses the same protocol as
  Dmitry's figure of Dan's checkpoints (pass@256, plain, 3 seeds, Lean), and the README says "The trace arms will be
  added to the same figure" (`L:SUM/README.md:L291`). Leon never states the comparison. Derived: Leon's T0 Stage-1
  45.4% vs Dan's pretraining-only ≈ 40% (from bins); Leon's best Stage-1 56.0% (T1v1 B256) vs Dan's r8 70.8–72.2%.
- **Not comparable without care**: Leon's post-RL textbook72 numbers (EI/GRPO on hard712) vs Dan's r8 — hard712 was
  designed from a gap analysis of dev58 (`L:D/THINKING_UPLIFT.md:L200-202`), Leon reads k 64 (pass@256 only in one
  512-attempt read, 84.5%), and Dan's textbook72 pass@1 is not in Leon's files (only textbook_dev pass@1 40.8% from
  ndbench, a different set and estimator). Leon's Charles sets (Tier A 80; Charles149) ≠ Dan's "long 90".

---

## 6. Eval-set definitions

| set | definition | source |
|---|---|---|
| textbook72 | 72 = textbook_dev 58 + textbook_train 14. dev58 has reference proofs (not all minimal); train14 has none (shortest found 2–20 lines) | `L:D/STAGE1_STATS.md:L89`; `L:D/THINKING_UPLIFT.md:L41`; `L:D/matched_eval/length_split_ynez.md:L13, L21, L27` |
| textbook_dev / dev58 | the project's dev set; a design set for hard712 and therefore for r2/r3 models | `L:D/THINKING_UPLIFT.md:L200-202`; `L:D/OVERNIGHT_20261008.md:L49-50` |
| Charles long (Dan's) | 90 theorems of Charles's release with >10 lines (guided-tts group "long 90") | `L:D/OOD_CHECK.md:L18, L40`; `FORK@4dcd0e4f:artifacts/gt/analysis_stdout.txt:L43` |
| Tier A / `charles_long_reach` | 80 of the 90, excluding ≥4 premises, formula depth 7, name exhaustion, states > 400 tokens; bins 11–20 (62), 21–30 (13), 31–51 (5); 27 classical. Selected with the SOTA model's failure analysis | `L:D/OOD_CHECK.md:L52-59`; `L:D/LIT_CRITIQUE.md:L324` |
| Charles149 | Charles's release of 2026-10-02 (173 problems) reduced to the 149 that share no renaming class with any training pool (`charles_eval/build_clean.py`); read at k 64 | `L:D/matched_eval/confusion_tb72.py:L9-11`; `L:D/RECIPE.md:L237` |
| OOD 840 | charles_long_reach (80) + `ood_or_reorder`, `ood_and_reorder`, `ood_commute` (n = 3–8, 40 per n, 720) + `ood_case_product` (40); 99 clusters | `L:D/stage1_stats/ood_clustered.md:L7`; `L:D/STAGE1_STATS.md:L160-162`; `L:D/OOD_CHECK.md:L60-68` |
| hard12 / hard12_test_1k | Dan's generator, 7–12-line references, K12 rules; band = T0_s0 solves 2–16 of 32; RL pool `rl_hard12` 5,000; sealed test 2,500, of which `hard12_test_1k` = 1,000 | `L:D/pools/hard12/README.md:L6-20`; `L:D/stage1_stats/hard12_seed_control.md:L1` |
| hard712 | proof-first generator, 23,092 problems (pool 21,592, test_1k, dev_500); every problem has a shortest proof of 7–12 lines, 90% need 9–12 | `L:D/hard712/README.md:L10-18` |
| 13–20 (test_13_20) | sealed generated composites, 13–20 lines; 986 valid of `t1320_n1000` (14 fail `valid_1320`) | `L:D/test_13_20/README.md:L6-18`; `L:D/THINKING_UPLIFT.md:L39-40, L203-204` |
| 21–30 | sealed, 1,000 fixed sample (RL slice) | `L:D/RECIPE.md:L235` |
| adapt_set (672) | 600 from `rl_hard_filtered` (75 per T0-pass × length cell) + textbook72 | `L:D/ADAPTIVITY.md:L199-207` |
| Dan's in-distribution sets (quoted) | holdout250, long pool L_true 13–16 (380), lengths ≥ 17 (21), rl_targets (4,495) | `L:D/OOD_CHECK.md:L15-16`; `DAN:…state_env_october.md:L36-38` |

Feature contrast (`L:D/matched_eval/source_split_ynez.md:L17-60`): 3+ premises textbook72 6%, Charles149 19%, 13–20
79%, RL pools 0%; 4 atoms 11 / 27 / 74 / 0%; case split 28 / 34 / 96 / 69%. Proof skeleton present in the RL pools:
textbook72 45%, Charles149 31%, 13–20 7% (L68).

---

## 7. Reviewed status; ambiguities; numbers that look wrong or unverifiable

### 7.1 Review status

- **No independent (external) review** of these results was found on `L:`. All notes are `written_by: agent:claude`
  inside Leon's folder (self-reported).
- In-folder critiques: `L:D/LIT_CRITIQUE.md` (2026-10-06, "deliberately hostile reading", scope includes the Stage-1
  summary; `L:D/LIT_CRITIQUE.md:L12-17`) — `STAGE1_STATS.md` is the response to its C1/C3/C4. `L:D/TRACE_AUDIT.md`
  audits the v1 traces; `L:D/search_traces/README.md` audits the search traces; `L:D/PLAN_CRITIQUE.md` (2026-10-08)
  critiques the plan. None reviews `THINKING_UPLIFT.md` or the `matched_eval/` tables.

### 7.2 Ambiguities and possible errors

1. **Dan's Stage-1 guided numbers (20.0% / 23.8%)** at `L:SUM/README.md:L180`: no source in git; the eval that would
   produce them was "not run" per `L:D/OOD_CHECK.md:L77` / `L:D/ood_check/EVAL_SPEC.md:L1`. Treat as unverifiable.
2. **textbook_train14 in Stage-1 data?** `L:D/ADAPTIVITY.md:L212-213` says "textbook72 train is in Stage-1's mixture",
   but `L:D/pipeline/arms.yaml:L6` and `L:D/pipeline/README.md:L195-198` exclude it (`--extra-exclude $TB_TRAIN`), as do
   the S1g3/T0S builds (`L:D/search_traces/README.md:L411-422`). Contradiction; actual data not checkable from git.
3. **Mixed seed sets in the OVERNIGHT Stage-1 table** (`L:D/OVERNIGHT_20261008.md:L166-174`): header says "2 seeds
   each", but "old T0" textbook72 17.2 is the 3-seed mean (`L:D/stage1_stats/tb72.md:L11`) and hard12 42.4 is T0 s1-2
   (`L:D/stage1_stats/hard12_seed_control.md:L11`). k is not stated for any column. The S1g3/T0S rows have no
   `stage1_stats`-style generated table.
4. **S1g3 seed spread is large**: ynez textbook72 pass@1 43.8 / 39.6 / 32.3 (s0/s1/s2) vs serrano 40.7 / 43.0
   (`L:D/EXPERIMENT_QUEUE.md:L140-142`): an 11.5-pp range (derived 43.8 − 32.3), larger than the S1g3 − T0S effect's
   lower CI bound (+3.7). The +10.3 pp thinking effect rests on serrano's 2 seeds.
5. **README Stage-1 claims softened by STAGE1_STATS**: "2.2–4.5 pp ahead at 29k" and "trace training costs the no-think
   policy 6–9 pp" (`L:SUM/README.md:L185-188`) are "within noise" / confounded with the empty-think format
   (`L:D/STAGE1_STATS.md:L291-297`). The README matched-token values (e.g. T1v1 1k 23.5%) differ slightly from
   STAGE1_STATS (23.8%) because of the interpolation grid (`L:D/STAGE1_STATS.md:L73-74`).
6. **OVERNIGHT overstates textbook72 seed 0**: "thinking ahead at ≥ 4k tokens in both seeds"
   (`L:D/OVERNIGHT_20261008.md:L304`), but r2 s0 at 4k is +3.0 [−0.9, +7.4] (`L:D/THINKING_UPLIFT.md:L75`); resolved only
   from 8k.
7. **textbook72 is not a clean test for r2/r3 (and the GRPO v2 models)**: hard712 was built from a dev58 gap analysis
   (`L:D/THINKING_UPLIFT.md:L200-202`); B64 chosen on the same sets (L183-187); one training seed per arm, problem-only
   intervals (L54-55, L181-182).
8. **The 512-attempt textbook72 numbers** (84.5% at k256, 84.7% at k512) exist only in `L:SUM/figures/fig_ceiling_tb72.json`
   and the figure labels "85%" / "79%"; no markdown table. Single seed (r2 s0 pair).
9. **Charles Tier A selection bias**: filtered "within reach" using the SOTA model's failure analysis
   (`L:D/LIT_CRITIQUE.md:L324`); 55 of 80 theorems are 0% in all Stage-1 cells (`L:D/STAGE1_STATS.md:L235`).
10. **hard12 filter-model bias**: T0 s0 was the selection model; its hard12 pass@1 is 14.7 pp below T0 s1-2
    (`L:D/stage1_stats/hard12_seed_control.md:L20`). Any hard12 comparison using T0 s0 is biased against it.
11. **ndbench "k2048" (textbook_dev 79.3 / 51.7%)** uses adaptive sampling (more draws for unsolved theorems)
    (`L:code/ndbench/dash/dan_only.py:L445-446`); not an item-uniform pass@2048.
12. **OOD_CHECK "trajectory r8" label**: the Charles-long numbers are guided-tts reads of the `trajectory` seeds, not
    `best-state` (`DAN:…state_env_october.md:L39`); the textbook72 k256 row is `best-state`. Both are
    `state_env_october` r8 but different seed sets.
13. **`length_split_ynez.md` §2 "GRPO"** is the plain `grpo_think` arm (`L:D/matched_eval/length_split.py:L124`), not
    RECIPE.md's KL-0 merged recipe; their textbook72 pass@5 differ (82.1% vs 82.3%; `…length_split_ynez.md:L143`,
    `L:D/RECIPE.md:L38`).
14. **`THINKING_UPLIFT.md` vs `tts_uplift_tables.md`**: the tables file (last commit 2026-10-09 18:28) lacks the seed-2
    pair and r3 s0 textbook72; seed-2 numbers are only in the note's update (`L:D/THINKING_UPLIFT.md:L298-311`). The r2
    seed-2 13–20 read crashed (OOM) and was being rerun (L306-307); no result in my files.
15. **EI compute** (rounds × k × fine-tune steps) for the THINKING_UPLIFT pairs is not stated in my slice files (RL slice).
