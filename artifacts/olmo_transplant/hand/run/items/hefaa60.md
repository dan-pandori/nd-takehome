# Item hefaa60

## Prompt (sent to the model verbatim)

Prove the product of two primitive polynomials in a UFD R[x] is primitive. Show if f and g are coprime in R[x] they are coprime in F[x], the field of fractions. The response must start with a verb.

## Constraints checked (official checker)

- `words:start_verb` {}: checker says followed

## Answer (the text after the model's private reasoning, which is not shown; 283 words)

Prove that the product of two primitive polynomials in a UFD \( R[x] \) is primitive. Let \( f, g \in R[x] \) be primitive, meaning their coefficient gcd is 1. Assume for contradiction that \( fg \) has a non-unit divisor \( d \in R \) dividing all its coefficients. Suppose \( p \) is a prime dividing \( d \). Since \( f \) is primitive, \( p \) cannot divide all coefficients of \( f \), so let \( a_i \) be a term of \( f \) with \( p \nmid a_i \). Similarly, \( g \) has a term \( b_j \) with \( p \nmid b_j \). The coefficient of \( x^{i+j} \) in \( fg \) includes \( a_i b_j \), which is not divisible by \( p \), contradicting \( p \mid \text{all coefficients of } fg \). Hence, \( d \) must be a unit, so \( fg \) is primitive.  

Next, show that if \( f, g \in R[x] \) are coprime in \( R[x] \), they remain coprime in \( F[x] \), where \( F \) is the field of fractions of \( R \). Since \( f \) and \( g \) are coprime in \( R[x] \), there exist \( a, b \in R[x] \) such that \( af + bg = 1 \). These polynomials \( a \) and \( b \) lie in \( F[x] \), so the same equation holds in \( F[x] \), implying \( \gcd(f, g) = 1 \) in \( F[x] \).  

Thus, primitivity is preserved under multiplication in \( R[x] \), and coprimality is inherited by the polynomial ring over the fraction field.
