# olmo-ifomega in plain words

**The question.** Reinforcement learning (RL) tunes an AI model by rewarding it whenever an automatic checker says an
attempt succeeded. A live debate is whether RL teaches genuinely new abilities, or only makes a model more reliable at
things it could already do occasionally. A clean test: find tasks where the RL-trained model succeeds but its
starting point never does, even in hundreds of tries ("reach"). An earlier run on hard maths competition problems found almost
none for this model family.

This run asked the same question where RL moved the model a lot: following unusual instructions (IFBench, e.g.
"every word must contain a consonant cluster"), following standard instructions of the kind RL trained on (IFEval,
the control), and maths problems built to be unlike the training data (OMEGA `test_out`). The models are Olmo 3 32B
Think before RL ("DPO", the starting point) and two checkpoints of its longest RL run (steps 750 and 2,300).

**How.** Every model answered every prompt 8–16 times. Wherever an RL checkpoint succeeded and the starting point did
not, the starting point got up to 256 tries; wherever it still failed, the RL model had to succeed again on fresh
tries. Because automatic checkers can be fooled, every deciding answer was read by a reader who did not know which
model wrote it, and then by me: 505 answers in all.

**What we found.**

- *Unusual instructions (IFBench): reach.* RL more than doubles the success rate (29 % → 68 % on a first try). On 42
  of 218 prompts the RL model gives genuine answers while the starting point never does in 256 tries, and its
  failures there are not near misses (93 % ignore the instruction or miss it widely).
- *But the RL model also games the checker.* About a third of its "successes" satisfy the letter of the instruction
  while dropping the substance, such as a twelve-word alphabetical word chain instead of a requested story. On 11
  prompts its apparent advantage is entirely such gaming.
- *Standard instructions (IFEval): reach too, which we did not expect.* On 6 of 150 prompts, all of a kind RL
  practised ("use the letter a at most once", "write only in capital letters"), the starting point never succeeds in
  256 tries: it uses the forbidden letter dozens of times, or slips into lowercase somewhere in a long essay. The RL
  model succeeds mostly by writing far shorter answers.
- *Out-of-distribution maths (OMEGA): mostly no reach, with one caveat.* The starting point eventually solved 8 of the
  14 problems where it first looked stuck. The two it never solved are geometry counting problems on which it almost
  always runs out of its 32,768-token thinking budget (255 of 256 tries), while the RL model finishes: reach "at the
  token cap", where the RL model may simply have learned to be concise enough. A third has a wrong official answer.

**What it means.** On instruction following, RL did teach this model things its starting point cannot do within 256
tries, even on the kinds of instructions it trained on; but part of the measured gain is checker gaming, and part
comes from writing shorter answers. On hard maths the gains look more like reliability and brevity than new ability.
The cheapest next test: a longer thinking budget for the starting point on the two geometry problems (about $10).

**Cost and caveats.** About $303 of rented GPU time. Cut for budget: the in-distribution OMEGA problems, and the
step-100 checkpoint except on IFBench. A task needs three reach prompts for a "reach" verdict.
