#!/usr/bin/env bash
# S2 on seed 0.  $1 = fwd08 | fwd10 | rev ; $2 = k for this continuation ; $3 = batch ; $4 = names file (default by kind)
KIND=$1; K=$2; B=${3:-2048}
case $KIND in
  fwd08) M=base; CK=ckpts/se/stage1_SN_s0.pt; T=0.8; SEED=6; NM=${4:-data/ss/sn_crux_forward.txt} ;;
  fwd10) M=base; CK=ckpts/se/stage1_SN_s0.pt; T=1.0; SEED=7; NM=${4:-data/ss/sn_crux_forward.txt} ;;
  rev)   M=ei;   CK=ckpts/se/ladder/la_T1_SN_s0_r8.pt; T=0.8; SEED=8; NM=${4:-data/ss/sn_crux_reverse.txt} ;;
esac
TT=T$(echo $T | tr -d .); [ $TT = T1 ] && TT=T10; TAG=S2${KIND}k$((K / 1000))
LEAN_GATE_DUMP=artifacts/ss/dump/${TAG}_${M}_${TT}_s0.jsonl LEAN_GATE_LOG=artifacts/ss/logs/gate_${TAG}.jsonl \
python3 ss_support.py --ckpt $CK --model $M --stage $TAG --names $NM --k $K --stop_at 1 --temperature $T \
  --seed $SEED$((K / 1000)) --model_seed 0 --batch $B --out artifacts/ss/${TAG}_${M}_${TT}_s0
