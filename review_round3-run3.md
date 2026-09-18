# Review of round3-run3 — base generalisation by pattern class, 72 Stage-1 draws, no RL

Reviewer session, 2026-09-18. Phase 1 (§Recount) was written from `~/review/round3-run3` (executor write-ups removed) and
committed before `run3-3.md`, `numbers.md`, `log.md`, `STATUS.md`, `QUESTIONS.md`, `artifacts/r3_3/summary.json`,
`posthoc_predictors_either_pass.json`, `run3_3_analysis.py` output or any figure was opened. Inputs: `BRIEF_base-generalisation.md`,
`preregistration/round3-run3.md` (commits `16378b0`, addendum `0c62ffb`), the code, `data/r3_3/`, `data/p2/`, `artifacts/r3_3/` (72 training
logs, 144 coverage files, pod queue logs), `artifacts/ign/cov_*`, `ckpts/r3_3/`. The addendum text itself states the reductio main-pass count
(12 / 24), so that one number was known before my recount.

Reviewer code (nothing shared with the executor except `nd_verify`): `review_r3_3_recount.py` (pools, splits, training-file scan, training
logs + checkpoint `extra`, coverage recount, ignition-study recount), `review_r3_3_tables.py`, `review_r3_3_extra.py`; parser, dependency
pruning, strict-reductio / strict-derived-ORE predicates, depth counter and renaming key are my own (`review_run5_recount.py`); the eight
first-half predicates were re-implemented from the pre-registration text. Outputs: `artifacts/review_r3_3/*.json`, `tables.txt`.
Counting rule as pre-registered: a draw *generalises* iff ≥ 1 stored proof verifies and carries the pattern on the dependency-pruned proof;
hits = Σ `count` of such proofs; rate = hits / Σ `n_tried`.

## Recount

### R0. Hard constraints, gate 0, completeness

| check | result |
|---|---|
| `nd_verify` tree hash, branch head vs `origin/main` vs `upstream/main` | equal (`9437bb7…`) |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf06…`, same as `dan_novelty`; last touched by `ca93f83` (2026-09-15). No test-file run in this run |
| expectations before the run | pre-registration committed 05:16:17 UTC; first pod ready 05:23:55 UTC. One amendment at 05:28 (predicate definition, before any sample). Deep-pass addendum committed 09:45:47; first deep job started 10:24:36 (`podlogs_r33b`) |
| supervised cap / pattern in Stage-1 data (my predicates, pruned and unpruned, all 155,000 proofs of each file) | max 6 lines in all three; `train_depth3_f0_a1` depth-3 **0**; `train_reductio_f0` strict reductio **0**; `train_derived_ore_f0` strict derived-ORE **0**. 1,550 proofs per file re-verified, 0 failures |
| first halves in Stage-1 data | also **0**: no line at depth ≥ 3 in the depth-3 set; no NEGI on `~goal` (with or without DN) in the reductio set (19 `AS ~goal` lines in 155,000); no ORE on a derived disjunction in the derived-ORE set. So a first-half attempt is itself out-of-distribution behaviour, not something the training data licenses |
| 72 Stage-1 draws | 72 logs, each 30 eval lines to step 6000, one `saved`; 72 checkpoints whose `extra.args` give `--mode abs --steps 6000 --bs 128 --cap 6`, seeds 30–53, the three pre-registered data files, `heldout.jsonl` |
| 144 coverage files | every file has exactly the pool's names and prompts (300 / 700 / 300 / 300 / 52 / 45), no duplicates, `n_tried` = 2,000 (main) or 20,000 (deep) on every record, log ends `DONE`, Σ `count` = `n_ok` everywhere. **5,299 + 4,599 + 302 + 142 + 45 + 92 distinct stored proofs re-verified: 0 failures; 0 pattern-label differences (3 patterns) between my predicates and the stored `pat`; 0 differences between my first-half counts on verified proofs and `fh_ok_by_pred`** |
| splits by renaming class | the four sampled pools share 0 classes with any of the three training files, with `heldout`, `validation_36` or the test prompts. (Inherited, not this run's: the campaign training files share 47–57 classes with `test_short`; nothing here touches the test files) |
| job failures | no traceback / OOM / `FAILED` in any log. `cov depth3 s42 p1` first ended after 2 records (07:07, rc = 0) and was resumed at 10:58; the file is complete. It finished **after** the addendum was written — harmless (s42 has 0 hits) but the addendum's "depth-3 part 1 shows 5 of 15 with 1–2 hits" was stated on 23 draws |

No hard-constraint violation. One reproducibility gap: **`fh_by_pred` (first-half counts over unverified samples) cannot be re-derived from
pulled files** — failures are not stored. Everything in E4 / E7 that uses a first-half *rate* rests on the executor's predicate code
(`patterns2.firsthalf`, which I read: it matches the pre-registration) plus my check of the verified subset.

### R1. Pools

| pool | recount |
|---|---|
| depth-3 | part 1 = first 300 of `targets_depth3.jsonl`, part 2 = the other 700; 1,000 renaming classes; all 1,000 generator proofs verify and are depth 3. By *minimum* length part 1 is 198 × 7 + 102 × 8 (the pre-registration's "166 × 7 + 134 × 8" is the generator's length). Required@8 stratum recomputed from the depth-≤ 2 search file: **142** (97 in part 1), equal to the `stratum` field; 136 of the 142 have minimum 8, **6** have minimum 7 |
| reductio | 300 classes, 300 oracle proofs verify and are strict reductio, 16 schemata, 7-line = `nand_neg` 26 + `negimp_to_pos` 26. `deep52` = exactly those 52 |
| `deep45` | equals the set of targets hit by any of the ignition study's 16 depth-3 draws (my recount of `artifacts/ign`: 45 targets). Only **3 of 45** are required@8 |
| derived-ORE strict, cap 6 | 363 strict candidates (= my predicate on the pruned generator proofs). Oracle: 363 reachable, 0 timeouts, **25 `requires`**, all 25 unrestricted proofs carry the pattern, 338 restricted proofs verify, none carries the pattern, 0 inconsistencies. Pool = 25 required (3 × 7, 16 × 8, 3 × 9, 3 × 10 lines) + **275 optional, all 7-line, each with a pattern-free proof of the same length** |

The depth-3 pool by what the shortest proof needs (unrestricted minimum / depth-≤ 2 minimum at bound 8): 402 targets 7 / 7 (pattern optional
at 7 lines), **167 targets 7 / 8 and 6 targets 7 / none (the 7-line proof needs depth 3)**, 104 targets 8 / 8, 136 targets 8 / none, 185 unknown.

### R2. Headline counts (E1, E2)

| class (pool, samples per draw) | draws with ≥ 1 hit | 95 % CP | pre-registered |
|---|---|---|---|
| depth-3, parts 1 + 2 (1,000 targets, 2.0M) | **15 / 24** | 0.41–0.81 | 12–18 ✓ |
| depth-3, part 1 alone (300, 600k) | 15 / 24 | 0.41–0.81 | — |
| reductio (300, 600k) | **12 / 24** | 0.29–0.71 | 5–11 ✗ (one above) |
| strict derived-ORE, cap 6 (300, 600k) | **0 / 24** | 0.00–0.14 | 18–24 ✗✗ |
| reductio deep (52, 1.04M) / either pass | 17 / 24 / **17 / 24** | 0.49–0.87 | — |
| depth-3 deep (45, 0.9M) / either pass | 18 / 24 / **19 / 24** | 0.58–0.93 | — |

**E2 fails.** The registered intervals (0.41–0.81 vs 0.29–0.71) overlap almost entirely; Fisher exact p = 0.56 (main), 0.74 (either
pass). By the pre-registration's own rule the base-level claim "structural patterns are generalised more readily" is dropped.

Draws zero in both passes: reductio s30, 33, 36, 43, 46, 50, 52 (7); depth-3 s32, 39, 42, 44, 50 (5). Same-seed draws of the two sets do
not co-generalise (Fisher p = 1.0), as expected since only the seed is shared.

### R3. What the hits are: a one-line length horizon, in both classes

- **Every one of the 11,320 depth-3 hits and 899 reductio hits of the main pass is a 7-line proof** — one line beyond the supervised cap.
  No draw of either class produces a single verified 8-line pattern proof in 600k–2M samples. E3's "never on an 8-line schema" holds
  (416 hits `nand_neg`, 483 `negimp_to_pos`, 0 elsewhere; deep pass the same two), but it is not specific to reductio: depth-3 has 0 hits on
  its 240 targets with minimum 8 as well. On the reductio pool nothing but strict reductio is ever verified (`n_ok` = hits in all 24 draws).
- **Depth-3 hits by stratum:** 10,111 on the 167 "7 / 8" targets, 77 on the 6 "7 / none" targets, 1,132 on the 402 "7 / 7" targets (beside
  2.50M pattern-free verified samples there), 0 elsewhere. The registered required@8 stratum gets **77 of 11,320 hits, in 4 / 24 draws**
  (0.05–0.37) — all on its six 7-line members; its 136 eight-line members get none.
- **Like-for-like at the horizon** (targets whose 7-line proof needs the pattern): depth-3 173 targets, **12 / 24** draws with a hit;
  reductio 52 targets, **12 / 24**. Identical counts, with depth-3 having 3.3× the sample budget on such targets. Pooled per-sample rate on
  them: depth-3 1.2·10⁻³, reductio 3.6·10⁻⁴; median among generalisers 3.7·10⁻⁴ vs 1.9·10⁻⁵. So if a class difference exists at the base
  level it is in the *rate among generalisers* (more depth-3 draws at ≥ 10⁻⁴: 6 vs 2 of 24 in the main pass, 7 vs 2 deep; Fisher p ≈ 0.25),
  not in the probability of emitting the pattern at all.
- **Derived-ORE's 0 / 24 is not a like-for-like zero.** Its pool holds 3 seven-line required targets (6,000 samples per draw; floor
  1.7·10⁻⁴) and 22 longer required ones beyond the horizon; the 275 optional targets all have a pattern-free 7-line proof, which the draws
  find readily (108–170 of 300 targets solved per draw, 1.61M verified samples in total, 0 strict, 4 loose derived-ORE). Required targets:
  0 of 600 draw × target pairs solved. The draws do attempt it (`ore_on_derived` on 11,240 samples of required targets). What the number
  supports: strict derived-ORE is never chosen when optional (contrast depth-3: 1,132 optional hits) and is below ≈ 10⁻⁴ where required at
  7 lines. It does not support a class ranking against the other two.
- **Concentration.** Rates span 2.7 (reductio) and 3.7 (depth-3) decades — E3's span ✓. Two reductio draws (s47, s49) carry 874 of 899 main
  hits; s49 has 387 of 453 on one target. Depth-3: s40, s52, s36 carry 93 %. 8 of 12 reductio and 6 of 15 depth-3 generalisers have 1–3 hits.

### R4. Deep pass (addendum)

| | recount | registered |
|---|---|---|
| DA1 reductio main-zero draws with a deep hit | **5 of 12** (s32, 41, 45, 48, 53) | 3–7 ✓ |
| DA2 ≥ 2 main hits confirmed / exactly 1 confirmed | 7 of 7 / **5 of 5** | all / 3–5 ✓ |
| DA3 depth-3 main-zero draws with a deep hit | **4 of 9** (s41, 43, 46, 49); s30 has 1 main hit, 0 deep | 2–5 ✓ |
| DA4 deep / main rate ratio, draws with ≥ 20 main hits on the deep pool | reductio 1.06, 1.02; depth-3 0.92, 1.05, 1.12, 1.00, 0.83, 1.03, 1.07 | [0.5, 2] ✓ |
| DA5 reductio zero in both passes | **7 of 24** < 8 → the registered consequence applies | |

The deep pass does what it was built for: the zero / non-zero split at 600k samples is a detection-floor artefact for roughly a third of
the "zeros" in both classes, the main-pass zeros are Poisson-consistent with the deep rates (expected main hits 0.1–1.3), and rates are
reproducible to ± 20 % across sampling seeds. "Generalises" is therefore a statement about a budget, and the fraction moves from
0.50 → 0.71 (reductio) and 0.63 → 0.79 (depth-3) with a further ≈ 10× samples on the easy targets. One asymmetry to keep in mind: `deep52`
is chosen by length alone, `deep45` by *having been hit by other draws of the same recipe* (3 / 45 required@8); both are a priori with
respect to this run, but the depth-3 deep pool is outcome-selected and only 30 of the 76 targets hit in this run's main pass lie in it.

### R5. Predictors (E4, E7)

| | reductio | depth-3 |
|---|---|---|
| final held-out loss vs indicator (registered: \|ρ\| < 0.3) | ρ = 0.03 ✓ — but the logged value has 4 decimals and takes 7 distinct values in 0.0822–0.0829 | ρ = −0.10 ✓ — 8 values in 0.0822–0.0831 |
| full-precision held-out mean from the breakdown vs indicator / either-pass | −0.34 (p 0.11) / −0.36 (0.09) | −0.24 (0.26) / **−0.42 (0.044)** |
| primary first-half rate vs indicator (registered: ρ > 0.5) | **0.14 (p 0.52)** ✗ | **0.04 (p 0.87)** ✗ |
| same, outcome from the independent deep pass | −0.10 (0.67) | 0.40 (0.057); vs deep hits 0.41 (0.046) |
| first-half rate vs log rate among generalisers | 0.49 (0.11) | 0.53 (0.043) |
| E7a first-half ≥ 10× verified rate in every generaliser | min 16× ✓ | min 20× ✓ |
| E7b zero-hit depth-3 draws have `d3_written` < 10⁻⁴ | — | **1 of 9** ✗ (the others 4·10⁻³ – 7·10⁻²) |

E4's positive half fails for both classes: zero-hit and generalising draws attempt the first half at the same rates (reductio 2·10⁻³–2·10⁻²
in both groups; depth-3 zero-hit draws open a third box in up to 7 % of samples and never close one validly). The other registered
predicates do no better (|ρ| ≤ 0.22 for reductio, ≤ 0.33 for depth-3). The negative half "passes" on a variable with no variance; on the
full-precision loss the sign is consistently negative (lower loss, more generalisation) at |ρ| 0.24–0.42, which n = 24 cannot separate
from either 0 or the 0.3 threshold.

Post hoc only (38 per-rule / per-class losses × 2 classes scanned, no correction): depth-3 draws with lower held-out loss on **NEGI lines**
generalise more — ρ = −0.74 (permutation p ≈ 10⁻⁴; ≈ 0.008 after Bonferroni over 76), −0.42 against the independent deep-pass indicator,
−0.62 either pass. The losses involved are 10⁻⁴–10⁻³, there is no mechanism on the table, and it is one survivor of a scan; it is a
candidate to pre-register on fresh draws, not a finding. The reductio analogue (AS-line loss, −0.45) does not survive correction.

### R6. External stratum (ignition study, recounted from `artifacts/ign/cov_*`)

Reductio 4 / 11 (0.11–0.69) as quoted in the brief. Depth-3 "10 / 16" pools four training sets: on `f0_a1`, the recipe used here, it is
**5 / 10** (0.19–0.81); the other three sets give 5 / 6. One reductio file has 3.0M samples rather than 600k. Neither stratum contradicts
the new counts.

### R7. Not derivable in phase 1

Spend (pod-hours are not in the pulled files I opened); first-half rates over unverified samples (R0); whether the bucket upload is complete.

### Phase-1 reading

The run is clean and the counts will reproduce. On the brief's question: at cap 6 and f = 0, about half of draws emit each of the two
patterns at 600k samples and 70–80 % with ≈ 1M more samples on easy targets; the intervals do not separate and on like-for-like targets
the two classes are tied at 12 / 24. What separates outcomes is not class but **length: every pre-RL pattern proof in either class is
cap + 1 lines**, the registered required@8 depth-3 stratum is reached only through its six 7-line members, and derived-ORE's zero reflects a
pool with three such targets. No registered draw-level property predicts generalisation.

## Compare (phase 2 — `run3-3.md`, `numbers.md` §Round 3 — Run 3, `STATUS.md`, `QUESTIONS.md`, read after commit `0d46113`)

| claim (executor) | recount | status |
|---|---|---|
| generalising draws: depth-3 15 / 24 (0.41–0.81), reductio 12 / 24 (0.29–0.71), strict derived-ORE 0 / 24 (0–0.14) | same | **reproduced** |
| hits per draw, both vectors (depth-3 parts 1 + 2 summed; reductio) | identical in all 48 entries | reproduced |
| either pass 19 / 24 and 17 / 24; zero in both s32, 39, 42, 44, 50 and s30, 33, 36, 43, 46, 50, 52 | same seeds | reproduced |
| deep rescues 4 of 9 (s41, 43, 46, 49) and 5 of 12 (s32, 41, 45, 48, 53), with the stated hit counts | same | reproduced |
| confirmation 12 / 12, 7 / 7, 2 / 3 (s30), 5 / 5; rate ratios 0.83–1.12 and 1.06, 1.02 | same | reproduced |
| part 1 11,206 hits, part 2 114; no draw rescued by part 2; required@8 77 hits in s36, 38, 40, 52; 76 targets ever hit | same | reproduced |
| reductio: 45 (draw, target) pairs, 31 distinct targets, only `nand_neg` / `negimp_to_pos`, 0 on 8-line-or-longer schemata; 387 of s49's 453 on one target | same | reproduced |
| frozen@256: depth-3 9 draws > 0 (max 27), reductio s39 1, s40 1, s47 13, s49 5 | same | reproduced |
| derived-ORE oracle: 363 → 25 required (3 / 16 / 3 / 3), 0 inconsistencies; loose derived-ORE 4 hits in 2 draws | same | reproduced |
| self-check: 211 depth-3 + 137 reductio distinct pattern proofs, 0 failures | same counts with my verifier loop and predicates; plus the 10,131 stored non-pattern proofs (10,479 distinct proofs in all) | reproduced |
| predictors: loss −0.10 / 0.02; first-half 0.04 / 0.14; among generalisers 0.53 / 0.49; NEGI −0.74, either-pass −0.62; AS −0.45 | same to two decimals (mine: 0.03 for reductio loss) | reproduced |
| first-half rates and E7 ratios (min 21 / 16) | min 20 / 16 with `n_tried` rather than `n_parsed` as denominator; **not re-derivable beyond the verified subset** (R0) | consistent |
| thresholds: rate ≥ 10⁻⁵ depth-3 7 / 24, ≥ 10⁻⁴ 4 / 24 | on the 2M denominator, yes; on part 1 alone (the same 600k budget as reductio) 9 / 24 and 6 / 24 — the 1.4M part-2 samples that hit almost nothing dilute the depth-3 rate 3.3× | reproduced; denominator matters |
| ignition stratum "depth-3 10 / 16" | 10 / 16 pools four training sets; on this run's recipe (`f0_a1`) it is 5 / 10 | reproduced; not disclosed |
| gate 0: own first pod after the pre-registration commit; the flagged pod is run 2's | `~/pods.log`: r33a 05:23:43, commit 05:16:17 | confirmed |
| spend ≈ 28 pod-hours ≈ $14; pods deleted; bucket holds 72 checkpoints, artefacts, data | pod-log start times match; no `r33*` pod on the account at 13:50 UTC; bucket lists 72 checkpoints, 144 coverage files, 7 data files | confirmed |
| all expectation marks (E1–E7, DA1–DA5) | same marks | reproduced |

Every number in the write-up reproduces. The executor's E-marks are honest, including the two large misses (derived-ORE 18–24 → 0; first-half
ρ > 0.5 → 0.04 / 0.14), and the NEGI correlation is labelled exploratory with its either-pass weakening reported.

**Where my reading differs from `run3-3.md`.**

1. *"The full depth-3 pool changed nothing: 99 % of hits … lie in the 300 shortest"* and *"every reductio hit is on a 7-line target"* are
   reported as two separate facts. They are one fact, and it is the main structure in the data: **all 12,219 main-pass pattern hits in
   both classes are 7-line proofs (cap + 1)**, and 90 % of the depth-3 hits fall on the 173 targets whose 7-line proof needs depth 3 while the
   depth-≤ 2 alternative is 8 lines (never sampled once on those targets). The write-up does not mention written length for depth-3.
2. *"The pattern, not its class, sets the base rate"* and *"'or nothing' fits … every strict derived-ORE draw."* The derived-ORE pool has
   **three** required targets inside the 7-line horizon (6,000 samples per draw, floor 1.7·10⁻⁴); the other 22 required ones are 8–10 lines,
   where depth-3 (240 targets) and reductio (248 targets) also score exactly 0. On like-for-like targets depth-3 and reductio are tied at
   12 / 24; derived-ORE has not been measured like-for-like. What does stand is the weaker statement in R3: strict derived-ORE is never chosen
   when a same-length alternative exists (0 of 1.61M verified samples; depth-3 is chosen 1,132 times in 7 draws in the analogous stratum).
3. The required@8 stratum result (4 / 24, 0.05–0.37) is given as a count without the consequence: on the stratum the *previous reviews asked
   for*, depth-3 generalises in **fewer** draws than reductio does on its all-required pool (Fisher p = 0.03) — entirely because 136 of its
   142 targets are 8-line. Any future "base rate on the required pool" must be quoted per minimum length.
4. `deep45` is outcome-selected by sibling draws (R4); the either-pass depth-3 figure (19 / 24) is therefore a little more favourable to
   depth-3 than reductio's 17 / 24 by construction. It does not change E2.

## Verdict

**The counts are right, the pre-registered test is decisive, and the run's discipline is good** (expectations and addendum committed before
their jobs, a priori deep pools, honest ✗ marks, complete pulls, $14 of $50). E2 fails at n = 24 each; per the brief the base-level class
claim is dropped, and clause (2)'s "or nothing" is a statement about a sampling budget for about a third of apparent zero-rate draws.

Two conclusions in `run3-3.md` go past the data: the derived-ORE zero is read as a property of the pattern when the pool gives it three
reachable required targets, and the dominant regularity — **pre-RL pattern proofs exist only at cap + 1 lines, in every class, in all 72
draws** — is not stated. That regularity also re-reads earlier results: run 5's and the ignition study's "7-line entry" for reductio is not a
property of `nand_neg`; it is where the base model's length reach ends. Whether a draw "generalises a pattern" is, in these data, whether it
emits a valid proof one line past the cap that happens to need the pattern; no registered draw-level property predicts it, and the one
post-hoc candidate (NEGI-line loss, ρ = −0.74 → −0.42 on independent samples) needs fresh draws.

Standards: start-index-normalised counts ✓ (`coverage.py` normalises before counting; my recount agrees); expectations before the run ✓; splits
disjoint by renaming class ✓; "every count reproducible from pulled files" ✓ for all hit counts, **✗ for first-half rates** (failures are not
stored; a 1-in-100 sample of failed strings per target would fix it at negligible size). Frozen control, base reachability and two seeds do
not apply (no RL; 24 seeds).

## Next measurement

One experiment, reusing the 72 bucket checkpoints, ≈ $5–8, no training:

**Length-matched required pools, deep sampling.** For each class build a schema pool of **≥ 50 targets whose minimum proof is 7 lines and
needs the pattern at bound 10**, and a second of ≥ 50 at **8 lines** (depth-3: the existing 173 + 136; reductio: the existing 52 + the
8-line schemata; strict derived-ORE: new schema instances, since the generator yields only 3 — see the run-2 note that generator pools are
mostly redundant). Sample all 24 draws per class at 20,000 per target. Pre-register: (a) 7-line generalisation fractions for the three
classes with intervals — the first like-for-like class comparison; (b) the 8-line fraction, expected ≈ 0 / 24 in every class if the horizon
reading is right, and > 0 somewhere if "7-line entry" is schema-specific; (c) NEGI-line loss vs the depth-3 7-line indicator, registered as
ρ < −0.4, tested on these independent samples. If (b) is ≈ 0 everywhere, the follow-up that speaks to the SPAR question is a cap-7 Stage-1
on the same seeds: does the horizon move to 8 lines (length reach is what RL has to elicit from) or stay at the schemata?
