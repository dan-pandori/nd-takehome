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

## §Compare (phase 2: `run_rl_continue.md`, `numbers.md` § rl-continue, `log.md` § rl-continue, `STATUS.md`)

Extra reviewer checks for this phase: `review_rc/phase2.py` → `review_rc/rv/phase2.log`; the Lean example in
`run_rl_continue.md` was re-run by me (`'t' depends on axioms: [propext, Classical.choice, Quot.sound]`, no errors).

| claim (where) | my value | verdict |
|---|---|---|
| r8 checkpoints md5 = `trajectory`'s; resume loaded 229,482 / 271,490 / 250,560 proofs; found_8 ⊆ found_9 (log, numbers) | same; and found_8 ⊆ found_16 (all rows) | reproduces |
| new targets r9–r16 +20 / +68 / +22; targets_cum 4,383→4,403, 4,365→4,433, 4,407→4,429 (all) | same | reproduces |
| new transfer +17 / +60 / +33; transfer_cum 2,185→2,202, 2,170→2,230, 2,190→2,223 | same | reproduces |
| target sample acc 0.918→0.937, 0.918→0.944, 0.924→0.942 | same | reproduces |
| s1 +18 / +20 at r13 / r14 | same | reproduces |
| "35 of its 48 new targets in r13–r16 have L_true 9, and 34 of them are the `excluded_middle` schema" (numbers) | 48 → 35 → 34 | reproduces |
| "At r16, s0 solves 1 of those 35 and s2 solves 9" (numbers, log) | 1 / 9 of the 35 | reproduces |
| "34 new targets are excluded-middle instances (s0 solves 1 of them at r16, s2 9)" (run headline) | of the **34 excluded-middle** targets s0 solves **0** and s2 **8**; the "1 / 9" are of the 35 L_true-9 targets (the extra one, `la_rl_targets_329`, is not an excluded-middle instance and both seeds solve it) | **differs** — reword (numbers.md has it right) |
| s1's burst = excluded middle ("one skill") (run) | 34/35 late L_true-9 targets are the schema; 36/68 of s1's new targets have an `X ∨ ¬X` line in the first proof (r13 11/18, r14 16/20). Of the pool's 40 `excluded_middle` targets s1 holds 1 at r8 → 38 at r16; s2 2 → 11; s0 1 → 1 | supported for the burst; the other ~30 of s1's +68 are spread over other schemas |
| group C sizes 36 / 35 / 28; C pass@256 (x1) r8 .083/.029/.036 → r12 .139/.229/.179 → r16 .167/.486/.143; mean 0.049 → 0.265; C solved 3/1/1 → 6/17/4 | same | reproduces |
| r8 seed spread 0.055 (numbers) / 0.054 (log) | 0.0548 | reproduces (rounding) |
| Falsifier 1 not met; falsifier 2 met (+0.216 > 0.055, 3/3) | same | reproduces |
| "s1's 16 new C solves include 7 A ∨ ¬A instances, Peirce's law and (P → Q) ∨ (Q → P)" (numbers) | 7 A ∨ ¬A (6 h250 + `textbook_a104fab`), Peirce, (P→Q)∨(Q→P); plus two Peirce-shaped h250 instances | reproduces |
| "Its new group C solves are classical too" (run) | 3 of the 16 are intuitionistically valid (`textbook_48e308…` ⊢ F, `textbook_94b2fb…` S-combinator, `la_transfer_205` distribution) | **overstated** — "most (13 of 16)" |
| "The RL is not saturated on the hard theorems" (run) | C rises on 3/3 seeds; the s0 / s2 gains are 3 theorems each (s2 also lost one 1/256 solve), but C pass@8 rises 0.003 → 0.081 and 0.001 → 0.081, far beyond single-hit re-draw | stands, as "not saturated on group C at k 256 on any seed; large on one seed" |
| tb72 x1 r8/r12/r16 48/51/51, 48/52/57, 53/58/56; h250 240/239/240, 236/241/246, 237/239/239 | same | reproduces |
| rr600 13–16 (k 64) 377→382, 362→370, 367→376; long2 21→21, 20→21, 20→20 | same; r8 and r16 at identical settings (k 64, batch 512, seed 0) | reproduces |
| "reads 0–0.54 % [cut off] (`best-state`'s cap diagnostic: non-terminating actions, ≤ 2 textbook problems)" (numbers); "0–0.54 % of read samples hit the caps" (run) | 0.54 % is the largest **whole-read** fraction. Per stratum: tb72 group C 1.03 % (s1 r16), h250 C 0.75 %, rr1316 L 13 0.73 %, tb72 rows up to 6.6 %. Cut samples are spread over 18 / 23 / 9 tb72 rows at r16, the top 2 rows hold 29/72, 27/100, 10/23 | **differs** — the "≤ 2 textbook problems" diagnostic is inherited and does not hold here; most reported strata exceed the policy's ≈ 0.1 % (settings inherited from `trajectory`, same at r8; the bias is downward on C at both endpoints, so the falsifier-2 verdict is not at risk, but the policy breach should be stated) |
| ladder truncated + step-capped 0.19–0.47 % per round | 0.19–0.47 % from round JSON `env_end` | reproduces |
| compute: ladder 33,261 / 32,844 / 31,471 GPU-s, 479/482/470 M gen tokens, 1.794 M attempts, 4,800 steps, 906/905/883 M train tokens, 1.57 M Lean checks; reads 6,074 / 6,826 / 6,084 GPU-s | 33,248 / 32,830 / 31,457 (+ 13–14 s of job-level rows the executor included); reads total 18,998 vs 18,984 | reproduces |
| 29.96 pod-h, $14.68 (A40 $0.49/h) | `BUDGET_WARNING` at 03:30: 29.86 of 30.40 h; consistent | not independently derivable (podbudget) |
| pre-registration before the first pod (17:23:14 vs 17:24) | commit `8cf9ccfe` 17:23:14; first ladder line 17:26:30; file never edited | reproduces |
| budget deviations: r12 x0 and r16 x0 tb72/h250 dropped, rr1316 at k 64, rr/long2 at batch 512 | as in `pod/rc/*` and the eval args; numbers.md lists r12 seed-1-only but not the dropped r16 x0 reads (log.md does) | minor omission in numbers.md |

**Labels.** Every number in `run_rl_continue.md`, `numbers.md` and the STATUS lines names the models (`trajectory`'s
best-cap12 T1 ladders, 9.56 M ALiBiGPT, `lean_staten`, from scratch on K12) and the checker (Lean alone). The r8 tb72/h250
values are `trajectory`'s files and are labelled so. No pre-2026-09-27 numbers are compared. No unlabelled number found.

**Wording against n.** The run claims a difference across seeds only as "3/3 seeds" (falsifier 2) and calls the
excluded-middle burst "on one seed" — both match n = 3. "Finding: s1's jump is one skill" is a single-seed observation and
the write-up says so in Limits.

**Expectations.** Written and committed before the first pod; the misses (s1 targets, s1/s2 transfer, C pass@256, s1
tb72/h250) are reported as misses in the headline table.

**Missing per policy.** (1) No term sizes are reported anywhere (policy: report term size as well as lines); mine are in
§Recount (new-target first proofs: median 70–97 Expr nodes vs 17–20.5 lines). (2) No guided read-out — the guided-by-default
rule is dated 2026-10-04, after this run's pre-registration and reads, so this is not held against the run; a guided
read of the r16 checkpoints is the natural follow-up. (3) Max-cap cut-offs above ≈ 0.1 % per stratum not reported as such
(row above).

## §Verdict

**Stands.** Every count the pre-registration promised reproduces from the pulled files with my own code: per-seed new
targets (+20 / +68 / +22) and transfer (+17 / +60 / +33), sample accuracy, tb72 / h250 / rr1316 / long2 read-outs, group C
pass@256 at r8 / r12 / r16, compute. The continuation is seamless (checkpoint md5s, found-set carry-over, round chain). 0 of
1,669 counted proofs re-checked in Lean were rejected (harness validated on four negative controls). No hard-constraint
violation; splits are clean (the 1 tb72 and 4 transfer class overlaps with training touch no counted new solve or C theorem).
**Falsifier 2 fires on the pre-registered quantity, on every seed, and "saturated" is falsified as pre-registered**;
falsifier 1 does not fire. On target counts, s0 and s2 look saturated (≤ 4 per round after r10 on s2, ≤ 3 after r11 on s0);
s1 is not, and s1's r13–r14 burst is the `excluded_middle` schema (1 → 38 of 40 pool instances).

**Reword.**
1. `run_rl_continue.md` headline: "34 new targets are excluded-middle instances (s0 solves 1 of them at r16, s2 9)" →
   s0 solves **0** and s2 **8** of the 34; the 1 / 9 refer to the 35 L_true-9 targets.
2. "Its new group C solves are classical too" → 13 of the 16; three are intuitionistic.
3. Cap-offs: "0–0.54 %" is the whole-read maximum; per stratum it reaches 1.03 % (group C) and single rows 6.6 %, above
   the policy's ≈ 0.1 %, and the inherited "≤ 2 textbook problems" diagnostic does not hold here. State it and the
   direction of the bias (downward on C at both endpoints).
4. "Not saturated on the hard theorems": add that on s0 and s2 the C gain is 3 theorems each at k 256 (pass@8 rises
   ≈ 25–75×, which is what makes it more than re-draw noise), and that the large gain is s1's.

**Not supported / not derivable.** Pod-hours and dollars come from `podbudget`, not from pulled files (consistent with
`BUDGET_WARNING`).

**Next measurements.** (a) Whether excluded middle is reachable for s0 / s2 with more rounds or is a seed-specific
discovery: continue s0 and s2 from r16 for 8 rounds (or seed-swap: inject s1's r14 accepted LEM proofs into s0's mix as a
replay-only control), with the 40-instance `excluded_middle` schema count as the pre-registered readout. (b) Re-read r8 and
r16 group C at max_action / max_steps doubled to bound the cap bias. (c) Guided read-out of the r16 checkpoints (policy
2026-10-04). (d) More seeds: the target-count verdict rests on one seed escaping; with 3 seeds one cannot say how often
the escape happens.
