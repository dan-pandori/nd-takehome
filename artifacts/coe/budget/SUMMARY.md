# Phase 0.2 — the compute-matched budget, restated with measured same-class costs (old full seeds s0 / s1 / s2)

Models: best-cap12 (`state_env_october`): pend = `trajectory/ckpts/tj/stage1_best12_s{S}_b1200.pt`, r8 = trajectory's
T1 ladder round 8 (9.56 M ALiBiGPT, lean_staten, from scratch on K12; Lean alone). Sources: `artifacts/coe/budget/budget.json`
(`coe/coe_budget.py`), `recount.txt` / `recount_adapt.txt` (`coe/cd_part3_recount.py` = capability-defs' cd_part3 with only the
budget changed; it reproduces the published 22 / 21 / 14 at the published K), timing `artifacts/coe/timing/A40_pend_s*_b*.json`
(coe-r0, alone on the card), replica `artifacts/coe/replica/` + registry rows (coe-r1).

**Per-attempt cost.** pend on the 322 (textbook72 + holdout250), k 256, sampling + Lean, A40 alone: s0 7.22 / 7.20 / 7.92 ms
at batch 2,048 / 1,024 / 512; s1 8.04 / 7.80 / 8.75; s2 6.36 / 6.48 / – (capability-defs used 3.6 ms, one J2 chunk on hard
theorems; its own J2 averages on hard theorems are 4.19 / 5.12 / 4.43 ms). Batch 1,024 = 2,048 per attempt at half the
memory (13.6 vs 25.5 GB). **GPU class:** trajectory's round 1 (pend sampling the 4,495 rl_targets at k 32, batch 2,048,
same seeds) re-run on an A40 reproduced the same solved counts (3,676; 3,705) in sample-phase 1,283.6 / 1,218.2 s against
1,155.9 / 1,174.4 s on the RTX A6000: A6000 / A40 = 0.90 / 0.96 (mean 0.932). No A6000 was available to time directly.

| r8 budget (base attempts per theorem) | s0 | s1 | s2 | × published | compute-matched set (cm) |
|---|---|---|---|---|---|
| K_att = ladder target attempts / 322 | 3,574 | 3,574 | 3,574 | 0.15–0.19 | 34 / 33 / 33 |
| K_train, same class, uniform (sample + fine-tune phases) | 7,416 | 7,126 | 9,921 | 0.34–0.43 | 33 / 27 / 24 |
| K_eval-set, same class, uniform (all ladder seconds) | 10,314 | 10,141 | 14,150 | 0.48–0.61 | 28 / 26 / 24 |
| K_eval-set as published (A6000 seconds / 3.6 ms) | 19,281 | 21,107 | 23,310 | 1 | 22 / 21 / 14 |
| K_adapt (512 on all, rest on the 86 / 77 / 77 failed) | 44,570 | 43,427 | 56,509 | 2.1–2.4 | 21 / 20 / 14 |

r16: K_train 17,531 / 15,884 / 20,422; uniform K_eval-set 24,619 / 22,827 / 29,510; K_adapt 109,875 / 100,929 / 119,575.

**J9 certificates (UB95 < 0.05 / K, r8 budgets):** 7 / 9 at the published K, 8 / 9 at the same-class uniform K_eval-set
(s1 1077 now certified; s2 1648 not), 9 / 9 at K_train and K_att, **0 / 9 at K_adapt**.

**Reading.** The published budget sits between two defensible allocations that differ 4–6×. Under uniform allocation the
compute-matched sets are larger than published (28 / 26 / 24 at the same-class K_eval-set); under adaptive allocation they
are slightly smaller (21 / 20 / 14) and no certificate holds. The budget-robust core — RL r8 solves, the base 0 successes in
≥ 66,304 attempts — is 18 / 17 / 8 (ledger critic, from capability-defs' files). Pre-registered expectations: per-attempt
cost 6–8 ms on the 322 (hit: 6.4–8.0); A6000 0.8–1.2 × A40 (hit: 0.90–0.96); uniform K_eval-set 0.4–0.6 × published (hit on
s0, s1; s2 0.61: marginal miss); K_train 0.55–0.8 × same-class K_eval-set (hit: 0.70–0.72); K_train sets between the
published and the 0.3 × K sizes (hit: 33 / 27 / 24); J9 holds with more margin under uniform allocation and fails under
the adaptive one (hit).
