# OUTLINE — "Did RL create it?" (paper draft and blog post)

Run `create-or-elicit-paper`, 2026-10-13. Every claim below names its evidence (figure / table) and its source. Ledger
rows `L#` are `claims_ledger.md` v3 on this branch. `R§n` is a section of `review_create-or-elicit.md` (§Recount / §Verdict),
whose corrections win over the ledger. `S-coe Obs n` is an observation of the librarian summary, which carries the review's
wording. Rows of other runs cite their own reviews through the ledger. `paper/LEDGER.md` is built from this outline and
holds one row per number as it finally appears.

**Model for every number unless stated:** `best_model.ALiBiGPT`, 6 layers × 384, 9,560,832 parameters, `lean_staten`
(proof-state environment, environment-assigned names), trained from scratch (Stage 1, 1,200 s on one A40), then T1
expert iteration (k 32, T 0.8, 600 fine-tune steps per round, 4,495 `rl_targets`, 20,000 replay records per round). Lean 4
core alone judges. Arms: **full** (K12; s0–s2 from `trajectory` / `rl-continue`, s3–s5 new), **knockout** (K12⁻; s0–s5),
**dose** (K12^1%; s0–s2).

## Working title

**Did RL Create It? A Pretraining Knockout, Compute-Matched Budgets and Exact Likelihoods in a From-Scratch Prover**

(Alternative for the critics: "Expert iteration amplifies what pretraining exposed: a composition knockout in a
from-scratch theorem prover".) "Interface" stays out of the title (proposal 27).

## One-paragraph story

Whether RL "created" a capability is not a yes/no fact about a model. It depends on the budget at which the base is
judged unable, on controls for what RL's extra training does without RL, and on what the base saw. In a from-scratch
prover with exact likelihoods we can do what cannot be done with LLMs: remove one inference composition (σ, the classical
reductio) from pretraining and run the same RL. Within 16 rounds, expert iteration from σ-free bases acquired no classical
family on 6 / 6 seeds, against 6 / 6 full-exposure seeds (pre-registered, p = 0.00024; 5 / 6 vs 0 / 6 acquired during
RL). Restoring σ in 1 % of pretraining restored acquisition on 3 / 3 seeds. The knockout bases still write σ, at about
10⁻⁶ per attempt on family members. The one knockout ladder that made progress did so mostly on members its base could
already reach within RL's budget. In this organism, EI amplified a composition that was rare-but-present in the base,
and did not, within 16 rounds, build it from a σ-free base. On the measurement side, equal-k "creations" shrink by
about 60–75 % once the base gets RL's compute as attempts. Test-time search and guided redraws recover a large part
of RL's gain at the base and add little after RL.

## Contributions (as the introduction will list them)

1. **An organism for causal create-vs-elicit questions:** a from-scratch prover over propositional logic, Lean as the
   only judge, teacher-forced likelihoods for any proof, and pretraining data that can be edited one inference
   composition at a time (§3).
2. **A measurement protocol, applied end to end** (§4). Budgets in base attempts matched to RL's compute (the created
   set is a curve in K, not a number). k-to-solve intervals from sampling plus a known-proof estimator calibrated down to
   p ≈ 10⁻⁴. Clopper–Pearson certificates. RL-free controls (replay-only, compute-matched continued pretraining,
   ability-matched placebos).
3. **A pre-registered causal knockout** (§5): σ-free pretraining → no classical family acquired by EI in 16 rounds
   (0 / 6 vs 6 / 6); 1 % σ restores it (3 / 3). Diagnostics separate "absent" from "rare": base rates at 10⁶ attempts,
   certificates, log p of known proofs along the ladders, and an extended ladder.
4. **Negative and null results reported at their strength:** a power-sampling null that fails its own positive control
   (sampler-specific); a seeded-round null; the knockout's own costs to general ability.
5. **Test-time compute before and after RL** (§6): guided step redraws and PUCT search help the base far more than the
   RL model; after RL, search finds nothing sampling does not on the hardest theorems.

## Section plan, claims and evidence

### Abstract (≤ 250 words)
Claims: question; organism; knockout result (0 / 6 vs 6 / 6, p = 0.00024; RL-only 5 / 6 vs 0 / 6, p = 0.0032); 1 % dose
3 / 3; σ rare not absent (10⁻⁶; 2 / 6 certified); budget shrink (54 / 51 / 60 → 21 / 20 / 14); test-time compute;
scope (9.56 M, propositional, 16 rounds, one RL algorithm). Sources: L89, L91 (corrected p), L97, L88, L1, L2, L28, MCTS-a
summary.

### 1. Introduction
- The debate: RLVR improves pass@1, yet base models overtake RL at large k [Yue et al., L67]. Is RL creating or
  eliciting? Sharpening without training reaches much of RL's gain [Karan & Du, L71].
- Three missing ingredients: (i) a budget (p > 0 for any proof at random init: e^289–e^3,228 attempts, L18), (ii)
  controls for non-RL training, (iii) an intervention on what the base saw. LLM studies have the first at best.
- This paper: a small organism where all three are possible. Headline result and contributions list.

### 2. Related work
Positioning (from `paper/notes/related_work_digest.md`, sub-agent; verified quotes only):
- RL expands vs sharpens: Yue et al. (equal k ≤ 1,024, L67); ProRL; coverage / pass@k work.
- Controlled organisms: Abdulsalam, Patel & Saxe (L68: pretraining excludes the shortcut, pass@1024 = 0, RL solves; a
  new action type; equal k); Tsilivis et al. (L69: amplification efficient unless exponentially small; p_cot = 0
  untested, quote at 0.01 only); Interplay (L70: 0 % / 0.1 % context exposure no transfer, 1 % enhances).
- Power sampling: Karan & Du (L71), Ji et al. (L72, abstract-level only: cite as such), Talwar et al. (lit UPDATE: MCMC
  power samplers do not converge at realistic budgets).
- Elicitation / latent capability: password-locked models, sandbagging, URIAL, fine-tuning enhances existing mechanisms.
- Rare outputs and budgets: repeated sampling, rare-output estimation, pass@k estimators, IRT (capability-defs cards).
- EI and theorem proving: ExIt, STaR-like filtering, DeepSeek-Prover, HTPS, AlphaZero concepts.
- Data ablation / unlearning-relearning.
Our differences: zero exposure at the level of one composition, with refill, held-out families, large-k base rates
and certification; 6 seeds per arm; compute recorded per arm.

### 3. Organism and setup
| claim | evidence | source |
|---|---|---|
| Model, data, interface, judge, EI protocol, Stage 1 | text, Table 1 (setup) | S-coe Configuration; L-legend (M12); L46 (3.7 epochs) |
| K12: 155,000 synthetic ND proofs, 2–12 lines; every RL rule ≥ 8.0 % of records | text | L42; legend |
| σ definition; σ in 16,703 records; σ⁺ in 16,961 (10.94 %); lemma route 0 | text, Lean example box | L78; R§1; S-coe Obs 1 |
| Families: six classical generator families, 40 trained + 40 held-out members each; strict members 123 trained / 106 held-out (per-family counts) | Table 2 | L82; R§2; S-coe Configuration |
| Reads: plain k 256, T 0.8, 96 steps, 512 tokens / action; guided ≤ 10 rejections | text | S-coe Configuration |
| Evaluation sets: the 322 (textbook72 scoring only + holdout250); transfer pool; p2/heldout 5,000 | text | legend; L60 |
| Lean examples of a σ proof (free positive reductio) and the lemma route | Box 1 (rendered with `nd2lean`, checked by Lean on the VPS) | `artifacts/coe/examples/knockout_first_sigma.md` (items 3–5); this run renders and checks them (`paper/scripts/lean_examples.py`) |

### 4. Measurement framework (applied to the full arm's old seeds s0–s2)
| claim | evidence | source |
|---|---|---|
| A capability is p(t) at a stated budget; k-to-solve = 1/p; random init needs ≤ e^289–e^3,228 attempts by the known-proof bound | text | L18 (corrected wording) |
| Equal-k "creation" (pend 0/256, r8 ≥ 1/256): 54 / 51 / 60; is a fact about n | text | L1 |
| Five budget allocations (K_att · K_train · K_uni · K_pub · K_adapt) at r8: 3,574 · 7,416/7,126/9,921 · 10,314/10,141/14,150 · 19,281/21,107/23,310 · 44,570/43,427/56,509; 0.15–0.19 / 0.34–0.43 / 0.48–0.61 / 1 / 2.1–2.4 × K_pub | Table 3 | L74, L73; R§12 / S-coe Obs 9 (reproduce) |
| The compute-matched set is a curve: 34/33/33 · 33/27/24 · 28/26/24 · 22/21/14 · 21/20/14; 21/20/14 at all five; 18/17/8 of them with 0 base successes in ≥ 66,304 attempts | Fig 4 (budget curve) | L2, L75; S-coe Obs 9 + rewording 5 |
| Net of replay-only: 20/14/8 at K_pub; 4/5/5 never solved by any seed's base | text | L3, L4 |
| Set level: Δ_cov positive at every allocation and seed (+21/+16/+12 at K_pub) | text | L10 |
| Known-proof estimator: 0.98/0.94/0.93 of measured p on calibration theorems; by p̂ bin 0.937 (≥ 10⁻³), 0.883 (10⁻⁴–10⁻³), 0.454 (10⁻⁵–10⁻⁴); runs ≈ 2× low below 10⁻⁴ | Fig 5 (calibration), Table | L15, L76, L77; S-coe Obs 9 (p̂-bin table reviewed; by-E bins not recounted → label) |
| Certification: UB95 < 0.05/K, needs ≈ 60 K zero-success attempts; J9 7/9 pairs at K_pub; 4 pairs on 3 theorems survive every RL-free control; only Peirce 1833 classical-only | text | L20, L22, L11 |
| RL-free controls: replay-only r8 solves 239/244/249 vs r8 286/286/293 vs pend 232/236/234; J7 220/215/219 (lateral move); no RL excess at matched IRT ability; update size RL 0.28 vs replay 0.30 | text / small table | L43, L45, L47, L48, L49 |
| Definitions disagree: mean Jaccard 0.29 / 0.34 across 12 definitions | text | L23 |
| Exact likelihoods (trajectory): eventual proof's worst step −6.2 → −1.3 nats by r8; group C reference proofs do not improve | text | L56, L59 |
| Knockout decision rule and power: created / needs exposure / neither; rejects at (3,0), (5,1), (6,2); 0/6 bounds per-seed creation rate < 0.39 | text | S-coe Configuration (pre-registered rule), R§Verdict "Next" 1 |

### 5. Results: the σ knockout (centre of the paper)
| claim | evidence | source |
|---|---|---|
| 5.1 K12⁻ = K12 minus exactly the 16,961 σ⁺ records, refilled per length from K12's own pools; filters hold; 0 overlap; refill Lean-accepted 16,961/16,961 (with negative control) | text | L79, L81 (stale caveat corrected), R§1, R§13, S-coe Obs 1 |
| 5.1 What else shifts: DN records 13.73 % → 3.29 %, NEGI 15.21 % → 5.19 %, classical-only 4.17 % → 1.35 % (−67.6 %) | text | S-coe Obs 1 (reviewer's values; ledger L80 has 4.13 → 1.33 from another sample: use the reviewed) |
| 5.1 General ability: held-out greedy −6.88 pp; +0.12 pp on 4,321 non-σ; 0.96 vs 0.45 on 679 σ; pass@256 at pend lower also on intuitionistic theorems (holdout250 −4.3 / 225; textbook72 −4.0 / 53); holdout250 recovers by r16, textbook72 −2.5 | text, appendix table | L93, R§8, S-coe Obs 7, rewording 2 |
| 5.2 **Primary (pre-registered): 6/6 full vs 0/6 knockout seeds have ≥ 1 family at the bar at r16; Boschloo p = 0.00024; x1 and guided same; original 178 sets same** | **Fig 1, Table 4** | L89–L90, R§3, S-coe Obs 2 |
| 5.2 Members solved 23–77 vs 0–2 (U = 36, p = 0.0011); IQM difference 53.0 [31.0, 72.8] of 106 | Fig 1 | R§3, R policy items (IQM) |
| 5.2 Per family (Holm over 6): contraposition_conv 6 vs 0 (Holm 0.0015); three families 3 vs 0 (p 0.034, Holm 0.17); excluded_middle 1 vs 0 (p 0.39); demorgan 0 vs 0 | Table 4 | R§3 (corrected p) |
| 5.2 RL-only reading: contraposition_conv at the bar at pend on 5/6 full seeds; acquired during RL 5/6 vs 0/6, **p = 0.0032** | text | L91 → corrected, R§3 |
| 5.2 Training side: knockout never reaches training share ≥ 0.5 on any family; strict trained targets solved r1 → r16 full 21→49 … knockout 0 in r1 on 6/6 | Fig 2a | R§4, S-coe Obs 2 |
| 5.3 Dose 1 % (1,550 σ records): r16 strict 58/39/30; families acquired during RL 3/3; vs knockout p = 0.0033 (exploratory); round 1 σ proofs 223/183/241 | Fig 1, text | L97, S-coe Obs 3 |
| 5.3 (C2, this run) dose r16 x1 and guided reads | Table | `artifacts/coe_paper/` (this run, pre-registered C2) |
| 5.4 σ in round 1 of every knockout ladder (6–13 σ proofs, sequent supplies ¬¬G); free positive reductio in 5/6 ladders (0/34/4/1/2/16 proofs over 16 rounds vs 17–50 thousand per full ladder) | Fig 2b | L84, L92, R§5, S-coe Obs 4 |
| 5.4 Certificates at K_train(16): s0, s3 certified out of reach (0 / 1.49 M, 0 / 1.34 M); s1, s2, s4, s5 not (6, 1, 3, 2 successes); no family certified; every knockout-base success on a strict member is a genuine σ | Table 5 | L88, R§6, S-coe Obs 4 |
| 5.4 Knockout s1's base has 4/18 contraposition_conv members within reach at K_train (**superseded by C4**: at n = 18,432 without early stopping, 916, 1460, 1096 and 1606 are within reach; 3 of the 5 members the ladder proves are not; the "mostly within reach" reading is dropped) | text | R§Verdict 5, rewording 3; C4 |
| 5.4 Log p of best known σ proof (median over 101 members): knockout bases −26 to −36 nats vs full s0 −19.2; pend → r16: full s3 −15.4 → −5.1, dose −25.3 → −8.7; knockout flat or falling; box-opening step −18.0 to −21.6 vs −10.5 | Fig 3 | L87, L98, R§11, S-coe Obs 4 |
| 5.5 Knockout s1 to r24 (exploratory): free+ per round 11 → 123; strict targets stall at 9; held-out 5/106 at r20 and r24, solved more often; 3 of its 4 contraposition_conv members were within its base's reach → elicitation | text, Fig 2 dashed | L96, R§Verdict 5, S-coe Obs 5 |
| 5.6 Phase 3a: one seeded round changes nothing (+2 on 1/5 seeds, p 0.25) | text | L95, S-coe Obs 6 |
| 5.7 Theorem-level compute-matched reach does not need σ: Δ_cov full +37/+36/+32 vs knockout +21 to +37 | text | L94, R§7, S-coe Obs 8 |
| 5.8 Sharpening null for one MH power sampler at matched decoded tokens (0/33, 0/27, 0/106) — and the sampler fails its positive control (0/17 vs plain 6–13/17); sampler-specific | small table | L85, L86 (reworded), R§9, S-coe Obs 10 + rewording 4 |
| 5.9 Robustness: redraw, guided, 178 sets, Lean re-check 448/448 + controls, prefilter 0/1,950 false rejects, replay never carried σ, splits | text | R§13, R§14, L99, S-coe Obs 12 |
| 5.9 (C1, this run) what the cut-offs hide: paired standard vs doubled caps on knockout r16, dose r16, full s4 r16 | Table | `artifacts/coe_paper/` (this run, pre-registered C1) |
| 5.10 (A2, exploratory, post hoc) base prior vs acquisition across ladders | Fig 6 | `paper/scripts/` (this run) from L87/L98 files |

### 6. Test-time compute before and after RL
| claim | evidence | source |
|---|---|---|
| Guided k 256 adds +18 to +22 on holdout250 for pend, −1 to +4 for r8 / r16 (ceiling); textbook72 pend +8/+10/+12 vs r8 +6/+4/+3; the r8–pend gap shrinks 44/31/37 → 21/14/19 | Fig 7a | L28 |
| Guided rescues part of the compute-matched sets (not compute-matched itself; 2.18× GPU-s per attempt) | text | L29, L31 |
| At matched sampled tokens guided beats plain on long problems on 6/6 r8 models (+5.2 to +10.3 pp) | text | L32 (MDD part not reviewed as stated) |
| MCTS (PUCT + learned value) at r8: gate fails on group C (Δ −2/0/−1); within ±3 of sampling on every pool | Fig 7b | mcts-a summary (reviewed) |
| At pend, search helps on the long pool: +19/+10/+14 (≈ 44 % of what 8 EI rounds add by sampling); value adds +5.3 over prior-only | Fig 7b | mcts-a summary (reviewed; CI executor's) |
| Interpretation: at the base, search substitutes for part of RL; after RL little is left — consistent with RL concentrating mass the base already spreads | text | (interpretation) |

### 7. Discussion
- What "creation" means here; the evidence ladder (equal k → budget → controls → certificate → intervention).
- Amplification threshold: 1 % exposure is enough; 0 % with base rates ≈ 10⁻⁶ is not, in 16 rounds of EI at k 32.
  Back-of-envelope: 123 strict targets × 32 attempts ≈ 3,900 attempts per round, so ≈ 0.004–0.02 expected σ proofs per
  round at pooled base rates of 1–5 × 10⁻⁶ (`paper/scripts/` arithmetic from L88). This explains why exploration, not
  credit assignment, is the bottleneck. Connects to Tsilivis (exponentially small proportions), Interplay (0 % / 0.1 % vs
  1 %), Abdulsalam (pass@1024 = 0 is not p = 0).
- Implications for evaluations and safety: "not elicited at k 256" is not "absent"; state budgets; report the curve.
- Earlier, smaller organism: "the 29 creations" in the 3.2 M whole-proof organism are reached by a proof-state base
  (28 / 29), confounded with the step interface (L51–L54). Interface as a future axis.

### 8. Limitations
Scale (9.56 M), propositional logic, near-saturated targets (97–98 % of `rl_targets` by r8, L64; saturation falsified as
pre-registered but targets mostly solved), seeds (6/6/3; per-family tests undetermined; ≈ 12–15 per arm for excluded
middle), one RL algorithm (T1 EI) and 16 rounds, the knockout also costs general ability, certification for 2/6 bases and
no family, estimator below 10⁻⁴, sharpening null sampler-specific, cut-offs (C1), old vs new full seeds pooled across GPU
classes and batches, dose arm reads (C2), Phase 2 plain comparators keep no text.

### 9. Reproducibility
Code (fork branches), data (bucket paths, md5s), compute table per arm (GPU-s, tokens, Lean checks, pod-hours, $), the
pre-registrations and their timestamps, the reviews.

### Appendices
A notation; B families and strict sets; C K12⁻ construction; D all per-seed reads; E budgets; F estimator; G certificates;
H power sampling; I pre-registered expectations vs outcomes (hits / misses); J Lean examples; K compute; L corrections
applied (Boschloo transposition, rewordings); M this run's checks C1–C3.

## Figures (all regenerated by `paper/scripts/`)
| # | content | data |
|---|---|---|
| F1 | strict held-out members solved per seed: pend and r16, full / knockout / dose; family-at-bar markers | `artifacts/coe/compare_{pend,r16}_x0.json`, `dose_summary.json` |
| F2 | (a) strict trained targets solved, cumulative per round; (b) free positive reductio proofs per round (log) | `artifacts/coe/rounds/*.json` |
| F3 | median log p of best known σ proof along each ladder | `artifacts/coe/score/rounds_*/summary.json`, `score/summary.json` |
| F4 | compute-matched set vs K with the five allocations marked | `artifacts/coe/budget/` |
| F5 | estimator calibration | `artifacts/coe/estimator/per_theorem.json` |
| F6 | (exploratory) base prior vs r16 acquisition across ladders | F1 + F3 data |
| F7 | test-time compute: guided and PUCT vs plain, pend vs r8 | capability-defs J3 files, mcts-a `artifacts/mcts/summary.json` (fork branches) |
| Box 1 | σ in Lean (free positive reductio; lemma route) | `nd2lean` render, Lean-checked |

## Blog post plan (`paper/blog.md`, 1,500–2,500 words, 4 figures)
1. So what first: "We removed one reasoning move from a small prover's training data. RL could not bring it back in 16
   rounds; putting back 1 % was enough."
2. The question in plain words (create vs elicit), why LLM studies cannot settle it.
3. The organism (what a proof is, what σ is, with the 3-line Lean example).
4. The knockout result (F1) — including that the knockout models still wrote σ, very rarely.
5. Why "created" depends on the budget (F4).
6. Search at test time (F7).
7. What we did not show (limitations, nulls), what's next.
Figures: F1, F2b or F3, F4, F7.
