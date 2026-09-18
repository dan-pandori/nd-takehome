#!/usr/bin/env bash
# round3-run1 queue runner. Usage: bash pod/r3_4b/runq.sh <jobsfile> <N>
# Each line: <name> <command...> ; log -> artifacts/r3_4b/q/<name>.log ; skipped if artifacts/r3_4b/q/<name>.done exists.
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p artifacts/r3_4b/q ckpts/r3_4b
J=$1; N=${2:-3}
run_one() {
  name=$1; shift
  [ -f artifacts/r3_4b/q/$name.done ] && { echo "skip $name"; return; }
  echo "$(date -u +%H:%M:%S) start $name"
  bash -c "$*" > artifacts/r3_4b/q/$name.log 2>&1 && touch artifacts/r3_4b/q/$name.done && echo "$(date -u +%H:%M:%S) done $name" || echo "$(date -u +%H:%M:%S) FAILED $name"
}
export -f run_one
while IFS= read -r line; do
  while [ "$(jobs -rp | wc -l)" -ge "$N" ]; do sleep 15; done
  run_one $line &
  sleep 5
done < <(grep -v '^#' "$J" | grep -v '^\s*$')
wait
echo "$(date -u +%H:%M:%S) QUEUE DONE $J"
