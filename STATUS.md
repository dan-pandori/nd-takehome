# STATUS — lean-format (proposal 8)

Brief: BRIEF_LEAN_FORMAT.md. Policy: AGENT_POLICY.md. Run id: lean-format. Only exception to the pause.

## lean-format
- 2026-09-21 02:52 UTC  run started (executor). 03:00 pre-registration committed (`preregistration/lean-format.md`, c2dcd0a) before any pod. Lean token format fixed in `lean_tok.py` (two naming schemes: `lean_rand` primary, `lean_seq`).
- 2026-09-21 03:04–08:03 UTC  four RTX 3090 pods (lf-1 … lf-4), all deleted; ≈ $6.2 of the $30 budget. 16 Lean-format arms + 7 Stage-1 models + solo timing rounds + checker of record.
- Result: `lean_seq` **not worse on all three** (held-out 0.909 / 0.896 / 0.936 vs token 0.883 / 0.883 / 0.948; depth-3 acquisition 0.476 / 0.479 vs 0.335 / 0.364; ladder transfer L* 11 / 11 vs 10 / 10). `lean_rand` (pre-registered primary): worse in distribution (0.882 / 0.790 / 0.830), better on depth-3 (0.433 / 0.462), equal L* (10 / 10). Frozen Lean base models already write depth-3 proofs (0.13–0.28 vs 0.005) and have L* 9–10 (token 7). Lean vs nd_verify: 0 disagreements on 41,840 counted proofs; 460 "Lean-only" acceptances among 13.9 M sampled (nd2lean's BOTE rendering is loose — see QUESTIONS.md).
- Deliverables: `run_lean_format.md`, `numbers.md` § lean-format, `log.md` § lean-format, `figures/lean_format.png`, bucket `hf://buckets/dan-pandori/nd-rl/lean-format/`. Two questions for Dan in `QUESTIONS.md` (2026-09-21).

LEAN-FORMAT DONE 2026-09-21T08:10:42Z

# STATUS — ds-generator (proposal 9, run 2: generator proof-shape distribution)

Brief: BRIEF_ds-generator.md. Policy: AGENT_POLICY.md. Run id: ds-generator. Sibling: ds-composition (same host, own pods `dsc-*`?; mine are `dsg-*`; `~/pods.log` is shared — gate-0 confound noted).

## ds-generator
- 2026-09-22 05:54 UTC  run started (executor). Generator knobs implemented behind flags (control path byte-identical, 3 code paths diffed), VPS probes of the G1 / G2 yields, pre-registration `preregistration/ds-generator.md` written ≈ 06:25 UTC before any pod. Two design deviations pre-registered: G1 is a null manipulation at cap 6 (ORE share 1.0 vs 1.5 %); G2 as run = the ladder pools' strict long generator restricted to cap 6 (+ boxes-in-ORE knob) because the literal G2 is degenerate (84 % reductio, bins 2–4 unfillable). Question in QUESTIONS.md.
- 2026-09-23 21:00 UTC  **Resumed** after the 2026-09-22 credit cut-off. `artifacts/dsg/` recovered from git, `data/` intact, control checkpoints and the two training sets pulled from the buckets; `ckpts/dsg/` gone, so G1 / G2 Stage-1 is retrained with a held-out reproduction check. Pre-registration addendum `2733373` committed 21:06 before any pod (gate 0). Missing work being run now: ladder T1 + frozen (8 × 32) for all three arms and both seeds, the textbook-schema table, and the checker-of-record pass.
- 2026-09-23 21:10–21:55  3090 / A40 out of stock; two pods instead of three — `dsg-1` RTX A6000 48 GB $0.33/h, `dsg-2` RTX 4090 24 GB $0.34/h — and **one seed per pod with all three arms on it**, so every arm-vs-arm comparison is on one GPU. The fast decode path failed the pre-registered equivalence check *only* with compaction on (1 row of 128 flips at decode step 162); per the pre-registered fallback the run uses `ND_SAMPLE_COMPACT=0` and the originally pre-registered `--batch 512` / `--max_new` 512, which passes exactly.
- 2026-09-24 08:50 UTC  **Result.** Both pre-registered accounts fail. *Transfer wall is not the shape
  distribution*: frozen ladder solves of 2,285 are C0 158 / 114, G1 170 (s1), G2 44 / 125, against a pre-registered
  450–760 for G2; G1 — an independent pool with the control's shape table — is above both C0 seeds, and its own T1
  seeds (916, 635) bracket the whole C0–G2 gap. *Textbook wall is not the rule shape*: 10 of 19 schemata are at 0
  solves in every arm and seed, G1 and G2 leave 17–19 of 19 at ≤ 2, and the `ORE`-needing families the brief named
  (dilemma / De Morgan / distribution) are at 0 everywhere. The run's clearest positive measurement is the **noise
  floor**: retraining Stage-1 from the same set and seed moves held-out greedy −4.44 to +5.96 pp (all in the 6-line
  bin) where a byte-identical checkpoint on new hardware and a new decode path moves +0.00 / +0.08 pp. Finding 3
  keeps its counter-example (G2: lower base rate, larger EI − frozen, both seeds). Lean vs `nd_verify`:
  **0 disagreements on 57,013 counted proofs**. Cost 21.34 pod-hours, $13.02 of $14; 11 of 12 ladder jobs
  (`la_frozen_g1_s0` dropped for budget — `QUESTIONS.md`). All pods deleted.
- Deliverables: `run_ds_generator.md`, `numbers.md` § ds-generator, `log.md`, `figures/dsg_{shape,readiness}.png`,
  `artifacts/dsg/summary.json`, `data/dsg/README.md`, bucket
  `hf://buckets/dan-pandori/nd-rl/ds-generator/{artifacts/dsg,ckpts/dsg,ckpts/ladder,data/dsg}`.

DS-GENERATOR DONE 2026-09-24T08:50:00Z


# STATUS — noise-floor (proposal 11, run 2: what difference can this project resolve?)

Brief: run brief `noise-floor`. Policy: `AGENT_POLICY.md`. Run id: noise-floor. Pods `nf-*`.
Sibling on this host: `cap-horizon` (own pods, own budget). My output is its yardstick, so interim
numbers go into `numbers.md` § noise-floor as each stage lands rather than at the end.

## noise-floor
- 2026-09-24 15:59 UTC  run started (executor). Read proposal 11, the `ds-generator` summary
  (§"the measurement noise is this run's real headline constraint"), the `ds-rendering` summary's
  Finding R-2 and its bimodality note, `ds-composition`'s ladder tables, and the `pod/dsg` harness.
- 16:05:12 UTC  pre-registration `e8f4c3b` committed and pushed **before any pod** (first pod
  `nf-1` created 16:05:45 UTC — gate 0 holds, 33 s). Design: four null pools P1–P4 from the
  unmodified generator (`knobs_from_args` returns `None` with no flags — verified) at generator
  seeds 21000/22000/23000/24000, assembled flat 31,000 × lengths 2–6 = 155,000, depth-3 excluded,
  × Stage-1 seeds 0 and 1 = eight models. Held-out greedy (overall / per length / depth-3 slice),
  coverage pass@2,000 on three pools, frozen ladder 8 × 32. Plus two n = 1 gap-closers from bucket
  checkpoints: `la_frozen_g1_s0` (`ds-generator`) and `ds-composition`'s C0 + A1 ladder, T1 and
  frozen, on **both** Stage-1 seeds. Fifteen standing findings named in advance as expected-to-fall
  or expected-to-stand.
- 16:05–16:14  Pods `nf-1` / `nf-2`, **NVIDIA A40 48 GB**, catalogue $0.49/h (real billed rate to be
  read from RunPod's billing API and recorded in `log.md`; `podbudget`'s column is a $0.49 estimate).
  Both have a **7.65-CPU cgroup quota** despite `nproc` 96, so `LEAN_GATE_WORKERS=3` × 4 concurrent
  chains, `coverage.py --procs 2`. `podbudget noise-floor --set 36 18` registered before the first pod.
- 16:16–16:21  Four null pools generated and assembled (4 min each). **Premise check passes**: every
  shape quantity agrees across P1–P4 to ≤ 0.26 pp and with the control's published table to ≤ 0.4 pp
  (`ORE` 1.42–1.48 % vs 1.46; box depth 53.1–53.3 / 35.3–35.5 / 11.3–11.4 % vs 53.2 / 35.4 / 11.4;
  mean premises 1.41–1.42 vs 1.41). 0 exact-`thm` and 0 renaming-class collisions with all nine
  evaluation / ladder pools, on all four sets. Pairwise class overlap between the four sets 5.8–6.0 %.
  **All four are replicates, not arms.** `numbers.md` § N1.
- 16:27  Pre-registration **addendum 1** (committed before any outcome existed): Stage-1 **seed 2** on
  all four pools, 4 × 3 = 12 cells, because the pre-registered design estimates the seed variance
  component with 1 degree of freedom and cannot answer E12. ≈ $2.7.
- 16:46  **First result — the held-out floor, eight null cells.** Overall greedy **0.868–0.963,
  sd 0.039**, i.e. the smallest difference two seeds can resolve is **± 20.9 pp**; pre-registered
  E1 (sd ≤ 0.02, range ≤ 5 pp) **missed by about 2×**. The 6-line bin is **0.473–0.920, sd 0.189,
  max/min 1.95×**, and the depth-3 slice **0.040–0.918, 22.9×** — and the two are the *same*
  quantity (all 500 depth-3 held-out theorems are 6-line; r = 0.9994 across the eight cells).
  Both between-pool and between-seed variance components are **negative**: the spread is neither the
  data draw nor the seed, it is the individual training run. `numbers.md` § N2.
- 17:45  **Scope cut, and the ceiling raised 36 h / $18 → 42 h / $21** (`log.md`, `QUESTIONS.md`): a
  frozen ladder measures at **1.94 pod-hours** on these A40s, not the brief's 1.25, and `pass@2,000`
  coverage at 0.7–2.4 h, so the brief's design needs ≈ 60 pod-hours against its 36. Dropped, in the
  brief's own order: `targets_depth3` coverage everywhere; seed 2 reduced to Stage-1 + held-out; the
  `ds-composition` gap-closer reduced to **A1 seed 1** (C0 seed 1 is already on file from
  `ds-generator` on the identical checkpoint and command). Projection ≈ 33 pod-hours ≈ $16.
- 23:28  **Headline result — the frozen-ladder floor, eight null cells.** Transfer theorems solved:
  **62 / 96 / 117 / 174 / 177 / 200 / 262 / 265 of 2,285 — a 4.27× range**, sd 74.1 (43.8 % of the
  mean). The smallest difference two seeds can resolve is **±235 %**. The control's published 158 /
  114 sits in the middle of that range, and so does every frozen-ladder value proposal 10 reported
  (G2 44 / 125, G1 170, A1 205, A2 111). Pre-registered E8 (1.4–2.5×) and E10 (±40–60 %) both
  **missed, the floor being far larger than predicted**; the falsifier (max/min < 1.2×, which would
  have revived the shape account) is **decisively not triggered**. `L*` is the robust readout:
  9 in seven cells, 10 in one, resolvable difference **±1.9 points**. `numbers.md` § N3.
- 2026-09-25 03:35  Pre-registration **addendum 2** (before any seed-3+ model existed): 40 more
  Stage-1 seeds on P1–P4, **held-out greedy only**, to pin the bimodal cell's high-mode probability.
  52 held-out cells in total, ≈ 6.5 pod-minutes per model.
- 05:00  **Both n = 1 gaps closed.** `ds-generator`'s missing `la_frozen_g1_s0` = **62** against its
  arm-mate's **170** — G1's own two seeds bracket C0 (158/114) and G2 (44/125) entirely.
  `ds-composition`'s A1 at Stage-1 seed 1: T1 **847** (C0's is 965, so "A1's T1 beats C0" **reverses**),
  frozen **194**, frozen `L*` **9** (so "A1 `L*` 10 vs C0 9" **dies**).
- 07:05  **Result.** The floor, per quantity: frozen ladder **62–265 of 2,285 (4.27×, ±235 %)**,
  `L*` **9–10 (±1.9)**, `targets_reductio_req` **6–46 (7.67×)**, `required@8` **61–242 (3.97×)**,
  held-out greedy overall **±16.3 pp** at 52 cells, 6-line bin and depth-3 slice **not resolvable at
  n = 2 at all**. The depth-3 slice is bimodal; the estimand is p(high mode) = **0.462, Wilson
  [0.333, 0.595]**. ≈ **99 % of the variance is the individual training run** — the pool variance
  component is negative on every quantity, so re-drawing the data set is no stronger a replicate than
  re-seeding Stage-1. **Of twenty standing findings scored, two survive, both the cap-8 arm.** The
  pre-registered falsifier (max/min < 1.2×) did not fire, by 3.6×. Seven of nineteen expectations met,
  nine missed, and the misses that matter all say the floor is bigger than predicted.
  Checker: **0 disagreements on 39,137 counted proofs**; in-loop gate 67.1 Lean-only per million
  distinct, 0 the other way. Cost **28.32 pod-hours, $13.88** of a 42 h / $21 ceiling; both pods deleted.
- Deliverables: **`NOISE_FLOOR.md`** (standing reference), `run_noise_floor.md`, `numbers.md`
  §§ N1–N11, `log.md`, `figures/nf_{cells,resolvable}.png`, `artifacts/nf/summary.json` (52 rows) and
  `artifacts/nf/premise.json`, bucket
  `hf://buckets/dan-pandori/nd-rl/noise-floor/{artifacts/nf,ckpts/nf,data/nf}`. Two questions for Dan
  in `QUESTIONS.md` (the `pod_budget_watch` bug I fixed; the budget raise the measured cost forced).

NOISE-FLOOR DONE 2026-09-25T07:25:00Z

## Run `lean-judge` (executor, 2026-09-27)

START 2026-09-27T17:20Z. Making **Lean the only judge** on the fork's `dan` branch (Dan, 2026-09-27):
`lean_judge.py`, the gate change, the six loop-file import swaps, `lean_check.py` with `Not.elim`,
tests, `LEAN_JUDGE.md`, and a seven-part acceptance test. Pre-registered in
`preregistration/lean-judge.md` (commit `579ee16`, before any pod). Pod budget 8 h / $4; one A40
(`lj1`, $0.49/h) for acceptance test 5 only.

LEAN-JUDGE DONE 2026-09-27T18:35:00Z — Lean alone decides on the fork's `dan` branch.
`lean_judge.py` (marker ⇒ reject, gate registry ⇒ that verdict, else batched `nd2lean` + Lean);
`lean_gate.py` no longer calls `nd_verify` and returns **clean ND strings** for accepted samples;
the six loop files import the Lean judge and batch; `lean_check.py` admits `Not.elim`, `Not.intro`,
`And.elim`, `Iff.elim`; `nd2lean.translate(require_all_pr=False)` for the judge only.
**All seven acceptance tests pass**: 281,817 / 281,817 stored ND proofs the old gate counted are
counted now (**0 losses**), line counts identical on all of them; 6,419 / 6,419 of the Lean-only
class now counted (41.7 % omitted premise re-statement, 25.9 % `Not.elim`); Lean agrees on the
literal text, `nd2lean(nd)` and `nd2lean(norm(nd))` on all 6,419; one expert-iteration round with
**0 `LEAN*` markers** in the training files and 166 hindsight relabels accepted; the judging step is
6.4× faster; `lean_check --selftest` 39/39. Read `LEAN_JUDGE.md`; counts in `numbers.md` § lean-judge
(L0–L8), write-up `run_lean_judge.md`, figures `figures/lj_*.png`, raw files `artifacts/lj/` and
`hf://buckets/dan-pandori/nd-rl/lean-judge/`. One A40 pod, 0.66 h, $0.32 of $4. Three questions for
Dan in `QUESTIONS.md` (the `no-denotation` class, `require_all_pr`, relabelling the pools).

## fast-stage1 (executor, started 2026-09-28T16:23:22Z)
Make Stage-1 training use the GPU (proposal 15 §1). Pre-registration `preregistration/fast-stage1.md`. Budget $5 / 10 pod-h.
FAST-STAGE1 DONE 2026-09-28T17:44:50Z — `train.py --impl fast` (default for from-scratch GPU training): packed, compiled,
one CUDA graph per step. **Equivalence 14/14 within the n = 8 MDD** vs stage1-dynamics arm C. Speed on an A40: 345 s → 128–135 s
per model (2.6–2.7×; ≈ 10× vs the brief's 1,288 s, which was legacy sharing a GPU); per-GPU throughput ≈ 3.2× legacy's best;
N seeds per A40 adds only ~10 % (GPU-bound), an H100 takes N = 16 (188 steps/s) but costs ≈ 1.9× per model. 5× per GPU **not met**.
Read `FAST_STAGE1.md`, `run_fast_stage1.md`. 1.49 pod-h, $1.47 of $5; pods deleted; bucket `hf://buckets/dan-pandori/nd-rl/fast-stage1/`.

# STATUS — lean-prefilter (proposal 15, items 3 and 4)

Brief: nd-rl `docs/proposals/improvements/BRIEF_lean-prefilter.md`. Policy: nd-rl `AGENT_POLICY.md`. Run id: lean-prefilter. Budget $3 / 6 pod-hours.

## lean-prefilter
- 2026-09-28 16:20 UTC  run started (executor). Prototype `lean_prefilter.py` (type checker for the `lean_seq` fragment, reject-only) removes all 1,158 Lean rejects of `lean-judge`'s test-5 dump with 0 false rejects on its 2,348 accepts. Pre-registration `preregistration/lean-prefilter.md` committed before any pod.
- 2026-09-28 16:34–17:59 UTC  Two A40 pods (`lp-t`, `lp-k`, $0.49/h billed), both deleted: 2.67 pod-hours, $1.31 of $3.
- Result: (a) **0 false rejects in 1,310,119 Lean-checked texts** (1.21 M distinct model samples from 8 checkpoints + 76 k edge mutants + 20 k stored bucket records); the filter removes 100 % of Lean's rejects. (b) filter off/on identical on 120 k texts. (c) T1 round on `ckpts/dsc/stage1_a1_s1.pt` (3.2 M, `lean_seq`): 1,111 s → 272 s (0.245; 259 s after `lean -j 1`), accepted set identical at fixed batch; gate share 57 % → 3–6 %. Worker finding: Lean's default thread count (one per visible core, 96) made quota-sized pools slower; `LEAN_GATE_THREADS=1` is now the default.
- Deliverables: `LEAN_GATE.md`, `run_lean_prefilter.md`, `numbers.md` § lean-prefilter, `log.md`, bucket `hf://buckets/dan-pandori/nd-rl/lean-prefilter/artifacts/lp/`. Merged into the fork's `dan`.

LEAN-PREFILTER DONE 2026-09-28T18:20:39Z — sound reject-only pre-filter (0 false rejects / 1.31 M texts), pipelined quota-sized gate; T1 round 1,111 s → 259 s. Pods deleted, bucket synced.

# STATUS — results-registry (proposal 15 §5)

Brief: `docs/proposals/improvements/BRIEF_results-registry.md` (nd-rl). Run id: results-registry. Budget $1 / 2 pod-hours.

## results-registry
- 2026-09-29 00:20 UTC  run started (executor). Pre-registration `preregistration/results-registry.md` committed before any pod.
- 2026-09-29 01:40 UTC  **Done.** Every pre-registered check passed: checkpoint URIs download to the recorded md5
  (5 / 5), negative controls fail (3 / 3), one filter gives control-checkpoint held-out accuracy for 25 runs,
  headline numbers reproduced exactly (3 / 3, one substitute named in advance), and cost is 0.06 ms per row and
  3–7 s per checkpoint. Backfill: 298,943 rows from 32 reviewed runs. Merged into the fork's `dan`: `save_ckpt`
  now uploads on save, and training scripts stop at start-up without `ND_RUN_ID` (see `REGISTRY.md`). Proposed
  policy text is in `QUESTIONS.md`. Spend: rr-1, RTX 3090, 0.21 h, $0.10; pod deleted.

RESULTS-REGISTRY DONE 2026-09-29T01:45:00Z

# STATUS — repo-hygiene (proposal 15 §6, cheap half)

## repo-hygiene (executor, started 2026-09-29T01:30:06Z)
- 01:33 pre-registration `preregistration/repo-hygiene.md` committed; no pods planned. Blocker found: the VPS's GitHub
  token lacks the `workflow` scope (QUESTIONS.md); default: workflow shipped as `ci/ci.yml`, run locally.
- LIMIT_HIT 2026-09-29T01:54:42Z (session paused; resumed the same minute, nothing lost).
- 01:56 artifacts/ out of the tip: 5,992 files verified in the bucket (0 lost; 1,981 uploaded first), fresh worktree
  227 MB. CPU CI (`ci/run_ci.sh`) green in a clean environment, red on scratch branch `ci-broken`. Not shown on GitHub:
  token lacks `workflow` scope (ships as `ci/ci.yml` + `ci/install_workflow.sh`). `record.save_config` in all 59
  scripts with `--out`/`--outdir`. Write-up `run_repo_hygiene.md`.
- Merged into `dan` (`77344dfd`); local CI on `dan` green (58 s). GitHub run pending the `workflow` scope.
- long-pool merged into `dan` meanwhile and re-added 5 artifacts/lpool files (all in the bucket): untracked; CI's config check caught its new script, fixed. CI green on the merged tip (50 s, local).
REPO-HYGIENE DONE 2026-09-29T02:00:32Z


# STATUS — repo-hygiene-2

## repo-hygiene-2 (executor, started 2026-09-29T15:34Z)
- 15:50 pre-registration `preregistration/repo-hygiene-2.md` committed; no pods planned. Orchestrator's AMENDMENT line removed from the top of this file.
- 16:00 merged into `dan` (0c34c534), Actions green on `dan`; acceptance met (0 lost, guard red on 6 MB, 148.1 MB worktree, 0 credential hits). Fetch demo switched from lean-prefilter to noise-floor (deviation, log.md).

REPO-HYGIENE-2 DONE 2026-09-29T15:58:53Z


# STATUS — compute-record

## compute-record (executor, started 2026-09-30T00:10Z)
- 00:15 pre-registration `preregistration/compute-record.md` committed (34693ad2). One GPU pod planned (≤ 15 min job).
- 00:19–00:41 pod cr1 (A40): GPU check parts 1–2; 00:54–00:57 pod cr2 (A40): part 3 after review fixes. Both deleted; 0.42 h, $0.21.
- Pre-registered expectations met: overhead 0.025 % of a step; 20 / 20 counters equal to independent counts; gpu_seconds / wall 0.989 (6 min), 0.975 (2 min); shorter jobs lose a fixed ~2 s a process (0.92–0.96). `run_compute_record.md`, `numbers.md`.
- Merged into `dan` (fast-forward to 03b620ed); GitHub Actions green on `dan` (run 36653017895) and on the same tip on `ci-compute-record` (36652863767). frontier-supply / search-expert get compute rows from any script that calls `record.save_config`; per-arm table: `python3 registry_merge.py --compute --q run_id=<run>`.
- Bucket: `hf://buckets/dan-pandori/nd-rl/compute-record/` (ckpts/, artifacts/); registry rows under `registry/compute-record/`.

COMPUTE-RECORD DONE 2026-09-30T01:02:02Z


# STATUS — grpo-state (GRPO in the proof-state environment, support-expanding advantages; code phase)

Brief: nd-rl `docs/proposals/orchestration` run brief `grpo-state`. Policy: AGENT_POLICY.md. Run id: grpo-state. Budget $3 / 6 pod-hours (code phase only).

## grpo-state
- 2026-09-30 02:10 UTC  run started (executor). Code phase: `grpo_state.py` + advantage variants + tests; the experiment is pre-registered for later, not run.
- 2026-09-30 02:17 UTC  pre-registration `preregistration/grpo-state.md` committed (c21af4c) before the first pod (02:21).
- Built `grpo_state.py` + `grpo_adv.py` (default / unlikely / pass@k / distinct), CPU tests in CI (green on `dan` at 4eb500d), two GPU smokes (RTX 3090 timings: 19.5 s / update, 8.6 GB, 1.47× with two jobs per card; A40 boundary path). Independent code review: no serious bug; fixes applied. 0.32 pod-h, $0.16; pods deleted. Merged into `dan`.
- Experiment not run (code phase): costed at ≈ $37–43 for the brief's 6 seeds (only s0–s3 exist); question in `QUESTIONS.md`, default Plan B (4 seeds, ≈ $24). Deliverables: `run_grpo_state.md`, `numbers.md` § grpo-state, `log.md`, bucket `hf://buckets/dan-pandori/nd-rl/grpo-state/`.

GRPO-STATE DONE 2026-09-30T02:51:03Z


# STATUS — best-state (Robbie's network and pretraining recipe in the proof-state format, cap 6 and cap 12)

Brief: run brief `best-state` (Dan, 2026-09-30). Policy: AGENT_POLICY.md. Budget $55 / 110 pod-hours.

## best-state
- 2026-09-30 15:59 UTC  run started (executor). Port of Robbie's recipe written (`best_model.py`, `state_train_best.py`, `state_train.py --recipe best`); both training sets checked (155,000 records each). Pre-registration `preregistration/best-state.md` committed before the first pod.
- 16:02–16:32 UTC  CPU tests pass (on a pod, CUDA hidden). Pilot: 300 s → held-out greedy 0.9424, val 0.0709; 1,200 s → 0.9626, val 0.0715. Pre-registered rule → **1,200 s** for all six models (9.56M params). Six A40 pods (bs-p0..p5) run Stage-1 → T1 ladder; two A40 reader pods (bs-r0 inherited, bs-r1 new frozen).
- 16:40 UTC  ladder batch 4,096 and then 2,048 OOM'd: ALiBi's prefill bias was built in fp32 (~29 GB). Now built in bf16 in place (bit-identical values, checked on GPU); ladder batch 2,048.
- 17:55 UTC  **Frozen read-outs, UNREVIEWED** (Lean alone; new = best recipe, 9.56M, `lean_staten`, Stage-1 1,200 s on A40; ours = 3.2M inherited SN-v2 cap-6 / SN-cap12 Stage-1). textbook72 pass@256 (all 72, per seed → IQM): best-cap6 19 / 18 / 20 → 19 vs ours-cap6 16 / 14 → 15; best-cap12 32 / 27 / 27 → 28.7 vs ours-cap12 26 / 29 / 32 / 26 → 27.5. Robbie's dev metric (dev 1,108, k 64, ≥ 7, read in the state env): best-cap6 569 / 466 / 506 → 514 vs ours-cap6 405 (s0; s1 pending); best-cap12 782 / 767 / 741 → 763 vs ours-cap12 745 / 782 / 804 / 781 → 781.5. Held-out greedy: best-cap6 0.963 / 0.967 / 0.955, best-cap12 0.926 / 0.951 / 0.903 (ours-cap12 0.969–0.978). MDDs (pre-registered): textbook72 9.3 (cap 6) / 6.5 (cap 12), dev 88 / 61. Only the cap-6 dev difference so far exceeds its MDD. Six T1 ladders running since ≈ 17:00, ≈ 25–30 min per round → done ≈ 21:30 UTC.
- 19:55 UTC  **All frozen read-outs, UNREVIEWED** (IQM; best = 9.56M best recipe, ours = 3.2M inherited; `artifacts/bs/analysis_stdout.txt`). best − ours, cap 6 / cap 12: textbook72 +4.0 / +1.2 (MDD 9.3 / 6.5); dev metric +147 / −18 (MDD 88 / 61); holdout250 pass@256 132 vs 93 / 187 vs 186.5; rr600 Q (13–16, /380) 6.3 vs 1.5 / 241 vs 214 (ours at `max_steps` 48); transfer_long2 (/21) 0 vs 0 / 6.3 vs 3; held-out greedy 0.962 vs 0.964 / 0.927 vs 0.976. Cap 6: the bigger recipe helps on transfer-type pools (dev +147, beyond the MDD); cap 12: no textbook72 / dev difference, lower held-out greedy, more long-pool solves. CI green on `ci-best-state` (36767006465); independent code review of the port found no result-changing bug. Ladders: cap 6 at round 5–6, cap 12 at round 3–4 (≈ 1 h / round) → cap-12 T1 ≈ 01:30 UTC.
- 23:00 UTC  **best-cap6 T1, seeds 1–2, UNREVIEWED** (s0 reading; `artifacts/bs/eval/T1_best6_s{1,2}__*`): textbook72 40 / 33 (ours cap-6 T1 22 / 16; ours cap-12 T1 36–38); dev metric 986 / 1,002 (ours cap-6 T1 746 / 663; cap-12 T1 927–972); holdout250 229 / 227 (160 / 220); rr600 Q 346 / 339 (/380; ours cap-6 T1 102 / 28, cap-12 T1 233–320); transfer_long2 18 / 17 of 21 (ours cap-6 T1 0 / 0, cap-12 T1 8–17); held-out greedy 0.996 / 0.994. Row-level check of long2 done (shortest accepted proofs 16–28 lines, n_ok up to 202/256). Recipe vs recipe, not compute-matched: the best-cap6 ladders took ≈ 4.5–5 h against ≈ 2.3 h for the 3.2M cap-6 ladders. Pods bs-p1, bs-p2 deleted. Cap-12 ladders at round 6; T1 ≈ 01:30–02:00 UTC.
- 04:50 UTC (2026-10-01)  **All read-outs done, UNREVIEWED.** T1 IQM, best vs ours: textbook72 37.3 vs 19 (cap 6), 51.7 vs 37.5 (cap 12); dev metric 997 vs 705, 1,054 vs 951; rr600 Q 345 vs 65, 376 vs 306; transfer_long2 17.7 vs 0, 20.7 vs 14.5. Frozen differences are small (textbook72 +4.0 / +1.2, inside the MDD; dev +147 / −18). Not compute-matched: equal attempts, ≈ 2× GPU-seconds per best ladder. Pre-registered "supported" condition holds; every T1 prediction missed high. Cap diagnostic: truncation is non-terminating actions; solved sets only grow at 2× caps (+2 max). `run_best_state.md`, `numbers.md` § best-state, `log.md`, `figures/best_state.png`. Port merged into the fork's `dan` (CI green on the same code). All pods deleted; 60.74 pod-hours, $29.76. Bucket `hf://buckets/dan-pandori/nd-rl/best-state/{ckpts,artifacts}` (manifest rows in `artifacts/MANIFEST.jsonl`).

BEST-STATE DONE 2026-10-01T05:00:12Z


# STATUS — guided-tts (proposal 24 Part A, narrowed: guided sampling vs plain resampling at test time, matched compute)

Brief: run brief `guided-tts` (Dan, 2026-10-03). Policy: AGENT_POLICY.md. Budget $10 / 20 pod-hours. No training.

## guided-tts
- 2026-10-03 18:05 UTC  run started (executor). Pre-registration `preregistration/guided-tts.md` committed before the first pod. Problem files copied to `data/gt/` (sha256 match both manifests).
- 18:50 UTC  Three A40 pods (gt-p0..p2, one model seed each). Plain reads done for 5 / 6 models (best12 s0 plain 178 / 259 solved; textbook72 48 = `trajectory`'s 48). **Checker gate passed on s1**: 109,151 distinct (state, step) pairs from the plain arm (cap 12 + cap 6), checker vs Lean 62,080 accept/accept, 47,071 reject/reject, **0 false rejects**, 0 misses. Guided-logical reads running.
- 21:45 UTC  **All reads done, UNREVIEWED** (`run_guided_tts.md`, `numbers.md` § guided-tts). Models: `trajectory(-cap6)` la_T1_best{12,6}_s{0,1,2}_r8 (9.56M ALiBiGPT, lean_staten); Lean alone. Matched sampled tokens, long (90 release theorems > 10 lines), k 64: guided-logical − plain +10.0 / +9.9 / +5.2 pp (cap 12), +7.4 / +8.1 / +10.3 (cap 6), MDD 2.7; matched wall-clock agrees; guided-structural ≈ plain (± 1.2). Falsifier not met. Checker: 0 false rejects in 314,541 steps. Deviation: best12 s0 structural rerun at batch 1,024 after an OOM (wall excluded). All pods deleted; 9.07 pod-h, $4.45.

- 21:48 UTC  Independent code review: nothing that changes a number. CI green on `ci-guided-tts`; checker + guided sampler merged into the fork's `dan` (fast-forward, e18e524e). Bucket `hf://buckets/dan-pandori/nd-rl/guided-tts/{artifacts/gt,artifacts/guided-tts,data/gt}`; manifest rows in `artifacts/MANIFEST.jsonl`. No pods left; 9.07 pod-h, $4.45 of $10.

GUIDED-TTS DONE 2026-10-03T21:48:15Z


# STATUS — create-or-elicit (proposal 27: the experiments for "Did RL create it?")

Brief: run brief `create-or-elicit` (Dan, 2026-10-11). Policy: AGENT_POLICY.md. Budget $140 / 300 pod-hours; hard stop 2026-10-17 05:14 UTC.

## create-or-elicit
- 2026-10-12 05:14 UTC  run started (executor).
- 05:52 UTC  Knockout set K12⁻ built on the VPS (`coe/coe_assemble.py`): K12 minus the 16,961 records whose DN cites a derived double negation (16,703 σ + 258 indirect), refilled per length from K12's own unused source records; 155,000 records, refill Lean check pending (first pod). Families: 6 classical, 136 trained / 123 held-out key-step members, all σ-covered. Pre-registration `preregistration/create-or-elicit.md` committed before the first pod; `podbudget` set to 300 h / $140.
- 06:12 UTC  11 pods up (all NVIDIA A40 SECURE $0.59/h, except coe-t6 RTX A6000 $0.59/h): coe-k0..k5 = knockout s0–s5, coe-f3..f5 = full s3–s5 (each: Stage 1 1,200 s → held-out greedy → 16-round T1 ladder at batch 1,024, reads beside it), coe-r0 = A40 timing (Phase 0.2) then old seeds' tracked-transfer reads and per-round analysis, coe-t6 = A6000 timing (Phase 0.2). Stage 1 ≈ 20 steps/s (≈ 24k steps). Ladders expected to end ≈ 22:00–00:00 UTC. Sub-agents: Phase 0.1 estimator analysis, Phase 0.4 claims ledger.
- 08:25 UTC  Ladders in round 2–3 (A40, 2,500–3,600 s per round). Round 1 (each base's own k 32 sample): strict σ-covered training targets solved — knockout 0 on 6 / 6 seeds, full s3–s5 17 / 15 / 20. Phase 0.1 (estimator: trustworthy in aggregate for E ≥ 10⁻⁴, a lower bound 2–4× too low below) and Phase 0.2 (same-class costs: the published K_eval-set halves under uniform allocation, doubles under adaptive; compute-matched r8 sets 34/33/33 … 21/20/14 across five budget definitions; J9 9/9 … 0/9) done; claims ledger v2 (84 entries). Pre-registration addenda 1–3 (budget allocation; strict σ-covered definition; Phase 2 design). Phase 2 under way: full s0's 33 compute-matched theorems — power sampling (α 4, α 2) 0 / 33, plain at matched tokens 1 / 33. Spend 08:25: see `podbudget create-or-elicit`.
- 11:36 UTC  Phase 2 done: sequence-level power sampling (α 4, α 2) of four bases reaches **0** of the target sets (full s0 / s1: 0 / 33, 0 / 27 compute-matched theorems; knockout s0 / s1: 0 / 106 strict σ-covered members); plain sampling at the same tokens 1–2 / 33–27 and 0 (T 0.8) / 1 (T 1.0) of 106. Knockout bases' log p of known σ proofs: median −26 to −36 nats (full base −19); the bottleneck is the step that opens the ¬G box. The knockout bases can still compose free σ at T 1.0 on one favourable theorem (≈ 10⁻⁵ per attempt; 0 / 131,072 at T 0.8). Ladders r5–r6 (55–67 min per round; end ≈ 23:00–02:00). Spend 60.93 pod-h, $35.96 (podbudget, 11:36). coe-r1 deleted.
- 14:33 UTC  Ladders r7–r9 (knockout) / r7 (full new). Knockout: 0 strict σ-covered training targets on 6 / 6 seeds; scaffolded σ proofs 30–240 per round; positive-free σ only on s5 (1 in r4, 2 in r8, non-strict targets); the one generated strict held-out theorem (`la_transfer_916`, whose premise invites ¬G) solved in the transfer samples of s1 (r4) and s3 (r8) — transfer proofs are never trained on. Full s3: negated_conditional, peirce_sequent at 1.00. Phase 2b done: power sampler stable (8 vs 32 MH steps agree), and p^α reaches 0 / 17 rarely-solved theorems where plain sampling at the same tokens reaches 6–13 / 17. Spend 91.5 pod-h, $53.99; projected ≈ $115–125 at the end of Phase 1 work — the 1 % dose arm (≈ $30) does not fit; a cheap Phase 3a (one EI round seeded with the knockout's own σ proof, ≈ $3) will be pre-registered after the ladders.
- 20:40 UTC  **Budget extended by Dan to $190 / 330 pod-h (answer 15:23 UTC, seen 20:31).** 1 % σ dose arm (Addendum 5) launched: coe-d0, coe-d1 = dose1 s0, s1 (A40; Stage 1 → 16-round ladder → reads → post job); dose1 s2's pod could not be created (A40 out of stock) — retrying every 10 min for an hour, else it runs on coe-k3 after that pod's post job. Knockout s3 finished 16 rounds; others at r14–r15. Knockout s1: free positive reductio spreading since r12 (1 → 2 → 5 → 10 per round), 3 strict targets by r13. Spend $89.19 at 20:30.
- 2026-10-13 03:28 UTC  **Phase 1 headline (pre-registered test, UNREVIEWED):** at r16, strict σ-covered held-out members solved full 42 / 75 / 77 / 65 / 23 / 33 vs knockout 0 / 2 / 1 / 0 / 0 / 2 of 106; ≥ 1 classical family acquired on 6 / 6 full seeds vs 0 / 6 knockout seeds — Boschloo p = 2.4 × 10⁻⁴ → **"needs exposure"** (contraposition_conv 6 vs 0, Holm 0.0015; three families 3 vs 0, Holm 0.17; excluded middle 1 vs 0). Yet 5 of 6 knockout ladders discovered the free reductio on their own (1–34 proofs in 16 rounds vs 17k–50k in the full arm), and knockout s1's spread slowly from r9 (5 strict targets by r16). Running: guided / redraw reads, certificates, compute-matched reach, Phase 3a, knockout s1 to r24, the 1 % dose arm (r3–r4). coe-r0 deleted.
- 16:48 UTC  **Final results (UNREVIEWED; `run_create_or_elicit.md`, `numbers.md` § create-or-elicit, `claims_ledger.md` v3 L85–L101).** (1) Pre-registered verdict **"needs exposure"**: families acquired 6 / 6 full vs 0 / 6 knockout seeds at r16 (Boschloo p = 2.4 × 10⁻⁴), robust to redraw and guided reads; knockout bases lose nothing off σ (held-out greedy without σ 0.950 vs 0.957). (2) **1 % σ dose restores acquisition** on 3 / 3 seeds (58 / 39 / 30 of 106 held-out members; exploratory vs knockout p = 0.0033). (3) Rare, not absent: 5 / 6 knockout ladders wrote the free reductio themselves; 4 / 6 knockout bases reach family members at ≈ 10⁻⁶ per attempt (2 / 6 certified out of reach at K_train(16)); knockout s1 continued to r24 kept the same 5 / 106 members, only solving them more often; RL never raised the knockout models' log p of known σ proofs. (4) Power sampling of the bases reaches none of what RL creates at matched compute (and 0 / 17 rare base solves vs plain 6–13). (5) The compute-matched "created" sets move with the budget (34 / 33 / 33 → 21 / 20 / 14; robust core 18 / 17 / 8). Phase 3a (one seeded round): no effect (1 / 5 seeds). Replay check passes on 6 / 6 knockout seeds; offline Lean re-check 1,062 / 1,062 accepted, 1,062 / 1,062 goal-negated rejected. **Spend $182.50 / 309.34 pod-hours** (budget $190 / 330 h); all 16 pods deleted. Not run: the 0.1 % dose arm (costed first in `next_steps.md`). Figures: `figures/coe_{estimator,budget,phase2,rounds,endpoint,logp}.{pdf,png}`.

CREATE-OR-ELICIT DONE 2026-10-13T17:39:11Z

# STATUS — kalmar-pretrain (proposal 29)

Brief: nd-rl `docs/proposals/state-env/BRIEF_kalmar-pretrain.md`. Policy: `AGENT_POLICY.md`. Run id: kalmar-pretrain.
Pods `kal-*` (`~/pods.log` is host-wide). Budget $50 (pod-hours advisory, 300 h; Dan 2026-10-19 03:24).

## kalmar-pretrain
- 2026-10-19 01:20 UTC  run started (executor). K12-Kalmár builder (`kalmar/kalmar.py`, `kalmar/build.py`) written and
  measured on the VPS before any pod: shared-lemma variant (primary) 110 lines / 111 actions / 21.9 k training tokens
  per proof on average (K12: 7 lines, ≈ 0.7 k), 0 / 2,000 decompose failures, Lean 200 / 200. Pre-registration
  `preregistration/kalmar-pretrain.md` committed before the first pod.
- 2026-10-19 02:25 UTC  Full K12-Kalmár built (155,000 records, 0 failures; 16.9 M (state, action) pairs, 108.9 actions per
  proof). Six community RTX 3090 pods ($0.22/h each): `kal-1` KAL-C s0 → s1 → s2 + the full Lean check of the training
  set; `kal-2/3/4` KAL-D s0/s1/s2 (656,285 steps = 3.675 epochs, ≈ 11.6 h each, ends ≈ 14:00 UTC); `kal-5` control
  read-outs; `kal-6` KAL-C read-outs. KAL-C s0 done (0.13 epochs, val 0.018).
- 2026-10-19 12:30 UTC  Full K12-Kalmár Lean check 155,000 / 155,000. Control and KAL-C read-outs complete (3 seeds each).
  KAL-D s0 / s2 trained (3.68 epochs, ≈ 10 h on a 3090 each); s1 finishing. First KAL-D numbers (s2): teacher-forced
  agreement 95.0 % (KAL-C 93.5 %, control 29 %), greedy tf1200 valid 35.6 % / exact-Kalmár 16.3 % — far below the
  pre-registered ≥ 99.5 % / ≥ 75–98 %. Running: KAL-D greedy + sampled reads, the EI ladder (Addendum 1) and its
  frozen arm on five A40s. Dan (03:24): $50 is the limit, hours advisory, EI ladder approved. Spend ≈ $15.
- 2026-10-20 09:31 UTC  **Final results (UNREVIEWED; `run_kalmar_pretrain.md`, `numbers.md` § kalmar-pretrain,
  plain summary `run_kalmar_pretrain_plain.md`).** (1) Pre-registered: KAL-D (Kalmár-proof pretraining, 3.68 epochs)
  did **not learn** the construction (TF agreement 94.5 %, greedy 32.6 % valid / 14.7 % exactly Kalmár) and **did not
  generalise** (G1(b), G2, hand_proved_14, ≥ 17; G3 partially), far below the K12 control (plain pass@32 holdout250 33
  vs 165). (2) EI ladder (Addendum 1, KAL-D s0, 3 rounds): targets 135 → 572 → 668 of 1,000 (frozen 119–146 per
  round); "keeps the algorithm" not met, "finds shorter proofs" met, both equally true of frozen sampling.
  (3) Exploratory (Addendum 3): the ladder's replay-only fine-tune (KAL-D+A: 600 steps, AdamW, 128 proofs per step,
  lr 3e-4 → 3e-5; 1.6 B tokens) gives TF 98.7–98.8 %, greedy 71–79 % valid, and solves 578 targets: the EI jump is
  that fine-tune, not RL. Greedy it matches the control on holdout250 (36.7 vs 38.1 %); plain pass@32 it trails there
  (136 vs 165) and leads on textbook72 (41 vs 24), G3 (56 vs 13), G1, ≥ 17, long2, candidate_v0. Still not "learned";
  learning rate, batch and optimizer not separated (`next_steps.md` 1). (4) The K12 control solves 177–191 / 200
  four-/five-premise problems at k 32 once the environment writes the premise lines. **Spend $46.04 / 101.69
  pod-hours** of $50; all pods deleted. Two independent claim checks (log 18:10, 05:53); all findings fixed.

KALMAR-PRETRAIN DONE 2026-10-20T09:39:51Z

# STATUS — kalmar-complexity (proposal 31: how many bits is Kalmár's construction, and which measure predicts difficulty?)

Brief: nd-rl `docs/proposals/state-env/BRIEF_kalmar-complexity.md`. Policy: `AGENT_POLICY.md`. Run id: kalmar-complexity.
Budget $15 / 40 pod-hours; hard stop 2026-10-23 12:20 UTC. Pods (if any) `kc-*`.

## kalmar-complexity
- 2026-10-20 12:20 UTC  run started (executor). Read kalmar-pretrain's run doc, review (§Recount, §Verdict), builder,
  data README, `tt_prover.py`, the proposal, lit-review-2's EDL note; checked what kalmar-pretrain logged (B1: train
  loss every 600 s for KAL-D, a mean of every 20th step; the control's curve is only inside its checkpoints).
- 12:30 UTC  pre-registration `preregistration/kalmar-complexity.md` committed before any pod, program or B1 number.
- 13:55 UTC  Python programs, explicit policy (exact), decision tree (626 bits, exact on fresh states), B1 done
  (KAL-D first-epoch code 1.25 × 10^7 bits, EDL 6.3–7.1 × 10^6; control 3.6–3.9 × 10^6 / 1.5–1.7 × 10^6). Pods
  `kc-1`, `kc-2` (A40, $0.59/h each) running B2; B1-snap done. BLC and RASP-L agents running; literature done.
- 17:20 UTC  **Final (UNREVIEWED; `run_kalmar_complexity.md`, `numbers.md` § kalmar-complexity, plain summary
  `run_kalmar_complexity_plain.md`).**
  - (1) Kalmár's construction (K-sl) is 5,443 bits of binary λ-calculus, 864 B of compressed Python (algorithm only).
    End to end it is 6.9–11.6 kbit. RASP-L per-step policy: 492 ops, attention depth 41. Decision tree: 626 bits over
    21 features. It is the largest of 9 calibration algorithms in every language (ranks agree, ρ 0.86–0.97).
  - (2) KAL-D absorbed 6.3–7.1 × 10^6 bits in its first epoch (≈ 1,200× the program); B2's small models absorbed
    1.1–1.5 × 10^6 per 16,384 theorems.
  - (3) Per-step computational demand predicts where KAL-D fails (RASP-L depth ρ +0.85, lookups +0.82, also within
    step types); program length does not (−0.08 given frequency).
  - (4) B3 (causal, pre-registered addendum 2): handing the model the search result cuts opener-step error 94 %
    (32 → 1.9 %, 3 paired seeds).
  - Spend $5.00 / 8.46 pod-hours of $15 / 40; all pods deleted.

KALMAR-COMPLEXITY DONE 2026-10-20T17:19:51Z

# STATUS — style-edl (proposal 32: does EDL rise with proof style when capability is fixed?)

Brief: nd-rl `docs/proposals/followups/BRIEF_style-edl.md`. Policy: AGENT_POLICY.md. Run id: style-edl. Budget $10 / 40 pod-hours.

## style-edl
- 2026-10-23 03:18 UTC  run started (executor). 2026-10-23T04:05:27Z  S_own pilot (VPS CPU, seed 0 only) done; pre-registration
  `preregistration/style-edl.md` committed before any pod.
- 2026-10-23 04:06–08:05 UTC  three pods, all deleted (sedl1 / sedl2 secure RTX A5000 $0.27/h, sedl3 secure A40 $0.59/h for
  8 min to redo one guided read that had run out of memory). Spend **$1.86 / 6.72 pod-hours of $10 / 40**.
- Result (pre-registered verdict: **against**).
  - Capability-preserving alternative styles barely differ from the learner's own on these theorems: identical proofs on
    85–94 %. Their EDL_c is within the 0.1-bit floor of S_own2's (0 of 9 seed × stream cells above it).
  - The brief's EDL flags S_short (+0.74 to +0.92 bits per proof), but that is the stream / test split (EDL_c and a
    cross-fit remove it).
  - Kalmár proofs cost 177–182 bits per proof of EDL_c, but training on them drops pass@32 from 1.00 to 0.25–0.38: not
    at fixed capability.
  - ℓ_V makes Kalmár's EDL negative and shows a small transient for S_short.
- Deliverables: `run_style_edl.md`, `run_style_edl_plain.md`, `numbers.md` § style-edl, `figures/style_edl.png`,
  `style_edl/` (`results.csv`, `streams_manifest.json`, `README.md`), `log.md` § style-edl; bucket
  `hf://buckets/dan-pandori/nd-rl/style-edl/`.


STYLE-EDL DONE 2026-10-23T08:22:24Z
