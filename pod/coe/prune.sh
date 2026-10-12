#!/usr/bin/env bash
# Keep the pod's 20 GB disk safe during 16-round ladders: found_<r>.jsonl / found_transfer_<r>.jsonl are cumulative (each
# proof carries its round), so only the last two rounds' copies are kept; mix_<r>.jsonl of finished rounds are gzipped.
# Usage: setsid nohup bash pod/coe/prune.sh > artifacts/coe/logs/prune.log 2>&1 &
cd /workspace/nd-takehome
while true; do
  for d in artifacts/coe/ladder/la_*; do
    [ -d "$d" ] || continue
    last=$(ls $d/round_*.json 2>/dev/null | sed 's/.*round_//; s/.json//' | sort -n | tail -1)
    [ -n "$last" ] || continue
    for f in $d/found_*.jsonl $d/found_transfer_*.jsonl; do
      [ -e "$f" ] || continue
      r=$(basename $f .jsonl | sed 's/.*_//')
      [ "$r" -lt $((last-1)) ] 2>/dev/null && rm -f "$f" && echo "$(date -u +%FT%TZ) rm $f"
    done
    for f in $d/mix_*.jsonl; do
      [ -e "$f" ] || continue
      r=$(basename $f .jsonl | sed 's/.*_//')
      [ "$r" -le "$last" ] 2>/dev/null && gzip -f "$f" && echo "$(date -u +%FT%TZ) gz $f"
    done
  done
  df -h / | tail -1 | awk -v t="$(date -u +%FT%TZ)" '{print t, "disk", $5, $4}'
  sleep 600
done
