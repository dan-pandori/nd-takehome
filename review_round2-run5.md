# Review of round2-run5 (target pools that require a pattern)

Reviewer session, independent of the executor. Phase 1 (this section) was written from the run brief
(`BRIEF_ROUND2.md` §Run 5), the pre-registration (log.md as committed in d0d8f16 and fe14f1f, *before* the
first pod job), the code, the data and the raw artefacts only — no executor write-up was read before it was
committed. All counts below come from my own code: `review_run5_recount.py` (own proof parser, own
dependency pruning, own start-index normaliser, own reductio / derived-ORE-strict predicates, own box-depth
counter, own atom-renaming key) and `review_run5_logic.py` (truth-table validity and a G4ip intuitionistic
prover). Only `nd_verify` is shared with the executor. Machine-readable outputs: `artifacts/review_r5/*.json`.

## Recount

### Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash of `nd_verify/` at HEAD = `origin/main` (9437bb7); sha256 of both files identical |
| `artifacts/TEST_RUN_DONE` | byte-identical to `origin/main` (Sep 15 07:38, one test run) |
| evaluation files read in training code | `train.py`: only `--data` / `--heldout`. `expert_iter.py` reads the target, transfer and held-out pools (targets are the RL prompts; transfer and held-out are only sampled for greedy tracking) and `targets/validation_36.jsonl` solely to build an *exclusion* set for `--relabel`, which is off in every run-5 arm. Nothing from an evaluation file enters training except the model's own verified target proofs, which is expert iteration by design. **OK** |
| cap 6 on supervised data | reductio sets: 155,000 proofs each, max 6 lines, 0 violations. Cap-8 sets (`train_derived_ore_strict_f0*_c8.jsonl`): 154,994 proofs each, **44,284 of 7–8 lines** (max 8). This is the brief's "cap-8 setting" carried over from campaign block C; it is not take-home compliant and the derived-ORE results must not be read as submission results. Flagged, not a quarantine (the brief specifies it). |
| hand-written / LLM-written training proofs | none found: all four sets are generator output; a 1 % random sample of each (1,563 proofs) re-verifies with `nd_verify`, 0 failures |

### Split disjointness (my renaming key, atoms relabelled by first appearance)

| training file | vs targets_reductio_req | transfer_reductio_req | targets_derived_ore_req | transfer_derived_ore_req | own held-out | val-36 |
|---|---:|---:|---:|---:|---:|---:|
| train_reductio_f0 | 0 | 0 | 0 | 0 | 0 (heldout) | 0 |
| train_reductio_f0.1 | 0 | 0 | 0 | 0 | 0 (heldout) | 0 |
| train_derived_ore_strict_f0_c8 | 0 | 0 | 0 | 0 | 0 (heldout_c8) | 0 |
| train_derived_ore_strict_f0.01_c8 | 0 | 0 | 0 | 0 | 0 (heldout_c8) | 0 |

Cross-family overlaps exist (reductio sets ∩ `heldout_c8` 118–122 classes; cap-8 sets ∩ `heldout` 101–122) but no arm pairs those files. `heldout` ∩ `heldout_c8` = 5 classes. Targets ∩ transfer = 0 classes in both pools; every key is distinct within each pool; my key equals the stored `key` field for all 815 records.

### Pattern frequency in the Stage-1 sets (my predicates, dependency-pruned)

| set | reductio | derived-ORE strict | derived-ORE loose (over AS or `X v X`) |
|---|---:|---:|---:|
| train_reductio_f0 | **0** | – | – |
| train_reductio_f0.1 | 15,500 (10.00 %) | – | – |
| train_derived_ore_strict_f0_c8 | – | **0** | 743 |
| train_derived_ore_strict_f0.01_c8 | – | 1,550 (1.00 %) | 2,226 |

So f = 0 is exactly zero for the strict predicate in both f = 0 sets.

### Oracle files (`necessity.py` outputs) — recounted, with my predicate on every stored proof

| file | n | reachable ≤ 10 (by min lines) | required | timeouts | required-but-fields-inconsistent | required whose oracle proof lacks the pattern (my pred.) | restricted proof containing the pattern | proof verify failures |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| run5_reductio_nec | 945 | 559 (6/7/8/9/10: 45/90/230/140/54) | 559; **514 at ≥ 7** | 0 | 0 | 0 | 0 (restricted search found 0 of 945) | 0 |
| run5_c8_nec | 1,568 | 1,441 (9/10: 1,127/314) | 120 (55/65) | 0 | 0 | 0 | 0 | 0 |
| run5_c8c_nec | 1,381 | 1,283 (976/307) | 68 (33/35) | 0 | 0 | 0 | 0 | 0 |
| run5_c8d_nec | 5,040 | 4,660 (3,578/1,082) | 196 (77/119) | 0 | 0 | 0 | 0 | 0 |

Reductio required by schema: 45 each of excluded_middle, nand_neg, neg_to_contra, contraposition_conv,
negimp_to_pos, nor_neg_ante, nand_to_imp, negcond_ante, peirce_seq, consequentia_cond, neg_both,
chain_neg; cases_neg 8, negimp_to_or 8, impimp_to_or / imp_cases_or / demorgan_nor_neg 1 each. Derived-ORE:
120 + 68 + 196 = 384 required records = **365 distinct renaming classes** = exactly the 300 + 65 in the two
pools (nothing dropped, nothing stratified). All 384 required derived-ORE records verify and contain the
strict pattern by my predicate.

### Pools

| pool | n | min lines (oracle) | all oracle proofs verify / contain pattern (my pred.) | `( ~ ( ~` in sequent | matched to an oracle record with requires = True, restricted search failed without timeout |
|---|---:|---|---|---:|---:|
| targets_reductio_req | 300 | 7/8/9/10: 52/133/82/33 | 300 / 300 | 0 | 300 |
| transfer_reductio_req | 150 | 27/67/41/15 | 150 / 150 | 0 | 150 |
| targets_derived_ore_req | 300 | 9/10: 126/174 | 300 / 300 | 91 (irrelevant for this pattern) | 300 |
| transfer_derived_ore_req | 65 | 28/37 | 65 / 65 | 18 | 65 |

Reductio pool by schema (targets): contraposition_conv 27; negcond_ante, nand_neg, neg_to_contra, chain_neg,
peirce_seq, neg_both, nand_to_imp, consequentia_cond, excluded_middle, negimp_to_pos 26 each; cases_neg 5,
negimp_to_or 5, impimp_to_or / demorgan_nor_neg / imp_cases_or 1. **The 52 seven-line targets are exactly the
nand_neg (26) and negimp_to_pos (26) instances**; every other schema is 8–10 lines.

**Independent logic check (no minlen).** All 450 reductio theorems are classically valid (truth table over
P, Q, R, S) and **none is provable in G4ip** (Dyckhoff's intuitionistic decision procedure; 16 self-test
cases incl. Peirce, excluded middle, De Morgan, `~~P ⊢ P`). Since `DN` is the only classical rule in
`spec.md`, every natural-deduction proof of every reductio target must use `DN`, and since no sequent contains
`( ~ ( ~`, the eliminated double negation must be built inside the proof. This confirms "requires DN"
unboundedly, stronger than the oracle's bound-10 search. It does not by itself force the *strict* predicate
(a `~~G` could in principle be assembled by `ORE`/`BOTE` before `DN`); that is what the empirical
solved-without-pattern count below is for. Derived-ORE theorems: 365/365 classically valid; 262/300 and
55/65 intuitionistically provable (informational; the ORE-necessity claim is only minlen-relative and is
tested empirically below).

Hand check: I read the oracle proofs of four random targets (`targets_reductio_req_165` negimp_to_pos 7
lines, `_77` peirce_seq 10 lines, `targets_derived_ore_strict_c8req_202` and `_24`, 9 lines); each is the
expected shape (`AS ~G … NEGI … DN`; `IMPE`/`ANDE1` → `ORE`). The machine check above covers all 815.

### Arms (identical EI: k = 32, 8 rounds, T = 0.8, retain 20k; frozen = same init, same seeds, `--no_train`)

Per target: solved = ≥ 1 verified proof in rounds 1–8; acquired = ≥ 1 verified proof whose dependency-pruned
form satisfies the pattern (my predicate); round = first per-round file the (name, normalised proof) appears
in. Every distinct normalised proof re-verified against its prompt with `nd_verify`.

| arm | targets solved /300 | acquired (rate) | solved w/o pattern | by min lines 7/8/9/10 (reductio) or 9/10 (ORE) | cum. acquired by round 1…8 | distinct proofs (pattern) | verified / failures | transfer solved (acq.) | executor round_8 cum. solved |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|
| ei_reductio_f0_s0 | 51 | 51 (0.170) | 0 | 51/0/0/0 | 2 11 25 47 51 51 51 51 | 52 (52) | 52 / 0 | 25/150 (25) | 51 ✓ |
| ei_reductio_f0_s1 | 0 | 0 | 0 | 0/0/0/0 | 0 … 0 | 0 | – | 0 (0) | 0 ✓ |
| ei_reductio_f0_s2 | 0 | 0 | 0 | 0/0/0/0 | 0 … 0 | 0 | – | 0 (0) | 0 ✓ |
| ei_reductio_f0.1_s0 | 53 | 53 (0.177) | 0 | 52/1/0/0 | 14 39 51 53 53 53 53 53 | 53 (53) | 53 / 0 | 27 (27) | 53 ✓ |
| ei_reductio_f0.1_s1 | 52 | 52 (0.173) | 0 | 52/0/0/0 | 17 40 51 52 52 52 52 52 | 52 (52) | 52 / 0 | 27 (27) | 52 ✓ |
| frozen_reductio_f0_s0 | 4 | 4 (0.013) | 0 | 4/0/0/0 | 2 2 2 3 3 3 3 4 | 4 (4) | 4 / 0 | 3 (3) | 4 ✓ |
| frozen_reductio_f0_s1 | 0 | 0 | 0 | | | 0 | – | 0 | 0 ✓ |
| frozen_reductio_f0_s2 | 0 | 0 | 0 | | | 0 | – | 0 | 0 ✓ |
| frozen_reductio_f0.1_s0 | 27 | 27 (0.090) | 0 | 27/0/0/0 | 14 20 22 22 22 22 25 27 | 27 (27) | 27 / 0 | 9 (9) | 27 ✓ |
| frozen_reductio_f0.1_s1 | 21 | 21 (0.070) | 0 | 21/0/0/0 | 17 17 19 21 21 21 21 21 | 21 (21) | 21 / 0 | 11 (11) | 21 ✓ |
| ei_derived_ore_strict_f0_c8_s0 | 26 | 26 (0.087) | 0 | 20/6 | 8 12 16 20 22 24 25 26 | 35 (35) | 35 / 0 | 8/65 (8) | 26 ✓ |
| ei_derived_ore_strict_f0_c8_s1 | 24 | 24 (0.080) | 0 | 16/8 | 7 11 13 14 16 18 21 24 | 34 (34) | 34 / 0 | 8 (8) | 24 ✓ |
| ei_derived_ore_strict_f0.01_c8_s0 | 48 | 48 (0.160) | 0 | 36/12 | 14 26 33 34 37 42 44 48 | 57 (57) | 57 / 0 | 13 (13) | 48 ✓ |
| ei_derived_ore_strict_f0.01_c8_s1 | 63 | 63 (0.210) | 0 | 36/27 | 20 30 37 42 52 57 61 63 | 96 (96) | 96 / 0 | 14 (14) | 63 ✓ |
| frozen_derived_ore_strict_f0_c8_s0 | 13 | 13 (0.043) | 0 | 13/0 | 8 9 10 12 12 13 13 13 | 21 (21) | 21 / 0 | 5 (5) | 13 ✓ |
| frozen_derived_ore_strict_f0_c8_s1 | 11 | 11 (0.037) | 0 | 11/0 | 7 10 10 10 10 11 11 11 | 14 (14) | 14 / 0 | 4 (4) | 11 ✓ |
| frozen_derived_ore_strict_f0.01_c8_s0 | 21 | 21 (0.070) | 0 | 21/0 | 14 15 16 19 20 21 21 21 | 30 (30) | 30 / 0 | 6 (6) | 21 ✓ |
| frozen_derived_ore_strict_f0.01_c8_s1 | 28 | 28 (0.093) | 0 | 23/5 | 20 21 21 22 23 24 26 28 | 46 (46) | 46 / 0 | 8 (8) | 28 ✓ |

Notes on the arm files: every per-round `found_r.jsonl` is a subset of `found_8.jsonl`; the stored `round`
field agrees with the first file of appearance for every proof; round-1 solved counts are identical between
each EI arm and its frozen twin (same init, same sampling seed), as they must be. Pattern evaluated on the
unpruned proof gives the same acquired counts in every arm. Solved-without-pattern is **0 in all 18 arms**
(0 of 4,700+ distinct proofs across pools), i.e. no target of either "required" pool was ever solved by a
pattern-free proof. On "≥ 100 proofs per arm": no reductio arm has 100 distinct proofs (the arms solve ≤ 53
targets with ~1 proof each), so I verified *every* counted proof in every arm and pool — 1,234 target proofs
and all transfer proofs — 0 failures.

**Length wall in the reductio arms.** All three solving EI reductio arms solve 51–52 of the 52 seven-line
targets (the nand_neg / negimp_to_pos instances, whose proofs are the 7-line template `PR PR AS ANDI|IMPE
NEGE NEGI DN`) and **0 of the 248 targets at 8–10 lines** (one exception: f = 0.1 s0 solves one 8-line
chain_neg). Transfer is the same: 25–27 of the 27 seven-line theorems, 0 of 123 longer. Every reductio proof
found has box depth 1. The reductio "acquisition" numbers are therefore the size of the 7-line stratum
(52/300 = 0.173), not a property of the pattern across the pool. The derived-ORE arms do not show this: EI
solves 9- and 10-line targets (f = 0: 6–8 ten-liners; f = 0.01: 12–27), while the frozen f = 0 models solve
only 9-line ones.

### Base reachability (Stage-1 f = 0 models, pass@10⁴, T = 0.8, all 300 targets; coverage files)

| model | targets solved /300 | with a strict-pattern proof | by min lines | ok samples of 3·10⁶ (per-sample rate) | first hit (samples) | distinct proofs verified / failures |
|---|---:|---:|---|---|---|---:|
| reductio f0 s0 | 6 | 6 | 7: 6 | 113 (3.8·10⁻⁵) | 139–4,899 | 6 / 0 |
| reductio f0 s1 | 0 | 0 | – | 0 | – | – |
| reductio f0 s2 | 1 | 1 | 7: 1 | 1 (3.3·10⁻⁷) | 5,047 | 1 / 0 |
| derived-ORE c8 f0 s0 | 27 | 27 | 9: 22, 10: 5 | 17,043 (5.7·10⁻³) | 1–9,707 | 41 / 0 |
| derived-ORE c8 f0 s1 | 27 | 27 | 9: 24, 10: 3 | 16,044 (5.3·10⁻³) | 1–9,577 | 42 / 0 |

Every base-solved target was solved with a strict-pattern proof (0 pattern-free). EI vs base: derived-ORE
f = 0 s0 solves 26, of which 8 are not reachable by the base model at 10⁴ samples (frozen: 13, all within
the base-reachable 27); s1: 24 with 7 new (frozen 11, all within base). Reductio f = 0 s0: EI 51, of which
45 not base-reachable at 10⁴.

### Pre-registered expectations (d0d8f16, 19:05 UTC, before any pod job) against my values

| id | expectation | my value | verdict |
|---|---|---|---|
| R5-E1 | reductio reachable-required ≥ 250 of 945; derived-ORE required 15–25 % of generator candidates; 0 oracle inconsistencies | 514 (≥ 7 lines) of 945; derived-ORE 120/1,568 = 7.7 %, 68/1,381 = 4.9 %, 196/5,040 = 3.9 %; 0 inconsistencies | reductio met; derived-ORE fraction **missed** (≈ 4–8 %, not 15–25 %); consistency met |
| R5-E2 | f = 0: s1, s2 solve 0/300; s0 ignites by round ≤ 4 and reaches 0.15–0.35; f = 0.1: 0.30–0.50 both seeds; frozen ≤ 3 targets each; solved-without-pattern 0 | s1, s2: 0/300 ✓; s0: first proof round 1, 47/300 by round 4, final 0.170 ✓; f = 0.1: 0.177 / 0.173 **below** the 0.30–0.50 range; frozen f = 0 s0 4 (**> 3**), f = 0.1 27 / 21 (**≫ 3**); solved-without-pattern 0 ✓ | half met; the f = 0.1 level and the frozen counts missed, and all three EI arms hit the 7-line wall described above |
| R5-E3 | derived-ORE f = 0 strict acquisition 0.00–0.03 (base pass@10⁴ strict on ≤ 5 % of targets); f = 10⁻²: 0.03–0.10; solve rate ≈ strict acquisition | f = 0: 0.087 / 0.080 (**above**); base pass@10⁴ strict on 27/300 = 9 % (**above** 5 %); f = 10⁻²: 0.160 / 0.210 (**above**); solve rate = acquisition exactly (0 pattern-free) | levels missed upward in every cell; the qualitative "solve = acquire" met |
| R5-E4 | frozen f = 0 vs EI f = 0 differ by < 3 targets for derived-ORE (no ignition); by ≥ 10× for reductio s0 / s7 | derived-ORE: 26 vs 13 and 24 vs 11 (**+13 / +13**, both seeds, EI ≈ 2× frozen); reductio s0: 51 vs 4 (≈ 13×) ✓; s7 never run (deviation logged at 19:20, before the queue) | derived-ORE half **missed**; reductio half met on one seed |

### Reproducibility

`python3 review_run5_recount.py all` and `python3 review_run5_logic.py` in the repository root regenerate
every number above from `artifacts/r5/`, `data/p2/` and `targets/`; outputs in `artifacts/review_r5/`.
Not re-derived: pod spend, kill-switch timing, and the minlen searches themselves (I checked their outputs
for internal consistency and, for reductio, replaced the bounded search by an unbounded logical argument).
