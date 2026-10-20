#### EI ladder from KAL-D s0 (pre-registered Addendum 1; `kalmar/ladder_analysis.py` → `artifacts/kalmar/ladder_summary.json`, `artifacts/kalmar/ladder_stdout.txt`)

**Protocol.** Addendum 1, at batch 1,024 (Addendum 2).
- Rounds: cut to 4 by the cost rule (log 14:30, 10-19). The EI arm then stopped after round 3's sampling, before its
  fine-tune (budget; log 01:15, 10-20).
- The EI process died once, in round 2's fine-tune (kal-12 restart, log 22:09). It resumed from round 1's checkpoint;
  round 2 was re-sampled with the same seed and gave identical counts.
- Frozen = KAL-D s0 with the same seeds and attempts, no training.
- Each round: k 16 at T 0.8 on the 1,000 targets; held-out greedy on `val300`.

| round | EI: targets solved this round / cumulative | frozen: this round / cumulative | EI held-out greedy (val300) |
|---|---|---|---|
| 1 (model KAL-D s0) | 135 / 135 | 135 / 135 | 87 / 300 |
| 2 (EI r1) | 572 / 576 | 138 / 164 | 215 / 300 |
| 3 (EI r2) | 668 / 673 | 146 / 183 | 223 / 300 |
| 4 | — | 119 / 188 | — |

Frozen held-out greedy: 87 / 300 every round. Round 3's EI numbers are from the log (its `round_3.json` is written
after the fine-tune, which did not run).

**New distinct Lean-accepted proofs per round** (`found_<r>.jsonl`; a proof counts in the round that first found it).
- Exact = the algorithm's ND proof, token for token. All 419 exact proofs in the EI arm's found files, and all 99 in
  the frozen arm's, have `written` equal to the algorithm's line count. So the shorter / longer columns compare like
  with like.
- Deduplication bias: a theorem's exact proof is new only once, so the exact share falls with the round.

LADDER_TABLES

**After the ladder** (greedy reads on tf1200; source `artifacts/kalmar/{tf,free}/la_kal_ei_s0_r{1,2}__*`):
- EI r1: TF 98.7 %, valid 71.2 %, exactly Kalmár 52.9 %.
- EI r2: TF 98.9 %, valid 75.7 %, exactly Kalmár 57.2 %.
- KAL-D s0, the base: 94.6 / 33.1 / 14.1 %.
- Greedy, EI follows the algorithm more than its base did, and TF agreement rose.

**Pre-registered ladder verdicts** (Addendum 1; criteria set for round 8, applied at round 3, the last round run).

| criterion | EI, round 3 | frozen, round 4 | verdict |
|---|---|---|---|
| keeps the algorithm: ≥ 50 % of new proofs exact, and TF fallen ≤ 1 point | 3.5 % exact; TF +4.3 pp (r2 vs base) | 2.6 % exact | **not met** |
| finds shorter proofs: mean ≥ 15 % below the algorithm's, or ≥ 30 % shorter deviations | mean −0.6 %; 43.0 % shorter | mean +0.4 %; 41.6 % shorter | **met** (share clause) |

- Frozen sampling of the untrained base meets "finds shorter proofs" equally, and so does round 1 (39.6 %). So both
  verdicts describe T 0.8 sampling from KAL-D plus the deduplication bias, not something EI did.
- Expectations: round 1 solves ≥ 90 % of targets (13.5 %, miss); exact share ≥ 70 % in round 1 (20.1 %, miss);
  actions per accepted proof within ±10 % of the algorithm's (written lines −0.3 to −0.6 %, hit); TF ≥ base − 1 and greedy
  exact-follow ≥ base − 5 after the ladder (+4.3 / +43.1 pp, hit); EI's cumulative solved exceeds frozen's by ≤ 3
  points (673 vs 183 at round 3, +49 points, miss).
- The size of the gain is not RL's (next section).

#### Exploratory, NOT pre-registered (Addendum 3): the replay-only fine-tune (`kalmar/exploratory.py` → `artifacts/kalmar/exploratory_stdout.txt`)

**KAL-D+A s0–s2.**
- Construction: KAL-D plus exactly the ladder's fine-tune command, without EI proofs. That is `state_train.py --init
  <KAL-D> --steps 600 --lr 3e-4 --min_lr 3e-5 --warmup 50 --recs 128`, on 20,000 K12-Kalmár records drawn with
  `random.Random(seed)`.
- Checkpoints: `ckpts/kalmar/anneal/kalDA_s{0,1,2}.pt`, md5 4516a1f5 / a2ee6578 / cbf7a110.
- Training hardware: s0 and s2 on A40s, s1 on an RTX 3090; 9,881–10,800 GPU-s each.
- Reads:
  - greedy and teacher-forced at batch 1,024;
  - targets with `guided_eval.py --arm plain --k 16 --seed 2` (round 2's seed);
  - plain k 32 at batch 1,024 (KAL-D's protocol; the control's reads are at 2,048, see the batch-effect check).

**What the fine-tune changes, all at once** (not separated by this run):

| | KAL-D pretraining (best recipe) | the fine-tune (ladder's command) |
|---|---|---|
| optimizer | Muon on the matrices + AdamW (lr 1e-3 → floor 3e-4), MTP 0.3 | AdamW on every weight, lr 3e-4 → 3e-5, no MTP |
| batch | 18,432-token budget batches | 128 whole proofs, ≈ 2.71 M tokens (≈ 150×) |
| tokens per seed | 12.03 B (656,285 steps) | 1.63 B (600 steps; 13.5 % of KAL-D's) |

More tokens alone explain little. KAL-D was still improving at its end: its last 156,285 steps (2.86 B tokens) added
+1.5 pp TF and +9.6 pp greedy validity. The fine-tune's 1.63 B added +4.3 pp and +42.1 pp (means of 3 seeds).

EXPLORATORY_TABLES

Notes:
- KAL-D s0's val300 greedy is 87 / 300 = 29.0 % (the ladder's round-1 held-out greedy, the same read). EI r2's is
  223 / 300 = 74.3 % (the ladder's round 3).
- The greedy suite reads all ran at batch 1,024 for every arm.
- MDD = 3.04 × the pooled per-seed sd (n = 3 per arm).
- Plain k 32 of KAL-D+A: batch 1,024 on A40s; S1_SECS s per seed (s0 / s1 / s2).
  KAL-D's took 3,900–4,200 s.
- The control's reads are at batch 2,048. In the batch-effect check, that moved one checkpoint's pass@32 by ≤ 6
  theorems per set (KAL-C s0, control s0).
- Beyond the MDD: the control leads on holdout250 (−28.7). KAL-D+A leads on ge17, long2, candidate_v0, textbook72,
  G1 as is and G3; the textbook72 and G3 gaps (+17.3, +43.0) are also far beyond the batch effect. Exploratory, one
  fine-tune recipe, NOT pre-registered.
