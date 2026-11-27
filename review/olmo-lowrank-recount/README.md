# Reviewer kit: olmo-lowrank (reviewer session, 2026-11-27)

My own code; no executor module is imported. Raw inputs are read from the phase-1 workspace `~/review/olmo-lowrank`
(hard links into the run worktree, read only). Scratch: `~/review/olr_rv` (upstream checkers, tokenizer files, item
texts). `out/answers_scope.json.gz` (answer texts) is not committed; `rvr_screen.py` rebuilds it from the samples.

- `rvr_core.py`, `rvr_graders.py`, `rvr_regrade.py`, `rvr_gradecmp.py`: re-grade of all 11 jobs with the upstream
  IFBench / IFEval checkers, row-by-row comparison (`out/regrade/`, `out/gradecmp.*`).
- `rvr_provenance.py`: prompt token ids rebuilt from my template rendering; decoding settings; endpoint file hashes.
- `rvr_plan.py`, `pod/rvr_pod.py`, `pod/rvr_job.sh`: seeded raw-weight recompute on an A100 (plan, self-test, fetch with
  sha256 checks, float64 QR + SVD spectra, my bf16 floors, LoRA overlaps, adapter truncation checks) -> `pod_out/`.
- `rvr_spectra_cmp.py`: my recompute against the stored spectra; `rvr_part1.py`: Part-1 aggregates and expectations over
  every matrix from the validated stored spectra (`out/part1.*`, `out/tables_md.txt`, `out/spike_energy.json`).
- `rvr_scope.py`, `rvr_screen.py`, `rvr_items.py`, `rvr_hand.py`, `rvr_adjudicate.py`, `hand/`: my blind hand gate (scope,
  mechanical rule-1 screen, items, batches, reader labels in `hand/labels/`, adjudications in `hand/adjud/`,
  `hand/POLICY.md`, accepted confirmations in `hand/confirm.json`).
- `rvr_readings.py`, `rvr_execlabels.py`: G, bootstrap intervals, readings, label sensitivity (`out/readings*`,
  `out/cells_mine.csv`); `rvr_agree.py`: agreement with the executor's and olmo-ifcurve's labels.
- `rvr_compute.py`: compute and cost from the job logs and `~/podhours.log`.
