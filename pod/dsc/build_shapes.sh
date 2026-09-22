#!/usr/bin/env bash
cd /home/dan/work/ds-composition
for arm in a1 a4 a3 a2; do cap=6; [ $arm = a3 ] && cap=8; echo "== shape $arm $(date -u +%FT%TZ)"; python3 dsc_assemble.py shape --set data/dsc/train_$arm.jsonl.gz --tag $arm --cap $cap || echo "FAILED shape $arm"; done
python3 dsc_readme.py > /dev/null; echo "SHAPES DONE $(date -u +%FT%TZ)"
