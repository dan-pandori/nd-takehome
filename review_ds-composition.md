# Review — run `ds-composition` (proposal 9 run 1: the training set's composition)

Reviewer: agent:claude, independent session. Started 2026-09-24 04:20 UTC.
Phase 1 workspace `~/review/ds-composition` (the run's repository with the executor's write-ups
removed). Phase-1 code is mine: `recount/rv.py` (own tokeniser, own proof parser, own
start-index normaliser, own depth counter, own pattern predicates, own renaming-class key, own
term-size counter) and `recount/r1..r8_*.py`. `patterns.py`, `coverage.py`, `dsc_analysis.py`,
`ladder_analysis.py` and every other analysis script of the executor's were **not** imported.
`nd_verify` (unmodified) and `nd2lean.py --check` are used where the protocol requires them.
All scripts and their JSON outputs are committed under `review/ds-composition-recount/`.

**Disclosure.** Before starting phase 1 I ran `git log` and `tail STATUS.md` in the main
checkout to establish whether the run had finished; that showed me the executor's summary line.
Everything below was nevertheless computed from the raw artefacts by my own code before I
opened `run_ds_composition.md`, `numbers.md` or `log.md`. Where a recounted number happens to
agree with that line I say so in §Compare rather than pretending I had not seen it.

---

## §Recount

### 0. Hard constraints

| constraint | check | result |
|---|---|---|
| `nd_verify` unmodified | `git hash-object nd_verify/{__init__,verify}.py` vs `origin/main` | **identical** (`dfa3bc3f…`, `1cfed53b…`) |
| `artifacts/TEST_RUN_DONE` unchanged | blob vs `origin/main` | **identical** (`1d5cf064…`); one test run on file, 2026-09-15 |
| at most one test-file run | no new `TEST_RUN_DONE` write, no test pool in any job command | **ok** |
| evaluation file read in training code | `grep` on `train.py` | `--heldout data/p2/heldout.jsonl` **is** read — but only inside `torch.no_grad()` to print a validation-loss log line (`train.py:116-123`); no gradient, no early stopping, no checkpoint selection (a single `save_ckpt` after the last step). Not a leak; flagged so the phrase "no evaluation file is read" is not used unqualified. |
| `lean_gate.py` unmodified | hash vs `origin/dan_lean_format` | **identical** |
| `nd2lean.py` | hash vs `origin/dan_lean_seed2` | **identical** — the BOTE fix is the owner's commit, taken whole, as amendment 3 says |
| `train.py` vs `origin/main` | 9 lines | tokenizer plumbing + an added assertion that the Lean rendering decodes back to the cap-checked ND proof. No change to the objective. |
| cap on the ND record | own re-parse of all 775,000 training records | **0 over cap** in every arm (A3 declared cap 8) |
| gate 0 (expectations written first) | `preregistration/ds-composition.md` committed `56c42bb` **2026-09-22T06:08:58Z**; first `dsc-*` pod 06:09:23Z. Amendment 3 `b836eef` **21:11:47Z**; first session-2 pod 21:12:35Z | **before, both times** (25 s and 48 s) |
| pods deleted | `list-pods` at 04:30 UTC: only `dsg-1`, `dsg-2` (sibling run `ds-generator`) | **no `dsc-*` pod alive** |
| spend | `podbudget ds-composition` | 25.70 h, **$12.84** of $18, ceiling 36 h |
| bucket | `hf buckets ls …/ds-composition/` | `artifacts/`, `ckpts/`, `data/` present (04:19–04:20 UTC) |

No hard-constraint violation. **No quarantine.**

### 1. The five sets (my own re-parse of every record)

| arm | n | per-length (2/3/4/5/6[/7/8]) | distinct renaming classes | duplicate texts | mean term size |
|---|---|---|---|---|---|
| C0 | 155,000 | 31,000 ×5 | 155,000 | 0 | 26.04 |
| A1 | 155,000 | 16,145 / 19,575 / 24,079 / 31,925 / 63,276 | 155,000 | 0 | 28.58 |
| A2 | 155,000 | 31,000 ×5 | 155,000 | 0 | 25.09 |
| A3 | 155,000 | 22,142 / 22,143 ×6 | 155,000 | 0 | 29.39 |
| A4 | 155,000 | 0 / 7,750 / 23,250 / 46,500 / 77,500 | 155,000 | 0 | 30.94 |

Every per-length count equals the pre-registration's table exactly. Every set is 155,000
distinct renaming classes with no duplicate rendered text.

**A2's quotas, achieved (my count of proofs containing the rule):** `ORE` 15,500 = **10.00 %**;
`ANDE1` ∪ `ANDE2` 12,464 = **8.04 %**; `BOTE` 7,750 = **5.00 %**. All three quotas are met.
Every other rule's share is in `review/ds-composition-recount/out_sets.json`.
*Caveat I would want stated:* 14,775 of A2's 15,500 `ORE` proofs are 6-line (708 five-line, 17
four-line). A2's histogram is flat, but 47.7 % of its 6-line bin is an `ORE` proof, so A2 is a
rule-quota change **and** a within-bin shape change at length 6.

**Amendment 1's confound fix verified.** Per-length reductio and derived-`ORE` rates:

| arm | reductio % at len 5 / 6 | derived-`ORE` % at len 5 / 6 |
|---|---|---|
| C0 | 17.34 / 16.68 | 0.09 / 0.20 |
| A1 | 17.34 / 16.68 | 0.09 / 0.20 |
| A4 | 17.34 / 16.68 | 0.09 / 0.20 |
| A2 | 17.34 / 16.68 | 0.28 / **10.32** (the quota, by design) |
| A3 | 17.34 / 16.68 (+ 5.79 / 5.18 at 7 / 8) | 0.09 / 0.20 (+ 3.43 / 13.59 at 7 / 8) |

A1 and A4 differ from the control in the **histogram only** — the conditional pattern mix
inside each length bin is bit-for-bit the control's rate. This is the single most important
thing to have got right in this run and it is right. A3's 7/8 bins carry `pool_cap8`'s own
rates, as the pre-registration states (5.78 / 5.17 and 3.43 / 13.59 — I measure 5.79 / 5.18).

### 2. Split disjointness (my own renaming-class key)

Atoms renamed in order of first appearance over premises-then-conclusion, premise order kept.
Overlap between **every** training file and **every** evaluation pool:

| | heldout | targets_depth3 | d3sub250 | transfer_depth3 | depth3_req | d3req_transfer | reductio_req | red_req_transfer | ladder targets | ladder transfer | val36 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 / A1 / A2 / A3 / A4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**All zero.** This answers the brief's open question: the control's a1 set overlaps the ladder
pools and the reductio pools in **0** renaming classes.

Evaluation pools do overlap one another (not a training leak, but worth recording because two
"independent" readiness measures partly share theorems): `targets_depth3 × depth3_req` 67,
`targets_reductio_req × ladder_rl_targets` 16, `targets_reductio_req × ladder_transfer` 15,
`transfer_reductio_req × ladder_*` 7 / 6, `targets_depth3 × ladder_rl_targets` 6.

### 3. Held-out greedy (5,000 theorems; every claimed proof re-verified by `nd_verify`)

I re-decided `solved` for all 50,000 arm×seed×theorem records. **0 disagreements** with the
executor's per-item verdicts.

| arm | overall | 2 | 3 | 4 | 5 | 6 | 6-bin, no-pattern | 6-bin, pattern |
|---|---|---|---|---|---|---|---|---|
| C0 s0 | 0.9088 | .994 | .989 | .951 | .924 | **.686** | .8178 | .6428 |
| C0 s1 | 0.8962 | .997 | .992 | .966 | .943 | **.583** | .8340 | .5007 |
| A1 s0 | 0.9172 | .996 | .988 | .966 | .941 | .695 | **.8907** | .6308 |
| A1 s1 | 0.9424 | .993 | .987 | .954 | .938 | .840 | **.8988** | .8207 |
| A2 s0 | 0.9186 | .999 | .989 | .963 | .929 | .713 | .7773 | .6919 |
| A2 s1 | 0.9402 | .997 | .986 | .962 | .931 | .825 | .7733 | .8420 |
| A3 s0 (cap 8) | 0.9508 | .998 | .988 | .957 | .934 | .877 | .8583 | .8831 |
| A3 s1 (cap 8) | 0.9536 | .997 | .994 | .960 | .948 | .869 | .8947 | .8606 |
| A4 s0 | 0.8166 | **.746** | .958 | .938 | .929 | .512 | .8462 | .4024 |
| A4 s1 | 0.8238 | **.696** | .952 | .943 | .917 | .611 | .8259 | .5405 |

Held-out pool composition (my classification of the generator proof): the 2/3/4-line bins are
100 % pattern-free; the 5-line bin is 43.6 % reductio; the 6-line bin is 75.3 % pattern
(50.0 % depth-3, 24.3 % reductio, 1.0 % derived-`ORE`). Because every arm's set is depth-3
f = 0, the 500 depth-3 six-line held-out theorems are out-of-distribution for all of them.

Against the pre-registration: C0's overall (0.9088 / 0.8962) reproduces the on-file
lean-format values (0.909 / 0.896) to four decimals — consistent with the control **not** being
retrained (`args.json` of every control job names `ckpts/lf/stage1_a1_seq_s{0,1}.pt`). C0's
6-bin 0.686 / 0.583 is inside the expected 0.58–0.69. **Misses:** A4's 2-line bin is 0.746 /
0.696 against an expected **≥ 0.95**, and A4's overall is 9.2 / 7.2 pp below C0 against an
expected ±1 pp. A1's full 6-bin moves **+0.9 pp (s0) / +25.7 pp (s1)** against an expected
+2 to +6 pp — the sign agrees but neither seed lands in the band, and the control's own 6-bin
spread across seeds (0.686 vs 0.583, 10.3 pp) is larger than the effect on s0.

The 6-bin **no-pattern** sub-bin is the stable version of that comparison: A1 +7.3 / +6.5 pp,
A2 −4.1 / −6.1 pp, A3 (cap 8) +4.1 / +6.1 pp, A4 +2.8 / −0.8 pp. A1 beats the cap-8 yardstick
on s0 (+7.3 vs +4.1) and ties it on s1 (+6.5 vs +6.1). This quantity is not in the
pre-registration; it is a defensible refinement but it is post-hoc.

### 4. Base rates at pass@2,000 (every stored proof re-verified; 0 `nd_verify` rejects)

Batch 1024, temperature 0.8, sampling seed 0, on the Stage-1 model of each arm × seed.

| arm | d3sub (250) solved / with depth-3 proof | d3req (300, required@8) with depth-3 proof | reductio-req (300) | stratum 7 (of 52) / stratum 8 (of 133) | distinct ≥ 8-line reductio proofs |
|---|---|---|---|---|---|
| C0 s0 / s1 | 139 / 71 ; 103 / 40 | 170 (.567) ; 108 (.360) | 28 (.093) ; 26 (.087) | 28/0 ; 26/0 | 0 ; 0 |
| A1 s0 / s1 | 129 / 70 ; 137 / 76 | 174 (.580) ; 197 (.657) | 16 (.053) ; 18 (.060) | 16/0 ; 18/0 | 0 ; 0 |
| A2 s0 / s1 | 108 / 48 ; 152 / 84 | 132 (.440) ; 214 (.713) | 23 (.077) ; **4 (.013)** | 23/0 ; 4/0 | 0 ; 0 |
| A3 s0 / s1 (cap 8) | 218 / 149 ; 228 / 163 | 276 (.920) ; 289 (.963) | 54 (.180) ; 72 (.240) | 30/**24** ; 42/**30** | **28** ; **32** |
| A4 s0 / s1 | 113 / 58 ; 100 / 49 | 167 (.557) ; 106 (.353) | 17 (.057) ; **0** | 17/0 ; 0/0 | 0 ; 0 |

Strata of the reductio pool are 52 / 133 / 82 / 33 — exactly the pre-registration's. Every
cap-6 arm solves **zero** targets in strata 8, 9 and 10 and writes **zero** accepted reductio
proofs of ≥ 8 pruned lines; A3 (cap 8) is the only arm that does either. (Counting distinct
proofs by *written* length rather than pruned length gives 29 / 33 instead of my 28 / 32 — a
convention difference, not a disagreement; the run should say which it uses.)

Against the pre-registration: C0's d3sub depth-3 rate (0.284 / 0.160) is **below** the expected
0.35–0.55 and C0's required@8 rate (0.567 / 0.360) is far **above** the expected 0.05–0.25;
C0's reductio stratum-7 solves (28 / 26) are just above the expected 5–25. A1's depth-3 gain is
−0.4 / +14.4 pp (d3sub) and +1.3 / +29.7 pp (d3req): sign disagrees across seeds on d3sub, so
by the two-seed rule this is **not** a difference on that pool. A1's reductio rate is **worse
than C0 on both seeds** (16 vs 28; 18 vs 26) — a clean two-seed finding against A1.

Seed spread on the reductio pool is enormous (A2 23 → 4, A4 17 → 0). Nothing about the reductio
pool other than "cap 6 never reaches ≥ 8 lines" should be stated as a difference between cap-6
arms.

### 5. Dial (4 rounds × k = 32, batch 768, frozen at equal attempts)

Acquisition = fraction of the 1,000 depth-3 targets with at least one accepted **depth-3**
proof, minimum round per start-index-normalised proof. Every found record re-verified;
**0 `nd_verify` rejects**.

| arm | EI | frozen | EI − frozen | Δ(EI−frozen) vs same-seed C0 |
|---|---|---|---|---|
| C0 s0 / s1 | 0.432 / 0.419 | 0.170 / 0.117 | +0.262 / +0.302 | — |
| A1 s0 / s1 | 0.437 / 0.408 | 0.212 / 0.270 | +0.225 / +0.138 | −0.037 / **−0.164** |
| A2 s0 / s1 | 0.408 / 0.406 | 0.135 / 0.262 | +0.273 / +0.144 | −0.011 / **−0.158** |
| A3 s0 / s1 (cap 8; labelled not-comparable) | 0.656 / 0.698 | 0.553 / 0.604 | +0.103 / +0.094 | — |
| A4 s0 / s1 | 0.403 / 0.383 | 0.155 / 0.118 | +0.248 / +0.265 | −0.014 / −0.037 |

C0's EI − frozen lands inside the expected +0.20 to +0.30. **Misses:** A1 and A2 were expected
"within ±0.05 of C0" and are −0.164 and −0.158 on seed 1.

EI acquisition in the five cap-6 arm×seed pairs spans **0.383–0.437** while frozen acquisition
spans 0.117–0.270 — the post-RL value is far more compressed than the base rate it starts from.

Falsifier 3 ("RL amplifies what the base does" gets a counter-example if an arm has a lower base
rate than C0 *and* a larger EI − frozen on both seeds): no arm qualifies. A4 has a lower frozen
rate than C0 on s0 only (0.155 vs 0.170) and a *smaller* EI − frozen. **No counter-example.**

### 6. Ladder (rung T1 and frozen, 8 × 32, batch 512) — **seed 0 only**

`L*` = the largest L with ≥ 5 solved transfer targets of `L_true` ≥ L (my own implementation on
the 2,285-target transfer pool). Every stored transfer proof re-verified; **0 rejects**.

| arm | T1 transfer solved | T1 `L*` | frozen transfer solved | frozen `L*` | frozen at round 1 |
|---|---|---|---|---|---|
| C0 | 856 | 12 | 158 | 9 | 76 |
| A1 | 965 | 11 | 205 | 10 | 117 |
| A2 | 977 | 11 | 111 | 9 | 54 |
| A3 (cap 8) | 1,438 | 12 | **976** | 11 | 766 |
| A4 | 966 | 12 | 156 | 10 | 67 |

**Seed 1's ladder does not exist.** `la_*_s1` directories hold 0–3 rounds (A3 s1: only
`args.json`), and even those kept only `record_found_*` files. Every ladder number above is
n = 1. From the partial seed-1 records I can recover one equal-attempts comparison: frozen
round 1, C0 **56** vs A1 **139** (seed 0: 76 vs 117) — A1's base ladder reachability beats the
control on both seeds at round 1, which is the only two-seed ladder statement available.

C0's T1 `L*` = 12 and A4's = 12 each rest on exactly 5 solved targets at `L_true` ≥ 12 — the
threshold itself. These `L*` values are knife-edge.

Falsifier 1 ("the cap sets the horizon" dies if A1 or A4 reaches ≥ 70 % of A3's gain in frozen
ladder solves *and* matches A3's frozen `L*`): A3's gain over C0 is 818 solves; 70 % is 573.
A1's gain is **+47**, A4's is **−2**. Neither matches A3's frozen `L*` = 11. **Finding 1 is not
falsified** — on one seed.

"The histogram is not a lever" clause: A1's full 6-bin is within ±1 pp of C0 on s0 but not s1,
and its frozen ladder solves are +29.7 %. The clause does not fire.

Textbook schemata, T1 seed 0, solves out of 40 per schema (19 schemata, 760 textbook targets):

| schema | C0 | A1 | A2 | A3 | A4 |
|---|---|---|---|---|---|
| contraposition | 19 | 40 | 39 | 39 | 37 |
| contraposition_conv | 1 | 0 | 0 | 31 | 0 |
| export | 6 | 5 | 26 | 39 | 1 |
| disjunctive_syllogism | 3 | **36** | **29** | 40 | **25** |
| demorgan_nand_to_or | 4 | **11** | 0 | 6 | 4 |
| dist_or_over_and_conv | 1 | 0 | 4 | 6 | **6** |
| constructive_dilemma | 0 | 0 | 0 | 5 | 0 |
| negated_conditional | 0 | 1 | 1 | 2 | 2 |
| peirce / peirce_sequent / import | 1 / 2 / 1 | 0 / 1 / 1 | 0 / 2 / 2 | 2 / 2 / 1 | 2 / 1 / 0 |
| demorgan_and_to_nor, demorgan_nor_to_and, demorgan_or_to_nand, dist_and_over_or(_conv), dist_or_over_and, excluded_middle, negated_conditional_conv | 0 | 0 / 0 / 0 / 0 / 0 / 0 / 0 | ≤ 1 | ≤ 1 | ≤ 1 |

Counting schemata at **≥ 5 T1 solves beyond** contraposition / contraposition_conv / export:
**C0 0, A1 2, A2 1, A3 4, A4 2.**

Falsifier 2 ("finding 2's rule-mix account dies if A2 moves ≥ 2 dead schemata to ≥ 5"): A2 moved
**1**. By the letter, **finding 2 is not falsified.** But A1 — a pure histogram change with the
control's exact within-bin rule mix — moved **2**, and A4 moved 2. So the schemata do move
under a composition change; they just do not move under *this* rule-quota change. Any wording
of the form "rule mix is not the lever, generator shape is" is not supported by this run; what
is supported is "A2's particular quotas did not move two schemata, while A1's histogram did".
The 19-schema table is also single-seed.

`L_true` = 7 bin (300 targets), T1 seed 0: C0 90, A1 144 (+54), A2 157 (+67), A3 193, A4 133.

### 7. Checker of record (Lean 4.34) and my own re-check

Executor's `record_*.json`, aggregated by me: **124,952 counted proofs**, `both_accept`
124,952, `nd_ok & lean_rej` **0**, `nd_rej & lean_ok` **0**. The record covers every dial and
ladder `found_*` file and every distinct accepted coverage proof (e.g. 195 record rows for
`cov_c0_s0_d3req`, which is exactly the 195 distinct accepted proofs I count). Held-out proofs
are not in the record but were Lean-gated at sampling time.

**My own re-check:** I drew **1,037 counted proofs** (199–210 per arm, 14–16 from each of
held-out s0/s1, all three coverage pools × 2 seeds, dial EI/frozen × 2 seeds and ladder
T1/frozen) and ran `nd2lean.py --check` myself:

| arm | n | nd_ok & lean_ok | nd_ok & lean_rej | nd_rej & lean_ok |
|---|---|---|---|---|
| C0 | 210 | 210 | 0 | 0 |
| A1 | 210 | 210 | 0 | 0 |
| A2 | 199 | 199 | 0 | 0 |
| A3 | 210 | 210 | 0 | 0 |
| A4 | 208 | 208 | 0 | 0 |

A negative control (a proof `nd_verify` rejects) is rejected by Lean with an application type
mismatch, so the checker is genuinely running.

**Gate totals across the run** (`gate_*.jsonl`, my aggregation): 26,715,560 samples gated,
5,752,957 both-accepted, `nd_ok & lean_rej` **0**, `nd_rej & lean_ok` **1,611**. I inspected the
1,611: they are all the known `BOTE` looseness (`n.elim` on `n : ¬A`, resolved as `Not.elim`),
which amendment 3 predicted and accepted by leaving `lean_tok.py` unchanged so the control's
checkpoints stay comparable. Because the gate is Lean **∧** `nd_verify`, none was counted.
`gate_selftest.jsonl`: 2,000 samples, 1,600 accepted, 0 disagreements.

Proposal 10's `lean_check` (allowlist + `#print axioms`) does not exist in this repository, so
the allowlist and axiom checks could not be run. `nd2lean.py`'s translation is core-Lean only
by construction.

### 8. Term size beside line count

Median term size (formula nodes over the dependency-pruned proof) / maximum pruned line count:

| arm | ladder T1 | ladder frozen | cov d3sub | cov d3req | cov redreq |
|---|---|---|---|---|---|
| C0 | 61 / 13 | 50 / 10 | 41 / 10 | 50 / 9 | 28 / **7** |
| A1 | 61 / 12 | 52 / 10 | 41.5 / 10 | 50 / 8 | 26.5 / **7** |
| A2 | 58 / 13 | 40.5 / 9 | 44 / 11 | 50 / 9 | 29 / **7** |
| A3 (cap 8) | 58 / 15 | 55 / 13 | 49 / 13 | 52 / 13 | 33 / **10** |
| A4 | 61 / 13 | 51 / 10 | 43 / 10 | 49 / 8 | 28 / **7** |

Two things follow that matter for the horizon claim. (a) On the **required-reductio** pool the
cap-6 arms stop dead at 7 pruned lines and A3 reaches 10 — a sharp, clean horizon. (b) On the
depth-3 pools the cap-6 arms routinely write accepted 8-, 9-, 10- and (A2) 11-line proofs.
"The cap sets the horizon" is therefore a statement about the *reductio* frontier, not a
universal line-length ceiling, and should be worded that way.

Training-set mean term size is itself a confound worth naming: C0 26.0, A2 25.1, A1 28.6,
A3 29.4, A4 30.9. A4 has the largest mean term size and the worst held-out accuracy.

### 9. Configuration audit

Every job's `args.json` / first log line, checked by me: Stage-1 `train.py --mode lean_seq
--steps 6000 --bs 128 --seed {0,1}`, `--cap 6` for C0/A1/A2/A4 and `--cap 8` for A3;
3,214,336 parameters, from scratch, `lean_seq` surface form. Each arm's EI and ladder job uses
its **own** set as `--train` and its own Stage-1 checkpoint as `--init`; the control's jobs use
`ckpts/lf/stage1_a1_seq_s{0,1}.pt` and `data/p2/train_depth3_f0_a1.jsonl`. Frozen controls run
at equal attempts everywhere (dial 4 × 32, ladder 8 × 32). Batch sizes are held fixed across
arms exactly as amendment 3 promised: held-out 512, dial 768, ladder 512, coverage 1024;
`max_new` 400 / 512. No duplicate target rows in any coverage file (the session-1 orphan
incident did not recur).
