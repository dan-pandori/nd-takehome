# Review — kalmar-complexity (proposal 31)

Reviewer: agent:claude, reviewer role, 2026-10-20. Run branch `dan_kalmar-complexity`; brief nd-rl
`docs/proposals/state-env/BRIEF_kalmar-complexity.md`; pre-registration `preregistration/kalmar-complexity.md`
(main body + Addenda 1 and 2). Phase 1 was done in `~/review/kalmar-complexity` (executor write-ups removed) with my own
scripts, `review/kalmar-complexity-recount/rv_*.py`; their outputs are in `review/kalmar-complexity-recount/out/`, and
every table below is generated from those files by `rv_tables.py`.

## Disclosure: what I saw before or during phase 1

- **Commit subjects.** The session's start-up context printed the run's last five commit subjects. They include the B3
  result ("focus-given states cut opener-step error 94 % (31.96 -> 1.94 %, 3 paired seeds), error-lookups correlation
  +0.61 -> -0.02; other steps -30 % (pre-registered < 30 % missed narrowly)"), which I knew before recounting B3.
  Checking timings, I also printed three more subjects ("explicit per-step policy (exact on 109,072 + 546,991 states)",
  "decision procedure (46-leaf tree, exact on 4,000 + fresh 2,000 theorems)").
- **The pre-registration's Addendum 2** quotes two Q4 values: RASP-L decision depth ρ = +0.85 and lookups +0.82.
- **BLC.** To learn the data interface I read `programs/blc/README.md`, whose results table gives the executor's BLC and
  CL bit counts and pass counts, and `runs/test_final_regen.log`, which gives the same numbers. My BLC and CL bit counts
  are therefore not blind. My test outcomes are: own parser, machine, codecs and a fresh seed.
- **Other raw logs and artefacts I printed:** `artifacts/kc/spend.txt`; one B3 job log's `READ` line (per-type errors of
  STD s0); `rasp_recheck_s99.log` and the head of `test_1000_s20261020.log` (pass counts); the top of
  `b2/kal_M_s0.json` (its summary line, `prequential_bits` 1,689,861).
- **Not read in phase 1:**
  - `run_kalmar_complexity.md`, `numbers.md`, `log.md`, `STATUS.md`, the plain summary, `next_steps.md`;
  - `kalmar_complexity/{README.md, prereg_outcomes.md, b2_text.md, numbers_section.tmpl.md, measures.csv, literature.md}`;
  - `artifacts/kc/{numbers_tables.md, compute_table.md, b1_preq.json, b1_snap_types.json, b2_summary.json,
    b2_per_type_table.json, b3_summary.json, python_sizes.*, kt_python.json, rank_agreement.json, q4/q4_results.json,
    q4/q4_analysis_stdout.txt}`;
  - the figures.

# §Recount (phase 1, blind)

## 0. Models every number below refers to

| label | checkpoint | size, architecture | format | from scratch? | trained on |
|---|---|---|---|---|---|
| KAL-D s0–s2 (kalmar-pretrain) | `ckpts/kc_src/stage1_kalD_s{0,1,2}.pt` (= `ckpts/kalmar/stage1_kalD_s*.pt`) | 9,560,832, ALiBiGPT `best`, 6 × 384 | `lean_staten` (state → action) | yes | K12-Kalmár sl, 155,000 theorems, 16,876,247 pairs; Muon + MTP; 656,285 steps = 3.68 epochs |
| control s0–s2 (best-state) | `ckpts/kc_src/stage1_best12_s{0,1,2}_b1200.pt` | 9,560,832, same | `lean_staten` | yes | K12's own proofs (`data/kh/train_k12.jsonl`, cap 12), 1,239,995 pairs; 23,951 steps = 3.67 epochs |
| KAL-C, KAL-D+A (kalmar-pretrain) | `stage1_kalC_s*` (24,020 steps), `anneal/kalDA_s*` (KAL-D + 600 annealing steps) | 9.56 M | `lean_staten` | yes | as kalmar-pretrain's review defines them |
| B2 S / M / L | not saved (block models are trained and discarded) | 426,240 / 3,220,480 / 9,560,832, ALiBiGPT 2 × 128 / 4 × 256 / 6 × 384 | `lean_staten` | yes | for block k, theorems [0, 64·2^k) of K12 order minus 10 % held out; AdamW, early stopping |
| B3 STD / FOC s0–s2 | not saved | 3,220,480 (size M) | `lean_staten`; FOC states carry the focus formula | yes | Kalmár pairs of K12 theorems [0, 8,192) (STD or FOC states); AdamW; 20,000 steps |

All read-outs are on **tf1200**: 1,200 held-out theorems from `data/p2/heldout.jsonl`, i.e. 137,984 states of their
Kalmár sl proofs.

## 1. Hard constraints and timing — no violation

- **`nd_verify`.** Its tree in HEAD equals `origin/main`'s (`9437bb72…`). No file under `kalmar_complexity/` imports it;
  `state_env` uses `nd_verify.verify.parse_formula` as a parser only. Nothing in this run is judged by `nd_verify`.
- **`artifacts/TEST_RUN_DONE`.** The blob equals `origin/main`'s (`1d5cf064…`, md5 `e2eea349…`).
- **Evaluation files in training code** (grep of `kalmar_complexity/`, `pod/kc/`):
  - `b2_preq.py` reads only `data/kalmar/train_kal_sl.jsonl.gz` and `data/kh/train_k12.jsonl`.
  - `b3_focus.py` reads `data/kalmar/tf1200_kal_sl.jsonl` only after training, for the read-out.
  - No textbook72 or test file is read anywhere.
- **Expectations before measurements.**
  - Pre-registration: commit `68f7ada4`, 12:30:36 UTC.
  - Addendum 1: `a32add38`, 13:16:43, before the first pod (kc-1 created 13:17:34; first B2 job 13:19:09).
  - Addendum 2: `c27a65d2`, 15:48:50, before kc-3 (16:00:34) and the first B3 job (16:01:24).
  - Later edits to the file only replace the header times: "≈ 16:10" became "15:49". Expectations were written
    before the runs.
- **Lean.** No proof is judged in this run. The programs' outputs are checked in Lean in §3a.

## 2. Split disjointness — 0 overlaps

Renaming class means the minimum over the 24 bijections of P Q R S; I also checked it with premise order and
duplicates factored out. Under both keys, **0 / 1,200** tf1200 theorems and **0 / 300** val300 theorems share a class with:

- K12 [0, 155,000) (KAL-D, the control);
- [0, 16,884) (B2);
- [0, 8,192) (B3).

tf1200 has 1,200 distinct classes (`rv_splits.py`).

## 3. Q1 — the programs

**3a. Hand-golfed Python** (`rv_python.py`). Sizes are my own counts. Tokenizer files are md5-identical to the hub's
`Qwen/Qwen3-8B` and `openai-community/gpt2` `tokenizer.json`.

| program (hand-golfed Python) | raw bytes | raw DEFLATE | gzip -9 | raw xz (9e) | Qwen3 tokens | GPT-2 tokens |
|---|---:|---:|---:|---:|---:|---:|
| K-sl algorithm | 1,907 | 864 | 882 | 906 | 897 | 1,195 |
| K-sl render ND | 465 | 293 | 311 | 321 | 244 | 308 |
| K-sl render lean_seq | 977 | 562 | 580 | 596 | 475 | 615 |
| parse | 251 | 153 | 171 | 162 | 122 | 156 |
| K-sl alg + lean_seq render | 2,884 | 1,347 | 1,365 | 1,381 | 1,372 | 1,810 |
| K-sl alg + ND render | 2,372 | 1,093 | 1,111 | 1,137 | 1,141 | 1,503 |
| K-tt algorithm | 749 | 378 | 396 | 394 | 377 | 491 |
| K-tt render Lean | 1,024 | 571 | 589 | 600 | 514 | 655 |
| K-tt alg + Lean render | 1,773 | 866 | 884 | 880 | 891 | 1,146 |
| K-sl per-step policy kpol | 3,794 | 1,654 | 1,672 | 1,658 | 1,838 | 2,387 |
| calib copy | 13 | 15 | 33 | 17 | 5 | 7 |
| calib reverse | 19 | 21 | 39 | 23 | 7 | 12 |
| calib parity | 20 | 22 | 40 | 24 | 9 | 12 |
| calib parity_nb | 42 | 43 | 61 | 46 | 20 | 23 |
| calib sort | 9 | 11 | 29 | 13 | 4 | 5 |
| calib sort_nb | 94 | 87 | 105 | 100 | 40 | 55 |
| calib add | 17 | 19 | 37 | 21 | 7 | 11 |
| calib add_nb | 116 | 100 | 118 | 113 | 60 | 79 |
| calib eval | 138 | 105 | 123 | 115 | 74 | 88 |
| calib taut | 320 | 222 | 240 | 239 | 152 | 188 |

Mechanical minification (python-minifier, the executor's settings; raw / DEFLATE bytes):

| file | raw | DEFLATE |
|---|---:|---:|
| `kalmar/kalmar.py` (builder + render) | 5,863 | 2,416 |
| `tt_prover.py` | 3,474 | 1,685 |
| `gen.py` (K12 generator, all knobs) | 17,076 | 5,324 |
| `policy.py` | 7,453 | 2,761 |
| decision-tree feature extractor (`features.py` + the `policy.py` it imports) | 10,509 | 3,962 |

Fresh sample: 1,000 K12 theorems, `random.Random(271828)`; the executor used seeds 20261020, 7, 13 and 99. Every
output is compared directly with `kalmar.build(p, 'sl')` and `tt_prover.solve(p)`:

- K-sl → ND text: **1,000 / 1,000** token-exact.
- K-sl → canonical `lean_seq`: **1,000 / 1,000**.
- K-tt → Lean source: **1,000 / 1,000**.
- The golfed per-step policy `kpol` against the builder's action: **109,957 / 109,957 states**.
- Negative control: K-sl's text equals the per-branch builder's on only 37 / 1,000 (one- and zero-atom theorems).
- The `tt_prover.py` copy is byte-identical to nd-rl `origin/dan:code/tools/tt_prover.py`.

**Lean on the programs' own outputs** (150 fresh theorems, seed 314159; Lean 4.34; chunks with a sentinel; unique
theorem names):

- K-tt's printed theorems: **150 / 150** accepted.
- K-sl's `lean_seq` text as `theorem … := by <text>`: **150 / 150** accepted. This needs `.1 / .2 / .elim` attached to
  the name and `maxRecDepth 4000`, as `lean_gate` does.
- 20 corrupted negatives: **0 / 20** accepted.
- No `sorry` or automation in any text.

Builder proofs on the sample: 109.0 ND lines on average (median 95, maximum 353) and 110.0 actions. This run counts no
model proofs, so there is no term-size table to re-derive.

**3b. BLC and binary CL** (`rv_blc.py`, `rv_blc_test.py`, `rv_calib.py blc`):

- my own BLC bit-string parser (checks closedness);
- a call-by-need machine with update frames;
- codecs written from the documented interface;
- Tromp's 9-rule bracket abstraction (minimum of the two "combinator" readings, as the executor states).

| program | BLC bits | binary CL bits (own bracket abstraction) | CL / BLC | fresh-sample check |
|---|---:|---:|---:|---|
| parse (prompt word → sequent) | 800 | 2,900 | 3.6 | 1000/1000 |
| K-sl algorithm | 5,443 | 23,921 | 4.4 | 1000/1000 (alone); 1000/1000 end to end |
| K-sl rendering (ND) | 616 | 3,776 | 6.1 | 1000/1000 end to end |
| K-tt algorithm | 1,636 | 7,442 | 4.5 | 1000/1000 end to end |
| K-tt rendering (Lean) | 4,204 | 24,245 | 5.8 | 1000/1000 end to end |
| K-sl algorithm + rendering (+ parse) | 6,059 (6,859) | 27,697 (30,597) | | |
| K-tt algorithm + rendering (+ parse) | 5,840 (6,640) | 31,687 (34,587) | | |
| calibration copy | 4 | 8 | 2.0 | 300/300 own random cases |
| calibration reverse | 87 | 197 | 2.3 | 300/300 own random cases |
| calibration parity | 82 | 185 | 2.3 | 300/300 own random cases |
| calibration add | 375 | 1,163 | 3.1 | 300/300 own random cases |
| calibration sort | 257 | 749 | 2.9 | 300/300 own random cases |
| calibration eval | 273 | 713 | 2.6 | 300/300 own random cases |
| calibration taut | 410 | 1,430 | 3.5 | 300/300 own random cases |

What the end-to-end checks covered:

- **"End to end"** means the composed term `render(ksl(parse(word)))`, and
  `(λs. ktt_render s (ktt s)) (parse word)`. Each was run on the encoded prompt and its output word decoded.
- **The CL terms** (S and K as λ-terms, run end to end through the same machine): **50 / 50** theorems for each of K-sl
  and K-tt. The executor's test ran CL on 3 inputs.
- **Negative controls:**
  - K-sl's output equals the per-branch builder's proof on 5 / 100 theorems (one-atom cases);
  - K-tt's output equals another prompt's Lean text on 0 / 100.
- **Call-by-need β-steps on my sample** (mean / median / max):
  - K-sl algorithm: 58,856 / 39,410 / 401,019;
  - K-sl end to end: 62,403 / 42,155 / 422,419;
  - K-tt end to end: 12,642 / 9,914 / 72,954.

**3c. RASP-L policy** (`rv_rasp.py`). My own walk of the program graph (`build_decision(9)`) gives:

- **Size:** **492 operations** if selects count (427 without them; inputs and constants excluded). By kind: 65
  select, 151 aggregate (134 max, 17 min), 2 selector-width, 248 sequence maps, 26 token maps. **Attention depth is
  41**.
- **Non-RASP-L operations: 96 of the 492 nodes are flagged by the executor's own interpreter.** That is 61
  composite-valued nodes (16-bit truth tables), 34 multi-field selects and 1 count-arithmetic node. A further 24 selects
  use an arbitrary vectorised predicate.
- **Fresh sample** (every state of the 1,000 theorems, the RASP decision program plus the plain-Python content
  renderer): **109,957 / 109,957 exact**, 1,000 / 1,000 theorems. I did not re-run the RASP rendering program.
- **Naive reference evaluator.** My own plain-loop evaluator uses each map's scalar `fn`, not its numpy `vfn`, and
  causal select / aggregate by enumeration. It agrees with the executor's numpy kernels on **171 / 171** states
  (2 theorems, seed 161803), and its rendered actions are exact. An 8-theorem run is in the background (see the
  addendum at the end of §Recount).

**3d. Decision trees** (`rv_dtree.py`, `rv_treepaths.py`). The trees use the executor's feature extractor (the artefact
under test) and my own template label (step tag | rule head; equal to the executor's on 109,957 / 109,957 states). Bits
use the stated code: a node costs 1 bit, a test log2 21 + log2 #values, a leaf log2 40.

| tree | fit on | leaves / tests / depth | bits (mine) | fit rows exact | fresh 1,000 theorems (109,957 states) | tf1200 (137,984 states) |
|---|---|---|---:|---|---|---|
| tree_b1 / b2 / b3 | rows_1000 (421 rows) | 47/46/11, 46/45/10, 46/45/11 | 639.3 / 624.4 / 625.6 | 421/421 each | 109,957 each (59 states with unseen vectors) | b3: 137,984 |
| tree_u_b1 / b2 / b3 / b4 | rows_union4000 (473 rows) | 47/46/11, 47/46/11, 46/45/11, 46/45/11 | 640.1 / 640.1 / 626.4 / 626.4 | 473/473 each | 109,957 each (23 states with unseen vectors) | u_b3, u_b1: 137,984 |

On the fresh sample there are 416 distinct feature vectors and 0 conflicting ones.

**What the tree decides:** only the 40-valued **template** (step tag + rule head). It does not choose the formula or the
cited lines. Its features come from `features.py`, which runs the whole per-step policy (`Policy(toks).act()`, "only to
read the frame analysis") and also encodes Kalmár's case table (`needed_children`). The extractor is 3,962 DEFLATE bytes
mechanically minified. The golfed per-step policy itself is 1,654.

**3e. Levin's Kt** (`rv_kt.py`; program bits = 8 × DEFLATE bytes; time = mean Python calls per theorem on my sample):

| program | Kt (bits) | program bits | log2 time |
|---|---:|---:|---:|
| K-sl algorithm | 6,921 | 6,912 | ≈ 9 (mean 507 calls) |
| K-sl + `lean_seq` rendering | 10,787 | 10,776 | ≈ 11 |
| K-tt algorithm | 3,033 | 3,024 | ≈ 9 |
| K-tt + Lean rendering | 6,938 | 6,928 | ≈ 9.6 |

The log-time term is ≈ 0.1 % of Kt: **Kt is program length to within 11 bits.**

## 4. Q2 — calibration and rank agreement (`rv_mech.py`, `rv_calib.py`)

- **Correctness of the calibration programs:**
  - Python (golfed, with and without builtins): 2,000 / 2,000 on my own random cases each;
  - BLC: 300 / 300 each (above);
  - RASP calibration programs, my graph walk (ops including selects / attention depth / flagged): copy 7/3/0,
    reverse 6/2/0, sort 2/1/0 (unique tokens) and 14/2/1 (repeats), parity 3/1/1 (flagged count arithmetic) and 31/5/0
    (scratchpad), addition 60/7/0, eval 61/13/1, **taut 63/13/41**; Kalmár sl decision 492/41/96.
- **Kalmár sl is the largest item in every language**:
  - Python DEFLATE 864 B vs taut 222;
  - BLC 5,443 vs taut 410 (13.3×);
  - CL 23,921 vs 1,430;
  - RASP-L 492 vs taut 63.
- **K-tt is second** in Python, BLC and CL (no RASP-L program). In BLC it is 4.0× taut.

**Spearman across languages** over the 9 items (copy, reverse, parity, sort, addition, eval, taut, Kalmár tt, Kalmár
sl), and over the 7 calibration items only:

| pair | ρ, 9 items | ρ, calibration only |
|---|---:|---:|
| Python DEFLATE (no-builtins) vs BLC | +0.97 | +0.93 |
| Python DEFLATE vs CL | +0.93 | +0.86 |
| Python DEFLATE vs RASP-L | +0.95 (n 8) | +0.93 |
| BLC vs CL | +0.98 | +0.96 |
| BLC vs RASP-L | +0.86 | +0.79 |
| Python raw with builtins vs BLC | +0.75 | +0.46 |

- With 9 items, much of the agreement comes from the two Kalmár programs being largest everywhere. **Within the 7
  calibration items** the languages still agree: ρ = +0.79 to +0.96, except Python *with* builtins, where sort is 9
  bytes (`s=sorted`).
- RASP-L ranks parity higher than Python does (parity with scratchpad 31 ops: rank 5 of 8, vs 7 of 9 in Python).
- **The K12 generator.** It is not golfed: `gen.py` mechanically minified, all knobs, is 5,324 DEFLATE bytes. That is
  6.2× the golfed K-sl but **2.2× the mechanically minified builder** (2,416), which is the like-for-like comparison
  available.

## 5. Q3 — absorbed bits

**5a. B1** (`rv_b1.py`, `rv_b1_logs.py`).

- **Token counts.** N is my own count from the data. I cut the canonical `lean_seq` into actions myself; loss tokens are
  action tokens + `<eos>`. The pair counts equal the checkpoints' `pairs` exactly.
- **Curves.** Read from the checkpoints with CPU torch. All 62 / 62 / 59 KAL-D points equal the printed
  `train_kalD_s*.log` lines.
- **What the logged loss is.** `train_loss` is the interval mean of the pre-update next-token loss on the action tokens
  (`mtp_loss(..)[1]`, the MTP auxiliary loss excluded), sampled every 20th step.
- **Formula.** L_preq = Σ_i loss_i × N × Δe_i / ln 2 over epoch 1.

| model | N loss tokens / epoch (own count) | pairs | curve points in epoch 1 | L_preq bits (interval mean) | bits/token | L_preq, next-point variant | EDL (a) final train | EDL (b) final held-out | EDL (c) end-of-epoch-1 train |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KAL-D s0 | 255,006,351 | 16,876,247 | 17 | 1.26e+07 | 0.0492 | 1.14e+07 | 6.97e+06 | 6.54e+06 | 1.67e+06 |
| KAL-D s1 | 255,006,351 | 16,876,247 | 17 | 1.24e+07 | 0.0488 | 1.13e+07 | 6.78e+06 | 6.27e+06 | 2.09e+06 |
| KAL-D s2 | 255,006,351 | 16,876,247 | 16 | 1.24e+07 | 0.0487 | 1.12e+07 | 7.31e+06 | 7.06e+06 | 2.12e+06 |
| control s0 | 19,375,057 | 1,239,995 | 12 | 3.79e+06 | 0.1955 | 2.56e+06 | 2.55e+06 | 1.47e+06 | 1.45e+06 |
| control s1 | 19,375,057 | 1,239,995 | 12 | 3.64e+06 | 0.1877 | 2.45e+06 | 1.93e+06 | 1.7e+06 | 1.57e+06 |
| control s2 | 19,375,057 | 1,239,995 | 12 | 3.87e+06 | 0.1997 | 2.59e+06 | 2.63e+06 | 1.61e+06 | 1.35e+06 |

- **KAL-D.** L_preq ≈ **1.25 × 10⁷ bits** (3 seeds within 1.3 %). Its absorbed bits depend on the choice of residual:
  ≈ 7 × 10⁶ against the final train or held-out loss, but ≈ 2 × 10⁶ against the end-of-epoch-1 loss. KAL-D > control
  on every seed under every residual.
- **Discretisation.** Taking each interval's loss from the next point instead of the interval mean moves KAL-D by −9 %
  but the control by **−33 %**. The control's first logged point (step 196, 3 % of its epoch) averages 1.34 nats/token,
  so its total is sensitive to the first interval.

**5b. B1-snap** (`rv_snap_cpu.py`, `rv_b1snap.py`).

- **CPU re-score.** My own fp32 scoring loop on KAL-D s0 (local checkpoint) over the first 30 tf1200 records (4,405
  states) reproduces the pod's per-state code. The total is within **0.03 %**, the median |Δ| is 5 × 10⁻⁵ nats, and 56
  states differ by > 0.05 nats (bf16). Greedy exactness on these states is 93.8 % (base 0).
- **Integration.** I recomputed it from `b1_snap.json`'s raw per-tag nats with my own per-tag token counts. The sum over
  types of the snapshot-based code for steps 24,020 → 178,581 is **1.11 / 1.16 / 1.11 × 10⁷ bits** (s0/s1/s2). The
  logged training curve over the same window gives **0.98 / 0.97 / 0.96 × 10⁷**, so the held-out, base-0 snapshot
  approximation is 13–20 % above the training stream.
- **Excess bits by type.** Σ excess is 6.0 / 6.4 / 6.4 × 10⁶. Per type, the largest totals are →I-B, lem, ¬¬ and →−.
  The largest per token are ∧+, ¬⊥, →I-A, ∨+ and ¬¬ (≈ 0.05–0.10 bits/token).
- **Snapshot losses barely improve in epoch 1.** Held-out code per token: s0 0.0379 → 0.0383 → 0.0342 at steps
  24,020 / 100,000 / 200,000, and 0.0163 at the end.

**5c. B2** (`rv_b2.py`).

- **Inputs.** Block token counts were recomputed from the data for all 13 jobs: **every block's `loss_tokens` equals
  my count** (kal / k12 own segmentation; eval 32 per theorem), and block 0's uniform code equals tokens × log2 111.
- **Protocols.** All Kalmár jobs are **v1** (4 evaluations of patience). K12 and eval were re-run as **v2** (patience
  3,000 steps, no stop before 5,000) at S / M / L; their v1 runs exist only at L.

| job | task | size | seed | protocol | L_preq bits | N loss tokens | L∞ bits/token | EDL bits | block-0 share of L / of EDL | at 8,192 thm: L / EDL | blocks at the step cap | training GPU-h (sum of block `secs`) |
|---|---|---|---:|---|---:|---:|---:|---:|---|---|---:|---:|
| eval_L_s0 | eval | L | 0 | v1 (4 evals) | 2.227e+05 | 524,288 | 0.1051 | 1.676e+05 | 0.06 / 0.08 | 1.194e+05 / 1.615e+04 | 5/9 | 1.18 |
| k12_L_s0 | k12 | L | 0 | v1 (4 evals) | 3.873e+05 | 2,055,332 | 0.1012 | 1.792e+05 | 0.14 / 0.29 | 2.7e+05 / 1.538e+05 | 4/9 | 1.39 |
| kal_L_s0 | kal | L | 0 | v1 (4 evals) | 1.374e+06 | 13,541,714 | 0.0233 | 1.059e+06 | 0.56 / 0.73 | 1.374e+06 / 1.059e+06 | 3/8 | 3.22 |
| kal_M_s0 | kal | M | 0 | v1 (4 evals) | 1.69e+06 | 27,100,176 | 0.0217 | 1.102e+06 | 0.46 / 0.70 | 1.395e+06 / 1.1e+06 | 4/9 | 2.76 |
| kal_M_s1 | kal | M | 1 | v1 (4 evals) | 1.771e+06 | 27,100,176 | 0.0255 | 1.078e+06 | 0.44 / 0.71 | 1.444e+06 / 1.118e+06 | 5/9 | 1.86 |
| kal_S_s0 | kal | S | 0 | v1 (4 evals) | 3.369e+06 | 27,100,176 | 0.0756 | 1.319e+06 | 0.23 / 0.58 | 2.346e+06 / 1.325e+06 | 5/9 | 1.28 |
| kal_S_s1 | kal | S | 1 | v1 (4 evals) | 3.375e+06 | 27,100,176 | 0.0708 | 1.457e+06 | 0.23 / 0.52 | 2.436e+06 / 1.497e+06 | 5/9 | 0.99 |
| v2_eval_L_s0 | eval | L | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 1.717e+05 | 524,288 | 0.1051 | 1.166e+05 | 0.08 / 0.12 | 1.07e+05 / 4.233e+04 | 9/9 | 1.94 |
| v2_eval_M_s0 | eval | M | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 1.631e+05 | 524,288 | 0.0241 | 1.505e+05 | 0.09 / 0.09 | 9.548e+04 / 2.79e+04 | 9/9 | 1.18 |
| v2_eval_S_s0 | eval | S | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 1.772e+05 | 524,288 | 0.1887 | 7.824e+04 | 0.08 / 0.17 | 1.033e+05 / 2.951e+04 | 9/9 | 0.45 |
| v2_k12_L_s0 | k12 | L | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 3.877e+05 | 2,055,332 | 0.1014 | 1.793e+05 | 0.14 / 0.29 | 2.692e+05 / 1.518e+05 | 7/9 | 2.00 |
| v2_k12_M_s0 | k12 | M | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 4.234e+05 | 2,055,332 | 0.0998 | 2.183e+05 | 0.12 / 0.24 | 3.004e+05 / 1.784e+05 | 7/9 | 1.23 |
| v2_k12_S_s0 | k12 | S | 0 | v2 (patience 3,000 steps, ≥ 5,000) | 6.449e+05 | 2,055,332 | 0.1574 | 3.215e+05 | 0.08 / 0.16 | 4.654e+05 / 2.876e+05 | 9/9 | 0.60 |

(At 8,192 theorems: L / EDL of the 8,192-prefix, with L∞ = the per-token code of the block that starts at 8,192.)

- **Kalmár's B2 "absorbed bits" are mostly the uniform code of the first 64 theorems.**
  - Block [0, 64) holds 113,516 loss tokens at log2 111 ≈ 6.79 bits each, 0.77 × 10⁶ bits.
  - That is **73 %** of size L's EDL at 8,192 theorems, **69–70 %** of size M's and **51–58 %** of size S's.
  - Without block 0, size L's EDL at 8,192 is ≈ 0.29 × 10⁶ bits.
  - K12's share is 29–34 % (L). Eval's is 8–17 % at 16,384 and 32–81 % at 8,192.
- **Size dependence at 8,192 theorems:**
  - S (2.35 / 2.44 × 10⁶) is far above M (1.39 / 1.44 × 10⁶); that gap is far outside the seed spread.
  - **L (1.374 × 10⁶) is below M s0 by 0.021 × 10⁶, inside M's seed-to-seed spread of 0.049 × 10⁶.** By the
    pre-registered rule, L < M is not established.
- **Kalmár vs K12 vs eval, EDL at 8,192 theorems:** Kalmár L 1.06 × 10⁶ > K12 L 1.52–1.54 × 10⁵ > eval L
  1.6 × 10⁴ (v1) / 4.2 × 10⁴ (v2). Kalmár has 13.5 M loss tokens there, K12 1.0 M and eval 0.26 M.
- **Shape.** Kalmár's per-block code per token falls monotonically, and so does its cumulative EDL / N
  (5.6–5.9 → 0.04–0.08 bits per token, every size and seed). There is no rise-then-fall. Eval's cumulative EDL / N *rises* at
  the last prefix, because its asymptote model codes 0.024–0.105 bits/token against 0.25–0.39 before.
- **Training rarely stopped early.** Most blocks stopped at the step cap: Kalmár 3–5 of 8–9, v2 7–9 of 9.
- **Per type** (bits per occurrence, prequential blocks, seed 0):
  - highest: ∧+ (S 9.0, M 4.1, L 6.1 bits), ∨+, `pr` (premise lines), →I-B, ¬⊥;
  - lowest: close (≈ 0.1–0.2), end, lem.

## 6. Q4 — which measure predicts KAL-D's per-type error (`rv_states.py`, `rv_q4.py`)

**My state table.** The builder is re-run per tf1200 record (proof text and tags equal the record's), and the actions
are walked in state-environment order. I keep my own scope stack and split valuation. My per-state demand measures
**equal the executor's on all 137,984 states**: explored (lookups of the focus search), focus height, target height,
declared-formula length, action length and depth.

**Outcome.** kalmar-pretrain's stored agree strings (`artifacts/kalmar/tf/*__tf1200.json`), joined by record name and
position (lengths checked per record). Types: 15, with ≥ 500 states, `close:*` grouped.

| step type | states | KAL-D s0 / s1 / s2 error | mean | KAL-D+A mean | KAL-C s0 |
|---|---:|---|---:|---:|---:|
| close | 44,290 | 0.0035 / 0.0142 / 0.0064 | 0.0081 | 0.0015 | 0.0113 |
| efq | 9,286 | 0.0141 / 0.0181 / 0.0162 | 0.0161 | 0.0021 | 0.0074 |
| end | 1,200 | 0.0042 / 0.0192 / 0.0058 | 0.0097 | 0.0039 | 0.0100 |
| leaf:and+ | 1,427 | 0.3959 / 0.3854 / 0.2558 | 0.3457 | 0.1023 | 0.3840 |
| leaf:and- | 9,336 | 0.0679 / 0.1065 / 0.1016 | 0.0920 | 0.0302 | 0.0978 |
| leaf:bot- | 639 | 0.3599 / 0.2300 / 0.1847 | 0.2582 | 0.1064 | 0.2426 |
| leaf:imp+A | 5,295 | 0.1027 / 0.1095 / 0.1058 | 0.1060 | 0.0258 | 0.1246 |
| leaf:imp+B | 11,908 | 0.1816 / 0.1689 / 0.1460 | 0.1655 | 0.0255 | 0.1704 |
| leaf:imp- | 6,240 | 0.0712 / 0.0822 / 0.0787 | 0.0774 | 0.0161 | 0.1276 |
| leaf:not+ | 5,884 | 0.0785 / 0.1074 / 0.0901 | 0.0920 | 0.0249 | 0.1547 |
| leaf:or+ | 4,520 | 0.2770 / 0.2854 / 0.2095 | 0.2573 | 0.0715 | 0.2657 |
| leaf:or- | 4,536 | 0.0725 / 0.1052 / 0.0754 | 0.0844 | 0.0240 | 0.0836 |
| lem | 23,086 | 0.0014 / 0.0094 / 0.0015 | 0.0041 | 0.0000 | 0.0022 |
| pr | 1,409 | 0.1299 / 0.0688 / 0.0575 | 0.0854 | 0.0007 | 0.0525 |
| split | 8,900 | 0.0343 / 0.0226 / 0.0330 | 0.0300 | 0.0023 | 0.0227 |

| predictor (per step type, n = 15) | source | ρ vs KAL-D mean error (perm. p) | s0 / s1 / s2 | vs KAL-D+A mean | partial ρ given log frequency (p) |
|---|---|---|---|---|---|
| b2_bits_per_occ_S | own | +0.85 (0.000) | +0.91 / +0.83 / +0.84 | +0.60 | +0.78 (0.001) |
| exec_rasp_eff_depth | executor (`rasp_per_type.json`) | +0.85 (0.000) | +0.74 / +0.87 / +0.89 | +0.90 | +0.85 (0.000) |
| exec_rasp_cone_depth | executor (`rasp_per_type.json`) | +0.84 (0.000) | +0.75 / +0.89 / +0.91 | +0.91 | +0.84 (0.000) |
| b2_bits_per_occ_L | own | +0.84 (0.000) | +0.93 / +0.80 / +0.80 | +0.55 | +0.75 (0.003) |
| b2_bits_per_occ_M | own | +0.82 (0.001) | +0.92 / +0.77 / +0.77 | +0.52 | +0.71 (0.004) |
| exec_rasp_cone_ops | executor (`rasp_per_type.json`) | +0.82 (0.000) | +0.73 / +0.87 / +0.89 | +0.89 | +0.81 (0.000) |
| explored | own | +0.82 (0.000) | +0.77 / +0.86 / +0.88 | +0.85 | +0.79 (0.000) |
| exec_log2_ops | executor (`states_tf1200`, policy ops) | +0.78 (0.001) | +0.69 / +0.81 / +0.82 | +0.84 | +0.76 (0.001) |
| target_h | own | +0.78 (0.001) | +0.72 / +0.79 / +0.83 | +0.79 | +0.78 (0.001) |
| tree_path | own | -0.76 (0.002) | -0.65 / -0.80 / -0.82 | -0.85 | -0.71 (0.002) |
| log_freq | own | -0.60 (0.018) | -0.68 / -0.61 / -0.50 | -0.56 | — |
| py_bytes | own | -0.55 (0.038) | -0.62 / -0.52 / -0.46 | -0.43 | -0.08 (0.771) |
| act_len | own | +0.52 (0.049) | +0.55 / +0.55 / +0.55 | +0.33 | +0.59 (0.019) |
| focus_h | own | +0.49 (0.069) | +0.44 / +0.59 / +0.62 | +0.50 | +0.59 (0.016) |
| decl_len | own | +0.42 (0.121) | +0.47 / +0.39 / +0.43 | +0.15 | +0.53 (0.041) |
| depth | own | +0.27 (0.332) | +0.16 / +0.34 / +0.39 | +0.39 | +0.48 (0.066) |
| exec_rasp_descent | executor (`rasp_per_type.json`) | +0.25 (0.364) | +0.29 / +0.20 / +0.12 | +0.18 | -0.19 (0.503) |

Notes on the predictors:

- `py_bytes` is my byte count of the executor's per-type snippets of `ksl_alg.py` (the mapping is theirs).
- `b2_bits_per_occ_*` is B2's Kalmár per-tag bits over the prequential blocks, divided by my occurrence counts.
- `tree_path` counts the tests on `tree_u_b3`'s path for each tf1200 state.
- The `exec_rasp_*` values are means over the executor's 1,000-theorem *training-distribution* sample
  (seed 20261020), not over tf1200. I did not recompute them.
- No per-type BLC predictor exists in the artefacts.

Further checks:

- **Within the 9 `leaf:*` types** (n = 9; |ρ| ≥ 0.68 for p ≈ 0.05):
  - positive: RASP effective depth +0.92 (p 0.001), target height +0.82 (0.011), B2 bits M / L +0.83 / +0.80,
    explored +0.67 (0.06);
  - negative: program-snippet bytes **−0.80** (0.014), depth −0.87, tree path −0.82;
  - decl_len +0.42 (0.27).

  Across all 15 types, a large share of every positive ρ comes from separating the 9 leaf types (high error) from the
  6 structural ones.
- **Snapshot code vs error.** KAL-D's final per-type code (B1-snap) ranks the types like their error at
  ρ = +0.88 / +0.63 / +0.63 (s0/s1/s2), +0.73 pooled.
- **State level.** A logistic regression of error on 15 type dummies ± 6 standardised demand measures, LR test with
  df 6:
  - LR = 6,530 / 7,502 / 5,888 (p ≈ 0) for s0 / s1 / s2;
  - the best single measure is explored (LR 4,936–6,374), then target height.
  - These χ² p-values treat 137,984 states as independent; states are clustered in 1,200 proofs.

## 7. B3 — focus-given states (`rv_b3.py`; my own opener classification from `rv_states.py`)

- **The opener count matches:** my count, 23,573, equals the executor's `class:opener` count in every B3 file. Per-type
  errors equal the files' `type:*` errors (max |Δ| 1e-16).
- **Every opener action declares the focus formula.** At **all 23,573 / 23,573** opener states, the formula the next
  action declares is **exactly the focus formula or its negation** (`decl_eq`). So FOC inserts, as a copyable span, the
  formula the step must write (up to a leading ¬). It does not insert only "where the search is".

| quantity | STD s0 / s1 / s2 | FOC s0 / s1 / s2 | 3-seed means STD → FOC | relative change (of means; per seed) |
|---|---|---|---|---|
| opener-state error (23,573 states) | 0.3349 / 0.3079 / 0.3160 | 0.0154 / 0.0232 / 0.0196 | 0.3196 → 0.0194 | -0.939; -0.954, -0.925, -0.938 |
| other-state error (114,411) | 0.0248 / 0.0194 / 0.0289 | 0.0161 / 0.0183 / 0.0165 | 0.0244 → 0.0170 | -0.303; -0.349, -0.058, -0.429 |
| all states | 0.0777 / 0.0687 / 0.0780 | 0.0160 / 0.0191 / 0.0170 | 0.0748 → 0.0174 | -0.768; -0.794, -0.722, -0.782 |
| other states without `pr` | 0.0167 / 0.0113 / 0.0210 | 0.0081 / 0.0103 / 0.0085 | 0.0163 → 0.0089 | -0.453; -0.518, -0.087, -0.597 |
| `pr` states (1,409) | 0.669 / 0.671 / 0.664 | 0.662 / 0.659 / 0.663 | | |

| step type | states | opener states | STD error (mean) | FOC error (mean) | relative change | mean `explored` |
|---|---:|---:|---:|---:|---:|---:|
| close | 44,290 | 0 | 0.0044 | 0.0019 | -0.56 | 0.23 |
| efq | 9,286 | 0 | 0.0167 | 0.0072 | -0.57 | 1.00 |
| end | 1,200 | 0 | 0.0233 | 0.0183 | -0.21 | 0.00 |
| leaf:and+ | 1,427 | 1,427 | 0.4681 | 0.0315 | -0.93 | 4.43 |
| leaf:and- | 9,336 | 3,112 | 0.0975 | 0.0088 | -0.91 | 1.20 |
| leaf:bot- | 639 | 639 | 0.3672 | 0.0000 | -1.00 | 3.45 |
| leaf:imp+A | 5,295 | 1,765 | 0.1324 | 0.0254 | -0.81 | 1.18 |
| leaf:imp+B | 11,908 | 5,954 | 0.1590 | 0.0205 | -0.87 | 1.48 |
| leaf:imp- | 6,240 | 2,080 | 0.1170 | 0.0129 | -0.89 | 1.25 |
| leaf:not+ | 5,884 | 2,942 | 0.1801 | 0.0039 | -0.98 | 1.79 |
| leaf:or+ | 4,520 | 4,520 | 0.3174 | 0.0360 | -0.89 | 3.24 |
| leaf:or- | 4,536 | 1,134 | 0.1132 | 0.0167 | -0.85 | 1.22 |
| lem | 23,086 | 0 | 0.0239 | 0.0149 | -0.38 | 0.00 |
| pr | 1,409 | 0 | 0.6681 | 0.6615 | -0.01 | 0.00 |
| split | 8,900 | 0 | 0.0336 | 0.0112 | -0.67 | 0.00 |

Spearman across the 15 types of error vs mean `explored`:

| arm | s0 | s1 | s2 | 3-seed mean |
|---|---|---|---|---|
| STD | +0.60 (p 0.021) | +0.63 (p 0.015) | +0.62 (p 0.017) | +0.61 (p 0.020) |
| FOC | −0.11 (p 0.695) | −0.08 (p 0.776) | −0.13 (p 0.633) | −0.02 (p 0.947) |

- **All six models stopped at the 20,000-step cap.** Their best validation step was 19,000 or 20,000, and none
  early-stopped. The two arms are matched on steps and on training tokens (3.665 × 10⁸ each).
- **The `pr` read-out is an artefact.** `pr` states are wrong about 66 % of the time in both arms, against 6–13 % for
  KAL-D. The reason: at name base 0 nothing in a premise state tells the model the base it must write.
- **Other-state error falls under FOC as well.** The other states are identical in both arms. Without `pr`, their error
  falls 45 % (3-seed means), with per-seed falls of 52 %, 9 % and 60 %.

## 8. Compute (from the pods' logs and JSON; `out/compute_jobs.json`)

- **Hardware:** three A40 pods: kc-1 13:17, kc-2 13:18, kc-3 16:00.
- **Jobs:** 26, with 27.1 h of summed job wall-clock. Jobs shared GPUs: for example, the six B3 jobs ran together on
  kc-3 for ≈ 1.0 h each. So job wall-clock is not exclusive GPU-seconds. The run's own spend file states 8.46 pod-hours
  (not yet reconciled by me).
- **B2 training seconds** (sum of block `secs`): Kalmár L 3.22 h, M 2.76 / 1.86 h, S 1.28 / 0.99 h; K12 v1 L 1.39 h;
  v2 L / M / S 2.00 / 1.23 / 0.60 h; eval v1 L 1.18 h; v2 1.94 / 1.18 / 0.45 h.
- **B3:** 1.00–1.01 h of training each.
- **B1-snap:** 24 checkpoints, 1,086 s.
- No generated tokens and no Lean checks.

## 9. Pre-registered expectations against my recount

| quantity (pre-registered) | expected | my recount | verdict |
|---|---|---|---|
| K-sl algorithm, Python raw / DEFLATE / xz bytes | 1,300 (900–1,900) / 650 (450–900) / 650 (450–950) | 1,907 / 864 / 906 | raw just above the range; DEFLATE, xz in |
| K-sl rendering to `lean_seq`, DEFLATE | 350 (200–600) | 562 | in |
| K-tt algorithm + Lean rendering, DEFLATE | 600 (400–850) | 866 | just above |
| K-sl algorithm, Qwen3 tokens | 450 (300–700) | 897 | above |
| K-sl / K-tt algorithm, BLC bits | 3,000 (1,500–5,000) / 2,300 (1,200–4,000) | 5,443 / 1,636 | K-sl above; K-tt in |
| rendering, BLC bits | 1,000 (400–2,500) | ND 616; Lean 4,204 | ND in; Lean above |
| CL / BLC | 2.5 (1.5–4) | 4.4–6.1 for the Kalmár programs; 2.0–3.6 calibration | above for the large programs |
| RASP-L ops / attention depth | 130 (70–250) / 15 (8–30) | 492 (427 without selects) / 41; 96 flagged non-RASP-L | both above |
| decision procedure leaves / bits | 35 (15–80) / 400 (150–1,000) | 46–47 / 624–640 (template only) | in |
| feature extractor, DEFLATE | 500 (300–800) | 3,962 mechanical (it runs the whole policy; golfed policy 1,654) | above |
| calibration BLC: copy / reverse / parity / addition / sort / eval / taut | 4 / 50 / 50 / 200 / 250 / 200 / 350 | 4 / 87 / 82 / 375 / 257 / 273 / 410 | — |
| Kalmár's rank; ≥ 5× next in BLC | 1 everywhere; ≥ 5× | 1 in Python-DEFLATE, BLC, CL, RASP-L; 13.3× taut | as expected |
| K12 generator vs K-sl, Python DEFLATE | generator 1.2–3× larger | 2.2× (both mechanical); 6.2× vs golfed K-sl | not like-for-like; 2.2× in range |
| Python-DEFLATE vs BLC ρ; RASP-L disagrees on parity / addition | ≥ 0.8; disagreement | +0.97 (+0.93 calibration only); RASP-L ranks parity higher | as expected; mild disagreement |
| B1 KAL-D first-epoch code | 1.5 × 10⁷ (0.5–4 × 10⁷) | 1.24–1.26 × 10⁷ | in |
| B1 KAL-D EDL (residual = final train) | 6 × 10⁶ (10⁶–2 × 10⁷) | 6.8–7.3 × 10⁶ | in |
| B1 control EDL; KAL-D > control | 2 × 10⁶ (10⁵–10⁷); 60 % | 1.9–2.6 × 10⁶; KAL-D > control in 3/3 seeds, all residuals | in |
| absorbed / K-sl BLC bits, ≥ 100 for every estimate | ≈ 2,000 (100–20,000) | B1: 1,150–1,340 (a, b), 310–390 (c); B2 Kalmár: 195 (L), 198–202 (M), 242–268 (S) | ≥ 100 holds, but B2 L / M fall to ≈ 53–61 without block 0's uniform code |
| B2 Kalmár L, 8,192 theorems (Addendum 1) | L 3 × 10⁶ (0.6–12 × 10⁶); EDL ≥ 100 × BLC | 1.37 × 10⁶; EDL 1.06 × 10⁶ = 195× | in |
| B2 size dependence | L < M < S | S ≫ M; L < M inside the seed spread | partly: S > M only |
| B2 bits per occurrence | highest ∧+, ∨+, ¬⊥, →I-B; lowest close, lem, split | highest ∧+, ∨+, `pr`, →I-B, ¬⊥; lowest close, end, lem (split mid) | mostly |
| B2 EDL per token vs data | Kalmár rises then falls; K12 and eval fall monotonically | Kalmár falls monotonically; K12 falls; eval rises at the last prefix | miss |
| K12's EDL < Kalmár's; eval's below both (Addendum 1) | — | 1.5 × 10⁵ < 1.06 × 10⁶; eval 1.6–4.2 × 10⁴ | as expected |
| best predictor: computational demand, ρ ≥ 0.6 | declared-formula length or evaluation height | evaluation (target) height +0.78; RASP depth +0.85, lookups +0.82, B2 bits +0.85; **declared length only +0.42 (p 0.12)** | met by height and depth, not by declared length |
| program length vs error | \|ρ\| < 0.4 | snippet bytes −0.55 (p 0.04); −0.08 given frequency; −0.80 within leaf types | miss: negative and \|ρ\| > 0.4 |
| frequency baseline | ρ between −0.4 and −0.7 | −0.60 | in |
| B2 per-type bits vs KAL-D error | ρ ≥ 0.7 | +0.82 / +0.84 / +0.85 (M / L / S) | in |
| state level: demand adds to type | LR p < 0.01 per seed | LR 5,888–7,502, df 6 (states clustered) | as expected |
| B1-snap: final KAL-D per-type code ranks like error (Addendum 1) | Spearman ≥ 0.8 | +0.88 / +0.63 / +0.63, pooled +0.73 | miss (s0 only) |
| B3: opener error falls ≥ 50 % (falsified if < 25 %) | ≥ 50 % | −93.9 % (−92.5 to −95.4 % per seed) | in |
| B3: other-state error changes < 30 % | < 30 % | −30.3 % (−5.8 to −42.9 % per seed); −45 % without `pr` | miss |
| B3: ∧+, ∨+, ¬⊥, →I-B each fall ≥ 40 % | ≥ 40 % | −93 / −89 / −100 / −87 % | in |
| B3: Spearman error vs lookups STD ≥ 0.6 → FOC ≤ 0.3 | | +0.61 → −0.02 (3-seed means) | in (STD just at 0.6) |

## 10. Phase-1 findings (before reading the write-up)

1. **Every program reproduces its builder on a fresh sample, and Lean accepts its outputs.** This covers the Python,
   BLC, CL, RASP-L, decision-tree and per-step-policy programs.
   - Sample: 1,000 theorems (seed 271828), plus tf1200 for the trees.
   - Lean: 150 / 150 K-tt and 150 / 150 K-sl theorems.
   - My BLC/CL bit counts and Python byte/token counts equal the files'.
2. **The "RASP-L" program is RASP-L plus flagged extensions.**
   - 96 of its 492 operations are non-RASP-L by the executor's own interpreter: 16-bit truth-table values and
     multi-field selects.
   - So is 41 / 63 of the taut calibration program.
   - A "RASP-L length" or "attention depth" for Kalmár or taut is a length in this extended language, not in RASP-L.
3. **The decision tree decides a template, not an action.** Its 40 labels are tag + rule head. Its features come from
   an extractor that runs the full per-step policy and encodes Kalmár's case table: 3,962 DEFLATE bytes as written,
   1,654 golfed. The ≈ 630 tree bits are therefore conditional on most of the algorithm.
4. **B2's absorbed bits for Kalmár are mostly a coding convention.**
   - 70–73 % (L, M) of the EDL at 8,192 theorems is block 0's uniform code.
   - "Absorbed ≥ 100 × the program" holds for B2 L / M only because of it.
   - L < M is not established (inside M's seed spread).
   - Kalmár's B2 numbers come from the v1 early-stopping protocol, while K12 and eval have v2 runs. Comparing tasks
     across protocols mixes two training procedures. For K12 at L, v1 and v2 agree within 0.1 %; for eval at L, v2's
     L_preq is 23 % below v1's.
5. **B1.** Reproduces from the raw curves with my own token counts: KAL-D ≈ 1.25 × 10⁷ bits; EDL 6.3–7.3 × 10⁶
   (residuals a, b) or 1.7–2.1 × 10⁶ (c). The control is sensitive (−33 %) to how its first logged interval is treated.
6. **Q4 reproduces, and the inputs are exact.** My independent state measures equal the executor's on every state.
   - Lookups correlate +0.82 with per-type error, RASP effective depth +0.85, B2 bits +0.82–0.85. Program-snippet
     length is *negative* (−0.55; −0.80 within leaf types).
   - The 15-type ρ is driven largely by leaf vs structural types. Within the 9 leaf types, depth-type measures still
     hold (+0.80 to +0.92) and lookups weaken (+0.67, p 0.06).
7. **B3 reproduces exactly, but the manipulation hands the model the formula.**
   - Openers: −93.9 % (3 paired seeds); lookups–error ρ +0.61 → −0.02. Other states also improve (−30 %; −45 %
     without the base-0 `pr` artefact).
   - At every opener state, the inserted focus is the formula the action declares, or its negation. So FOC removes
     both the choice of the next subformula and the composition of the formula to write.
   - All six models stopped at the 20,000-step cap.
