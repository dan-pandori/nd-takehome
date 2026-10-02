# Part B notes: nd-rl `origin/dan` experiment-summaries from 2026-09-21 to 2026-09-28 (21 dirs)

**Checker.** Before 09-27 the checker is Lean 4.34 ∧ `nd_verify` (lean-format through noise-floor). From 09-27 it is Lean alone (lean-judge onward). The exception is run4-grpo-review, which uses `nd_verify` only: counts made 09-17/18, 13,317/13,317 Lean-confirmed. lean-judge found 0 losses when it re-judged, and the Lean-only excess is 0.021 %. state-env measured that adding C0's Lean-only accepts changes its counts by +2/+1 (T1) and +7/+2 (frozen). So mixing the two checkers is ≈ harmless for counts, but rows are labelled. state-env, state-frontier and long-pool compare against C0 values that were measured under Lean ∧ nd_verify.

**Noise-floor MDDs** (n = 2 vs n = 2, control config 3.2M `lean_seq` cap 6, Lean ∧ nd_verify):
- Frozen-ladder transfer solved (of 2,285): ±397 (range 62–265 across null replicates, 4.27×).
- Frozen-ladder L*: ±1.9.
- Frozen RL-target solved (of 4,495): ±2,098.
- reductio_req pass@2000 (of 300): ±71.
- depth3_req required@8 (of 300): ±393.
- Held-out greedy:
  - Overall: ±16.3 pp.
  - 6-line bin: ±81.7 pp.
  - 2/3/4/5-line bins: ±1.7 / ±2.6 / ±8.1 / ±8.1 pp.
  - Depth-3 slice: not resolvable, because it is bimodal (P(high) = 0.462 [0.333, 0.595]).
- Other constants from the floor:
  - The n = 13 multiplier is 1.146·sd (the published 1.183 is wrong).
  - fast-stage1 uses MDD = 1.5064·sd at n = 8.
  - Pairing seeds across arms cuts the MDD by 13–17 % on the precise bins.
  - No floor exists for T1 ladders, state models, sc383 support counts or transfer_long.

**Same-checkpoint re-draw spread.** C0 s0 T1 on transfer2285 read 856 (ds-composition), 890 (ds-generator) and 923 (ds-rendering). So T1 re-runs alone move solved counts by about ±35.

**Pools are not interchangeable.**
- held-out: `data/heldout.jsonl` (lean-format and lean-seed2 full set) vs `data/p2/heldout.jsonl` (everything else). ckpt-avg uses only half B (2,500).
- Textbook: "textbook / 760" (19 schemata × 40) in state-env and ds-generator is **not** textbook72.
- L* on transfer2285 is censored at 14 (only 23 theorems at ≥ 13, 17 of them textbook). transfer_long rr600 is the replacement.
- K6 and K8flat in cap-horizon are copies of ds-composition C0 and A3 (duplicate rows).
- lean-judge describes the models as "~19 M"; every other summary says 3.2M.

**Not found in this part.** No textbook72, Robbie dev metric or holdout250 numbers: those read-outs start 09-29/30, so they belong to other parts. stage1-dynamics, fast-stage1 and run4-grpo-review report only means or ranges, with no per-seed values, so they have no metrics rows. ds-generator's textbook per-schema counts were not tabulated as totals.

**Per-theorem / per-run raw files**
- long-pool: `hf://buckets/dan-pandori/nd-rl/long-pool/artifacts/lpool` (re-read rows need a join to `data/lp`). The pool itself is on the fork `dan` (`470d39e0`).
- support-curves: `hf://buckets/dan-pandori/nd-rl/support-curves/artifacts/sc`.
- support-followups: `.../support-followups/artifacts/sf`.
- support-state: `.../support-state/artifacts/ss`, including the `dump/*.jsonl.gz` files.
- state-env: `.../state-env/artifacts/se`. The literal text is not stored.
- state-frontier: `.../state-frontier/artifacts/sf2/rs`, with dumps.
- ckpt-avg: `.../ckpt-avg/artifacts/ca`.
- Ladder runs: `.../<run>/artifacts/{lf,dsg,...}`.
- Fork branches: `dan_<run>` on `dan-pandori/nd-takehome`.

**Create vs elicit**
- **support-curves.** Claim: EI expands the base's support. Key numbers:
  - 29 theorems have 0 base successes in 4×10⁵ attempts, and EI solves them at p̂ 0.02–0.9995.
  - No pass@k crossover up to k = 10⁴.
  - Teacher-forced p ≤ 9.5e-8.

  Points to **creation** (relative to this base). Caveats: one 3.2M base, seed 0 only, and the counts sit inside the floor.
- **support-followups.** Claim: seed 1 replicates (29/29). Key numbers:
  - 10⁷ attempts drop 1 of the 6 longest survivors, via a non-EI route.
  - A 25M base reaches 0 and 2 of the 29, but it is a *weaker* prover (6-line 0.47 vs 0.69).

  Points to **creation, weakly**. The capacity test is invalid as a "stronger base" test, and the improbability is concentrated in 2–3 steps, which the controls show too.
- **support-state.** Claim: the SN base reaches 28 of the 29 survivors on each seed. Key numbers:
  - WP "expansion" was largely the interface (state + env naming, which are confounded).
  - EI still expands SN support: 30 theorems at 40k, 7 at 200k/temp, at `L_true` 7–11.

  Points to **elicitation for the WP survivors, with creation one level up**. Caveats: n = 1 on S1/S2, and the two base seeds differ 20× in p̂.
- **state-env / state-frontier.** Claims:
  - The state lifts base reachability: frozen 779–1,009 vs C0 114–158, above the MDD.
  - The state passes `L_true` ≥ 13 at 2.12 %, on 4 theorems.
  - 3 of those 4 theorems are reached by no state base (10×256) and no frozen ladder.

  Points to mostly **elicitation/amplification**. The ≥ 13 hits are weak **creation**: at k = 256 only, concentrated (91 % on 2 theorems), and not significant vs C0 (p = 0.0625).
- **long-pool.** Claim: cap-12/14 Stage-1 with no RL (88/118 of 600) beats every T1 model except SN-v2 s0 (179, while s1 gets 68). Points to **pretraining > RL for length**. Caveats: one sampling seed, and K12/K14 have n = 1.
- **cap-horizon.** Claim: a higher cap elicits longer writing (padding), not harder targets; T1 L* = 12 for every cap. Points to **elicitation**.
- **lean-format / lean-seed2.** Claim: the token-format "RL crosses depth-3 f = 0" was partly a surface barrier. In `lean_seq` the frozen base writes depth-3 proofs for 13–28 % of targets, and RL adds +1 L* bin (10 → 11), equal to or smaller than the token format's gain. Points to **amplification**.
- **run4-grpo-review.** Claim: GRPO ignited depth-3 in 12/12 arms on 2 draws with 0 in 8.56×10⁵ samples, while EI ignited in 1 of 3. Points to **creation**. Caveats:
  - The pattern is ≈ 70 % a vacuous box-nesting habit.
  - Token format, `nd_verify`.
  - The checkpoints are lost, so it cannot be re-measured.
- **ds-generator.** G2 is a counter-example to "RL amplifies base": lower frozen rate but larger EI − frozen on both seeds. Direction **unclear**, and it is within the floor.
- **ckpt-avg / stage1-dynamics.** The depth-3 "mode" is checkpoint oscillation and real capability (pass@8 moves too), so it is not decoding. This bears on how Stage-1 base rates should be read (point estimates are noisy). Direction **unclear**.
