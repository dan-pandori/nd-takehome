#!/usr/bin/env bash
# worker.sh <gpu>: run the lines of artifacts/olmo_ifladder/queue/q<gpu>.txt in order, one at a time, on GPU <gpu>
# (CUDA_VISIBLE_DEVICES=<gpu>, GPU=<gpu>). Lines are appended from the VPS (`podrun ... "echo '...' >> q0.txt"`); the
# file is re-read for every line, so appending while the worker runs is safe. q<gpu>.state = lines done. A line that
# exits non-zero is logged and skipped. stop<gpu> ends the worker after its current line.
G=$1; cd /workspace/nd-takehome; A=artifacts/olmo_ifladder; Q=$A/queue/q$G.txt; ST=$A/queue/q$G.state; LG=$A/logs/worker$G.log
mkdir -p $A/queue $A/logs; touch $Q; n=$(cat $ST 2>/dev/null || echo 0)
echo "WORKER $G up $(date -u +%FT%TZ) at line $((n+1))" >> $LG
while true; do
  [ -f $A/queue/stop$G ] && { echo "WORKER $G stop $(date -u +%FT%TZ)" >> $LG; exit 0; }
  line=$(sed -n "$((n+1))p" $Q)
  if [ -z "$line" ]; then sleep 20; continue; fi
  echo "LINE_START $G $((n+1)) $(date -u +%FT%TZ) :: $line" >> $LG
  CUDA_VISIBLE_DEVICES=$G GPU=$G bash -c "$line"; rc=$?
  echo "LINE_END $G $((n+1)) rc=$rc $(date -u +%FT%TZ)" >> $LG
  n=$((n+1)); echo $n > $ST
done
