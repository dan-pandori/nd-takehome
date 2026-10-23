#!/usr/bin/env bash
# Phase 5 for the Kalmar cells (style-edl): theta* (A_ES, chosen lr, order 0) read plain on all 256 and guided on the
# 128 test theorems. Usage: pod/sedl/q4k_cap.sh <seed> <lr as in the theta file name>. Restartable.
. pod/sedl/env.sh
J=pod/sedl/job.sh; O=artifacts/style_edl/cap; mkdir -p $O
export LEAN_GATE_LOG=artifacts/style_edl/logs/lean_gate_cap.jsonl
s=$1; lr=$2; T=s${s}_S_Kal; CK=ckpts/style_edl/s$s/S_Kal/theta_es_lr${lr}_E0_o0.pt
C="--k 32 --seed 2 --temperature 0.8 --max_steps 1024 --max_action 512 --batch 1024"
$J cap_plain_$T python3 guided_eval.py --ckpt $CK --arm plain --sets data/style_edl/sets/all256.jsonl $C --out $O/${T}__plain_k32_seed2
$J cap_logical_$T python3 guided_eval.py --ckpt $CK --arm logical --sets data/style_edl/sets/test128.jsonl $C --out $O/${T}__logical_k32_seed2
up artifacts/style_edl/cap
echo "QUEUE DONE $(date -u +%FT%TZ)"
