#!/usr/bin/env bash
# Pod 2 (2026-10-13 ~20:00): C2 and C3. Lane C: dose r16 plain x1 (s0-s2), then C3 (old full pend on textbook72);
# lane D: dose r16 guided (s0-s2).
source pod/coep/env.sh
S106=data/coe_paper/strict106.jsonl
laneC() { for S in 0 1 2; do bash pod/coep/read.sh la_dose1_s${S}_r16 $S106 c2_dose1_s${S}_x1 plain 1 512 96; done
  for S in 0 1 2; do bash pod/coep/read.sh stage1_best12_s${S}_b1200 data/coe_paper/tb72.jsonl c3_oldfull_s${S}_pend_tb72 plain 0 512 96; done
  touch artifacts/coe_paper/eval/LANE_C_DONE; }
laneD() { for S in 0 1 2; do bash pod/coep/read.sh la_dose1_s${S}_r16 $S106 c2_dose1_s${S}_g0 guided 0 512 96; done
  touch artifacts/coe_paper/eval/LANE_D_DONE; }
laneC > artifacts/coe_paper/logs/laneC.log 2>&1 &
laneD > artifacts/coe_paper/logs/laneD.log 2>&1 &
wait; up artifacts/coe_paper; echo ALL_DONE $(date -u +%FT%TZ) > artifacts/coe_paper/eval/ALL_DONE_POD2
