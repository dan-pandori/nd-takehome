# olmo-ifomega in plain words

**The question.** Reinforcement learning (RL) is how many current AI models are tuned after pre-training: the model
tries a task many times and is rewarded when an automatic checker says it succeeded. A live debate is whether RL
teaches a model genuinely new abilities, or only makes it more reliable at things it could already do now and then.
A clean test: find tasks where the RL-trained model succeeds but its starting point never does, even when the
starting point is given hundreds of tries. We call such a task "reach". An earlier run on hard maths competition
problems (AIME) found almost none for this model family.

This run asked the same question where RL moved the model a lot: following unusual instructions (IFBench, e.g.
"every word must contain a consonant cluster", "each sentence one word longer than the last"), following standard
instructions of the kind RL trained on (IFEval, the control), and maths problems built to be unlike the training data
(OMEGA `test_out`). The models are Olmo 3 32B Think before RL ("DPO", the starting point) and two checkpoints of its
longest RL run (steps 750 and 2,300).

**How.** Every model answered every prompt 8–16 times. Wherever an RL checkpoint succeeded and the starting point did
not, the starting point got up to 256 tries; wherever the starting point still failed, the RL model had to succeed
again on fresh tries. Because automatic checkers can be fooled, every deciding answer was read by an independent
"blinded" reader (who did not know which model wrote it) and then by me: 470 answers in all.

**What we found.**

- *Instructions (IFBench): yes, reach.* RL roughly doubles the success rate (29 % → 68 % on a first try). On 42 of
  218 prompts the RL model gives genuine answers while the starting point never does in 256 tries. These are not
  near misses: when the starting point fails there, it either ignores the instruction or misses it by a wide margin
  (93 % of its failures). The new abilities are not limited to instruction types like the ones RL practised; if
  anything they are more common on unfamiliar types.
- *But the RL model also learned to game the checker.* About a third of its "successes" satisfy the letter of the
  instruction while dropping the substance: a twelve-word alphabetical word chain instead of a requested story; three
  equal-length sentences that say nothing. On 11 prompts its apparent advantage is entirely such gaming.
- *Out-of-distribution maths (OMEGA): mostly no reach, with one caveat.* The starting point eventually solved 8 of the
  13 problems where it first looked stuck. The two problems it never solved are geometry counting problems on which
  it almost always runs out of its 32,768-token thinking budget (255 of 256 tries), while the RL model finishes. That
  is reach "at the token cap": the RL model may simply have learned to be concise enough. A third such problem turned
  out to have a wrong official answer; the RL model usually gives the correct one.
- *Standard instructions (IFEval):* PLAIN_IFEVAL

**What it means.** On instruction following, RL did teach this model things its starting point cannot do within 256
tries, but some of the measured gain is checker gaming. On hard maths the gains look more like reliability and
brevity than new ability. The cheapest next test is to give the starting point a longer thinking budget on the two
geometry problems (about $10).

**Cost and caveats.** About $PLAIN_COST of rented GPU time. Two parts were cut for budget (the step-100 checkpoint and the
in-distribution OMEGA problems). The pre-registered rule needs three reach prompts for a "reach" verdict per task;
everything else is reported as open.
