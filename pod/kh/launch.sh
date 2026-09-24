#!/usr/bin/env bash
# VPS side: launch named jobs from pod/kh/jobs.py on a pod (skipped if the log exists). Usage: [AFTER="job ..."] bash pod/kh/launch.sh <pod> <arm> <jobname> [jobname ...]
cd /home/dan/work/cap-horizon
P=$1; ARM=$2; shift 2
for NAME in "$@"; do
cmd=$(python3 pod/kh/jobs.py $ARM | awk -F'\t' -v n="$NAME" '$1==n{print $2}')
[ -n "$cmd" ] || { echo "no job $NAME"; continue; }
pre=""; for m in $AFTER; do pre="${pre}until [ -f artifacts/kh/$m.done ]; do sleep 30; done; "; done
bash pod/kh/w.sh $P sh "[ -f artifacts/kh/logs/$NAME.log ] && { echo already $NAME; exit 0; }; mkdir -p pod/kh/cmds; cat > pod/kh/cmds/$NAME.cmd <<'XEOF'
$pre$cmd
XEOF
setsid nohup bash pod/kh/job.sh $NAME \"\$(cat pod/kh/cmds/$NAME.cmd)\" > /dev/null 2>&1 < /dev/null & disown; sleep 1; echo launched $NAME" < /dev/null 2>&1 | tail -1
done
