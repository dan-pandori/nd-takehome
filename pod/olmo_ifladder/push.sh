#!/usr/bin/env bash
# push.sh <pod>: VPS-side; push the run's code and inputs to the pod (rsync into /workspace/nd-takehome).
N=$1; export POD_LOCAL_ROOT=/home/dan/work/olmo-ifladder
for p in olmo_ifladder olmo_ifomega/grade.py olmo_ifomega/vendor olmo_ifomega/problems.jsonl olmo32/grade.py olmo32/oi_math_utils.py pod/olmo_ifomega/fetch.sh pod/olmo_ifladder; do
  podpush $N $p > /dev/null 2>&1 || echo "PUSH_FAIL $p"
done
echo "pushed $(date -u +%T)"
