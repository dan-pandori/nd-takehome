#!/usr/bin/env bash
cd /home/dan/work/ds-composition
echo "== a2 $(date -u +%FT%TZ)"; python3 dsc_assemble.py assemble --arm a2 --seed 0 || echo "FAILED a2"
echo "== c0 shape $(date -u +%FT%TZ)"; python3 dsc_assemble.py shape --set /home/dan/nd-takehome/data/p2/train_depth3_f0_a1.jsonl --tag c0 || echo "FAILED c0"
echo "BUILD DONE $(date -u +%FT%TZ)"
