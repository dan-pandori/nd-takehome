# C3 / C4 independent recount

Code and outputs are in `rv/C3C4/`; downloaded files are in `rv/raw/`. I did not read the executor's audit files.

- **Solved** = at least one Lean-accepted sample for a pool prompt. Prompts are unique within each pool, so solved sets are keyed by exact prompt.
- **md5 spot-check:** `rr_T1_SN12_s0__ge17` is `f0bf83a8` both in audit/raw and in the bucket.

**Models** (params from summaries; no torch to load `.pt`). All from scratch. SN12 = 3.2 M `lean_staten` on K12 (md5 `800b5486` verified), T1 = + 8-round ladder on `rl_targets`. K12 T1 = 3.2 M `lean_seq` on K12 + ladder. SN6 ("ours" cap 6) = 3.2 M `lean_staten` on the cap-6 set (md5 `29276f24`). best6 / best12 = 9.56 M ALiBiGPT `lean_staten` on cap-6 / K12, + ladder.

## C3: Q (rr600 generator, L_true 13–16, /380, k 256)

| model | stated | mine |
|---|---|---|
| SN12 T1 s0–3 | 233/295/320/317 | same |
| SN12 Fz s0–3 | 134/212/228/216 | same |
| K12 T1 s0–1 | 79/72 | same |
| SN6 T1 / Fz | 102/28; 3/0 | same |

The difference is **+215.75**. Pooled seed sd is 35 and the MDD is 113 (stated: 119). Separation is complete; at 4 vs 2 seeds the smallest one-sided permutation p is 1/15.

**Same checkpoint, read twice:**
- SN12 T1 s0/s1 at max_steps 48 vs 96: 233→231, 295→296.
- **long-pool-2** re-read of s2/s3 (max_steps 96): 320→316, 317→313. Both z = +0.39.
- K12 Fz s0, long-pool rr vs rr2: 40 vs 38.

No pair disagrees. The overlap (Jaccard) of the Q-solved sets between the two reads is 0.86–0.93.

## C4: textbook72 (/72, k 256) and the dev metric

| cell | Fz | T1 |
|---|---|---|
| ours6 | 16/14 | 22/16 |
| best6 | 19/18/20 | 39/40/33 |
| ours12 | 26/29/32/26 | 37/38/36/38 |
| best12 | 32/27/27 | 52/51/52 |

All cells match the stated values. On textbook72, best − ours after RL is **+18.33** at cap 6 and **+14.17** (IQM) at cap 12 (stated +18.3 / +14.2). On the dev metric, which I re-derived as the 1,108 records with sha1(key) even, it is **+292.2 / +104.3** (stated +292.2 / +103.8).

**Pairs:**
- Same checkpoint:
  - best12 T1 s1 at 2× caps: 51 vs 53.
  - SN12 T1 s0 at a1024: 37 vs 37.
  - Trajectory sample seeds x0 vs x1: |Δ| ≤ 4, |z| ≤ 0.8.
- Fresh-seed replication (different checkpoints):
  - Trajectory best12 r8: 48/49/54.
  - Trajectory-cap6 best6 r8: 43/41/38.
  - Both are consistent (|z| < 0.6).

## MDD vs NOISE_FLOOR

NOISE_FLOOR has no row for these models or pools. Its pass@k counts on hard pools have a coefficient of variation of 0.43–0.48. Transplanting that variation gives:

| comparison | transplanted MDD | observed difference |
|---|---|---|
| C3 | ≈253 | 216 |
| textbook72, cap 6 T1 | ≈46 | 18 |
| textbook72, cap 12 T1 | ≈54 | 14 |

All three differences are inside the transplanted MDD. The observed seed sd is far smaller (1–4 on textbook72), and against that the differences are outside the MDD.

Adding the trajectory seeds gives full separation:
- best12 vs ours12, 6 vs 4 seeds: p = 1/210.
- best6 vs ours6, 6 vs 2 seeds: p = 1/28.

C3 has no replication.

## Leakage

My key is invariant to atom renaming and premise order.

| train set | Q | rr600 | textbook72 | dev |
|---|---|---|---|---|
| K12 | 0 | 0 | 1 | 1 |
| cap-6 set | 0 | 0 | 0 | 0 |
| `rl_targets` | 0 | 0 | 0 | 1 |

## Lean re-check

I ran my own statement renderer and driver with `-DmaxErrors`, rejecting on any error or `sorry`. I checked one random counted proof per solved theorem.

| set | accepted / checked | term size: median (max) | ND lines: median (max) |
|---|---|---|---|
| C3 SN12 T1, literal | 1,165/1,165 | 47–50 (124) | 19–21 (47) |
| C3 K12 T1, literal | 151/151 | 34–35 (50) | 15 (20) |
| C4 best, literal | 410/410 | Fz 14–21, T1 17–38 (154) | 6–16 (64) |
| C4 ours, nd2lean render* | 330/330 | 21–53 (139) | 6–12 (28) |

\*The textbook72 run stored no literal text, so these proofs were rendered from the stored ND proofs with `nd2lean`.

**Term size** = tokens left after removing `: formula` ascriptions and layout tokens (have/exact/by/;/:=/parens/=>/,/⟩/fun). Names, including binders, count.

**Negative controls: 739/739 rejected.**
- Drop the returned `have`: 200.
- Swap h1↔h2: 139.
- Pair with another theorem: 200.
- Truncate to 60%: 200.

I also interleaved each control with a good proof. Every control failed with an error on its own lines. 7 good neighbours failed, all of them right after a truncated control: the cut-off text spills into the next proof. That can only cause false rejections, and the positive batches had no truncated input and no rejections. **The harness is valid.**

## Ratings

- **C3: holds with caveats.** The counts are exact and Lean-clean, and they survive re-reads. But the comparison is 4 vs 2 seeds with no replication, and it is inside the transplanted floor. The 2×2 interaction is not supported.
- **C4: solid, with caveats.** It is replicated on fresh seeds. It is not compute-matched (about 1.6–1.9× the GPU-seconds), and ours6 has only n = 2.
