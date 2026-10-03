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
