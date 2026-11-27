25 findings: 3 errors, 6 imprecise, 16 nits. Most of the review checks out: every table I recomputed matched, every quoted executor text is in its cited file (two quotes are trimmed), and no Phase-2 verdict flips.

Checked and correct (no finding):
- §2 re-grade table and cut shares;
- §3 comparison table, except item 5 below;
- the §4 Part-1 table, all 25 rows × 11 columns, plus the LoRA table and the expectation scoring;
- §5 adapter table, including the near-tie σ₆₄/σ₆₅ − 1 = 0.047 % at layer 43 up_proj;
- §6 hand counts: 1,434 / 405 / 368 / 80 of 95 / 288 of 310 / 37 / 214 / 205 / 9 / 1,876; 18 of the 35 screened groups read genuine; the screened set equals the executor's 35 in-scope draws;
- the executor recount 1,400 / 1,802 / 367 / 332 / 35 / 119 (332 holds once reads are ordered by round);
- §6 agreement 1,370 of 1,474, 82 / 22, and the per-prompt counts;
- §7 rates, G values, intervals and the sensitivity table;
- §8 compute and costs; claims 1–31 numbers, except where listed below.

## Errors

1. **§4, "Floor A is crossed early."** Quote: "RL's net change passes floor A, which is sized to a single interval, in almost every direction from step 500 on, so signal rank is ≥ 256 in 100 % of matrices at 2,300."
   - Problem: false at step 500, and false for attention matrices even at 2,300.
   - Evidence (`out/part1.json`), N500:
     - median signal rank 392 [216, 788];
     - ≥ 256 in only 70 % of matrices;
     - median per type: q 642 / 5,120, k 322 / 1,024, v 132 / 1,024, o 287 / 5,120, gate 842, up 781, down 911 (of 5,120), i.e. 3–31 % of directions.
   - Evidence, N2300: q 2,230 / 5,120 (44 %), o 1,926 / 5,120 (38 %), k 711 / 1,024, v 825 / 1,024. Only gate / up / down are near 100 %.
   - What holds: the median exceeds the 256 censoring point from 500 on, and ≥ 256 covers 93 % of matrices at 750 and 99 % at 1,100.
   - Severity: error.

2. **§1 "Models".** Quote: "Part-2 arms are served by vLLM 0.11.0 in bf16 on one H200: `dpo` 32B plus rank-k LoRAs (T_k, C16), or `dpo` with the 448 matrices replaced by s2300's (F448)."
   - Problem: C16 is F448 plus a negative rank-16 LoRA, not dpo plus a LoRA. The sentence also contradicts the review's own §5 and claim 16.
   - Evidence:
     - `out/provenance.json` metas.C16: model_dir `/workspace/models/f448`, rev `dpo+s2300.448`, lora_rank 16;
     - pre-registration Part-2 table: "`C16` | F448 + rank-16 LoRA B = −U₁₆ Σ₁₆".
   - Severity: error (low impact).

3. **Zero-delta: claim 23, Must-be-reworded item 4, and "Not supported".**
   - Quotes:
     - "the conclusion (the LoRA path adds nothing beyond engine noise) is supported by the stored pair";
     - "or cite the stored pair: ≤ 0.25 nats, the size of run-to-run noise";
     - "The only claim not derivable from stored files is the second-pair zero-delta identity (item 4)."
   - Problem: every noise reference also depends on the unstored second-pair files.
     - run-to-run: mean 0.010, max 0.23;
     - batched vs single: max 0.15.
   - Consequence: the stored pair alone shows only "max 0.25 nats, 62 / 1,451 identical". It cannot show that this is "the size of run-to-run noise". The suggested fallback wording, and §1's "Run-to-run noise between two plain runs is 0.23 nats", are no more derivable than the identity claim.
   - Evidence:
     - `pod/olmo_lowrank/after0.sh` lines 12–15: `run1_vs_run2_plain = diff zero_plain.json zero2_plain.json`; batched-vs-single uses `zero2_plain.json` / `zero2_lora.json`;
     - `artifacts/olmo_lowrank/stage0/` holds only `zero_plain.json`, `zero_lora.json` and `zero2_diff.txt`. I recomputed the stored pair: 1,451 tokens, 62 identical, max 0.25.
   - Severity: error.

## Imprecise

4. **§1, attention backend.** Quote: "The second pair, reported bitwise identical in `stage0/zero2_diff.txt`, was run with `VLLM_ATTENTION_BACKEND=FLASH_ATTN`."
   - Problem: the first pair used the same backend, so this does not tell the pairs apart. As placed, it implies the backend explains why the second pair is identical.
   - Evidence:
     - `pod/olmo_lowrank/stage0.sh` line 34 (first pair; same line at a2b82204 and 60b8f9d3) and `after0.sh` line 9 (second pair) both set FLASH_ATTN;
     - all four stored logs (`artifacts/olmo_lowrank/logs/lr-a/zero{,2}_{plain,lora}.log`) print "Using Flash Attention backend on V1 engine".
   - Severity: imprecise.

5. **§4, LoRA preamble.** Quote: "the inner products are the run's, validated on my sample within 1e-4 for k ≤ 16".
   - Problem: the kit does not show this, and it contradicts §3's own table ("≤ 4.8e-5 / ≤ 8.2e-3").
   - Evidence (`out/spectra_cmp.json` lora):
     - main|inner_k16 max_rel 1.25e-4, above 1e-4;
     - ctrl|inner_k16 max_rel 8.2e-3;
     - main|inner_full 9.0e-7.
   - Severity: imprecise.

6. **§4, "One interval carries most of the top direction."**
   - Problem: "most" is not measured. The review shows no alignment between I_mid's top direction and the net change's. The magnitudes put it well below most in energy.
   - Evidence (`out/part1.json`, norm2_total × S_1): I_mid's top-direction energy is 8.2, against 31.2 for N1600, 31.5 for N2300 and 30.6 for K (1,100 → 2,100).
   - Evidence (`spectra/R32/rows.csv`, per matrix): median σ₁(I_mid) / σ₁(N2300) = 0.44, about 0.2 in energy. Even under perfect alignment the interval supplies at most ~2/3 of σ₁'s growth from 1,100 to 1,600 in amplitude.
   - Severity: imprecise.

7. **Policy checks on the write-up, "Model labels".** Quote: "The two inherited numbers (31× SFT move, cosine 0.0052) name olmo-weights".
   - Problem: the cosine is this run's own measurement, not an inherited number. The run doc does not name olmo-weights for it.
   - Evidence:
     - `run_olmo_lowrank.md`: "Cosine with RL's change: 0.0052; with its top 16: 0.0086." (no olmo-weights);
     - `numbers.md` LoRA table: N2300 main cos 0.00525, from this run's `tables/lora.csv`;
     - only `log.md` 22:16 says "(reproduces olmo-weights)". Only the 31× is labelled as inherited, in the plain summary.
   - Severity: imprecise.

8. **Must be reworded 5.** Quote: "'more than half': say 'about half'".
   - Problem: overstated as a must-reword.
     - The plain-summary statement holds on the energy-weighted measure (54 % below floor B). That is the run's and the review's own aggregate convention: S_k, and "energy in spikes" 46 %.
     - Claim 29 itself scores it "holds energy-weighted only". The per-matrix median of 48 % is a different statistic.
     - At most an optional rewording.
   - Evidence: `out/spike_energy.json` 32B|N2300 energy_weighted_spike_share 0.4586; median_spike_energy_share 0.5209.
   - Severity: imprecise.

9. **Missed claim: the "exact" spectra.** The review does not report its kit's evidence against `numbers.md`'s bucket line "`adapters_svd/` (exact spectra of RL's change)" or the README's "the exact SVD spectra of RL's change used for the adapters".
   - Problem: the executor's fp32 "exact" SVD spectra are visibly inexact. The claim is unflagged, though the evidence directly supports claim 11 and Must-be-reworded item 3.
   - Evidence: `out/spectra_cmp.json` `adapters_svd_top256_maxerr_over_s1`, n 28, max 4.2e-4 σ₁. My recompute against `pod_out/out/sv_32B_L*.npz` gives:
     - max 4.17e-4 σ₁, at σ₁ itself, layer 43 gate_proj;
     - median of the per-matrix maxima 1.5e-4 σ₁;
     - against 5.6e-8 σ₁ for the run's Gram-route `full_*.npz`.
   - Severity: imprecise.

## Nits

10. **§7 table, pooled dpo A rate.** Quote: "0.2895 (pooled)".
    - Problem: double rounding, the same slip the review attributes to `numbers.md`'s T4.
    - Evidence: the exact value is (1,262 / 20) / 218 = 63.1 / 218 = 0.289450, which is 0.2894 to 4 dp.
      - 1,262 = 251 fresh + 1,011 F_dpo_ifb strict on the 176; 0 on the 42.
      - `readings.json` stores 0.28945; `readings.txt` and `results.csv` both print 0.2894.
    - Severity: nit.

11. **Must be reworded 2 and 3: fairness on inherited wording.**
    - Item 2 does not say that the brief set the phrase. BRIEF line 45: "does the floor alone, C16, recover anything?" is the executor's wording verbatim. Claim 16 also misquotes the brief as calling it "the floor only"; that phrase is the pre-registration's.
    - Item 3 and claim 11 do not note that "exact SVD" is pre-registered. Pre-registration Part 2: "exact SVD (fp32, full) if stage 0 projects ≤ 1 H200-hour".
    - The rewordings are still warranted.
    - Severity: nit.

12. **Claim 24.** Quote: "GPU-seconds from job wall are 0.2–0.5 % above the meta t_load + t_gen sums".
    - Problem: the actual range is 0.17–0.42 %.
    - Evidence: F448 5,439 vs 5,430 (+0.17 %); T256 9,629 vs 9,589 (+0.42 %).
    - Severity: nit.

13. **Policy checks, "Compute".** Quote: "`numbers.md` has a per-arm table and flags".
    - Problem: `numbers.md` § olmo-lowrank has no flags or token ratios. Its compute table has job / GPU / GPU-seconds / tokens / draws / cut only. The 1.25× flag and "≤ 2.51×" appear only in `run_olmo_lowrank.md`'s Compute line, which claim 24 cites as "(run, numbers)".
    - Severity: nit.

14. **§4 observations.** Quote: "About 220 directions per matrix stand above floor B".
    - Problem: the median is 227, as given everywhere else (claims 3 and 17, §7, Verdict). "About 230" would be consistent.
    - Severity: nit.

15. **Claim 11 and Must-be-reworded item 3.** Quote: "≈ 0.25 % after vLLM's bf16 cast".
    - Problem: §5 measures medians of 2.38e-3–2.50e-3 ("about 2.4e-3"). The executor's log already says 0.24 %.
    - Severity: nit.

16. **§1.** Quote: "The olmo-ifomega F_* rows store no ids."
    - Problem: they store response ids, which §2 decodes (dec_bad 0 for F_*). They lack prompt ids and prompt_tokens.
    - Evidence: `out/provenance.json` rows: prompt_tokens_match 0 / 2,400 and 0 / 4,800; metas have no prompt_sha256_by_pid.
    - Severity: nit.

17. **§3.** Quote: "Accuracy target met. The pre-registered target (randomized shares within 2 % for k ≤ 64 …) holds on my sample."
    - Problem: on the sample, only randomized share₁₆ and share₂₅₆ (and σ₁) were compared. k = 1, 4, 64 were not compared directly; they are covered only via the run's `accuracy.csv`.
    - Evidence: `rvr_spectra_cmp.py` computes s1_rsvd, share16_rsvd and share256_rsvd only.
    - Severity: nit.

18. **Policy checks.** Quote: "The secret scan of 341 tracked files and 1,553 bucket objects … found 0 hits."
    - Problem: the kit has no scan script or output, so this cannot be re-checked. No "secret" hits in `review/olmo-lowrank-recount/*.py`, and no scan file in `out/`.
    - Severity: nit.

19. **Policy checks.** Quote: "Everything recounted here comes from git or the bucket except the zero-delta second pair".
    - Problem: §8's costs come from `~/podhours.log`, and claim 31's pod time from `~/pods.log`. Both are local ledgers, neither git nor bucket.
    - Severity: nit.

20. **§7 and claim 18: inconsistent resolution standard.**
    - Quotes: "On A it is 0.348, inside." (P2), against "'unresolved' is the better word than 'hit (tentative)'" (C16).
    - Problem: by the same ≈ 0.10 resolution, P2 on A is also unresolved: 0.048 from 0.3, CI [0.277, 0.419] straddles it.
    - Severity: nit.

21. **Claim 22.** Quote: "≤ 0.004 | reproduces".
    - Problem: the ≤ 0.004 is the rule-6 variant of the reviewer's own labels. The executor's rule-6 variant was not recomputed.
    - Evidence: `readings_execlabels.json` has only the main variant.
    - Severity: nit.

22. **Claim 20 quote.** The review quotes the plain summary as "a third of RL's checker-passing answers were gamed".
    - Problem: the source says "A third of RL's checker-passing answers on the hard prompts were gamed". The scope is dropped without an ellipsis; the claim 28 quote likewise drops "from the RL model".
    - Severity: nit.

23. **Missed executor double rounding.**
    - `numbers.md`'s Part-2 table gives "R | T16 | 0.075", but the true rate is 0.07552 (0.076).
    - The same file's hand table gives 0.076.
    - Evidence: `results.csv` R,T16 0.0755; `hand_arm_summary.csv` 0.075521.
    - The review caught T4's 0.048 but not this one.
    - Severity: nit.

24. **Missed plain-summary omission.** Quote: "points into RL's top directions five times more than chance, but only slightly".
    - Problem: it omits that the matched control adapter (16 dpo answers) already sits at 2.3× chance, so the RL-specific excess is 2.2×. That is why E5 missed.
    - Evidence: `out/part1.txt` N2300 ctrl 0.0070 vs random 0.0030; `numbers.md` olmo-ifladder: `lora_ctrl` = 16 genuine dpo trajectories.
    - The Verdict states the 2.2× but does not flag the summary.
    - Severity: nit.

25. **Missed pre-registration deviation.**
    - The pre-registration says "Per-prompt consistency audits by sub-agents after each round".
    - The executor ran them once after the last arm was read: `log.md` 00:27 "run once after the last arm is read"; only u1–u4 in `artifacts/olmo_lowrank/hand/adjudication/`.
    - Neither the write-up nor the review's policy checks label this a deviation.
    - Severity: nit.
