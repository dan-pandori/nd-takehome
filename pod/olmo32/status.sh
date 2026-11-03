#!/usr/bin/env bash
# status.sh: one-screen status of this pod's olmo32 jobs.
cd /workspace/nd-takehome; A=artifacts/olmo32
date -u +%T; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader | tr '\n' ' '; echo
ls $A/meta/*.done 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' '; echo
for f in $A/logs/q_*.log; do [ -f "$f" ] || continue; echo "$(basename $f): $(grep -E '^\[|JOB_|requests' $f | tail -n 1 | cut -c1-160)"; done
grep -h "Avg generation throughput" $A/logs/q_*.log 2>/dev/null | tail -n 1 | cut -c1-250
