## 2. The catalogue (20 cards; full cards in `capability_defs/cards/`)

Status after the critic pass: **standard** = recommended (§4); **kept** = valid with the revision shown; **descriptive** = a
useful number, not a verdict; **dropped** = fails as a decision rule.

| # | card | family | what it calls "RL created a capability" (post-critic) | status | here (cap 12, r8, seed 0 unless stated) |
|---|---|---|---|---|---|
| 1 | `passk-budget` (Dan's b) | sampling | RL solves t at k 256, and the base, given RL's compute as attempts on the evaluation theorems (K_eval-set ≈ 2 × 10⁴), never does; net of replay | **standard** | see §3.1 |
| 2 | `marginal-bracket` | sampling + likelihood | the base's k-to-solve interval [1 / UB, 1 / LB] lies above the budget | **standard** (its interval is the primary per-theorem output) | lower bound recovers 96 % of measured p on calibration theorems |
| 3 | `tf-proof-prob` (Dan's a) | likelihood | the base's *best known* proof of t (not RL's) is below 1 / K, and the base fails at k_eval | kept (RL's own proof only a descriptive "new route" tag) | see §3.2 |
| 4 | `passk-equal-k` | sampling | base 0 / 256, RL ≥ 1 / 256 | descriptive (group B) | 54 / 51 / 60 per seed |
| 5 | `capability-vs-propensity` | elicitation | no *per-theorem* method (more samples, guided redraws, prior-only search) reaches t within the budget; carrying verdicts across theorems is RL's defining act | **standard** (reporting format) | guided reads in §3.4 |
| 6 | `elicit-finetune` | elicitation | demonstrations raise the knockout (never-had-it) model as much as the base → teachable, not latent | kept (J6b design) | §3.5 |
| 7 | `reliability` | reliability | p̂_R ≥ ½ and the base outside the budget | kept (propensity side) | 13 of 24 compute-matched theorems |
| 8 | `schema-acquisition` | family | the family (members that *need* its key step) goes from base ≈ 0 to RL ≥ ½ on held-out members | **standard** | excluded middle s1, Peirce s2, … |
| 9 | `transfer-invariance` | family | mean over renamings / held-out members, key-step members only | folded into 8 | — |
| 10 | `irt-ability` | psychometric | RL's item-level gains exceed those of an ability-matched placebo (more pretraining, replay-only) | kept: **finds no RL-specific excess** | §3.6 |
| 11 | `compute-equivalent` | compute | what RL solves that a compute-matched pretraining continuation (J7) does not | kept (J7) | §3.6 |
| 12 | `sharpen-expand` | distribution | reshaping bits beyond the replay-only placebo | descriptive (ρ degenerate on hard theorems) | — |
| 13 | `new-proof-new-theorem` | likelihood + sampling | new theorem (certified) ∧ new *method* (route class absent from all base proofs) | kept (cross-theorem NP) | 5 theorems (s0) |
| 14 | `kl-update-size` | distribution | — | dropped (optimizer confound; RL ≈ replay update) | relative norm 0.28 vs replay 0.30 |
| 15 | `chain-reachability` | sampling | — | dropped (the base certificate alone decides); kept as mechanism | — |
| 16 | `bits-over-null` | null-relative | — | dropped (RL's share ≤ 5 % by construction against init) | median share 1.0–1.4 % |
| 17 | `out-of-data-novelty` | data-relative | RL's proofs use a combination of rules no pretraining proof uses | descriptive (the base is data-novel too) | 14 theorems (rule-set level) |
| 18 | `composition` | step-level | new composition (every step in base support) vs new move | pending critic | — |
| 19 | `latent-probe-steer` | mechanistic | probes / 2 × 2 steering / diffing | not computed | — |
| 20 | `causal-ablation` | intervention | RL from a base pretrained without the skill reaches it | partly run (J6, J6b) | §3.5 |
