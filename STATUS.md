# STATUS — novelty campaign (branch dan_novelty)

Started 2026-09-15 19:04 UTC. The take-home run's final status is in STATUS_takehome.md.

## Plan
Phase 1 (now): novelty.py log-probs + reachability; coverage.py base-model sampling (transfer k=1e4, val36 k=1e5) on p1; minlen.py on p2. Then Phase 2 (controlled-coverage pretraining, patterns P1-P3, f dial), Phase 3 if time.

## Done
- 19:20 read prior run, wrote Phase 1 plan (log.md)
- 19:40 novelty.py log-probs done (artifacts/novelty_phase1_*.jsonl); minlen labels for val36/transfer/targets; patterns.py tests pass; phase1_analysis.py + figures/phase1_*.png (partial coverage data)

## Running on pods
- p1: coverage.py base transfer k=1e4 shards 0,1 (ETA ~21:00 UTC); make_coverage_sets.py gen (Phase 2 pools, CPU)
- p2: coverage.py val36 k=1e5 then transfer shard 2
- p3: created 19:35, idle until Phase 2 pools exist

## Next step
- assemble Phase 2 sets (make_coverage_sets.py assemble/targets), minlen-label long pool, start Stage-1 row 1 on p3
- when coverage finishes: rerun phase1_analysis.py, write phase1.md
