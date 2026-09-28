# Review: run4-grpo (GRPO vs expert iteration at depth-3 f = 0, independent replication)

Reviewer: agent:claude, role reviewer, run id `run4-grpo-review`, 2026-09-28. No GPU used, no pod started.
Reviewed branch `dan_run4_grpo` @ 25295bc ("Salvaged partial replication results"). Raw data:
`hf://buckets/dan-pandori/nd-rl/run4-grpo/artifacts/r4/` (downloaded 2026-09-28 04:30 UTC, without
`found_transfer_*` and `mix_*`). Reviewer code and outputs: `artifacts/run4-grpo-review/` (run from
`~/review/run4-grpo-review/rv/`, paths relative to that directory).

**Model every number below is measured on, unless a row says otherwise.** Stage-1 draws s20–s25 of this run:
3,210,240-parameter transformer (`train.py` defaults, 4 layers, d 256), ND **token** format (`--mode abs`, shift on),
**from scratch**, 6,000 steps × batch 128 on `data/p2/train_depth3_f0_a1.jsonl` (155,000 records, cap 6; md5
`29276f24e77164518dc4de3a4a755633` for the copy in `~/nd-takehome/data/p2/`, same byte size as the bucket copy
`lean-format/data/p2/`). Checkpoints `ckpts/r4/stage1_depth3_f0_a1_s<s>.pt` — **none survive** (see R8). RL arms start
from these. **Checker:** every count in the run's files was produced under `nd_verify` (the run predates the
2026-09-27 Lean-only rule); the reviewer re-checked counted proofs in Lean 4 core (R6) and states counts as
"`nd_verify`-counted, Lean-confirmed" where every checked proof passed.

## §Recount (phase 1, written blind: no `run4.md`, `numbers.md`, `STATUS.md`, `log.md` read)

Own code: `rvlib.py` (parser, start-index normaliser = renumber labels in order of definition, dependency pruning =
lines the last line reaches through its citations, depth = max `|` count among kept lines; nothing imported from
`patterns.py`, `normalize.py`, `prune.py`). Ignition = first round with ≥ 20 target theorems solved by a depth-3 proof,
cumulative, min round per normalised proof; acquisition = depth-3 theorems / 1,000 at the last round (pre-registration).

### R1. What survives

| material | s20 | s21 | s22–s25 | s26–s29 (ext.) |
|---|---|---|---|---|
| Stage-1 checkpoint | – | – | – (training logs only) | – |
| coverage (base rate) file | ✓ | ✓ | ✓ | – |
| GRPO arm dirs (found/round/updates) | g8 seed 1, **round 1 only** | – | all 32 main arms (2 G × 2 lr × 2 seeds; 2 cut short: g32 s24 lr3e-5 e2 at r5, g32 s25 lr3e-5 e2 at r6) | – |
| EI / frozen arm dirs | – | – | EI 8 arms (s24 e2 to r4, s25 e2 to r6), frozen 4 | – |
| novelty file (all distinct proofs of the primary-seed arms, with round) | g8, g32, g8 lr3e-5, g32 lr3e-5, EI, frozen | same | same | – |
| sprint-sized arms | – | – | 8 (lr 1e-4, 1e-5) | – |
| ablations (`ei_*_noretain`, `grpo_g8_*_posonly`), lr 1e-5 / 3e-4 grid | – | – | – | – |

For s20/s21 the novelty files give each primary-seed arm's per-round depth-3 curve (they reproduce the found-file curves
exactly on s22–s25, 24/24 arms), but no per-update data, no held-out greedy and no second seeds. **Nothing of s26–s29
exists** in the bucket, on this VPS or anywhere in `hf://buckets/dan-pandori/nd-rl/`.

### R2. Base rates (the zero-rate claim)

Files `cov_depth3_f0_a1_s<s>.s0.jsonl`: first 300 targets of `data/p2/targets_depth3.jsonl` (checked: names
`targets_depth3_0..299`, each once), `n_tried` = 2,000 per target (600,000 per draw), T = 0.8 (log header), checkpoint
`ckpts/r4/stage1_depth3_f0_a1_s<s>.pt`. The files store every **`nd_verify`-accepted** distinct proof with its count; my
depth counter on those (`base_rate.py`):

| draw | verified samples | targets solved | depth-3 samples (pruned) | depth-3 distinct / theorems | rate |
|---|---|---|---|---|---|
| s20 | 294 | 7 | 19 | 5 / 3 | 3.2·10⁻⁵ |
| **s21** | 116 | 4 | **0** | 0 / 0 | **0** |
| s22 | 4,690 | 20 | 7 | 5 / 5 | 1.2·10⁻⁵ |
| **s23** | 793 | 5 | **0** | 0 / 0 | **0** |
| s24 | 1,619 | 37 | 1,442 | 39 / 35 | 2.4·10⁻³ |
| s25 | 2,823 | 12 | 10 | 1 / 1 | 1.7·10⁻⁵ |

Unpruned depth gives the same counts; my labels agree with the files' own `pat.depth3` flags on every proof. **Recount:
0 depth-3 samples in 600,000 on s21 and s23.** Supporting, independent of the coverage file: the frozen control at equal
attempts (256 per target on all 1,000 targets, T = 0.8) has 0 depth-3 proofs on s23 (found files) and on s21 (novelty
file, frozen source), i.e. 0 in a further 256,000 samples per draw, now over all 1,000 targets. Caveats: (a) the
counted set is `nd_verify`-accepted samples; samples `nd_verify` rejected were not stored, so a Lean-only base rate cannot
be recomputed, and since the checkpoints are lost it cannot be re-sampled either; (b) the 600,000 are on the hard first
300 targets (base solves 4–37 of them), not the 1,000 GRPO trains on — the frozen control covers the 1,000 at 256 each.

### R3. GRPO ignition and acquisition (depth-3 target theorems, cumulative)

From found files (s22–s25) and novelty files (s20, s21 primary seeds). Ignition round / round-8 acquisition:

| draw (base rate) | g8 lr1e-4 | g8 lr1e-4 e2 | g32 lr1e-4 | g32 lr1e-4 e2 | g8 lr3e-5 | g8 lr3e-5 e2 | g32 lr3e-5 | g32 lr3e-5 e2 |
|---|---|---|---|---|---|---|---|---|
| s20 (3.2e-5) | r1 / 0.505 | – | r1 / 0.475 | – | r1 / 0.460 | – | r1 / 0.440 | – |
| **s21 (0)** | r1 / 0.481 | – | r1 / 0.461 | – | r1 / 0.429 | – | r2 / 0.413 | – |
| s22 (1.2e-5) | r1 / 0.405 | r1 / 0.399 | r2 / 0.361 | r1 / 0.399 | r1 / 0.370 | r1 / 0.368 | r1 / 0.372 | r1 / 0.376 |
| **s23 (0)** | r2 / 0.423 | r1 / 0.424 | r2 / 0.389 | r3 / 0.384 | r2 / 0.416 | r1 / 0.413 | r3 / 0.373 | r4 / 0.374 |
| s24 (2.4e-3) | r1 / 0.444 | r1 / 0.457 | r1 / 0.386 | r1 / 0.403 | r1 / 0.413 | r1 / 0.405 | r1 / 0.399 | r1 / 0.363 (r5) |
| s25 (1.7e-5) | r1 / 0.476 | r1 / 0.476 | r1 / 0.453 | r1 / 0.427 | r1 / 0.433 | r1 / 0.440 | r1 / 0.387 | r1 / 0.355 (r6) |

**40 of 40 GRPO arms with surviving data ignite** (32 on s22–s25 + 4 each on s20, s21), **12 of 12 on the zero-rate
draws** (s21: 4 primary-seed arms; s23: all 8). Ignition *update* (from `updates.jsonl`, whose per-update counter I
checked equals my recount at every round boundary of every arm, 0 mismatches): lr 1e-4 arms 5–102 (4,000–81,600
samples); lr 3e-5 arms 8–160 (6,400–128,000 samples); on s23 specifically 23, 57, 59, 102 (lr 1e-4) and 39, 43, 110,
160 (lr 3e-5). No per-update data for s21. First depth-3 training sample: update 1–24 over the main arms (s23: 4–24).
Fraction of groups with reward variance at update 1: 0.04–0.15 (G = 8), 0.04–0.32 (G = 32).

Sprint-sized arms (3,200 samples, 100 updates × 4 groups × 8): depth-3 theorems at lr 1e-4 — s22 27, s23 1, s24 24,
s25 35 (3 of 4 reach 20); at lr 1e-5 — 9, 0, 10, 1.

### R4. Paired EI and frozen

| draw | EI seed = draw | EI e2 (seed + 100) | frozen (256/target) |
|---|---|---|---|
| s20 | ignites r8, 83 thms (novelty file) | – | 1 thm |
| **s21** | **no** (0 depth-3) | – | 0 |
| s22 | no (0) | r2 / 0.299 | 1 |
| **s23** | r6 / 0.255 | **no** (0) | 0 |
| s24 | r2 / 0.379 | r2 / 0.284 at r4 (cut short) | 17 |
| s25 | r3 / 0.324 | r3 / 0.288 at r6 (cut short) | 2 |

EI ignites in **6 of 8** arms on s22–s25 (7 of 10 counting the s20/s21 primary seeds); on the zero-rate draws 1 of 3 arms
with data. The two seeds of a draw disagree on s22 and s23. EI's held-out greedy at its last round 0.881–0.935.

### R5. Held-out greedy (5,000 in-distribution theorems, round 8 unless noted)

Stage-1 (frozen arm, = round-1 of EI): s22 0.881, s23 0.874, s24 0.872, s25 0.891. GRPO, last round, s22–s25 only
(none recorded for s20/s21 beyond g8 s20 r1 = 0.839):
lr 1e-4: G = 8 0.580–0.715, G = 32 0.601–0.689 (16 arms, all complete). lr 3e-5: G = 8 0.745–0.865, G = 32 0.765–0.858
(complete arms; the two cut-short arms 0.876 at r5, 0.814 at r6). Already after round 1 (32,000 samples) lr 1e-4 arms are
at 0.693–0.874. Sprint arms (3,200 samples): lr 1e-4 0.788–0.822, lr 1e-5 0.874–0.903.

### R6. Lean re-check (Lean alone decides)

`lean_recheck.py`: `nd2lean.translate(prompt, literal stored proof, require_all_pr=False)` then Lean 4 core via
`lean_gate.check_sources` (batched; `lean_judge.py`'s fallback path, files from `origin/dan`). Smoke test: two corrupted
proofs (wrong rule, wrong theorem) were rejected. Checked: **every** counted depth-3 proof on s21 (novelty file, 2,487)
and s23 (all 10 GRPO/EI arms, 4,640), all depth-3 proofs in all six coverage files, and a random 150 depth-3 + 100
other counted proofs per arm elsewhere (all proofs where an arm has fewer). **13,317 distinct (prompt, proof) pairs:
13,317 accepted, 0 rejected, 0 untranslatable** (`lean_tally.json`). All 13,317 had been accepted by `nd_verify`
(stored proofs are accepted ones), so agreement on this set is 100 %; the reverse direction (Lean accepts what
`nd_verify` rejected) is not checkable, because rejected samples were not stored.

### R7. Reachability of GRPO's depth-3 proofs under the base model

The novelty files carry each proof's start-index-marginalised log-probability under the draw's Stage-1 model at T = 0.8
(`base_logp_T08`, the executor's scoring; the checkpoints are gone, so I cannot re-score). From those values: every
distinct GRPO depth-3 proof on s20–s23 has log p < log(1/256) (s21 max −14.27, s23 max −14.86); s24 97.6–98.0 %, s25
99.8–99.9 %. Theorem-level (sum over a theorem's distinct depth-3 proofs): s21 max −13.75, s23 max −14.86; expected
number of depth-3 hits in 256 base samples, summed over all GRPO depth-3 theorems, 0.001 (s21) and < 0.001 (s23).

### R8. Model labels and checkpoints

Training logs (s22–s25 only): `params 3210240 mode abs shift True`, `train records 155000`, 6,000 steps, ≈ 215 s, saved
to `ckpts/r4/stage1_depth3_f0_a1_s<s>.pt`. No md5 was recorded and no checkpoint of this run was uploaded.
`hf://…/round3-run1/ckpts/r3_1/stage1_depth3_f0_a1_s20…s27.pt` carry the same file names but are **different
trainings** (their embedded args write to `ckpts/r3_1/`, training took 863–1,140 s, and re-scoring stored proofs at their
stored shift gives log-probabilities −36 to +16 nats away from this run's values; `ckpt_identity.py`). md5 of this run's
checkpoints: not recoverable.

### R9. Splits

Own canonicaliser (atoms renamed in order of first appearance, `F` kept as the constant, minimised over premise order),
`splits.py`: Stage-1 set (151,349 classes) ∩ targets = **0**, ∩ transfer = **0**, ∩ held-out = **21** of 5,000 — all 21
differ from a training theorem only in premise order (order-sensitive overlap 0). Pools pairwise disjoint. The 21 can
move held-out greedy by at most 0.004. Training set depth-3 count with my counter: 0 of 155,000.

### R10. Hard constraints and process

- `nd_verify/` tree `9437bb7…` on HEAD = `origin/main` = `origin/dan_run4_grpo`: unmodified.
- `artifacts/TEST_RUN_DONE` blob `1d5cf06…` = `origin/main`'s: unchanged.
- `grpo.py` trains only on `--targets` samples; `--transfer` and `--heldout` are sampled for evaluation only (lines
  247–265); no test file is read by `grpo.py`, `expert_iter.py`, `train.py`, `coverage.py` or `novelty.py` (grep).
- `nd_verify` was the reward and the counter (`grpo.py` line 34) — correct at the time (2026-09-17); every number above
  is therefore "`nd_verify` at run time, Lean-confirmed on re-check".
- Truncation: up to 6.4 % of the samples of a GRPO update hit `max_new` 400 (G = 32; ≤ 3.3 % at G = 8). Truncated samples
  get reward 0. Depth-3 proofs are ≈ 7.5 lines, far below the cap, so the depth-3 counts are not length-biased; the
  plain solve rates may be slightly low.
- Pre-registration committed 2026-09-17 23:00, amendments 1–3 at 23:10, 23:21, 23:26, each before the arms it governs
  (commit order on the branch; `~/pods.log` gate-0 comparison is in phase 2).

### R11. Shape of the acquired pattern (context for "new capability")

On s21/s23, GRPO's depth-3 proofs average 7.5–7.8 pruned lines and 7.1–7.3 term nodes (reviewer's term size: pruned
lines excluding `PR`/`R`), against 6.1–6.2 lines / 5.3–5.4 for the same arms' other proofs. **67–71 % of them
discharge a depth-3 assumption that nothing cites** (e.g. `S > (S > (Q > P))`: the third box is a vacuous `IMPI`);
EI's depth-3 proofs on s23 are the same (69 %). The base's depth-2 proofs of these targets re-order the boxes instead.
So what is crossed from zero is a **nesting habit** (open a box for every antecedent, in order), not a new inference
rule — the same object EI acquires.

## §Compare (phase 2: `run4.md`, `log.md` Run 4, `STATUS.md`, `QUESTIONS.md` on `origin/dan_run4_grpo` @ 25295bc)

`numbers.md` has **no Run 4 section** (the brief's deliverable was never written), so claims come from `run4.md` and
`log.md`. The salvage commit 25295bc also removed three `log.md` entries (02:19 s20/s21 base rates and the s27/s29
round-1 numbers; 02:25 ablations and lr grid; 02:46 pulls) and the 02:40 `STATUS.md` line; they are read from the diff.
"Reviewer" values are from §Recount; model for all rows = the 3.2 M token-format from-scratch Stage-1 draws above (none
of the executor's rows name the model — see V5).

| # | claim (source) | reviewer's value | verdict |
|---|---|---|---|
| 1 | GRPO ignited on "every draw, seed and primary setting: **30 of 30 arms**" (run4.md) | 40 of 40 arms with surviving data (32 on s22–s25 incl. both seeds; 4 primary-seed arms each on s20, s21) | **direction reproduces; the count "30" is not derivable** (no combination of the planned arms gives 30; s20/s21 second seeds and s27/s29 arms do not survive) |
| 2 | s21, s23: 0 depth-3 samples in 600,000 from the base (run4.md) | 0 and 0 (own predicate, first 300 targets, T 0.8, own Stage-1 ckpt); plus 0 in the frozen 256 × 1,000 on each | **reproduces** (under `nd_verify`; see V1) |
| 3 | s27, s29: 0 in 600,000; GRPO ignites there (run4.md "XXX"; log 02:07, 02:19) | no file exists | **not reproducible** — nothing of s26–s29 survives |
| 4 | ignition at update 5–110 (4,000–88,000 samples) (run4.md) | 5–160 (4,000–128,000): `grpo_g32_s23_lr3e-5_e2` ignites at update 160; lr 1e-4 only: 5–102 | **differs**: upper end 160 / 128,000, not 110 / 88,000 |
| 5 | round-8 GRPO acquisition 0.36–0.48 (run4.md) | complete arms 0.361–0.476 on s22–s25; 0.413–0.505 on s20/s21 (novelty files); 0.355/0.363 in the two cut-short arms | **reproduces for s22–s25; 0.36–0.51 over all surviving arms** |
| 6 | paired EI ignited in **6 of 10** arms (run4.md) | 6 of 8 on s22–s25; 7 of 10 adding the s20/s21 primary seeds (s20 ignites r8) | **differs / not derivable**: surviving arms give 7 of 10 or 6 of 8; the executor's 10 cannot be identified |
| 7 | EI acquisition 0.25–0.38 where it ignited (run4.md) | 0.255–0.379 on s22–s25; s20 EI ignites at r8 with 0.083 | **reproduces with correction**: 0.08–0.38 (s20 is "late", as the text says, but its value falls outside the range) |
| 8 | "every depth-3 proof GRPO found is unreachable by sampling … log p < 1/256 for 100 % of 4,300+ proofs on the five low-rate draws, medians −39 to −66" (run4.md) | from the executor's stored scores: 100 % on s20–s23; s25 1 theorem above 1/256 (log 01:19 itself says 745/746); medians −39.0 to −65.6; 12,570 GRPO depth-3 proofs on the five draws over the 4 primary settings | **reproduces with correction** (99.9 % on s25, not 100 %). Not independently re-scorable: checkpoints lost |
| 9 | s24: 10 theorems above 1/256 (run4.md) | 10 | reproduces |
| 10 | held-out greedy at r8: lr 1e-4 0.54–0.72, EI 0.88–0.93 (run4.md) | lr 1e-4 0.580–0.715 (s22–s25); EI 0.881–0.935 | **reproduces for the surviving arms**; the 0.54 low end (s20/s21) is not derivable |
| 11 | lr 3e-5 keeps 0.75–0.86 and still ignites every arm (run4.md) | 0.745–0.865 (14 complete arms), 20 of 20 surviving lr 3e-5 arms ignite | reproduces |
| 12 | lr 1e-5 ignites (s20 322 by r2); lr 3e-4 collapses (G32 held-out 0.17) (run4.md, log 02:07/02:25) | no file | **not reproducible** |
| 13 | G = 32 ignites later than G = 8 (update 11–110 vs 5–57) (run4.md) | later in 14 of 16 matched pairs (1 tie, 1 earlier); G = 32 range 6–160, G = 8 5–57 | **direction reproduces; G = 32 range differs** (6–160) |
| 14 | at update 1, 7–32 % of groups carry variance (run4.md) | 4–32 % (e2 seeds 4–5 %) | **differs** at the low end |
| 15 | variance rises to 0.3–0.5 within 20 updates on every draw (run4.md) | max over the first 20 updates 0.22–0.60; below 0.30 in three s23 G = 8 arms | **differs**: not on every arm of the zero-rate draw s23 |
| 16 | first depth-3 successes at update 1–24 (run4.md) | 1–24 | reproduces |
| 17 | sprint-sized budget: 24–60 depth-3 targets on 4 of 6 draws at lr 1e-4; 0–10 at lr 1e-5 (run4.md, log 23:46) | s22 27, s23 1, s24 24, s25 35 at 1e-4; 9, 0, 10, 1 at 1e-5; s20/s21 not on disk | **reproduces for the four surviving draws**; s20 (60) / s21 (6) not derivable |
| 18 | "the sprint's null result reproduces on budget and lr alone" (run4.md) | lr 1e-5 finds 9–10 depth-3 theorems on two draws | **reword**: fewer than 20 (no ignition), not a null |
| 19 | E1 held (2 of 6 zero-rate) | s21, s23 zero; s20/s22/s25 at 1–3·10⁻⁵ | reproduces |
| 20 | E5 held ("variance rises past 0.3 in igniting arms") | pre-registered E5: > 0.30 **by the ignition round** fails in 13 of 32 arms (all G = 8; max before ignition 0.21–0.30); "G = 32 higher than G = 8 at every update" fails at 406 of 4,963 paired updates | **mis-scored: E5 failed** |
| 21 | E7 held at 3e-5 "for 5 of 8 arms" | within 0.05 of Stage-1: 5 of 16 lr 3e-5 arms (4 of 14 complete); 0 of 16 at lr 1e-4 | **differs** (5 of 16, not 5 of 8) |
| 22 | E6 wrong: GRPO solves more targets than EI | GRPO 616–815 vs EI 362–682 at r8, GRPO above both EI seeds in every arm on s22, s23 and in 7 of 8 on s24, s25 (the exceptions are the two cut-short g32 lr 3e-5 e2 arms) | reproduces |
| 23 | E2 wrong on seed agreement: seeds disagree on 3 draws | disagree on s22 and s23; agree on s24, s25 (both ignite); s20/s21 second seeds lost | **2 reproduce; the third not derivable** |
| 24 | E3, E4 wrong in the opposite direction | GRPO ignites on 12 of 12 zero-rate arms, earlier than EI | reproduces; the misses are reported as misses |
| 25 | ablations: `ei_noretain` collapses (held-out 0.025 / 0.006), `grpo_g8_posonly` acq 0.505 / 0.481 (log 02:25, deleted by the salvage) | paired G8 lr 1e-4 arms 0.505 / 0.481 reproduce; the ablation arms themselves do not survive | **not reproducible** |
| 26 | pre-registration 23:00:11 before the first pod 23:01:07; amendments before their arms (run4.md, log) | commit times agree (49ecc8a 23:00:11; 2e69d57, d0d5ed0, d9002fd at 23:10–23:26); the pod time cannot be checked from this host's `pods.log` (no `r4-*` entries; the run used another VPS) | **reproduces from git; pod time not verifiable here**. Amendment 2 was written after round-1 results and says so |
| 27 | comparison with the round-2 executor's run 4, claim by claim (Dan's note in the brief) | absent from `run4.md` | **missing** |

## §Verdict

**V1 — the zero-base-rate claim.** On draws s21 and s23 the base model produced **0 depth-3 proofs in 600,000 samples**
(first 300 targets, T = 0.8, own Stage-1 checkpoint), and 0 more in the frozen control's 256,000 samples over all 1,000
targets; my own predicate gives 0 on both, and the executor's GRPO depth-3 proofs have theorem-level base probability
≤ e^−13.75 (s21) and ≤ e^−14.86 (s23) under those checkpoints (executor's scores). The claim reproduces **as a
statement about `nd_verify`-accepted samples of the run's own checkpoints**. It cannot be re-measured under the Lean-only
judge (rejected samples were not stored), and it cannot be re-measured at all on these draws, with or without a GPU,
because **no checkpoint of this run survives** (the `round3-run1` files with the same names are different trainings).
It is therefore a closed, not an extensible, result. The extension draws s27/s29 — half of the "four zero-rate draws" in
the deleted STATUS line — have **no surviving evidence**.

**V2 — ignition from zero.** GRPO ignites in **12 of 12** arms with data on the two zero-rate draws (s21: 4 primary-seed
arms; s23: 8 arms, both seeds), at update 23–160 on s23 (18,400–128,000 samples, i.e. within the 256,000 samples in
which the frozen base found none), while paired EI ignites in 1 of 3 arms there. Every counted proof Lean-checked on
these draws (7,127, plus the rest of 13,317 checked) is accepted by Lean 4. This stands, with n = 2 zero-rate draws.

**V3 — must be reworded.** "30 of 30 arms" → "40 of 40 arms whose files survive (12 of 12 on the zero-rate draws s21,
s23)"; drop s27/s29 or mark them "reported in the log, files lost". "6 of 10" EI → "6 of 8 on s22–s25 (7 of 10 with the
surviving s20/s21 primary seeds)". Ignition "update 5–110" → "5–160 (4,000–128,000 samples)"; G = 32 "11–110" →
"6–160". "100 % … on the five low-rate draws" → "100 % on s20–s23, 99.9 % on s25". Variance "7–32 %" → "4–32 %", and
"rises to 0.3–0.5 within 20 updates on every draw" → "on every draw except three s23 G = 8 arms (max 0.22–0.28)".
E5 → **failed** (both halves), E7 at 3e-5 → "5 of 16". "RL against a verifier in general" (E9) → "on-policy GRPO too,
with one model size, one pretraining set, one pattern". "The sprint's null reproduces" → "the sprint-sized budget stays
below the ignition line at lr 1e-5 (0–10 theorems)".

**V4 — not supported by surviving files.** Everything about s26–s29; the lr 1e-5 / 3e-4 grid; the `noretain` and
`posonly` ablations (and hence the E9 sentence about EI's retained slice); s20/s21 second seeds, per-update traces and
held-out values (the 0.54 low end); the "4,300+" proof count. These rest on log entries only, and three of those entries
were deleted by the salvage commit.

**V5 — labels.** No executor claim names its model (checkpoint, 3.2 M parameters, ND token format `abs`, from scratch on
`train_depth3_f0_a1`) or its checker (`nd_verify`, pre-2026-09-27). Both are findings; every row above applies to the
3.2 M token-format from-scratch draws s20–s25 of this run, and every count is `nd_verify`-counted and Lean-confirmed on
re-check (13,317 of 13,317). `numbers.md` §Run 4 does not exist; checkpoints were never uploaded and md5s never recorded.

**V6 — what "depth-3" is here (new, R11).** About 70 % of GRPO's (and EI's) depth-3 proofs on the zero-rate draws open a
third box whose assumption nothing cites; the base proves the same targets at depth 2 by re-ordering boxes. What is
crossed from zero is a proof-layout habit, reached by training, not a new inference rule. The run's result should be
quoted with that scope.

### What stands (quotable)

> In an independent replication (run4-grpo, 2026-09-17/18; 3.2 M-parameter ND-token transformers trained from scratch on
> `train_depth3_f0_a1`, a set with no depth-3 proof), two of six Stage-1 draws (s21, s23) produced no depth-3 proof in
> 600,000 base samples on the 300 hardest targets and none in 256,000 samples over all 1,000 targets (`nd_verify` at run
> time; the checkpoints are lost, so this cannot be re-measured under Lean). On-policy GRPO (groups of 8 or 32, binary
> reward, group-mean baseline, no KL, lr 1e-4 or 3e-5, 256,000 samples) ignited the depth-3 pattern (≥ 20 of 1,000 target
> theorems) in all 12 arms with surviving files on those two draws, after 18,400–128,000 samples on s23, reaching
> 0.37–0.48 acquisition; paired expert iteration ignited in 1 of 3 arms there. Across all six draws, 40 of 40 surviving
> GRPO arms and 6 of 8 paired EI arms on s22–s25 ignited. lr 1e-4 cost held-out greedy (0.58–0.72 vs 0.87–0.89 at
> Stage-1); lr 3e-5 ignited every arm at 0.75–0.87. Every depth-3 proof checked (7,127 on the zero-rate draws) is accepted
> by Lean 4. About 70 % of these depth-3 proofs nest a third, unused assumption: the acquired pattern is a box-nesting
> habit.

### Next measurement

What would settle V1/V4: fresh `a1` draws screened for zero rate **with Lean as the judge and every sample stored**
(not only verified ones), checkpoints uploaded with md5s, then GRPO (G = 8, lr 3e-5, 2 seeds) and EI (2 seeds) on ≥ 3
zero-rate draws, plus the `posonly` / `noretain` ablations on one of them. Nothing here was checkable with a GPU either:
the lost checkpoints cannot be recreated. Estimated cost on RTX 3090s (≈ 35 min per 600,000-sample Lean screen,
≈ 40 min per 8-round arm): ≈ 8 screens + 15 arms ≈ 15 GPU-hours ≈ $8–12 at the billed 3090 rate (check `costPerHr`).

Reviewer outputs: `artifacts/run4-grpo-review/` — `base_rate.json`, `arms.json`, `novelty_recount.json`,
`updates_check.json`, `lean_tally.json` (+ `lean_rejects.json`, empty), `splits.json`, `ckpt_identity.json`,
`shape.json`, `phase2_extra.txt`.
