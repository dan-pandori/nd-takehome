#!/usr/bin/env bash
# Wait for each J9 pod's job marker; pull its J9 chunks and logs; delete the pod. One VPS process.
cd /home/dan/work/capability-defs
W=/workspace/nd-takehome/artifacts/cd
declare -A JOB=([cd-a]=j9_s2b [cd-b]=j9_s0b [cd-d]=j9_s1b [cd-i]=j9_s1a [cd-j]=j9_s2a [cd-k]=j9_s0a)
left=6
while [ $left -gt 0 ]; do
  left=0
  for P in cd-a cd-b cd-d cd-i cd-j cd-k; do
    [ -e /tmp/cdorch/done_$P ] && continue
    left=$((left + 1))
    if timeout 60 podrun $P "test -e $W/${JOB[$P]}.done -o -e $W/${JOB[$P]}.fail" > /dev/null 2>&1; then
      echo "$(date -u +%FT%TZ) $P ${JOB[$P]} finished: $(timeout 60 podrun $P "ls $W | grep ${JOB[$P]}; tail -n 1 $W/logs/${JOB[$P]}.log" 2>&1 | tr '\n' ' ')"
      pod/cd/pull.sh $P 'artifacts/cd/j9/s*_k*.json*' > /dev/null 2>&1
      pod/cd/pull.sh $P artifacts/cd/logs > /dev/null 2>&1
      if ls artifacts/cd/logs/${JOB[$P]}.log > /dev/null 2>&1; then podrm $P 2>&1 | tail -1; touch /tmp/cdorch/done_$P; fi
    fi
  done
  [ $left -gt 0 ] && sleep 60
done
echo "$(date -u +%FT%TZ) all J9 pods finished and deleted"
