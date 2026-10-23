#!/usr/bin/env bash
# Upload this pod's theta* checkpoints and registry rows to the run's bucket prefix, then list what landed.
. pod/sedl/env.sh
{ hf buckets sync ckpts/style_edl $BK/style-edl/ckpts/style_edl && echo CKPTS_OK; } 2>&1 | tail -2
{ hf buckets sync artifacts/style-edl/registry $BK/style-edl/artifacts/style-edl/registry && echo REG_OK; } 2>&1 | tail -2
find ckpts/style_edl -name '*.pt' | wc -l
echo "UPLOAD DONE $(date -u +%FT%TZ)"
