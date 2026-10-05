## 6. Open questions for Dan (each with my recommendation)

1. **Which budget defines "the base cannot"?**
   - *Options:*
     - k_eval (256; the field's equal-k test);
     - 1 % of the base's pretraining compute per theorem (the safety-evaluation convention, ≈ 2–4 × 10³ attempts
       here);
     - **K_eval-set**: RL's GPU time spread as base attempts over the evaluation theorems (≈ 2 × 10⁴ at r8, ≈ 5 × 10⁴
       at r16);
     - K_total: all RL compute on one theorem (≈ 10⁶–10⁷).
   - *Recommendation:* K_eval-set for verdicts. Always print each theorem's k-to-solve interval, so a reader can apply
     any other budget. Do not use k_eval as a creation test.
2. **Is the replay pretraining inside our RL part of "RL"?**
   - Each EI round also trains on 20,000 pretraining records: ≈ 476 M tokens over 8 rounds, more than Stage-1 itself.
     The replay-only control solves ≈ a third of what equal-k calls RL-created.
   - *Recommendation:* report RL net of the replay-only control (and of a compute-matched continuation where
     affordable). Claims about "RL" should be claims about what the verifier signal added.
3. **"Created relative to this seed's base" or "relative to the pretraining recipe"?**
   - The three bases differ a lot. `textbook_245a0349` is 0 / 768 for s0's pend and 505 / 768 for s2's.
     `la_transfer_1382` is 0 / 17,152 for s0, 26 / 768 for s1.
   - *Recommendation:* use per-seed verdicts for mechanisms. A headline "RL creates X" claim should require that *no*
     seed's base reaches X within the budget.
4. **What is the unit of a capability: a theorem or a family?**
   - *Recommendation:* families defined by a key step (members that need it), for any creation headline. Theorem-level
     verdicts are noisier: seed Jaccard ≈ 0.35. They are also easier to over-read, since one theorem can be one lucky
     route.
5. **What counts as an elicitation method?**
   - *Recommendation:* per-theorem methods only: more samples, any temperature, guided step-checked redraws,
     prior-only search, renamings.
   - Anything that learns from verifier verdicts on *other* theorems (fine-tuning, value heads) is RL's own mechanism.
     It should be studied as teachability (how many demonstrations), not counted as the base's capability.
6. **If four demonstrations install a schema in the base, is the schema "latent"?**
   - *Recommendation:* call it **teachable**, and reserve **latent** for when the base learns it markedly faster than
     a model pretrained without the key move (J6b's design). On our data: ⟨J6b result⟩.
7. **Certification.** Certifying "the base cannot" by sampling needs ≈ 60 × K zero-success attempts: ≈ 1.2 M per
   theorem at K_eval-set, ≈ 2 A40-hours each.
   - *Recommendation:* label the cheap verdict "not reached within budget", and pay for certification only for the few
     theorems a headline rests on.
8. **The next experiment for "can RL create?"** The only design that can establish creation in the strong sense is
   an intervention on pretraining.
   - *Recommendation:* ablate a *composition* (DN applied to a negation box), not a primitive. Pretrain three seeds
     without it, run 16 EI rounds from each, and use the key-step excluded-middle family on held-out members as the
     read-out (≈ $26). Run it before moving to a richer domain, so the project has one clean creation test.
9. **Reporting standard.** *Recommendation:* every RL result reports:
   - propensity (plain pass@1);
   - capability within budget (best per-theorem method);
   - the compute-matched reach table net of replay.

   The equal-k "group B" stays a descriptive label only.
