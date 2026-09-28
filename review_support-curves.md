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
