# Review of run `ds-rendering`

Reviewer session, independent of the executor. `AGENT_POLICY.md` governs. Phase 1 was done in
`~/review/ds-rendering`, a copy of the run's repository with the executor's write-ups
(`run*.md`, `numbers.md`, `STATUS*.md`, `campaign.md`, `followup.md`, `ignition.md`,
`phase*.md`, `*_summary*.md`) removed; `log.md` was present in that copy but was **not read**
until phase 2. Every number in §Recount comes from code I wrote myself
(`review_dsr/rv_*.py`, committed with this file) run against the run's raw artefacts, the
pools and the brief + `preregistration/ds-rendering.md`.

**Models measured.** All five arms are the same architecture and schedule: **3.2 M parameters
(4 layers, d 256, 8 heads), trained from scratch, 6,000 steps, bs 128, lr 1e-3 → 1e-4, cap 6,
on the same 155,000-record ND set `data/p2/train_depth3_f0_a1.jsonl` (depth-3 removed, f = 0),
Lean `lean_seq`-family surface form with a random first-appearance name offset.** The arms
differ only in the rendering mode of `lean_tok.py`: C0 `lean_seq`, R1 `lean_seq_noprem`,
R3 `lean_seq_nofml`, R2 `lean_seq_intro`, R4 `lean_seq_funbare`. C0 seeds 0/1 are
lean-format's two Stage-1 checkpoints (`stage1_a1_seq_s{0,1}.pt`), re-measured here; every
other model was trained in this run. Sampler `path=fast, early=eos, compact=True,
rowrng=True`, **batch 2048** everywhere, `max_new` 400, T 0.8. Acceptance is
**`nd_verify` ∧ Lean on the literal sampled text** through `lean_gate.py` at every stage.

---

## §Recount

### 0. Hard constraints

| constraint | check | result |
|---|---|---|
| `nd_verify` unmodified | `git rev-parse HEAD:nd_verify` vs `origin/main:nd_verify` | tree `9437bb72b8009d6660dc5d85496ec7e580c815fe` on both — **identical** |
| `artifacts/TEST_RUN_DONE` unchanged | blob vs `origin/main` | `1d5cf064d739eb9484500d9ec85969a77f69058d` on both — **identical**; content still the 2026-09-15 single test run |
| `nd2lean.py` untouched | vs `origin/dan_lean_format` (the branch point; the file does not exist in `origin/main`) | blob `16676091348d0600672edb132126d4754529e24a` on both — **identical** |
| no evaluation file read in training code | `grep` of `train.py`, `model.py`, `tokenizer.py`, `lean_tok.py`; read of every `pod/dsr/plan_*.txt` | training reads only `data/p2/train_depth3_f0_a1.jsonl`. `--heldout data/p2/heldout.jsonl` is passed, but `train.py:93,116-121` uses it **only** for a logged validation loss on the first 2,000 records — no gradient, no checkpoint selection (the last step is saved unconditionally). Noted, not a violation. |
| gate 0 — pre-registration before the first pod | commit times vs `~/pods.log` | main pre-registration **21:15:54Z**, first pod `dsr-c0` **21:19:20Z** (+3 m 26 s). Addendum 1 (R4) **21:45:02Z**, pod `dsr-r4` **21:45:53Z** (+51 s). Addendum 2 (seed sweep) **21:58:38Z**, pod `dsr-s` **21:59:27Z** (+49 s). **All three pass.** |
| budget | `podbudget ds-rendering` | 32.69 h of a 36 h ceiling, **$16.01 of $18**. `~/runs/ds-rendering/BUDGET_WARNING` present (fired at 28.84 h). |
| pods deleted | `podls` | only `dsg-1`/`dsg-2` (ds-generator) alive; **every `dsr-*` pod is gone**. |

**No hard-constraint violation. No quarantine.**

### 1. Split disjointness, recomputed by renaming class

My own canonicaliser (`review_dsr/rv_norm.py:renaming_key`) relabels propositional variables
`v0, v1, …` in order of first appearance across the whole sequent; it is not the repo's
`normalize.py`. It separates all 155,000 training records into 155,000 distinct classes, so it
is not over-merging.

| training file × evaluation pool | shared renaming classes |
|---|---|
| `train_depth3_f0_a1` × `p2/heldout` (5,000) | **0** |
| `train_depth3_f0_a1` × `p2/targets_depth3` (1,000) | **0** |
| `train_depth3_f0_a1` × `r3_1/depth3_req` (300) | **0** |
| `train_depth3_f0_a1` × `p2/targets_reductio_req` (300) | **0** |
| `train_depth3_f0_a1` × `p2/transfer_depth3` (500) | **0** |
| `train_depth3_f0_a1` × `ladder/transfer` (2,285) | **0** |
| `train_depth3_f0_a1` × `data/transfer` (1,638) | **7** ⟵ |
| `ladder/rl_targets` (4,495) × `p2/targets_depth3` | **6** ⟵ |
| `ladder/rl_targets` × `r3_1/depth3_req` | **2** ⟵ |
| `ladder/rl_targets` × `p2/targets_reductio_req` | **16** ⟵ |
| `ladder/rl_targets` × `ladder/transfer`, × `heldout`, × `data/transfer`, × `transfer_depth3` | 0 |

*(Correction to the first commit of this file: it reported 5 / 2 / 6 for the three non-zero
rows. My first `renaming_key` excluded the token `R` as a rule name, so the atom `R` was never
relabelled and the relation under-merged. Fixed in `review_dsr/rv_norm.py`; the corrected
count for `train × data/transfer` is **7**, which is exactly what `dsr_splits.py` reports, and
every zero above is unchanged. The bug could only ever hide an overlap, never invent one.)*

**Finding R-1 (minor, inherited).** `data/transfer.jsonl` — the mechanism-test pool that
carries the run's headline E3/E4 numbers — is **not disjoint** from the training set by
renaming class: `transfer_{81,102,493,703,900,1115,1590}` are the same theorems as training
records up to renaming, and the training copies carry **shorter** proofs (2–6 lines) than the
pool's labels (7–16 lines).
That is 7 / 1,638 = 0.43 %, and the mechanism counts bin by the length the model *writes*, so
the effect on E3/E4 is at most a few proofs; but the pool is described in the
pre-registration as held out and it is not entirely. The overlap is **inherited** —
`data/transfer.jsonl` and the ladder pools are byte-identical to lean-format's / ladder-A's
(`ladder/transfer.jsonl` sha256 `47dd1886…`, `ladder/rl_targets.jsonl` `a5c4c277…`, exactly
the hashes the pre-registration names) — so this run did not introduce it, and the same 5
theorems are in every earlier run that used this pool.

The `rl_targets` × p2-target-pool overlaps (6, 2 and 16 classes) are **not** in the run's own
`dsr_splits.py` table, which checks the training set against every pool but not the ladder's
RL target pool against them. They matter only for a coverage number measured on a
ladder-trained checkpoint; every coverage number in this run is on a Stage-1 model, so nothing
in this run is affected. Worth adding to the standing splits check for future runs.

### 2. The render check, re-run

My own re-run (`rv_render.py`), **3,000 records sampled independently from all 155,000**,
tokenizer offset disabled, Lean called on the literal rendered texts:

| mode | vocab | render → `inverse` identical | mean proof tokens | ratio to C0 | Lean accepts literal texts | theorem-swapped negatives accepted |
|---|---|---|---|---|---|---|
| `lean_seq` (C0) | 107 | 3000 / 3000 | 82.6 | 1.000 | 1000 / 1000 | 0 / 300 |
| `lean_seq_noprem` (R1) | 107 | 3000 / 3000 | 58.3 | **0.706** | 1000 / 1000 | 0 / 300 |
| `lean_seq_nofml` (R3) | 107 | 3000 / 3000 | 78.9 | **0.955** | 1000 / 1000 | 0 / 300 |
| `lean_seq_intro` (R2) | 108 | 3000 / 3000 | 75.4 | **0.913** | 1000 / 1000 | 0 / 300 |
| `lean_seq_funbare` (R4) | 107 | 3000 / 3000 | 75.4 | **0.913** | 1000 / 1000 | 0 / 300 |

Reproduces the pre-registration's table (1.000 / 0.707 / 0.956 / 0.915) to ±0.002, on a
different sample. R4 is **exactly** token- and (unlike R2) vocabulary-matched to R2, as
addendum 1 claims. Text-length (`have`-line) histograms reproduce too: C0/R2/R3/R4
`1:84 2:712 3:861 4:818 5:401 6:124`, R1 `1:1116 2:934 3:857 4:93` (pre-registration:
`1:80 2:680 3:875 4:844 5:386 6:135` and `1:1106 2:931 3:888 4:75`).

Two supporting claims of the pre-registration also reproduce on my own 20,000-record sample:
premise-count distribution **0-prem 12.2 %, 1 39.4 %, 2 42.9 %, 3 5.4 %** (pre-registered
12 / 40 / 43 / 5), and the number of lines whose annotation R3 drops, **0.628 per proof**
(0.012 / 0.760 / 0.479 / 0.838 / 1.048 by ND length 2–6; pre-registered 0.625 and
0.012 / 0.752 / 0.479 / 0.828 / 1.053). R3 is confirmed **not** a brevity arm.

### 3. Held-out accuracy (E1, E2) and the depth-3 slice

`data/p2/heldout.jsonl`, 5,000 theorems, 1,000 per ND length 2–6, greedy (k = 1, T = 0).
The "depth-3 slice" is **my own** box-depth counter (`rv_norm.py:box_depth`, maximum `|`-gutter
nesting of the reference ND proof), not the run's: 500 of the 5,000 reference proofs have box
depth ≥ 3, and the a1 training set contains **zero** depth-3 proofs, so that slice is f = 0
zero-shot composition and the other 4,500 are in distribution.

| arm | seed | overall | 6-line bin | depth ≤ 2 (4,500) | **depth 3 (500)** | depth-3 failures that are `LEANPARSE` |
|---|---|---|---|---|---|---|
| C0 | 0 | 0.9084 | 0.684 | 0.9553 | 0.486 | 164 / 257 |
| C0 | 1 | 0.8966 | 0.585 | 0.9658 | 0.274 | 296 / 363 |
| R1 | 0 | 0.8766 | 0.550 | 0.9482 | 0.232 | 324 / 384 |
| R1 | 1 | 0.8716 | 0.536 | 0.9442 | 0.218 | 283 / 391 |
| R3 | 0 | 0.9152 | 0.769 | 0.9420 | 0.674 | 107 / 163 |
| R3 | 1 | 0.8358 | 0.421 | 0.9260 | 0.024 | 420 / 488 |
| R2 | 0 | 0.9414 | 0.848 | 0.9547 | 0.822 | 12 / 89 |
| R2 | 1 | 0.9418 | 0.819 | 0.9636 | 0.746 | 42 / 127 |
| R4 | 0 | 0.9418 | 0.842 | 0.9589 | 0.788 | 30 / 106 |
| R4 | 1 | 0.9140 | 0.683 | 0.9667 | 0.440 | 173 / 280 |

Every cell of both addendum tables reproduces exactly, including the grammar-violation counts.
C0's re-measurement (0.9084 / 0.8966) reproduces lean-format's inherited 0.9086 / 0.8960 to
0.06 pp, so **E1 for C0 holds** and the two measurement pipelines agree.

### 4. The seed sweep (E17–E20), n = 6 per arm

Seeds 2–5 for C0, R2, R3, R4 (R1 excluded by addendum 2). All 24 models are present.

| arm | n | depth-3 slice, per seed | mean | **across-seed sd** | depth ≤ 2 mean | overall mean |
|---|---|---|---|---|---|---|
| C0 | 6 | 0.486 0.274 0.824 0.502 0.848 0.262 | 0.533 | **0.256** | 0.9615 | 0.9186 |
| R2 | 6 | 0.822 0.746 0.742 0.846 **0.034** 0.778 | **0.661** | **0.310** | 0.9563 | 0.9268 |
| R3 | 6 | 0.674 0.024 0.788 0.038 0.808 0.632 | 0.494 | **0.365** | 0.9387 | 0.8942 |
| R4 | 6 | 0.788 0.440 0.808 0.754 0.480 0.104 | 0.562 | **0.276** | 0.9526 | 0.9136 |
| R1 | 2 | 0.232 0.218 | 0.225 | 0.010 | 0.9462 | 0.8741 |

- **E17 — missed.** Predicted mean R2 > R4 > C0 ≈ R3 **with mean(R2) − mean(C0) ≥ 0.25**. The
  ordering holds (0.661 > 0.562 > 0.533 > 0.494) but the gap is **0.129**, about half the
  pre-registered minimum.
- **E18 — falsified.** Predicted R2's sd is the **smallest** of the four and **< 0.10**, with
  C0's, R3's and R4's each > 0.12. R2's sd is **0.310**, the *second largest*; seed 4 collapses
  to 0.034. The hypothesis that `by intro` is the rendering that removes the depth-3 seed
  variance is dead. Every rendering in this family, including `intro`, is bimodal across
  Stage-1 seeds: 20 of the 26 models land either above 0.44 or below 0.11.
- **E19 — narrowly missed.** In-distribution means span 0.9387 (R3) to 0.9615 (C0) = **2.28 pp**,
  just outside the pre-registered 2 pp. C0/R2/R4 are within 0.9 pp of each other; R3 is the
  outlier.
- **E20 — holds.** Spearman ρ between the depth-3 slice rate and the count of `LEANPARSE`
  grammar violations at depth 3 is **−0.933** over the 24 sweep models and **−0.943** over all
  26. The depth-3 gap is a bookkeeping gap, not a logic gap.

**Finding R-2 (major).** *At n = 6 no arm's depth-3 held-out slice is distinguishable from
C0's.* Exact two-sided permutation tests on the six seeds per arm (all 924 splits):

| comparison | difference in means | exact p |
|---|---|---|
| R2 − C0 | +0.129 | **0.452** |
| R2 − R4 | +0.099 | **0.617** |
| R4 − C0 | +0.030 | 0.829 |
| R2 − R3 | +0.167 | 0.272 (permutation) |
| R1 − C0 (n = 2 vs 6) | **−0.308** | 0.072 (permutation) |

The pooled within-arm sd is **0.302**. The decision rule of addendum 2 ("if |mean(R2) −
mean(R4)| ≤ s, dropping the binder type accounts for the effect and the `fun`-vs-`intro`
choice does not") fires — 0.099 ≤ 0.302 — but so would a rule comparing **R2 to C0**, which is
the comparison the run exists to make. The sweep was launched to settle the mechanism and its
honest answer is that **six seeds are still not enough**: the only ordering with any support is
that R1 is *worse* than C0, and even that is p = 0.072.

### 5. Mechanism test (E3, E4): pass@16 on `data/transfer.jsonl`

1,638 theorems, k = 16, T = 0.8, seed 0, batch 2048. "Distinct" = distinct
**start-index-normalised** ND proof per theorem, using my own normaliser
(`rv_norm.py:norm_proof`, renumbering line labels to N1… and rewriting every citation);
binned by the ND length the model **wrote**.

| arm | seed | theorems solved | distinct proofs, all lengths | **7-line** | **8-line** | ≥ 9-line | mean Lean tokens |
|---|---|---|---|---|---|---|---|
| C0 | 0 | 906 | 1229 | **234** | **77** | 7 | 103.1 |
| C0 | 1 | 922 | 1242 | **265** | **67** | 1 | 103.3 |
| R1 | 0 | 681 | 859 | 164 (×0.70) | 48 (×0.62) | 1 | 80.8 |
| R1 | 1 | 855 | 1120 | 206 (×0.78) | 59 (×0.88) | 4 | 79.8 |
| R3 | 0 | 808 | 1051 | 187 (×0.80) | 78 (×1.01) | 5 | 104.8 |
| R3 | 1 | 656 | 804 | 118 (×0.45) | 30 (×0.45) | 2 | 101.5 |
| R2 | 0 | 891 | 1141 | 247 (×1.06) | 79 (×1.03) | 2 | 95.8 |
| R2 | 1 | 861 | 1079 | 206 (×0.78) | 47 (×0.70) | 3 | 93.2 |
| R4 | 0 | 831 | 1060 | 193 (×0.82) | 46 (×0.60) | 0 | 91.9 |
| R4 | 1 | 903 | 1237 | 246 (×0.93) | 84 (×1.25) | 7 | 95.2 |

- **C0 reproduces its pre-registered bands**: E3 7-line 130–270 → 234 / 265 ✓; E4 8-line
  50–140 → 77 / 67 ✓.
- **R1 missed E3 and E4 badly and in the wrong direction**: ×0.70 / ×0.78 on 7-line against a
  pre-registered **×2–3**, and ×0.62 / ×0.88 on 8-line against **×1.5–2.5**. R1 also solves
  far fewer theorems overall (681 / 855 vs 906 / 922).
- **R3, R2, R4** are all within noise of C0 on 7-line except R3 seed 1 (×0.45), which is the
  same seed whose depth-3 held-out slice collapsed to 0.024.
- ≥ 9-line counts are 0–7 and flip sign between seeds; **nothing is derivable from them**.

**Finding R-3 (wording).** Falsifier 1 as written — *"the horizon is text length is dead if
R1's distinct 7-line pass@16 count is within ±25 % of C0 on both seeds"* — **does not fire**:
seed 0 is −30 %, outside the ±25 % window. But it does not fire because R1 is *worse* than the
window's lower edge, not because it is better. The pre-registered hypothesis (shorter text →
more long proofs) is refuted far more strongly than by the null the falsifier was written to
catch. The write-up must not report falsifier 1 as "not triggered"; the correct statement is
that R1 moved the frontier in the opposite direction to the prediction.

**Term size, re-derived** (the brief asks for term sizes as well as line counts). Mean literal
Lean tokens of accepted proofs, by written ND length, mechanism stage:

| arm | 5-line | 6-line | **7-line** | 8-line |
|---|---|---|---|---|
| C0 | 89.3 / 89.0 | 107.2 / 108.1 | **127.4 / 127.7** | 156.2 / 160.1 |
| R1 | 68.0 / 68.1 | 84.7 / 82.2 | **104.9 / 106.0** | 146.9 / 133.6 |
| R3 | 91.7 / 93.5 | 106.3 / 107.7 | **135.7 / 132.9** | 166.0 / 168.7 |
| R2 | 81.6 / 81.6 | 97.2 / 97.7 | **119.7 / 116.2** | 149.5 / 144.8 |
| R4 | 83.0 / 82.1 | 95.2 / 95.5 | **121.1 / 117.9** | 139.0 / 149.8 |

This is worth stating in the write-up: R1's token saving on the *training* distribution is
29 %, but **on the 7-line proofs at the frontier it is only 18 %** (105 vs 127), because long
proofs have proportionally fewer premise lines. The manipulation the run's main question turns
on is weaker exactly where it was supposed to act.

### 6. Base rates at pass@2,000 (E5, E6, E7)

Stage-1 models, k = 2,000, T = 0.8, seed 0, batch 2048, `--lenfield min_lines_ub`.

| pool | arm s0 / s1 hit | rate s0 / s1 | vs C0 |
|---|---|---|---|
| `p2/targets_depth3` (1,000) | C0 **512 / 411** | 0.512 / 0.411 | — |
| | R1 393 / 443 | 0.393 / 0.443 | −11.9 / +3.2 pp |
| | R3 513 / 355 | 0.513 / 0.355 | ×1.00 / ×0.86 |
| | R2 544 / 502 | 0.544 / 0.502 | +3.2 / +9.1 pp |
| | R4 496 / 499 | 0.496 / 0.499 | −1.6 / +8.8 pp |
| `r3_1/depth3_req` (300) | C0 **175 / 111** | 0.583 / 0.370 | — |
| | R1 129 / 113 | 0.430 / 0.377 | −15.3 / +0.7 pp |
| | R3 208 / 146 | 0.693 / 0.487 | ×1.19 / ×1.32 |
| | R2 218 / 175 | 0.727 / 0.583 | +14.3 / +21.3 pp |
| | R4 178 / 162 | 0.593 / 0.540 | +1.0 / +17.0 pp |
| `p2/targets_reductio_req` (300) | C0 **31 / 26** | 0.103 / 0.087 | — |
| | R1 17 / 36 | ×0.55 / ×1.38 | |
| | R3 24 / 17 | ×0.77 / ×0.65 | |
| | R2 13 / 19 | ×0.42 / ×0.73 | |
| | R4 37 / 46 | ×1.19 / ×1.77 | |

- **E5 for C0 — marginal miss.** Pre-registered 0.25–0.50; measured **0.512** (s0, just above)
  and 0.411 (s1, inside).
- **E6 for C0 — large miss.** Pre-registered 0.05–0.25; measured **0.583 / 0.370**, a factor
  of 2–7 above the band. The `depth3_req` pool is far easier for these models than the
  pre-registration expected. Because E6's arm predictions are all *relative to C0*, this does
  not invalidate the comparisons, but it must be reported as a miss.
- **E7 for C0 — miss.** Pre-registered 5–25 hits; measured **31 / 26**, both above.
- **E5 for R1 — missed, wrong sign.** Pre-registered +10 to +20 pp; measured −11.9 / +3.2 pp.
  **E6 for R1** likewise: −15.3 / +0.7 pp. **E7 for R1**: pre-registered ×1.5–3 and ≥ C0;
  measured ×0.55 / ×1.38.
- **E5 for R2 — the declared null missed on one seed**: ±5 pp predicted, +3.2 / **+9.1** pp
  measured. The direction is *up*.
- **E7 for R3** is ×0.65 on seed 1, just outside its ×0.7–1.5 band.
- **Falsifier 2 does not fire and could not have**: R2's base depth-3 rate did not halve, it
  rose. The nested-lambda mechanism is not supported by R2; nor is it refuted, because
  §4 shows the arms are not separable at n = 2 or n = 6.

I also counted, with my own depth predicate, how many hits carry a genuinely depth-≥ 3 proof.
On `depth3_req` every hit does (by construction). On `targets_depth3` only 193–350 of the
355–544 hits do, i.e. **30–45 % of "depth-3 target" solves are shallow proofs of a theorem
that happens to admit one**; a claim about depth-3 *composition* should quote the `depth3_req`
pool or the depth-filtered count, not `targets_depth3`. On `targets_reductio_req`, **zero**
accepted proofs anywhere reach box depth 3.

### 7. Dial: EI − frozen at round 4 (E8)

`expert_iter.py --rounds 4 --k 32 --temperature 0.8 --batch 2048` on `p2/targets_depth3`
(1,000), arm's own set as `--train`; frozen is the same with `--no_train`. I recomputed the
cumulative solved count as the number of distinct target names in `found_4.jsonl`; it
reproduces `round_4.json`'s `targets_cum.solved` exactly for all 20 runs.

| arm | seed | EI cum solved | frozen cum solved | **EI − frozen** | vs C0 |
|---|---|---|---|---|---|
| C0 | 0 | 649 (0.649) | 356 (0.356) | **+0.293** | — |
| C0 | 1 | 666 (0.666) | 291 (0.291) | **+0.375** | — |
| R1 | 0 | 551 | 285 | +0.266 | −0.027 ✓ |
| R1 | 1 | 665 | 309 | +0.356 | −0.019 ✓ |
| R3 | 0 | 631 | 376 | +0.255 | −0.038 ✓ |
| R3 | 1 | 564 | 235 | +0.329 | −0.046 ✓ |
| R2 | 0 | 621 | 444 | +0.177 | **−0.116 ✗** |
| R2 | 1 | 609 | 369 | +0.240 | **−0.135 ✗** |
| R4 | 0 | 617 | 377 | +0.240 | −0.053 ✗ (just) |
| R4 | 1 | 652 | 348 | +0.304 | −0.071 ✗ |

- **E8 for C0 — s0 inside, s1 just outside.** Pre-registered +0.20 to +0.35; measured +0.293
  and **+0.375**. (Inherited from lean-format: +0.292 / +0.351.)
- **E8 for R1 and R3 hold** (within ±0.05 of C0 on both seeds). **E8 for R2 fails on both
  seeds** (−0.116, −0.135) and **R4 fails on both**, marginally.
- The mechanism is visible and consistent: R2's and R4's *base* (frozen) rates are the highest
  (0.444 / 0.369 and 0.377 / 0.348 vs C0's 0.356 / 0.291), and all arms converge to a similar
  EI endpoint (0.55–0.67), so the gap closes from below. **This is Finding 3 ("RL amplifies
  what the base does") behaving exactly as stated, not a counter-example.**
- **Falsifier 3 does not fire.** It needs an arm with a *lower* base rate than C0 **and** a
  *larger* EI − frozen on both seeds. R2/R4 have higher base rates and smaller gaps; R1 has a
  lower base rate on s0 and a *smaller* gap. No counter-example to Finding 3 in this run.

### 8. Ladder (E9, E10)

`ladder_ei.py`, 8 rounds × k 32, batch 2048, `max_new` 400, on the ladder pools
(`rl_targets.jsonl` 4,495 targets; `transfer.jsonl` 2,285, read-out pool). I recomputed
solved and `L*` from `found_transfer_8.jsonl` with my own `L*` (largest L such that ≥ 5 solved
theorems have `L_true` ≥ L; I first checked `n_lines == L_true` for all 2,285 pool records).

| run | arm | seed | solved / 2,285 | **`L*`** | textbook solved / 760 |
|---|---|---|---|---|---|
| T1 | **C0** | 0 | **923** (0.404) | **12** | 60 |
| T1 | **C0** | 1 | **1003** (0.439) | **11** | 79 |
| T1 | R1 | 0 | 837 (0.366) | 11 | 96 |
| T1 | R1 | 1 | 945 (0.414) | 11 | 113 |
| T1 | R3 | 0 | 898 (0.393) | 11 | 88 |
| T1 | R3 | 1 | 698 (0.305) | 11 | 35 |
| T1 | R4 | 0 | 771 (0.337) | 11 | 8 |
| T1 | R4 | 1 | 896 (0.392) | 11 | 78 |
| T1 | R2 | 0 | **658** (0.288) | **10** | 21 |
| T1 | R2 | 1 | 800 (0.350) | 11 | 101 |
| **frozen** | all | — | **not run** | — | — |

Every T1 value reproduces `round_8.json`'s `transfer_cum` exactly.

- **E10 — holds for C0** (pre-registered 10–11; measured 11 and 12) and for every other arm
  (all 11, except R2 s0 at 10). **E10 for R1 — missed**: pre-registered `L*` **11–12**;
  measured 11 / 11, i.e. no gain over C0's 11 / 12.
- C0 is the best arm on the ladder on both seeds by solved count (923 / 1003 vs the best
  alternative 945 / 898). The seed spread within an arm (e.g. R3 698 vs 898, R2 658 vs 800) is
  **larger than every between-arm difference**, so "C0 wins" is a two-seed observation, not an
  established ordering. A rank test over the 5 arms × 2 seeds gives C0 rank 2 and rank 1 — the
  only honest summary is "no arm beats C0, and none is shown to differ from it".

**Finding R-4 (major, scope).** **E9 has no data at all.** All ten `la_frz_*` directories
contain only `args.json`; `la_frz_c0_s0` started at 2026-09-24T03:26:17Z and the arm's
finaliser ran at 03:30:42Z. R3's frozen ladder got as far as 128,940 gated samples and no
`found_*.jsonl`. So there is **no frozen ladder, for any arm** — no `L*_frozen`, no frozen
solved count, and therefore **no equal-attempts frozen control for any ladder claim**. The
pre-registered drop order was "R2's ladder, then R4's ladder, then R2, then R3's ladder"; what
was actually dropped was the *frozen half of every arm's ladder*, which is not on that list
and is the half that carries the baseline. `podbudget` shows the run stopped at $16.01 of $18,
consistent with the "stop at $16" rule firing.

The nearest available base number is round 1 of each T1 ladder, which samples the Stage-1
checkpoint before any training — but at **32** attempts per theorem, not the ladder's 8 × 32:

| arm / seed | base solved / 2,285 | base rate | base `L*` |
|---|---|---|---|
| C0 0 / 1 | 65 / 59 | 0.028 / 0.026 | 9 / 9 |
| R1 0 / 1 | 81 / 80 | 0.035 / 0.035 | 9 / 9 |
| R3 0 / 1 | 113 / 79 | 0.049 / 0.035 | 9 / 9 |
| R2 0 / 1 | 146 / 79 | 0.064 / 0.035 | 9 / 9 |
| R4 0 / 1 | 78 / 95 | 0.034 / 0.042 | 9 / 9 |

Every arm's base reaches `L*` = 9 at 32 attempts and the ladder ends at 10–12, so the ladder
gain is large and real; but it is **not** the attempt-matched comparison the policy requires,
and any "the ladder reached `L*` 12" sentence must be published with this caveat and with the
base number beside it.

### 9. Checker agreement (E11) — my own re-verification

I drew **250 counted proofs per arm (1,250 total)**, sampled with my own seed across every
counting stage (held-out, mechanism, coverage, dial EI, dial frozen, ladder T1), and ran three
independent checks: `nd_verify` on the denoted ND proof; the **unmodified `nd2lean.py`**
translation checked in Lean (the checker of record, which renders the ND proof its own way);
and the **literal sampled Lean text** checked in Lean with the arm's own statement header.

| arm | mode | counted pool | sampled | `nd_verify` ok | translate failures | Lean ok (nd2lean) | disagreements | literal text stored | literal text Lean-ok |
|---|---|---|---|---|---|---|---|---|---|
| C0 | `lean_seq` | 25,727 | 250 | 250 | 0 | 250 | **0** | 250 / 250 | **250 / 250** |
| R1 | `lean_seq_noprem` | 21,653 | 250 | 250 | 0 | 250 | **0** | 250 / 250 | **250 / 250** |
| R2 | `lean_seq_intro` | 22,574 | 250 | 250 | 0 | 250 | **0** | 250 / 250 | **250 / 250** |
| R3 | `lean_seq_nofml` | 22,680 | 250 | 250 | 0 | 250 | **0** | 250 / 250 | **250 / 250** |
| R4 | `lean_seq_funbare` | 24,047 | 250 | 250 | 0 | 250 | **0** | 250 / 250 | **250 / 250** |

Also checked, on 40 translated counted proofs: no `sorry` anywhere, zero Lean errors, and
`#print axioms` reports either no axioms or `[propext, Classical.choice, Quot.sound]` — the
classical axioms `DN` legitimately needs. There is **no separate `lean_check` tool** in this
branch (proposal 9's allowlist / axiom checker does not exist here); `nd2lean.lean_check` and
`lean_gate.lean_check` are the two entry points and I ran both.

In-loop, aggregating every `gate_*.jsonl` the run wrote:

| arm | samples | `LEANPARSE` | distinct checked | `nd_verify`-ok & Lean-rejected | per million | Lean-ok & `nd_verify`-rejected |
|---|---|---|---|---|---|---|
| C0 | 4,526,336 | 765,514 | 3,242,554 | **0** | **0.0** | 150 |
| R1 | 4,506,336 | 747,631 | 3,241,268 | **0** | **0.0** | 62 |
| R2 | 4,526,336 | 595,161 | 3,395,111 | **0** | **0.0** | 510 |
| R3 | 4,814,016 | **1,249,366** | 3,096,894 | **0** | **0.0** | **1,223** |
| R4 | 4,526,336 | 669,606 | 3,324,654 | **0** | **0.0** | 263 |

**E11 holds with room to spare**: 0 per million against a budget of ≤ 100 per million, in
every arm (lean-format measured 33 per million). The reverse direction is non-zero but never
counted — the gate passes those through and `nd_verify` rejects them. Worth noting for the
write-up: **R3 is the loosest rendering on both counts** — 26 % of its samples are
`LEANPARSE` (vs 13–17 % for the others) and it has 1,223 Lean-accepts-that-`nd_verify`-rejects,
5–20× the other arms. That is the formula-free `have` letting Lean elaborate something the
recomputing `inverse` disagrees with, and it is the cost of R3 that the token count does not
show.

### 10. E12–E16

- **E12** (R1's accepted-length histogram moves right by 1–2 ND lines at the frontier, defined
  as the last length with ≥ 5 distinct verified proofs): C0's frontier is **9** on seed 0
  (7 distinct at length 9) and **8** on seed 1 (only 1 at length 9); R1's is **8** on both
  seeds (1 and 4 distinct at length 9). R1's frontier moves **left or not at all** — never
  right. **Missed.**
- **E13 / E14** (R4's depth-3 slice lands in 0.65–0.90 if the cost is binder-type repetition,
  0.20–0.55 if it is `fun` syntax): measured **0.788 / 0.440** — one seed in each band, which
  is what addendum 2 says, and at n = 6 (§4) the two bands are not separable at all.
  **Unresolved, correctly.**
- **E15** (depth ≤ 2 in 0.94–0.97 either way): 0.9589 / 0.9667 ✓.
- **E16** (R4's depth-3 pass@2,000 within ×0.8–1.25 of R2, or of C0): R4/R2 = 496/544 = 0.91
  and 499/502 = 0.99 — **inside the R2 band on both seeds**; R4/C0 = 0.97 and 1.21 — **also
  inside the C0 band on both seeds**. E16 **cannot discriminate**, because R2 and C0 are
  themselves within 1.22× of each other. The test as designed has no power.
- **Decision rule (proposal 10).** "An arm replaces the control iff, on both seeds, held-out
  greedy is within 1 pp of C0 or better *and* at least two of {depth-3 pass@2,000, reductio
  pass@2,000, ladder T1 `L*` or solved} improve with none worse." R1: held-out −3.2 / −2.5 pp
  → **fails**. R3: held-out −6.1 pp on s1 → **fails**. R4: +3.3 / −0.3 pp on held-out, and
  ladder solved is worse on both seeds → **fails**. R2: held-out +3.3 / +4.5 pp ✓, depth-3
  pass@2,000 up on both ✓, but **reductio pass@2,000 is worse on both** (×0.42, ×0.73) and
  **ladder solved is worse on both** (658 vs 923, 800 vs 1003) → **fails "none worse"**.
  **No arm qualifies; the control set is not replaced.** R3's separate "qualifies" rule
  (falsifier 4: held-out within 1 pp and no readiness number worse) also fails.

### 11. Summary of §Recount

Everything the run measured, I reproduce — held-out by length and by my own box depth, the
mechanism counts with my own start-index normaliser, the base rates with my own depth
predicate, the dial cumulative counts, the ladder `L*` with my own definition, the render
check on my own sample, and the checker agreement with my own 1,250-proof re-verification.
There is no arithmetic disagreement anywhere.

The findings are about **scope and inference**, not arithmetic:

1. **R-1** `data/transfer.jsonl` shares 7 renaming classes with the training set (inherited;
   reproduces `dsr_splits.py` exactly).
2. **R-2** At n = 6 no arm's depth-3 held-out slice is distinguishable from C0's (R2 − C0
   p = 0.45). E18 is falsified; E17 missed by half. The rendering effect the run was built to
   measure is **not established**.
3. **R-3** R1's 7-line count is 22–30 % *below* C0, so falsifier 1's "within ±25 %" does not
   literally fire, but the pre-registered direction (×2–3) is refuted outright. R1's token
   saving at the 7-line frontier is 18 %, not 29 %.
4. **R-4** The frozen ladder was not run for any arm; E9 has no data, and no ladder claim has
   an equal-attempts frozen control.
5. Large pre-registration misses to report as misses: E6 (C0 `depth3_req` 0.583 / 0.370 vs a
   0.05–0.25 band), E7, E12, E5/E6/E7 for R1 in the wrong direction, E8 for R2 and R4, E10
   for R1, E19.
6. No arm satisfies proposal 10's decision rule.


---

## §Compare — the executor's claims against my recount

Read in phase 2: `run_ds_rendering.md`, `numbers.md` § ds-rendering, `log.md`
§ ds-rendering, `STATUS.md`, `QUESTIONS.md`, `artifacts/dsr/summary.json`, both figures.

### Arithmetic: everything reproduces

| claim (source) | my independent value | verdict |
|---|---|---|
| Render check: token ratios 1.000 / 0.707 / 0.956 / 0.915 / 0.915; round-trip 3000/3000; Lean 1000/1000; negatives 0/300; vocab 107 / 107 / 107 / 108 / 107 (`numbers.md` § 1) | 1.000 / 0.706 / 0.955 / 0.913 / 0.913 on my own 3,000-record sample; same round-trip, Lean and negative counts; same vocabularies | **reproduces** |
| R1 text-length histogram `1:1106 2:931 3:888 4:75`; C0 `1:80 2:680 3:875 4:844 5:386 6:135` (§ 1) | `1:1116 2:934 3:857 4:93`; `1:84 2:712 3:861 4:818 5:401 6:124` (different sample) | **reproduces** |
| R3 drops an annotation on **0.625 lines per proof** (0.012/0.752/0.479/0.828/1.053 by length); premise mix 12/40/43/5 % (§ 1, pre-registration) | 0.628 (0.012/0.760/0.479/0.838/1.048); 12.2/39.4/42.9/5.4 % | **reproduces** |
| Splits: 7 shared order-sensitive classes in `data/transfer.jsonl`, 0 in every other pool (§ 2) | 7, and 0 everywhere else, with my own canonicaliser | **reproduces** |
| Held-out greedy, all five arms × 2 seeds, overall and by ND length (§ 3) | identical to 4 decimals in all 50 cells | **reproduces** |
| Depth ≤ 2 / depth-3 split of the held-out pool, all arms (§ 3) | identical in all 20 cells, using my own box-depth counter on the reference proofs | **reproduces** |
| Mechanism pass@16: solved, distinct 7 / 8 / ≥ 9-line, and the 7-line breakdown by `n_prem` (§ 4) | identical; each `n_prem` row sums to my independent 7-line total | **reproduces** |
| Base rates at pass@2,000 on all three pools, both seeds, incl. per-sample rate and distinct ≥ 8-line counts (§ 5) | identical in all 50 cells | **reproduces** |
| Dial: EI / frozen cumulative solved, EI − frozen, depth-3 acquisition, held-out at r4 (§ 6) | identical; my own union-of-`found_4.jsonl` count and my own depth-3 acquisition predicate both match to the unit | **reproduces** |
| Ladder T1 solved and `L*`, both seeds, all arms (§ 7) | identical, with my own `L*` (≥ 5 solved at `L_true` ≥ L) recomputed from `found_transfer_8.jsonl` | **reproduces** |
| Checker of record: 83,513 distinct counted proofs, 100 % accepted by unmodified `nd2lean.py --check` and by Lean on the literal text, zero rejections (§ 8) | my own 1,250-proof re-draw (250 per arm, across every stage): 1,250 `nd_verify`-ok, 1,250 Lean-ok via `nd2lean.py`, 1,250 literal texts Lean-ok, 0 translate failures, 0 disagreements. No `sorry`; axioms only `[propext, Classical.choice, Quot.sound]` | **reproduces** |
| Agreement: 16,300,481 pairs, `nd_verify`-ok/Lean-rejected **0**, Lean-ok/`nd_verify`-rejected **2,208** (§ 8b) | 16,300,481 and 0 and 2,208 exactly. Per-arm reconciles once the sweep pod's 77,550 pairs / 15 disagreements are split out as § 8b does | **reproduces** |
| Per-100k Lean-only ordering R1 1.9 < C0 4.5 < R4 7.8 < R2 15.0 < R3 39.6; "R3 ~9×" (§ 8b, write-up) | 1.9 / 4.5 / 7.8 / 15.0 / 39.6; 39.6 / 4.5 = **8.8×** | **reproduces** |
| Compensation: corr(frozen, EI − frozen) = −0.871 across arms, −0.782 across models; corr(frozen, EI endpoint) = +0.158; frozen sd 0.0454 → EI sd 0.0238 (`log.md` 00:10, write-up) | −0.871, −0.782, +0.158, 0.0454 → 0.0238 | **reproduces** (but see R-6) |
| Seed sweep n = 6: C0 0.533 (0.256), R2 **0.661 (0.310)**, R3 0.494 (0.365), R4 0.562 (0.276); in-distribution spread 2.28 pp; pooled sd 0.305 (`log.md` 23:31, write-up) | 0.533 (0.256) / 0.661 (0.310) / 0.494 (0.365) / 0.562 (0.276); 2.28 pp; pooled 0.302 | **reproduces** |
| "83,513 counted proofs"; "ladder ×0.757"; "in distribution the five span 2.28 pp" (write-up) | 83,513; 729/963 = 0.757; 2.28 pp | **reproduces** |
| Gate 0, budget, pods deleted | prereg + both addenda each precede their pod in `~/pods.log`; $16.01 / $18, 32.69 / 36 h; no `dsr-*` pod alive | **reproduces** |

**There is not one arithmetic disagreement in the run.** Every table in `numbers.md` is
sourced to a file, and every file says what the table says.

### Where the wording outruns the evidence

| claim | my independent value | verdict |
|---|---|---|
| **"At the base, untyped-binder arms beat the control"** — frozen dial C0 0.324, R4 0.362, R2 0.406 (write-up, headline table) | The arm means are right, but the **between-arm spread is not distinguishable from seed noise**: within-arm seed sd averages **0.047**, between-arm sd is **0.045**, one-way **F(4,5) = 1.32** (5 % critical value 5.19). Same on the EI side: F = 0.59. | **not supported at n = 2** — reword to "R2 and R4 have the highest frozen means; with two seeds per arm the ordering is not resolvable" |
| **"Expert iteration compensates: corr(frozen, EI − frozen) = −0.871"** (write-up, and `log.md` 00:10 as the entry's headline) | **This correlation is an artefact of the shared term.** If the EI endpoint were *statistically independent* of the frozen rate, the expected correlation would be **−0.886** (analytic, from the two sds) and the permutation null mean is **−0.904**; the observed −0.871 is **less negative than the null** (permutation p = 0.70). The data are exactly what independence predicts. | **not supported** — the −0.871 is not evidence of compensation. The executor's *other* statement of the same fact, **corr(frozen, EI endpoint) = +0.158, "where a rendering starts predicts almost nothing about where it ends"**, is the correct and non-artefactual one and should be the one the write-up leads with |
| **"the arms converge (sd 0.045 → 0.024)"** (write-up) | True as arithmetic, but both numbers are at or below the within-arm seed sd (0.047 frozen, 0.035 EI), so the "convergence" is not established either. The **more robust** version is in the artefacts and I reproduce it exactly: depth-3 **acquisition** arm means span **12.3 pp frozen (0.117–0.241, F(4,5) = 2.10)** and only **3.3 pp after 4 EI rounds (0.387–0.420, F = 0.32, between-arm sd 0.014 against a within-arm seed sd of 0.025)**. After EI the five renderings are *demonstrably* indistinguishable; before it they merely are not distinguished. | **reword** — use the acquisition spread, which supports the second half of the claim outright |
| **"By the 8-round ladder the control is above every arm on both seeds"** (write-up) | **Correct and the strongest claim in the run.** C0 is ranked first on both seeds among five arms; under arm exchangeability that is p ≈ **0.040** (permutation over arm labels within each seed). The ANOVA is not significant (F(4,5) = 1.69), so the *paired ranking* is what carries it — which is how the sentence is written. | **stands** |
| **"R2 … is worst, ×0.757"** (write-up) | R2 is worst on the **mean** (729) and on seed 0 (658, last of five), but on seed 1 it is **fourth** — R3's 698 is lower. | **reword** — "worst on the mean and on seed 0" |
| **"R1 writes the shortest text (−21 %)"** (write-up) | Not derivable from any committed artefact. The render check gives **−29.4 %** on the training records (`numbers.md` § 1) and my measurement on *accepted* mechanism proofs gives **−22 %**; at the 7-line frontier specifically it is **−18 %** (105 vs 127 tokens). "−21 %" names no population. | **not derivable** — say which set it is over; and the frontier figure (−18 %) is the one the argument actually needs |
| **"The horizon belongs to the ND proof's structure"** (write-up) | What is shown is that R1 is **worse everywhere**: 7-line ×0.70 / ×0.78, held-out −3.2 / −2.5 pp, depth-3 slice 0.23 vs 0.53. "Text length is not the lever *in the direction predicted*" follows. "The horizon lives in the ND structure" does **not** — the equally consistent reading is that the premise `have` lines are actively *useful* (they give the model an explicit, citable copy of each premise), which is a statement about the text, not about the ND proof. | **overreach** — the disjunction was not tested; the run cannot distinguish "text length is irrelevant" from "removing premise lines removes something useful" |
| Falsifier 1 ("dead if R1's 7-line count is within ±25 % of C0 on both seeds") | Seed 0 is **−30 %**, outside the window; seed 1 is −22 %, inside. The falsifier as written **does not fire**, because R1 is below the window, not inside it. | **report precisely** — the prediction (×2–3) is refuted far more strongly than the falsifier's null; do not say "falsifier 1 fired" |
| **"E8 holds on both clauses" / "C0's mean is +0.334, inside the band"** (`log.md` 23:50) | The pre-registration scores E8 **per seed**, and C0 seed 1 is **+0.375**, above the +0.20–0.35 band. The later `log.md` 00:10 entry scores R2 and R4 as failing E8 correctly. | **partially reworded already** — `numbers.md` § 6 prints both seeds, so a reader can see it; the write-up does not mention E8 at all |

### Deliverables and pre-registration hygiene

| item | status |
|---|---|
| `preregistration/ds-rendering.md` before the first pod, both addenda before their pods | **yes**, gate 0 passes three times |
| Expectations written before the run and misses reported as misses | **largely yes, and unusually well.** `log.md` 23:31 scores E17 as "half right", **E18 as "falsified, and it was my leading hypothesis"**, E19 as narrowly missed; 00:10 corrects an over-generalisation the executor had made 20 minutes earlier; 00:35 and 04:20 correct a per-arm multiplier twice (18× → 11.8× → 8.8×) and wire the figure to regenerate. The write-up carries a "What I got wrong" section. This is the standard the policy asks for. |
| `run_ds_rendering.md` ≤ 400 words + two figures | **yes** (≈ 330 words); both figures are labelled with the model, the data, the sampler batch and the acceptance rule |
| One rendered example of the same proof in all modes | **yes**, `examples/ds_rendering_four_modes.md` (five modes) |
| `numbers.md` § ds-rendering, `log.md` dated, `artifacts/dsr/summary.json`, `STATUS.md` line, pods deleted | **yes** |
| Bucket paths recorded in `numbers.md` | **no.** The bucket *is* populated (`hf://buckets/dan-pandori/nd-rl/ds-rendering/{artifacts,ckpts,data,figures}` plus `numbers.md`, `preregistration.md`, `run_ds_rendering.md`), but § 9 Cost records pods and dollars only. **Missing deliverable, one line to fix.** |
| Every number names the model it was measured on | **yes in `numbers.md`** (a standing model-label paragraph plus per-table sources) and in both figures; **the write-up's "−21 %" is the one unlabelled number.** |
| Questions to Dan with a stated default | **yes**, three entries dated 2026-09-23, including the `nd2lean.py` BOTE finding |

### Two things a reader of the committed artefacts alone would get wrong

**Finding R-5 (important, reproducibility).** `numbers.md` opens with *"Every number is
re-derived by `python3 dsr_analysis.py` → `artifacts/dsr/summary.json`"*. I re-ran it. Its
`seed_sweep` block reports **`n_seeds: 2` for every arm** — seeds 0 and 1 only — because
`dsr_analysis.py:29` looks for `held_*.jsonl` in `artifacts/dsr/<arm's pod>/` and
`artifacts/dsr/`, and the sweep's 16 files are in `artifacts/dsr/dsr-s/`. The committed
`summary.json` therefore states:

| arm | `summary.json` `seed_sweep` (n = 2) | the truth at n = 6 (log.md 23:31, and my recount) |
|---|---|---|
| C0 | depth-3 mean 0.380, **sd 0.150** | 0.533, **sd 0.256** |
| R2 | depth-3 mean 0.784, **sd 0.054** | 0.661, **sd 0.310** |
| R3 | 0.349, sd 0.460 | 0.494, sd 0.365 |
| R4 | 0.614, sd 0.246 | 0.562, sd 0.276 |

At n = 2, R2's sd (0.054) **is** the smallest of the four and below 0.10 — so the committed
`summary.json` says **E18 holds**, which is the exact opposite of the run's own finding and of
the write-up's "What I got wrong". Worse, **`numbers.md` has no seed-sweep section at all**:
the 24-model sweep that addendum 2 pre-registered (E17–E20) and that changed the run's
conclusion appears only in `log.md` and in one clause of the write-up. The numbers are right
in the log and right in my recount; they are absent from the numbers document and wrong in the
summary artefact. **This is the one thing in the run that must be fixed before anyone else
reads it:** add a § to `numbers.md` with the n = 6 table, and fix the `dsr_analysis.py` path
list so `summary.json` regenerates it.

**Finding R-6 (important).** The depth-3 panel of `figures/ds_rendering_readiness.png` — the
panel that carries the run's most eye-catching contrast (R2 0.822 / 0.746 against C0 0.486 /
0.274) — plots **only seeds 0 and 1**. A reader of the figure sees precisely the n = 2 picture
the run has already shown to be a seed lottery. The figure should either add the four sweep
seeds to that panel or carry the n = 6 mean ± sd beside it.

**Finding R-4, restated after phase 2.** The frozen ladder (E9) really was not run for any
arm, and — unlike most of what I flag — the executor handled this well: `log.md` 00:20 and
01:20 record the deviation **before acting**, with the measured round time, the arithmetic, the
alternative considered (truncate `la_T1` to 6 rounds) and the reason for rejecting it, and say
plainly *"E9 … is not measured for any arm and will be reported as not run, budget."*
`numbers.md` § 7 prints `– / –`; the readiness figure's header says so. The remaining gaps are
in the **write-up**, which mentions neither the cut nor any base number beside "ladder,
8 rounds (/2,285): C0 963". AGENT_POLICY requires *"a base-model reachability number with
every 'RL solved X'"*. The number exists and I computed it: at 32 attempts the Stage-1 base
solves **59–146 of 2,285 (2.6–6.4 %), `L*` = 9, in every arm**. One clause in the write-up
fixes this.

---

## §Verdict

**No hard-constraint violation.** `nd_verify` matches `origin/main` exactly, `TEST_RUN_DONE` is
untouched, `nd2lean.py` is byte-identical to the branch point, no evaluation file is read for
gradient or model selection, and the pre-registration and both addenda each precede their pod.
Nothing is quarantined.

**The measurement is sound.** I reproduced every number in `numbers.md` with code I wrote
myself — my own renaming-class canonicaliser, box-depth counter, start-index normaliser,
`L*`, depth-3 acquisition predicate, and a 1,250-proof re-verification through `nd_verify`,
the unmodified `nd2lean.py` and Lean on the literal sampled text. Zero disagreements, zero
translation failures, no `sorry`, only the classical axioms. In-loop, over 16.3 M gated pairs,
`nd_verify`-accepted-and-Lean-rejected is **0**, against a pre-registered budget of ≤ 100 per
million. The run's protocol discipline — one sampler batch everywhere, the literal text stored
beside every counted proof, the checker of record re-run on every pod before deletion — is the
best I have reviewed in this repository.

**What stands.**

1. **Rendering does almost nothing in distribution.** Five renderings span **2.28 pp** on the
   4,500 in-distribution held-out theorems. Solid, and the same at n = 6.
2. **The whole visible difference between renderings is zero-shot depth-3 composition**, and
   that difference is **bookkeeping, not logic**: Spearman ρ = **−0.93** between an arm's
   depth-3 rate and its count of `LEANPARSE` grammar violations at depth 3, over 24 models.
   This is the run's most robust mechanistic finding and it is under-sold in the write-up.
3. **The control wins the ladder.** C0 is first of five on **both** seeds (923 / 1003;
   p ≈ 0.04 under arm exchangeability), and C0 owns the only `L*` = 12. **No rendering variant
   buys RL readiness.** This is the run's headline and it survives.
4. **The arm that leads at Stage 1 need not lead after RL.** R2 has the best frozen dial
   (0.406) and the best Stage-1 depth-3 mean (0.661 at n = 6) and the **worst ladder mean**
   (729, ×0.757). Even granting that neither endpoint is individually significant at n = 2,
   the *reversal* is a real and useful warning, and it is the most transferable thing the run
   produced.
5. **Lean alone is not a sufficient checker for this ND rule set.** 2,208 Lean-accepted /
   `nd_verify`-rejected pairs in 16.3 M, **0** in the other direction, with a named mechanism
   (`nd2lean.py`'s `BOTE` → `.elim` resolving to `Not.elim` under `¬a ≡ a → False`, 74.5 % of
   cases) and a rendering-dependent rate (R1 1.9 < C0 4.5 < R4 7.8 < R2 15.0 < R3 **39.6** per
   100k). This is a finding about the *repository*, not about this run, it is correctly raised
   in `QUESTIONS.md`, and it deserves to be propagated: **any past or future claim in this
   project that rests on a Lean pass alone is not safe.**
6. **E18 is falsified and reported as falsified**; E17 missed by half; E19 narrowly missed;
   E9 unscored with the deviation recorded before acting. The reporting of misses is exemplary.
7. **No arm satisfies proposal 10's decision rule.** The control set is not replaced. R3's
   separate "qualifies" clause also fails. I agree with the run's conclusion.

**What must be reworded.**

- **"Expert iteration compensates: corr(frozen, EI − frozen) = −0.871"** → drop it. The
  independence null predicts −0.886. Replace with the executor's own
  **corr(frozen, EI endpoint) = +0.158** and with the acquisition spread: arm means span
  **12.3 pp frozen and 3.3 pp after four EI rounds** (F falls from 2.10 to 0.32). That says
  "EI erases whatever the rendering gave it" without leaning on a shared-term correlation.
- **"At the base, untyped-binder arms beat the control"** → "have the highest frozen means;
  F(4,5) = 1.32, not resolvable at two seeds."
- **"The horizon belongs to the ND proof's structure"** → "removing the premise re-statement
  shortens the text and makes the model worse on every measure; the cap + 1 horizon is not
  moved right by shortening the text. Whether that is because length is not the lever, or
  because the premise `have` lines are themselves useful, this run cannot say."
- **"R1 writes the shortest text (−21 %)"** → name the population: −29 % on the training
  records, −22 % on accepted mechanism proofs, **−18 % at the 7-line frontier**.
- **"R2 … is worst"** → "worst on the mean and on seed 0; fourth of five on seed 1."
- Add to the write-up: **the frozen ladder was cut for budget (E9 unscored)** and **the base
  reachability beside the ladder number** (59–146 / 2,285 at 32 attempts, `L*` 9, every arm).

**What is not supported and should not be repeated.** Any claim that R2's `by intro` rendering
is more seed-stable, or that any arm's depth-3 held-out rate differs from the control's. At
n = 6 the largest such gap (R2 − C0 = +0.129) has exact permutation **p = 0.45**, against a
pooled within-arm sd of **0.302**. The run says this itself in `log.md`; it must not leak back
out through `summary.json` (Finding R-5) or the readiness figure (Finding R-6).

**Must fix before this goes further** (both cheap, neither changes a conclusion):

1. `dsr_analysis.py:29` — add `artifacts/dsr/dsr-s` to the search path so `summary.json`'s
   `seed_sweep` block reports n = 6 instead of n = 2 and stops asserting the falsified E18.
   Add the n = 6 table to `numbers.md` as its own section.
2. Record the bucket paths in `numbers.md` § 9.

**The next measurement that would settle what is left open.** The run's own question — does
the rendering change RL readiness — is answered "no" by the ladder, and that answer is safe
because it is a paired ranking over five arms. What is *not* settled is the mechanism behind
the depth-3 held-out gap, and this run shows exactly why: **that cell needs far more seeds,
not more arms.** With the measured pooled within-arm sd of **0.302**, a two-sample test has
80 % power to detect

| seeds per arm | smallest detectable difference in the depth-3 slice |
|---|---|
| 6 (what the run has) | **0.489** |
| 20 | 0.268 |
| 40 | 0.189 |
| **87** | **0.129** — the observed R2 − C0 gap |

So the honest options are to run **{C0, R2} × ~85 seeds, Stage-1 and held-out only** — 170
models, ≈ 17 pod-hours, ≈ **$8.5** at the sweep's measured $0.05 per model — or to stop asking.
$8.5 is cheap for retiring a question that has already consumed two addenda, and nothing else
in the design has to change. Note also that the distribution is **bimodal, not normal** (of the
26 models, 20 sit either above 0.44 or below 0.11), so the cleaner estimand is *the probability
that a seed lands in the high mode* — C0 4/6, R2 5/6, R4 4/6, R3 3/6 — which needs a similar n
and would be reported as a proportion with a Wilson interval rather than a mean.

Second, and larger: **the ND-structure-vs-text disjunction R1 could not separate.** R1 removed
the premise lines *and* whatever value those lines carry as citable, formula-bearing
intermediate steps. The separating arm is one that keeps a premise line per premise but makes
it carry **no information the statement does not already give** — e.g. `have n1 := h1` with no
formula, R3's treatment applied to `PR` lines only. If that arm matches C0, the premise
*line* is what helps and length is irrelevant; if it matches R1, the premise *formula* is what
helps. One arm, two seeds, ≈ $2.5 — and it makes R1's negative result interpretable instead of
merely negative.
