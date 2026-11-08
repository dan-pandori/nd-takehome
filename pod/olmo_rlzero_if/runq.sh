#!/usr/bin/env bash
# runq.sh <job> ...: run named jobs in order on this pod, downloading the next job's weights while the current one
# samples. Waits until no sampler runs here (a queue can replace another while its job finishes); skips done jobs.
# A rerun of an unfinished job resumes it (sample.py keeps finished chunks). Job specs: pod/olmo_rlzero_if/jobs/<job>.spec,
# one line "<dir> <repo> <rev>|<command>".
cd /workspace/nd-takehome; A=artifacts/olmo_rlzero_if; L=$A/logs; mkdir -p $L
spec() { [ -f pod/olmo_rlzero_if/jobs/$1.spec ] && cat pod/olmo_rlzero_if/jobs/$1.spec; }
while pgrep -f 'olmo_rlzero_if/[s]ample.py' > /dev/null; do sleep 30; done
JOBS=("$@")
for idx in "${!JOBS[@]}"; do
  J=${JOBS[$idx]}; [ -f $A/meta/$J.done ] && continue
  S=$(spec "$J"); [ -n "$S" ] || { echo "unknown job $J"; continue; }
  NXT=${JOBS[$((idx+1))]:-}
  if [ -n "$NXT" ]; then NS=$(spec "$NXT"); read -r nd nr nv <<< "${NS%%|*}"
    [ -n "$nv" ] && { nohup nice -n 19 bash pod/olmo_rlzero_if/fetch.sh $nr $nv $nd > $L/prefetch_$nd.log 2>&1 < /dev/null & } ; fi
  echo "RUNQ start $J $(date -u +%FT%TZ)"
  bash -c "${S#*|}" > $L/q_$J.log 2>&1
  echo "RUNQ end $J $(date -u +%FT%TZ) $(grep -o 'JOB_DONE.*' $L/q_$J.log)"
done
echo "QUEUE_DONE $(date -u +%FT%TZ)"
