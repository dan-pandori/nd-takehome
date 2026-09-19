# Review of round3-run4a (reductio vs model size) — reviewer session, 2026-09-19

Independent of the executor. Phase 1 (§Recount) was written in `~/review/round3-run4a/` with the executor's write-ups
removed, **before** reading `run4a.md`, `numbers.md`, `log.md`, `STATUS.md`, `summary.json` or `run4a_analysis.py`.
Code: `review_r3_4a_lib.py` (my own proof parser, start-index normaliser, dependency pruner, strict-reductio predicate,
depth counter, renaming-class canonicaliser — only the unmodified `nd_verify` is imported from the repository),
`review_r3_4a_recount.py`, `review_r3_4a_splits.py`; outputs `artifacts/review_r3_4a/{recount,splits}.json`.

## §Recount (phase 1)

### Hard constraints — all pass

| check | result |
|---|---|
| `nd_verify/verify.py` blob hash | `1cfed53b…` = `origin/main` = `origin/dan_novelty` = `HEAD` (`__init__.py` `dfa3bc3f…` likewise) |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064…` identical on `origin/main`, `origin/dan_novelty`, `HEAD` (2026-09-15 07:38 UTC, untouched) |
| evaluation / test files in training code | `grep` for `test_long|test_short|score_test|TEST_RUN` over `train.py`, `expert_iter.py`, `coverage.py`, `eval_set.py`, `r3_4a_*.py`, `pod/r3_4a/*`: **no hit**. `train.py --heldout` is read for a no-gradient validation loss only; `expert_iter.py` reads transfer / held-out / validation-36 for evaluation and as an exclusion list; `r3_4a_pool.py` reads validation-36 only to drop its classes. The run changed no core code (diff vs merge-base `e1d6a3b` adds only `pod/r3_4a/*`, `r3_4a_*.py`, `run4a_*.py`). |
| gate 0 | pre-registration commits `da5bdd8` 17:55:56Z / `defddcb` 17:56:06Z; first pod of the run (`r4a-1`) created 17:56:44Z (`~/pods.log`). Expectations precede the first pod, by 48 s. |
| cap 6, no hand-/LLM-written proofs | training set: 155,000 records, 31,000 per length 2–6, max 6 lines, **0** verifier failures on all 155,000 (re-verified by me), and **every** `(prompt, proof)` pair is found verbatim in a generator-made source set (`train_depth3_f0_a1` 62,140; bucket `round2/run2/data/r2/train_r2_{impi_ore_f0, negi_ande_hyp_f0, ori_ore_f0, struct}` 35,357 / 25,191 / 18,514 / 13,798; unaccounted 0). |
| f = 0 | my strict predicate fires on **0 / 155,000** training proofs, on both the pruned and the written form (2,563 proofs use `DN` and 5,336 use `NEGI`, never in the `NEGI(~G) → DN` shape). |
| one test-file run | no test file touched by the run. |
| live pods | `podls` empty at 01:10Z. |

### Split disjointness by renaming class (my canonicaliser: minimum over the 24 atom bijections)

Training set (155,000 classes, no internal duplicates) vs every pool: targets_reductio_req (300) **0**, transfer_reductio_req
(150) **0**, held-out (5,000) **0**, validation-36 **0**, targets_reductio / transfer_reductio / targets_reductio2 /
transfer_reductio2 / r3_2 targets_reductio_req6 **0** each. Pool vs pool (targets, transfer, held-out, validation-36): 0
for all six pairs. RL rows of the pulled mix files (only `ei_m85_s0/mix_1–8` were pulled; 4,328 RL rows, 892 distinct):
all carry target prompts, none carries a transfer / held-out / validation prompt, all verify, all strict reductio; the
160,000 replay rows are all training-set rows.

Stricter than the repository's notion (also identifying premise reorderings): 25 held-out theorems and 2 validation-36
theorems (`modus_ponens`, `modus_tollens`) have a premise-permuted twin in the training set; targets and transfer still
0. This is inherited from the generator's key, does not touch any acquisition number here, and moves the held-out gate
by at most 25 / 5,000 = 0.005.

### Verifier re-runs

Every proof in every EI / frozen arm sample (400 random records per arm where the arm has more, otherwise all): **0
failures** in 4,321 checks; every distinct stored proof of every coverage file (141): 0 failures; all 5,000 greedy
held-out outputs of all 19 checkpoints re-verified (my count equals the stored `solved` flag in every file). My
predicate agrees with the label stored by the pod-side classifier on all 141 distinct coverage proofs; stored `written`
agrees on all 18,516 found records; stored `pruned` differs on 113 records, all of one target (see *8-line stratum*).
`found_r` files are cumulative and mutually consistent in every arm (0 inconsistencies); `acq_<tag>.jsonl` (the input of
the pass@10⁴ run) equals my acquired set in all 8 igniting arms; every b10k file covers every acquired target with
10,000 samples.

### Per-draw table (my counts)

Config **A** = lr 3e-4 / 6,000 steps (tags `m25_*`, `m85_*`); config **B** = the pre-registered retry, lr 1e-4 / 12,000
steps (`m25B_*`, `m85B_*`); `m3_*` = campaign command at 3.2M on the rebuilt set. Pre-RL = 300 × 2,000 samples (600,000
confirmed per file). "acquired" = ≥ 1 verified proof whose normalised, pruned form satisfies my strict predicate.
EI-only = acquired targets with 0 verified samples in 10,000 fresh base samples ÷ acquired.

| draw | params | held-out greedy | final val | pre-RL strict hits | rate | targets hit | EI acquired, rounds 1…8 | ign. round | 7/8/9/10 | frozen | base-reach@10⁴ | EI-only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| m3_s0 | 3,210,240 | 0.8668 | 0.0825 | 0 | 0 | 0 | 0 ×8 | – | 0/0/0/0 | 0 | – | undefined |
| m3_s1 | 3,210,240 | 0.8770 | 0.0827 | 14 | 2.3e-5 | 3 | 0,1,3,7,8,11,21,32 | 4 | 32/0/0/0 | 2 | 5 | 27/32 = 0.844 |
| m3_s2 | 3,210,240 | 0.8712 | 0.0825 | 0 | 0 | 0 | 0 ×8 | – | 0/0/0/0 | 0 | – | undefined |
| m25_s0 (A) | 25,321,472 | 0.8926 | 0.0820 | 1,872 | 3.1e-3 | 11 | 4,13,32,38,40,45,45,45 | 2 | 44/1/0/0 | 7 | 15 | 30/45 = 0.667 |
| m25_s1 (A) | 25,321,472 | 0.8972 | 0.0829 | 830 | 1.4e-3 | 10 | 4,20,37,49,52,52,52,52 | 2 | 52/0/0/0 | 7 | 11 | 41/52 = 0.788 |
| m25_s2 (A) | 25,321,472 | 0.9078 | 0.0822 | 14 | 2.3e-5 | 3 | 0,1,15,29,36,38,39,40 | 3 | 39/1/0/0 | 1 | 6 | 34/40 = 0.850 |
| m25B_s0 | 25,321,472 | 0.9104 | 0.0820 | 3 | 5.0e-6 | 2 | 0 ×8 (never trained) | – | 0/0/0/0 | 0 | – | undefined |
| m25B_s1 | 25,321,472 | 0.8972 | 0.0820 | 0 | 0 | 0 | 0 ×8 | – | 0/0/0/0 | 0 | – | undefined |
| m25B_s2 | 25,321,472 | 0.9104 | 0.0820 | 131 | 2.2e-4 | 5 | 0,1,9,31,39,43,44,48 | 3 | 48/0/0/0 | 2 | 10 | 38/48 = 0.792 |
| m85_s0 (A) | 85,208,064 | 0.8988 | 0.0820 | 37 | 6.2e-5 | 3 | 1,6,30,39,42,53,53,53 | 2 | 52/1/0/0 | 2 | 4 | 49/53 = 0.925 |
| m85_s1 (A) | 85,208,064 | 0.9134 | 0.0824 | 49 | 8.2e-5 | 2 | 1,11,28,33,42,46,51,52 | 2 | 52/0/0/0 | 2 | 5 | 47/52 = 0.904 |
| m85_s2 (A) | 85,208,064 | 0.8940 | 0.0823 | 6 | 1.0e-5 | 3 | 0 ×8 (never trained) | – | 0/0/0/0 | 0 | – | undefined |
| m85B_s0 | 85,208,064 | 0.9160 | 0.0820 | 0 | 0 | 0 | 0 ×8 | – | 0/0/0/0 | 0 | – | undefined |
| m85B_s1 | 85,208,064 | 0.9152 | 0.0821 | 4 | 6.7e-6 | 3 | 0 ×8 (never trained) | – | 0/0/0/0 | 0 | – | undefined |
| m85B_s2 | 85,208,064 | 0.9148 | 0.0821 | 1,548 | 2.6e-3 | 12 | 4,16,30,50,52,52,52,52 | 2 | 52/0/0/0 | 7 | 13 | 39/52 = 0.750 |
| m85_s3…s6 (A, pre-RL only, not pre-registered) | 85,208,064 | 0.8962 / 0.9008 / 0.8956 / 0.9022 | 0.0820–0.0824 | 13 / 2 / 60 / 8 | 2.2e-5 / 3.3e-6 / 1.0e-4 / 1.3e-5 | 2 / 1 / 7 / 5 | – | – | – | – | – | – |

Further facts from the same files:

- **Every pre-RL hit, at every size, is on a 7-line target of schema `nand_neg` or `negimp_to_pos`** (100 % of 4,591 hits
  over 19 checkpoints); no checkpoint has a verified sample on any 8-, 9- or 10-line target in 600,000 (+ up to 530,000
  b10k) samples.
- **Oracle:** 0 verified-without-pattern samples in any coverage file, 0 targets solved by a pattern-free proof in any
  arm (every solved target is an acquired target).
- **Distinct proofs (start-index-normalised):** one per acquired target in nearly every arm (e.g. `ei_m85_s0` 2,193 raw
  records → 53 distinct; `ei_m25_s1` 2,229 → 53 over 52 targets). Raw record counts are start-index duplicates and
  must not be quoted as proof counts.
- **8-line stratum:** the single "8-line" acquisition (in `m25_s0`, `m25_s2`, `m85_s0`, and the exploratory lr 3e-5 arm) is
  always `targets_reductio_req_42`, `( ( ~ ( P & S ) ) > R ) , ( ( ~ R ) > ( ~ R ) ) , ( ~ R ) |- ( P & S )`: a
  `negimp_to_pos` instance with an **unused premise**. Its proof is the 7-line shape plus the mandatory extra `PR` line
  (my pruner keeps PR lines → 8; the pod-side `pruned` field says 7 — that is the whole 113-record disagreement).
  Genuine 8-line acquisition is **0 in every arm**; 9–10-line 0 in every arm.
- **Frozen twins:** 0–7 targets, all 7-line, and in every arm a subset of what the base also reaches in the pre-RL +
  b10k samples. Frozen twins of never-training arms reproduce the EI arm sample-for-sample (same seeds), as they should.
- **Never-trained arms:** `mix_rl_records` = 0 in all 8 rounds of the four zero-rate arms **and** of the three
  non-zero-but-rare arms (`m25B_s0` 3 hits, `m85B_s1` 4 hits, `m85_s2` 6 hits per 600k). With 8 × 32 × 300 = 76,800 EI
  attempts the expected number of hits for those three is 0.38 / 0.51 / 0.77 (P(no hit) 0.68 / 0.60 / 0.46), so their
  staying at 0 is what the base rate predicts, not an additional finding.
- **Exploratory continuation** (`x_ei_m85_s2_r9-16`, not pre-registered): `m85_s2` gets its first accepted proof in
  round 13 and goes 1 → 13 → 29 → 49 targets in rounds 13–16 (ignition round 14; 49/0/0/0). **A draw that read "0 / 300
  after 8 rounds" ignites with more attempts.**
- **Exploratory ft_lr 3e-5** (`x_ei_m85_s0_lr3e-5`): 1,9,28,33,40,46,49,51; ignition round 2; 50/1/0/0 — same picture as
  ft_lr 1e-4 (53).
- **EI-only vs a larger base sample:** adding the 2,000 pre-RL samples and the 256 frozen samples to the 10⁴ changes
  EI-only by at most 2 targets per draw (0.644, 0.750, 0.825, 0.792, 0.844, 0.906, 0.904, 0.731 in table order of the
  igniting draws).
- **EI-only tracks the base rate, not the size.** Over the 8 igniting draws, Spearman ρ(pre-RL rate, EI-only fraction)
  = **−0.80** (p = 0.017): the two highest-rate draws (25M-A s0 3.1e-3; 85M-B s2 2.6e-3) have the two lowest fractions
  (0.667, 0.750) and the same-rate pair 3.2M s1 / 25M-A s2 (both 2.3e-5) have the same fraction (0.844 / 0.850). The
  numerator is capped by the 52-target 7-line ceiling that every strongly igniting arm hits, so the fraction is
  essentially 1 − (base-reachable 7-line targets) / 52.

### Which cell is the pre-registered one?

The pre-registration says: if seed 0 misses the gate, retry once at config B and "the better configuration (by held-out
greedy of seed 0) is used for all three seeds". Seed 0: 25M A 0.8926 (misses 0.90) vs B **0.9104** (passes); 85M A 0.8988
vs B **0.9160** (both miss 0.93 → "gate missed" label). By that rule **config B is the pre-registered cell at both
sizes**; config A's three draws per size are a second, complete cell. Both were run in full, so I score both.

### Pre-registered expectations against my counts

| | expectation | my value | verdict |
|---|---|---|---|
| P1 | non-zero draws: 3.2M same-set 0–2 of 3; 25M 2 of 3 (accept 1–3); 85M ≥ 2 of 3, falsified if ≤ 1 | 3.2M **1/3**; 25M **B 2/3, A 3/3**; 85M **B 2/3, A 3/3** (A with the 4 exploratory draws 7/7) | holds in either cell. Pooled 5/6 at each new size vs 1/3 (and the quoted 4/11) at 3.2M; exact 95 % intervals 5/6 → [0.36, 1.0], 1/3 → [0.01, 0.91], 4/11 → [0.11, 0.69] overlap. |
| P2 | median strict rate of non-zero draws within 1e-5–1e-3 at both sizes; ≥ 90 % of hits on `nand_neg` / `negimp_to_pos`, 7-line only | medians: 25M-A **1.4e-3** (out, above), 25M-B 1.1e-4 (n = 2), 85M-A 6.2e-5 (with extras 2.2e-5), 85M-B 1.3e-3 (n = 2; 6.7e-6 and 2.6e-3). Schema / stratum confinement 100 %. | confinement holds; the rate band is missed at 25M-A and 85M-B. No monotone rise with size (brief's E2 ≥ 10× per step: not seen — per-size ranges 0–2.3e-5, 0–3.1e-3, 0–2.6e-3 overlap almost entirely). |
| P3 | every draw with 0 hits in 600k acquires 0 / 300, frozen 0 / 300 | 4 zero-rate draws (3.2M s0, s2; 25M-B s1; 85M-B s0): all **0 / 300**, frozen 0, never trained | holds, non-vacuous at 85M (n = 1, in cell B; vacuous in cell A). See wording caveat below. |
| P4 | every draw with rate ≥ 1e-5 ignites by round 4 and gets ≥ 45 / 52 seven-line; 8-line ≥ 5 targets in ≥ 2 igniting 85M draws; 9–10 ≤ 3; frozen ≤ 30, 7-line | ignition by round 4: 8 of 9 (miss: `m85_s2`, rate exactly 1.0e-5, no hit in 8 rounds). ≥ 45 seven-line: 5 of 9 (misses: 3.2M s1 32, 25M-A s0 44, 25M-A s2 39, `m85_s2` 0). 8-line: **0 genuine** in every arm. 9–10: 0. Frozen ≤ 7, 7-line. | ignition part mostly holds; **8-line prediction missed outright**; frozen and 9–10 hold. |
| P5 | EI-only: 25M 0.5–0.85; 85M 0.3–0.7, median ≤ 0.6; "reversed" if 85M median > 3.2M value here and > 0.88 | 3.2M 0.844; 25M 0.667 / 0.788 / 0.850 (A), 0.792 (B); 85M **0.925 / 0.904 (A), 0.750 (B)** | 25M holds; **85M missed** (all three above 0.7). Reversal criterion: met on cell A (median 0.914, n = 2) and on the pooled three (median 0.904); **not** met on the pre-registered cell B (0.750, n = 1). Given ρ = −0.80 with base rate, I do not read this as a size effect in either direction. |
| P6 | held-out greedy 25M 0.89–0.93, 85M 0.89–0.94; val ≤ 0.083 | 25M 0.8926–0.9104; 85M 0.8940–0.9160; val 0.0820–0.0829 everywhere (3.2M 0.0825–0.0827) | holds. Gate: 25M passes on B (s0, s2; s1 0.8972 does not), **85M misses 0.93 in both configs → "gate missed" must label every 85M row.** |
| P7 | 0 targets solved by a pattern-free proof | 0 | holds. |

### Things phase 2 must check against the write-up (written before reading it)

1. Which cell (A or B) the headline uses at each size, and whether the 85M rows carry "gate missed".
2. Any "8-line stratum acquired" statement: it is target 42 with an unused premise, a 7-line proof.
3. Any "zero-rate ⇒ stays at 0" / "or nothing" wording: three *non-zero* draws also stayed at 0 for 8 rounds for lack of
   attempts, and one of them ignites in rounds 13–16. A 0-in-600k draw only bounds the rate at < 5e-6 (95 %), at which
   76,800 EI attempts would yield < 0.4 expected hits. The data support "nothing within 8 × 32 attempts", not "never".
4. Any "EI-only fraction rises with size": confounded with base rate (ρ = −0.80), two seeds in one config, contradicted
   by the third 85M value.
5. Proof counts quoted as raw found records rather than normalised distinct proofs.
6. Cost and pod count (pre-registered 2 pods, a third if needed; `~/pods.log` shows six `r4a-*` pods) — deletion times
   are only in the executor's log, so the spend is not derivable in phase 1.
