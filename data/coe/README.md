# data/coe — run `create-or-elicit` (the knockout set, the family sets, the read sets)

Bulk files (`*.jsonl.gz`, `src/`) are in `hf://buckets/dan-pandori/nd-rl/create-or-elicit/data/coe/`, not in git. Every count
below is reproducible from the scripts named and the files listed.

## K12⁻ — the σ knockout (`train_k12ko.jsonl.gz`, `coe/coe_assemble.py`, report `train_k12ko_assemble_report.json`)

- **σ** = a double-negation (DN) step that cites a negation-introduction (NEGI) line (`patterns.reductio`). **σ⁺** = a DN
  step that cites any *derived* line (`patterns.derived_dn`), which contains σ. Both are checked on the written and on the
  dependency-pruned proof (`coe/coe_sigma.py`; in K12 they coincide for every record).
- **Input:** K12 = `cap-horizon/data/kh/train_k12.jsonl.gz` (gz md5 c5a8cd37…, 155,000 records).
- **Removed:** the 16,961 K12 records with σ⁺ (16,703 σ + 258 whose DN cites an IMPE / ORE / BOTE / DN / ANDE line), per
  pruned length 4: 19, 5: 2,453, 6: 2,381, 7: 1,215, 8: 1,047, 9: 1,906, 10: 1,853, 11: 3,007, 12: 3,080. Kept: 138,039.
- **Refill (16,961):** per length, as many records as were removed, drawn uniformly (seed 0) from the records of K12's own
  sources that K12 did not use: lengths ≤ 6 from `lean-format/data/p2/train_depth3_f0_a1.jsonl` (md5 29276f24…; K12's
  short bins are a uniform subsample of it), lengths ≥ 7 from `cap-horizon/data/kh/pool_long_kh.jsonl` (md5 6ee34f38…;
  K12's long bins are a uniform draw from its eligible records).
- **Filters on every refill record:** K12's own (`kh_assemble.py`: same length; box depth ≤ 2 in pruned and written form;
  outside K12's 11 exclusion pools; long bins outside the a1 set's classes); σ⁺-free in both forms; no "lemma route" (an
  IMPI box that applies DN to its ¬¬X hypothesis, used by IMPE on a NEGI-built ¬¬X — 0 in K12); not the renaming class of
  any K12 record, kept or removed; not in any of 91 evaluation pools (every non-training `.jsonl` under `data/`, `targets/`,
  `data/eval_only/textbook72/`: 54,328 `canon_key` classes, 54,211 premise-order-invariant classes); distinct among
  themselves under both keys. Scan counts: a1 93,000 in range → 44,258 eligible; long pool 401,030 in range → 197,750.
  The 11th K12 exclusion pool, `data/dsc/targets_depth3_sub250.jsonl`, was missing on this host at assembly; it is a subset
  of `p2/targets_depth3.jsonl` (250 / 250) and the refill has 0 matches with it (checked 2026-10-12).
- **Lean:** all 16,961 refill records accepted (`artifacts/coe/refill_lean_check.json`); controls: 200 / 200 accepted
  unchanged, 0 / 200 with the goal negated (`artifacts/coe/refill_lean_negctl.json`).
- **Output:** 155,000 records (gz md5 6326ebdd…, uncompressed lines md5 466fc214…), per-length counts identical to K12;
  155,000 `canon_key` classes, 154,491 premise-order-invariant classes (all 509 collisions inherited from K12).
- **Overlap with evaluation pools** (premise-order-invariant key; `artifacts/coe/k12_eval_overlap.txt`), all inherited from
  K12, refill 0: `rl_targets` 4, transfer 2, holdout250 0, textbook72 1 (the known premise-swapped twin), dev1108 1,
  `p2/heldout` 21.
- **Shape vs K12** (`artifacts/coe/shape_k12_vs_ko.md`): DN records 13.73 % → 3.29 %; NEGI 15.21 % → 5.19 %; IMPI +5.1 points;
  classical-only (G4ip, 20,000-record sample) 4.13 % → 1.33 %; mean term size 35.91 → 36.25.

## Families (`families.json`, `coe/coe_families.py`)

The 19 generator schemata of `data/ladder/rl_targets.jsonl` (40 trained-on members each) and `data/ladder/transfer.jsonl`
(40 held-out members each). Classical-only = not provable by G4ip (`intuit.py`). Six families are classical; their
**strict σ-covered** members (classical-only and no ( ~ ( ~ subformula anywhere in the sequent: every DN step must cite a
double negation the proof built) are the sets every analysis uses (pre-registration Addendum 2):

| family | trained (strict) | held-out (strict) |
|---|---|---|
| contraposition_conv | 27 | 18 |
| demorgan_nand_to_or | 9 | 4 |
| excluded_middle | 38 | 37 |
| negated_conditional | 16 | 15 |
| peirce | 15 | 12 |
| peirce_sequent | 18 | 19 |
| generated (non-schema) | 0 | 1 |
| **total** | **123** | **106** (`sigma_heldout_strict.txt`) |

Keys `keystep_*` (classical-only) and `sigma_covered_*` (the pre-registered, superseded definition) are kept for the record.

## Read and tracking sets

- `transfer_track832.jsonl`: the 760 schema members + 72 generated classical-only theorems of the transfer pool — sampled
  at k 32 every ladder round (the new ladders' `--transfer`).
- `heldout1000.jsonl`: 1,000 of `p2/heldout.jsonl` (seed 20261012) — the new ladders' per-round greedy set.
- `read1054.jsonl` = textbook72 (72, scoring only) + holdout250 (250) + `fam_extra.jsonl` (732 tracked theorems not in
  holdout250); `r322.jsonl` = its first 322 lines; `track_in_h250.jsonl` = the 100 tracked theorems inside holdout250.
- `phase2_cm_ktrain_s{0,1}.txt`: the compute-matched r8 sets at K_train of the old full seeds (Phase 2 inputs).
- `known_targets.jsonl.gz` (bucket): 21,456 known accepted proofs (old full ladders) of the strict members, for scoring.
- `power_pilot32.jsonl`: development data for the power-sampler pilot (32 random non-schema `rl_targets`).
- `known_targets_heldout.jsonl.gz` (bucket): the subset of `known_targets` on the held-out strict members (9,501 proofs).
- `phase2b_posctl_s0.txt`: the 17 theorems full s0 pend solves rarely (p̂ 1.7 × 10⁻⁴ – 3.9 × 10⁻³), Phase 2b's positive control.
- `sigma_heldout_family105.txt` (the 105 family members), `sigma_heldout_strict_no916.txt` (the same list, the Phase 3a read
  set; `pod/coe/p3a.sh` writes `p3a_read105.jsonl` from it), `sigma_heldout178.txt` (the superseded pre-registered list;
  the post-ladder certificate sample used it, and the strict 106 are a subset).
- `phase3a_seed.jsonl`: the seed proof of Phase 3a — knockout s1's base's free reductio of `la_transfer_916` (Phase 2,
  plain T 1.0).

## Dose sets (`coe/coe_dose.py`; pre-registration Addendum 5)

- `train_k12dose1.jsonl.gz` (report `train_k12dose1_report.json`; **run**: arm `dose1`, seeds s0–s2): K12⁻ with 1,550
  refill records replaced by 1,550 of the removed σ records (1.0 % of 155,000), drawn with K12's σ length mix (lengths
  5–12: 226 / 219 / 111 / 95 / 174 / 168 / 275 / 282); per-length counts unchanged; σ⁺ records 1,550.
- `train_k12dose01.jsonl.gz` (report `train_k12dose01_report.json`; **built, not run** — it did not fit the budget,
  `next_steps.md` item 1): the same with 155 σ records (0.1 %).
