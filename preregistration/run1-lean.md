# Pre-registration — run1-lean (ND → Lean 4; in-context surface forms; novelty by model scale)

Written 2026-09-17 23:00 UTC, before any pod of this run was created. Brief: `BRIEF_RUN1_LEAN.md`
(proposal 1 of round 2). Policy: `AGENT_POLICY.md`.

## Question

Is what RL found in the take-home's token format "genuinely new" relative to *general* pretrained
capability, or only relative to the small model's own prior? Two handles: (1) the same theorems in a
surface form pretrained models know (Lean 4) versus the take-home token format, in-context, on one
30B instruct model — does the surface form move accuracy, and by how much per length; (2) for the
RL-found proof classes, the smallest Qwen3 instruct scale that proves the theorem in Lean, compared
with the Phase-1 base-model log-probabilities of the RL-found proofs.

## Design actually run

**Step 1 — `nd2lean.py`.** Deterministic translation of a spec.md proof into a Lean 4 term-mode
proof (`theorem … (P Q R S : Prop) (h1 : prem1) … : concl := have-chain`). Atoms → `Prop`
variables; `F` → `False`; `~` `&` `v` `>` → `¬ ∧ ∨ →`; premises → hypotheses; rules: `ANDI` →
`And.intro`, `ANDE1/2` → `.1/.2`, `IMPE` → application, `IMPI` → `fun h => …` (the box as a named
`have b_s : A → E := fun n_s : A => …` emitted when the box closes), `NEGI` → the same box at type
`¬A`, `ORI1/2` → `Or.inl/inr`, `ORE` → `Or.elim`, `NEGE` → application (`n_b n_a : False`), `BOTE` →
`False.elim`, `DN` → `Classical.not_not.mp`, `R` → the cited name. Lean 4.34.0 core via `elan`, no
Mathlib. Agreement check: every proof of `data/train.jsonl.gz` (154,990), `data/heldout.jsonl`
(5,000), `targets/validation_36_reference_proofs.jsonl` (36), `artifacts/novelty_phase1_proofs.jsonl`
(12,761) and the round-2 found-proof files — `nd_verify` accepts ⇒ Lean accepts. The converse
direction uses *rejected* proofs: single-edit mutations (one citation, rule name, formula token or
depth bar changed) of 2,000 valid proofs, run through both checkers, disagreements classified by
cause with an example each. A proof "Lean accepts" iff `lean` exits 0 with no `sorry`/`admit`
warning and the source contains no `sorry`, `axiom`, `by`, `native_decide`, `unsafe`,
`implemented_by`.

**Step 2 — in-context v0.** Qwen3-Coder-30B-A3B-Instruct, vLLM, one A100-80GB pod (`r1-a100`).
Theorems: validation-36 + 200 transfer theorems from `data/transfer.jsonl` (20 per generating length
7–16, seed 0) = 236. Examples: 20 verified proofs per draw — 10 from `data/train.jsonl.gz` (2 per
length 2–6) and 10 from `data/rl_targets.jsonl` generator proofs (1 per length 7–16); a draw is
re-sampled until all 14 non-`PR/AS` rules appear; 5 draws (seeds 0–4); class-disjoint from every
test theorem by construction (targets, transfer and validation are disjoint by renaming class; the
translator makes the three forms of each draw from the same 20 proofs). Forms: **lean** (term-mode
Lean 4, as above; the model completes after `:=`), **tokens** (the take-home format), **english**
(same line structure, rule names spelled out, boxes as indentation, Unicode connectives; parsed back
to tokens and judged by `nd_verify`). Decoding: greedy (T = 0) and 8 samples at T = 0.7, max 1,500
new tokens, same prompt. Metrics per form: greedy accuracy, mean sample accuracy (pass@1), pass@8,
overall and by generating-length stratum (val-36 by its `bin`), averaged over the 5 draws; the paired
Lean − tokens difference per (theorem, draw) with a 95 % bootstrap interval over theorems (theorem
as the resampling unit).

**Step 3 — novelty by scale.** Classes (from `artifacts/`): (a) depth-3 from f = 0 — theorems in
`artifacts/p2/novelty_depth3_f0_a1_s0_proofs.jsonl` whose pruned RL proof has box depth ≥ 3 (521;
a seed-0 sample of 60); (b) reductio from f = 0 — all 88 theorems in
`artifacts/p2/novelty_reductio_f0_s0_t2_proofs.jsonl` whose pruned proof is `patterns.reductio`;
(c) 9-line — the 60 theorems of `artifacts/novelty_phase1_theorems.jsonl` (final transfer +
targets) whose shortest RL-found written proof is ≥ 9 lines. Models: Qwen3-0.6B, 1.7B, 4B, 8B, 14B,
32B (instruct; the Qwen3 non-thinking chat mode) with the same Lean prompt (draw 0 of step 2) at
k = 16, T = 0.7, plus greedy. Per theorem: the smallest scale with ≥ 1 Lean-accepted proof.
Comparison: Spearman ρ between scale-of-first-success (rank, "none" = 7) and the Phase-1 base
log-probability of the RL-found proof (`base_logp_T08_any`, own Stage-1 base model), per class and
pooled; and per-scale solve rates.

## Expected results (falsifiable)

- **E1 (agreement).** ≥ 99.9 % of verifier-accepted dataset proofs are Lean-accepted after
  translation; every failure is a translator bug fixed before step 2 (target 100 %). Of mutated
  proofs that `nd_verify` rejects, I expect 2–8 % to be Lean-accepted, almost all from Lean's
  definitional unfolding of `¬A` as `A → False` (a `NEGI` box discharged as `IMPI`, `IMPE` on a
  negation) and from bookkeeping rules Lean does not have (line numbering, box end line, `PR` order).
- **E2 (form delta).** Greedy accuracy on the 236 theorems, mean over draws: tokens 0.35–0.55,
  Lean 0.45–0.65, english within ±0.05 of tokens. Paired Lean − tokens (greedy): **+0.10**, 95 %
  interval excluding 0; by stratum, +0.05 on val-36 ≤ 6 and lengths 7–8, **+0.15** on lengths ≥ 12
  (the token form's failures on long proofs are mostly bookkeeping: bad box cites, line numbers).
  pass@8 exceeds greedy by 0.15–0.25 in every form; the Lean − tokens delta at pass@8 is smaller
  than at greedy (+0.05).
- **E3 (scale).** Monotone in scale for every class. At k = 16 in Lean: 0.6B < 0.10 on every
  class; 32B ≥ 0.60 on depth-3, ≥ 0.40 on reductio, ≥ 0.20 on 9-line. Spearman ρ between
  scale-of-first-success and the base log-probability: |ρ| ≤ 0.30 per class (the small base
  model's prior is not what limits the pretrained models); pooled across classes ρ may reach −0.4
  only because the classes differ in length. If |ρ| > 0.5 within a class, the base log-probability
  tracks intrinsic difficulty rather than the small model's data gap.

## Budget and stop rule

$50 of pods (one A100-80GB at ≈ $1.6 / h, ≈ 8–12 h expected ≈ $15–20; a second, cheaper pod only
if Lean checking or the small models are slow). Hard stop 2026-09-19 04:50 UTC; the account
killswitch is armed for 06:00 UTC on 2026-09-19. Stop early if step 2 has not produced
verified outputs for at least one draw by 2026-09-18 12:00 UTC (then report step 1 and whatever
step 3 scales finished). Steps run in order 1 → 2 → 3; step 3 is dropped first if the budget binds.
