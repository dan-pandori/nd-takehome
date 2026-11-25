#!/usr/bin/env bash
# push.sh <pod>: VPS-side; push the run's code and manifest to the pod (rsync into /workspace/nd-takehome).
N=$1; export POD_LOCAL_ROOT=/home/dan/work/olmo-weights
for p in olmo_weights pod/olmo_weights; do podpush $N $p > /dev/null 2>&1 || echo "PUSH_FAIL $p"; done
echo "pushed $(date -u +%T)"
