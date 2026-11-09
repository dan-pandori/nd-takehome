# Item g4ead05

## Prompt (as the model received it)

Let f / [0, 5] -> \mathbb{R} be defined by  f(x):= 1 if * 0 <= x <= 1; 3 if * 1 < x <= 2; 2 if * 2 < x < 3; 4 if * 3 <= x <= 5  Show that f is Riemann Integrable and integrate f = 14 df from 0 to 5 . Your response must include bullet points denoted by * and at least one sub-bullet point denoted by - for each bullet point.

## Verifiable constraints

- `format:sub-bullets` {}: followed (official strict checker)

## Answer

* The function f is bounded on [0, 5].
  - All values of f are in the set {1, 2, 3, 4}, so it has an upper bound of 4 and a lower bound of 1, satisfying a necessary condition for Riemann integrability.
* The set of discontinuities of f has measure zero.
  - f is discontinuous only at x = 1, x = 2, and x = 3, which are isolated points. Since single points have Lebesgue measure zero, f is Riemann integrable on [0, 5].
* The integral of f from 0 to 5 is computed by summing areas of rectangles over intervals where f is constant.
  - On [0, 1]: height = 1, width = 1 ⇒ area = 1 × 1 = 1.
  - On (1, 2]: height = 3, width = 1 ⇒ area = 3 × 1 = 3.
  - On (2, 3): height = 2, width = 1 ⇒ area = 2 × 1 = 2.
  - On [3, 5]: height = 4, width = 2 ⇒ area = 4 × 2 = 8.
  - Total integral = 1 + 3 + 2 + 8 = 14.
