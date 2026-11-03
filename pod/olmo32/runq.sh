#!/usr/bin/env bash
# runq.sh <job> ...: run named jobs in order on this pod, downloading the next job's weights while the current one
# samples. Waits until no sampler runs here (a queue can replace another while its job finishes); skips done jobs.
# A rerun of an unfinished job resumes it (sample.py keeps finished chunks).
cd /workspace/nd-takehome; A=artifacts/olmo32; L=$A/logs; mkdir -p $L
T=allenai/Olmo-3.1-32B-Think; D=allenai/Olmo-3-32B-Think-DPO; S0=olmo32/stage0_problems.jsonl
spec() { case $1 in   # "<dir> <repo> <rev>|<command>"
  s0_dpo)  echo "dpo $D main|env PROBLEMS=$S0 bash pod/olmo32/job.sh s0_dpo dpo $D main 8 - 1001 4 0" ;;
  s0_rl)   echo "s2300 $T main|env PROBLEMS=$S0 bash pod/olmo32/job.sh s0_rl s2300 $T main 4 - 1002 4 0" ;;
  F_dpo)   echo "dpo $D main|bash pod/olmo32/job.sh F_dpo dpo $D main 16 - 2001 4 0" ;;
  F_s0100) echo "s0100 $T step_0100|bash pod/olmo32/job.sh F_s0100 s0100 $T step_0100 8 - 2002 4 0" ;;
  F_s0750) echo "s0750 $T step_0750|bash pod/olmo32/job.sh F_s0750 s0750 $T step_0750 8 - 2003 4 0" ;;
  F_s2300) echo "s2300 $T main|bash pod/olmo32/job.sh F_s2300 s2300 $T main 8 - 2004 4 0" ;;
  *) [ -f pod/olmo32/jobs/$1.spec ] && cat pod/olmo32/jobs/$1.spec ;;   # extension jobs: one spec file each
  esac; }
while pgrep -f 'olmo32/[s]ample.py' > /dev/null; do sleep 30; done
JOBS=("$@")
for idx in "${!JOBS[@]}"; do
  J=${JOBS[$idx]}; [ -f $A/meta/$J.done ] && continue
  S=$(spec "$J"); [ -n "$S" ] || { echo "unknown job $J"; continue; }
  NXT=${JOBS[$((idx+1))]:-}
  if [ -n "$NXT" ]; then NS=$(spec "$NXT"); read -r nd nr nv <<< "${NS%%|*}"
    [ -n "$nv" ] && { nohup nice -n 19 bash pod/olmo32/fetch.sh $nr $nv $nd > $L/prefetch_$nd.log 2>&1 < /dev/null & } ; fi
  echo "RUNQ start $J $(date -u +%FT%TZ)"
  bash -c "${S#*|}" > $L/q_$J.log 2>&1
  echo "RUNQ end $J $(date -u +%FT%TZ) $(grep -o 'JOB_DONE.*' $L/q_$J.log)"
done
echo "QUEUE_DONE $(date -u +%FT%TZ)"
