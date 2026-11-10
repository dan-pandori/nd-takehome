# Item heaa918

## Prompt (the request)

Prove the product of two primitive polynomials in a UFD R[x] is primitive. Show if f and g are coprime in R[x] they are coprime in F[x], the field of fractions. The response must start with a verb.

## Constraints checked (official checker)

- `words:start_verb` {}: checker says followed

## Answer (the text after the model's private reasoning, which is not shown; 97 words)

Let f and g be primitive polynomials in R[x]. Suppose their product fg is not primitive, implying a nonunit d ∈ R divides all coefficients of fg. Factor d into primes p₁,…,pₙ. Pick any p|d. In the domain R/pR, neither f̄ nor ḡ (mod p) is zero (since f and g are primitive), but f̄ḡ ≡ 0, a contradiction. Thus fg is primitive. If f and g are coprime in R[x], then ∃a,b ∈ R[x] with af + bg = 1. This relation persists in F[x], so their gcd in F[x] divides 1, making them coprime there.
