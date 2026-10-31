#!/usr/bin/env bash
# Sequential bring-up (podnew in parallel fails) of this run's pods = pod/coe/bringup_dose.sh for coe-dose01.
# Usage: pod/d01/bringup.sh <pod>:<seed> ...   (seed "ko" = priority 2, knockout s1 rounds 25-32)
export ND_RUN_ID=coe-dose01
cd /home/dan/work/coe-dose01
for spec in "$@"; do
  P=${spec%%:*}; S=${spec##*:}
  echo "=== $P $S $(date -u +%FT%TZ)"
  if [ ! -f ~/.config/nd-rl/pods/$P ]; then
    ok=0
    for try in 1 2 3; do
      timeout 900 podnew $P && { ok=1; break; }
      POD_EXTRA="--data-center-ids $([ $try = 1 ] && echo EU-SE-1 || echo CA-MTL-1)" timeout 900 podnew $P && { ok=1; break; }
    done
    [ $ok = 1 ] || { echo "GIVE UP $P"; continue; }
  fi
  sed -i 's/^GPU=\(NVIDIA [^"].*\)$/GPU="\1"/' ~/.config/nd-rl/pods/$P
  pod/d01/push.sh $P > /dev/null 2>&1 || { echo "push failed $P"; continue; }
  ARM=dose01; [ "$S" = ko ] && ARM=ko
  timeout 900 podrun $P "cd /workspace/nd-takehome && bash pod/d01/setup.sh $ARM; tail -n 3 artifacts/coe/logs/setup_*.log"
  timeout 30 podrun $P "cd /workspace/nd-takehome; mkdir -p artifacts/coe/logs; setsid nohup bash pod/coe/prune.sh > artifacts/coe/logs/prune.log 2>&1 < /dev/null & disown; sleep 1; echo prune-launched"
  if [ "$S" = ko ]; then
    timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/d01/ko_ext.sh > artifacts/coe/logs/ko_ext.log 2>&1 < /dev/null & disown; sleep 1; echo ko_ext-launched"
    timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/d01/backup.sh la_ko_s1 32 > artifacts/coe/logs/backup_la_ko_s1.log 2>&1 < /dev/null & disown; sleep 1; echo backup-launched"
  else
    timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/d01/seed.sh $S > artifacts/coe/logs/seed_dose01_s$S.log 2>&1 < /dev/null & disown; sleep 1; echo seed-launched"
    timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/d01/reader.sh $S > artifacts/coe/logs/reader_dose01_s$S.log 2>&1 < /dev/null & disown; sleep 1; echo reader-launched"
    timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/d01/backup.sh la_dose01_s$S 16 > artifacts/coe/logs/backup_la_dose01_s$S.log 2>&1 < /dev/null & disown; sleep 1; echo backup-launched"
  fi
done
echo "=== bringup done $(date -u +%FT%TZ)"
