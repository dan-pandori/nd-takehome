# INVENTORY: existing per-theorem data for base vs RL comparisons

Read-only survey, 2026-10-05. Prefixes:
- **W** = `~/work/` (run worktrees with pulled artefacts)
- **R** = `~/review/`
- **B** = `hf://buckets/dan-pandori/nd-rl/`
- **G:x** = `origin/dan_x` in `~/nd-takehome`

For the best-cap12 and cap-6 runs, git tracks only the `.json` read summaries. Their per-theorem `.jsonl` files are in
the bucket, with pulled copies in W. The support-* runs keep their records in git.

## Common read row (`state_eval.py`, `lpool_reread.py`, `eval_set.py`)

```
{"name":"textbook_c18068b3bc4dc6b6894a","thm":null,"prompt":"THM SEQ ( ( P v Q ) > ( Q v P ) ) PRF","reference_lines":7,
 "solved":true,"n_ok":36,"n_tried":256,"proofs":["N1 | ( P v Q ) : AS ; … QED",…],"written_lens":[7,8,11],
 "pruned_lens":[7,8,11],"reasons":["lean rejected",…],"fail_example":"LEANREJ …"}
```

| quantity | field |
|---|---|
| theorem id | `name` |
| statement | `prompt`; `thm` too, except tb72, where it is null |
| L label | `n_lines` (h250), `reference_lines` (tb72), `L_true_lb` (rr / long2) |
| k / successes | `n_tried` / `n_ok`; `n_ok` counts duplicate samples |
| accepted texts | `proofs`: every distinct Lean-accepted ND proof, uncapped |
| lines | `written_lens` / `pruned_lens` |

- Rows carry no log p and no term size.
- Checkpoint, training seed and sample seed are in the file name `s<S>_<ckpt>__<pool>_x<X>` (X = `--seed`) and in
  `*.args.json` (trajectory: x1 reads only).
- `reasons` is a list in tb72 / h250 reads and a dict in rr / long2 reads.
- A copy of every read is in the registry: one `pass_count` row per theorem in `artifacts/<run>/registry/`. In
  rl-continue's rows, `seed` holds the sample seed, not the training seed.

## A. Sampled reads

### A1. best-cap12 (trajectory's s0–s2)

Model: `ALiBiGPT` 6×384, 9,560,832 params, `lean_staten`, Stage 1 for 1,200 s on K12. Reads use T 0.8, `max_steps` 96,
`max_action` 512 and batch 2,048 unless noted.

| ckpt | pool × sample seed × k | path |
|---|---|---|
| 22 checkpoints: p0 (init), p50, p100, p200, p400, p800, p1600, p3000, p5000, p8000, p12000, p16000, p20000, pend (= r0), r1–r8 | tb72, h250 × x0, x1 × 256 (264 reads) | `W/trajectory/artifacts/tj/eval/s<S>_<ck>__{tb72,h250}_x{0,1}.jsonl` (692 MB); `B/trajectory/artifacts/tj/eval/` |
| pend, r8 | tb72, h250, rrQ100, long2, C × **x2** × 256 | `B/mcts-a/artifacts/mcts/eval/s<S>_{pend,r8}__<pool>__sample.jsonl` (bucket only; PUCT `__prior` / `__value` alongside) |
| r8 | C × **x3** × 2,560 | `B/mcts-a/artifacts/mcts/eval_x10/s<S>_r8__C__sample.jsonl` |
| r8, r16 | rr600 13–16 (400) × x0 × **64**; long2 × x0 × 256; batch 512 | `W/rl-continue/artifacts/rc/eval/s<S>_r{8,16}__{rr1316,long2}_x0.jsonl` |
| r12, r16 | tb72, h250 × **x1 only** × 256 | `W/rl-continue/artifacts/rc/eval/s<S>_r{12,16}__{tb72,h250}_x1.jsonl` |
| r8 | dev1108 × x0 × 64; held-out greedy | `W/grpo-best/artifacts/gb/eval/ei_s<S>_r8__{dev,held}_x0.jsonl` |

- Group C: 36 / 35 / 28 theorems.
- Attempts per C theorem: 1,024 at pend and 3,584 at r8.
- The mcts-a C-only x2 read and its full-pool x2 read are distinct draws: at s0 pend, only 2 / 36 rows share their
  first 20 failure reasons.
- **Replays, not new draws.**
  - rl-from-ckpt's `*_rr_*` reads are identical to trajectory's x1 (8 / 8 files).
  - guided-tts plain (r8) reproduces trajectory r8 x1 on tb72: `n_ok` identical on 70–71 / 72 rows (cap 12) and
    72 / 72 (cap 6).
- Other RL from the same pend:
  - GRPO (`grpo-best`): 3 arms at r2 / r4 / r8 and distinct at r2 / r4; tb72 / h250 x0 / x1 at k 256.
    Path: `W/grpo-best/artifacts/gb/eval/gb_<arm>_s<S>_r<k>__<pool>_x<X>.jsonl`.
  - rl-from-ckpt (A3).
- **Different instances.** `best-state`'s Fz / T1-r8 seeds are separate trainings, not trajectory's. Their reads are
  `W/best-state/artifacts/bs/eval/{Fz,T1}_best{12,6}_s<S>__{tb72,h250,dev,rr600,long2}.jsonl`, with rr600 = all 600 at
  k 256. Leon's dan12 / dan6 models are these instances.

### A2. best-cap6

Model: the same recipe trained on the cap-6 set `data/p2/train_depth3_f0_a1.jsonl` (155,000, md5 `29276f24…`). Rounds
r1–r8 come from `trajectory-cap6` and r9–r16 from `rl-continue-cap6`.

| ckpt | pool × x × k | path |
|---|---|---|
| the same 22 checkpoints | tb72, h250 × x0, x1 × 256 (264 reads) | `W/trajectory-cap6/artifacts/tj6/eval/` (343 MB); `B/trajectory-cap6/artifacts/tj6/eval/` |
| pend: B theorems; r8: C theorems | x0 × 256 at 2× caps (1,024 / 192) | `W/trajectory-cap6/artifacts/tj6/capdiag/s<S>_{pend,r8}__<pool>_x0_2x.jsonl` |
| r16 | tb72 × x1 × 256; h250-C only (24 / 21 / 26) × x1 | `W/rl-continue-cap6/artifacts/rc6/eval/s<S>_r16__{tb72,h250C}_x1.jsonl` |

There is no r12 read and no rr600 or long2 read.

### A3. rl-from-ckpt (best-cap12 s0–s2)

All paths are under `W/rl-from-ckpt/artifacts/rfc/`.

| what | pools × x × k | path |
|---|---|---|
| ladders from p1600 / p5000 / p12000 / p16000, read at r2, r4, r8 | tb72, h250 × x0, x1 × 256 (144 reads) | `eval/s<S>_<start>_r{2,4,8}__<pool>_x<X>.jsonl` |
| replay-only controls (4 starts + pend), r8 | same (60 reads) | `eval/c<S>_<start>_r8__<pool>_x<X>.jsonl` |
| in-loop | rl_targets / transfer | `la_T1_best12_s<S>_<start>/{alloc,round}_*.json`; `found` / `mix` files in `B/rl-from-ckpt/artifacts/rfc/` |

- The p0 ladders stopped after 2 rounds with 0 accepted.
- The pend ladder is trajectory's.

### A4. EI ladders' own records (rl_targets 4,495; transfer 2,285)

How `state_ladder_ei.py` samples:
- Round r samples checkpoint r−1, so round 1 samples **pend**.
- k 32 per theorem, T 0.8.
- **Ladder caps are 256 / 48** (`max_action` / `max_steps`), unlike the reads.
- Seed `1000·S + r`; transfer uses +500.

| file | content |
|---|---|
| `alloc_<r>.json` | `{"k":{name:32},"tried":{name:32·r},"accepted":{name:cumulative n_ok}}` over the 4,495 rl_targets. **Round-r successes out of 32 = accepted_r − accepted_{r−1}**, so round 1 (pend) is exact. |
| `found_<r>.jsonl` | cumulative distinct proofs: `name, thm, prompt, L_true, schema, proof, norm, written, pruned, round` |
| `found_transfer_<r>.jsonl` | the same for transfer. **No `n_ok`.** Round 1 gives an exact solved@32 indicator; later rounds only add new distinct proofs. |
| `round_<r>.json` | per-round and cumulative aggregates |
| `mix_<r>.jsonl` | training records (RL proofs + 20,000 replay) |

| ladder | alloc / round files | found / mix files |
|---|---|---|
| cap-12 r1–r8 | `W/trajectory/artifacts/tj/la_T1_best12_s<S>/` | `B/trajectory/artifacts/tj/la_T1_best12_s<S>/` |
| cap-12 r9–r16 | `W/rl-continue/artifacts/rc/la_T1_best12_s<S>/` (cumulative from r1) | `B/rl-continue/artifacts/rc/…`; local `R/rc_data/s<S>/{found_8,found_16,found_transfer_8,found_transfer_16,mix_16}.jsonl` |
| cap-6 r1–r8 | `W/trajectory-cap6/artifacts/tj6/la_T1_best6_s<S>/` | `B/trajectory-cap6/artifacts/tj6/…` |
| cap-6 r9–r16 | `W/rl-continue-cap6/artifacts/rc6/la_T1_best6_s<S>/` | `B/rl-continue-cap6/artifacts/rc6/…`; local `R/rc6_data/s<S>/` |

- Distinct target proofs, r8 → r16:
  - cap 12: 229,482 / 271,490 / 250,560 → 605,090 / 710,641 / 637,930;
  - cap 6: 72,175 / 48,085 / 36,334 → 295,168 / 202,492 / 168,090.
- The r16 checkpoint is never sampled in-loop.
- `found_16` is 0.45–0.96 GB per seed, so stream it line by line.

### A5. support-curves / -followups / -state, state-readouts (3.2 M models, not best-cap12)

Models:
- WP base: `B/support-curves/ckpts/lf/stage1_a1_seq_s{0,1}.pt` (`lean_seq`, cap 6).
- WP EI: `…/ckpts/ladder/la_T1_sc_s0_r8.pt` and `la_T1_sc_s1rerun_r8.pt`.
- SN base: `B/state-env/ckpts/se/stage1_SN_s{0,1}.pt` (`lean_staten`). SN EI: `…/se/ladder/la_T1_SN_s0_r8.pt`.

Sets are in `G:support-curves data/sc/`: `theorems.jsonl` (383; ⊂ transfer; 42 are in h250), `crux_forward.txt` (82)
and `falsifier_survivors.txt` (29; 3 are in h250).

Rows look like `{"name","L_true","model","ckpt_md5","temperature","seed","stage","k_requested","stop_at","n_tried","n_ok","first_hit","proofs",…}`.
`n_tried` stops early once `stop_at` successes are reached.

| data | path |
|---|---|
| pooled per (theorem, model, T, seed): `n, c, p_hat, proofs` (1,952 rows) | `G:support-curves artifacts/sc/summary.json` |
| stage files: s1 (k 10,000), s2 (base to 200k per T), s3 (seed 1) | `G:support-curves artifacts/sc/s*_{base,ei}_T*_s*.s*.jsonl` |
| base / EI teacher-forced log p of 297 EI crux proofs | `G:support-curves artifacts/sc/secondary_logp.jsonl` |
| seed-1 replication; 1.67 M × 6; 25 M base | `G:support-followups artifacts/sf/{a,b,c1,c2}_*.jsonl` |
| per-token log p of EI proofs under base (412 rows) | `G:support-followups artifacts/sf/d_steps.jsonl` |
| SN base: H (survivors ≤ 400k), S1 (383, k 10,000) | `G:support-state artifacts/ss/{H,S1,S2*}_*.jsonl` |
| S / SH bases on the 29; SN-cap12 T1 / frozen on 760 + 282 textbook theorems | `B/state-readouts/artifacts/state-readouts/` |

### A6. guided-tts

- Models: trajectory's cap-12 r8 and trajectory-cap6's r8, seeds 0–2.
- Arms: plain, structural, logical. k 256, **seed 1**.
- 259 theorems: tb72 plus Charles's 187 (`W/guided-tts/data/gt/`).
- Files: `W/guided-tts/artifacts/gt/eval/best{12,6}_s<S>_<arm>.rows.jsonl.gz` (18 files); also in
  `B/guided-tts/artifacts/gt/eval/`.
- Row: `name, prompt, min_lines, n_ok`; per-attempt `ok / tokens / draws / rej / steps`; `accepted` = {text: count}.
- **r8 only.**

### A7. organism-analysis compacted reads

`oa/oa_compact_read.py` keeps `{name, n_ok, n_tried, proofs, pruned_lens}` per theorem.

| `W/organism-analysis/data/oa_in/reads/` (and `B/organism-analysis/…`) | reads | size |
|---|---|---|
| `trajectory/` | 264 (= A1's trajectory reads) | 24 MB |
| `trajectory-cap6/` | 264 | 5.9 MB |
| `rl-from-ckpt/` | 212 (= A3) | 27 MB |

- The "~280 MB" is the whole of `data/oa_in`, which also holds copies of the score and target files.
- **Not included:** rl-continue(-cap6), mcts-a, grpo-best, guided-tts and best-state reads.
- Derived tables:
  - `data/oa/q1_rows.jsonl`: 5,526 rows = 307 theorems × (run, seed, start). Each row holds the reference proof's w1–w3,
    total, term size and lines under the start checkpoint, plus `ok0_x0, ok8_x0, ok0_x1, ok8_x1`.
  - `q2_steps.jsonl`: 55,260 reference steps.
  - `artifacts/oa/entropy/`: per-step teacher-forced entropy and lp, 111 checkpoints.
- These use 307 of the 315 references.

### A8. evidence-atlas

The whole-proof re-score used 3.2 M `lean_seq` models: C0 cap-6 and K12 cap-12, each frozen and T1, seeds 0 and 1.
- Reads: `W/evidence-atlas/artifacts/atlas/eval/{c0fz,c0t1,k12fz,k12t1}_s{0,1}__{tb72,dev,h250}.jsonl` (24 reads;
  k 256 / 64 / 256; seed 0).
- Re-reads: `eval_mn1024/` and `b4096_partial/`.
- `atlas/data/*.csv` is aggregates only, with no per-theorem rows.

## B. Teacher-forced scores

### B1. `tj_score.py`

- Per-action log p at T 1.0 and T 0.8, marginalised over 33 name bases; environment-assigned names are masked.
- `targets.jsonl` row: `tid` (`ref:` or `ev:`), `kind`, `n_steps`, `actions_b0`, `step_kind`, `lean_ok`, `term_size`.

```
{"tid":"ref:textbook_c18068b3bc4dc6b6894a","ckpt":"s0_pend","T1.0":{"total":-2.033,"mean":-0.254,"w1":-1.904,"w1_idx":1,
 "w1_kind":"box:orelim","w2":-0.059,"rest_mean":-0.018,"step_lp":[-0.0063,-1.9039,…],"raw_b0_total":-2.049,
 "incl_names_total":-6.156},"T0.8":{…}}
```

| dir | checkpoints | targets |
|---|---|---|
| `W/trajectory/artifacts/tj/score/s<S>/` | 22 cap-12 (p0 = init … r8); `ckpts_s<S>.md5` | 315 refs + `ev` 286 / 286 / 293 (r8's best x0 proof) |
| `…/tj/score/cand_s<S>/` | r8 | about 20k candidates |
| `W/trajectory-cap6/artifacts/tj6/score/s<S>/` | 22 cap-6 | 315 refs + `ev6` 268 / 269 / 262 |
| `…/tj6/score/cross_s<S>/` | 22 cap-6 | 1,664: cap-12 r8 eventual (865) + cap-6 eventual (799), all seeds |
| `…/tj6/score/rev12_s<S>/` | 22 cap-12 | the same 1,664 |
| `W/rl-from-ckpt/artifacts/rfc/score/s<S>_<start>/` | r0, r2, r4, r8, control r8 | 315 refs + that ladder's eventual proofs |

### B2. lit-measures

`W/lit-measures/artifacts/lit-measures/m1/steps.jsonl` (1,371 rows): per-step log p of SN EI s0 proofs under SN base s0
(3.2 M). Not best-cap12.

### B3. r16 proofs under base

**None.** No score file involves an r9–r16 proof or checkpoint.

## C. Checkpoints (38.28 MB each)

| model | bucket path | md5 (s0 / s1 / s2) |
|---|---|---|
| cap-12 Stage 1, steps 0 … end | `B/trajectory/ckpts/tj/stage1_best12_s<S>_b1200[_step<N>].pt` | pend 2bf801fd / eaff7f4d / abca9c63 |
| cap-12 r1–r8 | `B/trajectory/ckpts/tj/ladder/la_T1_best12_s<S>_r<r>.pt` | r8 f9afd386 / c85481f9 / 3b62784b |
| cap-12 r9–r16 | `B/rl-continue/ckpts/rc/ladder/la_T1_best12_s<S>_r<r>.pt` | r16 324de94f / 7ea8c8bb / f7924ccd |
| cap-6 Stage 1 | `B/trajectory-cap6/ckpts/tj6/stage1_best6_s<S>_b1200[_step<N>].pt` | pend dacd64d0 / 360900c4 / 427ef388 |
| cap-6 r1–r8 | `B/trajectory-cap6/ckpts/tj6/ladder/la_T1_best6_s<S>_r<r>.pt` | r8 586baf0b / a8dfc589 / 1b1843d5 |
| cap-6 r9–r16 | `B/rl-continue-cap6/ckpts/rc6/ladder/la_T1_best6_s<S>_r<r>.pt` | r16 d9d196d6 / 787bce93 / d4aa898c |
| rfc ladders / controls | `B/rl-from-ckpt/ckpts/rfc/{ladder,control}/` | |

- **Local, md5-verified:** `R/trajectory/rv/ck/` and `R/trajectory-cap6/rv6/ck/` hold pend, step 1,600 and r8 for all
  seeds. There is no local r16.
- **Code on `G:dan`:** `state_eval.py` (identical to trajectory's), `lpool_reread.py`, `state_ladder_ei.py` and
  `guided_eval.py`.
- **`tj_score.py` is not on dan.** The same blob (`570d558f`) is on four run branches. Its imports are byte-identical
  on dan, so `git show origin/dan_trajectory:tj_score.py` should run unchanged from a dan worktree.
- `tj_score` falls back to CPU when there is no GPU. `~/venv-cpu` has **torch 2.14.0+cpu**. Rough CPU cost: ≈ 10 s per
  target per checkpoint (trajectory's reviewer).

## D. Theorem sets

| set | n | file | fields |
|---|---|---|---|
| rl_targets | 4,495 | `W/trajectory/data/ladder/rl_targets.jsonl` | `n_lines` = `L_true`; `gen_proof` |
| transfer | 2,285 | `…/data/ladder/transfer.jsonl` | same |
| holdout250 | 250 | `…/data/bs/holdout250.jsonl` (⊂ transfer) | |
| textbook72 | 72 | `…/data/bs/textbook72.jsonl`, from `data/eval_only/textbook72/` | MANIFEST rule: "Never train or tune on these or on a renaming of them. Report dev58 and train14 separately and combined." |
| references | 315 | `…/data/tj/ref_targets.jsonl` | `proof`, `min_lines_ub` |
| rr600 13–16 | 400 | `W/rl-continue/data/rc/rr600_13_16.jsonl` | `L_true_lb`, `minlen_proof` |
| transfer_long2 | 21 | `…/data/ladder/transfer_long2.jsonl` | `ub_proof` |
| group C, cap 12 | 36 / 35 / 28 | `G:grpo-best artifacts/gb/groups.json` (A / B / C for all 322 per seed); `G:mcts-a data/mcts/groupC_s<S>.jsonl` | |
| group C, cap 6 | 52 / 52 / 60 | `W/rl-continue-cap6/artifacts/rc6/groupc.json`; `data/rc6/h250_C_s<S>.jsonl` | |

- The 3,735 generator rows of rl_targets carry `gen_proof`, an upper-bound proof.
- Minlen proofs for rl_targets and transfer are in `B/ladder-A/data/ladder/raw_textbook_minlen*.jsonl` and
  `pool_long_minlen*.jsonl`.
- textbook72 has reference proofs for 65 of its 72 theorems.

## E. Leon's excess description length

- **Where:** nd-rl `leon/benchmarking` and `-dan`: `code/ndbench/edl.py`, `analysis/edl.py`, `configs/edl*.yaml`,
  `adapters/danstate.py`. Summary: `experiment-summaries/2026-09-30-benchmarking/README.md`.
- **The quantity** (Donoway et al., arXiv:2601.04728): EDL = online code length − n × final test loss. The code length is the sum of each
  example's NLL scored *before* the update on it. The model is fine-tuned on 32–64 examples of a synthetic pattern
  class; the learning rate is chosen by code length, plus an ln 6 selection cost.
- **Leon's own base vs RL:** RL has lower EDL on 9 / 9 classes, but it starts with lower loss, and EDL tracks the
  starting loss (Spearman 0.94). Per nat of loss removed, RL costs as much or more on 7 / 9.
- **Dan's models:** best-state's dan12 s0 Fz vs T1, one data order. The results are not in git. According to the commit
  message of `3153696`, RL has lower EDL on 6 / 8 classes and lower starting loss on 6 / 8, and costs as much or more
  per nat on 3 / 8.
- **Applying it to ours:** possible through `configs/models.yaml`, but it needs new GPU runs and measures synthetic
  classes, not tb72, h250 or C.

## Gaps (no existing data)

1. **Base (pend) log p of r16's proofs: none.**
   - Exists: pend log p of the 315 references and of r8's eventual proofs (B1).
   - The r16 proof texts are in `R/rc_data/s<S>/found_16.jsonl` and the r16 reads, and the r16 checkpoints are in the
     bucket (C).
   - Filling the gap means running `tj_score.py`; on CPU that costs ≈ 10 s per proof per checkpoint.
2. **Large-k (≥ 4,096) samples of pend on B ∪ C: none.**
   - The most at pend is 768 attempts per B theorem and 1,024 per C theorem.
   - For h250 theorems, ladder round 1 adds 32 attempts, but stores only a solved flag per theorem.
   - The ≥ 10⁴-attempt data are all on the 3.2 M models (A5).
3. **Random-init / null-model samples: only degenerate random-init.**
   - Init (p0) reads solve nothing; ≈ 96 % of attempts are parse failures.
   - The rfc p0 ladders accepted 0 / 287,680 samples per seed.
   - No null model exists.
4. **Guided reads of pend / r8 / r16: r8 only** (guided-tts). mcts-a's PUCT search at pend and r8 is a different method.

Smaller gaps:
- rl-continue has no x0 tb72 / h250 reads at r12 / r16.
- rr600 / long2 at pend exist only as mcts-a's rrQ100 / long2 x2 reads.
- The cap-6 r16 h250 read covers only C.
- Transfer per-round `n_ok` was not stored.
- There is no dev1108 read at trajectory's pend.
