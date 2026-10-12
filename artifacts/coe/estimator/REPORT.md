# Phase 0.1: the known-proof estimator at small p

(Analysis by a sub-agent of the executor, 2026-10-12; saved by the executor. Script `coe/coe_estimator.py`.)

**Model, every number:** best-cap12 pend s0 / s1 / s2 = `trajectory/ckpts/tj/stage1_best12_s{S}_b1200.pt` (9.56 M
ALiBiGPT, lean_staten, from scratch on K12), T 0.8, Lean alone. **Estimate** E = Σ_F π_pend(F), teacher-forced over 33
name bases (capability-defs `bracket.json` LB08, reproduced exactly). **p̂** = c / n over x0–x4 + J2 + J9.
**Source:** `coe/coe_estimator.py` → `per_theorem.json` (330 seed × theorem rows), `summary.json`, `estimator.txt`;
`--selftest` checks the bound arithmetic and runs a positive control (807 / 807 of seed 0's J2 stage-A and calibration
proofs found among the J1 + stage-2 targets) and a negative one (0 matches when proofs are shifted to another theorem).
Inputs are capability-defs J1 / J2 / J9 files: all 260 are local and size-identical to the bucket, so nothing was
downloaded.

## Verdict

- **E ≥ 10⁻⁴: trustworthy in aggregate.** Observed / predicted base successes are 1.11 [1.10, 1.13] for E ≥ 10⁻³
  and 1.10 [0.99, 1.22] for E between 10⁻⁴ and 10⁻³. Per theorem, E / p̂ has a 10–90 % range of 0.76–1.09
  (p̂ ≥ 10⁻³) and 0.16–1.75 (p̂ between 10⁻⁴ and 10⁻³).
- **Below E ≈ 10⁻⁴ it is a lower bound that is too low:** by 2.1× in the 10⁻⁵–10⁻⁴ bin and 3.5–3.7× below 10⁻⁵.
- **It is almost never too high.** It is significantly above the sampled rate (Poisson p < 0.025) on 1 of 330
  theorems and above the 95 % Clopper–Pearson (CP) upper bound on 1 of 196.
- **For this run:** "within reach if E ≥ 2 / K" never falsely certifies reach. It loses power for p < 10⁻⁴, and at
  K ≈ 2 · 10⁴ the threshold 2 / K sits right at that edge.

**Table 1 — E / p̂ by p̂ bin (pend s0–s2; theorems with c ≥ 1).** Using the known set alone (dropping pend's own J2
finds) moves every median by ≤ 0.02.

| p̂ bin | n (s0/s1/s2) | median (s0/s1/s2) | P10–P90 | inside CP95 | above CP hi |
|---|---|---|---|---:|---:|
| ≥ 10⁻³ | 106 (34/33/39) | 0.94 (0.96/0.94/0.92) | 0.76–1.09 | 0.73 | 0.01 |
| 10⁻⁴–10⁻³ | 52 (19/16/17) | 0.88 (1.00/0.72/0.74) | 0.16–1.75 | 0.87 | 0 |
| 10⁻⁵–10⁻⁴ | 36 (11/10/15) | 0.45 (0.45/0.45/0.36) | 0.07–1.43 | 0.94 | 0 |
| < 10⁻⁵ | 2 (0/1/1) | s1 0.03, s2 0.70 | — | 2/2 | 0 |

Binning by p̂ conditions on c ≥ 1. Table 2 removes that selection: it bins by E_known, which does not depend on the
large-k outcomes, and it includes the 0-success hard theorems. Its columns factor exactly:
E / p = (μ / K) × (K / N), where μ = n_L · E is the predicted number of successes, K the successes whose proof was
already known, and N all successes.

**Table 2 — selection-free (pend s0–s2; all 240 hard + 90 calibration theorems).**

| E_known bin | theorems | observed / predicted [95 %] | coverage K / N | μ / K |
|---|---:|---|---|---|
| ≥ 10⁻³ | 104 | 25,431 / 22,834 = 1.11 [1.10, 1.13] | [0.09, 0.93]; π-allocated 0.92 | [0.96, 10.1] |
| 10⁻⁴–10⁻³ | 44 | 361 / 328 = 1.10 [0.99, 1.22] | [0.62, 0.88] | [1.03, 1.46] |
| 10⁻⁵–10⁻⁴ | 29 | 75 / 35.5 = 2.11 [1.66, 2.64] | [0.56, 0.60] | [0.79, 0.85] |
| 10⁻⁶–10⁻⁵ | 29 | 19 / 5.1 = 3.71 [2.24, 5.80] | 0.79 (15 / 19) | 0.34 |
| < 10⁻⁶ | 124 | 4 / 1.2 = 3.45 [0.94, 8.83] | 0.50 (2 / 4) | 0.58 |

## The unseen share (Task 3)

The quantity of interest is U = 1 − Σ_{F∈𝓕} π(F) / p, where 𝓕 is the known set built without the base's large-k
samples (J1: every read of every model, plus the reference proofs). Since 𝓕 is independent of J2 / J9, each base
success falls in 𝓕 with probability 1 − U, so K ~ Bin(N, 1 − U). Û = 1 − K / N then has an exact CP interval.
Good–Turing is not needed for an independent set:

- M̂₀ = f₁ / N is the missing mass of the base's own seen proofs, so it pairs with the sum over those proofs.
- The bracket's F (𝓕 plus pend's own finds) pairs with M̂₀ᵤ = f₁ᵤ / N, where f₁ᵤ counts the singletons outside 𝓕.

J2 / J9 rows keep only the distinct proofs of each chunk, so K and f₁ are given as exact bounds over every possible
allocation of the duplicates. The pre-registered rule (n_ok ≤ distinct + 1 in every chunk) recovers multiplicities
for 57 / 106 hard theorems and 0 / 90 calibration theorems.

**Table 3 — pend s0–s2, pooled by p̂ bin.**

| p̂ bin | N | unseen 1 − C [CP95] | M̂₀ (own) | M̂₀ᵤ | GT-corrected E / p̂, median |
|---|---:|---|---|---|---|
| ≥ 10⁻³ | 25,481 | [0.07, 0.91]; π-allocated 0.08 | [0.00, 0.13] | [0.00, 0.07] | 0.94–0.99 |
| 10⁻⁴–10⁻³ | 362 | [0.14, 0.30] [0.11, 0.35] | [0.23, 0.39] | [0.08, 0.14] | 1.08 |
| 10⁻⁵–10⁻⁴ | 45 | 0.22 [0.11, 0.37] | [0.78, 0.80] | 0.18 | 0.52 |
| < 10⁻⁵ | 2 | 0 [0, 0.84] | 1.00 | 0 | 0.36 |

On the recoverable subset alone, M̂₀ at 10⁻⁴–10⁻³ is 0.76, against [0.23, 0.39] on all theorems. That subset is
selected for few duplicates, so it is biased high and should not be used on its own.

## What limits it

1. **Teacher forcing under-predicts how often low-π proofs are sampled.** Taking the exactly scored known proofs of
   the hard theorems: proofs with π between 10⁻⁶ and 10⁻⁵ were sampled ≥ 46 times against 35.5 expected; proofs with
   π between 10⁻⁷ and 10⁻⁶ ≥ 13 times against 6.2 (≥ 2.1×, Poisson lower bound 1.13). The likely cause is the one in
   the capability-defs log (2026-10-05 09:01): the scorer conditions on the canonical defining name, while the sampler
   conditions on the name it sampled, which the environment then renames. Below 10⁻⁴ the shortfall has two parts:
   at E 10⁻⁵–10⁻⁴ it is mostly unseen proofs (coverage 0.58, μ / K 0.82); at 10⁻⁶–10⁻⁵ it is mostly calibration
   (μ / K 0.34, coverage 0.79).
2. Coverage at p̂ ≥ 10⁻³ cannot be identified without a model. The π-allocated estimate (0.92) relies on π itself.
   This run's own large-k reads keep multiplicities and will fix this.
3. Few successes at small p: 45 base successes in the 10⁻⁵–10⁻⁴ bin and 2 below 10⁻⁵.
4. **Population.** 105 / 106 of the hard theorems with base successes are RL-solved. Among base proofs that were
   already known, 218 / 256 came from the same seed's RL checkpoints and 29 only from other seeds or cap-6 models.
   The knockout arm's known sets will come from different models.
5. Stage B and J9 sampled only after 0 successes, and J9 stopped at the first success, so the CP intervals are
   approximate. The Table 2 sums stay unbiased (Wald's identity).
6. **Not limits.** Stage-1 bound terms carry ≤ 1.2 % of any estimate (median ≤ 0.03 %). `normalize.norm` leaves every
   one of these proofs unchanged.

## Pre-registered expectations (scoring rules in `summary.json`)

| expectation | result | score |
|---|---|---|
| median E / p̂ in [0.7, 1.2] for p̂ ≥ 10⁻³ | 0.96 / 0.94 / 0.92 | **hit** |
| 10–90 % range wider than [0.3, 3] for p̂ < 10⁻⁴ | 0.06–1.39 (n 38): 23× wide, but P90 < 3 | **hit** on width; the spread runs one way, downward |
| coverage ≥ 0.6 for p̂ ≥ 10⁻⁴ | pooled [0.10, 0.93]; 10⁻⁴–10⁻³ alone [0.70, 0.86] | **not measurable** pooled (calibration multiplicities); hit on 10⁻⁴–10⁻³ |
| coverage undetermined (≤ 3 successes) below 10⁻⁵ | 2 theorems with 1 success each, both known; CP [0.16, 1] | **hit** |
| Good–Turing on this run's large-k reads | none exist yet | **not measurable** |
