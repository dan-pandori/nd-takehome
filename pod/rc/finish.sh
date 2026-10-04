#!/usr/bin/env bash
# Replaces run.sh's tail (budget, 2026-10-04 01:45 UTC): wait for the ladder's r16, then run the r16 reads as two parallel
# jobs (tb72/h250 at sample seed 1 | long2/rr1316 at sample seed 0, batch 512) on the free GPU.  Usage: bash pod/rc/finish.sh <seed>
source pod/rc/env.sh
S=$1; N=la_T1_best12_s$S; CK=ckpts/rc/ladder/${N}_r16.pt
until [ -s artifacts/rc/$N/round_16.json ] && ! pgrep -f 'state_ladder_ei.p[y]' >/dev/null; do
  pgrep -f 'state_ladder_ei.p[y]' >/dev/null || { echo "LADDER NOT RUNNING and no round_16 $(date -u +%FT%TZ)"; exit 1; }; sleep 30; done
echo "=== r16 done $(date -u +%FT%TZ)"; up artifacts/rc
bash pod/rc/read.sh $CK s${S}_r16 1 tb72 h250 > artifacts/rc/finish_a_s$S.log 2>&1 &
bash pod/rc/read.sh $CK s${S}_r16 0 long2 rr1316 > artifacts/rc/finish_b_s$S.log 2>&1 &
wait; up artifacts/rc
touch artifacts/rc/RUN_DONE_s$S; echo "=== RUN DONE s$S $(date -u +%FT%TZ)"
