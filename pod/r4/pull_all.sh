#!/usr/bin/env bash
# Pull artifacts/r4 and ckpts/r4 from every r4-* pod into the worktree (rsync, incremental). Usage: bash pod/r4/pull_all.sh [pods...]
cd /home/dan/work/run4-grpo
PODS=${@:-$(ls ~/.config/nd-rl/pods | grep '^r4-')}
for p in $PODS; do
  echo "== $p"; bash pod/r4/sync.sh $p pull artifacts/r4 2>&1 | tail -n 1; [ "${CK:-1}" = 1 ] && bash pod/r4/sync.sh $p pull ckpts/r4 2>&1 | tail -n 1
done
ls artifacts/r4 | wc -l; du -sh artifacts/r4 ckpts/r4 2>/dev/null
