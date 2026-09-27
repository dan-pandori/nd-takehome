#!/usr/bin/env bash
# Upload this run's artifacts and checkpoints to the public HF bucket.  Staged with cp into a tree
# that mirrors the repo (never ln -f: a hard link plus a cp fallback overwrites the original).
#   bash pod/sd/upload.sh ckpts|artifacts|all
set -e
cd /home/dan/work/stage1-dynamics
B=hf://buckets/dan-pandori/nd-rl/stage1-dynamics
case "${1:-all}" in
  ckpts|all) hf buckets sync ckpts/sd "$B/ckpts/sd" ;;
esac
case "${1:-all}" in
  artifacts|all) hf buckets sync artifacts/sd "$B/artifacts/sd" ;;
esac
case "${1:-all}" in
  data|all) hf buckets sync data/sd "$B/data/sd" ;;
esac
echo "uploaded ${1:-all} to $B"
