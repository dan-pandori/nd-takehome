#!/usr/bin/env bash
# pod D (replaces queue_d3 after its J6b s0 child started): J6b s1, s2 after s0 finishes, then J2 stage A' / B for seed 0 only.
. pod/cd/env.sh
until grep -q "J6b s0 done" artifacts/cd/logs/j6b_s0.log 2>/dev/null; do sleep 60; done
for S in 1 2; do bash pod/cd/j6b.sh $S > artifacts/cd/logs/j6b_s$S.log 2>&1; done
bash pod/cd/j2b.sh 0 > artifacts/cd/logs/j2b_s0.log 2>&1
echo "$(date -u +%FT%TZ) QUEUE_D4_DONE"
