#!/usr/bin/env bash
# reap.sh <pod> <job:rows> [<job:rows> ...]: VPS-side (olmo-iffu's reaper, run olmo-transplant). For each job in order:
# wait for meta/<job>.done on the pod (every 2 min), pull its files into the worktree at once, check the samples file
# has the expected rows and the graded file the same count. After the last job (and only if every check passed) pull
# the pod's logs / env files and delete the pod. Writes ~/runs/olmo-transplant/reap_<pod>.log and a marker
# ~/runs/olmo-transplant/pulled_<job> per verified job; never deletes a pod whose pull or check failed.
N=$1; shift; L=~/runs/olmo-transplant/reap_$N.log; W=/home/dan/work/olmo-transplant; export POD_LOCAL_ROOT=$W
R=/workspace/nd-takehome/artifacts/olmo_transplant
log() { echo "$(date -u +%FT%TZ) $*" >> $L; }
ok=1
for s in "$@"; do
  J=${s%%:*}; E=${s##*:}
  until podrun $N "test -f $R/meta/$J.done" > /dev/null 2>&1; do sleep 120; done
  log "$J done on $N"
  for f in samples/$J.jsonl.gz graded/$J.jsonl meta/$J.json meta/$J.done meta/${J}_boundary.txt logs/q_$J.log logs/${J}_smi.log; do
    podpull $N artifacts/olmo_transplant/$f > /dev/null 2>&1 || log "PULL_FAIL $f (may not exist for this job)"
  done
  ns=$(python3 -c "import gzip
n=0
try:
    for l in gzip.open('$W/artifacts/olmo_transplant/samples/$J.jsonl.gz','rt'): n+=1
except Exception: pass
print(n)")
  ng=$(wc -l < $W/artifacts/olmo_transplant/graded/$J.jsonl 2>/dev/null || echo 0)
  log "$J samples=$ns graded=$ng expected=$E"
  if [ "$ns" = "$E" ] && [ "$ng" = "$E" ]; then touch ~/runs/olmo-transplant/pulled_$J; else ok=0; log "CHECK FAILED $J"; fi
done
podrun $N "ls $R/logs/ $R/meta/" 2>/dev/null | grep -E '\.log$|pod_env|pip_freeze' | while read f; do
  case $f in *.log) d=logs;; *) d=meta;; esac; podpull $N artifacts/olmo_transplant/$d/$f > /dev/null 2>&1; done
if [ $ok = 1 ]; then log "all checks passed; deleting $N"; podrm $N >> $L 2>&1; log "podrm rc=$?"; else log "CHECK FAILED; $N kept"; fi
