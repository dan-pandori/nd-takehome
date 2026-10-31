#!/usr/bin/env bash
# Insurance against a dead pod: after every 4th round, sync the ladder dir (found / found_transfer / alloc / round files of
# that round are complete once round_<r>.json exists) to the coe-dose01 bucket folder, so a new pod can --resume from it.
# Usage: setsid nohup bash pod/d01/backup.sh <ladder name, e.g. la_dose01_s0> <last round> > artifacts/coe/logs/backup_<name>.log 2>&1 &
# (hf buckets sync: --include alone restricts the upload; adding --exclude '*' excludes everything — dry-run, 2026-10-31)
source pod/d01/env.sh
L=artifacts/coe/ladder/$1; END=$2; done_r=0
while [ "$done_r" -lt "$END" ]; do
  last=$(ls $L/round_*.json 2>/dev/null | sed 's/.*round_//; s/.json//' | sort -n | tail -1)
  if [ -n "$last" ] && [ "$last" -gt "$done_r" ] && [ $((last % 4)) = 0 ]; then
    up $L --include "found_$last.jsonl" --include "found_transfer_$last.jsonl" --include 'round_*.json' --include 'alloc_*.json' --include 'args*.json'
    echo "$(date -u +%FT%TZ) backed up $L at r$last"; done_r=$last
  fi
  sleep 300
done
