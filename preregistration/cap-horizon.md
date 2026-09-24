---
run_id: cap-horizon
written_on: 2026-09-24
written_by: agent:claude
role: executor
status: pre-registered
---

# Pre-registration — `cap-horizon`: is the proof-length horizon a property of the training cap?

Written before the first pod. Budget **$22 / 44 pod-hours** (`podbudget cap-horizon --set 44 22`),
hard stop 30 h. Proposal 11 (`~/nd-rl/docs/proposals/2026-09-24-length-horizon-and-noise-floor.md`).
Sibling run `noise-floor` measures the error bar these claims must be read against; **no difference
below its resolvable-difference table is called real**, and if its table is not available at
write-up time this run says so and calls no small difference real.

## Question

Holding the generator, the `lean_seq` rendering, the 3.2 M-parameter from-scratch model
(4 layers, d 256, 8 heads, 3,214,336 parameters), the 6,000-step Stage-1 schedule and the
depth-3 f = 0 filter fixed, does raising the **training cap** move the proof-length horizon —
the maximum pruned length of accepted proof the model writes, the transfer `L*` after ladder
rung T1, and the frozen `L*` at equal attempts — and does it keep moving, or plateau?

Cap 6 is the **take-home's** constraint, not this project's. **Every arm above cap 6 is outside
the take-home rule, is labelled "cap N" in every row, and none is proposed for adoption as a
take-home submission.**

## Arms

Two inherited, not retrained (checkpoints, coverage and ladder outputs pulled from
`hf://buckets/dan-pandori/nd-rl/{lean-format,ds-composition}/`):

| arm | cap | records | per-length shape | provenance |
|---|---|---|---|---|
| **K6** | 6 | 155,000 | flat 31,000 × lengths 2–6 | `ds-composition` C0 = `lean-format`'s a1 set; ckpts `ckpts/lf/stage1_a1_seq_s{0,1}.pt` |
| **K8flat** | 8 | 155,000 | flat 22,142/22,143 × lengths 2–8 | `ds-composition` A3; ckpts `ckpts/dsc/stage1_a3_s{0,1}.pt` |

Four new, two Stage-1 seeds each:

| arm | cap | records | per-length shape |
|---|---|---|---|
| **K8add** | 8 | **217,000** | K6's **exact** 31,000 × 2–6 **plus** 31,000 × 7 and 31,000 × 8 |
| **K10** | 10 | 155,000 | 17,223 × lengths 2–3, 17,222 × lengths 4–10 |
| **K12** | 12 | 155,000 | 14,091 × lengths 2–11, 14,090 × length 12 |
| **K14** | 14 | 155,000 | 11,924 × length 2, 11,923 × lengths 3–14 |

**K8add is the only arm whose set size differs (217,000 vs 155,000).** Every table that shows it
says so. K8add vs K8flat is reported as the **confound break** it is (A3 added 7–8-line proofs
*and* removed 8,857 proofs per ≤ 6-line bin; K8add adds without removing), not as a set-size result.

### Deviation from the run brief, with its reason (written before the first pod)

The brief specifies three new arms (K8add, K10, K12) and puts a **K14 arm last** in the order for
spending headroom, behind K12's and K10's seed-1 ladders. **This run runs K14 as a fourth arm from
the start** and does **not** plan seed-1 ladders. Reason: the run's question is *monotone walk vs
plateau*, and with only K12 at the top, "plateau" and "K12 is the last point measured" are the same
observation; a fourth cap point turns that into a two-point answer. The seed-1 ladders would shrink
an error bar that the **sibling `noise-floor` run is measuring directly and at n = 4 × 2**, which is
a better instrument than n = 2 here. Budget arithmetic below shows all four arms fit inside $22.

### Set construction (all assembly on the VPS; no pod)

- **Bins of length ≤ 6 for every new arm come from K6's own training set**
  (`data/p2/train_depth3_f0_a1.jsonl`, 155,000 records, pulled from the `lean-format` bucket):
  K8add takes all 155,000 **byte-identically**; K10/K12/K14 take a uniform per-bin subsample
  (seed 0). So every new arm's short bins are a **subset of the control's exact records** and
  "short proofs removed" is pure subsetting, with no re-draw noise anywhere below the cap.
  This is stronger than the brief's requirement (which asks byte-identity for K8add only).
- **Bins of length ≥ 7 come from one new pool** `data/kh/pool_long_kh.jsonl`, generated with the
  **control's generator settings** — `gen.sample_one` short mode, `max_prem 3`, `max_depth 3`,
  output filter only, generator probabilities untouched — deduplicated by renaming class, with
  depth-3 excluded in the **pruned and the written** form and all eleven evaluation pools plus
  validation-36 plus K6's own 155,000 classes excluded by renaming class. Bins are drawn
  **uniformly at random** from the eligible classes of each length, which reproduces the pool's
  natural per-length pattern rates (the pool has no per-length generation caps, so a uniform draw
  *is* the natural-rate draw); achieved reductio / derived-`ORE` / per-rule rates are reported per
  length in `data/kh/README.md`.
  - **Disclosed difference from A3/K8flat:** A3's 7–8 bins came from `data/p2/pool_cap8.jsonl`,
    which is not in any bucket and no longer on this host. K8add's 7–8 bins are therefore a
    **fresh draw from the same generator settings**, not the same records. This is exactly the
    manipulation `noise-floor` is measuring, and the K8add-vs-K8flat comparison is read against
    its table.
- Feasibility, measured before writing this file (`kh_probe.py`, control settings, 150,000 tries,
  seed 12345, `artifacts/kh/probe_short_s12345.json`): distinct renaming classes per pruned
  length **7: 2,741 · 8: 2,972 · 9: 2,136 · 10: 1,949 · 11: 1,548 · 12: 1,176 · 13: 860 · 14: 621**
  per 150k tries at ≈ 9.7 s/core. Every bin up to 14 is fillable well inside the generation budget.
- **If a bin cannot be filled** inside the generation budget: the achieved per-length counts are
  reported, the deficit is filled **proportionally from the bins that did fill**, and the fraction
  per bin is disclosed in `data/kh/README.md`. No silent substitution. If a whole arm cannot be
  filled it is dropped and said so.
- **Split disjointness by renaming class** is checked between every new training set and all
  evaluation pools and reported as a number (expected 0 everywhere).

## Measurements

Per new arm × Stage-1 seed unless stated. **Acceptance is Lean ∧ `nd_verify` everywhere**
(`nd2lean.py` unmodified; the looseness fix is queued for after this run so these arms stay
comparable to proposal 10's). **Batch sizes and decode settings are fixed across every arm and
equal to `ds-composition`'s**, so the inherited K6/K8flat numbers stay comparable:
held-out 512, ladder 512, coverage 1024, `max_new` 400 (coverage) / 512 (ladder), `sample.py`
fast path.

1. **Held-out greedy**, `data/p2/heldout.jsonl` (5,000, k = 1, T = 0). **This pool is the cap-6
   distribution.** Every arm above cap 6 is measured **out of distribution** on it. It is a
   comparability check, **not this run's headline**, and is labelled so in every table.
2. **Coverage pass@2,000** (T 0.8, seed 0) on `targets_reductio_req` (300) — the run's sharp
   quantity — and `r3_1/depth3_req` (300) for continuity with proposal 10. Reported both seeds:
   targets solved; **max pruned line count of any accepted proof**; accepted proofs at ≥ 8, ≥ 10,
   ≥ 12 lines; per-stratum breakdown.
3. **Ladder T1 and frozen at equal attempts**, 8 rounds × k 32, read out on
   `data/ladder/transfer.jsonl` (2,285), labelled by true minimal length: solved and `L*`.
   **Seed 0 only** for the new arms. **The frozen number is reported beside every T1 number**
   (`AGENT_POLICY.md`: a base-model reachability figure with every "RL solved X").
4. **Term size (formula nodes over the pruned proof) beside every line count**, for the new arms
   **and** recomputed for K6 and K8flat from their bucket artifacts, plus the training-set mean
   term size per arm.

Dropped, per the brief: the **depth-3 dial** (three runs agree its round-4 endpoint is
base-rate-insensitive across frozen rates 0.032–0.322) and the `d3sub250` coverage pool.

### Two measurement ceilings, written down before the run

Both could masquerade as a plateau, which is this run's headline alternative. Both are reported
with every affected number.

- **`L*` is hard-censored at 14 by the transfer pool.** `data/ladder/transfer.jsonl`
  (`git hash-object` = `e0524d0a84d7163feb4815910e47e09648f622b2`, byte-identical to ladder-A's
  `e0524d0`; `rl_targets.jsonl` = `69233bcaa2ea80038297bba6e8864cb8b1f00b13` = `69233bc`) has
  `L_true` counts 7: 300, 8: 300, 9: 1,010, 10: 451, 11: 99, 12: 102, 13: 13, 14: 10 — so
  **≥ 13: 23 theorems and ≥ 14: 10**. `L*` = max L with ≥ 5 solved at `L_true ≥ L`, so
  **`L* > 14` is not measurable at all** and `L* = 14` requires solving 5 of 10. **The run brief's
  expectation bands of T1 `L*` 13–15 (K10) and 14–16 (K12) are therefore partly unattainable and
  are truncated here to 13–14 and 14.** Because of this, the **uncensored** headline readout is
  measurement 2's *max pruned length of any accepted proof*, and `L*` is reported beside the
  **per-bin solved counts at `L_true` 11 / 12 / 13 / 14**, which move before `L*` can.
- **`max_new` censors accepted length.** Measured token cost of a `lean_seq` proof (median /
  max over 60 sampled proofs per length): L 10 → 152 / 292, L 12 → 194 / 374, L 14 → 218 / 355.
  At coverage's `max_new` = 400 the longest proofs are clipped. The budget is **kept at 400 for
  comparability with the inherited K6/K8flat numbers**, and the **fraction of samples that hit
  `max_new`** is reported per arm. If the top arm's frontier is truncation-bound, a diagnostic
  re-run of `redreq` at `max_new` 768 on that arm's seed 0 is added and labelled as a deviation.

## Pre-registered expectations

Scored honestly afterwards, **including the misses**. K6 and K8flat columns are the known
(inherited) values, not predictions.

| quantity | K6 (known) | K8flat (known) | K8add | K10 | K12 | K14 |
|---|---|---|---|---|---|---|
| max accepted `redreq` pruned length | 7 | 10 | 9–10 | 11–13 | 13–15 | 14–17 |
| accepted `redreq` proofs ≥ 8 lines | 0 / 0 | 29 / 33 | 20–45 | 30–70 | 30–70 | 25–70 |
| `redreq` solved (of 300) | 28 / 26 | 54 / 72 | 45–80 | 60–110 | 60–110 | 55–110 |
| frozen ladder `L*` | 9 | 11 | 10–11 | 12–13 | 13–14 | 13–14 (censored) |
| T1 transfer `L*` | 12 | 12 | 12–13 | 13–14 | 14 (censored) | 14 (censored) |
| held-out greedy (**cap-6 pool, OOD above cap 6**) | 0.909 / 0.896 | 0.951 / 0.954 | ≥ K8flat | −3 to +3 pp of K8flat | −5 to +3 pp of K8flat | −8 to +3 pp of K8flat |

**Predicted relationship.** The two known points give **frozen `L*` = cap + 3** (cap 6 → 9,
cap 8 → 11) and **max accepted `redreq` length ≈ cap + 1.5** (cap 6 → 7, cap 8 → 10). This run
pre-registers the offsets **c_frozen = +3** and **c_maxlen = +2**, i.e.

- frozen `L*` = **min(cap + 3, 14)** → K10 13, K12 14, K14 14 (the last two censored by the pool);
- max accepted `redreq` pruned length = **cap + 2** → K8add 10, K10 12, K12 14, K14 16.

Scored as: **a monotone walk with a stable offset** (every consecutive pair non-decreasing and
every point inside its band) vs **an unordered set of points** vs **a plateau**. A monotone walk
with a stable c is the only form that lets the project predict the cap needed for a target length,
and that is what is being tested.

## Falsifiers, both checked explicitly

1. **The cap-sets-the-horizon account is dead** if K10 **and** K12 both leave T1 `L*` ≤ 12 and
   frozen `L*` ≤ 11 — no advance over cap 8 — **while their training sets demonstrably contain
   proofs at those lengths** (asserted from `data/kh/README.md`'s per-length counts) **and their
   max accepted `redreq` length is ≤ 10** (the uncensored readout, added here because `L*` alone
   is censored). Then the wall is the model or the EI procedure, not the data, and that is the
   headline.
2. **The "A3 removed short proofs" account is dead** if K8add and K8flat agree within
   `noise-floor`'s measured error bar on `redreq` solved and frozen ladder solved. Then adding long
   proofs is the whole effect and composition below the cap is irrelevant, consistent with
   everything else proposal 10 found.

Additionally recorded, from `ds-composition`'s reviewer: **"the cap sets the horizon" is a
reductio-depth horizon, not a line-length ceiling** — cap-6 models routinely write accepted 8–11
line proofs on the depth-3 pools while stopping dead at 7 lines on the required-reductio pool.
Every claim in this run is stated in the pool it was measured on.

## Model labelling

Every result table and every `numbers.md` section names the checkpoint(s) behind it: model
id/path, parameter count (3,214,336), format (`lean_seq`), **from scratch**, and the training set.
No number measured on one arm is stated as a property of "the model" or of the setting.

## Budget, pods and stop rule

- Ceiling registered before the first pod: `podbudget cap-horizon --set 44 22`.
  `~/runs/cap-horizon/BUDGET_WARNING` is checked between stages.
- **Four pods**, one per new arm, cheapest 24 GB+ card in stock (3090 $0.50/h preferred;
  A40 $0.49; A6000 $0.53; 4090 $0.74). The **GPU class and the real billed rate are recorded**
  (`podbudget`'s rate table has no A6000 or 4090 case and silently falls back to $0.50/h; the
  `GPU=` line each pod's config file gets is also unquoted by `podnew`, which makes `podbudget`
  read the class as "NVIDIA" — both are corrected for this run and the correction is logged).
- Estimate: generation ≈ 0 pod-hours (VPS), 8 Stage-1 ≈ 8, held-out + coverage ≈ 10, four ladders
  (T1 + frozen, seed 0) ≈ 16 → **≈ 34 pod-hours ≈ $17** against 44 h / $22.
- **Stop rule / drop order if the budget binds:** K14's ladder, then K14 entirely, then K12's
  ladder, then K12 entirely, then K8add's ladder. Held-out and `redreq` coverage are never
  dropped — they carry the two-seed evidence.
- Artifacts uploaded to `hf://buckets/dan-pandori/nd-rl/cap-horizon/{ckpts,artifacts,data}`
  **as each stage lands**, not only at the end (this host has ~47 GB free and the sibling run is
  using it too).
