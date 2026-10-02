#!/usr/bin/env bash
# Restart one GRPO ladder from scratch at decode batch 1,024 (after a CUDA OOM at 2,048), then its r8 reads.
# Usage: bash pod/gb/rerun.sh <adv> <seed>      (the old run's files are moved to *_oom2048)
source pod/gb/env.sh
N=gb_$1_s$2
[ -d artifacts/gb/$N ] && mv artifacts/gb/$N artifacts/gb/${N}_oom2048
[ -f artifacts/gb/logs/$N.log ] && mv artifacts/gb/logs/$N.log artifacts/gb/logs/${N}_oom2048.log
B=1024 bash pod/gb/grpo.sh $1 $2 > artifacts/gb/logs/$N.log 2>&1 || exit 1
bash pod/gb/read.sh ckpts/gb/${N}_r8.pt ${N}_r8 0 tb72 h250 dev held
bash pod/gb/read.sh ckpts/gb/${N}_r8.pt ${N}_r8 1 tb72 h250
