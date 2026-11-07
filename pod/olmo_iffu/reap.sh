#!/usr/bin/env bash
# reap.sh <pod> <job> <expected_rows> [more jobs as job:rows ...]: VPS-side. Waits for meta/<job>.done on the pod (every
# 2 min), pulls that job's files one by one into the worktree, checks the samples file has the expected rows and the
# graded file the same count, then (only if every check passed) pulls the pod's logs / env files and deletes the pod.
# Writes ~/runs/olmo-iffu/reap_<pod>.log; never deletes a pod whose pull failed.
N=$1; shift; L=~/runs/olmo-iffu/reap_$N.log; W=/home/dan/work/olmo-iffu; export POD_LOCAL_ROOT=$W
SPEC=("$@")
log() { echo "$(date -u +%FT%TZ) $*" >> $L; }
for s in "${SPEC[@]}"; do
  J=${s%%:*}
  until podrun $N "test -f /workspace/nd-takehome/artifacts/olmo_iffu/meta/$J.done" > /dev/null 2>&1; do sleep 120; done
  log "$J done on $N"
done
ok=1
for s in "${SPEC[@]}"; do
  J=${s%%:*}; R=${s##*:}
  for f in samples/$J.jsonl.gz graded/$J.jsonl meta/$J.json meta/$J.done logs/q_$J.log logs/${J}_smi.log; do
    podpull $N artifacts/olmo_iffu/$f > /dev/null 2>&1 || { log "PULL_FAIL $f"; ok=0; }
  done
  podrun $N "test -f /workspace/nd-takehome/artifacts/olmo_iffu/graded/${J}_trunc32k.jsonl" > /dev/null 2>&1 && \
    { podpull $N artifacts/olmo_iffu/graded/${J}_trunc32k.jsonl > /dev/null 2>&1 || { log "PULL_FAIL trunc $J"; ok=0; }; }
  ns=$(python3 -c "import gzip,sys
n=0
try:
    for l in gzip.open('$W/artifacts/olmo_iffu/samples/$J.jsonl.gz','rt'): n+=1
except Exception: pass
print(n)")
  ng=$(wc -l < $W/artifacts/olmo_iffu/graded/$J.jsonl 2>/dev/null || echo 0)
  log "$J samples=$ns graded=$ng expected=$R"
  [ "$ns" = "$R" ] && [ "$ng" = "$R" ] || { [ "$R" = "-" ] && [ "$ns" = "$ng" ] && [ "$ns" -gt 0 ]; } || ok=0
done
for f in logs/queue1.log logs/queue2.log logs/setup.log; do podpull $N artifacts/olmo_iffu/$f > /dev/null 2>&1; done
podrun $N "ls /workspace/nd-takehome/artifacts/olmo_iffu/meta/" 2>/dev/null | grep -E 'pod_env|pip_freeze' | while read f; do podpull $N artifacts/olmo_iffu/meta/$f > /dev/null 2>&1; done
if [ $ok = 1 ]; then log "all checks passed; deleting $N"; podrm $N >> $L 2>&1; log "podrm rc=$?"; else log "CHECK FAILED; $N kept"; fi
