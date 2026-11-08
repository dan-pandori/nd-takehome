#!/usr/bin/env bash
# job.sh <job> <writer> <requests.jsonl.gz> <seed> <gpu> [sampler flags ...]: sample answers after supplied thinking
# (olmo_transplant/sample_prefix.py) on one GPU, then grade (olmo_transplant/grade_rows.py). Run olmo-transplant.
J=$1; W=$2; RQ=$3; S=$4; G=$5; shift 5
cd /workspace/nd-takehome; A=artifacts/olmo_transplant; mkdir -p $A/samples $A/graded $A/meta $A/logs
export OMP_NUM_THREADS=8
( while sleep 30; do echo "$(date -u +%T) $(nvidia-smi -i $G --query-gpu=memory.used,utilization.gpu --format=csv,noheader)"; done ) > $A/logs/${J}_smi.log 2>&1 &
SMI=$!
echo "JOB_START $J $(date -u +%FT%TZ) writer=$W gpu=$G requests=$RQ extra=[$*]"
CUDA_VISIBLE_DEVICES=$G VLLM_ATTENTION_BACKEND=FLASH_ATTN python -u olmo_transplant/sample_prefix.py --model /workspace/models/$W \
  --tokenizer /workspace/models/tok --name $W --rev main --requests $RQ --seed $S --job $J \
  --out $A/samples/$J.jsonl.gz --meta $A/meta/$J.json "$@"
rc=$?; kill $SMI 2>/dev/null
python olmo_transplant/grade_rows.py $A/samples/$J.jsonl.gz $A/graded/$J.jsonl
echo "JOB_DONE $J rc=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] && touch $A/meta/$J.done
