#!/usr/bin/env bash
# Reader queue.  Usage: bash pod/rfc/reader.sh <queue file>
#   lines: "<label> <bucket relpath (from the nd-rl bucket root)> <sample seed> <reads...>"   reads: tb72 h250
# Repeatedly runs the FIRST line whose checkpoint is in the bucket and whose reads are not done (priority = file order);
# sleeps 60 s when nothing is ready.  The queue file may be edited while this runs (it is re-read every pass).
source pod/rfc/env.sh
Q=$1
while true; do
  left=0; ran=0
  while read -r L P SS RS; do
    [ -z "$L" ] && continue; [ "${L:0:1}" = "#" ] && continue
    [ -f artifacts/rfc/eval/.done_${L}_x$SS ] && continue
    left=$((left+1))
    LP=${P#*/}     # local path: drop the run prefix (rl-from-ckpt/ or trajectory/)
    if [ ! -s $LP ]; then
      mkdir -p $(dirname $LP); hf buckets cp $BK/$P $LP.part >/dev/null 2>&1 && mv $LP.part $LP || { rm -f $LP.part; continue; }
    fi
    bash pod/rfc/read.sh $LP $L $SS $RS
    ok=1; for R in $RS; do [ -s artifacts/rfc/eval/${L}__${R}_x$SS.json ] || ok=0; done
    [ $ok = 1 ] && touch artifacts/rfc/eval/.done_${L}_x$SS
    ran=1; break
  done < $Q
  [ $left = 0 ] && { echo "=== queue $Q empty $(date -u +%FT%TZ)"; exit 0; }
  [ $ran = 0 ] && sleep 60
done
