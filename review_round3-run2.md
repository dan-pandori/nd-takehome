# Review of round3-run2 — the 8-line reductio stratum and the derived-ORE base-rate dependence

Reviewer session, 2026-09-18. Phase 1 (§Recount) was written from `~/review/round3-run2` (executor write-ups removed) and
committed before `run2.md`, `numbers.md`, `log.md`, `STATUS.md`, `summary.json` or any figure was opened.
Inputs: `preregistration/round3-run2.md` (commit `6ffade0`), the code, `data/`, `artifacts/r3_2/`, `artifacts/r5/`, `ckpts/r3_2*`.

Reviewer code (nothing shared with the executor except `nd_verify`): `review_r3_2_recount.py` (arms, coverage, pools, splits, mix),
`review_r3_2_tables.py` (derived tables, raw-record verify), `review_r3_2_trainscan.py`; parser, dependency pruning, start-index
normaliser, reductio / strict-derived-ORE predicates, depth counter and renaming key are my own from `review_run5_recount.py`.
Outputs: `artifacts/review_r3_2/*.json`. Counting rule as pre-registered: a target is *acquired* when a verified, start-index-normalised
proof of it satisfies the pattern predicate on the dependency-pruned proof; its round is the minimum over the per-round found files and the
`round` field; stratum = the pool's `stratum`; ignition = first round with ≥ 10 acquired targets in the stratum.

## Recount

### R0. Hard constraints and gate 0

| check | result |
|---|---|
| `nd_verify` tree hash, run branch vs `origin/main` | equal (`9437bb7…`); workspace copies of `__init__.py`, `verify.py` hash-identical |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf06…` on `origin/main`, on the branch head and in the workspace; last touched by `ca93f83` (2026-09-15) |
| evaluation files in training code | `expert_iter.py` / `train.py` not modified by this run (run diff = `r3_2_pool.py`, `r3_2_analysis.py`, `pod/r3_2/*`); `test_*_prompts` are referenced only by `audit_test_overlap.py` and `score_test.py`, neither of which is in a job file; transfer / heldout / validation-36 are read by `expert_iter.py` for scoring and for the `eval_keys` exclusion only |
| what EI trained on (first and last `mix_<r>.jsonl` of all 17 EI arms, by renaming class) | 0 records in the arm's own transfer set, 0 in its own heldout file, 0 in validation-36; the RL-target share grows 0–924 → 112–2 816 records |
| expectations before the run | pre-registration committed 05:13:01 UTC; first job started 05:17:50 UTC (`queue_logs`); the only later edit (`9c6cda2`) changes the header timestamp |
| supervised caps | `train_reductio_f0`, `_f0.1`: max 6 lines; the three `train_derived_ore_strict_*_c8`: max 8 lines (the pre-registered "cap 8, not a submission result" track) |
| pattern in Stage-1 data (my predicate, pruned) | `train_reductio_f0` 0 / 155 000; `_f0.1` 15 500; `train_derived_ore_strict_f0_c8` 0 / 154 994; `_f0.001_c8` 155; `_f0.01_c8` 1 550 — the f levels are exact |
| new Stage-1 checkpoints (`extra.args` read without torch) | s1 (f = 10⁻³), s2–s5 (f = 0): `--mode abs --steps 6000 --bs 128 --cap 8`, seeds 1 / 2 / 3 / 4 / 5, the pre-registered data files |
| job failures | no `FAILED` in any queue log, no traceback / OOM in any job log |

No hard-constraint violation.

### R1. Pools and splits

- 345 pool: strata 6 / 7 / 8 / 9 / 10 = **45 / 52 / 133 / 82 / 33**; `stratum` = `min_lines_ub` = `n_lines` for 345 / 345; first 300 records equal run 5's
  pool field-for-field (300 / 300); the 45 six-liners are all in `run5_reductio_nec.jsonl` (which has exactly 45 six-line candidates), all schema
  `nor_neg_ante`, all with the rule sequence `PR AS ORI1 NEGE NEGI DN`. Oracle proofs: 345 / 345 verify, 345 / 345 satisfy my reductio predicate,
  oracle length = stratum 345 / 345, no `~ ( ~` in any sequent, 0 duplicate classes. Transfer 150: strata 27 / 67 / 41 / 15, same checks 150 / 150.
  Derived-ORE pool 300 (9 / 10 lines = 126 / 174) and transfer 65: all oracle proofs verify and are strict derived-ORE.
- 8-line stratum by schema: consequentia_cond 26, contraposition_conv 27, nand_to_imp 26, neg_both 26, neg_to_contra 26, chain_neg 1, negimp_to_or 1.
- Split disjointness by renaming class (my `rkey`), training file × evaluation pool: `train_reductio_f0` and `_f0.1` × {345 pool, six-line file, reductio
  transfer, `heldout`, validation-36} = **0** everywhere; the three cap-8 files × {derived-ORE pool, derived-ORE transfer, `heldout_c8`, validation-36} = **0**
  everywhere. Pool × transfer = 0 for both families. (Cross-family pairs that no arm uses are non-zero — reductio train × `heldout_c8` 118–122, cap-8 train ×
  `heldout` 101–122 — and the training files share 1–51 classes with the test *prompt* files; neither is an evaluation of this run. Full matrix: `splits.json`.)

### R2. Verification

Every distinct normalised proof of every arm (targets + transfer) was re-verified with `nd_verify` and re-classified: **0 failures in 33 arms**;
every solved target is solved with the pattern (0 "solved without pattern" on targets and transfer in all arms — no oracle errors). Because the
reductio arms hold only ≈ 1 distinct normalised proof per target (97–177 per arm), I also verified **every raw record** of each arm's last found
file with the pool's prompt: 1 – 6 649 records per arm, 80 917 in total, 0 failures, 0 records without the pattern, 0 prompt mismatches. My solved
counts equal the executor's `round_<last>.json` cumulative solved for targets and transfer in 33 / 33 arms; the `round` field agrees with
first-file appearance for every proof. Coverage files: proof lists complete (`n_distinct_ok` = list length) in all 13 files, all listed proofs
verify, 0 predicate disagreements with the executor's flags.

### R3. Reductio arms (345 pool; 512 attempts per target in every 16-round and every k = 64 arm)

Acquired targets per stratum at the last round; first-proof round / ignition round for the 8-line stratum; transfer acquired (of 150).

| arm | rounds × k | 6 | 7 | 8 | 9 | 10 | total | first 8-line | 8-line ignition | 9-line ignition | transfer 7 / 8 / 9 / 10 | frozen, same seed (6 / 7 / 8+) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A f0 s0 ss0 | 16 × 32 | 45 | 52 | 1 | 0 | 0 | 98 | 14 | — | — | 27 / 0 / 0 / 0 | 25 / 4 / 0 |
| A f0 s0 ss1 | 16 × 32 | 45 | 52 | 3 | 0 | 0 | 100 | 10 | — | — | 27 / 0 / 0 / 0 | 26 / 3 / 0 |
| A f0.1 s0 ss0 | 16 × 32 | 45 | 52 | **54** | **25** | 0 | 176 | 4 | **9** | 13 | 27 / 26 / 12 / 0 | 45 / 30 / 0 |
| A f0.1 s0 ss1 | 16 × 32 | 45 | 52 | 1 | 0 | 0 | 98 | 11 | — | — | 27 / 0 / 0 / 0 | 45 / 27 / 0 |
| A f0.1 s1 ss0 | 16 × 32 | 45 | 52 | 0 | 0 | 0 | 97 | — | — | — | 27 / 0 / 0 / 0 | 45 / 27 / 0 |
| A f0.1 s1 ss1 | 16 × 32 | 45 | 52 | 0 | 0 | 0 | 97 | — | — | — | 27 / 0 / 0 / 0 | 45 / 25 / 0 |
| B f0 s0 ss0 | 8 × 64 | 45 | 51 | 0 | 0 | 0 | 96 | — | — | — | 27 / 0 / 0 / 0 | (A ss0 frozen) |
| B f0.1 s0 ss0 | 8 × 64 | 45 | 52 | 1 | 0 | 0 | 98 | 3 | — | — | 27 / 0 / 0 / 0 | (A ss0 frozen) |
| B f0.1 s1 ss0 | 8 × 64 | 45 | 52 | 3 | 0 | 0 | 100 | 7 | — | — | 27 / 1 / 0 / 0 | (A ss0 frozen) |
| C f0 s1 ss1, round 8 | 8 × 32 | 11 | 0 | 0 | 0 | 0 | 11 | — | — | — | | 1 / 0 / 0 (frozen8) |
| C f0 s2 ss2, round 8 | 8 × 32 | 45 | 52 | 23 | 9 | 0 | 129 | 5 | **7** | — | | 7 / 0 / 0 (frozen8) |
| C f0 s1 ss1, round 16 (extension, not pre-registered) | 16 × 32 | 45 | 51 | 0 | 0 | 0 | 96 | — | — | — | 26 / 0 / 0 / 0 | 1 / 0 / 0 |
| C f0 s2 ss2, round 16 (extension, not pre-registered) | 16 × 32 | 45 | 52 | **27** | **25** | 0 | 149 | 5 | **7** | 9 | 27 / 14 / 13 / 0 | 8 / 1 / 0 |

- **8-line ignition: 1 of 6 A arms, 0 of 3 B arms, 1 of 2 C arms** (2 of 11 EI arms). No frozen arm has any 8-, 9- or 10-line proof at 512 attempts
  (0 of 8 frozen-16 arms), and no arm of any kind has a 10-line proof (0 / 33 everywhere).
- 8-line cumulative curves of the two igniting arms: f0.1 s0 ss0 `0 0 0 1 2 3 4 6 14 20 35 45 51 54 54 54`; f0 s2 ss2 `0 0 0 0 1 6 17 23 27 27 27 27 27 27 27 27`.
- **Ignition is by schema, not by stratum.** In f0.1 s0 ss0 the 54 eight-line targets are contraposition_conv 27 / 27 + neg_both 26 / 26 + chain_neg 1 / 1, and the 25
  nine-line targets are chain_neg 25 / 25. In f0 s2 ss2 the 27 are neg_both 26 / 26 + chain_neg 1 / 1, the 25 again chain_neg 25 / 25. Three 8-line schemata
  (consequentia_cond, nand_to_imp; neg_to_contra except below) and the 9-line excluded_middle / negcond_ante schemata are at 0 in every arm. The
  "1 eight-line target" of four non-igniting arms is the single chain_neg 8-liner.
- **Two "non-igniting" arms were still growing when they stopped**: A f0 s0 ss1 has neg_to_contra 0 → 1 → 2 at rounds 15–16 (8-line curve `… 1 1 1 1 1 2 3`), and
  B f0.1 s1 ss0 has neg_both 1 → 3 at rounds 7–8. Their non-ignition is a statement about the stop round, not an asymptote.
- 7-line stratum: 51–52 of 52 in all 11 EI arms (frozen at 512 attempts: 3–4 for f0 s0, 25–30 for f = 0.1, 0–1 for f0 s1 / s2). 6-line: 45 / 45 in all 11 EI arms.
- Transfer follows the acquired schemata (8- / 9-line transfer proofs only in the two igniting arms; +1 in B f0.1 s1 ss0). Heldout greedy: f0 s0 0.886 → 0.887–0.888;
  f = 0.1 0.967–0.968 → 0.969–0.978; f0 s1 0.871 → 0.885; f0 s2 0.894 → 0.907 (minimum over rounds never more than 0.007 below the start). From `round_*.json`, not recomputed (no GPU).
- The frozen-8 and frozen-16 controls of the C draws share seeds and their first 8 rounds are identical (`1`; `4 5 6 6 6 7 7 7`), so the 16-round frozen arm is a valid extension.
- C arm f0 s1: rounds 1–6 accepted nothing, so the model was untrained until round 7, where the EI arm and its frozen twin drew the same first six-line proof; ignition of
  the 6-line stratum followed at round 8 and of the 7-line stratum at round 10. The C arms' `args.json` was overwritten by the resume (it now shows `start_round 9`, `rounds 8`,
  init = the round-8 checkpoint); rounds 9–16 used seeds 1009–1016 / 2009–2016 and `round_9.json` loads `…_r8.pt`.

**Six-line base reachability, pass@10⁴ (45 targets, T = 0.8, seed 0).** s0 29 / 45 (28 993 pattern samples); **s1 13 / 45** (44 samples ≈ 10⁻⁴ per sample);
**s2 26 / 45** (2 139 samples ≈ 5 × 10⁻³). The draws run 5 called zero-rate are not zero-rate on the six-line stratum.

Pre-registered expectations against the recount:

| | expectation | recount | outcome |
|---|---|---|---|
| E1a | 8-line ignites in 3–5 of 6 A arms | 1 of 6 | **miss** |
| E1b | first 8-line proof between rounds 6 and 12 | rounds 14, 10, 4, 11, none, none | 2 of the 4 arms with a proof are inside the window |
| E1c | 9- and 10-line ≤ 3 targets in every arm | 25 nine-line targets in the igniting A arm (0 elsewhere in A); 10-line 0 | **miss** in the one arm that ignited |
| E1d | f = 0.1 ignites no more often than f = 0 s0 | 1 / 4 vs 0 / 2 | not decidable at this n (literal reading: miss) |
| E2 | 8-line ignites in ≤ 1 of 3 B arms | 0 of 3 | hit — but A at twice the rounds ignited 1 of 6 (1 of 3 on the matching seed-0 arms), so the attached inference "training rounds matter more than attempts per round" is not supported either way |
| E3a | zero-rate draws: 0 six-line hits at pass@10⁴ | 13 / 45 and 26 / 45 | **miss** |
| E3b | zero-rate draws: 0 / 345 after 8 rounds | 11 / 345 and 129 / 345 | **miss**; the pre-registered falsifier ("any six-line hit in a zero-rate draw followed by ignition: the wall was length-gated, not pattern-gated") is met by both draws |
| E3c | f0 s0 solves ≥ 30 of 45 six-liners by round 2 in both A arms | 33 and 38 | hit |
| E5 | seed-0 A arms' 7-line stratum at round 8 = run 5's 51–53 ± 2 | 52, 52, 52 (run 5, my recount: 51, 52, 52); curves f0 s0 `1 14 25 47 50 52 52 52` vs run 5 `2 11 25 47 51 51 51 51` | hit |
| falsifier | E1 at 0 / 6 with E2 at 0 / 3 → "real length wall" | 1 / 6 and 0 / 3, plus 1 / 2 C arms reaching 8 and 9 lines from f = 0 | not met; 8- and 9-line proofs are reachable by EI |

### R4. Derived-ORE, cap 8 (not a submission result; 300 targets, 8 rounds × 32 = 256 attempts)

Base strict reachability at pass@10⁴ (my predicate on the coverage proof lists): f = 0 — run-5 s0 27, s1 27, **s2 26, s3 9, s4 20, s5 27**; f = 10⁻³ — s0 37, s1 34;
f = 10⁻² — s0 36, s1 43. Keep rule (|r − 27| ≥ 5): s2 fails (1), s3 passes (18) → seeds 4, 5 trained as pre-registered; s4 passes (7), s5 fails (0). All four fresh
draws were run; I report all four.

| draw | f | base r (/300) | EI acquired (rate) | frozen | EI / r | EI / frozen | EI-only vs base@10⁴ | base not in EI | transfer (/65) |
|---|---|---|---|---|---|---|---|---|---|
| run-5 s0 | 0 | 27 | 26 (0.087) | 13 | 0.96 | 2.0 | 8 | 9 | |
| run-5 s1 | 0 | 27 | 24 (0.080) | 11 | 0.89 | 2.2 | 7 | 10 | |
| s2 | 0 | 26 | 36 (0.120) | 14 | 1.38 | 2.6 | 14 | 4 | 10 |
| s3 | 0 | 9 | 7 (0.023) | 6 | 0.78 | 1.2 | 1 | 3 | 5 |
| s4 | 0 | 20 | 43 (0.143) | 7 | **2.15** | 6.1 | **26** | 3 | 14 |
| s5 | 0 | 27 | 45 (0.150) | 13 | 1.67 | 3.5 | **25** | 7 | 10 |
| s0 | 10⁻³ | 37 | 40 (0.133) | 16 | 1.08 | 2.5 | 14 | 11 | 11 |
| s1 | 10⁻³ | 34 | 43 (0.143) | 18 | 1.26 | 2.4 | 16 | 7 | 11 |
| run-5 s0 | 10⁻² | 36 | 48 (0.160) | 21 | 1.33 | 2.3 | 18 | 6 | |
| run-5 s1 | 10⁻² | 43 | 63 (0.210) | 28 | 1.47 | 2.3 | 24 | 4 | |

- E4a (f = 10⁻³ acquisition 0.08–0.16 for both seeds): 0.133, 0.143 — **hit**.
- E4b (EI within 0.5–1.5 × r for each kept fresh f = 0 draw): s2 1.38 and s3 0.78 inside; **s4 2.15 and s5 1.67 outside**; s4 is also outside the falsifier band 0.5–2 ×.
- E4c (EI ≈ 2 × frozen): 2.6, 1.2, 6.1, 3.5 — holds for none of the four within ± 25 %.
- E4d (EI-only 5–10): 14, 1, 26, 25 — **0 of 4 inside**; s4 and s5 meet the pre-registered "EI-only ≥ 20" falsifier (as does run 5's f = 10⁻² s1, 24).
- Proportionality to base reach across the six f = 0 draws, (r, EI) = (27, 26), (27, 24), (26, 36), (9, 7), (20, 43), (27, 45): at r = 26–27 acquisition spans 24–45; Spearman ρ = 0.27
  (n = 6). The only support for "proportional" is the single low draw s3.
- Monotonicity in f: means 30.2 (n = 6; 25.0 for run 5's two) / 41.5 (n = 2) / 55.5 (n = 2) are monotone, but the f = 0 range 7–45 contains both f = 10⁻³ values and two
  f = 0 draws (43, 45) equal or exceed both f = 10⁻³ draws (40, 43). Base reach: 9–27 / 34–37 / 36–43.
- Frozen ⊆ base@10⁴ except 1–2 targets; frozen ⊆ EI except 0–2 targets.

### R5. Not derivable in phase 1

Heldout / transfer greedy numbers (GPU); pod spend; bucket upload. Checked against the log and `numbers.md` in phase 2.
