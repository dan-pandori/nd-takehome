# Can a small model learn a proof algorithm from examples? (kalmar-pretrain, plain-language summary)

## The setting

This project trains small language models (about 10 million parameters) to prove simple logic theorems built from four
letters with "and", "or", "not" and "implies". The model sees the current proof state, the facts established so far
plus the goal, and writes one step at a time. Lean, a proof checker used by mathematicians, decides whether a
finished proof is correct.

This run asks whether ordinary training on examples can teach a model a complete *method*.

## The method

Every theorem in this logic can be proved by one mechanical recipe, the truth-table argument behind Kalmár's
completeness proof:
1. Split into cases for every letter, true or false; with four letters that gives up to 16 cases.
2. In each case, prove each formula, or its negation, by a fixed recursion.
3. Close at once any case in which an assumption is false.

Every step depends only on the current state, so a model that learned the recipe could prove every theorem in the
domain. The catch is length: recipe proofs average 109 steps, against 8 for the project's usual training proofs.

## What we did

We generated recipe proofs for all 155,000 theorems of the project's standard training set (K12); Lean accepted every
one. We trained the project's best small model on these proofs from scratch, three times with
different seeds. Training made the same 3.7 passes over the data as the standard model's, which is about 27 times more
text. We compared it with the standard model, trained on K12's own short proofs. Before any training, we wrote down
what we expected and what would count as success.

## What we found

**As planned, the answer was no.**
- Shown each intermediate state of the recipe's proof of an unseen theorem, the model chose the recipe's next step
  94.5 % of the time.
- Writing whole proofs alone, it produced a correct proof for only a third of unseen theorems.
- On harder sets it solved far fewer than the standard model: 33 against 165 of 250, with 32 tries each.
- Its mistakes were mostly bookkeeping. It lost its place in the long recursion, or miscopied a long formula; it rarely
  got the logic wrong.

**A surprise: most of the failure was how training ended.** The project's training recipe lowers the learning rate
only to 30 % of its peak, and stops there.
- We trained each model for a further 600 small steps on recipe proofs it had already seen, with a learning rate
  decaying ten-fold. That is under 0.1 % of the original training.
- After this "annealing" the models chose the recipe's step 98.7 % of the time. They wrote correct proofs for 71–79 %
  of unseen theorems, and followed the recipe exactly in 54–60 %.
- The annealed models then roughly matched the standard model on ordinary held-out problems: 37 % against 38 % solved
  at the first try.
- They clearly beat it on theorems that need classical reasoning the standard data almost never shows (35 % against
  7 %), and on one set of externally collected problems (38 % against 16 %).
- They still fall short of what we had defined, in advance, as having learned the method: exact recipe-following on
  small problems is about two thirds, against a 90 % bar.
- This part was not planned in advance: a strong lead, not a settled result.

**Reinforcement learning, mostly explained.** In a few rounds of "expert iteration" the model is trained on its own
Lean-accepted proofs.
- After one round, the number of target problems solved jumped from 135 to 572 of 1,000.
- But each round's training step replays thousands of recipe proofs at a low learning rate: the same annealing.
- Annealing alone, with none of the model's own proofs, solves 578. So this reinforcement learning added nothing we
  could measure on top of annealing.
- It did not drift from the method: afterwards its proofs follow the recipe more often and are not shorter.

**A side finding.** Models trained on K12 had been reported to fail problems with four or more assumptions.
- Proofs begin by restating each assumption; K12 never has more than three, and with more the standard model
  restates them wrongly.
- When the environment restates them instead, it solves 177–191 of 200 such problems.

## What it means

Imitating an algorithm's long proofs nearly works at this scale, once training is finished properly. The
pattern-like parts are learned easily. Keeping track of a long computation needs a final low-learning-rate phase that
the project's standard recipe omits. Large apparent gains from reinforcement learning can come from that same missing
phase.
