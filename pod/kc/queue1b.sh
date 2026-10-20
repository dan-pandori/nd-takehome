#!/usr/bin/env bash
# kc-1, second queue: B2 v2 (patience in steps) for eval and K12 at S / M / L.  Usage: setsid nohup bash pod/kc/queue1b.sh &
. pod/kc/env.sh
B="python3 kalmar_complexity/b2_preq.py"
for t in k12 eval; do bash pod/kc/job.sh prep_${t}_16884 $B --task $t --size S --max_thm 16384 --prep_only --out /dev/null; done
for spec in "eval L" "k12 L" "eval M" "k12 M" "eval S" "k12 S"; do set -- $spec
  bash pod/kc/job.sh b2v2_$1_$2_s0 $B --task $1 --size $2 --max_thm 16384 --patience_steps 3000 --es_min 5000 --cap 20000 --out artifacts/kc/b2/v2_$1_$2_s0.json &
  sleep 5; done
wait
up artifacts/kc
echo QUEUE1B DONE > artifacts/kc/logs/queue1b.done
