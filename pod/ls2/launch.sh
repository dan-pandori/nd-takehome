#!/usr/bin/env bash
# VPS side: launch every job of a role on a pod, one podrun call per job (jobs already started on the pod are skipped). Usage: bash pod/ls2/launch.sh <pod> <a|b>
cd /home/dan/work/lean-seed2
bash pod/ls2/sync.sh $1 push pod/lf/job.sh > /dev/null < /dev/null
mapfile -t LINES < <(python3 pod/ls2/jobs.py $2)
for line in "${LINES[@]}"; do
  name="${line%%$'\t'*}"; cmd="${line#*$'\t'}"
  podrun $1 "[ -f artifacts/lf/logs/$name.log ] && { echo already $name; exit 0; }; mkdir -p pod/lf/cmds; cat > pod/lf/cmds/$name.cmd <<'XEOF'
$cmd
XEOF
setsid nohup bash pod/lf/job.sh $name \"\$(cat pod/lf/cmds/$name.cmd)\" > /dev/null 2>&1 < /dev/null & disown; sleep 1; echo launched $name" < /dev/null 2>&1 | tail -1
done
