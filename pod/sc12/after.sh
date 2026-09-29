#!/usr/bin/env bash
# After sn_seed.sh: literal-text re-checks, then the max_steps 96 diagnostic re-read (T1 and Stage-1, rr600 + ge17).
# Usage: bash pod/sc12/after.sh <seed>
source pod/sc12/env.sh; S=$1
until [ -f artifacts/sc12/sn_s$S.done ] || [ -f artifacts/sc12/sn_s$S.fail ]; do sleep 30; done
bash pod/sc12/recheck.sh T1_SN12_s$S; bash pod/sc12/recheck.sh stage1_SN12_s$S
MS=96 bash pod/sc12/reread.sh ckpts/sc12/ladder/la_T1_SN12_s${S}_r8.pt T1_SN12_s$S
MS=96 bash pod/sc12/reread.sh ckpts/sc12/stage1_SN12_s$S.pt stage1_SN12_s$S
echo "=== after done $(date -u +%FT%TZ)"
