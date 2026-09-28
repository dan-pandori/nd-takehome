# Review — run `support-curves`

Reviewer session, independent of the executor. `AGENT_POLICY.md` governs.
Phase 1 was done in `~/review/support-curves`, a copy of the repository with the executor's
write-ups removed (`run_support_curves.md`, `numbers.md`, `log.md`, `STATUS*.md`, …), from the
pre-registration, the code, the data and the raw artefacts only. My scripts are committed as
`review_sc_recount.py`, `review_sc_recount2.py`, `review_sc_passk.py`, `review_sc_leanrecheck.py`.

---

## §Recount

### 0. Hard constraints

| constraint | check | result |
|---|---|---|
| `nd_verify` unmodified | `git ls-tree -r HEAD -- nd_verify` vs `origin/main` | **identical blobs** (`dfa3bc3f…`, `1cfed53b…`) — PASS |
| `nd_verify` not used as a judge | grep over every file this run added (`support.py`, `sc_*.py`, `pod/sc/*.sh`) | the only hit is a comment saying it judges nothing — PASS |
| `artifacts/TEST_RUN_DONE` unchanged | blob vs `origin/main` | **identical** (`1d5cf064…`) — PASS |
| no sibling-owned file edited | `git diff --diff-filter=MDR <merge-base> HEAD` | only `QUESTIONS.md`, `STATUS.md`, `log.md`, `numbers.md` (all append-only run bookkeeping). `ladder_ei.py` / `expert_iter.py` untouched; the broken `origin/dan` import is worked around from outside in `sc_ladder_ei.py` — PASS |
| no evaluation file read in training code | read `ladder_ei.py`'s mix construction, then audited the artefacts: every one of the **542,824** training records in all 16 `mix_*.jsonl` files | **0** prompts from `data/sc/theorems.jsonl`, **0** from `data/ladder/transfer.jsonl`; every record is from `rl_targets.jsonl` ∪ `train_depth3_f0_a1.jsonl`. `found_transfer_*.jsonl` is recorded but never enters the mix — PASS |
| splits disjoint by renaming class | my own set intersection on the `key` field | eval ∩ Stage-1 train (155,000) = **0**; eval ∩ EI targets (4,495) = **0**; eval ∩ held-out (5,000) = **0**; literal `thm` overlap also 0 — PASS |
| gate 0 (expectations written first) | prereg commit `2e87c2f` **18:16:17Z**, first pod `sc1` **18:17:10Z** (53 s later). Addendum 1 `b3fa417` **18:33:20Z**, first stage-1 sample `18:33:34Z` (14 s later) | PASS, both tight but in order |
| budget | `podbudget support-curves`: **20.37 h / $9.99** of ceiling 30 h / $15; balance **$136.49** (floor $100); no pods left running | PASS |

No quarantine condition.

### 1. Theorem set

`data/sc/theorems.jsonl` md5 **`3cb6e7bf3b094ce24ebc0706777a9a70`** — matches the pre-registration.
383 records, 383 distinct names and 383 distinct renaming classes, `L_true` histogram
**7:60 8:60 9:60 10:60 11:60 12:60 13:13 14:10**, 183 `textbook` / 200 `gen`, 20 distinct schemata.
Exactly as pre-registered. `L_true` is inherited from `data/ladder/transfer.jsonl` (`minlen.py`
exact search, `L_true = n_lines ≤ minlen_bound` on all 2,285 records) and is an **upper bound** on
the minimal *Lean* proof length.

### 2. Raw sampling actually on file

My own catalogue of every `artifacts/sc/s*.jsonl` record (2,494 records, **49,715,072 samples**):

| stage | model | ckpt (md5) | model seed | sampling seed | T | k | stop | theorems | samples | successes |
|---|---|---|---|---|---|---|---|---|---|---|
| s1 | base | `stage1_a1_seq_s0.pt` (9bde44c0) | 0 | 0 | 0.8 | 10,000 | 50 | 383 | 3,726,864 | 3,982 |
| s1 | EI | `la_T1_sc_s0_r8.pt` (5cebd7ec) | 0 | 0 | 0.8 | 10,000 | 50 | 383 | 3,094,800 | 126,826 |
| s2a | base | same s0 | 0 | 20 | 0.8 | 40,000 | 5 | 338 | 13,520,000 | 18 |
| s2a | base | same s0 | 0 | 10 | 1.0 | 10,000 | 5 | 338 | 3,378,192 | 36 |
| s2b | base | same s0 | 0 | 11 | 1.0 | 40,000 | 5 | 82 | 3,155,648 | 74 |
| s2c | base | same s0 | 0 | 21 | 0.8 | 150,000 | 5 | 58 | 8,340,672 | 55 |
| s2c | base | same s0 | 0 | 12 | 1.0 | 150,000 | 5 | 58 | 7,188,336 | 106 |
| s2 | EI | same s0 | 0 | 30 | 1.0 | 10,000 | 50 | 82 | 349,264 | 68,961 |
| s2rev | EI | same s0 | 0 | 31 | 0.8 | 50,000 | 5 | 6 | 300,000 | 7 |
| s3 | base | `stage1_a1_seq_s1.pt` (fc27e52d) | 1 | 1 | 0.8 | 10,000 | 50 | 383 | 3,727,104 | 5,941 |
| s3 | EI | `la_T1_sc_s1_r8.pt` (**105be4f3**) | 1 | 1 | 0.8 | 10,000 | 50 | 383 | 2,934,192 | 168,777 |

Every sampling seed that is pooled is distinct (0, 10, 11, 12, 20, 21, 30, 31), and the per-batch
generator seed is `seed·1000003 + n`, so the pooled streams cannot overlap — pooling `(n, c)` across
stages at a fixed temperature is legitimate. Base-attempt totals per theorem on the φ-crux are
**200,000 at T = 0.8 and 200,000 at T = 1.0** (10k + 40k + 150k each).

Counting invariants, checked on all 2,494 records with my own code: `Σ proof counts = n_ok` (0
violations), `len(proofs) = n_distinct_ok` (0), `first_hit = min first` (0), `n_tried = k_requested`
whenever not stopped early (0), `n_ok ≥ stop_at` whenever stopped early (0). My own start-index
normaliser (renumber `N`-labels by order of first appearance) is a **no-op on all 1,196 stored
proofs** and collapses no two counted proofs in any record — no distinct-proof over- or under-count.

### 3. Lean re-check — every counted proof, not a sample

Independently of the run's judging path: **my own** ND-sequent → Lean statement builder (no
`lean_tok`, no `nd2lean`), the **literal sampled text** (`lean_text`) as the proof body — which is
what AGENT_POLICY requires for a `lean_seq` model, and a stronger test than the run's own path,
which Lean-checks `nd2lean.translate(prompt, norm(nd))` — and my own Lean driver with my own
error→theorem mapping and a per-theorem fallback.

| arm | distinct counted proofs | re-checked | Lean accepts | banned tokens | `n_lines` mismatch | `term_size` mismatch |
|---|---|---|---|---|---|---|
| base s0 T 0.8 | 93 | **93 (all)** | 93 | 0 | 0 | 0 |
| base s0 T 1.0 | 94 | **94 (all)** | 94 | 0 | 0 | 0 |
| base s1 T 0.8 | 55 | **55 (all)** | 55 | 0 | 0 | 0 |
| EI s0 T 0.8 | 354 | **354 (all)** | 354 | 0 | 0 | 0 |
| EI s0 T 1.0 | 283 | **283 (all)** | 283 | 0 | 0 | 0 |
| EI s1 T 0.8 | 317 | **317 (all)** | 317 | 0 | 0 | 0 |

**1,196 / 1,196 accepted.** No counted proof is rejected by Lean. "Banned tokens" scans each
accepted source for `sorry`, `admit`, `exact?`, `apply?`, `decide`, `native_decide`, `aesop`, `simp`,
`tauto`, `omega`, `axiom`, `sorryAx` — zero hits, and I treat a Lean *warning* as a rejection too, so
the `lean`-exits-0-on-`sorry` trap cannot hide here. Line counts and term sizes re-derived with my
own counters reproduce the stored values exactly. `nd_verify` was not used by the run and not by me.

### 4. Re-derived quantities vs the pre-registered predictions

All values below are **mine**, from the raw records. Models: **base s0/s1** = the 3,214,336-parameter
from-scratch `lean_seq` GPT `ckpts/lf/stage1_a1_seq_s{0,1}.pt`, cap 6, Stage 1 only; **EI s0/s1** =
8 rounds × k 32 expert iteration from those, `la_T1_sc_s0_r8.pt` / `la_T1_sc_s1_r8.pt`. Judge: **Lean
alone**.

| # | quantity | predicted | **my value** | verdict |
|---|---|---|---|---|
| E1 | EI transfer solved, 8 × 32, full 2,285 pool | 856–965 | **869** (s0), **972** (s1) | s0 in range; s1 +0.7 % above, inside the stated "+1 % under Lean alone" — **holds** |
| E2 | base s0 solved of 383 at k = 4,000, T 0.8 | 80–190 | **39 (10.2 %)** | **MISS, far low** |
| E2′ | base s0 at k = 10,000 | 100–220 | **45 (11.7 %)** | **MISS, far low** |
| E3 | EI s0 at k = 4,000 | 200–320 | **116 (30.3 %)** | **MISS, low** |
| E3′ | EI s0 at k = 10,000 | 230–340 | **121 (31.6 %)** | **MISS, low** |
| E4 | forward crux at k = 4,000 | 60–150 | **81** | holds |
| E4′ | forward crux at k = 10,000 | 50–130 | **82** | holds |
| **E5** | **falsifier**: forward-crux theorems, 0 base successes in **≥ 40,000** attempts at **both** T, p̂_EI ≥ 0.01 | 8 (range 0–19); **fires at ≥ 20** | **37** at the pre-registered ≥ 40,000/T; **29** at 200,000/T (4 × 10⁵ attempts total) | **MISS — the falsifier FIRES**, on either budget |
| E6 | reverse crux; survivors after extra EI attempts | 5–25; then 0–10 | **6**; **2** survive 50,000 more | holds |
| E7 | crossover k: exists for `L_true` 7–9 at 10³–10⁴; none for ≥ 11 | — | **no crossover in any stratum 7–13 within k ≤ 10,000**, either seed | second half holds; **first half MISSES** |
| E8 | theorems solved at `L_true` ≥ 13 (23), any model, any k | 0–2 | **1** (`la_transfer_1126`, `L_true` 13, EI only, both seeds) | holds |
| E9 | base T 1.0 vs T 0.8 on the forward crux | strictly more, < 3× | **33 vs 18 theorems = 1.83×**; per-attempt success rate **3.30×** | holds on theorem count; **above 3× on the rate** — the metric must be named |
| E10 | seed 0 vs seed 1 per-theorem agreement at k = 2,000 | ≥ 70 % | base **93.2 %**, EI **89.0 %** (at k = 10,000: 92.7 % / 90.3 %) | holds |
| E11 | 0 base successes after **100,000** attempts at both T, p̂_EI ≥ 0.01 | 0–12 | **33** | **MISS, far high** |
| E12 | Lean share of sampler wall time at k = 10,000 < 23 % | — | base **18.9 %**, EI **12.5 %** (s3: 20.7 % / 10.7 %); as low as **4.7 %** in stage 2c | holds |

Falsifier count as a function of the base-attempt budget per temperature — **monotone, and ≥ 20 at
every budget measured**:

| base attempts per temperature | 40,000 (pre-registered) | 50,000 | 100,000 | 150,000 | 200,000 |
|---|---|---|---|---|---|
| surviving theorems | **37** | 35 | 33 | 30 | **29** |

The count is identical whether the forward crux is taken at the pre-registered k = 4,000 (81
theorems, 61 with p̂_EI ≥ 0.01) or at the run's k = 10,000 (82, 58). My survivor **set** at 200,000/T
is set-equal to the executor's `data/sc/falsifier_survivors.txt`; my forward-crux, reverse-crux and
φ-crux sets are set-equal to `crux_forward.txt`, `crux_reverse.txt`, `crux_forward_phi.txt`.
Survivors by `L_true`: at 40,000/T `{7:1, 8:3, 9:18, 10:9, 11:5, 12:1}`; at 200,000/T
`{7:1, 9:13, 10:9, 11:5, 12:1}`.

### 5. pass@k (my own unbiased estimator) — no crossover anywhere

`1 − C(n−c, k)/C(n, k)` exactly, for k ≤ n; for early-stopped theorems (n < k) the plug-in
`1 − (1−p̂)^k`, marked `*` and only ever reached by theorems the model *already solves*, so it cannot
manufacture an EI advantage. Stage 1, seed 0, T = 0.8, mean over each stratum:

| `L_true` | m | base@32 | EI@32 | base@1,000 | EI@1,000 | base@10,000 | EI@10,000 |
|---|---|---|---|---|---|---|---|
| 7 | 60 | 0.0808 | 0.2624 | 0.1930 | 0.5350* → 0.3606 | 0.3167* | 0.4167* |
| 8 | 60 | 0.1114 | 0.5045 | 0.2402 | 0.5350 | 0.4000* | 0.5667* |
| 9 | 60 | 0.0000 | 0.4698 | 0.0000 | 0.5097 | 0.0000 | 0.5333* |
| 10 | 60 | 0.0012 | 0.1619 | 0.0226 | 0.2234 | 0.0333 | 0.2833* |
| 11 | 60 | 0.0000 | 0.0750 | 0.0000 | 0.1061 | 0.0000 | 0.1333* |
| 12 | 60 | 0.0000 | 0.0179 | 0.0000 | 0.0411 | 0.0000 | 0.0667* |
| 13 | 13 | 0.0000 | 0.0002 | 0.0000 | 0.0077 | 0.0000 | 0.0769 |
| 14 | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

(The 7/1,000 cell is 0.3606; the 0.5350 above it is the `L_true` 8 value — full table in
`review_sc_passk.py`'s output.) Searching every k from 1 to 10,000, **no stratum 7–13 crosses over**
on either seed; `L_true` 14 is 0 = 0 for both models at every k, which is not a crossover.

### 6. Secondary — the base's own probability of the EI proof

297 distinct EI-found proofs over all 82 forward-crux theorems are scored teacher-forced under the
base, marginalised over the random name offset. For the 29 survivors, the **best** (largest) base
log-probability of any EI proof of that theorem:

- max over survivors **−16.17** (p = 9.5 × 10⁻⁸, `la_transfer_616`), median **−25.65**, min **−85.24**
  (p = 9.6 × 10⁻³⁸, `la_transfer_454`).
- 0 successes in 200,000 T = 0.8 draws needs p ≪ 5 × 10⁻⁶; the largest single-proof lower bound is
  9.5 × 10⁻⁸, **~50× below** that. The direct-sampling result and the forward-pass result are
  mutually consistent, which is the strongest internal check the run has.
- This is correctly framed in `sc_secondary.py` as a lower bound on p_base for *that proof*, not for
  the theorem.

### 7. Proof length, term size and box depth (my own counters)

| arm | proofs | lines med / max | term size med / max | box depth med / max | shorter than `L_true` |
|---|---|---|---|---|---|
| base s0 T 0.8 | 93 | 8 / 11 | 50 / 91 | 3 / 3 | **5 (5 %)** |
| base s0 T 1.0 | 94 | 8 / 10 | 60 / 93 | 3 / 3 | 1 (1 %) |
| base s1 T 0.8 | 55 | 8 / 10 | 50 / 87 | 3 / 3 | 1 (2 %) |
| EI s0 T 0.8 | 354 | 9 / 13 | 67 / 122 | 3 / **5** | 0 |
| EI s0 T 1.0 | 283 | 10 / 13 | 77 / 123 | 3 / 4 | 0 |
| EI s1 T 0.8 | 317 | 9 / 14 | 61 / 122 | 3 / 4 | 0 |

EI proofs on the 29 survivors: 104 proofs, lines median 10 (range 7–13), term size median 87 (24–122),
max box depth 4. That a few base proofs come in **below** their `L_true` label is the expected
consequence of `L_true` being an ND-derived upper bound under Lean, and is worth stating explicitly
wherever `L_true` is used as "true length".

### 8. Two things the raw artefacts show that need saying

**(a) The seed-1 EI checkpoint that every stage-3 EI number was measured on no longer exists, and
its training record is gone.** Stage 3 records `ckpts/ladder/la_T1_sc_s1_r8.pt`, md5
**`105be4f3…`**. That file is not in `ckpts/ladder/` and `artifacts/sc/la_T1_sc_s1/` does not exist —
only `la_T1_sc_s1rerun/`, whose round-8 checkpoint is md5 **`12c13e61…`**, a different model. So:
the md5 label travels with every stage-3 record (good), but the `round_*.json`, `found_*`, `mix_*`
and per-round checkpoints for the model actually measured are lost; only its `gate_la_s1.jsonl`
survives. Consequences: the pre-registration's "all 8 round checkpoints uploaded" is **not met for
seed 1**; **E1's seed-1 value 972 belongs to the rerun chain (`12c13e61`), not to the checkpoint
stage 3 measured**; and my contamination audit of the training mixes covers seed 0 and the rerun but
*cannot* cover the seed-1 model that produced the stage-3 numbers. Every seed-1 EI number is
therefore reproducible only up to "an 8 × 32 EI run from `stage1_a1_seq_s1.pt` with seed 1", not to a
specific artefact. This does not touch the falsifier, which is entirely a seed-0 measurement.

**(b) `max_new` = 400 truncation is above the policy's 0.1 % line in one base stratum.** The
`--max_new` choice was validated on 6 `L_true` 7 theorems only. `support.py` stores `None` in its
uniform reservoir of grammar-rejected texts exactly when a sample produced no `<eos>`, which lets the
truncation rate be estimated post hoc. Estimated share of **all** samples cut off at 400 tokens:
base `L_true` 10 **≈ 1.0 %** (5 of 360 reservoir slots), base `L_true` 9/11/12 ≈ 0.2–0.3 %, base
`L_true` 7/8/13/14 and EI ≈ 0 %. AGENT_POLICY asks for this fraction to be reported and for `max_new`
to be raised above ≈ 0.1 % in any reported stratum. On the survivors, ≈ 0.7 % of base samples are
truncated, which turns 400,000 attempts into ≈ 397,000 effective — it cannot change E5, but the rate
belongs in the write-up, and the 400-vs-512 equivalence claim was established only on the shortest
stratum.

For context on why base coverage is so much lower than predicted: **36.5 %** of base samples at
T = 0.8 (43.7 % at T = 1.0) fall outside the strict `lean_seq` grammar, against **20.9 %** for EI.
Grammar brittleness, not only logical reach, is part of what E2/E2′ missed on — and it is a property
of the base checkpoint, measured identically for both models.

### 9. Recount summary

Every pre-registered quantity is re-derivable from the committed artefacts and my values agree with
the executor's derived name-lists set-for-set where those exist. The central result stands on my own
code and my own Lean: **the pre-registered falsifier fires** — 37 theorems at its own ≥ 40,000
attempts per temperature, 29 at 4 × 10⁵ attempts, against a threshold of 20 — and there is **no
base-catches-up crossover in any length stratum within k ≤ 10,000**. Four predictions miss (E2, E2′,
E3, E3′ all low; E5 and E11 high; E7's first half), and the two labelling issues in §8 need wording
fixes.

---

## §Compare — the executor's claims against my independent values

Read after §Recount was committed. Sources: `run_support_curves.md`, `numbers.md` § support-curves,
`log.md` (18:15 – 03:06). "Reproduces" means my value from my own code equals the executor's to the
precision stated.

### Method and models

| claim | my value | verdict |
|---|---|---|
| base = 3,214,336-param from-scratch `lean_seq` GPT, cap 6, Stage 1 only, md5 `9bde44c0…` / `fc27e52d…` | both md5s match the records on every row; every record carries checkpoint + md5 | **reproduces** |
| EI = base + 8 × 32 EI at T 0.8 on a **disjoint** pool, re-trained here | disjoint by renaming class (0 of 383, 0 of 2,285 pool-wide), by theorem string and by name; all 542,824 training records audited: 0 from either pool | **reproduces** |
| 383 theorems committed before any pod | md5 `3cb6e7bf…`, strata exact; prereg 18:16:17Z, first pod 18:17:10Z | **reproduces** |
| "10,000 per theorem per model at T 0.8, then up to 390,000 more on the crux across both temperatures" | 10,000 + 190,000 at T 0.8 + 200,000 at T 1.0 = 390,000 more | **reproduces** |
| Lean alone decides; `nd_verify` judged nothing | no `nd_verify` call anywhere in this run's code; blob identical to `origin/main` | **reproduces** |
| Lean 4.34.0 core, no Mathlib | `pod/sc/setup.sh` pins `v4.34.0`, setup log confirms it. **My re-check ran Lean 4.34.1** and all 1,196 counted proofs still pass — a cross-version confirmation, not a replay | **reproduces, and strengthened** |
| gate self-test 1,600 accepted / 400 rejected of 2,000 | `gate_selftest.jsonl`: exactly 1,600 / 400 / 0 conflicts | **reproduces** |

### The headline numbers

| claim | my value | verdict |
|---|---|---|
| E1 EI s0 transfer 869 / 2,285, `L*` 12 | **869**, `L*` 12 | **reproduces** |
| E2′ base 45 of 383 at k 10,000 (39 at k 4,000) | **45 (39)** | **reproduces** |
| E3′ EI 121 of 383 at k 10,000 (116 at k 4,000) | **121 (116)** | **reproduces** |
| SC3 per-stratum solved, all 8 bins × 2 models × 2 k | every one of the 32 cells | **reproduces exactly** |
| pooled: base 64 / 383 from 25,587,536 samples at T 0.8; 35 / 338 at T 1.0 from 13,722,176; EI 125 / 383 | identical, to the sample | **reproduces exactly** |
| E4′ forward crux 82 (81 at k 4,000); reverse 6 (4); φ-crux 58 (61) | identical, and my sets are **set-equal** to `crux_forward.txt`, `crux_reverse.txt`, `crux_forward_phi.txt` | **reproduces** |
| **E5 falsifier = 29, threshold 20 → FIRES** | **29** at 200,000/temperature, and my set is **set-equal** to `falsifier_survivors.txt` | **reproduces** |
| survivors 44 → 35 → 29 at 10,000 → 50,000 → 200,000 per temperature | **44 → 35 → 29** | **reproduces exactly** |
| "same count at the pre-registered k = 4,000 crux definition: 29" | 29 | **reproduces** |
| p̂_EI over the survivors "0.022 – 1.000" | 0.0220 – **0.9995** | reproduces at the low end; **the upper end is 0.9995, not 1.000** — write `≈ 1.00` or the exact value |
| E6 reverse crux 6, 2 survive 50,000 more EI attempts; the per-theorem table | every cell | **reproduces** |
| SC6 temperature: 19 of 338 solved at T 1.0; by `L_true` 7→6, 8→6, 9→7; 17 in the crux, 14 in the φ-subset; p̂ 1.0 × 10⁻⁴ – 7.3 × 10⁻⁴ | every figure | **reproduces exactly** |
| E7 "no crossover, any stratum, any k"; `L_true` 9 is 0.024 vs 0.533 | no crossover at any k in 1…10,000 in any stratum 7–13, on **either** seed, under my own estimator | **reproduces** |
| SC9 base `L_true` 7 climbs 0.123 → 0.335 (k 256 → 10,000) | 0.1231 → 0.3349 from `report.json`; **my stage-1-only value at k = 10,000 is 0.317** | reproduces from the run's own pooled curve; see the estimator note below |
| SC10 secondary: min −124.77, median −30.69 (p = 4.7 × 10⁻¹⁴), max −9.47, 297 proofs | min −124.77, median −30.69, max −9.47, n = 297 | **reproduces exactly** |
| E10 seed agreement, base 92.7 % | 355 / 383 = **92.7 %** | **reproduces** |
| E10 seed agreement, EI **90.9 %** | **90.3 %** (346 / 383) at equal attempts; 90.9 % only if seed 0's set is the **pooled** 125, which includes 50,000 extra attempts given to seed 0 alone | **differs by 2 theorems** — an asymmetric comparison; both readings clear E10's 70 % |
| SC13 ≈ 21 pod-hours, ≈ $10.3; balance above $100 | `podbudget`: **20.37 h, $9.99**; `rpbalance` **$136.49**; 5 pods, all deleted | reproduces (the write-up rounds up, which is the safe direction) |

### The five artefact checks behind the falsifier

| check | my value | verdict |
|---|---|---|
| 1. leakage — 0 overlap with the EI pool by name / string / renaming class, 0 of 2,285 pool-wide | reproduces, and extended: **0** eval-pool records in all 542,824 training records of every round | **reproduces** |
| 2. proof validity — "all **372** accepted EI proofs on them re-verified one proof per Lean process, 0 failures, 0 `sorry`/`simp`-class tokens" | 372 is the proof count for the **35**-survivor set (the 23:40 figure). For the final **29** survivors it is **315** (all EI arms) or 231 (seed 0). Separately, `sc_recheck.py`'s Lean call is `check_sources([tk.statement(...) + tx] if False else [nd2lean.translate(...)])` — the `if False` makes it check the **nd2lean translation of the normalised proof**, not the literal sampled text its docstring and the write-up both claim. The vacuity-token scan *is* on the literal text. | **the conclusion holds** — my own re-check ran the **literal sampled text** against my own statement builder for **all 1,196** counted proofs in the run and Lean accepted 1,196, 0 banned tokens — but **the count 372 is stale and the code does not do what it says** |
| 3. judging path — 11/11 `ladder_ei`-written proofs pass `support.py`'s judge, normalised and un-normalised | I re-ran `sc_selftest.py` myself: **11 accepted, 0 rejected; un-normalised 11/11** | **reproduces** |
| 4. sampler — "on 9 theorems the base demonstrably solves it returns 116/140/179 per 2,000"; "compaction on vs off agrees to 1 sample in 6,000 (`artifacts/sc/diag/`)" | **`artifacts/sc/diag/` does not exist** — not in the repository, not in the bucket (full recursive listing, 172 entries). The *substance* is recoverable from committed data: all 9 `known_solvable.txt` theorems are in the stage-1 records and base s0 solves **8 of 9** at **126–1,341 successes per 2,048** (`la_transfer_466` at 6/10,000), which brackets 116/140/179. The compaction on/off comparison is **not derivable from anything on file.** | **partly not derivable** — cite the stage-1 records instead, and drop or re-run the compaction comparison |
| 5. temperature — T 1.0 removed 17 crux theorems T 0.8 alone would have left in | 17 | **reproduces** |
| 6. duplicate records — only `s2c_base_T08_s0.s{0,1}` affected, every duplicate pair identical, `load_rows` now raises | no duplicated (file, theorem) record anywhere in the 2,494 committed records; all 2,494 pass my counting invariants | **reproduces** |

### The lost seed-1 checkpoint (SC2 / SC12 / log 00:35)

The run reports this fully and accurately, and I can confirm every part of it from the surviving
`gate_la_s1.jsonl` (32 records, the whole lost run's gate log):

| claim | my value | verdict |
|---|---|---|
| seed-1 EI ladder lost with pod `sc2`; seed-1 *measurements* intact | stage 3 records `la_T1_sc_s1_r8.pt` md5 `105be4f3…`, absent locally and from the bucket; `artifacts/sc/la_T1_sc_s1/` absent | **reproduces** |
| rerun round 1 matched the lost run **exactly** (parse-fail 54,051, distinct 79,599, Lean-accepted 7,089, transfer 57/2,285) | all four round-1 gate records are **identical field-for-field** | **reproduces** |
| round 2 diverged (transfer 374 vs 373) | the first differing gate record is index 4 = round 2 (107,167 vs 106,875 distinct; 38,050 vs 38,026 accepted) | **reproduces** |
| rerun is a different model, 972 / 2,285, `L*` 11, and **no number in this run is measured on it** | rerun r8 md5 `12c13e61…` ≠ `105be4f3…`; 972 / `L*` 11 confirmed; no record cites the rerun | **reproduces** |

The disclosure is exemplary. Two consequences still need to be *stated as limits* rather than only as
history: (i) the pre-registration's "all 8 round checkpoints uploaded" is **not met for seed 1**;
(ii) my contamination audit and every reproducibility guarantee cover seed 0 and the rerun but
**cannot cover the model stage 3's seed-1 numbers were measured on** — for that model only the gate log
survives. Every seed-1 number is reproducible to "an 8 × 32 EI run from `stage1_a1_seq_s1.pt`,
seed 1", not to an artefact. None of this touches the falsifier, which is entirely seed 0.

### Pre-registered predictions that are not reported

| prediction | its value | status in the write-up |
|---|---|---|
| **E11** (addendum 1): forward-crux theorems at 0 base successes after **100,000** attempts at both T with p̂_EI ≥ 0.01 — predicted **0–12** | **33** | **not reported anywhere.** SC8's monotone table skips the 100,000 row and E11 is never named. This is a pre-registered prediction that missed by ~3×, in the same direction as E5, and the brief requires misses to be reported as misses. |
| **E9**: base at T 1.0 vs T 0.8 on the forward crux — "strictly more, but fewer than 3× more" | **33 vs 18 theorems = 1.83×** (holds); **per-attempt success rate 3.30×** (does not) | not adjudicated. SC6 has the raw material; E9 needs one line naming the metric. |
| **E8**: `L_true` ≥ 13 solved by anything, any k — predicted 0–2 | **1** (`la_transfer_1126`, EI only, both seeds) | stated in SC9's prose but not tied to E8 |
| **E12**: Lean share of sampler wall at k = 10,000 below 23 % | base **18.9 %**, EI **12.5 %** (seed 1: 20.7 % / 10.7 %); 4.7 % in stage 2c | holds; SC11's "Lean is 3–26 % of wall" quotes a range whose top **exceeds** E12's own threshold without saying which arm or k it belongs to |
| **E2, E3, E4** (the k = 4,000 originals) | 39 / 116 / 81 | in SC7's table; the write-up's outcome table lists only the primed versions. Fine, but E2/E3 missed low at k = 4,000 too and the summary table should say so once. |

### Numerical slips

| claim | my value |
|---|---|
| SC11 "total artifact size for **≈ 38 M** samples is **≈ 6 MB**" | **8.6 MB** of per-theorem records for **49,715,072** samples |
| SC13 "samples drawn **≈ 47 M**" | **49,715,072** in the `support.py` stages alone (plus ≈ 3.5 M in stage 0) |
| `log.md` 02:05 "≈ 12 MB for ≈ 47 M samples" | 8.6 MB / 49.7 M — three different sample totals appear across the run's own documents |
| SC7 "the **35** falsifier survivors" (leakage check) | the final set is 29; 35 was the 23:40 count. The check is valid for both (29 ⊂ 35), but the wording is stale, as is the 372 in check 2 |

### Two estimator / design notes, neither of which changes a conclusion

1. **`max_new` = 400 truncation.** The equivalence probe (`probe/mn{400,512}.s0.jsonl`) is 6 theorems at
   `L_true` 7 **each with `n_ok` = 0**: byte-identical records there show only that no proof was found
   either way, not that a long proof would survive a 400-token cap. From `support.py`'s
   failure reservoir I estimate the share of **all** samples truncated at 400: base `L_true` 10
   **≈ 1.0 %**, base `L_true` 9/11/12 ≈ 0.2–0.3 %, elsewhere ≈ 0. AGENT_POLICY asks for this fraction to
   be reported and for `max_new` to be raised above ≈ 0.1 % in a reported stratum. On the survivors it
   turns 400,000 attempts into ≈ 397,000 effective, so E5 is untouched — but the rate belongs in SC11
   and "400 and 512 give byte-identical records" needs the qualifier that it was tested only on the
   shortest stratum with no successes.
2. **SC9's pooled pass@k.** `report.json` pools stage-2 attempts into the base curve (`max_k_measured`
   200,000) and flags `exact: false` for every k above `min_n` = 2,048, which the preamble explains and
   the figure draws dashed — correct, but the SC9 **table** does not mark which cells are
   extrapolated, and every base/EI cell at k ≥ 4,000 is. Separately, theorems entered stage 2 *because*
   they had 0 stage-1 successes, so their pooled p̂ carries a downward bias of order n₂/(n₁+n₂) ≈ 0.95 —
   which pushes base pass@k **down**, i.e. in the direction that favours the run's conclusion. At the
   22× gaps involved it is immaterial, and my stage-1-only curve (unbiased, fixed n) shows no crossover
   either. Say which n the curve is computed on.

---

## §Verdict

**What stands.** The central result reproduces on my own code, my own normaliser, my own statement
builder, my own Lean driver and a different Lean patch release. **The pre-registered falsifier fires:**
29 theorems on which the base model — 3,214,336 parameters, from scratch, `lean_seq`, cap 6, Stage 1
only, `stage1_a1_seq_s0.pt` md5 `9bde44c0…` — has **0 Lean-accepted successes in 200,000 attempts at
T = 0.8 and 200,000 at T = 1.0**, while its own 8 × 32 expert-iteration descendant
(`la_T1_sc_s0_r8.pt` md5 `5cebd7ec…`) solves each at p̂ 0.022–0.9995. The threshold was 20 and the
prediction was 8. At the pre-registration's own depth (≥ 40,000 attempts per temperature) the count is
**37**; the run reports the deeper, more conservative 29. The falsifier fires at every budget measured
(44 / 37 / 35 / 33 / 30 / 29 at 10k / 40k / 50k / 100k / 150k / 200k per temperature), and identically
whether the crux is taken at the pre-registered k = 4,000 or the k = 10,000 actually run. There is **no
base-catches-up crossover in any length stratum at any k ≤ 10,000, on either Stage-1 seed**. Two
independent measurement modes agree: direct sampling gives p_base < 7.5 × 10⁻⁶ (95 %) on the
survivors, and the base's teacher-forced probability of the EI model's own proof tops out at
9.5 × 10⁻⁸ there — 50× below what 400,000 draws could have surfaced. Every one of the 1,196 distinct
counted proofs in the whole run is accepted by Lean from its literal sampled text, with no vacuity
token. Splits are disjoint by renaming class three ways over, and all 542,824 EI training records are
free of the evaluation pool. Hard constraints pass; no quarantine condition. Spend 20.37 h / $9.99
against 30 h / $15, balance $136.49.

The run's honesty is above standard: the 19:05 scare, the 21:28 seed-labelling slip, the 00:03
duplicated shards and the 00:35 checkpoint loss are all written up with their mechanisms, their
blast radius and the guard added, and several of them would have produced a wrong number.

**What must be reworded.**

1. **E11 must be reported as a miss.** Predicted 0–12 at 100,000 attempts per temperature; measured
   **33**. Add the 100,000 row to SC8's table and name E11 beside it.
2. **`artifacts/sc/diag/` does not exist** — not in the repository, not in the bucket. Remove it from
   SC12, and re-base falsifier check 4 on committed data: base s0 solves **8 of the 9**
   `known_solvable.txt` theorems in the stage-1 records at 126–1,341 per 2,048. The compaction
   on/off comparison (116/116, 140/140, 179/178) is not reproducible from anything on file and should
   be dropped or re-run.
3. **"all 372 accepted EI proofs on them"** is the count for the 35-survivor set; for the 29 it is 315
   (231 at seed 0). Fix the number, and fix SC7's "the 35 falsifier survivors".
4. **`sc_recheck.py` does not check what it claims.** `[... ] if False else [nd2lean.translate(...)]`
   makes it Lean-check the translated normalised proof, not the literal sampled text, contradicting its
   docstring and SC8 check 2. Either delete the dead branch and check the literal text, or reword the
   claim. (My re-check does the literal text for all 1,196 proofs and it passes, so nothing downstream
   moves.)
5. **p̂_EI upper end is 0.9995, not 1.000.** And the EI seed-agreement figure should be **90.3 %** at
   equal attempts, or 90.9 % explicitly labelled as pooling 50,000 extra seed-0-only attempts.
6. **Sample totals.** ≈ 38 M (SC11), ≈ 47 M (SC13) and ≈ 47 M / ≈ 12 MB (`log.md`) should all be
   **49.7 M samples / 8.6 MB of per-theorem records**.
7. **`max_new` = 400.** Report the truncation fraction per stratum (base `L_true` 10 ≈ 1.0 %, above
   AGENT_POLICY's 0.1 % line) and qualify "400 and 512 give byte-identical records" — the probe was 6
   `L_true` 7 theorems with zero successes.
8. **Seed 1's limits.** State plainly that the pre-registration's "all 8 round checkpoints uploaded" is
   **not met for seed 1**, and that every seed-1 number is reproducible only to a recipe, not to an
   artefact. Put the EI md5s (`5cebd7ec…`, `105be4f3…`) in SC0 beside the base ones — for the seed-1
   model that md5 is now the only identifier that exists.
9. **SC9's table should say which n the curve uses** and mark the `exact: false` cells.

**What is not supported.** Nothing load-bearing. The write-up's own caveat — "one base and its EI
model, 3.2 M parameters, one pool, n = 2 seeds; *counts* sit inside `NOISE_FLOOR.md`'s floor and are not
the finding, the per-theorem structure is" — is the right claim at this n, and the wording elsewhere is
correctly scoped: "no crossover **within measured k**", "a lower bound for that proof only", "`L_true`
is an ND-derived **upper** bound". No "bistable", "wall" or "never" is asserted beyond the evidence;
`log.md`'s "strongly bimodal" is a mechanism sketch inside the log, not a headline claim, and the
per-theorem scatter does support it. One small addition I would make: **5 % of the base's own counted
proofs at T = 0.8 are shorter than their `L_true` label**, which is a clean demonstration of why
`L_true` is an upper bound under Lean and worth a sentence wherever `L_true` is used as "true length".

**The next measurement that would settle what is left open.** The result is one base model at 3.2 M
parameters. The single most informative next step is the **same 383-theorem protocol on a second,
independently pre-trained base of a different size** — the run's own conclusion ("experiment 2 should
target capacity and coverage, not search") is a statement about capacity, and support expansion at
3.2 M does not tell you whether the survivors are theorems a *larger* base already reaches. Second, at
this scale only: push the 5 survivors at `L_true` 11 and the 1 at 12 to **10⁷** base attempts at T = 1.0.
They are the ones whose per-proof log p is ≤ −30, so they are where the amplifier reading has no room
left, and 10⁷ costs ≈ 3 pod-hours at this run's measured 3.6 M samples/pod-hour. Third, close the
seed-1 gap by re-running stage 3 on `la_T1_sc_s1rerun_r8.pt` (≈ 1 pod-hour): it gives a seed-1 column
that is attached to an uploaded checkpoint, which the current one is not.
