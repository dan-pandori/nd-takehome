# Review — search-expert (reviewer, 2026-09-30)

Reviewer session, independent of the executor. Phase 1 was done in `~/review/search-expert` (executor write-ups
removed) with code written for this review (`review_sx/`). Lean alone decides; `nd_verify` was not used for anything.

**Model every number below applies to** (from the pre-registration and the run's `args.json` / registry rows; parameter
count not re-measured — no torch on the VPS): SN-cap12, `lean_staten` state-conditioned format, 3.2 M params (4 layers,
d 256), from scratch, Stage-1 on K12 `train_k12.jsonl` (155,000 proofs, cap 12, 6,000 steps). Seeds 0–3 are
`state-cap12`'s Stage-1 checkpoints; seeds 4–5 were trained in this run (registry: 6,000 steps each). Each arm is an
8-round EI ladder from that seed's Stage-1 checkpoint on the 4,495 `rl_targets`. Read-outs: round-8 checkpoint, no
search, k 256, T 0.8, seed 0, batch 2,048, `max_action` 512, `max_steps` 96 (identical in all 40 read-out summaries;
I checked). `T1` = `state-cap12`'s T1 ladder checkpoints (`la_T1_SN12_s{0-3}_r8.pt`, same Stage-1 seeds, different
selection rule: up to 4 random proofs per target), re-read here at the same settings.

## §Recount (phase 1, before reading any executor write-up)

### 1. Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72…` at `HEAD` = `origin/main`. **OK** |
| `nd_verify` not used as judge | ladder/search/read-out judge through `lean_judge.judge_many` → `lean_gate` (Lean); grep of `state_ladder_ei.py`, `state_search.py`, `state_sample.py`, `lpool_reread.py` finds no `nd_verify` call. **OK** |
| `artifacts/TEST_RUN_DONE` | no diff vs `origin/dan`; `test_run_once.sh` not in any pod script. **OK** |
| evaluation files in training code | `transfer_long2_91.jsonl` / `rr600_13to16.jsonl` are read only by `lpool_reread.py` (read-out). The ladder reads `transfer.jsonl` / `heldout.jsonl` only for per-round evals, which `--no_eval` skipped (all `found_transfer_*.jsonl` are empty), and uses their keys to *exclude* them from replay. **OK** |
| pre-registration before the run | `preregistration/search-expert.md` committed 02:31:18 UTC (9d138b60), never changed afterwards; first registry row 02:34:49, first ladder `args.json` 02:39:11. **OK** |

No hard-constraint violation. No quarantine.

### 2. Split disjointness by renaming class

Own key (`review_sx/splits.py`): minimum over the 24 permutations of the atoms P Q R S of (sorted premise list,
conclusion); `F` is falsum, not an atom; premise order ignored. Sanity test: a renamed, premise-permuted copy of a
theorem gets the same key, a one-atom change does not.

| training file | classes | × `transfer_long2_91` (91) | × `rr600_13to16` (400) |
|---|---|---|---|
| `train_k12.jsonl` (155,000 recs; bucket `cap-horizon/data/kh`) | 154,382 | 0 | 0 |
| `rl_targets.jsonl` (4,495) | 4,495 | 0 | 0 |

The two evaluation pools share 0 classes with each other and have no duplicate classes inside them.

### 3. Lean re-check of counted proofs

Own ND-string → Lean renderer and checker (`review_sx/rlean.py`). It writes the proof in the documented `lean_seq` term
map, one theorem per line, and passes a theorem only if no error falls on its line **and** `#print axioms` lists only
{propext, Classical.choice, Quot.sound}. Any error in the prelude fails the whole file.

**Negative controls, run in the same batches as the positives** (`review_sx/recheck.py`):

| control | n | passed Lean |
|---|---|---|
| literal texts the run recorded as rejected (`gate_rr_*.leanrej.jsonl`) | 300 | 0 |
| counted proof with one `Or.inl↔Or.inr` or `.1↔.2` swap | 56 | 0 |
| counted proof paired with a different theorem with the same premise count | 150 | 0 |
| `sorry` | 5 | 0 (caught by the `sorryAx` axiom check) |

**Positives:**
- Sampled pass (seeded): 150 counted read-out proofs per arm (A, A2, B, C, T1) plus 100 expert proofs from
  the ladders' `found_*.jsonl` per arm (A, A2, B, C). **1,150 / 1,150 accepted.**
- Full pass: **every** distinct counted read-out proof in all 40 read-out files, **46,956 / 46,956 accepted**
  (`review_sx/fullcheck_summary.jsonl.gz`).

**Prefilter soundness.** In the read-out gates every rejection came from `lean_prefilter`. For example,
`gate_rr_A_s0`: `filter_rej` 12,042 = `lean_rej` 12,042. Lean itself only saw the 122 texts that passed the filter, and
accepted all of them. The run did not measure the filter's false-rejection rate at read-out (`filter_false_rej: null`).
I sent 2,400 filter-rejected texts to Lean, 120 at random from each of the 20 read-out gates. **Lean accepted 0 of
2,400**, so a false-rejection rate above ≈ 0.12 % is ruled out at 95 %. The same checker is the step filter inside
the ladders and the search.

### 4. Read-out: primary Q (291 = the 91 + rr600 `L_true` 15–16) and strata

Recomputed from the per-theorem rows (`review_sx/recount_rr.py`). Every row satisfies `n_ok + Σ reasons = n_tried =
256` and `solved ⇔ proofs ≠ []`.

| arm | s0 | s1 | s2 | s3 | s4 | s5 | mean | IQM [95 % CI, bootstrap over seeds] |
|---|---|---|---|---|---|---|---|---|
| A (sampling expert) | 79 | 111 | 129 | 148 | 113 | 102 | 113.7 | 113.8 [93.3, 134] |
| B (best-first expert) | 76 | 118 | 122 | 144 | 117 | 97 | 112.3 | 113.5 [91.5, 131.8] |
| A2 (re-draw of A) | 80 | 129 | | | | | 104.5 | — |
| C (truncate-and-resume) | 72 | 121 | | | | | 96.5 | — |
| T1 (state-cap12, secondary) | 142 | 207 | 218 | 220 | | | 196.8 | 212.5 [142, 220] |

- **B − A on Q, paired per seed:** −3, +7, −7, −4, +4, −5. Mean **−1.33**, sd 5.54, t(5) = −0.59, 95 % CI of the
  mean [−7.1, +4.5]. IQM −2.0 [−5.5, 3.75].
- Discordant theorems (B-only / A-only), seeds 0–5: 26/29, 38/31, 34/41, 34/38, 33/29, 32/37. Summed: **197 B-only,
  205 A-only.**
- **Same-checkpoint spread (A vs A2):** Q differences −1 and −18. s = RMS((A − A2)/√2) = **9.01**. The pre-registered
  MDD formula gives **18.2** (6 pairs). Per-theorem flips: 47 in seed 0, 66 in seed 1. From the between-seed sd of B − A
  (5.54) the MDD is **7.9**. Both come from few pairs; the A–A2 estimate is dominated by seed 1's −18.
- **C − A2 on Q:** −8, −8 (2 seeds). C − A: −7, +10.
- **Strata, B − A mean over 6 seeds:** exact-17 (61) +0.17; ≥ 18 (30) +0.17; rr 13–14 (200) +2.0 (sd 5.7);
  rr 15–16 (200) −1.67; the 91 +0.33. None is separated from 0.
- **Truncation (action or step cap) per stratum:** 6 of 100 arm × seed × stratum cells exceed the 0.1 % policy line:
  A_s0 rr13 0.10 %, A_s1 rr14 0.12 %, A_s5 rr14 0.12 %, C_s0 rr13 0.12 %, T1_s0 rr16 0.12 %, and **B_s3 rr15 0.82 %**.
  B_s3's cell is one theorem (`lp_transfer_869`, 209 of 256 samples hit `max_action` 512). A_s3 solved that theorem
  (5/256) and B_s3 did not, so it can move B − A in seed 3 by at most 1. The effect on Q is negligible, but the
  run's settings breached the policy line.

### 5. Expert level (per round, from `alloc_r.json` / `round_r.json`; `review_sx/expert.py`)

**Budget matching:** in 0 of 8 × 4,495 target-rounds did B spend more actions than A on the same target in the same
seed and round (C vs A2 also 0). Every round's `budget_actions` equals the partner's actual actions. **B spent only
22.6–24.6 % of A's actions** over 8 rounds (C: 18.5–20.4 % of A2's).

**H1: targets one arm's expert solved in round r that the other arm's expert had never solved in rounds 1..r, summed over rounds.**

| seed | B-only | A-only | C-only | A2-only |
|---|---|---|---|---|
| 0 | 746 | 1,800 | 762 | 474 |
| 1 | 483 | 1,753 | 542 | 419 |
| 2 | 508 | 1,708 | | |
| 3 | 455 | 1,737 | | |
| 4 | 668 | 1,850 | | |
| 5 | 698 | 1,787 | | |
| sum | 3,558 | 10,635 (ratio B/A **0.33**) | 1,304 | 893 (ratio C/A2 **1.46**) |

Cumulative targets solved by round 8: A 4,075–4,206 and B 3,950–4,039 (B lower in every seed, by 114–167). A2
4,122 / 4,183, C 4,131 / 4,184. Targets with `L_true` ≥ 13 ever solved: 3–6 in every arm.

**Length of the selected (shortest) expert proof, same target, same seed:** B − A median 0 lines, mean +0.54 to +0.63.
B's proof is longer on ≈ 21–23 % of targets and shorter on < 1.2 %. C − A2: median 0, mean +0.33.

### 6. Length of read-out proofs, lines and term size

Term size is my own count over the elaborated proof term (`rvsize` in `rlean.py`: nodes of app/lam/proj/bvar/const,
`have`-lets collapsed, minus the parameter binders). It is not the executor's `lean_check` size, so compare it between
arms, not with their absolute numbers. Comparisons are on theorems both arms solve in the same seed, using each arm's
shortest proof:

| pool | pair | theorems | Δ lines median / mean | longer / same / shorter | Δ term size median / mean |
|---|---|---|---|---|---|
| the 91 | B − A | 72 | 0 / +1.06 | 26 / 36 / 10 | 0 / +2.2 |
| rr 13–16 | B − A | 930 | 0 / +0.67 | 369 / 429 / 132 | 0 / +1.5 |
| the 91 | C − A2 | 22 | 0 / +0.36 | 7 / 7 / 8 | 0 / +0.2 |
| rr 13–16 | C − A2 | 272 | 0 / +0.40 | 78 / 152 / 42 | 0 / +0.4 |

Per arm, the median shortest proof is 18–22 lines on the 91 (labels 17 / ≥ 18) and 15–16 lines on rr 13–16. The
median term size is 55–69 and 43–47. Some proofs are shorter than the ND-derived label (e.g. A_s0 has a 16-line
proof on a label-17 theorem), as expected under Lean.

### 7. Compute per arm (registry rows `artifacts/search-expert/registry/*.jsonl`, summed by me; GPU A40; smoke rows excluded)

| arm (8 rounds) | sampling GPU-s | actions | gen tokens | attempts | Lean checks | fine-tune GPU-s | train steps | train tokens | recorded wait GPU-s |
|---|---|---|---|---|---|---|---|---|---|
| A (per seed) | 5,645–7,259 | 9.75–10.11 M | 192–196 M | 1,150,720 | 611–651 k | 2,647–3,111 | 4,800 | 504–506 M | — |
| B (per seed) | 2,027–2,553 | 2.28–2.40 M | 43–46 M | 35,960 | 30–31 k | 2,678–3,136 | 4,800 | 520–525 M | 3,706–4,876 |
| A2 | 6,486 / 6,642 | 9.81 / 10.05 M | 193 / 195 M | 1,150,720 | 614 / 651 k | 3,056 / 3,108 | 4,800 | 504 M | — |
| C | 2,559 / 2,303 | 2.00 / 1.86 M | 40 / 37 M | 143,840 | 32 / 33 k | 3,100 / 3,161 | 4,800 | 516 M | 4,201 / 4,276 |

- The only quantity on which an arm exceeds its comparator is B's training tokens, at ≈ 1.035× A's. Nothing exceeds 1.25×.
- On sampling, B used ≈ 0.35× A's GPU-seconds and ≈ 0.23× A's actions and generated tokens. The wait phase is booked
  separately.
- A and B shared one GPU, so the GPU-seconds are wall time under co-tenancy.
- Each read-out cost 1,261–2,205 GPU-s.
