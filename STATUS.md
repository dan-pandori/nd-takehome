# STATUS — lean-format (proposal 8)

Brief: BRIEF_LEAN_FORMAT.md. Policy: AGENT_POLICY.md. Run id: lean-format. Only exception to the pause.

## lean-format
- 2026-09-21 02:52 UTC  run started (executor). 03:00 pre-registration committed (`preregistration/lean-format.md`, c2dcd0a) before any pod. Lean token format fixed in `lean_tok.py` (two naming schemes: `lean_rand` primary, `lean_seq`).
- 2026-09-21 03:04–08:03 UTC  four RTX 3090 pods (lf-1 … lf-4), all deleted; ≈ $6.2 of the $30 budget. 16 Lean-format arms + 7 Stage-1 models + solo timing rounds + checker of record.
- Result: `lean_seq` **not worse on all three** (held-out 0.909 / 0.896 / 0.936 vs token 0.883 / 0.883 / 0.948; depth-3 acquisition 0.476 / 0.479 vs 0.335 / 0.364; ladder transfer L* 11 / 11 vs 10 / 10). `lean_rand` (pre-registered primary): worse in distribution (0.882 / 0.790 / 0.830), better on depth-3 (0.433 / 0.462), equal L* (10 / 10). Frozen Lean base models already write depth-3 proofs (0.13–0.28 vs 0.005) and have L* 9–10 (token 7). Lean vs nd_verify: 0 disagreements on 41,840 counted proofs; 460 "Lean-only" acceptances among 13.9 M sampled (nd2lean's BOTE rendering is loose — see QUESTIONS.md).
- Deliverables: `run_lean_format.md`, `numbers.md` § lean-format, `log.md` § lean-format, `figures/lean_format.png`, bucket `hf://buckets/dan-pandori/nd-rl/lean-format/`. Two questions for Dan in `QUESTIONS.md` (2026-09-21).

LEAN-FORMAT DONE 2026-09-21T08:10:42Z

# STATUS — ds-composition (proposal 9, run 1)

Brief: BRIEF_ds-composition.md. Policy: AGENT_POLICY.md. Run id: ds-composition (pause lifted for this theme by Dan's brief). Sibling `ds-generator` on the same host (pods `dsg-*` are not mine; mine are `dsc-*`).

## ds-composition
- 2026-09-22 05:54 UTC  run started (executor). Pre-registration `preregistration/ds-composition.md` committed ≈ 06:12 before any `dsc-*` pod. Sets built on the VPS (`dsc_assemble.py`, streaming); A2 needs an ORE top-up from the unchanged generator (output filter only; disclosed).
- 2026-09-23 21:00 UTC  **Session 2 (resume).** Pre-registration amendment 3 committed 21:15 (b836eef) before any new pod: the 2026-09-22 host cleanup deleted `artifacts/`+`ckpts/` (committed round files restored from git into `artifacts/dsc_pre_cleanup/`; all checkpoints and proof-level files lost), so every number is re-measured from the surviving sets in `data/dsc/`. Code brought up to date with the runs that finished meanwhile: `sample.py`/`model.py` ← `dan_efficiency` (fast decode path, checked 64/64 identical greedy on the pod, 1.6× on sampled batches), `nd2lean.py` ← `dan_lean_seed2`'s BOTE fix; `lean_tok.py` unchanged (the control's checkpoints may not be retrained). Five pods 21:12–21:22 — **A40 $0.49/h** (`dsc-c0`, `dsc-a1`, `dsc-a3`) and **RTX A6000 $0.53/h** (`dsc-a2`, `dsc-a4`): no RTX 3090 is in stock on the account. Budget $18, ceiling 36 pod-hours; balance $220.36.
- 2026-09-24 04:20 UTC  Five arms complete on re-measured Stage-1 models (the first session's checkpoints were lost to the host cleanup). **The histogram is a lever in distribution** (A1 6-line no-pattern +7.3 / +6.5 pp on both seeds, above the cap-8 yardstick) **but the cap still sets the horizon** (frozen ladder transfer solves C0 158 / A1 205 / A4 156 vs cap-8 976; only cap 8 writes an accepted ≥ 8-line reductio proof, 29 / 33 vs 0). Finding 2's rule-mix account stands (A2 moved one schema, not two). Finding 3 gets no counter-example: EI round-4 acquisition lands at 0.38–0.44 in every cap-6 arm whatever base rate it starts from. **No arm replaces the control** (A1's required-reductio pass@2,000 is worse on both seeds). Lean ∧ `nd_verify` on 124,952 counted proofs: 0 disagreements. 25.70 pod-hours, $12.84 of $18; all five pods deleted. Deliverables: `run_ds_composition.md`, `numbers.md` § ds-composition, `figures/dsc_*.png`, `data/dsc/README.md`, bucket `hf://buckets/dan-pandori/nd-rl/ds-composition/`.

DS-COMPOSITION DONE 2026-09-24T04:20:00Z

# STATUS — cap-horizon (proposal 11, run 1)

Brief: the run brief in the executor prompt. Policy: AGENT_POLICY.md. Run id: cap-horizon. Sibling `noise-floor` on the same host (pods `nf-*` are not mine; mine are `kh-*`).

## cap-horizon
- 2026-09-24 16:07 UTC  run started (executor). Pre-registration `preregistration/cap-horizon.md` committed **2091f78 16:07:35Z, before any pod** (gate 0). Budget $22 / 44 pod-hours already registered; RunPod balance $177.81. Question: does raising the training cap move the proof-length horizon, and does it keep moving? Arms: **K6** (cap 6, inherited = `ds-composition` C0), **K8flat** (cap 8, inherited = A3), and four new — **K8add** (cap 8, 217,000: C0's exact bins plus 31,000 each at lengths 7 and 8), **K10**, **K12**, **K14** (flat 155,000 over lengths 2–cap). Deviation from the brief, with reason, in the pre-registration: K14 is run as a fourth arm from the start instead of seed-1 ladders, because the question is monotone-walk-vs-plateau and the sibling `noise-floor` run measures the error bar at n = 4 × 2.
- Two measurement ceilings pre-registered before the run: `L*` is **hard-censored at 14** by `data/ladder/transfer.jsonl` (only 23 theorems at `L_true` ≥ 13, 10 at ≥ 14), which truncates the brief's own expectation bands; and coverage's `max_new` = 400 clips the longest proofs. Both are reported with every affected number.
