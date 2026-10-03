#!/usr/bin/env bash
# One seed of rl-continue on one pod: ladder r9-r12 -> r12 reads -> ladder r13-r16 -> r16 reads -> r8 rr600/long2 baseline.
# Usage: bash pod/rc/run.sh <seed>.  Restartable (finished rounds / reads are skipped).  Skip a read group by creating
# artifacts/rc/SKIP_<group> on the pod (groups: r12x0 r16x0 r8rr) -- the budget priority order of the pre-registration.
source pod/rc/env.sh
S=$1; N=la_T1_best12_s$S; D=data/kh/train_k12.jsonl
case $S in 2) LB0=1024 ;; *) LB0=2048 ;; esac       # each seed's r8 ladder batch in trajectory (s2 resumed at 1,024 after an OOM)
grep -q SETUP_DONE artifacts/rc/logs/setup_s$S.log 2>/dev/null || bash pod/rc/setup.sh $S
grep -q SETUP_DONE artifacts/rc/logs/setup_s$S.log || { echo "SETUP FAILED"; exit 1; }
last() { ls artifacts/rc/$N/round_*.json 2>/dev/null | sed 's/.*round_\([0-9]*\).json/\1/' | sort -n | tail -n1; }
seg() {   # run rounds up to $1, resuming after the last finished round; on failure retry (batch 1,024 if it was an OOM)
  local end=$1 lb=$LB0 tries=0
  while [ "$(last)" -lt "$end" ]; do
    local nxt=$(( $(last) + 1 )); tries=$((tries+1)); [ $tries -gt 3 ] && { echo "LADDER FAILED $N at r$nxt"; exit 1; }
    echo "=== ladder $N r$nxt-r$end batch $lb ckpt md5 $(md5sum < ckpts/rc/ladder/${N}_r$((nxt-1)).pt | cut -c1-32) $(date -u +%FT%TZ)"
    ND_ARM=best12 ND_SEED=$S python3 state_ladder_ei.py --init ckpts/tj/stage1_best12_s${S}_b1200.pt --name $N --seed $S --batch $lb \
      --train $D --heldout data/p2/heldout.jsonl --outdir artifacts/rc --ckptdir ckpts/rc/ladder --resume --start_round $nxt \
      --rounds $((end-nxt+1)) >> artifacts/rc/logs/ladder_s$S.log 2>&1 \
      || { grep -q OutOfMemoryError artifacts/rc/logs/ladder_s$S.log && lb=1024; echo "=== ladder exit != 0, last round $(last), next batch $lb $(date -u +%FT%TZ)"; }
    up artifacts/rc
  done
}
reads() { local r=$1 x=$2; shift 2; bash pod/rc/read.sh ckpts/rc/ladder/${N}_r$r.pt s${S}_r$r $x "$@"; }
seg 12
reads 12 1 tb72 h250
[ -f artifacts/rc/SKIP_r12x0 ] || reads 12 0 tb72 h250
seg 16
reads 16 1 tb72 h250
reads 16 0 rr1316 long2
[ -f artifacts/rc/SKIP_r16x0 ] || reads 16 0 tb72 h250
[ -f artifacts/rc/SKIP_r8rr ] || reads 8 0 rr1316 long2
up artifacts/rc
touch artifacts/rc/RUN_DONE_s$S; echo "=== RUN DONE s$S $(date -u +%FT%TZ)"
