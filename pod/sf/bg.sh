#!/usr/bin/env bash
# Start a detached job on a pod and return.  Usage: pod/sf/bg.sh <pod> <jobname> "<command>"
# Every job writes the literal sampled text + Lean verdict to artifacts/sf2/dumps/<job>.jsonl (LEAN_GATE_DUMP).
. ~/.config/nd-rl/env; N=$1; J=$2; shift 2; F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || { echo "no pod $N"; exit 1; }; . "$F"
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
ssh $SSHO -p "$POD_PORT" "root@$POD_IP" "cd /workspace/nd-takehome && mkdir -p artifacts/sf2/logs artifacts/sf2/dumps && rm -f artifacts/sf2/$J.done artifacts/sf2/$J.fail && setsid nohup bash -c 'source pod/sf/env.sh; export LEAN_GATE_DUMP=artifacts/sf2/dumps/$J.jsonl LEAN_GATE_LOG=artifacts/sf2/logs/$J.gate.jsonl; { $*; } > artifacts/sf2/logs/$J.log 2>&1 && touch artifacts/sf2/$J.done || touch artifacts/sf2/$J.fail' < /dev/null > /dev/null 2>&1 & echo started $J on $N"
