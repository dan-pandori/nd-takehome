#!/usr/bin/env bash
# Redo (style-edl): the s2 S_Kal guided capability read, which ran out of GPU memory on sedl2 (RC 1, 06:52) while sharing
# the card with two other jobs. Same command and settings as q4k_cap.sh; alone on the GPU.
. pod/sedl/env.sh
mkdir -p ckpts/style_edl/s2/S_Kal artifacts/style_edl/cap
CK=ckpts/style_edl/s2/S_Kal/theta_es_lr0.0001_E0_o0.pt
[ -s $CK ] || hf buckets cp $BK/style-edl/$CK $CK
md5sum $CK
export LEAN_GATE_LOG=artifacts/style_edl/logs/lean_gate_cap.jsonl
rm -f artifacts/style_edl/logs/cap_logical_s2_S_Kal.log artifacts/style_edl/logs/cap_logical_s2_S_Kal.done
pod/sedl/job.sh cap_logical_s2_S_Kal python3 guided_eval.py --ckpt $CK --arm logical --sets data/style_edl/sets/test128.jsonl --k 32 --seed 2 --temperature 0.8 --max_steps 1024 --max_action 512 --batch 1024 --out artifacts/style_edl/cap/s2_S_Kal__logical_k32_seed2
up artifacts/style_edl/cap
echo "QUEUE DONE $(date -u +%FT%TZ)"
