# Card: novelty relative to the pretraining data (including "longer than the data")

Family N. Slug `out-of-data-novelty`. Notation: `_FRAME.md`.

## 1. Definition, formally

Here a capability is new if it is new **relative to the data**, not to the base model. The data-generating process
(the generator and its cap) defines what an "expert in the pretraining data" can do. Dmitry (20-09): generators let us
"explicitly define the boundary between this does what an expert in the pre-training data would do versus this learns
a new thing that you would need a new expert to prove".

Four levels, coarse to fine:
- **(L) Length:** the shortest Lean-valid proof of t is longer than the pretraining cap (cap 6 or 12 lines). Dan
  (20-09): "capability emergence equals … successfully generating true length longer proofs than we're in the data
  set?" Since L_true is an ND-derived upper bound, the cleaner test is RL's own shortest proof (lines and term size)
  against the cap.
- **(T) Theorem type:** t's renaming class, or its schema (e.g. premise-free A ∨ ¬A), occurs in no pretraining record.
- **(S) Proof skeleton:** RL's proof's rule-and-box structure (the sequence of ND rules with nesting, formulas
  abstracted) occurs in no pretraining proof. "Novelty of a proof relative to prior proofs seen" (reading group
  2026-09-17).
- **(M) Move:** some rule or move type RL uses never occurs in pretraining data.

**Compound divergence** (Keysers et al.) gives a graded version: the divergence between the distribution of rule
n-grams in RL's proofs and in the pretraining proofs.

## 2. Decision rule

| verdict | rule |
|---|---|
| **created (relative to data)** | RL solves t, held out, at k_eval, and t's proof is out of data at the chosen level (L, T or S) |
| **elicited** | t's level-L / T / S structure occurs in pretraining data (the base was trained on proofs of this kind) |
| **neither** | R fails |

**This is not a base-model definition:** a theorem can be out of data but solvable by the base (the base generalised
in pretraining), and then RL "created relative to data" while only "elicited relative to the base". Report both.

## 3. Null or floor

- The pretraining data are the reference; random weights are irrelevant.
- The floor is "how often does the *base* solve out-of-data items?" If the base already does, data-novelty is not RL's
  doing.

## 4. How to compute it here

CPU only, from K12 (`data/kh/train_k12.jsonl`) and the cap-6 set.

- **(T) for excluded middle** (`log.md` 05:11; `NOTES.md`). K12 has 163 records with an X ∨ ¬X conclusion, **all with
  premises; 0 are premise-free**. The DN rule occurs in 21,274 of 155,000 records (13.7 %). So s1's r16 A ∨ ¬A proofs
  are out of data at level T but not at level M. The base solves 0 / 6 holdout250 members at k 256 on every seed.
- **(L):** at cap 6, the theorems whose RL proofs need > 6 lines; cap-6 reads and L_true labels exist. `trajectory-cap6`
  B / C groups and `rl-continue-cap6`: cap-6 r16 solves group-C theorems with L_true 7–12.
- **(S), computed** (`analysis/cd_skeleton.py`, `out/skeleton.txt`, `log.md` 07:15). Skeletons are indexed from K12
  (155,000 proofs). A theorem counts as "novel" for a model if none of the model's accepted proofs of it (x0 ∪ x1) has
  an in-data skeleton. Theorems novel / solved:

  | abstraction | pend s0 | r8 s0 | r16 s0 | pend s1 | r8 s1 | r16 s1 |
  |---|---|---|---|---|---|---|
  | (depth, rule, citation offsets) | 211 / 236 | 261 / 289 | 268 / 294 | 218 / 245 | 259 / 287 | 277 / 303 |
  | (depth, rule) sequence | 176 / 236 | 227 / 289 | 236 / 294 | 186 / 245 | 226 / 287 | 244 / 303 |
  | rule multiset | 82 / 236 | 120 / 289 | 129 / 294 | 91 / 245 | 122 / 287 | 148 / 303 |
  | **rule set** | **3 / 236** | **14 / 289** | **15 / 294** | **15 / 245** | **18 / 287** | **29 / 303** |

  **The base itself solves most theorems only with skeletons that never occur in its data.** At any abstraction finer
  than the rule set, data-novelty does not separate RL from the base. At the rule-set level, RL adds 11–14 theorems
  whose combination of rules never occurs in K12. That is a small, coarse signal.

## 5. Sensitivity

- **Level choice:** length is coarse and skeleton is fine. Skeleton novelty fires on any reordering.
- **Abstraction:** what counts as the "same" skeleton (formula abstraction, line order) determines everything.
- **Representation:** ND rules vs Lean terms. Under Lean a proof may skip steps ND requires, so the length is lower.
- **Renaming:** classes are atom permutations (F is falsum).
- **Seed:** data-novelty is seed-independent for a fixed dataset; whether RL reaches it is not.

## 6. Failure modes

- **Data-novel ≠ base-novel:** the base may generalise beyond its data (it often does: depth-3 proofs appeared without
  depth-3 data in `lean-format`).
- **Generator artefacts:** the cap and the generator's rule distribution define the boundary arbitrarily. A
  "new-expert" item may be a trivial padding of an old one (`passk-equal-k` §6, `tf-proof-prob` §9).
- **Exact-match lookup understates closeness:** near-duplicates are not novel in any useful sense.

## 7. Relations

- The data-relative counterpart of every base-relative card.
- `causal-ablation` turns it into an intervention (remove the structure from the data, then test).
- `schema-acquisition` uses the type level.
- `transfer-invariance` uses the length level.

## 8. Literature anchor

- **Keysers et al. 2020 (1912.09713):** compound divergence D_C at fixed atom divergence (Sec. 2.1).
- **Yu et al. 2023 (2310.17567), Skill-Mix:** a counting argument against the corpus (Sec. 6).
- **Shin et al. 2023 (2303.07462):** novelty = first departure from a dated database (L6 note).
- **Romera-Paredes et al. 2023, FunSearch** (screened): "new" relative to the literature.
- **Group meeting 20-09** (Dan; Dmitry) and the reading group 2026-09-17, quoted in `analysis/CONTEXT_DIGEST.md` § 4.

## 9. Critic's verdict

*(pending)*
