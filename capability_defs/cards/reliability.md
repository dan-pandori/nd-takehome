# Card: reliability — a capability is what the model does reliably when it tries

Family R. Slug `reliability`. Notation: `_FRAME.md`.

## 1. Definition, formally

- **Per theorem.** θ *has the capability* to prove t iff p_θ(t) ≥ τ under a fair protocol (plain sampling, T 0.8, read
  caps), with τ = 1/2 by default (a coin-flip bar: "more often than not").
- **Per family** (a schema, a length bin, a renaming class): the share of members with p_θ ≥ τ, i.e. Cover@τ (Dragoi
  et al.), or the mean p_θ over members.
- **Across training seeds:** the share of seeds whose model meets the bar.
- **The conditional analysis behind it** (Harding & Sharadin): "a machine learning model has a capability to X just
  when it would reliably succeed at doing X if it 'tried'". "Tried" is operationalised as the outputs that are
  attempts at a proof of t (parsable, on-goal), under the best non-gerrymandered background conditions. This makes the
  decoder part of the model.

## 2. Decision rule

| verdict | rule |
|---|---|
| **created** | p_B(t) < τ_low = 0.05 and p_R(t) ≥ τ = 1/2: the base fails almost always, the RL model succeeds more often than not |
| **elicited** | — this definition does not separate an elicited capability from a created one. A move from p_B = 0.01 to p_R = 0.9 is "created" under it whether or not the base could reach t with 10³ attempts |
| **neither** | p_R < 1/2 |

Seed version: created on ≥ 2 of 3 seeds.

The rule is useful because it marks what changed in **default behaviour**, i.e. propensity. Paired with
`capability-vs-propensity`, it separates "RL converted a reachable capability into reliable behaviour" (elicitation)
from "RL made the reachable set larger" (creation).

## 3. Null or floor

- Reliability is the classical answer to the random-weights objection. A lucky success is not an ability: "A hopeless
  darts player may, once in a lifetime, hit the bull, but be unable to repeat the performance because he does not have
  the ability to hit the bull" (Kenny via SEP "Abilities", Sec. 4.3).
- Random weights never reach p ≥ 1/2 on any theorem, so under this definition they have no capability at all, at any
  k. No budget is needed: the threshold τ replaces it.

## 4. How to compute it here

- **Free.** p̂ from the k 256 reads, one draw to define and the other to check.
- **First numbers** (`out/defs_c12.txt`, cap 12, 322 theorems):
  - Created (p̂_pend < 0.05 and p̂_R ≥ 0.5) at r8: 71 / 62 / 60 (s0 / s1 / s2, draw x0). At r16 (x1): 75 / 80 / 61.
  - Redraw Jaccard 0.84–0.92 (the most stable of all definitions). Seed Jaccard 0.31–0.41.
  - Ratio to the equal-k set at r8: 1.31 / 1.22 / 1.00.
  - Jaccard with the equal-k set: 0.38. Reliability adds theorems the base solves rarely but at k 256; it drops
    theorems RL solves only rarely.

## 5. Sensitivity

- **τ and τ_low:** a two-threshold rule. Theorems near either threshold flip; report the (p_B, p_R) scatter, not just
  the count.
- **Temperature:** lowering T raises p for already-likely proofs. Reliability at T 0.8 is not greedy reliability.
  Greenblatt et al. use greedy correctness; ours is sampled.
- **Decoding:** a guided decoder raises reliability on long theorems (`guided-tts`). Under the conditional analysis the
  decoder belongs to the background conditions, so name it.
- **Representation and renaming:** p differs across renamings. The family version over a renaming class is more robust.
- **Noise:** binomial error at n = 256 is ≤ 0.03 on p around 1/2. The seed spread is far larger.

## 6. Failure modes

- **It cannot see latent capability.** A base with p = 0.04 that a trivial fine-tune lifts to 0.9 is "created" here.
  Greenblatt et al. show exactly this for password-locked models.
- **RL's sharpening counts as creation.** Raising p from 0.05 to 0.5 is the most common effect of RL in our data
  (B pass@1 0.001 → 0.56 at cap 12, `trajectory`).
- **Thresholds are conventions.** The SEP's reliability views leave "sufficiently high proportion" open.

## 7. Relations

- The propensity half of `capability-vs-propensity`.
- With τ = 1 / k_eval it becomes `passk-equal-k`.
- With families it is `schema-acquisition`'s and `transfer-invariance`'s reliability criterion.
- Disagreements with `passk-budget` mark sharpening (reliability says created, budget says elicited).

## 8. Literature anchor

- **Harding & Sharadin 2024 (2405.08989v1).**
  - Abstract: "a machine learning model has a capability to X just when it would reliably succeed at doing X if it
    'tried'".
  - Reliability as evidence (Sec. 3.1, Def. 5).
  - The conditional analysis CAMA (Sec. 4.1, Def. 10).
  - "we treat tokenizers, inference procedures, and other scaffolding for p_θ as part of the set of background
    conditions" (Sec. 2.3).
- **SEP "Abilities" (Maier & Kikkert 2025).**
  - The conditional analysis "(CA) S has the ability to A iff S would A if S tried to A" (Sec. 3.1).
  - Jaster's success view (Sec. 3.4).
  - Kenny's darts player (Sec. 4.3).
- **Dragoi et al. 2025, Cover@τ** (earlier review).
- **Greenblatt et al. 2024 (2405.19550v1):** greedy correctness as the metric (Sec. 4.2).
- All verified in `_claims_L2.md`.

## 9. Critic's verdict

*(pending)*
