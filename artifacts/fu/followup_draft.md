# Follow-up: did depth-3 replicate, what reductio showed, what cap-8 showed

Run 2026-09-16 (branch `dan_novelty`; details in `phase2.md` §Follow-up, `numbers.md`, `log.md`).

**Depth-3 at f = 0 replicates.** Three new f = 0 sets (assembler seeds 1–3, zero depth-3 proofs in written form) and two new f = 0.1 sets, two training seeds each, identical Stage-1 and expert iteration. All eight f = 0 arms acquire depth-3: 0.271–0.364, mean 0.339 ± 0.029; the six f = 0.1 arms give 0.122–0.355 (mean 0.307 ± 0.092, the low arm being a late-igniting f = 0.1 seed that was still climbing at round 8). The two distributions overlap completely; between-set SD is 0.012 against 0.027 between training seeds, so the pretraining draw does not matter. Two corrections to campaign 1: (i) "the base model produces none" is draw-dependent — four of six new f = 0 models put a third `IMPI` box at p ≈ 10⁻²–10⁻³ on a handful of `A > (B > (C > D))` targets (frozen controls find 0–10 such theorems in 256 attempts), while ≥ 94% of every arm's depth-3 proofs remain below 10⁻⁵; (ii) EI's outcome at 8 rounds is unstable on either side of f = 0.

**Reductio, tested properly, is elicitation.** A 606-target pool where the double negation must be derived (21 classical-only schemata without `~~`, plus 6 generator-native theorems; every instance checked classical-only) gives: f = 0 seeds 1 and 2 solve **0 / 606** (never trained); f = 0 seed 0 solves 58, all with the strict `NEGI(~G)…DN` shape, confined to the two 7-line schemata, and its base model already produces exactly that shape at 2·10⁻⁴–4·10⁻³ on 5 of 300 targets (pass@10⁴) — RL amplified a rare generalisation, it did not invent the sequence. f = 0.1 arms reach 10–16% and the same short schemata; Peirce, excluded middle, De Morgan and converse contraposition stay at 0 in every arm.

**Cap-8 strict derived-ORE is not acquired.** With targets that have no ≤ 8-line proof, strict acquisition is 0.008 / 0.008 (f = 0), 0.022 (10⁻³), 0.022 (10⁻²): flat, even at the natural cap-8 rate; the arms solve 40% of the targets by other routes (three-quarters with depth-3 proofs). Frozen controls: 159 / 161 solved, 3 / 2 strict; base pass@10⁴ (f = 0): 118 of 300 solved, strict proofs on 7 — the pattern is reachable, just never selected.

**One line.** RL crosses zero pretraining coverage only for the structural pattern (a deeper box) — reliably, in 8 of 8 arms — and for the rule-sequence patterns it only amplifies what the particular base model already generalised to at ~10⁻³.

![depth-3 strips](figures/followup_depth3_strips.png)
![reductio](figures/followup_reductio.png)
