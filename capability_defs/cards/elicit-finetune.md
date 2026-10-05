# Card: elicitable by small fine-tuning (sample complexity, description length)

Family E. Slug `elicit-finetune`. Notation: `_FRAME.md`.

## 1. Definition, formally

For a capability defined over a family 𝒯 (e.g. the 40 held-out transfer A ∨ ¬A instances), and a fine-tuning recipe
𝓕 (here: one EI-round fine-tune, 600 steps, lr 3e-4 → 3e-5, with 20,000 pretraining replay records):

- **Sample complexity to elicit:** N*_B(𝒯) = the smallest number of demonstrations D (proofs of *other* family
  members, never of 𝒯's own instances) such that 𝓕(B, D) reaches mean pass@256 ≥ τ on 𝒯.
- **Description-length version (prequential / EDL).** The online code length of the demonstrations under 𝓕 starting
  from B, Σᵢ −log π_{θ_{i−1}}(yᵢ), minus the final model's code length. Compare it with the same from a control start
  (init, or a model not pretrained on the family's moves): elicitation is cheap in bits, teaching expensive.
- **The Deeb–Roger variant** (information already in the weights): fine-tune on demonstrations T, test on held-out V,
  where T and V share the skill but no instance. Include a control model that never had the skill. Recovery on V
  beyond the control means the skill was present.

## 2. Decision rule

| verdict | rule |
|---|---|
| **elicited** (latent in the base) | N*_B small in absolute terms (≤ 16 demonstrations) **and** far below the control's: N*_B ≪ N*_control, or the control never reaches τ |
| **created** (by RL) | R solves 𝒯 at τ, while no D of size ≤ N_max moves B to τ, or B needs as much as the control |
| **neither** | R does not reach τ |

The comparison with a control is essential. "16 demonstrations suffice" means nothing if 16 suffice for a model that
never saw the moves (Deeb & Roger reject raw relearning budgets for lack of a baseline).

## 3. Null or floor

- **The control model is the floor.** Use init or an early pretraining checkpoint fine-tuned with the same 𝓕 and D,
  plus a matched non-family demonstration set (C16) from B.
- **Random weights:** 𝓕(init, D) with N ≤ 16 does not produce valid proofs at all, so the floor is ≈ 0.
- Dan's objection maps to "enough fine-tuning teaches anything". The rule therefore compares sample complexities
  instead of asking whether some N works.

## 4. How to compute it here

- **J4** (pre-registered): from pend s0 / s1 / s2, mixes A0 (replay only), A4 / A16 (4 / 16 A ∨ ¬A demonstrations from
  s1's r16 found set on `rl_targets`), C16 (16 length-matched non-LEM proofs). Read the 40 held-out transfer A ∨ ¬A
  instances at k 256. About 0.5 A40-hours per seed.
- An init-start control and a prequential sweep (N = 1, 2, 4, 8, 16) would cost ≈ 1 more GPU-hour. They are not run
  in J4; this is stated as a limitation.

## 5. Sensitivity

- **The recipe 𝓕:** learning rate, steps and replay fraction change N* by large factors. EDL "depends on the training
  algorithm" (Donoway et al., earlier review).
- **Demonstration quality:** demos the model "can't imitate well" give lower performance "no matter the number of
  demonstrations" (Greenblatt et al.). Ours are RL-found proofs, i.e. in-distribution for a sibling model.
- **Representation:** the fine-tune trains (state, action) pairs. A whole-proof format would teach differently.
- **Renaming:** test instances must not be renamings of demonstrations. This holds: the 40 transfer instances are a
  disjoint generation, checked for renaming-class overlap with textbook72.
- **Noise:** one fine-tune per arm per seed; the fine-tune seed adds variance. Report all three seeds.

## 6. Failure modes

- **Teaching vs eliciting is a matter of degree:** "the difference between tuning and training proper is a matter of
  degree" (Harding & Sharadin, fn. 38). The rule needs the control, not an absolute N.
- **Leakage:** T and V share sub-skills by design. Deeb & Roger: "if the goal is to unlearn the capability of coding,
  it's hard to construct T and V with low leakage".
- **The fine-tune also pretrains:** 20,000 replay records are more pretraining. A0 isolates that.
- **One family only (LEM)** in J4. Generalising needs more families.

## 7. Relations

- Extends `capability-vs-propensity` to weight changes.
- Its bits version is the training-side counterpart of `bits-over-null`.
- `schema-acquisition` supplies the families.
- `causal-ablation` is the stronger, interventional cousin.

## 8. Literature anchor

- **Greenblatt et al. 2024 (2405.19550v1).**
  - "fine-tuning on a single demonstration is often enough to recover most of the "hidden" performance" (Sec. 1).
  - 18 M-parameter models "locked from scratch require 2-4x the amount of data to unlock" (Sec. 7).
  - "it is not necessarily clear if fine-tuning is eliciting hidden capabilities or re-introducing them" (Sec. 3).
- **Deeb & Roger 2024 (2410.08827v3).**
  - The T / V design (Sec. 3.2): "training the model on T should not increase accuracy on V for a model that was not
    trained on either T or V".
  - Relearning time lacks "a reliable baseline for comparison" (Sec. 3.2).
- **Harding & Sharadin 2024:** "if a model can be fine-tuned with very little compute … this does provide indirect
  evidence that it already had the ability" (Sec. 5.2.2).
- **Whitney et al. 2020 (2009.07368v2):** examples needed and surplus description length to reach ε loss (Sec. 4).
- **Voita & Titov 2020 (2003.12298v1):** online code length with control tasks (Sec. 3–4).
- **Blier & Ollivier 2018 (1802.07044v5):** prequential coding.
- **Donoway et al. 2026, EDL** (earlier review).
- Verified in `_claims_L2.md` / `_claims_L3.md`.

## 9. Critic's verdict

*(pending)*
