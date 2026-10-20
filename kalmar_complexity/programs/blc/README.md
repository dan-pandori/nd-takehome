# Kalmár's construction in binary lambda calculus

`python3 test_blc.py --n 1000 --seed 20261020` (any seed) builds `*.lam` → `*.blc`, tests, writes `results.json`.

## Conventions
- Program = closed λ-term P; output = normal form of P applied to the encoded input; **bits = |BLC(P)|** (λ `00`, application `01`, variable i `1^i0`).
- `.lam`: `param x` is a λ-binder, `name = e` is `(λname. …) e`. `blc.py`'s deterministic optimiser inlines, moves, shares λ-free subterms and makes safe β/η steps where shorter; the optimised term is the one tested.
- Evaluation: call-by-need machine, read out by applying results to fresh variables; **β-steps** include read-out.
- CL: Tromp's bracket abstraction of the same term (S `00`, K `01`, application `1`), checked by graph reduction on 3–5 inputs.

## Encodings (the interface, not counted)
- Booleans λxy.x/λxy.y, pairs λs.s a b, Scott lists.
- **Formulas**: Scott, `Atom k | F | Not | And | Or | Imp`, k a Scott numeral (P=0…S=3). **Sequent**: (premise list, goal).
- **Token strings**: Church lists `λe s1…sK. t1 (… (tm e))`; number tokens are a letter applied to a Church numeral (`N 17`).
  - ND alphabet: `tokenizer.py` SYMS, `N`, RULES.
  - Lean alphabet: tt_prover's tokens in source order; `hN`/`hA` take an index (`h2`, `hQ`). Spacing rule in `tt_codec.py`.
- **K-sl structured proof**: `λL e PR…DN. L n d f r c (… e)`, one L per line: number n, depth d (Church), formula f, rule r (a bound variable), cited lines c (Church list). The renderer supplies the line printer, so rule variables become the output's rule letters.
- **K-tt tree**: Church-encoded, 15 constructors (`Spl`, `Efq`, tt_prover's 13 `prove` cases with formula and truth value).

## Results (1,000 theorems, seed 20261020, all outputs token-exact)

| program | BLC | CL | pass | β mean, median, max |
|---|---:|---:|---:|---|
| K-sl algorithm | 5,443 | 23,921 | 1000 | 57,017, 39,136, 401,263 |
| K-sl rendering (ND) | 616 | 3,776 | 1000 | 7,764, 6,281, 38,248 |
| parse | 800 | 2,900 | 1000 | 436, 413, 947 |
| **K-sl sum (+parse)** | **6,059 (6,859)** | 27,697 (30,597) | | |
| K-tt algorithm | 1,636 | 7,442 | 1000 | 7,948, 6,042, 47,210 |
| K-tt rendering (Lean) | 4,204 | 24,245 | 1000 | 5,458, 4,270, 41,718 |
| **K-tt sum (+parse)** | **5,840 (6,640)** | 31,687 (34,587) | | |

Calibration, BLC/CL bits (200 random cases each, all pass): copy 4/8, reverse 87/197, parity 82/185, addition 375/1,163, sort 257/749, eval 273/713, taut 410/1,430 (half the cases valid K12 sequents; agrees with `countermodel`).

Also passing: 110 edge cases (atom-free sequents, `~~(X v ~X)` premises, duplicate premises) and seed 7 (300/300). Full test: 300 s.

## Golfed
State-monad CPS instead of hand-threaded state (K-sl 8,512 → 6,142, first version passing the test); then shared helpers, Scott atom indices, one `hA` letter, optimiser passes for sharing and β (K-sl → 5,443, Lean renderer 5,590 → 4,204).

## Slack / caveats
- Encodings are free and shape the counts: Lean letter order is fixed (frequency-sorted: 4,007, reversed: 4,683); Scott atom indices were chosen for brevity.
- K-sl spends about 550 bits on references to the 15 rule variables and about 470 on formula equality (a 6×6 case table).
- Unlike the Python split, the algorithm assigns line numbers and depths (references need them); the renderer only formats.
- CL is not tuned: CL/BLC ≈ 4 for the large programs.
- β-steps are call-by-need (with sharing); normal order would take far more.
- `ksl_mirror.py`, `quick.py`: development aids; `runs/`: earlier results.
