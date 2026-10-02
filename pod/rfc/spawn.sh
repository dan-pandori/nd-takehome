#!/usr/bin/env bash
# VPS: create ladder pods one at a time (podnew in parallel fails) and start one ladder on each.
# Usage: bash pod/rfc/spawn.sh "<pod> <seed> <start>" ...      tries RTX A6000, then A40 (any DC), then A6000 EU-SE-1
cd /home/dan/work/rl-from-ckpt; export ND_RUN_ID=rl-from-ckpt
for job in "$@"; do
  set -- $job; P=$1; S=$2; ST=$3
  [ -f ~/.config/nd-rl/pods/$P ] || for g in "NVIDIA RTX A6000|" "NVIDIA A40|" "NVIDIA A40|--data-center-ids EU-SE-1" "NVIDIA RTX A6000|--data-center-ids EU-SE-1"; do
    POD_GPU="${g%%|*}" POD_EXTRA="${g#*|}" timeout 900 podnew $P > /tmp/rfc/podnew_$P.log 2>&1 && break; sleep 5; done
  [ -f ~/.config/nd-rl/pods/$P ] || { echo "$(date -u +%T) NO POD $P"; continue; }
  pod/rfc/push.sh $P > /dev/null 2>&1 || { sleep 30; pod/rfc/push.sh $P > /dev/null 2>&1; }
  pod/rfc/bg.sh $P L_s${S}_$ST "bash pod/rfc/setup.sh; bash pod/rfc/ladder.sh $S $ST"
  echo "$(date -u +%T) $P $(grep -o 'gpu [^)]*' /tmp/rfc/podnew_$P.log) L_s${S}_$ST"
done
