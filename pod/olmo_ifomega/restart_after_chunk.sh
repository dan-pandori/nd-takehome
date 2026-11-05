#!/usr/bin/env bash
# restart_after_chunk.sh <job> <tag>: wait until the running sequential job <job> writes its next chunk, then stop it
# (runq, job.sh, sampler, any engine process left on the GPU) and restart it through runq.sh from its spec. The restart
# resumes from the samples file (finished chunks kept, in-flight ones redrawn), so stopping right after a chunk lands
# loses the least work. Used to apply a changed spec (e.g. a --stop_file) to a running job. Logs: logs/restart_<tag>.log,
# the old job log kept as logs/q_<job>.<tag>.log, the new queue log logs/runq_<tag>.log.
J=$1; T=$2
cd /workspace/nd-takehome; A=artifacts/olmo_ifomega; L=$A/logs
rows() { grep -o 'samples=[0-9]*' $L/q_$J.log | tail -1 | cut -d= -f2; }
n0=$(rows); echo "$(date -u +%T) waiting for $J to pass samples=$n0"
while [ "$(rows)" = "$n0" ]; do sleep 15; done
echo "$(date -u +%T) $J at samples=$(rows): stopping"
pkill -f "runq.sh ${J:0:1}[${J:1:1}]${J:2}"
pkill -f "job.sh ${J:0:1}[${J:1:1}]${J:2}"
pkill -f "olmo_ifomega/[s]ample.py.*--job $J"
for k in $(seq 1 24); do
  pgrep -f 'olmo_ifomega/[s]ample.py' > /dev/null || break; sleep 5
done
sleep 10
for p in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader); do echo "killing GPU process $p"; kill $p; done
sleep 10; nvidia-smi --query-gpu=memory.used --format=csv,noheader
cp $L/q_$J.log $L/q_$J.$T.log
setsid nohup bash pod/olmo_ifomega/runq.sh $J > $L/runq_$T.log 2>&1 < /dev/null &
echo "$(date -u +%T) restarted $J (runq_$T)"
