
**Verdict (pre-registered rule; `style_edl/verdict.py` → `artifacts/style_edl/verdict.json`).**
- F = 0.1 bits per proof. The measured parts were |EDL_c(S_own) − EDL_c(S_own2)| ≤ 0.043 and order-to-order ≤ 0.031.
- Seeds (of 3) whose excess over S_own2 exceeds F, under EDL / EDL_c / cross-fit / ℓ_V EDL_c:
  - S_seed 2 / 0 / 0 / 0;
  - S_RL 2 / 0 / 0 / 0;
  - S_short 3 / 0 / 2 / 3;
  - S_Kal 3 / 3 / 3 / 0, with the capability criterion failed on 3 / 3 seeds.
- → **against**: no capability-fixed stream is above F under both EDL and EDL_c.
- Spearman ρ between style distance and the seed mean, over the six streams: EDL_c 0.14, EDL 0.71, cross-fit 0.54,
  ℓ_V EDL_c −0.20.

**Seed means with a bootstrap 95 % interval** (10,000 resamples of the three seeds; at n = 3 the interval is close to the seeds' min–max, `artifacts/style_edl/bootstrap.json`).

| stream | EDL per proof | EDL_c per proof | cross-fit EDL per proof | ℓ_V EDL_c per proof | plain pass@32 after |
|---|---|---|---|---|---|
| S_own | 0.058 [0.024, 0.095] | 0.025 [-0.005, 0.043] | 0.045 [0.011, 0.075] | 0.040 [0.038, 0.042] | 1.000 [1.000, 1.000] |
| S_own2 | 0.101 [-0.014, 0.225] | 0.035 [0.014, 0.054] | 0.018 [-0.007, 0.043] | 0.021 [0.003, 0.033] | 1.000 [1.000, 1.000] |
| S_seed | 0.195 [0.100, 0.269] | 0.061 [0.046, 0.073] | 0.065 [0.049, 0.088] | 0.051 [0.048, 0.058] | 1.000 [1.000, 1.000] |
| S_RL | -0.049 [-0.897, 0.555] | -0.057 [-0.370, 0.116] | -0.040 [-0.221, 0.053] | 0.054 [0.023, 0.076] | 1.000 [1.000, 1.000] |
| S_short | 0.943 [0.910, 0.968] | -0.105 [-0.340, 0.073] | 0.210 [0.098, 0.323] | 0.188 [0.160, 0.203] | 0.997 [0.992, 1.000] |
| S_Kal | 218 [190, 240] | 179 [177, 182] | 208 [185, 225] | -4.888 [-5.578, -3.971] | 0.328 [0.250, 0.383] |

**Pre-registered expectations against outcomes** (ranges were for the seed values; ✓ = all three seeds inside).

| stream | starting loss | EDL per proof | EDL_c per proof | style distance (1 − TF agreement) |
|---|---|---|---|---|
| S_own | 0.3–0.8 → 0.47–0.58 ✓ | −0.2–0.2 → 0.02–0.10 ✓ | −0.2–0.2 → −0.00–0.04 ✓ | ≤ 0.01 → 0.002–0.004 ✓ |
| S_own2 | 1.5–5 → 0.56–1.56 (1 / 3) | 0–0.5 → −0.01–0.22 (2 / 3) | 0–0.5 → 0.01–0.05 ✓ | 0.01–0.05 → 0.014–0.022 ✓ |
| S_seed | 1–3 → 0.81–1.94 (1 / 3) | 0–0.5 → 0.10–0.27 ✓ | 0–0.5 → 0.05–0.07 ✓ | 0.01–0.05 → 0.014–0.016 ✓ |
| S_RL | 1.5–8 → 1.26–1.83 (1 / 3) | 0.2–2 → −0.90–0.55 (1 / 3) | 0.2–2 → −0.37–0.12 (0 / 3) | 0.03–0.15 → 0.015–0.024 (0 / 3) |
| S_short | 5–25 → 2.83–3.29 (0 / 3) | 1–8 → 0.91–0.97 (0 / 3) | 1–8 → −0.34–0.07 (0 / 3) | 0.1–0.4 → 0.037–0.042 (0 / 3) |
| S_Kal | 200–800 → 1,255–1,411 (0 / 3) | 30–300 → 190–240 ✓ | 30–300 → 177–182 ✓ | 0.6–0.8 → 0.69–0.77 ✓ |

- **Ordering** S_own ≈ S_own2 ≈ S_seed < S_RL < S_short ≪ S_Kal. Only "≪ S_Kal" held: the seed-mean EDL_c are 0.025,
  0.035, 0.061, −0.057, −0.105 and 179. Per action, S_short and S_Kal were predicted within a factor of 3: −0.02 vs 1.54
  (missed). ρ ≥ 0.8: missed (0.14).
- **Capability.**
  - Before: plain pass@32 ≥ 0.99 ✓ (1.000).
  - After, plain pass@32 ≥ 0.98 on the five short streams ✓ (≥ 0.992); S_Kal 0.85–1.0 ✗ (0.25–0.38).
  - pass@1 before 0.93–0.98 ✓ (0.966–0.976). After: within ±0.03 for S_own / S_own2 / S_seed / S_RL ✓ (+0.002 to
    +0.022); S_short −0.10 to +0.02 ✓ (−0.013 to +0.013); S_Kal falling by 0.1–0.5 ✗ (it fell by 0.93–0.96).
- **ℓ_V.**
  - "Removes ≥ 60 % of S_short's and S_RL's EDL_c excess": not applicable, as neither had one. ℓ_V instead gives S_short
    an excess (+0.13 to +0.20, 3 / 3 above F). The intermediate fits put less mass on V(x) than the learner or θ* (e.g.
    block [16, 32), seed 0, order 1: 1.08 bits per theorem vs the learner's 0.24). Their own samples are not in V(x), so
    part of this dip may be valid proofs outside V; not checked.
  - S_Kal's EDL_V,c ≤ 20 % of its single-string EDL_c ✓ (−5.1 / −5.6 / −4.0, i.e. negative).
- **A_fixed:** the same ordering (EDL_c S_own 0.05, S_own2 0.03, S_seed 0.07, S_RL 0.07, S_short −0.15, S_Kal 217); its
  S_own EDL is positive at the chosen lr 1e-5 ✓.
- **Gate:** |EDL_c(S_own)| ≤ 0.3 on the pilot ✓ (0.043).
- **Addendum 1.**
  - S_short 0.1–1.5: EDL ✓ (0.91–0.97), EDL_c ✗ (−0.34 to 0.07), cross-fit ✓ (0.10–0.32). S_RL 0–0.8: EDL_c 2 / 3.
  - S_seed and S_RL do not clear F ✓; S_short at most even odds ✓ (it did not).
  - A1: differing proofs cost the learner 4–20 bits: S_own2 4.2–7.5 ✓, S_seed 2.4–4.3 (1 / 3; one at 3.999), S_RL 9.5–19.3 ✓,
    S_short 6.1–12.5 ✓.
  - EDL_c 0–4 bits per differing proof: single-direction −7.9 to 5.9 (4–13 differing test proofs: noisy); pooled
    cross-fit S_short 0.6 / 0.9 / 4.2, S_RL 0.7 / 0.5 / −5.2.
  - *same* proofs within ±0.2 ✓ (−0.015 to 0.154).

**Notes.**
- Table 6's "other" row is the VPS CPU smoke test of the runner (12 steps).
- S_Kal's arm used ≈ 90× the training tokens of the others, by design (its proofs are ≈ 25× longer; flagged per policy).
- The Kalmár proofs' TF agreement under the learners (0.27 / 0.31 / 0.23) reproduces kalmar-pretrain's E1 for the same
  checkpoints (0.278 / 0.302 / 0.228).
- Term size (`lean_check`, inference nodes; `artifacts/style_edl/term_sizes.json`), mean over seeds and halves:
  S_own 2.03, S_own2 2.20, S_seed 2.03, S_RL 2.11, S_short 1.88, S_Kal 96.4. ND lines: 3.50 / 3.71 / 3.50 / 3.60 / 3.26 /
  115.1.

**Sources.**
- `style_edl/results.csv`: one row per seed × stream, from `style_edl/analyze.py`.
- Per-block, per-proof losses: `artifacts/style_edl/edl/s{s}/{stream}.json`, `.fixed.json`, `edl_x/`, `lv/`.
- Capability rows: `artifacts/style_edl/cap/*.rows.jsonl.gz`.
- Reads: `artifacts/style_edl/reads/`. Streams: `data/style_edl/streams/`, `style_edl/streams_manifest.json`. V(x):
  `data/style_edl/vset.jsonl`.
- Compute: `artifacts/style_edl/compute.csv`, from the registry rows in `artifacts/style-edl/registry/`.
- Bucket: `hf://buckets/dan-pandori/nd-rl/style-edl/` (`artifacts/style_edl/`, `artifacts/style-edl/registry/`,
  `data/style_edl/`, `ckpts/style_edl/`).
