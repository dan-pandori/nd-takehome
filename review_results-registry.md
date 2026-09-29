# Review — results-registry

Reviewer session, 2026-09-29 (started 01:00 UTC). Branch `dan_results-registry` at `3bfdec15`, which the brief says
is merged into the fork's `dan` after acceptance (`origin/dan` = `3bfdec15`; authorised by the brief's Deliverables,
not a finding). Phase-1 workspace `~/review/results-registry` (write-ups removed). All scripts are `review_rr_*.py`
in this commit; they read the phase-1 copy and the public bucket, and write scratch to `/tmp/rrrev/`.

## §Recount (phase 1, written before reading `run_results_registry.md`, `numbers.md`, `log.md`)

This is an infrastructure run. It makes no model-quality claim. The pre-registration promised E1–E5, and I
re-derived each one with my own code.

### Hard constraints

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash `9437bb72…` at HEAD = `origin/main` ✔ |
| `artifacts/TEST_RUN_DONE` unchanged | blob `1d5cf064…` at HEAD = `origin/main` = run base `e455e037` ✔ |
| `nd_verify` used as a judge in this run's diff | no: the only new mentions are the checker *label* in `registry_backfill.py` ✔ |
| evaluation file read in training code | no new read. `record.py` md5-hashes the `--heldout` file inside the EI driver, which already reads it to evaluate. `train.py` / `fast_train.py` / `state_train.py` gained only `set_config` / `preflight` / `train_rows` ✔ |
| splits disjoint by renaming class (`review_rr_splits.py`; my key: atoms renamed, premises as a sorted multiset, minimum over atom permutations; control: a renamed training theorem collides ✔) | train `p2/train_depth3_f0_a1` (154,494 classes) vs `rr_heldout200`, `heldout[:500]` (smoke `eval_set`), `rr_transfer40`, `transfer[:2]` (coverage), `rr_targets40`: **0** shared each. Targets / transfer / held-out subsets pairwise: 0 ✔ |

No hard-constraint violation, so no quarantine.

### Lean re-check of counted proofs

The run counts proofs only in its smoke jobs, on throwaway models. Every stored counted proof is re-checked below
(22 in total: fewer than 100 exist).

Model labels: `smoke_s0` is a 3.2 M-parameter (3,214,336) `lean_seq` model trained from scratch for 300 steps on
`p2/train_depth3_f0_a1`, seed 0. `fs/fast1_s0` is fast-stage1's from-scratch 3.2 M `lean_seq` Stage-1 model.
`ei_fast1_s0_r1/_r2` are 30-step EI fine-tunes of it.

`review_rr_lean_recheck.py` renders each stored ND proof with the unmodified `nd2lean.translate` and runs each
theorem through `lean` alone, one process per theorem:

| source | Lean-accepted / stored |
|---|---|
| `smoke_s0` held-out greedy (`heldout_greedy.jsonl`, 4 solved of 500) | 4 / 4 |
| `ei_fast1_s0` `found_1`, `found_2`, `found_transfer_1`, `found_transfer_2` | 2/2, 6/6, 2/2, 8/8 |
| negative control: a translated proof with `Or.inr` → `Or.inl` | rejected ✔ |

Limitation (pre-existing, not introduced here): `eval_set.py` / `expert_iter.py` store the ND rendering, not the
literal sampled `lean_seq` text. So this re-check covers the rendering, not the literal string.

### E1 — every `ckpt_saved` row's URI downloads to a file with the recorded md5

`review_rr_e1.py` reads the eight live row files, downloads every `ckpt_uri` with `hf buckets cp`, and md5s it:

| ckpt | bytes | md5 (row = download) | upload_s |
|---|---|---|---|
| `rr/smoke_s0.state00150.pt` | 38,638,129 | `dc6f145e…` ✔ | 5.96 |
| `rr/smoke_s0.step00150.pt` | 12,876,613 | `0a4f424d…` ✔ | 3.43 |
| `rr/smoke_s0.pt` | 12,876,289 | `e0c3e36f…` ✔ | 4.12 |
| `rr/ei_fast1_s0_r1.pt` | 12,876,381 | `55499ed5…` ✔ | 3.74 |
| `rr/ei_fast1_s0_r2.pt` | 12,876,445 | `a163001b…` ✔ | 7.35 |

**5 / 5.** The bucket's `results-registry/ckpts/` holds exactly these five files, and local `ckpts/rr/` holds the
same five with sidecars. `train.log` prints each `uploaded …` line before the next training step, so the upload
blocks as designed. All checkpoint writes in the repository go through `save_ckpt` (grep `torch.save`: the only
other one is `fast_train.py`'s pretokenise cache). The two EI smokes from `smoke_s0` (`ei_smoke_s0`,
`ei_smoke2_s0`) accepted 0 proofs and trained nothing, so they saved no checkpoint. The checkpoints come from a
third EI run on `fs/fast1_s0`, which the pre-registration did not list; this is a harmless addition.

### E2 — negative controls (must fail)

`review_rr_e2.py` drives `record.run_id` / `record.publish_ckpt`, the non-torch half of `model.save_ckpt`. The VPS
has no torch, but `save_ckpt` is `run_id(required=…)` → `torch.save` → `publish_ckpt`, which I read.

| control | result |
|---|---|
| (a) one byte flipped in a downloaded checkpoint | md5 differs ✔ |
| (b) `ND_RUN_ID` unset: `run_id(required=True)` / `publish_ckpt` | `RuntimeError: ND_RUN_ID is not set` ✔ (also with `ND_OFFLINE=0`) |
| (c) non-existent bucket | `RuntimeError: upload FAILED … 404`, after 3 tries; **no sidecar written** ✔ |
| opt-out `ND_OFFLINE=1` | returns; sidecar `offline: true, uri: null` ✔ |

`tests/test_registry.py` (offline) passes: ALL PASS, with the `save_ckpt` torch cases skipped on the VPS.
Deviation from the pre-registration's wording: the opt-out is `ND_OFFLINE`, not `ND_CKPT_OFFLINE`.

### Row counts (`review_rr_e3.py`, my own reader of every `.jsonl` / `.jsonl.gz`)

299,006 rows = **63 live + 298,943 backfilled**, with 0 exact duplicates. There are 39 files: 8 live and **31**
`backfill_*` files, one per backfilled run. 32 run ids appear: 31 backfilled plus `results-registry`. I did not
check "32 reviewed runs" against a list. The run ids with a backfill file number 31, and `podjob` has none.

### E3 — "every held-out accuracy of the control checkpoints, by run" with one filter

Filter: `metric == heldout_greedy_acc`, overall rows only (no `L`, no `slice`).

| role set | rows | runs | runs with ≥ 1 row not shared with another run |
|---|---|---|---|
| pre-registered `{stage1, control, frozen}` (no row has `control`) | 1,964 | 21 | 19 (18 excluding `results-registry`) |
| implemented `{stage1, init, frozen}` | 3,091 | 25 | 23 (22 excluding `results-registry`) |

Against the threshold of **≥ 8 reviewed runs**, E3 passes by a wide margin under either reading. The table's
*content* has three defects:

1. **Every GRPO row in `run4-grpo` is labelled as the control checkpoint (`role=init`, `ckpt=` the Stage-1 init),
   but it measures the GRPO-trained model.** This affects 41 GRPO arms, 2,080 rows, and 260 overall
   `heldout_greedy_acc` rows, which fall in the E3 answer (8.4 % of its 3,091 rows) with values from 0.573 to
   0.917. Cause: old `grpo.py` wrote `ckpt: <init>` into every `round_<r>.json`. I verified this from the bucket
   copies of `grpo_g32_depth3_f0_a1_s22/round_{1,2,8}.json`, which all have `ckpt = ckpts/r4/stage1_depth3_f0_a1_s22.pt`.
   `round_stats` trusts that field. The same checkpoint measured by the EI arm's round 1 gives 0.8806. The GRPO
   rows give 0.6926, 0.6258, …, 0.6008 over rounds 1–8, so they are RL numbers. The live `grpo.py` passes the round
   checkpoint, so new runs are unaffected. The backfill needs `role=rl` (and no `ckpt`) for every GRPO round row.
2. **Rows are attributed to runs that inherited another run's artifacts.** Arms from lean-format (`la_T1_*`,
   `lf/*`) appear under `ds-composition`, `ds-generator` and `lean-seed2`. Novelty-campaign's `ei_abs_*` /
   `frozen_abs_*` appear under `ds-composition`, whose bucket prefix contains them. For example, 1,408
   named-arm rows are shared between ds-composition and novelty-campaign, and 1,224 between lean-format and
   lean-seed2. `NOT_OWN` excludes only `lf/summary.json`, not the round files. A "by run" count therefore counts
   some checkpoints under two to four runs.
3. **Superseded directories are backfilled under the same arm name.** `ds-composition/artifacts/dsc_pre_cleanup/`
   and `dsc/` both yield `arm=dsc/ei_a1_s0`. There are 75 (run, arm, round, ckpt, data) groups with two
   different held-out values, for example round 1: 0.9174 (`dsc`) vs 0.939 (`dsc_pre_cleanup`). Only `source`
   tells them apart.

Also: 240 held-out rows (ds-composition, novelty-campaign) have `data = None`. The query mixes `data/heldout.jsonl`
with `data/p2/heldout.jsonl`, and the live smoke adds `data/rr_heldout200.jsonl`, a 200-theorem subset, under the
same metric `heldout_greedy_acc`. This contradicts `record.split_of`'s stated intent ("a subset is never pooled
with the full set"). The live rows were written at `88a9bc9d`, and `round_stats` at HEAD would name the metric
`rr_heldout200_greedy_acc`, so this is a code-version artifact of the smoke rows.

### E4 — three headline numbers string-equal from the backfill (sources fetched independently from the bucket)

| number | source file (my fetch) | backfill row, `repr(value)` |
|---|---|---|
| lean-format `P1_heldout_greedy.token_full = 0.948` | `lean-format/artifacts/lf/summary.json` → 0.948 | `summary:P1_heldout_greedy/token_full` = `'0.948'` ✔ |
| ds-generator frozen C0 158 / 114 of 2,285 | `ds-generator/artifacts/dsg/summary.json` `rows[0,1].ladder.frozen.transfer_solved` = 158, 114; `transfer_n` = 2,285 | `'158'`, `'114'` ✔ |
| lean-prefilter 0 false rejects in 1,310,119 | no `summary*.json`; `lp/soundness.json` | every `…/false_rej` row = 0 ✔. 1,310,119 = `C1 all checkpoints (distinct)/n` 1,214,162 + `C2 all/n` 76,281 + `C3 all/n` 19,676: derivable from three rows, not stored as one |
| (the executor's substitute) state-env S s0 T1 solved 1,348 | `state-env/artifacts/se/summary.json` `headline.S.s0.T1_solved` = 1348 | `'1348'` ✔; also `transfer_solved_cum` arm `la_T1_S_s0` round 8, `labels.solved` = 1348 ✔ |

E4 reproduces 3 / 3 as pre-registered. The lean-prefilter number is reproducible as a sum, so a substitute was not
strictly needed.

### E5 — cost

- `record()` on the VPS, 2,000 rows (`review_rr_e5.py`): median **0.17 ms**/row, p99 0.25 ms, well under 5 ms. The
  first row that names a data file pays that file's md5 once per process.
- Upload per checkpoint, from the sidecars: 3.4–7.4 s for the 12.9 MB checkpoints and 6.0 s for the 38.6 MB state
  file, all under 30 s. Measured on the executor's pod; I did not re-time uploads.

### Other observations from the code and rows

- **Checker label follows the digest date, not the measurement date.** All 49,160 `run4-grpo` rows are labelled
  `lean`, but its artifacts are dated 2026-09-17/18, so they were measured before 2026-09-27. Runs from before
  `lean_gate.py` existed (first commit 2026-09-21: round2-*, round3-*, ladder-A, novelty-campaign, followup,
  ignition, run4-grpo) were judged in the loop by `nd_verify`. The Lean-agreement checks came afterwards, so
  `lean+nd_verify` follows AGENT_POLICY's blanket wording but is not literally how those runs counted.
- **Model label.** Live eval rows (`eval_set`, `coverage`, EI rounds) carry `ckpt` + `ckpt_md5` but no `n_params` /
  format. Only `train_rows` and `sdeval_rows` carry those. For EI / GRPO rows, `seed` is the driver's `--seed`,
  not necessarily the model's training seed, and REGISTRY.md's schema says otherwise. The EI fine-tune `train_loss`
  rows show `config.mode = 'rel'` (the argparse default) for a `lean_seq` model.
- Registry sync works: the bucket's `registry/results-registry/` holds the eight live files at the same sizes.

## §Compare (phase 2: `run_results_registry.md`, `numbers.md`, `log.md`, `STATUS.md`, `QUESTIONS.md`)

| claim (executor) | my value | verdict |
|---|---|---|
| E1 5 / 5 checkpoint URIs → recorded md5 | 5 / 5, own download + md5 | **reproduces** |
| E2 3 / 3 negative controls fail | 3 / 3, own harness (+ `ND_OFFLINE=0` still online) | **reproduces** |
| E3 "25 runs (24 reviewed + this smoke run), 3,091 rows" | 25 runs, 3,091 rows with `{stage1, init, frozen}`; 21 runs / 1,964 rows with the pre-registered `{stage1, control, frozen}` | **count reproduces; pass stands** (≥ 8) under either role set. **Content is wrong in part:** 260 of the 3,091 rows are GRPO-trained numbers labelled as the Stage-1 control (§Recount E3.1), and inherited arms are counted under several runs (E3.2). The `init` role replaced the pre-registered `control` without saying so |
| E4 3 / 3 exactly: 0.948; 158 / 114; state-env 1,348 as substitute "named before the check" | all four string-equal from my own bucket fetch. The substitute was named at 00:44:11 (transcript) and the acceptance run was at 00:50:00 | **reproduces.** lean-prefilter's 1,310,119 was reproducible after all, as the sum of three `/n` rows (1,214,162 + 76,281 + 19,676), with `false_rej = 0` in every row. The substitution was allowed but unnecessary, and "not stored, so the registry does not hold it" overstates the gap |
| E5 0.058 ms/row, 3.4–7.4 s / 12.9 MB checkpoint, 6.0 s / 38.6 MB state | 0.17 ms/row median on the VPS with a data file named. Upload seconds match the sidecars | **reproduces** (both ≪ 5 ms; the 3× difference is the per-row md5-cache / config path) |
| 298,943 backfilled + 63 live = 299,006; bucket alone gives the same | 298,943 + 63 = 299,006. The bucket `registry/` holds the same 39 files | **reproduces** |
| "backfill covers 32 reviewed runs" | 31 runs have rows (podjob has no result files, as REGISTRY.md says) | **reword:** 32 fetched, 31 with rows |
| "Checker labels: `lean+nd_verify` for runs before 2026-09-27, `lean` from then on" | label follows the *digest* date. `run4-grpo` (artifacts 2026-09-17/18) is labelled `lean` on all 49,160 rows | **differs:** 49,160 rows mislabelled. Runs before `lean_gate.py` (2026-09-21) were judged by `nd_verify` in the loop |
| model labels in `numbers.md` (smoke_s0 3.2 M `lean_seq` from scratch, 300 steps, seed 0; fast1_s0 3.2 M `lean_seq`, 6,000 steps) | match `train.log`, `ei3.log` (params 3,214,336, mode `lean_seq`) and the rows' configs | **reproduces**; every number in `numbers.md` names its model |
| smoke held-out greedy 4 / 500 | 4 / 500; all 4 proofs pass Lean | **reproduces** (throwaway model, labelled as such) |
| spend 0.21 pod-hours, $0.10, RTX 3090 at $0.50/h | not re-derived (no pod log read) | not derivable here |
| `log.md` / STATUS / QUESTIONS clock times (E4 substitute "01:05", acceptance "01:25", pod "created 00:47", DONE "01:45") | commits and files: acceptance 00:50, last executor commit 00:55:31, `executor.done` 00:55:50. Checkpoints were in the bucket at 00:42, before the pod was "created" | **differs:** the log's clock times are wrong by 20–50 min and in places out of order. The ordering that matters holds on commit times: pre-registration `454528da` at 00:23:07 precedes all code and pod work |

Wording against evidence: the run makes no seed-level or "never / wall" claim. "Every pre-registered check passed"
is literally true. It needs the qualifier that the E3 table it passes on contains mislabelled GRPO rows and
cross-run duplicates. Expectations were written before any pod (gate 0: pre-registration commit 00:23:07; first
checkpoint upload 00:42:44), and no miss was hidden. The one deviation (a file per process) is stated with its
reason.

## §Verdict

**Stands.**
- `save_ckpt` uploads before returning, verifies the remote size, writes an md5 sidecar and a row, and raises on a
  missing run id or a failed upload. I re-derived this independently: 5 / 5 downloads match, and all 3 negative
  controls fail as they should.
- The pre-flight check stops training scripts before the first step.
- `record()` is cheap.
- The backfill reproduces the three pre-registered headline numbers exactly.
- No hard constraint was touched: `nd_verify` and `TEST_RUN_DONE` are unchanged, `nd_verify` is not used as a
  judge, no evaluation file is read in training, and the smoke splits are disjoint.

**Must be fixed or reworded before the registry is used as the policy text in `QUESTIONS.md` proposes ("librarians
query it instead of reading prose").**
1. **GRPO rows mislabelled as control (correctness).** In `run4-grpo`, 2,080 rows over 41 GRPO arms carry
   `role=init` and `ckpt=` the Stage-1 init. They measure the GRPO-trained policy, and 260 of them sit in the E3
   control-accuracy answer, with values from 0.573 to 0.917. Fix in `registry_backfill.py`: for GRPO round files,
   set `role=rl` and `ckpt=None`, because the round file does not name the trained checkpoint. Live `grpo.py` is
   already correct.
2. **Checker label by measurement date, not digest date (labelling).** Relabel `run4-grpo` (49,160 rows). Consider
   `nd_verify` (Lean agreement post hoc) for runs before 2026-09-21 instead of `lean+nd_verify`.
3. **Cross-run inheritance and superseded directories (by-run counts).** Tag rows whose source directory belongs
   to another run (lean-format arms under ds-composition / ds-generator / lean-seed2; novelty-campaign arms under
   ds-composition) with `labels.inherited_from`. Tag `dsc_pre_cleanup` rows as superseded, which covers 75
   (arm, round) groups that now carry two values. Until then, "by run" answers double-count.
4. REGISTRY.md: document that the E3 recipe (`role=stage1,init,frozen`) mixes `data/heldout.jsonl`,
   `data/p2/heldout.jsonl` and 240 rows with `data=None`. Document that for EI / GRPO rows `seed` is the driver's
   seed. Document that eval rows carry no `n_params` / format, so a reader must join on `ckpt_md5` to label the
   model.
5. Reword: "32 reviewed runs" → 32 fetched, 31 with rows. The lean-prefilter headline is derivable (a sum of three
   rows). Correct the clock times in `log.md` / STATUS: the actual window is 00:20–00:56 UTC.

**Not supported.** Nothing in the write-up is unsupported beyond the checker-label sentence (item 2), and the
implication that the E3 table is a clean list of control-checkpoint accuracies (item 1).

**Next measurement that settles what is open.**
- After fixing items 1–3, re-run the E3 query and check the result. It should contain no row whose value differs
  across rounds for a fixed (`arm`, `ckpt`, `data`) unless `role=frozen` re-measures it. It should also contain no
  arm under two `run_id`s.
- `review_rr_findings.py` prints both counts: today they are 269 rows and 9 run pairs.
- On a pod with torch, run `tests/test_registry.py --online` to exercise the `save_ckpt` cases that were skipped
  on the VPS in this review.
