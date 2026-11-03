# Does reinforcement learning teach Olmo new maths, or make it use what it already knew? — a plain summary

**The question.** AI2 trained a 7-billion-parameter language model, Olmo 3, on text, then ran reinforcement learning
(RL) on maths problems: the model writes a solution, a checker says whether the final answer is right, and the model
is nudged towards answers that were right. AI2 published snapshots along the way. We asked whether RL lets the model
solve problems it *could not* solve before, or mostly makes it solve, more often, problems it could already solve now
and then.

**What we did.** We took 83 problems from the 2024–2026 American Invitational Mathematics Examination (AIME), all newer
than the model's training text, after removing 7 that (or close variants of which) appear in its RL or training data.
We sampled solutions from the model before RL (the "base") and after 500 and 2,800 RL steps, with exactly RL's prompt,
randomness and length limit, and graded them with RL's own checker. Every problem an RL snapshot solved and the base
had not went back to the base, attempt after attempt (up to 512), until it solved it — and the same the other way.

**What we found.**

1. *RL makes the model much better at first tries.* On one attempt the base solves a problem 9 % of the time; after
   500 RL steps 30 %, after 2,800 steps 42 %. With 8 attempts: 36 % against 63 %.

2. *But everything RL "newly" solved, the base could solve too, with more attempts.* Seventeen problems were solved
   by an RL snapshot and by the base in none of its first 16 attempts. Re-sampled, the base solved all 17, after 18 to
   383 attempts (typically about 70), with complete worked solutions, not lucky guesses. The 3 problems the base
   solved and the final RL model had missed, the RL model solved with more attempts. At these budgets RL added no
   problem the base could not do; it made rare correct solutions common.

3. *RL's correct solutions look like things the base would write.* Scored word by word by the base, every correct RL
   solution falls inside the range of the base's own correct solutions. The final model's are slightly less typical
   for the base (about 5 % less probable per token) than for itself, with no part unusually surprising to it.

4. *How much RL is that?* About a thousandth of the compute used to pretrain the model (1.5–3.2 × 10⁻³ at the last
   snapshot). Over that range the gains grew; genuinely new problems never appeared.

**What this does and does not show.** One model, one RL run, 83 problems, at most about 500 attempts per problem: a
problem the base fails 500 times might still fall at 5,000. Our decision rule, written in advance, came out
"inconclusive" only because one clause asked the base to match RL at 8 attempts, which sharpening alone never does.
RL this small may be exactly the regime where it only sharpens; Olmo 3.1 Think 32B spent far more of its compute on RL
(about 14 % of pretraining in GPU-hours), so the next test is planned there.

**What it cost.** About $39 of rented GPUs. Sampling is expensive — about half a dollar per million tokens —
because each solution is long (6,000 tokens for the base, 12,000 after RL) and the model's attention stores a lot per
token. The decision memo (`olmo_pilot/decision_32b.md`) prices the 32B test at about $110 for this design and $205–320
for one that pushes the starting model to 512–2,048 attempts.
