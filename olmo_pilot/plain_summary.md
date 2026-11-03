# Does reinforcement learning teach Olmo new maths, or make it use what it already knew? — a plain summary

DRAFT (numbers marked ⟨…⟩ are filled in when the last jobs finish).

**The question.** AI2 trained a 7-billion-parameter language model, Olmo 3, on text, then ran reinforcement learning
(RL) on it with maths problems: the model writes a solution, an automatic checker says whether the final answer is
right, and the model is nudged towards answers that were right. They published 28 snapshots along that RL run. We
asked whether RL lets the model solve problems it *could not* solve before, or whether it mostly makes it solve,
more often, problems it could already solve now and then.

**What we did.** We took 83 competition problems from the American Invitational Mathematics Examination (AIME) of
2024, 2025 and 2026 — all newer than the model's training text — after removing 7 that (or close variants of which)
appear in the model's RL or training data. We sampled solutions from the model before RL (the "base") and from the
RL snapshots after 500 and 2,800 RL steps, using exactly the prompt, randomness and length limit RL used, and graded
them with RL's own answer checker. Any problem an RL snapshot solved but the base had not was then given to the base
again and again — up to 512 more attempts — until it solved it or ran out.

**What we found.**

1. *RL makes the model much better at first tries.* The base solves a problem on one attempt 9 % of the time; after
   RL, 42 % (after 500 steps already 30 %). With 8 attempts the base solves 36 % of the problems, the RL model 63 %.

2. *But almost everything RL "newly" solves, the base can solve too, given more attempts.* Seventeen problems were
   solved by an RL snapshot and never by the base in its first 16 attempts. Given more attempts, the base solved 14
   of them within 128 tries and ⟨P3a⟩. ⟨One⟩ problem was solved by RL and never by the base within ⟨K⟩ attempts — and
   ⟨one⟩ problem went the other way: the base solves it and the RL model, given the same extra attempts, did not.
   So at the sampling budget we could afford, RL's gains look like sharpening — making rare correct solutions
   common — rather than new ability.

3. ⟨LL⟩

4. *How much RL is that?* RL's total compute was about a thousandth of the compute used to pretrain the model
   (between 1.4 × 10⁻³ and 3.1 × 10⁻³ at the last snapshot). Within that range, the gains grew with RL compute but
   the "new" problems did not pile up.

**What this does and does not show.** It is one model, one RL run, 83 problems and at most 512 base attempts per
problem. A problem the base fails 512 times could still be solvable at 5,000. And RL with this little compute may be
exactly the regime where it only sharpens; the larger Olmo 3.1 Think 32B spent far more of its compute on RL
(about 14 % of pretraining in GPU-hours), which is why the next test is planned there.

**What it cost.** $⟨cost⟩ of rented GPUs. Sampling this model is expensive — about half a dollar per million words
of output — because each solution is long (6,000 tokens for the base, 12,000 after RL) and the model's attention
design stores a lot per token. The decision memo (`olmo_pilot/decision_32b.md`) prices the 32B test at about
$100–185 for a design like this one.
