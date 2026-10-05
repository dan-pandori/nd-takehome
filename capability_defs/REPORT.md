# What should "capability" mean for this project, and how do we measure it?

Run `capability-defs` (proposal 26), 2026-10-05. Executor: agent:claude (`--effort max`). Branch `dan_capability-defs`
on the fork. Pre-registration: `preregistration/capability-defs.md` (3e6f9865) plus a `log.md` entry before every pod
job. Lean alone decides everywhere.

**Models.** Every number is measured on **best-cap12** unless labelled otherwise: `best_model.ALiBiGPT`, 6 × 384,
9,560,832 parameters, `lean_staten` proof-state format, trained from scratch on K12 (`data/kh/train_k12.jsonl`, 155,000
generated proofs, cap 12; Stage-1 1,200 s on an A40).
- **pend:** end of pretraining (run `trajectory`). **r8 / r16:** after 8 / 16 rounds of expert iteration, EI (the T1
  ladder of `trajectory` / `rl-continue`). Seeds s0–s2.
- **Cap 6:** the same network and recipe trained on the cap-6 set (`trajectory-cap6`, `rl-continue-cap6`).
- **Evaluation theorems:** textbook72 (scoring only, under its manifest rule) and holdout250: 322, never trained on.
- **Reads:** plain sampling, T 0.8, 96 steps, 512 tokens per action, k 256 per draw (x0, x1 = two sample seeds).
  Guided read-outs are labelled.

## 1. The plain answer

⟨PLAIN⟩

## 2. The catalogue

Twenty definitions, one card each in `capability_defs/cards/` (shared notation: `cards/_FRAME.md`). Each card gives:
- the formal quantity and a decision rule (created / elicited / neither / undetermined);
- a null, the cost here, sensitivities and failure modes;
- relations to other cards and literature anchors (`lit/REVIEW.md`: 185 papers screened, 57 read in depth);
- **a critic's verdict.** One subagent per card argued that the definition fails. Its strongest argument and my answer
  are on the card.

**Every critic landed a failure I accepted** (pre-registered: at least a third would). Six definitions are dropped as
decision rules, two are kept only as descriptions, one is folded into another, and the rest were revised.

Status after the critic pass: **standard** = recommended (§4); **kept** = valid with the revision shown;
**descriptive** = a useful number, not a verdict; **dropped** = fails as a decision rule. Families: S sampling,
L likelihood, E elicitation, T transfer, R reliability, P psychometric, C compute, D distribution or update, N null,
M mechanistic, X intervention. Last column: created-set size at r8 (draw x0), s0 / s1 / s2, where computed (§3.2).

| # | card | fam. | "RL created a capability on t" (after the critic) | status | r8 set |
|---|---|---|---|---|---|
| 1 | `passk-budget` (Dan's b) | S | RL solves t at k 256; the base is not within reach at K_eval-set (p̂ < 1 / K over ≥ K attempts); net of RL-free training | **standard** | ⟨cm_net⟩ |
| 2 | `marginal-bracket` | S L | the base's k-to-solve interval [1 / UB, 1 / estimate] lies above the budget (not certified elicited) | **standard**; the interval is the primary per-theorem output | ⟨brk⟩ |
| 3 | `capability-vs-propensity` | E | no per-theorem method (more samples, guided redraws, renamings) reaches t within the budget | **standard** (reporting format) | ⟨guided⟩ |
| 4 | `schema-acquisition` | T | a key-step family goes from base ≤ 0.05 to RL ≥ 0.5 on held-out members | **standard** | ⟨schema⟩ |
| 5 | `elicit-finetune` | E | demonstrations teach the base no faster than a never-had-it knockout → *teachable*, not latent | kept (teachability test) | §3.6 |
| 6 | `tf-proof-prob` (Dan's a) | L | the base's *best known* proof has π < 1 / K and the base fails at k_eval | kept (RL's own proof only a "new route" tag) | ⟨tfmax⟩ |
| 7 | `reliability` | R | p̂_R ≥ ½ and the base not within reach at K | kept (RL side of 1) | ⟨rel⟩ |
| 8 | `irt-ability` | P | RL's DIF+ items exceed those of an ability-matched RL-free placebo | kept: **finds no RL excess** | 26 / 26 / 30 (unmatched) |
| 9 | `compute-equivalent` | C | RL solves t; a pretraining continuation with RL's GPU time does not (J7) | kept | ⟨j7⟩ |
| 10 | `new-proof-new-theorem` | L S | 1, and every RL proof of t uses a rule set no base-accepted proof of any theorem uses | kept | ⟨npnt⟩ |
| 11 | `transfer-invariance` | T | the gain holds on held-out members and renamings | folded into 4 | — |
| 12 | `sharpen-expand` | D | RL's success mass sits on proofs the base would not reach (ρ ≥ ½), beyond the replay placebo | descriptive | ⟨sharp⟩ |
| 13 | `passk-equal-k` | S | base 0 / 256, RL ≥ 1 / 256 | descriptive ("group B") | 54 / 51 / 60 |
| 14 | `causal-ablation` | X | RL from a base pretrained without a *composition* acquires the family | redesigned, not run (≈ $26) | — |
| 15 | `chain-reachability` | S | t solved only after the ladder solved easier theorems | dropped; mechanism column | ⟨chain⟩ |
| 16 | `out-of-data-novelty` | D | RL's proofs use a rule combination absent from pretraining | dropped; descriptive | ⟨ood⟩ |
| 17 | `composition` | S | a step outside the base's support ("new move") vs new placement | dropped; bottleneck column | — |
| 18 | `kl-update-size` | D | RL's update is large or RL-specific | dropped (RL update ≈ replay update) | — |
| 19 | `bits-over-null` | N | RL's share of the bits over random init | dropped (≤ 5 % by construction) | — |
| 20 | `latent-probe-steer` | M | probes, steering, model diffing | dropped; not computed | — |

What the critics established:
- **"Created at k" is a fact about n, not about the base.** 0 / 512 base attempts put the base's k-to-solve above
  ≈ 170, while RL's budgets are 10³–10⁶. Equal-k is kept only as the project's descriptive "group B".
- **RL's own proof is the wrong object for likelihood.** RL's preferred proof is often the base's proof plus a vacuous
  detour: 35 of 120 cases contain a self-built Or-detour (`la_transfer_629`: pend solves it 178 / 256). Decide on the
  base's *best known* proof and on the sum over known proofs.
- **"Tied to RL's compute" is a menu of budgets.** Per training target, per evaluation theorem, or all of RL's compute
  on one theorem differ by 10⁴. The headline must be one set-level, compute-matched comparison.
- **Placebos must be matched.** IRT "gains beyond the pretraining axis" looked like 26–30 RL-created theorems against
  4–7 for a replay-only placebo, but the placebo had a third of RL's ability gain (§3.7).
- **Generator templates are not proof schemata.** Many members of the classical families are provable without the
  classical step, and those members carried the family rates. Families must keep only members that need the key step.
- **Elicitation methods must be per theorem.** A fine-tune or value head trained on verifier verdicts for *other*
  theorems is RL by another name.
- **Novelty tests cannot decide creation here.** Every rule RL uses occurs in ≥ 4 % of pretraining proofs, so "new
  move" measures placement (composition); and once a theorem is out of the base's reach, every proof of it is too.

## 3. Quantification on our models

### 3.0 Set-up

- **Existing artefacts:** plain reads of 22 checkpoints × 3 seeds × 2 draws at both caps; teacher-forced scores of
  references and RL's proofs; ladder logs; `rl-from-ckpt`'s ladders and replay-only controls.
- **Pod jobs** (NVIDIA A40, $0.49 / h), each pre-registered in `log.md` before launch:

  | job | what it did |
  |---|---|
  | J1 | teacher-forced scores under init / pend / r8 / r16 of every known accepted proof of the 322 theorems: 1.2–1.4 × 10⁵ proofs per seed at one name base, the top ≈ 4,500 per seed at all 33 |
  | J2 | 16,384 more pend attempts on every hard theorem; 65,536 where 16,384 found nothing; doubled-cap truncation check |
  | J3 | guided reads (step-checked redraws) of pend / r8 / r16, both caps |
  | J4, J6, J6b | excluded-middle demonstration fine-tunes of pend and of a knockout pretrained without double negation (DN) |
  | J5 | the missing plain draws (cap-12 r16 x0, cap-6 r16 holdout250) |
  | J7 | a pretraining continuation of pend matched to the r8 ladder's GPU time |
  | J8 | J1 scores under four earlier pretraining checkpoints (start dependence) |
  | J9 | certification sampling: ≈ 1.2–1.4 M more pend attempts on 3 theorems per seed |

- **Budgets** (`cards/_FRAME.md`; base attempts cost 3.6 ms on an A40):
  - k_eval = 256;
  - **K_eval-set** = ladder GPU-seconds / (322 × 3.6 ms) = 19,281 / 21,107 / 23,310 at r8 (s0 / s1 / s2) and
    ≈ 4.8–5.0 × 10⁴ at r16: RL's compute spent instead on base attempts over the evaluation set;
  - K_per ≈ 780–1,400 per training target; K_total ≈ 3.3–4.3 × 10⁶.
- **RL-free controls:** the **replay-only** ladder (`rl-from-ckpt`'s c⟨s⟩_pend_r8: the same 8 fine-tune rounds on
  pretraining replay, no RL proofs) and the **compute-matched continuation** (J7).
- **Hard theorems:** pend 0 / 512 on draws x0 + x1: 86 / 77 / 77 of the 322.

### 3.1 How far is the base from each theorem?

For every hard theorem RL solves, pend's k-to-solve is put in an interval (`cd_bracket.py`, `out/bracket.json`; F1):
- **sampling bound:** Clopper–Pearson over every base attempt: ≥ 16,896 per hard theorem, ≥ 66,048 where the first
  16,384 found nothing;
- **known-proof estimate:** pend's teacher-forced probability (T 0.8) summed over every Lean-accepted proof of t that any
  model ever found (J1; the base's own J2 proofs included).

**The known-proof estimate is accurate.** On 30 calibration theorems per seed, where pend's p is measured directly
(≈ 4,900 attempts each), it recovers a median **0.98 / 0.94 / 0.93** of p (s0 / s1 / s2; IQR within 0.85–1.02).
- Over all 54–64 measured theorems per seed, the 10th–90th percentile ratio is 0.2–1.4, and the estimate exceeds the
  sampling UB95 on 1–3 of them. It is not a strict lower bound: the scorer conditions on canonical names, while the
  sampler writes its own names and the environment renames ≈ 14 % of them. Certificates use a factor-2 margin.
- One proof carries most of the sum (median share 0.50–0.62), so Dan's "probability of a specific proof" is close to
  the whole answer *if* the proof is the base's best known one.
- Cost: one forward pass per proof, against 1 / p samples. It reaches probabilities sampling never could: e^−39 on
  s1's hardest RL-solved theorem.

**Where the base sits.** For the 55 / 45 / 52 hard theorems r8 solves, the estimate puts pend's k-to-solve at a median
10^4.6 / 10^5.3 / 10^4.5 attempts (range 10^2.3–10^16.8): right at K_eval-set ≈ 10^4.3. The verdict on a typical
theorem therefore depends on the budget (F2).

![F1](analysis/figures/cd_kts.png)

![F2](analysis/figures/cd_elicit_curve.png)

Verdicts at K_eval-set for the hard theorems r8 solves (bracket rule: elicited if the sampling lower bound or the
known-proof estimate / 2 is ≥ 1 / K):

⟨S31 TABLE⟩

⟨S31 TEXT⟩

### 3.2 What each definition calls "created", and how noisy that is

Created sets at r8 (draw x0) and r16 (draw x1), cap 12, per seed (`cd_part3.py`, `out/part3.txt`; rendered by
`cd_report_tables.py`). "Net" removes theorems the replay-only control solves on the same draw. Redraw floor: Jaccard
of the sets defined on the two sample draws. Seed floor: Jaccard between seeds' sets (pairs s0–s1, s0–s2, s1–s2).

⟨S32 TABLE⟩

- **The sets shrink as a definition asks more of the base.** ⟨S32 SHRINK⟩
- **Redraw floors are high** (⟨0.7–1.0⟩) for every sampling definition, so a verdict is stable across draws of the
  same two models.
- **Seed floors are low** (⟨0.1–0.4⟩): each seed's RL "creates" different theorems. The exception is rule-set novelty
  (0.55–0.62), which compares RL's proofs with the pretraining data rather than with the base.
- **Long pool** (`transfer_long2`, 21 theorems with long proofs; equal-k only, pend x2 vs RL x0): RL "creates" 13 / 15
  / 16 of 21 at r8. J10 gave pend 16,384 more attempts on each: ⟨J10⟩.
- **Cap 6** (weaker bases: pend solves 153 / 126 / 128 of holdout250 plain; no large-k base reads, so only the
  unbudgeted definitions): equal-k 101 / 132 / 122 at r8; reliable 104 / 124 / 110; schema members 31 / 43 / 47. ⟨cap-6
  guided⟩

### 3.3 Do the definitions agree?

![F3](analysis/figures/cd_agreement.png)

- Mean off-diagonal Jaccard ⟨0.27⟩ at r8 and ⟨0.31⟩ at r16 (pre-registered Q14: ≤ 0.4).
- Two clusters: ⟨clusters⟩
- Family-level and novelty definitions agree with nothing (≤ 0.2): they answer different questions.

**Where they disagree, in Lean** (`cd_examples.py`, `out/examples.md`).

⟨S33 EXAMPLES⟩

### 3.4 Threshold sensitivity

⟨S34⟩

### 3.5 Plain vs guided

⟨S35⟩

### 3.6 Families: excluded middle and the classical schemata

**Family-level verdicts** (`cd_schema.py --keystep`; F4). Families are the generator schemata of `rl_targets` and
transfer (40 trained-on and 40 held-out members each). Classical families keep only members that need the classical
step (not provable by G4ip). Shares are per EI round, ≥ 1 success in 32 attempts; round 1 samples pend.

| family (key-step members) | pend (round 1), s0 / s1 / s2 | r16 | verdict | cap-6 r16 |
|---|---|---|---|---|
| excluded middle A ∨ ¬A (39) | 0.00 / 0.00 / 0.00 | 0.00 / **0.95** / 0.26 | created on s1 only | 0.00 / 0.00 / 0.00 |
| Peirce ((A → B) → A) → A (15) | 0.00 / 0.00 / 0.00 | 0.00 / 0.27 / **1.00** | created on s2 only | 0.00 / 0.00 / 0.00 |
| Peirce, sequent form (20) | 0.00 / 0.00 / 0.05 | 0.30 / 0.05 / **1.00** | created on s2 only | 0 |
| negated conditional, classical members (20) | 0.05 / 0.00 / 0.00 | 1.00 / 0.65 / 1.00 | created on 3 / 3 | 0.10 / 0.10 / 0.05 |
| distribution ∧ over ∨ (40; intuitionistic) | 0.00 / 0.00 / 0.00 | 0.97 / 1.00 / 0.93 | created on 3 / 3 | 0.93 / 0.50 / 0.97 |
| De Morgan ¬(A ∧ B) ⊢ ¬A ∨ ¬B, classical members (13) | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 | never acquired | 0 |

![F4](analysis/figures/cd_schema.png)

These verdicts are relative to pend's 32 round-1 attempts; held-out members agree where read. Excluded middle at r16,
39 classical-only held-out instances at k 256: 0 / 36 / 13 solved (s0 / s1 / s2). The six holdout250 excluded-middle
members: pend 0 / 6 at ≥ 768 attempts on every seed; s1 r16 6 / 6.

**Each seed acquires different families.** Excluded middle bursts on one seed (rounds 13–14), Peirce on another. This
is the strongest evidence here that RL *can* produce a family-level capability its own base lacks, and a warning: at
n = 3, "RL creates X" is a per-run event, not a property of the recipe.

**Latent or teachable?** (J4, J6, J6b; 39 classical-only held-out A ∨ ¬A instances, k 256, plain reads.)

| model (cap 12) | s0 | s1 | s2 |
|---|---|---|---|
| pend | 0 | 0 | 0 |
| pend + replay-only fine-tune (A0) | 0 | 0 | 0 |
| pend + 16 non-LEM proofs (C16) | 0 | 0 | 0 |
| **pend + 4 LEM proofs (A4)** | **36** (0.66) | **33** (0.35) | **36** (0.64) |
| **pend + 16 LEM proofs (A16)** | **37** (0.79) | **34** (0.68) | **37** (0.83) |
| RL r16 | 0 | 36 (0.70) | 13 (0.13) |
| no-DN knockout (pretrained without any DN step) | 0 | 0 | 0 |
| knockout + 16 LEM proofs, K12 replay (J6) | 35 (0.71) | 37 (0.72) | 37 (0.70) |
| pend + 16 LEM proofs, DN-free replay (J6b, 2 fine-tune seeds) | 36, 36 | ⟨⟩ | ⟨⟩ |
| knockout + 16 LEM proofs, DN-free replay (J6b) | 34, 34 | ⟨⟩ | ⟨⟩ |
| either model + 16 matched non-LEM proofs, DN-free replay (J6b) | 0–0 | ⟨⟩ | ⟨⟩ |

Cells: solved of 39 (mean pass@1). LEM = law of excluded middle; the demonstrations are s1's RL proofs of *other*
instances. Fine-tunes are one ladder-style round (600 steps, 128 proofs per step).

- Four demonstrations install the schema in every seed's base, including s0, whose own RL never found it in 16 rounds.
- A model pretrained without a single DN step learns it as fast. The pre-registered J6b test (gain over the matched
  control, pend vs knockout; latent if ≥ 0.3 apart on ≥ 2 / 3 seeds, teachable if within 0.2) gives ⟨+0.05 / ⟩:
  **teachable, not latent**.
- The same 16 demonstrations also raise holdout250 solved@64 by +12 / +15 / +5 over the replay-only fine-tune.

**What RL "created" here is the discovery of an instance, not a hard-to-learn ability.** Once one proof exists, the
pattern is cheap to teach, to a base that has it latent or not.

### 3.7 Is RL "more of the same"?

Four set-level tests of whether RL is "more training of the same kind".

**IRT at matched ability** (`cd_irt_matched.py`, `out/irt_matched.txt`). A 2PL model calibrated on the pretraining
checkpoints puts every model on one ability scale θ. An item is "created" if the model solves it far above what its θ
predicts (DIF+, log-odds residual > ln 10) while the start checkpoint failed it in 512 attempts. Rate = created per
start-failed item the model solves.

| calibrated through p5000 (s0 / s1 / s2) | Δθ | created | rate |
|---|---|---|---|
| pretraining continuation to pend (no RL) | +0.65 / +0.41 / +1.14 | 47 / 60 / 54 | 1.31 / 1.22 / 0.86 |
| replay-only ladder r8 (no RL) | +2.12 / +2.09 / +2.14 | 50 / 49 / 54 | 1.04 / 0.80 / 0.73 |
| EI r2 | +2.33 / +2.05 / +2.69 | 48 / 41 / 48 | 0.86 / 0.72 / 0.62 |
| EI r8 | +4.37 / +4.53 / +5.14 | 60 / 54 / 51 | 0.65 / 0.55 / 0.40 |

At matched Δθ, EI "creates" no more than RL-free training (calibrated through p12000 the same holds: EI r2 37 / 46 /
46 vs replay 33 / 47 / 48). The original contrast, 26–30 for r8 against 4–7 for the replay-only placebo, compared
Δθ ≈ 2.1 with Δθ ≈ 0.6.

**Update size** (`cd_update.py`, s0; relative Frobenius norm of the weight change, summed over 26 matrices). RL r8
0.28; replay-only r8 0.30; late pretraining (step 20,000 → pend) 0.81; the gap between two seeds' bases 1.43. The RL
and replay-only updates have cosine 0.45; the RL-specific part (r8 minus replay-only) has norm 0.30. RL moves the
weights less than the last stretch of pretraining did.

**A compute-matched pretraining continuation (J7).** pend trained further on K12 for the r8 ladder's GPU time
(22,350 / 24,467 / 27,021 A40-seconds; ≈ 28,000 steps at s0), then read like RL. ⟨J7⟩

**Start dependence (J8).** `rl-from-ckpt`'s ladders started from earlier pretraining checkpoints. For each start, the
theorems its r8 solves that the start failed in 512 attempts, scored by the start's known-proof estimate:

| start (s0) | new solves | elicited at K_total | replay-only from the same start also solves | net of it | of which elicited at K_total |
|---|---|---|---|---|---|
| step 1,600 | 182 | 21 % | 83 % | 31 | 0 % |
| step 5,000 | 117 | 29 % | 63 % | 43 | 2 % |
| step 12,000 | 86 | 41 % | 66 % | 29 | 17 % |
| step 16,000 | 76 | 32 % | 53 % | 36 | 11 % |
| pend (§3.1) | 55 | 76 % | ⟨⟩ | ⟨⟩ | ⟨⟩ |

⟨J8 s1 s2⟩ From an earlier start, RL's new solves are further out of the start's reach, but most of them are what any
further training on pretraining data would bring; the net remainder is 29–43 theorems at every start.

### 3.8 Certifying a few theorems (J9)

⟨S38⟩

### 3.9 Pre-registered expectations vs outcomes

Scored against `preregistration/capability-defs.md` (L1–L3, Q1–Q16) and the per-job entries in `log.md`. "Hit" means
inside the pre-registered range on every seed unless counted.

| item | pre-registered | outcome | |
|---|---|---|---|
| L1 | ≥ 60 new papers screened, ≥ 20 in depth; ≥ 90 % of cited claims verified; ≤ 2 errors in ≥ 30 re-checked | 185 screened, 57 in depth; 32 / 32 re-checked claims correct | hit |
| L2 | no surveyed definition separates creation from elicitation without a budget or a reference model | none found (`lit/REVIEW.md`) | hit |
| L3 | critics break ≥ 1 / 3 of the cards | 20 / 20 | hit |
| Q1 | equal-k set 45–70 (r8), 55–85 (r16); redraw Jaccard 0.45–0.80 | 54 / 51 / 60; 61 / 65 / 61; 0.68–0.78 | hit |
| Q2 | 60–95 % of J2 theorems get ≥ 1 base success in 16,384 | 47 % / 37 % / 62 % | 1 / 3 |
| Q3 | known-proof estimate certifies 40–85 % of B elicited at K_total; 0 certifiable created there | 76 % / 71 % / 85 %; 0 | hit |
| Q4 | ≤ 25 % of B certified elicited at K_per by the estimate alone | 4 % / 0 % / 8 % | hit |
| Q5 | median log Σ_F π − max log π ≥ 1 nat | 0.33 / 0.45 / 0.44 | miss |
| Q6 | "new proof, old theorem" ≥ 20 % of B | 41 % / 29 % / 37 % | hit |
| Q7 | RL's share of the bits over the null < 2 % for ≥ 95 % of B | median 1.4 / 1.2 / 1.0 %; 81–88 % of B below 2 % | miss |
| Q8 | IRT: pretraining model ranks r8's successes at Spearman ≥ 0.7; r8 above every pretraining checkpoint; ≥ 3 of 6 LEM items in s1 r16's top residual decile | 0.57 / 0.59 / 0.56; yes on 3 / 3; 5 of 6 | a miss; b, c hit |
| Q9 | "p_pend < 0.05, p_r8 ≥ 0.5" is 1.2–2.5× the equal-k set | 1.31 / 1.22 / 1.00× | 2 / 3 |
| Q10 | excluded middle: s1 r16 ≥ 0.5; s0 ≤ 0.1; pend ≤ 0.05 | 36 / 39 solved (0.70); 0; 0 | hit |
| Q11 | 16 LEM demonstrations: held-out pass@256 ≥ 0.5 on ≥ 1 seed; control ≤ 0.1 | 37 / 34 / 37 of 39; control 0 | hit (3 / 3) |
| Q12 | pretraining-length equivalent of r8's ability 3–30× | 6.2 / 4.7 / 7.1× | hit (descriptive only) |
| Q13 | guided pend reads solve ≥ 10 % of B | ⟨⟩ | ⟨⟩ |
| Q14 | mean pairwise Jaccard ≤ 0.4; least-agreeing pair includes the K_total bracket | ⟨⟩ | ⟨⟩ |
| Q15 | known-proof estimate / p̂ median 0.3–1.0 on calibration theorems | 0.98 / 0.94 / 0.93 | hit |
| Q16 | beta-binomial from 256 attempts predicts solves at 10⁴ within ±25 %; zero-inflated at least as well | BB −0 % / +13 % / −7 %; ZIBB −32 % / −23 % / −33 % | BB hit; ZIBB miss |
| J1 stage 2 | replay failures < 1 %; Q15; Q5 expected to miss | 0 failures; Q15 hit; Q5 miss | hit |
| J2 A′ | ≤ 20 % of the hard theorems no RL model solves get a base success | ⟨⟩ | ⟨⟩ |
| J2 B | ≥ 50 % of stage-A zeros stay at 0 / 65,536 | ⟨⟩ | ⟨⟩ |
| J2 truncation | ≤ 1 doubled-cap re-read gets a success | ⟨⟩ | ⟨⟩ |
| J4 | A0 ≤ 0.1; A16's holdout250 solved@64 within ±3 % of A0's | A0 0; +12 / +15 / +5 theorems | A0 hit; ±3 % miss on 2 / 3 |
| J5 | r16 redraw Jaccard 0.6–0.8; cap-6 r16 ≥ r8 on holdout250 | 0.78 / 0.78 / 0.68; 232 vs 225, 233 vs 226, 232 vs 221 | hit |
| J6 | (i) knockout greedy 0.05–0.15 below pend; (ii) knockout 0 / 40 LEM; (iii) holdout250 0.85–0.97× pend; (iv) pend+A16 vs knockout+A16 within 0.2 | (i) 0.06 / 0.09 / 0.10; (ii) 1 / 0 / 1 of 40, the one being the intuitionistic member (0 / 39 classical-only); (iii) 0.88 / 0.80 / 0.85×; (iv) 0.05 / 0.08 / 0.00 | (i) hit; (ii) miss on 2 / 3 (technical); (iii) 2 / 3; (iv) hit, but its replay re-taught DN (→ J6b) |
| J6b | gain difference within 0.2 (teachable) | ⟨⟩ | ⟨⟩ |
| J7 | (i) θ between pend + 0.5 and r8; (ii) solves 30–70 % of B; (iii) solves fewer of the 322 than r8 | ⟨⟩ | ⟨⟩ |
| J8 | elicited share at K_total falls monotonically from pend to p1600; ≥ 50 % for pend, ≤ 25 % for p1600 | ⟨⟩ | ⟨⟩ |
| J9 | ≥ 6 of 9 theorems stay at 0 successes | ⟨⟩ | ⟨⟩ |

### 3.10 Compute

⟨S310⟩

## 4. Recommendation

Three definitions as the project standard, used together, plus one diagnostic. All use Lean as the only judge and
three training seeds, and report per-seed sets with the redraw and seed floors beside them.

**A. Compute-matched reach, with each theorem's k-to-solve interval** (`passk-budget` + `marginal-bracket`: Dan's (b)
made strict, with his (a) as the estimator).
- *Protocol:*
  1. RL model: plain reads (T 0.8, 96 steps, 512 tokens per action), k 256 on two sample seeds. "Solves" = ≥ 1
     Lean-accepted proof on the defining draw; the other draw gives the redraw floor.
  2. Base: the same protocol, 512 attempts per evaluation theorem. On every theorem RL solves and the base fails, add
     attempts until n ≥ K_eval-set = (ladder GPU-seconds) / (N_eval × measured seconds per base attempt). Here: 16,384,
     then 49,152 more where the first 16,384 found nothing.
  3. Known-proof estimate: teacher-force the base (T 0.8) on every accepted proof of t that any model found, including
     the base's own large-k proofs; 33 name bases for each checkpoint's top 20 proofs per theorem, the one-base bound
     (−ln 33) for the rest.
  4. Per theorem, print the **k-to-solve interval** [1 / UB95, 1 / estimate]. Verdict at K: **elicited** if p̂ ≥ 1 / K or
     the estimate is ≥ 2 / K; **not reached** if 0 successes in ≥ K attempts; **created (certified)** only if
     UB95 < 0.05 / K (≈ 60 K zero-success attempts, bought for headline theorems only); otherwise undetermined.
  5. Set level (the headline): Δ_cov = #{RL solves at 256} − #{base within reach at K_eval-set}, and the candidate
     created set **net of both RL-free controls** (the replay-only ladder; a pretraining continuation matched to the
     ladder's GPU time) and of other seeds' bases.
- *What counts as created:* a non-empty net set on ≥ 2 / 3 seeds, larger than the redraw floor, with its theorems
  certified if a headline rests on them.
- *Cost here:* ≈ ⟨⟩ A40-hours per seed (J1 + J2), about ⟨⟩ % of the r8 ladder.
- *What existing results show:* ⟨A-FOUND⟩

**B. Capability vs propensity** (`capability-vs-propensity`: the reporting format for every evaluation).
- *Protocol:* per model and theorem set, two numbers:
  - **propensity** = plain pass@1 (mean over theorems, k 256 reads);
  - **capability** = solved within the budget by the best *per-theorem* method: plain sampling up to K_eval-set, and
    guided reads (`guided_eval.py --arm logical`, k 256, T 0.8, max_rej 10).
  Nothing trained on verifier verdicts for other theorems counts as a per-theorem method.
- *What counts as created:* RL raises capability, not just propensity. Where it raises only propensity, it "converted
  capability into propensity" (elicited).
- *What existing results show:* ⟨B-FOUND⟩

**C. Key-step family acquisition, with a teachability test** (`schema-acquisition` + `elicit-finetune`).
- *Protocol:*
  - A family is a generator schema restricted to members that need its key step (classical families: members not
    provable by the G4ip decision procedure, `intuit.py`). Rates on held-out members: base within the budget, RL at
    k 256.
  - **Created at family level:** base ≤ 0.05 and RL ≥ 0.5 on held-out key-step members, on the seed in question; a
    recipe-level claim needs ≥ 2 / 3 seeds.
  - **Teachability:** fine-tune the base and a knockout pretrained without the key step on 16 demonstrations (control:
    16 length-matched non-family proofs; replay drawn from the knockout's corpus; two fine-tune seeds). **Latent** if
    the base's gain exceeds the knockout's by ≥ 0.3 (held-out pass@256) on ≥ 2 / 3 seeds; **teachable** if within 0.2.
- *What existing results show:* ⟨C-FOUND⟩

**D. Diagnostic: IRT ability with an ability-matched placebo** (`irt-ability`, with `compute-equivalent`).
- *Protocol:* fit a 2PL item-response model on the pretraining checkpoints (calibration through a fixed checkpoint),
  place RL and RL-free models on the same θ scale, and count items with DIF+ (success far above what θ predicts). RL is
  "off the pretraining axis" only if its DIF+ rate exceeds that of RL-free models at the same Δθ.
- *What existing results show:* ⟨D-FOUND⟩

**Dan's two notions, as we recommend using them.**
- **(a) Teacher-forced probability.** Use it as an *estimator* of the base's p, summed over every known accepted proof,
  never on RL's own proof alone (padding). It recovers 0.93–0.98 of the measured p (median), so it extends sampling
  to probabilities far below 1 / n cheaply: one forward pass per proof instead of 1 / p samples.
- **(b) pass@k at large k.** Replace "large k" by K_eval-set and report k-to-solve intervals. Extrapolate only at the set
  level: a beta-binomial fitted to ≈ 768 attempts per theorem predicted the number of hard theorems the base solves in
  16,384 attempts within 0–13 % on every seed (§3.9, Q16); per theorem, no unbiased estimate exists beyond the n
  sampled.

## 5. Glossary

- **Theorem t; Lean accepts.** One propositional sequent, e.g. ⊢ A ∨ ¬A. A proof counts iff Lean 4 checks it; nothing
  else judges.
- **Attempt.** One sample from the model, run to the end in the proof-state environment (T 0.8, the read caps).
- **Solve probability p.** The chance that one attempt proves t. Every other number here is a view of it.
- **pass@k.** The chance of at least one proof in k attempts: 1 − (1 − p)^k.
- **k-to-solve.** 1 / p, the expected number of attempts to the first proof ("the base needs ≈ 3,000 attempts").
- **Budget K.** How many attempts we allow before saying "cannot". **K_eval-set** (the headline): RL's GPU time spent
  instead on base attempts over the 322 evaluation theorems, ≈ 2 × 10⁴ each at r8. K_per: per training target
  (≈ 10³). K_total: all RL compute on one theorem (3–4 × 10⁶).
- **Within reach at K.** p ≥ 1 / K: at least a 63 % chance of a proof in K attempts.
- **base / pend; r8 / r16.** The model at the end of pretraining; the same model after 8 / 16 rounds of expert
  iteration (sample, keep what Lean accepts, fine-tune).
- **Hard theorem.** One the base failed in 512 attempts.
- **Replay-only control.** The same 8 fine-tune rounds as RL, on pretraining data only: no RL proofs, no verifier.
- **Compute-matched continuation (J7).** The base pretrained further for as long as the r8 ladder ran.
- **Created (at K).** RL solves t, the base is not within reach at K, and RL-free training does not solve t either.
  *Not reached:* 0 base successes in ≥ K attempts (cheap). *Certified:* 0 in ≈ 60 K attempts, so the base's chance
  of solving t within K is below 5 % at 95 % confidence (expensive).
- **Elicited.** RL solves t and the base is within reach: it found a proof often enough, or its known-proof estimate
  is ≥ 2 / K. RL made a reachable thing reliable.
- **Undetermined.** The evidence does not place the base on either side of the budget.
- **Propensity vs capability.** What the model does by default (plain pass@1) vs what it can do with the best
  per-theorem method within a budget (more samples, step-checked redraws, renamings).
- **Teacher-forced probability π(y).** The model's probability of writing one specific proof y, computed by feeding y
  through the model.
- **Known-proof estimate.** π_base(y) summed over every accepted proof of t that any model ever found. It recovers
  0.93–0.98 of the base's measured p (median), so it is an estimate of p, not just a bound; certificates use a
  factor-2 margin.
- **Key-step family.** Theorems sharing a proof pattern (e.g. all A ∨ ¬A), restricted to members that need the
  pattern's key step (here, members not provable intuitionistically).
- **Teachable vs latent.** A skill is *teachable* if a few demonstrations install it, also in a model pretrained without
  its key step; *latent* only if the base learns it markedly faster than that knockout.
- **IRT ability θ.** One score per checkpoint, fitted jointly with a difficulty per theorem; "more of the same" means
  RL's successes are predicted by its higher θ.
- **Placebo.** A comparison arm that gets the same kind of change without the ingredient in question (here: training
  without RL proofs). It sets the floor for "RL-specific".
- **Noise floors.** *Redraw:* the same model sampled again. *Seed:* another training run of the same recipe.
  Differences inside them are not findings.
- **Null model.** Random initialisation. Its k-to-solve on our hard theorems is e^290 to e^3,200 attempts (median
  ≈ e^850; J1), which answers "random weights eventually solve everything".

## 6. Open questions for Dan (each with my recommendation)

1. **Which budget defines "the base cannot"?**
   - *Options:* k_eval (256; the field's equal-k test); 1 % of pretraining compute per theorem (the safety-evaluation
     convention, ≈ 2–4 × 10³ attempts here); **K_eval-set** (RL's GPU time as base attempts over the evaluation set,
     ≈ 2 × 10⁴ at r8, ≈ 5 × 10⁴ at r16); K_total (all RL compute on one theorem, ≈ 4 × 10⁶).
   - *Recommendation:* K_eval-set for verdicts, and always print each theorem's k-to-solve interval so a reader can
     apply another budget. Never use k_eval as a creation test.
2. **Is the replay pretraining inside our RL part of "RL"?**
   - Each EI round also trains on 20,000 pretraining records (≈ 476 M tokens over 8 rounds, more than Stage 1). The
     replay-only control solves ⟨≈ a third⟩ of what equal-k calls RL-created.
   - *Recommendation:* report RL net of the replay-only control and of a compute-matched continuation. A claim about
     "RL" should be a claim about what the verifier signal added.
3. **Created relative to this seed's base, or to the pretraining recipe?**
   - The bases differ a lot: `textbook_245a0349` is 0 / 768 for s0's pend and 505 / 768 for s2's;
     `la_transfer_1382` is 0 / 17,152 for s0 and 26 / 768 for s1.
   - *Recommendation:* per-seed verdicts for mechanisms; a headline "RL creates X" should require that no seed's base
     reaches X within the budget.
4. **What is the unit of a capability: a theorem or a family?**
   - *Recommendation:* key-step families (members that need the key step) for any creation headline. Theorem-level
     verdicts agree across seeds only at Jaccard ⟨0.2–0.4⟩, and one theorem can be one lucky route.
5. **What counts as an elicitation method?**
   - *Recommendation:* per-theorem methods only: more samples, any temperature, guided step-checked redraws, prior-only
     search, renamings. Anything that learns from verifier verdicts on *other* theorems (fine-tuning, value heads) is
     RL's own mechanism; study it as teachability (how many demonstrations), not as the base's capability.
6. **If four demonstrations install a schema in the base, was it "latent"?**
   - *Recommendation:* call it **teachable**, and reserve **latent** for a base that learns it markedly faster than a
     model pretrained without the key step. On our data the knockout learns excluded middle ⟨as fast⟩ (J6b).
7. **How much certification to pay for?** Certifying "the base cannot within K" by sampling needs ≈ 60 K zero-success
   attempts: ≈ 1.2–1.4 M per theorem at K_eval-set, ≈ 1.3 A40-hours.
   - *Recommendation:* label the cheap verdict "not reached within budget" and certify only the few theorems a
     headline rests on (J9 did 9 for ≈ $⟨6⟩).
8. **The next experiment for "can RL create?"** Only an intervention on pretraining can show creation in the strong
   sense.
   - *Recommendation:* ablate a *composition* (DN applied to a negation-introduction line, 16,703 records), not a
     primitive; pretrain three seeds without it, run 16 EI rounds from each, and read out the key-step excluded-middle
     family on held-out members (≈ $26). Run it before moving to a richer domain.
9. **Reporting standard.** *Recommendation:* every RL result reports propensity (plain pass@1), capability within the
   budget (best per-theorem method), and the compute-matched reach table net of RL-free controls. Equal-k "group B"
   stays a descriptive label.
