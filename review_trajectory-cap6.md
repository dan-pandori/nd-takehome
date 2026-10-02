# Review — run `trajectory-cap6`

Reviewer session, 2026-10-02 (started 03:10 UTC). Phase 1 was done blind in `~/review/trajectory-cap6` (executor
write-ups removed), from the pre-registration (`preregistration/trajectory-cap6.md`, committed `f6e9ff57`
2026-10-01 19:33 UTC; first pod commit `50583b34` 19:44; first ladder `args.json` 19:59 UTC — **written before the run**),
the code and the raw artefacts. Reviewer code: `review_tj6/` (adapted from `review_tj/`, the cap-12 reviewer's own
code; nothing imported from `tj_*.py` / `tj6_*.py`); outputs `review_tj6/rv6/`. **Lean alone decides**; `nd_verify` was
not used for anything.

**Models.** Every cap-6 number below is on **best-cap6 s0 / s1 / s2** of this run: ALiBiGPT 6 × 384, **9,560,832
params** (read from the checkpoint), `lean_staten`, from scratch on `data/p2/train_depth3_f0_a1.jsonl` (cap 6, 155,000
records, md5 `29276f24…` — same on the pods' setup logs), recipe `best`, Stage-1 1,200 s (A40), then the T1 ladder (8
rounds × k 32). Checkpoint labels: `p<step>` = Stage-1 step, `pend` = end of Stage-1 = r0, `r1`–`r8` = ladder rounds.
Cap-12 numbers are on `trajectory`'s **best-cap12 s0–s2** (same recipe, cap-12 set), read from the bucket copy in
`~/review/trajectory/artifacts/tj`, and are labelled "cap-12". The checkpoint md5s I fetched (pend, p1600, r8 × 3 seeds)
equal the executor's `score/ckpts_s*.md5`.

## §Recount (phase 1, blind)

### Hard constraints

| check | result |
|---|---|
| `nd_verify/` tree hash vs `origin/main` | identical (`git ls-tree` md5 `429f7333…` both) |
| `nd_verify` / `verify_cli` used by run code (`tj6_*.py`, `tj_*.py`, `state_eval.py`, `state_ladder_ei.py`) | no reference |
| `artifacts/TEST_RUN_DONE` | byte-identical to `origin/main` (md5 `e2eea349…`) |
| evaluation files read in training code | `state_train*.py`, `state_ladder_ei.py`: no textbook72 / holdout250 / `data/bs` reference. The ladder *samples* `data/ladder/transfer.jsonl` (holdout250 ⊂ it) each round but trains only on RL-target proofs + the cap-6 set (`state_ladder_ei.py` §4) |
| training code changes in the branch | only `--save_steps` (checkpoint save with the schedule clock paused), inherited from `trajectory` |

No hard-constraint violation.

### Split disjointness (renaming class: 24 atom permutations, premise-order-insensitive, F not renamed)

| eval pool | vs cap-6 train set (155,000) | vs ladder RL targets | vs ladder transfer (sample-only) |
|---|---|---|---|
| textbook72 | 0 | 0 | 0 |
| holdout250 | 0 | 0 | 250 / 250 (by construction; never trained on) |

textbook72 ∩ holdout250 classes: 0.

### Reads: completeness, sanity (pre-reg 1), groups (pre-reg 2)

All 264 reads present (3 seeds × 22 checkpoints × 2 pools × 2 sampling seeds), every record `n_tried` 256 and
`n_ok = n_tried − len(reasons)`, `solved == bool(proofs)`.

| seed | tb72 r0 | tb72 r8 | h250 r0 | h250 r8 | pre-reg ranges (9–29 / 24–49 / 105–165 / 210–245) |
|---|---|---|---|---|---|
| s0 | 17 | 43 | 152 | 225 | all in |
| s1 | 14 | 41 | 124 | 228 | all in |
| s2 | 15 | 38 | 125 | 224 | all in |

(x0 reads. Stage-1 held-out greedy: 4,863 / 4,767 / 4,780 of 5,000.)

| seed | A | B | C | A-lost | pre-reg: A 125–180, B 85–135, C 40–80, A-lost ≤ 6; B > cap-12 B (54 / 51 / 60) |
|---|---|---|---|---|---|
| s0 | 169 | 101 | 52 | 2 | all in; B > 54 |
| s1 | 138 | 132 | 52 | 1 | all in; B > 51 |
| s2 | 140 | 122 | 60 | 0 | all in; B > 60 |

Cap-12 groups recounted from `trajectory`'s x0 reads: A 232 / 236 / 234, B 54 / 51 / 60, C 36 / 35 / 28.
Majority sets: A6 153, B6 113, C6 53; A12 239, B12 51, C12 31; **B6∩A12 = 75** (pre-reg ≈ 70, 45–100: in);
A6∩A12 152; C6∩A12 9.

### pass@k (pre-reg 7; groups from x0, pass@k from x1, unbiased estimator n = 256)

| seed | B r0 pass@256 (pred ≈ 0.12, 0.03–0.30) | B r8 pass@1 (≈ 0.45, 0.25–0.65) | B r8 pass@256 (≥ 0.85) | A r0 pass@1 (≈ 0.35) | A r8 pass@1 (≈ 0.8) | C r8 pass@256 (≤ 0.10) |
|---|---|---|---|---|---|---|
| s0 | 0.069 | **0.653** | 0.960 | 0.459 | 0.914 | 0.077 |
| s1 | 0.083 | 0.630 | 0.985 | 0.327 | 0.915 | 0.038 |
| s2 | 0.074 | 0.586 | 0.959 | 0.349 | 0.931 | 0.050 |

B r0 pass@256 sits inside its range but below the point value in 3/3. B r8 pass@1 is above the point value in 3/3 and
**s0's 0.653 is just outside the stated range**. A r8 pass@1 is ≈ 0.92 against a point value of 0.8, with no range stated.

### Truncation (per stratum = pool × group × checkpoint × sampling seed; `action truncated` + `step cap`)

**494 of 792 strata exceed 0.1 %.** The largest are C at r6–r8 on holdout250 (7–14 %) and s1 p0 (≈ 10 %, a random-init
model). At r8 x0: B 1.3 / 1.6 / 1.3 % (tb72:B 4.5 / 3.9 / 4.5 %), C 6.0 / 4.9 / 5.9 %. At pend x0: ≤ 0.02 % everywhere,
except s1 (B 2.0 %, h250:B 2.5 %). The caps were held at `max_action` 512 / `max_steps` 96, as pre-registered and disclosed.

**The 2× cap re-read (`capdiag`: `max_action` 1024, `max_steps` 192, batch 1,024, sample seed 0).** Its inputs equal my C@r8
and B@pend sets exactly. Theorems solved at 2×:

| seed | C@r8 tb72 / h250 | B@pend tb72 / h250 | residual cut-off at 2× (C@r8 tb72 / h250) |
|---|---|---|---|
| s0 | 3 / 28, 1 / 24 | 0 / 27, 5 / 74 | 2.9 % / 7.9 % |
| s1 | 1 / 31, 0 / 21 | 2 / 27, 6 / 105 | 1.0 % / 10.0 % |
| s2 | 3 / 34, 0 / 26 | 0 / 23, 10 / 99 | 4.9 % / 7.3 % |

The B@pend flips for s0 and s2 cannot be a cap effect: their cut-off at 1× was ≈ 0 %. They come from a sampling re-draw
(batch 1,024 instead of 2,048 changes the stream), consistent with B's r0 pass@256 of ≈ 0.07. So **B membership at r0
means "r0 pass@256 ≲ 0.07", not "r0 cannot"**: about 5–10 % of B flips to A on any re-draw. C at r8 is still 1–10 % cut
off at 2×.

### Eventual proofs

| seed | r8 x0 solved | candidates = distinct accepted r8-x0 proofs | replay failures | eventual = argmax T1.0 total | ties < 1e-3 | median margin to runner-up |
|---|---|---|---|---|---|---|
| s0 | 268 | 8,859 = 8,859 | 0 | 268 / 268 | 0 / 261 | 0.49 nats |
| s1 | 269 | 6,472 = 6,472 | 0 | 269 / 269 | 1 / 258 | 0.46 |
| s2 | 262 | 4,579 = 4,579 | 0 | 262 / 262 | 0 / 245 | 0.55 |

`data/tj6/eventual_s*.jsonl` = `artifacts/tj6/targets/eventual_s*.jsonl`; `targets_s*` = eventual + the 315 references;
`data/tj6/ref_targets.jsonl` is byte-identical to `trajectory`'s. `data/tj6/cross.jsonl` equals the three cap-6
eventual files plus `trajectory`'s three cap-12 eventual files exactly.

### Lean re-check (own ND→Lean renderer, `#print axioms` ⊆ {propext, Classical.choice, Quot.sound})

The counted texts are ND re-renderings of the literal `lean_seq` text: the x0 literal-text dumps were not pulled
(trajectory-learnings), as in `trajectory`. I re-render ND → Lean myself.

- **Negative controls.** 60 untouched r8 proofs: all pass. 60 stored `LEANREJ` texts: 0 pass. 60 theorem-mismatched: 0. `sorry`: 0.
  Or.inl ↔ Or.inr flipped at the ORI line: 8 / 60 pass, and all 8 are `A ∨ A` disjunctions, where the flip is still a valid
  proof. On the first 400 ORI proofs of s0 r8: 0 / 400 pass.
- **150 per arm** (30 longest distinct theorems + 120 random): s{0,1,2} × {pend x0, r8 x0, intermediate checkpoints x1}:
  **150 / 150 in all 9 arms**.
- **Every counted proof at pend x0 and r8 x0**: s0 391 / 391 and 8,859 / 8,859; s1 324 / 324 and 6,472 / 6,472;
  s2 311 / 311 and 4,579 / 4,579.
- **Every scored target** (cap-6 eventual × 3, the 315 references, the cap-12 eventual proofs; 1,291 distinct): 1,291 / 1,291.

No counted proof rejected.

### Teacher-forced scores (my CPU scorer, unpadded fp32, env-assigned names skipped)

612 base-0 sums (40 random targets × {p1600, pend, r8} × 3 seeds, plus 40 cross targets × {pend, r8} × 3 seeds) against the
executor's `raw_b0_total`: max |diff| 1.7e-4. 12 full 33-base marginals at pend: max |Δ total| 2.4e-5, max |Δ w1| 1.5e-5.
`rev12_s{K}` (cross targets under cap-12 checkpoints) re-scores `trajectory`'s own eventual proofs under their own
models: 2,595 (target, checkpoint) pairs at p1600 / pend / r8, all **bit-identical** to `trajectory`'s score files.
I therefore use the executor's per-step score files, with my own summaries and my own groups.

### Headline (pre-reg 3). B, per seed; w1 = worst step (nats, T 1.0); Δ_RL = w1(r8) − w1(r0), Δ_PT = w1(r0) − w1(p1600); medians within seed

| target | seed | n | w1 p1600 | w1 r0 | w1 r8 | Δ_RL | Δ_PT | Δ_RL > Δ_PT |
|---|---|---|---|---|---|---|---|---|
| own eventual | s0 | 101 | −14.21 | −10.70 | −0.92 | 9.32 | 3.59 | yes |
| | s1 | 132 | −11.54 | −10.03 | −0.97 | 8.58 | 1.11 | yes |
| | s2 | 122 | −11.81 | −9.69 | −1.04 | 8.51 | 1.84 | yes |
| reference | s0 | 101 | −13.13 | −10.46 | −3.52 | 5.93 | 1.72 | yes |
| | s1 | 132 | −10.69 | −9.93 | −2.98 | 4.98 | 1.48 | yes |
| | s2 | 122 | −11.09 | −8.54 | −3.99 | 4.45 | 1.22 | yes |
| cross-seed eventual (other two cap-6 seeds' proofs; (theorem, proof) pairs) | s0 | 181 | −14.94 | −10.86 | −4.00 | 6.30 | 3.26 | yes |
| | s1 | 242 | −11.45 | −10.50 | −3.04 | 6.22 | 1.24 | yes |
| | s2 | 231 | −12.06 | −10.99 | −4.09 | 5.77 | 1.34 | yes |

med Δ_RL − med Δ_PT, per seed, then IQM (= mean at n = 3) with a theorem-within-seed bootstrap 95 % CI:

- own: 5.73 / 7.47 / 6.68 → **6.63 [5.82, 7.65]**;
- reference: 4.20 / 3.50 / 3.22 → **3.64 [2.50, 4.62]**;
- cross-seed: 3.03 / 4.98 / 4.43 → **4.15 [3.40, 4.81]**.

Against the pre-registration:

- w1(r0) predicted ≈ −7 (−12 to −4): got −10.7 / −10.0 / −9.7. Inside the range, more negative than the point value.
- w1(r8) ≥ −1.5: yes, 3 / 3.
- Δ_RL ≈ +6 (+3 to +10): got 9.3 / 8.6 / 8.5. In range.
- Δ_PT ≈ +3 (0 to +5): got 3.6 / 1.1 / 1.8. In range.
- **Falsifier not triggered.** The decision rule for "RL-dominated" is met on own (3 / 3, IQM difference 6.6 ≥ 2), and also
  on both selection-free targets: reference (3 / 3, 3.6) and cross-seed (3 / 3, 4.2).
- **Missed prediction:** "reference Δ_PT ≥ Δ_RL (as at cap 12)". At cap 6, Δ_RL > Δ_PT on the references in 3 / 3 seeds,
  by 3.6 nats IQM.
- Cross-seed Δ_RL lies between reference and own (IQM 6.09, between 5.12 and 8.81) and is ≥ +2: as predicted.

Contrast: in group A the sign reverses. Δ_RL 2.1 / 2.1 / 2.5 vs Δ_PT 4.8 / 3.5 / 4.3, so Δ_PT > Δ_RL in 3 / 3.

### Cap 6 vs cap 12 (pre-reg 4), pooled (theorem, seed) pairs on B6∩A12 (75 theorems)

| item | prediction | reviewer value | verdict |
|---|---|---|---|
| 4a action count, cap-6 eventual, B6∩A12 vs A6∩A12 | difference ≥ 2 | median 12 (n 219) vs 10 (n 456): **exactly 2** | met (at the boundary) |
| 4b cap-12 eventual proof, median w1 under cap-6 pend / under cap-12 pend | ≤ −4 / ≥ −3 | **−11.76** (672 pairs; per cap-6 seed −12.11 / −11.71 / −10.93) / **−2.81** (224) | met |
| 4c cap-6 pend worst step of own eventual at action index ≥ 7 (1-based) | ≥ 50 % of pairs | **34 %** (75 / 219); median index 5 | **missed** |
| 4d cap-12 eventual proof, median w1 under cap-6 r8 minus under cap-6 pend | ≥ 2 | −6.44 vs −11.76: +5.32 (paired median +4.41) | met; still −6.4 at r8 |
| 4e cap-12 own eventual on B6∩A12, w1 pend − p1600 (cap-12 model) | ≥ 3 | paired median **+4.72** (n 224); difference of medians +5.19 | met |

### Totals (pre-reg 5) and C's references (pre-reg 6)

| seed | A total r0 (≈ −4, −7 to −1) | B total r0 (≈ −17, −30 to −8) | A total r8 (≈ −2) | B total r8 (≈ −3, −6 to −1) |
|---|---|---|---|---|
| s0 | −3.97 | −24.29 | −1.37 | −1.92 |
| s1 | −4.31 | −20.49 | −1.20 | −2.00 |
| s2 | −4.21 | −20.72 | −1.07 | −1.80 |

All values are in range. The B r0 total is lower than the point value in 3 / 3 seeds.

C's references cover n 46 / 46 / 54 of C's 52 / 52 / 60 theorems; textbook72 has 7 theorems without a reference.

- Median w1 at r0–r8 is ≤ −9.89 in every seed. The prediction "≤ −8 at every RL checkpoint" holds.
- Δ_RL is **+2.16** / −0.93 / −0.16. **|Δ_RL| < 2 misses in s0** (by 0.16) and holds in s1 and s2.

### Lengths and term size (my Lean elaboration: app + lam + proj + bvar + const nodes of the theorem value)

| seed | A eventual | B eventual | A reference | B reference | C reference |
|---|---|---|---|---|---|
| s0 | 24 / 9 / 10 | 33 / 11 / 12 | 23 / 9 / 10 | 29 / 9 / 10 | 36.5 / 10.5 / 11.5 |
| s1 | 24 / 9 / 10 | 32 / 10 / 11 | 23 / 9 / 10 | 28 / 9 / 10 | 36 / 10.5 / 11.5 |
| s2 | 23 / 9 / 10 | 31 / 11 / 12 | 22 / 9 / 10 | 28 / 9 / 10 | 33.5 / 10 / 11 |

(median term size / ND lines / env actions)

B's eventual proofs are larger than B's references in 3 / 3 seeds, by +3 to +4 term nodes and +1 to +2 lines or actions.

On B6∩A12, cap-6 eventual vs cap-12 eventual: term size 32 vs 34, ND lines 11 vs 11.5. On A6∩A12: 23 vs 26, 9 vs 10.

My term-size definition is not the executor's `term_size` field: Spearman 0.71, and 0 / 1,744 values are equal. Compare
orderings across the two, not values.

### Compute (re-derived from `round_*.json` and the read files)

- **Ladder.** Σ `secs` = 17,992 / 17,733 / 16,766 s, against `compute.json`'s 17,990 / 17,730 / 16,763 GPU-s.
  Target samples are 1,150,720 per seed, identical across seeds: the ladder seeds are matched by construction.
- **Read attempts.** 22 × 2 × 322 × 256 = 3,627,008 per seed, plus capdiag (s0 153 theorems × 256). That reproduces s0's
  3,666,176 exactly. s1 (+320,000) and s2 (+82,432 = one full 322-theorem read) count extra reads, presumably the
  dead-GPU / OOM retries. They are real spend, but the write-up should say so.
- Stage-1: 24,511 / 24,120 / 24,113 steps (`compute.json`; not re-derived).

### Phase-1 summary

The data are sound:

- every counted proof I checked is Lean-accepted (all pend and r8 x0 proofs);
- the selection, the targets and the scores reproduce to ≤ 2e-4;
- splits are disjoint;
- no hard-constraint violation.

The pre-registered headline holds as "RL-dominated" under the pre-registered rule, on own, reference and cross-seed targets.

Misses to look for in the write-up:

- reference Δ_PT ≥ Δ_RL (missed 3 / 3);
- 4c (34 % vs ≥ 50 %);
- C reference |Δ_RL| < 2 in s0 (2.16);
- B r8 pass@1 range in s0 (0.653 > 0.65);
- 4a met only at the boundary.

Caveats to look for:

- B at r0 is a single-draw label (≈ 5–10 % flips on re-draw);
- truncation exceeds 0.1 % in most r1–r8 strata, so r8 pass@k for B and C is biased low by up to ≈ 4 % of samples;
- Δ_PT is measured from step 1,600, where B's w1 is already −12 to −14.

## Phase 2 — compare (read `run_trajectory_cap6.md`, `numbers.md` § trajectory-cap6, `log.md` § trajectory-cap6)

Extra reviewer scripts: `review_tj6/phase2.py` and `review_tj6/robust_x1.py` (outputs in `rv6/phase2.log` and
`rv6/robust_x1.log`).

**Two aggregation notes.**

- For the cross-seed and cap-12 target rows, the executor averages a theorem's several fixed proofs and then takes the
  median over theorems. My phase 1 took the median over (theorem, proof) pairs. With the executor's aggregation I
  reproduce its numbers exactly (`phase2.log`, last two lines). The conclusions are the same under both.
- The "key checkpoints" table is pooled over (theorem, seed) pairs. It reproduces to the second decimal.

| claim (executor) | reviewer value | verdict |
|---|---|---|
| Models: best-cap6 s0–s2, 9,560,832 params, `lean_staten`, from scratch on the cap-6 set, Stage-1 1,200 s A40 + T1 ladder; cap-12 rows labelled as `trajectory`'s best-cap12 | read from the checkpoints; set md5 matches | reproduces; every number is labelled |
| Groups A 169 / 138 / 140, B 101 / 132 / 122, C 52 / 52 / 60, A-lost 2 / 1 / 0 | identical | reproduces |
| Sanity: tb72 pend 17 / 14 / 15, r8 43 / 41 / 38; h250 pend 152 / 124 / 125, r8 225 / 228 / 224; held-out greedy .973 / .953 / .956 | identical | reproduces |
| F1: B worst step −10.0 (end PT) → −0.98 (r8); Δ_RL +8.8 [8.2, 9.5] vs Δ_PT +2.2 [1.6, 2.7], 3 / 3 | pooled −10.00 → −0.98; IQM 8.81 vs 2.18; 3 / 3; paired 6.89 | reproduces. The rule's "RL-dominated" is met (3 / 3, IQM difference 6.6 ≥ 2-nat MDD) |
| F1: holds on references (+5.1 vs +1.5), another seed's eventual (+6.0 vs +2.2), cap-12 eventual (+4.6 vs +1.5) | 5.12 vs 1.47; 5.97 vs 2.17 (per-theorem mean; pair median 6.09 vs 1.95); 4.57 vs 1.50 (pair median 4.93 vs 1.74); each 3 / 3, each paired IQM ≥ 3 | reproduces |
| (robustness, reviewer) groups defined from the independent x1 draw, or B = r0 fails in both draws | own: Δ_RL − Δ_PT IQM 6.71 / 7.17; references: 3.70 / 3.86; 3 / 3 in each | the headline does not depend on the single-draw group label |
| F1: "After step 8,000 B is flat (+0.6)" | per seed −1.39 / +2.16 / +0.93 (mean 0.57); A +2.49 | **reword**: "+0.6 on average (−1.4 to +2.2 by seed)". s1's +2.2 is not flat |
| F1: "At cap 12 the two were about equal (+4.1 vs +4.6), and references gained only +1.5" | cap-12 (reviewed in `review_trajectory.md`): Δ_PT +4.09, Δ_RL +4.59, reference Δ_RL +1.55 | numbers right, **order swapped** relative to the sentence before it ("Δ_RL … vs Δ_PT"). Write "Δ_RL +4.6 vs Δ_PT +4.1", and label it best-cap12 |
| F2: B6∩A12 = 75; cap-12 eventual +4.7 in cap-12 PT, to −2.8; under cap 6 −11.8 → −6.4 under r8; cap-6 own proof reaches −0.9 | 75; +4.72 (paired), −2.81; −11.76 → −6.44; own −8.89 → −0.90 | numbers reproduce |
| F2: "RL at cap 6 finds its own route, not cap 12's" | (i) RL *does* lift cap 12's proof: +5.3 (medians), +4.4 paired, against a cap-6 Δ_PT of +1.5 on cap-12 proofs (B rows). (ii) The −0.9 for the own proof is r8's argmax, selected upward by construction. A selection-free cap-6-style proof, another cap-6 seed's eventual proof, reaches **−3.30** under r8 on B6∩A12 (pend −10.0). So the like-for-like gap at r8 is ≈ 3 nats, not ≈ 5.5. (iii) 4c missed (only 34 % of bad steps sit past action 7), so the bad step is mostly *not* past the trained length | **reword**: "RL raises cap 12's proof too (+4–5 nats), but cap-6-style proofs from other seeds end ≈ 3 nats higher (−3.3 vs −6.4): RL favours the cap-6 model's kind of proof". Drop "not cap 12's". Also say what 4c's miss implies: the gap is not mainly a too-long proof |
| F2 title: "longer training proofs do in pretraining what RL does at cap 6" | 4e (+4.7 ≥ 3) met; 4b met; 4d met | supported as a description of where the climb happens (cap-12 PT vs cap-6 RL). The mechanism behind it is not shown (4c miss, 4a only at the edge: 12 vs 10 actions) |
| F3: C references ≈ −12 throughout | pooled −12.8 (pend) … −12.1 (r8); per seed ≥ −9.9 max | reproduces |
| F3: "at 2× caps C is solved no more often than by a fresh draw" | C@r8 solved at 2×: 4 / 52, 1 / 52, 3 / 60. Expected from x1 pass@256 (.077 / .038 / .050): ≈ 4 / 2 / 3 | reproduces. `numbers.md` "the caps are not what keeps C unsolved" is fine **for doubling**: 2× still cuts off 5.7 % of C's r8 samples (1–10 % by seed × pool), so "not what keeps C unsolved at up to 2× caps" is the supported wording |
| B at pend solved at 2×: 5 / 101, 8 / 132, 10 / 122, "the rate a fresh draw gives" | identical; s0 / s2 had ≈ 0 % cut-off at 1× | reproduces. It also means B membership at r0 is "r0 pass@256 ≲ 0.07", which is worth one sentence in the write-up |
| Example (B6∩A12, s0, `la_transfer_1888`): `n1.2` at −14.9 / −4.3 / −0.40 / −0.43 | −14.85 / −4.26 / −0.40 / −0.43; the shown Lean text is accepted (no axioms) | reproduces |
| Hits / misses list: misses = reference Δ_PT ≥ Δ_RL; 4c; C \|Δ_RL\| < 2 in s0 | same three misses in my recount | reproduces. Also: B r8 pass@1 s0 .653 is marked ✓ "at the edge" of 0.25–0.65; it is outside by .003 (**trivial miss**, should be listed). 4a "at the edge" is correctly flagged |
| `numbers.md` totals: pend A −4.16, B −21.8; r8 A −1.21, B −1.91 | means of my per-seed medians: −4.16, −21.83, −1.21, −1.91 | reproduces |
| `numbers.md` cross-tab: A→A 152, B→A 75, B→B 37, C→A 9 | identical | reproduces |
| `numbers.md` 4a–4e, descriptive rows (cap-6 eventual under cap-12 pend −4.5; references −9.0 / −3.7) | 2; −11.8 / −2.8; 34 %; +4.4; +4.7; −4.49; −9.05 / −3.70 | reproduces |
| `numbers.md` "box opener in 160 / 355 (Or.elim 84, imp 54, neg 22), ∧E projection 71" | Or.elim 84, other boxes 76, projection 71 of 355 | reproduces |
| Proof size: eventual A 10 / 5, B 12 / 7; reference A 10 / 5, B 10 / 6, C 11 / 9 (actions / term size) | actions identical. My term size (a different node count) gives the same ordering: B eventual > B reference > A; C reference largest | reproduces (ordering). Term-size definitions differ (Spearman 0.71); both are internal |
| All targets Lean-accepted 583 / 584 / 577, cross 1,664 | all 1,291 distinct targets; all 20,936 counted pend / r8 x0 proofs | reproduces |
| Truncation: 494 / 792 strata > 0.1 %, max 14.2 % (RL), 11.7 % (PT), 200 / 288 RL strata | identical | reproduces. The Limits line names only C. B at r8 on textbook72 is 3.9–4.5 % cut off, so B's r8 pass@k is biased low by up to that much; say so |
| Re-score determinism: 19,030 pairs, max \|Δw1\| 0 | my 2,595-pair subset: 0 | reproduces |
| Compute: ladder 17,990 / 17,730 / 16,763 GPU-s A40; cap-12 ladders 22,350–27,021 (≈ 1.4×, A6000) and train tokens ≈ 1.5×, flagged > 1.25× | round files Σ secs 17,992 / 17,733 / 16,766; `trajectory`'s compute.json 22,350 / 24,467 / 27,021, 754 / 783 / 751 M tokens | reproduces; correctly flagged |
| Reads compute 19,632 / 20,644 / 19,889 GPU-s "incl. the 2× diagnostic" | attempts reproduce for s0. s1 / s2 include ≈ 5 h250-reads' and 1 full read's worth of extra attempts (retries after the dead GPU / OOM) | **add**: say the read rows include the retries |
| Spend 45.2 pod-hours, $22.62 | `podbudget`: 45.19 h, $22.62 | reproduces |
| Pre-registration before the run | commit 19:33:46; first pod 19:34:15 (`log.md`); ladders ≥ 19:59; file unchanged since | holds. The header's "~20:00" is disclosed in `log.md` |
| `nd_verify` not used; checker named | no use; all numbers post-2026-09-27, Lean only | holds |
| Literal-text dumps lost (disclosed in `log.md`) | My re-check renders ND → Lean from the stored `proofs`. Every counted proof passes, but the literal sampled text cannot be re-checked | **finding (minor, repeat from `trajectory`)**: fix `up()` to include `dump/` before the next run |

## §Verdict

**Stands.**

- The data and every pre-registered quantity reproduce from raw files with independent code: groups, sanity, pass@k,
  eventual selection, scores (≤ 2e-4), the headline, 4a–4e, totals, C, truncation and compute.
- No counted proof is rejected by Lean, and the negative controls fail as they should.
- Splits are disjoint and there is no hard-constraint violation.
- The headline is supported under the pre-registered rule, on own, reference and cross-seed targets: at cap 6, B's worst
  step climbs mainly in RL (Δ_RL − Δ_PT IQM 6.6 / 3.6 / 4.2 nats, 3 / 3 seeds, all ≥ the 2-nat MDD). It survives
  re-defining the groups from the independent draw.
- The contrast with cap 12 (about equal there; RL-dominated here) stands on these two model organisms. Note that the
  cap-12 comparison is between runs: different GPUs (A6000 vs A40) and > 1.25× ladder compute, as flagged.
- The misses are reported honestly.

**Reword.**

1. F2 "RL at cap 6 finds its own route, not cap 12's" → RL lifts cap 12's proof too (+4–5 nats), but cap-6-style proofs
   from other seeds end ≈ 3 nats higher at r8 (−3.3 vs −6.4). Compare against the selection-free −3.3, not the
   argmax-selected −0.9.
2. F1 "After step 8,000 B is flat (+0.6)" → give per-seed values (−1.4 / +2.2 / +0.9).
3. F1 cap-12 parenthesis: write "Δ_RL +4.6 vs Δ_PT +4.1 (best-cap12)"; the current order reads as swapped.
4. List the B r8 pass@1 s0 (.653 vs ≤ .65) as a (trivial) miss.
5. Limits: B's r8 pass@k is biased low by up to ≈ 4 % cut-off samples on textbook72. "Caps are not what keeps C
   unsolved" holds for doubling only: 2× still cuts off ≈ 6 %.
6. Say the read compute rows include retries. Say B at r0 means "r0 pass@256 ≲ 0.07": a re-draw moves 5–10 % of B to A.

**Not supported.**

- Any mechanism in which cap 6's bad step lies past the trained length: 4c missed, at 34 %.
- F2's title as an explanation rather than a description.

**Next measurements.**

- (a) Score r8 on proofs it did not select within the *same* seed (r8 x1's highest-likelihood proof that differs from the
  x0 argmax). This separates selection from preference without a cross-seed model difference.
- (b) To settle F2's "own route": on B6∩A12, give the cap-6 ladder cap 12's eventual proofs as injected targets (or
  score cap-12 proofs after one more round). That shows whether the ≈ 3-nat gap is a preference or just that RL never
  sampled them.
- (c) Re-read C at r8 at 4× caps on a pod (≈ 1 GPU-hour) to close the residual truncation question.
- (d) Keep the x0 literal-text dumps (`up()` excluding `dump/`).
