#!/usr/bin/env bash
# Stage and upload run proof-strategies' artifacts and data to the PUBLIC bucket
#   hf://buckets/dan-pandori/nd-rl/proof-strategies/{artifacts,data}/
# Copies (never links) into a mirror tree, excluding: Charles's release and anything derived from it (nd-rl is private),
# textbook72 proofs and per-record textbook72 labels (sealed), the pod tarball (holds both), inputs copied from other
# runs (data/ps/in/, already in the bucket under their own runs), and create-or-elicit's mix files (artifacts/ps/scratch/,
# in the bucket under create-or-elicit/). Every staged file is credential-scanned before upload.
#   bash proof_strategies/stage_upload.sh [--dry]
set -euo pipefail
cd "$(dirname "$0")/.."
ST=/tmp/ps_stage; rm -rf "$ST"; mkdir -p "$ST"
keep() {   # $1 = repo-relative file
  case "$1" in
    *charles*|*textbook72*|*ps_pod.tgz|artifacts/ps/scratch/*|data/ps/in/*) return 1;;
  esac
  return 0
}
n=0
while IFS= read -r f; do
  if keep "$f"; then mkdir -p "$ST/$(dirname "$f")"; cp "$f" "$ST/$f"; n=$((n+1)); fi
done < <(find artifacts/ps data/ps -type f | sort)
echo "staged $n files: $(du -sh "$ST" | cut -f1)"
find "$ST" -type f | grep -i -E "charles|textbook72|tgz" && { echo "excluded kind leaked into staging"; exit 1; } || true
python3 scan_secrets.py $(find "$ST" -type f) > /tmp/ps_scan.txt 2>&1 || { echo "SECRET SCAN HIT"; cat /tmp/ps_scan.txt | head; exit 1; }
echo "secret scan clean"
[ "${1:-}" = "--dry" ] && exit 0
hf buckets sync "$ST/artifacts" hf://buckets/dan-pandori/nd-rl/proof-strategies/artifacts 2>&1 | tail -2
hf buckets sync "$ST/data" hf://buckets/dan-pandori/nd-rl/proof-strategies/data 2>&1 | tail -2
echo uploaded
