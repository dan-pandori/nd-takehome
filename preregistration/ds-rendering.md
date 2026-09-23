# Pre-registration — run `ds-rendering` (proposal 10, arms R1 / R3 / R2 + control C0)

Written 2026-09-23 21:xx UTC on the VPS, **before any pod exists** (gate 0: this commit's timestamp
vs the first `ds-rendering` line in `~/pods.log`). Executor session. Repository
`~/work/ds-rendering`, branch `dan_ds-rendering` (worktree from `origin/dan_lean_format`).
Brief: `BRIEF_ds-rendering.md`. Proposal: `~/nd-rl/docs/proposals/2026-09-22-dataset-styles.md`.

## Question

With the ND proofs, the model, the schedule and the evaluation pools held **exactly** fixed, does
the *Lean rendering* the from-scratch model is trained on change held-out accuracy by length and
RL readiness? The sharp sub-question: is the "cap + 1" length horizon a property of the **text**
length or of the **ND proof's structure**?

Every arm trains on the *same 155,000 ND records* (`data/p2/train_depth3_f0_a1.jsonl`, cap 6,
depth-3 removed). Nothing about the data changes; only the tokenizer that renders each record
into Lean text. This is the tightest control available for a rendering question.

## Arms

All four are the same architecture and schedule: **3.2M parameters (4 layers, d 256, 8 heads),
trained from scratch, 6,000 steps, bs 128, lr 1e-3 → 1e-4, cap 6, on the 155,000-record a1 set,
Lean `lean_seq` surface form with a random first-appearance name offset.** Two Stage-1 seeds
(0, 1) each. Model labels in every table follow this line.

| arm | mode | rendering change | vocab |
|---|---|---|---|
| **C0** control | `lean_seq` | none — `have n1 : F1 := h1` premise lines, every `have` annotated, boxes are `( fun ( nS : A ) => by … )` | 107 |
| **R1** | `lean_seq_noprem` | premise lines are **not rendered**; later lines cite the statement hypothesis `hK` directly | 107 |
| **R3** | `lean_seq_nofml` | `have n3 := n1 n2` (no `: F`) for `IMPE`, `ANDE1/2`, `NEGE`, `R`; annotations kept elsewhere and on every `PR` | 107 |
| **R2** | `lean_seq_intro` | boxes are `( by intro nS ; … ; exact nE )` instead of `( fun ( nS : A ) => by … )` | 108 |

C0 reuses lean-format's two Stage-1 checkpoints (`stage1_a1_seq_s{0,1}.pt`, from the bucket) and
is re-measured here with this run's sampler, batch and code, so that all four arms share one
measurement pipeline. lean-format's inherited values are quoted beside the re-measurement.

## Already measured, before any pod — the render check

`dsr_render_check.py` (committed with this file), 3,000 a1 records per mode, output
`artifacts/dsr/render_check.json`:

| mode | round-trip render→`inverse` identical | Lean accepts literal texts | theorem-swapped negatives accepted | mean tokens / proof | ratio to C0 |
|---|---|---|---|---|---|
| `lean_seq` (C0) | 3000 / 3000 | 1000 / 1000 | 0 / 300 | 83.5 | 1.000 |
| `lean_seq_noprem` (R1) | 3000 / 3000 | 1000 / 1000 | 0 / 300 | 59.0 | **0.707** |
| `lean_seq_nofml` (R3) | 3000 / 3000 | 1000 / 1000 | 0 / 300 | 79.8 | **0.956** |
| `lean_seq_intro` (R2) | 3000 / 3000 | 1000 / 1000 | 0 / 300 | 76.4 | **0.915** |

Text length (`have` lines in the literal text, same 3,000 records; ND lengths 2–6 are flat):
C0 / R3 / R2 **1:80 2:680 3:875 4:844 5:386 6:135**; R1 **1:1106 2:931 3:888 4:75**.
R1 shortens the text by the number of premises, as intended: a 6-line ND proof is at most a
4-`have` text.

**Three of the brief's token predictions are already decided, and two are wrong:**

- R1 predicted 0.75–0.85 → **0.707**, missed low (more premises than the brief assumed: the a1 set
  is 12 % 0-premise, 40 % 1, 43 % 2, 5 % 3).
- R3 predicted 0.70–0.80 → **0.956**, **badly wrong**. The rules whose annotation R3 drops occur on
  only **0.625 lines per proof** in the a1 set (by ND length 2/3/4/5/6: 0.012/0.752/0.479/0.828/1.053).
  R3 is therefore **not a brevity arm**: it saves 4.4 % of tokens, not 20–30 %. I keep it, with the
  hypothesis restated below, and say so in the write-up.
- R2 predicted 1.00–1.05 → **0.915**: `by intro nS` does not write the binder's type, whereas
  `fun ( nS : A ) =>` does, so R2 is *shorter*, not longer. R2 is therefore not a pure box-syntax
  swap; it also removes the binder-type annotation. This is a confound and is declared here.

## Restated hypotheses (what each arm is now a test of)

- **R1 — the horizon.** If the "cap + 1" horizon is a property of the *text* the model writes, R1
  (which makes a 6-line ND proof a ≤ 4-`have` text) should push the ND length at which the model
  can still write proofs up by roughly the mean premise count (1.4). If the horizon lives in the ND
  proof's structure, R1 changes nothing. This is the run's main question.
- **R3 — per-step formula supervision.** lean-only found that a Lean model with *no* `have` lines
  (free-form terms) is 2–5 pp worse in distribution and 15–22 pp worse on transfer pass@16, and
  read this as "the per-step formula is the chain of thought". R3 removes that formula from the
  inference-chain steps only (0.625 lines per proof). It is a small dose of the same manipulation,
  and it is nearly free in tokens, so it is a clean test of whether the *formula* or the *line* is
  what helps.
- **R2 — the nested-lambda mechanism (plus a binder-type confound).** lean-format's untested
  explanation for the Lean base model composing depth 3 from a depth ≤ 2 set is that a nested
  `fun … => by` looks locally the same at every depth. R2 replaces it with a nested `by intro`,
  which also looks the same at every depth, so the *predicted result is a null*; a halving of the
  frozen depth-3 rate would instead support the lambda-form mechanism (or the binder type).

## Design actually run

**Held fixed in every arm, C0 included.** The ND record file; `train.py --steps 6000 --bs 128
--cap 6 --seed {0,1}`; the evaluation pools byte-identical to lean-format's / ladder-A's; sampler
**`path=fast, early=eos, compact=True, rowrng=True`, `batch=2048`, `max_new=400`, temperature
0.8** (the efficiency run's caveat: a batch change reshuffles the accepted set about as much as an
RNG re-draw, so the batch is the *same 2048* in every arm and every stage); reward and counting
**Lean ∧ `nd_verify`** on the literal sampled text through `lean_gate.py` (the brief's protocol
point 4 — `lean_check` alone is validated by lean-only phase 1 but is *not* used here, so all four
arms and the inherited control share one acceptance rule); `nd_verify` and `nd2lean.py`
unmodified.

Per arm, per seed:

1. **Stage-1** (C0: reuse the bucket checkpoints). Held-out greedy on `data/p2/heldout.jsonl`
   (5,000; 1,000 per ND length 2–6), reported overall and by length.
2. **Mechanism test.** `eval_set.py --k 16 --temperature 0.8 --seed 0` on `data/transfer.jsonl`
   (1,638 theorems); distinct start-index-normalised proofs by **written ND length** 7 / 8 / ≥ 9.
3. **Base rates.** `coverage.py --k 2000 --temperature 0.8 --seed 0` on `data/p2/targets_depth3.jsonl`
   (1,000), `data/r3_1/depth3_req.jsonl` (300, required@8) and `data/p2/targets_reductio_req.jsonl`
   (300). Targets hit, per-sample rate, hits by `min_lines_ub` stratum, distinct ≥ 8-line proofs.
   The literal Lean text of the first sample of every counted proof is stored (`proofs[].text`).
4. **Dial.** `expert_iter.py --rounds 4 --k 32 --temperature 0.8` EI and `--no_train` frozen on the
   1,000-target depth-3 pool, arm's own set as `--train`. EI − frozen at round 4.
5. **Ladder.** `ladder_ei.py` T1 and frozen, 8 × 32, pools byte-identical to ladder-A's
   (`transfer.jsonl` sha256 `47dd1886…`, `rl_targets.jsonl` `a5c4c277…`). `L*`, solved, by
   `L_true` bin, textbook solves per schema, held-out greedy at round 8.

All pool lengths (`n_lines`, `min_lines_ub`, `L_true`) are **ND** lengths, identical in every arm.
R1's text length is reported beside them so "8-line" means the same thing in every table.

## Pre-registered expectations (both seeds must agree in sign for a claim)

C0's inherited values (lean-format, same two checkpoints): held-out greedy **0.9086 / 0.8960**;
dial round 4 cumulative solved EI **0.650 / 0.646**, frozen **0.358 / 0.295** (EI − frozen
**+0.292 / +0.351**); ladder on the *full-set* model (a different model) T1 solved 794 / 839,
`L*` 11, frozen 304 / 309, `L*` 10.

| | C0 (predicted for the re-measurement) | R1 | R3 | R2 |
|---|---|---|---|---|
| **E1** held-out greedy, overall | 0.895–0.915 (reproduces the inherited value ±0.5 pp) | **+0.5 to +2 pp** vs C0 | −1.5 to +1 pp | −1 to +1 pp |
| **E2** held-out greedy, 6-line bin | 0.82–0.87 | **+2 to +4 pp** | −2 to +2 pp | −1.5 to +1.5 pp |
| **E3** pass@16 on `data/transfer.jsonl`, distinct 7-line proofs | 130–270 | **×2 to ×3** | ×0.8–1.5 | ×0.8–1.2 |
| **E4** same, 8-line | 50–140 | **×1.5 to ×2.5** | ×0.7–1.5 | ×0.8–1.2 |
| **E5** depth-3 pass@2,000, targets hit / 1,000 | 0.25–0.50 | **+10 to +20 pp** | within ×0.7–1.5 | **within ±5 pp** (null) |
| **E6** `depth3_req` pass@2,000, hit / 300 | 0.05–0.25 | **+10 to +20 pp** | within ×0.7–1.5 | within ×0.7–1.5 |
| **E7** `reductio_req` pass@2,000, hit / 300 | 5–25 | ×1.5–3, ≥ C0 | within ×0.7–1.5 | within ×0.7–1.5 |
| **E8** dial EI − frozen at round 4 (cumulative solved) | +0.20 to +0.35 | within ±0.05 of C0 | within ±0.05 | within ±0.05 |
| **E9** ladder frozen solved / 2,285; frozen `L*` | 150–340; 9–10 | **+20 to +50 %; `L*` +1** | ±15 %; unchanged | ±15 %; unchanged |
| **E10** ladder T1 `L*` | 10–11 | **11–12** | 11 | 11 |

Auxiliary, not primary:
- **E11** Every counted proof in every arm translates with the unmodified `nd2lean.py` and is
  accepted by Lean, and `nd_verify`/Lean agree on 100 % of counted proofs. In-loop
  `nd_verify`-accepted / Lean-rejected samples ≤ 100 per million distinct samples in every arm
  (lean-format measured 33 per million for `lean_seq`).
- **E12** R1's written-ND-length histogram of *accepted* proofs on `data/transfer.jsonl` moves right
  relative to C0 by 1–2 ND lines at the frontier (the length with ≥ 5 distinct verified proofs).

## Falsifiers (the point of the run)

1. **"The horizon is text length" is dead** if R1's distinct 7-line pass@16 count is within ±25 %
   of C0 on **both** seeds. Then the cap + 1 horizon lives in the ND structure, and the
   `--per_len` / cap arms of `ds-composition` are the only levers.
2. **The nested-lambda mechanism is supported** if R2's frozen (base) depth-3 rate at pass@2,000
   **halves** relative to C0 on both seeds. Pre-registered as *not* expected. (If it does halve, the
   binder-type confound above means the cause could be the missing `: A` rather than `fun` itself,
   and the write-up will say so.)
3. **Finding 3 ("RL amplifies what the base does") gets its first counter-example** if some arm has
   a *lower* base rate than C0 (E5) **and** a *larger* EI − frozen (E8), on both seeds.
4. **R3 qualifies** (proposal 10's decision rule) if held-out is within 1 pp of C0 and no readiness
   number is worse, on both seeds.

**Decision rule (proposal 10, unchanged).** An arm replaces the control set for later runs iff, on
both seeds, held-out greedy is within 1 pp of C0 or better *and* at least two of {depth-3
pass@2,000, reductio pass@2,000, ladder T1 `L*` or solved} improve with none worse.

## Budget and stop rules

- **$18 pod budget, 36 pod-hour ceiling** (`podbudget ds-rendering`). RTX 3090 at $0.50/h.
  Planned: four pods, one per arm, ≈ 5.5 pod-hours each ≈ 22 pod-hours ≈ **$11**.
- At most **2 concurrent sampling jobs per 24 GB GPU** (efficiency run; peak ≈ 6 GB per job at
  batch 2048), ≤ 3 jobs per GPU in total.
- `podbudget` is checked between stages; `~/runs/ds-rendering/BUDGET_WARNING` is checked at each
  stage boundary.
- **Drop order if short** (brief): R2's ladder, then R2 entirely, then R3's ladder. Stages run in
  the order 1 → 2 → 3 → 4 → 5 for every arm, so a cut loses the ladder first and never a base rate.
- **Hard stop 2026-09-25 03:01 UTC** (30 h from the session start). Pods deleted when their work is
  pulled; `artifacts/` and `ckpts/` uploaded to the bucket **after each stage**, not only at the end.
- If the projection exceeds the budget, `podbudget --extend` is tried within $18; if refused, the
  question goes to `QUESTIONS.md` with the stated default *drop the ladders of R3 and R2 and finish
  the rest*.

## What would make this run wrong

- A rendering variant whose `inverse` silently disagrees with the renderer would produce ND proofs
  that are not what the model wrote. Guarded by: 3,000-record round-trip per mode (passed, above),
  `train.py --cap 6`'s per-record `decode(encode(proof)) == proof` assertion on all 155,000 records
  at training time, and Lean on the literal text at counting time.
- A grammar that is looser for one arm would let that arm's samples be accepted more easily.
  Guarded by: each variant's grammar fixes *exactly* which lines carry a type and which form a box
  takes; anything else yields `LEANPARSE`. The 300 theorem-swapped negatives are rejected in every
  mode.
- Comparing arms at different sampler batches. Guarded by: batch 2048 everywhere, stated in every
  table.

---

# Addendum, 2026-09-23 22:0x UTC — a fifth arm, **R4 `lean_seq_funbare`**

Written **before the `dsr-r4` pod exists** (`~/pods.log`), after the four Stage-1 arms' held-out
greedy was in and before any of their coverage, dial or ladder results existed. It adds an arm;
it changes no number already pre-registered above.

## Why

The held-out result splits cleanly by the **box depth of the reference proof**
(`artifacts/dsr/summary.json` → `heldout_by_prem_len`, and `log.md` 2026-09-23 21:45):

| held-out greedy | depth ≤ 2 (4,500; in distribution) | depth 3 (500; **f = 0** — the a1 set has 0 depth-3 proofs of 155,000) |
|---|---|---|
| C0 `lean_seq` s0 / s1 | 0.955 / 0.966 | **0.486 / 0.274** |
| R1 `lean_seq_noprem` | 0.948 / 0.944 | 0.232 / 0.218 |
| R3 `lean_seq_nofml` | 0.942 / 0.926 | 0.674 / 0.024 |
| R2 `lean_seq_intro` | 0.955 / 0.964 | **0.822 / 0.746** |

In distribution the four renderings are the same to within 4 pp. **Every difference between them
is zero-shot depth-3 composition**, and R2 — pre-registered as a null and marked "drop first" —
roughly doubles it. That is the **opposite** of falsifier 2 above, which said the nested-lambda
mechanism would be supported by R2's depth-3 rate *halving*.

R2 changes two things at once, as the pre-registration declared: the box syntax (`fun … =>` →
`by intro`) **and** whether the box's hypothesis formula is written twice (once in the discharging
line's annotation, once as the binder's type) or once. R4 separates them.

## The arm

**R4 `lean_seq_funbare`**: boxes are `( fun nS => by … ; exact nE )` — the **`fun` syntax kept**,
the **binder's type dropped** (Lean infers it from the expected type; `inverse` reads it back from
the discharging line's annotation, exactly as in R2). Everything else is C0. Vocabulary **107**
(C0's; R2 needs 108 for `intro`), and the render check gives **mean 76.4 tokens per proof —
identical to R2's 76.4**, so R4 is a length- and vocabulary-matched control for R2.

Render check, run before this commit (`artifacts/dsr/render_check_funbare.json`): round-trip
**3000 / 3000**, Lean accepts **1000 / 1000** literal texts, theorem-swapped negatives **0 / 300**.

Same protocol as every other arm: two Stage-1 seeds, identical 155,000 ND records, 6,000 steps,
bs 128, cap 6, sampler batch 2048 / `max_new` 400 / T 0.8, acceptance Lean ∧ `nd_verify`.

## Pre-registered expectations for R4 (both seeds)

The two hypotheses make disjoint predictions on the depth-3 held-out slice:

| | if the cost is the **binder-type repetition** (R4 ≈ R2) | if the cost is the **`fun … =>` syntax** (R4 ≈ C0) |
|---|---|---|
| **E13** held-out greedy, depth-3 slice (500) | **0.65–0.90** | **0.20–0.55** |
| **E14** held-out greedy overall | 0.930–0.955 | 0.890–0.920 |
| **E15** held-out greedy, depth ≤ 2 (4,500) | 0.94–0.97 either way (no prediction distinguishes them) | |
| **E16** depth-3 pass@2,000 on `targets_depth3` | within ×0.8–1.25 of R2 | within ×0.8–1.25 of C0 |

**My prediction: the binder-type column** — R4 lands in 0.65–0.90 on E13 on both seeds. The reason:
`lean_seq` must re-emit the hypothesis formula at the binder after having written it in the
annotation, and at depth 3 those spans nest, so three formulas must each be reproduced twice
across an interleaved span; `intro` and bare `fun` each write it once.

**If R4 splits the seeds, or lands between the bands (0.55–0.65), the run reports the mechanism as
unresolved** and names the 2 × 2 that would settle it ({`fun`, `intro`} × {typed, untyped} — the
fourth cell, `by intro nS` *with* a type, has no Lean syntax, so the missing cell would have to be
`fun ( nS : A ) => by` against `fun nS => by` at a *matched token count*, which R4 vs C0 is not).

**Budget.** One more A40 ($0.49/h), the same job plan as the other arms, ≈ 5 pod-hours ≈ $2.50.
Projected total 25 of 36 pod-hours, ≈ $12.50 of $18. The drop order becomes: R2's ladder, then
**R4's ladder**, then R2, then R3's ladder.

---

# Addendum 2, 2026-09-23 22:0x UTC — a Stage-1 **seed sweep**, because R4 split the seeds

Written **before the `dsr-s` pod exists** (`~/pods.log`), immediately after R4's held-out result and
before any coverage, dial or ladder result for any arm. It adds seeds; it changes no number
already pre-registered.

## What happened

R4's depth-3 held-out slice (500 theorems, f = 0, greedy) is **0.788 / 0.440**. Addendum 1
pre-registered two disjoint bands — 0.65–0.90 if the cost is the binder-type repetition,
0.20–0.55 if it is the `fun … =>` syntax — and said in as many words: *"if R4 splits the seeds …
the run reports the mechanism as unresolved."* Seed 0 lands in the first band, seed 1 in the
second. **The mechanism is unresolved at n = 2, and I am reporting that.**

The full picture at n = 2 (held-out greedy, `data/p2/heldout.jsonl`):

| arm | in distribution (box depth ≤ 2, 4,500) | **depth-3 slice (500, f = 0)** | seed gap | grammar violations at depth 3 |
|---|---|---|---|---|
| C0 `lean_seq` | 0.955 / 0.966 | 0.486 / 0.274 | 0.21 | 164 / 296 |
| R1 `lean_seq_noprem` | 0.948 / 0.944 | 0.232 / 0.218 | 0.01 | 324 / 283 |
| R3 `lean_seq_nofml` | 0.942 / 0.926 | 0.674 / **0.024** | **0.65** | 107 / 420 |
| R2 `lean_seq_intro` | 0.955 / 0.964 | **0.822 / 0.746** | **0.08** | **12 / 42** |
| R4 `lean_seq_funbare` | 0.959 / 0.967 | 0.788 / 0.440 | 0.35 | 30 / 173 |

The obstacle is **Stage-1 seed variance in the depth-3 cell**, which is large for every rendering
that writes a box as a lambda (C0 0.21, R3 0.65, R4 0.35) and small for the one that does not
(R2 0.08). Two seeds cannot separate "R2 beats R4" from that variance. Four more seeds can, for
about $0.80 — 1.5 % of this run's budget — so it is worth doing rather than reporting a shrug.

## The sweep

`train.py --mode <arm's mode> --steps 6000 --bs 128 --cap 6 --seed {2,3,4,5}` on the **same**
155,000 ND records, then `eval_set.py` greedy on `data/p2/heldout.jsonl` — Stage-1 and held-out
only, nothing else. Arms **C0, R3, R2, R4** (R1 is excluded: its two seeds agree to 0.01 and it is
worse than the control everywhere, so more seeds would not change a conclusion). 16 Stage-1 runs
on one new A40, two at a time, ≈ 1.6 pod-hours ≈ **$0.80**. Everything else about the models,
data and sampler is unchanged. With the two seeds already in hand this gives **n = 6 per arm**.

## Pre-registered expectations (over the 6 seeds of each arm)

- **E17** Mean depth-3 slice rate: **R2 > R4 > C0 ≈ R3**, with `mean(R2) − mean(C0) ≥ 0.25`.
- **E18** R2's across-seed standard deviation on the depth-3 slice is the **smallest of the four**
  and is **< 0.10**; C0's, R3's and R4's are each **> 0.12**.
- **E19** Mean in-distribution (depth ≤ 2) accuracy is within **2 pp** across all four arms — i.e.
  the rendering still buys nothing in distribution, whatever it does out of it.
- **E20** Across all 24 models, the depth-3 slice rate and the count of grammar violations at
  depth 3 are strongly negatively related (Spearman ρ ≤ −0.8): the depth-3 gap *is* the
  bookkeeping gap, not a difference in logical competence.

**Decision rule for the mechanism.** Let `s` be the pooled across-seed standard deviation of the
depth-3 slice rate. If `mean(R2) − mean(R4) > s`, the `by intro` syntax contributes **beyond**
dropping the binder type. If `|mean(R2) − mean(R4)| ≤ s`, dropping the binder type accounts for
the effect and the `fun`-vs-`intro` choice does not. Either way the comparison of both against C0
is the reportable result. **If E18 holds but E17 does not, the finding is about variance, not
level**, and the write-up will say that instead.
