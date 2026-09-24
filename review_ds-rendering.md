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
| `train_depth3_f0_a1` × `data/transfer` (1,638) | **5** ⟵ |
| `ladder/rl_targets` (4,495) × `p2/targets_depth3` | **2** ⟵ |
| `ladder/rl_targets` × `p2/targets_reductio_req` | **6** ⟵ |
| `ladder/rl_targets` × `ladder/transfer`, × `heldout`, × `data/transfer`, × `depth3_req` | 0 |

**Finding R-1 (minor, inherited).** `data/transfer.jsonl` — the mechanism-test pool that
carries the run's headline E3/E4 numbers — is **not disjoint** from the training set by
renaming class: `transfer_{81,102,703,1115,1590}` are the same theorems as
`train_depth3_f0_a1_{19706,134842,72889,129083,76684}` up to renaming, and the training copies
carry **shorter** proofs (2, 6, 4, 6, 4 lines) than the pool's labels (7, 10, 13, 16 lines).
That is 5 / 1,638 = 0.3 %, and the mechanism counts bin by the length the model *writes*, so
the effect on E3/E4 is at most a few proofs; but the pool is described in the
pre-registration as held out and it is not entirely. The overlap is **inherited** —
`data/transfer.jsonl` and the ladder pools are byte-identical to lean-format's / ladder-A's
(`ladder/transfer.jsonl` sha256 `47dd1886…`, `ladder/rl_targets.jsonl` `a5c4c277…`, exactly
the hashes the pre-registration names) — so this run did not introduce it, and the same 5
theorems are in every earlier run that used this pool.

The `rl_targets` × `targets_depth3` / `targets_reductio_req` overlaps (2 and 6 classes) matter
only for a coverage number measured on a ladder-trained checkpoint; every coverage number in
this run is on a Stage-1 model, so nothing here is affected.

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
  as the length with ≥ 5 distinct verified proofs): from §5, the frontier is **9 for C0 s0,
  9 for C0 s1** (7, 1 distinct at 9 — so 8 on s1), and R1 reaches 8 on both seeds. R1's
  histogram moves **left**, not right. **Missed.**
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

1. **R-1** `data/transfer.jsonl` shares 5 renaming classes with the training set (inherited).
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

