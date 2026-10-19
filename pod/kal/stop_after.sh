#!/usr/bin/env bash
# Stop a ladder once round N's json exists.  Usage: bash pod/kal/stop_after.sh <name> <N>
cd /workspace/nd-takehome
until [ -f artifacts/kalmar/ladder/$1/round_$2.json ]; do sleep 30; done
pkill -f "state_ladder_ei.py --init ckpts/kalmar/stage1_kalD_s0.pt --name ${1:0:1}[${1:1:1}]${1:2}" || true
sleep 5; pkill -f "state_train.py --data artifacts/kalmar/ladder/${1:0:1}[${1:1:1}]${1:2}/mix" || true
echo "stopped $1 after round $2 at $(date -u +%FT%TZ)" >> artifacts/kalmar/logs/$1.log
