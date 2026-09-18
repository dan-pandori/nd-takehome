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

## Compare (phase 2 — `run2.md`, `numbers.md` §Round 3 run 2, `log.md` §Round 3 — Run 2, `STATUS.md`, read after commit `75cb89d`)

Every number in `numbers.md` §Round 3 run 2 that I could re-derive is identical to my recount: all 21 reductio arms (per-stratum acquired, first-proof and
ignition rounds, 8-line curves, transfer per stratum, violations), the three six-line coverage lines, all 20 derived-ORE arm lines, all 10 base-reachability
lines, and the 10 EI / base / EI-only decompositions. I found no differing value. The rows below are the claims of `run2.md`.

| # | claim (`run2.md`) | my independent value | verdict |
|---|---|---|---|
| 1 | 345 targets = run 5's 300 + 45 six-line `nor_neg_ante`; 21 arms; 0 oracle violations | 345 (45 / 52 / 133 / 82 / 33); 300 / 300 records unchanged; 11 EI + 10 frozen; 0 solved-without-pattern, 0 verify failures in 80 917 raw records | reproduces |
| 2 | E1 predicted 3–5 of 6; 1 of 6 ignited | 1 of 6 | reproduces; reported as a miss |
| 3 | `f0.1_s0` ss0: 54 of 133 eight-liners, first proof round 4, ten by round 9, then 25 of 82 nine-liners | 54 / 133, first 4, ignition 9 (curve … 6 14 …); 25 / 82, ignition 13 | reproduces |
| 4 | same checkpoint with seed 1 and the four other arms: 0–3 eight-liners in 512 attempts | 1, 0, 0, 1, 3 | reproduces |
| 5 | "f is irrelevant" | 8-line ignition in 1 of 4 f = 0.1 sixteen-round arms and 1 of 4 f = 0 sixteen-round arms (s0 ss0, s0 ss1, s1, s2); Wilson 95 % for 1 / 4: 0.05–0.70 | numbers reproduce; **wording too strong** — "no f effect detectable at 4 arms per level" |
| 6 | 10-line stratum stays at 0 | 0 / 33 in all 33 arms | reproduces ("stays" = within 16 rounds × 32) |
| 7 | E2 held: k = 64 × 8 ignited 0 of 3 | 0 of 3 (8-liners 1 / 3 / 0) | reproduces |
| 8 | "— the crossing needs training rounds, not samples" (also STATUS: "needs rounds not samples") | k = 32 × 16 on the same three (checkpoint, seed 0) pairs: 1 of 3; their seed-1 replicates: 0 of 3; f0 s2 ignited at **round 7** with k = 32 (224 attempts); B f0.1 s1 ss0 was rising 1 → 3 at its last two rounds | **not supported.** 0 / 3 vs 1 / 3 (or 1 / 6) is no difference, the one arm-pair that differs (54 vs 1) is matched by an equally large same-checkpoint seed difference (54 vs 1), and one arm crossed inside 8 rounds at k = 32 |
| 9 | E3 falsified: 13 and 26 of 45 six-liners at pass@10⁴ | 13 / 45 (44 samples), 26 / 45 (2 139 samples); all listed proofs verify | reproduces; reported as a miss |
| 10 | run 5 saw 0 and 1 hit in 3·10⁶ samples at 7–10 lines | run-5 coverage files, my predicate: s1 0 targets / 0 samples; s2 1 target / 1 sample (a 7-line `negimp_to_pos`); 0 at 8–10 lines for s0, s1, s2 | reproduces |
| 11 | both zero-rate draws enter through the six-liners and reach the 7-line stratum; s2 crosses to 8 lines (27 of 133, round 7) and 9 lines (25 of 82) | s1 45 / 51 / 0; s2 45 / 52 / 27 / 25, ignition rounds 2 / 3 / 7 / 9 | reproduces. The 16-round extension is a disclosed, post-hoc deviation (log 05:58); at the pre-registered 8 rounds the values are s1 11 / 0 / 0 and s2 45 / 52 / 23 / 9, so the conclusion does not depend on the extension for s2 but does for s1's 7-line entry |
| 12 | frozen controls: 0 eight-liners | 0 in all 10 frozen arms (512 or 256 attempts) | reproduces |
| 13 | E4: f = 10⁻³ acquisition 0.133 / 0.143 (in band) | 40 / 300, 43 / 300 | reproduces |
| 14 | EI means 0.101, 0.138, 0.185 at f = 0, 10⁻³, 10⁻² | 0.1006 (n = 6), 0.1383 (n = 2), 0.185 (n = 2) | reproduces; f = 0 range 0.023–0.150 contains both f = 10⁻³ values, so only the f = 0 vs 10⁻² contrast (n = 6 vs 2) is suggestive; no per-f difference is separable |
| 15 | base reachability spans 9–43 and EI follows it (Pearson 0.81) | r = 0.809 over the 10 draws; **0.62 over the six f = 0 draws, 0.62 without s3, −0.50 over the five f = 0 draws other than s3**; Spearman 0.27 at f = 0 | number reproduces; **interpretation needs a caveat**: the correlation is carried by one low draw (s3) and by the f > 0 draws, i.e. by f; among the five f = 0 draws at r = 20–27, EI spans 24–45 with no positive relation |
| 16 | two f = 0 draws with base 20 and 27 acquire 43 and 45 — 26 and 25 of them targets the base never reaches at 10⁴ | s4 43 (26 EI-only), s5 45 (25 EI-only) | reproduces |
| 17 | "the kept fresh draw (base 9) acquires 7" | s3: r = 9, EI 7. But s4 (r = 20) also passes the keep rule (`numbers.md` says so) | reproduces; **wording**: there are two kept draws, and the other one (s4) is the one that breaks the band |
| 18 | EI-only ≥ 20 in 3 of 10 draws | s4 26, s5 25, f = 10⁻² s1 24 | reproduces |
| 19 | 7 → 8 crossing: 2 of 11 trained arms, 0 of 8 frozen | 2 / 11 (2 / 8 among sixteen-round arms), 0 / 8 frozen-16 | reproduces |
| 20 | "every draw has a non-zero base rate at the schema's shortest instance" | 3 of 3 f = 0 draws tested (s0, s1, s2) have six-line hits; the six-liners are a **different schema** (`nor_neg_ante`, 45 / 45), not shorter instances of the 7–10-line schemata | numbers reproduce; **reword**: "at the shortest reductio-requiring targets (one six-line schema)"; "every" = 3 draws |
| 21 | "RL … carries it one stratum up in every arm" | 7-line stratum 51–52 / 52 in 11 / 11 EI arms | reproduces |
| 22 | "once crossed, the 9-line stratum follows within four rounds" | 8 → 9-line ignition gaps 4 and 2 rounds; in both arms the nine-liners are exactly `chain_neg` 25 / 25 | reproduces at n = 2; it is one schema following, not the stratum (57 of 82 nine-liners are at 0 in every arm) |
| 23 | "after entry RL produces schemata and lengths the base never emits" | f = 0 draws: 0 strict proofs at 8–10 lines in 2.5·10⁶ base samples each (run-5 coverage) and 0 in frozen-16. For the f = 0.1 s0 checkpoint there is **no 10⁴ coverage** at 8–9 lines, only the frozen arm (0 in 133 × 512 = 68 096 samples) | supported for s2 at the 10⁴ level; for f0.1 s0 "never" rests on 512 attempts per target — say "not in 512 attempts" |
| 24 | "per-run probability ≈ 0.2 in 16 rounds" | 2 / 11 = 0.18 mixes 8-round B arms in; sixteen-round arms 2 / 8 = 0.25, Wilson 95 % 0.07–0.59; two of the non-igniting arms were still rising at the stop | **needs the interval and the denominator**; "≈ 0.2" reads more exact than 2 events allow |
| 25 | "derived-ORE amplification is proportional to base reachability on average — f raises the base rate, not the multiplier" | EI / base by f: 0.78–2.15 (mean 1.30, n = 6), 1.08–1.26 (n = 2), 1.33–1.47 (n = 2); base reach 9–27 / 34–37 / 36–43 | reproduces as description; the pre-registration said that E4 outside 0.5–2 × means "'amplification in proportion to the base rate' is dropped" — s4 is at 2.15. The write-up reports the miss but keeps the clause softened ("a trend, not a per-draw law") rather than dropping it; see §Verdict |
| 26 | "the multiplier varies 0.8–2.2 × between draws of equal reachability" | at r = 26–27 (five draws) the multiplier is 0.89–1.67; 0.78 is s3 (r = 9) and 2.15 is s4 (r = 20) | **reword**: "0.9–1.7 × at equal reachability (r = 26–27), 0.8–2.2 × over all f = 0 draws" |
| 27 | spend ≈ 9.4 pod-hours ≈ $4.7 | queue logs span 05:17–08:3x on r32a / r32b and end ≈ 07:55 on r32c, consistent with 3.35 + 3.35 + 2.67 h × $0.50; balance attribution to foreign pods not checkable by me | consistent; within the $50 budget and the $8 estimate |
| 28 | bucket paths | `hf buckets ls`: `round3-run2/{artifacts,ckpts,data}` exist; `ckpts/r3_2` holds the 19 EI final checkpoints + 5 Stage-1 draws | reproduces ("21 trained arms" in `numbers.md` should read 17 EI arms / 19 checkpoints) |

Gate 0 and misses: expectations were committed (05:13:01 UTC) before the first job (05:17:50 UTC). E1, E3 and the E4 band / EI-only misses are reported as misses in
`run2.md`, `numbers.md` and `STATUS.md`. Two sub-expectations are not scored anywhere in the write-up: **E1c** ("9- and 10-line strata ≤ 3 targets in every arm" — missed, 25 in the
igniting arm) and **E1b** (first 8-line proof between rounds 6 and 12 — 2 of the 4 A arms with a proof; rounds 4 and 14 fall outside). The pre-registered **per-schema** report is
computed (`summary.json` `by_schema`) but absent from `run2.md` and `numbers.md`, and it changes the reading (below). Deviations (C extension, co-scheduling, the extra
coverage runs, starting the s2 / s3 arms before the keep rule was evaluated) are all disclosed in `log.md`.

## Verdict

**No hard-constraint violation; no number differs.** This is the cleanest recount of the series: 33 arms, 13 coverage files and the pools reproduce exactly, and the
write-up reports its own misses.

**What stands.**
1. EI at 512 attempts per target carried the 8-line reductio stratum past 10 targets in 1 of 6 pre-registered sixteen-round arms and 0 of 3 k = 64 arms (E1 missed, E2 hit);
   no frozen control produced any 8–10-line proof; the 10-line stratum is 0 everywhere.
2. Run 5's "zero-rate" f = 0 draws are not zero-rate on six-line targets (13 / 45 and 26 / 45 at pass@10⁴, from a training file with 0 reductio proofs in 155 000), and both
   enter the pool through that stratum; s2 then reaches 27 eight- and 25 nine-line targets that its base did not hit in 2.5·10⁶ samples. E3 is falsified, and with it run 5's
   reading of the 7-line result as a pattern gate. Two seeds (s1, s2) show the entry; one shows the onward crossing.
3. The same checkpoint with two sampling seeds gives 54 vs 1 eight-liners: the crossing is a per-run stochastic event.
4. Derived-ORE: f = 10⁻³ lands in the pre-registered band on two seeds; two of four fresh f = 0 draws exceed 1.5 × base reach with 25–26 EI-only targets against pass@10⁴
   — the pre-registered "EI-only ≥ 20" criterion for "RL adds substantially beyond the base's reach" is met in 3 of 10 draws.

**What must be reworded.**
- "the crossing needs training rounds, not samples" (row 8; also in `STATUS.md`) → "k = 64 × 8 ignited 0 of 3 and k = 32 × 16 ignited 1 of the same 3 seed-0 pairs (0 of 3 seed-1
  replicates); the design cannot separate rounds from samples, and one f = 0 draw crossed within 8 rounds at k = 32."
- "f is irrelevant" → "no f effect detectable (1 of 4 vs 1 of 4 sixteen-round arms)."
- "per-run probability ≈ 0.2" → "2 of 8 sixteen-round arms (Wilson 95 % 0.07–0.59); two further arms were still rising when stopped."
- "the schema's shortest instance" → the six-liners are one separate schema; "every draw" = 3 draws.
- "schemata and lengths the base never emits" → "never" holds at 10⁴ for the f = 0 draws only; for f0.1 s0 it is "0 in 512 attempts".
- "the kept fresh draw" → two draws pass the keep rule (s3, s4). "0.8–2.2 × between draws of equal reachability" → 0.9–1.7 × at equal reachability.
- Score E1b and E1c explicitly; correct "21 trained arms".

**What is not supported as written.**
- *Stratum* as the unit of ignition. Acquisition above 7 lines is schema-complete in every case: 54 = `contraposition_conv` 27 / 27 + `neg_both` 26 / 26 + `chain_neg` 1 / 1;
  27 = `neg_both` 26 / 26 + 1; both 25s = `chain_neg` 25 / 25; the "1 eight-liner" of four other arms is the single 8-line `chain_neg`; `consequentia_cond`, `nand_to_imp`,
  `excluded_middle`, `negcond_ante` (26 each) are 0 in all 11 arms. "The 8-line stratum ignites with probability p" should be "a schema ignites", with 2 of 5 large 8-line
  schemata ever acquired. The "7 → 8 crossing … then the 9-line stratum follows" narrative is one schema family (`chain_neg`) spanning 8–9 lines. This is the pre-registered
  per-schema report and it belongs in `numbers.md`.
- "Amplification proportional to base reachability on average." By the run's own falsifier (any kept draw outside 0.5–2 ×) the clause was to be dropped; s4 (kept) is at
  2.15 ×. The 0.81 correlation is between-f and one low draw; within the five comparable f = 0 draws it is absent (r = −0.50, EI 24–45 at base 20–27). What the data
  support: base reach ≈ 0 → EI ≈ 0 (one draw, s3), and above that acquisition is not predicted by base reach at n = 5.

**Next measurements that would settle what is open** (all small; ≈ $3–5 total on one 3090):
1. *Rounds vs samples, and the ignition probability:* the three seed-0 checkpoints × sampling seeds 2–5 at k = 32 × 16 and k = 64 × 8 (24 arms, ≈ 0.5 h each at N = 3); score
   per schema. With ≥ 6 arms per cell a 0.25 vs 0 difference is still not resolvable, so pre-register the comparison as "pooled ignition count with interval", not a contrast —
   or extend the two rising arms (A f0 s0 ss1, B f0.1 s1 ss0) to 24 rounds first, which is cheaper and tells whether "non-ignition" is just "late".
2. *"Never emits" for the f = 0.1 draw:* `coverage.py --k 10000` of `stage1_reductio_f0.1_s0` on the 54 + 25 acquired 8- / 9-line targets (≈ 20 min).
3. *Derived-ORE base-reach dependence:* needs draws with base reach between 0 and 20, which seeds do not supply on demand (five of six f = 0 draws are at 20–27). Either train
   ≈ 6 more cap-8 f = 0 seeds and keep whatever spread appears, or vary Stage-1 steps (2 000 / 4 000) on one seed to move base reach deliberately; pre-register a rank
   correlation within f = 0, not a Pearson across f.
4. *Is the six-line entry special to `nor_neg_ante`?* One arm per f = 0 draw on the 300 pool plus six-liners of a second schema (if `necessity.py` yields any) would say whether
   "entry at the shortest instance" is about length or about that schema.
