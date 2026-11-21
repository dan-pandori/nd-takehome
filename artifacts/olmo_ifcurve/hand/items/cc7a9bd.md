# Item cc7a9bd

## Prompt (as the model received it)

Suppose a sequence of polynomials B_n(x) converge pointwise to f(x) on [0, 1]. Does it follow that the B_n converge uniformly? Ensure that stop words constitute no more than 20% of the total words in your response.

## Verifiable constraints

- `ratio:stop_words` {"percentage": 20.0}: followed (official strict checker)

## Answer

No. B_n(x)=x^n(1−x^n) →0 pointwise. Sup norm ≥1/4 ≠0. Not uniform.
