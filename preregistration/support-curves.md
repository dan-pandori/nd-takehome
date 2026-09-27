---
run_id: support-curves
role: executor
written_on: 2026-09-27
branch: dan_support-curves
proposal: docs/proposals/2026-09-27-elicitation-curve.md (nd-rl), experiment 1
---

# Pre-registration — `support-curves`

Written **before the first pod**. Gate 0 compares this commit's timestamp with the first entry for
this run in `~/pods.log`.

## The question

On theorems neither model was trained on, does the expert-iteration (EI) model solve theorems the
base model essentially **cannot** — at k far beyond the attempts EI itself used — or does base
pass@k catch up? Equivalently: the first measured points of the elicitation curve, per-theorem
log p_base against log p_EI.

Two readings are on the table (proposal 12). **RL as a sampling amplifier**: EI acquires theorems
whose p_base is above roughly 1/(attempts EI spent), and base pass@k eventually catches it.
**RL as a generaliser**: EI acquires theorems far below that, and base pass@k never catches up.
The project's whole pattern to date predicts the amplifier; this run is set up so that the
generaliser reading can win.

## Models (every number below carries these labels)

| label | checkpoint | what it is |
|---|---|---|
| **base s0** | `ckpts/lf/stage1_a1_seq_s0.pt`, md5 `9bde44c0b6c7580951656bf57aec3e43` | 3,214,336-parameter from-scratch GPT, `lean_seq` Lean format, **cap 6**, Stage 1 only, trained on `data/p2/train_depth3_f0_a1.jsonl` (depth-3 frequency 0, A1 composition). Downloaded from `hf://buckets/dan-pandori/nd-rl/lean-format/ckpts/lf/`; md5 matches the value `ds-generator`'s review recorded. |
| **base s1** | `ckpts/lf/stage1_a1_seq_s1.pt`, md5 `fc27e52d017e5a361b3232fcd13f4ddc` | the same, Stage-1 seed 1. |
| **EI s0 / s1** | `ckpts/ladder/la_T1_sc_s0_r8.pt` / `..._s1_r8.pt` | **trained in this run**: ladder rung T1 (plain expert iteration, 8 rounds × k 32, T 0.8) from base s0 / base s1, mirroring `noise-floor`'s `la_T1_dsc_*` command exactly. Every round's checkpoint is uploaded. |

Both models are the **same architecture and tokenizer**; EI differs from its base only by 8 rounds
of expert iteration on `data/ladder/rl_targets.jsonl` (4,495 targets), which is **disjoint from the
transfer pool this run measures**.

### Deviation already recorded: the EI models genuinely have to be re-trained

The brief says to re-train "because no Lean-format EI checkpoint was ever uploaded". I checked
before accepting that, because re-training costs ≈ 6 of my 30 pod-hours. The bucket **does** hold
`hf://…/lean-format/ckpts/ladder/la_T1_seq_s{0,1}_r{1..8}.pt`. They are **not usable here**: both
their `args.json` files record `"init": "ckpts/lf/stage1_full_seq_s0.pt"` — a *different* Stage-1
checkpoint (md5 `f3d68227…` vs the A1 control's `9bde44c0…`), and **both seeds start from the same
seed-0 base**, so they are not two Stage-1 replicates. Re-training confirmed necessary.

## Judging — Lean alone decides

`lean_judge.py` is on `origin/dan` as of commit `9a1db24` (sibling run `lean-judge`), and this
worktree is merged up to it, so **`lean_judge` is what this run uses**, for both models identically.
`nd_verify` judges nothing here. Concretely: each sample is decoded, start-index-normalised
(`normalize.norm`), and each *distinct* normalised string is Lean-checked once via
`lean_judge.judge_many` — byte-for-byte the judging path `coverage.py` now takes. Numbers in this
run are therefore **under Lean alone**; where they are compared with pre-2026-09-27 numbers (Lean ∧
`nd_verify`) the comparison is labelled.

Proof length is reported in **lines** (`;`-count) **and term size** (`review_nf_ladder_cov.proof_term_size`:
formula syntax-tree nodes summed over the proof's lines). The pool's `L_true` labels come from
`minlen.py` and are **ND-derived upper bounds** on the minimal *Lean* proof length.

## Theorem set — fixed and committed before any sampling

`data/sc/theorems.jsonl`, md5 `3cb6e7bf3b094ce24ebc0706777a9a70`, built by `sc_theorems.py` with
seed 20260927 from `data/ladder/transfer.jsonl` (2,285 theorems, never trained on).

**383 theorems**: 60 each at `L_true` 7, 8, 9, 10, 11, 12 and **every** theorem at `L_true` 13 (13)
and 14 (10). 20 schemata, 183 textbook. The brief's "25 each at `L_true` 4–6 as anchors" is not
available — the transfer pool's histogram is 7:300 8:300 9:1010 10:451 11:99 12:102 13:13 14:10 and
holds nothing below 7, so the 7 and 8 bins are the anchors.

## Design

All sampling with `support.py` (written for this run; it does not touch `lean_gate.py`,
`lean_judge.py`, `coverage.py`, `eval_set.py`, `expert_iter.py`, `ladder_ei.py`, `eval_targets.py`,
`grpo.py` or `train.py`, which the two sibling runs own).

- **Stage 0 — EI training.** `ladder_ei.py --rounds 8 --k 32 --temperature 0.8 --batch 512 --max_new 512
  --heldout data/p2/heldout.jsonl --train data/p2/train_depth3_f0_a1.jsonl --init ckpts/lf/stage1_a1_seq_s<k>.pt
  --seed <k> --name la_T1_sc_s<k>`, both seeds. All 8 round checkpoints uploaded.
- **Stage 1 — both models, seed 0, T = 0.8, k up to 4,000 per theorem**, stopping a theorem at the
  first batch boundary with **50 successes**. Records (n, c, first-success index) per theorem.
- **Stage 2 — the crux sets, adaptive.**
  - *Forward crux* = theorems with c_EI ≥ 1 and c_base = 0 after stage 1. Base gets up to **40,000
    more attempts** each, **20,000 at T = 0.8 and 20,000 at T = 1.0**, stopping at 5 successes per
    temperature. EI gets 4,000 attempts at T = 1.0 on the same theorems for symmetry.
  - *Reverse crux* = c_base ≥ 1 and c_EI = 0. EI gets up to **20,000 more** attempts at T = 0.8.
- **Stage 3 — replication on Stage-1 seed 1:** both models at k = 2,000, T = 0.8, same 383 theorems.
- **Secondary (forward passes only):** base teacher-forced log-probability of each distinct EI-found
  proof on the forward crux, marginalised over the random name offset. This is a **lower bound on
  p_base for that proof**, not for the theorem.

Sampling is i.i.d. per theorem, so (n, c) at one temperature **add** across stages; the analysis sums
them.

### Stopping-rule caveat, stated here so it is not a surprise

A theorem that reaches 50 successes stops at a batch boundary, so its n is a stopping time and
p̂ = c/n carries an O(1/c) ≈ 2 % bias. Theorems that never reach 50 have fixed n and an exactly
unbiased p̂. The scatter spans 4+ decades; 2 % is invisible on it. Pass@k uses the unbiased
estimator 1 − C(n−c, k)/C(n, k) for k ≤ n only; anything beyond n is labelled extrapolation.

## Expected results (numeric; recorded before the first pod)

| # | quantity | prediction |
|---|---|---|
| E1 | EI transfer theorems solved at 8 × 32, full 2,285 pool, per seed | **856–965** (the on-file range for this base under Lean ∧ `nd_verify`; under Lean alone I expect the same to within +1 %) |
| E2 | base s0, theorems solved of 383 at k = 4,000, T = 0.8 | **80–190** (21–50 %) |
| E3 | EI s0, theorems solved of 383 at k = 4,000, T = 0.8 | **200–320** (52–84 %) |
| E4 | forward-crux size (c_EI ≥ 1, c_base = 0 at k = 4,000) | **60–150** theorems |
| E5 | **the falsifier** — forward-crux theorems with 0 base successes in ≥ 40,000 attempts at **both** temperatures while p̂_EI ≥ 0.01 | I predict **8** (range **0–19**), i.e. **the falsifier does not fire**. It fires at **≥ 20**. |
| E6 | reverse-crux size (c_base ≥ 1, c_EI = 0 at k = 4,000) | **5–25**; after 20,000 more EI attempts, **0–10** survive |
| E7 | per-stratum crossover k (base pass@k ≥ EI pass@k) | exists within measured k for `L_true` 7–9, at k between 10³ and 10⁴; **no crossover within measured k for `L_true` ≥ 11** |
| E8 | theorems solved at `L_true` ≥ 13 (23 of them), either model, any k | **0–2** (`L_true` ≥ 13 was solved 0 times in 11 `ds-generator` ladder runs) |
| E9 | base theorems solved at T = 1.0 vs T = 0.8 on the forward crux | T = 1.0 finds strictly more, but **fewer than 3×** more |
| E10 | seed 0 vs seed 1 agreement, stage 1 at k = 2,000 | per-theorem solved/not agrees on **≥ 70 %** of the 383; solve **counts** differ by up to the `NOISE_FLOOR.md` frozen-ladder floor (±235 % at n = 2), so a count difference is **not** a finding |

**The pre-registered falsifier (support expansion):** ≥ 20 forward-crux theorems with 0 base
successes in ≥ 40,000 attempts at both temperatures while the EI model solves each at p̂_EI ≥ 0.01.

## Budget and stop rule

Pod budget **$15**, ceiling **30 pod-hours**, hard stop 30 h, registered with
`podbudget support-curves --set 30 15` before the first pod. Balance floor **$100** (`rpbalance`);
two sibling runs hold up to $34 more, so I will not extend past $15 without asking in `QUESTIONS.md`.

Projection at the `noise-floor` measured rate (600,000 samples ≈ 0.7 A40-hours on 7-line targets;
these theorems are longer, so I budget **500,000 samples per pod-hour** and will re-measure in the
first stage-1 batch): stage 0 ≈ 6 h, stage 1 ≈ 4.4 h, stage 2 ≈ 14 h, stage 3 ≈ 3 h — **≈ 28 h**.

**Drop order if the measured throughput overruns** (the brief's, kept): (1) stage 3; (2) stage 1's
k from 4,000 to 2,000; (3) the theorem count, dropping whole `L_true` bins from 9 downward.
**Never** the forward crux's 40,000 base attempts — that is the falsifier.

## What would change my mind

If E5 comes out ≥ 20, the amplifier reading of this project's EI results is wrong on this pool and
proposal 12's experiment 2 should be re-ordered around capacity rather than search. If E5 comes out
0 and E7 shows crossover in every stratum, the project's headline EI numbers are a statement about
sample efficiency and should be relabelled as such everywhere.

---

# Addendum 1 — re-sizing on the measured throughput (2026-09-27 18:30 UTC)

Written **before any stage-1 sample was drawn**. Stage 0 (EI training) is running; no measurement
data exists yet. The brief requires the throughput to be measured in the first batch and the run
projected from it; this is that step, and it came out **7× better than budgeted**, so the design
scales **up**. The falsifier and every prediction above stand; the numbers below are additions.

## Measured (source: `artifacts/sc/probe/mn{400,512}.s0.jsonl`, pod `sc1`, A40 46 GB, $0.49/h)

Base s0 (`stage1_a1_seq_s0.pt`, md5 `9bde44c0…`), 6 theorems at `L_true` 7, k = 2,000, T = 0.8:

- **988–1,001 samples/s single-job on an idle A40 = 3.6 M samples per pod-hour**, against the
  500,000/pod-hour I budgeted from `noise-floor`'s 7-line reductio targets.
- Wall split **gen 76 % / Lean 23 %**. Lean is cheap because the model is extremely concentrated:
  **6 to 142 distinct normalised strings per 2,000 samples**, and only distinct strings are checked.
  Distinct-string count grows far slower than k, so the Lean share *falls* as k rises.
- `--max_new` 400 and 512 give **byte-identical** per-theorem records: the model always terminates
  inside 400 tokens. **Using 400.**
- Sampling uses `generate_ids_fast` with compaction on. `ds-generator` recorded that compaction can
  flip ~1 row in 128 versus the base path (a bf16 batch-repacking difference). That matters for a run
  reproducing an exact count; it does not matter here, because every sample is an i.i.d. draw and the
  estimand is a probability. Stage 0 keeps `ND_SAMPLE_COMPACT=0` to mirror `noise-floor` exactly.
- Early signal, not a result: the base solved **0 of those 6** `L_true` 7 theorems in 2,000 attempts
  each. If that holds up, **E2 lands at or below its lower bound**.

Projection of the design as briefed: stage 1 ≈ 0.9 pod-h, stage 2 ≈ 3 pod-h, stage 3 ≈ 0.4 pod-h,
stage 0 ≈ 6 pod-h — **≈ 10 of the 30 pod-hour ceiling**. Spending the other 20 on more base attempts
is the single best use of them, because the falsifier is a statement about how many attempts the base
model survives.

## Re-sized design

| stage | briefed | **running** |
|---|---|---|
| 1 (seed 0, T 0.8, both models) | k 4,000, stop at 50 | **k 10,000**, stop at 50 |
| 2a forward crux, base | +20,000 @ T 0.8, +20,000 @ T 1.0 | **+50,000 @ T 0.8, +50,000 @ T 1.0** |
| 2a forward crux, EI | +4,000 @ T 1.0 | **+10,000 @ T 1.0** |
| **2b (new)** — survivors of 2a still at 0 base successes | — | **+150,000 more at each temperature**, budget permitting: up to **4 × 10⁵ base attempts** on the strongest survivors |
| 2r reverse crux, EI | +20,000 @ T 0.8 | **+50,000 @ T 0.8** |
| 3 (seed 1, T 0.8, both models) | k 2,000 | **k 10,000** |

**The pre-registered crux is not lost.** `support.py` records `first_hit`, so "c_base ≥ 1 within
4,000 attempts" is exactly `first_hit ≤ 4000`. The forward crux is reported at **both** the
pre-registered k = 4,000 and the stricter k = 10,000, and the primary falsifier is evaluated at its
pre-registered ≥ 40,000 attempts. The 100,000- and 400,000-attempt versions are reported as
strictly stronger secondaries.

## Added predictions at the new k (the k = 4,000 predictions E1–E10 stand unchanged)

| # | quantity | prediction |
|---|---|---|
| E2′ | base s0 solved of 383 at **k = 10,000**, T = 0.8 | **100–220** |
| E3′ | EI s0 solved of 383 at **k = 10,000**, T = 0.8 | **230–340** |
| E4′ | forward-crux size at **k = 10,000** | **50–130** |
| E11 | forward-crux theorems at 0 base successes after **100,000** attempts at both temperatures, p̂_EI ≥ 0.01 | **0–12** (the falsifier's own threshold is 20 at 40,000) |
| E12 | Lean share of sampler wall time at k = 10,000 | **below** the 23 % measured at k = 2,000 |

Revised projection: stage 0 ≈ 6 h, stage 1 ≈ 2.2 h, stage 2 ≈ 6 h, stage 3 ≈ 2.2 h, slack ≈ 2 h —
**≈ 18 of 30 pod-hours ≈ $9 of $15** on two A40s at $0.49/h. Drop order unchanged; stage 2b is the
first thing cut, before stage 3.

## Defect found in a file this run may not edit

`ladder_ei.py` **does not import** on `origin/dan` `9a1db24`: that commit (sibling run `lean-judge`)
renamed `expert_iter.relabel` to `relabel_candidate` / `relabel_batch` and left `ladder_ei.py`'s
line 34 `from expert_iter import relabel` untouched. It breaks every caller, not just this run.
`ladder_ei.py` and `expert_iter.py` belong to the sibling, so this run does not edit them: stage 0
runs through **`sc_ladder_ei.py`**, which supplies the missing name from outside and raises if it is
ever called. The only call site is line 233, inside `if a.relabel:` (technique T3), which this run
never passes — so stage 0 executes `ladder_ei.py` unmodified.
