#!/usr/bin/env bash
# One status line per pod: last finished round, last ladder/run event, GPU use.  Usage: pod/rc/st.sh [sleep_secs]
sleep ${1:-0}
for s in 0 1 2; do
  podrun rc-s$s "cd /workspace/nd-takehome; echo \"s$s: \$(ls artifacts/rc/la_T1_best12_s$s/round_*.json | sed 's/.*round_//;s/.json//' | sort -n | tail -n1) | \$(grep -E '^===|FAIL|Error' artifacts/rc/run_s$s.log | tail -n1 | cut -c1-110) | \$(grep -E '=== round|Error|Traceback' artifacts/rc/logs/ladder_s$s.log | tail -n1 | cut -c1-100) | \$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader)\"" 2>&1 | tail -n1
done; date -u +%T
