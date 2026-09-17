#!/usr/bin/env bash
# Run-4 queue: run the commands in a jobs file, N at a time. Usage: bash pod/r4/runq.sh <jobsfile> <N>
# Each line: <name> <command...>; stdout/stderr -> artifacts/r4/<name>.log; skipped if artifacts/r4/<name>.done exists.
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
mkdir -p artifacts/r4 ckpts/r4
J=$1; N=${2:-3}
run_one() {
  name=$1; shift
  [ -f artifacts/r4/$name.done ] && { echo "skip $name"; return; }
  echo "$(date -u +%H:%M:%S) start $name"
  bash -c "$*" > artifacts/r4/$name.log 2>&1 && touch artifacts/r4/$name.done && echo "$(date -u +%H:%M:%S) done $name" || echo "$(date -u +%H:%M:%S) FAILED $name"
}
export -f run_one
while IFS= read -r line; do
  while [ "$(jobs -rp | wc -l)" -ge "$N" ]; do sleep 15; done
  run_one $line &
  sleep 5
done < <(grep -v '^#' "$J" | grep -v '^\s*$')
wait
echo "$(date -u +%H:%M:%S) QUEUE DONE $J"
