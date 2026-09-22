#!/usr/bin/env bash
# VPS side: launch every job of a role on a pod, one podrun call per job (jobs already started on the pod are skipped).
# Usage: bash pod/lo/launch.sh <pod> <role>
cd /home/dan/work/lean-only
bash pod/lo/sync.sh $1 push pod/lo/job.sh > /dev/null < /dev/null
mapfile -t LINES < <(python3 pod/lo/jobs.py $2)
for line in "${LINES[@]}"; do
  name="${line%%$'\t'*}"; cmd="${line#*$'\t'}"
  podrun $1 "[ -f artifacts/lo/logs/$name.log ] && { echo already $name; exit 0; }; mkdir -p pod/lo/cmds; cat > pod/lo/cmds/$name.cmd <<'XEOF'
$cmd
XEOF
setsid nohup bash pod/lo/job.sh $name \"\$(cat pod/lo/cmds/$name.cmd)\" > /dev/null 2>&1 < /dev/null & disown; sleep 1; echo launched $name" < /dev/null 2>&1 | tail -1
done
