#!/usr/bin/env bash
# Two GRPO ladders on one card, then their r8 read-outs.  Usage: bash pod/gb/pair.sh <adv1> <seed1> <adv2> <seed2>
source pod/gb/env.sh
bash pod/gb/grpo.sh $1 $2 > artifacts/gb/logs/gb_$1_s$2.log 2>&1 &
P1=$!
sleep 30
bash pod/gb/grpo.sh $3 $4 > artifacts/gb/logs/gb_$3_s$4.log 2>&1 &
P2=$!
wait $P1; R1=$?; wait $P2; R2=$?
echo "=== ladders done $(date -u +%FT%TZ) rc $R1 $R2"
for J in "$1 $2" "$3 $4"; do
  set -- $J; N=gb_$1_s$2
  [ -s ckpts/gb/${N}_r8.pt ] || { echo "no r8 for $N"; continue; }
  bash pod/gb/read.sh ckpts/gb/${N}_r8.pt ${N}_r8 0 tb72 h250 dev held
  bash pod/gb/read.sh ckpts/gb/${N}_r8.pt ${N}_r8 1 tb72 h250
done
echo "=== pair done $(date -u +%FT%TZ)"
