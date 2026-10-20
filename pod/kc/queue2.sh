#!/usr/bin/env bash
# kc-2: B2 Kalmár S / M to 16,384 (seeds 0, 1), K12 and eval at S / M / L.  Usage: setsid nohup bash pod/kc/queue2.sh &
. pod/kc/env.sh
B="python3 kalmar_complexity/b2_preq.py"
for t in kal k12 eval; do bash pod/kc/job.sh prep_${t}_16884 $B --task $t --size S --max_thm 16384 --prep_only --out /dev/null & done
wait
for spec in "kal M 0" "kal S 0" "k12 L 0" "eval L 0"; do set -- $spec
  bash pod/kc/job.sh b2_$1_$2_s$3 $B --task $1 --size $2 --seed $3 --max_thm 16384 --out artifacts/kc/b2/$1_$2_s$3.json & done
wait
up artifacts/kc
for spec in "k12 M 0" "k12 S 0" "eval M 0" "eval S 0" "kal S 1" "kal M 1"; do set -- $spec
  bash pod/kc/job.sh b2_$1_$2_s$3 $B --task $1 --size $2 --seed $3 --max_thm 16384 --out artifacts/kc/b2/$1_$2_s$3.json & done
wait
up artifacts/kc
echo QUEUE2 DONE > artifacts/kc/logs/queue2.done
