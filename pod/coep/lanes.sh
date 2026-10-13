#!/usr/bin/env bash
# Two lanes on one A40 (each read ~8 GB at batch 512). Lane A: C1 on the knockout r16 seeds. Lane B: C1 on dose / full s4,
# then C2 (dose r16 x1 + guided), then C3 (old full pend on textbook72). Usage: bash pod/coep/lanes.sh
source pod/coep/env.sh
S106=data/coe_paper/strict106.jsonl
laneA() {
  for S in 0 1 2 3 4 5; do
    bash pod/coep/read.sh la_ko_s${S}_r16 $S106 c1_ko_s${S}_std plain 0 512 96
    bash pod/coep/read.sh la_ko_s${S}_r16 $S106 c1_ko_s${S}_dbl plain 0 1024 192
  done
  touch artifacts/coe_paper/eval/LANE_A_DONE
}
laneB() {
  for C in dose1_s2 dose1_s0 dose1_s1 full_s4; do
    bash pod/coep/read.sh la_${C}_r16 $S106 c1_${C}_std plain 0 512 96
    bash pod/coep/read.sh la_${C}_r16 $S106 c1_${C}_dbl plain 0 1024 192
  done
  for S in 0 1 2; do
    bash pod/coep/read.sh la_dose1_s${S}_r16 $S106 c2_dose1_s${S}_x1 plain 1 512 96
    bash pod/coep/read.sh la_dose1_s${S}_r16 $S106 c2_dose1_s${S}_g0 guided 0 512 96
  done
  for S in 0 1 2; do
    bash pod/coep/read.sh stage1_best12_s${S}_b1200 data/coe_paper/tb72.jsonl c3_oldfull_s${S}_pend_tb72 plain 0 512 96
  done
  touch artifacts/coe_paper/eval/LANE_B_DONE
}
laneA > artifacts/coe_paper/logs/laneA.log 2>&1 &
laneB > artifacts/coe_paper/logs/laneB.log 2>&1 &
wait
up artifacts/coe_paper
echo ALL_DONE $(date -u +%FT%TZ) > artifacts/coe_paper/eval/ALL_DONE
