# Our side: headline numbers, protocols and sources (peer-rl-review)

Compiled 2026-10-17 by a read-only research agent. Every number is quoted as written in its source unless marked
**derived** (arithmetic shown). "Reviewed" = the nd-rl `experiment-summaries/<run>/README.md` on `origin/dan` says
"completed and reviewed" / "independently reviewed" with a review link (all summaries cited here do). Fork `numbers.md`
sections carry the heading "executor; UNREVIEWED" even where the run was later reviewed; where a per-seed value exists
only there, it is marked `exec-table` and its reviewed aggregate is named.

## 0. Source legend (paths for every citation)

nd-rl (read with `git -C ~/nd-rl show origin/dan:<path>`):

| tag | path |
|---|---|
| SEO | `origin/dan:docs/models/state_env_october.md` |
| R16 | `origin/dan:docs/models/state_env_october_r16.md` |
| BS | `origin/dan:experiment-summaries/2026-09-30-best-state-robbies-recipe-wins-after-rl-level-frozen-at-cap12/README.md` |
| TB | `origin/dan:experiment-summaries/2026-09-30-textbook72-sn-cap12-t1-solves-37-of-72/README.md` |
| SX | `origin/dan:experiment-summaries/2026-09-30-search-expert-best-first-ties-sampling-at-quarter-spend/README.md` |
| FS | `origin/dan:experiment-summaries/2026-09-30-frontier-supply-filter-works-gain-inside-mdd/README.md` |
| SC12 | `origin/dan:experiment-summaries/2026-09-29-state-cap12-state-and-cap12-proofs-compound-on-long-pool/README.md` |
| SE | `origin/dan:experiment-summaries/2026-09-28-state-env-state-lifts-below-the-wall/README.md` |
| TJ | `origin/dan:experiment-summaries/2026-10-01-trajectory-eventual-proof-worst-step-climbs-in-pretraining-and-rl/README.md` |
| TJ6 | `origin/dan:experiment-summaries/2026-10-02-trajectory-cap6-eventual-proof-worst-step-climbs-mainly-in-rl/README.md` |
| CM | `origin/dan:experiment-summaries/2026-10-02-compute-match-matched-ladder-gpu-time-does-not-close-gap/README.md` |
| GB | `origin/dan:experiment-summaries/2026-10-02-grpo-best-grpo-default-trades-theorems-with-ei-pass4-level-overall/README.md` |
| MC | `origin/dan:experiment-summaries/2026-10-02-mcts-a-puct-value-search-gate-fails-on-group-c/README.md` |
| RFC | `origin/dan:experiment-summaries/2026-10-02-rl-from-ckpt-early-start-ladders-reach-end-arm-from-step-5000/README.md` |
| EA | `origin/dan:experiment-summaries/2026-10-02-evidence-atlas-map-of-95-experiments-whole-proof-rescore/README.md` |
| CA | `origin/dan:experiment-summaries/2026-10-02-claim-audit-headline-counts-reproduce-three-claims-weaker-than-stated/README.md` |
| GT | `origin/dan:experiment-summaries/2026-10-03-guided-tts-logical-redraws-beat-plain-on-long-theorems-structural-redraws-do-not/README.md` |
| RC | `origin/dan:experiment-summaries/2026-10-03-rl-continue-cap12-group-c-rises-on-3-of-3-seeds-saturation-falsified-target-burst-is-one-seeds-excluded-middle/README.md` |
| RC6 | `origin/dan:experiment-summaries/2026-10-03-rl-continue-cap6-group-c-rises-on-3-of-3-seeds-saturation-falsified-cap-6-still-below-cap-12/README.md` |
| CD | `origin/dan:experiment-summaries/2026-10-05-capability-defs-compute-matched-budget-shrinks-equal-k-creations-rl-still-ahead-lem-teachable/README.md` |
| COE | `origin/dan:experiment-summaries/2026-10-12-create-or-elicit-sigma-knockout-not-acquired-in-16-ei-rounds-needs-exposure-1pct-dose-restores/README.md` |

Fork (`dan-pandori/nd-takehome`; worktree `/home/dan/work/peer-rl-review`, branch `dan_peer-rl-review` = fork `dan` at
`b8e736e4`):

| tag | path |
|---|---|
| NM | `fork:numbers.md` (worktree HEAD) |
| NM-GB | `fork:numbers.md` at `origin/dan_grpo-best` (`git show origin/dan_grpo-best:numbers.md`) |
| NM-CD | `fork:numbers.md` at `origin/dan_capability-defs` |
| NM-COE | `fork:numbers.md` at `origin/dan_create-or-elicit` |
| GTA | `fork:artifacts/gt/analysis_stdout.txt` (in HEAD's tree, excluded by the sparse checkout; `git show HEAD:artifacts/gt/analysis_stdout.txt`) |
| NF | `fork:NOISE_FLOOR.md` |
| PRE-GT | `fork:preregistration/guided-tts.md` |
| READ-BS | `fork:pod/bs/read.sh`; READ-GT = `fork:pod/gt/queue.sh` + `fork:pod/gt/env.sh` |

## 1. Files read

- nd-rl: SEO (all 69 lines), R16 (all 64), BS (all 197), TB (all 217), TJ (all 280), TJ6 (all 313), RC (all 226),
  RC6 (all 206), GT (all 190), GB (all 247), MC (all 188), CM (all 184), SX (all 184), CD (L1–260), COE (L1–130,
  L196–230, L370–390, L608–616), EA (all 132; `data/headline_table.csv` header + dev rows), CA (all 102), RFC (L1–12,
  L60–90, L130–160), FS (L6–60), SC12 (L30–50), SE (grep for judge), `docs/proposals/claude-heavy/BRIEF_peer-rl-review.md`
  (all 94), greps for `hard712|charles149|rl_hard12|hard12` (only hit: the brief) and for `904`.
- Fork: NF (all 106); NM § best-state L1478–1578, compute L1648–1681, § guided-tts L1705–1798; NM-GB § grpo-best
  L1705–1760; NM-CD L1870–1896; NM-COE L1860–1902 (grep-located); GTA (grep for long / tb72 / release / all / MDD rows);
  PRE-GT L26–40; `run_guided_tts.md` (grep); READ-BS; READ-GT; `guided_eval.py` L38–50; `state_eval.py` L21–60;
  data files `data/bs/{textbook72,dev1108,holdout250}.jsonl`, `data/ladder/transfer.jsonl`, `data/gt/*.jsonl`
  (tiny local counts only, see §9).

## 2. Our model lineage (all from scratch; all under `hf://buckets/dan-pandori/nd-rl/`)

| model (internal names) | params / arch | interface | Stage-1 data, cap | RL | judge | checkpoints |
|---|---|---|---|---|---|---|
| **SN-v2 cap 6** ("ours-cap6") | 3,216,384; GPT 4 × 256, RoPE, AdamW, 6,000 steps × 128 proofs [BS:L52] | proof state `lean_staten`, env-assigned names (SN-v2) | cap-6 control set `data/p2/train_depth3_f0_a1.jsonl` (155,000) | T1 ladder r8 | Lean alone [SE:L42] | `state-env/ckpts/se/stage1_SN_s{0,1}.pt`, `state-env/ckpts/se/ladder/la_T1_SN_s{0,1}_r8.pt` [TB:L49–50] |
| **SN-cap12** ("ours-cap12") | 3,216,384, same arch [SC12:L36] | `lean_staten` | K12 `data/kh/train_k12.jsonl` (155,000, flat lengths 2–12) | T1 r8 (8 × k 32, T 0.8) [SC12:L37] | Lean alone [SC12:L32] | `state-cap12/ckpts/sc12/stage1_SN12_s{0..3}.pt`, `state-cap12/ckpts/sc12/ladder/la_T1_SN12_s{0..3}_r8.pt` [TB:L47–48] |
| **cm12** | 3,216,384 | `lean_staten` | K12 (SN12 Stage-1 reused) | T1 at **k 64** (compute-matched to best12's ladder A40-s) [CM:L49–51] | Lean alone | `compute-match/ckpts/cm/` … `la_T1_cm12k64_s{0,1,2}_r8.pt` (subdir not verified) [CM:L39, L49] |
| **whole-proof C0 cap 6 / K12 cap 12** | 3,214,336; GPT 4 × 256 | whole proof `lean_seq` | cap-6 set / K12 | T1 r8 | C0 ladder trained under Lean ∧ `nd_verify` (2026-09-24), K12 ladder Lean alone; both re-read Lean alone [SC12:L38, L41] | `lean-format/ckpts/lf/stage1_a1_seq_s{0,1}.pt`, `ds-generator/ckpts/ladder/la_T1_c0_s{0,1}_r8.pt`, `cap-horizon/ckpts/kh/stage1_k12_s{0,1}.pt`, `state-cap12/ckpts/ladder/la_T1_K12_s{0,1}_r8.pt` [EA:L37–40] |
| **best-cap6** | 9,560,832; Robbie's `ALiBiGPT` 6 × 384, Peri-LN, 4 ALiBi + 4 NoPE heads, Muon + AdamW, MTP 0.3 (+1.88 M MTP head not saved), 1,200 s on one A40 [BS:L50] | `lean_staten` | cap-6 control set | T1 r8; r9–r16 (`rl-continue-cap6`) | Lean alone | best-state seeds: `best-state/ckpts/bs/stage1_best6_s{0,1,2}_b1200.pt`, `best-state/ckpts/bs/ladder/la_T1_best6_s{0,1,2}_r8.pt` [BS:L50]; trajectory-cap6 seeds: `trajectory-cap6/ckpts/tj6/ladder/la_T1_best6_s{S}_r{1..8}.pt` (fork `pod/tj6` on `origin/dan_trajectory-cap6`); r9–r16: `rl-continue-cap6/ckpts/rc6/ladder/la_T1_best6_s{0,1,2}_r{9..16}.pt` [RC6:L36, L66] |
| **`state_env_october`** = best-cap12 r8 ("best12") | 9,560,832, as above [SEO:L16–17] | `lean_staten` [SEO:L18] | K12 [SEO:L19] | T1 r8: 8 rounds, k 32, T 0.8, 4,495 `rl_targets`, K12 replay, 600 fine-tune steps / round [SEO:L20] | Lean 4 core alone [SEO:L21] | best-state seeds `best-state/ckpts/bs/ladder/la_T1_best12_s{0,1,2}_r8.pt`; trajectory seeds `trajectory/ckpts/tj/ladder/la_T1_best12_s{0,1,2}_r8.pt` (+ all pretraining ckpts `trajectory/ckpts/tj/stage1_best12_s*_b1200_step*.pt`); pretraining only `best-state/ckpts/bs/stage1_best12_s{0,1,2}_b1200.pt` [SEO:L26–29]; trajectory pend `trajectory/ckpts/tj/stage1_best12_s<S>_b1200.pt` (md5 2bf801fd / eaff7f4d / abca9c63) [GB:L36] |
| **`state_env_october_r16`** | same | same | same | r9–r16, same T1 settings, from trajectory's r8 [R16:L16–17] | Lean alone [R16:L18] | `rl-continue/ckpts/rc/ladder/la_T1_best12_s{0,1,2}_r16.pt`; r12 `…_r12.pt` [R16:L25–27] |
| best-cap12 "full, new" s3–s5 (`create-or-elicit`) | same recipe [COE:L62–64] | same | K12 | T1 r1–r16, A40, batch 1,024 [COE:L71] | Lean alone | `create-or-elicit/ckpts/coe/stage1_full_s{3,4,5}.pt`, `create-or-elicit/ckpts/coe/ladder/la_full_s{3,4,5}_r{R}.pt` [COE:L159–160] |
| GRPO arms from trajectory pend | 9,560,832 | `lean_staten` | K12 | GRPO (§4) | Lean alone [GB:L49] | `grpo-best/ckpts/gb/gb_<arm>_s<S>_r<k>.pt`, arms `default`, `unlikely`, `passk`, `distinct` [GB:L44; NM-GB:L1713] |

T1 ladder details (best-cap12): `state_ladder_ei.py`, 8 rounds × k 32 on `rl_targets` (4,495), fine-tune 600 steps × 128
proofs, AdamW lr 3e-4 → 3e-5, replay 20,000 K12 records per round [GB:L39–41]; in-loop `max_steps` 48, `max_action` 256
[BS:L60–62]; samples 2,285 `transfer` theorems each round, never trained [RC:L37–38]; T1 keeps up to 4 random successes
per target, no step filter [SX:L57–58].

## 3. Headline table

Common read protocol unless stated: state env, plain sampling, **T 0.8**, `max_steps` 96, `max_action` 512, solved =
≥ 1 Lean-accepted attempt of k; **Lean alone**; from scratch. "x0/x1/x2" = sample seed 0/1/2. IQM is rliable IQM
(= mean at n = 3, middle-two mean at n = 4) [BS:L39–40]; "mean" lines without a source are **derived**.

### 3a. textbook72 (72 = dev58 + train14; scoring only; `data/bs/textbook72.jsonl`), pass@256

| model / read | value (per seed) | protocol notes | source | reviewed? |
|---|---|---|---|---|
| best-cap12 r8, best-state seeds, plain x0 | **52 / 51 / 52**, IQM 51.6667 [51, 52]; dev58 42 / 44 / 42 (IQM 42.6667); train14 10 / 7 / 10 (IQM 9) | batch 2,048 | NM:L1515, L1524, L1533; BS:L94; SEO:L34 | yes (BS) |
| best-cap12 r8, trajectory seeds, plain | x0 **48 / 49 / 54**; x1 **48 / 48 / 53**; x2 49 / 50 / 55 | x0/x1 `state_eval`, batch 2,048 (A6000/A40); x1 also = guided-tts plain arm (seed 1); x2 = mcts-a sample arm | TJ:L108; RC:L147–149; R16:L33; GT:L103; MC:L81 | yes |
| … dev58 / train14 (x1) | 40 / 38 / 42; 8 / 10 / 11 | J3 table | NM-CD:L1876, L1879, L1882 | exec-table (CD reviewed; 322 totals at CD:L236 reproduce) |
| best-cap12 r8, trajectory seeds, **guided-logical** | **54 / 52 / 57** (guided-tts); J3 re-read 54 / 52 / 56 (dev58 43 / 41 / 45, train14 11 / 11 / 11) | `guided_eval.py --arm logical`, k 256, seed 1, ≤ 10 redraws, batch 2,048; not compute-matched | SEO:L43; NM:L1730–1732; NM-CD:L1876/1879/1882 | yes (GT) / exec-table |
| best-cap12 **r16** (trajectory seeds), plain x1 | **51 / 57 / 56** (mean 54.67 derived: 164/3) | rl-continue, batch 2,048 | R16:L33; RC:L147–149 | yes (RC) |
| … dev58 / train14 | 42 / 45 / 44; 9 / 12 / 12 | | NM-CD:L1877/1880/1883 | exec-table |
| best-cap12 **r16, guided-logical** (J3) | **55 / 56 / 62** (derived: dev58 + train14 = 45+10, 45+11, 50+12; mean 57.67); dev58 45 / 45 / 50 | k 256, seed 1, `max_rej` 10, batch 2,048 | NM-CD:L1877/1880/1883; 322-totals 295 / 303 / 303 at CD:L236 | exec-table (totals reviewed) |
| best-cap12 r16, new seeds s3–s5 (COE "full, new"), plain x0 | 55 / 54 / 51; dev58 44 / 44 / 42; train14 11 / 10 / 9 | read batch 512 [COE:L101]; ladders A40 batch 1,024 | NM-COE:L1868–1870 | exec-table (COE reviewed; only differences are in COE:L378–383) |
| best-cap12 frozen (pend), best-state seeds | 32 / 27 / 27, IQM 28.6667 | x0 | NM:L1515; BS:L94 | yes |
| best-cap12 pend, trajectory seeds | x0 32 / 32 / 38; x1 34 / 33 / 36; guided (J3) 42 / 43 / 48 (derived 36+6, 33+10, 38+10) | | TJ:L108; R16:L33; NM-CD:L1875/1878/1881 | yes / exec-table |
| best-cap12 pend + replay-only 8 rounds (no RL proofs) | 38 / 31 / 35 (x1) | RL-free control | RFC:L138 | yes |
| best-cap12 r8 GRPO arms (x0) | default 43 / 46 / 49; unlikely 41 / 45 / 49; pass@4 52 / 52 / 48 (EI 48 / 49 / 54) | MDD 9.8 | NM-GB:L1730 | exec-table (GB reviewed; not in GB summary) |
| best-cap6 r8, best-state seeds | 39 / 40 / 33, IQM 37.3333; frozen 19 / 18 / 20 | x0 | NM:L1513; BS:L94 | yes |
| best-cap6 r8, trajectory-cap6 seeds | x0 43 / 41 / 38; x1 43 / 43 / 39; guided 48 / 47 / 45 | | TJ6:L118; RC6:L106; GT:L103–104; NM:L1733–1735 | yes |
| best-cap6 r16 | plain x1 45 / 41 / 40; guided (J3) 51 / 46 / 48 (derived 40+11, 38+8, 38+10) | | RC6:L106; NM-CD:L1886/1889/1892 | yes / exec-table |
| best-cap6 pend (trajectory-cap6) | x0 17 / 14 / 15; x1 18 / 18 / 15 (derived 14+4, 15+3, 11+4); guided 29 / 23 / 27 (derived 24+5, 19+4, 21+6) | | TJ6:L118; NM-CD:L1884/1887/1890 | yes / exec-table |
| 3.2M SN-cap12 T1 r8 | **37 / 38 / 36 / 38**, IQM 37.5 [36, 38]; dev58 30 / 32 / 30 / 32; train14 7 / 6 / 6 / 6; union 46 | batch 4,096, seed 0 | TB:L83–86, L100 | yes |
| … re-read (s0–s2) | 36 / 40 / 36 | batch 2,048 | CM:L83 | yes |
| 3.2M SN-cap12 frozen | 26 / 29 / 32 / 26, IQM 27.5 [26, 32] | | TB:L87–90, L101 | yes |
| 3.2M cm12 (k 64 ladder) | 36 / 36 / 36 | | CM:L83 | yes |
| 3.2M SN-v2 cap 6 | T1 22 / 16; frozen 16 / 14 | | TB:L91–94 | yes |
| 3.2M whole proof `lean_seq` (s0, s1) | K12 cap-12 T1 25, 22; frozen 21, 21; C0 cap-6 T1 15, 13; frozen 12, 11 | `eval_set.py`, k 256, T 0.8, seed 0, batch 2,048, `max_new` 512 | EA:L41–43, L66–69 | yes (EA) |
| highest single textbook72 count on file by 2026-10-02 | 57 (`trajectory` `la_T1_best12_s2_r6`) | | EA:L96–99 | yes |

Union facts: all 12 3.2M checkpoints together solve 47 / 72; 25 solved by none (19 dev58 + 6 train14) [TB:L116–118].
Secondary judge: 0 of 6,128 distinct Lean-accepted proofs rejected by `nd_verify`, so Lean ∧ `nd_verify` counts are
unchanged for the 3.2M state models [TB:L119–120].

### 3b. Robbie's dev metric (dev1108: the 1,108 records of `data/ladder/transfer.jsonl` with `sha1(key)` even, all `L_true` ≥ 7; k 64; solved count) [NM:L1497–1498; BS:L69–70]

Read: `state_eval.py --k 64 --temperature 0.8 --seed 0 --batch 2048 --max_action 512 --max_steps 96 --lenfield n_lines`
[READ-BS:L14–15].

| model | value | source | reviewed? |
|---|---|---|---|
| best-cap12 r8, best-state seeds | **1,058 / 1,050 / 1,055**, IQM 1054.33 [1050, 1058] | NM:L1542; BS:L95; SEO:L35 | yes |
| best-cap12 r8 (EI), trajectory seeds | 1,055 / 1,043 / 1,060 (mean 1,053) | NM-GB:L1734; mean at GB:L123–124 | per-seed exec-table; mean reviewed |
| GRPO-pass@4 r8 | **1,064 / 1,070 / 1,039** (mean 1,058) | NM-GB:L1734; GB:L125 | as above |
| GRPO-default / -unlikely r8 | 1,022 / 1,024 / 1,031 (1,026); 1,024 / 1,023 / 1,034 (1,027) | NM-GB:L1734; GB:L123–124 | as above |
| best-cap12 frozen (best-state seeds) | 782 / 767 / 741, IQM 763.333 | NM:L1542 | yes |
| best-cap6 T1 / frozen | 1,002 / 986 / 1,002 (IQM 996.667) / 569 / 466 / 506 (IQM 513.667) | NM:L1540 | yes |
| 3.2M SN-cap12 T1 / frozen | 927 / 972 / 961 / 940 (IQM 950.5) / 745 / 782 / 804 / 781 (IQM 781.5) | NM:L1541 | yes |
| 3.2M cm12 | 934 / 995 / 972 → 967.00 | CM:L84 | yes |
| 3.2M SN-v2 cap 6 T1 / frozen | 746 / 663 / 405 / 329 | NM:L1539 | yes |
| 3.2M whole proof K12 T1 / C0 T1 | 797, 771 / 417, 465 | EA:L66–69 | yes |

No r12 / r16 checkpoint was read on dev1108 (0 mentions in the rl-continue, rl-continue-cap6, capability-defs and
create-or-elicit numbers.md sections).

### 3c. holdout250 (Robbie's `passk.py` pool, `data/bs/holdout250.jsonl`; `L_true` 7–14), pass@256

| model | value | source | reviewed? |
|---|---|---|---|
| best-cap12 r8, best-state seeds (x0) | 239 / 237 / 237, IQM 237.667 | NM:L1551; SEO:L36 | yes |
| best-cap12 r8, trajectory seeds | x0 238 / 237 / 239; x1 240 / 236 / 237 | TJ:L109; R16:L34 | yes |
| best-cap12 **r16** x1 | **240 / 246 / 239**; guided (J3) 240 / 247 / 241 | R16:L34; NM-CD:L1877/1880/1883 | yes / exec-table |
| best-cap12 pend | best-state 184 / 195 / 182 (IQM 187); trajectory x0 200 / 204 / 196, x1 196 / 205 / 200; guided 218 / 223 / 222 | NM:L1551; TJ:L109; R16:L34; NM-CD:L1875/1878/1881 | yes / exec-table |
| replay-only control | 206 / 210 / 213 | RFC:L138 | yes |
| best-cap6 r8 (best-state) / r16 (x1) / r16 guided | 226 / 229 / 227 / 232 / 233 / 232 / 233 / 235 / 236 | NM:L1549; NM-CD:L1886/1889/1892 | yes / exec-table |
| 3.2M SN-cap12 T1 | 217 / 221 / 223 / 219, IQM 220 | NM:L1550 | yes |
| 3.2M whole proof K12 T1 / C0 T1 | 181, 177 / 104, 102 | EA:L66–69 | yes |

### 3d. Charles's textbook release `release_2026-10-02` (r8 only; no r16 read on it)

Source set: nd-rl `origin/charles/main:data/textbook_problem/release_2026-10-02/`: `candidate_v0` 87, `candidate_v1` 72,
`batch3` 14, `hand_proved_14` 14 = 187; **long** = rows with `min_lines` > 10 = **90**; `derived` skipped; 2
`hand_proved_14` rows have `min_lines` > 96 and cannot be solved at `max_steps` 96 [PRE-GT:L30–35]. Local check: long =
37 + 32 + 7 + 14 = 90 (§9). Protocol: `guided_eval.py`, k 256, T 0.8, seed 1, batch 2,048, A40 [GT:L51–53]; models =
trajectory's best-cap12 r8 s0–s2 and trajectory-cap6's best-cap6 r8 s0–s2 [GT:L33–39].

Per file, solved@256 attempts (not compute-matched), cap 12 r8, plain vs guided-logical [SEO:L44–47; NM:L1730–1732]:

| set | plain s0 / s1 / s2 | guided-logical |
|---|---|---|
| candidate_v0 (87) | 67 / 65 / 71 | 75 / 71 / 75 |
| candidate_v1 (72) | 52 / 51 / 55 | 59 / 57 / 56 |
| batch3 (14) | 11 / 8 / 9 | 12 / 10 / 11 |
| hand_proved_14 (14) | 0 | 0 |
| release total (187), derived (sum of files) | 130 / 124 / 135 | 146 / 138 / 142 |

Cap 6 r8 per file plain / logical: s0 58/44/7/0 vs 65/49/9/0; s1 54/42/9/0 vs 66/51/9/0; s2 52/35/8/0 vs 62/47/9/0
[NM:L1733–1735].

**long (90)**, solved@256 attempts (attempt-matched k = 256 rows; counts derived as % × 90, exact):

| model | plain | guided-logical | source |
|---|---|---|---|
| cap 12 r8 | 42.2 / 34.4 / 46.7 % = **38 / 31 / 42** | 55.6 / 50.0 / 52.2 % = **50 / 45 / 47** | GTA:L268 |
| cap 6 r8 | 26.7 / 27.8 / 21.1 % = 24 / 25 / 19 | 35.6 / 38.9 / 34.4 % = 32 / 35 / 31 | GTA:L318 |

Matched sampled tokens (the pre-registered headline; k = plain-equivalent attempts): see §5.

### 3e. Long pools, group C, held-out greedy, training targets

| quantity | value | protocol | source | reviewed? |
|---|---|---|---|---|
| rr600 **Q** (generator theorems with `L_true` 13–16 in `transfer_long_rr600.jsonl`, /380) | best-cap12 T1 **377 / 375 / 376** (IQM 376); frozen 271 / 237 / 216; best-cap6 T1 350 / 346 / 339; SN-cap12 T1 233 / 295 / 320 / 317 (IQM 306) | `lpool_reread.py` k 256, x0 (inherited SN-cap12 Q at `max_steps` 48) | NM:L1558–1560; BS:L71–72, L97; SEO:L37 | yes |
| rr600 rows with `L_true_lb` 13–16 (/400) | r8 377 / 362 / 367 → r16 382 / 370 / 376 | **k 64**, x0, batch 512 | RC:L47–48, L147–149; R16:L36 | yes |
| `transfer_long2` (/21, lengths ≥ 17) | best-cap12 T1 21 / 21 / 20 (best-state); trajectory seeds r8 21 / 20 / 20 → r16 21 / 21 / 20; SN-cap12 T1 8 / 15 / 17 / 14 | k 256 | NM:L1568–1569; R16:L37 | yes |
| search-expert Q (91 of long-pool-2 + rr600 `L_true` 15–16 = 291) | SN-cap12 T1 142 / 207 / 218 / 220 | k 256, seed 0 | SX:L59–63, L95 | yes |
| **group C** (per seed, trajectory: tb72 + h250 theorems unsolved by pend and r8 on x0; 36 / 35 / 28) | solved x1: r8 3 / 1 / 1 → r12 5 / 8 / 5 → **r16 6 / 17 / 4**; pass@256 (fraction of C solved) r8 0.083 / 0.029 / 0.036 → r16 **0.167 / 0.486 / 0.143** | k 256, x1 | RC:L49–50, L107–109; R16:L38, L43–44 | yes |
| group C, GRPO-pass@4 r8 | 6 / 19 / 3 (EI 3 / 1 / 1) | x1 | GB:L96–99 | yes |
| group C cap 6 (52 / 52 / 60) | r8 4 / 2 / 3 → r16 10 / 8 / 11 | x1 | RC6:L56–57, L101–102 | yes |
| held-out greedy (`data/p2/heldout.jsonl`, 5,000, k 1, T 0) | best-cap12 T1 .992 / .990 / .993; frozen .926 / .951 / .903; trajectory seeds EI r8 .985 / .992 / .994 (Stage-1 .921 / .936 / .962); SN-cap12 T1 .963 / .976 / .973 / .979 | | NM:L1577–1578; NM-GB:L1733; TJ:L52 | yes / exec-table |
| `rl_targets` solved (/4,495) | pend pass@32 3,676 / 3,705 / 3,741; r8 4,383 / 4,365 / 4,407; r16 4,403 / 4,433 / 4,429 | cumulative over rounds | R16:L35 | yes |

## 4. RL-algorithm comparisons we ran

1. **Recipe/size, same T1 ladder (best-state).** best − ours (9.56M vs 3.2M) IQM: textbook72 cap 6 frozen +4.0, cap 6
   T1 **+18.3**, cap 12 frozen +1.2, cap 12 T1 **+14.2** (MDD 9.3 / 6.5); dev +146.7, +292.2, −18.2, +103.8 (MDD 88 /
   61) [BS:L104–110]. Not compute-matched: on A40 the best12 ladder used **1.6–1.9×** our GPU-s at equal attempts
   (1,793,960 gate samples per clean ladder) [BS:L128–133]. Claim-audit recount: cap-12 dev +104.3 [CA:L57–58].
2. **Compute-match (3.2M ladder at k 64 = 1.02× best12's ladder A40-s).** best12 − cm12 **+15.67** textbook72
   [15, 16], **+87.3** dev [60.3, 119.3]; cm12 − SN12 paired −1.33 textbook72, +13.7 dev (inside MDD 61) [CM:L93–95,
   L99–104]. Matched on A40-s only; cm12 drew 1.82× the attempts, 1.90× tokens [CM:L120–129].
3. **EI vs GRPO from the same pend (grpo-best; trajectory seeds; equal sampled attempts 1,792,168 vs 1,793,960).**
   Group C r8 x1: EI 3 / 1 / 1; default 2 / 9 / 3; unlikely 3 / 8 / 4; pass@4 6 / 19 / 3 (+7.7 vs EI, outside MDD 3.5,
   mostly seed 1; Welch t ≈ 1.55) [GB:L94–106]. All 322 x1: EI 288 / 284 / 290; default 278 / 278 / 279 (sign test 15 vs
   38, p 0.0022, favours EI); unlikely 277 / 277 / 279 (15 vs 44, p 0.0002); pass@4 286 / 301 / 285 (33 vs 20, p 0.098)
   [GB:L115–120]. Dev means: default 1,026, unlikely 1,027, EI 1,053, pass@4 1,058 [GB:L123–125]. GRPO settings: G 8,
   256 theorems / update, 561 updates, AdamW lr 3e-5, no KL, T 0.8, caps 256 / 48 [GB:L45–47]. GRPO GPU-s 1.00–1.13×
   EI's (co-tenant wall-clock), train tokens 0.17–0.37× [GB:L203].
4. **Search as the EI expert (search-expert; SN-cap12 3.2M; 6 seeds).** Q (/291): A sampling expert 113.7 mean, B
   best-first 112.3; B − A −1.3 (CI [−7.1, +4.5]; MDD 18.2 or 7.9); B spent 22.6–24.6 % of A's actions; C
   (truncate-and-resume) − A2 −8, −8; T1 recipe beats A by 63–96 on all 4 seeds (ingredient unidentified) [SX:L89–107,
   L110–115, L134–137].
5. **Test-time PUCT + learned value vs sampling (mcts-a; frozen best-cap12 pend / r8; matched wall clock).** Gate
   **FAIL**: group C r8 sample 4 / 2 / 4 vs value 2 / 2 / 3; value − sample −1.00 [−3.00, +1.33]; pend rrQ100 value −
   sample +19 / +10 / +14; at r8 value within ±3 of sampling on every pool [MC:L79, L90–94, L101–111].
6. **More EI rounds (rl-continue, r9–r16).** Cap 12: group C pass@256 mean +0.216 (3 / 3 seeds rise; s1 large via
   excluded middle); textbook72 +3 / +9 / +3 [RC:L105–116, L145–151]. Cap 6: C +0.121, textbook72 +2 / −2 / +1
   [RC6:L99–111]; cap 6 r16 is still 77 / 116 / 102 targets below cap 12's r16 [RC6:L128].
7. **Early-start EI and replay-only controls (rl-from-ckpt).** Ladders from p5000–p16000 end within 4 textbook72 of the
   pend arm; from p1600 13 short; EI − replay-only control at pend **+15.0** textbook72 [11.0, 19.3], +28.0 holdout250
   (ladders train on 1.3–1.6× the control's tokens) [RFC:L140–159].
8. **Target supply (frontier-supply; SN-cap12 3.2M; compute-matched).** Supply − control +7.5 of 291, inside the
   pre-registered MDD 10.5 [FS:L6–11].
9. **Compute-matched creation (capability-defs).** r8 equal-k "created" set 54 / 51 / 60 shrinks to 22 / 21 / 14 when the
   base gets RL's GPU time as attempts (K_eval-set 19,281 / 21,107 / 23,310); set-level Δ_cov +21 / +16 / +12 (r16 +24 /
   +32 / +14); RL-free controls at k 256: replay-only 239 / 244 / 249, J7 continuation 220 / 215 / 219 (of 322) [CD:L67–69,
   L117–127].

## 5. Guided read-out (plain vs guided-logical)

Arms: plain = a rejected action ends the attempt; guided-logical = actions rejected by the environment or by
`step_check.py` (prefilter rules) are redrawn without replacement, ≤ 10 per attempt [GT:L45–50]. Checker evidence is
step-level only (0 false rejects / 0 misses on 314,541 pairs) [GT:L110–118].

- **Matched sampled tokens** (pre-registered; k' = k · c_plain / c_arm, unbiased pass@k', interpolated) [GT:L56–58]:
  - long (90), cap 12: plain at k 64 36.8 / 28.7 / 40.2 %; logical − plain **+10.0 / +9.9 / +5.2 pp, IQM +9.1**; at
    k 256 +11.1 / +12.7 / +3.4, IQM +10.0; structural − plain IQM −0.8 [GT:L80]. Executor CI [+3.7, +13.5]; reviewer
    [+5.9, +11.7] [GT:L85–87].
  - long, cap 6: plain at k 64 21.8 / 24.1 / 17.9 %; logical − plain +7.4 / +8.1 / +10.3, IQM **+8.3**; k 256 IQM +8.4
    [GT:L81].
  - textbook72 k 64 IQM +5.4 (cap 12) / +4.8 (cap 6); Roy (78) +5.2 / +7.5; ≤ 10 lines (97) +2.6 / +9.7; 11–20 (67)
    +10.3 / +10.4; all 259 +5.6 / +7.9 [GT:L92–94]. Per seed textbook72 k 64 cap 12: plain 62.4 / 61.6 / 71.7 %,
    logical 68.1 / 67.8 / 75.1 % [GTA:L98].
  - Matched wall-clock agrees within ≈ 0.5 pp on long at k 64 (logical +9.1 / +8.8) [GT:L97–98]; at k = 1 structural
    loses in 6 / 6 and logical loses in 4 / 6 cells [GT:L99–101].
- **Solved@256 attempts (not compute-matched)**, all 259: cap 12 plain / structural / logical 178/185/200, 172/176/190,
  188/193/199; cap 6 152/158/171, 148/151/173, 134/147/163 [GT:L102–103]. textbook72 and release per file: §3a, §3d.
- **Guided on pend / r8 / r16 (capability-defs J3; tb72 + h250 = 322; guided with plain x1 in brackets)**: cap 12 pend
  260 (230) / 266 (238) / 270 (236); r8 293 (288) / 289 (284) / 297 (290); r16 295 (291) / 303 (303) / 303 (295); cap 6
  pend 212 (171) / 188 (144) / 202 (143), r8 274 (268) / 277 (269) / 274 (260), r16 284 (277) / 281 (274) / 284 (272).
  Guided ≥ plain at 18 / 18 checkpoints [CD:L232–240]. textbook72 guided − plain (derived from NM-CD): cap 12 pend +8 /
  +10 / +12, r8 +6 / +4 / +3, r16 +4 / −1 / +6.
- **Cost:** per read (mean of 3 seeds, A40), cap 12 plain 792 GPU-s / 14.7 M sampled tokens; logical 1,729 / 26.2 M
  (2.18×, 1.78×); structural 3.17×, 1.88×; cap 6 logical 2.34×, 2.68× [GT:L137–142]. Peak 20.8–42.3 GB at batch 2,048
  [GT:L144].

## 6. Noise floor / MDDs for the headline quantities

- **`NOISE_FLOOR.md` does not cover the state models.** It applies to the 3,214,336-param `lean_seq` cap-6 control only
  [NF:L10–16]; MDD = 5.364 · sd at n = 2 per arm (1.794 · sd at n = 6, 1.183 · sd at n = 13) [NF:L53–57]; ≈ 99 % of
  variance is the individual training run [NF:L79–84]; sampler and checker ≈ 0 [NF:L85–88]. It has no textbook72 or dev
  row.
- textbook72 (best-cap12 family, seeds as arms): pre-registered MDD **6.5** at cap 12, **9.3** at cap 6 (pooled per-seed
  SDs, two-sample t, 80 % power) [BS:L101–106]; ≈ **6.9** at 3 vs 3 (reviewer) [CM:L68–69]; ≈ **7** at n = 3 [RFC:L149];
  ≈ **7.8** at n = 3 [CA:L72]; **9.8** from EI's x0 seed spread (48 / 49 / 54) [NM-GB:L1730]. 3.2M paired T1 − frozen:
  pre-registered ≈ 8, ≈ 7.4 at the observed sd (n = 4 paired) [TB:L105–107]; whole-proof cells: ≈ 7 floor [EA:L76, L115].
- dev metric: **61** (cap 12) / **88** (cap 6) [BS:L101–106]; ≈ 65 at 3 vs 3 [CM:L68–69].
- holdout250: ≈ 5 at n = 3 (14 at p1600) [RFC:L149].
- all 322 (tb72 + h250): **9.3**; group C solved: **3.5** (from EI's sd 1.15) [GB:L64–66, L104]; group C per-seed MDD
  ≈ 6–7 [MC:L169–171]; r8 seed spread of C pass@256 0.055 (cap 12) [RC:L112–113], 0.038 (cap 6) [RC6:L108–109].
- guided − plain (long): executor's MDD ≈ 2.7 pp "not independently derived"; reviewer's per-seed band ≈ 4–5 pp
  [GT:L88–89]; ≈ 3 pp for the IQM [COE:L612–613]; executor bootstrap-over-attempts MDD: cap 12 logical 2.8 pp (k 64) /
  3.4 (k 256), cap 6 2.1 / 3.5 [GTA:L49, L55].
- long-pool Q291: MDD 18.2 (A vs A2 re-draw) or 7.9 (between-seed sd of B − A) [SX:L100–102]; supply MDD 10.5 [FS:L9].
- Re-draw (same checkpoint) spread: best-cap12 r8 textbook72 across x0 / x1 / x2: s0 48 / 48 / 49, s1 49 / 48 / 50, s2
  54 / 53 / 55 (derived from TJ:L108, RC:L148, MC:L81); batch 4,096 vs 2,048 re-draws moved whole-proof counts −4 to 0
  on textbook72, −5 to +7 on dev, −2 to +3 on holdout250 (11 pairs) [EA:L90–91]; identical-seed rerun nondeterminism
  ≈ half the seed spread is "weaker than stated" (variance ratio 0.543, F 95 % [0.23, 2.05]) [CA:L73].

## 7. Compute per arm (GPU-seconds are card occupancy; classes differ)

| arm (per seed) | GPU | GPU-s | other | source |
|---|---|---|---|---|
| best-cap12 Stage-1 (best-state) | A40 | 1,283–1,292 (23,951–24,123 steps) | | BS:L51, L82 |
| best-cap12 T1 ladder r1–r8 (best-state) | A40 | 25,876 / 30,524 / 28,952 | 1,794 k clean attempts; 393–419 M gen tokens; 4,800 train steps; 1.28–1.30 M Lean checks | BS:L82; NM:L1652–1660 |
| best-cap12 Stage-1 (trajectory) | A40 | 1,350 each | 442 / 447 / 447 M train tokens | TJ:L94 |
| best-cap12 T1 ladder r1–r8 (trajectory) | RTX A6000 | 22,350 / 24,467 / 27,021 | 1,794 / 1,794 / 2,011 k attempts (s2 incl. OOM round); 754 / 783 / 751 M train tokens | TJ:L95 |
| best-cap12 r9–r16 (rl-continue) | A40 | 33,248 / 32,830 / 31,457 (reviewer; executor 33,261 / 32,844 / 31,471) | 1,793,960 attempts; 478.5 / 481.7 / 469.8 M gen tokens; 4,800 steps | RC:L179–185; R16:L57–58 |
| best-cap12 total to r16 (trajectory seeds), **derived** | mixed | 56,948 / 58,647 / 59,828 (= 1,350 + 22,350 + 33,248; 1,350 + 24,467 + 32,830; 1,350 + 27,021 + 31,457) | ≈ 15.8–16.6 GPU-h | derived |
| best-cap6 T1 ladder (best-state / trajectory-cap6) | A40 | 20,057 / 16,881 / 17,885; 17,990 / 17,730 / 16,763 | | BS:L81; TJ6:L101 |
| best-cap6 r9–r16 (incl. r16 reads) | A40 | 33,464 / 25,666 / 26,517 | ≈ 1.82 M attempts | RC6:L164–168 |
| 3.2M SN-cap12 Stage-1 / ladder | 3090 / A40 | 1,852 / 1,835 (3090), 2,244 / 2,250 (A40); 12,672 / 12,992 (3090), 16,623 / 16,042 (A40) | 1,799 k attempts | BS:L84 |
| 3.2M cm12 ladder (k 64) | A40 | 27,485 / 29,226 / 30,675 (mean 29,129 vs best12 28,451: 1.02×) | 3,529,640 attempts | CM:L120–121 |
| GRPO ladders (561 updates) | A6000 (pass@4 s2 A40), 2 per card | default 25,250 / 24,571 / 28,861; unlikely 25,460 / 24,825 / 25,061; pass@4 25,392 / 25,271 / 29,360 | train tokens 128–277 M | GB:L197–201 |
| textbook72 read, per checkpoint (3.2M T1) | A40 | 101.0–108.6 | 18,432 attempts | TB:L63 |
| guided-tts read, 259 theorems × 256 (cap 12) | A40 | plain 792; logical 1,729 | 66,304 attempts | GT:L137–139; NM:L1763 |

Run spend: best-state 60.74 pod-h / $29.76 [BS:L74–76]; trajectory 53.92 / $28.00 [TJ:L84]; rl-continue 29.96 /
$14.68 [RC:L61–63]; guided-tts 9.07 / $4.45 [GT:L59–61]; grpo-best 68.10 / $35.27 [GB:L72].

## 8. Checkpoint paths and eval commands

Best checkpoints (all `hf://buckets/dan-pandori/nd-rl/…`):
- cap 12 r8: `best-state/ckpts/bs/ladder/la_T1_best12_s{0,1,2}_r8.pt` (52 / 51 / 52 tb72) and
  `trajectory/ckpts/tj/ladder/la_T1_best12_s{0,1,2}_r8.pt`.
- cap 12 r16: `rl-continue/ckpts/rc/ladder/la_T1_best12_s{0,1,2}_r16.pt`; more seeds:
  `create-or-elicit/ckpts/coe/ladder/la_full_s{3,4,5}_r16.pt`.
- cap 6 r8 / r16: `best-state/ckpts/bs/ladder/la_T1_best6_s{0,1,2}_r8.pt`,
  `trajectory-cap6/ckpts/tj6/ladder/la_T1_best6_s{0,1,2}_r8.pt`, `rl-continue-cap6/ckpts/rc6/ladder/la_T1_best6_s{0,1,2}_r16.pt`.
- GRPO-pass@4 r8: `grpo-best/ckpts/gb/gb_passk_s{0,1,2}_r8.pt`.
- Frozen: `best-state/ckpts/bs/stage1_best12_s{0,1,2}_b1200.pt`, `trajectory/ckpts/tj/stage1_best12_s{0,1,2}_b1200.pt`.

Commands (pod scripts on the fork; `source pod/<run>/env.sh` first):
- textbook72: `python3 state_eval.py --ckpt $CK --in data/bs/textbook72.jsonl --k 256 --temperature 0.8 --seed 0 --batch 2048
  --max_action 512 --max_steps 96 --lenfield reference_lines --out … --summary …` [READ-BS:L12–13].
- dev: same with `--in data/bs/dev1108.jsonl --k 64 --lenfield n_lines` [READ-BS:L14–15]; holdout250: `--in
  data/bs/holdout250.jsonl --k 256 --lenfield n_lines` [READ-BS:L16–17]; held-out greedy: `--in data/p2/heldout.jsonl
  --k 1 --temperature 0` [READ-BS:L18–19]; rr600 / long2: `python3 lpool_reread.py … --in
  data/ladder/transfer_long_rr600.jsonl` / `transfer_long2.jsonl --k 256 … --lenfield L_true_lb` [READ-BS:L20–23].
  `LEAN_GATE_DUMP` keeps every literal sample text [READ-BS:L5, L10].
- `state_eval.py` defaults are **not** the read settings (`--k 1 --temperature 0.0 --max_action 256 --max_steps 48`
  [fork:state_eval.py:L25–31]); always pass them explicitly.
- Guided: `python3 guided_eval.py --ckpt … --arm {plain,structural,logical} --k 256 --seed 1 --batch 2048 --sets $SETS
  --out …` [READ-GT queue.sh:L10]; defaults T 0.8, `max_action` 512, `max_steps` 96, `max_rej` 10 [fork:guided_eval.py:L42–48];
  env `ND_SAMPLE_PATH=fast`, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, `LEAN_GATE_WORKERS=32`; `SETS` =
  `data/gt/{tb72_textbook_dev,tb72_textbook_train,candidate_v0,candidate_v1,batch3,hand_proved_14}.jsonl` (fork
  `pod/gt/env.sh`). Logical arm runs only after `step_check_validate.py` passes on the plain dumps [READ-GT queue.sh:L15–18].
- Input format for re-scoring another set: jsonl rows with `name`, `prompt` = `THM <premises, comma-separated> SEQ <goal>
  PRF` (ASCII `v & > ~`, e.g. `THM ( P & ( Q v R ) ) SEQ ( ( P & Q ) v ( P & R ) ) PRF`) and a length field for
  `--lenfield` (fork `data/bs/textbook72.jsonl`, `data/bs/dev1108.jsonl`).
- Memory: plain reads 16.4–28.2 GB at batch 2,048–4,096 [BS:L73; TB:L54–55]; guided 20.8–42.3 GB at 2,048 (OOM →
  1,024 is a disclosed re-draw) [GT:L52–53, L144].

## 9. Ambiguities and caveats (for the comparison)

1. **Which textbook72 r8 number.** Two independent seed sets of the same recipe: best-state's 52 / 51 / 52 (x0) and
   trajectory's 48 / 49 / 54 (x0), 48 / 48 / 53 (x1), 49 / 50 / 55 (x2). SEO's guided table and R16's r8 column use
   trajectory x1. best-state's cap diagnostic raised s1 51 → 53 and s2 52 → 53 at 2× caps [BS:L168–175].
2. **Long pool 13–16 is two different quantities:** Q (/380, generator theorems, k 256; SEO:L37) vs rr600 rows with
   `L_true_lb` 13–16 (/400, k 64; R16:L36). Not comparable [RC:L51–52].
3. **Group C** values in R16 are fractions (pass@256 = share of the seed's C set solved on x1), not counts; C is defined
   on x0, so r8's non-zero values are re-draws [RC:L49–50, L107–108].
4. **dev1108 and holdout250 are subsets of the ladder's transfer pool** (local check: 1,108 / 1,108 and 250 / 250 names
   in `data/ladder/transfer.jsonl` (2,285); dev ∩ h250 = 0; h250 `L_true` 7–14). The ladder samples that pool every round
   (k 32) but never trains on it [RC:L37–38; TJ6:L70–71]. Premise-order overlaps: 1–2 dev1108 theorems, 1 textbook72
   theorem (`textbook_3ed45280…`, disjunctive syllogism, in K12) [BS:L177–180]; `candidate_v0/textbook_9d21fccc…` shares a
   renaming class with K12 [GT:L176–180]. Cap-12 textbook72 counts are inflated by ≤ 1 [EA:L106–108].
5. **Robbie's protocol differs:** his textbook72 cells were RL-trained on train14 (14 / 72) and judged by Lean ∧
   `nd_verify` [EA:L80–82, L117–118]; our textbook72 is scoring only. Prefer **dev58** for cross-person comparison. His
   combined model: 32 / 30 / 32 (Lean ∧ `nd_verify`) [BS:L148–150; TB:L125–127]. SEO:L51–52's "904 on the dev metric"
   for his combined model has no traceable source in nd-rl docs or summaries (grep finds it only in SEO).
6. **Exact match to Robbie's dev metric:** our dev1108 is re-derived from his selection rule; the md5 of
   `transfer.jsonl` against his fork commit `51604b3` could not be checked [BS:L184–185]. Our reads are k 64, T 0.8, in
   our state env, Lean alone.
7. **Exec-table values:** J3 pool splits (NM-CD), COE s3–s5 textbook72 (NM-COE), per-seed GRPO dev / textbook72
   (NM-GB) and the long counts (GTA) come from executor tables. Reviewed aggregates reproduce them: all 18 J3 rows sum to
   CD:L236–237's 322 totals (checked by arithmetic); GB means match GB:L123–125; GT "every solve count … reproduces"
   [GT:L8–10]; GT per-file sums equal GT:L102–103's 259 totals.
8. **Re-draws:** guided r8 s2 textbook72 is 57 in guided-tts and 56 in J3 (same settings, different theorem batch).
   Batch changes (4,096 vs 2,048; OOM → 1,024) are re-draws [BS:L65; EA:L90–91].
9. **Truncation above the 0.1 % policy** in many reads (r16 single textbook72 rows up to 6.6 %, tb72 group C up to 1.03 %
   [RC:L154–169]; best-cap12 T1 textbook72 up to 2.04 % [BS:L168–175]; cap 6 C strata 3–19 % [RC6:L136–151]). Counts are
   lower bounds; ≤ +2 per checkpoint on textbook72 where tested.
10. **Guided is not compute-matched** at k 256 attempts (≈ 1.8–2.7× tokens, 2.2–3.2× GPU-s); quote matched-token deltas
    for fair comparisons [GT:L132–142; CD:L243–244].
11. **GPU classes differ** (A40 vs RTX A6000 vs RTX 3090); trajectory's r1–r8 ladders ran on A6000, rl-continue's r9–r16
    on A40; capability-defs' K_eval-set mixes A6000 ladder seconds with an A40 per-attempt cost [CD:L70–71].
12. **No r16 numbers on dev1108 or Charles's release**, and no r16 guided read on the release; r16 guided exists only on
    tb72 + h250 (J3). No numbers on `hard712`, `charles149`, `hard12` or `release_2026-10-12_textbook72_distract2` exist
    on our side (grep of nd-rl `origin/dan` docs and summaries finds them only in the peer-rl-review brief).
13. Judge: every number in §3 is Lean alone (post-2026-09-27), except the C0 whole-proof ladder's training judge (Lean ∧
    `nd_verify`, re-read under Lean alone) [SC12:L41].
