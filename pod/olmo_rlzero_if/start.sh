#!/usr/bin/env bash
# start.sh <pod> <queue-log> <job> ...: VPS-side. Sync code to a registered pod, run setup if it has not run, wait for
# SETUP_DONE (and a real CUDA allocation), then start runq.sh with the jobs (detached).
P=$1; L=$2; shift 2; W=/home/dan/work/olmo-rlzero-if; WS="bash $W/pod/olmo_rlzero_if/w.sh"
$WS sync $P || exit 1
if ! $WS sh $P "grep -q SETUP_DONE artifacts/olmo_rlzero_if/logs/setup.log" 2>/dev/null; then
  $WS bg $P setup pod/olmo_rlzero_if/setup.sh
  n=0; until $WS sh $P "grep -q SETUP_DONE artifacts/olmo_rlzero_if/logs/setup.log" 2>/dev/null || [ $n -ge 40 ]; do n=$((n+1)); sleep 20; done
fi
$WS sh $P "grep -E 'CUDA_ALLOC_OK|GRADER_OK|VERSIONS' artifacts/olmo_rlzero_if/logs/setup.log" || exit 1
$WS sh $P "grep -q CUDA_ALLOC_OK artifacts/olmo_rlzero_if/logs/setup.log" || { echo "CUDA allocation failed on $P"; exit 1; }
$WS bg $P $L pod/olmo_rlzero_if/runq.sh "$@"
