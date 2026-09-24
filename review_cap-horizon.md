# Review — run `cap-horizon` (proposal 11 run 1: is the proof-length horizon a property of the training cap?)

Reviewer: agent:claude, independent session, started 2026-09-24 23:00 UTC.
Phase 1 was done in `~/review/cap-horizon` — the run's repository with the executor's write-ups
removed (`run*.md`, `numbers.md`, `STATUS*.md`, `campaign.md`, `followup.md`, `ignition.md`,
`phase*.md`, `*_summary*.md`). Phase-1 code is mine: `review/cap-horizon-recount/rvlib.py` (own
formula parser, own proof-line parser, own dependency pruner, own start-index normaliser, own box-depth
counter, own renaming-class key, own term-size counter) and `rv_sets.py`, `rv_cov.py`, `rv_ladder.py`,
`rv_rounds.py`, `rv_pool.py`, `rv_patterns.py`, `rv_termsize.py`, `rv_ckpt.py`, `rv_leansample.py`,
`rv_axioms.py`. None of the run's analysis code (`kh_analysis.py`, `kh_assemble.py`, `kh_size.py`,
`kh_readme.py`, `patterns.py`, `prune.py`, `coverage_lean.py`, `ladder_analysis.py`, `normalize.py`)
was imported. `nd_verify` (unmodified) and `nd2lean.py --check` (unmodified) are used where the
protocol requires the checkers themselves. All scripts and their JSON outputs are committed under
`review/cap-horizon-recount/`.

**Disclosure.** My pruner and my renaming key were sanity-checked once against `prune.pruned_length`
and against the pool files' stored `key` field on 50 oracle proofs before use; they agreed, and every
number below is then computed by my code from the raw artefacts. While orienting myself I read the
first screen of `artifacts/kh/summary.json`, which showed K6's held-out row (an inherited value that
the pre-registration already states); nothing else from any summary was read before this §Recount was
written and committed.

---

## §Recount

### 0. Hard constraints

| constraint | check | result |
|---|---|---|
| `nd_verify` unmodified | `git rev-parse HEAD:nd_verify` vs `origin/main:nd_verify` | **identical tree** `9437bb72…`; blobs `dfa3bc3f…` (`__init__.py`), `1cfed53b…` (`verify.py`); worktree clean |
| `artifacts/TEST_RUN_DONE` unchanged | blob vs `origin/main` | **identical** `1d5cf064…` — one test-file run on record, 2026-09-15T07:38:07Z; no new write this run |
| at most one test-file run | no test pool in any `pod/kh/jobs.py` command, no new `TEST_RUN_DONE` | **ok** |
| no repository code modified | `git diff --stat origin/dan_ds-composition..HEAD -- '*.py' nd_verify` | **only new files** (`kh_*.py`, `pod/kh/*`), 1,121 insertions, 0 deletions. `train.py`, `sample.py`, `prune.py`, `coverage_lean.py`, `ladder_ei.py`, `nd2lean.py`, `lean_gate.py`, `patterns.py` untouched |
| evaluation file read in training code | `grep` on `train.py`, `ladder_ei.py`, `grpo.py` | `train.py --heldout data/p2/heldout.jsonl` **is** read, but only under `torch.no_grad()` to print a validation-loss line (`train.py:118-123`); no gradient, no early stopping, no checkpoint selection. `ladder_ei.py:189-193` builds `eval_keys` from transfer ∪ held-out ∪ targets ∪ `validation_36` ∪ reserve and excludes those renaming classes from the retain/self-training mix (`:255`). **Not a leak**; flagged so "no evaluation file is read" is not used unqualified |
| ladder pools byte-identical to ladder-A's | `git hash-object` | `data/ladder/transfer.jsonl` = `e0524d0a84d7163feb4815910e47e09648f622b2`, `data/ladder/rl_targets.jsonl` = `69233bcaa2ea80038297bba6e8864cb8b1f00b13` — **both as pre-registered** |
| gate 0 (expectations written first) | `preregistration/cap-horizon.md` committed `2091f78` **2026-09-24T16:07:35Z**; budget registered 15:59:20Z; the four pods' ledger start ≈ 16:26Z (22:50 deletion − 6.40 h) | **before the first pod**, by ≈ 19 min |
| cap respected in the training data | my own re-parse of all 682,000 new training records | **0 records over cap** in every arm |
| pods deleted | `podls` | only `nf-1`, `nf-2` (sibling `noise-floor`); **no `kh-*` pod alive** |
| spend | `podbudget cap-horizon`, `~/podhours.log` | 4 pods × A40, 25.55 h, **$12.52** of $22 / 44 h. The GPU class is recorded correctly (`NVIDIA A40`, $0.49/h in the rate table) — the correction the pre-registration promised was applied |
| bucket | `hf buckets ls …/cap-horizon/` | `artifacts/`, `ckpts/`, `data/` present |
| RunPod balance | `rpbalance` | $158.12, above the $50 floor |

**No hard-constraint violation. No quarantine.**

### 1. The four new training sets — my own re-parse of every record

Per-length counts are **pruned** length, from my own dependency closure.

| quantity | K8add (cap 8) | K10 (cap 10) | K12 (cap 12) | K14 (cap 14) |
|---|---:|---:|---:|---:|
| records | **217,000** | 155,000 | 155,000 | 155,000 |
| per-length | 31,000 × 2–8 | 17,223 × 2–3, 17,222 × 4–10 | 14,091 × 2–11, 14,090 × 12 | 11,924 × 2, 11,923 × 3–14 |
| records over cap | 0 | 0 | 0 | 0 |
| depth-3 (pruned / written) | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| distinct renaming classes | 217,000 | 155,000 | 155,000 | 155,000 |
| distinct rendered texts | 217,000 | 155,000 | 155,000 | 155,000 |
| overlap with the 11 evaluation pools | **0** | **0** | **0** | **0** |
| records byte-identical to K6's set | **155,000** (all of it) | 86,112 | 70,455 | 59,616 |
| mean / median / max term size | 29.04 / 26 / 127 | 32.33 / 29 / 132 | 35.91 / 32 / 178 | 39.50 / 35 / 226 |

Every figure reproduces `data/kh/README.md` exactly, including the per-length mean/max term sizes
and the per-length reductio / derived-`ORE` shares (my own predicates; `out_patterns.json` —
e.g. K14 length 14: 21.09 % / 49.56 %, K10 overall 8.36 % / 9.91 %).

The provenance claim is **stronger than the brief asked and it holds**: the byte-identity counts are
exactly what pure subsetting of K6's 155,000 records predicts (K10 = 155,000 − 4 × 17,222; K12 =
155,000 − 84,545; K14 = 155,000 − 8 × 11,923), so no short-bin record in any arm is a re-draw.

Exclusion set: 14,026 renaming classes over the eleven pools — my own count, same as the README.
The long pool `data/kh/pool_long_kh.jsonl`: **518,843 records, 518,843 distinct renaming classes**,
pruned lengths 7–14 only, per-length `{7: 84048, 8: 85002, 9: 57414, 10: 57697, 11: 58317, 12: 58552,
13: 58803, 14: 59010}` — identical to the merge report.

**Not in the README, and I would want it said:** at a fixed 6,000 steps × batch 128 = 768,000 samples,
K8add sees **3.54 epochs** of its 217,000 records against **4.95 epochs** for every 155,000-record arm.
K8add's set-size difference is therefore also a training-exposure difference, not only a composition one.

### 2. Held-out greedy — `data/p2/heldout.jsonl`, 5,000, k = 1, T = 0

**This pool is the cap-6 distribution; every arm above cap 6 is measured out of distribution on it.**
Raw per-sample generations were not retained, so this is the one quantity I cannot re-derive from the
artefacts (no GPU / no `torch` on the VPS); I checked it for internal consistency instead — in every
file `solved` equals the sum over `by_len` and equals the Lean gate's `both_ok`.

| arm (from-scratch, 3,214,336 params, `lean_seq`) | s0 | s1 | max pruned length with ≥ 5 proofs |
|---|---:|---:|---:|
| K6 `ckpts/lf/stage1_a1_seq_s{0,1}.pt` | 0.9088 | 0.8962 | 6 / 6 |
| K8flat `ckpts/dsc/stage1_a3_s{0,1}.pt` | 0.9508 | 0.9536 | 9 / 8 |
| K8add `ckpts/kh/stage1_k8add_s{0,1}.pt` | 0.9384 | 0.9486 | 8 / 8 |
| K10 `ckpts/kh/stage1_k10_s{0,1}.pt` | 0.9464 | 0.9394 | 10 / 10 |
| K12 `ckpts/kh/stage1_k12_s{0,1}.pt` | 0.9428 | 0.9122 | 12 / 12 |
| K14 `ckpts/kh/stage1_k14_s{0,1}.pt` | 0.8870 | 0.9054 | 12 / 12 |

All eight new checkpoints read out (without `torch`, from the zip's pickle) as **3,214,336 parameters,
4 layers, d 256, 8 heads, `lean_seq`**, and their `train.py` command lines in
`artifacts/kh/logs/stage1_*.log` carry the right `--data`, `--cap` and `--seed` for every arm.

### 3. Coverage pass@2,000 (T 0.8, seed 0, batch 1024, `max_new` 400) on `targets_reductio_req` (300)

Acceptance re-derived by me as **nd_verify (re-run here) ∧ Lean**; distinct proofs deduped on the
**start-index-normalised** proof string; lengths from my own pruner.

| arm | solved /300 (s0 / s1) | max **pruned** accepted length | accepted ≥ 8 / ≥ 10 / ≥ 12 (pruned) | ≥ 8 (written) | mean term size |
|---|---|---|---|---|---|
| K6 (cap 6) | 28 / 26 | 7 / 7 | 0/0/0 · 0/0/0 | 0 / 0 | 28.2 / 26.5 |
| K8flat (cap 8) | 54 / 72 | 10 / 8 | 28/2/0 · 32/0/0 | 29 / 33 | 32.9 / 32.0 |
| K8add (cap 8, **217k set**) | 63 / **24** | 8 / 8 | 21/0/0 · 1/0/0 | 25 / 2 | 31.9 / 27.0 |
| K10 (cap 10) | 70 / 87 | 10 / 11 | 33/2/0 · 43/4/0 | 36 / 48 | 31.1 / 32.3 |
| K12 (cap 12) | 73 / 86 | **13** / 12 | 50/16/7 · 77/39/23 | 55 / 86 | 33.3 / 36.5 |
| K14 (cap 14) | 84 / 54 | **14** / **14** | 78/33/19 · 36/18/7 | 108 / 41 | 34.8 / 34.5 |

Per-stratum (`min_lines_ub` 7 / 8 / 9 / 10, pool sizes 52 / 133 / 82 / 33): **no arm solves a single
target in the 10-stratum, and only K12 solves any in the 9-stratum (2 on s0, 1 on s1).** All growth is
in the 7- and 8-strata.

The `≥ 8 lines` figure the pre-registration quotes for K8flat (29 / 33) is the **written** count; the
**pruned** count is 28 / 32. Both are given above so the comparison is like-for-like.

`r3_1/depth3_req` (300), same settings, solved and max pruned accepted length:
K6 170 / 108 (9, 8) · K8flat 276 / 289 (11, 13) · K8add 258 / 270 (12, 12) · K10 207 / 282 (13, 14) ·
K12 252 / 231 (15, 13) · K14 238 / 266 (16, 16). Full histograms in `out_cov.json`.

**The `max_new` ceiling is not binding.** The diagnostic re-run at `max_new` 768 (`covd_*`) produces an
**identical accepted set** to the 400-token run for all four new arms and for K8flat — my recount gives
the same solved count, the same distinct proofs, the same max length and the same mean term size; the
only change is 21 fewer parse failures on K14 (samples that had been truncated now parse, and none is
accepted). The frontier is not truncation-bound.

**A built-in reproducibility check passes.** `cov8f_K8flat_s0_redreq`, a fresh re-run of K8flat seed 0
on this run's pod, reproduces the inherited `ds-composition` file exactly: 54 solved, 58 distinct
accepted proofs, max pruned 10, ≥8 = 28, mean term size 32.90.

### 4. Ladder — rung T1 and frozen at equal attempts, 8 rounds × k 32, seed 0

`args.json` for all twelve ladders: **k 32, batch 512, `max_new` 512, T 0.8, 8 rounds, seed 0**, frozen
arms `no_train: true`. Attempts are equal. `L*` = max L with ≥ 5 theorems solved at `L_true ≥ L`
(the pre-registration's definition), recomputed by me from the cumulative `found_transfer_8.jsonl`
records with `L_true` joined from the pool file.

| arm | frozen solved /2285 | frozen `L*` | T1 solved /2285 | T1 `L*` | T1 solved at `L_true` ≥ 12 / ≥ 13 / ≥ 14 | max pruned accepted (frozen → T1) |
|---|---:|---:|---:|---:|---|---|
| K6 | 158 | **9** | 856 | **12** | 5 / 0 / 0 | 10 → 12 |
| K8flat | 976 | **11** | 1,438 | **12** | 11 / 1 / 0 | 13 → 15 |
| K8add | 857 | **10** | 1,428 | **12** | 9 / 1 / 0 | 14 → 16 |
| K10 | 743 | **11** | 1,554 | **12** | 10 / 0 / 0 | 15 → 16 |
| K12 | 1,088 | **12** | 1,685 | **12** | 15 / 3 / 1 | 17 → 18 |
| K14 | 1,140 | **12** | 1,655 | **12** | 17 / 4 / 1 | 19 → 20 |

`L*` by round (cumulative, my own recount from each proof's `round` field):

- frozen — K6 9,9,9,9,9,9,9,9 · K8add 10,10,10,10,10,10,10,10 · K10 10,10,11,11,11,11,11,11 ·
  K12 11,11,11,11,12,12,12,12 · K14 11,12,12,12,12,12,12,12 · K8flat 10,11,11,11,11,11,11,11
- T1 — K6 9,10,10,10,11,11,11,**12** · K8add 10,11,11,12,12,12,12,12 · K10 10,12,… · K12 11,12,… ·
  K14 11,12,… · K8flat 10,11,12,…

**Three facts the raw files establish and that I would put at the front of any write-up.**

1. **T1 `L*` = 12 for every arm, including cap 6.** It is not an instrument for this question: it is at
   its ceiling at cap 6 by round 8, so no arm can advance on it. The pre-registration anticipated
   censoring at 14 but not that the T1 readout saturates at 12 for the control as well.
2. **Frozen `L*` does walk with the cap — 9, 10/11, 11, 12, 12 — and compresses.** The offset the
   pre-registration predicted (`cap + 3`, censored at 14) is not what the data show: the achieved offset
   is +3 at cap 6, +3/+2 at cap 8, +1 at cap 10, 0 at cap 12, −2 at cap 14. There is a monotone
   non-decreasing walk, but **no stable offset**.
3. **The uncensored frontier — the longest accepted proof written — keeps moving with no sign of a
   plateau**, on both the frozen and the T1 model and on both evaluation pools: ladder transfer
   frozen 10 → 13/14 → 15 → 17 → 19 and T1 12 → 15/16 → 16 → 18 → 20 across caps 6 → 14;
   `redreq` max pruned 7 → 8/10 → 10-11 → 12-13 → 14; `d3req` 8-9 → 11-13 → 12 → 13-14 → 13-15 → 16.
   On `redreq` at cap 14 the longest accepted proof is exactly 14 — the cap — and on the ladder the
   models write accepted proofs **above** their training cap (K14: 20 pruned lines).

`L_true ≥ 13` is solved for the first time in this family of runs: K12 3 theorems, K14 4 (T1), and
K14 1 theorem at `L_true = 14`. Five would have been needed for `L* = 13`; the pool holds 23
theorems at `L_true ≥ 13`, so this is a near miss on a measurable quantity, not a censoring artefact.

Term size beside the line counts (distinct accepted ladder-transfer proofs, mean / max):
K6 61.2 / 131 (T1), K8flat 58.2 / 136, K8add 59.8 / 139, K10 55.9 / 149, K12 55.5 / 159, K14 57.9 / 154.
Mean term size is flat across arms while mean pruned length rises (8.6 → 9.5): the longer proofs are
**not** proportionally larger in formula nodes.

### 5. Lean is the checker of record

- **nd_verify re-run by me on 433,223 counted records** — every proof in every coverage file (14,361)
  and every record of every ladder `found_*`/`found_transfer_*` pool (418,862). **Zero rejects.**
- **Lean re-check through the unmodified `nd2lean.py --check` on 787 counted proofs, ≥ 125 per arm**
  (the 40 longest counted coverage proofs of the arm, 40 random further coverage proofs, every counted
  proof of an `L_true ≥ 12` ladder theorem, 40 random other ladder proofs):
  K6 125, K8flat 131, K8add 129, K10 130, K12 135, K14 137 — **nd_ok ∧ lean_ok on all 787,
  0 nd_ok&lean_rej, 0 nd_rej&lean_ok.**
- **Proposal 9's `lean_check` does not exist in this repository**, so I implemented its two checks
  myself (`rv_axioms.py`): every identifier in the generated Lean term is on an allowlist
  (`Classical.byContradiction`, `False.elim`, `Or.elim`, `Or.inl`, `Or.inr`, `.1`/`.2`, generated
  binder names, `P Q R S`, `False`) — **no identifier off it in any of the 787** — and `#print axioms`
  on each theorem — **787/787 within `{propext, Classical.choice, Quot.sound}`, no `sorryAx`, no
  `sorry` in any source.**
- **The run's own record of the checker (`artifacts/kh/record_*.json`) covers every counted proof of
  every arm** — e.g. K10: 35,300 + 12,726 + 7,683 + 2,018 ladder records and 2,227 coverage proofs,
  all `nd_ok&lean_ok`, zero disagreement. My sample is a subset and agrees.
- **456 in-loop disagreements exist and they are all in the safe direction.** Across the eleven
  `gate_*.jsonl` logs, 4,479,047 both-accepted checks, **`nd_ok&lean_rej` = 0** and
  `nd_rej&lean_ok` = 456. I re-ran nd_verify on all 456 and reproduce the stored verdict on every one:
  77 "premise block does not match declared premises", 221 `BOTE`, 76 `IMPI`, 23 `NEGE`, rest similar —
  i.e. the known `nd2lean` looseness (¬A translated as A → False, premises re-stated by position) that
  the pre-registration says is queued for a fix after this run. Because acceptance is Lean ∧ nd_verify,
  **no counted proof anywhere in this run rests on that looseness**, and Lean never rejected a proof
  nd_verify accepted.

### 6. The pre-registered expectations, scored against my values

Seed 0 / seed 1 where there are two. "in band" is judged on each seed separately.

| quantity | band | K8add | K10 | K12 | K14 |
|---|---|---|---|---|---|
| max accepted `redreq` pruned length | 9–10 / 11–13 / 13–15 / 14–17 | 8 / 8 **miss (low)** | 10 / 11 **miss (low)** | 13 / 12 **s0 hit, s1 low** | 14 / 14 **hit** |
| accepted `redreq` ≥ 8 lines (written) | 20–45 / 30–70 / 30–70 / 25–70 | 25 / 2 **s0 hit, s1 far low** | 36 / 48 **hit** | 55 / 86 **s0 hit, s1 high** | 108 / 41 **s0 high, s1 hit** |
| `redreq` solved of 300 | 45–80 / 60–110 / 60–110 / 55–110 | 63 / 24 **s0 hit, s1 far low** | 70 / 87 **hit** | 73 / 86 **hit** | 84 / 54 **s0 hit, s1 just low** |
| frozen ladder `L*` | 10–11 / 12–13 / 13–14 / 13–14 | 10 **hit** | 11 **miss** | 12 **miss** | 12 **miss** |
| T1 transfer `L*` | 12–13 / 13–14 / 14 / 14 | 12 **hit** | 12 **miss** | 12 **miss** | 12 **miss** |
| held-out greedy vs K8flat | ≥ K8flat / −3…+3 pp / −5…+3 pp / −8…+3 pp | −1.2 / −0.5 pp **miss** | −0.4 / −1.4 pp **hit** | −0.8 / −4.1 pp **hit** | −6.4 / −4.8 pp **hit** |

**Predicted relationship, scored.** `c_frozen = +3` (frozen `L*` = min(cap + 3, 14)) → predicted 11, 13,
14, 14; observed **10, 11, 12, 12**. `c_maxlen = +2` (max accepted `redreq` pruned length = cap + 2) →
predicted 10, 12, 14, 16; observed **8, 10–11, 12–13, 14**. Both offsets are **wrong and wrong in the
same direction**: they are too generous, and the gap widens with the cap. The form of the result is
**a monotone but sub-linear walk**, not "a monotone walk with a stable offset" and not "a plateau" —
on the frozen ladder each +2 of cap buys ≈ +0.75 of `L*`, while on the uncensored max-accepted-length
readout each +2 of cap buys ≈ +2 (ladder transfer) or ≈ +2 (`redreq`), i.e. the *frontier* tracks the
cap closely and the *`L*` statistic* saturates because it is a 5-theorem quantile on a pool whose mass
above `L_true` 12 is 125 theorems of 2,285.

**Falsifier 1 (the cap account is dead) is NOT triggered.** It required K10 **and** K12 to have T1
`L*` ≤ 12 *and* frozen `L*` ≤ 11 *and* max accepted `redreq` length ≤ 10. K12 fails two of the three
conditions (frozen `L*` = 12, max `redreq` length 13). K10 alone satisfies all three.

**Falsifier 2 (composition below the cap is irrelevant) cannot be decided.** K8add vs K8flat, `redreq`
solved 63 / 24 against 54 / 72 and frozen ladder solved 857 against 976. The sibling `noise-floor` run
is still executing (`nf-1`, `nf-2` were the only live pods at 23:00 UTC), so its resolvable-difference
table is not available. Note that the **within-arm seed spread of K8add on `redreq` (63 vs 24) is
larger than any between-arm difference at cap 8**, so at n = 2 this comparison is not resolvable from
this run's own data either.

### 7. What I could not re-derive

- Held-out greedy rates (no retained generations, no GPU here) — internal consistency only.
- The per-arm **fraction of samples that hit `max_new`**, which the pre-registration promised to report:
  the coverage gate files record `parse_fail` but not a truncation breakdown, so the only evidence in
  the artefacts is the `covd_*` (768-token) comparison, which is strong but indirect.
- `noise-floor`'s error bar, which the pre-registration makes this run's numbers conditional on.
