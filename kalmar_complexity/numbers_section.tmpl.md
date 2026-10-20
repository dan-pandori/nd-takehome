## kalmar-complexity (2026-10-20, executor; UNREVIEWED)

Pre-registration `preregistration/kalmar-complexity.md` (`68f7ada4`, 12:30 UTC; addendum 1 `a32add38`, 13:16), both
before the first pod (13:17:34). Tables below are generated from the result files by
`kalmar_complexity/numbers_tables.py` (assembled with `kalmar_complexity/assemble_numbers.py`). Lean is not called:
no proof is judged in this run; the builder's proofs are kalmar-pretrain's (155,000 / 155,000 Lean-accepted).

**Algorithms.**
- **K-sl:** K12-Kalmár, the shared-lemma variant with memo that kalmar-pretrain trained on (`kalmar/kalmar.py`, `sl`).
- **K-tt:** nd-rl `code/tools/tt_prover.py` (per-atom split, no memo, a Lean term).

**Models (every learned number names one).**
- **KAL-D s0–s2:** `kalmar-pretrain/ckpts/kalmar/stage1_kalD_s{0,1,2}.pt`. 9,560,832-param ALiBiGPT 6 × 384,
  `lean_staten`, from scratch on K12-Kalmár sl (155,000 proofs, 16,876,247 pairs), 656,285 steps.
- **Snapshots:** `_step{24020,100000,200000,350000,500000}`.
- **KAL-C:** `stage1_kalC_s*` (24,020 steps).
- **KAL-D+A:** `anneal/kalDA_s*` (KAL-D + 600 AdamW steps on replayed Kalmár proofs).
- **Control s0–s2:** best-state `stage1_best12_s{0,1,2}_b1200.pt`, the same network, from scratch on K12
  (`data/kh/train_k12.jsonl`, 155,000 proofs, 1,239,995 pairs), 23,951–24,123 steps.
- **B2 models:** trained here, from scratch, ALiBiGPT S 2 × 128 (0.4 M), M 4 × 256 (3.2 M), L 6 × 384 (9.6 M) on
  prefixes of the same data (below).

**Test protocol.** Every program reproduces its reference exactly:
- `kalmar.build` / `tt_prover.solve` on 1,000 K12 theorems (`kalmar_complexity/common.py`, seed 20261020) plus at
  least one fresh seed.
- Per-step programs reproduce every state the algorithm visits:
  - `policy.py` 109,072 + 546,991 states;
  - golfed `kpol.py` 109,072 + 326,761;
  - RASP-L 109,072 + 107,233, plus an executor re-check at seed 99, 22,018;
  - the decision tree 473 distinct rows of 4,000 theorems + a fresh 217,968 states + all 137,984 tf1200 states;
  - BLC 1,000 + 300 theorems, plus an executor re-check at seed 99, 150.

### Q1 — program length of Kalmár's construction (algorithm / rendering / parse reported separately)

{{t_programs}}

- **Python:** hand-golfed (`kalmar_complexity/programs/python/`). DEFLATE = raw zlib level 9; xz = raw LZMA2 9e.
  - Tokens: Qwen3 / GPT-2. Our model's own tokenizer (`lean_tok`) cannot spell Python.
  - `mechanical:` rows are python-minifier upper bounds, unused code included.
- **BLC / binary CL:** Tromp's encodings (λ = 00, application = 01, variable i = 1^i 0; S = 00, K = 01,
  application = 1), from the agent-written toolchain `kalmar_complexity/programs/blc/`.
  - Data enter and leave as Scott-encoded terms; the encodings are stated in its README.
  - Binary CL is plain bracket abstraction of the golfed λ-term (an upper bound).
- **RASP-L** (per-step policy, H = 9 formula levels): decision 492 primitive ops, attention depth 41, 96 flagged
  non-RASP-L ops; rendering 52 ops (+3 layers); total 544 ops / 6,991 source tokens / 401 lines.
  - Scaling: ops = 240 + 28·H, depth = 5 + 4·H.
  - Effective depth per state (the smallest program that still decides it): 4 (premise lines), 8.0 (excluded
    middle), 9.5 (splits), 13.2 (fixed lemma-box steps), 14.4 (after-recursion steps), 17.2 [13, 33] (recursion
    steps). Source: `kalmar_complexity/programs/rasp/results.json`.
- **Decision procedure:** 21 generic state features → 40 action templates. The smallest exact tree found (beam 3)
  has 46 leaves / 45 tests / **626 bits** (`artifacts/kc/dtree/tree_u_b3.json`).
  - It is conditional on its feature extractor: `features.py` + `policy.py` is 3,962 B DEFLATE (mechanical upper
    bound). Most of the algorithm sits in the features.
- **Levin's Kt** = program bits + log2 running time adds 9–15 bits to programs of 1,600–11,000 bits. For whole
  proofs it carries no extra information:
  - Python: K-sl 6,921 (500 calls / theorem);
  - BLC: K-sl 5,458 (median 39,136 β-steps). Sources: `artifacts/kc/kt_python.json`, BLC `results.json`.

### Q2 — calibration (the same languages)

{{t_calibration}}

- **Rank agreement** across the 9 items (Spearman, `artifacts/kc/rank_agreement.json`): Python DEFLATE vs BLC
  **+0.97**, vs binary CL +0.93, vs RASP-L +0.95; BLC vs RASP-L +0.86.
  - Python with builtins breaks it: vs BLC +0.75, vs binary CL +0.67. Builtins sort in 9 bytes.
- **Kalmár sl is the largest item in every language:** 13× taut in BLC, 3.9× in Python DEFLATE, 7.8× taut in
  RASP-L ops.
- **K12 generator** (`gen.py`, mechanical upper bound with all knobs): 5,324 B DEFLATE, against K-sl's mechanical
  2,416 B (2.2×). The proof style the control learns easily (92 % greedy) is *longer* to describe than Kalmár.
- **Learnability in our family** (from B2 below and kalmar-pretrain):
  - eval (273 BLC bits) still costs 0.25–0.28 bits/token on theorems 8,192–16,384 at every size; only M breaks
    through when trained on all 16,384 (0.024 bits/token on the next 500);
  - K12 is learned to 92 % greedy in 24k steps;
  - Kalmár (5,443 bits) is not learned exactly in 656k steps.

### Q3 — bits the network absorbs

**B1** (`kalmar_complexity/b1_preq.py` → `artifacts/kc/b1_preq.json`).
- Code: first-epoch prequential code from the logged training curves, L_preq = Σ_i loss_i × N × Δepochs_i / ln 2.
  - Curves are each checkpoint's `extra['curve']`: KAL-D every 600 s, the control every 30 s.
  - Each point is the mean of every 20th step's pre-update loss.
  - N = exact loss tokens (action + eos; `artifacts/kc/tokens_*.json`).
- EDL = L_preq − N × L∞. The headline residual is (b), the final model's held-out loss (val300 for KAL-D,
  p2/heldout for the control).

{{t_b1}}

- **Absorbed bits:**
  - **KAL-D 6.3–7.1 × 10^6 bits** (0.66–0.74 bits per parameter), against the 5,443-bit BLC program: **×1,150–1,300**.
  - The control absorbed 1.5–1.7 × 10^6.
  - Within epoch 1 alone (residual (c)): KAL-D 1.7–2.1 × 10^6, the control 1.35–1.57 × 10^6.
- **What the logs cannot give:** per-step-type bits (only aggregate loss was logged), and steps 1–19 (never
  sampled; bounded above).
- **B1-snap** (`b1_snap.py` → `artifacts/kc/b1_snap.json`; per type `b1_snap_types.json`; an approximation):
  - Per-step-type held-out code of the 24 checkpoints on tf1200's 137,984 states, integrated over steps
    24,020–178,581 of epoch 1.
  - Its total is 1.13–1.20× the logged curve's code over the same window.
  - Per loss token the leaf steps absorb most (∧ true 0.06–0.10, ¬⊥ 0.06–0.07, ∨ true 0.05–0.07 bits/token);
    excluded middle, splits and ex falso least (0.01–0.02).

**B2** (pods; `b2_preq.py` → `artifacts/kc/b2/*.json`; summary `b2_summary.py`; per type `b2_per_type.py`).
- Block-wise prequential code over K12's first theorems; blocks at 64 · 2^k; the first block at the uniform code
  (log2 111 bits/token).
- Each block is coded by a fresh model trained (AdamW, early stopping on 10 % of the prefix) on everything before it.
- EDL = code − N × the last model's per-token code on 500 later theorems.
- **v1:** stop after 4 validations without improvement. **v2:** patience 3,000 steps, no stop before 5,000; added
  because v1 stopped the eval task after a few hundred steps.
- **The codes depend on the training budget.** Several blocks reached the step cap (20,000 steps or 30 epochs) while
  still improving, so these are upper bounds for this learner.

{{t_b2}}

{{b2_text}}

### Q4 — which measure predicts where the model fails?

- **Outcome:** KAL-D's teacher-forced error per step type on tf1200 (kalmar-pretrain's stored verdicts; joined by
  `q4_join.py`, overall agreement reproduced exactly). 15 step types with ≥ 500 states.
- **Predictors** (`q4_states.py`, `q4_analysis.py`):
  - **explored:** the number of in-scope lookups the post-order search for the next needed subformula makes;
  - **log2_ops:** log2(1 + policy.py's operations) — Levin's Kt minus the constant program;
  - **target_h / focus_h:** formula heights;
  - **decl_len:** the tokens of the formula written;
  - **py_bytes:** the bytes of the code in `ksl_alg.py` that emits the step;
  - **rasp_*:** RASP-L depth / ops on the step's decision path;
  - **log_freq:** a data baseline.

{{t_q4}}

- **Partial Spearman given log frequency** (KAL-D mean): RASP-L effective depth +0.85 (p < 0.001), lookups +0.79
  (p < 0.001), log2 ops +0.76 (p 0.001), target height +0.78 (p < 0.001), Python code bytes **−0.08** (p 0.77). The
  negative raw ρ of program length is frequency.
- **Error classes** (KAL-D s2, kalmar-pretrain's `error_classes`, 6,903 disagreements;
  `artifacts/kc/q4/error_classes.json`):
  - "other subformula" (45 %) rises with RASP-L depth (ρ = +0.94) and lookups (+0.93);
  - "corrupted" (31 %) with lookups (+0.76);
  - "malformed" (6 %) with the declared formula's length (+0.86).
- **False-formula assertions** (kalmar-pretrain's `error_truth.py` rule, by type; `q4_error_truth.py` →
  `artifacts/kc/q4/error_truth_by_type.json`):
  - Totals reproduced: 6,903 disagreements, 4,002 scored, 671 false.
  - Per 1,000 states: ∧ true 39.2, ∨ true 36.1, →I A-false 16.1, →I B-true 14.5, the other leaf types 4–8, structural
    steps 0.
  - Spearman: RASP-L depth +0.81, lookups +0.81, focus height +0.75, Python code bytes −0.27 (n.s.).

{{t_types}}

### Pre-registered expectations against outcomes

{{t_prereg}}

### Compute (`kalmar_complexity/compute_rows.py` → registry rows, `artifacts/kc/compute_table.md`)

{{t_compute}}

Spend: {{spend}}. Bucket: `hf://buckets/dan-pandori/nd-rl/kalmar-complexity/` (`artifacts/kc`, `data/kc`, the
programs and figures are in git).
