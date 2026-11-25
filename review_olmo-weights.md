# Review: olmo-weights — how far Olmo 3's weights move at each training stage

Reviewer session, started 2026-11-25 07:16 UTC (model claude-opus-5-5, effort max). Run brief: nd-rl
`docs/proposals/followups/BRIEF_olmo-weights.md`. Pre-registration: `preregistration/olmo-weights.md` (commit `a92b8cb7`,
04:48:59 UTC). My code and outputs are in `review/olmo-weights-recount/`.

**Models.** Every number below is about released AI2 checkpoints. All are pretrained bf16 safetensors that nobody in this
project trained. Labels follow the executor's manifest (`olmo_weights/manifest/checkpoints.csv`: label → repo, branch,
commit):
- **`32B/…`** (32.23 B parameters, 707 tensors): `allenai/Olmo-3-1125-32B` (`s1`, `s2i1`, `s2i2`, `s2merge`, `s3`,
  `s3merge` = base `main`), `Olmo-3-32B-Think-SFT` (`sft1e-4`, `sft5e-5`), `Olmo-3-32B-Think-DPO` (`dpo`) and
  `Olmo-3.1-32B-Think` (`rl`).
- **`7B/…`** (7.30 B parameters, 355 tensors): `allenai/Olmo-3-1025-7B` (`s1`, `s2`, `s3`), `Olmo-3-7B-Think-SFT`
  (`sft`, `sftmain`), `Olmo-3-7B-Think-DPO` (`dpo`), `Olmo-3-7B-Think` (`rl`, `rlmain`) and `Olmo-3-7B-RL-Zero-{IF,Math,Code}`
  (`zif`, `zmath`, `zcode`).
- **LoRA:** `olmo-ifladder`'s `lora_main` and `lora_ctrl` (rank 16, α 32, on the 32B DPO model).

## Independence and early exposure

- Phase 1 ran in `~/review/olmo-weights/`, the copy with the executor's write-ups removed. I did not read the following
  before committing this section: `log.md`, `olmo_weights/README.md`, `artifacts/olmo_weights/tables/` (including
  `expectations.json`, `status.json` and `tests.json`), the registry rows, the figures, or `~/runs/olmo-weights/*table*.md`.
- **Exposure, 07:16 UTC (session start).** The auto-loaded memory index carried the executor's one-line summary of its
  `olmo-weights` learnings. It said: "streaming 15 TB … for $3.77 …, Hub branches misfiled (32B SFT soup under
  5e-5-step8000, RL-Zero name collisions; check headers + tensor sets), RL ≈ 8–9×LR per step but cancels (S 0.07–0.10)".
  - I did not open the memory file.
  - Every number below comes from my own code. The hint may still have steered my attention to the `5e-5-step8000` branch.

## §Recount (phase 1)

### R1. Manifest, commits and hashes, from my own Hub API fetch

I fetched the data myself with `rv_manifest_check.py` (stdlib `urllib` against `huggingface.co/api`, 07:3x UTC). The
responses are in `out/hub_api_responses.tgz`.

- **Refs and trees:** for 453 checkpoints, every manifest branch points at the manifest commit. All 3,141 shard files
  match the manifest in name, size and LFS sha256: **0 mismatches**. The total is 14.69 TB of unique checkpoints.
- **Job downloads:** 469 member downloads of 3,244 files, 15.17 TB, as pre-registered.
- **Hash checks.** Every pre-registered claim holds:
  - 32B base `main` = `stage3-step11921+11000+10000-nooptim` = `…-reshard32`;
  - 7B base `main` = `stage3-step11921`;
  - 32B SFT `main` = `5e-5-step8000`;
  - all 15 `Olmo-3-32B-Think` branches equal 3.1's `step_0050`–`step_0750`, and its `main` = `step_0750`;
  - 3.1 `main` = `step_2300`;
  - the 7B SFT, 7B Think, RL-Zero IF and Math, and both DPO `main`s equal no branch;
  - the only byte-identical branch pairs in the SFT/RL repos are RL-Zero-Code `step_100` = `step_1000`, `step_200` =
    `step_2000`, `main` = `step_300`, and RL-Zero-IF `step_100` = `step_1000`.
- **Stage-1 locations:** my own implementation of the pre-registered rule reproduces both lists exactly (32B: 25
  locations, 0 … 655,000; 7B: 30 locations, 0 … 1,412,000).
  - Early targets map to the nearest released pair start in log distance. For 32B, 2,000 → 1,000 is a duplicate and is
    dropped.
  - The even locations are rounded to the nearest pair start.

### R2. Steps and learning rates: the sources

- **Upstream copies.** I downloaded every cited source at its pinned commit:
  - OLMo-core `3c1a108b` (the eight `official/OLMo3` scripts and `scheduler.py`), `79a184cf` (`OLMo-sft.py`) and
    `38f66526` (`OLMo2-7B-sft.py`);
  - open-instruct `fb18a8e8` (nine `olmo3/*.sh`);
  - arXiv 2512.13961v2, whose sha256 `f7520876…` equals `sources/olmo3_paper_sha256.txt`.

  All 14 files the executor copied into `olmo_weights/sources/` are byte-identical to upstream.
- **The numbers.** I read the cited lines and tables myself. Every number in `steps_lr.md` that the analysis uses matches
  its source:
  - tokens per step: 8,388,608, 4,194,304, 2,097,152 and 1,048,576;
  - peak LRs: 6e-4, 3e-4, 2.0712e-4, 1e-4 / 5e-5, 7e-8 / 8e-8, 2e-6 and 1e-6;
  - warm-ups: 2,000, 0, 200 and 3 %;
  - schedules: cosine with α_f 0.1; linear to 0; constant RL with 1 minibatch and 1 epoch;
  - DPO pairs and batch, 200 K / 150 K at 128, which gives 1,562.5 and 1,171.9 steps;
  - Table 49's step totals (1,400, 750, 2,000);
  - the Fig. 4 caption's 6.210e-5. My evaluation of the stated cosine at 656,000 is 6.69e-5, as `steps_lr.md` says.
- **Caveat 1 (minor).** The 7B long-context script at `3c1a108b` has `max_duration = 5e12` tokens and `hard_stop = 597046`
  (lines 106–108), copied from pretrain-1. "Linear to 0 at 11,921" therefore rests on Table 35 (50 B tokens) and the
  released last step, not on the cited script lines.
- **Caveat 2 (substantive, see R7.1).** The row "SFT released `main` = `5e-5-step8000`, LR there ≈ 1.33e-5" is wrong.
  The weights under that branch are the soup of the two runs' final checkpoints, not the 5e-5 run's step 8,000. The
  report says so (§4.2.2: "a linearly weighted merge of two checkpoints trained with different learning rates"), and so
  does Table 47 ("1.0e-4 souped with 5.0e-5").

### R3. On-pod recompute from the raw released checkpoints (the brief's reviewer check)

**Pod.** One A40 (secure, $0.59/h) under the run's budget: 07:25–07:53 UTC, 0.476 h, $0.28.

**Code.** `rv_recompute.py` is independent of `engine.py`:
- its own safetensors header parser and byte reader, so any shard layout works;
- bf16 → float32 by bit shift, then everything in float64;
- ulp from the bf16 bit increment, |value(m + 1) − value(m)| on the magnitude bits;
- LoRA products formed explicitly (2·B·A in float64), and its own random rank-16 seeds.

**Self-test.** `rv_selftest.py` builds synthetic files with planted equal / 1-ulp / 2-ulp / zero / subnormal changes and a
negative control. My first version caught a bug in my own code: `torch.ldexp` in float64 on CUDA returns 2^k minus one
float64 ulp on large tensors. I then checked the engine's float32 `ldexp` on CUDA (`rv_ulp_cuda_check.py`): exact on
50 M values (0 differences against CPU and against exact powers of two). The engine is not affected.

**Sample.** `rv_plan.py` draws with `random.Random(20261125)`: 2 intervals from 7B jobs and 2 from 32B jobs, from chain
intervals with a predecessor (282 and 154 candidates). I added three fixed tasks:
- the 32B RL endpoint, for the LoRA cosine;
- the triple around the one checkpoint the executor re-staged (`32B/sft5e-5/8000`), read from its original Hub files;
- that checkpoint's interval to DPO.

20 checkpoints, 890 GB, 192 files, all sha256 = manifest.

| task | ‖Δ‖ / ‖θ_a‖ (mine = executor) | ≤ 1-ulp fraction | lag-1 cosine (or LoRA cos) | worst per-tensor rel. diff | count mismatches |
|---|---|---|---|---|---|
| 7B `s1` 5,000 → 8,000 (seeded) | 0.4378624 | 0.0122104 (exact) | 0.1413144 (Δ 2e-10) | 9e-10 | 0 / 355 tensors |
| 7B `rl` 1,125 → 1,150 (seeded) | 2.43670e-4 | 0.9877033 (exact) | −0.2027348 (Δ 3e-16) | 3e-8 | 0 |
| 32B `rl` 1,350 → 1,400 (seeded) | 9.89354e-4 | 0.9509689 (exact) | −0.2360272 (Δ 7e-16) | 2e-8 | 0 / 707 |
| 32B `sft1e-4` 10,000 → 10,790 (seeded) | 3.86911e-3 | 0.6649127 (exact) | −0.0549384 (Δ 2e-12) | 5e-10 | 0 |
| 32B `sft5e-5` 8,000 → 9,000 (targeted, original layout) | 6.04283e-2 | 0.0757183 (exact) | −0.9686390 (Δ 5e-11) | 6e-10 | 0 |
| 32B `sft5e-5/8000` → `dpo` (targeted) | 3.76498e-4 | 0.9393507 (exact) | – | 3e-9 | 0 |
| 32B `dpo` → `rl/2300`, all tensors + 448 LoRA matrices | ‖θ − θ_DPO‖² 357.6076 | 0.6519792 (exact) | cos_main 0.00524973, cos_ctrl 0.000186404 (Δ 1e-10) | 2e-9 (per-matrix cosine Δ ≤ 1.1e-9) | 0 |

**Result:** all of these are far inside the brief's 1e-4:
- every per-tensor squared norm and offset matches to ≤ 2.8e-8 relative;
- every lag-1 and offset cosine to ≤ 1.7e-9 absolute;
- the per-matrix LoRA dot products to ≤ 3.3e-5 relative (they can be near 0; as cosines ≤ 1.1e-9 absolute);
- the aggregated LoRA cosines to 1e-10 relative.

Every equal / ≤ 1-ulp count matches exactly on every tensor.

**Random baseline.** My own 8 random rank-16 baselines (other seeds, the same norm matching) give a mean of 1.9e-6 and an
sd of 4.8e-6, so z(main) = 1,088. The executor's draws give a mean of −5.6e-7, an sd of 5.0e-6 and z = 1,044.

**Merge check** (`rv_merge_check.py`, `rv_merge3.py`; lm_head and layer-63 `down_proj`, 655 M values per merge):
- **Stage-2 merge:** bit-for-bit equal to round_bf16((`s2i1/23842` + `s2i2/23842`) / 2).
- **SFT `main` (`5e-5-step8000`):** bit-for-bit equal to round_bf16((`sft5e-5/10790` + `sft1e-4/10790`) / 2).
- **Stage-3 merge:** 88.07 % bit-identical to the mean of `s3/10000`, `11000` and `11921`. Of the rest, 11.8 % differ by
  1 ulp and 0.09 % by more. Every float32 and float64 way of forming the mean gives the same 88.07 %; bf16 arithmetic
  gives 59–65 %. The residual ‖merge − mean‖ is 1.22× the pure-rounding residual.
  - So it is the equal-thirds mean up to rounding.
  - The 12 % off-by-one values are consistent with averaging higher-precision copies of those checkpoints, which the
    released bf16 files cannot show.

### R4. Download logs and data completeness

`rv_files.py` checks every job's `files.csv`:
- all 3,244 expected member × shard files are logged once, status ok, with the manifest sha256, size and commit;
- the 14 pre-staged files match `restage.json`, whose 14 originals match the manifest;
- 15.110 TB came from the Hub in the jobs, plus 64.5 GB for the restage.

`rv_load.py` checks that every shard is DONE and that every (chain, idx, tensor) row appears exactly once. Every interval
covers all 707 / 355 tensors; the parameter totals are 32,233,522,176 and 7,298,011,136. There are 0 non-finite values in
any interval.

### R5. Pre-registered expectations, recounted from the per-tensor statistics (`rv_recount.py`)

Definitions are the pre-registration's. r = ‖Δ‖ / ‖θ_a‖. Steps come from branch names; DPO counts as one jump of
pairs / 128 steps. The SFT LR for "÷ LR" is my implementation of the cited schedule, averaged over each interval's
steps.

| | 32B | 7B | score |
|---|---|---|---|
| **E1** median r / step, RL vs SFT (within-stage) | RL 1.624e-5 (45 intervals) vs SFT 5e-5 run 2.633e-5 (10): 1.62× | RL 8.94e-6 (54) vs SFT 1.669e-5 (42): 1.87× | **miss** (≥ 10× needed in both) |
| **E2** ‖θ_RLlast − θ_DPO‖ / ‖θ_DPO‖ < ‖θ_SFTmain − θ_base‖ / ‖θ_base‖ | 0.003642 (`rl/2300`) vs 0.1131 (`sft5e-5/8000` from `s3merge`): 31× smaller | 0.000806 (`rlmain`, beyond `rl/1375`'s 0.000798) vs 0.1495 (`sftmain` from `s3/11921`): 185× | **hit** both |
| **E3** > 50 % of weights within 1 ulp of DPO at RL last | 65.20 % (bitwise equal 34.30 %) | 87.61 % (67.89 %) | **hit** both |
| **E4** S_RL > S_SFT (native spacing, from the stage start) | S_RL 0.1006 (46) vs S_SFT 0.2633 (11) | 0.0707 (55) vs 0.2086 (43) | **miss** both |
| E4, RL subsampled to SFT's count | 0.240 at 12 intervals (*) | 0.084 at 43 | still a miss |
| **E5** LoRA at 2,300 (448 matrices) | cos_main 0.005250 > cos_ctrl 0.000186; both < 0.1; random 8: mean −5.6e-7, sd 5.0e-6, z = 1,044 | – | **hit** |
| **G1** 32B RL intervals > 50 % bitwise unchanged; SFT 1,000-step intervals < 10 % | RL 46 / 46 (min 0.580, median 0.801); SFT 16 / 18 below 10 % (median 0.048). Both 9,000 → 10,000 intervals exceed it (1e-4: 0.130; 5e-5: 0.227) | – | RL half hit; SFT half holds at the median, fails in 2 / 18 intervals |
| **G2** per-step ÷ LR, RL ≥ 2× SFT | RL 8.12 vs SFT 0.830: 9.8× | 8.94 vs 0.658: 13.6× | **hit** both |
| **G3** boundary r / step > the last within-stage interval before it | s1 → s2 1.76e-4 vs 6.16e-5; s2 → s3 1.53e-4 vs 4.96e-6 | 1.39e-4 vs 3.27e-5; 1.14e-4 vs 3.98e-6 (the last stage-2 interval is 84 steps) | **hit** |
| **G4** merges are averages (< 1 % residuals) | stage 2: residual 0.46 % of ‖i1 − i2‖, best weight 0.5000. Stage 3: best 4-checkpoint weights 0.0004 / 0.3327 / 0.3344 / 0.3325 on 9,000 / 10,000 / 11,000 / 11,921, but the equal-thirds residual is **16.7 %** of ‖merge₃ − `s3/11921`‖ (8.56 vs 51.20) | – | **miss** on the stage-3 residual, which is rounding level (R3) |
| **G5** DPO did not start from SFT `main`; best soup residual < 50 % of ‖θ_DPO − θ_SFTmain‖ | θ_DPO is 1.955 from SFT `main` and ≥ 310.2 from every other SFT checkpoint. The best two-checkpoint soup is SFT `main` itself (100 %) | – | **miss**. DPO started from the released SFT `main`, which is itself the 1e-4 + 5e-5 soup (R7.1) |
| **G6** 32B RL: embedding bitwise-unchanged fraction > every MLP type | 46 / 46 intervals (median 0.985 vs max-MLP 0.803) | – | **hit** |
| **G7** at step 1,000 each RL-Zero run is farther from its start than RL-from-DPO | – | IF 1.071e-3 and Math 8.35e-4 > 6.80e-4; **Code 6.61e-4 < 6.80e-4** | **miss** (2 of 3) |

(*) RL straightness on a coarser subsample needs chords between non-adjacent checkpoints. The stored lags (1–3) and
`dot_prev` give those exactly only for gaps ≤ 4 intervals. Subsampling the 46 RL intervals to 11 needs gaps of 5, so my
nearest exact value is at 12 intervals. Coarser subsampling can only raise S, so this bound is informative but not
decisive at 11.

**Sensitivity to the SFT soup detour (R7.1)** in the pre-registered 32B 5e-5 chain:
- E1: dropping the two intervals around the soup moves SFT's median to 2.26e-5 (1.39×), still a miss;
- E4: replacing the detour by the 7,000 → 9,000 chord gives S_SFT = 0.393, still a miss.

Other quantities recounted:
- consecutive-change cosines: median −0.221 for 32B RL and −0.198 for 7B RL, against −0.017 / −0.038 (32B SFT 5e-5 /
  1e-4) and −0.058 (7B SFT);
- distance from each stage's start, straightness for all 16 chains, per-module and per-layer r and the unchanged / ulp
  fractions per interval;
- LoRA by module and depth: cos_main > cos_ctrl in all 7 module types and all 8 depth bins, largest in `down`
  (0.0129), `v` (0.0127) and `o` (0.0107). ‖ΔW_main‖ / ‖θ_2300 − θ_DPO‖ over the targeted matrices = 0.468.
  (`out/rv_*.csv`, `out/rv_lora_breakdown.txt`)

### R6. The other pre-registered tests

- **Starts.** These tests pass. The first SFT checkpoint and each first RL-Zero checkpoint are nearer to base `main` than
  to `s3/11000`:
  - 7B SFT 52.07 vs 56.44;
  - IF 3.35 vs 22.45;
  - Math 0.51 vs 22.20;
  - Code 2.07 vs 22.29.

  No first interval exceeds 3× the second per step (ratios 0.54–1.03).

  The IF and Code "first" checkpoints are misfiled step-1,000 weights (R7.2), so those two rows test the wrong
  checkpoint. The conclusion still holds: IF `step_200` is 1.00 from base `main` and Code `step_400` is 1.14, against
  ≈ 22 for `s3/11000`.
- **Stage-3 start (32B).** `s3/1000` is 776.1 from the stage-2 merge and 1,712.9 from `s1/656000`; the merge itself is
  1,558.5 from 656,000. So stage 3 started from the stage-2 merge, as the card and report say, not from the script's
  `load_path` `step656000`.
- **7B DPO start.** θ_DPO is 1.202 from `sftmain` and 1.837 from `sft/43000`. `sftmain` is 1.389 from `sft/43000`, with
  91.8 % bitwise unchanged, which is consistent with the end of SFT near 43,297 steps.
- **Mains beyond the last branch** (r from the last branch vs the interval before it):
  - `rlmain` 2.74e-4 vs 2.70e-4 (≈ step 1,400);
  - `zifmain` 5.50e-4 vs 5.36e-4;
  - `zmathmain` 5.76e-4 vs 5.76e-4 (≈ step 2,000).
- **Duplicate names.** Under the pre-registered rule (distance from base `main` fitting the neighbours), IF `step_100` =
  `step_1000` belongs at 1,000, Code `step_100` = `step_1000` at 1,000, and `step_200` = `step_2000` at 2,000. The
  `step_100` / `step_200` names are the collisions.

### R7. Findings from the recount that the write-up must handle

1. **The 32B SFT `main` is the soup of the two runs' finals, filed under the branch `5e-5-step8000`.**
   - **Evidence:**
     - the Gram fit is 0.5000 / 0.5000 on `sft5e-5/10790` + `sft1e-4/10790`, residual 10.09, the bf16-rounding level;
     - it is bit-for-bit equal on the tested tensors (R3);
     - in the 5e-5 chain, the distance from base goes 424.6 → 583.3 → 443.7 at 7,000 → "8,000" → 9,000;
     - the change into "8,000" is 6.40e-2 against 1.70e-2 for the interval before it, and the next change reverses it
       (cosine −0.969).

   Consequences:
   - the pre-registration's "the released SFT is the 5e-5 run at step 8,000" and `steps_lr.md`'s "LR there ≈ 1.33e-5"
     are wrong;
   - the 5e-5 chain's 7,000 → 8,000 → 9,000 intervals are not training intervals;
   - E2's "SFT `main`" is the soup: that is correct as defined, but its label should say so;
   - G5's framing ("DPO did not start from SFT `main`") misses because the released `main` is the soup;
   - DPO started from it (1.955 away, 3.8e-4 relative, 93.9 % within 1 ulp).
2. **RL-Zero branches misfiled beyond the byte-identical pairs.** Distances from base `main` (×1e-4 of ‖θ_base‖) along the
   label order:
   - **IF:** `step_200` 3.20, `step_300` 5.36, **`step_400` 17.94**, `step_500` 8.05, … `main` 13.79. The change out of
     "400" reverses the change into it (cosine −0.92). It fits no position from 100 to 2,000 and lies beyond `main`.
   - **Code:** **`step_300` = `main` at 15.11**, beyond `step_2900`'s 14.73, so it is consistent with ≈ step 3,000. The
     genuine early checkpoints start at `step_400` (3.66).
   - **Math:** monotone throughout, clean.

   In label order:
   - the IF chain has 4 corrupted intervals (`s3/11921` → 100 → 200, 300 → 400 → 500);
   - the Code chain has 4 (`s3/11921` → 100 → 200 → 300 → 400);
   - per-interval rates there, and the chain straightness (IF 0.0995, Code 0.090), are not those of training intervals.

   The byte-identity rule cannot catch `step_400` or `step_300`.
3. **E4 subsampling to 11 RL intervals cannot be computed exactly from the stored statistics** (see (*)). If the write-up
   reports it, it must say how the chords were obtained.
4. **G4's stage-3 miss is a threshold below the bf16 rounding floor.** A perfectly rounded equal-thirds mean would still
   leave ≈ 14 % of ‖merge₃ − `s3/11921`‖. The 1 % criterion could not pass for any recipe.
5. **Caveat 1 of R2** (the 7B long-context script duration).

### R8. Compute and cost, from the logs

**Engine time.** The 13 engine runs (`summary.json`) took 17,698 s, 4.92 h on one A40 each, and downloaded 15.110 TB.

| job | b32_s1 | b32_s2 | b32_s3 | b7_s1 | b7_s2 | b7_s3 | p32_rl | p32_sft | p7_rl | p7_sft | z7_code | z7_if | z7_math |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A40 seconds | 3,613 | 2,461 | 1,157 | 992 | 822 | 226 | 3,405 | 2,175 | 884 | 750 | 491 | 372 | 349 |
| TB from the Hub | 3.159 | 2.063 | 0.967 | 0.861 | 0.730 | 0.204 | 3.030 | 1.483 | 0.832 | 0.686 | 0.452 | 0.321 | 0.321 |

Not counted in the table:
- the p32_sft restage, 450 s;
- one failed p32_sft attempt on `ow-d` (06:01, rc 1);
- stage 0 and stage 0b, about 30 min on `ow-s0`.

**Pods.** `~/podhours.log` lists 7 A40 pods (secure, $0.59/h; the rate in each registry file), 6.194 h, $3.65, plus one
RTX 4000 Ada request that never got a machine (0.36 h, logged at $0.10). The run total is 6.557 h and **$3.77** of the
$50 budget. Stage 0 cost $0.32 (A40) + $0.10, under the ≤ $3 gate.

**Stage-0 re-cost.** Stage 0 measured 1.06 GB/s at 8 files in flight and 0.88 GB/s through the engine with its GPU cache.
That projects ≈ 4.8 A40-hours × $0.59 × 1.3 ≈ $3.7, far below the $45 pause line, so no cut was needed.

Generated tokens, training steps, training tokens and Lean checks are all 0: nothing was sampled or trained.

**Reviewer pod:** 0.476 A40-hours, $0.28, 890 GB downloaded (registered under `olmo-weights`).

**Reproduce.** Run each with `ROOT` = the repository root:
- `python3 review/olmo-weights-recount/rv_manifest_check.py ROOT OUT`
- `rv_recount.py ROOT OUT`
- `rv_soup.py ROOT`
- `rv_files.py ROOT`
- `rv_compute.py ROOT`
- `rv_lora_breakdown.py ROOT`
- `rv_compare.py ROOT pod_out_unzipped OUT.json`

The pod side is `rv_job.sh` (plan.json), `rv_merge_check.py` (merge_plan.json) and `rv_merge3.py`.
