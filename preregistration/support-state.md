# Pre-registration — run `support-state` (2026-09-28)

Written before any pod of this run exists. Brief: `support-state` (Dan, 2026-09-28), $10 / 20 pod-hours.
Lean alone decides (`lean_gate.gate` on the literal `lean_seq` text the environment assembles; `nd_verify` judges
nothing). `LEAN_GATE_DUMP` is set on every job.

## Question

`support-curves` found 29 transfer theorems (`data/sc/falsifier_survivors.txt`) that the whole-proof base
`ckpts/lf/stage1_a1_seq_s0.pt` (3,214,336 params, `lean_seq`, from scratch, `train_depth3_f0_a1`, md5 `9bde44c0…`)
never solves in 400,000 attempts (200,000 at T 0.8 + 200,000 at T 1.0; p < 7.5 × 10⁻⁶), which its EI descendant solves
at p̂ 0.022–0.9995. **Does a base that sees the proof state reach them?** If yes, the "new move" was one the
whole-proof model could not track its way to, and the expansion is about state, not capability. If not, the
expansion survives a much stronger base.

## Models (all 3,216,384 params, `lean_staten`, from scratch, 6,000 × 128 on `data/p2/train_depth3_f0_a1.jsonl`, cap 6)

- **SN base s0 / s1**: `state-env`'s SN-v2 Stage-1 `ckpts/se/stage1_SN_s{0,1}.pt` (bucket `state-env/ckpts/se/`).
- **SN EI s0 / s1**: `ckpts/se/ladder/la_T1_SN_s{0,1}_r8.pt` (8 rounds × k 32 EI at T 0.8 on `rl_targets`, disjoint
  from the transfer pool).
- Sampled in the environment: `Env(canon=True, assign=True)` (the environment names what a step introduces),
  `--max_action 256 --max_steps 48`, the state-env settings. md5s are recorded on every record.
- The whole-proof numbers are **not re-run**: they are `support-curves`' on-file records (measured under Lean alone,
  2026-09-27, so no checker label is needed), carried with their model labels.

## What I already know (seen before writing this)

`state-env`'s frozen ladders (`artifacts/se/la_frozen_SN_s{0,1}/found_transfer_8.jsonl`, 8 rounds × k 32 = 256
attempts per transfer theorem at T 0.8, no training) already solve **21 / 29** survivors (SN base s0) and **18 / 29**
(s1); the SN T1 ladders solve 28 / 29 and 29 / 29. So the brief's falsifier very likely fires; the run's value is
the depth (does anything stay out of reach at 200,000?), the per-theorem probabilities, and whether EI expands the
*state* base's support too.

## Design (what will actually run)

Sampler `ss_support.py` (this run; `support.py`'s protocol and record format, sampling through
`state_sample.env_generate`). Batch 4,096 per job unless the first job's peak memory says otherwise (recorded).

- **H (headline).** The 29 survivors, SN base s0: up to 200,000 attempts at T 0.8, then — for every theorem not yet at
  5 successes — up to 200,000 at T 1.0; a theorem stops at 5 successes (batch boundary). Then the same on SN base
  s1. *Reached* = ≥ 1 Lean-accepted attempt at either temperature.
- **S1.** All 383 theorems (`data/sc/theorems.jsonl`, md5 `3cb6e7bf…`), SN base s0 and SN EI s0, k = 10,000,
  stop at 50, T 0.8 — `support-curves`' stage 1.
- **S2.** SN forward crux (SN base 0 / 10,000, SN EI ≥ 1): SN base to 40,000 at T 0.8 and 40,000 at T 1.0
  (`support-curves`' pre-registered depth); theorems still at 0 get deepened to 200,000 per temperature if budget
  remains. SN reverse crux (SN EI 0, SN base ≥ 1): SN EI up to +20,000 at T 0.8.
- **Scatter.** Per-theorem p̂_base vs p̂_EI (T 0.8, 383 theorems) for SN, next to `support-curves`' whole-proof one.
- **Part 3.** For each survivor SN base s0 reaches: does its proof contain the step that was improbable in the
  whole-proof EI proof (`support-followups` part D's worst step)? Descriptive only.

## Expected results (falsifiable)

| id | quantity | expectation |
|---|---|---|
| E1 | survivors reached by SN base s0 within 200,000 / temperature | **28** (range 25–29) |
| E1-F | **brief's falsifier for "expansion survives a stronger base" / confirmer for "about state"**: SN base s0 reaches ≥ 15 of 29 | **fires** (P ≈ 0.97) |
| E2 | survivors SN base s0 reaches at T 0.8 within its first 10,000 attempts | 24–29 |
| E3 | median p̂ (T 0.8) of SN base s0 over the 29 (unreached count as 0) | ≥ 3 × 10⁻³ |
| E4 | survivors reached by SN base s1 | ≥ 24 |
| E5 | S1: SN base s0 solves / 383 at k 10,000 | 170–260 (whole-proof base: 45) |
| E6 | S1: SN EI s0 solves / 383 | 210–300 (whole-proof EI: 121) |
| E7 | SN forward crux size at k 10,000 | 15–60 (whole-proof: 82) |
| E8 | **SN support-expansion falsifier** (does EI expand the *state* base's support too?): SN forward-crux theorems with 0 SN base successes at 40,000 / temperature and SN EI p̂ ≥ 0.01 | **5–25; "EI expands the SN base's support" iff ≥ 5** |
| E9 | SN reverse crux size | 0–15 |
| E10 | Part 3: share of reached survivors whose SN-base proof contains whole-proof EI's worst-step line (up to renaming) | 30–80 % |
| E11 | Attempt-level length-cap hits (action truncated or step cap) in any reported stratum | < 0.1 % |

**Readings.** E1-F fires → the whole-proof survivors were a *tracking* limit: a model that sees the state reaches
them at ordinary sample sizes, so the whole-proof "support expansion" was EI teaching state-tracking, not a new
move. It does not fire → the expansion survives a 5–6× stronger base. E8 separately tests whether the state base
has its own EI-only theorems; if ≥ 5, the elicitation-vs-expansion question simply moves up a level.

**Noise.** The headline is a per-model reachability count against a bound (whole-proof p < 7.5 × 10⁻⁶); the
predicted effect (0 → ≈ 28 of 29) is far outside any seed-level spread on file (frozen SN 21 vs 18 of 29 across
seeds). No noise floor has been measured for this quantity; I run n = 2 Stage-1 seeds for H and report both. S1 /
S2 are n = 1 (seed 0), as `support-curves`' stage 1 was; the S1 counts are compared with the whole-proof ones only
where the gap exceeds `NOISE_FLOOR.md`'s frozen-count MDD scaled to 383 theorems (≈ 397 × 383/2,285 ≈ 67).

## Budget and stop rule

`podbudget support-state --set 20 10`. RunPod balance floor $100. Stop rule: at 17 pod-hours or $8.50, stop
launching; drop in this order: S2's 200,000 deepening, then H's s1, then the reverse crux. Pods deleted as their
outputs (artifacts + dumps) are pulled.
