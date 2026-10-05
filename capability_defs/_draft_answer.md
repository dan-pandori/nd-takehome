## 1. The plain answer (draft; numbers to be finalised from out/part3.txt)

**A capability is something a model can do at a stated cost.** For one theorem, everything is a view of one number: p, the
chance that a single attempt finds a Lean-accepted proof. Equivalently, the k-to-solve, 1/p, is the expected number of
attempts.

Dan's objection is right: random weights have p > 0. But their k-to-solve is ≈ e^1000, so they fail any budget anyone
could pay for. The budget has to be tied to something.

We recommend tying it to RL's own compute. RL created a capability on t only if:
- the RL model solves t;
- the base does not, even given RL's GPU time as extra attempts (≈ 2 × 10⁴ per evaluation theorem here);
- training without RL proofs does not get there either.

On our cap-12 models, about half of RL's new solves disappear under that rule. RL is best described as amortised search
plus more training. What remains is a few theorems per seed, and a few proof schemata picked up by single seeds
(excluded middle on one seed, Peirce's law on another). Those schemata are new combinations of steps the base already
takes, and four demonstrations teach the base the same schema.

## 4. Recommendation (draft)

Four definitions, each with an exact protocol, used together:

**A. Compute-matched reach (per theorem and set level; Dan's (b) made strict).**
- *Protocol:*
  - RL model: plain sampling, T 0.8, read caps (96 steps, 512 tokens per action), k 256 on each of two sample seeds;
    "solves" = ≥ 1 Lean-accepted proof.
  - Base: the same protocol, up to K_eval-set = (RL GPU-seconds) / (N_eval × measured seconds per base attempt) on
    every evaluation theorem it fails at 512.
  - Per theorem, report the base's **k-to-solve interval [1 / UB95, 1 / LB]**, where UB95 is Clopper–Pearson over all
    base attempts and LB is the summed probability of every known proof (33 name bases for the leading proofs).
  - Verdicts:
    - **elicited** if the base finds a proof within K_eval-set, or LB ≥ 1 / K_eval-set;
    - **not reached** if it has 0 successes in ≥ K_eval-set attempts;
    - **created (certified)** only with ≥ 60 K_eval-set zero-success attempts, so reserve it for a few headline
      theorems.
  - All verdicts are net of a replay-only control (the same fine-tune rounds without RL proofs). Where affordable, also
    net of a compute-matched pretraining continuation.
  - Three seeds; per-seed sets plus IQM and stratified-bootstrap intervals.
- *What counts as created:* a positive set-level difference "RL solves at 256 − base solves within K_eval-set − what
  RL-free training solves", beyond the seed spread, on ≥ 2 / 3 seeds.
- *What we found:* [seed-0: 24 not-reached theorems at r8 (21 net of replay); s1 / s2 pending].

**B. Capability vs propensity (the reporting format for every evaluation).**
- Report two numbers per model and theorem set:
  - **propensity:** plain pass@1;
  - **capability:** the best *per-theorem* method within the budget, i.e. plain sampling at K and guided redraws at
    matched tokens. Nothing trained on other theorems' verdicts counts as a per-theorem method.
- RL "converted capability into propensity" where capability was already high.
- *Found:* [J3 pending].

**C. Key-step schema acquisition with a never-had-it control (family level).**
- Families are restricted to members that need the schema's key step (G4ip or a necessity check). Rates are taken on
  held-out members: base at the budget, RL at k 256.
- **Created at family level** if the base is ≈ 0 and RL ≥ ½.
- Then the teachability test: N demonstrations given to the base vs to a model pretrained without the key move.
  - Latent if the base learns much faster.
  - Teachable if both learn alike.
- *Found:* excluded middle (s1 only), Peirce (s2 only) and the classical members of `negated_conditional` (all seeds).
  Four excluded-middle demonstrations take pend s0 from 0 / 39 to 36 / 39 held-out instances, the same as s1's RL after
  16 rounds. [J6b pending: latent vs teachable].

**D. IRT ability with an ability-matched placebo (set level: "is RL more of the same?").**
- θ per checkpoint on a scale calibrated by pretraining.
- RL counts as "off-axis" only if its item-level gains exceed those of pretraining continuation or replay-only training
  at the same ability gain.
- *Found:* no RL-specific excess at matched Δθ. The original "26–30 vs 4–7" was unmatched.

**Dan's two notions, as we recommend using them.**
- (a) Teacher-forced probability: decide on the *base's best known proof* and on the known-proof sum, never on RL's own
  proof alone. The sum recovered 96 % of the base's measured p on calibration theorems, so it is practically an
  estimate of the solve probability, not just a bound.
- (b) pass@k at large k: replace "large k" by K_eval-set and report k-to-solve intervals. Extrapolate only at the set
  level: a beta-binomial fitted to ≈ 768 attempts predicted 23.8 of the 24 hard theorems the base solved at 16,384.
