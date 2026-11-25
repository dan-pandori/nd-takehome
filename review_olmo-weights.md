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

## §Comparison (phase 2): the executor's claims against my recount

Phase 2 started after commit `0ffe5c51` (07:58 UTC). I read:
- `run_olmo_weights.md`;
- `numbers.md` § olmo-weights;
- `log.md` § olmo-weights;
- `olmo_weights/plain_summary.md` and `olmo_weights/README.md`;
- `artifacts/olmo_weights/tables/*`;
- Figures 1, 5 and 7;
- the registry rows.

The executor's files are in the run worktree, since the main checkout `~/nd-takehome` is on another branch. New checks for
this phase are in `rv_phase2_checks.py` and `rv_spacing.py` (outputs `out/rv_phase2_checks.txt`, `out/rv_spacing.txt`).

| claim (where) | my independent value | verdict |
|---|---|---|
| 453 checkpoints, 15.2 TB, A40 pods, $3.77 of $50 (run, numbers) | 453 checkpoints (14.69 TB unique); 15.17 TB downloaded (469 member downloads); 6.56 pod-h, $3.77 | reproduces. "15.2 TB" is the download volume, not the size of the 453 checkpoints |
| Stage switches are obvious; the LR sets the per-step size (run) | all 4 boundary intervals exceed the interval before them (G3). Per-step ÷ LR is 0.57–0.87 at 1,000-step spacing in every stage | reproduces |
| Pretraining → SFT: median change per step 0.57–0.87 × LR (1,000-step intervals, both models) (run) | 32B 0.569 / 0.870 / 0.851 / 0.83 (5e-5) / 0.80 (1e-4); 7B 0.725 (31 intervals; executor 0.744 on 32, which include the 3,000 → 4,000 gap and the 814-step last interval) / 0.674 / 0.659 / 0.658 | reproduces. The "stage 1 pairs" row includes 2 non-pair intervals |
| **RL breaks this pattern: at a constant LR, its change per step grows to about 8–9 × the LR** (run; plain: "about ten times larger than the LR predicts", "an RL step is nearly as large as an SFT step") | 8.12 (32B) and 8.94 (7B) at the native **50- / 25-step** spacing. The ratio depends on spacing (below) | **numbers reproduce; the interpretation is not supported.** At matched spacing RL's per-step ÷ LR is in the band of the other stages |
| 80 % (32B, per 50 steps) / 92 % (7B, per 25 steps) of weights bitwise unchanged between RL checkpoints (run) | medians 0.801 / 0.924 | reproduces |
| Of the moved weights, at least three quarters move by ≤ 1 rounding step (run) | 32B: median 0.761, **min 0.599**; 7B: median 0.815, min 0.752 | **differs for 32B.** "About three quarters (median)" is right; "at least" is not |
| E1: RL's change per step only 1.3–1.9× smaller than SFT's (miss) (run, numbers) | 1.29 (32B, executor's chain without the soup name; the pre-registered chain gives 1.62) and 1.87 (7B) | **miss reproduces.** At matched 1,000-step spacing the ratio is 10.8–13.6× (32B) and 24.6× (7B) |
| RL consecutive changes cosine −0.2 (run) | −0.221 / −0.198, and −0.219 / −0.236 at 2× spacing | reproduces |
| E4: S = 0.10 vs 0.39 (32B), 0.07 vs 0.21 (7B) (miss) (run, numbers) | 0.1006 vs 0.393 (0.263 on the pre-registered chain with the soup), 0.0707 vs 0.2086. RL subsampled: 0.240 (12 intervals), 0.084 (43) | miss reproduces. The executor's "RL 0.24 at 12 intervals" is the exact value. The spacing still differs (≈ 200 vs 1,000 steps) |
| E2: RL total 0.36 % / 0.08 % of ‖θ‖, 31–185× smaller than SFT's (hit) | 0.364 % / 0.0806 %; 31.1× / 185× | reproduces (also from the raw weights for 32B: R3) |
| E3: 65 % / 88 % within one rounding step of DPO (hit) | 65.20 % / 87.61 % | reproduces (32B from the raw weights: 0.6519792 exactly) |
| Attention and MLP matrices move 1.1–1.9× the model average in every stage; norms barely move (run) | executor's table pooled by stage: 1.05–1.93; per family 0.96–1.99. In 32B stage 1, v moves 0.96× and o 1.01×. Norm vectors 0.00–0.30× | approximately. "≈ 1–2×" is accurate |
| DPO's jump concentrates on attention (32B 2.2–2.7×) (run) | q 2.16, k 2.59, v 2.65, o 2.56 vs MLP 0.96–1.42 (7B: attention 1.84–2.15, MLP 1.51–1.84) | reproduces |
| LoRA cos 0.0053 at 2,300, ≈ 1,000 random sd above chance, control 0.0002 (hit) (run) | 0.0052497 (rounds to 0.0052), z = 1,044 (my own draws: 1,088), control 0.000186; recomputed from raw weights (R3) | reproduces (rounding nit) |
| LoRA alignment grows during RL; adapter 0.47× RL's final change (run) | 0.00078 (50) → 0.00525 (2,300), near monotone; 0.468 | reproduces |
| 32B SFT `main` (= `5e-5-step8000`) is the equal-weight soup of both runs' finals; DPO started from it (run, numbers) | Gram fit 0.5000 / 0.5000, residual 10.09; **bit-for-bit** equal to round_bf16 of the mean on the tested tensors (R3); DPO 1.955 from it, ≥ 310 from everything else | reproduces, and more strongly than claimed |
| Stage 3 started from the stage-2 merge (run, numbers) | 776 vs 1,713 | reproduces |
| Five RL-Zero branch names hold misfiled weights, excluded (run, numbers) | the same five: IF `step_100` (= 1,000), `step_400` (17.9e-4, beyond `main`); Code `step_100` / `200` (= 1,000 / 2,000), `step_300` (= `main`, beyond 2,900). IF `step_400` lies outside the byte-identical rule, and the executor says so | reproduces |
| Expectations 7 of 12 hit (run, numbers, log) | E2, E3, E5, G2, G3, G6 hit; E1, E4, G4, G5, G7 miss. **G1 was scored on medians**, which the pre-registration does not specify: RL 46 / 46 intervals > 50 %, but SFT 2 of 18 1,000-step intervals ≥ 10 % (13.0 %, 22.7 %; `tables/expectations.json`: median 0.0665) | **6 or 7 of 12**, depending on the G1 reading. The write-up must say G1 was scored at the median |
| G4: the stage-3 merge is the equal-thirds average; bf16 rounding exceeds the 1 % threshold (run, numbers: "bf16 rounding of an exact average") | best weights 0.0004 / 0.3327 / 0.3344 / 0.3325; residual 16.7 %. Only **88.07 %** bit-identical to the rounded mean of the released branches (stage-2 merge and SFT soup: 100 %), with a residual 1.22× pure rounding | the miss reproduces. "Rounding of an exact average" is close but not exact: it is the equal-thirds mean up to rounding-level differences, consistent with averaging higher-precision copies |
| G5 miss; G7 miss (Code) (run, numbers) | 1.955 vs ≥ 310; Code 6.61e-4 vs 6.80e-4 | reproduce |
| Per-stage, chain, test, merge, main, LoRA-by-step and compute tables (numbers; `tables/*.csv`) | all 452 rows of `tables/intervals.csv` agree with mine to ≤ 4.7e-10 relative (r) and ≤ 5e-11 (lag-1 cosine). The 5,424 module rows both tables share agree to ≤ 5e-10. The stage, chain, test and LoRA values I recomputed agree to the printed precision. The only difference is the 7B stage-1 row (32 vs 31 intervals, 0.744 vs 0.725) | reproduces |
| Registry: 91 rows; compute table; bucket (numbers) | 91 rows = 13 jobs × 7 metrics; `gpu_seconds` equal `summary.json` for every job; generation, training and Lean metrics 0. The bucket holds 1,981 files with no `.safetensors` | reproduces |
| RunPod balance $218.24 → $214.36 (numbers) | no stored balance history | not derivable (plausible: $3.77 billed) |
| Plain summary: the LoRA "taught the starting model most of RL's new tricks" | inherited from `olmo-ifladder` (reviewed: `lora_main` elicits 40–41 of 48 IFBench/IFEval reach prompts on Olmo 3 32B Think DPO, `lora_ctrl` 0). It carries no label | supported, **unlabelled** (policy: inherited claims carry their label) |

### Why "RL breaks this pattern" does not stand

**Per-step ÷ LR falls with checkpoint spacing inside the same run.** The chords come exactly from the stored `o2`,
`dot_prev` and lags 1–3, which I verified on raw weights (R3).

| run | native spacing | 2× | 3× | 4× | first 1,000 steps (from the stage start) |
|---|---|---|---|---|---|
| 32B RL (Olmo 3.1 Think) | 7.98 (50 steps) | 4.96 | 3.75 | 3.15 (200) | **0.97** (1.08 if the lineage after the restart is 900 steps, see below) |
| 7B RL (Olmo 3 7B Think) | 8.92 (25) | 5.67 | 4.29 | 3.51 (100) | **0.68** |
| 7B SFT | 0.658 (1,000) | 0.452 | 0.364 | 0.314 (4,000) | 0.86 |
| 32B SFT 5e-5 / 1e-4 | 0.83 / 0.80 (1,000) | – | – | – | 0.90 / 0.86 |
| 32B mid-training | ingredient 1: 0.87 (1,000) | – | – | ingredient 2 (same schedule): 0.41 (4,000) | – |

- **Matched spacing.** Over ~1,000 steps, RL's per-step change is 0.7–1.1 × its LR, the same as SFT's 0.86–0.90 over its
  first 1,000 steps. The 8–9× comes from 25–50-step spacing. When consecutive changes anti-correlate (cosine −0.2), the
  displacement grows sublinearly with steps (here ∝ L^0.33), so short intervals inflate the per-step rate.
- **bf16 rounding.** Rounding plausibly adds to this at RL's and DPO's tiny LRs: at 25–50 steps ≥ 60 % of the moved
  weights move by ≤ 1 ulp. The 7B DPO jump, one 1,172-step interval at LR 8e-8, also gives 8.1× LR.
  - In the 32B RL run, the per-step rate drops back to the first-interval level after each optimizer restart (next
    section) and then climbs again. That fits a rounding effect.
  - The pre-registration listed both mechanisms under G2, but the headline attributes the excess to RL.

**What can be said.**
- At their released 25–50-step spacing, RL checkpoints differ by ≈ 8–9 × LR per step.
- Over 1,000 steps, RL moves ≈ 0.7–1.1 × LR per step, as the other stages do.
- RL's per-step change is ≈ 11–25× smaller than SFT's at matched spacing, which is about their LR ratio.
- G2, scored as pre-registered (native spacing), is a hit. E1, scored as pre-registered, is a miss.

### New finding: the 32B RL checkpoints are not one line (`Olmo-3.1-32B-Think`, identical to `Olmo-3-32B-Think` for 50–750)

Chords between checkpoints, from the stored statistics (`rv_spacing.py`; units 1e-4 of ‖θ_DPO‖):
- `step_150` and `step_250` are both "`step_100` + one fresh 50-step move":
  - each is 3.32 from step 100, the size of DPO → 50 (3.31);
  - each is 5.42 from step 50;
  - each is 6.09 from DPO;
  - they are 4.67 apart, which is √2 × 3.32, so the two moves are orthogonal (cosine 0.008).
- `step_200` descends from 150 (4.32), not from 250 (6.10).
- Steps 300 onward descend from 250 (d(250, 300) = 4.40, d(200, 300) = 7.29).

So 150 → 200 is a branch the run abandoned, and the released line restarts from step 100. The 200 → 250 "interval" is a
jump between branches (its cosine with the interval before is −0.645).

Three intervals show a fresh-optimizer signature (first-interval size, cosine ≈ 0 with the previous interval): DPO → 50,
100 → 150 and 1,850 → 1,900. The last is a resume without rollback: d(1800, 1900)² = d(1800, 1850)² + d(1850, 1900)².
The 7B RL chain shows none of this.

**Consequences:**
- Labels from 250 up probably overstate the optimizer steps along the released lineage by ≈ 100. That is small for
  per-step rates and ≈ 4 % for totals.
- **`olmo-ifcurve`'s step-200 point** (Figure 5's pass@1 0.347 and the rug of 7 first-genuine prompts at step 200; same
  commit `15d5e3cd`) is on the abandoned branch, not on the lineage of steps 250–2,300.
- The executor did not detect this. Its duplicate rule only covered byte-identical names.

### The brief's three reviewer checks

1. **Seeded recompute from raw checkpoints on a pod:** passed. ‖Δ‖, the ≤ 1-ulp fraction and the cosines (lag-1 and LoRA)
   agree with the executor's rows to ≤ 3e-8 relative, against the 1e-4 asked; counts are exact (R3).
2. **Manifest hashes, step and LR sources:** passed (R1, R2), with two caveats:
   - the 7B long-context script's duration;
   - the SFT `main` row of `steps_lr.md`, which the executor's own soup finding corrects but `steps_lr.md` still states.
3. **Figure 1's normalisation and stage marks:** they match the table:
   - the y-axis is r ÷ optimizer steps;
   - stage 1 is plotted as its 25 / 32 sampled 1,000-step intervals;
   - the boundary intervals (s2i1/1000, s3/1000, sft/1000, rl/50 or rl/25) are ringed;
   - merges and the SFT soup are hollow, and 7B `main`s are diamonds;
   - DPO is one 1,562.5- / 1,172-step jump;
   - the plotted extremes equal the table's (32B RL per step 6.6e-6 … 3.7e-5).

   Nit: in the 32B panel, the soup's "merge (0 steps)" label sits on the DPO point.

### Other policy checks

- **Expectations before data.** Committed at 04:48:59 UTC (`a92b8cb7`), before the first pod request (04:55:50);
  unchanged since. Misses are reported as misses, except for G1's scoring rule.
- **Models.** Every number in the write-up and `numbers.md` is labelled with repo, branch or commit, except the plain
  summary's inherited `olmo-ifladder` claim.
- **Compute rows.** Present and correct; per-arm table in `numbers.md`. No arm comparison is at stake.
- **Pre-registration declarations.** The language-model standards (hand gate, templates, budgets) and the seed / noise-floor
  standard do not apply: no text is generated and the statistics are deterministic. The pre-registration says so, and
  I agree.
- **Hard constraints.** No secret in the committed or uploaded files (my scan of the run's artifacts and code, including
  gzipped CSVs, against token patterns and the literal HF token); every count reproduces; no judge issue. No quarantine.
- **Spend.** $3.77 (executor) + $0.28 (this review) of $50; balance $213.98.

## §Verdict

**What stands:**
- the manifest and every pre-registered hash check;
- the step and LR sources;
- every per-tensor statistic, which reproduces from the raw weights;
- the distance, straightness, unchanged-fraction and module tables;
- E2 and E3: RL moves the weights 0.36 % (32B) and 0.08 % (7B) of ‖θ‖ in total, 31–185× less than SFT, and leaves
  65 % / 88 % of weights within one bf16 step of DPO;
- E5: the `olmo-ifladder` LoRA points along RL's change (cos 0.00525, ≈ 1,000 random sd, 28× the control) and the
  alignment grows during RL;
- G3 and G6, and the misses E1, E4, G4, G5 and G7;
- the checkpoint findings: the SFT `main` soup (now bit-for-bit), stage 3 from the stage-2 merge, the five misfiled
  RL-Zero names;
- the compute and cost.

**Must be reworded:**
1. **"RL breaks this pattern … 8–9 × the LR"** (run) and the plain summary's "about ten times larger than the LR predicts"
   and "an RL step is nearly as large as an SFT step". Say that this holds at the released 25–50-step spacing. Over
   ~1,000 steps RL moves 0.7–1.1 × LR per step, like every other stage, and ≈ 11–25× less per step than SFT. Name
   spacing (with anti-correlated changes) and bf16 rounding as the causes.
2. **E1's sentence** needs the same spacing caveat. The miss stands as pre-registered.
3. **"At least three quarters"** of moved RL weights within one rounding step → "about three quarters (32B median 76 %,
   range 60–79 %; 7B 75–83 %)".
4. **"7 of 12"** → say that G1 was scored at the median. Two of the 18 32B SFT 1,000-step intervals have more than 10 %
   unchanged.
5. **G4's "bf16 rounding of an exact average"** → "the equal-thirds mean up to rounding-level differences (88 %
   bit-identical to the rounded mean of the released branches)".
6. **Minor:**
   - "1.1–1.9×" → "≈ 1–2×";
   - 0.0053 → 0.0052;
   - "15.2 TB" is the download volume (the 453 checkpoints are 14.7 TB);
   - give the pre-registered-chain values next to the soup-excluded ones (E1 32B 1.62, S_SFT 0.263), as `log.md` does;
   - label the plain summary's `olmo-ifladder` claim;
   - `steps_lr.md`'s SFT `main` row is superseded.

**Not supported:** RL's large per-step change relative to its LR as a property of RL.

**Next measurements:**
- **RL at matched spacing, mid-run.** On a pod (< $1), difference RL checkpoints 1,000 steps apart:
  - 32B 300 → 1,300 and 1,300 → 2,300;
  - 7B 375 → 1,375.

  This settles whether mid-run RL also moves ≈ 1 × LR per step at 1,000-step spacing, as the from-start chords say.
- **Confirm the 32B RL branch point with direct differences.** Use θ_250 − θ_100 against θ_150 − θ_100, and look for a
  rollback at step 200 in AI2's RL logs. Mark `olmo-ifcurve`'s step-200 point as off-lineage.
- **Measure the bf16 rounding share of the RL / DPO changes.** Compare per-step change against time since each
  optimizer restart (the 1,850 → 1,900 reset is a natural experiment), or model flips against the fraction of weights
  near rounding boundaries.
