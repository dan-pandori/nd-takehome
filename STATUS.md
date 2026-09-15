# STATUS — novelty campaign (branch dan_novelty)

Started 2026-09-15 19:04 UTC. The take-home run's final status is in STATUS_takehome.md.

## Plan
Phase 1 (now): novelty.py log-probs + reachability; coverage.py base-model sampling (transfer k=1e4, val36 k=1e5) on p1; minlen.py on p2. Then Phase 2 (controlled-coverage pretraining, patterns P1-P3, f dial), Phase 3 if time.

## Done
- 19:20 read prior run, wrote Phase 1 plan (log.md)
- 19:40 novelty.py log-probs done (artifacts/novelty_phase1_*.jsonl); minlen labels for val36/transfer/targets; patterns.py tests pass; phase1_analysis.py + figures/phase1_*.png (partial coverage data)

## Running on pods (21:05 UTC)
- p1: coverage shards 0,1 finishing (~21:35); precursor extraction done; next: rows 2-3 Stage-1 (pod/p2jobs/rows23_s1_p1.txt) + derived_ore EI arms (row1_ei_p1.txt)
- p2: Stage-1 derived_ore_f0_s1, f0.02 s0/s1 (~21:15); EI depth3_f0.1 s0/s1 + frozen running (round 1); coverage shard 2 (slow, ~91 min); depth3_f0 ckpts copied from p3
- p3: EI reductio_f0 s0/s1, reductio_f0.1 s0 (round 1 done at 1,330 s/round; 8 rounds ~3 h); frozen + reductio_f0.1_s1 queued
- base pass@1e4 on pattern targets: paused (GPU congestion); rerun on 300 targets per pattern when EI arms finish

## Next step
- 21:35 phase1_analysis.py on full coverage -> finalise phase1.md; copy derived_ore ckpts p2->p1, start p1 EI queue; start rows 2-3 Stage-1 on p1 (reniced)
- Phase 3 prep done: data/p3/textbook_targets.jsonl (623), data/p3/precursors.jsonl (on p1), expert_iter --extra_train
