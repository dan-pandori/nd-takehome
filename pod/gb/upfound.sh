#!/usr/bin/env bash
# Upload the final cumulative archives (found_8 / found_transfer_8, gzipped) of every ladder on this pod to the bucket.
source pod/gb/env.sh
for d in artifacts/gb/gb_*; do
  for f in $d/found_8.jsonl $d/found_transfer_8.jsonl; do
    [ -s $f ] || continue; gzip -kf $f
    hf buckets cp $f.gz $BK/grpo-best/$f.gz >/dev/null 2>&1 && echo "up $f.gz" || echo "UPLOAD FAILED $f.gz"
  done
done
