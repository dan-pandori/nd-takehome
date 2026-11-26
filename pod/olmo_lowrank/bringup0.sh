#!/usr/bin/env bash
# bringup0.sh (pod side): the stage-0 pod: setup.sh with FETCH="dpo s2300", the GPU gate, then stage0.sh. Run detached:
# setsid nohup bash pod/olmo_lowrank/bringup0.sh > /dev/null 2>&1 < /dev/null &
cd /workspace/nd-takehome; A=artifacts/olmo_lowrank; mkdir -p $A/logs $A/meta
echo "BRINGUP0_START $(date -u +%FT%TZ)" >> $A/logs/bringup.log
FETCH="dpo s2300" bash pod/olmo_lowrank/setup.sh > $A/logs/setup.log 2>&1
grep -q SETUP_DONE $A/logs/setup.log && touch $A/meta/setup.done
grep -q "^GPU_OK" $A/meta/gpu_status 2>/dev/null || { echo "GPU_BAD $(date -u +%FT%TZ)" >> $A/logs/bringup.log; exit 1; }
echo "SETUP_OK $(date -u +%FT%TZ)" >> $A/logs/bringup.log
bash pod/olmo_lowrank/stage0.sh > $A/logs/stage0_run.log 2>&1
echo "BRINGUP0_END $(date -u +%FT%TZ)" >> $A/logs/bringup.log
