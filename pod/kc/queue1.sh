#!/usr/bin/env bash
# kc-1: B2 Kalmár L to 8,192 theorems, and B1-snap.  Usage: setsid nohup bash pod/kc/queue1.sh &
. pod/kc/env.sh
B="python3 kalmar_complexity/b2_preq.py"
bash pod/kc/job.sh prep_kal_8692 $B --task kal --size L --max_thm 8192 --prep_only --out /dev/null
bash pod/kc/job.sh snap bash pod/kc/snap.sh &
bash pod/kc/job.sh b2_kal_L_s0 $B --task kal --size L --max_thm 8192 --out artifacts/kc/b2/kal_L_s0.json &
wait
up artifacts/kc
echo QUEUE1 DONE > artifacts/kc/logs/queue1.done
