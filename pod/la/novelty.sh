#!/usr/bin/env bash
# Base reachability (novelty.py under stage1_abs.pt) of an arm's final found proofs: all transfer proofs and target
# proofs with L_true >= 8 (found_union_8 for T6 siblings). Usage: bash pod/la/novelty.sh <name> [round]
cd /workspace/nd-takehome; NAME=$1; R=${2:-8}; D=artifacts/ladder/$NAME
python3 - "$D" "$R" <<'PY'
import json, sys
d, r = sys.argv[1], sys.argv[2]
import os
src = f'{d}/found_union_{r}.jsonl' if os.path.exists(f'{d}/found_union_{r}.jsonl') else f'{d}/found_{r}.jsonl'
with open(f'{d}/nov_in_targets.jsonl', 'w') as fo:
    for l in open(src):
        if json.loads(l)['L_true'] >= 8:
            fo.write(l)
with open(f'{d}/nov_in_transfer.jsonl', 'w') as fo:
    for l in open(f'{d}/found_transfer_{r}.jsonl'):
        fo.write(l)
PY
python3 novelty.py --ckpts base=ckpts/stage1_abs.pt --src transfer=$D/nov_in_transfer.jsonl targets=$D/nov_in_targets.jsonl --out $D/novelty --batch 768
