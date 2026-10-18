# proof-strategies — the proof strategies in our pretraining data (UNREVIEWED)

Thirteen named strategies, each a checkable predicate over pruned ND proofs (`proof_strategies/TAXONOMY.md`). Lean
checked every searched or shown proof. Blind spot-check: 260 / 260. Independent second implementation: agrees on every
record.

**K12** (155,000 proofs): →I 43 %, cases 44 % (38 % redundant splits), ∨I 44 %, proof by contradiction 10.8 %. That last
is σ: it contains σ exactly, and σ⁺ = it ∪ DNE on a derived ¬¬. Only 59 of those 16,717 reductios do working
reasoning, and no K12 theorem is σ-covered.

**Textbooks** need what K12 lacks: working reductio 21 %, ¬I 38 %, modus tollens 12 %, disjunctive syllogism 14 %
(`TABLES.md`).

**RL** (create-or-elicit's ladders): full models wrote 29–67 working reductios before RL, 199–690 after; knockout
models 0–1, then 0–22.

**Expected vs outcome** (all 45: `proof_strategies/EXPECTATIONS.md`).
- Hits: σ reproduced; ∨I, cases, ∧I, ¬I, DNE, LEM, lemma-reuse ranges; textbook gaps; validation bars; zero idle steps
  in shortest proofs.
- Misses: →I (43 % vs 65–90 %); DS and MT (≤ 0.05 % vs 2–10 %); box-free 25 %; no dead lines; requires-∨E 14 %;
  knockout round-1 zeros 3 / 6.

![mix](proof_strategies/figures/k12_mix.png) ![textbooks](proof_strategies/figures/k12_vs_textbooks.png)
