# run kalmar-pretrain — pretraining on Kalmár proofs (executor, 2026-10-20; UNREVIEWED)

**Question.** Does a proof-state model pretrained on Kalmár-construction proofs learn to run it, and generalise?

**Setup.**
- Data: Kalmár proofs of K12's 155,000 theorems (all Lean-accepted), 109 actions per proof against 8.
- Model: 9.56 M best recipe, `lean_staten`, 3 seeds.
- Arms: **KAL-D** (data-matched, 3.68 epochs); KAL-C (compute-matched); **control** (K12).
- Lean decides; tables: `numbers.md` § kalmar-pretrain.

![](figures/kalmar_pretrain.png)

1. **Pre-registered: not learned; no generalisation, except partially on G3.**
   - Teacher-forced agreement: KAL-D 94.5 % (control 27.0 %).
   - Greedy proofs: KAL-D 32.6 % Lean-valid, 14.7 % exactly Kalmár; control 92.2 % valid.
   - Plain pass@32: holdout250 33 vs 165; rr600 17 vs 246.
   - Errors were mostly bookkeeping (76 % wrong or corrupted formulas).
2. **Exploratory (Addendum 3): a short fine-tune closes most of the gap.**
   - KAL-D+A = KAL-D plus the ladder's fine-tune on replayed Kalmár proofs only: 600 steps, AdamW, lr 3e-4 → 3e-5,
     128 proofs per step; 1.6 B tokens (13.5 % of KAL-D's).
   - Agreement 98.7–98.8 %; greedy valid 71–79 %, exactly Kalmár 54–60 %.
   - Not separated: lower learning rate, ≈ 150× larger batches, AdamW instead of Muon, no MTP. Extra tokens explain
     little (KAL-D's last 2.9 B: +9.6 points greedy).
   - Vs control, greedy % / plain pass@32: holdout250 36.7 vs 38.1 / 136 vs 165; G3 35.2 vs 7.2 / 56 vs 13;
     textbook72 41 vs 24 (pass@32).
   - Still not "learned": exact-follow at 1–2 atoms 63–69 % (bar 90 %).

   ![](figures/kalmar_anneal.png)

3. **EI ladder** (KAL-D s0, 3 rounds):
   - Targets solved: 135 → 572 → 668 of 1,000 (frozen 119–146).
   - **The replay-only fine-tune solves 578**: the jump is the fine-tune, not RL.
   - Pre-registered: "keeps the algorithm" fails (3.5 % of round 3's new proofs exact; bar 50 %), "finds shorter
     proofs" holds (43 %; bar 30 %); frozen sampling scores the same.
   - Greedy, EI follows the algorithm more (exactly Kalmár 14 → 57 %).

**Expectations vs outcomes.** Missed: most Kalmár-arm, four control (e.g. G1 supplied 92 % vs ≤ 20 %) and three of
five ladder predictions. Held: guided ≥ plain, KAL-C < control, control TF and greedy. Untested: KAL-D pass@256.

**Deviations.** KAL-D reads and the ladder at batch 1,024 (OOM at 2,048); no k extension; ladder stopped after 3
rounds; truncation above 0.1 % not re-read; some Addendum 3 reads on A40s.

**Spend.** $46.04 of $50.
