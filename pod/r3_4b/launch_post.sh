#!/usr/bin/env bash
cd /workspace/nd-takehome
nohup bash pod/r3_4b/post.sh "$@" > artifacts/r3_4b/q/post_$1_s$2.log 2>&1 < /dev/null &
disown; echo "launched post $1 s$2"
