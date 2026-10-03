# Review — mcts-a (PUCT search with a learned value vs sampling, Phases 0 + A)

Reviewer: agent:claude (reviewer role), a separate session from the executor. Started 2026-10-03 05:28 UTC.
Scripts and outputs: `review/mcts-a-recount/` (`r1_counts.py` … `r5_compute_boot.py`, with `*.json` / `*.log`). The
Lean driver `rlean.py` is reviewer-owned (copied from `origin/dan_compute-match:review/compute-match-recount/rlean.py`).
It has its own ND → Lean translator and does not import `nd2lean`, `lean_tok` or `lean_check`. Everything else was
written for this review.

**Model labels.** Every number below is on `trajectory`'s cap-12 models: `best_model.ALiBiGPT` 6 × 384,
9,560,832 parameters, `lean_staten` format, trained from scratch on K12 (155,000 generator proofs, cap 12).
- **pend** = `stage1_best12_s{S}_b1200.pt` (end of pretraining).
- **r8** = `la_T1_best12_s{S}_r8.pt` (T1 ladder after 8 EI rounds on `rl_targets`).

Both are frozen throughout. All read-outs ran on NVIDIA A40s. Every proof count is under **Lean alone** (Lean 4 core,
the 2026-09-27 judge). No pre-2026-09-27 number is compared here.

**Disclosure — phase-1 blindness was partial.** Three leaks reached me before I counted anything:
- The session's start-up context showed the branch's recent commit subjects. They include
  `MCTS-A GATE: FAIL (group C r8, value vs sample 2/4, 2/2, 3/4)` and the `DONE` subject.
- `preregistration/mcts-a.md` Addendum 2 (04:35 UTC) states the same gate numbers.
- From Addendum 1 I also knew the first tuning number (105 / 184).

I did not open `analysis.md`, `summary.json`, `log.md`, `termsize.json` or any `STATUS*` file in phase 1. All counts
below come from the per-job `eval/*.jsonl` / `*.json` files and the raw logs.

## §Recount (phase 1, blind to the write-ups)

### Hard constraints
- `nd_verify/`: tree hash identical on `HEAD`, `origin/dan` and `origin/main` (`1696a7f6…`). Nothing in the search,
  value or eval path calls it: `lean_gate.py` says it no longer calls `nd_verify`, and `grep` finds no call in
  `mcts*.py`, `value_head.py` or `state_eval.py`. Every proof here is judged by `lean_gate.gate` on the literal text.
- `artifacts/TEST_RUN_DONE`: no commit on this branch touches it (`git log origin/dan..HEAD -- artifacts/TEST_RUN_DONE`
  is empty). `test_run_once.sh` was not run (no log).
- **No evaluation file in training code.**
  - `mcts_value_data.py` reads only `--targets data/ladder/rl_targets.jsonl` and `--gen data/kh/train_k12.jsonl`
    (`pod/mcts/value.sh`). It asserts no name starts with `textbook_` / `h250` / `holdout` / `transfer` / `tb72`.
  - `mcts_value_train.py` reads only the vdata files.
  - The policy is never trained.
- Tuning used `tune200` (184 theorems). All 184 are `rl_targets` theorems held out by md5(name) % 10 == 0 with
  L_true ≥ 9, and they are *all* such theorems (184/184). It ran on s0 pend only.
- **Splits, by renaming class** (premise order free, all 24 atom permutations): there is **0** overlap between
  `rl_targets` (4,495) or `tune200` (184) and any of textbook72, holdout250, rrQ100, long2 or group C s0/s1/s2.
  - All of K12 train (155,000, a superset of the 1,500 value-data theorems) overlaps **1** textbook72 theorem.
    That theorem is in none of the group C sets. It is inherited from `trajectory`'s pretraining set, not introduced
    by this run.
- No hard-constraint violation. No quarantine.

### Group C and the pools
- **Group C rebuilt from `trajectory`'s per-theorem k 256 files** (bucket `trajectory/artifacts/tj/eval/`,
  `x0` = sample seed 0): tb72 ∪ h250 theorems unsolved by both pend and r8. My sets equal `data/mcts/groupC_s{0,1,2}`
  exactly (36 / 35 / 28; tb72 24/22/17, h250 12/13/11).
- `trajectory`'s seed-1 (`x1`) r8 counts on those sets are **3 / 1 / 1**, as the pre-registration says.
- `data/mcts/tb72` and `h250` equal `trajectory`'s inputs, by prompt.
- `rrQ100` ⊂ `transfer_long_rr600` L_true 13–16 (400): 100/100 in band. It is reproduced exactly by
  `random.Random(20261002).sample(band, 100)`.

### Solved per arm, pool, checkpoint, seed (`r1_counts.json`)
How these were counted:
- **Sample** = `state_eval.py` k 256, T 0.8, sample seed 2, batch 2,048, max_action 512, max_steps 96. A theorem counts
  if ≥ 1 of its 256 attempts is Lean-accepted.
- **prior / value** = PUCT on the tuned configs: prior K 2 / T 1.0, value K 8 / T 1.5, both max_action 256. Each
  search's wall budget is its own sampling job's `wall_s` (79/79 search jobs, exact).
- In every job the per-theorem jsonl count equals the per-job json's `solved`. No sampling row has
  solved ≠ (n_ok > 0), and every solved search row carries a literal text.

| ckpt | pool | seed | sample | prior | value |
|---|---|---|---|---|---|
| r8 | C | s0 | 4 | 2 | 2 |
| r8 | C | s1 | 2 | 1 | 2 |
| r8 | C | s2 | 4 | 3 | 3 |
| r8 | tb72 | s0 | 49 | 44 | 47 |
| r8 | tb72 | s1 | 50 | 44 | 49 |
| r8 | tb72 | s2 | 55 | 54 | 57 |
| r8 | h250 | s0 | 239 | 239 | 240 |
| r8 | h250 | s1 | 236 | 236 | 239 |
| r8 | h250 | s2 | 239 | 240 | 240 |
| r8 | rrQ100 | s0 | 96 | 96 | 96 |
| r8 | rrQ100 | s1 | 93 | 94 | 96 |
| r8 | rrQ100 | s2 | 92 | 88 | 90 |
| r8 | long2 | s0 | 21 | 20 | 21 |
| r8 | long2 | s1 | 19 | 14 | 18 |
| r8 | long2 | s2 | 19 | 17 | 19 |
| pend | C | s0 | 0 | 0 | 0 |
| pend | C | s1 | 0 | 1 | 1 |
| pend | C | s2 | 0 | 0 | 1 |
| pend | tb72 | s0 | 32 | 29 | 35 |
| pend | tb72 | s1 | 32 | 34 | 37 |
| pend | tb72 | s2 | 36 | 34 | 37 |
| pend | h250 | s0 | 199 | 215 | 206 |
| pend | h250 | s1 | 207 | 212 | 216 |
| pend | h250 | s2 | 204 | 212 | 203 |
| pend | rrQ100 | s0 | 59 | 76 | 78 |
| pend | rrQ100 | s1 | 65 | 69 | 75 |
| pend | rrQ100 | s2 | 60 | 66 | 74 |
| pend | long2 | s0 | 8 | 9 | 12 |
| pend | long2 | s1 | 5 | 3 | 4 |
| pend | long2 | s2 | 4 | 5 | 6 |

### Gate (pre-registered: Δ_s = value − sample on group C at r8; PASS iff Δ_s ≥ 3 and Δ_s > |sample − trajectory seed-1| on ≥ 2 seeds)

| seed | sample (seed 2) | prior | value | Δ_s | trajectory seed-1 | spread | passes |
|---|---|---|---|---|---|---|---|
| s0 | 4 | 2 | 2 | −2 | 3 | 1 | no |
| s1 | 2 | 1 | 2 | 0 | 1 | 1 | no |
| s2 | 4 | 3 | 3 | −1 | 1 | 3 | no |

**MCTS-A GATE: FAIL**, recomputed. This is also the pre-registered **falsifier**: Δ ≤ 0 on 3 of 3 seeds.

Spread across seeds:
- value − sample: per seed −2 / 0 / −1, mean −1.0, IQM over seeds −1. Stratified (by seed) bootstrap over theorems,
  95 % interval of the per-seed mean: [−3.0, +1.33].
- prior − sample: −2 / −1 / −1, mean −1.33, interval [−3.67, +1.0].
- At pend, value − sample is 0 / +1 / +1 and prior − sample is 0 / +1 / 0.

**The arms solve different theorems.** At r8 on group C, the union of the three arms is 7 / 3 / 5 against sampling's
4 / 2 / 4.
- On s0, value and sampling share **no** theorem (value-only 2, sample-only 4).
- On s1 they share 1; on s2 they share 2.
- At these rates (≈ 0.1 per theorem) which theorems get solved is dominated by draw noise. The per-seed MDD in the
  pre-registration (≈ 6–7) is the right frame.

### Pre-registered expectations against the recount (misses are misses)

| expectation (prereg) | observed | |
|---|---|---|
| r8 group C sample 1–3 | 4 / 2 / 4 | above on s0, s2 |
| r8 group C prior 2–5 | 2 / 1 / 3 | s1 below |
| r8 group C value 4–8 (point 5) | 2 / 2 / 3 | **miss on all 3** |
| pend group C sample 0–1 / prior 0–2 / value 0–3 | 0,0,0 / 0,1,0 / 0,1,1 | hit |
| gate ≈ 45 % PASS, central +2 to +4 | FAIL, Δ −2 / 0 / −1 | miss |
| prior vs sample within ±2 on group C | −2 / −1 / −1 (r8), 0 / +1 / 0 (pend) | hit |
| tb72 r8 sample ≈ 48–54 | 49 / 50 / 55 | s2 above |
| tb72 r8 search within ±4 of sample | prior −5 / −6 / −1; value −2 / −1 / +2 | prior misses on s0, s1 |
| tb72 pend sample ≈ 32–38; value +0 to +6 | 32 / 32 / 36; value +3 / +5 / +1 | hit |
| h250 r8 sample ≈ 237–240; every arm ±3 | 239 / 236 / 239; prior 0 / 0 / +1, value +1 / +3 / +1 | s1 sample 1 below; arms hit |
| rrQ100 r8 every arm ±3 | prior 0 / +1 / −4; value 0 / +3 / −2 | prior s2 miss |
| long2 r8 every arm ±3 | prior −1 / −5 / −2; value 0 / −1 / 0 | prior s1 miss |
| rrQ100 pend value ≥ sample, gain 0–10 | +19 / +10 / +14 (prior +17 / +4 / +6) | direction hit; size **above** range on 2 seeds |
| long2 pend value ≥ sample | +4 / −1 / +2 | s1 miss |
| value AUC 0.80–0.92 (held-out) | pend 0.770 / 0.744 / 0.765; r8 0.816 / 0.791 / 0.794 | **miss on 5 of 6** |
| Brier below constant | 6 / 6 | hit |
| steps-to-go Spearman 0.6–0.85 | pend 0.783 / 0.762 / 0.825; r8 0.687 / 0.709 / 0.765 | hit |
| group-C hardest step at depth ≥ 2 in most solves | value 8/9, prior 6/7 | hit |
| hard step prior rank 2–8 | median 2 (value: rank 1 ×1, 2 ×6, 3 ×2) | hit (at the low edge) |
| GPU util: search 40–75 %, sampling 70–95 % | search prior 52.6 %, value 72.0 %; sampling 63.2 % (44–74) | sampling below range; value above sampling |

The AUC and Spearman figures are from the training script's held-out report. I **recomputed s0 pend and s0 r8 on CPU**
from the bucket vdata and head (own MLP rebuild, own AUC / Brier / Spearman, `r4_value_*.json`):
- AUC 0.7703 / 0.8161 and Brier 0.12167 / 0.05339 (constant 0.17133 / 0.07426) are identical.
- Spearman is 0.7823 / 0.6865 against the script's 0.7828 / 0.6871 (tie handling).
- The held-out flag equals md5(name) % 10 == 0 on all 5,995 theorems.

### Lean re-check (`r2_lean.json`)
- **Search arms:** every solved tree in every job, including tuning and x10, re-checked from its **stored literal
  `lean_seq` text**, wrapped as `theorem t (P Q R S : Prop) (h_i : prem_i) : goal := by <text>` with
  `#print axioms`. Results: prior **3,303 / 3,303**, value **3,376 / 3,376**, x10 value **21 / 21** accepted.
  - No forbidden tactic (`sorry`, `decide`, `simp`, `tauto`, `exact?`, `Classical.em`, …) appears in any text.
  - Axioms ⊆ {propext, Classical.choice, Quot.sound}.
- **Sampling arm:** `state_eval` stores the env's ND string, not the literal text. I took one random accepted proof per
  solved theorem per job, plus every proof on group C, through my own ND → Lean translator: **2,269 / 2,269**
  accepted (x10 **64 / 64**).
- **Negative controls:**
  - 300 stored `LEANREJ` fail examples through the same translator: **0 / 300** accepted.
  - 200 search texts with the goal replaced by `False`: **0 / 200** accepted.
- No counted proof is rejected. Note that 99 % of sampled proofs (97,704 counted) were not individually re-checked.
  The ≥ 100 per arm requirement is met on every arm.

### Proof length: pruned lines and term size (`r3.json`)
My own pruner keeps the lines reachable from the last line. Term size counts inference nodes of the pruned proof:
PR / AS 0, ORE 3, DN 3, others 1. Search arms contribute the one proof per solved tree; sampling contributes the
shortest by term size per solved theorem. Figures are pooled over seeds.

| ckpt/pool/arm | n solves | pruned lines (median) | term size (median / mean) |
|---|---|---|---|
| pend/C/prior | 1 | 8 | 6 / 6 |
| pend/C/value | 2 | 15.0 | 13.0 / 13 |
| pend/h250/prior | 639 | 9 | 6 / 6.97 |
| pend/h250/sample | 610 | 9.0 | 5.0 / 6.19 |
| pend/h250/value | 625 | 9 | 6 / 7.33 |
| pend/long2/prior | 17 | 20 | 17 / 16.35 |
| pend/long2/sample | 17 | 19 | 15 / 16 |
| pend/long2/value | 22 | 21.0 | 16.5 / 17.73 |
| pend/rrQ100/prior | 211 | 17 | 13 / 14.01 |
| pend/rrQ100/sample | 184 | 16.0 | 12.0 / 12.55 |
| pend/rrQ100/value | 227 | 18 | 14 / 15.29 |
| pend/tb72/prior | 97 | 7 | 5 / 5.82 |
| pend/tb72/sample | 100 | 7.0 | 4.0 / 5.37 |
| pend/tb72/value | 109 | 8 | 6 / 6.5 |
| r8/C/prior | 6 | 17.0 | 15.5 / 14.17 |
| r8/C/sample | 10 | 17.0 | 15.0 / 15.1 |
| r8/C/value | 7 | 15 | 12 / 12.57 |
| r8/h250/prior | 715 | 10 | 7 / 7.34 |
| r8/h250/sample | 714 | 9.0 | 5.5 / 6.23 |
| r8/h250/value | 719 | 9 | 6 / 7.14 |
| r8/long2/prior | 51 | 22 | 19 / 18.86 |
| r8/long2/sample | 59 | 19 | 15 / 15.44 |
| r8/long2/value | 58 | 21.0 | 18.0 / 18.05 |
| r8/rrQ100/prior | 278 | 18.0 | 14.0 / 15.19 |
| r8/rrQ100/sample | 281 | 16 | 12 / 12.67 |
| r8/rrQ100/value | 282 | 18.0 | 14.0 / 14.71 |
| r8/tb72/prior | 142 | 9.5 | 7.0 / 7.7 |
| r8/tb72/sample | 154 | 9.0 | 6.5 / 7.19 |
| r8/tb72/value | 153 | 10 | 7 / 7.93 |

Paired, on theorems both arms solve (search proof − sampling's shortest of up to 256):

| ckpt/pool/arm | n common | Δ term (mean) | Δ pruned lines (mean) | search longer |
|---|---|---|---|---|
| pend/h250/prior | 600 | +0.68 | +0.65 | 27% |
| pend/h250/value | 586 | +0.94 | +0.94 | 31% |
| pend/long2/prior | 12 | +0.33 | +0.5 | 50% |
| pend/long2/value | 15 | +0.2 | +0.13 | 47% |
| pend/rrQ100/prior | 169 | +1.16 | +1.15 | 46% |
| pend/rrQ100/value | 175 | +1.61 | +1.69 | 53% |
| pend/tb72/prior | 88 | +0.8 | +0.83 | 20% |
| pend/tb72/value | 93 | +0.9 | +0.97 | 23% |
| r8/C/prior | 2 | -2 | -2 | 0% |
| r8/C/value | 3 | -6.67 | -6.33 | 0% |
| r8/h250/prior | 713 | +1.12 | +1.15 | 35% |
| r8/h250/value | 714 | +0.86 | +0.88 | 30% |
| r8/long2/prior | 51 | +4.04 | +3.88 | 84% |
| r8/long2/value | 57 | +2.81 | +2.67 | 72% |
| r8/rrQ100/prior | 275 | +2.88 | +2.85 | 68% |
| r8/rrQ100/value | 276 | +2.32 | +2.29 | 64% |
| r8/tb72/prior | 139 | +1.2 | +1.21 | 33% |
| r8/tb72/value | 148 | +0.85 | +0.73 | 29% |

**Reading.** Searched proofs are not shorter. Against the shortest of sampling's (many) proofs they are 0.2–4 term
nodes longer on average, and longest on the long pools at r8: long2 +2.8 to +4.0, rrQ100 +2.3 to +2.9. That
comparison favours sampling, which picks a minimum over many proofs. The only group-C overlaps (r8, 2–3 theorems)
go the other way. They are too few to say anything.

### Search statistics (`r3.json` `hardstep`)
For each found proof, the hardest step is the step with the lowest prior.

| pool / arm | solves | hardest step depth ≥ 2 | depth (median) | prior rank (median) | its prior (median) | nodes per solved tree (median) |
|---|---|---|---|---|---|---|
| group C / value (both ckpts) | 9 | 8 | 3 | 2 | 0.069 | 63 |
| group C / prior | 7 | 6 | 4 | 2 | 0.102 | 109 |
| x10 group C / value | 21 | 15 | 2 | 3 | 0.045 | 961 |
| tb72 / value | 262 | 196 | 2.5 | 1 | 0.51 | 30 |
| rrQ100 / value | 509 | 507 | 4 | 2 | 0.35 | 112 |
| long2 / value | 80 | 80 | 4 | 2 | 0.29 | 189 |

On group C at r8 the search finished very few proofs.
- Summed over seeds: **6 (prior) and 7 (value) Lean checks** in 367 s per arm, all accepted.
- Sampling, in the same wall clock, sent up to 5,264 finished attempts to the gate.
- The trees mostly never reach a terminal state.

### Compute per arm (per-job files; `r5.json`)
How the columns were derived:
- Matching is on wall clock, as pre-registered, so GPU-seconds = wall clock per job.
- Search actions and tokens come from `stats.sampled` / `stats.gen_tokens`, which count real decoded tokens.
- Sampling actions are `env.rows` (= `stop_eos` + `truncated`). Sampling tokens ≈ `action_declen_mean` × rows
  (derived, since `state_eval` keeps no token total).
- Sampling Lean checks are bounded above by `env_end.done`; the gate de-duplicates.
- Figures are summed over 3 seeds.

| ckpt/pool | wall s (each arm) | sample actions / tokens | prior actions / tokens (× sample) | value actions / tokens (× sample) | Lean checks s / p / v |
|---|---|---|---|---|---|
| pend/C | 113 | 190,009 / 3,213,798 | 51,144 / 708,925 (×0.27 / ×0.22) | 209,064 / 2,343,390 (×1.10 / ×0.73) | ≤13,397 / 1 / 2 |
| pend/h250 | 1460 | 1,896,917 / 36,009,238 | 1,079,470 / 13,256,272 (×0.57 / ×0.37) | 1,773,328 / 19,297,702 (×0.93 / ×0.54) | ≤132,685 / 641 / 629 |
| pend/long2 | 166 | 243,396 / 4,369,664 | 75,976 / 1,080,652 (×0.31 / ×0.25) | 245,096 / 2,565,929 (×1.01 / ×0.59) | ≤6,274 / 17 / 22 |
| pend/rrQ100 | 888 | 1,086,921 / 20,624,341 | 478,714 / 7,505,330 (×0.44 / ×0.36) | 1,024,616 / 12,354,685 (×0.94 / ×0.60) | ≤34,692 / 212 / 229 |
| pend/tb72 | 269 | 472,705 / 6,597,566 | 204,254 / 2,450,457 (×0.43 / ×0.37) | 469,856 / 4,826,154 (×0.99 / ×0.73) | ≤39,176 / 97 / 109 |
| r8/C | 367 | 459,059 / 7,814,929 | 248,548 / 3,866,054 (×0.54 / ×0.49) | 466,880 / 5,810,518 (×1.02 / ×0.74) | ≤5,264 / 6 / 7 |
| r8/h250 | 2242 | 2,896,217 / 51,386,041 | 1,130,778 / 16,971,069 (×0.39 / ×0.33) | 2,163,968 / 25,832,162 (×0.75 / ×0.50) | ≤170,574 / 723 / 736 |
| r8/long2 | 255 | 365,872 / 6,067,145 | 92,306 / 1,259,968 (×0.25 / ×0.21) | 244,472 / 2,463,402 (×0.67 / ×0.41) | ≤8,697 / 51 / 59 |
| r8/rrQ100 | 1747 | 1,808,343 / 31,850,903 | 731,934 / 12,039,403 (×0.40 / ×0.38) | 1,538,736 / 19,822,494 (×0.85 / ×0.62) | ≤52,842 / 279 / 285 |
| r8/tb72 | 669 | 854,954 / 12,388,910 | 504,732 / 7,356,807 (×0.59 / ×0.59) | 944,280 / 9,823,970 (×1.10 / ×0.79) | ≤31,484 / 144 / 155 |
| x10 r8/C | 3605 | 4,629,210 / 78,743,285 | — | 3,634,808 / 40,622,573 (×0.79 / ×0.52) | ≤52,396 / — / 21 |

- No arm used more than 1.25× its comparator on wall clock: search / sample = 0.907–1.005. Each search's wall overran
  its budget by at most 0.84 %, because the budget is checked at the top of a round.
- One search stopped early because every tree was solved: s0 r8 long2 value, 21/21 at 0.72 of budget.
- On actions and tokens the search arms used **fewer** than sampling (0.21–1.10×), never more than 1.25×. So the
  search is the lower-throughput arm at matched time, not a bigger spender.
- Registry `gpu_seconds` rows equal the per-job wall clocks (96/96).
- Peak memory: search value 13.2 GB max, prior 6.3 GB. Sampling peak reserved 20.7 GB on the s0 r8 group C job.

### Tuning (s0 pend, tune200, 184 theorems)
- Sampling solved 140. Prior, configs t0–t7: 143 / 143 / 140 / 140 / **146** / 144 / 144 / 146 → t4 (K 2, T 1.0;
  ties go to the earlier config).
- Value, t0–t7: 142 / 146 / **151** / 145 / 150 / 146 / 145 / 147 → t2 (K 8, T 1.5). Both winners follow the
  pre-registered rule and equal `cfg_final.json`, and every read-out used them.
- **Addendum 1's motivating number is from an invalid run.** "K 8 / T 1.0 PUCT-prior 105 / 184" is the job in
  `artifacts/mcts/invalid_maxaction64/` (search `max_action` 64; 104 / 102 for t1 / value t0). At the pre-registered
  `max_action` 256 the same config solves **143 / 184, above sampling's 140**.
  - The extra configs (K 2 / 4) were added on the strength of a bug.
  - One of them (t4) became the prior arm's winner. The value arm's winner is a pre-registered config.
  - No evaluation pool was read before the change, so it is not a forking-path problem for the gate.

### Truncation (policy: raise `max_action` if > 0.1 % of a reported stratum is cut off)
- Sampling attempts ending `truncated` (an action longer than 512 tokens): mean 0.19 %, **above 0.1 % in 15 of 30
  read-out jobs**, max 0.67 % (s0 pend rrQ100). On group C at r8: 0.18 % / 0.48 % / 0.08 %.
- Search actions truncated at 256: prior mean 0.03 % (4 jobs > 0.1 %, max 0.27 %), value ≤ 0.03 %.
- This is `trajectory`'s protocol, held on purpose. Truncated actions at this length are almost certainly runaway
  decodes, so the effect on counts is likely nil. It is still a policy deviation to state.

### Exploratory 10× read-out (Addendum 2; not part of the gate)
Sampling k 2,560 (seed 3) against PUCT-value at that wall clock (1,279 / 1,507 / 819 s), r8, group C:

| seed | sample k 2,560 | value | value − sample | value-only theorems |
|---|---|---|---|---|
| s0 | 10 | 9 | −1 | 1 |
| s1 | 7 | 5 | −2 | 3 |
| s2 | 5 | 7 | +2 | 3 |

- Mean −0.33, bootstrap 95 % [−2.67, +2.0].
- Sampling at k 2,560 solves 2.5 / 3.5 / 1.25× its k 256 count. Addendum 2 expected ≈ 2× (6–9); s0 is above that
  and s2 below.
- Addendum 2 gave ≈ 25 % to "value ≥ 3 ahead on ≥ 2 seeds". Observed: 0 seeds.

### Duplicate s0 pend draw
`dup_s0_pend_mc0/` is a second copy of s0 pend group C (sample / prior / value) and tb72 sample. Its counts are
identical to the counted copies (0 / 0 / 0 and 32), with wall clocks within 1 s. Quarantining it changes nothing.

### Smaller findings from phase 1
1. **Value-head training data.**
   - At r8, 89 % of the value-data rollouts are accepted (85,799 / 95,920 on s0; 0.887–0.895 on all seeds).
     At pend it is 42–47 %.
   - The held-out calibration theorems are `rl_targets` that the r8 policy was trained on by EI.
   - So the r8 value is trained and calibrated almost entirely on states the policy already solves. Nothing in it
     resembles group C, where sampling's success rate is ≈ 0.05 %.
   - An AUC on held-out `rl_targets` says little about whether the value ranks partial proofs of group-C theorems.
2. **The per-theorem `gen_tokens` field is padded.** In the search jsonl it is `sampled × max_action`
   (`t.gen_tokens += len(ids)` on the padded row), not real tokens. The run-level `stats.gen_tokens` and the registry
   rows use real tokens.
3. **Missing checkpoint hashes.** Registry `ckpt_md5` is null for 5 of 6 checkpoints; only s0 pend is hashed. The
   `x10` logs print md5s for the r8 checkpoints and show they were fetched from
   `trajectory/ckpts/tj/ladder/` (`f9afd386…`, `c85481f9…`, `3b62784b…`).
4. **Same pod, not just same GPU class.** I could confirm only that every job ran on an A40. The per-job jsons carry no
   host for search jobs. That each (seed, checkpoint) read-out ran on one pod is the scripts' design (`read.sh` runs
   the three arms back to back), and I did not verify it per job.

## §Compare (phase 2: `run_mcts_a.md`, `numbers.md` § mcts-a, `log.md`, `STATUS.md`)

| claim (source) | my independent value | verdict |
|---|---|---|
| Gate: value vs sample on group C at r8 2 vs 4, 2 vs 2, 3 vs 4; Δ −2 / 0 / −1; **FAIL**, falsifier fires (all) | identical; group C and the seed-1 spread 3 / 1 / 1 rebuilt from `trajectory`'s files | reproduces |
| prior on C r8 2 / 1 / 3; union of the arms 7 / 3 / 5 (numbers, STATUS) | 2 / 1 / 3; 7 / 3 / 5 | reproduces |
| Both solved tables, r8 and pend, 5 pools × 3 arms × 3 seeds (numbers) | all 90 cells identical | reproduces |
| Paired r8 C value − sample −1.00 [−3.00, +1.33]; prior − sample −1.33 [−3.67, +1.00] (numbers) | identical (own bootstrap, stratified by seed) | reproduces |
| pend rrQ100 value − sample **+14.3** (CI +9.7 to +19.3), per seed +19 / +10 / +14 (run, numbers, STATUS) | +19 / +10 / +14, mean 14.33; I did not bootstrap this pool | reproduces (per seed; CI not re-derived) |
| "about 45 % of what 8 EI rounds add on this pool" (run) | r8 − pend sampling on rrQ100 = 37 / 28 / 32, mean 32.3; 14.3 / 32.3 = 44 % | reproduces |
| "still climbing" at pend rrQ100 (run; figure) | solves in the last 10 % of the budget: value 1 / 7 / 3 of 78 / 75 / 74 | reproduces weakly (flat on s0) |
| "At r8, PUCT + value is within ±2 of sampling on every pool" (run); "At r8, every pool is within ±2" (STATUS) | value − sample at r8: h250 +1 / **+3** / +1, rrQ100 0 / **+3** / −2. The STATUS wording, with no arm named, also covers prior: tb72 −5 / −6, long2 −5, rrQ100 −4 | **differs**: ±3 for value; false for prior |
| Value held-out AUC 0.74–0.82, Spearman 0.69–0.83, Brier below constant (run, numbers table) | table identical to the script reports; s0 pend and s0 r8 recomputed on CPU: AUC, Brier identical, Spearman within 0.0006 | reproduces. The **pre-registered 0.80–0.92 was missed on 5 of 6** heads: numbers gives the values, and `log.md`'s expectations list gives no AUC verdict (see below) |
| GPU util search 72 % against sampling's 63 % (run, numbers) | value 72.0 %, sampling 63.2 %, prior 52.6 % | reproduces; prior's 53 % is in numbers but not in run |
| 10×: value 9 / 5 / 7 against sampling k 2,560 10 / 7 / 5; value-only 1 / 3 / 3, sample-only 2 / 5 / 1; "stays level" | identical; mean −0.33, bootstrap [−2.67, +2.0] | reproduces |
| Compute: read-outs 6.8 GPU-h, equal per arm; tuning 7,922 s (17 × 466 s); value data 8,929 s; sample tokens 109.5 M / 70.8 M (r8 / pend) | sum of read-out walls 24,528 s = 6.81 h; per-arm walls equal within 1 %; 17 × 466 s matches; r8 sample tokens 109.6 M (my derivation) | reproduces |
| "Search arms used at most 1.0× their sampling budget; no arm above 1.25× its comparator" | wall 0.907–1.005×; actions and tokens 0.21–1.10× | reproduces |
| Sampling "Lean checks" 268,861 / 226,224 (numbers) | equal to `env_end.done` sums, i.e. finished attempts. That is an upper bound on Lean checks, since `lean_gate` de-duplicates and prefilters | label: these are finished attempts, not Lean calls |
| Peak memory "search ≤ 10.7 GB" (numbers) | read-outs ≤ 10.7 GB is consistent; tuning value_t0 11.3 GB, x10 s2 value **13.2 GB** | add "(read-outs)" |
| Truncation: sampling 0.22 %, "above the 0.1 % guidance", trajectory's protocol; search 0.015 % (numbers, run) | pooled 0.22 %; 15 of 30 sampling jobs above 0.1 %, max 0.67 % | reproduces; disclosed |
| "lean_check accepted 6,490 of 6,490 found proofs" (log) | Lean on the literal text accepted 6,700 / 6,700 search proofs (read-outs 4,361 + tuning + x10) and 2,333 / 2,333 sampled proofs, through my own translator. I did not re-run `lean_check` | consistent; not re-derived as stated |
| Proof length: search proofs longer than sampling's shortest (numbers table, run caveat) | same direction on every pool: +0.2 to +4.0 term nodes, largest on r8 long2 / rrQ100 | reproduces |
| Search statistics: hardest step = **lowest log π** (numbers) | the pre-registration defines it as the lowest **prior**. Under the prereg definition: group C value hard step depth ≥ 2 in 8/9 solves, rank median 2. With log π, the root (name-token entropy) wins on r8 rrQ100 (median depth 0), as numbers notes | definition deviates from prereg, unflagged; prereg expectation still holds under its own definition |
| Pre-registration before the first pod (STATUS, log) | commit `339d0876` 23:13:52, first pod 23:14:12; header says "~23:50" and log corrects it | reproduces |
| Addendum 1 before any evaluation read-out; its motivating 105 / 184 later found invalid (max_action 64) (log 00:31) | `invalid_maxaction64/`: 105 / 104 / 102; at 256, K 8 / T 1.0 prior = 143 > sampling 140 | disclosed in log. `run_mcts_a.md` says only "two bugs were fixed … grid widened". The **prior arm's winner (K 2) is one of the configs the bug motivated**; run does not say so |
| Duplicate s0 pend draw quarantined, used in no table (log) | the duplicate's counts equal the counted ones (0 / 0 / 0, 32) | reproduces; changes nothing |
| "Search pays where the frozen policy is unreliable over many steps, which EI already fixes" (run, "my reading") | pend gains are mixed. Value − sample: rrQ100 +14.3, tb72 +3.0, long2 +1.7, h250 +5.0 (−1 on s2). Value − prior on h250 is −4.67, so on that pool most of the gain is search without the value | a reading; supported on rrQ100 only. Should say the value adds +5.3 [+0.7, +10.0] over prior on rrQ100 |
| "A value trained on that policy's rollouts cannot point to them [group C's rare steps]" (run) | not measured. No value prediction on group-C states exists in the artefacts. Indirect support: r8 value data is 89 % accepted rollouts on theorems the policy was trained on | **not supported as stated**; reword as a hypothesis |
| Model labels (run, numbers, STATUS gate line) | every table and the gate line name the trajectory cap-12 checkpoints, size, format, from scratch, K12 | reproduces |
| md5 "checked against trajectory's" (numbers, log 23:31) | registry `ckpt_md5` null for 5 of 6 checkpoints; x10 logs print r8 md5s | consistent with the log; registry rows incomplete |

**Expectations written before the run; misses reported as misses?**
- The gate and group-C misses are reported as misses (log expectations list, run, STATUS).
- The AUC miss (5 of 6 below 0.80) is not called a miss anywhere: run and STATUS quote "0.74–0.82" without the
  prediction.
- The prior-arm misses on tb72 / long2 / rrQ100 at r8 (−5, −6, −5, −4 against ±4 / ±3) are visible in the tables
  but not named.
- The pend rrQ100 gain exceeded the predicted 0–10 range on 2 seeds, which is a miss in the favourable direction.
- Sampling GPU util (63 %) fell below the predicted 70–95 %.

## §Verdict

**Stands.**
- MCTS-A GATE: FAIL, and the falsifier. Every count reproduces from the per-theorem files.
- Group C is exactly `trajectory`'s, and the seed-1 spread is right.
- Matching on wall clock is honest (≤ 1 % overrun, same GPU class, and the search arms decoded fewer tokens).
- All 6,700 search proofs and a 2,333-proof sample of sampled proofs pass Lean 4 core from stored text. The negative
  controls fail.
- Splits are disjoint by renaming class. The hard constraints hold. Value calibration reproduces.
- The pend rrQ100 gain (+19 / +10 / +14, 3 of 3 seeds) and the 10× read-out's "level" result reproduce.
- The pre-registration preceded the first pod, and the bug that invalidated the first tuning runs is disclosed in
  `log.md`.

**Must be reworded.**
1. "At r8, PUCT + value is within ±2 of sampling on every pool" should be within ±3 (h250 and rrQ100 s1 are +3).
   STATUS's "every pool within ±2" also needs "PUCT + value": the prior arm is −4 to −6 on tb72 / long2 / rrQ100.
2. Value calibration: state that the pre-registered AUC 0.80–0.92 was missed on 5 of 6 heads. Say also that the
   held-out theorems are `rl_targets`, on which r8 was EI-trained, with 89 % of r8 rollouts accepted. This
   calibration does not speak to group-C states.
3. "A value trained on that policy's rollouts cannot point to them" is a hypothesis; nothing measured it.
4. Name what the value itself adds where search helps. On pend rrQ100, value − prior is +5.3 [+0.7, +10.0] of the
   +14.3; on pend h250 the value arm is *below* prior (−4.7).
5. `run_mcts_a.md` should say the prior arm's tuned config (K 2) came from the grid extension that a since-invalidated
   number motivated. The gate is unaffected: the value arm's config was pre-registered.
6. Smaller fixes:
   - Sampling "Lean checks" are finished attempts.
   - The search peak is 13.2 GB counting the x10 run.
   - "Hardest step" uses log π where the pre-registration said prior.

**Not supported.** Nothing the run claims as a finding. Only the causal reading in item 3 is unsupported.

**Next measurement.** The gate leaves one question open: is the value blind on group C, or is the budget too small?
1. **Score the r8 value heads on group-C states directly.** The x10 sampling read has 253k attempts with ≈ 21 accepted
   proofs across seeds. Take the states on its accepted and its failed attempts and report AUC (on-track vs
   off-track partial proofs) per seed.
   - AUC ≈ 0.5 confirms the executor's reading.
   - A clearly higher AUC points to the search, not the value, and would justify a value trained on group-C-like
     data, e.g. rollouts on the 10× read's states.
2. Any rerun of the gate needs more statistical power. At ≈ 0.1 solve probability per theorem the per-seed MDD is
   ≈ 6–7, and the arms' solved sets barely overlap. Use several independent draws per arm (or a hard pool of ≥ 150
   theorems) before calling a search-vs-sampling difference on group C.
