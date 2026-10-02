#!/usr/bin/env bash
# Resume one GRPO ladder from its boundary-R checkpoint after a crash (grpo_state.py --resume_round), then its r8 reads.
# Usage: bash pod/gb/resume.sh <adv> <seed> <R>      log: artifacts/gb/logs/gb_<adv>_s<seed>_resume<R>.log
source pod/gb/env.sh
N=gb_$1_s$2
get grpo-best/ckpts/gb/${N}_r$3.pt ckpts/gb/${N}_r$3.pt || { echo "no checkpoint ${N}_r$3"; exit 1; }
B=${B:-2048} LP=${LP:-256} bash pod/gb/grpo.sh $1 $2 --resume_round $3 > artifacts/gb/logs/${N}_resume$3.log 2>&1 || exit 1
bash pod/gb/read.sh ckpts/gb/${N}_r8.pt ${N}_r8 0 tb72 h250 dev held
bash pod/gb/read.sh ckpts/gb/${N}_r8.pt ${N}_r8 1 tb72 h250
