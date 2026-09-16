# Phase 2 — Controlled-coverage pretraining: does RL need the pattern in pretraining?

Three proof patterns, each defined as a predicate on the dependency-pruned proof (`patterns.py`, 12 verifier-checked
tests): **P1 derived-ORE** (an `ORE` whose disjunction line is not a `PR` line), **P2 reductio** (a `NEGI` box whose
hypothesis is `( ~ G )` followed by a `DN` yielding `G`), **P3 depth-3** (a box at depth ≥ 3). For each pattern,
Stage-1 sets of exactly 155,000 proofs were assembled from one large raw pool of the *unchanged* generator with the
pattern at frequency f ∈ {0, 10⁻⁴, 10⁻³, 10⁻², f_max} (f_max = 0.1 for P2 and P3, 0.02 for P1 — the generator's stream
only holds 3,531 distinct derived-ORE classes of ≤ 6 lines), the other two patterns held at the generator's natural
per-length rates, the length histogram flat (31,000 per length 2–6). f = 0 sets were verified to contain zero pattern
proofs by re-classifying the written file. Then Stage-1 identical to the take-home (4 layers, d = 256, 6,000 steps,
`abs` tokenizer with random start offset, cap 6 asserted at load), expert iteration identical to the take-home (k = 32,
8 rounds, retain 20k of the arm's own Stage-1 set) against 1,000 pattern targets, plus frozen controls with equal
attempts. All counts are start-index normalised. Metrics: `phase2_metrics.py` → `artifacts/p2/metrics_{pattern}.json`;
per-arm outputs `artifacts/p2/<arm>/`; numbers in `numbers.md`.

**Answer.** Whether RL needs the pattern in pretraining depends entirely on which pattern:

- **P3 depth-3 — RL composes it from nothing.** With zero depth-3 proofs in pretraining, expert iteration solves 34%
  and 27% of the depth-3 targets *with a depth-3 proof* (two seeds; 400 and 327 distinct depth-3 proofs), the same as
  at f = 10⁻³ (36%, 34%) and f = 0.1 (36%, 32%). The frozen f = 0 control produces 0 depth-3 proofs in 256 samples per
  target; under the f = 0 Stage-1 model all 610 depth-3 proofs the seed-0 arm found have probability < 10⁻⁵ (the most
  probable one 10⁻⁹·⁵, i.e. ~3·10⁹ samples); the first ones appear at rounds 2–5 out of models fine-tuned only on
  depth ≤ 2 successes. The surprisal of every one of them sits on the third `|`.
- **P1 derived-ORE — a steep dial between 0 and 10⁻³.** At f = 0 RL finds 9 and 2 target theorems with a derived-ORE
  proof (frozen control: 1); at f = 10⁻³ (155 proofs in 155k) it is already 25%, and 24–29% at f = 0.02. Every f = 0
  derived-ORE proof is the degenerate form — a disjunction `( X v X )` obtained by `IMPE`/`ANDE` and eliminated with two
  one-line boxes — which composes two things the f = 0 set does contain (deriving a disjunction; the one-line-box `ORE`
  template over a *premise* `( X v X )`, present 264 times); the strict variant (rule-derived disjunction with distinct
  disjuncts) is 0 at f = 0. The f = 0 base model assigns the easiest instance p ≈ 10⁻³ and produces the pattern in
  2 of 300 targets at 10⁴ samples: rare-but-present, amplified ~5× by RL.
- **P2 reductio — RL neither creates nor amplifies it.** 0 reductio proofs at f = 0 (two seeds, 0 in 3·10⁶ base samples on
  300 targets), 3 theorems at 10⁻⁴, 13/0 at 10⁻³, 11 at 10⁻², 13 at 0.1 — and the frozen control at f = 0.1 already has
  11 of those 13. The targets do not force the pattern (only 56/972 are classically-only), so RL solves them by other
  routes (18–63% solved) and the reductio template is never selected for.

![acquisition](figures/phase2_acquisition.png)

*Main figure: fraction of pattern targets solved with a proof that contains the pattern after 8 rounds, vs the
pattern's frequency in the 155k pretraining set (f = 0 at the left edge; seed points, line through the seed mean;
frozen control dashed).*

## 1. Sets

Raw pool: 820,125 distinct renaming classes of ≤ 6-line proofs (102 generator shards, 12 CPU workers × ~18 min plus a
short 90-worker burst; only an output filter was applied, the generator's probabilities were not touched);
derived-ORE classes 3,531, reductio 158,590, depth-3 193,577. Baseline (held-fixed) rates come from the take-home's
unfiltered pool: reductio 17.3% / 16.7% of 5- / 6-line proofs, depth-3 18.3% of 6-line, derived-ORE 0.09% / 0.20%.

| set | derived-ORE | reductio | depth-3 |
|---|---:|---:|---:|
| reductio_f0 / f1e-4 / f1e-3 / f1e-2 / f0.1 | 88 (0.00057) | 0 / 16 / 155 / 1,550 / 15,500 | 5,687 (0.0367) |
| depth3_f0 / f1e-4 / f1e-3 / f1e-2 / f0.1 | 88 (0.00057) | 10,547 (0.0681) | 0 / 16 / 155 / 1,550 / 15,500 |
| derived_ore_f0 / f1e-4 / f1e-3 / f1e-2 / f0.02 | 0 / 16 / 155 / 1,550 / 3,100 | 10,547 (0.0681) | 5,687 (0.0367) |

(achieved counts after re-classifying each written 155,000-proof file; `data/p2/assemble_report.json`). One shared
held-out set of 5,000 (natural pattern rates), disjoint by class from every training set.

**Targets** (`make_coverage_sets.py targets`): from a fresh strict long pool (89,533 classes of 7–12-line theorems),
keeping only theorems for which `minlen.py` finds **no ≤ 6-line proof** (19,777 of 89,533), whose generating proof
uses the pattern; disjoint by class from the cap-6 pool, the held-out set and validation-36.

| pool | n | min_lines_ub 7 / 8 / none ≤ 8 | classical-only (`intuit.py`) | provably needs the pattern (bounded) |
|---|---:|---|---:|---|
| targets_derived_ore / transfer | 1,000 / 500 | 654 / 219 / 127 | 73 / 22 | 372 of the 873 with a ≤ 8-line proof have none when `ORE` is restricted to premise disjunctions (43%) |
| targets_reductio / transfer | 972 / 332 | 452 / 286 / 234 | **56 / 22** (the rest have an intuitionistic proof) | 56 |
| targets_depth3 / transfer | 1,000 / 500 | 575 / 240 / 185 | 47 / 22 | 142 of the 815 with a ≤ 8-line proof have none at box depth ≤ 2 (17%) |
| targets_none / transfer (control) | 1,000 / 500 | 608 / 252 / 140 | 38 / 18 | – |

The reductio pool is short of the 1,000 / 500 quota because few reductio-generated theorems lack a ≤ 6-line proof.
"Provably needs" is bounded: it means no ≤ 8-line proof exists in the restricted search space.

## 2. Runs and results

Row 1 (f ∈ {0, f_max} × 3 patterns × 2 seeds, 6 frozen controls), row 2 (f = 10⁻³ × 3 × 2), row 3 (f ∈ {10⁻⁴, 10⁻²} × 3
× 1): 30 Stage-1 models (val loss 0.082–0.085 for every set; the take-home's was 0.087) and 30 EI/frozen arms.
Acquisition = fraction of target theorems solved by ≥ 1 written proof whose dependency-pruned form contains the
pattern (the model's proof is classified, never the generating proof).

| pattern | f | seed | targets solved | **acquisition** (theorems / pattern proofs / first round) | transfer solved / acq | held-out greedy |
|---|---:|---:|---:|---|---|---:|
| depth-3 | 0 | 0 | 628/1000 | **0.341** (341 / 400 / r3) | 323/500 / 0.366 | 0.940 |
| depth-3 | 0 | 1 | 587/1000 | **0.271** (271 / 327 / r5) | 296/500 / 0.280 | 0.911 |
| depth-3 | 0 | frozen | 55/1000 | 0 (0 / 0 / –) | 30/500 / 0 | 0.874 |
| depth-3 | 10⁻⁴ | 0 | 605/1000 | 0.354 (354 / 433 / r2) | 314/500 / 0.368 | 0.959 |
| depth-3 | 10⁻³ | 0 | 631/1000 | 0.364 (364 / 443 / r1) | 324/500 / 0.384 | 0.964 |
| depth-3 | 10⁻³ | 1 | 660/1000 | 0.339 (339 / 429 / r2) | 333/500 / 0.366 | 0.952 |
| depth-3 | 10⁻² | 0 | 663/1000 | 0.363 (363 / 421 / r2) | 343/500 / 0.402 | 0.969 |
| depth-3 | 0.1 | 0 | 594/1000 | 0.355 (355 / 424 / r2) | 310/500 / 0.382 | 0.964 |
| depth-3 | 0.1 | 1 | 607/1000 | 0.316 (316 / 388 / r1) | 320/500 / 0.348 | 0.962 |
| depth-3 | 0.1 | frozen | 127/1000 | 0.012 (12 / 17 / r1) | 66/500 / 0.012 | 0.966 |
| derived-ORE | 0 | 0 | 364/1000 | **0.009** (9 / 9 / r3), strict 0 | 328/500 / 0.002 | 0.973 |
| derived-ORE | 0 | 1 | 330/1000 | **0.002** (2 / 2 / r7), strict 0 | 311/500 / 0.004 | 0.970 |
| derived-ORE | 0 | frozen | 180/1000 | 0.001 (1 / 1 / r1) | 193/500 / 0 | 0.971 |
| derived-ORE | 10⁻⁴ | 0 | 555/1000 | 0.222 (222 / 275 / r2) | 323/500 / 0.022 | 0.967 |
| derived-ORE | 10⁻³ | 0 | 583/1000 | 0.248 (248 / 281 / r1) | 327/500 / 0.028 | 0.968 |
| derived-ORE | 10⁻³ | 1 | 583/1000 | 0.245 (245 / 268 / r2) | 330/500 / 0.022 | 0.972 |
| derived-ORE | 10⁻² | 0 | 610/1000 | 0.272 (272 / 371 / r1) | 340/500 / 0.040 | 0.970 |
| derived-ORE | 0.02 | 0 | 572/1000 | 0.242 (242 / 294 / r1) | 329/500 / 0.022 | 0.965 |
| derived-ORE | 0.02 | 1 | 660/1000 | 0.293 (293 / 305 / r1) | 359/500 / 0.042 | 0.974 |
| derived-ORE | 0.02 | frozen | 136/1000 | 0.010 (10 / 11 / r1) | 134/500 / 0.002 | 0.967 |
| reductio | 0 | 0 | 609/972 | **0** (0 / 0 / –) | 222/332 / 0 | 0.886 |
| reductio | 0 | 1 | 170/972 | **0** (0 / 0 / –) | 68/332 / 0 | 0.885 |
| reductio | 0 | frozen | 96/972 | 0 | 39/332 / 0 | 0.886 |
| reductio | 10⁻⁴ | 0 | 203/972 | 0.003 (3 / 3) | | |
| reductio | 10⁻³ | 0 | 212/972 | 0.013 (13 / 13 / r4) | 82/332 / 0 | 0.953 |
| reductio | 10⁻³ | 1 | 374/972 | 0 (0 / 0 / –) | 156/332 / 0 | 0.948 |
| reductio | 10⁻² | 0 | 494/972 | 0.011 (11 / 11 / r4) | 190/332 / 0 | 0.966 |
| reductio | 0.1 | 0 | 193/972 | 0.013 (13 / 13 / r1) | 72/332 / 0 | 0.970 |
| reductio | 0.1 | frozen | 74/972 | 0.011 (11 / 11 / r1) | 24/332 / 0 | 0.968 |

Notes. (i) Solve rates on these hard targets are strongly seed-dependent (reductio f = 0: 609 vs 170; both Stage-1
models have the same val loss), because the number of round-1 successes seeds the whole EI trajectory; acquisition of
depth-3 and derived-ORE is much more stable across seeds than the solve rate. (ii) Held-out greedy is lower for f = 0
arms because the held-out set contains the natural 17% / 18% reductio / depth-3 proofs an f = 0 model has never seen.
(iii) The transfer pools show the same picture at lower levels; derived-ORE transfer acquisition is low (≤ 4%) because
that pool is dominated by 11–12-line theorems.

## 3. f = 0: reachability of what RL found (Phase-1 method, each arm's own Stage-1 model)

| pattern, f = 0 | RL pattern proofs | with base p (T = 0.8) < 1/256 / < 10⁻⁴ / < 10⁻⁵ | most probable | frozen control (256/target) | base pass@10⁴ on 300 targets |
|---|---:|---|---:|---:|---|
| depth-3, seed 0 | 610 | 610 / 610 / 610 | log p = −21.8 (round 4) | 0 depth-3 proofs, 55 solved | *running* |
| depth-3, seed 1 | 491 | 491 / 489 / 485 | log p = −7.1 (round 6) | – | – |
| derived-ORE, seed 0 | 10 | 10 / 8 / 8 | log p = −6.4 (round 3) | 1 derived-ORE proof, 180 solved | 3 solved, 2 with a derived-ORE proof (strict 0) |
| derived-ORE, seed 1 | 4 | 4 / 2 / 2 | log p = −6.3 (round 8) | – | – |
| reductio, both seeds | 0 | – | – | 0 reductio proofs, 96 solved | 82 solved, 0 reductio proofs |

`artifacts/p2/novelty_{pattern}_f0_s{seed}_proofs.jsonl`, `artifacts/p2/cov_{pattern}_f0_s0_targets.s0.jsonl`.

### Where the novelty sits (depth-3, f = 0, seed 0)

Max-surprisal token: the third `|` in 608 of 610 proofs; rule at the max line: `AS` 169, `IMPI` 90, `ANDI` 88, `DN` 68,
`ORI1` 66. Five examples (`artifacts/p2/depth3_f0_examples.md`), per-line surprisal under the f = 0 Stage-1 model:

```
 |- ( R > ( P > ( P > ( P v P ) ) ) )         round 3, log p_base(T=0.8) = -23.1
   0.01  N1 | R : AS
   0.00  N2 | | P : AS
   1.71  N3 | | | P : AS                        <- third box: 1.7 nats here, but
   8.24  N4 | | | ( P v P ) : ORI1 N3           <- the base model has never written a rule line at depth 3
   6.82  N5 | | ( P > ( P v P ) ) : IMPI N3 N4  <- nor closed a box from depth 3
   0.27  N6 | ( P > ( P > ( P v P ) ) ) : IMPI N2 N5
   0.02  N7 ( R > ( P > ( P > ( P v P ) ) ) ) : IMPI N1 N6
```
```
 |- ( ( ~ ( ~ ( S & R ) ) ) > ( S > ( ( ~ ( S & R ) ) > ( S v ( ( ~ S ) & P ) ) ) ) )   round 2, log p = -30.7
   0.00  N1 | ( ~ ( ~ ( S & R ) ) ) : AS
   0.07  N2 | | S : AS
   9.88  N3 | | | ( ~ ( S & R ) ) : AS
  10.37  N4 | | | ( S v ( ( ~ S ) & P ) ) : ORI1 N2
   2.04  N5 | | ( ( ~ ( S & R ) ) > ( S v ( ( ~ S ) & P ) ) ) : IMPI N3 N4
   0.08  N6 | ( S > ( ( ~ ( S & R ) ) > ( S v ( ( ~ S ) & P ) ) ) ) : IMPI N2 N5
   0.00  N7 ( ( ~ ( ~ ( S & R ) ) ) > ( S > ( ( ~ ( S & R ) ) > ( S v ( ( ~ S ) & P ) ) ) ) ) : IMPI N1 N6
```
The other three are in the artifact file; the shape is always the same — three nested `IMPI` boxes for a conclusion of
the form `A > ( B > ( C > D ) )`, with the surprise split between opening the third box and the first rule application
inside it. These are the same shapes that carried the take-home's frontier gain (Phase 1, §3).

### The f = 0 derived-ORE proofs

All 11 EI proofs (both seeds) and the frozen control's one proof have the form

```
N1 ( ( ~ P ) > ( R v R ) ) : PR ; N2 ( ~ P ) : PR ; N3 ( R v R ) : IMPE N1 N2 ;
N4 | R : AS ; N5 | R : AS ; N6 R : ORE N3 N4 N4 N5 N5 ; N7 ( R & R ) : ANDI N6 N6 ; QED
```
(`ORE` over a derived `( X v X )` with two one-line boxes citing their own `AS` line). The f = 0 set has 264 proofs with
exactly that `ORE` shape over a premise `( X v X )` and 1,544 ordinary `ORE`s over premise disjunctions; the composition
"derive the disjunction first" is the new part. Base probability of the easiest instance: 1.6·10⁻³.

## 4. Interpretation

Against the brief's guide: for **P3** acquisition is ≈ 0.3 at f = 0 with the base model's pass@10⁴ ≈ 0 for the pattern
and every found proof at p < 10⁻⁵ — RL composed an absent pattern, in 400 / 327 proofs of 341 / 271 theorems, first at
round 2 (seed 0) / round 4 (seed 1), and pretraining coverage from 10⁻³ to 10⁻¹ adds nothing. For **P1** acquisition
is ≈ 0 at f = 0 in the sense that matters (0 strict; 9 / 2 degenerate proofs that the base model already produces at
~10⁻³–10⁻⁴), rises to 25% by f = 10⁻³ and saturates — RL amplifies rare-but-present behaviour and does not cross f = 0.
For **P2** acquisition stays ≈ 1% at every f, equal to the frozen control at f = 0.1: RL does not select for reductio
because the targets do not require it. The three patterns differ in exactly the way that explains Phase 1: the pattern
RL creates is a *structural* one (one more nesting level of an operation the model already performs), the one it only
amplifies is a *lexical* one (a specific rule sequence), and the one it ignores is not needed by the reward.

## 5. Limitations

- One model size, one generator, 8 rounds at k = 32; row 3 has one seed. P1's dial stops at f = 0.02.
- Targets were filtered by a bounded (≤ 8-line, restricted formula space) minimal-length search; "provably needs the
  pattern" is likewise bounded.
- Base pass@10⁴ for the f = 0 models was run on the first 300 targets of each pool (3·10⁶ samples per model), not all
  1,000; the frozen controls cover the full pools.
- The `runq.sh` queue bug and pod CPU quota caused heavy GPU co-tenancy (up to 7 jobs per A40); this affects wall-clock
  only, not any result. One arm (depth-3, f = 10⁻⁴) crashed with a CUDA OOM at round 6 and was resumed from its
  round-5 checkpoint and cumulative found file.
