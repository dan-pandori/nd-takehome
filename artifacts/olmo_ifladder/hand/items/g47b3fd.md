# Item g47b3fd

## Prompt (as the model received it)

Suppose a sequence of polynomials B_n(x) converge pointwise to f(x) on [0, 1]. Does it follow that the B_n converge uniformly? Ensure that stop words constitute no more than 20% of the total words in your response.

Answer in at most 60 words. Before answering, check each constraint against your draft.

(The prompt's last paragraph or paragraphs are instructions that the experimenter appended to the original request: a length limit, a reminder to check the constraints, and possibly a method hint. An answer that is short because of them is not, for that reason, gutting the request.)

## Verifiable constraints

- `ratio:stop_words` {"percentage": 20.0}: followed (official strict checker)

## Answer

Polynomials may converge pointwise to discontinuous f(x), violating uniformity (continuous functions’ uniform limits are continuous). Example: B_n(x)=x^n tends to 0 on [0,1), 1 at x=1, differing by 1 in sup norm. Thus, uniform convergence fails.
