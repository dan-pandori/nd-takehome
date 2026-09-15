# STATUS — novelty campaign (branch dan_novelty)

Started 2026-09-15 19:04 UTC. The take-home run's final status is in STATUS_takehome.md.

## Plan
Phase 1 (now): novelty.py log-probs + reachability; coverage.py base-model sampling (transfer k=1e4, val36 k=1e5) on p1; minlen.py on p2. Then Phase 2 (controlled-coverage pretraining, patterns P1-P3, f dial), Phase 3 if time.

## Done
- 19:20 read prior run, wrote Phase 1 plan (log.md)
- 19:40 novelty.py log-probs done (artifacts/novelty_phase1_*.jsonl); minlen labels for val36/transfer/targets; patterns.py tests pass; phase1_analysis.py + figures/phase1_*.png (partial coverage data)

## Running on pods (22:40 UTC)
- p1: row-1 derived_ore: ei f0.02_s1 + frozen f0_s0 + frozen f0.02_s0 (~23:10); coverage shard 1 (~23:10); rows 2-3 Stage-1 done
- p2: row-1 depth3_f0 s0/s1 + frozen (~23:05); row-3 EI arms (reductio/depth3 f1e-4, f1e-2, ...; 3 running, 3 queued); coverage shard 2 (~00:00)
- p3: row-2 EI arms (f=1e-3 x 3 patterns x 2 seeds; 3 running, 3 queued); base pass@1e4 reductio_f0_s0 on 300 targets (~00:30)
- Done: row-1 reductio (5 arms), depth3 f0.1 (2 arms), derived_ore f0/f0.02 s0 (3 arms) -> artifacts/p2/metrics_*_partial.json, numbers.md

## Next step
- as arms finish: pullarm, phase2_metrics, numbers.md; base pass@1e4 (300 targets) for depth3_f0_s0 (p2) and derived_ore_f0_s0 (p1) when their GPUs free
- Phase 3 on p3 after row 2 (pod/p2jobs/phase3_p1.txt, data staged on p3)
- Phase 1: finalise phase1.md when both coverage shards complete
