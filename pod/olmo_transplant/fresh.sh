#!/usr/bin/env bash
# fresh.sh <job> <gpu> <pids> <budgets>: fresh budget forcing F(N) for s2300 (olmo_transplant/fresh_bf.py), then grade.
J=$1; G=$2; P=$3; B=$4
cd /workspace/nd-takehome; A=artifacts/olmo_transplant; mkdir -p $A/samples $A/graded $A/meta $A/logs
export OMP_NUM_THREADS=8
echo "JOB_START $J $(date -u +%FT%TZ) gpu=$G pids=$P budgets=$B"
CUDA_VISIBLE_DEVICES=$G VLLM_ATTENTION_BACKEND=FLASH_ATTN python -u olmo_transplant/fresh_bf.py --model /workspace/models/s2300 \
  --tokenizer /workspace/models/tok --name s2300 --rev main --pids $P --budgets $B --n 16 --seed 8103 --job $J \
  --out $A/samples/$J.jsonl.gz --meta $A/meta/$J.json
rc=$?
python olmo_transplant/grade_rows.py $A/samples/$J.jsonl.gz $A/graded/$J.jsonl
echo "JOB_DONE $J rc=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] && touch $A/meta/$J.done
