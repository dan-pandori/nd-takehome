# Item h0aaa27

## Prompt (as the model received it)

The response must start with a verb. Galois theory explained in depth using symbols and equations

## Verifiable constraints

- `words:start_verb` {}: followed (official strict checker)

## Answer

Define a finite Galois extension L/K with Galois group G = Gal(L/K) = {σ ∈ Aut(L) | σ(a) = a for all a ∈ K}, satisfying |G| = [L:K]. For any subgroup H ≤ G, the fixed field is L^H = {x ∈ L | σ(x) = x ∀σ ∈ H}, and [L : L^H] = |H|. Conversely, for an intermediate field F/K, let H_F = Gal(L/F), so L^{H_F} = F and [F : K] = [L : K]/|H_F|. This establishes a bijection between subgroups of G and intermediate fields between K and L, with correspondence H ↔ L^H and F ↔ H_F, such that [L:F] = |Gal(L/F)| and degrees multiply accordingly.
