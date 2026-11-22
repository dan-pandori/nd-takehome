# Item c1e2a5c

## Prompt (as the model received it)

Let f / [0, 5] -> \mathbb{R} be defined by  f(x):= 1 if * 0 <= x <= 1; 3 if * 1 < x <= 2; 2 if * 2 < x < 3; 4 if * 3 <= x <= 5  Show that f is Riemann Integrable and integrate f = 14 df from 0 to 5 . Your response must include bullet points denoted by * and at least one sub-bullet point denoted by - for each bullet point.

## Verifiable constraints

- `format:sub-bullets` {}: followed (official strict checker)

## Answer

* The function \( f \) is Riemann integrable on \([0, 5]\) because:  
  - It is bounded, as it takes values only in \(\{1, 2, 3, 4\}\).  
  - The set of discontinuities at \( x = 1, 2, 3 \) is finite, hence has measure zero.  

* The integral of \( f \) from 0 to 5 is 14 because:  
  - The integral is computed as the sum of areas of rectangles over each subinterval:  
    - \([0,1]\): \(1 \times (1 - 0) = 1\)  
    - \([1,2]\): \(3 \times (2 - 1) = 3\)  
    - \([2,3]\): \(2 \times (3 - 2) = 2\)  
    - \([3,5]\): \(4 \times (5 - 3) = 8\)  
  - Adding these areas gives \(1 + 3 + 2 + 8 = 14\).
