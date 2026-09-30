#!/usr/bin/env bash
# Pull what the analysis needs from a pod into THIS worktree (the full artifacts are in the bucket via `up`):
# round / alloc / args / supply jsons, cands_*, supply_found_8, found_8, logs, read-outs, registry rows.  Usage: pod/fsup/finish.sh <pod>
set -e; . ~/.config/nd-rl/env; N=$1; . ~/.config/nd-rl/pods/$N
SSHO="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -o ServerAliveInterval=30"
cd /home/dan/work/frontier-supply
rsync -rlptz --no-o --no-g -m -e "ssh $SSHO -p $POD_PORT" --include '*/' --include 'round_*.json' --include 'args.json' \
  --include 'supply_leak.json' --include 'cands_*.jsonl' --include 'supply_found_8.jsonl' --include 'found_8.jsonl' --include 'alloc_8.json' \
  --include 'logs/*.log' --include 'rr/*' --include '*.done' --include '*.fail' --include 'heldout_*' --exclude '*' \
  "root@$POD_IP:/workspace/nd-takehome/artifacts/fsup/" artifacts/fsup/
rsync -rlptz --no-o --no-g -e "ssh $SSHO -p $POD_PORT" "root@$POD_IP:/workspace/nd-takehome/artifacts/frontier-supply/" artifacts/frontier-supply/
ssh $SSHO -p $POD_PORT root@$POD_IP "cd /workspace/nd-takehome; source pod/fsup/env.sh; up artifacts/fsup; up artifacts/frontier-supply; up ckpts/fsup; echo uploaded"
