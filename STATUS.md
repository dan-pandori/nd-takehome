# STATUS — novelty campaign (branch dan_novelty)

Started 2026-09-15 19:04 UTC. The take-home run's final status is in STATUS_takehome.md.

## Plan
Phase 1 (now): novelty.py log-probs + reachability; coverage.py base-model sampling (transfer k=1e4, val36 k=1e5) on p1; minlen.py on p2. Then Phase 2 (controlled-coverage pretraining, patterns P1-P3, f dial), Phase 3 if time.

## Done
- 19:20 read prior run, wrote Phase 1 plan (log.md)
- 19:40 novelty.py log-probs done (artifacts/novelty_phase1_*.jsonl); minlen labels for val36/transfer/targets; patterns.py tests pass; phase1_analysis.py + figures/phase1_*.png (partial coverage data)

## Running on pods (23:55 UTC)
- p1: Phase 3 EI arms (ei_textbook, ei_textbook_precursor) round 4/8; frozen_textbook done
- p2: last row-3 arms (depth3 f1e-2, derived_ore f1e-4, derived_ore f1e-2) rounds 5-6/8
- p3: base pass@1e4 depth3_f0_s0 (300 targets, ~00:30)
- DONE: Phase 1 coverage (all 1,638 transfer theorems + val36) -> phase1.md final; Phase 2 rows 1-2 + 3 of 6 row-3 arms -> phase2.md draft, figures/phase2_acquisition.png

## Next step
- 00:15 pull last row-3 arms -> metrics, figure, phase2.md final
- 00:30 depth3 base pass@1e4 -> phase2.md table
- Phase 3: eval_val36_rounds.sh on both EI arms; novelty of newly solved validation theorems; phase3.md; then campaign.md; delete pods
