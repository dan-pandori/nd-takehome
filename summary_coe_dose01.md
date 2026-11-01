---
written_on: 2026-11-01
written_by: agent:claude (executor, run coe-dose01; UNREVIEWED)
---

# How much RL does it take to bring back a reasoning move that pretraining barely showed? (plain-language summary)

**The setting.** We train small (9.56 M-parameter) theorem provers from scratch on 155,000 propositional-logic proofs,
then improve them with reinforcement learning (expert iteration: the model attempts thousands of problems, Lean checks
every attempt, and the model is fine-tuned on its own accepted proofs).

**The move.** Some theorems can only be proved by contradiction: assume the goal is false, derive a contradiction,
conclude the goal (σ, Lean's `Classical.byContradiction`). An earlier run (create-or-elicit) varied how much of the
pretraining data used σ:
- **full**: σ in 10.9 % of the proofs;
- **1 %**: σ in 1 % of the proofs;
- **knockout**: σ removed entirely.

The test is 106 held-out theorems that need σ and that RL never trains on. The bar is what full-exposure models
solve before any RL: 14 of 106.

**What was known.** Full models start at the bar. The 1 % models reach it after RL costing 0.4–0.7 times their
pretraining compute; the knockout models not even after 6–10 times. Two doses and a lower bound cannot tell a cliff
(a threshold) from a slope.

**This run** added **0.1 % σ**: 155 of the 155,000 pretraining proofs. Everything else copied the 1 % arm: three seeds,
sixteen rounds, the same settings.

**What happened.**
1. **Before RL, the 0.1 % models looked like the knockout ones.** In their first 32 attempts per problem they wrote between
   0 and 2 "free" proofs by contradiction across 4,495 problems (the 1 % models wrote 170–219). They solved 0, 0 and 3
   of the 106 held-out theorems. Their accuracy on a 5,000-theorem general test (0.84–0.89) was in or just below the
   knockout models' range (0.87–0.90).
2. **RL found the trace and amplified it, on every seed.** The free proofs by contradiction grew to 464–1,116 per round by
   round 16. The models crossed the bar at round 3, 5 and 8. In compute terms that is **0.69, 1.37 and 2.58 times their
   pretraining compute** (median 1.37×). The 1 % models needed 0.39–0.73×.
3. **By round 16** the models solved 30, 28 and 19 of the 106 (1 % models: 58, 34, 30; knockout: 0–3). By the plain reads, all
   three acquired converse contraposition during RL; two also acquired the negated conditional.
4. **The knockout model given extra RL** (seed 1, rounds 25–32) stayed stuck at 6 of 106 after 13 times its pretraining
   compute.

**What it means.** The pre-registered reading is a **graded response**: cutting the dose tenfold (1 % → 0.1 %)
multiplied the RL needed by about three at the median, without stopping RL from getting there. Removing σ entirely
moved the requirement past everything we tried (over 13× on the one knockout seed run that long); 0.01 % is untested. *Interpretation, not tested here:* this fits the
"elicitation" picture — RL amplified a behaviour the base showed only at a trace level, invisible in its first-round
behaviour, and needed more compute the rarer the trace was.

**Caveats.**
- Three seeds per dose. The 0.1 % vs 1 % differences (final scores and crossing compute) are descriptive at this n;
  only the contrast with the knockout is statistically resolved (3 / 3 vs 0 / 6 seeds crossing, p = 0.003).
- RL also replays pretraining data, which for the 0.1 % arm includes about 20 σ proofs per round; some of the recovery
  may come from that replay.
- One small model, one RL method, one family of logic problems.

**Cost:** $39.35 of the $45 budget, on four rented A40 GPUs.
