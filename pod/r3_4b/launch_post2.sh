#!/usr/bin/env bash
cd /workspace/nd-takehome
pkill -f 'pod/r3_4b/pos[t].sh'
nohup bash pod/r3_4b/post2.sh "$@" > artifacts/r3_4b/q/post2_$1_s$2.log 2>&1 < /dev/null &
disown; echo "launched post2 $1 s$2"
