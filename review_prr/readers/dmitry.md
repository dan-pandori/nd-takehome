# Dmitry (chainik1125): RL and test-time-performance work since 2026-09-27

Reader notes for the independent reviewer, written 2026-10-17. Everything was read with `git -C ~/nd-rl` (`show`, `ls-tree`, `grep`, `log`, `diff`). I did not open any excluded path or ref. Each number carries a `ref:path:Lline` citation and a quoted fragment. "Re-derived" means I recomputed the number from committed per-theorem or per-generator data.

**Bottom line.**
- **Scope.** Since 2026-09-27, Dmitry's new work is:
  - a proposal dated 2026-10-05;
  - two parallel 10-hour sprints on 2026-10-06, each run by AI agents rather than by Dmitry directly:
    - Sprint A: a Claude Opus 5.5 team, branch `dmitry/selection-sprint`, merged into `dmitry/main`;
    - Sprint B: a Codex GPT-6.1 Sol team, on `dmitry/main`;
  - a transfer follow-up that never finished.
- **Common setup.** Both sprints measured Dan's `state_env_october_r16` checkpoint (9.56M parameters, proof-state interface), judged by Lean alone.
- **What they are.** Both are mainly test-time selection and stopping studies on a frozen generator.
- **The one RL piece.** Sprint B's joint REINFORCE training raised first-proof accuracy on its own synthetic distribution. Its learned retry/stop policy never beat simply returning its own first proof. It did not help on textbook72.
- **Where the gains are.** Every reported gain is to single-answer accuracy at small budgets. None raises large-k coverage.
- **Status.** Neither branch is merged into `origin/main`. The heavy Sprint B artifacts are not committed.

## Aliases used in citations

All paths are on `origin/dmitry/main` at af00a58 unless stated. The Sprint A files are identical on `origin/dmitry/selection-sprint` at a7cd488: `git diff a7cd488 af00a58 -- experiment-summaries/2026-10-06-proof-selection-sprint/ code/experiments/current/proof_selection_20261006/` is empty.

| alias | full ref:path |
|---|---|
| `PS` | `origin/dmitry/main:experiment-summaries/2026-10-06-proof-selection-sprint/summary.md` |
| `PSW/` | `origin/dmitry/main:code/experiments/current/proof_selection_20261006/` |
| `LCA` | `origin/dmitry/main:experiment-summaries/2026-10-06-learned-compute-allocation/summary.md` |
| `LCAS` | `origin/dmitry/main:experiment-summaries/2026-10-06-learned-compute-allocation/selection/summary.md` |
| `LCAA` | `origin/dmitry/main:experiment-summaries/2026-10-06-learned-compute-allocation/allocation/README.md` |
| `LCAE/` | `origin/dmitry/main:experiment-summaries/2026-10-06-learned-compute-allocation/` (committed figure data) |
| `LCAW/` | `origin/dmitry/main:code/experiments/current/learned_compute_allocation_20261006/` |
| `LCT` | `origin/dmitry/main:experiment-summaries/2026-10-06-learned-compute-transfer/summary.md` |
| `LCTW/` | `origin/dmitry/main:code/experiments/current/learned_compute_transfer_20261006/` |
| `PROP` | `origin/dmitry/main:proposals/learned-compute-allocation/README.md` |
| `CAP/` | `origin/dmitry/cap-comparison-textbook-eval-data:code/experiments/archived/cap_comparison_20260910/` |

## 1. Inventory of documents read (newest first)

| last commit (UTC) | document(s) | what it is | written_by |
|---|---|---|---|
| af00a58, 2026-10-06 20:41 | `LCT`, `LCTW/README.md`, `origin/dmitry/main:experiment-summaries/2026-10-06-learned-compute-transfer/live/README.md` | Transfer follow-up. The textbook72 rows are reused; the Charles evaluation is unfinished. | agent:codex |
| af00a58 | `LCA`, `LCAS`, `LCAA` | Sprint B reports | agent:codex |
| af00a58 | `LCAE/allocation/figures/main_live_results.csv`, `historical_live_results.csv`, `LCAE/figures/staged_main/metrics.json`, `LCAE/figures/causal_main/metrics.json.gz` | committed aggregates; per-theorem rows only for the causal test | agent:codex |
| af00a58 | `LCAW/`: `start.md`, `hypotheses.md`, `README.md`, `allocation/{main_method.md,audit.md,historical_method.md,train_live.py}`, `selection/{collect.py,data.py,main_data.py,test_collection_plan.md}`, `analysis/analyze_candidates.py` | Sprint B methods and code | agent:codex |
| af00a58 | `PROP` (written_on 2026-10-05) | proposal with three experiments | agent:codex |
| af00a58 | `code/experiments/current/proof-state/{results.md,run_v36.sh}` and the vendored `nd-takehome-dan/lean_judge.py` | older copy of Dan's code, plus an undated validation-36 table (context only) | none recorded |
| af00a58 | `docs/STATE.md:10`, `experiment-summaries/README.md:20` | index lines | – |
| a7cd488, 2026-10-06 20:27 | `PS` | Sprint A summary (text final at 05356a2, 07:20; a7cd488 only adds folder-map lines) | agent:claude |
| 821647b, 07:19 | `PSW/results/HEADLINE_SOURCES.md` | number-to-source map, built against e4421c4 | agent:claude (Worker B) |
| d6363f5, 07:17 | `PSW/reviews/04_final_delta.md`, `03_writeup_redteam.md` | Codex reviews of the write-up | agent:codex |
| 2026-10-06 | `PSW/results/`: `selection_*.json`, `B3/B4/B6/B7_*`, `phase4_within.json`, `splits.json`, `B2_allocation_by_bucket.txt`, `worker_A_phase3.md`, `worker_B_report.md`, `worker_B_phase2.md`; `PSW/code/`: `collect_pools.py`, `pool_lib.py`, `stopping.py`, `phase5.py`, `phase6.py`, `phase7.py` | Sprint A results and code | agent:claude |
| b3b8a58, 01:51 | `PSW/start.md`, `PSW/prior_pool_headroom.txt`, `PSW/research_log.md` | kickoff, headroom table from Dan's k=256 pools, log | agent:claude |
| 6e69a85, 2026-09-22 | `CAP/IMPORT.md`, `CAP/evaluation/textbook_{dev,train}.jsonl`, `CAP/prepare_data.py` | defines textbook dev58 / train14 (context; predates 09-27) | agent:claude (Sonnet 5) |
| 80659b2, 2026-09-27 | `origin/dmitry/proof-state` | no commits beyond `origin/main` (`git log origin/main..origin/dmitry/proof-state` is empty) | – |

Two further checks:
- `git log --all --since=2026-09-27 --author=chainik1125` lists only 315f362 (the 10-05 proposal) and the 10-06 sprint commits.
- `git merge-base --is-ancestor` shows that neither af00a58 nor a7cd488 is in `origin/main`.

## 2. What Dmitry tried; what worked; what did not

### 2.0 Framing

**Both sprints were run by AI agents.**
- Sprint A: `PS:L281-283` "Team: two Opus 5.5 workers (A: collector, pools, learned heads, trained judge; B: likelihood scorer, stopping, judge matrices) and a Codex reviewer".
- Sprint B: `LCA:L159` "with two GPT-6.1 Sol researchers and one GPT-6 Astra reviewer".

**Both execute the same proposal.**
- `PROP:L25-29` lists three experiments: "Select from eight rollouts", "Stop with an attempt cost", "Stop without an attempt cost".
- The reward in experiment 2 is `PROP:L155` "R_\lambda = V(x,y_{\mathrm{selected}})-\lambda(N-1)".

**Purpose.** The model, rather than Lean, should choose an attempt and decide when to stop. `PS:L59-61` "In the current pipeline that something is Lean. That is fine for measuring pass@k and no help for an RL loop that wants the model's own judgement as a reward, or for problems whose proofs cannot be checked."

### 2.1 Sprint A (Claude agents): select and stop on a frozen r16

**What is selected.** The candidates are k independent fresh-context attempts by the frozen generator r16-s0. A per-candidate scorer ranks them and selection keeps the argmax.
- `PS:L96` "A scorer maps an attempt to a number; selection keeps the argmax."
- `PSW/code/collect_pools.py:L15` "The k attempts of a theorem are flat indices t*k .. t*k+k-1 (independent fresh contexts)."

| tried | result | verdict | cite |
|---|---|---|---|
| Untrained own likelihood (mean masked per-token log-probability, finished attempts first) | k=8 recovers ~75% of the random-to-oracle gap | worked | `PS:L23-25` "recovers about three quarters of the gap, with no training" |
| Likelihood from the two sibling seeds as judge | better than self-judging; self-judging cell lowest in 5/6 rows | worked | `PS:L27-28`; `PS:L137` "Self-judging is the lowest cell in 5 of 6 rows" |
| Ancestor judges (r8, stage-1 of s0) | pre-registered prediction failed | did not | `PS:L156-157` "the pre-registered prediction that the ancestor would sit between self and siblings failed" |
| Scalar verifier heads: BCE, pairwise ranker, data ladder, sibling init | all at or below plain likelihood | did not | `PS:L38-39` "Three recipes that put a scalar head on the network instead ranked at or below untrained likelihood." |
| Likelihood judge trained pairwise (sibling s1, DPO-style; also a valid-only SFT variant) | within-theorem AUROC 0.893 / 0.942; k=8 selection ~93% of the gap | worked | `PS:L33-38` |
| Stopping rules: first-finished, count-of-finished, thresholds on own / sibling / trained-judge score, rank rules | trained-judge threshold closes about half of the count-to-oracle gap at mid budgets | partly worked | `PS:L41-48` |
| Difficulty-aware allocation; give-up rule | no gain at equal spend | did not | `PS:L237-238` "beats it on textbook72 only by spending five more attempts. All policies spend most on near-hopeless theorems, and a give-up rule loses on development data." |
| Budget control on textbook72 | thresholds overshoot their dev targets | did not | `PS:L264` "(a 4-attempt target spends 9.1)" |
| Not attempted: RL-trained stop action; listwise 8-proof context | – | out of scope | `PS:L67-69` "It did not train `ACCEPT`/`CONTINUE` actions by reinforcement learning, and it did not put eight proofs in one context" |

### 2.2 Sprint B (Codex agents): learned selection, stopping, joint RL

| tried | result | verdict | cite |
|---|---|---|---|
| Logistic score over ten public features (likelihood, entropy, length, syntax) | k=8 selection 87.50% (88.8% of the gap) | worked; strongest selector | `LCA:L13`; `LCA:L62` "The feature score recovers **88.8% of the gap**" |
| Neural selectors: pooled listwise chooser (8,192-token ALiBi context), per-proof marginal ranker, BCE critic, 385-parameter frozen head | all below the feature score | did not | `LCAS:L9` "fails the proposal's strongest-baseline criterion on the fresh 400-theorem test set" |
| Full BCE fine-tune as critic | destroys generation | harmful | `LCA:L77` "produces only 29/128 valid first proofs ... versus 93/128 from the original generator" |
| Threshold stopping on saved independent pools | 84.95% at 2.31 attempts; +2.98 pts over a dev-matched fixed mixture | worked, offline only | `LCA:L13` |
| Joint REINFORCE of generator plus stop/select heads, cost 0.03 or 0 | first-proof accuracy +12.6 pts; retry policy ≤ own first proof | the generator improved; allocation did not | `LCA:L15`; `LCA:L105` "That is a generator improvement." |
| Forced continuation (causal test) | one forced extra attempt lowers native correctness by 0.87 pts while availability rises | negative | `LCA:L17` |
| History-conditioned interface | collapses before adaptation (180/192 → 5/192 valid); later attempts still degrade after adaptation | major limitation | `LCA:L109` |
| Transfer to textbook72 | syntax-then-likelihood best (59.72%); thresholds overspend; joint models at or below first proof | weaker | `LCA:L131-133` |
| Not run: PPO, other cost values, 16 attempts | – | scope | `LCA:L141` "The sprint implements one policy-gradient update per episode batch, without repeated PPO epochs. Only costs 0 and 0.03 were trained." |

### 2.3 Transfer follow-up: unfinished

- `LCT:L4` "status: evaluation_in_progress".
- `LCT:L11` "Charles inference is in progress; no new Charles accuracy is reported yet."
- Its textbook72 table reuses Sprint B (`LCT:L11` "The textbook72 results below are complete and reused from the audited sprint.").

### 2.4 Context only

`code/experiments/current/proof-state/results.md:L1` "validation-36 (Lean 4.34.0 alone), greedy / pass@32 / pass@256 at T 0.8". This evaluates Dan's stage-1 and T1-round-8 state-env arms using older Dan code: `run_v36.sh:L8` "dan-pandori/nd-takehome @ add0a682 (dan_state-env)". It is undated, was committed in af00a58 as preexisting untracked work (`LCAW/start.md:L43` "Preexisting untracked directory: `code/experiments/current/proof-state/`"), and is not part of the RL / test-time work.

## 3. Headline numbers, one row per number as he reports it

**Model legend**
- **r16-s{0,1,2}** = Dan's `la_T1_best12_s{0,1,2}_r16.pt` (`state_env_october_r16`), from `hf://buckets/dan-pandori/nd-rl/rl-continue/ckpts/rc/ladder/`. It is Robbie's 9.56M ALiBi/NoPE recipe in Dan's proof-state interface, after 16 rounds of expert iteration. The model sees the Lean tactic state and writes one action; the environment applies it syntactically; Lean 4 judges the finished proof. Owner Dan; recipe Robbie.
  - `PS:L73-76` "Robbie's 9.56M ALiBi/NoPE recipe in Dan's proof-state interface (the model sees the Lean tactic state and writes one action; the environment applies it syntactically; Lean 4 judges the finished proof), after 16 rounds of expert iteration".
  - `LCAW/allocation/audit.md:L12` "It is ALiBiGPT, six layers of width 384, with the 111-token `lean_staten` tokenizer."
  - `LCAW/allocation/audit.md:L16-17` "It does not typecheck atomic proof terms; Lean verifies completed proofs."
  - Nominal context is 1,024 tokens: `PS:L68-69` "the checkpoint's context is 1,024 tokens".
- **Judge-A** (Sprint A) = Lean only, through Dan's `lean_judge.judge_many`.
- **Judge-B** (Sprint B) = Lean only, through `lean_gate.check_sources` on the literal Lean text. The RL reward is `lean_gate.lean_check`.
- Section 4.4 gives the code for both judges.

**Column notes**
- Sprint A selection rows: "n samples" is the pool size; m-subsets are drawn from it.
- "Reviewed?" first names the in-sprint agent review, then my own check.

### 3a. Sprint A (selection and stopping; holdout250 n=250, textbook72 n=72)

| # | value + metric (as reported) | eval set (n) | k | n samples / theorem | T | type | judge | model | compute / budget | seeds | reviewed? | citation + quote |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | 41% one-attempt validity; 69% pass@64 | textbook72 (72) | 1; 64 | 64 | 0.8 | plain sampling | Judge-A | r16-s0 | 512 tokens/action, 96 actions | generator s0, sampling seed 0 | Re-derived: 50/72 solvable = 0.694; m=1 mean 0.405 | `PS:L15` "proves 41% of the 72 textbook problems on one attempt and 69% if it may try 64 times" |
| A2 | 84% of attempts valid; pass@64 0.96 | holdout250 (250) | 1; 64 | 64 | 0.8 | plain sampling | Judge-A | r16-s0 | as A1 | as A1 | Re-derived: 240/250 solvable = 0.96 | `PS:L19` "holdout250 (250 theorems, 84% of attempts Lean-valid)"; `PS:L91` "pass@64 0.96" |
| A3 | k=8 selection by own likelihood: 0.918 [0.886, 0.946]; random 0.836; oracle 0.940 | holdout250 (250) | 8 | 64; 200 random 8-subsets | 0.8 sampling; likelihood at T=1 | selection, no training | Judge-A | r16-s0 generates and judges itself | 8 attempts plus one teacher-forced pass each | generator s0; paired theorem bootstrap B=1,000 | Codex midpoint audit recomputed phase 1 (`PS:L55`). Re-derived: 0.91752 / 0.93958 / 0.83574 | `PS:L24` "holdout250 0.836 (random attempt) → 0.918 (oracle 0.940)" |
| A4 | same as A3: 0.540 [0.441, 0.643]; random 0.405; oracle 0.594 | textbook72 (72) | 8 | as A3 | as A3 | as A3 | Judge-A | r16-s0 | as A3 | as A3 | Re-derived: 0.53979 / 0.59424 / 0.40545 | `PS:L24-25` "textbook72 0.405 → 0.540 (oracle 0.594)" |
| A5 | k=8, keep any finished attempt: 0.896 / 0.519 | both | 8 | as A3 | 0.8 | selection by environment flag | Judge-A | r16-s0 | 8 attempts | s0 | Re-derived: 0.89566 / 0.51944 | `PS:L124` "a finished attempt \| 0.896 \| 0.519" |
| A6 | k=8 selection by sibling likelihood: 0.928 / 0.567 | both | 8 | as A3 | 0.8 / 1 | selection, no training | Judge-A | generator r16-s0; judges r16-s1 and r16-s2 (mean) | 8 attempts plus 2 judge passes | s0 | Re-derived from the p3 files: 0.92766 / 0.56708 | `PS:L28` "raises the 8-attempt selection to 0.928 / 0.567" |
| A7 | k=8 selection by the pairwise-trained judge: 0.933 / 0.582, "about 93% of the gap" | both | 8 | as A3 | as A6 | selection with a trained judge | Judge-A | judge = r16-s1 fine-tuned pairwise on s0's training pools, 2 seeds averaged | 2 judge passes per candidate (`PS:L314`) | s0; judge seeds 0 and 1 | Codex final-delta re-parsed the phase-4 files. Re-derived: 0.9329 / 0.5818 | `PS:L37` "Eight-attempt selection with it reaches 0.933 / 0.582, about 93% of the gap" |
| A8 | Within-theorem AUROC: trained judge 0.893 / 0.942 vs plain s1 0.828 / 0.783 | both, theorems with both classes: 116 / 34 | – | 64 | 1 | ranking metric | Judge-A | as A7 | – | s0 pool | Re-derived from `PSW/results/phase4_within.json:L27,L153` | `PS:L202` "s1 trained pairwise \| **0.893** (+0.065 [0.036, 0.094] vs s1) \| **0.942** (+0.159 [0.088, 0.236])" |
| A9 | Self-judging penalty −0.029 [−0.048, −0.010] / −0.068 [−0.115, −0.019] (two-way fit, within-theorem AUROC) | both | – | 64 per generator | 1 | judge matrix, 3×3 | Judge-A | r16-s0/s1/s2 as generators and judges | – | 3 generator seeds | Traced in `PSW/results/HEADLINE_SOURCES.md:L45-46`; not re-derived | `PS:L29-30` "fitted self penalty −0.029 [−0.048, −0.010] and −0.068 [−0.115, −0.019]" |
| A10 | Scalar head, phase 1: within-theorem AUROC 0.646 / 0.596; k=8 accuracy 0.012 [0.001, 0.022] / 0.025 [0.010, 0.043] below own likelihood | both | 8 | 64 | – | selection with a learned head | Judge-A | r16-s0 plus scalar head, 3 seeds | input clipped at 1,024 tokens | 3 head seeds | Not re-derived | `PS:L166-168` "within-theorem AUROC among finished attempts 0.646 / 0.596; selected-proof accuracy at k=8 is below own-likelihood by 0.012 [0.001, 0.022] and 0.025 [0.010, 0.043]" |
| A11 | Stop at the first finished attempt: 0.892 at 1.6 attempts / 0.527 at 4.0 | both | ≤16 | first 16 of 64, 50 random orderings | 0.8 | stopping, no model judgement | Judge-A | r16-s0/s1/s2 (mean) | mean attempts 1.6 / 4.0; cap 16 | 3 generators | `PSW/results/B4_headline_table.md:L5` "0.892 [0.872-0.904] @ 1.59" | `PS:L220` "holdout250 0.892 at 1.6 attempts, textbook72 0.527 at 4.0" |
| A12 | Stop after the c-th finished attempt, siblings pick: 0.924 at 3.9 and 0.934 at 8.1 / 0.587 at 7.6; oracle pass@k 0.927 at 4, 0.943 at 8, 0.607 at 8 | both | ≤16 | as A11 | 0.8 | stopping + selection | Judge-A | as A11 | mean attempts | 3 generators | `HEADLINE_SOURCES.md:L130-131` | `PS:L222-223` "0.924 at 3.9 and 0.934 at 8.1 attempts on holdout250, 0.587 at 7.6 on textbook72, against oracle pass@k point estimates of 0.927 at 4, 0.943 at 8, and 0.607 at 8" |
| A13 | Oracle that stops at the first valid attempt: 0.953 at 2.0 / 0.653 at 7.2 | both | ≤16 | as A11 | 0.8 | oracle (Lean) | Judge-A | as A11 | cap 16 | 3 generators | B4 gives 0.952 @ 1.98 and 0.652 @ 7.18 (`B4_headline_table.md:L9,L16`) | `PS:L225` "reaches 0.953 at 2.0 attempts on holdout250 and 0.653 at 7.2 on textbook72" |
| A14 | Own-likelihood threshold: +0.012 [0.004, 0.021] at 4 attempts vs fixed-k with the same selector; spends 12 attempts on textbook72 when aiming at 4 | both | ≤16 | as A11 | 0.8 | stopping + selection | Judge-A | r16-s0 | dev-chosen τ | s0 | Not re-derived | `PS:L228-230` "adds +0.012 [0.004, 0.021] at 4 attempts on holdout250 over fixed-k with the same selector, but the same threshold spends 12 attempts on textbook72 when aiming at 4" |
| A15 | Trained-judge threshold: holdout250 0.935 @ 3.1 (target ≈4), 0.941 @ 6.4 (≈8); textbook72 0.630 @ 9.1 (≈4), 0.633 @ 12.0 (≈8) | both | ≤16 | as A11 | 0.8 | stopping + trained-judge selection | Judge-A | generators r16-s0/s1/s2; judge as A7 | τ chosen on the s0 dev split | 3 generators | Re-derived three-generator means from `PSW/results/B7_results.json:L1`: 0.9350 @ 3.119; 0.6303 @ 9.135; 0.9406 @ 6.446; 0.6327 @ 12.047 | `PS:L249` holdout250 m≈4 row "**0.935 @ 3.1**"; `PS:L251` textbook72 m≈4 row "**0.630 @ 9.1**" |
| A16 | At equal attempts, trained-judge threshold vs count-stop with siblings: +0.024 [0.017, 0.032] @ 2.3 attempts (holdout250); +0.035 [0.018, 0.056] @ 9.1 (textbook72); gap closed 50/53/44% and 55/60/54% | both | ≤16 | as A11 | 0.8 | as A15 | Judge-A | as A15 | count rule interpolated to the realised cost | 3 generators | Codex final-delta recomputed. Re-derived from `pooled_gens`: 0.0241, 0.0352; 0.501/0.534/0.443; 0.555/0.604/0.540 | `PS:L255-256` "adds +0.024 [0.017, 0.032] over count-stop with sibling selection on holdout250 at 2.3 attempts and +0.035 [0.018, 0.056] on textbook72 at 9.1" |
| A17 | Second sampling draw moves accuracy numbers by 0.001–0.004 / 0.001–0.028 | both | 8, 64 | 64 (draw 2 uses seed 100) | 0.8 | robustness check | Judge-A | r16-s0 | – | sampling seeds 0 and 100 | `PSW/results/B6_draw_compare.txt:L19` "pass64 draw1 0.694 draw2 0.667" | `PS:L300-301` "moves accuracy-type numbers by 0.001–0.004 on holdout250 and 0.001–0.028 on textbook72" |

### 3b. Sprint B (learned allocation) and the transfer follow-up

MAIN test = 400 theorems from two synthetic families (forward and two-leaf case elimination). Holdout is by atom-erased formula skeleton.

| # | value + metric (as reported) | eval set (n) | k | n samples / theorem | T | type | judge | model | compute / budget | seeds | reviewed? | citation + quote |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | Public-feature logistic selection 87.50%; random 71.59%; oracle availability 89.50% | MAIN test (400) | 8 | 8 | 0.8 | selection with a learned 10-feature logistic | Judge-B | r16-s0 generator; features include r16 likelihood replay | 256 tokens/action, 48 actions; plus replay | pool seed 91006 (`LCAW/selection/test_collection_plan.md:L23`); family-stratified bootstrap | Astra reconstruction (`LCA:L137`). Me: fixed-8 feature accuracy 0.875 and fixed-1 0.7159 match `LCAE/figures/staged_main/metrics.json:L1710,L1692`; per-item data not committed | `LCA:L13` "a logistic score over ten public statistics selects a valid proof on **87.5%** of theorems, versus **71.59%** for random selection; **89.5%** of pools contain a valid proof" |
| B2 | Neural selectors: pooled 81.67% (−5.83 [−7.75, −4.00]); marginal 86.13% (−1.38 [−2.46, −0.33]); BCE 84.79% (−2.71 [−4.42, −1.08]); frozen head 84.00% (−3.50 [−5.50, −1.75]) | MAIN test (400) | 8 | 8 | 0.8 | learned selection | Judge-B | full fine-tunes of r16-s0, plus a 385-parameter head on frozen r16-s0 | pooled chooser uses an 8,192-token context | 3 training seeds each (head: 1) | Astra; not re-derivable (artifacts not committed) | `LCA:L52-55` "Pooled neural chooser, three seeds \| 81.67% \| −5.83 [−7.75, −4.00]" |
| B3 | Threshold stopping (features) 84.95% at 2.31 expected attempts, 14,013 input tokens, +2.98 pts [1.76, 4.25] vs a dev-work-matched mixture; BCE 83.74% at 2.39, +3.09 [1.95, 4.32] | MAIN test (400) | ≤8 | 8 (saved pools) | 0.8 | offline stopping + selection | Judge-B | r16-s0 + feature model / BCE critic | cost 0.03 per extra attempt; work charged in logical input tokens | 3 BCE seeds | Matches `staged_main/metrics.json:L1680` (0.849485), `L1799` (+0.029752), `L646` (0.837387), `L765` (+0.030918) | `LCA:L68` "Public features \| 84.95% \| 2.31 \| 14,013 \| +2.98 points [1.76, 4.25]" |
| B4 | Joint RL, cost-aware: returned 85.319% at 1.021 attempts vs own first proof 85.333%; loses 0.0139 pp [0.0107, 0.0170] | MAIN test (400) | ≤8 contextual | 2 saved paths | 0.8 | RL-trained generator + stop/select heads | Judge-B (reward and evaluation) | format adapter of r16-s0 + REINFORCE, 200 × 8 episodes | 2,617 vs 2,136 input tokens | RL seeds 101/102/103 | Matches `LCAE/allocation/figures/main_live_results.csv:L268` (0.85319), `L78` (0.85333), `L1446` (−0.000139) | `LCA:L15` "cost-aware training returns correct proofs **85.319%** of the time at **1.021 attempts**, versus **85.333%** from returning those same models' first proof" |
| B5 | Joint RL, correctness-only: 83.974% at 2.325 vs own first proof 84.333%; loses 0.3595 pts [0.3171, 0.4048] | as B4 | as B4 | as B4 | 0.8 | as B4 | Judge-B | as B4, cost 0 | 14,666 input tokens | as B4 | Matches `main_live_results.csv:L1199`, `L1009`, `L1237` (−0.0035949) | `LCA:L99` "correctness-only retry loses **0.3595 points [0.3171, 0.4048]**" |
| B6 | First-proof accuracy gain from training: +12.58 pts [9.96, 15.29] (cost) / +11.58 [9.21, 14.13] (no cost) over the format-only 72.75% | as B4 | 1 | 2 paths | 0.8 | RL generator improvement (pass@1) | Judge-B | as B4 | 1,600 training episodes per seed | 3 RL seeds; controls 1 seed | Matches `main_live_results.csv:L724` (0.7275) | `LCA:L105` "Training improves first-proof accuracy over the format-only starting point by **12.58 points [9.96, 15.29]** with cost and **11.58 [9.21, 14.13]** without. That is a generator improvement." |
| B7 | Forcing one extra attempt: native correctness −0.87 pts [−1.14, −0.60]; availability 87.11% → 89.11% | 64 MAIN test theorems | +1 forced attempt | 8 futures per state | 0.8 | causal intervention | Judge-B | 2 frozen correctness-only checkpoints | – | 2 checkpoints | Re-derived from the 64 per-theorem rows of `causal_main/metrics.json.gz` (`primary.per_theorem`): −0.00867; 0.87109 → 0.89111; 57/64 theorems negative | `LCA:L17` "raises oracle availability from **87.11% to 89.11%**, while lowering correctness ... by **0.87 points [0.60, 1.14]**" |
| B8 | textbook72, k=8: random 42.36%, oracle 62.5%, syntax-then-likelihood 59.72%, features 55.56%, pooled / marginal / BCE 52.78 / 48.15 / 54.63%, frozen head 56.94% | textbook72 (72 = 58 dev + 14 rl_train roles) | 8 | 8 | 0.8 | selection | Judge-B | r16-s0 and the selectors above | 256 / 48 caps (Dan uses 512 / 96) | 3 training seeds | Astra reviews; not re-derivable | `LCA:L131` "random selection scores 42.36% and oracle availability is 62.5%. **Syntax then likelihood has the highest point estimate at 59.72%**" |
| B9 | textbook72 thresholds: 55.15% at 4.80 attempts (features), 55.23% at 4.43 (BCE); about 11,024 / 6,327 more input tokens than the dev mixtures | textbook72 (72) | ≤8 | 8 | 0.8 | stopping | Judge-B | as B3 | cost 0.03 | – | not re-derivable | `LCA:L133` "use 4.80 and 4.43 attempts and reach 55.15% and 55.23% accuracy. They exceed their frozen development-work mixtures by roughly 11,024 and 6,327 input tokens" |
| B10 | textbook72 joint RL: cost 41.40%, correctness-only 40.95%, own first proof 41.44%, format-only 41.67% | textbook72 (72) | ≤8 contextual | 2 paths (seed 92006) | 0.8 | RL generator + controller | Judge-B | as B4 | – | 3 RL seeds | Matches `historical_live_results.csv:L268` (0.41403), `L1199` (0.40951), `L78` (0.41435), `L724` (0.41667) | `LCA:L133` "Joint cost-aware and correctness-only policies score 41.40% and 40.95%, below their respective first-proof accuracy of 41.44%; the format-only first-proof point estimate is 41.67%" |
| T1 | textbook72 own pass@1 / own oracle@8 / returned correct / mean attempts: original + pooled selector 42.36 / 62.50 / 52.78 / 8.00; fixed-four joint 40.97 / 42.36 / 40.80 / 4.00; cost 41.44 / 43.98 / 41.40 / 1.04; correctness-only 41.44 / 43.29 / 40.95 / 2.37 | textbook72 (72) | 8 | 8 iid (row 1); 2 contextual paths (rows 2–4) | 0.8 | mixed | Judge-B | rows use different generators | – | 3 seeds (fixed-four: 1) | Reused from Sprint B, not new | `LCT:L17` "Original generator + trained fixed-eight pooled selector \| 42.36% \| 62.50% \| 52.78% \| 8.00"; `LCT:L19` "Joint model with compute penalty \| 41.44% \| 43.98% \| 41.40% \| 1.04" |

## 4. Protocol details

### 4.1 Theorem sets and sizes

**Sprint A**
- Splits are theorem-level, unit "equivalence group (atom renaming + premise permutation)":
  - train: rl_targets 4,495 + dev1108 776 + rr600 420;
  - dev: dev1108 332 + rr600 180;
  - test: holdout250 250 + textbook72 72 (`PSW/results/splits.json:L6574-6586`).
- Key overlap is 0 for `rl_targets~textbook72` and `rl_targets~holdout250` (`splits.json:L10` "rl_targets~textbook72": 0).
- Files come from Dan's nd-takehome (`PSW/code/pool_lib.py:L17-23`, e.g. "'textbook72': 'data/bs/textbook72.jsonl'"). Attempts per theorem: `pool_lib.py:L24` "SET_K = {'rl_targets': 16, 'dev1108': 16, 'rr600': 32, 'holdout250': 64, 'textbook72': 64}". The total is 6,525 theorems (`PS:L17`).
- holdout250 is Dan's `data/bs/holdout250.jsonl`. Dmitry's material does not document what it is held out from beyond this overlap audit. The Codex red team also asked for its provenance (`PSW/reviews/03_writeup_redteam.md:L38`).

**Sprint B MAIN**
- `LCA:L27` "The main corpus contains 1,600 training, 320 development and 400 test theorems, balanced between forward-generated formulas and two-branch disjunction elimination."
- Families use generator seeds 61011 / 61012 (`LCAW/selection/main_data.py:L48`). The split is by skeleton hash: `main_data.py:L82` "split = "train" if bucket < 70 else "dev" if bucket < 85 else "test"".
- Exclusions cover the K12 pretraining records, the 4,495 EI targets and the benchmark theorems (`LCAS:L23` "Canonical matches to all 155,000 cap 12 pretraining records, 4,495 expert-iteration targets, and known public benchmark theorem metadata were excluded").

**Sprint B historical:** textbook72 (`LCAW/allocation/historical_method.md:L15-17`).

**Transfer follow-up:** `LCT:L30` "The new primary set contains 187 ordinary proof problems: 87 candidate_v0, 72 candidate_v1, 14 hand-proved, and 14 batch3". No results.

### 4.2 The textbook72 dev58 / train14 definition

**Files on `origin/dmitry/cap-comparison-textbook-eval-data` (my counts)**
- `CAP/evaluation/textbook_dev.jsonl`: 58 rows, all `"role": "textbook_dev"`, with `reference_lines` from 1 to 33.
- `CAP/evaluation/textbook_train.jsonl`: 14 rows. Row 1 is `"family":"textbook_train"`, `"role":"rl_train"`, `"sampling_bucket":"book"`, `"sampling_weight_rational":"1/280"`, `"source_dataset":"book_prompt_container"`.
- `CAP/IMPORT.md:L14-17`: "`evaluation/textbook_train.jsonl` (14 rows) is the `textbook_train`-family subset extracted from `data/rl_common.jsonl` (prompt-only, no proof label). Together with `textbook_dev.jsonl` these are two of the three slices of the `protected_textbook` split recorded in `data/manifest.json` (`train: 14`, `development: 58`, `old_final: 73`, `all145_excluded_from_supervision: true`)."
- The third slice (old_final, 73 rows) "could not be recovered" (`CAP/IMPORT.md:L18`).

**Training rule as implemented in Dmitry's September cap comparison.** The 14 train rows were RL prompts (prompt-only). The 58 dev rows were for evaluation. All 145 protected textbook problems were excluded from supervised training.
- `CAP/prepare_data.py:L215` "'book':[prompt_only(x,'rl_train','book_prompt_container') for x in raw['book_prompt_container'] if x.get('family')=='textbook_train']}".
- The "book" bucket is weighted 1/20 of the common RL mix: `L218` "common_rl=weighted(rb,{'short':Fraction(1,2),'long':Fraction(9,20),'book':Fraction(1,20)})".
- `L255` "'book_classes':14,'book_population':145,'book_labels_read_or_emitted':False,'prompt_only':True".
- `L263-264` "'protected_textbook':{'train':14,'development':58,'old_final':73,... 'all145_excluded_from_supervision':True".

**Link to Dan's textbook72**
- Dan's textbook72 file carries the same split: `LCAW/allocation/historical_method.md:L16-17` "72 rows with unchanged proof-state prompts, source roles `textbook_dev` (58) and `rl_train` (14)".
- `PSW/results/worker_A_phase3.md:L122` "Dan's `numbers.md` calls this the "dev58 + train14" split (Robbie's naming)".
- The 14 names listed at `worker_A_phase3.md:L125-127` are identical to the 14 names in `CAP/evaluation/textbook_train.jsonl` (my comparison).

**October use: all 72 are eval-only**
- `PSW/start.md:L54` "`data/bs/textbook72.jsonl` (**eval only, never tune**)".
- `PS:L91` "eval-only by group rule".
- `historical_method.md:L18` "All 72 were excluded from MAIN supervision."
- `historical_method.md:L25` "Do not tune on historical outcomes."

**Exposure of r16 to train14.** Sprint A withdrew its own claim that the 14 were RL targets: `PSW/research_log.md:L174-175` "The "14 of 72 textbook theorems were RL targets" note is withdrawn (it was the `rl_train` role label = Robbie's train14 naming)". Sprint B's audit: `historical_method.md:L10-13` "finds one known Stage-1 pretraining match, and zero matches in the 4,495 EI target rows and the actual 90,436-row r16 final training mix. The historical source's 14 `rl_train` roles therefore do not establish that those 14 problems trained this r16."

**Group rule.** Beyond these statements I found no written group rule on training on train14.

### 4.3 Estimators

**Sprint A, selection**
- `PS:L106-108` "For pool size m, 200 shared random m-subsets per theorem (sampled without replacement); accuracy of the selected proof, oracle pass@m on the same subsets, and the random expectation; paired theorem bootstrap (1,000–2,000 resamples) for every difference; unsolvable theorems stay in the denominator."
- At m=1 all selectors are identical: `PSW/results/worker_B_report.md:L162` "All selectors coincide at k = 1."
- m=64 is a single subset (the whole pool).

**Sprint A, stopping**
- Policies see only the first 16 of the 64 attempts, in 50 random orderings: `PSW/code/phase5.py:L4` "Policies (N_max 16; R = 50 seeded orderings of the first 16 attempts"; `PSW/code/phase7.py:L12` "K = 16; R = 50".
- So the "first-valid oracle" is pass@16 within those 16 attempts.
- Fixed-k comparator: `PSW/code/stopping.py:L22` "the random mixture of fixed-k at adjacent k with the same selector (linear interpolation in k)".
- Gap fraction, from `PSW/reviews/04_final_delta.md:L10`: "`(trained-threshold accuracy − matched count/sibling accuracy) / (first-valid oracle accuracy − matched count/sibling accuracy)`". The count comparator is interpolated at each generator's realised attempts, then averaged.

**Sprint B**
- `LCA:L39` "Intervals below are paired 95% theorem-bootstrap intervals, stratified by the declared families". The staged metrics use 5,000 bootstrap samples (`staged_main/metrics.json` signature).
- Staged policy: `LCA:L64` "stop when the current proof's learned confidence passes a development-selected threshold, otherwise continue up to eight ... The primary reward is correctness minus 0.03 per additional attempt."
- Joint policies: `LCA:L83` "Native evaluation integrates the learned categorical stop and index probabilities along saved generation paths."

### 4.4 Judge (code)

**Sprint A: Lean alone, through Dan's `judge_many`**
- `PSW/code/collect_pools.py:L99` "res = lean_judge.judge_many([(prompts[i], recs[i]['nd']) for i in idx]) if idx else []". The pool file is written before Lean runs (`L154` "# pool serialised before any Lean call").
- `PSW/start.md:L58` "Lean alone decides validity". Lean version: `PSW/research_log.md:L16` "Lean 4.34.0".
- `PS:L84-86` "Lean judging used Dan's `judge_many` path (ND-to-Lean translation plus Lean 4 core), which his documentation describes as equivalent to the sampler's literal-text gate; that equivalence was not rechecked here."
- The sprint used Dan's code at `4dcd0e4f`, which is not in nd-rl. The only `lean_judge.py` in nd-rl is an older vendored copy (`PSW/research_log.md:L15-16` "an older commit with a 3.2M model that cannot load r16"). In that copy:
  - `code/experiments/current/proof-state/nd-takehome-dan/lean_judge.py:L2-4` "Lean alone decides whether a proof counts (Dan, 2026-09-27). `nd_verify` judges nothing any more";
  - `L112` "srcs.append(nd2lean.translate(prompt, nd, require_all_pr=False))".
- I could not inspect the exact judge code used.

**Sprint B: Lean alone on the literal Lean text**
- `LCAW/selection/collect.py:L168` ""lean_text": tok.statement(r["prompt"]) + " " + tok.text(e.text)" and `L189` "flags, wall, cpu = check_sources([p["lean_text"] for p in finished])".
- RL reward: `LCAW/allocation/train_live.py:L264` "verdicts, lean_wall, lean_process = lean_check(pending)" and `L298` "ep["reward"] = float(ep["correct"]) - args.cost * (ep["attempts"] - 1)".
- `nd_verify` is used only to check the generator's reference proofs when building the data (`LCAW/selection/main_data.py:L89` "ok, why, _ = verify_text(row["prompt"] + " " + row["proof"])").
- Integrity check: `LCAS:L56` "direct Lean checking of all 3200 public rendered transcripts matches every private validity label".

Neither sprint judges model outputs with "Lean AND nd_verify".

### 4.5 Sampling, budgets, seeds

**Sprint A sampling**
- `PSW/code/collect_pools.py:L13` "Sampling settings are Dan's: T 0.8, max_action 512, max_steps 96, batch 2048, early='eos', compaction on".
- Draw 1 uses sampling seed 0; draw 2 uses seed 100 (`PSW/code/phase6.py:L2-3`).
- Generator seeds s0/s1/s2 are separately trained r16 checkpoints (`PS:L76-77`).
- Likelihood is scored at T=1 and checked at 0.8 (`PS:L101`).

**Sprint A judges and ancestors**
- Ancestor judges are `la_T1_best12_s0_r8.pt` and `stage1_best12_s0_b1200.pt` (`PSW/results/worker_B_phase4.md:L129-130`).
- Trained judge: from sibling s1, trained on s0's training pools, two variants with two seeds each, early-stopped on dev within-theorem AUROC (`PS:L189-195`). "One hyper-parameter setting per variant" (`PS:L213`).
- Budgets are reported as mean attempts (cap 16). Token costs appear only in a worker report: `PSW/results/worker_B_report.md:L231` "First-finished 504 generated / 3.2 k total tokens per theorem".

**Sprint B sampling**
- `LCA:L37` "Independent proofs use temperature 0.8, at most 256 tokens per action and 48 actions."
- Test pools: `LCAW/selection/test_collection_plan.md:L23` "--seed 91006 --k 8 --temperature 0.8 --batch 256 --max-action 256 --max-steps 48".
- Chooser context: `LCAS:L11` "The chooser therefore uses an explicit 8,192-token ALiBi extrapolation".

**Sprint B joint RL**
- `LCAW/allocation/main_method.md:L12-13` "Three independent RL seeds, 101/102/103, are paired across costs 0 and 0.03".
- `L16-19` "Each arm receives 200 updates of eight complete episodes from the 1600 MAIN training theorems ... AdamW without weight decay, with base learning rate 1e-5, head rate 1e-3".
- `L43-46` "at most 1,024 emitted tokens, 256 per action, and 48 actions. The declared context is 16,384 tokens".
- `LCAA:L53-54` "one on-policy REINFORCE update per batch, not PPO".
- Historical paths use seed 92006 (`historical_method.md:L22-23`).

**Work accounting:** in logical input tokens (`LCA:L73`, "Logical unpadded model-input counts are lower bounds, not elapsed time").

## 5. Low-k vs large-k

### 5.1 Selection (Sprint A)

The generator is frozen, so selection cannot change pass@1 (all selectors agree at m=1) or coverage (oracle pass@m). It only changes the single-answer accuracy at budget m. The values below are my recomputation from the `per_theorem` / `selection` blocks of `PSW/results/selection_{set}_s0_r16_k64_p4.json:L1` (single-line JSON; Worker A's 200 subsets; generator s0). The k=8 entries match `PS:L121-128`.

textbook72 (72):

| m | random (= pass@1) | finished | own likelihood | sibling likelihood | trained judge | oracle pass@m |
|---|---|---|---|---|---|---|
| 1 | 0.405 | 0.405 | 0.405 | 0.405 | 0.405 | 0.405 |
| 2 | 0.404 | 0.459 | 0.462 | 0.468 | 0.474 | 0.477 |
| 4 | 0.406 | 0.498 | 0.511 | 0.525 | 0.537 | 0.543 |
| 8 | 0.406 | 0.519 | 0.540 | 0.567 | 0.582 | 0.594 |
| 16 | 0.407 | 0.539 | 0.570 | 0.611 | 0.618 | 0.633 |
| 32 | 0.407 | 0.557 | 0.595 | 0.641 | 0.649 | 0.662 |
| 64 | 0.407 | 0.556 | 0.625 | 0.653 | 0.681 | 0.694 |

holdout250 (250):

| m | random (= pass@1) | finished | own likelihood | sibling likelihood | trained judge | oracle pass@m |
|---|---|---|---|---|---|---|
| 1 | 0.836 | 0.836 | 0.836 | 0.836 | 0.836 | 0.836 |
| 2 | 0.836 | 0.876 | 0.885 | 0.889 | 0.894 | 0.899 |
| 4 | 0.836 | 0.888 | 0.905 | 0.913 | 0.919 | 0.925 |
| 8 | 0.836 | 0.896 | 0.918 | 0.928 | 0.933 | 0.940 |
| 16 | 0.836 | 0.900 | 0.926 | 0.939 | 0.942 | 0.949 |
| 32 | 0.836 | 0.901 | 0.934 | 0.947 | 0.950 | 0.956 |
| 64 | 0.836 | 0.904 | 0.936 | 0.952 | 0.952 | 0.960 |

**Own and sibling likelihood**
- Zero effect at m=1. Coverage is untouched.
- The gain over pass@1 grows with m: own likelihood on textbook72 is +0.057 at m=2 and +0.220 at m=64.
- The shortfall from oracle also grows: own likelihood is 0.015 below oracle at m=2 and 0.069 below at m=64.

**Trained judge**
- It tracks pass@m at every m. The residual to oracle is 0.003 → 0.014 on textbook72 and 0.005 → 0.008 on holdout250.
- Its absolute gain over pass@1 is therefore largest at the largest m, but it is capped by an unchanged pass@m.

### 5.2 Stopping (Sprint A)

These are budgeted numbers: accuracy at a mean attempt count, with the 16-attempt cap. The upper bound is the first-valid oracle, i.e. pass@16 within the first 16 attempts (0.953 / 0.653), which no rule changes.

- **Lowest budget.** At the lowest dev target (m≈2) every model-side rule collapses to "stop at the first finished attempt", so there is no gain. `PSW/results/B7_table.md:L3` gives 0.889 @ 1.59 (c=1) in every column for holdout250; `L6` gives 0.527 @ 3.99 for textbook72.
- **Trained-judge threshold vs count-stop with siblings, holdout250, same attempts** (my read of `B7_results.json:L1` `holdout250|Tjp|m{3,4,8}.pooled_gens.vs_count_sib`): +0.024 [0.017, 0.032] @ 2.3, +0.021 [0.015, 0.029] @ 3.1, +0.010 [0.005, 0.016] @ 6.4.
- **Same, textbook72** (`textbook72|Tjp|m{3,4,8}`): +0.037 [0.017, 0.061] @ 7.9, +0.035 [0.018, 0.056] @ 9.1, +0.024 [0.009, 0.042] @ 12.0.
- **Pattern.** On holdout250 the gains peak at 2–3 attempts and shrink by 8. On textbook72, the dev "low-budget" targets correspond to 8–12 realised attempts.
- **Own-likelihood threshold.** Its gain also shrinks with budget: `PSW/results/worker_B_report.md:L199-200` "**0.919 @ 3.93**; vs fixed-same +0.012 [0.004, 0.021]" and "**0.925 @ 8.26**; vs fixed-same +0.007 [0.002, 0.012]".
- **Allocation across theorems.** Adaptive rules put most attempts on near-hopeless theorems and 1–2 on easy ones. `PSW/results/B2_allocation_by_bucket.txt:L3` "m=4 count att by bucket [13.6, 5.8, 4.5, 2.3, 2.0]". Buckets are per-theorem pass rate 0–0.05 / 0.05–0.25 / 0.25–0.5 / 0.5–0.9 / 0.9–1 (`PSW/results/worker_B_phase2.md:L207-208`).

### 5.3 Offline staged stopping (Sprint B, features)

Fixed-budget feature selection gives 0.716 / 0.804 / 0.850 / 0.875 at 1 / 2 / 4 / 8 attempts (`staged_main/metrics.json:L1692,L1698,L1704,L1710`, `feature.0.03.policies.fixed{1,2,4,8}`). Oracle@8 is 0.895 (`LCA:L56`). Gain over the token-matched mixture, by cost:

| cost | adaptive result | gain | cite |
|---|---|---|---|
| 0.1 | 0.830 @ 1.93 attempts | +0.021 [0.008, 0.034] | `metrics.json:L1888-1889,L2007` |
| 0.03 | 0.849 @ 2.31 | +0.030 [0.018, 0.043] | `L1680,L1799` |
| 0 | 0.875 @ 6.84 | +0.0045 [0.0027, 0.0064] | `L1264-1265,L1383` |

So the adaptive gain is at low and mid budgets. At the largest budget it reaches only fixed-8 accuracy with slightly fewer attempts.

### 5.4 Joint RL (Sprint B)

**MAIN test**
- RL raised low-k accuracy: first-proof 72.75% → 85.33% (`main_live_results.csv:L724,L78`).
- Coverage stayed about where the original generator's iid coverage was: `LCAA:L42-43` "Finite-path oracle availability reaches approximately 90% in both primary arms", vs the original's iid oracle@8 of 89.50% (`LCA:L56`).
- More attempts hurt the returned answer: forced 8-attempt native selection gives 60.05% (cost arm, `main_live_results.csv:L192`) and 71.05% (no-cost arm, `L1123`).

**textbook72**
- No first-proof gain: 41.44% vs format-only 41.67% (`historical_live_results.csv:L78,L724`).
- Contextual oracle@8 is 43.98% / 43.29%, against the original's iid oracle@8 of 62.50% (`LCT:L17,L19-20`).
- Forced 8-attempt native selection falls to 20.4% / 30.7% (`historical_live_results.csv:L192,L1123`).

### 5.5 Answer to (f)

Yes. Every improvement acts on single-answer accuracy at small or moderate budgets, and none raises large-k coverage:
- Selection and stopping use a frozen generator.
- The joint RL raised in-distribution pass@1 toward the existing pass@8 and did not transfer to textbook72.
- The trained judge makes model-selected accuracy at budget m track pass@m. Its absolute gain over pass@1 therefore grows with m, but stays bounded by an unchanged pass@m.

## 6. Suspicious items

1. **Sprint B's per-item data are not committed.**
   - `LCA:L178-182` link to `../../artifacts/learned_compute_allocation_20261006/...`. `git ls-tree -r origin/dmitry/main -- artifacts/` returns 0 files.
   - The selection and textbook72 numbers (B1, B2, B8, B9) therefore cannot be re-derived. Only the committed aggregates (CSV, `staged_main/metrics.json`) and the 64-theorem causal rows can be checked; they match.
   - `LCA:L184` "Large raw artifacts and checkpoints remain local and uncommitted."
2. **Sprint A's pre-registration logs and raw pools are not committed.**
   - `PS:L271` cites "`logs/worker_{A,B}.md` with every pre-registration and freeze"; no `logs/` path exists on either ref.
   - Pools and scores live only in `~/runs/proof-selection/` (`PS:L275-277`).
   - The freeze timestamps can be checked only against `research_log.md` and the reviews.
3. **The two sprints use different Lean judge paths, and the Sprint A code is not inspectable.**
   - Sprint A uses `judge_many` (ND→Lean translation with `require_all_pr=False`); its equivalence to the literal-text gate "was not rechecked here" (`PS:L86`).
   - Sprint B checks the literal Lean text.
   - The `4dcd0e4f` judge code is not in nd-rl. The vendored copy is older (`run_v36.sh:L8` "@ add0a682").
4. **The test sets were reused across seven phases.**
   - `PS:L52-53` "The two test sets were used across seven phases, so later questions were posed knowing earlier test results".
   - textbook72 labels were summarised at 02:07:36, one minute before the 02:08 freeze (`PS:L292-293`).
   - The trained judge's τ was chosen on the same dev split used for its early stopping (`PS:L312-314`).
   - Each variant had a single hyper-parameter setting (`PS:L213`).
5. **The stopping-gap denominator is a 16-attempt oracle.** "Oracle stops at the first valid proof" means pass@16 within the first 16 attempts, in 50 orderings (`phase5.py:L4`). It is not the pass@64 headroom quoted in the executive summary (0.96 / 0.69). The count-rule vs pass@k comparisons are "variable allocation versus fixed k; no equivalence test" (`PS:L223`).
6. **textbook72 "m≈4" is really about 9 attempts.** `PS:L264` "(a 4-attempt target spends 9.1)". The low-budget labels in the phase-7 table are dev targets, not realised costs.
7. **Small n and draw-dependence on textbook72.**
   - Within-theorem AUROC rests on 32–42 theorems (`B7_results.json:L1`: textbook72 n = 34 / 41 / 42 / 32).
   - The levels move by up to 0.08 between draws, and trained-minus-plain falls from 0.159 to 0.094 (`PS:L302-304`).
   - Generator spread at the same target is large: s1 0.597 vs s2 0.674 at textbook72 m≈4 (`PSW/results/B7_results.json:L1`, key `textbook72|Tjp|m4`).
8. **Mixed subset draws.**
   - Selection headlines use Worker A's subsets, while the seed-spread and "0.01–0.04 across generators" statements use Worker B's B3 draw, whose s0 values differ: textbook72 siblings 0.5729 and oracle 0.5976 (`PSW/results/B3_results.json:L804-806`) vs A's 0.567 / 0.594.
   - This was flagged by the red team (`PSW/reviews/03_writeup_redteam.md:L14` "mixed subset draws understate the sibling–oracle gap").
9. **Minor rounding and duplicate-estimate inconsistencies.**
   - First-valid oracle: 0.953 @ 2.0 (`PS:L225`) vs 0.952 @ 1.98 (`B4_headline_table.md:L9`) vs `HEADLINE_SOURCES.md:L132` "0.95192 at 1.9837".
   - textbook72: 0.653 vs 0.652 @ 7.18 (`B4_headline_table.md:L16`).
   - First-finished: 0.892 @ 1.59 (`B4_headline_table.md:L5`) vs 0.889 @ 1.59 (`B7_table.md:L3`) for the same rule under different simulations.
   - `HEADLINE_SOURCES.md:L1` "Built against commit e4421c4"; its flagged item F1 refers to superseded text.
10. **The index overstates the summary.**
    - `experiment-summaries/README.md:L20` "while scalar verifier heads never beat untrained likelihood".
    - The final summary softened this to "no scalar verifier head showed a resolved advantage over plain likelihood" (`PS:L34`) after `04_final_delta.md:L25` noted the likelihood-input head's textbook "+0.011 [−0.102,0.125]".
11. **The Sprint B MAIN distribution is narrow and partly trivial.**
    - `LCAS:L29` "finds unsatisfiable premises in 400/800 forward training theorems and 79/160 forward development theorems". The test split was not audited.
    - The holdout is by skeleton within the same two generator families (`LCAW/hypotheses.md:L21` "Formula-skeleton disjointness is not an unseen proof-program-family test").
    - The +12.6-point first-proof gain (B6) is therefore in-distribution.
12. **The Sprint B textbook72 protocol is not Dan's.** `LCAS:L68` "Our eight attempts, 256-token action cap and 48-action cap differ from the upstream historical 256-attempt, 512-token/96-action evaluation". Sprint A uses 512 / 96 (`collect_pools.py:L30`). Textbook72 numbers from the two sprints are therefore not directly comparable to each other, nor to Dan's pass@256.
13. **The comparator for "+2.98 pts" is matched on development work, not test work.**
    - `LCA:L75` "Test work differences are −783 tokens [−2,259, +763] for features ... Thus the comparison is neither exact test-work matching nor evidence of statistically established work reduction."
    - The attempt-matched comparison (+0.040 [0.027, 0.055], `staged_main/metrics.json:L1765`, `feature.0.03.comparisons.matched_attempts`) appears only in the JSON.
14. **Controls are single-seed and checkpoint ages differ.** `LCA:L105` "Controls use one seed, and development selects fixed-one at update 100 while the other RL checkpoints use 200." Sprint B used only generator r16-s0, with no generator-seed replication.
15. **The transfer summary is not a result.** `LCT:L4` "status: evaluation_in_progress". Its table mixes iid and contextual definitions: `LCT:L22` "Their oracle values are not the same pool as the first row's oracle."
16. **Nominal context exceeded.** Sprint B's chooser (8,192 tokens) and joint policies (16,384 tokens) run beyond r16's nominal 1,024-token context (`LCAS:L11`; `main_method.md:L44-45`). These are new, untrained-for interfaces; the history-interface collapse (`LCA:L109`) bounds the joint-RL result.
17. **No human review evident.**
    - Reviews are agent reviews (Codex for Sprint A, Astra for Sprint B).
    - Sprint A was "not pushed" at writing (`PS:L279`); it is now on origin but unmerged.
    - `docs/STATE.md:L10` advertises "87.5% selected accuracy against 89.5% oracle availability" from the unmerged branch.
