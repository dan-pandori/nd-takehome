#!/usr/bin/env bash
# k = 256, T 0.8 on the 224 L_true >= 11 transfer theorems.  Usage: bash pod/sf/resample.sh <label> <bucket path or local ckpt> <state|whole> [cap: max_action (state, 256) | max_new (whole, 512)]
source pod/sf/env.sh
L=$1; C=$2; KIND=$3; CAP=$4; CK=ckpts/sf2/rs/$L.pt; mkdir -p ckpts/sf2/rs artifacts/sf2/rs
if [ -f "$C" ]; then cp "$C" $CK; else hf buckets cp hf://buckets/dan-pandori/nd-rl/$C $CK || exit 1; fi
md5sum $CK
echo "=== resample $L $KIND $C $(date -u +%FT%TZ)"
if [ "$KIND" = state ]; then
  python3 state_eval.py --ckpt $CK --in data/sf2/long.jsonl --k 256 --temperature 0.8 --seed 0 --batch 2048 --max_action ${CAP:-256} \
    --lenfield L_true --out artifacts/sf2/rs/$L.jsonl --summary artifacts/sf2/rs/$L.json || exit 1
else
  python3 eval_set.py --ckpt $CK --in data/sf2/long.jsonl --k 256 --temperature 0.8 --seed 0 --batch 2048 --max_new ${CAP:-512} \
    --lenfield L_true --out artifacts/sf2/rs/$L.jsonl --summary artifacts/sf2/rs/$L.json || exit 1
fi
python3 -c "import json;d=json.load(open('artifacts/sf2/rs/$L.json'));d['src_ckpt']='$C';json.dump(d,open('artifacts/sf2/rs/$L.json','w'),indent=1)"
gzip -f artifacts/sf2/dumps/rs_$L.jsonl 2>/dev/null
up artifacts/sf2
echo "=== done $(date -u +%FT%TZ)"
