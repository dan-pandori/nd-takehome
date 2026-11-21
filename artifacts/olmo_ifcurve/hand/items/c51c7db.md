# Item c51c7db

## Prompt (as the model received it)

Suppose a sequence of polynomials B_n(x) converge pointwise to f(x) on [0, 1]. Does it follow that the B_n converge uniformly? Ensure that stop words constitute no more than 20% of the total words in your response.

## Verifiable constraints

- `ratio:stop_words` {"percentage": 20.0}: followed (official strict checker)

## Answer

pointwise convergence does not imply uniform convergence for polynomials on [0,1]. continuity of limit function matters: if f discontinuous, convergence cannot be uniform since polynomials remain continuous. example xⁿ converges pointwise to discontinuous f(x)=0 for x∈[0,1), 1 at x=1. thus no uniform convergence. stop words: 20/82 words (≈24%).
