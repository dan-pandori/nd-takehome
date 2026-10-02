#!/usr/bin/env bash
# VPS: pull a pod's artifacts/rfc (no mixes / dumps / ckpts) + registry rows, check that the ckpts it wrote are in the
# bucket (md5 of local == size match in bucket listing), then delete the pod.  Usage: pod/rfc/finish.sh <pod> [--keep]
cd /home/dan/work/rl-from-ckpt; P=$1
pod/rfc/pull.sh $P artifacts/rfc </dev/null || { echo "PULL FAILED $P"; exit 1; }
pod/rfc/pull.sh $P artifacts/rl-from-ckpt </dev/null || { echo "REGISTRY PULL FAILED $P"; exit 1; }
loc=$(TO=60 pod/rfc/sh.sh $P "cd ckpts/rfc && find . -name '*.pt' -newer /workspace/nd-takehome/pod/rfc/env.sh -printf '%P %s\n' 2>/dev/null; find . -name '*.pt' -printf '%P %s\n'" </dev/null | sort -u)
rem=$(hf buckets list hf://buckets/dan-pandori/nd-rl/rl-from-ckpt/ckpts/rfc -R 2>/dev/null | awk '{print $NF, $1}' | sed 's#^rl-from-ckpt/ckpts/rfc/##')
miss=0; while read f s; do [ -z "$f" ] && continue
  # ladder copies made by ladder.sh fill() for untrained rounds are local only (logged); everything else must be uploaded
  echo "$rem" | grep -q "^$f " || { echo "NOT IN BUCKET: $f"; miss=$((miss+1)); }; done <<< "$loc"
[ $miss -gt 0 ] && { echo "keeping $P ($miss ckpts not in bucket)"; exit 1; }
[ "$2" = --keep ] && exit 0
podrm $P && echo "deleted $P"
