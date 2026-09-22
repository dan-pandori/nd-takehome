# Pre-registration — run `lean-seed2` (second Stage-1 seed for `lean_seq` on the ladder rung, after the BOTE fix)

Written 2026-09-22 ≈ 05:45 UTC, before any pod exists for this run. Executor: agent:claude. Branch `dan_lean_seed2`
(worktree from `dan_lean_format`). Brief `BRIEF_LEAN_SEED2.md`; policy `AGENT_POLICY.md`. Run start 05:31 UTC.

## Question

Proposal 8's "result that would matter" — transfer `L*` = 11 on the ladder rung (token format: 10 / 10) — rests on **one**
`lean_seq` Stage-1 model (seed 0) with two EI seeds. Does a second, independently trained Stage-1 model (seed 2) reproduce
it? Secondary: held-out accuracy and the mechanism numbers (7- / 8-line proofs at pass@16) for the second model.

## Step 1 — done before this file (commit 39bdc5b, 05:43 UTC)

`nd2lean.py` and `lean_tok.py` render BOTE as `False.elim nA` (was `nA.elim`, which Lean resolves to `Not.elim` on a
negation). 460 known "Lean yes, `nd_verify` no" texts re-checked: the 206 `.elim` cases are now rejected by Lean; 137
`¬A ≡ A → False` cases remain Lean-accepted (not closable in the translator); 117 unrestated-premise cases are structural
rejections in `nd2lean --check` but still inside the training-format grammar (`lean_tok.inverse` does not know the
premise count — unchanged here, harmless because a sample counts only if both checkers accept). 20,000 / 20,000 sampled
pool proofs (684 with BOTE) agree under the fixed checker of record. Details: `log.md` § lean-seed2.

## Design I will run

Identical to proposal 8's ladder arms except the Stage-1 seed (`pod/lf/jobs.py`, role `ladder`, scheme `seq`):

1. Stage-1 `lean_seq` on `data/train.jsonl` (154,990 cap-6 proofs), 4 layers, d 256, 8 heads, vocabulary 107, 6,000 steps,
   bs 128, lr 1e-3 → 1e-4, warm-up 200, **`--seed 2`** → `ckpts/lf/stage1_full_seq_s2.pt`. Held-out greedy on
   `data/heldout.jsonl` (5,000); pass@16 (T 0.8, seed 0) on `data/transfer.jsonl` (1,638) — the mechanism test.
2. Ladder rung T1 (`ladder_ei.py`, 8 rounds, k 32, T 0.8, `max_new` 512, 600 fine-tune steps at 3e-4, retain 20,000,
   ≤ 4 proofs per theorem × 4, `--batch 512`) from that checkpoint with **EI seeds 0 and 1** (the protocol of proposal 8,
   where both EI seeds came from the one Stage-1 model), pools `data/ladder/{rl_targets,transfer}.jsonl` (4,495 / 2,285),
   and the frozen controls (`--no_train`) with seeds 0 and 1 at equal attempts.
3. Checker: Lean in the loop on every distinct grammar-valid sample (`lean_gate.py`, 2 × 2 table logged per call) and,
   at the end, the fixed `nd2lean.py --check` + `nd_verify` on every counted proof (`pod/lf/record.py`). A proof counts iff
   both accept. `L*` = max L with ≥ 5 transfer theorems solved at `L_true` ≥ L (`lean_format_analysis.lstar`, unchanged).

**Deviation from "identical" that I know of:** the seed-2 model is trained on the fixed BOTE rendering (`False.elim nA`),
seeds 0 / 1 on `nA.elim`. BOTE occurs in 1.9 % of training proofs and in **0** of the 44 `L_true` ≥ 11 transfer proofs seeds
0 / 1 found (31 / 82 of all their found transfer proofs), so I do not expect it to move `L*`; it is stated so that a
difference cannot be blamed on it silently.

Pods: two RTX 3090 (`ls2-1`: Stage-1, held-out, pass@16, T1 s0 + frozen s0; `ls2-2`: T1 s1 + frozen s1 from the copied
checkpoint) — same pod-hours as one pod with four arms, half the wall-clock.

## Expected results (numbers; token / seed-0 values on file in `numbers.md` § lean-format)

| # | quantity | on file (`lean_seq` Stage-1 seed 0) | expectation for seed 2 |
|---|---|---|---|
| E1 | Stage-1 held-out greedy, `data/heldout.jsonl` | 0.936 (token 0.948; band ≥ 0.928) | 0.925–0.945; P(≥ 0.928) ≈ 0.8 |
| E2 | transfer `L*` at round 8, EI seeds 0 / 1 | 11 / 11 (token 10 / 10) | **11 / 11 with P ≈ 0.55**; at least one 11 P ≈ 0.75; 10 / 10 P ≈ 0.2; ≥ 12 in either seed P ≈ 0.1 |
| E3 | transfer theorems solved at `L_true` ≥ 11 | 12 / 13 (token 1 / 0) | 6–20 per arm |
| E4 | transfer solved / 2,285 at round 8 | 794 / 839 | 700–900 |
| E5 | frozen control, transfer `L*` and solved | 10 / 10; 304 / 309 | 10 (P ≈ 0.8; 9 P ≈ 0.15); 250–350 solved |
| E6 | pass@16 on `data/transfer.jsonl`; distinct proofs of written length 7 / 8 | 0.571; 266 / 130 (token `abs` 0.447; 108 / 1) | 0.53–0.60; 200–320 / 90–170 |
| E7 | in-loop "Lean yes, `nd_verify` no" | 33 per million (206 `.elim` + 137 + 117 of 13.9 M) | **0 of the `.elim` kind**; ≤ 25 per million in total, all `¬A ≡ A → False` or unrestated premises; 0 "`nd_verify` yes, Lean no" |
| E8 | checker of record on every counted proof | 41,840 / 41,840 | all counted proofs both-accept, 0 disagreements |
| E9 | ladder round time, 2 arms per 3090 | 27–36 min at 4 arms | 12–22 min |

**Statement I will make at the end.** "`L*` = 11 rests on two Stage-1 models" iff both EI arms of seed 2 reach transfer
`L*` ≥ 11 at round 8 (E2). If one of the two does, it is "two models, three of four arms"; if neither, "one model", and the
result is reported as not reproduced, with the `L_true` ≥ 11 counts side by side.

## Budget and stop rule

- Pods: **$10** (two RTX 3090 at ≈ $0.50 / h, planned ≈ 6 pod-hours ≈ $3). Ask in `QUESTIONS.md` before exceeding $10.
- Hard stop 20 h after start: **2026-09-23 01:31 UTC**. Pods deleted as soon as their files are pulled.
- Stop and report if the Stage-1 held-out greedy is < 0.90 (a broken training, not a seed effect) or a ladder round takes
  > 3× the on-file 4-arm time (> 108 min).
- Nothing beyond this run is launched (the pause stands). No test-file run. `nd_verify` unmodified. No hand- or LLM-written
  training proofs: every supervised record is a generator proof rendered deterministically by `lean_tok.py`; the cap
  (≤ 6 lines) is asserted on the ND record.
