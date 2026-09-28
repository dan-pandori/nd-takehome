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
