# Pre-registration — ladder-A (RL technique ladder, Phase A, rungs T1–T6)

Written 2026-09-18 01:14 UTC, before the first pod of this run. Executor: agent:claude. Branch `dan_ladder_a`.
Proposal: `~/nd-rl/docs/proposals/2026-09-17-rl-technique-ladder.md` (metric section binding). Policy: `AGENT_POLICY.md`.

## Question
Which expert-iteration-family technique raises the **true** proof-length frontier `L*` of the take-home's cap-6 `abs`
Stage-1 model the most, on a transfer pool it never trains on, at an equal sample budget, against a frozen control?

## Pools (built once, committed under `data/ladder/`, before any RL pod)
- Reservoir: strict long generator (`gen.py --long`, 7–16 generated lines, unchanged generator) + textbook-shaped
  schemata instances (`textbook_pool.py`, 26 schemata, random sub-formulas). Every theorem labelled by `minlen.py`
  at bound 14 (two stages: bound 8 with 10 s, then bound 14 with 120 s on the remainder). `L_true` = `min_lines_ub`.
  Unresolved (timeout or no proof ≤ 14 in the restricted space) recorded and never counted.
- **Transfer pool**: target ≥ 1,500 theorems with `L_true` in 7–14; ≤ 40 instances per schema. Never sampled in training.
- **RL-target pool**: ≈ 2,000 theorems with `L_true` in 7–14, same recipe, ≤ 40 per schema.
- Disjoint by renaming class (`gen.canon_key`) from each other, from Stage-1 train / held-out, from the take-home's
  `data/rl_targets.jsonl` and `data/transfer.jsonl`, and from validation-36. Checked by assertion in `make_ladder_pools.py`.
- Pool expectations: bin mass on transfer roughly 7: 35–45 %, 8: 25–35 %, 9: 10–20 %, 10: 5–10 %, 11–14: 3–10 %;
  the bound-14 stage leaves < 15 % of its input unresolved.
- Deviation from the brief's order, stated: the prover needs CPU cores, so the pool pod is created after this
  commit and before the pools are committed; no RL pod starts before `data/ladder/POOLS.md` is committed.

## Common protocol (every rung)
- Init: `ckpts/stage1_abs.pt` (the take-home's cap-6 abs model). Fine-tune per round: 600 steps, lr 3e-4, mix of
  accumulated target proofs (≤ 4 per theorem, ×4) + 20,000 retained Stage-1 records (as in `expert_iter.py`).
- Sample budget: **256 samples per RL target** in total per arm (8 rounds × N_targets × 32 samples), T = 0.8.
  Transfer: 32 samples per theorem per round from the current model, cumulative 256 (union over rounds), as in the
  take-home. Frozen control: the same 8 × 32 attempts from `stage1_abs.pt`.
- Two seeds per rung (seed 0, seed 1: sampling and training seeds). Frozen control: seeds 0 and 1.
- Counting: verifier-accepted proofs of the prompted sequent, start-index-normalised (`normalize.norm`), distinct per
  theorem. `L*` = largest L with ≥ 5 distinct theorems solved having `L_true ≥ L` (per pool, per seed). Solve rate per
  `L_true` bin with Wilson 95 % intervals. Base reachability of every counted proof: `novelty.py` log p under
  `stage1_abs.pt` at T = 0.8, marginalised over start index; "elicitation" if p ≥ 1e-5, "creation" otherwise
  (the Phase-1 line), also reported at the 1/256 line.
- Rungs (driver `ladder_ei.py`, a copy of `expert_iter.py` with the additions below):
  - **T1** baseline EI, uniform k = 32.
  - **T2** difficulty-weighted sampling: round 1 uniform; afterwards per-round budget N×32 allocated ∝ weight,
    weight 1 for never-solved targets, 4 for solved targets with smoothed per-sample acceptance < 0.1, 0 for
    acceptance ≥ 0.25 (saturated); per-target cap 128.
  - **T3** hindsight relabelling (`--relabel`): by-products (valid proofs of another conclusion from the same premises,
    ≥ 7 lines, class not in any pool) added to the training mix; reported as outside-target data.
  - **T4** moving target window: round 1 uniform; afterwards targets with `L_true` in [L*_cur+1, L*_cur+3] (L*_cur = the
    current target-pool L*) get k = min(128, budget/|window|), the remainder of the N×32 budget spread uniformly
    over the other targets. Labels come from the committed pool (no prover during the run).
  - **T5** precursor injection: rounds 1–3 as T1; after round 3 the unsolved targets' *generating* proofs (generator
    targets) and schema names (textbook targets) give the needed shapes (`patterns.py`, `patterns2.py`,
    `precursors.py` templates); a fresh cap-6 generator run (new seed, classes disjoint from every pool) supplies
    ≤ 6-line verified proofs with those shapes; they are added (×2) to round 4's training mix only; rounds 5–8 as T1.
  - **T6** sibling ensemble: 2 siblings from the same init, k = 16 each per round (same total budget), found target
    proofs pooled after every round's sampling; each sibling trains on the union from its own previous checkpoint.
    Transfer: 16 samples per sibling per round, union counted (256 per theorem in total).
- Order of runs: frozen (2 seeds) and T1 (2 seeds) first, then T2, T4, T6, T3, T5.

## Predictions (falsifiable; `L*` on transfer / on RL targets, seed-wise; a rung "raises" if both seeds beat T1)
Reference on the old pool at 512 attempts (`novelty_phase1_theorems.jsonl` × `minlen_transfer.jsonl`, bound 8):
frozen solved 89/297 at `L_true` 7 and 0/127 at 8; EI (s0, 16 rounds) 237/297, 62/127, and 10/65 of the unresolved.

| rung | mechanism (one line) | predicted `L*` transfer | predicted `L*` targets | falsifier |
|---|---|---|---|---|
| frozen | resampling only | **7** (solve 25–35 % at 7, ≤ 3 % at 8, 0 at ≥ 9) | 7 | ≥ 5 transfer theorems solved at `L_true ≥ 8` → 8 |
| T1 | keep-any-success amplifies what is already reachable | **9** (solve 60–80 % at 7, 20–45 % at 8, 3–12 % at 9, 0–3 % at 10) | 9–10 | `L*` ≤ 8 or ≥ 10 on both seeds |
| T2 | budget at the frontier moves the prior where it matters | 9 (≤ T1 + 1); targets **10** | 10 | targets `L*` ≤ T1's on both seeds |
| T3 | more long verified proofs per sample | 9; solve at 8 within ±5 points of T1 | 9 | transfer `L*` ≥ 10 on both seeds |
| T4 | keeps signal at the edge; window drift | 9; targets 10 | 10 | targets `L*` ≤ T1's on both seeds |
| T5 | cap-6 sub-steps of the needed shapes ignite them | 9; textbook-schema solve rate ≥ T1 + 5 points | 9 | schema solve rate ≤ T1's on both seeds |
| T6 | two policies = more diverse samples at equal k | 9 | 9 | transfer `L*` ≥ 10 on both seeds |

- Headline prediction: **no rung reaches `L* − L*_frozen ≥ 3` on transfer**; T1 reaches +2 (9 vs 7) on at least one
  seed; no rung beats T1's transfer `L*` on both seeds. If a rung does, Phase B is requested in `QUESTIONS.md`.
- Base reachability: ≥ 90 % of counted transfer proofs with `L_true ≥ 9` have base p < 1e-5 under every rung
  ("creation" by the Phase-1 line); at `L_true` = 7, 40–60 % are above 1e-5 (elicitation).
- Held-out greedy (in-distribution) stays ≥ 93 % for every rung.

## Budget and stop rule
- Pods: one RTX 3090 ($0.50/h, 32 vCPU) for pools, then up to three 3090s for arms. Predicted total ≈ $12–20; cap **$50**.
- Hard stop 36 h after 01:08 UTC 2026-09-18 (13:08 UTC 2026-09-19). Rungs that have not finished both seeds by then
  are reported as incomplete; the leaderboard is written with what is pulled back.
- If the transfer pool cannot reach 1,500 theorems at `L_true` 7–14 within 3 pod-hours of prover time, the run
  proceeds with the pool as built and says so.

## Amendment 2026-09-18 01:50 UTC (after the pool build and a killed round 1; before any rung result)
- **RL-target pool v2** (see `data/ladder/POOLS.md`): the first target pool gave the base model a foothold of 16/2,295 targets
  at k = 32 (round 1 of T1 s0 and T2 s0, both killed), because its `L_true`-7 bin was almost all textbook schemata. 1,500
  generator theorems at `L_true` 7 and 700 at `L_true` 8 were moved from the reserve into the target pool (4,495 targets).
  Transfer pool, budget per target, predictions and falsifiers unchanged; the target-pool `L*` predictions now refer to the
  v2 pool. The killed round-1 outputs were deleted and are not reused.
- Samplers run at `--batch 512` (two at 1,024 exceeded the 3090's 24 GB); this changes nothing statistically.
