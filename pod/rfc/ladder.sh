#!/usr/bin/env bash
# The T1 ladder from one start, exactly trajectory's (pod/rfc/seed.sh's ladder block: state_ladder_ei.py defaults, 8 rounds
# x k 32, T 0.8, rl_targets, replay from K12, ladder batch 2,048), name la_T1_best12_s<S>_<start>.  On a sampling OOM it
# resumes from the next round at batch 1,024 (as trajectory's seed 2 did; a sampling re-draw).
# Stop rule (start p0 only, pre-registered): rounds 1-2 first; if they accept no target proof, stop.
# Usage: bash pod/rfc/ladder.sh <seed> <start>
source pod/rfc/env.sh; source pod/rfc/ckpt.sh
S=$1; P=$2; D=data/kh/train_k12.jsonl; N=la_T1_best12_s${S}_$P; CK=$(startck $S $P)
fetch trajectory/$CK $CK
echo "=== start $N from $CK md5 $(md5sum < $CK | cut -c1-8) $(date -u +%FT%TZ)"
run() {  # run <batch> <start_round> <rounds> [--resume]
  ND_ARM=T1_$P ND_SEED=$S python3 state_ladder_ei.py --init $CK --name $N --seed $S --batch $1 --train $D \
    --heldout data/p2/heldout.jsonl --outdir artifacts/rfc --ckptdir ckpts/rfc/ladder --start_round $2 --rounds $3 $4; }
last() { ls artifacts/rfc/$N/round_*.json 2>/dev/null | sed 's/.*round_\([0-9]*\).json/\1/' | sort -n | tail -n1; }
fill() {  # a round with no accepted proof trains nothing and writes no checkpoint: its rN is the previous one (resume needs it)
  local r=$1 q; [ $r = 0 ] && return; [ -s ckpts/rfc/ladder/${N}_r$r.pt ] && return
  for q in $(seq $((r-1)) -1 0); do [ $q = 0 ] && { cp $CK ckpts/rfc/ladder/${N}_r$r.pt; break; }
    [ -s ckpts/rfc/ladder/${N}_r$q.pt ] && { cp ckpts/rfc/ladder/${N}_r$q.pt ckpts/rfc/ladder/${N}_r$r.pt; break; }; done
  echo "=== $N r$r: no training that round; r$r = copy of the previous checkpoint (local only)"; }
goto() {  # run rounds up to $1 from wherever the ladder is, with one OOM fallback to batch 1024
  local L=$(last); L=${L:-0}; [ $L -ge $1 ] && return 0; fill $L
  if [ $L = 0 ]; then run ${LB:-2048} 1 $1 && return 0; else run ${LB:-2048} $((L+1)) $(($1-L)) --resume && return 0; fi
  L=$(last); L=${L:-0}; fill $L; echo "=== failure after round $L; retry at batch 1024 $(date -u +%FT%TZ)"
  if [ $L = 0 ]; then run 1024 1 $1; else run 1024 $((L+1)) $(($1-L)) --resume; fi
}
if [ $P = p0 ]; then
  goto 2 || exit 1; up artifacts/rfc
  acc=$(python3 -c "import json; print(sum(json.load(open(f'artifacts/rfc/$N/round_{r}.json'))['targets_round']['solved'] for r in (1,2)))")
  echo "=== p0 stop-rule check: target solves in rounds 1+2 = $acc"
  [ "$acc" = 0 ] && { echo "=== STOP RULE: no accepted proof in rounds 1-2; ladder stopped"; touch artifacts/rfc/$N/STOPPED; up artifacts/rfc; exit 0; }
fi
goto 8 || exit 1
for r in 1 2 3 4 5 6 7 8; do fill $r; done
up artifacts/rfc
echo "=== ladder done $N $(date -u +%FT%TZ)"
