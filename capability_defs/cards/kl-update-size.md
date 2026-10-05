# Card: how far did RL move the model? (KL to the base and the size of the update)

Family D. Slug `kl-update-size`. Notation: `_FRAME.md`.

## 1. Definition, formally

Two views of "how big a change RL made", each with a reference scale.

- **Output space.**
  - Per theorem: KL(π_R(· | t) ‖ π_B(· | t)) on RL's own samples. Estimate it as the mean over R's attempts of
    log π_R(y) − log π_B(y), which needs teacher-forced scores of R's samples, failures included.
  - On the success set it splits into selection + reshaping bits (`sharpen-expand`).
  - Token level (URIAL): the share of positions where R's chosen token is not among the base's top choices.
- **Parameter space.**
  - Relative update norm ‖θ_R − θ_B‖ / ‖θ_B‖ per matrix.
  - Effective rank of ΔW (the number of singular values carrying 90 % of ‖ΔW‖²).
  - Whether a rank-r (LoRA) or d-dimensional random-subspace fine-tune reproduces R's gain (intrinsic dimension,
    Aghajanyan et al.).

**The reference scales** that make sizes interpretable:
- the update pretraining makes over a comparable span (θ_pend − θ_p20000);
- the replay-only control's update (8 rounds of the same fine-tune on pretraining data, `rl-from-ckpt`);
- seed-to-seed differences.

## 2. Decision rule

| verdict | rule |
|---|---|
| **elicited** ("a small update that switches on a behaviour") | RL's gain is reproduced by an update much smaller than the reference scale (low rank, small KL per theorem relative to the selection bits), or the token-level shift touches few positions |
| **created** | the gain needs an update as large or as high-rank as pretraining-scale changes, and no small update reproduces it |
| **neither** | no gain |

**This card is weak by design.** "Small update" is not "old capability": a rank-1 change can add a new skill if the
skill is simple (`sharpen-expand` §6). The rule is offered because Dan's brief asks for it, and the critic is expected
to land.

## 3. Null or floor

- The replay-only control (training without RL proofs) is the placebo update.
- Random reinitialisation of one matrix is the upper reference: any update below it counts as "local".
- The random-weights objection does not arise (no k).

## 4. How to compute it here

- **Parameter space:** CPU, seconds, from local checkpoints (pend, step 1,600 and r8 for all seeds, md5-verified in
  `~/review/trajectory/rv/ck/`; r16 from the bucket) with `~/venv-cpu` torch.
- **Output KL on R's samples:** J3's plain arm stores R's accepted texts with counts, but not its failures. Scoring
  every R attempt is a new job (not run).
- **Low-rank sufficiency:** a LoRA sweep is a new job (≈ 1 GPU-hour); not run here (stated).
- **Result:** in Part 3 (`out/update_size.txt`), if run.

## 5. Sensitivity

- **Parameterisation:** norms depend on layer and optimiser. Compare like with like (the same matrices, the same
  number of steps).
- **Precision:** Mukherjee et al.'s "RL updates small subnetworks" sparsity vanishes in float32 (Shenfeld et al.
  Sec. 6, via L3), so sparsity claims need fp32 checkpoints.
- **Temperature and decoding:** affect the output KL, not the parameter view.
- **Representation, renaming:** output KL is per prompt.
- **Seed:** the reference scale must include seed differences.

## 6. Failure modes

- **Small ≠ old.** The size of a change does not say whether the capability existed. A small update can unlock a new
  composition, a large one can only reformat.
- **Many updates achieve the same function:** parameter distance is not functional distance.
- **Output KL on R's samples is dominated by format / length changes,** not the hard step.

## 7. Relations

- Its success-set part is `sharpen-expand`.
- Low-rank sufficiency is a version of `elicit-finetune` (an elicitation budget counted in parameters: Donoway et al.,
  NeurIPS 2025, screened by L2).
- The token-level shift ties to `tf-proof-prob`'s step view.

## 8. Literature anchor

- **Lin et al. 2023 (2312.01552v1):** "77.7% of the tokens are at such unshifted positions" and shifted tokens are 5–7 %
  (Sec. 2.2).
- **Shenfeld et al. 2025 (2509.04259v1):** the forgetting "is determined by the distributional shift, measured as the
  KL-divergence between the fine-tuned and base policy evaluated on the new task" (abstract).
- **Mukherjee et al. 2025 (2505.11711):** RL changes 5–30 % of parameters (L3 note); disputed in fp32.
- **Aghajanyan et al. 2020 (2012.13255):** d90 intrinsic dimension falls over pretraining (L3 note).
- **LoRA Without Regret** (Thinking Machines blog): RL takes in "O(1) bits per episode" (L3 note; blog, quote verified
  by L3).
- Verified in `_claims_L3.md`.

## 9. Critic's verdict

*(pending)*
