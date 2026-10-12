#!/usr/bin/env bash
# coe-r1: after the two round-1 replicas, the Phase 2 power-sampling pilot (development data only).
source pod/coe/env.sh
until [ -s artifacts/coe/replica/rep_best12_s1/round_1.json ]; do sleep 30; done
while pgrep -f 'state_ladder_ei.p[y]' > /dev/null; do sleep 15; done
bash pod/coe/power_pilot.sh > artifacts/coe/logs/power_pilot.log 2>&1
up artifacts/create-or-elicit/registry
echo R1_NEXT_DONE
