# Review — run `guided-tts` (reviewer: agent:claude, 2026-10-03)

Models throughout (unless a row says otherwise): `best_model.ALiBiGPT` 6 × 384, 9,560,832 params (confirmed in every
read's summary `n_params`), `lean_staten` format, from scratch + 8-round T1 ladder; **cap 12** = `la_T1_best12_s{0,1,2}_r8.pt`
(Stage-1 on `train_k12.jsonl`), **cap 6** = `la_T1_best6_s{0,1,2}_r8.pt` (Stage-1 on `train_depth3_f0_a1.jsonl`).
Reads: T 0.8, k 256 per theorem, `max_steps` 96, `max_action` 512, ≤ 10 rejections per attempt, 259 theorems.
Checker: Lean 4.34.1 core everywhere (post-2026-09-27; no cross-date comparison in this run).

## Recount

Phase 1 was done in `~/review/guided-tts` (executor write-ups removed) with code I wrote, in `review_gt/`:
`rc_count.py` (solves, groups, pass@k, matched-token / matched-wall curves, theorem bootstraps, compute), `rc_lean.py`
(Lean re-check with my own statement builder + negative controls + checker-rejection test), `rc_splits.py` (renaming
class, minimised over premise order), `rc_size.py` (own line and term-size counters), plus the pooled IQM snippet whose
output is `rc_pooled.txt`. Inputs: `data/gt/*.jsonl` and `artifacts/gt/eval/*.{json,rows.jsonl.gz,steps.jsonl.gz}`.

### Hard constraints
| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72…` = `origin/main`'s |
| `nd_verify` used as judge | no: new code does not import it; `guided_eval.py` judges with `lean_gate.gate` only (`state_env` imports `nd_verify.verify.parse_formula` as a parser, pre-existing) |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064…`, unchanged from the base `0c492902` |
| evaluation files in training code | no training in this run (`train_steps` = 0); the problem files are read only by `guided_eval.py` / analysis |
| pre-registration before sampling | `preregistration/guided-tts.md` committed 18:10:36 UTC (`8ec7c0a6`), never edited after; first read's `_meta.utc` 18:18:xx |
| problem files | sha256 of all six `data/gt` files match the pre-registered prefixes |

No hard-constraint violation. (Observation: the run's commits are already on `origin/dan`, i.e. merged before review.)

### Split disjointness (renaming class, my canonicaliser, min over premise orders)
| training file | rows | eval rows in the same class |
|---|---|---|
| `train_k12.jsonl` (cap-12 Stage-1) | 155,000 | **2**: `tb72_textbook_dev/textbook_3ed45280…` (`P v Q, ~P ⊢ Q`, premise order swapped) and `candidate_v0/textbook_9d21fccc…` (`~(P v Q) ⊢ R > ~P`, renamed); both 7 lines, both in ≤ 10 |
| `train_depth3_f0_a1.jsonl` (cap-6 Stage-1) | 155,000 | 0 |
| ladder `rl_targets.jsonl` / `transfer.jsonl` | 4,495 / 2,285 | 0 / 0 |

Inherited from the cap-12 models' training set, not this run's design; it touches neither **long** nor any arm difference
(same theorems in every arm). Should be disclosed with the cap-12 textbook72 numbers.

### Lean re-check (literal stored text; statement rebuilt by me from the prompt)
5,211 distinct accepted texts — every solved theorem of every (model, arm) once, plus 60 random long and 60 random ≤ 10
texts per (model, arm): 250–320 per (model, arm). **0 rejected by Lean**, no `sorry`/axiom tokens, no warnings.
Harness negative controls (same texts, mutated): goal → `False` 195 / 200 rejected (the 5 accepted are theorems whose
goal is already `F`), `.1`↔`.2` swap 100 / 100 rejected, `Or.inl`↔`Or.inr` 96 / 105 rejected (rest symmetric
disjunctions). Per-step checker: 900 checker-rejected steps (150 per plain read, executor's standalone sources) → 900
Lean-rejected; 180 checker-passed → 180 Lean-accepted. No false reject found.

Caveat (evidence, not a defect found): every finished proof in every arm with a checker flag is "Lean-rejected" and every
unflagged one accepted (`rc_flags.txt`), but under `LEAN_PREFILTER=on` flagged texts are rejected by the prefilter (the same
term rules as the step checker) without reaching Lean — e.g. `best12_s0_structural`: "rej 20661 (filter 20661)". So the
pre-registered "second check" (no Lean-accepted plain proof contains a checker-rejected step) is circular on these
files; only the step-level agreement test is independent evidence. Rejected whole texts are not stored, so I could not
close it.

### Solved@256 (attempt-matched) per group — plain / structural / logical
| group (n) | c12 s0 | c12 s1 | c12 s2 | c6 s0 | c6 s1 | c6 s2 |
|---|---|---|---|---|---|---|
| textbook72 (72) | 48/53/54 | 48/50/52 | 53/55/57 | 43/47/48 | 43/43/47 | 39/41/45 |
| release (187) | 130/132/146 | 124/126/138 | 135/138/142 | 109/111/123 | 105/108/126 | 95/106/118 |
| long (90) | 38/38/50 | 31/34/45 | 42/43/47 | 24/26/32 | 25/25/35 | 19/25/31 |
| Roy (78) | 48/49/55 | 47/48/53 | 51/51/52 | 40/40/45 | 38/40/47 | 32/36/43 |
| Pelletier (8) | 2/2/3 | 1/1/2 | 2/2/2 | 1/1/2 | 2/2/2 | 1/1/2 |
| batch3 (14) | 11/11/12 | 8/8/10 | 9/10/11 | 7/7/9 | 9/9/9 | 8/8/9 |
| ≤ 10 (97) | 92/94/96 | 93/92/93 | 93/95/95 | 85/85/91 | 80/83/91 | 76/81/87 |
| 11–20 (67) | 36/36/46 | 29/31/41 | 40/42/45 | 22/24/30 | 24/24/33 | 18/23/30 |
| > 20 (23) | 2/2/4 | 2/3/4 | 2/1/2 | 2/2/2 | 1/1/2 | 1/2/1 |
| all (259) | 178/185/200 | 172/176/190 | 188/193/199 | 152/158/171 | 148/151/173 | 134/147/163 |

Per-file counts equal each read's own summary `solved` (0 mismatches). Group sizes 90 / 78 / 8 / 14 / 97 / 67 / 23 as
pre-registered.

### Matched sampled tokens (my implementation of the pre-registered curve)
k' = k · c_plain(t) / c_arm(t) per theorem, unbiased pass@k', linear interpolation, cap 256. Difference vs plain in pp,
[95 % theorem bootstrap]; per seed, then IQM over the 3 seeds with a stratified (theorems within seed) bootstrap.

**long (90)**
| | k 1 | k 64 | k 256 |
|---|---|---|---|
| logical c12 s0/s1/s2 | +1.8 / +1.6 / +2.3 | +10.0 [5.3,14.9] / +9.9 [5.6,14.9] / +5.2 [1.9,9.0] | +11.1 / +12.7 / +3.4 [−1.1,8.5] |
| logical c6 s0/s1/s2 | +3.1 / +2.2 / +2.9 | +7.4 [3.4,12.2] / +8.1 [3.4,13.6] / +10.3 [5.2,16.0] | +6.6 / +8.0 / +11.4 |
| logical IQM | | c12 **+9.1 [5.9,11.7]**, c6 **+8.3 [5.8,11.6]** | c12 +10.0 [5.5,13.6], c6 +8.4 [5.2,12.4] |
| structural c12 s0/s1/s2 | −1.8 / −0.6 / −1.6 | −1.2 / +0.9 / −1.1 | −1.2 / +0.3 / −0.2 |
| structural c6 s0/s1/s2 | +0.4 / −0.5 / +0.2 | +0.8 / +0.7 / +1.1 | −0.1 / −1.2 / +3.2 |
| structural IQM | | c12 −0.8 [−2.0,1.0], c6 +0.8 [−1.1,2.9] | c12 −0.3, c6 +0.3 |

Plain on long at k 64: c12 0.368 / 0.287 / 0.402, c6 0.218 / 0.241 / 0.179.

**≤ 10 lines (97)**, logical k 64: c12 +3.7 / +2.0 / +2.5 (IQM +2.6 [1.2,4.4]); c6 +7.7 / +10.5 / +10.0 (IQM +9.7
[6.3,13.0]). Structural k 64: c12 −0.9 / −0.8 / −0.8, c6 +0.7 / +2.8 / +1.5.
**Roy (78)**, logical k 64: c12 +6.6 / +5.7 / +2.1 (IQM +5.2 [2.7,7.4]); c6 +5.7 / +8.1 / +7.8 (IQM +7.5 [4.0,10.6]).
**Pelletier (8)** and **batch3 (14)**: logical point estimates +0 to +20 pp, intervals mostly touch 0 (n too small to
call per seed; `rc_count.txt`).

Matched wall-clock (one seconds-per-attempt ratio per job, GPU + checker + env + final Lean): logical on long k 64 +9.4 /
+11.5 / +4.9 (c12), +8.0 / +8.4 / +10.8 (c6) — not systematically smaller than the matched-token gain (prediction 7 not
borne out). Structural on long k 64 wall: −3.8 / −1.0 / −4.7 (c12), +0.8 / −0.3 / +1.1 (c6).

Falsifier (logical ≤ plain at every k on long, tokens): false for all 6 models.

### Compute and sampler statistics (per read; my sums from the rows, GPU s from the job summaries)
| read | sampled tok M | ratio | long ratio | GPU s | batch | peak GB | S-rej / accepted step | L-rej / step | truncated / draws | plain attempts ended by truncation | final Lean rejections |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c12 s0 plain / struct / logical | 15.45 / 29.67 / 27.03 | 1 / 1.92 / 1.75 | 1 / 2.23 / 1.97 | 868 / 2728 / 1976 | 2048 / **1024** / 2048 | 25.8 / 25.5 / 32.0 | 3.1 / 14.3 / 18.7 % | – / – / 16.4 % | .006 / .019 / .032 % | 68 | 12,962 / 22,910 / 0 |
| c12 s1 | 14.14 / 26.88 / 26.19 | 1 / 1.90 / 1.85 | 1 / 2.43 / 2.33 | 777 / 2439 / 1617 | 2048 | 24.0 / 30.9 / 23.8 | 2.9 / 11.7 / 19.5 % | 22.4 % | .009 / .021 / .038 % | 88 | 17,303 / 30,104 / 0 |
| c12 s2 | 14.61 / 26.59 / 25.46 | 1 / 1.82 / 1.74 | 1 / 2.26 / 2.04 | 732 / 2355 / 1594 | 2048 | 28.7 / 42.3 / 33.3 | 2.9 / 15.4 / 19.9 % | 14.5 % | .003 / .009 / .011 % | 33 | 12,822 / 20,950 / 0 |
| c6 s0 | 11.94 / 31.25 / 31.56 | 1 / 2.62 / 2.64 | 1 / 3.27 / 3.13 | 858 / 2428 / 2016 | 2048 | 30.9 / 37.7 / 38.9 | 4.6 / 19.7 / 30.2 % | 14.6 % | **.28 / 1.35 / 1.41 %** | **2,096 (3.2 %)** | 9,605 / 23,620 / 0 |
| c6 s1 | 10.73 / 23.32 / 25.09 | 1 / 2.17 / 2.34 | 1 / 2.78 / 2.82 | 615 / 1882 / 1409 | 2048 | 22.6 / 34.4 / 26.6 | 4.5 / 17.8 / 31.0 % | 21.6 % | **.16 / .61 / .81 %** | **1,124 (1.7 %)** | 14,932 / 30,613 / 0 |
| c6 s2 | 11.60 / 36.11 / 35.35 | 1 / 3.11 / 3.05 | 1 / 3.60 / 3.33 | 668 / 1918 / 1590 | 2048 | 20.8 / 25.1 / 23.3 | 5.2 / 24.7 / 32.6 % | 15.0 % | **.24 / 1.85 / 1.91 %** | **1,747 (2.6 %)** | 9,346 / 20,525 / 0 |

Every guided arm used > 1.25× plain's GPU s and sampled tokens at equal attempts (curves compare at matched budget).
Repeat probability of a with-replacement redraw (job summaries): 0.21–0.26 (c12 structural), 0.32–0.40 (c12 logical),
0.42–0.46 (c6 structural), 0.51–0.54 (c6 logical).

### Proof length (own counters; shortest accepted proof per theorem, theorems solved by all three arms)
Min lines, plain / structural / logical: c12 10.96/11.09/10.86, 10.93/10.68/10.60, 11.04/11.06/10.89; c6 10.28/10.01/9.99,
9.96/9.78/9.72, 9.90/9.62/9.56. Term size (term atoms with type annotations removed; my definition): c12 15.56/15.78/15.34,
15.52/15.12/15.02, 15.82/15.83/15.54; c6 14.42/13.97/13.99, 13.84/13.53/13.49, 13.77/13.35/13.23. Guided proofs are not
longer; the differences (≤ 0.5 term atoms) are small.

### Pre-registered expectations against my recount
| # | expectation | recount | verdict |
|---|---|---|---|
| 1 | plain textbook72 within ±3 of 48/49/54, 43/41/38 | 48/48/53, 43/43/39 | met |
| 2a | logical − plain on long, k 64 tokens ≥ +3 pp in ≥ 2/3 seeds, both caps | 6/6 seeds, +5.2 … +10.3 | met |
| 2b | on ≤ 10 lines the difference < +3 pp | c12 2/3 seeds (s0 +3.7); **c6 0/3 (+7.7, +10.5, +10.0)** | missed at cap 6 |
| 2c | guided-structural close to plain | yes (IQM −0.8 / +0.8 on long) | met |
| 3 | structural captures ≥ ½ of logical's gain on long | structural ≈ 0 in 6/6 | missed (falsified) |
| 3b | per-attempt pass@1 rises more than matched-token; c_logical/c_plain on long 1.3–2.5 | pass@1 yes (+5.7…+9.7 vs +1.6…+3.1); ratio c12 1.97–2.33 in range, **c6 2.82–3.33 above** | partly |
| 4 | plain long k 64 ≈ 0.35–0.6 (c12); logical +3…+12 at 64, +2…+8 at 256 | plain 0.37/0.29/0.40 (s1 below); +5…+10 at 64 ✓; at 256 +3.4…+12.7, **3/6 above +8** | partly |
| 5 | S-rej 1–5 % per accepted step; L-rej 0.5–4 %; final Lean rejections −≥ 80 % | plain S 2.9–5.2 % ✓ (guided arms 12–33 %); **L 14.5–22.4 % of accepted steps** (miss ×4–5); final rejections −100 % ✓ | partly |
| 6 | repeat mean 0.2–0.6 | 0.21–0.54 | met |
| 7 | matched-wall gain < matched-token gain | logical: smaller in 2/6, larger in 4/6 | missed |
| F | falsifier | not triggered | — |

### Findings from the recount (before reading the write-up)
1. **Batch not held fixed across arms**: `best12_s0_structural` ran at batch 1024 (all other reads 2048; log
   `best12_s0_structural_b1024.log`). Solve counts are unaffected in kind (a re-draw), but its matched-**wall-clock**
   curve is charged at the slower batch (structural c12 s0 wall −3.8 pp at k 64 vs −1.0 / −4.7 for s1 / s2; the
   GPU s 2,728 is the largest of the c12 structural reads).
2. **`max_action` 512 truncates above the policy's 0.1 % line at cap 6**: 0.16–0.28 % of plain draws and 1.7–3.2 % of
   plain attempts end by truncation; guided arms redraw 0.6–1.9 % of draws for truncation. Part of the cap-6 guided gain
   (including the ≤ 10-line gain) may be recovery from truncations rather than from the logical check; plain at cap 6
   loses up to 3.2 % of attempts this way. Whether a 512-token action is ever a legitimate step is not shown.
3. The "second check" on the checker is circular under the prefilter (above); the step-level agreement holds (my
   0 / 900 false rejects).
4. Two cap-12 Stage-1 renaming-class overlaps with the evaluation pools (≤ 10 lines only).

## Compare (phase 2: `run_guided_tts.md`, `numbers.md` § guided-tts, `log.md`, `STATUS.md`)

Every number in the write-up names its models (the cap-12 / cap-6 T1 r8 checkpoints, 9.56M ALiBiGPT, `lean_staten`,
from scratch + ladder, training sets named); the only inherited numbers (textbook72 48/49/54, 43/41/38) carry the
`trajectory*` x0 label. Checker named (Lean alone, post-2026-09-27); no cross-date comparison. Expectations were
committed before the first pod (`8ec7c0a6`, 18:10; first pod 18:14:47 in `~/pods.log`); deviations (batch 1,024 rerun,
added draws-based wall variant) are logged when they happened.

| claim (write-up) | my value | verdict |
|---|---|---|
| plain textbook72 48/48/53, 43/43/39; sanity ±3 ✓ | 48/48/53, 43/43/39 | reproduces |
| per-file solved@256 table (18 rows) | identical | reproduces |
| long, k 64 tokens, logical − plain +10.0/+9.9/+5.2 (c12), +7.4/+8.1/+10.3 (c6) | identical | reproduces |
| IQM +9.1 [+3.7, +13.5] c12, +8.3 [+4.1, +14.0] c6 | +9.1 [+5.9, +11.7], +8.3 [+5.8, +11.6] | point estimates reproduce; my theorem-within-seed bootstrap is narrower (theirs also resamples attempts — conservative) |
| k 256 +11.1/+12.7/+3.4, +6.6/+8.0/+11.4; IQM +10.0 / +8.4 | identical | reproduces |
| structural − plain on long −1.2/+0.9/−1.1, +0.8/+0.7/+1.1 (IQM −0.8 / +0.8) | identical | reproduces |
| Roy +5.2 / +7.5; ≤ 10 lines +2.6 / +9.7 (k 64 IQM) | +5.2 / +7.5; +2.6 / +9.7 | reproduces |
| batch3 +11.8 / +13.7, Pelletier +10.7 / +2.7 | per seed batch3 +11.0/+17.0/+9.5, +12.8/+10.7/+20.3; Pelletier n = 8 | reproduces in sign; n = 14 / 8 — "✓ on batch3" rests on intervals that nearly touch 0, say so |
| MDD on long ≈ 2.7 pp at k 64 | my per-seed theorem-bootstrap half-widths ≈ 4–5 pp; IQM interval half-width ≈ 3 pp | not independently derived as stated; every headline per-seed difference except c12 s2 (+5.2, CI [1.9, 9.0]) clears even the wider band |
| matched wall-clock long k 64: logical +9.1 / +8.8, structural −3.4 / +0.7 (s0-structural cell excluded) | logical per seed +9.4/+11.5/+4.9, +8.0/+8.4/+10.8; structural incl. the excluded cell −3.8/−1.0/−4.7 | reproduces within ≈ 0.5 pp |
| "at k = 1 every guided arm loses on wall-clock" | structural loses in 6/6; logical loses in 4/6, gains +1.1 / +0.5 in c6 s1 / s2 (my seconds include env + checker) | differs slightly — "logical loses at k = 1 at cap 12 and is ≈ even at cap 6" |
| falsifier not met (0/3 seeds at each cap) | not met in 6/6 | reproduces |
| per-attempt acceptance plain 32.3–38.1 %, logical 42.2–47.6 % (c12) etc. | 32.3–38.1 %, 42.2–47.6 %; c6 29.7–33.5 / 41.2–44.6 % | reproduces |
| 52–59 % of logical attempts end at the rejection cap | 52.4–58.8 % | reproduces |
| guided-logical S 13.8–21.7 %, L 10.0–15.8 % of draws | S 13.8–21.7 %, L 10.0–15.8 % (my per-accepted-step figures 14.5–22.4 % are a different denominator) | reproduces |
| rescued structural attempts carry wrong steps: 20,525–30,613 rejected vs plain 9,346–17,303 | identical | reproduces |
| guided-logical: 0 Lean-rejected finished proofs | 0 in 6/6; my Lean re-check 0 / 1,729 logical texts rejected | reproduces |
| **checker: "every Lean-rejected plain/structural proof was flagged; no flagged proof was Lean-accepted"** | true of the files, but Lean rejected **0** finished texts in all 12 reads: every rejection is a prefilter rejection (`rej N (filter N)` in all 11 readable logs), and the prefilter applies the same `lean_prefilter._term` rules as the step checker | **not supported as worded** — it is a tautology under `LEAN_PREFILTER=on`, not a check against Lean |
| checker gate 0 false rejects / 0 misses on 314,541 steps | my sample: 900 / 900 checker rejects Lean-rejected, 180 / 180 passes accepted | consistent (sample); scope: atomic `have` steps only, passes sampled at 25 % |
| truncation: plain cap 6 0.16–0.28 % of draws, "above the policy's 0.1 %", guided 0.6–1.9 % redrawn and charged | identical; plus 1.7–3.2 % of plain cap-6 attempts end by truncation | reproduces; disclosed but `max_action` not raised. Mitigation I checked: structural also redraws truncations and gains ≈ 0 on long, so truncation recovery does not drive the logical gain there; at cap 6 ≤ 10 lines structural is +1.6, a possible small share |
| with-replacement repeat 0.32–0.40 / 0.51–0.54 (logical), 0.21–0.26 / 0.42–0.46 (structural) | identical | reproduces |
| guided proofs not longer (lines, term size) | lines identical to theirs; my term-size counter (different definition, scale ≈ 2×) gives the same ordering, logical ≤ plain by ≤ 0.5 | reproduces |
| compute table (GPU s, tokens, ratios 2.18×/1.78× etc.) | identical from the summaries; tokens re-summed from rows equal `sampled_tokens` | reproduces; every guided arm > 1.25× plain at equal attempts is flagged ✓ |
| "on long, guided tokens per attempt 2.0–2.3× (c12), 2.8–3.3× (c6)" | logical 1.97–2.33 / 3.13–3.33; structural 2.23–2.43 / 2.78–3.60 | reproduces (logical) |
| spend 9.07 A40-h, $4.45; 4 pods | 4 `gt-*` pods in `~/pods.log`; hours not derivable from artifacts | not derivable (plausible) |
| expectations scoring (run file) | 1 ✓, 2 ✓ except ≤ 10 at cap 6 ✗, 3 ✗, k 256 above range, wall ✗ | reproduces; but #4's "plain long k 64 ≈ 0.35–0.6" (c12 s1 0.287 below), #3's ratio (cap 6 above 2.5) and #5's L-rate are scored only in `log.md`, not in the run file |

## Verdict

**Stands.** On these six models (cap-12 and cap-6 T1 r8, 9.56M ALiBiGPT, `lean_staten`), at matched sampled tokens,
guided-logical redraws beat plain resampling on **long** (90 release theorems > 10 lines) in 6 / 6 models: +5.2 to
+10.3 pp at 64 plain-equivalent attempts, +3.4 to +12.7 pp at 256; IQM +9.1 (cap 12) and +8.3 (cap 6). Matched
wall-clock agrees to within ≈ 0.5 pp. Guided-structural is indistinguishable from plain on long (|Δ| ≤ 1.2 pp per seed).
Every proof the run counts that I checked passes Lean: 5,211 texts, at least one per solved (model, arm, theorem).
The negative controls fail as they should. The per-step checker made no false reject on my 900-step sample. The
gains on Roy and on ≤ 10 lines at cap 6 also stand. No hard-constraint violation.

**Reword.**
1. "Every Lean-rejected plain/structural proof was flagged; no flagged proof was Lean-accepted" (run file, numbers,
   log, STATUS) → "every finished proof the gate rejected was rejected by the prefilter, whose rules the step checker
   shares; Lean itself rejected none. The checker's soundness evidence is the step-level agreement test." As written it
   reads as a whole-proof check against Lean, and it is not one.
2. "At k = 1 every guided arm loses on wall-clock" → logical loses at cap 12 (4 / 6 overall) and is about even at
   cap 6 (s1 and s2 slightly positive under job seconds that include env + checker).
3. batch3 (n = 14) and Pelletier (n = 8) should be described as "consistent with" a gain, not "✓". The batch3 IQM
   intervals reach +0.3 and +1.2; per-seed intervals touch 0 in 4 / 6 models.
4. Put the misses that only `log.md` scores into the run file's expectations paragraph: plain long k 64 below the
   predicted range for c12 s1; c_logical / c_plain on long 2.8–3.3 at cap 6 (predicted ≤ 2.5); the logical rejection
   rate of plain steps 3.1–4.8 % of draws (predicted 0.5–4 %).
5. The cap-12 textbook72 / ≤ 10 numbers should carry the 2-theorem renaming-class overlap with `train_k12.jsonl`
   (premise order and renaming; it does not affect long or any arm difference).

**Not supported.** Nothing in the headline. The only unsupported statement is the whole-proof "proof-level agreement"
in Reword 1.

**Settings.** One cell (`best12_s0_structural`) ran at batch 1,024. The run disclosed this and excluded the cell from
wall-clock comparisons, which is adequate. `max_action` 512 truncates 1.7–3.2 % of plain cap-6 attempts. That is above
the policy's 0.1 % line; the run disclosed it but did not raise the cap.

**Next measurements.**
- One plain read with `LEAN_PREFILTER=off` (or `shadow`) on one model, ≈ 15 A40-min. Lean then judges the flagged
  whole proofs and closes the circular check.
- A plain and logical pair at cap 6 with `max_action` ≈ 1,024 on one seed. It would measure how much of the cap-6
  gain on ≤ 10 lines (+9.7 pp, versus +2.6 at cap 12) is truncation recovery rather than the logical check.
- The open design question is why guided-structural rescues attempts but not solves (it yields 20–30 k more
  Lean-rejected finished proofs per read). An arm that redraws structural rejections but stops an attempt at its first
  flagged logical step would show whether logical redraws are needed, or whether early termination alone helps.
