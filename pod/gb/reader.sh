#!/usr/bin/env bash
# Reader queue.  Usage: bash pod/gb/reader.sh <queue file>   lines: "<label> <ckpt relpath> <sample seed> <reads...>"
# Runs the FIRST line whose checkpoint exists (locally, else in the grpo-best / trajectory bucket) and whose reads are not
# done; sleeps 60 s when nothing is ready; exits when every line is done.  The queue file may be edited live.
source pod/gb/env.sh
Q=$1
while true; do
  left=0; ran=0
  while read -r L P SS RS; do
    [ -z "$L" ] && continue; [ "${L:0:1}" = "#" ] && continue
    [ -f artifacts/gb/eval/.done_${L}_x$SS ] && continue
    left=$((left+1))
    if [ ! -s $P ]; then
      case $P in ckpts/tj/*) RUN=trajectory ;; *) RUN=grpo-best ;; esac
      get $RUN/$P $P || continue
    fi
    bash pod/gb/read.sh $P $L $SS $RS </dev/null
    ok=1; for R in $RS; do [ -s artifacts/gb/eval/${L}__${R}_x$SS.json ] || ok=0; done
    [ $ok = 1 ] && touch artifacts/gb/eval/.done_${L}_x$SS
    ran=1; break
  done < $Q
  [ $left = 0 ] && { echo "=== queue $Q empty $(date -u +%FT%TZ)"; exit 0; }
  [ $ran = 0 ] && sleep 60
done
