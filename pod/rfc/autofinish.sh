#!/usr/bin/env bash
# VPS: every 5 min, for each ladder pod whose post_* job is done (or failed: then keep and report), run finish.sh.
cd /home/dan/work/rl-from-ckpt
while true; do
  left=0
  for line in $(tr ' ' ':' < pod/rfc/ladder_pods.txt); do IFS=: read p s st <<< "$line"
    [ -f ~/.config/nd-rl/pods/$p ] || continue; left=$((left+1))
    m=$(TO=25 pod/rfc/sh.sh $p "ls artifacts/rfc/post_s${s}_$st.done artifacts/rfc/post_s${s}_$st.fail 2>/dev/null; true" </dev/null)
    case "$m" in *.done*) echo "$(date -u +%T) finishing $p"; bash pod/rfc/finish.sh $p;;
                 *.fail*) [ -f /tmp/rfc/reported_$p ] || { echo "$(date -u +%T) POST FAILED on $p"; touch /tmp/rfc/reported_$p; };; esac
  done
  [ $left = 0 ] && { echo "all ladder pods finished"; exit 0; }
  sleep 300
done
