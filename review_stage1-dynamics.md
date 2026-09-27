# Review — run `stage1-dynamics`

Reviewer: agent:claude, a separate session from the executor. `AGENT_POLICY.md` (nd-rl canonical
copy) governs. Phase 1 was done in `~/review/stage1-dynamics`, a copy of the run's repository with
every write-up removed (`run*.md`, `numbers.md`, `STATUS*.md`, `campaign.md`, `followup.md`,
`ignition.md`, `phase*.md`); I had the run brief
(`~/nd-rl/docs/proposals/followups/BRIEF_stage1-dynamics.md`),
`preregistration/stage1-dynamics.md` and its two addenda, the code, the data and the raw artefacts.
Every number in §Recount comes from code I wrote myself
(`review_sd_slices.py`, `review_sd_pick.py`, `review_sd_lean.py`, `review_sd_controls.py`,
`review_sd_splits.py`, `review_sd_expect.py`) — my own start-index/name normalisation, my own
box-depth counter, my own line counter, my own Wilson interval, my own Spearman, my own
renaming-class canonicaliser, my own Lean driver. `nd_verify` is used nowhere in this review.

**The model every number below is about** (unchanged from the pre-registration, and I verified it
from each checkpoint's own stored `train_args`): a **3,214,336-parameter from-scratch GPT**
(4 layers, d 256, 8 heads), Lean surface format **`lean_seq`**, **cap 6**,
`--bs 128 --lr 1e-3 --min_lr 1e-4 --warmup 200`. Arms C / W / W-6k / W-12k / R train on
`data/p2/train_depth3_f0_a1.jsonl` (155,000 records); arm F on `data/sd/train_fresh.jsonl`
(572,759). Judge: **Lean alone** (Lean 4.34.1), per Dan 2026-09-27.

---

## §Recount

### 0. Hard constraints

| constraint | my check | verdict |
|---|---|---|
| `nd_verify` unmodified | `git rev-parse HEAD:nd_verify` = `9437bb72…` = `origin/main:nd_verify` = `origin/dan:nd_verify`; `git diff origin/main HEAD -- nd_verify` empty | **pass** |
| `nd_verify` not used as a judge | absent from `sd_eval.py`, `sd_passk.py`, `pod/sd/*`. `sd_eval` imports only `lean_gate.lean_check`, which never calls it; `sample.generate(gate=False)` returns the literal texts and never reaches `lean_gate.gate()` (the only nd_verify caller). Every one of the 275 result files records `"judge": "lean_alone"` | **pass** |
| `artifacts/TEST_RUN_DONE` unchanged | blob `1d5cf064…` at HEAD = at `origin/main` | **pass** |
| no evaluation file read in training code | `data/p2/heldout.jsonl` **is** read by `train.py` — as the validation file, which is the point of the run. I traced every use: `loss.backward()` runs only on `loss_on(model, *batch(data, …))` from `--data`; the `val2k` and `--val_bins` passes are both inside `torch.no_grad()`; no checkpoint is selected on any validation number (step counts are fixed, the final checkpoint is saved unconditionally). No gradient and no selection from the eval pool | **pass, with the read disclosed** |
| `train.py`'s default behaviour unchanged | the run deletes only 5 lines of `train.py`. The old cosine lambda is replaced by `lr_at(a, s)`, which for `--sched cosine` is algebraically the same expression; `range(1, steps+1)` becomes `range(step0+1, steps+1)` with `step0 = 0` when not resuming; the rest is additive and gated on new flags. With the new flags unset the rng draw sequence is identical | **pass** |
| take-home cap 6 | every checkpoint's `train_args.cap` is 6; `train.py`'s loader asserts `n_lines <= 6` on every training record | **pass** |
| no hand-written or LLM-written training proofs | both training sets are generator output (`data/nf/train_p{1..4}.jsonl` → `sd_pool.py`; `data/p2/…` inherited); `train.py` re-verifies every training record's ND proof with `nd_verify` at load (a data-validity assertion, pre-existing in `origin/main`, not a judge of model output) | **pass** |

No quarantine condition fires.

### 1. Every counted quantity recomputed from the raw per-record files

`review_sd_slices.py` re-derives all 275 result files (`artifacts/sd/ev/*.json`, 47 final +
228 trajectory) from their own `*.jsonl[.gz]` — **1,375,000 per-record verdicts** — using my own
slice definitions, my own Wilson interval and my own term-size and written-line means. I also
re-derived the slice membership itself: my own ND-proof line counter and my own box-depth counter,
run over `data/p2/heldout.jsonl`, agree with the pool's stored `n_lines` on **5,000/5,000** records
and with its stored `pat.depth3` on **5,000/5,000**.

- My slice sizes: `all` 5,000, `len2…len6` 1,000 each, `depth3` 500 (all of them 6-line, max box
  depth exactly 3), `nodepth3_len6` 500. Matches the pre-registration.
- **0 disagreements** with the run's own `.json` across all 275 files, on every field I checked:
  `solved`, `n`, `mean_term_size`, `mean_written_lines`, `parse_fail`, `lean_rej_of_parsed`.
- No record anywhere is `lean_ok` without being `parsed` (0 of 1,375,000), so the "strict grammar
  **and** Lean" conjunction was actually applied.
- The run's separate checker cross-check (`artifacts/sd/xcheck/`) also reproduces exactly under my
  counting: `ckpts/nf/stage1_p1_s0.pt` 4,365/5,000 = 0.8730 and `stage1_p1_s1.pt` 4,682/5,000 =
  0.9364 under Lean alone, against 0.8726 and 0.9362 for the **same checkpoints** under
  Lean ∧ `nd_verify` in `artifacts/nf/summary.json` — i.e. **+400 and +200 per million** on held-out
  greedy. See finding F5 on how that number is labelled.

### 2. Lean re-check of counted proofs (my own harness)

`review_sd_lean.py` builds the Lean theorem statement from the held-out record with my own
ND→Lean formula translator (I never call `lean_tok.statement`), pairs it with the **stored literal
sampled text**, sends it to Lean 4.34.1 core, and requires both that Lean reports no error and that
`#print axioms t<k>` shows a subset of `{propext, Classical.choice, Quot.sound}` — so a `sorry`
proof could not pass my check even if it passed the run's. A batch that is not wholly clean is split
recursively to singletons.

I validated the harness first (`review_sd_controls.py`), because a clean result from a broken
checker is worthless — and the controls did catch a renumbering bug in my own recursive split,
which I fixed before the real pass:

| control | n | my verdict |
|---|---|---|
| untouched counted proofs | 60 | **60 accepted** |
| samples the run itself recorded as parsed-but-Lean-rejected | 60 | **60 rejected** |
| counted proofs corrupted by one `Or.inl`↔`Or.inr` / `.1`↔`.2` flip | 27 | **26 rejected**; the 1 acceptance is a genuine no-op (`Or.inl` vs `Or.inr` into `P ∨ P`) |
| a counted proof paired with a *different* theorem of the same premise count | 40 | **40 rejected** |
| `sorry` | 10 | **10 rejected** |

Then the real pass, stratified over seeds and over all six reported slices:

| arm | checkpoints drawn from | proofs re-checked | Lean rejections |
|---|---|---|---|
| C (cosine 6k) | 8 (c_s0…c_s7) | 120 | **0** |
| W-6k | 8 | 120 | **0** |
| W-12k | 8 | 120 | **0** |
| W-24k | 8 | 120 | **0** |
| F (fresh, 24k) | 4 | 120 | **0** |
| pass@8 accepted samples | 4 | 133 | **0** |
| **R (replicates)** | — | **0 — impossible, see F1** | — |
| total | | **733** | **0** |

Because I rebuild each statement from the held-out record carrying that `name`, the 733 acceptances
also confirm that each stored proof is credited to the theorem it actually proves.

### 3. Splits, by renaming class

My canonicaliser takes the lexicographic minimum, over all 24 bijections of `{P,Q,R,S}`, of
(sorted premise multiset, conclusion) — a true canonical form for the sequent. The project's own
`gen.canon_key` relabels atoms by first appearance **in the theorem string**, so it is sensitive to
the order the premises are written in. Under my key:

| pair | collisions (my key) | the run's claim |
|---|---|---|
| `train_depth3_f0_a1.jsonl` × `heldout.jsonl` | **21 held-out theorems** hit by 22 training records | 0 (asserted in `make_splits.py`) |
| `train_fresh.jsonl` × `heldout.jsonl` | **66 held-out theorems** | 0 (`data/sd/pool_fresh.json`) |
| either training file × the **depth-3 slice** | **0** | 0 |
| `heldout.jsonl` with itself | 2 records are one class (`heldout_3465`, `heldout_3912`) | 5,000 distinct |

Every collision I found is a pair of the *same sequent* with the premises written in the other
order, e.g. train `( R v P ) > ( S & F ) , ( R v P ) ⊢ ( S & F )` against
`heldout_1210 = ( R v S ) , ( ( R v S ) > ( Q & F ) ) ⊢ ( Q & F )`. So this is a property of the
project's key, not of this run's construction — but the run re-asserts "0 records collide with a
held-out class", and that is true only under the order-sensitive key.

**Bounded impact.** Mean solve rate on the leaked held-out theorems vs the rest, and the effect of
including them in the overall rate:

| arm | leaked held-out theorems | rate on them | rate on the rest | effect on the overall rate |
|---|---|---|---|---|
| control-trained (C, W, W-6k, W-12k, R), 16 checkpoints | 21 | 0.961 | 0.9315 | **+0.013 pp** (max +0.055) |
| fresh-trained (F), 4 checkpoints | 66 | 0.992 | 0.9322 | **+0.079 pp** (max +0.136) |

At most **+0.14 pp** on any reported rate, and exactly **0** on the depth-3 slice, which carries the
headline. No conclusion of this run moves.

I also reproduced the fresh-set construction from the four source pools. Record counts, length bins
and shares match `data/sd/pool_fresh.json` exactly (572,759 records; 18.35/20.39/20.42/20.35/20.49 %
at lengths 2/3/4/5/6; 0 records with a box depth ≥ 3, max box depth 2 — so "depth-3 excluded" holds
for both training sets under my own depth counter). Under my coarser key the same construction
yields 568,824 classes and 84 held-out collisions rather than 572,759 and 0 — the whole difference
being premise order, as above. Epoch arithmetic checks out: control 6,000 × 128 / 155,000 = **4.955**
epochs, fresh 24,000 × 128 / 572,759 = **5.364**.

### 4. Premises the run reads itself against

All quoted from `noise-floor`'s 52 cells under **Lean ∧ `nd_verify`**; recomputed by me from
`artifacts/nf/summary.json`:

| premise | pre-registration | my recount | verdict |
|---|---|---|---|
| overall held-out | 0.907 ± 0.030 | 0.9072 ± 0.0304 | reproduces |
| 6-line bin | 0.667 ± 0.152 | 0.6674 ± 0.1523 | reproduces |
| 5-line bin | 0.927 ± 0.015 | 0.9272 ± 0.0150 | reproduces |
| depth-3 slice | 0.440 ± 0.305, 24/52 above 0.44 | 0.4402 ± 0.3053, 24/52 | reproduces |
| 6-line non-depth-3 | 0.824 ± 0.037 | that is `noise-floor`'s `len6_none`, **n = 247** (6-line proofs with *no* pattern at all), not the n = 500 non-depth-3 complement this run reports. The n = 500 slice is 247 pattern-free + 253 other-pattern records and its `noise-floor` value is **not derivable** from the pulled artefacts (no per-record held-out verdicts in `artifacts/nf/`) | **mislabelled premise (F4)** |
| gate boundary | "≈ 67 per million on held-out greedy" | 67.15 per million is right, but it is over the 12,033,100 distinct (prompt, text) pairs `noise-floor`'s **in-loop gate** saw, not over held-out greedy. On held-out greedy the run's own `xcheck` measures **+200 to +400 per million** | **mislabelled population (F5)** |
| `train.py`'s old validation loss sees only short proofs | brief's premise | `data/p2/heldout.jsonl` is sorted by `n_lines` and its first 2,000 records are exactly 1,000 × 2-line + 1,000 × 3-line | reproduces |
| depth-3 slice is half the 6-line bin | brief's premise | 500 of 1,000, all 6-line | reproduces |

### 5. Term size and written lines, re-derived

The run's `mean_term_size` is `len(text.split())` and its `mean_written_lines` is
`count('have') + 1`. Both reproduce exactly under my own code on all 275 files. Two things about
what they mean:

- A second, deliberately different measure — content tokens only, dropping
  `have ; : := ( ) fun => by exact ⟨ ⟩ ,` — is 0.42–0.43 × the run's number on every arm and slice I
  checked (e.g. `w_s1` len6: 136.63 → 55.41; `c_s1` len6: 133.72 → 54.31), and preserves every
  ordering between arms. **Any comparison the run makes on term size is robust to the choice**;
  the absolute value is a surface token count of the tactic script, not a count of nodes in the
  elaborated term.
- `count('have') + 1` is **not** the ND line count. A box assumption line becomes a
  `fun (n : A) =>` binder, not a `have`, so a 6-line depth-3 proof reports 4.000 written lines —
  which is exactly what every depth-3 slice reports (3.999–4.067 on every checkpoint I looked at).
  Against the reference proof's `n_lines`, the counted proofs of `w_s1` are *longer* on this measure
  2,396 times, equal 1,632 and shorter 909. Reporting it as "written lines" invites reading it as an
  ND line count; it undercounts by the number of box assumptions (F7).

### 6. Gate 0 — expectations before outcomes

From git commit times and artefact/metrics timestamps, independent of `log.md`:

| record | committed | first outcome it covers | verdict |
|---|---|---|---|
| `preregistration/stage1-dynamics.md` | 2026-09-27T**18:05:40**Z | first pod `sd-1` 18:15:50Z (`~/pods.log`) | **before** |
| addendum 1 (arm R) | 18:**30:46**Z | `r6a_s0` training started 18:31:52Z (`m_r6a_s0.jsonl`), `r24a_s0` 18:34:10Z, first arm-R evaluation 19:55Z | **before** |
| addendum 2 (pass@8) | 20:**17:39**Z | the four `artifacts/sd/passk/` files 20:18:52–20:19:59Z | **before** |

Addendum 2 states on its face that it was written after arm F's trajectories were seen; it
pre-registers only the pass@8 measurement, whose outcomes did not exist. That is legitimate.
Budget: `podbudget` reports **8.74 h / $4.29** against a 30 h / $15 ceiling; `rpbalance` $142.65,
above the floor; no `sd-*` pod remains on the account.

### 7. Every pre-registered expectation, recounted

`review_sd_expect.py`; full output in `review_sd_expect.txt`. "hit"/"miss" is against the
pre-registration's own stated band, not against my judgement of the result.

#### Q1 saturation

| # | pre-registered | my recount | |
|---|---|---|---|
| E1 | median(W-24k − W-6k) on the 6-line bin = +12 pp (band +5…+25), ≥ 7/8 seeds > +2 pp | **+16.1 pp**; **7/8** seeds > +2 pp (s2 −2.3 pp). Falsifier fires on **0/8** seeds (needs 6/8) | **hit** |
| E2 | cross-seed sd of the 6-line bin falls from 0.152 at 6k to **< 0.10** at 24k | W-6k **0.1648** → W-24k **0.1579**. It does not fall | **miss** |
| E3 | median overall gain +3…+5 pp, landing near 0.945 | **+5.0 pp**; mean W-24k overall **0.9528** | **hit** |
| E4 | 2- and 3-line bins move < 1 pp | len2 median +0.2 pp (max 0.60); len3 median **+1.1 pp** (max 1.70) | len2 hit, **len3 marginal miss** |
| E5 | 6-line val loss at 24k below its 6k value in ≥ 7/8; **no** seed ends > 2 % above its own minimum | below in **8/8**. But **5/8** seeds end > 2 % above their own minimum (s0 **+108.6 %**, s7 +34.3 %, s3 +13.7 %, s6 +10.3 %, s2 +8.6 %) → **the falsifier of "long-proof loss keeps falling" fires** (needs ≥ 3/8) | first clause hit, **falsifier fires** |
| E6 | \|Δval2k\| < 0.01 in ≥ 6/8 while the 6-line bin moves ≥ 5 pp | **8/8** seeds have \|Δval2k\| ≤ 0.0027; **6/8** of those also move ≥ 5 pp on len6 | **hit** |

E5's falsifier was written to catch a *memorisation turn-up*. That is not what fired. `w_s0`'s
6-line validation loss oscillates for the whole run and keeps oscillating **inside the decay
phase** — 0.0355 at 20,400, 0.0854 at 21,000, 0.0740 at 24,000 — so seeds end above their minimum
because the curve never settles, not because it turns up. The distinction matters for what the run
may conclude (see §Verdict).

#### Q2 when the depth-3 mode is decided

| # | pre-registered | my recount | |
|---|---|---|---|
| E7 | high mode (> 0.44) in 3–5/8 at 6k and **7 or 8**/8 at 24k; ≥ 2/8 change mode after 6k | **4/8** at W-6k ✓; **6/8** at W-24k ✗; **4/8 change mode** (s3 high→low, s5 s6 s7 low→high) ✓ | headline **hit**, the 24k count **miss** |
| E8 | no seed regresses: d3(24k) ≥ d3(6k) − 5 pp for all 8 | **s2 regresses**: 0.732 → 0.640 (−9.2 pp) | **miss** |
| E9 | Spearman \|ρ\| (d3 at step 2,000 vs at 24k) < 0.6 | **ρ = −0.398** | **hit** |

Per-seed depth-3 with my own Wilson intervals on 500 records (W-6k → W-12k → W-24k):
s0 0.014→0.124→0.060, s1 0.568→0.804→0.942, s2 0.732→0.020→0.640, s3 0.448→0.042→0.404,
s4 0.782→0.886→0.920, s5 0.100→0.120→0.942, s6 0.006→0.028→0.492, s7 0.092→0.086→0.470.
W-12k is **not** between W-6k and W-24k for s2, s3, s5, s6 — the trajectory is non-monotone in the
same way arm F's is.

#### Q3 schedule at equal steps

| # | pre-registered | my recount | |
|---|---|---|---|
| E10 | median \|Δ\| ≤ 3 pp on the 6-line bin and ≤ 1.5 pp overall, ≤ 6/8 seeds in one direction; falsifier at > 5 pp or 8/8 | median \|Δ\| len6 **5.15 pp**, overall **1.71 pp**; **4/8** seeds each way; signed medians −2.3 pp and −0.3 pp; per-seed len6 Δ ranges from **−33.4 pp** (s0) to **+4.3 pp** (s2) | **the falsifier fires, marginally**, on the median-\|Δ\| clause; the sign-test clause holds |

#### Q4 steps or repetition

| # | pre-registered | my recount | |
|---|---|---|---|
| E11 | F's 6k→24k gain on the 6-line bin ≥ 0.6 × W's; falsifier < 0.5 | median W gain **+31.6 pp**; median F gain **−0.1 pp** (per seed +53.8, −17.3, +8.6, −8.8) → ratio **≈ 0.00** → **falsifier fires** | **miss** |
| E12 | F-24k − W-24k on len6 = +2…+8 pp, not > +15 pp | per seed **+43.5, −39.0, −30.1, +0.6 pp**; median **−14.8 pp** | **miss** |
| E13 | F's per-bin val loss higher than W's at 24k in ≥ 3/4 seeds while accuracy is equal or better | bins where F's loss is higher: 1/5, 3/5, 2/5, 2/5 → **0/4 seeds** on all five bins; and F's accuracy is *lower* than W's on 2 of 4 seeds | **miss** |

#### Q5 per-length loss as a proxy

| # | pre-registered | my recount | |
|---|---|---|---|
| E14 | pooled ρ(len6 loss, len6 acc) ≤ −0.85 and ≤ −0.80 **within every seed**; ρ(depth3) ≤ −0.80 | pooled **−0.885** over 8 × 24 = 192 checkpoints ✓; depth-3 pooled **−0.893** ✓. Within seed: −0.857, −0.961, −0.822, −0.826, −0.977, −0.906, **−0.657 (s6)**, −0.899 → **s6 fails the within-seed clause**; depth-3 within seed, **s3 = −0.789** also just fails | pooled **hit**, within-seed **miss on 1 of 8** |
| E15 | across 8 seeds at step 24,000: \|ρ(val2k, len6 acc)\| < 0.5 and \|ρ(len6 loss, len6 acc)\| > 0.8 | **−0.310** and **−0.905** | **hit** |
| E16 | per-bin validation costs 5–9 % of training wall time | **4.2–4.9 %** on all 20 runs (W 4.5–4.7 %, C 4.2–4.9 %, F 4.4–4.5 %) | **miss, cheaper than expected** |

#### Addendum 1 — the same-command replicate floor

Five runs of the identical command at each of two seeds, and three at 24,000 steps:

| set | 6-line bin | sd | overall sd | depth-3 | above 0.44 |
|---|---|---|---|---|---|
| seed 0, 6k (n = 5) | .802 .490 .609 .656 .664 | **0.1123** | 0.0169 | .736 .064 .310 .436 .416 | 1/5 |
| seed 1, 6k (n = 5) | .789 .589 .843 .804 .776 | **0.0989** | 0.0191 | .700 .280 .800 .720 .660 | 4/5 |
| seed 0, 24k (n = 3) | .519 .803 .554 | **0.1549** | 0.0299 | .060 .638 .148 | 1/3 |

| # | pre-registered | my recount | |
|---|---|---|---|
| E17 | per-seed sd of len6 in 0.03–0.10 and of overall in 0.005–0.020; falsifier len6 sd < 0.01 in both | len6 **0.1123** (s0, just above the band) and **0.0989** (s1, in band); overall **0.0169** and **0.0191**, both in band. Falsifier does not fire | **hit on overall, just over the band on len6** |
| E18 | the depth-3 slice straddles 0.44 within at least one seed's replicates | **both** seeds straddle it: s0 spans 0.064–0.736, s1 spans 0.280–0.800 | **hit, strongly** |
| E19 | at 24k the three replicates' 6-line spread is **no larger** than at 6k | sd **0.1549** at 24k against 0.1123 / 0.0989 at 6k — larger. Range 0.284 against 0.312 / 0.254 — comparable. n = 3 vs n = 5 | **miss (and underpowered)** |

#### Addendum 2 — pass@8 at loss troughs and peaks

| checkpoint | greedy (my count, pass@k file) | greedy (my count, ev file) | pass@8 | mean per-sample |
|---|---|---|---|---|
| `f_s1.step08000` (loss trough 0.0330) | 0.806 | 0.806 | **0.892** | 0.733 |
| `f_s1.step14000` (loss peak 0.0719) | 0.016 | 0.018 | **0.392** | 0.085 |
| `f_s0.step12000` (loss peak 0.1343) | 0.016 | 0.016 | **0.026** | 0.012 |
| `f_s0.step14000` (loss trough 0.0324) | 0.668 | 0.666 | **0.884** | 0.675 |

| # | pre-registered | my recount | |
|---|---|---|---|
| E21 | reading (i): pass@8 moves with greedy by ≥ 20 pp on ≥ 3 of the 4 ordered comparisons, and the low-greedy checkpoint stays < 0.60 at pass@8. Falsifier of (i): pass@8 differs < 10 pp in **both** pairs while greedy differs > 40 pp | pass@8 moves **−50.0 pp** and **+85.8 pp**, same sign as greedy in both pairs, ≥ 20 pp on **4/4** ordered comparisons; low-greedy checkpoints at pass@8 are **0.392** and **0.026**, both < 0.60. The falsifier does not fire | **hit** — reading (i), a real capability oscillation |
| E22 | pass@8 > greedy at all four checkpoints | 0.892 > 0.806, 0.392 > 0.018, 0.026 > 0.016, 0.884 > 0.666 — **4/4** | **hit** |

The two greedy readouts of the same checkpoint (the pass@k file's `greedy_ok` and the trajectory
evaluation's `depth3` rate, sampled independently) agree to within 0.002 on all four checkpoints,
which is a clean internal consistency check on the sampler.

### 8. Findings from §Recount

- **F1 — arm R's counted proofs cannot be re-checked in Lean from the pulled files.** `pod/sd/jobs.py`
  runs `sd_eval.py` **without `--texts`** for every arm-R evaluation (`ev_r6*`, `ev_r24`), so
  `artifacts/sd/ev/r6{a…d}_s{0,1}.jsonl` and `r24{a,b}_s0.jsonl` store verdicts but no literal proof
  text. The same is true of all 228 trajectory evaluations. I re-verified 733 counted proofs across
  the five arms that do store text and 0 were rejected, but for arm R — which carries E17–E19 and,
  through them, the licence for every cross-run claim in the run — **not one counted proof is
  independently checkable**. No torch is installed on this VPS, so I could not regenerate them.
  Remedy is cheap and needs no training: re-run `sd_eval.py --texts` on the ten arm-R checkpoints,
  which are pulled and uploaded (≈ 1 GPU-minute each).
- **F2 — "0 records collide with a held-out class" is true only under a premise-order-sensitive key.**
  Under a true renaming-class canonical form, 21 held-out theorems are in the control set's class
  and 66 are in the fresh set's; 2 held-out records are the same sequent as each other. Impact is
  bounded at **+0.14 pp** on any rate and **0** on the depth-3 slice. Pre-existing in
  `gen.canon_key`; the run inherits and re-asserts it.
- **F3 — E5's falsifier fired for a different reason than it was written for.** 5/8 seeds end more
  than 2 % above their own minimum 6-line loss, but the mechanism is a loss that oscillates
  throughout, including inside the LR decay, not a memorisation turn-up.
- **F4 — the "6-line non-depth-3 0.824 ± 0.037" premise is a different slice** from the n = 500
  complement this run reports (it is `noise-floor`'s n = 247 pattern-free 6-line records). The
  correct baseline for the n = 500 slice is not derivable from the pulled artefacts.
- **F5 — the gate boundary is quoted over the wrong population.** "≈ 67 per million on held-out
  greedy" is a number measured over 12 M in-loop gate samples. The run's own `xcheck` measures the
  held-out-greedy boundary at +200 to +400 per million (2 and 1 extra theorems in 5,000). Both are
  negligible; the label should say which is which.
- **F6 — E19 is underpowered and reads the wrong way.** n = 3 at 24,000 steps against n = 5 at 6,000;
  the 24k sd is larger, not "no larger".
- **F7 — `mean_written_lines` is not an ND line count.** It counts `have` tactics plus one, so box
  assumption lines are invisible and every depth-3 slice reports ≈ 4.0 written lines for 6-line
  theorems.

---

## §Compare

Read after §Recount was committed (`8f47cb90`). Sources compared: `run_stage1_dynamics.md`
(400 words of body, 416 with the title — inside the brief's ≤ 400), `numbers.md` § stage1-dynamics
(S1–S11), `log.md`, `artifacts/sd/summary.json`, `sd_tables.py`'s output.

### The write-up's claims

| claim (`run_stage1_dynamics.md`) | my independent value | verdict |
|---|---|---|
| "All five bins cost **4.7 %** of training time" | 4.70 % median over the 46 full-length runs from the checkpoint-recorded wall times, 4.50 % from the metrics files' last logged step | **reproduces** (see R5 for the population the range is quoted over) |
| Q1: 6k → 24k moves the 6-line bin by a median **+16.1 pp** (7/8 seeds) | **+16.1 pp**, 7/8 seeds > +2 pp | **reproduces** |
| …and depth-3 by **+25.6 pp** | **+25.6 pp** | **reproduces** |
| …2- and 3-line move **+0.2 and +1.1 pp** | +0.2 and +1.1 pp | **reproduces** |
| "The falsifier needed 6 of 8 seeds flat. **None** were." | 0/8 | **reproduces** |
| Q2: "All twelve 24,000-step runs visit both modes" | 12/12: every run's trajectory min < 0.44 and max > 0.44 (mins 0.004–0.038, maxima 0.488–0.934) | **reproduces** |
| …"spans ≈ 0.01 to 0.49–0.92 and crosses the 0.44 cut **1–10 times**" | crossings 1–10 over the 18 checkpoints at steps ≥ 6,000 (1–11 if the final checkpoint is included) | **reproduces** |
| …"Checkpoints sit in the high mode **37 %** of the time against `NOISE_FLOOR.md`'s 0.462 across 52 *runs*" | 0.37 (mean of the twelve per-run fractions over 18 checkpoints each); 24/52 = 0.4615 | **reproduces**; needs the checker label (R8) |
| …"pass@8 moves with it (0.892 → 0.392 and 0.026 → 0.884)" | identical | **reproduces** |
| "Arm R … the 6-line bin spans **0.490–0.802**, depth-3 **0.064–0.736**" | identical | **reproduces** |
| "Three same-command runs at 24,000 steps **reproduce nearly the whole** 52-cell floor (6-line sd 0.155 vs 0.152; depth-3 0.311 vs 0.305)" | the four sds are exact. But n = 3 gives a 95 % CI on the sd of **[0.081, 0.973]**; the n = 5 groups give [0.067, 0.323] and [0.059, 0.284]; the 52-cell 0.1523 has [0.128, 0.191]. All three contain it | numbers reproduce, **wording overstated (R4)** |
| Q3: "C and W-6k see identical batches" | verified by reading `train.py`: `lr_at` does not touch the rng; `--ckpt_every`/`--state_at` only trigger saves; the `val2k` block consumes the rng identically in both arms at every logged step; `--val_bins` uses its own `Random(12345)`; `--resume` restores `perm` and all three rng states after step 4,800's logging | **reproduces** |
| …"median Δ −0.3 pp overall, −2.3 pp at 6 lines, 4/8 each way, inside that floor" | −0.3 pp, −2.3 pp, 4/8 | **reproduces**; the resolution should be stated (R2) |
| Q4: "steps, not data … match on every trajectory-robust estimator (best depth-3 loss **0.0286 vs 0.0283**, best rate **0.823 vs 0.820**)" | 0.0286 vs 0.0283 and 0.823 vs 0.820, both under "best over the trajectory checkpoints, excluding the final decayed one" | numbers **reproduce**; the claim is **not supported as stated (R1)** |
| "572,759 fresh proofs (5.4 epochs) … 155,000 seen 19.8 times" | 5.364 and 19.82 epochs | **reproduces** |
| Q5: Spearman **−0.905** (6-line) and **−0.934** (depth-3) against **−0.310** for `val2k` across 8 seeds at 24,000 | −0.905, −0.934, −0.310 | **reproduces** |
| …"`val2k` moved 0.002 all run while the 6-line bin moved up to 45 pp" | \|Δval2k\| 0.0015–0.0027; max len6 move +45.0 pp (s5) | **reproduces** |
| "**10 met, 6 partly, 6 missed**" | my own scoring of the same 22, §Recount §7: 9 clear hits, 1 hit whose sibling clause fails, 6 partial, 6 misses — the same verdicts modulo where E7 and E13 are placed | **reproduces** |
| "**8.74 pod-hours, $4.29** of 30 h / $15; four A40s, real rate $0.49/h, deleted" | `podbudget` 8.74 h / $4.29; `runpodctl pod list` has no `sd-*` pod; `sd-4` billed $0.93 for 1.8964 h = $0.490/h | **reproduces** |

### `numbers.md` claims that do not reproduce

| § | claim | my value | verdict |
|---|---|---|---|
| S9 | proof length: C 85.4 / 4.16 / **122.5** / 5.23; W-6k 84.0 / 116.2 / 5.41; W-12k 83.6 / 113.9 / 5.52; W-24k 87.1 / 127.3 / 5.10 | C **86.4 / 4.15 / 126.7 / 5.13**; W-6k **84.5 / 4.17 / 118.4 / 5.36**; W-12k **83.9 / 4.19 / 115.3 / 5.49**; W-24k **86.8 / 4.19 / 125.8 / 5.16**. These are also exactly what the run's own `summary.json` holds and what `python3 sd_tables.py` prints today. The F-24k row is correct | **differs — a transcription error in the write-up, not in the analysis** (R6) |
| S8 | table headed "Spearman ρ, **arm W**", with an "at 6,000" column: −0.952 / −0.857 / −0.333 / −0.571 | those four are arm **C** (`sd_analysis.py` line 338: `(6000, ('C',))`), which I reproduce exactly. Arm W's own step-6,000 trajectory point gives −0.833 / −0.826 / −0.048 / −0.238; the decayed W-6k arm gives −0.881 / −0.881 / −0.524 / −0.548 | **mislabelled arm** (R7) |
| S8, S11 | "The 6-line loss falls from 6,000 to 24,000 in **7 of 8** seeds" | **8 of 8** (s0 is 0.0750 → 0.0740). `summary.json`'s own `E5_long_loss` has `falls_6k_to_end: true` for all 8 on `len6`; 7/8 is the **depth-3** count (s0 rises there) | **differs — understates its own result** (R9) |
| S7 | "Runs differing in **nothing a human specified** (checked: `sort -u` … returns exactly **1** string per group)" | true for both 6,000-step groups. **False for the 24,000-step group**: `w_s0` ran with `--ckpt_every 1000 --state_at 4800,9600`, `r24a_s0` and `r24b_s0` with neither. I read the code — both flags only trigger saves and cannot alter the trajectory — so the group is computationally equivalent, but not command-identical. Separately, the replicates did **not** hold GPU co-tenancy fixed (throughput 4.48–8.23 steps/s across the ten 6,000-step runs; disclosed in `log.md` at 19:05 but not in S7). I checked whether that drives the spread: pooled Spearman(throughput, 6-line rate) = **+0.115**, depth-3 **−0.018**, and the two seed groups disagree in sign — no evidence it does | **differs — overstated identity** (R3) |
| S10 | "a median **4.7 %** … (range **4.3–6.2 %**) over the **46 full-length runs**" | the 4.71 % median in `summary.json` is over **49** runs including the three 200–400-step smokes, whose overhead is 10.2–13.0 %. Over the 46 full-length runs it is median **4.70 %**, range **4.27–6.24 %** — so the number happens to be right and the range is right, but the sentence attributes one population's median to the other's range | **reproduces under the right population; the sentence mixes two** (R5) |
| S11 | E7 scored "**2/8**, 6/8, and 4 change" | 2/8 is W's **undecayed** step-6,000 checkpoint; "4 of 8 change mode" is computed from the **decayed** W-6k → W-24k pair, where the 6,000-step high count is **4/8** — inside E7's pre-registered 3–5 band. Two clauses of one expectation are scored on two different readings of "at 6,000 steps" | **inconsistent readings** (R10) |
| S11 | E13 scored "**3/4**" | 3/4 on the **6-line bin**; **0/4** if "per-bin" means all five bins. Which bin is not stated | **reproduces on one reading, needs the bin named** (R11) |
| prereg | baseline "6-line non-depth-3 **0.824 ± 0.037**" | that is `noise-floor`'s `len6_none`, **n = 247** (6-line, *no* pattern), not the n = 500 non-depth-3 complement this run reports. The n = 500 baseline is not derivable from the pulled artefacts | **mislabelled premise** (F4) |
| prereg | gate boundary "≈ 67 per million **on held-out greedy**" | 67.15 per million is over `noise-floor`'s 12,033,100 in-loop gate samples. On held-out greedy the run's own S1 measures **+400 and +200 per million** (2 and 1 extra theorems in 5,000). S1's cells are correct; only the pre-registration's sentence is | **mislabelled population** (F5) |
| S1 | "**Five** extra theorems in 20,000 theorem-cells" | the eight quoted cells differ in five of them, but the overall cell already contains its own bins: `stage1_p1_s0` gains **2** theorems (4,365 vs 4,363; both 6-line, one of them depth-3) and `stage1_p1_s1` gains **1** (4,682 vs 4,681; 6-line). **Three** distinct theorems in 10,000, appearing in 5 of the 8 cells | **differs — five is the cell count, not the theorem count** (R12) |
| pool | "**0** records collide with a held-out class" (`pool_fresh.json`, `make_splits.py`) | under a premise-order-insensitive renaming class: **21** held-out theorems in the control set's class, **66** in the fresh set's, **0** in the depth-3 slice. Effect on any reported rate ≤ **+0.14 pp** | **differs; bounded and immaterial** (F2) |

### Wording against n, and what the measured floor allows

Every cross-run comparison in this run is stated beside arm R's sd (E20 satisfied). What the
write-up does not state is the **resolution** those sds imply. Paired two-sided 95 % intervals,
computed by me from the per-seed values:

| comparison | n | mean difference | 95 % interval | what may be claimed |
|---|---|---|---|---|
| W-24k − W-6k, overall | 8 paired | **+5.3 pp** | **[+2.6, +7.9]** | a real gain |
| W-24k − W-6k, 5-line | 8 paired | **+5.4 pp** | **[+4.4, +6.3]** | a real gain |
| W-24k − W-6k, 6-line non-depth-3 | 8 paired | **+6.9 pp** | **[+5.5, +8.4]** | a real gain |
| W-24k − W-6k, 4-line | 8 paired | +2.8 pp | [+1.9, +3.7] | a real gain |
| W-24k − W-6k, 6-line | 8 paired | +16.8 pp | [+3.5, +30.1] | a real gain, poorly located |
| W-24k − W-6k, depth-3 | 8 paired | +26.6 pp | [+0.3, +52.9] | barely clears zero |
| W-6k − C, overall | 8 paired | −1.0 pp | [−3.3, +1.2] | no difference, to ±2 pp |
| W-6k − C, 6-line | 8 paired | −8.8 pp | [−20.7, +3.2] | **no difference detected, to ±12 pp** |
| F-24k − W-24k, 6-line (endpoint) | 4 vs 8 | −14.8 pp (median) | MDD **±21.1 pp** from R's 24k sd | **nothing may be claimed** |

Two consequences the write-up should carry. First, **Q1's strongest evidence is the slices that do
not oscillate** — overall, 5-line, 4-line and 6-line-non-depth-3 all clear zero with intervals of
±1–1.5 pp — not the 6-line bin and depth-3 slice it leads with, whose intervals are ±13 and ±26 pp.
The headline survives either way, and is stronger told the first way. Second, **E12's pre-registered
band (+2…+8 pp) was 4× below the design's resolution before the run started**; the right lesson is
not "steps, not data" but "this contrast needs a different readout".

---

## §Verdict

**Accept, with twelve rewordings and one gap to close.** No hard constraint is violated; nothing is
quarantined. This is the most carefully instrumented run in the series: every one of the 275 result
files recomputes exactly from its own raw records under code I wrote independently, the pre-registration
and both addenda were committed before the outcomes they cover, the misses are reported as misses
(6 of 22, all but one in the unfavourable direction, and the executor scored two of its own
expectations more harshly than the pre-registration required), and the deviations that mattered —
the arm-R chain split, the `sd_recheck.py` bug, the externally changed budget ledger — are disclosed
in `log.md` and `QUESTIONS.md` rather than smoothed over.

### What stands

1. **The blind spot is real.** `data/p2/heldout.jsonl` is length-sorted and its first 2,000 records
   are exactly 1,000 two-line and 1,000 three-line proofs, so every validation curve in this project
   before this run measured only proofs every model already solves at 0.99+. Verified directly.
2. **Stage 1 is not near saturation at 6,000 steps.** This is the run's headline and it holds with
   room to spare. Within seed, the 6k → 24k gain clears zero at 95 % on **every** slice, and the
   intervals are tightest exactly where the measurement is quietest: overall **+5.3 pp [+2.6, +7.9]**,
   5-line **+5.4 pp [+4.4, +6.3]**, 6-line non-depth-3 **+6.9 pp [+5.5, +8.4]**. E1's falsifier
   needed 6 of 8 seeds flat and got 0.
3. **The depth-3 "mode" is not a property of a seed, a data pool, or even a run — it is where a
   checkpoint happens to land.** Two distribution-free demonstrations, neither needing an sd:
   all **12** of the 24,000-step runs cross the 0.44 cut along their own trajectory (1–10 times), and
   **five runs of one fixed command line at one seed** span depth-3 0.064–0.736. This retires
   `NOISE_FLOOR.md`'s cross-seed bimodality as a separate phenomenon, and it retires "seed variance"
   as an explanation of it. It is the most consequential result in the run.
4. **The oscillation is capability, not decoding.** pass@8 at T = 0.8 on 500 depth-3 theorems moves
   **−50.0 pp** and **+85.8 pp** with greedy across the two within-run pairs, and the low-greedy
   checkpoints stay at 0.392 and 0.026 — so reading (ii) is dead and every bimodality this project
   has reported on greedy readouts is a real capability difference, not a measurement artefact. Well
   powered (n = 500, k = 8) and re-verified: I re-checked 133 of these accepted samples in Lean.
5. **Per-length validation loss ranks runs; `val2k` does not.** ρ = −0.905 (6-line) and −0.934
   (depth-3) against −0.310 for `val2k` across 8 seeds at a fixed step, and the pooled trajectory
   ρ is −0.885/−0.893 over 192 checkpoints. The instrumentation is worth its **4.7 %**.
6. **The judge.** Lean alone, `nd_verify` called nowhere, the 275 files self-consistent, 733 counted
   proofs re-verified in Lean (4.34.1 on my side, 4.34.0 on the pods) from their stored literal text
   with an added `#print axioms` check, after 197 negative controls confirmed my harness rejects what
   it should. The run also cross-checked its judge against two `noise-floor` checkpoints published
   under Lean ∧ `nd_verify` and against a second Lean rendering of 600 counted proofs — both
   reproduce under my counting.

### What must be reworded

- **R1 — "Q4 — steps, not data" is not supported as a positive claim.** The pre-registered estimator
  failed (E11 ratio ≈ 0, E12 median −14.8 pp), and with arm R's own 24,000-step sd the endpoint
  design's resolution is **±21 pp** on the 6-line bin against a pre-registered band of +2…+8 pp — it
  was 4× underpowered before the first pod. `numbers.md` S6 says this plainly ("the pre-registered
  endpoint estimator is not usable") and labels the substitutes "post-hoc"; the 400-word write-up
  does not, and its confident "steps, not data" reads as a demonstration. Reword to: *fresh data
  bought nothing detectable; the endpoint contrast cannot resolve anything below ≈ 20 pp, and the
  post-hoc trajectory estimators (best losses 0.0286 vs 0.0283, best rates 0.823 vs 0.820) are flat.*
- **R2 — Q3 needs its resolution.** "Schedules are indistinguishable" is right overall
  (−1.0 pp [−3.3, +1.2]); on the 6-line bin it is a non-detection at **±12 pp** (−8.8 pp
  [−20.7, +3.2]) and E10's own 5 pp falsifier fired. Say "no difference above ≈ 12 pp on the 6-line
  bin and ≈ 2 pp overall", not "indistinguishable".
- **R3 — S7's "differing in nothing a human specified" is not true of the 24,000-step group.**
  `w_s0` carries `--ckpt_every 1000 --state_at 4800,9600` and its two replicates carry neither. Both
  flags only trigger saves, so the group is computationally equivalent — say that, and drop the
  `sort -u` sentence, which returns 2 strings there. Add that co-tenancy was not held fixed
  (throughput 4.48–8.23 steps/s) and that it does not appear to drive the spread (pooled
  ρ = +0.115 on the 6-line bin, −0.018 on depth-3).
- **R4 — "reproduce nearly the whole 52-cell floor" claims more than n = 3 can.** The 95 % CI on
  that sd is [0.081, 0.973]. Say the same-command sd is **statistically indistinguishable** from the
  52-cell sd (all three replicate groups' CIs contain 0.1523) — which is the finding, and is enough.
- **R5 — S10 mixes two populations in one sentence.** The 4.7 % median in `summary.json` is over 49
  runs including three 200–400-step smokes at 10–13 %; the 4.3–6.2 % range is over the 46 full-length
  ones. Over those 46 alone: median 4.70 %, range 4.27–6.24 %. Quote one population.
- **R6 — S9's proof-length table is wrong in four of five rows.** Correct values, which are what the
  run's own `summary.json` holds and what `sd_tables.py` prints: C **86.4 / 4.15 / 126.7 / 5.13**,
  W-6k **84.5 / 4.17 / 118.4 / 5.36**, W-12k **83.9 / 4.19 / 115.3 / 5.49**, W-24k
  **86.8 / 4.19 / 125.8 / 5.16**; F-24k is already right. The analysis is fine; only the transcription
  is not. Add that "written lines" = `have`s + 1 **excludes box assumption lines**, which is why every
  depth-3 slice reads ≈ 4.0 written lines for 6-line theorems (F7).
- **R7 — S8's table is headed "arm W" but its 6,000-step column is arm C.** The four values
  (−0.952, −0.857, −0.333, −0.571) are arm C and reproduce exactly; arm W's own step-6,000 point gives
  −0.833/−0.826/−0.048/−0.238 and the decayed W-6k arm −0.881/−0.881/−0.524/−0.548. Relabel.
- **R8 — the write-up needs checker labels on its cross-date comparisons.** It quotes
  `NOISE_FLOOR.md`'s 0.462, 0.152 and 0.305 with no note that those were measured under
  **Lean ∧ `nd_verify`** while all its own numbers are under **Lean alone** (Dan, 2026-09-27).
  `numbers.md` labels them correctly; the 400-word document must too.
- **R9 — S8 and S11 understate the run's own result.** "The 6-line loss falls from 6,000 to 24,000 in
  7 of 8 seeds" is **8 of 8**; 7/8 is the depth-3 count. `summary.json` already has it right.
- **R10 — E7's two clauses are scored on two different readings of "at 6,000 steps."** 2/8 is W's
  undecayed step-6,000 checkpoint; the "4 of 8 change mode" count is from the decayed W-6k arm, where
  the 6,000-step count is 4/8 and inside the pre-registered 3–5 band. Use the decayed arm for both
  (it is what the arm table defines) and E7's first clause is met.
- **R11 — E13's "3/4" needs its bin named.** 3/4 on the 6-line bin; 0/4 on all five bins. The
  accompanying deflation ("the reason is the oscillation, not less memorisation") is correct and
  should stay.
- **R12 — S1's "five extra theorems" is a cell count.** Three distinct theorems in 10,000 (2 in
  `stage1_p1_s0`, 1 in `stage1_p1_s1`), appearing in five of the eight quoted cells.

Also carry F2, F4 and F5 from §Recount: the "0 held-out class collisions" claim holds only under the
project's premise-order-sensitive `canon_key` (21 and 66 collisions under a true canonical form,
worth ≤ +0.14 pp and exactly 0 on the depth-3 slice); the "6-line non-depth-3 0.824 ± 0.037" premise
is `noise-floor`'s n = 247 pattern-free slice, not this run's n = 500 complement; and the "≈ 67 per
million" gate boundary is a gate-population number, against +200–400 per million that this run's own
S1 measures on held-out greedy.

### What is not supported

- **The gap to close: arm R is not auditable.** `pod/sd/jobs.py` evaluates every arm-R checkpoint
  without `--texts`, so none of its counted proofs retains the literal Lean text a reviewer must
  re-check (the same is true of all 228 trajectory evaluations). Arm R's rates recompute exactly from
  its stored per-record verdicts, and I have no reason to doubt them — the same evaluator produced the
  733 proofs I did verify, and all 275 files are internally consistent — but arm R is the arm that
  licenses the run's central claim about the floor, and on the brief's standard ("re-check ≥ 100
  counted proofs per arm in Lean, from their stored literal text") it is unverified. **Remedy: re-run
  `sd_eval.py --texts --ckpts 'ckpts/sd/r6*.pt' 'ckpts/sd/r24*.pt'`. No training, ten checkpoints,
  ≈ 10 GPU-minutes, ≈ $0.10.** Do it before anything else here is built on.
- Q4's positive form (R1) and the n = 3 precision claim (R4).

### The next measurement

Two, in order of value per dollar.

1. **Make arm R checkable** — the `--texts` re-run above, ≈ $0.10. Then add `--texts` to the
   trajectory evaluations in any future run; storing the text costs **1.6 MB** per 5,000-theorem
   evaluation uncompressed (2.15 MB with text against 0.58 MB without, and far less gzipped) and is
   what makes the whole thing reviewable.
2. **The measurement that would settle what the oscillation is: average the weights, not the
   readouts.** Every ingredient is already in the bucket — 23 trajectory checkpoints per W seed. If
   the depth-3 rate of an average of the last k stable-phase checkpoints sits near the **high** end of
   its run's oscillation rather than near its mean, the oscillation is a wobble in the loss basin that
   weight averaging removes for free, "seed variance" stops being a property of Stage 1, and every
   future Stage 1 gets the high mode for nothing. If instead the average lands near the mean, the
   oscillation is a genuine alternation between distinct solutions and the right response is
   checkpoint selection on per-length loss (which this run has just shown works, ρ = −0.905). The
   run's own data already says this is the question worth asking: **averaging the readout** over
   steps 6,000–23,000 cuts the between-seed sd from 0.158 to **0.073** on the 6-line bin and from
   0.315 to **0.147** on depth-3, and on that readout F − W is **+1.4 pp** and **+0.2 pp** — so a
   trajectory readout is both 2× quieter and the only version of Q4 that could be answered. Cost:
   a CPU/GPU-minutes averaging job plus one evaluation per averaged checkpoint, ≈ 1 GPU-hour, ≈ $0.50.

If Q4 is to be answered properly rather than abandoned, the powered design follows from arm R: on the
trajectory-mean readout (sd 0.073) a 4-seed × 3-replicate cell per arm gives an MDD of ≈ ±6 pp, which
would actually test the pre-registered +2…+8 pp band. That is 24 runs of 24,000 steps, ≈ 35 GPU-hours,
≈ $17 — worth pre-registering as its own run rather than bolting onto this one.

---

Reviewer: agent:claude, 2026-09-27. Recount committed at `8f47cb90` before this section was written.
Scripts: `review_sd_slices.py`, `review_sd_pick.py`, `review_sd_lean.py`, `review_sd_controls.py`,
`review_sd_splits.py`, `review_sd_expect.py`. Raw outputs: `review_sd_expect.txt`,
`review_sd_splits.txt`, `review_sd_leanspec.verdicts.json`, `review_sd_controls.verdicts.json`.
