#!/usr/bin/env bash
# job.sh <job> <writer> <requests.jsonl.gz> <seed> [sampler flags ...]: sample answers after supplied thinking
# (olmo_answeronly/sample_prefix.py) on the worker's GPU (CUDA_VISIBLE_DEVICES set by worker.sh), then grade with
# olmo_transplant/grade_rows.py (unchanged). Run olmo-answeronly; pod/olmo_transplant/job.sh with this run's paths.
# writer = the model directory /workspace/models/<writer>; for the LoRA arm pass --lora <dir> --lora_name lora_main.
J=$1; W=$2; RQ=$3; S=$4; shift 4; G=${GPU:-0}
cd /workspace/nd-takehome; A=artifacts/olmo_answeronly; mkdir -p $A/samples $A/graded $A/meta $A/logs
export OMP_NUM_THREADS=8
until [ -f /workspace/models/$W/.complete ]; do sleep 20; done
( while sleep 30; do echo "$(date -u +%T) $(nvidia-smi -i $G --query-gpu=memory.used,utilization.gpu --format=csv,noheader)"; done ) > $A/logs/${J}_smi.log 2>&1 &
SMI=$!
echo "JOB_START $J $(date -u +%FT%TZ) writer=$W gpu=$G cvd=$CUDA_VISIBLE_DEVICES requests=$RQ extra=[$*]"
VLLM_ATTENTION_BACKEND=FLASH_ATTN python -u olmo_answeronly/sample_prefix.py --model /workspace/models/$W \
  --tokenizer /workspace/models/tok --name $W --rev main --requests $RQ --seed $S --job $J \
  --out $A/samples/$J.jsonl.gz --meta $A/meta/$J.json "$@"
rc=$?; kill $SMI 2>/dev/null
python olmo_transplant/grade_rows.py $A/samples/$J.jsonl.gz $A/graded/$J.jsonl
echo "JOB_DONE $J rc=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] && [ -z "$PARTIAL" ] && touch $A/meta/$J.done
