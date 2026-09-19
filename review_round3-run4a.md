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

## §Compare (phase 2) — executor's `run4a.md`, `numbers.md` §Round 3 — Run 4a, `log.md`, `STATUS.md` against my recount

Read only after commit `69d9dfc` (phase 1). Additional phase-2 checks of mine: transfer strata, held-out split with my
predicate, coverage logs vs files, the quoted run-5 files, the figures, a token scan of everything uploaded to the
public bucket (no `hf_…` / `rpa_…` / `sk-ant-…` string in `artifacts/r3_4a`, `data/r3_4a`, `pod/r3_4a`), bucket listing
(1,084 / 29 / 18 files, as stated).

| # | claim (where) | my independent value | verdict |
|---|---|---|---|
| 1 | Parameters 3,210,240 / 25,321,472 / 85,208,064 | same (train logs) | reproduces |
| 2 | Set: 155,000 = 31,000 × 5, reductio 0 (pruned and written), class overlap 0 with targets / transfer / held-out / req6 / val-36 | same, with my predicate and my canonicaliser; plus 0 verifier failures on all 155,000 and 100 % provenance in the five generator sets | reproduces (premise-order-free twins: 25 held-out, 2 val-36 — inherited, immaterial here) |
| 3 | Held-out greedy per draw (19 values), val 0.0820–0.0829 | identical to 4 d.p., from re-verifying every greedy output | reproduces |
| 4 | 679 of 5,000 held-out theorems reductio-labelled; f = 0 models solve 178–308; non-reductio "0.982–0.988" at 25M / 85M, 3.2M 0.957–0.971 | 679 (my predicate on the reference proofs); 178–308; 25M / 85M **0.980–0.992** (`m25B_s1` 0.9801, `m85B_s0` 0.9919, `m85B_s1` 0.9903); 3.2M 0.957–0.971 | reproduces except the quoted 25M / 85M range, which is 0.980–0.992 (the per-draw table has the right values) |
| 5 | "The 0.93 gate is unreachable / structurally unreachable for f = 0 models" | best case from these numbers ≈ (0.992 × 4,321 + 308) / 5,000 = 0.919 | supported as "not reached in 16 large draws and ≈ 0.92 at best"; "unreachable" is an inference, fine with that gloss. The 85M rows are labelled "gate missed (structural)" in `numbers.md`; `run4a.md` says it in the Setting paragraph. OK. |
| 6 | Pre-RL strict hits, rates, targets hit, pass@256 targets — all 19 draws | identical in every cell (hits 0 / 14 / 0; 1,872 / 830 / 14; 3 / 0 / 131; 37 / 49 / 6; 0 / 4 / 1,548; extras 13 / 2 / 60 / 8; pass@256 column identical) | reproduces |
| 7 | "0 hits on the 248 targets at 8–10 lines in 11.4M pre-RL samples" | 0 hits; the samples *on those 248 targets* are 19 × 248 × 2,000 = **9.42M** (11.4M is the total including 7-line targets); b10k adds 0 hits in 30,000 more on target 42 | reproduces; reword the denominator |
| 8 | EI acquired per round, ignition round, strata, trained rounds, frozen — 15 arms + 2 exploratory | identical in every cell | reproduces |
| 9 | "at most 1 eight-line target (`chain_neg`)" / `run4a.md`: "acquires at most one of 133 eight-line targets" | the one target is always `targets_reductio_req_42`, whose second premise `( ( ~ R ) > ( ~ R ) )` is unused; the proof is the 7-line `negimp_to_pos` shape + one mandatory PR line (pod-side `pruned` = 7). **Genuine 8-line acquisition: 0 of 132 in every arm at every size.** | reproduces as counted; should be reworded — the true statement is stronger than the one made |
| 10 | Transfer: 18–27 of the 27 seven-line theorems, 0 of 123 longer | 27 / 67 / 41 / 15 strata; igniting arms 18, 21, 25, 23, 20, 27, 27, 26 (extras 26, 24), all 7-line | reproduces |
| 11 | Solved-without-pattern 0 in all arms and coverage files | 0 | reproduces |
| 12 | Base-reachable@10⁴ and EI-only: 27/32, 30/45, 41/52, 34/40, 38/48, 49/53, 47/52, 39/52 | identical; `acq_*.jsonl` = my acquired sets; every acquired target has 10,000 fresh samples | reproduces |
| 13 | Run-5 row (quoted): s0 113 / 3·10⁶, EI 51, frozen 4, 6 / 51 reachable → 0.88; s1 0; s2 1 hit → EI 0; non-zero 1 / 3 by the first-2,000 rule | identical from `artifacts/r5/` with my code (s0 has 4 targets with a strict sample in the first 2,000; s2 none) | reproduces |
| 14 | Median non-zero rates ≈ 2·10⁻⁵ / 2·10⁻⁴ / 2·10⁻⁵ | 2.3e-5 (n = 1) / 2.2e-4 (n = 5) / 2.2e-5 (n = 9, two configs + extras pooled) | reproduces; pooled across configs |
| 15 | "EI-only fraction does not fall with size; it tracks base rate (> 10⁻³: 0.67–0.79; lower: 0.79–0.92)" | same split; Spearman ρ = −0.80 (p = 0.017, n = 8) | reproduces, and is the right reading. The executor does **not** claim a rise with size although the pre-registered reversal criterion is nominally met on cell A — correct restraint (n = 2, contradicted by 85M-B 0.75). |
| 16 | Low-rate draws: three ≤ 1.0·10⁻⁵ draws end at 0 / 300 with 0 trained rounds, expected hits 0.4–0.8; `m85_s2` continued: 0 through round 12, then 1 / 13 / 29 / 49 | same (0.38 / 0.51 / 0.77) | reproduces |
| 17 | ft-lr 3e-5 check: 1 / 9 / 28 / 33 / 40 / 46 / 49 / 51 (50 + 1) | same | reproduces (n = 1 draw; "no sensitivity" is a single-seed observation and is labelled exploratory) |
| 18 | Non-zero draws: 3.2M 1 / 3, 25M 5 / 6, 85M 9 / 10 | same counts; but 9 / 10 = B 2 / 3 (the configuration the executor's own rule makes the headline) + A 3 / 3 + **4 exploratory A-only draws added at 22:40 "to firm up the non-zero fraction"** after A was known to be 3 / 3 | counts reproduce; pooling is disclosed in `numbers.md` but the `run4a.md` table and Answer present only the pool — see Verdict |
| 19 | `run4a.md` Answer: '"Or nothing" survives to 85M but applies to ≈ 1 draw in 10 instead of 2 in 3' | zero-rate draws: 85M pre-registered 1 / 6 (B 1 / 3, A 0 / 3), with extras 1 / 10; 3.2M same-set 2 / 3, run 5 2 / 3, ignition study 7 / 11. Fisher exact: 1 / 10 vs 2 / 3 p = 0.11; 1 / 6 vs 2 / 3 p = 0.23; B vs A at 85M p = 0.30. **Outcome "nothing after 8 × 32": 3.2M 2 / 3, 25M 2 / 6, 85M 3 / 6 (p = 1.0).** | **differs in wording**: the difference is not established at these n, is config-dependent, and the practically relevant outcome (no ignition within budget) is as frequent at 85M as at 3.2M |
| 20 | "size did not move the wall" | 0 genuine 8–10-line acquisitions in 8 igniting arms (3.2M 1, 25M 4, 85M 3) + run 5; 0 base hits in 9.4M samples; 0 of 123 longer transfer theorems; one 85M arm through 16 rounds also 49 / 0 / 0 / 0 | supported for "8 rounds × 32, this pool, ≥ 2 seeds per new size". "Wall" is acceptable with that qualifier; nothing here tests more rounds after saturation (the saturated arms add 0 longer targets in their remaining 2–3 rounds). |
| 21 | P3 "held, non-vacuously at every size" | zero-rate draws at 85M: exactly one (`m85B_s0`) | reproduces; n = 1 at 85M should be said next to it |
| 22 | Spend 21.3 pod-hours ≈ $33.8, six pods | from the logged deletion times: 3.90 + 4.40 + 5.12 + 2.35 + 1.58 + 3.93 = 21.28 h × $1.59 = **$33.84**; creation times match `~/pods.log`; deletion times are log-only; `podls` empty; balance $127.78 at 01:12Z | reproduces (not derivable from repo files, as the executor says). Six pods instead of the pre-registered two–three: logged with reasons (co-tenancy OOMs, B cells); within the $50 ceiling and the $45 stop. |
| 23 | Gate 0: expectations before the run | pre-registration commit 17:55:56Z < first pod 17:56:44Z. Exploratory extras: expectations committed in `8ccd6cb` 21:43:46Z (first extras artefact 21:47:08Z) and `9663b4f` 22:32:27Z (first extra-draw Stage-1 log 23:19Z) — before their results; the log's clock labels ("21:47", "22:40") run a few minutes after the commits that contain them | holds |
| 24 | Misses reported as misses (P2 band, P4 three ways, P5 / E4) | my phase-1 scoring of P1–P7 matches the executor's line by line | holds — the expectations paragraph is accurate and complete |
| 25 | Retry rule "B replaces A if seed-0 held-out improves by > 0.01", fixed 19:02 | this threshold is **not** in the pre-registration (which says "the better configuration by held-out greedy of seed 0"); it was added mid-run but before any B result existed (rule committed `ae7f662` 18:54:56Z — the log labels it "19:02"; B seed-0 held-out files written 20:06Z and 20:55Z), and both rules select B at both sizes | no effect on any number; a logged mid-run amendment, acceptable |
| 26 | Stale-pull incident (22:31): 25M-A s0 / s2 coverage files overwritten and restored | all 27 coverage files complete (300 × 2,000 or acquired × 10,000); every per-theorem `n_ok` in the surviving pod logs equals the file (four pre-RL logs are partial because resumed runs overwrote them: `m3_s0/1/2`, `m25_s1` — no value mismatch in the parts that exist) | consistent |
| 27 | `mix_*.jsonl` "were not pulled" | one arm's mixes (`ei_m85_s0`) are on the VPS; I checked those (RL rows = target prompts only, all verify) | immaterial |

### One thing the write-up does not contain

**"Zero-rate" is a property of the draw *on this pool*, not absence of the shape from the model.** With my predicate on
the 5,000 greedy held-out outputs, 14 of 19 checkpoints — including the zero-rate draws `m25B_s1` and `m85B_s0` — emit
≥ 1 verified strict `AS ( ~ G ) … NEGI → DN` proof (0–11 per checkpoint; e.g. `heldout_4063` by `m85B_s0`). All are the
degenerate 5–6-line case where a premise is literally `( ~ ( ~ G ) )` and the contradiction is one `NEGE` with it, so
this is not a required-pool proof; but it shows every f = 0 base can already compose `NEGI` + `DN` into the strict
shape without having seen it, and that what separates zero-rate from non-zero draws is whether that composition
extends to a 7-line context (`IMPE` / `ANDI` before the `NEGE`). It also means "f = 0 base has never produced the
pattern" would be a wrong paraphrase of "zero-rate".

## §Verdict

**No hard-constraint violation. No quarantine.** `nd_verify` hash = `origin/main`; `TEST_RUN_DONE` untouched; no
evaluation or test file read by training code; cap 6 and generator-only provenance hold on all 155,000 training
records; splits disjoint by renaming class; pre-registration precedes the first pod; spend $33.8 < $50; pods deleted;
nothing sensitive in the public bucket. **Every number in `numbers.md` §Round 3 — Run 4a and in `run4a.md` reproduces
from the pulled files with independent code**, apart from one quoted range (row 4) and one denominator (row 7).

**What stands**

1. At 25M and 85M, as at 3.2M, every pre-RL strict-reductio sample (4,591 over 19 checkpoints) and every EI
   acquisition lies in the 52-target 7-line stratum of two schemata; EI saturates that stratum (39–52 seven-liners in
   8 rounds, ignition round 2–4) and acquires **no** genuine 8-, 9- or 10-line target at any size (≥ 2 igniting seeds at
   each new size, two Stage-1 configurations, two ft-lrs on one draw, 16 rounds on one draw). Frozen twins ≤ 7.
2. Zero-rate draws exist at every size including 85M (n = 1 there) and, never training, stay at 0 / 300.
3. The EI-only fraction does not fall with size (3.2M 0.84 / 0.88; 25M 0.67–0.85; 85M 0.75–0.92) — the brief's E4 and
   the executor's P5 are wrong — and it is governed by the draw's base rate (ρ = −0.80), being essentially
   1 − (base-reachable 7-line targets) / 52. It is instance-level spread inside one stratum, as the write-up says. No
   claim of a rise with size is made, and none would be supported.
4. No ≥ 10× rate increase per size step; per-draw rates span three orders of magnitude within each size and the size
   ranges overlap.
5. The 0.93 gate is missed at 85M in both configurations for the stated structural reason (679 reductio-labelled
   held-out theorems); non-reductio held-out greedy is 0.980–0.992 at both new sizes.

**What must be reworded**

- `run4a.md` Answer, "applies to ≈ 1 draw in 10 instead of 2 in 3" (also STATUS "less often", and the first bullet's
  "Bigger bases emit the pattern more often"). The 1 / 10 pools two Stage-1 configurations with four exploratory draws
  added, to the non-headline configuration, after it was known to be 3 / 3; in the configuration the executor's rule
  designates as headline the fraction is 1 / 3 at both 25M and 85M against 2 / 3 at 3.2M (n = 3 each). Fisher p = 0.11
  (pooled) / 0.23 (pre-registered draws). Suggested: "zero-rate draws were 2 / 3 at 3.2M, 1 / 6 at 25M and 1 / 6 at 85M
  (1 / 10 with four exploratory draws; B 1 / 3 vs A 0 / 7, so it depends on the Stage-1 recipe); the direction favours
  fewer zero-rate draws at scale but is not established. Counting outcomes instead — no accepted proof in 8 × 32 —
  'nothing' happened in 2 / 3, 2 / 6 and 3 / 6 draws."
- "'Or nothing' survives": say what the data bound. A 0-in-600k draw has rate < 5·10⁻⁶ (95 %), for which 76,800 EI
  attempts give < 0.4 expected hits; three *non-zero* draws also got nothing, and one ignited in rounds 13–16. The
  supported clause is "nothing within the attempt budget unless the base emits the shape on the pool at ≳ 2·10⁻⁵";
  no zero-rate draw has been run long enough to call it "never".
- "at most one of 133 eight-line targets": replace by "0 genuine 8-line targets (the single one counted is a 7-line
  proof of a target with an unused premise, `targets_reductio_req_42`)". Likewise P4's scoring.
- `numbers.md`: non-reductio held-out range 0.982–0.988 → 0.980–0.992; "0 hits … in 11.4M" → 9.4M samples on the 248
  longer targets.
- "no sensitivity" to ft-lr and "size did not move the wall" should carry their n (one draw; 8 rounds × 32).

**Not supported**

- Any quantitative size trend in the non-zero fraction or the median rate (25M median is 10× the 85M median; the
  ordering of medians is 3.2M ≈ 85M < 25M).
- Nothing else: the write-up does not overclaim on EI-only, ignition, or the wall.

**Next measurement that would settle what is open**

1. *Is "nothing" only a budget effect?* Take the four zero-rate checkpoints (in the bucket) and the two remaining
   low-rate ones (`m25B_s0`, `m85B_s1`) and run base sampling on the **52 seven-line targets only** to 10⁵–10⁶ samples
   per target (52 × 10⁵ = 5.2M samples ≈ 1 A100-hour at 85M). If every "zero-rate" draw has a non-zero rate at 10⁻⁷–10⁻⁶,
   clause (2) becomes a statement about attempts × rate, and the predicted ignition round follows from the rate; if
   some draw stays at 0 in 5·10⁶, "or nothing" has a real instance. Pre-register the expected first-hit round from the
   measured rate and test it on one such draw with k = 256.
2. *Is the 7-line wall a rounds effect?* Continue two saturated arms (one 25M, one 85M; round-8 checkpoints are in the
   bucket) to round 32 with the 52 saturated targets removed from sampling (so all k go to the 248 longer targets),
   frozen control at equal attempts. Either a genuine 8-line acquisition appears (then measure its base reachability),
   or the wall statement gains a 4× longer horizon.
3. *Recipe vs size for the non-zero fraction:* if the fraction matters to the SPAR answer, it needs ≈ 10 draws per
   cell in one fixed configuration at each size (coverage only, ≈ $1 per 85M draw); the present A / B split (0 / 7 vs
   1 / 3 zero-rate at 85M) cannot separate recipe from noise.
