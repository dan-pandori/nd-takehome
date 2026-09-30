# Review: grpo-state (code phase)

Reviewer session, 2026-09-30. Phase 1 was blind: I worked from `~/review/grpo-state` (executor write-ups removed), the
run brief (`nd-rl/docs/proposals/state-env/BRIEF_grpo-state.md`), `preregistration/grpo-state.md`, the code and the raw
artefacts (`artifacts/grpo_state/*/{steps,found_*,round_*,alloc_*,args}`, `artifacts/grpo-state/registry/`). I did not
open `run_grpo_state.md`, `numbers.md`, `log.md` or `STATUS.md` before committing this section. I did read the
pre-registration addendum (it is part of `preregistration/grpo-state.md`), which carries the executor's smoke table, and
the executor's CI log (Actions run 36661730711) for the test results.

Reviewer scripts (own code): `review/grpo-state-recount/` — `recount.py` (own start-index normaliser, line and
term-size counters, step aggregates, found / round / alloc / registry cross-checks), `lean_rv.py` + `lean_recheck.py`
(Lean re-check; the translator is the state-env reviewer's own ND → Lean renderer, copied from `review_se/`, not executor
code), `flip_why.py` (control audit), `adv_check.py` (advantages vs brute force / paper transcription), `splits.py`
(renaming-class disjointness). Outputs are the `*.json` files next to them.

**Model for every number below:** SN-cap12 Stage-1 s0 (`ckpts/sc12/stage1_SN12_s0.pt`, `lean_staten`, 4 layers, d 256,
3,216,384 parameters, from scratch on `data/kh/train_k12.jsonl`) and the GRPO updates on top of it (≤ 8 updates, lr 3e-5).
Judge: Lean alone (the `lean_gate` literal-text gate, then `lean_judge.judge_many`). No `nd_verify` anywhere.

## §Recount (phase 1, before reading the write-up)

### What the run was
This was the code phase only: `grpo_state.py`, `grpo_adv.py` (4 advantage variants), CPU tests in CI, a GPU smoke, and
the pre-registration plus costing. So the pre-registration promises **no measured quantities from this session**. There
are no per-arm counts, frontiers, acquisition or base-reachability to re-derive. What can be re-derived is the smoke (the
addendum's table), the bookkeeping, the Lean status of every counted proof, the advantage definitions, the inherited
numbers the pre-registration relies on, the splits, and the costing arithmetic.

### Hard constraints
| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72…` on `HEAD` = `origin/main` |
| `nd_verify` unused as a judge | reward: `lean_gate.gate` (literal text) → `lean_judge.judge_many`; boundary evals: `eval_set.judge` → `lean_judge`. The only `nd_verify` import on the path is `state_env.py:38` `parse_formula` (a parser, pre-existing, not a verdict). No `nd_verify` in `grpo_state.py`, `grpo_adv.py`, `gs_compute.py`, `tests/test_grpo*.py`, `pod/gs/` |
| `artifacts/TEST_RUN_DONE` | unchanged since the run's base `d3abe474` (no commit touches it) |
| no evaluation file read in training code | training rollouts come only from `--targets` (`flat_t = targets[...]`). Transfer and held-out are only sampled at boundaries, with no update. No `targets/test*` or `validation_36` read in `grpo_state.py` / `grpo_adv.py` |
| shared code untouched | `git diff d3abe474 HEAD` touches only new files plus `ci/run_ci.sh` (+2 test steps), `QUESTIONS.md`, `STATUS.md`, `MANIFEST.jsonl` and the executor's own write-ups |
| budget before first pod | `podbudget grpo-state set 6 h / $3` at 02:10:04Z; first pod `gs-smoke` at 02:21:17Z |
| pods deleted | `gs-smoke` (RTX 3090, 0.229 h) and `gs-smoke2` (A40, 0.095 h) both logged in `podhours.log` at deletion. Total ≈ 0.32 pod-h, ≈ $0.16 by podhours |
| pre-registration before runs | `c21af4c9` (02:17:48Z) precedes the first pod (02:21Z). The addendum (`cdc43d8b`, 02:35Z; later paragraphs in `d42cb7d8` / `4eb500d3`) came after the smoke and says so |

No hard-constraint violation.

### Lean re-check of counted proofs
Per arm directory: 150 random target proofs from the last `found_<r>.jsonl`, plus every proof of the last
`found_transfer_<r>.jsonl` (only `smoke2_*` have boundary evals). Two renderings: my own ND → Lean term translator, and
`lean_tok`'s `lean_seq` rendering. Lean 4.34.1 core. The axiom set must be ⊆ {propext, Classical.choice, Quot.sound}.

| arm | checked (targets + transfer) | accepted, own translator | accepted, `lean_seq` | sorry / marker in text |
|---|---|---|---|---|
| smoke_default | 150 | 150 | 150 | 0 |
| smoke_unlikely | 150 | 150 | 150 | 0 |
| smoke_passk | 150 | 150 | 150 | 0 |
| smoke_distinct | 150 | 150 | 150 | 0 |
| conc_default | 150 | 150 | 150 | 0 |
| conc_passk | 150 | 150 | 150 | 0 |
| smoke2_default | 150 + 155 | 305 | 305 | 0 |
| smoke2_unlikely | 150 + 172 | 322 | 322 | 0 |
| **total** | **1,527** | **1,527** | **1,527** | 0 |

Controls (own translator): 200 / 200 prompt swaps rejected (199 distinct), 100 / 100 `sorry` bodies rejected (sorryAx),
169 / 200 single-rule flips (ORI1↔ORI2, ANDE1↔ANDE2) rejected. I audited the 31 flips that passed on a separate 400-flip
sample (`flip_why.json`): 346 / 346 asymmetric flips are rejected, and 54 / 54 passing flips are on symmetric formulas
(`A ∨ A`, `A ∧ A`), where the flip is still a valid proof. Lean ran and discriminates.

*Caveat (inherited convention, minor):* `found_*.jsonl` stores the environment's ND record (`proof`), not the literal
assembled `lean_staten` text the gate checked (`res_tx` is not written). The state ladder does the same. So "re-check
from the stored literal text" is not possible, and I re-checked the ND record rendered two ways. A future run that wants a
literal-text audit trail would need to store `res_tx` (or a `LEAN_GATE_DUMP`, as state-cap12 did).

### Smoke recount (from `steps.jsonl`, `alloc_*.json`, `found_*.jsonl`, registry)
s / update = mean of `sample_judge_s + update_s`. Tokens = mean `update_tokens`. All runs: SN-cap12 s0, 256 theorems × G
8, decode batch 2,048, T 0.8, lr 3e-5, `--no_eval` except smoke2.

| run (GPU) | updates | s / update (sample+Lean, update) | peak alloc GB | mean reward | groups with variance | groups A ≠ 0 | all-fail groups | update tokens |
|---|---|---|---|---|---|---|---|---|
| smoke_default (3090) | 8 | 18.64 (16.01, 2.63) | 8.60 | 0.4651 | 0.565 | 0.565 | 0.274 | 1.10 M |
| smoke_unlikely (3090) | 4 | 19.83 (17.01, 2.82) | 8.05 | 0.4617 | 0.591 | 0.591 | 0.261 | 1.18 M |
| smoke_passk (3090) | 4 | 19.17 (17.49, 1.67) | 8.15 | 0.4625 | 0.606 | 0.320 | 0.247 | 0.68 M |
| smoke_distinct (3090) | 4 | 20.68 (17.55, 3.12) | 8.09 | 0.4634 | 0.601 | 0.664 | 0.254 | 1.29 M |
| conc_default (3090, 2 jobs, seed 1) | 6 | 26.51 (22.20, 4.31) | 8.92 | 0.4563 | 0.573 | 0.573 | 0.277 | 1.12 M |
| conc_passk (3090, 2 jobs, seed 1) | 6 | 26.37 (23.25, 3.12) | 8.62 | 0.4414 | 0.608 | 0.311 | 0.272 | 0.66 M |
| smoke2_default, KL 0.02 (**A40**), 64 targets | 2 | 24.81 (16.54, 8.27) | 7.73 | 0.3042 | 0.559 | 0.559 | 0.389 | 2.20 M |
| smoke2_unlikely (**A40**), 64 targets | 2 | 19.43 (16.14, 3.30) | 7.74 | 0.3047 | 0.553 | 0.553 | 0.398 | 1.21 M |

Every row of the addendum's smoke table reproduces to its printed precision: s / update, split, peak, reward, variance
fraction, A ≠ 0, the 1.47× two-jobs figure (2 × 19.5 / 26.5), and ≈ 1.1 M / ≈ 0.65 M tokens per update. The smoke2 runs
were on an **A40**, not the 3090 the addendum names for "the smoke"; the addendum's table does not include them.
Step 1's mean reward is 0.4702 in all four seed-0 smoke arms (same seed, same model, before any update), as it should be.

Bookkeeping, every arm and every found file:
- `found_<r>.jsonl` has no duplicate normalised proofs per target (my normaliser). The stored `norm` equals mine in
  every record, and `written` / `pruned` equal my line count / my reachability-pruned count in every record.
- `round_<r>.json` `targets_cum.solved` / `distinct_proofs` / `new_proofs_this_round` equal my counts. Examples:
  smoke_default 1,487 solved / 2,777 distinct; smoke2_default r1 45 / 156, r2 49 / 229 (+73); smoke2_unlikely r2 48 / 228
  (+72). `alloc` accepted / tried equals the step-mean reward exactly (e.g. 7,620 / 16,384 = 0.465088). The set of names
  with an accepted sample equals the solved set.
- `found_2` ⊇ `found_1` (smoke2), and the `round` fields split 156 / 73 and 156 / 72.
- `found_transfer_<r>` cumulative solved / distinct equal `transfer_cum` (smoke2_default 36 / 115 → 38 / 155;
  smoke2_unlikely 40 / 118 → 41 / 172). Held-out-200 greedy is 200 / 200 at both boundaries in both smoke2 runs.
- Registry compute rows exist per (phase, round) with `gpu_seconds` (phases sample / update / eval / job, GPU type
  named), `gen_tokens`, `attempts`, `actions`, `train_steps`, `train_tokens`, `lean_checks`. `attempts` reconciles: for
  smoke2, 8,720 = 2 × 2,048 training rollouts + 2 × (64 × 32 + 64 + 200) boundary rollouts.
- Proof length in the smoke found files: mean written 9.3–10.6 lines. Mean term size 5.4–6.6, where my definition
  counts rule applications reachable from the conclusion, PR / AS / R = 0 and ORE = DN = 3 (not `lean_check`'s size,
  which is for free-form Lean). No length claims rest on these; they are listed only as the per-arm record.

### Advantage variants (`adv_check.json`)
- **pass@k** equals brute-force enumeration of k-subsets (Chen et al. §2.4: mean over the subsets containing i of max
  reward − mean pass@k). I tested every c for G ∈ {2, 4, 8, 16} and every k (370 cases); the maximum difference is
  1.7e-16. k = 1 equals `default`. At G 8, k 4 the advantage is identically zero for c = 0 and for **c ≥ 5**. This
  explains the smoke's A ≠ 0 fraction (0.32 against 0.61 with variance), and it means pass@4 trains on ≈ 0.6× default's
  tokens per update by construction.
- **unlikely** equals my transcription of He et al. §4.1 (rank 0 = most likely under the sampling policy, factor
  1 − β(G − rank)/G, groups with zero unperturbed advantage skipped) on 2,000 random groups; the difference is exactly 0.
  One reading question: the code ranks over all G rollouts, which is one reading of "rank within the group"; the lit
  note does not settle it. The sequence log-prob is summed over every action token of a multi-step trajectory, so the
  ranking is length-confounded: a longer correct proof is "less likely" and gains credit. That is an interpretive
  caveat for E3 in a project about length.
- **default** and **distinct** match hand values. Distinct can move an all-correct group (not an arm).
- The `--adv_std` path divides pass@k by Chen's σ = √(R̄(1 − R̄)) (hand-checked). It is off in every pre-registered arm.

### Code (`grpo_state.py`), read line by line
Correct as far as I can see: on-policy sampling and log-probs at T (logits / T, matching the sampler); the exact
sampled ids, up to and including `<eos>`, used in the loss; zero-advantage rollouts skipped (no gradient anyway); a fixed
divisor; grad clip 1.0; AdamW (0.9, 0.95), wd 0; no dropout in `model.py`; RoPE, so no context truncation between
sampling and scoring. The budget is 561 updates × 2,048 = 1,148,928 rollouts against EI's 1,150,720 (−0.16 %), ≈ 255.6
attempts per target against 256. Boundaries fall at steps 70, 140, …, 561.

Findings (none invalidates the smoke):
1. **CI's trajectory-replay test is weak.** In the CI log all 8 CPU rollouts end in `syntax` after one action (0 / 8
   accepted), so test 1 only replays one-step trajectories. Multi-step state-id fidelity — the property that makes the
   update on-policy — is not exercised on CPU. The GPU smoke produces multi-step Lean-accepted proofs (checked above),
   but the ids fed to the loss are not stored, so that fidelity is not independently verifiable from the artefacts.
2. **The default `--heldout` is `data/heldout.jsonl`** (≠ `data/p2/heldout.jsonl`: different files, 4,996 vs 4,999
   classes). The same goes for the default `--lr 1e-4`. `pod/gs/grpo_seed.sh` passes `data/p2/heldout.jsonl` and
   `--lr 3e-5` explicitly, and state-cap12's EI ladders used p2. Correct as launched, but a hand launch without the
   runner would silently change both.
3. At a wrap of the shuffled target order, one update can hold the same theorem twice (4,495 is not a multiple of
   256). This is harmless for default / unlikely / pass@k. For `distinct`, both copies can claim the same "new" proof's
   bonus. Distinct is not an arm.
4. The distinct-proof archive and novelty keys use `normalize.norm`. My normaliser agrees on every stored record.

### Pre-registration arithmetic and inherited numbers
- **Inherited values trace to reviewed files.** T1 transfer 1,960 / 2,027 / 2,024 / 1,985 and targets 4,171–4,228:
  `origin/dan_state-cap12:review_sc12/ladder_recount.json`. Long pool Q: T1 233 / 295 / 320 / 317, Stage-1 134 / 212 /
  228 / 216 (`rr_recount.json`, Q = solves in gen-line bins 13–16, n = 90 + 90 + 100 + 100 = 380). `transfer_long2` +
  calib: T1 34 / 59 / 58 / 61, frozen 11 / 16 / 21 / 23 (`origin/dan_long-pool-2:review_long-pool-2.md` l. 82–83). All
  carry the SN-cap12 label.
- **MDD.** sd and MDD reproduce: 12.7 → 23, 40.4 → 72, 32.4 → 58, 0.004 → 0.7 pp, with c = 1.794 = (t₀.₉₇₅,₁₀ +
  t₀.₈,₁₀)·√(2/6); c = 2.37 at n = 4. Sign-test p 7/64 = 0.109 and 1/64 = 0.016, permutation minimum 2/64, and the
  deepening bounds 3/20,256 = 1.5e-4 and 3/10,256 = 2.9e-4 all check.
  **Mislabel:** the held-out row's values (0.969 / 0.977 / 0.978 / 0.974) are **Stage-1** held-out greedy (state-cap12
  gates), in a column headed "SN-cap12 T1 values". The T1 round-8 values are 0.962 / 0.9756 / 0.977 / 0.9772 (sd
  0.0073), which give **MDD ≈ 1.3 pp**, not 0.7 pp, for final-checkpoint comparisons such as E4. E4's 2 pp threshold is
  still above that.
- **Split disjointness by renaming class** (my key: atom permutations × premise multiset). `rl_targets` (the GRPO
  training pool) is disjoint from held-out (p2 and root), `transfer_long2`, calib, rr600, ge17 and validation_36. It
  overlaps `transfer` in **2 theorems** (`la_transfer_307` ~ `la_rl_targets_2228`, `la_transfer_842` ~
  `la_rl_targets_363`). Both are premise reorderings, which the pools' order-sensitive `key` does not merge. This is
  inherited from the ladder pools, is ≤ 2 / 2,285 of any transfer count, and is far inside every MDD. `transfer_long2_calib`
  = `ge17` (70 / 70), as POOLS.md documents. Stage-1's `train_k12` is not in the workspace; its disjointness is
  state-cap12's (`review_sc12/splits.json`), not re-derived here.
- **Design asymmetry not stated in § 4.** The EI ladders (state-cap12's command: `--train data/kh/train_k12.jsonl`,
  `rl_weight 4`, `retain 20000`) replay Stage-1 training proofs in every fine-tune. GRPO has no replay and no KL. This
  bears directly on E4 (held-out cost) and on "support" read-outs: EI's held-out retention is partly bought by replay.
  § 4 should list it under "not matched".
- **Missing scripts on this branch.** The read-outs name `lpool_reread.py` (only on `dan_long-pool-2` /
  `dan_state-cap12`), `ss_support.py` (only on `dan_support-state` / `dan_state-readouts`) and `pod/sc12/sn_seed.sh`
  (only on `dan_state-cap12`, which is **not merged** into `dan`). None is on `dan_grpo-state` / `dan`. The experiment run
  has to merge them first; the pre-registration does not say so.
- **Costing arithmetic** reproduces as written: 561 × 19.5 × 1.15 + 8 × 400 s = 4.38 h per ladder; ÷ 1.47 × 18 = 54
  pod-h; total 74 → 85 with margin, $37 → $43. Two inputs look **low** from the smoke's own rates:
  - *Boundary eval "≈ 400 s".* 80,405 rollouts (73,120 transfer pass@32, 2,285 greedy, 5,000 held-out). At the smoke's
    3090 rate (2,048 target rollouts per 16 s), transfer alone is ≈ 570 s, and transfer theorems are longer than the
    targets (mean `L_true` 9.07 against 8.22). On the A40, smoke2's boundary took 53–55 s of eval GPU time for 2,312 rollouts. At ≈ 630 s per boundary the
    ladders cost ≈ +6 pod-h.
  - *Support deepening "8.5 pod-h for 6 seeds".* Every base-unreached theorem consumes the full 10,000 (5k + 5k)
    attempts. At ≈ 85–128 rollouts / s for one job on a 3090 (the smoke rate, less for longer theorems), each costs
    ≈ 80–120 s. 8.5 pod-h (≈ 12.5 job-h at 1.47×) covers ≈ 380–560 base-unreached theorems in total, ≈ 65–95 per seed,
    out of ≈ 250 k256-unsolved per seed. If more than about a third of them survive 10k, the item is under-costed by up
    to ≈ 3×. The smoke does not measure this, so it is a risk, not an error.

### Wording to check in phase 2
- The addendum says "One RTX 3090" for the smoke; smoke2 ran on an A40.
- The addendum says E1's reason is contradicted at the start of training. That is correct and fair: base per-sample
  reward is 0.46, 0.57–0.61 of groups have variance, and 0.25–0.28 are all-fail.
- E5 (variance fraction 0.10–0.35 run average) now looks unlikely from a 0.57 start. It was committed before the smoke
  and not changed, which is right.
