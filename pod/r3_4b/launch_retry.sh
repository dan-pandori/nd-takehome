#!/usr/bin/env bash
cd /workspace/nd-takehome
nohup bash pod/r3_4b/retry.sh "$@" > retry_$1_s$2.log 2>&1 < /dev/null &
disown; echo "launched retry $1 s$2"
