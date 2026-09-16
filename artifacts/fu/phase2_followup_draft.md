
---

# Follow-up (2026-09-16): replication of depth-3 at f = 0, a reductio test that can fail, and a cap-8 strict derived-ORE dial

Reason: `review_campaign.md` (n = 2 seeds everywhere; the reductio dial measured nothing). Plans and pre-registered expectations: `log.md` 01:40 / 01:47 / 02:03 UTC. Numbers with sources: `numbers.md` (follow-up sections). All counts start-index normalised; every "RL solved X" comes with the base model's reachability under the arm's own Stage-1 model.

## A. Depth-3 at f = 0 replicates: 8 arms on 4 sets, 6 arms on 3 sets

Three new f = 0 depth-3 sets (assembler seeds 1, 2, 3) and two new f = 0.1 sets (11, 12) were subsampled from a reconstruction of the campaign-1 pool (723,534 classes; the merged 820k pool was never pulled), same 155k / 31k-per-length recipe, campaign-1 held-out reused, every f = 0 set re-classified in written form (0 depth-3; independent counter agrees), reductio 10,547 and derived-ORE 88 in every set. Two training seeds per set; identical Stage-1 and EI (k = 32, 8 rounds, retain 20k); a frozen control (256 attempts per target) for every new model. Acquisition = fraction of the 1,000 depth-3 targets solved by a written proof whose pruned form has a box at depth ≥ 3.

| f | set | seed | arm | solved | **acquisition** (theorems / depth-3 proofs) | first round | transfer acq | held-out greedy | base reachability of the arm's depth-3 proofs: n / below 10⁻⁵ / max log p (T = 0.8) / theorems with p > 1/256 |
|---|---|---|---|---:|---|---|---:|---:|---|
| 0 | a0 | 0 | EI | 628 | **0.341** (341 / 400) | 3 | 0.366 | 0.940 | 400 / 400 / -22.6 / 0 |
| 0 | a0 | 0 | frozen | 55 | **0.000** (0 / 0) | – | 0.000 | 0.874 | – |
| 0 | a0 | 1 | EI | 587 | **0.271** (271 / 327) | 5 | 0.280 | 0.911 | 327 / 324 / -9.9 / 0 |
| 0 | a1 | 0 | EI | 645 | **0.335** (335 / 409) | 2 | 0.372 | 0.907 | 409 / 394 / -3.3 / 3 |
| 0 | a1 | 0 | frozen | 175 | **0.005** (5 / 5) | 1 | 0.004 | 0.883 | – |
| 0 | a1 | 1 | EI | 698 | **0.364** (364 / 426) | 1 | 0.366 | 0.930 | 426 / 413 / -1.8 / 3 |
| 0 | a1 | 1 | frozen | 175 | **0.005** (5 / 5) | 1 | 0.004 | 0.883 | – |
| 0 | a2 | 0 | EI | 589 | **0.350** (350 / 430) | 2 | 0.368 | 0.945 | 430 / 413 / -2.4 / 3 |
| 0 | a2 | 0 | frozen | 166 | **0.004** (4 / 4) | 1 | 0.004 | 0.894 | – |
| 0 | a2 | 1 | EI | 652 | **0.341** (341 / 426) | 4 | 0.358 | 0.903 | 426 / 423 / -7.3 / 0 |
| 0 | a2 | 1 | frozen | 144 | **0.000** (0 / 0) | – | 0.000 | 0.880 | – |
| 0 | a3 | 0 | EI | 605 | **0.361** (361 / 435) | 2 | 0.386 | 0.945 | 435 / 432 / -2.7 / 1 |
| 0 | a3 | 1 | EI | 583 | **0.352** (352 / 425) | 1 | 0.378 | 0.919 | 425 / 406 / -1.3 / 9 |
| 0.1 | b0 | 0 | EI | 594 | **0.355** (355 / 424) | 2 | 0.382 | 0.964 | – |
| 0.1 | b0 | 0 | frozen | 127 | **0.012** (12 / 17) | 1 | 0.012 | 0.966 | – |
| 0.1 | b0 | 1 | EI | 607 | **0.316** (316 / 388) | 1 | 0.348 | 0.962 | – |
| 0.1 | b1 | 0 | EI | 657 | **0.349** (349 / 426) | 1 | 0.388 | 0.964 | 426 / 413 / -1.0 / 3 |
| 0.1 | b2 | 0 | EI | 604 | **0.352** (352 / 410) | 3 | 0.388 | 0.965 | 410 / 408 / -9.5 / 0 |
| 0.1 | b2 | 0 | frozen | 137 | **0.000** (0 / 0) | – | 0.004 | 0.968 | – |
| 0.1 | b2 | 1 | EI | 596 | **0.347** (347 / 428) | 2 | 0.380 | 0.971 | 428 / 357 / -0.9 / 7 |
| 0.1 | b2 | 1 | frozen | 173 | **0.010** (10 / 10) | 1 | 0.014 | 0.967 | – |

![strips](figures/followup_depth3_strips.png)

- **f = 0, 8 arms:** 0.341, 0.271, 0.335, 0.364, 0.350, 0.341, 0.361, 0.352 — mean **0.339 ± 0.029** (SD), min 0.271. **f = 0.1, 6 arms:** 0.355, 0.316 (campaign-1 set), 0.349, **0.122**, 0.352, 0.347 — mean **0.307 ± 0.092** (0.344 ± 0.016 without the late-igniting b1 s1, whose depth-3 count went 1 / 2 / 2 / 2 / 2 / 5 / 27 / 122 over the rounds and was still climbing). The distributions overlap completely (6 of 8 f = 0 arms inside the f = 0.1 range and 5 of 6 f = 0.1 arms inside the f = 0 range; permutation test on the difference of means p ≈ 0.5); **no f = 0 arm is near zero**; the low outlier of the whole family is an f = 0.1 arm.
- **Variance decomposition** (one-way random effects, sets as groups, 2 seeds per set): at f = 0, between-set SD 0.012 vs between-training-seed SD 0.027 (set share 17%, F = 1.4 — indistinguishable from pure seed noise at 4 groups); at f = 0.1 between-set SD 0 (F = 0.9; the b1 s1 outlier is a seed effect, its set-mate is at 0.349). The pretraining draw does not matter; the training seed does — expert iteration on these targets can ignite late.
- **First depth-3 proof:** FIRSTROUNDS.
- **Frozen controls (256 attempts per target):** depth-3 theorems a0 s0 0, a1 s0 5, a1 s1 5, a2 s0 4, a2 s1 0, a3 s0 1, a3 s1 10; f = 0.1: b0 s0 12, b2 s0 0, b2 s1 10, b1 s0 5, b1 s1 2. So the review's "expected 0" is *not* what the new controls show: four of the six new f = 0 models produce a three-nested-`IMPI` proof of the `A > (B > (C > D))` shape on 4–5 of the 1,000 targets within 256 samples.
- **Base reachability** (novelty.py, each arm's own Stage-1 model, T = 0.8, start-index marginalised, every depth-3 proof of the arm): 94–100% of each arm's depth-3 proofs are below 10⁻⁵ (table); but the *most* probable proof per arm ranges from log p −22.6 (campaign-1 model) to −1.3 (a3 s1: p ≈ 0.27, third-box `AS` line costing 0.4 nats), and the number of targets with any depth-3 proof above 1/256 is 0 / 0 / 3 / 3 / 3 / 0 / 1 / 9 across the eight f = 0 arms. The frozen controls find exactly those theorems (a1 s1: all 3 high-p theorems are among its 5 frozen finds).

**Reading.** The headline replicates and sharpens: with zero depth-3 proofs in pretraining, expert iteration reaches the f = 0.1 level in every one of eight arms. What changes is the mechanism's starting point. The campaign-1 model was one where the third box was a < 10⁻⁵ event everywhere (0 in 3·10⁶ base samples) and the first depth-3 proofs appeared at rounds 3 / 5 out of models fine-tuned on depth ≤ 2 successes; four of the six new models already assign 10⁻²–10⁻³ to a third box on a handful of targets and EI starts from those at round 1–2. Both routes end at 0.34. The honest one-line version is therefore: *the base model's willingness to open a third box is a rare, draw-dependent generalisation of the depth-2 nesting it was trained on (0 to 9 reachable targets per 1,000), and RL turns it into 340 targets in every case.* "The frozen control and the base model produce none" (campaign.md) holds for the campaign-1 model and for a2 s1 / b2 s0, not in general; it should read "produce at most a handful".

## B. A reductio test that can fail — and how it fails

**Pool.** The generator cannot supply it: 19,099 reductio-shaped long theorems without a `( ~ ( ~` sub-formula contain **7** classical-only ones (0.04%; a further 72-minute 180M-try run with an in-worker `intuit.py` filter found 85 more, too late to use). So `targets_reductio2` is built from 21 classical-only schemata without double negation (Peirce, excluded middle, Dummett, `~A>B, ~B |- A`, `~(~A&B), B |- A`, `~(A>B) |- A`, De Morgan `~(A&B) |- ~A v ~B`, converse contraposition, `A>B, ~A>B |- B`, …) with random sub-formulas (`reductio_pool.py`; every instance truth-table valid, `intuit.py` non-provable, no `( ~ ( ~` anywhere, class-disjoint from the reconstructed pool = every training set, the held-out set, the old reductio pools and validation-36; minlen bound 8, min_lines_ub ≥ 7 or None): **606 targets** (30 per schema + the 6 usable generator-native theorems; min_lines_ub 7 / 8 / None = 62 / 158 / 386) and **300 transfer**. Ten were printed and hand-checked (`log.md` 02:00): each needs the negated goal assumed. Since the only classical rule is DN and no double negation is given, every proof must apply DN to a derived (or assumed-and-discharged) `( ~ ( ~ G ) )`.

**Predicates on the model's proof:** strict = `patterns.reductio`; loose = `patterns.derived_dn` (a DN citing a rule-derived line); any-DN as an upper bound. Arms on the campaign-1 reductio sets: f = 0 seeds 0, 1 (existing models) and 2 (new Stage-1), f = 0.1 seeds 0, 1; frozen controls for all five; base pass@10⁴ on 300 targets for f = 0 seed 0.

| arm | solved / 606 | strict | loose | any-DN | first round | per round (strict) | transfer solved / strict (300) | schemata solved |
|---|---:|---:|---:|---:|---|---|---|---|
| EI f = 0 s0 | 58 | **58** (0.096) | 58 | 58 | 2 | 0 / 1 / 11 / 24 / 36 / 55 / 58 / 58 | 30 / 30 | nand_neg 29/30, negimp_to_pos 27/30, native 2/6 |
| EI f = 0 s1 | **0** | 0 | 0 | 0 | – | 0 … 0 | 0 / 0 | – |
| EI f = 0 s2 | **0** | 0 | 0 | 0 | – | 0 … 0 | 0 / 0 | – |
| EI f = 0.1 s0 | 95 | 95 (0.157) | 95 | 95 | 1 | 15 / 46 / 61 / 64 / 71 / 77 / 81 / 95 | 40 / 40 | nand_neg 30, negimp_to_pos 30, neg_both 22, chain_neg 11, native 2 |
| EI f = 0.1 s1 | 63 | 63 (0.104) | 63 | 63 | 1 | 17 / 48 / 61 / 62 / 62 / 63 / 63 / 63 | 30 / 30 | nand_neg 30, negimp_to_pos 30, chain_neg 2, native 1 |
| frozen f = 0 s0 | 3 | 3 | 3 | 3 | 2 | | 1 / 1 | nand_neg 3 |
| frozen f = 0 s1 / s2 | 0 / 0 | 0 | 0 | 0 | – | | 0 | – |
| frozen f = 0.1 s0 / s1 | 25 / 29 | 25 / 29 | | | 1 | | 15 / 10 | nand_neg 20 / 18, negimp_to_pos 5 / 11 |

![reductio](figures/followup_reductio.png)

- **Every solved target, in every arm, is solved by the strict reductio shape** (strict = loose = any-DN): there is no other way, which is what the pool was built for.
- **Base reachability.** f = 0 s0: base pass@10⁴ on 300 targets = **5 solved, all 5 by the strict shape** (92 hits in 3·10⁶ samples; per-sample rates 2·10⁻⁴–4·10⁻³; all instances of `~(~A & B), B |- A`; 0 depth-3 / derived-ORE samples); the 60 EI proofs have max log p −5.6 (p ≈ 4·10⁻³, the round-4 proof), median −21, 44 / 60 below 10⁻⁵, max-surprisal line NEGI (42) or DN (13). f = 0.1: 25–26 of the solved theorems have a proof above 1/256 under their base.
- **Reading against the pre-registered expectation** ("f = 0 stays ≈ 0 under both predicates and the solve rate ≈ frozen; if RL composes NEGI + DN, the loose predicate rises first"). Neither branch as written. Two of three f = 0 seeds are exactly the first branch (0 / 606, never trained). The third seed's Stage-1 model — trained on the *same* set — already produces the never-seen `NEGI(~G)…DN` sequence at ~10⁻³ on the easiest 7-line instances (its frozen control finds 3, base pass@10⁴ finds 5 of 300), and EI amplifies that to the two 7-line schemata (56 of 60 instances) and nothing longer; loose and strict rise together because the composed shape *is* the strict shape. So on a pool where reductio is genuinely required, RL does not invent the rule sequence: it amplifies it where the base model's own generalisation put it at 10⁻³, and stays at zero where it did not. The f = 0.1 arms (15,500 reductio proofs in pretraining) reach only 10–16%, confined to the four shortest schemata; Peirce, excluded middle, Dummett, De Morgan and converse contraposition are 0 / 30 in every arm including the f = 0.1 ones.

## C. Cap-8 dial for the non-degenerate derived ORE

**Pool.** Cap-8 raw pool from the unchanged generator's short mode with no per-length caps (`pool_cap8.jsonl`, 2,435,041 classes; strict derived-ORE = disjunction obtained by a rule, disjuncts differ: 2.4% of 7-line and 11.8% of 8-line proofs, ≈ 2% of a flat 2–8 set). Sets (`--simple`, 22,142 per length 2–8, new cap-8 held-out): strict derived-ORE **0 / 155 / 1,550** (f = 0 asserted in pruned and written form), everything else at its natural cap-8 rate conditional on non-strict: degenerate/other derived-ORE 743 / 732 / 676 (0.48%), reductio 5.4%, depth-3 7.1%. Stage-1 with `--cap 8` (val loss 0.08x), two seeds at f = 0, one at 10⁻³ and 10⁻². Targets (`targets_c8`, 500 + 250 transfer): strict-derived-ORE theorems generated at 9–16 lines for which minlen (bound 8) finds **no ≤ 8-line proof** — only 0.5% of the 9–14-line and 1.6% of the 12–16-line generator theorems qualify (the generator's strict ORE is, like its reductio, almost always redundant), 300 of the 500 are also depth-3 shapes. Like campaign 1's pools these are theorems whose *generating* proof uses the pattern, not theorems that provably need it.

| cap 8 arm | solved / 500 | **strict acquisition** (theorems / proofs) | first round | per round (strict theorems) | transfer solved / strict (250) | held-out (cap 8) greedy | strict proofs' base p: n / below 1/256 / below 10⁻⁵ / max log p |
|---|---:|---|---|---|---|---:|---|
| EI f = 0 s0 | 197 | **0.008** (4 / 5) | 1 | 2 2 2 3 3 3 3 4 | 120 / 1 | 0.926 | 5 / 2 / 0 / −1.2 |
| EI f = 0 s1 | 200 | **0.008** (4 / 5) | 1 | 2 3 4 4 4 4 4 4 | 118 / 1 | 0.936 | 5 / 2 / 0 / −2.9 |
| EI f = 10⁻³ s0 | 202 | **0.022** (11 / 17) | 1 | 2 2 4 4 5 7 8 11 | 124 / 1 | 0.929 | 17 / 13 / 5 / −0.6 |
| EI f = 10⁻² s0 | 218 | **0.022** (11 / 14) | 1 | 2 4 6 7 8 9 9 11 | 126 / 2 | 0.933 | 14 / 6 / 1 / −1.9 |
| frozen f = 0 s0 | 159 | 0.006 (3 / 4) | 1 | 2 2 2 2 2 3 3 3 | 94 / 1 | 0.918 | – |
| frozen f = 0 s1 | 161 | 0.004 (2 / 4) | 1 | 2 2 2 2 2 2 2 2 | 97 / 1 | 0.931 | – |
| base pass@10⁴, f = 0 s0, 300 targets | COV_C8 | | | | | | |

**Reading.** The dial is flat: 1–2% strict acquisition at every f from 0 to 10⁻² (the latter being roughly the generator's own cap-8 rate), against my pre-registered 10–35% for f ≥ 10⁻³. The arms solve ~40% of the targets, three-quarters of them with depth-3 proofs, i.e. they route around the disjunction elimination. The few strict proofs that do appear are 9-line `ANDE/IMPE → ORE` with distinct disjuncts and are mostly *reachable* under their own base (max log p −0.6 to −2.9; 0–5 of them below 10⁻⁵) — the cap-8 base models, which have seen ORE over premise disjunctions and (at f = 0) 743 degenerate derived OREs, already assign 10⁻¹–10⁻³ to a strict derived ORE on a couple of targets, and RL neither needs nor selects the pattern beyond that. So the non-degenerate derived ORE behaves like reductio, not like depth-3: no composition across f = 0, and not even amplification when the reward does not require the pattern. This is a cap-8 result and is not pooled with the cap-6 dial.
