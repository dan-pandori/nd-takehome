# Does reinforcement learning teach Olmo new maths, or make it use what it already knew? — a plain summary

**The question.** AI2 trained a 7-billion-parameter language model, Olmo 3, on text, then ran reinforcement learning
(RL) on it with maths problems: the model writes a solution, an automatic checker says whether the final answer is
right, and the model is nudged towards answers that were right. They published 28 snapshots along that RL run. We
asked whether RL lets the model solve problems it *could not* solve before, or whether it mostly makes it solve,
more often, problems it could already solve now and then.

**What we did.** We took 83 problems from the American Invitational Mathematics Examination (AIME) of 2024, 2025 and
2026 — all newer than the model's training text — after removing 7 that, or close variants of which, appear in the
model's RL or training data. We sampled solutions from the model before RL (the "base") and from the RL snapshots
after 500 and 2,800 RL steps, using exactly the prompt, randomness and length limit RL used, and graded them with
RL's own answer checker. Every problem an RL snapshot solved but the base had not was then given to the base again
and again — up to 512 more attempts — until it solved it; and every problem the base solved but the final RL model
had not was given to the RL model the same way.

**What we found.**

1. *RL makes the model much better at first tries.* On one attempt the base solves a problem 9 % of the time; after
   500 RL steps 30 %, after 2,800 steps 42 %. With 8 attempts the base solves 36 % of the problems and the final RL
   model 63 %.

2. *But everything RL "newly" solved, the base could solve too, given more attempts.* Seventeen problems were solved
   by an RL snapshot and never by the base in its first 16 attempts. Re-sampled, the base solved all 17 — after 18 to
   383 attempts, typically about 70 — with complete, correct worked solutions, not lucky guesses. The other way round
   was the same: the 3 problems the base solved and the final RL model had missed, the RL model solved when given more
   attempts (after 12 to 280). At the budgets we could afford, RL did not add a single problem the base could not do;
   it made rare correct solutions common.

3. *RL's correct solutions look like things the base would write.* We measured how probable the base finds each
   correct RL solution, word by word. Every one of them falls inside the range of the base's own correct solutions.
   The final RL model's solutions are slightly less typical for the base (about 5 % less probable per token) than
   for itself, but no particular step is foreign to it.

4. *How much RL is that?* RL's total compute was roughly a thousandth of the compute used to pretrain the model
   (1.4–3.1 × 10⁻³ at the last snapshot). Over that range the gains grew with RL compute, but genuinely new problems
   never appeared.

**What this does and does not show.** It is one model, one RL run, 83 problems and at most about 500 attempts per
problem. A problem the base fails 500 times could still be solvable at 5,000, and the formal decision rule we wrote in
advance came out "inconclusive" only because one of its clauses asked the base to match the RL model at 8 attempts,
which sharpening alone never does. RL with this little compute may be exactly the regime where it only sharpens;
Olmo 3.1 Think 32B spent far more of its compute on RL (about 14 % of pretraining in GPU-hours), which is why the next
test is planned there.

**What it cost.** About $⟨cost⟩ of rented GPUs. Sampling this model is expensive — about half a dollar per million
tokens of output — because each solution is long (6,000 tokens for the base, 12,000 after RL) and the model's
attention design stores a lot per token. The decision memo (`olmo_pilot/decision_32b.md`) prices the 32B test at about
$110 for a design like this one and $205–320 for one that pushes the base to 512–2,048 attempts.
