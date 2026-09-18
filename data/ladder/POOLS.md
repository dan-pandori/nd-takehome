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
