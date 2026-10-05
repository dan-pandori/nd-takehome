# Independent check of the Part 3 numbers (capability-defs)

I wrote my own code (`/tmp/indep/{common,sets13,calib4,lem5}.py`) and ran it on the raw files. I froze my numbers at 09:28 UTC, before opening `out/part3.json` (09:27, md5 cf22a9a1), `out/bracket.json`, `bracket_s01.txt`, `out/lem.json`, `lem.txt` and `log.md`. I did not read `analysis/*.py`.

## Results

| Quantity | Mine | Executor | Match? |
|---|---|---|---|
| 1. Equal-k created set, r8 x0, s0 / s1 / s2 | 54 / 51 / 60 | 54 / 51 / 60 | yes (same theorems) |
| 1. Jaccard, x0 vs x1 | .778 / .702 / .676 | same (from part3 sets; log says 0.68–0.78) | yes |
| 2. Net of replay, x0 | 37 / 27 / 33 | 37 / 27 / 33 | yes (same theorems) |
| 2. Net of replay, Jaccard x0 vs x1 | .810 / .667 / .615 | same (from part3 sets) | yes |
| 3. Not reached (compute-matched), s0 / s1 | 24 / 23 | 24 / 23 | yes (same theorems) |
| 3. Same, net of replay | 21 / 16 | 21 / 16 | yes (same theorems) |
| 4. Calibration median [IQR], stage-1 known proofs F only | s0 .957 [.875, 1.011]; s1 .929 [.838, .993] | identical | yes |
| 4. Same, F plus pend's J2-found proofs | s0 .982 [.904, 1.020]; s1 .940 [.848, .998] | — | **definition differs (A)** |
| 4. exp(LB) above the CP 95 % upper bound, ≥ 1 success | s0 3 / 57; s1 2 / 52 | s0 3 / 57; s1 not reported (bracket.json gives the same 2) | yes |
| 5. J4 / J6: solved out of 39 and mean rate, all 27 reads | e.g. A16 37 / 34 / 37 (.789 / .681 / .827); A4 36 / 33 / 36; pend, A0, C16 0; r16 0 / 36 / 13; no-DN + A16 35 / 37 / 37 | identical on all 27 reads | yes |

Beyond the table:
- All 40 comparable sets in `part3.json` are identical to mine: `eqk`, `eqk_net`, `cm` and `cm_net` for s0 and s1 (r8 and r16, x0 and x1), plus `eqk` and `eqk_net` for s2.
- For every H ∪ CAL theorem, `bracket.json`'s successes, attempts, CP upper bound, `n_proofs` and `LB08` equal my F-only values to within 2e-15.

## Disagreements and diagnosis

**A. The calibration leaves out the J2-found proofs, though the text says they are in it.**
- Stage 2 scored 344 (s0) / 827 (s1) proofs that pend found in J2 (ids `j2:`), mostly on CAL theorems.
- `bracket.json` and the 0.957 / 0.929 medians use only the stage-1 set F.
- The log's 07:50 and 09:23 entries say the stage-2 targets include these proofs. REPORT.md says the sum is "over every proof … any model ever found".
- Counting them raises the medians to 0.982 / 0.940. The exceedance counts do not change.
- The LB moves by up to +2.10 nats (`la_transfer_1552`, s0, H).
- Q15 says "Σ_F", so leaving them out is defensible; the inconsistency is in the labelling. State one definition.

**B. Two LB definitions coexist in the log.**
- The 09:01 seed-0 quantiles (0.54 / 0.80 / 0.96 / 1.05 / 1.43) match my version with the J2-found proofs exactly.
- The F-only version, which `bracket.json` uses, gives 0.54 / 0.79 / 0.95 / 1.05 / **1.30**.

**C. Minor:** the log says the two smaller exceedances are "< 1 %", but `la_transfer_2100` is +1.03 %.

**D. Not in the log (seed 1).**
- The exceedances are `la_transfer_1032` (+2.8 %) and `la_transfer_428` (+0.03 %).
- Separately, `textbook_418e4b67e7e59d93fa6b` has 0 successes in 17,152 attempts, yet exp(LB) = 1.89e-4 is above the zero-success upper bound of 1.75e-4.
- The "≥ 1 success" filter hides this case. It supports the finding that the LB is not strictly a bound.

**E. Presentation:** `part3.json` stores `cm = cm_net = []` for s2. Without J2 the set is undefined, not empty. Use null.

## Integrity checks (all passed)

- **Read files:** each plain read has all 322 names exactly once, with n_tried = 256.
- **J2 files:** they are disjoint, with distinct seeds (7000–7007, 7100).
- **Extra pend draws:** x4 is a separate draw, not a replay of x2 (0 / 36 identical reasons lists). x2 is not a replay of x0 or x1.
- **Stage-2 scores:** on all 7,994 targets scored in both stages, the stage-2 score is ≥ the stage-1 score − ln 33.
- **Unscored targets:** 24 / 58 stage-1 targets failed replay. Both of us dropped them.
- **Log cross-check:** the claims "24 of 54" and "27 / 57" about J2 hits reproduce.

## Second check, after stage B (2026-10-05 14:16 UTC)

A fresh subagent re-derived the compute-matched definitions with its own code (`/tmp/indep_check/`; it read the run's
scripts only for definitions), from the raw reads, J2 chunks and J9 chunks.

| s0 / s1 / s2 | independent | `out/part3.json` (13:59) |
|---|---|---|
| K_eval-set (r8) | 19,281 / 21,107 / 23,310 | same |
| equal-k (r8, x0) | 54 / 51 / 60 | same sets |
| compute-matched (cm) | 22 / 21 / 14 | same sets |
| cm, 0 base successes | 18 / 18 / **8** | 18 / 18 / **9** |
| cm net of replay-only | 20 / 14 / 8 | same sets |
| cm, no seed's base ever | 5 / 6 / 6 | same sets |
| r8 coverage / base within reach at K / Δ_cov | 286 / 286 / 293; 265 / 270 / 281; +21 / +16 / +12 | same |

- The one mismatch is timing: J9 chunk `s2_k4` (1 success on `la_transfer_1648`, s2) landed after part3.json was
  written. Leaving it out reproduces every part3 value; the final rerun includes it (cm0 s2 → 8; the theorem stays in
  cm at 1 / 721,664).
- Negative controls: counting the doubled-cap truncation chunks changes nothing (their only success is on a theorem
  already within reach); dropping J2 but keeping J9 shrinks cm to 3 / 3 / 3; dropping both empties cm (n ≤ 1,024 < K)
  and widens Δ_cov to +47 / +39 / +42 — the budget is what moves the answer.
- Integrity: every plain read covers the 322 theorems once at 256 attempts; chunk caps in each `args.json` match the
  file names; no sampling seed repeats within a seed; no chunk contains theorems outside the 322.
