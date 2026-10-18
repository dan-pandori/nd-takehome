# Pre-registered expectations vs outcomes

Pre-registration: `preregistration/proof-strategies.md` (commit a30bc33b, 18:52 UTC, before any pod and any strategy count);
pod jobs and the RL-mix analysis pre-registered in `log.md` (2026-10-18) before they ran. Outcomes under the final
taxonomy v1.2 unless marked; sources `TABLES.md`, `artifacts/ps/summary/*.json`, `artifacts/ps/tables.json`,
`artifacts/ps/rl_mix.json`. K12 = 155,000 proofs.

| # | expected | outcome | verdict |
|---|---|---|---|
| consistency | #10 on K12 reproduces σ = 16,703 | 16,703 σ records ⊂ 16,717 (+14 disguised reductios, σ⁺ \ σ) | hit |
| E1 | conditional proof uses 65–90 % | 42.95 % | **miss** (low) |
| E1 | ∨-introduction 30–55 % | 44.26 % | hit |
| E1 | proof by cases 25–50 % | 44.16 % | hit |
| E1 | conjunction introduction 30–55 % | 32.57 % | hit |
| E1 | ex falso 8–20 % | 8.04 % | hit |
| E1 | disjunctive syllogism 3–10 % | 0.03 % (v1.1: 0.24 %) | **miss** (far lower) |
| E1 | proof of a negation 4.4–7 % | 4.74 % | hit |
| E1 | modus tollens / contraposition 2–6 % | 0.05 % | **miss** (far lower) |
| E1 | DNE 2.5–3.5 % | 3.06 % | hit |
| E1 | excluded middle < 0.5 % | 0.03 % | hit |
| E1 | lemma reuse 10–35 % | 11.71 % | hit |
| E1 | box-free proofs 3–12 % | 24.91 % | **miss** (high) |
| E1 | vacuous discharge 15–40 % | 28.20 % | hit |
| E2 | primary: conditional proof 40–65 % | 37.65 % | **miss** (just below) |
| E2 | primary: proof by contradiction 2–6 % | 2.91 % | hit |
| E2 | unlabelled primary < 1 % | 0 | hit |
| E2 | curried primary: proof by contradiction 5–9 % | 3.50 % | **miss** |
| E3 | a strategy only in dead lines in 5–20 % | 0 (K12 has no dead lines) | **miss** |
| E4 | K12⁻: #10 = 0 | 0 | hit |
| E4 | K12⁻: ¬I 4–8 %, DNE 2.5–3.5 % | 5.19 %, 3.29 % | hit |
| E4 | cap-6: #10 3–10 %, nested cases < 2 % | 6.81 %, 0 | hit |
| E5 | textbooks (187): classical-only 15–35 % | 22.5 % | hit |
| E5 | textbooks: #10 15–35 % and ≥ 1.5 × K12 | 20.9 % (1.9 ×) | hit |
| E5 | textbooks: vacuous discharge < 5 % | 10.7 % | **miss** |
| E5 | a strategy ≥ 3 × K12 and ≥ 5 % absolute in textbooks | DS 14.4 % vs 0.03 %, MT 11.8 % vs 0.05 %, ¬I 38.0 % vs 4.74 % | hit |
| E6 | K12 #10 users on classical-only theorems 20–40 % | 25.6 % (4,279 / 16,717) | hit |
| E6 | K12 classical-only theorems proved with #10, 50–90 % | 68.6 % (4,279 / 6,238) | hit |
| E6 | shortest proofs use #10 at < ½ the generator rate | 2.2 % vs 10.0 % (same 990 theorems) | hit |
| E7 | spot-check ≥ 19 / 20 per strategy | 20 / 20 for all 13 (v1.1) | hit |
| E7 | second implementation ≥ 99.5 % per predicate | 100 % (v1.2: every compared label, every record) | hit |
| E7 | term-size formula = lean_check on 100 % | 400 / 400 | hit |
| E7 | canonical examples 100 % Lean-accepted | 30 / 30 | hit |
| J1 | ≥ 90 % of 1,610 schema instances found; 100 % of found proofs Lean-accepted | 1,610 / 1,610; 6,268 / 6,268 over J1–J6 | hit |
| J3 | ≥ 98 % of the K12 sample found | 990 / 990 | hit |
| J3 | shortest proofs: 0 redundant splits, 0 vacuous / pointless reductios, 0 vacuous ¬I; #10 < 5 % | all 0; 2.2 % | hit |
| J4 | DN ban = G4ip on ≥ 99 % | 593 / 594 | hit |
| J4 | requires ∨E for 30–60 % of theorems whose proof uses ∨E | 14.0 % (36 / 258) | **miss** |
| J4 | requires BOTE for < 50 % of theorems whose proof uses ex falso | 0 % (0 / 56) | hit |
| J5 | ≥ 120 / 187 textbook problems decided; requires-DN = G4ip on decided | 124; 123 / 124 | hit (one bound effect) |
| RL | full arm, round 1: ≥ 15 working reductios per seed | 76 / 32 / 52 (distinct proofs first found in round 1) | hit |
| RL | full arm, round 16 ≥ 10 × round 1 | counts: 2,263 / 805 / 686 new in round 16 = 29.8 × / 25.2 × / 13.2 ×; as shares of new proofs (round 16 has ≈ 3 × as many): 8.4 × / 8.9 × / 4.6 × | hit on counts, the quantity pre-registered; miss as shares |
| RL | RL reductios less template-heavy than K12 (99.6 %) | template-only share of RL reductio proofs: round 1 91–95 %, round 16 51–57 % (full) | hit |
| RL | knockout round 1: 0 working reductios on ≥ 5 / 6 seeds | 1 / 0 / 1 / 0 / 2 / 1: zero on 2 / 6 | **miss** |
| RL | knockout round 16: ≤ 50 per seed | 38 / 32 / 84 / 27 / 6 / 49 new in round 16 | **miss** (1 / 6 over) |

Most of the K12 misses share one cause: the pre-registration assumed K12 resembled textbook proofs more than it does. Its
generator rarely writes the named derived rules (disjunctive syllogism, modus tollens). A quarter of its proofs open no
box, and none has dead lines. Its theorems need case analysis far less often than its proofs perform it.
Note on the RL rows: the pre-registration stated them on the fine-tune mixes, which turned out to hold ≤ 4 proofs per
problem sampled from the accumulated pool (claim check #30); they are evaluated here on distinct proofs by the round they
were first found (`artifacts/ps/rl_found.json`). On the mix counts the second row had missed on 2 / 3 seeds. The RL misses
are about rare events (one or two working reductios in a round), guessed without a base rate.
