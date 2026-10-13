#!/usr/bin/env bash
# Pod 1 after the split (2026-10-13 ~20:00): C1 only. Lane A: knockout r16 s0-s5; lane B: dose r16 s2/s0/s1 + full s4.
# read.sh skips any read whose summary already exists, so finished reads are not redone.
source pod/coep/env.sh
S106=data/coe_paper/strict106.jsonl
laneA() { for S in 0 1 2 3 4 5; do
  bash pod/coep/read.sh la_ko_s${S}_r16 $S106 c1_ko_s${S}_std plain 0 512 96
  bash pod/coep/read.sh la_ko_s${S}_r16 $S106 c1_ko_s${S}_dbl plain 0 1024 192; done; touch artifacts/coe_paper/eval/LANE_A_DONE; }
laneB() { for C in dose1_s2 dose1_s0 dose1_s1 full_s4; do
  bash pod/coep/read.sh la_${C}_r16 $S106 c1_${C}_std plain 0 512 96
  bash pod/coep/read.sh la_${C}_r16 $S106 c1_${C}_dbl plain 0 1024 192; done; touch artifacts/coe_paper/eval/LANE_B_DONE; }
laneA > artifacts/coe_paper/logs/laneA.log 2>&1 &
laneB > artifacts/coe_paper/logs/laneB.log 2>&1 &
wait; up artifacts/coe_paper; echo ALL_DONE $(date -u +%FT%TZ) > artifacts/coe_paper/eval/ALL_DONE_POD1
