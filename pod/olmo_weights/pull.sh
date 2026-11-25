#!/usr/bin/env bash
# pull.sh <pod>: VPS-side; pull artifacts/olmo_weights/ (statistics CSVs, logs, stage-0 results; never weights).
N=$1; export POD_LOCAL_ROOT=/home/dan/work/olmo-weights
podpull $N artifacts/olmo_weights > /dev/null 2>&1 || echo "PULL_FAIL"
echo "pulled $(date -u +%T): $(find $POD_LOCAL_ROOT/artifacts/olmo_weights -name DONE | wc -l) DONE markers"
