#!/usr/bin/env bash
# Wait for a pod's EI training job to exit, then start that seed's EI stage-1 sampling on the same pod.
# Usage: pod/sc/after_ei.sh <pod> <seed>
set -u
P=$1; S=$2
until podrun "$P" "grep -q '^EXIT ' artifacts/sc/la_T1_sc_s$S.log" 2>/dev/null; do sleep 60; done
echo "$(date -u +%FT%TZ) la_T1_sc_s$S finished on $P"
podrun "$P" "tail -3 artifacts/sc/la_T1_sc_s$S.log"
podrun "$P" "test -f ckpts/ladder/la_T1_sc_s${S}_r8.pt" || { echo "NO r8 CHECKPOINT on $P"; exit 1; }
for SH in 0 1; do
  podbg "$P" "sc/s1_ei_T08_s${S}_sh$SH" "export PATH=\$HOME/.elan/bin:\$PATH LEAN_GATE_WORKERS=2 LEAN_GATE_LOG=artifacts/sc/gate_s1ei.jsonl; echo START \$(date -u +%FT%TZ); python3 support.py --ckpt ckpts/ladder/la_T1_sc_s${S}_r8.pt --model ei --stage $([ "$S" = 0 ] && echo s1 || echo s3) --in data/sc/theorems.jsonl --k 10000 --stop_at 50 --temperature 0.8 --seed $S --batch 2048 --max_new 400 --shard $SH/2 --out artifacts/sc/s$([ "$S" = 0 ] && echo 1 || echo 3)_ei_T08_s$S; echo EXIT \$? \$(date -u +%FT%TZ)"
done
echo "$(date -u +%FT%TZ) launched EI stage-1 sampling for seed $S on $P"
