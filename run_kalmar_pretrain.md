# run kalmar-pretrain — pretraining on Kalmár proofs (executor, 2026-10-19; UNREVIEWED)

**Question.** Does a proof-state model pretrained on Kalmár-construction proofs learn to run it, and generalise?

**Setup.**
- **Data.** Kalmár proofs of K12's 155,000 theorems (Lean 155,000 / 155,000). 109 actions per proof against 8; 27×
  the tokens.
- **Arms.** 9.56 M best recipe, `lean_staten`, 3 seeds each:
  - **KAL-D:** data-matched, 3.68 epochs.
  - **KAL-C:** compute-matched.
  - **Control:** best-cap12 Stage-1, trained on K12.
- Lean decides. Tables in `numbers.md` § kalmar-pretrain.

![](figures/kalmar_pretrain.png)

1. **Not learned (pre-registered criteria fail, 3 / 3 seeds).**
   - KAL-D's teacher-forced agreement on 1,200 held-out theorems is **94.5 %** (KAL-C 93.5 %, control 27.0 %).
   - Split, excluded-middle, ex-falso and closing steps are ≥ 96.6 %; premise lines 91.5 %; leaf steps 65–92 %.
   - KAL-D's greedy proofs: **32.6 %** Lean-valid, 14.7 % exactly Kalmár (4 atoms: 26.1 / 8.4 %). The control's:
     92.2 %.
2. **Mostly bookkeeping errors.**
   - Of KAL-D s2's 6,903 disagreements, 44.6 % write a formula of the problem that is not due next and 31.1 % one
     found nowhere in it.
   - Where checkable, 16.8 % assert something false in the branch.
3. **Solve rates.** KAL-D vs control, plain / guided pass@32, mean of 3:
   - holdout250 33 / 59 vs 165 / 198; rr600 17 / 66 vs 246 / 425; ≥ 17 lines 0.7 / 4 vs 13 / 40.
   - **Generalisation fails the pre-registered test** (ratio < 0.3: G1 supplied, G2, hand_proved_14, ≥ 17).
   - G3 classical is partial: guided 30 vs 16 of 106 clears the MDD (11.5); plain 18 vs 13 does not.
   - The control's 4–5-premise failures are its premise lines: once they are supplied it solves 177–191 / 200.
4. **EI ladder** from KAL-D s0 (4 rounds): LADDER_RESULT.

**Expectations vs outcomes.**
- Missed: every Kalmár-arm prediction (agreement, greedy, exact-follow, G1(b), G2, G3).
- Untested: KAL-D pass@256.
- Held: the control's predictions, "guided ≥ plain" and "KAL-C < control".
- The table is in `numbers.md`.

**Deviations.**
- KAL-D reads and the ladder at batch 1,024 (plain batch effect ≤ 6 theorems).
- No KAL-D k extension.
- Truncated actions > 0.1 %, not re-read at 2×.
- The learning curve (86.6 → 94.5 %) is confounded with the learning-rate schedule.

**Spend.** SPEND_TOTAL of $50.
