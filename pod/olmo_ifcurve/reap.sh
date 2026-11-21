#!/usr/bin/env bash
# reap.sh <pod> <job:rows[:meta]> [...]: VPS-side (olmo-transplant's reaper, run olmo-ifcurve). For each job in order:
# wait for its meta's .done marker on the pod (every 2 min; meta defaults to <job>.json), pull samples / graded / meta /
# logs, check the samples file has <rows> rows and the graded file the same count. After the last job (and only if every
# check passed) pull the pod's env files and logs, then delete the pod. Log ~/runs/olmo-ifcurve/reap_<pod>.log; marker
# ~/runs/olmo-ifcurve/pulled_<job>_<meta> per verified job. Never deletes a pod whose pull or check failed; KEEP=1 never
# deletes it (stage-0 pulls while the queue continues).
N=$1; shift; L=~/runs/olmo-ifcurve/reap_$N.log; W=/home/dan/work/olmo-ifcurve; export POD_LOCAL_ROOT=$W
A=artifacts/olmo_ifcurve; R=/workspace/nd-takehome/$A
log() { echo "$(date -u +%FT%TZ) $*" >> $L; }
ok=1
for s in "$@"; do
  IFS=: read -r J E MT <<< "$s"; MT=${MT:-$J.json}
  until podrun $N "test -f $R/meta/$MT.done" > /dev/null 2>&1; do sleep 120; done
  log "$J ($MT) done on $N"
  for f in samples/$J.jsonl.gz graded/$J.jsonl meta/$MT meta/$MT.done logs/${J}_smi.log; do
    podpull $N $A/$f > /dev/null 2>&1 || log "PULL_FAIL $f"
  done
  ns=$(python3 -c "import gzip
n=0
try:
    for l in gzip.open('$W/$A/samples/$J.jsonl.gz','rt'): n+=1
except Exception: pass
print(n)")
  ng=$(wc -l < $W/$A/graded/$J.jsonl 2>/dev/null || echo 0)
  log "$J samples=$ns graded=$ng expected=$E"
  if [ "$ns" = "$E" ] && [ "$ng" = "$E" ]; then touch ~/runs/olmo-ifcurve/pulled_${J}_${MT%.json}; else ok=0; log "CHECK FAILED $J"; fi
done
for d in logs meta; do podpull $N $A/$d > /dev/null 2>&1 || log "PULL_FAIL $d"; done
if [ "$KEEP" = "1" ]; then log "KEEP=1: $N kept (ok=$ok)"
elif [ $ok = 1 ]; then log "all checks passed; deleting $N"; podrm $N >> $L 2>&1; log "podrm rc=$?"; else log "CHECK FAILED; $N kept"; fi
