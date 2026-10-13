#!/usr/bin/env bash
# If every given marker exists on the pod: pull its results, upload them from the pod, delete the pod.
# Usage: pod/coe/reap.sh <pod> <ladder dir name or -> <marker> [marker ...]
cd /home/dan/work/create-or-elicit
P=$1; L=$2; shift 2
[ -f ~/.config/nd-rl/pods/$P ] || { echo "$P: gone"; exit 0; }
for m in "$@"; do
  timeout 25 podrun $P "test -e /workspace/nd-takehome/artifacts/coe/markers/$m" > /dev/null 2>&1 || { echo "$P: waiting for $m"; exit 0; }
done
for d in artifacts/coe/eval artifacts/coe/large artifacts/coe/budget artifacts/coe/timing artifacts/coe/score artifacts/coe/rounds \
         artifacts/coe/p3a artifacts/create-or-elicit artifacts/coe/logs artifacts/coe/markers; do
  pod/coe/pull.sh $P $d > /dev/null 2>&1
done
[ "$L" != - ] && pod/coe/pull.sh $P artifacts/coe/ladder/$L > /dev/null 2>&1
timeout 900 podrun $P "cd /workspace/nd-takehome; source pod/coe/env.sh > /dev/null 2>&1; for d in artifacts/coe/eval artifacts/coe/large artifacts/coe/budget artifacts/coe/timing artifacts/coe/score artifacts/coe/rounds artifacts/coe/p3a artifacts/coe/logs artifacts/create-or-elicit; do [ -d \$d ] && up \$d; done; [ $L != - ] && up artifacts/coe/ladder/$L; hf buckets sync artifacts/coe/dump \$BK/create-or-elicit/artifacts/coe/dump --include '*.gz' > /dev/null 2>&1; echo uploaded" 2>&1 | tail -1
podrm $P 2>&1 | tail -1
