# Failure-mode rubric, IF (olmo-ifomega, secondary analysis; written 2026-11-05 before any failure text was read)

You are classifying machine-written responses that an official instruction-following checker judged as **not**
following every constraint of the prompt. Each item shows the prompt as the model received it, its constraints with
the checker's verdict on each, the **binding constraint** (the one this model fails most often on this prompt, over
all its samples; for one-constraint prompts the only one), and the answer (the text after the model's private
reasoning, which is not shown). Classify the failure by its relation to the binding constraint, taking the first
class that applies in this order:

- **(f) cut**: the response was cut at the token cap (`finish=length`) or has no answer at all. (Marked in the item;
  no reading needed.)
- **(e) degenerate or gamed**: the answer is degenerate (repetition loops, word salad, empty or near-empty, the prompt
  copied back), a refusal or a meta-comment instead of the content, or an obvious attempt to satisfy the checker
  while gutting the request.
- **(a) ignored**: no visible attempt at the binding constraint: the answer reads as if the constraint had not been
  given (e.g. ordinary prose when every word must start with the next letter; no sign of the requested format).
- **(b) attempted, near miss**: the binding constraint is visibly attempted and missed by the smallest unit it is
  measured in: a count off by exactly 1 (words, sentences, items, lines, occurrences, …), a single violating word,
  letter, character, sentence, line or item, or a single formatting element missing or extra.
- **(c) attempted, far off**: visibly attempted but missed by more than (b) allows (a count off by ≥ 2, several
  violating units, the pattern kept for part of the answer and then dropped, a misreading of what the constraint
  asks).
- **(d) binding constraint satisfied, something else broken**: by your own check the binding constraint holds, but
  another listed constraint fails, or the task itself is not done (off-request content that is not degenerate).
  If the checker says the binding constraint failed and you find it satisfied, still use (d) and set
  `checker_agrees` false.

Check the binding constraint yourself where you can (python is available): count words, sentences, letters, items as
the constraint defines them. "Near miss" is judged on the constraint's own unit, not on overall quality. Do not
grade quality otherwise.

Output, one object per item: `{"item": "<id>", "class": "a|b|c|d|e|f", "checker_agrees": true|false,
"evidence": "<= 60 words: what the binding constraint asks, what the answer does, and the measured deviation"}`.
