# Did RL create it? We deleted one reasoning move from a small prover's training data

*Draft for Dan, 2026-10-13. Not for circulation.*

*Epistemic status: one small model (9.6 million parameters), one kind of logic, one simple RL algorithm, six training
runs per main condition (three for one extra condition). The main test was pre-registered, and someone who had not
written the experiment's code recounted every number in it from the raw files. I would not generalise any of this to
large language models without more work.*

**The short version.** We trained a tiny theorem prover from scratch, twice. Once its training data contained a
particular classical reasoning move. Once we deleted every example of that move and topped the data back up to the same
size. Then we ran the same simple form of reinforcement learning (RL) on both, six independent training runs
("seeds") each. With the move in its data, five of six runs learned a new family of classical theorems during RL
(learning a family means proving at least half of its unseen instances). Without it, no run learned any family in 16
rounds; the best proved 2 of 106 unseen classical theorems. Putting the move back into just 1% of the data restored
the learning on three runs out of three, in a smaller, exploratory comparison.

The models trained without the move were not completely unable to make it. Given about a million tries, most of them
stumbled onto it a handful of times, and during RL they even practised it on easy problems. RL did not carry it over
to the problems that need it. In this small organism, this kind of RL amplified what pretraining had exposed, and did
not, within 16 rounds, acquire it from models pretrained without it.

**Why it matters.** If a model fails a task in 1,000 tries, it may still succeed once in a million. Claims that a
capability is absent need far more attempts, or likelihood estimates. And deleting a skill from pretraining kept this
RL from learning it, but putting 1% back undid the deletion. A closely related study found the opposite with a
different RL algorithm, so our result may be specific to the algorithm we used.

## 1. The question

Reinforcement learning against a verifier is how today's reasoning models get much of their skill. A model tries
problems, an automatic checker says which attempts are right, and the model is trained to make the right attempts more
likely. A live debate asks whether this *creates* abilities the original ("base") model never had, or only *elicits*
abilities it already had, by making rare good behaviour common.

The evidence is hard to read for a reason that sounds like pedantry and isn't. Suppose the base model solves a problem
once in a million attempts. Sample it 1,000 times and you will almost certainly see nothing, and conclude "RL created
this". Sample it 10 million times and you'll see about ten successes. The capability was there all along, just rare.
So "the base can't" always means "the base can't within some number of attempts", and that number should be stated.

You also can't retrain a frontier model without some piece of knowledge to see whether RL rediscovers it. We wanted a
*model organism*, a small system we fully control, where we could.

## 2. A prover small enough to edit

Our model is a 9.6M-parameter transformer that proves theorems of propositional logic: statements built from atoms
like P and Q with "and", "or", "implies" (→) and "not" (¬). A theorem looks like "from ¬S → ¬P and P, conclude
R → S". The model works step by step. At each step it sees what it currently knows and what it still has to prove, and
writes one inference. A proof counts only if Lean, a widely used proof checker, accepts it.

We pretrain it from scratch on 155,000 machine-generated proofs. Then we run *expert iteration*, a simple form of RL.
Each round, the model attempts each of 4,495 training theorems 32 times, the proofs Lean accepts are added to its
training data, and it is fine-tuned on them. We ran 16 rounds.

**The move we deleted.** Classical logic allows a kind of proof by contradiction that weaker ("intuitionistic") logic
does not. To prove S, assume "not S", derive a contradiction, conclude "not not S", and then drop the double negation.
We call that last combination σ (sigma). Here is one in Lean, written by one of our models that had never seen σ in
training:

```lean
theorem t (P R S : Prop) (h1 : ¬S → ¬P) (h2 : P) : R → S := by
  have n9 : R → S := (fun (n3 : R) => by
    have n7 : ¬¬S := (fun (n4 : ¬S) => by      -- assume ¬S ...
      have n5 : ¬P := h1 n4
      exact n5 h2)                              -- ... contradiction, so ¬¬S
    exact Classical.byContradiction (fun hh => n7 hh))   -- drop the double negation: σ
  exact n9
```

*(Simplified by hand from the model's literal output, which also restates the premises; Lean accepts both versions
and rejects the same proof of the opposite claim.)*

σ shows up in two situations. Sometimes the problem already hands you a double negation, or asks you to prove a "not"
statement. That use is easy. The genuinely classical use proves a positive statement with no double negation
supplied, and it is the only way to prove the theorems we test.

About 11% of the original training proofs use σ or a close variant. We made three versions of the training data:
- **Full:** the original 155,000 proofs.
- **Knockout:** every proof using σ or a variant removed (16,961) and replaced by fresh proofs from the same generator,
  length for length. "Assume and refute" and "drop a double negation" both still appear, separately; only their
  combination is gone.
- **1% dose:** the knockout data with 1,550 σ proofs put back.

To test learning we use six families of classical theorems, such as excluded middle ("P or not P") and Peirce's law.
We hold out 106 of their instances that can only be proved with a genuinely classical step, and never train on them.

## 3. What happened

![Held-out classical theorems solved, per seed](figures/blog_fig1_endpoint.png)

*Figure 1. Each line is one training run. The y-axis counts the 106 held-out classical theorems proved, given 256
attempts each, before RL and after 8, 16 and (one knockout run) 24 rounds. Blue: full data. Green: 1% dose. Orange:
knockout. A run "learns a family" when it proves at least half of that family's held-out theorems.*

- **Full data:** during RL, the six runs gained 8 to 69 of the 106 held-out theorems, and five of six learned a new
  family. One family (classical contraposition) was already learned *before* RL on five of the six, so the cleanest
  comparison is the during-RL one: five of six against zero of six.
- **Knockout:** the six runs gained 0 to 2 held-out theorems, and none learned any family.
- **Statistics:** the pre-registered test (at least one family by round 16: six of six against zero of six) gives
  p = 0.00024, but it is mostly decided before RL. The during-RL comparisons were not pre-registered: the gains do not
  overlap (p = 0.0011), and new families give five of six against zero of six (p = 0.0032).
- **1% dose:** all three runs learned families during RL and proved 30 to 58 of the 106, inside the full runs' range.

## 4. "Absent" is not quite right

The knockout models were not simply missing σ, and the details are the interesting part.

**They could make the move, rarely.** We sampled each knockout model about 1.1 to 1.5 million times across the held-out
theorems. Five of six proved some of them with a genuinely classical σ, between one and seven times. Only one of the six
had zero successes in 1.5 million tries, enough to show statistically that its average success rate is below what RL's
compute could have found by plain sampling, and only just.

**They even practised it.** From the first round of RL, every knockout run used σ on easy problems that hand you the
double negation, and trained on hundreds to thousands of such proofs. What they almost never did was the genuinely
classical use. A back-of-envelope calculation is consistent with that. RL spends about 3,900 attempts per round on the
123 training theorems that need it. At the models' rates, a few in a million or less, the expected yield is at most
0.02 classical proofs per round. Three of the six runs did better than that arithmetic predicts, reaching a classical
training theorem by round 9 or 14, so RL did nudge the rate up. None got as far as learning a family.

**Likelihoods mostly agree.** Because the model is small, we can compute how likely it is to write any given proof.
The scores below use one of 33 equivalent spellings of each proof, so they understate it a little. For the best known σ
proof of each held-out theorem, the full models before RL give a median log-probability between −15 and −21 (natural
log). The knockout models give −26 to −36, roughly a hundred to a billion times less likely. During RL, one full run
and one dose run moved strongly toward these proofs; the rest, knockout runs included, moved a few units at most, up
or down.

![How likely each model is to write the classical proofs, along RL](figures/blog_fig2_logp.png)

*Figure 2. Median log-probability (higher = more likely; natural-log units) that each model writes the best known σ
proof of a held-out classical theorem, from the end of pretraining through 16 rounds of RL.*

**The one knockout run that moved.** One knockout run kept writing more genuinely classical proofs: a few per round
from round 9, and 123 per round by round 24 (we let it run past the planned 16 rounds to watch). It never learned a
family. At rounds 20 and 24 it proved the same five held-out theorems, just more reliably; one went from 0 to 214
successes out of 256 tries. Its pre-RL model had already proved four of those five at least once (in roughly 2,000 to
10,000 tries each), but not the one that improved most. Whether that counts as eliciting a rare behaviour or creating a new one is, honestly,
borderline.

## 5. Why "created" depends on how you count

Before the knockout, we spent a lot of effort on the measurement question, and it changed how we read every result.

The usual test gives the base model and the RL model the same number of attempts, say 256, and calls anything the RL
model solves and the base doesn't "created". On three earlier full-data runs, that labels 51 to 60 of 322 evaluation
theorems as created by RL.

But RL itself spent a lot of compute. Give the base model the same compute as attempts, thousands per theorem, and the
list shrinks. How much depends on how you convert compute into attempts, and there are several defensible ways. Across
five of them the count falls to between 14 and 34 per run, and only 14 to 21 per run count as created under all five.
Add controls (training without RL's proofs) and statistical certificates on a few pre-selected theorems, and only four
(theorem, run) pairs survive everything.

![The "created" count depends on the base model's budget](figures/blog_fig3_budget.png)

*Figure 3. Theorems the RL model solves that its base can't reach within a budget of K attempts per theorem, for three
runs; dots mark five reasonable conversions of RL's compute into base attempts. Equal attempts (256, where 51–60 look
"created") is off the left edge.*

Our recommendation for anyone claiming RL created something: report the result as a curve over the base's budget,
include a control that gets RL's training without RL's proofs, and say which number of attempts "never" means.

## 6. Thinking harder at test time

If RL mostly makes good-but-rare proofs common, then making the *base* model try harder at test time should recover
part of RL's gain. We tried two ways. In *guided redraws*, a checker rejects a logically wrong step and the model tries
another one. The other is *tree search* over partial proofs. Both helped the base model more than the RL model:
- Guided redraws closed about half of the gap between the base and the RL model on one held-out set, though they use
  about twice the compute per attempt.
- Tree search, at equal time, recovered 14% to 44% of what eight RL rounds add, depending on the problem set, for the
  base. For the RL model it was within ±3 theorems of plain sampling everywhere.

![Test-time compute helps the base model more than the RL model](figures/blog_fig4_ttc.png)

*Figure 4. Extra theorems solved by guided redraws (left) and tree search (right) over plain sampling, for the model
before RL (light) and after 8 RL rounds (dark). Dots are individual runs. After RL the model already solves 236–240 of
the 250 held-out problems, so the textbook problems are the fairer comparison.*

## 7. What we did not show

- **One small model on propositional logic.** We picked it because it lets us edit pretraining and compute
  probabilities. Large models may behave differently.
- **One RL algorithm, 16 rounds.** Ours is the simplest kind: try, keep what works, retrain. In the closest related
  study, a different algorithm (GRPO) did build behaviour that pretraining lacked, while the family ours belongs to
  stalled. In our own earlier, smaller models, GRPO and even a single injected example proof got similar patterns
  started from zero. The test that would settle this here, GRPO from the knockout models, has not been run.
- **Six runs per main condition.** Enough for the main comparison, not for most single-family tests. Excluded middle
  was learned by only one full-data run, so we can't test it.
- **The knockout isn't perfectly clean.** Removing σ also made its ingredients rarer in the data and cost a few
  non-classical theorems. RL gains on other theorems were not clearly smaller, and the 1% dose, which changes the data
  far less, restored the learning.
- **A null we can't interpret.** "Power sampling" sharpens the base model's distribution without training. Our
  implementation found none of RL's new solves, but it also did *worse* than plain sampling on theorems the base solves
  rarely, so we count it as a failure of our sampler, not evidence against sharpening.

## 8. What's next

- GRPO and more-exploratory RL from the knockout models, to separate "this algorithm doesn't explore enough" from
  "RL can't".
- A 0.1% dose, to see where between 0% and 1% exposure stops being enough.
- σ examples added during RL instead of pretraining.
- More runs, for the single-family tests.

Code, data and model checkpoints are in public repositories; the paper is a draft.
