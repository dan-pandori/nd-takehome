## style-edl (2026-10-23, executor; UNREVIEWED)

**Question.** Does EDL rise with the style of the target proofs when the learner's capability on the theorems is held
fixed? Pre-registration: `preregistration/style-edl.md` (+ Addendum 1, committed before any stream but S_own was scored).

**Models (every number here names one of these):**
- **Learners L_s, s0–s2:** best-state's `ckpts/bs/stage1_best12_s{0,1,2}_b1200.pt` (bucket `best-state/ckpts/bs/`; md5
  9c436c35 / f7ae9a9e / 354c4428, checked on every pod). 9,560,832-param ALiBiGPT 6 × 384, `lean_staten`, from scratch
  on K12 (`data/kh/train_k12.jsonl`, 155,000, md5 800b5486…), 1,200 s on an A40. These are kalmar-pretrain's control.
- **EI r8 (S_RL's proofs only):** best-state's `ckpts/bs/ladder/la_T1_best12_s{0,1,2}_r8.pt` (md5 991a0ac8 / 164a6c17 /
  d43c0381): 8 EI rounds from L_s on `rl_targets.jsonl` (k 32, T 0.8). Learner s gets its own base's ladder.
- **θ\*:** L_s fine-tuned by A_ES on the 128 stream proofs of one stream, at the chosen lr, order 0:
  `ckpts/style_edl/s{s}/{stream}/theta_es_lr{lr}_E0_o0.pt`. All 54 (3 lrs per cell) are in the bucket.

**Protocol (as pre-registered unless marked).**
- **Checker.** Lean alone decides: `lean_gate` on the literal text for every sampled proof, and Lean on the literal
  canonical `lean_seq` text for every stream proof. All 1,598 candidate proofs were accepted, and all 638 used proofs
  were re-confirmed by `lean_check`. `nd_verify` is never called. L_true labels are not used.
- **Theorems.** tf1200 (`data/kalmar/tf1200_kal_sl.jsonl`, md5 b99c3b8d; none in a K12 renaming class).
  - 632 are eligible for all three seeds: ≥ 29 / 32 Lean-valid at T 0.8 (seed 1), base and r8 greedy proofs valid, a
    valid k 4 draw (seed 3), and a minlen proof.
  - 256 were sampled (seed 20261023) and split 128 stream / 128 test by premise-order-invariant renaming class, with
    atom-count strata balanced (stream 16 / 34 / 36 / 42, test 15 / 34 / 37 / 42 for 1 / 2 / 3 / 4 atoms).
- **Reads.** Caps `max_steps` 1,024 and `max_action` 512, batch 1,024 for every read.
  - Peak memory: 7.5–7.7 GB for the greedy reads (`kal_free.py`'s `peak_alloc_gb`). `guided_eval.py` does not record it.
    One guided read of a Kalmár-trained θ* ran out of memory at ≥ 15.6 GB while sharing a 24 GB card. It was redone
    alone on an A40 (below).
  - Truncation (`max_action` hit): 144 of 390,752 attempts (0.04 %). 108 are in seed 1's S_Kal θ* plain read (1.3 % of
    its 8,192, above the policy's 0.1 % line), 9 in the other S_Kal θ* reads, 24 in the learners' reads, 3 in the
    other θ* reads. `max_steps` was never hit. A truncated action is > 512 tokens, against the longest action of any
    Kalmár proof (219), so these attempts are degenerate loops; a larger cap would not make them valid.
- **Scoring.** Teacher-forced NLL of the action tokens + `<eos>` in bits (fp32). Environment-assigned names are not
  coded (`kalmar/tf_agree.masked`). One name base per theorem.
- **A_ES.**
  - Optimiser: AdamW (0.9, 0.95, wd 0), constant lr, clip 1, 8 proofs per batch, the Stage-1 name shift.
  - Early stopping: validated on a quarter of the prefix, ≤ 8 passes, patience 2, then a refit on the whole prefix.
  - lr ∈ {1e-5, 1e-4, 1e-3}, chosen per seed × stream by the mean prequential code over two orders, + log₂ 3 bits.
  - A_fixed: E = 4 passes, chosen on the S_own pilot.
- **EDL and EDL_c.** EDL = Σ block bits − 128 × L_test. EDL_c subtracts the learner's own stream / test mismatch (same
  expectation). Cross-fit = the same protocol with the halves swapped, averaged (exploratory, post hoc).
- **Capability.** k 32, T 0.8, sample seed 2 (not the selection seed), on the 128 test theorems. Reported plain
  (primary) and guided (`--arm logical`, ≤ 10 rejections).
- **ℓ_V.** −log₂ Σ_{y ∈ V(x)} p(y | x) over V(x) = 2,852 distinct Lean-valid proofs collected for the 256 theorems
  (`data/style_edl/vset.jsonl`). It is computed on re-fits of the chosen-lr runs.
  - Their single-string bits match phase 4 to ≤ 0.03 bits per proof per block on the short streams, and to ≤ 2.1 bits
    on Kalmár's ≈ 300-bit proofs (memory-efficient attention's backward is not bit-deterministic).
  - EDL_c agrees to ≤ 0.003 bits per proof (short streams) and ≤ 0.17 (Kalmár, of ≈ 180).
- **Aggregation.** Per-seed values; with n = 3 the IQM is the mean. Floor F = 0.1 bits per proof (the pre-registered
  minimum; the measured parts were ≤ 0.043).

