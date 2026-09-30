# grpo-state (code phase): GRPO in the proof-state environment

**Built.** `grpo_state.py`: groups of G rollouts per theorem from the same start state. Reward 1 iff Lean accepts
the literal assembled proof. Every sampled action, including a failing last one, carries its rollout's advantage.
The loss is the policy gradient on action tokens given the state, using log-probs of the sampling distribution
(logits / T), plus an optional k3 KL to the initial policy. `grpo_adv.py` puts four advantages behind `--adv`:
- `default`: R − mean.
- `unlikely`: He et al. §4.1, β_rank 0.25.
- `passk`: Chen et al.'s analytic pass@k, PKPO-equivalent.
- `distinct`: a bonus for proofs new to the theorem.

The budget and outputs match `state_ladder_ei.py` (round-equivalents, `found_<r>`, `found_transfer_<r>`,
`round_<r>.json`, registry rows, compute rows per phase and round), so EI read-outs apply unchanged.
`state_sample.py` is untouched.

**Tested.**
- CI (`ci/run_ci.sh`, GitHub Actions, green):
  - Advantages on hand-made groups. pass@k matches brute force over all k-subsets, and k = 1 equals the default.
  - Trajectory replay: the recorded state ids reproduce.
  - The gradient equals autograd of −Σ A log π, including at T = 0.8, and does not depend on chunk size.
  - A = ±1 moves log π the right way, and KL = 0 when the reference equals the policy.
  - A tiny CPU run of every variant produces Lean-accepted found proofs and compute rows.
- GPU smoke, on SN-cap12 s0 with an RTX 3090 (`numbers.md` § grpo-state):
  - 19.5 s per update alone at 256 × 8 rollouts; peak 8.6 GB.
  - Two jobs per card give 1.47× throughput.
  - Base reward is ≈ 0.46, and ≈ 0.6 of groups are mixed. This is above my pre-registered E5, as Addendum 1 records.
- Second GPU smoke (A40, after the review fixes): the boundary-evaluation path runs on subsets. See `log.md`.

**Experiment**, not run: `preregistration/grpo-state.md`.
- Arms: EI and GRPO default / unlikely / pass@4 on SN-cap12.
- Read-outs: `transfer_long2`, the long pool, and support-curves-style base-unreached counts.
- Cost: the brief's 6 seeds come to ≈ $37–43, because only s0–s3 exist. Plan B (4 seeds) is ≈ $24.
- Default in `QUESTIONS.md`: Plan B.
