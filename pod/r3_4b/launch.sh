#!/usr/bin/env bash
# On the pod: start one draw detached so the ssh call returns. Usage: bash pod/r3_4b/launch.sh <25M|85M> <seed>
cd /workspace/nd-takehome
nohup bash pod/r3_4b/draw.sh "$@" > draw_$1_s$2.log 2>&1 < /dev/null &
disown; echo "launched $1 s$2"
