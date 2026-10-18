# proof-strategies — the proof strategies in our pretraining data (UNREVIEWED)

Thirteen named strategies, each a checkable predicate (`proof_strategies/TAXONOMY.md`). Lean checked every searched
or shown proof. Blind spot-check: 260 / 260. Independent second implementation: agrees on every record.

**K12** (155,000 proofs): →I 43 %, cases 44 % (38 % redundant splits), ∨I 44 %, proof by contradiction 10.8 %. The
knockout's σ is exactly the reductios via ¬I; σ⁺ adds DNE on a derived ¬¬. Only 59 of the 16,717 reductios do working
reasoning, all on theorems that do not need one; no K12 theorem is σ-covered.

**Textbooks** (187 problems) use what K12 lacks: working reductio 21 %, ¬I 38 %, modus tollens 12 %, disjunctive
syllogism 14 %.

**RL** (create-or-elicit's ladders): full models wrote 32–76 working reductios before RL and
6,951–26,450 in rounds 2–16; knockout models 0–2, then 72–772, proving ≤ 5 σ-covered problems.

**Expected vs outcome** (all 45: `proof_strategies/EXPECTATIONS.md`).
- Hits: σ reproduced; most K12 ranges; textbook gaps; validation; no idle steps in shortest proofs; RL growth.
- Misses: →I 43 % (expected 65–90 %); DS, MT ≤ 0.05 % (2–10 %); box-free 25 %; no dead lines; requires-∨E 14 %;
  knockout round-1 zeros 2 / 6.

![mix](proof_strategies/figures/k12_mix.png) ![textbooks](proof_strategies/figures/k12_vs_textbooks.png)
