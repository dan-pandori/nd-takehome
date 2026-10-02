# organism-analysis — what predicts RL success, and what RL learns (UNREVIEWED)

Stored data plus forward passes on 111 inherited checkpoints; no training. Models: best-cap12 / best-cap6 (9.56M
ALiBiGPT, `lean_staten`, from scratch, 3 seeds) and the `rl-from-ckpt` early-start ladders. Lean alone. Write-up:
`organism/ANALYSIS.md`; gallery: `organism/gallery.md`. `grpo-best` (not DONE) is not included.

**Q1: what predicts RL success?**

- **At cap 12, from the end of pretraining**, one worst-step threshold works about as well as any model: CV AUC
  0.77, 50 % point at −10.5 nats.
- **Cap 6 / early starts:** more features add 0.10–0.16 AUC.
- **Strongest feature: reference Lean term size** (P(solve) ≈ 0.9 at ≤ 8, ≈ 0.4 at ≥ 9; *post hoc*: mostly reductio).
- **Transfer:** rankings carry across caps and starts; the worst-step scale does not (50 % point −10.5 vs −21.6).

**Q2: what RL learns, by step class**

- →I boxes, applications, ∧E projections and ∨I rise by 6–7 nats at cap 6, mostly in rounds 1–2.
- They rise in never-solved theorems too (+0.5 to +4.5 nats per seed); class explains 12–37 % of gain variance.
- ¬I boxes do not move. *Post hoc*, the stuck ones are the boxes proving ¬¬X: they fall at cap 6 in 3 / 3 seeds. Yet ¬¬X
  boxes are 36–48 % of the negation boxes in RL's own training proofs.

**Q3: entropy and diversity**

- Entropy drops 16–30 % at r1, then is flat (cap 12) or rises (cap 6).
- The Cui fit rides on that one step (impossible ceilings).
- Distinct accepted proofs per theorem rise every round, even after pruning unused lines. There is no diversity
  collapse, so it cannot precede group C's stall.

**Predictions:** Q1 hit at cap 12, missed at cap 6; most entropy / diversity ones missed. **Spend:** 1.90 A40 pod-h, $0.93.
