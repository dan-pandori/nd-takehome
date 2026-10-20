# How much is there to learn in a proof-writing algorithm? (run kalmar-complexity, plain summary; UNREVIEWED)

**The setting.** In propositional logic, a 1930s proof by László Kalmár gives a mechanical recipe that proves
every valid statement:
- split into cases on each variable being true or false;
- in each case, prove every part of the statement, or its negation, from the inside out.

The previous run (kalmar-pretrain) taught small language models — 9.6 million parameters, trained from scratch — to
write proofs this way, one step at a time. They agreed with the recipe on about 95 % of steps, yet wrote a fully
correct recipe-following proof only about 14 % of the time. Dan asked: how many bits of information does such a model
have to absorb to learn the recipe? Is the length of the shortest program for it the right measure?

**What we measured.**
1. **The shortest programs we could write** for the recipe, in four very different languages, each checked to
   reproduce the original builder exactly on 1,000 test statements and on fresh ones:
   - compressed Python;
   - binary lambda calculus, a minimal programming language where every program has an exact length in bits;
   - RASP-L, a language designed to describe what a transformer (the kind of network the models are) can compute in
     one pass;
   - a decision tree over hand-picked features of the proof state.
2. **The same measurements for simpler algorithms** whose learnability is known: copying, reversing, sorting,
   parity, addition, evaluating a formula, and checking a truth table.
3. **How many bits the networks actually took in.** We use the standard "prequential" accounting. While a model
   trains, every example is first used to test it, and only then to train it. The cost of those first guesses,
   minus what the finished model still pays, is the information the network absorbed. We computed it from the
   earlier run's training logs and from new small-scale training runs.
4. **Which of these measures predicts where the models fail.** We compared each against the earlier run's record
   of which kinds of step the models got wrong.

**What we found.**
- **The recipe is short.** About 5,400 bits in lambda calculus (roughly 680 bytes), about 860 bytes of compressed
  Python. With the input parsing and the exact output format, 7,000–12,000 bits.
- **It is the largest of the algorithms we compared, in every language.** The languages agree closely on the
  ordering. Truth-table checking is next, 13 times smaller in lambda calculus.
- **But program length does not order how hard things are to learn.**
  - The style of the earlier run's comparison data is learned easily, and its generator program is about twice as
    long as the recipe.
  - Evaluating a formula takes under 300 bits, yet none of our small models got it right after 130,000 examples;
    one did after 260,000.
- **The networks absorbed about a thousand times the program's length.** In its first pass over the 155,000
  training proofs, the model took in about 6.6 million bits: roughly 0.7 bits per parameter. A model trained on the
  ordinary proofs absorbed about 1.6 million. {{B2_PLAIN}}
- **What predicts failure is the work one step requires, not the length of the instructions for it.**
  - Some steps need almost nothing: start a case split, close a finished sub-proof. Others require searching the
    formula for the next part not yet proved, checking which pieces are already available, and knowing which parts
    are true in the current case. "Write that this 'and' is true" is one such step.
  - The models fail on exactly those steps:
    - the transformer-language measure of how many sequential lookups a step needs correlates with the failure
      rate at about 0.85;
    - the code length for each kind of step does not (once we account for how often each step occurs);
    - the commonest kind of mistake — working on the wrong part of the formula — tracks the search demand most
      closely of all.
  - The RASP-L program needs about 40 sequential attention layers in the worst case; the models have 6.
  - {{B3_PLAIN}}

**What this means.** Dan's instinct — count bits — is right, but the bits to count are not the program's.
- A program length of a few thousand bits is a floor that no realistic learner comes near.
- How far above it a learner lands depends on how well its per-step computation matches what each step demands.
- The useful statement of "how much there is to learn" has two parts:
  - the bits a specific learner absorbs under a stated protocol (here about 6.6 million);
  - a per-step profile of computational demand, compared with the model's depth.
- For the follow-up question — how many of those bits pretraining and reinforcement learning each supply — the same
  accounting, applied to fixed test proofs, splits the bits by step type and by demand.

**How strong is the evidence?** Strong as a correlation:
- three trained models, fifteen kinds of step, and the same pattern within each kind of step;
- an independent check on the error analysis.

It is one architecture, though, and one hand-written program per language; the languages' own constants are as
large as the programs. The causal tests — give the model the search result, or give it more depth — are proposed in
`next_steps.md` {{B3_STATUS}}.
