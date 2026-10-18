- **Reproduction.** In all 12 ladders, every per-round cell is **identical to the executor's
  `artifacts/ps/rl_found.json`**: new distinct proofs, proofs with #10, working, template-only, free-working and
  neg-goal-working, rounds 1–16. The σ-covered target sets and their first rounds are identical too. 7,855,065 distinct
  proofs in all, 0 duplicate (name, proof) lines, 0 unparsable, 0 prompts that differ from `rl_targets.jsonl`. Re-running
  three ladders gives byte-identical counts.
- **Base reachability.** Round 1 is samples of the pretrained model, before any RL update. Working #10 in round 1:
  full 76 / 32 / 52, dose1 15 / 45 / 7, K12⁻ 1 / 0 / 1 / 0 / 2 / 1. σ-covered targets with a working #10 already in round
  1: full 17 / 15 / 20 (of 78 / 33 / 36 by round 16), dose1 2 / 17 / 2 (of 69 / 46 / 41), K12⁻ 0 in all six ladders (by
  round 16: 0 / 5 / 1 / 0 / 0 / 2).
- **Knockout ladders.** After RL they write working reductios: 358 / 399 / 772 / 169 / 72 / 375 in rounds 2–16. These
  are almost never `free` (0 / 32 / 2 / 1 / 0 / 12) and only ko_s2 has `neg_goal` ones (113). The rest are `scaffolded`
  with a non-immediate route, meaning the theorem supplies ¬¬G.
- **Lean re-check of counted RL proofs** (`rl_recheck.py`): reservoir samples per ladder of 120 working-#10 proofs (all
  74 for ko_s4) plus 60 any-#10 proofs, 2,114 in all (1,694 working). **2,114 / 2,114 accepted.** Two of them (ko_s0,
  ko_s5) contain a `BOTE` line that cites a *negation*, not ⊥. That is the state-env's ND decoding of Lean's `n.elim` on
  `n : ¬A`, which is valid in Lean (Lean alone decides) but not ND's BOTE. My renderer first wrote it as `False.elim` and
  rejected both. Rendered as `Not.elim` (what the env ran), both pass. Controls re-run after the change are unchanged.
  The classifier counts such a line as an ex falso instance, though it is really a reiteration. That affects ≈ 1 in 1,000
  reductio proofs in my sample.
