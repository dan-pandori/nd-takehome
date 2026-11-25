#!/usr/bin/env bash
# run_jobs.sh <job,job,...> <inflight> <disk_cap_gb>: run engine.py on each job in turn (downloads to the container disk
# /root/dl, GPU cache on). A job is retried up to 2 times (the engine resumes at shard granularity). Writes
# stats/<job>/JOB_DONE on success and logs/<job>.log; logs/queue_<host>.done when the list is finished.
cd /workspace/nd-takehome; A=artifacts/olmo_weights; mkdir -p $A/logs $A/stats
export HF_XET_HIGH_PERFORMANCE=1 HF_XET_CHUNK_CACHE_SIZE_BYTES=0
for J in $(echo "$1" | tr ',' ' '); do
  for try in 1 2 3; do
    date -u +"%FT%TZ start $J try $try" >> $A/logs/$J.log
    python olmo_weights/engine.py --job $J --work /root/dl --device cuda --inflight $2 --disk-cap-gb $3 --lora-dir /workspace/nd-takehome/lora >> $A/logs/$J.log 2>&1
    rc=$?
    n=$(python -c "import json; print(len(json.load(open('olmo_weights/manifest/jobs.json'))['$J']['members']) and len(__import__('glob').glob('$A/stats/$J/shard_*/DONE')))")
    date -u +"%FT%TZ end $J try $try rc $rc shards_done $n" >> $A/logs/$J.log
    [ $rc = 0 ] && { date -u +%FT%TZ > $A/stats/$J/JOB_DONE; break; }
    sleep 60
  done
done
date -u +%FT%TZ > $A/logs/queue_$(hostname).done
