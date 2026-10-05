## Glossary (plain language)

- **Theorem t.** One propositional sequent we ask a model to prove, e.g. ⊢ A ∨ ¬A.
- **Lean accepts / V(t, y).** The only judge. A proof counts iff Lean 4 checks it.
- **Attempt.** One sample from the model, run to completion in the proof-state environment (T 0.8, the read caps).
- **Solve probability p_θ(t).** The chance that one attempt by model θ proves t. All other numbers are views of it.
- **pass@k.** The chance of at least one proof in k attempts: 1 − (1 − p)^k.
- **k-to-solve.** 1 / p: the expected number of attempts until the first proof. "The base needs ≈ 3,000 attempts."
- **Budget K.** How many attempts (or how much compute, converted to attempts) we allow before saying "the model cannot
  do it".
  - **K_eval-set:** RL's GPU time spread as base attempts over the 322 evaluation theorems (≈ 2 × 10⁴ at r8).
  - **K_per:** RL's GPU time per training target (≈ 10³).
  - **K_total:** all of RL's compute on one theorem (≈ 10⁶–10⁷).
- **Base / pend.** The pretrained model at the end of pretraining. **r8 / r16:** the same model after 8 / 16 rounds of
  expert iteration (RL).
- **Replay-only control.** The same 8 rounds of fine-tuning as RL, but on pretraining data only: no RL proofs, no
  verifier. It separates "RL's proofs did it" from "more training did it".
- **Compute-matched continuation (J7).** The base trained further on its pretraining data for as long as RL's GPU time.
- **Created (at budget K).** RL solves t, and the base cannot, even with K attempts and with training that has no
  verifier. "Cannot" must be certified: no success in ≈ 60 K attempts, or a stated weaker version.
- **Elicited.** RL solves t, and the base can too within the budget (it found a proof, or its probability is certified
  above 1 / K). RL made a reachable thing reliable.
- **Undetermined.** The evidence does not place the base on either side of the budget. Common for rare theorems.
- **Propensity vs capability.** What the model *does* by default (one plain attempt) vs what it *can* do with the
  best per-theorem method within a budget (more samples, step-checked redraws, search without learned value heads).
- **Teacher-forced probability π(y).** The model's probability of writing one specific proof y, computed by feeding it
  the proof. It is a lower bound on p, because p sums over all proofs.
- **Known-proof bound.** The sum of π_base(y) over every proof of t that any model ever found. It is a guaranteed lower
  bound on the base's p.
- **Worst step.** The least likely single action in a proof under a model: the bottleneck decision.
- **Schema / family.** Theorems sharing a proof pattern, e.g. all A ∨ ¬A. A family-level capability is acquired as a
  whole and shows up on held-out members. **Key-step family:** only the members that genuinely need the schema's key
  step (e.g. the classical step for excluded middle).
- **Sharpening vs reshaping.** Sharpening concentrates probability on proofs the base already produces; reshaping
  changes which of the base's own proofs RL prefers. Pure conditioning on success (the exact form of "only elicits")
  reshapes nothing.
- **IRT ability θ.** A single latent score per checkpoint, fitted jointly with a difficulty per theorem. "More of the
  same" means RL's successes are predicted by its higher θ.
- **Placebo.** A comparison arm that gets the same kind of change without the ingredient in question (here: training
  without RL proofs, or more pretraining). It sets the noise floor for "RL-specific".
- **Noise floors.** *Redraw:* the same model sampled again. *Seed:* a different training run of the same recipe.
  Differences inside them are not findings.
- **Null model.** A model that should have no capability (random initialisation). It sets the floor for "any k
  eventually works": random weights need ≈ e^1000 attempts per proof here.
