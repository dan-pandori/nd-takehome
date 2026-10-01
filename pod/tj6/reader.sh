#!/usr/bin/env bash
# Reader queue.  Usage: bash pod/tj6/reader.sh <queue file>     lines: "<label> <bucket ckpt relpath> <sample seed> <reads...>"
# Repeatedly runs the FIRST line whose checkpoint is in the bucket and whose reads are not done (priority = file order);
# sleeps 60 s when nothing is ready.  Lines with DUMP in the label's 5th+ field are not special: set DUMP=1 per line by
# prefixing the label with '+'.
source pod/tj6/env.sh
Q=$1
while true; do
  left=0; ran=0
  while read -r L P SS RS; do
    [ -z "$L" ] && continue
    dump=0; [ "${L:0:1}" = "+" ] && { dump=1; L=${L:1}; }
    [ -f artifacts/tj6/eval/.done_${L}_x$SS ] && continue
    left=$((left+1))
    if [ ! -s $P ]; then
      mkdir -p $(dirname $P); hf buckets cp $BK/trajectory-cap6/$P $P.part >/dev/null 2>&1 && mv $P.part $P || { rm -f $P.part; continue; }
    fi
    DUMP=$dump bash pod/tj6/read.sh $P $L $SS $RS
    ok=1; for R in $RS; do [ -s artifacts/tj6/eval/${L}__${R}_x$SS.json ] || ok=0; done
    [ $ok = 1 ] && touch artifacts/tj6/eval/.done_${L}_x$SS
    ran=1; break
  done < $Q
  [ $left = 0 ] && { echo "=== queue $Q empty $(date -u +%FT%TZ)"; exit 0; }
  [ $ran = 0 ] && sleep 60
done
