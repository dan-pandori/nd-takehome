# ds-generator sets (proposal 9, run 2) — `data/dsg/`

Built 2026-09-22 06:21–06:25 UTC on pods dsg-2 (G1) / dsg-3 (G2), 31 CPU cores each (`pod/dsg/gen.sh`; logs and JSON
reports under `artifacts/dsg/`: `gen_*_stats.json`, `merge_*.txt`, `assemble_*.json`, `shape_*.json`, `overlap_*.json`,
`render_*.json`). The sets themselves (`train_g1.jsonl`, `train_g2.jsonl`, 155,000 records each) and the raw pools are not in
git; they are in the bucket `hf://buckets/dan-pandori/nd-rl/ds-generator/data/dsg/`. Every record is generator output verified
by `nd_verify` at generation, at assembly and (cap 6) by `train.py --cap 6`; no proof was hand- or LLM-written.

## Knob diff against the control generator (`gen.py`; control path byte-identical, see log.md 06:05)

| knob | control (a1 set, `sample_one` default) | G1 | G2 (as run) |
|---|---|---|---|
| `Gen.ore_steps` (forward steps in `ORE` branch 1) | 1 | **3** | 3 |
| `Gen.ore_boxes` (branch 1 takes full `step()`s: AS / close / nested ORE under `max_depth` 3, branch box protected by a floor) | off | **on** | on |
| mode mix | 45 % goal / 55 % forward | same | **50 / 50** |
| `Gen.strict` (no lazy `( Z > G )` / `G` fallback in `reach`; `finish` rejects `ANDI` / `ORI` / `BOTE` / `R` conclusions and any `F` in the theorem) | off | off | **on** |
| `bot_p` (probability of `F` as a sub-formula) | 0.02 | 0.02 | **0** |
| goal-mode `reach` budget / goal depth | {1,2,3} / {1,2,2,3} | same | **{3,4,5} / {2,3,3}** |
| forward steps | 1–10 | same | **6–22** |
| contradictory-premise theorems | kept | kept | **dropped** at generation |
| flags (`make_coverage_sets.py gen`) | none | `--ore_steps 3 --ore_boxes` | `--ladder --drop_contra --ore_boxes` (`--ladder` = `sample_one(long=True)`'s settings, the generator that built `data/ladder/`) |
| output caps at generation (`--cap_np`, `--cap_pat`) | 1,500 / 3,000 per worker (control pool `pool_cap6_recon`) | none (10⁹) | none |
| tries / seed | – | 6 M / 20000 | 30 M / 30000; fill pool (G1 knobs) 6 M / 40000 |

Assembly (`dsg_assemble.py`, seed 0): 31,000 per pruned length 2–6, uniform draw from the non-depth-3 proofs (depth-3 tested in
pruned and written form with `patterns.classify`), classes of every evaluation pool and validation-36 excluded. G2's 2- and
3-line bins could not be filled from its own pool (class saturation at 30 M tries) and were filled from the G1-knob fill pool as
pre-registered; every record carries `src` (`main` / `fill`). The control set `data/p2/train_depth3_f0_a1.jsonl` was assembled
by `make_coverage_sets.py assemble` (seed 1) from the capped control pool with the other two patterns held at the campaign's
natural baseline; it is the lean-format a1 set, unchanged.

Not in the brief's G2: the brief's literal G2 (100 % goal mode + strict) was probed and found degenerate (84 % reductio proofs,
2 / 3 / 4-line bins unfillable); see `preregistration/ds-generator.md` and `QUESTIONS.md` (2026-09-22).

### Shape table (per set, 155,000 proofs; shares in %; `dsg_shape.py`)

| quantity | C0 (a1) | G1 | G2 |
|---|---|---|---|
| length 2 / 3 / 4 / 5 / 6 | 31000 / 31000 / 31000 / 31000 / 31000 | 31000 / 31000 / 31000 / 31000 / 31000 | 31000 / 31000 / 31000 / 31000 / 31000 |
| box depth 0 / 1 / 2 / 3 | 53.2 / 35.4 / 11.4 / 0.0 | 52.2 / 34.7 / 13.1 / 0.0 | 23.0 / 45.4 / 31.6 / 0.0 |
| proofs with `AS` | 46.8 | 47.8 | 77.0 |
| proofs with `R` | 2.8 | 2.6 | 0.7 |
| proofs with `ANDI` | 22.9 | 22.4 | 15.0 |
| proofs with `ANDE1` | 2.2 | 2.2 | 5.4 |
| proofs with `ANDE2` | 2.1 | 2.2 | 5.2 |
| proofs with `ORI1` | 20.6 | 20.9 | 22.3 |
| proofs with `ORI2` | 20.3 | 21.1 | 22.1 |
| proofs with `ORE` | 1.5 | 0.9 | 0.3 |
| proofs with `IMPI` | 36.4 | 38.5 | 70.1 |
| proofs with `IMPE` | 40.2 | 38.8 | 9.8 |
| proofs with `NEGI` | 9.9 | 9.3 | 8.7 |
| proofs with `NEGE` | 12.0 | 11.4 | 10.6 |
| proofs with `DN` | 8.3 | 7.7 | 9.0 |
| proofs with `BOTE` | 1.9 | 2.2 | 1.8 |
| proofs with `ORE` (n) | 2256 (1.46) | 1374 (0.89) | 524 (0.34) |
| box inside an `ORE` branch (n) | 49 (0.03) | 52 (0.03) | 23 (0.01) |
| premises 0 / 1 / 2 / 3 | 12.3 / 39.6 / 42.6 / 5.5 | 12.6 / 40.3 / 42.1 / 4.9 | 35.5 / 50.7 / 13.7 / 0.0 |
| mean premises | 1.41 | 1.39 | 0.78 |
| mean lazy premises (labelled proofs) | not labelled | 0.68 (155000) | 0.29 (155000) |
| contradictory-premise theorems | 6.06 | 6.12 | 0.15 |
| final rule IMPI / IMPE / DN / ORI / ANDI / other | 34.0 / 16.2 / 6.4 / 24.9 / 12.3 / 6.2 | 38.1 / 15.8 / 5.6 / 24.2 / 10.8 / 5.5 | 70.0 / 7.2 / 5.8 / 13.3 / 1.8 / 1.8 |
| pattern proofs: reductio / derived-ORE / depth-3 | 10547 / 88 / 0 | 9374 / 57 / 0 | 8956 / 34 / 0 |
| mean tokens ND / Lean (`lean_seq`) | 112.6 / 138.4 | 113.4 / 139.0 | 125.1 / 148.6 |

### Assembly and render check

| set | source pool classes | usable non-depth-3 per length 2 / 3 / 4 / 5 / 6 | fill from G1-knob pool per length | render 3,000 round-trip / 1,000 Lean / 300 negatives |
|---|---|---|---|---|
| G1 | 745,885 read, 35,116 depth-3, 1,185 excluded | ≥ 31,000 / ≥ 31,000 / ≥ 31,000 / ≥ 31,000 / ≥ 31,000 | 0 / 0 / 0 / 0 / 0 = 0 (0.0 %) | 3000 / 1000 / 300 |
| G2 | 824,568 read, 265,067 depth-3, 520 excluded | 8421 / 15863 / ≥ 31,000 / ≥ 31,000 / ≥ 31,000 | 22,579 (73 %) / 15,137 (49 %) / 0 / 0 / 0 = 37,716 (24.3 %) | 3000 / 1000 / 300 |

### Overlap table (set records matching a pool theorem: order-sensitive `thm` / renaming class / premise-order-insensitive class; `dsg_overlap.py`)

| pool (n) | C0 (a1) | G1 | G2 |
|---|---|---|---|
| `data/p2/heldout.jsonl` (5,000) | 0 / 0 / 18 | 0 / 0 / 21 | 0 / 0 / 13 |
| `data/p2/targets_depth3.jsonl` (1,000) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `data/p2/transfer_depth3.jsonl` (500) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `data/p2/targets_reductio_req.jsonl` (300) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `data/p2/transfer_reductio_req.jsonl` (150) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `data/r3_1/depth3_req.jsonl` (300) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `data/r3_1/depth3_req_transfer.jsonl` (100) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `data/ladder/rl_targets.jsonl` (4,495) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `data/ladder/transfer.jsonl` (2,285) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| `data/train.jsonl` (154,990) | 1214 / 16047 / 16509 | 1111 / 14380 / 14858 | 854 / 11054 / 11223 |
| `data/transfer.jsonl` (1,638) | 1 / 7 / 9 | 0 / 13 / 14 | 1 / 14 / 14 |
| `data/rl_targets.jsonl` (3,000) | 2 / 19 / 19 | 0 / 21 / 21 | 1 / 28 / 30 |

## Resume phase, 2026-09-23/24 — what was rebuilt and what that costs you

The 2026-09-22 session was cut off mid-ladder and a host cleanup then deleted local `artifacts/` and `ckpts/`.
`data/dsg/` itself survived and is unchanged: `train_g1.jsonl` and `train_g2.jsonl` were re-fetched from the
bucket and are byte-identical to what the shape, overlap, assembly and render-check tables above describe
(155,000 lines each, verified on the pods).

**`ckpts/dsg/stage1_g{1,2}_s{0,1}.pt` in the bucket are retrained replicas**, not the 2026-09-22 originals (those
were never uploaded). Same set, same seed, same command line; different GPU class (RTX A6000 / RTX 4090 rather
than a 3090). They do **not** reproduce the originals: held-out greedy moves by −1.44, −4.44, −1.78 and +5.96 pp
respectively, and essentially all of the movement is in the 6-line bin (`numbers.md` § ds-generator G5). The same
comparison on a **byte-identical** checkpoint (C0, md5 verified) moves +0.00 / +0.08 pp, so this is training-run
variance rather than anything about the recovery or the sampler.

Consequence for anyone reading the tables: the **held-out and ladder** numbers for G1 / G2 are measured on the
retrained checkpoints; the **coverage (pass@2,000) and depth-3 dial** numbers are the 2026-09-22 measurements on
the originals. They are different draws of the same (set, seed) and the spread above is the scale on which to
read any difference between them.
