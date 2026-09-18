#!/usr/bin/env bash
# Usage: bash pod/la/status.sh <pod>  -> last round line of every arm log on that pod
podrun $1 'cd /workspace/nd-takehome; for f in artifacts/ladder/la_*.log; do echo "$f: $(grep -E "^=== round|FAILED|Traceback|Error" $f | tail -n 1)"; done; ls artifacts/ladder/*.done 2>/dev/null; tail -n 1 artifacts/ladder/q.log 2>/dev/null; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader'
