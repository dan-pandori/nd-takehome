#!/usr/bin/env bash
# VPS side: launch every chain assigned to a pod, one podrun call per chain, under setsid/nohup.
# A chain is a shell line of `bash pod/sd/job.sh <name> '<cmd>'` calls run in sequence.
#   bash pod/sd/launch.sh <pod-name> <chain-id> [<chain-id> ...]
cd /home/dan/work/stage1-dynamics
P=$1; shift
bash pod/sd/sync.sh $P push pod/sd/job.sh > /dev/null < /dev/null
for cid in "$@"; do
  mapfile -t LINES < <(python3 pod/sd/jobs.py chain $cid)
  SCRIPT="cd /workspace/nd-takehome"$'\n'
  for line in "${LINES[@]}"; do
    IFS=$'\t' read -r name cmd <<< "$line"
    SCRIPT+="[ -f artifacts/sd/$name.done ] || bash pod/sd/job.sh $name '$cmd'"$'\n'
  done
  SCRIPT+="touch artifacts/sd/chain_$cid.done"$'\n'
  podrun $P "mkdir -p pod/sd/chains artifacts/sd/logs; cat > pod/sd/chains/$cid.sh <<'XEOF'
$SCRIPT
XEOF
setsid nohup bash pod/sd/chains/$cid.sh > artifacts/sd/logs/chain_$cid.out 2>&1 < /dev/null & disown; sleep 1; echo launched chain $cid" < /dev/null 2>&1 | tail -1
done
