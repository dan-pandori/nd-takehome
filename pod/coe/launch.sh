#!/usr/bin/env bash
# Launch the seed job and the reader on a pod, detached.  Usage: pod/coe/launch.sh <pod> <full|ko> <seed>
P=$1; ARM=$2; S=$3
timeout 30 podrun $P "cd /workspace/nd-takehome; mkdir -p artifacts/coe/logs; setsid nohup bash pod/coe/seed.sh $ARM $S > artifacts/coe/logs/seed_${ARM}_s$S.log 2>&1 < /dev/null & disown; sleep 1; echo seed-launched"
timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/coe/reader.sh $ARM $S > artifacts/coe/logs/reader_${ARM}_s$S.log 2>&1 < /dev/null & disown; sleep 1; echo reader-launched"
timeout 30 podrun $P "ps aux | grep -c '[p]od/coe/seed.sh'; ps aux | grep -c '[p]od/coe/reader.sh'"
