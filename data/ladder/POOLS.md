# ladder-A pools (built 2026-09-18 01:15–01:30 UTC on pod la-1, 32 vCPU; assembled on the VPS by `make_ladder_pools.py`)

Job: `pod/la/pool.sh`; logs `artifacts/ladder/{gen_long,textbook,gen_inj,minlen_long8,minlen_tb8,minlen_tb14,minlen_long14,pools}.log`;
summary `pools_summary.json`. Files here: `transfer.jsonl` (2,285), `rl_targets.jsonl` (2,295), `reserve.jsonl` (18,407, unused in
Phase A), label files `raw_textbook_minlen{8,14,}.jsonl`, `pool_long_minlen14.jsonl`, `pool_long_cand14.jsonl`; the 63k-theorem
generator pool and its bound-8 labels (`pool_long.jsonl`, `pool_long_minlen8.jsonl`, 57 + 34 MB) and the T5 injection pool
(`pool_inject_cap6.jsonl`) are not in git; they are uploaded to `hf://buckets/dan-pandori/nd-rl/ladder-A/data/ladder/`.

## Sources
- **Strict long generator**: `make_coverage_sets.py gen --long --min 7 --max 16` (the take-home generator, unchanged knobs
  max_prem 3 / max_depth 3, strict mode; output filter only), 32 workers × 40,000 tries, seed 7000: 70,524 verifier-accepted
  proofs of 7–16 lines (0 verifier rejects; 22,449 contradictory-premise theorems dropped), merged to **63,342** distinct
  renaming classes (155 validation-36 classes and 7,027 class duplicates dropped).
- **Textbook schemata**: `textbook_pool.py --n 3900 --seed 11` (26 schemata, random sub-formulas, ≤ 90 prompt tokens),
  excluding the classes of Stage-1 train / held-out, the take-home's `rl_targets` / `transfer` and validation-36:
  **3,797** instances (151 per schema; `dn_elim` 22).
- **T5 injection reservoir** (`pool_inject_cap6.jsonl`): `make_coverage_sets.py gen --min 2 --max 6`, unchanged generator,
  seed 9000, 16 workers × 12,000 tries: 41,146 distinct classes of verified ≤ 6-line proofs (validation-36 classes removed;
  classes of every ladder / take-home pool are excluded again at run time).

## True length (`L_true`)
`minlen.py`: iterative deepening over the 14 rules with Fitch semantics, hypotheses / lemmas / rule partners restricted to the
subformula closure of the theorem plus negations and double negations. Stage 1: bound 8, 10 s per theorem; a label 2–8 is
final (the search at every smaller bound terminated without a proof). Stage 2 on the stage-1 `None`s: bound **14**, 120 s.
Every proof found is checked with `nd_verify`.

| source | n | ≤ 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | unresolved at 14 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| generator | 63,342 | 43,017 | 12,443 | 5,406 | 1,776 | 508 | 140 | 40 | 8 | 4 | **0** (0 timeouts) |
| textbook | 3,797 | 1,065 | 760 | 203 | 303 | 787 | 122 | 375 | 87 | 91 | **4** (timeouts) |

**Caveat (on every table):** "no proof of length ≤ L−1" is a proof of non-existence *within the restricted formula space*,
not in general; a theorem's true minimal length can be lower if the only shorter proof uses a formula outside the closure.
Unresolved theorems are excluded from the pools and never counted. The prover bound is recorded per record (`minlen_bound`).

## Assembly (`make_ladder_pools.py`, seed 0)
Candidates: `7 ≤ L_true ≤ 14`, class not in the 164,664 excluded classes (Stage-1 train 154,990 + held-out 5,000, take-home
`rl_targets` 3,000 + `transfer` 1,638, validation-36; 65 generator and 1 textbook classes removed), deduplicated by class
across sources: **22,987**. Stratified by (source, schema, `L_true`), alternately assigned to transfer / targets; textbook strata
first with ≤ **40 instances per schema per pool**; `L_true` 7 and 8 capped at **300 per pool** (textbook counts toward the cap,
generator fills the rest) so the frontier bins are not drowned; everything else → `reserve.jsonl`. Assertions: the three pools
and the exclusion set are pairwise class-disjoint.

| pool | n | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | generator / textbook |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| transfer | 2,285 | 300 | 300 | 1,010 | 451 | 99 | 102 | 13 | 10 | 1,525 / 760 |
| rl_targets | 2,295 | 300 | 300 | 1,004 | 456 | 99 | 106 | 16 | 14 | 1,535 / 760 |
| reserve | 18,407 | 12,547 | 5,001 | 63 | 388 | 64 | 207 | 66 | 71 | 17,200 / 1,207 |

Textbook schemata present (40 per pool each): constructive_dilemma, contraposition, contraposition_conv, demorgan ×4,
disjunctive_syllogism, dist ×4, excluded_middle, export, import, negated_conditional(_conv), peirce, peirce_sequent (19).
Schemata whose instances all have `L_true ≤ 6` (explosion, hypothetical_syllogism, modus_tollens, dn forms, consequentia
mirabilis) are absent. By-source split per bin: `pools_summary.json` → `by_L_true_source`.

Record fields: `name, thm, key (renaming class), prompt, n_lines (= L_true, used for binning by the driver), L_true,
minlen_bound, source, schema, gen_lines, n_prem, rules, gen_proof (generator targets only: the generating proof, an upper
bound; read by T5 for shapes; never trained on)`.

## Amendment 01:50 UTC (before any rung result): RL-target pool v2
Round 1 of T1 s0 and T2 s0 (k = 32) accepted a proof for only **16 of 2,295** targets: the pool's `L_true` 7 bin was 236/300
textbook instances (contraposition, export, …, which the base model almost never writes) and only 64 generator theorems, so
expert iteration had almost no positives to train on. The targets are a *training* pool; to give every rung the same
foothold, **1,500 generator theorems at `L_true` 7 and 700 at `L_true` 8** were moved from the reserve into `rl_targets.jsonl`
(now **4,495**: 7: 1,800, 8: 1,000, 9: 1,004, 10: 456, 11: 99, 12: 106, 13: 16, 14: 14; generator 3,735 / textbook 760).
The transfer pool is unchanged. Class-disjointness re-asserted. The sample budget stays 256 per target (8 × 32).

# long-pool: `transfer_long.jsonl` — a transfer pool for the length frontier (run `long-pool`, 2026-09-28)

Built 18:48–21:35 UTC on pods `lp-l1` (RTX 4090, cpu.max 10.2 CPUs) and `lp-l2` (RTX 4090, cpu.max 54.4 CPUs); CPU pods
had no stock. Scripts: `pod/lp/label.sh` (generate + staged `minlen.py`), `lp_assemble.py` (labels, disjointness,
assembly), `lp_finalize.py` (Lean check of every label proof, re-read subset), `lp_shape.py`, `lp_stages.py`.
Files here: **`transfer_long.jsonl` (1,913)**, `transfer_long_rr600.jsonl` (the 100-per-bin seed-0 subset the run's
re-read used), `transfer_long_ge17.jsonl` (70 theorems with no proof ≤ 16 lines found: `L_true ≥ 17`, lower bound only,
not binned), `transfer_long_summary.json` (counts, timeouts, the disjointness table). Raw chunks and every label file:
`hf://buckets/dan-pandori/nd-rl/long-pool/data/lp/` (`<chunk>.jsonl`, `<chunk>_ml{10,12,14,16}.jsonl`).

## Sources (same families as the ladder's pools)
- **Strict long generator**, `make_coverage_sets.py gen --long` with take-home knobs (max_prem 3, max_depth 3, strict,
  contradictory premises dropped, pattern caps off), i.e. the ladder's command, with only the **output length
  filter** changed: long minimal proofs are rare and their rate rises with the generated length (theorems with `L_true`
  ≥ 13 are 2 per 12,601 at 12–15 generated lines against 1–2 % of theorems at ≥ 32 lines), so the chunks keep
  longer and longer generated proofs. The generator's probabilities are untouched; the generated length is recorded
  (`gen_lines`) and is ≥ `L_true`.

  | chunk | workers × tries | generated lines kept | seed | distinct classes |
  |---|---|---|---|---:|
  | g1 (pilot) | 10 × 100,000 | 12–40 | 31000 | 24,400 |
  | g2 | 48 × 1,000,000 | 20–60 | 32000 | 255,368 |
  | g3 | 48 × 5,000,000 | 28–80 | 33000 | 224,596 |
  | g4 | 48 × 6,000,000 | 32–90 | 34000 | 103,852 |
- **Textbook schemata**, `textbook_pool.py --n 3900 --seed 41` (unchanged), keeping the 6 schemata whose instances reach
  `L_true` ≥ 11 (906 instances): peirce (11), dist_and_over_or_conv / dist_or_over_and / negated_conditional (12),
  dist_or_over_and_conv (13), demorgan_nand_to_or (14). Each schema has one base length, so **no textbook schema reaches
  15 or 16**. Bins 15–16 are generator-only.

## True length (`L_true`)
The ladder's `minlen.py`, unchanged: iterative deepening over the 14 rules, with formulas restricted to the theorem's
subformula closure (same caveat as above). It is run in four stages. Each stage runs only on theorems the previous stage
searched completely without finding a proof:

| stage | bound / time | label if found | entered | timeouts |
|---|---|---|---:|---:|
| A | 10 / 5 s | ≤ 10 (dropped) | 609,122 | 1,003 (0.2 %) |
| B | 12 / 30 s | 11, 12 | 21,992 | 143 (0.7 %) |
| C | 14 / 120 s | 13, 14 | 4,518 | 136 (3.0 %) |
| D | 16 / 600 s | 15, 16 | 697 | 53 (7.6 %) |

A label L is final: the search at every smaller length finished without a proof. **A timeout at any stage = label unknown.**
Those theorems are excluded and never counted. A stage-D timeout could have been a 15, 16 or ≥ 17. Per-chunk detail is in
`artifacts/lp/stages.md`. Every label proof is checked twice. `minlen.py` checks it internally as a labelling tool (as
for the ladder). **Lean** checks it too (`lean_check.py --check --field minlen_proof`): **1,913 / 1,913 accepted**. The
term size by `lean_check`'s definition (`label_term_size`) is 4–16, median 9. `L_true` is ND-derived and is an **upper
bound under Lean**, like the ladder's labels: Lean may accept a shorter proof (e.g. `n.elim` on `n : ¬A`).

## Disjointness (renaming class = `gen.canon_key` over the prompt, premise order kept)
Candidates (16,906 labelled `L_true` ≥ 11 plus 70 at ≥ 17, 8 duplicate classes across chunks dropped) were checked against
**117 files, 5,736,567 records** (`artifacts/lp/excl_manifest.txt`). The files are:
- every `data/**/*.jsonl` in git: the ladder's transfer / rl_targets, held-out, all `data/p2` target and transfer pools,
  and the r1–r3 pools;
- the take-home `data/train.jsonl.gz`;
- all ten `data/p2/train_depth3_*` Stage-1 sets, including `train_depth3_f0_a1`, the C0 / state-env set;
- cap-horizon's K8add / K8flat / K10 / K12 / K14 sets;
- ds-composition's A1–A4 sets;
- ds-generator's G1 / G2 sets;
- the ladder's reserve, raw textbook and generator pools, and its T5 injection pool;
- validation-36.

**161 classes were excluded**: 156 textbook instances that coincide with the ladder's textbook / reserve / rl_targets /
transfer pools and with the reductio2 / run-5 pools (short schemata instantiated twice), and 5 generator classes (in the
ladder's `transfer.jsonl`, the run-5 cap-8 candidate / target pools, cap-horizon's K12 training set and the ladder generator
pool; one class may sit in several files). After exclusion the pool shares **0 classes** with every
file (asserted).

## Assembly (`lp_assemble.py`, seed 0)
For each bin 11–16: at most **300** generator theorems, drawn uniformly, plus textbook instances at ≤ **40 per schema per
bin** (the ladder's cap).

| bin | 11 | 12 | 13 | 14 | 15 | 16 | total | ≥ 17 (lower bound, separate file) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| labelled, generator (available) | 11,438 | 5,406 | 2,535 | 975 | 443 | 131 | | 70 |
| **pool** | **373** | **428** | **341** | **340** | **300** | **131** | **1,913** | 70 |
| of which textbook | 73 | 128 | 41 | 40 | 0 | 0 | 282 | 0 |

Shape (label proof = the `minlen` proof; `artifacts/lp/shape.md`):

| L_true | n | gen / textbook | premises (mean) | prompt tokens (median / max) | generated lines (median) | label term size (median, range) | max box depth (median / max) | label proofs using ORE / DN / NEGI / IMPI (%) |
|---|---:|---|---:|---|---:|---|---|---|
| 11 | 373 | 300 / 73 | 2.20 | 50 / 103 | 31.0 | 7 (4–13) | 2 / 4 | 37 / 23 / 19 / 88 |
| 12 | 428 | 300 / 128 | 2.14 | 50 / 107 | 30.0 | 9 (4–12) | 2 / 4 | 57 / 20 / 14 / 73 |
| 13 | 341 | 300 / 41 | 2.40 | 52 / 111 | 31.0 | 9 (5–12) | 2 / 4 | 69 / 16 / 4 / 84 |
| 14 | 340 | 300 / 40 | 2.49 | 53 / 97 | 33.0 | 10 (5–13) | 3 / 5 | 68 / 26 / 16 / 85 |
| 15 | 300 | 300 / 0 | 2.73 | 56 / 111 | 33.0 | 10 (6–15) | 3 / 5 | 87 / 23 / 7 / 96 |
| 16 | 131 | 131 / 0 | 2.79 | 56 / 102 | 33 | 11 (8–16) | 3 / 5 | 94 / 11 / 8 / 96 |

Compared with `transfer.jsonl` at 11–14 (median prompt 33–46 tokens, max 90), prompts are slightly longer: median 50–56,
max 111, which is within the old pool's overall maximum of 112. Longer bins use more ORE (37 % → 94 % of label proofs) and more premises.
Record fields are as for `transfer.jsonl`: `n_lines = L_true`, `minlen_bound`, `source`, `schema`, `gen_lines`, `n_prem`,
`rules`, `gen_proof` (generator only; an upper bound, never trained on). New fields: `minlen_proof`, `minlen_secs`,
`label_lean_ok`, `label_term_size`, `chunk`, `L_true_lb`.
**Numbers on this pool are not comparable with `transfer.jsonl` numbers.** It is a different theorem distribution, with
100–400 theorems per bin where the old pool had 10–102 at 11–14. That changes what `L*` (≥ 5 solved at ≥ L) means, so
report per-bin rates.
