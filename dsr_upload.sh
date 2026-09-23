#!/usr/bin/env bash
# Upload ds-rendering artefacts to the public bucket, FROM THE HOST.
#
# The pods cannot do this: `hf` is not installed on the RunPod image and huggingface_hub is not importable there,
# so pod/dsr/finish.sh's own `hf buckets sync` silently failed on every pod (caught 2026-09-23 23:45 UTC, log.md).
# finish.sh still does the useful half -- it waits for ARM_DONE and runs the checker of record without my host --
# and the upload happens here after pull.sh.
#
# The bucket is PUBLIC: only artifacts/dsr/<pod>/, ckpts/dsr/ and the committed write-ups go up. Never ~/.config,
# never a shell log, nothing that could carry a token.
set -u
B="hf://buckets/dan-pandori/nd-rl/ds-rendering"
cd "$(dirname "$0")"
for d in artifacts/dsr/*/; do
  p=$(basename "$d")
  echo "== $p"
  hf buckets sync "$d" "$B/artifacts/$p" || echo "FAILED artifacts/$p"
done
[ -d ckpts/dsr ] && { echo "== ckpts"; hf buckets sync ckpts/dsr "$B/ckpts" || echo "FAILED ckpts"; }
echo "== done $(date -u +%FT%TZ)"
