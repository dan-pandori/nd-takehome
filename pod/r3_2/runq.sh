#!/usr/bin/env bash
# round3-run2 queue runner: bash pod/r3_2/runq.sh <jobsfile> <N>. Each line: <name> <command...>; log artifacts/r3_2/logs/<name>.log,
# skipped if artifacts/r3_2/logs/<name>.done exists.
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
mkdir -p artifacts/r3_2/logs ckpts/r3_2
J=$1; N=${2:-3}
run_one() {
  name=$1; shift
  [ -f artifacts/r3_2/logs/$name.done ] && { echo "skip $name"; return; }
  echo "$(date -u +%FT%TZ) start $name"
  bash -c "$*" > artifacts/r3_2/logs/$name.log 2>&1 && touch artifacts/r3_2/logs/$name.done && echo "$(date -u +%FT%TZ) done $name" || echo "$(date -u +%FT%TZ) FAILED $name"
}
export -f run_one
while IFS= read -r line; do
  while [ "$(jobs -rp | wc -l)" -ge "$N" ]; do sleep 15; done
  run_one $line &
  sleep 5
done < <(grep -v '^#' "$J" | grep -v '^\s*$')
wait
echo "$(date -u +%FT%TZ) QUEUE DONE $J"
