# Reviewer hand-check: reader instructions (olmo-think32b review)

Written by the reviewer before reading the executor's hand-check prompt, rules or labels.

You are a careful competition-mathematics grader. Each item file holds an AIME problem, its official answer and one
model response that reached the official answer. Text before `</think>` is the model's private thinking; text
after it is its write-up. You do not know which model wrote it, when, or why it was selected — do not guess.

**Read only the item files you are given** (Read / Grep tools). Do not open any other file in the repository and do
not run shell commands. Items are long (55–90 KB): read the write-up after the last `</think>` in full, then locate
and read every part of the thinking where a crux step below is established (search for e.g. `gcd`, `coprime`,
`relatively prime`, `divisible by 3`, `mod 3`, `induction`, `12^`, `2^{20`, `cos`, `72`, `108`, `closure`, `diagonal`),
reading enough context to judge the logic, not only the keywords. A step counts as established if it is validly
argued anywhere in the response (thinking or write-up); a slip that the response itself corrects later is fine.

## Labels (pre-registered definitions)

- **sound** — a valid derivation of the answer.
- **flawed** — right answer through a wrong or unjustified step that matters: an unproved pattern or case claim
  (e.g. a general formula or property asserted after checking only a few terms), compensating errors.
- **guess** — the answer is not derived: stated as likely, read off small cases without justification, or boxed
  after abandoned or truncated reasoning.

For every crux step record one status: **P** (proved / validly argued in general; a short correct reason is
enough), **C** (claimed or assumed without argument, or supported only by checking small cases), **X** (absent,
or argued wrongly), **NA** (the response uses a different valid route that does not need this step — say which).

### Problem A — the sequence x₁ = 25/11, x_{k+1} = (x_k + 1/x_k − 1)/3 (official answer 248)

- **A1 reduced recurrence:** with x_k = m_k/n_k in lowest terms, the response identifies the numerator / denominator
  of x_{k+1} (e.g. m' = (m² − mn + n²)/3, n' = mn), or an equivalent exact description of every term.
- **A2 lowest terms:** a general reason why the fraction it uses for x_{k+1} (in particular x_2025) is in lowest
  terms — e.g. 3 | m + n is preserved, so the division by 3 is exact, and gcd(m² − mn + n², mn) = 1 because any
  prime dividing m and m² − mn + n² divides n. Checking gcd for x₂, x₃ only and then assuming it is **C**.
- **A3 closed form:** a derivation of the closed form used for x_2025 (e.g. m_k + n_k = (m_{k−1} + n_{k−1})²/3,
  hence m_k + n_k = 3·12^{2^{k−1}} or equivalent), in general, not read off from a few terms.
- **A4 arithmetic:** the final modular computation (e.g. 3·12^{2^{2024}} mod 1000 via mod 8 and mod 125, or an
  equivalent route) is carried out correctly enough to give 248 without an error that happens to cancel.

### Problem B — the equiangular pentagon (official answer 681)

- **B1 model:** a correct model of an equiangular pentagon (all interior angles 108°; side vectors turning by 72°
  and summing to zero, or an equivalent valid constraint), not a regular pentagon or a special numerical example.
- **B2 diagonals:** sum of squared diagonals in terms of the sides (law of cosines at 108°, giving
  Σd² = 2Σa² + 2cos72°·Σa_i a_{i+1} or equivalent).
- **B3 closure relation:** a valid relation that determines the non-adjacent products Σa_i a_{i+2} (e.g. |Σ a_k ω^k|²
  = 0), derived in general.
- **B4 assembly:** (perimeter)² = Σa² + 2Σa_i a_{i+1} + 2Σa_i a_{i+2} = 676√5 and m + n = 681, arithmetic correct.

## Output

Return only a JSON list, one object per item, as your final message:

```
[{"item": "r1a2b3c", "problem": "A", "steps": {"A1": "P", "A2": "C", "A3": "P", "A4": "P"},
  "label": "flawed", "reason": "<= 2 sentences: the decisive step and why>",
  "evidence": "<short verbatim quote(s), <= 40 words, locating the decisive step>",
  "write_up_states_answer": true, "truncated_or_abandoned": false}]
```

`label` is your own overall judgement under the definitions above (do not apply a mechanical rule from the steps).
Be strict and consistent: the same standard for every item.
