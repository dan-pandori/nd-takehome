# Pre-registration: lit-measures (three cheap measurements from the literature review)

Run `lit-measures`, branch `dan_lit-measures` (fork, from `origin/dan`). Executor, 2026-09-30. Budget **$3, ceiling 6
pod-hours** (`podbudget lit-measures`: 6 h / $3). Judge: Lean alone; no part of this run calls `nd_verify`. Logs are
natural logs (nats) throughout. The three parts are independent; one failing does not stop the others.

## M1. Where the state base finds EI's new proofs improbable (no sampling, forward passes only, VPS CPU)

**Models** (support-state's labels): SN base s0 = state-env `ckpts/se/stage1_SN_s0.pt` (md5 `ec3888d9`, 3,216,384
params, `lean_staten`, from scratch on `data/p2/train_depth3_f0_a1.jsonl`, 6,000 × 128, cap 6); SN EI s0 =
`la_T1_SN_s0_r8.pt` (`fb448247`; its proofs only are used, from support-state's records).

**Sets.** S = every distinct accepted SN EI s0 proof, from support-state's S1/S2 records, of the 7 theorems SN base s0
does not reach at 200,000 attempts per temperature (`1108 1185 1352 198 2089 394 988`). C1 (controls, as part D's C1) =
distinct SN EI s0 proofs of theorems SN base s0 does reach (S1 or S2), restricted to `L_true` 7–11 and, per `L_true`,
sampled to at most 5 theorems per S theorem (length-matched; seed 0). C2 = SN base s0's own accepted proofs of the
same C1 theorems. **Score**: each action's log p under SN base s0, conditioned on the state the environment shows at
that step (`Env(canon=True, assign=True)`, the names the environment assigns — no name marginalisation needed), summed
over the action's tokens incl. its terminator. Per proof: total, worst step w1, second-worst w2, rest (total − w1 − w2),
s1 = w1 / total, s2 = (w1 + w2) / total; label with part D's rule and cut-offs (`sf_d_analysis.label`). Primary unit:
the best (highest total log p) EI proof per theorem, as part D.

**Expectations / falsifiers.**
- E1.1 ≥ 5 / 7 S theorems labelled concentrated. Falsified if ≤ 3 / 7.
- E1.2 (degree) median w1 of S is ≥ 2 nats below C1's median w1; one-sided permutation test (theorem-level, best
  proof each, 100,000 permutations) p < 0.10. Falsified if S's median w1 is above C1's. (n = 7: low power; stated.)
- E1.3 (Invisible Leash App. C.4) fraction of S with w1 < ln(3 / N): N = 400,000 (both temperatures pooled; −11.8)
  ≥ 4 / 7; also reported at N = 200,000 (−11.1). The same fraction is reported for part D's 29 (from
  `artifacts/sf/d_summary_T08.json`, WP base, N = 400,000); not a prediction, a recount.

## M2. Initialisation seed vs data-order seed (pods)

**Code**: `train.py --data_seed` (default = `--seed`): `torch.manual_seed(seed)` → init only (the model has no
dropout); data order + per-step name-shift draws ← `data_seed` (legacy `random.Random`, fast `plan`/`draw`).
CPU test `tests/test_data_seed.py` passes (default == explicit, both factors change the trajectory). On the pod:
new code with the default vs `origin/dan`'s `train.py`, legacy and `--impl fast`, 300 steps: per-step losses must be
identical; and a full legacy 6,000-step run of `--seed 0` on `train_p1` compared with noise-floor's `stage1_p1_s0` log.

**Deviation from the brief's 3 × 3 grid → 8 × 8.** A simulation (two-way random effects, bootstrap over both factors'
levels) gives a degenerate interval at 3 × 3; at 6 × 6 the data-share 95 % interval spans ≈ [0.05, 0.83] for a true
share of 0.5; at 8 × 8 ≈ [0.12, 0.75] with 95 % power to exclude 0. 64 cells at `--impl fast` (≈ 2 min train +
≈ 1 min eval each) ≈ 3.5 GPU-h ≈ $1–1.5. **Recipe** = noise-floor's control: `train.py --mode lean_seq --steps 6000
--bs 128 --cap 6 --impl fast` on `data/nf/train_p1.jsonl` (155,000 records, depth-3 excluded), init seeds 0–7 ×
data seeds 100–107 (disjoint from init seeds so no cell is "seed = data_seed" by accident). **Read-outs**: `eval_set.py`
held-out greedy (`data/p2/heldout.jsonl`, 5,000; default batch, peak memory recorded) overall and depth-3 slice (500),
and final validation loss. **Analysis**: two-way crossed ANOVA variance components (init, data, residual incl.
interaction), share of each with a two-way bootstrap (resample init levels and data levels, 2,000 draws) 95 % interval;
per-cell table. Mode: high = depth-3 ≥ 0.5; report the high-mode count by row (init) and by column (data), and the
χ²/Fisher-type permutation test of row vs column concentration.

**Expectations / falsifiers.**
- E2.1 data order carries ≥ 30 % of the depth-3 variance (point estimate). Falsified if the interval's upper bound < 30 %.
- E2.2 depth-3 mode follows the data order more than the init (data share > init share). Falsified if init share >
  data share with non-overlapping intervals.
- E2.3 (check) the 64 cells' depth-3 spread resembles noise-floor's 52 legacy cells (sd ≈ 0.3, range ⊇ [0.1, 0.8]).
  If sd < 0.15 the fast path does not reproduce the bimodality and M2 answers a different question (reported as such).

## M3. Mode shares round by round (files only; heavy download on a pod)

**Runs**: every EI ladder with per-round `found_<r>.jsonl` in the bucket whose family has ≥ 2 seeds of the same arm:
whole-proof `la_T1_*` of `ladder-A`, `ds-composition`, `ds-generator`, `lean-format`, `lean-seed2`, `support-curves`;
state `la_T1_*` of `state-env`, `state-frontier`, `state-cap12`; `round3-run4b` `ei_depth3_*`. Frozen ladders (no
training) are reported as the no-RL reference. **Per seed and round**: of the proofs newly found that round (`round`
field), the share by maximum box depth (0, 1, 2, ≥ 3) and the rule mix (share of each rule over all steps).
**End mode** of a seed = its final-round share of depth-≥ 3 proofs among all found proofs; within each (family, arm),
the seeds are ranked by it. **Separation at round r** = the seeds' ordering on the same share at round r agrees with
the final ordering (pairwise, within arm).

**Expectations / falsifiers.**
- E3.1 modes separate by round 2: pairwise agreement at round 2 ≥ 75 % over all within-arm seed pairs. Falsified if
  ≤ 60 % (chance is 50 %).
- E3.2 the depth-≥ 3 share moves monotonically with rounds in at least half the ladders (amplification of one mode);
  reported, not a headline.

## Stop rule

Stop M2 at 64 cells or at 5.5 pod-hours / $2.75, whichever first; M3 pod job at 1 pod-hour. Never more than 4
processes at once on the VPS. Pods deleted when their files are pulled and md5-matched.
