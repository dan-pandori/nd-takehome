#!/usr/bin/env bash
# Pull only the deep-pass files (deep_*) from every r33 pod into this worktree.
cd /home/dan/work/round3-run3
for p in r33a r33b r33c r33d; do F=~/.config/nd-rl/pods/$p; [ -f "$F" ] || continue; . "$F"
  timeout 150 rsync -rlptz --no-o --no-g --include 'deep_*' --exclude '*' -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT" root@$POD_IP:/workspace/nd-takehome/artifacts/r3_3/ artifacts/r3_3/ 2>/dev/null; done
for t in depth3_f0_a1:45 reductio_f0:52; do tag=${t%%:*}; n=${t##*:}; c=0; for f in artifacts/r3_3/deep_${tag}_s*.s0.jsonl; do [ -f "$f" ] && [ "$(wc -l < $f)" = "$n" ] && c=$((c+1)); done; echo "$tag complete deep files: $c / 24"; done
