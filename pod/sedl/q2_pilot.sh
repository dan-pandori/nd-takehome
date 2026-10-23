#!/usr/bin/env bash
# S_own pilot on the GPU (style-edl): seed 0, A_ES and A_fixed (E in 1,2,4), lr grid 1e-5,1e-4,1e-3, orders 0,1.
. pod/sedl/env.sh
J=pod/sedl/job.sh; D=data/style_edl/streams; O=artifacts/style_edl/edl
L=ckpts/bs/stage1_best12_s0_b1200.pt
$J edl_s0_S_own python3 style_edl/edl_run.py --ckpt $L --stream $D/s0/S_own.stream.jsonl --test $D/s0/S_own.test.jsonl --algo es --lrs 1e-5,1e-4,1e-3 --orders 0,1 --arm S_own --lseed 0 --save_theta ckpts/style_edl/s0/S_own --out $O/s0/S_own.json
$J edlfix_s0_S_own python3 style_edl/edl_run.py --ckpt $L --stream $D/s0/S_own.stream.jsonl --test $D/s0/S_own.test.jsonl --algo fixed --epochs 1,2,4 --lrs 1e-5,1e-4,1e-3 --orders 0,1 --arm S_own --lseed 0 --out $O/s0/S_own.fixed.json
up artifacts/style_edl/edl
echo "QUEUE DONE $(date -u +%FT%TZ)"
