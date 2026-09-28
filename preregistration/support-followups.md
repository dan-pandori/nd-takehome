---
run_id: support-followups
role: executor
written_on: 2026-09-28
branch: dan_support-followups (from origin/dan_support-curves)
proposal: 12 (elicitation curve); follow-ups named in review_support-curves.md §Verdict
---

# Pre-registration — `support-followups`

Written **before the first pod** and before any D computation. Budget: `podbudget support-followups`
30 pod-hours / $15 (registered by Dan). RunPod balance at writing: $136.49 (floor $100).

## The question

`support-curves` found 29 transfer theorems (`data/sc/falsifier_survivors.txt`) with 0 base successes
in 200,000 attempts at T 0.8 and 200,000 at T 1.0 that the base's own EI descendant solves at
p̂ 0.022–0.9995. Four pressure tests: **D** what kind of improbability separates the base from those
proofs (a new move, or per-step reliability compounding over a long proof); **A** does it replicate on
an uploaded seed-1 EI checkpoint; **B** are the longest survivors reachable at 25× more depth; **C** is
it an artefact of 3.2 M-parameter capacity.

## Models (every number carries one of these labels)

| label | checkpoint | md5 | what it is |
|---|---|---|---|
| base s0 | `ckpts/lf/stage1_a1_seq_s0.pt` | `9bde44c0b6c7580951656bf57aec3e43` | 3,214,336 params, from scratch, `lean_seq`, cap 6, Stage 1 only, trained on `data/p2/train_depth3_f0_a1.jsonl` (6,000 × 128) |
| base s1 | `ckpts/lf/stage1_a1_seq_s1.pt` | `fc27e52d017e5a361b3232fcd13f4ddc` | the same, Stage-1 seed 1 |
| EI s0 | `ckpts/ladder/la_T1_sc_s0_r8.pt` | `5cebd7eca859f4a4bb1dcc4ed47b8bbc` | base s0 + 8 × k 32 EI at T 0.8 on the disjoint ladder pool (support-curves) |
| EI s1rerun | `ckpts/ladder/la_T1_sc_s1rerun_r8.pt` | `12c13e6115571022d66a23ad2bb59e6d` | base s1 + the same recipe, re-trained after the original (`105be4f3…`) was lost |
| big s0 | `ckpts/sf/stage1_big_seq_s0.pt` (this run) | recorded when trained | 8 layers, d 512, 8 heads (≈ 25.5 M params; exact count reported), otherwise the base's recipe: `train.py --mode lean_seq --steps 6000 --bs 128 --cap 6 --seed 0`, same data, same lr schedule (1e-3 → 1e-4, warmup 200) |

Judge everywhere: Lean alone (`lean_judge.judge_many` via `support.py`), both models identically; every
accepted literal text stored. `nd_verify` judges nothing.

## Sampler settings (all new sampling in this run)

Fast path (`generate_ids_fast`, compaction on, per-row seeding), **batch 4,096** for the 3.2 M models if
the first job's `torch.cuda.max_memory_allocated` allows (recorded per job; `support.py` is extended to
log it and the no-`<eos>` count per theorem), **`max_new` 512**. Truncation (= no `<eos>` within 512) is
reported per `L_true` stratum; if it exceeds 0.1 % of samples in a reported stratum, the stratum is
flagged and later jobs raise `max_new` to 640. Sampling seeds are fresh (≥ 100) so no stream replays a
support-curves stream. Batch and `max_new` differ from support-curves (2,048 / 400): comparison with
its numbers is a sampling re-draw, not a correctness change (`NOISE_FLOOR.md`).

## D — where is the improbability? (forward passes only, VPS CPU or a pod GPU)

**Proof sets** (all scored teacher-forced under **base s0**, at T 1.0 = the model's own distribution
as primary and T 0.8 as secondary; also under EI s0 for reference):
- **S** — every distinct EI s0 proof of the 29 survivors in `artifacts/sc/summary.json` (the set
  `sc_secondary.py` scored, restricted to the 29; review: 231 proofs).
- **C1** — every distinct EI s0 proof of the other 53 forward-crux theorems (base s0 solves them, but
  only after > 10,000 attempts).
- **C2** — the base s0's own accepted proofs in stage 1 (T 0.8, `s1_base_T08_s0.s{0,1}.jsonl`), all
  distinct ones.

**Per-step decomposition, exactly marginalised over the name offset.** For each proof and each allowed
offset s, the per-token log p; the marginal prefix log-probability L(t) = logsumexp_s Σ_{u≤t} log p_s(u);
token t's marginal contribution is L(t) − L(t−1) (the log-probability of token t given the prefix,
with the offset integrated out by its posterior). The contributions sum exactly to `sc_secondary.py`'s
`logp_T1` (checked per proof to 1e-3). A **step** is one `have … ;` head-and-term (for a box-valued
`have`, the head up to and including the box's `fun ( n : A ) => by` is one step, the "box opening"),
or one `exact …` (with trailing `)` / `<eos>`). Tokens are classed **syntax** (brackets `( ) ⟩ ,`,
keywords `have exact fun => by`, `: := ;`, `hh`, `<eos>`), **naming/citation** (`n*` and `h*` names;
sub-labelled fresh name vs cited name), **logic** (formula atoms, connectives, `False`, and the
rule-carrying tokens `.1 .2 .elim Or.inl Or.inr Or.elim Classical.byContradiction ⟨` and the `(` that
opens a box term right after `:=`).

**Per proof:** total log p, number of steps, worst step's log p (w1), share of the total in the worst
1 and worst 2 steps (s1, s2), the 3 lowest-log-p tokens and their classes; per set, the share of total
surprisal by token class.

**Classification (primary unit: each survivor's most-probable EI proof under the base, T 1.0):**
- *concentrated*: s2 ≥ 0.50 **and** w1 ≤ −6 nats (one step at p ≤ 1/400);
- *spread*: s2 < 0.50 **and** w1 > −6 nats;
- otherwise *mixed*.

**Readings:** **"a new move"** if ≥ 20 of 29 survivors are concentrated; **"compounding reliability"** if
≥ 20 of 29 are spread; otherwise **"mixed"**. Supporting check: the fraction of survivors whose w1 lies
below the 5th percentile of C2's w1 (new move predicts most; compounding predicts few, with the
survivors' median per-step log p excluding the worst step within 2× of C1's).

**Expected:** mixed, leaning to new move — concentrated **17 (10–24)** of 29, spread **≤ 8**. The
compounding reading (≥ 20 spread) **will not** occur (my falsifiable prediction). Lowest tokens: logic
(rule / formula choice) ≥ 50 % of the worst-3 tokens over S, syntax ≤ 20 %. Survivors' worst step
below C2's 5th percentile for ≥ 15 of 29.

## A — seed-1 column on an uploaded checkpoint

Deviation from the brief: support-curves' stage 3 ran **k = 10,000, stop at 50** (not 2,000; see
`artifacts/sc/s3_*` records), so A re-runs exactly that: base s1 and EI s1rerun, 383 theorems, T 0.8,
k 10,000, stop 50. Reported beside the lost-checkpoint column (EI s1 `105be4f3…`: 144 / 383 solved;
base s1: 37 / 383; forward crux 107; 28 of the 29 survivors solved by EI s1, 1 by base s1).

**Expected:** EI s1rerun solves **145 (125–165)** / 383; base s1 re-draw **37 (32–43)**; forward crux
(base s1 0, EI s1rerun > 0) **105 (85–125)**; of the 29 survivors, EI s1rerun solves **≥ 24** and base s1
**≤ 2**; per-theorem solved/not agreement EI s1rerun vs lost EI s1 **≥ 88 %**, vs EI s0 **≥ 85 %**;
base s1 re-draw vs its support-curves draw **≥ 95 %**.

## B — depth on the longest survivors

The 6 survivors at `L_true` 11 (5) and 12 (1): la_transfer_{87, 1858, 1893, 1932, 2038, 454}; their
best EI proof's base log p (T 0.8) is −30.9 to −85.2. Base s0, T 1.0, up to **1,666,667 more attempts
each (10⁷ total)**, stop at 5 successes. None ⇒ p_base < 1.8 × 10⁻⁶ (95 %, 3/1.67 M) each.

**Expected:** 0 successes on ≥ 5 of 6; total successes ≤ 3.

## C — a bigger base (big s0)

Train big s0 (above); held-out greedy on `data/p2/heldout.jsonl` (`eval_set.py --k 1 --temperature 0`;
base s0 = 0.9088). Measure its sampling throughput first and re-project before committing the sampling.
Then the 82 forward-crux theorems at k 10,000, T 0.8, stop 50; then every survivor it has not solved:
up to 200,000 per temperature (T 0.8 then T 1.0), stop at 5 per temperature. Seed 1 only if budget
allows. Caveat to state: 6,000 × 128 is the 3.2 M model's schedule; a 25 M model may be further from
saturation (stage1-dynamics found the 3.2 M model not saturated) — "more capacity, same data and
steps", not a tuned larger model. If training diverges (loss NaN or val loss > 2× base s0's), one
retry at lr 5e-4, reported.

**Expected:** held-out greedy **0.90–0.96**; of the 82 forward-crux at k 10,000: **20 (8–40)**; of the 29
survivors within 200,000 per temperature: **6 (2–14)**.

**Falsifier for "the expansion is a 3.2 M-capacity artefact": big s0 reaches ≥ 15 of the 29 within
200,000 attempts per temperature.** I predict it does not fire.

## Stop rule, budget, drop order

Order D, A, B, C (D on the VPS in parallel with pods). Pods: A40 at the billed rate (record
`costPerHr`). Stop at 30 pod-hours / $15 or if the balance would fall below $100 counting `state-env`'s
remaining ceiling. Drop order: C seed 1, then C's T 1.0 depth, then B's depth halved. If C would not
fit, finish D, A, B, write up, and put C's projection in `QUESTIONS.md`.
