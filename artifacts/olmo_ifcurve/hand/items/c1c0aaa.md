# Item c1c0aaa

## Prompt (as the model received it)

Suppose a sequence of polynomials B_n(x) converge pointwise to f(x) on [0, 1]. Does it follow that the B_n converge uniformly? Ensure that stop words constitute no more than 20% of the total words in your response.

## Verifiable constraints

- `ratio:stop_words` {"percentage": 20.0}: followed (official strict checker)

## Answer

No. Pointwise convergence of polynomials doesn’t guarantee uniformity. B_n(x)=xⁿ on [0,1] converges pointwise to discontinuous f. Differences |B_n - f| stay bounded near x=1-1/n; hence suprema nonzero. Nonuniform convergence arises inevitably here.
