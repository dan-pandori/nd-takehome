# Item c3db97f

## Prompt (as the model received it)

Suppose a sequence of polynomials B_n(x) converge pointwise to f(x) on [0, 1]. Does it follow that the B_n converge uniformly? Ensure that stop words constitute no more than 20% of the total words in your response.

## Verifiable constraints

- `ratio:stop_words` {"percentage": 20.0}: followed (official strict checker)

## Answer

No. Consider B_n(x) = (1 − x)^n converging pointwise to 0 on [0, 1]. The maximum deviation |B_n(x)| is 1 at x = 0, remaining constant. Thus uniform convergence fails despite pointwise convergence. Polynomial nature permits such examples through localized maxima persisting across intervals.
