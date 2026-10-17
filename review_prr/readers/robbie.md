# Robbie: improving RL and test-time performance (independent reader notes)

Reader: research assistant to the independent reviewer, 2026-10-17. Everything was read with
`git -C ~/nd-rl show / ls-tree / grep / log`. The only other source was WebFetch of robbiewmthompson.com.
Nothing was checked out, fetched or written in ~/nd-rl, and no checkpoint was downloaded. The one file
written outside this document is a PNG copied out of git into /tmp so the GRPO timeline figure could be read. It
has since been deleted.

**Ref abbreviations** (heads as of today)

| code | ref @ head (last commit date) |
|---|---|
| RE | `origin/robbie-experiments` @ 99f3c37 (2026-10-14) |
| AL | `origin/autoresearch-loops` @ 9ebcb0a (2026-10-08) |
| AT | `origin/autoresearch-thoughts` @ 45a0d43 (2026-10-08) |
| AP | `origin/autoresearch-pretrain` @ 84d2769 (2026-09-29) |
| WT | `origin/robbie_where-things-are` @ 84dafbd (2026-10-01) |
| PR | `origin/robbie_pretrain_recipe` @ 76740e5 (2026-09-30) |
| DM | `origin/dmitry/main` @ af00a58 (2026-10-06); used only to identify the temperature sweep's judge |

**Path abbreviations** (`Lnn` = line number in that file, checked with `sed -n`/`grep -n`)

| code | path |
|---|---|
| RETRY | RE:`experiment-summaries/2026-10-08-retry-ei/README.md` |
| RH / RP | RE:`code/experiments/current/retry_ei_20261008/harness.py` / `pretrain.py` |
| WALL | RE:`experiment-summaries/2026-10-14-grpo-wall-model-diff/README.md` |
| MD | RE:`code/experiments/current/model_diff_20261014/README.md` |
| TS / TST | RE:`code/experiments/current/temp_sweep_20261006/README.md` / `results_table.md` |
| CM | RE:`experiment-summaries/2026-09-28-combined-model/README.md` (blog draft, last edit 2026-10-06) |
| CP | RE:`experiment-summaries/2026-09-28-combined-pipeline/README.md` |
| FACT | RE:`code/experiments/current/factorial_20260929/README.md` |
| TTS | RE:`experiment-summaries/2026-09-29-test-time-scaling/README.md` |
| BIG | RE:`experiment-summaries/2026-09-30-bigger-model-longer-pretrain/README.md` |
| LOOPS | AL:`experiment-summaries/2026-10-08-test-time-loops/README.md` |
| LREAD | AL:`code/experiments/current/autoresearch_loops/README.md` |
| SPIKE / SPIKET | AL:`code/experiments/current/looped_spike_20261006/README.md` / `results_table.md` |
| THO | AT:`experiment-summaries/2026-10-07-test-time-thoughts/README.md` |
| COCO | AT:`code/experiments/current/coconut_spike_20261006/README.md` |

---

## 1. Inventory of documents read (newest first)

| date | document | used for |
|---|---|---|
| 2026-10-14 | WALL (+ `figs/f2_grpo_timeline.png`, read as an image); MD; RE:`.../model_diff_20261014/out/hardpop.txt`, `nd.py`, `gen_check.py`, `figures.py` | GRPO wall and model diff |
| 2026-10-08 | RETRY; RE:`.../retry_ei_20261008/README.md`, RH, RP, `analyze.py`, `episodes.py` | retry-EI |
| 2026-10-08 | LOOPS; LREAD; AL:`.../autoresearch_loops/RESULTS.md`, `harness.py` (sha256 prefix 2eec1b61666a), `remote.sh`, `results/590_control-untied-198/results.json`; SPIKE; SPIKET; `passk_page.py` | test-time loops; the RL-efficiency recipe; run 590 |
| 2026-10-08 | THO; COCO | test-time thoughts |
| 2026-10-06 | TS; TST; RE:`.../temp_sweep_20261006/sweep_remote.py`, `remote.sh`, `analyze.py`; DM:`.../proof_selection_20261006/code/collect_pools.py`, DM:`.../proof-state/nd-takehome-dan/lean_judge.py` | temperature sweep and its judge |
| 2026-10-06 (first drafted 09-29) | CM; RE:`.../2026-09-28-combined-model/charts/passk.csv`, `runs.csv`, `textbook-tts.csv` | blog draft: factorial, test-time scaling, TTRL, proof state |
| 2026-10-05 / 09-30 | RE:`code/experiments/current/ttrl/ttrl.py`, `scale.py` | TTRL and test-time EI on dev |
| 2026-10-01 | WT:`docs/WHERE_THINGS_ARE.md` | where the checkpoints are; list of blog posts |
| 2026-09-30 | BIG | bigger model and longer pretraining |
| 2026-09-30 | PR:`code/shared_code/README.md` | run 198 recipe and judge advice |
| 2026-09-30 | RE:`code/experiments/current/state_recipes_20260930/README.md`, `harness_state.py` | proof-state judge |
| 2026-09-29/30 | TTS; RE:`.../2026-09-29-test-time-scaling/charts/scaling.csv`; RE:`.../test_time_scaling/engine.py`, `analyze.py` | test-time scaling on c005 |
| 2026-09-29 | FACT | 2×2×2 factorial |
| 2026-09-29 | AP:`code/experiments/current/autoresearch/harness.py` (sha256 prefix 2aa52f23e7ec), `score_holdout.py`, `textbook72/MANIFEST.json`, `RESULTS.md` (rows 153, 186, 198) | definition of the dev metric; textbook72 scoring |
| 2026-09-28 | CP | combined pipeline c001 to c005 |
| 2026-09-26 to 29 | RE:`experiment-summaries/2026-09-21-pretrain-ablations/README.md` | context only (definitions of the dev metric and textbook72) |
| blog | https://robbiewmthompson.com/blog/ (the index lists no nd-rl post); https://robbiewmthompson.com/blog/combined-model/ ("Published September 29, 2026"); https://robbiewmthompson.com/blog/pretraining-ablations/ ("Published September 26, 2026") | published versions |
| not found | Guessed slugs /blog/retry-ei/ and /blog/grpo-wall/, plus /sitemap.xml, /sitemap-index.xml and /rss.xml, all return HTTP 404. **The long-RL experiment** that WALL analyses (GRPO v3/v4, EI v2/v4) is not committed on any ref allowed here: there is no `long_rl_20261014` folder, and the linked note `.claude/notes/long-rl-what-models-learn.md` is missing from RE, AL, AT and main. | |

Blog quotes below come from WebFetch, which passes the page through a summarising model. They are probably
verbatim but are marked "(WebFetch)".

---

## 2. What Robbie tried to improve RL and test-time performance, and what happened

All of Robbie's write-ups carry `written_by: agent:claude`. None of them, and nothing else in git, records a
review by a third party.

### 2.1 RL side

| attempt | outcome as he reports it | cite |
|---|---|---|
| Combined pipeline (c001 to c005): 186 pretraining, then Leon's EI recipe, then verifier-guided RL sampling | **Worked.** Leon's recipe: "+117 on the same pretrained weights and samples". Guided sampling: "another +101". The best in-budget pipeline (c005) scores "904 vs 680–687" | CP:L44, L46, L56-57 |
| Full 4,495-target RL pool | "did nothing measurable (c003: +3.7, inside pretraining noise)" | CP:L50 |
| 2×2×2 factorial (format × pretraining × RL) | Average effects: "pretraining … **+408**", "RL … **+268**", "data format … **+92**". "Leon's RL buys coverage, not accuracy" | CM:L18-20, L29-30 |
| RL-efficiency recipe found by the test-time-loops autoresearch loop (507: token-budget fine-tune batches; 509: Muon fine-tune; 510: more and shorter rounds) | **Worked.** Run 198's untied model with 507's `rl()` "scores 792 (790/785/800), against 680 under the old harness" | LOOPS:L86-88 |
| Bigger model / longer pretraining (38M params; 1,200 s) | **Did not work.** "no gain, and a seed coin flip" | BIG:L6, L62-63 |
| Dan's proof-state interface with plain EI, 4 recipes | **Worked** on the dev metric: "The proof state wins on every recipe: +111 to +178 over the whole proof (medians)". Judged by Lean alone | CM:L441, L461 |
| Retry-EI: multi-attempt episodes with Lean error tokens (arms retry, blank, repair, resume, resume_rl) | **Did not work.** "Every variant proved fewer dev theorems than plain expert iteration." | RETRY:L15-17 |
| GRPO (long-RL experiment): only analysed after the fact | 1 of 4 GRPO runs crossed a "wall" (depth-3 box closing). EI learned the same thing gradually. Model diffing finds "no new features", only a "small, distributed change to blocks 0-2" | WALL:L11-13, L34-35, L45-56 |

### 2.2 Test-time side

| attempt | outcome | cite |
|---|---|---|
| Resampling invalid lines (verifier-guided line redraw, cap 10) on c005 | **Worked**, mostly at low k: "pass@1 goes from 31.2% to 57.4%", and "+4.7 points overall" at k = 64 for "1.5× plain's wall-clock" | TTS:L135, L105-106 |
| Sampling without replacement over rejected lines (SWOR) | Small gain: "+2 points at pass@1 and +1 at pass@64, for about 5% more tokens" | TTS:L181 |
| SMC | "second, just behind resampling" | TTS:L140 |
| Beam search, best-first search | **Did not work**: "no better than plain sampling at matched tokens" | TTS:L143 |
| Learned value head | **Did not work**: "No gain from V." | TTS:L253 |
| k = 1,024 on theorems no method solved | "About 90% stay unsolved at 1,024 resampled attempts" | TTS:L202 |
| Temperature sweep (on Dan's r16 proof-state prover, not his own model) | "boring, T=0.8 is fine". "Nothing here changes what anyone should do." | TS:L7, L13 |
| Test-time RL (TTRL with statement-only variants) and plain test-time EI on the dev failures, i.e. training on the eval statements | Both raise cumulative dev coverage far above sampling more. "Plain expert iteration on the eval statements wins. Variants add little." | CM:L323, L329-333 |
| Looped transformer, more loops at test time | **Did not work**: "Extra loops are worth 2 to 4% on dev for three times the compute per sample, the benefit saturates by about 4 loops" | LOOPS:L14-16 |
| Coconut-style continuous thoughts | **Did not work**: "no test-time scaling". The best thoughts-loop model scores 711 against the 792 untied control | COCO:L12, THO:L53, L68-69 |

---

## 3. Headline numbers as Robbie reports them

**Legend for the repeated columns**

- **Eval sets**
  - DEV: dev half (`sha1(key) % 2 == 0`) of fork 51604b3's `data/ladder/transfer.jsonl`, 1,108 theorems, L_true 7 to 14.
  - HO: the holdout half, 1,177 theorems, 114 of them longer than 10 lines.
  - HO250: 250 holdout theorems, all of 7 or more lines.
  - TB72: Dmitry's textbook72 = dev58 + train14, scored together.
  - DEVLONG: the 329 dev theorems of length 10 or more.
  - SP3: the 1,805 spine-3 ladder RL targets. These are training targets, not an eval set.
  - dH250 / dTB72: Dan's `data/bs/holdout250.jsonl` / `textbook72.jsonl` (fork 4dcd0e4f), used in the temperature sweep.
- **Judges**
  - LN: Lean 4 (v4.34.0) AND nd_verify, through fork 51604b3's gate.
  - L: Lean alone.
  - N: nd_verify alone.
  - L?: "Lean-judged" per the docstring; the gate code is not committed.
- **Models.** Every model writes whole proofs in `lean_seq` (Lean 4 tactic text) unless marked state.
  - M198: run 198 recipe. 6 untied Peri-LN blocks, d 384, 8 heads (4 ALiBi + 4 NoPE), MLP 1280, Muon (Polar Express), MTP head in pretraining only, 9,557,760 params. Trained from scratch for 300 s on one A40 on Dan's cap-6 Stage-1 file (155k proofs of at most 6 lines). Sampling stops at 512 new tokens.
  - M186: the same architecture and parameter count (153/186 recipe).
  - M590: the M198 trunk with the loops-harness `pretrain.py` (sha b27dd2cb03ba).
  - MLOOP: shared-core looped trunk, 6.40M params (512 variant: 9.56M).
  - MTHO: M198 plus per-line continuous thoughts.
  - MNAIVE: autoresearch 012 (fork GPT 4×256, RoPE, AdamW).
  - MBIG: 198 recipe at d 768, 12 heads, MLP 2560, 38.0M params, 1,200 s pretraining.
  - MLONG: long-RL checkpoints on the untied 198 trunk (~10M); recipe not committed.
  - MDAN: Dan's `la_T1_best12_s0_r16`. Proof-state interface; not Robbie's model; parameter count not stated.
- **RL recipes**
  - RLF: frozen-harness EI. 4 rounds × 1,500 targets × k 32 at T 0.8. Keeps at most 4 accepted proofs per theorem at weight ×4, replays 20k pretraining records, and fine-tunes 600 steps × 128 with AdamW 3e-4. Budget: 2,400 s total including 300 s of pretraining, one A40.
  - RLL: loops-harness EI with 507's `rl()`. Rounds run until 1,800 s of RL clock are used (Lean time is not charged). Each round samples every target 8 times at T 0.8 and gives failed targets 24 more samples. The fine-tune uses 76,800 records per round in token-budget batches, with 20k replay. 16 to 17 rounds fit. One A40.
  - RLLEON: Leon's EI. About 15 rounds × 400 targets × ~32 samples, hardest-first, T 1.0, fresh AdamW each round, GEM loss. c004/c005 add verifier-guided RL sampling. c005 stops RL 1,800 s after the start (~1,450 s of RL).
  - RLLONG: GRPO or EI for about 180 rounds; details not committed.
- **Rev.** (my check)
  - R: I recomputed it from committed per-problem data: RE:`experiment-summaries/2026-09-28-combined-model/charts/passk.csv`, per-problem `n_ok` of 256, unbiased estimator 1 − C(n−c,k)/C(n,k), averaged over problems and then over seeds. All 32 pass@k entries in CM:L113-120 reproduce to the rounding shown (8 cells × held-out pass@1/64/256 and textbook pass@256). The 8 dev entries match `charts/runs.csv`.
  - X: matches a second committed source.
  - A: I checked the arithmetic (means and differences) from the per-seed numbers given.
  - N: no committed raw data, so it cannot be re-derived from git.

### 3a. RL pipeline numbers

| # | value + metric (as reported) | eval (n) | k | n samp | T | sampler | judge | model | RL + compute | seeds | Rev. | citation + quote |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | 687.3 dev solved (c001) | DEV 1,108 | 64 | 64 | 0.8 | plain | LN | M186 (186's saved weights) | RLF | 0/1/2: 676/703/683 | A | CP:L27 "c001 \| 186 pretrain + frozen harness expert iteration (replay) \| 687.3 \| 676 / 703 / 683" |
| A2 | 804.3 (c002) | DEV | 64 | 64 | 0.8 | plain | LN | M186 | RLLEON, unguided, sample-matched 192k | 776/831/806 | A | CP:L28 "+ Leon's GEAR expert iteration (sample-matched, 192k) \| 804.3" |
| A3 | 808.0 (c003) | DEV | 64 | 64 | 0.8 | plain | LN | M186 (re-pretrained on the pod) | RLLEON + full 4,495-target pool | 809/812/803 | A | CP:L29 |
| A4 | 905.0 (c004); ran 2,583 to 2,728 s, over the 2,400 s budget | DEV | 64 | 64 | 0.8 | plain eval | LN | M186 | RLLEON + guided RL sampling | 925/894/896 | A | CP:L30, L53-54 "c004 overran the harness's 2,400 s" |
| A5 | **904.3** (c005) | DEV | 64 | 64 | 0.8 | plain eval | LN | M186 | RLLEON + guided, 1,800 s deadline; 13/11/13 rounds | 915/893/905 | A | CP:L31 "c005 \| c004 with exact-output sampler speedups + an RL deadline \| **904.3** \| 915 / 893 / 905" |
| A6 | factorial "best" cell 904.0 (a separate run of the c005 recipe) | DEV | 64 | 64 | 0.8 | plain | LN | M186 | as A5 | 916/895/901 | X (runs.csv) | FACT:L57 "lean-best-leon **904.0** (916/895/901, reproducing c005's 904.3)" |
| A7 | factorial cells: naive 142, + Lean 193, + best pretraining 457, + best RL 444, − Lean 782, − best pretraining 414, − best RL 682 | DEV | 64 | 64 | 0.8 | plain | LN (lean_seq) / N (abs) | MNAIVE or M186; abs or lean_seq | RLF or RLLEON | 3 each | X (runs.csv) | CM:L113-120; FACT:L55-58 |
| A8 | main effects "pretraining … **+408**", "RL … **+268**", "data format … **+92**" | DEV | 64 | 64 | 0.8 | plain | LN/N | factorial | factorial | 3 per cell | A (I get 408.1 / 267.6 / 91.8 from the cell means) | CM:L18-20 |
| A9 | best cell: held-out pass@1 30%, pass@64 79%, pass@256 82%; textbook pass@256 44% | HO250; TB72 | 1/64/256 | 256 | 0.8 | plain | LN | M186 | as A5 | 3 | **R** (passk.csv: 0.301 / 0.791 / 0.820; 0.435) | CM:L117 "\| **best** \| **904** \| 30% \| **79%** \| **82%** \| **44%** \|" |
| A10 | best minus best RL: dev 682, pass@1 44%, pass@64 59%, pass@256 62%, textbook 28% | HO250; TB72 | 1/64/256 | 256 | 0.8 | plain | LN | M186 | RLF | 3 | **R** (0.438 / 0.589 / 0.617; 0.278) | CM:L120 |
| A11 | "Leon's RL lowers held-out pass@1 (43.8% → 30.1% on the best pretraining) while raising pass@64 (58.9% → 79.1%)" | HO250 | 1/64 | 256 | 0.8 | plain | LN | M186 | RLF vs RLLEON | 3 | **R** | FACT:L66-67 |
| A12 | "Textbook72 did move: 12.5% → 43.5% pass@256, mostly from RL on top of the best pretraining (27.8% → 43.5%)" | TB72 (dev58 + train14) | 256 | 256 | 0.8 | plain | LN/N | naive → best | factorial | 3 | **R** | FACT:L65-66 |
| A13 | 590 control **792** (790/785/800), against 680 under the old harness | DEV | 64 | 64 | 0.8 | plain (`n_loops` ignored) | LN | M590 | RLL, 1,800 s RL; 1,311 RL targets solved | 0/1/2 | X (results.json L2210 `seed_metrics`) | LOOPS:L71 "590 control: run 198's untied six blocks with 507's RL \| 792 \| 792"; L87 "scores 792 (790/785/800), against 680 under the old harness" |
| A14 | looped keeps at 8 loops: 675 → 690 → 732 → 748 → 764 → 766 | DEV | 64 | 64 | 0.8 | plain, `n_loops` = 8 | LN | MLOOP | RLL variants (500 to 512) | 3 each | X (RESULTS.md) | LOOPS:L65-70 |
| A15 | 198: 681 (680/670/694); 9.6M params at 1,200 s: 420 (702/294/265); 38M params at 1,200 s: 440 (710/300/311) | DEV | 64 | 64 | 0.8 | plain | LN | M198 / MBIG | RLF; harness constants changed ("off-protocol") | 3 each | A | BIG:L38-40; L18-19 "so this is off-protocol" |
| A16 | textbook /72: 18.3 / 18.7 / 18.0 (same three arms) | TB72 | 256 | 256 | 0.8 | plain | LN | as A15 | as A15 | 3 | A | BIG:L38-40 |
| A17 | proof state vs whole proof, per seed: 198 whole 669/692/216 against state 852/824/798; "+111 to +178 … (medians)" | DEV | 64 | 64 | 0.8 | state: step env, 256 tokens/step, 48 steps | **L** (dan_best-state fork a005ad61) | 4 recipes (198/207/201/204); state interface | RLF (4 rounds) | 3 per cell | A (155, 169, 111, 178) | CM:L436-441; RE:`.../state_recipes_20260930/README.md`:L28-30 "The judge there is Lean alone" |
| A18 | thoughts loop best (708): 711 at 8 thoughts | DEV | 64 | 64 | 0.8 | plain, 8 thoughts/line | LN (fork 51604b3) | MTHO | RLL-like, 1,800 s | 3 | X (THO table) | THO:L53 "708 \| 704's sampling with a token-budget fine-tune \| 711 \| 693 \| keep, incumbent" |

### 3b. Retry-EI (2026-10-08)

Setup that applies to every row in 3b:
- Model and budgets: base is run 590 (M590 plus 33 error/`<fail>` vocabulary tokens), 300 s of pretraining, RLL with a 1,800 s RL budget.
- Eval: DEV 1,108 at T 0.8 and 512 max new tokens. Each theorem gets 64 independent samples, plus (except for `iid`) 8 episodes of up to 8 attempts.
- Judge: LN. RETRY:L39-40 "Acceptance is always the fork's Lean gate and `nd_verify`"; RH:L29-31 "the ones Lean AND nd_verify accept".
- Compute and seeds: one A40 per run, seeds 0/1/2.
- Checkpoints: "Checkpoints were not kept" (RETRY:L59).
- Rev.: A for the means. There is no raw data in git ("not committed", RETRY:L58-59), so N for everything else.

| # | value + metric | k / attempts | citation + quote |
|---|---|---|---|
| B1 | `iid` (plain EI, 590 unchanged): 787/778/747, mean **771** | 64 independent | RETRY:L67 "\| `iid` \| 787 / 778 / 747, 771 \|" |
| B2 | `resume`: 762 (64 independent); 749 (8×8 episodes); attempt 2 accepted 7.3% in episode vs 12.1% independent | 64 / 8×8 | RETRY:L68 |
| B3 | `blank`: 718 / 721; 10.3% vs 10.4% | 64 / 8×8 | RETRY:L69 |
| B4 | `retry`: 712 / 712; 9.9% vs 10.3% | 64 / 8×8 | RETRY:L70 |
| B5 | `repair`: 706 / 660; 1.8% vs 10.4% | 64 / 8×8 (3 attempts in RL) | RETRY:L71 |
| B6 | `resume_rl`: 811/329/717, mean 619; episodes 608 | 64 / 8×8 | RETRY:L72; L129 "`resume_rl`'s 811 is one seed of three, with another at 329" |
| B7 | "Run 590 as recorded: 790 / 785 / 800, mean 792. Run 198 in its original harness: 680." | 64 | RETRY:L74 (X with AL results.json) |
| B8 | reruns at 64 samples: `retry` 717/711/486, `blank` 712/682/260. Pooled over six runs: `retry` 675, `blank` 635, six plain runs 766 | 64 | RETRY:L105-107 "The same arm and seed does not reproduce across pods." |
| B9 | distinct proofs among 8 attempts: `retry` episode 5.7 vs 4.7 independent; "the extra variety is worth about four dev theorems" | 8 | RETRY:L96, L119-120 |
| B10 | RL rounds completed: `iid` 16 to 17, `retry`/`blank` 6 to 8, `repair` 20 to 21. Retry-style arms stalled in 3 of 15 runs against 0 of 6 plain runs | | RETRY:L80, L121 |
| B11 | the per-attempt independent-sample rate is computed "exactly from each theorem's count of accepted samples out of 64" (hypergeometric) | 64 | RETRY:L54-55; RE:`.../retry_ei_20261008/analyze.py`:L6-12 |

### 3c. GRPO wall and model diff (2026-10-14)

Setup that applies to every row in 3c:
- Models are MLONG checkpoints from HF: GRPO v3 s0 ("wall"), v3 s1, v4 s0, v4 s1; EI v2 s0/s1 and v4 s0/s1. Each run has its own pretraining seed (MD:L43).
- The RL recipe, compute and judge of the long-RL runs are **not committed**.
- Rev.: N for everything (artifacts and checkpoints are not in git).
- Seeds: one RL run per label.

| # | value + metric | eval / measure | judge | citation + quote |
|---|---|---|---|---|
| C1 | "spine-3 ladder targets 15% → 97%" for GRPO v3 s0; "seed 1, same recipe, never did" | SP3 (1,805 **training** targets), cumulative solved over ~180 RL rounds | L? | WALL:L11-13. The f2 legend reads "GRPO v3 s0 (1743)", "v3 s1 (235)", "v4 s0 (239)", "v4 s1 (247)" |
| C2 | hard-pop accuracy, teacher-forced (1,000 records): pretrained 21-24%, GRPO with no wall 25-33%, GRPO wall final 69%, EI finals 81-87%, EI v4 s1 52% | teacher-forced pops | n/a | MD:L74-80 |
| C3 | free generation, 60 spine-3 targets × 4 samples at T 0.8: g0_pre 2/240 accepted, g1_fin 28/240, g0_fin 180/240 | SP3 subset | L? ("harness.sample, Lean-judged") | MD:L85-91; RE:`.../model_diff_20261014/gen_check.py`:L3 |
| C4 | transplanting g0_fin blocks into g0_pre: blocks 0-2 → 27/60 targets, blocks 0-3 → 45/60; g0_fin 52/60; g0_pre 1/60 | SP3 subset, free generation | L? | MD:L113-115 |
| C5 | residual patching at closing tokens takes k=1 pops "7% → 88%" | teacher-forced | n/a | WALL:L48 |
| C6 | relative weight change, pretrain → final: GRPO s0 9.0%, GRPO s1 8.7%, EI s0 72% | weights | n/a | MD:L44 |
| C7 | the diff-SAE's top 20 latents take held-out "k1 r2 pops 27% → 60% (top 100: 72%, = the full difference)" | teacher-forced | n/a | WALL:L60-62 |
| C8 | "EI v4 s1 final (dev 186, the weak seed)" | DEV (presumably) | ? | MD:L80. This is the only dev number for a long-RL run in git |

### 3d. Test-time numbers

| # | value + metric | eval (n) | k | n samp | T | sampler | judge | model | seeds | Rev. | citation + quote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 | plain pass@1 31.2%, pass@64 80.8% | HO 1,177 | 1 / 64 | 64 | 0.8 | plain | LN (engine `Gate`, RE:`.../test_time_scaling/engine.py`:L212 "Lean AND nd_verify on finished proofs") | c005 final (M186 + RLLEON) | 3 checkpoints | X (scaling.csv L2, L8) | TTS:L79, L82 |
| D2 | resample (cap 10) pass@1 57.4%, pass@64 85.6% | HO | 1 / 64 | 64 | 0.8 | line resampling | LN | c005 | 3 | X (scaling.csv L9, L15) | TTS:L79, L82; L135 "pass@1 goes from 31.2% to 57.4%" |
| D3 | longer than 10 lines (of 114): plain 6.6 → resample 19.5 at k=1; 40.7 → 54.3 at k=64 | HO, 114 long | 1 / 64 | 64 | 0.8 | plain / resample | LN | c005 | 3 | X | TTS:L79, L82 |
| D4 | compute-matched: resample k=32 84.3% at 10,759 tokens/theorem vs plain k=64 80.8% at 13,971 | HO | 32 / 64 | 64 | 0.8 | | LN | c005 | 3 | X (scaling.csv L14, L8) | TTS:L90-91 |
| D5 | SMC N=64 84.4% at 16,147 tokens; N=32 82.9% at 7,968 | HO | N | | 0.8 | SMC | LN | c005 | 3 | X | TTS:L94-95 |
| D6 | beam B=16 76.6% at 6,784 tokens; best-first 75.8% at 6,800 | HO | | | 0.8 | search | LN | c005 | 3 | X | TTS:L96-97 |
| D7 | `guided_kv`: "1.5× plain's wall-clock for +4.7 points overall and +30% on long proofs" | HO | 64 | 64 | 0.8 | KV-cache resampling | LN | c005 | 3 | N | TTS:L105-106 |
| D8 | SWOR at cap 10: pass@1 59.7, pass@64 86.5 (resample 57.4 / 85.6) | HO | 1 / 64 | 64 | 0.8 | SWOR | LN | c005 | 3 | N | TTS:L178 |
| D9 | stubborn theorems at k = 1,024: plain solves 1/3/3 and resample 12/17/11, of 137/143/147 | HO subset | 1,024 | 1,024 | 0.8 | plain / resample | LN | c005 | per seed | N | TTS:L196-200 |
| D10 | value head: AUC 0.857 overall, "Only 0.689 within theorem and depth"; "No gain from V" | 332 rl_targets val; 300-theorem dev subset | | | 0.8 | SMC/beam/best-first | LN | c005 s0 | 1 | N | TTS:L230-234, L253 |
| D11 | textbook (c005): plain 17.6 / 29.8 / 41.7%; resample 26.0 / 38.6 / 50.5%; no repeats 27.4 / 41.1 / 51.9% at k = 1 / 8 / 256 | TB72 (dev58 + train14) | 1/8/256 | 256 | 0.8 | 3 samplers | LN | c005 | 3 | X (textbook-tts.csv L2, L5, L10, L29, L32, L37, L56, L59, L64) | TTS:L281-285; CM:L191-197 |
| D12 | the same split by subset at 256 samples: dev58 42.5 → 51.7 → 52.3; train14 38.1 → 45.2 → 50.0 | dev58 / train14 | 256 | 256 | 0.8 | | LN | c005 | 3 | X (csv L19, L28, L46, L55, L73, L82) | CM:L204-206 |
| D13 | temperature sweep: T=0 one attempt 0.860 / 0.417; T=0.5 pass@1 0.858 / 0.420; T=0.8 pass@1 0.833 / 0.407; T=0.8 pick-of-8 0.915 / 0.532; T=0.8 pass@8 0.942 / 0.594; T=0.1 pass@64 0.912 / 0.486 | dH250 / dTB72 | 1/8/64 | 64 (1 at T=0) | swept | plain; "pick" = highest mean log-prob at T=1 | L (DM `lean_judge.py`:L2 "Lean alone decides whether a proof counts"; run with Dan's fork 4dcd0e4f) | MDAN (state interface: `state_env`, MAX_ACTION 512, MAX_STEPS 96; DM `collect_pools.py`:L26-30) | 1 generator seed, 1 sampling seed | X (TST) | TS:L31-36 |
| D14 | best oracle pass@64: holdout 0.960 at T 0.5 and 0.8; textbook 0.653 at T 0.5, 0.8 and 1 | dH250 / dTB72 | 64 | 64 | swept | plain | L | MDAN | 1 | X | TST:L9-11, L22-24 |
| D15 | TTRL 48 of 64 vs sampling more 31 at matched samples (2,623 vs 2,412 per target), seed 0; seed 1: 41 vs 31; unrelated variants 28 | 64 dev failures of c005 s0 | cumulative over rounds | ~2,400-2,600 per target | **1.0** | guided (`guided.generate`) | LN | c005 s0 / s1 + test-time training | 2 | N | CM:L276, L280-281, L284, L293-295 |
| D16 | at scale, dev solved (baseline + newly solved targets), 3-seed mean: sample more 1,002 / 1,020; **targets-only EI 1,069 / 1,088**; TTRL 929 / 1,079 (at 1x / 5x) | DEV (each seed's failures: 193 / 215 / 203) | cumulative | 256 per round (16 for TTRL items) | **1.0** | guided | LN ("passes Lean ∧ nd_verify in any round") | c005 s0-s2 + test-time RL on the dev statements | 3 | N | CM:L329-333; L309-311 |
| D17 | c004 s0: EI 1,072 (H100, 127 min) vs TTRL 1,076 (A40, 167 min) | DEV (183 failures) | cumulative | | 1.0 | guided | LN | c004 s0 | **1** | N | CM:L379-380, L386-392 |
| D18 | loops: 8- vs 2-loop gap "+18, +18, +18, +21, +12, +27 across the kept models" | DEV | 64 | 64 | 0.8 | plain at 8 vs 2 loops | LN | MLOOP | 3 | X | LREAD:L49-50 |
| D19 | retry depth on targets that failed 8 tries at 1 loop: 11.4% at 2 loops, 13.8% at 4, 15.9% at 8 | RL targets (~4,100 per arm) | 24 | | 0.8 | plain | LN | MLOOP (502) | within run | N | LOOPS:L89-91 |
| D20 | run 198 seed 0, before RL → after 4 RL rounds → after 12: textbook 15 → 18 → 20 of 72 at k=256 with pass@1 0.114 → 0.151 → 0.173; DEVLONG 0 → 110 → 121 of 329 at k=64 | TB72 / DEVLONG | 1, 256 / 64 | 256 / 64 | 0.8 | plain | LN | M198 | RLF (12 rounds = 4 frozen + 8 more) | **1** | X | SPIKET:L25-26, L32-33, L39-40 |
| D21 | thoughts after RL (701): "thinking is worth 44, 53 and 57 dev theorems on the three seeds" (8 vs 0 thoughts) | DEV | 64 | 64 | 0.8 | plain | LN | MTHO | 3 | N | THO:L58-59 |
| D22 | blog: "At 1x, i.e. doubling the pipeline's compute, it takes dev from 904 to 1,069. That's 81% of the failures solved" | DEV | | | 1.0 | guided | LN | c005 | 3 | A | https://robbiewmthompson.com/blog/combined-model/ (WebFetch) |

---

## 4. Dev metric: definition and eval protocol

**Definition.** "dev theorems solved at L_true >= 7 with EVAL_K attempts". Sources: AP harness L16 (pretraining loop); RH:L34-35 and AL harness L24 (loops harness).

| element | value | cite |
|---|---|---|
| set | The dev half of fork 51604b3's `data/ladder/transfer.jsonl`: `int(sha1(key)) % 2 == 0`. The odd half is the holdout. | RH:L194-200, L620-621; AP harness L193-199 |
| n theorems | 1,108, reference length 7 to 14: "150 of 7 lines, 152 of 8, 477 of 9, 219 of 10, 49 of 11, 54 of 12, 5 of 13 and 2 of 14" | RE:`experiment-summaries/2026-09-21-pretrain-ablations/README.md`:L210-211 ("The dev pool has 1,108 theorems") |
| k = n | `EVAL_K = 64` samples per theorem; 70,912 samples per eval | AP harness L70; RH:L81 |
| T | `TEMP = 0.8`; `MAX_NEW = 512`; `SAMPLE_BATCH = 1024`; sampling seed `seed * 1000 + 777` | RH:L80, L409-412; AP harness L68 |
| estimator | A raw count of theorems with at least one accepted sample among exactly 64 draws: `solved_ge7 = ge[7]` from `lstar()`. One draw of pass@64, reported as a count; not the unbiased estimator. | RH:L141-143, L551 |
| judge | Lean 4 AND nd_verify through fork 51604b3's `sample.generate` gate. Run 590's gate log shows `"both_ok": 691225, "nd_ok_lean_rej": 0, "nd_rej_lean_ok": 1`. | AP harness L12-14; AL `remote.sh`:L16-17 "the reward is Lean AND nd_verify"; AL `results/590_control-untied-198/results.json`:L2250-2253 |
| level knob | Loops/thoughts harnesses only: evaluated at `n_loops = 8` (or 8 thoughts), with the same eval at level 2 (or 0) recorded as a diagnostic. 590 ignores the knob. | RH:L85-87; AL RESULTS.md row 590 |
| aggregation | 3 pipeline seeds (0/1/2), each re-pretraining from scratch on its own A40; the 3-seed mean is reported (590: 790/785/800 → 792) | AL results.json L2210; LREAD:L22 "three seeds per idea in parallel" |
| selection | Dev was the selection set: "'Best pretraining' was found in the Lean format, by the loop that was selecting on this dev metric" | CM:L490-492 |
| holdout status | "The holdout half of the transfer pool has not been scored for any model from the new harness, including the 792" (590 `holdout_metric: null`) | LOOPS:L102-103; results.json L2208 |

**Other eval sets and how they relate to textbook72 dev58 / train14**

- Robbie's "dev" is the ladder **transfer** dev half. It has nothing to do with textbook72's "dev58".
- **textbook72** is scored offline by `score_holdout.py --pool textbook`:
  - "(58 dev + 14 train textbook problems, never trained on)", at `TEXTBOOK_K = 256` (AP `score_holdout.py`:L14, L33).
  - Same sampler, temperature and judge as the dev eval (L11-12).
  - train14 has no reference lengths; dev58's are upper bounds (L38).
  - Nothing is trained on either split, despite the name "train14". MANIFEST rule: "Never train or tune on these or on a renaming of them. Report dev58 and train14 separately and combined." (AP `textbook72/MANIFEST.json`:L5).
- **Robbie mostly reports textbook72 combined** ("of 72", pass@256). He gives split numbers only for c005's test-time scaling (CM:L204-206; textbook-tts.csv), where dev58 runs a few points above train14 at k=256 (plain 42.5 vs 38.1).
- **holdout250**: the first 250 holdout-half theorems ranked by `sha1("passk:" + key)` (AP `score_holdout.py`:L60-63). 256 samples each, unbiased estimator (CM:L91-94).
- **HO (all 1,177)**: used for test-time scaling, with the unbiased estimator `pass_at_k` (RE `test_time_scaling/analyze.py`:L22-24).
- **The temperature sweep's holdout250/textbook72** are Dan's `data/bs/*.jsonl` (DM `pool_lib.py`:L21-22). I did not verify that they are identical to Robbie's own pools.

---

## 5. Low-k / budgeted vs large-k effects, per improvement

| improvement | low k / fixed budget | largest k reported | cite |
|---|---|---|---|
| Leon's EI recipe (on best pretraining, Lean format) | holdout250 pass@1 **43.8 → 30.1 (−13.7)**. Textbook pass@1 0.183 → 0.191 (+0.8; my recomputation from `passk.csv`) | holdout250 pass@64 58.9 → 79.1, pass@256 61.7 → 82.0. Textbook pass@256 27.8 → 43.5. Dev (k=64) 681.7 → 904.0 | FACT:L66-67; CM:L117, L120; FACT:L55-58 |
| Leon's EI recipe, other three pairs | holdout pass@1 7 → 12 (naive), 26 → 28 (abs-best), 8 → 7 (lean-naive) | pass@64 +20 to +27 points in every pair | CM:L113-120 |
| Verifier-guided resampling at inference | holdout pass@1 **31.2 → 57.4**. At matched tokens, resample k=8 (2,690 tokens) 80.2% ≈ plain k=64 (13,971 tokens) 80.8%. Textbook k=1: 17.6 → 26.0 | holdout k=64 80.8 → 85.6. Textbook k=256 41.7 → 50.5 | TTS:L79-82; scaling.csv L8, L12; CM:L193-197 |
| SWOR on top of resampling | pass@1 +2.3 (cap 10) | pass@64 +0.9 | TTS:L178 |
| SMC | N=2: 55.2% at 380 tokens (plain k=2: 46.6% at 437) | N=64 84.4% at 16.1k tokens | scaling.csv L21, L3, L26 |
| Beam / best-first | no better than plain at matched tokens; best-first < 5% within 1k tokens | 76.6 / 75.8% at ~6.8k tokens (plain k=32: 78.5% at 7.0k) | TTS:L143-147; scaling.csv L7, L20, L32 |
| Learned value head | no change (±8 of 300) | no change | TTS:L253-254 |
| Temperature | k=1: T 0 to 0.5 best (holdout 0.858-0.866; T 0.8 0.833; T 1 0.788) | k ≥ 4-8: T 0.5 to 1 tie; k=64 holdout 0.960 at T 0.5/0.8; T 0.1 worst at k=64 among T ≤ 1 (0.912) | TS:L39-41; TST:L6-11 |
| RL-efficiency recipe (507 → 590) | not measured at low k (no pass@1 for 590 in git) | dev (k=64) 680 → 792 | LOOPS:L86-88 |
| More RL rounds (198 seed 0, old harness, 4 → 12 rounds) | textbook pass@1 0.151 → 0.173 | textbook 18 → 20 of 72 (k=256); DEVLONG 110 → 121 (k=64); dev 680 → 716 | SPIKET:L25-26, L39-40; SPIKE:L41 |
| Proof-state interface | not reported ("no held-out or textbook numbers yet") | dev (k=64) +111 to +178 medians | CM:L441, L460 |
| Test-time loops | per-sample success on long dev (1-4 arm, 4 RL rounds) 13.4% → 16.8% (1 → 4 loops). At matched compute: 96.5 at 4 loops vs 92 at 2 loops (SPIKET column "solved at m", m at 198's compute) | dev k=64: +12 to +27 at 3× compute per sample. After 12 RL rounds the benefit is ~0 (118 at 1 loop vs 115 at 8) | SPIKE:L37, L41-42; LREAD:L49-50; SPIKET:L48, L51, L57 |
| Thoughts | before RL, valid share on RL targets ~4% at 0 thoughts → 10.5-12% at 8 | after RL, flat in thought count (spike); 701 +44 to +57 dev at 8 vs 0 | THO:L55-60; COCO:L64-65 |
| Retry-EI | attempt-2 success ≤ independent rate (9.9 vs 10.3% for `retry`) | dev at 64 attempts: all arms < `iid` 771 | RETRY:L65-72 |
| Test-time EI / TTRL on dev failures | Only budget-indexed cumulative coverage. At the smallest budget reported (1x pipeline time) EI 1,069 vs sample-more 1,002 vs TTRL 929 | 5x: 1,088 / 1,020 / 1,079. c004 s0: TTRL passes EI at ~150 min (single seed) | CM:L329-333, L379-383 |
| Bigger model / longer pretraining | not reported at low k | none at k=64 (dev) or k=256 (textbook) | BIG:L36-48 |

**Overall pattern** (my reading of his numbers)
- Inference-time verifier guidance (resampling, SWOR, SMC) is a low-k / fixed-budget improvement. It adds a little at large k.
- Leon's RL recipe is a large-k coverage improvement that **lowers** held-out pass@1 on the strong pretraining. Robbie says so himself: "Our metric is pass@64, which rewards that." (CM:L29-30)
- Most other claimed RL gains (RL-efficiency recipe, proof state, full pool, retry-EI) are reported only at k=64 on dev.

---

## 6. Suspicious items, inconsistencies, superseded numbers

1. **Run-198 baseline quoted as 680 and as 681, with seeds reordered.**
   - AP RESULTS row 198: "680/670/694 on seeds 0/1/2: mean 681.33". BIG:L38 matches ("680 / 670 / 694 \| 681").
   - SPIKE:L35 gives "680 (seeds 670, 680, 694)", which changes the order.
   - LOOPS:L87, RETRY:L74 and COCO:L41 use "680". COCO's 680 is apparently the seed-0 value (COCO:L60 "Run 198's final checkpoint").
   - The same 680 also appears for 186 ("3-seed metric 680", CP:L23; AP RESULTS row 186 "mean 680.3").
2. **The retry-EI headline answers "no to both", but one question compares against "the run 198 baseline"** (RETRY:L12-15).
   - The retry arms average 706 to 718 (RETRY:L69-71), above the 680 that RETRY:L74 gives for run 198.
   - "No" holds only against plain EI under the new harness (`iid` 771 / 590 792).
3. **The plain EI arm does not reproduce its own control.**
   - `iid` ("590 unchanged") averages 771 against 590's 792. RETRY:L127-128 marks this "Open … seed noise, or the 33 extra vocabulary tokens".
   - Same-arm, same-seed reruns differ enormously: `retry` s2 729 vs 486, `blank` s2 731 vs 260 (RETRY:L70, L105).
   - With outcomes this bimodal, single three-seed means are fragile.
4. **Single-seed claims.**
   - `resume_rl` 811 (RETRY:L129).
   - The c004 race "TTRL edges past EI" ("One seed", CM:L392). It also compares an H100 that was "CPU-bound" with an A40, and the EI job was "OOM-killed … after 127 minutes" (CM:L387-391).
   - The GRPO wall is 1 of 4 runs.
   - All of D20 (seed 0).
   - The temperature sweep ("One generator seed, one sampling seed", TS:L47).
   - The value head (seed 0).
5. **The GRPO-wall protocol cannot be determined from git.**
   - The long-RL experiment is not committed: no working folder, and WALL:L11 links to a missing note `.claude/notes/long-rl-what-models-learn.md`. `nd.py` points at `/Users/robbie/...` paths.
   - The GRPO / EI hyperparameters, compute, judge and dev scores are therefore unknown, except "dev 186" for EI v4 s1 (MD:L80).
   - The headline "15% → 97%" is **cumulative training-target coverage** of 1,805 spine-3 RL targets over ~180 rounds (f2 legend 1743/235/239/247), not an eval metric.
   - Minor drift between documents: "calls 84-102" (MD:L10) vs "calls 80-102" (MD:L95). The summary says the takeoff proofs "all go through depth 3" (WALL:L40), while MD:L95 says "99% reach depth 3".
   - WALL:L35 "Runs that start at depth 4" means close-runs with D_start = 4, not RL runs.
6. **Test-time training on the eval set, scored on the same "dev solved" axis.**
   - TTRL and targets-only EI train on the dev statements. They score "baseline + solved", where solved = "passes Lean ∧ nd_verify in any round", sampled at T 1.0 with the guided sampler (CM:L309-311, L400; RE `ttrl/scale.py`:L2-3; `ttrl.py`:L7).
   - That is cumulative coverage under adaptation. It is not comparable with the 64-sample, T 0.8, plain dev metric, even though both are reported as "dev theorems solved (of 1,108)".
   - It also contradicts his own rule a day earlier: "test-time training on evaluation theorems is ruled out (Robbie, 2026-09-29)" (TTS:L209-210, L307-308). Later caveats justify using dev ("held-out is untouched", CM:L397-398).
7. **Mixed denominators in one sentence.** "At 1x, EI solves 81% of the failures … At 5x it reaches 98.2%" (CM:L335-336).
   - 81% is a share of the ~204 failures.
   - 98.2% is 1,088/1,108 of the whole dev set. As a share of failures, 5x is about 90%.
8. **Cross-judge and cross-statistic comparisons.**
   - "Plain RL in the proof state nearly matches Leon's RL: 198 goes 669 → 824; the combined model gets 904" (CM:L448-449).
   - 669 and 824 are medians judged by **Lean alone** (CM:L461). 904 is a mean judged by Lean ∧ nd_verify, on a different recipe (186).
   - Robbie reports the judge gap as small ("+0 to +7 accepts", state README L30; and "agree on more than 99.9%" between nd_verify and Lean, CM:L494-495).
   - Within the proof-state table the C0 arm was rerun on the same fork, so that table is internally consistent.
9. **Budget overruns and protocol changes inside "best" numbers.**
   - c004 (905) ran over the 2,400 s budget with `ND_TOTAL_SECS=3600` for all runs (CP:L53-54, L65-66).
   - The bigger-model runs changed three harness constants in "an uncommitted local copy, so this is off-protocol" (BIG:L18-19).
   - The temperature check script "isn't committed" (BIG:L31-32).
10. **Dev selection bias, and holdout never scored for the new-harness models.**
    - The 186/198 recipes were hill-climbed on this dev metric over ~200 runs (SPIKE:L57; CM:L490-492).
    - 590's 792, and every loops/thoughts/retry number, is dev-only. The holdout was never scored (results.json L2208 `"holdout_metric": null`; LOOPS:L102-103).
11. **The loops summary overstates what was kept.** "Every kept experiment was an RL-efficiency change" (LOOPS:L81), but 512 (alternating core pairs, an architecture change) was kept at 766 (LOOPS:L70). LREAD:L47-48 says the gains came "from RL efficiency … not from loops", which is compatible.
12. **Superseded best-looped number.** THO:L69 says the loops loop's "best looped model: 748". LOOPS:L69-70 has 764 (510) and 766 (512) as later keeps. Probably written before 510/512 landed.
13. **Two different "904"s.**
    - The combined pipeline's c005 (915/893/905 → 904.3) is used for test-time scaling and TTRL.
    - The factorial's fresh "best" cell (916/895/901 → 904.0) is what CM's pass@k table reports.
    - CM:L199-200 notes that c005 is a separate run (textbook 41.7% vs 44%).
14. **Blog vs repo draft.**
    - The published post is dated "September 29, 2026" but contains the TTRL-at-scale results computed 10-01/10-02, so it was edited after its date.
    - According to WebFetch it has **no** "On the best checkpoint: TTRL edges past EI" section, which the repo draft added on 10-06 (b85437a, CM:L372-392).
    - WT:L83 lists the post as "(draft, unlisted)" as of 10-01. The blog index lists no nd-rl post.
15. **Wording: Lean-verified vs Lean ∧ nd_verify.** LOOPS:L38-39 says the oracle returns "only Lean-verified attempts", while the harness it describes returns "the ones Lean AND nd_verify accept" (AL harness L20).
16. **The "pass@1" for resampling is not one plain sample.** It is one resampled attempt (336 vs 218 tokens per attempt, scaling.csv L9 vs L2) and costs 1.5× wall-clock with the KV implementation. Robbie does give token-matched comparisons (TTS:L88-97), so the claim survives at matched tokens.
17. **The temperature sweep is on someone else's model and pools.**
    - Model: Dan's r16 proof-state prover. Pools: Dmitry's, from Dan's `data/bs/` files. Judge: Lean alone.
    - It says nothing direct about Robbie's whole-proof models at T 0.8. The suggested follow-up, a temperature sweep for resampling, "Temperature sweep for resample. The RL sampler used T 1.0; the eval uses 0.8" (TTS:L304), was not run.
18. **No raw artifacts in git for most rows.**
    - Retry-EI ("not committed"), GRPO wall (`ckpt/`, `runs/` not committed), TTRL, the test-time-scaling raw outputs, and the loops pass@k pages (private claude.ai artifacts) cannot be re-derived from git.
    - The factorial pass@k (`passk.csv`) and the test-time-scaling / textbook CSVs are aggregates or per-problem counts that do reproduce his tables (see Rev. R/X above).

### Checkpoints (what is said; nothing downloaded)

- WT:L21 calls `robbiethompson2018/nd-rl-checkpoints` the store for "Autoresearch runs uploaded by `pod.py`, one directory per seed: `pretrain.pt`, `rl_round_0N.pt`, `final.pt` (includes RL), `summary.json`, `source/pretrain.py`".
- RE `code/experiments/current/autoresearch/README.md`:L59 says "The public checkpoint repository is".
- Run 198: `runs/198-claude_lean-muon-no-rms-retest_s0/` (also `_s1`, `_s2`), "Score 681 on the autoresearch harness" (WT:L47; PR README L91-93).
- Bigger-model arms: `runs/<arm>_s<k>` (BIG:L28).
- Looped spike: `runs/looped-spike-20261006_*` (SPIKE:L68-69; the 12-round runs have `rl_round_01`-`08` = rounds 5-12).
- Loops loop: `runs/5xx-*` (LOOPS:L44-45). Thoughts loop: `runs/<id>_s<seed>` (THO:L37).
- Long-RL GRPO/EI pretrain/final checkpoints, plus v4 trajectories every 5 rounds (WALL:L17-18; MD:L34, L41).
- **Not on HF:**
  - The combined-pipeline c001-c005 checkpoints: "on local disk … not yet on HF" (CP:L73-74). The TTS cites `runs/combo-c005_s{0,1,2}/final.pt` without saying where (TTS:L32).
  - Retry-EI: "Checkpoints were not kept" (RETRY:L59).
  - Coconut spike outputs "have not been uploaded to Hugging Face" (COCO:L93-94).
  - Temperature-sweep pools "not uploaded" (TS:L53).
- There is also a private dataset `ndrl/nd-rl-autoresearch` (WT:L22).

### Judges used, by experiment (code cites)

| experiment | judge | cite |
|---|---|---|
| frozen pretraining-loop harness (dev metric, RLF) | Lean AND nd_verify | AP harness L12-14 |
| loops / thoughts / retry-EI harnesses (RLL, oracle and eval) | Lean AND nd_verify | AL harness L20; RH:L29-31, L208; AL `remote.sh`:L16-17; RETRY:L39-40 |
| test-time scaling engine | Lean AND nd_verify (`gate(...)` then `verify_text(...)`) | RE `test_time_scaling/engine.py`:L13, L212, L228-230 |
| TTRL / test-time EI | Lean ∧ nd_verify ("in any round") | CM:L310-311; `ttrl.py` imports `nd_verify.verify_text` (L39) |
| factorial | Lean ∧ nd_verify for lean_seq; **nd_verify alone** for the abs format | FACT:L22-23; CM:L494-495 |
| proof-state recipes | **Lean alone** (dan_best-state a005ad61) | state README L28-30; `harness_state.py`:L411 |
| temperature sweep | **Lean** via Dan's `lean_judge.judge_many` (DM's vendored copy: "Lean alone decides") | TS sweep_remote L6; DM `collect_pools.py`:L96-105; DM `lean_judge.py`:L2-5 |
| GRPO-wall free generation | "Lean-judged" (harness not committed) | `gen_check.py`:L3 |
| shared `lean_seq` code (advice) | "Judge with Lean, not with an ND verifier" | PR `code/shared_code/README.md`:L37 |
