# Review: evidence-atlas

Reviewer: agent:claude, role reviewer. This session is separate from the executor's. Phase 1 was done in
`~/review/evidence-atlas`, which has the executor's `run*.md`, `numbers.md` and `STATUS*.md` removed. I did not open
`atlas/ATLAS.md`, `atlas/MAP.md` or `atlas/raw/*_notes.md` before committing this section; they are also executor
write-ups. Scripts and outputs are in `review_ea/`.

## §Recount (phase 1, written before reading the executor's write-up)

### What the run is

The run synthesizes across experiments: an experiment map, harmonized tables and figures, a protocol table, and a
create-vs-elicit table. Its one new measurement is the whole-proof re-score in pre-registration Addendum 1. That
re-score covers eight existing checkpoints. All are 3.2 M parameters (4 × 256), `lean_seq`, from scratch, judged by
Lean alone:
- **C0 frozen:** `lean-format` `stage1_a1_seq_s{0,1}`, trained on the cap-6 control set (`train_depth3_f0_a1`, 155k).
- **C0 T1:** `ds-generator` `la_T1_c0_s{0,1}_r8` (ladder, 8 × 32 on `rl_targets`, replay of the cap-6 set).
- **K12 frozen:** `cap-horizon` `stage1_k12_s{0,1}` (`train_k12`, cap 12, 155k).
- **K12 T1:** `state-cap12` `la_T1_K12_s{0,1}_r8` (ladder 8 × 32, replay of K12).

I confirmed the T1 provenance from `artifacts/dsg/la_T1_c0_s0/args.json` (ds-generator) and `pod/sc12/k12_t1.sh`
(state-cap12). The pools are textbook72 (k 256), dev1108 (k 64) and holdout250 (k 256), at T 0.8 and sample seed 0.

### Hard constraints: all pass

| check | result |
|---|---|
| `nd_verify` unmodified | blob `9437bb72…` is identical at `origin/main` and `HEAD` |
| `nd_verify` used as a judge | No. The re-score goes through `eval_set.py` → `lean_judge.judge_many`: a strict-grammar marker, then `nd2lean.translate`, then Lean. `eval_set.py`, `lean_judge.py`, `nd2lean.py`, `sample.py`, `lean_gate.py` and `model.py` have no diff against `origin/dan`. In `atlas/scripts`, `nd_verify` appears only as a label in checker-class strings. |
| `artifacts/TEST_RUN_DONE` | No diff against `origin/main` or `origin/dan`. No test-file run. |
| evaluation files read in training code | No training in this run. The only new code is `atlas/scripts/*`: analysis, plus the `rescore.py` wrapper, which only sets `max_new` and records stop counts. |

### Re-score recount (`review_ea/recount.py`; own counter: solved iff the row stores ≥ 1 accepted proof)

Checks on all 24 final reads (`artifacts/atlas/eval/`):
- prompts are identical, in order, to `data/bs/{textbook72,dev1108,holdout250}.jsonl`;
- `n_tried` = k for every row;
- `solved` agrees with the stored proofs, and my count equals the summary `.json`;
- args are k 256/64/256, T 0.8, seed 0, **batch 2,048**, `max_new` 512;
- peak memory is 8.0–8.4 GB per job;
- rows = 153,344 per checkpoint (72·256 + 1108·64 + 250·256).

Solved counts per seed (s0, s1):

| model (3.2M lean_seq, scratch, Lean alone) | textbook72 /72 | holdout250 /250 | dev1108 /1108 |
|---|---|---|---|
| C0 frozen | 12, 11 | 15, 8 | 54, 36 |
| C0 T1 | 15, 13 | 104, 102 | 417, 465 |
| K12 frozen | 21, 21 | 115, 104 | 415, 384 |
| K12 T1 | 25, 22 | 181, 177 | 797, 771 |

Against the Addendum 1 expected ranges, 6 of 12 cells are inside the range in both seeds. The misses:
- **C0 frozen:** holdout250 (expected 30–90, got 15, 8) and dev1108 (expected 100–400, got 54, 36), far below.
- **K12 frozen:** holdout250 (expected 120–190, got 115, 104) and dev1108 (expected 450–750, got 415, 384), below.
- **K12 T1:** textbook72 s1 (expected 25–38, got 22).

C0 frozen textbook72 (12, 11) and K12 T1 textbook72 s0 (25) sit on the edge of their ranges.

**Batch deviation.** The pre-registration says batch 4,096. Every final read used 2,048, the same for all arms; the job
script notes that 4,096 OOMs with two jobs packed per card. Eleven earlier reads at 4,096 are kept in
`artifacts/atlas/b4096_partial/`. Re-drawing at the other batch changed per-theorem results as follows:

| read | at 2,048 | at 4,096 |
|---|---|---|
| K12 frozen textbook72, s0 / s1 | 21 / 21 | 17 / 18 |
| C0 T1 dev1108, s0 / s1 | 417 / 465 | 424 / 460 |

Most other reads moved by 0–3 theorems. So a sampling re-draw alone moves textbook72 by up to 4 of 72.

**Truncation (`max_new` 512).** 11 of 24 reads have more than 0.1 % of samples at the cap. The worst is 0.258 %
(K12 frozen s1, holdout250). Pre-registration statement (iii), "< 0.1 %", is a **miss** for these reads. All 11 were
re-read at `max_new` 1,024 with the same batch and seed (`eval_mn1024/`). The solved count and the solved set were
identical in all 11 (0 theorems gained or lost).

At 1,024, 4 reads are still above 0.1 %: C0 frozen s0 dev 0.107 %, C0 frozen s0 textbook72 0.190 %, C0 T1 s0
textbook72 0.233 %, and K12 frozen s0 textbook72 0.130 %. Accepted proofs are at most 18 lines, far below 512 tokens.
That pattern points to non-terminating degenerate samples rather than long proofs being cut off. The cap does not bias
these counts.

### Lean re-check (`review_ea/lean_recheck.py`)

**Method.**
- **Header:** I render the theorem statement myself from the pool prompt with my own formula parser. It is not taken
  from `nd2lean`.
- **Body:** this comes from the unmodified `nd2lean.translate(require_all_pr=False)`, the same ND→Lean step the judge
  uses.
- **Lean check:** my own batching harness on Lean 4.34. Any error inside a theorem's span rejects it, and any `sorry`
  rejects it.
- **Sample:** one random stored proof per solved (read, theorem) for all 24 reads, which re-derives every solved
  count; plus every stored proof of both C0-frozen checkpoints. Total 4,356 proofs.

**Results.**

| checkpoint | checked | Lean-rejected |
|---|---|---|
| c0fz s0 / s1 | 121 / 86 (all stored proofs) | 0 / 0 |
| c0t1 s0 / s1 | 536 / 580 | 0 / 0 |
| k12fz s0 / s1 | 551 / 509 | 0 / 0 |
| k12t1 s0 / s1 | 1,003 / 970 | 0 / 0 |

Every per-read solved count is re-derived exactly from Lean-confirmed proofs. C0 frozen has fewer than 100 stored
proofs per checkpoint (121 and 86), so all of them were checked.

**Negative controls (600 random positives each).**
- (A) same body, goal replaced by `False`: **0/600 accepted**.
- (B) same body checked against a different theorem from the same read: **0/600 accepted**.

So the harness does reject.

One limit: the stored text is the decoded ND string, not the literal `lean_seq` token text. The strict-grammar step can
only be confirmed indirectly, because every stored proof is translatable. This limitation is inherited from
`eval_set.py`.

**Line counts and term size** (my definition: rule nodes + hypothesis/binder leaves, AS = PR = 1, R transparent), on
the Lean-confirmed sample:

| | median lines | max lines | median size | max size |
|---|---|---|---|---|
| C0 frozen | 8 | 11 | 8–9 | 11 |
| C0 T1 | 9 | 13 | 9–10 | 23 |
| K12 frozen | 9 | 16 | 10 | 35 |
| K12 T1 | 10 | 18 | 10–11 | 44 |

Full table in `review_ea/lean_recheck.json`.

### Split disjointness by renaming class (`review_ea/splits.py`)

My key is the minimum, over all atom permutations, of (sorted set of premises, goal). It is invariant to renaming and
to premise order.

| training file ∩ pool | textbook72 | dev1108 | holdout250 |
|---|---|---|---|
| C0 Stage-1 `train_depth3_f0_a1` (155k) | 0 | 0 | 0 |
| K12 Stage-1 `train_k12` (155k) | **1** | 0 | 0 |
| ladder `rl_targets` (4,495; the T1 RL targets) | 0 | 0 | 0 |

The three pools are pairwise disjoint. The one overlap is `textbook_3ed45280e6c686e76ac6`,
`(P v Q) , ~P ⊢ Q` (disjunctive syllogism), which is in `train_k12` with its premises in the opposite order. All four
K12 checkpoints solve it (n_ok 11, 16, 66, 195) and no C0 checkpoint does. **K12 textbook72 counts include one
training-set theorem**, and so do all cap-12 families scored on textbook72 from `train_k12` (SN-cap12, best-cap12).
In `ladder_ei.py`, transfer and dev-type samples are evaluation-only: only `found` on the targets enters training.

**Robbie's factorial: 14 of the 72 textbook72 theorems have `split = train`** in `passk.csv`, and `data/bs/textbook72`
labels them `role: rl_train`. They are RL training targets for those cells, so Robbie's textbook72 numbers are not
held-out on 14 of 72 theorems. The fork's T1 ladders never train on textbook72.

### Inputs to the pre-registered comparisons, recomputed from per-theorem files

**Proof-state comparators on textbook72.** Recounted from `hf://…/textbook72/artifacts/textbook72/eval/*.jsonl`; same
72 prompts as `data/bs/textbook72`; k 256, T 0.8, seed 0, batch 4,096, `max_action` 512, `max_steps` 96.

| model | per seed |
|---|---|
| SN-v2 cap 6 frozen | 16, 14 |
| SN-v2 cap 6 T1 | 22, 16 |
| SN-cap12 frozen | 26, 29, 32, 26 |
| SN-cap12 T1 | 37, 38, 36, 38 |

**Proof-state comparators on holdout250** (best-state summaries on `origin/dan_best-state`):

| model | per seed |
|---|---|
| SN6 frozen | 103, 83 |
| SN6 T1 | 169, 151 |
| SN12 frozen | 183, 188, 198, 185 |
| SN12 T1 | 217, 221, 223, 219 |

**Statement (i): whole-proof below proof-state at matched cap and stage.**
- **holdout250:** holds in 4 of 4 cells, all by large margins (≥ 70 theorems).
- **textbook72:** the direction holds in 4 of 4 cells. The mean differences are:

  | cell | whole-proof vs state | difference |
  |---|---|---|
  | C0 frozen vs SN6 frozen | 11.5 vs 15 | 3.5 |
  | C0 T1 vs SN6 T1 | 14 vs 19 | 5 |
  | K12 frozen vs SN12 frozen | 21 vs 28.25 | 7.25 |
  | K12 T1 vs SN12 T1 | 23.5 vs 37.25 | 13.75 |

  The pre-registration reads per-cell differences under ≈ 7 as inside the floor. By that rule only the cap-12 cells
  (one of them at the edge) are outside it on textbook72.

**Statement (ii): C0 T1 above Robbie's `lean-naive-ei`.** Robbie's values, recounted from per-problem `n_ok`, are
textbook72 8, 6, 10 and holdout250 45, 42, 37 (3 seeds). C0 T1 is 15, 13 and 104, 102, so (ii) holds on both pools.
- The checkers differ: Robbie's cells are Lean gate ∧ `nd_verify` (`f_recompute.py` `ROBBIE_JUDGE`), the fork reads
  are Lean alone.
- On textbook72, Robbie's cells trained on 14 of the 72 theorems.

Both differences favour Robbie's cells, so the direction stands a fortiori. The model size of Robbie's cells was not
checked here.

**Expectation 2: "highest textbook72 pass@k on file is best-cap12 T1 (≈ 52/72)".**
- best-state's T1 best-cap12 reads (9.56 M, `lean_staten`, scratch, K12) are 52, 51, 52, with `_cap` re-reads at 53.
- The atlas's own harmonized table has higher values. `trajectory` `la_T1_best12_s2_r6` reads **57/72** at k 256,
  Lean alone. I recounted it from `hf://…/trajectory/artifacts/tj/eval/s2_r6__tb72_x0.jsonl`: 57 of 72 with ≥ 1
  stored proof, n_tried 256.
- The same model's second read (`_x1`) is 56. Several intermediate rounds of seed 2 read 54–57.

So **the highest textbook72 value on file is 57 (best-cap12 ladder, seed 2, round 6), not ≈ 52**. That is the same
family at an intermediate round and a different seed. Best-cap12 T1 at round 8 is 51–53.

No Robbie factorial cell exceeds 32 (`lean-best-leon`: 32, 30, 32). I did not recount the autoresearch rows (one per
config).

**Fraction of families with matched protocol.** In the harmonized textbook72 table, 7 of 201 families have a
k 256, Lean-alone row. Most families are single autoresearch configs scored under Lean ∧ `nd_verify`. Statement 2's
"fewer than half of the families at the same k and checker" holds.

### Atlas data tables (spot checks)

| check | result |
|---|---|
| `experiment_map.csv` row count | 95 rows, 95 unique ids; every row has a source; 5 rows have an empty `model`. nd-rl `dan` has 63 `experiment-summaries/` entries. Expectation 1 (≥ 55) holds. |
| `dev_holdout_harmonized.csv` vs best-state on-file summaries | 24 of 24 rows that cite best-state per-read files match |
| SN textbook72 rows (12 seeds) | all match my recount |
| Robbie factorial rows checked | all match `passk.csv` |
| `rescore_wholeproof.csv` | values equal my recount |
| `truncation_check.csv` | equals my 512 vs 1,024 comparison |

**Malformed table.** `protocol_differences.csv` has two rows ("Token era (fork)" and "Leon") whose free-text fields
contain unquoted commas. Their columns are shifted: `pools` holds part of `judge_version`, `k` holds pools, and so on,
and `csv.DictReader` returns an overflow column. As written, the table misreports k, temperature, decode limits and
seeds for those two protocols.

### Compute (from genstats and podjob logs; `review_ea/compute.py`)

- **Pods.** 5 pods: `ea-rescore` on an A40; `ea-rescore2`, `ea-rescore3`, `ea-trunc` and `ea-trunc2` on RTX 3090s.
  `podhours.log` gives 1.078 pod-hours in total. Its dollar column is $0.54, which is the $0.50/h fallback; the real
  billed rate was not recorded in the logs I read.
- **Expectation 5 ("0 pods, p ≈ 0.7").** Superseded by Addendum 1, which planned one pod with two jobs. The run used
  5 pods because of a failed first setup, the batch-4,096 OOM, and the truncation re-reads. Cost was ≤ $1.5 under any
  plausible 3090 or A40 rate.
- **Per checkpoint (final reads, `max_new` 512).** 153,344 samples, 22.6–31.7 M generated tokens, and 230–285 s of
  sampler wall time, 260–323 s of job wall time. Two jobs shared one 3090, so GPU-seconds per job overstate exclusive
  GPU use by up to 2×. No training.
- **Registry.** `registry/evidence-atlas/` holds 62 files with pass@k rows plus `gpu_seconds`, `attempts`,
  `gen_tokens` and `lean_checks` rows. The compute rows are recorded.

### Not recounted (judgement content)

- **Expectation 3** (1–5 headline comparisons mix checkers or k unannounced) and **expectation 4** (create-vs-elicit
  strength ratings) are judgements, not counts. I check their wording in phase 2.
- **Create-vs-elicit table.** It rates 11 lines of evidence, and none is rated above "moderate".
- **Length-frontier CSV** (477 KB): not recounted beyond the re-score.

## §Comparison (phase 2: executor's `run_evidence_atlas.md`, `atlas/ATLAS.md`, `numbers.md` § evidence-atlas, `log.md`, `STATUS.md`)

**Gate 0.** The pre-registration (453cebab, 16:53Z) and Addendum 1 (b4f08b79, 17:23:40Z, pushed to
`origin/dan_evidence-atlas`) were both committed before the first pod (`ea-rescore`, 17:24:44Z). The addendum's ranges
and statements were written before any whole-proof read existed.

| # | claim (where) | my value | verdict |
|---|---|---|---|
| 1 | Re-score table, 24 per-seed counts (numbers.md, ATLAS §3 / §5) | identical in all 24 (§Recount) | **reproduces** |
| 2 | Lean alone decides; `nd_verify` unused | unmodified hash; judge path is `lean_judge`; 4,356 / 4,356 Lean-confirmed; negative controls 0 / 1,200 | **reproduces** |
| 3 | Map has 95 experiments; expectation 1 (≥ 55) hit | 95 rows, 95 ids | **reproduces** |
| 4 | "14 of 23 create-vs-elicit rows judged by `nd_verify` alone" (ATLAS headline 7) | 14 of 23 `checker_class = nd_verify` | **reproduces** |
| 5 | (i) "whole proof below state … **held, 4 / 4 on both**" (ATLAS §5); "proof state beats whole proof in all 12 cap × stage × pool cells" (ATLAS headline 3, run summary, STATUS) | holdout250 +81.5, +57, +79, +41 (reproduces); dev 4 / 4 large; textbook72 +3.5, +5, +7.25, +13.75 | **reproduces as a direction; must be reworded.** On textbook72 the same paragraph and the pre-registration say differences under ≈ 7 are inside the floor. So only cap-12 T1 (+13.75) is a finding there, cap-12 frozen is at the edge, and the two cap-6 cells are not differences. "Beats in all 12 cells" should read "beats in all 8 dev / holdout250 cells and in the cap-12 T1 textbook72 cell; the other textbook72 cells point the same way but are inside the floor". Whole proof has 2 seeds against 2–4 for state. The state reads also used a different batch (4,096) and decode limits (`max_steps` 96 / `max_action` 512). |
| 6 | Expectation 2 hit: "best-cap12 T1 has the top textbook72 number (51.7)" (run summary); "The best textbook72 number on file is best-9.56M state cap 12 after its T1 ladder: 52 / 51 / 52" (ATLAS headline 2) | best-state reads 52, 51, 52, with `_cap` re-reads at 53. The atlas's own `textbook72_harmonized.csv` contains **57** (trajectory `la_T1_best12_s2_r6`, which I recounted from the bucket `.jsonl`) and 53–56 at other seed-2 rounds. The trajectory re-run's own round-8 T1 reads are 48–54. | **differs.** Highest on file is 57, not 52; the family is the same recipe, but the claim as written is false. Reword to "best-cap12 (9.56M state, cap 12) is the top family: round-8 T1 51–53 in best-state, 48–54 in trajectory's re-run, with a maximum of 57 at seed 2, round 6". Expectation 2 is a **partial miss**: the family is right, the "≈ 52 is the highest" number is not. |
| 7 | (ii) "C0 T1 above Robbie's `lean-naive-ei` … textbook72 14 vs 8, holdout250 103 vs 41" (ATLAS §5) | Robbie's cells 8, 6, 10 / 45, 42, 37 (recounted from `passk.csv`); C0 T1 15, 13 / 104, 102 | **reproduces.** But two caveats are missing. **(a)** 14 of the 72 textbook72 theorems are `split = train` (RL targets) for Robbie's factorial cells; the atlas never says so, and it bears on every fork ↔ Robbie textbook72 row (Figure 2, headline 2's "32 / 30 / 32 †"). **(b)** The checker differs (†). Both favour Robbie's cells, so the direction stands. |
| 8 | "fork whole proof vs Robbie naive lean cells: **mostly** apples to apples … same format, **size class**" (ATLAS §6) | `params` is **empty** for every `robbie-factorial` row in `textbook72_harmonized.csv`. The model label is "pre=012 baseline". | **not derivable from the run's files.** This is an unlabelled model size in a headline comparison: label it or drop "same size class". With (7a), "mostly" should become "partly" on textbook72. |
| 9 | (iii) truncation "**missed** … 0.12–0.26 % on 11 of 24 … identical solved set" (ATLAS §5) | 11 of 24 over 0.1 %, maximum 0.258 %; identical solved sets in 11 of 11; 4 reads still over 0.1 % at 1,024 | **reproduces**, and is reported as a miss. "Truncation stays at 0.01–0.23 %" matches the 1,024 reads (0.006–0.233 %). |
| 10 | Range predictions: textbook72 7 / 8 seeds in range; frozen holdout / dev below; T1 rows in range (ATLAS §5) | same; C0 frozen textbook72 12 and K12 T1 s0 25 are on the boundary | **reproduces**; misses are reported as misses |
| 11 | batch 4,096 vs 2,048 re-draws: −5 to +7 dev, −2 to +3 holdout250, −4 to 0 textbook72 (numbers.md, ATLAS §5) | +3, +7, −5 / −2, −2, 0, +3 / 0, −2, −4, −3 | **reproduces** |
| 12 | Batch 2,048 instead of the pre-registered 4,096 | all 24 reads at 2,048; the log gives the OOM reason | **reproduces**. The deviation is disclosed in `log.md` as a policy deviation. ATLAS §5 states batch 2,048 but does not say it differs from the pre-registration. Minor. |
| 13 | Compute: per arm 491–574 GPU-s, 306,688 attempts, 45–62 M generated tokens; registry rows written (numbers.md) | sampler wall 477–546 s per arm (sum of 2 seeds), job wall 535–621 s; 306,688 attempts; 45.2 / 50.3 / 56.8 / 62.3 M tokens; 62 registry files with `gpu_seconds`, `gen_tokens`, `lean_checks` | **reproduces** (GPU-s within ≈ 10 % of my log-derived wall). Two jobs shared each 3090, so "GPU-seconds" is shared-card wall time; say so. |
| 14 | Cost "$0.54", "RTX 3090 $0.50/h, A40 $0.49/h" (log, run summary) | `podhours.log` 1.078 h; $0.54 equals `podbudget`'s $0.50/h fallback | **not derivable.** The policy asks for the real billed rate, and the logs I read only show the fallback. Either way the cost is under the $1.5 pre-registered cap. |
| 15 | Pods: "0 (p ≈ 0.7)" reported as a miss, with 5 used (run summary) | 5 pods, 1.078 h | **reproduces**; reported as a miss |
| 16 | "Re-reading one checkpoint at another batch flips 6–11 of 70 textbook72 problems" (ATLAS §3, §6) | this run's 4 textbook72 re-draw pairs flip 0, 2, 4 and 5 of 72 | **inherited, not re-derived here.** It is consistent in size with this run's own pairs. |
| 17 | Frozen best vs ours on textbook72 +4.0 / +0.5; after T1 +18 / +14 (ATLAS headline 4) | from the table rows: 19.0−15.0, 28.7−28.25, 37.3−19.0, 51.7−37.25 | **reproduces** arithmetically. The heading "pretraining recipe matters more after RL" compares 9.56M with 3.2M, so the recipe includes 3× parameters and more RL compute per sample. Add "and size" to the heading. |
| 18 | rr600 13–16-line rates (2 % → 87 % etc.), support-survivor 28 / 29, depth-3 13–28 %, Robbie's +408 / +268 / +92 main effects (ATLAS headlines 5–6) | not recounted (inherited; the per-stratum files are in other runs) | **not derivable here**; these carry their source runs' review status |
| 19 | "All textbook72 files are byte-identical … dev1108 and holdout250 the same sets" (ATLAS headline 1) | Robbie's `passk.csv` problem names equal `data/bs` for textbook72 (72 / 72) and holdout250 (250 / 250); Dmitry's and Charles's files not checked | **reproduces** for the part checked |
| 20 | Harmonized tables trace to files (stop rule) | spot checks all match (§Recount). `protocol_differences.csv` has 2 of 10 rows with shifted columns (unquoted commas). | **finding**: fix the CSV quoting. The prose table in ATLAS §6 is unaffected. |
| 21 | Split hygiene (not claimed in the write-up) | K12 Stage-1 ∩ textbook72 = 1 theorem (`textbook_3ed45280…`, solved by all K12 checkpoints, in training with its premises swapped) | **finding (minor).** Every cap-12 family's textbook72 count (K12 whole proof, SN-cap12, best-cap12) includes one theorem that is in its training set. Interface comparisons at cap 12 are unaffected, because both sides share it. |
| 22 | Term size (policy) | re-score proofs: median 8–11, maximum 11–44 by cell (§Recount); the atlas reports none for the re-score | **missing (minor).** The re-score reports counts only, and the atlas length figure uses `L_true` strata. G_notes explains why some runs' term sizes are absent. |
| 23 | Model labels | every fork row in ATLAS §3 and numbers.md names checkpoint, size, format, init and training set; Robbie's rows lack size (row 8) | **reproduces**, except row 8 |

Wording against n:
- Whole-proof rows have 2 seeds, the pre-registered count, and only per-seed values and means are given (no IQM or
  bootstrap interval, which is equivalent to the mean at n = 2).
- "Barely solves dev theorems at all" for C0 frozen (54 / 36 of 1,108) is fair.
- "Weight of evidence is elicitation or amplification" is labelled as a rating with a rubric, not a measurement.

## §Verdict

**No hard-constraint violation.**
- `nd_verify` is unmodified and unused as a judge.
- `TEST_RUN_DONE` is unchanged.
- There was no training and no test-file run.
- The pre-registration and addendum predate every pod.

**Stands.**
- The whole-proof re-score: all 24 per-seed counts reproduce exactly, and every counted theorem is Lean-confirmed by an
  independent header and harness with working negative controls.
- The truncation check: identical solved sets at 1,024.
- The batch-4,096 re-draw spreads.
- The holdout250 and dev1108 interface gaps (whole proof below state in all 8 cells, by 41–322 theorems).
- C0 T1 above Robbie's `lean-naive-ei`.
- The map size, the create-vs-elicit checker tally, the per-arm compute, and the reported misses (pods, truncation,
  frozen ranges).

**Must be reworded.**
1. **"Proof state beats whole proof in all 12 cap × stage × pool cells"** (ATLAS headline 3, §5 "4 / 4 on both", run
   summary, STATUS). On textbook72 only the cap-12 T1 cell is outside the floor the atlas itself quotes. The two cap-6
   cells (+3.5, +5) are not differences.
2. **"The best textbook72 number on file is best-cap12 T1, 52 / 51 / 52"**, and expectation 2 listed as a hit. The
   atlas's own table holds 57 (trajectory, seed 2, round 6). State it as the family's range (48–57 across best-state
   and trajectory reads), and mark expectation 2 as a partial miss.
3. **Fork ↔ Robbie textbook72 comparisons** (Figure 2, headline 2, §6 "mostly apples to apples"). Robbie's factorial
   cells were RL-trained on 14 of the 72 textbook72 theorems (`split = train`), which the atlas does not mention, and
   their parameter count is not recorded. Downgrade to "partly" and label the size.
4. **Headline 4.** "Pretraining recipe" → "pretraining recipe and size (9.56M vs 3.2M)".
5. **GPU-seconds and dollars.** Say "two jobs per shared 3090". The $0.50/h is `podbudget`'s fallback rate, not a
   verified billed rate.

**Fix.** Quote the free-text fields in `protocol_differences.csv`: 2 of its 10 rows are column-shifted.

**Minor.**
- The K12 training set contains one textbook72 theorem (disjunctive syllogism, premises swapped), affecting every
  cap-12 family's textbook72 count by ≤ 1.
- The re-score reports no term sizes. Mine: median 8–11, max 11–44.

**Not supported or not derivable here.**
- The billed rate.
- Robbie's model size.
- The inherited headline numbers in rows 16 and 18, which carry their source runs' review status.

**Next measurements that would settle what is open.**
- **(a)** Read the textbook72 interface comparison at more seeds or at higher k, in a paired design: same theorems,
  whole proof vs state at matched cap, 4+ seeds each. Only then can the cap-6 textbook72 cells be called. The atlas
  already has 4 seeds for SN-cap12.
- **(b)** Re-read Robbie's `lean-naive-ei` cells on the 58 `textbook_dev` theorems only, or report the fork rows on
  the same 58, for a held-out fork ↔ Robbie textbook comparison.
- **(c)** Get the frozen best-cap12 pass@4,096 on textbook72 (atlas open question 4). That is the base-reachability
  number every "RL solved X" there lacks.
