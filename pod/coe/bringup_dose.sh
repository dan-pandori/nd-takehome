#!/usr/bin/env bash
# Sequential bring-up of the dose-arm pods.  Usage: pod/coe/bringup_dose.sh <arm dose1|dose01> <pod>:<seed> ...
export ND_RUN_ID=create-or-elicit
cd /home/dan/work/create-or-elicit
ARM=$1; shift
for spec in "$@"; do
  P=${spec%%:*}; S=${spec##*:}
  echo "=== $P $ARM s$S $(date -u +%FT%TZ)"
  if [ ! -f ~/.config/nd-rl/pods/$P ]; then
    ok=0
    for try in 1 2 3; do
      timeout 900 podnew $P && { ok=1; break; }
      POD_EXTRA="--data-center-ids $([ $try = 1 ] && echo EU-SE-1 || echo CA-MTL-1)" timeout 900 podnew $P && { ok=1; break; }
    done
    [ $ok = 1 ] || { echo "GIVE UP $P"; continue; }
  fi
  pod/coe/push.sh $P > /dev/null 2>&1 || { echo "push failed $P"; continue; }
  timeout 900 podrun $P "cd /workspace/nd-takehome && bash pod/coe/setup.sh; tail -1 artifacts/coe/logs/setup_*.log"
  timeout 600 podrun $P "cd /workspace/nd-takehome && source pod/coe/env.sh > /dev/null 2>&1; [ -s data/coe/train_k12$ARM.jsonl ] || { hf buckets cp \$BK/create-or-elicit/data/coe/train_k12$ARM.jsonl.gz data/coe/train_k12$ARM.jsonl.gz && gunzip -f data/coe/train_k12$ARM.jsonl.gz; }; md5sum data/coe/train_k12$ARM.jsonl; wc -l data/coe/train_k12$ARM.jsonl"
  timeout 30 podrun $P "cd /workspace/nd-takehome; mkdir -p artifacts/coe/logs; setsid nohup bash pod/coe/seed2.sh $ARM $S > artifacts/coe/logs/seed_${ARM}_s$S.log 2>&1 < /dev/null & disown; sleep 1; echo seed-launched"
  timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/coe/reader.sh $ARM $S > artifacts/coe/logs/reader_${ARM}_s$S.log 2>&1 < /dev/null & disown; sleep 1; echo reader-launched"
  timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/coe/prune.sh > artifacts/coe/logs/prune.log 2>&1 < /dev/null & disown; sleep 1; echo prune-launched"
  timeout 30 podrun $P "cd /workspace/nd-takehome; setsid nohup bash pod/coe/post.sh $ARM $S > artifacts/coe/logs/post_${ARM}_s$S.log 2>&1 < /dev/null & disown; sleep 1; echo post-queued"
done
echo "=== bringup_dose done $(date -u +%FT%TZ)"
