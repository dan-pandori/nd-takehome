# Review — mcts-b (reviewer, 2026-10-03)

## §Recount (phase 1, blind to the executor's write-ups)

mcts-b is conditional on `mcts-a`'s gate (brief `nd-rl/docs/proposals/state-env/BRIEF_mcts-b.md`, §"First: check the
gate"). If the gate failed, or the reviewer did not let it stand, the brief says: run no pods, write a ≤ 150-word
`run_mcts_b.md`, add `MCTS-B DONE <UTC> (not run: gate)`. There is no `preregistration/mcts-b.md`. None was due, because
the brief asks for one only "before the first pod". So the one quantity to re-derive is the gate.

**Gate, recounted from `origin/dan_mcts-a:artifacts/mcts/eval/s{0,1,2}_r8__C__{value,sample,prior}.json`**. I applied
the rule in `origin/dan_mcts-a:preregistration/mcts-a.md` §Gate myself: PASS iff Δ_s ≥ 3 on ≥ 2 of 3 seeds, and also
above the re-draw spread.

Model: `trajectory` cap-12 r8, `ckpts/mcts/la_T1_best12_s{s}_r8.pt` (ALiBiGPT 9.56 M, `lean_staten`, from scratch on
K12, then T1 EI). GPU: A40. Group C: `data/mcts/groupC_s{s}.jsonl`. Sampling: k 256, T 0.8, seed 2, batch 2048.
Search budget = the sampling read's `wall_s`.

| seed | n (group C) | PUCT + value | sampling | Δ_s | PUCT prior only | budget s |
|---|---|---|---|---|---|---|
| s0 | 36 | 2 | 4 | −2 | 2 | 131.4 |
| s1 | 35 | 2 | 2 | 0 | 1 | 160.4 |
| s2 | 28 | 3 | 4 | −1 | 3 | 75.3 |

On 0 of 3 seeds is Δ_s ≥ 3, so **the gate FAILS**. Δ ≤ 0 on every seed, so mcts-a's falsifier also fires. The mcts-a
reviewer (`origin/dan_mcts-a:review_mcts-a.md` §Verdict) lets "MCTS-A GATE: FAIL" stand. They re-checked all 6,700 search
proofs and 2,333 sampled proofs in Lean 4 core. Under the brief, Phase B therefore must not run.

**What the run did** (`git diff origin/dan...HEAD`): it touched 2 files, `STATUS.md` (+6) and `run_mcts_b.md` (+14). It
added no code, data or artefacts.
- Pods: `podbudget mcts-b` shows 0.00 h, $0.00 of $45 / 90 h. No `mcts-b` entry in `~/pods.log`.
- Counted proofs: none, so there are no Lean re-checks to do (the ≥ 100 per arm requirement is vacuous), and no
  term sizes, splits or compute rows to re-derive.

**Hard constraints.**
- `nd_verify/` is identical to `origin/main`'s (`git diff --quiet origin/main HEAD -- nd_verify`).
- `nd_verify` is not used as a judge: the run added no code.
- `artifacts/TEST_RUN_DONE` is unchanged from `origin/dan`.
- No training code was added, so no evaluation file is read in training. `test_run_once.sh` was not run.

No violation.

## §Compare (phase 2: `run_mcts_b.md`, the `STATUS.md` § mcts-b lines)

The brief's not-run branch asks for no `numbers.md` § mcts-b and no `log.md` entry, and the run added neither.
`run_mcts_b.md` is 142 words, within the ≤ 150 limit.

| Claim | My value | Verdict |
|---|---|---|
| `MCTS-A GATE: FAIL`, reviewed and left standing | FAIL (0 of 3 seeds with Δ ≥ 3); mcts-a reviewer: "Stands" | reproduces |
| Group C r8, PUCT + value vs sampling: 2 vs 4, 2 vs 2, 3 vs 4 (Δ −2 / 0 / −1) | 2/4, 2/2, 3/4; Δ −2 / 0 / −1 | reproduces |
| "at matched GPU-seconds" | search `budget_s` = sampling `wall_s` (131.4 / 160.4 / 75.3 s), same A40 | reproduces (it is wall clock on the same GPU class, which the mcts-a reviewer accepted) |
| Model: `trajectory` best-cap12 s0–s2, 9.56 M, `lean_staten`, from scratch on K12 | `la_T1_best12_s{s}_r8.pt`: from scratch on K12, **then 8 rounds of T1 EI** | reproduces, but the label is incomplete (see wording 1) |
| No pod, $0 | `podbudget mcts-b`: 0.00 h, $0.00; no `pods.log` entry | reproduces |
| Suggestion 1: score the r8 value heads on group-C states | the mcts-a reviewer's "next measurement" 1, which the run restates correctly | reproduces (it is a proposal, not a claim) |
| Suggestion 2: search helped at end of pretraining on long proofs (rrQ100 +14.3) | mcts-a reviewer: pend rrQ100 +19 / +10 / +14, 3 of 3 seeds; STATUS CI +9.7 to +19.3 | number reproduces; the label and the attribution need wording (see wording 2) |
| "the gap EI already closes" | mcts-a at r8: every pool within ±3 for PUCT + value | interpretation; consistent with the evidence, not measured directly |
| Suggestion 3: a re-gate needs several draws or a ≥ 150-theorem pool | the mcts-a reviewer's "next measurement" 2 | reproduces |
| `MCTS-B DONE 2026-10-03T05:50:23Z (not run: gate)` | `executor.done` exists; the driver logged the executor done at 05:52:13Z | reproduces |

Expectations and gate 0: the brief requires a pre-registration only before the first pod. No pod was created, so none
was owed. No miss was hidden. Nothing compares numbers across the 2026-09-27 checker change: every number here is from
mcts-a, after that date, and judged by Lean alone, as the write-up says.

## §Verdict

**Stands.**
- The gate failed and its review stands, so not running Phase B was correct and is what the brief prescribes.
- The run spent no pods and no money and changed no code, data or artefacts.
- The hard constraints hold: `nd_verify` is identical to `origin/main`'s and unused, `TEST_RUN_DONE` is unchanged, and
  no evaluation file is read in training. No quarantine.

**Should be reworded** (minor; none changes the conclusion):
1. Model label: "from scratch on K12" should read "from scratch on K12, then T1 EI to r8"
   (`la_T1_best12_s{0,1,2}_r8.pt`). As written, the checkpoint reads like the end-of-pretraining one.
2. Suggestion 2: name the checkpoint behind "end of pretraining" (mcts-a's pend, `trajectory`'s
   `stage1_best12_s{0,1,2}_b1200.pt`) and the pool (rr600 L13–16 / rrQ100).
   - Say "PUCT search", not "a value-guided expert". Per the mcts-a reviewer, the value adds only +5.3 [+0.7, +10.0] of
     the +14.3; the rest comes from the search with the prior alone.
   - "The gap EI already closes" is an interpretation of r8's within-±3 result and should be marked as one.

**Not supported.** Nothing.

**Next measurement.** The same as mcts-a's: AUC of the r8 value heads on group-C partial proofs, taken from the 10×
sampling read's states. Before any Phase B, also run a compute-matched search-vs-EI comparison at pend / early rounds.
