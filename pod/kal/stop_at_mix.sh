#!/usr/bin/env bash
# Stop the EI ladder when round N's fine-tune starts (its mix file exists and the state_train child runs), i.e. after
# round N's sampling, before its fine-tune.  Usage: bash pod/kal/stop_at_mix.sh <name> <N>
cd /workspace/nd-takehome
D=artifacts/kalmar/ladder/$1
until [ -f $D/mix_$2.jsonl ] && pgrep -f "state_train.py --data $D/mix_[$2]" > /dev/null; do sleep 20; done
pkill -f "state_ladder_ei.py --init ckpts/kalmar/stage1_kalD_s0.pt --name ${1:0:1}[${1:1:1}]${1:2}" || true
sleep 3; pkill -f "state_train.py --data $D/mix_[$2]" || true
echo "stopped $1 after round $2 sampling (before its fine-tune) at $(date -u +%FT%TZ)" >> artifacts/kalmar/logs/$1.log
