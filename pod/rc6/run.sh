#!/usr/bin/env bash
# One seed of rl-continue-cap6 on one pod: ladder r9-r16 -> r16 reads (tb72 + h250, sample seed 1 = group C read-out).
# Usage: bash pod/rc6/run.sh <seed>.  Restartable (finished rounds / reads are skipped).  Optional reads beyond the
# pre-registered core run only if artifacts/rc6/DO_<group> exists on the pod (groups: r16x0 r12x1 rr) -- added when the
# budget allows, in the pre-registration's priority order.
source pod/rc6/env.sh
S=$1; N=la_T1_best6_s$S; D=data/p2/train_depth3_f0_a1.jsonl; LB0=2048     # trajectory-cap6 ran every seed at 2,048
grep -q SETUP_DONE artifacts/rc6/logs/setup_s$S.log 2>/dev/null || bash pod/rc6/setup.sh $S
grep -q SETUP_DONE artifacts/rc6/logs/setup_s$S.log || { echo "SETUP FAILED"; exit 1; }
last() { ls artifacts/rc6/$N/round_*.json 2>/dev/null | sed 's/.*round_\([0-9]*\).json/\1/' | sort -n | tail -n1; }
seg() {   # run rounds up to $1, resuming after the last finished round; on failure retry (batch 1,024 if it was an OOM)
  local end=$1 lb=$LB0 tries=0
  while [ "$(last)" -lt "$end" ]; do
    local nxt=$(( $(last) + 1 )); tries=$((tries+1)); [ $tries -gt 3 ] && { echo "LADDER FAILED $N at r$nxt"; exit 1; }
    echo "=== ladder $N r$nxt-r$end batch $lb ckpt md5 $(md5sum < ckpts/rc6/ladder/${N}_r$((nxt-1)).pt | cut -c1-32) $(date -u +%FT%TZ)"
    ND_ARM=best6 ND_SEED=$S python3 state_ladder_ei.py --init ckpts/tj6/stage1_best6_s${S}_b1200.pt --name $N --seed $S --batch $lb \
      --train $D --heldout data/p2/heldout.jsonl --outdir artifacts/rc6 --ckptdir ckpts/rc6/ladder --resume --start_round $nxt \
      --rounds $((end-nxt+1)) >> artifacts/rc6/logs/ladder_s$S.log 2>&1 \
      || { grep -q OutOfMemoryError artifacts/rc6/logs/ladder_s$S.log && lb=1024; echo "=== ladder exit != 0, last round $(last), next batch $lb $(date -u +%FT%TZ)"; }
    up artifacts/rc6
  done
}
reads() { local r=$1 x=$2; shift 2; bash pod/rc6/read.sh ckpts/rc6/ladder/${N}_r$r.pt s${S}_r$r $x "$@"; }
seg 16
reads 16 1 tb72 h250
[ -f artifacts/rc6/DO_r16x0 ] && reads 16 0 tb72 h250
[ -f artifacts/rc6/DO_r12x1 ] && reads 12 1 tb72 h250
[ -f artifacts/rc6/DO_rr ] && { reads 16 0 rr1316 long2; reads 8 0 rr1316 long2; }
up artifacts/rc6
touch artifacts/rc6/RUN_DONE_s$S; echo "=== RUN DONE s$S $(date -u +%FT%TZ)"
