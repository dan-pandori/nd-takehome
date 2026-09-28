# Review — run `state-env` (proposal 13: an AlphaProof-style proof state for the policy)

Reviewer: agent:claude (reviewer role), a separate session from the executor. Started 2026-09-28 15:50 UTC.
Phase 1 was done in `~/review/state-env`, a copy of the run's repository with the executor's write-ups removed. I used
the run brief (`STATE_ENV.md`), `preregistration/state-env.md`, the code, `data/` and the raw artefacts under
`artifacts/se/`. Every number below comes from code I wrote for this review, in `review_se/`:

| script | what it re-derives |
|---|---|
| `review_se/recount.py` → `recount.json` | per-round ladder counts from `found_transfer_<r>.jsonl` / `found_<r>.jsonl` with my own start-index normaliser, `L*` and `≥ L` counts, textbook slice, held-out rates and failure reasons from `heldout_*.jsonl`, env diagnostics from the raw counters in `round_<r>.json`, renaming-class split disjointness under a real canonical form |
| `review_se/c0.py` | the C0 control's on-file numbers from `git show HEAD:artifacts/dsg/…`, plus what Lean alone would add to them (from the gate's Lean-vs-`nd_verify` disagreement logs) |
| `review_se/lean_recheck.py`, `run_recheck.py` → `recheck.json` | Lean 4.34.1 core re-check of 2,792 counted proofs, with negative controls |
| `review_se/gate2_recheck.py` → `gate2_recheck.json` | gate 2 ("the environment's state is Lean's state"), re-run in Lean and parsed with my own precedence parser |
| `review_se/termsize.py` → `termsize.json` | a term size I defined independently of `lean_check` |

## §Recount (phase 1, written before reading `run_state_env.md`, `numbers.md` or `log.md`)

### R0. The models these numbers are about

| label | checkpoint | params | format | from scratch? | training set |
|---|---|---|---|---|---|
| **S** (state only) | `ckpts/se/stage1_S_s{0,1}.pt` | 3,216,384 (from the training logs) | `lean_state` = `lean_seq` + 4 tokens | yes | `data/p2/train_depth3_f0_a1.jsonl` (155,000 records, cap 6, depth 3 with f = 0); 6,000 steps × 128 proofs (≈ 640 pairs) |
| **SH** (history + state) | `ckpts/se/stage1_SH_s{0,1}.pt` | 3,216,384 | `lean_stateh` | yes | same |
| **SN** (canonical names; "SN-v2" = these checkpoints sampled with environment-assigned names) | `ckpts/se/stage1_SN_s{0,1}.pt` | 3,216,384 | `lean_staten` | yes | same set, alpha-renamed by `state_env.canonicalise` |
| **C0** (whole-proof control, on file) | `ckpts/lf/stage1_a1_seq_s{0,1}.pt` | 3,214,336 | `lean_seq` | yes | same set; `train.py --bs 128 --steps 6000` |

The +2,048 parameters are the 4 extra token embeddings (4 × 256 × 2). T1 is 8 rounds of expert iteration from each
Stage-1 checkpoint (`state_ladder_ei.py`: k = 32, T = 0.8, env batch 2,048, `--max_action 256`, `--max_steps 48`, the same
values in every `args.json`). "Frozen" is the same loop with `--no_train`. RL-target attempts are equal between T1 and
frozen in every arm: `alloc_8.json` gives 1,150,720 = 4,495 × 32 × 8 tried in all 12 ladders. S, SH and SN numbers are
under **Lean alone**. C0's on-file numbers are under **Lean ∧ `nd_verify`** (`ds-generator`, 2026-09-23/24).

### R1. Transfer pool (2,285 theorems, `data/ladder/transfer.jsonl`), cumulative at round 8

`L*` = max L with ≥ 5 theorems solved at `L_true` ≥ L. `L_true` is the pool's ND-derived `n_lines`, which is an upper
bound under Lean. "Textbook" = the 760 transfer theorems with `source == textbook` (19 schemata).

| arm | T1 solved s0 / s1 | T1 `L*` | T1 solved at `L_true` ≥ 12 | T1 ≥ 13 (which) | T1 textbook /760 | frozen solved | frozen `L*` | frozen ≥ 13 |
|---|---|---|---|---|---|---|---|---|
| S | **1,348 / 1,389** | 12 / 12 | 8 / 11 | **1 / 2** (`la_transfer_1126`; `1126`, `1198`) | 182 / 216 | **779 / 787** | 11 / 10 | 0 / 0 |
| SH | 1,257 / 1,390 | 12 / 12 | 6 / 8 | 0 / 0 | 148 / 201 | 516 / 479 | 10 / 10 | 0 / 0 |
| SN (v2) | 1,557 / 1,403 | 12 / 12 | 18 / 12 | 3 / 1 (`978` (L 14), `1126`, `1198`; `1126`) | 236 / 197 | 975 / 801 | 11 / 11 | 0 / 0 |
| C0 (git; Lean ∧ `nd_verify`) | 890 / 965 | 12 / 11 | 5 / 3 | 0 / 0 | 37 / 89 | 158 / 114 | 9 / 9 | 0 / 0 |
| C0 with Lean-only accepts added | 892 / 966 | 12 / 11 | — | 0 / 0 | — | 165 / 116 | 9 / 9 | 0 / 0 |

- Every per-round count (solved, `L*`, RL targets solved) that I re-derive from `found_*` matches the round json's own
  summary in all 12 ladders × 8 rounds. Found sets are cumulative with 0 theorems lost between rounds. After my own
  normaliser there are 0 duplicate proofs. The stored `written` length equals my own line count for every row.
- The three `L_true` ≥ 13 theorems any arm solved are ordinary ND proofs. Their written length is at least `L_true`
  (1126: 13 lines = `L_true`; 978: 14 = `L_true`; 1198: 13–29 lines). None uses the Lean-only `n.elim`-on-`¬A`
  shortcut (my own predicate: `BOTE` citing a non-`F` line). So they are not an artefact of switching checkers. No
  frozen run solves any of them at equal attempts.
- Adding Lean-only accepts back to C0 changes almost nothing (+2 / +1 T1, +7 / +2 frozen, none at ≥ 13). The C0
  comparison is not distorted by the checker change.
- The SH arm's round-1 counts differ between T1 and frozen (378 vs 373; 332 vs 348), although both start from the same
  checkpoint with the same seed. For S and SN they are identical (577 = 577, 588 = 588, 794 = 794, 604 = 604). This is
  consistent with a sampling re-draw on a different pod (`NOISE_FLOOR.md`: sampler contributes ≈ 0), not a bug.

**Against the noise floor** (`NOISE_FLOOR.md`, measured on **C0's configuration**, not on these state models, so it
is the nearest available reference and no more):
- Frozen solved: S − C0 = (779 + 787)/2 − (158 + 114)/2 = **+647**, above the MDD of 397. Ratio 5.8× vs the 3.35×
  floor. SN: +752. SH: +362, **inside** the floor.
- Frozen `L*`: S 10.5 vs 9 (+1.5), at the edge of the ±2 resolution. SN +2, at the edge. SH +1, noise.
- T1 solved: S − C0 = +441, SN +553, SH +396. No T1 floor has been measured. The C0 T1 re-draw spread on one
  checkpoint is 856 / 890 / 923.
- T1 `L*`: 12 / 12 vs 12 / 11 for every arm — no resolvable difference.
- With n = 2 the IQM is the mean. A stratified bootstrap over two values is degenerate, so I report per-seed values.

### R2. Held-out greedy (5,000, `data/p2/heldout.jsonl`), in the environment, Stage-1 checkpoints

| arm | s0 | s1 | 6-line bin s0 / s1 | how failures end (s0; s1) |
|---|---|---|---|---|
| S | **0.9578** | **0.8012** | 0.904 / 0.678 | 191 Lean-rejected, 20 env-syntax; **581 `unbound`**, 343 Lean-rejected |
| SH | 0.9516 | 0.9554 | 0.870 / 0.895 | 201 / 202 Lean-rejected |
| SN (v2) | 0.9700 | 0.9584 | 0.941 / 0.904 | `unbound` 2 / 1 |
| SN-v1 | 0.9716 | **0.6230** | 0.944 / 0.663 | s1: **1,424 `unbound`**, 392 Lean-rejected |
| C0 (git `heldout_c0_s*.json`, Lean ∧ `nd_verify`) | 0.9088 | 0.8960 | 0.686 / 0.582 | — |

All of these match the `*.json` summaries. SN-v2's sampling really assigned names: `names_renamed` is 6,054 / 6,026 of
≈ 19,800 names defined; the counter is absent for S and SN-v1. The pre-registration quotes C0 s1 as 0.8968 / 0.584, but
the file on disk says 0.8960 / 0.582 — a 0.1–0.2 pp difference in an inherited number. The noise floor for held-out
overall at n = 2 is 16.3 pp, and the 6-line bin is "not resolvable at n = 2 at all" (`NOISE_FLOOR.md`).

### R3. Environment diagnostics (round 8, from the raw counters; all sampling in the round)

| arm s0 / s1 | mean actions per attempt | attempts ended by an env syntax check | actions that hit `--max_action` 256 | step cap | peak `max_memory_allocated` |
|---|---|---|---|---|---|
| S | 8.51 / 8.75 | 11.1 % / 11.1 % | 0.002 % / 0.008 % | 0 | 10.2 / 12.7 GB (held-out job 7.6 / 8.1 GB) |
| SH | 8.30 / 8.48 | 13.0 % / 10.4 % | 0.003 % / 0.005 % | 0 | 19.0 / 20.4 GB |
| SN | 9.41 / 8.96 | 7.2 % / 6.0 % | 0.000 % / 0.005 % | 0 | 12.5 / 12.1 GB |

These counters are the run's own. I can re-derive the ratios from them, but not the counts themselves, because the
per-attempt stream is not stored. The batch probe (`probe_b{1024..8192}.json`, S s0 on the RL targets at k = 1) solves
943–986 of 4,495 across batch sizes, which is what a re-draw looks like.

### R4. Lean re-check of counted proofs

- **Sample.** 2,792 counted proofs, all re-checked in Lean. The 14 ladder runs contribute 192 proofs at `L_true` ≥ 12
  (every one there is), 120 random transfer proofs each and 30 random RL-target proofs each. The 8 held-out files
  contribute 100 random solved proofs each. Per arm: S 837, SH 823, SN 1,132 (including SN-v1 held-out), all ≥ 100.
- **Renderings.** Each proof was rendered two ways: (a) my own ND → Lean term-mode translator, which does not import
  `nd2lean` or `lean_tok` and picks each application's function by formula; (b) `lean_tok.proof_tokens`, the
  `lean_seq` text the environment assembles, modulo hypothesis names.
- **Checking.** One theorem per line with `#print axioms` after it and `-DmaxErrors`. Any error in a theorem's line
  range rejects it. Axioms must be a subset of {`propext`, `Classical.choice`, `Quot.sound`}.
- **Result: 0 of 2,792 rejected under either rendering.**
- **Negative controls, run first.**

  | control | own translator | `lean_seq` rendering |
  |---|---|---|
  | untouched counted proofs, must pass | 150 / 150 | 150 / 150 |
  | one `ORI1`↔`ORI2` / `ANDE1`↔`ANDE2` flip, should fail | 137 / 150 | 137 / 150 |
  | proof paired with a different theorem of the same premise count, must fail | 150 / 150 | 150 / 150 |
  | samples the run itself recorded as `LEANREJ`, must fail | 200 / 200 | 200 / 200 |
  | bare `sorry`, must fail | 20 / 20 | — |

  The flipped proofs that passed are benign no-ops: in a fresh sample, all 25 passing flips out of 218 were
  `X ∧ X` / `X ∨ X`. The controls also caught a bug in my first translator (zero-premise prompts failed to parse; 23 of
  the 150 untouched proofs were rejected). I fixed it before the real pass.
- **Finding A1 (auditability).** The run did **not store the literal sampled text**. `LEAN_GATE_DUMP` was not set in
  `pod/se/env.sh`, and `found_*.jsonl` / `heldout_*.jsonl` hold the ND string that `lean_tok.inverse` decoded from it.
  So my re-check is of a faithful re-rendering, not of the literal text the policy (Dan, 2026-09-27) names as what
  counts. The two are alpha-variants: the model's names, including S's random offset, are replaced by N-indices, with
  shadowing resolved lexically as Lean does. Lean's verdict should not depend on that. Still, "the literal text" cannot
  be re-checked from the pulled files.

### R5. Term size (my definition, not `lean_check`'s)

Term size here = the lines reachable from the conclusion by following citations whose rule is not `PR` or `R`. A box
is reached through the rule citing it. For each solved transfer theorem I take the smallest such proof found.

| arm | theorems whose smallest found proof has term size ≥ 12 (s0 / s1) | largest (s0 / s1) | median size at `L_true` 12 |
|---|---|---|---|
| T1 S | 11 / 10 | 18 / 17 | 10 / 10 |
| T1 SH | 1 / 5 | 13 / 12 | 9.5 / 10 |
| T1 SN | 23 / 9 | 25 / 14 | 10 / 10 |
| T1 C0 | 0 / 0 | 10 / 11 | 9 / 9 |
| frozen S / SH / SN / C0 | 0 / 1, 0 / 0, 3 / 1, 0 / 0 | ≤ 14 | — |

Term size and line count tell the same story. Per `L_true` bin the medians are the same across arms: sizes 6 / 7 / 8 /
8–9 / 9–10 at `L_true` 7–11, one to two below the line count. The state-conditioned T1 runs reach proofs with 12–25
inference nodes; C0's T1 reaches 11 at most.

### R6. Gates

- **Gate 2** (state = Lean's state), re-run from the stored case sources: **0 mismatches / 5,600**. That covers 2,000
  random, 500 `Or.elim`, 300 negation, 1,300 canonical and 1,500 gate-2b cases. Gate 2b spans 510 top / 922 imp / 18
  or1 / 29 neg / 21 or2 frames.
- **Gate 2 negative control.** I mutated 600 gate-2b cases (dropped a hypothesis, renamed one, or changed the goal).
  594 were flagged; the 6 unflagged were zero-hypothesis states, where the drop and rename mutations do nothing.
- **Limitation.** I compared Lean's state against the renderer state *stored in the case file*. I did not re-run
  `state_env` to confirm that the stored state is what the policy was shown.
- **Gates 1 / 1b / 3** (byte-identical round trip, environment replay) need the environment's own decomposition. I did
  not re-implement it, so these are **not re-derived**.

### R7. Splits (renaming class = min over the 24 bijections of {P,Q,R,S} of (sorted premise multiset, conclusion); `F` is falsum)

| pair | colliding theorems |
|---|---|
| train (155,000) vs transfer (2,285) | **0** |
| train vs RL targets (4,495) | **0** |
| train vs held-out (5,000) | 21 (premise-order variants, lengths 3–6; inherited from the `p2` set, same as found in earlier reviews) |
| RL targets vs transfer | **2** (`la_transfer_842`, `la_transfer_307`, both `L_true` 9; premise-order variants of `la_rl_targets_363` / `_2228`; inherited from the ladder pools) |
| held-out vs transfer | 0 |
| train vs `targets/validation_36.jsonl` | 1 |

Transfer is never trained on: the fine-tune mix is RL-target proofs plus retained training records. The 2
target/transfer collisions are worth at most 2 of ≈ 1,350 solved and do not touch `L_true` ≥ 10.

### R8. Hard constraints

- `nd_verify/` tree at the run's HEAD = `9437bb72…` = `origin/main`'s. **Unmodified.**
- `nd_verify` is not used as a judge anywhere in the run's code. Judging goes `state_sample` → `lean_gate` (Lean on the
  assembled text) → `eval_set.judge` → `lean_judge.judge_many`. `state_env.py` and `lean_tok.py` import only
  `nd_verify`'s *parsers* (`parse_formula`, `parse_proof_tokens`). C0 comparisons carry the "Lean ∧ `nd_verify`" label
  in the pre-registration, `se_tables.py` and `se_figures.py`.
- `artifacts/TEST_RUN_DONE`: blob `1d5cf064…`, identical in HEAD, `origin/main` and `origin/dan`; the file's SHA-1 in the
  review copy matches. **Unchanged.**
- No evaluation file is read in training code. `state_train.py --heldout` loads the first 2,000 held-out records only
  for a `torch.no_grad()` validation loss; no checkpoint is selected on it. `state_ladder_ei.py` reads transfer and
  held-out only to sample and judge them. No `targets/test*` reference exists in `state_*.py`, `se_*.py` or `pod/se/`.
- **No hard-constraint violation. No quarantine.**

### R9. Pre-registered predictions for arm S, against the recount

| quantity | predicted | recount (s0 / s1) | hit? |
|---|---|---|---|
| held-out greedy overall | 0.85 – 0.95 | 0.9578 / 0.8012 | **miss on both seeds**, in opposite directions |
| held-out 6-line bin | ≥ 0.60, and ≥ C0's own seed on ≥ 1 seed | 0.904 / 0.678 vs C0 0.686 / 0.582 | hit |
| T1 transfer solved | 700 – 1,250 | 1,348 / 1,389 | **miss** (above) |
| T1 `L*` | 12 (11–13) | 12 / 12 | hit |
| T1 solved at `L_true` ≥ 13 | 0 – 3 | 1 / 2 | hit |
| T1 textbook / 760 | 20 – 120 | 182 / 216 | **miss** (above) |
| frozen transfer solved | 80 – 400 | 779 / 787 | **miss** (about 2× the top of the range) |
| frozen `L*` | 9 (8–10) | 11 / 10 | **miss on s0** |
| mean actions per attempt | 4 – 12 | 8.51 / 8.75 | hit |
| attempts ended by syntax | < 45 % | 11.1 % / 11.1 % | hit |
| actions hitting 256 | < 0.1 % | 0.002 % / 0.008 % | hit |
| SH vs S held-out | SH ≥ S by ≤ 2 pp | −0.6 pp / +15.4 pp | **miss** |
| SH vs S T1 solved | indistinguishable | −91 / +1 | hit (inside 62–265) |
| **falsifier 1** (`L*` ≥ 13 with ≥ 5 at ≥ 13, both seeds) | — | `L*` 12, 1 / 2 | **does not fire** |
| **falsifier 2** (`L*` ≤ 12 with 0 at ≥ 13, both seeds) | prior 0.6 | 1 / 2 at ≥ 13 | **does not fire** → the pre-registered "moved but not decisive" band |

SN (addendum 1, carried to SN-v2):

| prediction | recount | hit? |
|---|---|---|
| T1 ≥ S on the same seed | 1,557 vs 1,348; 1,403 vs 1,389 | hit, but s1's +14 is noise |
| gain large on s1, small on s0 | +209 on s0, +14 on s1 | **miss**: the opposite |
| 0–5 at `L_true` ≥ 13 | 3 / 1 | hit |
| held-out ≥ 0.94 with spread < 3 pp; `unbound` < 1 % | 0.9700 / 0.9584, spread 1.2 pp; 2 / 1 `unbound` | met, but measured after the SN-v2 decision, which the addendum itself says does not count as confirmation |

Process notes:
- The pre-registration was committed at `5bb93132` (04:21:13 UTC), before the first pod (`se-1`, 04:22:57 UTC in `~/pods.log`).
- The SN addenda are labelled "added after seeing a result".
- The pre-registration gives no minimum detectable difference for its headline quantities, which `AGENT_POLICY.md`
  requires. It quotes only the frozen run-to-run range. The rule is dated 2026-09-28, the same day, so it may
  post-date the pre-registration.
- T1 S s0 resumed at round 3 and S s1 at round 2 after the empty-term crash fix (`42742a82`). The fix changes only
  attempts that crashed.
- T1 SH s0 resumed at round 6 with the micro-batched fine-tune (`dd610df3`).
