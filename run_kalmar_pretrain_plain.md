# Can a small model learn a proof algorithm from examples? (kalmar-pretrain, plain-language summary)

## The setting

This project trains small language models, about 10 million parameters, to prove simple logic theorems. These are
statements built from four letters with "and", "or", "not" and "implies". The model sees the current proof state, the
facts established so far plus the goal, and writes one step at a time. Lean, a proof checker used by mathematicians,
decides whether a finished proof is correct.

The project asks how much training against such a checker teaches genuinely new skills. This run asks a related
question: can ordinary training on examples teach a model a complete *method*?

## The method

Every theorem in this logic can be proved by one mechanical recipe, the truth-table argument behind Kalmár's
completeness proof:
1. Split into cases for every letter, true or false; with four letters that gives up to 16 cases.
2. In each case, prove each formula, or its negation, by a fixed recursion.
3. A case in which an assumption is false closes immediately.

Every step depends only on what the current state shows. A model that learned the recipe could prove every theorem in
the domain, including kinds it never saw. The catch is length. Recipe proofs average 109 steps; the project's usual
training proofs average 8.

## What we did

We generated a recipe proof for each of the 155,000 theorems in the project's standard training set (K12), and Lean
accepted all of them. We trained the project's best small model on them from scratch, three times with different
seeds:
- for the same 3.7 passes over its data as the standard model, which takes about 27 times more training text;
- for the standard model's budget, an eighth of one pass.

We compared both with the standard model, which learns from K12's own short proofs.

## What we found

**It learned the mechanical parts, not the whole recipe.**
- Shown each intermediate state of the recipe's proof of an unseen theorem, the fully trained model chose the
  recipe's next step 94.5 % of the time.
- Case splits and case closings were near-perfect. Steps that need a judgement, such as which piece of which formula
  to prove next, were 65–92 %.
- Writing whole proofs alone, it produced a correct proof for 29–36 % of unseen theorems. It followed the recipe
  exactly 14–16 % of the time.
- The standard model proves 92 % of the same theorems its own way.
- Accuracy was still rising when training stopped, so more training or a larger model might go further.

**The mistakes are bookkeeping, not logic.**
- Of one model's 6,903 wrong steps:
  - 45 % write a formula that belongs to the problem but is not the one due next: the model loses its place in the
    recursion;
  - 31 % write a formula that appears nowhere in the problem: a copying slip;
  - only 1.4 % get a truth value backwards.
- One slip usually ruins a hundred-step proof, so 95 % per step yields few complete proofs.

**It mostly did not help.**
- **Long held-out problems.** With 32 tries each it solved fewer than the standard model: 33 against 165 of 250 on
  one held-out set, and 17 against 246 of 600 on long problems.
- **Larger formulas.** On formulas larger than any in training, every model failed.
- **One exception: classical reasoning.** Some theorems need an argument the standard data almost never shows. Here we
  used decoding in which a checker rejects a logically wrong step and the model tries again. The recipe-trained models
  then solved 26–34 of 106 such theorems and the standard models 12–19, on every seed. The recipe treats these theorems
  like any other.

**A side finding.** Models trained on K12 were known to fail every problem with four or more assumptions. The cause is a
vocabulary quirk:
- Proofs begin by restating each assumption under a label, and the label "h4" never occurs in K12.
- When the environment restates the assumptions, the standard model solves 177–191 of 200 such problems.

**Reinforcement learning on top.** LADDER_PLAIN

## What it means

At this scale, imitating a complete algorithm's long proofs did not produce a model that runs the algorithm reliably.
The model learned the pattern-like parts. It did not learn to keep track of where it is in a long computation. Short
proofs it can get right are worth more than a long method it executes imperfectly. The method paid off only where it
was designed to: theorems whose proof needs a step the ordinary training data almost never shows.
