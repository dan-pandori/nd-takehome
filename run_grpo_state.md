# grpo-state (code phase): GRPO in the proof-state environment

**Built.** `grpo_state.py` draws G rollouts per theorem from one start state. Reward is 1 iff Lean accepts the
literal proof. Every sampled action carries its rollout's advantage. The loss is the policy gradient on action tokens
(log-probs of logits / T), plus an optional KL to the initial policy. `--adv` (`grpo_adv.py`) selects:
- `default`: R − mean
- `unlikely`: He et al., β 0.25
- `passk`: Chen et al., PKPO-equivalent
- `distinct`: bonus for new proofs

Budget and outputs match `state_ladder_ei.py`, compute rows included.

**Tested.**
- CI:
  - pass@k matches brute force, and k = 1 gives the default.
  - Trajectories replay.
  - The gradient equals autograd of −Σ A log π, including at T = 0.8, and does not depend on chunk size.
  - KL is 0 at the reference.
  - A tiny CPU run of each variant finds Lean-accepted proofs.
- GPU, SN-cap12 s0, on an RTX 3090:
  - 19.5 s per update of 2,048 rollouts; peak 8.6 GB.
  - Two jobs per card give 1.47× throughput.
  - The base's reward is ≈ 0.46 with ≈ 0.6 of groups mixed, above my pre-registered E5.
- An A40 smoke on pool subsets ran the boundary evaluations after the review fixes.
- Cost: 0.32 pod-h, $0.16.

**Experiment**, not run (`preregistration/grpo-state.md`):
- Arms: EI and GRPO default / unlikely / pass@4 on SN-cap12.
- Read-outs: `transfer_long2`, the long pool, and base-unreached support.
- Six seeds cost ≈ $37–43, since only s0–s3 exist. Plan B (4 seeds) is ≈ $24 and is the `QUESTIONS.md` default.
