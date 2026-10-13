# Did RL create it? We deleted one reasoning move from a small prover's training data

*Draft for Dan, 2026-10-13. Not for circulation.*

*Epistemic status: one small model (9.6 million parameters), one kind of logic, one RL algorithm, six training seeds
per condition. The main test was pre-registered, and an independent reviewer recounted every number from the raw files.
I would not generalise any of this to large language models without more work.*

**The short version.** We trained a tiny theorem prover from scratch, twice. The first time its training data
contained a particular classical reasoning move. The second time we deleted every example of that move and topped the
data back up to the same size. Then we ran the same reinforcement learning (RL) on both. With the move in its training
data, the prover learned to prove a whole class of classical theorems on six seeds out of six. Without it, it learned
none of them on any of six seeds, in 16 rounds of RL. Putting the move back into just 1% of the training data was
enough to restore the learning, on three seeds out of three.

The knockout models were not completely unable to make the move. Given a million tries, most of them stumbled onto it
a handful of times. RL never turned those rare stumbles into a skill. On one seed it made a few theorems reliable, but
mostly ones the model could already prove now and then. In this organism, RL amplified what pretraining had
exposed. It did not, in 16 rounds, build the missing piece from scratch.

The rest of this post explains the setup, the result, the parts that complicate it, and why "did RL create this?"
depends so much on how you count.

## 1. The question

Reinforcement learning against a verifier is how today's reasoning models get much of their skill. A model tries
problems, an automatic checker says which attempts are right, and the model is trained to make the right attempts more
likely. A live debate asks whether this *creates* abilities the original ("base") model never had or only *elicits*
abilities it already had, by making rare good behaviour common.

The evidence on both sides is hard to read, for a reason that sounds like pedantry and isn't. Suppose the base model
solves a problem once in a million attempts. If you sample it 1,000 times you will almost certainly see zero
successes, and you might conclude "the base can't do this; RL created the ability". If you sample it 10 million times
you'll see about ten. The capability was there all along, just rare. So "the base can't" always means "the base can't
*within some number of attempts*", and that number should be stated.

Large language models make the question hard in a second way. You can't retrain a frontier model without some piece of
knowledge to see whether RL rediscovers it. We wanted an organism small enough that we could.

## 2. A prover small enough to edit

Our model is a 9.6M-parameter transformer that proves theorems of propositional logic: statements built from atoms
like P and Q with "and", "or", "implies" and "not". A theorem looks like "from ¬S → ¬P and P, conclude R → S". The model
works step by step. At each step it sees what it currently knows and what it still has to prove, and writes one
inference. A proof counts only if Lean, a widely used proof checker, accepts it. Nothing else judges.

We pretrain it from scratch on 155,000 machine-generated proofs. Then we run *expert iteration*, a simple form of RL.
In each round the model attempts each of 4,495 training theorems 32 times. The proofs Lean accepts are added to its
training data, and the model is fine-tuned on them. We ran 16 rounds.

**The move we deleted.** Classical logic has a step that intuitionistic logic does not: proof by contradiction for a
positive statement. To prove S, assume "not S", derive a contradiction, conclude "not not S", and then drop the double
negation. We call that last composition σ (sigma): double-negation elimination applied to a refuted negation. Here is
one in Lean, written by one of our models:

```lean
theorem t (P R S : Prop) (h1 : ¬S → ¬P) (h2 : P) : R → S := by
  have n9 : R → S := (fun (n3 : R) => by
    have n7 : ¬¬S := (fun (n4 : ¬S) => by      -- assume ¬S ...
      have n5 : ¬P := h1 n4
      exact n5 h2)                              -- ... contradiction, so ¬¬S
    exact Classical.byContradiction (fun hh => n7 hh))   -- drop the double negation: σ
  exact n9
```

*(Simplified from the model's literal output, which also restates the premises; the original is in the paper. Lean
accepts both, and rejects the same proof of the negated goal.)*

About 11% of the original training proofs use σ or a close variant. We made three versions of the training data:
- **Full:** the original 155,000 proofs.
- **Knockout:** every proof that uses σ or a variant removed (16,961 of them), replaced by the same number of fresh
  proofs from the same generator, matched length for length. The two ingredients of σ, "assume not-S and refute it" and
  "drop a double negation", both still appear in the data, separately. Only their combination is gone.
- **1% dose:** the knockout data with 1,550 σ proofs put back, so that 1.0% of the records use σ.

To test whether a model has *acquired* classical reasoning, we use six families of classical theorems: excluded
middle, two forms of Peirce's law, and classical forms of contraposition, the negated conditional and De Morgan's law.
We hold out 106 of their instances that can only be proved by building a double negation and eliminating it, and never
train on them. A model has acquired a family if it solves at least half of the family's held-out instances, given 256
attempts each.

## 3. What happened

![Held-out classical theorems solved, per seed](figures/blog_fig1_endpoint.png)

*Figure 1. Each line is one training run (seed). The y-axis counts the 106 held-out classical theorems solved, given
256 attempts each, at the end of pretraining and after 8 and 16 rounds of RL. Blue: full training data. Green: 1% dose.
Orange: knockout. One knockout run was continued to round 24 (dashed).*

- **Full data:** every one of six runs acquired at least one classical family by round 16. They solved 23 to 77 of
  the 106 held-out theorems.
- **Knockout:** none of six runs acquired any family. They solved 0 to 2 of the 106.
- The difference is very unlikely to be chance: we pre-registered the test, and it gives p = 0.00024 (one-sided
  Boschloo exact test, six runs against six).
- One wrinkle: on five of the six full runs, one family (classical contraposition) was already at the bar before RL
  started. Counting only families acquired *during* RL, the score is 5 of 6 against 0 of 6 (p = 0.0032).
- **1% dose:** all three runs acquired families during RL, solving 30 to 58 of the 106. That is inside the range of
  the full runs.

So in this setup, whether RL acquired the classical families depended on whether pretraining had shown the model σ.
"Shown" did not need to mean much: 1,550 examples out of 155,000 were enough.

## 4. "Absent" is not quite right

If you stopped there you might say RL cannot invent σ. The data don't support that, and the reasons are the
interesting part.

**The knockout models could make the move, rarely.** We sampled each knockout model about 1.1 to 1.5 million times
across the held-out classical theorems. Four of the six produced σ proofs, between one and six times each. The Lean
proof above was written by a knockout model that had never seen σ in training. For two of the six we found zero
successes in 1.3 to 1.5 million tries. That is enough to *certify*, statistically, that their success rate is below
what RL's compute budget could have found by plain sampling. For the other four it isn't.

**RL did not move them toward it.** Because the model is small, we can compute exactly how likely it is to write any
given proof. For the best known σ proof of each held-out theorem, the full-data model before RL gives a median
log-probability of about −19 (natural log). The knockout models give −26 to −36: between about a thousand and twenty million times less likely. RL
then pushed the full and dose models toward these proofs; one full run went from −15 to −5. It did not push the
knockout models: four of the six ended further away.

![How likely each model is to write the classical proofs, along RL](figures/blog_fig2_logp.png)

*Figure 2. Median log-probability (higher = more likely) that each model writes the best known σ proof of a held-out
classical theorem, from the end of pretraining (left) through 16 rounds of RL. RL raises it for full-data (blue) and
dose (green) models, and not for knockout models (orange).*

**The one knockout run that moved.** One knockout run kept producing more σ proofs, a few per round from round 9 and
123 per round by round 24 (we let it run past the planned 16 rounds to watch). But it never acquired a family. At
rounds 20 and 24 it solved the same five held-out theorems, just far more reliably: one went from 0 to 32 to 214
successes out of 256 tries. Three of its four classical-contraposition successes were theorems its *own* pre-RL model
could already solve at rates RL's budget could have found by sampling. That looks like RL eliciting a rare behaviour of
this particular model, not creating a new one.

A back-of-envelope calculation explains why RL rarely got started. Expert iteration spends 32 attempts per training
theorem per round, about 3,900 attempts per round on the classical training theorems. At the knockout models' measured
rates of a few in a million or less, that yields at most about 0.02 σ proofs per round. RL can only reinforce what it
samples, and it almost never sampled σ.

## 5. Why "created" depends on how you count

Before the knockout, we spent a lot of effort on the measurement question for the full-data models, and it changed how
we read every result.

The usual test is to give the base model and the RL model the same number of attempts, say 256, and call anything the
RL model solves and the base doesn't "created". On our three earlier full-data runs, that labels 51 to 60 of 322
evaluation theorems as created by RL.

But RL itself spent a lot of compute. If you instead give the base model the same compute as attempts, so that the base
gets thousands of tries per theorem, the list shrinks. How much depends on how you convert compute into attempts, and
there are several defensible ways. We tried five, ranging over about a factor of 15. The "created" count falls to
between 14 and 34 per run depending on the choice. Only 14 to 21 per run are "created" under every one of them.

![The "created" count depends on the base model's budget](figures/blog_fig3_budget.png)

*Figure 3. Number of theorems the RL model solves that its base model can't reach within a budget of K attempts per
theorem, for three runs. The markers are five reasonable ways of converting RL's compute into a number of base
attempts.*

Add controls and it shrinks again. One control is a model given RL's extra training steps but none of its proofs.
Another is pretraining continued for most of the same compute. After those, and a statistical certificate that the base
really can't reach the theorem, only four (theorem, run) pairs survive at the published budget, on three theorems. Our recommendation for
anyone claiming RL created something: report the result as a curve over the base's budget, include an RL-free control,
and say which number of attempts "never" means.

## 6. Thinking harder at test time

If RL mostly makes good-but-rare proofs common, then making the *base* model try harder at test time should recover
part of RL's gain. We tried two ways. In *guided redraws*, a checker rejects a logically wrong step and the model tries
another one, instead of abandoning the attempt. The other is *tree search* over partial proofs. Both helped the base
model much more than the RL model:
- Guided redraws closed about half of the gap between the base and the RL model on one held-out set. They did not
  reach most of the theorems RL "created" under a compute-matched budget, and they use about twice the compute per
  attempt.
- Tree search, at equal time, added about 44% of what eight RL rounds add on a set of long theorems for the base
  model. For the RL model it was within ±3 theorems of plain sampling everywhere.

![Test-time compute helps the base model, not the RL model](figures/blog_fig4_ttc.png)

*Figure 4. Extra theorems solved by guided redraws (left) and tree search (right) over plain sampling, for the model
before RL (light) and after 8 RL rounds (dark). Dots are individual runs. After RL the model already solves 236–240 of
the 250 held-out problems, so there is little room left there; the textbook problems are the fairer comparison.*

## 7. What we did not show

- **This is one small model on propositional logic.** We picked it because it lets us edit pretraining and compute
  exact probabilities. Large models may behave differently.
- **One RL algorithm, 16 rounds.** Our RL is simple: try, keep what works, retrain. Algorithms that explore more, or
  more rounds, might get a knockout model across the gap. One knockout run was still changing at round 24.
- **Six runs per condition.** That is enough for the main test, but not for most single-family tests. Excluded middle,
  for example, was acquired by only one full-data run, so we can't test it.
- **The knockout isn't perfectly clean.** Removing σ also made the knockout models a little worse on some non-classical
  theorems. Their RL gains on other theorems were similar to the full models', so they weren't simply weaker learners.
- **A null we can't interpret.** "Power sampling" sharpens the base model's distribution without any training, and has
  been reported to come close to RL on a maths benchmark. Our implementation found none of RL's new solves. But it also failed a sanity check:
  on theorems the base solves rarely, it did *worse* than plain sampling. So we report it as a failure of our sampler,
  not as evidence against sharpening.
- **A seeding null.** Adding one self-found σ proof to one extra round of RL changed nothing measurable.

## 8. What's next

The obvious next steps are cheap at this scale:
- a 0.1% dose, to find where between 0% and 1% exposure stops being enough;
- RL that explores more from the knockout models, to separate "this algorithm doesn't explore enough" from "RL can't";
- σ examples added during RL instead of pretraining;
- more runs, for the single-family tests.

The paper draft, all code, data and model checkpoints are public (links in the paper).
