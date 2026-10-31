---
written_on: 2026-10-31
written_by: agent:claude (executor, run coe-dose01)
---

# Pre-registration — coe-dose01: how much RL brings σ back when pretraining holds only 0.1 % of it?

Written 2026-10-31 20:25 UTC, before the first pod. Brief: run brief `coe-dose01` (Dan, 2026-10-31, proposal 33).
Policy: `AGENT_POLICY.md`. Branch `dan_coe-dose01` (from the fork's `dan_create-or-elicit`).

## Question

The midterm figure (nd-rl `docs/writeups/2026-10-31-rl-needed-to-reproduce-sigma/`) plots, per ladder, the strict
σ-covered held-out members solved (y, of 106) against cumulative RL ÷ pretraining FLOPs (x). The bar is the full-exposure
bases' median before any RL update, **14 of 106**. Full exposure needs no RL; the 1 % σ dose reaches the bar at
0.39–0.73× (rounds 2–3, 3 of 3 seeds); the knockout does not reach it by 5.6–9.5× (0 of 6). Two doses and a lower bound
cannot tell a threshold from a smooth curve. **Where does a 0.1 % σ dose fall?**

## Models (every number below names these)

- **New (priority 1):** three bases `ckpts/coe/stage1_dose01_s{0,1,2}.pt` and their ladders `la_dose01_s{0,1,2}`:
  `best_model.ALiBiGPT` 6 × 384, 9,560,832 params (to be confirmed from the checkpoints), `lean_staten` (proof-state
  format, environment-assigned names), from scratch on **K12^0.1%** = `data/coe/train_k12dose01.jsonl.gz` (K12⁻ with 155
  refill records replaced by 155 removed σ records, 0.1 %; report `data/coe/train_k12dose01_report.json`).
- **Inherited (create-or-elicit, same architecture and format):** full s0–s5 (K12, σ in 10.9 %), dose1 s0–s2 (K12^1%),
  knockout s0–s5 (K12⁻). Their numbers are quoted from `artifacts/coe/rounds/*.json` and `rl_needed/rl_curve.json`.
- **Priority 2:** knockout s1 (`stage1_ko_s1.pt`, K12⁻) continued from create-or-elicit's `la_ko_s1_r24.pt`.

## Design (what will actually run)

**Priority 1 — the 0.1 % arm, seeds s0–s2, one A40 (SECURE) pod per seed, the 1 % arm's protocol with only the
pretraining set changed** (`pod/d01/seed.sh` = `pod/coe/seed2.sh` with `ARM=dose01`; code tree unchanged since the 1 %
arm's launch commit `dd6035e1` except `coe/` analysis scripts, `review_coe/`, data additions):
1. Stage 1: `state_train.py --recipe best --mode lean_staten --cap 12 --budget_secs 1200` on K12^0.1%, seed S, on an A40.
2. Held-out greedy on `data/p2/heldout.jsonl` (5,000).
3. T1 EI, 16 rounds (`state_ladder_ei.py`, defaults as in `la_dose1_s*/args.json`): the 4,495 targets at k 32,
   T 0.8, batch 1,024; 600 fine-tune steps per round (lr 3e-4, 128 records per step), mix = up to 4 accepted proofs per
   target × weight 4 + **20,000 replay records per round from K12^0.1%**; Lean alone (`lean_gate`); per round, k 32
   samples + greedy on the 832 tracked transfer theorems (`transfer_track832.jsonl`, which hold the 106 strict members)
   and greedy on `heldout1000`. Ladder seed = S, as in every other arm.
4. Reads (k 256, T 0.8, batch 512 on `read1054`): base plain x0 and guided g0 beside the ladder (the 1 % arm had both);
   the **r16 plain x0** read after it. The r16 guided g0 read runs only if the budget allows (below); the 1 % arm has no
   r16 guided read, so it would be compared with the full / knockout arms only.
5. `coe/coe_rounds.py` on the pod → `artifacts/coe/rounds/la_dose01_s{S}.json` (the format of `la_dose1_s*`), plus
   `coe/d01_heldout_proofs.py` → every accepted proof of a strict held-out member, for the reviewer's Lean check.
6. Not run (they served create-or-elicit's other questions): the base's x1 redraw and r8 reads, the timing read,
   standard A, the along-the-ladder scoring of known σ proofs.

**Priority 2 — knockout s1 rounds 25–32** (only if ≥ $10 remains after priority 1; rule below). create-or-elicit's
Addendum 6 procedure: `state_ladder_ei.py --resume --start_round 25 --rounds 8`, every setting unchanged (replay from
K12⁻), from the r24 files in the bucket (`create-or-elicit/artifacts/coe/ladder/la_ko_s1/found_24*`, `alloc_24.json`,
`ckpts/coe/ladder/la_ko_s1_r24.pt` — present, checked 20:15 UTC); then the plain r32 read on `read1054` and
`coe_rounds.py` through r32 → `artifacts/coe/rounds/la_ko_s1_r32.json` (create-or-elicit's files are not modified).

**The figure** (`rl_needed/`): copy `extract_rl_curve.py` and `make_figure.py`; first re-run the copy unchanged and check
that it reproduces the published `rl_curve.json` for all 15 existing ladders (every x and y per round; and the README's
totals, e.g. knockout s1 9.78×, dose1 s0 5.97×) with `review_rcs/ourruns.py`'s definitions; then add `la_dose01_s*`
(arm `dose01`, registry `coe-dose01`) and, if run, knockout s1 r25–32. x = cumulative RL compute after round r's sampling
÷ Stage-1 compute (sampling 2N per decoded and re-read state token; fine-tune 6N per trained token incl. replay;
Stage 1 6N·D). y = `heldout_cum_by_round` summed over families (a member counts once any round's k 32 sample solves it).
Crossing = first round with y ≥ 14; its x is "the RL ÷ pretraining compute needed".

## Expected results (numeric, falsifiable)

Per seed, s0–s2 are exchangeable a priori, so each gets the same prediction. y as defined above, of 106.

| quantity | prediction per 0.1 % seed | reference (inherited) |
|---|---|---|
| y at r1 (base's own k 32 sample) | **0–3** (point 1) | 1 %: 3 / 13 / 2; knockout 0 × 6; full 2–19 |
| free positive reductio proofs in round 1 (`sigma_subtypes` pos_free*, all targets) | **3–100** (point 25); ≥ 1 on ≥ 2 / 3 seeds | 1 %: 170–219; knockout 0 × 6 (first at r2–r15 on 5 / 6 seeds, s0 never) |
| y at r16 | point **18**, 80 % interval **3–45** | 1 %: 58 / 34 / 30; knockout 0–3 |
| first round with y ≥ 14 | point **r6 (x ≈ 1.8×)**; 80 % interval r3 (≈ 0.7×) to "not reached by r16 (≈ 6×)"; P(reached by r16) = 0.6 | 1 %: r2 / r2 / r3 (0.39 / 0.41 / 0.73×) |
| r16 plain read (k 256): strict held-out solved | point 22, 80 % interval 3–50; ≥ 1 family acquired (≥ 50 % of its strict members) on 2 / 3 seeds, contraposition_conv most likely | 1 %: 58 / 39 / 30, 3 / 3 |
| base plain read (k 256): families acquired | 0 on ≥ 2 / 3 seeds | 1 %: 1 / 3 (s1, contraposition_conv) |
| held-out greedy (p2, 5,000) | 0.91–0.95 | 1 %: 0.917 / 0.945 / 0.929 |
| RL ÷ pretraining FLOPs at r16 (after r16's sampling; incl. last fine-tune) | 5.6–6.1× (5.9–6.4×) | 1 %: 5.73–5.95× (5.97–6.21×) |

Arm level: **2 of 3 seeds reach 14 by r16** (P(0 / 3) ≈ 0.15, P(3 / 3) ≈ 0.3), with the crossing seeds' median x between
1.0× and 3.0×.

**Priority 2, knockout s1 at r32:** y point **7**, 80 % interval 5–12; **P(y ≥ 14 by r32) = 0.1**; r32 plain read (k 256)
point 7 of 106 (80 % interval 5–14); x at r32 ≈ 13× (+≈ 0.45× per round from 9.52× at r24); free positive reductio
proofs per round at r32 150–500 (r24: 123).

## Reading rules (decided on y, by r16, before any result)

- **Threshold — "0.1 % behaves like the knockout":** 0 / 3 seeds reach 14 by r16 **and** every seed's r16 y ≤ 5 (the
  knockout range through r24). Then the RL needed falls from ≤ 0.73× (1 %) to > 6× somewhere between 0.1 % and 1 %.
  (My probability 0.15.)
- **Graded — "crosses, but later than the 1 % arm":** ≥ 2 / 3 seeds reach 14 by r16 **and** the crossing seeds' median x
  is above 0.73× (later than every 1 % seed). (0.5.)
- **No resolvable dose effect between 0.1 % and 1 %:** ≥ 2 / 3 seeds reach 14 at x ≤ 0.73× (by r3). Any threshold would
  then lie below 0.1 %. (0.1.)
- **Intermediate** (anything else: 1 / 3 crossing, or 0 / 3 crossing with some r16 y of 6–13): reported per seed as a
  partial response, above the knockout in level, with no threshold-vs-graded verdict at 3 seeds. (0.25.)

## Statistics and the noise floor (n = 3 per dose arm, fixed by the brief and the budget)

- Per seed values throughout, plus the IQM (at n = 3, the mean) with a stratified-bootstrap 95 % interval.
- **Crossing indicator by r16**, one-sided Boschloo (columns = arms): 0.1 % vs knockout (0 / 6): 3 / 3 → p = 0.0033,
  2 / 3 → 0.034, 1 / 3 → 0.17. 0.1 % vs 1 % (3 / 3): 0 / 3 → p = 0.016, 1 / 3 → 0.11, 2 / 3 → 0.34.
- **r16 y, exact one-sided Mann–Whitney:** the smallest attainable p is 0.012 against the knockout (3 vs 6) and 0.05
  against the 1 % arm (3 vs 3).
- **Minimum detectable difference** for r16 y (two-sided t, α 0.05, power 0.8, the 1 % arm's seed SD 15.1): ≈ 46 members
  against the 1 % arm (n 3 / 3) and ≈ 47 against the knockout (Welch, df ≈ 2). My predicted 0.1 %-vs-1 % difference
  (≈ 20) is **inside** it, so no level difference against the 1 % arm will be called a finding; the arm-level reading
  rests on the crossing indicator (resolvable against the knockout at 2–3 / 3) and on per-seed crossing compute, which
  is reported descriptively. Redesigning with more seeds does not fit $45 with priority 2 (≈ $10 per seed).
- Caveat written in advance: replay carries σ at the arm's own rate (≈ 20 σ records per round at 0.1 %, ≈ 200 at 1 %,
  0 in the knockout), so part of any recovery may be the replayed exposure, not RL on the model's own proofs.

## Compute (recorded per arm and round)

Registry rows (`record.py`, ND_RUN_ID `coe-dose01`): GPU-seconds (A40), generated tokens, attempts, training steps and
tokens, Lean checks, per phase and round. Arms are matched on protocol: 143,840 target attempts and 600 fine-tune steps ×
128 records per round, the same per-round reads. Expected: every per-ladder quantity within 0.95–1.05× of the 1 % arm's
mean; any above 1.25× is flagged.

## Budget and stop rule

- **$45 binding, 90 pod-hours advisory** (`podbudget coe-dose01` already set to 90 h / $45). RunPod balance $244.10
  (floor $35).
- Projection, A40 SECURE ≈ $0.59/h (the rate RunPod reports at creation is recorded): priority 1 ≈ 3 × 17.5 h ≈ 52 h ≈
  **$31**; priority 2 ≈ 11 h ≈ **$6.5**; the three r16 guided reads ≈ 2–3.5 h each ≈ $4–6.
- **Priority 2 starts only when priority 1's projection from measured round times (after ≥ 2 rounds on every seed) is
  ≤ $35**, i.e. ≥ $10 remains. The r16 guided reads run only if priorities 1 + 2 are projected at ≤ $39.
- Ladders run all 16 (priority 2: 8) rounds; no early stop on results. A dead ladder pod is resumed on a new A40 from its
  last 4-round backup in the bucket (`pod/d01/backup.sh`); if that would break $45, priority 2 is dropped first.
- Pods are deleted once their files are pulled. Hard stop 72 h after the start (2026-11-03 20:13 UTC).
