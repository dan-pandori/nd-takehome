#!/usr/bin/env bash
# Exploratory (post hoc, log 2026-10-23 ~04:55): the same A_ES protocol with stream and test halves swapped (cross-fit),
# so the split's stream / test mismatch cancels in the mean of the two directions. Kalmar cells wait for q3. Restartable.
. pod/sedl/env.sh
J=pod/sedl/job.sh; D=data/style_edl/streams; O=artifacts/style_edl/edl_x
for S in S_own S_own2 S_seed S_short S_RL S_Kal; do
  if [ $S = S_Kal ]; then until grep -q "QUEUE DONE" artifacts/style_edl/logs/queue_q3_edl.log 2>/dev/null; do sleep 60; done; fi
  for s in 0 1 2; do
    L=ckpts/bs/stage1_best12_s${s}_b1200.pt
    $J xfit_s${s}_$S python3 style_edl/edl_run.py --ckpt $L --stream $D/s$s/$S.test.jsonl --test $D/s$s/$S.stream.jsonl --lrs 1e-5,1e-4,1e-3 --orders 0,1 --arm $S --lseed $s --algo es --out $O/s$s/$S.json
  done
  up artifacts/style_edl/edl_x
done
echo "QUEUE DONE $(date -u +%FT%TZ)"
