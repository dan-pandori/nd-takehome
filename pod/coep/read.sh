#!/usr/bin/env bash
# One read (pre-registration create-or-elicit-paper C1-C3). k 256, T 0.8, batch 512, fast path, Lean in the loop.
# Usage: bash pod/coep/read.sh <ckpt-name> <in-file> <tag> <plain|guided> <sample-seed> <max_action> <max_steps>
source pod/coep/env.sh
CK=ckpts/coe_paper/$1.pt; IN=$2; TAG=$3; KIND=$4; SS=$5; MA=$6; MS=$7; OUT=artifacts/coe_paper/eval/$TAG
[ -s "$CK" ] || { echo "READ FAILED no ckpt $CK"; exit 1; }
echo "=== read $TAG $KIND seed $SS caps $MA/$MS $(date -u +%FT%TZ)"
if [ ! -s $OUT.json ]; then
  if [ "$KIND" = plain ]; then
    python3 state_eval.py --ckpt $CK --in $IN --k 256 --temperature 0.8 --seed $SS --batch 512 \
      --max_action $MA --max_steps $MS --out $OUT.jsonl --summary $OUT.json > $OUT.log 2>&1 || { echo "READ FAILED $TAG"; exit 1; }
    gzip -f $OUT.jsonl
  else
    python3 guided_eval.py --ckpt $CK --arm logical --sets $IN --k 256 --seed $SS --batch 512 \
      --max_action $MA --max_steps $MS --max_rej 10 --out $OUT > $OUT.log 2>&1 || { echo "READ FAILED $TAG"; exit 1; }
  fi
fi
up artifacts/coe_paper/eval
echo "=== read done $TAG $(date -u +%FT%TZ)"
