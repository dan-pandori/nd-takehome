#!/usr/bin/env bash
# Launch phase 2: wait for each pod's setup, re-sync code, launch its role. Log artifacts/lo/launch_all.log
cd /home/dan/work/lean-only
declare -A ROLE=([lo-1]=la_seq_s0 [lo-2]=la_free_s0 [lo-3]=la_seq_s1 [lo-4]=la_free_s1 [lo-5]=d3_seq [lo-6]=d3_free)
for n in lo-1 lo-2 lo-3 lo-4 lo-5 lo-6; do
  for i in $(seq 1 30); do
    podrun $n "grep -q SETUP_DONE artifacts/lo/logs/setup.log 2>/dev/null && echo READY" < /dev/null 2>/dev/null | grep -q READY && break
    sleep 20
  done
  echo "$(date -u +%FT%TZ) $n setup ready after $i checks"
  bash pod/lo/sync.sh $n > /dev/null 2>&1 < /dev/null
  bash pod/lo/sync.sh $n push data/lo > /dev/null 2>&1 < /dev/null
  bash pod/lo/launch.sh $n ${ROLE[$n]} < /dev/null 2>&1 | grep -v "^Warning"
  echo "$(date -u +%FT%TZ) $n launched ${ROLE[$n]}"
done
echo LAUNCH_ALL_DONE
