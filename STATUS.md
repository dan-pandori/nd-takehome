# STATUS — novelty campaign (branch dan_novelty)

Started 2026-09-15 19:04 UTC. The take-home run's final status is in STATUS_takehome.md.

## Plan
Phase 1 (now): novelty.py log-probs + reachability; coverage.py base-model sampling (transfer k=1e4, val36 k=1e5) on p1; minlen.py on p2. Then Phase 2 (controlled-coverage pretraining, patterns P1-P3, f dial), Phase 3 if time.

## Done
- 19:20 read prior run, wrote Phase 1 plan (log.md)
- 19:40 novelty.py log-probs done (artifacts/novelty_phase1_*.jsonl); minlen labels for val36/transfer/targets; patterns.py tests pass; phase1_analysis.py + figures/phase1_*.png (partial coverage data)

## Running on pods (20:20 UTC)
- p1: coverage.py base transfer k=1e4 shards 0,1 (ETA ~21:35); then Phase-2 EI arms for derived_ore (queue pod/p2jobs/row1_ei_p1.txt)
- p2: coverage shard 2 (slowed by sharing); Phase-2 Stage-1 row 1 (depth3_f0.1, derived_ore_f0, derived_ore_f0.02 x 2 seeds) then EI/frozen depth3 arms (pod/p2jobs/row1_*_p2.txt)
- p3: Phase-2 Stage-1 row 1 (reductio_f0, reductio_f0.1, depth3_f0 x 2 seeds) then EI/frozen reductio arms (pod/p2jobs/row1_*_p3.txt)
- Phase-2 pools built and pulled: data/p2/ (820k-class cap-6 pool on p1; 15 train sets of 155k; targets/transfer per pattern; minlen + intuit labels)

## Next step
- when Stage-1 row 1 finishes: copy depth3_f0 ckpts p3->p2, derived_ore ckpts p2->p1, start p1 EI queue
- when coverage finishes: rerun phase1_analysis.py, write phase1.md; queue base pass@1e4 on pattern targets for f=0 seed-0 models
- rows 2-3 (f=1e-3 x2 seeds; f=1e-4,1e-2 x1 seed): sets exist, push + queue after row 1
