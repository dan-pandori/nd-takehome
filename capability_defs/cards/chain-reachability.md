# Card: chain reachability — creation as a chain of elicitations

Family S. Slug `chain-reachability`. Notation: `_FRAME.md`.

## 1. Definition, formally

- **One step of elicitation.** Model θ' is reachable from θ at budget k if every proof θ' learned was sampled from θ
  within k attempts. Expert iteration is exactly this: round r trains only on proofs that model r − 1 found in 32
  attempts.
- **Chain depth** d_s(t) of theorem t under ladder s: the first round whose sampler (model r − 1) solves t. Per round,
  the ladder logs give, for each target, its successes out of 32 (`alloc_r.json`); for held-out transfer theorems, the
  first-found round (`found_transfer_16.jsonl`).
- **Chain-created:**
  - t is outside the base's reach at the budget (p_B(t) < 0.05 / K_per, `passk-budget`);
  - yet t is reached after d ≥ 2 rounds, each of which elicited only what its predecessor could already sample at
    k 32.
- **"Elicitation is not transitive":** a chain of elicitations can end in a creation relative to its start.

## 2. Decision rule

| verdict | rule |
|---|---|
| **created (by chaining)** | t is first solved at round d ≥ 2 and is certified outside the base's reach at K_per. RL built it from steps the base could take, in an order the base would not take |
| **elicited** | d = 1 (pend solved t in round 1 at k 32), or p_B(t) ≥ 1 / K_per |
| **neither** | never solved |

**Relative verdicts.** Relative to the round-(d−1) model, every theorem is elicited. Relative to the base, chained
theorems can be created. Both statements are true; which one is "the" answer depends on the comparison Dan wants. The
card recommends **relative to the base, at matched compute**.

## 3. Null or floor

- The budget per round (k 32) and per target (K_per) are explicit.
- A ladder from random init never starts: `rl-from-ckpt`'s p0 ladder accepted 0 of 287,680 attempts, so chains need a
  first link.
- That is the answer to the random-weights objection in this frame: random weights have no first link at any feasible
  k.

## 4. How to compute it here

- Free from the ladder logs (`cd_schema.py` already parses them) and from J2 (the base's reach at K_per).
- First numbers (family level; `out/schema_c12.txt`). `dist_and_over_or`: 0 / 40 targets at round 1 (pend, k 32) on
  every seed, then 0.97 / 0.90 / 0.78 by r8. Excluded middle on s1 first appears at rounds 2, 10, 12 and then bursts at
  13–14.
- Per-theorem chain depths for holdout250 (⊂ transfer) are in Part 3.

## 5. Sensitivity

- **Per-round budget k:** a larger k makes chains shorter. A long chain at k 32 can be one step at k 10³.
- **Replay:** each round also pretrains on 20,000 K12 records, so links are not pure elicitation. The replay-only
  control (`rl-from-ckpt`) gives the size of that effect.
- **Decoding:** ladders sample plain at T 0.8 with the ladder caps (`max_action` 256 / `max_steps` 48), not the read
  caps.
- **Representation, renaming:** per ladder.
- **Seed:** chains are seed-specific (LEM on 1 of 3 seeds).

## 6. Failure modes

- **Transfer between targets.** A chain may reach t through generalisation from other targets, not through any sampled
  proof of t. This is still "created relative to the base", but not "a chain of elicitations of t".
- **"Created by chaining" depends on the base-reach certificate,** which has the `passk-budget` limits.
- **Not a property of R alone:** two ladders reaching the same model by different paths get the same R but different
  chains.

## 7. Relations

- Refines `passk-budget` (K_per vs per-round k).
- Explains `compute-equivalent`'s large RL multipliers: RL compute is spent at the frontier.
- The theoretical counterpart is the RL query barrier (below).

## 8. Literature anchor

- **Mousavi-Hosseini & Erdogdu 2026 (2603.06957):** outcome-reward RL needs about 1 / Q_q(ε) queries; the barrier is "a
  fundamental property of post-training with outcome rewards" (Sec. 5.1). Theorems solved with p_B ≪ 1 / queries are
  not explained by sharpening (L5 note).
- **Xie et al. 2024, XPO (2405.21046):** on-policy methods are stuck while coverage is low (Prop. 2.1).
- **Greenblatt et al. 2024 (2405.19550v1):** expert iteration "is able to pick up on a few lucky examples … and
  gradually bootstrap" (App. D.2).
- **Earlier reviews:** Go-Explore (return-then-explore), Abdulsalam et al. (iterated shifts reach 0 %-at-pass@1024
  buckets).
- **Project:** `rl-continue` (the excluded-middle burst at r13–14).

## 9. Critic's verdict

*(pending)*
