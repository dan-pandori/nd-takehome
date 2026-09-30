#!/usr/bin/env bash
# At the end of a pod's work: gzip the Lean dumps (literal texts of every checked sample) and upload artifacts/sx
# (dumps included), ckpts/sx and this process-tree's registry rows to the bucket.  Usage: bash pod/sx/finalize.sh
source pod/sx/env.sh
while pgrep -f 'pair.s[h]|t1read[s]|lpool_rerea[d]' > /dev/null; do sleep 30; done
for f in artifacts/sx/dump/*.jsonl; do [ -s "$f" ] && gzip -f "$f"; done
hf buckets sync artifacts/sx $BK/artifacts/sx >/dev/null 2>&1 || echo "UPLOAD FAILED artifacts"
hf buckets sync ckpts/sx $BK/ckpts/sx >/dev/null 2>&1 || echo "UPLOAD FAILED ckpts"
hf buckets sync artifacts/search-expert/registry hf://buckets/dan-pandori/nd-rl/registry/search-expert >/dev/null 2>&1 || echo "UPLOAD FAILED registry"
du -sh artifacts/sx/dump ckpts/sx
echo "=== finalize done $(date -u +%FT%TZ)"
