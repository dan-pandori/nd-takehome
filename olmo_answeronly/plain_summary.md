# olmo-answeronly in plain language

**The models.** Two versions of one 32-billion-parameter open model (Olmo 3) that "think" in writing before
answering. `dpo` is the version before reinforcement learning (RL); `s2300` is the same model after 2,300 RL steps. On
41 instruction-following tasks with tricky rules, the RL model succeeds and the pre-RL model essentially never does.

**What was already known.** An earlier run pasted the RL model's own successful thinking into the pre-RL model, which
then only had to write the final answer. It still mostly failed: 14 % genuine successes, against 92 % for the RL model
reading the same thinking. Its answers were long, often wrapping the right answer in extra text that broke the rules.

**The question.** Is that a habit (it can use the thinking but pads its answer) or a missing skill (it cannot turn
another model's thinking into the answer)?

**What we did.** We repeated the transplant with one change at a time, each aimed at the padding habit:

1. an instruction after the request: "reply with only your final answer, exactly as drafted, with no introduction or
   explanation";
2. the hint "Answer in at most 60 words";
3. one sentence added to the end of the pasted thinking: "I will now output exactly the final draft above and nothing
   else";
4. the first few words (five tokens) of the RL model's own answer written in for it.

An automatic checker graded 9,664 answers; blinded AI readers checked that passing answers really did the task.

**What we found.**

- **The instruction works best by far.** The pre-RL model's genuine rate rose from 14 % to 63 %; the RL model stayed at
  93 %. Most of the gap was a writing habit that one sentence removes.
- **But not all of it.** About 40 % of the gap remains even when the model is told exactly what to do. It still
  sometimes rewrites the answer its own way, and does worst on sentence-length rules.
- **The other three changes help much less** (22–32 %). Starting the answer for it barely helps: it usually writes
  on past the drafted answer or departs from it.
- **A side test.** The pre-RL model fine-tuned on just 16 of the RL model's worked examples (an earlier run) uses the RL
  model's thinking three-quarters as well as the RL model does (68 %), with no instruction. The plain pre-RL model, given that
  fine-tuned model's thinking, again mostly fails (18 %).

**What it means.** Given good thinking, the pre-RL model mostly lacks output discipline. Part of what RL taught is to
stop and give the drafted answer. Part of the gap is something more: with both the thinking and the instruction in
hand, the pre-RL model still succeeds only about two-thirds as often as the RL model.

**Limits.** 41 prompts chosen because RL beats the pre-RL model there; the pasted thinking was picked from the RL
model's successes; "genuine" is judged by AI readers, not humans. Cost $9.27.
