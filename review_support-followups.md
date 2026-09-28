# Review — `support-followups`

Reviewer: agent:claude (reviewer role), independent session. Phase 1 written 2026-09-28 13:00–13:50 UTC in
`~/review/support-followups` (executor write-ups removed) before opening `run*.md`, `numbers.md`, `log.md`,
`STATUS.md`, `abc_report.txt`, `d_report_*.txt` or any `*summary*.json`. My scripts and their outputs are in
`review/support-followups-recount/` (run from a checkout root; outputs go to `rev_sf/`). I used none of the
executor's analysis code (`sf_*.py`, `support.py` counting, `normalize.py`, `lean_judge.py`); only the model
definition (`model.load_ckpt`), the tokenizer's vocabulary, and the reviewer-owned Lean driver from
`review_sc_leanrecheck.py`.

**Disclosures.** (1) The pre-registration addendum (08:46 UTC) states three seed-0 results of stage C (big s0
0 / 29 survivors, 6 / 82 forward crux, held-out 0.879); I read them as part of the pre-registration. (2) The
session's start-up git status showed the last five commit subjects (e.g. "C seed 1, numbers SF0-SF8, write-up");
they contain no numbers. Nothing else from the executor's write-ups was seen in phase 1.

**Models** (labels as in the pre-registration; all `lean_seq`, cap 6, from scratch, Stage 1 on
`data/p2/train_depth3_f0_a1.jsonl`, 6,000 steps × 128):
base s0 `ckpts/lf/stage1_a1_seq_s0.pt` (3,214,336 params, md5 `9bde44c0…`); base s1 (`fc27e52d…`);
EI s0 `la_T1_sc_s0_r8.pt` (`5cebd7ec…`, base s0 + 8 × k 32 EI); EI s1rerun `la_T1_sc_s1rerun_r8.pt` (`12c13e61…`);
big s0 `ckpts/sf/stage1_big_seq_s0.pt` (`4efb5a1e…`) and big s1 (`05ed8839…`): **25,329,664 params** (8 layers,
d 512, 8 heads), recipe identical to base s0's — I read both checkpoints' embedded `args` (data, steps 6,000,
bs 128, lr 1e-3 → 1e-4, warmup 200, wd 0.1, cap 6, seed 0 / 1). Judge: Lean alone.

## §Recount (phase 1, blind)

### 0. Hard constraints and gate 0

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72` at HEAD = `origin/main`'s; `git diff origin/main HEAD -- nd_verify` empty |
| `nd_verify` used as a judge | no: no `sf_*.py` / `support.py` / `lean_judge.py` / `eval_set.py` import of it. `train.py` imports `verify_text` only to assert that *training records* satisfy the cap (pre-existing take-home code, judges no model output) |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064` = `origin/main`'s; last touched 2026-09-15 |
| evaluation file read in training code | `pod/sf/c_train.sh` passes `--heldout data/p2/heldout.jsonl` to `train.py`; it is read only for the logged val loss (first 2,000 records), no checkpoint selection (the step-6,000 model is saved). Same recipe as base s0's. No transfer-pool file is read by training |
| pre-registration before results | committed `352676c` 04:09 UTC; first run artefact (`d_steps.jsonl`) 04:25, first commit of results 04:37. Addendum `fe0a939` 08:46, before any seed-1 file (first: `c_heldout_greedy_s1` 09:09). `git diff 352676c HEAD` on the pre-registration adds only the addendum |
| split disjointness (my own renaming canonicaliser) | train (155,000 records, 154,494 classes) × transfer pool (383): **0**; held-out (5,000) × transfer: **0**; train × held-out: **0** under first-appearance renaming, **21 classes** if premise order is also quotiented (inherited take-home split; affects base and big alike; the held-out is not a headline quantity here) |

No quarantine condition.

### 1. Lean re-check of every counted proof

All distinct accepted proofs of every new arm (451 — fewer than 100 exist in four arms, so I re-checked all),
from the stored literal `lean_text`, with my own statement builder and one-file-per-chunk Lean driver
(warnings count as failures). Negative controls: a proof with its final `exact` replaced by `exact h1`, and a
`sorry` body — both rejected.

| arm | model | distinct proofs / theorems | Lean accepts | banned tokens | `n_lines` / `term_size` mismatches (my counters) |
|---|---|---|---|---|---|
| A base | base s1 | 50 / 37 | 50 | 0 | 0 / 0 |
| A EI | EI s1rerun | 380 / 147 | 380 | 0 | 0 / 0 |
| B | base s0, T 1.0 | 1 / 1 | 1 | 0 | 0 / 0 |
| C big s0 | big s0 | 7 / 6 | 7 | 0 | 0 / 0 |
| C big s1 | big s1 | 13 / 10 | 13 | 0 | 0 / 0 |

Term size = formula nodes summed over the normalised ND proof's lines (the definition `support.py` documents).
Lengths: A base lines median 8 (max 10), term median 47.5 (max 80), 1 proof shorter than `L_true`; A EI 9 (13),
61 (122), 0 shorter; big s0 7 (10), 35 (79); big s1 9 (11), 63 (89).

### 2. A — seed-1 column (T 0.8, k 10,000, stop 50, batch 4,096, `max_new` 512, sampling seed 101)

One record per theorem per model, all 383 theorems. Peak memory recorded per job: max 17.43 GB.

| quantity | my value | pre-registered expectation | |
|---|---|---|---|
| EI s1rerun solved | **147 / 383** | 145 (125–165) | hit |
| base s1 re-draw solved | **37 / 383** | 37 (32–43) | hit |
| forward crux (base s1 0, EI s1rerun > 0) | **110** (reverse crux 0) | 105 (85–125) | hit |
| survivors solved by EI s1rerun | **29 / 29** | ≥ 24 | hit |
| survivors solved by base s1 re-draw | **2** (la_transfer_543, _1645) | ≤ 2 | hit (at the bound) |
| agreement EI s1rerun vs lost EI s1 (144 solved) | **366 / 383 = 95.6 %** (10 rerun-only, 7 lost-only) | ≥ 88 % | hit |
| agreement EI s1rerun vs EI s0 (121 solved) | **345 / 383 = 90.1 %** | ≥ 85 % | hit |
| agreement base s1 re-draw vs support-curves draw | **377 / 383 = 98.4 %** (3 each way) | ≥ 95 % | hit |

Old seed-1 column recounted: lost EI s1 144, base s1 37, forward crux 107, survivors 28 (EI) / 1 (base) — all as
the pre-registration quotes. New and old forward-crux sets share 97 theorems.

### 3. B — depth on the six longest survivors (base s0, T 1.0, sampling seed 201)

6 × 1,666,667 = 10,000,002 attempts (on top of 200,000 at T 0.8 and 200,000 at T 1.0 each in support-curves).
**1 success in total**: la_transfer_1932 (`L_true` 11), first at attempt 985,640, p̂ = 6.0 × 10⁻⁷. The other five:
0, p < 1.80 × 10⁻⁶ each (95 %, exact). Expectation "0 on ≥ 5 of 6, total ≤ 3": **hit**. No-`<eos>` 44 per million.

The one success is **not the EI's route**: 8 lines, term size 59, shorter than `L_true` 11 and than every EI s0
proof of this theorem (11–12 lines, term 75–78). It re-binds `n63` and `n64` (shadowing), uses a non-sequential
name `n23`, and closes the goal with `n63.elim` on the λ-bound `n63 : ¬¬P` instead of first deriving `¬¬P`
from `P` as the EI proofs do. Lean accepts it (re-checked alone).

### 4. C — the bigger base (T 0.8 then T 1.0, batch 1,024, `max_new` 512)

**Held-out greedy** (`data/p2/heldout.jsonl`, 5,000, k 1, T 0; recounted from per-row files):

| model | overall | L2 | L3 | L4 | L5 | L6 | final val loss (log) |
|---|---|---|---|---|---|---|---|
| base s0 (this run's re-draw) | 0.9090 | 0.994 | 0.989 | 0.951 | 0.924 | **0.687** | 0.0729 |
| big s0 | **0.8792** | 0.999 | 0.993 | 0.975 | 0.958 | **0.471** | 0.0724 |
| big s1 | **0.8842** | 1.000 | 0.997 | 0.979 | 0.960 | **0.485** | 0.0725 |

Expectations: big s0 0.90–0.96 **miss** (below); big s1 0.85–0.93 hit. (The pre-registration quotes base s0 = 0.9088; this run's re-draw gives 0.9090.) The 8× larger model is better at L2–L5,
**worse by ≈ 0.2 at L6 in both seeds**, and has the same val loss: it is not a stronger prover of cap-length
proofs than the base (n = 2 big seeds vs 1 base seed).

**Forward crux (82 theorems, k 10,000, stop 50)** — each theorem exactly once per seed:

| | big s0 | big s1 | union / intersection |
|---|---|---|---|
| solved | **6 / 82** (L 7: 4, L 9: 2) | **8 / 82** (L 7: 4, L 9: 4) | 8 / 6 |
| expectation | 20 (8–40) — **miss** (below) | 2–15 — hit | |

**Survivors (29)** — after the crux pass, 190,000 more at T 0.8 (200,000 total), then 200,000 at T 1.0 if still
unsolved; no (theorem, temperature, sampling-seed) stream repeats:

| | big s0 | big s1 | union |
|---|---|---|---|
| survivors reached | **0 / 29** | **2 / 29**: la_transfer_1932 (T 0.8, 5 hits in 155,408, stopped), la_transfer_2169 (T 1.0, 1 in 200,000, after 0 in 200,000 at T 0.8) | **2** |
| attempts | 28 × 200,000 + 1 × 390,000 (la_transfer_588 covered by two shards, seeds 311 / 331) at T 0.8; 29 × 200,000 at T 1.0 | 28 × 200,000 + 155,408 at T 0.8; 28 × 200,000 at T 1.0 | |
| expectation | 6 (2–14) — **miss** (below) | 0–2 — hit | |

**Falsifier (≥ 15 of 29): does not fire**, per seed or for the union. big s1's la_transfer_1932 proofs are
11 lines, term 65 (EI s0's: 11–12 lines, term 75–78); its la_transfer_2169 proof is 10 lines, term 44.

### 5. Truncation (`max_new` 512; no-`<eos>` per file family × `L_true`)

Strata above the pre-registered 0.1 %: A base s1 L 10 **1.39 %** (8,354 / 600,000; la_transfer_191 53.5 %,
survivor la_transfer_1004 27.7 %), A base s1 L 13 0.39 %; C1 big s0 L 11 **1.25 %** (la_transfer_564 10 %);
C1 big s1 L 12 0.22 %; C2 big s1 T 0.8 L 11 0.11 %; C2 big s1 T 1.0 L 9 0.18 % (survivor la_transfer_149 2.3 %),
L 11 0.15 %. **Every job ran at `max_new` 512**: the pre-registered rule "flag and raise later jobs to 640" was
not applied (check in phase 2 whether it was reported). Effect: truncations are degenerate loops concentrated on a
few theorems; on no survivor that a zero-success claim rests on does it exceed 2.3 % of attempts, so no zero is
at risk, but the A base s1 result on la_transfer_1004 rests on ≈ 7,200 completed attempts, not 10,000.

### 6. D — where the improbability sits (stored per-token log p of base s0; my segmentation and classes)

**Sets** (re-derived from the support-curves raw records): S = **133** distinct EI s0 proofs of the 29
survivors (T 0.8 ∪ T 1.0; 104 at T 0.8 alone) — the stored set equals mine exactly. The pre-registration's
"review: 231 proofs" does not match either count (check in phase 2). C1 = 164 EI s0 proofs of the other 53 forward
crux; C2 = 62 base s0 stage-1 proofs over 45 theorems; **C3** (not pre-registered) = 53 base s0 proofs of 33
forward-crux theorems from support-curves' stage 2.

**Numbers are internally consistent but carry ≈ 0.1–0.5 nat numerical noise.** Token contributions sum to the
stored totals (0 mismatches > 1e-3). The pre-registered check "sum to `sc_secondary.py`'s `logp_T1` to 1e-3"
**fails for 320 of 339** shared proofs (max 0.17 nats). My own CPU fp32 teacher-forced re-score of 30 proofs
(all name offsets, logsumexp) differs from the stored totals by median 0.11, max 0.36 nats (T 1.0; 0.54 at T 0.8)
and from support-curves' by up to 0.33 — three computations, three answers at this level; I read it as GPU
reduced-precision noise, not an error. No survivor's classification is within 0.5 nats of a threshold (nearest:
w1 = −6.47 at T 1.0).

**Classification** (primary unit: each survivor's most base-probable EI proof; steps = `have … ;` / box-opening
head / `exact …` / second `Or.elim` branch opening; my step counts, w1 and s2 equal the stored ones for 29 / 29):

| | T 1.0 (primary) | T 0.8 | expectation |
|---|---|---|---|
| concentrated / mixed / spread | **28 / 1 / 0** (mixed: la_transfer_1004, s2 0.41, w1 −9.8) | 28 / 1 / 0 | concentrated 17 (10–24) — **miss** (above); spread ≤ 8 — hit; compounding (≥ 20 spread) does not occur — hit |
| pre-registered reading | **"a new move"** (≥ 20 concentrated) | same | "mixed, leaning to new move" — the reading is stronger than expected |
| survivors' w1 below C2's 5th percentile (−7.14) | **26 / 29** | 26 / 29 (p5 −8.83) | ≥ 15 — hit |
| worst-3 tokens, primary proofs (87) | logic **51.7 %** (formula 27, rule 18), syntax **31.0 %**, names 17.2 % | logic 52.9 %, syntax 29.9 % | logic ≥ 50 % — hit (by 1.5 points); syntax ≤ 20 % — **miss** |
| worst-3 tokens, all 133 S proofs | logic 53.4 %, syntax 35.1 % | | |
| worst step | box-opening `have` 13, plain `have` 7, `exact` 9 | | |
| survivors' median w1 / median total / median per-step log p excluding the worst | −10.96 / −21.84 / −0.060 | −13.38 / −25.65 / −0.043 | |
| surprisal share over S | syntax 33 %, formula 30 %, rule 22 %, cited names 14 %, fresh names 1 % | | |

**The contrast sets do not separate the survivors from theorems the base does reach.** C1 (EI proofs of
crux theorems the base *does* solve, rarely) is **144 / 164 concentrated**, median w1 **−10.48**, median total
**−21.92**, per-step excluding worst −0.055 — indistinguishable from the survivors' −10.96 / −21.84 / −0.060. C3
(the base's *own* rare proofs of crux theorems) is 38 / 53 concentrated (w1 −7.18); C2 (the base's ordinary proofs)
14 / 62 (w1 −4.64). So "one improbable step in an otherwise near-deterministic proof" is the profile of *any*
rare proof under this base, reachable or not; it does not by itself explain why the 29 survivors are unreached
at 400,000 attempts while the 53 C1 theorems are reached. Stage B adds a concrete counter-example to reading the
EI proof's improbable step as the gate: the base reached la_transfer_1932 by a different, shorter route (§3).

### 7. Model labels in this recount

Every number above names its model; the A "lost EI s1" column (`105be4f3…`) is support-curves' record, read from
`artifacts/sc/s3_*`; the checkpoint itself is not available and I did not verify it.
