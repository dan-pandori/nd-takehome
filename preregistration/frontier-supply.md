# Pre-registration — run `frontier-supply` (proposal 16 item 1: new EI targets just past the frontier)

Written 2026-09-30 ≈ 02:05 UTC (committed bbeca3f5, 02:06), **before any pod exists for this run** (`podbudget frontier-supply`: 40 h / $20;
`~/pods.log` has no `fs-*` line at this commit). Executor: agent:claude. Branch `dan_frontier-supply` (from the fork's
`origin/dan`, d3abe474). Policy: `AGENT_POLICY.md` (nd-rl canonical). Lean alone decides throughout.

## Question

Expert iteration learns only where p̂ > 0. The fixed `rl_targets` pool (4,495) has 30 theorems above `L_true` 12 and
SN-cap12's cumulative `L*` on it is 12 (state-cap12 `la_T1_SN12_s0`, round 8), yet the same model solves 17–18-line
theorems (long-pool-2 re-read). Does **supplying new targets just past what the model can do** — built each round
from its own solves and failures, kept only if 32 attempts give p̂ ∈ (0, 1/4] (STP 2502.00212v4 §3.2) — move the
long-proof frontier more than spending the same attempts on the fixed pool?

## Model (every number below is on this model unless labelled)

SN-cap12: `lean_staten` state policy (proof-state observation, environment-assigned names), 3,216,384 parameters,
4 layers × d 256, from scratch, Stage-1 = `state_train.py --data data/kh/train_k12.jsonl --mode lean_staten
--steps 6000 --recs 128 --cap 12 --seed S` on K12 (cap-horizon's cap-12 set, 155 k proofs). s0–s3 from
`hf://buckets/dan-pandori/nd-rl/state-cap12/ckpts/sc12/`; **s4, s5 trained here with the identical recipe.**

## Design as I will run it

EI protocol = state-cap12's `sn_seed.sh` ladder: `state_ladder_ei.py`, 8 rounds, k 32, T 0.8, batch 2048,
`max_action` 256, `max_steps` 48, `ft_steps` 600 / round at lr 3e-4, `ft_recs` 128, retain 20,000 K12 records,
≤ 4 proofs per theorem × `rl_weight` 4.

| arm | seeds | what |
|---|---|---|
| **C** control | s0–s3 **reused**: state-cap12's `la_T1_SN12_s{0..3}` (same code path, same settings); s4, s5 new | `rl_targets`, k 32 uniform: 143,840 attempts / round |
| **S** supply | s0–s5 new | `rl_targets` at k 24 (+1 on 24 random targets) = 107,904, **plus** 1,123 candidates × 32 filter attempts = 35,936 → **143,840 / round** |
| **C′** control rerun | s0, s1 new | C with a different EI seed (`--ei_seed S+100`: sampling, mix shuffles, fine-tune seed); same Stage-1 checkpoint |

- **Split:** 25 % of each round's attempts go to supply. Filter attempts are the only supply attempts: the proofs a
  kept candidate's filter attempts found are its training proofs (≤ 4 × 4, as for any target); kept candidates and
  their proofs accumulate in the replay like `rl_targets` proofs. If fewer than 1,123 candidates can be made, the
  shortfall goes back to `rl_targets` as extra random attempts, so the total stays 143,840. Fine-tune steps: 600 in
  every arm and round.
- **Candidates** (rebuilt every round from the current model; half from each source, the other fills a shortfall):
  - (a) mutations of theorems solved **this round** (`rl_targets` and supply), using the shortest written proof as
    the upper bound `w`: *chain* (cut: a premise of T2 matched by substitution to T1's conclusion; ub w1+w2−1),
    *conj* (goal strengthened to G1 ∧ G2 over both premise sets; w1+w2+1), *contrapose* (Γ, A ⊢ G → Γ, ¬G ⊢ ¬A;
    w+3), *hyp layer* (Γ ⊢ G → Γ∖A ⊢ A → G; w+1), *case layer* (A replaced by A ∨ B and B → G; w+4). Kept only at
    upper bound ∈ [base+1, base+4]; `base` starts at the current `rl_targets` `L*` and moves +1 after a round in
    which more (a)-candidates had p̂ > 1/4 than p̂ = 0, −1 (never below `L*`) when > 75 % had p̂ = 0 (Lee et al.
    2502.01612 §7.1: too-hard targets hurt). Deviation from the brief's fixed `L*`+1…+4, because SN-cap12's
    `rl_targets` `L*` (12) is the pool's ceiling, not the model's.
  - (b) the focused open goal, under every hypothesis in scope, at the point where a **failed `rl_targets` attempt**
    ended in the environment (syntax / truncation / step cap; the state before the failing action), drawn first
    from targets with this-round p̂ ≤ 1/4. Attempts Lean rejected after finishing have no located failure point and
    are not used.
  - All: ≤ 8 premises, statement ≤ 300 state tokens, deduplicated by renaming class, never an `rl_targets` class
    already, never a class filtered before.
- **Leakage:** every candidate's renaming class (atoms by first appearance, premise order ignored) is checked against
  `transfer`, `transfer_long`, `transfer_long2`, `transfer_long2_calib`, `transfer_long_rr600`, `transfer_long_ge17`,
  both held-out sets, `validation_36` and `reserve`; matches are dropped and counted.
- **Per-round sampled transfer evaluation is skipped** in the new ladders (greedy transfer / held-out kept). It
  never touches training (own seed, keyed noise); it cost ≈ 1/3 of sampling. Deviation, for budget.
- **Read-out** of every final (r8) checkpoint **and every Stage-1 base (frozen reachability)**, all by me at one
  setting: `lpool_reread.py`, k 256, T 0.8, seed 0, batch 2048, `max_action` 512, `max_steps` 96, on
  `transfer_long2` + `transfer_long2_calib` (91: bins `L_lb` = 17 (61) and ≥ 18 (30)) and `transfer_long_rr600`
  `L_true` 13–16 (400).
- **Compute** per arm and round: GPU-seconds (and GPU type), generated tokens, attempts / actions, fine-tune steps
  and tokens, Lean checks, as `record.py` rows; reused C ladders derived from their round logs. If S's GPU-seconds
  exceed C's by > 25 % (same GPU type), I add a control given the extra attempts on 2 seeds.

## Quantities and statistics

- **Primary:** per-seed solves on the 91 long-pool-2 theorems (the two bins nearest the control's frontier: `L_lb`
  17 and ≥ 18; state-cap12 T1 solved 34 / 59 / 58 / 61, long-pool-2 LP2 table), S − C paired by seed.
- **Secondary:** rr600 13–16 solves (Q); `L*` on the read-out (expected to saturate at 18 for every final
  checkpoint — reported, not a decision quantity); filter pass rate overall and per source.
- **Statistics:** per-seed values; IQM of S − C with a stratified-bootstrap 95 % CI; paired MDD = (t₀.₉₇₅,₅ + t₀.₈,₅)
  · sd_d / √6 = 1.425 · sd_d. **Provisional sd_d = 12.8** (the between-seed sd of C's four values — conservative,
  since pairing removes the Stage-1 part) → **MDD ≈ 18 of 91**. Updated from the C vs C′ spread (sd_d ≈ √(mean d²)
  over the 2 pairs, each difference is a no-treatment S − C) once measured; I report both.

## Expected results (falsifiable)

1. **Filter:** ≥ 5 % of candidates pass p̂ ∈ (0, 1/4] (brief). My forecast: 10 % overall, (a) 12 %, (b) 6 %.
2. **Brief's hypothesis:** S − C on the primary > MDD. **My point forecast: +6 of 91 (80 % interval −6 … +18)**, i.e.
   inside the MDD — the supplied targets are a few hundred per ladder against ~4,000 solved `rl_targets`, and the
   model already solves at L 17–18 without them.
3. C vs C′ |difference| ≤ 12 per seed.
- **Falsifier:** < 5 % pass, or S − C inside the MDD.

## Budget and stop rules

$20, 40 pod-hours. 10 new ladders (6 S, 2 C, 2 C′), 2 Stage-1 seeds, ≈ 22 read-outs. Stop and debug if the first S
ladder keeps 0 candidates in rounds 1–2. At 80 % of budget: finish running ladders, drop C′ s1 before any S seed.
Priority if cut: S s0–s5 and C s4–s5 > C′ s0 > C′ s1.
