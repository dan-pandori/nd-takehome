#!/usr/bin/env bash
# Resume a T1 ladder after a failure (e.g. sampling OOM) from the round after the last completed one, at ladder sampling
# batch LB (default 1024; a batch change is a sampling re-draw).  Usage: bash pod/tj6/ladder_resume.sh <seed>
source pod/tj6/env.sh
S=$1; LB=${LB:-1024}; D=data/p2/train_depth3_f0_a1.jsonl; N=la_T1_best6_s$S
last=$(ls artifacts/tj6/$N/round_*.json 2>/dev/null | sed 's/.*round_\([0-9]*\).json/\1/' | sort -n | tail -n1)
[ -z "$last" ] && { echo "no completed round"; exit 1; }
[ "$last" -ge 8 ] && { echo "ladder complete"; exit 0; }
nxt=$((last+1)); echo "=== resume $N from round $nxt (batch $LB) $(date -u +%FT%TZ)"
ND_ARM=best6 ND_SEED=$S python3 state_ladder_ei.py --init ckpts/tj6/stage1_best6_s${S}_b1200.pt --name $N --seed $S --batch $LB \
  --train $D --heldout data/p2/heldout.jsonl --outdir artifacts/tj6 --ckptdir ckpts/tj6/ladder --resume --start_round $nxt \
  --rounds $((9-nxt)) || exit 1
up artifacts/tj6
echo "=== ladder done $N $(date -u +%FT%TZ)"
