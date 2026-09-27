#!/usr/bin/env bash
# When sc1's stage-2b T=1.0 crux arm exits, start the matching T=0.8 deep arm on the same pod, so the
# falsifier is evaluated at equal depth at both temperatures.
set -u
until podrun sc1 "grep -q '^EXIT ' artifacts/sc/s2b_base_T10_sh0.log && grep -q '^EXIT ' artifacts/sc/s2b_base_T10_sh1.log" 2>/dev/null; do sleep 60; done
echo "$(date -u +%FT%TZ) s2b finished"
for SH in 0 1; do
  podbg sc1 "sc/s2c_base_T08_sh$SH" "export PATH=\$HOME/.elan/bin:\$PATH LEAN_GATE_WORKERS=2 LEAN_GATE_LOG=artifacts/sc/gate_s2cT08.jsonl; echo START \$(date -u +%FT%TZ); python3 support.py --ckpt ckpts/lf/stage1_a1_seq_s0.pt --model base --stage s2c_T08 --in data/sc/theorems.jsonl --names data/sc/crux_forward_phi.txt --k 150000 --stop_at 5 --temperature 0.8 --seed 21 --model_seed 0 --batch 2048 --max_new 400 --shard $SH/2 --out artifacts/sc/s2c_base_T08_s0; echo EXIT \$? \$(date -u +%FT%TZ)"
done
echo "$(date -u +%FT%TZ) launched T=0.8 deep arm on sc1"
