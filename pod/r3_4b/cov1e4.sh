#!/usr/bin/env bash
# On the pod: bash pod/r3_4b/cov1e4.sh <tag> <seed> <shard i/n> <batch> [rev]  -- detached launcher for cov1e4_job.sh
cd /workspace/nd-takehome; mkdir -p artifacts/r3_4b/q
nohup bash pod/r3_4b/cov1e4_job.sh "$@" > /dev/null 2>&1 < /dev/null &
disown; echo "queued cov1e4 $*"
