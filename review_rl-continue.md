# Review — rl-continue (reviewer session, 2026-10-04)

Reviewer kit: `review_rc/` (my own code: `recount.py`, `groupc.py`, `reads.py`, `recheck.py` + `rlean.py`, `sizes.py`,
`splits.py`, `compute.py`; outputs in `review_rc/rv/`). It is adapted from my `review_rc6/` kit on `dan_rl-continue-cap6`
and shares no code with `rc_analysis.py` / `rc_compute.py` / `tj_analysis.py`. Inputs: `found_{8,16}.jsonl`,
`found_transfer_{8,16}.jsonl`, `mix_16.jsonl` from `hf://buckets/dan-pandori/nd-rl/rl-continue/artifacts/rc/la_T1_best12_s*/`;
round / alloc JSONs, eval rows and registry rows in git. Phase 1 ran in `~/review/rl-continue` with the executor's
write-ups removed.

**Model for every number below** (unless marked "pend" or "r8"): `trajectory`'s T1 cap-12 ladders continued here,
`la_T1_best12_s{0,1,2}_r{12,16}`: ALiBiGPT 9,560,832 params, `lean_staten` state format, trained from scratch on K12
(`data/kh/train_k12.jsonl`, cap 12), then 16 EI rounds (r1–r8 in `trajectory`, r9–r16 here, A40). "r8" = `trajectory`'s
`la_T1_best12_s*_r8.pt`; "pend" = its end-of-pretraining checkpoint. Lean alone decides throughout (the ladder imports
`lean_judge.verify_text`; `state_env` imports `nd_verify.verify.parse_formula` for parsing only).

## §Recount (phase 1, written before reading `run_rl_continue.md`, `numbers.md`, `log.md`, `STATUS.md`)

### Hard constraints

| check | result |
|---|---|
| `nd_verify/` unmodified | tree hash `9437bb72…` = `origin/main`'s |
| `nd_verify` as judge | not used: ladder judges through `lean_judge`; reads through `state_eval.py` / `lpool_reread.py` (Lean, `reasons` = `lean rejected` / `lean_seq parse: …`) |
| `artifacts/TEST_RUN_DONE` | unchanged since `cf5924e2` (no diff from the merge base) |
| eval files in training code | `state_ladder_ei.py` reads `transfer.jsonl` only to sample it (never trained); no `textbook72` / `holdout250` / `rr600` / `long2` path in `state_ladder_ei.py` or `state_train.py` |
| code changed by the run | none of the ladder / eval / judge code; only `pod/rc/*`, `rc_analysis.py`, `rc_compute.py`, `data/rc/rr600_13_16.jsonl` (+ `pod/tj`, `tj_*.py` checked out from `dan_trajectory`) |
| pre-registration before the run | committed `8cf9ccfe` 17:23:14 UTC; first ladder start 17:26:30 UTC; the file was not edited afterwards |

No hard-constraint violation.

### Seamlessness of the resume (r8 → r9, r12 → r13)

- r9 sampled from `la_T1_best12_s{0,1,2}_r8.pt` with md5 `f9afd386…` / `c85481f9…` / `3b62784b…` — equal to
  `trajectory`'s `artifacts/tj/score/ckpts_s*.md5`. r13 started from r12 checkpoints whose md5 equals the registry's
  `ckpt_saved` rows (`dc51ae00…` / `1cc84270…` / `960307b9…`).
- Resume line proof counts 229,482 / 271,490 / 250,560 = my line counts of `found_8.jsonl`.
- Every r8 found row (by name + exact proof text) is in `found_16` (229,482/229,482, 271,490/271,490, 250,560/250,560;
  transfer 103,137 / 117,044 / 112,969 all kept); no r8-solved target lost; no row's `round` ≤ 8 is missing from found_8.
- Round chain: round r samples from `_r{r-1}.pt`; sampling seeds `seed*1000 + r` (9…16, 1009…1016, 2009…2016). The
  copied r1–r8 round JSONs are byte-identical to `dan_trajectory`'s.
- Ladder batch: s0, s1 2,048; s2 1,024 (as in `trajectory`'s r8). No OOM retries in r9–r16.

### Ladder: targets and transfer (found files, my first-round-per-name count)

My cumulative counts equal the round JSONs' `targets_cum` / `transfer_cum` for every round r1–r16 on every seed (0 mismatches).
My start-index normaliser agrees with the run's `norm` field on every row (0 differences); every found row is distinct.

| seed | targets r8 → r16 (of 4,495) | new r9–r16 | transfer r8 → r16 (of 2,285) | new r9–r16 | new targets per round r9…r16 |
|---|---|---|---|---|---|
| s0 | 4,383 → 4,403 | **+20** | 2,185 → 2,202 | **+17** | 4, 9, 2, 0, 1, 3, 0, 1 |
| s1 | 4,365 → 4,433 | **+68** | 2,170 → 2,230 | **+60** | 6, 6, 2, 6, 18, 20, 5, 5 |
| s2 | 4,407 → 4,429 | **+22** | 2,190 → 2,223 | **+33** | 4, 3, 3, 3, 2, 3, 2, 2 |

(r6–r8 per round, for reference: 18/14/5, 20/9/9, 27/13/12 — as the pre-registration states.) The 96 new targets
(union) share no theorem across all three seeds. New-target `L_true`: s1's are mostly 9 (40/68) and 12 (12/68).

Target sample accuracy (from alloc counters; equals the JSON field every round): r8 0.918 / 0.918 / 0.924 →
r16 0.937 / 0.944 / 0.942. Transfer sample accuracy r16 0.820 / 0.820 / 0.814.

**Excluded middle (my pattern: a line deriving `X ∨ ¬X` or `¬X ∨ X`) in the first proof of each new target:** s0 0/20,
s1 36/68 (r13 11/18, r14 16/20), s2 8/22. Across *all* accepted rows the LEM share is flat (s1 2.2–2.6 %), so it is
the new-target solutions, not the bulk, that use it.

### Read-outs (k 256 at T 0.8, max_action 512, max_steps 96; rr1316 k 64; sample seed as named)

Group C (seed-0 draw `x0`: not solved at pend and not at r8; tb72 + h250): 36 / 35 / 28 theorems (tb72 24/22/17, h250 12/13/11).
pass@256 on sample seed 1 (`x1`):

| seed | pend | r8 | r12 | r16 | Δ r16 − r8 | r16 C pass@8 / pass@1 |
|---|---|---|---|---|---|---|
| s0 | 0/36 | 3/36 = 0.083 | 5/36 = 0.139 | 6/36 = 0.167 | +0.083 | 0.081 / 0.035 |
| s1 | 0/35 | 1/35 = 0.029 | 8/35 = 0.229 | 17/35 = 0.486 | +0.457 | 0.257 / 0.144 |
| s2 | 0/28 | 1/28 = 0.036 | 5/28 = 0.179 | 4/28 = 0.143 | +0.107 | 0.081 / 0.044 |
| pooled | 0 | 0.051 | 0.182 | 0.273 | | |

**Falsifier 2 fires:** mean Δ +0.216 > r8 spread 0.055 (max − min of 0.083 / 0.029 / 0.036), 3/3 seeds rise. s0's and
s2's Δ (+0.083, +0.107) each exceed 0.055 on their own. Base reachability of C on pend's independent `x1` draw: 0/99.
Cross-seed: of s1's 17 r16 C solves, 7 — six h250 theorems (`la_transfer_1424, 1453, 1572, 478, 795, 956`) and tb72
`textbook_a104fab…` — were solved by **no** pend or r8 read of any seed on either draw; s2's `la_transfer_956` and
`textbook_a104fab…` likewise. Most other C solves were solved by another seed's r8 (C is per-seed). s2 lost one r8 C solve
(`textbook_920bfc…`, 1/256 at r8) — a single-hit re-draw.

Solved (x1), r8 → r12 → r16: tb72 48 → 51 → 51 / 48 → 52 → 57 / 53 → 58 → 56; h250 240 → 239 → 240 / 236 → 241 → 246 /
237 → 239 → 239.

rr1316 (400, k 64, batch 512, sample seed 0), r8 → r16: 377 → 382 (+5) / 362 → 370 (+8) / 367 → 376 (+9); union over
seeds 390 → 389. long2 (21, k 256): 21 → 21 / 20 → 21 / 20 → 20. r8 and r16 reads at identical settings.

All eval rows consistent (`n_ok = n_tried − Σ reasons`, `solved ⇔ proofs`), 0 exceptions.

**Cut-offs** (`action truncated` + `step cap`, from per-row `reasons`): r16 tb72 0.39 / 0.54 / 0.13 %, tb72 group C
0.52 / 1.03 / 0.16 %, h250 group C 0.75 / 0.69 / 0.04 %, single tb72 rows up to 6.6 %; rr1316 strata up to 0.73 %
(L 13, r16 s2); long2 up to 0.33 %. **Above the policy's ≈ 0.1 % per reported stratum** in most strata, at r8 as well as
r16 (settings inherited from `trajectory`). The C strata are where cut-offs are highest, so if anything the C solve
counts are biased down, at both endpoints.

### Lean re-check (my renderer + `#print axioms`, reviewer code)

Negative controls first: 60/60 untouched counted proofs pass; 0/200 samples the run recorded as Lean-rejected pass;
0/60 proofs paired with a different theorem of the same premise count pass; `sorry` fails; 1/60 `Or.inl ↔ Or.inr` flips
pass (benign).

| seed | new targets: every first proof + 100 random r9–r16 rows | new transfer: every first proof + 30 random | r16 read: every proof of every solved C theorem + 100 tb72 + 50 rr1316/long2 |
|---|---|---|---|
| s0 | 120/120 | 47/47 | 412/412 (262 C proofs) |
| s1 | 168/168 | 90/90 | 457/457 (307 C proofs) |
| s2 | 122/122 | 63/63 | 190/190 (40 C proofs) |

**0 of 1,669 rejected.** Proof length (first proof of each new target): lines median 20.5 / 17 / 17 vs `L_true` median
9.5 / 9 / 9 (no first proof shorter than `L_true`); term size (Expr nodes) median 72.5 / 70 / 96.5, range 19–396;
random r9–r16 rows median 14 lines, size 40–46. Shortest r16 proofs of s1's 6 never-before-solved h250 C theorems: 9
lines, term size 25–67.

### Splits (renaming class: 24 atom permutations, F = falsum, premise order ignored)

| eval pool | vs `train_k12` (replay) | vs `rl_targets` (trained) | vs r16 fine-tune mix prompts (s0/s1/s2) |
|---|---|---|---|
| textbook72 | 1 (`textbook_3ed45…`, not in any C) | 0 | 0 / 0 / 0 |
| holdout250 | 0 | 0 | 0 |
| transfer 2,285 | 2 (`la_transfer_396`, `_1061`) | 2 (`_307`, `_842`) | 2 / 3 / 2 |
| long2, rr600 13–16 | 0 | 0 | 0 |

None of the overlapping transfer theorems is among any seed's new transfer solves, so the r9–r16 transfer counts
are unaffected. 0 exact-prompt overlaps anywhere.

### Compute (registry rows, own sums; all NVIDIA A40)

| seed | ladder r9–r16 GPU-s | gen tokens | attempts | Lean checks | train steps / tokens |
|---|---|---|---|---|---|
| s0 | 33,248 | 478.5 M | 1,793,960 | 1,564,866 | 4,800 / 905.5 M |
| s1 | 32,830 | 481.7 M | 1,793,960 | 1,560,787 | 4,800 / 904.9 M |
| s2 | 31,457 | 469.8 M | 1,793,960 | 1,569,404 | 4,800 / 883.3 M |

Registry per-round GPU-s equal the round JSONs' `secs` to ≤ 3 s. Round time 3,660–4,635 s, growing. Reads: 5.28 GPU-h
over all seeds (read rows carry the *sample* seed in `seed`, not the training seed, so per-training-seed read compute has
to be split by `ckpt`). Ladder + reads = 32.4 GPU-h; reads ran beside the ladders, so pod-hours (29.86 per
`BUDGET_WARNING`) are lower. Seeds are within 1.06× of each other on every metric.

### Pre-registered expectations against my recount

| expectation | per seed s0 / s1 / s2 | verdict |
|---|---|---|
| new targets +20 to +40 | +20 / +68 / +22 | s0, s2 hit (at the bottom edge); s1 **miss** |
| new transfer +10 to +20 | +17 / +60 / +33 | s0 hit; s1, s2 **miss** (above) |
| new per round mostly ≤ 8 by r13–r16 | s1 18, 20 at r13–r14 | s0, s2 hit; s1 **miss** |
| target sample acc 0.92–0.95 | 0.937 / 0.944 / 0.942 | hit |
| C pass@256 unchanged within r8 spread | +0.083 / +0.457 / +0.107 vs 0.055 | **miss** on all three |
| tb72 within ±3 of r8 | +3 / +9 / +3 | s1 **miss** |
| h250 within ±3 of r8 | 0 / +10 / +2 | s1 **miss** |
| rr1316 ±10, long2 ±1 | +5/+8/+9; 0/+1/0 | hit |
| Falsifier 1 (≥ 60 new targets on ≥ 2 seeds) | 1 seed | does not fire |
| Falsifier 2 (C pass@256) | mean +0.216, 3/3 rising | **fires** |

My phase-1 reading: "saturated" as pre-registered is **falsified** (falsifier 2), on the pre-registered quantity. The
target-count side looks saturated on two seeds; s1 escaped by picking up excluded-middle proofs at r13–r14, and its
group-C, tb72 and h250 gains are mostly that. n = 3 training seeds, one continuation each.
