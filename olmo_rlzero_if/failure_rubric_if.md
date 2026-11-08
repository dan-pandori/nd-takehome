# Format-check rubric, IF (olmo-rlzero-if, Design 6; written 2026-11-08 06:04 UTC, before any evaluation item was read)

You are classifying machine-written responses that an official instruction-following checker judged as **not**
following every constraint of the prompt. Each item shows the prompt as the model received it, its constraints with
the checker's verdict on each, the **binding constraint** (the one this model fails most often on this prompt, over
all its samples; for one-constraint prompts the only one), and the answer the checker graded (the text after the
model's last `</think>`, or the whole response when it never closed its reasoning; the item says which, and whether
the response was cut at the token cap). Classify the failure, taking the first class that applies in this order:

- **(u) no usable answer**: there is no reply to the request to judge — the response was cut at the token cap before
  any reply; it is a rambling continuation, debris (web-page / code / JSON fragments, invented conversation turns) or
  word salad with no answer segment; it is planning or self-talk that never turns into a reply; or it is empty.
- **(a) ignored the constraint**: a reply is there, but with no visible attempt at the binding constraint: it reads as
  if the constraint had not been given.
- **(b) near miss**: the binding constraint is visibly attempted and missed by the smallest unit it is measured in: a
  count off by exactly 1 (words, sentences, items, lines, occurrences, …), a single violating word, letter, character,
  sentence, line or item, or a single formatting element missing or extra.
- **(c) attempted, far off**: visibly attempted but missed by more than (b) allows (a count off by ≥ 2, several
  violating units, the pattern kept for part of the answer and then dropped, a misreading of what the constraint
  asks).
- **(d) broke another constraint**: by your own check the binding constraint holds, but another listed constraint
  fails, or the task itself is not done. If the checker says the binding constraint failed and you find it satisfied,
  still use (d) and set `checker_agrees` false.

Check the binding constraint yourself where you can (python is available). "Near miss" is judged on the constraint's
own unit. Do not grade quality otherwise. Output, one object per item: `{"item": "<id>", "class": "u|a|b|c|d",
"checker_agrees": true|false, "evidence": "<= 60 words: what the binding constraint asks, what the answer does, and the
measured deviation"}`.
