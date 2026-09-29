
## depth3: five pattern proofs found by EI (normalised), with round

- seed 0, round 3, ` |- ( ( ~ ( ~ Q ) ) > ( ( ( R v R ) & S ) > ( ( R & ( Q v S ) ) > ( ( ( R v R ) & S ) v ( P > S ) ) ) ) )` (7 lines):

```
N1 | ( ~ ( ~ Q ) ) : AS ; N2 | | ( ( R v R ) & S ) : AS ; N3 | | | ( R & ( Q v S ) ) : AS ; N4 | | | ( ( ( R v R ) & S ) v ( P > S ) ) : ORI1 N2 ; N5 | | ( ( R & ( Q v S ) ) > ( ( ( R v R ) & S ) v ( P > S ) ) ) : IMPI N3 N4 ; N6 | ( ( ( R v R ) & S ) > ( ( R & ( Q v S ) ) > ( ( ( R v R ) & S ) v ( P > S ) ) ) ) : IMPI N2 N5 ; N7 ( ( ~ ( ~ Q ) ) > ( ( ( R v R ) & S ) > ( ( R & ( Q v S ) ) > ( ( ( R v R ) & S ) v ( P > S ) ) ) ) ) : IMPI N1 N6 ; QED
```

- seed 0, round 4, ` |- ( ( ~ ( ~ ( S > R ) ) ) > ( Q > ( ( ~ ( ~ R ) ) > R ) ) )` (7 lines):

```
N1 | ( ~ ( ~ ( S > R ) ) ) : AS ; N2 | | Q : AS ; N3 | | | ( ~ ( ~ R ) ) : AS ; N4 | | | R : DN N3 ; N5 | | ( ( ~ ( ~ R ) ) > R ) : IMPI N3 N4 ; N6 | ( Q > ( ( ~ ( ~ R ) ) > R ) ) : IMPI N2 N5 ; N7 ( ( ~ ( ~ ( S > R ) ) ) > ( Q > ( ( ~ ( ~ R ) ) > R ) ) ) : IMPI N1 N6 ; QED
```

- seed 0, round 4, ` |- ( ( ~ ( ~ P ) ) > ( ( ~ ( ~ ( P v S ) ) ) > ( ( ~ P ) > P ) ) )` (7 lines):

```
N1 | ( ~ ( ~ P ) ) : AS ; N2 | | ( ~ ( ~ ( P v S ) ) ) : AS ; N3 | | | ( ~ P ) : AS ; N4 | | | P : DN N1 ; N5 | | ( ( ~ P ) > P ) : IMPI N3 N4 ; N6 | ( ( ~ ( ~ ( P v S ) ) ) > ( ( ~ P ) > P ) ) : IMPI N2 N5 ; N7 ( ( ~ ( ~ P ) ) > ( ( ~ ( ~ ( P v S ) ) ) > ( ( ~ P ) > P ) ) ) : IMPI N1 N6 ; QED
```

- seed 0, round 3, ` |- ( ( P > S ) > ( ( ~ ( ~ ( R & P ) ) ) > ( R > ( R & P ) ) ) )` (7 lines):

```
N1 | ( P > S ) : AS ; N2 | | ( ~ ( ~ ( R & P ) ) ) : AS ; N3 | | | R : AS ; N4 | | | ( R & P ) : DN N2 ; N5 | | ( R > ( R & P ) ) : IMPI N3 N4 ; N6 | ( ( ~ ( ~ ( R & P ) ) ) > ( R > ( R & P ) ) ) : IMPI N2 N5 ; N7 ( ( P > S ) > ( ( ~ ( ~ ( R & P ) ) ) > ( R > ( R & P ) ) ) ) : IMPI N1 N6 ; QED
```

- seed 0, round 4, ` |- ( ( S v ( R > P ) ) > ( ( ~ ( ~ R ) ) > ( ( ~ ( ~ ( P & Q ) ) ) > ( P v ( ~ ( ~ R ) ) ) ) ) )` (7 lines):

```
N1 | ( S v ( R > P ) ) : AS ; N2 | | ( ~ ( ~ R ) ) : AS ; N3 | | | ( ~ ( ~ ( P & Q ) ) ) : AS ; N4 | | | ( P v ( ~ ( ~ R ) ) ) : ORI2 N2 ; N5 | | ( ( ~ ( ~ ( P & Q ) ) ) > ( P v ( ~ ( ~ R ) ) ) ) : IMPI N3 N4 ; N6 | ( ( ~ ( ~ R ) ) > ( ( ~ ( ~ ( P & Q ) ) ) > ( P v ( ~ ( ~ R ) ) ) ) ) : IMPI N2 N5 ; N7 ( ( S v ( R > P ) ) > ( ( ~ ( ~ R ) ) > ( ( ~ ( ~ ( P & Q ) ) ) > ( P v ( ~ ( ~ R ) ) ) ) ) ) : IMPI N1 N6 ; QED
```


## depth3: pre-RL pattern samples (top targets by hit count, per model)

- depth3_f0_a1_s0: ` |- ( ( ( R & S ) & ( ~ P ) ) > ( ( R & S ) > ( ( S & ( P v P ) ) > ( Q v ( S & ( P v P ) ) ) ) ) )` hits 72/2000 (first at sample 43)
- depth3_f0_a1_s0: ` |- ( ( S & P ) > ( R > ( ( ( ~ ( ~ Q ) ) > ( ~ ( ~ Q ) ) ) & ( ( ~ ( ~ Q ) ) > ( ~ ( ~ Q ) ) ) ) ) )` hits 40/2000 (first at sample 6)
- depth3_f0_a1_s1: ` |- ( ( ~ ( ~ Q ) ) > ( Q > ( ( ~ Q ) > ( ( P > S ) v ( ~ ( ~ Q ) ) ) ) ) )` hits 303/2000 (first at sample 4)
- depth3_f0_a1_s1: ` |- ( Q > ( ( S > S ) > ( ( ( S & S ) v ( R v R ) ) > ( Q v ( Q & ( ~ S ) ) ) ) ) )` hits 31/2000 (first at sample 54)
- depth3_f0_a1_s4: ` |- ( P > ( ( Q & R ) > ( ( ~ ( ~ ( ~ Q ) ) ) > Q ) ) )` hits 1/2000 (first at sample 1888)
- depth3_f0_a1_s6: ` |- ( ( S & P ) > ( R > ( ( ( ~ ( ~ Q ) ) > ( ~ ( ~ Q ) ) ) & ( ( ~ ( ~ Q ) ) > ( ~ ( ~ Q ) ) ) ) ) )` hits 3/2000 (first at sample 186)
- depth3_f0_a1_s9: ` |- ( Q > ( ( S > S ) > ( ( ( S & S ) v ( R v R ) ) > ( Q v ( Q & ( ~ S ) ) ) ) ) )` hits 356/2000 (first at sample 5)
- depth3_f0_a1_s9: ` |- ( ( ~ Q ) > ( ( ~ S ) > ( S > ( S v ( ~ R ) ) ) ) )` hits 190/2000 (first at sample 10)
- depth3_f0_a2_s0: ` |- ( ( ( R & S ) & ( ~ P ) ) > ( ( R & S ) > ( ( S & ( P v P ) ) > ( Q v ( S & ( P v P ) ) ) ) ) )` hits 171/2000 (first at sample 29)
- depth3_f0_a2_s0: ` |- ( R > ( Q > ( ( ~ ( ~ ( ~ Q ) ) ) > ( Q v ( ~ ( ~ ( ~ Q ) ) ) ) ) ) )` hits 101/2000 (first at sample 3)
- depth3_f0_a2_s1: ` |- ( Q > ( P > ( ( ( P > Q ) & R ) > ( Q & P ) ) ) )` hits 2/2000 (first at sample 239)
- depth3_f0_a2_s1: ` |- ( ( ~ ( ~ ( ~ S ) ) ) > ( S > ( ( ( P v R ) v ( ~ Q ) ) > ( ( ~ ( ~ ( ~ S ) ) ) & ( ~ ( ~ ( ~ S ) ) ) ) ) ) )` hits 1/2000 (first at sample 1427)
- depth3_f0_s1: ` |- ( ( ~ ( ~ ( ~ R ) ) ) > ( R > ( Q v ( ( ( Q v Q ) > R ) > ( ( Q v Q ) > R ) ) ) ) )` hits 1/2000 (first at sample 360)

## reductio: five pattern proofs found by EI (normalised), with round

- seed 0, round 5, `( ~ ( ( ~ ( ( P > S ) & ( R > S ) ) ) & Q ) ) , Q |- ( ( P > S ) & ( R > S ) )` (7 lines):

```
N1 ( ~ ( ( ~ ( ( P > S ) & ( R > S ) ) ) & Q ) ) : PR ; N2 Q : PR ; N3 | ( ~ ( ( P > S ) & ( R > S ) ) ) : AS ; N4 | ( ( ~ ( ( P > S ) & ( R > S ) ) ) & Q ) : ANDI N3 N2 ; N5 | F : NEGE N4 N1 ; N6 ( ~ ( ~ ( ( P > S ) & ( R > S ) ) ) ) : NEGI N3 N5 ; N7 ( ( P > S ) & ( R > S ) ) : DN N6 ; QED
```

- seed 0, round 7, `( ~ ( ( ~ Q ) & ( ( ~ Q ) & ( ~ Q ) ) ) ) , ( Q v ( R > R ) ) |- Q` (8 lines):

```
N1 ( ~ ( ( ~ Q ) & ( ( ~ Q ) & ( ~ Q ) ) ) ) : PR ; N2 ( Q v ( R > R ) ) : PR ; N3 | ( ~ Q ) : AS ; N4 | ( ( ~ Q ) & ( ~ Q ) ) : ANDI N3 N3 ; N5 | ( ( ~ Q ) & ( ( ~ Q ) & ( ~ Q ) ) ) : ANDI N3 N4 ; N6 | F : NEGE N5 N1 ; N7 ( ~ ( ~ Q ) ) : NEGI N3 N6 ; N8 Q : DN N7 ; QED
```

- seed 0, round 8, `( ~ ( ( ~ Q ) & ( ( ~ Q ) & ( ~ Q ) ) ) ) , ( Q v ( R > R ) ) |- Q` (9 lines):

```
N1 ( ~ ( ( ~ Q ) & ( ( ~ Q ) & ( ~ Q ) ) ) ) : PR ; N2 ( Q v ( R > R ) ) : PR ; N3 | ( ~ Q ) : AS ; N4 | ( ( ~ Q ) & ( ~ Q ) ) : ANDI N3 N3 ; N5 | ( ( ~ Q ) & ( ( ~ Q ) & ( ~ Q ) ) ) : ANDI N3 N4 ; N6 | F : NEGE N5 N1 ; N7 ( ~ ( ~ Q ) ) : NEGI N3 N6 ; N8 Q : DN N7 ; N9 Q : DN N7 ; QED
```

- seed 0, round 6, `( ( ~ ( P v S ) ) > ( S & R ) ) , ( ~ ( S & R ) ) |- ( P v S )` (7 lines):

```
N1 ( ( ~ ( P v S ) ) > ( S & R ) ) : PR ; N2 ( ~ ( S & R ) ) : PR ; N3 | ( ~ ( P v S ) ) : AS ; N4 | ( S & R ) : IMPE N1 N3 ; N5 | F : NEGE N4 N2 ; N6 ( ~ ( ~ ( P v S ) ) ) : NEGI N3 N5 ; N7 ( P v S ) : DN N6 ; QED
```

- seed 0, round 5, `( ( ~ P ) > ( ( P > S ) & ( ~ R ) ) ) , ( ~ ( ( P > S ) & ( ~ R ) ) ) |- P` (7 lines):

```
N1 ( ( ~ P ) > ( ( P > S ) & ( ~ R ) ) ) : PR ; N2 ( ~ ( ( P > S ) & ( ~ R ) ) ) : PR ; N3 | ( ~ P ) : AS ; N4 | ( ( P > S ) & ( ~ R ) ) : IMPE N1 N3 ; N5 | F : NEGE N4 N2 ; N6 ( ~ ( ~ P ) ) : NEGI N3 N5 ; N7 P : DN N6 ; QED
```


## reductio: pre-RL pattern samples (top targets by hit count, per model)

- reductio_f0_s0: `( ~ ( ( ~ ( Q & R ) ) & ( Q > P ) ) ) , ( Q > P ) |- ( Q & R )` hits 38/10000 (first at sample 348)
- reductio_f0_s0: `( ~ ( ( ~ ( Q & R ) ) & ( R > P ) ) ) , ( R > P ) |- ( Q & R )` hits 36/10000 (first at sample 524)
- reductio_f0_s3: `( ~ ( ( ~ ( Q v S ) ) & ( ~ Q ) ) ) , ( ~ Q ) |- ( Q v S )` hits 5/2000 (first at sample 25)
- reductio_f0_s3: `( ~ ( ( ~ ( Q & R ) ) & ( Q > P ) ) ) , ( Q > P ) |- ( Q & R )` hits 5/2000 (first at sample 128)
- reductio_f0_s7: `( ~ ( ( ~ ( Q v S ) ) & ( ~ Q ) ) ) , ( ~ Q ) |- ( Q v S )` hits 48/2000 (first at sample 45)
- reductio_f0_s7: `( ~ ( ( ~ ( S v R ) ) & ( ~ R ) ) ) , ( ~ R ) |- ( S v R )` hits 36/2000 (first at sample 22)
- reductio_f0_s9: `( ~ ( ( ~ ( Q & S ) ) & S ) ) , S |- ( Q & S )` hits 5/2000 (first at sample 7)
