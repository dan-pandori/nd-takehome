#!/usr/bin/env bash
# VPS: build the four sets one after another (a2 waits for the ORE top-up generation), then the control's shape table.
cd /home/dan/work/ds-composition
for arm in a1 a4 a3; do
  echo "== $arm $(date -u +%FT%TZ)"; python3 dsc_assemble.py assemble --arm $arm --seed 0 || echo "FAILED $arm"
done
while pgrep -f "make_coverage_sets.py ge[n]" > /dev/null; do sleep 20; done
echo "== a2 $(date -u +%FT%TZ)"; python3 dsc_assemble.py assemble --arm a2 --seed 0 || echo "FAILED a2"
echo "== c0 shape $(date -u +%FT%TZ)"; python3 dsc_assemble.py shape --set /home/dan/nd-takehome/data/p2/train_depth3_f0_a1.jsonl --tag c0 || echo "FAILED c0"
echo "BUILD DONE $(date -u +%FT%TZ)"
