#!/usr/bin/env bash
# VPS side: pull a pod's read summaries, logs, registry rows and ladder files (no found_*.jsonl, no *.pt), and upload
# the pod's final archives to the bucket.  Usage: bash pod/gb/finish.sh <pod>     (podrm separately, after checking)
cd /home/dan/work/grpo-best
P=$1
for d in artifacts/gb/eval artifacts/gb/logs artifacts/grpo-best; do bash pod/gb/pull.sh $P $d >/dev/null 2>&1 || echo "PULL FAILED $P $d"; done
for d in $(podrun $P "cd /workspace/nd-takehome; ls -d artifacts/gb/gb_*" </dev/null); do bash pod/gb/pull.sh $P $d >/dev/null 2>&1 </dev/null || echo "PULL FAILED $P $d"; done
bash pod/gb/push.sh $P >/dev/null 2>&1 </dev/null
podrun $P "cd /workspace/nd-takehome; bash pod/gb/upfound.sh; source pod/gb/env.sh; up artifacts/gb" </dev/null
