# Review — run `kalmar-pretrain`

Reviewer: agent:claude (role reviewer), a separate session from the executor. Started 2026-10-20 09:32 UTC.
Kit: `review_kal/` (reviewer code; every number below is printed by a script there into `review_kal/out/`).

## §Recount (phase 1 — written before reading the executor's write-ups)

### What I read, and what I did not

- **Read:** the run brief (in the executor's command line), `preregistration/kalmar-pretrain.md` (main design plus
  Addenda 1–3), the code (`kalmar/*.py`, `pod/kal/*.sh`, the diffs to `state_env.py` / `state_train.py` /
  `state_train_best.py`, and `guided_eval.py`, `lean_gate.py`, `state_ladder_ei.py`), the data, and the raw artefacts:
  `artifacts/kalmar/{tf,free,eval,ladder,dump,ctl_stored,logs}`, the registry rows, and the checkpoints from the bucket.
- **Also read (disclosed):** `data/kalmar/README.md`. It is a data description written by the executor, with dataset
  statistics; I read it in phase 1 to learn the file formats. I recomputed its numbers myself and did not copy them.
- **Not opened in phase 1:**
  - `run_kalmar_pretrain*.md`, `numbers.md`, `log.md`, `STATUS.md`, `next_steps.md`;
  - `artifacts/kalmar/{analysis_stdout.txt, numbers_tables.md, summary.json, exploratory_stdout.txt, compute_stdout.txt,
    compute.json, ladder_stdout.txt, ladder_summary.json, gen_verdicts.txt, stats_k12_vs_kal.json, numbers_src/}`;
  - figures.
- **Snapshot:** after the executor's final commit `9c997fe8` (09:40 UTC), every raw artefact I counted from is
  byte-identical in the run worktree and in the phase-1 copy (1,146 files). The only differing files are two
  `numbers_src/*.md` write-up drafts, which I did not read.
- **Independence:** my code imports none of `kalmar/`, `lean_judge`, `gen` or `nd_verify`.
  - Builder: `kc.kalmar`, written from nd-rl `dan:code/tools/tt_prover.py` plus the pre-registered memo rule.
  - Lean harness: `rlean.py`, my own from earlier reviews, with Lean 4.34.1 (the pods' toolchain).
  - Project code used as infrastructure only:
    - `state_env.decompose`, to obtain the environment's canonical states and names;
    - `model.load_ckpt` and `sample.generate_ids_fast` (CPU), to re-run checkpoints;
    - `lean_check.check`, to measure the project's term size.

### Models (every number below names one of these)

All arms use the same network: the 9,560,832-parameter ALiBiGPT (6 × 384, `lean_staten`), trained from scratch with
`state_train.py --recipe best`, seeds 0 / 1 / 2. Metadata was read from the checkpoints themselves (`extra`).

| label | checkpoint | training |
|---|---|---|
| **control** | best-state `ckpts/bs/stage1_best12_s{0,1,2}_b1200.pt` (run's copy `ckpts/ctl/…`; s0 md5 `9c436c35…` matches the registry's `ckpt_md5`) | K12 `data/kh/train_k12.jsonl` (155,000 theorems, 1,239,995 pairs); 23,951 / 23,987 / 24,123 steps = 3.667 / 3.668 / 3.690 epochs of pairs; 1,200 A40-s |
| **KAL-C** | `ckpts/kalmar/stage1_kalC_s{0,1,2}.pt` | K12-Kalmár sl `data/kalmar/train_kal_sl.jsonl` (the same 155,000 theorems, 16,876,247 pairs); 24,020 steps = **0.135** epochs of pairs; RTX 3090 |
| **KAL-D** | `ckpts/kalmar/stage1_kalD_s{0,1,2}.pt` | K12-Kalmár sl; 656,285 steps = 3.675 × 178,581 batches per epoch (3.676 epochs); 36,885 s (s0) on RTX 3090; snapshots at steps 24,020 / 100k / 200k / 350k / 500k |
| **KAL-D+A** (Addendum 3, exploratory) | `ckpts/kalmar/anneal/kalDA_s{0,1,2}.pt` | KAL-D s fine-tuned for 600 steps: lr 3e-4 → 3e-5, 128 records per step, on `replay20k_s` (20,000 K12-Kalmár records, 2,180,885 pairs) |
| **EI r1 / r2** | `ckpts/kalmar/ladder/la_kal_ei_s0_r{1,2}.pt` | KAL-D s0 + 1 or 2 EI rounds (Addendum 1) |

### Hard constraints — all hold

- **`nd_verify` unmodified:** its tree hash `9437bb72…` is the same in `origin/main`, the base
  `origin/dan_create-or-elicit` and `HEAD`. The working copy has no diff, and no commit on the run branch touches it.
- **`artifacts/TEST_RUN_DONE` unchanged:** blob `1d5cf064…`, the same as in `origin/main`.
- **`nd_verify` judges nothing:**
  - The run's only `nd_verify` import is `state_env.py`'s `from nd_verify.verify import parse_formula`. That is a parser,
    pre-existing.
  - Every count goes through `lean_gate.gate`: Lean on the literal text, behind the reject-only `lean_prefilter`.
    `kal_free.py`, `guided_eval.py` and the ladder all use it.
- **No evaluation file is read by training code:**
  - Stage 1: `--data train_kal_sl`, and `--heldout val300_kal_sl` (the first 300 of tf1200). `state_train_best.train`
    uses the held-out set only for the logged validation-loss curve and `final_val`, and saves the last step. There is
    no selection and no early stopping.
  - Anneal: `make_replay.py` samples 20,000 records of `train_kal_sl`.
  - Ladder: the fine-tune mixes are the found proofs of `ei_targets1000` plus 20,000 replayed `train_kal_sl` records.
    Transfer (`ei_transfer200`) and `val300` are only read.
- **Gate 0 (pre-registration before the first pod):**
  - Pre-registration commit `84ae22cf`: 2026-10-19T01:44:06Z. First pod `kal-1`: 01:50:40Z. Pre-registered.
  - Addendum 1 (03:28:08Z) predates every ladder launch (13:10:40Z) and the end of KAL-D training (≈ 12:00Z).
  - Addendum 2 (13:10:57Z): the batch-1,024 relaunches it describes started 15–22 s earlier (KAL-D plain reads
    13:10:35–39Z; ladders 13:10:40–42Z). No read had finished, as stated, but the relaunch came first.
  - Addendum 3 (2026-10-20T00:11:14Z) is labelled exploratory and was written after the EI round-2 numbers it cites.
- **No QUARANTINE.**

### K12-Kalmár — rebuilt independently, Lean-valid, and it is the algorithm

- **Rebuild** (`review_kal/rebuild.py`):
  - My own construction gives an ND proof string identical to the stored `proof`, and per-action step tags identical
    to the stored `tags`, for **155,000 / 155,000** training records.
  - Likewise for every record of every read set, 0 mismatches: tf1200, val300, holdout250, rr600, ge17, long2,
    candidate_v0 / v1, batch3, hand_proved_14, G1 200, G2 240, G3 106.
  - The training file holds exactly K12's 155,000 theorems in K12's order.
  - My construction is what I take the brief and the pre-registration to describe:
    - the prover's `prove` / `split` cases;
    - X ∨ ¬X derived once per atom at the top (variant sl);
    - first false premise → ex falso;
    - memo: cite a formula already in scope;
    - R when a box's conclusion was found outside it.
- **Lean, with no run code at all** (`review_kal/lean_train.py`):
  - My builder → my ND→Lean renderer → my harness: **614 / 614** accepted (400 random training theorems plus 214
    read-set theorems).
  - Controls: Or.inl↔Or.inr flipped at every ORI line, 0 / 200 pass; proof paired with another theorem, 0 / 150 pass.
- **Lean on the canonical `lean_seq` text, `lean_check` (the project's free-form judge)** (`review_kal/termsize.py`):
  - **150 / 150** random records accepted.
  - Term size equals the stored `term_size` for 150 / 150; `lean_seq` token count equals the stored count for 150 / 150.
- **Teacher-forced verdicts re-derived on CPU** (`review_kal/tf_cpu.py`):
  - 16 tf1200 records (4 per atom count), 1,727 states, re-run in fp32 with my own name masking.
  - Stored verdicts reproduced: KAL-D s0 1,726 / 1,727, control s0 1,724, KAL-C s0 1,727, KAL-D+A s0 1,726.
  - Each mismatch is a single state, consistent with bf16-vs-fp32 near-ties.

**Dataset statistics** (all 155,000; `review_kal/rebuild.py`, `review_kal/stats.py`; term size from the 150-record
`lean_check` sample):

| per proof | K12 (its own proofs) | K12-Kalmár sl |
|---|---|---|
| ND lines, mean / p50 / p99 / max | 7.00 / 7 / 12 / 12 | 107.88 / 95 / 285 / 527 |
| state-env actions = lines + 1, mean / max | — | 108.88 / 528 |
| ND box depth, mean / max | — | 4.25 / 6 |
| atoms 0 / 1 / 2 / 3 / 4 (theorems) | 49 / 5,138 / 39,338 / 73,917 / 36,558 | same theorems |
| term size (lean_check inference nodes), 150-record sample mean (max) | 4.36 (11) | 88.86 |
| (state, action) pairs, total | 1,239,995 | 16,876,247 |
| pair tokens (state + action + eos), mean / total | 774.95 / 120.1 M | 21,120.6 / 3.274 B |
| longest state per proof, mean / max (tokens) | 104.5 / 386 | 229.3 / 655 |
| longest action, max (tokens) | 219 | 219 (an →I leaf step, `leaf:imp+A`, of record 93283) |
| largest canonical name, mean / max | 5.79 / 12 | 18.78 / 31 |
| canonical `lean_seq` tokens, mean / max | 126.8 / 467 | 1,755 / 15,691 |
| longest pair | 367 + 24 + eos = 392 (record 124962) | 513 + 219 + eos = 733 (record 93283) |
| pb variant (my builder), ND lines mean / p50 / p99 / max; pairs total | — | 150.64 / 131 / 384 / 626; 23,504,837 |

### E1 — teacher-forced agreement (tf1200; 137,984 states per model)

Recounted from the stored per-state verdict strings (re-derived on CPU above) with my own step types, depths and
positions (`review_kal/tf.py`). The totals equal the stored totals for all 29 models.

| model | s0 | s1 | s2 | worst type with ≥ 500 states | records fully agreeing |
|---|---|---|---|---|---|
| control | 0.2783 | 0.3024 | 0.2282 | ¬⊥ / ∨− ≈ 0.00 | 0 / 0 / 0 |
| KAL-C | 0.9384 | 0.9324 | 0.9339 | ∧+ 0.58–0.62 | 123 / 81 / 126 |
| KAL-D | **0.9460** | **0.9381** | **0.9500** | ∧+ 0.60 / 0.61 / 0.74 | 170 / 164 / 192 |
| KAL-D+A | 0.9875 | 0.9870 | 0.9879 | ∧+ 0.87 / ¬⊥ 0.89 / ¬⊥ 0.88 | 647 / 678 / 715 |
| EI r1 / r2 (s0) | 0.9870 / 0.9893 | | | ∧+ 0.87 / 0.90 | 637 / 687 |

- **KAL-D by step type** (s0 / s1 / s2):

  | step type | agreement |
  |---|---|
  | close | 0.997 / 0.986 / 0.994 |
  | lem | 0.999 / 0.991 / 0.999 |
  | efq | 0.986 / 0.982 / 0.984 |
  | split | 0.966 / 0.977 / 0.967 |
  | ¬(A→B) | 0.93 / 0.92 / 0.92 |
  | ∧− | 0.93 / 0.89 / 0.90 |
  | ∨− | 0.93 / 0.89 / 0.92 |
  | ¬¬A | 0.92 / 0.89 / 0.91 |
  | →I with A false | 0.90 / 0.89 / 0.89 |
  | →I with B true | 0.82 / 0.83 / 0.85 |
  | ∨+ | 0.72 / 0.71 / 0.79 |
  | ¬⊥ | 0.64 / 0.77 / 0.82 |
  | ∧+ | 0.60 / 0.61 / 0.74 |
  | premise lines | 0.87 / 0.93 / 0.94 |
- **By box depth** (KAL-D s0): 0.97 / 0.99 / 0.96 / 0.92 / 0.90 at depths 0–4, then 0.99 / 0.99 at depths 5–6. Not
  monotone.
- **By position decile** (KAL-D s0): 0.985 in the first decile, ≈ 0.93 through the middle, 0.959 in the last.
- **KAL-D snapshots** (s0 / s1 / s2):

  | step | agreement |
  |---|---|
  | 24,020 | 0.875 / 0.864 / 0.858 |
  | 100k | 0.871 / 0.878 / 0.881 |
  | 200k | 0.899 / 0.875 / 0.877 |
  | 350k | 0.908 / 0.912 / 0.906 |
  | 500k | 0.935 / 0.926 / 0.928 |
  | final | 0.946 / 0.938 / 0.950 |

  KAL-C (24,020 steps on its own complete schedule) reaches 0.932–0.938, about what KAL-D's snapshots reach at 500k
  steps (0.926–0.935).

### E2 / E3 — free generation on tf1200 (`review_kal/free.py`)

- **Exact-follow, my definition:** the Lean-accepted literal text equals the algorithm's canonical text with every name
  shifted by the attempt's base. The comparison first re-splits `n.elim` / `n.1` back into tokens.
- It equals the stored `follow` flag on **every row of all 195 free reads**. So do the action counts, the stored
  `dev_tag` / `dev_depth` against my tags, the first-deviation step of every accepted deviating attempt, and the
  solved counts.

**Greedy (k 1, T 0), success / exact-follow, all and by atom count:**

| model | all | 1 atom | 2 atoms | 3 atoms | 4 atoms |
|---|---|---|---|---|---|
| control s0 / s1 / s2 | 0.918 / 0.944 / 0.905 (follow 0) | 0.90 / 0.91 / 0.91 | 0.93 / 0.94 / 0.91 | 0.90 / 0.94 / 0.89 | 0.93 / 0.97 / 0.90 |
| KAL-C s0 | 0.269 / 0.102 | 0.32 / 0.13 | 0.31 / 0.14 | 0.27 / 0.11 | 0.20 / 0.05 |
| KAL-C s1 | 0.141 / 0.066 | 0.20 / 0.07 | 0.15 / 0.10 | 0.15 / 0.07 | 0.09 / 0.02 |
| KAL-C s2 | 0.223 / 0.106 | 0.25 / 0.13 | 0.26 / 0.14 | 0.21 / 0.11 | 0.19 / 0.06 |
| **KAL-D s0** | **0.331 / 0.141** | 0.49 / 0.19 | 0.39 / 0.20 | 0.29 / 0.14 | 0.24 / 0.07 |
| **KAL-D s1** | **0.291 / 0.137** | 0.31 / 0.17 | 0.34 / 0.17 | 0.29 / 0.14 | 0.24 / 0.08 |
| **KAL-D s2** | **0.356 / 0.163** | 0.31 / 0.08 | 0.39 / 0.22 | 0.40 / 0.20 | 0.31 / 0.11 |
| KAL-D+A s0 | 0.713 / 0.539 | 0.83 / 0.65 | 0.82 / 0.63 | 0.68 / 0.51 | 0.59 / 0.43 |
| KAL-D+A s1 | 0.743 / 0.565 | 0.81 / 0.63 | 0.83 / 0.64 | 0.72 / 0.58 | 0.65 / 0.45 |
| KAL-D+A s2 | 0.787 / 0.598 | 0.86 / 0.65 | 0.86 / 0.69 | 0.79 / 0.57 | 0.68 / 0.51 |
| EI r1 / r2 (s0) | 0.713 / 0.529; 0.757 / 0.572 | 0.85 / 0.66; 0.85 / 0.65 | 0.83 / 0.60; 0.85 / 0.66 | 0.67 / 0.52; 0.74 / 0.55 | 0.58 / 0.41; 0.64 / 0.47 |

- **KAL-D snapshots** (greedy success / exact-follow on tf1200, s0 / s1 / s2). These are mid-schedule checkpoints, so
  the learning rate is still high:

  | step | s0 | s1 | s2 |
  |---|---|---|---|
  | 24,020 | 0.065 / 0.010 | 0.062 / 0.018 | 0.070 / 0.015 |
  | 100k | 0.144 / 0.016 | 0.067 / 0.023 | 0.094 / 0.022 |
  | 200k | 0.110 / 0.029 | 0.127 / 0.018 | 0.059 / 0.008 |
  | 350k | 0.141 / 0.044 | 0.195 / 0.044 | 0.183 / 0.063 |
  | 500k | 0.230 / 0.125 | 0.253 / 0.053 | 0.208 / 0.096 |
  | final (656k) | 0.331 / 0.141 | 0.291 / 0.137 | 0.356 / 0.163 |
- **Valid deviations (KAL-D s0 / s1 / s2):**
  - 228 / 185 / 231 accepted deviating attempts. In actions, 134 / 118 / 158 are shorter than the algorithm's proof
    and 86 / 62 / 65 longer.
  - In term size (`lean_check`, `review_kal/termsize_dev.py`): 119 / 115 / 152 are smaller and 91 / 55 / 64 larger.
    Summed size is 0.98 / 0.91 / 0.93 of the algorithm's.
  - The control writes no exact-follow attempt. All its accepted proofs are shorter K12-style proofs.
- **First deviation of greedy KAL-D attempts** (stored, checked against my tags), most frequent algorithm step types:
  - s0: premise line 18 %, →I with B true 17 %, ∨+ 15 %, ∧+ 11 %;
  - s1: lem 18 %, ∨+ 17 %, →I with B true 14 %;
  - s2: →I with B true 16 %, ∨+ 15 %, ¬¬A 11 %.
- **E3, sampled (k 8, T 0.8) per attempt:**
  - KAL-D s0 / s1 / s2: success 0.183 / 0.138 / 0.164; exact-follow **0.068 / 0.060 / 0.062**; valid deviation
    0.115 / 0.078 / 0.102.
  - KAL-C: exact-follow 0.040 / 0.024 / 0.039.
  - Control: exact-follow 0.

### Pre-registered "learned the construction" — not met by any model

Criteria: (i) TF ≥ 99 % overall and ≥ 95 % on every step type with ≥ 500 states; (ii) greedy exact-follow ≥ 90 % on
1–2-atom theorems and ≥ 60 % on 4-atom theorems.

| model | (i) | (ii): exact-follow on 1–2 atoms / 4 atoms |
|---|---|---|
| KAL-D | fails on 3 / 3 seeds | 0.20 / 0.17 / 0.18 and 0.07 / 0.08 / 0.11; fails on 3 / 3 |
| KAL-C | fails on 3 / 3 | fails on 3 / 3 |
| KAL-D+A (Addendum 3's revision clause) | TF 0.987–0.988 < 0.99; worst type 0.87–0.89 | 0.64 / 0.64 / 0.68 and 0.43 / 0.45 / 0.51 |

By the pre-registered table, KAL-D is **not learned** (neither (i) nor (ii)), and so is KAL-D+A.

### E4 — solve rates (`review_kal/solve.py`)

Every row is internally consistent (`n_ok = Σ ok = Σ accepted counts`, accepted only on `done`). Solved counts equal
the stored summaries for all 28 eval reads. Settings:

- **Plain and guided (logical) reads:** k 32, T 0.8, `max_steps` 1,024, `max_action` 512, sampling seed 1.
  - Batch 2,048: control and KAL-C.
  - Batch 1,024: KAL-D and KAL-D+A (Addendum 2).
- **Control k 256 reads:**
  - New reads (batch 2,048, `max_steps` 1,024): ge17, the release sets, G1–G3.
  - Stored best-state reads (`max_steps` 96): holdout250, rr600, long2, textbook72.

Solved at k (s0 / s1 / s2):

| set | control plain k32 | KAL-C plain k32 | KAL-D plain k32 | KAL-D+A plain k32 | control guided k32 | KAL-C guided k32 | KAL-D guided k32 | control plain k256 |
|---|---|---|---|---|---|---|---|---|
| holdout250 | 165/170/160 | 24/19/11 | 35/24/41 | 133/130/146 | 194/205/196 | 44/52/28 | 53/58/66 | 184/195/182 |
| rr600 Q (L_true 13–16, 400) | 189/152/121 | 2/4/0 | 8/8/13 | 126/117/161 | 312/287/287 | 17/28/19 | 39/29/45 | 271/237/216 |
| ≥ 17 (ge17 70 + long2 21) | 17/16/13 | 1/0/0 | 0/0/2 | 34/28/40 | 58/52/48 | 6/6/2 | 8/4/10 | 35/27/23 |
| release, excluding the 5 four-premise problems (182) | 60/51/58 | 17/6/20 | 35/29/36 | 89/74/86 | 88/84/91 | 42/33/28 | 51/50/60 | 72/71/76 |
| hand_proved_14 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| textbook72 (scoring only) | 25/22/24 | 14/5/11 | 21/18/20 | 40/42/41 | 35/37/34 | 26/19/18 | 30/30/33 | 32/27/27 |
| G1 as is (200) | 0/11/26 | 7/5/6 | 35/15/17 | 65/48/61 | 3/21/50 | 25/38/24 | 54/40/35 | 1/13/30 |
| G2 (240) | 0/2/3 | 0/0/0 | 0/0/0 | 2/2/3 | 6/3/5 | 1/4/0 | 2/2/1 | 1/3/5 |
| G3 (106) | 12/9/19 | 14/7/4 | 19/18/17 | 52/58/59 | 16/12/19 | 22/23/7 | 29/34/26 | 17/14/20 |

- **The release's 5 four-premise problems** are solved by no model in any read, so "all 187" equals "182".
- **pass@1 on holdout250** (unbiased, from k 32):
  - KAL-D 0.024 / 0.012 / 0.027;
  - KAL-C 0.008 / 0.009 / 0.004;
  - KAL-D+A 0.246 / 0.261 / 0.310;
  - control 0.263 / 0.297 / 0.324 (from its stored k 256 rows: 0.273 / 0.305 / 0.324).
- **KAL-D pass@256 does not exist:** the pre-registered k 32 + 224 extension was not run (no read in `eval/`).
  KAL-D's pass@32 is far below the control's pass@32 on every in-distribution set, so the missing pass@256 cannot
  reverse a sign there.
- **Guided − plain at k 32** (holdout250, points of the set):
  - control +11.6 / +14.0 / +14.4;
  - KAL-C +8.0 / +13.2 / +6.8;
  - KAL-D +7.2 / +13.6 / +10.0.

  Guided ≥ plain in every arm × set × seed cell. The equal cells are hand_proved_14 (0 everywhere) and control s2
  on G3.
- **Batch-effect check (Addendum 2), plain k 32 at batch 2,048 vs 1,024:**
  - control s0: holdout250 165 / 166, rr600 Q 189 / 188, release 60 / 58, textbook72 25 / 28;
  - KAL-C s0: holdout250 24 / 18, release 17 / 21, textbook72 14 / 13.

  The re-draw spread is ≤ 6 theorems against arm differences of 120–145 on holdout250 and rr600.
- **Seed statistics.** With 3 seeds per arm the IQM is the mean. Arm difference, mean of 3, with a 95 % interval from
  resampling seeds:

  | comparison (plain pass@32) | difference | 95 % interval |
  |---|---|---|
  | KAL-D − control, holdout250 | −131.7 | [−141.0, −122.7] |
  | KAL-D − control, rr600 Q | −144.3 | [−179.3, −113.0] |
  | KAL-D − control, textbook72 | −4.0 | [−6, −2] (inside the pre-registered MDD of 9) |
  | KAL-D − control, G3 | +4.7 | [−0.7, +9.0] |
  | KAL-D+A − control, textbook72 | +17.3 | [+15.7, +19.0] |
  | KAL-D+A − control, G3 | +43.0 | [+37.3, +48.7] |
  | KAL-D+A − control, ≥ 17 | +18.7 | [+13.0, +24.7] |
  | KAL-D+A − control, G1 as is | +45.7 | [+31.3, +60.0] |
  | KAL-D+A − control, holdout250 | −28.7 | [−37.3, −19.0] |

  Greedy tf1200, KAL-D − control: −58.8 / −65.3 / −54.9 pp per seed.

### E5 — generalisation (`review_kal/gen.py`)

- **Construction checks (own code):**
  - **K12:** total sequent size p99 39, max 71; per formula max 65; formula depth ≤ 9; ≤ 3 premises.
  - **G1:**
    - 100 four-premise and 100 five-premise theorems.
    - Each is a `p2/heldout` theorem with 2–3 premises, with its premises and goal kept, plus distractors over its own
      atoms.
    - 200 / 200 valid and none in a K12 class.
  - **G2:**
    - 240 sequents: 80 per total-size bin (40–49 / 50–59 / 60–79), each bin and size equal to the stored values.
    - All are valid and have ≤ 3 premises.
    - All are above K12's p99 size; 26 are above its maximum.
    - None is in a K12 class.
  - **G3:** exactly the 106 names in `data/coe/sigma_heldout_strict.txt`; none in a K12 class.
- **Pre-registered rule, applied to KAL-D greedy.** KAL-D's greedy rate is divided by its tf1200 greedy rate weighted
  to the set's own atom mix:
  - ≥ 0.7 and above the control's pass@32 by more than the MDD → generalises;
  - < 0.3 → does not;
  - otherwise → partially.

| test | KAL-D greedy s0 / s1 / s2 | ratio to in-distribution | control pass@32 (same seed) | verdict s0 / s1 / s2 |
|---|---|---|---|---|
| G1(b) premise lines supplied | 0.105 / 0.050 / 0.105 | 0.34 / 0.17 / 0.28 | 0.920 / 0.885 / 0.955 | partially / does not / does not |
| G2 [40, 49] | 0 / 0 / 0 | 0 | 0 / 0.025 / 0.025 | does not ×3 |
| G2 [50, 59] | 0 / 0 / 0 | 0 | 0 / 0 / 0.013 | does not ×3 |
| G2 [60, 79] | 0 / 0 / 0 | 0 | 0 | does not ×3 |
| G3 | 0.104 / 0.085 / 0.113 | 0.33 / 0.29 / 0.31 | 0.11 / 0.08 / 0.18 | partially / does not / partially |
| hand_proved_14 | 0 / 0 / 0 | 0 | 0 | does not ×3 |
| ≥ 17 (91) | 0 / 0 / 0.022 | 0 / 0 / 0.06 | 0.19 / 0.18 / 0.14 | does not ×3 |

- The "partially" cells pass only the ratio leg. KAL-D's in-distribution rate is ≈ 0.3, so the ratio is weak. In each
  of them KAL-D is at or below the control.
- **G1(a), as is:**
  - greedy: KAL-D 0.055 / 0.035 / 0.040, control 0 / 0.03 / 0.085;
  - plain pass@32: KAL-D 35 / 15 / 17 of 200, control 0 / 11 / 26.
- **G1(b) pass@32** (T 0.8, premise lines supplied): control 184 / 177 / 191, KAL-D 38 / 30 / 41, KAL-C 24 / 39 / 21
  of 200.
- KAL-C and KAL-D+A under the same rule (`out/gen.json`):
  - KAL-C: "does not" everywhere except G1(b) "partially" on s0 / s1.
  - KAL-D+A: "partially" on G3 ×3, G1(b) s0 / s2 and ≥ 17 s2; "does not" elsewhere.

### Caps — did they truncate the comparison? (`review_kal/out/cutoffs.txt`, `trunc_bound.txt`)

- **Step cap (1,024 actions):** never reached in an eval read (the most steps any attempt took is 730). In the free
  reads, one row hit it (KAL-D s2, G2 greedy). The stored control reads (cap 96) record no step-cap reason.
- **Action cap (512 tokens):**
  - 340 (read × set) strata exceed the pre-registered 0.1 % action-truncation threshold. Examples:
    - control s1, G2: 14.3 %;
    - KAL-C s0, holdout250: 1.1 %;
    - control s0, holdout250: 0.81 %;
    - stored control s0, holdout250: 0.94 %.
  - The pre-registered rule was "re-read at 2× that cap". **No read at `max_action` 1,024 exists.**
  - Upper bound, if every truncated attempt had been a success (theorems with 0 successes and ≥ 1 truncated attempt):
    - KAL-D s0 / s1 / s2 holdout250: +24 / +87 / +68 (KAL-D would be ≤ 59 / 111 / 109, against the control's
      165 / 170 / 160);
    - KAL-D rr600 (all 600): +38 / +226 / +161;
    - G2, KAL-D: +92 / +138 / +116 of 240.
  - The algorithm's longest action is ≤ 305 tokens (G2) and ≤ 172 tokens elsewhere, and K12's is 219, so a truncated
    action is a runaway. A 2× re-read would settle it.
  - The in-distribution sign is safe on holdout250 even under the bound, but on rr600 and G2 the bound alone cannot
    exclude a change.

### Addendum 1 — the EI ladder from KAL-D s0 (`review_kal/ladder.py`)

Counted from the cumulative `found_<r>.jsonl`, which agree with each other round by round. "Exact" means the ND string
equals my algorithm proof. The EI arm stopped after round 3 sampling (no `round_3.json`); the frozen arm ran 4 rounds.

| arm, round | new distinct proofs | exact Kalmár | actions / algorithm's | shorter deviations | longer deviations | cumulative targets solved (of 1,000) |
|---|---|---|---|---|---|---|
| EI r1 (= frozen r1) | 313 | 0.201 | 0.994 | 0.396 | 0.329 | 135 |
| EI r2 | 2,029 | 0.139 | 0.997 | 0.412 | 0.395 | 576 |
| EI r3 | 2,100 | 0.035 | 0.994 | 0.430 | 0.487 | 673 |
| frozen r2 | 213 | 0.075 | 0.990 | 0.432 | 0.404 | 164 |
| frozen r3 | 198 | 0.081 | 1.003 | 0.404 | 0.429 | 183 |
| frozen r4 | 154 | 0.026 | 1.004 | 0.416 | 0.481 | 188 |

- **Per-round reads** (`round_<r>.json`):
  - targets solved this round: 135 (KAL-D s0) → 572 (EI r1 model);
  - held-out greedy (`val300`): 0.290 → 0.717;
  - transfer greedy: 0.070 → 0.335;
  - the frozen arm stays at 0.290 / 0.070.
- **After the ladder:**
  - EI r1 / r2 TF agreement is 0.9870 / 0.9893, against KAL-D s0's 0.9460.
  - Greedy exact-follow is 0.529 / 0.572, against 0.141.
  - Round 8 was not reached.

### Addendum 3 — anneal control

- **KAL-D+A s0, targets** (k 16, sampling seed 2, `eval/kalDA_s0_targets_k16`): **578 / 1,000**.
  - EI round 2 (EI r1 model, seed 2) solved 572.
  - The base re-read at the same settings (`kalD_s0_targets_k16`) solved 133.
- **Held-out greedy (`val300`):**
  - KAL-D+A s0 / s1 / s2: 0.707 / 0.720 / 0.763;
  - EI r1: 0.717.
- **On tf1200:**
  - TF agreement: KAL-D+A 0.9875 / 0.9870 / 0.9879, EI r1 0.9870.
  - Greedy success: 0.713 / 0.743 / 0.787 against EI r1's 0.713.
- KAL-D+A s0 is within 1.5 % of EI r1 on every one of these.
- **Confound to weigh in phase 2.** The anneal is not only a learning-rate change: 600 steps × 128 records ≈ 76,800
  records, about 0.5 epoch of K12-Kalmár records. In the registry it is 1.63 B training tokens per seed, against 12.03 B
  for KAL-D (+13.5 %).

### Compute (`review_kal/compute.py`, the run's registry: 1,413 rows)

| arm | GPU-hours (registry) | GPU | training steps | training tokens | generated tokens (reads) | Lean checks |
|---|---|---|---|---|---|---|
| KAL-D training | 30.36 | RTX 3090 | 1,968,855 (3 × 656,285) | 36.09 B | — | — |
| KAL-C training | 1.35 | RTX 3090 | 72,060 (3 × 24,020) | 1.32 B | — | — |
| KAL-D+A training | 8.72 | A40 5.98 + 3090 2.74 | 1,800 | 4.88 B | — | — |
| EI fine-tune children | 6.07 | A40 | 1,200 | 3.28 B | — | — |
| control reads | 3.25 | A40 2.91 + 3090 0.34 | — | — | 219 M | 101,430 |
| KAL-C reads | 8.65 | A40 7.82 + 3090 0.84 | — | — | 414 M | 7,764 |
| KAL-D reads | 12.93 | A40 10.84 + 3090 2.09 | — | — | 560 M | 18,987 |
| KAL-D+A reads | 8.66 | A40 8.29 + 3090 0.37 | — | — | 382 M | 31,055 |
| frozen ladder | 2.02 | A40 | — | — | 69 M | 2,151 |
| EI ladder sampling | 0.09 (gap) | A40 | — | — | 3.9 M | 0 |

- The control's own training (1,200 A40-s per seed) belongs to best-state, not this registry.
- **Registry gaps.** The EI ladder's sampling rows are almost absent:
  - 0.09 GPU-h and 16,000 attempts are recorded;
  - its rounds took 13,001 s and 15,065 s (`round_<r>.json` `secs`), 3 rounds in all.

  Per policy, the ladder's per-round compute must therefore come from logs.
- **Training compute:** KAL-D uses 27.3× the control's steps (656,285 against 24,020) at the same per-step token
  budget. This is flagged > 1.25× by design.

### Splits (`review_kal/splits.py`; own premise-order-invariant renaming-class key, also with premises as a set)

- **K12 / K12-Kalmár against each pool:** 0 theorems from tf1200, val300, holdout250, rr600, ge17, long2, candidate_v1,
  batch3, hand_proved_14, G1, G2, G3 and ei_transfer200 fall in a K12 class.
  - candidate_v0 has 1 (`textbook_9d21fccc…`).
  - textbook72 has 1 (`textbook_3ed45280…`, the known premise-swapped twin noted in the capability-defs review).
  - These are two different classes, both inherited with the sets.
- **EI targets (`ei_targets1000`, trained on by EI) against every pool:** 0.
- The anneal replay sets are subsets of the training file.

### Lean re-check of counted proofs (`review_kal/recheck.py`; literal stored text, Lean 4.34.1, axioms ⊆ {propext, Classical.choice, Quot.sound})

- **Counted proofs:** 150 per group, reservoir-sampled from every eval row's `accepted` texts and every valid free-read
  text. **All 1,050 accepted.**

  | group | pool of distinct counted texts | accepted |
  |---|---|---|
  | control | 101,157 | 150 / 150 |
  | KAL-C | 7,854 | 150 / 150 |
  | KAL-D | 18,661 | 150 / 150 |
  | KAL-D+A | 31,164 | 150 / 150 |
  | EI r1 / r2 greedy | 1,978 | 150 / 150 |
  | EI ladder dump | 22,518 | 150 / 150 |
  | frozen ladder dump | 2,829 | 150 / 150 |

- **Controls, run first in the same harness:**

  | control | passed |
  |---|---|
  | first Or.inl↔Or.inr flipped | 1 / 266 (a benign no-op) |
  | text paired with another theorem of the same premise count | 0 / 200 |
  | `exact sorry` | 0 / 30 (`sorryAx`) |
  | texts the run's prefilter rejected before Lean (ladder dumps) | **0 / 300** (pool 44,597): no filter false rejects in the sample |

### textbook72 hygiene (`review_kal/hygiene.py`; every sequent span keyed by renaming class; conclusions of ≥ 7 nodes searched literally)

- **No textbook72 sequent appears in any artefact, data file, log or the pre-registration**, apart from these:
  - **By design:** the 26 eval-row files of the scoring reads, and the control's copied stored best-state reads
    `ctl_stored/Fz_best12_s*__tb72.jsonl` (all 72 prompts).
  - **Code fixtures:** 5 textbook72 renaming classes occur as hand-written examples, 6 times in all: the default
    example of `kalmar/kalmar.py` and 5 fixtures in `kalmar/test_kalmar.py`. These are textbook-standard sequents in tests, a hygiene
    note rather than a leak; `data/bs/textbook72.jsonl` is itself public in the fork.
  - **Literal conclusion matches** in other sets' proofs: formulas of 7–10 nodes that also occur as a subformula. These
    are not sequents.
- `data/kalmar/textbook72_kal_sl.jsonl` holds lengths and hashed names only.

### Pre-registered expectations against my values (per seed unless stated)

| expectation | my value | |
|---|---|---|
| E1 KAL-D TF ≥ 99.5 %, ≥ 98 % on every type with ≥ 500 states | 94.6 / 93.8 / 95.0 %; ∧+ 0.60–0.74 | miss |
| E1 lowest types: ex-falso decision, ∨+ disjunct, ∧− conjunct | lowest are ∧+, ¬⊥, ∨+ and →I with B true; efq is 0.98 | partial (∨+ only) |
| E1 KAL-C 97–99.5 % | 93.2–93.8 % | miss |
| E1 control ≤ 40 % | 22.8–30.2 % | hit |
| E2 KAL-D greedy 1 / 2 / 3 / 4 atoms ≥ 98 / 95 / 90 / 75 % | 0.31–0.49 / 0.34–0.39 / 0.29–0.40 / 0.24–0.31 | miss |
| E2 exact-follow within 5 points of success | gaps 15–19 points overall | miss |
| E2 KAL-C 1–2 atoms 80–95 %, 3 atoms 50–80 %, 4 atoms 20–60 % | 0.15–0.32; 0.15–0.27; 0.09–0.20 | miss (4 atoms 2 / 3 seeds below 20 %) |
| E2 control on tf1200 0.90–0.95 | 0.918 / 0.944 / 0.905 | hit |
| E3 KAL-D exact-follow ≥ 60 % of T 0.8 attempts | 6.0–6.8 % | miss |
| E4 holdout250 KAL-D pass@256 ≥ 235; control 187 (184 / 195 / 182) | KAL-D pass@32 24–41 (pass@256 not run); control stored 184 / 195 / 182 | miss (control value reproduces) |
| E4 rr600 Q KAL-D ≥ 350 / 380; control 241 (271 / 237 / 216) | KAL-D pass@32 8–13 of 400; control 271 / 237 / 216 | miss (the Q stratum has 400 theorems, not 380) |
| E4 ≥ 17 KAL-D ≥ 80 / 91; control long2 10 / 5 / 4 | KAL-D 0 / 0 / 2 at k 32; control long2 10 / 5 / 4 | miss (control value reproduces) |
| E4 release (182) KAL-D ≥ 160; hand_proved_14 KAL-D ≥ 10, control 0 | 35 / 29 / 36; hand_proved_14 0 everywhere | miss; control 0 holds |
| E4 textbook72 KAL-D ≥ 60; control 28.7 (32 / 27 / 27) | 21 / 18 / 20 at k 32; control 32 / 27 / 27 | miss |
| E4 pass@1 holdout250 KAL-D ≥ 0.75; control 0.3–0.5 | 0.012–0.027; control 0.27–0.32 | miss; control in range on 2 of 3 seeds (0.273 below) |
| E4 KAL-C below control on holdout250 pass@32, above on hand_proved_14 | below (11–24 vs 160–170); hand_proved_14 0 = 0 | hit / miss |
| E4 guided ≥ plain; KAL-D gain ≤ 3 points; control 3–9 points | ≥ everywhere; KAL-D +7.2 / +13.6 / +10.0; control +11.6 / +14.0 / +14.4 (holdout250) | hit / miss / miss |
| E5 G1(a) ≤ 5 % both arms | KAL-D greedy 5.5 / 3.5 / 4.0 %; control greedy 0 / 3 / 8.5 %; pass@32 KAL-D 17.5 / 7.5 / 8.5 %, control 0 / 5.5 / 13 % | greedy: hit on 4 of 6 cells; pass@32: miss on 4 of 6 |
| E5 G1(b) KAL-D greedy ≥ 60 %; control pass@32 ≤ 20 % | 10.5 / 5.0 / 10.5 %; control 92 / 89 / 96 % | miss / miss |
| E5 G2 KAL-D greedy ≥ 60 / 40 / 20 % per bin; control pass@32 ≤ KAL-D's | 0 in every bin; control 0–3 / 240 at k 32, KAL-D 0 | miss / miss on s1, s2 |
| E5 G3 KAL-D pass@32 ≥ 90; control pass@256 ≤ 30 | 19 / 18 / 17; control 17 / 14 / 20 | miss / hit |
| Add. 1 round 1 ≥ 90 % of targets | 13.5 % | miss |
| Add. 1 exact share ≥ 70 % in r1, within ±15 points thereafter | 20.1 → 13.9 → 3.5 % | miss |
| Add. 1 actions per accepted proof within ±10 % | 0.99–1.00 | hit |
| Add. 1 EI cumulative − frozen ≤ 3 points | +49.0 points at r3 (673 vs 183) | miss |
| Add. 1 after r8: TF ≥ base − 1 point, exact-follow ≥ base − 5 points | r8 not reached; at r2: +4.3 and +43 points | not testable at r8; went up, not down |
| Add. 3 "annealing explains the jump" (KAL-D+A within ≈ 10 % of EI r1) | targets 578 vs 572; val300 greedy 0.707 vs 0.717 | holds as read (but see the confound) |

### Not derivable from the stored files

- **First-deviation step types for rejected attempts:** no text is stored for them. The stored `dev_*` fields are
  consistent with my tags on every row.
- **The pre-registration's "0 attempts reached 90 steps" in the stored control reads:** those rows hold no per-attempt
  steps. There is no step-cap reason and no accepted proof near 96 lines.
- **KAL-D pass@256:** not run.

*(§Recount committed before I opened `run_kalmar_pretrain.md`, `numbers.md` or `log.md`.)*
