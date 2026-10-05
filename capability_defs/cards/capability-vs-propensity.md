# Card: capability = the best elicitation within a budget; propensity = default behaviour

Family E (elicitation cost). Slug `capability-vs-propensity`. Notation: `_FRAME.md`.

## 1. Definition, formally

- **Propensity.** prop_θ(t) = p_θ(t) under the default protocol: one plain attempt at T 0.8. It is what the model
  *would* do.
- **Capability at budget C.** cap_θ(t; C) = max over elicitation methods m with cost(m) ≤ C of P(m elicits a valid
  proof of t from θ). It is what the model *can* do. The method set M is declared in advance:
  - plain sampling with any T;
  - guided sampling (step-checked redraws, `guided_sample.py`);
  - best-first / PUCT search with the model as the policy (`mcts-a`);
  - prompt-level changes (another renaming of the same theorem).
  - **Not** fine-tuning: that is `elicit-finetune`, because it changes the model.
- **Cost** is measured in GPU-seconds, or in attempt-equivalents of the base's plain sampling.
- **Budget C** is tied to RL's compute as in `passk-budget`: C_per or C_total.

## 2. Decision rule

For base B and RL model R, per theorem:

| verdict | rule |
|---|---|
| **created** | cap_R(t; C_eval) high, and cap_B(t; C) < 0.05 for every method in M at the budget C: no allowed method gets the base there |
| **elicited** | cap_B(t; C) ≥ 1 − 1/e for some method within C, while prop_B(t) is low. RL converted a capability into a propensity: "can" was already true, RL changed "would" |
| **neither** | R fails at C_eval |

This is the exact sense of the dangerous-capability literature: "capability evaluations are about whether an AI system
*can* do some task … alignment evaluations are about whether it *would*" (van der Weij et al.).

## 3. Null or floor

- The budget is the floor. Random weights have cap(t; C) ≈ 0 for every allowed method at any C we can afford, because
  every method samples from the model's own distribution.
- The method set must not supply the proof. Guided sampling only checks steps; it never proposes them. The
  "reasonable prompt" condition of Greenblatt et al.: "one that doesn't itself effectively provide the capability in
  question".

## 4. How to compute it here

- **Plain sampling at large budgets:** J2.
- **Guided sampling:** J3 (pend / r8 / r16, cap 12; cap 6 on pod C), ≈ 2 A40-hours per seed.
- **PUCT search** at pend and r8 exists from `mcts-a`: it closed ≈ 44 % of the 8-round EI gain on rrQ100 at matched wall
  clock, but nothing on group C.
- **Analysis:** the method-maximum per theorem at matched cost (guided costs 2–3× plain per attempt; use
  `guided-tts`'s matched-token accounting).

## 5. Sensitivity

- **The method set M.** Adding a stronger method can only move theorems from created to elicited. The verdict is
  relative to M and must be stated with it.
- **Budget C:** as in `passk-budget`.
- **Temperature:** part of M; take the best T.
- **Representation:** the proof-state interface is itself a powerful elicitation method for whole-proof models
  (`support-state`: 28 of 29 survivors). Whether "interface" is in M is a design decision.
- **Renaming:** a prompt-level method in M. Allow all renamings of t, but count each as an attempt.
- **Noise:** per method, binomial at the read's n. Maximising over methods inflates (a winner's curse), so confirm the
  winning method on a fresh draw.

## 6. Failure modes

- **Open-ended M.** "No method we tried elicits it" is not "no method can". Absence of capability is never certified,
  only bounded (Greenblatt et al. Sec. 2: "it is difficult to show that a model does not possess a particular
  capability").
- **Methods that teach.** A search with a strong learned value function, or a prompt with worked examples, carries
  information in; its cost must count, or it must be excluded.
- **Maximum over methods vs noise:** see §5.

## 7. Relations

- `passk-budget` is the special case M = {plain sampling}.
- `elicit-finetune` extends M to weight changes.
- `reliability` is the propensity side.
- The pair (cap, prop) is what the report recommends showing for every theorem set.

## 8. Literature anchor

- **van der Weij et al. 2024 (2406.07358v4).**
  - "actual capability to be the best performance on a certain task it can achieve, given the best currently available
    capability elicitation techniques such as prompting and fine-tuning" (Sec. 2).
  - The 1 % of training cost convention, quoted from Anthropic (2023) (Sec. 2).
  - "Capability evaluations are about whether an AI system can do some task … whereas alignment evaluations are about
    whether an AI system would do some task" (Sec. 2).
- **Shevlane et al. 2023 (2305.15324v2):** capability vs propensity (Abstract; Sec. 1). "Researchers will need to bring
  latent capabilities to the surface" (Table 2).
- **Hofstätter et al. 2025 (2502.02180v3):** "A latent capability … is one that a model exhibits with low probability
  by default, but can be revealed through small changes to the context, activations, or weights" (Sec. 3.3).
- **Greenblatt et al. 2024 (2405.19550v1):** the reasonable-prompt definition (Sec. 2).
- **Firestone 2020 (PNAS 117(43)):** performance constraints mask competence; a fair comparison accommodates them.
- All verified in `_claims_L2.md`.

## 9. Critic's verdict

*(pending)*
