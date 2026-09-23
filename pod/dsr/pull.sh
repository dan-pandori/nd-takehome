#!/usr/bin/env bash
# Pull every pod's artifacts into artifacts/dsr/<pod>/ (never a shared flat dir: two pods writing the same
# relative path would clobber each other -- the upload-staging hard-link trap).  Usage: bash pod/dsr/pull.sh [pods...]
cd /home/dan/work/ds-rendering
PODS=("$@"); [ ${#PODS[@]} -eq 0 ] && PODS=(dsr-c0 dsr-r1 dsr-r3 dsr-r2 dsr-r4)
for p in "${PODS[@]}"; do
  [ -f ~/.config/nd-rl/pods/$p ] || { echo "skip $p (gone)"; continue; }
  bash pod/dsr/sync.sh $p pullall 2>/dev/null && echo "pulled $p -> artifacts/dsr/$p/"
done
