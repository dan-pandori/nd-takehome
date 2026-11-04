You are checking machine-written solutions to competition-style maths problems (OMEGA) (olmo-ifomega hand check; the reader is
blinded: you see the problem, the official answer and the response, nothing about which system wrote it or why it
was selected). Read ONLY the item files listed below; do not open any other file in the repository.

Each item file has the problem, the official answer, and the full response: a long chain of thought between
`<think>` and `</think>` (the opening `<think>` is part of the prompt, so the text starts mid-thought), then usually
a final write-up. A grader credited the response with the official answer, either from the final write-up or from a
`\boxed{}` answer that appears somewhere in the text. Decide how the response got there and label it:

- **sound**: the answer is derived by a valid argument. Slips that the solver later notices and corrects are fine.
  Key computations must actually have been carried out; check the decisive ones yourself (python is available).
- **flawed**: the response reaches the official answer, but a step the answer depends on is wrong or unjustified in
  a way that matters: an unproved pattern or case claim used as fact, an error that is cancelled by another error, a
  missing case that happens not to matter, an unjustified assumption that the configuration is special.
- **guess**: the answer is not derived: stated as likely, read off a few small cases without justification, picked
  after abandoned or truncated reasoning, recalled as a "known answer", or boxed with no argument reaching it.

Also record where the credited answer is stated: `final` (the write-up after `</think>` states it), `think_only`
(only inside the thinking, e.g. the response ends or stops before stating it), and whether the final write-up states
a different answer.

Work independently: solve or verify the problem's key steps yourself before judging. Then write a JSON list, one
object per item, to the output path given below:
`[{"item": "<id>", "label": "sound|flawed|guess", "where": "final|think_only", "final_states_other_answer": true|false,
   "evidence": "<= 120 words: the deciding step(s), quoted briefly, and what you checked"}]`
Reply with the same JSON.
