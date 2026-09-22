# Pre-registration — run `ds-composition` (proposal 9, run 1: the training set's composition)

Written 2026-09-22 ≈ 06:10 UTC, before any pod exists for this run. Executor: agent:claude. Worktree `~/work/ds-composition`,
branch `dan_ds-composition` (from `origin/dan_lean_format`). Brief `BRIEF_ds-composition.md`; proposal
`~/nd-rl/docs/proposals/2026-09-22-dataset-styles.md` (its "Protocol shared by every arm" is the protocol); policy `AGENT_POLICY.md`.
Sibling run `ds-generator` shares this host, `~/pods.log` and the pod registry: a pod named `dsg-*` in `pods.log` before this
commit belongs to it, not to this run (my pods are `dsc-*`).

## Question

Holding the generator, the Lean `lean_seq` rendering, the 3.2M model, the 6,000-step schedule, the cap (6 on the ND record),
the set size (155,000) and the depth-3 f = 0 filter fixed, does the **composition** of the pretraining set — per-length
histogram (A1, A4), per-rule quotas (A2), or, as a yardstick outside the take-home's cap-6 rule, the cap itself (A3, cap 8) —
change (a) held-out greedy accuracy by length and (b) RL readiness: base rates of depth-3 and required-reductio proofs at
pass@2,000, EI − frozen after 4 dial rounds, and transfer `L*` after ladder rung T1?

## Sets (built on the VPS with `dsc_assemble.py`, seed 0; shape / overlap / render tables in `data/dsc/README.md`)

All sets are drawn from the control's pool `data/p2/pool_cap6_recon.jsonl` (723,534 renaming classes, the unchanged
generator), with the classes of `data/p2/heldout.jsonl`, `{targets,transfer}_depth3`, `{targets,transfer}_reductio_req`,
`data/r3_1/depth3_req{,_transfer}`, `data/ladder/{rl_targets,transfer}` and validation-36 excluded (14,026 classes), and depth-3
proofs excluded in the pruned **and** the written form. Every written record is re-verified by `nd_verify` and cap-asserted;
`train.py --cap` re-asserts it on the pod, and the `lean_seq` rendering must denote exactly the record's ND proof.
Measured per-length shares of the full pool (all 723,534 classes, not the proposal's 200k sample): 2 / 3 / 4 / 5 / 6 =
**10.42 / 12.63 / 15.53 / 20.60 / 40.82 %**. Per-proof rule shares of the pool: `ORE` 1.60 %, `ANDE1` 1.70, `ANDE2` 1.69,
`BOTE` 1.48, `R` 2.05.

| arm | change to the control (one each) | per-length counts (2 / 3 / 4 / 5 / 6 [/ 7 / 8]) |
|---|---|---|
| **C0** control | `data/p2/train_depth3_f0_a1.jsonl`; Stage-1 checkpoints `lean-format/ckpts/lf/stage1_a1_seq_s{0,1}.pt` (not retrained) | 31,000 × 5 |
| **A1** natural histogram | the pool's own shares above | 16,145 / 19,575 / 24,079 / 31,925 / 63,276 (`counts_from_shares`, rounding fixed on the largest bins) |
| **A2** rule quotas | flat histogram; ≥ 10 % of proofs use `ORE` (15,500), ≥ 8 % `ANDE1` or `ANDE2` (12,400), ≥ 5 % `BOTE` (7,750), a proof may count toward several; quota proofs allocated across lengths in proportion to availability; the remainder of each length bin drawn uniformly (as the control draws) | 31,000 × 5 |
| **A3** cap-8 yardstick (**outside the take-home rule; every A3 number is labelled "cap 8"**) | lengths 2–8 flat; 2–6 from the control's pool, 7–8 from `data/p2/pool_cap8.jsonl` (the follow-up's class-deduplicated cap-8 pool, unchanged generator); `train.py --cap 8` | 22,143 × 6 + 22,142 |
| **A4** cap-heavy dose | shares 0 / 5 / 15 / 30 / 50 % | 0 / 7,750 / 23,250 / 46,500 / 77,500 |

**Deviation / disclosure for A2.** The pool holds 11,577 `ORE`-using proofs of ≤ 6 lines, fewer than the 15,500 quota, so
`ORE` proofs are topped up with `make_coverage_sets.py gen --only rule:ORE` — the unchanged generator (knobs 3 / 3), an
**output filter only**, 2 × 3,000,000 tries on the VPS (first batch: 6,390 proofs before deduplication against the pool). The
conditional distribution of an `ORE`-using proof is the generator's in both sources.

## Measurements (identical for every arm; two Stage-1 seeds; sampling seed 0; EI seed = Stage-1 seed)

Acceptance everywhere: a sample counts iff **Lean 4.34 accepts the literal sampled text and `nd_verify` accepts the ND proof it
denotes** (`lean_gate.py`, unchanged, inside `sample.generate`; `coverage_lean.py` applies the same rule to large-k sampling,
which `coverage.py` did not); `nd2lean.py --check` (unmodified) on every counted proof at the end (`pod/dsc/record.py`); every
disagreement is a bug and is reported. Literal texts are stored beside every counted proof (`found_*.jsonl` field `text`,
coverage `texts_ok`) — a small additive change to `sample.py`, `expert_iter.py`, `ladder_ei.py`.

1. **Stage-1** `train.py --mode lean_seq --steps 6000 --bs 128 --cap {6|8} --seed {0,1}`, then held-out greedy on
   `data/p2/heldout.jsonl` (5,000; 1,000 per length) via `eval_set.py`: overall, by length, and split by whether the generator
   proof of the held-out theorem has a pattern (`pat` any) or not.
2. **Base rates** `coverage_lean.py --k 2000 --temperature 0.8 --seed 0` on `data/p2/targets_depth3.jsonl` (1,000),
   `data/r3_1/depth3_req.jsonl` (300, required@8), `data/p2/targets_reductio_req.jsonl` (300; strata `min_lines_ub` 7 / 8 / 9 / 10 =
   52 / 133 / 82 / 33): targets solved; targets solved with a pattern proof (depth-3 / derived-`DN` reductio); per-sample rate; hits by
   stratum; distinct ≥ 8-line pattern proofs.
3. **Dial** `expert_iter.py --rounds 4 --k 32 --temperature 0.8 --batch 768` EI and `--no_train` frozen on the 1,000-target
   depth-3 pool with the arm's own set as `--train`: acquisition (targets with a depth-3 proof, min round per normalised proof) at
   round 4, EI − frozen, held-out greedy at round 4. Control from `lean-format/artifacts/lf/{ei,frozen}_d3_seq_s{0,1}/round_4.json`
   and `found_4.jsonl`.
4. **Ladder** `ladder_ei.py` T1 and frozen, 8 × 32, `--batch 512`, pools byte-identical to ladder-A's (`data/ladder/`,
   `rl_targets.jsonl` v2 4,495 / `transfer.jsonl` 2,285): transfer solved, `L*` (max L with ≥ 5 solved at `L_true` ≥ L), by
   `L_true` bin, textbook solves per schema, held-out greedy at round 8. Control: run on the a1 checkpoints.
5. Differences are quoted only when both seeds agree in sign; frozen controls at equal attempts everywhere.

## Control values on file (a1 `lean_seq` seeds 0 / 1; lean-format, reviewed)

Held-out greedy 0.909 / 0.896; by length s0 0.994 / 0.989 / 0.951 / 0.924 / **0.685**, s1 0.997 / 0.992 / 0.966 / 0.942 / **0.583**
(the 0.852 six-line value the brief quotes is the *full-set* model's; the a1 f = 0 models lose the depth-3 six-line theorems of the
held-out set — the pattern / non-pattern split will show this). Dial round 4: EI solved 650 / 646, frozen 358 / 295 of 1,000;
round-8 acquisition EI 0.476 / 0.479, frozen 0.206 / 0.134. Ladder on the a1 models: not on file (full-set model: T1 794 / 839
solved, `L*` 11; frozen 304 / 309, `L*` 10).

## Expected results (numbers; both seeds unless stated; "pp" = percentage points against the same-seed control)

| arm | held-out overall; 6-bin; 2–3 bins | depth-3 pass@2,000 targets solved with a depth-3 proof (1,000 pool; req8) | reductio-req pass@2,000 (stratum 7 of 52; strata ≥ 8 of 248) | dial EI − frozen acquisition at round 4 | ladder frozen solved, `L*`; T1 solved, `L*` | textbook schemata with ≥ 5 T1 solves beyond contraposition / contraposition_conv / export |
|---|---|---|---|---|---|---|
| C0 | measured (0.909 / 0.896 on file); 6-bin 0.58–0.69; ≥ 0.98 | 0.35–0.55; 0.05–0.25 | 5–25 targets; 0–5 | +0.20 to +0.30 | 150–320, 9–10; 500–800, 10–11 | ≤ 2 |
| A1 | −1 to +1 pp; **+2 to +6 pp**; ≥ 0.98 | +5 to +15 pp; +5 to +15 pp | ×1–2; ≥ C0 | within ±0.05 of C0 | **+15 to +40 %**, +0–1; +10 to +30 %, 11–12 | unchanged (≤ 2) |
| A2 | −1 to +0.5 pp; ±1.5 pp; ≥ 0.98 | ×0.5–2 of C0 | ×0.5–2 | within ±0.05 | ±10 %, unchanged; ±10 %, 11 | brief: **≥ 2 new**, `L_true` = 7 bin +20 to +60. My own point expectation: 0–1 new, `L_true` = 7 bin +10 to +40 (P(≥ 2 new) ≈ 0.35) |
| A3 (cap 8) | −1 to +1 pp; **+3 to +8 pp**; ≥ 0.98 | ≥ 0.6 (7–8-line targets are in-distribution length: **not an f = 0-at-length number**) | ×2–5; ≥ 5 | not comparable (labelled) | **≥ 1,000**, 11–12; ≥ 1,200, 12–13 | +1–3 |
| A4 | −1 to +1 pp; ≥ A1's 6-bin; **2-bin ≥ 0.95** (no 2-line training proofs) | ≥ A1 | ≥ A1 | within ±0.05 | ≥ A1 | unchanged |

**Falsifiers (from the brief, adopted).** Finding 1 ("the cap sets the horizon") is dead if A1 or A4 reaches ≥ 70 % of A3's
gain over C0 in frozen ladder solves *and* matches A3's frozen `L*`. The histogram is not a lever if A1's 6-bin is within ±1 pp
of C0 *and* its frozen ladder solves are within ±10 %. Finding 2's rule-mix version is dead if A2 moves ≥ 2 dead schemata to
≥ 5 T1 solves; it stands if 17 / 19 stay ≤ 2. Finding 3 (RL amplifies what the base does) gets its first counter-example if any
arm has a lower base rate than C0 (dial frozen at round 4 and pass@2,000) and a larger EI − frozen, on both seeds.

**Decision rule (proposal 9).** An arm replaces the control iff, on both seeds, held-out greedy is within 1 pp of C0 or better
*and* at least two of {depth-3 pass@2,000, reductio pass@2,000, ladder T1 `L*` or solved} improve with none worse. A3 is excluded
from the decision (outside the cap rule).

## Design and budget

Five RTX 3090 pods (≈ $0.50 / h), one per arm (`dsc-c0`, `dsc-a1`, …), `pod/dsc/` harness (one `nohup` job per launch call,
`LEAN_GATE_WORKERS=12`, per-process CUDA memory cap): Stage-1 (2 seeds) → held-out greedy → ladder T1 + frozen (the long
jobs, 4 arms) and dial EI + frozen (4 arms) concurrently → coverage (3 pools × 2 seeds) → checker of record. Planned
≈ 7.5 pod-hours per arm (control ≈ 5 without Stage-1) ≈ 35 pod-hours ≈ **$18**; ceiling **$22**. Stop rule: at $20 spent drop
A4's ladder, then A4, then A2's ladder. Balance at the start: $121.38 (`rpbalance` 05:56 UTC). Hard stop 30 h after 05:54 UTC
(2026-09-23 11:54 UTC). Pods deleted as soon as pulled; `ckpts/`, `artifacts/`, `data/` of this run uploaded to
`hf://buckets/dan-pandori/nd-rl/ds-composition/` at the end. No test-file run; `nd_verify`, `nd2lean.py`, `lean_gate.py` unmodified;
every training proof is generator output rendered deterministically by `lean_tok.py`.

## Amendment 2026-09-22 07:20 UTC (before any arm result beyond Stage-1 held-out; written when the confound was found)

The first draw of A1–A4 (06:06–06:39, `data/dsc/v1_uniform/`) filled each length bin **uniformly** from the pool. The pool
`pool_cap6_recon.jsonl` is pattern-enriched by its generation caps (`cap_np` on pattern-free proofs), and the control's assembler
compensates by drawing reductio and derived-`ORE` proofs at the generator's *natural* per-length rates (`make_coverage_sets.assemble_set`,
`NATURAL` table from the take-home's class-deduplicated raw pool) and the rest pattern-free. The uniform draw therefore changed a
second thing: A1 held 38,994 reductio / 1,458 derived-`ORE` proofs against the control's 10,547 / 88. All four sets were re-drawn
at 07:12–07:17 with the control's rule (reductio and derived-`ORE` at the natural rate per length — 2–6 from the control's table,
7–8 (A3 only) from `pool_cap8.jsonl`'s own class-deduplicated rates 5.78 / 5.17 % reductio and 3.43 / 13.59 % derived-`ORE`;
A2's quota picks are random among `ORE` / `ANDE` / `BOTE` proofs and the fill compensates), the arm pods' jobs were killed and
restarted on the new sets (≈ 1.1 pod-hours per arm pod lost, ≈ $2.2). Stage-1 held-out values of the first draw are kept in
`artifacts/dsc/v1_uniform/` and reported as a side observation only. Expectations unchanged.
