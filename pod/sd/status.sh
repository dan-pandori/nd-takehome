#!/usr/bin/env bash
# bash pod/sd/status.sh <pod>   -- one line per chain and the tail of each running job
bash pod/sd/sync.sh $1 sh 'cd /workspace/nd-takehome; ls artifacts/sd/*.done artifacts/sd/*.failed 2>/dev/null | sed "s|artifacts/sd/||" | tr "\n" " "; echo; for f in artifacts/sd/logs/*.log; do b=${f##*/}; b=${b%.log}; [ -f artifacts/sd/$b.done ] && continue; [ -f artifacts/sd/$b.failed ] && continue; echo "-- $b: $(tail -n 1 $f)"; done; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader'
