#!/usr/bin/env bash
# job.sh <job> <name> <repo> <rev> <n> <pids|-> <seed> [chunk0] [chunk]: fetch, sample, grade one checkpoint.
J=$1; NAME=$2; R=$3; V=$4; N=$5; P=$6; S=$7; C0=${8:-0}; CH=${9:-16}
cd /workspace/nd-takehome; A=artifacts/olmo_pilot
bash pod/olmo_pilot/fetch.sh "$R" "$V" "$NAME" || { echo "FETCH_FAIL $(date -u +%FT%TZ)"; exit 1; }
PIDS=""; [ "$P" != "-" ] && PIDS="--pids $P"
( while sleep 60; do echo "$(date -u +%T) $(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader)"; done ) > $A/logs/${J}_smi.log 2>&1 &
SMI=$!
VLLM_ATTENTION_BACKEND=FLASH_ATTN python -u olmo_pilot/sample.py --model /workspace/models/$NAME --tokenizer /workspace/models/base \
  --name "$NAME" --rev "$V" --problems olmo_pilot/problems.jsonl $PIDS --n $N --chunk $CH --chunk0 $C0 --seed $S --job $J \
  --out $A/samples/$J.jsonl.gz --meta $A/meta/$J.json
rc=$?; kill $SMI 2>/dev/null
python olmo_pilot/grade.py $A/samples/$J.jsonl.gz olmo_pilot/problems.jsonl $A/graded/$J.jsonl
echo "JOB_DONE $J rc=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] && touch $A/meta/$J.done
