# Review — run `frontier-supply`

Reviewer: agent:claude (reviewer role), 2026-09-30. The policy is `AGENT_POLICY.md` (nd-rl canonical). **Lean alone decides**: every
count below is "at least one Lean-accepted proof" as stored by the run's judge, and I re-checked a sample in Lean myself.

**Model for every number (unless labelled):** SN-cap12. This is a `lean_staten` state policy (proof-state observation,
environment-assigned names) with 3,216,384 parameters (4 layers × d 256), trained from scratch. Its Stage-1 data is K12 (cap-horizon's
cap-12 set, 155,000 proofs). The Stage-1 checkpoints are `ckpts/sc12/stage1_SN12_s{0..5}.pt`: s0–s3 come from state-cap12 and s4–s5
were trained in this run. The arms are:
- **C** — the final EI checkpoints on `rl_targets` only. s0–s3 are state-cap12's reused `la_T1_SN12_s{0..3}_r8.pt`; s4–s5 are new
  (`la_C_s{4,5}_r8`).
- **S** — the supply arm, `la_S_s{0..5}_r8`, all new.
- **C′** — the control rerun with EI seed S+100, `la_R_s{0,1}_r8`.
- **B** — the Stage-1 bases.

All read-outs use the same settings: k 256, T 0.8, seed 0, batch 2048, `max_action` 512, `max_steps` 96, on an NVIDIA A40.

## Recount (phase 1 — written from `~/review/frontier-supply` before reading any executor write-up)

I used scripts I wrote myself: `review_fsup_recount.py`, `review_fsup_lean_recheck.py`, `review_fsup_filter_leak.py` and
`review_fsup_terms.py`. They read only the raw rows (`artifacts/fsup/rr/*.jsonl`, `la_*/cands_*.jsonl`, `supply_found_8.jsonl`,
`found_8.jsonl`, `round_*.json`, the registry rows) and the pool files. Solved means the row's `proofs` list is non-empty. I checked
that this matches the stored `solved` flag on every row, and that every row has `n_tried` = 256.

### R1. Solves per checkpoint (the primary is the 91 long-pool-2 theorems plus rr600 `L_true` 15–16, 291 in total)

| ckpt | primary /291 | lp2 /91 | exact-17 /61 | ≥18 /30 | rr 15–16 /200 | rr 13–14 /200 |
|---|---|---|---|---|---|---|
| C s0 | 142 | 33 | 25 | 8 | 109 | 120 |
| C s1 | 207 | 60 | 42 | 18 | 147 | 149 |
| C s2 | 218 | 57 | 39 | 18 | 161 | 156 |
| C s3 | 220 | 58 | 42 | 16 | 162 | 156 |
| C s4 | 220 | 61 | 44 | 17 | 159 | 154 |
| C s5 | 207 | 47 | 31 | 16 | 160 | 151 |
| S s0 | 139 | 36 | 28 | 8 | 103 | 120 |
| S s1 | 217 | 62 | 44 | 18 | 155 | 152 |
| S s2 | 226 | 61 | 42 | 19 | 165 | 158 |
| S s3 | 233 | 66 | 46 | 20 | 167 | 158 |
| S s4 | 228 | 66 | 49 | 17 | 162 | 151 |
| S s5 | 216 | 58 | 38 | 20 | 158 | 155 |
| C′ s0 | 145 | 34 | 26 | 8 | 111 | 123 |
| C′ s1 | 197 | 52 | 39 | 13 | 145 | 146 |
| B s0–s5 | — | 7 / 20 / 18 / 23 / 25 / 19 | 5/17/15/18/19/13 | 2/3/3/5/6/6 | see below | see below |

- The Stage-1 bases were read on lp2 for all six seeds. The rr read-outs for B s0 and s1 died with a CUDA OOM at 04:24–04:26, and
  their logs are the only trace; s2–s5 were never read on rr. So frozen reachability on the primary is incomplete; see phase 2.
- The Stage-1 union over seeds solves 41 of the 91 lp2 theorems. Every final checkpoint and every base solves at least one `L_lb` ≥ 18
  theorem, so L* on the read-out is 18 everywhere, as forecast (it saturates).
- Seed 0 is low in every arm: C 142, S 139, C′ 145. Its Stage-1 base is the weakest (7 of 91), so seed 0 dominates the between-seed
  spread (sd of C on the primary is 30.2).

### R2. S − C, paired by seed

The MDD is 1.425 · sd_d, the formula as pre-registered. I report sd_d two ways: from C′ − C (2 pairs, as pre-registered) and from
S − C itself (5 df).

| quantity | S − C per seed (s0…s5) | mean | IQM [bootstrap 95 %] | C′ − C (s0, s1) | MDD (C′-based) | MDD (S−C sd) | paired t (5 df) |
|---|---|---|---|---|---|---|---|
| **primary /291** | −3, +10, +8, +13, +8, +9 | **+7.5** | **+8.75 [+2.5, +11.0]** | +3, −10 | **10.5** | 7.8 | 3.36, p ≈ 0.02 |
| lp2 /91 | +3, +2, +4, +8, +5, +11 | +5.5 | +5.0 [+2.75, +8.75] | +1, −8 | 8.1 | 4.8 | 3.97, p ≈ 0.01 |
| exact-17 /61 | +3, +2, +3, +4, +5, +7 | +4.0 | +3.75 [+2.5, +5.5] | +1, −3 | 3.2 | 2.6 | 5.5, p ≈ 0.003 |
| ≥18 /30 | 0, 0, +1, +4, 0, +4 | +1.5 | +1.25 [0, +3.25] | 0, −5 | 5.0 | 2.8 | — |
| rr 15–16 /200 | −6, +8, +4, +5, +3, −2 | +2.0 | +2.5 [−2.75, +6.0] | +2, −2 | 2.9 | 7.3 | — |
| rr 13–14 /200 | 0, +3, +2, +2, −3, +4 | +1.3 | +1.75 [−1.0, +3.25] | +3, −3 | 4.3 | 3.6 | — |

- The bootstrap resamples the 6 paired differences, with 20,000 draws and RNG seed 0. There is one stratum, because the differences are
  already paired.
- By the pre-registered rule, the primary S − C is inside the C′-based MDD (+7.5 against 10.5), so the brief's hypothesis
  "S − C > MDD" is **not met**. The pre-registered point forecast was +8, and the result matches it.
- The effect is nevertheless consistently positive: 5 of 6 seeds on the primary and 6 of 6 on lp2 and on exact-17. The bootstrap
  interval of the IQM excludes 0. The C′-based sd_d rests on only 2 pairs, and one of them (s1, −10) is larger than any S − C
  difference except s3's.
- The gain sits in lp2, mostly exact-17. rr 15–16 contributes +2, which is inside its own noise.

**Per-theorem flips on the primary.** S-only / C-only by seed: 31/34, 27/17, 24/16, 26/13, 23/15, 27/18. For C′ against C: 25/22 on s0
and 23/33 on s1. The net flips are therefore −3, +10, +8, +13, +8, +9 for S against +3, −10 for C′.

**New against reused ladders.** The C′ ladders are new and their C counterparts are reused; C′ − C is +3 and −10. If anything, the new
ladders score lower than the reused ones, so the S − C difference is not an artefact of reusing state-cap12's ladders for C s0–s3. The
C read-outs also reproduce the pre-registration's state-cap12 lp2 numbers: 33 / 60 / 57 / 58 against 34 / 59 / 58 / 61.

### R3. Filter (supply candidates, 6 S ladders × 8 rounds × 1,123 = 53,904)

A candidate passes when 0 < n_ok ≤ 8 of 32. "Zero" means n_ok = 0; "easy" means n_ok > 8.

| slice | pass | zero | easy |
|---|---|---|---|
| **all** | **6,894 / 53,904 = 12.8 %** | 75.5 % | 11.7 % |
| (a) mutations | 15.8 % | 70.1 % | 14.1 % |
| (b) open goals | 9.8 % | 80.8 % | 9.3 % |
| a:hyp / contrapose / case / conj / chain | 32.0 / 22.6 / 15.3 / 13.8 / 10.5 % | | |
| round 1 → 8 | 14.9, 14.0, 12.5, 11.9, 12.6, 12.9, 12.3, 11.3 % | | |
| per seed | 12.0 – 14.0 % | | |

- The forecast was 10 % overall, 12 % for (a) and 6 % for (b); all three came out higher. The brief's 5 % floor is met.
- The kept candidates in `cands_*.jsonl` equal the names in `supply_found_8.jsonl` for every seed: 1,075 / 1,255 / 1,151 / 1,165 /
  1,128 / 1,120 targets carrying 2,138 – 2,823 proofs.
- The length window stayed low throughout. `base` started at 12 and reached 13 by round 2–3 on five seeds (by round 7 on s0), so the
  (a) upper bounds were 14–17. None of the supplied targets lies inside the 17–18 read-out band by construction.
- Supply proofs by source (my line counts): (a) has a median of 16 lines, and 4,477 of 9,282 proofs are ≥ 17 lines. (b) has a median of
  11 lines, the same as `rl_targets` proofs.
- Every S ladder spent 143,840 attempts per round (107,904 on targets + 35,936 filter attempts, with no shortfall). C and C′ also spent
  143,840 per round.

### R4. Lean re-check of stored proofs (870 proofs)

I took 150 random proofs plus the 30 longest from each of C, S, C′ and B (read-out rows), and 150 random supply training proofs from
`supply_found_8.jsonl`.

- Each stored ND string was translated with `nd2lean.translate(require_all_pr=False)`. The theorem statement was rendered
  independently from the prompt by my own code and compared; there were 0 mismatches.
- I scanned for `sorry` / `admit` / `axiom` / `native_decide` / `decide` / `exact?`. The only hit was `Classical.byContradiction`
  (422 times), which is the classical rules DN/RAA.
- I checked the proofs in Lean core with no Mathlib: 40 theorems per file, 22 files. **All 870 were accepted**, with no output and
  exit code 0.
- As a negative control, a file with one goal changed to `False` and one `sorry` theorem gave an error and a sorry warning (exit
  code 1).
- The literal sampled texts are not stored: the environment returns ND, and `lean_gate` registers Lean's verdict on the literal text
  under the (prompt, ND) key. So "from stored literal text" here means the stored ND re-rendered to Lean. This is the same path every
  state-policy run has used.

### R5. Term size, by my own counter

My counter builds a tree: PR/AS count 1, R is transparent, and every other rule counts 1 + the sizes of its references (shared
subproofs are duplicated). I also report the DAG size (distinct lines reached, excluding R). Medians are taken over solved
(checkpoint, theorem) pairs of the per-theorem minimum.

| stratum | C tree / dag / lines | S | C′ | B |
|---|---|---|---|---|
| exact-17 | 29 / 19 / 21 | 30 / 20 / 21 | 31 / 19 / 21 | 29 / 19 / 19 |
| ≥ 18 | 32 / 20 / 21 | 32 / 20 / 21 | 30 / 20 / 21 | 27 / 19 / 20 |
| rr 15 | 21 / 16 / 17 | 21 / 15 / 16 | 21 / 16 / 16 | — |
| rr 16 | 22 / 16 / 18 | 22 / 17 / 18 | 23 / 16 / 18 | — |

Term size does not separate the arms: S solves more theorems, not differently sized proofs. The median written line counts of the
lp2 solves (21) are above the `L_lb` labels (17–18), which is consistent with labels being lower bounds and proofs carrying R/PR lines.

### R6. Split disjointness

I used my own renaming-class key: my own parser, the minimum over the 24 atom permutations, and the premise set sorted with
duplicates and order ignored. Overlaps of each training source with each evaluation pool:

| training source | lp2_91 | rr600_13_16 | t_long2 | t_long2_calib | t_long_rr600 | t_long_ge17 | t_long | transfer | heldout | p2/heldout | val_36 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| supply kept (6,466 classes) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| every supply candidate (46,834) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rl_targets (4,495) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| train_k12 (154,382) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 331 | 22 | 2 |

- The read-out pools, and every long pool, are disjoint from all training data.
- The K12 overlaps with `data/heldout`, `p2/heldout`, `transfer` and `validation_36`, and the `rl_targets` overlap with `transfer`, are
  inherited from cap-horizon and the ladder. They touch no quantity of this run: the per-round sampled transfer evaluation was off, and
  greedy transfer and held-out are diagnostics only.
- The in-loop leak filter dropped 0–1 (a) and 3–21 (b) candidates per ladder.
- `data/ladder/reserve.jsonl`, which the pre-registration lists as a leak pool, does not exist in the repository or on `origin/dan`.
  `supply_leak.json` records it as "missing". My check makes this moot for the pools that exist, but a reserve pool was never checked
  because none exists.

### R7. Hard constraints

- **`nd_verify` is unmodified.** Its tree hash `9437bb72` equals `origin/main`'s.
- **`nd_verify` is not used as a judge.** The run's only new import from it is `parse_formula`, in `supply.py:53` (parsing
  statements). Judging goes through `eval_set.judge` → `lean_judge.judge_many` (Lean).
- **`artifacts/TEST_RUN_DONE` is unchanged.** Its blob `1d5cf064` is the same as `origin/main`'s.
- **Evaluation files are not read in training code.** `state_ladder_ei.py` reads the long pools only to build the exclusion set for
  candidates (R6). It already read transfer/held-out for greedy diagnostics before this run. No evaluation theorem enters a training
  file.
- **The expected results were committed before the first pod.** The pre-registration was committed at 02:06 (`bbeca3f5`) and the
  primary-quantity deviation at 02:11 (`7c54dfc6`); the first pod, `fsup1`, started at 02:22.
- **The 04:00 relaunch was not selective.** All five ladders killed at 04:00 were relaunched from scratch with the same seeds. Their
  round-1 numbers reproduce exactly: R s0 3,586, R s1 3,722, S s2 3,682 (filter 152 pass), S s3 3,637 (172 pass).

### R8. Compute (registry rows, NVIDIA A40)

| arm | GPU-s per ladder | gen tokens | train steps | train tokens | Lean checks |
|---|---|---|---|---|---|
| S s0–s5 | 19,339 – 20,589 (mean 19,977) | 244 – 258 M | 4,800 | 676 – 724 M | 610 – 690 k |
| C s4, s5 | 21,377, 19,689 | 261 M, 247 M | 4,800 | 690 M, 686 M | 857 k, 858 k |
| C′ s0, s1 | 19,880, 19,918 | 244 M, 247 M | 4,800 | 663 M, 685 M | 758 k, 828 k |

- S is within 1.25× of C on every metric: S's train tokens are about 4 % higher, and its Lean checks are lower.
- C s4's registry shows 1,352,840 attempts and 14.5 M actions. That is 143,840 attempts (one round) more than every other ladder's
  1,209,000, which looks like a doubly-recorded round. Its GPU-s may be inflated by one round's sampling.
- The reused C s0–s3 have no registry rows here. The read-out rows for C s0–s2 are also absent: only `rr_la_C_s{3,4,5}` exist, and
  `rr_la_C_s3` counts 204,800 attempts, a partial duplicate.

### R9. Settings checks

- The read-out peak memory was 12.1–17.3 GB at batch 2048.
- Cut-offs (action truncation + step cap), as a fraction of samples:
  - ≤ 0.09 % on every read-out except S s5 rr (0.14 %) and B s5 lp2 (0.63 %).
  - Both are above the policy's ≈ 0.1 %, B s5 clearly so.
  - Neither touches a decision quantity much: B has no rr, and S s5's 0.14 % is spread over 400 theorems × 256 samples.

## Comparison (phase 2)

I read `run_frontier_supply.md`, `numbers.md` § frontier-supply (FS-1…6) and the frontier-supply part of `log.md` only after
committing §Recount (commit `49ec722f`). The model is the same as above (SN-cap12) for every row.

| claim (executor) | my value | verdict |
|---|---|---|
| FS-1 per-seed primary: C 142/207/218/220/220/207; S 139/217/226/233/228/216; C′ 145/197 | identical (R1) | reproduces |
| FS-1 on the 91: C 33/60/57/58/61/47, S 36/62/61/66/66/58, C′ 34/52; base 7/20/18/23/25/19 | identical | reproduces |
| FS-2 primary S − C −3, +10, +8, +13, +8, +9; mean 7.5, IQM 8.8, CI [2.5, 11.0]; flips 158 / 113 | identical; flips 158 / 113 | reproduces |
| FS-2 on the 91: mean 5.5, CI [2.8, 8.8], flips 69 / 36; exact-17 +4.0 (6/6); ≥18 +1.5; rr 15–16 +2.0 [−2.8, 6.0]; rr 13–14 +1.3 | +5.5 [2.75, 8.75]; +4.0 (6/6); +1.5; +2.0 [−2.75, 6.0]; +1.3 | reproduces (flips on the 91 not separately recounted) |
| FS-3 C′ − C +3, −10, flips 48 / 55; sd_d 7.4 → MDD 10.5; S − C sd 5.5, t 3.4 | identical | reproduces |
| "S − C is inside the MDD, so the falsifier is met. There is no demonstrated frontier gain" | +7.5 < 10.5 | reproduces; correct reading of the pre-registered rule |
| "S beats C on the 91 in 6 of 6 seeds, on the primary in 5 of 6" | yes | reproduces |
| FS-4 filter 6,894 / 53,904 = 12.8 %; (a) 15.8 %, (b) 9.8 %; zero 40,686, easy 6,324 | 12.8 %, 15.8 %, 9.8 %; zero 75.5 %, easy 11.7 % (= 40,686 / 6,324 of 53,904) | reproduces |
| FS-4 per op: chain 10.5, conj 14.0, case 15.4, contrapose 22.7, hyp 32.3 % ("S s0–s3, s5") | over all six seeds: 10.5, 13.8, 15.3, 22.6, 32.0 % | differs by ≤ 0.3 pt because of the seed subset; fine as labelled |
| FS-4 window 13–16 → 14–17 from round 2 (s2, s4), 3 (s1, s3, s5), 7 (s0); no shortfall; leak drops 75 (21/14/4/10/10/16); kept pool 1,075…1,120 | identical | reproduces |
| FS-4 kept targets' shortest proof: median (a) 13–15 lines, (b) 9–10 | over **all** kept proofs: (a) 16, (b) 11 (different statistic) | consistent |
| FS-5 read-out solves: median 20–22 lines, term size 14–17 on the 91; S and C do not differ | lines 21 in every arm; my tree / DAG sizes 29–32 / 19–20 (a different definition from `lean_check`'s elaborated term size) | "S and C do not differ" reproduces under my measure too; absolute term sizes are not comparable across the two definitions |
| FS-5 "0 rejected" by `lean_check` | my Lean re-check: 870 / 870 accepted | reproduces |
| FS-6 GPU-s: S 19,340–20,434; C s4 / s5 20,491 / 19,689; C′ 19,880 / 19,918; within 25 % | registry sums: S 19,339–20,589; C s4 **21,377**; others identical | reproduces for the claim. C s4's registry carries a second round-1 `sample` row (143,840 attempts, 887 GPU-s) left over from the ladder killed at 04:00. The executor's 20,491 = 21,377 − 887 excludes it correctly, but the registry row is still there. S s4 is 20,589, not 20,434 (the range is slightly off). |
| "Compute matched: … GPU-seconds within ±5 %" | S mean 19,977 against C s4 / s5 20,491 / 19,689 | reproduces |
| "Supplied targets are rare but **short** …: the filter selects rarity, not length" | the (a) window never exceeded ub 17 (base 12 → 13, pinned to the `rl_targets` L*), so length was capped **by the window rule, not by the filter**; (b) open goals are sub-goals, short by construction; 48 % of (a) proofs are ≥ 17 lines | **reword**: the design did not offer targets at the read-out's 17–18 length, so this run cannot say whether the filter selects against length |
| "Stage-1 bases read on the 91 only (… budget)" | the B s0 / s1 rr read-outs OOM'd (04:24–04:26 logs), and s2–s5 were cut at 10:10 for budget | reproduces (the caveat is disclosed); the pre-registered "frozen reachability on every read-out pool" is a **miss** on rr 13–16 |
| `reserve.jsonl` missing ("a generator reserve, not an evaluation pool") | missing; my R6 check finds 0 overlaps with every pool that exists | fine; the pre-registration's leak list named a file that does not exist |
| C re-reads match long-pool-2 (33 / 60 / 57 vs 34 / 59 / 58) | 33 / 60 / 57 / 58 | reproduces (±1 is a sampling re-draw on another pod) |

**Expectations and misses.** The pre-registration was committed at 02:06 and the deviation at 02:11, both before the first pod
(02:22). The write-up reports every expectation against its outcome:
- Filter ≥ 5 %: met.
- S − C > MDD: missed, and reported as a miss.
- The point forecast +8 came out as +7.5.
- C vs C′ ≤ 12: met.

The (a) 12 % and (b) 6 % per-source forecasts are not tabulated against their outcomes (15.8 % and 9.8 %). This is minor.

**Wording against n.**
- "no demonstrated frontier gain" is right under the pre-registered rule.
- "The direction is consistent" is right: 5/6 on the primary and 6/6 on the 91.
- The run avoids "never" and "wall".
- The MDD rests on 2 C′ pairs (sd_d from 2 df). The write-up says so and names the fix.

**Model labels.** `numbers.md` and `run_frontier_supply.md` name SN-cap12 (`lean_staten`, 3.2 M parameters, from scratch, K12)
for every number. The reused C s0–s3 carry their state-cap12 origin, and the long-pool-2 comparison is on the same checkpoints. No
unlabelled number was found. There is no comparison with a pre-2026-09-27 (Lean ∧ `nd_verify`) number.

**Hard constraints.** None was violated (R7), so there is no quarantine.

## Verdict

**What stands.**
- The filter produces targets: 12.8 % pass at p̂ ∈ (0, 1/4], above the 5 % floor, with (a) 15.8 % and (b) 9.8 %.
- The pre-registered test is not met: primary S − C = +7.5 of 291 against a C′-based MDD of 10.5.
- Every per-seed count, paired difference, interval, flip count and compute figure reproduces from the raw rows with my own code.
- 870 / 870 stored proofs pass Lean on re-check.
- The splits are disjoint from every read-out pool.

**What must be reworded.**
1. "the filter selects rarity, not length" should become something like "the supplied targets were short because the length
   window was anchored to the `rl_targets` L* (12–13), giving upper bounds of at most 17; the run did not offer targets at the
   read-out's length".
2. FS-6's S range should be 19,339–20,589 GPU-s. Note that the C s4 registry carries a stale round-1 row from the killed ladder.
3. List the per-source forecast misses (the forecasts were lower than the outcomes) in the expected/outcome table.

**What is not supported.** Nothing claimed is unsupported. The write-up does not claim a gain.

A reader should not infer "no effect" either:
- The paired differences are positive on 5/6 seeds on the primary and 6/6 on the 91 and on exact-17.
- The paired t is 3.4 (p ≈ 0.02), and the IQM bootstrap CI [2.5, 11.0] excludes 0.
- The miss comes from a C′-based sd_d estimated from 2 pairs, one of them −10.

"Small positive effect, not established against the pre-registered MDD" is the accurate summary. The gain is concentrated on
exact-17 (+4.0 of 61) and absent on rr 15–16 (+2.0, inside its noise).

**Next measurements.**
1. C′ on s2–s5, four ladders. This is about 4 × 5.5 A40-hours, roughly $11. It turns sd_d into a 6-pair estimate, and it settles
   whether +7.5 is outside the MDD. With 6 pairs, a sd_d near the S − C sd of 5.5 would give an MDD of about 8.
2. Stage-1 base read-outs on rr 13–16 for all six seeds, about 16 min each. They complete the pre-registered frozen reachability.
3. If (1) confirms the effect: a supply arm whose window is anchored to the model's read-out frontier (base 16–17) rather than the
   `rl_targets` L*. This separates "more rare targets" from "longer targets".
