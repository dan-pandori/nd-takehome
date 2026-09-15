# STATUS — novelty campaign (branch dan_novelty)

Started 2026-09-15 19:04 UTC. The take-home run's final status is in STATUS_takehome.md.

## Plan
Phase 1 (now): novelty.py log-probs + reachability; coverage.py base-model sampling (transfer k=1e4, val36 k=1e5) on p1; minlen.py on p2. Then Phase 2 (controlled-coverage pretraining, patterns P1-P3, f dial), Phase 3 if time.

## Done
- 19:20 read prior run, wrote Phase 1 plan (log.md)
- 19:40 novelty.py log-probs done (artifacts/novelty_phase1_*.jsonl); minlen labels for val36/transfer/targets; patterns.py tests pass; phase1_analysis.py + figures/phase1_*.png (partial coverage data)

## Running on pods (23:15 UTC)
- p1: Phase 3 (ei_textbook, ei_textbook_precursor, frozen_textbook; 8 rounds); base pass@1e4 derived_ore_f0_s0 (300 targets, ~13 min)
- p2: row-3 EI arms (3 running, 3 queued); base pass@1e4 depth3_f0_s0 (300 targets); novelty of depth3 f=0 arms; coverage shard 2 (~00:40)
- p3: row-2 EI arms (depth3_f0.001_s1, derived_ore_f0.001 s0/s1); base pass@1e4 reductio_f0_s0 (300 targets, ~01:00)
- Row 1 COMPLETE (18 arms) + row-2 reductio/depth3 s0: metrics in artifacts/p2/metrics_*_partial.json; HEADLINE: depth3 acquisition at f=0 is 0.34/0.27 (frozen 0), reductio 0/0, derived_ore 0.009/0.002 (degenerate form only)

## Next step
- finish rows 2-3 (~00:30), base pass@1e4 + novelty for f=0 arms, phase2_figure.py, write phase2.md
- Phase 3 results (~01:30): val36 per round (eval_val36_rounds.sh on p1), phase3.md
- Phase 1: final phase1_analysis.py when shard 2 completes (~00:40); campaign.md last
