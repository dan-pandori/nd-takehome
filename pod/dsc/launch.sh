#!/usr/bin/env bash
# VPS side: launch named jobs from pod/dsc/jobs.py on a pod (skipped if the log exists). Usage: [AFTER="job ..."] bash pod/dsc/launch.sh <pod> <arm> <jobname> [jobname ...]
cd /home/dan/work/ds-composition
P=$1; ARM=$2; shift 2
for NAME in "$@"; do
cmd=$(python3 pod/dsc/jobs.py $ARM | awk -F'\t' -v n="$NAME" '$1==n{print $2}')
[ -n "$cmd" ] || { echo "no job $NAME"; continue; }
pre=""; for m in $AFTER; do pre="${pre}until [ -f artifacts/dsc/$m.done ]; do sleep 30; done; "; done   # AFTER="job1 job2": wait for done markers first
bash pod/dsc/w.sh $P sh "[ -f artifacts/dsc/logs/$NAME.log ] && { echo already $NAME; exit 0; }; mkdir -p pod/dsc/cmds; cat > pod/dsc/cmds/$NAME.cmd <<'XEOF'
$pre$cmd
XEOF
setsid nohup bash pod/dsc/job.sh $NAME \"\$(cat pod/dsc/cmds/$NAME.cmd)\" > /dev/null 2>&1 < /dev/null & disown; sleep 1; echo launched $NAME" < /dev/null 2>&1 | tail -1
done
