#!/usr/bin/env bash
# push.sh <pod>: VPS-side; push the run's code and request files to the pod (rsync into /workspace/nd-takehome).
N=$1; export POD_LOCAL_ROOT=/home/dan/work/olmo-answeronly
for p in olmo_answeronly olmo_transplant olmo_iffu olmo_ifomega/grade.py olmo_ifomega/vendor olmo_ifomega/problems.jsonl olmo32/grade.py olmo32/oi_math_utils.py pod/olmo_ifomega/fetch.sh pod/olmo_answeronly artifacts/olmo_answeronly/requests; do
  podpush $N $p > /dev/null 2>&1 || echo "PUSH_FAIL $p"
done
echo "pushed $(date -u +%T)"
