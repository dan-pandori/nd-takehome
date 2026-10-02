# Part E notes: Leon, Dmitry, Charles, nd-rl main, sprint/infra branches

## Coverage
- `sprint/r1-cot-2026-09-08`, `infra/runpod-setup`: 0 commits not on `origin/dan`, so nothing new.
- `main`: has no experiment summary absent from `dan` (dan has ~50 main lacks). Main adds the
  `lean_seq` tokenizer (PR #19) and Robbie's `docs/WHERE_THINGS_ARE.md` (run 198, score 681).
- `leon/benchmarking-dan` adds ndbench adapters, a Lean judge and dashboards for Dan's 12
  best-state checkpoints. **No numbers for Dan's models are committed** (outputs on `/scratch`).

## textbook72 identity
- Dmitry's branch adds only data: `textbook_dev.jsonl` (58), `textbook_train.jsonl` (14) and
  `synthetic_dev.jsonl`. **sha256 is byte-identical to the fork's `data/eval_only/textbook72/`**
  (dev 1b04192d…, train e6a219e0…). The third `protected_textbook` slice (`old_final`, 73) is lost.
- Dmitry's cap-comparison numbers (caps 6/10/12, 1 seed, 16 samples, dev58, best 10/58) are already
  on `dan` (`2026-09-10-proof-cap-comparison`), so no row; strict nd_verify, temperature not stated.
- Leon's run-1 sealed `textbook_dev.jsonl` has sha256 5d5273db…, which is **different** from
  1b04192d…. It may be a re-serialisation; I did not check content equality. ndbench's
  `textbook_dev` v1 is stated to be prompt-identical (58/58) to the fork file (DANSTATE_PLAN §0).
  Charles uses Dmitry's 72 directly.

## Protocol differences on textbook (do not compare across rows without care)
| source | pool | k | T | checker | seeds |
|---|---|---|---|---|---|
| Leon run 1 | dev58 | 32 | 0.8 | nd_verify (unfixed) | 2 sampling |
| Leon run 2 | dev58 | 256 | 0.8 | nd_verify (unfixed) | 1 |
| Leon ndbench | dev58 | 1-4096 (pass@k %) | 0.8 | nd_v2 (fixed) | 1 |
| Charles exp-00 | all 72 | 64 | 1.0 | strict_verify | 1 |
| Charles exp-00c | all 72 | 32 (avg solve rate) | 1.0 | strict_verify | 1 |
| Dan (fork) | 72 | 256 | (see Dan parts) | Lean | 3 |

- Leon/Charles models: 3.2M token prover (Robbie's `share_pretrain_4l_seed0`, f4409e4f) or 039_muon
  s1 (418af3f9, params not found); Dan's are 9.56M `lean_staten`: format, size and checker differ.
- Run 2 kept found proofs of any written length (52% > 11 lines); run-3 arms cap at 11 lines.
- Run-2 training used line-verified sampling; its sealed eval is plain sampling.
- Length-generalisation pass@1 values are 3-seed means (`mean_of_3`); per-seed not extracted.
- Charles's "new capability" = frozen 0/32, trained ≥ 0.5: a k=32 threshold, not a support test.

## nd_verify fix (leon/nd-verify-fix, also vendored in ndbench as nd_v2)
- Bug: `box_citable` never checked that a cited box ends before the citing line. Circular proofs of
  non-theorems (`|- P > Q`, and any formula with classical rules) verify.
- Leon scanned 876,479 accepted proofs from his own runs 1-3 and found 0 forward citations. ndbench
  re-judged 1.47M benchmark samples with nd_v2 and found no mismatch.
- **The fork's `nd_verify/verify.py` is the unfixed version** (sha 5dc502c2…). Leon argues that
  Lean-judged results are unaffected because `lean_seq` names each step before use. Results judged
  by nd_verify alone have not been scanned. That covers Dan's token-format runs, Charles's
  strict_verify, Dmitry's cap-comparison and Robbie's runs, if they rely on nd_verify. This is an
  open check.

## Open questions the evidence raises
- On textbook dev58, every 3.2M RL checkpoint sits at 5-10/58 (k ≤ 256). Leon's run-2 champion is
  the only one past 6 reference lines (3/43). ndbench finds base vs rl not robustly ordered at k up
  to 4096.
- In synthetic pools, RL lifts are large in distribution and one line past the training max.
  Beyond 2 lines past, every arm (Leon) is near zero. Charles's EI shows L8 0 → 0.27.
- Not found: ndbench results for Dan's models; Charles exp-00b (unmerged branch, unreviewed, "inert").
