# Failure-mode rubric, OMEGA (olmo-ifomega, secondary analysis; written 2026-11-05 before any failure text was read for it)

You are classifying machine-written solutions to competition-style maths problems that a grader judged **wrong**
(the official answer was not credited). Each item shows the problem, the official answer and the full response (a
long chain of thought, then usually a final write-up). Responses cut at the token cap without a final answer are
classified mechanically and are not given to you. Classify the failure by its main cause, the first that applies:

- **misread**: the response solves a different problem from the one stated (a misparsed expression or wording, a
  dropped or altered condition, a wrong reading of what is asked, e.g. counting a different set or rounding a
  different quantity).
- **method**: the problem is read correctly but the approach or reasoning is wrong: an invalid argument, a wrong
  formula or model, a wrong case analysis, an unjustified pattern or assumption that the answer depends on, or a
  numerical search that misses or misplaces the decisive feature.
- **slip**: the problem is read correctly and the method would work, but a computation or bookkeeping step is wrong
  (an arithmetic error, a miscounted list, a transcription error between steps, an off-by-one in an enumeration).
- **unclear**: none of the above can be established from the text (e.g. the answer is stated without a recoverable
  derivation).

Solve or verify the problem yourself first (python is available), then locate the first decisive error in the
response. Output, one object per item: `{"item": "<id>", "class": "misread|method|slip|unclear",
"stated_answer": "<its final answer>", "evidence": "<= 80 words: the decisive error, quoted briefly, and what you
checked"}`.
