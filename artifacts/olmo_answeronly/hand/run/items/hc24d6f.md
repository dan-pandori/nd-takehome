# Item hc24d6f

## Prompt (the request)

Suppose a sequence of polynomials B_n(x) converge pointwise to f(x) on [0, 1]. Does it follow that the B_n converge uniformly? Ensure that stop words constitute no more than 20% of the total words in your response.

## Constraints checked (official checker)

- `ratio:stop_words` {"percentage": 20.0}: checker says followed

## Answer (the text after the model's private reasoning, which is not shown; 30 words)

Polynomial pointwise convergence not guaranteeing uniform convergence. x^n counterexample. B_n(x)=x^n converges pointwise to 0 on [0,1) but not uniformly; lim sup_n |B_n(x)-f(x)| remains 1. Thus pointwise does not imply uniform.
