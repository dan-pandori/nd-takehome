# Pre-registration — state-cap12: proof state + cap-12 training proofs together

Run id `state-cap12`, executor, fork branch `dan_state-cap12` (from `origin/dan` at `3cb0a0f8`, which carries
`long-pool`'s pool). Written 2026-09-29 ≈ 02:35 UTC, before any pod. Checker: **Lean alone** (`lean_judge`).

## Question

`state-env`'s SN-v2 (proof state, environment-assigned names, cap-6 training set) and `cap-horizon`'s K12
(whole-proof `lean_seq`, cap-12 flat training set) each moved something. Trained together — SN-v2 on K12's
155,000 proofs — does the long-proof frontier move further than either lever alone, read on `long-pool`'s pool?

### What changed since the brief was written

`long-pool` re-read the comparators on `transfer_long_rr600.jsonl` (k 256, final checkpoints). SN-v2 cap-6 T1
already reads `L*` **≥ 17 / 15** there, i.e. at the pool's ceiling on seed 0. So the brief's falsifier ("T1 `L*`
on the long pool ≤ the larger of SN-v2-cap-6's and K12's on both seeds") **fires by construction**: nothing can
exceed a ceilinged `L*`. I report it as written, but it cannot discriminate. The primary quantity below replaces it.

## Design (what I will run)

Models: 4 layers, d 256, 8 heads, from scratch, `lean_staten` (≈ 3,216,384 params — reported from the checkpoint).

1. **Gates on K12** (`data/kh/train_k12.jsonl`, cap 12, flat 2–12, 155,000; bucket `cap-horizon/data/kh/`),
   canonical variant: gate 1 (round trip byte for byte, all 155,000), 1b (Lean on 3,000 reassembled texts),
   3 (environment replay, all 155,000), and gate 2 (Lean's state vs the renderer's) on 1,500 cuts of the ≥ 7-line
   proofs. Stop rule: any gate failure is fixed or explained before Stage-1.
2. **Stage-1 SN-cap12, 4 seeds (0–3)**: `state_train.py --mode lean_staten --cap 12 --steps 6000 --recs 128`.
   Four instead of the brief's two because the seed spread is the whole problem (SN-v2 cap 6 T1 Q = 102 vs 28 below).
3. **Held-out greedy** on `data/p2/heldout.jsonl` (5,000; comparable to SN-v2 cap 6's 0.970 / 0.958).
4. **T1 ladder**, 4 seeds: `state_ladder_ei.py` exactly as `state-env` (8 rounds × k 32, T 0.8, batch 2,048,
   `max_action` 256, `max_steps` 48, `rl_targets.jsonl`, in-loop transfer = original `transfer.jsonl`), replay set =
   K12. `LEAN_GATE_DUMP` set (literal text kept).
5. **Frozen**: instead of a `--no_train` ladder, a k = 256 re-read of each Stage-1 checkpoint (deviation, for cost:
   a frozen ladder samples each transfer theorem 8 × 32 = 256 times from the same model, so the transfer readout
   is the same estimator; the frozen ladder's target-side counts are not used in this question).
6. **Comparator K12 whole-proof T1** (its T1 checkpoints are not in the bucket): `ladder_ei.py` from
   `cap-horizon/ckpts/kh/stage1_k12_s{0,1}.pt`, replay `train_k12`, 8 × 32, batch 2,048, `max_new` 512, Lean alone.
7. **Long-pool readout**, identical to `long-pool` pass 2 (`lpool_reread.py`, k 256, T 0.8, seed 0; state batch
   2,048 / `max_action` 512 / `max_steps` 48; whole-proof batch 1,024 / `max_new` 1,536) on `transfer_long_rr600.jsonl`
   and `transfer_long_ge17.jsonl`, for: SN-cap12 T1 r8 (4 seeds), SN-cap12 Stage-1 (4), K12 T1 r8 (2).
   SN-v2 cap-6 T1/frozen, K12 frozen s0 and C0 come from `long-pool`'s files (`artifacts/sc12/lp_rr2/`).
   Original-pool frozen: the same re-read on `transfer.jsonl` (k 256).

## Primary quantity and the minimum detectable difference

**Q = generator theorems of `rr600` solved in bins `L_true` 13–16** (380 theorems: 90/90/100/100), final
checkpoint, k 256. Textbook theorems are excluded because every model solves ≈ none of them (`long-pool`). Values on
file: SN-v2 cap-6 T1 **102 / 28**; S cap-6 T1 29 / 28; K12 frozen s0 **38**; C0 T1 2 / 2.

No noise floor exists on this pool. Pooling the two state T1 pairs (S, SN-v2) gives sd ≈ 37. MDD (two-sample t,
80 % power, α 0.05): **≈ 199 at 2 vs 2**, **≈ 119 at 4 SN-cap12 seeds vs 2 comparator seeds**. So this run can only
detect compounding if SN-cap12's mean Q is ≳ 65 + 119 ≈ **185** (≈ half the stratum). A smaller gain is not a finding
at this n. Reported: per-seed values, IQM with stratified-bootstrap 95 % CI (n = 4 → the IQM is the mean of the
middle two).

## Expected results (numeric)

| quantity | SN-cap12 T1 | SN-cap12 frozen (Stage-1) | K12 T1 (whole-proof) |
|---|---|---|---|
| Q (gen 13–16, /380) | 60–200, mean ≈ 110 | 15–80 | 30–90 |
| rr600 total /600 | 150–350 | 50–200 | 90–220 |
| per-bin rate 13 / 14 / 15 / 16 | 20–50 / 20–45 / 12–40 / 8–35 % | 5–25 / 5–25 / 3–20 / 1–12 % | 10–25 / 10–25 / 8–20 / 2–10 % |
| ≥ 17 file solved /70 | 2–20 | 0–5 | 0–5 |
| `L*` rr600 | ≥ 17 on ≥ 2 of 4 seeds, ≥ 15 on all | 14–16 | 15–16 |
| original pool, solved /2,285 | 1,500–1,900 (in-loop cumulative) | 900–1,500 | 1,550–1,800 |
| original pool `L*` | 12–13; 2–8 thms at `L_true` ≥ 13 | 12 | 12 |

Held-out greedy (p2, 5,000): SN-cap12 ≥ 0.93 overall on every seed, spread < 4 pp. Gates: 0 failures.
Environment: 0.0 % step-cap hits, action-cap ≤ 0.01 %, whole-proof truncation reported per stratum.

Prior: 0.45 that SN-cap12's mean Q exceeds both comparators' means; 0.15 that it does so by more than the MDD.

## Falsifiers

- **Compounding refuted** if mean Q(SN-cap12 T1, 4 seeds) ≤ max(mean Q SN-v2-cap-6 T1 = 65, mean Q K12 T1).
- **Compounding supported** only if it exceeds both by more than the MDD (≈ 119); in between = "not resolved at n".
- Brief's falsifier (T1 `L*` rr600 ≤ max comparator `L*` on both seeds): reported; fires by construction (ceiling).
- Secondary: "the cap lever transfers to the state policy" is refuted if SN-cap12 frozen Q ≤ SN-v2 cap-6 frozen Q
  (3 / 0) + 10 on ≥ 3 of 4 seeds.

## Budget and stop rule

$20, ≤ 40 pod-hours (`podbudget state-cap12 --set 40 20`); RTX 3090 or A40 class (≈ $0.50/h), one ladder per
card. Estimated ≈ 25 pod-hours. Stop rule: at $15 spent, no new ladders; seeds 2–3 are dropped first (then the run
is n = 2 and says so). Balance floor $100.
