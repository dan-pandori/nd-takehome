### Five f = 0 depth-3 proofs (arm ei_depth3_f0_s0), per-line surprisal under the f = 0 Stage-1 model (nats, T = 1, start index excluded)

** |- ( ( ~ ( ~ ( S & R ) ) ) > ( S > ( ( ~ ( S & R ) ) > ( S v ( ( ~ S ) & P ) ) ) ) )** — found at round 2, written 7, pruned 7, log p_base(T=0.8) = -30.7, log p_final = -0.0
```
   0.00  N1 | ( ~ ( ~ ( S & R ) ) ) : AS
   0.07  N2 | | S : AS
   9.88  N3 | | | ( ~ ( S & R ) ) : AS
  10.37  N4 | | | ( S v ( ( ~ S ) & P ) ) : ORI1 N2
   2.04  N5 | | ( ( ~ ( S & R ) ) > ( S v ( ( ~ S ) & P ) ) ) : IMPI N3 N4
   0.08  N6 | ( S > ( ( ~ ( S & R ) ) > ( S v ( ( ~ S ) & P ) ) ) ) : IMPI N2 N5
   0.00  N7 ( ( ~ ( ~ ( S & R ) ) ) > ( S > ( ( ~ ( S & R ) ) > ( S v ( ( ~ S ) & P ) ) ) ) ) : IMPI N1 N6
```
** |- ( R > ( P > ( P > ( P v P ) ) ) )** — found at round 3, written 7, pruned 7, log p_base(T=0.8) = -23.1, log p_final = -1.7
```
   0.01  N1 | R : AS
   0.00  N2 | | P : AS
   1.71  N3 | | | P : AS
   8.24  N4 | | | ( P v P ) : ORI1 N3
   6.82  N5 | | ( P > ( P v P ) ) : IMPI N3 N4
   0.27  N6 | ( P > ( P > ( P v P ) ) ) : IMPI N2 N5
   0.02  N7 ( R > ( P > ( P > ( P v P ) ) ) ) : IMPI N1 N6
```
** |- ( ( ~ ( ~ S ) ) > ( P > ( P > ( P v ( R & R ) ) ) ) )** — found at round 3, written 7, pruned 7, log p_base(T=0.8) = -23.5, log p_final = -1.8
```
   0.00  N1 | ( ~ ( ~ S ) ) : AS
   0.00  N2 | | P : AS
   3.11  N3 | | | P : AS
  11.24  N4 | | | ( P v ( R & R ) ) : ORI1 N3
   2.41  N5 | | ( P > ( P v ( R & R ) ) ) : IMPI N3 N4
   0.32  N6 | ( P > ( P > ( P v ( R & R ) ) ) ) : IMPI N2 N5
   0.00  N7 ( ( ~ ( ~ S ) ) > ( P > ( P > ( P v ( R & R ) ) ) ) ) : IMPI N1 N6
```
** |- ( ( ~ ( ~ P ) ) > ( ( ~ ( ~ ( Q v Q ) ) ) > ( ( ~ P ) > ( S v ( ~ ( ~ P ) ) ) ) ) )** — found at round 3, written 7, pruned 7, log p_base(T=0.8) = -26.0, log p_final = -0.0
```
   0.00  N1 | ( ~ ( ~ P ) ) : AS
   0.01  N2 | | ( ~ ( ~ ( Q v Q ) ) ) : AS
   4.24  N3 | | | ( ~ P ) : AS
  12.42  N4 | | | ( S v ( ~ ( ~ P ) ) ) : ORI2 N1
   2.25  N5 | | ( ( ~ P ) > ( S v ( ~ ( ~ P ) ) ) ) : IMPI N3 N4
   0.37  N6 | ( ( ~ ( ~ ( Q v Q ) ) ) > ( ( ~ P ) > ( S v ( ~ ( ~ P ) ) ) ) ) : IMPI N2 N5
   0.00  N7 ( ( ~ ( ~ P ) ) > ( ( ~ ( ~ ( Q v Q ) ) ) > ( ( ~ P ) > ( S v ( ~ ( ~ P ) ) ) ) ) ) : IMPI N1 N6
```
** |- ( ( ~ ( ~ ( P v S ) ) ) > ( ( ~ ( ~ R ) ) > ( ~ ( ~ ( ~ ( ~ ( P v S ) ) ) ) ) ) )** — found at round 3, written 7, pruned 7, log p_base(T=0.8) = -26.9, log p_final = -0.2
```
   0.00  N1 | ( ~ ( ~ ( P v S ) ) ) : AS
   0.00  N2 | | ( ~ ( ~ R ) ) : AS
   2.42  N3 | | | ( ~ ( ~ ( ~ ( P v S ) ) ) ) : AS
  10.32  N4 | | | F : NEGE N1 N3
   6.29  N5 | | ( ~ ( ~ ( ~ ( ~ ( P v S ) ) ) ) ) : NEGI N3 N4
   0.90  N6 | ( ( ~ ( ~ R ) ) > ( ~ ( ~ ( ~ ( ~ ( P v S ) ) ) ) ) ) : IMPI N2 N5
   0.06  N7 ( ( ~ ( ~ ( P v S ) ) ) > ( ( ~ ( ~ R ) ) > ( ~ ( ~ ( ~ ( ~ ( P v S ) ) ) ) ) ) ) : IMPI N1 N6
```

Max-surprisal token over all 610 depth-3 proofs: [('|', 608), ('R', 1), ('(', 1)]; rule at max line: [('AS', 169), ('IMPI', 90), ('ANDI', 88), ('DN', 68), ('ORI1', 66)]
