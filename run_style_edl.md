# run style-edl — does EDL rise with proof style when capability is fixed? (executor, 2026-10-23; UNREVIEWED)

**Question.** Does EDL charge a learner for *which* valid proof it is taught, when it already proves the theorem?

**Setup** (`preregistration/style-edl.md`; `numbers.md` § style-edl).
- Learners: K12 bases `stage1_best12_s{0,1,2}_b1200` (9.56 M, `lean_staten`, from scratch).
- 256 tf1200 theorems all three prove (≥ 29 / 32), split 128 / 128 by renaming class.
- Six Lean-checked streams: own greedy, own sample, other seed's, shortest (minlen), EI r8's, Kalmár's.
- EDL: prequential blocks 0–128, early-stopped AdamW; EDL_c removes the split's mismatch.
- Capability: pass@32 on the test theorems after training.

![](figures/style_edl.png)

**Pre-registered verdict: against.** No capability-fixed stream beats S_own2 by the floor (0.1 bits per proof) under
both EDL and EDL_c.
1. **Capability-preserving styles are mostly the learner's**: identical on 94 % (other seed), 92–94 % (EI r8),
   85–88 % (shortest) of theorems.
2. **Their EDL_c is at the floor**: −0.40 to +0.06 bits per proof above S_own2 (0 of 9 cells above F); pass@32 ≥ 0.99.
3. **The brief's EDL flags S_short** (+0.74 to +0.92, all seeds) **from the split alone**: the stream half holds 21–26
   of the learner's 30–39 differing shortest proofs. Swapping halves (exploratory) leaves +0.19 / +0.06 / +0.33.
4. **Only learnable style is charged.** θ* learns the shortest style (differing proofs 6–13 → 1.1–1.4 bits; ≈ 0.6–4 bits
   of EDL each); EI's and the other seed's deviations (2–19 bits each) are not learned.
5. **Kalmár: a large EDL, not at fixed capability.** EDL_c 179 / 182 / 177 bits per proof (1.5 per action); θ*'s test
   loss falls from ≈ 1,300 to ≈ 90. pass@32 falls from 1.00 to 0.38 / 0.35 / 0.25 (guided 0.60 / 0.60 / 0.59).
6. **ℓ_V** (any collected valid proof counts) turns Kalmár's EDL_c into −5.1 / −5.6 / −4.0 (valid mass collapses) and
   gives S_short +0.13 to +0.20 over S_own2 (valid mass dips mid-learning).

**Expectations vs outcomes.** Held: S_own, S_own2, S_seed ≈ 0; S_Kal's EDL; short-stream capability. Missed: S_short
(1–8) and S_RL (0.2–2); S_Kal's starting loss (≈ 1,300 vs 200–800) and capability (0.25–0.38 vs 0.85–1.0);
ρ(style distance, EDL_c) 0.14 (≥ 0.8); ℓ_V removing S_short's excess (it added one).

**Deviations.** Environment-assigned names not coded; one theorem set; early stopping; EDL_c; post-hoc cross-fit;
A5000s (no 3090); a duplicate job; an out-of-memory guided read redone on an A40.

**Spend.** $1.86 of $10 (6.7 pod-hours).
