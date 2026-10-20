#!/usr/bin/env bash
# kc-2, second queue (replaces queue2's second wave): B2 Kalmár S and M at seed 1 (seed spread), started beside
# Kalmár M s0.  The v1 K12 / eval M / S runs of queue2 are dropped: v2 (queue1b) covers K12 and eval at S / M / L.
. pod/kc/env.sh
B="python3 kalmar_complexity/b2_preq.py"
for spec in "kal S 1" "kal M 1"; do set -- $spec
  bash pod/kc/job.sh b2_$1_$2_s$3 $B --task $1 --size $2 --seed $3 --max_thm 16384 --out artifacts/kc/b2/$1_$2_s$3.json &
  sleep 5; done
wait
up artifacts/kc
echo QUEUE2B DONE > artifacts/kc/logs/queue2b.done
